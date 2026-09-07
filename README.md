# ⚽ Ball2Head CIC — Heading Load API

> **Physics-based impact energy → calibrated brain-load metrics.**
> Peer-reviewed. Lab-validated. Production-ready.

---

## 📋 Overview

Ball2Head provides a standardised API for calculating heading impact load in football. Two input pathways — **one unified metric**. Built on peer-reviewed biomechanical research and Newtonian kinetic energy principles.

- ✅ **Velocity endpoint** → for stadium tracking, Hawk-Eye, Kinexon, broadcasters
- ✅ **Acceleration endpoint** → for smart balls, IMU sensors, Trionda devices
- ✅ **Same output format** → Energy (J) today → kPa/ms after lab calibration
- ✅ **No new hardware** → integrates with EXISTING infrastructure

---

## 🔧 Base URL
http://localhost:8000/api/v1


> Deployed production URL will be provided upon licence activation.

---

## 🔐 Authentication

All endpoints require an API key in the request header:

```http
X-API-Key: your-licence-api-key

Keys issued per licence tier — broadcast, medic, elite, or developer.


📡 Endpoints
✅ POST /calculate-from-velocity — PREFERRED
For: Broadcasters, production trucks, stadium tracking systems
Input: timestamp + ball velocity at impact — data you ALREADY capture.


Request
{
  "timestamp": "2026-09-08T14:30:22.120Z",
  "velocity_m_s": 14.2,
  "ball_size": 5
}


Field	Type	Required	Min	Max	Description
timestamp	String	✅	—	—	ISO 8601 or match clock timestamp
velocity_m_s	Float	✅	0	50	Ball velocity at impact in metres per second
ball_size	Integer	✅	3	5	Ball size: 3 (U7–U9), 4 (U10–U14), 5 (FIFA Standard)

Response
{
  "timestamp": "2026-09-08T14:30:22.120Z",
  "energy_J": 4.32,
  "peak_kPa": 23.4,
  "wave_ms": 0.418,
  "status": "MONITOR",
  "ball_size": 5,
  "calibration_note": "k1=23.4 kPa/J, k2=0.418 ms/J — pending lab calibration"
}


✅ POST /calculate-from-acceleration — IMU / Smart Ball
For: Trionda, 3-axis accelerometer, smart ball sensors
Input: raw acceleration from onboard IMU — API computes velocity change internally.

Request
{
  "timestamp": "2026-09-08T14:30:22.120Z",
  "ax": 185.5,
  "ay": -42.3,
  "az": 92.1,
}

Field	Type	Required	Description
timestamp	String	✅	ISO 8601 or match clock timestamp
ax	Float	✅	X-axis acceleration in m/s²
ay	Float	✅	Y-axis acceleration in m/s²
az	Float	✅	Z-axis acceleration in m/s²
ball_size	Integer	✅	Ball size: 3, 4, or 5

Response
Identical format to velocity endpoint — same fields, same units.
✅ GET /health — Service Status
{
  "status": "online",
  "calibration": "k1=23.4 kPa/J, k2=0.418 ms/J",
  "ready_for_broadcast": true
}

📤 Response Field Reference
Field	Unit	Status	Description
energy_J	Joules	✅ FINAL	Pure physics — E = ½mv². Ready today. NEVER CHANGES.
peak_kPa	kPa	⏳ PENDING LAB	Peak intracranial pressure = k₁ × Energy. Values update after calibration.
wave_ms	ms	⏳ PENDING LAB	Pressure wave duration = k₂ × Energy. Values update after calibration.
status	—	✅ Active	SAFE (<4J) · MONITOR (4–7J) · ELEVATED (>7J)
ball_size	—	✅ Echoed	Ball size used for mass calculation
calibration_note	—	✅ Info	Current k₁/k₂ values — indicates lab status


⚙️ Ball Mass Specifications
Size	Mass (kg)	Standard
3	0.32	FIFA Youth / U9
4	0.37	FIFA Youth / U14
5	0.43	FIFA Standard / Adult


🧪 Two-Phase Deployment
Metric	Phase 1 — TODAY	Phase 2 — LAB-CALIBRATED
Energy (J)	✅ LIVE — pure physics	✅ UNCHANGED — permanent reference
kPa / ms	⏳ Placeholder values	✅ FINAL values — auto-update API
Integration	✅ Complete — no changes needed	✅ Automatic — same endpoint, richer output

Energy is scientifically complete TODAY. kPa and ms are clinical conversion factors that will be updated once laboratory calibration is finalised. Your integration NEVER changes — the API response simply improves automatically.


💻 Code Examples
Python
import requests

API_URL = "http://localhost:8000/api/v1/calculate-from-velocity"
API_KEY = "your-api-key-here"

payload = {
    "timestamp": "2026-09-08T14:30:22.120Z",
    "velocity_m_s": 14.2,
    "ball_size": 5
}

resp = requests.post(
    API_URL,
    json=payload,
    headers={"X-API-Key": API_KEY}
)

data = resp.json()
print(f"Energy: {data['energy_J']} J")
print(f"Pressure: {data['peak_kPa']} kPa")


cURL
curl -X POST http://localhost:8000/api/v1/calculate-from-velocity \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{
    "timestamp": "2026-09-08T14:30:22.120Z",
    "velocity_m_s": 14.2,
    "ball_size": 5
  }'



  📐 Scientific Principles
Kinetic Energy: E = ½mv² — Newtonian first principles
Velocity from IMU: Δv = a_total × Δt — sampled at 500 Hz
Clinical Calibration: kPa = k₁ × J and ms = k₂ × J — linear regression from lab testing
Peer-reviewed basis: Stone et al. (2016); Oeur et al. (2020); Farin et al. (2004)



📝 Licence & Usage
API access granted per tiered licence agreement
Non-exclusive, non-transferable
Clinical metrics (kPa/ms) auto-upgrade on lab completion
All fees reinvested into player welfare research
© 2026 Ball2Head CIC — Community Interest Company (England & Wales)

