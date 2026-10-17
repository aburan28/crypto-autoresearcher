"""Matched variable-width controls for the archived binary ANF support scan."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.icperf_binary_boolean_support import (equations, eval_anf,
                                                  support_stats, trial_mask)  # noqa: E402

PARENT = ROOT / "research/icperf_binary_boolean_support_20261017/support.json"
CHAIN = ROOT / "research/icperf_binary_torsion_m8_chain_20261017/chain.json"
SOURCE = ROOT / "tools/icperf_binary_boolean_support.py"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    parent_bytes, chain_bytes = PARENT.read_bytes(), CHAIN.read_bytes()
    parent, chain = json.loads(parent_bytes), json.loads(chain_bytes)
    assert parent["chain_sha256"] == hashlib.sha256(chain_bytes).hexdigest()
    assert parent["source_sha256"] == hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    gamma = parent["arms"][0]["target_coordinate"]
    assert gamma == chain["target_channel_phi"][chain["selected_channel"]]
    gamma = chain["gamma"]
    configs = [("torsion_phi", 9, 1024, chain["target_channel_phi"][chain["selected_channel"]]),
               ("classical_raw_x", 10, 1024, chain["raw_sum"][0])]
    arms = []
    for kind, k, offset, target in configs:
        nvars = 8*k + 6*61
        polys = equations(kind, k, offset, target, gamma)
        stats = [support_stats(poly, nvars) for poly in polys]
        trials = []
        for i in range(8):
            mask = trial_mask(kind, i, nvars)
            trials.append({"assignment_hex": hex(mask),
                           "field_equation_values": [eval_anf(poly, mask) for poly in polys]})
        arms.append({"kind": kind, "base_dimension": k, "offset": offset,
                     "boolean_variables": nvars, "target_coordinate": target,
                     "equation_stats": stats,
                     "total_coefficient_bit_terms": sum(row["coefficient_bit_terms"] for row in stats),
                     "trial_rows": trials})
    result = {"schema": "icperf-binary-boolean-support-width-controls-v1",
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "parent_support_sha256": hashlib.sha256(parent_bytes).hexdigest(),
              "parent_source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "chain_sha256": hashlib.sha256(chain_bytes).hexdigest(),
              "arms": arms,
              "scope": "symbolic equal-width controls; offsets are not matched realized factor-base sizes; no solver or speed claim"}
    with args.out.open("x") as stream:
        json.dump(result, stream, sort_keys=True, indent=2)
        stream.write("\n")
    print(json.dumps({"path": str(args.out), "terms": {a["kind"]: a["total_coefficient_bit_terms"] for a in arms}}, sort_keys=True))


if __name__ == "__main__":
    main()
