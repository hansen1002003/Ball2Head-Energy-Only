from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from pydantic import BaseModel
import tensorflow as tf
import numpy as np
import asyncio
import csv
from datetime import datetime
from pathlib import Path
import os
import sys

# ==========================================
# ✅ SAFE AUTOMATIC PATHS + FIX IMPORT PATH
# ==========================================
SCRIPT_DIR = Path(__file__).resolve().parent   # src/ folder
PROJECT_ROOT = SCRIPT_DIR.parent               # root folder

# ✅ CRITICAL: Tell Python to look inside src/ for compute_energy.py
sys.path.append(str(SCRIPT_DIR))

# ✅ PATHS ALWAYS CORRECT
MODEL_PATH = PROJECT_ROOT / "models" / "energy_model.h5"
SCALER_PATH = PROJECT_ROOT / "models" / "scaler.npy"
CSV_FILE = PROJECT_ROOT / "live_stream_log.csv"

print(f"📂 Project Root: {PROJECT_ROOT}")
print(f"📂 Model Path: {MODEL_PATH}")

# ✅ NOW IMPORT WORKS — because we added sys.path
from compute_energy import compute_impact_energy

# ==========================================
# INITIALISE APP
# ==========================================
app = FastAPI(title="Ball2Head — Impact Energy + Live Trionda Stream")

model = tf.keras.models.load_model(str(MODEL_PATH))
mean_, scale_ = np.load(str(SCALER_PATH))

# ==========================================
# INPUT SCHEMA
# ==========================================
class SensorData(BaseModel):
    ax: float
    ay: float
    az: float

# ==========================================
# CSV LOGGING
# ==========================================
CSV_HEADERS = [
    "timestamp_unix", "time_readable",
    "ax_m_s2", "ay_m_s2", "az_m_s2",
    "energy_physics_J", "energy_model_J", "source"
]

if not CSV_FILE.exists():
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(CSV_HEADERS)

def save_to_csv(ax, ay, az, energy_physics, energy_model, source):
    now = datetime.now()
    row = [
        now.timestamp(),
        now.strftime("%Y-%m-%d %H:%M:%S.%f"),
        round(ax, 6), round(ay, 6), round(az, 6),
        round(energy_physics, 8), round(energy_model, 8),
        source
    ]
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(row)

# ==========================================
# ENDPOINTS
# ==========================================
@app.post("/api/calculate-energy")
def calc_energy(data: SensorData):
    # 1️⃣ ALWAYS RUN PHYSICS FIRST — FOUNDATION
    physics_J = compute_impact_energy(data.ax, data.ay, data.az)

    # 2️⃣ MODEL CORRECTION — AUTOMATIC, IF POSSIBLE
    try:
        vec = np.array([[data.ax, data.ay, data.az]])
        vec_s = (vec - mean_) / scale_
        model_J = float(model.predict(vec_s, verbose=0)[0][0])

        # ✅ INTELLIGENT GUARD: Only use model if it makes PHYSICAL SENSE
        # Reject impossible values (negative energy or way off physics)
        if model_J > 0 and abs(model_J - physics_J) < (physics_J * 1.5):
            final_J = model_J  # ✅ Model is good → use refined result
        else:
            final_J = physics_J  # ⚠️ Model is bad → FALLBACK TO SAFE PHYSICS

    except Exception:
        final_J = physics_J  # ⚠️ Any error → pure physics

    # 3️⃣ LOG BOTH — for audit/training
    save_to_csv(data.ax, data.ay, data.az, physics_J, final_J, "api_post")

    # ✅ RETURN FINAL — CLEAN, TRUSTWORTHY ANSWER
    return {
        "impact_energy_J": round(final_J, 6),
        "_physics_reference_J": round(physics_J, 6)  # Optional: keep for audit
    }

# ==========================================
# LIVE STREAM + BLE
# ==========================================
TRIONDA_SERVICE_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb"
TRIONDA_CHAR_UUID    = "0000ffe4-0000-1000-8000-00805f9b34fb"
TRIONDA_NAME_KEYWORD = "Trionda"

try:
    from bleak import BleakScanner, BleakClient
    BLE_AVAILABLE = True
except ImportError:
    BLE_AVAILABLE = False
    print("⚠️ Bleak not installed. Run: pip install bleak")

active_connections = set()
bleak_client = None
streaming_active = False

async def decode_and_calculate(raw_bytes: bytes):
    ax = int.from_bytes(raw_bytes[0:2], byteorder='little', signed=True) / 100.0
    ay = int.from_bytes(raw_bytes[2:4], byteorder='little', signed=True) / 100.0
    az = int.from_bytes(raw_bytes[4:6], byteorder='little', signed=True) / 100.0
    return ax, ay, az

async def handle_ball_data(_, raw_data: bytes):
    global streaming_active
    if not streaming_active:
        return
    ax, ay, az = await decode_and_calculate(raw_bytes)
    energy_physics = compute_impact_energy(ax, ay, az)
    vec = np.array([[ax, ay, az]])
    vec_s = (vec - mean_) / scale_
    energy_model = float(model.predict(vec_s, verbose=0)[0][0])
    save_to_csv(ax, ay, az, energy_physics, energy_model, "live_ball")
    message = {
        "ax": round(ax, 4), "ay": round(ay, 4), "az": round(az, 4),
        "energy_physics_J": round(energy_physics, 6),
        "energy_model_J": round(energy_model, 6),
        "timestamp": datetime.now().isoformat()
    }
    disconnected = set()
    for ws in active_connections:
        try:
            await ws.send_json(message)
        except Exception:
            disconnected.add(ws)
    active_connections.difference_update(disconnected)

@app.websocket("/ws/live-ball")
async def ws_live_ball(websocket: WebSocket):
    global bleak_client, streaming_active
    await websocket.accept()
    active_connections.add(websocket)
    try:
        if not BLE_AVAILABLE:
            await websocket.send_json({"error": "BLE not installed"})
            return
        await websocket.send_json({"status": "scanning"})
        devices = await BleakScanner.discover()
        target = None
        for d in devices:
            if d.name and TRIONDA_NAME_KEYWORD.lower() in d.name.lower():
                target = d
                break
        if not target:
            await websocket.send_json({"status": "error", "message": "Ball not found"})
            return
        await websocket.send_json({"status": "connecting", "name": target.name})
        bleak_client = BleakClient(target.address)
        await bleak_client.connect()
        streaming_active = True
        await websocket.send_json({"status": "connected"})
        await bleak_client.start_notify(TRIONDA_CHAR_UUID, handle_ball_data)
        while streaming_active and bleak_client and bleak_client.is_connected:
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"status": "error", "message": str(e)})
    finally:
        active_connections.discard(websocket)
        streaming_active = False
        if bleak_client and bleak_client.is_connected:
            try:
                await bleak_client.stop_notify(TRIONDA_CHAR_UUID)
                await bleak_client.disconnect()
            except Exception:
                pass
            bleak_client = None

# ==========================================
# ROOT + DOWNLOAD
# ==========================================
@app.get("/")
def root():
    return {
        "name": "Ball2Head Impact Energy API",
        "endpoints": {
            "POST /api/calculate-energy": "Manual input",
            "WS /ws/live-ball": "Live BLE stream",
            "GET /csv/download": "Download logs"
        },
        "csv_log": str(CSV_FILE.resolve())
    }

@app.get("/csv/download")
def download_csv():
    if not CSV_FILE.exists():
        return {"error": "No data"}
    return FileResponse(CSV_FILE, filename="ball2head_live_log.csv", media_type="text/csv")