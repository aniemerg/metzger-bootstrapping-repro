"""Baseline parameters for the lunar-industry bootstrapping model.

All values transcribed from Metzger et al., Tables 1 & 2, and the Fig. 1 inset.
Interpretation choices are documented in ASSUMPTIONS.md (referenced as A#).
"""

# --------------------------------------------------------------------------
# Generation sequence (the evolutionary spiral)
# --------------------------------------------------------------------------
GENERATIONS = [1.0, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0]

# --------------------------------------------------------------------------
# Table 2: one basic set = 21 assets (Gen 1.0 baseline).
# Each asset: (name, qty, mass_minus_electronics_kg, electronics_kg,
#              power_kW, feed_kg_hr, product_kg_hr)
# --------------------------------------------------------------------------
ASSETS = [
    # name                   qty  mass-elec  elec  power  feed  product
    ("Power Distrib & Backup", 1,   2000.0,   0.0,  0.00,  0.0,  0.0),
    ("Excavators (swarming)",  5,     70.0,  19.0,  0.30, 20.0,  0.0),
    ("Chem Plant 1 - Gases",   1,    733.0,  30.0,  5.58,  4.0,  1.8),
    ("Chem Plant 2 - Solids",  1,    733.0,  30.0,  5.58, 10.0,  1.0),
    ("Metals Refinery",        1,   1019.0,  19.0, 10.00, 20.0,  3.15),
    ("Solar Cell Manufacturer",1,    169.0,  19.0,  0.50,  0.3,  0.0),
    ("3D Printer 1 - Small",   4,    169.0,  19.0,  5.00,  0.5,  0.5),
    ("3D Printer 2 - Large",   4,    300.0,  19.0,  5.00,  0.5,  0.5),
    ("Robonaut assemblers",    3,    135.0,  15.0,  0.40,  0.0,  0.0),
]

# Number of distinct asset units per basic set (the "21" in the flow diagram).
ASSETS_PER_SET = sum(qty for _, qty, *_ in ASSETS)  # == 21

# Structural mass (minus electronics) of one basic set [kg]  (A2)
M_SET_STRUCT = sum(qty * m for _, qty, m, *_ in ASSETS)
# Electronics mass of one basic set [kg]
E_SET = sum(qty * e for _, qty, _m, e, *_ in ASSETS)
# Total mass of one basic set [kg]  (~7.7 MT, matches Table 2)
M_SET_TOTAL = M_SET_STRUCT + E_SET

# Per-printer product rate at the Table 2 baseline [kg/hr] and printers per set.
PRINTERS_PER_SET = 8           # 4 small + 4 large
PRINTER_SPEED_TABLE2 = 0.5     # kg/hr per printer (Table 2 -> 8*0.5 = 4 kg/hr)
# Fig. 2 "maximum manufacturing" growth case explicitly uses 0.5 kg/hr/printer
# ("The manufacturing rate is assumed to be 0.5 kg/hr for each additive
# manufacturing unit ... to reproduce hardware as quickly as possible"). (A3)
PRINTER_SPEED_BASELINE = 0.5   # kg/hr per printer

# Single robonaut: structural mass, electronics mass [kg]  (A1/A6)
M_ROBONAUT_STRUCT = 135.0
E_ROBONAUT = 15.0
M_ROBONAUT_TOTAL = M_ROBONAUT_STRUCT + E_ROBONAUT

# Single electronics-maker asset: assume same envelope as a metals/printer-class
# unit. The paper does not give a separate line item; we model it with a
# printer-class mass and a calibrated throughput (A7).
M_ELECMAKER_STRUCT = 300.0
E_ELECMAKER = 19.0
M_ELECMAKER_TOTAL = M_ELECMAKER_STRUCT + E_ELECMAKER

# --------------------------------------------------------------------------
# Per-generation factors
# --------------------------------------------------------------------------
# Crudeness factor: mass multiplier of that generation's hardware (A4)
CRUDENESS = {1.0: 1.0, 2.0: 2.5, 2.5: 2.5, 3.0: 1.5, 4.0: 1.0, 5.0: 1.0, 6.0: 1.0}

# Electronics closure fraction F made locally (A5)
CLOSURE_F = {1.0: 0.0, 2.0: 0.0, 2.5: 0.0, 3.0: 0.90, 4.0: 0.95, 5.0: 0.99, 6.0: 1.00}

# Robonaut Weeks Per Asset, in generation order (A6)
RWPA = {1.0: 4, 2.0: 4, 2.5: 6, 3.0: 7, 4.0: 7, 5.0: 8, 6.0: 8}

# Generations <= this import robonauts from Earth instead of fabricating them.
ROBONAUT_IMPORT_THROUGH = 2.5

# --------------------------------------------------------------------------
# Timing, power, calibration
# --------------------------------------------------------------------------
GEN_YEARS_BASELINE = 2.0
HOURS_PER_YEAR = 24 * 365            # 8760
WEEKS_PER_YEAR = 52.0
DUTY_CYCLE_BASELINE = 0.70           # (A9)

# THE single calibrated unknown: electronics-maker output [kg/hr] (A7).
# Frozen after calibration against Fig. 3 / Fig. 4.
ELEC_THROUGHPUT_KG_PER_HR = 0.2  # calibrated vs Fig.2 Gen-6 mass; then frozen

# Set-asides subtracted from a generation's structural output [kg] (A12)
SET_ASIDES_KG = {3.0: 80_000.0, 4.0: 10_000.0, 5.0: 120_000.0}

# Unit conversions
KG_PER_TON = 1000.0


def gen_hours(gen_years=GEN_YEARS_BASELINE):
    """Hours in one generation."""
    return gen_years * HOURS_PER_YEAR


def weeks_per_gen(gen_years=GEN_YEARS_BASELINE):
    """Robonaut work-weeks available per robonaut in one generation."""
    return gen_years * WEEKS_PER_YEAR


def next_gen(gen):
    """Return the generation after `gen`, or None if it is the last."""
    i = GENERATIONS.index(gen)
    return GENERATIONS[i + 1] if i + 1 < len(GENERATIONS) else None


def prev_gen(gen):
    """Return the generation before `gen`, or None if it is the first."""
    i = GENERATIONS.index(gen)
    return GENERATIONS[i - 1] if i > 0 else None


if __name__ == "__main__":
    print(f"Assets per set : {ASSETS_PER_SET}")
    print(f"Struct mass/set: {M_SET_STRUCT:,.0f} kg")
    print(f"Elec mass/set  : {E_SET:,.0f} kg")
    print(f"Total mass/set : {M_SET_TOTAL:,.0f} kg  (~{M_SET_TOTAL/KG_PER_TON:.1f} MT)")
