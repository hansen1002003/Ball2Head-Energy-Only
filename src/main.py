# ============================================================
# 🏆 BALL2HEAD — Heading Load Calculation Dashboard
# Calibration based on Phillips et al. (2026)
# Pressure Wave Propagation from Association Football Head Collisions
# ============================================================
# Author: Hansen Sominabo Kekom
# Institution: Birmingham Newman University
# GitHub: https://github.com/hansen1002003/Ball2Head-Energy-Only
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np

# ============================================================
# ⚙️ PAGE CONFIG — Kept identical for deployed compatibility
# ============================================================
st.set_page_config(
    page_title="Ball2Head — Heading Load Calculator",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 📚 CALIBRATION CONSTANTS — Derived from Phillips et al. (2026)
# ============================================================
# k₁ = Peak Pressure (kPa) per Joule
# k₂ = Pressure Wave Duration (ms) per Joule
# Source: Size 5 = mean response across modern synthetic balls
# Size 3/4 = scaled from FIFA regulation mass ratios

CALIBRATION = {
    3: {  # U8–U10
        "name": "Size 3 (U8–U10)",
        "mass_kg": 0.320,
        "k1_kPa_per_J": 1.37,
        "k2_ms_per_J": 0.073
    },
    4: {  # U12–U14
        "name": "Size 4 (U12–U14)",
        "mass_kg": 0.370,
        "k1_kPa_per_J": 1.28,
        "k2_ms_per_J": 0.070
    },
    5: {  # U16–Elite — FIFA standard
        "name": "Size 5 (U16–Elite)",
        "mass_kg": 0.430,
        "k1_kPa_per_J": 1.19,
        "k2_ms_per_J": 0.067
    }
}

# ============================================================
# 🌧️ BALL CONDITION / WET FACTORS — Phillips et al. (2026), p.9
# Combines measured water uptake (Table 1) + pressure amplification
# ============================================================
CONDITION_FACTORS = {
    "Dry — Standard (FIFA regulation)": {
        "factor": 1.00,
        "description": "Baseline — no adjustment"
    },
    "Damp — Morning dew / light drizzle": {
        "factor": 1.10,
        "description": "+~5–10% — minimal water absorption"
    },
    "Wet — Rain (modern synthetic ball)": {
        "factor": 1.25,
        "description": "+~25% — coated ball, moderate water uptake"
    },
    "Wet — Heavy rain / older leather ball": {
        "factor": 1.55,
        "description": "+~55% — significant water + material effect"
    }
}

# ============================================================
# 🎨 HEADER & INTRODUCTION
# ============================================================
st.title("⚽ Ball2Head — Heading Load Calculator")
st.markdown("""
> **Estimates peak intracranial pressure and pressure wave duration from ball velocity at impact.**  
> Calibrated against *Phillips et al. (2026) — Pressure Wave Propagation from Association Football Head Collisions*.  
> Values are standardised baseline estimates — individual ball behaviour may vary.
""")
st.divider()

# ============================================================
# 📥 INPUT SECTION
# ============================================================
st.subheader("📋 Input Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    ball_size = st.selectbox(
        "Ball Size / Age Group",
        options=[3, 4, 5],
        format_func=lambda x: CALIBRATION[x]["name"],
        index=2,  # Default = Size 5
        help="FIFA regulation match ball size — determines mass and calibration constants."
    )

with col2:
    velocity_kmh = st.number_input(
        "Ball Velocity at Impact (km/h)",
        min_value=1.0,
        max_value=150.0,
        value=18.0,
        step=1.0,
        help="Inbound ball speed immediately prior to head contact. Convert m/s → km/h: ×3.6"
    )

with col3:
    condition_label = st.selectbox(
        "Ball / Pitch Condition",
        options=list(CONDITION_FACTORS.keys()),
        index=0,  # Default = Dry — NO CHANGE to existing behaviour!
        help="""
        Adjustment for wet conditions. Phillips et al. (2026) measured up to 317% 
        higher peak pressure in wet leather balls due to increased mass and 
        altered material stiffness.
        """
    )

# Convert units
velocity_mps = velocity_kmh / 3.6  # m/s — physics calculation

# Get calibration values
m = CALIBRATION[ball_size]["mass_kg"]
k1 = CALIBRATION[ball_size]["k1_kPa_per_J"]
k2 = CALIBRATION[ball_size]["k2_ms_per_J"]
wet_factor = CONDITION_FACTORS[condition_label]["factor"]

# ============================================================
# 🧮 CALCULATION — Physics Layer
# ============================================================
# Kinetic Energy: E = ½ m v²
dry_energy_joules = 0.5 * m * (velocity_mps ** 2)

# Baseline Dry values (for transparency)
dry_kpa = dry_energy_joules * k1
dry_ms = dry_energy_joules * k2

# Apply condition factor → Final adjusted values
adjusted_energy = dry_energy_joules * wet_factor
adjusted_kpa = dry_kpa * wet_factor
adjusted_ms = dry_ms * wet_factor

# ============================================================
# 📊 DISPLAY RESULTS
# ============================================================
st.divider()
st.subheader("📊 Calculated Heading Load")

# Show condition factor notice if wet
if wet_factor > 1.00:
    st.info(f"""
    💡 **Wet condition adjustment applied: ×{wet_factor:.2f}**  
    Baseline (Dry) values: **{dry_kpa:.1f} kPa** | **{dry_ms:.2f} ms**  
    Adjusted for {condition_label.split(" — ")[0].lower()}: **+{((wet_factor-1)*100):.0f}%**  
    *(Phillips et al., 2026 — up to 317% pressure increase measured in wet conditions)*
    """)
else:
    st.success("✅ Using dry regulation ball baseline (FIFA standard) — no wet adjustment applied")

# Main metrics — side by side
col_a, col_b, col_c = st.columns(3)
with col_a:
    st.metric("⚡ Kinetic Energy", f"{adjusted_energy:.1f} J")
with col_b:
    st.metric("🧠 Peak Pressure", f"{adjusted_kpa:.1f} kPa")
with col_c:
    st.metric("📐 Wave Duration", f"{adjusted_ms:.2f} ms")

# Detailed breakdown table
with st.expander("📋 View Full Calculation Details"):
    detail_df = pd.DataFrame([
        {"Parameter": "Ball Size", "Value": CALIBRATION[ball_size]["name"], "Note": f"Mass = {m*1000:.0f} g (FIFA standard)"},
        {"Parameter": "Inbound Velocity", "Value": f"{velocity_kmh:.1f} km/h ({velocity_mps:.1f} m/s)", "Note": "Measured pre-impact speed"},
        {"Parameter": "Ball Condition", "Value": condition_label, "Note": f"Factor applied: ×{wet_factor:.2f}"},
        {"Parameter": "Baseline Energy (Dry)", "Value": f"{dry_energy_joules:.1f} J", "Note": "E = ½mv²"},
        {"Parameter": "Calibration k₁", "Value": f"{k1:.2f} kPa/J", "Note": "From Phillips et al. (2026)"},
        {"Parameter": "Calibration k₂", "Value": f"{k2:.3f} ms/J", "Note": "From PPSI₉₀ Time data"},
        {"Parameter": "Baseline Pressure (Dry)", "Value": f"{dry_kpa:.1f} kPa", "Note": "Before wet adjustment"},
        {"Parameter": "Baseline Duration (Dry)", "Value": f"{dry_ms:.2f} ms", "Note": "Before wet adjustment"},
        {"Parameter": "---", "Value": "---", "Note": "---"},
        {"Parameter": "✅ Final Energy", "Value": f"{adjusted_energy:.1f} J", "Note": "Adjusted for condition"},
        {"Parameter": "✅ Final Peak Pressure", "Value": f"{adjusted_kpa:.1f} kPa", "Note": "Adjusted for condition"},
        {"Parameter": "✅ Final Wave Duration", "Value": f"{adjusted_ms:.2f} ms", "Note": "Adjusted for condition"},
    ])
    st.dataframe(detail_df, hide_index=True, use_container_width=True)

# ============================================================
# 📤 EXPORT SECTION
# ============================================================
st.divider()
st.subheader("📥 Export Result")

export_df = pd.DataFrame({
    "Timestamp": [pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")],
    "Ball_Size": [CALIBRATION[ball_size]["name"]],
    "Velocity_kmh": [round(velocity_kmh, 1)],
    "Condition": [condition_label],
    "Condition_Factor": [round(wet_factor, 2)],
    "Baseline_Dry_Energy_J": [round(dry_energy_joules, 1)],
    "Baseline_Dry_Pressure_kPa": [round(dry_kpa, 1)],
    "Baseline_Dry_Duration_ms": [round(dry_ms, 2)],
    "Adjusted_Energy_J": [round(adjusted_energy, 1)],
    "Adjusted_Pressure_kPa": [round(adjusted_kpa, 1)],
    "Adjusted_Duration_ms": [round(adjusted_ms, 2)],
    "Calibration_k1_kPa_per_J": [round(k1, 2)],
    "Calibration_k2_ms_per_J": [round(k2, 3)],
    "Source": ["Phillips et al. (2026) — Ball2Head Framework"]
})

csv = export_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📄 Download Result as CSV",
    data=csv,
    file_name=f"ball2head_result_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
    mime="text/csv",
    type="primary"
)

# ============================================================
# 📚 METHODOLOGY & REFERENCES
# ============================================================
st.divider()
with st.expander("📖 Methodology & References"):
    st.markdown("""
    ### Methodology
    1. **Kinetic Energy**: $E_k = \\frac{1}{2}mv^2$ — fundamental Newtonian physics.  
       $m$ = regulation ball mass (FIFA standard); $v$ = inbound velocity at impact.
    2. **Pressure Calibration**: $P_{peak} = k_1 \\times E_k$ — derived from peak-to-peak 
       intracranial pressure measurements in surrogate head model (Phillips et al., 2026).
    3. **Wave Duration**: $t_{wave} = k_2 \\times E_k$ — derived from PPSI$_{90}$ Time, 
       the interval over which 90% of signal energy is transferred.
    4. **Wet Condition Adjustment**: Accounts for both increased mass from water 
       absorption (+2.2% to +59.9% measured) and altered material stiffness causing 
       up to 317% higher peak pressure in wet conditions. Factors are conservative 
       estimates based on published experimental data.

    ### Reference
    > Phillips, I., Mitchell, S., Lepper, P. & Harland, A. (2026).  
    > *Pressure wave propagation from association football head collisions.*  
    > **Proceedings of the Institution of Mechanical Engineers, Part P: Journal of Sports Engineering and Technology.**

    ### Important Notes
    - Values are **estimates** based on a standard regulation match ball.
    - Individual ball material, construction, and condition may cause ±50% variation.
    - Wet condition adjustments are evidence-based estimates — actual values may vary.
    - Not for clinical diagnosis — intended for exposure monitoring and comparative tracking.
    """)

# ============================================================
# 🦶 FOOTER
# ============================================================
st.markdown("""
---
<div style="text-align: center; color: #666; font-size: 0.9em;">
    <strong>Ball2Head</strong> — Independent Heading Load Monitoring Framework<br>
    Based on peer-reviewed research. For educational & clinical use.<br>
    GitHub: <a href="https://github.com/hansen1002003/Ball2Head-Energy-Only" target="_blank">hansen1002003/Ball2Head-Energy-Only</a>
</div>
""", unsafe_allow_html=True)