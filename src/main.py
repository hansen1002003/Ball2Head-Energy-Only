"""
Ball2Head — Heading Load Calculator
====================================
Calibration: Phillips et al. (2026) — A1/B1 Mean — FIFA 430g
Author: Hansen Sominabo Kekom
Version: 1.0 — Streamlit Only (Cloud-Ready)
"""

import streamlit as st
import pandas as pd
import numpy as np

# =============================================================================
# CALIBRATION — PURE PHILLIPS ET AL. (2026)
# =============================================================================
class Calibration:
    """Elite Standard — A1/B1 Mean, FIFA 430g"""
    BALL_MASS_DRY_KG = 0.430
    
    DRY_k1_KPA_PER_J = 1.19
    DRY_k2_MS_PER_J = 0.067
    
    WET_FACTORS = {
        "dry": 1.00,
        "damp": 1.10,
        "wet_synthetic": 1.25
    }
    
    @classmethod
    def get_factors(cls, condition: str):
        cond = condition.lower().strip()
        factor = cls.WET_FACTORS.get(cond, 1.00)
        return {
            "k1_kpa_j": round(cls.DRY_k1_KPA_PER_J * factor, 4),
            "k2_ms_j": round(cls.DRY_k2_MS_PER_J * factor, 5),
            "wet_factor": factor
        }

# =============================================================================
# CORE CALCULATION ENGINE
# =============================================================================
def calculate_metrics(velocity_mps: float, condition: str = "dry"):
    if velocity_mps <= 0:
        raise ValueError("Velocity must be greater than 0")
    
    energy_j = 0.5 * Calibration.BALL_MASS_DRY_KG * (velocity_mps ** 2)
    
    dry_k1 = Calibration.DRY_k1_KPA_PER_J
    dry_k2 = Calibration.DRY_k2_MS_PER_J
    factors = Calibration.get_factors(condition)
    
    baseline_kpa = round(dry_k1 * energy_j, 2)
    baseline_ms = round(dry_k2 * energy_j, 3)
    
    adjusted_kpa = round(factors["k1_kpa_j"] * energy_j, 2)
    adjusted_ms = round(factors["k2_ms_j"] * energy_j, 3)
    
    if adjusted_kpa < 30:
        category = "LOW"
    elif adjusted_kpa < 60:
        category = "MODERATE"
    elif adjusted_kpa < 90:
        category = "HIGH"
    else:
        category = "EXTREME"
    
    return {
        "ball_velocity_mps": round(velocity_mps, 2),
        "condition": condition,
        "kinetic_energy_j": round(energy_j, 2),
        "baseline_dry_kpa": baseline_kpa,
        "baseline_dry_wave_duration_ms": baseline_ms,
        "adjusted_kpa": adjusted_kpa,
        "adjusted_wave_duration_ms": adjusted_ms,
        "wet_factor_applied": factors["wet_factor"],
        "load_category": category,
        "calibration_used": "A1/B1 Mean — FIFA 430g — Phillips et al. (2026)"
    }

# =============================================================================
# STREAMLIT INTERFACE
# =============================================================================
def run_streamlit():
    st.set_page_config(page_title="Ball2Head — Heading Load", layout="wide")
    st.title("⚽ Ball2Head — Heading Load Metrics")
    st.subheader("Calibrated from Phillips et al. (2026) — Elite Size 5 Standard")
    
    with st.expander("📋 Methodology & Calibration Source"):
        st.markdown("""
        **Calibration Source:** Mean of A1 (Thermally Bonded) & B1 (Fuse-Welded) elite match balls, 
        standardised to FIFA regulation 430 g dry mass.
        
        **Formula:**
        - Kinetic Energy: $E = \\frac{1}{2}mv^2$
        - Peak Pressure: $P = k_1 \\times E$  → **k₁ = 1.19 kPa/J (dry)**
        - Wave Duration: $t = k_2 \\times E$  → **k₂ = 0.067 ms/J (dry)**
        
        **Wet Conditions:** Damp ×1.10 | Wet Synthetic ×1.25
        **Reference:** Phillips, I. et al. (2026) — Pressure wave propagation
        """)
    
    # Single Calculation
    st.header("🎯 Single Calculation")
    col1, col2 = st.columns(2)
    with col1:
        velocity = st.number_input("Ball Velocity at Impact (m/s)", 
                                   min_value=5.0, max_value=35.0, value=18.0, step=0.5)
    with col2:
        condition = st.selectbox("Match Conditions", 
                                options=["dry", "damp", "wet_synthetic"], index=0)
    
    if st.button("Calculate Metrics", type="primary"):
        result = calculate_metrics(velocity, condition)
        st.success("✅ Calculation Complete — Pure Phillips Calibration")
        
        rcol1, rcol2, rcol3 = st.columns(3)
        with rcol1:
            st.metric("Kinetic Energy", f"{result['kinetic_energy_j']} J")
            st.metric("Baseline Dry Pressure", f"{result['baseline_dry_kpa']} kPa")
        with rcol2:
            st.metric("Adjusted Pressure", f"{result['adjusted_kpa']} kPa", 
                     delta=f"×{result['wet_factor_applied']}")
            st.metric("Baseline Dry Duration", f"{result['baseline_dry_wave_duration_ms']} ms")
        with rcol3:
            st.metric("Adjusted Duration", f"{result['adjusted_wave_duration_ms']} ms")
            st.metric("Load Category", result['load_category'])
        
        st.json(result)
    
    st.divider()
    
    # Batch CSV Upload
    st.header("📁 Batch CSV Processing")
    st.info("Upload CSV with a velocity column → all columns preserved + metrics appended → download results.")
    
    uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write(f"📋 Uploaded: {len(df)} rows × {len(df.columns)} columns")
        
        vel_col = None
        for c in df.columns:
            if str(c).lower() in ["velocity", "speed", "ball_velocity", "ballvelocity", "ball_velocity_mps"]:
                vel_col = c
                break
        
        if not vel_col:
            st.error("❌ Could not find velocity column. Use 'velocity' or 'ball_velocity_mps'")
            return
        
        cond_col = None
        for c in df.columns:
            if str(c).lower() in ["condition", "weather", "match_condition"]:
                cond_col = c
                break
        
        st.info(f"✅ Using velocity column: **{vel_col}**" + 
                (f" | Condition: **{cond_col}**" if cond_col else " | Default: DRY"))
        
        results = []
        for _, row in df.iterrows():
            v = float(row[vel_col])
            c = str(row[cond_col]).lower().strip() if cond_col else "dry"
            if "wet" in c and "synthetic" not in c:
                c = "damp" if "damp" in c or "light" in c else "wet_synthetic"
            elif c not in ["dry", "damp", "wet_synthetic"]:
                c = "dry"
            results.append(calculate_metrics(v, c))
        
        metrics_df = pd.DataFrame(results)
        metrics_df = metrics_df.drop(columns=["calibration_used"])
        output_df = pd.concat([df.reset_index(drop=True), metrics_df], axis=1)
        
        st.success(f"✅ Processed {len(df)} rows")
        st.dataframe(output_df, use_container_width=True)
        
        csv = output_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Results CSV",
            data=csv,
            file_name=f"ball2head_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            type="primary"
        )
    
    st.divider()
    st.caption("Elite Size 5 — A1/B1 Mean — FIFA 430g — Phillips et al. (2026)")

# =============================================================================
# RUN
# =============================================================================
if __name__ == "__main__":
    run_streamlit()