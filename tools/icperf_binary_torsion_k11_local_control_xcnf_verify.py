"""Verify serialized four-channel XCNF for the same-width local control."""

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

MANIFEST = ROOT / "research/icperf_binary_torsion_k11_local_control_xcnf_20261017/manifest.json"
BASE = ROOT / "research/icperf_binary_torsion_k11_local_control_20261017/base.json"
CHAIN = ROOT / "research/icperf_binary_torsion_m8_chain_20261017/chain.json"
CANDIDATE = ROOT / "research/icperf_binary_torsion_k11_xcnf_20261017/manifest.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    manifest, base, chain, candidate = [json.loads(p.read_bytes()) for p in
                                        (MANIFEST, BASE, CHAIN, CANDIDATE)]
    assert manifest["source_sha256"] == sha(ROOT / "tools/icperf_binary_torsion_k11_local_control_xcnf.py")
    assert manifest["base_sha256"] == sha(BASE) and manifest["chain_sha256"] == sha(CHAIN)
    assert manifest["candidate_manifest_sha256"] == sha(CANDIDATE)
    assert manifest["projected_columns"] == 316 and manifest["selected_offset"] == 4096
    assert len(manifest["arms"]) == len(candidate["arms"]) == 4
    assert {arm["channel"] for arm in manifest["arms"]} == set(range(4))
    reference = {arm["channel"]: arm for arm in candidate["arms"]}
    checks = []
    for arm in manifest["arms"]:
        assert arm["kind"] == "torsion_phi" and arm["base_dimension"] == 11
        assert arm["target_coordinate"] == chain["target_channel_phi"][arm["channel"]]
        assert arm["planted_witness"] == {"available": False}
        prior = reference[arm["channel"]]
        for key in ("primary_variables", "live_gates", "cnf_clauses",
                    "native_xor_rows", "membership_forbid_clauses"):
            assert arm[key] == prior[key]
        checked = verify_arm(arm, base)
        for seed in range(3):
            evaluate(arm, base, chain, seed)
        checked["channel"] = arm["channel"]
        checked["direct_field_evaluations"] = 3
        checks.append(checked)
    output = {"schema": "icperf-binary-torsion-k11-local-control-xcnf-verification-v1",
              "scope": "serialized gate, membership and direct field checks; no solver run",
              "source_sha256": sha(Path(__file__)), "manifest_sha256": sha(MANIFEST),
              "base_sha256": sha(BASE), "chain_sha256": sha(CHAIN),
              "candidate_manifest_sha256": sha(CANDIDATE), "arms": checks}
    with args.out.open("x") as stream:
        json.dump(output, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"arms": len(checks), "direct_field_evaluations": 3*len(checks)},
                     sort_keys=True))


if __name__ == "__main__":
    main()
