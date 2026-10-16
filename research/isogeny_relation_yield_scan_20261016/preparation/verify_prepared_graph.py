"""Replay structural and group-law checks on one prepared graph input.

The group arithmetic uses harness.toycurve, separate from the preparer's
verify_collector implementation. Random-base uniformity requires the committed
base root and is checked by optional post-seal deterministic replay.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from math import isqrt
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from harness.toycurve import EllipticCurve


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_prepared(path):
    lines = Path(path).read_text().splitlines()
    head = lines[0].split()
    if len(head) != 7 or head[0] != "curve":
        raise ValueError("bad prepared header")
    p, a, b, r, nbase, ntarget = map(int, head[1:])
    if len(lines) != 1 + nbase + ntarget or nbase % 2:
        raise ValueError("bad prepared record count")
    base = []
    for i, line in enumerate(lines[1:1 + nbase]):
        terms = line.split()
        if len(terms) != 4 or terms[:2] != ["base", str(i)]:
            raise ValueError("bad base row")
        base.append(tuple(map(int, terms[2:])))
    targets = []
    for i, line in enumerate(lines[1 + nbase:]):
        terms = line.split()
        if len(terms) != 6 or terms[:2] != ["target", str(i)]:
            raise ValueError("bad target row")
        targets.append(tuple(map(int, terms[2:])))
    return (p, a, b, r), base, targets


def expected_xs(p, a, b, count, rule):
    if rule == "low_x":
        values = range(p)
    elif rule == "mid_x":
        values = ((p // 2 + i) % p for i in range(p))
    else:
        raise ValueError("unsupported deterministic base rule")
    out = []
    for x in values:
        rhs = (x * x * x + a * x + b) % p
        if rhs and pow(rhs, (p - 1) // 2, p) == 1:
            out.append(x)
            if len(out) == count:
                return out
    raise ValueError("insufficient liftable x-values")


def verify(prepared_path, manifest_path, base_root_path=None, target_root_path=None):
    manifest = json.loads(Path(manifest_path).read_text())
    if manifest.get("schema") != "isogeny-relation-input/v1" or sha(prepared_path) != manifest["input_sha256"]:
        raise ValueError("manifest or prepared digest mismatch")
    (p, a, b, r), base, targets = read_prepared(prepared_path)
    E = EllipticCurve(p, a, b)
    G, Q = tuple(manifest["generator"]), tuple(manifest["Q"])
    if not E.is_on_curve(G) or not E.is_on_curve(Q) or E.mul(r, G) is not None or E.mul(r, Q) is not None:
        raise ValueError("generator or Q certificate failed")
    if abs(r - (p + 1)) > isqrt(4 * p) or 2 * r <= p + 1 + isqrt(4 * p):
        raise ValueError("Hasse uniqueness failed")
    if len(base) != 2 * manifest["base_abscissae"] or len(targets) != manifest["target_count"]:
        raise ValueError("base or target count mismatch")
    for i in range(0, len(base), 2):
        point, inverse = base[i], base[i + 1]
        if not E.is_on_curve(point) or inverse != E.negate(point) or point[1] != min(point[1], p - point[1]):
            # A transported base can reverse the canonical sign convention.
            if manifest["arm"] != "u2_transport" or not E.is_on_curve(point) or inverse != E.negate(point):
                raise ValueError("signed base pair failed")
    if len({base[i][0] for i in range(0, len(base), 2)}) != len(base) // 2:
        raise ValueError("duplicate base x-orbit")
    arm = manifest["arm"]
    base_x = [base[i][0] for i in range(0, len(base), 2)]
    if arm in ("low_x", "mid_x", "u2_native"):
        rule = "low_x" if arm != "mid_x" else "mid_x"
        if base_x != expected_xs(p, a, b, len(base_x), rule):
            raise ValueError("deterministic native base rule failed")
    if arm == "u2_transport":
        source_a, source_b = a * pow(16, -1, p) % p, b * pow(64, -1, p) % p
        if base_x != [4 * x % p for x in expected_xs(p, source_a, source_b, len(base_x), "low_x")]:
            raise ValueError("transported coordinate base rule failed")
    seen = set()
    for alpha, beta, x, y in targets:
        point = x, y
        if not (0 <= alpha < r and 1 <= beta < r) or point in seen or not E.is_on_curve(point):
            raise ValueError("target law or uniqueness failed")
        if E.add(E.mul(alpha, G), E.mul(beta, Q)) != point:
            raise ValueError("target group equation failed")
        seen.add(point)
    base_digest = hashlib.sha256(json.dumps(base, separators=(",", ":")).encode()).hexdigest()
    target_digest = hashlib.sha256(json.dumps([(u, v, (x, y)) for u, v, x, y in targets], separators=(",", ":")).encode()).hexdigest()
    if base_digest != manifest["base_sha256"] or target_digest != manifest["target_vector_sha256"]:
        raise ValueError("base or target-vector digest mismatch")
    replay = False
    if base_root_path is not None and target_root_path is not None:
        roots = [bytes.fromhex(Path(path).read_text().strip()) for path in (base_root_path, target_root_path)]
        if [hashlib.sha256(root).hexdigest() for root in roots] != [manifest["base_root_sha256"], manifest["target_root_sha256"]]:
            raise ValueError("root digest mismatch")
        from prepare_graph_input import prepare
        study = Path(__file__).resolve().parents[1]
        walk = study / ("walk-p29-2048-attempt2.jsonl" if manifest["stratum"] == "P29" else "walk-p37-256.jsonl")
        regenerated, _ = prepare(walk, manifest["index"], arm, manifest["stage"], roots[0], roots[1], len(targets))
        if regenerated != Path(prepared_path).read_bytes():
            raise ValueError("seed replay differs")
        replay = True
    return {"status": "pass", "targets_checked": len(targets), "base_points_checked": len(base),
            "arm": arm, "group_law_replayed": True, "deterministic_seed_replay": replay,
            "limit": "relation completeness, rank and solve cost not checked"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepared", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--base-root", type=Path)
    parser.add_argument("--target-root", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.prepared, args.manifest, args.base_root, args.target_root), sort_keys=True))
