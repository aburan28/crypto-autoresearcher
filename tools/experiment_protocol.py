#!/usr/bin/env python3
"""Experiment protocol, export and review: the one shape every runner uses.

`docs/experiment-protocol.md` states the rules. This tool checks them without
judgment, so a protocol that passes `validate` leaves the executor no choice
to make and leaves the reviewer every number to recompute.

    python3 tools/experiment_protocol.py validate <protocol|export|review>.json
    python3 tools/experiment_protocol.py hash <protocol.json>
    python3 tools/experiment_protocol.py freeze <protocol.json> [--commit SHA|auto] [--filed-before-affected-data]
    python3 tools/experiment_protocol.py seeds <protocol.json> [--arm A --instance I --replicate R | --all]
    python3 tools/experiment_protocol.py power --n N --alpha 0.05 --m 3
    python3 tools/experiment_protocol.py blind <export.json> --out blinded.json [--nonce HEX]
    python3 tools/experiment_protocol.py flow <export.json>
    python3 tools/experiment_protocol.py check-export <export.json> --protocol <protocol.json> [--verify-files]
    python3 tools/experiment_protocol.py review new <export.json> --out-dir DIR --role validator [--runtime R --model M --session S]
    python3 tools/experiment_protocol.py review validate <review.json>
    python3 tools/experiment_protocol.py from-taskq <result.json> --protocol P --arm ARM --instance I --out export.json
    python3 tools/experiment_protocol.py from-ecbench <session_dir> --protocol P --out export.json
    python3 tools/experiment_protocol.py from-rows <rows.jsonl|rows.csv> --protocol P --out export.json [--map key=column ...]

Schemas: `schemas/experiment-protocol.v1.json`, `schemas/experiment-export.v1.json`,
`schemas/experiment-review.v1.json`. Exit status: 0 clean, 1 findings, 2 the
input could not be read or a write was refused (an existing review, a frozen
protocol). The tool never edits an export or a review that exists: both are
write-once, and a correction is a new record that names the old one.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import secrets
import subprocess
import sys
import time
from pathlib import Path, PurePosixPath
from typing import Any

import jsonschema

REPO = Path(__file__).resolve().parents[1]
SCHEMAS = {
    "experiment.protocol/v1": REPO / "schemas/experiment-protocol.v1.json",
    "experiment.export/v1": REPO / "schemas/experiment-export.v1.json",
    "experiment.review/v1": REPO / "schemas/experiment-review.v1.json",
}
SEED_DOMAIN = b"experiment.protocol/v1 seed\n"
BLIND_DOMAIN = b"experiment.export/v1 blind\n"
DECISIVE_DESIGNS = {"one_factor", "factorial", "absolute"}
COMPLETED = {"succeeded", "failed"}
NOT_COMPLETED = {"timeout", "cancelled", "infra_error", "interrupted"}
ISOLATION_RANK = {"none": -1, "L0": 0, "L1": 1, "L2": 2, "L3": 3,
                  "tierD": 0, "tierC": 1, "tierB": 2, "tierA": 3}
REQUIRED_REVIEW_CHECKS = ("hashes", "protocol_adherence", "controls", "recompute", "scope")
ECBENCH_ROLES = {"reference": "reference", "baseline": "baseline", "candidate": "candidate", "control": "control_aa"}


class Refused(Exception):
    """The input cannot be read, or the write would overwrite a record."""


# ---------------------------------------------------------------------------
# Primitives
# ---------------------------------------------------------------------------

def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> Any:
    def pairs(items):
        out = {}
        for k, v in items:
            if k in out:
                raise ValueError(f"duplicate key {k!r} in {path}")
            out[k] = v
        return out
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs,
                          parse_constant=lambda v: (_ for _ in ()).throw(ValueError(f"non-finite number {v} in {path}")))
    except (OSError, ValueError) as exc:
        raise Refused(f"cannot read {path}: {exc}") from exc


def write_once(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError as exc:
        raise Refused(f"{path} exists; records are write-once (file a new one that names it)") from exc
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(json.dumps(obj, indent=2, sort_keys=False, ensure_ascii=False) + "\n")


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def git_head(repo: Path) -> str | None:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def protocol_hash(protocol: dict[str, Any]) -> str:
    """sha256 of the canonical JSON without the freeze block."""
    body = {k: v for k, v in protocol.items() if k != "freeze"}
    return sha256_bytes(canonical(body))


def schema_errors(obj: Any, schema_id: str) -> list[str]:
    schema = read_json(SCHEMAS[schema_id])
    validator = jsonschema.Draft202012Validator(schema)
    out = []
    for err in sorted(validator.iter_errors(obj), key=lambda e: list(e.absolute_path)):
        where = "/".join(str(p) for p in err.absolute_path) or "<root>"
        out.append(f"schema: {where}: {err.message}")
    return out


def detect_kind(obj: Any) -> str:
    if not isinstance(obj, dict) or obj.get("schema") not in SCHEMAS:
        raise Refused("document has no recognised 'schema' field "
                      "(experiment.protocol/v1 | experiment.export/v1 | experiment.review/v1)")
    return obj["schema"]


# ---------------------------------------------------------------------------
# Protocol
# ---------------------------------------------------------------------------

def power_check(n: int | None, alpha: float, m: int) -> dict[str, Any]:
    """An empirical rank test cannot reject below its resolution: the smallest
    attainable two-sided p with the add-one estimate is 2/(N+1), which must
    be below alpha/m for m corrected tests."""
    if n is None:
        return {"rank_test_n": None, "min_attainable_two_sided_p": None, "threshold": alpha / m, "passes": False,
                "reason": "rank_test_n is null"}
    min_p = 2.0 / (n + 1)
    return {"rank_test_n": n, "min_attainable_two_sided_p": min_p, "threshold": alpha / m,
            "passes": min_p < alpha / m, "n_needed": int(2 * m / alpha) + 1}


def lint_protocol(p: dict[str, Any], base: Path | None = None) -> list[str]:
    f: list[str] = []
    arms = {a["id"]: a for a in p.get("arms", [])}
    roles = {a["id"]: a["role"] for a in p.get("arms", [])}
    ledger = p.get("variable_ledger", {})
    comps = {c["id"]: c for c in ledger.get("comparisons", [])}
    names = {x["name"] for x in ledger.get("factors", [])} | {x["name"] for x in ledger.get("independent", [])}
    metrics = {m["id"]: m for m in p.get("metrics", {}).get("primary", []) + p.get("metrics", {}).get("secondary", [])}

    for cid, c in comps.items():
        for a in c["arms"]:
            if a not in arms:
                f.append(f"comparison {cid} names unknown arm {a!r}")
        for d in c["differs_in"]:
            if d not in names:
                f.append(f"comparison {cid} differs_in {d!r} is not a factor or independent variable in the ledger")
        if c["design"] == "one_factor" and len(c["differs_in"]) != 1:
            f.append(f"comparison {cid} is one_factor but differs in {len(c['differs_in'])} factors")
        if c["design"] == "aa" and len(c["arms"]) < 2:
            f.append(f"comparison {cid} is aa and needs two arms that differ only in a nuisance factor")
        if c["design"] == "confounded" and not (c.get("reason") or "").strip():
            f.append(f"comparison {cid} is confounded and needs 'reason'")
        if c["design"] == "absolute" and not (c.get("threshold") or "").strip():
            f.append(f"comparison {cid} is absolute and needs 'threshold'")

    aa = p["controls"]["aa"]
    has_aa = any(c["design"] == "aa" for c in comps.values())
    if aa["present"]:
        if aa["comparison"] not in comps or comps[aa["comparison"]]["design"] != "aa":
            f.append("controls.aa.comparison must name a ledger comparison with design aa")
    elif not has_aa and not (aa.get("not_applicable_reason") or "").strip():
        f.append("no A/A comparison and no controls.aa.not_applicable_reason: every protocol states its noise floor or why none exists")
    pos = p["controls"]["positive"]
    if pos["present"]:
        if roles.get(pos["arm"]) != "control_positive":
            f.append("controls.positive.arm must be an arm with role control_positive")
        if not (pos.get("expected_detection") or "").strip():
            f.append("controls.positive.expected_detection is required when a positive control is present")
    elif not (pos.get("not_applicable_reason") or "").strip():
        f.append("no positive control and no controls.positive.not_applicable_reason: a 'nothing found' is evidence only when the detector demonstrably finds the thing")
    neg = p["controls"]["negative"]
    if neg["present"]:
        if roles.get(neg["arm"]) != "control_negative":
            f.append("controls.negative.arm must be an arm with role control_negative")
        if neg.get("null_population") is None:
            f.append("controls.negative.null_population is required when a negative control is present")
    elif not (neg.get("not_applicable_reason") or "").strip():
        f.append("no negative control and no controls.negative.not_applicable_reason")

    for c in p["claims"]:
        if c["class"] == "comparative":
            if not c["decided_by"]:
                f.append(f"claim {c['id']} is comparative and names no deciding comparison")
            for cid in c["decided_by"]:
                if cid not in comps:
                    f.append(f"claim {c['id']} is decided by unknown comparison {cid!r}")
                elif comps[cid]["design"] not in DECISIVE_DESIGNS:
                    f.append(f"claim {c['id']} is decided by {cid}, whose design {comps[cid]['design']} decides nothing "
                             "(only one_factor, factorial and absolute comparisons carry a criterion)")
        elif c["decided_by"]:
            for cid in c["decided_by"]:
                if cid not in comps:
                    f.append(f"claim {c['id']} is decided by unknown comparison {cid!r}")

    for h in p.get("hypotheses", []):
        for pr in h["predictions"]:
            if pr["metric"] not in metrics:
                f.append(f"prediction {pr['id']} names unknown metric {pr['metric']!r}")
            role = pr.get("role", "decisive")
            if pr["provenance"]["sample_status"] == "in_sample" and role != "calibration":
                f.append(f"prediction {pr['id']} is in_sample but role {role}: an in-sample prediction may calibrate the "
                         "instrument but may not carry a criterion (set role: calibration, or name out-of-sample cells)")
            if pr["provenance"]["sample_status"] == "partially_in_sample" and role == "decisive" \
                    and not (pr["provenance"].get("decisive_scope") or "").strip():
                f.append(f"prediction {pr['id']} is partially in sample: name decisive_scope (the cells no data was seen for)")

    for cid in p["decision_rule"]["comparison_ids"]:
        if cid not in comps:
            f.append(f"decision_rule cites unknown comparison {cid!r}")
        elif comps[cid]["design"] not in DECISIVE_DESIGNS:
            f.append(f"decision_rule cites {cid}, whose design {comps[cid]['design']} decides nothing")
    if p["decision_rule"]["multiple_comparison_correction"] == "none" and p["sample_size"]["power"]["tests_in_family"] > 1:
        f.append("decision_rule applies no multiple-comparison correction to a family of more than one test")

    rz = p["randomization"]
    if rz["arm_order"] == "fixed" and not (rz.get("arm_order_reason") or "").strip():
        f.append("randomization.arm_order is fixed without arm_order_reason (one-time costs land on whichever arm runs first)")
    sd = rz["seed_derivation"]
    if sd["method"] == "explicit_list" and not sd.get("seeds"):
        f.append("seed_derivation.method explicit_list needs a non-empty 'seeds' list")
    if sd["method"] == "harness_drawn" and not (sd.get("note") or "").strip():
        f.append("seed_derivation.method harness_drawn: 'note' must name the backend's seed rule and the spec seed it starts from")
    if sd["method"] == "external_nonce" and not sd.get("nonce") and p["freeze"]["status"] == "frozen":
        f.append("seed_derivation.method external_nonce: record the nonce once drawn (after the freeze)")

    pw = p["sample_size"]["power"]
    if pw["method"] == "rank_test":
        computed = power_check(pw.get("rank_test_n"), pw["alpha"], pw["tests_in_family"])
        if pw["passes"] != computed["passes"]:
            f.append(f"sample_size.power.passes is {pw['passes']} but 2/(N+1)={computed['min_attainable_two_sided_p']} "
                     f"against alpha/m={computed['threshold']} gives {computed['passes']} (N needed >= {computed.get('n_needed')})")
        if pw.get("min_attainable_two_sided_p") is not None and computed["min_attainable_two_sided_p"] is not None \
                and abs(pw["min_attainable_two_sided_p"] - computed["min_attainable_two_sided_p"]) > 1e-12:
            f.append("sample_size.power.min_attainable_two_sided_p does not equal 2/(N+1)")
    pf = p["sample_size"]["preflight_runtime"]
    if pf["estimated_total_seconds"] is None and p["freeze"]["status"] == "frozen":
        f.append("preflight_runtime.estimated_total_seconds is null on a frozen protocol: time one call per arm first")

    timed_primary = [m["id"] for m in p["metrics"]["primary"] if m["kind"] == "timed"]
    iso = p["measurement"]["isolation_required"]
    if timed_primary:
        if not (p["measurement"].get("timed_primary_justification") or "").strip():
            f.append(f"primary metric(s) {timed_primary} are timed without measurement.timed_primary_justification")
        if ISOLATION_RANK[iso] < 2:
            f.append(f"primary metric(s) {timed_primary} are timed but isolation_required is {iso}; a clock is evidence at L2/tierB or better")
    for m in metrics.values():
        if m["kind"] == "derived" and not (m.get("formula") or "").strip():
            f.append(f"metric {m['id']} is derived without a formula")

    ck = p["execution"]["checkpoint"]
    if ck["policy"] != "none":
        if not ck.get("interval_seconds") or not ck.get("grace_seconds"):
            f.append("execution.checkpoint: a checkpointing policy needs interval_seconds and grace_seconds above zero")
        if ck["restore_validation"] == "none":
            f.append("execution.checkpoint: a checkpointing policy needs restore_validation (manifest_sha256, application_managed or criu_selfcheck)")
    mc = p["execution"].get("measurement_class")
    if mc == "measurement" and ck["policy"] == "criu":
        f.append("execution: measurement_class measurement with checkpoint policy criu: a restored row's clock is invalid, so a timed metric cannot ride a CRIU-checkpointed job (counted units may)")
    if p["execution"]["timeout_seconds"] and pf["estimated_total_seconds"] and p["execution"]["timeout_seconds"] < pf["estimated_total_seconds"] / max(1, p["sample_size"]["instances"] * p["sample_size"]["replicates"]):
        f.append("execution.timeout_seconds is below the preflight estimate per sample")

    ap = p["analysis_plan"]
    if ap["script"] and base is not None:
        path = (base / ap["script"]["path"]) if not Path(ap["script"]["path"]).is_absolute() else Path(ap["script"]["path"])
        if path.is_file() and ap["script"]["sha256"] and sha256_file(path) != ap["script"]["sha256"]:
            f.append(f"analysis_plan.script.sha256 does not match {path}")
    if p["freeze"]["status"] == "frozen":
        if ap["script"] and not ap["script"]["sha256"]:
            f.append("frozen protocol: analysis_plan.script.sha256 is null (freeze the analysis before the data)")
        if not ap["frozen_before_data"]:
            f.append("frozen protocol: analysis_plan.frozen_before_data is false")
        if p["freeze"]["protocol_sha256"] != protocol_hash(p):
            f.append("freeze.protocol_sha256 does not match the canonical hash of this document: the protocol changed after it was frozen (file an amendment under a new version instead)")
        if not p["freeze"]["frozen_at"]:
            f.append("frozen protocol without frozen_at")
    for am in p.get("amendments", []):
        if not am["filed_before_affected_data"]:
            f.append(f"amendment {am['id']} was filed after the data it affects: report both versions, and the amended cells decide nothing")
    for a in arms.values():
        same = a.get("same_instrument_as")
        if same:
            if same not in arms:
                f.append(f"arm {a['id']} names unknown same_instrument_as {same!r}")
            else:
                for key in ("commit", "binary_sha256", "threads"):
                    if a["instrument"].get(key) != arms[same]["instrument"].get(key):
                        f.append(f"arm {a['id']} declares the same instrument as {same} but {key} differs")
    return f


def derive_seed(protocol_sha: str, arm: str, instance: str, replicate: int) -> int:
    msg = SEED_DOMAIN + f"{protocol_sha}\n{arm}\n{instance}\n{replicate}".encode("utf-8")
    return int.from_bytes(hashlib.sha256(msg).digest()[:8], "big")


def seeds_table(p: dict[str, Any]) -> list[dict[str, Any]]:
    sd = p["randomization"]["seed_derivation"]
    sha = p["freeze"]["protocol_sha256"] or protocol_hash(p)
    rows = []
    n_inst, n_rep = p["sample_size"]["instances"], p["sample_size"]["replicates"]
    explicit = sd.get("seeds") or []
    k = 0
    for arm in p["arms"]:
        for i in range(n_inst):
            for r in range(n_rep):
                if sd["method"] == "protocol_hash_sha256":
                    seed: int | str = derive_seed(sha, arm["id"], str(i), r)
                elif sd["method"] == "explicit_list":
                    seed = explicit[k % len(explicit)] if explicit else ""
                    k += 1
                elif sd["method"] == "harness_drawn":
                    seed = ""
                else:
                    seed = derive_seed(sha + ":" + str(sd.get("nonce") or ""), arm["id"], str(i), r)
                rows.append({"arm": arm["id"], "instance": str(i), "replicate": r, "seed": seed})
    return rows


def freeze(path: Path, commit: str | None, filed_before: bool) -> dict[str, Any]:
    p = read_json(path)
    if detect_kind(p) != "experiment.protocol/v1":
        raise Refused("freeze takes a protocol")
    if p["freeze"]["status"] == "frozen":
        raise Refused(f"{path} is already frozen ({p['freeze']['protocol_sha256']}); bump version and amend instead")
    errors = schema_errors(p, "experiment.protocol/v1")
    if errors:
        raise Refused("protocol does not validate; fix before freezing:\n  " + "\n  ".join(errors))
    if commit == "auto":
        commit = git_head(path.parent)
    p["freeze"] = {"status": "frozen", "protocol_sha256": protocol_hash(p), "commit": commit,
                   "frozen_at": now_iso(), "filed_before_affected_data": filed_before}
    path.write_text(json.dumps(p, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return p["freeze"]


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

def compute_flow(runs: list[dict[str, Any]]) -> dict[str, Any]:
    excluded: dict[str, list[str]] = {}
    for r in runs:
        if r["exclusion"]["excluded"]:
            excluded.setdefault(r["exclusion"]["rule"] or "unspecified", []).append(r["run_id"])
    return {"planned": len(runs),
            "attempted": sum(1 for r in runs if r["attempts"] >= 1),
            "completed": sum(1 for r in runs if r["outcome_class"] == "completed"),
            "not_completed": sum(1 for r in runs if r["outcome_class"] == "not_completed"),
            "interrupted": sum(1 for r in runs if r["status"] == "interrupted"),
            "resumed": sum(1 for r in runs if r["resumed"] > 0),
            "excluded": [{"rule": k, "run_ids": v} for k, v in sorted(excluded.items())]}


def lint_export(e: dict[str, Any], protocol: dict[str, Any] | None, base: Path | None, verify_files: bool) -> list[str]:
    f: list[str] = []
    arm_roles = {a["id"]: a["role"] for a in e["arms"]}
    for r in e["runs"]:
        rid = r["run_id"]
        if r["arm"] not in arm_roles:
            f.append(f"run {rid}: arm {r['arm']!r} is not in export.arms")
        want = "completed" if r["status"] in COMPLETED else "not_completed"
        if r["outcome_class"] != want:
            f.append(f"run {rid}: status {r['status']} is outcome_class {want}, not {r['outcome_class']}")
        if (r["status"] == "interrupted" or r["resumed"] > 0) and r["measurements"]["wall_valid"]:
            f.append(f"run {rid}: interrupted or resumed, so wall_valid must be false (counted units stay valid)")
        if r["isolation"].get("contended") and r["measurements"]["wall_valid"]:
            f.append(f"run {rid}: contended, so wall_valid must be false")
        if r["verification"]["status"] == "refuted" and not r["exclusion"]["excluded"]:
            f.append(f"run {rid}: certificate refuted but the row is not excluded as an invalid measurement")
        if r["exclusion"]["excluded"] and not (r["exclusion"].get("rule") or "").strip():
            f.append(f"run {rid}: excluded without naming the protocol rule")
        if r["checkpoint"] and r["checkpoint"]["policy"] != "none" and r["resumed"] > 0 \
                and r["checkpoint"]["restored_from_generation"] is None:
            f.append(f"run {rid}: resumed {r['resumed']} time(s) but restored_from_generation is null")
    if e["flow"] != compute_flow(e["runs"]):
        f.append("flow does not match the runs (recompute with `flow`)")
    for n in e["notes"]:
        if n["kind"] != "observation":
            f.append("notes carry observations only")
    if protocol is not None:
        psha = protocol["freeze"]["protocol_sha256"]
        if protocol["freeze"]["status"] != "frozen":
            f.append("protocol is not frozen: an export may only bind a frozen protocol")
        elif e["protocol"]["sha256"] != psha:
            f.append(f"export.protocol.sha256 {e['protocol']['sha256'][:12]} != frozen protocol {psha[:12]}")
        if e["protocol"]["protocol_id"] != protocol["protocol_id"] or e["protocol"]["version"] != protocol["version"]:
            f.append("export.protocol id/version differ from the protocol")
        parms = {a["id"]: a for a in protocol["arms"]}
        for a in e["arms"]:
            if a["id"] not in parms:
                f.append(f"export arm {a['id']} is not in the protocol")
            elif a["role"] != parms[a["id"]]["role"]:
                f.append(f"export arm {a['id']} has role {a['role']}, protocol says {parms[a['id']]['role']}")
            elif parms[a["id"]]["instrument"]["binary_sha256"] and a["binary_sha256"] \
                    and a["binary_sha256"] != parms[a["id"]]["instrument"]["binary_sha256"]:
                f.append(f"export arm {a['id']} ran binary {a['binary_sha256'][:12]}, protocol pinned {parms[a['id']]['instrument']['binary_sha256'][:12]}")
        missing = sorted(set(parms) - {r["arm"] for r in e["runs"]})
        if missing:
            f.append(f"protocol arms with no run in the export: {missing}")
        planned = len(protocol["arms"]) * protocol["sample_size"]["instances"] * (protocol["sample_size"]["replicates"] + protocol["sample_size"].get("warmups", 0))
        measured = [r for r in e["runs"] if not r["warmup"]]
        expected_measured = len(protocol["arms"]) * protocol["sample_size"]["instances"] * protocol["sample_size"]["replicates"]
        if len(measured) != expected_measured:
            f.append(f"export has {len(measured)} measured rows; the protocol plans {expected_measured} "
                     f"(arms x instances x replicates); {planned} with warmups. A shortfall must be an infrastructure stop, never a choice")
        iso_req = protocol["measurement"]["isolation_required"]
        for r in measured:
            tier = r["isolation"]["tier"]
            if r["measurements"]["wall_valid"] and iso_req != "none" and tier is not None \
                    and ISOLATION_RANK.get(tier, -1) < ISOLATION_RANK[iso_req]:
                f.append(f"run {r['run_id']}: wall_valid but earned {tier} below the protocol's {iso_req}")
        if protocol["analysis_plan"]["script"] and e["analysis"]["script"] \
                and protocol["analysis_plan"]["script"]["sha256"] \
                and e["analysis"]["script"]["sha256"] != protocol["analysis_plan"]["script"]["sha256"]:
            f.append("analysis.script.sha256 differs from the frozen analysis_plan.script.sha256")
        if protocol["randomization"]["blinding"]["analysis_labels_masked"] and not e["analysis"]["blinded"]:
            f.append("protocol requires masked arm labels during analysis but export.analysis.blinded is false")
        if protocol["randomization"]["seed_derivation"]["method"] == "protocol_hash_sha256":
            table = {(s["arm"], s["instance"], s["replicate"]): s["seed"] for s in seeds_table(protocol)}
            for r in measured:
                key = (r["arm"], r["instance_id"], r["replicate"])
                if key in table and r["seed"] is not None and str(r["seed"]) != str(table[key]):
                    f.append(f"run {r['run_id']}: seed {r['seed']} is not the protocol-derived seed {table[key]}")
    if verify_files and base is not None:
        for fl in e["files"] + [a for r in e["runs"] for a in r["artifacts"]]:
            path = base / fl["path"]
            if not path.is_file():
                f.append(f"file missing: {fl['path']}")
                continue
            if path.stat().st_size != fl["bytes"] or sha256_file(path) != fl["sha256"]:
                f.append(f"file changed since export: {fl['path']}")
    return f


def blind(e: dict[str, Any], nonce: str) -> tuple[dict[str, Any], dict[str, str]]:
    """Replace arm ids by labels that depend only on the nonce, keeping roles
    hidden too: an analyst who sees 'reference' has not been blinded."""
    ranked = sorted(e["arms"], key=lambda a: sha256_bytes(BLIND_DOMAIN + f"{nonce}\n{a['id']}".encode()))
    mapping = {a["id"]: f"arm-{k:02d}" for k, a in enumerate(ranked)}
    out = json.loads(json.dumps(e))
    out["arms"] = [{"id": mapping[a["id"]], "role": "candidate" if a["role"] in ("reference", "baseline", "candidate") else a["role"],
                    "binary_sha256": None, "commit": None} for a in sorted(e["arms"], key=lambda a: mapping[a["id"]])]
    for r in out["runs"]:
        r["arm"] = mapping[r["arm"]]
    out["analysis"]["blinded"] = True
    out["analysis"]["blinding_key_sha256"] = sha256_bytes(canonical({"nonce": nonce, "mapping": mapping}))
    return out, mapping


def render_flow(e: dict[str, Any]) -> str:
    fl = e["flow"]
    lines = [f"planned {fl['planned']}  attempted {fl['attempted']}  completed {fl['completed']}  "
             f"not_completed {fl['not_completed']}  interrupted {fl['interrupted']}  resumed {fl['resumed']}"]
    for x in fl["excluded"]:
        lines.append(f"  excluded by {x['rule']}: {len(x['run_ids'])} ({', '.join(x['run_ids'][:6])}{'...' if len(x['run_ids']) > 6 else ''})")
    by_arm: dict[str, dict[str, int]] = {}
    for r in e["runs"]:
        d = by_arm.setdefault(r["arm"], {"rows": 0, "measured": 0, "completed": 0, "verified": 0, "wall_valid": 0})
        d["rows"] += 1
        d["measured"] += not r["warmup"]
        d["completed"] += r["outcome_class"] == "completed"
        d["verified"] += r["verification"]["status"] == "verified"
        d["wall_valid"] += bool(r["measurements"]["wall_valid"])
    lines.append("arm                 rows measured completed verified wall_valid")
    for arm, d in sorted(by_arm.items()):
        lines.append(f"{arm:<20}{d['rows']:>4} {d['measured']:>8} {d['completed']:>9} {d['verified']:>8} {d['wall_valid']:>10}")
    return "\n".join(lines)


def run_row(**kw: Any) -> dict[str, Any]:
    row = {"run_id": None, "arm": None, "instance_id": None, "seed": None, "replicate": 0, "warmup": False,
           "status": "succeeded", "outcome_class": "completed", "attempts": 1, "resumed": 0, "checkpoint": None,
           "measurements": {"counted": {}, "wall_seconds": None, "wall_valid": False, "cpu_user_seconds": None,
                            "cpu_sys_seconds": None, "max_rss_bytes": None, "counters": {}},
           "isolation": {"tier": None, "contended": None, "blockers": []},
           "verification": {"status": "not_run", "verifier": None},
           "exclusion": {"excluded": False, "rule": None},
           "artifacts": [], "started_at": None, "finished_at": None, "worker": None, "backend_ref": None}
    for k, v in kw.items():
        if isinstance(v, dict) and isinstance(row.get(k), dict):
            row[k].update(v)
        else:
            row[k] = v
    row["outcome_class"] = "completed" if row["status"] in COMPLETED else "not_completed"
    return row


def export_skeleton(protocol: dict[str, Any], protocol_path: str, backend: str, export_id: str) -> dict[str, Any]:
    return {"schema": "experiment.export/v1", "export_id": export_id, "created": now_iso(),
            "protocol": {"path": protocol_path, "sha256": protocol["freeze"]["protocol_sha256"] or protocol_hash(protocol),
                         "protocol_id": protocol["protocol_id"], "version": protocol["version"]},
            "producer": {"runtime": os.environ.get("AUTORESEARCH_RUNTIME") or ("claude_code" if os.environ.get("CLAUDECODE") else None),
                         "model": os.environ.get("AUTORESEARCH_RESOLVED_MODEL"), "session": None, "role": "executor"},
            "source": {"repo": protocol["repository"], "commit": None, "dirty": None},
            "backend": backend,
            "host": {"path": None, "sha256": None, "class_id": None,
                     "summary": {"cpu_model": None, "logical_cpus": None, "memory_bytes": None, "kernel": None,
                                 "hypervisor": None, "isolation_tier_max": None}},
            "arms": [{"id": a["id"], "role": a["role"], "binary_sha256": a["instrument"]["binary_sha256"],
                      "commit": a["instrument"]["commit"]} for a in protocol["arms"]],
            "runs": [], "flow": compute_flow([]), "files": [],
            "analysis": {"script": None, "blinded": False, "blinding_key_sha256": None, "outputs": [], "unmasked_at": None},
            "notes": [], "reviews_dir": "reviews"}


def file_entry(base: Path, rel: str, kind: str = "raw") -> dict[str, Any]:
    path = base / rel
    return {"path": rel, "sha256": sha256_file(path), "bytes": path.stat().st_size, "kind": kind}


def from_taskq(result: dict[str, Any], protocol: dict[str, Any], protocol_path: str, arm: str, instance: str,
               export_id: str) -> dict[str, Any]:
    if result.get("schema") != "taskq.task-result/v1":
        raise Refused("not a taskq.task-result/v1 document")
    e = export_skeleton(protocol, protocol_path, "taskq", export_id)
    src = result.get("source", {})
    e["source"] = {"repo": src.get("repo", protocol["repository"]), "commit": src.get("resolved_commit"), "dirty": False}
    env = result.get("environment", {})
    e["host"]["summary"].update({"cpu_model": env.get("cpu_model"), "logical_cpus": env.get("cpus") or env.get("logical_cpus"),
                                 "kernel": env.get("kernel")})
    e["host"]["class_id"] = env.get("pod") or env.get("node")
    status = result["status"]
    seeds = {(s["arm"], s["instance"], s["replicate"]): s["seed"] for s in seeds_table(protocol)}
    for i, run in enumerate(result.get("runs", [])):
        run_status = "succeeded" if run.get("exit_code") == 0 and not run.get("timed_out") else ("timeout" if run.get("timed_out") else "failed")
        if status in ("cancelled", "infra_error"):
            run_status = status
        ver = run.get("verification") or {}
        metrics = run.get("metrics") or {}
        counted = {k: v for k, v in metrics.items() if isinstance(v, (int, float, str)) and not k.startswith("_")}
        rep = sum(1 for r in result["runs"][:i] if not r.get("warmup"))
        e["runs"].append(run_row(
            run_id=f"{result['task_id']}/run-{run['index']}", arm=arm, instance_id=instance,
            seed=seeds.get((arm, instance, rep)), replicate=rep, warmup=bool(run.get("warmup")), status=run_status,
            attempts=result.get("attempt", 1),
            measurements={"counted": counted, "wall_seconds": run.get("wall_seconds"),
                          "wall_valid": run_status == "succeeded" and not run.get("warmup"),
                          "cpu_user_seconds": run.get("user_cpu_seconds"), "cpu_sys_seconds": run.get("sys_cpu_seconds"),
                          "max_rss_bytes": (run.get("max_rss_kb") or 0) * 1024 if run.get("max_rss_kb") is not None else None,
                          "counters": {}},
            verification={"status": ver.get("status", "not_run" if not ver else "error"), "verifier": ver.get("verifier")},
            exclusion={"excluded": ver.get("status") == "refuted", "rule": "invalid_measurement: certificate refuted" if ver.get("status") == "refuted" else None},
            worker=result.get("worker", {}).get("id"), backend_ref=result["task_id"],
            started_at=result.get("timing", {}).get("started_at"), finished_at=result.get("timing", {}).get("finished_at")))
    for a in result.get("artifacts", []):
        e["files"].append({"path": a["path"], "sha256": a["sha256"], "bytes": a["bytes"],
                           "kind": "log" if a["path"].startswith("_taskq_logs/") else "raw"})
    e["flow"] = compute_flow(e["runs"])
    e["backend_record"] = {"task_id": result["task_id"], "spec_sha256": result.get("spec_sha256"), "fence": result.get("fence"),
                           "status": status, "outcome_class": result.get("outcome_class")}
    return e


def from_ecbench(session_dir: Path, protocol: dict[str, Any], protocol_path: str, export_id: str,
                 files_prefix: str = "") -> dict[str, Any]:
    session = read_json(session_dir / "session.json")
    if session.get("schema") != "ecbench.session/v1":
        raise Refused("not an ecbench.session/v1 directory")
    e = export_skeleton(protocol, protocol_path, "ecbench", export_id)
    e["source"]["commit"] = session.get("git_commit")
    e["source"]["dirty"] = session.get("git_dirty")
    e["host"]["class_id"] = session.get("env_class_id")
    if (session_dir / "host.json").is_file():
        host = read_json(session_dir / "host.json")
        e["host"]["path"] = str(PurePosixPath(files_prefix) / "host.json") if files_prefix else "host.json"
        e["host"]["sha256"] = sha256_file(session_dir / "host.json")
        stable = host.get("stable") if isinstance(host.get("stable"), dict) else {}
        virt = stable.get("virtualization")
        if isinstance(virt, dict):
            virt = " ".join(str(virt[k]) for k in ("dmi_vendor", "dmi_product", "hypervisor", "detected") if virt.get(k)) \
                or json.dumps(virt, sort_keys=True)
        e["host"]["summary"].update({
            "cpu_model": stable.get("cpu_model") or host.get("cpu_model"),
            "logical_cpus": int(stable["logical_cpus"]) if str(stable.get("logical_cpus", "")).isdigit() else None,
            "memory_bytes": int(stable["mem_total_kib"]) * 1024 if str(stable.get("mem_total_kib", "")).isdigit() else None,
            "kernel": stable.get("kernel_release") or (host.get("kernel") if isinstance(host.get("kernel"), str) else None),
            "hypervisor": str(virt) if virt else None})
    arm_roles = {a["id"]: a["role"] for a in protocol["arms"]}
    best = -1
    with (session_dir / "records.jsonl").open(encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            r = json.loads(line)
            arm = r["arm"]
            if arm not in arm_roles:
                arm_roles[arm] = ECBENCH_ROLES.get(r.get("role"), "candidate")
                e["arms"].append({"id": arm, "role": arm_roles[arm], "binary_sha256": r.get("binary_sha256"), "commit": session.get("git_commit")})
            outcome = r.get("outcome", {})
            status = "succeeded" if outcome.get("status") == "verified" else ("timeout" if outcome.get("status") == "timeout" else "failed")
            iso = r.get("isolation", {})
            tier = iso.get("level")
            best = max(best, ISOLATION_RANK.get(tier, -1))
            cost = r.get("cost", {})
            t = r.get("time", {})
            counted = {"total_gae": cost.get("total_gae"), "s": cost.get("s")}
            counters = dict(r.get("counters", {}))
            for k, v in (r.get("field_ops") or {}).items():
                counters[f"field_ops.{k}"] = v
            req = ISOLATION_RANK[protocol["measurement"]["isolation_required"]]
            e["runs"].append(run_row(
                run_id=r["record_id"], arm=arm, instance_id=r["workload"]["workload_id"], seed=r.get("algorithm_seed"),
                replicate=r.get("round", 0), warmup=bool(r.get("warmup")), status=status,
                measurements={"counted": {k: v for k, v in counted.items() if v is not None},
                              "wall_seconds": (t.get("solve_wall_ns") / 1e9) if t.get("solve_wall_ns") is not None else None,
                              "wall_valid": status == "succeeded" and not r.get("warmup") and ISOLATION_RANK.get(tier, -1) >= req and req >= 0,
                              "cpu_user_seconds": (t.get("user_ns") / 1e9) if t.get("user_ns") is not None else None,
                              "cpu_sys_seconds": (t.get("sys_ns") / 1e9) if t.get("sys_ns") is not None else None,
                              "max_rss_bytes": (t.get("max_rss_kib") or 0) * 1024 if t.get("max_rss_kib") is not None else None,
                              "counters": counters,
                              "perf": {k: v for k, v in (t.get("hw_solve") or {}).items() if k in ("instructions", "cycles")}},
                isolation={"tier": tier, "contended": ISOLATION_RANK.get(tier, -1) < req if tier else None,
                           "blockers": list(iso.get("blockers", []))},
                verification={"status": "verified" if outcome.get("matches_target") else ("refuted" if outcome.get("recovered") is not None else "no_claim"),
                              "verifier": "ecbench: [k]G = Q recomputed by the harness"},
                exclusion={"excluded": outcome.get("status") not in ("verified",) and not r.get("warmup") and outcome.get("recovered") is not None,
                           "rule": "invalid_measurement: wrong answer" if outcome.get("recovered") is not None and not outcome.get("matches_target") else None},
                backend_ref=r.get("run_id")))
    e["host"]["summary"]["isolation_tier_max"] = next((k for k, v in ISOLATION_RANK.items() if v == best and k.startswith("L")), None)
    for name in ("spec.json", "plan.json", "records.jsonl", "session.json", "host.json"):
        if (session_dir / name).is_file():
            kind = {"spec.json": "protocol", "plan.json": "protocol", "records.jsonl": "raw", "session.json": "summary", "host.json": "host"}[name]
            entry = file_entry(session_dir, name, kind)
            if files_prefix:
                entry["path"] = str(PurePosixPath(files_prefix) / name)
            e["files"].append(entry)
    e["flow"] = compute_flow(e["runs"])
    e["backend_record"] = {"session_id": session["session_id"], "spec_sha256": session.get("spec_sha256"),
                           "records_sha256": session.get("records_sha256"), "status": session.get("status")}
    return e


DEFAULT_MAP = {"run_id": "run_id", "arm": "arm", "instance_id": "instance_id", "seed": "seed", "replicate": "replicate",
               "warmup": "warmup", "status": "status", "wall_seconds": "wall_seconds", "tier": "tier",
               "verification": "verification"}


def from_rows(path: Path, protocol: dict[str, Any], protocol_path: str, export_id: str, mapping: dict[str, str],
              files_prefix: str = "") -> dict[str, Any]:
    cols = {**DEFAULT_MAP, **mapping}
    if path.suffix == ".csv":
        with path.open(newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
    else:
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    e = export_skeleton(protocol, protocol_path, "manual", export_id)
    counted_ids = [m["id"] for m in protocol["metrics"]["primary"] + protocol["metrics"]["secondary"] if m["kind"] in ("counted", "exact", "rate")]
    for i, row in enumerate(rows):
        def get(key, default=None):
            return row.get(cols.get(key, key), default)
        status = str(get("status", "succeeded"))
        warm = str(get("warmup", "false")).lower() in ("1", "true", "yes")
        counted = {m: row[cols.get(m, m)] for m in counted_ids if cols.get(m, m) in row and row[cols.get(m, m)] not in ("", None)}
        for k, v in list(counted.items()):
            try:
                counted[k] = int(v) if str(v).lstrip("-").isdigit() else float(v)
            except ValueError:
                counted[k] = str(v)
        wall = get("wall_seconds")
        e["runs"].append(run_row(
            run_id=str(get("run_id", f"row-{i}")), arm=str(get("arm")), instance_id=str(get("instance_id", "0")),
            seed=get("seed"), replicate=int(get("replicate", 0) or 0), warmup=warm, status=status,
            measurements={"counted": counted, "wall_seconds": float(wall) if wall not in (None, "") else None,
                          "wall_valid": False, "counters": {}},
            isolation={"tier": get("tier")},
            verification={"status": str(get("verification", "not_run"))}))
    entry = file_entry(path.parent, path.name, "raw")
    if files_prefix:
        entry["path"] = str(PurePosixPath(files_prefix) / path.name)
    e["files"].append(entry)
    e["flow"] = compute_flow(e["runs"])
    return e


# ---------------------------------------------------------------------------
# Review
# ---------------------------------------------------------------------------

def lint_review(r: dict[str, Any], base: Path | None) -> list[str]:
    f: list[str] = []
    kinds = {c["kind"] for c in r["checks"]}
    missing = [k for k in REQUIRED_REVIEW_CHECKS if k not in kinds]
    if missing:
        f.append(f"review lacks required check kinds: {missing}")
    for k in ("controls", "recompute", "scope"):
        if k in kinds and all(c["result"] == "not_covered" for c in r["checks"] if c["kind"] == k):
            f.append(f"check {k} is not_covered: a reviewer who did not read the {k} has a scaffold, not a review")
    placeholders = [c["id"] for c in r["checks"] if "<reviewer:" in c["detail"]]
    if "<reviewer:" in r["recommendation"]["reason"]:
        placeholders.append("recommendation")
    if placeholders:
        f.append(f"unfilled scaffold text in: {placeholders}")
    rp = r["replay"]
    if rp["performed"]:
        if rp["units_sampled"] != rp["identical"] + rp["mismatched"]:
            f.append("replay: units_sampled != identical + mismatched")
        if not rp["nonce"]:
            f.append("replay performed without a nonce drawn after publication")
        if rp["miss_probability"] is None:
            f.append("replay performed without the miss-probability table")
    elif rp["units_sampled"] or rp["identical"] or rp["mismatched"]:
        f.append("replay not performed but counts are non-zero")
    for j in r["judgments"]:
        if j["verdict"] in ("supported_within_scope", "refuted_within_scope", "more_extreme_than_controls") and not j.get("scope"):
            f.append(f"judgment on {j['claim_id']}: a scoped verdict needs its scope")
    if any(c["result"] == "fail" and c["kind"] in ("hashes", "protocol_adherence") for c in r["checks"]):
        for j in r["judgments"]:
            if j["verdict"] in ("supported_within_scope", "more_extreme_than_controls"):
                f.append(f"judgment on {j['claim_id']} is positive although hashes or protocol adherence failed")
    if base is not None:
        path = base / r["export"]["path"]
        if path.is_file() and sha256_file(path) != r["export"]["sha256"]:
            f.append("export.sha256 does not match the export on disk")
    return f


def miss_table(k: int) -> dict[str, float]:
    return {str(frac): round((1 - frac) ** k, 6) for frac in (0.01, 0.05, 0.1, 0.25, 0.5)}


def review_scaffold(export_path: Path, export: dict[str, Any], protocol: dict[str, Any] | None,
                    role: str, runtime: str | None, model: str | None, session: str | None) -> dict[str, Any]:
    tok = secrets.token_hex(3)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    checks = []
    file_findings = lint_export(export, protocol, export_path.parent, verify_files=True)
    hash_fail = [x for x in file_findings if x.startswith("file ")]
    checks.append({"id": "hashes", "kind": "hashes", "result": "fail" if hash_fail else "pass",
                   "detail": "; ".join(hash_fail) if hash_fail else f"{len(export['files'])} files and every artifact hash recomputed from disk"})
    adherence = [x for x in file_findings if not x.startswith("file ")]
    checks.append({"id": "adherence", "kind": "protocol_adherence",
                   "result": "fail" if adherence else ("pass" if protocol else "not_covered"),
                   "detail": "; ".join(adherence) if adherence else ("export binds the frozen protocol; arms, seeds, row counts and isolation agree" if protocol else "no protocol supplied")})
    for kind, text in (("controls", "<reviewer: A/A spread, positive-control detection, negative-control population; cite rows>"),
                       ("recompute", "<reviewer: headline numbers recomputed from the raw rows with the frozen analysis; cite values>"),
                       ("statistics", "<reviewer: effect size, interval, correction as the decision rule states>"),
                       ("scope", "<reviewer: what the rows do and do not cover>"),
                       ("blinding", "<reviewer: were arm labels masked until the analysis was frozen>")):
        checks.append({"id": kind, "kind": kind, "result": "not_covered", "detail": text})
    return {"schema": "experiment.review/v1", "review_id": f"REV-{stamp}-{tok}", "created": now_iso(),
            "export": {"path": export_path.name, "sha256": sha256_file(export_path), "export_id": export["export_id"]},
            "protocol_sha256": export["protocol"]["sha256"],
            "reviewer": {"runtime": runtime, "model": model, "session": session, "role": role,
                         "independence": {"same_session_as_producer": False, "same_host_class": None,
                                          "shares_code_with_producer": True, "declared_conflicts": []}},
            "checks": checks,
            "replay": {"performed": False, "method": None, "units_sampled": 0, "nonce": None, "identical": 0, "mismatched": 0, "miss_probability": None},
            "observations": [], "judgments": [], "open_questions": [],
            "recommendation": {"action": "no_action", "reason": "<reviewer: fill in>"},
            "asserts_nothing_about": ["official research status", "hypothesis status", "the correctness of the design"]}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _report(findings: list[str], label: str) -> int:
    for x in findings:
        print(f"FINDING: {x}")
    print(f"{'OK' if not findings else 'FAIL'}: {label} ({len(findings)} finding(s))")
    return 1 if findings else 0


def cmd_validate(args) -> int:
    path = Path(args.file)
    obj = read_json(path)
    kind = detect_kind(obj)
    findings = schema_errors(obj, kind)
    if not findings:
        if kind == "experiment.protocol/v1":
            findings = lint_protocol(obj, path.parent)
        elif kind == "experiment.export/v1":
            protocol = read_json(Path(args.protocol)) if args.protocol else None
            findings = lint_export(obj, protocol, path.parent, args.verify_files)
        else:
            findings = lint_review(obj, path.parent)
    return _report(findings, f"{kind} {path}")


def cmd_hash(args) -> int:
    print(protocol_hash(read_json(Path(args.file))))
    return 0


def cmd_freeze(args) -> int:
    fr = freeze(Path(args.file), args.commit, args.filed_before_affected_data)
    print(json.dumps(fr, indent=2))
    return 0


def cmd_seeds(args) -> int:
    p = read_json(Path(args.file))
    if args.all:
        for row in seeds_table(p):
            print(json.dumps(row))
        return 0
    if args.arm is None or args.instance is None:
        raise Refused("seeds needs --all or --arm, --instance and --replicate")
    sha = p["freeze"]["protocol_sha256"] or protocol_hash(p)
    print(derive_seed(sha, args.arm, args.instance, args.replicate))
    return 0


def cmd_power(args) -> int:
    print(json.dumps(power_check(args.n, args.alpha, args.m), indent=2))
    return 0


def cmd_blind(args) -> int:
    e = read_json(Path(args.file))
    if detect_kind(e) != "experiment.export/v1":
        raise Refused("blind takes an export")
    nonce = args.nonce or secrets.token_hex(16)
    out, mapping = blind(e, nonce)
    write_once(Path(args.out), out)
    key_path = Path(args.out).with_suffix(".key.json")
    fd = os.open(key_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(json.dumps({"nonce": nonce, "mapping": mapping}, indent=2) + "\n")
    print(f"blinded export: {args.out}\nkey (keep closed until the analysis is frozen): {key_path}\n"
          f"blinding_key_sha256: {out['analysis']['blinding_key_sha256']}")
    return 0


def cmd_flow(args) -> int:
    e = read_json(Path(args.file))
    computed = compute_flow(e["runs"])
    print(render_flow({**e, "flow": computed}))
    if computed != e.get("flow"):
        print("FINDING: the export's flow block differs from the rows")
        return 1
    return 0


def cmd_check_export(args) -> int:
    path = Path(args.file)
    e = read_json(path)
    protocol = read_json(Path(args.protocol))
    findings = schema_errors(e, "experiment.export/v1") + schema_errors(protocol, "experiment.protocol/v1")
    if not findings:
        findings = lint_export(e, protocol, path.parent, args.verify_files)
    return _report(findings, f"export {path} against {args.protocol}")


def cmd_review(args) -> int:
    if args.review_cmd == "validate":
        path = Path(args.file)
        r = read_json(path)
        findings = schema_errors(r, "experiment.review/v1") or lint_review(r, path.parent)
        return _report(findings, f"review {path}")
    export_path = Path(args.file)
    export = read_json(export_path)
    if detect_kind(export) != "experiment.export/v1":
        raise Refused("review new takes an export")
    protocol = None
    if args.protocol:
        protocol = read_json(Path(args.protocol))
    elif (export_path.parent / export["protocol"]["path"]).is_file():
        protocol = read_json(export_path.parent / export["protocol"]["path"])
    r = review_scaffold(export_path, export, protocol, args.role, args.runtime, args.model, args.session)
    out_dir = Path(args.out_dir) if args.out_dir else export_path.parent / export["reviews_dir"]
    out = out_dir / f"{r['review_id']}.json"
    write_once(out, r)
    print(f"review scaffold: {out}\nfill every not_covered check, the observations, judgments and recommendation; never edit the export")
    return 0


def _prefix(target: Path, out: Path) -> str:
    """Path of `target` relative to the export's directory, '' when it is that directory."""
    rel = os.path.relpath(target.resolve(), out.resolve().parent)
    return "" if rel == "." else rel


