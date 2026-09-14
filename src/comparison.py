# ==============================================================
# Ball2Head — STANDARDISED COMPARISON DASHBOARD (FIXED)
# Peak-to-Peak Pressure (kPa) | PPSI90 Total Duration (ms)
# All Ball Types × Sizes 3/4/5 × Dry/Damp/Wet Conditions
# Birmingham Newman University — Final Year Project
# Hansen Sominabo Kekom
# Calibration Source: Phillips, I. et al. (2026)
# ==============================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --------------------------------------------------------------
# FONT SETUP — Plain Arial, NO special symbols → guaranteed display
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
    "A1": {"name": "Thermally Bonded", "mass_dry_kg": 0.4365, "k1_kPa_J": 0.0789, "k2_ms_J": 0.00344, "color": "#1f77b4"},
    "B1": {"name": "Fuse Welded",    "mass_dry_kg": 0.4369, "k1_kPa_J": 0.0756, "k2_ms_J": 0.00334, "color": "#ff7f0e"},
    "C1": {"name": "Machine Stitched","mass_dry_kg": 0.4273, "k1_kPa_J": 0.0818, "k2_ms_J": 0.00359, "color": "#d62728"},
    "D1": {"name": "Hand Stitched",   "mass_dry_kg": 0.4243, "k1_kPa_J": 0.0722, "k2_ms_J": 0.00324, "color": "#2ca02c"},
    "E1": {"name": "Synthetic Moulded","mass_dry_kg": 0.4370, "k1_kPa_J": 0.0775, "k2_ms_J": 0.00337, "color": "#9467bd"},
    "F1": {"name": "Laceless Leather","mass_dry_kg": 0.4392, "k1_kPa_J": 0.0662, "k2_ms_J": 0.00309, "color": "#8c564b"},
    "G1": {"name": "Laced Leather",   "mass_dry_kg": 0.4496, "k1_kPa_J": 0.0650, "k2_ms_J": 0.00300, "color": "#e377c2"},
}

# ==============================================================
# ENVIRONMENTAL CONDITIONS — Dry / Damp / Wet
# ==============================================================
conditions = {
    "Dry":  {"mass_factor": 1.00, "color": "#8B4513"},
    "Damp": {"mass_factor": 1.03, "color": "#FF8C00"},
    "Wet":  {"mass_factor": 1.06, "color": "#1976D2"},
}

# ==============================================================
# BALL SIZE SCALING — FIFA Standard Mass Ratios
# ==============================================================
size_profile = {
    3: {"scale": 0.78, "label": "Size 3 (U10)", "color": "#4CAF50"},
    4: {"scale": 0.90, "label": "Size 4 (U14)", "color": "#FF9800"},
    5: {"scale": 1.00, "label": "Size 5 (Elite)", "color": "#E91E63"},
}

# Velocity range matching Phillips et al. (2026)
velocities = np.array([10, 14, 18, 23, 28, 35])

# ==============================================================
# PHYSICS CALCULATION — Velocity Input Only
# ==============================================================
# NOTE: Rise Time excluded — requires sensor sampling rate (500Hz+),
# which is not available from stadium tracking or computer vision.
# We calculate ONLY: Peak-to-Peak Pressure and PPSI90 Total Duration.

def compute_metrics(v, mass_kg, k1, k2):
    """
    Input: Ball velocity (m/s)  [from computer vision / stadium tracking]
    Output: Peak-to-Peak Pressure (kPa), PPSI90 Total Duration (ms)
    E = 0.5 * mass * velocity^2
    Pressure = k1 * Energy
    Duration = k2 * Energy   -> PPSI90 Total Pressure Wave Duration
    """
    Energy = 0.5 * mass_kg * (v ** 2)
    Peak_Pressure_kPa = k1 * Energy
    PPSI90_Duration_ms = k2 * Energy
    return round(Energy, 2), round(Peak_Pressure_kPa, 3), round(PPSI90_Duration_ms, 4)

# ==============================================================
# BUILD FULL DATASET — ALL Combinations
# ==============================================================
rows = []
for ball_id, ball in ball_data.items():
    for size, sz in size_profile.items():
        for cond, env in conditions.items():
            mass = ball["mass_dry_kg"] * sz["scale"] * env["mass_factor"]
            for v in velocities:
                E, kPa, ms = compute_metrics(v, mass, ball["k1_kPa_J"], ball["k2_ms_J"])
                rows.append({
                    "Ball_Type": ball_id,
                    "Ball_Name": ball["name"],
                    "Ball_Size": size,
                    "Size_Label": sz["label"],
                    "Condition": cond,
                    "Mass_kg": round(mass, 4),
                    "Velocity_m_s": v,
                    "Energy_J": E,
                    "Peak_Pressure_kPa": kPa,
                    "PPSI90_Duration_ms": ms,
                })

