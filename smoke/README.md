# MCP-Atlas Smoke Test

Offline reproducibility check. No network, no API keys, no vendor calls.
Runs in under 30 seconds.

## Usage

From the release root:

```bash
pip install -r requirements.txt   # only pandas/numpy needed for this test
python smoke/smoke_test.py
```

## What it validates

1. **Public split is intact.** `data/public_split.csv` parses cleanly and
   contains 500 rows.
2. **Per-task scores reproduce the leaderboard.** For each of the 20
   models, recompute `pass@0.75` from the per-task `coverage_score` values
   in `runs/scored_public_subset/<model>.csv` and compare against the
   canonical pass rate stored in `runs/coverage_stats/<model>.json` under
   the `public` split. Tolerance is 0.15 percentage points.
3. **Diagnosis category counts are consistent.** For each
   `runs/diagnosis_v2/<model>.json`, the `primary_failure_distribution`
   counts sum to `tasks_diagnosed` (±1 for legacy format).

## Expected output

```
MCP-Atlas offline smoke test
============================================================
[OK] Public split has 500 tasks

[OK] claude_haiku_4_5    canonical=41.2%  recomputed=41.2%  diff=0.00pp
...
[OK] All 20 models reproduce pass rate within 0.15 pp

[OK] All v2 diagnoses sum correctly

ALL TESTS PASSED.
```

If any check fails, the script raises `AssertionError` with the offending
model and the discrepancy. Exit code is non-zero.

## What it does NOT validate

- The agent trajectories themselves (this is offline; live re-evaluation
  requires level 3 — see `docs/REPRODUCIBILITY.md`).
- Judge consistency (re-scoring requires an LLM endpoint — see level 2 in
  `docs/REPRODUCIBILITY.md`).
- Figure regeneration (see `figures/regenerate_all.sh`).
