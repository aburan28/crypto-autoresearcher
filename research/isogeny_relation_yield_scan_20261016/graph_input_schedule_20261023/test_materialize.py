"""Replay the three full-quota P37 preparation controls and rejection cases."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOTS = STUDY / "seed_custody_20261022/control"
CONTROL = HERE / "control"
sys.path.insert(0, str(HERE))
from materialize import parse_prepared  # noqa: E402

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
    print(json.dumps({"schema": "ectd.graph-materializer-control.v1", "status": "pass",
                      "scope": "P37 vertex 0, three public-root full-quota prepared arms",
                      "target_count_per_arm": 2048, "base_signed_points": 3200,
                      "coefficient_vector_sha256": next(iter(coefficients)),
                      "source_graph_input_equal": True, "u2_pointwise_map_equal": True,
                      "independent_group_replay": group_replay,
                      "rejected_mutations": rejected}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
