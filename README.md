# ⚽ Ball2Head — Physics-First Impact Energy Framework
**Pure Physics Core + Future AI Refinement • Auditable • Historical-Ready • BLE Live Stream**

---

## 🎯 **Project Overview**
Ball2Head calculates football heading impact energy directly from smart-ball IMU data:
- **Layer A (Current)**: **First-principles physics** — no training required, works on *any* historical logs
- **Layer B (Future)**: Optional AI refinement — only for real-world minor corrections
- **Built on**: PINN methodology (Raissi et al., 2019) — physics is always the constraint, never learned

---

## 🧠 **How It Works**
### Core Physics (`src/compute_energy.py`)
> **Universal, auditable — no black box**
1. **Total Acceleration**: \(a_{\text{total}} = \sqrt{a_x^2 + a_y^2 + a_z^2}\)
2. **Velocity Change**: \(\Delta v = a_{\text{total}} \cdot \Delta t\) (sampling rate = 500 Hz)
3. **Impact Energy**: \(E = \frac{1}{2} m v^2\) — FIFA-standard ball mass \(m = 0.43\ \text{kg}\)

### Architecture


---

## 🚀 **How to Run**

### 1. Install Dependencies
```bash
pip install -r requirements.txt


Start API Server
uvicorn src.api:app --reload

Endpoints:
POST /api/calculate-energy — Manual input: {ax, ay, az}
WS /ws/live-ball — 📡 Live Trionda ball stream
GET /csv/download — Download full log

Run Direct Ball Streamer
python src/ball_streamer.py
Scans → connects → prints live energy readings.

📚 Scientific References
Raissi et al. (2019) — Physics-Informed Neural Networks framework
Stone et al. (2016) — Smart-ball IMU validation
Goldstein (2002) — Classical mechanics derivation
Young & Freedman (2016) — Standard constants & units


✅ Key Advantages
✅ Historical-ready: Works on any existing IMU logs — no retraining
✅ Auditable: Physics fully visible, no proprietary secrets
✅ Safe: Automatic fallback — impossible values rejected
✅ BLE-ready: Native support for Trionda smart ball
✅ Future-proof: Layer B can be added later without breaking core



📄 License & Status
Research / Academic Project — built for player welfare equity.
