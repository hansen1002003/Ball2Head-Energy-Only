import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf

# Load clean data
df = pd.read_csv("../data/ball_energy_dataset.csv")
X = df[["ax_m_s2", "ay_m_s2", "az_m_s2"]].values
y = df["total_energy_J"].values

# Split & scale
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

# Minimal model — learns only correction/linearity
model = tf.keras.Sequential([
    tf.keras.layers.Dense(16, activation='relu', input_shape=(3,)),
    tf.keras.layers.Dense(1)
])
model.compile(optimizer='adam', loss='mse')

# Train
model.fit(X_train_s, y_train, epochs=50, batch_size=8,
          validation_data=(X_test_s, y_test), verbose=1)

# Save
model.save("../models/energy_model.h5")
np.save("../models/scaler.npy", [scaler.mean_, scaler.scale_])

# Evaluate
loss = model.evaluate(X_test_s, y_test, verbose=0)
print(f"✅ Done — Test MSE: {loss:.6f}")