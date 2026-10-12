"""EXP-PFDR-011cd0 merge and comparison tool (EC-9).  TASK-20261001-7f7a33.

Imports no crypto_autoresearcher module.  Reads keys, statuses, digests and rows; computes
no kappa, z, ratio or dispersion and interprets nothing.

Subcommands
  merge        canonical row set of a job-launched run (R10, R12, R13, R14, R17) at the run
               root: rows.jsonl.gz, staircase.jsonl.gz, solve-certs.jsonl.gz (when present),
               merge-report.json (per-key source, harvest-rows map, bases map).
  view         a scratch view: one symlink per run directory to its canonical location, and
               view-map.json (link, target, sha256 of every target file).  NA-16 F-J2-1.
  fixcompare   R10 (G-FIX) against the archived EXP-PFDR-1b78f7 canonical rows, staircases
               and harvest rows of the same jobs.
  srchcompare  R14 vs R13 (G-SRCH): at_X_fix SS block and X_fix row set per key.
  tabcompare   R12 vs R13 (G-TAB): TT/TB blocks and R13 rows_digest vs R12's row streams.
  curvecheck   G-CURVE: every panel instance's (p, a, b, N, P) equals design.json's entry.
"""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import os
import subprocess
import sys
from collections import Counter, defaultdict

REPO = "/home/user/crypto-autoresearcher"
EXPDIR = "experiments/EXP-PFDR-011cd0"
KEY_FIELDS = ("bits", "curve", "m", "arm", "mode")
TIMING_KEYS = ("seconds",)
HARVEST_TIMING_KEYS = ("harvest_seconds", "worker_maxrss_bytes")
PAIR_KEYS = ("pairs_raw", "pairs_formal", "pairs_nonformal")


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def absp(p: str) -> str:
    return p if os.path.isabs(p) else os.path.join(REPO, p)


def rel(p: str) -> str:
    return os.path.relpath(absp(p), REPO)


def read_jsonl(path: str):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as fh:
        for line in fh:
            if line.strip():
                yield json.loads(line)


def row_m(r: dict):
    if r.get("m") is not None:
        return r["m"]
    meth = str(r.get("method", ""))
    return int(meth[4:]) if meth.startswith("ic_m") else None


def key_of(r: dict) -> tuple:
    return (r.get("bits"), r.get("curve"), row_m(r), r.get("arm"), r.get("mode"))


def ks(k) -> str:
    return json.dumps(list(k))


