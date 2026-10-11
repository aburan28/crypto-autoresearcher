#!/usr/bin/env python3
"""J7 (b) -- TASK-20260924-d95e70. The ell-substitution prediction on U62, C20
and S10 (prediction-rule.yaml, declared first; see ORDER.log).

Reads ONLY the Stage-1 archive (curve.json, targets-F-S3.jsonl.gz) for B and
x_R and the archived s/stratum/one_in_R flags used by the frozen set rules.
Does NOT open closures.jsonl.gz, certificates.jsonl.gz or instance-sets.json.

Per instance:
  1. f_0..f_16 by rtlib.descent (own code); self-test by direct F_{2^17}
     evaluation; cross-check against the archived engine's descended_E
     (experiments/EXP-CERTBIN-e94b27/impl/macaulay.py, imported unchanged).
  2. ell = sum_k Tr(t^k / x_R^2) f_k, checked == v_0 + v_9 + Tr(B / x_R^2).
  3. pi: v_0 -> v_9 + Tr(B / x_R^2); R'_4 = degree-4 Macaulay space of the 17
     substituted polynomials in v_1..v_17 (2618 x 3214): rank, 1 in R'_4, fall
     profile dim(R'_4 cap B'_{<=d}), d = 0..4.
  4. If 1 in R'_4: the structured W^(1) witness (C_4, a) with
     sum_{C_4} mu f_k + ell * a = 1 in B, deg mu <= 2, deg a <= 3, verified by
     verify_witness (a separate routine that rebuilds everything from f_k).
Writes predictions.json and w1-witnesses.jsonl.gz.
"""
import gzip
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rtlib as R  # noqa: E402

REPO = "/home/user/crypto-autoresearcher"
SRC = os.path.join(REPO, "experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05")
ENGINE = os.path.join(REPO, "experiments/EXP-CERTBIN-e94b27/impl")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load_sets():
    curve = json.load(open(os.path.join(SRC, "curve.json")))
    by = {}
    for line in gzip.open(os.path.join(SRC, "targets-F-S3.jsonl.gz"), "rt"):
        r = json.loads(line)
        if r["D"] == 4:
            by[r["idx"]] = r
    idxs = sorted(by)
    U62 = [i for i in idxs if by[i]["stratum"] == "unsat" and by[i]["one_in_R"] is False]
    C20 = [i for i in idxs if by[i]["stratum"] == "unsat" and by[i]["one_in_R"] is True][:20]
    S10 = [i for i in idxs if by[i]["stratum"] == "sat"][:10]
    assert len(U62) == 62 and len(C20) == 20 and len(S10) == 10, (len(U62), len(C20), len(S10))
    return curve, by, {"U62": U62, "C20": C20, "S10": S10}


def engine_E_sets(B, xR):
    sys.path.insert(0, ENGINE)
    from gf2n import TableField
    from macaulay import descended_E, EQ_MONS, mono_mask
    global _F
    try:
        _F
    except NameError:
        _F = TableField()
    E = descended_E(_F, B, xR)
    masks = [mono_mask(m) for m in EQ_MONS]
    return [frozenset(masks[j] for j in range(len(masks)) if E[k, j]) for k in range(R.NEQ)]


_CL = None


def engine_R4p(fp):
    global _CL
    sys.path.insert(0, ENGINE)
    from closure import Closure
    if _CL is None:
        _CL = Closure(17, 4, 17)
        assert _CL.R == 2618 and _CL.C == 3214
    eqs = [[m >> 1 for m in f] for f in fp]
    assert all(not (m & 1) for f in fp for m in f)
    res, _ = _CL.macaulay_closure(eqs, want_cert=False)
    return {"rank": res["rank"], "one": res["one"], "dims_by_deg": res["dims_by_deg"]}


def verify_witness(fs, c, C4, a):
    """Independent check of a structured W^(1) witness. Returns (ok, why)."""
    ell = set()
    for k in range(R.NEQ):
        if c[k]:
            ell ^= set(fs[k])
    if R.deg(ell) > 1:
        return False, "sum c_k f_k is not linear"
    for mu, k in C4:
        if bin(mu).count("1") > 2:
            return False, "multiplier of degree > 2 in C_4"
    if R.deg(a) > 3:
        return False, "deg a > 3"
    acc = set()
    for mu, k in C4:
        for m in fs[k]:
            acc ^= {mu | m}
    acc ^= R.pmul(ell, a)
    return (acc == {0}), ("ok" if acc == {0} else f"residual has {len(acc)} monomials")


