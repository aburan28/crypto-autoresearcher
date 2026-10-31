#!/usr/bin/env python3
"""Execute the fixed exploratory parameter panel with the unchanged native A.

The original public cohort is verified by its unchanged source-A reader. Its
source protocol identity remains distinct from this sweep's frozen protocol.
Native launches, wait4 collection, stream shape checks and splitting reuse the
source-pinned helpers. No native result is retried or selected by its outcome.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path, PurePosixPath
import random
import re
import signal
import sys
import time

SOURCE_A = "fe01ccd832832488c58abeef17548b0a8db6035f"
IMAGE_ADAPTER_B = "de6ed88850fc8bad17ccbabfad8b66a791e478e5"
OLD_PROTOCOL = "c2c74431575058b141bc6a49dda895e87f59a2ea2c77b9db6635960ad7c480b1"
BL_ARMS = ("static_small", "static_full", "static_filled", "harvest", "harvest_disabled")
VARIANTS = (("dpminus1_cap1", -1, 1), ("dpminus1_cap2", -1, 2),
            ("dp0_cap1", 0, 1), ("dp0_cap2", 0, 2), ("dp0_cap4", 0, 4),
            ("dpplus1_cap1", 1, 1), ("dpplus1_cap2", 1, 2), ("dpplus1_cap4", 1, 4))
PREFIXES = (1, 8, 16, 32, 64)
FIXTURE_COLUMNS = ("fixture_id", "stratum", "p", "a", "b", "gx", "gy", "r", "N", "seed")
TARGET_COLUMNS = ("fixture_id", "replicate", "target_id", "target_ordinal", "qx", "qy", "infinity")
SETTING_COLUMNS = ("cell_id", "fixture_id", "replicate", "dp_bits", "initial_chains", "endpoint_cap",
                   "max_precomp_ops", "max_online_ops", "seed")
HEX = re.compile(r"[0-9a-f]{64}\Z")
REV = re.compile(r"[0-9a-f]{40}\Z")
REUSED = {
    "execution/run_experiment.py": "e2f03b383fa9a21e984b8648e3700db7834954e26f3f30e86b7addf2f5b2f48d",
    "cohort/public_inputs.py": "2577dd4568efd53e4b74150e5b8b0f0a5767d240d471f0110e0b1d178b750829",
    "protocol/seed_rules.py": "d1348c404cf9c7a90d7c70abf7f23797ac49c132b555f75f3065f9fc92421b4c",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sha_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def read_json(path):
    def unique(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    value = json.loads(Path(path).read_text(), object_pairs_hook=unique)
    require(isinstance(value, dict), "JSON object required")
    return value


def write_json(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def table_bytes(columns, rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=columns, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


def protocol_read(path):
    protocol = read_json(path)
    require(protocol.get("schema") == "experiment.protocol/v1", "official experiment protocol required")
    actual = digest(canonical({k: v for k, v in protocol.items() if k != "freeze"}))
    freeze = protocol.get("freeze", {})
    require(freeze.get("status") == "frozen" and freeze.get("protocol_sha256") == actual
            and freeze.get("filed_before_affected_data") is True, "changed or unfrozen sweep protocol")
    require(protocol.get("protocol_id") == "EXP-ECDLP-f50061", "wrong sweep experiment")
    config = protocol.get("extensions", {}).get("parameter_sweep", {})
    observed = tuple((x.get("id"), x.get("dp_shift"), x.get("cap_multiplier")) for x in config.get("variants", []))
    require(observed == VARIANTS and tuple(config.get("bl_arms", [])) == BL_ARMS
            and tuple(config.get("prefixes", [])) == PREFIXES, "sweep grid/arms/prefixes differ from fixed design")
    require(config.get("source_input_protocol_sha256") == OLD_PROTOCOL
            and config.get("expected_cells") == 128 and config.get("targets_per_cell") == 64,
            "explicit original public-panel reuse binding required")
    require(HEX.fullmatch(config.get("source_manifest_sha256", "")) is not None,
            "frozen staged-source manifest SHA required")
    execution = protocol["execution"]
    placement = execution["placement"]
    require(execution.get("backend") == "modal" and execution.get("measurement_class") == "measurement"
            and execution["checkpoint"]["policy"] == "none" and execution["retries"]["max_attempts"] == 1,
            "count-primary Modal/no-restore/no-retry execution required")
    require(placement.get("runtime") == "vm" and placement.get("block_network") is True,
            "network-blocked VM placement required")
    for seconds in (execution["timeout_seconds"], placement["child_timeout_seconds"]):
        require(type(seconds) in (int, float) and math.isfinite(seconds) and seconds > 0,
                "positive finite operational watchdog required")
    return protocol, actual


def source_and_context(source_path, context_path, protocol, protocol_hash, inputs_hash, binary):
    manifest, context = read_json(source_path), read_json(context_path)
    require(manifest.get("schema") == "classical.ecdlp.parameter-sweep.source-manifest/v1",
            "sweep source manifest required")
    require(context.get("schema") == "classical.ecdlp.parameter-sweep.modal-provider-context/v1"
            and context.get("provider") == "modal", "actual Modal controller context required")
    require(sha_file(source_path) == context.get("source_manifest_sha256")
            == protocol["extensions"]["parameter_sweep"]["source_manifest_sha256"],
            "staged source-manifest identity differs from protocol/context")
    require(protocol["extensions"]["parameter_sweep"].get("inputs_manifest_sha256") == inputs_hash,
            "public-panel manifest differs from the new frozen protocol")
    require(REV.fullmatch(manifest.get("source_revision_c", "")) is not None
            and manifest["source_revision_c"] == context.get("source_revision_c"),
            "actual committed sweep source C identity required")
    root = Path(source_path).resolve().parent
    files = manifest.get("files")
    require(isinstance(files, dict) and "engine.py" in files, "complete staged source file map required")
    for relative, expected in files.items():
        rel = PurePosixPath(relative)
        require(not rel.is_absolute() and ".." not in rel.parts and str(rel) == relative
                and HEX.fullmatch(expected or "") is not None, "unsafe source path/hash")
        path = root / relative
        require(not path.is_symlink() and path.resolve().is_relative_to(root)
                and sha_file(path) == expected, "staged source bytes differ: " + relative)
    require(Path(__file__).resolve() == root / "engine.py" and sha_file(__file__) == files["engine.py"],
            "executing engine differs from committed staged source")
    require({p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
            == set(files) | {Path(source_path).name}, "unbound staged source files")
    for path in [root, *root.rglob("*")]:
        require(not path.is_symlink() and not os.access(path, os.W_OK), "source must be immutable to workload UID")
    require(context.get("runtime") == "vm" and context.get("block_network") is True
            and context.get("requested_cpu") == [2, 2]
            and context.get("requested_memory_mib") == [12288, 12288], "actual registered VM resources required")
    for key, prefix in (("app_id", "ap"), ("sandbox_id", "sb"), ("image_id", "im")):
        require(re.fullmatch(prefix + r"-[A-Za-z0-9]+", context.get(key, "")) is not None,
                "actual SDK object identity required: " + key)
        declared = protocol["execution"]["placement"].get(key)
        if key != "sandbox_id":
            require(declared == context[key], "frozen provider identity differs: " + key)
    for key, expected in (("source_revision", SOURCE_A), ("source_a_revision", SOURCE_A),
                          ("source_b_revision", IMAGE_ADAPTER_B), ("adapter_revision", IMAGE_ADAPTER_B),
                          ("protocol_sha256", protocol_hash), ("source_input_protocol_sha256", OLD_PROTOCOL),
                          ("inputs_manifest_sha256", inputs_hash)):
        require(context.get(key) == expected, "provider context differs: " + key)
    for field, context_field, expected in (("native_source_a", "source_a_revision", SOURCE_A),
                                           ("image_adapter_source_b", "source_b_revision", IMAGE_ADAPTER_B),
                                           ("binary_sha256", "binary_sha256", sha_file(binary)),
                                           ("build_info_sha256", "build_info_sha256", None),
                                           ("adapter_manifest_sha256", "adapter_manifest_sha256", None)):
        require(HEX.fullmatch(manifest.get(field, "")) is not None if field.endswith("sha256") else True,
                "source manifest identity missing: " + field)
        require(manifest.get(field) == context.get(context_field)
                and (expected is None or manifest[field] == expected), "image/source manifest differs: " + field)
    return manifest, context


def load_helpers(context, binary, study_root=Path("/opt/study")):
    """Reuse the image's immutable A helpers and B2 build verifier unchanged."""
    study_root = Path(study_root).resolve()
    for relative, expected in REUSED.items():
        require(sha_file(study_root / relative) == expected, "source-A helper differs: " + relative)
    sys.path.insert(0, str(study_root))
    spec = importlib.util.spec_from_file_location("parameter_sweep_image_adapter", study_root / "modal/engine.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.verify_build(context, binary, root=study_root)
    return module


def derive_setting(base, fixture, variant_id, dp_shift, cap_multiplier):
    r = int(fixture["r"])
    dp = r.bit_length() // 3 + dp_shift
    require(0 <= dp <= 20 and cap_multiplier in (1, 2, 4), "unsupported prospective setting")
    divisor = 1 << (2 * dp)
    initial = (r + divisor // 2) // divisor
    cap = cap_multiplier * initial
    require(1 <= initial <= cap <= r, "native arena/initial-chain guard would be violated")
    root = math.isqrt(r)
    return {**base, "cell_id": base["cell_id"] + "--" + variant_id,
            "dp_bits": dp, "initial_chains": initial, "endpoint_cap": cap,
            "max_precomp_ops": 256 * cap * (1 << dp) + 8192,
            "max_online_ops": 256 * (root + (root * root < r)) + 8192}


def seed(protocol_hash, nonce, cell, purpose):
    return int.from_bytes(hashlib.sha256(b"classical.ecdlp.parameter-sweep.v1\0" + b"\0".join(
        x.encode("ascii") for x in (protocol_hash, nonce, cell, purpose))).digest()[:8], "big")


def build_schedule(cohort, protocol_hash):
    cells = sorted(cohort.settings)
    random.Random(seed(protocol_hash, cohort.nonce_hex, "cohort", "cell_order")).shuffle(cells)
    schedule = []
    for cell in cells:
        slots = [(variant, arm) for variant, _, _ in VARIANTS for arm in BL_ARMS] + [("shared", "rho_reference")]
        random.Random(seed(protocol_hash, cohort.nonce_hex, cell, "slot_order")).shuffle(slots)
        schedule.extend((cell, variant, arm) for variant, arm in slots)
    return schedule


def write_slices(out, cohort, base_cell, setting, helper):
    require(not out.exists(), "fresh derived cell slices required")
    out.mkdir(parents=True)
    tables = (("fixtures.tsv", FIXTURE_COLUMNS, [cohort.fixtures[setting["fixture_id"]]]),
              ("targets.tsv", TARGET_COLUMNS, cohort.targets[base_cell]),
              ("settings.tsv", SETTING_COLUMNS, [setting]))
    result = {}
    for name, columns, rows in tables:
        data = table_bytes(columns, rows)
        with (out / name).open("xb") as stream:
            stream.write(data)
        result[name] = {"path": str((out / name).resolve()), "bytes": len(data),
                        "sha256": digest(data), "rows": len(rows)}
    return result


def target_status_counts(path):
    counts = Counter()
    with Path(path).open() as stream:
        for line in stream:
            row = json.loads(line)
            if row.get("row_kind") == "target":
                counts[str(row.get("status", "missing_status"))] += 1
    return dict(sorted(counts.items()))


def execute(args, protocol, protocol_hash, cohort, manifest, context, helper):
    schedule = build_schedule(cohort, protocol_hash)
    require(len(cohort.settings) == 128 and len(schedule) == 5248 and len(set(schedule)) == 5248,
            "complete registered 128-cell/41-arm schedule required")
    require(not args.out.exists(), "fresh output directory required")
    args.out.mkdir(parents=True)
    for name, path in (("launch-protocol-bytes.json", args.protocol),
                       ("launch-provider-context-bytes.json", args.provider_context),
                       ("launch-source-manifest-bytes.json", args.source_manifest),
                       ("source-public-inputs-manifest.json", args.public_root / "inputs-manifest.json")):
        (args.out / name).write_bytes(Path(path).read_bytes())
    write_json(args.out / "schedule.json", {"schema": "classical.ecdlp.parameter-sweep.schedule/v1",
               "protocol_sha256": protocol_hash, "source_input_protocol_sha256": cohort.protocol_sha256,
               "inputs_manifest_sha256": args.inputs_manifest_sha256,
               "order_law": "SHA256-domainseed/newprotocol/publicnonce shuffles base cells, then all41 variant-arm slots within each basecell; solver seeds unchanged from original public settings",
               "slots": [{"base_cell_id": c, "variant_id": v, "arm": a,
                          "arm_id": v + "." + a, "cell_id": c + "--" + v} for c, v, a in schedule]})
    variants = {v: (shift, cap) for v, shift, cap in VARIANTS}
    variants["shared"] = (0, 4)
    settings = {(cell, variant): derive_setting(base, cohort.fixtures[base["fixture_id"]], variant, *rule)
                for cell, base in cohort.settings.items() for variant, rule in variants.items()}
    for variant in variants:
        folder = args.out / "panels" / variant
        folder.mkdir(parents=True)
        data = table_bytes(SETTING_COLUMNS, [settings[cell, variant] for cell in sorted(cohort.settings)])
        (folder / "settings.tsv").write_bytes(data)
    (args.out / "panels/fixtures.tsv").write_bytes((args.public_root / "fixtures.tsv").read_bytes())
    timeout = float(protocol["execution"]["placement"]["child_timeout_seconds"])
    deadline = time.monotonic() + float(protocol["execution"]["timeout_seconds"])
    records, slices, unresolved_paths = [], {}, set()
    launch_stop = None
    for ordinal, (base_cell, variant, arm) in enumerate(schedule):
        setting = settings[base_cell, variant]
        cell = setting["cell_id"]
        dest = args.out / "cells" / cell / arm
        dest.mkdir(parents=True)
        record = {"schema": "classical.ecdlp.parameter-sweep.child-execution/v1", "ordinal": ordinal,
                  "base_cell_id": base_cell, "cell_id": cell, "variant_id": variant,
                  "arm": arm, "native_arm": arm, "arm_id": variant + "." + arm,
                  "fixture_id": setting["fixture_id"], "replicate": int(setting["replicate"]),
                  "solver_seed": int(setting["seed"]), "setting": setting,
                  "source_revision": SOURCE_A, "source_b_revision": IMAGE_ADAPTER_B,
                  "source_c_revision": manifest["source_revision_c"], "binary_sha256": manifest["binary_sha256"],
                  "protocol_sha256": protocol_hash, "source_input_protocol_sha256": cohort.protocol_sha256,
                  "inputs_manifest_sha256": args.inputs_manifest_sha256,
                  "backend": "modal", "runtime": "vm",
                  "provider_identity": {k: context[k] for k in ("app_id", "sandbox_id", "image_id")},
                  "target_ids": [t["target_id"] for t in cohort.targets[base_cell]],
                  "retries": 0, "resumed": False, "attempts": 0,
                  "native_spawn_observation": "not_started", "started_at": None, "finished_at": None}
        if launch_stop or helper.STOP["signal"] is not None or time.monotonic() >= deadline:
            reason = launch_stop or ("interrupted" if helper.STOP["signal"] else "global_timeout")
            record.update(status="not_attempted", reason=reason, argv=None, exitcode=None,
                          rusage=None, clock={"wall_valid": False})
        else:
            raw, stdout, stderr = dest / "raw.jsonl", dest / "stdout.log", dest / "stderr.log"
            try:
                key = base_cell, variant
                if key not in slices:
                    slices[key] = write_slices(args.out / "inputs" / cell, cohort, base_cell, setting, helper)
                files = slices[key]
                argv = [str(args.binary.resolve()), "--run", files["fixtures.tsv"]["path"],
                        files["targets.tsv"]["path"], files["settings.tsv"]["path"], arm, str(raw.resolve())]
                record.update(argv=argv, input_slices=files, host_before=helper.host_facts(context),
                              raw_output=raw.relative_to(args.out).as_posix(),
                              stdout=stdout.relative_to(args.out).as_posix(),
                              stderr=stderr.relative_to(args.out).as_posix(), timeout_seconds=timeout)
                record["native_call_started_at"] = helper.utc()
                record["attempts"] = None
                record["native_spawn_observation"] = "unresolved"
                record.update(helper.wait_child(argv, stdout, stderr, timeout, deadline))
                record["native_spawn_observation"] = "wait4_reaped_child"
                require(record["clock"]["wall_valid"] is False, "no clock qualification is supplied")
                for item in files.values():
                    require(Path(item["path"]).stat().st_size == item["bytes"]
                            and sha_file(item["path"]) == item["sha256"], "native public input slice changed")
                if record["termination_reason"]:
                    record["status"] = "interrupted" if record["termination_reason"] == "interrupted" else "timed_out"
                elif record["exitcode"]:
                    record["status"] = "native_nonzero"
                else:
                    try:
                        record["shape_check"] = helper.shape_check(raw, cell, setting, arm, cohort.targets[base_cell])
                        native_summary = read_json(stdout)
                        require(native_summary.get("cells") == 1 and native_summary.get("targets") == 64
                                and native_summary.get("rows") == record["shape_check"]["raw_rows"]
                                and native_summary.get("clocks_emitted") is False,
                                "native stdout summary differs from its complete clock-free raw stream")
                        record["native_summary"] = native_summary
                        record["target_status_counts"] = target_status_counts(raw)
                        require(sum(record["target_status_counts"].values()) == 64, "wrong actual target-row coverage")
                        record["status"] = "completed"
                    except (OSError, ValueError, KeyError, TypeError) as error:
                        record.update(status="invalid_output", shape_error={"type": type(error).__name__, "message": str(error)})
            except Exception as error:
                record.update(status="infra_error", error={"type": type(error).__name__, "message": str(error)})
                if record["native_spawn_observation"] == "unresolved":
                    launch_stop = "unresolved_native_spawn_requires_supervisor_quiescence"
                    unresolved_paths.update(p.relative_to(args.out).as_posix() for p in (raw, stdout, stderr))
            try:
                record["host_after"] = helper.host_facts(context)
            except Exception as error:
                record["host_after_error"] = {"type": type(error).__name__, "message": str(error)}
            if raw.exists() and record["native_spawn_observation"] == "wait4_reaped_child":
                try:
                    record["raw_parts"] = helper.split_stream(raw, args.out)
                except Exception as error:
                    record["raw_archival_error"] = {"type": type(error).__name__, "message": str(error)}
        record.setdefault("exitcode", None)
        record.setdefault("rusage", None)
        record.setdefault("clock", {"wall_valid": False})
        write_json(dest / "execution.json", record)
        records.append(record)
        if (ordinal + 1) % 128 == 0:
            print(json.dumps({"completed_slots": ordinal + 1, "planned_slots": len(schedule),
                              "confirmed_children": sum(r["attempts"] == 1 for r in records),
                              "native_spawn_unresolved": sum(r["attempts"] is None for r in records)}), flush=True)
    target_counts = Counter()
    for record in records:
        target_counts.update(record.get("target_status_counts", {}))
    summary = {"schema": "classical.ecdlp.parameter-sweep.execution-summary/v1",
               "planned": len(schedule), "planned_target_arm_cases": len(schedule) * 64,
               "attempted": sum(r["attempts"] == 1 for r in records),
               "attempts_unresolved": sum(r["attempts"] is None for r in records),
               "completed": sum(r["status"] == "completed" for r in records),
               "status_counts": dict(sorted(Counter(r["status"] for r in records).items())),
               "actual_target_status_counts": dict(sorted(target_counts.items())),
               "launch_stop_reason": launch_stop, "protocol_sha256": protocol_hash,
               "source_input_protocol_sha256": cohort.protocol_sha256,
               "inputs_manifest_sha256": args.inputs_manifest_sha256,
               "public_target_ids": 8192, "shared_rho_children_planned": 128,
               "rho_reference_reused_as_new_observations": False,
               "all_clocks_wall_valid": False, "independent_public_equation_verification": False,
               "native_counter_replay_verified": False, "scientific_review": False}
    write_json(args.out / "summary.json", summary)
    raw_manifest = {"schema": "classical.ecdlp.parameter-sweep.raw-manifest/v1",
                    "protocol_sha256": protocol_hash, "source_input_protocol_sha256": cohort.protocol_sha256,
                    "inputs_manifest_sha256": args.inputs_manifest_sha256,
                    "source_revision": SOURCE_A, "source_b_revision": IMAGE_ADAPTER_B,
                    "source_c_revision": manifest["source_revision_c"], "binary_sha256": manifest["binary_sha256"],
                    "flow": summary, "complete_native_index": not unresolved_paths,
                    "unresolved_mutable_paths": sorted(unresolved_paths),
                    "groups": [{"variant": r["variant_id"], "arm": r["arm"], "arm_id": r["arm_id"],
                                "fixture_id": r["fixture_id"], "replicate": r["replicate"],
                                "base_cell_id": r["base_cell_id"], "cell_id": r["cell_id"],
                                "execution": "cells/" + r["cell_id"] + "/" + r["arm"] + "/execution.json",
                                "raw": r.get("raw_output"), "status": r["status"], "attempts": r["attempts"],
                                "native_spawn_observation": r["native_spawn_observation"],
                                "settings": "panels/" + r["variant_id"] + "/settings.tsv"} for r in records],
                    "files": [{"path": p.relative_to(args.out).as_posix(), "bytes": p.stat().st_size,
                               "sha256": sha_file(p)} for p in sorted(args.out.rglob("*"))
                              if p.is_file() and p.relative_to(args.out).as_posix() not in unresolved_paths]}
    write_json(args.out / "algorithm-raw-manifest.json", raw_manifest)
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("public-root", "protocol", "source-manifest", "provider-context", "binary", "out"):
        parser.add_argument("--" + name, required=True, type=Path)
    parser.add_argument("--inputs-manifest-sha256", required=True)
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args(argv)
    require(os.getuid() == os.geteuid() == os.getgid() == os.getegid() == 1000
            and not os.getgroups(), "reserved unprivileged workload identity required")
    protocol, protocol_hash = protocol_read(args.protocol)
    manifest, context = source_and_context(args.source_manifest, args.provider_context, protocol,
                                           protocol_hash, args.inputs_manifest_sha256, args.binary)
    helper = load_helpers(context, args.binary)
    cohort = helper.load_inputs(args.public_root, args.inputs_manifest_sha256)
    require(cohort.protocol_sha256 == OLD_PROTOCOL, "source public panel identity changed")
    schedule = build_schedule(cohort, protocol_hash)
    if args.plan_only:
        print(json.dumps({"planned_children": len(schedule), "target_arm_cases": len(schedule) * 64,
                          "source_input_protocol_sha256": cohort.protocol_sha256,
                          "new_protocol_sha256": protocol_hash, "measurement_started": False}))
        return 0
    for signum in (signal.SIGTERM, signal.SIGINT):
        signal.signal(signum, lambda number, frame: helper.STOP.update(signal=number))
    summary = execute(args, protocol, protocol_hash, cohort, manifest, context, helper)
    print(json.dumps(summary), flush=True)
    return 0 if summary["completed"] == summary["planned"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
