#!/usr/bin/env python3
"""J1 G4-R: the validator's own harvested-row verifier on the declared sample.

TASK-20261002-0114ff. Written from the specification text (row identity
sum_i c_i F_i + kcoef Q == rhs P; G4-R) without reading verify_rows.py. Own
affine Weierstrass arithmetic (standard library). factor_base.py and curve.py
are imported ONLY to construct bases (RV-3), loaded as modules of a synthetic
package so that the index_calculus __init__ is not executed; their
verification or counting routines are not called.

Per sampled instance (rederivation/outputs/g4r-sample.json):
  B1 a bases.jsonl.gz line exists; (p, a, b, N, P) equal design.json's entry
  B2 P and Q on the curve; N*P = O
  B3 every base point on the curve, y != 0, x-coordinates distinct
  B4 |F| equals the declared size (s_sub for the SUB family and known_log,
     s_dick for the DICK family)
  B5 the points equal the base rebuilt by factor_base.py with the
     specification's seed for the arm (cells.arms.bases)
Per harvested row of a sampled instance:
  R1 indices in [0, |F|)
  R2 sum c_i F_i + kcoef Q - rhs P == O   (the row's group identity)
  R3 TT/TB: kcoef == rhs == 0
  R4 TT/TB: the two elements' points have equal x and coeffs == +-(u1 - sigma u2)
     with sigma = +1 iff the points are equal (sigma = -1 iff negatives)
  R5 TT/TB: each tail element's ybit == [y(stored-orientation sum) > p // 2]
  R6 SS: coeffs == b1 - sigma b2 for some sigma, b = H + s e_j (base part)
  R7 cert_ok is true
Usage: g4r_verify.py SAMPLE_JSON OUT_JSON
"""
import gzip
import importlib
import json
import os
import sys
import types

WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-pfdr011cd0-5753edf2e"
EXP = WT + "/experiments/EXP-PFDR-011cd0"
RUNS = {"R12": EXP + "/runs/RUN-PFDR-011cd0-table/attempt-1/jobs",
        "R13": EXP + "/runs/RUN-PFDR-011cd0-search/attempt-1/jobs"}
DESIGN = EXP + "/runs/RUN-PFDR-011cd0-p0-design/attempt-3/design.json"
IC = WT + "/src/crypto_autoresearcher/index_calculus"


def load_engine():
    pkg = types.ModuleType("icpkg")
    pkg.__path__ = [IC]
    sys.modules["icpkg"] = pkg
    return importlib.import_module("icpkg.curve"), importlib.import_module("icpkg.factor_base")


def add(P1, P2, a, p):
    if P1 is None:
        return P2
    if P2 is None:
        return P1
    x1, y1 = P1
    x2, y2 = P2
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def neg(P1, p):
    return None if P1 is None else (P1[0], (-P1[1]) % p)


def mul(k, P1, a, p):
    if k < 0:
        k, P1 = -k, neg(P1, p)
    R, A = None, P1
    while k:
        if k & 1:
            R = add(R, A, a, p)
        A = add(A, A, a, p)
        k >>= 1
    return R


def on_curve(P1, a, b, p):
    x, y = P1
    return (y * y - (x * x * x + a * x + b)) % p == 0


def comb(vec, F, a, p):
    """sum c_i F_i for a sparse integer vector."""
    R = None
    for i, c in vec.items():
        R = add(R, mul(c, F[i], a, p), a, p)
    return R


def evec(e):
    d = {}
    if "base" in e:
        d[e["base"]] = 1
    elif "tail" in e:
        for i, s in e["tail"]:
            d[i] = d.get(i, 0) + s
    else:
        _, H, j, s = e["enc"]
        for i, t in H:
            d[i] = d.get(i, 0) + t
        d[j] = d.get(j, 0) + s
    return {k: v for k, v in d.items() if v}


def lin(u, v, x, y):
    out = {}
    for k, c in u.items():
        out[k] = out.get(k, 0) + x * c
    for k, c in v.items():
        out[k] = out.get(k, 0) + y * c
    return {k: c for k, c in out.items() if c}


def rebuild(fbm, E, P, arm, c, sz):
    s_sub, s_dick, size0 = sz["s_sub"], sz["s_dick"], sz["size0"]
    FB = fbm.FactorBase
    if arm == "subgroup":
        return FB.subgroup(E, size0, c), s_sub
    if arm == "dickson":
        return FB.dickson(E, size0, c), s_dick
    if arm == "small_x":
        return FB.small_x(E, s_sub), s_sub
    if arm.startswith("random_sub_r"):
        return FB.random(E, s_sub, seed=c + 1000 * int(arm[-1])), s_sub
    if arm == "known_null_sub":
        return FB.random(E, s_sub, seed=c + 6000), s_sub
    if arm == "planted_sub":
        return FB.planted(E, s_sub, seed=c + 8000), s_sub
    if arm.startswith("random_dick_r"):
        return FB.random(E, s_dick, seed=c + 3000 + 1000 * int(arm[-1])), s_dick
    if arm == "known_null_dick":
        return FB.random(E, s_dick, seed=c + 7000), s_dick
    if arm == "known_log":
        return FB.known_log(E, P, s_sub), s_sub
    raise ValueError(arm)


