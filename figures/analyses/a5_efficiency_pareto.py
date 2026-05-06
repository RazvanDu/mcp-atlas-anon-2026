#!/usr/bin/env python3
"""
Analysis 5: Efficiency Pareto Frontier

Plots mean wall-clock time per task against pass rate for all models,
highlighting the Pareto frontier and identifying dominated configurations.

Produces:
  - fig_efficiency_pareto.pdf  (time vs pass rate scatter with Pareto frontier)
"""

import csv
import json
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

csv.field_size_limit(sys.maxsize)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from data_loader import (
    load_coverage_stats, get_provider, COVERAGE_DIR, SCORED_DIR,
)
from plot_style import apply_style, clean_axes, save_pdf, PROVIDER_COLORS


def _scored_csv_for(slug):
    """Return path to the per-model scored CSV, or None if missing."""
    p = SCORED_DIR / f"{slug}.csv"
    return p if p.is_file() else None


def _mean_trajectory_time(csv_path):
    """Mean of per-task `trajectory_time` (seconds), excluding non-positive entries."""
    times = []
    with open(csv_path, newline="") as fh:
        for row in csv.DictReader(fh):
            try:
                t = float(row.get("trajectory_time", ""))
                if t > 0:
                    times.append(t)
            except (ValueError, TypeError):
                pass
    return float(np.mean(times)) if times else None


def collect():
    """Return list of dicts: slug, label, provider, pass_rate, mean_time, n_tasks."""
    rows = []
    for fpath in sorted(COVERAGE_DIR.iterdir()):
        if fpath.suffix != ".json":
            continue
        slug = fpath.stem
        scored = _scored_csv_for(slug)
        if scored is None:
            print(f"  [skip] {slug}: no scored CSV")
            continue
        mean_t = _mean_trajectory_time(scored)
        if mean_t is None:
            print(f"  [skip] {slug}: no valid trajectory_time")
            continue
        with open(fpath) as f:
            d = json.load(f)
        # Use the `all` (1000-task) pass rate so the Pareto plot matches the
        # leaderboard figure. Falls back to `public` if `all` is missing.
        stats = d.get("all") or d.get("public") or d
        label = stats.get("model_name") or slug
        rows.append({
            "slug": slug,
            "label": label,
            "provider": get_provider(label),
            "pass_rate": stats.get("pass_rate_0.75", 0),
            "mean_time": mean_t,
        })
        print(f"  {slug}: mean_time={mean_t:.1f}s pass_rate={stats.get('pass_rate_0.75',0):.1f}%")
    return rows


def pareto_frontier(rows):
    """Lower time better, higher pass_rate better."""
    sorted_rows = sorted(rows, key=lambda r: r["mean_time"])
    frontier, best_pr = [], -1
    for r in sorted_rows:
        if r["pass_rate"] > best_pr:
            frontier.append(r)
            best_pr = r["pass_rate"]
    return frontier


# Hand-tuned label offsets keyed by display name.
LABEL_OFFSETS = {
    "Muse Spark":                     (-10,  8, "right"),
    "Claude Opus 4.7":                (-10,  2, "right"),
    "Gemini 3.1 Pro Preview":         ( 10,  0, "left"),
    "Claude Opus 4.6":                ( 10,  0, "left"),
    "GPT-5.5":                        ( 10, -6, "left"),
    "GLM-5.1":                        ( 10,  2, "left"),
    "Gemini 3 Pro Preview":           (-10, 10, "right"),
    "Claude Opus 4.5":                (-10,-10, "right"),
    "Claude Sonnet 4.6":              ( 10, -3, "left"),
    "GPT-5.4":                        ( 10,  3, "left"),
    "GPT-5.2":                        ( 10,  0, "left"),
    "Kimi K2.5":                      ( 10,  0, "left"),
    "Gemini 3 Flash Preview":         (-10,  5, "right"),
    "Claude Sonnet 4.5":              ( 10, -3, "left"),
    "GLM-4.7":                        (-10,  0, "right"),
    "Gemini 3.1 Flash Lite Preview":  (-10,-10, "right"),
    "GPT-5.4 Mini":                   ( 10,  0, "left"),
    "GPT-5.1":                        ( 10, -3, "left"),
    "o3 Pro":                         (-10,  0, "right"),
    "Claude Haiku 4.5":               ( 10,  0, "left"),
}


def plot(rows):
    apply_style()
    fig, ax = plt.subplots(figsize=(11, 6.5))
    fig.patch.set_facecolor("white")

    frontier = pareto_frontier(rows)
    frontier_slugs = {r["slug"] for r in frontier}
    fx = [r["mean_time"] for r in frontier]
    fy = [r["pass_rate"] for r in frontier]
    ax.plot(fx, fy, "-", color="#2e8b57", linewidth=1.2, zorder=1, alpha=0.5)

    for r in rows:
        c = PROVIDER_COLORS.get(r["provider"], "#888888")
        on_frontier = r["slug"] in frontier_slugs
        ax.scatter(r["mean_time"], r["pass_rate"],
                   s=110 if on_frontier else 80, c=c,
                   edgecolor="#2e8b57" if on_frontier else "white",
                   linewidth=1.5 if on_frontier else 0.6, zorder=5)

    for r in rows:
        ox, oy, ha = LABEL_OFFSETS.get(r["label"], (10, 0, "left"))
        weight = "bold" if r["slug"] in frontier_slugs else "normal"
        color = "#222222" if r["slug"] in frontier_slugs else "#444444"
        ax.annotate(r["label"], (r["mean_time"], r["pass_rate"]),
                    fontsize=9.5, fontweight=weight,
                    xytext=(ox, oy), textcoords="offset points",
                    ha=ha, va="center", color=color)

    ax.set_xlabel("Mean Trajectory Time per Task (seconds)", fontsize=14, labelpad=8)
    ax.set_ylabel(r"Pass Rate at Coverage $\geq$ 0.75 (%)", fontsize=14, labelpad=8)
    ax.tick_params(axis="both", labelsize=12)
    ax.set_xlim(0, max(r["mean_time"] for r in rows) * 1.1 if rows else 215)
    ax.set_ylim(36, 86)
    clean_axes(ax)
    ax.grid(axis="both", alpha=0.2, linestyle="-", linewidth=0.5, color="#cccccc")

    handles = [Patch(facecolor=PROVIDER_COLORS["Anthropic"], label="Anthropic"),
               Patch(facecolor=PROVIDER_COLORS["Google"],    label="Google"),
               Patch(facecolor=PROVIDER_COLORS["OpenAI"],    label="OpenAI"),
               Patch(facecolor=PROVIDER_COLORS["Meta"],      label="Meta"),
               Patch(facecolor=PROVIDER_COLORS["Other"],     label="Open-source"),
               Line2D([0], [0], color="#2e8b57", linewidth=1.5, label="Pareto frontier")]
    leg = ax.legend(handles=handles, loc="lower left",
                    bbox_to_anchor=(0.68, 0.03), fontsize=10, frameon=True,
                    edgecolor="#cccccc", fancybox=False,
                    handlelength=1.2, handletextpad=0.5, borderpad=0.5)
    leg.get_frame().set_linewidth(0.4)

    plt.tight_layout()
    save_pdf(fig, "fig_efficiency_pareto.pdf")


if __name__ == "__main__":
    print("Extracting trajectory times...")
    rows = collect()
    print(f"\nCollected {len(rows)} models")
    if rows:
        plot(rows)
