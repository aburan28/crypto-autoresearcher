"""J-VAL (4): G-REL-style recount of TT (and TB) relation counts at m = 4, EXP-PFDR-0b3699 RA-04.
TASK-20261009-33b5cf. Independent reader: standard library only; no producer code
(analyze_a.py, harvest.py, run_jobs.py) is imported or copied. Written from the text of
experiments/EXP-PFDR-011cd0/specification.yaml counting_conventions CC-1, CC-1b, CC-2,
CC-3, CC-4, CC-7 and EC-2 (R_star, multiplicity histogram):

  Within one (instance, class), x-groups are the star rows sharing their first element
  (elements[0]). For a group with star rows row_2..row_k, pair (1, j) carries row_j and
  pair (i, j), 2 <= i < j, carries row_j - row_i; a row is the integer vector
  (c_1..c_|F| over base indices ascending, kcoef, rhs). Each relation is reduced mod N
  (N = the curve's group order from design.json); a zero vector is dropped. MONIC: multiply
  by the inverse mod N of the first nonzero coordinate. Distinct relation = distinct monic
  vector (relations_distinct). Sign-only (CC-1b): the lexicographically smaller of v and
  -v mod N (relations_distinct_sign). Nonformal (CC-2): every relation of a generic or
  planted arm (empty formal basis) -- the row's own "formal" flag is also tallied.
  R_star: distinct monic vectors among the star-row relations (pairs (1, j)) only.
  Multiplicity M_r = number of pairs carrying r; histogram {M: #relations}.

Sampling rule: attacks/j-val/sampling-rule.yaml (written before any count was read).
Sources read: design.json (curves, N, S); every job's harvest-rows.jsonl.gz and
rows.jsonl.gz under the run's attempt-1/jobs/; the run-root rows.jsonl.gz.
planted_target is derived from planted_sub per controls_design_notes: on curves in S
every relation; elsewhere the curve's planted TT monic vector (fb_params of the
planted_sub census row; indices [a,b,c,d], signs [1,1,-1,-1]) removed by exact match.
Seed: the sample uses random.Random(f"TASK-20261009-33b5cf|J-VAL|G-REL-recount|{b}").
Usage: python recount.py <repo> <out-summary.json> <scratch-percurve.jsonl.gz>
"""
import gzip
import json
import math
import os
import random
import sys
from collections import Counter, defaultdict

RUN = "experiments/EXP-PFDR-0b3699/runs/RUN-PFDR-0b3699-table"
DESIGN = "experiments/EXP-PFDR-0b3699/runs/RUN-PFDR-0b3699-p0-design/design.json"
ARMS = ["subgroup", "small_x", "random_sub_r0", "random_sub_r1", "random_sub_r2",
        "known_null_sub", "planted_sub", "small_x_offset"]
NULLS = ["random_sub_r0", "random_sub_r1", "random_sub_r2", "known_null_sub"]
CLASSES = ("TT", "TB")


def vec_of(row):
    d = defaultdict(int)
    for idx, c in row["coeffs"]:
        d[int(idx)] += int(c)
    return d, int(row["kcoef"]), int(row["rhs"])


def sub(a, b):
    da, ka, ra = a
    db, kb, rb = b
    d = defaultdict(int, da)
    for i, c in db.items():
        d[i] -= c
    return d, ka - kb, ra - rb


def reduce_vec(v, N):
    """Dense-order tuple of (idx, value mod N) for nonzero base coords, then kcoef, rhs."""
    d, k, r = v
    coords = tuple((i, c % N) for i, c in sorted(d.items()) if c % N)
    return coords, k % N, r % N


def first_nonzero(rv):
    coords, k, r = rv
    if coords:
        return coords[0][1]
    if k:
        return k
    if r:
        return r
    return 0


def scale(rv, s, N):
    coords, k, r = rv
    return tuple((i, (c * s) % N) for i, c in coords), (k * s) % N, (r * s) % N


def monic(rv, N):
    a = first_nonzero(rv)
    return scale(rv, pow(a, -1, N), N)


def sign_norm(rv, N):
    # v vs -v: equal up to the first nonzero coordinate (zero in both), which is a vs N - a.
    a = first_nonzero(rv)
    return rv if a < N - a else scale(rv, N - 1, N)


