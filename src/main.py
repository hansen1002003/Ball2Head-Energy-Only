"""
Ball2Head — Heading Load Calculator
====================================
Calibration derived from:
  Phillips, I. et al. (2026) "Pressure wave propagation from association football head collisions"
  Proc IMechE Part P: J Sports Engineering and Technology

Method: Linear proportionality P ∝ E → k₁ = P/E, k₂ = t/E
Elite Standard: Mean of A1 (Thermally Bonded) & B1 (Fuse-Welded)
Standardised to: FIFA Size 5 — 430 g dry mass

Author: Hansen Sominabo Kekom
Version: 1.0 — Pure Phillips Calibration
"""

import streamlit as st
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
from typing import Optional, List
import uvicorn
import threading

# =============================================================================
# CALIBRATION CONSTANTS — DERIVED EXCLUSIVELY FROM PHILLIPS ET AL. (2026)
# =============================================================================
# Source: A1/B1 mean at 18 m/s, standardised to FIFA 430 g
# k₁ = Pressure ÷ Energy  |  k₂ = Duration ÷ Energy

class Calibration:
    """Elite Standard — A1/B1 Mean, FIFA 430g"""
    BALL_MASS_DRY_KG = 0.430       # FIFA regulation mass
    
    DRY_k1_KPA_PER_J = 1.19        # kPa/J — baseline
    DRY_k2_MS_PER_J = 0.067        # ms/J — baseline
    
    # Wet condition factors — from Phillips measured A1/B1 mass increase + pressure effect
    WET_FACTORS = {
        "dry": 1.00,
        "damp": 1.10,
        "wet_synthetic": 1.25
    }
    
    @classmethod
    def get_factors(cls, condition: str):
        """Get k1, k2 adjusted for conditions"""
        cond = condition.lower().strip()
        factor = cls.WET_FACTORS.get(cond, 1.00)
        return {
            "k1_kpa_j": round(cls.DRY_k1_KPA_PER_J * factor, 4),
            "k2_ms_j": round(cls.DRY_k2_MS_PER_J * factor, 5),
            "wet_factor": factor
        }


# =============================================================================
# CORE CALCULATION ENGINE — PURE PHILLIPS PROPORTIONALITY
# =============================================================================

def calculate_metrics(velocity_mps: float, condition: str = "dry"):
    """
    Calculate heading load metrics from ball velocity.
    
    Formula (from Phillips et al. 2026 — P ∝ E, t ∝ E):
        E = ½ × m × v²
        P = k₁ × E
        t = k₂ × E
    
    Args:
        velocity_mps: Ball speed at impact (m/s)
        condition: dry / damp / wet_synthetic
    
    Returns:
        Dictionary of all calculated metrics
    """
    if velocity_mps <= 0:
        raise ValueError("Velocity must be greater than 0")
    
    # Step 1: Kinetic Energy — E = ½mv²
    energy_j = 0.5 * Calibration.BALL_MASS_DRY_KG * (velocity_mps ** 2)
    
    # Step 2: Get calibration constants (baseline + condition-adjusted)
    dry_k1 = Calibration.DRY_k1_KPA_PER_J
    dry_k2 = Calibration.DRY_k2_MS_PER_J
    factors = Calibration.get_factors(condition)
    
    # Step 3: Calculate baseline (dry) values
    baseline_kpa = round(dry_k1 * energy_j, 2)
    baseline_ms = round(dry_k2 * energy_j, 3)
    
    # Step 4: Calculate condition-adjusted values
    adjusted_kpa = round(factors["k1_kpa_j"] * energy_j, 2)
    adjusted_ms = round(factors["k2_ms_j"] * energy_j, 3)
    
    # Step 5: Load category — from pressure thresholds
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
# FAST API — FOR DATA PROVIDERS / AUTOMATED INTEGRATION
# =============================================================================
api_app = FastAPI(
    title="Ball2Head API",
    description="Heading Load Metrics — Calibrated from Phillips et al. (2026)",
    version="1.0.0"
)

class CalculationRequest(BaseModel):
    match_id: Optional[str] = None
    timestamp: Optional[str] = None
    ball_velocity_mps: float
    condition: str = "dry"  # dry / damp / wet_synthetic

class CalculationResponse(BaseModel):
    calculation_id: str
    match_id: Optional[str]
    timestamp: Optional[str]
    ball_velocity_mps: float
    condition: str
    kinetic_energy_j: float
    baseline_dry_kpa: float
    baseline_dry_wave_duration_ms: float
    adjusted_kpa: float
    adjusted_wave_duration_ms: float
    wet_factor_applied: float
    load_category: str
    calibration_reference: str


