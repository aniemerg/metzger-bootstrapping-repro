"""Reproduce the paper's figures from the model. Styling roughly mimics the
paper: black & white, log axes, marker-per-series, for easy side-by-side.

Run:  python figures.py          # produces all figures into figures/
      python figures.py 2        # produce only Fig. 2
"""
import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import parameters as P
from model import Config, solve

OUT = os.path.join(os.path.dirname(__file__), "figures")
os.makedirs(OUT, exist_ok=True)

GENS = P.GENERATIONS
MT = P.KG_PER_TON  # kg per metric ton

plt.rcParams.update({
    "font.size": 9, "axes.grid": True, "grid.alpha": 0.3,
    "lines.markersize": 5, "figure.dpi": 130,
})


def _save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {path}")


def _series(cfg, attr, scale=1.0):
    r = solve(cfg)
    return [getattr(r[g], attr) * scale for g in GENS]


# --------------------------------------------------------------------------
def fig2():
    """Growth of lunar industry: asset mass and robonauts, max vs reduced rate."""
    cmax = Config()
    cred = Config(utilization=0.5)  # reduced manufacturing = half rate (A8)

    mass_max = _series(cmax, "asset_mass_kg", 1 / MT)
    mass_red = _series(cred, "asset_mass_kg", 1 / MT)
    robo_max = _series(cmax, "X")
    robo_red = _series(cred, "X")

    fig, ax1 = plt.subplots(figsize=(6, 4.2))
    ax2 = ax1.twinx()
    ax1.plot(GENS, mass_max, "ks-", label="Mass, Max")
    ax1.plot(GENS, mass_red, "s-", mfc="white", color="k", label="Mass, Red.")
    ax2.plot(GENS, robo_max, "k^--", label="Robonauts, Max.")
    ax2.plot(GENS, robo_red, "^--", mfc="white", color="k", label="Robonauts, Red.")

    ax1.set_yscale("log"); ax2.set_yscale("log")
    ax1.set_ylim(1, 1e5); ax2.set_ylim(1, 1e5)
    ax1.set_xlabel("Generation"); ax1.set_ylabel("Mass (ton)")
    ax2.set_ylabel("Number of Robonauts")
    l1, lab1 = ax1.get_legend_handles_labels()
    l2, lab2 = ax2.get_legend_handles_labels()
    ax1.legend(l1 + l2, lab1 + lab2, fontsize=7, loc="upper left")
    ax1.set_title("Fig. 2 (repro): Growth of lunar industry by generation")
    _save(fig, "fig02_growth.png")


# --------------------------------------------------------------------------
def fig3():
    """Production of solids, fluids, electronics by generation (max vs reduced)."""
    cmax, cred = Config(), Config(utilization=0.5)
    rmax, rred = solve(cmax), solve(cred)

    def prod(r, attr):
        return [getattr(r[g], attr) / MT for g in GENS]

    # electronics produced locally = F(N) * electronics mass of produced hardware
    def elec_prod(cfg, r):
        out = []
        for g in GENS:
            F = cfg.F(g)
            E = (r[g].W * P.E_SET + r[g].V * P.E_ELECMAKER
                 + (0 if g <= P.ROBONAUT_IMPORT_THROUGH else r[g].U * P.E_ROBONAUT))
            out.append(F * E / MT)
        return out

    fig, ax = plt.subplots(figsize=(6, 4.2))
    ax.plot(GENS, prod(rmax, "solids_kg"), "ks-", label="Solids, Max.")
    ax.plot(GENS, prod(rred, "solids_kg"), "s-", mfc="white", color="k", label="Solids, Red.")
    ax.plot(GENS, prod(rmax, "fluids_kg"), "k^--", label="Fluids, Max.")
    ax.plot(GENS, prod(rred, "fluids_kg"), "^--", mfc="white", color="k", label="Fluids, Red.")
    e_max, e_red = elec_prod(cmax, rmax), elec_prod(cred, rred)
    ax.plot(GENS, [v if v > 0 else float("nan") for v in e_max], "ko:", label="Electronics, Max.")
    ax.plot(GENS, [v if v > 0 else float("nan") for v in e_red], "o:", mfc="white", color="k", label="Electronics, Red.")

    ax.set_yscale("log"); ax.set_ylim(1, 1e5)
    ax.set_xlabel("Generation"); ax.set_ylabel("Mass (Ton)")
    ax.legend(fontsize=7, loc="upper left")
    ax.set_title("Fig. 3 (repro): Production of materials & parts per generation")
    _save(fig, "fig03_production.png")


