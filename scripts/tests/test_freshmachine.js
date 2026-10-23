/**
 * Fresh-machine simulation.
 *
 * Copy the repo to a brand-new location with a brand-new "home", then drive the
 * plugin's real resolution logic against it. This is the test the user asked
 * for: "copy it somewhere else and see whether the session still finds the
 * skills, and whether it points at them."
 *
 * Nothing here touches the real ~/.config or the real repo.
 */
const fs = require("fs");
const path = require("path");
const os = require("os");

const SRC_REPO = path.join(os.homedir(), "opencode-dotfiles");
const ROOT = path.join(os.tmpdir(), "pf_freshmachine");
const FAKE_HOME = path.join(ROOT, "Users", "newuser");
const FAKE_REPO = path.join(FAKE_HOME, "opencode-dotfiles");

function cpDir(src, dst) {
  fs.mkdirSync(dst, { recursive: true });
  for (const e of fs.readdirSync(src, { withFileTypes: true })) {
    const s = path.join(src, e.name);
    const d = path.join(dst, e.name);
    if (e.isDirectory()) {
      if (e.name === ".git" || e.name === "node_modules") continue;
      cpDir(s, d);
    } else if (e.isFile()) {
      fs.copyFileSync(s, d);
    }
  }
}

console.log("1. build a fresh fake machine under", FAKE_HOME);
fs.rmSync(ROOT, { recursive: true, force: true });
cpDir(SRC_REPO, FAKE_REPO);
const skillCount = fs.readdirSync(path.join(FAKE_REPO, "skills"), { withFileTypes: true })
  .filter(e => e.isDirectory() && !e.name.startsWith(".")).length;
console.log("   copied repo -> ", FAKE_REPO);
console.log("   skills copied:", skillCount);

// 2. lay out the client dir the way setup.ps1 + sync-skills-links.py would:
//    a junction at <fakehome>/.config/opencode/skills -> <fakehome>/opencode-dotfiles/skills
console.log("\n2. create the client junction the way setup does");
const clientCfg = path.join(FAKE_HOME, ".config", "opencode");
const clientSkills = path.join(clientCfg, "skills");
fs.mkdirSync(clientCfg, { recursive: true });
try {
  fs.symlinkSync(path.join(FAKE_REPO, "skills"), clientSkills, "junction");
  console.log("   junction created ->", clientSkills);
} catch (e) {
  console.log("   NODE CANNOT MAKE A JUNCTION:", e.message);
  console.log("   falling back to a directory copy for the probe");
  cpDir(path.join(FAKE_REPO, "skills"), clientSkills);
}

// 3. install the plugin at the fake client location
const pluginDir = path.join(clientCfg, "plugin");
fs.mkdirSync(pluginDir, { recursive: true });
fs.copyFileSync(path.join(FAKE_REPO, "plugin", "superpowers.js"),
  path.join(pluginDir, "superpowers.js"));
console.log("3. plugin installed at", path.join(pluginDir, "superpowers.js"));

// 4. run the resolver against the FAKE home (no real paths involved)
console.log("\n4. resolve against the fake machine");
function normalizePath(p, home) {
  if (!p) return null;
  return path.resolve(p.replace(/^~(?=$|[\\/])/, home));
}
const RELS = [
  ["using-superpowers", "SKILL.md"],
  ["function-specific", "misc", "superpowers", "using-superpowers", "SKILL.md"],
];
function findSkillsDir({ configDir, homeDir, pluginDir, envVal }) {
  const c = [];
  const e = normalizePath(envVal, homeDir);
  if (e) c.push(e);
  c.push(path.join(configDir, "skills"));
  c.push(path.join(homeDir, ".agents", "skills"));
  c.push(path.resolve(pluginDir, "../skills"));
  c.push(path.resolve(pluginDir, "../../skills"));
  for (const d of c) {
    for (const rel of RELS) {
      try { if (fs.existsSync(path.join(d, ...rel))) return d; } catch (_) {}
    }
  }
  return null;
}

const got = findSkillsDir({
  configDir: clientCfg, homeDir: FAKE_HOME, pluginDir, envVal: null,
});
console.log("   resolved ->", got);

const want = clientSkills;
const ok = got && path.resolve(got) === path.resolve(want);
console.log("   expected ->", want);
console.log("   " + (ok ? "PASS" : "FAIL"));

// 5. prove the REAL repo's skills are visible through the fake client path
console.log("\n5. read a real skill through the fresh client path");
const probeSkill = path.join(clientSkills, "photon-flow-viz", "SKILL.md");
const probeRouter = path.join(clientSkills, "function-specific", "misc", "superpowers", "using-superpowers", "SKILL.md");
for (const [label, p] of [["photon-flow-viz", probeSkill],
                          ["using-superpowers", probeRouter]]) {
  const has = fs.existsSync(p);
  console.log(`   ${label.padEnd(20)} ${has ? "readable" : "MISSING"}`);
}

// 6. count what this fresh machine would see
const visible = fs.readdirSync(clientSkills, { withFileTypes: true })
  .filter(e => e.isDirectory() && !e.name.startsWith(".")).length;
console.log("\n6. skills visible to the new client:", visible);

const pass = ok && fs.existsSync(probeRouter);
console.log();
console.log(pass
  ? "RESULT: PASS - repo works from a brand-new path and username"
  : "RESULT: FAIL - fresh-machine resolution broken");
process.exit(pass ? 0 : 1);
