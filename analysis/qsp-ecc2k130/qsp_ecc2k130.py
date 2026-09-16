#!/usr/bin/env python3
"""Quasi-subfield-polynomial (QSP) index calculus evaluated at the ECC2K-130 field.

Every number this script prints is THIS PROGRAM'S arithmetic, computed under the
conventions stated below from formulas read in two frozen sources:

  [HKPYY20]  Huang, Kosters, Petit, Yeo, Yun, "Quasi-subfield polynomials and the
             elliptic curve discrete logarithm problem", J. Math. Cryptol. 14(1)
             2020, 25-38.  Frozen at inputs/HUANG-2020-JMC-QSP/.
             Used: Definition 3.1, Lemma 3.1, Theorem 3.2, Remark 3.1, Lemma 4.1,
             Lemma 4.3, Appendix A.1 (M(E)), Appendix C.2.
  [EP21]     Euler, Petit, "New results on quasi-subfield polynomials", arXiv
             1909.11326v2.  Frozen at inputs/EULER-PETIT-2019-QSP/.
             Used: Definition 2 (beta), Theorem 1, Lemma 2, Proposition 2,
             Proposition 5 (Types 1, 1bis, 2, 3), Proposition 6, Propositions 7-8,
             Remark 1, Section 4.4.

Target: the Certicom ECC2K-130 curve y^2 + xy = x^3 + 1 over F_{2^131}
(KN-LIT-096 / KN-LIT-661e97): p = q = 2, n = 131.  The generic baseline is
sqrt(2^131) ~ 2^65.5 group operations; the recorded rho estimate with the
Frobenius and negation speedups is 2^60.9 iterations (KN-LIT-096).

Nothing here is evidence about the ECDLP.  It is a pre-compute audit in the
sense of docs/inventor-protocol.md section 8: exact baseline embedding and method
ceiling of the published algorithm at one parameter, with every assumption named.

Usage:  python3 qsp_ecc2k130.py  [--json results.json] [--md table.md]
"""
from __future__ import annotations

import argparse
import json
import math
import sys

N_EXT = 131          # extension degree of the ECC2K-130 field over F_2
P = 2                # characteristic
KAPPA = 4.876        # Rojas exponent constant used by [HKPYY20] Lemma 3.1
ROJAS_M_EXP = 5.188  # m^5.188 factor, [HKPYY20] Lemma 3.1
GENERIC_LOG2 = N_EXT / 2                 # sqrt(2^131): 65.5
RHO_BASELINE_LOG2 = 60.9                 # KN-LIT-096 estimate with speedups
BETA_GENERIC_THRESHOLD = 1 / (2 * KAPPA) # alpha_beta > 1  <=>  beta < 1/(2 kappa) = 0.1025 ([EP21] Remark 1)


# ---------------------------------------------------------------------------
# 1. Field facts: ord_131(2), factorisation of X^131 - 1 over F_2, 2^131 - 1
# ---------------------------------------------------------------------------
def mult_order(a: int, m: int) -> int:
    o, x = 1, a % m
    while x != 1:
        x = x * a % m
        o += 1
    return o


def f2_polymulmod(a: int, b: int, mod: int) -> int:
    """Multiply two F_2[X] polynomials (bit-packed ints) modulo `mod`."""
    deg = mod.bit_length() - 1
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a >> deg & 1:
            a ^= mod
    return r


def f2_gcd(a: int, b: int) -> int:
    while b:
        # a mod b
        db = b.bit_length()
        while a and a.bit_length() >= db:
            a ^= b << (a.bit_length() - db)
        a, b = b, a
    return a


def cyclotomic_131_irreducible_over_f2() -> dict:
    """Ben-Or style check: Phi_131 = (X^131-1)/(X-1) is irreducible over F_2 iff
    gcd(X^(2^k) - X, Phi) = 1 for all k < 130 (its degree is 130 and it is
    squarefree).  Returns the first k at which a non-trivial gcd appears, if any."""
    phi = (1 << 131) - 1        # X^130 + ... + X + 1: bits 0..130 set, degree 130
    x = 0b10
    xp = x
    for k in range(1, 130):
        xp = f2_polymulmod(xp, xp, phi)   # X^(2^k) mod Phi
        g = f2_gcd(phi, xp ^ x)
        if g != 1:
            return {"irreducible": False, "first_nontrivial_gcd_at_k": k}
    return {"irreducible": True, "first_nontrivial_gcd_at_k": None}