# --------------------------------------------------------------------------
def fig4():
    """Mass launched to Moon per generation: baseline & closure-failure variants."""
    baseline = Config()
    no_elec = Config(closure_override={g: 0.0 for g in GENS})           # no electronics fab
    # no chip fab: can make passive electronics (~95%) but never the chips (~5%),
    # so F is capped at 0.95 -> only the small chip fraction is ever imported.
    no_chip = Config(closure_override={g: min(P.CLOSURE_F[g], 0.95) for g in GENS})
    reduced = Config(utilization=0.5)

    fig, ax = plt.subplots(figsize=(6, 4.2))
    ax.plot(GENS, _series(baseline, "launch_kg", 1 / MT), "ks-", label="Baseline Strategy")
    ax.plot(GENS, _series(no_elec, "launch_kg", 1 / MT), "ko:", mfc="white", label="No Electronics Fab")
    ax.plot(GENS, _series(no_chip, "launch_kg", 1 / MT), "k^:", mfc="white", label="No Computer Chips Fab")
    ax.plot(GENS, _series(reduced, "launch_kg", 1 / MT), "s-", mfc="white", color="k", label="Reduced Manufacturing")

    ax.set_yscale("log"); ax.set_ylim(0.01, 1e4)
    ax.set_xlabel("Generation (spaced in 2 year intervals)"); ax.set_ylabel("Mass (ton)")
    ax.legend(fontsize=7, loc="upper left")
    ax.set_title("Fig. 4 (repro): Mass launched to Moon per generation")
    _save(fig, "fig04_launch_mass.png")


# --------------------------------------------------------------------------
def fig5():
    """Power available vs needed (max & reduced)."""
    cmax, cred = Config(), Config(utilization=0.5)
    fig, ax = plt.subplots(figsize=(6, 4.2))
    ax.plot(GENS, _series(cmax, "power_avail_kW", 1e-3), "ks-", label="Available, Max.")
    ax.plot(GENS, _series(cmax, "power_need_kW", 1e-3), "s-", mfc="white", color="k", label="Needs, Max.")
    ax.plot(GENS, _series(cred, "power_avail_kW", 1e-3), "k^--", label="Available, Red.")
    ax.plot(GENS, _series(cred, "power_need_kW", 1e-3), "^--", mfc="white", color="k", label="Needs, Red.")
    ax.set_yscale("log"); ax.set_ylim(0.01, 1e4)
    ax.set_xlabel("Generation"); ax.set_ylabel("Power (MW)")
    ax.legend(fontsize=7, loc="upper left")
    ax.set_title("Fig. 5 (repro): Power generated vs needed")
    _save(fig, "fig05_power.png")


# --------------------------------------------------------------------------
def _duty_cycle_family(attr, scale, ylabel, title, name, ylim=None):
    fig, ax = plt.subplots(figsize=(6, 4.2))
    styles = [("ks-", "70% duty cycle", 0.70), ("ko--", "60% duty cycle", 0.60),
              ("k^-", "50% duty cycle", 0.50), ("kd--", "40% duty cycle", 0.40)]
    for fmt, lab, dc in styles:
        cfg = Config(printer_speed=0.5, duty_cycle=dc)  # text: 1 kg/h units in these cases
        ax.plot(GENS, _series(cfg, attr, scale), fmt, mfc="white", label=lab)
    ax.set_yscale("log")
    if ylim: ax.set_ylim(*ylim)
    ax.set_xlabel("Generation"); ax.set_ylabel(ylabel)
    ax.legend(fontsize=7, loc="upper left"); ax.set_title(title)
    _save(fig, name)


def fig6():
    _duty_cycle_family("asset_mass_kg", 1 / MT, "Mass (Ton)",
                       "Fig. 6 (repro): Asset mass vs generation, by duty cycle",
                       "fig06_duty_mass.png", ylim=(1, 1e5))


