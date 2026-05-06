# MCP-Atlas Data Schema

Column-by-column reference for every CSV and JSON shipped in this release.
The Croissant manifest at `data/croissant.jsonld` gives a one-line
description per field; this document specifies the structure of nested
JSON values inside string-typed columns.

## Files

| Path | Rows | Description |
|---|---|---|
| `data/public_split.csv` | 500 | Tasks, claims, reference trajectories |
| `runs/scored_public_subset/<model>.csv` | 500 | Per-task model output + scoring (one CSV per model, 20 total) |
| `runs/coverage_stats/<model>.json` | — | Aggregate pass-rate stats (one JSON per model) |
| `runs/diagnosis_v2/<model>.json` | — | v2 failure-mode diagnosis (one JSON per model) |
| `data/claims_schema.json` | — | JSON Schema for `GTFA_CLAIMS` |

---

## `data/public_split.csv` — task definitions (500 rows)

| Column | Type | Description |
|---|---|---|
| `TASK` | string | 24-char hex task identifier (unique key). |
| `PROMPT` | string | Natural-language single-turn user request. |
| `ENABLED_TOOLS` | JSON list[string] | Tool names available to the agent for this task. Format: `<server>_<tool>`. 6–37 entries per task. |
| `TRAJECTORY` | JSON list[step] | Reference solution trajectory (see schema below). |
| `GTFA` | string | Reference final-answer prose. |
| `GTFA_CLAIMS` | Python list literal | Atomic factual claims (see `claims_schema.json`). |
| `SPLIT` | enum | Always `"public"` in this release. |
| `REQUIRED_TOOLS` | JSON list[string] | Tool names called in the reference solution. Subset of `ENABLED_TOOLS`. |
| `REQUIRED_SERVERS` | JSON list[string] | Server names referenced by `REQUIRED_TOOLS`. |

### `TRAJECTORY` element schema

A list of OpenAI-style chat-completion step dicts:

```json
{
  "role": "assistant" | "tool",
  "content": "<text or list of {text, type: 'text'} blocks>",
  "tool_calls": [                           // only on assistant steps that call tools
    {
      "id": "<uuid>",
      "type": "function",
      "function": {
        "name": "<server>_<tool>",
        "arguments": "<json-encoded arg object>"
      }
    }
  ],
  "tool_call_id": "<uuid>"                  // only on tool-role steps; matches the assistant's tool_call.id
}
```

---

## `runs/scored_public_subset/<model>.csv` — model output + scoring (500 rows)

Inherits all 9 columns from `public_split.csv` and adds:

| Column | Type | Description |
|---|---|---|
| `script_model_response` | string | Model's verbatim final-answer text. May be empty or start with `ERROR:` for failed runs. |
| `agent_trajectory` | JSON list[turn] | Enriched per-turn agent trace (see schema below). |
| `errors` | JSON list[error] | Run-level errors. Empty list `[]` means clean run. See "Error shapes" below. |
| `trajectory_time` | float | Wall-clock seconds for the agent loop. |
| `num_retry` | int | Number of retries the agent loop performed (network/API-level retries). |
| `num_turns` | int | Total number of assistant turns (1-indexed). |
| `coverage_score` | float in [0, 1] | Mean of per-claim scores. Task passes if ≥ 0.75. |
| `fully_covered_claims` | int | Count of claims scored 1.0. |
| `partially_covered_claims` | int | Count of claims scored 0.5. |
| `total_claims` | int | Total number of atomic claims for this task. |
| `coverage_details_json` | JSON object | Full per-claim scoring breakdown (see schema below). |
| `evaluation_confidence` | float in [0, 1] | Mean per-claim confidence reported by the judge. |

### `agent_trajectory` element schema

A list of one dict per assistant turn. Last turn additionally carries
`final_answer`.

```json
{
  "turn": 1,                                // 1-indexed
  "assistant_reasoning": "<text>" | null,   // model's chain-of-thought / planning text
  "tool_calls": [
    {
      "name": "<server>_<tool>",
      "parameters": <object>,               // tool args, parsed (not stringified)
      "status": "success" | "error",
      "error_message": "<text>" | null,
      "output_summary": "<text>"            // tool result, summarized/truncated
    }
  ],
  "parallel": false | true,                 // true if the agent issued multiple parallel tool calls in this turn
  "final_answer": "<text>"                  // present only on the terminal turn
}
```

### `errors` shapes

Two shapes appear in this release:

```json
// (a) Run hit the per-task tool-call budget
{"reason": "max_tool_calls_reached",
 "maxToolCalls": 100,
 "totalToolCalls": 100}

// (b) Underlying LLM API returned an error (e.g. context window exceeded)
{"message": "<error text>",
 "serverResponse": "<raw upstream response>"}
```

`max_tool_calls_reached` and `max_turns_reached` are run-level terminations:
the agent exhausted its budget without producing a final answer. Tasks with
non-empty `errors` typically score 0.

### `coverage_details_json` schema

```json
{
  "per_claim": [
    {
      "claim": "<atomic claim text>",
      "score": 0.0 | 0.5 | 1.0,
      "covered": false | "partial" | true,
      "reason": "<judge justification>"
    }
  ],
  "coverage_score": 0.0..1.0,
  "total_claims": <int>,
  "fully_covered_claims": <int>,
  "partially_covered_claims": <int>,
  "explanation": "<status text>",
  "confidence": 0.0..1.0
}
```

---

## `runs/coverage_stats/<model>.json` — aggregate stats

Top-level keys: `all`, `public`. (`private` is held back during review.)
Each split contains:

| Key | Type | Description |
|---|---|---|
| `model_name` | string | Public display name (e.g. `"Claude Opus 4.7"`). |
| `evaluator_model` | string | Judge model used for claim scoring. |
| `total_tasks` | int | Tasks evaluated in this split. |
| `valid_responses` | int | Tasks with a non-empty, non-error response. |
| `empty_or_error` | int | `total_tasks - valid_responses`. |
| `tasks_with_scraping_errors` | int | Tasks with a non-empty `errors` column. |
| `clean_runs` | int | Tasks with neither empty/error response nor scraping errors. |
| `mean_coverage` | float | Mean `coverage_score` over `valid_responses`. |
| `pass_rate_0.50` | float % | Fraction with `coverage_score ≥ 0.50`. |
| `pass_rate_0.75` | float % | **Headline metric.** Fraction with `coverage_score ≥ 0.75`. |
| `run_config` | object | Strategy + decoding params used for this run. |

---

## `runs/diagnosis_v2/<model>.json` — failure-mode diagnosis

| Key | Description |
|---|---|
| `model_name` | Public display name. |
| `timestamp` | ISO timestamp of the diagnosis run. |
| `diagnosis_threshold` | Coverage cutoff below which a task is treated as failed (`0.75`). |
| `diagnosis_version` | `"v2"`. |
| `scoring` | Mirror of the headline scoring numbers. |
| `run_health` | Counts of `max_tool_calls_reached`, `context_window`, etc. |
| `diagnosis.tasks_diagnosed` | Number of failing tasks fed through the v2 diagnosis. |
| `diagnosis.primary_failure_distribution` | `{<mode>: <count>}` — must sum to `tasks_diagnosed` (±1). |
| `diagnosis.examples` | `{<mode>: [{task_id, prompt_snippet, diagnosis_summary}, …]}`. All `task_id` values are guaranteed to be in the public split. |

Failure modes are defined in `harness/mcp_failure_taxonomy.py`. See that
file for the canonical list of categories and definitions.
