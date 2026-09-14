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
ball_labels = ['G1\nLaced Leather\n(LOWEST Risk)', 'E1\nSynthetic Moulded\n(HIGHEST Risk)']
joules_input = [74.46, 72.38]
kpa_output = [3.57, 18.24]
colors_energy = ['#2ca02c', '#ff9800']   # Green = G1, Orange = E1
colors_pressure = ['#2ca02c', '#d62728'] # Green = G1, Red = E1

# ======================
# FIGURE — 2 SUBPLOTS
# ======================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.5))

# --- Left Plot: Kinetic Energy Input (Joules) ---
bars1 = ax1.bar(ball_labels, joules_input, color=colors_energy, edgecolor='#333333', linewidth=0.6, width=0.55)
ax1.set_ylabel('Kinetic Energy Input (J)', fontweight='bold', labelpad=10)
ax1.set_title('Input: Impact Energy', pad=12)
ax1.set_ylim(0, 85)
ax1.grid(axis='y', linestyle='--', alpha=0.4)
ax1.set_axisbelow(True)

# Value labels + annotations
for bar in bars1:
    h = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., h + 1.2,
             f'{h:.2f} J', ha='center', va='bottom', fontweight='semibold')
ax1.text(0, 78, '↑ Highest Input', ha='center', fontsize=10, fontweight='bold', color='#2ca02c')

# --- Right Plot: Peak Pressure Output (kPa) ---
bars2 = ax2.bar(ball_labels, kpa_output, color=colors_pressure, edgecolor='#333333', linewidth=0.6, width=0.55)
ax2.set_ylabel('Peak Pressure Output (kPa)', fontweight='bold', labelpad=10)
ax2.set_title('Output: Intracranial Pressure Wave', pad=12)
ax2.set_ylim(0, 21)
ax2.grid(axis='y', linestyle='--', alpha=0.4)
ax2.set_axisbelow(True)

# Value labels + annotations
for bar in bars2:
    h = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., h + 0.35,
             f'{h:.2f} kPa', ha='center', va='bottom', fontweight='semibold')
ax2.text(0, 5, '↓ Lowest Output', ha='center', fontsize=10, fontweight='bold', color='#2ca02c')
ax2.text(1, 19.5, '↑ Highest Output', ha='center', fontsize=10, fontweight='bold', color='#d62728')

# --- Main Title & Key Insight Annotation ---
fig.suptitle('The Energy Transfer Anomaly — Input Energy ≠ Output Pressure\nSame Impact Velocity (18 m/s) — Ball Construction Determines Risk',
             fontsize=14, fontweight='bold', y=1.05)

# Central arrow showing the reversal
fig.text(0.5, 0.52, '→ 5.1× Pressure Difference ←\nDespite Nearly Identical Input Energy',
         ha='center', va='center', fontsize=12, fontweight='bold', color='#555',
         bbox=dict(boxstyle='round,pad=0.4', fc='#fff3cd', ec='#d62728', alpha=0.9))

# Source citation
plt.figtext(0.5, 0.01,
            'Source: Phillips, I. et al. (2026) Pressure wave propagation from association football head collisions — Table 3 / Figure 3(a)',
            ha='center', fontsize=9, style='italic')

# Clean up spines
for ax in [ax1, ax2]:
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

plt.tight_layout(rect=[0, 0.04, 1, 0.97])

# Save for dissertation
plt.savefig('energy_vs_pressure_anomaly.png', dpi=300, bbox_inches='tight')
plt.savefig('energy_vs_pressure_anomaly.pdf', bbox_inches='tight')
plt.show()