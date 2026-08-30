# ⚽ Ball2Head — Physics-First Impact Energy Framework
**Pure Physics Core + Future AI Refinement • Auditable • Historical-Ready**

---

## 🎯 **Project Overview**
Ball2Head calculates football heading impact energy directly from smart-ball IMU data:
- **Layer A (Current)**: **First-principles physics** — no training required, works on *any* historical IMU logs
- **Built on**: PINN methodology (Raissi et al., 2019) — physics is always the constraint, never learned

---

## 🧠 **How It Works**
### Core Physics (`src/compute_energy.py`)
Universal, auditable — no black box

1. **Total Acceleration**:
   a_total = sqrt( a_x² + a_y² + a_z² )

2. **Velocity Change**:
   Δv = a_total × Δt
   (sampling rate = 500 Hz)

3. **Impact Energy**:
   E = ½ × m × v²
   (FIFA‑standard ball mass m = 0.43 kg)

### Architecture


---

## 🚀 **How to Run**

### 1. Install Dependencies
```bash
pip install -r requirements.txt


Start API Server
uvicorn src.api:app --reload

Endpoints:
POST /api/calculate-energy — Manual input: {ax, ay, az, timestamp}




📚 Scientific References
Raissi et al. (2019) — Physics-Informed Neural Networks framework
Stone et al. (2016/2018) — Smart-ball IMU validation
Goldstein (2002) — Classical mechanics derivation
Young & Freedman (2016) — Standard constants & units


✅ Key Advantages
✅ API Endpoints/Historical-ready: Works on any existing IMU logs — no retraining
✅ Auditable: Physics fully visible, no proprietary secrets



📄 License & Status
Research / Academic Project — built for player welfare equity.
