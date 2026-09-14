import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams

# ======================
# PH.D STANDARD SETTINGS
# ======================
rcParams['font.family'] = 'serif'
rcParams['font.size'] = 11
rcParams['axes.labelsize'] = 12
rcParams['axes.titlesize'] = 13
rcParams['xtick.labelsize'] = 11
rcParams['ytick.labelsize'] = 11
rcParams['figure.dpi'] = 300
rcParams['savefig.dpi'] = 300
rcParams['savefig.bbox'] = 'tight'
rcParams['axes.linewidth'] = 0.8

# ======================
# DATA
# ======================
ball_labels = [
    'G1\nLaced\nLeather',
    'F1\nLaceless\nLeather',
    'A1–E1\nSynthetic\nRange'
]
ppsi90_times = [0.577, 0.220, 0.235]  # Mean of 0.223–0.248 for synthetics
error_min = [0, 0, 0.223]
error_max = [0, 0, 0.248]
colors = ['#ff7f0e', '#2ca02c', '#1f77b4']  # Orange = G1, Green = F1, Blue = Synthetics

# ======================
# FIGURE
# ======================
fig, ax = plt.subplots(figsize=(9, 6))

# Main bars
bars = ax.bar(ball_labels, ppsi90_times, color=colors, edgecolor='#333333',
              linewidth=0.6, width=0.55, zorder=3)

# Range bar for synthetics (min–max indicator)
ax.hlines(0.223, xmin=2-0.25, xmax=2+0.25, color='#1f77b4', linestyle='--',
          linewidth=1.5, alpha=0.7, label='Min Range')
ax.hlines(0.248, xmin=2-0.25, xmax=2+0.25, color='#1f77b4', linestyle='--',
          linewidth=1.5, alpha=0.7, label='Max Range')
ax.fill_between([2-0.3, 2+0.3], 0.223, 0.248, color='#1f77b4', alpha=0.12)

# Axes setup
ax.set_ylabel('PPSI90 Pressure Rise Time (ms)', fontweight='bold', labelpad=10)
ax.set_title('Pressure Wave Rise Time — The "Slow Burn" Effect of Laced Leather', pad=15, fontsize=14, fontweight='bold')
ax.set_ylim(0, 0.65)
ax.grid(axis='y', linestyle='--', alpha=0.4, zorder=0)
ax.set_axisbelow(True)

# Value labels + annotations
for i, bar in enumerate(bars):
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., h + 0.015,
            f'{h:.3f} ms', ha='center', va='bottom', fontweight='semibold', fontsize=12)

# G1 standout annotation
ax.annotate(
    '2.4× Longer\nRise Time',
    xy=(0, 0.577), xytext=(0.6, 0.52),
    arrowprops=dict(facecolor='#ff7f0e', edgecolor='#ff7f0e', width=2, headwidth=8, shrink=0.05),
    fontsize=13, fontweight='bold', color='#d65f00',
    bbox=dict(boxstyle='round,pad=0.4', fc='#ffe8cc', ec='#ff7f0e', alpha=0.9)
)

# Baseline reference line
ax.axhline(y=0.235, color='#555555', linestyle=':', linewidth=1.5, alpha=0.6,
           label='Synthetic Mean (0.235 ms)')

# Legend & source
ax.legend(loc='upper right', fontsize=10)
plt.figtext(0.5, 0.02,
            'Source: Phillips, I. et al. (2026) Pressure wave propagation from association football head collisions — PPSI90 rise-time metric',
            ha='center', fontsize=9, style='italic')

# Cleanup spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout(rect=[0, 0.05, 1, 0.98])

# Save for dissertation
plt.savefig('ppsi90_rise_time.png', dpi=300, bbox_inches='tight')
plt.savefig('ppsi90_rise_time.pdf', bbox_inches='tight')
plt.show()