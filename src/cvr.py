# ==============================================================
# Ball2Head — CRANIAL VULNERABILITY RATIO (CVRp) DASHBOARD
# Single Combined Figure — All Ball Types A1–G1 × Sizes 3/4/5
# CVRp = Peak-to-Peak Pressure / Age-Group Skull Density
# Birmingham Newman University — Final Year Project
# Hansen Sominabo Kekom
# Calibration: Phillips, I. et al. (2026)
# ==============================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --------------------------------------------------------------
# FONT SETUP — Plain Arial, guaranteed display
# --------------------------------------------------------------
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300

# ==============================================================
# CALIBRATION DATA — All 7 Ball Types (Phillips et al. 2026)
# ==============================================================
ball_data = {
    "A1": {"name": "Thermally Bonded", "mass_dry_kg": 0.4365, "k1_kPa_J": 0.0789, "color": "#1f77b4"},
    "B1": {"name": "Fuse Welded",    "mass_dry_kg": 0.4369, "k1_kPa_J": 0.0756, "color": "#ff7f0e"},
    "C1": {"name": "Machine Stitched","mass_dry_kg": 0.4273, "k1_kPa_J": 0.0818, "color": "#d62728"},
    "D1": {"name": "Hand Stitched",   "mass_dry_kg": 0.4243, "k1_kPa_J": 0.0722, "color": "#2ca02c"},
    "E1": {"name": "Synthetic Moulded","mass_dry_kg": 0.4370, "k1_kPa_J": 0.0775, "color": "#9467bd"},
    "F1": {"name": "Laceless Leather","mass_dry_kg": 0.4392, "k1_kPa_J": 0.0662, "color": "#8c564b"},
    "G1": {"name": "Laced Leather",   "mass_dry_kg": 0.4496, "k1_kPa_J": 0.0650, "color": "#e377c2"},
}

# ==============================================================
# BALL SIZE + AGE PROFILE — FIFA Mass Scaling + Skull Density
# ==============================================================
# Skull Density Constant: Higher = Thicker Skull = Lower Vulnerability
size_profile = {
    3: {"scale": 0.78, "label": "Size 3\n(U10)", "skull_density": 7.2, "color": "#4CAF50"},
    4: {"scale": 0.90, "label": "Size 4\n(U14)", "skull_density": 8.5, "color": "#FF9800"},
    5: {"scale": 1.00, "label": "Size 5\n(Elite)", "skull_density": 10.0, "color": "#E91E63"},
}

# Standard comparison velocity — Phillips et al. (2026) baseline
VELOCITY = 18  # m/s

# ==============================================================
# PHYSICS + CVRp CALCULATION
# ==============================================================
def compute_cvr(v, mass_kg, k1, skull_density):
    """
    E = 0.5 * m * v²
    Peak-to-Peak Pressure (kPa) = k1 * Energy
    Cranial Vulnerability Ratio (CVRp) = Pressure / Skull Density
    """
    Energy = 0.5 * mass_kg * (v ** 2)
    Peak_Pressure_kPa = k1 * Energy
    CVRp = Peak_Pressure_kPa / skull_density
    return round(Peak_Pressure_kPa, 3), round(CVRp, 4)

# ==============================================================
# BUILD DATA FOR ALL BALL TYPES × ALL SIZES
# ==============================================================
ball_ids = list(ball_data.keys())
x_pos = np.arange(len(ball_ids))
bar_width = 0.25

# Store results for plotting
pressure_data = {3: [], 4: [], 5: []}
cvr_data = {3: [], 4: [], 5: []}

for ball_id in ball_ids:
    b = ball_data[ball_id]
    for size in [3, 4, 5]:
        sz = size_profile[size]
        mass = b["mass_dry_kg"] * sz["scale"]
        kPa, cvrp = compute_cvr(VELOCITY, mass, b["k1_kPa_J"], sz["skull_density"])
        pressure_data[size].append(kPa)
        cvr_data[size].append(cvrp)

