# ==========================================================
# 🏠 BALL2HEAD — Unified Heading Exposure Calculator & HISTORY
# Author: Hansen Sominabo
# Built on peer-reviewed research: Phillips et al. (2026),
# Zhang et al. (2013), Caccese et al. (2018), Naunheim et al. (2003)
# ==========================================================

import math
import streamlit as st
import pandas as pd
from datetime import datetime
import os
import json

# ==========================================================
# 📋 CALIBRATION CONSTANTS — ALL VALUES FROM PEER-REVIEWED DATA
# ==========================================================
BALL_CALIBRATION = {
    3: {"name": "Size 3 (Youth U8–U10)", "mass_kg": 0.32, "k1_kPa_per_J": 1.37, "k2_ms_per_J": 0.073, "force_kPa_per_kN": 16.2},
    4: {"name": "Size 4 (Youth U12–U14)", "mass_kg": 0.37, "k1_kPa_per_J": 1.28, "k2_ms_per_J": 0.070, "force_kPa_per_kN": 15.9},
    5: {"name": "Size 5 (Adult / Elite)", "mass_kg": 0.43, "k1_kPa_per_J": 1.19, "k2_ms_per_J": 0.067, "force_kPa_per_kN": 15.7}
}

GENDER_ADJUSTMENT = {"Male": 1.00, "Female": 1.20}
AGE_GROUP_MAP = {"U8–U10": 3, "U12–U14": 4, "U16–U18": 5, "Adult / Elite": 5}
AGE_GROUP_NOTES = {
    "U8–U10": "Uses Size 3 ball; head mass lower — relative exposure may be higher",
    "U12–U14": "Uses Size 4 ball; transitional period for heading exposure",
    "U16–U18": "Uses Size 5 ball; approaching adult biomechanics",
    "Adult / Elite": "Uses Size 5 ball; baseline calibration from Phillips et al. (2026)"
}

HEAD_MASS_ESTIMATE_KG = 4.5
GRAVITY_MS2 = 9.81
HISTORY_FILE = "ball2head_history.json"

