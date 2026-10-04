#!/usr/bin/env python3
"""J1 (c), (d), (e) with the validator's own comparators, after the seal.

TASK-20261002-0114ff. Standard library only. Reads the census rows (root
rows.jsonl.gz of R12, R13, R14), the harvest rows of R12, R13 and R14 attempt-1
jobs, design.json, the jobs-spec files, row-verify.json and solve-verify.json.
(c) universes (77020, 6226, 264) from jobs-spec vs census rows; no duplicate key;
    curve seeds c = 10 .. 10 + n - 1 per design.json final n; |F| equal across each
    family on each curve and equal to design s_sub / s_dick; status counts.
(d) own G4-R per-instance row counts vs row-verify.json per_instance; own G4-D vs
    solve-verify.json (root and attempt).
(e) G-CURVE: (p, a, b, N, P) of every census row equals design.json's (bits, c).
    G-TAB: for every R13 instance, R13's TT and TB harvest blocks equal R12's for
    the same (bits, curve, m, arm), and R13's rows_digest[TT/TB] equals sha256 over
    R12's harvest rows of that instance and class, each line
    json.dumps(row minus {bits, curve, m, arm, mode}, sort_keys, (',', ':')) + '\n'
    (the canonical line the frozen text names; key-field set chosen here and
    reported).
    G-SRCH: for every R14 instance, its SS rows (retain xfix) equal R13's SS rows
    with seq < X_fix (all fields but the key fields, in order); where R14's
    at_X_fix block is censored (census found k first), R14's rows must be an
    order-preserving prefix of R13's; the at_X_fix block equals R13's when not
    censored; R14 TT/TB rows_digest equals R13's.
"""
import collections
import gzip
import hashlib
import json
import os
import sys

WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-pfdr011cd0-5753edf2e"
RUNS = WT + "/experiments/EXP-PFDR-011cd0/runs/"
HERE = os.path.dirname(os.path.abspath(__file__))
KEYF = ("bits", "curve", "m", "arm", "mode")
SUB = ["subgroup", "small_x", "random_sub_r0", "random_sub_r1", "random_sub_r2", "known_null_sub", "planted_sub"]
DICK = ["dickson", "random_dick_r0", "random_dick_r1", "random_dick_r2", "known_null_dick"]


def canon(r):
    return json.dumps({k: v for k, v in r.items() if k not in KEYF}, sort_keys=True, separators=(",", ":")) + "\n"


def census(run):
    out, dup = {}, 0
    with gzip.open(RUNS + run + "/rows.jsonl.gz", "rt") as fh:
        for line in fh:
            r = json.loads(line)
            k = (r["bits"], r["curve"], int(r["method"].replace("ic_m", "")), r["arm"], r["mode"])
            dup += k in out
            out[k] = r
    return out, dup


def expected(run):
    js = json.load(open(RUNS + run + "/attempt-1/jobs-spec.json"))
    return [tuple(k) for j in js["jobs"] for k in j["expected_keys"]]


def harvest_by_instance(run, keyfilter=None):
    """yield (key, [rows]) per instance, streaming each job file."""
    jd = RUNS + run + "/attempt-1/jobs"
    for job in sorted(os.listdir(jd)):
        fp = os.path.join(jd, job, "harvest-rows.jsonl.gz")
        cur, rows = None, []
        with gzip.open(fp, "rt") as fh:
            for line in fh:
                r = json.loads(line)
                k = tuple(r[f] for f in KEYF)
                if k != cur:
                    if cur is not None and (keyfilter is None or cur in keyfilter):
                        yield cur, rows
                    cur, rows = k, []
                rows.append(r)
        if cur is not None and (keyfilter is None or cur in keyfilter):
            yield cur, rows


