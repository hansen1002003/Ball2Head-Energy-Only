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
    'C1\nMachine-Stitched\n(Official Elite)',
    'E1\nMoulded\n(Recreational)'
]
blu_values = [1.42, 4.36]
colors = ['#2ca02c', '#d62728']  # Green = Safest, Red = Most Dangerous
rankings = ['6th / 7\n(Safest)', '1st / 7\n(Most Dangerous)']

# ======================
# FIGURE
# ======================
fig, ax = plt.subplots(figsize=(8, 6))

# Main bars
bars = ax.bar(ball_labels, blu_values, color=colors, edgecolor='#333333',
              linewidth=0.6, width=0.5, zorder=3)

# Axes setup
ax.set_ylabel('Brain Load Units (BLU = kPa × ms)', fontweight='bold', labelpad=10)
ax.set_title('The "Elite Ball" Paradox — Official Match Ball vs Recreational',
             pad=15, fontsize=14, fontweight='bold')
ax.set_ylim(0, 5.2)
ax.grid(axis='y', linestyle='--', alpha=0.4, zorder=0)
ax.set_axisbelow(True)

# Value labels + rankings
for i, bar in enumerate(bars):
    h = bar.get_height()
    # BLU value
    ax.text(bar.get_x() + bar.get_width()/2., h + 0.12,
            f'{h:.2f} BLU', ha='center', va='bottom', fontweight='bold', fontsize=13)
    # Ranking below value
    ax.text(bar.get_x() + bar.get_width()/2., h/2,
            rankings[i], ha='center', va='center', fontsize=11, fontweight='semibold',
            color='white', bbox=dict(boxstyle='round,pad=0.3', fc='black', alpha=0.5))

# 3.1× difference annotation
ax.annotate(
    '3.1× Higher\nBrain Load',
    xy=(1, 4.36), xytext=(0.5, 4.8),
    arrowprops=dict(facecolor='#d62728', edgecolor='#d62728', width=2, headwidth=8, shrink=0.05),
    fontsize=13, fontweight='bold', color='#d62728',
    bbox=dict(boxstyle='round,pad=0.4', fc='#ffdbdb', ec='#d62728', alpha=0.9))

# Source citation
plt.figtext(0.5, 0.02,
            'Source: Phillips, I. et al. (2026) Pressure wave propagation — BLU = Peak Pressure × Wave Duration',
            ha='center', fontsize=9, style='italic')

# Cleanup spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout(rect=[0, 0.05, 1, 0.98])

# Save for dissertation
plt.savefig('elite_ball_paradox.png', dpi=300, bbox_inches='tight')
plt.savefig('elite_ball_paradox.pdf', bbox_inches='tight')
plt.show()