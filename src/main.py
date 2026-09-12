"""
Ball2Head — Dual-Use Impact Engine
====================================
Investigational Research — Hansen Sominabo Kekom
Birmingham Newman University — Final Year Project

Calibration Sources:
  🧠 HEADING — Phillips, I. et al. (2026) — Pressure wave propagation
    • C1 @ 18 m/s = 5.7 kPa | k₁ = 0.0818 kPa/J | k₂ = 0.0036 ms/J
    • Mass: 0.430 kg (FIFA Standard)

  ⚽ KICK — Nunome et al. (2024) — Biomechanics of Instep Soccer Kick
    • 20 m/s = 1,900 N | 9.2 ms contact | k_foot = 22.1 N/J | T_foot = 0.107 ms/J
    • Peak Power = Energy ÷ Contact Time (kW)

Core Methodology:
  • Kinetic Energy:       E = ½mv²
  • HEADING → Brain Load: kPa, ms, BLU  (Phillips et al.) — CUMULATIVE RISK
  • KICK → Shot Power:    Force(N), ContactTime(ms), PeakPower(kW)  (Nunome et al.) — PEAK PERFORMANCE
  • Wet Adjustment:       Damp ×1.10 | Wet Synthetic ×1.25

Risk Thresholds (Heading): 🟢 0–45 | 🟡 45–90 | 🔴 90–160 BLU
Performance Tiers (Kick): 🔵 <5kW | 🟢 5–8kW | 🟡 8–12kW | 🔴 >12kW
Version: 3.2.0 — ✅ Interactive HTML Downloads for BOTH graphs · Clean visuals
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import base64

# =============================================================================
# DUAL CALIBRATION — PHILLIPS (HEAD) + NUNOME (KICK)
# =============================================================================
class DualCalibration:
    BALL_MASS_DRY_KG = 0.430  # FIFA Standard Mass
    
    # === HEADING — Phillips et al. (2026) — C1 Elite Machine-Stitched ===
    HEAD_k1_KPA_PER_J_DRY = 0.0818   # 5.7 kPa ÷ 69.66 J ✅
    HEAD_k2_MS_PER_J_DRY = 0.0036    # 0.250 ms PPSI₉₀ ÷ 69.66 J ✅
    
    # === KICK — Nunome et al. (2024) — Elite Instep Kick ===
    KICK_k_FORCE_PER_J_DRY = 22.1     # 1,900 N ÷ 86.0 J ✅
    KICK_k_TIME_PER_J_DRY = 0.107     # 9.2 ms ÷ 86.0 J ✅
    
    WET_FACTORS = {"dry": 1.00, "damp": 1.10, "wet_synthetic": 1.25}
    
    @classmethod
    def get_head_constants(cls, condition: str = "dry") -> dict:
        factor = cls.WET_FACTORS.get(str(condition).lower().strip(), 1.00)
        return {
            "kPa_per_J": round(cls.HEAD_k1_KPA_PER_J_DRY * factor, 5),
            "ms_per_J": round(cls.HEAD_k2_MS_PER_J_DRY * factor, 6),
            "wet_factor": factor
        }
    
    @classmethod
    def get_kick_constants(cls, condition: str = "dry") -> dict:
        factor = cls.WET_FACTORS.get(str(condition).lower().strip(), 1.00)
        return {
            "force_per_J_N": round(cls.KICK_k_FORCE_PER_J_DRY * factor, 3),
            "time_per_J_ms": round(cls.KICK_k_TIME_PER_J_DRY * factor, 5),
            "wet_factor": factor
        }

# =============================================================================
# SINGLE IMPACT CALCULATION — DUAL MODE
# =============================================================================
def calculate_impact(velocity_mps: float, impact_type: str = "heading", condition: str = "dry") -> dict | None:
    try:
        velocity = float(velocity_mps)
        if velocity <= 0:
            return None
    except:
        return None
    
    joules = 0.5 * DualCalibration.BALL_MASS_DRY_KG * (velocity ** 2)
    
    if impact_type.lower() == "heading":
        cal = DualCalibration.get_head_constants(condition)
        total_kpa = cal["kPa_per_J"] * joules
        total_ms = cal["ms_per_J"] * joules
        brain_load = total_kpa * total_ms
        
        if brain_load < 45:
            category = "LOW"
        elif brain_load < 90:
            category = "MODERATE"
        elif brain_load < 160:
            category = "HIGH"
        else:
            category = "ELEVATED"
        
        return {
            "impact_type": "heading",
            "ball_velocity_mps": round(velocity, 2),
            "condition": condition,
            "Joules": round(joules, 2),
            "Total_kPa": round(total_kpa, 2),
            "PPSI90_ms": round(total_ms, 3),
            "Brain_Load_Units": round(brain_load, 4),
            "Load_Category": category
        }
    
    elif impact_type.lower() == "kick":
        cal = DualCalibration.get_kick_constants(condition)
        peak_force_N = cal["force_per_J_N"] * joules
        contact_time_ms = cal["time_per_J_ms"] * joules
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
            "ball_velocity_mps": round(velocity, 2),
            "condition": condition,
            "Joules": round(joules, 2),
            "Peak_Force_N": round(peak_force_N, 0),
            "Contact_Time_ms": round(contact_time_ms, 2),
            "Peak_Power_kW": round(peak_power_kW, 2),
            "Performance_Category": perf_cat
        }
    
    return None

# =============================================================================
# 🧠 HEADING CHART — Cumulative Line Graph (Risk Over Time)
# =============================================================================
def generate_head_chart(df: pd.DataFrame) -> tuple:
    df = df.copy()
    df = df.sort_values(["player_name", "Minute"])
    df["Cumulative_Brain_Load"] = df.groupby("player_name")["Brain_Load_Units"].cumsum().round(2)
    df["Player_Label"] = df["player_name"] + " (" + df.groupby("player_name")["player_name"].transform("count").astype(str) + " Headers)"
    
    max_load = df["Cumulative_Brain_Load"].max()
    y_max = max(160, round(max_load * 1.1, -1))
    x_max = max(95, round(df["Minute"].max() + 5, -1))
    
    fig = px.line(
        df, x="Minute", y="Cumulative_Brain_Load", color="Player_Label", markers=True,
        title="<b>🧠 HEADING — Cumulative Brain Load Index</b><br><sup>Phillips et al. (2026) · C1 Elite · 5.7 kPa @ 18 m/s</sup>",
        labels={"Minute": "Match Timeline (Minutes)", "Cumulative_Brain_Load": "Cumulative Brain Load (BLU)"},
        hover_data={"Minute": True, "Cumulative_Brain_Load": ": .2f", "Joules": ": .1f J", "Total_kPa": ": .1f kPa"}
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

# =============================================================================
# ⚽ KICK CHART — Peak Power Bar Chart (Performance Per Shot)
# =============================================================================
def generate_kick_chart(df: pd.DataFrame) -> tuple:
    df = df.copy()
    df = df.sort_values("Minute")
    df["Label"] = df["player_name"] + " — " + df["Minute"].astype(str) + "'"
    
    fig = px.bar(
        df, x="Label", y="Peak_Power_kW", color="Performance_Category",
        color_discrete_map={
            "DEVELOPING": "#3498db",
            "COMPETITIVE": "#2ecc71",
            "ELITE": "#f39c12",
            "WORLD-CLASS": "#e74c3c"
        },
        title="<b>⚽ KICK — Peak Shot Power</b><br><sup>Nunome et al. (2024) · Elite Instep Kick Calibration</sup>",
        labels={"Peak_Power_kW": "Peak Power (kW)", "Label": "Player & Minute"},
        hover_data={
            "ball_velocity_mps": True,
            "Peak_Force_N": True,
            "Contact_Time_ms": True,
            "Joules": True
        }
    )
    
    fig.update_layout(
        xaxis_title="",
        height=500,
        margin=dict(l=20, r=20, t=60, b=60),
        showlegend=True,
        legend_title="Performance Tier"
    )
    return fig, df

# =============================================================================
# 📄 INTERACTIVE HTML DOWNLOAD — Works for BOTH Charts!
# =============================================================================
def get_html_download_link(fig, filename="Interactive_Chart.html", button_text="📄 Download Interactive Graph"):
    """Generate a clickable download link for the Plotly chart as interactive HTML."""
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
# MAIN APPLICATION
# =============================================================================
def run_application():
    st.set_page_config(page_title="Ball2Head — Dual Impact Engine", layout="wide")
    if "entries" not in st.session_state:
        st.session_state.entries = []
    
    st.title("⚽🧠 Ball2Head — Dual Impact Engine")
    st.subheader("🧠 Heading Brain Health · ⚽ Kick Shot Power · One Unified System")
    
    with st.expander("📋 Methodology & Calibration Sources"):
        st.markdown("""
        **🧠 HEADING — Phillips et al. (2026):** Pressure wave propagation from head collisions.
        - Output: Peak Pressure (kPa) · PPSI₉₀ (ms) · **Brain Load Units — CUMULATIVE RISK**
        - Graph type: 📈 Rising line = total exposure over time
        
        **⚽ KICK — Nunome et al. (2024):** Biomechanics of instep soccer kicks.
        - Output: Peak Force (N) · Contact Time (ms) · **Peak Power (kW) — PEAK PERFORMANCE**
        - Graph type: 📊 Individual bars = power of each shot
        """)
    
    st.header("📋 Match Information")
    col1, col2 = st.columns(2)
    with col1:
        match_teams = st.text_input("Match", value="Team A vs Team B")
    with col2:
        match_date = st.text_input("Date", value=pd.Timestamp.now().strftime("%Y-%m-%d"))
    
    st.divider()
    
    # ─── METHOD 1: CSV UPLOAD ──────────────────────────────────────────
    st.header("📁 Method 1: Batch Upload from CSV")
    st.info("""
    Required Columns: **player_name, Minute, ball_velocity_mps, impact_type**
    impact_type: 'heading' or 'kick' | Optional: condition (dry/damp/wet)
    """)
    
    uploaded_file = st.file_uploader("Upload Events CSV", type=["csv"])
    
    if uploaded_file:
        df_raw = pd.read_csv(uploaded_file)
        vel_col = next((c for c in df_raw.columns if "vel" in c.lower() or "speed" in c.lower()), None)
        name_col = next((c for c in df_raw.columns if "name" in c.lower() or "player" in c.lower()), None)
        time_col = next((c for c in df_raw.columns if "min" in c.lower() or "time" in c.lower()), None)
        type_col = next((c for c in df_raw.columns if "type" in c.lower() or "impact" in c.lower()), None)
        cond_col = next((c for c in df_raw.columns if "cond" in c.lower()), None)
        
        if not all([vel_col, name_col, time_col, type_col]):
            st.error("Need columns: player_name, Minute, ball_velocity_mps, impact_type")
            return
        
        results = []
        for _, row in df_raw.iterrows():
            itype = str(row[type_col]).lower().strip()
            cond = str(row[cond_col]).lower() if cond_col and pd.notna(row[cond_col]) else "dry"
            calc = calculate_impact(float(row[vel_col]), itype, cond)
            if calc:
                calc["player_name"] = str(row[name_col])
                calc["Minute"] = float(row[time_col])
                results.append(calc)
        
        if results:
            df_calc = pd.DataFrame(results)
            st.success(f"✅ {len(df_calc)} impacts calculated")
            
            head_df = df_calc[df_calc["impact_type"] == "heading"].reset_index(drop=True)
            kick_df = df_calc[df_calc["impact_type"] == "kick"].reset_index(drop=True)
            
            if len(head_df) > 0:
                st.subheader("🧠 Heading — Cumulative Brain Load")
                st.dataframe(head_df, use_container_width=True)
                fig_head, df_head = generate_head_chart(head_df)
                st.plotly_chart(fig_head, use_container_width=True)
                
                # 📥 DOWNLOADS — CSV + Interactive HTML
                dl1, dl2 = st.columns(2)
                with dl1:
                    st.download_button("📥 Download Heading Data (CSV)", df_head.to_csv(index=False), 
                                       "heading_ledger.csv", type="primary", use_container_width=True)
                with dl2:
                    st.markdown(get_html_download_link(fig_head, 
                        f"{match_teams.replace(' ','_')}_Heading_Chart.html",
                        "📄 Download Interactive Heading Graph"), unsafe_allow_html=True)
            
            if len(kick_df) > 0:
                st.subheader("⚽ Kick — Peak Shot Power")
                st.dataframe(kick_df, use_container_width=True)
                fig_kick, df_kick = generate_kick_chart(kick_df)
                st.plotly_chart(fig_kick, use_container_width=True)
                
                # 📥 DOWNLOADS — CSV + Interactive HTML
                dl3, dl4 = st.columns(2)
                with dl3:
                    st.download_button("📥 Download Kick Data (CSV)", df_kick.to_csv(index=False), 
                                       "kick_ledger.csv", type="primary", use_container_width=True)
                with dl4:
                    st.markdown(get_html_download_link(fig_kick, 
                        f"{match_teams.replace(' ','_')}_Kick_Chart.html",
                        "📄 Download Interactive Kick Graph"), unsafe_allow_html=True)
    
    st.divider()
    
    # ─── METHOD 2: MANUAL INPUT ───────────────────────────────────────
    st.header("✍️ Method 2: Enter Impact Manually")
    
    with st.form("manual_entry_form"):
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            name = st.text_input("Player Name / ID")
            minute = st.number_input("Match Minute", min_value=0.0, max_value=120.0, step=1.0)
            impact_type = st.selectbox("Impact Type", ["heading", "kick"])
        with col_b:
            velocity = st.number_input("Ball Velocity (m/s)", min_value=5.0, max_value=40.0, step=0.5, value=18.0)
            condition = st.selectbox("Match Condition", ["dry", "damp", "wet_synthetic"])
        with col_c:
            st.markdown("<br>", unsafe_allow_html=True)
            add_btn = st.form_submit_button("➕ Add to Ledger", type="primary", use_container_width=True)
        
        if add_btn:
            if not name:
                st.error("Enter Player Name")
            else:
                calc = calculate_impact(velocity, impact_type, condition)
                if calc:
                    calc["player_name"] = name
                    calc["Minute"] = minute
                    st.session_state.entries.append(calc)
                    if impact_type == "heading":
                        st.success(f"✅ 🧠 {name} — {velocity} m/s → {calc['Total_kPa']} kPa | {calc['Brain_Load_Units']} BLU")
                    else:
                        st.success(f"✅ ⚽ {name} — {velocity} m/s → {calc['Peak_Power_kW']} kW | {calc['Performance_Category']}")
    
    # ─── DISPLAY RESULTS & DOWNLOADS ──────────────────────────────────
    if st.session_state.entries:
        st.divider()
        st.subheader(f"📊 Full Ledger — {len(st.session_state.entries)} Impact(s)")
        df_all = pd.DataFrame(st.session_state.entries)
        st.dataframe(df_all, use_container_width=True)
        
        head_entries = df_all[df_all["impact_type"] == "heading"].reset_index(drop=True)
        kick_entries = df_all[df_all["impact_type"] == "kick"].reset_index(drop=True)
        
        if len(head_entries) > 0:
            st.subheader("🧠 Heading — Cumulative Brain Load")
            fig_head, df_head = generate_head_chart(head_entries)
            st.plotly_chart(fig_head, use_container_width=True)
            
            dl_h1, dl_h2 = st.columns(2)
            with dl_h1:
                st.download_button("📥 Download Heading Data (CSV)", df_head.to_csv(index=False), 
                                   "manual_head_ledger.csv", type="primary", use_container_width=True)
            with dl_h2:
                st.markdown(get_html_download_link(fig_head, "Manual_Heading_Chart.html",
                    "📄 Download Interactive Heading Graph"), unsafe_allow_html=True)
        
        if len(kick_entries) > 0:
            st.subheader("⚽ Kick — Peak Shot Power")
            fig_kick, df_kick = generate_kick_chart(kick_entries)
            st.plotly_chart(fig_kick, use_container_width=True)
            
            dl_k1, dl_k2 = st.columns(2)
            with dl_k1:
                st.download_button("📥 Download Kick Data (CSV)", df_kick.to_csv(index=False), 
                                   "manual_kick_ledger.csv", type="primary", use_container_width=True)
            with dl_k2:
                st.markdown(get_html_download_link(fig_kick, "Manual_Kick_Chart.html",
                    "📄 Download Interactive Kick Graph"), unsafe_allow_html=True)
        
        st.download_button("📥 Download ALL Combined Data (CSV)", df_all.to_csv(index=False), 
                           "full_combined_ledger.csv", type="secondary", use_container_width=True)

# =============================================================================
# RUN APPLICATION
# =============================================================================
if __name__ == "__main__":
    run_application()