def field_facts() -> dict:
    ord2 = mult_order(2, N_EXT)
    try:
        import sympy  # type: ignore
        mers = 2 ** N_EXT - 1
        fac = sympy.factorint(mers)
        fac_str = {str(k): v for k, v in fac.items()}
        primality = {str(k): bool(sympy.isprime(k)) for k in fac}
        sympy_version = sympy.__version__
    except Exception as exc:  # pragma: no cover
        fac_str, primality, sympy_version = {"error": str(exc)}, {}, None
    irr = cyclotomic_131_irreducible_over_f2()
    return {
        "n": N_EXT,
        "ord_131_of_2": ord2,
        "phi_131_irreducible_over_F2": irr,
        "X131_minus_1_over_F2": "(X + 1) * Phi_131(X) with Phi_131 irreducible of degree 130"
        if irr["irreducible"] and ord2 == 130 else "see phi_131_irreducible_over_F2",
        "divisor_degrees_of_X131_minus_1": [0, 1, 130, 131],
        "2^131-1": str(2 ** N_EXT - 1),
        "2^131-1_factorisation": fac_str,
        "2^131-1_factor_primality": primality,
        "sympy_version": sympy_version,
        "n_plus_1_divisors": sorted(d for d in range(1, N_EXT + 2) if (N_EXT + 1) % d == 0),
    }


# ---------------------------------------------------------------------------
# 2. Quasi-subfield polynomial admissibility at n = 131
# ---------------------------------------------------------------------------
def lemma41_min_log2_deg(n: int, np_: int) -> float:
    """[HKPYY20] Lemma 4.1: floor(n/n') * l + (n mod n') >= n'  with l = log_2 deg(lambda).
    Returns the smallest real l satisfying it (0 if already satisfied at l = 0)."""
    q, r = divmod(n, np_)
    need = np_ - r
    return max(0.0, need / q)


