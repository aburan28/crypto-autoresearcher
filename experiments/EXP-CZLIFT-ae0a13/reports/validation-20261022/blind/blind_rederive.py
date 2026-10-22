"""Blind re-derivation for REVIEW-CZLIFT-AE0A13-20261022 joint J3 (sealed, phase 1).

Statement (review_plan.blind_rederivation.quantity):
  For y^2 = x^3 + B at two anomalous primes from the specification's input
  range: s_tor(P) from two independent Hensel starts, the check
  [n]s_tor(P) = O mod p^k, s_tor(P+Q) = s_tor(P)+s_tor(Q), and
  v_p(z([p]s_tor(P))).
Parameters: curve family, k and n as stated in the specification (k = 4;
cm range 50 <= p <= 600; prime-order subgroup n != p, n >= 11, #E odd).

The statement is internally inconsistent with the specification: on an
anomalous curve #E(F_p) = p, so no prime n != p divides #E, the spec's formula
P^ - [n^{-1} mod p^k]([n]P^) is undefined (n = p is not invertible mod p^k),
and the spec places anomalous curves out of scope.  Both readings are computed
from mathematics alone:

  Reading A (literal): anomalous j = 0 curves y^2 = x^3 + B, 50 <= p <= 600,
    lifted by the integer CM model (the canonical lift).  "s_tor" is the
    Q_p-rational p-torsion lift T of P, which exists iff [p]P^ lies in E^2;
    T = P^ - tau with z(tau) = z([p]P^)/p (z is additive on E^1/E^5 since
    log z = z + (2a/5) z^5 + (3b/7) z^7 + ... and p > 7).  Reported: T from
    two Hensel starts, [p]T = O mod p^k, homomorphism, v_p(z([p]T)),
    v_p(z([p]P^)) on the canonical lift and on a non-canonical lift
    y^2 = x^3 + p c x + B as a control.

  Reading B (spec-consistent): non-anomalous j = 0 curves y^2 = x^3 + B,
    p = 1 mod 3 in [50, 600], #E odd, largest prime n | #E with n >= 11.
    s_tor by the spec formula F1 = P^ - [n^{-1} mod p^k]([n]P^) AND by an
    independent group-theoretic projection F2 = [e]P^, e = 1 mod #E,
    e = 0 mod p^{k-1} (projection of E(Z/p^k), order #E p^{k-1}, onto its
    prime-to-p part), each from two Hensel starts.  Reported: agreement,
    [n]s_tor = O mod p^k, homomorphism, v_p(z([n]s_tor)) (the Smart functional
    the claim says vanishes), the literal v_p(z([p]s_tor)) (not a formal-group
    point; recorded as-is), reduction to P, and the F1 addition count against
    2(bits(n)+bits(p^k))+1.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from blind_lib import (O, Curve, count_points, is_prime, prime_factors,  # noqa: E402
                       random_affine_point, self_test, vp)

SEED = 0x93FB1C
K_SPEC = 4
PMIN, PMAX = 50, 600
PAIRS = 8


def primes_1mod3():
    return [p for p in range(PMIN, PMAX + 1) if is_prime(p) and p % 3 == 1]


def twist_reps(p):
    """Minimal B in each class of F_p^* / (F_p^*)^6 (the six j = 0 twists)."""
    sixth = {pow(u, 6, p) for u in range(1, p)}
    seen, reps = set(), []
    for B in range(1, p):
        if B in seen:
            continue
        cls = {B * s % p for s in sixth}
        seen |= cls
        reps.append(B)
    return reps


def fp_add(p, a, b, P, Q):
    E1 = Curve(p, a, b, 1)
    R = E1.add((P[0], P[1], 1), (Q[0], Q[1], 1))
    n = E1.normalize(R, 1)
    return None if n[0] == "inf" else (n[1], n[2])


def fp_mul(p, a, b, m, P):
    E1 = Curve(p, a, b, 1)
    n = E1.normalize(E1.mul(m, (P[0], P[1], 1)), 1)
    return None if n[0] == "inf" else (n[1], n[2])


# ----------------------------------------------------------------- reading B
def s_tor_F1(E: Curve, n: int, P_hat):
    m = pow(n, -1, E.p ** K_SPEC)
    return E.sub(P_hat, E.mul(m, E.mul(n, P_hat)))


def s_tor_F2(E: Curve, N: int, P_hat):
    k1 = K_SPEC - 1
    e = E.p ** k1 * pow(E.p ** k1, -1, N)
    assert e % N == 1 and e % E.p ** k1 == 0
    return E.mul(e, P_hat)


def s_tor_point(p, a, b, N, n, x0, y0, r=0, method="F1"):
    """Public helper: normalized s_tor(P) mod p^4 for P = (x0, y0)."""
    E = Curve(p, a, b, K_SPEC)
    Ph = E.hensel_lift(x0, y0, r)
    S = s_tor_F1(E, n, Ph) if method == "F1" else s_tor_F2(E, N, Ph)
    return E.normalize(S)


def reading_B(rng):
    rows = []
    for p in primes_1mod3():
        for B in twist_reps(p):
            N = count_points(p, 0, B)
            if N % 2 == 0 or N % p == 0:
                continue
            big = [q for q in set(prime_factors(N)) if q >= 11 and q != p]
            if not big:
                continue
            n = max(big)
            E1 = Curve(p, 0, B, 1)
            e_n, Nn = 0, N
            while Nn % n == 0:
                Nn //= n
                e_n += 1
            # cofactor clears the prime-to-n part; then step down to exact order n
            # (handles a non-cyclic n-Sylow, e.g. E(F_p) = (Z/n)^2)
            while True:
                R = random_affine_point(p, 0, B, rng)
                Pp = E1.mul(Nn, (R[0], R[1], 1))
                if E1.is_O(Pp, 1):
                    continue
                while not E1.is_O(E1.mul(n, Pp), 1):
                    Pp = E1.mul(n, Pp)
                Pn = E1.normalize(Pp, 1)
                P = (Pn[1], Pn[2])
                break
            E = Curve(p, 0, B, K_SPEC)
            r2 = rng.randrange(1, p ** (K_SPEC - 1))
            starts = [E.hensel_lift(*P, 0), E.hensel_lift(*P, r2)]
            E.ops = 0
            S1 = s_tor_F1(E, n, starts[0])
            cost_F1 = E.ops
            S1b = s_tor_F1(E, n, starts[1])
            S2 = s_tor_F2(E, N, starts[0])
            S2b = s_tor_F2(E, N, starts[1])
            norms = [E.normalize(S) for S in (S1, S1b, S2, S2b)]
            canonical = all(x == norms[0] for x in norms)
            nS = E.mul(n, S1)
            deg = E.is_O(nS)
            z_nS = E.z(nS)
            v_z_nS = vp(z_nS, p, K_SPEC)
            pS = E.mul(p, S1)
            Yu = E.unit(pS[1])
            v_z_pS_literal = vp(E.z(pS), p, K_SPEC) if Yu else None
            pS_in_formal_group = E.normalize(pS)[0] == "inf" and E.normalize(pS, 1) == ("inf", 0, 0)
            reduces = E.normalize(S1, 1) == ("aff", P[0], P[1])
            # Smart functional on the Hensel section (information only)
            v_z_nPh = [vp(E.z(E.mul(n, Ph)), p, K_SPEC) for Ph in starts]
            # homomorphism on random pairs
            hom_ok, hom_n = 0, 0
            for _ in range(PAIRS):
                d = rng.randrange(2, n - 1)
                Q = fp_mul(p, 0, B, d, P)
                PQ = fp_add(p, 0, B, P, Q)
                if Q is None or PQ is None:
                    continue
                sP = s_tor_F1(E, n, E.hensel_lift(*P, rng.randrange(p ** 3)))
                sQ = s_tor_F1(E, n, E.hensel_lift(*Q, rng.randrange(p ** 3)))
                sPQ = s_tor_F1(E, n, E.hensel_lift(*PQ, rng.randrange(p ** 3)))
                hom_n += 1
                hom_ok += E.eq(E.add(sP, sQ), sPQ)
            bound = 2 * ((n).bit_length() + (p ** K_SPEC).bit_length()) + 1
            rows.append({
                "p": p, "B": B, "N": N, "n": n, "n_sylow_exponent": e_n,
                "P": list(P), "r_start2": r2,
                "s_tor_F1_start1": list(norms[0]),
                "s_tor_F1_start2": list(norms[1]),
                "s_tor_F2_start1": list(norms[2]),
                "s_tor_F2_start2": list(norms[3]),
                "canonical_4way": canonical,
                "n_s_tor_is_O_mod_p4": deg,
                "v_p_z_n_s_tor": v_z_nS,
                "z_n_s_tor_mod_p4": z_nS % p ** K_SPEC,
                "literal_v_p_z_p_s_tor": v_z_pS_literal,
                "literal_p_s_tor_in_formal_group": pS_in_formal_group,
                "s_tor_reduces_to_P": reduces,
                "v_p_z_n_Phat_starts": v_z_nPh,
                "homomorphism_pairs_ok": hom_ok, "homomorphism_pairs": hom_n,
                "cost_F1_additions": cost_F1, "cost_bound": bound,
                "cost_within_bound": cost_F1 <= bound,
            })
    return rows


# ----------------------------------------------------------------- reading A
def T_section(E: Curve, P_hat):
    """p-torsion lift: T = P^ - tau, z(tau) = z([p]P^)/p. Needs v(z([p]P^)) >= 2."""
    p = E.p
    R = E.mul(p, P_hat)
    assert E.normalize(R, 1) == ("inf", 0, 0), "[p]P^ not in E^1"
    zR = E.z(R)
    v = vp(zR, p, E.K)
    if v < 2:
        return None, v
    tau = E.point_from_z(zR // p)
    return E.sub(P_hat, tau), v


def reading_A(rng):
    rows = []
    for p in primes_1mod3():
        Bs = [B for B in twist_reps(p) if count_points(p, 0, B) == p]
        for B in Bs:
            P = random_affine_point(p, 0, B, rng)  # order p (E(F_p) = Z/p)
            out = {"p": p, "B": B, "N": p, "P": list(P)}
            try:
                pow(p, -1, p ** K_SPEC)
                out["spec_formula_defined"] = True
            except ValueError:
                out["spec_formula_defined"] = False
            res = {}
            for K in (K_SPEC + 1, K_SPEC + 2):
                E = Curve(p, 0, B, K)
                r2 = rng.randrange(1, p ** (K - 1))
                starts = [E.hensel_lift(*P, 0), E.hensel_lift(*P, r2)]
                Ts, vs = [], []
                for Ph in starts:
                    T, v = T_section(E, Ph)
                    Ts.append(T)
                    vs.append(v)
                if any(T is None for T in Ts):
                    res[K] = {"v_p_z_p_Phat_starts": vs, "split": False}
                    continue
                norms = [E.normalize(T, K_SPEC) for T in Ts]
                pT = E.mul(p, Ts[0])
                hom_ok, hom_n = 0, 0
                for _ in range(PAIRS):
                    d = rng.randrange(2, p - 1)
                    Q = fp_mul(p, 0, B, d, P)
                    PQ = fp_add(p, 0, B, P, Q)
                    if Q is None or PQ is None:
                        continue
                    tP, _ = T_section(E, E.hensel_lift(*P, rng.randrange(p ** 3)))
                    tQ, _ = T_section(E, E.hensel_lift(*Q, rng.randrange(p ** 3)))
                    tPQ, _ = T_section(E, E.hensel_lift(*PQ, rng.randrange(p ** 3)))
                    hom_n += 1
                    hom_ok += E.eq(E.add(tP, tQ), tPQ, K_SPEC)
                res[K] = {
                    "split": True,
                    "v_p_z_p_Phat_starts": vs,
                    "T_start1_mod_p4": list(norms[0]),
                    "T_start2_mod_p4": list(norms[1]),
                    "canonical_2starts": norms[0] == norms[1],
                    "p_T_is_O_mod_pK": E.is_O(pT),
                    "p_T_is_O_mod_p4": E.is_O(pT, K_SPEC),
                    "v_p_z_p_T": vp(E.z(pT), p, K),
                    "T_reduces_to_P": E.normalize(Ts[0], 1) == ("aff", P[0], P[1]),
                    "homomorphism_pairs_ok": hom_ok, "homomorphism_pairs": hom_n,
                }
            out["by_working_precision"] = {str(K): v for K, v in res.items()}
            out["T_stable_K5_vs_K6"] = (
                res.get(K_SPEC + 1, {}).get("T_start1_mod_p4")
                == res.get(K_SPEC + 2, {}).get("T_start1_mod_p4")
            )
            # control: non-canonical lift y^2 = x^3 + p c x + B
            ctrl = []
            for _ in range(4):
                c = rng.randrange(1, p)
                E = Curve(p, p * c, B, K_SPEC + 1)
                Ph = E.hensel_lift(*P, rng.randrange(p ** 3))
                ctrl.append({"a": p * c, "v_p_z_p_Phat": vp(E.z(E.mul(p, Ph)), p, E.K)})
            out["noncanonical_lift_control"] = ctrl
            rows.append(out)
    return rows


def main():
    rng = random.Random(SEED)
    st = self_test()
    A = reading_A(rng)
    Bv = reading_B(rng)
    primary_A = [r["p"] for r in A][:2]
    primary_B = [Bv[0]["p"], Bv[-1]["p"]] if Bv else []
    summary = {
        "statement_finding": (
            "Statement asks for anomalous primes; the specification requires a prime "
            "subgroup n != p and excludes anomalous curves, so the spec's s_tor formula is "
            "undefined there. Both readings computed."),
        "self_test": st,
        "reading_A": {
            "primes": [r["p"] for r in A],
            "primary_two": primary_A,
            "spec_formula_defined_any": any(r["spec_formula_defined"] for r in A),
            "all_split_canonical_lift": all(r["by_working_precision"]["5"]["split"] for r in A),
            "all_canonical_2starts": all(r["by_working_precision"]["5"].get("canonical_2starts") for r in A),
            "all_p_T_is_O": all(r["by_working_precision"]["5"].get("p_T_is_O_mod_p4") for r in A),
            "all_homomorphism": all(r["by_working_precision"]["5"].get("homomorphism_pairs_ok")
                                    == r["by_working_precision"]["5"].get("homomorphism_pairs") for r in A),
            "v_p_z_p_T_min": min(r["by_working_precision"]["5"].get("v_p_z_p_T", -1) for r in A),
            "v_p_z_p_Phat_canonical_min": min(min(r["by_working_precision"]["5"]["v_p_z_p_Phat_starts"]) for r in A),
            "v_p_z_p_Phat_noncanonical": sorted({c["v_p_z_p_Phat"] for r in A for c in r["noncanonical_lift_control"]}),
            "T_stable_K5_vs_K6_all": all(r["T_stable_K5_vs_K6"] for r in A),
        },
        "reading_B": {
            "curves": len(Bv),
            "primes": sorted({r["p"] for r in Bv}),
            "primary_two": primary_B,
            "all_canonical_4way": all(r["canonical_4way"] for r in Bv),
            "all_n_s_tor_is_O": all(r["n_s_tor_is_O_mod_p4"] for r in Bv),
            "min_v_p_z_n_s_tor": min(r["v_p_z_n_s_tor"] for r in Bv),
            "all_reduce_to_P": all(r["s_tor_reduces_to_P"] for r in Bv),
            "homomorphism_ok_over_total": [sum(r["homomorphism_pairs_ok"] for r in Bv),
                                           sum(r["homomorphism_pairs"] for r in Bv)],
            "literal_v_p_z_p_s_tor_values": sorted({str(r["literal_v_p_z_p_s_tor"]) for r in Bv}),
            "literal_p_s_tor_in_formal_group_any": any(r["literal_p_s_tor_in_formal_group"] for r in Bv),
            "v_p_z_n_Phat_hist": {str(v): sum(1 for r in Bv for x in r["v_p_z_n_Phat_starts"] if x == v)
                                  for v in sorted({x for r in Bv for x in r["v_p_z_n_Phat_starts"]})},
            "cost_F1_mean": sum(r["cost_F1_additions"] for r in Bv) / len(Bv),
            "cost_F1_max": max(r["cost_F1_additions"] for r in Bv),
            "cost_all_within_bound": all(r["cost_within_bound"] for r in Bv),
        },
    }
    out = {"seed": SEED, "k": K_SPEC, "summary": summary, "reading_A": A, "reading_B": Bv}
    here = Path(__file__).resolve().parent
    (here / "blind_output.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
