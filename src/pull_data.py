"""
Download one regular season of Statcast data (only the columns this repo needs).
Descarga una temporada regular de Statcast (solo las columnas que usa este repo).

Usage / Uso:
    python src/pull_data.py --season 2025
    python src/pull_data.py --season 2026
A full season takes a while (often 20-40 minutes). Let it finish.
Una temporada completa tarda (a menudo 20-40 minutos). Déjalo terminar.
"""
import argparse
import os

from pybaseball import statcast, cache

# Wide windows; postseason and spring training are removed with game_type == "R"
# Ventanas amplias; la postemporada y el spring training se quitan con game_type == "R"
SEASON_DATES = {
    2025: ("2025-03-18", "2025-09-30"),
    2026: ("2026-03-25", "2026-10-01"),
}
KEEP = ["batter", "game_date", "game_type", "bat_speed", "swing_length",
        "launch_speed", "launch_angle", "launch_speed_angle", "description"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--season", type=int, required=True, choices=sorted(SEASON_DATES))
    a = ap.parse_args()
    cache.enable()
    start, end = SEASON_DATES[a.season]
    df = statcast(start_dt=start, end_dt=end)
    df = df[df["game_type"] == "R"]
    df = df[[c for c in KEEP if c in df.columns]]
    df = df.dropna(subset=["bat_speed"])
    os.makedirs("data", exist_ok=True)
    out = f"data/statcast_{a.season}.csv"
    df.to_csv(out, index=False)
    print(f"[ok] {out}: {len(df):,} swings with bat speed / swings con bat speed, "
          f"{df['batter'].nunique()} batters / bateadores")


if __name__ == "__main__":
    main()
