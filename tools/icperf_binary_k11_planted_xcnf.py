"""Freeze satisfiable known-point XCNF controls for both 316-column k11 bases.

This constructs complete Boolean witnesses and verifies the serialized formulas.
It does not call a SAT solver or measure natural relation yield.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.icperf_binary_all_channels_xcnf import encode  # noqa: E402
from tools.icperf_binary_circuit_xcnf import (  # noqa: E402
    allowed_values, construct, evaluate_nodes, live_nodes, write_gzip,
)
from tools.icperf_binary_k11_root_certificate import INPUTS, load, synthetic_control  # noqa: E402
from tools.icperf_binary_k11_solver import (  # noqa: E402
    check_xcnf_model, parse_model, primary_bits,
)
from tools.icperf_binary_circuit_xcnf_verify import parse  # noqa: E402


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def model_text(values: list[bool]) -> str:
    literals = [str(i if values[i] else -i) for i in range(1, len(values))]
    lines = ["s SATISFIABLE"]
    for start in range(0, len(literals), 20):
        lines.append("v " + " ".join(literals[start:start+20]) + " 0")
    return "\n".join(lines) + "\n"


def build_one(label: str, out_dir: Path) -> dict:
    base, _, chain = load(label)
    control = synthetic_control(label)
    assert control["base_kind"] == label
    target = control["synthetic_target_phi"]
    assignment = int(control["assignment_hex"], 16)
    offset, width = base["selected_offset"], 11
    allowed = allowed_values("torsion_phi", base, offset, width)
    raw, meta = encode("torsion_phi", width, offset, target, chain["gamma"], allowed)
    circuit, outputs = construct("torsion_phi", width, offset, target, chain["gamma"])
    nodes = sorted(live_nodes(circuit, outputs) | set(range(2, circuit.nvars + 2)))
    variable_nodes = [node for node in nodes if node >= 2]
    evaluated = evaluate_nodes(circuit, assignment)
    assert all(evaluated[node] == 0 for row in outputs for node in row)
    assert len(variable_nodes) == meta["cnf_variables"]
    values = [False] + [bool(evaluated[node]) for node in variable_nodes]
    nvars, clauses, xors = parse(raw)
    assert nvars == meta["cnf_variables"]
    check_xcnf_model(values, clauses, xors)
    assert primary_bits(values, circuit.nvars) == assignment
    text = model_text(values)
    assert parse_model(text, nvars) == values
    formula = out_dir / f"{label}.xcnf.gz"
    model = out_dir / f"{label}.known_model.txt"
    meta["gzip_sha256"] = write_gzip(formula, raw)
    with model.open("x") as stream:
        stream.write(text)
    return {"base_kind": label, "base_sha256": sha(INPUTS[label][0]),
            "existing_manifest_sha256": sha(INPUTS[label][1]),
            "synthetic_control": control,
            "formula": {"path": str(formula.relative_to(ROOT)), "sha256": meta["gzip_sha256"],
                        "raw_sha256": meta["raw_xcnf_sha256"], "bytes": formula.stat().st_size,
                        "raw_bytes": len(raw)},
            "model": {"path": str(model.relative_to(ROOT)), "sha256": sha(model),
                      "variables": nvars, "primary_assignment_hex": hex(assignment),
                      "full_xcnf_model_verified": True},
            "input_counts": {k: meta[k] for k in ("cnf_variables", "cnf_clauses",
                       "native_xor_rows", "membership_forbid_clauses", "live_gates")}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir = args.out_dir.resolve()
    assert args.out_dir.is_dir() and not any(args.out_dir.iterdir())
    rows = [build_one(label, args.out_dir) for label in ("weighted", "local_random")]
    result = {"schema": "icperf-binary-k11-planted-xcnf-v1",
              "scope": "two exact SAT-positive input witnesses; no SAT solver trial, natural relation, rank or ECDLP cost claim",
              "source_sha256": sha(Path(__file__)),
              "encoder_sha256": sha(ROOT / "tools/icperf_binary_all_channels_xcnf.py"),
              "circuit_source_sha256": sha(ROOT / "tools/icperf_binary_circuit_xcnf.py"),
              "certificate_source_sha256": sha(ROOT / "tools/icperf_binary_k11_root_certificate.py"),
              "solver_adapter_sha256": sha(ROOT / "tools/icperf_binary_k11_solver.py"),
              "arms": rows}
    with (args.out_dir / "manifest.json").open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"bases": len(rows), "xcnf_gzip_bytes": sum(row["formula"]["bytes"] for row in rows),
                      "variables": [row["model"]["variables"] for row in rows]}, sort_keys=True))


if __name__ == "__main__":
    main()