def fig7():
    _duty_cycle_family("X", 1.0, "Number of Robonauts",
                       "Fig. 7 (repro): Robonauts vs generation, by duty cycle",
                       "fig07_duty_robonauts.png", ylim=(1, 1e6))


# --------------------------------------------------------------------------
def fig8():
    """Printers per set vs years to reproduce one Gen-1.0 set (crudeness 2.5)."""
    import numpy as np
    fig, ax = plt.subplots(figsize=(6, 4.2))
    # reproduction time of a single seed set making one next-gen (crude 2.5) set,
    # as a function of printer count and speed, two printer-mass variants.
    cf = P.CRUDENESS[2.0]
    base_struct = P.M_SET_STRUCT  # next-gen set structural mass per set
    printer_speeds = [0.01, 0.1, 1.0]
    n_printers = np.array([1, 2, 3, 5, 10, 20, 50, 100, 300, 1000])
    for speed in printer_speeds:
        for mass_mult, ls, mk in [(1.0, "-", "s"), (0.5, "--", "o")]:
            # mass to print = crude * (set struct + extra printer mass added)
            extra_printer_mass = (n_printers - P.PRINTERS_PER_SET).clip(min=0) * \
                                 (0.5 * (169 + 300)) * mass_mult
            total_mass = cf * (base_struct + extra_printer_mass)
            rate = n_printers * speed * P.DUTY_CYCLE_BASELINE  # kg/hr
            years = total_mass / rate / P.HOURS_PER_YEAR
            lbl = f"{speed} kg/hr, {'Std' if mass_mult==1 else 'Low'} Mass"
            ax.plot(years, n_printers, ls, marker=mk, mfc="white" if mass_mult < 1 else "k",
                    color="k", label=lbl, markersize=4)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(0.1, 100); ax.set_ylim(1, 1000)
    ax.set_xlabel("Years to Reproduce One Set"); ax.set_ylabel("Number of Printers per Set")
    ax.legend(fontsize=6, loc="upper right")
    ax.set_title("Fig. 8 (repro): Printers per set vs reproduction time")
    _save(fig, "fig08_printers.png")


# --------------------------------------------------------------------------
def _const_production_run(speed):
    """Hold production-per-generation constant by stretching generation length
    inversely with printer speed (2 yr @ 0.5 kg/hr -> 10 yr @ 0.1 kg/hr, per the
    paper's note that slow printers force ~10-year generations). The asset-mass
    trajectory is then nearly speed-independent, but the robonaut-manufacturing
    burden varies because available work-weeks scale with generation length.
    Returns (cumulative_year, mass_per_gen, robonauts_per_gen)."""
    gen_years = 2.0 * (0.5 / speed)   # speed * gen_years held constant
    cfg = Config(printer_speed=speed, gen_years=gen_years)
    r = solve(cfg)
    years = [(i + 1) * gen_years for i in range(len(GENS))]
    mass = [r[g].asset_mass_kg / MT for g in GENS]
    robo = [r[g].X for g in GENS]
    return years, mass, robo


