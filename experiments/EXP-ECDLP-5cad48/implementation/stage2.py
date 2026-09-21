#!/usr/bin/env python3
"""Stage 2 of EXP-ECDLP-5cad48: sampled-W eight-prime ladder.

Authorized package under DEC-20260907-ddfbce / v1_stage2_authorized.
H3 is not executed. Certificate kind none. No SMALL-W / LARGE-W.
No fit of a. No a98ea9 Stage 5.
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
    {"id": "S2-P523", "p": 523, "a": 2, "b": 6, "N": 523, "M_grid": (5, 8, 12)},
    {"id": "S2-P1033", "p": 1033, "a": 0, "b": 5, "N": 1087, "M_grid": (6, 10, 16)},
    {"id": "S2-P2063", "p": 2063, "a": 1, "b": 5, "N": 2129, "M_grid": (7, 13, 21)},
    {"id": "S2-P4111", "p": 4111, "a": 1, "b": 8, "N": 4177, "M_grid": (8, 16, 28)},
    {"id": "S2-P8219", "p": 8219, "a": 1, "b": 1, "N": 8117, "M_grid": (9, 20, 37)},
    {"id": "S2-P16417", "p": 16417, "a": 0, "b": 5, "N": 16447, "M_grid": (11, 25, 49)},
    {"id": "S2-P32779", "p": 32779, "a": 3, "b": 5, "N": 32909, "M_grid": (13, 32, 64)},
    {"id": "S2-P65539", "p": 65539, "a": 0, "b": 11, "N": 65287, "M_grid": (16, 40, 84)},
)
ARMS = (
    "floor(Mx/p)",
    "x mod M",
    "sha",
    "shuffle",
    "P2",
    "quadratic_character",
    "planted_theta",
)
N_PAIRS = 1_000_000
N_GROUPS = 20
SEED_BASE = 20260803
SHUFFLE_SEED = 20260803
PLANTED_SEED = 20260803


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


def whole_group_q(hv: np.ndarray, m: int) -> tuple[np.ndarray, np.ndarray, int]:
    hv, m = remap_labels(hv, m)
    q = np.bincount(hv, minlength=m).astype(np.float64) / float(len(hv))
    return hv, q, m


def plugin_w(hv: np.ndarray, m: int, n_group: int, pairs: np.ndarray, q: np.ndarray) -> dict:
    i = pairs[:, 0]
    j = pairs[:, 1]
    s = (hv[i] + hv[j]) % m
    c = hv[(i + j) % n_group]
    n = pairs.shape[0]
    hist = np.bincount(s * m + c, minlength=m * m).reshape(m, m).astype(np.float64)
    row = hist.sum(axis=1)
    deltas = np.empty(m, dtype=np.float64)
    pi_c = np.empty(m, dtype=np.float64)
    idx = np.arange(m)
    for d in range(m):
        deltas[d] = hist[idx, (idx + d) % m].sum() / n
    dstar = int(np.argmax(deltas))
    delta = float(deltas[dstar])
    if delta <= 0.0:
        raise RuntimeError("plug-in delta is 0")
    target_s = (idx - dstar) % m
    denom = row[target_s]
    pi_c = np.divide(hist[target_s, idx], denom, out=np.zeros(m), where=denom > 0)
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


def _legendre(x: int, p: int) -> int:
    if x % p == 0:
        return 0
    r = pow(x % p, (p - 1) // 2, p)
    return -1 if r == p - 1 else int(r)


def build_arms(xs: np.ndarray, p: int, n: int, m: int) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(SHUFFLE_SEED)
    floor_h = (xs * m) // p
    shuf = floor_h.copy()
    rng.shuffle(shuf)
    sha = np.array([_sha_label(int(v), m) for v in xs], dtype=np.int64)
    quad = np.zeros(n, dtype=np.int64)
    for i, x in enumerate(xs):
        if i == 0 or int(x) == 0:
            quad[i] = 0
        else:
            quad[i] = (_legendre(int(x), p) + 1) % m
    planted_rng = np.random.default_rng(PLANTED_SEED)
    theta = float(p) ** (-1.0 / 9.0)
    replace = planted_rng.random(n) < theta
    planted = sha.copy()
    planted[replace] = (np.arange(n, dtype=np.int64) % m)[replace]
    return {
        "floor(Mx/p)": floor_h.astype(np.int64),
        "x mod M": (xs % m).astype(np.int64),
        "sha": sha,
        "shuffle": shuf.astype(np.int64),
        "P2": ((np.arange(n, dtype=np.int64) * m) // n),
        "quadratic_character": quad,
        "planted_theta": planted,
    }


def main() -> int:
    t0 = time.time()
    exp_dir = Path(__file__).resolve().parents[1]
    run_dir = exp_dir / "runs" / "RUN-ECDLP-5cad48-S2"
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
                hv, q, meff = whole_group_q(arms[name], m)
                seed = SEED_BASE + 1000 * cell_index + 10 * arm_index + int(m)
                rng = np.random.default_rng(seed)
                pairs = rng.integers(0, n, size=(N_PAIRS, 2), dtype=np.int64)
                jack = jackknife_w(hv, meff, n, pairs, q)
                m_out["arms"][name] = {
                    "M_eff": int(meff),
                    "min_q": float(q.min()),
                    "W_plugin": jack["W_plugin"],
                    "W_jack": jack["W_jack"],
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
        "run_id": "RUN-ECDLP-5cad48-S2",
        "stage": 2,
        "authorized_by": "DEC-20260907-ddfbce",
        "executable_package": "sampled_W_ladder",
        "H3_executed": False,
        "H3_counts_unchanged": {"n_draws": 200, "n_pairs": 10000000},
        "certificate": {"kind": "none"},
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
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

    (run_dir / "manifest.yaml").write_text(
        "run:\n"
        "  id: RUN-ECDLP-5cad48-S2\n"
        "  experiment_id: EXP-ECDLP-5cad48\n"
        "  status: valid\n"
        "  certificate_kind: none\n"
        "  SMALL_W_or_LARGE_W: false\n"
        "  H3_executed: false\n"
        f"  raw_result_sha256: {raw_hash}\n"
    )
    (run_dir / "environment.json").write_text(
        json.dumps({"python": sys.version, "platform": platform.platform(), "numpy": np.__version__}, indent=2)
        + "\n"
    )
    (run_dir / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-5cad48/implementation/stage2.py\n"
    )
    stdout = [
        f"RUN-ECDLP-5cad48-S2 elapsed={elapsed:.3f}s raw_sha256={raw_hash}",
        "Sampled-W ladder only. H3 not executed. W unclassified.",
    ]
    for cell in cells_out:
        stdout.append(f"{cell['id']} p={cell['p']} N={cell['N']}")
        floor = cell["Ms"][0]["arms"]["floor(Mx/p)"]
        stdout.append(
            f"  M={cell['Ms'][0]['M']} floor W_plugin={floor['W_plugin']:.8e} "
            f"W_jack={floor['W_jack']:.8e}"
        )
    (run_dir / "stdout.log").write_text("\n".join(stdout) + "\n")
    (run_dir / "stderr.log").write_text("")
    (exp_dir / "execution-report-stage2.yaml").write_text(
        "experiment_id: EXP-ECDLP-5cad48\n"
        "run_id: RUN-ECDLP-5cad48-S2\n"
        "stage: 2\n"
        "status: valid\n"
        "certificate:\n"
        "  kind: none\n"
        "SMALL_W_or_LARGE_W: false\n"
        "execution_authorized_stages: [0, 1, 2]\n"
        "H3_executed: false\n"
        "fit_of_a: false\n"
        "a98ea9_stage5_authorized: false\n"
        f"raw_result_sha256: {raw_hash}\n"
        "not_a_W_decay_claim: true\n"
    )
    print("\n".join(stdout))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
