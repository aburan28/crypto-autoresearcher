"""J2b(4): certificates for the four degenerate main-census records (b20-r3-n4096, c = 6, 30, 42, 47).

For each: regenerate the curve and the three base points with reviewer code (ownec.py), enumerate the whole
half-box H(3, T) in the frozen order, and record every skipped vector. Certificates:
  exhaustion  : |H(3,T)| vectors enumerated, distinct labels = |H| - duplicate_skips - infinity_skips < n;
  relations   : every duplicate x(v.P) = x(v'.P) gives u = v - v' (same point) or u = v + v' (opposite points)
                with u in [-2T, 2T]^3 and u.P = O; every infinity skip gives u = v in [-T, T]^3 with u.P = O.
                Each distinct u is verified twice: by Jacobian scalar multiplication u1 P1 + u2 P2 + u3 P3 = O,
                and arithmetically, u1 + u2 k2 + u3 k3 = 0 mod N with P_i = k_i P_1 found by own BSGS.
The full collision list is hashed (scratch file, not staged); the distinct relations and their multiplicities
are listed.

usage: python3 -I -B degenerate.py <toy-main-jobs.jsonl> <scratch-dir> <out.json>
"""
import hashlib
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ownec  # noqa: E402

jobs_path, scratch, out_path = sys.argv[1:4]
os.makedirs(scratch, exist_ok=True)
recs = [json.loads(ln) for ln in open(jobs_path) if ln.strip()]
deg = sorted((r for r in recs if r["status"] == "degenerate"), key=lambda r: (r["cell"], r["c"]))


def normalise(u):
    nz = next((e for e in u if e), 0)
    return tuple(u) if nz > 0 else tuple(-e for e in u)


def dlog(E, G, Q, N):
    """k with k G = Q (own baby-step giant-step)."""
    m = math.isqrt(N) + 1
    table = {}
    R = None
    for j in range(m):
        table.setdefault(R, j)
        R = E.add(R, G)
    step = E.neg(E.mul(m, G))
    Y = Q
    for i in range(m + 1):
        if Y in table:
            return (i * m + table[Y]) % N
        Y = E.add(Y, step)
    raise ValueError("no log")


out_recs = []
for r in deg:
    cell, c, n, rk = r["cell"], r["c"], r["n"], r["r"]
    p, a, b, N, _ = ownec.regenerate_curve(r["bits"], ownec.SEED_BLOCK["main"] + c)
    E = ownec.EC(p, a, b)
    labels, meta, extra = ownec.build_gap(E, rk, n, ownec.job_rng("gap", "main", cell, c), record_collisions=True)
    T = meta["T"]
    H = ownec.half_box_size(rk, T)
    pts = extra["points"]
    rel = {}
    for col in extra["collisions"]:
        v, w = col["vector"], col["earlier_vector"]
        u = [x - y for x, y in zip(v, w)] if col["same_point"] else [x + y for x, y in zip(v, w)]
        u = normalise(u)
        rel[u] = rel.get(u, 0) + 1
    for v in extra["infinities"]:
        u = normalise(v)
        rel[u] = rel.get(u, 0) + 1
    ks = [1] + [dlog(E, pts[0], P, N) for P in pts[1:]]
    rel_rows = []
    for u, mult in sorted(rel.items(), key=lambda kv: (-kv[1], max(map(abs, kv[0])))):
        Q = None
        for ui, P in zip(u, pts):
            Q = E.add(Q, E.mul(ui, P))
        rel_rows.append({"u": list(u), "collisions_explained": mult, "max_abs": max(map(abs, u)),
                         "in_box_2T": max(map(abs, u)) <= 2 * T, "u_dot_P_is_O": Q is None,
                         "u_dot_k_mod_N_is_0": sum(x * y for x, y in zip(u, ks)) % N == 0})
    distinct = H - meta["duplicate_skips"] - meta["infinity_skips"]
    coll_txt = json.dumps([[col["earlier_vector"], col["vector"], col["same_point"]] for col in extra["collisions"]])
    fn = os.path.join(scratch, f"collisions-{cell}-c{c}.json")
    with open(fn, "w") as f:
        f.write(coll_txt)
    shortest = min(rel_rows, key=lambda x: (x["max_abs"], -x["collisions_explained"])) if rel_rows else None
    out_recs.append({
        "cell": cell, "c": c, "curve": {"p": p, "a": a, "b": b, "N": N,
                                        "equal_to_record": [p, a, b, N] == [r["p"], r["a"], r["b_coef"], r["N"]]},
        "base_points": [list(P) for P in pts], "dlogs_base_P1": ks,
        "recorded_gap_meta": r["gap_meta"], "regenerated_gap_meta": meta,
        "gap_meta_equal": meta == r["gap_meta"],
        "exhaustion_certificate": {"half_box_size": H, "enumerated": meta["enumerated"],
                                   "duplicate_skips": meta["duplicate_skips"], "infinity_skips": meta["infinity_skips"],
                                   "distinct_labels": distinct, "n": n, "exhausted_before_n": meta["enumerated"] == H and distinct < n,
                                   "builder_returned_no_set": labels is None},
        "relation_certificate": {"distinct_relations": len(rel_rows), "shortest": shortest,
                                 "all_relations_verified": all(x["u_dot_P_is_O"] and x["u_dot_k_mod_N_is_0"] and x["in_box_2T"] for x in rel_rows),
                                 "collisions_total": len(extra["collisions"]) + len(extra["infinities"]),
                                 "collisions_explained_total": sum(x["collisions_explained"] for x in rel_rows),
                                 "relations": rel_rows[:12]},
        "first_5_collisions": [[col["earlier_vector"], col["vector"], "same point" if col["same_point"] else "opposite points"]
                               for col in extra["collisions"][:5]],
        "infinity_vectors": extra["infinities"],
        "full_collision_list_sha256_not_staged": hashlib.sha256(coll_txt.encode()).hexdigest(),
        "status_record": r["status"], "record_fields_null": [k for k in ("null_C", "null_D", "gap_C", "gap_D", "plant_m",
                                                                          "plant_internal", "plant_C", "plant_D", "plant_feasible") if r[k] is None],
    })
out = {"script": "scripts/degenerate.py (own arithmetic: scripts/ownec.py)", "python": sys.version,
       "executable": sys.executable, "degenerate_records_in_main_jobs": len(deg),
       "records": out_recs,
       "summary": {"all_regenerate_degenerate": all(x["exhaustion_certificate"]["exhausted_before_n"] for x in out_recs),
                   "all_gap_meta_equal": all(x["gap_meta_equal"] for x in out_recs),
                   "all_relations_verified": all(x["relation_certificate"]["all_relations_verified"] for x in out_recs),
                   "all_curves_equal": all(x["curve"]["equal_to_record"] for x in out_recs)}}
with open(out_path, "w") as f:
    json.dump(out, f, indent=1)
    f.write("\n")
print(json.dumps(out["summary"]))
for x in out_recs:
    print(x["cell"], x["c"], x["exhaustion_certificate"], x["relation_certificate"]["distinct_relations"],
          x["relation_certificate"]["shortest"])
