import numpy as np
# FIFA standard constants
M_BALL = 0.43       # kg - official mass of size 5 football
SAMPLE_RATE = 500   # Hz - Trionda IMU sample rate
DT = 1 / SAMPLE_RATE # Time interval between samples (s)

def compute_impact_energy(ax, ay, az): 
    # Pythagoras: total acceleration magnitude
    a_total = np.sqrt(ax**2 + ay**2 + az**2)

    # Kinematics: velocity change = acceleration * time step
    delta_v = a_total * DT

    #Kinetic Energy Theorem: E = 0.5 * m * v^2
    return 0.5 * M_BALL * (delta_v ** 2)