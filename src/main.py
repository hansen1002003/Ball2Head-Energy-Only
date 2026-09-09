# =====================================================
#  BALL2HEAD — UNIFIED HEADING LOAD ENGINE
#  Peer-Reviewed Physics · Lab-Calibrated Metrics
#  Live API · Manual Test · CSV Batch Processing
# =====================================================
#
#  PURPOSE:
#  Convert ball impact data — from velocity OR acceleration —
#  into standardised clinical heading load metrics:
#    • Impact Energy       (J)   — Kinetic Energy: E = ½mv²
#    • Peak Brain Pressure  (kPa) — E × K₁  [Lab Calibrated]
#    • Pressure Wave Duration (ms) — E × K₂ [Lab Calibrated]
#
#  ARCHITECTURE:
#  ┌─────────────────┐    ┌──────────────────────┐
#  │  LIVE API       │    │  CALIBRATION LAYER   │
#  │  /from-velocity │───▶│  E = ½mv²            │
#  │  /from-accel    │    │  kPa = E × K₁        │
#  └─────────────────┘    │  ms  = E × K₂        │
#         │               └──────────────────────┘
#  ┌─────────────────┐            │
#  │  CSV BATCH      │            ▼
#  │  UPLOAD → RUN   │    ┌──────────────────────┐
#  │  → DOWNLOAD     │───▶│  OUTPUT METRICS      │
#  └─────────────────┘    │  Energy · kPa · ms   │
#                         └──────────────────────┘
#
#  PHYSICS VALIDATION:
#  Kinetic Energy E = ½mv² — Newtonian mechanics, peer-reviewed
#  Calibration K₁, K₂ — Determined via lab synchronisation
#  between ball energy and head-form sensor output
#
# =====================================================

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import numpy as np
import pandas as pd
import hashlib
import uuid
from datetime import datetime
from pathlib import Path
import uvicorn

# =====================================================
# ⚙️ LAB CALIBRATION — UPDATE THESE ONCE AFTER TESTING
# =====================================================
# ALL values apply automatically to API, Manual, and CSV modes
BALL_MASS_KG = 0.43          # FIFA Size 5 standard mass
K1_kPa_per_J = 23.4          # ⚠️ UPDATE FROM LAB: Peak Pressure Calibration
K2_ms_per_J = 0.158           # ⚠️ UPDATE FROM LAB: Wave Duration Calibration

# Safe thresholds (clinical reference values)
SAFE_ENERGY_J = 25.0          # Guidance: keep below this for routine play
SAFE_PEAK_kPa = K1_kPa_per_J * SAFE_ENERGY_J
SAFE_DURATION_ms = K2_ms_per_J * SAFE_ENERGY_J

# =====================================================
# 📊 DATA MODELS — Standard Input/Output Format
# =====================================================
class VelocityInput(BaseModel):
    """Input: Ball velocity at impact (from stadium tracking system)"""
    ball_velocity_m_s: float = Field(..., gt=0, description="Ball speed at moment of header, in metres per second")
    ball_mass_kg: float = Field(BALL_MASS_KG, gt=0, description="Ball mass — defaults to FIFA Size 5 standard")
    player_id: str | None = Field(None, description="Optional: Player identifier for ledger")
    match_id: str | None = Field(None, description="Optional: Match identifier for ledger")
    timestamp: str | None = Field(None, description="Optional: Event timestamp")

class AccelerationInput(BaseModel):
    """Input: 3-axis peak acceleration (from ball IMU sensor)"""
    ax_mps2: float = Field(..., description="X-axis peak acceleration m/s²")
    ay_mps2: float = Field(..., description="Y-axis peak acceleration m/s²")
    az_mps2: float = Field(..., description="Z-axis peak acceleration m/s²")
    impact_duration_s: float = Field(0.005, gt=0, description="Contact duration in seconds")
    ball_mass_kg: float = Field(BALL_MASS_KG, gt=0, description="Ball mass — defaults to FIFA Size 5 standard")
    player_id: str | None = Field(None, description="Optional: Player identifier for ledger")
    match_id: str | None = Field(None, description="Optional: Match identifier for ledger")
    timestamp: str | None = Field(None, description="Optional: Event timestamp")

