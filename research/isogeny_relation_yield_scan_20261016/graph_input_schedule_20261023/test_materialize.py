"""Replay the three full-quota P37 preparation controls and rejection cases."""
from __future__ import annotations

import json
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
ROOTS = STUDY / "seed_custody_20261022/control"
CONTROL = HERE / "control"
sys.path.insert(0, str(HERE))
from materialize import load_schedule, parse_prepared  # noqa: E402

ARMS = ("P37-v0000-low_x", "P37-v0000-u2_transport", "P37-v0000-graph_transport")


def check(arm: str, prepared: Path, *, root_override: dict[str, Path] | None = None) -> subprocess.CompletedProcess:
    roots = {name: ROOTS / (name + ".hex") for name in ("base", "target", "verifier")}
    roots.update(root_override or {})
    command = [sys.executable, str(HERE / "materialize.py"), "check",
               "--arm-key", arm, "--base-root-file", str(roots["base"]),
               "--target-root-file", str(roots["target"]),
               "--verifier-root-file", str(roots["verifier"]),
               "--commitment", str(CONTROL / "commitment.json"),
               "--output-dir", str(prepared)]
    return subprocess.run(command, capture_output=True, text=True, check=False)


def require_rejection(name: str, result: subprocess.CompletedProcess, phrase: str) -> dict:
    if result.returncode == 0 or phrase not in result.stderr:
        raise AssertionError(f"{name} was not rejected for {phrase!r}")
    return {"case": name, "status": "rejected", "reason_contains": phrase}