def write_gz_jsonl(path: str, recs) -> str:
    tmp = path[:-3]
    with open(tmp, "w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    subprocess.run(["gzip", "-n", tmp], check=True)
    return sha256(path)


def canonical_row_line(rec: dict) -> bytes:
    """Must equal harvest.canonical_row_line (sorted keys, ',' ':' separators, newline)."""
    return (json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n").encode()


# ------------------------------------------------------------------------------------------
# merge

def cmd_merge(a) -> int:
    rd = absp(a.run_dir)
    for f in ("rows.jsonl.gz", "merge-report.json"):
        if os.path.exists(os.path.join(rd, f)):
            print(f"refusing: {rd}/{f} exists (records are immutable)", file=sys.stderr)
            return 3
    expected: dict[str, None] = {}
    job_of_attempt: dict = {}
    sources: dict[str, dict] = {}
    superseded, dup_same_attempt, non_cell = [], [], []
    attempts_info = []
    for att in a.attempts:
        ad = os.path.join(rd, att)
        idx = json.load(open(os.path.join(ad, "jobs-index.json")))
        spec = json.load(open(os.path.join(ad, "jobs-spec.json")))
        names_ran = {j["job"] for j in idx["jobs"]}
        for j in spec["jobs"]:
            for k in j["expected_keys"]:
                expected.setdefault(ks(k), None)
        attempts_info.append({"attempt": att, "jobs_ran": sorted(names_ran),
                              "not_started": idx["not_started"],
                              "jobs_index_sha256": sha256(os.path.join(ad, "jobs-index.json"))})
        for j in idx["jobs"]:
            jd = absp(j["job_dir"])
            rp = os.path.join(jd, "rows.jsonl.gz")
            if not os.path.exists(rp):
                continue
            seen_here = Counter()
            for r in read_jsonl(rp):
                k = ks(key_of(r))
                seen_here[k] += 1
                if seen_here[k] > 1:
                    dup_same_attempt.append({"key": json.loads(k), "attempt": att, "job": j["job"]})
                    continue
                if k not in expected:
                    non_cell.append({"key": json.loads(k), "attempt": att, "job": j["job"],
                                     "status": r.get("status")})
                    continue
                prev = sources.get(k)
                cand = {"attempt": att, "job": j["job"], "job_dir": j["job_dir"], "row": r}
                if prev is None:
                    sources[k] = cand
                elif prev["row"].get("status") == "failed_infrastructure":
                    superseded.append({"key": json.loads(k), "attempt": prev["attempt"],
                                       "status": "failed_infrastructure",
                                       "status_reason": prev["row"].get("status_reason"),
                                       "superseded_by": att})
                    sources[k] = cand
                else:
                    superseded.append({"key": json.loads(k), "attempt": att, "status": r.get("status"),
                                       "note": "later row not used: an earlier attempt holds a "
                                               "non-infrastructure row for this key"})
    missing = sorted(k for k in expected if k not in sources)
    keys_sorted = sorted(sources, key=lambda k: tuple(json.loads(k)))
    rows = [sources[k]["row"] for k in keys_sorted]
    rows_sha = write_gz_jsonl(os.path.join(rd, "rows.jsonl.gz"), rows)
    # staircases and certificates from the source jobs of the canonical rows
    by_job: dict = defaultdict(set)
    for k in keys_sorted:
        by_job[sources[k]["job_dir"]].add(k)
    stairs, certs = [], []
    harvest_map, bases_map = {}, {}
    for jd_rel, keyset in sorted(by_job.items()):
        jd = absp(jd_rel)
        sp = os.path.join(jd, "staircase.jsonl.gz")
        if os.path.exists(sp):
            stairs.extend(s for s in read_jsonl(sp) if ks(key_of(s)) in keyset)
        cp = os.path.join(jd, "solve-certs.jsonl.gz")
        if os.path.exists(cp):
            for c in read_jsonl(cp):
                kk = c["key"]
                if ks((kk["bits"], kk["curve"], kk["m"], kk["arm"], kk["mode"])) in keyset:
                    certs.append(c)
        hp = os.path.join(jd, "harvest-rows.jsonl.gz")
        hsha = sha256(hp) if os.path.exists(hp) else None
        for k in keyset:
            harvest_map[k] = {"harvest_rows_file": rel(hp) if hsha else None, "sha256": hsha}
        bp = os.path.join(jd, "bases.jsonl.gz")
        if os.path.exists(bp):
            bsha = sha256(bp)
            for b in read_jsonl(bp):
                bases_map[ks((b["bits"], b["curve"], b["m"], b["arm"]))] = {"bases_file": rel(bp), "sha256": bsha}
    stairs.sort(key=lambda s: (key_of(s), s.get("class", "")))
    st_sha = write_gz_jsonl(os.path.join(rd, "staircase.jsonl.gz"), stairs)
    canonical = {"rows.jsonl.gz": rows_sha, "staircase.jsonl.gz": st_sha}
    if certs:
        certs.sort(key=lambda c: json.dumps(c["key"], sort_keys=True))
        canonical["solve-certs.jsonl.gz"] = write_gz_jsonl(os.path.join(rd, "solve-certs.jsonl.gz"), certs)
    counts = Counter(r.get("status") for r in rows)
    rep = {"what": "EXP-PFDR-011cd0 canonical row set (merge_relcensus.py merge)",
           "run_id": a.run_id, "canonical_location": rel(rd), "created_at": now(),
           "attempts": attempts_info, "expected_keys": len(expected), "canonical_rows": len(rows),
           "missing_keys": [json.loads(k) for k in missing],
           "keys_with_exactly_one_canonical_row": not missing and not dup_same_attempt,
           "per_key_source": {k: {"attempt": sources[k]["attempt"], "job": sources[k]["job"],
                                  "rows_file": rel(os.path.join(absp(sources[k]["job_dir"]), "rows.jsonl.gz"))}
                              for k in keys_sorted},
           "superseded_rows": superseded, "duplicate_rows_within_attempt": dup_same_attempt,
           "non_cell_rows_excluded": non_cell,
           "harvest_rows_map": harvest_map,
           "harvest_rows_note": "harvest rows stay in their job directories and are mapped here (spec harvest_rows_note)",
           "bases_map": bases_map,
           "canonical_files": canonical, "canonical_staircase_records": len(stairs),
           "canonical_solve_certificates": len(certs),
           "counts_by_status": dict(counts),
           "sort_rule": "(bits, curve, m, arm, mode), stable"}
    with open(os.path.join(rd, "merge-report.json"), "w") as fh:
        json.dump(rep, fh, indent=1)
    print(json.dumps({k: rep[k] for k in ("run_id", "expected_keys", "canonical_rows",
                                          "keys_with_exactly_one_canonical_row", "counts_by_status")}))
    return 0 if rep["keys_with_exactly_one_canonical_row"] else 1


# ------------------------------------------------------------------------------------------
# view

def cmd_view(a) -> int:
    vd = a.out
    if os.path.exists(vd):
        print(f"refusing: view {vd} exists", file=sys.stderr)
        return 3
    os.makedirs(vd)
    entries = []
    for run in a.runs:
        tgt = absp(run)
        name = os.path.basename(tgt.rstrip("/"))
        link = os.path.join(vd, name)
        os.symlink(tgt, link)
        files = {}
        for root, dirs, fs in os.walk(tgt):
            dirs.sort()
            for f in sorted(fs):
                p = os.path.join(root, f)
                files[os.path.relpath(p, tgt)] = sha256(p)
        entries.append({"link": link, "target": rel(tgt), "files_sha256": files})
    vm = {"what": "EXP-PFDR-011cd0 scratch view (NA-16 F-J2-1)", "created_at": now(),
          "view_dir": vd, "entries": entries}
    with open(os.path.join(vd, "view-map.json"), "w") as fh:
        json.dump(vm, fh, indent=1)
    print(json.dumps({"view": vd, "links": [e["link"] for e in entries]}))
    return 0


# ------------------------------------------------------------------------------------------
# fixcompare (G-FIX)

ARCHIVE = "experiments/EXP-PFDR-1b78f7/runs"


def archived_sources(old_runs: str) -> dict:
    """m -> (canonical rows path, staircase path, harvest-row resolver)."""
    base = absp(old_runs)
    out = {}
    m3 = os.path.join(base, "RUN-PFDR-1b78f7-census-m3")
    out[3] = {"rows": os.path.join(m3, "rows.jsonl.gz"), "stairs": os.path.join(m3, "staircase.jsonl.gz"),
              "hmap": None, "hfile": os.path.join(m3, "harvest-rows.jsonl.gz")}
    m4 = os.path.join(base, "RUN-PFDR-1b78f7-census-m4", "merged")
    out[4] = {"rows": os.path.join(m4, "rows.jsonl.gz"), "stairs": os.path.join(m4, "staircase.jsonl.gz"),
              "hmap": json.load(open(os.path.join(m4, "merge-report.json")))["harvest_rows_map"]}
    m5 = os.path.join(base, "RUN-PFDR-1b78f7-census-m5")
    out[5] = {"rows": os.path.join(m5, "rows.jsonl.gz"), "stairs": os.path.join(m5, "staircase.jsonl.gz"),
              "hmap": json.load(open(os.path.join(m5, "merge-report.json")))["harvest_rows_map"]}
    return out


def old_hkey(k) -> str:
    bits, c, m, arm, mode = k
    return json.dumps(["main", m, bits, c, arm, mode])


def strip_row(r: dict) -> dict:
    return {k: v for k, v in r.items() if k not in TIMING_KEYS}


def diff_dict(old: dict, new: dict, path: str, out: list, skip=()) -> None:
    """Every key of OLD compared with NEW (keys only in NEW are listed by the caller)."""
    for k, v in old.items():
        if k in skip:
            continue
        p = f"{path}.{k}" if path else k
        if k not in new:
            out.append({"path": p, "old": v, "new": "<absent>"})
        elif isinstance(v, dict) and isinstance(new[k], dict):
            diff_dict(v, new[k], p, out)
        elif v != new[k]:
            out.append({"path": p, "old": v, "new": new[k]})


def ss_groups(hrows: list[dict], scope_attempt: int | None = None) -> dict:
    """SS x-groups from star rows (first element shared): group -> rows (attempt order)."""
    g = defaultdict(list)
    for r in hrows:
        if r["class"] != "SS":
            continue
        if scope_attempt is not None and r["attempt"] > scope_attempt:
            continue
        g[json.dumps(r["elements"][0], sort_keys=True)].append(r)
    return g


def cmd_fixcompare(a) -> int:
    old = archived_sources(a.old_runs)
    new_rows = {ks(key_of(r)): r for r in read_jsonl(os.path.join(absp(a.new), "rows.jsonl.gz"))}
    new_stairs = defaultdict(list)
    for s in read_jsonl(os.path.join(absp(a.new), "staircase.jsonl.gz")):
        new_stairs[ks(key_of(s))].append(s)
    idx_files = sorted(os.path.join(absp(a.new), d, "jobs-index.json") for d in os.listdir(absp(a.new))
                       if d.startswith("attempt-") and os.path.exists(os.path.join(absp(a.new), d, "jobs-index.json")))
    scratch_of_job = {}
    for f in idx_files:
        for j in json.load(open(f))["jobs"]:
            if j.get("scratch_harvest_rows"):
                scratch_of_job[(j["m"], j["bits"], j["curve_offset"])] = j["scratch_harvest_rows"]
    ms = sorted({k[2] for k in map(json.loads, new_rows)})
    old_rows, old_stairs = {}, defaultdict(list)
    for m in ms:
        for r in read_jsonl(old[m]["rows"]):
            k = ks(key_of(r))
            if k in new_rows:
                old_rows[k] = r
        for s in read_jsonl(old[m]["stairs"]):
            k = ks(key_of(s))
            if k in new_rows:
                old_stairs[k].append(s)
    # old harvest rows per key (needed per job: m3 from the single root file)
    need = defaultdict(set)
    for k in new_rows:
        bits, c, m, arm, mode = json.loads(k)
        if m == 3:
            need[old[3]["hfile"]].add(k)
        else:
            ent = old[m]["hmap"].get(old_hkey((bits, c, m, arm, mode)))
            if ent:
                need[absp(ent["harvest_rows_file"])].add(k)
    old_h = defaultdict(list)
    old_h_sha = {}
    for path, keyset in need.items():
        old_h_sha[rel(path)] = sha256(path)
        for r in read_jsonl(path):
            kk = ks(key_of(r))
            if kk in keyset:
                old_h[kk].append(r)
    new_h = defaultdict(list)
    new_h_files = {}
    for (m, b, c), ent in scratch_of_job.items():
        new_h_files[f"{m}-b{b:02d}-c{c}"] = ent
        for r in read_jsonl(ent["path"]):
            new_h[ks(key_of(r))].append(r)
    report_inst, diff_rows_out = [], []
    digests = {}
    unattributed = []
    for k in sorted(new_rows, key=lambda x: tuple(json.loads(x))):
        nr, orow = new_rows[k], old_rows.get(k)
        kk = json.loads(k)
        ent = {"key": kk, "status_new": nr.get("status")}
        hn = new_h.get(k, [])
        digests[k] = {"new_harvest_rows_sha256": hashlib.sha256(b"".join(
            canonical_row_line(r) for r in hn)).hexdigest(), "new_harvest_rows": len(hn)}
        if orow is None:
            ent["problem"] = "no archived row for this key"
            unattributed.append(ent)
            report_inst.append(ent)
            continue
        diffs: list = []
        diff_dict({x: v for x, v in strip_row(orow).items() if x != "harvest"},
                  {x: v for x, v in strip_row(nr).items() if x != "harvest"}, "", diffs)
        ho, hn_blk = orow.get("harvest") or {}, nr.get("harvest") or {}
        hdiffs: list = []
        for top in ho:
            if top in HARVEST_TIMING_KEYS:
                continue
            if top == "SS":
                ss_o, ss_n = ho["SS"], hn_blk.get("SS", {})
                diff_dict({x: v for x, v in ss_o.get("at_stop", {}).items() if x not in PAIR_KEYS},
                          {x: v for x, v in ss_n.get("at_stop", {}).items()}, "harvest.SS.at_stop", hdiffs)
                diff_dict({x: v for x, v in ss_o.items() if x not in ("at_stop", "at_A_fix")},
                          ss_n, "harvest.SS", hdiffs)
                if ss_o.get("at_A_fix") is not None or ss_n.get("at_A_fix") is not None:
                    diff_dict({x: v for x, v in (ss_o.get("at_A_fix") or {}).items() if x not in PAIR_KEYS},
                              ss_n.get("at_A_fix") or {}, "harvest.SS.at_A_fix", hdiffs)
                pairs = {}
                for scope in ("at_stop", "at_A_fix"):
                    so, sn = ss_o.get(scope) or {}, ss_n.get(scope) or {}
                    for pk in PAIR_KEYS:
                        if pk in so:
                            pairs[f"{scope}.{pk}"] = {"old": so[pk], "new": sn.get(pk),
                                                      "new_ge_old": sn.get(pk) is not None and sn.get(pk) >= so[pk]}
                ent["ss_pairs"] = pairs
            else:
                if top not in hn_blk:
                    hdiffs.append({"path": f"harvest.{top}", "old": ho[top], "new": "<absent>"})
                elif isinstance(ho[top], dict):
                    diff_dict(ho[top], hn_blk[top], f"harvest.{top}", hdiffs)
                elif ho[top] != hn_blk[top]:
                    hdiffs.append({"path": f"harvest.{top}", "old": ho[top], "new": hn_blk[top]})
        so_st = sorted((json.dumps(s, sort_keys=True) for s in old_stairs.get(k, [])))
        sn_st = sorted((json.dumps(s, sort_keys=True) for s in new_stairs.get(k, [])))
        ent["staircase_equal"] = so_st == sn_st
        ho_rows = old_h.get(k, [])
        rows_equal = [canonical_row_line(r) for r in ho_rows] == [canonical_row_line(r) for r in hn]
        ent["harvest_rows_equal"] = rows_equal
        ent["harvest_rows_old"], ent["harvest_rows_new"] = len(ho_rows), len(hn)
        if not rows_equal:
            so_set = Counter(canonical_row_line(r) for r in ho_rows)
            sn_set = Counter(canonical_row_line(r) for r in hn)
            for line in (so_set - sn_set):
                diff_rows_out.append({"key": kk, "side": "old_only", "row": json.loads(line)})
            for line in (sn_set - so_set):
                diff_rows_out.append({"key": kk, "side": "new_only", "row": json.loads(line)})
        # C(k', 2) from the retained rows at <= 24 bits (all rows retained there)
        if kk[0] <= 24 and nr.get("harvest"):
            g = ss_groups(hn)
            ck2 = sum((len(v) + 1) * len(v) // 2 for v in g.values())
            ent["ss_pairs_raw_eq_Ck2_from_rows"] = (nr["harvest"]["SS"]["at_stop"]["pairs_raw"] == ck2)
            ent["ss_Ck2_from_rows"] = ck2
        # attribution: groups with >= 3 members whose members span >= 2 attempts (OBJ-5 straddle)
        g = ss_groups(hn)
        straddle = 0
        for v in g.values():
            first_att = v[0]["elements"][0]["enc"][0]
            atts = {first_att} | {r["attempt"] for r in v}
            if len(v) + 1 >= 3 and len(atts) >= 2:
                straddle += 1
        ent["ss_groups_ge3_spanning_ge2_attempts"] = straddle
        ent["solver_and_block_diffs"] = diffs + hdiffs
        pair_up = any(p["new"] != p["old"] for p in ent.get("ss_pairs", {}).values())
        bad = []
        if diffs or hdiffs:
            bad.append("non-pair differences")
        if not ent["staircase_equal"]:
            bad.append("staircase differs")
        if not rows_equal:
            bad.append("harvest rows differ")
        if any(not p["new_ge_old"] for p in ent.get("ss_pairs", {}).values()):
            bad.append("SS pairs new < old")
        if ent.get("ss_pairs_raw_eq_Ck2_from_rows") is False:
            bad.append("SS pairs_raw != C(k',2) from rows")
        if pair_up and straddle == 0:
            bad.append("pair difference without a straddling x-group")
        ent["unattributed"] = bad
        if bad:
            unattributed.append({"key": kk, "reasons": bad})
        report_inst.append(ent)
    passed = not unattributed and len(new_rows) == len(old_rows)
    dr_path = os.path.join(absp(a.new), "fix-diff-rows.jsonl.gz")
    dr_sha = write_gz_jsonl(dr_path, diff_rows_out)
    with open(os.path.join(absp(a.new), "fix-digests.json"), "w") as fh:
        json.dump({"what": "per-instance sha256 of the R10 harvest-row stream (canonical lines) in the task scratch",
                   "scratch_files": new_h_files, "per_instance": digests}, fh, indent=1)
    rep = {"gate": "G-FIX", "pass": passed, "created_at": now(),
           "new_run": rel(absp(a.new)), "old_runs": rel(absp(a.old_runs)),
           "instances_compared": len(report_inst), "archived_rows_found": len(old_rows),
           "archived_harvest_files_sha256": old_h_sha,
           "instances_with_pair_change": sum(1 for e in report_inst
                                             if any(p["new"] != p["old"] for p in e.get("ss_pairs", {}).values())),
           "unattributed": unattributed, "fix_diff_rows": {"path": rel(dr_path), "sha256": dr_sha,
                                                           "rows": len(diff_rows_out)},
           "rules": ("every solver column, TT/TB/table/ss_store/on block key of the archived row equal "
                     "(timing keys excluded); informative ranks and census_saturated_at_row equal; "
                     "staircases equal; harvest rows equal; SS pairs_raw/pairs_formal/pairs_nonformal "
                     "(at_stop, at_A_fix) new >= old; at <= 24 bits new pairs_raw == sum C(k',2) from the "
                     "retained rows; a pair difference needs an SS x-group of >= 3 members spanning >= 2 "
                     "attempts in that instance"),
           "instances": report_inst}
    with open(absp(a.out), "w") as fh:
        json.dump(rep, fh, indent=1)
    print(json.dumps({k: rep[k] for k in ("gate", "pass", "instances_compared", "archived_rows_found",
                                          "instances_with_pair_change")} | {"unattributed": len(unattributed)}))
    return 0 if passed else 1


# ------------------------------------------------------------------------------------------
# srchcompare (G-SRCH) and tabcompare (G-TAB)

def load_canonical(run_dir: str) -> tuple[dict, dict]:
    rd = absp(run_dir)
    rows = {ks(key_of(r)): r for r in read_jsonl(os.path.join(rd, "rows.jsonl.gz"))}
    mr = json.load(open(os.path.join(rd, "merge-report.json")))
    return rows, mr


def harvest_rows_for(mr: dict, keys: set, cls: set) -> dict:
    files = defaultdict(set)
    for k in keys:
        ent = mr["harvest_rows_map"].get(k)
        if ent and ent["harvest_rows_file"]:
            files[ent["harvest_rows_file"]].add(k)
    out = defaultdict(list)
    for f, keyset in files.items():
        for r in read_jsonl(absp(f)):
            k = ks(key_of(r))
            if k in keyset and r["class"] in cls:
                out[k].append(r)
    return out


def rdir(x: str) -> str:
    """A run given by id (RUN-...) or by path."""
    return x if (os.path.isabs(x) or x.startswith("experiments")) else os.path.join(EXPDIR, "runs", x)


def ik(k: str) -> str:
    """Instance key without the mode."""
    b, c, m, arm, _ = json.loads(k)
    return json.dumps([b, c, m, arm])


def cmd_srchcompare(a) -> int:
    srows, smr = load_canonical(rdir(a.search))
    crows, cmr = load_canonical(rdir(a.check))
    s_by = {ik(k): k for k in srows}
    pairs = []
    for k in crows:
        if ik(k) in s_by:
            pairs.append((k, s_by[ik(k)]))
    sh = harvest_rows_for(smr, {s for _, s in pairs}, {"SS"})
    ch = harvest_rows_for(cmr, {c for c, _ in pairs}, {"SS"})
    inst, fails, prefix_listed = [], [], []
    strip = lambda r: {x: v for x, v in r.items() if x not in KEY_FIELDS}
    for ck, sk in sorted(pairs, key=lambda p: tuple(json.loads(p[0]))):
        cr, sr = crows[ck], srows[sk]
        ent = {"key": json.loads(ik(ck))}
        if cr.get("status") != "completed_valid" or sr.get("status") != "completed_valid":
            ent["skipped"] = f"status census={cr.get('status')} search={sr.get('status')}"
            inst.append(ent)
            fails.append(ent)
            continue
        cx, sx = cr["harvest"]["SS"]["at_X_fix"], sr["harvest"]["SS"]["at_X_fix"]
        crs = [strip(r) for r in ch.get(ck, [])]
        if not cx["censored"]:
            ent["block_equal"] = cx == sx
            srs = [strip(r) for r in sh.get(sk, []) if r["seq"] < sx["X_fix"]]
            ent["xfix_rows_equal"] = crs == srs
            ok = ent["block_equal"] and ent["xfix_rows_equal"]
        else:
            # census stopped before X_fix: compare the recorded prefix (attempts <= census's)
            att = cr["attempts"]
            srs = [strip(r) for r in sh.get(sk, []) if r["attempt"] <= att]
            ent["censored_prefix_rows_equal"] = crs == srs
            ent["census_attempts"] = att
            ok = ent["censored_prefix_rows_equal"]
            prefix_listed.append(ent["key"])
        ent["rows_digest_equal"] = (cr["harvest"].get("rows_digest") == sr["harvest"].get("rows_digest"))
        ok = ok and ent["rows_digest_equal"]
        ent["pass"] = ok
        if not ok:
            fails.append(ent)
        inst.append(ent)
    passed = not fails and len(pairs) == len(crows)
    rep = {"gate": "G-SRCH", "pass": passed, "created_at": now(), "check_run": rel(absp(rdir(a.check))),
           "search_run": a.search, "check_instances": len(crows), "matched": len(pairs),
           "census_stopped_before_X_fix": prefix_listed, "failures": fails, "instances": inst,
           "rules": ("at_X_fix SS block equal and SS rows with seq < X_fix equal (all fields but the key; "
                     "R14 retains exactly those rows); census stopped before X_fix: rows of attempts <= "
                     "census attempts equal (listed); TT/TB rows_digest equal")}
    with open(a.out, "w") as fh:
        json.dump(rep, fh, indent=1)
    print(json.dumps({k: rep[k] for k in ("gate", "pass", "check_instances", "matched")}
                     | {"failures": len(fails), "censored": len(prefix_listed)}))
    return 0 if passed else 1


def cmd_tabcompare(a) -> int:
    trows, tmr = load_canonical(rdir(a.table))
    srows, smr = load_canonical(rdir(a.search))
    t_by = {ik(k): k for k in trows}
    pairs = [(t_by[ik(k)], k) for k in srows if ik(k) in t_by]
    th = harvest_rows_for(tmr, {t for t, _ in pairs}, {"TT", "TB"})
    inst, fails = [], []
    for tk, sk in sorted(pairs, key=lambda p: tuple(json.loads(p[0]))):
        tr, sr = trows[tk], srows[sk]
        ent = {"key": json.loads(ik(tk))}
        if tr.get("status") != "completed_valid" or sr.get("status") != "completed_valid":
            ent["skipped"] = f"status table={tr.get('status')} search={sr.get('status')}"
            fails.append(ent)
            inst.append(ent)
            continue
        ok = True
        for c in ("TT", "TB"):
            beq = tr["harvest"][c] == sr["harvest"][c]
            h = hashlib.sha256()
            n = 0
            for r in th.get(tk, []):
                if r["class"] == c:
                    h.update(canonical_row_line({x: v for x, v in r.items() if x not in KEY_FIELDS}))
                    n += 1
            deq = sr["harvest"].get("rows_digest", {}).get(c) == h.hexdigest()
            ent[c] = {"block_equal": beq, "rows_digest_equal": deq, "rows": n,
                      "digest_rows_search": sr["harvest"].get("rows_digest_rows", {}).get(c)}
            ok = ok and beq and deq
        ent["table_block_equal"] = tr["harvest"]["table"] == sr["harvest"]["table"]
        ok = ok and ent["table_block_equal"]
        ent["pass"] = ok
        if not ok:
            fails.append(ent)
        inst.append(ent)
    passed = not fails and len(pairs) == len(srows)
    rep = {"gate": "G-TAB", "pass": passed, "created_at": now(), "table_run": a.table,
           "search_run": a.search, "search_instances": len(srows), "matched": len(pairs),
           "failures": fails, "instances": inst,
           "rules": ("for every (m, bits, curve, arm) in R12 and R13: TT and TB blocks equal and R13's "
                     "rows_digest equals the sha256 of R12's canonical TT/TB row stream (harvest.canonical_row_line "
                     "of each row without key fields, in file order)")}
    with open(a.out, "w") as fh:
        json.dump(rep, fh, indent=1)
    print(json.dumps({k: rep[k] for k in ("gate", "pass", "search_instances", "matched")} | {"failures": len(fails)}))
    return 0 if passed else 1


def cmd_curvecheck(a) -> int:
    design = json.load(open(a.design))
    cur = {(c["bits"], c["curve"]): c for c in design["curves"]}
    fails, n = [], 0
    for run in a.runs:
        rd = absp(run if (os.path.isabs(run) or run.startswith("experiments")) else os.path.join(EXPDIR, "runs", run))
        for r in read_jsonl(os.path.join(rd, "rows.jsonl.gz")):
            if r.get("status") == "failed_infrastructure" and "p" not in r:
                continue
            n += 1
            d = cur.get((r["bits"], r["curve"]))
            got = (r.get("p"), r.get("a"), r.get("b"), r.get("N"), r.get("P"))
            want = None if d is None else (d["p"], d["a"], d["b"], d["N"], d["P"])
            if got != want:
                fails.append({"run": rel(rd), "key": list(key_of(r)), "reason":
                              "no design entry" if d is None else "curve fields differ"})
    rep = {"gate": "G-CURVE", "pass": not fails, "created_at": now(), "design": a.design,
           "design_sha256": sha256(a.design), "runs": a.runs, "instances_checked": n,
           "failures": fails[:500], "failure_count": len(fails)}
    with open(a.out, "w") as fh:
        json.dump(rep, fh, indent=1)
    print(json.dumps({k: rep[k] for k in ("gate", "pass", "instances_checked", "failure_count")}))
    return 0 if rep["pass"] else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("merge")
    m.add_argument("--run-dir", required=True)
    m.add_argument("--run-id", required=True)
    m.add_argument("--attempts", nargs="+", required=True)
    v = sub.add_parser("view")
    v.add_argument("--runs", nargs="+", required=True)
    v.add_argument("--out", required=True)
    f = sub.add_parser("fixcompare")
    f.add_argument("--old-runs", required=True)
    f.add_argument("--new", required=True)
    f.add_argument("--scratch", required=False, default=None)
    f.add_argument("--out", required=True)
    s = sub.add_parser("srchcompare")
    s.add_argument("--search", required=True)
    s.add_argument("--check", required=True)
    s.add_argument("--out", required=True)
    t = sub.add_parser("tabcompare")
    t.add_argument("--table", required=True)
    t.add_argument("--search", required=True)
    t.add_argument("--out", required=True)
    c = sub.add_parser("curvecheck")
    c.add_argument("--design", required=True)
    c.add_argument("--runs", nargs="+", required=True)
    c.add_argument("--out", required=True)
    a = ap.parse_args()
    return {"merge": cmd_merge, "view": cmd_view, "fixcompare": cmd_fixcompare,
            "srchcompare": cmd_srchcompare, "tabcompare": cmd_tabcompare,
            "curvecheck": cmd_curvecheck}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
