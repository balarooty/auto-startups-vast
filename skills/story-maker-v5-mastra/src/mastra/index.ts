import path from "node:path";
import { Mastra } from "@mastra/core/mastra";
import { LibSQLStore } from "@mastra/libsql";
import { SKILL_ROOT } from "./config.js";
import { agents } from "./agents/index.js";
import { episodeWorkflow } from "./workflows/episode.js";

export const mastra = new Mastra({
  agents,
  workflows: { episode: episodeWorkflow },
  // Workflow snapshots (suspend/resume state for GATE 0/1/2) persist here.
  // Run *content* stays on the filesystem — outputs/ and render_state.json
  // remain the source of truth for resume.
  storage: new LibSQLStore({
    id: "story-maker-v5-mastra",
    url: `file:${path.join(SKILL_ROOT, ".mastra", "mastra.db")}`,
  }),
});
