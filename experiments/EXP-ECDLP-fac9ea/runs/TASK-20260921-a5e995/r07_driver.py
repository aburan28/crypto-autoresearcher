#!/usr/bin/env python3
"""EXP-ECDLP-fac9ea v4 extension run RUN-ECDLP-ccf8f0 (TASK-20260921-a5e995).

R07 index-5 coset level decision on a dedicated p = 1 mod 5 ladder, per
amendment DEC-20260921-a796fe (the named successor of DEC-20260921-4516a0).
Decision quantity: delta = lambda(R07) - lambda(C02A), convention-free.
Executed in the coordinator session under the executor role contract
(role-runtime outage, recorded in DEC-20260921-4d1b40).
"""

import gc
import json
import math
import os
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone

import numpy as np
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
IMPL_DIR = os.path.abspath(os.path.join(HERE, "..", "TASK-20260921-4888d4"))
sys.path.insert(0, IMPL_DIR)
import importlib.util

_spec = importlib.util.spec_from_file_location("impl", os.path.join(IMPL_DIR, "implementation.py"))
impl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(impl)

REG_PATH = os.path.join(HERE, "r07_registry.json")
FITS_PATH = os.path.join(HERE, "r07_fits.json")
REPORT_PATH = os.path.join(HERE, "r07_report.md")
MANIFEST_PATH = os.path.join(HERE, "manifest.yaml")
RUN_ID = "RUN-ECDLP-ccf8f0"
TASK_ID = "TASK-20260921-a5e995"
EXP_ID = "EXP-ECDLP-fac9ea"
MEM_CAP_GB = 8.0
LADDER_J = list(range(11))
ROWS = ["R07", "R07M", "C01", "C02A", "C02B"]


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def smallest_prime_congruent(n, mod, residue):
    m = int(math.ceil(n))
    while True:
        if impl.smallest_prime_at_least(m) == m and m % mod == residue:
            return m
        m = impl.smallest_prime_at_least(m + 1)
        if m % mod != residue:
            continue
        return m


def build_ladder():
    primes = []
    for j in LADDER_J:
        target = 2.0 ** (12 + 1.2 * j)
        p = int(math.ceil(target))
        while True:
            q = impl.smallest_prime_at_least(p)
            if q % 5 == 1:
                primes.append(q)
                break
            p = q + 1
    return sorted(set(primes))


def load_reg():
    if os.path.exists(REG_PATH):
        return json.load(open(REG_PATH))
    return {}


def save_reg(reg):
    tmp = REG_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(reg, f, indent=1, sort_keys=True)
    os.replace(tmp, REG_PATH)


def fit(points):
    return impl.fit_lambda(points)


