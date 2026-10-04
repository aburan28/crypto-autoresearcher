#!/usr/bin/env python3
"""TASK-20260923-b8f163, joint J2: control recomputation from per-target records.

Reads targets-*.jsonl.gz and references.json (committed bytes). Uses no impl/
code; does not run analysis.py or report.py. Zero trials; no RUN-id.

  1. counts per family and D (records, idx, degenerate, arms), references, shortfall
  2. C-UNIF recomputed (F-RANDX own references incl. modal, both D), with the
     validator's own exact equal-tailed 99.9% Binomial acceptance region
  3. STRUCTURAL TEST of C-UNIF: with K_rank = 17 = number of r bits, the
     affine system {e_k(r) = 1 for all k} has at most one solution, and the
     reference's own r is one (self replay). So full-replay survival should
     hold iff x_R(target) == x_R(reference). Tested on every affine-route
     family, every reference key (own and cross-family) and both D.
  4. NESTING recomputed (per-pair flag monotonicity; hash-class nesting)
  5. PS0 / PS1 / PS3 reach: how many instances each item can actually test
  6. C-PASS flags and hash-content flags re-read
"""
import gzip
import json
import math
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
RUN = os.path.join(REPO, "experiments", "EXP-CERTBIN-4e92d7", "runs", "RUN-CERTBIN-3b7e05")
FAMS = ["F-S3", "F-S3-REV", "F-PLANT", "F-RANDX", "F-AFF-1", "F-AFF-2", "F-AFF-3", "F-NULLF2"]
AFFINE = ["F-S3", "F-S3-REV", "F-PLANT", "F-RANDX", "F-AFF-1", "F-AFF-2", "F-AFF-3"]


def load():
    recs = {}
    for f in FAMS:
        rows = []
        with gzip.open(os.path.join(RUN, f"targets-{f}.jsonl.gz"), "rt") as fh:
            for line in fh:
                rows.append(json.loads(line))
        recs[f] = rows
    refs = json.load(open(os.path.join(RUN, "references.json")))
    return recs, refs


def binom_logpmf(k, n, p):
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1) + k * math.log(p) + (n - k) * math.log1p(-p)


def accept_region(n, p, level=0.999):
    """Equal-tailed: largest lo with P(X < lo) <= a/2, smallest hi with P(X > hi) <= a/2."""
    a2 = (1 - level) / 2
    pmf = [math.exp(binom_logpmf(k, n, p)) for k in range(n + 1)]
    lo, cum = 0, 0.0
    while lo <= n and cum + pmf[lo] <= a2:
        cum += pmf[lo]
        lo += 1
    hi, cum = n, 0.0
    while hi >= 0 and cum + pmf[hi] <= a2:
        cum += pmf[hi]
        hi -= 1
    return lo, hi


def ref_xR(refs, fam, label, D, recs):
    """x_R of a reference in the family whose records carry it."""
    if ":" in label:
        src, lab = label.split(":")
    else:
        src, lab = fam, label
    r = refs[src]["references"][lab]
    if lab == "modal":
        idx = r["instance_idx_per_D"][f"D{D}"]
        pool = recs[src] if src in recs else recs[fam]
        xs = {t["x_R"] for t in pool if t["idx"] == idx and t["D"] == D}
        assert len(xs) == 1
        return xs.pop(), src, lab
    return r["x_R"], src, lab


def ref_K(refs, src, lab, D):
    return refs[src]["references"][lab][f"D{D}"]["len_strict"]


