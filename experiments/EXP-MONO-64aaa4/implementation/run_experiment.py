#!/usr/bin/env python3
"""
EXP-MONO-64aaa4: Matched-(N,tau) CM-vs-ordinary m=4 root-multiplicity
collision-rate comparison.

Implements experiments/EXP-MONO-64aaa4/specification.yaml exactly, per the
frozen contract. See implementation.md for the disclosed interpretation of
the "admissible 4-tuple" / "2^(m-2)=4 sign classes" text: this code draws
(m-1)=3 distinct factor-base x-coordinates per tuple and forms the 4
sign-classes eps in {(+,+,+),(+,+,-),(+,-,+),(+,-,-)} (eps_1 fixed +1,
canonical mod global sign flip), because that is the unique construction
consistent with H-MONO-45183a B-1/B-2's own unmodified combinatorics
(index set {1,2,3} for m=4, group (Z/2)^{m-2} of order 4, ALL C(4,2)=6
class-pairs of branch type (1,2) each with forced probability (tau-1)/N,
summing to exactly 6(tau-1)/N) -- the exact frozen prediction this run must
independently reproduce as Stage 1's hard gate.

No hypothesis/experiment/goal status is changed by this script. This
script performs measurement only.
"""
import hashlib
import json
import sys
import time
from fractions import Fraction

DOMAIN = "EXP-MONO-64aaa4/v1"
PRIME_LO = 101
PRIME_HI = 3000
NTUPLES = 20000
M = 4  # arity under test
NCLASSES = 4  # 2^(M-2)
NPAIRS = 6  # C(4,2)

SIGN_CLASSES = [
    (1, 1, 1),
    (1, 1, -1),
    (1, -1, 1),
    (1, -1, -1),
]


def seed_bytes(label, p, role, draw_index, counter):
    s = f"{DOMAIN}|{label}|{p}|{role}|{draw_index}|{counter}"
    return hashlib.sha256(s.encode("ascii")).digest()


