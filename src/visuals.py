import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Set clean, professional medical-dashboard styling
sns.set_theme(style="whitegrid")
plt.rcParams.update(
    {
        "font.size": 11,
        "axes.labelsize": 12,
        "axes.titlesize": 14,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "figure.titlesize": 16,
    }
)

# 1. GENERATE SIMULATED EXPERT CALIBRATED DATA (Based on Dr. Phillips' framework)
np.random.seed(42)
timestamps = np.sort(np.random.randint(1, 95, size=14))  # 14 headers in a match
kinetic_energy = np.random.uniform(15, 45, size=14)  # Joules (J)

# Calculate kPa and ms using non-linear scaling normalized by Joules
kpa_per_j = np.random.uniform(0.6, 1.2, size=14)  # kPa/J baseline
ms_per_j = np.random.uniform(2.0, 3.5, size=14)  # ms/J baseline

kpa = kpa_per_j * kinetic_energy
duration_ms = (ms_per_j * kinetic_energy) / 1000  # Convert microsecond scale to ms

df = pd.DataFrame(
    {
        "Minute": timestamps,
        "Kinetic_Energy_J": kinetic_energy,
        "kPa_per_J": kpa_per_j,
        "ms_per_J": ms_per_j,
        "Total_kPa": kpa,
        "Duration_ms": duration_ms,
    }
)

# 2. INITIALIZE DASHBOARD LAYOUT (2x2 Grid)
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle(
    "POST-MATCH HEADLOAD BRAIN BIOMECHANICS REPORT\nPlayer ID: PL_8832 | Match Date: 11-09-2026",
    weight="bold",
    y=0.98,
)

# ------------------------------------------------------------------
# PLOT 1: ACUTE SPONTANEOUS IMPACT RISK TIERING (Top Left)
# ------------------------------------------------------------------
ax1 = axes[0, 0]
# Clinical Thresholds
ax1.axhspan(0, 20, color="#2ecc71", alpha=0.15, label="Low Risk Zone")
ax1.axhspan(20, 35, color="#f1c40f", alpha=0.15, label="Moderate Exposure")
ax1.axhspan(35, 55, color="#e74c3c", alpha=0.15, label="High Acoustic Load Trigger")

scatter = ax1.scatter(
    df["Minute"],
    df["Total_kPa"],
    s=df["Kinetic_Energy_J"] * 6,
    c=df["kPa_per_J"],
    cmap="YlOrRd",
    edgecolors="black",
    alpha=0.9,
    zorder=3,
)
ax1.set_title("Individual Heading Events: Internal Peak Pressure (kPa)", weight="bold")
ax1.set_xlabel("Match Timeline (Minutes)")
ax1.set_ylabel("Peak Internal Pressure (kPa)")
ax1.set_xlim(0, 95)
ax1.set_ylim(0, 55)
# Annotate the highest peak risk header for the doctor
max_idx = df["Total_kPa"].idxmax()
ax1.annotate(
    f"High Transfer Event\n({df.loc[max_idx, 'Total_kPa']:.1f} kPa)",
    xy=(df.loc[max_idx, "Minute"], df.loc[max_idx, "Total_kPa"]),
    xytext=(df.loc[max_idx, "Minute"] - 18, df.loc[max_idx, "Total_kPa"] - 8),
    arrowprops=dict(facecolor="black", shrink=0.08, width=1, headwidth=6),
    weight="bold",
    bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.5),
)
cbar = fig.colorbar(scatter, ax=ax1, orientation="vertical", pad=0.02)
cbar.set_label("Energy Transfer Efficiency (kPa / Joule)")

# ------------------------------------------------------------------
# PLOT 2: CUMULATIVE DOSAGE CURVE OVER 90 MINS (Top Right)
# ------------------------------------------------------------------
ax2 = axes[0, 1]
df["Cumulative_kPa"] = df["Total_kPa"].cumsum()

ax2.plot(
    df["Minute"],
    df["Cumulative_kPa"],
    color="#2c3e50",
    linewidth=3,
    marker="o",
    markersize=6,
    label="Cumulative Internal Strain",
    zorder=3,
)
# Historical team baseline shaded reference zone
ax2.fill_between(
    df["Minute"],
    df["Cumulative_kPa"] * 0.8,
    df["Cumulative_kPa"] * 1.2,
    color="#7f8c8d",
    alpha=0.1,
    label="Player Rolling Season Baseline",
)

ax2.set_title(
    "Cumulative Sub-Concussive Micro-Trauma Progression", weight="bold"
)
ax2.set_xlabel("Match Timeline (Minutes)")
ax2.set_ylabel("Total Cumulative Pressure (kPa)")
ax2.set_xlim(0, 95)
ax2.legend(loc="upper left")

# ------------------------------------------------------------------
# PLOT 3: PRESSURE VS TIME-DOMAIN EFFICIENCY MATRIX (Bottom Left)
# ------------------------------------------------------------------
ax3 = axes[1, 0]
# Normalised metrics comparison to highlight severe stiffness/wetness spikes
sns.regplot(
    x="Duration_ms",
    y="Total_kPa",
    data=df,
    ax=ax3,
    scatter_kws={"s": 80, "color": "#8e44ad", "edgecolor": "black", "alpha": 0.8},
    line_kws={"color": "#34495e", "linestyle": "--", "linewidth": 1.5},
)
ax3.set_title(
    "Acoustic Wave Characteristic Mapping (kPa vs. Duration)", weight="bold"
)
ax3.set_xlabel("Wave Duration Threshold (ms)")
ax3.set_ylabel("Internal Transferred Pressure (kPa)")

# ------------------------------------------------------------------
# PLOT 4: BALL MATERIAL CORRELATION CHECKSUM (Bottom Right)
# ------------------------------------------------------------------
ax4 = axes[1, 1]
# Showing normalized energy metrics per event to isolate abnormal spikes
x_axis = np.arange(len(df))
ax4.bar(
    x_axis - 0.2,
    df["kPa_per_J"],
    width=0.4,
    label="Pressure Load Index (kPa/J)",
    color="#16a085",
    alpha=0.85,
)
ax4.bar(
    x_axis + 0.2,
    df["ms_per_J"],
    width=0.4,
    label="Duration Index (ms/J)",
    color="#d35400",
    alpha=0.85,
)

ax4.set_title("Normalized Ball Energy Structural Efficiency", weight="bold")
ax4.set_xlabel("Header Event Sequence Number")
ax4.set_ylabel("Index Ratio (Metric / Joule Input)")
ax4.set_xticks(x_axis)
ax4.set_xticklabels(x_axis + 1)
ax4.legend(loc="upper right")

# Final Layout adjustments and display execution
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.show()