def main() -> None:
    # The same fixed vertex/arm universe carries a stage-specific target quota.
    # This is a schedule binding check only; no confirmation stream is drawn.
    _, p29_discovery = load_schedule("P29-v0000-low_x", "discovery")
    _, p29_confirmation = load_schedule("P29-v0000-low_x", "confirmation")
    _, p37_confirmation = load_schedule("P37-v0000-low_x", "confirmation")
    if (p29_discovery["target_count"] != 8192 or
            p29_confirmation["target_count"] != 32768 or
            p37_confirmation["target_count"] != 32768 or
            p29_confirmation["stage"] != "confirmation" or
            p37_confirmation["stage"] != "confirmation"):
        raise AssertionError("stage-specific fixed target quotas differ")
    try:
        load_schedule("P29-v0000-low_x", "finalist")
    except ValueError:
        pass
    else:
        raise AssertionError("unsupported stage was accepted")
    secondary_coefficients = set()
    secondary_verified = 0
    with tempfile.TemporaryDirectory(prefix="ectd-p29-secondary-controls-") as temporary:
        temp = Path(temporary)
        p29_walk = STUDY / "walk-p29-2048-attempt2.jsonl"
        legacy = ROOT / "research/conductor_relation_yield_20261014"
        source_files = (STUDY / "preparation/prepare_graph_input.py",
                        legacy / "prepare_input.py", legacy / "verify_collector.py")
        root_values = {name: bytes.fromhex((ROOTS / f"{name}.hex").read_text().strip())
                       for name in ("base", "target", "verifier")}
        commitment = {
            "schema": "isogeny-relation-seed-commitment/v2",
            **{f"{name}_root_sha256": hashlib.sha256(value).hexdigest()
               for name, value in root_values.items()},
            "graph_sha256": hashlib.sha256(p29_walk.read_bytes()).hexdigest(),
            "graph_manifest_sha256": hashlib.sha256((STUDY / "manifest-v2.json").read_bytes()).hexdigest(),
            "source_sha256": {path.relative_to(ROOT).as_posix():
                              hashlib.sha256(path.read_bytes()).hexdigest()
                              for path in source_files},
        }
        commitment_path = temp / "p29-commitment.json"
        commitment_path.write_text(json.dumps(commitment, sort_keys=True) + "\n")
        for arm in ("P29-E2-low_x", "P29-E2-random_x",
                    "P29-E3-low_x", "P29-E3-random_x"):
            output = temp / arm
            command = [sys.executable, str(HERE / "materialize.py"), "prepare",
                       "--arm-key", arm,
                       "--base-root-file", str(ROOTS / "base.hex"),
                       "--target-root-file", str(ROOTS / "target.hex"),
                       "--verifier-root-file", str(ROOTS / "verifier.hex"),
                       "--commitment", str(commitment_path), "--output-dir", str(output)]
            prepared = subprocess.run(command, capture_output=True, text=True, check=False)
            if prepared.returncode:
                raise AssertionError(f"{arm} materialization failed: {prepared.stderr}")
            binding = json.loads(prepared.stdout)
            secondary_coefficients.add(binding["coefficient_vector_sha256"])
            check_command = [sys.executable, str(HERE / "materialize.py"), "check",
                             "--arm-key", arm,
                             "--base-root-file", str(ROOTS / "base.hex"),
                             "--target-root-file", str(ROOTS / "target.hex"),
                             "--verifier-root-file", str(ROOTS / "verifier.hex"),
                             "--commitment", str(commitment_path), "--output-dir", str(output)]
            checked = subprocess.run(check_command, capture_output=True, text=True, check=False)
            if checked.returncode:
                raise AssertionError(f"{arm} binding replay failed: {checked.stderr}")
            verify = subprocess.run([sys.executable,
                                     str(STUDY / "preparation/verify_prepared_graph.py"),
                                     "--prepared", str(output / "prepared.txt"),
                                     "--manifest", str(output / "manifest.json")],
                                    capture_output=True, text=True, check=False)
            if verify.returncode or json.loads(verify.stdout).get("targets_checked") != 8192:
                raise AssertionError(f"{arm} independent input verification failed: {verify.stderr}")
            secondary_verified += 1
    if len(secondary_coefficients) != 1 or secondary_verified != 4:
        raise AssertionError("E2/E3 endpoints do not share the exact P29 coefficient stream")
    bindings = {}
    group_replay = {}
    for arm in ARMS:
        result = check(arm, CONTROL / arm)
        if result.returncode:
            raise AssertionError(f"{arm} replay failed: {result.stderr}")
        bindings[arm] = json.loads(result.stdout)
        prepared = CONTROL / arm
        command = [sys.executable, str(STUDY / "preparation/verify_prepared_graph.py"),
                   "--prepared", str(prepared / "prepared.txt"),
                   "--manifest", str(prepared / "manifest.json")]
        replay = subprocess.run(command, capture_output=True, text=True, check=False)
        if replay.returncode or json.loads(replay.stdout).get("status") != "pass":
            raise AssertionError(f"{arm} group replay failed: {replay.stderr}")
        group_replay[arm] = json.loads(replay.stdout)
    coefficients = {binding["coefficient_vector_sha256"] for binding in bindings.values()}
    if len(coefficients) != 1:
        raise AssertionError("same-stratum coefficient streams differ")
    native = CONTROL / ARMS[0] / "prepared.txt"
    graph = CONTROL / ARMS[2] / "prepared.txt"
    if native.read_bytes() != graph.read_bytes():
        raise AssertionError("source graph transport differs at index zero")
    _, native_base, native_targets = parse_prepared(native)
    _, transformed_base, transformed_targets = parse_prepared(
        CONTROL / ARMS[1] / "prepared.txt")
    p = 81640512137
    if (len(native_base) != 3200 or len(native_targets) != 2048 or
            transformed_base != [[4 * x % p, 8 * y % p] for x, y in native_base] or
            transformed_targets != [[a, b, 4 * x % p, 8 * y % p]
                                    for a, b, x, y in native_targets]):
        raise AssertionError("u=2 source points or targets differ from exact map")
    rejected = []
    rejected.append(require_rejection(
        "swapped-root", check(ARMS[0], CONTROL / ARMS[0],
                              root_override={"verifier": ROOTS / "base.hex"}),
        "roots must be distinct"))
    rejected.append(require_rejection(
        "unscheduled-arm", check("P37-v0001-power_x", CONTROL / ARMS[0]),
        "arm absent"))
    with tempfile.TemporaryDirectory(prefix="ectd-prepared-mutation-") as tmp:
        changed = Path(tmp) / "arm"
        shutil.copytree(CONTROL / ARMS[0], changed)
        source = changed / "prepared.txt"
        lines = source.read_text().splitlines()
        first_target = next(index for index, line in enumerate(lines) if line.startswith("target 0 "))
        values = lines[first_target].split()
        values[2] = str((int(values[2]) + 1) % 81640511861)
        lines[first_target] = " ".join(values)
        source.write_text("\n".join(lines) + "\n")
        rejected.append(require_rejection(
            "changed-target", check(ARMS[0], changed),
            "prepared input metadata differs"))
        changed_checkpoint = Path(tmp) / "graph"
        shutil.copytree(CONTROL / ARMS[2], changed_checkpoint)
        manifest_path = changed_checkpoint / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["checkpoint_sha256"] = "0" * 64
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        rejected.append(require_rejection(
            "changed-graph-checkpoint", check(ARMS[2], changed_checkpoint),
            "prepared graph-transport checkpoint differs"))
    print(json.dumps({"schema": "ectd.graph-materializer-control.v1", "status": "pass",
                      "scope": "P37 transport controls plus public-root P29 E2/E3 prepared inputs; no collector runs",
                      "target_count_per_arm": 2048, "base_signed_points": 3200,
                      "confirmation_quota_binding": {"P29": p29_confirmation["target_count"],
                                                      "P37": p37_confirmation["target_count"]},
                      "coefficient_vector_sha256": next(iter(coefficients)),
                      "source_graph_input_equal": True, "u2_pointwise_map_equal": True,
                      "independent_group_replay": group_replay,
                      "secondary_endpoints_prepared": secondary_verified,
                      "secondary_shared_coefficient_sha256": next(iter(secondary_coefficients)),
                      "rejected_mutations": rejected}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
