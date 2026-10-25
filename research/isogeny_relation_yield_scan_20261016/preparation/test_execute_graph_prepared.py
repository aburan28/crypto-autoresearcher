"""One fixed public P29 check-vertex control for the phased graph runner."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

from prepare_graph_input import prepare
from execute_graph_prepared import check_frozen_sources, require_scientific_seed_mode

STUDY = Path(__file__).resolve().parents[1]
BASE_ROOT = b"B" * 32
TARGET_ROOT = b"T" * 32
VERIFIER_ROOT = b"V" * 32


def check_source_binding_control():
    with TemporaryDirectory() as scratch:
        checkout = Path(scratch)
        source = checkout / "source.py"
        source.write_text("value = 1\n")
        subprocess.run(["git", "init", "-q"], cwd=checkout, check=True)
        subprocess.run(["git", "add", "source.py"], cwd=checkout, check=True)
        subprocess.run(["git", "-c", "user.name=Control", "-c", "user.email=control@example.invalid",
                        "commit", "-q", "-m", "freeze"], cwd=checkout, check=True)
        frozen = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=checkout,
                                         text=True).strip()
        (checkout / "runs").mkdir()
        (checkout / "runs" / "output.json").write_text("{}\n")
        check_frozen_sources(checkout, [source], frozen)
        subprocess.run(["git", "add", "runs/output.json"], cwd=checkout, check=True)
        subprocess.run(["git", "-c", "user.name=Control", "-c", "user.email=control@example.invalid",
                        "commit", "-q", "-m", "publish run"], cwd=checkout, check=True)
        current = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=checkout,
                                          text=True).strip()
        if current == frozen:
            raise AssertionError("run commit did not advance HEAD")
        check_frozen_sources(checkout, [source], frozen)
        source.write_text("value = 2\n")
        try:
            check_frozen_sources(checkout, [source], frozen)
        except ValueError:
            pass
        else:
            raise AssertionError("modified source passed the commit binding")
        subprocess.run(["git", "restore", "source.py"], cwd=checkout, check=True)
        for invalid in ("0" * 40, "not-a-commit"):
            try:
                check_frozen_sources(checkout, [source], invalid)
            except ValueError:
                pass
            else:
                raise AssertionError("invalid source commit passed the binding")
        subprocess.run(["git", "switch", "--orphan", "unrelated"], cwd=checkout,
                       check=True, stdout=subprocess.DEVNULL)
        source.write_text("value = 1\n")
        subprocess.run(["git", "add", "source.py"], cwd=checkout, check=True)
        subprocess.run(["git", "-c", "user.name=Control", "-c", "user.email=control@example.invalid",
                        "commit", "-q", "-m", "unrelated identical source"], cwd=checkout, check=True)
        try:
            check_frozen_sources(checkout, [source], frozen)
        except ValueError:
            pass
        else:
            raise AssertionError("nonancestor source commit passed the binding")
    return {"frozen_source_commit": frozen, "later_run_commit": current,
            "ancestor_and_mutation_checks": "pass"}


def main():
    check_source_binding_control()
    parser = argparse.ArgumentParser()
    parser.add_argument("--collector", type=Path, required=True)
    parser.add_argument("--count-verifier", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--target-count", type=int, choices=(8, 128), default=8)
    parser.add_argument("--index", type=int, choices=(0, 8), default=8)
    args = parser.parse_args()
    root = args.output.resolve()
    root.mkdir(mode=0o700, parents=True, exist_ok=False)
    arm = "low_x" if args.index == 0 else "graph_transport"
    payload, meta = prepare(STUDY / "walk-p29-2048-attempt2.jsonl", args.index,
                            arm, "discovery", BASE_ROOT, TARGET_ROOT, args.target_count)
    scientific_payload, scientific_meta = prepare(
        STUDY / "walk-p29-2048-attempt2.jsonl", args.index, arm, "discovery",
        BASE_ROOT, TARGET_ROOT, args.target_count, VERIFIER_ROOT)
    require_scientific_seed_mode(scientific_meta)
    if scientific_payload == payload:
        raise AssertionError("independent verifier root did not change target points")
    for key, value in (("seed_mode", None),
                       ("verifier_root_sha256", meta["target_root_sha256"])):
        altered = dict(scientific_meta)
        altered[key] = value
        try:
            require_scientific_seed_mode(altered)
        except ValueError:
            pass
        else:
            raise AssertionError("scientific executor accepted an invalid seed mode")
    try:
        require_scientific_seed_mode(meta)
    except ValueError:
        pass
    else:
        raise AssertionError("historical two-root control passed scientific gate")
    prepared = root / "prepared.txt"
    manifest = root / "manifest.json"
    prepared.write_bytes(payload)
    manifest.write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n")
    refusal_command = [sys.executable, str(STUDY / "preparation/execute_graph_prepared.py"),
                       "--input", str(prepared), "--manifest", str(manifest),
                       "--collector", str(args.collector), "--count-verifier", str(args.count_verifier),
                       "--output", str(root / "scientific-rejected"),
                       "--admission", str(root / "unused-admission.json")]
    refusal = subprocess.run(refusal_command, capture_output=True, text=True)
    (root / "scientific-refusal.stdout").write_text(refusal.stdout)
    (root / "scientific-refusal.stderr").write_text(refusal.stderr)
    if (refusal.returncode == 0 or
            "scientific graph input requires three distinct committed roots" not in refusal.stderr or
            (root / "scientific-rejected").exists()):
        raise AssertionError("old two-root input passed scientific runner gate")
    command = [sys.executable, str(STUDY / "preparation/execute_graph_prepared.py"),
               "--input", str(prepared), "--manifest", str(manifest),
               "--collector", str(args.collector), "--count-verifier", str(args.count_verifier),
               "--output", str(root / "attempt"), "--control", "--watchdog-seconds", "120",
               "--memory-gib", "2"]
    result = subprocess.run(command, capture_output=True, text=True)
    (root / "wrapper.stdout").write_text(result.stdout)
    (root / "wrapper.stderr").write_text(result.stderr)
    (root / "command.json").write_text(json.dumps(command, indent=2) + "\n")
    if result.returncode:
        raise RuntimeError(f"graph control runner failed: {result.returncode}; see saved outputs")
    receipt = json.loads((root / "attempt/receipt.json").read_text())
    rank = json.loads((root / "attempt/rank_verify.stdout").read_text())
    checked = json.loads((root / "attempt/input_verify.stdout").read_text())
    if (receipt["status"] != "completed_control" or checked["status"] != "pass" or
            rank["status"] != "valid" or not rank["independent_ordered_count_match"] or
            rank["targets"] != args.target_count):
        raise AssertionError("fixed graph collector control did not verify")
    print(json.dumps({"status": "pass", "mode": receipt["mode"], "stratum": "P29",
                      "index": args.index, "arm": arm, "targets": rank["targets"],
                      "useful_targets": rank["useful_targets"],
                      "ordered_count_match": rank["independent_ordered_count_match"],
                      "input_sha256": hashlib.sha256(payload).hexdigest(),
                      "collector_sha256": receipt["bindings"]["collector_binary_sha256"],
                      "count_sha256": receipt["bindings"]["count_binary_sha256"],
                      "receipt_sha256": hashlib.sha256((root / "attempt/receipt.json").read_bytes()).hexdigest(),
                      "limit": "fixed public implementation control; outside discovery inference"}, sort_keys=True))


if __name__ == "__main__":
    main()
