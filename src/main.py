"""
Ball2Head — Dual-Use Impact Engine
====================================
Investigational Research — Hansen Sominabo Kekom
Birmingham Newman University — Final Year Project

Calibration Sources:
  🧠 HEADING — Phillips, I. et al. (2026) — Pressure wave propagation
    • EXACT TEST VELOCITY: 18.20 ± 0.27 m/s (dry conditions)
    • 7 ball types (A1–G1) · 3 sizes (5/4/3) · Dry/Damp/Wet
    • A1 = Thermally Bonded Elite — DEFAULT STANDARD
    • C1 = Machine-Stitched Elite — PRIMARY REFERENCE
    • Water uptake per ball type from paper Table 1 — NOT uniform scaling
    • Leather balls (F1,G1): pressure & PPSI amplified beyond mass effect
    • Energy_Index_Pa2s = (P_peak)² × duration — reduced-order approximation
      NOTE: This is NOT the paper's integrated PPSI₉₀ metric. Values are ~60× larger.
    • PPSI90_Time_ms = pressure wave duration — matches paper definition
  ⚽ KICK — Nunome et al. (2024) — Biomechanics of Instep Soccer Kick
    • Independent calibration — separate constants

Core Methodology:
  • Kinetic Energy:       E = ½mv²
  • HEADING → Brain Load: Peak-to-Peak Pressure(kPa), PPSI90 Time(ms),
                           Energy Index(Pa²·s), Brain Load Units(kPa·ms)
  • KICK → Shot Power:    Force(N), ContactTime(ms), PeakPower(kW)

Risk Thresholds (Heading): 🟢 0–45 | 🟡 45–90 | 🔴 90–160 BLU
Performance Tiers (Kick): 🔵 <5kW | 🟢 5–8kW | 🟡 8–12kW | 🔴 >12kW

Version: 4.8.0 — ✅ Column names corrected per academic naming standards
"""
import os
os.environ["PANDAS_DATAFRAME_BACKEND"] = "numpy"  # ← SKIPS PyArrow entirely!
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import base64

