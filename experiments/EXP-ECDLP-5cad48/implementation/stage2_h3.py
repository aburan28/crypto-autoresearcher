#!/usr/bin/env python3
"""H3 of EXP-ECDLP-5cad48: 200 draws of n=1e7 versus exact W.

Authorized package under DEC-20260907-0fc640 / v1_stage2_h3_authorized.
Locked counts 200 and 1e7 are not reduced. Certificate kind none.
No SMALL-W / LARGE-W. No fit of a. No a98ea9 Stage 5.
"""
from __future__ import annotations

import hashlib
import json
import platform
import resource
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
O2 = REPO / "analysis" / "o2-sum-compatible-filters"
sys.path.insert(0, str(O2))
from fourier_obstruction import dlog_table  # noqa: E402

CELLS = (
    {"id": "S2-P523", "s1_id": "S1-P523", "p": 523, "a": 2, "b": 6, "N": 523, "M_grid": (5, 8, 12)},
    {"id": "S2-P1033", "s1_id": "S1-P1033", "p": 1033, "a": 0, "b": 5, "N": 1087, "M_grid": (6, 10, 16)},
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
STAGE1_REUSE = frozenset(
    {"floor(Mx/p)", "x mod M", "sha", "shuffle", "P2"}
)
N_PAIRS = 10_000_000
N_DRAWS = 200
N_GROUPS = 20
SEED_BASE = 20260803
SHUFFLE_SEED = 20260803
PLANTED_SEED = 20260803
S1_RAW = REPO / "experiments" / "EXP-ECDLP-5cad48" / "runs" / "RUN-ECDLP-5cad48-S1" / "raw-result.json"


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


def exact_w(hv: np.ndarray, m: int, n: int) -> dict:
    hv, m = remap_labels(hv, m)
    ind = np.zeros((m, n))
    for bucket in range(m):
        ind[bucket] = hv == bucket
    counts = ind.sum(axis=1)
    fourier = np.fft.rfft(ind, axis=1)
    fourier_s = np.fft.fft(fourier, axis=0)
    w_s = np.fft.ifft(fourier_s * fourier_s, axis=0)
    w = np.fft.irfft(w_s, n=n, axis=1).real
    num = np.stack([w[:, hv == c].sum(axis=1) for c in range(m)], axis=1)
    den = np.real(np.fft.ifft(np.fft.fft(counts) ** 2))
    pi = num / np.maximum(den[:, None], 1e-12)
    tot = float(n) ** 2
    deltas = [sum(num[(c - d) % m, c] for c in range(m)) / tot for d in range(m)]
    dstar = int(np.argmax(deltas))
    delta = float(deltas[dstar])
    q = counts / n
    pi_c = pi[(np.arange(m) - dstar) % m, np.arange(m)]
    w_rel = float(np.sum(q * (pi_c / delta - 1.0) ** 2))
    return {"M_eff": int(m), "W": w_rel, "dstar": dstar, "M_delta": m * delta}


def w_from_hist(hist: np.ndarray, q: np.ndarray, n: int) -> dict:
    m = hist.shape[0]
    row = hist.sum(axis=1)
    deltas = np.empty(m, dtype=np.float64)
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
    return {"W": w_rel, "dstar": dstar, "M_delta": m * delta}


def pair_hist(hv: np.ndarray, m: int, n_group: int, pairs: np.ndarray) -> np.ndarray:
    i = pairs[:, 0]
    j = pairs[:, 1]
    s = (hv[i] + hv[j]) % m
    c = hv[(i + j) % n_group]
    return np.bincount(s * m + c, minlength=m * m).reshape(m, m).astype(np.float64)


def jackknife_from_groups(group_hists: list[np.ndarray], q: np.ndarray, n_pairs: int) -> dict:
    full = np.sum(group_hists, axis=0)
    t_all = w_from_hist(full, q, n_pairs)
    n_g = len(group_hists)
    leave_n = n_pairs - (n_pairs // n_g)
    t_g = [w_from_hist(full - h, q, leave_n)["W"] for h in group_hists]
    mean_leave = float(np.mean(t_g))
    w_jack = n_g * t_all["W"] - (n_g - 1) * mean_leave
    return {
        "W_plugin": t_all["W"],
        "W_jack": w_jack,
        "dstar_plugin": t_all["dstar"],
        "M_delta_plugin": t_all["M_delta"],
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


def load_stage1_exact() -> dict:
    raw = json.loads(S1_RAW.read_text())
    out = {}
    for cell in raw["cells"]:
        for mrow in cell["Ms"]:
            for arm, rec in mrow["arms"].items():
                out[(cell["id"], int(mrow["M"]), arm)] = float(rec["W_exact"])
    return out


def main() -> int:
    t0 = time.time()
    exp_dir = Path(__file__).resolve().parents[1]
    run_dir = exp_dir / "runs" / "RUN-ECDLP-5cad48-S2H3"
    run_dir.mkdir(parents=True, exist_ok=True)
    s1_exact = load_stage1_exact()

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
                if name in STAGE1_REUSE:
                    w_exact = s1_exact[(cell["s1_id"], int(m), name)]
                    exact_source = "stage1_reuse"
                else:
                    w_exact = exact_w(hv, meff, n)["W"]
                    exact_source = "computed_once_stage0_fft"
                draws = []
                for draw in range(N_DRAWS):
                    seed = (
                        SEED_BASE
                        + 100000 * cell_index
                        + 1000 * arm_index
                        + 100 * int(m)
                        + draw
                    )
                    rng = np.random.default_rng(seed)
                    pairs = rng.integers(0, n, size=(N_PAIRS, 2), dtype=np.int64)
                    folds = np.array_split(np.arange(N_PAIRS), N_GROUPS)
                    group_hists = [pair_hist(hv, meff, n, pairs[leave]) for leave in folds]
                    jack = jackknife_from_groups(group_hists, q, N_PAIRS)
                    draws.append(
                        {
                            "draw": draw,
                            "seed": seed,
                            "W_plugin": jack["W_plugin"],
                            "W_jack": jack["W_jack"],
                            "bias_plugin": jack["W_plugin"] - w_exact,
                            "bias_jack": jack["W_jack"] - w_exact,
                            "dstar_plugin": jack["dstar_plugin"],
                            "SMALL_W_or_LARGE_W": False,
                        }
                    )
                bias_jack = np.array([d["bias_jack"] for d in draws], dtype=np.float64)
                m_out["arms"][name] = {
                    "M_eff": int(meff),
                    "W_exact": w_exact,
                    "exact_W_source": exact_source,
                    "n_draws": N_DRAWS,
                    "n_pairs": N_PAIRS,
                    "n_groups": N_GROUPS,
                    "mean_bias_jack": float(bias_jack.mean()),
                    "se_bias_jack": float(bias_jack.std(ddof=1) / np.sqrt(N_DRAWS)),
                    "draws": draws,
                    "SMALL_W_or_LARGE_W": False,
                }
            cell_out["Ms"].append(m_out)
        cells_out.append(cell_out)

    elapsed = time.time() - t0
    raw = {
        "experiment_id": "EXP-ECDLP-5cad48",
        "run_id": "RUN-ECDLP-5cad48-S2H3",
        "stage": 2,
        "package": "H3_200_draw_n_1e7",
        "authorized_by": "DEC-20260907-0fc640",
        "H3_executed": True,
        "H3_counts_unchanged": {"n_draws": N_DRAWS, "n_pairs": N_PAIRS},
        "certificate": {"kind": "none"},
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "a98ea9_stage5_authorized": False,
        "n_pairs": N_PAIRS,
        "n_draws": N_DRAWS,
        "n_groups": N_GROUPS,
        "seed_base": SEED_BASE,
        "q_c_source": "whole-group label vector",
        "cells": cells_out,
        "elapsed_seconds": elapsed,
        "peak_rss_bytes": peak_rss_bytes(),
        "git": _git_info(),
        "not_a_W_decay_claim": True,
    }
    raw_path = run_dir / "raw-result.json"
    raw_path.write_text(json.dumps(raw, indent=2) + "\n")
    raw_hash = hashlib.sha256(raw_path.read_bytes()).hexdigest()

    (run_dir / "manifest.yaml").write_text(
        "run:\n"
        "  id: RUN-ECDLP-5cad48-S2H3\n"
        "  experiment_id: EXP-ECDLP-5cad48\n"
        "  status: valid\n"
        "  certificate_kind: none\n"
        "  SMALL_W_or_LARGE_W: false\n"
        "  H3_executed: true\n"
        "  n_draws: 200\n"
        "  n_pairs: 10000000\n"
        f"  raw_result_sha256: {raw_hash}\n"
    )
    (run_dir / "environment.json").write_text(
        json.dumps({"python": sys.version, "platform": platform.platform(), "numpy": np.__version__}, indent=2)
        + "\n"
    )
    (run_dir / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-5cad48/implementation/stage2_h3.py\n"
    )
    stdout = [
        f"RUN-ECDLP-5cad48-S2H3 elapsed={elapsed:.3f}s raw_sha256={raw_hash}",
        "H3 200 x 1e7. Counts unchanged. W unclassified.",
    ]
    for cell in cells_out:
        stdout.append(f"{cell['id']} p={cell['p']} N={cell['N']}")
        floor = cell["Ms"][0]["arms"]["floor(Mx/p)"]
        stdout.append(
            f"  M={cell['Ms'][0]['M']} floor mean_bias_jack recorded; "
            f"n_draws={floor['n_draws']}"
        )
    (run_dir / "stdout.log").write_text("\n".join(stdout) + "\n")
    (run_dir / "stderr.log").write_text("")
    (exp_dir / "execution-report-h3.yaml").write_text(
        "experiment_id: EXP-ECDLP-5cad48\n"
        "run_id: RUN-ECDLP-5cad48-S2H3\n"
        "stage: 2\n"
        "package: H3_200_draw_n_1e7\n"
        "status: valid\n"
        "certificate:\n"
        "  kind: none\n"
        "SMALL_W_or_LARGE_W: false\n"
        "H3_executed: true\n"
        "H3_n_draws: 200\n"
        "H3_n_pairs: 10000000\n"
        "fit_of_a: false\n"
        "a98ea9_stage5_authorized: false\n"
        f"raw_result_sha256: {raw_hash}\n"
        "not_a_W_decay_claim: true\n"
    )
    print("\n".join(stdout))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
