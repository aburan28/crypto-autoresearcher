#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocols 2-r4 / 2-a1-r4 -- the RL-3 RECORDER-GAP COMPUTATION, as launchkind's reading_rule words
it: childend RG-4 (b) with its attribution sentence replaced by gapattr RH-1, conditioned by attcount RI-1, with the
non-launch list as launchkind RJ-2 leaves it, and with the named gaps of RI-1 (c), RJ-1 (c), RJ-3 and RJ-4 (b). Stdout
paths are relativized EXACTLY as DEC-20260924-daf670 LKA-10 words it. New file.

Class (RH-7; RI-1 (f); RJ-1 (d); RJ-3; RJ-4; DEC-20260924-daf670 LKA-8): epsilon (SE-2 (5) recording) read-only, after
the driver has exited; its verdict effect is failclosed RF-3 (a)'s (E2). It attributes no file RH-1 does not (RI-1 (e);
RJ-1 (d)); every RI-1 / RJ condition only ADDS gaps.

DEFINITIONS USED
  run directory  the absolute path the package records for itself: command.txt line 2 "# GFPN_RUN_DIR=<path>" (LKA-10).
  relativize     a recorded path is relativized ONLY by removing the exact string prefix "<run directory>/"; no
                 normalization, symlink resolution or case folding (LKA-10). A path without that prefix does not
                 relativize.
  the six forms  (RJ-4 (a)) LK-1 child/<tag>.stdout; LK-2 solver/<tag>.ms.log; LK-3 solver/<tag>.callgrind.stdout;
                 LK-4 comparator/stdout.log; LK-5 health/<tag>.ms.log; LK-6 pari/<tag>.gp.stdout (<tag> one path
                 component).
  files          every file under child/, solver/, health/, comparator/ and pari/ of the package (RG-4 (b)).
  file_abs       "<run directory>/" + the file's relative path (the form the launch records carry).
