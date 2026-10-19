"""Count the selected k11 weighted-base m8 circuit and membership input.

Uses the frozen schoolbook GF(2^61) Circuit construction and seven Pphi3
equations. This is an input-size diagnostic, not a solver or cost trial.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.icperf_binary_circuit_xcnf import construct  # noqa: E402
from tools.icperf_binary_torsion_coordinate import pphi3  # noqa: E402

BASE = ROOT / "research/icperf_binary_torsion_k11_weighted_20261017/base.json"
CHAIN = ROOT / "research/icperf_binary_torsion_m8_chain_20261017/chain.json"
PRIOR = ROOT / "research/icperf_binary_circuit_xcnf_20261017/manifest.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    base, chain, prior = [json.loads(path.read_bytes()) for path in (BASE, CHAIN, PRIOR)]
    selected = next(row for row in base["candidate_scans"]
                    if row["offset"] == base["selected_offset"])
    width, offset, gamma = 11, base["selected_offset"], base["coordinate"]["gamma"]
    assert chain["gamma"] == gamma and chain["curve"] == base["curve"]
    target = chain["target_channel_phi"][chain["selected_channel"]]
    circuit, outputs = construct("torsion_phi", width, offset, target, gamma)
    counts = circuit.live_counts([node for row in outputs for node in row])
    allowed = selected["accepted_phi"]
    assert len(allowed) == 632 and all(offset <= t < offset + (1 << width) for t in allowed)
    checks = []
    for seed in range(3):
        h = hashlib.sha256(f"k11-weighted-input:{seed}".encode()).digest()
        ts = [allowed[int.from_bytes(h[i:i+2], "big") % len(allowed)] for i in range(0, 16, 2)]
        us = [int.from_bytes(hashlib.sha256(h + bytes([i])).digest()[:8], "big") & ((1 << 61) - 1)
              for i in range(6)]
        assignment = sum((t ^ offset) << (i * width) for i, t in enumerate(ts))
        assignment |= sum(u << (8 * width + i * 61) for i, u in enumerate(us))
        triples = [[ts[0], ts[1], us[0]]]
        triples += [[us[i-1], ts[i+1], us[i]] for i in range(1, 6)]
        triples += [[us[-1], ts[-1], target]]
        observed = [circuit.evaluate(row, assignment) for row in outputs]
        expected = [pphi3(*row, gamma) for row in triples]
        assert observed == expected
        checks.append({"seed": seed, "base_phi": ts, "intermediate_phi": us,
                       "equation_values": observed})
    prior_arm = next(a for a in prior["arms"] if a["kind"] == "torsion_phi")
    forbidden = (1 << width) - len(allowed)
    output = {"schema": "icperf-binary-torsion-k11-circuit-support-v1",
              "scope": "selected-channel circuit and exact membership input counts; no solver, relation or ECDLP cost",
              "source_sha256": sha(Path(__file__)), "base_sha256": sha(BASE),
              "chain_sha256": sha(CHAIN), "prior_manifest_sha256": sha(PRIOR),
              "channel": chain["selected_channel"], "target_phi": target,
              "base_dimension": width, "offset": offset,
              "projected_columns": selected["projected_columns"],
              "accepted_coordinate_values": len(allowed),
              "primary_variables": circuit.nvars, "output_zero_units": 7*61,
              "live_gates": counts,
              "exact_membership_forbidden_values": forbidden,
              "exact_membership_forbid_clauses": 8 * forbidden,
              "cnf_gate_clauses_plus_output_and_membership":
                  3 * counts["and"] + 7*61 + 8*forbidden,
              "native_xor_rows": counts["xor"],
              "direct_field_controls": checks,
              "prior_k10_selected": {"projected_columns": prior_arm["allowed_coordinate_values"]//2,
                                     "primary_variables": prior_arm["primary_variables"],
                                     "live_gates": prior_arm["live_gates"],
                                     "membership_forbid_clauses": prior_arm["membership_forbid_clauses"]}}
    with args.out.open("x") as stream:
        json.dump(output, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"live_gates": counts, "membership_clauses": 8*forbidden,
                      "primary_variables": circuit.nvars}, sort_keys=True))


if __name__ == "__main__":
    main()
