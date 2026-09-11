import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. FIXED DATA INGESTION & DATASET SIMULATION
np.random.seed(42)

raw_data = {
    "Player_ID": [
        "VVD_04",
        "VVD_04",
        "VVD_04",
        "VVD_04",
        "KON_05",
        "KON_05",
        "MAC_10",
        "MAC_10",
        "SZO_08",
    ],
    "Minute": [12, 34, 56, 82, 22, 71, 15, 44, 63],  # Fixed syntax clip
    "kPa_per_J": [0.85, 0.92, 1.10, 0.78, 0.95, 1.05, 0.65, 0.72, 0.80],
    "ms_per_J": [2.4, 2.8, 3.1, 2.2, 2.6, 2.9, 1.9, 2.1, 2.3],
    "Joules": [25.4, 30.1, 42.3, 22.1, 28.5, 35.0, 18.2, 20.5, 24.0],  # Fixed syntax clip
}

df_match = pd.DataFrame(raw_data)

# Compute your core calibrated metrics
df_match["Total_kPa"] = df_match["kPa_per_J"] * df_match["Joules"]
df_match["Total_ms"] = (df_match["ms_per_J"] * df_match["Joules"]) / 1000
df_match["Brain_Load_Units"] = df_match["Total_kPa"] * df_match["Total_ms"]

# Calculate individual total header metrics for naming nomenclature
header_counts = df_match["Player_ID"].value_counts().to_dict()
df_match["Header_Count"] = df_match["Player_ID"].map(header_counts)
df_match["Nomenclature_ID"] = (
    df_match["Player_ID"] + " (" + df_match["Header_Count"].astype(str) + " Headers)"
)

# Sort chronologically to track cumulative progression accurately
df_match = df_match.sort_values(["Nomenclature_ID", "Minute"])

# Calculate cumulative load timeline per player
df_match["Cumulative_Brain_Load"] = df_match.groupby("Nomenclature_ID")[
    "Brain_Load_Units"
].cumsum()

# 2. GENERATE INTERACTIVE LIVE GRAPH
fig = px.line(
    df_match,
    x="Minute",
    y="Cumulative_Brain_Load",
    color="Nomenclature_ID",
    markers=True,
    title="<b>POST-MATCH SQUAD HEAD-LOAD LEDGER</b><br><sup>Metrics Normalized via Lab-Calibrated Inverse Core Constants</sup>",
    labels={
        "Minute": "Match Timeline (Minutes)",
        "Cumulative_Brain_Load": "Cumulative Brain Load Index",
        "Nomenclature_ID": "Player Squad Profiles",
    },
    # The magic hover template: maps out exactly what the doctor sees on hover
    hover_data={
        "Nomenclature_ID": False,  # Hide redundant label
        "Minute": True,
        "Cumulative_Brain_Load": ":.2f",
        "Joules": ":.1f J",
        "kPa_per_J": ":.2f kPa/J",
        "ms_per_J": ":.2f ms/J",
        "Total_kPa": ":.1f kPa",
    },
)

# 3. ADD CLINICAL BACKGROUND RISK THRESHOLDS (Green/Amber/Red Zones)
fig.add_hrect(
    y0=0, y1=45, fillcolor="#2ecc71", opacity=0.06, layer="below", line_width=0
)
fig.add_hrect(
    y0=45, y1=90, fillcolor="#f1c40f", opacity=0.06, layer="below", line_width=0
)
fig.add_hrect(
    y0=90, y1=160, fillcolor="#e74c3c", opacity=0.06, layer="below", line_width=0
)

# Style tweaks for an elite clinical dashboard feel
fig.update_layout(
    xaxis=dict(range=[0, 95], dtick=10, gridcolor="rgba(0,0,0,0.05)"),
    yaxis=dict(range=[0, 160], gridcolor="rgba(0,0,0,0.05)"),
    plot_bgcolor="white",
    hovermode="closest",
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    margin=dict(l=50, r=50, t=80, b=50),
)

# Format the line stroke thickness and markers
fig.update_traces(line=dict(width=3.5), marker=dict(size=8))

# 4. EXPORT AS AN INTERACTIVE LIVE WEBPAGE FOR THE DOCTOR'S IPAD
output_html = "Squad_Live_Interactive_HeadLoad.html"
fig.write_html(output_html)
print(
    f"\nSuccess! Interactive HTML live graph generated: '{output_html}'"
)
print("Open this file in your browser to test the dynamic hover effects.")

# Automatically open in default browser for testing
import webbrowser

webbrowser.open(output_html)
