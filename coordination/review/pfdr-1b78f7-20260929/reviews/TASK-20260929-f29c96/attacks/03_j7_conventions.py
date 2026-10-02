"""J7: kappa and z at every excursion cell (discovery and Stage R) and the family excursion
count under each declared alternative convention (attacks/choices.yaml, hashed before this
script was written).  Deterministic (no randomness).  Output: attacks/out/03_j7_conventions.json

Conventions: FROZEN; ALT-a1 relations; ALT-a2 n + dup_formal; ALT-a3 pairs recomputed from
rows (as specified); ALT-b1 exposure-normalised; ALT-b2 six-random pool where |F| matches;
ALT-c (A1 does not read poisson_mean: identity); ALT-d1 no censoring drop; ALT-d2 drop only
the affected arm; ALT-e1 structured-arm residual variance; ALT-e2 dispersion-floored V;
ALT-f SS at stop.
"""
import json
import math
import os
import statistics
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rtlib import (EXCURSIONS, OUT, P, RANDOMS, RUNS, RUNGS, STRUCT, build_index,  # noqa: E402
                   canonical_rows, censored, iter_jsonl, usable)

ANALYZE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..")


def load_bundles():
    b = {}
    for line in open(os.path.join(OUT, "out", "02_bundles.jsonl")):
        r = json.loads(line)
        if r["mode"] != "census":
            continue
        want = "A_fix" if r["class"] == "SS" else "stop"
        if r["scope"] != want:
            continue
        src = "sr" if r["file"].startswith(P + "stage-r") else "main"
        b[(src, r["m"], r["bits"], r["curve"], r["arm"], r["class"])] = r
    return b


def frozen_count(r, cl):
    h = r["harvest"]
    return h["SS"]["at_A_fix"]["pairs_nonformal"] if cl == "SS" else h[cl]["at_stop"]["pairs_nonformal"]


def poisson_mean(r, cl):
    h = r["harvest"]
    return h["SS"]["at_A_fix"]["poisson_mean"] if cl == "SS" else h[cl]["at_stop"]["poisson_mean"]


def stats_frozen(nA, nR):
    C_A = float(sum(nA))
    C_R = sum(sum(v) for v in nR) / 3.0
    s2 = sum(statistics.variance(v) for v in nR) if nR else 0.0
    V = max(s2, C_R)
    SD = math.sqrt(V * 4 / 3)
    return {"C_A": C_A, "C_R": C_R, "V": V, "sum_s2": s2, "kappa": C_A / C_R if C_R > 0 else None,
            "z": (C_A - C_R) / SD if SD > 0 else None, "resolved": C_R >= 10}


