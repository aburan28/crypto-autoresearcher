#!/usr/bin/env python3
"""Exercise the admitted per-candidate failure contract without GP or scanning."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_sibling(name: str):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load frozen sibling module {name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


pipeline = load_sibling("pipeline")
run_scan = load_sibling("run_scan")


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def endpoint_certificate(
    hit: pipeline.Hit, status: str, **overrides: object
) -> dict[str, str]:
    values: dict[str, str] = {
        "schema": "m51-deep-endpoint-certificate/v1",
        "global_index": str(hit.global_index),
        "source_b": str(hit.b),
        "source_a2": "0",
        "source_order": str(run_scan.AMBIENT_ORDER),
        "source_orbit_rep": str(hit.b),
        "source_orbit_size": "51",
        "source_to_orbit_rep_frobenius_power": "0",
        "expected_order": str(run_scan.AMBIENT_ORDER),
        "field_degree": str(run_scan.FIELD_BITS),
        "field_modulus_bits": str((1 << 51) + (1 << 6) + (1 << 3) + 2 + 1),
        "class_trace": str((1 << 51) + 1 - run_scan.AMBIENT_ORDER),
        "class_discriminant": str(-7 * run_scan.F_PI**2),
        "f_pi": str(run_scan.F_PI),
        "f_pi_factorization": "271*120871",
        "f_pi_factor_primality": "1",
        "class_discriminant_271_valuation": "2",
        "kernel_extension_coprime_to_271": "1",
        "maximal_order_class_number": "1",
        "f271_census_sha256": pipeline.CENSUS_SHA256,
        "f271_census_source_revision": run_scan.CENSUS_SOURCE_REVISION,
        "f271_census_source_sha256": run_scan.CENSUS_SOURCE_SHA256,
        "f271_census_complete_orbit_count": "16",
        "control_mode": "0",
        "admitted_failure": "0",
    }
    values.update({key: str(value) for key, value in overrides.items()})
    values["status"] = status
    return values


def write_endpoint(path: Path, certificate: dict[str, str]) -> None:
    body = "".join(
        f"{key}={value}\n"
        for key, value in certificate.items()
        if key != "status"
    )
    path.write_text(body + f"status={certificate['status']}\n")


def main() -> int:
    hit = pipeline.Hit(global_index=7, b=11, x0=13, x1=17, x2=19)
    job = pipeline.Job(
        label="contract-failure",
        hit=hit,
        source_seed=23,
        target_seed=29,
        control_mode=0,
    )
    with tempfile.TemporaryDirectory(prefix="m51-harness-contract-") as raw_tmp:
        snapshots = Path(raw_tmp) / "snapshots"
        snapshots.mkdir()
        frozen_entries: dict[str, str] = {}
        frozen_lines: list[str] = []
        for name in ("classify_recover.gp", "floor271_orbits.csv"):
            source = HERE / name
            target = snapshots / name
            target.write_bytes(source.read_bytes())
            frozen_entries[name] = run_scan.sha256_file(target)
            frozen_lines.append(f"{frozen_entries[name]}  {name}\n")
        frozen_manifest = "".join(frozen_lines)
        (snapshots / "FROZEN.sha256").write_text(frozen_manifest)
        payload = Path(raw_tmp) / "payload"
        certificates = payload / "certificates"
        partials = payload / "partials"
        certificates.mkdir(parents=True)
        partials.mkdir()
        certificate = certificates / "0000-rank-0000000007.kv"
        (partials / certificate.name).write_text("rejected test certificate\n")
        pipeline.failure_certificate(
            certificate,
            job,
            "certificate_rejected:selftest",
            hashlib.sha256(b"\0").hexdigest(),
        )
        source = hit.binding()
        relative = certificate.relative_to(payload).as_posix()
        record = {
            "schema": "m51-deep-classification-record/v1",
            **source,
            "source_hit": source,
            "status": "GP_ERROR",
            "admitted_failure": True,
            "control_mode": 0,
            "certificate_path": relative,
            "certificate_sha256": run_scan.sha256_file(certificate),
            "certificate_bytes": certificate.stat().st_size,
        }
        (payload / "records.jsonl").write_text(
            json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n"
        )
        (payload / "pairs.jsonl").write_text("")
        selection = {
            "schema": run_scan.SELECTION_SCHEMA,
            "target_pairs": run_scan.TARGET_PAIRS,
            "selected_count": 0,
            "selected": [],
            "valid": False,
            "cutoff_global_index": None,
            "blocking_failures": [record],
            "provisional_selected": [],
            "rule": "first eligible distinct parent orbit in global-index order; no outcome backfill",
        }
        write_json(payload / "selection.json", selection)
        driver_rows = [[
            hit.global_index,
            hit.b,
            run_scan.derive_endpoint_seed(
                b"m51-deep-scan/v1/source-witness", source
            ),
            run_scan.derive_endpoint_seed(
                b"m51-deep-scan/v1/target-rank2", source
            ),
            0,
            relative,
        ]]
        (payload / "driver.gp").write_text(
            f"EMBED_SEED={run_scan.EMBED_SEED};\n"
            f"WITNESS_COUNT={run_scan.WITNESS_COUNT};\n"
            f"MAX_WITNESS_ATTEMPTS={run_scan.MAX_WITNESS_ATTEMPTS};\n"
            f"BATCH_ROWS={json.dumps(driver_rows, separators=(',', ':'))};\n"
            f"read({json.dumps(str((snapshots / 'classify_recover.gp').resolve()))});\n"
        )
        (payload / "gp.stdout").write_bytes(b"")
        (payload / "gp.stderr").write_bytes(b"")
        empty_hash = hashlib.sha256(b"").hexdigest()
        fake_gp = Path(raw_tmp) / "gp-2.15"
        runtime = {
            "schema": "m51-deep-gp-runtime/v1",
            "mode": "extracted-binary",
            "gp_binary": str(fake_gp.resolve()),
            "gp_binary_sha256": run_scan.PINNED_GP_BINARY_SHA256,
            "source_image_content_id": run_scan.PINNED_GP_IMAGE_ID,
            "command": [str(fake_gp.resolve()), "-q", "-f", "-s", run_scan.GP_STACK],
            "environment": run_scan.GP_CHILD_ENV,
            "exit_status": 0,
            "stdout_sha256": empty_hash,
            "stderr_sha256": empty_hash,
            "global_failure": False,
            "shared_extension_initialization": True,
            "gp_stack": run_scan.GP_STACK,
            "classifier_sha256": run_scan.sha256_file(snapshots / "classify_recover.gp"),
            "census_sha256": run_scan.sha256_file(snapshots / "floor271_orbits.csv"),
        }
        write_json(payload / "runtime.json", runtime)
        gp_runtime = {"kind": "binary", "path": str(fake_gp)}
        records, pairs = run_scan.validate_classification_payload(
            payload,
            [source],
            snapshots,
            gp_runtime,
        )
        if records != [record] or pairs:
            raise RuntimeError("admitted-failure contract returned unexpected rows")
        string_typed_source = dict(source)
        string_typed_source["global_index"] = str(hit.global_index)
        try:
            run_scan.parse_source_hit(string_typed_source, "string-typed source")
        except run_scan.RunError:
            pass
        else:
            raise RuntimeError("generated JSON accepted a decimal string as an integer")

        for label, validator, expected_error in (
            (
                "pipeline-success/fatal-full",
                lambda value, degree: pipeline.validate_codomain_minpoly_bits(
                    value, degree
                ),
                pipeline.PipelineError,
            ),
            (
                "runner-success/fatal-full",
                lambda value, degree: run_scan.validate_codomain_minpoly_bits(
                    value, degree, "minpoly regression"
                ),
                run_scan.RunError,
            ),
        ):
            validator(0b11, 1)
            validator((1 << 51) | 1, 51)
            for bad_value, bad_degree in (
                (1 << 500, 51),
                ((1 << 500) | 1, 51),
                ((1 << 17) | 1, 51),
                (1 << 51, 51),
            ):
                try:
                    validator(bad_value, bad_degree)
                except expected_error:
                    pass
                else:
                    raise RuntimeError(
                        f"{label} accepted invalid codomain minimal polynomial"
                    )

        orphan = payload / "orphan-evidence"
        orphan.write_text("not admitted\n")
        try:
            run_scan.validate_classification_payload(
                payload, [source], snapshots, gp_runtime
            )
        except run_scan.RunError:
            pass
        else:
            raise RuntimeError("pipeline payload accepted an orphan evidence file")
        orphan.unlink()
        driver_path = payload / "driver.gp"
        admitted_driver = driver_path.read_bytes()
        driver_path.write_bytes(admitted_driver + b"\\ extra GP input\n")
        try:
            run_scan.validate_classification_payload(
                payload, [source], snapshots, gp_runtime
            )
        except run_scan.RunError:
            pass
        else:
            raise RuntimeError("pipeline payload accepted a changed GP driver")
        driver_path.write_bytes(admitted_driver)

        adversarial = [
            endpoint_certificate(
                hit,
                "SIEVE_FALSE_POSITIVE_ORDER",
                source_order=run_scan.AMBIENT_ORDER,
            ),
            endpoint_certificate(
                hit,
                "SIEVE_FALSE_POSITIVE_ORDER",
                source_order=-1,
            ),
            endpoint_certificate(
                hit,
                "SIEVE_FALSE_POSITIVE_ORDER",
                source_order=2,
            ),
            endpoint_certificate(
                hit,
                "SIEVE_FALSE_POSITIVE_ORDER",
                source_order=1 << 500,
            ),
            endpoint_certificate(
                hit,
                "SIEVE_FALSE_POSITIVE_ORDER",
                source_order=run_scan.HASSE_MIN - 1,
            ),
            endpoint_certificate(
                hit,
                "SIEVE_FALSE_POSITIVE_ORDER",
                source_order=run_scan.HASSE_MAX + 1,
            ),
            endpoint_certificate(
                hit,
                "SIEVE_FALSE_POSITIVE_ORDER",
                source_order=run_scan.AMBIENT_ORDER - 1,
            ),
            endpoint_certificate(
                hit,
                "SIEVE_FALSE_POSITIVE_ORDER",
                source_order=run_scan.HASSE_MIN,
                source_orbit_rep=1 << 500,
            ),
            endpoint_certificate(
                hit,
                "SIEVE_FALSE_POSITIVE_ORDER",
                source_order=run_scan.HASSE_MAX,
                source_orbit_size=2,
            ),
            endpoint_certificate(
                hit, "KNOWN_CRATER", source_orbit_rep=hit.b, source_orbit_size=1
            ),
            endpoint_certificate(
                hit, "KNOWN_F271", source_orbit_rep=hit.b, source_orbit_size=17
            ),
            endpoint_certificate(
                hit,
                "EXCLUDED_PILOT_ORBIT",
                pilot_exclusion_scope="source-orbit",
            ),
            endpoint_certificate(
                hit,
                "EXCLUDED_PILOT_ORBIT",
                pilot_exclusion_scope="entire-parent-fiber",
            ),
            endpoint_certificate(hit, "DIRECT_PARENT"),
            endpoint_certificate(hit, "CERTIFIED_BOTTOM_PARENT"),
        ]
        for number, forged in enumerate(adversarial):
            try:
                pipeline.validate_certificate(forged, job, scientific=True)
            except pipeline.PipelineError:
                pass
            else:
                raise RuntimeError(
                    f"pipeline accepted forged benign label {forged['status']}"
                )
            forged_path = Path(raw_tmp) / f"forged-{number}.kv"
            write_endpoint(forged_path, forged)
            try:
                run_scan.parse_endpoint_certificate(
                    forged_path,
                    hit.binding(),
                    forged["status"],
                    False,
                    0,
                    pipeline.CENSUS_SHA256,
                    job.source_seed,
                    job.target_seed,
                    f"forged benign {number}",
                )
            except run_scan.RunError:
                pass
            else:
                raise RuntimeError(
                    f"runner accepted forged benign label {forged['status']}"
                )

        fatal_status_forges = [
            endpoint_certificate(
                hit,
                "UNKNOWN_EMBEDDING_EXHAUSTED",
                admitted_failure=1,
                embedding_attempts=1,
            ),
            endpoint_certificate(
                hit,
                "WRONG_ORBIT_SIZE",
                admitted_failure=1,
                source_orbit_size=51,
            ),
        ]
        for number, forged in enumerate(fatal_status_forges):
            try:
                pipeline.validate_certificate(forged, job, scientific=True)
            except pipeline.PipelineError:
                pass
            else:
                raise RuntimeError(
                    f"pipeline accepted unexplained fatal label {forged['status']}"
                )
            forged_path = Path(raw_tmp) / f"forged-fatal-{number}.kv"
            write_endpoint(forged_path, forged)
            try:
                run_scan.parse_endpoint_certificate(
                    forged_path,
                    hit.binding(),
                    forged["status"],
                    True,
                    0,
                    pipeline.CENSUS_SHA256,
                    job.source_seed,
                    job.target_seed,
                    f"forged fatal {number}",
                )
            except run_scan.RunError:
                pass
            else:
                raise RuntimeError(
                    f"runner accepted unexplained fatal label {forged['status']}"
                )

        valid_sieve = endpoint_certificate(
            hit,
            "SIEVE_FALSE_POSITIVE_ORDER",
            source_order=run_scan.AMBIENT_ORDER - 2,
        )
        pipeline.validate_certificate(valid_sieve, job, scientific=True)
        valid_sieve_path = Path(raw_tmp) / "valid-sieve.kv"
        write_endpoint(valid_sieve_path, valid_sieve)
        run_scan.parse_endpoint_certificate(
            valid_sieve_path,
            hit.binding(),
            "SIEVE_FALSE_POSITIVE_ORDER",
            False,
            0,
            pipeline.CENSUS_SHA256,
            job.source_seed,
            job.target_seed,
            "valid sieve false positive",
        )
        for boundary_name, boundary_order in (
            ("lower", run_scan.HASSE_MIN),
            ("upper", run_scan.HASSE_MAX),
        ):
            boundary_sieve = endpoint_certificate(
                hit,
                "SIEVE_FALSE_POSITIVE_ORDER",
                source_order=boundary_order,
            )
            pipeline.validate_certificate(boundary_sieve, job, scientific=True)
            boundary_path = Path(raw_tmp) / f"valid-sieve-{boundary_name}.kv"
            write_endpoint(boundary_path, boundary_sieve)
            run_scan.parse_endpoint_certificate(
                boundary_path,
                hit.binding(),
                "SIEVE_FALSE_POSITIVE_ORDER",
                False,
                0,
                pipeline.CENSUS_SHA256,
                job.source_seed,
                job.target_seed,
                f"valid sieve {boundary_name} Hasse boundary",
            )

        schema_adversarial = []
        unknown_field = dict(valid_sieve)
        unknown_field["unfrozen_extension_field"] = "1"
        schema_adversarial.append(("unknown field", unknown_field))
        wrong_seed = dict(valid_sieve)
        wrong_seed.update(
            embedding_seed=str(run_scan.EMBED_SEED),
            witness_seed=str(job.source_seed + 1),
            target_witness_seed=str(job.target_seed),
            witness_count_required=str(run_scan.WITNESS_COUNT),
            witness_attempt_cap=str(run_scan.MAX_WITNESS_ATTEMPTS),
        )
        schema_adversarial.append(("wrong deterministic seed", wrong_seed))
        for label, forged in schema_adversarial:
            try:
                pipeline.validate_certificate(forged, job, scientific=True)
            except pipeline.PipelineError:
                pass
            else:
                raise RuntimeError(f"pipeline accepted certificate with {label}")
            forged_path = Path(raw_tmp) / f"schema-{label.replace(' ', '-')}.kv"
            write_endpoint(forged_path, forged)
            try:
                run_scan.parse_endpoint_certificate(
                    forged_path,
                    hit.binding(),
                    "SIEVE_FALSE_POSITIVE_ORDER",
                    False,
                    0,
                    pipeline.CENSUS_SHA256,
                    job.source_seed,
                    job.target_seed,
                    f"certificate {label}",
                )
            except run_scan.RunError:
                pass
            else:
                raise RuntimeError(f"runner accepted certificate with {label}")

        duplicate_json = Path(raw_tmp) / "duplicate.json"
        duplicate_json.write_text('{"schema":"x","schema":"y"}\n')
        for malformed in (duplicate_json,):
            try:
                run_scan.load_json(malformed)
            except run_scan.RunError:
                pass
            else:
                raise RuntimeError("strict JSON parser accepted duplicate keys")
        nonfinite_json = Path(raw_tmp) / "nonfinite.json"
        nonfinite_json.write_text('{"value":NaN}\n')
        overflow_json = Path(raw_tmp) / "overflow.json"
        overflow_json.write_text('{"value":1e999}\n')
        for malformed in (nonfinite_json, overflow_json):
            try:
                run_scan.load_json(malformed)
            except run_scan.RunError:
                pass
            else:
                raise RuntimeError("strict JSON parser accepted a non-finite value")

        publish_source = Path(raw_tmp) / "publish-source"
        publish_target = Path(raw_tmp) / "publish-target"
        publish_source.mkdir()
        publish_target.mkdir()
        (publish_source / "source-only").write_text("source\n")
        (publish_target / "target-only").write_text("target\n")
        try:
            run_scan.promote_directory(publish_source, publish_target)
        except FileExistsError:
            pass
        else:
            raise RuntimeError("directory publication replaced an existing target")
        if not (publish_source / "source-only").is_file() or not (
            publish_target / "target-only"
        ).is_file():
            raise RuntimeError("failed no-replace publication changed either directory")

        orphan_root = Path(raw_tmp) / "orphan-index-recovery"
        orphan_root.mkdir()
        (orphan_root / "evidence.txt").write_text("terminal evidence\n")
        write_json(
            orphan_root / "DIRECTORIES.json",
            {"schema": "m51-sealed-directory-index/v1", "directories": []},
        )
        run_scan.seal_final(orphan_root)
        run_scan.verify_tree_manifest(orphan_root)

        mismatched_root = Path(raw_tmp) / "mismatched-orphan-index"
        mismatched_root.mkdir()
        (mismatched_root / "evidence.txt").write_text("terminal evidence\n")
        write_json(
            mismatched_root / "DIRECTORIES.json",
            {
                "schema": "m51-sealed-directory-index/v1",
                "directories": ["forged-empty-directory"],
            },
        )
        try:
            run_scan.seal_final(mismatched_root)
        except run_scan.RunError:
            pass
        else:
            raise RuntimeError("mismatched orphan directory index was accepted")
        if (mismatched_root / "MANIFEST.sha256").exists():
            raise RuntimeError("mismatched orphan index produced a root seal")

        immutable_file = Path(raw_tmp) / "immutable-file"
        immutable_file.write_bytes(b"first")
        try:
            run_scan.atomic_write_bytes(immutable_file, b"second")
        except FileExistsError:
            pass
        else:
            raise RuntimeError("atomic file publication replaced its target")
        if immutable_file.read_bytes() != b"first":
            raise RuntimeError("failed atomic publication changed its target")

        partial_root = Path(raw_tmp) / "stale-root-partials"
        partial_root.mkdir()
        stale_partial = partial_root / ".session.json.partial-123-456-7"
        stale_partial.write_bytes(b"incomplete")
        run_scan.cleanup_stale_root_partials(partial_root)
        if stale_partial.exists():
            raise RuntimeError("known crash partial was not removed on resume")

        orphan_process = run_scan.run_process(
            [
                "/bin/sh",
                "-c",
                "sleep 100 </dev/null >/dev/null 2>&1 & echo $!; kill -9 $$",
            ],
            timeout=5,
        )
        orphan_pid = int(orphan_process["stdout"].strip())
        if (
            orphan_process["exit_status"] != -9
            or b"residual process group terminated and reaped"
            not in orphan_process["stderr"]
            or Path(f"/proc/{orphan_pid}").exists()
        ):
            raise RuntimeError("residual process group was not terminated and reaped")

        inherited_pipe_started = time.monotonic()
        inherited_pipe_process = run_scan.run_process(
            [
                "/bin/sh",
                "-c",
                "trap '' TERM; sleep 30 & echo $!",
            ],
            timeout=10,
        )
        inherited_pipe_elapsed = time.monotonic() - inherited_pipe_started
        inherited_pipe_pid = int(inherited_pipe_process["stdout"].strip())
        if (
            inherited_pipe_elapsed >= 6
            or b"residual process group terminated and reaped"
            not in inherited_pipe_process["stderr"]
            or Path(f"/proc/{inherited_pipe_pid}").exists()
        ):
            raise RuntimeError(
                "leader-exit descendant held inherited pipes past bounded cleanup"
            )

        stable_base = {
            "kind": "binary",
            "path": "/frozen/gp",
            "sha256": run_scan.PINNED_GP_BINARY_SHA256,
            "source_image_id": run_scan.PINNED_GP_IMAGE_ID,
            "version_stdout": "GP/PARI CALCULATOR Version 2.15.2\n",
            "version_stderr": "",
            "ldd_path": "/usr/bin/ldd",
            "ldd_resolved_path": "/usr/bin/ldd",
            "ldd_sha256": "1" * 64,
            "ldd_stderr": "",
            "shared_objects": {"/lib/libc.so.6": {"sha256": "2" * 64, "bytes": 1}},
        }
        first_runtime = {**stable_base, "ldd_stdout": "libc => /lib/libc.so.6 (0x1)\n"}
        second_runtime = {**stable_base, "ldd_stdout": "libc => /lib/libc.so.6 (0x2)\n"}
        if run_scan.stable_gp_runtime_identity(first_runtime) != run_scan.stable_gp_runtime_identity(second_runtime):
            raise RuntimeError("ASLR-bearing ldd text contaminated resume identity")

        snapshot_root = Path(raw_tmp) / "snapshot-run"
        snapshot_inputs = snapshot_root / "inputs"
        snapshot_root.mkdir()
        snapshots.rename(snapshot_inputs)
        for path in snapshot_inputs.iterdir():
            path.chmod(0o444)
        frozen = (
            frozen_entries,
            hashlib.sha256(frozen_manifest.encode()).hexdigest(),
        )
        run_scan.verify_snapshot(snapshot_root, frozen)
        tampered = snapshot_inputs / "classify_recover.gp"
        tampered.chmod(0o644)
        tampered.write_bytes(tampered.read_bytes() + b"\\ tamper\n")
        try:
            run_scan.verify_snapshot(snapshot_root, frozen)
        except run_scan.RunError:
            pass
        else:
            raise RuntimeError("snapshot mutation was not rejected")
    print("harness contract ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