def main():
    design = json.load(open(RUNS + "RUN-PFDR-011cd0-p0-design/attempt-3/design.json"))
    dc = {(c["bits"], c["curve"]): c for c in design["curves"]}
    rep = {}
    c12, d12 = census("RUN-PFDR-011cd0-table")
    c13, d13 = census("RUN-PFDR-011cd0-search")
    c14, d14 = census("RUN-PFDR-011cd0-srch-check")
    e12, e13, e14 = expected("RUN-PFDR-011cd0-table"), expected("RUN-PFDR-011cd0-search"), expected("RUN-PFDR-011cd0-srch-check")
    uni = {}
    for name, c, d, e in (("R12", c12, d12, e12), ("R13", c13, d13, e13), ("R14", c14, d14, e14)):
        uni[name] = {"expected_keys": len(e), "expected_unique": len(set(e)), "census_rows": len(c), "duplicate_census_keys": d,
                     "missing": len(set(e) - set(c)), "extra": len(set(c) - set(e)),
                     "status_counts": dict(collections.Counter(r["status"] for r in c.values()))}
    # curve seeds per final n
    seeds_bad = []
    for panel, c, mode in (("table", c12, "table"), ("search", c13, "search")):
        got = collections.defaultdict(set)
        for (b, cv, m, arm, md) in c:
            if arm != "known_log":
                got[(m, b)].add(cv)
        for m, d in design["final_n"][panel].items():
            for b, n in d.items():
                if got[(int(m), int(b))] != set(range(10, 10 + n)):
                    seeds_bad.append([panel, m, b])
    pc1 = sorted({(b, cv) for (b, cv, m, arm, md) in c12 if arm == "known_log"})
    r14c = sorted({(b, cv, m) for (b, cv, m, arm, md) in c14})
    # |F| matching
    fbad = []
    for c, mode in ((c12, "table"), (c13, "search"), (c14, "census")):
        groups = collections.defaultdict(dict)
        for (b, cv, m, arm, md), r in c.items():
            groups[(b, cv, m)][arm] = r["fb_size"]
        for (b, cv, m), arms in groups.items():
            sz = dc[(b, cv)]["sizes"][str(m)]
            for fam, want in ((SUB, sz["s_sub"]), (DICK, sz["s_dick"])):
                vals = {a: arms[a] for a in fam if a in arms}
                if any(v != want for v in vals.values()):
                    fbad.append({"mode": mode, "key": [b, cv, m], "want": want, "got": vals})
    rep["c_universe_seeds_sizes"] = {"universes": uni, "curve_seed_sets_not_equal_final_n": seeds_bad,
                                     "pc1_curves": pc1, "r14_bits_curve_m": r14c,
                                     "family_size_mismatches": fbad[:50], "family_size_mismatch_count": len(fbad)}
    # (e) G-CURVE
    gc = []
    for name, c in (("R12", c12), ("R13", c13), ("R14", c14)):
        for k, r in c.items():
            d = dc.get((k[0], k[1]))
            if d is None or (r["p"], r["a"], r["b"], r["N"], tuple(r["P"])) != (d["p"], d["a"], d["b"], d["N"], tuple(d["P"])):
                gc.append([name] + list(k))
    rep["e_G_CURVE"] = {"instances_checked": len(c12) + len(c13) + len(c14), "failures": gc[:50], "failure_count": len(gc)}
    # (e) G-TAB
    want13 = {(b, cv, m, arm, "table"): k for k in c13 for (b, cv, m, arm, md) in [k]}
    tab = {"compared": 0, "blocks_equal": 0, "digest_equal": 0, "failures": []}
    # instances with zero rows never appear in harvest_by_instance: build the digest map first
    dig = {}
    for k12, rows in harvest_by_instance("RUN-PFDR-011cd0-table", set(want13)):
        for cls in ("TT", "TB"):
            h = hashlib.sha256()
            n = 0
            for r in rows:
                if r["class"] == cls:
                    h.update(canon(r).encode())
                    n += 1
            dig[(k12, cls)] = (h.hexdigest(), n)
    empty = hashlib.sha256(b"").hexdigest()
    for k12, k13 in want13.items():
        tab["compared"] += 1
        h12, h13 = c12[k12]["harvest"], c13[k13]["harvest"]
        be = h12["TT"] == h13["TT"] and h12["TB"] == h13["TB"]
        de = all(h13["rows_digest"][cls] == dig.get((k12, cls), (empty, 0))[0] and
                 h13["rows_digest_rows"][cls] == dig.get((k12, cls), (empty, 0))[1] for cls in ("TT", "TB"))
        tab["blocks_equal"] += be
        tab["digest_equal"] += de
        if not (be and de) and len(tab["failures"]) < 30:
            tab["failures"].append({"key": list(k13), "blocks_equal": be, "digest_equal": de})
    tab["pass"] = tab["compared"] == tab["blocks_equal"] == tab["digest_equal"] == 6226
    rep["e_G_TAB"] = tab
    # (e) G-SRCH
    want14 = set(c14)
    r14rows = dict(harvest_by_instance("RUN-PFDR-011cd0-srch-check", want14))
    want13s = {(b, cv, m, arm, "search") for (b, cv, m, arm, md) in c14}
    r13rows = dict(harvest_by_instance("RUN-PFDR-011cd0-search", want13s))
    srch = {"compared": 0, "uncensored_equal": 0, "censored_prefix_ok": 0, "censored": [], "failures": [],
            "block_equal_uncensored": 0, "rows_digest_equal": 0}
    for k14 in sorted(c14):
        b, cv, m, arm, _ = k14
        k13 = (b, cv, m, arm, "search")
        srch["compared"] += 1
        xf = dc[(b, cv)]["X_fix"]
        a = [canon(r) for r in r14rows.get(k14, []) if r["class"] == "SS"]
        bb = [canon(r) for r in r13rows.get(k13, []) if r["class"] == "SS" and r["seq"] < xf]
        h14, h13 = c14[k14]["harvest"], c13[k13]["harvest"]
        cens = h14["SS"]["at_X_fix"]["censored"]
        srch["rows_digest_equal"] += h14["rows_digest"] == h13["rows_digest"]
        if not cens:
            ok = a == bb
            srch["uncensored_equal"] += ok
            be = h14["SS"]["at_X_fix"] == h13["SS"]["at_X_fix"]
            srch["block_equal_uncensored"] += be
            if not (ok and be):
                srch["failures"].append({"key": list(k14), "rows_equal": ok, "block_equal": be, "n14": len(a), "n13": len(bb)})
        else:
            ok = a == bb[:len(a)]
            srch["censored_prefix_ok"] += ok
            srch["censored"].append({"key": list(k14), "n14": len(a), "n13_lt_xfix": len(bb), "prefix_equal": ok,
                                     "census_formally_distinct_encodings": h14["SS"]["at_X_fix"]["formally_distinct_encodings"]})
            if not ok:
                srch["failures"].append({"key": list(k14), "censored_prefix_equal": False})
    srch["censored_count"] = len(srch["censored"])
    srch["pass"] = not srch["failures"] and srch["rows_digest_equal"] == srch["compared"]
    rep["e_G_SRCH"] = srch
    # (d) own G4-R vs row-verify.json; own G4-D vs solve-verify.json
    rv12 = json.load(open(RUNS + "RUN-PFDR-011cd0-table/row-verify.json"))
    rv13 = json.load(open(RUNS + "RUN-PFDR-011cd0-search/row-verify.json"))
    pi = {}
    pi.update(rv12["per_instance"])
    pi.update(rv13["per_instance"])
    own = {}
    with gzip.open(os.path.join(HERE, "outputs", "g4r-result-per-instance.jsonl.gz"), "rt") as fh:
        for line in fh:
            r = json.loads(line)
            own[json.dumps(r["key"])] = r
    cmpd, eq, diff = 0, 0, []
    for k, r in own.items():
        p = pi.get(k)
        cmpd += 1
        if p is not None and p["rows_checked"] == r["rows"] and p["failed"] == r["rows_failed"] == 0:
            eq += 1
        elif len(diff) < 20:
            diff.append({"key": k, "own": [r["rows"], r["rows_failed"]], "producer": p})
    sv = json.load(open(RUNS + "RUN-PFDR-011cd0-srch-check/solve-verify.json"))
    sva = json.load(open(RUNS + "RUN-PFDR-011cd0-srch-check/attempt-1/solve-verify.json"))
    g4d = json.load(open(os.path.join(HERE, "outputs", "g4d-result.json")))
    rep["d_G4"] = {"G4R_own_sample_instances_compared": cmpd, "G4R_rows_checked_and_zero_failures_equal": eq, "G4R_differences": diff,
                   "G4R_producer": {"R12": [rv12["sampled_instances"], rv12["rows_checked"], rv12["failure_count"], rv12["pass"]],
                                    "R13": [rv13["sampled_instances"], rv13["rows_checked"], rv13["failure_count"], rv13["pass"]]},
                   "G4D_producer_root": [sv["records"], sv["verified"], sv["failed"], sv["pass"], sv["certificates_sha256"]],
                   "G4D_producer_attempt": [sva["records"], sva["verified"], sva["failed"], sva["pass"], sva["certificates_sha256"]],
                   "G4D_own": {k.split("wt-pfdr011cd0-5753edf2e/")[-1]: [v["records"], v["records_passing_all_checks"], v["pass"], v["sha256"]] for k, v in g4d["files"].items()}}
    json.dump(rep, open(sys.argv[1], "w"), indent=1, sort_keys=True, default=str)
    print(json.dumps({"universes": uni, "seeds_bad": seeds_bad, "fsize_bad": len(fbad), "G-CURVE": rep["e_G_CURVE"]["failure_count"],
                      "G-TAB": {k: v for k, v in tab.items() if k != "failures"}, "G-TAB-fail": tab["failures"][:3],
                      "G-SRCH": {k: v for k, v in srch.items() if k not in ("censored", "failures")}, "G-SRCH-fail": srch["failures"][:3],
                      "d": {k: v for k, v in rep["d_G4"].items() if k != "G4R_differences"}, "d_diff": diff[:3]}, indent=1, default=str))


if __name__ == "__main__":
    main()
