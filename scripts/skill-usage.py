#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Trace historical skill usage from local Codex and ZCode logs.

This is a forensic/inventory tool, not a runtime hook.

Evidence policy
---------------
* ZCode: a real ``Skill`` function call with an ``input.skill`` value.
* Codex: an actual tool call/result that reads a skill's ``SKILL.md``.
* Skill descriptions in system/developer context and assistant prose are ignored.

The scanner is streaming and keeps per-file state. Re-running after a full scan
only reads appended bytes for plain JSONL files. A compressed ``.jsonl.zst``
file is treated as immutable after its first successful scan (its compressed
byte offset is not a useful resume point).

Usage
-----
    python scripts/skill-usage.py --scan        # incremental scan + report
    python scripts/skill-usage.py --scan --full # rebuild the local cache
    python scripts/skill-usage.py --json        # machine-readable summary
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        try:
            _stream.reconfigure(errors="replace")
        except Exception:
            pass

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
ARCHIVE = ROOT / "skills-archive"
DB_PATH = ROOT / ".skill-usage" / "usage.sqlite"
REPORT_PATH = SKILLS / "indexes" / "usage.md"
CODEX_SESSIONS = Path.home() / ".codex" / "sessions"
CODEX_ARCHIVED = Path.home() / ".codex" / "archived_sessions"
ZCODE_ROLLOUT = Path.home() / ".zcode" / "cli" / "rollout"

FM_RE = __import__("re").compile(r"^---\r?\n(.*?)\r?\n---\r?\n", __import__("re").S)
NAME_RE = __import__("re").compile(r"^name:\s*(.+?)\s*$", __import__("re").M)
PATH_RE = __import__("re").compile(
    r"(?i)(?:^|[\\/\"'`\s])skills[\\/](?:[^\"'`\r\n]*[\\/])?([^\\/\"'`\r\n]+)[\\/]SKILL\.md"
)
SKILL_PATH_RE = __import__("re").compile(
    r"(?i)(?:^|[\\/\"'`\s])(?:skills|skills-archive)[\\/](?:[^\"'`\r\n]*[\\/])?([^\\/\"'`\r\n]+)[\\/]SKILL\.md"
)
Z_SKILL_RE = __import__("re").compile(r"^[^:]+:(.+)$")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def stable_id(*parts: str) -> str:
    h = hashlib.sha256()
    for part in parts:
        h.update(part.encode("utf-8", "replace"))
        h.update(b"\0")
    return h.hexdigest()[:32]


def read_frontmatter(path: Path) -> tuple[str | None, str | None]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None, None
    m = FM_RE.match(text)
    if not m:
        return None, None
    fm = m.group(1)
    name_m = NAME_RE.search(fm)
    name = name_m.group(1).strip().strip('"\'') if name_m else None
    # Only the routing name is needed. Description is intentionally not stored.
    return name, None


def discover_skills() -> dict[str, dict[str, Any]]:
    """Map canonical skill names to their physical locations.

    Includes active and archived skills. A name can only map to one canonical
    route for reporting; duplicate hits are still shown in ``duplicates``.
    """
    found: dict[str, list[str]] = defaultdict(list)
    for base in (SKILLS, ARCHIVE):
        if not base.exists():
            continue
        for path in base.rglob("SKILL.md"):
            rel = path.relative_to(base)
            if any(part in {".git", "node_modules", "__pycache__", ".venv"} for part in rel.parts):
                continue
            fm_name, _ = read_frontmatter(path)
            name = fm_name or path.parent.name
            found[name].append(str(path.resolve()))
    return {name: {"name": name, "paths": paths, "path": paths[0]} for name, paths in found.items()}


def normalize_skill_name(raw: str, known: dict[str, dict[str, Any]]) -> str | None:
    raw = raw.strip().strip('"\'')
    if not raw:
        return None
    if raw in known:
        return raw
    if ":" in raw:
        tail = raw.rsplit(":", 1)[-1]
        if tail in known:
            return tail
    if "/" in raw:
        tail = raw.rsplit("/", 1)[-1]
        if tail in known:
            return tail
    return None


def extract_skill_paths(text: str, known: dict[str, dict[str, Any]]) -> set[str]:
    """Find exact skill-directory / SKILL.md references in a command string."""
    out: set[str] = set()
    # Exact path boundary prevents a short skill name (e.g. ``ck``) from
    # matching inside another directory name like ``delivery-no-pseudoblock``.
    for name in known:
        pat = re.compile(
            r"(?i)(?:^|[\\/\"'`\s])" + re.escape(name) + r"[\\/]SKILL\.md(?=$|[\\s\"'`;|&)])"
        )
        if pat.search(text):
            out.add(name)
    return out

