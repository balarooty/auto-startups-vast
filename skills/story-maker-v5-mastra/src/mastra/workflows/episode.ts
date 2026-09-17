import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { createStep, createWorkflow } from "@mastra/core/workflows";
import { z } from "zod";
import { env, runPath, SKILL_ROOT } from "../config.js";
import {
  beatBoard,
  critiqueAgent,
  imagePrompter,
  planFixer,
  sceneWriter,
  spatialPlanner,
  spatialQa,
  storyboardPlanner,
  storyDeveloper,
  videoPrompter,
} from "../agents/index.js";
import { authorArtifact, authorFileSet } from "../lib/authoring.js";
import { launchRenderDetached, mustRun, runPython, validateArtifact } from "../lib/python.js";
import { generationPlan, parseSceneIds, sheetPaths } from "../lib/scenes.js";

// ── Schemas ────────────────────────────────────────────────────────────────

const inputSchema = z.object({
  /** Series folder under stories/. */
  series: z.string().optional(),
  /** Episode number inside stories/<series>/episodes/. */
  episode: z.number().int().optional(),
  /** Explicit story file alternative to series+episode. */
  storyFile: z.string().optional(),
  /** Overrides episode_spec.target_seconds when >0. */
  targetSeconds: z.number().int().positive().optional(),
  /** How far to run: "plan" stops after critique, "sheets" after GATE 1. */
  mode: z.enum(["plan", "sheets", "full"]).default("full"),
});

const ctxSchema = z.object({
  runDir: z.string(),
  series: z.string(),
  episode: z.number(),
  targetSeconds: z.number(),
  intakeMode: z.string(),
  source: z.string(),
  mode: z.enum(["plan", "sheets", "full"]),
  scenes: z.array(z.string()).default([]),
  gates: z.record(z.string(), z.boolean()).default({}),
  status: z.string().default("running"),
});

type Ctx = z.infer<typeof ctxSchema>;

const reviewSchema = z.object({
  approved: z.boolean(),
  notes: z.string().optional(),
});

// ── Shared helpers ─────────────────────────────────────────────────────────

const specPath = (runDir: string) => runPath(runDir, "episode_spec.json");

function episodeContext(runDir: string) {
  return [
    { label: "episode spec", path: specPath(runDir) },
    { label: "story source", path: runPath(runDir, "story_source.md") },
    { label: "series bible", path: runPath(runDir, "series_bible.md") },
    { label: "developed story", path: runPath(runDir, "developed_story.md") },
    { label: "beat board", path: runPath(runDir, "beat_board.md") },
    { label: "scenes", path: runPath(runDir, "scenes.md") },
  ];
}

async function revalidateStageA(ctx: Ctx): Promise<string[]> {
  const failures: string[] = [];
  const run = ctx.runDir;
  const checks: Array<[string, string, string[]]> = [
    [runPath(run, "developed_story.md"), "screenplay", []],
    [runPath(run, "beat_board.md"), "beat_board", ["--target-seconds", String(ctx.targetSeconds)]],
    [
      runPath(run, "scenes.md"),
      "scenes",
      ["--target-seconds", String(ctx.targetSeconds), "--run-dir", run],
    ],
  ];
  for (const scene of ctx.scenes) {
    checks.push([runPath(run, `spatial_plan_${scene}.md`), "spatial_plan", ["--run-dir", run, "--scene", scene]]);
    checks.push([runPath(run, `storyboard_${scene}.md`), "storyboard", ["--scenes-path", runPath(run, "scenes.md")]]);
  }
  for (const [artifact, schema, args] of checks) {
    if (!fs.existsSync(artifact)) continue;
    const v = await validateArtifact(artifact, schema, args);
    if (!v.ok) failures.push(`${path.basename(artifact)}: ${v.errors.join("; ")}`);
  }
  return failures;
}

// ── Steps ──────────────────────────────────────────────────────────────────

