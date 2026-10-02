"""AMD-20261002-236691 E-5 (3)-(4): raw-result.json writer for run roots and run directories.
TASK-20261002-71b610.

  write_raw_v6.py --kind {panel-root|srch-check-root|stage-r-root|calibrate|analysis}
                  --dir <location> --run-id <id>

Standard library plus PyYAML.  Refuses (exit 3) if <location>/raw-result.json exists and writes
it with open mode 'x'.  Never opens a rows, harvest-rows, staircase, bases or solve-certs file;
copies values from the named JSON/YAML files only and computes no statistic, kappa, z, ratio,
dispersion or relation count.  A key (or file) absent from a source is written as null and
listed in absent_keys; it never raises on a missing key.  Prints only the path written and its
list of top-level keys.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys

import yaml

REPO = "/home/user/crypto-autoresearcher"
KINDS = ("panel-root", "srch-check-root", "stage-r-root", "calibrate", "analysis")
EXCLUDED = {"raw-result.json", "manifest.yaml", "checksums.sha256"}
NEVER_OPEN = ("rows.jsonl", "harvest-rows.jsonl", "staircase.jsonl", "bases.jsonl", "solve-certs.jsonl")
ABSENT = object()


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(p):
    return os.path.relpath(os.path.abspath(p), REPO)


class Src:
    """Value copier: every missing file or key becomes None and is listed in absent_keys."""

    def __init__(self, loc):
        self.loc = loc
        self.absent = []
        self.cache = {}

    def load(self, relname):
        if any(os.path.basename(relname).startswith(x) for x in NEVER_OPEN):
            raise SystemExit(f"refusing to open {relname} (E-5 (3))")
        if relname in self.cache:
            return self.cache[relname]
        p = os.path.join(self.loc, relname)
        doc = ABSENT
        if os.path.exists(p):
            with open(p) as fh:
                doc = yaml.safe_load(fh) if relname.endswith(".yaml") else json.load(fh)
        self.cache[relname] = doc
        return doc

    def get(self, relname, *path):
        doc = self.load(relname)
        label = relname + ("" if not path else ":" + ".".join(str(x) for x in path))
        if doc is ABSENT:
            self.absent.append(label)
            return None
        cur = doc
        for k in path:
            if isinstance(cur, dict) and k in cur:
                cur = cur[k]
            elif isinstance(cur, list) and isinstance(k, int) and -len(cur) <= k < len(cur):
                cur = cur[k]
            else:
                self.absent.append(label)
                return None
        return cur

    def length(self, relname, *path):
        v = self.get(relname, *path)
        return None if v is None else len(v)


def files_sha256(loc):
    out = {}
    for root, dirs, fs in os.walk(loc):
        dirs.sort()
        for f in sorted(fs):
            p = os.path.join(root, f)
            r = os.path.relpath(p, loc)
            if r in EXCLUDED:
                continue
            out[r] = sha256(p)
    return out


def attempt_dirs(loc):
    ds = [d for d in os.listdir(loc) if re.fullmatch(r"attempt-\d+", d) and os.path.isdir(os.path.join(loc, d))]
    return sorted(ds, key=lambda d: int(d.split("-")[1]))


def panel_common(s, loc):
    attempts = {}
    for att in attempt_dirs(loc):
        rr = os.path.join(att, "raw-result.json")
        attempts[att] = {
            "status": s.get(os.path.join(att, "manifest.yaml"), "run", "status"),
            "raw_result_sha256": sha256(os.path.join(loc, rr)) if os.path.exists(os.path.join(loc, rr)) else None,
            "completeness": s.get(rr, "completeness"),
            "status_totals": s.get(rr, "status_totals"),
            "not_started": s.get(rr, "not_started"),
            "checkpoint": s.get(rr, "checkpoint"),
        }
        if attempts[att]["raw_result_sha256"] is None:
            s.absent.append(rr + " (sha256)")
    mr = "merge-report.json"
    merge = {
        "expected_keys": s.get(mr, "expected_keys"),
        "canonical_rows": s.get(mr, "canonical_rows"),
        "missing_keys_count": s.length(mr, "missing_keys"),
        "keys_with_exactly_one_canonical_row": s.get(mr, "keys_with_exactly_one_canonical_row"),
        "counts_by_status": s.get(mr, "counts_by_status"),
        "superseded_rows_count": s.length(mr, "superseded_rows"),
        "duplicate_rows_within_attempt_count": s.length(mr, "duplicate_rows_within_attempt"),
        "non_cell_rows_excluded_count": s.length(mr, "non_cell_rows_excluded"),
        "canonical_files": s.get(mr, "canonical_files"),
    }
    pks = s.get(mr, "per_key_source") or {}
    fi = []
    for att in attempt_dirs(loc):
        for ent in s.get(os.path.join(att, "raw-result.json"), "failed_infrastructure_instances") or []:
            src = pks.get(json.dumps(list(ent[:5])))
            if src is not None and src.get("attempt") == att:
                fi.append({"attempt": att, "entry": ent})
    return attempts, merge, fi


def exec_block(s):
    return {"exit_code": s.get("execution.json", "exit_code"),
            "watchdog_expired": s.get("execution.json", "watchdog_expired")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", required=True, choices=KINDS)
    ap.add_argument("--dir", required=True)
    ap.add_argument("--run-id", required=True)
    a = ap.parse_args()
    loc = a.dir if os.path.isabs(a.dir) else os.path.join(REPO, a.dir)
    out = os.path.join(loc, "raw-result.json")
    if os.path.exists(out):
        print(f"refusing: {rel(out)} exists", file=sys.stderr)
        return 3
    s = Src(loc)
    raw = {"run_id": a.run_id, "location": rel(loc), "kind": a.kind,
           "written_at": dt.datetime.now(dt.timezone.utc).isoformat(),
           "writer": {"path": rel(__file__), "sha256": sha256(os.path.abspath(__file__))},
           "files_sha256": files_sha256(loc),
           "files_sha256_note": ("snapshot at written_at of every file beneath the location except raw-result.json, "
                                 "manifest.yaml and checksums.sha256; files appended or written later (logs, "
                                 "post-processing records, finalize-extra.yaml) are covered by checksums.sha256")}
    if a.kind in ("panel-root", "srch-check-root", "stage-r-root"):
        attempts, merge, fi = panel_common(s, loc)
        raw.update({"attempts": attempts, "merge": merge, "failed_infrastructure_instances": fi})
        if a.kind == "panel-root":
            raw["gates"] = {"G4-R": {"pass": s.get("row-verify.json", "pass")}}
            raw["certificate"] = {"instances_claimed": 0, "note": "measurement run; no solve is claimed (kind none)"}
        elif a.kind == "srch-check-root":
            gr = s.get("grel-report.json", "runs") or {}
            raw["gates"] = {
                "G4-D": {"pass": s.get("solve-verify.json", "pass"), "records": s.get("solve-verify.json", "records"),
                         "verified": s.get("solve-verify.json", "verified")},
                "G-SRCH": {"pass": s.get("srch-report.json", "pass"),
                           "check_instances": s.get("srch-report.json", "check_instances"),
                           "matched": s.get("srch-report.json", "matched"),
                           "failures_count": s.length("srch-report.json", "failures")},
                "G-TAB": {"pass": s.get("tab-report.json", "pass"),
                          "search_instances": s.get("tab-report.json", "search_instances"),
                          "matched": s.get("tab-report.json", "matched"),
                          "failures_count": s.length("tab-report.json", "failures")},
                "G-CURVE": {"pass": s.get("curve-report.json", "pass"),
                            "instances_checked": s.get("curve-report.json", "instances_checked"),
                            "failure_count": s.get("curve-report.json", "failure_count")},
                "G-REL": {"pass": s.get("grel-report.json", "pass"),
                          "runs": {k: {"compared_instance_class_scopes": v.get("compared_instance_class_scopes"),
                                       "mismatch_count": v.get("mismatch_count")} for k, v in gr.items()}},
            }
            raw["certificate"] = {
                "instances_claimed": s.get("solve-verify.json", "records"),
                "instances_verified": s.get("solve-verify.json", "verified"),
                "verify_pass": s.get("solve-verify.json", "pass"),
                "verify_report": rel(os.path.join(loc, "solve-verify.json")),
                "verifier_sha256": s.get("solve-verify.json", "verifier_sha256"),
                "certificates_file": rel(os.path.join(loc, "solve-certs.jsonl.gz")),
                "certificates_sha256": s.get("solve-verify.json", "certificates_sha256"),
            }
        else:
            gr = s.get("grel-report.json", "runs") or {}
            raw["gates"] = {"G4-R": {"pass": s.get("row-verify.json", "pass")},
                            "G-REL": {"pass": s.get("grel-report.json", "pass"),
                                      "runs": {k: {"compared_instance_class_scopes": v.get("compared_instance_class_scopes"),
                                                   "mismatch_count": v.get("mismatch_count")} for k, v in gr.items()}}}
            steps = {}
            for st in ("step-calibrate", "step-unmask"):
                ex = os.path.join(st, "execution.json")
                steps[st] = {k: s.get(ex, k) for k in ("exit_code", "watchdog_expired", "wall_seconds",
                                                       "peak_rss_bytes_max_descendant", "cpu_seconds_descendants")}
            raw["steps"] = steps
            scp = os.path.join(loc, "stage-calibration.json")
            raw["stage_calibration_sha256"] = sha256(scp) if os.path.exists(scp) else None
            if raw["stage_calibration_sha256"] is None:
                s.absent.append("stage-calibration.json (sha256)")
            raw["outcome_ids"] = s.get("analysis.json", "outcome_ids")
            raw["certificate"] = {"instances_claimed": 0, "note": "measurement run; no solve is claimed (kind none)"}
    elif a.kind == "calibrate":
        cal = s.load("calibration.json")
        raw["exec"] = exec_block(s)
        if cal is ABSENT:
            s.absent.append("calibration.json")
            raw["declared_metrics"] = None
        else:
            raw["declared_metrics"] = {k: v for k, v in cal.items() if k not in ("generators", "cells")}
        raw["arm_read_log"] = {k: s.get("arm-read-log.json", k) for k in
                               ("structured_or_planted_arm_parsed", "illegal_parsed_arms", "parsed_arms")}
        raw["certificate"] = {"kind": "none", "instances_claimed": 0,
                              "note": "measurement run; no solve is claimed (kind none)"}
    else:  # analysis
        an = s.load("analysis.json")
        raw["exec"] = exec_block(s)
        if an is ABSENT:
            s.absent.append("analysis.json")
            raw["declared_metrics"] = None
        else:
            raw["declared_metrics"] = dict(an)
        raw["outcome_ids"] = s.get("analysis.json", "outcome_ids")
        cj = os.path.join(loc, "cells.jsonl")
        raw["cells_jsonl_sha256"] = sha256(cj) if os.path.exists(cj) else None
        if raw["cells_jsonl_sha256"] is None:
            s.absent.append("cells.jsonl (sha256)")
        h = s.load("heuristics.json")
        if h is ABSENT:
            s.absent.append("heuristics.json")
            h = None
        raw["heuristics"] = h
        raw["certificate"] = {"kind": "none", "instances_claimed": 0,
                              "note": "measurement run; no solve is claimed (kind none)"}
    raw["absent_keys"] = s.absent
    with open(out, "x") as fh:
        json.dump(raw, fh, indent=1)
    print(rel(out))
    print(json.dumps(list(raw.keys())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
