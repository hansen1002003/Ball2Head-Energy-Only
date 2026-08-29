import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# ==========================================
# CLEAN ACADEMIC STYLE
# ==========================================
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica"],
    "font.size": 10,
    "axes.linewidth": 0,
})

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def draw_box(ax, x, y, w, h, text, facecolor="#f0f4f8", edgecolor="#2c3e50", bold=False):
    box = FancyBboxPatch((x, y), w, h,
                          boxstyle="round,pad=0.15",
                          facecolor=facecolor,
                          edgecolor=edgecolor,
                          linewidth=1.5)
    ax.add_patch(box)
    weight = "bold" if bold else "normal"
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontweight=weight, wrap=True)

def draw_arrow_down(ax, x_center, y_from, y_to):
    """Draw a straight DOWN arrow connecting boxes properly"""
    arrow = FancyArrowPatch((x_center, y_from), (x_center, y_to),
                            arrowstyle="->,head_width=0.25,head_length=0.35",
                            lw=1.8, color="#34495e", mutation_scale=12)
    ax.add_patch(arrow)

# ==========================================
# FIGURE 1: TWO-LAYER ARCHITECTURE — FIXED ARROWS
# ==========================================
fig1, ax1 = plt.subplots(figsize=(8, 10))
ax1.set_xlim(0, 10)
ax1.set_ylim(0, 11)
ax1.axis("off")

# Title
ax1.text(5, 10.6, "Ball2Head — Two-Layer Architecture", ha="center", fontsize=14, fontweight="bold")

# X center for all boxes — perfectly aligned
CX = 5

# 1. Input
draw_box(ax1, 1.5, 9.3, 7, 0.7,
         "📡 Smart Ball IMU Input\n$a_x$, $a_y$, $a_z$ (m/s²)",
         facecolor="#e8f4f8", edgecolor="#2980b9")

# 2. Layer A — Pure Physics
draw_box(ax1, 1.0, 7.2, 8, 1.6,
         "🔬 LAYER A — PURE PHYSICS (Analytical Core)\n"
         "• Total Acceleration: $a_{total} = \\sqrt{a_x^2 + a_y^2 + a_z^2}$\n"
         "• Velocity Change: $\\Delta v = a_{total} \\cdot \\Delta t$\n"
         "• Impact Energy: $E = \\frac{1}{2} m (\\Delta v)^2$",
         facecolor="#d4edda", edgecolor="#28a745", bold=True)
ax1.text(9.2, 8.0, "Analytical\nFoundation", fontsize=9, color="#28a745", ha="center")

# 3. Physics-Only Result
draw_box(ax1, 1.8, 6.0, 6.4, 0.6,
         "Physics-Only Result $E_{physics}$ (J)",
         facecolor="#fff3cd", edgecolor="#ffc107")

# 4. Layer B — AI Refinement
draw_box(ax1, 1.0, 4.0, 8, 1.5,
         "🤖 LAYER B — AI REFINEMENT (Optional Correction)\n"
         "• Scaling & Normalisation\n"
         "• Model Prediction → $E_{model}$\n"
         "• ✅ PHYSICAL VALIDATION CHECK (Reject Impossible Values)",
         facecolor="#e2e3ff", edgecolor="#6f42c1", bold=True)
ax1.text(9.2, 4.75, "Optional\nRefinement", fontsize=9, color="#6f42c1", ha="center")

# 5. Final Result
draw_box(ax1, 1.8, 2.8, 6.4, 0.6,
         "✅ Final Validated Energy $E_{final}$",
         facecolor="#d1e7dd", edgecolor="#198754")

# 6. Audit Log
draw_box(ax1, 1.0, 1.5, 8, 0.6,
         "📄 CSV Audit Log: SAVE BOTH → $E_{physics}$ AND $E_{final}$",
         facecolor="#f8f9fa", edgecolor="#6c757d")

# ==========================================
# ✅ FIXED ARROWS — Now TOUCHING each box properly
# ==========================================
draw_arrow_down(ax1, CX, 9.3, 8.8)     # Input → Layer A
draw_arrow_down(ax1, CX, 7.2, 6.6)     # Layer A → Physics Result
draw_arrow_down(ax1, CX, 6.0, 5.5)     # Physics Result → Layer B
draw_arrow_down(ax1, CX, 4.0, 3.4)     # Layer B → Final Result
draw_arrow_down(ax1, CX, 2.8, 2.1)     # Final → Audit Log

plt.tight_layout()
plt.savefig("architecture_diagram.png", dpi=300, bbox_inches="tight")
print("✅ Saved: architecture_diagram.png — Arrows Fixed!")

# ==========================================
# FIGURE 2: SAFETY DECISION FLOW
# ==========================================
fig2, ax2 = plt.subplots(figsize=(8, 9))
ax2.set_xlim(0, 10)
ax2.set_ylim(0, 10)
ax2.axis("off")

ax2.text(5, 9.5, "Safety Validation — Decision Logic", ha="center", fontsize=14, fontweight="bold")

# Model Output
draw_box(ax2, 3.0, 8.2, 4, 0.7, "📥 Model Output $E_{model}$", facecolor="#e2e3ff", edgecolor="#6f42c1")

# Conditions
cond_text = """❓ TWO CONDITIONS:
1. $E_{model} > 0$  (Energy is Positive)
2. $|E_{model} - E_{physics}| < 1.5 \\times E_{physics}$
(Within Physically Reasonable Range)"""
draw_box(ax2, 1.5, 6.0, 7, 1.5, cond_text, facecolor="#fff3cd", edgecolor="#d4a017")

# Branches
draw_box(ax2, 0.5, 3.5, 3.5, 0.8, "✅ YES → Use $E_{model}$", facecolor="#d4edda", edgecolor="#28a745")
draw_box(ax2, 6.0, 3.5, 3.5, 0.8, "❌ NO → Fallback to $E_{physics}$", facecolor="#f8d7da", edgecolor="#dc3545")

# Arrows
draw_arrow_down(ax2, 5, 8.2, 7.5)
draw_arrow_down(ax2, 3, 6.0, 4.3)
draw_arrow_down(ax2, 7, 6.0, 4.3)

# Final
draw_box(ax2, 2.5, 1.5, 5, 0.7, "🔒 ALWAYS Trust Physics When In Doubt", facecolor="#f8f9fa", edgecolor="#2c3e50")
draw_arrow_down(ax2, 3, 3.5, 2.2)
draw_arrow_down(ax2, 7, 3.5, 2.2)

# Explanation
note_text = """💡 Why this is ANALYTICAL:
Not "magic" — it is a MATHEMATICAL GUARD CONDITION
that defines what counts as a PHYSICALLY VALID answer.
Model is ONLY trusted when it respects the laws of physics."""
ax2.text(5, 0.5, note_text, ha="center", fontsize=9, style="italic", color="#444444")

plt.tight_layout()
plt.savefig("safety_decision_flow.png", dpi=300, bbox_inches="tight")
print("✅ Saved: safety_decision_flow.png")

plt.show()
print("\n🎉 Both diagrams generated — Arrows Fixed!")