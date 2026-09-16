import fs from "node:fs";
import path from "node:path";
import type { Agent } from "@mastra/core/agent";
import { env } from "../config.js";
import { contextBlock } from "./prompts.js";
import { validateArtifact } from "./python.js";

export interface AuthorJob {
  /** Where the artifact lands on disk. */
  artifactPath: string;
  /** validate.py schema name, e.g. "storyboard". */
  schema: string;
  /** Extra validate.py args, e.g. ["--scene", "s1", "--run-dir", runDir]. */
  validateArgs?: string[];
  /** The task for the agent — what to author and which contract to follow. */
  task: string;
  /** Files inlined into the first prompt as labelled context. */
  contextFiles?: Array<{ label: string; path: string }>;
  /** Image paths attached as vision input (sheet review agents). */
  images?: Array<{ label: string; path: string }>;
  maxAttempts?: number;
}

export interface AuthorResult {
  artifactPath: string;
  ok: boolean;
  attempts: number;
  errors: string[];
  warnings: string[];
}

interface ImagePart {
  type: "image";
  image: Buffer;
  mediaType?: string;
}

const MIME: Record<string, string> = {
  ".webp": "image/webp",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
};

/**
 * The write → validate → fix loop that the SKILL.md runbook performs by hand:
 * generate the artifact, write it, run the deterministic validator, feed the
 * errors back, retry until ok:true (or attempts exhausted).
 */
export async function authorArtifact(agent: Agent, job: AuthorJob): Promise<AuthorResult> {
  const maxAttempts = job.maxAttempts ?? env.maxAuthoringAttempts;
  fs.mkdirSync(path.dirname(job.artifactPath), { recursive: true });

  const imageParts: ImagePart[] = (job.images ?? [])
    .filter((img) => fs.existsSync(img.path))
    .map((img) => ({
      type: "image" as const,
      image: fs.readFileSync(img.path),
      mediaType: MIME[path.extname(img.path).toLowerCase()],
    }));

  const messages: Array<
    | { role: "user"; content: string | Array<{ type: "text"; text: string } | ImagePart> }
    | { role: "assistant"; content: string }
  > = [
    {
      role: "user",
      content:
        imageParts.length > 0
          ? [
              { type: "text", text: job.task + contextBlock(job.contextFiles ?? []) },
              ...imageParts,
            ]
          : job.task + contextBlock(job.contextFiles ?? []),
    },
  ];

  let lastErrors: string[] = [];
  let lastWarnings: string[] = [];

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    const result = await agent.generate(messages as never, { maxSteps: 8 });
    const text = String(result.text ?? "").trim();
    if (text) {
      fs.writeFileSync(job.artifactPath, text.endsWith("\n") ? text : `${text}\n`);
    }
    messages.push({ role: "assistant", content: text });

    const verdict = await validateArtifact(job.artifactPath, job.schema, job.validateArgs ?? []);
    lastErrors = verdict.errors;
    lastWarnings = verdict.warnings;
    if (verdict.ok) {
      return { artifactPath: job.artifactPath, ok: true, attempts: attempt, errors: [], warnings: lastWarnings };
    }

    messages.push({
      role: "user",
      content:
        `The artifact failed validation (attempt ${attempt}/${maxAttempts}). ` +
        `Rewrite the COMPLETE artifact fixing every error — do not explain, output the artifact only.\n` +
        `Validator errors:\n${verdict.errors.map((e) => `- ${e}`).join("\n")}`,
    });
  }

  return { artifactPath: job.artifactPath, ok: false, attempts: maxAttempts, errors: lastErrors, warnings: lastWarnings };
}

export interface MultiFileJob {
  task: string;
  contextFiles?: Array<{ label: string; path: string }>;
  images?: Array<{ label: string; path: string }>;
  /** Deterministic check run after each generation — the validator covers the
   * set of files the agent was asked to write via write_file. */
  validate: () => Promise<{ ok: boolean; errors: string[]; warnings?: string[] }>;
  maxAttempts?: number;
}

/**
 * Same write→validate→fix loop for agents that author a SET of files
 * (e.g. image-prompter writes char/loc/object/sheet prompts) — the agent
 * writes via write_file; the step only re-validates and feeds errors back.
 */
export async function authorFileSet(agent: Agent, job: MultiFileJob): Promise<{ ok: boolean; errors: string[] }> {
  const maxAttempts = job.maxAttempts ?? env.maxAuthoringAttempts;
  const messages: Array<{ role: "user" | "assistant"; content: string }> = [
    { role: "user", content: job.task + contextBlock(job.contextFiles ?? []) },
  ];
  let lastErrors: string[] = [];
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    const result = await agent.generate(messages as never, { maxSteps: 12 });
    messages.push({ role: "assistant", content: String(result.text ?? "") });
    const verdict = await job.validate();
    if (verdict.ok) return { ok: true, errors: [] };
    lastErrors = verdict.errors;
    messages.push({
      role: "user",
      content:
        `Validation failed (attempt ${attempt}/${maxAttempts}). Fix the files ` +
        `with write_file — rewrite the COMPLETE content of each broken file.\n` +
        `Errors:\n${lastErrors.map((e) => `- ${e}`).join("\n")}`,
    });
  }
  return { ok: false, errors: lastErrors };
}