const intakeStep = createStep({
  id: "intake",
  description: "Run prepare_episode.py and load the episode spec",
  inputSchema,
  outputSchema: ctxSchema,
  execute: async ({ inputData }) => {
    const args = [
      "--stories-root",
      env.storiesRoot,
      "--outputs-root",
      env.outputsRoot,
    ];
    if (inputData.storyFile) {
      args.push("--story-file", inputData.storyFile);
    } else if (inputData.series && inputData.episode !== undefined) {
      args.push("--series", inputData.series, "--episode", String(inputData.episode));
    } else {
      throw new Error("intake requires either storyFile or series+episode");
    }
    const res = await mustRun("scripts/prepare_episode.py", args);

    // prepare_episode prints "prepared <series>/epi-N" — resolve the spec
    // deterministically instead of scanning for the newest file.
    const m = res.stdout.match(/prepared\s+(\S+)\/epi-(\d+)/);
    if (!m) throw new Error(`could not parse prepare_episode output:\n${res.stdout}`);
    const specFile = path.join(env.outputsRoot, m[1], `epi-${m[2]}`, "episode_spec.json");
    const spec = JSON.parse(fs.readFileSync(specFile, "utf8"));
    return {
      runDir: spec.run_dir.startsWith("/") ? spec.run_dir : path.resolve(SKILL_ROOT, spec.run_dir),
      series: spec.series,
      episode: spec.episode,
      targetSeconds: (inputData.targetSeconds ?? Number(spec.target_seconds)) || 300,
      intakeMode: spec.intake_mode,
      source: spec.source,
      mode: inputData.mode,
      scenes: [],
      gates: {},
      status: "running",
    };
  },
});

