#!/usr/bin/env python3
"""J5 (b): G-FIX attribution of the nine unattributed keys from full-retention rows.

TASK-20261002-0114ff. Inputs: the two RV-6 (a) re-executions in the validator's
scratch (census mode, --retain all), the archived R10 run root (rows.jsonl.gz,
staircase.jsonl.gz, solve-certs.jsonl.gz, fix-report.json, fix-digests.json).
Standard library only.

Equality with the archive (where it retained):
  census rows: every key equal except timing/memory keys and 'retain';
  staircases and solve certificates equal;
  harvest rows: the default-retention subset of the full rows (rows whose
  census_rank_after is not null: harvest.py keeps a class's rows while that
  class is unsaturated above 24 bits) hashes to fix-digests.json per instance.
Attribution, per key and scope (at_stop; at_A_fix = attempts <= A_fix):
  new = sum over SS x-groups of C(k', 2) from the full rows (k' = 1 + star rows);
  D = new - old (fix-report old); the pre-OBJ-5 end_attempt pairs a new member
  with the earlier members of the FIRST sorted run holding its x plus the earlier
  members of its own attempt; runs are contiguous attempt ranges, so member j can
  miss only earlier members whose attempt is neither the first member's attempt
  nor its own. bound = sum over members of that count (an upper bound on the
  undercount, reached when the first member's run holds only its own attempt).
  D is ATTRIBUTED iff 0 <= D <= bound and (D > 0 implies a group of >= 3 members
  spanning >= 2 attempts exists); otherwise the residual D - bound is listed.
"""
import gzip
import hashlib
import json
import math
import os
import sys

S = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/rv-0114ff/j5"
WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-pfdr011cd0-5753edf2e"
R10 = WT + "/experiments/EXP-PFDR-011cd0/runs/RUN-PFDR-011cd0-fix-check/"
KEYF = ("bits", "curve", "m", "arm", "mode")
TIMING = {"seconds", "harvest_seconds", "worker_maxrss_bytes", "retain", "peak_bytes"}


def deepdiff(a, b, path=""):
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k in TIMING:
                continue
            if k not in a or k not in b:
                out.append(path + "/" + k + (" (only new)" if k in a else " (only archived)"))
            else:
                out += deepdiff(a[k], b[k], path + "/" + k)
    elif a != b:
        out.append(path)
    return out


def key_of(r):
    return (r["bits"], r["curve"], int(r["method"].replace("ic_m", "")), r["arm"], r["mode"])


