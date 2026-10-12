"""J-PROV (1): the six DEF-1 superseding records of EXP-PFDR-0b3699. TASK-20261009-33b5cf.
PyYAML + standard library; no producer code; nothing is written outside the out path.

For each run R (tests, repro, p0-design by PROC-DEF1 / TASK-20261009-70f831; table,
calibrate, analysis by PROC-DEF1-C / TASK-20261009-57637b), with ORIG = run-root
manifest.yaml, CMD = run-root command.txt, V2 = supersessions/R/manifest_v2.yaml:
  (a) STRIP: locate the first "\\n  code:\\n" in V2; the INSERT that follows must be
      "    command: |-\\n" + one "      " + L + "\\n" per line L of CMD; the bytes after
      it up to the start of the trailing "supersession:\\n" block, together with the
      prefix, must equal ORIG byte for byte; nothing else may differ.
  (b) REBUILD: construct V2 independently from ORIG, CMD and the append template of
      DEC-20261009-ff58fe def1_repair (with the PROC-DEF1-C changes for the
      continuation runs) and compare bytes with V2.
  (c) YAML: top-level keys {run, supersession}; run.code.command == CMD minus its
      final newline; V2.run without code.command deep-equals ORIG.run.
  (d) hashes: ORIG and CMD vs the def1_repair runs_now / 57637b card values and the
      5ea531 / 398fce receipt path_sha256; V2 vs the registry superseding_sha256 and
      the 70f831 / 57637b receipt path_sha256; registry superseded_sha256 vs ORIG.
  (e) the supersession block's path, hash, command_source, archived_by, task and (for
      table, calibrate, analysis) the four continuation lines.
  (f) ORIG preconditions of the construction: ends with "\\n", one "\\n  code:\\n";
      CMD ends with "\\n", no tab, no empty line, no leading whitespace, printable ASCII.
No seeds. Usage: python prov_check.py <repo> <out.json>
"""
import hashlib
import json
import os
import sys

import yaml

EXP = "experiments/EXP-PFDR-0b3699"
ARCH = "coordination/design/TASK-20260928-102217/archives"
FIRST = ["RUN-PFDR-0b3699-tests", "RUN-PFDR-0b3699-repro", "RUN-PFDR-0b3699-p0-design"]
CONT = ["RUN-PFDR-0b3699-table", "RUN-PFDR-0b3699-calibrate", "RUN-PFDR-0b3699-analysis"]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def append_text(rid, orig_sha, cmd_sha, cont):
    o = f"{EXP}/runs/{rid}/manifest.yaml"
    c = f"{EXP}/runs/{rid}/command.txt"
    lines = ["supersession:",
             "  record: run_manifest_supersession",
             f"  supersedes_path: {o}",
             f"  supersedes_sha256: {orig_sha}",
             "  adds: [run.code.command]",
             f"  command_source: {c} (verbatim; sha256 {cmd_sha})",
             "  command_not_logged: run_jobs.py finalize invocations are not in command.txt (DEF-1 provenance gap; DEC-20261008-8cb005 FP-7)"]
    if cont:
        lines += ["  archived_by: TASK-20261008-398fce (run.protocol.output_archive and run.task_id are the pinned launcher's constants, AMD-20261008-9c080d A-5)",
                  "  executing_task: TASK-20261008-9456e8",
                  "  protocol_version: 2",
                  "  protocol_amendment: AMD-20261008-9c080d",
                  "  finalize_argv_source: experiments/EXP-PFDR-0b3699/execution-report-9456e8.yaml (AMD-20261008-9c080d A-9)",
                  "  decision: DEC-20261009-ff58fe",
                  "  task: TASK-20261009-57637b"]
    else:
        lines += ["  archived_by: TASK-20261008-5ea531 (run.protocol.output_archive names TASK-20261002-33afa9, which DEC-20261008-8cb005 superseded)",
                  "  decision: DEC-20261009-ff58fe",
                  "  task: TASK-20261009-70f831"]
    lines += ["  nothing_else_changed: true"]
    return "".join(l + "\n" for l in lines).encode()


