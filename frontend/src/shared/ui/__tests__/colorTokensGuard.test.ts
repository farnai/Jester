import test, { describe, it } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const SRC_DIR = path.resolve(__dirname, "../../..");

// Explicitly documented and justified exceptions
const ALLOWED_EXCEPTIONS = new Set([
  // Celestial planetary backdrop artwork (Saturn, Mars, Jupiter, etc. SVG art palette)
  path.normalize(path.join(SRC_DIR, "modules/auth/RegistrationScene.tsx")),
  // Official 3rd-party OAuth brand assets (Google 4-color SVG paths & Apple official logo)
  path.normalize(path.join(SRC_DIR, "modules/auth/SocialAuthButtons.tsx")),
  // Orphaned legacy stylesheet not imported by any route
  path.normalize(path.join(SRC_DIR, "modules/home/homeEditorial.css")),
  // HTML5 2D Canvas theme color fallback resolver
  path.normalize(path.join(SRC_DIR, "modules/home/ShareCardModal.tsx")),
]);

// Ignored non-active surfaces
const IGNORED_PATHS = [
  path.normalize("/modules/smoke_test/"),
  path.normalize("/modules/inspector/"),
  path.normalize("/modules/self/"),
  path.normalize("/shared/runtime/"),
  path.normalize("/shared/DebugBar.tsx"),
  path.normalize("/ui/VisualLab.tsx"),
  path.normalize("/ui/BackendAuditDebugPage.tsx"),
  path.normalize("/ui/tokens/"),
  path.normalize("/ui/primitives/"),
  path.normalize("/ui/tokensCatalogData.ts"),
  path.normalize("/colors.css"),
  path.normalize("/index.css"),
  path.normalize("/__tests__/"),
];

function getAllFiles(dir: string): string[] {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  const files: string[] = [];
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...getAllFiles(fullPath));
    } else if (entry.isFile() && /\.(tsx|ts|css)$/.test(entry.name)) {
      files.push(fullPath);
    }
  }
  return files;
}

function stripVars(input: string): string {
  let result = "";
  let i = 0;
  while (i < input.length) {
    if (input.slice(i, i + 4) === "var(") {
      let depth = 1;
      i += 4;
      while (i < input.length && depth > 0) {
        if (input[i] === "(") depth++;
        else if (input[i] === ")") depth--;
        i++;
      }
    } else {
      result += input[i];
      i++;
    }
  }
  return result;
}

export function scanForNakedColors(filePath: string): { line: number; raw: string; match: string }[] {
  const content = fs.readFileSync(filePath, "utf-8");
  const violations: { line: number; raw: string; match: string }[] = [];

  const lines = content.split("\n");
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Strip comments
    let stripped = line.replace(/\/\*.*?\*\//g, "").replace(/\/\/.*$/, "");

    // Strip var(...) usages including nested fallbacks
    stripped = stripVars(stripped);

    // Skip CSS mask-image linear-gradient stops that define alpha transparency channel
    if (stripped.includes("mask-image")) continue;

    // Skip standard neutral box-shadow elevation alphas (rgba(0,0,0,...) or rgba(34,38,48,...))
    stripped = stripped.replace(/rgba?\(\s*(0|34)\s*,\s*(0|38)\s*,\s*(0|48)\s*,\s*[\d.]+\s*\)/g, "");

    // Look for raw hex colors (#fff, #123456)
    const hexMatches = stripped.match(/#(?:[0-9a-fA-F]{3,4}){1,2}\b/g);
    if (hexMatches) {
      for (const m of hexMatches) {
        violations.push({ line: i + 1, raw: line.trim(), match: m });
      }
    }

    // Look for naked rgb/rgba
    const rgbMatches = stripped.match(/rgba?\([^)]+\)/g);
    if (rgbMatches) {
      for (const m of rgbMatches) {
        violations.push({ line: i + 1, raw: line.trim(), match: m });
      }
    }
  }

  return violations;
}

describe("Active UI Color Tokens Regression Guard", () => {
  it("should enforce that active user interface files contain zero unauthorized direct colors", () => {
    const allFiles = getAllFiles(SRC_DIR);
    const activeFiles = allFiles.filter((file) => {
      const normalized = path.normalize(file);
      if (ALLOWED_EXCEPTIONS.has(normalized)) return false;
      for (const ignored of IGNORED_PATHS) {
        if (normalized.includes(ignored)) return false;
      }
      return true;
    });

    const fileViolations: { file: string; violations: { line: number; raw: string; match: string }[] }[] = [];

    for (const file of activeFiles) {
      const v = scanForNakedColors(file);
      if (v.length > 0) {
        fileViolations.push({
          file: path.relative(SRC_DIR, file).replace(/\\/g, "/"),
          violations: v,
        });
      }
    }

    if (fileViolations.length > 0) {
      const message = fileViolations
        .map(
          (fv) =>
            `File: ${fv.file}\n` +
            fv.violations.map((v) => `  L${v.line}: ${v.match} in "${v.raw}"`).join("\n")
        )
        .join("\n\n");
      assert.fail(`Direct naked colors found in active UI outside centralized tokens:\n\n${message}`);
    }

    assert.equal(fileViolations.length, 0);
  });
});
