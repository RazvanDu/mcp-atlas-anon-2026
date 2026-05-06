"""Data loading utilities for MCP-Atlas figures.

Reads from the released ``runs/`` tree:
  runs/coverage_stats/<model>.json       canonical pass rates and coverage
  runs/diagnosis_v2/<model>.json         v2 diagnosis summaries
  runs/scored_public_subset/<model>.csv  per-task scoring + agent trajectories

Each per-model JSON has its display name in ``model_name``. Use
``load_coverage_stats()`` to get a pass-rate-sorted list of models with all
canonical metrics.
"""

import json
import os
from pathlib import Path

_BASE = Path(__file__).resolve().parent.parent
RUNS_DIR = _BASE / "runs"
COVERAGE_DIR = RUNS_DIR / "coverage_stats"
DIAGNOSIS_DIR = RUNS_DIR / "diagnosis_v2"
SCORED_DIR = RUNS_DIR / "scored_public_subset"

# Provider mapping derives entirely from display name.
_PROVIDER_PREFIX = {
    "Claude": "Anthropic",
    "Gemini": "Google",
    "GPT-": "OpenAI",
    "o3":    "OpenAI",
    "Muse":  "Meta",
}


def get_provider(display_name):
    """Return provider family from a model's display name."""
    for prefix, provider in _PROVIDER_PREFIX.items():
        if display_name.startswith(prefix):
            return provider
    return "Open-source"


def load_coverage_stats(split="all"):
    """Load coverage stats for all models for a given split.

    Args:
        split: 'all', 'public', or 'private'.

    Returns:
        List of dicts sorted by pass_rate_0.75 (descending), each with at
        minimum: ``label``, ``provider``, ``mean_coverage``, ``pass_rate_0.50``,
        ``pass_rate_0.75``, plus any extra fields from the source JSON.
    """
    if not COVERAGE_DIR.is_dir():
        raise FileNotFoundError(f"Expected coverage stats at {COVERAGE_DIR}")

    results = []
    for fpath in sorted(COVERAGE_DIR.iterdir()):
        if not fpath.suffix == ".json":
            continue
        with open(fpath) as f:
            data = json.load(f)
        if split in data:
            stats = data[split]
        else:
            stats = data.get("all", data)
        label = stats.get("model_name") or fpath.stem
        results.append({
            "label": label,
            "provider": get_provider(label),
            **stats,
        })
    results.sort(key=lambda x: x.get("pass_rate_0.75", 0), reverse=True)
    return results


def load_diagnosis_summaries():
    """Load v2 diagnosis summaries for all models.

    Returns:
        List of dicts sorted by pass rate, each with ``label``, ``provider``,
        and a nested ``diagnosis`` dict containing ``primary_failure_distribution``
        and ``category_split``.
    """
    if not DIAGNOSIS_DIR.is_dir():
        raise FileNotFoundError(f"Expected v2 diagnoses at {DIAGNOSIS_DIR}")

    results = []
    for fpath in sorted(DIAGNOSIS_DIR.iterdir()):
        if not fpath.suffix == ".json":
            continue
        with open(fpath) as f:
            data = json.load(f)
        label = data.get("model_name") or fpath.stem
        results.append({
            "label": label,
            "provider": get_provider(label),
            "diagnosis": data,
        })
    results.sort(
        key=lambda x: x["diagnosis"].get("scoring", {}).get("pass_rate_0.75", 0),
        reverse=True,
    )
    return results
