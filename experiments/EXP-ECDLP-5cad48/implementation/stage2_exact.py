#!/usr/bin/env python3
"""Stage 2 exact-G measurement of EXP-ECDLP-5cad48.

Authorized computation only under the later
v1_stage2_exact_g_authorized amendment. Records exact G,
M_delta, W, min_q, and cs_bound on the archived Stage 2
eight-prime table. Does not classify W. Does not fit a.
Certificate kind none. No a98ea9 Stage 5.
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
import yaml

REPO = Path(__file__).resolve().parents[3]
O2 = REPO / "analysis" / "o2-sum-compatible-filters"
sys.path.insert(0, str(O2))
from fourier_obstruction import dlog_table  # noqa: E402

EXP = REPO / "experiments" / "EXP-ECDLP-5cad48"
AUTH = EXP / "amendments" / "v1_stage2_exact_g_authorized.yaml"
S0_RAW = EXP / "runs" / "RUN-ECDLP-5cad48-S0" / "raw-result.json"
S1_RAW = EXP / "runs" / "RUN-ECDLP-5cad48-S1" / "raw-result.json"

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
SHARED_ARMS = ("floor(Mx/p)", "x mod M", "sha", "shuffle", "P2")
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


def refuse_unless_authorized() -> None:
    rec = yaml.safe_load(AUTH.read_text())
    block = rec.get("protocol_amendment", rec)
    if not block.get("exact_g_execution_authorized"):
        raise SystemExit("refuse: exact_g_execution_authorized is not true")
    if block.get("SMALL_W_or_LARGE_W"):
        raise SystemExit("refuse: authorization classified W")
    if block.get("fit_of_a"):
        raise SystemExit("refuse: authorization set fit_of_a true")
    if block.get("cs_bound_official_supported"):
        raise SystemExit("refuse: authorization set an official bound claim")


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
        "M_delta_exact": m * delta,
        "G_exact": g,
        "W_exact": w_rel,
        "min_q": min_q,
        "cs_bound_exact": 1.0 + (w_rel / max(min_q, 1e-18)) ** 0.5,
        "dstar_exact": dstar,
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


def _close(a: float, b: float) -> bool:
    return abs(float(a) - float(b)) <= 1e-12 * max(1.0, abs(float(b)))


def overlap_stage1(cells_out: list[dict]) -> dict:
    raw = json.loads(S1_RAW.read_text())
    by_id = {cell["id"]: cell for cell in raw["cells"]}
    pairs = (("S2-P523", "S1-P523"), ("S2-P1033", "S1-P1033"))
    rows = []
    holds = True
    for s2_id, s1_id in pairs:
        s2 = next(c for c in cells_out if c["id"] == s2_id)
        s1 = by_id[s1_id]
        s1_ms = {m_out["M"]: m_out for m_out in s1["Ms"]}
        for m_out in s2["Ms"]:
            m = m_out["M"]
            for name in SHARED_ARMS:
                left = m_out["arms"][name]
                right = s1_ms[m]["arms"][name]
                ok = all(
                    _close(left[k], right[k])
                    for k in ("G_exact", "M_delta_exact", "W_exact", "min_q", "cs_bound_exact")
                )
                holds = holds and ok
                rows.append({"s2": s2_id, "s1": s1_id, "M": m, "arm": name, "holds": ok})
    return {"holds": holds, "n_rows": len(rows), "rows": rows}


def overlap_stage0(cells_out: list[dict]) -> dict:
    raw = json.loads(S0_RAW.read_text())
    s2 = next(c for c in cells_out if c["id"] == "S2-P65539")
    m_out = next(x for x in s2["Ms"] if x["M"] == 40)
    field_map = {
        "G_exact": "G",
        "M_delta_exact": "M_delta",
        "W_exact": "W",
        "min_q": "min_q",
        "cs_bound_exact": "cs_bound",
    }
    rows = []
    holds = True
    for name in SHARED_ARMS:
        left = m_out["arms"][name]
        right = raw["arms"][name]
        ok = all(_close(left[lk], right[rk]) for lk, rk in field_map.items())
        holds = holds and ok
        rows.append({"s2": "S2-P65539", "s0": "RUN-ECDLP-5cad48-S0", "M": 40, "arm": name, "holds": ok})
    return {"holds": holds, "n_rows": len(rows), "rows": rows}


def main() -> int:
    t0 = time.time()
    refuse_unless_authorized()
    run_dir = EXP / "runs" / "RUN-ECDLP-5cad48-S2G"
    run_dir.mkdir(parents=True, exist_ok=True)

    cells_out = []
    n_rows = 0
    for cell in CELLS:
        p, a, b, n = cell["p"], cell["a"], cell["b"], cell["N"]
        _g0, pts = dlog_table(p, a, b, n)
        if len(pts) != n:
            raise RuntimeError(f"{cell['id']}: dlog table length {len(pts)} != {n}")
        xs = np.array([0 if pt is None else pt[0] for pt in pts], dtype=np.int64)
        cell_out = {"id": cell["id"], "p": p, "a": a, "b": b, "N": n, "Ms": []}
        for m in cell["M_grid"]:
            arms = build_arms(xs, p, n, m)
            m_out = {"M": int(m), "arms": {}}
            for name in ARMS:
                exact = bucket_stats(arms[name], m, n)
                exact["SMALL_W_or_LARGE_W"] = False
                m_out["arms"][name] = exact
                n_rows += 1
            cell_out["Ms"].append(m_out)
        cells_out.append(cell_out)

    if n_rows != 168:
        raise RuntimeError(f"expected 168 exact rows, got {n_rows}")
    ov1 = overlap_stage1(cells_out)
    ov0 = overlap_stage0(cells_out)
    if not ov1["holds"] or not ov0["holds"]:
        raise RuntimeError("overlap with archived Stage 0 or Stage 1 failed")

    elapsed = time.time() - t0
    git = _git_info()
    raw = {
        "experiment_id": "EXP-ECDLP-5cad48",
        "run_id": "RUN-ECDLP-5cad48-S2G",
        "stage": "2G",
        "authorized_by": "DEC-20260907-13e22e",
        "certificate": {"kind": "none"},
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "cs_bound_official_supported": False,
        "a98ea9_stage5_authorized": False,
        "n_exact_rows": n_rows,
        "overlap_stage1": ov1,
        "overlap_stage0": ov0,
        "overlap_holds": bool(ov1["holds"] and ov0["holds"]),
        "cells": cells_out,
        "elapsed_seconds": elapsed,
        "peak_rss_bytes": peak_rss_bytes(),
        "git": git,
        "not_a_W_decay_claim": True,
        "not_an_official_cs_bound": True,
    }
    raw_path = run_dir / "raw-result.json"
    raw_path.write_text(json.dumps(raw, indent=2) + "\n")
    raw_hash = hashlib.sha256(raw_path.read_bytes()).hexdigest()

    (run_dir / "manifest.yaml").write_text(
        "run:\n"
        "  id: RUN-ECDLP-5cad48-S2G\n"
        "  experiment_id: EXP-ECDLP-5cad48\n"
        "  status: valid\n"
        "  certificate_kind: none\n"
        "  SMALL_W_or_LARGE_W: false\n"
        "  fit_of_a: false\n"
        "  cs_bound_official_supported: false\n"
        f"  raw_result_sha256: {raw_hash}\n"
        f"  n_exact_rows: {n_rows}\n"
        f"  overlap_holds: {str(bool(ov1['holds'] and ov0['holds'])).lower()}\n"
        f"  code:\n"
        f"    path: experiments/EXP-ECDLP-5cad48/implementation/stage2_exact.py\n"
        f"    commit: {git['commit']}\n"
        f"    dirty: {str(git['dirty']).lower()}\n"
    )
    (run_dir / "environment.json").write_text(
        json.dumps({"python": sys.version, "platform": platform.platform(), "numpy": np.__version__}, indent=2)
        + "\n"
    )
    (run_dir / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-5cad48/implementation/stage2_exact.py\n"
    )
    stdout = [
        f"RUN-ECDLP-5cad48-S2G elapsed={elapsed:.3f}s raw_sha256={raw_hash}",
        f"n_exact_rows={n_rows} overlap_holds={ov1['holds'] and ov0['holds']}",
        "W recorded as observation only. Not SMALL-W or LARGE-W.",
    ]
    for cell in cells_out:
        stdout.append(f"{cell['id']} p={cell['p']} N={cell['N']}")
        for m_out in cell["Ms"]:
            p2 = m_out["arms"]["P2"]
            stdout.append(
                f"  M={m_out['M']} P2 G_exact={p2['G_exact']:.8e} "
                f"W_exact={p2['W_exact']:.8e}"
            )
    (run_dir / "stdout.log").write_text("\n".join(stdout) + "\n")
    (run_dir / "stderr.log").write_text("")
    (EXP / "execution-report-s2g.yaml").write_text(
        "experiment_id: EXP-ECDLP-5cad48\n"
        "run_id: RUN-ECDLP-5cad48-S2G\n"
        "stage: 2G\n"
        "status: valid\n"
        "certificate:\n"
        "  kind: none\n"
        "SMALL_W_or_LARGE_W: false\n"
        "fit_of_a: false\n"
        "cs_bound_official_supported: false\n"
        "a98ea9_stage5_authorized: false\n"
        f"n_exact_rows: {n_rows}\n"
        f"overlap_holds: {str(bool(ov1['holds'] and ov0['holds'])).lower()}\n"
        f"raw_result_sha256: {raw_hash}\n"
        "not_a_W_decay_claim: true\n"
        "not_an_official_cs_bound: true\n"
        f"git_commit: {git['commit']}\n"
        f"git_dirty: {str(git['dirty']).lower()}\n"
        f"recorded_at: {datetime.now(timezone.utc).isoformat()}\n"
    )
    print("\n".join(stdout))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
