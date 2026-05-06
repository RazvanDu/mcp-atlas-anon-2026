#!/usr/bin/env python3
"""Generate the leaderboard performance figure (Fig. 1) from runs/coverage_stats/."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from data_loader import load_coverage_stats
from plot_style import apply_style, save_pdf, PROVIDER_COLORS

apply_style()
covs = load_coverage_stats("all")
labels = [c["label"] for c in covs]
prs = [c.get("pass_rate_0.75", 0) for c in covs]
ci = [c.get("ci_95", 2.5) for c in covs]
colors = [PROVIDER_COLORS.get(c["provider"], "#888") for c in covs]

fig, ax = plt.subplots(figsize=(11, 7.5))
y = np.arange(len(labels))
ax.barh(y, prs, xerr=ci, color=colors, edgecolor="white", linewidth=0.5)
ax.set_yticks(y)
ax.set_yticklabels(labels)
ax.invert_yaxis()
ax.set_xlabel(r"Pass Rate at Coverage $\geq$ 0.75 (%)")
ax.set_xlim(0, 90)
ax.grid(axis="x", alpha=0.2)
for i, (pr, c) in enumerate(zip(prs, ci)):
    ax.text(pr + c + 1, i, f"{pr:.1f}", va="center", fontweight="bold", fontsize=10)

plt.tight_layout()
save_pdf(fig, "fig_leaderboard_performance.pdf")
print("Saved fig_leaderboard_performance.pdf")