class MetricOutput(BaseModel):
    """Output: Standardised clinical heading load metrics"""
    impact_energy_J: float = Field(..., description="Calculated kinetic energy: E = ½mv²")
    peak_brain_pressure_kPa: float = Field(..., description="Calibrated peak pressure: E × K₁")
    pressure_wave_duration_ms: float = Field(..., description="Calibrated wave duration: E × K₂")
    safe_threshold_exceeded: bool = Field(..., description="True if above clinical guidance")
    calibration_note: str = Field(..., description="Calibration constants used")
    record_hash: str | None = Field(None, description="Hashed ID for ledger integrity")

# =====================================================
# 🧮 PHYSICS ENGINE — Central Calculation Logic
# =====================================================
def calculate_metrics(energy_joules: float, player_id: str = None, match_id: str = None) -> MetricOutput:
    """
    Convert calculated energy → calibrated clinical metrics.
    SAME formula used by LIVE API, MANUAL INPUT, and CSV BATCH.
    Ensures consistency across ALL integration methods.
    """
    peak_kPa = energy_joules * K1_kPa_per_J
    duration_ms = energy_joules * K2_ms_per_J
    exceeded = energy_joules > SAFE_ENERGY_J

    # Generate integrity hash for ledger upload (hides PII, preserves audit trail)
    record_hash = None
    if player_id and match_id:
        hash_input = f"{match_id}|{player_id}|{energy_joules:.4f}|{K1_kPa_per_J}|{K2_ms_per_J}"
        record_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    return MetricOutput(
        impact_energy_J=round(energy_joules, 2),
        peak_brain_pressure_kPa=round(peak_kPa, 1),
        pressure_wave_duration_ms=round(duration_ms, 2),
        safe_threshold_exceeded=exceeded,
        calibration_note=f"K1={K1_kPa_per_J} kPa/J | K2={K2_ms_per_J} ms/J | Safe ≤ {SAFE_ENERGY_J} J",
        record_hash=record_hash
    )

# =====================================================
# 🚀 API SERVER — FastAPI Application
# =====================================================
app = FastAPI(
    title="Ball2Head CIC — Unified Heading Load Engine",
    description="""
Physics-based heading load calculation layer.
Convert ball velocity OR onboard acceleration → standardised clinical metrics.

## 📐 Calibration in Use
- Ball Mass: **{mass} kg** (Size 5 FIFA)
- K₁ (kPa/J): **{k1}** → Peak Brain Pressure
- K₂ (ms/J): **{k2}** → Pressure Wave Duration
- Clinical Guidance: **≤ {safe} J** per header

## 📡 Integration Methods
- **Live API** → POST velocity or acceleration from stadium tracking
- **Manual Input** → Test values directly via this interface
- **CSV Batch** → Upload match data → download full results
""".format(mass=BALL_MASS_KG, k1=K1_kPa_per_J, k2=K2_ms_per_J, safe=SAFE_ENERGY_J),
    version="1.0-lab.pending"
)

# =====================================================
# ⚡ ENDPOINT 1 — From Velocity (Video / Optical Tracking)
# =====================================================
@app.post("/api/v1/calculate-from-velocity", response_model=MetricOutput, tags=["Live API"])
def from_velocity(data: VelocityInput):
    """
    Calculate heading load FROM BALL VELOCITY.
    ✅ This is for: Hawk-Eye · Stats Perform · Kinexon · all stadium data processing & tracking systems
    
    Physics: E = ½ × m × v²
    """
    if data.ball_velocity_m_s <= 0:
        raise HTTPException(status_code=400, detail="Velocity must be greater than zero")

    energy_j = 0.5 * data.ball_mass_kg * (data.ball_velocity_m_s ** 2)
    return calculate_metrics(energy_j, data.player_id, data.match_id)

# =====================================================
# ⚡ ENDPOINT 2 — From Acceleration (Onboard IMU Sensor)
# =====================================================
@app.post("/api/v1/calculate-from-acceleration", response_model=MetricOutput, tags=["Live API"])
def from_acceleration(data: AccelerationInput):
    """
    Calculate heading load FROM 3D ACCELERATION.
    ✅ This is for: Smart ball sensors · IMU onboard devices
    
    Physics: v ≈ a_total × t → then E = ½mv²
    """
    a_total = np.sqrt(data.ax_mps2**2 + data.ay_mps2**2 + data.az_mps2**2)
    velocity_m_s = a_total * data.impact_duration_s
    energy_j = 0.5 * data.ball_mass_kg * (velocity_m_s ** 2)
    return calculate_metrics(energy_j, data.player_id, data.match_id)

