"""
EP Offseason Development Plan — pipeline runner
Usage / Uso:
    python src/run_pipeline.py --input data/statcast_2026.csv --top 1
    python src/run_pipeline.py --input data/statcast_2026.csv --batter 691026
"""
from __future__ import annotations

import argparse
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from select_player import load_statcast, competitive_swings, compare_windows, resolve_names, WINDOW_WEEKS
from diagnose import diagnose
from plan_builder import build_plan_md

# EP brand system (falls back if ep_chart_style.py is not on the path)
try:
    import ep_chart_style  # noqa: F401
except ImportError:
    pass
NAVY, GOLD, OFFWHITE = "#0B1B33", "#D4A53A", "#F5F3EC"


def plot_trend(df: pd.DataFrame, batter: int, name: str, out_path: str) -> None:
    g = df[df["batter"] == batter].set_index("game_date")["bat_speed"]
    weekly = g.resample("W").agg(["mean", "count"])
    # Keep empty weeks as NaN so absences show as a break in the line
    # Mantener semanas vacías como NaN para que las ausencias se vean como un corte en la línea
    weekly.loc[weekly["count"] < 10, "mean"] = float("nan")
    start, end = g.index.min(), g.index.max()

    fig, ax = plt.subplots(figsize=(9, 4.5), facecolor=OFFWHITE)
    ax.set_facecolor(OFFWHITE)
    ax.axvspan(start, start + pd.Timedelta(weeks=WINDOW_WEEKS), color=NAVY, alpha=0.08)
    ax.axvspan(end - pd.Timedelta(weeks=WINDOW_WEEKS), end, color=GOLD, alpha=0.15)
    ax.plot(weekly.index, weekly["mean"], color=NAVY, lw=2, marker="o", ms=4)
    ax.set_title(f"{name} — weekly bat speed, 2026 (competitive swings)", color=NAVY, loc="left")
    ax.set_ylabel("Bat speed (mph)", color=NAVY)
    ax.text(start, ax.get_ylim()[1], " early window", va="top", color=NAVY, fontsize=9)
    ax.text(end, ax.get_ylim()[1], "late window ", va="top", ha="right", color="#8a6a1f", fontsize=9)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.text(0.99, 0.01, "Emerson Performance · Data: Baseball Savant",
             ha="right", fontsize=8, color="#666")
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


MAX_GAP_DAYS = 14          # gap without games that flags a possible IL stint
MAX_MISSING_END_DAYS = 10  # days missed at the end of the season