def main():
    fixrep = json.load(open(R10 + "fix-report.json"))
    finst = {tuple(x["key"]): x for x in fixrep["instances"]}
    unattr = {tuple(x["key"]) for x in fixrep["unattributed"]}
    fdig = json.load(open(R10 + "fix-digests.json"))["per_instance"]
    arch_rows = {}
    with gzip.open(R10 + "rows.jsonl.gz", "rt") as fh:
        for line in fh:
            r = json.loads(line)
            arch_rows[key_of(r)] = r
    arch_stair = {}
    with gzip.open(R10 + "staircase.jsonl.gz", "rt") as fh:
        for line in fh:
            r = json.loads(line)
            arch_stair.setdefault(json.dumps({k: r.get(k) for k in ("bits", "curve", "m", "arm", "mode")}, sort_keys=True), []).append(line)
    arch_certs = {json.dumps(json.loads(l)["key"], sort_keys=True): l.strip() for l in gzip.open(R10 + "solve-certs.jsonl.gz", "rt")}
    report = {"jobs": {}, "nine_keys": {}}
    for job in ("4-b26-c0", "5-b32-c0"):
        d = os.path.join(S, job)
        new_rows = {key_of(json.loads(l)): json.loads(l) for l in open(os.path.join(d, "rows.jsonl"))}
        jr = {"census_instances": 0, "census_row_diffs": {}, "staircase_equal": {}, "certs_equal": {},
              "default_subset_digest_equal": {}, "full_rows_sha256_gz": None}
        # staircase and certs
        new_stair = {}
        for l in open(os.path.join(d, "staircase.jsonl")):
            r = json.loads(l)
            new_stair.setdefault(json.dumps({k: r.get(k) for k in ("bits", "curve", "m", "arm", "mode")}, sort_keys=True), []).append(l)
        job_stair = {}
        with gzip.open(R10 + "attempt-1/jobs/" + job + "/staircase.jsonl.gz", "rt") as fh:
            for l in fh:
                r = json.loads(l)
                job_stair.setdefault(json.dumps({k: r.get(k) for k in ("bits", "curve", "m", "arm", "mode")}, sort_keys=True), []).append(l)
        new_certs = {json.dumps(json.loads(l)["key"], sort_keys=True): l.strip() for l in open(os.path.join(d, "solve-certs.jsonl"))}
        # group rows per instance
        per = {}
        with open(os.path.join(d, "harvest-rows.jsonl")) as fh:
            for line in fh:
                r = json.loads(line)
                per.setdefault(tuple(r[f] for f in KEYF), []).append(r)
        for k, nr in sorted(new_rows.items()):
            if k[4] != "census":
                continue
            jr["census_instances"] += 1
            ar = arch_rows.get(k)
            jr["census_row_diffs"][json.dumps(k)] = deepdiff(nr, ar) if ar else ["ARCHIVED ROW ABSENT"]
            sk = json.dumps({"bits": k[0], "curve": k[1], "m": k[2], "arm": k[3], "mode": k[4]}, sort_keys=True)
            nl = [json.loads(x) for x in new_stair.get(sk, [])]
            jl = [json.loads(x) for x in job_stair.get(sk, [])]
            rl = [json.loads(x) for x in arch_stair.get(sk, [])]
            jr["staircase_equal"][json.dumps(k)] = {"job_file_in_order": nl == jl,
                                                    "root_as_multiset": sorted(map(lambda r: json.dumps(r, sort_keys=True), nl)) == sorted(map(lambda r: json.dumps(r, sort_keys=True), rl))}
            ck = json.dumps({"bits": k[0], "curve": k[1], "m": k[2], "arm": k[3], "mode": k[4]}, sort_keys=True)
            jr["certs_equal"][json.dumps(k)] = (json.loads(new_certs[ck]) == json.loads(arch_certs[ck])) if ck in new_certs and ck in arch_certs else (ck not in new_certs and ck not in arch_certs)
            rows = per.get(k, [])
            sub = [r for r in rows if r["census_rank_after"] is not None]
            h_nokey = hashlib.sha256()
            h_withkey = hashlib.sha256()
            for r in sub:
                h_nokey.update((json.dumps({x: v for x, v in r.items() if x not in KEYF}, sort_keys=True, separators=(",", ":")) + "\n").encode())
                h_withkey.update((json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n").encode())
            fd = fdig.get(json.dumps(list(k)))
            jr["default_subset_digest_equal"][json.dumps(k)] = {
                "subset_rows": len(sub), "full_rows": len(rows),
                "archived_rows": fd["new_harvest_rows"] if fd else None,
                "equal_nokey": bool(fd) and h_nokey.hexdigest() == fd["new_harvest_rows_sha256"],
                "equal_withkey": bool(fd) and h_withkey.hexdigest() == fd["new_harvest_rows_sha256"]}
            # SS groups and attribution
            A_fix = nr["harvest"].get("attempt_budget_A_fix")
            for scope in ("at_stop", "at_A_fix"):
                groups = {}
                for r in rows:
                    if r["class"] != "SS":
                        continue
                    if scope == "at_A_fix" and r["attempt"] > A_fix:
                        continue
                    e1, e2 = r["elements"]
                    g = groups.setdefault(json.dumps(e1, sort_keys=True), [e1["enc"][0]])
                    g.append(e2["enc"][0])
                new = sum(math.comb(len(g), 2) for g in groups.values())
                bound, straddle, rich = 0, 0, []
                for gid, att in groups.items():
                    if len(att) >= 3 and len(set(att)) >= 2:
                        straddle += 1
                    b = 0
                    for j in range(2, len(att)):
                        b += sum(1 for i in range(1, j) if att[i] not in (att[0], att[j]))
                    bound += b
                    if b:
                        rich.append({"first": json.loads(gid)["enc"], "member_attempts": att, "k": len(att),
                                     "C_k_2": math.comb(len(att), 2), "max_missed": b})
                fi = finst.get(k, {}).get("ss_pairs", {})
                old = fi.get(f"{scope}.pairs_raw", {}).get("old")
                arch_new = fi.get(f"{scope}.pairs_raw", {}).get("new")
                reexec = nr["harvest"]["SS"].get(scope, {}).get("pairs_raw")
                D = None if old is None else new - old
                attributed = D is not None and 0 <= D <= bound and (D == 0 or straddle > 0)
                ent = {"new_from_full_rows": new, "reexec_counter": reexec, "archived_R10_new": arch_new, "old_1b78f7": old,
                       "D": D, "max_undercount_bound": bound, "groups_ge3_span_ge2": straddle,
                       "attributed": attributed, "residual": None if attributed or D is None else D - bound,
                       "groups_with_possible_miss": rich if k in unattr else len(rich),
                       "new_eq_reexec_eq_archived": new == reexec == arch_new}
                if k in unattr:
                    report["nine_keys"].setdefault(json.dumps(list(k)), {})[scope] = ent
                else:
                    report["jobs"].setdefault(job + "|other_instances", {})[json.dumps(list(k)) + "|" + scope] = {x: ent[x] for x in ("D", "max_undercount_bound", "attributed", "new_eq_reexec_eq_archived")}
        h = hashlib.sha256()
        with open(os.path.join(d, "harvest-rows.jsonl"), "rb") as fh:
            for b in iter(lambda: fh.read(1 << 20), b""):
                h.update(b)
        jr["full_rows_sha256"] = h.hexdigest()
        jr["full_rows_bytes"] = os.path.getsize(os.path.join(d, "harvest-rows.jsonl"))
        report["jobs"][job] = jr
    json.dump(report, open(sys.argv[1], "w"), indent=1, sort_keys=True)
    for job in ("4-b26-c0", "5-b32-c0"):
        jr = report["jobs"][job]
        print(job, "census instances", jr["census_instances"],
              "row diffs", {k: v for k, v in jr["census_row_diffs"].items() if v},
              "stair all equal (job in order, root multiset)", all(v["job_file_in_order"] and v["root_as_multiset"] for v in jr["staircase_equal"].values()), "certs all equal", all(jr["certs_equal"].values()),
              "digest nokey all", all(v["equal_nokey"] for v in jr["default_subset_digest_equal"].values()),
              "digest withkey all", all(v["equal_withkey"] for v in jr["default_subset_digest_equal"].values()))
    for k, v in report["nine_keys"].items():
        print(k, {s: {x: e[x] for x in ("new_from_full_rows", "reexec_counter", "archived_R10_new", "old_1b78f7", "D", "max_undercount_bound", "groups_ge3_span_ge2", "attributed", "residual")} for s, e in v.items()})
    oth = report["jobs"].get("4-b26-c0|other_instances", {}) | report["jobs"].get("5-b32-c0|other_instances", {})
    print("other instances: all attributed", all(v["attributed"] for v in oth.values()), "all new==reexec==archived", all(v["new_eq_reexec_eq_archived"] for v in oth.values()), len(oth))


if __name__ == "__main__":
    main()
