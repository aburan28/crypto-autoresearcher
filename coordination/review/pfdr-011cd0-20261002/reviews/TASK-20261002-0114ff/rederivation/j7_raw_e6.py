#!/usr/bin/env python3
"""J7 (d), (e), (f): write_raw_v6.py re-run comparison; E-6 status; E-4 data files.

TASK-20261002-0114ff. Standard library plus PyYAML (parsing only).
(d) archived raw-result.json of R12, R13, R14 roots and R15, R16 vs the re-run on
    scratch copies (written_at and files_sha256 excluded; path strings mapped);
    files_sha256 snapshot semantics: every archived files_sha256 entry is compared
    with the archived file's current bytes, and the files present now but absent
    from the snapshot are listed.
(e) E-6 recomputed from raw-result.json and execution.json only, against each
    location's manifest status; finalize-extra.yaml (roots, R15, R16) against E-4 (3)
    and the raw-result values it must copy; finalize-inputs.json (attempts) against
    E-4 (2).
(f) executed_sources over-inclusion at roots (files listed that the location did not
    run) is listed for the record.
"""
import hashlib
import json
import os
import sys

import yaml

WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-pfdr011cd0-5753edf2e"
S = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/rv-0114ff/wr"
REPO = "/home/user/crypto-autoresearcher"
EXP = "experiments/EXP-PFDR-011cd0"
LOCS = [("RUN-PFDR-011cd0-table", "panel-root"), ("RUN-PFDR-011cd0-search", "panel-root"),
        ("RUN-PFDR-011cd0-srch-check", "srch-check-root"), ("RUN-PFDR-011cd0-calibrate", "calibrate"),
        ("RUN-PFDR-011cd0-analysis", "analysis")]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def canon(x, maps):
    if isinstance(x, dict):
        return {canon(k, maps): canon(v, maps) for k, v in x.items()}
    if isinstance(x, list):
        return [canon(v, maps) for v in x]
    if isinstance(x, str):
        for a, b in maps:
            x = x.replace(a, b)
    return x


