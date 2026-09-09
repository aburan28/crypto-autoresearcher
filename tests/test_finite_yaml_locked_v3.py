"""Reproducible finite YAML v2 checks with explicit prerequisite deferral.

Preliminary mode exercises only parsing, metadata and no-context CLI refusals.
The admitted suite consumes real parent-published per-case capsules. It does
not create a Git fixture, authority, claim, source snapshot or scientific run.
"""
from __future__ import annotations
import argparse
import base64
import dataclasses
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import time
from datetime import datetime, timezone


def load(root):
    name = "finite_yaml_locked_v3_test_subject"
    spec = importlib.util.spec_from_file_location(name, root / "harness/finite_yaml_locked_v3.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def stamp():
    return datetime.now(timezone.utc).isoformat()


def capture(path, blobs):
    path = Path(path)
    if not os.path.lexists(path):
        return {"path": str(path), "exists": False}
    st = path.lstat()
    result = {"path": str(path), "exists": True, "mode": st.st_mode,
              "device": st.st_dev, "inode": st.st_ino, "nlink": st.st_nlink,
              "size": st.st_size, "mtime_ns": st.st_mtime_ns}
    if stat.S_ISLNK(st.st_mode):
        result["symlink_target"] = os.readlink(path)
    elif stat.S_ISREG(st.st_mode):
        raw = path.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        result.update(sha256=sha, bytes=len(raw))
        blobs.setdefault(sha, {"sha256": sha, "bytes": len(raw), "base64": base64.b64encode(raw).decode()})
    return result


def timing_metadata_case(case, module):
    """Ten frozen pure timing predicates; no process measurements are claimed."""
    name = case["case_id"]
    pre = {"wall_seconds": 0.5, "cpu_seconds": 0.1, "peak_rss_bytes": 1024,
           "boundary": module.PRE_RAW_BOUNDARY}
    value = {"wall_seconds": 1.0, "cpu_seconds": 0.2, "peak_rss_bytes": 2048,
             "boundary": module.FINAL_TIMING_BOUNDARY}
    if name == "timing-missing-object":
        value = None
    elif name.startswith("timing-missing-"):
        del value[name.removeprefix("timing-missing-")]
    elif name == "timing-nonfinite-wall":
        value["wall_seconds"] = float("nan")
    elif name == "timing-nonfinite-cpu":
        value["cpu_seconds"] = float("inf")
    elif name == "timing-negative-wall":
        value["wall_seconds"] = -1
    elif name == "timing-boolean-rss":
        value["peak_rss_bytes"] = True
    elif name == "timing-wrong-endpoint":
        value["boundary"] = module.PRE_RAW_BOUNDARY
    else:
        raise ValueError("unknown frozen timing metadata case")
    check = module.validate_final_timing(value, pre, module.FINAL_MEASUREMENT_ENDPOINT)
    child = {"return_code": 0, "group_quiescent": True, "timed_out": False,
             "memory_killed": False, "cpu_killed": False, "infrastructure_error": None, "stderr": ""}
    classified = module.classify_final(child, {"original_integrity": True}, True, check)
    passed = check["complete"] is False and classified["status"] == "completed_invalid" and classified["valid"] is False
    # NaN/Infinity are retained as explicit safe representations, never emitted
    # as nonfinite JSON or passed off as observations.
    return {"status": "executed", "outcome": "pass" if passed else "fail", "acceptance_covered": passed,
            "scope": "pure final-measurement predicate/classification metadata only",
            "input_safe_repr": repr(value), "pre_raw_metadata": pre, "final_endpoint_metadata": module.FINAL_MEASUREMENT_ENDPOINT,
            "measurement_predicate": check, "classification": classified,
            "normal_admission_succeeded": False, "child_entered": False, "scientific_runs": 0}


def verified_case_context(module, record, case_id):
    """Read-only routing from independently published parent authority."""
    p = module._p
    capsule = Path(record["capsule_path"])
    candidates = [root for root in (module.REPO_ROOT, *module.REPO_ROOT.parents) if (root / ".git").exists()]
    allowed = any(capsule.is_relative_to(root / "coordination/pending-ideas/BATCH-e9d1c7/timing-correction/qa-admission")
                  or capsule.is_relative_to(root / "coordination/pending-ideas/BATCH-e9d1c7/timing-correction/qa/scratch")
                  for root in candidates)
    p.require(capsule.is_absolute() and allowed, "case_capsule_namespace", "parent capsule must stay in the declared QA namespace")
    reference = p.strict_json(p.read_regular(capsule)[0])
    p.require(reference["case_id"] == case_id, "case_capsule_id", "wrong selected case")
    repository, authority, case = module.published_authority(reference, {})
    p.relative_name(case_id, leaf=True)
    expected_root = repository / module.MIRROR_SCRATCH_ROOT / "fixtures" / case_id / "repo"
    fixture_root = Path(case["fixture_root"])
    p.require(fixture_root == expected_root, "case_fixture_root", "exact per-case fixture checkout required")
    plan_raw = p.read_regular(fixture_root / p.relative_name(case["plan"]["path"]))[0]
    p.require(p.digest(plan_raw) == case["plan"]["sha256"], "case_plan_hash", "published sidecar drift")
    plan = p.strict_json(plan_raw)["execution_plan"]
    for fixed in ("tests/test_finite_yaml_locked_v3.py", "harness/finite_yaml_locked_v3.py", "harness/finite_yaml_process_v2.py"):
        matches = [row for row in plan["source_closure"] if row["path"] == fixed]
        p.require(len(matches) == 1, "case_source_membership", fixed)
        current = p.read_regular(fixture_root / fixed)[0]
        blob = p.git(repository, reference["git"], ["show", authority["source_snapshot"] + ":" + fixed], module.tool_environment())
        p.require(current == blob and p.digest(current) == matches[0]["sha256"], "case_source_snapshot", fixed)
    python = plan["dependency_closure"]["python"]
    p.require(str(Path(python["executable"]).resolve()) == python["executable"], "case_python_path", "normalized interpreter required")
    p.bind_file(python["executable"], python["sha256"])
    outer = plan["environment_policy"]["outer"]
    p.require(type(outer) is dict and all(type(k) is str and type(v) is str for k, v in outer.items()),
              "case_outer_environment", "explicit string allowlist required")
    p.require(not any(k.startswith(("PYTHON", "LD_", "DYLD_")) or any(token in k.upper() for token in ("TOKEN", "SECRET", "PASSWORD", "API_KEY")) for k in outer),
              "case_outer_environment", "forbidden loader/credential environment variable")
    return reference, authority, case, plan


def verify_published_index(module, record, index_path, case_id):
    reference, authority, case, plan = verified_case_context(module, record, case_id)
    p = module._p
    repository = Path(reference["authority_repository"])
    relative = "coordination/pending-ideas/BATCH-e9d1c7/timing-correction/qa-admission/admitted-index.json"
    p.require(index_path.absolute() == repository / relative, "admitted_index_namespace", "exact parent index path required")
    current = p.read_regular(repository / relative)[0]
    blob = p.git(repository, reference["git"], ["show", reference["publication_commit"] + ":" + relative], module.tool_environment())
    p.require(current == blob, "admitted_index_publication", "index differs from the independently published Git blob")
    return reference, authority, case, plan


def route_admitted_case(case, module, record, index_path, blobs):
    """One fixed case in one fresh process; actual REPO_ROOT is never patched."""
    name = case["case_id"]
    reference, authority, published, plan = verify_published_index(module, record, index_path, name)
    root = Path(published["fixture_root"])
    evidence_dir = Path(reference["authority_repository"]) / module.MIRROR_SCRATCH_ROOT / "case-evidence"
    # The parent prepares the directory. This task reserves only its one new
    # per-case evidence file outside the clean fixture checkout.
    fd = module._p.open_directory(evidence_dir)
    os.close(fd)
    evidence = evidence_dir / (name + ".json")
    module._p.require(not os.path.lexists(evidence), "case_evidence_existing", "no repeated case attempt or overwrite")
    command = [plan["dependency_closure"]["python"]["executable"], "-B",
               str(root / "tests/test_finite_yaml_locked_v3.py"), "--source-root", str(root),
               "--admitted-index", str(index_path.absolute()), "--single-case", name,
               "--evidence", str(evidence)]
    started = time.monotonic()
    completed = subprocess.run(command, cwd=root, env=dict(plan["environment_policy"]["outer"]),
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               timeout=3600, check=False)
    process_record = {"argv": command, "cwd": str(root), "environment": plan["environment_policy"]["outer"],
                      "exit_code": completed.returncode, "duration_seconds": time.monotonic() - started,
                      "stdout_base64": base64.b64encode(completed.stdout).decode(),
                      "stderr_base64": base64.b64encode(completed.stderr).decode(),
                      "case_id": name, "routing_scope": "one parent-published case per fresh interpreter; no inherited module cache or root override"}
    if not evidence.is_file() or evidence.is_symlink():
        return {"status": "failed", "outcome": "fail", "acceptance_covered": False,
                "process": process_record, "error": {"type": "MissingCaseEvidence", "message": "per-case process did not produce its exclusive report"}}
    body = module._p.strict_json(evidence.read_bytes())
    module._p.require(body["case_id"] == name, "case_evidence_id", "wrong returned case")
    for key, blob in body["blobs"].items():
        raw = base64.b64decode(blob["base64"])
        module._p.require(hashlib.sha256(raw).hexdigest() == key == blob["sha256"] and len(raw) == blob["bytes"],
                          "case_evidence_blob", "returned embedded bytes do not match")
        blobs.setdefault(key, blob)
    result = body["result"]
    result["process"] = process_record
    result["per_case_evidence"] = capture(evidence, blobs)
    if completed.returncode != 0:
        result.update(outcome="fail", acceptance_covered=False)
    return result


def preliminary(case, module, root):
    name = case["case_id"]
    result = {"status": "deferred", "outcome": None, "acceptance_covered": False,
              "reason": "Requires actual post-snapshot parent-published authority and clean QA fixture.",
              "scientific_runs": 0, "child_entered": False}
    operations = {}
    p = module._p
    if name.startswith("timing-"):
        return timing_metadata_case(case, module)
    if name == "duplicate-keys":
        operations = {"input_utf8": '{"x":1,"x":2}', "predicate": "duplicate_keys"}
        action = lambda: p.strict_json(operations["input_utf8"])
    elif name in ("nonfinite-nan", "nonfinite-inf"):
        operations = {"input_utf8": '{"x":' + ("NaN" if name.endswith("nan") else "Infinity") + '}', "predicate": "nonfinite_number"}
        action = lambda: p.strict_json(operations["input_utf8"])
    elif name == "malformed-external-hash":
        operations = {"expected_sha256": "not-a-sha256", "predicate": "external_hash_format"}
        action = lambda: module.validate_lock("not-read", "not-a-sha256", "RUN-ECDLP-56d8aa", {})
    elif name in ("boolean-format-version", "boolean-worker-count"):
        operations = {"input": True, "predicate": "exact_integer"}
        action = lambda: p.exact_integer(True, "exact_integer")
    elif name in ("zero-watchdog", "null-watchdog"):
        value = 0 if name.startswith("zero") else None
        operations = {"input": value, "predicate": "watchdog"}
        action = lambda: p.positive_number(value, "watchdog")
    elif name.startswith("inventory-"):
        ids = [r["id"] for r in module.RECOVERY_CASES]
        b, i = list(ids), list(ids)
        if name == "inventory-delete":
            b.pop()
        elif name == "inventory-duplicate":
            b[-1] = b[0]
        elif name == "inventory-mismatched":
            i[-1] = "incorrect"
        elif name == "inventory-reordered":
            b[0], b[1] = b[1], b[0]
        operations = {"B": b, "I": i, "predicate": None if name == "inventory-identical" else "recovery_case_inventory"}
        action = lambda: module.validate_recovery_case_arms(b, i)
        result["acceptance_covered"] = True
    elif name == "nonquiescent-classification":
        operations = {"child_metadata": {"return_code": 0, "group_quiescent": False}, "predicate": None}
        def action():
            observed = p.classify(operations["child_metadata"])
            operations["actual"] = observed
            assert observed["status"] == "failed_infrastructure" and observed["valid"] is False
        result["acceptance_covered"] = True
    elif name == "unsupported-resource-host-metadata":
        operations = {"metadata": {"name": "posix", "uid": 0, "has_nproc": True, "has_wait4": True}, "predicate": "resource_host"}
        action = lambda: p.host_supported(**operations["metadata"])
        result["acceptance_covered"] = True
    elif name == "fabricated-verified-token":
        operations = {"input": "plain caller mapping", "predicate": "verified_token"}
        action = lambda: module.execute_locked({"scientific_execution_authorized": False})
    elif name.startswith("no-lock-"):
        exp = name.removeprefix("no-lock-")
        entry = root / "experiments" / exp / "source-v4/locked_entry.py"
        if not entry.is_file() or entry.is_symlink():
            raise ValueError("source-v4 refusal entry is missing or aliased")
        command = [sys.executable, "-I", "-S", "-B", str(entry)]
        completed = subprocess.run(command, cwd=root, env={"PATH": "/usr/bin:/bin", "LC_ALL": "C"},
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10, check=False)
        refused = (completed.returncode == 2 and not completed.stdout
                   and b"--launch-context-fd" in completed.stderr and b"required" in completed.stderr
                   and b"can't open file" not in completed.stderr)
        result.update(status="executed", outcome="pass" if refused else "fail",
                      acceptance_covered=refused, reason=None, scope="actual source-v4 argparse no-context refusal only",
                      command=command, cwd=str(root), exit_code=completed.returncode,
                      stdout_base64=base64.b64encode(completed.stdout).decode(), stderr_base64=base64.b64encode(completed.stderr).decode(),
                      environment={"PATH": "/usr/bin:/bin", "LC_ALL": "C"})
        return result
    else:
        return result
    result.update(status="executed", reason=None, scope="preliminary pure parser/metadata/refusal; no admitted fixture",
                  inputs=operations, normal_admission_succeeded=False)
    try:
        action()
    except module.FiniteYamlLockError as exc:
        result.update(outcome="pass" if exc.predicate == operations["predicate"] else "fail",
                      error={"type": type(exc).__name__, "message": str(exc), "predicate": exc.predicate})
    except Exception as exc:
        result.update(outcome="fail", error={"type": type(exc).__name__, "message": str(exc)})
    else:
        result["outcome"] = "pass" if operations["predicate"] is None else "fail"
    return result


def named_predicate(name):
    table = {"missing-lock": "file_access", "wrong-external-hash": "external_lock_hash",
        "malformed-external-hash": "external_hash_format", "duplicate-keys": "duplicate_keys",
        "nonfinite-nan": "nonfinite_number", "nonfinite-inf": "nonfinite_number",
        "science-authority-true": "scientific_authority", "run-id-mismatch": "authority_run",
        "bad-run-id": "authority_run", "claim-release-present": "claim_release",
        "claim-newer-epoch": "claim_newer_epoch", "native-receipt-copied-producer": "native_copied_producer",
        "native-receipt-requested-effort-low": "native_reasoning_effort",
        "metric-decision-wrong-id": "metric_decision", "sidecar-missing-row": "plan_run_inventory",
        "sidecar-extra-row": "plan_run_inventory", "sidecar-duplicate-row": "plan_run_inventory",
        "model-constant-override": "configuration_membership", "incidence-config-extra-field": "configuration_membership",
        "incidence-config-boolean-p": "configuration_membership", "argv-executable-not-bound": "argv_binding",
        "source-closure-incomplete": "source_closure_membership", "dependency-pyyaml-omitted": "dependency_distribution_membership",
        "dependency-version-mismatch": "dependency_version", "fabricated-verified-token": "verified_token",
        "zero-watchdog": "watchdog", "null-watchdog": "watchdog", "wrong-host-uid": "effective_uid",
        "bedrock-in-caller-metadata": "prohibited_caller_provider", "bedrock-in-native-receipt": "prohibited_native_provider",
        "unprobed-verified-provenance": "native_probe", "degraded-fallback-receipt": "native_fallback_degradation"}
    if name.startswith("reserved-wrong-config-") or name == "cross-experiment-reserved-run":
        return "configuration_membership"
    mirror_overlays = {
        "prelaunch-claim-drift": "claim_mirror_bytes", "postlaunch-claim-drift": "claim_mirror_bytes",
        "prelaunch-native-receipt-drift": "native_receipt_mirror_bytes",
        "postlaunch-native-receipt-drift": "native_receipt_mirror_bytes"}
    if name in mirror_overlays:
        return mirror_overlays[name]
    if name.startswith("mirror-"):
        label = "native_receipt" if name.endswith("native-receipt") else "claim"
        predicate = "present" if "-missing-" in name else ("nonalias" if "-symlink-" in name or "-hardlink-" in name
                    else ("identity" if "-same-bytes-new-inode-" in name else "bytes"))
        return label + "_mirror_" + predicate
    if name.startswith("claim-mismatch-"):
        return "claim_" + name.removeprefix("claim-mismatch-")
    if name in ("expired-caller-claim", "expired-lock-reference", "future-acquired-claim", "actual-claim-expiry-between-phases"):
        return "claim_current"
    if name.startswith(("symlink-", "hardlink-")) or name in ("raw-result-symlink_raw", "raw-result-hardlink_raw", "child-manifest-collision", "manifest-file-race-barrier"):
        return "exclusive_file"
    if name.startswith("postlaunch-"):
        target = name.removeprefix("postlaunch-").replace("-mutation", "").replace("-drift", "")
        return {"lock": "approval_lock_unchanged", "spec": "specification_unchanged",
                "plan": "execution_plan_unchanged", "claim": "claim_current_and_unchanged",
                "native-receipt": "native_receipt_unchanged", "schema": "schema_unchanged",
                "executable": "executable_and_dependencies_unchanged", "git-state": "commit_unchanged"}.get(target)
    if name == "clean-tree-negative-control":
        return "tree_unchanged"
    return table.get(name)


def admitted(case, module, record, blobs):
    """One exact parent-prepared case. Never synthesize missing authority."""
    p, name = module._p, case["case_id"]
    required = {"capsule_path", "lock_path", "expected_sha256", "run_id", "expected_predicate",
                "expected_status", "evidence_paths", "prelaunch_mutation"}
    if set(record) != required:
        raise ValueError("parent admitted-index row has wrong fields")
    reference = p.strict_json(Path(record["capsule_path"]).read_bytes())
    if reference["case_id"] != name:
        raise ValueError("index/capsule case mismatch")
    result = {"status": "executed", "scope": "parent-prepared normal admission", "acceptance_covered": False,
              "normal_admission_succeeded": False, "child_entered": False, "scientific_runs": 0,
              "started_at": stamp(), "inputs": record,
              "before": [capture(path, blobs) for path in record["evidence_paths"]]}
    snapshot = None
    original_paths = []
    try:
        _, authority, published_case, _ = verified_case_context(module, record, name)
        authority_repository = Path(reference["authority_repository"])
        original_paths = [authority_repository / authority[kind]["path"] for kind in ("claim", "native_receipt")]
        result["genuine_originals_before"] = [capture(path, blobs) for path in original_paths]
        token = module.validate_lock(record["lock_path"], record["expected_sha256"], record["run_id"], reference)
        result["normal_admission_succeeded"] = True
        snapshot = p.strict_json(token.snapshot_json)
        result["admission_snapshot_sha256"] = p.digest(p.canonical(snapshot))
        # All relevant source and fixture input bytes are retained once by hash.
        for binding in snapshot["bindings"].values():
            if Path(binding["path"]).is_relative_to(snapshot["root"]):
                result["before"].append(capture(binding["path"], blobs))
        mutation = record["prelaunch_mutation"]
        if mutation is not None:
            allowed = snapshot["case"].get("prelaunch_mutation")
            if mutation != allowed:
                raise ValueError("mutation must be explicitly parent-published")
            target = Path(mutation["path"])
            mirror_paths = {Path(value["path"]) for value in snapshot["mirror_bindings"].values()}
            if target not in mirror_paths and (not target.is_relative_to(snapshot["root"]) or "/qa/scratch/" not in str(target)):
                raise ValueError("mutation outside disposable fixture or exact independently bound mirror")
            if target.is_symlink() or p.digest(target.read_bytes()) != mutation["before_sha256"]:
                raise ValueError("mutation before identity/hash differs")
            # Mutation controls are deliberate edits only to named disposable
            # fixture copies, not real records or published source files.
            if mutation.get("kind") == "same_bytes_new_inode":
                import tempfile
                raw_before = target.read_bytes()
                fd, temporary = tempfile.mkstemp(prefix=".identity-control-", dir=target.parent)
                try:
                    with os.fdopen(fd, "wb") as stream:
                        stream.write(raw_before)
                        stream.flush()
                        os.fsync(stream.fileno())
                    os.replace(temporary, target)
                finally:
                    if os.path.exists(temporary):
                        os.unlink(temporary)
            else:
                with target.open("r+b") as stream:
                    stream.write(mutation["after_utf8"].encode())
                    stream.truncate()
                    stream.flush()
                    os.fsync(stream.fileno())
        if case["kind"] in ("mapping_admission",) or name in ("baseline", "required-original-envelope"):
            result.update(outcome="pass", acceptance_covered=True)
        else:
            manifest_path = module.execute_locked(token)
            manifest = p.strict_json(Path(manifest_path).read_bytes())["run"]
            result.update(manifest=manifest, manifest_path=manifest_path,
                          outcome="pass" if manifest["status"] == record["expected_status"] else "fail")
            raw = p.strict_json((Path(manifest_path).parent / "raw-result.json").read_bytes())
            result["raw_result"] = raw
            log = (Path(manifest_path).parent / "stdout.txt").read_text()
            result["child_entered"] = '"sentinel_entered": true' in log
            target = record["expected_predicate"]
            if target is not None:
                fixed = named_predicate(name)
                result["outcome"] = "pass" if target in raw["postflight_failures"] and not manifest["result"]["valid"] and (fixed is None or target == fixed) else "fail"
            # The test independently recomputes every declared artifact hash and
            # exact expected profile membership. It does not rely on a producer
            # status string alone for a clean positive control.
            if manifest["status"] == "completed_valid":
                expected_names = set(module.PROFILES[manifest["experiment_id"]]["manifest_hashed_names"])
                assert set(manifest["artifacts"]) == expected_names
                for name_, reference_ in manifest["artifacts"].items():
                    bytes_ = (Path(manifest_path).parent / name_).read_bytes()
                    assert p.digest(bytes_) == reference_["sha256"] and len(bytes_) == reference_["bytes"]
                assert all(manifest["protocol"]["post_run_checks"].values())
                assert all(raw["additional_post_run_checks"].values())
                assert manifest["result"]["metrics"]["wrapper_postprocessing_complete"] is True
                assert raw["launch_receipt"]["wrapper_postprocessing"] is None
                assert raw["cost_boundary"]["raw_mirror_requirement"] == "unavailable_by_declared_boundary"
                timing = module.validate_final_timing(manifest["resources"]["wrapper_postprocessing"],
                    raw["cost_boundary"]["pre_raw_observation"], raw["cost_boundary"]["final_measurement_endpoint"])
                assert timing["complete"] and raw["cost_boundary"]["raw_result_self_hash"] is False
                assert "wrapper_postprocessing_complete" not in raw["additional_post_run_checks"]
                assert "receipt_wrapper_timing_mirror_complete" not in raw["additional_post_run_checks"]
            result["acceptance_covered"] = result["outcome"] == "pass"
            for path in sorted(Path(manifest_path).parent.iterdir()):
                result.setdefault("outputs", []).append(capture(path, blobs))
    except module.FiniteYamlLockError as exc:
        expected = record["expected_predicate"]
        fixed = named_predicate(name)
        actual_predicate = exc.predicate
        if snapshot is not None:
            diagnostic = Path(snapshot["root"]) / snapshot["plan"]["fixture_authorization"]["terminal_diagnostic"]
            if diagnostic.is_file() and not diagnostic.is_symlink():
                body = p.strict_json(diagnostic.read_bytes())
                result["terminal_diagnostic"] = body
                result.setdefault("outputs", []).append(capture(diagnostic, blobs))
                if body.get("predicate"):
                    actual_predicate = body["predicate"]
            output = Path(snapshot["run_directory"])
            if output.is_dir() and not output.is_symlink():
                for path in sorted(output.iterdir()):
                    result.setdefault("outputs", []).append(capture(path, blobs))
                stdout = output / "stdout.txt"
                if stdout.is_file() and not stdout.is_symlink():
                    result["child_entered"] = '"sentinel_entered": true' in stdout.read_text(errors="replace")
        result.update(error={"type": type(exc).__name__, "message": str(exc), "predicate": exc.predicate},
                      actual_target_predicate=actual_predicate,
                      outcome="pass" if expected is not None and actual_predicate == expected and (fixed is None or fixed == expected) else "fail")
        result["acceptance_covered"] = result["outcome"] == "pass"
    finally:
        result["after"] = [capture(path, blobs) for path in record["evidence_paths"]]
        result["genuine_originals_after"] = [capture(path, blobs) for path in original_paths]
        if original_paths:
            before = result.get("genuine_originals_before", [])
            result["genuine_originals_unchanged"] = before == result["genuine_originals_after"]
            if not result["genuine_originals_unchanged"]:
                result["outcome"] = "fail"
                result["acceptance_covered"] = False
        if "mirror" in name or name in ("prelaunch-claim-drift", "postlaunch-claim-drift", "prelaunch-native-receipt-drift", "postlaunch-native-receipt-drift"):
            result["evidence_label"] = "disposable mirror integrity only; never a genuine authority event"
        result["finished_at"] = stamp()
    return result


def run_suite(root, admitted_index=None):
    module = load(root)
    inventory_path = root / "tests/fixtures/finite_yaml_locked_v3/cases.json"
    inventory = json.loads(inventory_path.read_text())
    cases = inventory["cases"]
    assert len(cases) == 174 and len({r["case_id"] for r in cases}) == 174
    inherited_digest = hashlib.sha256(json.dumps(cases[:154], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert inherited_digest == "b10f855194c5523bce8b71f498edb21f9545db4d61e735ca184d013c5c4515fd"
    assert len(inventory["amendment_overlays"]) == 4
    blobs, results = {}, []
    index = json.loads(Path(admitted_index).read_text()) if admitted_index else {}
    # Clean full-profile baselines precede mutation comparisons. Without those
    # successes, no unrelated dirty-tree failure can count as target coverage.
    baselines = {"child-success", "profile-EXP-ECDLP-abf981", "profile-EXP-ECDLP-2cb7f8"}
    ordered = sorted(cases, key=lambda c: (0 if c["case_id"] in baselines else 1, cases.index(c))) if index else cases
    baseline_ok = not index
    passed_baselines = set()
    for case in ordered:
        start = time.monotonic()
        name = case["case_id"]
        try:
            if name in index:
                if name not in baselines and not baseline_ok and case["kind"] in (
                    "execution", "fixture_execution", "postflight_failure", "output_race", "output_order", "identity_drift", "profile_failure", "output_alias", "environment"):
                    result = {"status": "deferred", "outcome": None, "acceptance_covered": False,
                              "reason": "Required clean baseline and both profiles have not passed.", "scientific_runs": 0}
                else:
                    result = route_admitted_case(case, module, index[name], Path(admitted_index), blobs)
                    if name in baselines and result.get("outcome") == "pass" and result.get("manifest", {}).get("status") == "completed_valid":
                        passed_baselines.add(name)
                    baseline_ok = passed_baselines == baselines
            else:
                result = preliminary(case, module, root)
        except Exception as exc:
            result = {"status": "failed", "outcome": "fail", "acceptance_covered": False,
                      "error": {"type": type(exc).__name__, "message": str(exc)}, "scientific_runs": 0}
        result.update(case_id=name, kind=case["kind"], attempt=1,
                      duration_seconds=time.monotonic() - start)
        if name in inventory["amendment_overlays"]:
            result["amendment_overlay"] = inventory["amendment_overlays"][name]
        results.append(result)
    # Useful extra pure checks are explicitly outside the 174 admitted controls.
    extra = []
    for mapping in module.CONFIGURATIONS:
        module.check_configuration(mapping["experiment_id"], mapping["run_id"], mapping["configuration"])
        mutated = dict(mapping["configuration"], version=True)
        try:
            module.check_configuration(mapping["experiment_id"], mapping["run_id"], mutated)
        except module.FiniteYamlLockError:
            rejected = True
        else:
            rejected = False
        extra.append({"run_id": mapping["run_id"], "exact_metadata_accepted": True,
                      "boolean_version_rejected": rejected, "scope": "pure metadata only; E01 admission remains deferred"})
    return {"schema": "crypto.autoresearch.finite_yaml_v3_test_execution.v1", "recorded_at": stamp(),
            "source_root": str(root), "inventory_sha256": hashlib.sha256(inventory_path.read_bytes()).hexdigest(),
            "command": sys.argv, "cwd": str(Path.cwd()), "mode": "parent_admitted" if index else "preliminary",
            "scientific_runs": 0, "cases": results, "extra_metadata_checks": extra, "blobs": blobs,
            "summary": {"declared": len(results), "executed": sum(r["status"] == "executed" for r in results),
                        "deferred": sum(r["status"] == "deferred" for r in results),
                        "failed": sum(r.get("outcome") == "fail" for r in results),
                        "acceptance_covered": sum(r.get("acceptance_covered", False) for r in results)},
            "limitations": ["Preliminary helpers do not establish normal-admission coverage.",
                "No scientific loader or reserved RUN directory is invoked.",
                "Full acceptance requires independently prepared clean published fixture authority and actual native/claim/dependency bindings.",
                "This producer's test assertions remain subject to fresh independent QA."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=Path(__file__).absolute().parents[1])
    parser.add_argument("--admitted-index")
    parser.add_argument("--single-case")
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    if args.single_case:
        if not args.admitted_index:
            parser.error("--single-case requires the parent-published admitted index")
        root = args.source_root.absolute()
        module = load(root)
        inventory = json.loads((root / "tests/fixtures/finite_yaml_locked_v3/cases.json").read_text())
        case = next(c for c in inventory["cases"] if c["case_id"] == args.single_case)
        index = json.loads(Path(args.admitted_index).read_text())
        blobs = {}
        verify_published_index(module, index[args.single_case], Path(args.admitted_index), args.single_case)
        observed = admitted(case, module, index[args.single_case], blobs)
        result = {"schema": "crypto.autoresearch.finite_yaml_v3_single_case.v1", "case_id": args.single_case,
                  "result": observed, "blobs": blobs, "command": sys.argv, "cwd": str(Path.cwd()),
                  "summary": {"failed": int(observed.get("outcome") != "pass")}}
    else:
        result = run_suite(args.source_root.absolute(), args.admitted_index)
    with args.evidence.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    print(json.dumps(result["summary"], sort_keys=True))
    return 1 if result["summary"]["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