const stageAStep = createStep({
  id: "stage-a-authoring",
  description: "Agents 1-4 author developed_story → beats → scenes → spatial plans → storyboards → image prompts, each under a write/validate/fix loop",
  inputSchema: ctxSchema,
  outputSchema: ctxSchema,
  execute: async ({ inputData }) => {
    const ctx: Ctx = { ...inputData };
    const run = ctx.runDir;
    const TARGET = String(ctx.targetSeconds);

    await authorArtifact(storyDeveloper, {
      artifactPath: runPath(run, "developed_story.md"),
      schema: "screenplay",
      task:
        `Author developed_story.md for run ${run} (target ${TARGET}s). ` +
        "Produce the full animation screenplay per assets/screenplay-format.md " +
        "(consult directors-guide.md, anime-studio-playbook.md, " +
        "unbound-storytelling-guide.md via read_file as needed), ending with " +
        "## Characters and ## Locations sections using stable char_NN / loc_NN ids. " +
        "Intake mode: " + ctx.intakeMode + ".",
      contextFiles: episodeContext(run).slice(0, 3),
    }).then(requireOk("developed_story.md"));

    await authorArtifact(beatBoard, {
      artifactPath: runPath(run, "beat_board.md"),
      schema: "beat_board",
      validateArgs: ["--target-seconds", TARGET],
      task:
        `Extract beat_board.md (8-15 dramatic beats with description/emotion/` +
        `estimated_seconds) from developed_story.md for target ${TARGET}s.`,
      contextFiles: [
        { label: "developed story", path: runPath(run, "developed_story.md") },
      ],
    }).then(requireOk("beat_board.md"));

    await authorArtifact(sceneWriter, {
      artifactPath: runPath(run, "scenes.md"),
      schema: "scenes",
      validateArgs: ["--target-seconds", TARGET, "--run-dir", run],
      task:
        `Author scenes.md grouping the beat board into scenes ` +
        `(scene_count = ceil(${TARGET} / 70)). Each ## Scene sN block needs ` +
        `scene_id, target_seconds, cast, characters_present, location_id, ` +
        `objects, beats, beat, plus style_target/acting_beat/layout_strategy/` +
        `visual_motif/sound_world. Per-scene targets must sum within 15% of ${TARGET}s.`,
      contextFiles: [
        { label: "developed story", path: runPath(run, "developed_story.md") },
        { label: "beat board", path: runPath(run, "beat_board.md") },
      ],
    }).then(requireOk("scenes.md"));

    ctx.scenes = parseSceneIds(fs.readFileSync(runPath(run, "scenes.md"), "utf8"));
    if (!ctx.scenes.length) throw new Error("scenes.md produced no scene ids");

    for (const scene of ctx.scenes) {
      // Spatial plan is advisory: a persistent failure falls back to legacy.
      const plan = await authorArtifact(spatialPlanner, {
        artifactPath: runPath(run, `spatial_plan_${scene}.md`),
        schema: "spatial_plan",
        validateArgs: ["--run-dir", run, "--scene", scene],
        task:
          `Author spatial_plan_${scene}.md for scene ${scene} of run ${run}: ` +
          "a 2.5D coordinate contract (landmarks, zones, per-generation and " +
          "per-shot spatial state). First establish the Dynamic Shot Depth & " +
          "Duration Plan per assets/production-rules.md §1.",
        contextFiles: episodeContext(run).slice(3),
      });
      if (!plan.ok) {
        fs.appendFileSync(
          runPath(run, "spatial_plan_warnings.log"),
          `${scene}: spatial plan failed validation — continuing with legacy behaviour\n${plan.errors.join("\n")}\n`,
        );
      }

      await authorArtifact(storyboardPlanner, {
        artifactPath: runPath(run, `storyboard_${scene}.md`),
        schema: "storyboard",
        validateArgs: ["--scenes-path", runPath(run, "scenes.md")],
        task:
          `Author storyboard_${scene}.md for scene ${scene}: ## Generation gK — ` +
          "a-b s blocks (each 5-15s, contiguous, summing to the scene target) " +
          "with panel_grid and ### Shot blocks. 15s is load-bearing; a shot " +
          "never straddles a generation boundary. Follow the Dynamic Shot Depth " +
          "plan — vary pacing (oners through montage), pair contrasting camera " +
          "angles, motivated movement.",
        contextFiles: [
          ...episodeContext(run).slice(2),
          { label: "spatial plan", path: runPath(run, `spatial_plan_${scene}.md`) },
        ],
      }).then(requireOk(`storyboard_${scene}.md`));

      const promptsOk = await authorFileSet(imagePrompter, {
        task:
          `Author the image prompts for scene ${scene} under ${run}/image_prompts/ ` +
          `using write_file for EVERY file: characters/<cid>.txt for each cast ` +
          `id, locations/<lid>.txt per location_id, objects/<oid>.txt, and ` +
          `${scene}/storyboard_sheet_<gen>.txt for every generation in the ` +
          `storyboard (format per prompts/storyboard_sheet_template.md — read ` +
          `it and prompts/character_sheet_template.md etc. via read_file). ` +
          `Skip files that already exist (shared across scenes).`,
        contextFiles: [
          { label: "storyboard", path: runPath(run, `storyboard_${scene}.md`) },
          { label: "spatial plan", path: runPath(run, `spatial_plan_${scene}.md`) },
          { label: "developed story", path: runPath(run, "developed_story.md") },
        ],
        validate: () =>
          validateArtifact(
            runPath(run, "image_prompts", scene, "storyboard_sheet_g1.txt"),
            "prompts",
            ["--run-dir", run, "--scene", scene],
          ),
      });
      requireOk(`image prompts for ${scene}`)({ ok: promptsOk.ok, errors: promptsOk.errors });
    }
    return ctx;
  },
});

