"""Bootstrapping model engine: per-generation calculation + fixed-point iterator.

Implements the recursion of Metzger et al. Fig. 1. See ASSUMPTIONS.md for the
interpretation choices (A1-A12) behind every term.

Notation (per generation N):
  Z_N : number of basic sets present (Z_{N+1} = W_N, forward coupling)
  W_N : number of basic sets that gen N fabricates (for gen N+1)
  X_N : number of robonauts gen N needs for assembly labor
  Y_N : number of electronics-maker assets gen N needs
  U_N : robonauts gen N must produce for N+1   == X_{N+1} (backward coupling)
  V_N : elec-makers gen N must produce for N+1 == Y_{N+1} (backward coupling)
"""

from dataclasses import dataclass, field
import parameters as P


@dataclass
class Config:
    """A single scenario's knobs. Defaults = paper baseline."""
    printer_speed: float = P.PRINTER_SPEED_BASELINE      # kg/hr per printer
    duty_cycle: float = P.DUTY_CYCLE_BASELINE
    gen_years: float = P.GEN_YEARS_BASELINE
    utilization: float = 1.0          # 0.5 == "reduced manufacturing" (A8)
    rwpa_mult: float = 1.0            # x1/3 faster, x3 slower robonauts (A6)
    closure_override: dict = None     # override CLOSURE_F (for Fig.4 variants)
    elec_throughput: float = P.ELEC_THROUGHPUT_KG_PER_HR

    def F(self, gen):
        if self.closure_override is not None:
            return self.closure_override.get(gen, P.CLOSURE_F[gen])
        return P.CLOSURE_F[gen]


@dataclass
class GenResult:
    gen: float
    Z: float = 0.0   # sets present
    W: float = 0.0   # sets fabricated for next gen
    X: float = 0.0   # robonauts (assembly labor)
    Y: float = 0.0   # electronics makers
    U: float = 0.0   # robonauts produced for next gen
    V: float = 0.0   # elec makers produced for next gen
    asset_mass_kg: float = 0.0      # total hardware mass present this gen
    struct_mass_kg: float = 0.0     # structural (solids+metals) mass present
    elec_mass_kg: float = 0.0       # electronics mass present
    fluids_kg: float = 0.0          # fluids produced over the generation
    solids_kg: float = 0.0          # solids (plastics/rubber + metals) produced
    power_avail_kW: float = 0.0
    power_need_kW: float = 0.0
    launch_kg: float = 0.0


def _robo_imported(gen):
    """Robonauts of/produced-by this producing generation are imported."""
    return gen <= P.ROBONAUT_IMPORT_THROUGH


def solve(cfg: Config, n_iter=500, damping=0.5):
    """Run the fixed-point iteration over all generations; return dict gen->GenResult."""
    gens = P.GENERATIONS
    Z = {g: 0.0 for g in gens}
    X = {g: 0.0 for g in gens}
    Y = {g: 0.0 for g in gens}
    W = {g: 0.0 for g in gens}
    Z[gens[0]] = 1.0  # one Earth-built seed set

    T = P.gen_hours(cfg.gen_years)
    weeks_avail = P.weeks_per_gen(cfg.gen_years) * cfg.duty_cycle
    eff_speed = cfg.printer_speed * cfg.utilization

    for _ in range(n_iter):
        Znew, Xnew, Ynew, Wnew = dict(Z), dict(X), dict(Y), dict(W)

        # ---- Forward pass: each producing gen N fabricates W_N sets ----
        for i, N in enumerate(gens):
            nxt = P.next_gen(N)
            # production target generation (for crudeness): next gen, or self at closure
            cf = P.CRUDENESS[nxt] if nxt is not None else 1.0
            F = cfg.F(N)

            # backward inputs: robonauts/elec-makers N must build for N+1
            if nxt is not None:
                U = X[nxt]
                V = Y[nxt]
            else:  # terminal generation: closure relation U = X*W/Z, V = Y*W/Z
                U = X[N] * (W[N] / Z[N]) if Z[N] > 0 else 0.0
                V = Y[N] * (W[N] / Z[N]) if Z[N] > 0 else 0.0

            imp = _robo_imported(N)  # imported robonauts not printed/assembled locally

            # gross printing capacity this generation [kg]
            Pcap = Z[N] * P.PRINTERS_PER_SET * eff_speed * cfg.duty_cycle * T
            setaside = P.SET_ASIDES_KG.get(N, 0.0)

            # Solve the linear mass-balance for W (basic sets):
            #   Pcap - setaside = cf*m_set_s*W + F*e_set*W
            #                   + (cf*m_robo_s + F*e_robo)*U_eff
            #                   + (cf*m_elec_s + F*e_elec)*V
            U_eff = 0.0 if imp else U
            robo_cost = (cf * P.M_ROBONAUT_STRUCT + F * P.E_ROBONAUT) * U_eff
            elec_cost = (cf * P.M_ELECMAKER_STRUCT + F * P.E_ELECMAKER) * V
            denom = cf * P.M_SET_STRUCT + F * P.E_SET
            w = (Pcap - setaside - robo_cost - elec_cost) / denom
            w = max(w, 0.0)
            Wnew[N] = w
            if nxt is not None:
                Znew[nxt] = w

        # ---- Local pass: robonaut labor X and elec-maker count Y ----
        for N in gens:
            nxt = P.next_gen(N)
            if nxt is not None:
                U, V = X[nxt], Y[nxt]
            else:
                U = X[N] * (Wnew[N] / Z[N]) if Z[N] > 0 else 0.0
                V = Y[N] * (Wnew[N] / Z[N]) if Z[N] > 0 else 0.0
            imp = _robo_imported(N)
            F = cfg.F(N)

            # assets that gen N must assemble (imported robonauts need no assembly)
            assets = 21.0 * Wnew[N] + V + (0.0 if imp else U)
            rwpa = P.RWPA[N] * cfg.rwpa_mult
            Xnew[N] = assets * rwpa / weeks_avail if weeks_avail > 0 else 0.0

            # electronics gen N makes locally = F * electronics mass produced
            e_robo = 0.0 if imp else P.E_ROBONAUT * U
            E_total = P.E_SET * Wnew[N] + P.E_ELECMAKER * V + e_robo
            elec_to_make = F * E_total
            cap = cfg.elec_throughput * cfg.duty_cycle * T
            Ynew[N] = elec_to_make / cap if cap > 0 else 0.0

        # ---- convergence check + damping ----
        def merge(old, new):
            return {g: old[g] + damping * (new[g] - old[g]) for g in gens}
        Z2, X2, Y2, W2 = merge(Z, Znew), merge(X, Xnew), merge(Y, Ynew), merge(W, Wnew)
        Z2[gens[0]] = 1.0
        delta = max(abs(X2[g] - X[g]) for g in gens) + max(abs(W2[g] - W[g]) for g in gens)
        Z, X, Y, W = Z2, X2, Y2, W2
        if delta < 1e-9:
            break

    return _assemble_results(cfg, Z, X, Y, W)