# =============================================================================
# PHILLIPS ET AL. (2026) — BALL CALIBRATION DATABASE
# =============================================================================
class BallCalibration:
    """Complete calibration — 7 ball types × 3 sizes × 3 conditions.
    Moisture uptake values DIRECTLY from Phillips Table 1 (NOT uniform guesses).
    Leather balls get additional amplification per paper findings."""
    # === BALL TYPE DEFINITIONS — Size 5, Dry @ 18.20 m/s ===
    BALL_TYPES = {
        "A1": {
            "name": "Thermally Bonded Elite",
            "construction": "Thermally Bonded — Modern Elite Match",
            "mass_dry_kg": 0.4365,
            "k1_kPa_per_J": 0.18360,
            "k2_ms_per_J": 0.00337,
            "R2_pressure": 0.991,
            "R2_duration": 0.988,
            "water_uptake_pct": 2.6,     # ✅ Phillips Table 1
            "is_leather": False
        },
        "B1": {
            "name": "Fuse-Welded Elite",
            "construction": "Fuse-Welded — Seamless Match",
            "mass_dry_kg": 0.4365,
            "k1_kPa_per_J": 0.17800,
            "k2_ms_per_J": 0.00327,
            "R2_pressure": 0.987,
            "R2_duration": 0.984,
            "water_uptake_pct": 2.2,     # ✅ Phillips Table 1
            "is_leather": False
        },
        "C1": {
            "name": "Machine-Stitched Elite",
            "construction": "Machine-Stitched — FIFA Quality Pro",
            "mass_dry_kg": 0.4273,
            "k1_kPa_per_J": 0.08052,
            "k2_ms_per_J": 0.00351,
            "R2_pressure": 0.994,
            "R2_duration": 0.992,
            "water_uptake_pct": 6.9,     # ✅ Phillips Table 1
            "is_leather": False
        },
        "D1": {
            "name": "Hand-Stitched Elite",
            "construction": "Hand-Stitched — Traditional Match",
            "mass_dry_kg": 0.4243,
            "k1_kPa_per_J": 0.12800,
            "k2_ms_per_J": 0.00317,
            "R2_pressure": 0.982,
            "R2_duration": 0.980,
            "water_uptake_pct": 10.4,    # ✅ Phillips Table 1
            "is_leather": False
        },
        "E1": {
            "name": "Synthetic Moulded",
            "construction": "Moulded — Training/Recreational",
            "mass_dry_kg": 0.4370,
            "k1_kPa_per_J": 0.25200,
            "k2_ms_per_J": 0.00330,
            "R2_pressure": 0.989,
            "R2_duration": 0.986,
            "water_uptake_pct": 1.4,     # ✅ Phillips Table 1
            "is_leather": False
        },
        "F1": {
            "name": "Laceless Leather",
            "construction": "Leather — Historical 1950s–60s",
            "mass_dry_kg": 0.4392,
            "k1_kPa_per_J": 0.07910,
            "k2_ms_per_J": 0.00303,
            "R2_pressure": 0.985,
            "R2_duration": 0.981,
            "water_uptake_pct": 34.3,    # ✅ Phillips Table 1
            "is_leather": True,
            "pressure_amp_wet": 2.77,     # ✅ Paper finding: +277%
            "PPSI_amp_wet": 8.36          # ✅ Paper finding: +836%
        },
        "G1": {
            "name": "Laced Leather",
            "construction": "Leather — Vintage Pre-1970s",
            "mass_dry_kg": 0.4496,
            "k1_kPa_per_J": 0.04800,
            "k2_ms_per_J": 0.00775,
            "R2_pressure": 0.980,
            "R2_duration": 0.978,
            "water_uptake_pct": 59.9,    # ✅ Phillips Table 1
            "is_leather": True,
            "pressure_amp_wet": 3.17,     # ✅ Paper finding: +317%
            "PPSI_amp_wet": 15.19         # ✅ Paper finding: +1519%
        },
    }

    # === BALL SIZE SCALING FACTORS (FIFA Standards) ===
    BALL_SIZES = {
        "Size 5 (Elite Adult)": {"mass_factor": 1.00, "vel_range": "13–23 m/s"},
        "Size 4 (U12–U14)":     {"mass_factor": 0.90, "vel_range": "11–20 m/s"},
        "Size 3 (U8–U10)":      {"mass_factor": 0.78, "vel_range": "10–15 m/s"}
    }

    # === MOISTURE MULTIPLIERS — Damp = 50% of full uptake; Wet = 100% uptake ===
    @classmethod
    def get_moisture_factors(cls, ball_type_id: str, condition: str) -> dict:
        """Returns mass multiplier and leather amplification factors from Phillips data."""
        ball = cls.BALL_TYPES[ball_type_id]
        uptake_pct = ball["water_uptake_pct"]
        if condition == "dry":
            mass_mult = 1.00
            pressure_amp = 1.00
            PPSI_amp = 1.00
        elif condition == "damp":
            mass_mult = 1.00 + (uptake_pct / 100.0) * 0.5
            pressure_amp = 1.00
            PPSI_amp = 1.00
        elif condition == "wet":
            mass_mult = 1.00 + (uptake_pct / 100.0)
            if ball.get("is_leather", False):
                pressure_amp = ball.get("pressure_amp_wet", 1.00)
                PPSI_amp = ball.get("PPSI_amp_wet", 1.00)
            else:
                pressure_amp = mass_mult
                PPSI_amp = mass_mult
        else:
            mass_mult = 1.00
            pressure_amp = 1.00
            PPSI_amp = 1.00
        return {
            "mass_mult": round(mass_mult, 4),
            "pressure_amp": round(pressure_amp, 3),
            "PPSI_amp": round(PPSI_amp, 3),
            "uptake_pct": uptake_pct
        }

    @classmethod
    def get_ball_calibration(cls, ball_type: str, ball_size: str, condition: str) -> dict:
        bt = ball_type.upper().strip()
        if bt not in cls.BALL_TYPES:
            raise ValueError(f"Invalid ball_type: {ball_type}. Must be A1,B1,C1,D1,E1,F1,G1")
        ball = cls.BALL_TYPES[bt]
        if ball_size not in cls.BALL_SIZES:
            raise ValueError(f"Invalid ball_size: {ball_size}. Must be Size 5/4/3")
        size = cls.BALL_SIZES[ball_size]
        cond_key = str(condition).lower().strip()
        if cond_key not in ["dry", "damp", "wet"]:
            raise ValueError(f"Invalid condition: {condition}. Must be dry/damp/wet")
        mf = cls.get_moisture_factors(bt, cond_key)
        mass_kg = ball["mass_dry_kg"] * size["mass_factor"] * mf["mass_mult"]
        k1 = ball["k1_kPa_per_J"]
        k2 = ball["k2_ms_per_J"]
        return {
            "ball_type_id": bt,
            "ball_name": ball["name"],
            "ball_size": ball_size,
            "condition": cond_key,
            "mass_kg": round(mass_kg, 4),
            "k1_kPa_per_J": round(k1, 5),
            "k2_ms_per_J": round(k2, 6),
            "R2_pressure": ball["R2_pressure"],
            "R2_duration": ball["R2_duration"],
            "vel_range": size["vel_range"],
            "mass_mult": mf["mass_mult"],
            "pressure_amp": mf["pressure_amp"],
            "PPSI_amp": mf["PPSI_amp"],
            "water_uptake_pct": mf["uptake_pct"]
        }