def _common_export_args(args) -> tuple[dict[str, Any], str]:
    protocol = read_json(Path(args.protocol))
    if detect_kind(protocol) != "experiment.protocol/v1":
        raise Refused("--protocol must be an experiment.protocol/v1 file")
    if protocol["freeze"]["status"] != "frozen":
        raise Refused("the protocol is not frozen; an export binds a frozen protocol only")
    out = Path(args.out)
    try:
        rel = os.path.relpath(Path(args.protocol).resolve(), out.resolve().parent)
    except ValueError:
        rel = str(Path(args.protocol))
    return protocol, rel


def cmd_from_taskq(args) -> int:
    protocol, rel = _common_export_args(args)
    e = from_taskq(read_json(Path(args.file)), protocol, rel, args.arm, args.instance, args.export_id)
    write_once(Path(args.out), e)
    print(f"export: {args.out}")
    return _report(schema_errors(e, "experiment.export/v1") or lint_export(e, protocol, None, False), "export")


def cmd_from_ecbench(args) -> int:
    protocol, rel = _common_export_args(args)
    e = from_ecbench(Path(args.session_dir), protocol, rel, args.export_id, _prefix(Path(args.session_dir), Path(args.out)))
    write_once(Path(args.out), e)
    print(f"export: {args.out}")
    return _report(schema_errors(e, "experiment.export/v1") or lint_export(e, protocol, None, False), "export")