def recount_instance(rows, N):
    groups = defaultdict(list)
    order = []
    formal_flags = Counter()
    for r in rows:
        key = json.dumps(r["elements"][0], sort_keys=True)
        if key not in groups:
            order.append(key)
        groups[key].append(vec_of(r))
        formal_flags[bool(r.get("formal"))] += 1
    mult = Counter()
    sign_set = set()
    star = set()
    zero_pairs = 0
    pairs = 0
    for key in order:
        g = groups[key]
        rels = []
        for j in range(len(g)):
            rels.append((g[j], True))
            for i in range(j):
                rels.append((sub(g[j], g[i]), False))
        for v, is_star in rels:
            pairs += 1
            rv = reduce_vec(v, N)
            if first_nonzero(rv) == 0:
                zero_pairs += 1
                continue
            m = monic(rv, N)
            mult[m] += 1
            sign_set.add(sign_norm(rv, N))
            if is_star:
                star.add(m)
    return {"relations_distinct": len(mult), "relations_distinct_sign": len(sign_set),
            "R_star": len(star), "multiplicity_histogram": dict(Counter(mult.values())),
            "relation_pairs": pairs, "relation_pairs_zero": zero_pairs,
            "rows": len(rows), "rows_flag_formal": formal_flags[True], "set": set(mult)}


def planted_tt_monic(fb_params, N):
    for pr in fb_params.get("planted_relations", []):
        if pr["class"] == "TT":
            d = defaultdict(int)
            for i, s in zip(pr["indices"], pr["signs"]):
                d[int(i)] += int(s)
            return monic(reduce_vec((d, 0, 0), N), N)
    return None


