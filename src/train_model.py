import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error

import tensorflow as tf

# ==========================================
# LOAD CLEAN DATA
# ==========================================
df = pd.read_csv("../data/ball_energy_dataset.csv")

# Inputs: 3-axis acceleration
X = df[["ax_m_s2", "ay_m_s2", "az_m_s2"]].values

# Target: Known impact energy
y = df["total_energy_J"].values

# ==========================================
# SPLIT & SCALE
# ==========================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

# ==========================================
# MINIMAL MODEL — Learns ONLY small corrections
# ==========================================
model = tf.keras.Sequential([
    tf.keras.layers.Dense(16, activation='relu', input_shape=(3,)),
    tf.keras.layers.Dense(1)
])

model.compile(optimizer='adam', loss='mse')

# ==========================================
# TRAIN
# ==========================================
print("🔄 Training model...")
model.fit(
    X_train_s, y_train,
    epochs=50,
    batch_size=8,
    validation_data=(X_test_s, y_test),
    verbose=1
)

# ==========================================
# SAVE MODEL + SCALER
# ==========================================
model.save("../models/energy_model.h5")
np.save("../models/scaler.npy", [scaler.mean_, scaler.scale_])
print("\n💾 Saved → energy_model.h5 + scaler.npy")

# ==========================================
# EVALUATE — MSE + R² + MAE
# ==========================================
# Get predictions
y_pred = model.predict(X_test_s, verbose=0).flatten()

# Calculate metrics
mse = np.mean(np.square(y_test - y_pred))
rmse = np.sqrt(mse)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

# Unix timestamp — consistent across entire project
unix_time_now = int(pd.Timestamp.now().timestamp())

# ==========================================
# PRINT CLEAR SUMMARY
# ==========================================
print("\n" + "="*50)
print("📊 MODEL PERFORMANCE — Unix Timestamp:", unix_time_now)
print("="*50)
print(f"  Mean Squared Error (MSE):  {mse:.8f}")
print(f"  Root Mean Sq Error (RMSE): {rmse:.8f}")
print(f"  Mean Abs Error (MAE):      {mae:.8f} J")
print(f"  R² Score (Accuracy):       {r2:.4f}  (~{r2*100:.1f}%)")
print("="*50)

# R² Interpretation — simple to quote anywhere
if r2 >= 0.95:
    print("✅ EXCELLENT — Physics + corrections explain ~95%+ of variation")
elif r2 >= 0.90:
    print("✅ VERY GOOD — Physics explains most, model fine-tunes well")
elif r2 >= 0.80:
    print("⚠️ ACCEPTABLE — More data may improve precision")
else:
    print("⚠️ NEEDS REVIEW — Check data quality or sample size")

print(f"\n⏳ Timestamp for this training run (Unix): {unix_time_now}")