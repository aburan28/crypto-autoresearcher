#!/usr/bin/env python3
"""Frozen descriptive arithmetic for the reused-input classical parameter sweep.

The counted phases are disjoint: fixture_validation, setup, target deltas.
No event snapshot, nested scalar-multiplication diagnostic or field operation
is added to group_additions. Existing public-verifier reports bind each of nine
native-arm slices. Partial and censored panels remain visible and yield no
success-only paired comparison. This program launches nothing.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import random

VARIANTS = ("dpminus1_cap1", "dpminus1_cap2", "dp0_cap1", "dp0_cap2", "dp0_cap4",
            "dpplus1_cap1", "dpplus1_cap2", "dpplus1_cap4")
BL_ARMS = ("static_small", "static_full", "static_filled", "harvest", "harvest_disabled")
ARM_IDS = tuple(v + "." + a for v in VARIANTS for a in BL_ARMS) + ("shared.rho_reference",)
PREFIXES = (1, 8, 16, 32, 64)
NATIVE_SCHEMA = "classical.ecdlp.endpoint-reuse.row.v1"
NATIVE_SCOPE = "classical_ecdlp_endpoint_reuse"
RAW_SCHEMA = "classical.ecdlp.parameter-sweep.raw-manifest/v1"
CHILD_SCHEMA = "classical.ecdlp.parameter-sweep.child-execution/v1"
FAMILIES = ("counters", "auxiliary_work", "upstream_stats", "rng", "fill", "reuse", "memory")
STATE_FIELDS = ("known_count", "pending_count", "endpoint_cap", "accepted_count", "precompute_reported_ops_total", "table_state_hash64")


def require(value, message):
    if not value:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path):
    def unique(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key: " + key)
            result[key] = value
        return result
    return json.loads(Path(path).read_text(), object_pairs_hook=unique)


def write_json(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, separators=(",", ":"), allow_nan=False)
        stream.write("\n")


def vector(value):
    require(isinstance(value, dict) and "group_additions" in value, "native counter vector/group_additions missing")
    require(all(isinstance(k, str) and k and type(v) is int and v >= 0 for k, v in value.items()),
            "counter vectors require nonnegative exact integers")
    return dict(value)


def add_vectors(left, right):
    return {k: left.get(k, 0) + right.get(k, 0) for k in set(left) | set(right)}


def native_counter_sequences(rows):
    """Losslessly retain integer families as JSON arrays, never a price sum."""
    def fields(value, prefix):
        if isinstance(value, dict):
            for key, child in value.items():
                yield from fields(child, prefix + "." + key)
        elif type(value) is int:
            yield prefix, value
    sequences = defaultdict(list)
    for row in rows:
        kind = row["row_kind"]
        for family in FAMILIES:
            for key, value in fields(row.get(family, {}), "native." + kind + "." + family):
                sequences[key].append(value)
        for key in STATE_FIELDS:
            if key in row:
                require(type(row[key]) is int, "non-integer native state")
                sequences["native." + kind + ".state." + key].append(row[key])
    return {key: json.dumps(values, separators=(",", ":")) for key, values in sorted(sequences.items())}


def summarize_stream(rows, target_ids, expected_identity, setting=None):
    """Each counted phase contributes exactly once, including all upfront work."""
    validation, setup, answers, initial = [], [], {}, []
    for row in rows:
        require(row.get("schema") == NATIVE_SCHEMA and row.get("scope") == NATIVE_SCOPE,
                "unexpected native row schema/scope")
        require((row.get("cell_id"), row.get("fixture"), row.get("replicate"), row.get("arm")) == expected_identity,
                "native stream identity differs from child metadata")
        kind = row["row_kind"]
        if kind == "fixture_validation":
            validation.append(row)
        elif kind == "setup":
            setup.append(row)
        elif kind == "initial_endpoint":
            initial.append([row["index"], row["fp"], row["exponent"]])
        elif kind == "target":
            i = row["target_ordinal"]
            require(type(i) is int and 0 <= i < len(target_ids) and i not in answers,
                    "duplicate/out-of-range target ordinal")
            require(row["target_id"] == target_ids[i], "target ID differs from sealed child target list")
            answers[i] = row
    require(len(validation) <= 1 and len(setup) <= 1, "duplicate counted validation/setup phase")
    if setting is not None and setup:
        for key in ("dp_bits", "initial_chains", "endpoint_cap", "max_precomp_ops", "max_online_ops", "seed"):
            require(setup[0]["parameters"].get(key) == int(setting[key]), "native setup parameter differs from sealed setting: " + key)
    valid = vector(validation[0]["counters"]) if validation else None
    prepared = vector(setup[0]["counters"]) if setup else None
    fields = set(valid or prepared or {})
    if valid is not None and prepared is not None:
        require(set(valid) == set(prepared), "counter fields changed between disjoint phases")
    total = dict(prepared or {})
    prefixes, solved, statuses, trace = {}, 0, Counter(), []
    contiguous = True
    for i in range(len(target_ids)):
        if i not in answers:
            contiguous = False
            continue
        row = answers[i]
        counts = vector(row["counters"])
        require(not fields or fields == set(counts), "counter fields changed within native stream")
        total = add_vectors(total, counts)
        statuses[row["status"]] += 1
        solved += row["status"] == "solved" and row.get("verified_scalar") is not None
        trace.append([i, row["status"], row.get("verified_scalar"), counts])
        if contiguous and i + 1 in PREFIXES and prepared is not None:
            prefixes[str(i + 1)] = {"solver_api_counters": dict(total),
                                    "full_native_counters": add_vectors(valid, total) if valid is not None else None,
                                    "verified_targets": solved}
    complete = len(validation) == 1 and len(setup) == 1 and set(answers) == set(range(len(target_ids)))
    if validation:
        require(validation[0].get("target_count") == len(target_ids), "upfront validation target count differs")
    return {"validation_counters": valid, "setup_counters": prepared, "prefixes": prefixes,
            "observed_full_native_counters": add_vectors(valid or {}, total),
            "observed_solver_api_counters": total, "output_complete": complete,
            "all_targets_solved": complete and solved == len(target_ids),
            "observed_target_cases": len(answers), "observed_verified_scalar_claims": solved,
            "status_counts": dict(statuses), "native_rows": len(rows),
            "initial_entries_sha256": hashlib.sha256(canonical(initial)).hexdigest(),
            "target_answer_counter_trace_sha256": hashlib.sha256(canonical(trace)).hexdigest()}


def manifest_index(manifest_path, protocol=None):
    manifest_path = Path(manifest_path)
    manifest = read_json(manifest_path)
    require(manifest.get("schema") == RAW_SCHEMA, "unexpected sweep raw-manifest schema")
    if protocol is not None:
        require(manifest["protocol_sha256"] == protocol["freeze"]["protocol_sha256"], "wrong frozen sweep protocol")
    files = {}
    for item in manifest["files"]:
        relative = PurePosixPath(item["path"])
        require(not relative.is_absolute() and ".." not in relative.parts and item["path"] not in files,
                "unsafe/duplicate raw manifest member")
        files[item["path"]] = item
    return manifest, files


def checked_file(root, item):
    path = root / item["path"]
    require(path.is_file() and not path.is_symlink() and path.stat().st_size == item["bytes"] and sha(path) == item["sha256"],
            "raw file bytes/hash differ: " + str(path))
    return path


def read_native(root, files, logical):
    item = files.get(logical)
    require(item is not None, "native logical stream missing from manifest")
    if (root / logical).is_file():
        parts = [item]
    else:
        parts = sorted((v for k, v in files.items() if k.startswith(logical + ".parts/")), key=lambda x: x["path"])
        require(parts, "native original and exact parts unavailable")
    rows, findings, digest, size = [], [], hashlib.sha256(), 0
    for part in parts:
        path = checked_file(root, part)
        with path.open("rb") as stream:
            for number, line in enumerate(stream, 1):
                digest.update(line); size += len(line)
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                    require(isinstance(row, dict), "native row must be a JSON object")
                    rows.append(row)
                except (ValueError, UnicodeError) as error:
                    findings.append({"part": part["path"], "line": number, "error": type(error).__name__})
    require(size == item["bytes"] and digest.hexdigest() == item["sha256"], "native logical stream hash differs")
    return rows, findings, parts


def target_panel(path):
    result = defaultdict(dict)
    with Path(path).open(newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            key = row["fixture_id"], int(row["replicate"])
            i = int(row["target_ordinal"])
            require(i not in result[key], "duplicate public target ordinal")
            result[key][i] = row["target_id"]
    require(len(result) == 128 and len({f for f, _ in result}) == 64, "registered64curves/tworeplicates required")
    require(all(set(v) == set(range(64)) for v in result.values()), "registered64targets per cell required")
    require(len({t for v in result.values() for t in v.values()}) == 8192, "public target IDs are not globally unique")
    return {k: [v[i] for i in range(64)] for k, v in result.items()}


def load_verifications(index_path, root, files, targets_path):
    index_path = Path(index_path)
    index = read_json(index_path)
    require(index.get("schema") == "classical.ecdlp.parameter-sweep.verification-index/v1", "unexpected verification index")
    result = {}
    for entry in index["groups"]:
        variant = entry["variant"]
        require(variant in (*VARIANTS, "shared") and variant not in result, "unplanned/duplicate verification group")
        if entry.get("summary") is None:
            require(entry.get("status")=="not_run" and isinstance(entry.get("reason"),str) and entry["reason"],
                    "absent verifier report needs an explicit not_run observation/reason")
            result[variant]={"summary":{},"path":None,"sha256":None,
                             "binding_findings":["independent verification not run: "+entry["reason"]]}
            continue
        path = Path(entry["summary"])
        if not path.is_absolute():
            path = index_path.parent / path
        require(sha(path) == entry["sha256"], "verification summary hash differs")
        summary = read_json(path)
        require(summary.get("schema") == "classical.ecdlp.endpoint-reuse.public-verification.v1", "old public verifier report required")
        bound = summary.get("input_sha256", {})
        findings = []
        for input_path in (targets_path, root / "panels/fixtures.tsv", root / ("panels/" + variant + "/settings.tsv")):
            if bound.get(str(Path(input_path).resolve()), bound.get(str(input_path))) != sha(input_path):
                findings.append("verification input binding differs: " + str(input_path))
        result[variant] = {"summary": summary, "path": str(path.resolve()), "sha256": entry["sha256"],
                           "binding_findings": findings}
    require(set(result) == set(VARIANTS) | {"shared"}, "allnine independent verification slices required")
    return result


def collect_children(manifest_path, protocol, targets_path, verification_index):
    manifest, files = manifest_index(manifest_path, protocol)
    root = Path(manifest_path).resolve().parent
    targets = target_panel(targets_path)
    verifications = load_verifications(verification_index, root, files, Path(targets_path))
    settings = {}
    for variant in (*VARIANTS,"shared"):
        path=checked_file(root,files["panels/"+variant+"/settings.tsv"])
        with path.open(newline="") as stream:
            table=list(csv.DictReader(stream,delimiter="\t"))
        settings[variant]={r["cell_id"]:r for r in table}
        require(len(table)==128 and len(settings[variant])==128,"variant settings must preserve all128cells")
    seen, children = set(), []
    observed = {v: Counter() for v in (*VARIANTS, "shared")}
    witnesses = Counter(); cases = Counter()
    for group in manifest["groups"]:
        variant, arm = group["variant"], group["arm"]
        arm_id = variant + "." + arm
        pair = group["fixture_id"], group["replicate"]
        key = arm_id, *pair
        require(arm_id in ARM_IDS and group["arm_id"] == arm_id and key not in seen and pair in targets,
                "unplanned/duplicate child identity")
        seen.add(key)
        metadata_path = checked_file(root, files[group["execution"]])
        metadata = read_json(metadata_path)
        require(metadata.get("schema") == CHILD_SCHEMA and metadata["arm_id"] == arm_id
                and metadata["fixture_id"] == pair[0] and metadata["replicate"] == pair[1]
                and metadata["variant_id"] == variant and metadata["arm"] == arm,
                "child metadata/group identity differs")
        require(metadata["attempts"] == group["attempts"] and metadata["status"] == group["status"],
                "child attempt/outcome differs between metadata and complete schedule")
        require(metadata["protocol_sha256"] == manifest["protocol_sha256"]
                and metadata["binary_sha256"] == manifest["binary_sha256"]
                and metadata["source_revision"] == manifest["source_revision"]
                and metadata["source_b_revision"] == manifest["source_b_revision"]
                and metadata["source_c_revision"] == manifest["source_c_revision"], "child source/protocol identity differs")
        require(metadata["target_ids"] == targets[pair], "child did not use the identical registered public target list")
        setting=settings[variant].get(metadata["cell_id"])
        require(setting is not None and setting["fixture_id"]==pair[0] and int(setting["replicate"])==pair[1]
                and metadata["solver_seed"]==int(setting["seed"]),"child setting identity/common public seed differs")
        child = {"arm_id": arm_id, "variant": variant, "arm": arm, "fixture_id": pair[0], "replicate": pair[1],
                 "cell_id": metadata["cell_id"], "execution": group["execution"], "raw": group.get("raw"),
                 "status": metadata["status"], "attempts": metadata["attempts"], "metadata": metadata,
                 "analysis": None, "findings": [], "verification_passed": False}
        if metadata["attempts"] == 1 and group.get("raw") in files:
            try:
                rows, findings, parts = read_native(root, files, group["raw"])
                child["findings"].extend(findings)
                child["analysis"] = summarize_stream(rows, targets[pair],
                    (metadata["cell_id"], pair[0], pair[1], arm),setting)
                bound = verifications[variant]["summary"].get("input_sha256", {})
                original = root / group["raw"]
                if bound.get(str(original.resolve()), bound.get(str(original))) != files[group["raw"]]["sha256"]:
                    for part in parts:
                        p = root / part["path"]
                        if bound.get(str(p.resolve()), bound.get(str(p))) != part["sha256"]:
                            verifications[variant]["binding_findings"].append("verification does not bind native stream/part: " + part["path"])
                observed[variant].update(child["analysis"]["status_counts"])
                witnesses[variant] += child["analysis"]["observed_verified_scalar_claims"]
                cases[variant] += child["analysis"]["observed_target_cases"]
            except (ValueError, OSError, KeyError, TypeError) as error:
                child["findings"].append({"error_type": type(error).__name__, "message": str(error)})
        elif metadata["attempts"] == 1:
            child["findings"].append({"error_type": "MissingNativeStream"})
        children.append(child)
    expected = {(arm, fixture, rep) for arm in ARM_IDS for fixture, rep in targets}
    require(seen == expected, "manifest must preserve all5248planned slots, including zero/unknown attempts")
    for variant, record in verifications.items():
        summary = record["summary"]
        if (summary.get("target_arm_cases") != cases[variant]
                or summary.get("verified_case_witnesses") != witnesses[variant]
                or {k: v for k, v in summary.get("producer_status_counts", {}).items() if v} != dict(observed[variant])):
            record["binding_findings"].append("verification coverage/status/witness counts differ from actual retained streams")
        record["passed"] = summary.get("status") == "public_equations_and_trace_pass" and not record["binding_findings"]
    for child in children:
        child["verification_passed"] = verifications[child["variant"]]["passed"]
        child["verification_status"] = "verified" if child["verification_passed"] else ("not_run" if verifications[child["variant"]]["path"] is None else "error")
    return manifest, files, children, verifications


def quantile(values, q):
    values = sorted(values); x = (len(values) - 1) * q
    a, b = math.floor(x), math.ceil(x)
    return values[a] + (values[b] - values[a]) * (x - a)


def summarize(children, protocol_hash, nonce, repetitions=10000, variants=VARIANTS, expected_curves=64):
    curves = sorted({x["fixture_id"] for x in children})
    require(len(curves) == expected_curves, "incorrect curve-cluster count")
    lookup = {(x["arm_id"], x["fixture_id"], x["replicate"]): x for x in children}
    require(len(lookup) == len(children), "duplicate observed execution identity")
    seed = int.from_bytes(hashlib.sha256("\0".join((protocol_hash, nonce, "parameter_sweep_bootstrap")).encode("ascii")).digest()[:8], "big")
    rng = random.Random(seed)
    indices = [[rng.randrange(len(curves)) for _ in curves] for _ in range(repetitions)]
    aa = []
    for variant in variants:
        for curve in curves:
            for rep in (0, 1):
                a = lookup.get((variant + ".static_small", curve, rep)); b = lookup.get((variant + ".harvest_disabled", curve, rep))
                fields = ("validation_counters", "prefixes", "status_counts", "initial_entries_sha256", "target_answer_counter_trace_sha256")
                if not a or not b or not a["analysis"] or not b["analysis"] or any(a["analysis"][k] != b["analysis"][k] for k in fields):
                    aa.append({"variant": variant, "fixture_id": curve, "replicate": rep})
    comparisons = []
    for variant in variants:
        candidate = variant + ".harvest"
        for baseline in (variant + ".static_small", variant + ".static_full", variant + ".static_filled", "shared.rho_reference"):
            for prefix, metric in ((64, "full_native_group_additions_m64"), *((p, "solver_api_group_additions_m" + str(p)) for p in PREFIXES)):
                ratios, incomplete = [], []
                for curve in curves:
                    values = {}
                    for arm in (candidate, baseline):
                        records = [lookup.get((arm, curve, rep)) for rep in (0, 1)]
                        value = 0
                        for record in records:
                            panel = record and record["analysis"]
                            part = panel and panel["prefixes"].get(str(prefix))
                            if (not record or record["attempts"] != 1 or record["status"] != "completed" or record["findings"]
                                    or not record["verification_passed"] or not panel["all_targets_solved"] or not part
                                    or part["verified_targets"] != prefix):
                                incomplete.append(curve);continue
                            counts = part["full_native_counters"] if metric == "full_native_group_additions_m64" else part["solver_api_counters"]
                            if counts is None:
                                incomplete.append(curve);continue
                            value += counts["group_additions"]
                        values[arm] = value
                    if values[candidate] <= 0 or values[baseline] <= 0:
                        incomplete.append(curve)
                    else:
                        ratios.append(values[candidate] / values[baseline])
                item = {"variant": variant, "candidate": candidate, "baseline": baseline, "metric": metric,
                        "prefix": prefix, "exploratory": True, "incomplete_curves": sorted(set(incomplete))}
                if not incomplete and len(ratios) == len(curves):
                    logs = [math.log(x) for x in ratios]
                    bootstrap = [math.exp(math.fsum(logs[i] for i in row) / len(row)) for row in indices]
                    item.update(curves=len(curves), gmean_ratio=math.exp(math.fsum(logs)/len(logs)),
                                curve_ratio_range=[min(ratios), max(ratios)],
                                pointwise_cluster_bootstrap_ci95=[quantile(bootstrap,.025),quantile(bootstrap,.975)])
                else:
                    item["undefined_reason"] = "Entire paired64curve/tworeplicate panel required; failures/censoring/missing rows are not dropped."
                if any(x["variant"] == variant for x in aa):
                    item.pop("gmean_ratio", None);item.pop("pointwise_cluster_bootstrap_ci95", None)
                    item["undefined_reason"] = "Exact A/A control incomplete or mismatched for this variant."
                comparisons.append(item)
    return {"schema":"classical.ecdlp.parameter-sweep.analysis/v1", "curves":len(curves),
            "replicates_per_curve":2, "bootstrap_replicates":repetitions,"bootstrap_seed":str(seed),
            "bootstrap_unit":"curve, preserving bothreplicates/allprefixes/allvariants/sharedRho covariance",
            "aa_mismatches":aa, "comparisons":comparisons,
            "shared_rho_planned_slots":sum(x["arm_id"]=="shared.rho_reference" for x in children),
            "shared_rho_observation_rows":sum(x["arm_id"]=="shared.rho_reference" and x["attempts"]==1 for x in children),
            "shared_rho_unresolved_slots":sum(x["arm_id"]=="shared.rho_reference" and x["attempts"] is None for x in children),
            "shared_rho_unattempted_slots":sum(x["arm_id"]=="shared.rho_reference" and x["attempts"]==0 for x in children),
            "primary_metric":"full_native_group_additions_m64", "selection_qualification":False,
            "scope":"Exploratory reused-cohort parameter comparisons; no familywise discovery, independent counter replay, qualified clock or exponent inference."}


def write_parts(out, rows, limit=60000):
    parts, batch = [], []
    def flush():
        if not batch:
            return
        path = out / ("per-child-" + str(len(parts)).zfill(4) + ".json")
        data = canonical(batch) + b"\n";require(len(data)<=limit,"one analysis row exceeds part limit")
        path.write_bytes(data);parts.append({"path":path.name,"bytes":len(data),"sha256":sha(path),"rows":len(batch)})
    for row in rows:
        if batch and len(canonical(batch+[row]))+1>limit:
            flush();batch=[]
        batch.append(row)
    flush()
    write_json(out/"per-child-index.json",{"files":parts,"rows":len(rows)})


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("protocol","raw-manifest","verification-index","targets","out"):
        p.add_argument("--"+name,required=True,type=Path)
    p.add_argument("--external-nonce",required=True)
    args=p.parse_args();require(not args.out.exists(),"fresh analysis output directory required")
    protocol=read_json(args.protocol);body={k:v for k,v in protocol.items() if k!="freeze"}
    require(protocol["freeze"]["status"]=="frozen" and hashlib.sha256(canonical(body)).hexdigest()==protocol["freeze"]["protocol_sha256"],"valid frozen protocol required")
    require({x["id"] for x in protocol["arms"]}==set(ARM_IDS),"wrong41-arm protocol")
    require(sha(Path(__file__)) == protocol["analysis_plan"]["script"]["sha256"], "analysis source differs from frozen script")
    config=protocol["extensions"]["parameter_sweep"]
    require(args.external_nonce==config.get("public_nonce_hex",config.get("original_nonce_hex")),"bootstrap nonce differs from frozen reused-public nonce")
    manifest,files,children,verifications=collect_children(args.raw_manifest,protocol,args.targets,args.verification_index)
    summary=summarize(children,protocol["freeze"]["protocol_sha256"],args.external_nonce)
    summary["flow"]=manifest["flow"]
    summary["verification_slices"]={v:{k:r[k] for k in ("path","sha256","passed","binding_findings")} for v,r in verifications.items()}
    summary["native_counter_replay_verified"]=False;summary["all_clocks_wall_valid"]=False
    summary["protocol_sha256"]=protocol["freeze"]["protocol_sha256"]
    summary["input_bindings"]={str(x.resolve()):sha(x) for x in (args.raw_manifest,args.verification_index,args.targets)}
    args.out.mkdir(parents=True)
    write_parts(args.out,[{k:v for k,v in child.items() if k!="metadata"} for child in children])
    write_json(args.out/"summary.json",summary)
    print(json.dumps({"planned_child_slots":len(children),"actual_confirmed_children":sum(x["attempts"]==1 for x in children),"shared_rho_rows":summary["shared_rho_observation_rows"],"aa_mismatches":len(summary["aa_mismatches"]),"comparisons":len(summary["comparisons"])}))


if __name__=="__main__":
    main()
