"""Write and independently verify the fresh P29 E2/E3 schedule supplement.

This versioned side schedule leaves the already archived 8,206-arm graph
schedule byte-for-byte intact. It adds only the prespecified secondary
same-conductor controls and does not select graph finalists.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
SPEC = ROOT / "experiments/EXP-ECTD-0cf008/specification.yaml"
OUTPUT = HERE / "p29-secondary-floor-arms.jsonl"
MANIFEST = HERE / "p29-secondary-floor-manifest.json"
VERIFICATION = HERE / "p29-secondary-floor-verification.json"
sys.path.insert(0, str(ROOT))
from research.conductor_relation_yield_20261014.verify_collector import (  # noqa: E402
    Curve, certify_group,
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def j_invariant(p: int, a: int, b: int) -> int:
    denominator = (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p
    if denominator == 0:
        raise ValueError("singular secondary curve")
    return 1728 * 4 * pow(a, 3, p) * pow(denominator, -1, p) % p


def expected_rows() -> tuple[list[dict], dict]:
    doc = json.loads(SPEC.read_text())["experiment"]
    p29 = next(row for row in doc["inputs"]["primary_pairs"] if row["id"] == "P29")
    spec_sha = sha(SPEC)
    rows = []
    for endpoint in doc["inputs"]["secondary_P29_floor_models"]:
        if endpoint["f_E"] != p29["f_pi"] or endpoint["id"] not in ("P29-E2", "P29-E3"):
            raise ValueError("secondary model does not match the frozen P29 floor identity")
        model = {"a": endpoint["a"], "b": endpoint["b"],
                 "j": j_invariant(p29["p"], endpoint["a"], endpoint["b"])}
        generator = [endpoint["gx"], endpoint["gy"]]
        curve = Curve(p29["p"], model["a"], model["b"], p29["r"])
        certify_group(curve, tuple(generator))
        for arm in ("low_x", "random_x"):
            rows.append({
                "arm_key": f"{endpoint['id']}-{arm}",
                "stratum": "P29", "endpoint_id": endpoint["id"],
                "curve_role": "secondary_same_conductor_floor",
                "source_spec_sha256": spec_sha,
                "curve_source_spec_sha256": doc["inputs"]["secondary_source_spec_sha256"],
                "p": p29["p"], "r": p29["r"], "model": model,
                "generator": generator, "conductor_factor": endpoint["f_E"],
                "base_rule": arm, "base_x_orbits": p29["B"],
                "discovery_targets": 8192,
                "target_domain": ["P29", "discovery"],
                "target_coefficients_shared_with": "P29 graph discovery stream",
                "finalist_selection_eligible": False,
            })
    return rows, p29


def write_once(path: Path, payload: bytes) -> None:
    if path.exists():
        if path.read_bytes() != payload:
            raise ValueError(f"refusing to overwrite frozen schedule artifact: {path}")
    else:
        path.write_bytes(payload)


def main() -> None:
    rows, p29 = expected_rows()
    encoded_rows = b"".join((json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n").encode()
                            for row in rows)
    write_once(OUTPUT, encoded_rows)
    receipt = {
        "schema": "ectd-p29-secondary-floor-schedule/v1",
        "status": "candidate_unapproved",
        "source_specification": str(SPEC.relative_to(ROOT)),
        "source_specification_sha256": sha(SPEC),
        "curve_source_specification_sha256": json.loads(SPEC.read_text())["experiment"]["inputs"]["secondary_source_spec_sha256"],
        "primary_graph_schedule_sha256": sha(HERE / "discovery-arms.jsonl"),
        "p": p29["p"], "r": p29["r"], "conductor_factor": p29["f_pi"],
        "arms": len(rows), "target_count_per_arm": 8192,
        "target_probes": len(rows) * 8192,
        "endpoints": ["P29-E2", "P29-E3"], "base_rules": ["low_x", "random_x"],
        "same_target_coefficient_stream": True,
        "finalist_selection_eligible": False,
        "schedule_path": str(OUTPUT.relative_to(ROOT)),
        "schedule_sha256": sha(OUTPUT),
        "generator_sha256": sha(Path(__file__)),
        "checks": ["exact frozen endpoint labels and source hash",
                   "same P29 field, subgroup order, and conductor factor",
                   "nonsingular curve and exact prime-order generator certificate",
                   "fixed native/random base rules and graph discovery target quota"],
        "limits": "Schedule identity only; no target preparation, relation, rank, or ECDLP result",
    }
    encoded_manifest = (json.dumps(receipt, sort_keys=True, indent=2) + "\n").encode()
    write_once(MANIFEST, encoded_manifest)
    verification = verify()
    encoded_verification = (json.dumps(verification, sort_keys=True, indent=2) + "\n").encode()
    write_once(VERIFICATION, encoded_verification)
    print(json.dumps(verification, sort_keys=True))


def verify() -> dict:
    expected, p29 = expected_rows()
    manifest = json.loads(MANIFEST.read_text())
    actual = [json.loads(line) for line in OUTPUT.read_text().splitlines()]
    if actual != expected:
        raise ValueError("secondary floor schedule rows differ from exact frozen identities")
    expected_counts = {endpoint: {arm: 1 for arm in ("low_x", "random_x")}
                       for endpoint in ("P29-E2", "P29-E3")}
    counts: dict[str, dict[str, int]] = {}
    for row in actual:
        counts.setdefault(row["endpoint_id"], {})[row["base_rule"]] = counts.setdefault(
            row["endpoint_id"], {}).get(row["base_rule"], 0) + 1
        curve = Curve(row["p"], row["model"]["a"], row["model"]["b"], row["r"])
        certify_group(curve, tuple(row["generator"]))
    if (counts != expected_counts or manifest.get("arms") != 4 or
            manifest.get("target_count_per_arm") != 8192 or
            manifest.get("target_probes") != 32768 or
            manifest.get("source_specification_sha256") != sha(SPEC) or
            manifest.get("primary_graph_schedule_sha256") != sha(HERE / "discovery-arms.jsonl") or
            manifest.get("schedule_sha256") != sha(OUTPUT) or
            manifest.get("generator_sha256") != sha(Path(__file__)) or
            manifest.get("p") != p29["p"] or manifest.get("r") != p29["r"]):
        raise ValueError("secondary floor manifest or exact counts differ")
    return {"schema": "ectd-p29-secondary-floor-verification/v1",
            "status": "pass", "arms_checked": len(actual), "target_probes": 32768,
            "schedule_sha256": sha(OUTPUT), "manifest_sha256": sha(MANIFEST),
            "counts": counts,
            "limit": "Identity and schedule validation only; not scientific execution"}


if __name__ == "__main__":
    main()