def main():
    curve_m, fbm = load_engine()
    sample = json.load(open(sys.argv[1]))["sample"]
    design = json.load(open(DESIGN))
    dc = {(c["bits"], c["curve"]): c for c in design["curves"]}
    want = {}
    for s in sample:
        want.setdefault(s[-1], set()).add(tuple(s[:5]))
    inst = {}
    row_fail_examples = []
    tot = {"rows": 0, "rows_ok": 0, "instances": 0}
    rowchk = {f"R{i}": 0 for i in range(1, 8)}
    for run, jd in RUNS.items():
        for job in sorted(os.listdir(jd)):
            bfp = os.path.join(jd, job, "bases.jsonl.gz")
            bases = {}
            if os.path.exists(bfp):
                with gzip.open(bfp, "rt") as fh:
                    for line in fh:
                        r = json.loads(line)
                        key = (r["bits"], r["curve"], r["m"], r["arm"], "table" if run == "R12" else "search")
                        if key in want.get(run, ()):
                            bases[key] = r
            if not bases:
                continue
            ctx = {}
            for key, r in bases.items():
                bits, c, m, arm, mode = key
                d = dc.get((bits, c))
                p, a, b, N = r["p"], r["a"], r["b"], r["N"]
                P, Q = tuple(r["P"]), tuple(r["Q"])
                F = [tuple(x) for x in r["points"]]
                chk = {}
                chk["B1"] = d is not None and (d["p"], d["a"], d["b"], d["N"], tuple(d["P"])) == (p, a, b, N, P)
                chk["B2"] = on_curve(P, a, b, p) and on_curve(Q, a, b, p) and mul(N, P, a, p) is None
                chk["B3"] = all(on_curve(x, a, b, p) and x[1] != 0 for x in F) and len({x[0] for x in F}) == len(F)
                sz = d["sizes"][str(m)]
                E = curve_m.Curve(p, a, b, N)
                fb, expect = rebuild(fbm, E, P, arm, c, sz)
                chk["B4"] = len(F) == expect
                chk["B5"] = [tuple(x) for x in fb.points] == F
                ctx[key] = (p, a, N, P, Q, F)
                inst[key] = {"run": run, "base_checks": chk, "rows": 0, "rows_failed": 0,
                             "planted_relations": fb.params.get("planted_relations") if arm == "planted_sub" else None}
            hfp = os.path.join(jd, job, "harvest-rows.jsonl.gz")
            with gzip.open(hfp, "rt") as fh:
                for line in fh:
                    r = json.loads(line)
                    key = (r["bits"], r["curve"], r["m"], r["arm"], r["mode"])
                    if key not in ctx:
                        continue
                    p, a, N, P, Q, F = ctx[key]
                    vec = {}
                    for i, x in r["coeffs"]:
                        vec[i] = vec.get(i, 0) + x
                    vec = {k: v for k, v in vec.items() if v}
                    bad = []
                    if not all(0 <= i < len(F) for i in vec):
                        bad.append("R1")
                    else:
                        lhs = add(comb(vec, F, a, p), mul(r["kcoef"], Q, a, p), a, p)
                        if lhs != mul(r["rhs"], P, a, p):
                            bad.append("R2")
                    e1, e2 = r["elements"]
                    if r["class"] in ("TT", "TB"):
                        if r["kcoef"] % N or r["rhs"] % N:
                            bad.append("R3")
                        u1, u2 = evec(e1), evec(e2)
                        try:
                            P1, P2 = comb(u1, F, a, p), comb(u2, F, a, p)
                        except IndexError:
                            P1 = P2 = None
                        if P1 is None or P2 is None or P1[0] != P2[0]:
                            bad.append("R4")
                        else:
                            sg = 1 if P1 == P2 else -1
                            if vec not in (lin(u1, u2, 1, -sg), lin(u1, u2, -1, sg)):
                                bad.append("R4")
                            for e, Pe in ((e1, P1), (e2, P2)):
                                if "tail" in e and e["ybit"] != (Pe[1] > p // 2):
                                    bad.append("R5")
                    else:
                        b1, b2 = evec(e1), evec(e2)
                        if vec not in (lin(b1, b2, 1, -1), lin(b1, b2, 1, 1)):
                            bad.append("R6")
                    if r.get("cert_ok") is not True:
                        bad.append("R7")
                    inst[key]["rows"] += 1
                    tot["rows"] += 1
                    if bad:
                        inst[key]["rows_failed"] += 1
                        for x in set(bad):
                            rowchk[x] += 1
                        if len(row_fail_examples) < 20:
                            row_fail_examples.append({"key": list(key), "failed": sorted(set(bad)),
                                                      "class": r["class"], "elements": r["elements"],
                                                      "coeffs": r["coeffs"], "kcoef": r["kcoef"], "rhs": r["rhs"]})
                    else:
                        tot["rows_ok"] += 1
    missing = sorted(list(k) for run in want for k in want[run] if k not in inst)
    tot["instances"] = len(inst)
    base_fail = {k: sum(1 for v in inst.values() if not v["base_checks"][k]) for k in ("B1", "B2", "B3", "B4", "B5")}
    cover = {}
    for key, v in inst.items():
        cover.setdefault(f"{v['run']}|m{key[2]}|{key[3]}", 0)
        cover[f"{v['run']}|m{key[2]}|{key[3]}"] += 1
    rep = {"sample_instances": len(sample), "instances_checked": len(inst), "missing_bases_for_sampled": missing,
           "rows_checked": tot["rows"], "rows_passing_all": tot["rows_ok"], "row_check_failures": rowchk,
           "base_check_failures": base_fail, "row_fail_examples": row_fail_examples,
           "coverage_run_m_arm_instances": cover,
           "rows_by_class": {},
           "pass": (not missing and tot["rows"] == tot["rows_ok"] and not any(base_fail.values()))}
    json.dump(rep, open(sys.argv[2], "w"), indent=1, sort_keys=True)
    with gzip.open(sys.argv[2].replace(".json", "-per-instance.jsonl.gz"), "wt") as fh:
        for key in sorted(inst):
            fh.write(json.dumps({"key": list(key), **inst[key]}, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in rep.items() if k not in ("row_fail_examples", "coverage_run_m_arm_instances")}))


if __name__ == "__main__":
    main()
