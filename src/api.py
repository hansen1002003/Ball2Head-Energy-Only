# ==========================================
# BALL2HEAD API — Impact Energy Calculation & Live Stream
# Purpose: Take acceleration data → return impact energy using PHYSICS first, AI second
# Rule: Physics is ALWAYS the foundation. AI only helps when it is proven reliable.
# ==========================================

# Standard tools we need
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
# SMART PATH SETUP — NO MORE "FILE NOT FOUND" ERRORS
# Figures out where your files are automatically, so you can run from any folder
# ==========================================

# Finds the folder THIS file (api.py) is sitting in
SCRIPT_DIR = Path(__file__).resolve().parent   # This points to: src/ folder

# Go UP one folder — so we land in the main project folder
PROJECT_ROOT = SCRIPT_DIR.parent               # This points to: Ball2Head-Energy-Only/

# Tell Python: "Also look in this same src folder when importing files"
# This fixes the "No module named compute_energy" error
sys.path.append(str(SCRIPT_DIR))

# Now we can safely find our model files — ALWAYS works, no guessing
MODEL_PATH = PROJECT_ROOT / "models" / "energy_model.h5"
SCALER_PATH = PROJECT_ROOT / "models" / "scaler.npy"
CSV_FILE = PROJECT_ROOT / "live_stream_log.csv"

# Print where we are looking — helps if anything goes wrong
print(f"📂 Project Root: {PROJECT_ROOT}")
print(f"📂 Model Path: {MODEL_PATH}")

# ✅ Import our PHYSICS FORMULA — lives in compute_energy.py
# This is where the real calculation happens — pure math, no black box
from compute_energy import compute_impact_energy

# ==========================================
# START THE API SERVER
# ==========================================
app = FastAPI(title="Ball2Head — Impact Energy + Live Trionda Stream")

# Load our trained AI model (once, when server starts)
# Note: Model is just a helper — PHYSICS is the boss
model = tf.keras.models.load_model(str(MODEL_PATH))

# Load the scaling numbers we saved during training
# These let the AI understand normalised input correctly
mean_, scale_ = np.load(str(SCALER_PATH))

# ==========================================
# WHAT INPUT WE ACCEPT
# Tells the API: "We need 3 numbers — acceleration in X, Y, Z directions"
# ==========================================
class SensorData(BaseModel):
    ax: float   # Acceleration along X axis (m/s²)
    ay: float   # Acceleration along Y axis (m/s²)
    az: float   # Acceleration along Z axis (m/s²)

# ==========================================
# SAVE EVERYTHING TO CSV — FOR AUDIT & LATER USE
# Creates a log file so we can see every calculation ever made
# ==========================================

# What columns we will save in the CSV file
CSV_HEADERS = [
    "timestamp_unix", "time_readable",       # When it happened
    "ax_m_s2", "ay_m_s2", "az_m_s2",         # Raw input
    "energy_physics_J", "energy_model_J",     # Both answers — Physics vs AI
    "source"                                  # Where it came from (manual or live ball)
]

# If CSV file doesn't exist yet → create it and write the column headers
if not CSV_FILE.exists():
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(CSV_HEADERS)

def save_to_csv(ax, ay, az, energy_physics, energy_model, source):
    """Save every single calculation to CSV automatically"""
    now = datetime.now()  # Get current time
    
    # Put everything in one row
    row = [
        now.timestamp(),                          # Computer-friendly time
        now.strftime("%Y-%m-%d %H:%M:%S.%f"),    # Easy-to-read time
        round(ax, 6), round(ay, 6), round(az, 6), # Inputs neatly rounded
        round(energy_physics, 8), round(energy_model, 8), # Both results
        source                                     # Manual input or live ball?
    ]
    
    # Append this row to our log file
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(row)

# ==========================================
# MAIN ENDPOINT — CALCULATE IMPACT ENERGY
# This is where the magic happens: PHYSICS first, AI second
# ==========================================
@app.post("/api/calculate-energy")
def calc_energy(data: SensorData):
    # STEP 1: ALWAYS RUN PHYSICS FIRST — THIS IS THE FOUNDATION
    # We NEVER skip this. Physics is always correct, always auditable.
    physics_J = compute_impact_energy(data.ax, data.ay, data.az)

    # STEP 2: ASK AI FOR ITS OPINION — BUT ONLY TRUST IF IT MAKES SENSE
    try:
        # Format acceleration data the way the AI expects
        vec = np.array([[data.ax, data.ay, data.az]])
        vec_s = (vec - mean_) / scale_  # Apply same scaling as during training
        
        # Ask AI to predict the energy
        model_J = float(model.predict(vec_s, verbose=0)[0][0])

        # ✅ THE SAFETY CHECK — IS THE AI ANSWER REASONABLE?
        # Rule 1: Energy can NEVER be negative (impossible in real life)
        # Rule 2: AI answer shouldn't be wildly different from physics
        if model_J > 0 and abs(model_J - physics_J) < (physics_J * 1.5):
            final_J = model_J   # ✅ AI looks good → use its refined answer
        else:
            final_J = physics_J # ⚠️ AI is wrong → FALL BACK TO PHYSICS
            
    except Exception:
        # If anything breaks with AI → just use physics, no problem
        final_J = physics_J

    # STEP 3: SAVE BOTH ANSWERS — so we can compare later
    save_to_csv(data.ax, data.ay, data.az, physics_J, final_J, "api_post")

    # Return the FINAL answer (safe, trusted) + pure physics for reference
    return {
        "impact_energy_J": round(final_J, 6),          # What you should use
        "_physics_reference_J": round(physics_J, 6)    # Always keep the pure physics for audit
    }

