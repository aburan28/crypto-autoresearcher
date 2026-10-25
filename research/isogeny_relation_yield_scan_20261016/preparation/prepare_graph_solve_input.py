"""Prepare one finalist solve-stage arm on an independent target domain.

This additive module leaves the frozen discovery/confirmation preparer intact.
It derives the same source generator and endpoint points with the existing
verified helpers, but uses the distinct ``solve`` domain separator and quota.
It prepares inputs only; admission and execution are separate gates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
STUDY = Path(__file__).resolve().parents[1]
LEGACY = ROOT / "research/conductor_relation_yield_20261014"
sys.path.insert(0, str(STUDY / "preparation"))
sys.path.insert(0, str(LEGACY))

import prepare_graph_input as graph  # noqa: E402

SOLVE_TARGETS = {"P29": 32768, "P37": 32768}
ORDINARY_ARMS = {"low_x", "mid_x", "random_x"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(walk_path: Path, index: int, arm: str, base_root: bytes,
            target_root: bytes, verifier_root: bytes,
            target_count: int | None = None) -> tuple[bytes, dict]:
    walk_path = Path(walk_path).resolve()
    if len({base_root, target_root, verifier_root}) != 3 or any(
            len(root) != 32 for root in (base_root, target_root, verifier_root)):
        raise ValueError("three distinct 256-bit roots are required")
    if arm not in ORDINARY_ARMS:
        raise ValueError("solve stage supports the three prespecified ordinary bases only")
    header, model, curve, generator = graph.load_vertex(walk_path, index)
    stratum = header["stratum"]
    expected = SOLVE_TARGETS[stratum]
    if target_count is None:
        target_count = expected
    if target_count != expected:
        raise ValueError("solve-stage quota differs from the frozen contract")
    config = graph.SCHEDULE[stratum]
    k, coefficients, target_rejections = graph.target_coefficients(
        target_root, stratum, "solve", curve.r, target_count, verifier_root)
    q = graph.multiply(k, generator, curve)
    if q is None:
        raise AssertionError("selected solve-stage Q is identity")
    base, base_rejections = graph.base_points(
        curve, config["B"], arm, base_root, stratum, model["j"])
    targets = [(alpha, beta, graph.multiply(scalar, generator, curve))
               for alpha, beta, scalar in coefficients]
    if any(point is None for _, _, point in targets):
        raise AssertionError("solve-stage target construction failed")
    rows = [f"curve {curve.p} {curve.a} {curve.b} {curve.r} {len(base)} {len(targets)}"]
    rows.extend(f"base {i} {x} {y}" for i, (x, y) in enumerate(base))
    rows.extend(f"target {i} {alpha} {beta} {point[0]} {point[1]}"
                for i, (alpha, beta, point) in enumerate(targets))
    payload = ("\n".join(rows) + "\n").encode()
    sources = (Path(__file__), Path(graph.__file__), LEGACY / "prepare_input.py",
               LEGACY / "verify_collector.py")
    metadata = {
        "schema": graph.SCHEMA, "stratum": stratum, "index": index,
        "j": model["j"], "arm": arm, "stage": "solve",
        "seed_mode": "independent_verifier_root",
        "p": curve.p, "a": curve.a, "b": curve.b, "r": curve.r,
        "target_count": target_count, "schedule_conformant": True,
        "base_abscissae": config["B"], "generator": generator, "Q": q,
        "base_rejections": base_rejections,
        "target_rejections": target_rejections,
        "base_root_sha256": hashlib.sha256(base_root).hexdigest(),
        "target_root_sha256": hashlib.sha256(target_root).hexdigest(),
        "verifier_root_sha256": hashlib.sha256(verifier_root).hexdigest(),
        "graph_sha256": digest(walk_path),
        "source_sha256": {str(path.resolve().relative_to(ROOT)): digest(path)
                          for path in sources},
        "input_sha256": hashlib.sha256(payload).hexdigest(),
        "base_sha256": hashlib.sha256(json.dumps(base, separators=(",", ":")).encode()).hexdigest(),
        "target_vector_sha256": hashlib.sha256(json.dumps(targets, separators=(",", ":")).encode()).hexdigest(),
        "limits": "fresh solve-stage preparation only; no solve or ECDLP cost claim",
    }
    return payload, metadata


def read_root(path: Path) -> bytes:
    value = Path(path).read_text().strip()
    if len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise ValueError("root file must contain one lowercase 256-bit hex value")
    return bytes.fromhex(value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--walk", type=Path, required=True)
    parser.add_argument("--index", type=int, required=True)
    parser.add_argument("--arm", choices=sorted(ORDINARY_ARMS), required=True)
    for name in ("base-root-file", "target-root-file", "verifier-root-file",
                 "commitment", "output-dir"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    roots = {name: read_root(getattr(args, name + "_root_file"))
             for name in ("base", "target", "verifier")}
    if len(set(roots.values())) != 3:
        parser.error("base, target and verifier roots must differ")
    commitment = json.loads(args.commitment.read_text())
    expected = {name + "_root_sha256": hashlib.sha256(value).hexdigest()
                for name, value in roots.items()}
    if any(commitment.get(key) != value for key, value in expected.items()):
        parser.error("solve commitment does not bind supplied roots")
    if commitment.get("graph_sha256") != digest(args.walk):
        parser.error("solve commitment does not bind this graph")
    header, _, _, _ = graph.load_vertex(args.walk, args.index)
    if commitment.get("stratum") not in (None, header.get("stratum")):
        parser.error("solve commitment stratum differs")
    for source in (Path(__file__), Path(graph.__file__),
                   LEGACY / "prepare_input.py", LEGACY / "verify_collector.py"):
        relative = str(source.resolve().relative_to(ROOT))
        if commitment.get("source_sha256", {}).get(relative) != digest(source):
            parser.error("solve commitment source hash differs: " + relative)
    payload, metadata = prepare(args.walk, args.index, args.arm,
                                roots["base"], roots["target"], roots["verifier"])
    metadata["commitment_sha256"] = digest(args.commitment)
    args.output_dir.mkdir(mode=0o700, parents=False, exist_ok=False)
    with (args.output_dir / "prepared.txt").open("xb") as output:
        output.write(payload)
    with (args.output_dir / "manifest.json").open("x") as output:
        json.dump(metadata, output, indent=2, sort_keys=True)
        output.write("\n")
    print(json.dumps(metadata, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
