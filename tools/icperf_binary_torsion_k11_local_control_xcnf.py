"""Freeze four m8 XCNF target channels for the same-width random control.

The four raw targets and seven-equation torsion circuit match the weighted
k11 candidate. Only the target-blind accepted-coordinate set changes.
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
from tools.icperf_binary_circuit_xcnf import allowed_values, write_gzip  # noqa: E402

BASE = ROOT / "research/icperf_binary_torsion_k11_local_control_20261017/base.json"
CHAIN = ROOT / "research/icperf_binary_torsion_m8_chain_20261017/chain.json"
CANDIDATE = ROOT / "research/icperf_binary_torsion_k11_xcnf_20261017/manifest.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    assert args.out_dir.is_dir()
    base, chain, candidate = [json.loads(p.read_bytes()) for p in (BASE, CHAIN, CANDIDATE)]
    assert base["curve"] == chain["curve"] == candidate["curve"]
    assert candidate["chain_sha256"] == sha(CHAIN)
    offset, width = base["selected_offset"], base["selection"]["width"]
    assert offset == candidate["selected_offset"] == 4096 and width == 11
    allowed = allowed_values("torsion_phi", base, offset, width)
    assert len(allowed) == 632
    reference = {row["channel"]: row for row in candidate["arms"]}
    assert set(reference) == set(range(4))
    arms = []
    for channel, target in enumerate(chain["target_channel_phi"]):
        raw, meta = encode("torsion_phi", width, offset, target, chain["gamma"], allowed)
        prior = reference[channel]
        for key in ("primary_variables", "live_gates", "cnf_clauses",
                    "native_xor_rows", "membership_forbid_clauses"):
            assert meta[key] == prior[key], key
        path = args.out_dir / f"torsion_phi_channel_{channel}.xcnf.gz"
        meta["gzip_path"] = str(path.resolve().relative_to(ROOT))
        meta["gzip_sha256"] = write_gzip(path, raw)
        meta["gzip_bytes"] = path.stat().st_size
        meta["channel"] = channel
        arms.append(meta)
    output = {"schema": "icperf-binary-torsion-k11-local-control-xcnf-v1",
              "scope": "four exact membership and seven-equation control inputs; no solver or speed claim",
              "source_sha256": sha(Path(__file__)), "base_sha256": sha(BASE),
              "chain_sha256": sha(CHAIN), "candidate_manifest_sha256": sha(CANDIDATE),
              "curve": base["curve"], "selected_offset": offset,
              "projected_columns": base["candidate_scans"][0]["projected_columns"],
              "arms": arms}
    with (args.out_dir / "manifest.json").open("x") as stream:
        json.dump(output, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"arms": len(arms), "columns": output["projected_columns"],
                      "gzip_bytes": sum(row["gzip_bytes"] for row in arms)}, sort_keys=True))


if __name__ == "__main__":
    main()
