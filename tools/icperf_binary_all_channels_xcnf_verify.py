"""Parse all binary m8 channel formulas and check their target constants."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.icperf_binary_circuit_xcnf_verify import (check_gate_definitions,
                                                      parse, verify_arm)  # noqa: E402
from tools.icperf_koblitz_subgroup_fixture import mul  # noqa: E402

MANIFEST = ROOT / "research/icperf_binary_all_channels_xcnf_20261017/manifest.json"
PARENT = ROOT / "research/icperf_binary_circuit_xcnf_20261017/manifest.json"
CHAIN = ROOT / "research/icperf_binary_torsion_m8_chain_20261017/chain.json"
BASES = {"torsion_phi": ROOT / "research/icperf_binary_torsion_coordinate_20261017/base.json",
         "classical_raw_x": ROOT / "research/icperf_binary_projected_base_20261017/base.json"}
POLY = (1 << 61) | (1 << 5) | (1 << 2) | (1 << 1) | 1


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def product(a: int, b: int) -> int:
    return mul(a, b, POLY)


def square(a: int) -> int:
    return product(a, a)


def phi3(a: int, b: int, c: int, gamma: int) -> int:
    q = lambda t: square(t) ^ t
    return product(product(q(a), q(b)), q(c)) ^ product(gamma, square(a ^ b ^ c))


def raw3(a: int, b: int, c: int, curve_b: int) -> int:
    e2 = product(a, b) ^ product(a, c) ^ product(b, c)
    return square(e2) ^ product(product(a, b), c) ^ curve_b


def evaluate(arm: dict, base: dict, chain: dict, seed: int) -> None:
    raw = gzip.decompress((ROOT / arm["gzip_path"]).read_bytes())
    nvars, clauses, xors = parse(raw)
    gates = check_gate_definitions(arm, nvars, clauses, xors)
    scan = next(row for row in base["candidate_scans"] if row["offset"] == arm["offset"])
    allowed = sorted(scan["accepted_phi"] if arm["kind"] == "torsion_phi"
                     else [row[0] for row in scan["raw_points"]])
    seed_bytes = hashlib.sha256(f"{arm['kind']}:{arm['channel']}:{seed}".encode()).digest()
    base_values = [allowed[seed_bytes[i] % len(allowed)] for i in range(8)]
    full_values = [int.from_bytes(hashlib.sha256(seed_bytes + bytes([i])).digest()[:8], "big") & ((1 << 61) - 1)
                   for i in range(6)]
    width, offset = arm["base_dimension"], arm["offset"]
    assignment = sum((v ^ offset) << (i * width) for i, v in enumerate(base_values))
    assignment |= sum(v << (8 * width + i * 61) for i, v in enumerate(full_values))
    values = [False] * (nvars + 1)
    for var in range(1, arm["primary_variables"] + 1):
        values[var] = bool((assignment >> (var - 1)) & 1)
    for var in range(arm["primary_variables"] + 1, nvars + 1):
        gate = gates[var]
        values[var] = (values[gate[1]] and values[gate[2]]) if gate[0] == "and" else \
            bool((sum(values[operand] for operand in gate[1]) & 1) ^ gate[2])
    output_start = 3 * arm["live_gates"]["and"]
    units = clauses[output_start:output_start + 7 * 61]
    observed = [sum(int(values[-unit[0]]) << bit for bit, unit in
                    enumerate(units[i * 61:(i + 1) * 61])) for i in range(7)]
    triples = [[base_values[0], base_values[1], full_values[0]]]
    triples += [[full_values[i-1], base_values[i+1], full_values[i]] for i in range(1, 6)]
    triples += [[full_values[-1], base_values[-1], arm["target_coordinate"]]]
    expected = [phi3(*row, chain["gamma"]) if arm["kind"] == "torsion_phi" else
                raw3(*row, chain["curve"]["b_polynomial_bits"]) for row in triples]
    assert observed == expected


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    manifest_blob, parent_blob, chain_blob = [p.read_bytes() for p in (MANIFEST, PARENT, CHAIN)]
    manifest, parent, chain = [json.loads(blob) for blob in (manifest_blob, parent_blob, chain_blob)]
    assert manifest["source_sha256"] == sha((ROOT / "tools/icperf_binary_all_channels_xcnf.py").read_bytes())
    assert manifest["parent_manifest_sha256"] == sha(parent_blob)
    assert manifest["chain_sha256"] == sha(chain_blob)
    bases = {kind: json.loads(path.read_bytes()) for kind, path in BASES.items()}
    assert {kind: sha(path.read_bytes()) for kind, path in BASES.items()} == manifest["base_sha256"]
    assert len(manifest["arms"]) == 8
    assert {(a["kind"], a["channel"]) for a in manifest["arms"]} == \
        {(kind, channel) for kind in BASES for channel in range(4)}
    rows = []
    for arm in manifest["arms"]:
        target = (chain["target_channel_phi"][arm["channel"]] if arm["kind"] == "torsion_phi"
                  else chain["target_channels"][arm["channel"]][0])
        assert arm["target_coordinate"] == target
        if arm["channel"] == manifest["selected_channel"]:
            prior = next(row for row in parent["arms"] if row["kind"] == arm["kind"])
            assert all(arm[key] == prior[key] for key in prior)
        checked = verify_arm(arm, bases[arm["kind"]])
        for seed in (0, 1, 2):
            evaluate(arm, bases[arm["kind"]], chain, seed)
        checked["channel"] = arm["channel"]
        checked["independent_direct_field_evaluations"] = 3
        rows.append(checked)
    output = {"schema": "icperf-binary-all-channels-xcnf-verification-v1",
              "scope": "serialized-formula and direct field-evaluation checks; no selected-formula solver run",
              "source_sha256": sha(Path(__file__).read_bytes()),
              "manifest_sha256": sha(manifest_blob), "parent_manifest_sha256": sha(parent_blob),
              "chain_sha256": sha(chain_blob), "arms": rows}
    with args.out.open("x") as stream:
        json.dump(output, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"arms": len(rows), "direct_field_evaluations": 3 * len(rows)}, sort_keys=True))


if __name__ == "__main__":
    main()
