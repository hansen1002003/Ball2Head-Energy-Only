"""
Ball2Head — API Endpoint
========================
Separate FastAPI service — deploy separately
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid

app = FastAPI(title="Ball2Head API", version="1.0.0")

# Calibration — same as Streamlit
class Calibration:
    BALL_MASS_DRY_KG = 0.430
    DRY_k1_KPA_PER_J = 1.19
    DRY_k2_MS_PER_J = 0.067
    WET_FACTORS = {"dry": 1.00, "damp": 1.10, "wet_synthetic": 1.25}

def calculate_metrics(velocity_mps: float, condition: str = "dry"):
    if velocity_mps <= 0:
        raise ValueError("Velocity must be greater than 0")
    energy_j = 0.5 * Calibration.BALL_MASS_DRY_KG * (velocity_mps ** 2)
    factor = Calibration.WET_FACTORS.get(condition.lower().strip(), 1.00)
    k1 = Calibration.DRY_k1_KPA_PER_J * factor
    k2 = Calibration.DRY_k2_MS_PER_J * factor
    
    baseline_kpa = round(Calibration.DRY_k1_KPA_PER_J * energy_j, 2)
    baseline_ms = round(Calibration.DRY_k2_MS_PER_J * energy_j, 3)
    adj_kpa = round(k1 * energy_j, 2)
    adj_ms = round(k2 * energy_j, 3)
    
    cat = "LOW" if adj_kpa < 30 else "MODERATE" if adj_kpa < 60 else "HIGH" if adj_kpa < 90 else "EXTREME"
    
    return {
        "energy_j": round(energy_j, 2),
        "baseline_dry_kpa": baseline_kpa,
        "baseline_dry_ms": baseline_ms,
        "adjusted_kpa": adj_kpa,
        "adjusted_ms": adj_ms,
        "wet_factor": factor,
        "category": cat
    }

class Request(BaseModel):
    match_id: str = None
    timestamp: str = None
    ball_velocity_mps: float
    condition: str = "dry"

@app.post("/v1/calculate")
def api_calc(req: Request):
    try:
        res = calculate_metrics(req.ball_velocity_mps, req.condition)
        return {
            "calculation_id": f"b2h_{uuid.uuid4().hex[:8]}",
            "match_id": req.match_id,
            "timestamp": req.timestamp,
            **res,
            "reference": "Phillips et al. (2026) — A1/B1 Mean — FIFA 430g"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)