def cmd_from_rows(args) -> int:
    protocol, rel = _common_export_args(args)
    mapping = dict(kv.split("=", 1) for kv in args.map)
    e = from_rows(Path(args.file), protocol, rel, args.export_id, mapping, _prefix(Path(args.file).parent, Path(args.out)))
    write_once(Path(args.out), e)
    print(f"export: {args.out}")
    return _report(schema_errors(e, "experiment.export/v1") or lint_export(e, protocol, None, False), "export")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate"); v.add_argument("file"); v.add_argument("--protocol"); v.add_argument("--verify-files", action="store_true"); v.set_defaults(fn=cmd_validate)
    h = sub.add_parser("hash"); h.add_argument("file"); h.set_defaults(fn=cmd_hash)
    fz = sub.add_parser("freeze"); fz.add_argument("file"); fz.add_argument("--commit", default="auto")
    fz.add_argument("--filed-before-affected-data", action="store_true"); fz.set_defaults(fn=cmd_freeze)
    s = sub.add_parser("seeds"); s.add_argument("file"); s.add_argument("--all", action="store_true"); s.add_argument("--arm")
    s.add_argument("--instance"); s.add_argument("--replicate", type=int, default=0); s.set_defaults(fn=cmd_seeds)
    pw = sub.add_parser("power"); pw.add_argument("--n", type=int, required=True); pw.add_argument("--alpha", type=float, default=0.05)
    pw.add_argument("--m", type=int, default=1); pw.set_defaults(fn=cmd_power)
    b = sub.add_parser("blind"); b.add_argument("file"); b.add_argument("--out", required=True); b.add_argument("--nonce"); b.set_defaults(fn=cmd_blind)
    fl = sub.add_parser("flow"); fl.add_argument("file"); fl.set_defaults(fn=cmd_flow)
    ce = sub.add_parser("check-export"); ce.add_argument("file"); ce.add_argument("--protocol", required=True)
    ce.add_argument("--verify-files", action="store_true"); ce.set_defaults(fn=cmd_check_export)
    rv = sub.add_parser("review"); rsub = rv.add_subparsers(dest="review_cmd", required=True)
    rn = rsub.add_parser("new"); rn.add_argument("file"); rn.add_argument("--protocol"); rn.add_argument("--out-dir")
    rn.add_argument("--role", default="validator", choices=["validator", "red-team", "reviewer", "sheriff", "human", "other"])
    rn.add_argument("--runtime"); rn.add_argument("--model"); rn.add_argument("--session")
    rvv = rsub.add_parser("validate"); rvv.add_argument("file")
    rv.set_defaults(fn=cmd_review)
    for name, fn in (("from-taskq", cmd_from_taskq), ("from-rows", cmd_from_rows)):
        c = sub.add_parser(name); c.add_argument("file"); c.add_argument("--protocol", required=True); c.add_argument("--out", required=True)
        c.add_argument("--export-id", required=True)
        if name == "from-taskq":
            c.add_argument("--arm", required=True); c.add_argument("--instance", default="0")
        else:
            c.add_argument("--map", action="append", default=[])
        c.set_defaults(fn=fn)
    fe = sub.add_parser("from-ecbench"); fe.add_argument("session_dir"); fe.add_argument("--protocol", required=True)
    fe.add_argument("--out", required=True); fe.add_argument("--export-id", required=True); fe.set_defaults(fn=cmd_from_ecbench)

    args = ap.parse_args(argv)
    try:
        return args.fn(args)
    except Refused as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    except jsonschema.SchemaError as exc:
        print(f"REFUSED: schema broken: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