def ep21_lemma2_max_np_linearized(n: int, ell: int) -> int:
    """[EP21] Lemma 2: a completely splitting linearized L = X^{p^n'} - (a_l X^{p^l} + ...)
    with l >= 1 needs n >= n' + (n' - l) * floor((n' - 1)/l).  Return the largest n'
    compatible with this for the given l (n' > l)."""
    best = 0
    for np_ in range(ell + 1, n):
        if n >= np_ + (np_ - ell) * ((np_ - 1) // ell):
            best = np_
    return best


def beta(n: int, np_: int, ell: float) -> float:
    return ell * n / (np_ * np_)


def linearized_f2_census(n: int) -> list[dict]:
    """[EP21] Proposition 2 / [HKPYY20] Section 4.3: with coefficients in F_2, L_f splits
    completely over F_{2^n} iff f | X^n - 1 over F_2.  At n = 131 the monic divisors are
    1, X+1, Phi_131, X^131-1 (field_facts), so the only candidates are n' = 1 and n' = 130."""
    out = []
    # n' = 1: f = X + 1, L = X^2 + X, lambda = X, l = 0: the subfield F_2 itself.
    out.append({"n_prime": 1, "f": "X + 1", "L": "X^2 - X", "log2_deg_lambda": 0,
                "beta": 0.0, "note": "subfield polynomial of F_2; |V| = 2, useless as a factor base"})
    # n' = 130: f = Phi_131 = X^130 + ... + X + 1, lambda has degree 2^129 (Type 1bis of [EP21]).
    out.append({"n_prime": 130, "f": "Phi_131(X) = X^130 + ... + X + 1",
                "L": "X^(2^130) + X^(2^129) + ... + X^2 + X", "log2_deg_lambda": 129,
                "beta": beta(n, 130, 129),
                "note": "[EP21] Type 1bis; beta = 1 - 1/(n-1)^2; |V| = 2^130 (half the field)"})
    return out


def published_family_membership(n: int) -> dict:
    """Which published QSP families ([EP21] Propositions 5 and 6, [HKPYY20] Lemma 4.3)
    admit extension degree n at p = 2?"""
    hits = []
    # Type 1 ([HKPYY20] Lemma 4.3): n = p_{k+1} = 1 + q' + q'^2 + ... + q'^{k+1}, q' a power of 2, a >= 2 in [EP21]
    for r in range(1, 12):
        qp = 2 ** r
        s, i = 1, 0
        while s < 10 * n:
            s += qp ** (i + 1)
            i += 1
            if s == n and i >= 2:
                hits.append({"family": "Type 1", "q_prime": qp, "k_plus_1": i})
    # Type 1bis: always available, n' = n - 1 (beta ~ 1)
    hits.append({"family": "Type 1bis", "n_prime": n - 1, "beta": beta(n, n - 1, n - 2)})
    # Type 2 ([EP21] Prop 5): n = q^{d+1} - 1 with q a power of 2, d >= 1
    for r in range(1, 12):
        q = 2 ** r
        d = 1
        while q ** (d + 1) - 1 <= n:
            if q ** (d + 1) - 1 == n:
                hits.append({"family": "Type 2", "q": q, "d": d})
            d += 1
    # Multiplicative families ([EP21] Prop 6): (1) n = 2ik even; (2) p = kn + k - 1 with k >= 2; (3) p = kn - k - (-1)^n
    mult = {"family_1_needs_even_n": n % 2 == 0,
            "family_2_p_equals_kn_plus_k_minus_1_with_p_2": any(k * n + k - 1 == 2 for k in range(2, 4)),
            "family_3_p_equals_kn_minus_k_minus_neg1_pow_n_with_p_2": any(k * n - k - (-1) ** n == 2 for k in range(2, 4))}
    return {"additive_hits": hits, "multiplicative_families_at_p_2": mult}


def multiplicative_census(n: int, factorisation: dict) -> list[dict]:
    """[HKPYY20] Appendix C.2: V = {0} U mu_r for r | 2^n - 1, L = X^{2^n'} - X^a with
    a = 2^n' mod r; |V| = 1 + gcd(2^n' - a, 2^n - 1).  Report every (r, n') with |V| >= 2^n'/2."""
    primes = [int(k) for k in factorisation if k.isdigit()]
    mults = [factorisation[str(k)] for k in primes]
    divisors = [1]
    for pr, e in zip(primes, mults):
        divisors = [d * pr ** i for d in divisors for i in range(e + 1)]
    rows = []
    mers = 2 ** n - 1
    for r in sorted(divisors):
        if r == 1 or r == mers:
            continue
        for np_ in range(1, n):
            if 2 ** np_ <= r:
                continue
            a = pow(2, np_, r)
            if a == 0:
                continue
            size_v = 1 + math.gcd(2 ** np_ - a, mers)
            if size_v >= 2 ** (np_ - 1):
                rows.append({"r": str(r), "n_prime": np_, "a": str(a), "log2_a": math.log2(a) if a > 1 else 0.0,
                             "|V|": str(size_v), "|V|/2^n'": size_v / 2 ** np_,
                             "beta": beta(n, np_, math.log2(a)) if a > 1 else 0.0})
    return rows


# ---------------------------------------------------------------------------
# 3. Cost surface of the [HKPYY20] algorithm at n = 131 (log2 arithmetic ops)
# ---------------------------------------------------------------------------
def log2_factorial(m: int) -> float:
    return sum(math.log2(i) for i in range(2, m + 1))


def cost_cell(n: int, np_: int, d: int, m: int, frobenius_orbits: int = 1) -> dict:
    """[HKPYY20] Theorem 3.2:
         m! * q^{n - n'm + n'} * O~(m^5.188 (3d)^{4.876 m^2}) + m q^{2n'}
       with |F| ~ |V| ~ q^{n'} and success probability |F|^m/(m! q^n) capped at 1.
       Also the resultant-model floor: the univariate polynomial h of Lemma 3.1 has degree
       M(E) = prod_k lambda_k = 2^{m(m-1)} d^{m(m-1)/2} with lambda_k = d^{k-1} 2^{m-1}
       (Appendix A.1) and must be root-found once per attempt,
       so relation search costs at least (attempts) * M(E) under that model."""
    ell = math.log2(d)
    b = beta(n, np_, ell)
    log2_orbit = math.log2(frobenius_orbits)               # 0 unless V is Frobenius-stable on a Koblitz curve
    log2_p_succ = min(0.0, np_ * m - n - log2_factorial(m))
    log2_attempts = np_ - log2_orbit - log2_p_succ         # (2^{n'}/orbits) relations / success prob
    log2_rojas = ROJAS_M_EXP * math.log2(m) + KAPPA * m * m * math.log2(3 * d)
    log2_relation_phase = log2_attempts + log2_rojas
    log2_linear_algebra = math.log2(m) + 2 * (np_ - log2_orbit)
    log2_ME = m * (m - 1) * (1 + ell / 2)
    log2_floor = log2_attempts + log2_ME
    total = max(log2_relation_phase, log2_linear_algebra)  # log2 of the dominant term
    # d = 2 forces lambda = a X^2 + b X + c, an affine linearized polynomial, so [EP21]
    # Theorem 1 (beta >= 3/4) and Lemma 2 (n' <= 11 at l = 1, n = 131) apply; d >= 3 admits a
    # non-linearized lambda that no published theorem excludes.
    excluded = (d <= 2) and (b < 0.75 or np_ > ep21_lemma2_max_np_linearized(n, 1))
    return {"n_prime": np_, "d": d, "log2_d": ell, "m": m, "alpha": np_ * m / n, "beta": b,
            "frobenius_orbits": frobenius_orbits,
            "linearized_only_and_excluded_by_EP21": excluded,
            "log2_attempts": log2_attempts, "log2_rojas_per_attempt": log2_rojas,
            "log2_relation_phase": log2_relation_phase, "log2_linear_algebra": log2_linear_algebra,
            "log2_total_theorem32": total, "log2_M_E": log2_ME,
            "log2_resultant_floor": max(log2_floor, log2_linear_algebra)}


def cost_surface(n: int) -> dict:
    """Sweep n' in 2..n-1, m from ceil(n/n') to ceil(n/n')+3, and d = the smallest integer
    degree admitted by Lemma 4.1 (cost is monotone increasing in d, so the minimum over d
    is at d_min).  d_min < 2 is bumped to 2 because lambda linear means a subfield
    polynomial (impossible for prime n) and the quasi-subfield definition needs deg > 1."""
    rows = []
    for np_ in range(2, n):
        lmin = lemma41_min_log2_deg(n, np_)
        d_min = max(2, math.ceil(2 ** lmin - 1e-9))
        for d in sorted({d_min, max(d_min, 3)}):
            for m in range(math.ceil(n / np_), math.ceil(n / np_) + 4):
                if m < 2:
                    continue
                for orbits in (1, n):
                    rows.append(cost_cell(n, np_, d, m, orbits))
    qsp_rows = [r for r in rows if r["beta"] <= 1.0 and not r["linearized_only_and_excluded_by_EP21"]]
    plain = [r for r in rows if r["frobenius_orbits"] == 1]
    plain_qsp = [r for r in qsp_rows if r["frobenius_orbits"] == 1]
    frob_qsp = [r for r in qsp_rows if r["frobenius_orbits"] != 1]
    best_total = min(plain, key=lambda r: r["log2_total_theorem32"])
    best_total_qsp = min(plain_qsp, key=lambda r: r["log2_total_theorem32"]) if plain_qsp else None
    best_floor = min(plain, key=lambda r: r["log2_resultant_floor"])
    best_floor_qsp = min(plain_qsp, key=lambda r: r["log2_resultant_floor"]) if plain_qsp else None
    best_floor_frob = min(frob_qsp, key=lambda r: r["log2_resultant_floor"]) if frob_qsp else None
    best_total_frob = min(frob_qsp, key=lambda r: r["log2_total_theorem32"]) if frob_qsp else None
    admissible_np = sorted({r["n_prime"] for r in qsp_rows})
    generic_beating_np = sorted({r["n_prime"] for r in qsp_rows if r["beta"] < BETA_GENERIC_THRESHOLD})
    return {"rows": rows, "n_prime_with_some_qsp_cell_beta_le_1": admissible_np,
            "n_prime_with_beta_below_generic_threshold": generic_beating_np,
            "beta_generic_threshold": BETA_GENERIC_THRESHOLD,
            "best_theorem32_any": best_total, "best_theorem32_beta_le_1_not_excluded": best_total_qsp,
            "best_resultant_floor_any": best_floor, "best_resultant_floor_beta_le_1_not_excluded": best_floor_qsp,
            "best_theorem32_frobenius_orbits_not_excluded": best_total_frob,
            "best_resultant_floor_frobenius_orbits_not_excluded": best_floor_frob}


def prop8_exponent_table(kappa: float = KAPPA) -> list[dict]:
    """[EP21] Proposition 8 / Remark 1 asymptotic exponent 1 - alpha_beta/2 with
    alpha_beta = 1/(2 kappa beta), m >> 1, m fixed, and its value at n = 131."""
    rows = []
    for b in (1.0, 0.99994, 0.8, 0.75, 0.7, 0.6, 0.4, 0.2, 0.15, 0.1025, 0.1, 0.0958):
        ab = 1 / (2 * kappa * b)
        e = 1 - ab / 2
        rows.append({"beta": b, "alpha_beta": ab, "exponent": e, "log2_cost_at_n_131": e * N_EXT,
                     "beats_generic_65.5": e * N_EXT < GENERIC_LOG2,
                     "beats_rho_60.9": e * N_EXT < RHO_BASELINE_LOG2})
    return rows


def linearized_theorem1_bound() -> dict:
    """[EP21] Theorem 1: every completely splitting linearized QSP has beta >= 3/4.
    Consequence at n = 131 under Proposition 8's asymptotics and under Lemma 2's exact
    n' reach."""
    ab = 1 / (2 * KAPPA * 0.75)
    reach = {ell: ep21_lemma2_max_np_linearized(N_EXT, ell) for ell in range(1, 12)}
    kappa_needed = 1 / (2 * 0.75)  # alpha_beta > 1 at beta = 3/4  <=>  kappa < 2/3
    return {"beta_min": 0.75, "alpha_beta_at_kappa_4.876": ab, "exponent": 1 - ab / 2,
            "log2_cost_at_n_131": (1 - ab / 2) * N_EXT,
            "kappa_needed_for_alpha_beta_gt_1_at_beta_0.75": kappa_needed,
            "lemma2_max_n_prime_for_l": reach,
            "note": "[EP21] Section 4.4 says kappa < 1.5 would give alpha_beta > 1 at beta = 3/4; "
                    "from alpha_beta = 1/(2 kappa beta) that requires kappa < 2/3, not 1.5. "
                    "Recorded as a discrepancy in the source text, not adjudicated here."}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None)
    ap.add_argument("--md", default=None)
    args = ap.parse_args()

    facts = field_facts()
    out = {
        "schema": "crypto.autoresearch.analysis.qsp_ecc2k130.v1",
        "conventions": {
            "p": P, "n": N_EXT, "kappa": KAPPA, "generic_log2": GENERIC_LOG2,
            "rho_baseline_log2": RHO_BASELINE_LOG2,
            "cost_unit": "log2 of arithmetic operations over F_{2^131} as counted by [HKPYY20] Theorem 3.2; "
                         "the O~ cofactor is dropped; the 3^{kappa m^2} and m! factors are KEPT because at "
                         "n = 131 they are not constants a reader can ignore",
        },
        "field_facts": facts,
        "linearized_F2_coefficient_census": linearized_f2_census(N_EXT),
        "linearized_theorem1_bound": linearized_theorem1_bound(),
        "published_family_membership": published_family_membership(N_EXT),
        "multiplicative_census": multiplicative_census(N_EXT, facts["2^131-1_factorisation"]),
        "lemma41_admissibility": [
            {"n_prime": np_, "n_mod_n_prime": N_EXT % np_, "floor_n_over_n_prime": N_EXT // np_,
             "min_log2_deg_lambda": lemma41_min_log2_deg(N_EXT, np_),
             "beta_at_min": beta(N_EXT, np_, max(1.0, lemma41_min_log2_deg(N_EXT, np_)))}
            for np_ in range(2, N_EXT)],
        "prop8_exponent_table": prop8_exponent_table(),
        "cost_surface": cost_surface(N_EXT),
    }
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(out, fh, indent=1)
    cs = out["cost_surface"]
    lines = []
    lines.append(f"# QSP index calculus at n = 131 (ECC2K-130 field): cost surface\n")
    lines.append(f"Generic sqrt(2^131) = 2^{GENERIC_LOG2}; recorded rho estimate 2^{RHO_BASELINE_LOG2} (KN-LIT-096).\n")
    lines.append(f"ord_131(2) = {facts['ord_131_of_2']}; Phi_131 irreducible over F_2: {facts['phi_131_irreducible_over_F2']['irreducible']}; "
                 f"2^131 - 1 = {' * '.join(f'{k}^{v}' if v > 1 else k for k, v in facts['2^131-1_factorisation'].items())}.\n")
    lines.append("## n' at which some cell has beta <= 1 (a QSP is *definable*)\n")
    lines.append(", ".join(map(str, cs["n_prime_with_some_qsp_cell_beta_le_1"])) + "\n")
    lines.append(f"## n' at which beta < 1/(2 kappa) = {BETA_GENERIC_THRESHOLD:.4f} (Prop 8 asymptotic generic-beating region)\n")
    lines.append(", ".join(map(str, cs["n_prime_with_beta_below_generic_threshold"])) + "\n")
    lines.append("## Cheapest cells (Theorem 3.2 with every factor kept)\n")
    lines.append("| selection | n' | d | m | orbits | alpha | beta | log2 attempts | log2 Rojas/attempt | log2 relation phase | log2 lin. alg. | log2 total | log2 resultant floor |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for label, r in (("min total, any (d=2 rows are linearized-only)", cs["best_theorem32_any"]),
                     ("min total, beta<=1, not excluded", cs["best_theorem32_beta_le_1_not_excluded"]),
                     ("min floor, any (d=2 rows are linearized-only)", cs["best_resultant_floor_any"]),
                     ("min floor, beta<=1, not excluded", cs["best_resultant_floor_beta_le_1_not_excluded"]),
                     ("min total, Frobenius orbits (L in F_2[X], Koblitz)", cs["best_theorem32_frobenius_orbits_not_excluded"]),
                     ("min floor, Frobenius orbits (L in F_2[X], Koblitz)", cs["best_resultant_floor_frobenius_orbits_not_excluded"])):
        if r is None:
            continue
        lines.append(f"| {label} | {r['n_prime']} | {r['d']} | {r['m']} | {r['frobenius_orbits']} | {r['alpha']:.3f} | {r['beta']:.3f} | {r['log2_attempts']:.1f} | "
                     f"{r['log2_rojas_per_attempt']:.1f} | {r['log2_relation_phase']:.1f} | {r['log2_linear_algebra']:.1f} | "
                     f"{r['log2_total_theorem32']:.1f} | {r['log2_resultant_floor']:.1f} |")
    lines.append("\n## Selected cells (n' with n = 131 = -1 mod n', the Lemma 4.1 best case, at their smallest m)\n")
    lines.append("| n' | d | m | orbits | excluded (linearized) | alpha | beta | log2 attempts | log2 M(E) | log2 relation phase | log2 lin. alg. | log2 total | log2 floor |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in cs["rows"]:
        if (N_EXT + 1) % r["n_prime"] == 0 and r["m"] == math.ceil(N_EXT / r["n_prime"]) and r["n_prime"] >= 11:
            lines.append(f"| {r['n_prime']} | {r['d']} | {r['m']} | {r['frobenius_orbits']} | {r['linearized_only_and_excluded_by_EP21']} | {r['alpha']:.3f} | {r['beta']:.3f} | {r['log2_attempts']:.1f} | {r['log2_M_E']:.1f} | "
                         f"{r['log2_relation_phase']:.1f} | {r['log2_linear_algebra']:.1f} | {r['log2_total_theorem32']:.1f} | {r['log2_resultant_floor']:.1f} |")
    lines.append("\n## [EP21] Proposition 8 asymptotic exponent, evaluated at n = 131 (m >> 1 regime; NOT reachable at n = 131, see rows above)\n")
    lines.append("| beta | alpha_beta | exponent | log2 cost | < 65.5 | < 60.9 |\n|---|---|---|---|---|---|")
    for r in out["prop8_exponent_table"]:
        lines.append(f"| {r['beta']} | {r['alpha_beta']:.3f} | {r['exponent']:.3f} | {r['log2_cost_at_n_131']:.1f} | {r['beats_generic_65.5']} | {r['beats_rho_60.9']} |")
    lines.append("\n## Multiplicative QSP census (r | 2^131 - 1, |V| >= 2^(n'-1))\n")
    mc = out["multiplicative_census"]
    ratio_key = "|V|/2^n'"
    lines.append("none" if not mc else "\n".join(
        "- r=%s, n'=%d, |V|/2^n'=%.3f, beta=%.3f" % (r["r"], r["n_prime"], r[ratio_key], r["beta"]) for r in mc))
    lines.append("\n## Published additive families containing n = 131\n")
    lines.append(json.dumps(out["published_family_membership"], indent=1))
    lines.append("\n## Linearized QSPs: Theorem 1 and Lemma 2 of [EP21]\n")
    lines.append(json.dumps(out["linearized_theorem1_bound"], indent=1))
    md = "\n".join(lines) + "\n"
    if args.md:
        with open(args.md, "w") as fh:
            fh.write(md)
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
