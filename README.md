# EP Offseason Development Plan

**From a Statcast decline to a 12-week strength plan — with the monitoring metric that proves whether it worked.**
*De una caída en Statcast a un plan de fuerza de 12 semanas, con la métrica de monitoreo que demuestra si funcionó.*

Emerson Performance (EP) · Emerson Jimenez

---

## Why this repo / Por qué este repo

Most public analytics work stops at the finding. A player development staff has to answer the next question: *what do we do about it this offseason, and how will we know it worked?* This repo connects both sides — the data and the weight room — using the EP four-layer template.

*La mayoría del análisis público termina en el hallazgo. Un staff de desarrollo tiene que responder la siguiente pregunta: qué hacemos en esta offseason y cómo sabremos si funcionó. Este repo une las dos partes, los datos y el gimnasio, con la plantilla de cuatro capas de EP.*

| Layer / Capa | What it does / Qué hace | File |
|---|---|---|
| 1. Data | Competitive swings, first 6 vs last 6 weeks of 2026 | `src/select_player.py` |
| 2. Finding | Mann-Whitney + Benjamini-Hochberg + Cohen's d → `CONFIRMED` / `NOT CONFIRMED` | `src/select_player.py` |
| 3. Biomechanics | Rule-based reading: **force** vs **efficiency** profile → `INTERPRETATION` | `src/diagnose.py` |
| 4. Training | 12-week block, emphasis changes by profile | `src/plan_builder.py` |
| 5. Monitoring | Required: bat sensor. Recommended: med ball, CMJ height. Optional: force-plate RFD. 2027 follow-up vs natural rebound threshold | `src/plan_builder.py`, `src/natural_rebound.py` |

## Method / Método

- **Competitive swings / Swings competitivos:** each hitter's slowest 10% removed, swings ≥ 60 mph always kept (Baseball Savant–style filter).
- **Windows / Ventanas:** first 6 weeks vs last 6 weeks of the season; minimum 75 competitive swings in each.
- **Test:** one-sided Mann-Whitney U (early > late), corrected with **Benjamini-Hochberg** because the whole league is tested at once. `CONFIRMED` requires BH-q < 0.05 **and** a drop ≥ 1.0 mph (statistical *and* practical significance).
- **Profile rule / Regla de perfil:**
  - Swing length up ≥ 0.2 ft while bat speed falls → **efficiency** (sequencing / energy transfer).
  - Swing length down ≥ 0.2 ft → **swing_change**: a shorter swing produces less bat speed by itself (in the 2026 data, bat speed loss and swing shortening correlate, r = 0.49). The hitting coach leads; these hitters are not auto-selected for an S&C plan.
  - Swing length stable (within ±0.2 ft) → **force** (power production).
- **Injury / absence filter / Filtro de lesiones y ausencias:**
  - *Automatic:* a gap of ≥ 14 days without games from 4 weeks before the late window to season end, or ≥ 10 days missed at the end of the season, flags a possible IL stint and the hitter is skipped.
  - *Manual:* `data/injury_exclusions.csv` (columns `batter_name, action, injury_type, reason`, with a public source in `reason`). `action = exclude` skips the hitter; `action = annotate` keeps him eligible and adds the injury context to the plan. With `injury_type = oblique`, rotational work follows an anti-rotation → controlled rotation → ballistic progression, pending medical clearance.
- **League summary / Resumen de liga:** `output/decline_causes_summary.md` classifies every `CONFIRMED` decline (known injury, absence, swing change, possible force loss). In 2026, **11 of 21 confirmed declines (52%) had an explanation other than strength loss**. Injuries that create no gap and are not in the file are missed, so the "possible force loss" group is an upper bound.
  - *Una lesión cerca de la ventana final no es pérdida de fuerza. Un hueco de 14+ días sin juegos, o terminar la temporada antes, excluye al bateador automáticamente.*
- **Correction log / Registro de correcciones:**
  - v1 treated a shorter swing as "force" and selected Jazz Chisholm (thumb sprain in early September 2026, swing −0.4 ft). Fixed in v2 with the `swing_change` profile.
  - v2 relied on manual injury checks and Samuel Basallo was recommended; his late window started right after a right (lead) shoulder IL stint (July 20 – mid-August 2026). Fixed in v3 with automatic absence detection.
  - v3 selected Vaughn Grissom, whose oblique-strain IL stint (early June 2026) fell outside the absence check. v4 keeps him as the application case with the injury context and an oblique-specific progression, instead of a generic plan.
  - Spearman weekly trend ρ < −0.3 (p < 0.05) → decline is **progressive** → in-season maintenance section added.
- **Natural rebound baseline / Línea base de recuperación natural** (`src/natural_rebound.py`): hitters with a `CONFIRMED` decline in the previous season are followed into the first 6 weeks of the next one. Their recovery, adjusted for the league-wide shift measured in all other hitters, is what happens *without* the plan. The plan only counts as successful if the player's recovery exceeds the **75th percentile** of that natural rebound. Regression to the mean is included on purpose: the plan has to beat everything that happens without it.
- *Los bateadores con caída `CONFIRMED` en la temporada anterior se siguen hasta las primeras 6 semanas de la siguiente. Su recuperación, ajustada por el cambio general de la liga, es lo que pasa **sin** el plan. El plan solo es éxito si el jugador supera el **percentil 75** de esa recuperación natural.*
- No ML and no LLM-generated text. Every rule is visible and auditable in the code.
- *Sin ML y sin texto generado por LLM. Cada regla es visible y auditable en el código.*

