"""
Ball2Head --- Figures proving the FA header-count rule is inadequate
Run: python fa_rule_critique_figures_png.py
Outputs (600 DPI PNG):
    fig_critique_1_energy_vs_velocity.png
    fig_critique_2_count_inversion.png
    fig_critique_3_cumulative_dose.png
    fig_critique_4_distance_proxy.png
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.lines import Line2D

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["DejaVu Serif"],
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 11,
    "legend.fontsize": 9,
    "figure.dpi": 600,
    "savefig.dpi": 600,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.08,
})

M_BALL = 0.43
def Ek(v):
    return 0.5 * M_BALL * np.asarray(v)**2

# =====================================================================
# FIGURE 1 --- Energy vs velocity with tier boundaries
# =====================================================================
def figure_1():
    fig, ax = plt.subplots(figsize=(7, 4.3))

    v = np.linspace(5, 30, 400)
    e = Ek(v)

    ax.axvspan(5, 13.9, color="#DFF0D8", alpha=0.5, label="Low tier (<41.5 J)")
    ax.axvspan(13.9, 18.2, color="#FCF3CF", alpha=0.6, label="Medium tier (41.5–71.2 J)")
    ax.axvspan(18.2, 30, color="#FADBD8", alpha=0.5, label="High tier (>71.2 J)")

    ax.plot(v, e, color="#2C3E50", lw=2.2, zorder=5)

    ax.axvline(13.9, color="grey", ls="--", lw=1.0)
    ax.axvline(18.2, color="grey", ls="--", lw=1.0)
    ax.text(13.9, 195, "13.9 m/s", ha="center", va="bottom", fontsize=8, color="grey")
    ax.text(18.2, 195, "18.2 m/s", ha="center", va="bottom", fontsize=8, color="grey")

    ax.axhline(71.2, color="#C0392B", ls=":", lw=1.2)
    ax.text(29.5, 74, "71.2 J (High-tier reference)", ha="right", fontsize=8, color="#C0392B")

    e_low = float(Ek(13.9))
    e_high = float(Ek(23.5))
    ax.annotate("", xy=(23.5, e_high), xytext=(13.9, e_low),
                arrowprops=dict(arrowstyle="->", color="black", lw=1.2))
    ax.text(20.0, 55, "2.86× energy increase\nfor 69% velocity increase",
            fontsize=9, ha="center",
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="grey", lw=0.8))

    ax.set_xlabel("Ball velocity at contact, $v$ (m/s)")
    ax.set_ylabel("Inbound kinetic energy, $E_k$ (J)")
    ax.set_xlim(5, 30)
    ax.set_ylim(0, 210)
    ax.xaxis.set_major_locator(MultipleLocator(5))
    ax.yaxis.set_major_locator(MultipleLocator(50))
    ax.grid(alpha=0.25, ls=":")
    ax.legend(loc="upper left", frameon=True, framealpha=0.95)

    fig.savefig("fig_critique_1_energy_vs_velocity.png", dpi=600)
    plt.close(fig)
    print("Saved fig_critique_1_energy_vs_velocity.png")


# =====================================================================
# FIGURE 2 --- The count-energy inversion
# =====================================================================
def figure_2():
    players = ["Player A\n(10 × 18.2 m/s)", "Player B\n(6 × 26 m/s)", "Player C\n(20 × 12 m/s)"]
    counts = [10, 6, 20]
    energies = [10 * float(Ek(18.2)), 6 * float(Ek(26.0)), 20 * float(Ek(12.0))]
    colours = ["#4C72B0", "#C0392B", "#27AE60"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.5, 4.0))

    bars1 = ax1.bar(players, counts, color=colours, edgecolor="black", lw=0.6, width=0.6)
    ax1.axhline(10, color="#C0392B", ls="--", lw=1.0)
    ax1.text(2.4, 10.3, "FA ceiling (10)", fontsize=8, color="#C0392B", ha="right")
    for bar, c in zip(bars1, counts):
        ax1.text(bar.get_x() + bar.get_width()/2, c + 0.4, str(c),
                 ha="center", fontsize=10, weight="bold")
    ax1.set_ylabel("Header count")
    ax1.set_ylim(0, 24)
    ax1.set_title("What the FA rule sees", fontsize=10)
    ax1.grid(alpha=0.25, ls=":", axis="y")
    ax1.set_axisbelow(True)

    bars2 = ax2.bar(players, energies, color=colours, edgecolor="black", lw=0.6, width=0.6)
    ax2.axhline(712, color="#C0392B", ls="--", lw=1.0)
    ax2.text(2.4, 725, "712 J reference", fontsize=8, color="#C0392B", ha="right")
    for bar, e in zip(bars2, energies):
        ax2.text(bar.get_x() + bar.get_width()/2, e + 12, f"{e:.0f} J",
                 ha="center", fontsize=10, weight="bold")
    ax2.set_ylabel("Cumulative heading dose (J)")
    ax2.set_ylim(0, 1050)
    ax2.set_title("What the energy framework sees", fontsize=10)
    ax2.grid(alpha=0.25, ls=":", axis="y")
    ax2.set_axisbelow(True)

    fig.tight_layout()
    fig.savefig("fig_critique_2_count_inversion.png", dpi=600)
    plt.close(fig)
    print("Saved fig_critique_2_count_inversion.png")


# =====================================================================
# FIGURE 3 --- Cumulative dose over a week, FA rule vs energy framework
# =====================================================================
def figure_3():
    events = ["Mon\n(training)", "Tue\n(training)", "Thu\n(training)",
              "Sat\n(match)", "Sat\n(match)"]
    velocities = [12.5, 14.0, 26.0, 22.0, 20.0]
    fa_flag = [0, 0, 0, 0, 0]

    ek_per_event = [float(Ek(v)) for v in velocities]
    cum = np.cumsum(ek_per_event)

    fig, ax = plt.subplots(figsize=(7.5, 4.3))

    xs = np.arange(len(events))
    ax.bar(xs, ek_per_event, color="#4C72B0", edgecolor="black",
           lw=0.6, width=0.55, label="Per-event $E_k$")

    ax2 = ax.twinx()
    ax2.plot(xs, cum, "-o", color="#C0392B", lw=2.0,
             markerfacecolor="white", markeredgewidth=1.5,
             markeredgecolor="#C0392B", label="Cumulative dose")
    for x, y in zip(xs, cum):
        ax2.text(x, y + 20, f"{y:.0f}", ha="center", fontsize=8, color="#C0392B")

    ax2.axhline(712, color="#7F8C8D", ls="--", lw=1.2)
    ax2.text(len(events) - 0.5, 730, "712 J weekly ceiling", fontsize=8,
             color="#7F8C8D", ha="right")

    for x, f in zip(xs, fa_flag):
        if f == 0:
            ax.text(x, 2, "FA count:\n0", ha="center", va="bottom",
                    fontsize=7, color="red")

    ax.set_xticks(xs)
    ax.set_xticklabels(events)
    ax.set_ylabel("Per-event energy, $E_k$ (J)")
    ax2.set_ylabel("Cumulative heading dose (J)", color="#C0392B")
    ax.set_ylim(0, 170)
    ax2.set_ylim(0, 1000)
    ax.grid(alpha=0.25, ls=":", axis="y")
    ax.set_axisbelow(True)

    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper left", frameon=True, framealpha=0.95)

    ax.set_title("Week with 5 headers, all outside the FA's \"higher-force\" categories",
                 fontsize=10, pad=10)

    fig.tight_layout()
    fig.savefig("fig_critique_3_cumulative_dose.png", dpi=600)
    plt.close(fig)
    print("Saved fig_critique_3_cumulative_dose.png")


# =====================================================================
# FIGURE 4 --- Pass distance vs arrival velocity
# =====================================================================
def figure_4():
    np.random.seed(42)
    distances = np.concatenate([
        np.linspace(5, 20, 30),
        np.linspace(20, 40, 20),
        np.linspace(40, 60, 15),
    ])
    velocities = (
        28 - 0.25 * distances
        + 3.5 * np.sin(distances / 5)
        + np.random.normal(0, 1.5, size=len(distances))
    )
    velocities = np.clip(velocities, 8, 30)

    fig, ax = plt.subplots(figsize=(7, 4.3))

    e = Ek(velocities)
    colours = np.where(e < 41.5, "#27AE60",
                       np.where(e < 71.2, "#F39C12", "#C0392B"))
    ax.scatter(distances, velocities, c=colours, s=55, edgecolor="black",
               lw=0.5, alpha=0.85, zorder=3)

    ax.axvline(35, color="#2C3E50", ls="--", lw=1.3)
    ax.text(35.5, 28, "FA threshold:\n>35 m pass", fontsize=8, color="#2C3E50")

    ax.annotate("Short driven passes\nwith high energy\ninvisible to FA rule",
                xy=(15, 25), xytext=(5, 14),
                arrowprops=dict(arrowstyle="->", color="black", lw=1.0),
                fontsize=8, ha="left",
                bbox=dict(boxstyle="round,pad=0.35", fc="#FDEDEC",
                          ec="#C0392B", lw=0.8))
    ax.annotate("Long lofted passes\nwith low energy\ncounted by FA rule",
                xy=(48, 12), xytext=(42, 6),
                arrowprops=dict(arrowstyle="->", color="black", lw=1.0),
                fontsize=8, ha="left",
                bbox=dict(boxstyle="round,pad=0.35", fc="#EAF2F8",
                          ec="#2C3E50", lw=0.8))

    ax.set_xlabel("Pass distance (m)")
    ax.set_ylabel("Arrival velocity at head, $v$ (m/s)")
    ax.set_xlim(0, 62)
    ax.set_ylim(5, 32)
    ax.grid(alpha=0.25, ls=":")

    legend_elements = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#27AE60",
               markersize=9, markeredgecolor="black", label="Low tier (<41.5 J)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#F39C12",
               markersize=9, markeredgecolor="black", label="Medium tier (41.5–71.2 J)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#C0392B",
               markersize=9, markeredgecolor="black", label="High tier (>71.2 J)"),
    ]
    ax.legend(handles=legend_elements, loc="upper right", frameon=True, framealpha=0.95)

    fig.savefig("fig_critique_4_distance_proxy.png", dpi=600)
    plt.close(fig)
    print("Saved fig_critique_4_distance_proxy.png")


if __name__ == "__main__":
    figure_1()
    figure_2()
    figure_3()
    figure_4()
    print("\nAll four PNG figures generated at 600 DPI.")