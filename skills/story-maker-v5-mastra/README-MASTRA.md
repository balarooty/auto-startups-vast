# story-maker-v5-mastra — standalone service

The story-maker-v5 pipeline as a **Mastra application**: the SKILL.md runbook
becomes a typed workflow, each "agent" in the roster becomes a real isolated
Mastra agent, and the human approval gates become code-enforced
`suspend()`/`resume()` points instead of runbook rules.

## What changed vs. the regular skill

| | story-maker-v5 (skill) | story-maker-v5-mastra (service) |
|---|---|---|
| Orchestration | Runbook the host agent follows | Typed Mastra workflow (`src/mastra/workflows/episode.ts`) |
| Agents 1–7 | One context roleplaying personas | Isolated agents (`src/mastra/agents/`), per-agent models |
| Gates 0/1/2 | "STOP and ask" instructions | `suspend()`/`resume()` — cannot be skipped |
| Write→validate→fix | Agent self-discipline | `authorArtifact` / `authorFileSet` loops (`src/mastra/lib/authoring.ts`) |
| Runs under | A Devin/Claude session | Standalone HTTP service, any caller |
| Vision step | Host agent opens sheet images | Vision-capable model gets image bytes in the prompt |
| Python hands | `tools/`, `scripts/` via Bash | Same files, invoked via child_process — **unchanged** |

The filesystem is still the source of truth: `outputs/` artifacts and
`render_state.json` carry resume data; Mastra snapshots (LibSQL,
`.mastra/mastra.db`) only track where a run sits in the workflow.

## Setup

```bash
cd skills/story-maker-v5-mastra
pip install -r requirements.txt          # python hands (same as v5)
npm install                              # node orchestrator
cp mastra.env.example .env               # LLM_* config
# set PYTHON_BIN to the env you pip-installed into — the prompt/image
# validators import httpx, fal_client, etc. which system python3 lacks.
# repo-root .env still needs FAL_KEY / REPLICATE_API_TOKEN / COMFYUI_URL(+AUTH)
```

## Run

```bash
npm run dev      # mastra dev — studio UI + API on :4111
# or
npm run build && npm start               # compiled .mastra/output server
```

### Start an episode run

```bash
curl -X POST http://localhost:4111/api/workflows/episode/start-async \
  -H 'Content-Type: application/json' \
  -d '{"inputData": {"series": "shiva", "episode": 6, "mode": "full"}}'
# → {"runId": "...", "status": "running"|"suspended", ...}
```

Inputs: `series`+`episode`, or `storyFile`; optional `targetSeconds`;
`mode`: `plan` (Stage A + critique only, no image spend) | `sheets` (through
GATE 1) | `full` (default — through the detached render).

### Approve a gate

When a run suspends, `GET /api/workflows/episode/runs/:runId` shows the
suspended step and its payload (sheet paths, report, manifest). Resume:

```bash
curl -X POST http://localhost:4111/api/workflows/episode/resume \
  -H 'Content-Type: application/json' \
  -d '{"runId": "<runId>", "step": "gate-1-sheets",
       "resumeData": {"approved": true}}'
```

`approved: false` + `notes` re-suspends with your feedback attached — the gate
holds until explicitly approved. GATE 0 (`stage-a-critique`) resumes with
`{"proceed": true|false}` — it only suspends if the critique/fix loop cannot
converge on its own.

## Model config

- `LLM_PROVIDER` — `anthropic` (default), `openai`, `google`, …
- `LLM_MODEL` — default model for authoring agents
- `VISION_MODEL` — video-prompter + spatial-qa (they read sheet images)
- `CRITIQUE_MODEL` — critique-agent + plan-fixer
- `MODEL_<AGENT_ID>` — per-agent override, e.g. `MODEL_VIDEO_PROMPTER=openai/gpt-5`

## Layout

```
src/mastra/
├── index.ts                 # Mastra instance (agents + workflow + LibSQL storage)
├── config.ts                # env, skill-root discovery
├── provider.ts              # env-driven model factory
├── lib/
│   ├── python.ts            # validate.py / build_images / manifest / detached render
│   ├── authoring.ts         # write→validate→fix loops (single artifact + file sets)
│   ├── prompts.ts           # prompt/asset file loader
│   └── scenes.ts            # scene/generation parsing from artifacts
├── tools/files.ts           # read_file / write_file (repo-scoped)
├── agents/index.ts          # 10 agents mapped 1:1 from prompts/*.md
└── workflows/episode.ts     # the pipeline + gates
```

## Known limits (v1)

- Stage-D render is launched detached (hours-long); the workflow ends with
  `status: "rendering (pid N)"` — watch `<run>/render.log`, `qc.md`, and
  `render_state.json`. A follow-up automation can poll `episode_status.py`.
- GATE 1 rejection doesn't yet re-run sheet generation — the run holds at the
  gate; regenerate sheets manually then resume.
- `stories/` input layout is identical to v5 — see SKILL.md's intake section.