## Run it / Cómo correrlo

```bash
pip install -r requirements.txt
# Use the same 2026 Statcast pull from ep-bat-speed-fatigue
# Usa el mismo pull de Statcast 2026 de ep-bat-speed-fatigue
python src/run_pipeline.py --input data/statcast_2026.csv --top 1
# With the natural rebound baseline (needs the 2025 pull too)
# Con la línea base de recuperación natural (necesita también el pull de 2025)
python src/run_pipeline.py --input data/statcast_2026.csv --prev-input data/statcast_2025.csv --top 1
# Force a specific hitter / Forzar un bateador específico:
python src/run_pipeline.py --input data/statcast_2026.csv --batter <MLBAM_ID>
```

Required columns / Columnas necesarias: `batter, game_date, bat_speed, swing_length`.
Outputs in `output/`: league leaderboard CSV, weekly trend chart, and the bilingual plan (`*_offseason_plan.md`).

**Testing / Pruebas:** `python src/make_synthetic.py` creates synthetic test data. It is **not** real players and must not be published.
*`make_synthetic.py` crea datos sintéticos de prueba. **No** son jugadores reales y no se deben publicar.*

## Limitations / Limitaciones

1. **No medical, workload or training history.** The plan is a template for a coach to individualize after an in-person assessment, not a prescription.
2. **Cause is not identified by the data.** A bat speed decline can come from fatigue, minor injury, approach changes (e.g., more two-strike swings late in the season), or deliberate mechanical changes. The force/efficiency split is an `INTERPRETATION`.
3. **Swing length is an indirect proxy** for path efficiency; it does not measure hip-trunk separation.
4. **Early vs late windows** are sensitive to schedule and roster moves (IL stints, call-ups).
5. If no hitter reaches `CONFIRMED`, the pipeline produces no plan. That is a valid result and is reported as such.
6. **The natural rebound baseline comes from one offseason (2025→2026).** It does not know what each player actually did that winter, and one season-to-season transition may not generalize. With fewer than 10 decliners it is flagged as provisional.

1. *Sin historial médico, de carga ni de entrenamiento. El plan es una plantilla para individualizar tras una evaluación en persona.*
2. *Los datos no identifican la causa: fatiga, lesión menor, cambio de enfoque o cambio mecánico intencional. La separación fuerza/eficiencia es una `INTERPRETATION`.*
3. *El swing length es un indicador indirecto de eficiencia; no mide la separación cadera-tronco.*
4. *Las ventanas son sensibles al calendario y movimientos de roster.*
5. *Si ningún bateador llega a `CONFIRMED`, no se genera plan. Es un resultado válido.*
6. *La línea base viene de una sola offseason (2025→2026). No sabe qué hizo cada jugador ese invierno. Con menos de 10 bateadores se marca como provisional.*

## Link to EP research / Conexión con la investigación de EP

The monitoring layer is built so any staff can use it. **Only one thing is required during the offseason:** bat speed from a bat sensor. The 2027 Statcast check is a follow-up, compared against the natural rebound threshold. Med ball throws and jump height are **recommended**: they do not make the plan more reliable, but if bat speed does not improve they show *why* (force improved but did not transfer, or force did not improve). **Early-phase CMJ RFD (0–100 ms)** is optional, for clubs with force plates — it is the variable proposed as a bat speed predictor in the EP SABR Research Grant proposal.

*La capa de monitoreo está pensada para que cualquier staff la use. **Solo una cosa es requerida durante la offseason:** bat speed con sensor. El Statcast de 2027 es seguimiento, comparado contra el umbral de recuperación natural. Balón medicinal y altura de salto son **recomendados**: no hacen el plan más confiable, pero si el bat speed no mejora explican por qué. La **RFD temprana del CMJ** es opcional, para clubes con plataformas de fuerza; es la variable de la propuesta de EP para el SABR Research Grant.*

## Literature / Literatura

*All references verified against publisher or university repository records (October 2026). / Todas las referencias verificadas contra registros de editorial o repositorio universitario (octubre 2026).*


- Welch CM et al. (1995). Hitting a baseball: a biomechanical description. *JOSPT* 22(5):193–201.
- Szymanski DJ et al. (2007). Effect of twelve weeks of medicine ball training on high school baseball players. *J Strength Cond Res* 21(3):894–901. https://doi.org/10.1519/R-18415.1
- DeRenne C, Szymanski DJ (2009). Effects of baseball weighted implement training: a brief review. *Strength Cond J* 31(2):30–37.
- Haff GG, Nimphius S (2012). Training principles for power. *Strength Cond J* 34(6):2–12. https://doi.org/10.1519/SSC.0b013e31826db467
- Suchomel TJ, Nimphius S, Stone MH (2016). The importance of muscular strength in athletic performance. *Sports Med* 46(10):1419–1449. https://doi.org/10.1007/s40279-016-0486-0
- Claudino JG et al. (2017). The countermovement jump to monitor neuromuscular status: a meta-analysis. *J Sci Med Sport* 20(4):397–402. https://doi.org/10.1016/j.jsams.2016.08.011

Data: Baseball Savant (MLB Advanced Media). Not affiliated with MLB.