def _norm(name: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode().lower()
    s = s.replace(".", "").replace(" jr", "").strip()
    return " ".join(s.split())


def injury_status(table: pd.DataFrame, path: str) -> pd.DataFrame:
    """Injury file (data/injury_exclusions.csv) columns:
        batter_name, action (exclude | annotate), injury_type, reason
    exclude  -> hitter skipped (injury affects the late window directly)
    annotate -> hitter stays eligible, plan carries the injury context
    Plus automatic absence detection (possible IL) from gaps between games.

    Archivo de lesiones: exclude = se excluye; annotate = sigue elegible y el plan
    lleva el contexto de la lesión. Además, detección automática de ausencias."""
    lookup = {}
    if path and os.path.exists(path):
        ex = pd.read_csv(path, encoding="utf-8").fillna("")
        for _, e in ex.iterrows():
            lookup[_norm(e["batter_name"])] = {
                "action": str(e.get("action", "exclude") or "exclude").strip().lower(),
                "injury_type": str(e.get("injury_type", "")).strip().lower(),
                "reason": str(e.get("reason", "")),
            }
    rows = []
    for _, r in table.iterrows():
        info = lookup.get(_norm(r["batter_name"]))
        excluded, context, itype = "", "", ""
        if info and info["action"] == "exclude":
            excluded = "injury: " + info["reason"]
        elif r.get("max_gap_days_recent", 0) >= MAX_GAP_DAYS:
            excluded = (f"absence: {int(r['max_gap_days_recent'])}-day gap without games "
                        f"near the late window (possible IL)")
        elif r.get("days_missing_at_end", 0) >= MAX_MISSING_END_DAYS:
            excluded = (f"absence: last {int(r['days_missing_at_end'])} days of the season "
                        f"missed (possible IL)")
        if info and info["action"] == "annotate":
            context, itype = info["reason"], info["injury_type"]
        rows.append((excluded, context, itype))
    return pd.DataFrame(rows, columns=["excluded_reason", "injury_context", "injury_type"],
                        index=table.index)


def decline_category(r) -> str:
    if r["status"] != "CONFIRMED":
        return ""
    if str(r["excluded_reason"]).startswith("injury"):
        return "injury"
    if str(r["excluded_reason"]).startswith("absence"):
        return "absence"
    if r["profile"] == "swing_change":
        return "swing_change"
    if r["injury_context"]:
        return "possible_force_with_injury_history"
    return "possible_force_or_efficiency"


CATEGORY_TEXT = {
    "injury": ("Known injury affecting the late window", "Lesión conocida que afecta la ventana final"),
    "absence": ("Absence of 14+ days (possible IL)", "Ausencia de 14+ días (posible IL)"),
    "swing_change": ("Clearly shorter swing (swing/approach change)", "Swing claramente más corto (cambio de swing/enfoque)"),
    "possible_force_with_injury_history": ("Possible force loss, with earlier injury that season",
                                           "Posible pérdida de fuerza, con lesión previa esa temporada"),
    "possible_force_or_efficiency": ("Possible force/efficiency loss (no other explanation found)",
                                     "Posible pérdida de fuerza/eficiencia (sin otra explicación encontrada)"),
}


def write_causes_summary(table: pd.DataFrame, out_path: str) -> None:
    c = table[table["status"] == "CONFIRMED"].copy()
    n = len(c)
    L = ["# What is behind the 2026 bat speed declines? / ¿Qué hay detrás de las caídas de bat speed 2026?",
         "*Emerson Performance (EP) · Emerson Jimenez · Data: Baseball Savant*\n",
         f"Hitters with a `CONFIRMED` decline (first vs last 6 weeks, BH-q < 0.05, drop ≥ 1 mph): **{n}**\n",
         "| Category / Categoría | n | % |", "|---|---|---|"]
    for key, (en, es) in CATEGORY_TEXT.items():
        k = int((c["category"] == key).sum())
        L.append(f"| {en} / *{es}* | {k} | {100 * k / n:.0f}% |" if n else f"| {en} / *{es}* | 0 | - |")
    other = int(c["category"].isin(["injury", "absence", "swing_change"]).sum())
    L.append("")
    L.append(f"**EN:** {other} of {n} confirmed declines ({100 * other / max(n, 1):.0f}%) have an "
             "explanation other than strength loss. Training alone would not be expected to fix them.")
    L.append(f"\n**ES:** {other} de {n} caídas confirmadas ({100 * other / max(n, 1):.0f}%) tienen una "
             "explicación distinta a la pérdida de fuerza. No se esperaría que el entrenamiento solo las corrija.\n")
    L.append("Note: injury categories use automatic gap detection plus a manually curated file with public "
             "sources; injuries that cause no gap and are not in the file are missed, so the "
             "'no other explanation' group is an upper bound.\n")
    L.append("| Hitter | Drop (mph) | Swing length Δ (ft) | Category | Detail |")
    L.append("|---|---|---|---|---|")
    for _, r in c.sort_values("bat_speed_drop", ascending=False).iterrows():
        detail = r["excluded_reason"] or r["injury_context"] or ""
        sl = r["swing_length_late"] - r["swing_length_early"]
        L.append(f"| {r['batter_name']} | {r['bat_speed_drop']:.2f} | {sl:+.2f} | "
                 f"{CATEGORY_TEXT[r['category']][0]} | {detail} |")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--outdir", default="output")
    ap.add_argument("--top", type=int, default=1, help="plans for the top-N CONFIRMED decliners")
    ap.add_argument("--batter", type=int, help="force a specific MLBAM id")
    ap.add_argument("--name", help='force a specific hitter by name, e.g. "Samuel Basallo"')
    ap.add_argument("--prev-input", help="previous season Statcast CSV for the natural rebound baseline")
    ap.add_argument("--exclusions", default="data/injury_exclusions.csv",
                    help="injury file (columns: batter_name, action, injury_type, reason)")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    rebound = None
    if args.prev_input:
        import json
        from natural_rebound import natural_rebound
        rb_table, rebound = natural_rebound(args.prev_input, args.input)
        rb_table.to_csv(os.path.join(args.outdir, "natural_rebound_table.csv"), index=False)
        with open(os.path.join(args.outdir, "natural_rebound_summary.json"), "w", encoding="utf-8") as fh:
            json.dump(rebound, fh, indent=2)
        print("[baseline]", rebound)

    df = competitive_swings(load_statcast(args.input))
    table = resolve_names(compare_windows(df))
    table["profile"] = [diagnose(r)["profile"] for r in table.to_dict("records")]
    table = table.join(injury_status(table, args.exclusions))
    table["category"] = table.apply(decline_category, axis=1)
    table.to_csv(os.path.join(args.outdir, "bat_speed_decline_leaderboard.csv"), index=False)
    write_causes_summary(table, os.path.join(args.outdir, "decline_causes_summary.md"))
    print("[ok] decline_causes_summary.md")

    if args.name:
        picks = table[table["batter_name"].map(_norm) == _norm(args.name)]
    elif args.batter:
        picks = table[table["batter"] == args.batter]
    else:
        # Auto-pick: CONFIRMED, not excluded for injury, and a profile S&C can own
        # Selección automática: CONFIRMED, sin exclusión por lesión, y perfil que corresponde a S&C
        eligible = table[(table["status"] == "CONFIRMED") & (table["excluded_reason"] == "")
                         & (table["profile"].isin(["force", "efficiency"]))]
        skipped = table[(table["status"] == "CONFIRMED") & ~table.index.isin(eligible.index)]
        for _, s in skipped.iterrows():
            why = s["excluded_reason"] or f"profile {s['profile']}"
            print(f"[skip] {s['batter_name']}: {why}")
        picks = eligible.head(args.top)
    if picks.empty:
        print("No eligible CONFIRMED decline — no plan generated (this is a valid result).")
        print("No hay caída CONFIRMED elegible — no se generó plan (es un resultado válido).")
        return

    for _, r in picks.iterrows():
        row = r.to_dict()
        name = str(row["batter_name"])
        slug = name.lower().replace(" ", "-").replace(".", "")
        chart = f"{slug}_bat_speed_trend.png"
        plot_trend(df, row["batter"], name, os.path.join(args.outdir, chart))
        success = None
        if rebound:
            from natural_rebound import success_threshold_text
            success = success_threshold_text(rebound, row["bat_speed_drop"])
        injury = ({"context": row["injury_context"], "type": row["injury_type"]}
                  if row.get("injury_context") else None)
        md = build_plan_md(name, row, diagnose(row), chart_file=chart, success=success,
                           injury=injury)
        with open(os.path.join(args.outdir, f"{slug}_offseason_plan.md"), "w", encoding="utf-8") as fh:
            fh.write(md)
        print(f"[ok] {name}: drop {row['bat_speed_drop']:.2f} mph, q={row['q_bh']:.3g} -> {slug}_offseason_plan.md")


if __name__ == "__main__":
    main()
