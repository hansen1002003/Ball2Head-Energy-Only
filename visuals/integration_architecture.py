import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ─── SETUP FIGURE ───
fig, ax = plt.subplots(figsize=(14, 16))
ax.set_xlim(0, 14)
ax.set_ylim(0, 20)
ax.axis('off')

# ─── COLOUR SCHEME ───
c_sensor = '#4A90D9'     # Blue — Stadium Sensors
c_api = '#27AE60'         # Green — Your API (Independent Core)
c_fusion = '#F39C12'      # Orange — Calibration & Fusion
c_dash = '#E74C3C'        # Red — Medic Dashboard
c_text = '#2c3e50'
c_arrow = '#34495E'

# ─── DRAWING FUNCTIONS ───
def draw_box(x, y, w, h, title, content, color):
    """Draw a rounded box with title and content"""
    # Box
    patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3",
                           facecolor=color, alpha=0.9, edgecolor='#1a1a1a', lw=1.5)
    ax.add_patch(patch)
    # Title
    ax.text(x + w/2, y + h - 0.4, title, ha='center', va='top',
            fontsize=11, fontweight='bold', color='white')
    # Content
    ax.text(x + 0.4, y + h - 1.0, content, ha='left', va='top',
            fontsize=9, color='white', linespacing=1.5)

def draw_arrow(x1, y1, x2, y2, label=''):
    """Draw connecting arrow with optional label"""
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', lw=2.5, color=c_arrow))
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx + 0.2, my, label, fontsize=9, ha='left', va='center',
                bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='none', alpha=0.85))

# ─── TITLE ───
ax.text(7, 19.5, "BALL2HEAD — COMPLETE SYSTEM ARCHITECTURE",
        ha='center', va='center', fontsize=18, fontweight='bold', color=c_text)
ax.text(7, 19.0, "Independent Physics Core → Calibration Fusion → Medic Dashboard",
        ha='center', va='center', fontsize=11, style='italic', color='#7f8c8d')

# ═══════════════════════════════════════════════════════════════════════
# LEVEL 1: STADIUM DATA SOURCES
# ═══════════════════════════════════════════════════════════════════════
draw_box(0.5, 16.0, 5.8, 2.2,
         "🔵 SMART BALL SENSOR",
         "• timestamp (universal sync key)\n• ax, ay, az (500Hz IMU)\n• Raw acceleration data",
         c_sensor)

draw_box(7.7, 16.0, 5.8, 2.2,
         "🔵 OPTICAL CAMERA / UWB",
         "• timestamp (SYNCED with ball)\n• Player ID / Team ID\n• Position & Event Type",
         c_sensor)

# ═══════════════════════════════════════════════════════════════════════
# LEVEL 2: YOUR API — PHYSICS CORE
# ═══════════════════════════════════════════════════════════════════════
draw_box(2.0, 12.0, 10.0, 3.0,
         "🟢 BALL2HEAD API — PHYSICS CORE ✅ INDEPENDENT",
         "📥 INPUT:  timestamp, ax, ay, az\n⚙️ PROCESS: Pure Newtonian Mechanics\n   a_total = √(ax²+ay²+az²)\n   Δv = a × Δt\n   Energy = ½ × m × (Δv)²\n📤 OUTPUT: timestamp, energy_J\n\n🔒 NO player data · NO assumptions · AUDITABLE",
         c_api)

# ═══════════════════════════════════════════════════════════════════════
# LEVEL 3: CALIBRATION & DATA FUSION
# ═══════════════════════════════════════════════════════════════════════
draw_box(2.0, 7.5, 10.0, 3.5,
         "🟠 CALIBRATION & DATA FUSION — THEIR SIDE",
         "🔗 MATCH by TIMESTAMP ← Universal Key\n\n📐 CONVERT ENERGY → CLINICAL UNITS\n   Peak Pressure (kPa)  = energy_J × k₁\n   Wave Duration (ms)   = energy_J × k₂\n   (k₁, k₂ = Lab-calibrated constants)\n\n🧩 JOIN DATA:\n   + Player ID + Team ID + Event Details\n   → Filter access by team / role",
         c_fusion)

# ═══════════════════════════════════════════════════════════════════════
# LEVEL 4: MEDIC DASHBOARD
# ═══════════════════════════════════════════════════════════════════════
draw_box(2.0, 2.0, 10.0, 4.5,
         "🔴 MEDIC DASHBOARD — ROLE-BASED ACCESS",
         "┌─────────────────────────────────────────────────┐\n│ TIME  │ PLAYER │ ENERGY │ PRESSURE │ DURATION │ STATUS │\n├─────────────────────────────────────────────────┤\n│ 14:32 │ #7 H   │ 24.6 J │ 578 kPa  │ 10.3 ms  │ 🟡 WARN│\n│ 15:05 │ #12 A  │ 32.1 J │ 754 kPa  │ 14.1 ms  │ 🔴 REV│\n└─────────────────────────────────────────────────┘\n\n🟢 SAFE <15J  │  🟡 WARNING 15–30J  │  🔴 CRITICAL >30J\n\n🔒 Team A sees ONLY Team A players\n📋 Full audit trail: Energy × k = Result",
         c_dash)

# ═══════════════════════════════════════════════════════════════════════
# CONNECTING ARROWS
# ═══════════════════════════════════════════════════════════════════════
draw_arrow(3.4, 16.0, 7.0, 15.2, "Input: timestamp + accel")
draw_arrow(10.6, 16.0, 7.0, 15.2, "Timestamp Sync")
draw_arrow(7.0, 15.0, 7.0, 15.0)  # align
draw_arrow(7.0, 14.8, 7.0, 12.5, "")

draw_arrow(7.0, 12.0, 7.0, 11.0, "Output: timestamp + energy_J")
draw_arrow(7.0, 11.0, 7.0, 7.5, "Apply k₁, k₂ + Player Data")
draw_arrow(7.0, 7.5, 7.0, 6.5, "")
draw_arrow(7.0, 6.0, 7.0, 2.0, "Display & Threshold Check")

# ═══════════════════════════════════════════════════════════════════════
# LEGEND
# ═══════════════════════════════════════════════════════════════════════
ax.text(0.8, 0.5, "🔵 Sensors", fontsize=10, color=c_sensor, fontweight='bold')
ax.text(3.0, 0.5, "🟢 Physics Core", fontsize=10, color=c_api, fontweight='bold')
ax.text(5.8, 0.5, "🟠 Calibration/Fusion", fontsize=10, color=c_fusion, fontweight='bold')
ax.text(9.0, 0.5, "🔴 Dashboard/UI", fontsize=10, color=c_dash, fontweight='bold')

plt.tight_layout()
plt.savefig('Ball2Head_Complete_Architecture.png', dpi=180, bbox_inches='tight', facecolor='white')
print("✅ Diagram saved as: Ball2Head_Complete_Architecture.png")
plt.show()