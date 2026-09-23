#!/usr/bin/env python3
"""J4 step 2 (TASK-20260923-29e7af, red team). PREDICTIONS, written and sealed
BEFORE pivot-hazards.json is opened (RT-2).

Inputs (all archived, committed at or before becae035f):
  forms-D4.json            -- my own exact affine forms (j4_forms.py)
  curve-constraint.json    -- tau = (1,0,...,0): Tr(x_R) = r_0; every F-S3 x_R has r_0 = Tr(A) = 0
  targets-{F-S3,F-RANDX,F-PLANT}.jsonl.gz -- ONLY idx, D, x_R, degenerate are read.
    No match flag, no 'replay_first_zero', no hazard.

For every F-S3 reference (U1, U2, U3, S1, S2; modal as supplementary) and every
pivot k, three classes against the earlier pivots j < k:
  DEP      a_k lies in span{a_j : j < k, a_j != 0}  (the literal F_2^17 test the
           card asks for).
  DEP_TAU  a_k is NOT in that span, but IS in span{a_j : j < k} + span{tau}.
           On curve targets r_0 = 0 identically, so e_k is constant there.
  IND      neither.
Structural prediction (no data needed beyond the forms and r_ref):
  DEP      h_k = 0 EXACTLY on any target set. Proof: on the survivor set,
           e_k(r) = e_k(r_ref) = 1, because r_ref satisfies every earlier
           condition (self-replay) and a_k is a sum of earlier a_j.
  DEP_TAU  h_k = 0 EXACTLY on curve targets (r_0 = 0 = r_ref,0); on F-RANDX
           targets (r_0 uniform) a nonconstant form on the survivor subspace,
           so about 1/2.
  IND      nonconstant affine form on the survivor affine subspace: exactly
           balanced on the subspace; on the finite curve sample, h_k about 1/2
           with sd 1/(2 sqrt(S_k)). Band stated at 99.9%: 0.5 +- 3.29/(2 sqrt S_k).
A pivot with h_k = 1 cannot occur (r_ref is in every survivor subspace).
Exact recomputation: S_k, zeros_k, h_k from the forms and the archived x_R.

P2 set (spec M2): union over the 5 declared F-S3 references at D = 4 of
(reference, pivot) with e_k nonconstant over the family's non-degenerate
targets (both arms pooled) and S_k >= 200.
"""
import gzip
import hashlib
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = "/home/user/crypto-autoresearcher/experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05"
TAU = 1          # from curve-constraint.json (tau_bits)
DECLARED = ["U1", "U2", "U3", "S1", "S2"]


def targets(fam, D=4):
    out = []
    with gzip.open(os.path.join(RUN, f"targets-{fam}.jsonl.gz"), "rt") as f:
        for line in f:
            d = json.loads(line)
            if d["D"] == D:
                out.append((d["idx"], d["x_R"], bool(d["degenerate"])))
    return out


class Span:
    def __init__(self, init=()):
        self.b = {}
        for v in init:
            self.add(v)

    def reduce(self, v):
        while v:
            h = v.bit_length() - 1
            if h in self.b:
                v ^= self.b[h]
            else:
                return v
        return 0

    def add(self, v):
        v = self.reduce(v)
        if v:
            self.b[v.bit_length() - 1] = v
            return True
        return False

    def dim(self):
        return len(self.b)


def evalf(a0, a, rs):
    rs = np.asarray(rs, dtype=np.int64)
    return ((np.bitwise_count(rs[:, None] & a[None, :]) & 1).astype(np.uint8) ^ a0[None, :])


def hazard(e):
    T, K = e.shape
    zero = (e == 0)
    has0 = zero.any(axis=1)
    fz = np.where(has0, zero.argmax(axis=1), K)
    counts = np.bincount(fz, minlength=K + 1)
    geq = np.cumsum(counts[::-1])[::-1]
    Sk, zk = geq[:K], counts[:K]
    dep = zero.any(axis=0) & (e == 1).any(axis=0)
    return Sk, zk, dep, int(counts[K])


def classify(a):
    lit, mod = Span(), Span([TAU])
    cls, rho_lit, rho_mod = [], [], []
    for x in a:
        x = int(x)
        rho_lit.append(lit.dim())
        rho_mod.append(mod.dim() - 1)
        if x == 0:
            cls.append("CONST")
            continue
        in_lit = lit.reduce(x) == 0
        in_mod = mod.reduce(x) == 0
        cls.append("DEP" if in_lit else ("DEP_TAU" if in_mod else "IND"))
        lit.add(x)
        mod.add(x)
    return cls, rho_lit, rho_mod


