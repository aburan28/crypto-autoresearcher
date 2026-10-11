#!/usr/bin/env python3
"""J1 (a), (b), (g): receipts, checksums, required artifacts, manifests, pins and views.

TASK-20261002-0114ff (validator), after the seal. Standard library plus PyYAML
for PARSING the YAML manifests and amendment only (declared deviation from
RV-3's 'standard library plus numpy'; no comparator logic is shared with any
producer script).
(a) every path_sha256 of the TASK-20261002-a3cee2 snapshot receipt re-hashed at
    the worktree; every file under the R12-R16 run directories that no receipt
    binds is listed; every checksums.sha256 under them verified (listed files
    hash-equal, no file of the location unlisted, no listed file absent).
(b) per location: spec required_artifacts (per_run + per_run_data) and the v6
    additions (E-4 finalize-inputs.json / finalize-extra.yaml, E-5 raw-result.json,
    E-6 null-tables.npz, E-7 view-map.json, E-9 gate reports); manifest fields of
    NA-16 (spec required_artifacts per_run text) and the v6 block (E-3, E-4).
(g) pin timeline (pins.helpers before R12; pins.calibration_json after R15 and
    before R16), helper bytes vs pins, view maps of R15 and R16 (same targets,
    identical files_sha256, equal to the archived bytes), O-C2 bracket.
"""
import glob
import hashlib
import json
import os
import sys

import yaml

WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-pfdr011cd0-5753edf2e"
EXP = "experiments/EXP-PFDR-011cd0"
RUNDIRS = {"R12": "RUN-PFDR-011cd0-table", "R13": "RUN-PFDR-011cd0-search", "R14": "RUN-PFDR-011cd0-srch-check",
           "R15": "RUN-PFDR-011cd0-calibrate", "R16": "RUN-PFDR-011cd0-analysis"}
ARCH = "coordination/design/TASK-20260928-102217/archives"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def files_under(d):
    out = []
    for root, _, fs in os.walk(d):
        for f in fs:
            out.append(os.path.relpath(os.path.join(root, f), WT))
    return sorted(out)