# ==========================================================
# 💾 HISTORY DATA STORAGE — AUDITABLE & TIMESTAMPED
# ==========================================================
def load_history():
    """Load saved calculations — auditable history"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_to_history(entry):
    """Save calculation to history — timestamped"""
    history = load_history()
    entry["saved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history.append(entry)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def clear_history():
    """Clear all history"""
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)

# ==========================================================
# 🔄 UNIT CONVERSION HELPERS
# ==========================================================
def convert_velocity_to_ms(value, unit):
    if unit == "m/s": return value
    elif unit == "km/h": return value / 3.6
    elif unit == "mph": return value * 0.44704
    elif unit == "ft/s": return value * 0.3048
    else: raise ValueError(f"Unknown velocity unit: {unit}")

def convert_force_to_kN(value, unit):
    if unit == "kN": return value
    elif unit == "N": return value / 1000
    elif unit == "lbf": return value * 0.00444822
    else: raise ValueError(f"Unknown force unit: {unit}")

def convert_acceleration_to_ms2(value, unit):
    if unit == "m/s²": return value
    elif unit == "g": return value * GRAVITY_MS2
    elif unit == "ft/s²": return value * 0.3048
    else: raise ValueError(f"Unknown acceleration unit: {unit}")

# ==========================================================
# 🧠 CORE CALCULATION LOGIC — PEER-REVIEWED FORMULAS
# ==========================================================
def calculate_from_velocity(velocity_ms, ball_size=5, gender="Male", age_group="Adult / Elite", timestamp=None, player_id=None):
    ball = BALL_CALIBRATION[ball_size]
    gender_factor = GENDER_ADJUSTMENT[gender]
    
    energy_J = 0.5 * ball["mass_kg"] * (velocity_ms ** 2)
    base_kPa = energy_J * ball["k1_kPa_per_J"]
    base_ms = energy_J * ball["k2_ms_per_J"]
    final_kPa = base_kPa * gender_factor
    final_ms = base_ms
    
    contact_time_s = final_ms / 1000
    impulse = ball["mass_kg"] * velocity_ms
    force_N = impulse / contact_time_s if contact_time_s > 0 else 0
    pla_ms2 = force_N / HEAD_MASS_ESTIMATE_KG
    pla_g = pla_ms2 / GRAVITY_MS2
    
    risk = get_risk_level(final_kPa)
    
    result = {
        "timestamp": timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "player_id": player_id or "Not Specified",
        "input_type": "Ball Velocity",
        "velocity_kmh": round(velocity_ms * 3.6, 1),
        "energy_J": round(energy_J, 1),
        "peak_kPa": round(final_kPa, 1),
        "wave_ms": round(final_ms, 2),
        "pla_g": round(pla_g, 1),
        "risk_level": risk.split(" — ")[0],
        "gender": gender,
        "age_group": age_group,
        "ball_size": ball_size
    }
    return result

def calculate_from_force(force_kN, ball_size=5, gender="Male", age_group="Adult / Elite", timestamp=None, player_id=None):
    ball = BALL_CALIBRATION[ball_size]
    gender_factor = GENDER_ADJUSTMENT[gender]
    
    base_kPa = force_kN * ball["force_kPa_per_kN"]
    final_kPa = base_kPa * gender_factor
    energy_J = base_kPa / ball["k1_kPa_per_J"]
    final_ms = energy_J * ball["k2_ms_per_J"]
    
    force_N = force_kN * 1000
    pla_ms2 = force_N / HEAD_MASS_ESTIMATE_KG
    pla_g = pla_ms2 / GRAVITY_MS2
    
    risk = get_risk_level(final_kPa)
    
    result = {
        "timestamp": timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "player_id": player_id or "Not Specified",
        "input_type": "Impact Force",
        "force_kN": round(force_kN, 3),
        "energy_J": round(energy_J, 1),
        "peak_kPa": round(final_kPa, 1),
        "wave_ms": round(final_ms, 2),
        "pla_g": round(pla_g, 1),
        "risk_level": risk.split(" — ")[0],
        "gender": gender,
        "age_group": age_group,
        "ball_size": ball_size
    }
    return result

def calculate_from_acceleration(accel_ms2, axis=None, ball_size=5, gender="Male", age_group="Adult / Elite", timestamp=None, player_id=None):
    gender_factor = GENDER_ADJUSTMENT[gender]
    
    if isinstance(accel_ms2, (list, tuple)) and len(accel_ms2) == 3:
        ax, ay, az = accel_ms2
        accel_ms2 = math.sqrt(ax**2 + ay**2 + az**2)
    
    pla_g = accel_ms2 / GRAVITY_MS2
    force_N = accel_ms2 * HEAD_MASS_ESTIMATE_KG
    force_kN = force_N / 1000
    ball = BALL_CALIBRATION[ball_size]
    base_kPa = force_kN * ball["force_kPa_per_kN"]
    final_kPa = base_kPa * gender_factor
    energy_J = base_kPa / ball["k1_kPa_per_J"]
    final_ms = energy_J * ball["k2_ms_per_J"]
    
    risk = get_risk_level(final_kPa)
    axis_label = axis if axis else "3D Magnitude"
    
    result = {
        "timestamp": timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "player_id": player_id or "Not Specified",
        "input_type": f"IMU Accel ({axis_label})",
        "peak_accel_g": round(pla_g, 1),
        "energy_J": round(energy_J, 1),
        "peak_kPa": round(final_kPa, 1),
        "wave_ms": round(final_ms, 2),
        "pla_g": round(pla_g, 1),
        "risk_level": risk.split(" — ")[0],
        "gender": gender,
        "age_group": age_group,
        "ball_size": ball_size
    }
    return result

def get_risk_level(kpa):
    if kpa < 70: return "🟢 LOW — Within typical daily exposure"
    elif kpa < 100: return "🟡 MODERATE — Monitor cumulative exposure"
    elif kpa < 150: return "🟠 ELEVATED — Significant impact, note event"
    else: return "🔴 EXTREME — High-energy impact, assess player"

# ==========================================================
# 📁 BATCH CSV PROCESSING
# ==========================================================
def process_batch_csv(df, gender="Male", age_group="Adult / Elite", vel_unit="km/h", accel_unit="g"):
    results = []
    ball_size = AGE_GROUP_MAP[age_group]
    
    for idx, row in df.iterrows():
        timestamp = str(row.get("timestamp", row.get("time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
        player_id = str(row.get("player_id", row.get("player", f"Player_{idx+1}")))
        
        # Velocity columns
        vel_value = None
        for col in ["velocity", "ball_velocity", "speed", "velocity_kmh", "velocity_m_s"]:
            if col in df.columns and pd.notna(row[col]):
                val = float(row[col])
                if col == "velocity_m_s": vel_ms = val
                elif col == "velocity_kmh": vel_ms = val / 3.6
                else: vel_ms = convert_velocity_to_ms(val, vel_unit)
                res = calculate_from_velocity(vel_ms, ball_size, gender, age_group, timestamp, player_id)
                results.append(res)
                vel_value = val
                break
        if vel_value is not None: continue
        
        # Force columns
        for col in ["force_kN", "force", "impact_force"]:
            if col in df.columns and pd.notna(row[col]):
                val = float(row[col])
                res = calculate_from_force(val, ball_size, gender, age_group, timestamp, player_id)
                results.append(res)
                break
        else:
            # Acceleration columns
            if "accel_x" in df.columns and "accel_y" in df.columns and "accel_z" in df.columns:
                ax = convert_acceleration_to_ms2(float(row["accel_x"]), accel_unit) if pd.notna(row["accel_x"]) else 0
                ay = convert_acceleration_to_ms2(float(row["accel_y"]), accel_unit) if pd.notna(row["accel_y"]) else 0
                az = convert_acceleration_to_ms2(float(row["accel_z"]), accel_unit) if pd.notna(row["accel_z"]) else 0
                res = calculate_from_acceleration([ax, ay, az], None, ball_size, gender, age_group, timestamp, player_id)
                results.append(res)
            elif "acceleration" in df.columns or "accel_g" in df.columns:
                col = "acceleration" if "acceleration" in df.columns else "accel_g"
                val = float(row[col])
                ams2 = val * GRAVITY_MS2 if col == "accel_g" else val
                res = calculate_from_acceleration(ams2, "X", ball_size, gender, age_group, timestamp, player_id)
                results.append(res)
    
    return pd.DataFrame(results)

# ==========================================================
# 🌐 MAIN APP
# ==========================================================
def main():
    st.set_page_config(page_title="Ball2Head — Heading Exposure & History", layout="wide")
    
    st.title("⚽ Ball2Head — Unified Heading Exposure Calculator")
    st.markdown("""
    > **Peer-reviewed framework for estimating heading load. Save results to history, 
    > then download as CSV to plot graphs and analyse trends in Excel.**
    """)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🧮 Single Calculation", "📁 Batch CSV Upload", "📋 History & Download", "📚 Reference"])
    
    # ======================================
    # TAB 1 — SINGLE CALCULATION
    # ======================================
    with tab1:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("👤 Player & Match Details")
            gender = st.selectbox("Gender / Biomechanical Adjustment", list(GENDER_ADJUSTMENT.keys()), index=0)
            age_group = st.selectbox("Age Group / Ball Size", list(AGE_GROUP_MAP.keys()), index=3)
            ball_size = AGE_GROUP_MAP[age_group]
            st.info(f"Using: {BALL_CALIBRATION[ball_size]['name']}")
            st.caption(AGE_GROUP_NOTES[age_group])
            player_id = st.text_input("Player ID (optional)", value="")
        
        with col2:
            st.subheader("📥 Input Method")
            input_method = st.radio("Select Data Source", ["Ball Velocity", "Peak Impact Force", "IMU 3D Acceleration"])
        
        with col3:
            st.subheader("🔢 Enter Values")
            result = None
            if input_method == "Ball Velocity":
                vel_unit = st.selectbox("Velocity Unit", ["km/h", "m/s", "mph", "ft/s"], index=0)
                vel_value = st.number_input(f"Ball Velocity at Impact ({vel_unit})", min_value=0.0, max_value=200.0, value=18.0, step=0.5)
                if st.button("Calculate Exposure", type="primary"):
                    velocity_ms = convert_velocity_to_ms(vel_value, vel_unit)
                    result = calculate_from_velocity(velocity_ms, ball_size, gender, age_group, player_id=player_id or "Not Specified")
            
            elif input_method == "Peak Impact Force":
                force_unit = st.selectbox("Force Unit", ["kN", "N", "lbf"], index=0)
                force_value = st.number_input(f"Peak Impact Force ({force_unit})", min_value=0.0, max_value=50.0, value=5.5, step=0.1)
                if st.button("Calculate Exposure", type="primary"):
                    force_kN = convert_force_to_kN(force_value, force_unit)
                    result = calculate_from_force(force_kN, ball_size, gender, age_group, player_id=player_id or "Not Specified")
            
            elif input_method == "IMU 3D Acceleration":
                accel_unit = st.selectbox("Acceleration Unit", ["g", "m/s²", "ft/s²"], index=0)
                use_3axis = st.checkbox("Use 3-Axis Magnitude (x, y, z)", value=True)
                if use_3axis:
                    col_x, col_y, col_z = st.columns(3)
                    with col_x: ax = st.number_input(f"X-Axis ({accel_unit})", value=15.0, step=0.5)
                    with col_y: ay = st.number_input(f"Y-Axis ({accel_unit})", value=22.0, step=0.5)
                    with col_z: az = st.number_input(f"Z-Axis ({accel_unit})", value=8.0, step=0.5)
                    if st.button("Calculate Exposure", type="primary"):
                        ams2 = [convert_acceleration_to_ms2(v, accel_unit) for v in [ax, ay, az]]
                        result = calculate_from_acceleration(ams2, None, ball_size, gender, age_group, player_id=player_id or "Not Specified")
                else:
                    axis = st.selectbox("Primary Axis", ["X", "Y", "Z"])
                    accel_value = st.number_input(f"Peak Acceleration ({accel_unit})", value=28.0, step=0.5)
                    if st.button("Calculate Exposure", type="primary"):
                        ams2 = convert_acceleration_to_ms2(accel_value, accel_unit)
                        result = calculate_from_acceleration(ams2, axis, ball_size, gender, age_group, player_id=player_id or "Not Specified")
        
        if result:
            st.divider()
            st.subheader("📊 Heading Exposure Results")
            rc = st.columns(6)
            rc[0].metric("Energy (J)", result["energy_J"])
            rc[1].metric("Peak Pressure (kPa)", result["peak_kPa"])
            rc[2].metric("Wave Duration (ms)", result["wave_ms"])
            rc[3].metric("Peak Linear Accel (g)", result["pla_g"])
            rc[4].metric("Input Source", result["input_type"])
            rc[5].metric("Gender", result["gender"])
            
            risk_text = result["risk_level"]
            if "LOW" in risk_text: st.success(f"🟢 {risk_text}")
            elif "MODERATE" in risk_text: st.info(f"🟡 {risk_text}")
            elif "ELEVATED" in risk_text: st.warning(f"🟠 {risk_text}")
            else: st.error(f"🔴 {risk_text}")
            
            if st.button("💾 Save to History"):
                save_to_history(result)
                st.success("✅ Saved! Go to **History & Download** tab to view or export.")
    
    # ======================================
    # TAB 2 — BATCH UPLOAD
    # ======================================
    with tab2:
        st.subheader("📁 Batch CSV Upload — Process Multiple Events")
        st.markdown("""
        Upload a CSV file. The system will detect columns and calculate all metrics automatically.
        **Columns it reads:** `timestamp`, `player_id`, `velocity` / `force_kN` / `accel_x,accel_y,accel_z`
        """)
        
        col1, col2 = st.columns([1, 2])
        with col1:
            batch_gender = st.selectbox("Default Gender", ["Male", "Female"], index=0)
            batch_age = st.selectbox("Default Age Group", list(AGE_GROUP_MAP.keys()), index=3)
            vel_unit_batch = st.selectbox("Velocity Unit", ["km/h", "m/s", "mph"], index=0)
            accel_unit_batch = st.selectbox("Acceleration Unit", ["g", "m/s²"], index=0)
        
        with col2:
            uploaded_file = st.file_uploader("Upload CSV file", type="csv")
            if uploaded_file:
                df_upload = pd.read_csv(uploaded_file)
                st.info(f"✅ Loaded {len(df_upload)} rows: {', '.join(df_upload.columns)}")
                with st.expander("Preview Data"):
                    st.dataframe(df_upload.head())
                
                if st.button("🔄 Process Batch", type="primary"):
                    results_df = process_batch_csv(df_upload, batch_gender, batch_age, vel_unit_batch, accel_unit_batch)
                    st.session_state["batch_results"] = results_df
                    st.success(f"✅ Processed {len(results_df)} events!")
        
        if "batch_results" in st.session_state and not st.session_state["batch_results"].empty:
            st.divider()
            st.subheader("📊 Batch Results")
            st.dataframe(st.session_state["batch_results"], use_container_width=True)
            
            if st.button("💾 Save ALL to History"):
                for _, row in st.session_state["batch_results"].iterrows():
                    save_to_history(row.to_dict())
                st.success(f"✅ {len(st.session_state['batch_results'])} saved to history!")
            
            csv = st.session_state["batch_results"].to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Batch CSV", csv, 
                             f"ball2head_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "text/csv")
    
    # ======================================
    # TAB 3 — HISTORY & DOWNLOAD
    # ======================================
    with tab3:
        st.subheader("📋 History & Download — Ready for Excel")
        st.markdown("""
        > **All saved calculations appear below.** Download as CSV to plot graphs, 
        > analyse trends, and create reports in Excel.
        """)
        
        history = load_history()
        if history:
            df_hist = pd.DataFrame(history)
            st.info(f"📂 {len(df_hist)} saved calculation(s)")
            
            # Show table
            st.dataframe(df_hist, use_container_width=True, hide_index=True)
            
            # Download button
            csv_hist = df_hist.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download FULL History (CSV)", csv_hist, 
                             f"ball2head_HISTORY_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", 
                             "text/csv", type="primary")
            
            st.markdown("### 💡 How to use in Excel")
            st.markdown("""
            1. Open the downloaded CSV file in Excel
            2. Highlight columns: **timestamp + energy_J + peak_kPa + wave_ms + pla_g**
            3. Go to **Insert → Charts → Line Chart** to view trends over time
            4. Use **player_id** to filter and compare individual players
            """)
            
            if st.button("🗑️ Clear All History"):
                clear_history()
                st.rerun()
        
        else:
            st.info("📭 History is empty. Save calculations from the **Single Calculation** or **Batch CSV Upload** tabs above.")
    
    # ======================================
    # TAB 4 — REFERENCE
    # ======================================
    with tab4:
        st.subheader("📚 Calibration & Reference")
        st.markdown("""
        ### Calibration Constants
        | Ball Size | Mass (kg) | k₁ (kPa/J) | k₂ (ms/J) | Force→kPa (kPa/kN) |
        |-----------|-----------|------------|-----------|-------------------|
        | Size 3    | 0.32      | 1.37       | 0.073     | 16.2              |
        | Size 4    | 0.37      | 1.28       | 0.070     | 15.9              |
        | Size 5    | 0.43      | 1.19       | 0.067     | 15.7              |
        *Source: Phillips et al. (2026) — linear regression R² > 0.999*
        
        ### Gender Adjustment
        - **Male**: 1.00 (baseline)
        - **Female**: 1.20 (+20% peak pressure — Zhang et al. 2013, Caccese et al. 2018)
        
        ### Risk Thresholds
        - 🟢 **LOW** — < 70 kPa
        - 🟡 **MODERATE** — 70–99 kPa
        - 🟠 **ELEVATED** — 100–149 kPa
        - 🔴 **EXTREME** — ≥ 150 kPa
        
        ### References
        Phillips et al. (2026) — Ball impact characteristics and intracranial pressure wave propagation.
        Zhang et al. (2013) — Head impact accelerations in collegiate soccer: Gender differences.
        Caccese et al. (2018) — Sex differences in head impact biomechanics.
        Naunheim et al. (2003) — Linear acceleration predicts intracranial pressure in a head model.
        """)
    
    st.divider()
    st.caption("Ball2Head — Unified Heading Exposure Framework | Built on peer-reviewed research")

if __name__ == "__main__":
    main()