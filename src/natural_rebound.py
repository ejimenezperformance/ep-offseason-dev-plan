"""
Natural rebound baseline / Línea base de recuperación natural

Question: how much bat speed do hitters with a CONFIRMED in-season decline recover
over the offseason on their own (rest + their usual routine, no EP plan)?
Pregunta: ¿cuánto bat speed recuperan solos en la offseason los bateadores con caída
CONFIRMED (descanso + su rutina normal, sin plan de EP)?

Design:
  - Decliners: CONFIRMED in season Y (e.g., 2025).
  - Recovery = early-window bat speed in Y+1  minus  late-window bat speed in Y.
  - Controls: all other hitters with data in both seasons. Their change
    (early Y+1 minus early Y) estimates the league-wide shift (aging, measurement),
    which is subtracted from the decliners' recovery.
  - Includes regression to the mean ON PURPOSE: a plan must beat everything that
    happens without it, including statistical regression.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from select_player import (load_statcast, competitive_swings, compare_windows,
                           MIN_SWINGS_PER_WINDOW, WINDOW_WEEKS)

MIN_DECLINERS = 10   # below this, the baseline is reported as unreliable


def early_window_means(df: pd.DataFrame) -> pd.DataFrame:
    start = df["game_date"].min()
    early = df[df["game_date"] < start + pd.Timedelta(weeks=WINDOW_WEEKS)]
    g = early.groupby("batter")["bat_speed"].agg(["mean", "count"])
    g = g[g["count"] >= MIN_SWINGS_PER_WINDOW]
    return g.rename(columns={"mean": "bat_speed_next_early", "count": "n_next_early"})


def natural_rebound(prev_path: str, next_path: str) -> tuple[pd.DataFrame, dict]:
    prev = competitive_swings(load_statcast(prev_path))
    nxt = competitive_swings(load_statcast(next_path))

    t = compare_windows(prev).merge(early_window_means(nxt), left_on="batter",
                                    right_index=True, how="inner")
    t["recovery_mph"] = t["bat_speed_next_early"] - t["bat_speed_late"]
    t["pct_recovered"] = t["recovery_mph"] / t["bat_speed_drop"]
    t["change_early_to_early"] = t["bat_speed_next_early"] - t["bat_speed_early"]

    dec = t[t["status"] == "CONFIRMED"]
    ctl = t[t["status"] != "CONFIRMED"]
    league_shift = float(ctl["change_early_to_early"].median()) if len(ctl) else 0.0
    adj = dec["recovery_mph"] - league_shift

    summary = {
        "n_decliners": int(len(dec)),
        "n_controls": int(len(ctl)),
        "league_shift_mph": round(league_shift, 2),
        "median_recovery_mph": round(float(dec["recovery_mph"].median()), 2) if len(dec) else None,
        "median_recovery_adj_mph": round(float(adj.median()), 2) if len(dec) else None,
        "iqr_recovery_adj_mph": ([round(float(adj.quantile(.25)), 2), round(float(adj.quantile(.75)), 2)]
                                 if len(dec) else None),
        "median_pct_recovered": round(float(dec["pct_recovered"].median()), 2) if len(dec) else None,
        "pct_full_recovery": round(float((dec["change_early_to_early"] >= 0).mean()), 2) if len(dec) else None,
        "reliable": bool(len(dec) >= MIN_DECLINERS),
    }
    return t, summary


def success_threshold_text(s: dict, drop: float) -> tuple[str, str]:
    """Success rule for the plan: beat the natural rebound, not just 'improve'."""
    if not s or s["median_recovery_adj_mph"] is None:
        return ("No natural-rebound baseline available: any 2027 improvement cannot be "
                "attributed to the plan.",
                "Sin línea base de recuperación natural: ninguna mejora en 2027 se puede "
                "atribuir al plan.")
    nat = s["median_recovery_adj_mph"]
    hi = s["iqr_recovery_adj_mph"][1]
    warn_en = "" if s["reliable"] else f" (small sample: n={s['n_decliners']}, treat as provisional)"
    warn_es = "" if s["reliable"] else f" (muestra pequeña: n={s['n_decliners']}, tomar como provisional)"
    return (f"Hitters with a confirmed decline recovered a median of {nat:+.1f} mph on their own "
            f"(league-adjusted, n={s['n_decliners']}){warn_en}. For this {drop:.1f} mph drop, the plan "
            f"counts as successful only if recovery exceeds {hi:+.1f} mph (75th percentile of natural "
            f"rebound).",
            f"Los bateadores con caída confirmada recuperaron solos una mediana de {nat:+.1f} mph "
            f"(ajustado por la liga, n={s['n_decliners']}){warn_es}. Para esta caída de {drop:.1f} mph, "
            f"el plan solo cuenta como éxito si la recuperación supera {hi:+.1f} mph (percentil 75 "
            f"de la recuperación natural).")


if __name__ == "__main__":
    import argparse, json, os
    ap = argparse.ArgumentParser()
    ap.add_argument("--prev", required=True, help="Statcast season Y (e.g., 2025)")
    ap.add_argument("--next", required=True, help="Statcast season Y+1 (e.g., 2026)")
    ap.add_argument("--outdir", default="output")
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    table, s = natural_rebound(a.prev, a.next)
    table.to_csv(os.path.join(a.outdir, "natural_rebound_table.csv"), index=False)
    with open(os.path.join(a.outdir, "natural_rebound_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(s, fh, indent=2)
    print(json.dumps(s, indent=2))
