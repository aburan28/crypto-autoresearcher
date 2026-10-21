"""Turn a k11 XCNF primary assignment into exact full-point relation checks.

Accepts the weighted candidate or its same-width local random control and
any of their four raw target channels. A Boolean root is accepted only after
the archived coordinate equations and an exact raw-curve point sum pass.
The synthetic self-check constructs its own target and is not a solver run.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.icperf_binary_root_certificate import certificate  # noqa: E402
from tools.icperf_binary_torsion_coordinate import phi_from_x  # noqa: E402
from tools.icperf_ordinary_binary_fixture import add, scale  # noqa: E402

CHAIN = ROOT / "research/icperf_binary_torsion_m8_chain_20261017/chain.json"
INPUTS = {
    "weighted": (ROOT / "research/icperf_binary_torsion_k11_weighted_20261017/base.json",
                 ROOT / "research/icperf_binary_torsion_k11_xcnf_20261017/manifest.json"),
    "local_random": (ROOT / "research/icperf_binary_torsion_k11_local_control_20261017/base.json",
                     ROOT / "research/icperf_binary_torsion_k11_local_control_xcnf_20261017/manifest.json"),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(label: str) -> tuple[dict, dict, dict]:
    base_path, manifest_path = INPUTS[label]
    base, manifest, chain = [json.loads(p.read_bytes()) for p in (base_path, manifest_path, CHAIN)]
    assert manifest["base_sha256"] == sha(base_path)
    assert manifest["chain_sha256"] == sha(CHAIN)
    assert base["curve"] == chain["curve"] == manifest["curve"]
    assert manifest["selected_offset"] == base["selected_offset"] == 4096
    assert {arm["channel"] for arm in manifest["arms"]} == set(range(4))
    assert all(arm["kind"] == "torsion_phi" and arm["base_dimension"] == 11
               for arm in manifest["arms"])
    return base, manifest, chain


def primary_from_model(path: Path, nvars: int) -> int:
    """Read a SAT model's signed DIMACS literals; require every primary bit."""
    signed = {}
    sat = False
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("c"):
            continue
        if line.startswith("s "):
            assert line == "s SATISFIABLE", "model is not a SAT result"
            sat = True
            continue
        assert line[0] == "v", "expected DIMACS model lines starting with v"
        for token in line[1:].split():
            literal = int(token)
            if literal == 0:
                continue
            index = abs(literal)
            if index > nvars:
                continue
            value = literal > 0
            assert index not in signed or signed[index] == value, "contradictory literal"
            signed[index] = value
    assert sat and set(signed) == set(range(1, nvars + 1)), "incomplete primary assignment"
    return sum(1 << (index - 1) for index, value in signed.items() if value)


def check(label: str, channel: int, assignment: int) -> dict:
    base, manifest, chain = load(label)
    arm = next(row for row in manifest["arms"] if row["channel"] == channel)
    assert arm["target_coordinate"] == chain["target_channel_phi"][channel]
    assert 0 <= assignment < (1 << arm["primary_variables"])
    bound_chain = dict(chain, selected_channel=channel)
    result = certificate(assignment, base, bound_chain, arm)
    return {"schema": "icperf-binary-k11-root-certificate-v1",
            "scope": "one direct full-point assignment check; no root search or ECDLP cost result",
            "source_sha256": sha(Path(__file__)), "base_kind": label,
            "base_sha256": sha(INPUTS[label][0]), "manifest_sha256": sha(INPUTS[label][1]),
            "chain_sha256": sha(CHAIN), "channel": channel,
            "assignment_hex": hex(assignment), "result": result}


def synthetic_control(label: str) -> dict:
    """Build one known relation under a separate synthetic target for each base."""
    base, manifest, chain = load(label)
    scan = next(row for row in base["candidate_scans"] if row["offset"] == 4096)
    reps = scan["selected_representatives"][:8]
    ts = [row[0] for row in reps]
    points = [tuple(row[1:]) for row in reps]
    gamma, b = chain["gamma"], chain["curve"]["b_polynomial_bits"]
    assert all(phi_from_x(point[0], gamma) == t for point, t in zip(points, ts))
    partial, total = [], None
    for point in points:
        total = add(total, point, b)
        assert total is not None and total[0] != gamma
        partial.append(total)
    us = [phi_from_x(point[0], gamma) for point in partial[1:7]]
    target_t = phi_from_x(total[0], gamma)
    projected = scale(4, total, b)
    assert projected is not None
    width = 11
    assignment = sum((t ^ 4096) << (i * width) for i, t in enumerate(ts))
    assignment |= sum(t << (8 * width + i * 61) for i, t in enumerate(us))
    synthetic_chain = copy.deepcopy(chain)
    synthetic_chain["target_channels"] = [list(total) for _ in range(4)]
    synthetic_chain["target_channel_phi"] = [target_t for _ in range(4)]
    synthetic_chain["subgroup_target"] = list(projected)
    checks = []
    for channel in range(4):
        arm = dict(next(row for row in manifest["arms"] if row["channel"] == channel),
                   target_coordinate=target_t)
        bound = dict(synthetic_chain, selected_channel=channel)
        accepted = certificate(assignment, base, bound, arm)
        assert accepted["certified"] and accepted["unique_projected_rows"] == 1
        flipped = certificate(assignment ^ 1, base, bound, arm)
        assert not flipped.get("certified", False)
        checks.append({"channel": channel, "certified": True,
                       "sign_certificates": len(accepted["full_point_certificates"]),
                       "unique_projected_rows": accepted["unique_projected_rows"],
                       "bit_flip_certified": flipped.get("certified", False)})
    return {"base_kind": label, "base_sha256": sha(INPUTS[label][0]),
            "manifest_sha256": sha(INPUTS[label][1]),
            "input_representatives": reps, "intermediate_phi": us,
            "synthetic_raw_target": list(total), "synthetic_projected_target": list(projected),
            "synthetic_target_phi": target_t, "assignment_hex": hex(assignment),
            "channels": checks}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-kind", choices=INPUTS)
    parser.add_argument("--channel", type=int, choices=range(4))
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--assignment-hex")
    group.add_argument("--model-file", type=Path)
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.self_check:
        assert args.base_kind is None and args.channel is None
        assert args.assignment_hex is None and args.model_file is None
        output = {"schema": "icperf-binary-k11-root-synthetic-controls-v1",
                  "scope": "synthetic known-point extraction checks, not archived-target relation yield",
                  "source_sha256": sha(Path(__file__)), "chain_sha256": sha(CHAIN),
                  "bases": [synthetic_control(label) for label in INPUTS]}
    else:
        assert args.base_kind is not None and args.channel is not None
        assert (args.assignment_hex is None) != (args.model_file is None)
        _, manifest, _ = load(args.base_kind)
        arm = next(row for row in manifest["arms"] if row["channel"] == args.channel)
        assignment = (int(args.assignment_hex, 16) if args.assignment_hex is not None else
                      primary_from_model(args.model_file, arm["primary_variables"]))
        output = check(args.base_kind, args.channel, assignment)
        if args.model_file is not None:
            output["model_sha256"] = sha(args.model_file)
    with args.out.open("x") as stream:
        json.dump(output, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"schema": output["schema"],
                      "checked_bases": len(output.get("bases", [])),
                      "certified": output.get("result", {}).get("certified", False)}, sort_keys=True))


if __name__ == "__main__":
    main()
