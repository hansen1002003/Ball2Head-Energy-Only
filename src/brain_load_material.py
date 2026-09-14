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
categories = ['Synthetic\n(A1, B1, C1, D1, E1)', 'Leather\n(F1, G1)']
avg_kpa = [11.81, 4.66]
avg_blu = [2.81, 1.66]
colors = ['#d62728', '#2ca02c']  # Red = Synthetic, Green = Leather

# ======================
# FIGURE — 2 SUBPLOTS
# ======================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# --- Left Plot: Peak Pressure (kPa) ---
bars1 = ax1.bar(categories, avg_kpa, color=colors, edgecolor='#333333', linewidth=0.6, width=0.55)
ax1.set_ylabel('Average Peak Pressure (kPa)', fontweight='bold', labelpad=10)
ax1.set_title('Pressure Wave Magnitude', pad=12)
ax1.set_ylim(0, 14)
ax1.grid(axis='y', linestyle='--', alpha=0.4)
ax1.set_axisbelow(True)

# Value labels
for bar in bars1:
    h = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., h + 0.3,
             f'{h:.2f} kPa', ha='center', va='bottom', fontweight='semibold')

# Annotation: 2.5× difference
ax1.annotate(
    '2.5× Higher',
    xy=(0, 11.81), xytext=(0.5, 12.8),
    arrowprops=dict(arrowstyle='->', lw=2, color='#d62728'),
    fontsize=12, fontweight='bold', color='#d62728',
    bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='#d62728', alpha=0.9)
)

# --- Right Plot: Brain Load Units (BLU) ---
bars2 = ax2.bar(categories, avg_blu, color=colors, edgecolor='#333333', linewidth=0.6, width=0.55)
ax2.set_ylabel('Average Brain Load Units (BLU)', fontweight='bold', labelpad=10)
ax2.set_title('Total Brain Load (kPa × ms)', pad=12)
ax2.set_ylim(0, 3.5)
ax2.grid(axis='y', linestyle='--', alpha=0.4)
ax2.set_axisbelow(True)

# Value labels
for bar in bars2:
    h = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., h + 0.08,
             f'{h:.2f} BLU', ha='center', va='bottom', fontweight='semibold')

# Annotation: 1.7× difference
ax2.annotate(
    '1.7× Higher',
    xy=(0, 2.81), xytext=(0.5, 3.2),
    arrowprops=dict(arrowstyle='->', lw=2, color='#d62728'),
    fontsize=12, fontweight='bold', color='#d62728',
    bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='#d62728', alpha=0.9)
)

# --- Main Title & Source ---
fig.suptitle('Synthetic vs Leather Footballs — Material Effect on Head Impact Load\nMean Values at 18 m/s Impact Velocity, Dry Conditions',
             fontsize=14, fontweight='bold', y=1.02)

plt.figtext(0.5, 0.01,
            'Source: Phillips, I. et al. (2026) Pressure wave propagation from association football head collisions',
            ha='center', fontsize=9, style='italic')

# Clean up
for ax in [ax1, ax2]:
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

plt.tight_layout(rect=[0, 0.04, 1, 0.98])

# Save
plt.savefig('synthetic_vs_leather_load.png', dpi=300, bbox_inches='tight')
plt.savefig('synthetic_vs_leather_load.pdf', bbox_inches='tight')
plt.show()