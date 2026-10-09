#!/usr/bin/env python3
"""EXP-ECDLP-84af7b (H-ECDLP-2f1033, SNFS-G1): cyclotomic lift with complete splitting.

For toy Mersenne primes p = 2^c - 1 and rank-0 curves E/Q, lift E to every subfield K of
Q(zeta_c) of degree d <= dmax (Gaussian-period polynomials; p splits completely in each) and
to seeded random fields of the same degree in which p also splits completely. Enumerate
K-points in a work ladder, reduce at every degree-one prime above p, and record: distinct
residues D(W), non-torsion new points N(W), the relation yield ratio R(W) = N/D, the covering
exponent gamma, residue coincidences, and the trace relation [T] * sum_i r_i(P) = O at every
point (CTRL-TRACE). Pure Python 3 standard library; PARI/GP, when present, supplies the
optional CTRL-RANK0 (ellrank over Q) and field discriminants. Observations only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import random
import subprocess
import sys
import time
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ecnf  # noqa: E402
import gptool  # noqa: E402
import nfield  # noqa: E402

EXP = "EXP-ECDLP-84af7b"
HYP = "H-ECDLP-2f1033"

# rank-0 curves over Q (recalled; CTRL-RANK0 re-checks with PARI when available)
CURVES = [
    {"label": "32a2", "ainvs": [0, 0, 0, -1, 0], "note": "y^2 = x^3 - x, CM by Z[i], rank 0 (1 is not congruent)"},
    {"label": "congruent-2", "ainvs": [0, 0, 0, -4, 0], "note": "y^2 = x^3 - 4x, rank 0 (2 is not congruent)"},
    {"label": "congruent-3", "ainvs": [0, 0, 0, -9, 0], "note": "y^2 = x^3 - 9x, rank 0 (3 is not congruent)"},
    {"label": "36a1", "ainvs": [0, 0, 0, 0, 1], "note": "y^2 = x^3 + 1, CM by Z[zeta_3], rank 0"},
    {"label": "mordell-m1", "ainvs": [0, 0, 0, 0, -1], "note": "y^2 = x^3 - 1, rank 0"},
    {"label": "11a1", "ainvs": [0, -1, 1, -10, -20], "note": "non-CM, rank 0 (Cremona 11a1, recalled a-invariants)"},
    {"label": "14a1", "ainvs": [1, 0, 1, 4, -6], "note": "non-CM, rank 0 (Cremona 14a1, recalled a-invariants)"},
]


def b_model(a1, a2, a3, a4, a6):
    """(a2', a4', a6') with y'^2 = x^3 + a2' x^2 + a4' x + a6' isomorphic over Q to [a1,a2,a3,a4,a6]
    via y' = y + (a1 x + a3)/2: the x-coordinate is unchanged, so torsion points stay in small shells."""
    return (Fraction(a1 * a1 + 4 * a2, 4), Fraction(2 * a4 + a1 * a3, 2), Fraction(a3 * a3 + 4 * a6, 4))


def abelian_control_conductors(c, d, p, count):
    """The `count` smallest primes m = 1 mod d, m != c, such that p is a d-th power residue mod m,
    i.e. p splits completely in the cyclic degree-d subfield of Q(zeta_m). Same Galois structure
    as the cyclotomic arm (cyclic of order d), different conductor; p's splitting is accidental
    rather than forced by 2^c = 1 mod p."""
    out = []
    m = d + 1
    while len(out) < count:
        if m != c and nfield._is_prime(m) and (m - 1) % d == 0 and pow(p, (m - 1) // d, m) == 1:
            out.append(m)
        m += d
    return out


_FIELD_CACHE = {}


def field_record(fld, K):
    """Field metadata: polynomial discriminant, PARI nfdisc when gp is present, and the field root
    discriminant: exact m^((d-1)/d) for a cyclic degree-d subfield of Q(zeta_m) with m prime
    (conductor-discriminant formula), else from nfdisc, else the polynomial bound (flagged)."""
    key = tuple(fld["g"])
    if key not in _FIELD_CACHE:
        rec = dict(fld, disc=K.discriminant(), root_discriminant_poly=K.root_discriminant())
        rec["nfdisc_pari"] = gptool.nfdisc(fld["g"]) if K.d > 1 else 1
        if fld.get("conductor"):
            m, d = fld["conductor"], fld["d"]
            rec["field_disc"] = m ** (d - 1) if d > 1 else 1
            rec["field_disc_source"] = "conductor-discriminant formula (cyclic, prime conductor)"
            if rec["nfdisc_pari"] is not None and K.d > 1:
                rec["ctrl_disc_pari_agrees"] = abs(rec["nfdisc_pari"]) == rec["field_disc"]
        elif rec["nfdisc_pari"] is not None:
            rec["field_disc"] = abs(rec["nfdisc_pari"])
            rec["field_disc_source"] = "PARI nfdisc"
        else:
            rec["field_disc"] = abs(rec["disc"])
            rec["field_disc_source"] = "polynomial discriminant (upper bound; gp absent)"
        rec["root_discriminant_field"] = rec["field_disc"] ** (1.0 / K.d) if K.d > 1 else 1.0
        _FIELD_CACHE[key] = rec
    return _FIELD_CACHE[key]


def subfield_degrees(c, dmax):
    return [d for d in range(2, dmax + 1) if (c - 1) % d == 0]


def fit_gamma(rungs):
    """Slope of log D against log W over the last three rungs with D > 0 and increasing W."""
    pts = [(math.log(r["work"]), math.log(r["distinct_residues"])) for r in rungs if r["distinct_residues"] > 0]
    pts = pts[-3:]
    if len(pts) < 2:
        return None
    n = len(pts)
    mx = sum(x for x, _ in pts) / n
    my = sum(y for _, y in pts) / n
    sxx = sum((x - mx) ** 2 for x, _ in pts)
    if sxx == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in pts) / sxx


def run_cell(K, A, B, a2, p, ladder, aux, split_for_T, T, seed):
    """One enumeration up to max(ladder) candidates; each rung is a snapshot of the cumulative
    state when `tried` first reaches that rung's work budget."""
    E = ecnf.CurveNF(K, A, B, a2)
    ladder = sorted(set(ladder))
    rungs = []
    all_points = {}
    residues = set()
    cum = {"coincidences": 0, "new_nontorsion": 0, "trace_ok": 0, "trace_fail": 0, "rational": 0,
           "no_residue": 0}
    min_height = None
    rung_i = 0
    last_tried, last_shells = 0, 0

    def snapshot(tried, shells):
        D = len(residues)
        rungs.append({"work": tried, "shells_completed": shells, "points_found_cumulative": len(all_points),
                      "distinct_residues": D, "new_nontorsion_points": cum["new_nontorsion"],
                      "relation_yield_ratio": (cum["new_nontorsion"] / D) if D else None,
                      "residue_coincidences": cum["coincidences"], "rational_points_seen": cum["rational"],
                      "points_without_residue": cum["no_residue"],
                      "trace_relation_ok": cum["trace_ok"], "trace_relation_fail": cum["trace_fail"],
                      "min_new_point_log_height_over_log_p": (min_height / math.log(p)) if min_height is not None else None})

    for kind, tried, shells, P in E.iter_search(aux, ladder[-1], checkpoints=ladder, seed=seed):
        last_tried, last_shells = tried, shells
        if kind == "checkpoint":
            while rung_i < len(ladder) and tried >= ladder[rung_i]:
                snapshot(tried, shells)
                rung_i += 1
            continue
        if kind != "point":
            continue
        key = (P[0], P[1])
        if key in all_points:
            continue
        all_points[key] = True
        res = ecnf.residues_at_p(E, P, p)
        if any(r is None for r in res):
            cum["no_residue"] += 1
            continue
        uniq = set(res)
        cum["coincidences"] += len(res) - len(uniq)
        residues |= uniq
        tr = ecnf.trace_relation_holds(E, res, p, T)
        if tr:
            cum["trace_ok"] += 1
        elif tr is False:
            cum["trace_fail"] += 1
        if K.is_rational(P[0]) and K.is_rational(P[1]):
            cum["rational"] += 1
            continue
        if not ecnf.is_torsion_candidate(E, P, split_for_T, T):
            cum["new_nontorsion"] += 1
            h = K.height(P[0])
            min_height = h if min_height is None else min(min_height, h)
    while rung_i < len(ladder):
        snapshot(last_tried, last_shells)
        rung_i += 1
    return {"rungs": rungs, "gamma": fit_gamma(rungs),
            "max_relation_yield_ratio": max((r["relation_yield_ratio"] or 0) for r in rungs),
            "total_new_nontorsion_points": cum["new_nontorsion"],
            "trace_relation_failures": cum["trace_fail"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--c", type=int, nargs="+", default=[13, 17, 19, 31])
    ap.add_argument("--dmax", type=int, default=12)
    ap.add_argument("--ladder", type=int, nargs="+", default=[300, 1000, 3000, 10000, 30000, 100000])
    ap.add_argument("--curves", type=int, default=len(CURVES))
    ap.add_argument("--random-fields", type=int, default=2)
    ap.add_argument("--abelian-controls", type=int, default=3)
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--aux-primes", type=int, default=8)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    started = time.time()
    cell_seconds = []
    raw = {"experiment_id": EXP, "hypothesis_id": HYP, "gp_version": gptool.gp_version(),
           "curves": [], "cells": []}
    # curves and CTRL-RANK0
    curves = []
    for cv in CURVES[: args.curves]:
        a2, A, B = b_model(*cv["ainvs"])
        rk = gptool.ellrank_Q(cv["ainvs"])
        row = dict(cv, model={"a2": str(a2), "a4": str(A), "a6": str(B)}, ctrl_rank0=rk)
        excluded = rk is not None and rk.get("rank_upper", 0) != 0
        row["excluded_not_rank0"] = excluded
        raw["curves"].append(row)
        if not excluded:
            curves.append((cv["label"], a2, A, B))
    for seed in args.seeds:
        for c in args.c:
            p = 2 ** c - 1
            assert nfield._is_prime(p)
            fields = [{"kind": "cyclotomic", "d": 1, "g": [0, 1], "label": "Q"}]
            for d in subfield_degrees(c, args.dmax):
                g = nfield.gaussian_period_polynomial(c, d)
                fields.append({"kind": "cyclotomic", "d": d, "g": g, "conductor": c, "label": f"Q(zeta_{c})^({d})"})
            controls = []
            for f in [x for x in fields if x["d"] > 1]:
                Kc = nfield.NumberField(f["g"])
                for m in abelian_control_conductors(c, f["d"], p, args.abelian_controls):
                    g = nfield.gaussian_period_polynomial(m, f["d"])
                    controls.append({"kind": "abelian_control", "d": f["d"], "g": g, "conductor": m,
                                     "label": f"Q(zeta_{m})^({f['d']})"})
                for i in range(args.random_fields):
                    rf = nfield.random_split_field(f["d"], p, seed=f"{seed}:{i}", target_rootdisc=Kc.root_discriminant())
                    if rf and rf["g"] != f["g"]:
                        controls.append({"kind": "random_split", "d": f["d"], "g": rf["g"], "label": f"rand{i}(d={f['d']})"})
                    elif rf is None:
                        raw["cells"].append({"seed": seed, "c": c, "p": p, "field": {"kind": "random_split", "d": f["d"]},
                                             "invalid": f"no random completely split field of degree {f['d']} found (search exhausted)"})
            for fld in fields + controls:
                K = nfield.NumberField(fld["g"])
                if K.d > 1 and not K.splits_completely(p):
                    raw["cells"].append({"seed": seed, "c": c, "p": p, "field": fld, "invalid": "CTRL-SPLIT failed"})
                    continue
                aux = K.degree_one_primes(args.aux_primes, avoid=(p,))
                split_for_T = aux[:6]
                rng = random.Random(f"{EXP}:order:{seed}:{c}")
                for label, a2, A, B in curves:
                    T = ecnf.torsion_bound(ecnf.CurveNF(K, A, B, a2), split_for_T,
                                           lambda q, a, b: ecnf.fp_order_bsgs(q, a, b, rng))
                    t0 = time.time()
                    cell = run_cell(K, A, B, a2, p, args.ladder, aux, split_for_T, T, seed)
                    cell.update({"seed": seed, "c": c, "p": p, "field": field_record(fld, K),
                                 "curve": label, "torsion_bound_T": T})
                    raw["cells"].append(cell)
                    cell_seconds.append(round(time.time() - t0, 3))
                    print(f"seed={seed} c={c} {fld['label']} {label}: D={cell['rungs'][-1]['distinct_residues']} "
                          f"N={cell['total_new_nontorsion_points']} Rmax={cell['max_relation_yield_ratio']:.3f} "
                          f"gamma={cell['gamma']} trace_fail={cell['trace_relation_failures']}", file=sys.stderr, flush=True)
    # summary per (c, d): cyclotomic vs random
    summ = {}
    for cell in raw["cells"]:
        if "invalid" in cell:
            continue
        key = f"c={cell['c']} d={cell['field']['d']}"
        s = summ.setdefault(key, {"cyclotomic": [], "abelian_control": [], "random_split": []})
        s[cell["field"]["kind"]].append({"gamma": cell["gamma"], "Rmax": cell["max_relation_yield_ratio"],
                                         "N": cell["total_new_nontorsion_points"]})
    for key, s in summ.items():
        def mean(xs):
            xs = [x for x in xs if x is not None]
            return sum(xs) / len(xs) if xs else None
        for arm in ("abelian_control", "random_split"):
            s[f"gamma_cyclotomic_minus_{arm}"] = (
                mean([x["gamma"] for x in s["cyclotomic"]]) - mean([x["gamma"] for x in s[arm]])
                if s[arm] and s["cyclotomic"] and mean([x["gamma"] for x in s["cyclotomic"]]) is not None
                and mean([x["gamma"] for x in s[arm]]) is not None else None)
            s[f"N_cyclotomic_minus_{arm}"] = (
                mean([x["N"] for x in s["cyclotomic"]]) - mean([x["N"] for x in s[arm]])
                if s[arm] and s["cyclotomic"] else None)
            s[f"Rmax_{arm}"] = max((x["Rmax"] for x in s[arm]), default=None)
        s["Rmax_cyclotomic"] = max((x["Rmax"] for x in s["cyclotomic"]), default=None)
    raw["summary"] = summ
    raw["trace_relation_failures_total"] = sum(c.get("trace_relation_failures", 0) for c in raw["cells"] if "invalid" not in c)
    raw_path = os.path.join(args.out, "raw-result.json")
    with open(raw_path, "w", encoding="utf-8") as fh:
        json.dump(raw, fh, indent=1, sort_keys=True, default=str)
    here = os.path.dirname(os.path.abspath(__file__))
    manifest = {"experiment_id": EXP, "command": " ".join(sys.argv), "python": platform.python_version(),
                "platform": platform.platform(), "gp_version": raw["gp_version"],
                "source_sha256": {f: hashlib.sha256(open(os.path.join(here, f), "rb").read()).hexdigest()
                                  for f in ("run.py", "nfield.py", "ecnf.py", "gptool.py")},
                "raw_result_sha256": hashlib.sha256(open(raw_path, "rb").read()).hexdigest(),
                "started_unix": started, "finished_unix": time.time(),
                "wall_clock_seconds": round(time.time() - started, 3), "cell_seconds": cell_seconds,
                "raw_result_is_replay_deterministic": "raw-result.json carries no timing; CTRL-REPLAY compares it byte for byte",
                "asserts_nothing_about": "the hypothesis; observations only"}
    try:
        manifest["git_commit"] = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:  # noqa: BLE001
        manifest["git_commit"] = None
    with open(os.path.join(args.out, "manifest.yaml"), "w", encoding="utf-8") as fh:
        for k, v in manifest.items():
            fh.write(f"{k}: {json.dumps(v)}\n")


if __name__ == "__main__":
    main()