df = pd.DataFrame(rows)
df.to_csv("Ball2Head_Standardised_Full_Dataset.csv", index=False)
print(f"✅ Full Dataset Saved: {len(df)} rows")

# ==============================================================
# 📊 FIGURE 1: PRESSURE COMPARISON — All Ball Types × Sizes × Conditions @ 18 m/s
# ==============================================================
speed_18 = df[df["Velocity_m_s"] == 18]
fig1, axes = plt.subplots(2, 4, figsize=(18, 9))
axes = axes.flatten()

for idx, ball_id in enumerate(ball_data.keys()):
    ax = axes[idx]
    bd = speed_18[speed_18["Ball_Type"] == ball_id]
    x_pos = np.arange(9)
    labels = []
    values = []
    bar_colors = []
    
    for size in [3, 4, 5]:
        for cond in ["Dry", "Damp", "Wet"]:
            entry = bd[(bd["Ball_Size"] == size) & (bd["Condition"] == cond)]
            val = entry["Peak_Pressure_kPa"].values[0]
            lbl = f"S{size}-{cond[0]}"
            labels.append(lbl)
            values.append(val)
            bar_colors.append(conditions[cond]["color"])
    
    bars = ax.bar(x_pos, values, color=bar_colors, edgecolor="black", linewidth=0.5)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, fontsize=7, rotation=45)
    ax.set_ylabel("Peak-to-Peak Pressure (kPa)", fontweight="bold")
    ax.set_title(f"{ball_id}: {ball_data[ball_id]['name'][:15]}", fontweight="bold", fontsize=9)
    ax.set_ylim(0, 8.5)
    ax.tick_params(axis='y', labelsize=8)

axes[-1].axis("off")
fig1.suptitle("PEAK-TO-PEAK PRESSURE — All Ball Types × Sizes × Conditions @ 18 m/s\n"
               "Input: Velocity Only | Dry=100% | Damp=+3% Mass | Wet=+6% Mass | Phillips et al. (2026)",
               fontsize=15, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("Ball2Head_Figure1_Pressure_Comparison.png", dpi=300, bbox_inches="tight")
plt.savefig("Ball2Head_Figure1_Pressure_Comparison.pdf", bbox_inches="tight")
print("✅ Figure 1 — Pressure Comparison Saved")

# ==============================================================
# 📊 FIGURE 2: PPSI90 DURATION COMPARISON — All Ball Types × Sizes × Conditions @ 18 m/s
# ==============================================================
fig2, axes = plt.subplots(2, 4, figsize=(18, 9))
axes = axes.flatten()

for idx, ball_id in enumerate(ball_data.keys()):
    ax = axes[idx]
    bd = speed_18[speed_18["Ball_Type"] == ball_id]
    x_pos = np.arange(9)
    labels = []
    values = []
    bar_colors = []
    
    for size in [3, 4, 5]:
        for cond in ["Dry", "Damp", "Wet"]:
            entry = bd[(bd["Ball_Size"] == size) & (bd["Condition"] == cond)]
            val = entry["PPSI90_Duration_ms"].values[0]
            lbl = f"S{size}-{cond[0]}"
            labels.append(lbl)
            values.append(val)
            bar_colors.append(conditions[cond]["color"])
    
    bars = ax.bar(x_pos, values, color=bar_colors, edgecolor="black", linewidth=0.5)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, fontsize=7, rotation=45)
    ax.set_ylabel("PPSI90 Duration (ms)", fontweight="bold")
    ax.set_title(f"{ball_id}: {ball_data[ball_id]['name'][:15]}", fontweight="bold", fontsize=9)
    ax.set_ylim(0, 0.30)
    ax.tick_params(axis='y', labelsize=8)

