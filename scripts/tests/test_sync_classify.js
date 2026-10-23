/**
 * Regression test for sync-skills-links.py link/directory classification.
 *
 * Three bugs were fixed here, each of which produced a silent wrong answer:
 *
 *   1. is_link() used only Path.is_symlink(), which is False for a Windows
 *      junction. The script creates junctions itself, then failed to recognise
 *      its own work.
 *
 *   2. skill_names() counted junctions as skill names, so a client whose
 *      skills/ dir contained `dotfiles -> repo` was reported as having
 *      "1 unique skill: dotfiles" and skipped as if it needed repair.
 *
 *   3. Nothing protected client-owned system directories. Codex keeps
 *      `~/.codex/skills/.system/` (imagegen, openai-docs, skill-creator...).
 *      Because dot-directories are excluded from skill_names(), that client
 *      looked empty and was scheduled for whole-directory replacement --
 *      which would have deleted Codex's own capabilities.
 *
 * This test builds a throwaway tree with all three shapes and asserts the
 * classifier gets each one right.
 */
const fs = require("fs");
const os = require("os");
const path = require("path");
const { execFileSync } = require("child_process");

const ROOT = path.join(os.tmpdir(), "pf_synctest");

function sh(cmd, args) {
  return execFileSync(cmd, args, { encoding: "utf8" });
}

// --- build the fixture -----------------------------------------------------
fs.rmSync(ROOT, { recursive: true, force: true });
const auth = path.join(ROOT, "repo", "skills");
fs.mkdirSync(path.join(auth, "skill-a"), { recursive: true });
fs.mkdirSync(path.join(auth, "skill-b"), { recursive: true });
fs.writeFileSync(path.join(auth, "skill-a", "SKILL.md"), "---\nname: skill-a\n---\n");

// client 1: plain real dir containing its own extra skill
const c1 = path.join(ROOT, "client1", "skills");
fs.mkdirSync(path.join(c1, "skill-a"), { recursive: true });
fs.mkdirSync(path.join(c1, "skill-own"), { recursive: true });

// client 2: skills/ dir is itself a junction to the repo
const c2 = path.join(ROOT, "client2", "skills");
fs.mkdirSync(path.dirname(c2), { recursive: true });
sh("cmd", ["/c", "mklink", "/J", c2, auth]);

// client 3: skills/ contains a client-owned system dir plus a junction child
const c3 = path.join(ROOT, "client3", "skills");
fs.mkdirSync(path.join(c3, ".system", "imagegen"), { recursive: true });
fs.writeFileSync(path.join(c3, ".system", "imagegen", "SKILL.md"), "x");
sh("cmd", ["/c", "mklink", "/J", path.join(c3, "dotfiles"), auth]);

// --- ask the python module what it thinks ----------------------------------
const PY = `
import importlib.util, json, sys
spec = importlib.util.spec_from_file_location(
    "s", r"${path.join(process.env.USERPROFILE || os.homedir(), "opencode-dotfiles", "scripts", "sync-skills-links.py")}")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
from pathlib import Path
root = Path(r"${ROOT}")
out = {
  "c1_is_link": m.is_link(root / "client1" / "skills"),
  "c2_is_link": m.is_link(root / "client2" / "skills"),
  "c2_target":  m.link_target(root / "client2" / "skills"),
  "c3_sysdirs": m.system_dirs(root / "client3" / "skills"),
  "c3_names":   sorted(m.skill_names(root / "client3" / "skills")),
  "c1_names":   sorted(m.skill_names(root / "client1" / "skills")),
  "auth_names": sorted(m.skill_names(root / "repo" / "skills")),
}
print(json.dumps(out))
`;

const raw = execFileSync("python", ["-X", "utf8", "-c", PY], { encoding: "utf8" });
const r = JSON.parse(raw.trim().split("\n").pop());

// --- assertions ------------------------------------------------------------
let fail = 0;
function ok(cond, label, detail) {
  console.log(`${cond ? "PASS" : "FAIL"}  ${label}`);
  if (detail) console.log(`        ${detail}`);
  if (!cond) fail++;
}

ok(r.c1_is_link === false, "real dir is NOT a link",
   `is_link(client1/skills) = ${r.c1_is_link}`);

ok(r.c2_is_link === true, "junction IS detected as a link",
   `is_link(client2/skills) = ${r.c2_is_link}`);

ok(path.resolve(r.c2_target || "") === path.resolve(auth),
   "junction target resolves to the repo",
   `got ${r.c2_target}`);

ok(Array.isArray(r.c3_sysdirs) && r.c3_sysdirs.includes(".system"),
   "client-owned system dir detected (blocks whole-dir replacement)",
   `system_dirs(client3/skills) = ${JSON.stringify(r.c3_sysdirs)}`);

ok(!r.c3_names.includes("dotfiles"),
   "junction child is NOT counted as a skill name (bug 2)",
   `skill_names(client3/skills) = ${JSON.stringify(r.c3_names)}`);

ok(r.c1_names.includes("skill-own"),
   "a real extra skill IS counted (so it can be protected)",
   `skill_names(client1/skills) = ${JSON.stringify(r.c1_names)}`);

console.log();
fs.rmSync(ROOT, { recursive: true, force: true });

if (fail) {
  console.log(`RESULT: ${fail} FAILURE(S)`);
  process.exit(1);
}
console.log("RESULT: PASS - link/junction/system-dir classification is correct");
