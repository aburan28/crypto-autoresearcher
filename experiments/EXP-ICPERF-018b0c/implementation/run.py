"""Prepare frozen k11 inputs for EXP-ICPERF-018b0c.

This entry point performs deterministic input preparation only. Scientific
solver calls belong to an approved trial plan invoked through ``run``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from tools.icperf_binary_all_channels_xcnf import encode  # noqa: E402
from tools.icperf_binary_circuit_xcnf import allowed_values, write_gzip  # noqa: E402
from tools.icperf_binary_torsion_coordinate import gamma_for, phi_from_x  # noqa: E402
from tools.icperf_ordinary_binary_fixture import add, on_curve, scale  # noqa: E402

HERE = Path(__file__).resolve().parents[1]
INPUTS = HERE / "inputs"
FIXTURE = ROOT / "research/icperf_ordinary_binary_fixture_20261017/fixture.json"
CHAIN = ROOT / "research/icperf_binary_torsion_m8_chain_20261017/chain.json"
BASES = {
    "weighted": ROOT / "research/icperf_binary_torsion_k11_weighted_20261017/base.json",
    "local_random": ROOT / "research/icperf_binary_torsion_k11_local_control_20261017/base.json",
}
POSITIVE = ROOT / "research/icperf_binary_k11_planted_xcnf_20261017/complete/manifest.json"
DOMAIN = b"ICPERF-k11-natural-v1\0"
MAX_COUNTER = 1024
TARGETS = 8
WIDTH = 11
OFFSET = 4096


def sha(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def canonical(record: dict) -> bytes:
    return (json.dumps(record, indent=2, sort_keys=True) + "\n").encode()


def write_new(path: Path, record: dict) -> str:
    blob = canonical(record)
    with path.open("xb") as stream:
        stream.write(blob)
    return sha(blob)


def load(path: Path) -> tuple[dict, str]:
    blob = path.read_bytes()
    return json.loads(blob), sha(blob)


def target_schedule(fixture: dict, fixture_sha: str, gamma: int) -> dict:
    r = fixture["prime_order"]
    b = fixture["b_polynomial_bits"]
    generator = tuple(fixture["generator"])
    source = tuple(fixture["source_point"])
    torsion = scale(r, source, b)
    assert torsion is not None and scale(4, torsion, b) is None
    assert scale(r, generator, b) is None
    inverse4 = pow(4, -1, r)
    candidates: list[dict] = []
    admitted: list[dict] = []
    seen: set[tuple[int, int]] = set()
    for counter in range(MAX_COUNTER):
        block = hashlib.sha256(DOMAIN + bytes.fromhex(fixture_sha)
                               + counter.to_bytes(4, "big")).digest()
        scalar = 1 + int.from_bytes(block, "big") % (r - 1)
        subgroup = scale(scalar, generator, b)
        assert subgroup is not None and on_curve(subgroup, b)
        row = {"counter": counter, "scalar": scalar,
               "subgroup_point": list(subgroup)}
        if subgroup in seen:
            row["rejection"] = "duplicate_subgroup_point"
        else:
            root = scale(inverse4, subgroup, b)
            assert root is not None
            raw = [add(root, scale(c, torsion, b), b) for c in range(4)]
            if any(point is None for point in raw):
                row["rejection"] = "non_affine_raw_channel"
            elif any(point[0] in (0, gamma) for point in raw):
                row["rejection"] = "zero_or_pole_raw_x"
            else:
                assert all(on_curve(point, b) and scale(4, point, b) == subgroup
                           for point in raw)
                row["raw_channels"] = [list(point) for point in raw]
                row["channel_phi"] = [phi_from_x(point[0], gamma) for point in raw]
                row["target_index"] = len(admitted)
                admitted.append(row)
                seen.add(subgroup)
        candidates.append(row)
        if len(admitted) == TARGETS:
            break
    if len(admitted) != TARGETS:
        raise ValueError("fewer than eight admissible base-independent targets")
    return {"schema": "icperf-k11-target-schedule-v1", "experiment": "EXP-ICPERF-018b0c",
            "scope": "public known-answer input schedule; no solver or relation trial",
            "source_sha256": sha(Path(__file__).read_bytes()),
            "domain_hex": DOMAIN.hex(), "fixture_sha256": fixture_sha,
            "curve": {key: fixture[key] for key in ("field_degree", "field_polynomial",
                                                    "b_polynomial_bits", "prime_order", "cofactor")},
            "generator": list(generator), "source_point": list(source),
            "torsion_order_four": list(torsion), "inverse_cofactor_mod_r": inverse4,
            "gamma": gamma, "candidate_limit": MAX_COUNTER,
            "candidates": candidates, "admitted": admitted}


def prepare() -> dict:
    if not INPUTS.is_dir() or any(INPUTS.iterdir()):
        raise ValueError("inputs directory must exist and be empty; never overwrite a frozen input")
    fixture, fixture_sha = load(FIXTURE)
    chain, chain_sha = load(CHAIN)
    assert fixture["prime_order"] == chain["curve"]["prime_order"]
    assert fixture["field_polynomial"] == chain["curve"]["field_polynomial"]
    gamma = gamma_for(fixture["b_polynomial_bits"])
    assert gamma == chain["gamma"]
    bases = {label: load(path) for label, path in BASES.items()}
    assert all(base["curve"] == chain["curve"] and base["selected_offset"] == OFFSET
               for base, _ in bases.values())
    target = target_schedule(fixture, fixture_sha, gamma)
    target_sha = write_new(INPUTS / "target_manifest.json", target)
    positive, positive_sha = load(POSITIVE)
    controls = {}
    for label in BASES:
        row = next(item for item in positive["arms"] if item["base_kind"] == label)
        formula = ROOT / row["formula"]["path"]
        model = ROOT / row["model"]["path"]
        assert sha(formula.read_bytes()) == row["formula"]["sha256"]
        assert sha(model.read_bytes()) == row["model"]["sha256"]
        controls[label] = {"formula_path": rel(formula),
                           "formula_gzip_sha256": row["formula"]["sha256"],
                           "formula_raw_sha256": row["formula"]["raw_sha256"],
                           "known_model_path": rel(model),
                           "known_model_sha256": row["model"]["sha256"],
                           "source_manifest_sha256": positive_sha,
                           "source_row": row}
    positive_record = {"schema": "icperf-k11-positive-inputs-v1",
                       "experiment": "EXP-ICPERF-018b0c",
                       "source_manifest_path": rel(POSITIVE),
                       "source_manifest_sha256": positive_sha,
                       "controls": controls}
    positive_input_sha = write_new(INPUTS / "positive_manifest.json", positive_record)
    arms = []
    for target_row in target["admitted"]:
        for label, (base, base_sha) in bases.items():
            allowed = allowed_values("torsion_phi", base, OFFSET, WIDTH)
            assert len(allowed) == 632
            for channel, target_phi in enumerate(target_row["channel_phi"]):
                raw, meta = encode("torsion_phi", WIDTH, OFFSET, target_phi, gamma, allowed)
                filename = f"natural_{target_row['target_index']:02d}_{label}_channel_{channel}.xcnf.gz"
                path = INPUTS / filename
                gzip_sha = write_gzip(path, raw)
                arms.append({"target_index": target_row["target_index"],
                             "counter": target_row["counter"], "base_kind": label,
                             "base_sha256": base_sha, "channel": channel,
                             "gzip_path": rel(path), "gzip_sha256": gzip_sha,
                             **meta})
    assert len(arms) == 64
    formula_record = {"schema": "icperf-k11-natural-formulas-v1",
                      "experiment": "EXP-ICPERF-018b0c",
                      "scope": "deterministic XCNF inputs; no solver observation",
                      "source_sha256": sha(Path(__file__).read_bytes()),
                      "target_manifest_sha256": target_sha,
                      "positive_manifest_sha256": positive_input_sha,
                      "chain_sha256": chain_sha,
                      "encoder_sha256": sha((ROOT / "tools/icperf_binary_all_channels_xcnf.py").read_bytes()),
                      "circuit_sha256": sha((ROOT / "tools/icperf_binary_circuit_xcnf.py").read_bytes()),
                      "bases": {label: digest for label, (_, digest) in bases.items()},
                      "arms": arms}
    formula_sha = write_new(INPUTS / "formula_manifest.json", formula_record)
    return {"targets": len(target["admitted"]), "formulas": len(arms),
            "target_manifest_sha256": target_sha,
            "positive_manifest_sha256": positive_input_sha,
            "formula_manifest_sha256": formula_sha}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prepare", choices=["prepare"])
    args = parser.parse_args()
    assert args.prepare == "prepare"
    print(json.dumps(prepare(), sort_keys=True))


if __name__ == "__main__":
    main()