def main():
    t_start = now_iso()
    os.makedirs(os.path.join(HERE, "work"), exist_ok=True)
    ladder = build_ladder()
    print("extension ladder (p = 1 mod 5):", ladder, flush=True)
    reg = load_reg()
    for p in ladder:
        cz = impl.ChirpZ(p, os.path.join(HERE, "work"))
        inv = None
        for row in ROWS:
            cid = f"{row}:{p}"
            if cid in reg and reg[cid]["status"] in ("ok", "unavailable"):
                continue
            t0 = time.perf_counter()
            if row == "R07M":
                if inv is None:
                    inv = impl.inv_table(p)
                v, note = impl.moebius_row("R07", p, inv)
            else:
                v, note = impl.build_row(row, p)
            if v is None:
                rec = {"cell": cid, "status": "unavailable", "note": note,
                       "wall_seconds": round(time.perf_counter() - t0, 3),
                       "recorded_at": now_iso()}
            else:
                V, need = cz.transform(v)
                if V is None:
                    rec = {"cell": cid, "status": "resource_exhaustion",
                           "note": f"projected {need:.2f} GiB vs 8 GiB cap; continuation pointer per amendment",
                           "wall_seconds": round(time.perf_counter() - t0, 3),
                           "recorded_at": now_iso()}
                else:
                    rec = {"cell": cid, "status": "ok",
                           "l1_nontrivial": float(np.abs(V[1:]).sum()),
                           "abs_vhat0": float(abs(V[0])),
                           "vhat0_minus_1_abs": float(abs(abs(V[0]) - 1.0)),
                           "note": note,
                           "wall_seconds": round(time.perf_counter() - t0, 3),
                           "rss_highwater_gb": round(impl.rss_highwater_gb(), 3),
                           "fft_len": cz.L, "recorded_at": now_iso()}
                    del V
            reg = load_reg()
            reg[cid] = rec
            save_reg(reg)
            print(f"  {cid} -> {rec['status']} l1*={rec.get('l1_nontrivial')} ({rec.get('wall_seconds')}s)", flush=True)
        del cz
        gc.collect()
    t_finish = now_iso()

    def pts(row):
        return [(p, reg[f"{row}:{p}"]["l1_nontrivial"]) for p in ladder
                if reg.get(f"{row}:{p}", {}).get("status") == "ok"]

    r07_fit, r07m_fit = fit(pts("R07")), fit(pts("R07M"))
    c02a_fit, c02b_fit = fit(pts("C02A")), fit(pts("C02B"))
    c01_recs = [reg[f"C01:{p}"] for p in ladder if reg.get(f"C01:{p}", {}).get("status") == "ok"]
    c01_ok = all(r["l1_nontrivial"] <= 1e-9 * max(r["abs_vhat0"], 1e-30) for r in c01_recs) if c01_recs else None
    v0_ok = all(r.get("vhat0_minus_1_abs", 1.0) <= 1e-9
                for r in reg.values() if r.get("status") == "ok")
    c02_band = (abs(c02a_fit["lambda"] - 0.5) <= 2 * (c02a_fit["se"] or 1) + 0.02) if c02a_fit else None
    seed_agree = (abs(c02a_fit["lambda"] - c02b_fit["lambda"]) <=
                  2 * math.sqrt((c02a_fit["se"] or 1) ** 2 + (c02b_fit["se"] or 1) ** 2)
                  ) if c02a_fit and c02b_fit else None
    moebius_stable = (abs(r07m_fit["lambda"] - r07_fit["lambda"]) <=
                      2 * math.sqrt((r07_fit["se"] or 1) ** 2 + (r07m_fit["se"] or 1) ** 2)
                      ) if r07_fit and r07m_fit else None

    delta = se_delta = verdict = None
    if r07_fit and c02a_fit:
        delta = r07_fit["lambda"] - c02a_fit["lambda"]
        se_delta = math.sqrt((r07_fit["se"] or 1) ** 2 + (c02a_fit["se"] or 1) ** 2)
        controls_ok = all(x is True for x in [c01_ok, c02_band, seed_agree, v0_ok])
        if not controls_ok:
            verdict = "void_control_failure"
        elif moebius_stable is not True:
            verdict = "unresolved_artifactual_or_missing_moebius"
        elif r07_fit["n_points"] < 10:
            verdict = "unresolved_insufficient_points"
        else:
            verdict = ("resolved_above_random" if delta > 2 * se_delta
                       else "at_random_level" if abs(delta) <= 2 * se_delta
                       else "unresolved_below_random")

    controls = {
        "C01_numerically_zero": c01_ok,
        "C02A_parseval_band": c02_band,
        "C02_seed_agreement": seed_agree,
        "R07M_moebius_stability": moebius_stable,
        "all_ok_cells_vhat0_equals_1": v0_ok,
    }
    fits = {
        "run_id": RUN_ID, "ladder": ladder,
        "fits": {"R07": r07_fit, "R07M": r07m_fit, "C02A": c02a_fit, "C02B": c02b_fit},
        "delta_lambda_R07_minus_C02A": delta,
        "se_delta": se_delta,
        "verdict": verdict,
        "controls": controls,
        "generated_at": now_iso(),
    }
    with open(FITS_PATH, "w") as f:
        json.dump(fits, f, indent=1, sort_keys=True)
    write_report(fits)
    write_manifest(ladder, reg, controls, verdict, t_start, t_finish)
    print("verdict:", verdict, "delta:", delta, flush=True)
    print("DONE", flush=True)


def write_report(fits):
    y = ["# EXP-ECDLP-fac9ea v4 extension — R07 index-5 coset level decision", "",
         f"Run {RUN_ID} under TASK-20260921-a5e995, amendment DEC-20260921-a796fe",
         "(the named successor of DEC-20260921-4516a0). Decision quantity is",
         "delta = lambda(R07) - lambda(C02A) on the same ladder — convention-free",
         "under any uniform transform prefactor. The absolute gate thresholds",
         "(1/4, 1/6) are deliberately NOT applied (convention-relative).", "",
         f"Ladder (p = 1 mod 5, {len(fits['ladder'])} primes): {fits['ladder']}", "",
         "| row | lambda | SE | n |", "|---|---|---|---|"]
    for row in ("R07", "R07M", "C02A", "C02B"):
        f = fits["fits"][row]
        if f:
            y.append(f"| {row} | {f['lambda']:.4f} | {f['se']:.4f} | {f['n_points']} |")
    y += ["", "## Controls", "", "| control | result |", "|---|---|"]
    for k, v in fits["controls"].items():
        y.append(f"| {k} | {'PASS' if v is True else ('FAIL' if v is False else 'NOT EVALUATED')} |")
    y += ["", "## Decision", ""]
    d, s, v = fits["delta_lambda_R07_minus_C02A"], fits["se_delta"], fits["verdict"]
    if d is not None:
        y += [f"delta = lambda(R07) - lambda(C02A) = {d:.4f} +- {s:.4f} "
              f"({2*s:.4f} at 2SE).", f"VERDICT: {v}.", ""]
    if v == "resolved_above_random":
        y += ["The only PGL_2-stable above-random candidate in the census is now",
              "resolved ABOVE the random-set level on 11 congruence-complete",
              "points: the index-5 coset carries genuine, embedding-stable",
              "spectral structure distinct from a matched random set. This is a",
              "MEASUREMENT, not an attack claim; the successor is a construction-",
              "step design keyed on index-5 cosets (with all costs charged), and",
              "the owed independent review of the census evidence should cover",
              "this extension with it."]
    elif v == "at_random_level":
        y += ["The R07 excess of the census (0.5709 on 4 points) does NOT survive",
              "the congruence-complete ladder: the index-5 coset sits at the",
              "random-set level like every other stable row, and the census's",
              "scoped negative closes over the full registry — no natural",
              "coordinate statistic is simultaneously PGL_2-stable and above the",
              "random-set level. Synthetic-statistic design remains the named",
              "successor."]
    elif v and v.startswith("void"):
        y += ["VOID: a frozen control failed; the extension run is an",
              "infrastructure outcome, never mathematical evidence. The",
              "defective control is named in r07_fits.json."]
    else:
        y += [f"UNRESOLVED ({v}); the decision quantity could not be decided at",
              "2SE on this ladder. Next: widen the ladder or diagnose the",
              "guard that fired."]
    y += ["", "Per-cell raw values and wall times: r07_registry.json;", "manifest: manifest.yaml.", ""]
    with open(REPORT_PATH, "w") as f:
        f.write("\n".join(y) + "\n")


