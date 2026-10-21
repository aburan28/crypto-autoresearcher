"""Freeze four k11 weighted-base m8 torsion-coordinate XCNF inputs.

These are membership-constrained field-equation inputs for the same four
archived raw target channels as the k10 comparison. No solver is invoked.
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

BASE = ROOT / "research/icperf_binary_torsion_k11_weighted_20261017/base.json"
CHAIN = ROOT / "research/icperf_binary_torsion_m8_chain_20261017/chain.json"
SUPPORT = ROOT / "research/icperf_binary_torsion_k11_weighted_20261017/circuit_support.json"
PRIOR = ROOT / "research/icperf_binary_all_channels_xcnf_20261017/manifest.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    assert args.out_dir.is_dir()
    base, chain, support, prior = [json.loads(path.read_bytes()) for path in
                                   (BASE, CHAIN, SUPPORT, PRIOR)]
    assert support["base_sha256"] == sha(BASE) and support["chain_sha256"] == sha(CHAIN)
    assert base["curve"] == chain["curve"] and len(chain["target_channel_phi"]) == 4
    assert prior["chain_sha256"] == sha(CHAIN)
    width, offset = 11, base["selected_offset"]
    allowed = allowed_values("torsion_phi", base, offset, width)
    assert len(allowed) == 632
    arms = []
    for channel, target in enumerate(chain["target_channel_phi"]):
        raw, meta = encode("torsion_phi", width, offset, target, chain["gamma"], allowed)
        if channel == chain["selected_channel"]:
            assert meta["live_gates"] == support["live_gates"]
            assert meta["membership_forbid_clauses"] == support["exact_membership_forbid_clauses"]
        path = args.out_dir / f"torsion_phi_channel_{channel}.xcnf.gz"
        meta["gzip_path"] = str(path.resolve().relative_to(ROOT))
        meta["gzip_sha256"] = write_gzip(path, raw)
        meta["gzip_bytes"] = path.stat().st_size
        meta["channel"] = channel
        arms.append(meta)
    output = {"schema": "icperf-binary-torsion-k11-xcnf-v1",
              "scope": "four exact coordinate-membership and seven-equation inputs; no solver, relation yield, rank or speed claim",
              "source_sha256": sha(Path(__file__)), "base_sha256": sha(BASE),
              "chain_sha256": sha(CHAIN), "circuit_support_sha256": sha(SUPPORT),
              "prior_all_channels_sha256": sha(PRIOR),
              "curve": base["curve"], "selected_offset": offset,
              "projected_columns": support["projected_columns"], "arms": arms}
    with (args.out_dir / "manifest.json").open("x") as stream:
        json.dump(output, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"arms": len(arms), "columns": support["projected_columns"],
                      "gzip_bytes": sum(a["gzip_bytes"] for a in arms)}, sort_keys=True))


if __name__ == "__main__":
    main()
