#!/usr/bin/env python3
"""Statistics, gates and the mechanical decision rule of EXP-CMFB-cea1d2 (trial t8), plus the run-output
writer shared with driver.py.

    python3 experiments/EXP-CMFB-cea1d2/implementation/analyze.py --runs-root experiments/EXP-CMFB-cea1d2/runs --out {run_dir}

All constants are literals below.  The classification is an Executor observation; any status change is
the Coordinator's.  check.py recomputes every table from the raw per-member records WITHOUT importing
this module.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import resource
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))

import numpy as np  # noqa: E402
import yaml  # noqa: E402

import count  # noqa: E402
import curves  # noqa: E402

DELTA = 0.005
ALPHA = 0.05
RANDOMIZATION_DRAWS = 20000
BOOTSTRAP_RESAMPLES = 5000
BLOCK_L = 3
MATERIAL = 0.02
CONTRAST_LEVEL = 0.99
Z_MDE = 2.77 + 0.84  # Holm level alpha/9 at 80 percent power
VAR_INFLATION = 3.0
BAND_GENERIC = (1.98, 2.02)
BAND_WRONG = (0.96, 1.04)
SIGMA_BAND = (0.75, 1.33)
ARMS = ("FAM", "N-A", "N-B")
STREAM = {"ci": 0, "fam_na": 1, "fam_natheta": 2, "na_nb": 3, "slope": 4}


# ------------------------------------------------------------------- run outputs
def _git(*args: str) -> str:
    try:
        return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True,
                              check=False).stdout.strip()
    except OSError:
        return ""


def sha256_file(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


SOURCE_FILES = [
    "experiments/EXP-CMFB-cea1d2/implementation/driver.py",
    "experiments/EXP-CMFB-cea1d2/implementation/count.py",
    "experiments/EXP-CMFB-cea1d2/implementation/curves.py",
    "experiments/EXP-CMFB-cea1d2/implementation/analyze.py",
    "experiments/EXP-CMFB-cea1d2/implementation/check.py",
    "src/crypto_autoresearcher/__init__.py",
    "src/crypto_autoresearcher/parallel.py",
]


def provenance() -> dict:
    mem_kb = 0
    try:
        with open("/proc/meminfo") as handle:
            for line in handle:
                if line.startswith("MemTotal"):
                    mem_kb = int(line.split()[1])
    except OSError:
        pass
    return {
        "commit": _git("rev-parse", "HEAD") or "unknown",
        "dirty": bool(_git("status", "--porcelain", "--untracked-files=no")),
        "environment": {"python": sys.version, "numpy": np.__version__, "pyyaml": yaml.__version__,
                        "platform": platform.platform(), "machine": platform.machine(),
                        "cpu_count": os.cpu_count(), "mem_total_bytes": mem_kb * 1024},
        "source_sha256": {f: sha256_file(REPO / f) for f in SOURCE_FILES},
    }


def write_run_outputs(run_dir: Path, *, trial_id: str, run_id: str, role: str, raw: dict, timings: dict,
                      workers: int, started: float, memory_mb: int) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    prov = provenance()
    own = resource.getrusage(resource.RUSAGE_SELF)
    kids = resource.getrusage(resource.RUSAGE_CHILDREN)
    peak = max(own.ru_maxrss, kids.ru_maxrss) * 1024
    peak = max(peak, timings.get("worker_rss_bytes_max", 0))
    finished = time.time()
    raw = dict(raw)
    raw["peak_rss_bytes"] = peak
    raw["timings"] = timings
    summary = {"gate_passed": raw.get("gate_passed"), "classification": raw.get("classification"),
               "official": raw.get("official"), "instance_list_sha256": raw.get("instance_list_sha256"),
               "members": len(raw.get("members") or [])}
    manifest = {"run": {
        "id": run_id, "experiment_id": curves.EXPERIMENT_ID, "trial_id": trial_id, "role": role,
        "status": "completed",
        "code": {"commit": prov["commit"], "dirty": prov["dirty"], "command": list(sys.orig_argv),
                 "source_sha256": prov["source_sha256"]},
        "environment": prov["environment"],
        "seeds": list(curves.FROZEN_SEEDS),
        "inputs": {"workers": workers, "memory_mb": memory_mb, "K": raw.get("K"),
                   "instance_list_sha256": raw.get("instance_list_sha256")},
        "timing": {"started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started)),
                   "finished_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(finished)),
                   "wall_seconds": round(finished - started, 3),
                   "stages": timings.get("stages", {}),
                   "tau_seconds_per_triple": timings.get("tau_seconds_per_triple"),
                   "bsgs_seconds_total": timings.get("bsgs_seconds_total"),
                   "count_seconds_total": timings.get("count_seconds_total")},
        "resources": {"peak_rss_bytes": peak, "cpu_seconds": round(own.ru_utime + own.ru_stime + kids.ru_utime
                                                                    + kids.ru_stime, 3)},
        "result": summary,
        "artifacts": {"raw_result": "raw-result.json"},
    }}
    (run_dir / "raw-result.json").write_text(json.dumps(raw, sort_keys=True, separators=(",", ":")) + "\n")
    (run_dir / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False))


# --------------------------------------------------------------------- statistics
def ana_rng(seed: int, cell: str, arm: str, stream: int, member: int = 0) -> np.random.Generator:
    return curves.rng(seed, cell, arm, member, stream)


def ratio_vector(V: np.ndarray) -> np.ndarray:
    """ratio_j = coverage of the member base / mean coverage of its matched random bases."""
    return V[:, 0] / V[:, 1:].mean(axis=1)


def t_stat(V: np.ndarray) -> float:
    return float(np.mean(ratio_vector(V) - 1.0))


def randomization_p(V: np.ndarray, gen: np.random.Generator, draws: int = RANDOMIZATION_DRAWS) -> dict:
    """Two-sided randomization test: per draw, for each member pick one of its 201 coverages as the
    pseudo-observed value (uniform), take the other 200 as null pool, T* = mean(ratio* - 1)."""
    n, m = V.shape
    t_obs = t_stat(V)
    u = gen.integers(0, m, size=(draws, n))
    pick = V[np.arange(n)[None, :], u]
    others = (V.sum(axis=1)[None, :] - pick) / (m - 1)
    t_star = (pick / others - 1.0).mean(axis=1)
    p = (1 + int((np.abs(t_star) >= abs(t_obs)).sum())) / (draws + 1)
    return {"t_obs": t_obs, "p": p, "draws": draws}


def block_indices(n: int, L: int, gen: np.random.Generator, resamples: int) -> np.ndarray:
    """Moving-block bootstrap: ceil(n/L) overlapping blocks of length L drawn with replacement, cut to n."""
    L = min(L, n)  # a cell with fewer than L members (underpowered, descriptive only) uses blocks of n
    if L == 1:
        return gen.integers(0, n, size=(resamples, n))
    nb = -(-n // L)
    starts = gen.integers(0, n - L + 1, size=(resamples, nb))
    idx = (starts[:, :, None] + np.arange(L)[None, None, :]).reshape(resamples, nb * L)
    return idx[:, :n]


def boot_t(x: np.ndarray, L: int, gen: np.random.Generator, resamples: int = BOOTSTRAP_RESAMPLES) -> np.ndarray:
    return x[block_indices(len(x), L, gen, resamples)].mean(axis=1)


def percentile_ci(draws: np.ndarray, level: float) -> tuple[float, float]:
    lo, hi = np.percentile(draws, [50 * (1 - level), 100 - 50 * (1 - level)])
    return float(lo), float(hi)


def holm(pvals: dict) -> dict:
    items = sorted(pvals.items(), key=lambda kv: (kv[1], str(kv[0])))
    m, out, running = len(items), {}, 0.0
    for rank, (key, p) in enumerate(items):
        running = max(running, min(1.0, (m - rank) * p))
        out[key] = running
    return out


def ks_uniform_p(values: np.ndarray) -> float:
    x = np.sort(values)
    n = len(x)
    d = max(float(np.max(np.arange(1, n + 1) / n - x)), float(np.max(x - np.arange(0, n) / n)))
    lam = (math.sqrt(n) + 0.12 + 0.11 / math.sqrt(n)) * d
    return float(min(1.0, max(0.0, 2 * sum((-1) ** (k - 1) * math.exp(-2 * k * k * lam * lam)
                                           for k in range(1, 101)))))


def ks_normal_p(z: np.ndarray) -> float:
    x = np.sort(z)
    n = len(x)
    cdf = np.array([0.5 * (1 + math.erf(v / math.sqrt(2))) for v in x])
    d = max(float(np.max(np.arange(1, n + 1) / n - cdf)), float(np.max(cdf - np.arange(0, n) / n)))
    lam = (math.sqrt(n) + 0.12 + 0.11 / math.sqrt(n)) * d
    return float(min(1.0, max(0.0, 2 * sum((-1) ** (k - 1) * math.exp(-2 * k * k * lam * lam)
                                           for k in range(1, 101)))))


def ols_slope(x: np.ndarray, y: np.ndarray) -> float:
    xc = x - x.mean()
    return float((xc * (y - y.mean())).sum() / (xc * xc).sum())


def mde(sigma_rel: float, n: int) -> float:
    """80 percent power minimum detectable effect at the Holm level with a 3-fold variance inflation."""
    return Z_MDE * math.sqrt(VAR_INFLATION) * 1.0025 * sigma_rel / math.sqrt(n)


def pool_scans(scans: list[dict]) -> dict:
    S = sum(s["S"] for s in scans)
    L = sum(s["L"] for s in scans)
    V = sum(s["V"] for s in scans)
    Vl = sum(s["Vlift"] for s in scans)
    R = S / L
    return {"n_curves": len(scans), "S_total": S, "L_total": L, "R_pool": R, "se": 2.0 / math.sqrt(S),
            "R_wrong": (Vl / V) / (L / S), "lifts_ok": all(s["lifts_ok"] and s["zero"] == 0 for s in scans)}


# -------------------------------------------------------------- gates (t2 and t3)
def qr_pools(scans: list[dict]) -> dict:
    out: dict = {}
    keys = sorted({(s["arm"], s["cell"]) for s in scans})
    for arm, cell in keys:
        out[f"{arm}|{cell}"] = pool_scans([s["scan"] for s in scans if s["arm"] == arm and s["cell"] == cell])
    return out


def gates_from_t2(c: dict) -> dict:
    pools = qr_pools(c["qr_scans"])
    nb = [v for k, v in pools.items() if k.startswith("N-B|")]
    return {
        "brute_force_60_cases": c["brute_force"]["cases"] == 60 and c["brute_force"]["failures"] == 0,
        "instances_valid": not c["instances"]["failures"],
        "labelling": all(x["check"]["ok"] for x in c["labelling"]) and bool(c["labelling"]),
        "m0_recount": all(r["m0"]["loop_failures"] == 0 and r["m0"]["hist_failures"] == 0 for r in c["m0_recount"]),
        "qr_generic_band": bool(nb) and all(BAND_GENERIC[0] <= v["R_pool"] <= BAND_GENERIC[1] for v in nb),
        "legendre_x_negative_control": bool(nb) and all(BAND_WRONG[0] <= v["R_wrong"] <= BAND_WRONG[1] for v in nb),
        "lifts_and_full_period": all(v["lifts_ok"] for v in pools.values()) and all(x["ok"] for x in c["full_period"]),
        "parallel_determinism": bool(c["determinism"]["passed"]),
    }


def sensitivity_from_records(recs: list[dict], cells: list[str]) -> dict:
    """Planted B+1 base against 200 random size-B bases on the N-B-ctrl curves of each cell."""
    out, gates = {}, {}
    for cell in cells:
        rs = sorted((r for r in recs if r["cell"] == cell), key=lambda r: r["index"])
        rows, V = [], []
        for r in rs:
            rnd = np.array(r["random_seen"], dtype=float)
            planted = float(r["member_seen"])
            k_ge = int((rnd >= planted).sum())
            known = count.planted_known_ratio(r["base_size"], r["N"])
            rows.append({"index": r["index"], "p": r["p"], "N": r["N"], "B": r["base_size"],
                         "ratio": planted / rnd.mean(), "known_ratio": known, "k_ge": k_ge,
                         "rank_p": (1 + k_ge) / (len(rnd) + 1), "detected": (1 + k_ge) / (len(rnd) + 1) <= 0.01})
            V.append([planted] + list(rnd))
        V = np.array(V)
        ratio = np.array([x["ratio"] for x in rows])
        known = np.array([x["known_ratio"] for x in rows])
        se = float(ratio.std(ddof=1) / math.sqrt(len(ratio))) if len(ratio) > 1 else float("inf")
        tol = max(0.001, 3 * se)
        rz = randomization_p(V, ana_rng(curves.SEEDS["randomization"], cell, "N-B-ctrl", 0))
        cell_out = {"n": len(rows), "detected": sum(x["detected"] for x in rows), "curves": rows,
                    "pooled_ratio": float(ratio.mean()), "pooled_known": float(known.mean()),
                    "pooled_se": se, "tolerance": tol,
                    "within_tolerance": abs(float(ratio.mean() - known.mean())) <= tol,
                    "randomization_p": rz["p"], "t_obs": rz["t_obs"]}
        out[cell] = cell_out
        gates[f"sensitivity_{cell}"] = (cell_out["n"] == 8 and cell_out["detected"] >= 7
                                        and cell_out["within_tolerance"] and rz["p"] <= 0.001)
    ok_m0 = all(r["m0"]["loop_failures"] == 0 for r in recs)
    ok_valid = all(r["validity"]["ok"] and r["label_check"]["ok"] and r["distinct_classes"] for r in recs)
    gates["sensitivity_m0_and_validity"] = bool(recs) and ok_m0 and ok_valid
    return {"cells": out, "gates": gates}


# ----------------------------------------------------------------------- analysis
def load_run(runs_root: Path, trial_id: str):
    d = runs_root / curves.TRIALS[trial_id][0]
    try:
        raw = json.loads((d / "raw-result.json").read_text())
        manifest = yaml.safe_load((d / "manifest.yaml").read_text())
    except (OSError, ValueError):
        return None, None
    return manifest, raw


def required_manifest_fields_ok(m: dict | None) -> bool:
    try:
        r = m["run"]
        return bool(r["code"]["command"] and r["code"]["commit"] and r["environment"] and r["seeds"]
                    and r["timing"]["wall_seconds"] is not None and r["resources"]["peak_rss_bytes"] > 0)
    except (KeyError, TypeError):
        return False


def member_matrix(members: list[dict]) -> np.ndarray:
    return np.array([[m["member_seen"]] + m["random_seen"] for m in members], dtype=float)


def run_analysis(runs_root: Path, official: bool = True) -> dict:
    runs_root = Path(runs_root)
    loaded = {t: load_run(runs_root, t) for t in curves.TRIALS if t != "t8-analysis"}
    defects = [t for t, (m, r) in loaded.items() if m is None]
    out: dict = {"schema": "crypto.autoresearch.cmfb.analysis.v1", "experiment_id": curves.EXPERIMENT_ID,
                 "trial_id": "t8-analysis", "run_id": curves.TRIALS["t8-analysis"][0], "official": official,
                 "seeds": curves.FROZEN_SEEDS, "constants": {
                     "delta": DELTA, "alpha": ALPHA, "randomization_draws": RANDOMIZATION_DRAWS,
                     "bootstrap_resamples": BOOTSTRAP_RESAMPLES, "block_length_fam": BLOCK_L,
                     "material": MATERIAL, "contrast_level": CONTRAST_LEVEL}}
    if defects:
        out.update({"classification": "INCOMPLETE", "defects": defects, "gate_passed": False})
        return out
    raws = {t: r for t, (m, r) in loaded.items()}
    t1, t2, t3 = raws["t1-inventory"], raws["t2-gate-instrument"], raws["t3-gate-sensitivity"]
    inv = curves.build_instances()
    plan = inv["plan"]
    out["instance_list_sha256"] = inv["sha256"]
    cells = plan["cells"]
    members = [m for t in curves.MEASURE_TRIALS for m in raws[t]["members"]]

    # ---- invalidation rules I1..I9 (the parts decidable from the run set)
    rules: dict = {}
    rules["I1"] = (len(loaded) == 7 and all(required_manifest_fields_ok(m) for m, _ in loaded.values()))
    rules["I2"] = all(m["m0"]["loop_failures"] == 0 and m["m0"]["hist_failures"] == 0 for m in members) \
        and all(r["m0"]["loop_failures"] == 0 and r["m0"]["hist_failures"] == 0 for r in t2["controls"]["m0_recount"])
    rules["I3"] = t2["controls"]["brute_force"]["failures"] == 0 and t2["controls"]["brute_force"]["cases"] == 60
    inst_ok = all(i["validity"]["ok"] for i in t1["instances"]) and not t2["controls"]["instances"]["failures"]
    seen_p: dict = {}
    for i in inv["instances"]:
        if i["arm"] in ("N-A", "N-B"):
            key = (i["arm"], i["cell"])
            if i["p"] in seen_p.setdefault(key, set()):
                inst_ok = False
            seen_p[key].add(i["p"])
    rules["I4"] = inst_ok and all(m["validity"]["ok"] for m in members)
    rules["I5"] = all(m["label_check"]["ok"] and m["distinct_classes"] for m in members) and all(
        x["check"]["ok"] for x in t2["controls"]["labelling"])
    g2 = gates_from_t2(t2["controls"])
    rules["I6"] = g2["qr_generic_band"] and g2["legendre_x_negative_control"] and g2["lifts_and_full_period"]
    sens = sensitivity_from_records(t3["members"], cells)
    rules["I7"] = all(sens["gates"].values())
    shas = {t: r["instance_list_sha256"] for t, r in raws.items()}
    expected_members = [i for i in inv["instances"] if i["arm"] != "N-B-ctrl"]
    got = sorted((m["arm"], m["cell"], m["index"], m["p"], m["N"], m["A"], m["B"]) for m in members)
    want = sorted((i["arm"], i["cell"], i["index"], i["p"], i["N"], i["A"], i["B"]) for i in expected_members)
    rules["I8"] = (all(s == inv["sha256"] for s in shas.values()) and got == want
                   and all(r["seeds"] == curves.FROZEN_SEEDS for r in raws.values())
                   and all(m["run"]["seeds"] == curves.FROZEN_SEEDS for m, _ in loaded.values())
                   and all(m["random_distinct_failures"] == 0 for m in members)
                   and len({(m["arm"], m["cell"], m["index"]) for m in members}) == len(members))
    t2_scans = {(s["arm"], s["cell"], s["index"]): s["scan"] for s in t2["controls"]["qr_scans"]}
    rules["I9"] = all(t2_scans.get((m["arm"], m["cell"], m["index"])) == m["scan"] for m in members)
    out["all_inputs_official"] = bool(all(r.get("official") for r in raws.values()) and official)
    rules["gates_t2"] = all(g2.values())
    rules["gates_t3"] = all(sens["gates"].values())
    void = not all(rules.values())
    out["rules"] = rules

    # ---- arm-by-cell tables
    counts = t1["inventory"]["counts"]
    M = {c: (counts[c] if c in counts else counts["C16"] + counts["C20"]) for c in cells}
    tables, cell_info = {}, {}
    for cell in cells:
        info = {"M_c": M[cell], "arms": {}}
        for arm in ARMS:
            mem = sorted((m for m in members if m["arm"] == arm and m["cell"] == cell), key=lambda m: m["index"])
            if not mem:
                continue
            V = member_matrix(mem)
            sig = np.array([np.std(V[j, 1:], ddof=1) / V[j, 1:].mean() for j in range(len(mem))])
            form = np.array([count.sigma_rel_formula(m["base_size"], m["N"]) for m in mem])
            rms = float(np.sqrt(np.mean(sig ** 2)))
            gen_ci = ana_rng(curves.SEEDS["bootstrap"], cell, arm, STREAM["ci"])
            L = BLOCK_L if arm == "FAM" else 1
            x = ratio_vector(V) - 1.0
            ci = percentile_ci(boot_t(x, L, gen_ci), 0.95)
            rz = randomization_p(V, ana_rng(curves.SEEDS["randomization"], cell, arm, 0))
            ranks = []
            for j in range(len(mem)):
                m0 = V[j, 0]
                r = V[j, 1:]
                gt, eq = int((r > m0).sum()), int((r == m0).sum())
                e = int(ana_rng(curves.SEEDS["randomization"], cell, arm, curves.STREAM_TIE, j).integers(0, eq + 1))
                ranks.append((1 + gt + e) / V.shape[1])
            ranks = np.array(ranks)
            z = np.concatenate([(V[j, 1:] - V[j, 1:].mean()) / np.std(V[j, 1:], ddof=1) for j in range(len(mem))])
            lag1 = (float(np.corrcoef(x[:-1], x[1:])[0, 1]) if arm == "FAM" and len(x) > 3 else None)
            row = {"arm": arm, "cell": cell, "n": len(mem), "T": float(x.mean()), "ci95": ci,
                   "randomization_p": rz["p"], "ratio": [float(v) for v in ratio_vector(V)],
                   "mean_log2_p": float(np.mean([math.log2(m["p"]) for m in mem])),
                   "sigma_rel_rms_measured": rms, "sigma_rel_rms_formula": float(np.sqrt(np.mean(form ** 2))),
                   "sigma_ratio": rms / float(np.sqrt(np.mean(form ** 2))),
                   "sigma_flag_I10": not (SIGMA_BAND[0] <= rms / float(np.sqrt(np.mean(form ** 2))) <= SIGMA_BAND[1]),
                   "mde": mde(rms, len(mem)), "min_rank_p": float(ranks.min()),
                   "sidak_p": float(1 - (1 - ranks.min()) ** len(mem)), "ks_uniform_p": ks_uniform_p(ranks),
                   "ks_normal_p": ks_normal_p(z), "lag1_autocorr": lag1,
                   "twisted_fraction": float(np.mean([m["twisted"] for m in mem])),
                   "p_mod_120": [m["p_mod_120"] for m in mem], "index": [m["index"] for m in mem],
                   "log2_p": [math.log2(m["p"]) for m in mem]}
            tables[f"{arm}|{cell}"] = row
            info["arms"][arm] = len(mem)
        info["n_fam"] = info["arms"].get("FAM", 0)
        info["mde_ok"] = all(tables[f"{a}|{cell}"]["mde"] <= DELTA / 2 for a in ARMS if f"{a}|{cell}" in tables)
        info["powered"] = bool(M[cell] >= 8 and info["n_fam"] >= 8 and len(info["arms"]) == 3
                               and all(n >= 8 for n in info["arms"].values()) and info["mde_ok"])
        cell_info[cell] = info
    powered = [c for c in cells if cell_info[c]["powered"]]
    pvals = {k: v["randomization_p"] for k, v in tables.items() if k.split("|")[1] in powered}
    adj = holm(pvals)
    for k, v in tables.items():
        v["holm_p"] = adj.get(k)
        inside = v["ci95"][0] >= -DELTA and v["ci95"][1] <= DELTA
        v["ci_inside_delta"] = bool(inside)
        rejected = v["holm_p"] is not None and v["holm_p"] <= ALPHA
        v["holm_rejected"] = bool(rejected)
        v["detected_excess"] = bool(rejected and v["T"] > DELTA)
        v["detected_deficit"] = bool(rejected and v["T"] < -DELTA)
    out["tables"], out["cells"], out["powered_cells"] = tables, cell_info, powered

    # ---- contrasts (99 percent, block bootstrap within cell and arm), slopes
    def arm_members(arm, cell, stratum=None):
        mem = sorted((m for m in members if m["arm"] == arm and m["cell"] == cell
                      and (stratum is None or m["stratum"] == stratum)), key=lambda m: m["index"])
        return ratio_vector(member_matrix(mem)) - 1.0 if mem else None

    contrasts = {}
    for cell in powered:
        for name, (a1, s1, a2, s2) in {"fam_na": ("FAM", None, "N-A", None),
                                       "fam_natheta": ("FAM", None, "N-A", "theta"),
                                       "na_nb": ("N-A", None, "N-B", None)}.items():
            x1, x2 = arm_members(a1, cell, s1), arm_members(a2, cell, s2)
            gen = ana_rng(curves.SEEDS["bootstrap"], cell, a1, STREAM[name])
            d1 = boot_t(x1, BLOCK_L if a1 == "FAM" else 1, gen)
            d2 = boot_t(x2, BLOCK_L if a2 == "FAM" else 1, gen)
            lo, hi = percentile_ci(d1 - d2, CONTRAST_LEVEL)
            contrasts[f"{name}|{cell}"] = {"estimate": float(x1.mean() - x2.mean()), "ci99": (lo, hi),
                                           "excludes_zero": bool(lo > 0 or hi < 0), "lower_above_delta": bool(lo > DELTA)}
    out["contrasts"] = contrasts
    slopes = {}
    for arm in ARMS:
        if len(powered) < 3:
            slopes[arm] = {"assessable": False, "powered_cells": len(powered)}
            continue
        xs = [(np.array(tables[f"{arm}|{c}"]["log2_p"]), np.array(tables[f"{arm}|{c}"]["ratio"]) - 1.0) for c in powered]
        est = ols_slope(np.concatenate([a for a, _ in xs]), np.concatenate([b for _, b in xs]))
        gen = ana_rng(curves.SEEDS["bootstrap"], "C24", arm, STREAM["slope"])
        L = BLOCK_L if arm == "FAM" else 1
        idxs = [block_indices(len(a), L, gen, BOOTSTRAP_RESAMPLES) for a, _ in xs]
        sl = np.array([ols_slope(np.concatenate([a[ix[r]] for (a, _), ix in zip(xs, idxs)]),
                                 np.concatenate([b[ix[r]] for (_, b), ix in zip(xs, idxs)]))
                       for r in range(BOOTSTRAP_RESAMPLES)])
        lo, hi = percentile_ci(sl, 0.95)
        slopes[arm] = {"assessable": True, "slope_per_log2p": est, "ci95": (lo, hi), "positive": bool(lo > 0)}
    out["slopes"] = slopes

    # ---- scan-efficiency branch (pools from t2, all instances of the arm and cell)
    pools = qr_pools(t2["controls"]["qr_scans"])
    nb_in = all(BAND_GENERIC[0] <= v["R_pool"] <= BAND_GENERIC[1] for k, v in pools.items() if k.startswith("N-B|"))
    anomalies = {}
    for k, v in pools.items():
        arm = k.split("|")[0]
        if arm in ("FAM", "N-A"):
            band = max(0.02, 3 * v["se"])
            anomalies[k] = {"R_pool": v["R_pool"], "band": band, "outside": abs(v["R_pool"] - 2.0) > band}
    scan_branch = None
    if nb_in:
        fam = [k for k, v in anomalies.items() if k.startswith("FAM|") and v["outside"]]
        na = [k for k, v in anomalies.items() if k.startswith("N-A|") and v["outside"]]
        if fam or na:
            scan_branch = "E2_scan_lead" if na else "E3_scan_lead"
    out["scan_efficiency"] = {"pools": pools, "anomalies": anomalies, "branch": scan_branch}
    out["sensitivity"] = sens["cells"]
    out["bateman_horn"] = t1["inventory"]["bateman_horn"]
    out["pooling"] = plan
    out["instance_list_sha256"] = inv["sha256"]
    out["member_counts"] = counts

    # ---- decision rule
    out["classification"], out["lead_tier"] = classify(void, powered, tables, contrasts, slopes, defects)
    out["holm_rejection_below_delta"] = [k for k, v in tables.items() if v["holm_rejected"]
                                         and not v["detected_excess"] and not v["detected_deficit"]]
    out["gate_passed"] = not void
    out["growth_assessable"] = len(powered) >= 3
    out["members_total"] = len(members)
    return out


def classify(void: bool, powered: list, tables: dict, contrasts: dict, slopes: dict, defects: list):
    if defects:
        return "INCOMPLETE", None
    if void:
        return "INSTRUMENT_VOID", None
    if not powered:
        return "INCONCLUSIVE_UNDERPOWERED", None
    rows = [v for k, v in tables.items() if k.split("|")[1] in powered]
    exc = [v for v in rows if v["detected_excess"]]
    dfc = [v for v in rows if v["detected_deficit"]]
    if not exc and not dfc and all(v["ci_inside_delta"] for v in rows):
        return "NULL_AT_RESOLUTION", None
    if not exc and not dfc and not any(v["holm_rejected"] for v in rows):
        return "INCONCLUSIVE_UNRESOLVED", None
    if exc:
        fam_big = any(v["arm"] == "FAM" and v["T"] >= MATERIAL for v in rows if v["cell"] in powered)
        slope = slopes.get("FAM", {})
        tier = "MATERIAL" if fam_big and slope.get("assessable") and slope.get("positive") else "SUB-THRESHOLD"
        if any(v["arm"] == "N-B" for v in exc):
            return "E1_LEAD", tier
        for v in exc:
            if v["arm"] == "N-A":
                c = contrasts.get(f"na_nb|{v['cell']}")
                if c and c["excludes_zero"] and c["lower_above_delta"]:
                    return "E2_LEAD", tier
        fam_only = (all(v["arm"] == "FAM" for v in exc))
        if fam_only:
            for v in exc:
                c = contrasts.get(f"fam_na|{v['cell']}")
                if c and c["excludes_zero"] and c["lower_above_delta"]:
                    return "E3_LEAD", tier
        return "INCONCLUSIVE_UNATTRIBUTED", None
    if dfc:
        return "DEFICIT_RECORDED", None
    return "INCONCLUSIVE_UNRESOLVED", None  # Holm rejection below delta with a wide interval: R3/R4 gap


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-root", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    started = time.time()
    raw = run_analysis(Path(args.runs_root))
    write_run_outputs(Path(args.out), trial_id="t8-analysis", run_id=curves.TRIALS["t8-analysis"][0],
                      role="analysis_and_decision", raw=raw, timings={"stages": {"analysis_seconds": time.time() - started}},
                      workers=1, started=started, memory_mb=curves.TRIALS["t8-analysis"][2])
    print(raw["classification"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