const critiqueStep = createStep({
  id: "stage-a-critique",
  description: "Agent 6 evaluates all Stage A artifacts against the directing questions; fixer loop until zero FAILs, then a human override if it cannot converge",
  inputSchema: ctxSchema,
  outputSchema: ctxSchema,
  resumeSchema: z.object({ proceed: z.boolean(), notes: z.string().optional() }),
  suspendSchema: z.object({
    reason: z.string(),
    report: z.string(),
    errors: z.array(z.string()),
    rounds: z.number(),
  }),
  execute: async ({ inputData, resumeData, suspend }) => {
    const ctx: Ctx = { ...inputData };
    const run = ctx.runDir;
    const reportPath = runPath(run, "critique_report.md");

    // Resumed after a GATE 0 human review — proceed only on explicit approval.
    if (resumeData) {
      if (!resumeData.proceed) {
        return await suspend({
          reason: "GATE 0 still awaiting director disposition",
          report: reportPath,
          errors: [],
          rounds: env.maxCritiqueRounds,
        });
      }
      ctx.gates["gate-0"] = true;
      return ctx;
    }

    for (let round = 1; round <= env.maxCritiqueRounds; round++) {
      const res = await authorArtifact(critiqueAgent, {
        artifactPath: reportPath,
        schema: "critique",
        validateArgs: [
          "--question-bank",
          path.join(SKILL_ROOT, "assets", "directing-questions.md"),
        ],
        task:
          `Evaluate the full Stage A plan for run ${run} against ` +
          "assets/directing-questions.md (read it via read_file — evaluate ALL " +
          "questions across every section). Read every artifact under " +
          `${run} (developed_story.md, beat_board.md, scenes.md, ` +
          "spatial_plan_*.md, storyboard_*.md) and write critique_report.md " +
          "marking each question PASS/FAIL/ADVISORY with specifics.",
        contextFiles: [],
      });
      if (res.ok) {
        ctx.gates["gate-0"] = true;
        return ctx;
      }
      // Feed the FAILs to the fixer, then re-validate everything it touched.
      await planFixer.generate(
        `Critique round ${round} for run ${run} left these FAILs — fix the ` +
          `referenced artifacts under ${run}:\n` +
          res.errors.map((e) => `- ${e}`).join("\n") +
          `\n\nFull report: ${reportPath}`,
      );
      const stillBroken = await revalidateStageA(ctx);
      if (stillBroken.length) {
        throw new Error(
          `plan-fixer broke validation after critique round ${round}:\n${stillBroken.join("\n")}`,
        );
      }
    }

    return await suspend({
      reason:
        `GATE 0 unresolved after ${env.maxCritiqueRounds} critique/fix rounds — ` +
        "review the report and resume with { proceed: true } to override or " +
        "{ proceed: false } to hold.",
      report: reportPath,
      errors: lastErrors(reportPath),
      rounds: env.maxCritiqueRounds,
    });
  },
});

function lastErrors(reportPath: string): string[] {
  const p = `${reportPath}.validation.json`;
  if (!fs.existsSync(p)) return [];
  try {
    const j = JSON.parse(fs.readFileSync(p, "utf8"));
    return (j.errors ?? []).map(String);
  } catch {
    return [];
  }
}

const stageBStep = createStep({
  id: "stage-b-images",
  description: "Generate asset plates + storyboard sheets via Python, then spatial QA per scene",
  inputSchema: ctxSchema,
  outputSchema: ctxSchema,
  execute: async ({ inputData }) => {
    const ctx: Ctx = { ...inputData };
    if (ctx.mode === "plan") return { ...ctx, status: "plan-complete" };
    const run = ctx.runDir;

    await mustRun("scripts/build_images.py", ["--output-dir", run, "--assets-only"], 60 * 60 * 1000);
    for (const scene of ctx.scenes) {
      await mustRun("scripts/build_images.py", ["--output-dir", run, "--scene", scene], 60 * 60 * 1000);
    }

    // Agent 7 spatial QA — per-scene report, merged into spatial_qa_report.md.
    const reports: string[] = [];
    for (const scene of ctx.scenes) {
      const plan = runPath(run, `spatial_plan_${scene}.md`);
      if (!fs.existsSync(plan)) continue; // legacy fallback — skip Agent 7
      const gens = generationPlan(run, [scene]);
      const sheets = sheetPaths(run, gens);
      const sceneReport = runPath(run, `spatial_qa_report_${scene}.md`);
      const sha = (p: string) => crypto.createHash("sha256").update(fs.readFileSync(p)).digest("hex");
      const hashLines = [
        `spatial_plan_${scene}.md: ${sha(plan)}`,
        ...sheets.map((p) => `${path.basename(p)}: ${sha(p)}`),
      ].join("\n");
      await authorArtifact(spatialQa, {
        artifactPath: sceneReport,
        schema: "spatial_qa",
        validateArgs: ["--run-dir", run, "--scene", scene],
        task:
          `Inspect each storyboard sheet for scene ${scene} against ` +
          `${plan} (read it via read_file) and write the spatial QA report. ` +
          `Use these precomputed sha256 values verbatim in the report fields:\n` +
          hashLines,
        images: sheets.map((p) => ({ label: path.basename(p), path: p })),
      });
      reports.push(sceneReport);
    }
    if (reports.length) {
      fs.writeFileSync(
        runPath(run, "spatial_qa_report.md"),
        reports.map((r) => fs.readFileSync(r, "utf8")).join("\n\n"),
      );
    }
    return ctx;
  },
});

