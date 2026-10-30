"""Run a fixed-scalar P37 24-edge control of the finalist transfer adapter."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
STUDY = ROOT / "research/isogeny_relation_yield_scan_20261016"
sys.path.insert(0, str(STUDY / "preparation"))
import prepare_graph_input as graph
from prepare_graph_solve_input import transfer_points

WALK = STUDY / "walk-p37-256.jsonl"
RUNNER = STUDY / "graph_trial_adapter_20261023/path_transfer.py"
CHECKER = STUDY / "graph_trial_adapter_20261023/check_path_transfer.py"
ENDPOINT = 24


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    out = args.output_dir.resolve()
    out.mkdir(mode=0o700, parents=True, exist_ok=False)
    runner = shutil.which("sage")
    if runner is None:
        raise RuntimeError("Sage executable is unavailable")

    # These fixed roots are public implementation-control fixtures. They are
    # not the post-freeze target stream or an admitted experiment seed.
    roots = {"base": b"B" * 32, "target": b"T" * 32,
             "verifier": b"V" * 32}
    with WALK.open(encoding="utf-8") as stream:
        header = json.loads(next(stream))
    scalar = graph.draw(roots["verifier"], ["P37", "solve", "q_scalar"],
                        header["r"] - 1)[0] + 1
    manifests = {}
    for name, index in (("source", 0), ("endpoint", ENDPOINT)):
        points = transfer_points(WALK, index, scalar)
        _, model, curve, _ = graph.load_vertex(WALK, index)
        manifest = {
            "schema": graph.SCHEMA, "stage": "solve", "stratum": "P37",
            "index": index, "j": model["j"], "p": curve.p,
            "a": curve.a, "b": curve.b, "r": curve.r,
            "generator": points["generator"], "Q": points["Q"],
            "source_model": points["source_model"],
            "source_generator": points["source_generator"],
            "source_Q": points["source_Q"],
            "source_points_sha256": points["source_points_sha256"],
            "fixture_kind": "public fixed-scalar implementation control",
        }
        path = out / f"{name}-manifest.json"
        write_json(path, manifest)
        manifests[name] = path

    commands = [
        [runner, "-python", str(RUNNER), "--stratum", "P37", "--index",
         str(ENDPOINT), "--source-manifest", str(manifests["source"]),
         "--endpoint-manifest", str(manifests["endpoint"]), "--out", str(out / "transfer.json")],
        [runner, "-python", str(CHECKER), "--stratum", "P37", "--index",
         str(ENDPOINT), "--source-manifest", str(manifests["source"]),
         "--endpoint-manifest", str(manifests["endpoint"]), "--result",
         str(out / "transfer.json"), "--out", str(out / "check.json")],
    ]
    write_json(out / "command.json", {
        "command": "run_control.py --output-dir " + str(out),
        "runner_command": commands[0], "checker_command": commands[1],
        "runner_sha256": sha(RUNNER), "checker_sha256": sha(CHECKER),
        "control_source_sha256": sha(Path(__file__)),
        "walk_sha256": sha(WALK), "fixture_root_sha256": {
            key: hashlib.sha256(value).hexdigest() for key, value in roots.items()},
        "fixed_scalar_value_written_to_artifacts": False,
    })
    attempts = []
    for name, command in zip(("runner", "checker"), commands):
        started = time.monotonic()
        proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True,
                              check=False)
        elapsed = time.monotonic() - started
        (out / f"{name}.stdout").write_text(proc.stdout, encoding="utf-8")
        (out / f"{name}.stderr").write_text(proc.stderr, encoding="utf-8")
        attempts.append({"phase": name, "return_code": proc.returncode,
                         "wall_seconds": elapsed,
                         "stdout_sha256": sha(out / f"{name}.stdout"),
                         "stderr_sha256": sha(out / f"{name}.stderr")})
        if proc.returncode != 0:
            break
    record = {
        "schema": "ectd.graph-path-transfer-control.v1",
        "status": "completed" if len(attempts) == 2 and attempts[-1]["return_code"] == 0
                  else "invalid",
        "stratum": "P37", "endpoint_index": ENDPOINT,
        "saved_edge_count": ENDPOINT,
        "known_scalar_fixture": True,
        "scientific_target_stream": False,
        "attempts": attempts,
    }
    write_json(out / "attempt.json", record)
    return 0 if record["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
