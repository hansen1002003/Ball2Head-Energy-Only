# ⚽ Ball2Head — Heading Load Framework
> **Lab-Calibrated • Video-Enabled • Sensor-Free Estimation**  
> *Peer-Reviewed Physics • Open Methodology • Independent Governance*

---

## 📌 Overview

Ball2Head provides a standardised, scalable framework for measuring football heading load — **without requiring player-worn sensors**. By combining peer-reviewed biomechanical principles with one-time laboratory calibration, ball velocity measured from video or optical tracking is converted into clinically meaningful exposure metrics.

> **Core Innovation:** Calibrate once in the lab → deploy everywhere with existing stadium/grassroots video infrastructure.

---

## 🔬 Methodology — Peer-Reviewed Foundation

### Physics Chain

Ball Velocity → [½mv²] → Impact Energy → [k₁] → Peak Pressure (kPa)
→ [k₂] → Pulse Duration (ms)


### References
- **Energy from Velocity**: Newtonian kinetic energy — Stone et al. (2018), Naunheim et al. (2007)
- **Calibration Method**: Linear regression — Montgomery (2019), Bland & Altman (1999)
- **Optical Tracking Validation**: IEEE Std 1559 (2016) — velocity measurement accuracy

### Calibration Constants
Values derived from **one-time laboratory testing** (ball firing + headform measurement):
- `k₁` = Peak Pressure conversion factor — **kPa per Joule**
- `k₂` = Pulse Duration conversion factor — **ms per Joule**
- Mass = Standard FIFA ball mass by size (3 / 4 / 5)

> ⚠️ **Current values = PLACEHOLDERS** — replace with lab-derived regression results when available.

---

## 📁 Project Structure
Ball2Head/
├── README.md ← This file
├── dashboard.py ← Streamlit calibration & load monitor
├── requirements.txt ← Dependencies
├── examples/
│ └── sample_tracking.csv ← Example optical tracking input
└── docs/
├── methodology.md ← Full peer-reviewed methodology
└── calibration.md ← Lab testing protocol

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install streamlit pandas numpy

2. Run Dashboard
streamlit run dashboard.py

3. Update Calibration (When Lab Data Available)
Edit dashboard.py → CALIBRATION dictionary:
CALIBRATION = {
    5: {
        "mass_kg": 0.43,
        "k1_kPa_per_J": YOUR_LAB_VALUE,   # Energy → Peak Pressure
        "k2_ms_per_J": YOUR_LAB_VALUE,    # Energy → Pulse Duration
    }
}

📄 CSV Data Format
Input — Optical / Video Tracking
TABLE
time_s	velocity_m_s
0.00	0.0
0.02	12.3
0.04	18.7

Output — Processed Results
TABLE
time_s	velocity_m_s	Energy_J	Peak_kPa	Duration_ms
0.00	0.0	0.0	0.0	0.0
0.02	12.3	24.3	391	8.4
0.04	18.7	55.9	900	19.3


⚙️ How It Works
Input → Ball velocity from video, optical tracking, or smart ball
Physics → E = ½mv² calculates impact energy
Calibration → Lab-derived constants convert energy → clinical metrics
Output → Standardised heading load + risk assessment
Deploy → Works at all levels — elite stadiums to grassroots pitches
📊 Dashboard Features
✍️ Single Impact — Manual velocity input & instant calculation
📁 Batch Processing — Upload CSV, process entire sessions
📋 Data Guide — Format specification + workflow documentation
📥 Export — Download full results for analysis/reporting
🎯 Risk Thresholds — Visual exposure indicators (Green / Yellow / Red)


🏛️ Governance
Ball2Head CIC — Community Interest Company
Open methodology • Fully auditable • No proprietary lock-in
Non-profit structure • All reinvested into player welfare
Independent from equipment vendors • Standards-aligned
⚠️ Status & Disclaimer
Physics layer: ✅ Complete — peer-reviewed first principles
Calibration constants: ⏳ Placeholder values — awaiting lab testing
Deployment: ✅ Ready — update k₁ / k₂ once lab data available
This framework provides standardised exposure estimation, not medical diagnosis. Clinical thresholds should be reviewed and approved by medical governance bodies before adoption.


📚 Citation
Keskom, H. (2026). Ball2Head: Independent Framework for Standardised Heading Load Measurement. Final-Year Research Project, Birmingham Newman University. Patent Pending GB2620633.4


🤝 Contributing
This project follows open-physics principles. All methodology is auditable and peer-reviewable. Calibration data and validation reports welcome.
Built on lived experience • Guided by peer review • For player welfare ⚽
