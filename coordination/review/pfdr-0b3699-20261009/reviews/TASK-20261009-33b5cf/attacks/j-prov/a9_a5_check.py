"""J-PROV (2) A-5 and (3) A-9, EXP-PFDR-0b3699 RA-04 to RA-06. TASK-20261009-33b5cf.
PyYAML + standard library; no producer code imported (the pinned run_jobs.py is parsed
with ast only to read its INFERENCE literal).

(2) A-5: every RA-04..06 manifest (run root and attempt-1) carries run.task_id
    TASK-20261002-8a6b8a, run.protocol.handoff TASK-20261002-8a6b8a,
    run.protocol.output_archive TASK-20261002-33afa9, run.protocol.amendments [] and an
    inference block equal to the pinned launcher's INFERENCE literal; and
    execution-report-9456e8.yaml names the executing task, protocol version and output
    archive for the runs.
(3) A-9: parse execution-report-9456e8.yaml argv_list_A9. Writer model (from the pinned
    run_jobs.py source read for this task: init_root appends command.txt per invocation
    and writes environment.json once; log() appends stdout.log / stderr.log; step and
    census-jobs run run_wrapper.py exec into attempt-1/<step> or attempt-1/jobs/<job>;
    census-jobs gzips the job *.jsonl; merge writes rows.jsonl.gz, staircase.jsonl.gz,
    merge-report.json; finalize writes raw-result.json, manifest.yaml, checksums.sha256
    at attempt-1 and the run root). For every file in the three run roots: the logged
    invocation that wrote it, with evidence (command.txt line == logged argv after
    normalising the program token; execution.json command == the inner argv of the
    step; job execution windows inside the census window; output file named in the
    executed command; writer field of the data file; manifest reason / completeness /
    gate-report == the finalize argv). Timing: every logged window contains its
    execution.json [started, finished]; every stdout.log line time lies in a logged
    window of its run; each finalize window starts at or after its manifest
    timing.finished_at and ends before the next logged invocation starts.
No seeds. Usage: python a9_a5_check.py <repo> <out.json>
"""
import ast
import datetime as dt
import json
import os
import re
import shlex
import sys

import yaml

EXP = "experiments/EXP-PFDR-0b3699"
RUNS = f"{EXP}/runs"
RUNIDS = {"table": "RUN-PFDR-0b3699-table", "cal": "RUN-PFDR-0b3699-calibrate", "an": "RUN-PFDR-0b3699-analysis"}


def ts(s):
    s = str(s).replace("Z", "+00:00")
    return dt.datetime.fromisoformat(s).timestamp()


def norm(argv_tokens):
    """Drop the interpreter and the path prefix of run_jobs.py so a logged argv compares
    with a command.txt line ('run_jobs.py ...')."""
    t = list(argv_tokens)
    if t and t[0].endswith("python"):
        t = t[1:]
    if t and t[0].endswith("run_jobs.py"):
        t[0] = "run_jobs.py"
    return t