def main():
    amd = yaml.safe_load(open(f"{WT}/{EXP}/amendments/AMD-20261002-236691.yaml"))["protocol_amendment"]
    block, task, notes = amd["manifest_protocol_block_v6"], amd["manifest_task_id_v6"], amd["manifest_writer_notes_v6"]
    pin_cal = yaml.safe_load(open(f"{WT}/{EXP}/implementation-notes-236691.yaml"))["pin_calibration_json"]["pins"]["calibration_json"]["sha256"]
    design_pin = "eb7e907d57b3486f5ceda4684498f6671e168df7925424c7522e13f0514ede0e"
    rep = {"d_write_raw": {}, "e_status": {}, "e_finalize_extra": {}, "e_finalize_inputs": {}, "f_executed_sources": {}}
    for run, kind in LOCS:
        loc = f"{WT}/{EXP}/runs/{run}"
        arch = json.load(open(f"{loc}/raw-result.json"))
        scr = f"{S}/{run}"
        maps = [(os.path.relpath(scr, REPO), f"{EXP}/runs/{run}"),
                (os.path.relpath(f"{WT}/{EXP}/amd-236691/write_raw_v6.py", REPO), f"{EXP}/amd-236691/write_raw_v6.py")]
        new = canon(json.load(open(f"{scr}/raw-result.json")), maps)
        keys = sorted((set(arch) | set(new)) - {"written_at", "files_sha256"})
        diff = [k for k in keys if arch.get(k) != new.get(k)]
        snap = arch.get("files_sha256") or {}
        snap_bad = [f for f, h in snap.items() if not os.path.exists(f"{loc}/{f}") or sha(f"{loc}/{f}") != h]
        present = []
        for r_, ds, fs in os.walk(loc):
            for f in fs:
                rr = os.path.relpath(os.path.join(r_, f), loc)
                if rr not in ("raw-result.json", "manifest.yaml", "checksums.sha256"):
                    present.append(rr)
        rep["d_write_raw"][run] = {"kind": kind, "keys_compared": keys, "differing_keys": diff,
                                   "differences": {k: [arch.get(k), new.get(k)] for k in diff},
                                   "archived_absent_keys": arch.get("absent_keys"),
                                   "files_sha256_snapshot_entries": len(snap),
                                   "snapshot_entries_whose_file_changed_since": snap_bad,
                                   "files_present_now_not_in_snapshot": sorted(set(present) - set(snap))}
        # E-6 status
        m = yaml.safe_load(open(f"{loc}/manifest.yaml"))["run"]
        if kind in ("panel-root", "srch-check-root"):
            mg = arch["merge"]
            gates = arch["gates"]
            gate_false = [g for g, v in gates.items() if v.get("pass") is False]
            gate_absent = [g for g, v in gates.items() if v.get("pass") is None]
            if mg["duplicate_rows_within_attempt_count"] or gate_false:
                st, cl = "invalid", "a"
            elif mg["missing_keys_count"] or gate_absent:
                st, cl = "failed_infrastructure", "b"
            else:
                st, cl = "completed_valid", "c"
        elif kind == "calibrate":
            ex = json.load(open(f"{loc}/execution.json"))
            al = arch["arm_read_log"]
            absent = [f for f in ("calibration.json", "arm-read-log.json", "null-tables.npz", "view-map.json") if not os.path.exists(f"{loc}/{f}")]
            cal_design = json.load(open(f"{loc}/calibration.json")).get("design_sha256")
            if ex.get("exit_code") == 4 or al.get("structured_or_planted_arm_parsed") is True:
                st, cl = "invalid", "R15 invalid"
            elif ex.get("exit_code") != 0 or ex.get("watchdog_expired") or absent or cal_design != design_pin:
                st, cl = "failed_infrastructure", "R15 fi"
            else:
                st, cl = "completed_valid", "R15 cv"
        else:
            ex = json.load(open(f"{loc}/execution.json"))
            absent = [f for f in ("analysis.json", "cells.jsonl", "heuristics.json", "view-map.json") if not os.path.exists(f"{loc}/{f}")]
            an_cal = json.load(open(f"{loc}/analysis.json"))["calibration"]["sha256"]
            if ex.get("exit_code") != 0 or ex.get("watchdog_expired") or absent or an_cal != pin_cal:
                st, cl = "failed_infrastructure", "R16 fi"
            else:
                st, cl = "completed_valid", "R16 cv"
        rep["e_status"][run] = {"recomputed": st, "clause": cl, "manifest_status": m["status"],
                                "manifest_status_rule": m.get("status_rule"), "equal": st == m["status"]}
        # finalize-extra.yaml (E-4 (3))
        fe = yaml.safe_load(open(f"{loc}/finalize-extra.yaml"))
        ck = {"extra.protocol": fe.get("extra", {}).get("protocol") == block,
              "extra.task_id": fe.get("extra", {}).get("task_id") == task,
              "extra.canonical": fe.get("extra", {}).get("canonical") is True,
              "extra.status_rule": str(fe.get("extra", {}).get("status_rule", "")).startswith("AMD-20261002-236691 E-6"),
              "inputs.executed_sources": isinstance(fe.get("inputs", {}).get("executed_sources"), dict),
              "inputs.writer_notes": fe.get("inputs", {}).get("writer_notes") == notes,
              "deviations_list": isinstance(fe.get("deviations"), list),
              "unexpected_list": isinstance(fe.get("unexpected"), list)}
        if kind in ("panel-root", "srch-check-root"):
            ck["completeness == raw merge"] = fe.get("completeness") == arch["merge"]
            summ = fe.get("summary") or {}
            ck["summary.gates == raw gates"] = summ.get("gates", summ) == arch["gates"] or all(summ.get(k) == v for k, v in arch["gates"].items()) or summ.get("gates") == arch["gates"]
            ck["timing present"] = bool(fe.get("timing", {}).get("started_at")) and bool(fe.get("timing", {}).get("finished_at"))
            idx = json.load(open(f"{loc}/attempt-1/jobs-index.json"))
            ck["timing.started_at == attempt jobs-index started_at"] = fe.get("timing", {}).get("started_at") == idx["started_at"]
            res = fe.get("resources", {})
            jobs = idx["jobs"]
            ck["resources.peak_rss == max job"] = res.get("peak_rss_bytes_max_job_process") == max((j.get("peak_rss_bytes") or 0) for j in jobs)
            ck["resources.cpu == sum jobs"] = abs((res.get("cpu_seconds_sum_job_processes") or 0) - round(sum((j.get("cpu_seconds") or 0) for j in jobs), 3)) < 0.01
            ck["resources.wall == attempts"] = res.get("wall_seconds_attempts") == idx["wall_seconds"]
            ck["spec_command == frozen"] = bool(fe.get("spec_command"))
            if run.endswith("table") or run.endswith("search"):
                ck["summary fixed E-6 note"] = "Cross-run gates G-TAB, G-SRCH, G-CURVE and G-REL are evaluated at" in json.dumps(fe.get("summary"))
        elif kind == "calibrate":
            ck["completeness.outputs_present"] = sorted(fe.get("completeness", {}).get("outputs_present", [])) == sorted(["calibration.json", "arm-read-log.json", "null-tables.npz", "view-map.json"])
        else:
            ck["completeness.outputs_present"] = sorted(fe.get("completeness", {}).get("outputs_present", [])) == sorted(["analysis.json", "cells.jsonl", "heuristics.json", "view-map.json"])
            ck["summary.outcome_ids == raw"] = (fe.get("summary") or {}).get("outcome_ids") == arch.get("outcome_ids")
        ck["manifest inputs.executed_sources == finalize-extra"] = m["inputs"].get("executed_sources") == fe.get("inputs", {}).get("executed_sources")
        rep["e_finalize_extra"][run] = {"checks": ck, "failed": [k for k, v in ck.items() if not v],
                                        "top_keys": sorted(fe), "summary_keys": sorted((fe.get("summary") or {}).keys())}
        # (f) executed sources at the location
        es = fe.get("inputs", {}).get("executed_sources") or {}
        rep["f_executed_sources"][run] = sorted(es)
        # attempts: finalize-inputs.json (E-4 (2))
        if os.path.exists(f"{loc}/attempt-1/finalize-inputs.json"):
            fi = json.load(open(f"{loc}/attempt-1/finalize-inputs.json"))
            rep["e_finalize_inputs"][run + "/attempt-1"] = {
                "exactly_two_keys": sorted(fi) == ["executed_sources", "writer_notes"],
                "writer_notes_equal_v6": fi.get("writer_notes") == notes,
                "executed_sources": sorted(fi.get("executed_sources", {})),
                "hashes_equal_worktree": all(os.path.exists(f"{WT}/{p}") and sha(f"{WT}/{p}") == h for p, h in fi.get("executed_sources", {}).items())}
    json.dump(rep, open(sys.argv[1], "w"), indent=1, sort_keys=True, default=str)
    for run, v in rep["d_write_raw"].items():
        print("D", run, "differing:", v["differing_keys"], json.dumps(v["differences"], default=str)[:400], "| snapshot changed:", v["snapshot_entries_whose_file_changed_since"][:8], "| now-not-in-snapshot:", v["files_present_now_not_in_snapshot"][:10])
    for run, v in rep["e_status"].items():
        print("E6", run, v)
    for run, v in rep["e_finalize_extra"].items():
        print("FE", run, "failed:", v["failed"], "summary keys:", v["summary_keys"])
    for run, v in rep["e_finalize_inputs"].items():
        print("FI", run, {k: v[k] for k in ("exactly_two_keys", "writer_notes_equal_v6", "hashes_equal_worktree")})
    for run, v in rep["f_executed_sources"].items():
        print("ES", run, v)


if __name__ == "__main__":
    main()