def main():
    repo, out_summary, out_percurve = sys.argv[1], sys.argv[2], sys.argv[3]
    design = json.load(open(os.path.join(repo, DESIGN)))
    Nof = {(c["bits"], c["curve"]): int(c["N"]) for c in design["curves"]}
    S = {int(b): set(v) for b, v in design["S"].items()}
    curves_b = {b: sorted(c for (bb, c) in Nof if bb == b) for b in (30, 32)}
    sample = {b: set(random.Random(f"TASK-20261009-33b5cf|J-VAL|G-REL-recount|{b}").sample(curves_b[b], 510))
              for b in (30, 32)}

    jobs_dir = os.path.join(repo, RUN, "attempt-1", "jobs")
    rec = {}            # (bits, curve, arm, class) -> recount dict
    census_job = {}     # (bits, curve, arm) -> selected census fields (per-job file)
    status = Counter()
    planted_vec = {}
    harvest_instances_seen = set()
    for job in sorted(os.listdir(jobs_dir)):
        hrows = defaultdict(list)
        with gzip.open(os.path.join(jobs_dir, job, "harvest-rows.jsonl.gz"), "rt") as fh:
            for line in fh:
                if not line.strip():
                    continue
                r = json.loads(line)
                if r["m"] != 4 or r["mode"] != "table":
                    raise SystemExit(f"unexpected row m/mode in {job}")
                hrows[(r["bits"], r["curve"], r["arm"], r["class"])].append(r)
        for k, rows in hrows.items():
            harvest_instances_seen.add(k)
            rec[k] = recount_instance(rows, Nof[(k[0], k[1])])
        with gzip.open(os.path.join(jobs_dir, job, "rows.jsonl.gz"), "rt") as fh:
            for line in fh:
                if not line.strip():
                    continue
                r = json.loads(line)
                key = (r["bits"], r["curve"], r["arm"])
                status[r.get("status")] += 1
                f = {"status": r.get("status"), "N": r.get("N"), "fb_size": r.get("fb_size")}
                for cl in CLASSES:
                    a = r["harvest"][cl]["at_stop"]
                    f[cl] = {k2: a.get(k2) for k2 in ("relations_distinct", "relations_distinct_sign",
                                                      "relations_nonformal", "R_star", "multiplicity_histogram",
                                                      "informative_rank", "rows_emitted", "relation_pairs",
                                                      "relation_pairs_zero")}
                census_job[key] = f
                if r["arm"] == "planted_sub":
                    planted_vec[(r["bits"], r["curve"])] = planted_tt_monic(r["fb_params"], int(r["N"]))

    # run-root merged census rows: same fields, for the merge-fidelity comparison
    census_root = {}
    with gzip.open(os.path.join(repo, RUN, "rows.jsonl.gz"), "rt") as fh:
        for line in fh:
            if not line.strip():
                continue
            r = json.loads(line)
            key = (r["bits"], r["curve"], r["arm"])
            f = {"status": r.get("status"), "N": r.get("N"), "fb_size": r.get("fb_size")}
            for cl in CLASSES:
                a = r["harvest"][cl]["at_stop"]
                f[cl] = {k2: a.get(k2) for k2 in ("relations_distinct", "relations_distinct_sign",
                                                  "relations_nonformal", "R_star", "multiplicity_histogram",
                                                  "informative_rank", "rows_emitted", "relation_pairs",
                                                  "relation_pairs_zero")}
            if key in census_root:
                census_root.setdefault("__dup__", []).append(key)
            census_root[key] = f

    def rc(b, c, arm, cl):
        x = rec.get((b, c, arm, cl))
        if x is None:
            return {"relations_distinct": 0, "relations_distinct_sign": 0, "R_star": 0,
                    "multiplicity_histogram": {}, "relation_pairs": 0, "relation_pairs_zero": 0,
                    "rows": 0, "rows_flag_formal": 0, "set": set()}
        return x

    # per-curve counts (TT, TB) for every arm, plus planted_target
    n = {}
    planted_present = {}
    for (b, c) in Nof:
        for arm in ARMS:
            for cl in CLASSES:
                n[(b, c, arm, cl)] = rc(b, c, arm, cl)["relations_distinct"]
        pv = planted_vec.get((b, c))
        present = pv is not None and pv in rc(b, c, "planted_sub", "TT")["set"]
        planted_present[(b, c)] = present
        n[(b, c, "planted_target", "TT")] = n[(b, c, "planted_sub", "TT")] - (0 if c in S[b] else (1 if present else 0))

    # comparison of recount with census harvester fields
    FIELDS = ("relations_distinct", "relations_distinct_sign", "R_star", "multiplicity_histogram")

    def compare(keys):
        mism = []
        for (b, c, arm) in keys:
            cj = census_job.get((b, c, arm))
            if cj is None:
                mism.append({"key": [b, c, arm], "what": "census row missing"})
                continue
            for cl in CLASSES:
                x = rc(b, c, arm, cl)
                for fld in FIELDS:
                    want = cj[cl][fld]
                    got = x[fld]
                    if fld == "multiplicity_histogram":
                        want = {str(k): v for k, v in (want or {}).items()}
                        got = {str(k): v for k, v in got.items()}
                    if want != got:
                        mism.append({"key": [b, c, arm, cl], "field": fld, "census": want, "recount": got})
                if cj[cl]["relations_nonformal"] != x["relations_distinct"] - 0:
                    mism.append({"key": [b, c, arm, cl], "field": "relations_nonformal",
                                 "census": cj[cl]["relations_nonformal"], "recount": x["relations_distinct"]})
                if x["rows_flag_formal"]:
                    mism.append({"key": [b, c, arm, cl], "field": "row formal flag true", "recount": x["rows_flag_formal"]})
        return mism

    primary_keys = [(b, c, arm) for b in (30, 32) for c in sorted(sample[b]) for arm in ARMS] + \
                   [(b, c, arm) for (b, c) in sorted(Nof) for arm in NULLS if c not in sample[b]]
    all_keys = [(b, c, arm) for (b, c) in sorted(Nof) for arm in ARMS]
    mism_primary = compare(primary_keys)
    mism_all = compare(all_keys)

    # merge fidelity: per-job census fields == run-root census fields
    merge_mism = [list(k) for k in census_job if census_root.get(k) != census_job[k]]
    merge_extra = [list(k) for k in census_root if k != "__dup__" and k not in census_job]

    # harvest instances without a census row (should be none)
    orphan = [list(k) for k in harvest_instances_seen if (k[0], k[1], k[2]) not in census_job]

    # write bulky per-curve table to scratch
    with gzip.open(out_percurve, "wt") as fh:
        for (b, c) in sorted(Nof):
            rowd = {"bits": b, "curve": c, "in_sample": c in sample[b], "in_S": c in S[b],
                    "planted_tt_present": planted_present[(b, c)]}
            for arm in ARMS + ["planted_target"]:
                rowd[arm] = n[(b, c, arm, "TT")]
            for arm in ARMS:
                rowd[arm + "|TB"] = n[(b, c, arm, "TB")]
                rowd[arm + "|sign"] = rc(b, c, arm, "TT")["relations_distinct_sign"]
            fh.write(json.dumps(rowd, sort_keys=True) + "\n")

    summary = {
        "sample_sizes": {b: len(sample[b]) for b in sample},
        "sample_sha256_of_sorted_list": {b: __import__("hashlib").sha256(json.dumps(sorted(sample[b])).encode()).hexdigest() for b in sample},
        "census_rows_job_files": len(census_job), "census_rows_root": len([k for k in census_root if k != "__dup__"]),
        "census_root_duplicate_keys": len(census_root.get("__dup__", [])),
        "census_status_counts": dict(status),
        "harvest_instances_with_rows": len(harvest_instances_seen),
        "orphan_harvest_instances": orphan,
        "primary_keys_compared": len(primary_keys), "primary_mismatches": mism_primary[:50],
        "primary_mismatch_count": len(mism_primary),
        "supplementary_all_keys_compared": len(all_keys), "supplementary_mismatch_count": len(mism_all),
        "supplementary_mismatches": mism_all[:50],
        "merge_fidelity_mismatches": merge_mism[:50], "merge_fidelity_mismatch_count": len(merge_mism),
        "merge_root_extra_keys": merge_extra[:50],
        "planted_tt_vector_present_on_curves": sum(planted_present.values()),
        "planted_tt_vector_absent": [list(k) for k, v in planted_present.items() if not v],
    }
    json.dump(summary, open(out_summary, "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in summary.items() if not isinstance(v, list) or len(v) < 20}, default=str, indent=0))


if __name__ == "__main__":
    main()
