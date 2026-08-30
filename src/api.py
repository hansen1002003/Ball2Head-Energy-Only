# --------------------------
# 🔒 SAFE PATH SETUP
# --------------------------
import sys
from pathlib import Path

# Current folder = src/
SCRIPT_DIR = Path(__file__).resolve().parent
# Add THIS folder to Python search path
sys.path.insert(0, str(SCRIPT_DIR))

# --------------------------
# 🚀 IMPORTS
# --------------------------
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import numpy as np
# Import physics core
from compute_energy import compute_impact_energy

# --------------------------
# 🛡️ CIC CLOUD APPLICATION
# --------------------------
app = FastAPI(
    title="Ball2Head CIC — Physics-Only Engine",
    description="Locked, validated impact energy calculation service",
    version="2.0-cic-secured"
)

# ✅ SECURITY: Valid API keys issued ONLY via signed contract
VALID_API_KEYS = {
    "CIC-DEMO-KEY-2026": "internal-test"
}

# --------------------------
# 📦 DATA SCHEMA — CLEAN INPUT
# --------------------------
class IMUData(BaseModel):
    ax: float
    ay: float
    az: float
    sampling_rate: float = 500.0  # ✅ IEEE standard default
    timestamp: float | None = None  # ✅ Optional → becomes null if missing

# --------------------------
# ✅ SECURED ENDPOINT — CLEAN RESPONSE
# --------------------------
@app.post("/api/v1/calculate-energy", summary="Compute validated impact energy")
def calculate(
    data: IMUData,
    x_api_key: str = Header(..., description="Contract-issued secure access key")
):
    # 🔐 Key validation — first line of defence
    if x_api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=403, detail="Unauthorised: Invalid API key")

    try:
        # ✅ Calculate time step safely
        dt = 1.0 / data.sampling_rate
        # ✅ Pure physics calculation
        energy_J = compute_impact_energy(data.ax, data.ay, data.az, dt)
        
        # ✅ RESPONSE: ONLY energy + timestamp (null if missing)
        return {
            "energy_J": round(energy_J, 6),
            "timestamp": data.timestamp
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Calculation error: {str(e)}")