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
import resource
from pathlib import Path
import sys
import time

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


def transfer_points(walk_path: Path, index: int, scalar: int) -> dict:
    """Build a scalar-free, public-point record for one saved endpoint."""
    header, source_model, source_curve, source_generator = graph.load_vertex(
        Path(walk_path), 0)
    endpoint_header, endpoint_model, endpoint_curve, endpoint_generator = graph.load_vertex(
        Path(walk_path), index)
    if endpoint_header["stratum"] != header["stratum"]:
        raise ValueError("source and finalist strata differ")
    if not 1 <= scalar < source_curve.r:
        raise ValueError("source scalar must be a nonzero group scalar")
    source_q = graph.multiply(scalar, source_generator, source_curve)
    endpoint_q = graph.multiply(scalar, endpoint_generator, endpoint_curve)
    if source_q is None or endpoint_q is None:
        raise ValueError("source or endpoint target is identity")
    pair = {"G": list(source_generator), "Q": list(source_q)}
    return {
        "source_model": source_model,
        "source_generator": source_generator,
        "source_Q": source_q,
        "source_points_sha256": hashlib.sha256(json.dumps(
            pair, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "generator": endpoint_generator,
        "Q": endpoint_q,
        "endpoint_j": endpoint_model["j"],
    }


def prepare(walk_path: Path, index: int, arm: str, base_root: bytes,
            target_root: bytes, verifier_root: bytes,
            target_count: int | None = None) -> tuple[bytes, dict]:
    preparation_started = time.monotonic()
    cpu_started = resource.getrusage(resource.RUSAGE_SELF)
    walk_path = Path(walk_path).resolve()
    if len({base_root, target_root, verifier_root}) != 3 or any(
            len(root) != 32 for root in (base_root, target_root, verifier_root)):
        raise ValueError("three distinct 256-bit roots are required")
    if arm not in ORDINARY_ARMS:
        raise ValueError("solve stage supports the three prespecified ordinary bases only")
    header, model, curve, generator = graph.load_vertex(walk_path, index)
    source_header, source_model, _, _ = graph.load_vertex(walk_path, 0)
    if source_header["stratum"] != header["stratum"]:
        raise ValueError("source and finalist strata differ")
    stratum = header["stratum"]
    expected = SOLVE_TARGETS[stratum]
    if target_count is None:
        target_count = expected
    if target_count != expected:
        raise ValueError("solve-stage quota differs from the frozen contract")
    config = graph.SCHEDULE[stratum]
    target_started = time.monotonic()
    k, coefficients, target_rejections = graph.target_coefficients(
        target_root, stratum, "solve", curve.r, target_count, verifier_root)
    q = graph.multiply(k, generator, curve)
    public_points = transfer_points(walk_path, index, k)
    target_seconds = time.monotonic() - target_started
    if q is None or public_points["generator"] != generator or public_points["Q"] != q:
        raise AssertionError("public transfer pair differs from the solve-stage G,Q")
    base_started = time.monotonic()
    base, base_rejections = graph.base_points(
        curve, config["B"], arm, base_root, stratum, model["j"])
    base_seconds = time.monotonic() - base_started
    target_point_started = time.monotonic()
    targets = [(alpha, beta, graph.multiply(scalar, generator, curve))
               for alpha, beta, scalar in coefficients]
    target_point_seconds = time.monotonic() - target_point_started
    if any(point is None for _, _, point in targets):
        raise AssertionError("solve-stage target construction failed")
    rows = [f"curve {curve.p} {curve.a} {curve.b} {curve.r} {len(base)} {len(targets)}"]
    rows.extend(f"base {i} {x} {y}" for i, (x, y) in enumerate(base))
    rows.extend(f"target {i} {alpha} {beta} {point[0]} {point[1]}"
                for i, (alpha, beta, point) in enumerate(targets))
    serialization_started = time.monotonic()
    payload = ("\n".join(rows) + "\n").encode()
    serialization_seconds = time.monotonic() - serialization_started
    cpu_ended = resource.getrusage(resource.RUSAGE_SELF)
    sources = (Path(__file__), Path(graph.__file__), LEGACY / "prepare_input.py",
               LEGACY / "verify_collector.py")
    metadata = {
        "schema": graph.SCHEMA, "stratum": stratum, "index": index,
        "j": model["j"], "arm": arm, "stage": "solve",
        "seed_mode": "independent_verifier_root",
        "p": curve.p, "a": curve.a, "b": curve.b, "r": curve.r,
        "target_count": target_count, "schedule_conformant": True,
        "base_abscissae": config["B"], "generator": generator, "Q": q,
        # Public points only: these let a later rootless worker time the
        # source-to-finalist map without receiving the verifier root or scalar.
        **{key: public_points[key] for key in (
            "source_model", "source_generator", "source_Q", "source_points_sha256")},
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
        "preparation_measurement": {
            "schema": "ectd.graph-solve-preparation-measurement/v1",
            "wall_seconds": time.monotonic() - preparation_started,
            "process_cpu_seconds": (cpu_ended.ru_utime + cpu_ended.ru_stime -
                                    cpu_started.ru_utime - cpu_started.ru_stime),
            "peak_rss_platform_units": cpu_ended.ru_maxrss,
            "target_stream_and_source_pair_seconds": target_seconds,
            "base_generation_seconds": base_seconds,
            "target_point_construction_seconds": target_point_seconds,
            "serialization_seconds": serialization_seconds,
            "target_count": target_count,
            "base_point_count": len(base),
        },
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
