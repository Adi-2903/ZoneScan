"""Run: python examples/score_synthetic.py (from services/api). Inputs are synthetic."""

from datetime import datetime

from zonescan.models import ScoreInputs, Zone
from zonescan.scoring import calculate_strength


timestamp = datetime.fromisoformat("2026-01-05T10:10:00+05:30")
inputs = ScoreInputs(
    day_return=.01,
    daily_sigma20=.02,
    rvol=1.5,
    oi_change_daily_pct=-.025,
    direction="bullish",
    price_above_vwap=True,
    price_above_ema20=False,
    structure="range",
    sector="neutral",
    current_price=110.0,
    atr=1.0,
    nearest_zone=Zone("SYN-Z1", "SYNTHETIC-X", "bullish", 106.5, 107.5,
                      "5m", timestamp, timestamp),
)
result = calculate_strength(inputs)
print("data_mode=synthetic")
print("available=", result.available)
print("strength=", result.strength)
print("components=", result.components)
print("component_contexts=", result.component_contexts)
print("algorithm_version=", result.algorithm_version)
print("parameter_version=", result.parameter_version)