# =============================================================================
# NUNOME ET AL. (2024) — KICK CALIBRATION
# =============================================================================
class KickCalibration:
    """Shot power constants — Nunome et al. (2024)."""
    KICK_k_FORCE_PER_J_DRY = 22.1
    KICK_k_TIME_PER_J_DRY = 0.107
    KICK_MASS_REF_KG = 0.430

    @classmethod
    def get_kick_constants(cls, ball_mass_kg: float, mass_mult: float) -> dict:
        mass_ratio = ball_mass_kg / cls.KICK_MASS_REF_KG
        return {
            "force_per_J_N": round(cls.KICK_k_FORCE_PER_J_DRY * mass_ratio, 3),
            "time_per_J_ms": round(cls.KICK_k_TIME_PER_J_DRY * mass_ratio, 5)
        }

# =============================================================================
# IMPACT CALCULATION — WITH UPDATED COLUMN NAMES
# =============================================================================
def calculate_impact(velocity_mps: float, impact_type: str,
                     ball_type: str, ball_size: str, condition: str) -> dict | None:
    try:
        velocity = float(velocity_mps)
        if velocity <= 0:
            return None
    except (ValueError, TypeError):
        return None
    try:
        cal = BallCalibration.get_ball_calibration(ball_type, ball_size, condition)
    except ValueError:
        return None

    joules = 0.5 * cal["mass_kg"] * (velocity ** 2)

    if impact_type.lower() == "heading":
        base_kpa = cal["k1_kPa_per_J"] * joules
        base_ms = cal["k2_ms_per_J"] * joules
        total_kpa = base_kpa * cal["pressure_amp"]
        total_ms = base_ms

        # === ENERGY INDEX — reduced-order approximation, NOT paper's integral PPSI90 ===
        peak_pa = total_kpa * 1000
        duration_s = total_ms / 1000
        energy_index = (peak_pa ** 2) * duration_s * cal["PPSI_amp"]

        brain_load_kpa_ms = total_kpa * total_ms

        if brain_load_kpa_ms < 45:
            category = "LOW"
        elif brain_load_kpa_ms < 90:
            category = "MODERATE"
        elif brain_load_kpa_ms < 160:
            category = "HIGH"
        else:
            category = "ELEVATED"

        return {
            "impact_type": "heading",
            "ball_type_id": cal["ball_type_id"],
            "ball_name": cal["ball_name"],
            "ball_size": cal["ball_size"],
            "condition": cal["condition"],
            "ball_velocity_mps": round(velocity, 2),
            "mass_kg": round(cal["mass_kg"], 4),
            "Joules": round(joules, 2),
            "Peak_to_Peak_Pressure_kPa": round(total_kpa, 2),       # ✅ Updated
            "PPSI90_Time_ms": round(total_ms, 3),                     # ✅ Correct as-is
            "Energy_Index_Pa2s": round(energy_index, 1),              # ✅ Renamed
            "Brain_Load_Units_kPa_ms": round(brain_load_kpa_ms, 4),   # ✅ Updated with units
            "Load_Category": category,
            "Water_Uptake_pct": cal["water_uptake_pct"],
            "Moisture_Amplification": cal["pressure_amp"] if cal["pressure_amp"] > 1 else "1.00"
        }

    elif impact_type.lower() == "kick":
        kick_cal = KickCalibration.get_kick_constants(cal["mass_kg"], cal["mass_mult"])
        peak_force_N = kick_cal["force_per_J_N"] * joules
        contact_time_ms = kick_cal["time_per_J_ms"] * joules
        peak_power_kW = joules / (contact_time_ms / 1000) if contact_time_ms > 0 else 0

        if peak_power_kW < 5:
            perf_cat = "DEVELOPING"
        elif peak_power_kW < 8:
            perf_cat = "COMPETITIVE"
        elif peak_power_kW < 12:
            perf_cat = "ELITE"
        else:
            perf_cat = "WORLD-CLASS"

        return {
            "impact_type": "kick",
            "ball_type_id": cal["ball_type_id"],
            "ball_name": cal["ball_name"],
            "ball_size": cal["ball_size"],
            "condition": cal["condition"],
            "ball_velocity_mps": round(velocity, 2),
            "mass_kg": round(cal["mass_kg"], 4),
            "Joules": round(joules, 2),
            "Peak_Force_N": round(peak_force_N, 0),
            "Contact_Time_ms": round(contact_time_ms, 2),
            "Peak_Power_kW": round(peak_power_kW, 2),
            "Performance_Category": perf_cat
        }
    return None