def _assemble_results(cfg, Z, X, Y, W):
    """Turn converged state into per-generation reported quantities."""
    res = {}
    T = P.gen_hours(cfg.gen_years)
    eff_speed = cfg.printer_speed * cfg.utilization
    for N in P.GENERATIONS:
        cf = P.CRUDENESS[N]
        imp = _robo_imported(N)
        r = GenResult(gen=N, Z=Z[N], W=W[N], X=X[N], Y=Y[N])
        r.U = X[P.next_gen(N)] if P.next_gen(N) else 0.0
        r.V = Y[P.next_gen(N)] if P.next_gen(N) else 0.0

        # mass present this generation (A10): sets + robonauts + elec makers
        struct = cf * (Z[N] * P.M_SET_STRUCT + X[N] * P.M_ROBONAUT_STRUCT
                       + Y[N] * P.M_ELECMAKER_STRUCT)
        elec = (Z[N] * P.E_SET + X[N] * P.E_ROBONAUT + Y[N] * P.E_ELECMAKER)
        r.struct_mass_kg = struct
        r.elec_mass_kg = elec
        r.asset_mass_kg = struct + elec

        # production over the generation (for Fig. 3): split solids vs fluids
        # by the basic set's product mix (chem gases=fluids; solids+metals).
        prod_total = Z[N] * P.PRINTERS_PER_SET * eff_speed * cfg.duty_cycle * T
        # one set's hourly outputs: gases(fluids)=1.8, solids(chem2)=1.0, metals=3.15
        fluids_frac = 1.8 / (1.8 + 1.0 + 3.15)
        r.fluids_kg = prod_total * fluids_frac
        r.solids_kg = prod_total * (1 - fluids_frac)

        # power available vs needed (A: solar scaled to exceed need) (Fig. 5)
        power_per_set = sum(q * pw for _, q, _m, _e, pw, *_ in P.ASSETS)  # 64.36 kW
        r.power_need_kW = Z[N] * power_per_set
        r.power_avail_kW = r.power_need_kW * 8.0  # paper: avail >> need

        # launch mass (A11)
        if N == P.GENERATIONS[0]:
            r.launch_kg = P.M_SET_TOTAL  # full seed
        else:
            prev = P.prev_gen(N)
            Fprev = cfg.F(prev)
            E_here = (Z[N] * P.E_SET + Y[N] * P.E_ELECMAKER
                      + (0.0 if imp else X[N] * P.E_ROBONAUT))
            imported_elec = (1.0 - Fprev) * E_here
            imported_robo = X[N] * P.M_ROBONAUT_TOTAL if imp else 0.0
            r.launch_kg = imported_elec + imported_robo
        res[N] = r
    return res


if __name__ == "__main__":
    r = solve(Config())
    print(f"{'Gen':>5} {'Sets Z':>10} {'Robonauts':>12} {'ElecMkr':>10} "
          f"{'Mass(MT)':>12} {'Launch(MT)':>12}")
    for g in P.GENERATIONS:
        x = r[g]
        print(f"{g:>5} {x.Z:>10.2f} {x.X:>12.1f} {x.Y:>10.2f} "
              f"{x.asset_mass_kg/1000:>12.1f} {x.launch_kg/1000:>12.2f}")