def main():
    repo, outp = sys.argv[1:3]
    R = lambda *p: os.path.join(repo, *p)  # noqa: E731
    out = {"A5": {}, "A9": {}}
    # launcher INFERENCE literal
    tree = ast.parse(open(R(EXP, "run_jobs.py")).read())
    infer = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "INFERENCE" for t in node.targets):
            infer = ast.literal_eval(node.value)
    for key, rid in RUNIDS.items():
        for loc in ("", "attempt-1"):
            m = yaml.safe_load(open(R(RUNS, rid, loc, "manifest.yaml")))["run"]
            out["A5"][f"{rid}/{loc or 'root'}"] = {
                "task_id": m["task_id"] == "TASK-20261002-8a6b8a",
                "protocol.handoff": m["protocol"]["handoff"] == "TASK-20261002-8a6b8a",
                "protocol.output_archive": m["protocol"]["output_archive"] == "TASK-20261002-33afa9",
                "protocol.amendments_empty": m["protocol"]["amendments"] == [],
                "inference_equals_launcher_literal": m["inference"] == infer}
    er = yaml.safe_load(open(R(EXP, "execution-report-9456e8.yaml")))["execution_report"]
    prov = er.get("per_run_provenance", {})
    out["A5"]["execution_report_per_run_provenance"] = {
        "executing_task": prov.get("executing_task"), "protocol_version": prov.get("protocol_version"),
        "output_archive": prov.get("output_archive"),
        "runs_listed": [r["run_id"] for r in er["runs"]],
        "per_run_entries_name_them_individually": all(
            any(k in r for k in ("executing_task", "protocol_version", "output_archive")) for r in er["runs"])}
    notes = yaml.safe_load(open(R(EXP, "implementation-notes.yaml")))["implementation_notes"]["continuation_9456e8"]
    txt = json.dumps(notes)
    out["A5"]["implementation_notes_continuation_names"] = {
        "executing_task": notes.get("task_id") == "TASK-20261008-9456e8",
        "protocol_version_2": str(notes.get("protocol_version", "")).startswith("2"),
        "output_archive_TASK-20261008-398fce": "TASK-20261008-398fce" in txt}

    # A-9
    argv = er["argv_list_A9"]
    wins = []
    for a in argv:
        toks = shlex.split(a["argv_verbatim_shell_quoted"])
        wins.append({"label": a["label"], "start": ts(a["utc_start"]), "end": ts(a["utc_end"]),
                     "exit": a.get("exit"), "tokens": toks, "run_id": toks[toks.index("--run-id") + 1]})
    out["A9"]["logged_invocations"] = [{"label": w["label"], "run_id": w["run_id"],
                                        "utc": [dt.datetime.utcfromtimestamp(w["start"]).isoformat(),
                                                dt.datetime.utcfromtimestamp(w["end"]).isoformat()]} for w in wins]
    files_report = {}
    problems = []
    for key, rid in RUNIDS.items():
        root = R(RUNS, rid)
        mw = [w for w in wins if w["run_id"] == rid]
        nonfin = [w for w in mw if "finalize" not in w["tokens"]]
        fin = [w for w in mw if "finalize" in w["tokens"]]
        # command.txt lines vs logged non-finalize argv
        lines = [l for l in open(os.path.join(root, "command.txt")).read().split("\n") if l]
        cmd_match = [shlex.split(l) == norm(w["tokens"]) for l, w in zip(lines, nonfin)]
        if len(lines) != len(nonfin) or not all(cmd_match):
            problems.append(f"{rid}: command.txt lines {len(lines)} vs logged non-finalize {len(nonfin)}; match {cmd_match}")
        m = yaml.safe_load(open(os.path.join(root, "manifest.yaml")))["run"]
        t0, t1 = ts(m["timing"]["started_at"]), ts(m["timing"]["finished_at"])
        # finalize vs manifest timing and next invocation
        fin_rep = []
        for w in fin:
            nxt = [x for x in wins if x["start"] > w["start"]]
            nstart = min(x["start"] for x in nxt) if nxt else None
            toks = w["tokens"]
            reason = toks[toks.index("--reason") + 1]
            comp = json.loads(toks[toks.index("--completeness") + 1])
            gr = [toks[i + 1] for i, x in enumerate(toks) if x == "--gate-report"]
            raw = json.load(open(os.path.join(root, "raw-result.json")))
            fin_rep.append({
                "label": w["label"],
                "starts_at_or_after_manifest_finished_at": w["start"] >= t1 - 1,
                "gap_seconds_after_finished_at": round(w["start"] - t1, 3),
                "ends_before_next_logged_invocation": nstart is None or w["end"] <= nstart,
                "manifest_validity_reason_equals_argv": m["validity"]["reason"] == reason,
                "manifest_completeness_equals_argv": m["completeness"] == comp,
                "raw_result_gates_equal_argv_gate_reports": sorted(raw["gates"]) == sorted(gr),
                "manifest_status_equals_argv": m["status"] == toks[toks.index("--status") + 1]})
        # executions inside windows
        exec_rep = []
        for d, _, fs in os.walk(os.path.join(root, "attempt-1")):
            if "execution.json" in fs:
                ex = json.load(open(os.path.join(d, "execution.json")))
                s, f = ts(ex["started_at"]), ts(ex["finished_at"])
                inside = [w["label"] for w in nonfin if w["start"] - 1 <= s and f <= w["end"] + 1]
                rel = os.path.relpath(d, root)
                inner_ok = None
                if not rel.startswith("attempt-1/jobs/"):
                    step = rel.split("/")[-1]
                    w = next((w for w in nonfin if "--step" in w["tokens"]
                              and w["tokens"][w["tokens"].index("--step") + 1] == step), None)
                    if w:
                        inner = w["tokens"][w["tokens"].index("--") + 1:]
                        inner_ok = ex["command"] == inner
                exec_rep.append({"dir": rel, "inside_window": inside, "inner_command_equals_logged": inner_ok})
                if not inside:
                    problems.append(f"{rid}: execution {rel} outside every logged window")
                if inner_ok is False:
                    problems.append(f"{rid}: execution {rel} command differs from the logged inner argv")
        # stdout.log line times
        bad_lines = []
        for fn in ("stdout.log", "stderr.log"):
            for line in open(os.path.join(root, fn)):
                mm = re.match(r"\[([^\]]+)\]", line)
                if mm:
                    tt = ts(mm.group(1))
                    if not any(w["start"] - 1 <= tt <= w["end"] + 1 for w in nonfin):
                        bad_lines.append(line.strip()[:120])
        # every file -> writer
        fmap = {}
        for d, _, fs in os.walk(root):
            for f in fs:
                rel = os.path.relpath(os.path.join(d, f), root)
                parts = rel.split("/")
                if rel in ("manifest.yaml", "raw-result.json", "checksums.sha256",
                           "attempt-1/manifest.yaml", "attempt-1/raw-result.json", "attempt-1/checksums.sha256"):
                    wr = "finalize: " + ",".join(w["label"] for w in fin)
                elif rel == "command.txt":
                    wr = "init_root of every logged non-finalize invocation: " + ",".join(w["label"] for w in nonfin)
                elif rel == "environment.json":
                    wr = "init_root of the first logged invocation: " + nonfin[0]["label"]
                elif rel in ("stdout.log", "stderr.log"):
                    wr = "log()/init_root of logged invocations: " + ",".join(w["label"] for w in nonfin)
                elif parts[0] == "attempt-1" and parts[1] == "jobs":
                    ex = json.load(open(os.path.join(root, "attempt-1", "jobs", parts[2], "execution.json")))
                    if f.endswith(".jsonl.gz"):
                        named = any(c.endswith(f"jobs/{parts[2]}/{f[:-3]}") for c in ex["command"])
                        wr = f"census CLI (job {parts[2]}) via run_wrapper.py exec under census-jobs, gzip -n by census-jobs; output named in executed command: {named}"
                        if not named:
                            problems.append(f"{rid}: {rel} not named in its job command")
                    else:
                        wr = f"run_wrapper.py exec of job {parts[2]} under census-jobs"
                elif parts[0] == "attempt-1":
                    wr = f"run_wrapper.py exec of step {parts[1]}"
                elif rel in ("rows.jsonl.gz", "staircase.jsonl.gz", "merge-report.json"):
                    wr = "run_jobs.py merge (inner argv of logged 'merge')"
                elif rel in ("row-verify.json", "checks-report.json"):
                    wj = json.load(open(os.path.join(root, rel)))
                    wr = f"analyze_a.py checks (inner argv of logged 'checks'); file writer/gate field: {wj.get('writer') or wj.get('gate')}"
                elif rel in ("calibration.json", "arm-read-log.json") or (rel == "view-map.json" and key == "cal"):
                    wj = json.load(open(os.path.join(root, rel)))
                    wr = f"analyze_a.py calibrate (inner argv of logged 'calibrate'); file writer/step field: {wj.get('writer') or wj.get('step') or wj.get('rule', '')[:40]}"
                elif rel in ("analysis.json", "cells.jsonl") or (rel == "view-map.json" and key == "an"):
                    wj = json.load(open(os.path.join(root, rel))) if rel.endswith(".json") else {}
                    wr = f"analyze_a.py unmask (inner argv of logged 'unmask'); file writer/step field: {wj.get('writer') or wj.get('step')}"
                else:
                    wr = None
                    problems.append(f"{rid}: {rel} has no writer in the model")
                fmap[rel] = wr
        files_report[rid] = {"files": len(fmap), "unassigned": [k for k, v in fmap.items() if v is None],
                             "command_txt_lines_match_logged": cmd_match, "finalize": fin_rep,
                             "executions": len(exec_rep),
                             "executions_outside_windows": [e for e in exec_rep if not e["inside_window"]],
                             "step_inner_commands_equal_logged": [e for e in exec_rep if e["inner_command_equals_logged"] is not None],
                             "log_lines_outside_windows": bad_lines,
                             "writer_of_every_non_job_file": {k: v for k, v in fmap.items() if not k.startswith("attempt-1/jobs/")},
                             "job_files": sum(1 for k in fmap if k.startswith("attempt-1/jobs/"))}
    out["A9"]["runs"] = files_report
    out["A9"]["problems"] = problems
    json.dump(out, open(outp, "w"), indent=1, default=str)
    print(json.dumps(out, indent=1, default=str)[:14000])


if __name__ == "__main__":
    main()
