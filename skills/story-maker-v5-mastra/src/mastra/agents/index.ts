import { Agent } from "@mastra/core/agent";
import { modelFor } from "../provider.js";
import { skillDoc } from "../lib/prompts.js";
import { readFileTool, writeFileTool } from "../tools/files.js";

/**
 * One Mastra agent per prompts/*.md template — the same "agent roster" the
 * SKILL.md runbook defines, but as isolated agents instead of roleplayed
 * personas in one context. Each agent's instructions are the verbatim prompt
 * file; large reference docs are consulted on demand via read_file.
 */

const authoringTools = { read_file: readFileTool };
const reviewTools = { read_file: readFileTool, write_file: writeFileTool };

function makeAgent(id: string, promptFile: string, role: "authoring" | "vision" | "critique", tools = authoringTools) {
  return new Agent({
    id,
    name: id,
    instructions: [
      skillDoc(promptFile),
      "",
      "You are a pipeline agent inside a Mastra workflow. Output ONLY the artifact " +
        "document itself — no preamble, no explanations, no markdown fences around the " +
        "whole reply. If you need a reference doc listed in your instructions, call " +
        "read_file on it (paths like assets/<name>.md resolve inside the skill).",
    ].join("\n"),
    model: modelFor(role, id),
    tools,
  });
}

export const storyDeveloper = makeAgent("story-developer", "prompts/story_developer.md", "authoring");
export const beatBoard = makeAgent("beat-board", "prompts/beat_board.md", "authoring");
export const sceneWriter = makeAgent("scene-writer", "prompts/scene_writer.md", "authoring");
export const spatialPlanner = makeAgent("spatial-planner", "prompts/spatial_planner.md", "authoring");
export const storyboardPlanner = makeAgent("storyboard-planner", "prompts/storyboard_planner.md", "authoring");
// Image-prompter authors a set of files (char/loc/object/sheet prompts), so it
// gets write_file — the step re-validates rather than writing its reply.
export const imagePrompter = makeAgent("image-prompter", "prompts/image_prompter.md", "authoring", reviewTools);

export const critiqueAgent = makeAgent("critique-agent", "prompts/critique_agent.md", "critique", reviewTools);

// Vision agents receive the actual storyboard sheet image bytes in the prompt —
// the "sheet wins over the plan" policy only works if the model sees the pixels.
export const videoPrompter = makeAgent("video-prompter", "prompts/video_prompter.md", "vision");
export const spatialQa = makeAgent("spatial-qa", "prompts/spatial_qa_agent.md", "vision", reviewTools);

// Stage-A fixer: turns critique FAILs into concrete artifact edits.
export const planFixer = new Agent({
  id: "plan-fixer",
  name: "plan-fixer",
  instructions: [
    "You are the director-fixer in a story-to-video pipeline. You are given a critique ",
    "report with FAILed directing questions and the artifacts it flagged. Read the ",
    "referenced artifacts with read_file, fix ONLY what the critique flags (preserve ",
    "everything that passed — formats, ids, shot counts, transitions), and rewrite the ",
    "full corrected files with write_file. The artifact formats are defined in ",
    "prompts/*.md and assets/screenplay-format.md — consult them when unsure. When ",
    "done, reply with a one-line list of files you rewrote.",
  ].join(""),
  model: modelFor("critique", "plan-fixer"),
  tools: reviewTools,
});

export const agents = {
  "story-developer": storyDeveloper,
  "beat-board": beatBoard,
  "scene-writer": sceneWriter,
  "spatial-planner": spatialPlanner,
  "storyboard-planner": storyboardPlanner,
  "image-prompter": imagePrompter,
  "critique-agent": critiqueAgent,
  "video-prompter": videoPrompter,
  "spatial-qa": spatialQa,
  "plan-fixer": planFixer,
};
