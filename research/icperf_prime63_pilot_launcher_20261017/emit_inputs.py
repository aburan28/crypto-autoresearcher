"""Deterministic public positive inputs for TASK-20261017-4d8c00.

Only this producer sees signed witnesses.  Solver-facing JSON contains the
frozen base, target point, and the archived sparse polynomial encoding.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import random
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]
from crypto_autoresearcher.index_calculus.curve import Curve
from crypto_autoresearcher.index_calculus.factor_base import FactorBase
from crypto_autoresearcher.index_calculus.msolve import decomposition_system, evaluate
from tools.icperf_prime_coset_quadratic import lift_system, serialize

OUT = Path(__file__).resolve().parent
ARCHIVE = ROOT / "research/icperf_prime_475_target_systems_20261017/systems.json.gz"
SCAN = ROOT / "research/icperf_prime_coset_896_20261017/scan.json"
CONTROLS = ROOT / "research/icperf_prime_475_controls_20261017/controls.json"
DOMAIN = "ICPERF-PRIME63-PLANTED-V1"
FORM_SEED = 20261017


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def strict_json(path):
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt") as stream:
        return json.load(stream, parse_int=int, parse_float=Decimal)


def bases(archive, scan, controls):
    selected = next(a for a in scan["attempts"] if a["base_parameters"]["seed"] == scan["selected_seed"])
    c = archive["curve"]
    result = {"coset": (selected["points"], selected["base_parameters"], "subgroup")}
    for row in controls["controls"]:
        result[row["kind"]] = (row["points"], row["parameters"], row["kind"])
    assert set(result) == {"coset", "random", "small_x"}
    assert all(len(v[0]) == 475 for v in result.values())
    return {arm: FactorBase(kind, [tuple(p) for p in points], params, c["p"])
            for arm, (points, params, kind) in result.items()}


def selection(E, fb, arm, m, public_targets):
    """Fixed SHA stream; public targets are consulted only for collision rejection."""
    accepted, rejected, seen = [], [], set()
    total = None
    for index in range(100000):
        digest = hashlib.sha256(f"{DOMAIN}|{arm}|{m}|{index}".encode()).digest()
        point = fb.points[int.from_bytes(digest[:16], "big") % len(fb.points)]
        x, y = point
        sign = -1 if digest[16] & 1 else 1
        signed = point if sign == 1 else E.neg(point)
        if x in seen:
            rejected.append({"index": index, "reason": "repeated_x"})
            continue
        candidate = E.add(total, signed)
        if candidate is None:
            rejected.append({"index": index, "reason": "infinity_sum"})
            continue
        if tuple(candidate) in public_targets:
            rejected.append({"index": index, "reason": "public_target_collision"})
            continue
        accepted.append({"index": index, "point": list(point), "sign": sign,
                         "signed_point": list(signed), "digest_sha256": digest.hex()})
        seen.add(x)
        total = candidate
        if len(accepted) == m:
            return accepted, rejected, list(total)
    raise RuntimeError("selection exhausted")


def root_values(E, direct, encoded, points, m):
    """Evaluate the archived direct separating form at the signed-free x chain."""
    xs = [int(p[0]) for p in points]
    sums, total = [], None
    for point in points:
        total = E.add(total, tuple(point))
        if total is None:
            raise ValueError("unsigned partial sum at infinity")
        sums.append(total)
    values = xs + [int(sums[k + 1][0]) for k in range(m - 2)] + [0]
    values[-1] = -evaluate(direct.polys[-1], values, E.p) % E.p
    assert all(evaluate(poly, values, E.p) == 0 for poly in direct.polys)
    mapped = dict(zip(direct.names, values))
    for name in encoded["variables"]:
        if name.startswith("q"):
            factor, exponent = name[1:].split("_")
            mapped[name] = pow(xs[int(factor) - 1], int(exponent), E.p)
    ordered = [mapped[name] for name in encoded["variables"]]
    return {name: str(value) for name, value in zip(encoded["variables"], ordered)}


def build():
    archive, scan, controls = map(strict_json, (ARCHIVE, SCAN, CONTROLS))
    assert archive["curve"] == scan["curve"] == controls["curve"]
    c = archive["curve"]
    E = Curve(c["p"], c["a"], c["b"], c["order"])
    arms = bases(archive, scan, controls)
    targets = {tuple(row["point"]) for row in archive["targets"]}
    public, witnesses = [], []
    for arm in ("coset", "random", "small_x"):
        fb = arms[arm]
        for m in (2, 8):
            selected, rejected, target = selection(E, fb, arm, m, targets)
            points = [row["point"] for row in selected]
            signed_points = [row["signed_point"] for row in selected]
            if arm == "coset":
                lifted, direct, _, _ = lift_system(E, fb, target[0], m, FORM_SEED)
                encoded, encoder = serialize(lifted), "quadratic_lift"
            else:
                direct = decomposition_system(E, fb, target[0], m, random.Random(FORM_SEED))
                encoded, encoder = serialize(direct), "direct"
            root = root_values(E, direct, encoded, signed_points, m)
            cell = f"{arm}-m{m}"
            public.append({"cell": cell, "arm": arm, "m": m, "p": str(c["p"]),
                           "curve": c, "target_point": [str(v) for v in target],
                           "base_points": [[str(x), str(y)] for x, y in fb.points],
                           "base_parameters": fb.params, "encoder": encoder,
                           "variables": encoded["variables"], "equations": encoded["equations"],
                           "encoding": encoded,
                           "base_point_sha256": sha_points(fb.points)})
            witnesses.append({"cell": cell, "selected": selected, "rejections": rejected,
                              "root": root, "target_point": [str(v) for v in target]})
    return {"schema": "icperf-prime63-planted-public-v1", "domain": DOMAIN,
            "curve": c, "systems": public}, {
            "schema": "icperf-prime63-planted-witnesses-v1", "domain": DOMAIN,
            "witnesses": witnesses}


def sha_points(points):
    payload = json.dumps([list(p) for p in points], separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def main():
    public, witnesses = build()
    path = OUT / "planted_public.json.gz"
    with path.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", filename="", mtime=0) as stream:
            stream.write((json.dumps(public, sort_keys=True, separators=(",", ":")) + "\n").encode())
    (OUT / "planted_witnesses.json").write_text(json.dumps(witnesses, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"systems": len(public["systems"]), "public_sha256": sha(path),
                      "witness_sha256": sha(OUT / "planted_witnesses.json")}, sort_keys=True))


if __name__ == "__main__":
    main()
