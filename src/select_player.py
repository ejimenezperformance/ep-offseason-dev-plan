"""
Layer 1 — DATA / Capa 1 — DATOS
Finds the hitters with the largest in-season bat speed decline (2026).
Encuentra a los bateadores con la mayor caída de bat speed en la temporada 2026.

Input: Statcast pitch-level CSV (same pull used in ep-bat-speed-fatigue) with columns:
    batter, game_date, bat_speed, swing_length
Optional: batter_name (if missing, names are resolved with pybaseball).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

MIN_SWINGS_PER_WINDOW = 75      # minimum competitive swings in each window
WINDOW_WEEKS = 6                # early window vs late window length
MIN_DROP_MPH = 1.0              # practical threshold for a "real" decline
ALPHA = 0.05


def load_statcast(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)
    needed = {"batter", "game_date", "bat_speed", "swing_length"}
    missing = needed - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns / Faltan columnas: {missing}")
    # Regular season only: postseason swings would distort the late window
    # Solo temporada regular: los swings de postemporada alterarían la ventana final
    if "game_type" in df.columns:
        df = df[df["game_type"] == "R"]
    df = df.dropna(subset=["bat_speed"]).copy()
    df["game_date"] = pd.to_datetime(df["game_date"])
    return df


def competitive_swings(df: pd.DataFrame) -> pd.DataFrame:
    """Baseball Savant-style filter: drop each batter's slowest 10% of swings,
    but always keep swings >= 60 mph (removes checked/defensive swings)."""
    p10 = df.groupby("batter")["bat_speed"].transform(lambda s: s.quantile(0.10))
    return df[(df["bat_speed"] >= p10) | (df["bat_speed"] >= 60)].copy()


def cohens_d(a: np.ndarray, b: np.ndarray) -> float:
    pooled = np.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1))
                     / (len(a) + len(b) - 2))
    return float((a.mean() - b.mean()) / pooled) if pooled > 0 else 0.0


def compare_windows(df: pd.DataFrame) -> pd.DataFrame:
    """Early window (first N weeks of the season) vs late window (last N weeks)."""
    start, end = df["game_date"].min(), df["game_date"].max()
    early_end = start + pd.Timedelta(weeks=WINDOW_WEEKS)
    late_start = end - pd.Timedelta(weeks=WINDOW_WEEKS)

    rows = []
    for batter, g in df.groupby("batter"):
        early = g[g["game_date"] < early_end]
        late = g[g["game_date"] > late_start]
        if len(early) < MIN_SWINGS_PER_WINDOW or len(late) < MIN_SWINGS_PER_WINDOW:
            continue
        e_bs, l_bs = early["bat_speed"].to_numpy(), late["bat_speed"].to_numpy()
        e_sl = early["swing_length"].dropna().to_numpy()
        l_sl = late["swing_length"].dropna().to_numpy()
        _, p = stats.mannwhitneyu(e_bs, l_bs, alternative="greater")

        # monotonic trend across the whole season (weekly means)
        weekly = g.set_index("game_date")["bat_speed"].resample("W").mean().dropna()
        rho, p_trend = (stats.spearmanr(np.arange(len(weekly)), weekly.values)
                        if len(weekly) >= 8 else (np.nan, np.nan))

        # Absence check (possible IL): longest gap between games from 4 weeks before the
        # late window to season end, plus days missed at the end of the season.
        # Chequeo de ausencia (posible IL): mayor hueco entre juegos desde 4 semanas antes
        # de la ventana final hasta el fin de temporada, y días perdidos al final.
        games = pd.Series(sorted(g["game_date"].dt.normalize().unique()))
        recent = games[games >= late_start - pd.Timedelta(weeks=4)]
        max_gap = int(recent.diff().dt.days.max()) if len(recent) > 1 else 0
        missing_end = int((end.normalize() - games.iloc[-1]).days)

        rows.append({
            "max_gap_days_recent": max_gap,
            "days_missing_at_end": missing_end,
            "batter": batter,
            "batter_name": g["batter_name"].iloc[0] if "batter_name" in g else None,
            "n_early": len(e_bs), "n_late": len(l_bs),
            "bat_speed_early": e_bs.mean(), "bat_speed_late": l_bs.mean(),
            "bat_speed_drop": e_bs.mean() - l_bs.mean(),
            "swing_length_early": e_sl.mean() if len(e_sl) else np.nan,
            "swing_length_late": l_sl.mean() if len(l_sl) else np.nan,
            "p_mannwhitney": p,
            "cohens_d": cohens_d(e_bs, l_bs),
            "trend_rho": rho, "trend_p": p_trend,
        })

    out = pd.DataFrame(rows)
    if out.empty:
        return out
    # Benjamini-Hochberg correction: many hitters are tested at once
    out = out.sort_values("p_mannwhitney").reset_index(drop=True)
    m = len(out)
    q = out["p_mannwhitney"] * m / (np.arange(m) + 1)
    out["q_bh"] = np.minimum.accumulate(q[::-1])[::-1].clip(upper=1)
    out["status"] = np.where(
        (out["q_bh"] < ALPHA) & (out["bat_speed_drop"] >= MIN_DROP_MPH),
        "CONFIRMED", "NOT CONFIRMED")
    return out.sort_values("bat_speed_drop", ascending=False).reset_index(drop=True)


def resolve_names(table: pd.DataFrame) -> pd.DataFrame:
    """Fill missing batter names with pybaseball (optional)."""
    if "batter_name" in table and table["batter_name"].notna().all():
        return table
    try:
        from pybaseball import playerid_reverse_lookup
        ids = playerid_reverse_lookup(table["batter"].astype(int).tolist(), key_type="mlbam")
        ids["batter_name"] = ids["name_first"].str.title() + " " + ids["name_last"].str.title()
        table = table.drop(columns=["batter_name"], errors="ignore").merge(
            ids[["key_mlbam", "batter_name"]], left_on="batter", right_on="key_mlbam",
            how="left").drop(columns="key_mlbam")
    except Exception:
        table["batter_name"] = table.get("batter_name", table["batter"].astype(str))
    table["batter_name"] = table["batter_name"].fillna(table["batter"].astype(str))
    return table