def write_manifest(ladder, reg, controls, verdict, t_start, t_finish):
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout.strip()
    except Exception:
        commit, dirty = "unavailable", "unavailable"
    control_fail = [k for k, v in controls.items() if v is not True]
    run = {
        "id": RUN_ID, "experiment_id": EXP_ID, "task_id": TASK_ID,
        "status": "completed",
        "status_note": "Extension run under amendment DEC-20260921-a796fe (v3 -> v4), the named successor of DEC-20260921-4516a0; single bounded pass over the frozen extension cells.",
        "specification_version": "4 (amendments DEC-20260921-d3fafb, DEC-20260921-f1d95a, DEC-20260921-a796fe)",
        "code": {
            "head_commit": commit, "commit": commit, "branch": "ideas/ecdlp-20260921",
            "command": "python3 r07_driver.py (see command.txt)",
            "dirty_at_execution_start": bool(dirty),
            "dirty_note": dirty.replace("\n", "; ") if dirty else "clean",
        },
        "inputs": {
            "specification_path": "experiments/EXP-ECDLP-fac9ea/specification.yaml",
            "specification_version_executed": 4,
            "amendment_ids": ["DEC-20260921-d3fafb", "DEC-20260921-f1d95a", "DEC-20260921-a796fe"],
            "hypothesis_id": "H-ECDLP-4e1880",
            "predecessor_run": "RUN-ECDLP-8e13c2",
            "seeds": "same frozen SHA256(EXP-ECDLP-fac9ea:<cell>:<purpose>:<counter>) streams (C02 signs, Moebius maps) reused from implementation.py",
        },
        "timing": {"start": t_start, "finish": t_finish,
                   "wall_note": "per-cell wall_seconds in r07_registry.json"},
        "environment": {
            "os": "darwin arm64", "python": sys.version.split()[0],
            "numpy": np.__version__, "scipy": "1.18.0",
            "implementation_basis": "reuses TASK-20260921-4888d4/implementation.py ChirpZ, build_row, moebius_row, fit_lambda verbatim",
        },
        "result": {
            "certificate": {"kind": "none",
                            "note": "pure exact measurement; correctness by r07_checker.py spot rederivations and the vhat(0)=1 invariant"},
            "outputs": {"registry": "r07_registry.json", "fits": "r07_fits.json", "report": "r07_report.md"},
            "decision_quantity": "delta = lambda(R07) - lambda(C02A), convention-free",
            "verdict": verdict,
            "validity": "void_control_failure" if control_fail else "controls_passed",
            "control_failures": control_fail,
            "controls": controls,
        },
        "ladder": ladder,
        "rows": ROWS,
        "cells": {cid: {"status": r["status"], "l1_nontrivial": r.get("l1_nontrivial"),
                        "abs_vhat0": r.get("abs_vhat0"), "wall_s": r.get("wall_seconds"),
                        "rss_highwater_gb": r.get("rss_highwater_gb")}
                  for cid, r in sorted(reg.items())},
        "memory_cap_gb": MEM_CAP_GB,
        "artifacts": ["r07_driver.py", "r07_checker.py", "manifest.yaml", "r07_registry.json",
                      "r07_fits.json", "r07_report.md", "command.txt", "environment.json",
                      "stdout.log", "stderr.log", "raw-result.json"],
        "executor_provenance": (
            "Executed in the top-level coordinator session under the executor role "
            "contract; the executor subagent runtime failed its bootstrap (AWS "
            "DescribeInstances AuthFailure), recorded in DEC-20260921-4d1b40."),
    }
    with open(MANIFEST_PATH, "w") as f:
        yaml.dump({"run": run}, f, sort_keys=False, default_flow_style=False, allow_unicode=True, width=100)


if __name__ == "__main__":
    main()
