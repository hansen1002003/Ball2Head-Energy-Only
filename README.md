# ⚽ Ball2Head — Unified Heading Exposure Calculator & Brain Health Ledger

> **Peer-reviewed, open-source framework for estimating heading load in football.**  
> Built on research from Phillips et al. (2026), Zhang et al. (2013), Caccese et al. (2018), Naunheim et al. (2003).  
> 🟢 **Live App:** [ball2head.streamlit.app](https://ball2head.streamlit.app)

---

## 📋 Table of Contents
- [Overview](#-overview)
- [Key Features](#-key-features)
- [Quick Start](#-quick-start)
- [How It Works](#-how-it-works)
- [Calibration & Science](#-calibration--science)
- [Risk Thresholds](#-risk-thresholds)
- [Data Format](#-batch-csv-format)
- [Local Development](#-local-development)
- [References](#-references)
- [License](#-license)

---

## 🌟 Overview

**Ball2Head** provides a standardized, peer-reviewed method to convert ball velocity, impact force, or IMU acceleration into clinically meaningful metrics:
- **Kinetic Energy (J)** — Energy transferred at impact
- **Peak Intracranial Pressure (kPa)** — Estimated brain pressure
- **Pressure Wave Duration (ms)** — Impact loading duration
- **Peak Linear Acceleration (g)** — Head acceleration magnitude

All calculations are **auditable, timestamped, and exportable** — built for player welfare research and clinical monitoring.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🧮 **Single Calculation** | Instant metric conversion from velocity, force, or acceleration |
| 📁 **Batch CSV Upload** | Process hundreds of events in one upload |
| 📋 **History & Download** | Save all results → export CSV → plot in Excel |
| 👤 **Age & Gender Adjustment** | Ball size + biomechanical factors built-in |
| 📊 **Peer-Reviewed Calibration** | Linear regression R² > 0.999 (Phillips et al., 2026) |
| 🔒 **Local-First Data** | No server storage — compliant with GDPR & data protection |
| 📱 **Fully Responsive** | Works on desktop, tablet, and mobile |

---

## 🚀 Quick Start

### 🟢 Use Online (Recommended)
**👉 [ball2head.streamlit.app](https://ball2head.streamlit.app)** — No installation needed!

### 💻 Run Locally
```bash
# Clone the repo
git clone https://github.com/hansen1002003/Ball2Head-Energy-Only.git
cd Ball2Head-Energy-Only

# Install dependencies
pip install -r requirements.txt

# Launch the app
streamlit run src/main.py

🧠 How It Works
Input Methods
Ball Velocity (km/h, m/s, mph, ft/s) — simplest & most widely available
Peak Impact Force (kN, N, lbf) — from load cells or sensor data
IMU 3D Acceleration (g, m/s²) — from in-ball or head-mounted sensors

Output Metrics
Metric	Unit	Description
Energy	Joules (J)	Kinetic energy transferred to the head
Peak Pressure	kPa	Estimated intracranial pressure
Wave Duration	ms	Pressure wave propagation time
Peak Linear Acceleration	g	Resultant head acceleration
Risk Level	—	Colour-coded exposure classification


🔬 Calibration & Science
Ball Size Constants
Ball Size	Age Group	Mass (kg)	k₁ (kPa/J)	k₂ (ms/J)	Force→kPa (kPa/kN)
Size 3	U8–U10	0.32	1.37	0.073	16.2
Size 4	U12–U14	0.37	1.28	0.070	15.9
Size 5	U16–Elite	0.43	1.19	0.067	15.7

Source: Phillips et al. (2026) — linear regression R² > 0.999
Biomechanical Adjustment
Male: 1.00 (baseline)
Female: 1.20 (+20% — Zhang et al., 2013; Caccese et al., 2018)


🎯 Risk Thresholds
Table
Level	Colour	Peak Pressure	Guidance
LOW	🟢 Green	< 70 kPa	Within typical daily exposure
MODERATE	🟡 Yellow	70–99 kPa	Monitor cumulative exposure
ELEVATED	🟠 Orange	100–149 kPa	Significant impact — note event
EXTREME	🔴 Red	≥ 150 kPa	High-energy impact — assess player


📁 Batch CSV Format
Upload a CSV file with any combination of these columns:
Table
Column	Required?	Format	Example
timestamp	Optional	YYYY-MM-DD HH:MM:SS	2026-09-10 15:30:45
player_id	Optional	Text	Ronaldo_7
velocity / velocity_kmh	One required	Numeric	45.2
force_kN	One required	Numeric	3.8
accel_x, accel_y, accel_z	One required	Numeric (g or m/s²)	18.5, -12.3, 25.1

The system auto-detects input type and computes all metrics for every row.
📊 Using the History Data
After saving calculations or processing a batch:
Go to History & Download tab
Click Download CSV
Open in Excel / Google Sheets
Visualise trends:
Line Chart → Pressure over time
Scatter Plot → Energy vs Pressure
Pivot Table → Per-player summary
📚 References
Phillips et al. (2026) — Ball impact characteristics and intracranial pressure wave propagation.
Zhang et al. (2013) — Head impact accelerations in collegiate soccer: Gender differences.
Caccese et al. (2018) — Sex differences in head impact biomechanics.
Naunheim et al. (2003) — Linear acceleration predicts intracranial pressure in a head model.


📄 License
This work is released for independent academic and clinical use.
Code is open for audit and transparency — as part of a Community Interest Company (CIC) mission for player welfare.
For commercial integration or league-wide deployment, please contact for licensing terms.
<div align="center">
Built for player welfare — from grassroots to elite.
If this helps, ⭐ Star the repo & share the link!
Live App · GitHub
</div> ``