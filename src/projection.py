"""
Projection test / Prueba de proyección

Question: does late-season bat speed (last 6 weeks of season Y) predict next season's
bat speed better than the full-season average of Y?
Pregunta: ¿el bat speed de las últimas 6 semanas de la temporada Y predice el de la
temporada siguiente mejor que el promedio de toda la temporada Y?

Why it matters for a front office: if late-season bat speed carries into next year,
projection and player valuation should weight recent bat speed more than the season mean.
Por qué importa a un front office: si el bat speed de fin de temporada se arrastra al año
siguiente, la proyección y la valoración deben pesar más el bat speed reciente.

Design:
  Predictors (season Y): full-season mean, late-6-week mean, both together.
  Targets (season Y+1): first 6 weeks (A) and full season (B).
  Models: simple linear regression, evaluated with leave-one-out cross-validation (LOO).
  Comparison: LOO MAE of full-season model minus LOO MAE of late-window model, with a
  paired bootstrap 95% CI. CONFIRMED only if the CI excludes zero.
  All hitters with enough swings in both seasons, not only decliners.
"""
from __future__ import annotations

import argparse
import os

import numpy as np
import pandas as pd

from select_player import load_statcast, competitive_swings, MIN_SWINGS_PER_WINDOW, WINDOW_WEEKS

MIN_FULL_SEASON_SWINGS = 300
N_BOOT = 2000
SEED = 2026


def window_means(df: pd.DataFrame) -> pd.DataFrame:
    start, end = df["game_date"].min(), df["game_date"].max()
    early = df[df["game_date"] < start + pd.Timedelta(weeks=WINDOW_WEEKS)]
    late = df[df["game_date"] > end - pd.Timedelta(weeks=WINDOW_WEEKS)]
    out = pd.DataFrame({
        "full_mean": df.groupby("batter")["bat_speed"].mean(),
        "full_n": df.groupby("batter")["bat_speed"].size(),
        "early_mean": early.groupby("batter")["bat_speed"].mean(),
        "early_n": early.groupby("batter")["bat_speed"].size(),
        "late_mean": late.groupby("batter")["bat_speed"].mean(),
        "late_n": late.groupby("batter")["bat_speed"].size(),
    })
    return out


