"""
Layers 4-5 — TRAINING APPLICATION + MONITORING METRIC
Capas 4-5 — APLICACIÓN AL ENTRENAMIENTO + MÉTRICA DE MONITOREO

12-week offseason block. The profile from diagnose.py changes the emphasis:
  force      -> more max strength and rotational power volume
  efficiency -> more mobility/sequencing work + coordination with the hitting coach
This is a TEMPLATE for a coach to individualize. It is not a prescription
written without assessing the athlete.
"""
from __future__ import annotations

PHASES = [
    {
        "weeks": "1-3",
        "en": "General preparation / Restore",
        "es": "Preparación general / Recuperación",
        "base": [
            ("Hip and thoracic mobility circuit", "Circuito de movilidad de cadera y torácica"),
            ("Eccentric-focused squat and RDL (3x8, 3-sec lowering)",
             "Sentadilla y RDL con énfasis excéntrico (3x8, bajada de 3 seg)"),
            ("Anti-rotation core: Pallof press, dead bug", "Core anti-rotación: Pallof press, dead bug"),
        ],
        "force": [("Trap bar deadlift intro (3x6 @ moderate load)",
                   "Introducción a peso muerto con trap bar (3x6 carga moderada)")],
        "efficiency": [("Hip-shoulder separation drills (half-kneeling cable rotations)",
                        "Drills de separación cadera-hombro (rotaciones con polea en media rodilla)")],
    },
    {
        "weeks": "4-7",
        "en": "Maximal strength",
        "es": "Fuerza máxima",
        "base": [
            ("Trap bar deadlift (4x4-5)", "Peso muerto trap bar (4x4-5)"),
            ("Rear-foot elevated split squat (3x6/side)", "Sentadilla búlgara (3x6 por lado)"),
            ("Landmine rotational press (3x6/side)", "Press rotacional con landmine (3x6 por lado)"),
        ],
        "force": [("Extra strength set on main lifts (+1 set)",
                   "Serie extra de fuerza en los ejercicios principales (+1 serie)")],
        "efficiency": [("Lead-leg block drills (stride + firm front leg)",
                        "Drills de bloqueo de pierna delantera (zancada + pierna firme)")],
    },
    {
        "weeks": "8-10",
        "en": "Rotational power",
        "es": "Potencia rotacional",
        "base": [
            ("Rotational med ball scoop/shot-put throws (4x5/side, max intent)",
             "Lanzamientos rotacionales de balón medicinal (4x5 por lado, máxima intención)"),
            ("Countermovement and broad jumps (4x3)", "Saltos con contramovimiento y horizontales (4x3)"),
            ("Strength maintenance: main lifts at 2x3", "Mantenimiento de fuerza: ejercicios principales 2x3"),
        ],
        "force": [("Heavier med ball (+1-2 kg) on half the sets",
                   "Balón más pesado (+1-2 kg) en la mitad de las series")],
        "efficiency": [("Step-behind med ball throws focused on sequence",
                        "Lanzamientos con paso atrás enfocados en la secuencia")],
    },
    {
        "weeks": "11-12",
        "en": "Transfer and taper to spring training",
        "es": "Transferencia y descarga hacia spring training",
        "base": [
            ("Overload/underload bat work (coordinated with hitting coach)",
             "Trabajo con bates pesados/livianos (coordinado con el coach de bateo)"),
            ("Reduce lifting volume ~40%, keep intensity",
             "Bajar volumen de pesas ~40%, mantener intensidad"),
            ("Retest all monitoring metrics", "Repetir todas las pruebas de monitoreo"),
        ],
        "force": [],
        "efficiency": [("Video review of sequence with hitting coach",
                        "Revisión de video de la secuencia con el coach de bateo")],
    },
]