# =============================================================================
# CHARTS — UPDATED COLUMN REFERENCES
# =============================================================================
def generate_head_chart(df: pd.DataFrame) -> tuple:
    df = df.copy()
    df = df.sort_values(["player_name", "Minute"])
    df["Cumulative_Brain_Load"] = df.groupby("player_name")["Brain_Load_Units_kPa_ms"].cumsum().round(2)
    df["Cumulative_Energy_Index"] = df.groupby("player_name")["Energy_Index_Pa2s"].cumsum().round(1)
    df["Player_Label"] = df["player_name"] + " (" + df.groupby("player_name")["player_name"].transform("count").astype(str) + " Headers)"
    max_load = df["Cumulative_Brain_Load"].max()
    y_max = max(160, round(max_load * 1.1, -1))
    x_max = max(95, round(df["Minute"].max() + 5, -1))
    ball_type_used = df["ball_type_id"].iloc[0] if "ball_type_id" in df.columns else "A1"
    ball_size_used = df["ball_size"].iloc[0] if "ball_size" in df.columns else "Size 5"

    fig = px.line(
        df, x="Minute", y="Cumulative_Brain_Load", color="Player_Label", markers=True,
        title=f"<b>🧠 HEADING — Cumulative Brain Load Index</b><br><sup>Phillips et al. (2026) · {ball_type_used} {ball_size_used}</sup>",
        labels={"Minute": "Match Timeline (Minutes)", "Cumulative_Brain_Load": "Cumulative Brain Load (kPa·ms)"},
        hover_data={
            "Minute": True,
            "Cumulative_Brain_Load": ": .2f",
            "Joules": ": .1f J",
            "Peak_to_Peak_Pressure_kPa": ": .1f kPa",
            "PPSI90_Time_ms": ": .2f ms",
            "Energy_Index_Pa2s": ": ,.0f Pa²·s"
        }
    )
    fig.add_hrect(y0=0, y1=45, fillcolor="#2ecc71", opacity=0.06, layer="below", line_width=0)
    fig.add_hrect(y0=45, y1=90, fillcolor="#f1c40f", opacity=0.06, layer="below", line_width=0)
    fig.add_hrect(y0=90, y1=160, fillcolor="#e74c3c", opacity=0.06, layer="below", line_width=0)
    fig.update_layout(
        xaxis=dict(range=[0, x_max], dtick=10),
        yaxis=dict(range=[0, y_max]),
        height=500,
        margin=dict(l=20, r=20, t=60, b=40)
    )
    fig.update_traces(line=dict(width=3.5), marker=dict(size=8))
    return fig, df