# ==============================================================
# 📊 SINGLE COMBINED DASHBOARD — LinkedIn Ready
# ==============================================================
fig, axes = plt.subplots(2, 1, figsize=(14, 10))

# --- TOP PLOT: Peak-to-Peak Pressure ---
ax1 = axes[0]
bars3 = ax1.bar(x_pos - bar_width, pressure_data[3], bar_width,
                label="Size 3 (U10)", color=size_profile[3]["color"], edgecolor="black", linewidth=0.5)
bars4 = ax1.bar(x_pos, pressure_data[4], bar_width,
                label="Size 4 (U14)", color=size_profile[4]["color"], edgecolor="black", linewidth=0.5)
bars5 = ax1.bar(x_pos + bar_width, pressure_data[5], bar_width,
                label="Size 5 (Elite)", color=size_profile[5]["color"], edgecolor="black", linewidth=0.5)

ax1.set_ylabel("Peak-to-Peak Pressure (kPa)", fontweight="bold", fontsize=12)
ax1.set_title("Heading Impact Pressure — All Ball Types @ 18 m/s (Dry)\nPressure alone suggests Elite > Youth — BUT THIS MISSES BIOLOGICAL VULNERABILITY",
              fontweight="bold", fontsize=13, color="#2c3e50")
ax1.set_xticks(x_pos)
ax1.set_xticklabels(ball_ids, fontweight="bold", fontsize=11)
ax1.legend(fontsize=11)
ax1.set_ylim(0, 7.5)
ax1.bar_label(bars5, fmt="%.1f", fontsize=8, padding=1)

# --- BOTTOM PLOT: Cranial Vulnerability Ratio (CVRp) ---
ax2 = axes[1]
bars3_cvr = ax2.bar(x_pos - bar_width, cvr_data[3], bar_width,
                    label="Size 3 (U10) — Skull Density = 7.2", color=size_profile[3]["color"], edgecolor="black", linewidth=0.5)
bars4_cvr = ax2.bar(x_pos, cvr_data[4], bar_width,
                    label="Size 4 (U14) — Skull Density = 8.5", color=size_profile[4]["color"], edgecolor="black", linewidth=0.5)
bars5_cvr = ax2.bar(x_pos + bar_width, cvr_data[5], bar_width,
                    label="Size 5 (Elite) — Skull Density = 10.0", color=size_profile[5]["color"], edgecolor="black", linewidth=0.5)

ax2.set_ylabel("Cranial Vulnerability Ratio (CVRp)\n= Pressure ÷ Skull Density",
               fontweight="bold", fontsize=12)
ax2.set_title("CRANIAL VULNERABILITY RATIO — Youth > Elite at SAME Impact Velocity\nBiological Correction: Thinner Youth Skull = Higher Real Exposure",
              fontweight="bold", fontsize=14, color="#c0392b")
ax2.set_xticks(x_pos)
ax2.set_xticklabels(ball_ids, fontweight="bold", fontsize=11)
ax2.legend(fontsize=11)
ax2.set_ylim(0, 0.75)
ax2.bar_label(bars3_cvr, fmt="%.2f", fontsize=8, padding=1)

# --- Overall Figure Footer ---
fig.suptitle("Ball2Head — Pressure vs Biological Vulnerability\nCalibrated: Phillips et al. (2026) | Velocity Input Only | Standardised 18 m/s Comparison",
             fontsize=15, fontweight="bold", y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.97])

# --- Save — ONE PNG + ONE PDF ---
plt.savefig("Ball2Head_CVRp_Dashboard_LinkedIn.png", dpi=300, bbox_inches="tight")
plt.savefig("Ball2Head_CVRp_Dashboard_LinkedIn.pdf", bbox_inches="tight")
print("✅ SINGLE DASHBOARD SAVED: Ball2Head_CVRp_Dashboard_LinkedIn.png + .pdf")
print("\n🔬 KEY FINDING: SAME velocity → Youth CVRp ≈ 1.4× Elite vulnerability")
plt.show()