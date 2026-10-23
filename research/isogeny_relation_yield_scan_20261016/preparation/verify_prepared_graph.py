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


def verify(prepared_path, manifest_path, base_root_path=None, target_root_path=None,
           verifier_root_path=None):
    manifest = json.loads(Path(manifest_path).read_text())
    if manifest.get("schema") != "isogeny-relation-input/v1" or sha(prepared_path) != manifest["input_sha256"]:
        raise ValueError("manifest or prepared digest mismatch")
    if (manifest.get("seed_mode") not in (None, "independent_verifier_root") or
            (manifest.get("seed_mode") == "independent_verifier_root") !=
            ("verifier_root_sha256" in manifest)):
        raise ValueError("manifest seed mode differs")
    (p, a, b, r), base, targets = read_prepared(prepared_path)
    E = EllipticCurve(p, a, b)
    G, Q = tuple(manifest["generator"]), tuple(manifest["Q"])
    if not E.is_on_curve(G) or not E.is_on_curve(Q) or E.mul(r, G) is not None or E.mul(r, Q) is not None:
        raise ValueError("generator or Q certificate failed")
    if abs(r - (p + 1)) > isqrt(4 * p) or 2 * r <= p + 1 + isqrt(4 * p):
        raise ValueError("Hasse uniqueness failed")
    if len(base) != 2 * manifest["base_abscissae"] or len(targets) != manifest["target_count"]:
        raise ValueError("base or target count mismatch")
    arm = manifest["arm"]
    for i in range(0, len(base), 2):
        point, inverse = base[i], base[i + 1]
        if not E.is_on_curve(point) or inverse != E.negate(point) or point[1] != min(point[1], p - point[1]):
            # A transported base can reverse the canonical sign convention.
            if arm not in ("u2_transport", "graph_transport") or not E.is_on_curve(point) or inverse != E.negate(point):
                raise ValueError("signed base pair failed")
    if len({base[i][0] for i in range(0, len(base), 2)}) != len(base) // 2:
        raise ValueError("duplicate base x-orbit")
    base_x = [base[i][0] for i in range(0, len(base), 2)]
    if arm in ("low_x", "mid_x", "u2_native"):
        rule = "low_x" if arm != "mid_x" else "mid_x"
        if base_x != expected_xs(p, a, b, len(base_x), rule):
            raise ValueError("deterministic native base rule failed")
    if arm == "u2_transport":
        source_a, source_b = a * pow(16, -1, p) % p, b * pow(64, -1, p) % p
        if base_x != [4 * x % p for x in expected_xs(p, source_a, source_b, len(base_x), "low_x")]:
            raise ValueError("transported coordinate base rule failed")
    if arm == "graph_transport":
        study = Path(__file__).resolve().parents[1]
        stratum = manifest["stratum"]
        if stratum not in ("P29", "P37"):
            raise ValueError("unsupported graph transport stratum")
        stride, size, end = ((8, 256, 2048) if stratum == "P29" else (4, 1600, 256))
        index = manifest["index"]
        if not isinstance(index, int) or not 0 <= index <= end or index % stride or len(base) != 2 * size:
            raise ValueError("graph transport check-vertex schedule differs")
        directory = study / "path_transport/controls" / f"{stratum.lower()}-twoedge-attempt1"
        walk = study / ("walk-p29-2048-attempt2.jsonl" if stratum == "P29" else "walk-p37-256.jsonl")
        checkpoint_path = directory / f"edge-{index:04d}.json"
        expected_path = str(checkpoint_path.relative_to(ROOT))
        checkpoint = json.loads(checkpoint_path.read_text())
        path_manifest = json.loads((directory / "manifest.json").read_text())
        if (manifest.get("checkpoint_path") != expected_path or
                manifest.get("checkpoint_sha256") != sha(checkpoint_path) or
                manifest.get("checkpoint_manifest_sha256") != sha(directory / "manifest.json") or
                manifest.get("checkpoint_terminal_sha256") != sha(directory / f"edge-{end:04d}.json") or
                path_manifest.get("schema") != "ectd.path-base-transport.v1" or
                path_manifest.get("stratum") != stratum or path_manifest.get("graph_sha256") != manifest["graph_sha256"] or
                sha(walk) != manifest["graph_sha256"] or
                path_manifest.get("p") != p or path_manifest.get("r") != r or
                path_manifest.get("check_stride") != stride or path_manifest.get("signed_base_points") != len(base) or
                checkpoint.get("index") != index or checkpoint.get("check_vertex") is not True or
                checkpoint.get("model", {}).get("a") != a or checkpoint.get("model", {}).get("b") != b or
                checkpoint.get("model", {}).get("j") != manifest["j"] or
                checkpoint.get("generator") != list(G) or
                checkpoint.get("base") != [list(point) for point in base] or
                checkpoint.get("base_sha256") != hashlib.sha256(json.dumps(checkpoint["base"], separators=(",", ":")).encode()).hexdigest()):
            raise ValueError("graph transport archive binding differs")
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
    if (base_root_path is None) != (target_root_path is None):
        raise ValueError("base and target roots must be supplied together")
    if verifier_root_path is not None and base_root_path is None:
        raise ValueError("verifier root requires base and target roots")
    if base_root_path is not None:
        roots = [bytes.fromhex(Path(path).read_text().strip()) for path in (base_root_path, target_root_path)]
        independent = manifest.get("seed_mode") == "independent_verifier_root"
        if independent != (verifier_root_path is not None):
            raise ValueError("verifier root replay mode differs from manifest")
        if independent:
            roots.append(bytes.fromhex(Path(verifier_root_path).read_text().strip()))
        expected_hashes = [manifest["base_root_sha256"], manifest["target_root_sha256"]]
        if independent:
            expected_hashes.append(manifest["verifier_root_sha256"])
        if (any(len(root) != 32 for root in roots) or len(set(roots)) != len(roots) or
                [hashlib.sha256(root).hexdigest() for root in roots] != expected_hashes):
            raise ValueError("root digest mismatch")
        study = Path(__file__).resolve().parents[1]
        walk = study / ("walk-p29-2048-attempt2.jsonl" if manifest["stratum"] == "P29" else "walk-p37-256.jsonl")
        if manifest["stage"] == "solve":
            from prepare_graph_solve_input import prepare as prepare_solve
            regenerated, _ = prepare_solve(walk, manifest["index"], arm,
                                           roots[0], roots[1], roots[2], len(targets))
        else:
            from prepare_graph_input import prepare
            regenerated, _ = prepare(walk, manifest["index"], arm, manifest["stage"],
                                     roots[0], roots[1], len(targets),
                                     roots[2] if independent else None)
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
    parser.add_argument("--verifier-root", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.prepared, args.manifest, args.base_root,
                            args.target_root, args.verifier_root), sort_keys=True))
