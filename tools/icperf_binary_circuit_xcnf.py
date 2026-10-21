"""Freeze membership-constrained XCNF inputs for the binary m=8 chain.

This only materializes and checks input formulas. It never invokes a solver.
The formulas still omit curve-lift, sign and pole branches and are not DLP
experiments or complete point-decomposition instances.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
import resource
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.icperf_binary_boolean_support import N  # noqa: E402
from tools.icperf_binary_circuit_support import Circuit  # noqa: E402

CIRCUIT_RECORD = ROOT / "research/icperf_binary_circuit_support_20261017/circuit.json"
PHI_BASE = ROOT / "research/icperf_binary_torsion_coordinate_20261017/base.json"
RAW_BASE = ROOT / "research/icperf_binary_projected_base_20261017/base.json"
CHAIN = ROOT / "research/icperf_binary_torsion_m8_chain_20261017/chain.json"


def selected_scan(base: dict) -> dict:
    return next(row for row in base["candidate_scans"]
                if row["offset"] == base["selected_offset"])


def construct(kind: str, width: int, offset: int, target: int, gamma: int):
    nvars = 8 * width + 6 * N
    circuit = Circuit(nvars)
    base = [circuit.variable(offset, width, i * width) for i in range(8)]
    full = [circuit.variable(0, N, 8 * width + i * N) for i in range(6)]
    triples = [[base[0], base[1], full[0]]]
    triples += [[full[i - 1], base[i + 1], full[i]] for i in range(1, 6)]
    triples += [[full[-1], base[-1], circuit.constant(target)]]
    outputs = [circuit.phi3(*row, gamma) if kind == "torsion_phi" else
               circuit.raw3(*row) for row in triples]
    return circuit, outputs


def live_nodes(circuit: Circuit, outputs: list[list[int]]) -> set[int]:
    live: set[int] = set()
    stack = [node for row in outputs for node in row]
    while stack:
        node = stack.pop()
        if node in live:
            continue
        live.add(node)
        op, a, b = circuit.nodes[node]
        if op in ("xor", "and"):
            stack.extend((a, b))
    return live


def allowed_values(kind: str, base: dict, offset: int, width: int) -> set[int]:
    scan = selected_scan(base)
    full = (scan["accepted_phi"] if kind == "torsion_phi" else
            [row[0] for row in scan["raw_points"]])
    allowed = {value ^ offset for value in full}
    assert len(allowed) == len(full)
    assert all(0 <= value < (1 << width) for value in allowed)
    return allowed


def forbidden_clause(mapping: dict[int, int], block: int, width: int,
                     value: int) -> list[int]:
    literals = []
    for bit in range(width):
        primary_node = 2 + block * width + bit
        var = mapping[primary_node]
        literals.append(-var if value & (1 << bit) else var)
    return literals


def evaluate_nodes(circuit: Circuit, assignment: int) -> list[int]:
    values = [0] * len(circuit.nodes)
    values[1] = 1
    for i in range(circuit.nvars):
        values[2 + i] = (assignment >> i) & 1
    for node in range(circuit.nvars + 2, len(circuit.nodes)):
        op, a, b = circuit.nodes[node]
        values[node] = values[a] ^ values[b] if op == "xor" else values[a] & values[b]
    return values


def planted_assignment(width: int, offset: int, chain: dict) -> int:
    bits = 0
    for i, row in enumerate(chain["base_representatives"]):
        coordinate = row[0]
        value = coordinate ^ offset
        assert 0 <= value < (1 << width)
        bits |= value << (i * width)
    for i, coordinate in enumerate(chain["intermediate_phi"]):
        bits |= coordinate << (8 * width + i * N)
    return bits


def encode(kind: str, width: int, offset: int, target: int, gamma: int,
           allowed: set[int], parent_counts: dict, chain: dict) -> tuple[bytes, dict]:
    circuit, outputs = construct(kind, width, offset, target, gamma)
    live = live_nodes(circuit, outputs)
    assert circuit.live_counts([node for row in outputs for node in row]) == parent_counts
    # Include every primary input, even if dead, so the frozen variable order
    # remains explicit and membership clauses address all eight blocks.
    nodes = sorted(live | set(range(2, circuit.nvars + 2)))
    mapping = {node: i + 1 for i, node in enumerate(node for node in nodes if node >= 2)}
    inverse = {variable: node for node, variable in mapping.items()}
    clauses: list[list[int]] = []
    xors: list[tuple[list[int], bool]] = []
    for node in nodes:
        op, a, b = circuit.nodes[node]
        if op == "and":
            z, x, y = mapping[node], mapping[a], mapping[b]
            clauses.extend(([-z, x], [-z, y], [z, -x, -y]))
        elif op == "xor":
            row = [mapping[node]] + [mapping[value] for value in (a, b) if value >= 2]
            rhs = (a == 1) ^ (b == 1)
            xors.append((row, rhs))
    for row in outputs:
        for node in row:
            if node == 1:
                clauses.append([])
            elif node >= 2:
                clauses.append([-mapping[node]])
    for block in range(8):
        for value in range(1 << width):
            if value not in allowed:
                clauses.append(forbidden_clause(mapping, block, width, value))

    witness = {"available": kind == "torsion_phi"}
    if kind == "torsion_phi":
        assignment = planted_assignment(width, offset, chain)
        values = evaluate_nodes(circuit, assignment)
        assert all(values[node] == 0 for row in outputs for node in row)
        assert all(((assignment >> (block * width)) & ((1 << width) - 1)) in allowed
                   for block in range(8))
        assert all(any((values[inverse[var]] if var > 0 else
                        1 - values[inverse[-var]]) for var in clause)
                   for clause in clauses)
        assert all((sum(values[inverse[var]] for var in row) & 1) == rhs
                   for row, rhs in xors)
        witness = {"available": True, "primary_assignment_hex": hex(assignment),
                   "all_output_bits_zero": True, "all_clauses_hold": True,
                   "all_xors_hold": True, "base_membership_holds": True}

    stream = io.StringIO()
    stream.write(f"p cnf {len(mapping)} {len(clauses) + len(xors)}\n")
    for clause in clauses:
        stream.write(" ".join(map(str, clause)) + " 0\n")
    for row, rhs in xors:
        stream.write(("x" if rhs else "x-") + str(row[0]))
        stream.write(" " + " ".join(map(str, row[1:])) + " 0\n")
    raw = stream.getvalue().encode("ascii")
    meta = {"kind": kind, "base_dimension": width, "offset": offset,
            "target_coordinate": target, "primary_variables": circuit.nvars,
            "cnf_variables": len(mapping), "cnf_clauses": len(clauses),
            "native_xor_rows": len(xors), "output_zero_units": 7 * N,
            "allowed_coordinate_values": len(allowed),
            "forbidden_coordinate_values": (1 << width) - len(allowed),
            "membership_forbid_clauses": 8 * ((1 << width) - len(allowed)),
            "live_gates": parent_counts, "raw_xcnf_bytes": len(raw),
            "raw_xcnf_sha256": hashlib.sha256(raw).hexdigest(),
            "planted_witness": witness}
    return raw, meta


def write_gzip(path: Path, raw: bytes) -> str:
    with path.open("xb") as stream:
        with gzip.GzipFile(fileobj=stream, mode="wb", filename="", mtime=0,
                           compresslevel=9) as compressed:
            compressed.write(raw)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    assert args.out_dir.is_dir()
    paths = (CIRCUIT_RECORD, PHI_BASE, RAW_BASE, CHAIN)
    blobs = [path.read_bytes() for path in paths]
    record, phi_base, raw_base, chain = [json.loads(blob) for blob in blobs]
    source = ROOT / "tools/icperf_binary_circuit_support.py"
    assert record["source_sha256"] == hashlib.sha256(source.read_bytes()).hexdigest()
    assert record["chain_sha256"] == hashlib.sha256(blobs[3]).hexdigest()
    assert chain["base_sha256"] == hashlib.sha256(blobs[1]).hexdigest()
    started_wall, started_cpu = time.perf_counter(), time.process_time()
    configs = [
        ("torsion_phi", 10, phi_base, chain["target_channel_phi"][chain["selected_channel"]]),
        ("classical_raw_x", 9, raw_base, chain["raw_sum"][0]),
    ]
    arms = []
    for kind, width, base, target in configs:
        offset = base["selected_offset"]
        parent = next(arm for arm in record["arms"] if
                      arm["kind"] == kind and arm["base_dimension"] == width)
        allowed = allowed_values(kind, base, offset, width)
        raw, meta = encode(kind, width, offset, target, chain["gamma"], allowed,
                           parent["all_equations_live"], chain)
        path = args.out_dir / f"{kind}.xcnf.gz"
        meta["gzip_path"] = str(path.resolve().relative_to(ROOT))
        meta["gzip_sha256"] = write_gzip(path, raw)
        meta["gzip_bytes"] = path.stat().st_size
        arms.append(meta)
    result = {"schema": "icperf-binary-circuit-xcnf-v1",
              "scope": "membership-constrained input equations only; no solver, curve-lift/sign/pole constraints, degree of regularity, relation or speed claim",
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "parent_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(blob).hexdigest()
                                for path, blob in zip(paths, blobs)},
              "xcnf_semantics": "CNF clauses plus native XOR lines; xV ... 0 means XOR=1, x-V ... 0 means XOR=0; first line p cnf variables total_clauses; AND equivalences are three CNF clauses; all seven field equations are zero",
              "curve": chain["curve"], "arms": arms,
              "preparation": {"wall_seconds": time.perf_counter() - started_wall,
                              "cpu_seconds": time.process_time() - started_cpu,
                              "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss *
                                                (1 if sys.platform == "darwin" else 1024),
                              "loadavg_end": list(os.getloadavg()),
                              "git_head": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                                         capture_output=True, text=True, check=True).stdout.strip(),
                              "git_status_porcelain": subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                                                                      capture_output=True, text=True, check=True).stdout.splitlines(),
                              "python_version": sys.version}}
    with (args.out_dir / "manifest.json").open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"path": str(args.out_dir), "arms": [{k: row[k] for k in
                                                              ("kind", "cnf_variables", "cnf_clauses", "native_xor_rows", "gzip_bytes")}
                                                             for row in arms]}, sort_keys=True))


if __name__ == "__main__":
    main()
