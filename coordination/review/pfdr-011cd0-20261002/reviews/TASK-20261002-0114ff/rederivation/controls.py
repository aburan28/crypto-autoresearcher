#!/usr/bin/env python3
"""Positive and negative controls for the validator's own instruments.

TASK-20261002-0114ff. In memory only. Shows that g4d_verify.py, g4r_verify.py
and relcount.py can FAIL (a verifier that cannot fail certifies nothing).
  G4-D: the first R14 certificate passes; k+1, Q off-curve, a key outside the
        R14 universe and a perturbed p each fail the stated check.
  G4-R: the first sampled R12 TT row, R12 TB row and R13 SS row pass the
        identity; coefficient+1, kcoef+1 and rhs+1 each fail it.
  relcount: a synthetic 4-member x-group (3 star rows) yields C(4,2) = 6 pair
        relations; a duplicated star relation is counted once with M = 2; the
        known_log formal test accepts 2F_0 - F_1 and rejects F_0 + F_1 - F_3.
Standard library only.
"""
import gzip
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-pfdr011cd0-5753edf2e"
R = WT + "/experiments/EXP-PFDR-011cd0/runs/"


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    g4d, g4r, rc = load("g4d_verify"), load("g4r_verify"), load("relcount")
    res = {}
    # ---- G4-D
    rec = json.loads(gzip.open(R + "RUN-PFDR-011cd0-srch-check/solve-certs.jsonl.gz", "rt").readline())
    p, a, b, N, k = rec["p"], rec["a"], rec["b"], rec["N"], rec["k"]
    P, Q = tuple(rec["P"]), tuple(rec["Q"])
    res["G4D_positive_kP_eq_Q"] = g4d.mul(k, P, a, p) == Q
    res["G4D_N1_k_plus_1_rejected"] = g4d.mul(k + 1, P, a, p) != Q
    res["G4D_N2_Q_offcurve_rejected"] = not g4d.on_curve((Q[0], (Q[1] + 1) % p), a, b, p)
    universe = {(bb, c, m, arm, "census") for bb in (20, 26) for c in range(10, 14)
                for m in (3, 4, 5) for arm in g4d.ARMS}
    kd = rec["key"]
    res["G4D_positive_key_in_universe"] = (kd["bits"], kd["curve"], kd["m"], kd["arm"], kd["mode"]) in universe
    res["G4D_N3_key_curve14_rejected"] = (kd["bits"], 14, kd["m"], kd["arm"], kd["mode"]) not in universe
    res["G4D_N3b_N_times_P_nonzero_for_N_plus_1"] = g4d.mul(N + 1, P, a, p) is not None
    res["G4D_N4_isprime_rejects_carmichael_561_and_N_times_3"] = (not g4d.is_prime(561)) and (not g4d.is_prime(3 * N))
    # ---- G4-R
    def first_row(job, cls, run):
        fp = R + run + "/attempt-1/jobs/" + job + "/harvest-rows.jsonl.gz"
        for line in gzip.open(fp, "rt"):
            r = json.loads(line)
            if r["class"] == cls and r["curve"] % 10 == 0:
                return r
    def bases_for(job, run, key):
        for line in gzip.open(R + run + "/attempt-1/jobs/" + job + "/bases.jsonl.gz", "rt"):
            r = json.loads(line)
            if (r["bits"], r["curve"], r["m"], r["arm"]) == key:
                return r
    for run, job, cls in (("RUN-PFDR-011cd0-table", "3-b30-c10", "TT"), ("RUN-PFDR-011cd0-table", "3-b30-c10", "TB"),
                          ("RUN-PFDR-011cd0-search", "3-b30-c10", "SS")):
        r = first_row(job, cls, run)
        bs = bases_for(job, run, (r["bits"], r["curve"], r["m"], r["arm"]))
        p, a, N = bs["p"], bs["a"], bs["N"]
        F = [tuple(x) for x in bs["points"]]
        P, Q = tuple(bs["P"]), tuple(bs["Q"])

        def ident(coeffs, kc, rh):
            vec = {}
            for i, c in coeffs:
                vec[i] = vec.get(i, 0) + c
            lhs = g4r.add(g4r.comb({i: c for i, c in vec.items() if c}, F, a, p), g4r.mul(kc, Q, a, p), a, p)
            return lhs == g4r.mul(rh, P, a, p)
        c0 = [list(x) for x in r["coeffs"]]
        c1 = [list(x) for x in r["coeffs"]]
        c1[0][1] += 1
        res[f"G4R_{cls}_positive"] = ident(c0, r["kcoef"], r["rhs"])
        res[f"G4R_{cls}_N_coeff_plus1_rejected"] = not ident(c1, r["kcoef"], r["rhs"])
        res[f"G4R_{cls}_N_kcoef_plus1_rejected"] = not ident(c0, r["kcoef"] + 1, r["rhs"])
        res[f"G4R_{cls}_N_rhs_plus1_rejected"] = not ident(c0, r["kcoef"], r["rhs"] + 1)
    # ---- relcount
    N = 101
    u1, u2, u3, u4 = {0: 1, 1: 1}, {2: 1, 3: -1}, {4: 1, 5: 1}, {6: 1, 7: 1}
    star = [rc.diff(u1, u2), rc.diff(u1, {k: -v for k, v in u3.items()}), rc.diff(u1, u4)]
    st, nf = rc.count_class({"g": star}, N, False)
    res["REL_4member_group_6_distinct"] = st["n_nonformal"] == 6 and st["pairs"] == 6 and st["R_star"] == 3
    st2, _ = rc.count_class({"g": star, "h": [dict(star[0])]}, N, False)
    res["REL_duplicate_relation_counted_once_M2"] = st2["n_nonformal"] == 6 and st2["hist_nonformal"].get(2) == 1
    res["REL_monic_projective"] = rc.monic({3: 2, 5: 4}, N) == rc.monic({3: 5, 5: 10}, N) == ((3, 1), (5, 2))
    res["REL_zero_dropped"] = rc.monic({3: 101, 5: -202}, N) is None
    res["REL_knownlog_formal_2F0_minus_F1"] = rc.is_formal_knownlog(rc.monic({0: 2, 1: -1}, N), N)
    res["REL_knownlog_nonformal_F0_F1_minus_F3"] = not rc.is_formal_knownlog(rc.monic({0: 1, 1: 1, 3: -1}, N), N)
    res["REL_kcoef_never_formal"] = not rc.is_formal_knownlog(rc.monic({0: 1, rc.KC: 3}, N), N)
    res["all_behaved_as_stated"] = all(v for k, v in res.items())
    json.dump(res, open(sys.argv[1], "w"), indent=1, sort_keys=True)
    print(json.dumps(res))


if __name__ == "__main__":
    main()
