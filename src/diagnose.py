"""
Layers 2-3 — FINDING + BIOMECHANICS INTERPRETATION
Capas 2-3 — HALLAZGO + INTERPRETACIÓN BIOMECÁNICA

Rule-based (no ML, no LLM text). Every output carries a label:
  CONFIRMED       -> comes straight from the data and the statistical test
  INTERPRETATION  -> biomechanical reading of the data; a hypothesis, not a fact
"""
from __future__ import annotations

import math

SWING_LENGTH_CHANGE_FT = 0.2   # change in swing length considered meaningful (ft)


def diagnose(row: dict) -> dict:
    drop = row["bat_speed_drop"]
    sl_change = row["swing_length_late"] - row["swing_length_early"]
    progressive = (not math.isnan(row.get("trend_rho", math.nan))
                   and row["trend_rho"] < -0.3 and row["trend_p"] < 0.05)

    finding = {
        "label": "CONFIRMED" if row["status"] == "CONFIRMED" else "NOT CONFIRMED",
        "en": (f"Bat speed fell {drop:.1f} mph from the first to the last 6 weeks "
               f"({row['bat_speed_early']:.1f} → {row['bat_speed_late']:.1f} mph; "
               f"Mann-Whitney BH-q = {row['q_bh']:.3g}, Cohen's d = {row['cohens_d']:.2f})."),
        "es": (f"El bat speed bajó {drop:.1f} mph entre las primeras y las últimas 6 semanas "
               f"({row['bat_speed_early']:.1f} → {row['bat_speed_late']:.1f} mph; "
               f"Mann-Whitney BH-q = {row['q_bh']:.3g}, d de Cohen = {row['cohens_d']:.2f})."),
    }

    if sl_change >= SWING_LENGTH_CHANGE_FT:
        profile = "efficiency"
        interp_en = ("Bat speed dropped while the swing got LONGER. A longer path with less "
                     "speed points to a sequencing/efficiency problem (hip-trunk separation, "
                     "energy transfer), not only lost force.")
        interp_es = ("El bat speed bajó mientras el swing se hizo MÁS LARGO. Un recorrido más "
                     "largo con menos velocidad apunta a un problema de secuencia/eficiencia "
                     "(separación cadera-tronco, transferencia de energía), no solo a pérdida de fuerza.")
    elif sl_change <= -SWING_LENGTH_CHANGE_FT:
        # A clearly shorter swing produces less bat speed mechanically (league-wide,
        # swing shortening and bat speed loss correlate). Not a force problem.
        # Un swing claramente más corto genera menos bat speed por mecánica. No es fuerza.
        profile = "swing_change"
        interp_en = ("Bat speed dropped while the swing got clearly SHORTER. A shorter swing "
                     "generates less bat speed by itself, so this looks like a swing or approach "
                     "change (e.g., shortening up, more contact-oriented), not lost force. "
                     "Primary owner: hitting coach.")
        interp_es = ("El bat speed bajó mientras el swing se hizo claramente MÁS CORTO. Un swing "
                     "más corto genera menos bat speed por sí solo, así que esto parece un cambio "
                     "de swing o de enfoque (ej. acortar, buscar más contacto), no pérdida de "
                     "fuerza. Responsable principal: coach de bateo.")
    else:
        profile = "force"
        interp_en = ("Bat speed dropped with a stable swing length. Same path, less speed "
                     "points to a drop in force/power production (lower-body and rotational).")
        interp_es = ("El bat speed bajó con un swing de largo estable. Mismo recorrido con "
                     "menos velocidad apunta a una caída en la producción de fuerza/potencia "
                     "(tren inferior y rotacional).")

    if progressive:
        interp_en += (" The decline is progressive across the season (weekly trend), "
                      "consistent with an in-season maintenance deficit.")
        interp_es += (" La caída es progresiva durante la temporada (tendencia semanal), "
                      "compatible con un déficit de mantenimiento en temporada.")

    return {
        "finding": finding,
        "profile": profile,
        "progressive": progressive,
        "swing_length_change": sl_change,
        "interpretation": {"label": "INTERPRETATION", "en": interp_en, "es": interp_es},
    }
