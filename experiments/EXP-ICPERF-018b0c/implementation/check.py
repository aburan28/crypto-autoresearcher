"""Independently replay the prepared k11 pilot inputs and positive witnesses.

Reads serialized XCNF and point data. This does not invoke a solver and does
not turn the public known-answer targets into a discrete-log measurement.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from tools.icperf_binary_all_channels_xcnf_verify import evaluate  # noqa: E402
from tools.icperf_binary_circuit_xcnf_verify import parse, verify_arm  # noqa: E402
from tools.icperf_binary_k11_solver import check_xcnf_model, parse_model  # noqa: E402
from tools.icperf_binary_root_certificate import certificate  # noqa: E402
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
DOMAIN = b"ICPERF-k11-natural-v1\0"


def sha(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def load(path: Path) -> tuple[dict, str]:
    blob = path.read_bytes()
    return json.loads(blob), sha(blob)


def check_targets(target: dict, fixture: dict, fixture_sha: str, gamma: int) -> None:
    assert target["fixture_sha256"] == fixture_sha
    assert bytes.fromhex(target["domain_hex"]) == DOMAIN
    assert target["gamma"] == gamma
    assert target["candidate_limit"] == 1024
    assert len(target["admitted"]) == 8
    r, b = fixture["prime_order"], fixture["b_polynomial_bits"]
    generator = tuple(fixture["generator"])
    torsion = scale(r, tuple(fixture["source_point"]), b)
    assert torsion is not None and scale(4, torsion, b) is None
    assert target["torsion_order_four"] == list(torsion)
    inverse4 = pow(4, -1, r)
    assert target["inverse_cofactor_mod_r"] == inverse4
    accepted = []
    seen = set()
    for counter, row in enumerate(target["candidates"]):
        assert row["counter"] == counter
        hash_value = hashlib.sha256(DOMAIN + bytes.fromhex(fixture_sha)
                                    + counter.to_bytes(4, "big")).digest()
        scalar = 1 + int.from_bytes(hash_value, "big") % (r - 1)
        point = scale(scalar, generator, b)
        assert point is not None and on_curve(point, b)
        assert row["scalar"] == scalar and row["subgroup_point"] == list(point)
        if point in seen:
            assert row["rejection"] == "duplicate_subgroup_point"
            continue
        root = scale(inverse4, point, b)
        raw = [add(root, scale(c, torsion, b), b) for c in range(4)]
        if any(p is None for p in raw):
            assert row["rejection"] == "non_affine_raw_channel"
        elif any(p[0] in (0, gamma) for p in raw):
            assert row["rejection"] == "zero_or_pole_raw_x"
        else:
            assert row["target_index"] == len(accepted)
            assert row["raw_channels"] == [list(p) for p in raw]
            assert row["channel_phi"] == [phi_from_x(p[0], gamma) for p in raw]
            assert all(scale(4, p, b) == point for p in raw)
            accepted.append(row)
            seen.add(point)
        if len(accepted) == 8:
            assert counter == len(target["candidates"]) - 1
            break
    assert accepted == target["admitted"]


def check_positives(positive: dict, bases: dict, chain: dict) -> list[dict]:
    source_path = ROOT / positive["source_manifest_path"]
    original, digest = load(source_path)
    assert digest == positive["source_manifest_sha256"]
    checked = []
    for label in ("weighted", "local_random"):
        row = next(entry for entry in original["arms"] if entry["base_kind"] == label)
        control = positive["controls"][label]
        assert control["source_row"] == row
        formula_path = ROOT / control["formula_path"]
        model_path = ROOT / control["known_model_path"]
        packed = formula_path.read_bytes()
        raw = gzip.decompress(packed)
        assert sha(packed) == row["formula"]["sha256"] == control["formula_gzip_sha256"]
        assert sha(raw) == row["formula"]["raw_sha256"] == control["formula_raw_sha256"]
        assert sha(model_path.read_bytes()) == row["model"]["sha256"] == control["known_model_sha256"]
        nvars, clauses, xors = parse(raw)
        assert nvars == row["model"]["variables"]
        values = parse_model(model_path.read_text(), nvars)
        check_xcnf_model(values, clauses, xors)
        synthetic = row["synthetic_control"]
        assigned = sum(1 << (i - 1) for i in range(1, 455) if values[i])
        assert assigned == int(synthetic["assignment_hex"], 16)
        bound_chain = dict(chain, selected_channel=0,
                           target_channels=[synthetic["synthetic_raw_target"]] * 4,
                           subgroup_target=synthetic["synthetic_projected_target"])
        arm = {"kind": "torsion_phi", "base_dimension": 11, "offset": 4096,
               "primary_variables": 454,
               "target_coordinate": synthetic["synthetic_target_phi"]}
        result = certificate(assigned, bases[label], bound_chain, arm)
        assert result["certified"] and result["unique_projected_rows"] == 1
        flipped = certificate(assigned ^ 1, bases[label], bound_chain, arm)
        assert not flipped.get("certified", False)
        checked.append({"base_kind": label, "formula_sha256": sha(packed),
                        "model_sha256": sha(model_path.read_bytes()),
                        "full_model_and_point_checked": True,
                        "first_primary_bit_flip_rejected": True})
    return checked


def check_formulas(formulas: dict, target: dict, target_sha: str,
                   positive_sha: str, bases: dict, base_sha: dict,
                   chain: dict) -> list[dict]:
    assert formulas["target_manifest_sha256"] == target_sha
    assert formulas["positive_manifest_sha256"] == positive_sha
    assert formulas["bases"] == base_sha
    assert len(formulas["arms"]) == 64
    seen = set()
    checked = []
    for arm in formulas["arms"]:
        key = (arm["target_index"], arm["base_kind"], arm["channel"])
        assert key not in seen
        seen.add(key)
        target_row = target["admitted"][arm["target_index"]]
        assert arm["counter"] == target_row["counter"]
        assert arm["target_coordinate"] == target_row["channel_phi"][arm["channel"]]
        label = arm["base_kind"]
        assert arm["base_sha256"] == base_sha[label]
        assert arm["kind"] == "torsion_phi" and arm["base_dimension"] == 11
        assert arm["offset"] == 4096 and arm["primary_variables"] == 454
        # The emitter records the compressed digest but not its byte count.
        # Derive that redundant verifier field from the serialized file.
        checked_arm = dict(arm, gzip_bytes=(ROOT / arm["gzip_path"]).stat().st_size)
        result = verify_arm(checked_arm, bases[label])
        evaluate(checked_arm, bases[label], chain, 20261017 + arm["target_index"])
        checked.append({"target_index": arm["target_index"], "base_kind": label,
                        "channel": arm["channel"],
                        "gzip_sha256": result["gzip_sha256"],
                        "membership_truth_table_checked_per_block": result["membership_truth_table_checked_per_block"],
                        "serialized_gate_target_evaluation_checked": True})
    assert seen == {(i, label, channel) for i in range(8)
                    for label in bases for channel in range(4)}
    return checked


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    fixture, fixture_sha = load(FIXTURE)
    chain, chain_sha = load(CHAIN)
    gamma = gamma_for(fixture["b_polynomial_bits"])
    assert gamma == chain["gamma"]
    target, target_sha = load(INPUTS / "target_manifest.json")
    positive, positive_sha = load(INPUTS / "positive_manifest.json")
    formulas, formula_sha = load(INPUTS / "formula_manifest.json")
    bases = {label: load(path) for label, path in BASES.items()}
    check_targets(target, fixture, fixture_sha, gamma)
    positives = check_positives(positive, {label: base for label, (base, _) in bases.items()}, chain)
    arms = check_formulas(formulas, target, target_sha, positive_sha,
                          {label: base for label, (base, _) in bases.items()},
                          {label: digest for label, (_, digest) in bases.items()}, chain)
    assert formulas["chain_sha256"] == chain_sha
    record = {"schema": "icperf-k11-input-independent-replay-v1",
              "scope": "target, positive-model and serialized-formula checks; no solver trial",
              "source_sha256": sha(Path(__file__).read_bytes()),
              "fixture_sha256": fixture_sha, "chain_sha256": chain_sha,
              "target_manifest_sha256": target_sha,
              "positive_manifest_sha256": positive_sha,
              "formula_manifest_sha256": formula_sha,
              "targets_checked": len(target["admitted"]),
              "positive_controls": positives, "natural_arms": arms}
    with args.out.open("x") as stream:
        json.dump(record, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"targets_checked": len(target["admitted"]),
                      "positives_checked": len(positives),
                      "formulas_checked": len(arms)}, sort_keys=True))


if __name__ == "__main__":
    main()