def fig9_10_11():
    speeds = [0.1, 0.15, 0.2, 0.25, 0.333, 0.4, 0.5]
    markers = ["d", "o", "s", "^", "D", "o", "s"]
    data = {s: _const_production_run(s) for s in speeds}

    # Fig 9: mass of assets vs year of completion
    fig, ax = plt.subplots(figsize=(6, 4.2))
    for s, mk in zip(speeds, markers):
        yrs, mass, _ = data[s]
        ax.plot(yrs, mass, marker=mk, color="k", mfc="white", label=f"{s} kg/hr", markersize=4, lw=0.8)
    ax.set_yscale("log"); ax.set_ylim(1, 1e5); ax.set_xlim(0, 80)
    ax.set_xlabel("Year"); ax.set_ylabel("Mass of Assets (Ton)")
    ax.legend(fontsize=6); ax.set_title("Fig. 9 (repro): Asset mass by year (const. production/gen)")
    _save(fig, "fig09_mass_by_year.png")

    # Fig 10: robonauts vs year
    fig, ax = plt.subplots(figsize=(6, 4.2))
    for s, mk in zip(speeds, markers):
        yrs, _, robo = data[s]
        ax.plot(yrs, robo, marker=mk, color="k", mfc="white", label=f"{s} kg/hr", markersize=4, lw=0.8)
    ax.set_yscale("log"); ax.set_ylim(30, 1e5); ax.set_xlim(0, 60)
    ax.set_xlabel("Year"); ax.set_ylabel("Number of Robonauts")
    ax.legend(fontsize=6); ax.set_title("Fig. 10 (repro): Robonauts by year (const. production/gen)")
    _save(fig, "fig10_robonauts_by_year.png")

    # Fig 11: Gen-6 mass vs Gen-6 robonauts (non-monotonic)
    fig, ax = plt.subplots(figsize=(6, 4.2))
    xs = [data[s][2][-1] for s in speeds]  # gen-6 robonauts
    ys = [data[s][1][-1] for s in speeds]  # gen-6 mass
    ax.plot(xs, ys, "k-d", mfc="white")
    for s, x, y in zip(speeds, xs, ys):
        ax.annotate(f"{s} kg/hr", (x, y), fontsize=6, xytext=(0, 5), textcoords="offset points")
    ax.set_xlabel("Robonauts"); ax.set_ylabel("Mass of Assets (Ton)")
    ax.set_title("Fig. 11 (repro): Gen-6 mass vs robonauts by printer speed")
    _save(fig, "fig11_mass_vs_robonauts.png")


# --------------------------------------------------------------------------
def fig12_13_14():
    cases = [("Fast Robonauts", 1 / 3.0, "ko:"), ("Nominal Robonauts", 1.0, "ks-"),
             ("Slow Robonauts", 3.0, "k^--")]
    results = {lab: solve(Config(rwpa_mult=m)) for lab, m, _ in cases}

    # Fig 12: robonauts per generation
    fig, ax = plt.subplots(figsize=(6, 4.2))
    for lab, m, fmt in cases:
        r = results[lab]
        ax.plot(GENS, [r[g].X for g in GENS], fmt, mfc="white", label=lab)
    ax.set_yscale("log"); ax.set_ylim(1, 1e5)
    ax.set_xlabel("Generation"); ax.set_ylabel("Number of Robonauts")
    ax.legend(fontsize=7); ax.set_title("Fig. 12 (repro): Robonauts by productivity")
    _save(fig, "fig12_rwpa_robonauts.png")

    # Fig 13: asset mass per generation
    fig, ax = plt.subplots(figsize=(6, 4.2))
    for lab, m, fmt in cases:
        r = results[lab]
        ax.plot(GENS, [r[g].asset_mass_kg / MT for g in GENS], fmt, mfc="white", label=lab)
    ax.set_yscale("log"); ax.set_ylim(1, 1e5)
    ax.set_xlabel("Generation"); ax.set_ylabel("Mass of Assets (ton)")
    ax.legend(fontsize=7); ax.set_title("Fig. 13 (repro): Asset mass by robonaut productivity")
    _save(fig, "fig13_rwpa_mass.png")

    # Fig 14: launch mass per generation
    fig, ax = plt.subplots(figsize=(6, 4.2))
    for lab, m, fmt in cases:
        r = results[lab]
        ax.plot(GENS, [r[g].launch_kg / MT for g in GENS], fmt, mfc="white", label=lab)
    ax.set_yscale("log"); ax.set_ylim(1, 100)
    ax.set_xlabel("Generation (space in 2 year intervals)"); ax.set_ylabel("Mass (tonne)")
    ax.legend(fontsize=7); ax.set_title("Fig. 14 (repro): Launch mass by robonaut productivity")
    _save(fig, "fig14_rwpa_launch.png")


ALL = {2: fig2, 3: fig3, 4: fig4, 5: fig5, 6: fig6, 7: fig7, 8: fig8,
       9: fig9_10_11, 10: fig9_10_11, 11: fig9_10_11,
       12: fig12_13_14, 13: fig12_13_14, 14: fig12_13_14}


if __name__ == "__main__":
    if len(sys.argv) > 1:
        done = set()
        for a in sys.argv[1:]:
            fn = ALL[int(a)]
            if fn not in done:
                fn(); done.add(fn)
    else:
        for fn in [fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9_10_11, fig12_13_14]:
            fn()