def iter_jsonl_lines(path: Path) -> Iterator[tuple[int, str, int]]:
    """Yield (line number, line, byte offset after line) for a plain JSONL."""
    with path.open("rb") as fh:
        offset = 0
        line_no = 0
        while True:
            raw = fh.readline()
            if not raw:
                break
            line_no += 1
            offset += len(raw)
            yield line_no, raw.decode("utf-8", "replace"), offset


def iter_codex_file(path: Path, start_offset: int = 0) -> Iterator[tuple[int, str, int]]:
    if path.suffix == ".zst":
        if start_offset:
            return
        data = subprocess.run(
            ["node", "-e",
             "const fs=require('fs'),z=require('zlib');"
             "process.stdout.write(z.zstdDecompressSync(fs.readFileSync(process.argv[1])));",
             str(path)],
            capture_output=True,
            check=False,
        )
        if data.returncode != 0:
            raise RuntimeError(data.stderr.decode("utf-8", "replace")[:500])
        # One large decompressed buffer is unavoidable for zstd; scan line-wise.
        offset = 0
        for line_no, raw in enumerate(data.stdout.splitlines(keepends=True), 1):
            offset += len(raw)
            yield line_no, raw.decode("utf-8", "replace"), offset
        return
    with path.open("rb") as fh:
        if start_offset:
            fh.seek(start_offset)
        offset = start_offset
        line_no = 0
        while True:
            raw = fh.readline()
            if not raw:
                break
            line_no += 1
            offset += len(raw)
            yield line_no, raw.decode("utf-8", "replace"), offset


def walk_strings(value: Any) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from walk_strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from walk_strings(v)


READ_COMMAND_RE = __import__("re").compile(
    r"(?i)(?:\bget-content\b|\btype\s+|\bcat\s+|\breadalltext\s*\(|\bopen\s*\(|\bread_text\s*\(|\breadfile\b|\bfile_read\b|\bread_file\b)"
)
MUTATION_RE = __import__("re").compile(
    r"(?i)(?:\bwritealltext\s*\(|\bwrite_text\s*\(|\bfile_write\b|\bwrite_file\b|\bapply_patch\b|\bremove-item\b|\bmove-item\b|\bset-content\b|\bout-file\b|\bgit\s+diff\b)"
)


def looks_like_read(args: str) -> tuple[bool, str]:
    """Return ``(is_read, command)`` only for a direct skill-body read.

    Command names are parsed, not substring-searched across a whole script:
    this is important because agents often run a Python edit script that both
    references a skill path and prints unrelated text.
    """
    try:
        obj = json.loads(args)
    except Exception:
        return False, ""
    cmd = obj.get("cmd") if isinstance(obj, dict) else None
    if not isinstance(cmd, str):
        return False, ""
    # A path assembled dynamically (Join-Path/variable) cannot be proven to
    # target the skill body; metadata commands often mention such a path while
    # actually reading a different file. Require a literal SKILL.md token.
    if "SKILL.md" not in cmd:
        return False, ""
    # A read command must have SKILL.md on its own command line. Parse lines
    # and reject whole-script patterns that only mention it in an inline editor.
    for line in cmd.splitlines():
        # Skip comments and git metadata invocations.
        if re.match(r"\s*#", line) or re.search(r"(?i)\bgit\s+(?:diff|show|log|ls-files|check-attr)\b", line):
            continue
        # PowerShell: Get-Content <path>; allow surrounding statements on the
        # same line but require the path argument to name SKILL.md.
        if re.search(r"(?i)\bGet-Content\b.*SKILL\.md", line):
            if re.search(r"(?i)\bJoin-Path\b|\$[A-Za-z_][A-Za-z0-9_]*\s*[\/\\]", line):
                continue
            if re.search(r"(?i)\$lines\s*=\s*Get-Content\b", line):
                continue
            if re.search(r"(?i)\b(?:Set-Content|Out-File|WriteAllText|WriteAllBytes|apply_patch)\b", line):
                continue
            return True, line
        # Unix-style cat/type <path>
        if re.search(r"(?i)(?:^|[;&|]\s*)(?:cat|type)\s+.*SKILL\.md", line):
            return True, line
        # Python direct file reads. Keep this intentionally narrow: an inline
        # script that edits or filters a skill is not a model load.
        if re.search(r"(?i)\b(?:Path|open)\s*\(.*SKILL\.md.*\)\s*\.\s*read(?:_text|_bytes)?\s*\(", line):
            if re.search(r"(?i)\b(?:write|unlink|replace|rename)\s*\(", line):
                continue
            return True, line
        if re.search(r"(?i)\bReadAllText\s*\(.*SKILL\.md", line):
            return True, line
    return False, ""

