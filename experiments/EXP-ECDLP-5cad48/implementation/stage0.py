#!/usr/bin/env python3
"""Stage 0 of EXP-ECDLP-5cad48: reproduce the KN-FIND-ffe1df fixture.

Exact whole-group FFT convolution from analysis/o2-sum-compatible-filters/rt_exp_1.py.
Certificate kind none. No SMALL-W / LARGE-W reading. No a98ea9 Stage 5.
"""
from __future__ import annotations

import hashlib
import json
import platform
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
O2 = REPO / "analysis" / "o2-sum-compatible-filters"
sys.path.insert(0, str(O2))
from fourier_obstruction import dlog_table  # noqa: E402

P = 65539
A = 0
B = 11
N = 65287
M = 40
SHUFFLE_SEED = 20260803

WINDOWS = {
    "floor(Mx/p)": {"M_delta": (1.001, 1.004), "M_max_pi": (1.082, 1.086)},
    "sha": {"M_max_pi": (1.080, 1.084)},
    "P2": {"G": (19.9, 20.1)},
}


def _git_info() -> dict:
    def _run(args):
        try:
            return subprocess.run(
                ["git"] + args, cwd=REPO, capture_output=True, text=True, timeout=30
            ).stdout.strip()
        except Exception as exc:
            return f"error: {exc}"

    dirty = _run(["status", "--porcelain"])
    return {
        "commit": _run(["rev-parse", "HEAD"]),
        "dirty": dirty != "",
        "dirty_summary": dirty[:2000],
    }


def peak_rss_bytes() -> int:
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024


def bucket_stats(hv: np.ndarray, m: int, n: int) -> dict:
    used = np.flatnonzero(np.bincount(hv, minlength=m) > 0)
    if len(used) < m:
        remap = -np.ones(m, dtype=np.int64)
        remap[used] = np.arange(len(used))
        hv, m = remap[hv], len(used)
    if m < 2:
        raise RuntimeError("M_eff < 2")
    ind = np.zeros((m, n))
    for a in range(m):
        ind[a] = hv == a
    counts = ind.sum(axis=1)
    fourier = np.fft.rfft(ind, axis=1)
    fourier_s = np.fft.fft(fourier, axis=0)
    w_s = np.fft.ifft(fourier_s * fourier_s, axis=0)
    w = np.fft.irfft(w_s, n=n, axis=1).real
    num = np.stack([w[:, hv == c].sum(axis=1) for c in range(m)], axis=1)
    den = np.real(np.fft.ifft(np.fft.fft(counts) ** 2))
    pi = num / np.maximum(den[:, None], 1e-12)
    g = m * float(pi.max())
    tot = float(n) ** 2
    deltas = [sum(num[(c - d) % m, c] for c in range(m)) / tot for d in range(m)]
    dstar = int(np.argmax(deltas))
    delta = float(deltas[dstar])
    q = counts / n
    pi_c = pi[(np.arange(m) - dstar) % m, np.arange(m)]
    w_rel = float(np.sum(q * (pi_c / delta - 1.0) ** 2))
    min_q = float(q.min())
    return {
        "M_eff": int(m),
        "M_delta": m * delta,
        "G": g,
        "W": w_rel,
        "min_q": min_q,
        "cs_bound": 1.0 + (w_rel / max(min_q, 1e-18)) ** 0.5,
        "dstar": dstar,
    }


def _sha_label(x: int) -> int:
    return int(hashlib.sha256(str(int(x)).encode()).hexdigest(), 16) % M


def in_window(value: float, lo: float, hi: float) -> bool:
    return lo <= value <= hi


