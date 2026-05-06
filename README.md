# MCP-Atlas — Code Companion (Anonymous Release)

This repository accompanies the NeurIPS 2026 Evaluations & Datasets Track
submission *MCP-Atlas: A Large-Scale Benchmark for Tool-Use Competency
with Real MCP Servers*. It contains the evaluation harness, claims
evaluator, failure-mode diagnostic pipeline, figure-regeneration code,
and an offline smoke test.

The dataset itself (the 500-task public split) is hosted separately —
see the dataset URL in the paper supplementary. A small 10-row sample is
included in `data_sample/` so the smoke test runs without an external
download.

## Contents

```
.
├── data_sample/
│   ├── public_split_sample_10.csv   First 10 public-split tasks
│   └── claims_schema.json           Claims-list format spec
├── harness/
│   ├── score_claims.py              Live claim evaluator (Gemini-3.1-Pro by default)
│   ├── single_model_diagnostic_v2.py  v2 failure-mode diagnostic pipeline
│   ├── mcp_failure_taxonomy.py      Authoritative 11-mode taxonomy
│   └── README.md
├── figures/
│   ├── data_loader.py               Loads runs/ tree (see paper supplementary)
│   ├── plot_style.py
│   ├── generate_plot.py             Leaderboard performance figure
│   ├── analyses/
│   │   ├── a3_public_private_gap.py  Public-private split gap figure
│   │   └── a5_efficiency_pareto.py   Efficiency Pareto frontier figure
│   └── regenerate_all.sh
├── smoke/
│   ├── smoke_test.py                Offline reproducibility check (no LLM calls)
│   └── README.md
├── docs/
│   ├── DATA_SCHEMA.md               Per-column schema documentation
│   ├── DATASHEET.md                 Gebru-style datasheet
│   ├── EVAL_PROTOCOL.md             Verbatim evaluator prompt + run config
│   └── REPRODUCIBILITY.md           Three reproducibility levels
├── requirements.txt
├── LICENSE                          Apache-2.0 (code)
└── THIRD-PARTY-LICENSES.md          MCP server upstream licenses
```

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Smoke test (no credentials, no network)

```bash
python smoke/smoke_test.py
```

Runs four offline checks: sample CSV parses with the expected schema,
claims schema is valid JSON-Schema with the 0.75 pass threshold, the
failure taxonomy module exposes the 11 modes (4 tool-call + 7
cognitive), and every harness script compiles. If a full `runs/` tree
is also present as a sibling, an additional optional check verifies
each model's per-task coverage scores reproduce the canonical pass
rate within 0.15 pp. Exits in <5s offline.

## Re-score against the claims evaluator (needs an LLM endpoint)

The evaluator script targets any OpenAI-compatible endpoint. Set:

```bash
export LITELLM_API_KEY=<your_key>
export LITELLM_BASE_URL=<https://your-openai-compatible-endpoint>
```

Then:

```bash
python harness/score_claims.py \
    --groundtruth-file=data_sample/public_split_sample_10.csv \
    --model-file=<your scored CSV with prompts and responses> \
    --evaluator-model=gemini/gemini-3.1-pro-preview
```

## Re-run failure diagnosis

```bash
python harness/single_model_diagnostic_v2.py \
    --scored-file=<your scored CSV> \
    --output-dir=./out/diag/ \
    --concurrency=15
```

This produces a `diagnosis_summary_*.json` matching the schema released
with the paper. The taxonomy is fixed at 11 modes (4 tool-call + 7
cognitive); see `harness/mcp_failure_taxonomy.py` for definitions.

## Regenerate paper figures

```bash
bash figures/regenerate_all.sh
```

Requires the released `runs/` tree (in the paper's supplementary, not
shipped here to keep this repo small). The data_loader expects
`runs/coverage_stats/`, `runs/diagnosis_v2/`, and
`runs/scored_public_subset/` siblings of the figures directory.

## License

Code: Apache-2.0 (see `LICENSE`)
Third-party MCP server licenses: see `THIRD-PARTY-LICENSES.md`

## Anonymity

This repository is anonymized for the NeurIPS 2026 double-blind review
process. Author identity, institutional affiliation, and any internal
infrastructure references have been removed. Live re-evaluation
requires the user to provide their own OpenAI-compatible LLM endpoint
and credentials; we do not ship internal endpoints.
