"""Reveal both seeds only after every prespecified arm has sealed run records."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def expected_arms(plan):
    matrix = plan["execution_matrix"]
    pairs = {
        (endpoint, arm)
        for endpoint in matrix["primary_endpoints"]
        for arm in matrix["primary_arms_per_endpoint"]
    }
    pairs.update(
        (endpoint, arm)
        for endpoint in matrix["secondary_endpoints"]
        for arm in matrix["secondary_arms_per_endpoint"]
    )
    assert len(pairs) == matrix["total_prepared_inputs"]
    return pairs


def require_committed_clean(paths):
    relative = []
    for path in paths:
        resolved = Path(path).resolve()
        if REPO not in resolved.parents:
            raise ValueError(f"sealed artifact outside repository: {resolved}")
        relative.append(str(resolved.relative_to(REPO)))
    subprocess.run(["git", "ls-files", "--error-unmatch", "--", *relative],
                   cwd=REPO, capture_output=True, text=True, check=True)
    dirty = subprocess.run(["git", "status", "--porcelain", "--", *relative],
                           cwd=REPO, capture_output=True, text=True, check=True).stdout
    if dirty:
        raise ValueError("sealed artifacts are dirty in the local checkout")


def reveal(plan, commitment_path, index_path, private_dir, output_path):
    commitment = json.loads(commitment_path.read_text())
    index = json.loads(index_path.read_text())
    if commitment["schema"] != "arity3-seed-commitment/v1":
        raise ValueError("invalid seed commitment schema")
    specification_path = (REPO / commitment["specification_path"]).resolve()
    if sha256(specification_path) != commitment["specification_sha256"]:
        raise ValueError("approved specification digest changed")
    if index["schema"] != "arity3-sealed-output-index/v1":
        raise ValueError("invalid sealed index schema")
    entries = index["entries"]
    pairs = [(entry["endpoint"], entry["arm"]) for entry in entries]
    if len(pairs) != len(set(pairs)) or set(pairs) != expected_arms(plan):
        raise ValueError("sealed index does not cover the complete prespecified arm matrix")
    target_seed = bytes.fromhex((private_dir / "target.seed").read_text().strip())
    k_seed = bytes.fromhex((private_dir / "k.seed").read_text().strip())
    if len(target_seed) != 32 or len(k_seed) != 32:
        raise ValueError("invalid private seed length")
    if hashlib.sha256(target_seed).hexdigest() != commitment["target_seed_sha256"]:
        raise ValueError("target seed commitment mismatch")
    if hashlib.sha256(k_seed).hexdigest() != commitment["k_seed_sha256"]:
        raise ValueError("k seed commitment mismatch")
    archived_paths = [commitment_path, index_path, specification_path]
    validated = []
    for entry in entries:
        run_dir = Path(entry["run_dir"]).resolve()
        manifest_path = Path(entry["input_manifest"]).resolve()
        receipt_path = run_dir / "receipt.json"
        if sha256(receipt_path) != entry["receipt_sha256"]:
            raise ValueError(f"run receipt digest mismatch: {run_dir}")
        receipt = json.loads(receipt_path.read_text())
        manifest = json.loads(manifest_path.read_text())
        if receipt["status"] != "completed_unreviewed" or receipt["admission_sha256"] is None:
            raise ValueError(f"run not admitted and completed: {run_dir}")
        if (manifest["endpoint"], manifest["arm"]) != (entry["endpoint"], entry["arm"]):
            raise ValueError(f"arm identity mismatch: {run_dir}")
        if receipt["manifest_sha256"] != sha256(manifest_path):
            raise ValueError(f"input manifest changed: {run_dir}")
        if manifest["target_seed_sha256"] != commitment["target_seed_sha256"]:
            raise ValueError(f"target seed binding mismatch: {run_dir}")
        if manifest["k_seed_sha256"] != commitment["k_seed_sha256"]:
            raise ValueError(f"k seed binding mismatch: {run_dir}")
        if manifest["seed_commitment_sha256"] != sha256(commitment_path):
            raise ValueError(f"public commitment binding mismatch: {run_dir}")
        for name, field in (("plan.json", None), ("prepare_input.py", "preparer_sha256"),
                            ("execute_prepared.py", "execute_sha256"),
                            ("collector.rs", "collector_source_sha256"),
                            ("count_verify.cpp", "count_source_sha256"),
                            ("verify_collector.py", "verifier_sha256"),
                            ("exact_interval.py", "inference_sha256")):
            expected = commitment["source_sha256"][name]
            actual = manifest["plan_sha256"] if field is None else receipt[field]
            if actual != expected:
                raise ValueError(f"frozen source changed: {name}, {run_dir}")
        phases = {phase["phase"]: phase for phase in receipt["phases"]}
        required = ("collector", "count", "verify", "interval")
        if set(phases) != set(required):
            raise ValueError(f"missing execution phase: {run_dir}")
        for phase in required:
            path = run_dir / f"{phase}.stdout"
            if phases[phase]["status"] != "completed" or phases[phase]["stdout_sha256"] != sha256(path):
                raise ValueError(f"unsealed phase output: {phase}, {run_dir}")
            archived_paths.append(path)
        archived_paths.extend((receipt_path, manifest_path))
        validated.append({"endpoint": entry["endpoint"], "arm": entry["arm"],
                          "receipt_sha256": entry["receipt_sha256"]})
    require_committed_clean(archived_paths)
    result = {
        "schema": "arity3-seed-reveal/v1", "status": "revealed_after_seal",
        "target_seed_hex": target_seed.hex(), "k_seed_hex": k_seed.hex(),
        "seed_commitment_sha256": sha256(commitment_path),
        "sealed_index_sha256": sha256(index_path),
        "sealed_arms": validated,
    }
    with output_path.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--commitment", type=Path, required=True)
    parser.add_argument("--sealed-index", type=Path, required=True)
    parser.add_argument("--private-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    plan = json.loads((HERE / "plan.json").read_text())
    result = reveal(plan, args.commitment, args.sealed_index,
                    args.private_dir, args.output)
    print(json.dumps({"status": result["status"], "sealed_arms": len(result["sealed_arms"]),
                      "output": str(args.output)}, sort_keys=True))


if __name__ == "__main__":
    main()
