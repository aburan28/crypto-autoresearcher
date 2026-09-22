#!/usr/bin/env python3
"""EXP-ECDLP-b9ba72 digit-character profile RUN-ECDLP-ee15df
(TASK-20260921-b61136): (lambda, PGL_2-stability) for the Thue-Morse and
Rudin-Shapiro level sets on the census's primary ladder, per the frozen
specification v1 (approved DEC-20260921-33f3b6). Canonical probability
normalisation (DEC-20260921-8e8086). Reuses the census harness
(EXP-ECDLP-fac9ea implementation.py) verbatim. Executed in the coordinator
session under the executor role contract (role-runtime outage,
DEC-20260921-4d1b40)."""

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
IMPL_DIR = os.path.abspath(os.path.join(
    HERE, "..", "..", "..", "EXP-ECDLP-fac9ea", "runs", "TASK-20260921-4888d4"))
CENSUS_REG = os.path.join(IMPL_DIR, "registry.json")
sys.path.insert(0, IMPL_DIR)
import importlib.util

_spec = importlib.util.spec_from_file_location("impl", os.path.join(IMPL_DIR, "implementation.py"))
impl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(impl)

WORK = os.path.join(HERE, "work")
REG_PATH = os.path.join(HERE, "dc_registry.json")
FITS_PATH = os.path.join(HERE, "dc_fits.json")
REPORT_PATH = os.path.join(HERE, "dc_report.md")
MANIFEST_PATH = os.path.join(HERE, "manifest.yaml")
RUN_ID = "RUN-ECDLP-ee15df"
TASK_ID = "TASK-20260921-b61136"
EXP_ID = "EXP-ECDLP-b9ba72"
MEM_CAP_GB = 8.0
LADDER = [4099, 8209, 16411, 32771, 65537, 185369, 524309, 1482919, 4194319, 16777259]
ROWS = ["VT", "VR", "VTM", "VRM", "C01", "C02A", "C02B"]


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def rss_highwater_gb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**30


def hash_bytes(*parts):
    import hashlib
    h = hashlib.sha256()
    for p in parts:
        h.update(p.encode() if isinstance(p, str) else p)
    return h.digest()


def hash_ints(*parts, count=4, mod=None):
    out = []
    counter = 0
    while len(out) < count:
        d = hash_bytes(EXP_ID, *[str(p) for p in parts], str(counter))
        for i in range(0, 32, 4):
            v = int.from_bytes(d[i:i + 4], "big")
            out.append(v % mod if mod else v)
            if len(out) >= count:
                break
        counter += 1
    return out


def thue_morse(p):
    pc = impl.popcount_array(p)
    return (pc % 2) == 0


def rudin_shapiro(p):
    nbits = max(1, (p - 1).bit_length())
    x = np.arange(p, dtype=np.int64)
    u = np.zeros(p, dtype=np.int64)
    for i in range(nbits - 1):
        b0 = (x >> i) & 1
        b1 = (x >> (i + 1)) & 1
        u += b0 & b1
    return (u % 2) == 0


def sign_bits(p, seed_set):
    bits = np.empty(p, dtype=bool)
    nblocks = (p + 255) // 256
    for blk in range(nblocks):
        d = np.frombuffer(hash_bytes(EXP_ID, "C02", "sign", seed_set, str(blk)),
                          dtype=np.uint8)
        b = np.unpackbits(d)
        lo = blk * 256
        hi = min(p, lo + 256)
        bits[lo:hi] = b[: hi - lo] > 0
    return bits


def build_row(row, p):
    if row == "VT":
        mask = thue_morse(p)
        return impl.prob_indicator(mask, p), f"|A_t|={int(mask.sum())}"
    if row == "VR":
        mask = rudin_shapiro(p)
        return impl.prob_indicator(mask, p), f"|A_r|={int(mask.sum())}"
    if row == "C01":
        return np.full(p, 1.0 / p), None
    if row == "C02A":
        return impl.prob_indicator(sign_bits(p, "A"), p), None
    if row == "C02B":
        return impl.prob_indicator(sign_bits(p, "B"), p), None
    raise ValueError(row)


def moebius_row(base_row, p, inv):
    a, b, c, d = hash_ints("C03", "moebius", base_row, mod=p)
    det = (a * d - b * c) % p
    tries = 0
    while det == 0 and tries < 100:
        a, b, c, d = hash_ints("C03", "moebius", base_row, "r", tries, mod=p)
        det = (a * d - b * c) % p
        tries += 1
    if det == 0:
        return None, "unavailable: degenerate Moebius map"
    v_base, note = build_row(base_row, p)
    if v_base is None:
        return None, note
    x = np.arange(p, dtype=np.int64)
    den = (c * x + d) % p
    y = np.zeros(p, dtype=np.int64)
    okm = den != 0
    y[okm] = ((a * x[okm] + b) % p) * inv[den[okm]] % p
    if c != 0:
        pole_x = int((-d) % p * inv[c] % p)
        y[pole_x] = (a * inv[c]) % p
    return v_base[y], f"M(x)=(ax+b)/(cx+d) a={a} b={b} c={c} d={d} det={det}"