const gate1Step = createStep({
  id: "gate-1-sheets",
  description: "GATE 1 — human visual confirmation of all storyboard sheets + spatial QA report; assetctl approve-all on pass",
  inputSchema: ctxSchema,
  outputSchema: ctxSchema,
  resumeSchema: reviewSchema,
  suspendSchema: z.object({
    reason: z.string(),
    runDir: z.string(),
    sheets: z.array(z.string()),
    spatialQaReport: z.string(),
    notes: z.string().optional(),
  }),
  execute: async ({ inputData, resumeData, suspend }) => {
    const ctx: Ctx = { ...inputData };
    if (ctx.mode === "plan") return { ...ctx, status: "plan-complete" };
    const run = ctx.runDir;
    const gens = generationPlan(run, ctx.scenes);
    const sheets = sheetPaths(run, gens);
    const qaReport = runPath(run, "spatial_qa_report.md");

    // A BLOCKER in spatial QA halts the gate even if the human tries to approve.
    const qa = fs.existsSync(qaReport) ? fs.readFileSync(qaReport, "utf8") : "";
    if (resumeData?.approved && /^-?\s*Blocker:\s*[1-9]/m.test(qa)) {
      return await suspend({
        reason: "GATE 1 halted — spatial_qa_report.md contains BLOCKER entries",
        runDir: run,
        sheets,
        spatialQaReport: qaReport,
      });
    }

    if (!resumeData?.approved) {
      return await suspend({
        reason:
          "GATE 1 — visually confirm every storyboard sheet (clean equal " +
          "panels, no text, consistent characters, readable motion) and the " +
          "spatial QA report. Resume { approved: true } to continue, or " +
          "{ approved: false, notes } to send feedback.",
        runDir: run,
        sheets,
        spatialQaReport: fs.existsSync(qaReport) ? qaReport : "(none)",
        notes: resumeData?.notes,
      });
    }

    await mustRun("scripts/assetctl.py", ["--run-dir", run, "approve-all"]);
    ctx.gates["gate-1"] = true;
    return ctx;
  },
});

const stageCStep = createStep({
  id: "stage-c-video-prompts",
  description: "Agent 5 authors a Ref2VA video prompt per generation, reading the actual sheet image",
  inputSchema: ctxSchema,
  outputSchema: ctxSchema,
  execute: async ({ inputData }) => {
    const ctx: Ctx = { ...inputData };
    if (ctx.mode !== "full") return { ...ctx, status: "sheets-complete" };
    const run = ctx.runDir;
    const bible = (name: string) => path.join(SKILL_ROOT, "assets", name);

    for (const { scene, gen } of generationPlan(run, ctx.scenes)) {
      const sheet = runPath(run, `storyboard_sheet_${scene}_${gen}.webp`);
      await authorArtifact(videoPrompter, {
        artifactPath: runPath(run, "video_prompts", `${scene}_${gen}.txt`),
        schema: "video_prompt",
        validateArgs: ["--run-dir", run, "--scene", scene],
        task:
          `Author the Ref2VA video prompt for ${scene}/${gen} of run ${run}. ` +
          "THE SHEET IMAGE WINS OVER THE PLAN — describe what is actually " +
          "drawn. 6 sections: subject_definitions / summary / retention_analysis " +
          "/ detailed_description / overall_soundscape / non_diegetic_music. " +
          "Generation-local [Shot N] At MM:SS.mmm timestamps, 8-value transition " +
          "grammar, <d>[English] dialogue with (SN) speaker bindings, declare " +
          "<Audio 1> iff an audio ref is attached to this generation. Consult " +
          "the prompt bibles via read_file: " +
          [bible("minimax-h3-prompt-bible.md"), bible("minimax-h3-modes-guide.md"), bible("cinematography-bible.md")].join(", "),
        contextFiles: [
          { label: "storyboard", path: runPath(run, `storyboard_${scene}.md`) },
          { label: "spatial plan", path: runPath(run, `spatial_plan_${scene}.md`) },
          { label: "developed story", path: runPath(run, "developed_story.md") },
        ],
        images: [{ label: `storyboard_sheet_${scene}_${gen}`, path: sheet }],
      }).then(requireOk(`video prompt ${scene}/${gen}`));
    }
    return ctx;
  },
});

