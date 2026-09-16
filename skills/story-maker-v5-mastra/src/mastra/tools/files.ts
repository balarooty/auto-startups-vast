import fs from "node:fs";
import path from "node:path";
import { createTool } from "@mastra/core/tools";
import { z } from "zod";
import { REPO_ROOT, SKILL_ROOT } from "../config.js";

// Agents may read anything under the skill dir (prompts/assets) or the repo's
// stories/ and outputs/ trees. Writes are limited to outputs/ run dirs.
function resolveRead(p: string): string {
  const abs = path.resolve(SKILL_ROOT, p);
  const allowed = [SKILL_ROOT, path.join(REPO_ROOT, "stories"), path.join(REPO_ROOT, "outputs")];
  if (!allowed.some((root) => abs === root || abs.startsWith(root + path.sep))) {
    throw new Error(`read_file: path outside allowed roots: ${abs}`);
  }
  return abs;
}

function resolveWrite(p: string): string {
  const abs = path.resolve(SKILL_ROOT, p);
  const root = path.join(REPO_ROOT, "outputs");
  if (!(abs === root || abs.startsWith(root + path.sep))) {
    throw new Error(`write_file: only outputs/ paths are writable: ${abs}`);
  }
  return abs;
}

export const readFileTool = createTool({
  id: "read_file",
  description:
    "Read a text file. Paths may be relative to the skill root or absolute. " +
    "Use it to consult asset docs (assets/*.md), prompt templates (prompts/*.md), " +
    "the story source, or previously authored run artifacts.",
  inputSchema: z.object({ path: z.string().describe("File path to read") }),
  outputSchema: z.object({ content: z.string() }),
  execute: async (input) => {
    const abs = resolveRead(input.path);
    if (!fs.existsSync(abs)) return { content: `__MISSING__: ${abs}` };
    return { content: fs.readFileSync(abs, "utf8") };
  },
});

export const writeFileTool = createTool({
  id: "write_file",
  description:
    "Write a file under the repo outputs/ tree (run artifacts). Parent dirs are created.",
  inputSchema: z.object({
    path: z.string().describe("Destination path under outputs/"),
    content: z.string().describe("Full file contents"),
  }),
  outputSchema: z.object({ written: z.string(), bytes: z.number() }),
  execute: async (input) => {
    const abs = resolveWrite(input.path);
    fs.mkdirSync(path.dirname(abs), { recursive: true });
    fs.writeFileSync(abs, input.content);
    return { written: abs, bytes: Buffer.byteLength(input.content) };
  },
});