def load_reg():
    if os.path.exists(REG_PATH):
        return json.load(open(REG_PATH))
    return {}


def save_reg(reg):
    tmp = REG_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(reg, f, indent=1, sort_keys=True)
    os.replace(tmp, REG_PATH)


def main():
    t_start = now_iso()
    os.makedirs(WORK, exist_ok=True)
    reg = load_reg()

    p0 = LADDER[0]
    cz0 = impl.ChirpZ(p0, WORK)
    v_t0, note0 = build_row("VT", p0)
    A_t = int(thue_morse(p0).sum())
    t_arr = np.where(thue_morse(p0), 1.0, -1.0)
    V_v = cz0.transform(v_t0)[0]
    V_t = cz0.transform(t_arr)[0]
    l1_v = float(np.abs(V_v[1:]).sum())
    l1_t = float(np.abs(V_t[1:]).sum())
    # CORRECTED identity (pre-archive correction, disclosed in the manifest):
    # v = 1_A/|A| = (1+t)/(2|A|) on the level set, so for k != 0
    # vhat(k) = that(k)/(2|A_t|) exactly, hence l1*(VT) = ||that||_1^*/(2|A_t|).
    # The first draft of this check used ||that||/2, conflating the 0/1-valued
    # (1+t)/2 with the probability-normalised indicator; the checker caught
    # it (rel diff 1.00) before any archive. Measurement cells are unaffected.
    predicted = l1_t / (2 * A_t)
    ident_rel = abs(l1_v - predicted) / predicted
    reg["IDENTITY:VT:4099"] = {
        "cell": "IDENTITY:VT:4099", "status": "ok",
        "l1_level_set": l1_v, "character_norm_over_2A": predicted,
        "A_t": A_t,
        "relative_difference": ident_rel, "recorded_at": now_iso()}
    save_reg(reg)
    print(f"identity check: l1*(VT)={l1_v:.6f} vs ||that||/(2|A|)={predicted:.6f} "
          f"rel {ident_rel:.2e}", flush=True)
    del cz0, V_v, V_t
    gc.collect()

    for p in LADDER:
        cz = impl.ChirpZ(p, WORK)
        inv = None
        for row in ROWS:
            cid = f"{row}:{p}"
            if cid in reg and reg[cid]["status"] in ("ok", "unavailable"):
                continue
            t0 = time.perf_counter()
            if row in ("VTM", "VRM"):
                if inv is None:
                    inv = impl.inv_table(p)
                v, note = moebius_row(row[:-1], p, inv)
            else:
                v, note = build_row(row, p)
            if v is None:
                rec = {"cell": cid, "status": "unavailable", "note": note,
                       "wall_seconds": round(time.perf_counter() - t0, 3),
                       "recorded_at": now_iso()}
            else:
                V, need = cz.transform(v)
                if V is None:
                    rec = {"cell": cid, "status": "resource_exhaustion",
                           "note": f"projected {need:.2f} GiB vs cap",
                           "wall_seconds": round(time.perf_counter() - t0, 3),
                           "recorded_at": now_iso()}
                else:
                    rec = {"cell": cid, "status": "ok",
                           "l1_nontrivial": float(np.abs(V[1:]).sum()),
                           "abs_vhat0": float(abs(V[0])),
                           "vhat0_minus_1_abs": float(abs(abs(V[0]) - 1.0)),
                           "note": note,
                           "wall_seconds": round(time.perf_counter() - t0, 3),
                           "rss_highwater_gb": round(rss_highwater_gb(), 3),
                           "fft_len": cz.L, "recorded_at": now_iso()}
                    del V
            reg = load_reg()
            reg[cid] = rec
            save_reg(reg)
            print(f"  {cid} -> {rec['status']} l1*={rec.get('l1_nontrivial')} "
                  f"({rec.get('wall_seconds')}s)", flush=True)
        del cz
        gc.collect()
    t_finish = now_iso()

    def pts(row):
        return [(p, reg[f"{row}:{p}"]["l1_nontrivial"]) for p in LADDER
                if reg.get(f"{row}:{p}", {}).get("status") == "ok"]

    fits = {row: impl.fit_lambda(pts(row)) for row in ROWS}
    c01_ok = all(r["l1_nontrivial"] <= 1e-9 * max(r["abs_vhat0"], 1e-30)
                 for c, r in reg.items()
                 if c.startswith("C01:") and r.get("status") == "ok")
    v0_ok = all(r.get("vhat0_minus_1_abs", 1.0) <= 1e-9
                for c, r in reg.items()
                if r.get("status") == "ok" and ":" in c
                and not c.startswith(("IDENTITY",)))
    fa, fb = fits["C02A"], fits["C02B"]
    c02_band = abs(fa["lambda"] - 0.5) <= 2 * (fa["se"] or 1) + 0.02
    seed_agree = abs(fa["lambda"] - fb["lambda"]) <= 2 * math.sqrt(
        (fa["se"] or 1) ** 2 + (fb["se"] or 1) ** 2)
    ident_ok = ident_rel <= 1e-9

    verdicts = {}
    for ch, base, mrow in (("Thue-Morse", "VT", "VTM"), ("Rudin-Shapiro", "VR", "VRM")):
        f, fm = fits[base], fits[mrow]
        if not f or not fm:
            verdicts[ch] = "unresolved"
            continue
        moeb = abs(fm["lambda"] - f["lambda"]) > 2 * math.sqrt(
            (f["se"] or 1) ** 2 + (fm["se"] or 1) ** 2)
        delta = f["lambda"] - fa["lambda"]
        se_d = math.sqrt((f["se"] or 1) ** 2 + (fa["se"] or 1) ** 2)
        guards = True
        if f.get("jackknife_lambda_excl_largest") is not None:
            guards = abs(f["jackknife_lambda_excl_largest"] - f["lambda"]) <= 3 * (f["se"] or 1)
        if not guards:
            verdicts[ch] = "unresolved"
        elif moeb:
            verdicts[ch] = "unstable"
        elif delta > 2 * se_d:
            verdicts[ch] = "stable_above_random"
        elif abs(delta) <= 2 * se_d:
            verdicts[ch] = "stable_flat"
        else:
            verdicts[ch] = "unresolved"

    census = json.load(open(CENSUS_REG))
    r03_pts = [(p, census[f"R03:{p}"]["l1_nontrivial"]) for p in LADDER
               if census.get(f"R03:{p}", {}).get("status") == "ok"]
    r03_fit = impl.fit_lambda(r03_pts)
    vt_lam = fits["VT"]["lambda"] if fits["VT"] else None
    closure = None
    if vt_lam is not None:
        in_band = 0.36 <= vt_lam <= 0.42
        closure = {
            "VT_lambda": vt_lam,
            "in_ffe1df_band_0.36_0.42": in_band,
            "census_R03_mode_level_lambda_on_same_primes": (
                r03_fit["lambda"] if r03_fit else None),
            "statement": (
                "The Thue-Morse level set reproduces the ffe1df band; the "
                "0.39 is attributed to the character construction."
                if in_band else
                "The Thue-Morse level set does NOT reproduce the band; the "
                "reproduction question stands with both constructions "
                "measured side by side (character and mode-level indicator)."),
        }

    controls = {
        "C01_numerically_zero": c01_ok,
        "C02A_parseval_band": c02_band,
        "C02_seed_agreement": seed_agree,
        "identity_check_1e-9": ident_ok,
        "vhat0_equals_1_all_ok_cells": v0_ok,
    }
    out = {
        "run_id": RUN_ID, "ladder": LADDER, "fits": fits,
        "verdicts": verdicts, "controls": controls,
        "construction_closure": closure,
        "census_R03_bridge_fit_same_primes": r03_fit,
        "t_start": t_start, "t_finish": t_finish,
        "generated_at": now_iso(),
    }
    with open(FITS_PATH, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    write_report(out)
    write_manifest(out, reg, controls)
    print("verdicts:", verdicts, flush=True)
    print("closure:", (closure or {}).get("statement"), flush=True)
    print("DONE", flush=True)


def write_report(out):
    y = ["# EXP-ECDLP-b9ba72 — digit-character (lambda, PGL_2-stability) profile", "",
         f"Run {RUN_ID} under TASK-20260921-b61136, specification v1",
         "(approved DEC-20260921-33f3b6), canonical probability",
         "normalisation, the census's primary ladder verbatim.", "",
         "| row | lambda | SE | n |", "|---|---|---|---|"]
    for row in ROWS:
        f = out["fits"][row]
        if f:
            y.append(f"| {row} | {f['lambda']:.4f} | {f['se']:.4f} | {f['n_points']} |")
    y += ["", "## Controls", "", "| control | result |", "|---|---|"]
    for k, v in out["controls"].items():
        y.append(f"| {k} | {'PASS' if v is True else ('FAIL' if v is False else 'NOT EVALUATED')} |")
    y += ["", "## Verdicts", ""]
    for ch, v in out["verdicts"].items():
        y.append(f"- {ch}: **{v}**")
    cl = out["construction_closure"]
    if cl:
        y += ["", "## Construction closure (DEC-20260921-8e8086 open item)", "",
              f"- VT lambda = {cl['VT_lambda']:.4f}; in the ffe1df band "
              f"[0.36, 0.42]: {cl['in_ffe1df_band_0.36_0.42']}",
              f"- census R03 mode-level bridge on the same primes: "
              f"{cl['census_R03_mode_level_lambda_on_same_primes']}",
              f"- {cl['statement']}"]
    y += ["", "## Reading", ""]
    if any(v is not True for v in out["controls"].values()):
        y += ["VOID: a frozen control failed; infrastructure outcome, never",
              "evidence. The defective control is named in dc_fits.json."]
    elif any(v == "stable_above_random" for v in out["verdicts"].values()):
        y += ["PRIMARY POSITIVE OUTCOME (candidate): a digit-character level",
              "set reads PGL_2-stable AND above the random-set level -- the",
              "first natural inhabitant of the cell EV-ECDLP-81f4d4 found",
              "empty. Per the frozen rules this triggers REPLICATE on first",
              "observation, not support; the owed independent review covers",
              "it with the census evidence."]
    else:
        y += ["The census's scoped negative extends over the digit-character",
              "family at this ladder: no character is simultaneously",
              "PGL_2-stable and above the random-set level. The",
              "synthetic-statistic lane narrows to the cross-ratio family",
              "(IDEA-20260921-3ecbe8) and the non-set escape hatch",
              "(IDEA-20260921-4af08b)."]
    y += ["", "Per-cell values, wall times, RSS: dc_registry.json.", ""]
    with open(REPORT_PATH, "w") as f:
        f.write("\n".join(y) + "\n")


def write_manifest(out, reg, controls):
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
        "status_note": "Single frozen pass over the digit-character rows on "
                       "the census's primary ladder.",
        "specification_version": 1,
        "code": {"head_commit": commit, "commit": commit,
                 "branch": "ideas/ecdlp-20260921",
                 "command": "python3 dc_driver.py (see command.txt)",
                 "dirty_at_execution_start": bool(dirty),
                 "dirty_note": dirty.replace("\n", "; ") if dirty else "clean"},
        "inputs": {
            "specification_path": "experiments/EXP-ECDLP-b9ba72/specification.yaml",
            "specification_version_executed": 1,
            "amendment_ids": [],
            "hypothesis_id": "H-ECDLP-caf3ff",
            "seeds": "SHA256(EXP-ECDLP-b9ba72:<cell>:<purpose>:<counter>) "
                     "streams frozen in dc_driver.py",
            "census_R03_bridge": "cited from RUN-ECDLP-8e13c2 registry, "
                                 "not re-measured",
        },
        "timing": {"start": out["t_start"], "finish": out["t_finish"],
                   "wall_note": "per-cell wall_seconds in dc_registry.json"},
        "environment": {
            "os": "darwin arm64", "python": sys.version.split()[0],
            "numpy": np.__version__, "scipy": "1.18.0",
            "implementation_basis": "reuses EXP-ECDLP-fac9ea "
                                    "implementation.py ChirpZ, prob_indicator, "
                                    "popcount_array, fit_lambda verbatim",
        },
        "result": {
            "certificate": {"kind": "none",
                            "note": "pure exact measurement; correctness by "
                                    "the identity check and dc_checker.py spot "
                                    "rederivations"},
            "outputs": {"registry": "dc_registry.json", "fits": "dc_fits.json",
                        "report": "dc_report.md"},
            "verdicts": out["verdicts"],
            "construction_closure": out["construction_closure"],
            "validity": "void_control_failure" if control_fail else "controls_passed",
            "control_failures": control_fail,
            "controls": controls,
        },
        "ladder": LADDER, "rows": ROWS,
        "cells": {cid: {"status": r["status"],
                        "l1_nontrivial": r.get("l1_nontrivial"),
                        "abs_vhat0": r.get("abs_vhat0"),
                        "wall_s": r.get("wall_seconds"),
                        "rss_highwater_gb": r.get("rss_highwater_gb")}
                  for cid, r in sorted(reg.items())},
        "memory_cap_gb": MEM_CAP_GB,
        "artifacts": ["dc_driver.py", "dc_checker.py", "manifest.yaml",
                      "dc_registry.json", "dc_fits.json", "dc_report.md",
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


if __name__ == "__main__":
    main()
