"""The sweeper: enumerate decomposition configurations per target, cost them.

For a target group (q, n, CM data, declared extension-field endomorphisms)
the sweep

1. certifies the CM discriminant class (``small_discriminant_scan``);
2. builds the catalogue of cheap endomorphisms: units, small-norm elements,
   isogeny-cycle "pumps" (powers of the generator of the first principal
   power of a split prime), and declared Frobenius-type maps;
3. enumerates generator sets (GLV pairs, unit x pump boxes, Frobenius
   monomial boxes), LLL-reduces each relation lattice EXACTLY, and measures
   the provable and empirical coefficient size;
4. costs every configuration with one operation-count model and ranks them;
5. labels each configuration with the literature construction it reproduces,
   or "no literature match" when the sweep has none.

Nothing here claims a speed-up: a cost-model ranking is a hypothesis
generator, and any configuration that beats a known construction on paper
is a candidate for an explicit implementation and a measured experiment.
"""
from __future__ import annotations

import itertools
import json
import time
from dataclasses import asdict, dataclass, field
from math import log2

from . import costmodel as CM
from . import lattice as LA
from . import quadorder as QO
from .targets import Target


SMALL_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47)


@dataclass
class SweepOptions:
    disc_bound: int = 2_000_000       # certify |D_K| > bound by exact scan
    small_norm_max: int = 64          # single-isogeny GLV candidates up to this degree
    pump_primes: tuple[int, ...] = SMALL_PRIMES
    pump_height_steps: tuple[int, ...] = (-1, 0, 1)   # j around the n^(1/4) target
    max_dim: int = 8
    lattice_samples: int = 32
    affine_tables: bool = True


@dataclass
class ConfigResult:
    label: str
    generators: list[str]
    dim: int
    coeff_bits_bound: int
    coeff_bits_empirical: int
    balanced_bits: float
    basis_inf_norm_bits: list[int]
    cost_M: float
    cost_breakdown: dict
    known_as: str
    endomorphism_cost_M: float
    speedup_vs_generic: float = 1.0
    note: str = ""


@dataclass
class TargetResult:
    name: str
    family: str
    verified: bool
    verification: str
    q_bits: int
    n_bits: int
    ext_degree: int
    cost_model: str
    frobenius_discriminant_bits: int
    discriminant_certificate: str
    cm_discriminant: int | None
    class_number: int | None
    min_nonscalar_degree: int | None
    cheap_endomorphisms: list[dict]
    pumps: list[dict]
    configs: list[ConfigResult]
    best: str
    best_cost_M: float
    generic_cost_M: float
    conclusion: str
    elapsed_s: float


# ---------------------------------------------------------------------------
# catalogue
# ---------------------------------------------------------------------------

def _class_number(D: int) -> int | None:
    """h(D) by counting reduced forms (small |D| only)."""
    if -D > 10**7:
        return None
    count = 0
    absD = -D
    a = 1
    while 3 * a * a <= absD:
        for b in range(-a + 1, a + 1):
            if (b * b - D) % (4 * a):
                continue
            c = (b * b - D) // (4 * a)
            if c < a:
                continue
            if c == a and b < 0:
                continue
            from math import gcd
            if gcd(gcd(a, abs(b)), c) != 1:
                continue
            count += 1
        a += 1
    return count


def _unit_generator(D: int, lam_omega: int, n: int) -> CM.Generator | None:
    if D == -3:
        # omega = zeta_6; use zeta_3 = omega - 1 (same lattice, conventional name)
        return CM.Generator("zeta_3", (lam_omega - 1) % n, CM.ENDOMORPHISM_COSTS["unit"]["M"],
                            "unit", degree=1, height=1,
                            detail={"relation": "zeta^2 + zeta + 1 = 0"})
    if D == -4:
        return CM.Generator("i", lam_omega % n, CM.ENDOMORPHISM_COSTS["unit"]["M"],
                            "unit", degree=1, height=1, detail={"relation": "i^2 + 1 = 0"})
    return None


def _isogeny_cost(degree: int) -> float:
    """One cyclic separable endomorphism of the given degree, as a single Velu map."""
    try:
        return CM.isogeny_step_cost(degree) + CM.ISOGENY_CHAIN_OVERHEAD_M
    except ValueError:
        # composite even degree: Velu-style, ~4(ell-1) M + overhead (assumption)
        return 4.0 * (degree - 1) + CM.ISOGENY_CHAIN_OVERHEAD_M