# Replaces the rotational work when the hitter had an oblique strain that season.
# Principle: anti-rotation -> controlled rotation -> ballistic, each step only if
# symptom-free and cleared by the club's medical staff.
# Reemplaza el trabajo rotacional cuando hubo distensión de oblicuo esa temporada.
OBLIQUE_OVERRIDE = {
    "1-3": [
        ("OBLIQUE — Isometric anti-rotation first: Pallof press holds, side plank, half-kneeling anti-rotation",
         "OBLICUO — Primero anti-rotación isométrica: Pallof isométrico, plancha lateral, anti-rotación en media rodilla"),
        ("OBLIQUE — No loaded or ballistic rotation in this phase",
         "OBLICUO — Sin rotación con carga ni balística en esta fase"),
    ],
    "4-7": [
        ("OBLIQUE — Controlled rotation: cable chops and lifts, slow tempo, progressive load",
         "OBLICUO — Rotación controlada: chops y lifts con polea, tempo lento, carga progresiva"),
        ("OBLIQUE — Replace landmine rotational press with half-kneeling landmine press (no trunk rotation) until week 6",
         "OBLICUO — Cambiar el press rotacional con landmine por press en media rodilla (sin rotación de tronco) hasta la semana 6"),
    ],
    "8-10": [
        ("OBLIQUE — Ballistic progression: med ball throws at ~50% → 75% → max intent across the 3 weeks, both sides",
         "OBLICUO — Progresión balística: balón medicinal al ~50% → 75% → máxima intención en las 3 semanas, ambos lados"),
        ("OBLIQUE — Skip the heavier med ball (+1-2 kg) this offseason",
         "OBLICUO — No usar el balón más pesado (+1-2 kg) esta offseason"),
    ],
    "11-12": [
        ("OBLIQUE — Bat overload work only after pain-free max-intent throws",
         "OBLICUO — Bates pesados solo después de lanzamientos a máxima intención sin dolor"),
    ],
}
# Items removed from the standard plan when the oblique override applies
OBLIQUE_REMOVE = {
    "Landmine rotational press (3x6/side)",
    "Rotational med ball scoop/shot-put throws (4x5/side, max intent)",
    "Heavier med ball (+1-2 kg) on half the sets",
}

MONITORING = [
    ("REQUIRED — Bat speed with a bat sensor in cage sessions (best of 5 swings) — every 2 weeks",
     "REQUERIDO — Bat speed con sensor de bate en la jaula (mejor de 5 swings) — cada 2 semanas"),
    ("2027 FOLLOW-UP — Statcast competitive-swing bat speed, first 6 weeks, vs the success "
     "threshold below",
     "SEGUIMIENTO 2027 — Bat speed de swings competitivos de Statcast, primeras 6 semanas, "
     "contra el umbral de éxito de abajo"),
    ("RECOMMENDED — Rotational med ball throw and CMJ height (low-cost equipment): if bat speed "
     "does not improve, they show whether force improved but did not transfer to the swing",
     "RECOMENDADO — Balón medicinal rotacional y altura del CMJ (equipo de bajo costo): si el bat "
     "speed no mejora, muestran si la fuerza subió pero no se transfirió al swing"),
    ("OPTIONAL — CMJ early-phase RFD (0-100 ms), only if the club has force plates",
     "OPCIONAL — RFD temprana del CMJ (0-100 ms), solo si el club tiene plataformas de fuerza"),
]

IN_SEASON = [
    ("In-season maintenance: 2 lifts/week, 1 heavy compound + 1 rotational power movement",
     "Mantenimiento en temporada: 2 sesiones/semana, 1 ejercicio compuesto pesado + 1 de potencia rotacional"),
    ("Trigger: if monthly bat speed falls >1 mph from baseline, review workload",
     "Alerta: si el bat speed mensual cae >1 mph de la línea base, revisar la carga"),
]

LITERATURE = [
    "Welch CM et al. (1995). Hitting a baseball: a biomechanical description. JOSPT 22(5):193-201.",
    "Szymanski DJ et al. (2007). Effect of twelve weeks of medicine ball training on high school "
    "baseball players. J Strength Cond Res 21(3):894-901. https://doi.org/10.1519/R-18415.1",
    "DeRenne C, Szymanski DJ (2009). Effects of baseball weighted implement training: a brief review. "
    "Strength Cond J 31(2):30-37.",
    "Haff GG, Nimphius S (2012). Training principles for power. Strength Cond J 34(6):2-12. https://doi.org/10.1519/SSC.0b013e31826db467",
    "Suchomel TJ, Nimphius S, Stone MH (2016). The importance of muscular strength in athletic "
    "performance. Sports Med 46(10):1419-1449. https://doi.org/10.1007/s40279-016-0486-0",
    "Claudino JG et al. (2017). The countermovement jump to monitor neuromuscular status: "
    "a meta-analysis. J Sci Med Sport 20(4):397-402. https://doi.org/10.1016/j.jsams.2016.08.011",
]


