import streamlit as st
import pandas as pd
import numpy as np

# ============================================================
# 📚 CALIBRATION CONSTANTS — LAB-DERIVED (PEER-REVIEWED METHOD)
# ============================================================
# Update these k₁, k₂ values once lab testing is complete
# Methodology: Linear regression — Energy(J) → kPa, Energy(J) → ms
# Reference: Stone et al. (2018); Naunheim et al. (2007); Montgomery (2019)
CALIBRATION = {
    3: {
        "name": "Size 3 (U8–U9)",
        "mass_kg": 0.32,
        "k1_kPa_per_J": 16.1,     # Energy → Peak Pressure (kPa/J)
        "k2_ms_per_J": 0.346,     # Energy → Pressure Wave Duration (ms/J)
        "note": "PLACEHOLDER — Replace with lab values"
    },
    4: {
        "name": "Size 4 (U10–U14)",
        "mass_kg": 0.37,
        "k1_kPa_per_J": 19.7,
        "k2_ms_per_J": 0.377,
        "note": "PLACEHOLDER — Replace with lab values"
    },
    5: {
        "name": "Size 5 (Adult/Elite)",
        "mass_kg": 0.43,
        "k1_kPa_per_J": 23.4,
        "k2_ms_per_J": 0.418,
        "note": "PLACEHOLDER — Replace with lab values"
    }
}

# Risk thresholds — can be updated per clinical guidance
RISK_THRESHOLDS = {
    "low_kPa": 700,
    "high_kPa": 1200
}

# ============================================================
# ⚙️ PHYSICS ENGINE — FIRST PRINCIPLES, PEER-REVIEWED
# ============================================================
def compute_kinetic_energy(velocity_m_s, mass_kg):
    """
    E = ½mv² — Newtonian kinetic energy
    Reference: Stone et al. (2018); Naunheim et al. (2003)
    """
    return 0.5 * mass_kg * np.square(velocity_m_s)

def energy_to_clinical(energy_J, k1_kPa_per_J, k2_ms_per_J):
    """
    Calibrated linear mapping from lab-derived constants
    kPa = k₁ × Energy  |  ms = k₂ × Energy
    Reference: Linear regression — Montgomery (2019); Bland & Altman (1999)
    """
    peak_kPa = energy_J * k1_kPa_per_J
    duration_ms = energy_J * k2_ms_per_J
    return peak_kPa, duration_ms

# ============================================================
# 🖥️ DASHBOARD INTERFACE
# ============================================================
st.set_page_config(
    page_title="Ball2Head — Heading Load Calibration & Monitor",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("⚽ Ball2Head — Heading Load Dashboard")
st.subheader("Lab-Calibrated • Video-Enabled • Sensor-Free Estimation")
st.markdown("---")

# --- Sidebar: Configuration & Calibration Reference ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    ball_size = st.selectbox(
        "Select Ball Size",
        options=[3, 4, 5],
        format_func=lambda x: CALIBRATION[x]["name"]
    )
    
    cfg = CALIBRATION[ball_size]
    
    st.subheader("📋 Calibration Constants")
    st.info(cfg["note"])
    st.write(f"**Ball Mass:** {cfg['mass_kg']} kg")
    st.write(f"**k₁ (kPa/J):** {cfg['k1_kPa_per_J']}")
    st.write(f"**k₂ (ms/J):** {cfg['k2_ms_per_J']}")
    
    st.subheader("📐 Risk Thresholds")
    st.write(f"🟢 < {RISK_THRESHOLDS['low_kPa']} kPa")
    st.write(f"🟡 {RISK_THRESHOLDS['low_kPa']}–{RISK_THRESHOLDS['high_kPa']} kPa")
    st.write(f"🔴 > {RISK_THRESHOLDS['high_kPa']} kPa")
    
    show_physics = st.checkbox("Show Physics & Calibration Formula")

# --- Formula Reference (Expandable) ---
if show_physics:
    with st.expander("📖 Physics & Calibration Method — Peer-Reviewed"):
        st.latex(r"""
        \begin{aligned}
        \text{Kinetic Energy} &: \quad E = \tfrac{1}{2} m v^2 \\
        \text{Peak Pressure} &: \quad P_{\text{kPa}} = k_1 \times E_J \\
        \text{Pulse Duration} &: \quad t_{\text{ms}} = k_2 \times E_J \\
        \end{aligned}
        """)
        st.markdown("""
        **Methodology Notes:**
        - **Energy**: Fundamental Newtonian mechanics — Stone et al. (2018), Naunheim et al. (2007)
        - **Calibration**: Simple linear regression — Energy vs headform pressure/duration
        - **k₁, k₂**: Derived once from lab testing; constant across all video/field use
        - **Video Input**: Optical velocity → Energy via physics → Clinical metrics via constants
        """)

# --- Main Tabs ---
tab1, tab2, tab3 = st.tabs([
    "✍️ Single Impact Test",
    "📁 Batch CSV Processing",
    "📋 Data Format Guide"
])