def build_catalogue(T: Target, D: int | None, lam_omega: int | None, opts: SweepOptions):
    n = T.n
    gens: dict[str, CM.Generator] = {}
    cheap: list[dict] = []
    pumps: list[dict] = []
    if D is not None and lam_omega is not None:
        u = _unit_generator(D, lam_omega, n)
        if u is not None:
            gens["unit"] = u
            cheap.append({"name": u.name, "degree": 1, "height": 1, "cost_M": u.cost_M,
                          "kind": "unit"})
        # small-norm single endomorphisms
        for N in range(2, opts.small_norm_max + 1):
            for el in QO.elements_of_norm(D, N, primitive_only=True):
                g = CM.Generator(f"endo[{el.a}+{el.b}w] deg {N}", el.eigenvalue(lam_omega, n),
                                 _isogeny_cost(N), "isogeny", degree=N, height=el.height,
                                 detail={"a": el.a, "b": el.b})
                gens[f"iso{N}:{el.a},{el.b}"] = g
                cheap.append({"name": g.name, "degree": N, "height": el.height,
                              "cost_M": g.cost_M, "kind": "isogeny", "a": el.a, "b": el.b})
        # isogeny-cycle pumps: for each split prime, the first principal power
        for ell in opts.pump_primes:
            if QO.kronecker_symbol_disc(D, ell) != 1:
                continue
            beta = QO.smallest_principal_power(D, ell, kmax=64)
            if beta is None:
                continue
            k = round(log2(beta.norm) / log2(ell))
            per_bit = CM.pump_cost_per_height_bit(ell)
            pumps.append({"ell": ell, "cycle_length": k, "generator": f"{beta.a}+{beta.b}w",
                          "norm": beta.norm, "height": beta.height,
                          "step_cost_M": CM.isogeny_step_cost(ell),
                          "cost_per_height_bit_M": per_bit,
                          "beta": beta})
    # declared extension-field generators
    for dg in T.declared_generators:
        cost = CM.ENDOMORPHISM_COSTS[dg["cost_key"]]["M"]
        g = CM.Generator(dg["name"], dg["eigenvalue"] % n, cost, dg["kind"],
                         detail={"order_mod_n": dg.get("order_mod_n")})
        gens[f"declared:{dg['name']}"] = g
        cheap.append({"name": g.name, "degree": None, "height": None, "cost_M": cost,
                      "kind": dg["kind"], "order_mod_n": dg.get("order_mod_n")})
    return gens, cheap, pumps


# ---------------------------------------------------------------------------
# configurations
# ---------------------------------------------------------------------------

def _identity(n: int) -> CM.Generator:
    return CM.Generator("1", 1, 0.0, "identity")


def _product(a: CM.Generator, b: CM.Generator, n: int) -> CM.Generator:
    """a*b as a generator.  Cost is INCREMENTAL: every box that uses a*b also
    contains a and b, so a*b(P) costs one more application of the cheaper factor."""
    return CM.Generator(f"{a.name}*{b.name}", a.eigenvalue * b.eigenvalue % n,
                        min(a.cost_M, b.cost_M), "product",
                        degree=a.degree * b.degree, height=a.height * b.height)


def _power(g: CM.Generator, e: int, n: int) -> CM.Generator:
    """g^e as a generator; incremental cost (g^(e-1) is always in the same box)."""
    if e == 0:
        return _identity(n)
    if e == 1:
        return g
    return CM.Generator(f"{g.name}^{e}", pow(g.eigenvalue, e, n), g.cost_M, "product",
                        degree=g.degree ** e, height=g.height ** e)


def _pump_generator(D: int, pump: dict, j: int, lam_omega: int, n: int) -> CM.Generator:
    beta: QO.RingElement = pump["beta"]
    a, b = QO.power(D, (beta.a, beta.b), j)
    el = QO.RingElement(D, a, b)
    steps = j * pump["cycle_length"]
    return CM.Generator(f"cycle[{pump['ell']}^{steps}]", el.eigenvalue(lam_omega, n),
                        CM.cycle_pump_cost(pump["ell"], steps), "cycle",
                        degree=pump["ell"] ** steps, height=el.height,
                        detail={"ell": pump["ell"], "steps": steps, "a": a, "b": b})


