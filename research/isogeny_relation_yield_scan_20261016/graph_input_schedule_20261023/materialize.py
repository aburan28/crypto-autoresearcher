"""Bind one fixed graph-discovery arm to an exact prepared input.

This is preparation, not scientific execution or Coordinator admission. The
schedule, commitment and graph are checked before an output directory exists.
The completed binding can be checked again after moving the output directory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
SCHEDULE_DIR = STUDY / "graph_schedule_20261023"
PREPARER = STUDY / "preparation/prepare_graph_input.py"
SOLVE_PREPARER = STUDY / "preparation/prepare_graph_solve_input.py"
SOLVE_TARGETS = {"P29": 32768, "P37": 32768}
sys.path.insert(0, str(STUDY / "preparation"))
from prepare_graph_input import SCHEDULE, target_coefficients  # noqa: E402

WALKS = {"P29": STUDY / "walk-p29-2048-attempt2.jsonl",
         "P37": STUDY / "walk-p37-256.jsonl"}
def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def load_schedule(arm_key: str, stage: str = "discovery") -> tuple[dict, dict]:
    if stage not in ("discovery", "confirmation", "solve"):
        raise ValueError("unsupported graph schedule stage")
    manifest = json.loads((SCHEDULE_DIR / "manifest.json").read_text())
    receipt = json.loads((SCHEDULE_DIR / "verification.json").read_text())
    schedule_path = SCHEDULE_DIR / "discovery-arms.jsonl"
    schedule_sha = sha(schedule_path)
    if (manifest.get("schema") != "ectd-graph-discovery-schedule/v1" or
            manifest.get("arms") != 8206 or manifest.get("target_probes") != 60889088 or
            manifest.get("schedule_sha256") != schedule_sha or
            manifest.get("graph_manifest_sha256") != sha(STUDY / "manifest-v2.json") or
            receipt.get("status") != "pass" or receipt.get("arms_checked") != 8206 or
            receipt.get("schedule_sha256") != schedule_sha or
            receipt.get("counts") != manifest.get("counts")):
        raise ValueError("candidate schedule or independent verification differs")
    found = None
    seen = set()
    rows = 0
    for line in schedule_path.open(encoding="utf-8"):
        row = json.loads(line)
        key = row.get("arm_key")
        if not isinstance(key, str) or key in seen:
            raise ValueError("missing or duplicate schedule arm key")
        seen.add(key)
        rows += 1
        if key == arm_key:
            found = row
    if rows != manifest["arms"] or found is None:
        raise ValueError("arm absent from complete frozen candidate schedule")
    stratum = found["stratum"]
    config = SCHEDULE.get(stratum)
    if (config is None or found["base_rule"] not in (
            "low_x", "mid_x", "random_x", "power_x", "graph_transport",
            "u2_native", "u2_transport") or
            found["discovery_targets"] != config["discovery"] or
            found["base_x_orbits"] != config["B"] or
            not 0 <= found["path_index"] <= (2048 if stratum == "P29" else 256)):
        raise ValueError("arm parameters differ from fixed discovery schedule")
    found = dict(found)
    found["stage"] = stage
    found["target_count"] = SOLVE_TARGETS[stratum] if stage == "solve" else config[stage]
    return manifest, found


def read_root(path: Path) -> bytes:
    text = path.read_text().strip()
    if len(text) != 64 or any(char not in "0123456789abcdef" for char in text):
        raise ValueError("root must be a lowercase 256-bit hex value")
    return bytes.fromhex(text)


def check_commitment(row: dict, root_paths: dict[str, Path], commitment_path: Path) -> tuple[dict, dict]:
    roots = {name: read_root(path) for name, path in root_paths.items()}
    if len(set(roots.values())) != 3:
        raise ValueError("base, target and verifier roots must be distinct")
    commitment = json.loads(commitment_path.read_text())
    walk = WALKS[row["stratum"]]
    graph = json.loads((STUDY / "manifest-v2.json").read_text())
    verification_name = "verification-" + row["stratum"].lower() + "-full.json"
    if (commitment.get("schema") != "isogeny-relation-seed-commitment/v2" or
            graph["files"].get(walk.name, {}).get("sha256") != sha(walk) or
            graph["files"].get(verification_name, {}).get("sha256") != sha(STUDY / verification_name) or
            commitment.get("graph_manifest_sha256") != sha(STUDY / "manifest-v2.json") or
            commitment.get("graph_sha256") != sha(walk)):
        raise ValueError("commitment differs from certified graph")
    for name, root in roots.items():
        if commitment.get(name + "_root_sha256") != hashlib.sha256(root).hexdigest():
            raise ValueError("root differs from commitment: " + name)
    sources = [PREPARER, ROOT / "research/conductor_relation_yield_20261014/prepare_input.py",
               ROOT / "research/conductor_relation_yield_20261014/verify_collector.py"]
    if row["stage"] == "solve":
        sources.append(SOLVE_PREPARER)
    for source in sources:
        relative = source.relative_to(ROOT).as_posix()
        if commitment.get("source_sha256", {}).get(relative) != sha(source):
            raise ValueError("preparation source differs from commitment: " + relative)
    if row["base_rule"] == "graph_transport":
        checkpoint = STUDY / row["checkpoint_path"]
        if row.get("checkpoint_sha256") != sha(checkpoint):
            raise ValueError("scheduled graph checkpoint differs")
        for key, source in (("checkpoint_manifest_sha256", "manifest"),
                            ("checkpoint_terminal_sha256", "terminal")):
            path = STUDY / json.loads((SCHEDULE_DIR / "manifest.json").read_text())["checkpoint_bindings"][row["stratum"]][source]
            if commitment.get(key) != sha(path):
                raise ValueError("graph transport checkpoint commitment differs")
    return roots, commitment


def parse_prepared(path: Path) -> tuple[list[int], list[list[int]], list[list[int]]]:
    with path.open(encoding="utf-8") as stream:
        parts = next(stream).split()
        if len(parts) != 7 or parts[0] != "curve":
            raise ValueError("invalid prepared curve header")
        header = [int(value) for value in parts[1:]]
        base = []
        for index in range(header[4]):
            parts = next(stream).split()
            if len(parts) != 4 or parts[:2] != ["base", str(index)]:
                raise ValueError("invalid prepared base row")
            base.append([int(parts[2]), int(parts[3])])
        targets = []
        for index in range(header[5]):
            parts = next(stream).split()
            if len(parts) != 6 or parts[:2] != ["target", str(index)]:
                raise ValueError("invalid prepared target row")
            targets.append([int(value) for value in parts[2:]])
        if stream.readline():
            raise ValueError("prepared input has trailing rows")
    return header, base, targets


def expected_binding(row: dict, roots: dict[str, bytes],
                     commitment_path: Path, prepared_dir: Path,
                     stage: str = "discovery") -> dict:
    input_path = prepared_dir / "prepared.txt"
    input_manifest_path = prepared_dir / "manifest.json"
    prepared = json.loads(input_manifest_path.read_text())
    header, base, targets = parse_prepared(input_path)
    output_model = row.get("output_model", row["model"])
    output_generator = row.get("output_generator", row["generator"])
    expected = {"stratum": row["stratum"], "index": row["path_index"],
                "arm": row["base_rule"], "stage": stage,
                "j": row["model"]["j"], "target_count": row["target_count"],
                "base_abscissae": row["base_x_orbits"], "generator": output_generator,
                "graph_sha256": sha(WALKS[row["stratum"]]),
                "commitment_sha256": sha(commitment_path),
                "input_sha256": sha(input_path)}
    if any(prepared.get(key) != value for key, value in expected.items()):
        raise ValueError("prepared input metadata differs from scheduled arm")
    commitment = json.loads(commitment_path.read_text())
    if prepared.get("source_sha256") != commitment.get("source_sha256"):
        raise ValueError("prepared source bindings differ from commitment")
    if row["base_rule"] == "graph_transport":
        schedule_manifest = json.loads((SCHEDULE_DIR / "manifest.json").read_text())
        checkpoint_path = STUDY / row["checkpoint_path"]
        checkpoint_bindings = schedule_manifest["checkpoint_bindings"][row["stratum"]]
        expected_checkpoints = {
            "checkpoint_sha256": row["checkpoint_sha256"],
            "checkpoint_manifest_sha256": checkpoint_bindings["manifest_sha256"],
            "checkpoint_terminal_sha256": checkpoint_bindings["terminal_sha256"],
        }
        if (expected_checkpoints["checkpoint_sha256"] != sha(checkpoint_path) or
                commitment.get("checkpoint_manifest_sha256") != expected_checkpoints["checkpoint_manifest_sha256"] or
                commitment.get("checkpoint_terminal_sha256") != expected_checkpoints["checkpoint_terminal_sha256"]):
            raise ValueError("scheduled graph-transport checkpoint differs from commitment")
        for key in ("checkpoint_sha256", "checkpoint_manifest_sha256",
                    "checkpoint_terminal_sha256"):
            if prepared.get(key) != expected_checkpoints[key]:
                raise ValueError("prepared graph-transport checkpoint differs")
    if (prepared.get("schema") != "isogeny-relation-input/v1" or
            prepared.get("seed_mode") != "independent_verifier_root" or
            prepared.get("schedule_conformant") is not True or
            header != [row["p"], output_model["a"], output_model["b"], row["r"],
                       2 * row["base_x_orbits"], row["target_count"]] or
            len(base) != 2 * row["base_x_orbits"] or
            len(targets) != row["target_count"] or
            prepared.get("base_sha256") != hashlib.sha256(json.dumps(base, separators=(",", ":")).encode()).hexdigest() or
            prepared.get("target_vector_sha256") != hashlib.sha256(json.dumps(
                [[a, b, [x, y]] for a, b, x, y in targets], separators=(",", ":")).encode()).hexdigest()):
        raise ValueError("prepared rows differ from schedule or metadata")
    for name, root in roots.items():
        if prepared.get(name + "_root_sha256") != hashlib.sha256(root).hexdigest():
            raise ValueError("prepared root differs: " + name)
    k, coefficients, _ = target_coefficients(
        roots["target"], row["stratum"], stage, row["r"],
        row["target_count"], roots["verifier"])
    actual_coefficients = [[a, b] for a, b, _, _ in targets]
    if actual_coefficients != [[a, b] for a, b, _ in coefficients]:
        raise ValueError("prepared target coefficients differ from fixed stream")
    coefficient_sha = hashlib.sha256(canonical(actual_coefficients)).hexdigest()
    return {"schema": "ectd.graph-prepared-arm-binding.v1",
            "mode": "preparation_only", "arm_key": row["arm_key"],
            "schedule_sha256": sha(SCHEDULE_DIR / "discovery-arms.jsonl"),
            "schedule_manifest_sha256": sha(SCHEDULE_DIR / "manifest.json"),
            "commitment_sha256": sha(commitment_path),
            "prepared_input_sha256": sha(input_path),
            "prepared_manifest_sha256": sha(input_manifest_path),
            "coefficient_vector_sha256": coefficient_sha,
            "q_scalar_commitment_sha256": hashlib.sha256(str(k).encode()).hexdigest(),
            **({"stage": stage} if stage != "discovery" else {}),
            "target_count": row["target_count"],
            "control_reference": row.get("control_reference")}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "check"))
    parser.add_argument("--arm-key", required=True)
    parser.add_argument("--stage", choices=("discovery", "confirmation", "solve"), default="discovery")
    parser.add_argument("--base-root-file", type=Path, required=True)
    parser.add_argument("--target-root-file", type=Path, required=True)
    parser.add_argument("--verifier-root-file", type=Path, required=True)
    parser.add_argument("--commitment", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    _, row = load_schedule(args.arm_key, args.stage)
    root_paths = {"base": args.base_root_file, "target": args.target_root_file,
                  "verifier": args.verifier_root_file}
    roots, _ = check_commitment(row, root_paths, args.commitment)
    if args.action == "prepare":
        if args.output_dir.exists():
            raise ValueError("prepared output exists; never overwrite an attempt")
        preparer = SOLVE_PREPARER if args.stage == "solve" else PREPARER
        command = [sys.executable, str(preparer), "--walk", str(WALKS[row["stratum"]]),
                   "--index", str(row["path_index"]), "--arm", row["base_rule"]]
        if args.stage != "solve":
            command += ["--stage", args.stage]
        command += ["--base-root-file", str(args.base_root_file),
                   "--target-root-file", str(args.target_root_file),
                   "--verifier-root-file", str(args.verifier_root_file),
                   "--commitment", str(args.commitment), "--output-dir", str(args.output_dir)]
        subprocess.run(command, check=True)
    binding = expected_binding(row, roots, args.commitment, args.output_dir, args.stage)
    binding_path = args.output_dir / "binding.json"
    if args.action == "prepare":
        with binding_path.open("x", encoding="utf-8") as stream:
            json.dump(binding, stream, indent=2, sort_keys=True)
            stream.write("\n")
    elif json.loads(binding_path.read_text()) != binding:
        raise ValueError("saved prepared-arm binding differs")
    print(json.dumps(binding, sort_keys=True))


if __name__ == "__main__":
    main()