def main():
    rep = {}
    amd = yaml.safe_load(open(f"{WT}/{EXP}/amendments/AMD-20261002-236691.yaml"))["protocol_amendment"]
    block, task, notes = amd["manifest_protocol_block_v6"], amd["manifest_task_id_v6"], amd["manifest_writer_notes_v6"]
    # ---------------- (a) receipts
    rec = json.load(open(f"{WT}/{ARCH}/TASK-20261002-a3cee2/snapshot-receipt.json"))
    mism, absent = [], []
    for p, h in rec["path_sha256"].items():
        fp = os.path.join(WT, p)
        if not os.path.exists(fp):
            absent.append(p)
        elif sha(fp) != h:
            mism.append(p)
    bound = set(rec["path_sha256"])
    other_bound = set()
    for r in glob.glob(f"{WT}/{ARCH}/*/*receipt*.json"):
        try:
            other_bound |= set(json.load(open(r)).get("path_sha256", {}))
        except Exception:
            pass
    unbound = []
    run_files = []
    for rid, rd in RUNDIRS.items():
        for f in files_under(f"{WT}/{EXP}/runs/{rd}"):
            run_files.append(f)
            if f not in bound and f not in other_bound:
                unbound.append(f)
    a3_paths_in_runs = [p for p in bound if any(p.startswith(f"{EXP}/runs/{rd}/") for rd in RUNDIRS.values())]
    rep["a_receipt"] = {"receipt": f"{ARCH}/TASK-20261002-a3cee2/snapshot-receipt.json",
                        "paths_bound": len(bound), "rehash_mismatches": mism, "absent": absent,
                        "run_files_R12_R16": len(run_files), "a3cee2_paths_in_R12_R16": len(a3_paths_in_runs),
                        "unbound_run_files": unbound,
                        "pass": not mism and not absent and not unbound}
    # checksums
    cks = []
    for rid, rd in RUNDIRS.items():
        for cf in sorted(glob.glob(f"{WT}/{EXP}/runs/{rd}/**/checksums.sha256", recursive=True)):
            loc = os.path.dirname(cf)
            listed, bad, missing = {}, [], []
            for line in open(cf):
                if not line.strip():
                    continue
                h, p = line.rstrip("\n").split(None, 1)
                p = p.lstrip("*")
                listed[p] = h
                fp = os.path.join(loc, p)
                if not os.path.exists(fp):
                    missing.append(p)
                elif sha(fp) != h:
                    bad.append(p)
            present = [os.path.relpath(os.path.join(r_, f), loc) for r_, _, fs in os.walk(loc) for f in fs]
            unlisted = sorted(p for p in present if p not in listed and p != "checksums.sha256")
            cks.append({"file": os.path.relpath(cf, WT), "entries": len(listed), "mismatching": bad,
                        "listed_but_absent": missing, "unlisted_files": unlisted[:50], "unlisted_count": len(unlisted),
                        "lists_itself": "checksums.sha256" in listed,
                        "pass": not bad and not missing and not unlisted})
    rep["a_checksums"] = {"files": cks, "pass": all(c["pass"] for c in cks)}
    # ---------------- (b) artifacts and manifests
    per_run = ["manifest.yaml", "command.txt", "environment.json", "stdout.log", "stderr.log", "raw-result.json",
               "checksums.sha256"]
    data = {"R12": ["rows.jsonl.gz", "staircase.jsonl.gz", "merge-report.json", "row-verify.json"],
            "R13": ["rows.jsonl.gz", "staircase.jsonl.gz", "merge-report.json", "row-verify.json"],
            "R14": ["rows.jsonl.gz", "solve-certs.jsonl.gz", "solve-verify.json", "srch-report.json", "tab-report.json",
                    "curve-report.json", "grel-report.json"],
            "R15": ["calibration.json", "arm-read-log.json", "view-map.json", "null-tables.npz"],
            "R16": ["analysis.json", "cells.jsonl", "heuristics.json", "view-map.json"]}
    locs = []
    for rid, rd in RUNDIRS.items():
        base = f"{EXP}/runs/{rd}"
        if rid in ("R12", "R13", "R14"):
            locs.append((rid, base, "run_root", per_run + data[rid] + ["finalize-extra.yaml"]))
            att_req = per_run + ["jobs-spec.json", "jobs-index.json", "finalize-inputs.json", "jobs"]
            if rid == "R14":
                att_req += ["solve-certs.jsonl.gz", "solve-verify.json"]
            locs.append((rid, base + "/attempt-1", "attempt", att_req))
        else:
            locs.append((rid, base, "run_root", per_run + data[rid] + ["finalize-extra.yaml", "execution.json"]))
    mrep = []
    for rid, loc, kind, req in locs:
        missing = [f for f in req if not os.path.exists(f"{WT}/{loc}/{f}")]
        m = yaml.safe_load(open(f"{WT}/{loc}/manifest.yaml"))["run"]
        inf = m.get("inference", {})
        code = m.get("code", {})
        tm = m.get("timing", {})
        rs = m.get("resources", {})
        cert = (m.get("result") or {}).get("certificate") or {}
        inputs = m.get("inputs") or {}
        env = m.get("environment") or {}
        ck = {
            "run_id": m.get("id") == loc.split("/")[3],
            "experiment_id": m.get("experiment_id") == "EXP-PFDR-011cd0",
            "status_vocab": m.get("status") in ("completed_valid", "failed_infrastructure", "invalid"),
            "completeness": bool(m.get("completeness")),
            "code_commit": isinstance(code.get("commit"), str) and len(code.get("commit")) == 40,
            "code_dirty_bool": isinstance(code.get("dirty"), bool),
            "code_source_sha256": isinstance(code.get("source_sha256"), dict) and len(code.get("source_sha256")) > 0,
            "command": bool(code.get("command")) and bool(code.get("spec_command")),
            "environment": all(env.get(k) for k in ("python_version", "numpy_version", "operating_system", "cpu_model")),
            "inputs_seeds": bool(inputs.get("seeds")) or rid in ("R15", "R16"),
            "inputs_cells": bool(inputs.get("cells")) or rid in ("R15", "R16"),
            "inference_requested_policy": inf.get("requested_policy") == "executor-implementation",
            "inference_backend": bool(inf.get("backend")) and "bedrock" not in json.dumps(inf).lower().replace("bedrock never selected", ""),
            "inference_resolved_model_id_null": "resolved_model_id" in inf and inf.get("resolved_model_id") is None,
            "inference_provenance": inf.get("model_provenance") == "withheld by the session's artifact policy; not probe-verified",
            "inference_model_verified_false": inf.get("model_verified") is False,
            "inference_reasoning_effort": bool(inf.get("reasoning_effort")),
            "inference_fallback_used": isinstance(inf.get("fallback_used"), bool),
            "inference_degraded_requirements": isinstance(inf.get("degraded_requirements"), list),
            "timing_started_finished": bool(tm.get("started_at")) and bool(tm.get("finished_at")),
            "resources_rss_cpu_wall": any("rss" in k for k in rs) and any("cpu" in k for k in rs) and (any("wall" in k for k in rs) or tm.get("wall_seconds") is not None),
            "certificate_claimed_verified_NA16_literal": "instances_claimed" in cert and "instances_verified" in cert,
            "certificate_kind_declared": cert.get("kind") in ("none", "discrete_log"),
            "v6_protocol_block": m.get("protocol") == block,
            "v6_task_id": m.get("task_id") == task,
            "v6_executed_sources": isinstance(inputs.get("executed_sources"), dict) and len(inputs.get("executed_sources")) > 0,
            "v6_writer_notes": inputs.get("writer_notes") == notes,
            "location_kind": m.get("location_kind") == kind,
        }
        es = inputs.get("executed_sources") or {}
        es_bad = {p: h for p, h in es.items() if not os.path.exists(f"{WT}/{p}") or sha(f"{WT}/{p}") != h}
        es_missing_min = []
        if kind == "attempt":
            mins = [f"{EXP}/run_jobs.py", f"{EXP}/amd-236691/finalize_attempt_v6.py", "experiments/EXP-PFDR-1b78f7/amd-1de84f/run_wrapper.py"]
            mins += sorted(os.path.relpath(p, WT) for p in glob.glob(f"{WT}/src/crypto_autoresearcher/index_calculus/*.py"))
            if rid == "R14":
                mins.append(f"{EXP}/verify_solves.py")
            es_missing_min = [p for p in mins if p not in es]
            fi = json.load(open(f"{WT}/{loc}/finalize-inputs.json"))
            ck["finalize_inputs_exact_two_keys"] = sorted(fi) == ["executed_sources", "writer_notes"]
            ck["finalize_inputs_equal_manifest"] = fi.get("executed_sources") == es and fi.get("writer_notes") == inputs.get("writer_notes")
        ck["executed_sources_hash_equal_worktree"] = not es_bad
        ck["executed_sources_minimum_E4"] = not es_missing_min
        arts = m.get("artifacts")
        art_missing = [a for a in (arts or []) if not os.path.exists(f"{WT}/{loc}/{a}")]
        mrep.append({"run": rid, "location": loc, "kind": kind, "missing_required": missing, "checks": ck,
                     "failed_checks": [k for k, v in ck.items() if not v], "executed_sources_mismatch": es_bad,
                     "executed_sources_missing_minimum": es_missing_min, "status": m.get("status"),
                     "manifest_artifacts_absent": art_missing, "code_commit": code.get("commit"), "code_dirty": code.get("dirty"),
                     "certificate": cert})
    rep["b_manifests"] = {"locations": mrep, "pass": all(not x["missing_required"] and not x["failed_checks"] and not x["manifest_artifacts_absent"] for x in mrep)}
    # ---------------- (g) pins, views
    notes_doc = list(yaml.safe_load_all(open(f"{WT}/{EXP}/implementation-notes-236691.yaml")))
    nd = {}
    for d in notes_doc:
        if isinstance(d, dict):
            nd.update(d)
    ph = nd.get("pin_helpers", {})
    helpers = (ph.get("pins") or {}).get("helpers") or {}
    hbytes = {p: (sha(f"{WT}/{p}") == h) for p, h in (helpers.get("sha256") or {}).items()}
    pin_cal = nd.get("pin_calibration_json") or {}
    vm15 = json.load(open(f"{WT}/{EXP}/runs/RUN-PFDR-011cd0-calibrate/view-map.json"))
    vm16 = json.load(open(f"{WT}/{EXP}/runs/RUN-PFDR-011cd0-analysis/view-map.json"))
    t15 = {e["target"]: e["files_sha256"] for e in vm15["entries"]}
    t16 = {e["target"]: e["files_sha256"] for e in vm16["entries"]}
    vm_arch = {}
    for tgt, fs in t16.items():
        bad = [f for f, h in fs.items() if not os.path.exists(f"{WT}/{tgt}/{f}") or sha(f"{WT}/{tgt}/{f}") != h]
        under = [os.path.relpath(p, f"{WT}/{tgt}") for p in files_under(f"{WT}/{tgt}")]
        notin = [os.path.relpath(f"{WT}/{p}", f"{WT}/{tgt}") for p in under if os.path.relpath(f"{WT}/{p}", f"{WT}/{tgt}") not in fs]
        vm_arch[tgt] = {"files": len(fs), "mismatch_vs_archive": bad, "archive_files_not_in_view_map": notin[:20],
                        "archive_files_not_in_view_map_count": len(notin)}
    cal = json.load(open(f"{WT}/{EXP}/runs/RUN-PFDR-011cd0-calibrate/calibration.json"))
    an = json.load(open(f"{WT}/{EXP}/runs/RUN-PFDR-011cd0-analysis/analysis.json"))
    m15 = yaml.safe_load(open(f"{WT}/{EXP}/runs/RUN-PFDR-011cd0-calibrate/manifest.yaml"))["run"]
    m16 = yaml.safe_load(open(f"{WT}/{EXP}/runs/RUN-PFDR-011cd0-analysis/manifest.yaml"))["run"]
    m12a = yaml.safe_load(open(f"{WT}/{EXP}/runs/RUN-PFDR-011cd0-table/attempt-1/manifest.yaml"))["run"]
    rep["g_pins_views"] = {
        "pins_helpers_appended_at": ph.get("appended_at"), "pins_helpers": helpers,
        "helper_bytes_equal_pins": hbytes,
        "R12_attempt1_started_at": m12a["timing"]["started_at"],
        "pins_calibration_json": pin_cal,
        "calibration_json_sha256_archive": sha(f"{WT}/{EXP}/runs/RUN-PFDR-011cd0-calibrate/calibration.json"),
        "R16_analysis_calibration_sha256": an["calibration"]["sha256"],
        "R15_timing": m15["timing"], "R16_timing": m16["timing"],
        "view_maps_same_targets": sorted(t15) == sorted(t16),
        "view_maps_identical_files_sha256": t15 == t16,
        "view_map_targets": sorted(t16),
        "view_map_vs_archive": vm_arch,
        "design_json_sha256_archive": sha(f"{WT}/{EXP}/runs/RUN-PFDR-011cd0-p0-design/attempt-3/design.json"),
        "design_json_sha256_in_calibration_json": cal.get("design_sha256"),
        "design_json_sha256_in_a3cee2_receipt": rec["path_sha256"].get(f"{EXP}/runs/RUN-PFDR-011cd0-p0-design/attempt-3/design.json"),
        "design_json_sha256_in_7505b5_receipt": json.load(open(f"{WT}/{ARCH}/TASK-20261002-7505b5/snapshot-receipt.json"))["path_sha256"].get(f"{EXP}/runs/RUN-PFDR-011cd0-p0-design/attempt-3/design.json"),
        "design_pin": "eb7e907d57b3486f5ceda4684498f6671e168df7925424c7522e13f0514ede0e",
    }
    json.dump(rep, open(sys.argv[1], "w"), indent=1, sort_keys=True, default=str)
    print(json.dumps({"a_receipt": {k: v for k, v in rep["a_receipt"].items() if k != "unbound_run_files"},
                      "unbound_n": len(rep["a_receipt"]["unbound_run_files"]),
                      "a_checksums_pass": rep["a_checksums"]["pass"],
                      "checksum_failures": [c for c in cks if not c["pass"]][:5],
                      "b_pass": rep["b_manifests"]["pass"],
                      "b_fail": [{k: x[k] for k in ("location", "missing_required", "failed_checks", "manifest_artifacts_absent", "executed_sources_missing_minimum")} for x in mrep if x["missing_required"] or x["failed_checks"] or x["manifest_artifacts_absent"]]},
                     indent=1, default=str)[:6000])


if __name__ == "__main__":
    main()
