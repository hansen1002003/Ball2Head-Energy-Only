import numpy as np
# FIFA standard constants
M_BALL = 0.43       # kg
SAMPLE_RATE = 500   # Hz
DT = 1 / SAMPLE_RATE

def compute_impact_energy(ax, ay, az):
    a_total = np.sqrt(ax**2 + ay**2 + az**2)
    delta_v = a_total * DT
    return 0.5 * M_BALL * (delta_v ** 2)