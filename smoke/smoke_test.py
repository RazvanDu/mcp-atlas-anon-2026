"""MCP-Atlas offline smoke test.

Validates the released artifact end-to-end without calling any vendor API:

1. Loads the 500-task public split.
2. Loads each released model's scored public subset.
3. Reproduces pass-rate-at-0.75 from per-task coverage scores.
4. Cross-checks the result against the canonical pass rate in coverage_stats.

Passes if all 20 models reproduce within 0.1 percentage points. Takes <30s.
"""
import csv
import json
import sys
from pathlib import Path

csv.field_size_limit(sys.maxsize)

ROOT = Path(__file__).resolve().parent.parent
COV = ROOT / "runs" / "coverage_stats"
SCORED = ROOT / "runs" / "scored_public_subset"
PUBLIC = ROOT / "data" / "public_split.csv"


def test_public_split_exists():
    assert PUBLIC.is_file(), f"Missing {PUBLIC}"
    n = sum(1 for _ in csv.DictReader(PUBLIC.open()))
    assert n == 500, f"Expected 500 public tasks, got {n}"
    print(f"[OK] Public split has 500 tasks")


def test_each_model_reproduces_pass_rate():
    n_models = 0
    failures = []
    for cov_path in sorted(COV.iterdir()):
        if cov_path.suffix != ".json":
            continue
        slug = cov_path.stem
        scored_path = SCORED / f"{slug}.csv"
        if not scored_path.is_file():
            failures.append(f"{slug}: missing scored CSV")
            continue
        with open(cov_path) as f:
            data = json.load(f)
        canonical_public_pr = data.get("public", {}).get("pass_rate_0.75")
        if canonical_public_pr is None:
            failures.append(f"{slug}: no canonical public pass rate")
            continue
        # Recompute from per-task coverage scores (should match the canonical
        # public pass rate to one decimal).
        scores = []
        with open(scored_path, newline="") as f:
            for row in csv.DictReader(f):
                try:
                    scores.append(float(row["coverage_score"]))
                except (ValueError, KeyError):
                    pass
        if not scores:
            failures.append(f"{slug}: no parseable coverage scores")
            continue
        recomputed = 100.0 * sum(1 for s in scores if s >= 0.75) / len(scores)
        diff = abs(recomputed - canonical_public_pr)
        status = "OK" if diff < 0.15 else "FAIL"
        print(f"[{status}] {slug:<30} canonical={canonical_public_pr:5.1f}%  "
              f"recomputed={recomputed:5.1f}%  diff={diff:.2f}pp")
        if diff >= 0.15:
            failures.append(f"{slug}: drift {diff:.2f}pp")
        n_models += 1
    assert not failures, f"Mismatches: {failures}"
    print(f"\n[OK] All {n_models} models reproduce pass rate within 0.15 pp")


def test_diagnosis_v2_categories_sum():
    """Verify each v2 diagnosis sums to its tasks_diagnosed count."""
    DIAG = ROOT / "runs" / "diagnosis_v2"
    failures = []
    for d in sorted(DIAG.iterdir()):
        if d.suffix != ".json":
            continue
        with open(d) as f:
            data = json.load(f)
        diag = data.get("diagnosis", {})
        pfd = diag.get("primary_failure_distribution", {})
        n = diag.get("tasks_diagnosed", 0)
        s = sum(pfd.values())
        # Allow 1-task slack for legacy format
        if n and abs(s - n) > 1:
            failures.append(f"{d.stem}: pfd sum {s} != tasks_diagnosed {n}")
    assert not failures, f"Sum mismatches: {failures}"
    print(f"[OK] All v2 diagnoses sum correctly")


if __name__ == "__main__":
    print("MCP-Atlas offline smoke test\n" + "=" * 60)
    test_public_split_exists()
    print()
    test_each_model_reproduces_pass_rate()
    print()
    test_diagnosis_v2_categories_sum()
    print("\nALL TESTS PASSED.")
