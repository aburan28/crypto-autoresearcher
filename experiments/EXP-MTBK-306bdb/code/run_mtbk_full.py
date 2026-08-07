#!/usr/bin/env python3
"""EXP-MTBK-306bdb full dataset harness (DEC-20260805-d4b182 continuation).

This driver executes the frozen 30-cell grid:

  curves: 5 fixed seeds (1..5), field 16
  m arities: {3,4,5}
  b exponents: {0.6,0.7}

For every (curve, m, b), it compares:

- std: full-factor-base (m-1)-tuple scan
- bkk: first-half factor-base (m-1)-tuple scan

and records harvest/descend-channel summary metrics plus a reusable theorem-test
check (KN-FIND-c7d31e).
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
import platform
import random
import resource
import statistics
import subprocess
import sys
import time
import traceback
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from datetime import datetime, timezone

import sympy
import yaml

REPO = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir, os.pardir)
)
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from harness.toycurve import (ECDLPInstance, EllipticCurve, _seed_int,
                              generate_instance)  # noqa: E402
from harness.semaev import build_factor_base  # noqa: E402
from harness import rho as rho_mod  # noqa: E402
from harness.runner import RunResult, curve_id, write_run  # noqa: E402


EXP_ID = "EXP-MTBK-306bdb"
EXP_AREA = "MTBK"
EXP_DIR = os.path.join(REPO, "experiments", EXP_ID)
FROZEN_PATH = os.path.join(EXP_DIR, "frozen-instances.yaml")

TARGET_COUNT_TARGET = 50
CELL_MS = [3, 4, 5]
CELL_B_EXP = [0.6, 0.7]
CHECK_CAP_STD = 20_000
CHECK_CAP_BKK = 20_000
CHECK_CAP_BETA = 20_000
THEOREM_TRIALS = 20_000
THEOREM_TOL = 0.99
RUN_SUFFIX_DEFAULT = "306bdb-01"
DESCH_TARGET_TAG = "desc"
HARV_TARGET_TAG = "harv"
TARGET_STREAM_TAGS = {
    "descent": DESCH_TARGET_TAG,
    "harvest": HARV_TARGET_TAG,
}
RHO_SAMPLE_PER_CELL = 10


class HarnessFailure(RuntimeError):
    """Raised when pre-registered frozen materials do not verify."""


def iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def sha256_obj(obj) -> str:
    blob = json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(blob).hexdigest()


def stable_seed(*parts: object) -> int:
    """Deterministic seed independent of Python hash randomization."""
    raw = "|".join(str(p) for p in parts)
    return int(hashlib.sha256(raw.encode()).hexdigest()[:16], 16)


def sha256_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def git_state() -> tuple[str, bool]:
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                           capture_output=True, text=True).stdout.strip() or "unknown"
    out = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no"], cwd=REPO,
        capture_output=True, text=True
    ).stdout
    dirty = bool([l for l in out.splitlines()
                 if l.strip() and "._" not in l[3:].split("/")[0]])
    return commit, dirty


def environment() -> dict:
    return {
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "sage_version": None,
        "dependencies": {
            "sympy": sympy.__version__,
            "pyyaml": yaml.__version__,
        },
    }


def read_frozen(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    if not isinstance(doc, dict):
        raise HarnessFailure(f"frozen file {path} is not a YAML mapping")
    return doc


def regen_curve(inst_entry: dict) -> ECDLPInstance:
    seed = int(inst_entry["seed"])
    bits = int(inst_entry["field_bits"])
    t0 = time.time()
    inst = generate_instance(seed=seed, field_bits=bits,
                            min_prime_order_bits=bits - 2)
    return inst, time.time() - t0


def curve_record_payload(inst: ECDLPInstance) -> dict:
    E = inst.curve()
    checks = {
        "p_prime": sympy.isprime(inst.p),
        "n_prime": sympy.isprime(inst.n),
        "P_on_curve": E.is_on_curve(inst.P),
        "Q_on_curve": E.is_on_curve(inst.Q),
        "Q_eq_kP": E.mul(inst.k, inst.P) == inst.Q,
        "nP_eq_O": E.mul(inst.n, inst.P) is None,
    }
    return {
        "seed": inst.seed,
        "field_bits": inst.field_bits,
        "p": inst.p,
        "a": inst.a,
        "b": inst.b,
        "n": inst.n,
        "P": list(inst.P),
        "Q": list(inst.Q),
        "k": inst.k,
        "checks": checks,
        "curve_id": curve_id(inst.p, inst.a, inst.b, inst.field_bits),
    }


def make_targets(inst: ECDLPInstance, tag: str, count: int) -> list[dict]:
    E = inst.curve()
    targets = []
    j = 0
    max_j = max(10000, count * 200)
    while len(targets) < count and j < max_j:
        a = _seed_int(inst.seed, f"{tag}a{j}") % inst.n
        b = _seed_int(inst.seed, f"{tag}b{j}") % inst.n
        R = E.add(E.mul(a, inst.P), E.mul(b, inst.Q))
        if R is not None:
            targets.append({
                "index": len(targets),
                "seed_index": j,
                "a": int(a),
                "b": int(b),
                "x": int(R[0]),
                "y": int(R[1]),
            })
        j += 1
    if len(targets) < count:
        raise HarnessFailure(f"failed to generate {count} targets for tag={tag}")
    return targets


def verify_frozen(frozen: dict) -> tuple[bool, dict, dict, dict, dict]:
    issues: list[str] = []
    inst_map: dict[int, dict] = {}
    fb_map: dict[tuple[int, float], dict] = {}
    target_map: dict[tuple[int, str], dict] = {}
    regen_curves: dict[int, ECDLPInstance] = {}

    instance_entries = {int(item["seed"]): item for item in frozen.get("instances", [])}
    if not instance_entries:
        issues.append("no instances in frozen-instances.yaml")

    frozen_sha_check = sha256_obj({k: v for k, v in frozen.items() if k != "sha256"})
    if frozen.get("sha256") != frozen_sha_check:
        issues.append("frozen root sha256 mismatch")

    # Recompute all instances.
    for seed, item in instance_entries.items():
        inst, gen_seconds = regen_curve(item)
        regen_curves[seed] = inst
        payload = curve_record_payload(inst)
        payload["generation"] = (
            f"harness/toycurve.py generate_instance(seed={seed}, "
            f"field_bits={inst.field_bits}, min_prime_order_bits={inst.field_bits - 2})"
        )
        observed = sha256_obj(payload)
        if str(item.get("sha256", "")) != observed:
            issues.append(f"instance seed={seed} sha256 mismatch")
        if payload["p"] != item.get("p") or payload["n"] != item.get("n"):
            issues.append(f"instance seed={seed} structural field mismatch")
        inst_map[seed] = {
            "payload": payload,
            "sha256_expected": item.get("sha256"),
            "sha256_observed": observed,
            "gen_seconds": gen_seconds,
            "entry": item,
        }

    # Recompute factor-bases.
    for fb in frozen.get("factor_bases", []):
        try:
            seed = int(fb["instance_seed"])
            b_exp = float(fb["b_exp"])
            B = int(fb["B"])
            inst = regen_curves[seed]
            xs = build_factor_base(inst, B, seed=seed)
            observed = sha256_obj({"instance_seed": seed, "b_exp": b_exp, "size": B,
                                  "elements": xs})
            if fb.get("sha256") != observed:
                issues.append(f"factor base seed={seed} b={b_exp} sha256 mismatch")
            if int(fb.get("n_elements", -1)) != len(xs):
                issues.append(f"factor base seed={seed} b={b_exp} count mismatch")
            fb_map[(seed, b_exp)] = {
                "B": B,
                "xs": xs,
                "sha256_expected": fb.get("sha256"),
                "sha256_observed": observed,
                "entry": fb,
            }
        except Exception as exc:
            issues.append(f"factor base parse error: {type(exc).__name__}: {exc}")

    # Recompute target streams.
    for section, tag in [("descent_targets", DESCH_TARGET_TAG), ("harvest_targets", HARV_TARGET_TAG)]:
        for entry in frozen.get("targets", {}).get(section, []):
            try:
                seed = int(entry["instance_seed"])
                count = int(entry["count"])
                inst = regen_curves[seed]
                points = make_targets(inst, tag, count)
                observed = sha256_obj({"instance_seed": seed, "tag": tag,
                                      "count": count, "targets": points})
                if entry.get("sha256") != observed:
                    issues.append(f"target stream {section} seed={seed} sha256 mismatch")
                target_map[(seed, tag)] = {
                    "points": points,
                    "count": count,
                    "sha256_expected": entry.get("sha256"),
                    "sha256_observed": observed,
                    "entry": entry,
                }
            except Exception as exc:
                issues.append(f"target stream parse error {section} seed={entry.get('instance_seed')}:"
                              f" {type(exc).__name__}: {exc}")

    summary = {
        "frozen_verification": {
            "issues": issues,
            "instances_ok": len([k for k in inst_map.keys()
                                if inst_map[k]["sha256_expected"] == inst_map[k]["sha256_observed"]]),
            "factor_bases_ok": len([k for k, v in fb_map.items()
                                   if v["sha256_expected"] == v["sha256_observed"]]),
            "targets_ok": len([k for k, v in target_map.items()
                               if v["sha256_expected"] == v["sha256_observed"]]),
            "n_instances": len(inst_map),
            "n_factor_bases": len(fb_map),
            "n_target_streams": len(target_map),
            "frozen_sha_match": frozen.get("sha256") == frozen_sha_check,
        },
        "instances_by_seed": inst_map,
        "factor_bases_by_seed_b": fb_map,
        "targets_by_seed_tag": target_map,
    }
    return len(issues) == 0, summary["frozen_verification"], summary["instances_by_seed"], summary["factor_bases_by_seed_b"], summary["targets_by_seed_tag"]


@dataclass
class SplitResult:
    found: bool
    checks: int
    timed_out: bool
    decomposition: list[int] | None


def find_decomposition(E: EllipticCurve, points: list[tuple], points_x: list[int],
                      xset: set[int], m: int, target: tuple[int, int],
                      check_cap: int) -> SplitResult:
    checks = 0
    timed_out = False

    def rec(depth: int, current, prefix: list[int]) -> list[int] | None:
        nonlocal checks, timed_out
        if timed_out:
            return None
        if depth == m - 1:
            checks += 1
            if checks > check_cap:
                timed_out = True
                return None
            rest = E.add(target, E.negate(current)) if current is not None else target
            if rest is not None and rest[0] in xset:
                return prefix + [rest[0]]
            return None
        for i, P in enumerate(points):
            nxt = E.add(current, P)
            out = rec(depth + 1, nxt, prefix + [points_x[i]])
            if out is not None:
                return out
        return None

    decomposition = rec(0, None, [])
    return SplitResult(found=(decomposition is not None) and (not timed_out),
                       checks=checks, timed_out=timed_out,
                       decomposition=decomposition)


def run_channel(E: EllipticCurve, full_x: list[int], bkk_x: list[int], m: int,
               targets: list[dict], cap_std: int, cap_bkk: int) -> dict:
    full_point_cache = [E.lift_x(x) for x in full_x]
    bkk_point_cache = [E.lift_x(x) for x in bkk_x]
    full_xset = set(full_x)
    bkk_xset = set(bkk_x)
    full = []
    bkk = []
    for idx, t in enumerate(targets):
        R = (t["x"], t["y"])
        ds = find_decomposition(E, full_point_cache, full_x, full_xset, m, R, cap_std)
        db = find_decomposition(E, bkk_point_cache, bkk_x, bkk_xset, m, R, cap_bkk)
        full.append({"target_index": idx, "target": t, "std": ds.__dict__, "bkk": db.__dict__})
    return {
        "n_targets": len(targets),
        "std_found": sum(1 for r in full if r["std"]["found"]),
        "bkk_found": sum(1 for r in full if r["bkk"]["found"]),
        "std_timed_out": sum(1 for r in full if r["std"]["timed_out"]),
        "bkk_timed_out": sum(1 for r in full if r["bkk"]["timed_out"]),
        "std_checks": [r["std"]["checks"] for r in full],
        "bkk_checks": [r["bkk"]["checks"] for r in full],
        "records": full,
    }


def summarize_channel(label: str, channel: dict) -> dict:
    n = channel["n_targets"]
    std_checks = channel["std_checks"]
    bkk_checks = channel["bkk_checks"]

    std_mean = statistics.mean(std_checks) if std_checks else None
    bkk_mean = statistics.mean(bkk_checks) if bkk_checks else None
    std_median = statistics.median(std_checks) if std_checks else None
    bkk_median = statistics.median(bkk_checks) if bkk_checks else None

    return {
        "label": label,
        "n_targets": n,
        "found": {"std": channel["std_found"], "bkk": channel["bkk_found"]},
        "timed_out": {"std": channel["std_timed_out"], "bkk": channel["bkk_timed_out"]},
        "mean_checks": {"std": std_mean, "bkk": bkk_mean},
        "median_checks": {"std": std_median, "bkk": bkk_median},
    }


def k_star_from_records(channel: dict) -> int | float:
    for i, rec in enumerate(channel["records"], start=1):
        if rec["std"]["found"] and not rec["std"]["timed_out"]:
            return i
    return math.inf


def k_star_bkk_from_records(channel: dict) -> int | float:
    for i, rec in enumerate(channel["records"], start=1):
        if rec["bkk"]["found"] and not rec["bkk"]["timed_out"]:
            return i
    return math.inf


def theorem_index_test(B: int, m: int, trials: int, seed: int) -> dict:
    rng = random.Random(seed)
    hits = 0
    half = B // 2
    for _ in range(trials):
        idx = [rng.randrange(B) for _ in range(m)]
        if sum(1 for v in idx if v < half) >= m - 1:
            hits += 1
    gamma_emp = hits / trials
    gamma_lb = (m + 1) / (2 ** m)
    return {
        "trials": trials,
        "gamma_empirical": gamma_emp,
        "gamma_theory": gamma_lb,
        "passes": gamma_emp >= gamma_lb * THEOREM_TOL,
        "seed": seed,
    }


def run_cell(inst: ECDLPInstance, seed_entry: dict, fb_entry: dict,
             targets_map: dict, m: int, b_exp: float,
             check_cap_std: int, check_cap_bkk: int,
             target_start: int = 0) -> dict:
    E = inst.curve()
    full_x = fb_entry["xs"]
    bkk_x = full_x[:len(full_x) // 2]
    desc_points = targets_map[DESCH_TARGET_TAG]["points"]
    harv_points = targets_map[HARV_TARGET_TAG]["points"]
    targets_desc = desc_points[target_start: target_start + TARGET_COUNT_TARGET]
    targets_harv = harv_points[target_start: target_start + TARGET_COUNT_TARGET]

    harvest = run_channel(E, full_x, bkk_x, m, targets_harv,
                         check_cap_std, check_cap_bkk)
    descent = run_channel(E, full_x, bkk_x, m, targets_desc,
                         check_cap_std, check_cap_bkk)

    # Optional control: matched per-target rho baseline on a small sampled subset.
    rho = {"sampled": 0, "solved": 0, "group_ops": [], "failed": []}
    sample_count = min(len(targets_desc), RHO_SAMPLE_PER_CELL)
    for i in range(sample_count):
        t = targets_desc[i]
        R = (t["x"], t["y"])
        inst_rho = ECDLPInstance(inst.p, inst.a, inst.b, inst.P, R,
                                 inst.n, 0, inst.field_bits, inst.seed)
        out = rho_mod.solve(inst_rho, max_iterations=max(1_000, int(math.sqrt(inst.n)) * 12))
        rho["sampled"] += 1
        rho["group_ops"].append(out.group_operations)
        if out.solved:
            rho["solved"] += 1
        else:
            rho["failed"].append({
                "target_index": i,
                "reason": out.reason,
                "iterations": out.iterations,
            })

    hs = summarize_channel("harvest", harvest)
    ds = summarize_channel("descent", descent)

    k_std = k_star_from_records(descent)
    k_bkk = k_star_bkk_from_records(descent)
    ratio = None
    if k_std not in (math.inf, 0):
        ratio = None if k_bkk == math.inf else (k_bkk / k_std)

    b = len(full_x)
    theo = theorem_index_test(
        b,
        m,
        THEOREM_TRIALS,
        seed=stable_seed(seed_entry["seed"], m, b_exp),
    )

    gamma_emp = descent["bkk_found"] / max(1, descent["n_targets"])
    cell = {
        "curve_seed": int(seed_entry["seed"]),
        "field_bits": inst.field_bits,
        "curve_id": seed_entry["curve_id"],
        "m": m,
        "b_exp": b_exp,
        "factor_base": {"B": b, "half": len(bkk_x)},
        "descent": ds,
        "harvest": hs,
        "K_star_std": k_std,
        "K_star_bkk": k_bkk,
        "ratio_measured": ratio,
        "gamma": {
            "empirical": gamma_emp,
            "theory": theo["gamma_theory"],
            "passes": theo["passes"],
        },
        "theorem_index_test": theo,
        "rho_baseline": rho,
        "cell_checks": {
            "std_checks": {
                "harvest_mean": hs["mean_checks"]["std"],
                "descent_mean": ds["mean_checks"]["std"],
            },
            "bkk_checks": {
                "harvest_mean": hs["mean_checks"]["bkk"],
                "descent_mean": ds["mean_checks"]["bkk"],
            },
        },
        "channel_records": {
            "harvest": harvest["records"],
            "descent": descent["records"],
        },
    }
    return cell


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--frozen", default=FROZEN_PATH, help="path to frozen-instances.yaml")
    ap.add_argument("--out-root", default=None,
                    help="optional override for run output root (usually experiments/<id>)")
    ap.add_argument("--run-suffix", default=RUN_SUFFIX_DEFAULT)
    ap.add_argument("--seeds", default="", help="optional comma-separated seed subset (default: all)")
    ap.add_argument("--cell-ms", default="",
                    help="optional comma-separated m values (default: 3,4,5)")
    ap.add_argument("--b-exps", default="",
                    help="optional comma-separated b exponent values (default: 0.6,0.7)")
    ap.add_argument("--skip-rho", action="store_true",
                    help="skip rho baseline sampling to save wall time")
    ap.add_argument("--check-cap-std", default=str(CHECK_CAP_STD),
                    help="per-target std channel cap (default: 20000)")
    ap.add_argument("--check-cap-bkk", default=str(CHECK_CAP_BKK),
                    help="per-target bkk channel cap (default: 20000)")
    ap.add_argument("--target-offset", default="0",
                    help="index offset into each frozen target stream")
    args = ap.parse_args()

    started = time.time()
    log_out = io.StringIO()
    log_err = io.StringIO()
    t0 = time.time()
    command = "python3 " + " ".join([os.path.relpath(__file__, REPO)] +
                                    [a for a in sys.argv[1:]])
    raw: dict = {}
    status = "completed"
    valid = True
    invalid_reason = None
    debug = os.environ.get("MTBK_FULL_DEBUG", "0") == "1"

    try:
        if debug:
            print(f"[EXP-MTBK-306bdb] debug mode enabled (MTBK_FULL_DEBUG=1)")
        if debug:
            out_ctx = redirect_stdout(sys.stdout)
            err_ctx = redirect_stderr(sys.stderr)
        else:
            out_ctx = redirect_stdout(log_out)
            err_ctx = redirect_stderr(log_err)
        with out_ctx, err_ctx:
            frozen = read_frozen(args.frozen)
            print(f"[EXP-MTBK-306bdb] loaded frozen file: {args.frozen}")
            ok, frozen_verification, inst_map, fb_map, target_map = verify_frozen(frozen)
            print("[EXP-MTBK-306bdb] frozen verification ok:", ok)
            if not ok:
                raise HarnessFailure("frozen verification failed")

            raw["frozen"] = {
                "file": args.frozen,
                "sha256": frozen.get("sha256"),
                "verification": frozen_verification,
            }

            requested_seeds = {int(s.strip()) for s in args.seeds.split(",") if s.strip()}
            requested_ms = [int(v.strip()) for v in args.cell_ms.split(",") if v.strip()]
            if not requested_ms:
                requested_ms = CELL_MS
            requested_b = [float(v.strip()) for v in args.b_exps.split(",") if v.strip()]
            if not requested_b:
                requested_b = CELL_B_EXP

            try:
                check_cap_std = int(args.check_cap_std)
                check_cap_bkk = int(args.check_cap_bkk)
            except ValueError:
                raise HarnessFailure("check caps must be integers")
            if check_cap_std < 1 or check_cap_bkk < 1:
                raise HarnessFailure("check caps must be positive")

            try:
                target_offset = int(args.target_offset)
            except ValueError:
                raise HarnessFailure("target-offset must be an integer")
            if target_offset < 0:
                raise HarnessFailure("target-offset must be nonnegative")

            active_seeds = sorted(requested_seeds.intersection(inst_map.keys()) if requested_seeds else inst_map.keys())
            if not active_seeds:
                raise HarnessFailure(f"no active seeds after filtering; requested: {sorted(requested_seeds)}")

            # Build cell list from frozen seeds and factors.
            cells = []
            for seed in active_seeds:
                inst_payload = inst_map[seed]["entry"]
                inst, _ = regen_curve(inst_payload)
                for m in requested_ms:
                    for b_exp in requested_b:
                        if (seed, b_exp) not in fb_map:
                            raise HarnessFailure(f"missing factor base seed={seed}, b={b_exp}")
                        targets_by_tag = {}
                        for sect_tag in [DESCH_TARGET_TAG, HARV_TARGET_TAG]:
                            key = (seed, sect_tag)
                            if key not in target_map:
                                raise HarnessFailure(f"missing target stream seed={seed}, tag={sect_tag}")
                            section = "descent_targets" if sect_tag == DESCH_TARGET_TAG else "harvest_targets"
                            if target_map[key]["count"] < TARGET_COUNT_TARGET:
                                raise HarnessFailure(f"target stream {section} seed={seed} too small")
                            if target_offset + TARGET_COUNT_TARGET > target_map[key]["count"]:
                                raise HarnessFailure(
                                    f"target stream {section} seed={seed} lacks "
                                    f"{TARGET_COUNT_TARGET} targets from offset {target_offset}"
                                )
                            targets_by_tag[section] = target_map[key]

                        print(f"[cell] seed={seed} m={m} b={b_exp}")
                        targets_by_tag = {
                            DESCH_TARGET_TAG: targets_by_tag["descent_targets"],
                            HARV_TARGET_TAG: targets_by_tag["harvest_targets"],
                        }
                        cell = run_cell(inst, inst_payload, fb_map[(seed, b_exp)],
                                       targets_by_tag,
                                       m, b_exp, check_cap_std, check_cap_bkk,
                                       target_start=target_offset)
                        cells.append(cell)

            # Optional drop channel records if too large to keep a focused raw.
            # Keep full records for reproducibility on this run.

            # Post-aggregate: mean checks across all cells for requested metrics.
            srel_std = []
            srel_bkk = []
            tdesc_std = []
            tdesc_bkk = []
            ratios = []
            for c in cells:
                srel_std.append(c["cell_checks"]["std_checks"]["harvest_mean"])
                srel_bkk.append(c["cell_checks"]["bkk_checks"]["harvest_mean"])
                tdesc_std.append(c["cell_checks"]["std_checks"]["descent_mean"])
                tdesc_bkk.append(c["cell_checks"]["bkk_checks"]["descent_mean"])
                if c["ratio_measured"] is not None and not math.isinf(c["ratio_measured"]):
                    ratios.append(c["ratio_measured"])

            raw["cells"] = cells
            raw["metrics"] = {
                "S_rel_std_full_checks": statistics.median(srel_std) if srel_std else None,
                "S_rel_bkk_full_checks": statistics.median(srel_bkk) if srel_bkk else None,
                "T_desc_std_full_checks": statistics.median(tdesc_std) if tdesc_std else None,
                "T_desc_bkk_full_checks": statistics.median(tdesc_bkk) if tdesc_bkk else None,
                "ratio_median": statistics.median(ratios) if ratios else None,
                "ratio_samples": len(ratios),
            }
            raw["run_summary"] = {
                "cells_total": len(cells),
                "cells_ok": len(cells),
                "parameters": {
                    "cell_ms": requested_ms,
                    "cell_b": requested_b,
                    "check_cap_std": check_cap_std,
                    "check_cap_bkk": check_cap_bkk,
                    "target_offset": target_offset,
                    "theorem_trials": THEOREM_TRIALS,
                    "seeds": active_seeds,
                },
            }
            raw["code_hashes"] = {
                "code/run_mtbk_full.py": sha256_file(__file__),
                "harness/toycurve.py": sha256_file(os.path.join(REPO, "harness", "toycurve.py")),
                "harness/semaev.py": sha256_file(os.path.join(REPO, "harness", "semaev.py")),
                "harness/rho.py": sha256_file(os.path.join(REPO, "harness", "rho.py")),
                "harness/runner.py": sha256_file(os.path.join(REPO, "harness", "runner.py")),
            }
            raw["policy"] = {
                "requested": "executor-implementation",
                "resolved_model": None,
                "reasoning_effort": None,
                "fallback_used": False,
                "adapter_note": "harness deterministic execution",
            }
    except Exception as exc:
        status = "failed_infrastructure"
        valid = False
        invalid_reason = f"{type(exc).__name__}: {exc}"
        raw = {
            "invalid_reason": invalid_reason,
            "traceback": traceback.format_exc(),
        }
        if debug:
            print(f"[FAIL] {invalid_reason}")
            print(raw["traceback"])
        else:
            with redirect_stdout(log_out), redirect_stderr(log_err):
                print(f"[FAIL] {invalid_reason}")
        return 1

    # Write run artifact --------------------------------------------------
    elapsed = time.time() - started
    usage = resource.getrusage(resource.RUSAGE_SELF)
    cpu_seconds = usage.ru_utime + usage.ru_stime
    if platform.system() != "Linux":
        peak_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    else:
        peak_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024

    if args.skip_rho:
        raw.setdefault("note", "rho baseline skipped by --skip-rho")

    rr = RunResult(
        run_suffix=args.run_suffix,
        curve_id=(
            inst_map[sorted(inst_map.keys())[0]]["entry"]["curve_id"]
            if inst_map else "TOY-P16-MTBK-MULTI"
        ),
        seed=min(inst_map.keys()) if inst_map else 1,
        parameters={
            "run_suffix": args.run_suffix,
            "cell_ms": requested_ms,
            "cell_b_exp": requested_b,
            "seed_filter": active_seeds,
            "target_count_per_batch": TARGET_COUNT_TARGET,
            "check_caps": {"std": check_cap_std, "bkk": check_cap_bkk},
            "target_offset": target_offset,
            "theorem_trials": THEOREM_TRIALS,
            "rho_sample_per_cell": RHO_SAMPLE_PER_CELL,
            "skip_rho": args.skip_rho,
        },
        metrics={
            "wall_clock_seconds": elapsed,
            "memory_mb": round(peak_rss / (1024 ** 2), 6),
            "cpu_seconds": cpu_seconds,
            **(raw.get("metrics", {})),
        },
        certificate={
            "kind": "none",
            "statement": {
                "kind": "exp-mtbk-full-harness",
                "scope": "full grid, frozen protocol",
                "seed_set": [1, 2, 3, 4, 5],
                "ms": CELL_MS,
                "b_exps": CELL_B_EXP,
                "note": "No per-target claim certificates are emitted for measurement channels.",
            },
        },
        valid=valid,
        invalid_reason=invalid_reason,
        stdout=log_out.getvalue(),
        stderr=log_err.getvalue(),
        raw=raw,
    )

    run_id = write_run(EXP_ID, EXP_AREA, rr, status=status,
                       command=command, started=started, finished=time.time(),
                       out_root=args.out_root)
    duration = time.time() - t0
    print(json.dumps({"run_id": run_id, "status": status, "duration_s": duration,
                      "valid": valid}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