def codex_events(obj: dict[str, Any], known: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Extract actual tool-call evidence, never prompt/context metadata."""
    payload = obj.get("payload")
    if not isinstance(payload, dict):
        return []
    typ = payload.get("type")
    # Execute/read calls are represented as function_call objects.
    # event_msg item_completed is a duplicate completion event and is skipped.
    if typ == "function_call":
        name = str(payload.get("name") or "")
        args = payload.get("arguments")
        if not isinstance(args, str):
            args = json.dumps(args, ensure_ascii=False) if args is not None else ""
        # Restrict to tools that can actually read files/execute commands.
        if name.lower() not in {"exec_command", "read_file", "read", "bash", "shell", "write_stdin"}:
            return []
        is_read, cmd = looks_like_read(args)
        if not is_read:
            return []
        skills = extract_skill_paths(cmd, known)
        return [
            {
                "skill": skill,
                "kind": "read",
                "client": "codex",
                "raw_name": skill,
                "event_time": str(obj.get("timestamp") or ""),
                "tool": name,
                "evidence": args[:1200],
            }
            for skill in sorted(skills)
        ]
    return []


def zcode_events(obj: dict[str, Any], known: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    if obj.get("type") != "model_io":
        return []
    response = obj.get("response")
    if not isinstance(response, dict):
        return []
    calls = response.get("toolCalls")
    if not isinstance(calls, list):
        return []
    out = []
    for call in calls:
        if not isinstance(call, dict) or call.get("name") != "Skill":
            continue
        inp = call.get("input") or {}
        raw = inp.get("skill") if isinstance(inp, dict) else None
        if not isinstance(raw, str):
            continue
        skill = normalize_skill_name(raw, known)
        if not skill:
            continue
        out.append(
            {
                "skill": skill,
                "kind": "explicit",
                "client": "zcode",
                "raw_name": raw,
                "event_time": str(obj.get("startedAt") or obj.get("timestamp") or ""),
                "tool": "Skill",
                "evidence": json.dumps({"skill": raw, "args": inp.get("args", "")}, ensure_ascii=False)[:1200],
                "call_id": str(call.get("id") or ""),
            }
        )
    return out


def file_state(conn: sqlite3.Connection, path: str) -> tuple[int, int, int]:
    row = conn.execute("SELECT offset, size, mtime_ns FROM file_state WHERE path=?", (path,)).fetchone()
    return tuple(row) if row else (0, 0, 0)


def record_file_state(conn: sqlite3.Connection, path: str, offset: int, size: int, mtime_ns: int, scanned_at: str) -> None:
    conn.execute(
        "INSERT INTO file_state(path,offset,size,mtime_ns,scanned_at) VALUES(?,?,?,?,?) "
        "ON CONFLICT(path) DO UPDATE SET offset=excluded.offset,size=excluded.size,mtime_ns=excluded.mtime_ns,scanned_at=excluded.scanned_at",
        (path, offset, size, mtime_ns, scanned_at),
    )


def session_id_from_file(path: Path) -> str:
    # Codex rollout filenames carry the session id but old response_item lines
    # do not. Example: ...-01a0d436-21b6-73e1-9fa3-5abe9a23b869_<fork>.jsonl
    # The common 36-char UUID is the original session; the second UUID suffix
    # identifies a rollout/fork segment and must not split one conversation.
    import re
    matches = re.findall(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", path.name)
    return matches[0] if matches else ""


def scan_file(conn: sqlite3.Connection, path: Path, client: str, known: dict[str, dict[str, Any]]) -> tuple[int, int]:
    stat = path.stat()
    file_session_id = session_id_from_file(path) if client == "codex" else ""
    old_offset, old_size, old_mtime = file_state(conn, str(path))
    start = old_offset if old_size == stat.st_size and old_mtime == stat.st_mtime_ns else 0
    if old_size and old_size != stat.st_size:
        # A file can be rewritten or rotated. Never trust a stale offset.
        start = 0
    events = 0
    last_offset = 0
    try:
        rows = iter_codex_file(path, start)
        for line_no, line, offset in rows:
            last_offset = offset
            try:
                obj = json.loads(line)
            except Exception:
                continue
            extracted = codex_events(obj, known) if client == "codex" else zcode_events(obj, known)
            payload = obj.get("payload") if isinstance(obj.get("payload"), dict) else {}
            payload_call_id = str(payload.get("call_id") or "")
            for ev in extracted:
                if payload_call_id and not ev.get("call_id"):
                    ev["call_id"] = payload_call_id
                session_id = str(obj.get("sessionId") or file_session_id or "")
                # Keep real repeated calls in one session, but collapse the
                # same call repeated across model_io snapshots or rollout
                # continuations. ZCode provides a call id; old Codex rollouts
                # expose a stable call_id on function_call payloads.
                # Old Codex rollouts have no stable call id and repeat every
                # read across model snapshots. Collapse to one evidence row
                # per (session, skill, kind) so counts mean "sessions where
                # the skill was observed", not "snapshot lines".
                if session_id:
                    event_id = stable_id(client, session_id, ev["skill"], ev["kind"])
                else:
                    event_id = stable_id(client, str(path), f"{ev['skill']}:{ev['kind']}")
                before = conn.total_changes
                conn.execute(
                    "INSERT OR IGNORE INTO events(id,client,session_id,event_time,skill,raw_name,kind,source_file,line_no,tool,evidence) "
                    "VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        event_id,
                        ev["client"],
                        session_id,
                        ev.get("event_time", ""),
                        ev["skill"],
                        ev.get("raw_name", ev["skill"]),
                        ev["kind"],
                        str(path),
                        line_no,
                        ev.get("tool", ""),
                        ev.get("evidence", ""),
                    ),
                )
                if conn.total_changes > before:
                    events += 1
        if path.suffix != ".zst":
            record_file_state(conn, str(path), last_offset, stat.st_size, stat.st_mtime_ns, utc_now())
        else:
            record_file_state(conn, str(path), stat.st_size, stat.st_size, stat.st_mtime_ns, utc_now())
        conn.commit()
        return events, last_offset
    except Exception as exc:
        print(f"WARN scan failed: {path}: {exc}", file=sys.stderr)
        return events, last_offset


def rebuild_usage(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM usage")
    conn.execute(
        "INSERT INTO usage(skill,explicit_count,read_count,first_used,last_used,clients) "
        "SELECT skill,"
        "SUM(CASE WHEN kind='explicit' THEN 1 ELSE 0 END),"
        "SUM(CASE WHEN kind='read' THEN 1 ELSE 0 END),"
        "MIN(NULLIF(event_time,'')),MAX(NULLIF(event_time,'')),"
        "GROUP_CONCAT(DISTINCT client) "
        "FROM events GROUP BY skill"
    )
    conn.commit()


def setup_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS events(
          id TEXT PRIMARY KEY,
          client TEXT NOT NULL,
          session_id TEXT,
          event_time TEXT,
          skill TEXT NOT NULL,
          raw_name TEXT,
          kind TEXT NOT NULL,
          source_file TEXT NOT NULL,
          line_no INTEGER,
          tool TEXT,
          evidence TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_events_skill ON events(skill);
        CREATE INDEX IF NOT EXISTS idx_events_client ON events(client);
        CREATE TABLE IF NOT EXISTS file_state(
          path TEXT PRIMARY KEY,
          offset INTEGER NOT NULL,
          size INTEGER NOT NULL,
          mtime_ns INTEGER NOT NULL,
          scanned_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS usage(
          skill TEXT PRIMARY KEY,
          explicit_count INTEGER NOT NULL DEFAULT 0,
          read_count INTEGER NOT NULL DEFAULT 0,
          first_used TEXT,
          last_used TEXT,
          clients TEXT
        );
        """
    )
    conn.commit()