axes[-1].axis("off")
fig2.suptitle("PPSI90 TOTAL PRESSURE WAVE DURATION — All Ball Types × Sizes × Conditions @ 18 m/s\n"
               "Note: Rise Time excluded — requires sensor sampling rate, not scalable from velocity data",
               fontsize=15, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("Ball2Head_Figure2_Duration_Comparison.png", dpi=300, bbox_inches="tight")
plt.savefig("Ball2Head_Figure2_Duration_Comparison.pdf", bbox_inches="tight")
print("✅ Figure 2 — Duration Comparison Saved")

# ==============================================================
# 📊 FIGURE 3: VELOCITY RESPONSE CURVES — Dry Condition, All Sizes, All Ball Types
# ==============================================================
dry_data = df[df["Condition"] == "Dry"]
fig3, axes = plt.subplots(2, 4, figsize=(18, 9))
axes = axes.flatten()

for idx, ball_id in enumerate(ball_data.keys()):
    ax = axes[idx]
    bd = dry_data[dry_data["Ball_Type"] == ball_id]
    for size in [3, 4, 5]:
        sz = bd[bd["Ball_Size"] == size]
        ax.plot(sz["Velocity_m_s"], sz["Peak_Pressure_kPa"],
                color=size_profile[size]["color"], linewidth=2.5,
                marker="o", markersize=5, label=size_profile[size]["label"])
    ax.set_xlabel("Impact Velocity (m/s)", fontweight="bold")
    ax.set_ylabel("Peak Pressure (kPa)", fontweight="bold")
    ax.set_title(f"{ball_id} — Velocity Response (Dry)", fontweight="bold", fontsize=9)
    ax.set_xlim(9, 36)
    ax.legend(fontsize=8)

axes[-1].axis("off")
fig3.suptitle("PRESSURE vs VELOCITY RESPONSE — Dry Condition\nSame Construction → Same k1/k2 → Pressure Scales With Mass × Velocity²",
               fontsize=15, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("Ball2Head_Figure3_Velocity_Response.png", dpi=300, bbox_inches="tight")
plt.savefig("Ball2Head_Figure3_Velocity_Response.pdf", bbox_inches="tight")
print("✅ Figure 3 — Velocity Response Curves Saved")

# ==============================================================
# 📊 FIGURE 4: SUMMARY TABLE — All Ball Types, Dry Condition @ 18 m/s (FIXED FILTERS)
# ==============================================================
fig4, ax_table = plt.subplots(figsize=(16, 10))
ax_table.axis("tight")
ax_table.axis("off")

headers = ["Ball\nType", "Size 3 (U10)\nkPa | PPSI90 ms", "Size 4 (U14)\nkPa | PPSI90 ms", "Size 5 (Elite)\nkPa | PPSI90 ms", "% Increase\nSize3→Size5"]
summary_rows = []
dry_18 = df[(df["Velocity_m_s"] == 18) & (df["Condition"] == "Dry")]

for ball_id in ball_data.keys():
    # ✅ FIXED: Proper parentheses around each filter condition
    s3 = dry_18[(dry_18["Ball_Size"] == 3) & (dry_18["Ball_Type"] == ball_id)]
    s4 = dry_18[(dry_18["Ball_Size"] == 4) & (dry_18["Ball_Type"] == ball_id)]
    s5 = dry_18[(dry_18["Ball_Size"] == 5) & (dry_18["Ball_Type"] == ball_id)]
    
    k3, t3 = s3["Peak_Pressure_kPa"].values[0], s3["PPSI90_Duration_ms"].values[0]
    k4, t4 = s4["Peak_Pressure_kPa"].values[0], s4["PPSI90_Duration_ms"].values[0]
    k5, t5 = s5["Peak_Pressure_kPa"].values[0], s5["PPSI90_Duration_ms"].values[0]
    
    pct = ((k5 - k3) / k3) * 100
    summary_rows.append([
        ball_id,
        f"{k3:.2f} | {t3:.3f}",
        f"{k4:.2f} | {t4:.3f}",
        f"{k5:.2f} | {t5:.3f}",
        f"{pct:.1f}%"
    ])

table = ax_table.table(cellText=summary_rows, colLabels=headers,
                       loc="center", cellLoc="center", colWidths=[0.10, 0.28, 0.28, 0.28, 0.12])
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 2.1)

for (r,c), cell in table.get_celld().items():
    if r == 0:
        cell.set_facecolor("#154360")
        cell.set_text_props(color="white", fontweight="bold")
    elif c == 3:
        cell.set_facecolor("#fff8e1")
    if r > 0 and c == 0:
        cell.set_text_props(fontweight="bold", color=ball_data[summary_rows[r-1][0]]["color"])

fig4.suptitle("STANDARDISED COMPARISON — All Ball Types @ 18 m/s (Dry)\n"
               "Peak-to-Peak Pressure (kPa) | PPSI90 Total Pressure Wave Duration (ms)",
               fontsize=16, fontweight="bold", y=0.98)
plt.tight_layout()
plt.savefig("Ball2Head_Figure4_Summary_Table.png", dpi=300, bbox_inches="tight")
plt.savefig("Ball2Head_Figure4_Summary_Table.pdf", bbox_inches="tight")
print("✅ Figure 4 — Summary Table Saved")

# ==============================================================
print("\n" + "="*70)
print("✅ ANALYSIS COMPLETE — Velocity-Input Only Model")
print("="*70)
print("📁 Files Created:")
print("  • Ball2Head_Standardised_Full_Dataset.csv")
print("  • Figure1 — Pressure Comparison (All Types/Sizes/Conditions)")
print("  • Figure2 — PPSI90 Duration Comparison")
print("  • Figure3 — Velocity Response Curves")
print("  • Figure4 — Summary Table @ 18 m/s")
print("\n🔬 METHODOLOGY NOTE:")
print("  Only Peak-to-Peak Pressure and PPSI90 Duration calculated.")
print("  Rise Time excluded — requires sensor sampling rate data which")
print("  is not available from computer vision or stadium tracking.")
print("  Model accepts ONLY velocity input — fully scalable in real world.")
plt.show()