/**
 * Verify that the patched plugin would actually inject the bootstrap.
 *
 * The distinctive assertion: getBootstrapContent() must not return null, and the
 * content it returns must look like a routing prompt.
 *
 * Resolver duplicated here on purpose (it must match plugin/superpowers.js).
 */
const path = require("path");
const fs = require("fs");
const os = require("os");

const ROUTER_RELS = [
  ["using-superpowers", "SKILL.md"],
  ["function-specific", "misc", "superpowers", "using-superpowers", "SKILL.md"],
];

function normalizePath(p, home) {
  if (!p) return null;
  return path.resolve(p.replace(/^~(?=$|[\\/])/, home));
}

function findSkillsDir(configDir, homeDir, pluginDir, envVal) {
  const cands = [];
  const e = normalizePath(envVal, homeDir);
  if (e) cands.push(e);
  cands.push(path.join(configDir, "skills"));
  cands.push(path.join(homeDir, ".agents", "skills"));
  cands.push(path.resolve(pluginDir, "../skills"));
  cands.push(path.resolve(pluginDir, "../../skills"));

  for (const dir of cands) {
    for (const rel of ROUTER_RELS) {
      try {
        if (fs.existsSync(path.join(dir, ...rel))) return dir;
      } catch (_) {}
    }
  }
  return null;
}

const homeDir = os.homedir();
const configDir = path.join(homeDir, ".config", "opencode");
const pluginDir = path.join(configDir, "plugin");

console.log("home      :", homeDir);
console.log("configDir :", configDir);
console.log();

const dir = findSkillsDir(configDir, homeDir, pluginDir, null);
console.log("resolved  :", dir || "(none)");

if (!dir) {
  console.log("\nRESULT: FAIL - bootstrap would be null, skills never advertised");
  process.exit(1);
}

let skillPath = null;
for (const rel of ROUTER_RELS) {
  const p = path.join(dir, ...rel);
  if (fs.existsSync(p)) { skillPath = p; break; }
}
console.log("router    :", skillPath);
console.log("exists    :", !!skillPath);

if (!skillPath) {
  console.log("\nRESULT: FAIL - router skill not found under", dir);
  process.exit(1);
}

const raw = fs.readFileSync(skillPath, "utf8");
const body = raw.replace(/^---[\s\S]*?\n---\n/, "");
console.log("bootstrap :", body.length, "chars");

const mentionsSkill = /skill/i.test(body);
const mentionsRouting = /(L0|L1|L2|\u67e5|\u8def\u7531|invoke)/i.test(body);
const hasEnforcement = /(MUST|EXTREMELY|Red Flags)/.test(body);

console.log("\nmentions 'skill'   :", mentionsSkill);
console.log("mentions routing   :", mentionsRouting);
console.log("has enforcement    :", hasEnforcement);

console.log("\n--- first lines the model receives ---");
console.log(body.split("\n").slice(0, 5).join("\n"));

if (!mentionsSkill || !mentionsRouting) {
  console.log("\nRESULT: FAIL - content is not a router prompt");
  process.exit(1);
}
console.log("\nRESULT: PASS - bootstrap injects a router prompt");
