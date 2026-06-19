# Reproduction Plan

Reproducing **Metzger, Muscatello, Mueller & Mantovani (2013), "Affordable,
Rapid Bootstrapping of the Space Industry and Solar System Civilization,"
*Journal of Aerospace Engineering* 26(1):18-29**, DOI
10.1061/(ASCE)AS.1943-5525.0000236. The PDF in `docs/` is the authors'
preprint; full citation in `CITATION.cff` / `README.md`.

## Goal & ground rules

- Reproduce the **method** described in the paper and regenerate all 14 figures.
- **Qualitative** match is the target. Match the shapes, trends, orders of
  magnitude, and cross-over points — not bug-for-bug numbers.
- **No overfitting.** Lock baseline parameters from Tables 1 & 2 up front.
  Calibrate only the single genuine unknown (electronics-maker throughput)
  against one figure, then generate everything else with no further tuning.
- When curves diverge from the paper, **report the divergence** rather than
  tuning assumptions to hide it. Method fidelity > number matching.

## The model (reconstruction of Fig. 1)

A six-generation evolutionary spiral (Gen 1.0, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0).
Each generation's machines fabricate the hardware of the next. The model is a
**two-directional recursion** solved by fixed-point iteration:

- **Forward:** Gen N's printers fabricate Gen N+1's hardware -> `Z_{N+1} = W_N`
  (basic sets propagate forward).
- **Backward:** Gen N+1's needs (robonauts X, electronics-makers Y) become Gen
  N's production targets -> `U_N = X_{N+1}`, `V_N = Y_{N+1}`.

Because W depends on throughput diverted to U/V, and U/V depend on next gen's W,
it is circular and must be iterated to consistency (paper says exactly this).

### Core per-generation equations

```
Throughput:   P_N   = Z_N * (printers/set * printer_speed) * duty_cycle * T_gen
Basic sets:   W_N   = [P_N - crude(N+1)*(U*m_robo + V*m_elec) - F(N+1)*E_total]
                      / (crude(N+1) * m_set_struct)
Robonauts:    X_N   = (U + V + 21*W_N) * RWPA(N) / (weeks_per_gen * duty_cycle)
Elec makers:  Y_N   = F(N+1)*E_total / (elec_throughput * duty_cycle * T_gen)
E_total              = e_set*W_N + e_robo*U + e_elec*V   (electronics mass)
```

Set-asides subtracted from output: Gen 3.0 −80 MT (construction eq.),
Gen 4.0 −10 MT (building reinforcement), Gen 5.0 −120 MT (6 spacecraft for the
asteroid-belt seed).

## High-level steps

1. [done] Set up Python environment (venv, numpy, matplotlib).
2. [in progress] Document PLAN.md + ASSUMPTIONS.md.
3. `parameters.py` — all Table 1/2 constants and documented assumptions.
4. `model.py` — per-generation engine + fixed-point iterator.
5. Reproduce **Fig. 2** (baseline growth); iterate until satisfied; calibrate
   the one unknown here.
6. `figures.py` — mass-produce Figs. 3–14 with parameter sweeps.
7. Final review: side-by-side comparison, divergence report, revisit plan.

## Artifacts

- `parameters.py`, `model.py`, `figures.py`
- `ASSUMPTIONS.md` — every interpretation decision (auditable)
- `figures/` — 14 output PNGs
- `PLAN.md` (this file) — revisited as work proceeds

## Plan log (revisited over time)

- **Init:** Plan agreed with user. Run the whole thing; iterate Fig. 2 to
  satisfaction before mass-producing; roughly match style; match method.
- **Build:** Env (venv), parameters, model engine + damped fixed-point iterator
  all done. Set masses match Table 2 exactly (21 assets, 7.7 MT).
- **Fig. 2 checkpoint:** Corrected printer speed 0.4 -> 0.5 (Fig. 2 max case),
  calibrated the one unknown (electronics throughput = 0.2 kg/hr) so Gen-6 mass
  hits ~29,000 MT. Strong match. Proceeded to mass-produce.
- **Figs. 3-14:** All generated. Fixed two bugs found in review: (a) Fig. 4
  "no chip fab" import fraction (50% -> 5%, since chips are a small mass
  fraction); (b) Figs. 9-11 production scheme (per-set budget held constant via
  gen-length stretch ∝ 1/speed, replacing a broken 6 MT/set cap that shrank the
  industry to zero).
- **Final review:** 13/14 figures strong qualitative matches; Fig. 11 partial
  (monotonic vs paper's gentle peak) — documented as a divergence, not tuned
  away. See README.md fidelity table + divergences. Plan complete.
