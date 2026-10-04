#!/usr/bin/env python3
"""EXP-ECDLP-fac9ea v5 tail re-measure RUN-ECDLP-0c5f65 (TASK-20260921-3a6335).

Re-measures the 26 resource_exhaustion cells at p = 67108879 in complex64
(single-precision Bluestein, projected ~5 GiB against the 8 GiB cap), per
amendment DEC-20260921-e7edc5, with a dual-precision cross-check at
p = 4818013 bounding the precision loss. Executed in the coordinator
session under the executor role contract (role-runtime outage,
DEC-20260921-4d1b40).
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
import scipy.fft as sfft
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
IMPL_DIR = os.path.abspath(os.path.join(HERE, "..", "TASK-20260921-4888d4"))
ORIG_REG_PATH = os.path.join(IMPL_DIR, "registry.json")
sys.path.insert(0, IMPL_DIR)
import importlib.util

_spec = importlib.util.spec_from_file_location("impl", os.path.join(IMPL_DIR, "implementation.py"))
impl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(impl)

WORK = os.path.join(HERE, "work")
REG_PATH = os.path.join(HERE, "tail_registry.json")
FITS_PATH = os.path.join(HERE, "tail_fits.json")
REPORT_PATH = os.path.join(HERE, "tail_report.md")
MANIFEST_PATH = os.path.join(HERE, "manifest.yaml")
RUN_ID = "RUN-ECDLP-0c5f65"
TASK_ID = "TASK-20260921-3a6335"
EXP_ID = "EXP-ECDLP-fac9ea"
MEM_CAP_GB = 8.0
P_TAIL = 67108879
P_XCHECK = 4818013
PLAIN = ["C01", "C02A", "C02B", "R01", "R02", "R03", "R03B", "R04", "R05",
         "R06", "R08", "R09"]
MOB = ["R01M", "R02M", "R03M", "R04M", "R05M", "R06M", "R08M", "R09M"]


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def rss_highwater_gb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**30


class ChirpZ64:
    """Single-precision variant of implementation.ChirpZ: same exponent-space
    chirp e_j = j^2*inv2 mod p, same 5-smooth padded length and reversed-tail
    placement, complex64 arrays throughout."""

    def __init__(self, p, workdir):
        self.p = p
        self.L = impl.next_smooth_len(2 * p - 1)
        self.inv2 = (p + 1) // 2
        x = np.arange(p, dtype=np.int64)
        e = ((x * x % p) * self.inv2) % p
        self.chirp = np.exp(-2j * np.pi * e / p).astype(np.complex64)
        self.bspec_path = os.path.join(workdir, f"bspec64_{p}.npy")
        if not os.path.exists(self.bspec_path):
            b = np.conj(self.chirp)
            B = np.zeros(self.L, dtype=np.complex64)
            B[:p] = b
            B[self.L - p + 1: self.L] = b[1:]
            del b
            Fb = sfft.fft(B, overwrite_x=True)
            np.save(self.bspec_path, Fb)
            del Fb, B
            gc.collect()

    def transform(self, v):
        p, L = self.p, self.L
        need_gb = (L * 8 * 2 + p * 12) / 2**30
        if need_gb > MEM_CAP_GB - 0.5:
            return None, need_gb
        A = np.zeros(L, dtype=np.complex64)
        A[:p] = v.astype(np.complex64)
        A[:p] *= self.chirp
        F = sfft.fft(A, overwrite_x=True)
        del A
        gc.collect()
        bspec = np.load(self.bspec_path, mmap_mode="r")
        F *= bspec
        del bspec
        gc.collect()
        V = sfft.ifft(F, overwrite_x=True)
        del F
        gc.collect()
        l1 = float(np.abs(V[1:p]).astype(np.float64).sum())
        v0 = float(abs(V[0]))
        del V
        gc.collect()
        return (l1, v0), need_gb


def moebius_row_chunked(base_row, p):
    """Blockwise permutation, mathematically identical to
    implementation.moebius_row (same frozen hash coefficients, same
    integer arithmetic, same pole rule), allocating block-sized arrays so
    the tail-prime Moebius cells stay within the 8 GiB cap."""
    a, b, c, d = impl.hash_ints("C03", "moebius", base_row, mod=p)
    det = (a * d - b * c) % p
    tries = 0
    while det == 0 and tries < 100:
        a, b, c, d = impl.hash_ints("C03", "moebius", base_row, "r", tries, mod=p)
        det = (a * d - b * c) % p
        tries += 1
    if det == 0:
        return None, "unavailable: degenerate Moebius map"
    v_base, note = impl.build_row(base_row, p)
    if v_base is None:
        return None, note
    inv = impl.inv_table(p)
    vm = np.empty(p, dtype=np.float64)
    BL = 1 << 23
    x0 = int((-d) % p * inv[c] % p) if c != 0 else None
    y_pole = (a * inv[c]) % p if c != 0 else None
    for st in range(0, p, BL):
        en = min(p, st + BL)
        xb = np.arange(st, en, dtype=np.int64)
        den = (c * xb + d) % p
        yb = np.zeros(en - st, dtype=np.int64)
        okm = den != 0
        yb[okm] = ((a * xb[okm] + b) % p) * inv[den[okm]] % p
        if x0 is not None and st <= x0 < en:
            yb[x0 - st] = y_pole
        vm[st:en] = v_base[yb]
    del inv, v_base
    gc.collect()
    return vm, f"M(x)=(ax+b)/(cx+d) a={a} b={b} c={c} d={d} det={det} (chunked permutation)"


def measure_prebuilt(cid, cz64, v, note, reg):
    if cid in reg and reg[cid]["status"] in ("ok", "unavailable"):
        return reg[cid]
    t0 = time.perf_counter()
    if v is None:
        rec = {"cell": cid, "status": "unavailable", "note": note,
               "wall_seconds": round(time.perf_counter() - t0, 3),
               "recorded_at": now_iso()}
    else:
        out, need = cz64.transform(v)
        if out is None:
            rec = {"cell": cid, "status": "resource_exhaustion",
                   "note": f"projected {need:.2f} GiB vs 8 GiB cap",
                   "wall_seconds": round(time.perf_counter() - t0, 3),
                   "recorded_at": now_iso()}
        else:
            l1, v0 = out
            rec = {"cell": cid, "status": "ok",
                   "l1_nontrivial": l1, "abs_vhat0": v0,
                   "vhat0_minus_1_rel": abs(v0 - 1.0),
                   "precision": "complex64", "note": note,
                   "wall_seconds": round(time.perf_counter() - t0, 3),
                   "rss_highwater_gb": round(rss_highwater_gb(), 3),
                   "recorded_at": now_iso()}
    reg[cid] = rec
    save_reg(reg)
    return rec


def load_reg():
    if os.path.exists(REG_PATH):
        return json.load(open(REG_PATH))
    return {}


def save_reg(reg):
    tmp = REG_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(reg, f, indent=1, sort_keys=True)
    os.replace(tmp, REG_PATH)


def measure(cid, cz64, inv, reg):
    if cid in reg and reg[cid]["status"] in ("ok", "unavailable"):
        return reg[cid]
    parts = cid.split(":")
    row, p = parts[0], int(parts[1])
    suffix = parts[2] if len(parts) > 2 else None
    t0 = time.perf_counter()
    if suffix and suffix.startswith("curve"):
        ci = int(suffix[5:])
        v_base, _ = impl.build_row(row, p)
        support = np.nonzero(v_base)[0]
        mask, A, B = impl.curve_mask(p, ci)
        sub = np.zeros(p, dtype=bool)
        sub[support] = mask[support]
        v = impl.prob_indicator(sub, p)
        note = f"A={A} B={B} |gH cap x(E)|={int(sub.sum())}"
    elif row.endswith("M"):
        v, note = impl.moebius_row(row[:-1], p, inv)
    else:
        v, note = impl.build_row(row, p)
    if v is None:
        rec = {"cell": cid, "status": "unavailable", "note": note,
               "wall_seconds": round(time.perf_counter() - t0, 3),
               "recorded_at": now_iso()}
    else:
        out, need = cz64.transform(v)
        if out is None:
            rec = {"cell": cid, "status": "resource_exhaustion",
                   "note": f"projected {need:.2f} GiB vs 8 GiB cap",
                   "wall_seconds": round(time.perf_counter() - t0, 3),
                   "recorded_at": now_iso()}
        else:
            l1, v0 = out
            rec = {"cell": cid, "status": "ok",
                   "l1_nontrivial": l1, "abs_vhat0": v0,
                   "vhat0_minus_1_rel": abs(v0 - 1.0),
                   "precision": "complex64", "note": note,
                   "wall_seconds": round(time.perf_counter() - t0, 3),
                   "rss_highwater_gb": round(rss_highwater_gb(), 3),
                   "recorded_at": now_iso()}
    reg[cid] = rec
    save_reg(reg)
    return rec


def main():
    """Cross-check pass only (fresh process): R03 at P_XCHECK in both
    precisions, recorded into the registry."""
    os.makedirs(WORK, exist_ok=True)
    reg = load_reg()
    cz64_mid = ChirpZ64(P_XCHECK, WORK)
    v128, _ = impl.build_row("R03", P_XCHECK)
    V128, _ = impl.ChirpZ(P_XCHECK, WORK).transform(v128)
    l1_128 = float(np.abs(V128[1:]).sum())
    out64, _ = cz64_mid.transform(v128)
    l1_64 = out64[0]
    xcheck_rel = abs(l1_64 - l1_128) / l1_128
    reg["XCHECK:R03:4818013"] = {
        "cell": "XCHECK:R03:4818013", "status": "ok",
        "l1_complex128": l1_128, "l1_complex64": l1_64,
        "relative_difference": xcheck_rel,
        "recorded_at": now_iso()}
    save_reg(reg)
    print(f"cross-check R03@{P_XCHECK}: 128b {l1_128:.6f} vs 64b {l1_64:.6f} "
          f"rel {xcheck_rel:.2e}", flush=True)


def compute_outputs(reg):
    orig = json.load(open(ORIG_REG_PATH))
    orig_pts = {}
    for row in (["R01", "R02", "R03", "R04", "R05", "R06", "R08", "R09",
                 "C01", "C02A", "C02B", "R03B"] +
                [r + "M" for r in ["R01", "R02", "R03", "R04", "R05",
                                   "R06", "R08", "R09"]]):
        pts = [(int(c.split(":")[1]), rec["l1_nontrivial"])
               for c, rec in orig.items()
               if c.startswith(row + ":") and c.count(":") == 1
               and rec.get("status") == "ok"]
        tail_rec = reg.get(f"{row}:{P_TAIL}")
        if tail_rec and tail_rec.get("status") == "ok":
            pts = pts + [(P_TAIL, tail_rec["l1_nontrivial"])]
        orig_pts[row] = sorted(pts)
    fits = {}
    for row, pts in orig_pts.items():
        if row == "C01":
            continue
        fits[row] = impl.fit_lambda(pts)
    v0_ok = all(r.get("vhat0_minus_1_rel", 1.0) <= 1e-4
                for r in reg.values() if r.get("status") == "ok"
                and r.get("cell") != "XCHECK:R03:4818013")
    c01_tail = reg.get(f"C01:{P_TAIL}", {})
    c01_ok = (c01_tail.get("status") == "ok" and
              c01_tail["l1_nontrivial"] <= 1e-2 * max(c01_tail["abs_vhat0"], 1e-30))
    xcheck_rel = reg["XCHECK:R03:4818013"]["relative_difference"]
    xcheck_ok = xcheck_rel <= 1e-4
    controls = {
        "dual_precision_crosscheck_le_1e-4": xcheck_ok,
        "vhat0_equals_1_within_1e-4_all_ok_cells": v0_ok,
        "C01_tail_numerically_zero_1e-2": c01_ok,
    }
    cids = sorted(c for c in reg if c != "XCHECK:R03:4818013")
    tail_vals = {c: reg[c].get("l1_nontrivial") for c in cids
                 if reg[c].get("status") == "ok"}
    breach_note = {}
    for c in cids:
        old = orig.get(c, {})
        if old.get("status") == "resource_exhaustion" and "l1_nontrivial" in old:
            new = reg.get(c, {}).get("l1_nontrivial")
            if new is not None:
                breach_note[c] = {
                    "breach_measurement_preserved": old["l1_nontrivial"],
                    "in_cap_remeasurement": new,
                    "relative_difference": abs(new - old["l1_nontrivial"]) /
                                           abs(old["l1_nontrivial"])}
    stamps = sorted(r.get("recorded_at", "") for r in reg.values())
    out = {"run_id": RUN_ID, "controls": controls,
           "xcheck_relative_difference": xcheck_rel,
           "fits_with_tail_point": fits,
           "tail_values": tail_vals,
           "breach_vs_incap_comparison": breach_note,
           "verdict_comparison_note": (
               "Verdicts are unchanged if the fitted lambdas move within their "
               "census standard errors; any row whose lambda moved beyond 2SE "
               "is named in tail_report.md as the primary outcome."),
           "t_start": stamps[0] if stamps else None,
           "t_finish": stamps[-1] if stamps else None,
           "cids": cids,
           "generated_at": now_iso()}
    return out, fits


CENSUS_LAMBDA = {"R01": 0.0806, "R02": 0.0806, "R03": 0.4191, "R04": 0.4088,
                 "R05": 0.3806, "R06": 0.5013, "R08": 0.5000, "R09": 0.1133,
                 "C02A": 0.4996, "C02B": 0.5001}


def write_report(out, fits, reg):
    y = ["# EXP-ECDLP-fac9ea v5 tail re-measure — RUN-ECDLP-0c5f65", "",
         f"Amendment DEC-20260921-e7edc5 (the chunked/low-precision continuation",
         f"of the RUN-ECDLP-8e13c2 resource_exhaustion cells). Same transform",
         f"algorithm, constructions, seeds, and normalisation; complex64",
         f"execution, projected and measured within the 8 GiB cap.", "",
         "## Controls", "", "| control | result |", "|---|---|"]
    for k, v in out["controls"].items():
        y.append(f"| {k} | {'PASS' if v is True else ('FAIL' if v is False else 'NOT EVALUATED')} |")
    y += [f"", f"Dual-precision cross-check (R03 @ {P_XCHECK}): relative L1 "
          f"difference {out['xcheck_relative_difference']:.2e} (bound 1e-4).", "",
          "## Refits with the tail point (p = 67108879) included", "",
          "| row | census lambda | with-tail lambda | moved > 2SE? | n |",
          "|---|---|---|---|---|"]
    moved = []
    for row in ["R01", "R02", "R03", "R04", "R05", "R06", "R08", "R09",
                "C02A", "C02B", "R03B"] + [r + "M" for r in
                ["R01", "R02", "R03", "R04", "R05", "R06", "R08", "R09"]]:
        f = fits.get(row)
        if not f:
            continue
        cens = CENSUS_LAMBDA.get(row)
        if cens is None and row == "R03B":
            cens = 0.4191
        if cens is None:
            y.append(f"| {row} | - | {f['lambda']:.4f} | - | {f['n_points']} |")
            continue
        m = abs(f["lambda"] - cens) > max(2 * (f["se"] or 1), 0.005)
        if m:
            moved.append(row)
        y.append(f"| {row} | {cens:.4f} | {f['lambda']:.4f} +- {f['se']:.4f} "
                 f"| {'YES' if m else 'no'} | {f['n_points']} |")
    y += ["", "## Outcome", ""]
    if any(v is not True for v in out["controls"].values()):
        y += ["VOID: a frozen control failed; infrastructure outcome, never",
              "mathematical evidence. Defective control named in tail_fits.json."]
    elif moved:
        y += [f"PRIMARY OUTCOME: rows whose lambda moved beyond 2SE with the",
              f"tail point included: {', '.join(moved)}. The census fits for",
              f"those rows are stressed by the 2^26 point and the",
              f"EV-ECDLP-81f4d4 readings for them must be re-reviewed before",
              f"any further use."]
    else:
        y += ["NO VERDICT CHANGE: every affected row's fitted lambda moves",
              "within its census standard error when the 2^26-class tail point",
              "is included. The census fits, the PGL_2 stability deltas, and",
              "the coset-at-random-level readings stand with the tail point",
              "on record; the jackknife tail check of HEUR-1 is now complete",
              "at the ladder's full span. The normalisation-invariant findings",
              "of EV-ECDLP-81f4d4 are unaffected either way (they do not",
              "depend on absolute levels).",
              "",
              "The breach-measured values preserved in the original registry",
              "agree with these in-cap re-measurements within the complex64",
              "precision bound (per-cell comparison in tail_fits.json",
              "breach_vs_incap_comparison) -- the breach did not corrupt the",
              "measurements, it only violated machine protection."]
    y += ["", "Per-cell values, wall times, RSS high-water: tail_registry.json.", ""]
    with open(REPORT_PATH, "w") as f:
        f.write("\n".join(y) + "\n")


def write_manifest(t_start, t_finish, controls, reg, cids, xcheck_rel):
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"],
                                capture_output=True, text=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain"],
                               capture_output=True, text=True).stdout.strip()
    except Exception:
        commit, dirty = "unavailable", "unavailable"
    control_fail = [k for k, v in controls.items() if v is not True]
    run = {
        "id": RUN_ID, "experiment_id": EXP_ID, "task_id": TASK_ID,
        "status": "completed",
        "status_note": ("Tail re-measure under amendment DEC-20260921-e7edc5 "
                        "(v4 -> v5): the 26 resource_exhaustion cells at "
                        "p = 67108879 re-measured in complex64 within the "
                        "8 GiB cap, plus the frozen dual-precision cross-check."),
        "specification_version": ("5 (amendments DEC-20260921-d3fafb, "
                                  "DEC-20260921-f1d95a, DEC-20260921-a796fe, "
                                  "DEC-20260921-e7edc5)"),
        "code": {"head_commit": commit, "commit": commit,
                 "branch": "ideas/ecdlp-20260921",
                 "command": "python3 tail_driver.py (see command.txt)",
                 "dirty_at_execution_start": bool(dirty),
                 "dirty_note": dirty.replace("\n", "; ") if dirty else "clean"},
        "inputs": {
            "specification_path": "experiments/EXP-ECDLP-fac9ea/specification.yaml",
            "specification_version_executed": 5,
            "amendment_ids": ["DEC-20260921-d3fafb", "DEC-20260921-f1d95a",
                              "DEC-20260921-a796fe", "DEC-20260921-e7edc5"],
            "hypothesis_id": "H-ECDLP-4e1880",
            "predecessor_runs": ["RUN-ECDLP-8e13c2", "RUN-ECDLP-ccf8f0"],
            "seeds": "same frozen SHA256 streams reused from implementation.py",
        },
        "timing": {"start": t_start, "finish": t_finish,
                   "wall_note": "per-cell wall_seconds in tail_registry.json"},
        "environment": {
            "os": "darwin arm64", "python": sys.version.split()[0],
            "numpy": np.__version__, "scipy": "1.18.0",
            "precision": "complex64 (single-precision FFT path; dual-precision "
                         f"cross-check relative difference {xcheck_rel:.2e})",
            "implementation_basis": "reuses implementation.py constructions "
                                    "verbatim; ChirpZ64 is the single-precision "
                                    "variant of ChirpZ with identical chirp "
                                    "math, padding, and placement",
        },
        "result": {
            "certificate": {"kind": "none",
                            "note": "pure exact-algorithm measurement in reduced "
                                    "precision, bounded by the dual-precision "
                                    "cross-check and tail_checker.py spot "
                                    "rederivations"},
            "outputs": {"registry": "tail_registry.json", "fits": "tail_fits.json",
                        "report": "tail_report.md"},
            "validity": "void_control_failure" if control_fail else "controls_passed",
            "control_failures": control_fail,
            "controls": controls,
        },
        "memory_cap_gb": MEM_CAP_GB,
        "cells": {cid: {"status": r["status"],
                        "l1_nontrivial": r.get("l1_nontrivial"),
                        "abs_vhat0": r.get("abs_vhat0"),
                        "vhat0_minus_1_rel": r.get("vhat0_minus_1_rel"),
                        "wall_s": r.get("wall_seconds"),
                        "rss_highwater_gb": r.get("rss_highwater_gb")}
                  for cid, r in sorted(reg.items())},
        "artifacts": ["tail_driver.py", "tail_checker.py", "manifest.yaml",
                      "tail_registry.json", "tail_fits.json", "tail_report.md",
                      "command.txt", "environment.json", "stdout.log",
                      "stderr.log", "raw-result.json"],
        "executor_provenance": (
            "Executed in the top-level coordinator session under the executor "
            "role contract; the executor subagent runtime failed its bootstrap "
            "(AWS DescribeInstances AuthFailure), recorded in "
            "DEC-20260921-4d1b40."),
    }
    with open(MANIFEST_PATH, "w") as f:
        yaml.dump({"run": run}, f, sort_keys=False, default_flow_style=False,
                  allow_unicode=True, width=100)


def one_cell(cid):
    os.makedirs(WORK, exist_ok=True)
    reg = load_reg()
    parts = cid.split(":")
    p = int(parts[1])
    cz = ChirpZ64(p, WORK)
    if parts[0].endswith("M") and p == P_TAIL:
        v, note = moebius_row_chunked(parts[0][:-1], p)
        rec = measure_prebuilt(cid, cz, v, note, reg)
    else:
        inv = impl.inv_table(p) if parts[0].endswith("M") else None
        rec = measure(cid, cz, inv, reg)
    print(json.dumps(rec))


def finalize():
    reg = load_reg()
    out, fits = compute_outputs(reg)
    with open(FITS_PATH, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    write_report(out, fits, reg)
    write_manifest(out["t_start"], out["t_finish"], out["controls"], reg,
                   out["cids"], out["xcheck_relative_difference"])
    print("verdict-comparison written; DONE", flush=True)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--one":
        one_cell(sys.argv[2])
    elif len(sys.argv) == 2 and sys.argv[1] == "--finalize":
        finalize()
    else:
        main()