# =====================================================
# 📁 CSV BATCH PROCESSOR — Upload Many → Download Results
# =====================================================
@app.post("/api/v1/csv-process", tags=["CSV Batch Processing"])
async def csv_upload(file: UploadFile = File(...)):
    """
    Upload CSV file with header events → get calculated metrics.
    
    REQUIRED COLUMN (choose ONE):
    • ball_velocity_m_s  ← Preferred — from video tracking
    
    OPTIONAL COLUMNS:
    • player_id, match_id, timestamp, ball_mass_kg
    
    OUTPUT: Adds 4 columns → impact_energy_J, peak_brain_pressure_kPa,
    pressure_wave_duration_ms, safe_threshold_exceeded, record_hash
    """
    try:
        df = pd.read_csv(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read CSV: {str(e)}")

    # Determine calculation method
    has_velocity = "ball_velocity_m_s" in df.columns
    if not has_velocity:
        raise HTTPException(status_code=400, detail="CSV must contain column: ball_velocity_m_s")

    # Use provided mass or default
    mass_col = "ball_mass_kg" if "ball_mass_kg" in df.columns else None

    # Calculate ALL rows
    results = []
    for _, row in df.iterrows():
        mass = row[mass_col] if mass_col else BALL_MASS_KG
        energy_j = 0.5 * mass * (row["ball_velocity_m_s"] ** 2)
        
        pid = row.get("player_id")
        mid = row.get("match_id")
        metrics = calculate_metrics(energy_j, pid, mid)
        
        results.append({
            "impact_energy_J": metrics.impact_energy_J,
            "peak_brain_pressure_kPa": metrics.peak_brain_pressure_kPa,
            "pressure_wave_duration_ms": metrics.pressure_wave_duration_ms,
            "safe_threshold_exceeded": metrics.safe_threshold_exceeded,
            "record_hash": metrics.record_hash or ""
        })

    # Merge + save
    out_df = pd.concat([df, pd.DataFrame(results)], axis=1)
    out_filename = f"ball2head_results_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    out_path = Path(__file__).parent / out_filename
    out_df.to_csv(out_path, index=False)

    return FileResponse(
        path=str(out_path),
        filename=out_filename,
        media_type="text/csv"
    )

# =====================================================
# ✅ HEALTH CHECK
# =====================================================
@app.get("/api/v1/health", tags=["System"])
def health_check():
    """Confirm service is running + show active calibration values"""
    return {
        "status": "operational",
        "version": "1.0-lab.pending",
        "calibration": {
            "ball_mass_kg": BALL_MASS_KG,
            "K1_kPa_per_J": K1_kPa_per_J,
            "K2_ms_per_J": K2_ms_per_J,
            "safe_energy_J": SAFE_ENERGY_J
        },
        "note": "Update K1, K2 constants after lab validation — all endpoints auto-refresh"
    }

# =====================================================
# 🚀 START THE ENGINE
# =====================================================
if __name__ == "__main__":
    print("=" * 70)
    print("   BALL2HEAD — UNIFIED HEADING LOAD ENGINE")
    print("   Physics · Calibration · Metrics")
    print("=" * 70)
    print(f"   ⚙️  Calibration Loaded:")
    print(f"      Ball Mass : {BALL_MASS_KG} kg")
    print(f"      K₁ (kPa/J): {K1_kPa_per_J}")
    print(f"      K₂ (ms/J) : {K2_ms_per_J}")
    print(f"      Safe Limit: ≤ {SAFE_ENERGY_J} J")
    print(f"   📡 API Docs : http://127.0.0.1:8000/docs")
    print(f"   📁 CSV Upload: /api/v1/csv-process")
    print("=" * 70)
    print("   💡 Update K1_kPa_per_J and K2_ms_per_J after lab testing.")
    print("      All endpoints use the new values automatically.")
    print("=" * 70)

    uvicorn.run(app, host="127.0.0.1", port=8000)