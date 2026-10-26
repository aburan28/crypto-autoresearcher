#!/usr/bin/env python3
"""Export retained rows/identities only; this program never runs mathematics."""
import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--protocol", type=Path, default=HERE/"protocol.json")
    parser.add_argument("--analysis", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    out = args.out.resolve()
    if out.parent != HERE:
        raise SystemExit("Export belongs beside its protocol; use a fresh filename in this track")
    if out.exists():
        raise SystemExit("Refusing to overwrite a previous export")
    run = args.run.resolve()
    analysis = args.analysis.resolve() if args.analysis else HERE/"reports"/run.name
    receipt = json.loads((run/"execution.json").read_text())
    if not analysis.is_dir():
        raise SystemExit("Run frozen analysis first and pass its fresh output directory")
    sys.path.insert(0, str(REPO))
    from tools import experiment_protocol as ep
    protocol = ep.read_json(args.protocol)
    issues = ep.schema_errors(protocol, "experiment.protocol/v1") or ep.lint_protocol(protocol, args.protocol.parent)
    if issues or protocol["freeze"]["status"] != "frozen":
        raise SystemExit("Protocol is not frozen/valid: "+str(issues))
    rel = lambda path: str(Path(path).resolve().relative_to(HERE))
    export = ep.from_rows(run/"rows.jsonl", protocol, rel(args.protocol), "PASS2-F6-"+run.name, {}, files_prefix=rel(run))
    observed = receipt["source"]
    export["producer"] = {"runtime": "native_codex", "model": None,
                          "session": receipt["task"]+"/"+run.name, "role": "executor"}
    export["source"] = {"repo": protocol["repository"], "commit": observed["head"], "dirty": observed["dirty"]}
    for arm in export["arms"]:
        arm["commit"] = observed["instrument_commit"]
        arm["binary_sha256"] = observed["binary_sha256"]
    export["host"] = {
        "path": rel(run/"execution.json"), "sha256": ep.sha256_file(run/"execution.json"),
        "class_id": receipt["host"]["host"],
        "summary": {"cpu_model": receipt["host"]["cpu_model"],
                    "logical_cpus": receipt["host"]["logical_cpus"], "memory_bytes": None,
                    "kernel": receipt["host"]["kernel"], "hypervisor": None,
                    "isolation_tier_max": "L0"}}
    native_rows = {row["arm"]: row for row in [json.loads(line) for line in (run/"rows.jsonl").read_text().splitlines() if line.strip()]}
    for row in export["runs"]:
        row["started_at"], row["finished_at"] = receipt["started_at"], receipt["finished_at"]
        row["worker"] = receipt["host"]["host"]
        row["measurements"]["wall_valid"] = False
        # Shared process resource diagnostics are retained once in execution.json,
        # not misrepresented as two independent per-arm clocks.
        row["measurements"]["counters"] = native_rows[row["arm"]].get("native_counters", {})
        row["isolation"]["contended"] = None
        row["isolation"]["blockers"] = ["shared managed host; no clock metric"]
        row["verification"]["verifier"] = "retained exact matrix/point and separate-implementation checks; same producer session"
        if row["status"] == "failed":
            row["exclusion"] = {"excluded": True, "rule": "protocol: failed certificate or execution is not a mathematical null"}
        row["artifacts"] = [ep.file_entry(HERE, rel(run/name), "raw") for name in ("execution.json", "case-index.json")]
    export["files"] = [ep.file_entry(HERE, rel(path), "log" if path.suffix == ".txt" else "raw")
                       for path in sorted(run.rglob("*")) if path.is_file()]
    export["analysis"]["script"] = {"path": "analysis.py", "sha256": ep.sha256_file(HERE/"analysis.py"),
                                      "bytes": (HERE/"analysis.py").stat().st_size}
    export["analysis"]["outputs"] = [ep.file_entry(HERE, rel(path), "analysis")
                                     for path in sorted(analysis.rglob("*")) if path.is_file()]
    export["notes"] = [
        {"kind": "observation", "by": receipt["task"],
         "text": "Two actual implementation/checker stages of one frozen panel; shared setup and process resources are not independent timing trials."},
        {"kind": "observation", "by": receipt["task"],
         "text": "Producer model inherited and unprobed; native checker is a separate implementation in the same session, not canonical independent review."},
        {"kind": "observation", "by": receipt["task"],
         "text": "Whole-session native counters and diagnostic rusage are retained in execution.json; field-operation pricing and complete ECDLP cost are unmeasured."}]
    export["flow"] = ep.compute_flow(export["runs"])
    issues = ep.schema_errors(export, "experiment.export/v1") or ep.lint_export(export, protocol, HERE, True)
    if issues:
        rejected = out.with_name(out.stem+"-rejected.json")
        ep.write_once(rejected, export)
        raise SystemExit("Export refused; candidate retained at "+str(rejected)+": "+str(issues))
    ep.write_once(out, export)
    print(ep.render_flow(export))


if __name__ == "__main__":
    main()
