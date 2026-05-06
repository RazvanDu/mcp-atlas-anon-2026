"""Shared matplotlib styling for MCP Atlas paper figures."""

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# Font sizes calibrated for single-panel figures at figsize ~(9-10, 7-9).
# For dual-panel, pass fs_dual to functions.
FS = {"val": 22, "label": 21, "xlabel": 22, "tick": 22, "leg": 18, "legtitle": 20}
FS_DUAL = {"val": 18, "label": 17, "xlabel": 18, "tick": 19, "leg": 16, "legtitle": 17}

# Provider colors (for provider-based plots)
PROVIDER_COLORS = {
    "Anthropic": "#D97706",
    "Google": "#2563EB",
    "OpenAI": "#059669",
    "Meta": "#E11D48",
    "Other": "#7C3AED",
}

# Pass rate tier colors (matching original MCP Atlas paper)
PASS_TIERS = [
    (70, "\u226570%", "#2e8b57"),
    (60, "60\u201370%", "#5cb85c"),
    (50, "50\u201360%", "#8fd19e"),
    (40, "40\u201350%", "#d4897a"),
    (0,  "<40%",        "#c0564e"),
]

COVERAGE_BLUE = "#5b9bd5"


def apply_style():
    """Set global matplotlib style for paper figures."""
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "DejaVu Serif"],
        "mathtext.fontset": "dejavuserif",
    })


def clean_axes(ax):
    """Remove top/right spines, lighten remaining ones, add subtle grid."""
    ax.grid(axis="x", alpha=0.25, linestyle="-", linewidth=0.5,
            color="#cccccc", zorder=0)
    ax.set_axisbelow(True)
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)
    for sp in ["left", "bottom"]:
        ax.spines[sp].set_linewidth(0.5)
        ax.spines[sp].set_color("#bbbbbb")


def save_pdf(fig, path):
    """Save figure as PDF with consistent settings."""
    from matplotlib.backends.backend_pdf import PdfPages
    with PdfPages(path) as pdf:
        pdf.savefig(fig, facecolor="white", bbox_inches="tight", pad_inches=0.15)
    print(f"Saved to {path}")
    plt.close(fig)
