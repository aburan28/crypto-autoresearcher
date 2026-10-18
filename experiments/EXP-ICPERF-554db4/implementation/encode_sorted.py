"""Prepare sorted eight-summand positive XCNF inputs; no solver is invoked.

The original field circuit and membership set are retained. Seven adjacent
unsigned comparators constrain the encoded 11-bit summand values. Each
positive witness is rebuilt from entire curve points after a stable sort.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.icperf_binary_all_channels_xcnf import encode as original_encode  # noqa: E402
from tools.icperf_binary_circuit_xcnf import allowed_values, evaluate_nodes, forbidden_clause, live_nodes  # noqa: E402
from tools.icperf_binary_circuit_support import Circuit  # noqa: E402
from tools.icperf_binary_torsion_coordinate import phi_from_x  # noqa: E402
from tools.icperf_ordinary_binary_fixture import add, on_curve, scale  # noqa: E402

HERE = Path(__file__).resolve().parents[1]
INPUTS = HERE / "inputs"
POSITIVE = ROOT / "experiments/EXP-ICPERF-018b0c/inputs/positive_manifest.json"
BASES = {
    "weighted": ROOT / "research/icperf_binary_torsion_k11_weighted_20261017/base.json",
    "local_random": ROOT / "research/icperf_binary_torsion_k11_local_control_20261017/base.json",
}
WIDTH, OFFSET, FIELD_BITS = 11, 4096, 61
PRIMARY = 8 * WIDTH + 6 * FIELD_BITS


def sha(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def canonical(data: dict) -> bytes:
    return (json.dumps(data, sort_keys=True, indent=2) + "\n").encode()


def put_new(path: Path, blob: bytes) -> str:
    with path.open("xb") as stream:
        stream.write(blob)
    return sha(blob)


def gzip_new(path: Path, raw: bytes) -> str:
    with path.open("xb") as stream:
        with gzip.GzipFile(fileobj=stream, mode="wb", filename="", mtime=0,
                           compresslevel=9) as packed:
            packed.write(raw)
    return sha(path.read_bytes())


def complement(circuit: Circuit, node: int) -> int:
    return circuit.gate("xor", node, 1)


def or_gate(circuit: Circuit, a: int, b: int) -> int:
    return circuit.gate("xor", circuit.gate("xor", a, b), circuit.gate("and", a, b))


def greater(circuit: Circuit, left: int, right: int) -> int:
    """Unsigned left > right, with the most significant bit read first."""
    gt, equal = 0, 1
    for bit in range(WIDTH - 1, -1, -1):
        a = 2 + left * WIDTH + bit
        b = 2 + right * WIDTH + bit
        new_gt = circuit.gate("and", equal, circuit.gate("and", a, complement(circuit, b)))
        gt = or_gate(circuit, gt, new_gt)
        equal = circuit.gate("and", equal, complement(circuit, circuit.gate("xor", a, b)))
    return gt


def circuit_sorted(target: int, gamma: int) -> tuple[Circuit, list[list[int]], list[int]]:
    circuit = Circuit(PRIMARY)
    base = [circuit.variable(OFFSET, WIDTH, i * WIDTH) for i in range(8)]
    full = [circuit.variable(0, FIELD_BITS, 8 * WIDTH + i * FIELD_BITS) for i in range(6)]
    triples = [[base[0], base[1], full[0]]]
    triples += [[full[i - 1], base[i + 1], full[i]] for i in range(1, 6)]
    triples += [[full[-1], base[-1], circuit.constant(target)]]
    equations = [circuit.phi3(*row, gamma) for row in triples]
    comparators = [greater(circuit, i, i + 1) for i in range(7)]
    return circuit, equations, comparators


def emit(target: int, gamma: int, allowed: set[int], primary: int) -> tuple[bytes, str, dict]:
    circuit, equations, comparators = circuit_sorted(target, gamma)
    outputs = equations + [[node] for node in comparators]
    live = live_nodes(circuit, outputs)
    nodes = sorted(live | set(range(2, PRIMARY + 2)))
    mapping = {node: index + 1 for index, node in enumerate(node for node in nodes if node >= 2)}
    inverse = {variable: node for node, variable in mapping.items()}
    clauses: list[list[int]] = []
    xors: list[tuple[list[int], bool]] = []
    for node in nodes:
        op, a, b = circuit.nodes[node]
        if op == "and":
            z, x, y = mapping[node], mapping[a], mapping[b]
            clauses.extend(([-z, x], [-z, y], [z, -x, -y]))
        elif op == "xor":
            xors.append(([mapping[node]] + [mapping[value] for value in (a, b) if value >= 2],
                         (a == 1) ^ (b == 1)))
    for row in outputs:
        for node in row:
            if node == 1:
                clauses.append([])
            elif node >= 2:
                clauses.append([-mapping[node]])
    for block in range(8):
        for value in range(1 << WIDTH):
            if value not in allowed:
                clauses.append(forbidden_clause(mapping, block, WIDTH, value))
    values = evaluate_nodes(circuit, primary)
    if not all(values[node] == 0 for row in outputs for node in row):
        raise ValueError("sorted planted witness fails field equation or order comparator")
    if not all(any((bool(values[inverse[abs(lit)]]) if lit > 0
                    else not bool(values[inverse[abs(lit)]])) for lit in clause)
               for clause in clauses):
        raise ValueError("sorted planted witness fails CNF")
    if not all(bool(sum(values[inverse[var]]
                        for var in row) & 1) == rhs for row, rhs in xors):
        raise ValueError("sorted planted witness fails native XOR")
    stream = io.StringIO()
    stream.write(f"p cnf {len(mapping)} {len(clauses) + len(xors)}\n")
    for clause in clauses:
        stream.write(" ".join(map(str, clause)) + " 0\n")
    for row, rhs in xors:
        stream.write(("x" if rhs else "x-") + str(row[0]))
        stream.write(" " + " ".join(map(str, row[1:])) + " 0\n")
    raw = stream.getvalue().encode("ascii")
    literals = [str(var if values[node] else -var) for node, var in sorted(mapping.items(), key=lambda x: x[1])]
    model = "s SATISFIABLE\n" + "".join("v " + " ".join(literals[i:i + 120]) + " 0\n"
                                       for i in range(0, len(literals), 120))
    counts = circuit.live_counts([node for row in outputs for node in row])
    meta = {"cnf_variables": len(mapping), "cnf_clauses": len(clauses),
            "native_xor_rows": len(xors), "primary_variables": PRIMARY,
            "live_gates": counts, "comparator_outputs": len(comparators),
            "output_zero_units": sum(node >= 2 for row in outputs for node in row),
            "membership_forbid_clauses": 8 * ((1 << WIDTH) - len(allowed)),
            "raw_xcnf_bytes": len(raw), "raw_xcnf_sha256": sha(raw)}
    return raw, model, meta


def point_assignment(points: list[tuple[int, int]], gamma: int, b: int) -> tuple[int, list[int], tuple[int, int]]:
    if len(points) != 8 or not all(on_curve(point, b) for point in points):
        raise ValueError("eight curve points required")
    bits = 0
    for index, point in enumerate(points):
        t = phi_from_x(point[0], gamma)
        value = t ^ OFFSET
        if not 0 <= value < (1 << WIDTH):
            raise ValueError("point outside encoded coordinate range")
        bits |= value << (index * WIDTH)
    partial = None
    intermediates = []
    for index, point in enumerate(points):
        partial = add(partial, point, b)
        if index in range(1, 7):
            if partial is None or partial[0] in (0, gamma):
                raise ValueError("non-affine or exceptional intermediate point")
            t = phi_from_x(partial[0], gamma)
            intermediates.append(t)
            bits |= t << (8 * WIDTH + (index - 1) * FIELD_BITS)
    if partial is None:
        raise ValueError("non-affine target")
    return bits, intermediates, partial


def prepare() -> dict:
    if not INPUTS.is_dir() or any(INPUTS.iterdir()):
        raise ValueError("input directory must exist and be empty")
    positive_blob = POSITIVE.read_bytes()
    positive = json.loads(positive_blob)
    gamma = 70364449406991
    b = 31
    rows = {}
    for label in ("weighted", "local_random"):
        source = positive["controls"][label]
        original_raw = gzip.decompress((ROOT / source["formula_path"]).read_bytes())
        base_blob = BASES[label].read_bytes()
        base = json.loads(base_blob)
        allowed = allowed_values("torsion_phi", base, OFFSET, WIDTH)
        target = source["source_row"]["synthetic_control"]
        original_emitted, _ = original_encode("torsion_phi", WIDTH, OFFSET,
                                              target["synthetic_target_phi"], gamma, allowed)
        if original_emitted != original_raw:
            raise ValueError(f"{label}: original unsorted bytes do not re-emit")
        original_points = [tuple(row[1:]) for row in target["input_representatives"]]
        old_bits, _, old_sum = point_assignment(original_points, gamma, b)
        if old_bits != int(target["assignment_hex"], 16) or list(old_sum) != target["synthetic_raw_target"]:
            raise ValueError(f"{label}: source point tuple does not match planted target")
        ordered = sorted(enumerate(original_points),
                         key=lambda item: (phi_from_x(item[1][0], gamma) ^ OFFSET))
        sorted_points = [point for _, point in ordered]
        primary, intermediates, total = point_assignment(sorted_points, gamma, b)
        if total != old_sum or scale(4, total, b) != tuple(target["synthetic_projected_target"]):
            raise ValueError(f"{label}: stable sort changed raw or projected target")
        raw, model, meta = emit(target["synthetic_target_phi"], gamma, allowed, primary)
        formula_path = INPUTS / f"{label}.sorted.xcnf.gz"
        model_path = INPUTS / f"{label}.sorted.known_model.txt"
        formula_sha = gzip_new(formula_path, raw)
        model_sha = put_new(model_path, model.encode())
        rows[label] = {"base_kind": label, "base_sha256": sha(base_blob),
                       "source_formula_sha256": sha((ROOT / source["formula_path"]).read_bytes()),
                       "original_raw_sha256": sha(original_raw),
                       "original_reemission_byte_equal": True,
                       "source_model_sha256": sha((ROOT / source["known_model_path"]).read_bytes()),
                       "target_coordinate": target["synthetic_target_phi"],
                       "raw_target": target["synthetic_raw_target"],
                       "projected_target": target["synthetic_projected_target"],
                       "original_primary_hex": hex(old_bits), "sorted_primary_hex": hex(primary),
                       "sorted_point_source_indices": [index for index, _ in ordered],
                       "sorted_points": [list(point) for point in sorted_points],
                       "sorted_intermediate_phi": intermediates,
                       "formula_path": str(formula_path.relative_to(ROOT)),
                       "formula_gzip_sha256": formula_sha,
                       "model_path": str(model_path.relative_to(ROOT)),
                       "model_sha256": model_sha, **meta}
    manifest = {"schema": "icperf-binary-m8-sorted-positive-v1",
                "experiment_id": "EXP-ICPERF-554db4", "scope": "two planted input controls; zero scientific solver calls",
                "gamma": gamma, "positive_manifest_sha256": sha(positive_blob),
                "encoder_sha256": sha(Path(__file__).read_bytes()), "arms": rows}
    put_new(INPUTS / "sorted_positive_manifest.json", canonical(manifest))
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prepare", choices=["prepare"])
    parser.parse_args()
    print(json.dumps({"arms": list(prepare()["arms"]), "solver_calls": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
