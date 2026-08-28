from fastapi import FastAPI
from pydantic import BaseModel
import tensorflow as tf
import numpy as np

app = FastAPI(title="Ball2Head — Impact Energy")

# Load model & scaler
model = tf.keras.models.load_model("./models/energy_model.h5")
mean_, scale_ = np.load("./models/scaler.npy")

class SensorData(BaseModel):
    ax: float
    ay: float
    az: float

@app.post("/api/calculate-energy")
def calc_energy(data: SensorData):
    vec = np.array([[data.ax, data.ay, data.az]])
    vec_s = (vec - mean_) / scale_
    pred_J = float(model.predict(vec_s, verbose=0)[0][0])
    return {"impact_energy_J": round(pred_J, 6)}