# ==========================================
# LIVE BALL CONNECTION — Trionda Smart Ball via Bluetooth
# This section handles connecting to the real ball wirelessly
# ==========================================

# Bluetooth codes to find & talk to the Trionda ball
# These are standard ID numbers — given by the ball manufacturer
TRIONDA_SERVICE_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb"
TRIONDA_CHAR_UUID    = "0000ffe4-0000-1000-8000-00805f9b34fb"
TRIONDA_NAME_KEYWORD = "Trionda"  # Ball name we search for

# Try to load Bluetooth library — tell user if not installed
try:
    from bleak import BleakScanner, BleakClient
    BLE_AVAILABLE = True
except ImportError:
    BLE_AVAILABLE = False
    print("⚠️ Bleak not installed. Run: pip install bleak")

# Keep track of who is connected and streaming status
active_connections = set()   # List of dashboard connections
bleak_client = None          # Our connection to the ball
streaming_active = False     # Is ball currently sending data?


def decode_and_calculate(raw_bytes: bytes):
    """
    Convert raw numbers coming from the ball → real acceleration values
    The ball sends compressed integers — we convert them back to m/s²
    """
    ax = int.from_bytes(raw_bytes[0:2], byteorder='little', signed=True) / 100.0
    ay = int.from_bytes(raw_bytes[2:4], byteorder='little', signed=True) / 100.0
    az = int.from_bytes(raw_bytes[4:6], byteorder='little', signed=True) / 100.0
    return ax, ay, az


async def handle_ball_data(_, raw_data: bytes):
    """
    EVERY TIME THE BALL SENDS A READING — THIS FUNCTION RUNS
    Decode → calculate physics → ask AI → save → send to dashboard
    """
    global streaming_active
    if not streaming_active:
        return  # Not streaming yet → ignore
    
    # Turn raw bytes into real acceleration numbers
    ax, ay, az = await decode_and_calculate(raw_data)
    
    # Calculate PHYSICS answer
    energy_physics = compute_impact_energy(ax, ay, az)
    
    # Calculate AI answer
    vec = np.array([[ax, ay, az]])
    vec_s = (vec - mean_) / scale_
    energy_model = float(model.predict(vec_s, verbose=0)[0][0])
    
    # Save BOTH to CSV log
    save_to_csv(ax, ay, az, energy_physics, energy_model, "live_ball")
    
    # Send everything to the dashboard in clean format
    message = {
        "ax": round(ax, 4), "ay": round(ay, 4), "az": round(az, 4),
        "energy_physics_J": round(energy_physics, 6),
        "energy_model_J": round(energy_model, 6),
        "timestamp": datetime.now().isoformat()
    }
    
    # Send to everyone watching the dashboard
    disconnected = set()
    for ws in active_connections:
        try:
            await ws.send_json(message)
        except Exception:
            disconnected.add(ws)  # Mark anyone who dropped off
    active_connections.difference_update(disconnected)


@app.websocket("/ws/live-ball")
async def ws_live_ball(websocket: WebSocket):
    """
    The LIVE STREAM CONNECTION — Dashboard connects here
    This handles: scanning for ball → connecting → receiving data
    """
    global bleak_client, streaming_active
    await websocket.accept()
    active_connections.add(websocket)
    
    try:
        # Check if Bluetooth is available
        if not BLE_AVAILABLE:
            await websocket.send_json({"error": "BLE not installed"})
            return

        # STEP 1: Search for Trionda ball nearby
        await websocket.send_json({"status": "scanning"})
        devices = await BleakScanner.discover()
        target = None
        for d in devices:
            if d.name and TRIONDA_NAME_KEYWORD.lower() in d.name.lower():
                target = d
                break
        
        # Ball not found → tell user
        if not target:
            await websocket.send_json({"status": "error", "message": "Ball not found"})
            return

        # STEP 2: Connect to the ball
        await websocket.send_json({"status": "connecting", "name": target.name})
        bleak_client = BleakClient(target.address)
        await bleak_client.connect()
        streaming_active = True
        await websocket.send_json({"status": "connected"})

        # STEP 3: Ask ball to send acceleration data continuously
        await bleak_client.start_notify(TRIONDA_CHAR_UUID, handle_ball_data)
        
        # Keep connection alive while ball is streaming
        while streaming_active and bleak_client and bleak_client.is_connected:
            await asyncio.sleep(0.5)

    # If user disconnects → end nicely
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"status": "error", "message": str(e)})
    
    # Cleanup: stop ball, close connection
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
# SIMPLE INFORMATION PAGES
# ==========================================

# Homepage — shows what this API can do
@app.get("/")
def root():
    return {
        "name": "Ball2Head Impact Energy API",
        "endpoints": {
            "POST /api/calculate-energy": "Manual input — send ax,ay,az → get energy",
            "WS /ws/live-ball": "Live Trionda ball stream via Bluetooth",
            "GET /csv/download": "Download all saved calculations as CSV"
        },
        "csv_log": str(CSV_FILE.resolve())
    }

# Download the full log file
@app.get("/csv/download")
def download_csv():
    if not CSV_FILE.exists():
        return {"error": "No data calculated yet"}
    return FileResponse(CSV_FILE, filename="ball2head_live_log.csv", media_type="text/csv")