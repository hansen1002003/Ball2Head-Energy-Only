"""
Ball2Head — Heading Load & Brain Health Ledger
===============================================
Calibration: Phillips et al. (2026) — A1/B1 Mean — FIFA 430g
Author: Hansen Sominabo Kekom
Version: 2.0 — Interactive Ledger + CSV Export
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
from io import StringIO, BytesIO
import base64

# =============================================================================
# 📐 CALIBRATION — PURE PHILLIPS ET AL. (2026)
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
        cond = str(condition).lower().strip()
        factor = cls.WET_FACTORS.get(cond, 1.00)
        return {
            "k1_kpa_j": round(cls.DRY_k1_KPA_PER_J * factor, 4),
            "k2_ms_j": round(cls.DRY_k2_MS_PER_J * factor, 5),
            "wet_factor": factor
        }

# =============================================================================
# 🧮 CORE CALCULATION ENGINE
# =============================================================================
def calculate_metrics(velocity_mps: float, condition: str = "dry"):
    """Calculate heading load from velocity — Phillips et al. (2026)"""
    try:
        velocity = float(velocity_mps)
        if velocity <= 0:
            return None
    except (ValueError, TypeError):
        return None
    
    # Kinetic Energy: E = ½mv²
    energy_j = 0.5 * Calibration.BALL_MASS_DRY_KG * (velocity ** 2)
    
    # Get condition-adjusted constants
    factors = Calibration.get_factors(condition)
    
    # Baseline (dry) values
    baseline_kpa = round(Calibration.DRY_k1_KPA_PER_J * energy_j, 2)
    baseline_ms = round(Calibration.DRY_k2_MS_PER_J * energy_j, 3)
    
    # Adjusted values
    adjusted_kpa = round(factors["k1_kpa_j"] * energy_j, 2)
    adjusted_ms = round(factors["k2_ms_j"] * energy_j, 3)
    
    # Load category
    if adjusted_kpa < 30:
        category = "LOW"
    elif adjusted_kpa < 60:
        category = "MODERATE"
    elif adjusted_kpa < 90:
        category = "HIGH"
    else:
        category = "EXTREME"
    
    return {
        "ball_velocity_mps": round(velocity, 2),
        "condition": condition,
        "kinetic_energy_j": round(energy_j, 2),
        "baseline_dry_kpa": baseline_kpa,
        "baseline_dry_wave_duration_ms": baseline_ms,
        "adjusted_kpa": adjusted_kpa,
        "adjusted_wave_duration_ms": adjusted_ms,
        "wet_factor_applied": factors["wet_factor"],
        "kpa_per_j": round(adjusted_kpa / energy_j, 4) if energy_j > 0 else 0,
        "ms_per_j": round(adjusted_ms / energy_j, 4) if energy_j > 0 else 0,
        "load_category": category
    }

# =============================================================================
# 📊 INTERACTIVE BRAIN HEALTH LEDGER GENERATOR
# =============================================================================
def generate_ledger_html(df_results, match_info=None):
    """
    Generate the interactive post-match squad brain health ledger
    with the exact visual style from your reference — cumulative load,
    player timelines, hover tooltips, full professional report.
    """
    match_info = match_info or {}
    match_date = match_info.get("date", pd.Timestamp.now().strftime("%Y-%m-%d"))
    match_teams = match_info.get("teams", "Team A vs Team B")
    total_minutes = match_info.get("total_minutes", 90)
    
    # Prepare player data for ledger
    player_data = {}
    all_events = []
    
    for _, row in df_results.iterrows():
        pid = str(row.get("player_id", f"P_{_}"))
        pname = str(row.get("player_name", pid))
        minute = float(row.get("event_minute", _ * 2))
        energy = row.get("kinetic_energy_j", 0)
        kpa = row.get("adjusted_kpa", 0)
        ms = row.get("adjusted_wave_duration_ms", 0)
        kpa_per_j = row.get("kpa_per_j", 0)
        ms_per_j = row.get("ms_per_j", 0)
        
        if pid not in player_data:
            player_data[pid] = {
                "name": pname,
                "events": [],
                "cumulative_load": 0,
                "total_headers": 0,
                "total_energy": 0,
                "total_kpa": 0,
                "total_ms": 0
            }
        
        # Cumulative load = sum of kPa/J (normalised per-Joule → consistent across all impacts)
        load_value = kpa_per_j
        player_data[pid]["cumulative_load"] += load_value
        player_data[pid]["total_headers"] += 1
        player_data[pid]["total_energy"] += energy
        player_data[pid]["total_kpa"] += kpa
        player_data[pid]["total_ms"] += ms
        
        player_data[pid]["events"].append({
            "minute": minute,
            "energy": energy,
            "kpa": kpa,
            "ms": ms,
            "kpa_per_j": kpa_per_j,
            "ms_per_j": ms_per_j,
            "cumulative": player_data[pid]["cumulative_load"]
        })
    
    # Prepare JSON for chart
    chart_players = []
    colors = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e", "#17becf", "#e377c2"]
    
    for idx, (pid, data) in enumerate(player_data.items()):
        sorted_events = sorted(data["events"], key=lambda x: x["minute"])
        chart_players.append({
            "id": pid,
            "name": data["name"],
            "color": colors[idx % len(colors)],
            "totalHeaders": data["total_headers"],
            "totalEnergy": round(data["total_energy"], 1),
            "totalKpa": round(data["total_kpa"], 1),
            "totalMs": round(data["total_ms"], 1),
            "finalCumulative": round(data["cumulative_load"], 2),
            "dataPoints": [{"x": e["minute"], "y": e["cumulative"], 
                            "energy": e["energy"], "kpa": e["kpa"], "ms": e["ms"],
                            "kpaPerJ": e["kpa_per_j"], "msPerJ": e["ms_per_j"]} 
                           for e in sorted_events]
        })
    
    # Build HTML — professional, interactive, matches your design
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Post-Match Squad Brain Health Ledger</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.8/dist/chart.umd.min.js"></script>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Roboto, sans-serif; }}
        body {{ background: #f8f9fa; padding: 30px; max-width: 1400px; margin: 0 auto; }}
        .header {{ background: white; padding: 25px 30px; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); margin-bottom: 25px; }}
        .header h1 {{ font-size: 26px; color: #1a1a2e; margin-bottom: 8px; }}
        .header p {{ color: #666; font-size: 14px; }}
        .match-meta {{ display: flex; gap: 30px; margin-top: 15px; flex-wrap: wrap; }}
        .meta-item {{ font-size: 14px; }}
        .meta-item strong {{ color: #1a1a2e; }}
        .chart-container {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); margin-bottom: 25px; position: relative; height: 550px; }}
        .legend {{ display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 15px; }}
        .legend-item {{ display: flex; align-items: center; gap: 6px; font-size: 13px; }}
        .legend-swatch {{ width: 14px; height: 14px; border-radius: 3px; display: inline-block; }}
        .summary-table {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #eee; font-size: 14px; }}
        th {{ background: #f8f9fa; font-weight: 600; color: #333; }}
        .download-btn {{ background: #1a1a2e; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-size: 14px; margin-top: 15px; }}
        .download-btn:hover {{ background: #333; }}
        .footer {{ margin-top: 25px; font-size: 12px; color: #888; text-align: center; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 Post-Match Squad Brain Health Ledger</h1>
        <p style="font-size: 13px; color: #888;">Metrics Normalised via Lab-Calibrated Inverse Core Constants — Phillips et al. (2026)</p>
        <div class="match-meta">
            <div class="meta-item"><strong>Match:</strong> {match_teams}</div>
            <div class="meta-item"><strong>Date:</strong> {match_date}</div>
            <div class="meta-item"><strong>Duration:</strong> {total_minutes} mins</div>
            <div class="meta-item"><strong>Calibration:</strong> A1/B1 Mean — FIFA 430g</div>
        </div>
    </div>

    <div class="chart-container">
        <div class="legend" id="legend"></div>
        <canvas id="brainLoadChart"></canvas>
    </div>

    <div class="summary-table">
        <h3>📋 Player Summary</h3>
        <table id="summaryTable">
            <thead>
                <tr>
                    <th>Player ID</th>
                    <th>Name</th>
                    <th>Headers</th>
                    <th>Total Energy (J)</th>
                    <th>Total kPa</th>
                    <th>Total ms</th>
                    <th>Cumulative Brain Load Index</th>
                </tr>
            </thead>
            <tbody id="summaryBody"></tbody>
        </table>
        <button class="download-btn" onclick="window.print()">📄 Download PDF Report</button>
    </div>

    <div class="footer">
        Calibration: Phillips, I. et al. (2026) — Pressure wave propagation from association football head collisions<br>
        k₁ = 1.19 kPa/J | k₂ = 0.067 ms/J — Standardised to FIFA Size 5 — 430g<br>
        Generated by Ball2Head — Investigational Research — {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")}
    </div>

    <script>
        const playerData = {json.dumps(chart_players)};
        const totalMinutes = {total_minutes};
        
        // Build legend
        const legendDiv = document.getElementById('legend');
        playerData.forEach(p => {{
            const div = document.createElement('div');
            div.className = 'legend-item';
            div.innerHTML = `<span class="legend-swatch" style="background:${p.color}"></span>${p.name} (${p.totalHeaders} Headers)`;
            legendDiv.appendChild(div);
        }});
        
        // Build summary table
        const tableBody = document.getElementById('summaryBody');
        playerData.forEach(p => {{
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${{p.id}}</td>
                <td>${{p.name}}</td>
                <td>${{p.totalHeaders}}</td>
                <td>${{p.totalEnergy}}</td>
                <td>${{p.totalKpa}}</td>
                <td>${{p.totalMs}}</td>
                <td><strong>${{p.finalCumulative}}</strong></td>
            `;
            tableBody.appendChild(row);
        }});
        
        // Draw chart
        const ctx = document.getElementById('brainLoadChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                datasets: playerData.map(p => ({{
                    label: `${{p.name}} (${{p.totalHeaders}} Headers)`,
                    data: p.dataPoints.map(d => ({{x: d.x, y: d.y}})),
                    borderColor: p.color,
                    backgroundColor: p.color + '20',
                    borderWidth: 3,
                    pointRadius: 5,
                    pointHoverRadius: 8,
                    tension: 0.2,
                    fill: false
                }}))
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                interaction: {{ intersect: true, mode: 'index' }},
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{
                        backgroundColor: '#1a1a2e',
                        titleFont: {{ size: 14, weight: 'bold' }},
                        bodyFont: {{ size: 13 }},
                        padding: 15,
                        cornerRadius: 8,
                        callbacks: {{
                            label: function(context) {{
                                const d = context.raw;
                                return [
                                    `Player: ${{context.dataset.label}}`,
                                    `Minute: ${{d.x}}`,
                                    `Cumulative Brain Load Index: ${{d.y.toFixed(2)}}`,
                                    `Energy: ${{d.energy}} J`,
                                    `kPa/J: ${{d.kpaPerJ}}`,
                                    `ms/J: ${{d.msPerJ}}`,
                                    `Peak Pressure: ${{d.kpa}} kPa`,
                                    `Wave Duration: ${{d.ms}} ms`
                                ];
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        type: 'linear',
                        title: {{ display: true, text: 'Match Timeline (Minutes)', font: {{ size: 14, weight: 'bold' }} }},
                        min: 0, max: totalMinutes,
                        ticks: {{ stepSize: 10 }}
                    }},
                    y: {{
                        title: {{ display: true, text: 'Cumulative Brain Load Index', font: {{ size: 14, weight: 'bold' }} }},
                        beginAtZero: true
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    return html_template

# =============================================================================
# 🖥️ STREAMLIT MAIN INTERFACE
# =============================================================================
def run_streamlit():
    st.set_page_config(page_title="Ball2Head — Brain Health Ledger", layout="wide")
    st.title("⚽ Ball2Head — Post-Match Squad Brain Health Ledger")
    st.subheader("Calibrated from Phillips et al. (2026) — Elite Size 5 Standard")
    
    # Methodology
    with st.expander("📋 Methodology & Calibration Source"):
        st.markdown("""
        **Calibration Source:** Mean of A1 (Thermally Bonded) & B1 (Fuse-Welded) elite match balls, 
        standardised to FIFA regulation 430 g dry mass.
        
        **Formula:**
        - Kinetic Energy: $E = \\frac{1}{2}mv^2$
        - Peak Pressure: $P = k_1 \\times E$  → **k₁ = 1.19 kPa/J (dry)**
        - Wave Duration: $t = k_2 \\times E$  → **k₂ = 0.067 ms/J (dry)**
        
        **Cumulative Brain Load Index** = Sum of kPa/J per impact — normalised for fair comparison.
        
        **Reference:** Phillips, I. et al. (2026) — *Pressure wave propagation from association football head collisions*
        """)
    
    # -------------------------------------------------------------------------
    # SECTION 1 — BATCH CSV UPLOAD → FULL LEDGER
    # -------------------------------------------------------------------------
    st.header("📁 Upload Match Data → Generate Interactive Ledger")
    st.info("""
    **Required columns in your CSV:**
    - `player_id` or `player_name` — to identify each player
    - `ball_velocity_mps` or `velocity` — ball speed at impact in m/s
    - `event_minute` or `timestamp` — match time in minutes
    - `condition` — dry / damp / wet_synthetic (optional, defaults to dry)
    
    All other columns preserved. Output: Interactive HTML Ledger + Calculated CSV.
    """)
    
    # Match info
    col1, col2, col3 = st.columns(3)
    with col1:
        match_teams = st.text_input("Match", value="Team A vs Team B")
    with col2:
        match_date = st.text_input("Date", value=pd.Timestamp.now().strftime("%Y-%m-%d"))
    with col3:
        total_mins = st.number_input("Match Duration (Minutes)", value=90, min_value=1, max_value=200)
    
    uploaded_file = st.file_uploader("Upload Match Events CSV", type=["csv"])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write(f"📋 Uploaded: {len(df)} rows × {len(df.columns)} columns")
        
        # Auto-detect columns
        vel_col = None
        for c in df.columns:
            if str(c).lower() in ["velocity", "speed", "ball_velocity", "ballvelocity", "ball_velocity_mps"]:
                vel_col = c
                break
        
        pid_col = None
        for c in df.columns:
            if str(c).lower() in ["player_id", "playerid", "player"]:
                pid_col = c
                break
        
        name_col = None
        for c in df.columns:
            if str(c).lower() in ["player_name", "playername", "name"]:
                name_col = c
                break
        
        time_col = None
        for c in df.columns:
            if str(c).lower() in ["minute", "event_minute", "time", "timestamp", "match_time"]:
                time_col = c
                break
        
        cond_col = None
        for c in df.columns:
            if str(c).lower() in ["condition", "weather", "match_condition"]:
                cond_col = c
                break
        
        if not vel_col:
            st.error("❌ Could not find velocity column. Ensure 'velocity' or 'ball_velocity_mps' exists.")
            return
        
        st.info(f"✅ Velocity: **{vel_col}** | Player ID: **{pid_col or 'Auto'}** | Time: **{time_col or 'Auto'}**")
        
        # Process all rows
        results = []
        for idx, row in df.iterrows():
            # Player info
            pid = str(row.get(pid_col, f"P{idx}")) if pid_col else f"P{idx}"
            pname = str(row.get(name_col, pid)) if name_col else pid
            
            # Time
            minute = float(row[time_col]) if time_col else float(idx * 2)
            
            # Velocity & condition
            vel = float(row[vel_col])
            cond = str(row[cond_col]).lower().strip() if cond_col else "dry"
            if "wet" in cond and "synthetic" not in cond:
                cond = "damp" if "damp" in cond or "light" in cond else "wet_synthetic"
            elif cond not in ["dry", "damp", "wet_synthetic"]:
                cond = "dry"
            
            # Calculate
            metrics = calculate_metrics(vel, cond)
            if metrics:
                metrics["player_id"] = pid
                metrics["player_name"] = pname
                metrics["event_minute"] = minute
                results.append(metrics)
        
        if not results:
            st.error("❌ No valid calculations — check velocity values")
            return
        
        # Combine with original data
        metrics_df = pd.DataFrame(results)
        output_df = pd.concat([df.reset_index(drop=True), metrics_df], axis=1)
        
        # Show results
        st.success(f"✅ Processed {len(results)} header impacts across {metrics_df['player_id'].nunique()} players")
        st.dataframe(output_df, use_container_width=True)
        
        # Download CSV
        csv = output_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Calculated CSV",
            data=csv,
            file_name=f"ball2head_calculated_{match_date}.csv",
            mime="text/csv",
            type="primary"
        )
        
        # Generate & Show Interactive Ledger
        st.divider()
        st.header("🧠 Interactive Post-Match Squad Brain Health Ledger")
        
        match_info = {
            "teams": match_teams,
            "date": match_date,
            "total_minutes": total_mins
        }
        html_content = generate_ledger_html(metrics_df, match_info)
        
        # Display in app
        st.components.v1.html(html_content, height=700, scrolling=True)
        
        # Download HTML ledger
        b64_html = base64.b64encode(html_content.encode()).decode()
        href = f'<a href="data:text/html;charset=utf-8;base64,{b64_html}" download="BrainHealth_Ledger_{match_date}.html">📄 Download Full Interactive Ledger (HTML)</a>'
        st.markdown(href, unsafe_allow_html=True)
    
    st.divider()
    
    # -------------------------------------------------------------------------
    # SECTION 2 — SINGLE CALCULATION
    # -------------------------------------------------------------------------
    st.header("🎯 Single Impact Calculation")
    col1, col2 = st.columns(2)
    with col1:
        velocity = st.number_input("Ball Velocity (m/s)", min_value=5.0, max_value=35.0, value=18.0, step=0.5)
    with col2:
        condition = st.selectbox("Match Condition", ["dry", "damp", "wet_synthetic"], index=0)
    
    if st.button("Calculate Single Impact", type="primary"):
        result = calculate_metrics(velocity, condition)
        if result:
            st.success("✅ Calculation Complete")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Energy", f"{result['kinetic_energy_j']} J")
                st.metric("Baseline kPa", f"{result['baseline_dry_kpa']} kPa")
            with c2:
                st.metric("Adjusted kPa", f"{result['adjusted_kpa']} kPa", delta=f"×{result['wet_factor_applied']}")
                st.metric("kPa per Joule", f"{result['kpa_per_j']} kPa/J")
            with c3:
                st.metric("Wave Duration", f"{result['adjusted_wave_duration_ms']} ms")
                st.metric("Load Category", result['load_category'])
            st.json(result)
    
    st.divider()
    st.caption("Ball2Head — Investigational Research | Phillips et al. (2026) | A1/B1 Mean — FIFA 430g")

# =============================================================================
# RUN APP
# =============================================================================
if __name__ == "__main__":
    run_streamlit()