def collect_files() -> list[tuple[Path, str]]:
    out: list[tuple[Path, str]] = []
    for base in (CODEX_SESSIONS, CODEX_ARCHIVED):
        if base.exists():
            for p in base.rglob("*.jsonl*"):
                if p.is_file() and p.suffix in {".jsonl", ".zst"}:
                    out.append((p, "codex"))
    if ZCODE_ROLLOUT.exists():
        for p in ZCODE_ROLLOUT.rglob("*.jsonl"):
            if p.is_file():
                out.append((p, "zcode"))
    return sorted(out, key=lambda x: (str(x[0])))


def write_report(conn: sqlite3.Connection, known: dict[str, dict[str, Any]]) -> None:
    rows = list(conn.execute(
        "SELECT skill,explicit_count,read_count,first_used,last_used,clients FROM usage ORDER BY "
        "(explicit_count + read_count) DESC, last_used DESC, skill ASC"
    ))
    counts = {r[0]: r for r in rows}
    total = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    active_names = set()
    if (SKILLS / "indexes" / "active.md").exists():
        text = (SKILLS / "indexes" / "active.md").read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"`([^`]+)`", text):
            if m.group(1) in known:
                active_names.add(m.group(1))
    lines = [
        "# Skill usage report",
        "",
        f"> Generated: `{utc_now()}`  |  evidence events: **{total}**",
        "> ZCode `explicit` = real `Skill` tool call; Codex `read` = actual `SKILL.md` read (one per session).",
        "> Text mentions and injected skill catalogs are excluded.",
        "",
        "| Skill | Explicit | Read evidence | Last observed | Clients | Layer |",
        "| --- | ---: | ---: | --- | --- | --- |",
    ]
    for skill, explicit, read, first, last, clients in rows:
        paths = known.get(skill, {}).get("paths", [])
        if any(str(SKILLS / ".system") in p for p in paths):
            layer = "system"
        elif skill in active_names:
            layer = "active"
        elif any(str(ARCHIVE) in p for p in paths):
            layer = "archive"
        else:
            layer = "library"
        lines.append(f"| `{skill}` | {explicit} | {read} | {last or '-'} | {clients or '-'} | {layer} |")
    never = sorted(set(known) - set(counts))
    lines += ["", f"## Never observed ({len(never)})", ""]
    lines += [f"- `{x}`" for x in never] if never else ["- (none)"]
    lines += ["", "## Files scanned", ""]
    for path, offset, size, mtime, scanned in conn.execute(
        "SELECT path,offset,size,mtime_ns,scanned_at FROM file_state ORDER BY path"
    ).fetchall():
        lines.append(f"- `{path}` — offset {offset}/{size}, mtime {mtime}, scanned {scanned}")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def print_summary(conn: sqlite3.Connection, known: dict[str, dict[str, Any]], top: int) -> None:
    rows = list(conn.execute(
        "SELECT skill,explicit_count,read_count,last_used,clients FROM usage ORDER BY "
        "(explicit_count + read_count) DESC, last_used DESC, skill ASC LIMIT ?", (top,)
    ))
    total_events = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    print(f"Skill usage events: {total_events}")
    for skill, explicit, read, last, clients in rows:
        print(f"{skill:40} explicit={explicit:<3} read={read:<3} last={last or '-':25} clients={clients or '-'}")
    never = sorted(set(known) - {r[0] for r in conn.execute("SELECT skill FROM usage")})
    print(f"Never observed: {len(never)}")
    print(f"Report: {REPORT_PATH}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Trace historical Codex/ZCode skill usage")
    parser.add_argument("--scan", action="store_true", help="scan logs (incremental)")
    parser.add_argument("--full", action="store_true", help="discard cache and rescan everything")
    parser.add_argument("--json", action="store_true", help="print machine-readable summary")
    parser.add_argument("--top", type=int, default=20)
    args = parser.parse_args()

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    known = discover_skills()
    conn = sqlite3.connect(DB_PATH)
    setup_db(conn)
    if args.full:
        conn.execute("DELETE FROM events")
        conn.execute("DELETE FROM file_state")
        conn.execute("DELETE FROM usage")
        conn.commit()
    if args.scan:
        files = collect_files()
        total = 0
        for idx, (path, client) in enumerate(files, 1):
            n = 0
            try:
                n, _ = scan_file(conn, path, client, known)
            except FileNotFoundError:
                # Codex may compress/rotate a live rollout while we scan. The
                # .zst sibling will be discovered on the next invocation.
                print(f"SKIP vanished: {path}", file=sys.stderr)
            total += n
            if idx % 10 == 0 or idx == len(files):
                print(f"scanned {idx}/{len(files)} files, new events {total}", file=sys.stderr)
        rebuild_usage(conn)
        write_report(conn, known)
        print(f"Scanned {len(files)} files; inserted {total} new events.")
    else:
        rebuild_usage(conn)
    if args.json:
        rows = [dict(zip(("skill", "explicit_count", "read_count", "first_used", "last_used", "clients"), r)) for r in conn.execute("SELECT skill,explicit_count,read_count,first_used,last_used,clients FROM usage ORDER BY (explicit_count+read_count) DESC, skill")]
        print(json.dumps({"events": conn.execute("SELECT COUNT(*) FROM events").fetchone()[0], "skills": rows, "db": str(DB_PATH), "report": str(REPORT_PATH)}, ensure_ascii=False, indent=2))
    else:
        print_summary(conn, known, args.top)
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