def main():
    t0 = time.time()
    curve, by, sets = load_sets()
    B = curve["B"]
    sp = R.Space(range(1, 18), 4)
    assert sp.C == 3214
    out = {"task": "TASK-20260924-d95e70", "joint": "J7(b)",
           "rule": "prediction-rule.yaml PR-1..PR-5",
           "engine_modules_sha256": {f: sha(os.path.join(ENGINE, f)) for f in ("macaulay.py", "gf2n.py")},
           "source_sha256": {f: sha(os.path.join(SRC, f)) for f in ("curve.json", "targets-F-S3.jsonl.gz")},
           "curve": {"A": curve["A"], "B": B}, "instances": []}
    wit = gzip.open(os.path.join(HERE, "w1-witnesses.jsonl.gz"), "wt")
    for sname in ("U62", "C20", "S10"):
        for idx in sets[sname]:
            rec = by[idx]
            xR = rec["x_R"]
            ti = time.time()
            fs = R.descent(B, xR)
            st = R.selftest_descent(B, xR, fs, trials=32, seed=idx)
            agree = (fs == engine_E_sets(B, xR))
            c, ell = R.ell_of(B, xR, fs)
            c0 = R.gtr(R.gmul(B, R.ginv(R.gmul(xR, xR))))
            want = {1, 1 << 9} | ({0} if c0 else set())
            ell_ok = (ell == want)
            fp = [R.substitute(f, c0) for f in fs]
            # the dependency sum_k c_k f'_k = 0
            dep = set()
            for k in range(R.NEQ):
                if c[k]:
                    dep ^= fp[k]
            ech, labels = R.macaulay(sp, fp, 2, track=True)
            one = 0 in ech.rows
            prof = ech.dims_by_deg(sp.coldeg, 4)
            w = None
            if one:
                p = ech.prov[0]
                C4 = []
                while p:
                    b = p.bit_length() - 1
                    C4.append(labels[b])
                    p ^= 1 << b
                g = set()
                for mu, k in C4:
                    for m in fs[k]:
                        g ^= {mu | m}
                h = g ^ {0}
                a = {m & ~1 for m in h if m & 1}
                assert h == R.pmul(ell, a), "kernel decomposition failed"
                ok, why = verify_witness(fs, c, C4, a)
                w = {"ok": ok, "why": why, "size_C4": len(C4), "deg_a": R.deg(a), "terms_a": len(a)}
                wit.write(json.dumps({"set": sname, "idx": idx, "x_R": xR, "c": c,
                                      "C4": sorted([[mu, k] for mu, k in C4]),
                                      "a": sorted(a), "verified": ok}) + "\n")
            # cross-check R'_4 with the ARCHIVED engine's generic builder,
            # imported unchanged (closure.Closure(nv=17, D=4, neq=17)),
            # variables v_1..v_17 remapped to 0..16.
            eng = engine_R4p(fp)
            pred_W1 = one
            pred_W1_dim = 4048 if ech.rank() == 3214 else None
            inst = {"set": sname, "idx": idx, "x_R": xR, "archived_s": rec["s"],
                    "archived_one_in_R_4": rec["one_in_R"], "archived_rank_4": rec["rank"],
                    "descent_selftest": st, "construction_equals_engine_descended_E": agree,
                    "ell_identity_holds": ell_ok, "c0": c0, "dependency_sum_c_k_fprime_k_is_zero": (dep == set()),
                    "rank_R4p": ech.rank(), "one_in_R4p": one, "fall_profile_R4p_d0_to_d4": prof,
                    "PR1_predict_one_in_W1": pred_W1,
                    "PR2_predict_dim_W1": pred_W1_dim,
                    "PR2_lower_bound_dim_W1": ech.rank() + 834,
                    "engine_R4p": eng,
                    "engine_R4p_agrees": (eng["rank"] == ech.rank() and eng["one"] == one
                                          and eng["dims_by_deg"] == prof),
                    "w1_witness": w, "seconds": round(time.time() - ti, 2)}
            out["instances"].append(inst)
            print(sname, idx, xR, "rank", ech.rank(), "one", one, "prof", prof, "ell", ell_ok,
                  "agree", agree, "st", st, "wit", w and w["ok"], f"{time.time() - ti:.1f}s", flush=True)
    wit.close()
    out["seconds_total"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(HERE, "predictions.json"), "w"), indent=1)
    print("done", out["seconds_total"])


if __name__ == "__main__":
    main()