def build_plan_md(name: str, row: dict, dx: dict, chart_file: str | None = None,
                  success: tuple[str, str] | None = None, injury: dict | None = None) -> str:
    oblique = bool(injury and "oblique" in str(injury.get("type", "")))
    p = dx["profile"]
    L = []
    L.append(f"# Offseason Development Plan — {name}")
    L.append("*Emerson Performance (EP) · Emerson Jimenez*\n")
    if chart_file:
        L.append(f"![Bat speed trend]({chart_file})\n")

    L.append("## 1. Data / Datos")
    L.append(f"- Competitive swings: {row['n_early']} early / {row['n_late']} late")
    L.append(f"- Bat speed: {row['bat_speed_early']:.1f} → {row['bat_speed_late']:.1f} mph")
    L.append(f"- Swing length: {row['swing_length_early']:.2f} → {row['swing_length_late']:.2f} ft\n")

    f = dx["finding"]
    L.append(f"## 2. Finding / Hallazgo — `{f['label']}`")
    L.append(f"**EN:** {f['en']}\n\n**ES:** {f['es']}\n")

    it = dx["interpretation"]
    L.append(f"## 3. Biomechanics / Biomecánica — `{it['label']}`")
    L.append(f"**EN:** {it['en']}\n\n**ES:** {it['es']}\n")
    if injury:
        L.append("### Injury context / Contexto de lesión — `INTERPRETATION`")
        L.append(f"- Public report / Reporte público: {injury['context']}")
        L.append("- **EN:** The data cannot separate residual effects of this injury from in-season "
                 "fatigue. Both are plausible contributors to the decline. The plan is adjusted to "
                 "rebuild the injured area progressively, pending medical clearance.")
        L.append("- **ES:** Los datos no pueden separar las secuelas de esta lesión de la fatiga de la "
                 "temporada. Ambas pueden contribuir a la caída. El plan se ajusta para reconstruir la "
                 "zona lesionada de forma progresiva, sujeto a autorización médica.\n")

    L.append(f"## 4. Training application / Aplicación — profile: `{p}`")
    if p == "swing_change":
        L.append("> **EN:** Swing-change profile: the hitting coach leads. The S&C block below is "
                 "general preparation only, with no extra emphasis.\n>\n"
                 "> **ES:** Perfil de cambio de swing: lo lidera el coach de bateo. El bloque de "
                 "fuerza de abajo es solo preparación general, sin énfasis extra.\n")
    if oblique:
        L.append("> **EN:** Oblique strain this season: rotational work follows an anti-rotation → "
                 "controlled rotation → ballistic progression. Each step only if symptom-free and "
                 "cleared by the club's medical staff.\n>\n"
                 "> **ES:** Distensión de oblicuo esta temporada: el trabajo rotacional sigue la "
                 "progresión anti-rotación → rotación controlada → balística. Cada paso solo sin "
                 "síntomas y con autorización del cuerpo médico del club.\n")
    # Table header goes after any note so the markdown table stays intact
    # El encabezado va después de las notas para que la tabla no se rompa
    L.append("| Weeks | Phase / Fase | Work / Trabajo |\n|---|---|---|")
    for ph in PHASES:
        items = ph["base"] + ph.get(p, [])
        if oblique:
            items = [it for it in items if it[0] not in OBLIQUE_REMOVE] + OBLIQUE_OVERRIDE.get(ph["weeks"], [])
        work = "<br>".join(f"{en} / *{es}*" for en, es in items)
        L.append(f"| {ph['weeks']} | {ph['en']} / *{ph['es']}* | {work} |")
    if dx["progressive"]:
        L.append("\n**In-season / En temporada** (decline was progressive / la caída fue progresiva):")
        L += [f"- {en} / *{es}*" for en, es in IN_SEASON]
    L.append("")

    L.append("## 5. Monitoring / Monitoreo")
    L += [f"- {en} / *{es}*" for en, es in MONITORING]
    L.append("")

    L.append("### Success threshold / Umbral de éxito — natural rebound baseline")
    if success:
        L.append(f"**EN:** {success[0]}\n\n**ES:** {success[1]}\n")
    else:
        L.append("**EN:** Not computed. Run with `--prev-input` (previous season) to set it. "
                 "Without it, a 2027 improvement cannot be attributed to the plan.\n\n"
                 "**ES:** No calculado. Corre con `--prev-input` (temporada anterior) para "
                 "definirlo. Sin él, una mejora en 2027 no se puede atribuir al plan.\n")

    L.append("## Limitations / Limitaciones")
    L.append("- No access to the player's medical, workload or training history. "
             "The plan is a template to individualize after an in-person assessment.")
    L.append("- A bat speed decline can also come from approach changes (e.g., two-strike "
             "swings), minor injury, or mechanical changes. The data cannot separate these.")
    L.append("- *Sin acceso al historial médico, de carga ni de entrenamiento del jugador. "
             "El plan es una plantilla para individualizar tras una evaluación en persona.*")
    L.append("- *La caída también puede venir de cambios de enfoque (ej. swings con dos strikes), "
             "lesiones menores o cambios mecánicos. Los datos no separan estas causas.*\n")

    L.append("## Literature / Literatura")
    L += [f"- {ref}" for ref in LITERATURE]
    return "\n".join(L) + "\n"
