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
# DATA — ALL 7 BALLS
# ======================
ball_codes = ['E1', 'A1', 'B1', 'G1', 'D1', 'C1', 'F1']
blu_values = [4.36, 3.23, 3.04, 2.06, 2.00, 1.42, 1.27]
construction = [
    'Synthetic Moulded',
    'Thermally Bonded — FIFA Elite Standard',
    'Fuse-Welded',
    'Laced Leather',
    'Hand-Stitched',
    'Machine-Stitched',
    'Laceless Leather'
]
colors = ['#d62728', '#9467bd', '#ff7f0e', '#ffb347', '#2ca02c', '#1f77b4', '#17a248']

# ======================
# FIGURE
# ======================
fig, ax = plt.subplots(figsize=(12, 7))

# Main bars
bars = ax.bar(ball_codes, blu_values, color=colors, edgecolor='#222222',
              linewidth=0.7, width=0.65, zorder=3)

# Axes setup
ax.set_ylabel('Brain Load Units (BLU = kPa × ms)', fontweight='bold', labelpad=10)
ax.set_xlabel('Ball Code — Construction Method', fontweight='bold', labelpad=10)
ax.set_title('Heading Load by Ball Construction — All 7 Ball Types\nTest Condition: 18 m/s Impact Velocity, Dry Surface',
             pad=18, fontsize=14, fontweight='bold')
ax.set_ylim(0, 5.2)
ax.grid(axis='y', linestyle='--', alpha=0.4, zorder=0)
ax.set_axisbelow(True)

# Value labels above each bar
for bar in bars:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., h + 0.07,
            f'{h:.2f}', ha='center', va='bottom', fontweight='bold', fontsize=11)

# Annotate key comparisons
# E1 vs C1
ax.annotate(
    f'E1 = {blu_values[0]/blu_values[5]:.1f}× C1\n(identical velocity)',
    xy=(5, blu_values[5]), xytext=(0.8, 4.6),
    arrowprops=dict(arrowstyle='->', lw=1.8, color='#333333'),
    fontsize=11, fontweight='bold', bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='#555', alpha=0.9))

# A1 (Elite) note
ax.text(1, 3.45, 'A1 = FIFA Elite Standard\nHigher BLU due to construction',
        ha='center', fontsize=10, fontweight='semibold', color='#9467bd',
        bbox=dict(boxstyle='round,pad=0.25', fc='#f3e9f8', ec='#9467bd', alpha=0.8))

# Safest ball note
ax.text(6, 1.45, 'Safest\n(F1)', ha='center', fontsize=10, fontweight='bold', color='#17a248')

# Source citation
plt.figtext(0.5, 0.015,
            'Source: Phillips, I. et al. (2026) Pressure wave propagation from association football head collisions. '
            'BLU = Peak Pressure (kPa) × PPSI90 Duration (ms). A1 = FIFA Elite Standard; C1 = Machine-Stitched construction.',
            ha='center', fontsize=8.5, style='italic', wrap=True)

# Cleanup spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout(rect=[0, 0.04, 1, 0.97])

# Save for dissertation
plt.savefig('all_balls_blu_ranking.png', dpi=300, bbox_inches='tight')
plt.savefig('all_balls_blu_ranking.pdf', bbox_inches='tight')
plt.show()