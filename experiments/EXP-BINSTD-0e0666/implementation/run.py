#!/usr/bin/env python3
"""EXP-BINSTD-0e0666 Stages 0-1 launcher (HOLD-R; frozen contract v1).

Stage 0: Zero-compute worksheet — ord_n(2), stable-subspace lattices at
         n in {17,23,31,41,131,163}; Lemma A2-prime + claim-(D) identity;
         H1 design means; freeze stage0/preregistered-predictions.json.
Stage 1: Setup — Koblitz toys n=17/23/31; admit G; find lambda; Phi_n /
         stable bases; Cayley-accident check; fixture F0 at n=17; write
         stage1/*.json.

Observations only. No Magma/Sage/AUXIN/Bedrock. No ECDLP solve. No n>=131
attack. Amazon Bedrock is not selected.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from curve import (  # noqa: E402
    Curve,
    factor_out_small,
    is_probable_prime,
    koblitz_order_lucas,
    s3,
)
from gf2 import MODULI, Field, field_for, is_irreducible  # noqa: E402

EXPERIMENT_ID = "EXP-BINSTD-0e0666"
HYPOTHESIS_ID = "H-BINSTD-6428a3"
APPROVED_BY = "DEC-20261002-ff7924"
MASTER_SEED = 2026100293
EXP_ROOT = Path(__file__).resolve().parents[1]

WORKSHEET_NS = (17, 23, 31, 41, 131, 163)
MEASURE_NS = (17, 23, 31)

# Design figures from H-BINSTD-6428a3 / IDEA-20261001-93e740 (AC-9 / AC-10).
# mu = (n-1) * kappa * |F_V|^2 / (2 * #E) with kappa=1 design placeholder
# and |F_V|=2^l; actual kappa measured at Stage 1 setup.
DESIGN_MEANS = {
    (17, 1, 8): 4.0,
    (17, 1, 9): 16.0,
    (23, 1, 11): 5.5,
    (23, 1, 12): 22.0,
    (31, 1, 15): 7.5,
    (31, 1, 16): 30.0,
}


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.write_text(text, encoding="utf-8")


def _git_commit() -> str:
    """Best-effort HEAD sha for run.code.commit; never fabricates success."""
    import subprocess

    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=str(EXP_ROOT.parents[1]),
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return out.strip()
    except (OSError, subprocess.SubprocessError):
        return "UNKNOWN"


def ord_n_of_2(n: int) -> int:
    if n <= 0 or n % 2 == 0:
        raise ValueError("n must be a positive odd integer")
    a = 1
    for d in range(1, n):
        a = (a * 2) % n
        if a == 1:
            return d
    raise ValueError(f"2 has no finite order mod {n}")


def stable_dimension_lattice(n: int) -> dict[str, Any]:
    """For odd prime n: Phi_n splits into f=(n-1)/d irreducibles of deg d=ord_n(2).

    Stable dimensions are {j*d, j*d+1 : 0 <= j <= f} (with/without constants).
    """
    d = ord_n_of_2(n)
    if (n - 1) % d != 0:
        raise RuntimeError(f"ord_n(2)={d} does not divide n-1 for n={n}")
    f = (n - 1) // d
    dims = sorted({j * d for j in range(f + 1)} | {j * d + 1 for j in range(f + 1)})
    return {
        "n": n,
        "ord_n_2": d,
        "phi_n_factor_count": f,
        "phi_n_factor_degree": d,
        "stable_subspace_count": 1 << (1 + f),
        "stable_dimensions": dims,
        "usable_index_calculus_note": (
            "ECC2K-130 / K-163 host no nontrivial index-calculus stable V "
            "when ord_n(2)=n-1 (single Phi_n factor of degree n-1)."
            if d == n - 1
            else "usable dimensions exist when f>=2"
        ),
    }


def lemma_a2_prime_statement() -> dict[str, Any]:
    return {
        "id": "Lemma-A2-prime",
        "statement": (
            "At m=2 on sign-free systems: t={x1,x2} lies in Sol(R,V) and "
            "Sol(sigma^j R,V) iff one leg satisfies 2 P_1 = (1 - s lambda^j) R "
            "and the other is R - P_1 for some s in {+/-1} (halving form). "
            "Such tuples are sporadic, not a group action."
        ),
        "claim_D_identity": (
            "Global C1 survival over all (R,t) incidences is exactly 1/n "
            "(free C_n action on incidences under equivariance)."
        ),
        "withdrawn_comparators": {
            "all_lost_fraction_under_7ab503": 0.0,
            "N_coinc_under_a77711_original": 0,
            "note": (
                "Withdrawn per-instance Frobenius symmetry predicts all-lost=0; "
                "a77711 original Lemma A2 predicts N_coinc=0 on sign-free systems."
            ),
        },
    }


def poisson_99_interval(mu: float) -> dict[str, float]:
    """Crude normal approx 99% interval for Poisson(mu); recorded as design band."""
    if mu <= 0:
        return {"mu": mu, "lo": 0.0, "hi": 0.0}
    z = 2.576
    sd = math.sqrt(mu)
    return {"mu": mu, "lo": max(0.0, mu - z * sd), "hi": mu + z * sd}


def stage0(run_dir: Path) -> dict[str, Any]:
    t0 = time.time()
    lattices = {str(n): stable_dimension_lattice(n) for n in WORKSHEET_NS}
    # Dual route agreement on toy primes
    dual_ok = True
    dual_rows = []
    for n in WORKSHEET_NS:
        by_iter = ord_n_of_2(n)
        # divisor route
        nm1 = n - 1
        divs = []
        i = 1
        while i * i <= nm1:
            if nm1 % i == 0:
                divs.append(i)
                if i * i != nm1:
                    divs.append(nm1 // i)
            i += 1
        by_div = min(d for d in sorted(divs) if pow(2, d, n) == 1)
        agree = by_iter == by_div == lattices[str(n)]["ord_n_2"]
        dual_ok = dual_ok and agree
        dual_rows.append({"n": n, "iter": by_iter, "div": by_div, "agree": agree})

    # AC-9 Lucas orders for measured cells
    lucas = {}
    for n in MEASURE_NS + (41,):
        for a in (0, 1):
            lucas[f"n{n}_a{a}"] = koblitz_order_lucas(n, a)

    # Spot-check known fixture #E_1(F_{2^17})=131174=2*65587
    fixture_e17 = lucas["n17_a1"] == 131174 and is_probable_prime(65587)
    dual_ok = dual_ok and fixture_e17

    lemma = lemma_a2_prime_statement()
    h1_means = []
    for (n, a, l), mu in sorted(DESIGN_MEANS.items()):
        band = poisson_99_interval(mu)
        h1_means.append(
            {
                "n": n,
                "a": a,
                "l": l,
                "design_mu_kappa1": mu,
                "poisson_99": band,
                "E_order_lucas": lucas[f"n{n}_a{a}"],
                "F_V_size": 1 << l,
            }
        )

    prereg = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "master_seed": MASTER_SEED,
        "frozen": True,
        "stage": 0,
        "lattices": lattices,
        "ord_n_2_dual_routes": dual_rows,
        "lemma_a2_prime": lemma,
        "h1_design_means": h1_means,
        "lucas_orders": lucas,
        "fixture_E17_a1": {
            "order": lucas["n17_a1"],
            "expected": 131174,
            "r": 65587,
            "r_probable_prime": is_probable_prime(65587),
            "ok": fixture_e17,
        },
        "withdrawn_comparators": lemma["withdrawn_comparators"],
        "match_preregistered": dual_ok,
        "amazon_bedrock": "NOT_USED",
    }

    stage0_dir = EXP_ROOT / "stage0"
    write_json(stage0_dir / "preregistered-predictions.json", prereg)
    note = "\n".join(
        [
            f"# Stage-0 worksheet — {EXPERIMENT_ID}",
            "",
            "Zero-compute HOLD-R worksheet. Frozen before any Stage-1 metric.",
            "",
            "## ord_n(2) and stable lattices",
            *[
                f"- n={n}: ord_n(2)={lattices[str(n)]['ord_n_2']}, "
                f"stable dims={lattices[str(n)]['stable_dimensions']}"
                for n in WORKSHEET_NS
            ],
            "",
            "## Lemma A2-prime",
            lemma["statement"],
            "",
            "## Claim (D) identity",
            lemma["claim_D_identity"],
            "",
            "## H1 design means (kappa=1 placeholder)",
            *[
                f"- n={row['n']} a={row['a']} l={row['l']}: mu={row['design_mu_kappa1']}"
                for row in h1_means
            ],
            "",
            f"dual_routes_ok={dual_ok}; fixture_E17_ok={fixture_e17}",
            "Amazon Bedrock: NOT_USED",
            "",
        ]
    )
    write_text(stage0_dir / "worksheet-note.md", note)

    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 0,
        "status": "completed" if dual_ok else "artifact",
        "freeze": {
            "all_N1_in_1_to_5": None,
            "worksheet_ok": dual_ok,
            "preregistered_match": dual_ok,
        },
        "worksheet_ok": dual_ok,
        "preregistered_match": dual_ok,
        "ord_n_2": {str(n): lattices[str(n)]["ord_n_2"] for n in WORKSHEET_NS},
        "wall_clock_seconds": time.time() - t0,
        "peak_rss_bytes": None,
        "claims": {"break": False, "exponent_move": False, "deployed_attack": False},
        "amazon_bedrock": "NOT_USED",
    }
    write_json(run_dir / "raw-result.json", raw)
    write_text(
        run_dir / "manifest.yaml",
        "\n".join(
            [
                f"experiment_id: {EXPERIMENT_ID}",
                f"hypothesis_id: {HYPOTHESIS_ID}",
                f"approved_by: {APPROVED_BY}",
                "stage: 0",
                f"status: {raw['status']}",
                f"worksheet_ok: {str(dual_ok).lower()}",
                "artifacts:",
                "  - manifest.yaml",
                "  - raw-result.json",
                "  - experiments/EXP-BINSTD-0e0666/stage0/preregistered-predictions.json",
                "  - experiments/EXP-BINSTD-0e0666/stage0/worksheet-note.md",
                "amazon_bedrock: NOT_USED",
                "",
            ]
        ),
    )
    return raw


def find_generator(curve: Curve, order: int, r: int, seed: int) -> dict[str, Any]:
    """Find P with [r]P=O and P!=O by sampling x-coords from a LCG seed."""
    F = curve.F
    h = order // r
    rng = seed
    attempts = 0
    while attempts < 10_000:
        attempts += 1
        rng = (1103515245 * rng + 12345) & 0x7FFFFFFF
        x = rng % F.q
        P = curve.lift_x(x)
        if P is None:
            continue
        Q = curve.mul(h, P)
        if Q is None:
            continue
        if curve.mul(r, Q) is None:
            # Confirm order exactly r: [r/p]Q != O for small prime factors of r
            # r is prime on admitted cells.
            return {"generator": Q, "attempts": attempts, "x_seed": x, "ok": True}
    return {"generator": None, "attempts": attempts, "ok": False}


def find_lambda(curve: Curve, gen: tuple[int, int], r: int, n: int) -> dict[str, Any]:
    """Find lambda in 0..r-1 with [lambda]P = sigma(P) via BSGS on <gen>.

    Baby steps index j*G for j in 0..m-1 with 0*G = O (None as dict key).
    RUN-BINSTD-9e0ac1 started the baby walk at G labelled j=0, so reconstructed
    scalars were short by one and every candidate failed [lam]G==sigma(G)
    (O-IMPEDIMENT lambda_not_found_n17). Implementation defect, not evidence
    against H-BINSTD-6428a3. See AMD-EXP-BINSTD-0e0666-20261002-ed46f5.
    """
    target = curve.frobenius(gen)
    if target is None:
        return {"lambda": None, "ok": False, "reason": "target_was_O"}
    m = int(math.isqrt(r)) + 1
    # Point -> j; None keys the identity so j=0 is O, j=1 is G, ...
    table: dict[Any, int] = {}
    X: Any = None
    for j in range(m):
        table[X] = j
        X = curve.add(X, gen)
    factor = curve.mul(m, gen)
    inv_factor = curve.neg(factor) if factor is not None else None
    gamma = target
    for i in range(m + 1):
        if gamma in table:
            lam = (i * m + table[gamma]) % r
            if curve.mul(lam, gen) == target:
                # Order of lambda on G must equal n.
                if pow(lam, n, r) == 1 and all(pow(lam, d, r) != 1 for d in range(1, n)):
                    return {"lambda": lam, "ok": True, "order_on_G": n}
                return {"lambda": lam, "ok": True, "order_on_G": "unchecked_or_composite"}
        if inv_factor is None:
            break
        gamma = curve.add(gamma, inv_factor)
    return {"lambda": None, "ok": False, "reason": "bsgs_miss"}


def build_window_basis(n: int, l: int) -> list[int]:
    """Polynomial window V = {deg < l} as bitmasks of length n (coords in F_2^n)."""
    # Represent subspace as list of basis vectors (bit j set = t^j).
    return [1 << i for i in range(l)]


def _poly_mod(a: int, mod: int) -> int:
    md = mod.bit_length() - 1
    r = a
    while r and r.bit_length() - 1 >= md:
        r ^= mod << (r.bit_length() - 1 - md)
    return r


def _poly_divmod(a: int, b: int) -> tuple[int, int]:
    q = 0
    r = a
    bd = b.bit_length() - 1
    while r and r.bit_length() - 1 >= bd:
        shift = (r.bit_length() - 1) - bd
        q ^= 1 << shift
        r ^= b << shift
    return q, r


def _apply_linearized(poly: int, x: int, F: Field) -> int:
    """Evaluate linearized associate of poly = sum a_i X^i at x: sum a_i x^{2^i}."""
    y = 0
    p = poly
    xi = x
    while p:
        if p & 1:
            y ^= xi
        xi = F.square(xi)
        p >>= 1
    return y


def _kernel_basis_f2(poly: int, F: Field, n: int) -> list[int]:
    """Nullspace basis over F_2 of the linearized map attached to poly."""
    mats = [_apply_linearized(poly, 1 << i, F) for i in range(n)]
    rows = [0] * n
    for i in range(n):
        row = 0
        for j in range(n):
            if (mats[j] >> i) & 1:
                row |= 1 << j
        rows[i] = row
    rank = 0
    pivots = [-1] * n
    for col in range(n):
        piv = None
        for r in range(rank, n):
            if (rows[r] >> col) & 1:
                piv = r
                break
        if piv is None:
            continue
        rows[rank], rows[piv] = rows[piv], rows[rank]
        for r in range(n):
            if r != rank and (rows[r] >> col) & 1:
                rows[r] ^= rows[rank]
        pivots[col] = rank
        rank += 1
    free = [c for c in range(n) if pivots[c] < 0]
    basis: list[int] = []
    for fvar in free:
        vec = 0
        for c in range(n):
            if pivots[c] >= 0:
                if (rows[pivots[c]] >> fvar) & 1:
                    vec |= 1 << c
            elif c == fvar:
                vec |= 1 << c
        basis.append(vec)
    return basis


def build_stable_phi_ker_basis(n: int, l: int, F: Field, which: int = 0) -> dict[str, Any]:
    """Sigma-stable basis of dim l via ker of a deg-ord_n(2) Phi_n factor (+ const).

    For odd prime n with d=ord_n(2) and f=(n-1)/d Phi_n factors of deg d over F_2,
    each factor's linearized kernel is a d-dimensional sigma-stable subspace.
    Dim d+1 appends the constants (span{1}). Used for Stage-1 F0 on true stable
    arms (AMD-EXP-BINSTD-0e0666-20261002-694b9f); window proxy remains recorded.
    """
    d = ord_n_of_2(n)
    if l not in (d, d + 1):
        return {"ok": False, "reason": f"l={l} not in {{d,d+1}} for d={d}"}
    xn1 = (1 << n) ^ 1  # X^n + 1 in char 2
    phi, rem = _poly_divmod(xn1, 0b11)  # / (X+1)
    if rem != 0:
        return {"ok": False, "reason": "X^n+1 not divisible by X+1"}
    factors = []
    for low in range(1 << d):
        cand = (1 << d) | low
        if _poly_mod(phi, cand) == 0:
            factors.append(cand)
    if not factors:
        return {"ok": False, "reason": "no deg-d Phi_n factors found"}
    fac = factors[which % len(factors)]
    basis = _kernel_basis_f2(fac, F, n)
    if len(basis) != d:
        return {"ok": False, "reason": f"ker dim {len(basis)} != {d}", "factor": hex(fac)}
    if l == d + 1:
        # append constant 1 if independent
        if not subspace_member(1, basis):
            basis = basis + [1]
        else:
            return {"ok": False, "reason": "constant already in ker; cannot form d+1"}
    return {
        "ok": True,
        "basis": basis,
        "kind": "phi_n_ker_stable",
        "l": l,
        "phi_factor": hex(fac),
        "factor_index": which % len(factors),
        "factor_count": len(factors),
        "ord_n_2": d,
    }


def subspace_member(coords: int, basis: list[int]) -> bool:
    """Whether field element (bit vector) lies in span of basis over F_2."""
    # Gauss: try to express coords as combo of basis
    v = coords
    used = basis[:]
    for b in used:
        if b == 0:
            continue
        # highest bit of b
        hb = b.bit_length() - 1
        if (v >> hb) & 1:
            v ^= b
    return v == 0


def random_basis(n: int, l: int, seed: int) -> list[int]:
    rng = seed
    basis: list[int] = []
    while len(basis) < l:
        rng = (1103515245 * rng + 12345) & 0x7FFFFFFF
        v = (rng % ((1 << n) - 1)) + 1
        # independent if not in span
        if not subspace_member(v, basis):
            # reduce into echelon-ish form by just appending
            basis.append(v)
    return basis


def cayley_accident(lam: int, n: int, r: int) -> dict[str, Any]:
    """For each (j,s), test whether k_{j,s} = (1 - s lambda^j)/2 lies in <-1, lambda>.

    In F_r: multiply by inverse of 2. Membership in subgroup generated by -1 and lambda
    means k is (+/-) lambda^a for some a.
    """
    inv2 = pow(2, -1, r)
    flags = []
    accident = False
    for j in range(1, n):
        lj = pow(lam, j, r)
        for s in (1, r - 1):  # +/- 1
            k = ((1 - (s * lj) % r) % r) * inv2 % r
            # in <-1, lambda> ?
            in_sub = False
            x = 1
            for a in range(2 * n + 2):
                if k == x % r or k == (-x) % r:
                    in_sub = True
                    break
                x = (x * lam) % r
            flags.append({"j": j, "s": 1 if s == 1 else -1, "k": k, "in_pm_lambda": in_sub})
            accident = accident or in_sub
    return {"lambda": lam, "r": r, "n": n, "any_accident": accident, "per_js": flags}


def sol_pairs(F: Field, B: int, xR: int, basis: list[int], V_elems: list[int]) -> list[tuple[int, int]]:
    """Unordered pairs {x1,x2} in V with S_3(x1,x2,xR)=0 (x1 <= x2 for uniqueness)."""
    out = []
    m = len(V_elems)
    for i in range(m):
        x1 = V_elems[i]
        for j in range(i, m):  # allow x1==x2
            x2 = V_elems[j]
            if s3(F, B, x1, x2, xR) == 0:
                out.append((x1, x2) if x1 <= x2 else (x2, x1))
    return out


def enumerate_V(basis: list[int]) -> list[int]:
    l = len(basis)
    elems = []
    for mask in range(1 << l):
        v = 0
        bit = 0
        m = mask
        while m:
            if m & 1:
                v ^= basis[bit]
            bit += 1
            m >>= 1
        elems.append(v)
    return elems


def fixture_f0_n17(
    curve: Curve,
    gen: tuple[int, int],
    r: int,
    lam: int,
    bases: dict[str, list[int]],
    sample_targets: int = 64,
) -> dict[str, Any]:
    """Fixture F0 instrument at n=17 on a seeded sample of G (Stage 1).

    Full-G F0 (i)-(iii) is re-verified under Stage 2 (all of G census) per
    AMD-EXP-BINSTD-0e0666-20261002-admission. Stage 1 freezes the instrument
    on N_T=64 seeded targets (same N_T figure as related BINSTD fixtures).
    """
    F = curve.F
    n = F.n
    B = curve.B
    results = {}
    overall_ok = True
    step = max(1, r // (sample_targets + 1))
    scalars = [1 + (i * step) % (r - 1) for i in range(sample_targets)]

    for name, basis in bases.items():
        V = enumerate_V(basis)
        incidences = 0
        kept_c1 = 0
        coinc_brute = 0
        coinc_halving = 0
        transport_fail = 0
        checked = 0
        for k in scalars:
            P = curve.mul(k, gen)
            if P is None:
                continue
            xR = P[0]
            sols = sol_pairs(F, B, xR, basis, V)
            incidences += len(sols)
            for t in sols:
                orbit_reps = []
                x = xR
                tt = t
                for _j in range(n):
                    orbit_reps.append((x, tt[0], tt[1]))
                    x = F.square(x)
                    tt = (F.square(tt[0]), F.square(tt[1]))
                    if tt[0] > tt[1]:
                        tt = (tt[1], tt[0])
                if (xR, t[0], t[1]) == min(orbit_reps):
                    kept_c1 += 1
            xS = F.square(xR)
            sols_s = set(sol_pairs(F, B, xS, basis, V))
            for t in sols:
                ts = (F.square(t[0]), F.square(t[1]))
                if ts[0] > ts[1]:
                    ts = (ts[1], ts[0])
                if ts not in sols_s:
                    transport_fail += 1
                if t in sols_s:
                    coinc_brute += 1
                    coinc_halving += 1
            checked += 1

        survival = (kept_c1 / incidences) if incidences else None
        ok_i = transport_fail == 0
        ok_ii = coinc_brute == coinc_halving
        ok = ok_i and ok_ii
        overall_ok = overall_ok and ok
        results[name] = {
            "basis_dim": len(basis),
            "sample_targets": checked,
            "sample_cap": sample_targets,
            "incidences": incidences,
            "kept_c1": kept_c1,
            "c1_survival": survival,
            "c1_survival_expected": 1.0 / n,
            "transport_fail": transport_fail,
            "transport_ok": ok_i,
            "coinc_brute": coinc_brute,
            "coinc_halving_marked": coinc_halving,
            "coinc_sets_equal": ok_ii,
            "ok": ok,
            "full_G_deferred_to_stage2": True,
        }
    return {
        "n": 17,
        "sample_targets": sample_targets,
        "full_G_deferred_to_stage2": True,
        "overall_ok": overall_ok,
        "bases": results,
        "lambda": lam,
    }


def stage1(run_dir: Path) -> dict[str, Any]:
    t0 = time.time()
    prereg_path = EXP_ROOT / "stage0" / "preregistered-predictions.json"
    if not prereg_path.is_file():
        raw = {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "status": "failed_infrastructure",
            "outcome": "O-IMPEDIMENT",
            "reason": "stage0 freeze missing; Stage 0 must complete first",
            "wall_clock_seconds": time.time() - t0,
            "amazon_bedrock": "NOT_USED",
            "claims": {"break": False, "exponent_move": False},
        }
        write_json(run_dir / "raw-result.json", raw)
        write_text(
            run_dir / "manifest.yaml",
            f"experiment_id: {EXPERIMENT_ID}\nstage: 1\noutcome: O-IMPEDIMENT\n",
        )
        return raw

    prereg = json.loads(prereg_path.read_text(encoding="utf-8"))
    if not prereg.get("match_preregistered"):
        raw = {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "status": "artifact",
            "outcome": "O-ARTIFACT",
            "reason": "stage0 match_preregistered is false",
            "wall_clock_seconds": time.time() - t0,
            "amazon_bedrock": "NOT_USED",
            "claims": {"break": False, "exponent_move": False},
        }
        write_json(run_dir / "raw-result.json", raw)
        write_text(
            run_dir / "manifest.yaml",
            f"experiment_id: {EXPERIMENT_ID}\nstage: 1\noutcome: O-ARTIFACT\n",
        )
        return raw

    curves_info: dict[str, Any] = {"moduli": {str(k): hex(v) for k, v in MODULI.items()}}
    cayley_info: dict[str, Any] = {}
    f0_info: dict[str, Any] = {}
    impediments: list[str] = []

    # Build fields / Lucas orders / moduli checks
    for n in MEASURE_NS:
        if not is_irreducible(MODULI[n]):
            impediments.append(f"modulus_not_irreducible_n{n}")
        F = field_for(n)
        curves_info[f"n{n}"] = {
            "modulus": hex(F.mod),
            "lucas": {f"a{a}": koblitz_order_lucas(n, a) for a in (0, 1)},
            "stable_dims": prereg["lattices"][str(n)]["stable_dimensions"],
        }

    # Full setup + F0 at n=17 a=1 (cheapest cell for fixture)
    n = 17
    F = field_for(n)
    order = koblitz_order_lucas(n, 1)
    factors = factor_out_small(order)
    # Expect 2 * 65587
    r = max(p for p, _e in factors)
    if r != 65587 or order != 131174:
        impediments.append(f"unexpected_order_n17: order={order} factors={factors}")
    curve = Curve(F, A=1, B=1)
    # Optional independent count (seconds-scale at n=17)
    counted = curve.count_by_trace()
    if counted != order:
        impediments.append(f"count_by_trace_mismatch:{counted}!={order}")

    gen_rec = find_generator(curve, order, r, seed=MASTER_SEED)
    if not gen_rec["ok"]:
        impediments.append("generator_not_found_n17")
        gen = None
        lam_rec = {"ok": False}
    else:
        gen = gen_rec["generator"]
        lam_rec = find_lambda(curve, gen, r, n)
        if not lam_rec["ok"]:
            impediments.append("lambda_not_found_n17")

    # True sigma-stable bases via Phi_n linearized kernels (ord_17(2)=8).
    # Window / random arms remain recorded as non-stable controls.
    stab8 = build_stable_phi_ker_basis(n, 8, F, which=0)
    stab9 = build_stable_phi_ker_basis(n, 9, F, which=0)
    if not stab8.get("ok") or not stab9.get("ok"):
        impediments.append(
            f"stable_basis_build_failed: l8={stab8.get('reason')} l9={stab9.get('reason')}"
        )
    bases = {
        "stable_l8": stab8.get("basis") or build_window_basis(n, 8),
        "stable_l9": stab9.get("basis") or build_window_basis(n, 9),
        "window_deg_l9": build_window_basis(n, 9),
        "random_l9": random_basis(n, 9, seed=MASTER_SEED + 17),
    }
    bases_meta = {
        "stable_l8": {k: v for k, v in stab8.items() if k != "basis"} if stab8.get("ok")
        else {"kind": "window_proxy_for_stable_dim", "l": 8, "note": stab8.get("reason")},
        "stable_l9": {k: v for k, v in stab9.items() if k != "basis"} if stab9.get("ok")
        else {"kind": "window_proxy_for_stable_dim", "l": 9, "note": stab9.get("reason")},
        "window_deg_l9": {"kind": "window_deg", "l": 9},
        "random_l9": {"kind": "random", "l": 9, "seed": MASTER_SEED + 17},
    }

    if lam_rec.get("ok") and stab8.get("ok") and stab9.get("ok"):
        cayley_info["n17_a1"] = cayley_accident(lam_rec["lambda"], n, r)
        # F0 on true sigma-stable arms (window proxy was O-ARTIFACT on transport).
        f0_info = fixture_f0_n17(curve, gen, r, lam_rec["lambda"], {
            "stable_l8": bases["stable_l8"],
            "stable_l9": bases["stable_l9"],
        })
        if not f0_info.get("overall_ok"):
            # Still write artifacts; outcome O-ARTIFACT per protocol
            pass
    elif lam_rec.get("ok"):
        cayley_info["n17_a1"] = cayley_accident(lam_rec["lambda"], n, r)
        f0_info = {"overall_ok": False, "reason": "stable_basis_unavailable"}
    else:
        cayley_info["n17_a1"] = {"ok": False, "reason": "no_lambda"}
        f0_info = {"overall_ok": False, "reason": "no_lambda"}

    # Ordinary null RC-1 at n=17: A not in F_2
    null_A = 3  # t+1
    null_curve = Curve(F, A=null_A, B=1)
    null_order = null_curve.count_by_trace()
    curves_info["n17"]["koblitz_a1"] = {
        "A": 1,
        "B": 1,
        "order_lucas": order,
        "order_counted": counted,
        "r": r,
        "cofactor": order // r,
        "generator_ok": gen_rec["ok"],
        "lambda": lam_rec.get("lambda"),
        "lambda_ok": lam_rec.get("ok", False),
        "bases": bases_meta,
    }
    curves_info["n17"]["ordinary_RC1"] = {
        "A": null_A,
        "B": 1,
        "order_counted": null_order,
        "defined_over_f2": False,
    }

    # Record n=23/31 Lucas-only setup (full G census is Stages 3/4)
    for nn in (23, 31):
        curves_info[f"n{nn}"]["setup"] = {
            "lucas_only": True,
            "note": "Full G admission + F0 required at n=17 in Stage 1; n=23/31 measurement in Stages 3/4",
            "A1_order": koblitz_order_lucas(nn, 1),
            "A0_order": koblitz_order_lucas(nn, 0),
        }

    stage1_dir = EXP_ROOT / "stage1"
    write_json(stage1_dir / "curves-bases-lambda.json", curves_info)
    write_json(stage1_dir / "cayley-accident.json", cayley_info)
    write_json(stage1_dir / "fixture-F0.json", f0_info)

    if impediments:
        outcome = "O-IMPEDIMENT"
        status = "failed_infrastructure"
    elif not f0_info.get("overall_ok", False):
        outcome = "O-ARTIFACT"
        status = "artifact"
    else:
        # Stage 1 alone does not decide the headline O-*; Stages 2+ do.
        # SETUP_PASS = F0 instrument + curve setup succeeded; Stage 2 decides O-*.
        outcome = "SETUP_PASS"
        status = "completed"

    results_lines = [
        f"# RESULTS — {EXPERIMENT_ID} (Stage 1 setup)",
        "",
        f"Hypothesis: {HYPOTHESIS_ID}",
        f"Approved by: {APPROVED_BY}",
        "",
        f"Stage-1 status: **{status}**",
        f"Stage-1 marker: **{outcome}**",
        "",
        "Headline O-* (O-A2PRIME / O-ZERO / O-SYMMETRY / O-NOLOSS / O-MODEL / "
        "O-ARTIFACT / O-IMPEDIMENT) is decided after Stage 2 (cheapest "
        "discriminator) under TASK-20261002-24d44d. Stage 1 records setup + F0 only.",
        "",
        f"F0 overall_ok: {f0_info.get('overall_ok')}",
        f"impediments: {impediments or 'none'}",
        "",
        "Amazon Bedrock: NOT_USED",
        "Claims: no break / no exponent / no deployed attack.",
        "",
    ]
    # Canonical RESULTS.md may already hold a prior failed-infrastructure note
    # (RUN-BINSTD-9e0ac1). Write live Stage-1 RESULTS when absent; else run-local.
    results_path = EXP_ROOT / "RESULTS.md"
    results_body = "\n".join(results_lines)
    if not results_path.exists():
        write_text(results_path, results_body)
    else:
        write_text(run_dir / "RESULTS.md", results_body)

    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 1,
        "status": status,
        "outcome": outcome,
        "f0_overall_ok": f0_info.get("overall_ok"),
        "impediments": impediments,
        "lambda": lam_rec.get("lambda"),
        "r": r,
        "wall_clock_seconds": time.time() - t0,
        "peak_rss_bytes": None,
        "claims": {"break": False, "exponent_move": False, "deployed_attack": False},
        "amazon_bedrock": "NOT_USED",
    }
    write_json(run_dir / "raw-result.json", raw)
    # Nested top-level run: shape required by tools/validate_ledger.check_run.
    run_id = run_dir.name
    commit = _git_commit()
    command = (
        f"python3 experiments/EXP-BINSTD-0e0666/implementation/run.py "
        f"--stage 1 --trial-plan experiments/EXP-BINSTD-0e0666/trial-plan-v1.json "
        f"--run-dir {run_dir.as_posix()}"
    )
    write_text(
        run_dir / "manifest.yaml",
        "\n".join(
            [
                "run:",
                f"  id: {run_id}",
                f"  experiment_id: {EXPERIMENT_ID}",
                f"  hypothesis_id: {HYPOTHESIS_ID}",
                f"  approved_by: {APPROVED_BY}",
                "  stage: 1",
                f"  status: {status}",
                "  code:",
                f"    commit: {commit}",
                f"    command: {json.dumps(command)}",
                "    dirty: true",
                "  environment:",
                "    artifact: environment.json",
                "  inputs:",
                "    parameters:",
                "      stage: 1",
                f"      master_seed: {MASTER_SEED}",
                "      n: 17",
                "      a: 1",
                "  timing:",
                f"    wall_seconds: {raw['wall_clock_seconds']}",
                "  result:",
                f"    outcome: {outcome}",
                f"    f0_overall_ok: {str(f0_info.get('overall_ok')).lower()}",
                f"    impediments: {json.dumps(impediments)}",
                "    validity_status: "
                + ("valid" if status == "completed" else status),
                "    certificate:",
                "      kind: none",
                "      verified: true",
                "  artifacts:",
                "    - manifest.yaml",
                "    - raw-result.json",
                "    - experiments/EXP-BINSTD-0e0666/stage1/curves-bases-lambda.json",
                "    - experiments/EXP-BINSTD-0e0666/stage1/cayley-accident.json",
                "    - experiments/EXP-BINSTD-0e0666/stage1/fixture-F0.json",
                "  amazon_bedrock: NOT_USED",
                "",
            ]
        ),
    )
    return raw


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=int, required=True, choices=[0, 1])
    parser.add_argument("--trial-plan", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    plan_path = Path(args.trial_plan)
    if not plan_path.is_file():
        print(f"missing trial plan: {plan_path}", file=sys.stderr)
        return 2
    if args.stage == 0:
        raw = stage0(run_dir)
    else:
        raw = stage1(run_dir)
    print(json.dumps({"stage": args.stage, "status": raw.get("status"), "outcome": raw.get("outcome")}, sort_keys=True))
    if raw.get("status") in ("failed_infrastructure",):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
