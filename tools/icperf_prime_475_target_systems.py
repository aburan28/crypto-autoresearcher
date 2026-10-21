"""Freeze common public known-answer targets and exact m=2..8 prime systems.

These are solver inputs, not decomposition attempts or ECDLP measurements.
The scalar is public only to make the target arithmetic independently replayable;
it must never be used by a solver or described as an unseen target.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]
from crypto_autoresearcher.index_calculus.curve import Curve  # noqa: E402
from crypto_autoresearcher.index_calculus.factor_base import FactorBase  # noqa: E402
from crypto_autoresearcher.index_calculus.msolve import decomposition_system  # noqa: E402
from tools.icperf_prime_coset_quadratic import lift_system, serialize  # noqa: E402

FIXTURE = ROOT / "research/icperf_prime_fixtures_20261017/n63_seed20261017.json"
SCAN = ROOT / "research/icperf_prime_coset_896_20261017/scan.json"
CONTROLS = ROOT / "research/icperf_prime_475_controls_20261017/controls.json"
ENCODER = ROOT / "tools/icperf_prime_coset_quadratic.py"
MSOLVE = ROOT / "src/crypto_autoresearcher/index_calculus/msolve.py"
DOMAIN = "icperf-prime-475-public-known-answer-v1"
FORM_SEED = 20261017


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_record() -> dict:
    fixture = json.loads(FIXTURE.read_bytes())
    scan = json.loads(SCAN.read_bytes())
    controls = json.loads(CONTROLS.read_bytes())
    c = fixture["curve"]
    assert c == scan["curve"] == controls["curve"]
    assert c["order"] > 2**50 and c["order"] < 2**63
    curve = Curve(c["p"], c["a"], c["b"], c["order"])
    generator = tuple(fixture["witness"])
    assert curve.is_on_curve(generator)
    assert curve.mul(c["order"], generator) is None
    selected = next(a for a in scan["attempts"]
                    if a["base_parameters"]["seed"] == scan["selected_seed"])
    assert selected["realized_size"] == controls["size"] == 475
    arms = {"coset": FactorBase("subgroup", [tuple(p) for p in selected["points"]],
                                selected["base_parameters"], c["p"])}
    for row in controls["controls"]:
        arms[row["kind"]] = FactorBase(row["kind"], [tuple(p) for p in row["points"]],
                                       row["parameters"], c["p"])
    assert set(arms) == {"coset", "random", "small_x"}
    targets = []
    for m in range(2, 9):
        digest = hashlib.sha256(f"{DOMAIN}|{sha(FIXTURE)}|{m}".encode()).digest()
        scalar = 1 + int.from_bytes(digest, "big") % (c["order"] - 1)
        point = curve.mul(scalar, generator)
        assert point is not None and curve.is_on_curve(point)
        targets.append({"m": m, "scalar": scalar, "point": list(point),
                        "derivation_sha256": digest.hex()})
    assert len({tuple(t["point"]) for t in targets}) == 7
    systems = []
    for target in targets:
        m = target["m"]
        for name in ("coset", "random", "small_x"):
            base = arms[name]
            if name == "coset":
                lifted, direct, _, _ = lift_system(curve, base, target["point"][0],
                                                   m, FORM_SEED)
                encodings = {"direct": serialize(direct), "quadratic_lift": serialize(lifted)}
            else:
                direct = decomposition_system(curve, base, target["point"][0],
                                              m, random.Random(FORM_SEED))
                encodings = {"direct": serialize(direct)}
            systems.append({"m": m, "arm": name, "target_point": target["point"],
                            "encodings": encodings})
    return {"schema": "icperf-prime-475-target-systems-v1",
            "scope": "public known-answer common-target input preparation only; no solver, natural relation, regularity, rank or end-to-end observation",
            "source_sha256": sha(Path(__file__)), "fixture_sha256": sha(FIXTURE),
            "scan_sha256": sha(SCAN), "controls_sha256": sha(CONTROLS),
            "encoder_sha256": sha(ENCODER), "msolve_source_sha256": sha(MSOLVE),
            "target_domain": DOMAIN, "separating_form_seed": FORM_SEED,
            "curve": c, "generator": list(generator), "base_size": 475,
            "targets": targets, "systems": systems}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    record = build_record()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("xb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", filename="", mtime=0) as compressed:
            compressed.write((json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode())
    print(json.dumps({"targets": len(record["targets"]), "systems": len(record["systems"]),
                      "sha256": sha(args.out), "bytes": args.out.stat().st_size}, sort_keys=True))


if __name__ == "__main__":
    main()
