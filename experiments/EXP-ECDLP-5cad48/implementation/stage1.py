#!/usr/bin/env python3
"""Stage 1 of EXP-ECDLP-5cad48: exact W plus jackknife versus exact.

Two smallest RT-EXP-1 primes only. Certificate kind none.
No SMALL-W / LARGE-W reading. No Stage 2. No a98ea9 Stage 5.
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

CELLS = (
    {"id": "S1-P523", "p": 523, "a": 2, "b": 6, "N": 523, "M_grid": (5, 8, 12)},
    {"id": "S1-P1033", "p": 1033, "a": 0, "b": 5, "N": 1087, "M_grid": (6, 10, 16)},
)
ARMS = ("floor(Mx/p)", "x mod M", "sha", "shuffle", "P2")
N_PAIRS = 1_000_000
N_GROUPS = 20
SEED_BASE = 20260803
SHUFFLE_SEED = 20260803


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


def remap_labels(hv: np.ndarray, m: int) -> tuple[np.ndarray, int]:
    used = np.flatnonzero(np.bincount(hv, minlength=m) > 0)
    if len(used) < m:
        remap = -np.ones(m, dtype=np.int64)
        remap[used] = np.arange(len(used))
        hv = remap[hv]
        m = int(len(used))
    if m < 2:
        raise RuntimeError("M_eff < 2")
    return hv.astype(np.int64, copy=False), m


def bucket_stats(hv: np.ndarray, m: int, n: int) -> dict:
    hv, m = remap_labels(hv, m)
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
        "q": q,
        "hv": hv,
        "m": m,
    }


def plugin_w(hv: np.ndarray, m: int, n_group: int, pairs: np.ndarray, q: np.ndarray) -> dict:
    i = pairs[:, 0]
    j = pairs[:, 1]
    a = hv[i]
    b = hv[j]
    c = hv[(i + j) % n_group]
    s = (a + b) % m
    n = pairs.shape[0]
    deltas = np.empty(m, dtype=np.float64)
    pi_at = np.empty((m, m), dtype=np.float64)
    for d in range(m):
        target_s = (np.arange(m) - d) % m
        agree = c == ((s + d) % m)
        deltas[d] = float(np.mean(agree))
        for ct in range(m):
            mask = s == target_s[ct]
            denom = int(mask.sum())
            if denom == 0:
                pi_at[d, ct] = 0.0
            else:
                pi_at[d, ct] = float(np.mean(c[mask] == ct))
    dstar = int(np.argmax(deltas))
    delta = float(deltas[dstar])
    if delta <= 0.0:
        raise RuntimeError("plug-in delta is 0")
    pi_c = pi_at[dstar]
    w_rel = float(np.sum(q * (pi_c / delta - 1.0) ** 2))
    return {"W": w_rel, "dstar": dstar, "M_delta": m * delta, "n": n}


def jackknife_w(hv: np.ndarray, m: int, n_group: int, pairs: np.ndarray, q: np.ndarray) -> dict:
    t_all = plugin_w(hv, m, n_group, pairs, q)
    folds = np.array_split(np.arange(pairs.shape[0]), N_GROUPS)
    t_g = []
    for leave in folds:
        keep = np.ones(pairs.shape[0], dtype=bool)
        keep[leave] = False
        t_g.append(plugin_w(hv, m, n_group, pairs[keep], q)["W"])
    mean_leave = float(np.mean(t_g))
    w_jack = N_GROUPS * t_all["W"] - (N_GROUPS - 1) * mean_leave
    return {
        "W_plugin": t_all["W"],
        "W_jack": w_jack,
        "dstar_plugin": t_all["dstar"],
        "M_delta_plugin": t_all["M_delta"],
        "leave_one_group_mean": mean_leave,
    }


def _sha_label(x: int, m: int) -> int:
    return int(hashlib.sha256(str(int(x)).encode()).hexdigest(), 16) % m


def build_arms(xs: np.ndarray, p: int, n: int, m: int) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(SHUFFLE_SEED)
    floor_h = (xs * m) // p
    shuf = floor_h.copy()
    rng.shuffle(shuf)
    return {
        "floor(Mx/p)": floor_h.astype(np.int64),
        "x mod M": (xs % m).astype(np.int64),
        "sha": np.array([_sha_label(int(v), m) for v in xs], dtype=np.int64),
        "shuffle": shuf.astype(np.int64),
        "P2": ((np.arange(n, dtype=np.int64) * m) // n),
    }


def main() -> int:
    t0 = time.time()
    exp_dir = Path(__file__).resolve().parents[1]
    run_dir = exp_dir / "runs" / "RUN-ECDLP-5cad48-S1"
    run_dir.mkdir(parents=True, exist_ok=True)

    cells_out = []
    for cell_index, cell in enumerate(CELLS):
        p, a, b, n = cell["p"], cell["a"], cell["b"], cell["N"]
        _g0, pts = dlog_table(p, a, b, n)
        if len(pts) != n:
            raise RuntimeError(f"{cell['id']}: dlog table length {len(pts)} != {n}")
        xs = np.array([0 if pt is None else pt[0] for pt in pts], dtype=np.int64)
        cell_out = {"id": cell["id"], "p": p, "a": a, "b": b, "N": n, "Ms": []}
        for m in cell["M_grid"]:
            arms = build_arms(xs, p, n, m)
            m_out = {"M": int(m), "arms": {}}
            for arm_index, name in enumerate(ARMS):
                exact = bucket_stats(arms[name], m, n)
                hv, meff = exact["hv"], exact["m"]
                q = exact["q"]
                seed = SEED_BASE + 1000 * cell_index + 10 * arm_index + int(m)
                rng = np.random.default_rng(seed)
                pairs = rng.integers(0, n, size=(N_PAIRS, 2), dtype=np.int64)
                jack = jackknife_w(hv, meff, n, pairs, q)
                bias = jack["W_jack"] - exact["W"]
                m_out["arms"][name] = {
                    "M_eff": exact["M_eff"],
                    "W_exact": exact["W"],
                    "G_exact": exact["G"],
                    "M_delta_exact": exact["M_delta"],
                    "min_q": exact["min_q"],
                    "cs_bound_exact": exact["cs_bound"],
                    "dstar_exact": exact["dstar"],
                    "W_plugin": jack["W_plugin"],
                    "W_jack": jack["W_jack"],
                    "bias": bias,
                    "dstar_plugin": jack["dstar_plugin"],
                    "M_delta_plugin": jack["M_delta_plugin"],
                    "seed": seed,
                    "SMALL_W_or_LARGE_W": False,
                }
            cell_out["Ms"].append(m_out)
        cells_out.append(cell_out)

    elapsed = time.time() - t0
    raw = {
        "experiment_id": "EXP-ECDLP-5cad48",
        "run_id": "RUN-ECDLP-5cad48-S1",
        "stage": 1,
        "authorized_by": "DEC-20260907-e187e3",
        "certificate": {"kind": "none"},
        "SMALL_W_or_LARGE_W": False,
        "stage2_authorized": False,
        "a98ea9_stage5_authorized": False,
        "n_pairs": N_PAIRS,
        "n_groups": N_GROUPS,
        "seed_base": SEED_BASE,
        "q_c_source": "whole-group label vector",
        "cells": cells_out,
        "elapsed_seconds": elapsed,
        "peak_rss_bytes": peak_rss_bytes(),
        "not_a_W_decay_claim": True,
    }
    raw_path = run_dir / "raw-result.json"
    raw_path.write_text(json.dumps(raw, indent=2) + "\n")
    raw_hash = hashlib.sha256(raw_path.read_bytes()).hexdigest()

    manifest = {
        "run": {
            "id": "RUN-ECDLP-5cad48-S1",
            "experiment_id": "EXP-ECDLP-5cad48",
            "status": "valid",
            "validity_reason": "Stage 1 exactness-anchor package recorded. W unclassified.",
            "code": {"path": "experiments/EXP-ECDLP-5cad48/implementation/stage1.py"},
            "environment": {
                "python": sys.version,
                "platform": platform.platform(),
                "numpy": np.__version__,
            },
            "inputs": {
                "parameters": {
                    "cells": CELLS,
                    "n_pairs": N_PAIRS,
                    "n_groups": N_GROUPS,
                    "seed_base": SEED_BASE,
                }
            },
            "timing": {"elapsed_seconds": elapsed},
            "result": {
                "raw_result_sha256": raw_hash,
                "certificate": {"kind": "none"},
                "SMALL_W_or_LARGE_W": False,
            },
        }
    }
    (run_dir / "manifest.yaml").write_text(
        "run:\n"
        f"  id: RUN-ECDLP-5cad48-S1\n"
        f"  experiment_id: EXP-ECDLP-5cad48\n"
        f"  status: valid\n"
        f"  certificate_kind: none\n"
        f"  SMALL_W_or_LARGE_W: false\n"
        f"  raw_result_sha256: {raw_hash}\n"
    )
    (run_dir / "environment.json").write_text(
        json.dumps({"python": sys.version, "platform": platform.platform(), "numpy": np.__version__}, indent=2)
        + "\n"
    )
    (run_dir / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-5cad48/implementation/stage1.py\n"
    )
    stdout = [
        f"RUN-ECDLP-5cad48-S1 elapsed={elapsed:.3f}s raw_sha256={raw_hash}",
        "W recorded as observation only. Not SMALL-W or LARGE-W.",
    ]
    for cell in cells_out:
        stdout.append(f"{cell['id']} p={cell['p']} N={cell['N']}")
        for m_out in cell["Ms"]:
            floor = m_out["arms"]["floor(Mx/p)"]
            stdout.append(
                f"  M={m_out['M']} floor W_exact={floor['W_exact']:.8e} "
                f"W_jack={floor['W_jack']:.8e} bias={floor['bias']:.8e}"
            )
    (run_dir / "stdout.log").write_text("\n".join(stdout) + "\n")
    (run_dir / "stderr.log").write_text("")
    report = {
        "experiment_id": "EXP-ECDLP-5cad48",
        "run_id": "RUN-ECDLP-5cad48-S1",
        "stage": 1,
        "status": "valid",
        "certificate": {"kind": "none"},
        "SMALL_W_or_LARGE_W": False,
        "execution_authorized_stages": [0, 1],
        "stage2_authorized": False,
        "a98ea9_stage5_authorized": False,
        "raw_result_sha256": raw_hash,
        "git": _git_info(),
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    (exp_dir / "execution-report-stage1.yaml").write_text(
        "experiment_id: EXP-ECDLP-5cad48\n"
        "run_id: RUN-ECDLP-5cad48-S1\n"
        "stage: 1\n"
        "status: valid\n"
        "certificate:\n"
        "  kind: none\n"
        "SMALL_W_or_LARGE_W: false\n"
        "execution_authorized_stages: [0, 1]\n"
        "stage2_authorized: false\n"
        "a98ea9_stage5_authorized: false\n"
        f"raw_result_sha256: {raw_hash}\n"
        "not_a_W_decay_claim: true\n"
    )
    print("\n".join(stdout))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