class Cells:
    def __init__(self):
        self.main = build_index(canonical_rows("census-m3") + canonical_rows("census-m4")
                                + canonical_rows("census-m5"))
        self.sr = build_index(list(iter_jsonl(os.path.join(RUNS, P + "stage-r", "rows.jsonl.gz"))))
        self.bund = load_bundles()
        self.D = self.dispersion_index()

    def ix(self, src):
        return self.main if src == "main" else self.sr

    def dispersion_index(self):
        """D per (class, m, bits): pooled sum s^2 / sum mean over every random triple
        (both families, curves 0..4), frozen counts."""
        out = {}
        for cl in ("TT", "TB", "SS"):
            for m in (3, 4, 5):
                for b in RUNGS:
                    s2 = mu = 0.0
                    for c in range(5):
                        for fam in (RANDOMS["subgroup"], RANDOMS["dickson"]):
                            rs = [self.main.get(("main", m, b, c, a, "census")) for a in fam]
                            if not all(usable(r) for r in rs) or any(censored(r) for r in rs):
                                continue
                            v = [frozen_count(r, cl) for r in rs]
                            s2 += statistics.variance(v)
                            mu += statistics.mean(v)
                    out[(cl, m, b)] = (s2 / mu) if mu > 0 else None
        return out

    def curve_rows(self, src, m, b, c, A, drop="frozen"):
        """(rows for A and its three randoms, reason-or-None)."""
        ix = self.ix(src)
        rs = [ix.get(("main", m, b, c, a, "census")) for a in (A,) + RANDOMS[A]]
        if any(r is None for r in rs):
            return rs, "missing"
        if rs[0]["fb_size"] != rs[1]["fb_size"]:
            return rs, "unmatched_size"
        if not all(usable(r) for r in rs):
            return rs, "status"
        cens = [censored(r) for r in rs]
        if drop == "frozen" and any(cens):
            return rs, "censored"
        if drop == "affected" and cens[0]:
            return rs, "censored_A"
        return rs, None

    def cell(self, conv, src, A, cl, m, b):
        curves = range(5) if src == "main" else range(5, 10)
        drop = {"ALT-d1": "none", "ALT-d2": "affected"}.get(conv, "frozen")
        nA, nR, kept, blocked = [], [], [], []
        extra_R = []  # ALT-b2 pooled randoms
        for c in curves:
            rs, why = self.curve_rows(src, m, b, c, A, drop)
            if why is not None:
                continue
            if conv == "ALT-d2":
                cens = [censored(r) for r in rs]
                use = [rs[0]] + [r for r, cz in zip(rs[1:], cens[1:]) if not cz]
            else:
                use = rs
            if conv in ("ALT-a1", "ALT-a3"):
                vals = []
                for r in use:
                    rec = self.bund.get((src, m, b, c, r["arm"], cl))
                    if rec is None or not rec["complete"]:
                        vals = None
                        break
                    vals.append(rec["relations"] if conv == "ALT-a1" else rec["pairs_from_rows"])
                if vals is None:
                    blocked.append(c)
                    continue
            elif conv == "ALT-a2":
                vals = []
                for r in use:
                    h = r["harvest"]
                    if cl == "SS":
                        a = h["SS"]["at_A_fix"]
                        vals.append(a["pairs_nonformal"] + a["encodings_recorded"] - a["formally_distinct_encodings"])
                    else:
                        vals.append(h[cl]["at_stop"]["pairs_nonformal"] + h[cl]["at_stop"]["dup_formal"])
            elif conv == "ALT-b1":
                mus = [poisson_mean(r, cl) for r in use]
                mref = statistics.mean(mus[1:])
                vals = [frozen_count(r, cl) * (mref / mu) if mu > 0 else 0.0 for r, mu in zip(use, mus)]
            elif conv == "ALT-f":
                vals = [r["harvest"][cl]["at_stop"]["pairs_nonformal"] for r in use]
            else:
                vals = [frozen_count(r, cl) for r in use]
            nA.append(vals[0])
            nR.append(vals[1:])
            kept.append(c)
            if conv == "ALT-b2" and A in ("subgroup", "small_x", "dickson"):
                other = RANDOMS["dickson"] if A != "dickson" else RANDOMS["subgroup"]
                ors = [self.ix(src).get(("main", m, b, c, a, "census")) for a in other]
                if (all(o is not None and usable(o) and not censored(o) for o in ors)
                        and ors[0]["fb_size"] == rs[1]["fb_size"]):
                    extra_R.append([frozen_count(o, cl) for o in ors])
                else:
                    extra_R.append(None)
        if not kept:
            return {"curves_kept": [], "blocked_curves": blocked, "resolved": False, "z": None,
                    "kappa": None}
        if conv == "ALT-d2" or conv == "ALT-b2":
            # variable number of randoms per curve: Var(C_A - C_R) = sum_j V_j (1 + 1/k_j)
            C_A = float(sum(nA))
            refs = []
            for j in range(len(kept)):
                rv = list(nR[j])
                if conv == "ALT-b2" and extra_R and extra_R[j] is not None:
                    rv = rv + extra_R[j]
                refs.append(rv)
            C_R = sum(statistics.mean(v) for v in refs)
            var_s = sum(statistics.variance(v) * (1 + 1 / len(v)) for v in refs if len(v) >= 2)
            var_p = sum(statistics.mean(v) * (1 + 1 / len(v)) for v in refs)
            varD = max(var_s, var_p)
            st = {"C_A": C_A, "C_R": C_R, "V": varD, "kappa": C_A / C_R if C_R > 0 else None,
                  "z": (C_A - C_R) / math.sqrt(varD) if varD > 0 else None, "resolved": C_R >= 10,
                  "randoms_per_curve": [len(v) for v in refs]}
        else:
            st = stats_frozen(nA, nR)
            if conv == "ALT-e2":
                D = self.D.get((cl, m, b)) or 1.0
                V = max(st["sum_s2"], max(D, 1.0) * st["C_R"])
                SD = math.sqrt(V * 4 / 3)
                st.update({"V": V, "D_rung": D, "z": (st["C_A"] - st["C_R"]) / SD if SD > 0 else None})
            if conv == "ALT-e1" and st["C_R"] > 0:
                kh = st["C_A"] / st["C_R"]
                e2 = sum((a - kh * statistics.mean(r)) ** 2 for a, r in zip(nA, nR))
                s2 = st["sum_s2"]
                V_A = max(0.0, (len(nA) / max(1, len(nA) - 1)) * e2 - kh * kh * s2 / 3)
                V_R = max(s2, st["C_R"])
                SD_alt = math.sqrt(V_A + V_R / 3)
                SD_f = math.sqrt(V_R * 4 / 3)
                SD = max(SD_alt, SD_f)
                st.update({"V_A": V_A, "V_R": V_R, "SD_used": SD,
                           "z": (st["C_A"] - st["C_R"]) / SD if SD > 0 else None})
        st.update({"curves_kept": kept, "blocked_curves": blocked, "counts_A": nA, "counts_R": nR})
        return st


