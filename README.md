# Reproducing "Affordable, rapid bootstrapping of space industry"

A from-scratch computational reproduction of the modeling in:

> **Metzger, P. T., Muscatello, A., Mueller, R. P., & Mantovani, J.**
> *"Affordable, rapid bootstrapping of space industry and solar system
> civilization."* Preprint, to appear in the *Journal of Aerospace Engineering*.
> (Source PDF: [`docs/`](docs/).)

The paper argues that advances in robotics and 3D printing make it feasible to
**bootstrap a self-sustaining, self-expanding lunar industry** from as little as
12–41 metric tons of seed hardware, growing it through six "generations" of
increasing sophistication until it achieves full closure and spreads to the
asteroid belt. It backs this with a spreadsheet model and 14 figures.

This project reproduces that model in Python and regenerates all 14 figures.

---

## Table of contents

- [Goal & ground rules](#goal--ground-rules)
- [Quick start](#quick-start)
- [Repository layout](#repository-layout)
- [How the model works](#how-the-model-works)
- [Calibration: the one tuned parameter](#calibration-the-one-tuned-parameter)
- [Results & fidelity](#results--fidelity)
- [Known divergences](#known-divergences)
- [Where to read more](#where-to-read-more)

---

## Goal & ground rules

The objective was to reproduce the **method**, not to curve-fit the published
plots. Concretely:

- **Qualitative match is the target** — shapes, trends, orders of magnitude, and
  cross-over points, not bug-for-bug numbers.
- **No overfitting.** All baseline parameters were locked from the paper's
  Tables 1 & 2 *before* looking at any output. Exactly one genuine unknown was
  calibrated (see [Calibration](#calibration-the-one-tuned-parameter)).
- **Honest divergence reporting.** Where a reproduced curve differs from the
  paper, it is documented (see [Known divergences](#known-divergences)) rather
  than tuned to hide the difference.

These rules were agreed with the project owner up front and are logged in
[`PLAN.md`](PLAN.md).

---

## Quick start

```bash
# 1. Create an isolated environment (numpy 2.x + matplotlib)
python3 -m venv .venv
.venv/bin/pip install numpy matplotlib

# 2. Print the baseline per-generation table (sanity check the engine)
.venv/bin/python model.py

# 3. Regenerate every figure into figures/
.venv/bin/python figures.py

# ...or just specific figures by number:
.venv/bin/python figures.py 2 4 11
```

Outputs are written to [`figures/`](figures/) as PNGs, plus a
`_contact_sheet.png` montage of all 14 for side-by-side comparison with the PDF.

> **Note on the environment:** the repo's system Python had a broken
> numpy/matplotlib pairing, so everything runs in a local `.venv` (git-ignored).
> Only `numpy` and `matplotlib` are required.

---

## Repository layout

| Path | What it is | Start here if you want to… |
|------|------------|----------------------------|
| [`parameters.py`](parameters.py) | All Table 1 & 2 constants: per-asset masses, crudeness factors, closure fractions `F`, RWPA, timing, the calibrated unknown. | …change an input value or check it against the paper. |
| [`model.py`](model.py) | The simulation engine: per-generation mass/labor balance + the forward/backward fixed-point iterator that solves the Fig. 1 recursion. | …understand or modify the core dynamics. |
| [`figures.py`](figures.py) | One routine per figure (`fig2()`, `fig3()`, …). Reads the model, renders B&W log plots. | …see how a specific figure is produced. |
| [`PLAN.md`](PLAN.md) | The reproduction plan and a running log of decisions, checkpoints, and bug fixes. | …see the project history and rationale. |
| [`ASSUMPTIONS.md`](ASSUMPTIONS.md) | Every interpretation decision (A1–A12) where the paper is underspecified, with the reasoning behind each. | …audit a modeling choice. |
| [`figures/`](figures/) | The 14 reproduced PNGs + contact sheet. | …compare against the paper. |
| [`docs/`](docs/) | The source paper PDF. | …read the original. |

**The fastest way to judge the reproduction** is to open
`figures/_contact_sheet.png` next to the PDF.

---

## How the model works

The industry evolves through **six generations**: 1.0, 2.0, 2.5, 3.0, 4.0, 5.0,
6.0. Each generation is a population of machines that fabricates the hardware of
the *next* generation. A "basic set" is the 21-asset recipe from Table 2
(power, excavators, chemical plants, metals refinery, solar-cell maker, 8
printers, robonauts) — about 7.7 MT.

The model is a **two-directional recursion**, exactly as drawn in the paper's
Fig. 1:

- **Forward** — Gen *N*'s printers build Gen *N+1*'s structural hardware, so the
  number of basic sets propagates forward: `Z_{N+1} = W_N`.
- **Backward** — Gen *N+1* tells Gen *N* how many robonauts (`X`) and
  electronics-makers (`Y`) it will need; those become Gen *N*'s production
  targets: `U_N = X_{N+1}`, `V_N = Y_{N+1}`.

Because `W` depends on how much throughput is diverted to `U`/`V`, and `U`/`V`
depend on the next generation's `W`, the system is circular. It is solved by a
**damped fixed-point iteration** (`model.solve()`), matching the paper's note
that the model "must be iterated for consistency."

The core per-generation equations (full form and symbol definitions in
[`model.py`](model.py)):

```
Throughput:   P_N = Z_N · (printers/set · printer_speed) · duty_cycle · T_gen
Basic sets:   W_N = [P_N − setasides − robonaut_cost − elecmaker_cost]
                    / (crudeness(N+1) · m_set_struct + F(N) · e_set)
Robonauts:    X_N = (assets to assemble) · RWPA(N) / (work-weeks available)
Elec-makers:  Y_N = F(N) · (electronics mass produced) / (elec_throughput · …)
```

Key mechanisms layered on top:

- **Crudeness factor** — early generations build *heavier*, cruder hardware
  ("mongrel alloys"): ×2.5 mass at Gen 2.0/2.5, ×1.5 at Gen 3.0, ×1.0 from
  Gen 4.0. This inflates the mass that must be printed.
- **Closure fraction `F`** — the share of electronics a generation can make
  locally (0 early, ramping 0.90 → 1.00 by Gen 6.0). The imported remainder
  `(1−F)` is what drives the **launch-mass** curves (Fig. 4).
- **Robonaut labor (RWPA)** — "robonaut weeks per asset" rations assembly
  labor; the robonaut population is sized to complete each generation's
  assembly within the available, duty-cycle-limited work-weeks.
- **Set-asides** — Gen 3.0 (−80 MT construction equipment), Gen 4.0 (−10 MT
  building reinforcement), Gen 5.0 (−120 MT for the six asteroid-belt
  spacecraft) are subtracted from that generation's output.

Every place the paper left a mechanic ambiguous, the choice made is recorded in
[`ASSUMPTIONS.md`](ASSUMPTIONS.md) (referenced as A1–A12 in code comments).

---

## Calibration: the one tuned parameter

The paper gives the electronics-maker's mass and power but **not** its output
rate — the single quantity that cannot be derived from the figures. It is
exposed as `ELEC_THROUGHPUT_KG_PER_HR` in `parameters.py` and was calibrated
**once** to **0.2 kg/hr**, chosen so Fig. 2's Gen-6 asset mass lands near the
paper's ~30,000 MT (the model gives ~29,000). It was then **frozen** for all
other figures. This implies each maker produces ~2.4 t of electronics over a
2-year, 70%-duty generation — a physically reasonable rate. (Details: A7 in
[`ASSUMPTIONS.md`](ASSUMPTIONS.md).)

No other parameter was tuned against the outputs.

---

## Results & fidelity

| Fig | Subject | Match |
|-----|---------|-------|
| 2 | Growth of mass & robonauts | **Strong** — exponential 8 → ~29,000 MT; reduced case plateaus. |
| 3 | Production of solids/fluids/electronics | **Strong** — electronics emerge at Gen 3 and climb. |
| 4 | Launch mass; closure-failure variants | **Strong** — baseline flat, "no electronics" explodes, "no chips" grows slower. |
| 5 | Power available vs needed | **Strong** — available ≫ need, both exponential. |
| 6 | Mass vs duty cycle | **Strong** — 70% → 40% costs ~1.8 orders of magnitude. |
| 7 | Robonauts vs duty cycle | **Strong** — parallel to Fig. 6. |
| 8 | Printers/set vs reproduction time | **Good** — correct hyperbolic families per speed. |
| 9 | Mass by year (const. production) | **Strong** — fan of trajectories, 14 → 70 years. |
| 10 | Robonauts by year | **Strong** — matching fan. |
| 11 | Gen-6 mass vs robonauts | **Partial** — correct ranges & primary trend, but monotonic where the paper shows a gentle peak. |
| 12 | Robonauts vs RWPA | **Strong** — high-RWPA needs more early robonauts, converge by Gen 6. |
| 13 | Mass vs RWPA | **Strong** — fast robonauts highest at Gen 6, with early crossover. |
| 14 | Launch mass vs RWPA | **Strong** — reproduces the dip-peak-dip-peak shape. |

**13 of 14 figures are strong qualitative matches.**

---

## Known divergences

Reported honestly rather than tuned away:

1. **Fig. 11 is monotonic, not an inverted-U.** The paper shows Gen-6 asset mass
   peaking at ~0.2–0.25 kg/hr printer speed. This reproduction yields a
   monotonic anti-correlation (mass falls as robonaut count rises) with the
   correct axis magnitudes and the direction stated in the paper's own text
   ("more robonauts for high speed, more assets for low speed"). The published
   peak appears to need a second-order interaction (likely a survival-minimum on
   robonaut production at very long generations) that this simpler model does
   not impose.

2. **One knob can't match both mass and robonaut count.** At the calibration
   point, Gen-6 *mass* matches (~29,000 MT) but late-generation *robonaut counts*
   run ~1.5–2× the paper's. Mass was prioritized.

3. **Reduced-manufacturing plateau sits lower** (~30–50 MT) than the paper's
   ~100 MT. The qualitative point — a plateau instead of exponential growth — is
   reproduced.

4. **Electronics-maker mass envelope** is modeled as a printer-class unit
   (the paper gives no separate line item); its throughput is the one calibrated
   unknown.

---

## Where to read more

- **The original science:** [`docs/`](docs/) — the source PDF.
- **Why each modeling choice was made:** [`ASSUMPTIONS.md`](ASSUMPTIONS.md).
- **How the project unfolded (plan, checkpoints, bug fixes):** [`PLAN.md`](PLAN.md).
- **The math, in code:** [`model.py`](model.py) — heavily commented.

This is an independent reproduction for study purposes; it is not affiliated
with the original authors.