ATTRIBUTION (RH-1 (i)-(vi), each reading only records written in the installing process or by the frozen code before
the launch): (i) stdout_path / stderr_path; (ii) an argv element equal to the file; (iii) an argv element
"--callgrind-out-file=<path>" with <path> the file; (iv) a directory named as a whole argv element by exactly one
record's argv, the file under it; (v) CHILD-JOB OUTPUT (child_end "exec"; last argv element the package's
child/<tag>.spec.json; that file parses and carries "out" == <dir>/<tag>; the file is <out>.npz or <out>.meta.json);
(vi) RENAMED ATTEMPT FILE (<tag>.ms.out|.ms.log|.ms.err + ".ssf-attempt<k>" in solver/ or health/; the event of
<tag> at that site lists it under renamed_files["attempt<k>"]; at least k records carry <dir>/<tag>.ms.log; R is the
k-th of them). NON-LAUNCH writes (RG-4 (b) as RJ-2 leaves it): a1_health.py 141-143 (health/<tag>.ms) and
a1_health.py 251 (health/health-<p>.json); a1_pari.py 91-93 is REMOVED by RJ-2.
RI-1: per (<dir>, <tag>) the counts (a) (i)-(iii); (b) one launch per other stdout_path; (c) a failed count is a named
gap and every file of the tag present is a gap; (d) at N >= 2 with (a) holding, the final files only to the last record.
RJ-1: Ncg(<tag>) == S-1 attempt records of <tag> with callgrind_result_present true; per site likewise.
RJ-3: comparator launch records == 1 iff raw-result.json carries mapping "comparator" with key "child", else 0.
RJ-4 (b): a launch record whose stdout_path does not relativize, or relativizes to none of the six forms, is an
UNKNOWN-KIND GAP.
"""
import json
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r4_common as R                                    # noqa: E402

FIVE_DIRS = ("child", "solver", "health", "comparator", "pari")
EVENTS_FILE = "solver-events.json"
FORMS = (                                                # RJ-4 (a): the six production launch kinds
    ("LK-1 child job (v2_driver.py 101)", re.compile(r"^child/([^/]+)\.stdout$")),
    ("LK-3 callgrind (v2_solver.py 517)", re.compile(r"^solver/([^/]+)\.callgrind\.stdout$")),
    ("LK-2 msolve at S-1 (v2_driver.py 166)", re.compile(r"^solver/([^/]+)\.ms\.log$")),
    ("LK-4 comparator (v2_driver.py 650)", re.compile(r"^(comparator)/stdout\.log$")),
    ("LK-5 msolve at S-2 (a1_health.py 147)", re.compile(r"^health/([^/]+)\.ms\.log$")),
    ("LK-6 gp (a1_pari.py 96)", re.compile(r"^pari/([^/]+)\.gp\.stdout$")),
)
# RG-4 (b) non-launch list as RJ-2 leaves it (a1_pari.py 91-93 REMOVED); the name patterns this stage derives
NONLAUNCH_R4 = (
    ("a1_health.py 141-143 (the health system's input file <tag>.ms)", re.compile(r"^health/health_p\d+_d\d+(_reinvoke|_seed2|_seed2_reinvoke)?\.ms$")),
    ("a1_health.py 251 (health-<p>.json)", re.compile(r"^health/health-\d+\.json$")),
)
# the childend / gapattr list BEFORE RJ-2 (used ONLY by a scratch evaluator that disables RJ-2; never by delivered code)
NONLAUNCH_BEFORE_RJ2 = NONLAUNCH_R4 + (
    ("a1_pari.py 91-93 (the gp script <tag>.gp)", re.compile(r"^pari/[^/]+\.gp$")),)
FINAL_EXTS = (".ms", ".ms.out", ".ms.log", ".ms.err")
RENAMED = re.compile(r"^(?P<tag>[^/]+)(?P<ext>\.ms\.out|\.ms\.log|\.ms\.err)\.ssf-attempt(?P<k>\d+)$")
SITE_OF_DIR = {"solver": R.SITE_S1, "health": R.SITE_S2}


# ----------------------------------------------------------------------------- inputs (read-only, after the driver exited)
def run_dir_recorded(rd_disk):
    """LKA-10: the run directory the package records for itself (command.txt line 2)."""
    try:
        lines = open(os.path.join(rd_disk, "command.txt")).read().splitlines()
    except OSError:
        return None
    if len(lines) >= 2 and lines[1].startswith("# GFPN_RUN_DIR="):
        return lines[1][len("# GFPN_RUN_DIR="):]
    return None


def relativize(path, rd_rec):
    """LKA-10: remove the exact prefix "<run directory>/" only; else None."""
    if not isinstance(path, str) or not rd_rec:
        return None
    pre = rd_rec + "/"
    return path[len(pre):] if path.startswith(pre) else None


def form_of(rel):
    """RJ-4 (a): (kind label, tag) of a relativized stdout path, or None."""
    if rel is None:
        return None
    for label, rx in FORMS:
        m = rx.match(rel)
        if m:
            return label, m.group(1)
    return None


def package_files(rd_disk):
    out = []
    for d in FIVE_DIRS:
        base = os.path.join(rd_disk, d)
        if not os.path.isdir(base):
            continue
        for dp, _dn, fn in os.walk(base):
            for f in fn:
                out.append(os.path.relpath(os.path.join(dp, f), rd_disk))
    return sorted(out)


def load_doc(rd_disk):
    try:
        return json.load(open(os.path.join(rd_disk, EVENTS_FILE)))
    except Exception:                                    # noqa: BLE001
        return None


def load_raw(rd_disk):
    try:
        return json.load(open(os.path.join(rd_disk, "raw-result.json")))
    except Exception:                                    # noqa: BLE001
        return None


def _argv(rec):
    a = rec.get("argv")
    return [x for x in a if isinstance(x, str)] if isinstance(a, list) else []


# ----------------------------------------------------------------------------- RH-1 attribution (epsilon)
def _renamed_ok(rel, rec, launches_by_log, doc, rd_rec):
    """RH-1 (vi) for one file and one record."""
    d, name = rel.split("/", 1) if "/" in rel else (None, rel)
    if d not in SITE_OF_DIR or "/" in name:
        return False
    m = RENAMED.match(name)
    if not m:
        return False
    tag, k = m.group("tag"), int(m.group("k"))
    site = ((doc or {}).get("sites") or {}).get(SITE_OF_DIR[d]) or {}
    listed = any(e.get("tag") == tag and name in ((e.get("renamed_files") or {}).get("attempt%d" % k) or {})
                 for e in site.get("events") or [])
    if not listed:
        return False
    L = launches_by_log.get((d, tag), [])
    return len(L) >= k and L[k - 1] is rec


def _spec_ok(rel, rec, rd_disk, rd_rec):
    """RH-1 (v) for one file and one record."""
    if rec.get("child_end") != "exec":
        return False
    argv = _argv(rec)
    if not argv:
        return False
    last = argv[-1]
    lrel = relativize(last, rd_rec)
    if lrel is None or not re.match(r"^child/[^/]+\.spec\.json$", lrel):
        return False
    try:
        spec = json.load(open(os.path.join(rd_disk, lrel)))
    except Exception:                                    # noqa: BLE001
        return False
    out = spec.get("out") if isinstance(spec, dict) else None
    if not isinstance(out, str) or out != last[:-len(".spec.json")]:
        return False
    return rd_rec + "/" + rel in (out + ".npz", out + ".meta.json")


def attribute(files, records, rd_disk, rd_rec, doc, launches_by_log, final_last):
    """RH-1 (i)-(vi) with RI-1 (d) (final_last: {(dir, tag): the last record of L, where N >= 2 and RI-1 (a) holds}).
    Returns {file: [(ordinal, clause), ...]}."""
    dir_named = {}
    for r in records:
        for x in set(_argv(r)):
            dir_named.setdefault(x, []).append(r)
    out = {}
    for rel in files:
        fa = rd_rec + "/" + rel if rd_rec else None
        hits = []
        d = rel.split("/", 1)[0]
        base = os.path.basename(rel)
        tag_final = None
        for ext in FINAL_EXTS:
            if d in SITE_OF_DIR and base.endswith(ext) and "/" not in rel[len(d) + 1:]:
                tag_final = base[:-len(ext)]
        for r in records:
            if fa is None:
                break
            argv = _argv(r)
            # RI-1 (d): an earlier record of L(<dir>, <tag>) attributes nothing by (i) or (ii); a record outside L (a
            # callgrind child naming <dir>/<tag>.ms) is not restricted
            restricted = (tag_final is not None and (d, tag_final) in final_last
                          and any(x is r for x in launches_by_log.get((d, tag_final), []))
                          and r is not final_last[(d, tag_final)])
            if not restricted:
                if fa in (r.get("stdout_path"), r.get("stderr_path")):
                    hits.append((r.get("ordinal"), "i"))
                if fa in argv:
                    hits.append((r.get("ordinal"), "ii"))
            if ("--callgrind-out-file=" + fa) in argv:
                hits.append((r.get("ordinal"), "iii"))
            for x in argv:
                if fa.startswith(x + "/") and len(dir_named.get(x, [])) == 1 and os.path.isabs(x):
                    hits.append((r.get("ordinal"), "iv"))
                    break
            if _spec_ok(rel, r, rd_disk, rd_rec):
                hits.append((r.get("ordinal"), "v"))
            if _renamed_ok(rel, r, launches_by_log, doc, rd_rec):
                hits.append((r.get("ordinal"), "vi"))
        out[rel] = hits
    return out


# ----------------------------------------------------------------------------- RI-1 counts (epsilon)
def ri1_counts(records, doc, rd_rec):
    """RI-1 (a) and (b). Returns (per_tag rows, site rows, duplicate rows, launches_by_log)."""
    sites = (doc or {}).get("sites") or {}
    launches_by_log = {}
    for r in records:
        rel = relativize(r.get("stdout_path"), rd_rec)
        f = form_of(rel)
        if f and (f[0].startswith("LK-2") or f[0].startswith("LK-5")):
            d = rel.split("/", 1)[0]
            launches_by_log.setdefault((d, f[1]), []).append(r)
    for L in launches_by_log.values():
        L.sort(key=lambda r: (r.get("ordinal") is None, r.get("ordinal")))
    keys = set(launches_by_log)
    for d, site in SITE_OF_DIR.items():
        sec = sites.get(site) or {}
        for a in sec.get("attempt_records") or []:
            keys.add((d, a.get("tag")))
        for p in sec.get("passthrough_records") or []:
            keys.add((d, p.get("tag")))
        for e in sec.get("events") or []:
            keys.add((d, e.get("tag")))
    rows = []
    for (d, tag) in sorted(keys, key=lambda x: (x[0], str(x[1]))):
        site = SITE_OF_DIR[d]
        sec = sites.get(site) or {}
        N = len(launches_by_log.get((d, tag), []))
        n_att = sum(1 for a in sec.get("attempt_records") or [] if a.get("tag") == tag)
        n_pt = sum(1 for p in sec.get("passthrough_records") or [] if p.get("tag") == tag) if site == R.SITE_S1 else 0
        ok_i = N == n_att + n_pt
        evs = [e for e in sec.get("events") or [] if e.get("tag") == tag]
        row = {"dir": d, "tag": tag, "N": N, "attempt_records": n_att, "passthrough_records": n_pt, "a_i": ok_i}
        if evs:
            e = evs[0]
            att = e.get("attempts") or []
            ren = e.get("renamed_files") or {}
            nums = [x.get("attempt") for x in att]
            ok_ii = (len(evs) == 1 and N == len(att) and N == e.get("accepted_attempt") and N == 1 + len(ren)
                     and nums == list(range(1, len(att) + 1)))
            row.update(event=True, n_events=len(evs), event_attempts=len(att), accepted_attempt=e.get("accepted_attempt"),
                       renamed_files_keys=len(ren), attempt_numbers=nums, a_ii=ok_ii)
        else:
            row.update(event=False, a_ii=True)
        row["holds"] = row["a_i"] and row["a_ii"]
        rows.append(row)
    site_rows = []
    for d, site in SITE_OF_DIR.items():
        c = ((sites.get(site) or {}).get("counters") or {})
        n = sum(len(v) for (dd, _t), v in launches_by_log.items() if dd == d)
        want = (c.get("attempts_total") or 0) + ((c.get("passthrough_calls_gb_only_true") or 0) if site == R.SITE_S1 else 0)
        site_rows.append({"site": site, "dir": d, "launch_records": n, "attempts_total": c.get("attempts_total"),
                          "passthrough_calls_gb_only_true": c.get("passthrough_calls_gb_only_true") if site == R.SITE_S1 else None,
                          "holds": n == want})
    by_path = {}
    for r in records:
        rel = relativize(r.get("stdout_path"), rd_rec)
        f = form_of(rel)
        if f and (f[0].startswith("LK-2") or f[0].startswith("LK-5")):
            continue
        by_path.setdefault(r.get("stdout_path"), []).append(r.get("ordinal"))
    dups = [{"stdout_path": p, "ordinals": o} for p, o in sorted(by_path.items(), key=lambda x: str(x[0])) if len(o) > 1]
    return rows, site_rows, dups, launches_by_log


# ----------------------------------------------------------------------------- RJ-1, RJ-3, RJ-4 (epsilon)
def rj1_callgrind(records, doc, rd_rec):
    """RJ-1 (b): Ncg(<tag>) == S-1 attempt records of <tag> with callgrind_result_present true; per site likewise."""
    ncg = {}
    for r in records:
        f = form_of(relativize(r.get("stdout_path"), rd_rec))
        if f and f[0].startswith("LK-3"):
            ncg[f[1]] = ncg.get(f[1], 0) + 1
    present = {}
    for a in (((doc or {}).get("sites") or {}).get(R.SITE_S1) or {}).get("attempt_records") or []:
        if (a.get("rb1") or {}).get("callgrind_result_present") is True:
            present[a.get("tag")] = present.get(a.get("tag"), 0) + 1
    rows = [{"tag": t, "Ncg": ncg.get(t, 0), "attempt_records_with_callgrind_result_present": present.get(t, 0),
             "holds": ncg.get(t, 0) == present.get(t, 0)} for t in sorted(set(ncg) | set(present), key=str)]
    site = {"callgrind_launch_records": sum(ncg.values()), "attempt_records_with_callgrind_result_present": sum(present.values()),
            "holds": sum(ncg.values()) == sum(present.values())}
    return rows, site


def rj3_comparator(records, raw, rd_rec):
    """RJ-3: comparator launch records == 1 iff raw-result.json carries mapping "comparator" with the key "child"."""
    n = 0
    for r in records:
        f = form_of(relativize(r.get("stdout_path"), rd_rec))
        if f and f[0].startswith("LK-4"):
            n += 1
    comp = (raw or {}).get("comparator") if isinstance(raw, dict) else None
    key = isinstance(comp, dict) and "child" in comp
    return {"comparator_launch_records": n, "raw_comparator_child_key_present": key, "holds": n == (1 if key else 0)}


def rj4_unknown(records, rd_rec):
    """RJ-4 (b): records whose stdout_path does not relativize (LKA-10) or matches none of the six forms."""
    out = []
    for r in records:
        rel = relativize(r.get("stdout_path"), rd_rec)
        if form_of(rel) is None:
            out.append({"ordinal": r.get("ordinal"), "stdout_path": r.get("stdout_path"),
                        "why": "no '<run directory>/' prefix (LKA-10)" if rel is None else "none of the six forms (RJ-4 (a))"})
    return out


# ----------------------------------------------------------------------------- the composition
def _evaluate(rd_disk, nonlaunch, ri1_on, rj1_on, rj3_on, rj4_on):
    """The RL-3 recorder-gap computation. Delivered code calls it ONLY through recorder_gaps() with every condition on
    and NONLAUNCH_R4; a development scratch evaluator may call it with a condition off (DEC-20260924-daf670 LKA-11 (b);
    launchkind RJ-5 (a), (c)), never a package."""
    rd_rec = run_dir_recorded(rd_disk)
    doc = load_doc(rd_disk)
    raw = load_raw(rd_disk)
    records = list((doc or {}).get("launch_records") or []) if isinstance(doc, dict) else []
    files = package_files(rd_disk)
    named = []
    if rd_rec is None:
        named.append({"kind": "RUN DIRECTORY NOT RECORDED", "why": "command.txt line 2 carries no '# GFPN_RUN_DIR=' (LKA-10)"})
    if doc is None:
        named.append({"kind": "SOLVER-EVENTS NOT READABLE", "why": "solver-events.json missing or unparseable"})
    rows, site_rows, dups, launches_by_log = ri1_counts(records, doc, rd_rec)
    tag_gap = set()
    dup_ordinals = set()
    final_last = {}
    if ri1_on:
        for r in rows:
            if not r["holds"]:
                named.append(dict(r, kind="COUNT GAP"))
                tag_gap.add((r["dir"], r["tag"]))
            elif r["N"] >= 2:
                final_last[(r["dir"], r["tag"])] = launches_by_log[(r["dir"], r["tag"])][-1]
        for s in site_rows:
            if not s["holds"]:
                named.append(dict(s, kind="SITE COUNT GAP"))
        for dd in dups:
            named.append(dict(dd, kind="DUPLICATE-PATH GAP"))
            dup_ordinals |= set(dd["ordinals"])
    cg_rows, cg_site = rj1_callgrind(records, doc, rd_rec)
    cg_gap_tags = set()
    if rj1_on:
        for r in cg_rows:
            if not r["holds"]:
                named.append(dict(r, kind="CALLGRIND COUNT GAP"))
                cg_gap_tags.add(r["tag"])
        if not cg_site["holds"]:
            named.append(dict(cg_site, kind="CALLGRIND SITE COUNT GAP"))
    comp = rj3_comparator(records, raw, rd_rec)
    comp_gap = rj3_on and not comp["holds"]
    if comp_gap:
        named.append(dict(comp, kind="COMPARATOR COUNT GAP"))
    unk = rj4_unknown(records, rd_rec) if rj4_on else []
    for u in unk:
        named.append(dict(u, kind="UNKNOWN-KIND GAP"))
    att = attribute(files, records, rd_disk, rd_rec, doc, launches_by_log, final_last)
    gaps, attribution, nonl = [], {}, {}
    for rel in files:
        why = []
        d = rel.split("/", 1)[0]
        base = os.path.basename(rel)
        # RI-1 (c): every file of a tag whose count failed
        for ext in FINAL_EXTS:
            if d in SITE_OF_DIR and base.endswith(ext) and (d, base[:-len(ext)]) in tag_gap:
                why.append("RI-1 (c): a file of a tag with a COUNT GAP")
        m = RENAMED.match(base)
        if d in SITE_OF_DIR and m and (d, m.group("tag")) in tag_gap:
            why.append("RI-1 (c): a renamed file of a tag with a COUNT GAP")
        # RJ-1 (c)
        if d == "solver":
            for suf in (".callgrind.stdout", ".callgrind.stderr", ".callgrind.out"):
                if base.endswith(suf) and base[:-len(suf)] in cg_gap_tags:
                    why.append("RJ-1 (c): a callgrind file of a tag with a CALLGRIND COUNT GAP")
        # RJ-3
        if d == "comparator" and comp_gap:
            why.append("RJ-3: a comparator/ file with a COMPARATOR COUNT GAP")
        hits = att.get(rel) or []
        # RI-1 (c): every file RH-1 attributes to a record carrying a duplicated stdout_path
        if any(o in dup_ordinals for o, _c in hits):
            why.append("RI-1 (c): attributed to a record with a DUPLICATE-PATH GAP")
        nl = [label for label, rx in nonlaunch if rx.match(rel)]
        if not hits and not nl:
            why.append("RH-1: attributed to no launch record and not a listed non-launch write")
        attribution[rel] = hits
        if nl:
            nonl[rel] = nl
        if why:
            gaps.append({"file": rel, "why": sorted(set(why))})
    return {"run_directory_recorded": rd_rec, "n_launch_records": len(records), "n_files": len(files),
            "files": files, "attribution": {k: [list(x) for x in v] for k, v in attribution.items()},
            "non_launch_files": nonl, "non_launch_list": [label for label, _rx in nonlaunch],
            "ri1_rows": rows, "ri1_site_rows": site_rows, "ri1_duplicate_paths": dups,
            "rj1_rows": cg_rows, "rj1_site": cg_site, "rj3": comp, "rj4_unknown_kind": unk,
            "conditions": {"RI-1": ri1_on, "RJ-1": rj1_on, "RJ-2": nonlaunch is NONLAUNCH_R4, "RJ-3": rj3_on, "RJ-4 (b)": rj4_on},
            "named_gaps": named, "gap_files": gaps, "any_gap": bool(named or gaps)}


def recorder_gaps(rd_disk):
    """RL-3 RECORDER GAPS as launchkind's reading_rule words it: every condition on; the RJ-2 non-launch list."""
    return _evaluate(rd_disk, NONLAUNCH_R4, True, True, True, True)
