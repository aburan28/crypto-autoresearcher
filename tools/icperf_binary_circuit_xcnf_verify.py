"""Independently parse and check frozen binary m=8 XCNF input artifacts.

This verifier reads the serialized formula, not the producer's Circuit DAG.
It checks each base's complete coordinate-membership truth table and evaluates
every clause and XOR on the planted torsion primary assignment.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/icperf_binary_circuit_xcnf_20261017/manifest.json"
PHI_BASE = ROOT / "research/icperf_binary_torsion_coordinate_20261017/base.json"
RAW_BASE = ROOT / "research/icperf_binary_projected_base_20261017/base.json"


def sha(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def expected_allowed(arm: dict, base: dict) -> set[int]:
    selected = [scan for scan in base["candidate_scans"]
                if scan["offset"] == arm["offset"]]
    assert len(selected) == 1
    scan = selected[0]
    if arm["kind"] == "torsion_phi":
        absolute = scan["accepted_phi"]
    else:
        absolute = [row[0] for row in scan["raw_points"]]
    return {value ^ arm["offset"] for value in absolute}


def parse(raw: bytes) -> tuple[int, list[list[int]], list[tuple[list[int], bool]]]:
    lines = raw.decode("ascii").splitlines()
    header = lines.pop(0).split()
    assert len(header) == 4 and header[:2] == ["p", "cnf"]
    nvars, nconstraints = map(int, header[2:])
    clauses: list[list[int]] = []
    xors: list[tuple[list[int], bool]] = []
    xor_started = False
    for line in lines:
        assert line.endswith(" 0")
        if line.startswith("x"):
            xor_started = True
            tokens = line[1:].split()
            rhs = not tokens[0].startswith("-")
            variables = [abs(int(token)) for token in tokens[:-1]]
            assert len(variables) in (2, 3)
            assert all(1 <= value <= nvars for value in variables)
            xors.append((variables, rhs))
        else:
            assert not xor_started
            tokens = line.split()
            assert tokens[-1] == "0"
            clause = [int(token) for token in tokens[:-1]]
            assert all(1 <= abs(value) <= nvars for value in clause)
            clauses.append(clause)
    assert len(clauses) + len(xors) == nconstraints
    return nvars, clauses, xors


def check_gate_definitions(arm: dict, nvars: int, clauses: list[list[int]],
                           xors: list[tuple[list[int], bool]]) -> dict[int, tuple]:
    and_count = arm["live_gates"]["and"]
    xor_count = arm["live_gates"]["xor"]
    assert len(xors) == xor_count
    assert nvars == arm["primary_variables"] + and_count + xor_count
    gates = {}
    for i in range(and_count):
        c1, c2, c3 = clauses[3 * i:3 * i + 3]
        assert len(c1) == len(c2) == 2 and len(c3) == 3
        z = -c1[0]
        x, y = c1[1], c2[1]
        assert -c2[0] == z and c3 == [z, -x, -y]
        assert z > max(x, y)
        assert z not in gates
        gates[z] = ("and", x, y)
    for row, rhs in xors:
        z, *operands = row
        assert z > max(operands)
        assert z not in gates
        gates[z] = ("xor", operands, rhs)
    assert set(gates) == set(range(arm["primary_variables"] + 1, nvars + 1))
    return gates


def forbidden_from_clause(clause: list[int], block: int, width: int) -> int:
    assert len(clause) == width
    expected = set(range(block * width + 1, (block + 1) * width + 1))
    assert {abs(value) for value in clause} == expected
    return sum((1 << i) for i, value in enumerate(clause) if value < 0)


def verify_arm(arm: dict, base: dict) -> dict:
    path = ROOT / arm["gzip_path"]
    packed = path.read_bytes()
    raw = gzip.decompress(packed)
    assert sha(packed) == arm["gzip_sha256"] and sha(raw) == arm["raw_xcnf_sha256"]
    assert len(raw) == arm["raw_xcnf_bytes"] and len(packed) == arm["gzip_bytes"]
    nvars, clauses, xors = parse(raw)
    assert nvars == arm["cnf_variables"]
    assert len(clauses) == arm["cnf_clauses"] and len(xors) == arm["native_xor_rows"]
    gates = check_gate_definitions(arm, nvars, clauses, xors)
    and_clauses = 3 * arm["live_gates"]["and"]
    output_units = clauses[and_clauses:and_clauses + arm["output_zero_units"]]
    assert len(output_units) == arm["output_zero_units"]
    assert all(len(clause) == 1 and clause[0] < 0 for clause in output_units)
    membership = clauses[and_clauses + arm["output_zero_units"]:]
    width = arm["base_dimension"]
    expected = expected_allowed(arm, base)
    assert len(expected) == arm["allowed_coordinate_values"]
    forbidden = set(range(1 << width)) - expected
    assert len(forbidden) == arm["forbidden_coordinate_values"]
    assert len(membership) == 8 * len(forbidden)
    for block in range(8):
        group = membership[block * len(forbidden):(block + 1) * len(forbidden)]
        observed = {forbidden_from_clause(clause, block, width) for clause in group}
        assert observed == forbidden

    witness = arm["planted_witness"]
    result = {"kind": arm["kind"], "gzip_sha256": sha(packed),
              "raw_xcnf_sha256": sha(raw), "variables": nvars,
              "and_gates_checked": arm["live_gates"]["and"],
              "xor_gates_checked": arm["live_gates"]["xor"],
              "output_zero_units_checked": len(output_units),
              "membership_truth_table_checked_per_block": 1 << width,
              "membership_blocks_checked": 8,
              "planted_full_assignment_checked": False}
    if witness["available"]:
        assignment = int(witness["primary_assignment_hex"], 16)
        values = [False] * (nvars + 1)
        for var in range(1, arm["primary_variables"] + 1):
            values[var] = bool((assignment >> (var - 1)) & 1)
        for var in range(arm["primary_variables"] + 1, nvars + 1):
            gate = gates[var]
            if gate[0] == "and":
                values[var] = values[gate[1]] and values[gate[2]]
            else:
                values[var] = (sum(values[operand] for operand in gate[1]) & 1) ^ gate[2]
        assert all(any(values[abs(lit)] if lit > 0 else not values[-lit]
                       for lit in clause) for clause in clauses)
        assert all((sum(values[var] for var in row) & 1) == rhs
                   for row, rhs in xors)
        result["planted_full_assignment_checked"] = True
        result["clauses_checked_on_witness"] = len(clauses)
        result["xors_checked_on_witness"] = len(xors)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    manifest_blob = MANIFEST.read_bytes()
    manifest = json.loads(manifest_blob)
    bases = {"torsion_phi": json.loads(PHI_BASE.read_bytes()),
             "classical_raw_x": json.loads(RAW_BASE.read_bytes())}
    arms = [verify_arm(arm, bases[arm["kind"]]) for arm in manifest["arms"]]
    record = {"schema": "icperf-binary-circuit-xcnf-verification-v1",
              "scope": "independent serialized-formula check; no solver invocation or ECDLP result",
              "source_sha256": sha(Path(__file__).read_bytes()),
              "manifest_sha256": sha(manifest_blob),
              "base_sha256": {kind: sha(path.read_bytes()) for kind, path in
                              (("torsion_phi", PHI_BASE), ("classical_raw_x", RAW_BASE))},
              "arms": arms}
    with args.out.open("x") as stream:
        json.dump(record, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"path": str(args.out), "verified": arms}, sort_keys=True))


if __name__ == "__main__":
    main()
