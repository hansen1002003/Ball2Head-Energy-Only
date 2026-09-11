"""
Ball2Head — Post-Match Squad Brain Health Ledger
==================================================
Investigational Research — Hansen Sominabo Kekom
Birmingham Newman University — Final Year Project

Calibration Source:
  Phillips, I. et al. (2026) — Pressure wave propagation from association
  football head collisions. Mean of A1/B1 elite match balls — FIFA 430g dry mass.

Core Methodology:
  • Kinetic Energy:       E = ½mv²
  • Peak Pressure:        P = k₁ × E      → k₁ = 1.19 kPa/J  (dry)
  • Wave Duration:        τ = k₂ × E      → k₂ = 0.067 ms/J (dry)
  • Brain Load Units:     BLU = P × τ     → DOUBLE-CALIBRATED metric
  • Wet Adjustment:       Damp ×1.10 | Wet Synthetic ×1.25

Risk Thresholds (Visual Guide):
  🟢 Low:       0–45    Brain Load Units
  🟡 Moderate: 45–90    Brain Load Units
  🔴 Elevated: 90–160   Brain Load Units

Version: 2.1 — CSV Batch + Manual Input + Unified Plotly Ledger
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import base64

# =============================================================================
# PHILLIPS CALIBRATION CONSTANTS — A1/B1 MEAN, FIFA 430g DRY MASS
# =============================================================================
class PhillipsCalibration:
    """
    Lab-calibrated constants from Phillips et al. (2026).
    Derived from mean values of A1 (thermally bonded) and B1 (fuse-welded)
    elite match balls, standardised to FIFA regulation mass.
    """
    # Ball mass — FIFA standard Size 5
    BALL_MASS_DRY_KG = 0.430
    
    # Dry calibration constants
    k1_KPA_PER_J_DRY = 1.19    # Peak pressure constant (kPa per Joule)
    k2_MS_PER_J_DRY = 0.067    # Wave duration constant (ms per Joule)
    
    # Environmental correction factors
    WET_FACTORS = {
        "dry": 1.00,
        "damp": 1.10,
        "wet_synthetic": 1.25
    }
    
    @classmethod
    def get_adjusted_constants(cls, match_condition: str = "dry") -> dict:
        """
        Apply environmental correction factors to base dry constants.
        Returns k₁, k₂, and applied factor for audit trail.
        """
        condition = str(match_condition).lower().strip()
        factor = cls.WET_FACTORS.get(condition, 1.00)
        
        return {
            "kPa_per_J": round(cls.k1_KPA_PER_J_DRY * factor, 4),
            "ms_per_J": round(cls.k2_MS_PER_J_DRY * factor, 5),
            "wet_factor_applied": factor
        }

# =============================================================================
# SINGLE IMPACT CALCULATION ENGINE
# =============================================================================
def calculate_single_impact(
    velocity_mps: float,
    match_condition: str = "dry"
) -> dict | None:
    """
    Calculate all heading load metrics from ball velocity at impact.
    
    Physics Chain:
      Velocity → Kinetic Energy → Calibrated Pressure & Duration → Brain Load
    
    Returns complete audit trail including all intermediate values.
    """
    try:
        velocity = float(velocity_mps)
        if velocity <= 0:
            return None
    except (ValueError, TypeError):
        return None
    
    # Step 1: Calculate kinetic energy — E = ½mv²
    joules = 0.5 * PhillipsCalibration.BALL_MASS_DRY_KG * (velocity ** 2)
    
    # Step 2: Get condition-adjusted calibration constants
    cal = PhillipsCalibration.get_adjusted_constants(match_condition)
    
    # Step 3: Calculate peak pressure and wave duration
    total_kpa = cal["kPa_per_J"] * joules
    total_ms = cal["ms_per_J"] * joules
    
    # Step 4: Brain Load Units = kPa × ms — DOUBLE-CALIBRATED EXPOSURE METRIC
    brain_load_units = total_kpa * total_ms
    
    # Step 5: Assign load category from cumulative threshold guide
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
        "kPa_per_J": cal["kPa_per_J"],
        "ms_per_J": cal["ms_per_J"],
        "Total_kPa": round(total_kpa, 2),
        "Total_ms": round(total_ms, 3),
        "Brain_Load_Units": round(brain_load_units, 4),
        "Load_Category": category
    }

# =============================================================================
# UNIFIED PLOTLY LEDGER GENERATOR
# =============================================================================
def generate_brain_health_ledger(input_dataframe: pd.DataFrame) -> tuple:
    """
    Produce interactive squad ledger — identical output whether sourced from
    batch CSV upload or manual single-impact entry.
    
    Calculates:
      • Player header count & display label
      • Chronological sorting per player
      • Cumulative brain load timeline
      • Plotly chart with clinical risk bands & audit-ready hover tooltips
    
    Returns: (plotly_figure, enriched_dataframe)
    """
    df = input_dataframe.copy()
    
    # Create standardised player label with header count
    header_counts = df["player_name"].value_counts().to_dict()
    df["Header_Count"] = df["player_name"].map(header_counts)
    df["Player_Label"] = df["player_name"] + " (" + df["Header_Count"].astype(str) + " Headers)"
    
    # Sort chronologically so cumulative load progresses correctly
    df = df.sort_values(["Player_Label", "Minute"])
    
    # Compute cumulative brain load — tracks exposure progression per player
    df["Cumulative_Brain_Load"] = df.groupby("Player_Label")[
        "Brain_Load_Units"
    ].cumsum().round(2)
    
    # Generate interactive line chart — standardised visual format
    fig = px.line(
        df,
        x="Minute",
        y="Cumulative_Brain_Load",
        color="Player_Label",
        markers=True,
        title=(
            "<b>POST-MATCH SQUAD HEAD-LOAD LEDGER</b>"
            "<br><sup>Metrics Normalised via Lab-Calibrated Inverse Core Constants — "
            "Phillips et al. (2026)</sup>"
        ),
        labels={
            "Minute": "Match Timeline (Minutes)",
            "Cumulative_Brain_Load": "Cumulative Brain Load Index",
            "Player_Label": "Player Squad Profiles",
        },
        hover_data={
            "Minute": True,
            "Cumulative_Brain_Load": ": .2f",
            "Joules": ": .1f J",
            "kPa_per_J": ": .2f kPa/J",
            "ms_per_J": ": .3f ms/J",
            "Total_kPa": ": .1f kPa",
        },
    )
    
    # Add clinical risk threshold bands — visual guide for medics
    fig.add_hrect(y0=0, y1=45, fillcolor="#2ecc71", opacity=0.06, layer="below", line_width=0)
    fig.add_hrect(y0=45, y1=90, fillcolor="#f1c40f", opacity=0.06, layer="below", line_width=0)
    fig.add_hrect(y0=90, y1=160, fillcolor="#e74c3c", opacity=0.06, layer="below", line_width=0)
    
    # Professional dashboard styling — consistent clinical presentation
    fig.update_layout(
        xaxis=dict(range=[0, 95], dtick=10, gridcolor="rgba(0,0,0,0.05)"),
        yaxis=dict(range=[0, 160], gridcolor="rgba(0,0,0,0.05)"),
        plot_bgcolor="white",
        hovermode="closest",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        margin=dict(l=50, r=50, t=80, b=50),
        height=600,
    )
    fig.update_traces(line=dict(width=3.5), marker=dict(size=8))
    
    return fig, df

# =============================================================================
# STREAMLIT APPLICATION — MAIN INTERFACE
# =============================================================================
def run_application():
    """
    Unified interface supporting TWO input methods:
      1. Batch CSV Upload → process entire match event log
      2. Manual Entry → add individual impacts, build ledger incrementally
    
    BOTH methods produce IDENTICAL calculations, chart, and exports.
    """
    st.set_page_config(
        page_title="Ball2Head — Brain Health Ledger",
        layout="wide"
    )
    
    # Persist session state — accumulate manual entries
    if "manual_entries" not in st.session_state:
        st.session_state.manual_entries = []
    
    # ─── PAGE HEADER ──────────────────────────────────────────────────────
    st.title("⚽🧠 Post-Match Squad Brain Health Ledger")
    st.subheader(
        "Double-Calibrated: kPa × ms | Phillips et al. (2026) — "
        "A1/B1 Mean — FIFA 430g"
    )
    
    with st.expander("📋 Methodology, Formula & Calibration Source"):
        st.markdown("""
        **Calibration Source:** Phillips, I. et al. (2026). Pressure wave propagation
        from association football head collisions. Mean of A1/B1 elite match balls,
        standardised to FIFA 430 g dry mass.
        
        **Physics Chain:**
        - Kinetic Energy: $E = \\frac{1}{2}mv^2$
        - Peak Pressure: $P = k_1 \\times E$  → **k₁ = 1.19 kPa/J**
        - Wave Duration: $τ = k_2 \\times E$  → **k₂ = 0.067 ms/J**
        - **Brain Load Units = P × τ** → Uses BOTH constants — complete exposure metric
        
        **Risk Thresholds (Visual Guide):**
        🟢 Low: 0–45 | 🟡 Moderate: 45–90 | 🔴 Elevated: 90–160
        """)
    
    # ─── MATCH CONTEXT ───────────────────────────────────────────────────
    st.header("📋 Match Information")
    col_match1, col_match2 = st.columns(2)
    with col_match1:
        match_teams = st.text_input("Match", value="Team A vs Team B")
    with col_match2:
        match_date = st.text_input("Date", value=pd.Timestamp.now().strftime("%Y-%m-%d"))
    
    st.divider()
    
    # ─── INPUT METHOD 1: BATCH CSV UPLOAD ────────────────────────────────
    st.header("📁 Method 1: Upload Match Events CSV")
    st.info(
        "Required columns: `player_name`, `Minute` (match time in minutes), "
        "`ball_velocity_mps` (speed at impact). Optional: `condition`."
    )
    
    uploaded_file = st.file_uploader(
        "Upload Match Events CSV File",
        type=["csv"],
        key="csv_uploader"
    )
    
    if uploaded_file:
        df_raw = pd.read_csv(uploaded_file)
        st.write(f"📋 Uploaded {len(df_raw)} rows × {len(df_raw.columns)} columns")
        
        # Auto-detect required columns
        vel_col = next((c for c in df_raw.columns if str(c).lower() in [
            "velocity", "ball_velocity_mps", "speed", "ballvelocity"
        ]), None)
        name_col = next((c for c in df_raw.columns if str(c).lower() in [
            "player_name", "playername", "player", "name"
        ]), None)
        time_col = next((c for c in df_raw.columns if str(c).lower() in [
            "minute", "event_minute", "time", "timestamp"
        ]), None)
        cond_col = next((c for c in df_raw.columns if str(c).lower() in [
            "condition", "weather", "match_condition"
        ]), None)
        
        if not all([vel_col, name_col, time_col]):
            st.error("❌ CSV must contain columns: player_name, Minute, ball_velocity_mps")
            return
        
        # Process every row through calculation engine
        results = []
        for _, row in df_raw.iterrows():
            velocity = float(row[vel_col])
            player_name = str(row[name_col])
            minute = float(row[time_col])
            condition = str(row[cond_col]).lower().strip() if cond_col else "dry"
            if condition not in ["dry", "damp", "wet_synthetic"]:
                condition = "dry"
            
            calc = calculate_single_impact(velocity, condition)
            if calc:
                calc["player_name"] = player_name
                calc["Minute"] = minute
                results.append(calc)
        
        if not results:
            st.error("❌ No valid calculations — check velocity values")
            return
        
        # Generate and display standard ledger
        df_calc = pd.DataFrame(results)
        st.success(f"✅ Calculated {len(df_calc)} header impacts across {df_calc['player_name'].nunique()} players")
        
        fig, df_final = generate_brain_health_ledger(df_calc)
        st.plotly_chart(fig, use_container_width=True)
        
        # Export options
        csv_download = df_final.to_csv(index=False)
        st.download_button(
            "📥 Download Calculated CSV",
            csv_download,
            f"BrainHealth_Ledger_{match_date}.csv",
            "text/csv",
            type="primary"
        )
        
        html_ledger = fig.to_html()
        b64_html = base64.b64encode(html_ledger.encode()).decode()
        download_link = (
            f'<a href="data:text/html;charset=utf-8;base64,{b64_html}" '
            f'download="BrainHealth_Interactive_{match_date}.html">'
            f'📄 Download Full Interactive HTML Ledger</a>'
        )
        st.markdown(download_link, unsafe_allow_html=True)
        
        with st.expander("📋 View Complete Calculation Table"):
            st.dataframe(df_final, use_container_width=True)
    
    st.divider()
    
    # ─── INPUT METHOD 2: MANUAL SINGLE IMPACT ENTRY ──────────────────────
    st.header("✍️ Method 2: Enter Header Impacts Manually")
    st.info(
        "Add headers one at a time — ledger builds automatically. "
        "Same calculations, same chart, same export formats."
    )
    
    with st.form("manual_entry_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            input_name = st.text_input("Player Name / ID", placeholder="e.g. VVD_04")
            input_minute = st.number_input("Match Minute", min_value=0.0, max_value=120.0, step=0.5)
        with col2:
            input_velocity = st.number_input(
                "Ball Velocity (m/s)",
                min_value=5.0, max_value=35.0, step=0.5, value=18.0
            )
            input_condition = st.selectbox(
                "Match Condition",
                options=["dry", "damp", "wet_synthetic"],
                index=0
            )
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            submit_button = st.form_submit_button(
                label="➕ Add Header Impact to Ledger",
                type="primary",
                use_container_width=True
            )
        
        if submit_button:
            if not input_name:
                st.error("❌ Please enter a Player Name / ID")
            else:
                calculation = calculate_single_impact(input_velocity, input_condition)
                if calculation:
                    calculation["player_name"] = input_name
                    calculation["Minute"] = input_minute
                    st.session_state.manual_entries.append(calculation)
                    st.success(
                        f"✅ Added: {input_name} — {input_velocity} m/s → "
                        f"{calculation['Brain_Load_Units']} BLU"
                    )
                else:
                    st.error("❌ Invalid velocity — check value entered")
    
    # ─── DISPLAY MANUAL ENTRIES & GENERATE LEDGER ────────────────────────
    if st.session_state.manual_entries:
        st.divider()
        st.subheader(f"📊 Ledger — {len(st.session_state.manual_entries)} Impact(s) Entered")
        
        manual_df = pd.DataFrame(st.session_state.manual_entries)
        ledger_fig, ledger_df = generate_brain_health_ledger(manual_df)
        
        st.plotly_chart(ledger_fig, use_container_width=True)
        
        # Manual entry exports
        manual_csv = ledger_df.to_csv(index=False)
        st.download_button(
            "📥 Download Manual Ledger CSV",
            manual_csv,
            f"Manual_Ledger_{match_date}.csv",
            "text/csv",
            type="primary"
        )
        
        manual_html = ledger_fig.to_html()
        b64_manual = base64.b64encode(manual_html.encode()).decode()
        manual_link = (
            f'<a href="data:text/html;charset=utf-8;base64,{b64_manual}" '
            f'download="Manual_Interactive_Ledger_{match_date}.html">'
            f'📄 Download Manual Interactive HTML Ledger</a>'
        )
        st.markdown(manual_link, unsafe_allow_html=True)
        
        with st.expander("📋 View Manual Calculation Table"):
            st.dataframe(ledger_df, use_container_width=True)
        
        # Clear button
        if st.button("🗑️ Clear All Manual Entries", type="secondary"):
            st.session_state.manual_entries = []
            st.rerun()
    
    st.divider()
    st.caption(
        "Ball2Head — Investigational Research | Phillips et al. (2026) | "
        "Double-Calibrated: kPa × ms | A1/B1 Mean — FIFA 430g"
    )

# =============================================================================
# RUN APPLICATION
# =============================================================================
if __name__ == "__main__":
    run_application()