def enumerate_configurations(T: Target, D, lam_omega, gens, pumps, opts: SweepOptions):
    n = T.n
    one = _identity(n)
    configs: list[tuple[str, list[CM.Generator], str]] = []
    configs.append(("generic", [one], "double-and-add / wNAF (no endomorphism)"))
    unit = gens.get("unit")
    # 2-dim: identity + any single cheap endomorphism
    for key, g in gens.items():
        if g.kind == "unit":
            configs.append((f"GLV-2 [{g.name}]", [one, g], "GLV 2001 (Gallant-Lambert-Vanstone), unit automorphism"))
        elif g.kind == "isogeny":
            configs.append((f"GLV-2 [{g.name}]", [one, g],
                            "GLV 2001 with a degree-N endomorphism (cf. Guillevic-Masson-Thome 2020 for N up to the hundreds)"))
        elif g.kind == "frobenius":
            configs.append((f"2-dim [{g.name}]", [one, g], "GLS 2009 (Galbraith-Lin-Scott) / Galbraith-Scott 2008 G2"))
    # paid pumps: unit x pump boxes and two-pump boxes
    if D is not None and pumps:
        target_bits = (n.bit_length() - 1) / 4
        for pump in pumps:
            bits_per_power = pump["cycle_length"] * log2(pump["ell"]) / 2
            j0 = max(1, round(target_bits / bits_per_power))
            for dj in opts.pump_height_steps:
                j = j0 + dj
                if j < 1:
                    continue
                alpha = _pump_generator(D, pump, j, lam_omega, n)
                if unit is not None:
                    configs.append((f"pump-4 [{unit.name} x {alpha.name}]",
                                    [one, unit, alpha, _product(unit, alpha, n)],
                                    "no literature match found: unit x isogeny-cycle box (this sweep)"))
                    if opts.max_dim >= 6:
                        a2 = _power(alpha, 2, n)
                        configs.append((f"pump-6 [{unit.name} x {alpha.name}^(0..2)]",
                                        [one, unit, alpha, _product(unit, alpha, n), a2, _product(unit, a2, n)],
                                        "no literature match found: unit x cycle powers (this sweep)"))
                else:
                    configs.append((f"pump-2 [{alpha.name}]", [one, alpha],
                                    "GLV 2001 with a cycle endomorphism (degree ell^k)"))
                    # no unit: the cheapest small-degree endomorphism plays the
                    # role of the free generator in a {1, g, alpha, g*alpha} box
                    cheap_iso = sorted((g for g in gens.values() if g.kind == "isogeny"),
                                       key=lambda g: g.cost_M)
                    if cheap_iso and dj == 0:
                        g0 = cheap_iso[0]
                        configs.append((f"pump-4 [{g0.name} x {alpha.name}]",
                                        [one, g0, alpha, _product(g0, alpha, n)],
                                        "no literature match found: small-degree endomorphism x isogeny-cycle box (this sweep)"))
        # two different pumps, no unit needed
        if len(pumps) >= 2:
            for pa, pb in itertools.combinations(pumps[:4], 2):
                ha = pa["cycle_length"] * log2(pa["ell"]) / 2
                hb = pb["cycle_length"] * log2(pb["ell"]) / 2
                ja = max(1, round(target_bits / 2 / ha))
                jb = max(1, round(target_bits / 2 / hb))
                A = _pump_generator(D, pa, ja, lam_omega, n)
                B = _pump_generator(D, pb, jb, lam_omega, n)
                configs.append((f"pump-4 [{A.name} x {B.name}]", [one, A, B, _product(A, B, n)],
                                "no literature match found: two-cycle box (this sweep)"))
                if unit is not None:
                    configs.append((f"pump-8 [{unit.name} x {A.name} x {B.name}]",
                                    [one, unit, A, _product(unit, A, n), B, _product(unit, B, n),
                                     _product(A, B, n), _product(unit, _product(A, B, n), n)],
                                    "no literature match found: unit x two-cycle box (this sweep)"))
    # declared Frobenius-type generators: monomial boxes
    frob = [g for g in gens.values() if g.kind == "frobenius"]
    units_decl = [g for g in gens.values() if g.kind == "unit" and g is not unit] + ([unit] if unit else [])
    for f in frob:
        order = f.detail.get("order_mod_n") or 2
        for d in range(2, min(order, opts.max_dim) + 1):
            gl = [_power(f, i, n) for i in range(d)]
            known = ("Galbraith-Scott 2008 (G2 of pairing curves, psi^i basis)" if "G2" in T.name or "untwist" in f.name
                     else "GLS 2009 (Galbraith-Lin-Scott)" if d == 2 else "Frobenius-power basis (Kobayashi et al. 1999 / GLS 2009 F_{p^m})")
            configs.append((f"frob-{d} [{f.name}^(0..{d-1})]", gl, known))
        for u in units_decl:
            for d in range(2, min(order, opts.max_dim // 2) + 1):
                gl = []
                for i in range(d):
                    fi = _power(f, i, n)
                    gl.append(fi)
                    gl.append(_product(u, fi, n) if i else u)
                known = ("Longa-Sica 2012 4-GLV (GLV x GLS)" if d == 2
                         else "unit x Frobenius-power box")
                configs.append((f"frob-{2*d} [{u.name} x {f.name}^(0..{d-1})]", gl, known))
    # de-duplicate by eigenvalue multiset and cap dimension
    seen = set()
    out = []
    for label, gl, known in configs:
        if len(gl) > opts.max_dim:
            continue
        key = tuple(sorted(g.eigenvalue for g in gl))
        if key in seen:
            continue
        seen.add(key)
        out.append((label, gl, known))
    return out


# ---------------------------------------------------------------------------
# evaluation
# ---------------------------------------------------------------------------

def evaluate(label: str, gl: list[CM.Generator], known: str, T: Target, opts: SweepOptions) -> ConfigResult:
    n = T.n
    lams = [g.eigenvalue for g in gl]
    if len(set(lams)) != len(lams):
        raise ValueError(f"{label}: repeated eigenvalue")
    red = LA.reduce(lams, n)
    cb = LA.coefficient_bits(red, samples=opts.lattice_samples)
    bits = cb["empirical_max_bits"]
    cost = CM.multiscalar_cost(bits, gl, T.cost_model, affine_tables=opts.affine_tables)
    endo = sum(g.cost_M for g in gl)
    return ConfigResult(
        label=label, generators=[g.name for g in gl], dim=len(gl),
        coeff_bits_bound=cb["bound_bits"], coeff_bits_empirical=bits,
        balanced_bits=cb["balanced_bits"], basis_inf_norm_bits=cb["basis_inf_norm_bits"],
        cost_M=cost.total_M,
        cost_breakdown={"doublings": cost.doublings, "additions": round(cost.additions, 1),
                        "precomp_M": round(cost.precomp_M, 1), "endomorphism_M": round(cost.endomorphism_M, 1),
                        "window": cost.window, "DBL_M": cost.breakdown["DBL"],
                        "loop_add_M": cost.breakdown["loop_add"]},
        known_as=known, endomorphism_cost_M=endo)


def sweep_target(T: Target, opts: SweepOptions | None = None) -> TargetResult:
    opts = opts or SweepOptions()
    t0 = time.time()
    n = T.n
    Dfrob = QO.frobenius_discriminant(T.q, T.trace) if T.h else None
    D = None
    cert = ""
    hcl = None
    mindeg = None
    lam_omega = None
    if T.model == "structural" and "D" in T.coeffs:
        D = T.coeffs["D"]
        cert = f"declared CM discriminant {D} (synthetic CM construction)"
    elif Dfrob is not None and Dfrob < 0:
        scan = QO.small_discriminant_scan(Dfrob, opts.disc_bound)
        cert = scan.certificate
        D = scan.found
    else:
        cert = "cofactor not declared: Frobenius trace unknown, CM class not determined here"
    if D is not None:
        hcl = _class_number(D)
        mindeg = QO.min_nonscalar_degree(D)
        roots = QO.omega_eigenvalues(D, n)
        lam_omega = roots[0] if roots else None
        if lam_omega is None:
            cert += "; omega has no eigenvalue mod n (CM field inert at n): no decomposition from CM"
            D = None
    gens, cheap, pumps = build_catalogue(T, D, lam_omega, opts)
    configs = enumerate_configurations(T, D, lam_omega, gens, pumps, opts)
    results: list[ConfigResult] = []
    for label, gl, known in configs:
        try:
            results.append(evaluate(label, gl, known, T, opts))
        except ValueError as e:
            results.append(ConfigResult(label, [g.name for g in gl], len(gl), 0, 0, 0.0, [], float("inf"),
                                        {}, known, 0.0, note=str(e)))
    generic = next(r for r in results if r.label == "generic")
    for r in results:
        r.speedup_vs_generic = generic.cost_M / r.cost_M if r.cost_M else 0.0
    results.sort(key=lambda r: r.cost_M)
    best = results[0]
    # conclusion text
    if D is None and Dfrob is not None and Dfrob < 0:
        concl = (f"No cheap endomorphism exists: {cert}. The only decomposition is the generic one "
                 f"unless the group is viewed over an extension field.")
    else:
        concl = (f"Best modelled configuration: {best.label} at {best.cost_M:.0f} M "
                 f"({best.speedup_vs_generic:.2f}x generic); literature: {best.known_as}.")
        pump_best = [r for r in results if r.label.startswith("pump")]
        if pump_best:
            pb = pump_best[0]
            base2 = [r for r in results if r.label.startswith("GLV-2") or r.label.startswith("2-dim")]
            ref = base2[0] if base2 else generic
            concl += (f" Best isogeny-cycle pump: {pb.label} at {pb.cost_M:.0f} M vs "
                      f"{ref.label} at {ref.cost_M:.0f} M ({'wins' if pb.cost_M < ref.cost_M else 'loses'} "
                      f"by {abs(pb.cost_M-ref.cost_M)/ref.cost_M*100:.1f}% under this cost model).")
    pumps_out = [{k: v for k, v in p.items() if k != "beta"} for p in pumps]
    return TargetResult(
        name=T.name, family=T.family, verified=bool(T.verified), verification=T.verification,
        q_bits=T.q.bit_length(), n_bits=n.bit_length(), ext_degree=T.ext_degree, cost_model=T.cost_model,
        frobenius_discriminant_bits=(abs(Dfrob).bit_length() if Dfrob is not None else 0),
        discriminant_certificate=cert, cm_discriminant=D, class_number=hcl,
        min_nonscalar_degree=mindeg, cheap_endomorphisms=cheap, pumps=pumps_out,
        configs=results, best=best.label, best_cost_M=best.cost_M, generic_cost_M=generic.cost_M,
        conclusion=concl, elapsed_s=time.time() - t0)


# ---------------------------------------------------------------------------
# reporting
# ---------------------------------------------------------------------------

def to_jsonable(res: TargetResult) -> dict:
    d = asdict(res)
    return d


def markdown_report(results: list[TargetResult], opts: SweepOptions) -> str:
    L: list[str] = []
    L.append("# Endomorphism-ring sweep: scalar-multiplication decompositions\n")
    L.append("Generated by `python -m harness.endosweep`. All costs are operation counts in base-field "
             "multiplications under the model in `costmodel.py` (S = %.1f M); nothing here is a timing. "
             "Coefficient sizes are from exact LLL reduction of the relation lattice; `bound` is the "
             "provable Babai bound and `emp` the maximum over %d random scalars.\n" % (CM.S_PER_M, opts.lattice_samples))
    L.append("## Summary\n")
    L.append("| target | family | n bits | CM disc | h | min non-scalar degree | best config | best M | generic M | speedup | literature |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in results:
        best = r.configs[0]
        L.append(f"| {r.name} | {r.family} | {r.n_bits} | "
                 f"{r.cm_discriminant if r.cm_discriminant is not None else f'|D_K| > {opts.disc_bound}' if r.frobenius_discriminant_bits else 'n/a'} | "
                 f"{r.class_number if r.class_number is not None else ''} | "
                 f"{r.min_nonscalar_degree if r.min_nonscalar_degree is not None else ('>= %d' % (opts.disc_bound // 4) if r.frobenius_discriminant_bits else '')} | "
                 f"{best.label} | {best.cost_M:.0f} | {r.generic_cost_M:.0f} | {best.speedup_vs_generic:.2f}x | {best.known_as} |")
    L.append("")
    for r in results:
        L.append(f"## {r.name}\n")
        L.append(f"- family: {r.family}; verified: {r.verified} ({r.verification})")
        L.append(f"- field: q = p^{r.ext_degree}, {r.q_bits} bits; subgroup order n: {r.n_bits} bits; cost model: `{r.cost_model}`")
        L.append(f"- discriminant certificate: {r.discriminant_certificate}")
        if r.cheap_endomorphisms:
            L.append("- cheap endomorphism catalogue (first 8): " + "; ".join(
                f"{c['name']} (deg {c['degree']}, H {c['height']}, {c['cost_M']:.0f} M)" if c.get('degree') else
                f"{c['name']} ({c['cost_M']:.0f} M, order {c.get('order_mod_n')} mod n)" for c in r.cheap_endomorphisms[:8]))
        if r.pumps:
            L.append("- isogeny-cycle pumps (split primes, first principal power): " + "; ".join(
                f"ell={p['ell']}: cycle length {p['cycle_length']}, generator {p['generator']} (norm {p['norm']}), "
                f"{p['cost_per_height_bit_M']:.1f} M per bit of height" for p in r.pumps))
        L.append(f"- **conclusion:** {r.conclusion}\n")
        L.append("| config | dim | coeff bits (bound/emp/ideal) | basis inf-norm bits | DBL | ADD | endo M | precomp M | total M | speedup | literature |")
        L.append("|---|---|---|---|---|---|---|---|---|---|---|")
        for c in r.configs[:14]:
            if c.cost_M == float("inf"):
                L.append(f"| {c.label} | {c.dim} | — | — | — | — | — | — | invalid: {c.note} | | |")
                continue
            cb = c.cost_breakdown
            L.append(f"| {c.label} | {c.dim} | {c.coeff_bits_bound}/{c.coeff_bits_empirical}/{c.balanced_bits:.1f} | "
                     f"{c.basis_inf_norm_bits} | {cb['doublings']} | {cb['additions']} | {cb['endomorphism_M']} | "
                     f"{cb['precomp_M']} | {c.cost_M:.0f} | {c.speedup_vs_generic:.2f}x | {c.known_as} |")
        L.append("")
    return "\n".join(L)


def run_sweep(targets: list[Target], opts: SweepOptions | None = None) -> list[TargetResult]:
    opts = opts or SweepOptions()
    out = []
    for T in targets:
        if not T.verified:
            continue
        out.append(sweep_target(T, opts))
    return out


def main(argv=None) -> int:
    import argparse
    from .targets import all_targets
    ap = argparse.ArgumentParser(description="endomorphism-ring decomposition sweeper")
    ap.add_argument("--out-dir", default="outputs/endosweep")
    ap.add_argument("--targets", default="all", help="comma-separated substrings, or 'all'")
    ap.add_argument("--no-synthetic", action="store_true")
    ap.add_argument("--disc-bound", type=int, default=SweepOptions.disc_bound)
    ap.add_argument("--max-dim", type=int, default=SweepOptions.max_dim)
    ap.add_argument("--samples", type=int, default=SweepOptions.lattice_samples)
    ap.add_argument("--projective-tables", action="store_true", help="charge full additions, no affine tables")
    args = ap.parse_args(argv)
    opts = SweepOptions(disc_bound=args.disc_bound, max_dim=args.max_dim, lattice_samples=args.samples,
                        affine_tables=not args.projective_tables)
    T = all_targets(include_synthetic=not args.no_synthetic)
    if args.targets != "all":
        subs = [s.strip().lower() for s in args.targets.split(",")]
        T = [t for t in T if any(s in t.name.lower() for s in subs)]
    import os
    os.makedirs(args.out_dir, exist_ok=True)
    results = []
    for t in T:
        if not t.verified:
            print(f"[skip] {t.name}: {t.verification}")
            continue
        r = sweep_target(t, opts)
        results.append(r)
        print(f"[{r.elapsed_s:6.1f}s] {r.name:40s} best={r.best} {r.best_cost_M:.0f}M "
              f"generic={r.generic_cost_M:.0f}M ({r.configs[0].speedup_vs_generic:.2f}x)")
    with open(os.path.join(args.out_dir, "sweep.json"), "w") as f:
        json.dump({"options": asdict(opts), "results": [to_jsonable(r) for r in results]}, f, indent=1, default=str)
    with open(os.path.join(args.out_dir, "sweep.md"), "w") as f:
        f.write(markdown_report(results, opts))
    print(f"wrote {args.out_dir}/sweep.json and sweep.md")
    return 0
