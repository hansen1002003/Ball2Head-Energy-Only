# ⚽ Ball2Head — Unified Heading Exposure Calculator & Brain Health Ledger

> **Peer-reviewed, open-source framework for estimating heading load in football.**   
> 🟢 **Live App:** [ball2head.streamlit.app](https://ball2head.streamlit.app)
> 
> **Calibrated against Phillips et al. (2026) Pressure Wave Propagation Data**

## Overview
Ball2Head calculates **Peak-to-Peak Pressure (kPa)** and **PPSI₉₀ Total Pressure Wave Duration (ms)** from **ball velocity only** — no head sensors required. Designed for stadium tracking, computer vision, and elite/youth match analysis.

## Key Metrics
- **Input**: Ball impact velocity (m/s)
- **Output 1**: Peak-to-Peak Pressure (kPa) — from E = ½mv² → P = k₁·E
- **Output 2**: PPSI₉₀ Duration (ms) — total pressure wave duration, NOT rise time
- **Why no Rise Time?** Requires 500Hz+ sensor sampling — unavailable from stadium tracking/vision

## Coverage
- **All 7 ball types** (A1–G1) from Phillips et al. (2026)
- **All sizes**: 3 (U10), 4 (U14), 5 (Elite) — FIFA-standard mass scaling
- **All conditions**: Dry (100%), Damp (+3% mass), Wet (+6% mass)

## Methodology
- **k₁ (kPa/J)** and **k₂ (ms/J)** directly from Phillips lab calibration
- Mass scaling: Size 3 = 0.78, Size 4 = 0.90, Size 5 = 1.00
- Water absorption: Damp +3%, Wet +6% → pressure scales linearly with mass

## Status
✅ Velocity-only model — fully scalable across elite, youth, grassroots
✅ Peer-reviewed foundation — no lab testing required for core metrics