def solve_unique(a0, a):
    """Unique r with e_k(r) = 1 for all k, if the system has rank 17."""
    rows = [(int(x), 1 ^ int(c)) for x, c in zip(a, a0) if x]
    piv = {}
    for v, b in rows:
        for h in sorted(piv, reverse=True):
            if (v >> h) & 1:
                v ^= piv[h][0]
                b ^= piv[h][1]
        if v:
            h = v.bit_length() - 1
            for h2 in list(piv):
                if (piv[h2][0] >> h) & 1:
                    piv[h2] = (piv[h2][0] ^ v, piv[h2][1] ^ b)
            piv[h] = (v, b)
        elif b:
            return None, "inconsistent"
    if len(piv) < 17:
        return None, f"rank {len(piv)}"
    r = 0
    for h, (v, b) in piv.items():
        assert v == 1 << h
        r |= b << h
    return r, "unique"


def main():
    forms = json.load(open(os.path.join(HERE, "forms-D4.json")))["refs"]
    cc = json.load(open(os.path.join(HERE, "curve-constraint.json")))
    assert cc["tau_bits"] == TAU
    fams = {f: targets(f) for f in ("F-S3", "F-RANDX", "F-PLANT")}
    refsj = json.load(open(os.path.join(RUN, "references.json")))["F-S3"]["references"]
    cols = json.load(open(os.path.join(RUN, "column-order-D4.json")))["columns"]
    coldeg = {c["col"]: c["degree"] for c in cols}
    out = {"generated_before_opening": "pivot-hazards.json", "tau": TAU, "per_ref": {}, "P2": [],
           "cross": {}}
    for lab in DECLARED + ["modal"]:
        F = forms[lab]
        a0 = np.array(F["a0"], dtype=np.uint8)
        a = np.array(F["a"], dtype=np.int64)
        K = len(a)
        Tst = refsj[lab]["D4"]["T_strict"]
        assert len(Tst) == K
        cls, rho_lit, rho_mod = classify(a)
        ruq, st = solve_unique(a0, a)
        rec = {"x_R": F["x_R"], "K": K, "x_R_r0": F["x_R"] & 1,
               "class_counts": {c: cls.count(c) for c in ("CONST", "DEP", "DEP_TAU", "IND")},
               "full_replay_survivor_set": {"status": st, "r": ruq, "equals_r_ref": ruq == F["x_R"]}}
        # F-S3 scoring set (modal: idx > 100)
        T = [(i, x) for i, x, dg in fams["F-S3"] if not dg and (lab != "modal" or i > 100)]
        rs = [x for _, x in T]
        e = evalf(a0, a, rs)
        Sk, zk, dep, full = hazard(e)
        rec["n_scored"] = len(rs)
        rec["full_replay_survivors"] = full
        rec["K_sampled"] = int(dep.sum())
        rec["K_exact"] = int((a != 0).sum())
        rec["nonzero_but_constant_on_curve_targets"] = [int(k) for k in range(K) if a[k] != 0 and not dep[k]]
        # early window: every pivot up to and including the first with S_k < 200
        win = []
        for k in range(K):
            if k > 0 and Sk[k - 1] < 200:
                break
            h = float(zk[k] / Sk[k]) if Sk[k] else None
            if cls[k] in ("DEP",):
                pred = "0 exactly (any target set)"
            elif cls[k] == "DEP_TAU":
                pred = "0 exactly on curve targets (r_0 = 0); ~1/2 on uniform-x targets"
            elif cls[k] == "IND":
                w = 3.29 / (2 * math.sqrt(Sk[k])) if Sk[k] else None
                pred = f"~1/2, 99.9% band [{0.5 - w:.4f}, {0.5 + w:.4f}]" if w else "n/a"
            else:
                pred = "constant pivot (a_k = 0); not r-dependent"
            win.append({"k": k, "p_k": Tst[k][0], "c_k": Tst[k][1], "deg_c_k": coldeg[Tst[k][1]], "a0": int(a0[k]), "a": int(a[k]), "a_hex": hex(int(a[k])),
                        "class": cls[k], "rho_literal_before": rho_lit[k], "rho_mod_tau_before": rho_mod[k],
                        "sampled_dependent": bool(dep[k]), "S_k": int(Sk[k]), "zeros_k": int(zk[k]),
                        "h_exact_recomputed": h, "structural_prediction": pred,
                        "in_P2": bool(lab in DECLARED and dep[k] and Sk[k] >= 200)})
        rec["early_window"] = win
        # last step at which each rank is first reached
        rec["rank_literal_reaches_17_at_k"] = next((k for k in range(K) if rho_lit[k] == 17), None)
        rec["rank_mod_tau_reaches_16_at_k"] = next((k for k in range(K) if rho_mod[k] == 16), None)
        out["per_ref"][lab] = rec
        if lab in DECLARED:
            for w_ in win:
                if w_["in_P2"]:
                    out["P2"].append({"ref": lab, **{k: w_[k] for k in (
                        "k", "p_k", "c_k", "deg_c_k", "a_hex", "class", "rho_literal_before", "rho_mod_tau_before", "S_k",
                        "zeros_k", "h_exact_recomputed", "structural_prediction")}})
        # cross-scoring on F-RANDX (uniform x) and F-PLANT: discriminates DEP from DEP_TAU
        for fam in ("F-RANDX", "F-PLANT"):
            rs2 = [x for _, x, dg in fams[fam] if not dg]
            e2 = evalf(a0, a, rs2)
            Sk2, zk2, dep2, full2 = hazard(e2)
            cw = []
            for k in range(K):
                if k > 0 and Sk2[k - 1] < 50:
                    break
                cw.append({"k": k, "class": cls[k], "S_k": int(Sk2[k]), "zeros_k": int(zk2[k]),
                           "h_exact_recomputed": float(zk2[k] / Sk2[k]) if Sk2[k] else None,
                           "sampled_dependent": bool(dep2[k])})
            out["cross"].setdefault(fam, {})[lab] = {"n_scored": len(rs2), "full_replay_survivors": full2,
                                                     "early_window": cw}
    # P2 summary as I predict it
    P2 = out["P2"]
    hs = sorted(p["h_exact_recomputed"] for p in P2)
    n = len(hs)
    med = (hs[(n - 1) // 2] + hs[n // 2]) / 2 if n else None
    inband = sum(1 for h in hs if 0.4 <= h <= 0.6)
    out["P2_summary_predicted"] = {
        "n": n, "median_h": med, "frac_in_[0.4,0.6]": inband / n if n else None,
        "n_DEP": sum(p["class"] == "DEP" for p in P2), "n_DEP_TAU": sum(p["class"] == "DEP_TAU" for p in P2),
        "n_IND": sum(p["class"] == "IND" for p in P2),
        "n_exact_zero": sum(h == 0 for h in hs),
        "IND_all_in_band": all(0.4 <= p["h_exact_recomputed"] <= 0.6 for p in P2 if p["class"] == "IND"),
        "restricted_to_rank_increasing_mod_tau": {
            "n": sum(p["class"] == "IND" for p in P2),
            "frac_in_[0.4,0.6]": (sum(0.4 <= p["h_exact_recomputed"] <= 0.6 for p in P2 if p["class"] == "IND")
                                  / max(1, sum(p["class"] == "IND" for p in P2)))},
        "restricted_to_rank_increasing_literal": {
            "n": sum(p["class"] != "DEP" for p in P2),
            "frac_in_[0.4,0.6]": (sum(0.4 <= p["h_exact_recomputed"] <= 0.6 for p in P2 if p["class"] != "DEP")
                                  / max(1, sum(p["class"] != "DEP" for p in P2)))},
    }
    # early-form identity across references (repeated hazard sequences)
    ident = {}
    for i, l1 in enumerate(DECLARED + ["modal"]):
        for l2 in (DECLARED + ["modal"])[i + 1:]:
            f1, f2 = forms[l1], forms[l2]
            n_same = 0
            for k in range(min(len(f1["a"]), len(f2["a"]))):
                if f1["a"][k] == f2["a"][k] and f1["a0"][k] == f2["a0"][k]:
                    n_same += 1
                else:
                    break
            ident[f"{l1}~{l2}"] = n_same
    out["identical_form_prefix_length"] = ident
    s = json.dumps(out, indent=1)
    p = os.path.join(HERE, "predictions-D4.json")
    with open(p, "w") as f:
        f.write(s)
    print("sha256", hashlib.sha256(s.encode()).hexdigest())
    print(json.dumps(out["P2_summary_predicted"], indent=1))
    print(json.dumps(out["identical_form_prefix_length"], indent=1))
    for lab, rec in out["per_ref"].items():
        print(lab, rec["class_counts"], "K_sampled", rec["K_sampled"], "K_exact", rec["K_exact"],
              "const_on_curve", rec["nonzero_but_constant_on_curve_targets"],
              "survivor_set", rec["full_replay_survivor_set"], "full_surv", rec["full_replay_survivors"],
              "lit17@", rec["rank_literal_reaches_17_at_k"], "mod16@", rec["rank_mod_tau_reaches_16_at_k"])


if __name__ == "__main__":
    main()
