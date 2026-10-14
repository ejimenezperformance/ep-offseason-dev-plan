"""Synthetic data for testing the pipeline only. NOT real players, NOT for publication.
Datos sintéticos solo para probar el pipeline. NO son jugadores reales, NO publicar.

Creates two seasons (2025, 2026). Decliners in 2025 recover ~60% of their drop by
early 2026, so the natural rebound module has a known answer to recover."""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)


def season(year: int, profiles: dict) -> pd.DataFrame:
    dates = pd.date_range(f"{year}-03-27", f"{year}-09-28", freq="D")
    rows = []
    for bid, (base, drop, sl_d) in profiles.items():
        for i, d in enumerate(dates):
            frac = i / len(dates)
            for _ in range(rng.integers(2, 6)):
                rows.append({"batter": bid, "batter_name": f"Synthetic Hitter {bid}",
                             "game_date": d, "bat_speed": rng.normal(base - drop * frac, 3.0),
                             "swing_length": rng.normal(7.3 + sl_d * frac, 0.4)})
    return pd.DataFrame(rows)


# id: (start mph, in-season drop, swing length change)
p2025, p2026 = {}, {}
for bid in range(1, 41):
    base = rng.normal(72, 1.5)
    drop25 = rng.choice([0.0, 0.0, 2.5, 3.0])          # ~half decline in 2025
    p2025[bid] = (base, drop25, 0.0)
    start26 = base - drop25 + 0.6 * drop25             # recovers ~60% over the offseason
    p2026[bid] = (start26, rng.choice([0.0, 0.0, 2.0]), rng.choice([0.0, 0.4]))

season(2025, p2025).to_csv("data/synthetic_2025.csv", index=False)
season(2026, p2026).to_csv("data/synthetic_2026.csv", index=False)
print("written data/synthetic_2025.csv, data/synthetic_2026.csv")
