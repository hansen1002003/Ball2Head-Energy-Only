"""
Ball2Head — Post-Match Squad Brain Health Ledger
==================================================
Calibration: Phillips et al. (2026) — A1/B1 Mean — FIFA 430g
Brain Load Index = kPa × ms  (BOTH k₁ AND k₂ — double-calibrated)
Green/Amber/Red Thresholds: 0–45 / 45–90 / 90–160
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import base64

# =============================================================================
# 📐 PHILLIPS CALIBRATION — YOUR CONSTANTS
# =============================================================================
class Calibration:
    BALL_MASS_DRY_KG = 0.430
    DRY_k1_KPA_PER_J = 1.19   # kPa/J — Phillips A1/B1 Mean
    DRY_k2_MS_PER_J = 0.067   # ms/J — Phillips A1/B1 Mean
    
    WET_FACTORS = {"dry": 1.00, "damp": 1.10, "wet_synthetic": 1.25}
    
    @classmethod
    def get_constants(cls, condition="dry"):
        cond = str(condition).lower().strip()
        f = cls.WET_FACTORS.get(cond, 1.00)
        return {
            "kPa_per_J": round(cls.DRY_k1_KPA_PER_J * f, 4),
            "ms_per_J": round(cls.DRY_k2_MS_PER_J * f, 5),
            "factor": f
        }

# =============================================================================
# 🧮 CALCULATION ENGINE — PER IMPACT
# =============================================================================
def calculate_impact(velocity_mps, condition="dry"):
    """From velocity → Joules → kPa/J & ms/J → Total kPa & ms → Brain Load Units"""
    try:
        v = float(velocity_mps)
        if v <= 0:
            return None
    except:
        return None
    
    # Step 1: Kinetic Energy E = ½mv²
    joules = 0.5 * Calibration.BALL_MASS_DRY_KG * (v ** 2)
    
    # Step 2: Get calibrated constants
    c = Calibration.get_constants(condition)
    kpa_per_j = c["kPa_per_J"]
    ms_per_j = c["ms_per_J"]
    
    # Step 3: Total Pressure & Duration for THIS impact
    total_kpa = kpa_per_j * joules
    total_ms = ms_per_j * joules  # Already in ms since k₂ = ms/J
    
    # Step 4: BRAIN LOAD UNITS = kPa × ms  ← DOUBLE CALIBRATED!
    brain_load_units = total_kpa * total_ms
    
    return {
        "ball_velocity_mps": round(v, 2),
        "condition": condition,
        "Joules": round(joules, 2),
        "kPa_per_J": round(kpa_per_j, 4),
        "ms_per_J": round(ms_per_j, 5),
        "Total_kPa": round(total_kpa, 2),
        "Total_ms": round(total_ms, 3),
        "Brain_Load_Units": round(brain_load_units, 4)
    }

# =============================================================================
# 📊 GENERATE PLOTLY LEDGER — EXACTLY THE FORMAT YOU LIKE
# =============================================================================
def generate_ledger_chart(df):
    """
    df must contain: player_id, player_name, Minute, Joules,
                     kPa_per_J, ms_per_J, Total_kPa, Total_ms, Brain_Load_Units
    """
    # Label: PlayerName (X Headers)
    header_counts = df["player_name"].value_counts().to_dict()
    df["Header_Count"] = df["player_name"].map(header_counts)
    df["Player_Label"] = df["player_name"] + " (" + df["Header_Count"].astype(str) + " Headers)"
    
    # Sort chronologically per player
    df = df.sort_values(["Player_Label", "Minute"])
    
    # Cumulative Brain Load Timeline
    df["Cumulative_Brain_Load"] = df.groupby("Player_Label")["Brain_Load_Units"].cumsum().round(2)
    
    # Generate Plotly Line Chart — EXACTLY THE STYLE
    fig = px.line(
        df,
        x="Minute",
        y="Cumulative_Brain_Load",
        color="Player_Label",
        markers=True,
        title="<b>POST-MATCH SQUAD HEAD-LOAD LEDGER</b><br><sup>Metrics Normalized via Lab-Calibrated Inverse Core Constants — Phillips et al. (2026)</sup>",
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
    
    # ⚠️ CLINICAL RISK THRESHOLDS — Green / Amber / Red
    fig.add_hrect(y0=0, y1=45, fillcolor="#2ecc71", opacity=0.06, layer="below", line_width=0)
    fig.add_hrect(y0=45, y1=90, fillcolor="#f1c40f", opacity=0.06, layer="below", line_width=0)
    fig.add_hrect(y0=90, y1=160, fillcolor="#e74c3c", opacity=0.06, layer="below", line_width=0)
    
    # Style — Elite Clinical Dashboard
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
# 🖥️ STREAMLIT INTERFACE
# =============================================================================
def run_app():
    st.set_page_config(page_title="Ball2Head — Brain Health Ledger", layout="wide")
    st.title("⚽🧠 Post-Match Squad Brain Health Ledger")
    st.subheader("Double-Calibrated: kPa × ms | Phillips et al. (2026) — A1/B1 Mean — FIFA 430g")
    
    with st.expander("📋 Methodology & Formula"):
        st.markdown("""
        **Calibration:** k₁ = 1.19 kPa/J | k₂ = 0.067 ms/J — A1/B1 Mean, FIFA 430g
        
        **Brain Load Units = Total kPa × Total ms**
        > Uses **BOTH** Phillips constants — Pressure MAGNITUDE × Wave DURATION
        > More accurate than pressure alone — captures COMPLETE exposure
        
        **Risk Thresholds (visual guide):**
        🟢 Green: 0–45 — Low
        🟡 Amber: 45–90 — Moderate
        🔴 Red: 90–160 — Elevated
        
        *Reference: Phillips et al. (2026) — Pressure wave propagation from association football head collisions*
        """)
    
    # Upload Section
    st.header("📁 Upload Match Data")
    st.info("Columns needed: `player_name`, `Minute` (match time), `ball_velocity_mps`, `condition` (optional)")
    
    match_teams = st.text_input("Match", value="Team A vs Team B")
    uploaded = st.file_uploader("Upload Match Events CSV", type=["csv"])
    
    if uploaded:
        df_raw = pd.read_csv(uploaded)
        st.write(f"📋 {len(df_raw)} rows uploaded")
        
        # Auto-detect columns
        vel_col = next((c for c in df_raw.columns if str(c).lower() in ["velocity", "ball_velocity_mps", "speed"]), None)
        name_col = next((c for c in df_raw.columns if str(c).lower() in ["player_name", "playername", "player"]), None)
        time_col = next((c for c in df_raw.columns if str(c).lower() in ["minute", "event_minute", "time"]), None)
        cond_col = next((c for c in df_raw.columns if str(c).lower() in ["condition", "weather"]), None)
        
        if not all([vel_col, name_col, time_col]):
            st.error("❌ Missing columns! Need: player_name, Minute, ball_velocity_mps")
            return
        
        # Calculate EVERY row
        results = []
        for _, row in df_raw.iterrows():
            vel = row[vel_col]
            name = row[name_col]
            minute = row[time_col]
            cond = str(row[cond_col]).lower().strip() if cond_col else "dry"
            if cond not in ["dry", "damp", "wet_synthetic"]: cond = "dry"
            
            calc = calculate_impact(vel, cond)
            if calc:
                calc["player_name"] = name
                calc["Minute"] = minute
                results.append(calc)
        
        if not results:
            st.error("❌ No valid data — check velocity values")
            return
        
        df_calc = pd.DataFrame(results)
        st.success(f"✅ Calculated {len(df_calc)} headers across {df_calc['player_name'].nunique()} players")
        
        # Generate Chart — EXACTLY THE STYLE
        fig, df_final = generate_ledger_chart(df_calc)
        st.plotly_chart(fig, use_container_width=True)
        
        # Download CSV
        csv = df_final.to_csv(index=False)
        st.download_button("📥 Download Calculated CSV", csv, "BrainHealth_Ledger.csv", "text/csv", type="primary")
        
        # Download Interactive HTML
        html_bytes = fig.to_html()
        b64 = base64.b64encode(html_bytes.encode()).decode()
        href = f'<a href="data:text/html;charset=utf-8;base64,{b64}" download="BrainHealth_Interactive.html">📄 Download Interactive HTML Ledger</a>'
        st.markdown(href, unsafe_allow_html=True)
        
        # Show data table
        with st.expander("📋 View Calculated Data Table"):
            st.dataframe(df_final, use_container_width=True)
    
    st.divider()
    st.caption("Ball2Head | Phillips et al. (2026) | Double-Calibrated: kPa × ms | A1/B1 Mean — FIFA 430g")

if __name__ == "__main__":
    run_app()