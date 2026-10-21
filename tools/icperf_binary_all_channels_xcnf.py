"""Freeze all four raw-target-channel binary m8 XCNF input variants.

Two selected-channel files are reused by digest from the prior manifest; six
new files vary only the public target constant. This never invokes a solver.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.icperf_binary_circuit_xcnf import (allowed_values, construct,
                                               forbidden_clause, live_nodes,
                                               write_gzip)  # noqa: E402

PARENT = ROOT / "research/icperf_binary_circuit_xcnf_20261017/manifest.json"
CHAIN = ROOT / "research/icperf_binary_torsion_m8_chain_20261017/chain.json"
BASES = {"torsion_phi": ROOT / "research/icperf_binary_torsion_coordinate_20261017/base.json",
         "classical_raw_x": ROOT / "research/icperf_binary_projected_base_20261017/base.json"}


def sha(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def encode(kind: str, width: int, offset: int, target: int, gamma: int,
           allowed: set[int]) -> tuple[bytes, dict]:
    circuit, outputs = construct(kind, width, offset, target, gamma)
    live = live_nodes(circuit, outputs)
    nodes = sorted(live | set(range(2, circuit.nvars + 2)))
    mapping = {node: i + 1 for i, node in enumerate(node for node in nodes if node >= 2)}
    clauses: list[list[int]] = []
    xors: list[tuple[list[int], bool]] = []
    for node in nodes:
        op, a, b = circuit.nodes[node]
        if op == "and":
            z, x, y = mapping[node], mapping[a], mapping[b]
            clauses.extend(([-z, x], [-z, y], [z, -x, -y]))
        elif op == "xor":
            row = [mapping[node]] + [mapping[v] for v in (a, b) if v >= 2]
            xors.append((row, (a == 1) ^ (b == 1)))
    for output in outputs:
        for node in output:
            assert node != 1
            if node >= 2:
                clauses.append([-mapping[node]])
    assert len(clauses) == 3 * sum(circuit.nodes[n][0] == "and" for n in nodes) + 7 * 61
    for block in range(8):
        for value in range(1 << width):
            if value not in allowed:
                clauses.append(forbidden_clause(mapping, block, width, value))
    stream = io.StringIO()
    stream.write(f"p cnf {len(mapping)} {len(clauses) + len(xors)}\n")
    for clause in clauses:
        stream.write(" ".join(map(str, clause)) + " 0\n")
    for row, rhs in xors:
        stream.write(("x" if rhs else "x-") + str(row[0]))
        stream.write(" " + " ".join(map(str, row[1:])) + " 0\n")
    raw = stream.getvalue().encode("ascii")
    live_counts = circuit.live_counts([node for row in outputs for node in row])
    meta = {"kind": kind, "base_dimension": width, "offset": offset,
            "target_coordinate": target, "primary_variables": circuit.nvars,
            "cnf_variables": len(mapping), "cnf_clauses": len(clauses),
            "native_xor_rows": len(xors), "output_zero_units": 7 * 61,
            "allowed_coordinate_values": len(allowed),
            "forbidden_coordinate_values": (1 << width) - len(allowed),
            "membership_forbid_clauses": 8 * ((1 << width) - len(allowed)),
            "live_gates": live_counts, "raw_xcnf_bytes": len(raw),
            "raw_xcnf_sha256": sha(raw), "planted_witness": {"available": False}}
    return raw, meta


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    assert args.out_dir.is_dir()
    parent_blob, chain_blob = PARENT.read_bytes(), CHAIN.read_bytes()
    parent, chain = json.loads(parent_blob), json.loads(chain_blob)
    bases = {kind: json.loads(path.read_bytes()) for kind, path in BASES.items()}
    assert parent["parent_sha256"][str(CHAIN.relative_to(ROOT))] == sha(chain_blob)
    assert chain["selected_channel"] in range(4)
    arms = []
    for kind, width in (("torsion_phi", 10), ("classical_raw_x", 9)):
        base = bases[kind]
        offset = base["selected_offset"]
        allowed = allowed_values(kind, base, offset, width)
        for channel in range(4):
            target = (chain["target_channel_phi"][channel] if kind == "torsion_phi"
                      else chain["target_channels"][channel][0])
            if channel == chain["selected_channel"]:
                row = next(arm for arm in parent["arms"] if arm["kind"] == kind)
                assert row["target_coordinate"] == target
                assert sha((ROOT / row["gzip_path"]).read_bytes()) == row["gzip_sha256"]
                meta = dict(row)
                meta["provenance"] = "reused frozen selected-channel artifact"
            else:
                raw, meta = encode(kind, width, offset, target, chain["gamma"], allowed)
                path = args.out_dir / f"{kind}_channel_{channel}.xcnf.gz"
                meta["gzip_path"] = str(path.resolve().relative_to(ROOT))
                meta["gzip_sha256"] = write_gzip(path, raw)
                meta["gzip_bytes"] = path.stat().st_size
                meta["provenance"] = "new target-constant variant"
            meta["channel"] = channel
            arms.append(meta)
    output = {"schema": "icperf-binary-all-channels-xcnf-v1",
              "scope": "eight membership-constrained input formulas; no solver, relation yield, rank or speed claim",
              "source_sha256": sha(Path(__file__).read_bytes()),
              "parent_manifest_sha256": sha(parent_blob), "chain_sha256": sha(chain_blob),
              "base_sha256": {kind: sha(path.read_bytes()) for kind, path in BASES.items()},
              "selected_channel": chain["selected_channel"],
              "curve": chain["curve"], "arms": arms}
    with (args.out_dir / "manifest.json").open("x") as stream:
        json.dump(output, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"arms": len(arms), "new_files": sum(a["provenance"].startswith("new") for a in arms)}, sort_keys=True))


if __name__ == "__main__":
    main()
