#!/usr/bin/env python3
"""EXP-MONO-a20e48 run driver.

Usage: python3 run_experiment.py <master_seed> <output_dir>

Executes Stage 0-4 of the frozen contract for one replication run (one
master seed -> one domain suffix "run-<seed>"), and writes the full set of
required artifacts into <output_dir>.
"""
from __future__ import annotations

import json
import math
import sys
import time

import fieldext as fe
import fieldpoly as fp
import battery as bt
import seed as sd
import tower

P = 211
C = 2
DOMAIN_BASE = "EXP-MONO-a20e48/v1"


# ---------------------------------------------------------------------
# Stage 0
# ---------------------------------------------------------------------

def is_prime_trial(n: int) -> bool:
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


def stage0(p: int, c: int):
    t0 = time.time()
    prime_ok = is_prime_trial(p)
    odd_ok = (p % 2 == 1)
    mod3 = p % 3
    mod8 = p % 8
    mod3_ok = (mod3 == 1)
    two_is_qr = pow(2, (p - 1) // 2, p)  # +1 if QR, p-1 if non-residue
    two_nonsquare = (two_is_qr == p - 1)
    two_cube_test = pow(2, (p - 1) // 3, p)
    two_noncube = (two_cube_test != 1)
    c_is_2 = (c == 2)

    m_k_search = {}
    fields = {}
    for k in [1, 2, 3, 4]:
        mk = fe.find_m_k(p, k)
        m_k_search[k] = mk
        fields[k] = fe.FpK(p, k, mk)

    # k=1 sqrt cross-check against fp_common.sqrt_mod (ported inline, no
    # cross-experiment import -- self-contained port of the same classic
    # Tonelli-Shanks algorithm, used ONLY as the cross-check reference).
    def fp_common_sqrt_mod(a, p):
        a %= p
        if a == 0:
            return 0

        def legendre(a, p):
            a %= p
            if a == 0:
                return 0
            r = pow(a, (p - 1) // 2, p)
            return -1 if r == p - 1 else r

        if legendre(a, p) != 1:
            return None
        if p % 4 == 3:
            return pow(a, (p + 1) // 4, p)
        q, s = p - 1, 0
        while q % 2 == 0:
            q //= 2
            s += 1
        z = 2
        while legendre(z, p) != -1:
            z += 1
        m = s
        cc = pow(z, q, p)
        t = pow(a, q, p)
        r = pow(a, (q + 1) // 2, p)
        while t != 1:
            i, t2i = 0, t
            while t2i != 1:
                t2i = (t2i * t2i) % p
                i += 1
            b = pow(cc, 1 << (m - i - 1), p)
            m = i
            cc = (b * b) % p
            t = (t * cc) % p
            r = (r * b) % p
        return r

    F1 = fields[1]
    mismatches = 0
    checked = 0
    for a in range(p):
        r1 = fp_common_sqrt_mod(a, p)
        r2 = F1.sqrt((a,))
        checked += 1
        if r1 is None:
            if r2 is not None:
                mismatches += 1
        else:
            expected = min(r1, (-r1) % p)
            if r2 is None or r2[0] != expected:
                mismatches += 1

    # Frobenius-two-ways cross-check, one per k, on a fixed test element.
    frob_cross = {}
    for k in [1, 2, 3, 4]:
        F = fields[k]
        x = tuple((i * 7 + 3) % p for i in range(k))
        ok_all = True
        details = []
        for j in [1, 2, 3]:
            a1 = F.frob_iter(x, j)
            a2 = F.frob_direct(x, j)
            ok = F.eq(a1, a2)
            ok_all = ok_all and ok
            details.append({"j": j, "iterated": a1, "direct": a2, "match": ok})
        frob_cross[k] = {"test_element": x, "all_match": ok_all, "detail": details}

    transcript = {
        "p": p,
        "prime_verified": prime_ok,
        "odd_verified": odd_ok,
        "p_mod_3": mod3,
        "p_mod_3_eq_1_verified": mod3_ok,
        "p_mod_8": mod8,
        "c": c,
        "c_is_2": c_is_2,
        "two_pow_p_minus_1_over_2_mod_p": two_is_qr,
        "two_is_nonsquare_verified": two_nonsquare,
        "two_pow_p_minus_1_over_3_mod_p": two_cube_test,
        "two_is_noncube_verified": two_noncube,
        "m_k_search": {
            str(k): {
                "kind": v["kind"], "a": v["a"], "b": v["b"],
                "branch": v["branch"],
                "n_candidates_tried": len(v["search_log"]),
                "search_log": v["search_log"] if k != 1 else v["search_log"],
            }
            for k, v in m_k_search.items()
        },
        "sqrt_cross_check_k1_vs_fp_common": {
            "checked": checked, "mismatches": mismatches, "pass": mismatches == 0,
        },
        "frobenius_two_ways_cross_check": frob_cross,
        "all_pass": (
            prime_ok and odd_ok and mod3_ok and two_nonsquare and two_noncube
            and mismatches == 0 and all(v["all_match"] for v in frob_cross.values())
        ),
        "wall_seconds": time.time() - t0,
    }
    return transcript, fields


# ---------------------------------------------------------------------
# N1 census helpers
# ---------------------------------------------------------------------

def _log_row(log_file, row):
    if log_file is not None:
        log_file.write(json.dumps(row, default=str) + "\n")


def n1_k1_exhaustive(F0, A, B, reverse=False, log_file=None):
    tw = bt.Towers(F0)
    p = F0.p
    hist = {}
    strata = {"i": 0, "ii": 0, "none": 0}
    for e1 in range(p):
        for e2 in range(p):
            r = bt.n1_classify_point(F0, tw, A, B, F0.from_int(e1), F0.from_int(e2), reverse=reverse)
            strata[r["stratum"]] += 1
            if r["class"] is not None:
                hist[r["class"]] = hist.get(r["class"], 0) + 1
            _log_row(log_file, {"e1": e1, "e2": e2, "stratum": r["stratum"],
                                 "class": r["class"], "perm": r["perm"]})
    return hist, strata


def n1_sampled(F0, A, B, domain, S, reverse=False, log_file=None):
    tw = bt.Towers(F0)
    perms = set()
    strata = {"i": 0, "ii": 0, "none": 0}
    class_hist = {}
    for j in range(S):
        e1, _ = sd.draw_field_element(domain, F0.p, F0.k, j, 0)
        e2, _ = sd.draw_field_element(domain, F0.p, F0.k, j, 1)
        r = bt.n1_classify_point(F0, tw, A, B, e1, e2, reverse=reverse)
        strata[r["stratum"]] += 1
        if r["perm"] is not None:
            perms.add(r["perm"])
            class_hist[r["class"]] = class_hist.get(r["class"], 0) + 1
        _log_row(log_file, {"draw_index": j, "e1": e1, "e2": e2, "stratum": r["stratum"],
                             "class": r["class"], "perm": r["perm"]})
    grp = bt.subgroup_closure(list(perms), 4)
    smallest_class = min(class_hist.items(), key=lambda kv: kv[1]) if class_hist else None
    return {"n_samples": S, "distinct_perms_observed": len(perms),
            "generators": sorted(perms), "group_order": len(grp),
            "group_elements": grp, "strata": strata,
            "class_histogram": class_hist, "smallest_observed_class": smallest_class}


def n1_k1_exhaustive_as_group(F0, A, B, reverse=False):
    tw = bt.Towers(F0)
    p = F0.p
    perms = set()
    for e1 in range(p):
        for e2 in range(p):
            r = bt.n1_classify_point(F0, tw, A, B, F0.from_int(e1), F0.from_int(e2), reverse=reverse)
            if r["perm"] is not None:
                perms.add(r["perm"])
    grp = bt.subgroup_closure(list(perms), 4)
    return {"n_samples": "exhaustive", "distinct_perms_observed": len(perms),
            "generators": sorted(perms), "group_order": len(grp)}


# ---------------------------------------------------------------------
# N2 / N2-twin census helpers
# ---------------------------------------------------------------------

def n2_exhaustive_k1(F0, a_fn, b_fn, exclude_zeros_of, reverse=False, log_file=None):
    tw = bt.Towers(F0)
    p = F0.p
    perms = set()
    excluded = 0
    class_hist = {}
    for x in range(p):
        e = F0.from_int(x)
        if any(F0.is_zero(f(e)) for f in exclude_zeros_of):
            excluded += 1
            _log_row(log_file, {"e": x, "stratum": "ii", "class": None, "perm": None})
            continue
        r = bt.n2_classify_point(F0, tw, e, a_fn, b_fn, reverse=reverse)
        if r["perm"] is not None:
            perms.add(r["perm"])
            class_hist[r["class"]] = class_hist.get(r["class"], 0) + 1
        _log_row(log_file, {"e": x, "stratum": r["stratum"], "class": r["class"], "perm": r["perm"]})
    grp = bt.subgroup_closure(list(perms), 4)
    smallest_class = min(class_hist.items(), key=lambda kv: kv[1]) if class_hist else None
    return {"n_samples": p - excluded, "excluded_ramification": excluded,
            "distinct_perms_observed": len(perms), "generators": sorted(perms),
            "group_order": len(grp), "class_histogram": class_hist,
            "smallest_observed_class": smallest_class}


def n2_sampled(F0, a_fn, b_fn, exclude_zeros_of, domain, S, coord_index=0, reverse=False, log_file=None):
    tw = bt.Towers(F0)
    perms = set()
    excluded = 0
    class_hist = {}
    for j in range(S):
        e, _ = sd.draw_field_element(domain, F0.p, F0.k, j, coord_index)
        if any(F0.is_zero(f(e)) for f in exclude_zeros_of):
            excluded += 1
            _log_row(log_file, {"draw_index": j, "e": e, "stratum": "ii", "class": None, "perm": None})
            continue
        r = bt.n2_classify_point(F0, tw, e, a_fn, b_fn, reverse=reverse)
        if r["perm"] is not None:
            perms.add(r["perm"])
            class_hist[r["class"]] = class_hist.get(r["class"], 0) + 1
        _log_row(log_file, {"draw_index": j, "e": e, "stratum": r["stratum"], "class": r["class"], "perm": r["perm"]})
    grp = bt.subgroup_closure(list(perms), 4)
    smallest_class = min(class_hist.items(), key=lambda kv: kv[1]) if class_hist else None
    return {"n_samples": S, "excluded_ramification": excluded,
            "distinct_perms_observed": len(perms), "generators": sorted(perms),
            "group_order": len(grp), "class_histogram": class_hist,
            "smallest_observed_class": smallest_class}


# ---------------------------------------------------------------------
# N4
# ---------------------------------------------------------------------

def n4_exact(F3, domain):
    poly = [F3.from_int((-C) % F3.p), F3.zero(), F3.zero(), F3.one()]
    rng = iter(sd.DeterministicFieldRNG(domain, F3.p, F3.k, "n4-root-split"))
    roots = fp.full_split_roots(poly, F3, F3.q, rng)
    roots_sorted = sorted(roots, key=lambda r: F3.lex_key(r))
    roots_sorted_rev = sorted(roots, key=lambda r: F3.lex_key(r), reverse=True)
    verify = {"cube_checks": [F3.eq(F3.pow(r, 3), F3.from_int(C)) for r in roots_sorted]}

    def perm_and_order(labelling):
        results = {}
        for k in [1, 2, 3, 4]:
            perm = []
            for r in labelling:
                img = F3.frob_direct(r, k)
                match = None
                for j2, r2 in enumerate(labelling):
                    if F3.eq(img, r2):
                        match = j2
                        break
                if match is None:
                    raise RuntimeError(f"N4: Frobenius^{k} image matched no labelled root")
                perm.append(match)
            perm = tuple(perm)
            grp = bt.subgroup_closure([perm], 3)
            results[k] = {"permutation": perm, "group_order": len(grp)}
        return results

    return {
        "roots_ascending_lex": roots_sorted,
        "roots_descending_lex": roots_sorted_rev,
        "cube_root_verification": verify,
        "R_k_ascending": perm_and_order(roots_sorted),
        "R_k_descending": perm_and_order(roots_sorted_rev),
    }


# ---------------------------------------------------------------------
# N3 / N5
# ---------------------------------------------------------------------

def random_poly_control(Fk, degree, domain, S, log_file=None):
    hist = {}
    n_discards = 0
    j = 0
    accepted = 0
    while accepted < S:
        coeffs = []
        for i in range(degree):
            v, _ = sd.draw_field_element(domain, Fk.p, Fk.k, j, i)
            coeffs.append(v)
        coeffs.append(Fk.one())
        if not fp.is_squarefree(coeffs, Fk):
            n_discards += 1
            _log_row(log_file, {"draw_index": j, "coeffs": coeffs[:degree], "squarefree": False, "discarded": True})
            j += 1
            continue
        shape = fp.distinct_degree_shape(coeffs, Fk, Fk.q)
        label = bt.shape_to_partition_label(shape, degree)
        hist[label] = hist.get(label, 0) + 1
        _log_row(log_file, {"draw_index": j, "coeffs": coeffs[:degree], "squarefree": True,
                             "discarded": False, "shape": shape, "label": label})
        accepted += 1
        j += 1
    return {"n_accepted": accepted, "n_squarefree_discards": n_discards, "histogram": hist}


S4_CHEBOTAREV = {"1^4": 1 / 24, "2.1.1": 1 / 4, "2^2": 1 / 8, "3+1": 1 / 3, "4": 1 / 4}
S5_CHEBOTAREV = {
    "1^5": 1 / 120, "2.1^3": 10 / 120, "2^2.1": 15 / 120, "3.1^2": 20 / 120,
    "3.2": 20 / 120, "4.1": 30 / 120, "5": 24 / 120,
}


def density_report(hist, forced, n):
    out = {}
    for label, p_forced in forced.items():
        obs = hist.get(label, 0)
        expected = p_forced * n
        se = math.sqrt(n * p_forced * (1 - p_forced)) if 0 < p_forced < 1 else 0.0
        dev = (obs - expected) / se if se > 0 else 0.0
        out[label] = {
            "observed_count": obs, "observed_density": obs / n if n else 0.0,
            "forced_density": p_forced, "expected_count": expected,
            "binomial_se_count": se, "deviation_in_se": dev,
            "within_3_se": abs(dev) <= 3.0,
        }
    return out


# ---------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------

def main():
    master_seed = sys.argv[1]
    outdir = sys.argv[2]
    domain_suffix = f"run-{master_seed}"
    domain = f"{DOMAIN_BASE}/{domain_suffix}"

    t_start = time.time()
    result = {"master_seed": master_seed, "domain": domain}

    import os
    import contextlib
    log_dir = f"{outdir}/per_base_point_log"
    os.makedirs(log_dir, exist_ok=True)

    def logf(name):
        return open(f"{log_dir}/{name}.jsonl", "w")

    # ---- Stage 0 ----
    stage0_transcript, fields = stage0(P, C)
    result["stage0"] = stage0_transcript
    if not stage0_transcript["all_pass"]:
        result["status"] = "failed_infrastructure"
        result["reason"] = "Stage-0 verification failed"
        return result, t_start

    A, B = 1, 1  # N1 curve

    with contextlib.ExitStack() as stack:
        f_n1_k1 = stack.enter_context(logf("N1_k1_exhaustive"))

        # ---- N1 ----
        n1 = {}
        hist_k1, strata_k1 = n1_k1_exhaustive(fields[1], A, B, log_file=f_n1_k1)
        n1["k1_exhaustive_histogram"] = hist_k1
        n1["k1_exhaustive_strata"] = strata_k1
        n1["k1_group"] = n1_k1_exhaustive_as_group(fields[1], A, B)

        ref_hist = {  # EXP-MONO-4c7479 RUN-MONO-4c7479-20260830, cell p=211,A=1,B=1
            "identity": 6105, "sigma_i": 11100, "sigma1_sigma2": 4950,
            "block_swap_involution": 11100, "four_cycle": 11055,
        }
        n1["reproduction_control"] = {
            "reference_run": "EXP-MONO-4c7479/runs/RUN-MONO-4c7479-20260830",
            "reference_histogram": ref_hist,
            "observed_histogram": hist_k1,
            "match": hist_k1 == ref_hist,
        }

        n1["ladder"] = {1: n1["k1_group"]}
        for k in [2, 3, 4]:
            with logf(f"N1_k{k}_sampled") as f_n1_k:
                n1["ladder"][k] = n1_sampled(fields[k], A, B, domain, 10000, log_file=f_n1_k)

        n1["labelling_control_k1"] = n1_k1_exhaustive_as_group(fields[1], A, B, reverse=True)
        # (labelling-control log intentionally omitted from the primary
        # per_base_point_log set to bound artifact size; the control's
        # aggregate group order is the required output per
        # `controls.labelling_control`.)

        result["N1"] = n1

        # ---- N2 ----
        n2 = {}
        c_elts = {k: fields[k].from_int(C) for k in [1, 2, 3, 4]}

        def make_n2_ab(k):
            c_elt = c_elts[k]
            F0 = fields[k]
            return (lambda e: e), (lambda e: F0.mul(c_elt, e))

        n2["ladder"] = {}
        for k in [1, 2, 3, 4]:
            F0 = fields[k]
            a_fn, b_fn = make_n2_ab(k)
            with logf(f"N2_k{k}") as f_n2_k:
                if k == 1:
                    n2["ladder"][1] = n2_exhaustive_k1(F0, a_fn, b_fn, [a_fn], log_file=f_n2_k)
                else:
                    n2["ladder"][k] = n2_sampled(F0, a_fn, b_fn, [a_fn], domain, 10000, log_file=f_n2_k)

        # sample-size control at k=1
        F0 = fields[1]
        a_fn, b_fn = make_n2_ab(1)
        with logf("N2_sample_size_control_S1000") as f1000, logf("N2_sample_size_control_S100000") as f100000:
            n2["sample_size_control"] = {
                "exhaustive": n2["ladder"][1],
                "S_1000": n2_sampled(F0, a_fn, b_fn, [a_fn], domain, 1000, log_file=f1000),
                "S_100000": n2_sampled(F0, a_fn, b_fn, [a_fn], domain, 100000, log_file=f100000),
            }
        n2["sample_size_control"]["R1_consistent"] = (
            n2["sample_size_control"]["exhaustive"]["group_order"]
            == n2["sample_size_control"]["S_1000"]["group_order"]
            == n2["sample_size_control"]["S_100000"]["group_order"]
        )

        n2["labelling_control_k1"] = n2_exhaustive_k1(fields[1], a_fn, b_fn, [a_fn], reverse=True)

        result["N2"] = n2

        # ---- N2-twin ----
        n2t = {}

        def make_n2t_ab(k):
            F0 = fields[k]
            one_elt = F0.one()
            return (lambda e: e), (lambda e, F0=F0, one_elt=one_elt: F0.add(e, one_elt))

        n2t["ladder"] = {}
        for k in [1, 2, 3, 4]:
            F0 = fields[k]
            a_fn, b_fn = make_n2t_ab(k)
            with logf(f"N2twin_k{k}") as f_n2t_k:
                if k == 1:
                    n2t["ladder"][1] = n2_exhaustive_k1(F0, a_fn, b_fn, [a_fn, b_fn], log_file=f_n2t_k)
                else:
                    n2t["ladder"][k] = n2_sampled(F0, a_fn, b_fn, [a_fn, b_fn], domain, 10000, log_file=f_n2t_k)

        a_fn, b_fn = make_n2t_ab(1)
        n2t["labelling_control_k1"] = n2_exhaustive_k1(fields[1], a_fn, b_fn, [a_fn, b_fn], reverse=True)

        result["N2_twin"] = n2t

        # ---- N4 ----
        n4 = n4_exact(fields[3], domain)
        result["N4"] = n4

        # ---- N3 ----
        n3 = {"ladder": {}}
        for k in [1, 2, 3, 4]:
            with logf(f"N3_k{k}") as f_n3_k:
                hist = random_poly_control(fields[k], 4, domain, 2000, log_file=f_n3_k)
            n3["ladder"][k] = hist
            n3["ladder"][k]["density_vs_S4"] = density_report(hist["histogram"], S4_CHEBOTAREV, hist["n_accepted"])
            n3["ladder"][k]["rarest_observed"] = min(hist["histogram"].items(), key=lambda kv: kv[1]) if hist["histogram"] else None

        # identical_object_null control: split S=2000 at k=1 by seed parity (j even/odd)
        F1 = fields[1]
        half_a, half_b = {}, {}
        j = 0
        accepted_a = accepted_b = 0
        while accepted_a < 1000 or accepted_b < 1000:
            coeffs = []
            for i in range(4):
                v, _ = sd.draw_field_element(domain, F1.p, F1.k, j, i)
                coeffs.append(v)
            coeffs.append(F1.one())
            if fp.is_squarefree(coeffs, F1):
                shape = fp.distinct_degree_shape(coeffs, F1, F1.q)
                label = bt.shape_to_partition_label(shape, 4)
                if j % 2 == 0 and accepted_a < 1000:
                    half_a[label] = half_a.get(label, 0) + 1
                    accepted_a += 1
                elif j % 2 == 1 and accepted_b < 1000:
                    half_b[label] = half_b.get(label, 0) + 1
                    accepted_b += 1
            j += 1
        n3["identical_object_null_control"] = {
            "half_even_j": {"histogram": half_a, "density_vs_S4": density_report(half_a, S4_CHEBOTAREV, 1000)},
            "half_odd_j": {"histogram": half_b, "density_vs_S4": density_report(half_b, S4_CHEBOTAREV, 1000)},
        }
        result["N3"] = n3

        # ---- N5 ----
        n5 = {"ladder": {}}
        for k in [1, 2, 3, 4]:
            with logf(f"N5_k{k}") as f_n5_k:
                hist = random_poly_control(fields[k], 5, domain, 2000, log_file=f_n5_k)
            n5["ladder"][k] = hist
            n5["ladder"][k]["density_vs_S5"] = density_report(hist["histogram"], S5_CHEBOTAREV, hist["n_accepted"])
            n5["ladder"][k]["rarest_observed"] = min(hist["histogram"].items(), key=lambda kv: kv[1]) if hist["histogram"] else None
            n5["ladder"][k]["verdict"] = "UNDECIDED"
            n5["ladder"][k]["U"] = 120
            n5["ladder"][k]["L"] = 1
        result["N5"] = n5

    result["total_wall_seconds"] = time.time() - t_start
    result["status"] = "completed"
    return result, t_start


if __name__ == "__main__":
    import resource
    result, t_start = main()
    outdir = sys.argv[2]
    ru = resource.getrusage(resource.RUSAGE_SELF)
    # ru_maxrss is bytes on macOS/BSD, kilobytes on Linux.
    peak_rss_bytes = ru.ru_maxrss if sys.platform == "darwin" else ru.ru_maxrss * 1024
    result["peak_rss_bytes"] = peak_rss_bytes
    with open(f"{outdir}/raw-result.json", "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(json.dumps({"status": result.get("status"), "wall_seconds": result.get("total_wall_seconds"),
                       "peak_rss_bytes": peak_rss_bytes}))
