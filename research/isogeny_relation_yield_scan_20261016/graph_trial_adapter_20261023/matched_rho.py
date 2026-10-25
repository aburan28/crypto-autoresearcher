"""Run one plain r-adding Pollard-rho solve on the prepared exact G,Q pair."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import platform
import random
import resource
import sys
import time
import types
from pathlib import Path

STUDY = Path(__file__).resolve().parents[1]
ROOT = STUDY.parents[1]
LEGACY_DRIVER = ROOT / "experiments/EXP-ECTD-001/driver"
RHO_SOURCE = LEGACY_DRIVER / "rho_bsgs.py"
CURVE_SOURCE = LEGACY_DRIVER / "curve.py"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rho_module():
    package_name = "ectd_matched_rho"
    if package_name not in sys.modules:
        package = types.ModuleType(package_name)
        package.__path__ = [str(LEGACY_DRIVER)]
        sys.modules[package_name] = package
    return importlib.import_module(package_name + ".rho_bsgs")


def run(input_path: Path, manifest_path: Path, seed: int,
        max_steps: int = 60_000_000) -> dict:
    manifest = json.loads(manifest_path.read_text())
    p, a, b, order = (manifest[key] for key in ("p", "a", "b", "r"))
    generator = tuple(manifest["generator"])
    target = tuple(manifest["Q"])
    module = rho_module()
    start = time.monotonic()
    cpu_start = resource.getrusage(resource.RUSAGE_SELF)
    scalar, ops, steps, restarts = module.pollard_rho_plain(
        generator, target, order, a, p, random.Random(seed),
        max_steps=max_steps)
    elapsed = time.monotonic() - start
    cpu_end = resource.getrusage(resource.RUSAGE_SELF)
    verified = (scalar is not None and
                module.independent_verify_discrete_log(scalar, generator,
                                                       target, a, p))
    return {
        "schema": "ectd.graph-matched-rho-result/v1",
        "status": "verified_scalar" if verified else
                  ("censored_step_cap" if scalar is None else "invalid_scalar"),
        "method": "plain_r_adding_walk_no_negation",
        "input_sha256": sha(input_path), "prepared_manifest_sha256": sha(manifest_path),
        "rho_source_sha256": sha(RHO_SOURCE), "curve_source_sha256": sha(CURVE_SOURCE),
        "p": p, "a": a, "b": b,
        "r": order, "generator": list(generator), "Q": list(target),
        "seed": seed, "max_steps": max_steps, "scalar": scalar if verified else None,
        "group_ops": ops, "steps": steps, "degenerate_restarts": restarts,
        "verified": verified, "wall_seconds": elapsed,
        "process_cpu_seconds": (cpu_end.ru_utime + cpu_end.ru_stime -
                                cpu_start.ru_utime - cpu_start.ru_stime),
        "peak_rss_platform_units": cpu_end.ru_maxrss,
        "platform": platform.platform(), "python": sys.version,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--max-steps", type=int, default=60_000_000)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.max_steps <= 0 or args.seed < 0:
        parser.error("seed and step cap must be nonnegative and positive")
    result = run(args.input, args.manifest, args.seed, args.max_steps)
    with args.out.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({key: result[key] for key in
                      ("schema", "status", "group_ops", "steps", "wall_seconds",
                       "output_sha256") if key in result}, sort_keys=True))
    return 0 if result["status"] in ("verified_scalar", "censored_step_cap") else 1


if __name__ == "__main__":
    raise SystemExit(main())
