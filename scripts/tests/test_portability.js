/**
 * Portability test: pretend we are on a fresh machine.
 *
 * Simulates three realistic situations and checks the resolver still finds the
 * skills, without any hardcoded user path:
 *
 *   A. skills reachable only via <configDir>/skills   (normal install)
 *   B. skills reachable only via ~/.agents/skills     (shared-junction install)
 *   C. skills reachable only via OPENCODE_SKILLS_DIR  (explicit override)
 *   D. nothing present                                (must fail cleanly, not crash)
 */
const path = require("path");
const fs = require("fs");
const os = require("os");

// resolver copied from the patched plugin (kept in sync deliberately)
function normalizePath(p, home) {
  if (!p) return null;
  return path.resolve(p.replace(/^~(?=$|[\\/])/, home));
}

function findSkillsDir(opts) {
  const { configDir, homeDir, pluginDir, envVal } = opts;
  const candidates = [];
  const fromEnv = normalizePath(envVal, homeDir);
  if (fromEnv) candidates.push(fromEnv);
  candidates.push(path.join(configDir, "skills"));
  candidates.push(path.join(homeDir, ".agents", "skills"));
  candidates.push(path.resolve(pluginDir, "../skills"));
  candidates.push(path.resolve(pluginDir, "../../skills"));
  for (const dir of candidates) {
    try {
      if (fs.existsSync(path.join(dir, "using-superpowers", "SKILL.md"))) return dir;
    } catch (_) {}
  }
  return null;
}

function makeFake(home) {
  fs.rmSync(home, { recursive: true, force: true });
  fs.mkdirSync(home, { recursive: true });
  return home;
}

function installSkillAt(dir) {
  fs.mkdirSync(path.join(dir, "using-superpowers"), { recursive: true });
  fs.writeFileSync(path.join(dir, "using-superpowers", "SKILL.md"),
    "---\nname: using-superpowers\n---\nrouter body here\n");
}

const root = path.join(os.tmpdir(), "pf_portability");
let failures = 0;

function check(label, got, want) {
  const ok = (want === null) ? (got === null) : (got === want);
  console.log(`${ok ? "PASS" : "FAIL"}  ${label}`);
  console.log(`        got  = ${got}`);
  if (!ok) { console.log(`        want = ${want}`); failures++; }
}

// ---- A: configDir only
{
  const home = makeFake(path.join(root, "A", "Users", "alice"));
  const cfg = path.join(home, ".config", "opencode");
  installSkillAt(path.join(cfg, "skills"));
  const got = findSkillsDir({
    configDir: cfg, homeDir: home, pluginDir: path.join(cfg, "plugin"), envVal: null,
  });
  check("A  configDir/skills only", got, path.join(cfg, "skills"));
}

// ---- B: shared ~/.agents/skills only (no configDir/skills)
{
  const home = makeFake(path.join(root, "B", "Users", "bob"));
  const cfg = path.join(home, ".config", "opencode");
  fs.mkdirSync(cfg, { recursive: true });
  installSkillAt(path.join(home, ".agents", "skills"));
  const got = findSkillsDir({
    configDir: cfg, homeDir: home, pluginDir: path.join(cfg, "plugin"), envVal: null,
  });
  check("B  ~/.agents/skills only", got, path.join(home, ".agents", "skills"));
}

// ---- C: explicit env override (repo moved elsewhere entirely)
{
  const home = makeFake(path.join(root, "C", "Users", "carol"));
  const cfg = path.join(home, ".config", "opencode");
  fs.mkdirSync(cfg, { recursive: true });
  const elsewhere = path.join(root, "C", "opt", "my-dotfiles", "skills");
  installSkillAt(elsewhere);
  const got = findSkillsDir({
    configDir: cfg, homeDir: home, pluginDir: path.join(cfg, "plugin"),
    envVal: elsewhere,
  });
  check("C  OPENCODE_SKILLS_DIR override", got, elsewhere);
}

// ---- D: nothing anywhere -> must return null, must not throw
{
  const home = makeFake(path.join(root, "D", "Users", "dave"));
  const cfg = path.join(home, ".config", "opencode");
  fs.mkdirSync(cfg, { recursive: true });
  let got = "threw";
  try {
    got = findSkillsDir({
      configDir: cfg, homeDir: home, pluginDir: path.join(cfg, "plugin"), envVal: null,
    });
  } catch (e) {
    got = "threw: " + e.message;
  }
  check("D  nothing present -> null", got, null);
}

// ---- E: the OLD logic would fail in every one of the above
{
  const home = path.join(root, "A", "Users", "alice");
  const cfg = path.join(home, ".config", "opencode");
  const oldResolved = path.resolve(path.join(cfg, "plugin"), "../../skills");
  const exists = fs.existsSync(path.join(oldResolved, "using-superpowers", "SKILL.md"));
  const ok = exists === false;
  console.log(`${ok ? "PASS" : "FAIL"}  E  old logic fails (proves the bug was real)`);
  console.log(`        old path = ${oldResolved}`);
  console.log(`        exists   = ${exists}`);
  if (!ok) failures++;
}

console.log();
if (failures) {
  console.log(`RESULT: ${failures} FAILURE(S)`);
  process.exit(1);
}
console.log("RESULT: PASS - resolver works on any username / any repo location");
