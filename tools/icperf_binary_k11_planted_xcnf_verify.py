"""Replay both frozen planted XCNF formulas and their complete witnesses."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.icperf_binary_circuit_xcnf_verify import parse  # noqa: E402

MANIFEST = ROOT / "research/icperf_binary_k11_planted_xcnf_20261017/complete/manifest.json"
CONTROLS = ROOT / "research/icperf_binary_k11_root_certificate_20261017/synthetic_controls.json"
SAGE = ROOT / "research/icperf_binary_k11_root_certificate_20261017/sage_replay.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def model_values(path: Path, nvars: int) -> list[bool]:
    states, bits = [], {}
    for line in path.read_text().splitlines():
        if line.startswith("s "):
            states.append(line)
        elif line.startswith("v "):
            for token in line[2:].split():
                literal = int(token)
                if literal == 0:
                    continue
                index = abs(literal)
                assert 1 <= index <= nvars
                assert index not in bits or bits[index] == (literal > 0)
                bits[index] = literal > 0
        else:
            raise ValueError("unexpected model line")
    assert states == ["s SATISFIABLE"] and len(bits) == nvars
    return [False] + [bits[i] for i in range(1, nvars+1)]


def replay() -> dict:
    manifest = json.loads(MANIFEST.read_bytes())
    controls = json.loads(CONTROLS.read_bytes())
    sage = json.loads(SAGE.read_bytes())
    assert manifest["schema"] == "icperf-binary-k11-planted-xcnf-v1"
    assert sage["controls_sha256"] == sha(CONTROLS)
    for key, path in (("source_sha256", ROOT / "tools/icperf_binary_k11_planted_xcnf.py"),
                      ("encoder_sha256", ROOT / "tools/icperf_binary_all_channels_xcnf.py"),
                      ("circuit_source_sha256", ROOT / "tools/icperf_binary_circuit_xcnf.py"),
                      ("certificate_source_sha256", ROOT / "tools/icperf_binary_k11_root_certificate.py"),
                      ("solver_adapter_sha256", ROOT / "tools/icperf_binary_k11_solver.py")):
        assert manifest[key] == sha(path)
    assert {row["base_kind"] for row in manifest["arms"]} == {"weighted", "local_random"}
    original = {row["base_kind"]: row for row in controls["bases"]}
    checked = []
    for row in manifest["arms"]:
        label = row["base_kind"]
        assert row["synthetic_control"] == original[label]
        base = ROOT / f"research/icperf_binary_torsion_k11_{'weighted' if label == 'weighted' else 'local_control'}_20261017/base.json"
        assert row["base_sha256"] == sha(base)
        formula = ROOT / row["formula"]["path"]
        model = ROOT / row["model"]["path"]
        assert row["formula"]["sha256"] == sha(formula)
        assert row["model"]["sha256"] == sha(model)
        raw = gzip.decompress(formula.read_bytes())
        assert hashlib.sha256(raw).hexdigest() == row["formula"]["raw_sha256"]
        assert len(raw) == row["formula"]["raw_bytes"]
        nvars, clauses, xors = parse(raw)
        assert nvars == row["model"]["variables"] == row["input_counts"]["cnf_variables"]
        assert len(clauses) == row["input_counts"]["cnf_clauses"]
        assert len(xors) == row["input_counts"]["native_xor_rows"]
        values = model_values(model, nvars)
        assert all(any(values[abs(lit)] == (lit > 0) for lit in clause) for clause in clauses)
        assert all(bool(sum(values[var] for var in literals) & 1) == rhs
                   for literals, rhs in xors)
        assignment = sum(1 << i for i in range(454) if values[i+1])
        assert hex(assignment) == row["model"]["primary_assignment_hex"] == original[label]["assignment_hex"]
        assert all(item["certified"] and item["unique_projected_rows"] == 1
                   for item in original[label]["channels"])
        checked.append({"base_kind": label, "variables": nvars,
                        "cnf_clauses_checked": len(clauses),
                        "xor_rows_checked": len(xors),
                        "known_model_satisfies_xcnf": True,
                        "independent_sage_point_replay_sha256": sha(SAGE)})
    return {"schema": "icperf-binary-k11-planted-xcnf-replay-v1",
            "scope": "complete constructed Boolean witnesses checked against exact XCNF and earlier independent Sage point replay; no SAT solver trial",
            "source_sha256": sha(Path(__file__)), "manifest_sha256": sha(MANIFEST),
            "synthetic_controls_sha256": sha(CONTROLS), "sage_replay_sha256": sha(SAGE),
            "arms": checked}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = replay()
    with args.out.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"arms": len(result["arms"]),
                      "variables": [row["variables"] for row in result["arms"]]}, sort_keys=True))


if __name__ == "__main__":
    main()