def family(C, conv):
    exc, n_res, n_blocked = [], 0, 0
    for m in (3, 4, 5):
        for A in STRUCT:
            for cl in ("TT", "SS"):
                for b in RUNGS:
                    st = C.cell(conv, "main", A, cl, m, b)
                    if st.get("blocked_curves"):
                        n_blocked += 1
                        continue
                    if st["resolved"] and st["z"] is not None:
                        n_res += 1
                        if abs(st["z"]) > 3:
                            exc.append([A, cl, m, b, round(st["z"], 3), round(st["kappa"], 4)])
    return {"resolved_cells": n_res, "cells_blocked": n_blocked, "excursions": exc,
            "excursion_count": len(exc)}


def main():
    C = Cells()
    convs = ["FROZEN", "ALT-a1", "ALT-a2", "ALT-a3", "ALT-b1", "ALT-b2", "ALT-c", "ALT-d1",
             "ALT-d2", "ALT-e1", "ALT-e2", "ALT-f"]
    out = {"dispersion_index_D_rung": {f"{k[0]}|{k[1]}|{k[2]}": v for k, v in sorted(C.D.items())}}
    for conv in convs:
        cells = {}
        for A, cl, m, b in EXCURSIONS:
            for src in ("main", "sr"):
                st = C.cell(conv if conv != "ALT-c" else "FROZEN", src, A, cl, m, b)
                cells[f"{A}|{cl}|{m}|{b}|{'discovery' if src == 'main' else 'stageR'}"] = {
                    k: (round(v, 4) if isinstance(v, float) else v) for k, v in st.items()}
        fam = family(C, conv if conv != "ALT-c" else "FROZEN")
        out[conv] = {"excursion_cells": cells, "family": fam}
        print(conv, "family excursions:", fam["excursion_count"], "resolved", fam["resolved_cells"],
              "blocked", fam["cells_blocked"], file=sys.stderr)
        for k, v in cells.items():
            print("   ", k, "kappa", v.get("kappa"), "z", v.get("z"), "res", v.get("resolved"),
                  "blocked", v.get("blocked_curves"), file=sys.stderr)
    with open(os.path.join(OUT, "out", "03_j7_conventions.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