def main() -> int:
    t0 = time.time()
    exp_dir = Path(__file__).resolve().parents[1]
    run_dir = exp_dir / "runs" / "RUN-ECDLP-5cad48-S0"
    run_dir.mkdir(parents=True, exist_ok=True)

    g0, pts = dlog_table(P, A, B, N)
    if len(pts) != N:
        raise RuntimeError(f"dlog table length {len(pts)} != {N}")
    xs = np.array([0 if pt is None else pt[0] for pt in pts], dtype=np.int64)
    rng = np.random.default_rng(SHUFFLE_SEED)
    floor_h = (xs * M) // P
    shuf = floor_h.copy()
    rng.shuffle(shuf)
    arms = {
        "floor(Mx/p)": floor_h,
        "x mod M": xs % M,
        "sha": np.array([_sha_label(int(v)) for v in xs], dtype=np.int64),
        "shuffle": shuf,
        "P2": (np.arange(N, dtype=np.int64) * M) // N,
    }
    results = {}
    for name, hv in arms.items():
        results[name] = bucket_stats(hv, M, N)

    checks = {
        "floor_M_delta": in_window(results["floor(Mx/p)"]["M_delta"], *WINDOWS["floor(Mx/p)"]["M_delta"]),
        "floor_M_max_pi": in_window(results["floor(Mx/p)"]["G"], *WINDOWS["floor(Mx/p)"]["M_max_pi"]),
        "sha_M_max_pi": in_window(results["sha"]["G"], *WINDOWS["sha"]["M_max_pi"]),
        "p2_G": in_window(results["P2"]["G"], *WINDOWS["P2"]["G"]),
    }
    fixture_pass = all(checks.values())
    wall = time.time() - t0
    raw = {
        "experiment_id": "EXP-ECDLP-5cad48",
        "run_id": "RUN-ECDLP-5cad48-S0",
        "stage": 0,
        "certificate_kind": "none",
        "fixture": {"p": P, "a": A, "b": B, "N": N, "M": M, "G0": list(g0)},
        "shuffle_seed": SHUFFLE_SEED,
        "arms": {
            k: {kk: (float(vv) if isinstance(vv, (float, np.floating)) else int(vv)) for kk, vv in v.items()}
            for k, v in results.items()
        },
        "windows": WINDOWS,
        "checks": checks,
        "fixture_pass": fixture_pass,
        "p2_W_note": "P2 is known-large G, not known-large W. Near-zero W is expected.",
        "not_a_W_decay_claim": True,
        "not_a98ea9_stage5": True,
        "h_ecdlp_07c7c6_unchanged": True,
        "wall_clock_seconds": wall,
    }
    (run_dir / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    stdout = (
        f"EXP-ECDLP-5cad48 Stage 0 fixture_pass={fixture_pass}\n"
        f"floor M*delta={results['floor(Mx/p)']['M_delta']:.6f} "
        f"G={results['floor(Mx/p)']['G']:.6f} W={results['floor(Mx/p)']['W']:.6f}\n"
        f"xmod  M*delta={results['x mod M']['M_delta']:.6f} "
        f"G={results['x mod M']['G']:.6f} W={results['x mod M']['W']:.6f}\n"
        f"sha   G={results['sha']['G']:.6f} W={results['sha']['W']:.6f}\n"
        f"P2    G={results['P2']['G']:.6f} W={results['P2']['W']:.6f}\n"
        f"checks={checks}\n"
    )
    print(stdout, end="")
    (run_dir / "stdout.log").write_text(stdout)
    (run_dir / "stderr.log").write_text("")
    (run_dir / "command.txt").write_text("python3 implementation/stage0.py\n")
    env = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "numpy": np.__version__,
    }
    (run_dir / "environment.json").write_text(json.dumps(env, indent=2) + "\n")
    validity = "valid" if fixture_pass else "failed_infrastructure"
    reason = (
        "Stage 0 fixture windows matched KN-FIND-ffe1df / REDTEAM digits."
        if fixture_pass
        else f"Stage 0 fixture miss: {checks}. Infrastructure, not mathematics."
    )
    manifest = {
        "run": {
            "id": "RUN-ECDLP-5cad48-S0",
            "experiment_id": "EXP-ECDLP-5cad48",
            "hypothesis_id": "H-ECDLP-2ade73",
            "goal_id": "GOAL-ECDLP-001",
            "batch_id": "BATCH-5a5091",
            "task_id": "TASK-20260907-6114ae",
            "stage": 0,
            "status": "completed_valid" if fixture_pass else "failed_infrastructure",
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "code": {**_git_info(), "command": "python3 implementation/stage0.py"},
            "inference": {
                "requested_policy": "executor-implementation",
                "resolved_model_id": "cursor-grok-4.6-cloud-agent",
                "model_provenance": "cursor cloud agent session acting as executor",
                "model_verified": False,
                "reasoning_effort": "medium",
                "fallback_used": False,
                "degraded_requirements": None,
            },
            "environment": {**env, "artifact": "environment.json"},
            "inputs": {
                "parameters": {
                    "p": P,
                    "a": A,
                    "b": B,
                    "N": N,
                    "M": M,
                    "authorized_stages": [0],
                },
                "seeds": {"declared": [SHUFFLE_SEED], "note": "Seed governs shuffle only."},
            },
            "timing": {"wall_clock_seconds": round(wall, 3)},
            "resources": {
                "wall_clock_seconds": round(wall, 3),
                "peak_rss_bytes": peak_rss_bytes(),
            },
            "result": {
                "validity_status": validity,
                "valid": fixture_pass,
                "validity_reason": reason,
                "certificate": {
                    "kind": "none",
                    "verified": True,
                    "note": "Observation-only fixture; no discrete log.",
                },
                "metrics": {
                    "fixture_pass": fixture_pass,
                    "checks": checks,
                    "floor_M_delta": float(results["floor(Mx/p)"]["M_delta"]),
                    "floor_G": float(results["floor(Mx/p)"]["G"]),
                    "sha_G": float(results["sha"]["G"]),
                    "p2_G": float(results["P2"]["G"]),
                    "not_a_W_decay_claim": True,
                },
                "scientific_boundary": (
                    "Stage 0 fixture only. W is recorded, not classified. "
                    "No Stage 1/2. No a98ea9 Stage 5. No H-07c7c6 change."
                ),
            },
            "artifacts": {
                "raw_result": "raw-result.json",
                "stdout": "stdout.log",
                "stderr": "stderr.log",
                "environment": "environment.json",
                "command": "command.txt",
            },
        }
    }
    import yaml

    (run_dir / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False))
    report = {
        "execution_report": {
            "experiment_id": "EXP-ECDLP-5cad48",
            "run_id": "RUN-ECDLP-5cad48-S0",
            "stage": 0,
            "task_id": "TASK-20260907-6114ae",
            "status": "completed" if fixture_pass else "failed_infrastructure",
            "fixture_pass": fixture_pass,
            "certificate_kind": "none",
            "observations_not_conclusions": {
                "W_recorded": True,
                "SMALL_W_or_LARGE_W": False,
                "h_ecdlp_07c7c6": "unchanged specified",
                "a98ea9_stage5": False,
            },
        }
    }
    (exp_dir / "execution-report-stage0.yaml").write_text(
        yaml.safe_dump(report, sort_keys=False)
    )
    return 0 if fixture_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
