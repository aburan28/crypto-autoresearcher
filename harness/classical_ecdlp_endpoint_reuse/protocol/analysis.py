#!/usr/bin/env python3
"""Frozen arithmetic for the endpoint-reuse study; does not launch trials.

Input is the public settings/target TSVs and an exact manifest of native JSONL
streams. Complete setup plus target counter deltas are added one counter at a
time. In particular, scalar-multiplication and doubling diagnostics are never
added to group_additions. A separately produced witness report is required to
qualify the primary panel. This script produces observations, not ledger state.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import random
from collections import defaultdict

ARMS = ("static_small", "static_full", "static_filled", "harvest", "harvest_disabled", "rho_reference")
PREFIXES = (1, 8, 16, 32, 64)
SCOPE = "classical_ecdlp_endpoint_reuse"

def read_json(path: Path):
    return json.loads(path.read_text())

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read_tsv(path: Path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))

def require(condition, message):
    if not condition:
        raise ValueError(message)

def exact_counters(value):
    require(isinstance(value, dict), "counter vector is not a mapping")
    result = {}
    for key, number in value.items():
        require(isinstance(key, str) and key, "empty counter name")
        require(isinstance(number, int) and not isinstance(number, bool) and number >= 0,
                "nonnegative integer counter required: " + key)
        result[key] = number
    require("group_additions" in result, "native counters.group_additions missing")
    return result

def add_vectors(left, right):
    return {key: left.get(key, 0) + right.get(key, 0) for key in set(left) | set(right)}

def quantile(values, q):
    require(values and 0 <= q <= 1, "invalid quantile")
    values = sorted(values)
    x = (len(values) - 1) * q
    lower = math.floor(x)
    upper = math.ceil(x)
    return values[lower] + (values[upper] - values[lower]) * (x - lower)

def cluster_summary(curve_ratios, bootstrap_indices):
    require(curve_ratios and all(math.isfinite(v) and v > 0 for v in curve_ratios),
            "ratios must be positive and defined; no numerical floors")
    logs = [math.log(v) for v in curve_ratios]
    gmean = math.exp(math.fsum(logs) / len(logs))
    boot = [math.exp(math.fsum(logs[i] for i in ids) / len(ids))
            for ids in bootstrap_indices]
    return {"curves": len(logs), "gmean_ratio": gmean,
            "curve_ratio_range": [min(curve_ratios), max(curve_ratios)],
            "pointwise_cluster_bootstrap_ci95": [quantile(boot, .025), quantile(boot, .975)]}

def raw_files(manifest_path):
    manifest = read_json(manifest_path)
    require(manifest.get("schema") == "classical.ecdlp.endpoint-reuse.raw-manifest.v1",
            "unexpected raw manifest schema")
    return manifest, [item for item in manifest["files"] if item["path"].endswith("/raw.jsonl")]

def stream_parts(manifest_path, manifest, item):
    """Read a native stream once, directly or from exact line-complete parts.

    Metadata/logs are not native rows. Original and partition copies are not
    double-counted, and reconstruction never writes into a sealed run folder.
    """
    path = manifest_path.parent / item["path"]
    if path.is_file():
        paths = [(path, item)]
    else:
        prefix = item["path"] + ".parts/"
        parts = sorted((p for p in manifest["files"] if p["path"].startswith(prefix)), key=lambda p: p["path"])
        require(parts, "native original and lossless parts are unavailable: " + item["path"])
        paths = [(manifest_path.parent / p["path"], p) for p in parts]
    digest, size = hashlib.sha256(), 0
    for part, description in paths:
        require(part.stat().st_size == description["bytes"] and sha(part) == description["sha256"],
                "raw stream/part bytes/hash mismatch: " + str(part))
        with part.open("rb") as stream:
            for line in stream:
                digest.update(line)
                size += len(line)
                if line.strip():
                    row = json.loads(line)
                    require(row.get("scope") == SCOPE, "unexpected native scope")
                    yield row
    require(size == item["bytes"] and digest.hexdigest() == item["sha256"],
            "logical native stream reconstruction mismatch: " + item["path"])

def native_rows(manifest_path):
    manifest, files = raw_files(manifest_path)
    for item in files:
        yield from stream_parts(manifest_path, manifest, item)

def panels(settings_rows, target_rows, rows):
    cells = {r["cell_id"]: r for r in settings_rows}
    require(len(cells) == len(settings_rows), "duplicate settings cell")
    by_pair = {(r["fixture_id"], int(r["replicate"])): r["cell_id"] for r in settings_rows}
    require(len(by_pair) == len(cells), "duplicate fixture/replicate cell")
    fixtures = sorted({r["fixture_id"] for r in settings_rows})
    require(len(fixtures) == 64 and len(cells) == 128, "fixed64curve/two-replicate coverage required")
    require(all((f, rep) in by_pair for f in fixtures for rep in (0, 1)), "replicate coverage")
    targets = defaultdict(dict)
    duplicates = []
    seen_points = defaultdict(dict)
    for r in target_rows:
        pair = (r["fixture_id"], int(r["replicate"]))
        require(pair in by_pair, "unknown target cell")
        cell = by_pair[pair]
        ordinal = int(r["target_ordinal"])
        require(ordinal not in targets[cell], "duplicate target ordinal")
        targets[cell][ordinal] = r["target_id"]
        point = (r["qx"], r["qy"], r["infinity"])
        if point in seen_points[cell]:
            duplicates.append({"cell_id": cell, "ordinal": ordinal,
                               "first_ordinal": seen_points[cell][point], "target_id": r["target_id"]})
        else:
            seen_points[cell][point] = ordinal
    require(len(target_rows) == 8192 and len({r["target_id"] for r in target_rows}) == 8192,
            "fixed8192globallyunique target IDs required, including repeatedQ")
    require(all(set(targets[c]) == set(range(64)) for c in cells), "fixed64targets/cell required")
    setup, answers, events = {}, defaultdict(dict), defaultdict(int)
    initial_entries = defaultdict(list)
    for row in rows:
        cell, arm = row["cell_id"], row["arm"]
        require(cell in cells and arm in ARMS, "unplanned native cell/arm")
        require(row["fixture"] == cells[cell]["fixture_id"], "native fixture identity mismatch")
        key = (cell, arm)
        kind = row["row_kind"]
        if kind == "setup":
            require(key not in setup, "duplicate setup")
            setup[key] = exact_counters(row["counters"])
        elif kind == "target":
            ordinal = int(row["target_ordinal"])
            require(ordinal in targets[cell] and row["target_id"] == targets[cell][ordinal],
                    "native target identity mismatch")
            require(ordinal not in answers[key], "duplicate target record")
            answers[key][ordinal] = row
        elif kind == "initial_endpoint":
            initial_entries[key].append([row["index"], row["fp"], row["exponent"]])
            events[key] += 1
        else:
            events[key] += 1
    result = []
    for cell in sorted(cells):
        for arm in ARMS:
            key = (cell, arm)
            require(key in setup, "missing setup: " + str(key))
            require(set(answers[key]) == set(range(64)), "missing target output: " + str(key))
            total = dict(setup[key])
            verified = 0
            prefixes = {}
            statuses = defaultdict(int)
            for ordinal in range(64):
                row = answers[key][ordinal]
                vector = exact_counters(row["counters"])
                require(set(vector) == set(setup[key]), "native counter fields changed within setup/target stream")
                total = add_vectors(total, vector)
                statuses[row["status"]] += 1
                verified += row["status"] == "solved" and row.get("verified_scalar") is not None
                if ordinal + 1 in PREFIXES:
                    prefixes[str(ordinal + 1)] = {"counters": dict(total), "verified_targets": verified}
            target_signature = [[i, answers[key][i]["status"], answers[key][i].get("verified_scalar"),
                                 answers[key][i]["counters"]] for i in range(64)]
            result.append({"cell_id": cell, "fixture_id": cells[cell]["fixture_id"],
                           "replicate": int(cells[cell]["replicate"]), "arm": arm,
                           "prefixes": prefixes, "status_counts": dict(statuses),
                           "initial_entries_sha256": hashlib.sha256(json.dumps(initial_entries[key], separators=(",", ":")).encode()).hexdigest(),
                           "target_answer_counter_trace_sha256": hashlib.sha256(json.dumps(target_signature, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
                           "unique_public_targets": len(seen_points[cell]), "event_rows": events[key]})
    return result, duplicates

def summarize(cell_panels, protocol_hash, external_nonce, repetitions=10000):
    curves = sorted({r["fixture_id"] for r in cell_panels})
    require(len(curves) == 64, "exact64curve bootstrap unit required")
    lookup = {(r["fixture_id"], r["replicate"], r["arm"]): r for r in cell_panels}
    seed = int.from_bytes(hashlib.sha256((protocol_hash + "\0" + external_nonce +
                                        "\0cluster-bootstrap-v1").encode()).digest()[:8], "big")
    rng = random.Random(seed)
    indices = [[rng.randrange(len(curves)) for _ in curves] for _ in range(repetitions)]
    comparisons = []
    for candidate, baseline in (("harvest", "static_filled"), ("harvest", "static_small"), ("harvest", "static_full"),
                                ("harvest", "rho_reference"), ("harvest_disabled", "static_small")):
        for prefix in PREFIXES:
            ratios, incomplete = [], []
            for curve in curves:
                values = {}
                for arm in (candidate, baseline):
                    records = [lookup[(curve, replicate, arm)]["prefixes"][str(prefix)] for replicate in (0, 1)]
                    if any(r["verified_targets"] != prefix for r in records):
                        incomplete.append(curve)
                    values[arm] = sum(r["counters"]["group_additions"] for r in records)
                if values[baseline] <= 0 or values[candidate] <= 0:
                    incomplete.append(curve)
                else:
                    ratios.append(values[candidate] / values[baseline])
            item = {"candidate": candidate, "baseline": baseline, "prefix": prefix,
                    "metric": "complete_setup_plus_online_group_additions",
                    "decisive": candidate == "harvest" and baseline == "static_filled" and prefix == 64,
                    "incomplete_curves": sorted(set(incomplete))}
            if not incomplete and len(ratios) == 64:
                item.update(cluster_summary(ratios, indices))
            else:
                item["undefined_reason"] = "full registered paired panel incomplete; no success-only gain"
            comparisons.append(item)
    aa_mismatches = []
    for curve in curves:
        for rep in (0, 1):
            a, b = (lookup[(curve, rep, arm)] for arm in ("static_small", "harvest_disabled"))
            if any(a[name] != b[name] for name in ("prefixes", "status_counts", "initial_entries_sha256", "target_answer_counter_trace_sha256")):
                aa_mismatches.append({"fixture_id": curve, "replicate": rep})
    return {"schema": "classical.ecdlp.endpoint-reuse.analysis.v1", "curves": len(curves),
            "replicates_per_curve": 2, "bootstrap_replicates": repetitions,
            "bootstrap_seed": str(seed), "bootstrap_unit": "curve, preserving bothreplicates and allprefixes",
            "aa_counter_mismatches": aa_mismatches, "comparisons": comparisons,
            "scope": "complete ECgroup_addition invocation count only; not a runtime or exponent claim"}

def write_parts(path, rows, byte_limit=60000):
    parts, batch = [], []
    for row in rows:
        candidate = batch + [row]
        raw = json.dumps(candidate, separators=(",", ":"), allow_nan=False).encode() + b"\n"
        if len(raw) > byte_limit and batch:
            parts.append(batch)
            batch = [row]
        else:
            batch = candidate
    if batch:
        parts.append(batch)
    result = []
    for i, part in enumerate(parts):
        target = path / ("per-cell-" + str(i).zfill(3) + ".json")
        raw = json.dumps(part, separators=(",", ":"), allow_nan=False).encode() + b"\n"
        require(len(raw) <= byte_limit, "one analysis row exceeds part limit")
        target.write_bytes(raw)
        result.append({"path": target.name, "bytes": len(raw), "sha256": sha(target), "rows": len(part)})
    return result

def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ("protocol", "settings", "targets", "raw_manifest", "verification", "out"):
        p.add_argument("--" + key.replace("_", "-"), required=True, type=Path)
    p.add_argument("--external-nonce", required=True)
    args = p.parse_args()
    protocol = read_json(args.protocol)
    require(protocol["freeze"]["status"] == "frozen", "analysis requires an actual prospectively frozen protocol")
    verification = read_json(args.verification)
    require(verification.get("schema") == "classical.ecdlp.endpoint-reuse.public-verification.v1",
            "independent public verification report missing")
    observed = {"target_rows": 0, "witnesses": 0, "statuses": defaultdict(int)}
    def rows_observed_once():
        for row in native_rows(args.raw_manifest):
            if row["row_kind"] == "target":
                observed["target_rows"] += 1
                observed["witnesses"] += row.get("verified_scalar") is not None
                observed["statuses"][row["status"]] += 1
            yield row
    panels_out, duplicates = panels(read_tsv(args.settings), read_tsv(args.targets), rows_observed_once())
    require(verification.get("target_arm_cases") == observed["target_rows"],
            "independent verification target identity coverage differs")
    require(verification.get("verified_case_witnesses") == observed["witnesses"],
            "independent verification final-scalar witness count differs")
    inputs = verification.get("input_sha256", {})
    raw_manifest, raw_streams = raw_files(args.raw_manifest)
    paths = [args.settings, args.targets]
    for item in raw_streams:
        original = args.raw_manifest.parent / item["path"]
        if inputs.get(str(original), inputs.get(str(original.resolve()))) == item["sha256"]:
            continue
        parts = [p for p in raw_manifest["files"] if p["path"].startswith(item["path"] + ".parts/")]
        require(parts, "independent verifier binds neither original nor all exact native parts")
        paths.extend(args.raw_manifest.parent / p["path"] for p in parts)
    for path in paths:
        bound = inputs.get(str(path), inputs.get(str(path.resolve())))
        require(bound == sha(path), "independent verification input binding differs: " + str(path))
    verifier_statuses = {k: v for k, v in verification.get("producer_status_counts", {}).items() if v}
    require(dict(observed["statuses"]) == verifier_statuses, "independent verification source-status counts differ")
    summary = summarize(panels_out, protocol["freeze"]["protocol_sha256"], args.external_nonce)
    summary["independent_verification"] = {"path": str(args.verification), "sha256": sha(args.verification),
                                            "status": verification.get("status"),
                                            "native_cost_counters_verified": False,
                                            "execution_or_isolation_attested": False}
    primary = next(c for c in summary["comparisons"] if c["decisive"])
    summary["primary_panel_eligible"] = verification.get("status") == "public_equations_and_trace_pass" and not summary["aa_counter_mismatches"] and "undefined_reason" not in primary
    summary["duplicate_public_queries"] = duplicates
    args.out.mkdir(parents=True, exist_ok=False)
    parts = write_parts(args.out, panels_out)
    (args.out / "per-cell-index.json").write_text(json.dumps({"files": parts, "rows": len(panels_out)}, indent=2) + "\n")
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n")

if __name__ == "__main__":
    main()
