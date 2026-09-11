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
  • Peak Pressure:        P = k₁ × E        → k₁ = 1.19 kPa/J  (dry)
  • Wave Duration:        τ = k₂ × E        → k₂ = 0.067 ms/J (dry)
  • Brain Load Units:     BLU = P × τ       → DOUBLE-CALIBRATED metric
  • Wet Adjustment:       Damp ×1.10 | Wet Synthetic ×1.25

Risk Thresholds (Visual Guide):
  🟢 Low:       0–45    Brain Load Units
  🟡 Moderate:  45–90   Brain Load Units
  🔴 Elevated:  90–160  Brain Load Units

Version: 2.2.1 — FIXED HTML Export + CSV Batch + Manual Input
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import base64

# =============================================================================
# PHILLIPS CALIBRATION — A1/B1 MEAN, FIFA 430g
# =============================================================================
class PhillipsCalibration:
    BALL_MASS_DRY_KG = 0.430
    k1_KPA_PER_J_DRY = 1.19
    k2_MS_PER_J_DRY = 0.067
    WET_FACTORS = {"dry": 1.00, "damp": 1.10, "wet_synthetic": 1.25}
    
    @classmethod
    def get_adjusted_constants(cls, match_condition: str = "dry") -> dict:
        condition = str(match_condition).lower().strip()
        factor = cls.WET_FACTORS.get(condition, 1.00)
        return {
            "kPa_per_J": round(cls.k1_KPA_PER_J_DRY * factor, 4),
            "ms_per_J": round(cls.k2_MS_PER_J_DRY * factor, 5),
            "wet_factor_applied": factor
        }

# =============================================================================
# SINGLE IMPACT CALCULATION
# =============================================================================
def calculate_single_impact(velocity_mps: float, match_condition: str = "dry") -> dict | None:
    try:
        velocity = float(velocity_mps)
        if velocity <= 0:
            return None
    except:
        return None
    
    joules = 0.5 * PhillipsCalibration.BALL_MASS_DRY_KG * (velocity ** 2)
    cal = PhillipsCalibration.get_adjusted_constants(match_condition)
    total_kpa = cal["kPa_per_J"] * joules
    total_ms = cal["ms_per_J"] * joules
    brain_load_units = total_kpa * total_ms
    
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
# ✅ CHART GENERATOR — AUTO-SCALES TO DATA
# =============================================================================
def generate_brain_health_ledger(input_dataframe: pd.DataFrame) -> tuple:
    df = input_dataframe.copy()
    
    header_counts = df["player_name"].value_counts().to_dict()
    df["Header_Count"] = df["player_name"].map(header_counts)
    df["Player_Label"] = df["player_name"] + " (" + df["Header_Count"].astype(str) + " Headers)"
    
    df = df.sort_values(["Player_Label", "Minute"])
    
    df["Cumulative_Brain_Load"] = df.groupby("Player_Label")[
        "Brain_Load_Units"
    ].cumsum().round(2)
    
    max_load = df["Cumulative_Brain_Load"].max()
    y_max = max(160, round(max_load * 1.1, -1))
    x_max = max(95, round(df["Minute"].max() + 5, -1))
    
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
    
    fig.add_hrect(y0=0, y1=45, fillcolor="#2ecc71", opacity=0.06, layer="below", line_width=0)
    fig.add_hrect(y0=45, y1=90, fillcolor="#f1c40f", opacity=0.06, layer="below", line_width=0)
    fig.add_hrect(y0=90, y1=160, fillcolor="#e74c3c", opacity=0.06, layer="below", line_width=0)
    
    fig.update_layout(
        xaxis=dict(range=[0, x_max], dtick=10, gridcolor="rgba(0,0,0,0.05)"),
        yaxis=dict(range=[0, y_max], gridcolor="rgba(0,0,0,0.05)"),
        plot_bgcolor="white",
        hovermode="closest",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        margin=dict(l=50, r=50, t=80, b=50),
        height=600,
    )
    fig.update_traces(line=dict(width=3.5), marker=dict(size=8))
    
    return fig, df

# =============================================================================
# ✅ FIXED HTML DOWNLOAD — no encoding argument
# =============================================================================
def get_html_download_link(fig, filename="Post-Match_Squad_Head-Ledger.html"):
    """Convert Plotly figure to downloadable interactive HTML file — FIXED"""
    html_content = fig.to_html(include_plotlyjs="cdn", full_html=True)
    b64 = base64.b64encode(html_content.encode()).decode()
    href = f'<a href="data:text/html;charset=utf-8;base64,{b64}" download="{filename}" style="display:inline-block; padding:0.5rem 1rem; color:#0c5460; background-color:#d1ecf1; border-radius:0.3rem; text-decoration:none; font-weight:500;">📄 Download Interactive HTML — Post-Match Head-Ledger Graph</a>'
    return href

# =============================================================================
# MAIN APPLICATION
# =============================================================================
def run_application():
    st.set_page_config(page_title="Ball2Head — Brain Health Ledger", layout="wide")
    
    if "manual_entries" not in st.session_state:
        st.session_state.manual_entries = []
    
    st.title("⚽🧠 Post-Match Squad Brain Health Ledger")
    st.subheader(
        "Double-Calibrated: kPa × ms | Phillips et al. (2026) — "
        "A1/B1 Mean — FIFA 430g"
    )
    
    with st.expander("📋 Methodology, Formula & Calibration Source"):
        st.markdown("""
        **Calibration Source:** Phillips, I. et al. (2026). Pressure wave propagation
        from association football head collisions. Mean of A1/B1 elite match balls.
        
        **Formula:**
        - $E = ½mv²$ → $P = k₁·E$ → $τ = k₂·E$ → **BLU = P × τ**
        - Risk Zones: 🟢 0–45 | 🟡 45–90 | 🔴 90–160
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
            calc = calculate_single_impact(
                float(row[vel_col]),
                str(row[cond_col]).lower() if cond_col else "dry"
            )
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
            velocity = st.number_input("Ball Velocity (m/s)", min_value=5.0, max_value=35.0, step=0.5, value=15.0)
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
                    st.success(f"✅ Added: {name} — {velocity} m/s → {calc['Brain_Load_Units']} BLU")
    
    # ─── DISPLAY MANUAL LEDGER ────────────────────────────────────────
    if st.session_state.manual_entries:
        st.divider()
        st.subheader(f"📊 Ledger — {len(st.session_state.manual_entries)} Impact(s) Entered")
        
        manual_df = pd.DataFrame(st.session_state.manual_entries)
        fig, ledger_df = generate_brain_health_ledger(manual_df)
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.download_button("📥 Download CSV", ledger_df.to_csv(index=False), "manual_ledger.csv", type="primary")
        st.markdown(get_html_download_link(fig, "Manual_Head-Ledger.html"), unsafe_allow_html=True)
        
        with st.expander("📋 View Data Table"):
            st.dataframe(ledger_df, use_container_width=True)
        
        if st.button("🗑️ Clear All Entries"):
            st.session_state.manual_entries = []
            st.rerun()
    
    st.divider()
    st.caption("Ball2Head | Phillips et al. (2026) | Double-Calibrated: kPa × ms")

if __name__ == "__main__":
    run_application()