import streamlit as st
import pandas as pd
import numpy as np

# --------------------------
# 📚 PRE-CALIBRATED CONSTANTS — FROM YOUR LAB WORK
# --------------------------
CALIBRATION = {
    3: {"mass": 0.32, "k1": 16.1, "k2": 0.346},   # Size 3
    4: {"mass": 0.37, "k1": 19.7, "k2": 0.377},   # Size 4
    5: {"mass": 0.43, "k1": 23.4, "k2": 0.418}    # Size 5
}

# --------------------------
# ⚙️ BALL2HEAD PHYSICS ENGINE
# --------------------------
def compute_energy(vel, mass):
    return 0.5 * mass * (vel ** 2)

def compute_clinical(energy, k1, k2):
    return energy * k1, energy * k2

# --------------------------
# 🖥️ DASHBOARD START
# --------------------------
st.set_page_config(page_title="Ball2Head — Grassroots Load Monitor", layout="wide")
st.title("⚽ Ball2Head — Heading Load Dashboard")
st.subheader("Lab-Calibrated • Video-Ready • No Field Sensors Needed")

# --- Sidebar: Settings ---
with st.sidebar:
    st.header("⚙️ Configuration")
    ball_size = st.selectbox("Select Ball Size", [3,4,5], format_func=lambda x: f"Size {x}")
    st.info("✅ Constants loaded from lab calibration.")
    show_debug = st.checkbox("Show Physics/Calibration Details")

# Load constants
mass = CALIBRATION[ball_size]["mass"]
k1 = CALIBRATION[ball_size]["k1"]
k2 = CALIBRATION[ball_size]["k2"]

if show_debug:
    st.code(f"""
    Ball Size: {ball_size}
    Mass: {mass} kg
    k₁ (kPa/J): {k1}
    k₂ (ms/J): {k2}
    """)

# --- Input Mode Selection ---
tab1, tab2 = st.tabs(["✍️ Single Header Test", "📁 Batch Session Upload"])

# --- Tab 1: Manual ---
with tab1:
    vel_input = st.number_input("Enter Ball Velocity (m/s)", min_value=1.0, max_value=35.0, value=15.0)
    if st.button("Calculate Load"):
        energy = compute_energy(vel_input, mass)
        kPa, ms = compute_clinical(energy, k1, k2)
        col1, col2, col3 = st.columns(3)
        col1.metric("Impact Energy", f"{energy:.1f} J")
        col2.metric("Peak Pressure", f"{kPa:.0f} kPa")
        col3.metric("Pulse Duration", f"{ms:.2f} ms")
        # Risk logic
        if kPa > 1200: st.error("🔴 HIGH RISK — Caution Required")
        elif kPa > 700: st.warning("🟡 MODERATE RISK — Monitor Exposure")
        else: st.success("🟢 LOW RISK — Normal Play")

# --- Tab 2: Batch CSV Upload ---
with tab2:
    uploaded_file = st.file_uploader("Upload Camera Tracking CSV", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        if "velocity_m_s" not in df.columns:
            st.error("CSV must have column: velocity_m_s")
        else:
            st.success(f"Loaded {len(df)} samples")
            # Compute full chain
            df["Energy_J"] = compute_energy(df["velocity_m_s"], mass)
            df["Peak_kPa"] = df["Energy_J"] * k1
            df["Duration_ms"] = df["Energy_J"] * k2
            # Show
            st.dataframe(df[["time_s", "velocity_m_s", "Energy_J", "Peak_kPa", "Duration_ms"]])
            # Export
            st.download_button("📥 Download Results CSV", df.to_csv(index=False), file_name="ball2head_results.csv")

st.markdown("---")
st.caption("Ball2Head CIC — Physics Core Validated • Lab Calibrated • FA/Inquiry Ready")