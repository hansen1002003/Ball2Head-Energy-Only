"""
Ball2Head — Post-Match Squad Brain Health Ledger
==================================================
Investigational Research — Hansen Sominabo Kekom
Birmingham Newman University — Final Year Project

Calibration Source:
  Phillips, I. et al. (2026) — Pressure wave propagation from association
  football head collisions. **Table values from paper — C1 @ 18 m/s = 5.7 kPa**

Ball Type — C1 Elite Machine-Stitched (Primary Standard):
  • Peak Pressure @ 18 m/s:  5.7 kPa   → k₁ = 0.0818 kPa/J
  • Rise Time @ 18 m/s:      80 μs      → k₂ = 0.00115 ms/J
  • Mass: 0.430 kg (FIFA standard)

Core Methodology:
  • Kinetic Energy:       E = ½mv²
  • Peak Pressure:        P = k₁ × E   → k₁ = 0.0818 kPa/J  (C1 — from paper)
  • Wave Duration:        τ = k₂ × E   → k₂ = 0.00115 ms/J  (C1 — from paper)
  • Brain Load Units:     BLU = P × τ
  • Wet Adjustment:       Damp ×1.10 | Wet Synthetic ×1.25

Risk Thresholds:  🟢 0–45 | 🟡 45–90 | 🔴 90–160 Brain Load Units
Version: 2.5.0 — ✅ CORRECTED to 5.7 kPa @ 18 m/s (C1 — Direct from Paper Table)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import base64

# =============================================================================
# PHILLIPS CALIBRATION — C1 ELITE, EXACT VALUES FROM PAPER TABLE
# =============================================================================
class PhillipsCalibration:
    BALL_MASS_DRY_KG = 0.430  # FIFA standard mass
    
    # === C1 — ELITE MACHINE-STITCHED — PRIMARY STANDARD ===
    # Values DIRECTLY from Phillips et al. (2026) — Table: C1 @ 18 m/s (Dry)
    # Peak Pressure: 5.7 kPa | Rise Time: 80 μs
    k1_KPA_PER_J_DRY = 0.0818   # = 5.7 kPa ÷ 69.66 J  ✅ Paper-validated
    k2_MS_PER_J_DRY = 0.00115   # = 0.080 ms ÷ 69.66 J ✅ Paper-validated
    
    WET_FACTORS = {"dry": 1.00, "damp": 1.10, "wet_synthetic": 1.25}
    
    @classmethod
    def get_adjusted_constants(cls, match_condition: str = "dry") -> dict:
        condition = str(match_condition).lower().strip()
        factor = cls.WET_FACTORS.get(condition, 1.00)
        return {
            "kPa_per_J": round(cls.k1_KPA_PER_J_DRY * factor, 5),
            "ms_per_J": round(cls.k2_MS_PER_J_DRY * factor, 6),
            "wet_factor_applied": factor
        }

# =============================================================================
# SINGLE IMPACT CALCULATION — CORRECTED C1 VALUES
# =============================================================================
def calculate_single_impact(velocity_mps: float, match_condition: str = "dry") -> dict | None:
    try:
        velocity = float(velocity_mps)
        if velocity <= 0:
            return None
    except:
        return None
    
    # Step 1: Kinetic Energy — FIFA standard mass
    joules = 0.5 * PhillipsCalibration.BALL_MASS_DRY_KG * (velocity ** 2)
    
    # Step 2: Get calibration constants (C1-specific, wet-adjusted)
    cal = PhillipsCalibration.get_adjusted_constants(match_condition)
    
    # Step 3: TRUE absolute values — matching Phillips lab measurements
    total_kpa = cal["kPa_per_J"] * joules
    total_ms = cal["ms_per_J"] * joules
    
    # Step 4: Combined Brain Load Index
    brain_load_units = total_kpa * total_ms
    
    # Risk category
    if brain_load_units < 45:
        category = "LOW"
    elif brain_load_units < 90:
        category = "MODERATE"
    elif brain_load_units < 160:
        category = "HIGH"
    else:
        category = "ELEVATED"
    
    return {
        "ball_velocity_mps": round(velocity, 2),
        "condition": match_condition,
        "Joules": round(joules, 2),
        "Total_kPa": round(total_kpa, 2),       # ✅ Matches paper: 5.7 kPa @ 18 m/s
        "Total_ms": round(total_ms, 3),          # ✅ Matches paper: 0.080 ms @ 18 m/s
        "Brain_Load_Units": round(brain_load_units, 4),
        "Load_Category": category
    }

# =============================================================================
# CHART GENERATOR
# =============================================================================
def generate_brain_health_ledger(input_dataframe: pd.DataFrame) -> tuple:
    df = input_dataframe.copy()
    
    header_counts = df["player_name"].value_counts().to_dict()
    df["Header_Count"] = df["player_name"].map(header_counts)
    df["Player_Label"] = df["player_name"] + " (" + df["Header_Count"].astype(str) + " Headers)"
    
    df = df.sort_values(["Player_Label", "Minute"])
    df["Cumulative_Brain_Load"] = df.groupby("Player_Label")["Brain_Load_Units"].cumsum().round(2)
    
    max_load = df["Cumulative_Brain_Load"].max()
    y_max = max(160, round(max_load * 1.1, -1))
    x_max = max(95, round(df["Minute"].max() + 5, -1))
    
    fig = px.line(
        df, x="Minute", y="Cumulative_Brain_Load", color="Player_Label", markers=True,
        title="<b>POST-MATCH SQUAD HEAD-LOAD LEDGER</b><br><sup>C1 Elite Machine-Stitched — Phillips et al. (2026) | 5.7 kPa @ 18 m/s</sup>",
        labels={"Minute": "Match Timeline (Minutes)", "Cumulative_Brain_Load": "Cumulative Brain Load Index"},
        hover_data={"Minute": True, "Cumulative_Brain_Load": ": .2f", "Joules": ": .1f J", "Total_kPa": ": .1f kPa", "Total_ms": ": .3f ms"}
    )
    
    fig.add_hrect(y0=0, y1=45, fillcolor="#2ecc71", opacity=0.06, layer="below", line_width=0)
    fig.add_hrect(y0=45, y1=90, fillcolor="#f1c40f", opacity=0.06, layer="below", line_width=0)
    fig.add_hrect(y0=90, y1=160, fillcolor="#e74c3c", opacity=0.06, layer="below", line_width=0)
    
    fig.update_layout(xaxis=dict(range=[0, x_max], dtick=10), yaxis=dict(range=[0, y_max]), height=600)
    fig.update_traces(line=dict(width=3.5), marker=dict(size=8))
    return fig, df

# =============================================================================
# HTML DOWNLOAD
# =============================================================================
def get_html_download_link(fig, filename="Post-Match_Squad_Head-Ledger.html"):
    html_content = fig.to_html(include_plotlyjs="cdn", full_html=True)
    b64 = base64.b64encode(html_content.encode()).decode()
    href = f'<a href="data:text/html;charset=utf-8;base64,{b64}" download="{filename}" style="display:inline-block; padding:0.5rem 1rem; color:#0c5460; background-color:#d1ecf1; border-radius:0.3rem; text-decoration:none; font-weight:500;">📄 Download Interactive HTML</a>'
    return href

# =============================================================================
# MAIN APPLICATION
# =============================================================================
def run_application():
    st.set_page_config(page_title="Ball2Head — Brain Health Ledger", layout="wide")
    if "manual_entries" not in st.session_state:
        st.session_state.manual_entries = []
    
    st.title("⚽🧠 Post-Match Squad Brain Health Ledger")
    st.subheader("C1 Elite Machine-Stitched — Phillips et al. (2026) | 5.7 kPa @ 18 m/s")
    
    with st.expander("📋 Methodology & Calibration Source"):
        st.markdown("""
        **Calibration Source:** Phillips, I. et al. (2026). Pressure wave propagation from association football head collisions.
        
        **C1 — Elite Machine-Stitched Match Ball (Dry):**
        - Peak-to-Peak Pressure @ 18 m/s: **5.7 kPa** ✅ (paper table)
        - Rise Time @ 18 m/s: **80 μs (0.080 ms)** ✅ (paper table)
        - PPSI₉₀: ~30 Pa²·s
        
        **Formula:** $E = ½mv²$ → $P = k₁·E$ → $τ = k₂·E$ → **BLU = P × τ**
        - k₁ = 0.0818 kPa/J  (derived from 5.7 kPa ÷ 69.66 J)
        - k₂ = 0.00115 ms/J (derived from 0.080 ms ÷ 69.66 J)
        """)
    
    st.header("📋 Match Information")
    col1, col2 = st.columns(2)
    with col1:
        match_teams = st.text_input("Match", value="Team A vs Team B")
    with col2:
        match_date = st.text_input("Date", value=pd.Timestamp.now().strftime("%Y-%m-%d"))
    
    st.divider()
    
    # ─── METHOD 1: CSV UPLOAD ──────────────────────────────────────────
    st.header("📁 Method 1: Upload Match Events CSV")
    st.info("Columns: player_name, Minute, ball_velocity_mps | Optional: condition")
    
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    
    if uploaded_file:
        df_raw = pd.read_csv(uploaded_file)
        vel_col = next((c for c in df_raw.columns if "vel" in c.lower() or "speed" in c.lower()), None)
        name_col = next((c for c in df_raw.columns if "name" in c.lower() or "player" in c.lower()), None)
        time_col = next((c for c in df_raw.columns if "min" in c.lower() or "time" in c.lower()), None)
        cond_col = next((c for c in df_raw.columns if "cond" in c.lower()), None)
        
        if not all([vel_col, name_col, time_col]):
            st.error("Need columns: player_name, Minute, ball_velocity_mps")
            return
        
        results = []
        for _, row in df_raw.iterrows():
            cond = str(row[cond_col]).lower() if cond_col and pd.notna(row[cond_col]) else "dry"
            calc = calculate_single_impact(float(row[vel_col]), cond)
            if calc:
                calc["player_name"] = str(row[name_col])
                calc["Minute"] = float(row[time_col])
                results.append(calc)
        
        if results:
            df_calc = pd.DataFrame(results)
            fig, df_final = generate_brain_health_ledger(df_calc)
            st.success(f"✅ {len(df_calc)} impacts calculated")
            st.plotly_chart(fig, use_container_width=True)
            st.download_button("📥 Download CSV", df_final.to_csv(index=False), "ledger.csv", type="primary")
            st.markdown(get_html_download_link(fig, f"{match_teams.replace(' ','_')}_Head-Ledger.html"), unsafe_allow_html=True)
    
    st.divider()
    
    # ─── METHOD 2: MANUAL INPUT ───────────────────────────────────────
    st.header("✍️ Method 2: Enter Header Impacts Manually")
    
    with st.form("manual_entry_form"):
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            name = st.text_input("Player Name / ID")
            minute = st.number_input("Match Minute", min_value=0.0, max_value=120.0, step=1.0)
        with col_b:
            velocity = st.number_input("Ball Velocity (m/s)", min_value=5.0, max_value=35.0, step=0.5, value=18.0)
            condition = st.selectbox("Match Condition", ["dry", "damp", "wet_synthetic"])
        with col_c:
            st.markdown("<br>", unsafe_allow_html=True)
            add_btn = st.form_submit_button("➕ Add to Ledger", type="primary", use_container_width=True)
        
        if add_btn:
            if not name:
                st.error("Enter Player Name")
            else:
                calc = calculate_single_impact(velocity, condition)
                if calc:
                    calc["player_name"] = name
                    calc["Minute"] = minute
                    st.session_state.manual_entries.append(calc)
                    st.success(f"✅ Added: {name} — {velocity} m/s → {calc['Total_kPa']} kPa | {calc['Brain_Load_Units']} BLU")
    
    # ─── DISPLAY MANUAL LEDGER ────────────────────────────────────────
    if st.session_state.manual_entries:
        st.divider()
        st.subheader(f"📊 Ledger — {len(st.session_state.manual_entries)} Impact(s) Entered")
        df_manual = pd.DataFrame(st.session_state.manual_entries)
        st.dataframe(df_manual, use_container_width=True)
        
        if len(df_manual) >= 1:
            fig, df_final = generate_brain_health_ledger(df_manual)
            st.plotly_chart(fig, use_container_width=True)
            st.download_button("📥 Download Full Ledger CSV", df_final.to_csv(index=False), "manual_ledger.csv", type="primary")
            st.markdown(get_html_download_link(fig, "Manual_Head-Ledger.html"), unsafe_allow_html=True)

# =============================================================================
# RUN APPLICATION
# =============================================================================
if __name__ == "__main__":
    run_application()