def draw_uniform(label, p, role, draw_index, counter_start, modulus):
    """Rejection-sampled uniform draw in [0, modulus) per the contract's
    seed_derivation_rule ('rejection sampling against modulo bias').
    Returns (value, next_counter)."""
    limit = (2**256 // modulus) * modulus
    c = counter_start
    while True:
        d = seed_bytes(label, p, role, draw_index, c)
        v = int.from_bytes(d, "big")
        c += 1
        if v < limit:
            return v % modulus, c


def is_prime(n):
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def primes_in_range(lo, hi):
    return [p for p in range(lo, hi + 1) if is_prime(p)]


def quad_char(a, p):
    """Legendre symbol chi(a) in {-1,0,1} mod p (p odd prime)."""
    a %= p
    if a == 0:
        return 0
    r = pow(a, (p - 1) // 2, p)
    return 1 if r == 1 else -1


def count_points(A, B, p):
    """#E(F_p) = 1 + sum_{x=0}^{p-1} (1 + chi(x^3+Ax+B)), chi(0)=0."""
    total = 1
    for x in range(p):
        f = (x * x * x + A * x + B) % p
        total += 1 + quad_char(f, p)
    return total


def two_torsion_count(A, B, p):
    """tau = #E(F_p)[2] = (# roots of x^3+Ax+B mod p) + 1."""
    roots = 0
    for x in range(p):
        f = (x * x * x + A * x + B) % p
        if f == 0:
            roots += 1
    return roots + 1


def is_singular(A, B, p):
    disc = (4 * pow(A, 3, p) + 27 * pow(B, 2, p)) % p
    return disc == 0


def j_invariant(A, B, p):
    num = (1728 * 4 * pow(A, 3, p)) % p
    den = (4 * pow(A, 3, p) + 27 * pow(B, 2, p)) % p
    if den == 0:
        return None
    return (num * pow(den, p - 2, p)) % p


def construct_ordinary(p, max_t=65536):
    for t in range(max_t):
        a_digest = seed_bytes("curve-a", p, "ord", 0, t)
        b_digest = seed_bytes("curve-b", p, "ord", 0, t)
        A = int.from_bytes(a_digest, "big") % p
        B = int.from_bytes(b_digest, "big") % p
        if is_singular(A, B, p):
            continue
        if A == 0 or B == 0:
            continue  # reject j=0 or j=1728
        N = count_points(A, B, p)
        if N % p == 1:
            continue  # not ordinary (supersingular criterion at toy p: N == 1 mod p)
        tau = two_torsion_count(A, B, p)
        return {"p": p, "A": A, "B": B, "N": N, "tau": tau, "role": "ord",
                "trials": t + 1, "j": None}
    return None


def construct_cm_j0(p, max_t=65536):
    """A=0, B = first accepted value of the b-stream, role 'cm', rejecting B=0."""
    for t in range(max_t):
        b_digest = seed_bytes("curve-b", p, "cm", 0, t)
        B = int.from_bytes(b_digest, "big") % p
        if B == 0:
            continue
        A = 0
        if is_singular(A, B, p):
            continue
        N = count_points(A, B, p)
        tau = two_torsion_count(A, B, p)
        return {"p": p, "A": A, "B": B, "N": N, "tau": tau, "role": "cm",
                "trials": t + 1, "j": 0}
    return None


def construct_cm_j1728(p, max_t=65536):
    """B=0, A = first accepted value of the a-stream, role 'cm', rejecting A=0."""
    for t in range(max_t):
        a_digest = seed_bytes("curve-a", p, "cm", 0, t)
        A = int.from_bytes(a_digest, "big") % p
        if A == 0:
            continue
        B = 0
        if is_singular(A, B, p):
            continue
        N = count_points(A, B, p)
        tau = two_torsion_count(A, B, p)
        return {"p": p, "A": A, "B": B, "N": N, "tau": tau, "role": "cm",
                "trials": t + 1, "j": 1728}
    return None


def ec_neg(P, p):
    if P is None:
        return None
    x, y = P
    return (x, (-y) % p)


def ec_add(P, Q, A, p):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None  # point at infinity
        lam = ((3 * x1 * x1 + A) * pow((2 * y1) % p, p - 2, p)) % p
    else:
        lam = ((y2 - y1) * pow((x2 - x1) % p, p - 2, p)) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3 % p, y3 % p)


def sqrt_mod_p(a, p):
    """Both square roots of a (a must be a nonzero QR mod p, p odd).
    Returns (small, large) with small < large, small+large = p."""
    a %= p
    # p is a toy-scale prime; brute-force is fine and avoids Tonelli-Shanks bugs.
    for y in range(1, (p // 2) + 1):
        if (y * y) % p == a:
            other = (p - y) % p
            return (min(y, other), max(y, other))
    raise ValueError("no square root found (should not happen for a factor-base x)")


def build_factor_base(A, B, p):
    fb = []
    excluded_zero = 0
    for x in range(p):
        f = (x * x * x + A * x + B) % p
        if f == 0:
            excluded_zero += 1
            continue
        if quad_char(f, p) == 1:
            fb.append(x)
    digest = hashlib.sha256(",".join(map(str, fb)).encode("ascii")).hexdigest()
    return {"fb": fb, "size": len(fb), "digest": digest, "excluded_zero": excluded_zero}


def point_for_x(x, A, B, p, sign_bit):
    """sign_bit in {0,1}: 0 -> smaller root, 1 -> larger root."""
    f = (x * x * x + A * x + B) % p
    small, large = sqrt_mod_p(f, p)
    y = small if sign_bit == 0 else large
    return (x, y)


def measure_curve(curve, fb_info, ntuples, arm, budget_deadline=None):
    """arm in {'fixed', 'random'}.
    Returns dict with per-tuple pair-collision counts and per-tuple
    any-collision indicator, plus raw counts."""
    A, B, p, role = curve["A"], curve["B"], curve["p"], curve["role"] + str(curve.get("j"))
    fb = fb_info["fb"]
    nfb = len(fb)
    if nfb < 3:
        raise RuntimeError(f"factor base too small (size={nfb}) at p={p}")

    total_pairs_colliding = 0
    tuples_with_collision = 0
    counter_cursor = {}  # per tuple_id running counter, but we recompute fresh each tuple

    for tid in range(ntuples):
        counter = 0
        chosen = []
        # draw 3 distinct factor-base indices
        while len(chosen) < 3:
            idx, counter = draw_uniform("fb-x", p, role, tid, counter, nfb)
            if idx not in chosen:
                chosen.append(idx)
        xs = [fb[i] for i in chosen]

        if arm == "fixed":
            sign_bits = [0, 0, 0]
        else:
            sign_bits = []
            for _ in range(3):
                b, counter = draw_uniform("fb-x", p, role, tid, counter, 2)
                sign_bits.append(b)

        pts = [point_for_x(xs[k], A, B, p, sign_bits[k]) for k in range(3)]

        # 4 signed-sum classes: eps_1 fixed +1
        sums = []
        for eps in SIGN_CLASSES:
            acc = None
            for k in range(3):
                term = pts[k] if eps[k] == 1 else ec_neg(pts[k], p)
                acc = ec_add(acc, term, A, p)
            # represent x-coordinate; infinity gets sentinel "INF"
            xval = "INF" if acc is None else acc[0]
            sums.append(xval)

        collisions_this_tuple = 0
        for i in range(NCLASSES):
            for j in range(i + 1, NCLASSES):
                if sums[i] == sums[j]:
                    collisions_this_tuple += 1
        total_pairs_colliding += collisions_this_tuple
        if collisions_this_tuple > 0:
            tuples_with_collision += 1

        if budget_deadline is not None and tid % 2000 == 0 and time.time() > budget_deadline:
            raise TimeoutError(f"budget deadline exceeded during measurement at tuple {tid}")

    return {
        "ntuples": ntuples,
        "total_pairs_colliding": total_pairs_colliding,
        "tuples_with_collision": tuples_with_collision,
        "rate_pairs_per_tuple": total_pairs_colliding / ntuples,
        "rate_any_collision": tuples_with_collision / ntuples,
    }


def predicted_rate(tau, N):
    if tau == 1:
        return 0.0
    return NPAIRS * (tau - 1) / N


def binomial_se_pairs(tau, N, ntuples):
    """SE for total colliding pairs over ntuples*NPAIRS approx-independent
    Bernoulli(  (tau-1)/N ) trials (0 if tau==1)."""
    p_pair = 0.0 if tau == 1 else (tau - 1) / N
    n_trials = ntuples * NPAIRS
    var = n_trials * p_pair * (1 - p_pair)
    return var ** 0.5


def fisher_exact_2x2(a, b, c, d):
    from scipy.stats import fisher_exact
    table = [[a, b], [c, d]]
    odds_ratio, p_value = fisher_exact(table)
    return odds_ratio, p_value


def main():
    t_start = time.time()
    hard_deadline = t_start + 3600
    stage0_soft_deadline = t_start + 1800

    result = {
        "run": "RUN-MONO-64aaa4-1",
        "seed": 20260901,
        "prime_range": [PRIME_LO, PRIME_HI],
        "stage0": {},
        "stage1": {},
        "stage2": {},
        "stage3": {},
        "status": None,
        "timing": {},
    }

    # ---------------- STAGE 0: matched-(N,tau) pair search ----------------
    primes = primes_in_range(PRIME_LO, PRIME_HI)
    transcript = []
    matches = []  # list of dicts {p, N, tau, ord, cm}

    stage0_stopped_early = False
    stage0_last_prime = None
    for p in primes:
        stage0_last_prime = p
        if time.time() > stage0_soft_deadline:
            stage0_stopped_early = True
            break
        ordc = construct_ordinary(p)
        cm0 = construct_cm_j0(p)
        cm1728 = construct_cm_j1728(p)
        transcript.append({
            "p": p,
            "ord": None if ordc is None else {k: ordc[k] for k in ("A", "B", "N", "tau", "trials")},
            "cm_j0": None if cm0 is None else {k: cm0[k] for k in ("A", "B", "N", "tau", "trials")},
            "cm_j1728": None if cm1728 is None else {k: cm1728[k] for k in ("A", "B", "N", "tau", "trials")},
        })
        if ordc is None:
            continue
        for cm, label in ((cm0, "j0"), (cm1728, "j1728")):
            if cm is None:
                continue
            if ordc["N"] == cm["N"] and ordc["tau"] == cm["tau"]:
                matches.append({
                    "p": p, "N": ordc["N"], "tau": ordc["tau"],
                    "ord": ordc, "cm": cm, "cm_variant": label,
                })

    result["stage0"]["primes_scanned"] = len(transcript)
    result["stage0"]["last_prime_scanned"] = stage0_last_prime
    result["stage0"]["stopped_early_on_soft_deadline"] = stage0_stopped_early
    result["stage0"]["num_matches_found"] = len(matches)
    result["stage0"]["matches"] = [
        {"p": m["p"], "N": m["N"], "tau": m["tau"], "cm_variant": m["cm_variant"],
         "ord": {k: m["ord"][k] for k in ("A", "B", "N", "tau", "trials")},
         "cm": {k: m["cm"][k] for k in ("A", "B", "N", "tau", "trials")}}
        for m in matches
    ]
    result["timing"]["stage0_seconds"] = time.time() - t_start

    if not matches:
        result["status"] = "no_matched_pair_found"
        result["stage0"]["transcript_note"] = (
            "No matched (N,tau) pair found within the declared range "
            f"[{PRIME_LO},{PRIME_HI}] (or within the scanned prefix if the "
            "1800s soft deadline triggered early termination -- see "
            "stopped_early_on_soft_deadline)."
        )
        write_transcript(transcript)
        return finalize(result, t_start)

    # Primary pair = smallest-p match; replication pair = next match, if any.
    primary = matches[0]
    replication = matches[1] if len(matches) > 1 else None

    # ---------------- STAGE 1 + STAGE 2 for the primary pair ----------------
    def run_stage_1_and_2(pair, tag):
        p = pair["p"]
        ordc = pair["ord"]
        cm = pair["cm"]
        tau = pair["tau"]
        N = pair["N"]

        fb_ord = build_factor_base(ordc["A"], ordc["B"], p)
        fb_cm = build_factor_base(cm["A"], cm["B"], p)

        stage1 = {"p": p, "N": N, "tau": tau, "predicted_rate": predicted_rate(tau, N)}
        stage1["factor_base_ord"] = {"size": fb_ord["size"], "digest": fb_ord["digest"]}
        stage1["factor_base_cm"] = {"size": fb_cm["size"], "digest": fb_cm["digest"]}
        stage1["construction_transcript"] = {
            "ord": {
                "p": p, "A": ordc["A"], "B": ordc["B"], "N": N, "tau": tau,
                "j_invariant": j_invariant(ordc["A"], ordc["B"], p),
                "n1_nonzero_squares": fb_ord["size"],
                "n2_nonzero_nonsquares": p - fb_ord["excluded_zero"] - fb_ord["size"],
                "role": "ordinary",
            },
            "cm": {
                "p": p, "A": cm["A"], "B": cm["B"], "N": N, "tau": tau,
                "j_invariant": j_invariant(cm["A"], cm["B"], p),
                "n1_nonzero_squares": fb_cm["size"],
                "n2_nonzero_nonsquares": p - fb_cm["excluded_zero"] - fb_cm["size"],
                "role": f"cm_{pair['cm_variant']}",
            },
        }

        curve_ord = dict(ordc)
        curve_ord["role"] = "ord"
        curve_ord["j"] = None
        curve_cm = dict(cm)
        curve_cm["role"] = "cm"
        curve_cm["j"] = pair["cm_variant"]

        measurements = {}
        for curve, cname in ((curve_ord, "ord"), (curve_cm, "cm")):
            fb_info = fb_ord if cname == "ord" else fb_cm
            for arm in ("fixed", "random"):
                key = f"{cname}_{arm}"
                measurements[key] = measure_curve(
                    curve, fb_info, NTUPLES, arm,
                    budget_deadline=hard_deadline - 30,
                )

        se_pairs = binomial_se_pairs(tau, N, NTUPLES)
        stage1["se_pairs_per_20000"] = se_pairs
        stage1_pass = True
        stage1_detail = {}
        for cname in ("ord", "cm"):
            for arm in ("fixed", "random"):
                key = f"{cname}_{arm}"
                m = measurements[key]
                pred = stage1["predicted_rate"]
                observed_pairs = m["total_pairs_colliding"]
                expected_pairs = pred * NTUPLES
                if tau == 1:
                    ok = observed_pairs == 0
                    reason = "exact-zero required (tau=1)"
                else:
                    ok = abs(observed_pairs - expected_pairs) <= 3 * se_pairs
                    reason = f"within 3 SE ({se_pairs:.4f}) of expected {expected_pairs:.4f}"
                stage1_detail[key] = {
                    "observed_total_pairs_colliding": observed_pairs,
                    "observed_rate_pairs_per_tuple": m["rate_pairs_per_tuple"],
                    "observed_tuples_with_any_collision": m["tuples_with_collision"],
                    "observed_rate_any_collision": m["rate_any_collision"],
                    "expected_pairs": expected_pairs,
                    "pass": bool(ok),
                    "reason": reason,
                }
                stage1_pass = stage1_pass and ok

        stage1["per_curve_arm"] = stage1_detail
        stage1["pass"] = stage1_pass

        stage2 = {"note": None}
        if stage1_pass:
            if tau == 1:
                for arm in ("fixed", "random"):
                    ord_zero = measurements[f"ord_{arm}"]["total_pairs_colliding"] == 0
                    cm_zero = measurements[f"cm_{arm}"]["total_pairs_colliding"] == 0
                    stage2[arm] = {
                        "comparison": "exact-zero check (tau=1)",
                        "ord_exactly_zero": ord_zero,
                        "cm_exactly_zero": cm_zero,
                        "agree": ord_zero and cm_zero,
                    }
            else:
                for arm in ("fixed", "random"):
                    ord_m = measurements[f"ord_{arm}"]
                    cm_m = measurements[f"cm_{arm}"]
                    a = ord_m["tuples_with_collision"]
                    b_ = ord_m["ntuples"] - a
                    c = cm_m["tuples_with_collision"]
                    d = cm_m["ntuples"] - c
                    odds_ratio, pvalue = fisher_exact_2x2(a, b_, c, d)
                    stage2[arm] = {
                        "comparison": "fisher_exact_2x2 on {collision, no-collision} outcomes, "
                                      "ord vs cm, 20000 tuples each",
                        "table": {"ord_collision": a, "ord_no_collision": b_,
                                  "cm_collision": c, "cm_no_collision": d},
                        "odds_ratio": odds_ratio,
                        "p_value": pvalue,
                        "significant_at_0.05": bool(pvalue < 0.05),
                        "ord_rate_any_collision": ord_m["rate_any_collision"],
                        "cm_rate_any_collision": cm_m["rate_any_collision"],
                        "ord_rate_pairs_per_tuple": ord_m["rate_pairs_per_tuple"],
                        "cm_rate_pairs_per_tuple": cm_m["rate_pairs_per_tuple"],
                    }
        else:
            stage2["note"] = "Stage 1 gate FAILED for this pair; Stage 2 not computed (per contract)."

        return stage1, stage2, measurements

    stage1_primary, stage2_primary, meas_primary = run_stage_1_and_2(primary, "primary")
    result["stage1"]["primary"] = stage1_primary
    result["stage2"]["primary"] = stage2_primary

    if not stage1_primary["pass"]:
        result["status"] = "failed_infrastructure"
        result["stage1"]["disposition"] = (
            "Stage 1 gate FAILED on the primary matched pair: at least one "
            "curve/arm did not reproduce its own G6/G7-predicted rate. Per "
            "contract, this implicates the implementation, NOT "
            "H-MONO-1d50ac's main claim. Stage 2 not computed for the "
            "primary pair."
        )
        write_transcript(transcript)
        return finalize(result, t_start)

    result["status"] = "completed_valid"

    # ---------------- STAGE 3: replication, if found and budget permits ----------------
    if replication is None:
        result["stage3"]["applicable"] = False
        result["stage3"]["reason"] = (
            "No second matched-(N,tau) pair was found within the declared "
            "search range; Stage 3 is not applicable."
        )
    else:
        remaining = hard_deadline - time.time()
        if remaining < 300:
            result["stage3"]["applicable"] = False
            result["stage3"]["reason"] = (
                f"A second matched pair was found (p={replication['p']}) but "
                f"only {remaining:.0f}s remained under the 3600s wall-clock "
                "budget after the primary pair's measurement -- insufficient "
                "for a second full 20000x2-arm x 2-curve measurement. "
                "Reported explicitly as a budget constraint, not executed."
            )
        else:
            stage1_rep, stage2_rep, meas_rep = run_stage_1_and_2(replication, "replication")
            result["stage3"]["applicable"] = True
            result["stage3"]["pair"] = {"p": replication["p"], "N": replication["N"],
                                         "tau": replication["tau"]}
            result["stage3"]["stage1"] = stage1_rep
            result["stage3"]["stage2"] = stage2_rep

    write_transcript(transcript)
    return finalize(result, t_start)


def write_transcript(transcript):
    out_path = "/Volumes/SSD990/crypto-autoresearcher/experiments/EXP-MONO-64aaa4/runs/RUN-MONO-64aaa4-1/stage0_transcript.json"
    with open(out_path, "w") as f:
        json.dump(transcript, f, indent=1)


def finalize(result, t_start):
    result["timing"]["total_seconds"] = time.time() - t_start
    return result


if __name__ == "__main__":
    try:
        res = main()
        print(json.dumps(res, indent=2))
    except TimeoutError as e:
        print(json.dumps({"status": "infrastructure_or_integrity_failure",
                           "error": "TimeoutError", "message": str(e)}, indent=2))
        sys.exit(2)
    except Exception as e:
        import traceback
        print(json.dumps({"status": "infrastructure_or_integrity_failure",
                           "error": type(e).__name__, "message": str(e),
                           "traceback": traceback.format_exc()}, indent=2))
        sys.exit(1)