def generate_kick_chart(df: pd.DataFrame) -> tuple:
    df = df.copy()
    df = df.sort_values("Minute")
    df["Label"] = df["player_name"] + " — " + df["Minute"].astype(str) + "'"
    ball_type_used = df["ball_type_id"].iloc[0] if "ball_type_id" in df.columns else "A1"
    ball_size_used = df["ball_size"].iloc[0] if "ball_size" in df.columns else "Size 5"

    fig = px.bar(
        df, x="Label", y="Peak_Power_kW", color="Performance_Category",
        color_discrete_map={
            "DEVELOPING": "#3498db",
            "COMPETITIVE": "#2ecc71",
            "ELITE": "#f39c12",
            "WORLD-CLASS": "#e74c3c"
        },
        title=f"<b>⚽ KICK — Peak Shot Power</b><br><sup>Nunome et al. (2024) · {ball_type_used} {ball_size_used}</sup>",
        labels={"Peak_Power_kW": "Peak Power (kW)", "Label": "Player & Minute"},
        hover_data={"ball_velocity_mps": True, "Peak_Force_N": True, "Contact_Time_ms": True, "Joules": True}
    )
    fig.update_layout(
        xaxis_title="", height=500, margin=dict(l=20, r=20, t=60, b=60),
        showlegend=True, legend_title="Performance Tier"
    )
    return fig, df

# =============================================================================
# HTML DOWNLOAD
# =============================================================================
def get_html_download_link(fig, filename="Interactive_Chart.html", button_text="📄 Download Interactive Graph"):
    html_content = fig.to_html(include_plotlyjs="cdn", full_html=True)
    b64 = base64.b64encode(html_content.encode()).decode()
    href = f'''
    <a href="data:text/html;charset=utf-8;base64,{b64}" download="{filename}" 
       style="display:inline-block; padding:0.5rem 1rem; color:#ffffff; 
              background:linear-gradient(90deg, #4CAF50, #2196F3); 
              border-radius:0.5rem; text-decoration:none; font-weight:600; 
              box-shadow:0 2px 6px rgba(0,0,0,0.15); margin: 0.5rem 0;">
        {button_text}
    </a>
    '''
    return href

