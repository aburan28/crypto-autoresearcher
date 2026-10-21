"""Verify four k11 weighted-base XCNF files independently of their emitter."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.icperf_binary_all_channels_xcnf_verify import evaluate  # noqa: E402
from tools.icperf_binary_circuit_xcnf_verify import verify_arm  # noqa: E402

MANIFEST = ROOT / "research/icperf_binary_torsion_k11_xcnf_20261017/manifest.json"
BASE = ROOT / "research/icperf_binary_torsion_k11_weighted_20261017/base.json"
CHAIN = ROOT / "research/icperf_binary_torsion_m8_chain_20261017/chain.json"
SUPPORT = ROOT / "research/icperf_binary_torsion_k11_weighted_20261017/circuit_support.json"
PRIOR = ROOT / "research/icperf_binary_all_channels_xcnf_20261017/manifest.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    manifest, base, chain, support = [json.loads(path.read_bytes()) for path in
                                      (MANIFEST, BASE, CHAIN, SUPPORT)]
    assert manifest["source_sha256"] == sha(ROOT / "tools/icperf_binary_torsion_k11_xcnf.py")
    assert manifest["base_sha256"] == sha(BASE) and manifest["chain_sha256"] == sha(CHAIN)
    assert manifest["circuit_support_sha256"] == sha(SUPPORT)
    assert manifest["prior_all_channels_sha256"] == sha(PRIOR)
    assert manifest["projected_columns"] == 316 and manifest["selected_offset"] == 4096
    assert len(manifest["arms"]) == 4
    assert {arm["channel"] for arm in manifest["arms"]} == set(range(4))
    checks = []
    for arm in manifest["arms"]:
        assert arm["kind"] == "torsion_phi" and arm["base_dimension"] == 11
        assert arm["target_coordinate"] == chain["target_channel_phi"][arm["channel"]]
        assert arm["planted_witness"] == {"available": False}
        checked = verify_arm(arm, base)
        for seed in range(3):
            evaluate(arm, base, chain, seed)
        checked["channel"] = arm["channel"]
        checked["direct_field_evaluations"] = 3
        checks.append(checked)
    selected = next(arm for arm in manifest["arms"] if arm["channel"] == chain["selected_channel"])
    assert selected["live_gates"] == support["live_gates"]
    assert selected["membership_forbid_clauses"] == support["exact_membership_forbid_clauses"]
    output = {"schema": "icperf-binary-torsion-k11-xcnf-verification-v1",
              "scope": "serialized gate, membership and direct field checks; no selected-formula solver run",
              "source_sha256": sha(Path(__file__)), "manifest_sha256": sha(MANIFEST),
              "base_sha256": sha(BASE), "chain_sha256": sha(CHAIN),
              "arms": checks}
    with args.out.open("x") as stream:
        json.dump(output, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"arms": len(checks), "direct_field_evaluations": 3 * len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