def main():
    repo, outp = sys.argv[1:3]
    R = lambda *p: os.path.join(repo, *p)  # noqa: E731
    reg = yaml.safe_load(open(R("tools/run_supersession_registry.yaml")))
    recs = reg["records"] if isinstance(reg, dict) and "records" in reg else reg
    regmap = {r["run_id"]: r for r in recs if str(r.get("run_id", "")).startswith("RUN-PFDR-0b3699")}
    rc = {t: json.load(open(R(ARCH, t, "snapshot-receipt.json")))["path_sha256"] for t in
          ("TASK-20261008-5ea531", "TASK-20261008-398fce", "TASK-20261009-70f831", "TASK-20261009-57637b")}
    dec = yaml.safe_load(open(R("ledger/decisions/DEC-20261009-ff58fe.yaml")))["coordinator_decision"]["def1_repair"]
    runs_now = {r["run_id"]: r for r in dec["runs_now"]}
    card57 = {r["run_id"]: r for r in yaml.safe_load(open(R("ledger/handoffs/TASK-20261009-57637b.yaml")))["handoff"]["runs"]}
    out = {"registry_records_for_experiment": sorted(regmap), "runs": {}}
    for rid in FIRST + CONT:
        cont = rid in CONT
        op, cp, vp = f"{EXP}/runs/{rid}/manifest.yaml", f"{EXP}/runs/{rid}/command.txt", f"{EXP}/supersessions/{rid}/manifest_v2.yaml"
        O, C, V = open(R(op), "rb").read(), open(R(cp), "rb").read(), open(R(vp), "rb").read()
        res = {}
        # (f)
        Ct = C.decode("ascii", errors="strict")
        res["preconditions"] = {
            "orig_ends_newline": O.endswith(b"\n"), "orig_code_marker_once": O.count(b"\n  code:\n") == 1,
            "cmd_ends_newline": C.endswith(b"\n"), "cmd_no_tab": b"\t" not in C,
            "cmd_no_empty_line": all(l for l in Ct[:-1].split("\n")),
            "cmd_no_leading_ws": all(not l[:1].isspace() for l in Ct[:-1].split("\n")),
            "cmd_printable_ascii": all(32 <= ch < 127 for ch in C if ch != 10)}
        # (a) strip
        i = V.find(b"\n  code:\n")
        insert = b"    command: |-\n" + b"".join(b"      " + l.encode() + b"\n" for l in Ct[:-1].split("\n"))
        j = i + len(b"\n  code:\n")
        ok_insert = V[j:j + len(insert)] == insert
        k = V.rfind(b"\nsupersession:\n")
        stripped = V[:j] + V[j + len(insert):k + 1] if ok_insert and k > 0 else None
        res["strip"] = {"insert_found_after_first_code_marker": ok_insert,
                        "trailing_block_found": k > 0,
                        "stripped_equals_orig_bytes": stripped == O,
                        "appended_bytes": len(V) - (k + 1) if k > 0 else None}
        # (b) rebuild
        oi = O.find(b"\n  code:\n") + len(b"\n  code:\n")
        built = O[:oi] + insert + O[oi:] + append_text(rid, sha(O), sha(C), cont)
        res["rebuild_equals_v2_bytes"] = built == V
        if built != V:
            res["rebuild_first_diff_at"] = next((n for n in range(min(len(built), len(V))) if built[n] != V[n]), min(len(built), len(V)))
        # (c) yaml
        y2, y0 = yaml.safe_load(V), yaml.safe_load(O)
        cmdv = y2["run"]["code"].get("command")
        r2 = json.loads(json.dumps(y2["run"], default=str))
        r2["code"].pop("command", None)
        res["yaml"] = {"top_keys": sorted(y2.keys()), "run_id": y2["run"]["id"] == rid,
                       "command_equals_cmd": cmdv == Ct[:-1],
                       "run_minus_command_deep_equals_orig": r2 == json.loads(json.dumps(y0["run"], default=str))}
        # (d) hashes
        exp_src = runs_now.get(rid) if not cont else card57.get(rid)
        rk = "TASK-20261008-398fce" if cont else "TASK-20261008-5ea531"
        vk = "TASK-20261009-57637b" if cont else "TASK-20261009-70f831"
        reg_r = regmap.get(rid, {})
        res["hashes"] = {
            "orig_sha256": sha(O), "cmd_sha256": sha(C), "v2_sha256": sha(V),
            "orig_eq_ruling_value": exp_src and exp_src["orig_sha256"] == sha(O),
            "cmd_eq_ruling_value": exp_src and exp_src["cmd_sha256"] == sha(C),
            "orig_eq_receipt_" + rk: rc[rk].get(op) == sha(O),
            "cmd_eq_receipt_" + rk: rc[rk].get(cp) == sha(C),
            "v2_eq_receipt_" + vk: rc[vk].get(vp) == sha(V),
            "registry_superseded_path_ok": reg_r.get("superseded_path") == op,
            "registry_superseded_sha256_eq_orig": reg_r.get("superseded_sha256") == sha(O),
            "registry_superseding_path_ok": reg_r.get("superseding_path") == vp,
            "registry_superseding_sha256_eq_v2": reg_r.get("superseding_sha256") == sha(V),
            "registry_decision_id": reg_r.get("decision_id"),
            "registry_notes_name_task": (vk in str(reg_r.get("notes", ""))),
            "registry_kind": reg_r.get("supersession_kind")}
        # (e) block
        blk = y2["supersession"]
        res["block"] = {
            "supersedes_path_ok": blk.get("supersedes_path") == op,
            "supersedes_sha256_ok": blk.get("supersedes_sha256") == sha(O),
            "command_source_ok": blk.get("command_source") == f"{cp} (verbatim; sha256 {sha(C)})",
            "task": blk.get("task"), "task_ok": blk.get("task") == vk,
            "archived_by": blk.get("archived_by"),
            "continuation_lines_ok": (blk.get("executing_task") == "TASK-20261008-9456e8" and blk.get("protocol_version") == 2
                                      and blk.get("protocol_amendment") == "AMD-20261008-9c080d"
                                      and str(blk.get("finalize_argv_source", "")).startswith(f"{EXP}/execution-report-9456e8.yaml"))
            if cont else ("executing_task" not in blk),
            "keys": list(blk.keys())}
        out["runs"][rid] = res
    flat_fail = []
    for rid, res in out["runs"].items():
        def walk(x, p):
            if isinstance(x, dict):
                for kk, vv in x.items():
                    walk(vv, p + "." + kk)
            elif x is False:
                flat_fail.append(p)
        walk(res, rid)
    out["failed_checks"] = flat_fail
    json.dump(out, open(outp, "w"), indent=1, default=str)
    print(json.dumps(out, indent=1, default=str)[:6000])
    print("FAILED CHECKS:", flat_fail)


if __name__ == "__main__":
    main()
