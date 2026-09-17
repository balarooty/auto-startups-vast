import fs from "node:fs";
import path from "node:path";
import dotenv from "dotenv";

// The skill root is discovered by walking up from cwd (or STORY_MAKER_ROOT)
// looking for scripts/validate.py — this stays correct under both `mastra dev`
// and the compiled `.mastra/output` bundle.
function findSkillRoot(start: string): string {
  let dir = path.resolve(start);
  for (let i = 0; i < 8; i++) {
    if (fs.existsSync(path.join(dir, "scripts", "validate.py"))) return dir;
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  throw new Error(
    `Could not locate story-maker-v5-mastra skill root from ${start}. ` +
      `Run from inside the skill directory or set STORY_MAKER_ROOT.`,
  );
}

export const SKILL_ROOT = process.env.STORY_MAKER_ROOT
  ? path.resolve(process.env.STORY_MAKER_ROOT)
  : findSkillRoot(process.cwd());

export const REPO_ROOT = path.resolve(SKILL_ROOT, "..", "..");

// Repo-root .env is the canonical credentials file (FAL_KEY, REPLICATE_API_TOKEN,
// COMFYUI_URL, ...). A local .env inside the skill dir may add LLM_* vars.
dotenv.config({ path: path.join(REPO_ROOT, ".env") });
dotenv.config({ path: path.join(SKILL_ROOT, ".env") });

export const env = {
  storiesRoot: path.resolve(SKILL_ROOT, process.env.STORIES_ROOT ?? "stories"),
  outputsRoot: path.resolve(
    SKILL_ROOT,
    process.env.OUTPUTS_ROOT ?? "outputs/story-maker-v5-mastra",
  ),
  llmProvider: (process.env.LLM_PROVIDER ?? "anthropic").toLowerCase(),
  llmModel: process.env.LLM_MODEL ?? "",
  visionModel: process.env.VISION_MODEL ?? "",
  critiqueModel: process.env.CRITIQUE_MODEL ?? "",
  pythonBin: process.env.PYTHON_BIN ?? "python3",
  maxAuthoringAttempts: Number(process.env.MAX_AUTHORING_ATTEMPTS ?? 4),
  maxCritiqueRounds: Number(process.env.MAX_CRITIQUE_ROUNDS ?? 3),
};

export const runPath = (runDir: string, ...parts: string[]) =>
  path.join(runDir, ...parts);
