"""MCP-Atlas offline smoke test.

Validates that the released code companion is internally consistent and
ready to run, without any vendor API or network access.

Checks:
  1. Sample public-split data parses and has the expected schema.
  2. Claims schema is valid JSON Schema with the expected fields.
  3. Failure taxonomy module imports and exposes 11 modes (4 tool-call + 7 cognitive).
  4. Harness scripts compile (no syntax errors).

If you also have the full `runs/` tree from the paper supplementary
checked out as a sibling of `harness/`, this test additionally verifies
that every model's per-task coverage scores reproduce the canonical
pass rate within 0.15 percentage points.

Runtime: <5 seconds offline, ~30 seconds with the full runs/ tree.
"""
import ast
import csv
import json
import sys
from pathlib import Path

csv.field_size_limit(sys.maxsize)

ROOT = Path(__file__).resolve().parent.parent
SAMPLE_CSV = ROOT / "data_sample" / "public_split_sample_10.csv"
CLAIMS_SCHEMA = ROOT / "data_sample" / "claims_schema.json"
TAXONOMY = ROOT / "harness" / "mcp_failure_taxonomy.py"
HARNESS_DIR = ROOT / "harness"

# Optional full-tree paths (present only if the user has the supplementary)
FULL_DATA = ROOT / "data" / "public_split.csv"
COV = ROOT / "runs" / "coverage_stats"
SCORED = ROOT / "runs" / "scored_public_subset"


# ---------------------------------------------------------------------------
# Always-on checks
# ---------------------------------------------------------------------------

def test_sample_data_parses():
    assert SAMPLE_CSV.is_file(), f"Missing {SAMPLE_CSV}"
    expected_cols = {"TASK", "PROMPT", "ENABLED_TOOLS", "GTFA_CLAIMS",
                     "TRAJECTORY"}
    with SAMPLE_CSV.open() as f:
        rdr = csv.DictReader(f)
        cols = set(rdr.fieldnames or [])
        rows = list(rdr)
    missing = expected_cols - cols
    assert not missing, f"Sample CSV missing columns: {missing}"
    assert len(rows) == 10, f"Expected 10 rows in sample, got {len(rows)}"
    # Each row should have non-empty key fields and a parseable claims list
    for i, row in enumerate(rows):
        assert row["TASK"], f"row {i}: empty TASK"
        assert row["PROMPT"], f"row {i}: empty PROMPT"
        try:
            claims = ast.literal_eval(row["GTFA_CLAIMS"])
        except Exception as e:
            raise AssertionError(f"row {i}: GTFA_CLAIMS not parseable: {e}")
        assert isinstance(claims, list) and len(claims) > 0, \
            f"row {i}: claims list empty or wrong type"
    print(f"[OK] Sample CSV: {len(rows)} rows, {len(cols)} columns, "
          f"all required fields present and well-formed")


def test_claims_schema_valid():
    assert CLAIMS_SCHEMA.is_file(), f"Missing {CLAIMS_SCHEMA}"
    with CLAIMS_SCHEMA.open() as f:
        schema = json.load(f)
    assert schema.get("type") == "array", "claims_schema.json: type must be 'array'"
    assert "items" in schema, "claims_schema.json: missing 'items'"
    assert schema.get("_scoring", {}).get("task_pass_threshold") == 0.75, \
        "claims_schema.json: task_pass_threshold must be 0.75"
    print(f"[OK] Claims schema is valid JSON-Schema with the expected scoring rubric")


def test_taxonomy_has_11_modes():
    assert TAXONOMY.is_file(), f"Missing {TAXONOMY}"
    sys.path.insert(0, str(HARNESS_DIR))
    try:
        import mcp_failure_taxonomy as tax
    finally:
        sys.path.pop(0)
    expected_tool = {"malformed_call", "wrong_tool", "no_tool_use", "err_recovery"}
    expected_cog = {"task_misunderstanding", "faulty_synthesis",
                    "response_misparsing", "early_termination",
                    "hallucinated_fact", "logical_error", "constraint_violation"}
    actual_tool = set(tax.TOOL_CALL_MODES.keys())
    actual_cog = set(tax.COGNITIVE_MODES.keys())
    assert actual_tool == expected_tool, \
        f"TOOL_CALL_MODES mismatch: extra={actual_tool - expected_tool}, missing={expected_tool - actual_tool}"
    assert actual_cog == expected_cog, \
        f"COGNITIVE_MODES mismatch: extra={actual_cog - expected_cog}, missing={expected_cog - actual_cog}"
    assert len(tax.ALL_MODES) == 11, f"Expected 11 modes, got {len(tax.ALL_MODES)}"
    print(f"[OK] Failure taxonomy: {len(tax.ALL_MODES)} modes "
          f"({len(actual_tool)} tool-call + {len(actual_cog)} cognitive)")


def test_harness_scripts_compile():
    """Python-compile every script in harness/ to catch syntax errors."""
    import py_compile
    failures = []
    for f in sorted(HARNESS_DIR.glob("*.py")):
        try:
            py_compile.compile(str(f), doraise=True)
        except py_compile.PyCompileError as e:
            failures.append(f"{f.name}: {e}")
    assert not failures, f"Harness compile errors: {failures}"
    n = len(list(HARNESS_DIR.glob("*.py")))
    print(f"[OK] All {n} harness scripts compile without syntax errors")


# ---------------------------------------------------------------------------
# Optional checks (run only if the full runs/ tree is present)
# ---------------------------------------------------------------------------

def test_full_runs_pass_rate_reproduction():
    if not (FULL_DATA.is_file() and COV.is_dir() and SCORED.is_dir()):
        print("[SKIP] Full runs/ tree not present "
              "(only required for full-supplementary verification)")
        return
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
        if diff >= 0.15:
            failures.append(f"{slug}: drift {diff:.2f}pp")
        n_models += 1
    assert not failures, f"Mismatches: {failures}"
    print(f"[OK] All {n_models} models reproduce pass rate within 0.15 pp")


if __name__ == "__main__":
    print("MCP-Atlas offline smoke test")
    print("=" * 60)
    test_sample_data_parses()
    test_claims_schema_valid()
    test_taxonomy_has_11_modes()
    test_harness_scripts_compile()
    print()
    test_full_runs_pass_rate_reproduction()
    print("\nALL TESTS PASSED.")