def main():
    recs, refs = load()
    out = {"task": "TASK-20260923-b8f163", "joint": "J2"}

    # 1. counts
    cnt = {}
    for f in FAMS:
        for D in (3, 4):
            rs = [r for r in recs[f] if r["D"] == D]
            nd = [r for r in rs if not r["degenerate"]]
            cnt[f"{f}/D{D}"] = {"records": len(rs), "distinct_idx": len({r["idx"] for r in rs}),
                                "degenerate": len(rs) - len(nd),
                                "unsat_nondeg": sum(1 for r in nd if r["s"] == 0),
                                "sat_nondeg": sum(1 for r in nd if r["s"] >= 1),
                                "stratum_field_consistent": all(r["stratum"] == ("degenerate" if r["degenerate"] else ("sat" if r["s"] >= 1 else "unsat")) for r in rs),
                                "degenerate_iff_xR_lt_512": all((r["x_R"] is not None and r["x_R"] < 512) == r["degenerate"] for r in rs) if f != "F-NULLF2" else all(not r["degenerate"] for r in rs)}
    out["counts"] = cnt
    out["references"] = {f: {"labels": list(refs[f]["references"].keys()), "shortfall": refs[f]["shortfall"]} for f in FAMS}

    # 2. C-UNIF recomputed
    unif = {}
    for D in (3, 4):
        for lab in ("U1", "U2", "U3", "S1", "S2", "modal"):
            K = ref_K(refs, "F-RANDX", lab, D)
            Kr = refs["F-RANDX"]["references"][lab][f"D{D}"]["K_rank"]
            sc = [r for r in recs["F-RANDX"] if r["D"] == D and not r["degenerate"] and (lab != "modal" or r["idx"] > 100)]
            surv = sum(1 for r in sc if r["refs"][lab]["replay_first_zero"] == K)
            p = 2.0 ** (-Kr)
            lo, hi = accept_region(len(sc), p)
            p_fail_if_true = 1 - sum(math.exp(binom_logpmf(k, len(sc), p)) for k in range(lo, hi + 1))
            unif[f"D{D}/{lab}"] = {"n": len(sc), "K_rank": Kr, "survivors": surv, "expected": len(sc) * p,
                                   "accept": [lo, hi], "pass": lo <= surv <= hi,
                                   "prob_reject_under_its_own_null": p_fail_if_true}
    out["C-UNIF_recomputed"] = unif

    # 3. structural test: survival iff x_R equals the reference's x_R
    struct = {"pairs_tested": 0, "pairs_consistent": 0, "total_survivors": 0, "survivors_with_equal_xR": 0,
              "inconsistent": [], "K_rank_values": defaultdict(int)}
    for f in AFFINE:
        for D in (3, 4):
            rs = [r for r in recs[f] if r["D"] == D]
            keys = set()
            for r in rs:
                keys |= set(r["refs"].keys())
            for key in sorted(keys):
                xr, src, lab = ref_xR(refs, f if not (f == "F-S3-REV") else "F-S3-REV", key, D, recs)
                K = ref_K(refs, src, lab, D)
                struct["K_rank_values"][refs[src]["references"][lab][f"D{D}"]["K_rank"]] += 1
                have = [r for r in rs if key in r["refs"]]
                surv = [r for r in have if r["refs"][key]["replay_first_zero"] == K]
                same = [r for r in have if r["x_R"] == xr]
                ok = sorted(r["idx"] for r in surv) == sorted(r["idx"] for r in same)
                struct["pairs_tested"] += 1
                struct["pairs_consistent"] += ok
                struct["total_survivors"] += len(surv)
                struct["survivors_with_equal_xR"] += sum(1 for r in surv if r["x_R"] == xr)
                if not ok or surv:
                    struct["inconsistent" if not ok else "survivor_cases"] = struct.get("inconsistent" if not ok else "survivor_cases", []) + [
                        {"family": f, "D": D, "ref": key, "ref_x_R": xr, "survivor_idx": [r["idx"] for r in surv],
                         "equal_xR_idx": [r["idx"] for r in same]}]
    struct["K_rank_values"] = dict(struct["K_rank_values"])
    out["C-UNIF_structural_test"] = struct

    # 4. nesting
    nest = {"pairs": 0, "flag_violations": 0, "class_violations": 0}
    for f in FAMS:
        for D in (3, 4):
            rs = [r for r in recs[f] if r["D"] == D]
            for r in rs:
                for key, c in r["refs"].items():
                    m = c["match"]
                    nest["pairs"] += 1
                    if (m["ops"] and not m["strict"]) or (m["strict"] and not m["set"]) or (m["set"] and not m["rank"]):
                        nest["flag_violations"] += 1
            for fine, coarse in (("h_ops", "h_strict"), ("h_strict", "h_set"), ("h_set", "h_rank")):
                grp = defaultdict(set)
                for r in rs:
                    grp[r[fine]].add(r[coarse])
                nest["class_violations"] += sum(1 for v in grp.values() if len(v) > 1)
    out["NESTING_recomputed"] = nest

    # 5. PS reach
    reach = {}
    for f in FAMS:
        for D in (3, 4):
            rs = [r for r in recs[f] if r["D"] == D]
            sat = [r for r in rs if r["s"] >= 1]
            uns = [r for r in rs if r["s"] == 0]
            reach[f"{f}/D{D}"] = {
                "PS0_testable_instances(s>=1)": len(sat), "PS0_solutions_tested": sum(r["s"] for r in sat),
                "PS0_vacuous_instances(s=0)": len(uns), "PS0_fail_flags": sum(1 for r in rs if r["PS0_fail"]),
                "PS1_testable(s>=1)": len(sat), "PS1_fail_flags": sum(1 for r in rs if r["PS1_fail"]),
                "sat_with_one_in_R": sum(1 for r in sat if r["one_in_R"]),
                "unsat_with_one_in_R": sum(1 for r in uns if r["one_in_R"]),
                "PS3_fail_flags": sum(1 for r in rs if r["PS3_fail"]),
                "PS3_nontrivial(s>=1)": len(sat),
            }
    out["PS_reach"] = reach
    # 6. C-PASS flags
    out["C-PASS_flags"] = {f"{f}": sum(1 for r in recs[f] if not r["cpass"]) for f in FAMS}
    json.dump(out, open(os.path.join(HERE, "j2_controls.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "PS_reach"}, indent=1)[:6000])
    print(json.dumps(out["PS_reach"], indent=0)[:4000])


if __name__ == "__main__":
    main()