# =============================================================================
# MAIN APPLICATION — WITH CORRECTED COLUMN NAMES
# =============================================================================
def run_application():
    st.set_page_config(page_title="Ball2Head — Dual Impact Engine", layout="wide")
    if "entries" not in st.session_state:
        st.session_state.entries = []

    st.title("⚽🧠 Ball2Head — Dual Impact Engine")
    st.subheader("🧠 Heading Brain Health · ⚽ Kick Shot Power")

    st.header("📋 Match Information")
    col1, col2 = st.columns(2)
    with col1:
        match_teams = st.text_input("Match", value="Team A vs Team B")
    with col2:
        match_date = st.text_input("Date", value=pd.Timestamp.now().strftime("%Y-%m-%d"))

    st.info("""
    ℹ️ **Metric Clarification:**
    • **Energy_Index_Pa2s** = reduced-order approximation of PPSI₉₀, NOT the paper's integrated metric. Values ~60× larger.
    • **PPSI90_Time_ms** = pressure wave duration — directly calibrated from Phillips et al.
    • **Peak_to_Peak_Pressure_kPa** = peak-to-peak pressure as defined in the source paper.
    • **Brain_Load_Units_kPa_ms** = pressure × duration — unit explicitly shown.
    """)

    st.divider()

    # ─── METHOD 1: CSV UPLOAD ──────────────────────────────────────────
    st.header("📁 Method 1: Batch Upload from CSV")
    st.info("""
    ℹ️ **Standard values used where columns missing:**
    ball_type = **A1** · ball_size = **Size 5 (Elite Adult)** · condition = **dry**
    Required columns: player_name, Minute, ball_velocity_mps, impact_type
    """)
    uploaded_file = st.file_uploader("Upload Events CSV", type=["csv"])
    if uploaded_file:
        df_raw = pd.read_csv(uploaded_file)
        vel_col = next((c for c in df_raw.columns if "vel" in c.lower() or "speed" in c.lower()), None)
        name_col = next((c for c in df_raw.columns if "name" in c.lower() or "player" in c.lower()), None)
        time_col = next((c for c in df_raw.columns if "min" in c.lower() or "time" in c.lower()), None)
        type_col = next((c for c in df_raw.columns if "type" in c.lower() or "impact" in c.lower()), None)
        btype_col = next((c for c in df_raw.columns if "ball_type" in c.lower()), None)
        bsize_col = next((c for c in df_raw.columns if "ball_size" in c.lower()), None)
        cond_col = next((c for c in df_raw.columns if "cond" in c.lower() or "wet" in c.lower() or "dry" in c.lower()), None)

        if not all([vel_col, name_col, time_col, type_col]):
            st.error("❌ Missing required columns! Need: player_name, Minute, ball_velocity_mps, impact_type")
            return

        results = []
        errors = []
        for idx, row in df_raw.iterrows():
            try:
                itype = str(row[type_col]).lower().strip()
                vel = float(row[vel_col])
                btype = str(row[btype_col]).upper().strip() if btype_col else "A1"
                bsize = str(row[bsize_col]).strip() if bsize_col else "Size 5 (Elite Adult)"
                cond = str(row[cond_col]).lower().strip() if cond_col else "dry"
                calc = calculate_impact(vel, itype, btype, bsize, cond)
                if calc:
                    calc["player_name"] = str(row[name_col])
                    calc["Minute"] = float(row[time_col])
                    results.append(calc)
                else:
                    errors.append(f"Row {idx+1}: Invalid values")
            except Exception as e:
                errors.append(f"Row {idx+1}: {str(e)}")

        if errors:
            st.warning(f"⚠️ {len(errors)} rows skipped — check format")
        if results:
            df_calc = pd.DataFrame(results)
            st.success(f"✅ {len(df_calc)} impacts calculated")

            head_df = df_calc[df_calc["impact_type"] == "heading"].reset_index(drop=True)
            kick_df = df_calc[df_calc["impact_type"] == "kick"].reset_index(drop=True)

            if len(head_df) > 0:
                st.subheader("🧠 Heading — Cumulative Brain Load & PPSI90")
                st.dataframe(head_df, use_container_width=True)
                fig_head, _ = generate_head_chart(head_df)
                st.plotly_chart(fig_head, use_container_width=True)
                c1, c2 = st.columns(2)
                with c1:
                    st.download_button("📥 Download Heading Data (CSV)", head_df.to_csv(index=False), "heading_ledger.csv", use_container_width=True)
                with c2:
                    st.markdown(get_html_download_link(fig_head, f"{match_teams.replace(' ','_')}_Heading.html"), unsafe_allow_html=True)

            if len(kick_df) > 0:
                st.subheader("⚽ Kick — Peak Shot Power")
                st.dataframe(kick_df, use_container_width=True)
                fig_kick, _ = generate_kick_chart(kick_df)
                st.plotly_chart(fig_kick, use_container_width=True)
                c3, c4 = st.columns(2)
                with c3:
                    st.download_button("📥 Download Kick Data (CSV)", kick_df.to_csv(index=False), "kick_ledger.csv", use_container_width=True)
                with c4:
                    st.markdown(get_html_download_link(fig_kick, f"{match_teams.replace(' ','_')}_Kick.html"), unsafe_allow_html=True)

    st.divider()

    # ─── METHOD 2: MANUAL INPUT ───────────────────────────────────────
    st.header("✍️ Method 2: Enter Impact Manually")
    with st.form("manual_entry_form"):
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            name = st.text_input("Player Name / ID")
            minute = st.number_input("Match Minute", min_value=0.0, max_value=120.0, step=1.0)
            impact_type = st.selectbox("Impact Type", ["heading", "kick"])
            ball_type = st.selectbox("Ball Type",
                ["A1 — Thermally Bonded Elite",
                 "B1 — Fuse-Welded Elite",
                 "C1 — Machine-Stitched Elite",
                 "D1 — Hand-Stitched Elite",
                 "E1 — Synthetic Moulded",
                 "F1 — Laceless Leather",
                 "G1 — Laced Leather"], index=0)
        with col_b:
            ball_size = st.selectbox("Ball Size",
                ["Size 5 (Elite Adult)",
                 "Size 4 (U12–U14)",
                 "Size 3 (U8–U10)"], index=0)
            velocity = st.number_input("Ball Velocity (m/s)", min_value=5.0, max_value=40.0, step=0.5, value=18.20)
            condition = st.selectbox("Match Condition",
                ["dry", "damp", "wet"], index=0)
        with col_c:
            st.markdown("<br>", unsafe_allow_html=True)
            st.info("✅ Moisture from Phillips Table 1 · Leather: pressure amplifies when wet")
            add_btn = st.form_submit_button("➕ Add to Ledger", type="primary", use_container_width=True)

        if add_btn:
            if not name:
                st.error("Enter Player Name")
            else:
                btype_id = ball_type.split(" — ")[0]
                calc = calculate_impact(velocity, impact_type, btype_id, ball_size, condition)
                if calc:
                    calc["player_name"] = name
                    calc["Minute"] = minute
                    st.session_state.entries.append(calc)
                    if impact_type == "heading":
                        note = f"💧 Uptake: {calc['Water_Uptake_pct']}%" if calc['condition'] != 'dry' else ""
                        st.success(f"✅ 🧠 {name} — {btype_id} · {velocity} m/s → {calc['Peak_to_Peak_Pressure_kPa']} kPa | Energy Index: {calc['Energy_Index_Pa2s']:,} Pa²·s | {calc['Brain_Load_Units_kPa_ms']} kPa·ms {note}")
                    else:
                        st.success(f"✅ ⚽ {name} — {btype_id} · {velocity} m/s → {calc['Peak_Power_kW']} kW | {calc['Performance_Category']}")
                else:
                    st.error("❌ Invalid input — check all fields")

    # ─── RESULTS LEDGER ───────────────────────────────────────────────
    if st.session_state.entries:
        st.divider()
        st.subheader(f"📊 Full Ledger — {len(st.session_state.entries)} Impact(s)")
        df_all = pd.DataFrame(st.session_state.entries)
        st.dataframe(df_all, use_container_width=True)

        head_entries = df_all[df_all["impact_type"] == "heading"].reset_index(drop=True)
        kick_entries = df_all[df_all["impact_type"] == "kick"].reset_index(drop=True)

        if len(head_entries) > 0:
            st.subheader("🧠 Heading — Cumulative Brain Load & PPSI90")
            fig_head, _ = generate_head_chart(head_entries)
            st.plotly_chart(fig_head, use_container_width=True)
            c1, c2 = st.columns(2)
            with c1:
                st.download_button("📥 Download Heading Data (CSV)", head_entries.to_csv(index=False), "manual_head_ledger.csv", use_container_width=True)
            with c2:
                st.markdown(get_html_download_link(fig_head, "Manual_Heading_Chart.html"), unsafe_allow_html=True)

        if len(kick_entries) > 0:
            st.subheader("⚽ Kick — Peak Shot Power")
            fig_kick, _ = generate_kick_chart(kick_entries)
            st.plotly_chart(fig_kick, use_container_width=True)
            c3, c4 = st.columns(2)
            with c3:
                st.download_button("📥 Download Kick Data (CSV)", kick_entries.to_csv(index=False), "manual_kick_ledger.csv", use_container_width=True)
            with c4:
                st.markdown(get_html_download_link(fig_kick, "Manual_Kick_Chart.html"), unsafe_allow_html=True)

        st.download_button("📥 Download ALL Combined Data (CSV)", df_all.to_csv(index=False), "full_combined_ledger.csv", type="secondary", use_container_width=True)

if __name__ == "__main__":
    run_application()