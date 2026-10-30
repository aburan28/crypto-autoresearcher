#!/usr/bin/env python3
"""Post-data replay of sealed output; never executes a scientific search.

The only correction to the frozen verifier is equality of sparse counters:
an absent integer counter and an explicit zero denote the same count. Native
invalid_output remains invalid_output; this produces a separate receipt.
"""
import argparse
import hashlib
import inspect
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "tools"), str(ROOT / "research/prime_sat_followup_20261029")]
import artifact_store
import driver
import encoding


def same_counts(left, right):
    if any(type(v) is not int or v < 0 for v in [*left.values(), *right.values()]):
        return False
    return all(left.get(k, 0) == right.get(k, 0) for k in left.keys() | right.keys())


def main(raw_path, out):
    if out.exists():
        raise FileExistsError(out)
    protocol = json.loads((ROOT / "experiments/EXP-PNEXT-624f41/protocol.json").read_text())
    for rel, expected in protocol["extensions"]["source_sha256"].items():
        if hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() != expected:
            raise ValueError("frozen source changed: " + rel)
    receipt_path = raw_path.parent / "execution-receipt.json"
    receipt = artifact_store.read_json(receipt_path)
    if (receipt["status"], receipt["returncode"], receipt["check_returncode"]) != ("invalid_output", 0, 1):
        raise ValueError("unexpected native receipt")
    for name, expected in receipt["artifact_sha256"].items():
        if artifact_store.content_digest(raw_path.parent / name) != expected:
            raise ValueError("sealed artifact changed: " + name)
    assert same_counts({"a": 3}, {"a": 3, "b": 0})
    assert not same_counts({"a": 3}, {"a": 3, "b": 1})
    assert not same_counts({"a": 3}, {"a": 4})
    assert not same_counts({}, {"a": -1})
    assert not same_counts({}, {"a": False})
    source = inspect.getsource(encoding.verify)
    old = 'or got["costs"] != arm["census"]["costs"]'
    new = 'or not same_counts(got["costs"], arm["census"]["costs"])'
    if source.count(old) != 1:
        raise ValueError("expected exact narrow verifier correction")
    namespace = dict(encoding.__dict__, same_counts=same_counts)
    exec(compile(source.replace(old, new), str(__file__) + ":corrected_verify", "exec"), namespace)
    encoding.verify = namespace["verify"]
    checked = driver.verify(raw_path)
    result = {"schema": "prime-sat-supplemental-check/v1",
              "recorded_at": datetime.now(timezone.utc).isoformat(),
              "filed_before_affected_data": False, "exploratory_only": True,
              "native_status_unchanged": receipt["status"],
              "native_receipt_sha256": hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
              "checker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "raw_sha256": artifact_store.content_digest(raw_path),
              "correction": {"before": old, "after": new},
              "counter_controls_passed": 5, "result": checked,
              "scope": "Replay existing models, certificates, chart sets and counters. No new learner run, no native status transition, no independent scientific review."}
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps(result, sort_keys=True))
    return 0 if checked["valid"] else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.raw.resolve(), args.out.resolve()))
