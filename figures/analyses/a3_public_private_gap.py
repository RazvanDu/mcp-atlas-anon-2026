#!/usr/bin/env python3
"""
Analysis 3: Public vs. Private Split Gap as a Contamination Signal

Compares model performance on the public (released) vs private (held-out)
500-task splits. Large gaps may indicate data contamination or memorization.

Produces:
  - fig_public_private_gap.pdf  (dumbbell plot showing both splits + gap)

Note: the private split is held back during peer review; this script
exits gracefully when no `private` block is present in the per-model
coverage_stats JSONs and the figure cannot be regenerated until the
camera-ready release.
"""

import sys, os
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from data_loader import load_coverage_stats, COVERAGE_DIR
from plot_style import apply_style, clean_axes, save_pdf, PROVIDER_COLORS


def _has_private_split():
    """Return True iff at least one coverage_stats JSON has a `private` block."""
    import json
    for fpath in COVERAGE_DIR.iterdir():
        if fpath.suffix != ".json":
            continue
        with open(fpath) as f:
            d = json.load(f)
        if "private" in d:
            return True
    return False


def plot_gap():
    apply_style()

    pub = load_coverage_stats("public")
    prv = load_coverage_stats("private")

    pub_lookup = {r["label"]: r for r in pub}
    prv_lookup = {r["label"]: r for r in prv}

    all_stats = load_coverage_stats("all")
    rows = []
    for r in all_stats:
        lbl = r["label"]
        if lbl not in pub_lookup or lbl not in prv_lookup:
            continue
        pub_pr = pub_lookup[lbl].get("pass_rate_0.75", 0)
        prv_pr = prv_lookup[lbl].get("pass_rate_0.75", 0)
        rows.append({
            "label": lbl,
            "provider": r["provider"],
            "public": pub_pr,
            "private": prv_pr,
            "gap": pub_pr - prv_pr,
            "overall": r.get("pass_rate_0.75", 0),
        })
    rows.sort(key=lambda x: x["overall"], reverse=True)

    n = len(rows)
    y_pos = np.arange(n)
    labels = [r["label"] for r in rows]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    fig.patch.set_facecolor("white")

    for i, r in enumerate(rows):
        is_big_gap = r["gap"] > 6
        ax.plot([r["private"], r["public"]], [i, i],
                color="#cc3333" if is_big_gap else "#aaaaaa",
                linewidth=2.5 if is_big_gap else 1.5,
                zorder=2, solid_capstyle="round")

    prv_vals = [r["private"] for r in rows]
    pub_vals = [r["public"] for r in rows]
    ax.scatter(prv_vals, y_pos, s=90, c="#2e8b57", zorder=5,
               edgecolor="white", linewidth=0.6, label="Private (held-out)")
    ax.scatter(pub_vals, y_pos, s=90, c="#5b9bd5", zorder=5,
               edgecolor="white", linewidth=0.6, label="Public (released)")

    for i, r in enumerate(rows):
        x_pos = max(r["public"], r["private"]) + 0.5
        color = "#cc3333" if r["gap"] > 6 else "#333333"
        ax.text(x_pos, i, f"{r['gap']:+.1f}", va="center", ha="left",
                fontsize=12, fontweight="bold", color=color)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=13, fontweight="bold")
    ax.invert_yaxis()
    ax.set_xlabel("Pass Rate @ 0.75 (%)", fontsize=15, labelpad=8)
    ax.tick_params(axis="x", labelsize=13)
    ax.tick_params(axis="y", length=0, pad=6)
    clean_axes(ax)

    ax.legend(fontsize=12, loc="lower right", frameon=True,
              edgecolor="#cccccc", fancybox=False, markerscale=1.2,
              borderpad=0.5).get_frame().set_linewidth(0.4)

    plt.tight_layout()
    save_pdf(fig, "fig_public_private_gap.pdf")


if __name__ == "__main__":
    if not _has_private_split():
        print("Fig. 4 (public/private gap) requires the private split, which is")
        print("held back during peer review. The figure cannot be regenerated")
        print("from this release; it will be available at camera-ready.")
        sys.exit(0)
    plot_gap()
