"""J2b(1): regenerate and recount the 33 pre-selected main-census jobs with reviewer-written code.

For each job of outputs/recount-selection.json (fixed before any count was read): regenerate the curve
(bits, seed 8,100,000 + c), the r base points and the log-GAP set, the 20 null sets and the planted set with
scripts/ownec.py (own builders, own group law, own Jacobi symbol and Cipolla roots; seeding convention read from
run.py / vendor/curve.py), count C and D of every set with own counters that never call labelsum.c, and compare
p, a, b_coef, N, gap_C, gap_D, gap_meta, null_C, null_D, plant_m, plant_internal, plant_C, plant_D and
plant_feasible with the record, field by field.

Counters:  A = numpy pair-sum array, sort, run lengths (every set);
           B = numpy histogram np.bincount over [0, p) (every set when p < 2^25);
           P = pure-Python dict prefix counter (plant prefixes; it decides plant_m and plant_internal).
Mode --sets-only (no numpy; any interpreter): regenerate the sets only and print their sha256 digests, using the
recorded null_C for the plant threshold; used to show the regenerated sets are interpreter-independent.

usage: python3 -I -B recount.py <toy-main-jobs.jsonl> <recount-selection.json> <out.json> [--sets-only] [--workers 2]
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ownec  # noqa: E402

args = sys.argv[1:]
SETS_ONLY = "--sets-only" in args
WORKERS = int(args[args.index("--workers") + 1]) if "--workers" in args else 1
jobs_path, sel_path, out_path = [a for a in args if not a.startswith("--") and not a.isdigit()][:3]

if not SETS_ONLY:
    import numpy as np

    def pair_sums(labels, p):
        x = np.asarray(labels, dtype=np.int64)
        n = len(x)
        s = np.empty(n * (n - 1) // 2, dtype=np.int64)
        off = 0
        for i in range(n - 1):
            k = n - 1 - i
            s[off:off + k] = x[i] + x[i + 1:]
            off += k
        return np.where(s >= p, s - p, s)

    def count_sort(labels, p):
        s = pair_sums(labels, p)
        s.sort(kind="stable")
        if len(s) == 0:
            return 0, 0
        cut = np.flatnonzero(s[1:] != s[:-1]) + 1
        edges = np.concatenate(([0], cut, [len(s)]))
        L = np.diff(edges).astype(np.int64)
        return int((L * (L - 1) // 2).sum()), int(len(L))

    def count_hist(labels, p):
        m = np.bincount(pair_sums(labels, p), minlength=p).astype(np.int64)
        return int((m * (m - 1) // 2).sum()), int(np.count_nonzero(m))


def one(job):
    rec = job["record"]
    cell, c, bits, r, n = rec["cell"], rec["c"], rec["bits"], rec["r"], rec["n"]
    t0 = time.time()
    p, a, b, N, _ = ownec.regenerate_curve(bits, ownec.SEED_BLOCK["main"] + c)
    E = ownec.EC(p, a, b)
    res = {"cell": cell, "c": c, "selection_hash": job["selection_hash"], "fields": {}, "checks": {}}
    F = res["fields"]

    def put(name, recorded, mine):
        F[name] = {"recorded": recorded, "recount": mine, "equal": recorded == mine}

    put("p", rec["p"], p)
    put("a", rec["a"], a)
    put("b_coef", rec["b_coef"], b)
    put("N", rec["N"], N)
    gap, meta, extra = ownec.build_gap(E, r, n, ownec.job_rng("gap", "main", cell, c))
    put("gap_meta", rec["gap_meta"], meta)
    nulls = [ownec.build_null(E, n, ownec.job_rng("null", "main", cell, c, k)) for k in range(20)]
    sets_ok = {
        "gap_built": gap is not None,
        "all_sets_n_distinct": all(len(set(s)) == n for s in nulls + ([gap] if gap else [])),
        "all_labels_in_L": all(E.in_L(x) for s in nulls + ([gap] if gap else []) for x in s),
        "base_points_on_curve": all(E.on(P) for P in extra["points"]),
    }
    # verify the first 8 and last 8 gap labels by Jacobian scalar multiplication of their coefficient vectors
    # (independent of the enumeration's affine addition path), and the label order against those vectors
    if gap is not None:
        vecs = extra["vectors"]
        idx = sorted(set(list(range(min(8, n))) + list(range(max(0, n - 8), n))))
        good = 0
        for i in idx:
            Q = None
            for ci, P in zip(vecs[i], extra["points"]):
                Q = E.add(Q, E.mul(ci, P))
            good += Q is not None and Q[0] == gap[i]
        sets_ok["gap_labels_verified_by_scalar_mult"] = good == len(idx)
        sets_ok["gap_labels_verified_by_scalar_mult_count"] = len(idx)
        sets_ok["gap_vectors_strictly_lexicographic"] = all(vecs[i] < vecs[i + 1] for i in range(len(vecs) - 1))
    res["checks"].update(sets_ok)
    digests = {"gap": ownec.set_digest(gap) if gap else None, "null": [ownec.set_digest(s) for s in nulls]}
    if SETS_ONLY:
        pl, pm = ownec.build_plant(E, n, ownec.job_rng("plant", "main", cell, c), rec["null_C"])
        digests["plant"] = ownec.set_digest(pl)
        res["digests"] = digests
        res["plant_meta_from_recorded_null_C"] = {k: pm[k] for k in ("m", "internal", "feasible")}
        res["seconds"] = round(time.time() - t0, 2)
        return res
    use_hist = p < (1 << 25)
    nullA = [count_sort(s, p) for s in nulls]
    gapA = count_sort(gap, p)
    put("null_C", rec["null_C"], [x[0] for x in nullA])
    put("null_D", rec["null_D"], [x[1] for x in nullA])
    put("gap_C", rec["gap_C"], gapA[0])
    put("gap_D", rec["gap_D"], gapA[1])
    pl, pm = ownec.build_plant(E, n, ownec.job_rng("plant", "main", cell, c), [x[0] for x in nullA])
    plA = count_sort(pl, p)
    put("plant_m", rec["plant_m"], pm["m"])
    put("plant_internal", rec["plant_internal"], pm["internal"])
    put("plant_feasible", rec["plant_feasible"], pm["feasible"])
    put("plant_C", rec["plant_C"], plA[0])
    put("plant_D", rec["plant_D"], plA[1])
    res["checks"]["plant_set_n_distinct_in_L"] = len(set(pl)) == n and all(E.in_L(x) for x in pl)
    res["checks"]["plant_internal_counter_P_equals_counter_A"] = count_sort(pl[: pm["m"]], p)[0] == pm["internal"]
    res["checks"]["plant_threshold_float_vs_exact_agree"] = pm["exact_threshold_agrees"]
    res["checks"]["plant_m_minimal"] = (pm["m"] == 4 or not pm["feasible"]
                                       or count_sort(pl[: pm["m"] - 1], p)[0] < pm["thr_float"])
    if use_hist:
        B = [count_hist(s, p) for s in nulls + [gap, pl]]
        A = nullA + [gapA, plA]
        res["checks"]["counter_B_histogram_equals_counter_A_on_all_22_sets"] = B == A
    else:
        res["checks"]["counter_B_histogram_equals_counter_A_on_all_22_sets"] = "not run (p >= 2^25: histogram too large)"
    pairs = n * (n - 1) // 2
    res["checks"]["identity_C_ge_pairs_minus_D_all_sets"] = all(C >= pairs - D for C, D in nullA + [gapA, plA])
    res["digests"] = dict(digests, plant=ownec.set_digest(pl))
    res["all_fields_equal"] = all(v["equal"] for v in F.values())
    res["seconds"] = round(time.time() - t0, 2)
    # keep the report small: long lists only when they differ
    for k in ("null_C", "null_D"):
        if F[k]["equal"]:
            F[k] = {"equal": True, "count": 20}
    return res


if __name__ == "__main__":
    with open(sel_path) as f:
        sel = json.load(f)
    want = {(j["cell"], j["c"]): j for j in sel["jobs"]}
    found = {}
    for ln in open(jobs_path):
        if ln.strip():
            r = json.loads(ln)
            if (r["cell"], r["c"]) in want and r["block"] == "main":
                found[(r["cell"], r["c"])] = r
    todo = [{"record": found[k], "selection_hash": want[k]["selection_hash"]} for k in want]
    todo.sort(key=lambda j: -j["record"]["n"])
    t0 = time.time()
    if WORKERS > 1:
        from multiprocessing import Pool
        with Pool(WORKERS) as pool:
            results = pool.map(one, todo, chunksize=1)
    else:
        results = [one(j) for j in todo]
    order = [(j["cell"], j["c"]) for j in sel["jobs"]]
    results.sort(key=lambda r: order.index((r["cell"], r["c"])))
    out = {"script": "scripts/recount.py" + (" --sets-only" if SETS_ONLY else ""), "python": sys.version,
           "executable": sys.executable, "selection_file": os.path.basename(sel_path),
           "jobs": results, "wall_seconds": round(time.time() - t0, 1)}
    if not SETS_ONLY:
        nf = sum(1 for r in results for v in r["fields"].values() if not v["equal"])
        out["summary"] = {"jobs": len(results), "jobs_all_fields_equal": sum(r["all_fields_equal"] for r in results),
                          "field_comparisons": sum(len(r["fields"]) for r in results), "field_mismatches": nf,
                          "checks_failed": [(r["cell"], r["c"], k) for r in results for k, v in r["checks"].items()
                                            if v is False]}
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    print(json.dumps(out.get("summary"), indent=0) if not SETS_ONLY else f"{len(results)} jobs digests written",
          "wall", out["wall_seconds"])
