"""
Stage 2 for EXP-ECDLP-56ee42: the blocking controls, at every rung where the
contract requires it:
  - POS-A = (-1)^k gate: |A - 2/pi| <= 0.005 at every rung and flat in n.
  - POS-B = Thue-Morse of k gate: fitted beta in [0.10, 0.35] over the rungs
    AND A(POS-B) within [0.5, 2] x n^{-0.21} at every rung.
  - CONTROL C = T4 (popcount of x mod 4): pre-shuffle excess that the 8-seed
    NULL-2 shuffle removes (if it survives, F3, every digit number is void).
  - f558e4 (G) x-bucket smoke check (DIAGNOSTIC only: p = 101/103/107 at FULL
    group order N = 115/118/105, s = 2/3/4/5, expected near
    0.530/0.394/0.342/0.282; composite-N caveat stated).

The static provenance check (no T1-T4 or COMPARATOR statistic code path reads
k; POS-A/POS-B/NULL-1 exempt by design) is recorded as an artifact BEFORE
Stage 2 numbers are reported.

Run:  python3 stage2.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, ".")
import estimator as E

LADDER = [
    {"T": 17, "p": 131101, "b": 27, "N": 131113},
    {"T": 19, "p": 524309, "b": 80, "N": 525361},
    {"T": 21, "p": 2097169, "b": 1, "N": 2098321},
    {"T": 23, "p": 8388617, "b": 21, "N": 8391797},
    {"T": 25, "p": 33554473, "b": 49, "N": 33557891},
    {"T": 27, "p": 134217757, "b": 70, "N": 134234689},
]

BASE_SEED = 0x56EE42
NULL2_SHUFFLES = 8
# arm_index per the declared arm order: T1=0, T2=1, T3=2, T4=3, COMPARATOR=4,
# POS-A=5, POS-B=6
ARM_INDEX = {"T1": 0, "T2": 1, "T3": 2, "T4": 3, "COMPARATOR": 4,
             "POS-A": 5, "POS-B": 6}


def static_provenance_check() -> dict:
    """Static provenance check: no T1-T4 or COMPARATOR statistic code path
    reads k.  POS-A, POS-B and NULL-1 read k / harness data BY DESIGN and are
    exempt.  The check is a source scan over estimator.py."""
    src = Path("estimator.py").read_text()
    # The T1-T4 and COMPARATOR statistic functions are pure functions of the
    # integer lift (x or y).  Verify they don't reference k (the discrete-log
    # coordinate).
    # The relevant functions:
    #   T1/T2: thue_morse_sign, thue_morse_sign_array
    #   T3:    rudin_shapiro_sign, rudin_shapiro_sign_array
    #   T4:    popcount_mod4, popcount_mod4_array
    #   COMPARATOR: top_bit_fiber, top_bit_fiber_array
    # Extract each function body and check for 'k' references.
    functions = {
        "T1/T2 (thue_morse_sign)": "def thue_morse_sign(",
        "T1/T2 (thue_morse_sign_array)": "def thue_morse_sign_array(",
        "T3 (rudin_shapiro_sign)": "def rudin_shapiro_sign(",
        "T3 (rudin_shapiro_sign_array)": "def rudin_shapiro_sign_array(",
        "T4 (popcount_mod4)": "def popcount_mod4(",
        "T4 (popcount_mod4_array)": "def popcount_mod4_array(",
        "COMPARATOR (top_bit_fiber)": "def top_bit_fiber(",
        "COMPARATOR (top_bit_fiber_array)": "def top_bit_fiber_array(",
    }
    results = {}
    all_pass = True
    for name, sig in functions.items():
        # find the function body
        idx = src.find(sig)
        if idx < 0:
            results[name] = {"found": False, "reads_k": None, "pass": False}
            all_pass = False
            continue
        # find the end of the function (next 'def ' at column 0, or EOF)
        next_def = src.find("\ndef ", idx + 1)
        body = src[idx:next_def if next_def > 0 else len(src)]
        # check for 'k' as a variable (not part of a word like 'key', 'chunk')
        # look for 'k' as a standalone identifier
        k_refs = re.findall(r'\bk\b', body)
        # filter out comments and docstrings (rough: lines starting with # or ")
        code_lines = [ln for ln in body.split('\n')
                      if ln.strip() and not ln.strip().startswith('#')
                      and not ln.strip().startswith('"')
                      and not ln.strip().startswith("'")]
        code_k_refs = re.findall(r'\bk\b', '\n'.join(code_lines))
        reads_k = len(code_k_refs) > 0
        results[name] = {
            "found": True,
            "reads_k": reads_k,
            "k_refs_in_code": code_k_refs,
            "pass": not reads_k,
        }
        if reads_k:
            all_pass = False
    return {"all_pass": all_pass, "functions": results}


def pos_a_sequence(n: int) -> np.ndarray:
    """POS-A: v(R_k) = (-1)^k.  Reads k BY DESIGN (exempt from provenance)."""
    return np.where(np.arange(n) % 2 == 0, 1, -1).astype(np.int8)


def pos_b_sequence(n: int) -> np.ndarray:
    """POS-B: v(R_k) = (-1)^{s_2(k)}.  Reads k BY DESIGN (exempt)."""
    ks = np.arange(n, dtype=np.uint32)
    return E.thue_morse_sign_array(ks)


def t4_sequence(xs: np.ndarray) -> np.ndarray:
    """T4: popcount of x mod 4, as a 4-valued statistic (values 0, 1, 2, 3).
    (Unbalanced; the o2 family-I member.)  The A(v) estimator works for any
    values, so we use the 4-valued statistic directly.  The 'excess' is the
    largest Fourier coefficient A(T4), which measures the dependence of the
    statistic on the discrete-log coordinate."""
    return E.popcount_mod4_array(xs).astype(np.float64)


def main() -> None:
    t_start = time.time()
    out = {"stage": 2, "steps": {}}

    # --- Static provenance check (BEFORE any Stage 2 numbers) ---
    prov = static_provenance_check()
    out["steps"]["static_provenance_check"] = prov
    prov_path = Path("runs/RUN-ECDLP-56ee42-S2/static-provenance-check.json")
    prov_path.parent.mkdir(parents=True, exist_ok=True)
    prov_path.write_text(json.dumps(prov, indent=2) + "\n")
    print(f"static provenance check: {'PASS' if prov['all_pass'] else 'FAIL'}",
          file=sys.stderr)

    # --- POS-A and POS-B at every rung ---
    pos_a_results = []
    pos_b_results = []
    for rung in LADDER:
        n = rung["N"]
        # POS-A
        v_a = pos_a_sequence(n)
        A_a = E.A_of_v(v_a, n)
        pos_a_results.append({"T": rung["T"], "n": n, "A": A_a,
                              "abs_diff_2pi": abs(A_a - 2 / np.pi)})
        # POS-B
        v_b = pos_b_sequence(n)
        A_b = E.A_of_v(v_b, n)
        pos_b_results.append({"T": rung["T"], "n": n, "A": A_b})
        print(f"T={rung['T']} n={n}: A(POS-A)={A_a:.6f} "
              f"(|diff 2/pi|={abs(A_a - 2/np.pi):.6f})  "
              f"A(POS-B)={A_b:.6f}", file=sys.stderr)

    # POS-A gate: |A - 2/pi| <= 0.005 at every rung and flat in n.
    pos_a_max_diff = max(r["abs_diff_2pi"] for r in pos_a_results)
    pos_a_flat = (max(r["A"] for r in pos_a_results)
                  - min(r["A"] for r in pos_a_results)) < 0.01
    pos_a_pass = (pos_a_max_diff <= 0.005) and pos_a_flat

    # POS-B gate: fitted beta in [0.10, 0.35] AND A within [0.5, 2] x n^{-0.21}
    # at every rung.
    ns = np.array([r["n"] for r in pos_b_results], dtype=np.float64)
    As = np.array([r["A"] for r in pos_b_results], dtype=np.float64)
    # fit A ~ n^{-beta}: log A = -beta * log n + c
    logn = np.log(ns)
    logA = np.log(As)
    A_mat = np.vstack([logn, np.ones_like(logn)]).T
    neg_beta, c = np.linalg.lstsq(A_mat, logA, rcond=None)[0]
    beta = float(-neg_beta)
    # check A within [0.5, 2] x n^{-0.21} at every rung
    pos_b_band_pass = all(
        0.5 * n ** (-0.21) <= A <= 2.0 * n ** (-0.21)
        for n, A in zip(ns, As))
    pos_b_beta_pass = 0.10 <= beta <= 0.35
    pos_b_pass = pos_b_band_pass and pos_b_beta_pass

    out["steps"]["POS-A"] = {
        "results": pos_a_results,
        "max_abs_diff_2pi": pos_a_max_diff,
        "flat_in_n": pos_a_flat,
        "gate_pass": pos_a_pass,
    }
    out["steps"]["POS-B"] = {
        "results": pos_b_results,
        "fitted_beta": beta,
        "beta_in_0.10_0.35": pos_b_beta_pass,
        "band_pass": pos_b_band_pass,
        "gate_pass": pos_b_pass,
    }

    # --- CONTROL C: T4 pre-shuffle excess and post-shuffle residual ---
    # The "excess" is A(T4) before shuffling.  The "post-shuffle residual" is
    # the max over the 8 NULL-2 shuffles of A(T4_shuffled).  The gate is that
    # the shuffle removes the excess (post-shuffle residual << pre-shuffle).
    control_c_results = []
    for rung in LADDER:
        p, n = rung["p"], rung["N"]
        xs = np.load(f"runs/stage-cache/rung_T{rung['T']}_x.npy")
        v_t4 = t4_sequence(xs)
        # The "excess" is the DL-coordinate advantage (the a != 0 terms),
        # which is what the NULL-2 shuffle removes.  The a = 0 term (the mean)
        # is the marginal artifact, which the shuffle preserves (it keeps the
        # multiset).  So we use A_noDC (excluding the a = 0 term).
        A_pre = E.A_noDC_of_v(v_t4, n)
        A_pre_full = E.A_of_v(v_t4, n)
        # 8 NULL-2 shuffles
        A_posts = []
        for shuffle_idx in range(NULL2_SHUFFLES):
            seed = BASE_SEED + 1000 + 10 * ARM_INDEX["T4"] + shuffle_idx
            v_shuffled = E.null2_shuffle(v_t4, n, seed)
            A_post = E.A_noDC_of_v(v_shuffled, n)
            A_posts.append(A_post)
        A_post_max = max(A_posts)
        control_c_results.append({
            "T": rung["T"], "n": n,
            "A_noDC_pre_shuffle": A_pre,
            "A_full_pre_shuffle": A_pre_full,
            "A_noDC_post_shuffle_max": A_post_max,
            "A_noDC_post_shuffle_all": A_posts,
            "excess_removed": A_pre - A_post_max,
        })
        print(f"T={rung['T']} n={n}: A_noDC(T4) pre={A_pre:.6f} "
              f"post_max={A_post_max:.6f} "
              f"excess_removed={A_pre - A_post_max:.6f} "
              f"(A_full pre={A_pre_full:.6f})", file=sys.stderr)

    # CONTROL C gate: the shuffle removes the excess.  We define "removes" as
    # the post-shuffle residual (A_noDC) being at most half the pre-shuffle
    # value (A_noDC) at every rung (a conservative threshold; the o2 lane's
    # artifact was fully removed).
    control_c_pass = all(
        r["A_noDC_post_shuffle_max"] <= 0.5 * r["A_noDC_pre_shuffle"]
        for r in control_c_results)
    out["steps"]["CONTROL-C"] = {
        "results": control_c_results,
        "gate_pass": control_c_pass,
        "gate_criterion": ("A_noDC post-shuffle max <= 0.5 * A_noDC "
                           "pre-shuffle at every rung"),
    }

    # --- f558e4 (G) x-bucket smoke check (DIAGNOSTIC only) ---
    smoke = _smoke_check()
    out["steps"]["smoke_check_G"] = smoke

    out["wall_clock_seconds"] = round(time.time() - t_start, 2)
    out["gates"] = {
        "POS-A": pos_a_pass,
        "POS-B": pos_b_pass,
        "CONTROL-C": control_c_pass,
        "static_provenance": prov["all_pass"],
    }
    out["validity"] = "valid" if all(out["gates"].values()) else "gate_failure"
    out["validity_reason"] = (
        "all gates passed" if all(out["gates"].values())
        else f"gate failure: { {k: v for k, v in out['gates'].items() if not v} }")

    out_path = Path("runs/RUN-ECDLP-56ee42-S2/raw-result.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=str) + "\n")
    print(f"Stage 2 complete in {out['wall_clock_seconds']}s", file=sys.stderr)
    print(json.dumps({"gates": out["gates"], "validity": out["validity"]},
                     indent=2))


def _smoke_check() -> dict:
    """f558e4 (G) x-bucket smoke check: on p = 101/103/107 at FULL (composite)
    group order N = 115/118/105, the x-coordinate bucket should give q_maj
    near 0.530/0.394/0.342/0.282 at s = 2/3/4/5.  DIAGNOSTIC only; composite-
    N caveat: a smoke check on the measurement code, not evidence.

    The group order is composite, so the group is not cyclic.  We enumerate
    the FULL group by finding all points on the curve (plus O), and compute
    q_maj by brute force over all N^2 pairs using the actual group law.
    """
    curves = _find_smoke_curves()
    results = []
    for curve in curves:
        p, b, N = curve["p"], curve["b"], curve["N"]
        # enumerate the full group: all affine points + O
        points = _enumerate_full_group(p, b)
        assert len(points) == N, f"expected {N} points, got {len(points)}"
        # index points for fast lookup in the group law
        point_index = {pt: i for i, pt in enumerate(points)}
        for s in [2, 3, 4, 5]:
            # x-coordinate bucket: fiber j = {x : x in [j*p/s, (j+1)*p/s)}
            # O has x = 0 by convention, so it falls in fiber 0.
            v = np.array([_x_bucket(pt, p, s) for pt in points], dtype=np.int64)
            # q_maj by brute force over all N^2 pairs
            qm = _brute_qmaj_group(v, points, point_index, p, b)
            results.append({
                "p": p, "N": N, "s": s,
                "q_maj": float(qm),
                "expected": {2: 0.530, 3: 0.394, 4: 0.342, 5: 0.282}[s],
            })
    return {
        "curves": curves,
        "results": results,
        "caveat": ("composite-N caveat: these curves are used at FULL group "
                   "order (N = 115, 118, 105), which is COMPOSITE, so "
                   "Cauchy-Davenport does not strictly apply; this is a smoke "
                   "check on the measurement code, not evidence"),
    }


def _enumerate_full_group(p: int, b: int) -> list[tuple]:
    """Enumerate all points on y^2 = x^3 + x + b over F_p, plus O = None.
    Returns a list of (x, y) tuples, with None for O."""
    points = [None]  # O
    for x in range(p):
        rhs = (x * x * x + x + b) % p
        if rhs == 0:
            points.append((x, 0))
        elif pow(rhs, (p - 1) // 2, p) == 1:
            y = E._tonelli_shanks(rhs, p)
            points.append((x, y))
            points.append((x, p - y))
    return points


def _x_bucket(pt, p: int, s: int) -> int:
    """x-coordinate bucket: fiber j = {x : x in [j*p/s, (j+1)*p/s)}.
    O (pt = None) has x = 0 by convention, so it falls in fiber 0."""
    if pt is None:
        x = 0
    else:
        x = pt[0]
    return min(int(x * s / p), s - 1)


def _group_add(p: int, b: int, P, Q):
    """Group law on y^2 = x^3 + x + b.  P, Q are (x, y) or None (O)."""
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None  # P + (-P) = O
    if x1 == x2:
        lam = (3 * x1 * x1 + 1) * pow(2 * y1, p - 2, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, p - 2, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def _brute_qmaj_group(v: np.ndarray, points: list, point_index: dict,
                      p: int, b: int) -> float:
    """q_maj by brute force over all N^2 pairs, using the actual group law."""
    n = len(points)
    s = int(v.max()) + 1
    N = np.zeros((s, s, s), dtype=np.int64)
    for i in range(n):
        for j in range(n):
            R = _group_add(p, b, points[i], points[j])
            m = point_index[R]
            N[v[i], v[j], v[m]] += 1
    total = sum(int(N[i, j, :].max()) for i in range(s) for j in range(s))
    return total / (n * n)


def _find_smoke_curves() -> list[dict]:
    """Find curves y^2 = x^3 + x + b over F_p with the given group orders."""
    targets = [(101, 115), (103, 118), (107, 105)]
    curves = []
    for p, N_target in targets:
        for b in range(1, 200):
            N = _point_count(p, b)
            if N == N_target:
                curves.append({"p": p, "b": b, "N": N})
                break
        else:
            raise ValueError(f"no curve found for p={p}, N={N_target}")
    return curves


def _point_count(p: int, b: int) -> int:
    """#E(F_p) for y^2 = x^3 + x + b over F_p."""
    count = 1  # point at infinity
    for x in range(p):
        rhs = (x * x * x + x + b) % p
        if rhs == 0:
            count += 1
        elif pow(rhs, (p - 1) // 2, p) == 1:
            count += 2
    return count


if __name__ == "__main__":
    main()