# ============================================================
# TAB 1 — Single Manual Calculation
# ============================================================
with tab1:
    st.subheader("Single Header Estimation")
    
    vel_input = st.number_input(
        "Ball Velocity at Impact (m/s)",
        min_value=1.0, max_value=35.0, value=15.0, step=0.5,
        help="Measured from video / optical tracking"
    )
    
    if st.button("Calculate Heading Load", type="primary"):
        energy_J = compute_kinetic_energy(vel_input, cfg["mass_kg"])
        peak_kPa, duration_ms = energy_to_clinical(
            energy_J, cfg["k1_kPa_per_J"], cfg["k2_ms_per_J"]
        )
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Impact Energy", f"{energy_J:.1f} J")
        col2.metric("Peak Pressure", f"{peak_kPa:.0f} kPa")
        col3.metric("Pulse Duration", f"{duration_ms:.2f} ms")
        
        # Risk assessment
        kpa_low = RISK_THRESHOLDS["low_kPa"]
        kpa_high = RISK_THRESHOLDS["high_kPa"]
        
        if peak_kPa > kpa_high:
            st.error(f"🔴 **HIGH EXPOSURE** — {peak_kPa:.0f} kPa. Consider monitoring cumulative load.")
        elif peak_kPa > kpa_low:
            st.warning(f"🟡 **MODERATE EXPOSURE** — {peak_kPa:.0f} kPa. Monitor frequency.")
        else:
            st.success(f"🟢 **LOW EXPOSURE** — {peak_kPa:.0f} kPa. Within typical range.")

# ============================================================
# TAB 2 — Batch CSV Processing (Full Workflow)
# ============================================================
with tab2:
    st.subheader("Batch Session Processing")
    st.markdown("""
    Upload CSV from optical tracking system. Required columns:
    - `time_s` — timestamp in seconds
    - `velocity_m_s` — ball speed at each frame
    """)
    
    uploaded_file = st.file_uploader("Upload Tracking CSV", type="csv")
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        required_cols = ["time_s", "velocity_m_s"]
        missing = [c for c in required_cols if c not in df.columns]
        
        if missing:
            st.error(f"❌ Missing required columns: {', '.join(missing)}")
        else:
            st.success(f"✅ Loaded {len(df)} data points")
            
            # Full calculation chain
            df["Energy_J"] = compute_kinetic_energy(df["velocity_m_s"], cfg["mass_kg"])
            df["Peak_kPa"] = df["Energy_J"] * cfg["k1_kPa_per_J"]
            df["Duration_ms"] = df["Energy_J"] * cfg["k2_ms_per_J"]
            
            # Summary stats
            st.subheader("📊 Session Summary")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Events", len(df))
            col2.metric("Max Energy", f"{df['Energy_J'].max():.1f} J")
            col3.metric("Max Pressure", f"{df['Peak_kPa'].max():.0f} kPa")
            
            # Results table
            st.subheader("📋 Full Results")
            display_cols = ["time_s", "velocity_m_s", "Energy_J", "Peak_kPa", "Duration_ms"]
            st.dataframe(df[display_cols], use_container_width=True)
            
            # Export
            st.download_button(
                label="📥 Download Full Results CSV",
                data=df.to_csv(index=False),
                file_name=f"ball2head_results_size{ball_size}.csv",
                mime="text/csv",
                type="primary"
            )

# ============================================================
# TAB 3 — Data Format Guide
# ============================================================
with tab3:
    st.subheader("📄 CSV Format Specification")
    st.markdown("""
    **Input CSV — Optical Tracking Output:**
    | time_s | velocity_m_s |
    |---|---|
    | 0.00 | 0.0 |
    | 0.02 | 12.3 |
    | 0.04 | 18.7 |
    
    **Output CSV — After Processing:**
    | time_s | velocity_m_s | Energy_J | Peak_kPa | Duration_ms |
    |---|---|---|---|---|
    | 0.00 | 0.0 | 0.0 | 0.0 | 0.0 |
    | 0.02 | 12.3 | 24.3 | 391 | 8.4 |
    | 0.04 | 18.7 | 55.9 | 900 | 19.3 |
    
    **Calibration Workflow — Peer-Reviewed:**
    1. **Sheet 1** — Optical velocity output from camera system
    2. **Sheet 2** — IMU/smart ball energy (lab sync)
    3. **Sheet 3** — Headform pressure & duration (ground truth)
    4. **Regression** — Energy → kPa (k₁) and Energy → ms (k₂)
    5. **Deploy** — Fixed k₁, k₂ values into this dashboard
    """)

# --- Footer ---
st.markdown("---")
st.caption("""
Ball2Head CIC • Open-Physics Framework • Lab-Calibrated Constants  
Methodology: Stone et al. (2018) • Naunheim et al. (2007) • Montgomery (2019)  
k₁, k₂ values are PLACEHOLDERS — replace with lab-derived regression results
""")