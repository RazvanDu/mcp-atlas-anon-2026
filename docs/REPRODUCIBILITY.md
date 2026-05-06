# MCP-Atlas Reproducibility Guide

Three levels of reproducibility, increasing in cost and infrastructure
requirements. Most reviewers will only need level 1.

## Level 1 — Smoke (no credentials, ~30s)

Recomputes pass-rate-at-0.75 for all 20 models from per-task coverage
scores in `runs/scored_public_subset/` and confirms each matches the
canonical value in `runs/coverage_stats/`.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python smoke/smoke_test.py
```

Expected output: 20 lines `[OK] <model> canonical=X.X% recomputed=X.X%
diff=0.00pp`, then `ALL TESTS PASSED.` Total runtime under 30 seconds. No
network calls, no API keys required.

This level validates that:
- the per-task scores in the released CSVs reproduce the leaderboard
  numbers exactly, and
- every diagnosed task in `runs/diagnosis_v2/` is in the public split.

## Level 2 — Re-score (one LLM endpoint)

Runs the claim evaluator (`harness/score_claims.py`) over an existing
scored CSV to confirm that the per-claim coverage outcomes are stable
under judge re-execution. Useful for verifying the scoring methodology.

### Prerequisites

An OpenAI-compatible LLM endpoint serving the judge model. The default
judge is `gemini/gemini-3.1-pro-preview`; any model with
JSON-schema-mode support works.

```bash
export LITELLM_BASE_URL="<your endpoint, e.g. https://your-proxy/v1>"
export LITELLM_API_KEY="<your key(s), comma-separated for rotation>"
```

### Run

```bash
python harness/score_claims.py \
  --groundtruth-file=data/public_split.csv \
  --model-file=runs/scored_public_subset/claude_opus_4_7.csv \
  --num-tasks=50
```

Tunables: `--evaluator-model`, `--num-tasks`, `--concurrency`,
`--api-key`, `--base-url`. Output is a re-scored CSV alongside the input;
compare `coverage_score` against the released file.

### Expected variance

Per-claim verdicts are stable in aggregate (judge ceiling estimated at
2–5 percentage points of pass-rate variance under temperature-0
re-execution). Individual claims may flip between `partially_fulfilled`
and `fulfilled`/`not_fulfilled` on borderline cases.

### Approximate cost

Roughly 1 judge call per claim. With ~4.7 claims/task on average, scoring
500 tasks is ~2,350 calls. At Gemini 3.1 Pro pricing, expect ~$15–25 for
the full public split.

## Level 3 — Re-evaluate (full agent-trajectory generation)

Generates new agent trajectories for one or more models against the live
MCP servers, then scores them. This reproduces the leaderboard from
scratch.

This level requires infrastructure that **is not bundled** with this
release:

1. **An agent-loop driver.** This release includes the scoring harness
   and diagnostic pipeline but does not ship the trajectory-generation
   driver or the agent server. You will need to run an OpenAI-tools-style
   agent loop yourself; the per-task fields you must supply to your loop
   are: `PROMPT` (user message), `ENABLED_TOOLS` (allowed tool names),
   plus the MCP servers themselves.

2. **The 36 upstream MCP servers**, each installed from its upstream
   source. See `THIRD-PARTY-LICENSES.md` for the inventory. Some require
   API keys (e.g. `brave-search`, `oxylabs`, `twelvedata`,
   `lara-translate`, `notion`, `slack`, `github`, `airtable`,
   `google-maps`, `google-workspace`); others are self-hosted
   (e.g. `filesystem`, `memory`, `mongodb`, `cli-mcp-server`,
   `e2b-server`).

3. **A sandboxed execution environment.** The leaderboard runs were
   performed inside a containerized environment with allow-listed network
   egress; we strongly recommend the same.

### Run config used for the leaderboard

| Setting | Value |
|---|---|
| `max_tool_calls` | 100 |
| `max_turns` | 256 |
| pass threshold | `coverage_score ≥ 0.75` |
| primary judge | `gemini/gemini-3.1-pro-preview` |
| agent system prompt | none (verbatim PROMPT as the only user message) |

Per-model strategy and decoding parameters are recorded in each
`runs/coverage_stats/<model>.json` under `run_config`.

### Approximate cost and runtime

Per-task latency varies by model (mean trajectory time ranges ~30–200
seconds; see `figures/analyses/a5_efficiency_pareto.py`). For a full
500-task public-split run with a frontier model, budget several hours
of wall-clock time and $50–200 in inference cost depending on the model.

### Replication tolerance

Network-dependent tools (web search, API calls) introduce non-determinism
that cannot be eliminated. Expect pass-rate drift of up to 2–3 percentage
points between independent re-evaluations even at temperature 0.

---

## Validating a fresh re-evaluation

After level 3 you can re-run levels 1 and 2 against your new CSVs:

```bash
# Re-score your fresh trajectories
python harness/score_claims.py \
  --groundtruth-file=data/public_split.csv \
  --model-file=<your fresh scored CSV>

# Diagnose failure modes (v2 taxonomy)
python harness/single_model_diagnostic_v2.py \
  --scored-file=<your fresh scored CSV>
```

The diagnostic pipeline reads the `agent_trajectory` column directly; it
is self-contained against any scored CSV that follows the schema in
`docs/DATA_SCHEMA.md`.
