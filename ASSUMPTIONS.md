# Assumptions & Interpretation Decisions

The paper's spreadsheet is not public, so several mechanics are underspecified.
This file records every decision made to fill the gaps, so the reproduction is
auditable. Each entry: what the paper says, the ambiguity, and the choice made.

## A1. The "21 assets" per basic set

Table 2 lists exactly 21 units in a basic set:
1 power station + 5 excavators + 1 gas chem plant + 1 solids chem plant +
1 metals refinery + 1 solar-cell maker + 4 small printers + 4 large printers +
3 robonauts = **21**.

**Decision:** Treat the 21-unit set as the fixed recipe. Robonauts (X) and
electronics-makers (Y) are tracked as *separate populations* sized by the
labor/electronics equations, not double-counted against the 21. The flow
diagram's `21*W` term is structural assets; `U` (robonauts) and `V` (elec
makers) are added on top.

## A2. Structural mass vs. electronics mass

Table 2 has a "Mass minus Electronics" column and a separate "Mass of
Electronics" column.

**Decision:** Printers fabricate **structural** mass (mass-minus-electronics).
Electronics are handled separately: a fraction `F(N)` made locally, `(1-F)`
imported from Earth. This cleanly explains the launch-mass curves (Fig. 4):
launch mass after Gen 1.0 is dominated by imported electronics.

## A3. Production rate

**Decision:** Only printers contribute to fabrication throughput. Per set:
8 printers (4 small + 4 large) x printer_speed. Baseline printer_speed used for
the canonical growth case is **0.4 kg/hr** (text: "baseline case with 70% duty
cycle, 0.4 kg/h printer speeds"), giving 3.2 kg/hr/set. Table 2's "4 kg/hr"
row corresponds to 0.5 kg/hr printers; printer speed is the swept parameter.

## A4. Crudeness factor

Per paper: Gen 2.0 & 2.5 = 2.5x mass; Gen 3.0 = 1.5x; Gen 4.0+ = 1.0x;
Gen 1.0 = 1.0 (Earth-built).

**Decision:** Crudeness multiplies the **mass of the hardware being produced**
(i.e. of generation N+1 when N is the producer). It inflates mass-to-print; it
does not change printer throughput.

## A5. Closure fraction F (electronics made locally)

Paper, Fig. 1 table: F = 0.00, 0.00, 0.90, 0.95, 0.99, 1.00 for
Gen 1.0, 2.0, 2.5(?), 3.0, 4.0, 5.0. Text gives Gen 3.0/4.0/5.0/6.0 targets of
90%/95%/99%/100%.

**Decision:** Use F by generation:
`{1.0:0, 2.0:0, 2.5:0, 3.0:0.90, 4.0:0.95, 5.0:0.99, 6.0:1.00}`.
(The Fig.1 inset lists 6 rows 1.0–6.0 as 0,0,0.9,0.95,0.99,1.0; the text aligns
the 90/95/99/100 with Gen 3/4/5/6. We follow the text's generation alignment
and set Gen 2.5 = 0, consistent with "import electronics boxes" at Gen 2.5.)

## A6. RWPA (Robonaut Weeks Per Asset)

Paper: "RWPA for successive generations is 4, 4, 6, 7, 7 and 8."

**Decision:** Map in generation order:
`{1.0:4, 2.0:4, 2.5:6, 3.0:7, 4.0:7, 6.0:8}` — six values for the six
producing generations (1.0 through 5.0 produce; 6.0 uses 8). Robonaut work-weeks
available per generation = `104 weeks * duty_cycle` per robonaut over a 2-yr
generation. For Gen <= 2.5 robonauts are imported from Earth (not fabricated),
so they are not subtracted from local production but ARE counted/launched.

## A7. Electronics-maker throughput (THE one calibrated unknown)

Paper gives electronics-maker mass/power but **not** an output rate (kg of
electronics per hour). This is the single parameter we calibrate.

**Decision:** Introduce `ELEC_THROUGHPUT_KG_PER_HR` as a named constant.
Calibrate it once against Fig. 3 (electronics production) / Fig. 4 (launch-mass
divergence of the "no chip fab" case), then freeze it for all other figures.
Initial guess: O(0.01–0.1 kg/hr) per maker, since electronics are low-mass,
high-value. Final value recorded here after calibration.

  -> Calibrated value: **0.2 kg/hr** per electronics-maker. Chosen so the Gen-6
  asset mass in Fig. 2 lands near the paper's ~30,000 MT (model gives ~29,000).
  This implies each maker produces ~2.4 t of electronics over a 2-yr/70%
  generation — physically reasonable for an electronics production line. Frozen
  for all other figures. (Side effect: robonaut count comes out ~1.5-2x the
  paper's at late generations — recorded as a known divergence, not tuned away.)

## A8. "Reduced manufacturing rate = half"

Text: reduced case "reduces the time-averaged manufacturing rate to half its
maximum" via voluntary pausing.

**Decision:** Model as a 0.5 utilization multiplier on throughput (equivalent to
pausing half the time), NOT as halving printer hardware speed.

## A9. Generation timing and solar duty cycle

**Decision:** Baseline generation length = 2 years = 17,520 hr. Baseline solar
duty cycle = 0.70 (peak-of-eternal-light, sun-following). Sweeps: duty cycle
{0.4,0.5,0.6,0.7}; printer speed {0.1..0.5 kg/hr}; RWPA x{1/3,1,3}.

## A10. Asset mass reported (Figs. 2, 6, 13)

**Decision:** "Mass of assets" at Gen N = total mass of Gen N's hardware present
= `Z_N * m_set_total * crude(N)` + robonaut mass + elec-maker mass + cumulative
solar-cell mass. Solar cells and robonauts accumulate (not retired); other
assets retired at end of their generation (paper's conservative assumption).
Gen 1.0 ~= 7.7 MT (one set), matching Table 2's "~7.7 MT launched to Moon".

## A11. Launch mass (Figs. 4, 14)

**Decision:** Mass launched from Earth =
- Gen 1.0: the entire first set (~7.7 MT).
- Gen >= 2.0: imported electronics `(1-F(N)) * E_total(N)` + imported robonaut
  electronics/whole robonauts for Gen <= 2.5.
Variant cases: "no electronics fab" => F=0 everywhere (all electronics
imported); "no chip fab" => F capped so chips always imported.

## A12. Spacecraft / set-aside accounting

**Decision:** Gen 3.0 −80 MT, Gen 4.0 −10 MT, Gen 5.0 −120 MT subtracted from
that generation's available structural production before computing W.
