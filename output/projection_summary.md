# Projection test: does late-season bat speed carry into next season? (2025 → 2026)
*¿El bat speed de fin de temporada se arrastra a la siguiente? (2025 → 2026)*

*Emerson Performance (EP) · Emerson Jimenez · Data: Baseball Savant*

Hitters with ≥ 300 competitive swings in both seasons and ≥ 75 in each window: **225**. Models: linear regression, leave-one-out cross-validation.

## A. First 6 weeks of 2026 / Primeras 6 semanas — `NOT CONFIRMED`

| Predictor (2025) | LOO MAE (mph) | LOO R² |
|---|---|---|
| Full-season mean / Promedio de temporada | 0.755 | 0.857 |
| Last 6 weeks / Últimas 6 semanas | 0.786 | 0.846 |
| Both / Ambos | 0.745 | 0.861 |

MAE(full) − MAE(late) = **-0.031 mph** (95% bootstrap CI -0.086 to +0.023). Positive = last 6 weeks predicts better.
Both-predictor model weights: full-season 0.62, last 6 weeks 0.33.

**EN:** No reliable difference: late-season bat speed does not beat the full-season mean.
**ES:** Sin diferencia confiable: el bat speed de fin de temporada no supera al promedio de temporada.

## B. Full 2026 season / Temporada completa — `NOT CONFIRMED`

| Predictor (2025) | LOO MAE (mph) | LOO R² |
|---|---|---|
| Full-season mean / Promedio de temporada | 0.712 | 0.870 |
| Last 6 weeks / Últimas 6 semanas | 0.769 | 0.851 |
| Both / Ambos | 0.709 | 0.871 |

MAE(full) − MAE(late) = **-0.056 mph** (95% bootstrap CI -0.112 to +0.000). Positive = last 6 weeks predicts better.
Both-predictor model weights: full-season 0.72, last 6 weeks 0.23.

**EN:** No reliable difference: late-season bat speed does not beat the full-season mean.
**ES:** Sin diferencia confiable: el bat speed de fin de temporada no supera al promedio de temporada.

## Limitations / Limitaciones
- One season pair. Survivor bias: only hitters who played enough in both seasons are included.
- The late window is part of the full season, so the predictors overlap.
- Bat speed only; this does not test whether the change carries into outcomes (xwOBA, barrels).
- *Un solo par de temporadas. Sesgo de supervivencia: solo bateadores que jugaron suficiente en ambas.*
- *La ventana final es parte de la temporada completa, así que los predictores se solapan.*
- *Solo bat speed; no prueba si el cambio se traslada a resultados (xwOBA, barrels).*
