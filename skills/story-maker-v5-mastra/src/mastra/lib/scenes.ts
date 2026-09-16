import fs from "node:fs";
import path from "node:path";

/** Scene ids declared in scenes.md — `## Scene sN — title` / `scene_id: sN`. */
export function parseSceneIds(scenesMd: string): string[] {
  const ids = new Set<string>();
  for (const m of scenesMd.matchAll(/^## Scene (s\d+)\b/gm)) ids.add(m[1]);
  for (const m of scenesMd.matchAll(/^scene_id:\s*(s\d+)\s*$/gm)) ids.add(m[1]);
  return [...ids].sort((a, b) => Number(a.slice(1)) - Number(b.slice(1)));
}

/** Generation ids inside a storyboard — `## Generation gK — a-b s`. */
export function parseGenerationIds(storyboardMd: string): string[] {
  const ids = new Set<string>();
  for (const m of storyboardMd.matchAll(/^## Generation (g\d+)\b/gm)) ids.add(m[1]);
  return [...ids].sort((a, b) => Number(a.slice(1)) - Number(b.slice(1)));
}

/** Every (scene, gen) pair across all storyboard files on disk. */
export function generationPlan(runDir: string, sceneIds: string[]): Array<{ scene: string; gen: string }> {
  const plan: Array<{ scene: string; gen: string }> = [];
  for (const scene of sceneIds) {
    const board = path.join(runDir, `storyboard_${scene}.md`);
    if (!fs.existsSync(board)) continue;
    for (const gen of parseGenerationIds(fs.readFileSync(board, "utf8"))) {
      plan.push({ scene, gen });
    }
  }
  return plan;
}

/** Sheet image paths present on disk for a generation plan. */
export function sheetPaths(runDir: string, plan: Array<{ scene: string; gen: string }>): string[] {
  return plan
    .map(({ scene, gen }) => path.join(runDir, `storyboard_sheet_${scene}_${gen}.webp`))
    .filter((p) => fs.existsSync(p));
}