def loo_predictions(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Leave-one-out predictions from OLS with intercept."""
    n = len(y)
    Xd = np.column_stack([np.ones(n), X])
    pred = np.empty(n)
    for i in range(n):
        m = np.ones(n, bool)
        m[i] = False
        beta, *_ = np.linalg.lstsq(Xd[m], y[m], rcond=None)
        pred[i] = Xd[i] @ beta
    return pred


def evaluate(t: pd.DataFrame, target: str) -> dict:
    y = t[target].to_numpy()
    preds = {
        "full_season": loo_predictions(t[["full_mean"]].to_numpy(), y),
        "late_6wk": loo_predictions(t[["late_mean"]].to_numpy(), y),
        "both": loo_predictions(t[["full_mean", "late_mean"]].to_numpy(), y),
    }
    res = {"n": int(len(y))}
    abs_err = {}
    for k, p in preds.items():
        e = np.abs(y - p)
        abs_err[k] = e
        res[f"mae_{k}"] = float(e.mean())
        res[f"r2_{k}"] = float(1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum())

    # Paired bootstrap: MAE(full) - MAE(late). Positive = late window predicts better.
    rng = np.random.default_rng(SEED)
    d = abs_err["full_season"] - abs_err["late_6wk"]
    boots = np.array([d[rng.integers(0, len(d), len(d))].mean() for _ in range(N_BOOT)])
    res["mae_diff_full_minus_late"] = float(d.mean())
    res["ci95"] = [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))]
    lo, hi = res["ci95"]
    if lo > 0:
        res["status"], res["winner"] = "CONFIRMED", "late_6wk"
    elif hi < 0:
        res["status"], res["winner"] = "CONFIRMED", "full_season"
    else:
        res["status"], res["winner"] = "NOT CONFIRMED", "no difference"

    # Weights when both predictors are used (full sample, unstandardized mph-per-mph)
    Xd = np.column_stack([np.ones(len(y)), t["full_mean"], t["late_mean"]])
    beta, *_ = np.linalg.lstsq(Xd, y, rcond=None)
    res["both_coef_full"], res["both_coef_late"] = float(beta[1]), float(beta[2])
    return res


def build_table(prev_path: str, next_path: str) -> pd.DataFrame:
    a = window_means(competitive_swings(load_statcast(prev_path))).add_prefix("y_")
    b = window_means(competitive_swings(load_statcast(next_path))).add_prefix("next_")
    t = a.join(b, how="inner")
    t = t[(t["y_full_n"] >= MIN_FULL_SEASON_SWINGS) & (t["y_late_n"] >= MIN_SWINGS_PER_WINDOW)
          & (t["next_early_n"] >= MIN_SWINGS_PER_WINDOW)
          & (t["next_full_n"] >= MIN_FULL_SEASON_SWINGS)].copy()
    t = t.rename(columns={"y_full_mean": "full_mean", "y_late_mean": "late_mean"})
    t["late_minus_full"] = t["late_mean"] - t["full_mean"]
    return t


def summary_md(results: dict, t: pd.DataFrame, prev_label: str, next_label: str) -> str:
    L = [f"# Projection test: does late-season bat speed carry into next season? ({prev_label} → {next_label})",
         f"*¿El bat speed de fin de temporada se arrastra a la siguiente? ({prev_label} → {next_label})*\n",
         "*Emerson Performance (EP) · Emerson Jimenez · Data: Baseball Savant*\n",
         f"Hitters with ≥ {MIN_FULL_SEASON_SWINGS} competitive swings in both seasons and ≥ "
         f"{MIN_SWINGS_PER_WINDOW} in each window: **{len(t)}**. "
         "Models: linear regression, leave-one-out cross-validation.\n"]
    names = {"next_early_mean": f"A. First 6 weeks of {next_label} / Primeras 6 semanas",
             "next_full_mean": f"B. Full {next_label} season / Temporada completa"}
    for target, r in results.items():
        L.append(f"## {names[target]} — `{r['status']}`\n")
        L.append("| Predictor ({}) | LOO MAE (mph) | LOO R² |".format(prev_label))
        L.append("|---|---|---|")
        L.append(f"| Full-season mean / Promedio de temporada | {r['mae_full_season']:.3f} | {r['r2_full_season']:.3f} |")
        L.append(f"| Last 6 weeks / Últimas 6 semanas | {r['mae_late_6wk']:.3f} | {r['r2_late_6wk']:.3f} |")
        L.append(f"| Both / Ambos | {r['mae_both']:.3f} | {r['r2_both']:.3f} |")
        lo, hi = r["ci95"]
        L.append(f"\nMAE(full) − MAE(late) = **{r['mae_diff_full_minus_late']:+.3f} mph** "
                 f"(95% bootstrap CI {lo:+.3f} to {hi:+.3f}). Positive = last 6 weeks predicts better.")
        L.append(f"Both-predictor model weights: full-season {r['both_coef_full']:.2f}, "
                 f"last 6 weeks {r['both_coef_late']:.2f}.\n")
        if r["winner"] == "late_6wk":
            L.append("**EN:** Late-season bat speed predicts next season better than the full-season mean.")
            L.append("**ES:** El bat speed de fin de temporada predice la siguiente mejor que el promedio de toda la temporada.\n")
        elif r["winner"] == "full_season":
            L.append("**EN:** The full-season mean predicts better; late-season bat speed adds noise, not signal.")
            L.append("**ES:** El promedio de toda la temporada predice mejor; el bat speed de fin de temporada agrega ruido, no señal.\n")
        else:
            L.append("**EN:** No reliable difference: late-season bat speed does not beat the full-season mean.")
            L.append("**ES:** Sin diferencia confiable: el bat speed de fin de temporada no supera al promedio de temporada.\n")
    L.append("## Limitations / Limitaciones")
    L.append("- One season pair. Survivor bias: only hitters who played enough in both seasons are included.")
    L.append("- The late window is part of the full season, so the predictors overlap.")
    L.append("- Bat speed only; this does not test whether the change carries into outcomes (xwOBA, barrels).")
    L.append("- *Un solo par de temporadas. Sesgo de supervivencia: solo bateadores que jugaron suficiente en ambas.*")
    L.append("- *La ventana final es parte de la temporada completa, así que los predictores se solapan.*")
    L.append("- *Solo bat speed; no prueba si el cambio se traslada a resultados (xwOBA, barrels).*")
    return "\n".join(L) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prev", required=True, help="Statcast season Y, e.g. data/statcast_2025.csv")
    ap.add_argument("--next", required=True, help="Statcast season Y+1, e.g. data/statcast_2026.csv")
    ap.add_argument("--outdir", default="output")
    ap.add_argument("--labels", nargs=2, default=["2025", "2026"])
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)

    t = build_table(a.prev, a.next)
    if len(t) < 30:
        print(f"Only {len(t)} hitters qualify — too few for a projection test.")
        return
    results = {tg: evaluate(t, tg) for tg in ["next_early_mean", "next_full_mean"]}
    t.to_csv(os.path.join(a.outdir, "projection_table.csv"))
    with open(os.path.join(a.outdir, "projection_summary.md"), "w", encoding="utf-8") as fh:
        fh.write(summary_md(results, t, *a.labels))
    for tg, r in results.items():
        print(f"[{tg}] n={r['n']}  MAE full={r['mae_full_season']:.3f}  late={r['mae_late_6wk']:.3f}  "
              f"both={r['mae_both']:.3f}  diff={r['mae_diff_full_minus_late']:+.3f}  "
              f"CI=[{r['ci95'][0]:+.3f}, {r['ci95'][1]:+.3f}]  {r['status']} ({r['winner']})")
    print("[ok] output/projection_summary.md")


if __name__ == "__main__":
    main()