@api_app.post("/v1/calculate", response_model=CalculationResponse)
async def api_calculate(request: CalculationRequest):
    """Calculate heading load from ball velocity — live endpoint"""
    try:
        result = calculate_metrics(request.ball_velocity_mps, request.condition)
        return CalculationResponse(
            calculation_id=f"b2h_{uuid.uuid4().hex[:8]}",
            match_id=request.match_id,
            timestamp=request.timestamp,
            **result,
            calibration_reference="Phillips et al. (2026) — A1/B1 Mean — FIFA 430g"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def run_api():
    """Run API in background thread"""
    uvicorn.run(api_app, host="0.0.0.0", port=8000)


# =============================================================================
# STREAMLIT INTERFACE — FOR MANUAL USE / BATCH CSV
# =============================================================================

def run_streamlit():
    st.set_page_config(page_title="Ball2Head — Heading Load Calculator", layout="wide")
    st.title("⚽ Ball2Head — Heading Load Metrics")
    st.subheader("Calibrated from Phillips et al. (2026) — Elite Size 5 Standard")
    
    # Methodology statement — full transparency
    with st.expander("📋 Methodology & Calibration Source"):
        st.markdown("""
        **Calibration Source:** Mean of A1 (Thermally Bonded) & B1 (Fuse-Welded) elite match balls, 
        standardised to FIFA regulation 430 g dry mass.
        
        **Formula:**
        - Kinetic Energy: $E = \\frac{1}{2}mv^2$
        - Peak Pressure: $P = k_1 \\times E$  → **k₁ = 1.19 kPa/J (dry)**
        - Wave Duration: $t = k_2 \\times E$  → **k₂ = 0.067 ms/J (dry)**
        
        **Wet Conditions:** Adjustment factors derived from Phillips' measured mass increase 
        and pressure amplification (A1/B1 mean).
        - Damp: ×1.10
        - Wet Synthetic: ×1.25
        
        **Reference:** Phillips, I. et al. (2026) — *Pressure wave propagation from association football head collisions*
        """)
    
    # -------------------------------------------------------------------------
    # SECTION 1 — MANUAL INPUT
    # -------------------------------------------------------------------------
    st.header("🎯 Single Calculation")
    col1, col2 = st.columns(2)
    
    with col1:
        velocity = st.number_input("Ball Velocity at Impact (m/s)", 
                                   min_value=5.0, max_value=35.0, value=18.0, step=0.5)
    with col2:
        condition = st.selectbox("Match Conditions", 
                                options=["dry", "damp", "wet_synthetic"],
                                index=0,
                                help="Dry = Standard baseline")
    
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
    
    # -------------------------------------------------------------------------
    # SECTION 2 — BATCH CSV UPLOAD
    # -------------------------------------------------------------------------
    st.header("📁 Batch CSV Processing")
    st.info("""
    Upload any CSV file. The system will look for columns named:
    **ball_velocity_mps** (required), **condition** (optional, defaults to dry).
    All other columns will be preserved — your data is returned with our metrics appended.
    """)
    
    uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write(f"📋 Uploaded: {len(df)} rows × {len(df.columns)} columns")
        
        # Find velocity column — flexible matching
        vel_col = None
        for c in df.columns:
            if str(c).lower() in ["velocity", "speed", "ball_velocity", "ballvelocity", "ball_velocity_mps"]:
                vel_col = c
                break
        
        if not vel_col:
            st.error("❌ Could not find velocity column. Please ensure your CSV has a column named 'velocity' or 'ball_velocity_mps'")
            return
        
        # Find condition column
        cond_col = None
        for c in df.columns:
            if str(c).lower() in ["condition", "weather", "match_condition", "status"]:
                cond_col = c
                break
        
        st.info(f"✅ Using velocity column: **{vel_col}**" + 
                (f" | Condition column: **{cond_col}**" if cond_col else " | Defaulting to DRY condition"))
        
        # Process all rows
        results = []
        for _, row in df.iterrows():
            v = float(row[vel_col])
            c = str(row[cond_col]).lower().strip() if cond_col else "dry"
            if "wet" in c and "synthetic" not in c:
                if "damp" in c or "light" in c:
                    c = "damp"
                else:
                    c = "wet_synthetic"
            elif c not in ["dry", "damp", "wet_synthetic"]:
                c = "dry"
            
            metrics = calculate_metrics(v, c)
            results.append(metrics)
        
        # Combine original data + new metrics
        metrics_df = pd.DataFrame(results)
        metrics_df = metrics_df.drop(columns=["calibration_used"])
        output_df = pd.concat([df.reset_index(drop=True), metrics_df], axis=1)
        
        st.success(f"✅ Processed {len(df)} rows successfully")
        st.dataframe(output_df, use_container_width=True)
        
        # Download
        csv = output_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Results as CSV",
            data=csv,
            file_name=f"ball2head_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            type="primary"
        )
    
    st.divider()
    
    # -------------------------------------------------------------------------
    # API INFORMATION
    # -------------------------------------------------------------------------
    st.header("🔌 API Integration — For Data Providers")
    st.code("""
# Endpoint: http://localhost:8000/v1/calculate
# Method: POST

{
  "match_id": "MATCH_001",
  "timestamp": "00:27:11.050",
  "ball_velocity_mps": 18.5,
  "condition": "dry"
}

# Response includes: Energy, Baseline kPa, Adjusted kPa, Duration, Category
# Calibration: A1/B1 Mean — FIFA 430g — Phillips et al. (2026)
    """, language="http")
    
    st.caption("""
    All calculations use ONLY Size 5 elite ball calibration (A1/B1 Mean). 
    No gender adjustments, no head mass assumptions — pure Phillips et al. (2026) proportionality.
    """)


# =============================================================================
# RUN BOTH — API + STREAMLIT
# =============================================================================
if __name__ == "__main__":
    # Start FastAPI in background
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    
    # Run Streamlit (main thread)
    run_streamlit()