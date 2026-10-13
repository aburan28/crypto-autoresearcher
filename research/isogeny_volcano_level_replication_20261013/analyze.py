#!/usr/bin/env python3
"""Fail-closed level analysis for the independent m=37/m=41 rho replication."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import re
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
FIELDS = ("run", "ops", "walks", "cycles", "abandoned", "useless", "ok", "sec")
NAME_RE = re.compile(r"c([0-9]+)_m([01])_r([0-9]+)\.csv")
BOOTSTRAP_REPS = 50_000
INNER_RESAMPLES = 4_096
BOOTSTRAP_SEED = 20261013
MAX_BOOTSTRAP_CELLS = 2_000_000
SHUFFLE_SEED = 2026101317
CFG = {
    "m37": {
        "m": 37,
        "ell": 230603167,
        "levels": ("crater", "floor73", "floor2663", "bottom"),
        "setup": 155.0,
        "factors": ("73", "2663"),
        "grid": {(0, 0): "crater", (1, 0): "floor73", (0, 1): "floor2663", (1, 1): "bottom"},
        "sample": ROOT / "research/isogeny_volcano_rho_20261005/sample.csv",
        "source": ROOT / "research/isogeny_volcano_rho_20261005/rho.c",
        "source_sha256": "7c8195ae671124f057ab913bb10e98f7a75c5c5e16cbbac3f67b5fd87a20b106",
        "sample_sha256": "994caf2b456058c8fee9dc87f6289d7a07a22a0c07b03e64bbfb015797f7d4cd",
        "params": None,
        "params_sha256": None,
        "seed_base": 37_000_000_000,
        "level_counts": {"crater": 1, "floor73": 74, "floor2663": 22, "bottom": 30},
        "archive": ROOT / "research/isogeny_volcano_rho_20261005/results.json",
        "chunks_lower": 2,
        "chunks_crater": 10,
        "rows": 500,
    },
    "m41": {
        "m": 41,
        "ell": 549756390943,
        "levels": ("crater", "floor409", "floor1721", "bottom"),
        "setup": 167.0,
        "factors": ("409", "1721"),
        "grid": {(0, 0): "crater", (1, 0): "floor409", (0, 1): "floor1721", (1, 1): "bottom"},
        "sample": ROOT / "research/isogeny_volcano_rho_m41_20261006/sample.csv",
        "source": ROOT / "research/isogeny_volcano_rho_m41_20261006/rho.c",
        "source_sha256": "212cd0aebf36e9095b42677a02286c85834763d9b37028b49529020de5cec90f",
        "sample_sha256": "37931f3e0417f1fe0f25965aa18e858e29f6fdc028cff4ae3bccf5d47fd564dc",
        "params": ROOT / "research/isogeny_volcano_rho_m41_20261006/params.h",
        "params_sha256": "89c1c89ef929d8758ad43cebe98553091ed9bbb358a8fbe9aca721865cd58ec3",
        "seed_base": 41_000_000_000,
        "level_counts": {"crater": 1, "floor409": 30, "floor1721": 30, "bottom": 30},
        "archive": ROOT / "research/isogeny_volcano_rho_m41_20261006/results.json",
        "chunks_lower": 1,
        "chunks_crater": 15,
        "rows": 200,
    },
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def raw_tree_sha256(raw: Path, files: list[Path]) -> str:
    h = hashlib.sha256()
    for path in sorted(files):
        h.update(path.relative_to(raw).as_posix().encode())
        h.update(b"\0")
        h.update(bytes.fromhex(sha256(path)))
    return h.hexdigest()


def read_sample(path: Path, cfg: dict) -> list[dict[str, str]]:
    if sha256(path) != cfg["sample_sha256"]:
        raise ValueError(f"{path}: sample hash does not match the frozen protocol")
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        if tuple(reader.fieldnames or ()) != ("id", "level", "b"):
            raise ValueError(f"{path}: expected header id,level,b")
        rows = list(reader)
    ids = [r["id"] for r in rows]
    if not rows or len(ids) != len(set(ids)) or any(not x.isdigit() for x in ids):
        raise ValueError(f"{path}: empty, duplicate, or nonnumeric curve id")
    if any(r["level"] not in cfg["levels"] or not r["b"].isdigit() for r in rows):
        raise ValueError(f"{path}: invalid level or b")
    crater = [r for r in rows if r["level"] == "crater"]
    if len(crater) != 1 or crater[0]["id"] != "0":
        raise ValueError(f"{path}: expected the sole crater to have id 0")
    if any(not any(r["level"] == lev for r in rows) for lev in cfg["levels"]):
        raise ValueError(f"{path}: one or more configured levels are absent")
    counts = {lev: sum(r["level"] == lev for r in rows) for lev in cfg["levels"]}
    if counts != cfg["level_counts"]:
        raise ValueError(f"{path}: frozen level-count mismatch: {counts}")
    return rows


def expected_files(sample: list[dict[str, str]], cfg: dict) -> dict[str, int]:
    out: dict[str, int] = {}
    for curve in sample:
        crater = curve["level"] == "crater"
        for mode in ((0, 1) if crater else (0,)):
            chunks = cfg["chunks_crater"] if crater else cfg["chunks_lower"]
            for chunk in range(chunks):
                out[f"c{curve['id']}_m{mode}_r{chunk}.csv"] = cfg["rows"]
    return out


def load_study(raw: Path, sample: list[dict[str, str]], cfg: dict):
    expected = expected_files(sample, cfg)
    if not raw.is_dir():
        raise ValueError(f"{raw}: raw directory is missing")
    entries = sorted(raw.iterdir())
    if any(not p.is_file() for p in entries):
        raise ValueError(f"{raw}: raw directory contains a non-file entry")
    actual = [p for p in entries if p.suffix == ".csv"]
    actual_names = {p.name for p in actual}
    if len(actual) != len(entries) or actual_names != set(expected):
        missing = sorted(set(expected) - actual_names)
        extra = sorted({p.name for p in entries} - set(expected))
        raise ValueError(f"{raw}: file-set mismatch; missing={missing[:8]} extra={extra[:8]}")
    data: dict[tuple[str, int], dict[str, list[float]]] = {}
    chunks: dict[tuple[str, int], dict[int, dict[str, np.ndarray]]] = {}
    seen_keys: set[tuple[str, int, int, int]] = set()
    for path in actual:
        match = NAME_RE.fullmatch(path.name)
        if not match:
            raise ValueError(f"{path}: invalid filename")
        cid, mode, chunk = match.group(1), int(match.group(2)), int(match.group(3))
        bucket = data.setdefault(
            (cid, mode),
            {name: [] for name in ("ops", "walks", "cycles", "abandoned", "useless", "sec")},
        )
        chunk_values = {name: [] for name in ("ops", "walks", "cycles", "abandoned", "useless", "sec")}
        with path.open(newline="") as f:
            reader = csv.DictReader(f)
            if tuple(reader.fieldnames or ()) != FIELDS:
                raise ValueError(f"{path}: schema mismatch")
            rows = list(reader)
        want = expected[path.name]
        if len(rows) != want:
            raise ValueError(f"{path}: expected {want} rows, found {len(rows)}")
        runs: set[int] = set()
        for row in rows:
            try:
                run = int(row["run"])
                ops = int(row["ops"])
                sec = float(row["sec"])
                counts = [int(row[x]) for x in FIELDS[2:6]]
                ok = int(row["ok"])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{path}: nonnumeric row") from exc
            key = (cid, mode, chunk, run)
            if key in seen_keys or run in runs:
                raise ValueError(f"{path}: duplicate run {run}")
            seen_keys.add(key)
            runs.add(run)
            if ok != 1 or ops <= cfg["setup"] or not math.isfinite(sec) or sec <= 0 or any(x < 0 for x in counts):
                raise ValueError(f"{path}: unverified or invalid row {run}")
            bucket["ops"].append(float(ops))
            chunk_values["ops"].append(float(ops))
            for name, value in zip(FIELDS[2:6], counts):
                bucket[name].append(float(value))
                chunk_values[name].append(float(value))
            bucket["sec"].append(sec)
            chunk_values["sec"].append(sec)
        if runs != set(range(want)):
            raise ValueError(f"{path}: run ids are not exactly 0..{want - 1}")
        key = (cid, mode)
        if chunk in chunks.setdefault(key, {}):
            raise ValueError(f"{path}: duplicate chunk id")
        chunks[key][chunk] = {name: np.asarray(values, dtype=float) for name, values in chunk_values.items()}
    arrays = {k: {m: np.asarray(v, dtype=float) for m, v in vals.items()} for k, vals in data.items()}
    return arrays, chunks, actual


def curve_arrays(sample, data, level: str, mode: int, metric: str) -> list[np.ndarray]:
    return [data[(r["id"], mode)][metric] for r in sample if r["level"] == level]


def curve_chunk_arrays(sample, chunks, level: str, mode: int, metric: str) -> list[list[np.ndarray]]:
    out = []
    for row in sample:
        if row["level"] != level:
            continue
        by_chunk = chunks[(row["id"], mode)]
        out.append([by_chunk[k][metric] for k in sorted(by_chunk)])
    return out


def sample_means(values: np.ndarray, reps: int, rng: np.random.Generator, max_cells: int) -> np.ndarray:
    out = np.empty(reps)
    block = max(1, min(reps, max_cells // len(values)))
    for start in range(0, reps, block):
        stop = min(reps, start + block)
        idx = rng.integers(0, len(values), size=(stop - start, len(values)), dtype=np.int32)
        out[start:stop] = values[idx].mean(axis=1)
    return out


def aggregate_reservoirs(units: np.ndarray, reps: int, rng, max_cells: int) -> np.ndarray:
    """Resample unit rows, drawing one empirical mean from each selected row."""
    if units.ndim != 2 or not len(units) or not units.shape[1]:
        raise ValueError("empty bootstrap reservoir")
    out = np.empty(reps)
    block = max(1, min(reps, max_cells // len(units)))
    for start in range(0, reps, block):
        stop = min(reps, start + block)
        shape = (stop - start, len(units))
        ui = rng.integers(0, len(units), size=shape, dtype=np.int32)
        ri = rng.integers(0, units.shape[1], size=shape, dtype=np.int32)
        out[start:stop] = units[ui, ri].mean(axis=1)
    return out


def chunk_aware_means(curves: list[list[np.ndarray]], reps: int, inner: int, rng, max_cells: int) -> np.ndarray:
    """Empirical curve -> process-chunk -> solve bootstrap (chunk -> solve for crater)."""
    curve_reservoirs = []
    for chunks in curves:
        chunk_reservoirs = np.vstack([sample_means(values, inner, rng, max_cells) for values in chunks])
        curve_reservoirs.append(aggregate_reservoirs(chunk_reservoirs, inner, rng, max_cells))
    reservoirs = np.vstack(curve_reservoirs)
    if len(curves) == 1:
        # There is no curve-sampling layer for the sole crater; its reservoir
        # already resamples process chunks and then solves within each chunk.
        return rng.choice(reservoirs[0], size=reps, replace=True)
    return aggregate_reservoirs(reservoirs, reps, rng, max_cells)


def interval(x: np.ndarray, alpha: float) -> list[float]:
    return [float(np.quantile(x, alpha / 2)), float(np.quantile(x, 1 - alpha / 2))]


def describe(
    study: str,
    arm: str,
    level: str,
    mode: int,
    curves: list[np.ndarray],
    secs: list[np.ndarray],
    setup: float,
    ell: int,
    diagnostics: dict[str, list[np.ndarray]],
):
    flat = np.concatenate(curves)
    time = np.concatenate(secs)
    adj = flat - setup
    q = np.quantile(flat, [.05, .25, .5, .75, .90, .95, .99])
    aq = np.quantile(adj, [.05, .25, .5, .75, .90, .95, .99])
    curve_means = np.asarray([x.mean() for x in curves])
    diag_flat = {name: np.concatenate(parts) for name, parts in diagnostics.items()}
    total_walks = float(diag_flat["walks"].sum())
    total_ops = float(flat.sum())
    return {
        "study": study, "arm": arm, "level": level, "mode": mode,
        "n_curves": len(curves), "n_solves": len(flat),
        "solves_per_curve_min": min(map(len, curves)), "solves_per_curve_max": max(map(len, curves)),
        "mean_ops": float(curve_means.mean()), "sd_ops": float(flat.std(ddof=1)),
        "cv_ops": float(flat.std(ddof=1) / flat.mean()),
        "q05_ops": float(q[0]), "q25_ops": float(q[1]), "median_ops": float(q[2]), "q75_ops": float(q[3]),
        "q90_ops": float(q[4]), "q95_ops": float(q[5]), "q99_ops": float(q[6]),
        "mean_ops_over_sqrt_r": float(curve_means.mean() / math.sqrt(ell)),
        "between_curve_sd_of_mean_ops": float(curve_means.std(ddof=1)) if len(curve_means) > 1 else 0.0,
        "min_curve_mean_ops": float(curve_means.min()), "max_curve_mean_ops": float(curve_means.max()),
        "setup_ops_subtracted": setup, "mean_ops_ex_setup": float(np.mean([x.mean() - setup for x in curves])),
        "sd_ops_ex_setup": float(adj.std(ddof=1)), "cv_ops_ex_setup": float(adj.std(ddof=1) / adj.mean()),
        "q05_ops_ex_setup": float(aq[0]), "q25_ops_ex_setup": float(aq[1]), "median_ops_ex_setup": float(aq[2]),
        "q75_ops_ex_setup": float(aq[3]), "q90_ops_ex_setup": float(aq[4]), "q95_ops_ex_setup": float(aq[5]),
        "q99_ops_ex_setup": float(aq[6]),
        "mean_walk_starts": float(diag_flat["walks"].mean()),
        "mean_short_cycles": float(diag_flat["cycles"].mean()),
        "mean_local_cap_restarts": float(diag_flat["abandoned"].mean()),
        "mean_useless_collisions": float(diag_flat["useless"].mean()),
        "cycles_per_1000_walks": float(1000 * diag_flat["cycles"].sum() / total_walks),
        "local_cap_restarts_per_1000_walks": float(1000 * diag_flat["abandoned"].sum() / total_walks),
        "useless_collisions_per_1000_walks": float(1000 * diag_flat["useless"].sum() / total_walks),
        "mean_sec_descriptive": float(time.mean()), "sd_sec_descriptive": float(time.std(ddof=1)),
        "aggregate_ns_per_counted_op_descriptive": float(1e9 * time.sum() / total_ops),
    }


CONTRAST_FIELDS = (
    "study", "kind", "metric", "numerator", "denominator", "factor", "context",
    "ratio", "log2_ratio", "pointwise95_ratio_lo", "pointwise95_ratio_hi",
    "pointwise95_bits_lo", "pointwise95_bits_hi", "simultaneous95_ratio_lo",
    "simultaneous95_ratio_hi", "simultaneous95_bits_lo", "simultaneous95_bits_hi",
    "simultaneous90_ratio_lo", "simultaneous90_ratio_hi", "equivalent_within_3pct_simultaneous90",
)


def contrast(study, kind, metric, num_name, den_name, num, den, bnum, bden, *, factor="", context="", family=0, setup=0.0):
    n, d = num - setup, den - setup
    bn, bd = bnum - setup, bden - setup
    if min(n, d, float(bn.min()), float(bd.min())) <= 0:
        raise ValueError("nonpositive mean in ratio contrast")
    br = bn / bd
    bb = np.log2(br)
    p95r, p95b = interval(br, .05), interval(bb, .05)
    row = {k: "" for k in CONTRAST_FIELDS}
    row.update(study=study, kind=kind, metric=metric, numerator=num_name, denominator=den_name,
               factor=factor, context=context, ratio=float(n / d), log2_ratio=float(math.log2(n / d)),
               pointwise95_ratio_lo=p95r[0], pointwise95_ratio_hi=p95r[1],
               pointwise95_bits_lo=p95b[0], pointwise95_bits_hi=p95b[1])
    if family:
        s95r, s95b = interval(br, .05 / family), interval(bb, .05 / family)
        s90r = interval(br, .10 / family)
        row.update(simultaneous95_ratio_lo=s95r[0], simultaneous95_ratio_hi=s95r[1],
                   simultaneous95_bits_lo=s95b[0], simultaneous95_bits_hi=s95b[1],
                   simultaneous90_ratio_lo=s90r[0], simultaneous90_ratio_hi=s90r[1],
                   equivalent_within_3pct_simultaneous90=bool(s90r[0] > .97 and s90r[1] < 1.03))
    return row


def interaction(study, names, means, boots):
    crater, a, b, bottom = (names[x] for x in ((0, 0), (1, 0), (0, 1), (1, 1)))
    ratio = means[bottom] * means[crater] / (means[a] * means[b])
    br = boots[bottom] * boots[crater] / (boots[a] * boots[b])
    pr, pb = interval(br, .05), interval(np.log2(br), .05)
    row = {k: "" for k in CONTRAST_FIELDS}
    row.update(study=study, kind="vertical_interaction", metric="ops", numerator=f"{bottom}*{crater}",
               denominator=f"{a}*{b}", factor="factor1_x_factor2", context="native negation-only arms",
               ratio=float(ratio), log2_ratio=float(math.log2(ratio)), pointwise95_ratio_lo=pr[0],
               pointwise95_ratio_hi=pr[1], pointwise95_bits_lo=pb[0], pointwise95_bits_hi=pb[1])
    return row


def load_archive(path: Path, cfg: dict):
    obj = json.loads(path.read_text())
    if not obj.get("validity", {}).get("all_verified"):
        raise ValueError(f"{path}: archived comparison is not verified")
    means = obj["H2_level_effect_negation_only"]["ops"]["level_means"]
    tau = obj["H1_any_curve_faster_than_crater_with_frobenius"]["ops"]["level_ratio_vs_crater_tau"]
    crater = means["crater"]
    return {
        "source": str(path.relative_to(ROOT)), "sha256": sha256(path), "pooled": False,
        "vs_crater_neg": {lev: {"ratio": float(means[lev] / crater), "log2_ratio": float(math.log2(means[lev] / crater))}
                           for lev in cfg["levels"][1:]},
        "vs_crater_tau": {lev: {"ratio": float(tau[lev][0]), "log2_ratio": float(math.log2(tau[lev][0]))}
                           for lev in cfg["levels"]},
    }


def load_json(path: Path):
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: missing or invalid JSON") from exc


def expected_job_records(study: str, sample: list[dict[str, str]], cfg: dict) -> list[dict]:
    jobs = []
    for curve in sample:
        crater = curve["level"] == "crater"
        modes = (0, 1) if crater else (0,)
        chunks = cfg["chunks_crater"] if crater else cfg["chunks_lower"]
        for mode in modes:
            for chunk in range(chunks):
                seed = cfg["seed_base"] + 10_000 * int(curve["id"]) + 1_000 * mode + chunk
                jobs.append({
                    "study": study, "curve_id": curve["id"], "level": curve["level"], "b": curve["b"],
                    "mode": mode, "chunk": chunk, "rows": cfg["rows"], "seed": seed,
                    "filename": f"c{curve['id']}_m{mode}_r{chunk}.csv",
                })
    return jobs


def validate_run_metadata(run_root: Path, samples: dict[str, list[dict[str, str]]]) -> dict:
    expected_jobs = [job for study, cfg in CFG.items() for job in expected_job_records(study, samples[study], cfg)]
    expected_by_key = {(j["study"], j["filename"]): j for j in expected_jobs}
    expected_solves = sum(j["rows"] for j in expected_jobs)
    if len(expected_by_key) != len(expected_jobs):
        raise ValueError("internal duplicate expected job")

    session = load_json(run_root / "session.json")
    required_session = {
        "status": "complete", "studies": ["m37", "m41"], "jobs": len(expected_jobs),
        "expected_solves": expected_solves, "completed_jobs": len(expected_jobs),
    }
    for key, value in required_session.items():
        if session.get(key) != value:
            raise ValueError(f"session.json: {key}={session.get(key)!r}, expected {value!r}")
    if session.get("error") is not None or not session.get("started_utc") or not session.get("finished_utc"):
        raise ValueError("session.json: error or missing timestamps")

    plan = load_json(run_root / "plan.json")
    if plan.get("shuffle_seed") != SHUFFLE_SEED or plan.get("workers") != 4 or plan.get("cores") != [0, 1, 2, 3]:
        raise ValueError("plan.json: frozen scheduling parameters do not match")
    if plan.get("expected_solves") != expected_solves or not isinstance(plan.get("created_utc"), str):
        raise ValueError("plan.json: solve count or timestamp mismatch")
    actual_plan = plan.get("jobs")
    if not isinstance(actual_plan, list) or len(actual_plan) != len(expected_jobs):
        raise ValueError("plan.json: job count mismatch")
    scheduled_jobs = list(expected_jobs)
    random.Random(SHUFFLE_SEED).shuffle(scheduled_jobs)
    if actual_plan != scheduled_jobs:
        raise ValueError("plan.json: exact frozen job plan mismatch")
    expected_core = {(job["study"], job["filename"]): [0, 1, 2, 3][i % 4]
                     for i, job in enumerate(scheduled_jobs)}

    build = load_json(run_root / "build-provenance.json")
    git = build.get("git", {})
    if not re.fullmatch(r"[0-9a-f]{40}", git.get("commit", "")) or git.get("status_porcelain") != "":
        raise ValueError("build-provenance.json: producer commit missing or worktree was dirty")
    builds = build.get("builds")
    if not isinstance(builds, list) or {x.get("study") for x in builds} != set(CFG):
        raise ValueError("build-provenance.json: expected exactly both study builds")
    for receipt in builds:
        study = receipt["study"]
        cfg = CFG[study]
        if receipt.get("source_sha256") != cfg["source_sha256"] or receipt.get("sample_sha256") != cfg["sample_sha256"]:
            raise ValueError(f"build-provenance.json: {study} source/sample mismatch")
        if receipt.get("params_sha256") != cfg["params_sha256"]:
            raise ValueError(f"build-provenance.json: {study} params mismatch")
        binary = Path(receipt.get("binary", ""))
        if not binary.is_file() or sha256(binary) != receipt.get("binary_sha256"):
            raise ValueError(f"build-provenance.json: {study} binary missing or changed")

    receipt_path = run_root / "jobs.jsonl"
    try:
        receipts = [json.loads(line) for line in receipt_path.read_text().splitlines() if line.strip()]
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{receipt_path}: missing or invalid receipts") from exc
    if len(receipts) != len(expected_jobs):
        raise ValueError(f"{receipt_path}: expected {len(expected_jobs)} receipts, found {len(receipts)}")
    seen = set()
    for receipt in receipts:
        job = receipt.get("job", {})
        filename = f"c{job.get('curve_id')}_m{job.get('mode')}_r{job.get('chunk')}.csv"
        key = (job.get("study"), filename)
        if key in seen or key not in expected_by_key:
            raise ValueError(f"{receipt_path}: duplicate or unexpected receipt {key}")
        seen.add(key)
        expected = expected_by_key[key]
        if job != {k: v for k, v in expected.items() if k != "filename"} or receipt.get("status") != "completed":
            raise ValueError(f"{receipt_path}: job or status mismatch for {key}")
        validation = receipt.get("validation", {})
        if validation != {"rows": expected["rows"], "verified": expected["rows"]}:
            raise ValueError(f"{receipt_path}: validation mismatch for {key}")
        raw = run_root / expected["study"] / "raw" / expected["filename"]
        if not raw.is_file() or receipt.get("sha256") != sha256(raw):
            raise ValueError(f"{receipt_path}: raw hash mismatch for {key}")
        if Path(receipt.get("output", "")).resolve() != raw.resolve():
            raise ValueError(f"{receipt_path}: output path mismatch for {key}")
        if receipt.get("core") != expected_core[key] or not receipt.get("started_utc") or not receipt.get("finished_utc"):
            raise ValueError(f"{receipt_path}: scheduling/timestamp mismatch for {key}")
        command = receipt.get("command")
        partial = raw.with_suffix(raw.suffix + ".partial")
        if not isinstance(command, list) or len(command) != 11:
            raise ValueError(f"{receipt_path}: command shape mismatch for {key}")
        if command[:3] != ["taskset", "-c", str(expected_core[key])] or command[4:10] != [
            "run", expected["b"], "0", str(expected["mode"]), str(expected["rows"]), str(expected["seed"])
        ]:
            raise ValueError(f"{receipt_path}: command arguments mismatch for {key}")
        if Path(command[3]).resolve() != (run_root / expected["study"] / "build" / "rho").resolve():
            raise ValueError(f"{receipt_path}: binary command path mismatch for {key}")
        if Path(command[10]).resolve() != partial.resolve():
            raise ValueError(f"{receipt_path}: partial output command path mismatch for {key}")
    if seen != set(expected_by_key):
        raise ValueError(f"{receipt_path}: incomplete receipt key set")
    if not (run_root / "host.json").is_file() or not (run_root / "run-command.txt").is_file():
        raise ValueError("run host or command provenance is missing")
    return {
        "producer_commit": git["commit"], "worktree_clean_before_build": True,
        "plan_sha256": sha256(run_root / "plan.json"), "receipts_sha256": sha256(receipt_path),
        "session_sha256": sha256(run_root / "session.json"), "jobs": len(expected_jobs),
        "verified_solves": expected_solves,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-root", type=Path, required=True, help="contains m37/raw and m41/raw")
    ap.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    sample_paths = {study: cfg["sample"] for study, cfg in CFG.items()}
    for study, cfg in CFG.items():
        if sha256(cfg["source"]) != cfg["source_sha256"]:
            raise ValueError(f"{study}: current source hash does not match the frozen protocol")
        if cfg["params"] and sha256(cfg["params"]) != cfg["params_sha256"]:
            raise ValueError(f"{study}: current params hash does not match the frozen protocol")
    samples = {study: read_sample(sample_paths[study], cfg) for study, cfg in CFG.items()}
    run_metadata = validate_run_metadata(args.run_root, samples)
    summaries, contrasts, studies, all_arms = [], [], {}, {}
    archives = {s: load_archive(Path(cfg["archive"]), cfg) for s, cfg in CFG.items()}
    seeds = np.random.SeedSequence(BOOTSTRAP_SEED).spawn(10)
    seed_i = 0
    for study, cfg in CFG.items():
        sample = samples[study]
        raw = args.run_root / study / "raw"
        data, chunks, files = load_study(raw, sample, cfg)
        arms = {"crater_neg": ("crater", 0), "crater_tau": ("crater", 1)}
        arms.update({lev: (lev, 0) for lev in cfg["levels"][1:]})
        means, boots = {}, {}
        for arm, (level, mode) in arms.items():
            curves = curve_arrays(sample, data, level, mode, "ops")
            curve_chunks = curve_chunk_arrays(sample, chunks, level, mode, "ops")
            secs = curve_arrays(sample, data, level, mode, "sec")
            diagnostics = {
                name: curve_arrays(sample, data, level, mode, name)
                for name in ("walks", "cycles", "abandoned", "useless")
            }
            summaries.append(describe(study, arm, level, mode, curves, secs, cfg["setup"], cfg["ell"], diagnostics))
            means[arm] = float(np.mean([x.mean() for x in curves]))
            print(f"bootstrap {study}/{arm}: {len(curves)} curves, "
                  f"{sum(len(x) for x in curve_chunks)} chunks", file=sys.stderr, flush=True)
            boots[arm] = chunk_aware_means(curve_chunks, BOOTSTRAP_REPS, INNER_RESAMPLES,
                                            np.random.default_rng(seeds[seed_i]), MAX_BOOTSTRAP_CELLS)
            seed_i += 1
        all_arms[study] = (means, boots)
        studies[study] = {
            "m": cfg["m"], "levels": list(cfg["levels"]), "setup_ops_subtracted": cfg["setup"],
            "sample_path": str(sample_paths[study]), "sample_sha256": sha256(sample_paths[study]),
            "raw_path": str(raw), "raw_file_count": len(files), "raw_tree_sha256": raw_tree_sha256(raw, files),
            "n_verified_solves": int(sum(len(v["ops"]) for v in data.values())),
        }
    # The six primary comparisons are one multiplicity family.
    for study, cfg in CFG.items():
        means, boots = all_arms[study]
        for level in cfg["levels"][1:]:
            contrasts.append(contrast(study, "primary_level_vs_crater_neg", "ops", level, "crater_neg",
                                      means[level], means["crater_neg"], boots[level], boots["crater_neg"],
                                      context="six-contrast Bonferroni family", family=6))
            contrasts.append(contrast(study, "setup_excluded_sensitivity", "ops_minus_setup", level, "crater_neg",
                                      means[level], means["crater_neg"], boots[level], boots["crater_neg"],
                                      context="pointwise sensitivity only", setup=cfg["setup"]))
        for level in cfg["levels"]:
            arm = "crater_neg" if level == "crater" else level
            contrasts.append(contrast(study, "secondary_level_vs_crater_tau", "ops", arm, "crater_tau",
                                      means[arm], means["crater_tau"], boots[arm], boots["crater_tau"],
                                      context="native Frobenius action context; pointwise only"))
            contrasts.append(contrast(study, "secondary_level_vs_crater_tau_ex_setup", "ops_minus_setup", arm, "crater_tau",
                                      means[arm], means["crater_tau"], boots[arm], boots["crater_tau"],
                                      context="fixed target-dependent setup removed; pointwise sensitivity only",
                                      setup=cfg["setup"]))
        grid, f = cfg["grid"], cfg["factors"]
        for factor, absent, present in ((f[0], ((1, 0), (0, 0)), ((1, 1), (0, 1))),
                                        (f[1], ((0, 1), (0, 0)), ((1, 1), (1, 0)))):
            for context, pair in (("other_factor_absent", absent), ("other_factor_present", present)):
                num, den = grid[pair[0]], grid[pair[1]]
                num_arm = "crater_neg" if num == "crater" else num
                den_arm = "crater_neg" if den == "crater" else den
                contrasts.append(contrast(study, "vertical_edge", "ops", num, den, means[num_arm], means[den_arm],
                                          boots[num_arm], boots[den_arm], factor=factor, context=context))
        named_means = {lev: means["crater_neg" if lev == "crater" else lev] for lev in cfg["levels"]}
        named_boots = {lev: boots["crater_neg" if lev == "crater" else lev] for lev in cfg["levels"]}
        contrasts.append(interaction(study, grid, named_means, named_boots))
    archive_cmp = {}
    for study, archive in archives.items():
        archive_cmp[study] = archive
        fresh = {r["numerator"]: r for r in contrasts if r["study"] == study and r["kind"] == "primary_level_vs_crater_neg"}
        for level, old in archive["vs_crater_neg"].items():
            old["fresh_minus_archive_bits"] = float(fresh[level]["log2_ratio"] - old["log2_ratio"])
    primary_rows = [r for r in contrasts if r["kind"] == "primary_level_vs_crater_neg"]
    global_equivalence = all(r["equivalent_within_3pct_simultaneous90"] is True for r in primary_rows)
    result = {
        "analysis": {
            "primary_metric": "ops",
            "bootstrap": "three-stage empirical hierarchical bootstrap: curves, process chunks, solves; crater chunks then solves",
            "bootstrap_reps": BOOTSTRAP_REPS, "inner_resamples_per_chunk": INNER_RESAMPLES,
            "empirical_reservoir_approximation": True, "max_bootstrap_cells": MAX_BOOTSTRAP_CELLS,
            "seed": BOOTSTRAP_SEED, "pointwise_confidence": .95, "primary_family_size": 6,
            "simultaneous_method": "Bonferroni", "equivalence_margin_ratio": [.97, 1.03],
            "timing_status": "descriptive only",
        },
        "validity": {"all_rows_verified": True, "exact_file_sets": True, "duplicate_rows": 0,
                     "run_metadata_and_receipts_verified": True},
        "run_metadata": run_metadata,
        "primary_global_equivalence_within_3pct_simultaneous90": global_equivalence,
        "studies": studies, "level_summaries": summaries, "contrasts": contrasts,
        "archived_pilot_comparison": archive_cmp,
        "interpretation_guardrail": "Operation-count differences do not establish an executable isogeny transfer, an ECDLP speedup, or a weak curve.",
    }
    with (args.output_dir / "results.json").open("w") as f:
        json.dump(result, f, indent=2, sort_keys=True)
        f.write("\n")
    with (args.output_dir / "level-summary.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summaries[0]))
        w.writeheader(); w.writerows(summaries)
    with (args.output_dir / "contrasts.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CONTRAST_FIELDS)
        w.writeheader(); w.writerows(contrasts)
    print(json.dumps({"output_dir": str(args.output_dir), "studies": studies}, indent=2))


if __name__ == "__main__":
    main()