const manifestStep = createStep({
  id: "manifest",
  description: "Build + approve render_manifest.json (immutable content-addressed lock)",
  inputSchema: ctxSchema,
  outputSchema: ctxSchema,
  execute: async ({ inputData }) => {
    if (inputData.mode !== "full") return { ...inputData, status: "sheets-complete" };
    await mustRun("scripts/build_manifest.py", [inputData.runDir, "--approve"]);
    return inputData;
  },
});

const gate2Step = createStep({
  id: "gate-2-render",
  description: "GATE 2 — human confirms the locked render manifest before paid GPU render",
  inputSchema: ctxSchema,
  outputSchema: ctxSchema,
  resumeSchema: reviewSchema,
  suspendSchema: z.object({
    reason: z.string(),
    runDir: z.string(),
    manifest: z.string(),
    prompts: z.array(z.string()),
    notes: z.string().optional(),
  }),
  execute: async ({ inputData, resumeData, suspend }) => {
    const ctx: Ctx = { ...inputData };
    if (ctx.mode !== "full") return { ...ctx, status: "sheets-complete" };
    const run = ctx.runDir;
    if (!resumeData?.approved) {
      return await suspend({
        reason:
          "GATE 2 — review render_manifest.json and the video prompts before " +
          "the paid render. Resume { approved: true } to launch, or " +
          "{ approved: false, notes } to hold.",
        runDir: run,
        manifest: runPath(run, "render_manifest.json"),
        prompts: fs.existsSync(runPath(run, "video_prompts"))
          ? fs.readdirSync(runPath(run, "video_prompts")).map((f) => runPath(run, "video_prompts", f))
          : [],
        notes: resumeData?.notes,
      });
    }
    ctx.gates["gate-2"] = true;
    return ctx;
  },
});

const renderStep = createStep({
  id: "stage-d-render",
  description: "Launch render_all.py detached — sequential tail-conditioned Minimax H3 render, hours",
  inputSchema: ctxSchema,
  outputSchema: ctxSchema,
  execute: async ({ inputData }) => {
    const ctx: Ctx = { ...inputData };
    if (ctx.mode !== "full") return { ...ctx, status: "sheets-complete" };
    const { pid, logFile } = launchRenderDetached(ctx.runDir);
    ctx.status = `rendering (pid ${pid})`;
    await runPython("scripts/episode_status.py", [
      "--run-dir",
      ctx.runDir,
      "--set",
      "rendering",
    ]);
    fs.appendFileSync(
      logFile,
      `\n[mastra] launched at ${new Date().toISOString()} pid=${pid}\n`,
    );
    return ctx;
  },
});

function requireOk(what: string) {
  return (r: { ok: boolean; errors: string[] }) => {
    if (!r.ok) throw new Error(`${what} failed validation after all attempts:\n${r.errors.join("\n")}`);
    return r;
  };
}

// Mode routing: `plan` stops after the critique gate (no image spend),
// `sheets` additionally runs Stage B and suspends at GATE 1, `full` runs
// everything through the detached render. Each step early-returns on mode so
// the chain stays linear and the ctx contract survives a short-circuited run.
export const episodeWorkflow = createWorkflow({
  id: "episode",
  description:
    "story-maker-v5 pipeline as a service: intake → Stage A authoring → " +
    "critique (GATE 0) → image build → GATE 1 → video prompts → manifest → " +
    "GATE 2 → detached render",
  inputSchema,
  outputSchema: ctxSchema,
})
  .then(intakeStep)
  .then(stageAStep)
  .then(critiqueStep)
  .then(stageBStep)
  .then(gate1Step)
  .then(stageCStep)
  .then(manifestStep)
  .then(gate2Step)
  .then(renderStep)
  .commit();
