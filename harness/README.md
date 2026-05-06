# MCP-Atlas Harness

Three scripts for working with the released runs.

| Script | Purpose |
|---|---|
| `score_claims.py` | Claim-by-claim coverage scoring against an LLM judge. |
| `single_model_diagnostic_v2.py` | v2 failure-mode diagnosis on a scored CSV. |
| `mcp_failure_taxonomy.py` | Authoritative list of failure-mode categories. Imported by the diagnostic. |

All three require an OpenAI-compatible LLM endpoint:

```bash
export LITELLM_BASE_URL="<your endpoint, e.g. https://your-proxy/v1>"
export LITELLM_API_KEY="<your key(s); comma-separated for round-robin>"
```

Both scripts accept `--api-key` and `--base-url` to override env vars.

## `score_claims.py` — re-score a model's outputs

Re-runs the claim evaluator over an existing scored CSV. Each task's
atomic claims are judged independently against the model's response, the
mean of per-claim scores becomes `coverage_score`, and a task passes at
`coverage_score >= 0.75`.

```bash
python score_claims.py \
  --groundtruth-file=../data/public_split.csv \
  --model-file=../runs/scored_public_subset/claude_opus_4_7.csv \
  --num-tasks=50
```

Key flags:
- `--evaluator-model` — judge model. Default `gemini/gemini-2.5-pro`. The
  paper leaderboard used `gemini/gemini-3.1-pro-preview`.
- `--num-tasks` — limit for quick checks.
- `--concurrency` — auto-set per evaluator family; override if needed.
- `--model-name` — override; otherwise inferred from the input filename.

The judge prompt is reproduced verbatim in `docs/EVAL_PROTOCOL.md`.

## `single_model_diagnostic_v2.py` — categorize failures

Reads a scored CSV, selects tasks with `coverage_score < 0.75`, and uses
an LLM to classify each one into a failure mode from
`mcp_failure_taxonomy.py`. Outputs a per-model JSON with the same shape
as `runs/diagnosis_v2/<model>.json`.

```bash
python single_model_diagnostic_v2.py \
  --scored-file=../runs/scored_public_subset/claude_opus_4_7.csv \
  --verbose
```

The diagnostic uses the `agent_trajectory` column directly (no
re-enrichment needed). Output is written next to the input CSV.

## `mcp_failure_taxonomy.py` — taxonomy module

Defines `TOOL_CALL_MODES` (4 categories) and `COGNITIVE_MODES` (7
categories). Each entry has a `description` and an `example`. The
diagnostic and any reporting tooling import from this module — do not
hardcode mode names elsewhere.

## Cost notes

Per claim: one judge call. Average task has ~4.7 claims, so scoring 500
public tasks is ~2,350 calls. Diagnosis is one call per failed task,
typically 50–250 calls per model.
