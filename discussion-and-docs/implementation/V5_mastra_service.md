# V5 — Mastra service variant (`story-maker-v5-mastra`)

## Goal

Turn the `story-maker-v5` agent-skill pipeline into a standalone service: the
same Ref2VA pipeline driven by a typed Mastra workflow over HTTP instead of a
runbook a host agent (Claude/Devin) executes inside a session. The original
skill at `skills/story-maker-v5/` is untouched — the variant is a copy at
`skills/story-maker-v5-mastra/` with a `src/mastra/` orchestrator added.

## Decisions

- **Python hands stay verbatim.** `tools/`, `scripts/`, `prompts/`, `assets/`,
  `tests/` copied unchanged; the Mastra layer invokes them via child_process.
  All prompt craft, validators, manifest locking, and fingerprint resume are
  reused as-is.
- **Filesystem remains source of truth.** `outputs/` artifacts +
  `render_state.json` carry resume data; Mastra's LibSQL snapshot store only
  tracks which step a run is on (needed for gate suspend/resume).
- **Runbook → workflow.** `src/mastra/workflows/episode.ts` is a linear chain:
  `intake → stage-a-authoring → stage-a-critique → stage-b-images →
  gate-1-sheets → stage-c-video-prompts → manifest → gate-2-render →
  stage-d-render`. `mode` input (`plan|sheets|full`) early-returns each step
  so short-circuited runs still satisfy the ctx contract.
- **Gates are code now.** GATE 1/2 are `suspend()`/`resume()` steps; rejection
  re-suspends with notes instead of failing. GATE 0's critique/fix loop is
  automatic up to `MAX_CRITIQUE_ROUNDS`, then suspends for director override.
- **Write→validate→fix is a loop, not a discipline.** `lib/authoring.ts`
  implements `authorArtifact` (one file per call, text written by the step)
  and `authorFileSet` (agent writes N files via `write_file`; the step
  re-validates). Each retries with validator errors fed back, capped by
  `MAX_AUTHORING_ATTEMPTS`.
- **Agents are isolated.** One Mastra agent per `prompts/*.md` (10 total
  incl. plan-fixer). Instructions = the verbatim prompt file; big asset docs
  are pulled on demand via a repo-scoped `read_file` tool.
- **Vision agents get real pixels.** video-prompter and spatial-qa receive the
  storyboard sheet image bytes in the prompt — the "sheet wins over the plan"
  policy needs actual image input, not a description.
- **Model config via env.** `LLM_PROVIDER` + `LLM_MODEL` / `VISION_MODEL` /
  `CRITIQUE_MODEL` + `MODEL_<AGENT_ID>` overrides; bare model ids get the
  provider prepended, `provider/model` values pass through.
- **Intake is deterministic.** The intake step parses
  `prepared <series>/epi-N` from `prepare_episode.py` stdout rather than
  scanning for the newest spec file.
- **Stage D stays detached.** `render_all.py` is spawned detached logging to
  `<run>/render.log` (it's already fingerprint-resumable); the workflow ends
  `status: "rendering (pid N)"`.

## Verified

- `npx tsc --noEmit` clean; `mastra build` bundles successfully.
- `node .mastra/output/index.mjs` serves `/api/workflows/episode` (all steps +
  suspend/resume schemas present).
- `POST /api/workflows/episode/start-async` executes `intake` end-to-end —
  `prepare_episode.py` runs and fails correctly on a missing story folder.
- Live `plan`-mode run on OpenRouter `deepseek/deepseek-v4.1-flash`
  (2026-09-16): intake → Stage A (all 5 artifacts + 8 image-prompt files,
  validators ok) → GATE 0 critique (valid report on attempt 3 —
  write→validate→fix loop corrected a narration preamble, then a summary
  count mismatch) → early return on `mode: "plan"`. Run: success.
- Resume waterfall verified: re-running the episode skips already-valid
  artifacts (`alreadyValid` in `src/mastra/lib/authoring.ts`), matching the
  runbook's "continue from the first missing artifact" rule.
- Fixes landed during live testing: `write_file` now permits the configured
  `OUTPUTS_ROOT` (run dirs live under the skill dir, not `REPO_ROOT/outputs`);
  `PYTHON_BIN` must point at the env with requirements installed (prompt
  validators import `httpx`/`fal_client`); OpenRouter needs the full
  `openrouter/<vendor>/<model>` id — a bare `deepseek/...` resolves to the
  DeepSeek API provider.
- Not yet exercised: GATE 1/2 suspend→resume, image spend, and the render
  handoff.

## Notable risks

- **Vision fidelity**: the video-prompter must actually describe the sheet
  pixels; a weak `VISION_MODEL` degrades the discrepancy-authority policy.
- **Two state systems**: workflow snapshots vs. `render_state.json` — kept
  separate by design (snapshot = position, filesystem = data) but worth
  remembering when debugging resumes.
- **GATE 1 rejection** currently holds the run rather than looping back to
  sheet regeneration — flagged in README-MASTRA.md known-limits.
