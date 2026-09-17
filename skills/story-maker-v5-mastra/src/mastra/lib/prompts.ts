import fs from "node:fs";
import path from "node:path";
import { SKILL_ROOT } from "../config.js";

const cache = new Map<string, string>();

/** Read a prompt template or asset doc shipped inside the skill dir. */
export function skillDoc(relPath: string): string {
  const abs = path.join(SKILL_ROOT, relPath);
  if (!cache.has(abs)) {
    cache.set(abs, fs.readFileSync(abs, "utf8"));
  }
  return cache.get(abs)!;
}

export function fileExists(...parts: string[]): boolean {
  return fs.existsSync(path.join(...parts));
}

export function readIfExists(...parts: string[]): string {
  const abs = path.join(...parts);
  return fs.existsSync(abs) ? fs.readFileSync(abs, "utf8") : "";
}

/** Inline several files into a labelled block for an agent prompt. */
export function contextBlock(files: Array<{ label: string; path: string }>): string {
  return files
    .filter((f) => fs.existsSync(f.path))
    .map((f) => `\n\n===== ${f.label} (${f.path}) =====\n${fs.readFileSync(f.path, "utf8")}`)
    .join("");
}
