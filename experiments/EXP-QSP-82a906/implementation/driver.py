#!/usr/bin/env python3
"""EXP-QSP-82a906 driver: Stage 0–4 under TASK-20260917-66ec2b.

Contract: specification.yaml v1 as modified by amendments/v2.yaml.
Observations only. No interpretation of H1, H-QSP-645a07, or (E').
"""
from __future__ import annotations

import hashlib
import json
import os
import resource
import statistics
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from chain import S0_Y, compose_lambda_y, expand_s3_at_xi1, per_variable_degrees, ydeg
from f2arith import deg
from i2_python import resultant_i2
from i3_gcd import has_nonconstant_common_factor
from runlib import EXP_DIR, IMPL, RUNS_DIR, Run

FIELD_MOD = {
    17: (1 << 17) | (1 << 3) | 1,
    23: (1 << 23) | (1 << 5) | 1,
}
FIELD_POLY_STR = {
    17: "z^17 + z^3 + 1",
    23: "z^23 + z^5 + 1",
}

D2 = [(5, "X^2 + 1"), (7, "X^2 + X + 1")]
D3 = [
    (8, "X^3"),
    (9, "X^3 + 1"),
    (10, "X^3 + X"),
    (11, "X^3 + X + 1"),
    (12, "X^3 + X^2"),
    (13, "X^3 + X^2 + 1"),
    (14, "X^3 + X^2 + X"),
    (15, "X^3 + X^2 + X + 1"),
]
LAMBDAS = {2: D2, 3: D3}

RUN_IDS = {
    0: "RUN-QSP-c4b336",
    1: "RUN-QSP-55bd71",
    2: "RUN-QSP-28ef77",
    3: "RUN-QSP-c6490f",
    4: "RUN-QSP-5ec02a",
}

I1_BIN = os.path.join(IMPL, "i1_sylvester")
BASE_SEED = 20260917


def hex_coeff(c: int) -> str:
    return format(c, "x") if c else "0"


def compile_i1() -> tuple[bool, str]:
    src = os.path.join(IMPL, "i1_sylvester.c")
    cmd = ["gcc", "-O2", "-o", I1_BIN, src]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        return False, p.stderr
    return True, p.stdout + p.stderr


def i1_resultant(f_y: list[int], g_y: list[int]) -> tuple[int, bool, int, str]:
    lines = [str(len(f_y))] + [hex_coeff(c) for c in f_y]
    lines += [str(len(g_y))] + [hex_coeff(c) for c in g_y]
    inp = "\n".join(lines) + "\n"
    p = subprocess.run([I1_BIN], input=inp, capture_output=True, text=True, timeout=120)
    if p.returncode != 0:
        return -1, True, 0, "i1_fail:%s" % p.stderr.strip()
    deg_e, zero, poly = -1, True, 0
    for line in p.stdout.splitlines():
        if line.startswith("deg "):
            deg_e = int(line.split()[1])
        elif line.startswith("zero "):
            zero = line.split()[1] == "1"
        elif line.startswith("poly "):
            h = line.split()[1]
            poly = int(h, 16) if h != "0" else 0
    return deg_e, zero, poly, p.stdout.strip()


def i2_resultant(f_y: list[int], g_y: list[int], n: int) -> tuple[int, bool, int]:
    return resultant_i2(f_y, g_y, n, FIELD_MOD[n])


def agree(a, b) -> bool:
    d1, z1, p1 = a[0], a[1], a[2]
    d2, z2, p2 = b[0], b[1], b[2]
    if z1 != z2:
        return False
    if z1:
        return True
    return d1 == d2 and p1 == p2 and p1 != -1 and p2 != -1


def cell_row(n, d, lam_bits, lam_poly, s0, s1, i1, i2, i3_flag, wall, rss):
    d1, z1, p1 = i1[0], i1[1], i1[2]
    d2, z2, p2 = i2[0], i2[1], i2[2]
    deg_elim = d1 if not z1 else 0
    md_paper = 4 * d
    md_note = 4 * d * d
    dx0, dy0 = per_variable_degrees(s0)
    dx1, dy1 = per_variable_degrees(s1)
    return {
        "n": n,
        "n_prime": (n + 1) // 2,
        "d": d,
        "lambda_bits": lam_bits,
        "lambda": lam_poly,
        "field_polynomial": FIELD_POLY_STR[n],
        "S0_deg_X": dx0,
        "S0_deg_Y": dy0,
        "S1_deg_X": dx1,
        "S1_deg_Y": dy1,
        "I1_deg_elim": d1,
        "I2_deg_elim": d2,
        "I1_identically_zero": z1,
        "I2_identically_zero": z2,
        "I1_elim_hex": format(p1, "x") if p1 not in (-1,) and not z1 else ("0" if z1 else "not_f2"),
        "I2_elim_hex": format(p2, "x") if p2 not in (-1,) and not z2 else ("0" if z2 else "not_f2"),
        "identically_zero": z1,
        "I3_common_factor": i3_flag,
        "rho_paper": None if z1 else (deg_elim / md_paper),
        "rho_note": None if z1 else (deg_elim / md_note),
        "M_E_paper": md_paper,
        "M_E_note": md_note,
        "wall_clock_seconds": round(wall, 6),
        "peak_rss_bytes": rss,
        "implementations": "I1_C_Bareiss_F2X / I2_Python_Newton_F2n",
    }


def median_rho(rows):
    vals = [r["rho_paper"] for r in rows if r["rho_paper"] is not None]
    if not vals:
        return None
    return statistics.median(vals)


def random_bivariate(dx: int, dy: int, stream: str, start_i: int) -> tuple[list[int], int]:
    i = start_i
    while True:
        h = hashlib.sha256(("%s:%d" % (stream, i)).encode()).digest()
        need = (dx + 1) * (dy + 1)
        bits = []
        acc = int.from_bytes(h, "little")
        k = 0
        while len(bits) < need:
            if k >= acc.bit_length() and len(bits) < need:
                i += 1
                acc = int.from_bytes(hashlib.sha256(("%s:%d" % (stream, i)).encode()).digest(), "little")
                k = 0
            bits.append((acc >> k) & 1)
            k += 1
        y = []
        for j in range(dy + 1):
            c = 0
            for ii in range(dx + 1):
                if bits[ii + j * (dx + 1)]:
                    c |= 1 << ii
            y.append(c)
        while y and y[-1] == 0:
            y.pop()
        dxm, dym = per_variable_degrees(y)
        i += 1
        if dxm == dx and dym == dy:
            return y, i


def stage0(run: Run) -> dict:
    ok, clog = compile_i1()
    gcc_ok = ok
    run.log("gcc_build", "ok" if ok else "FAIL")
    if clog:
        run.log("gcc_log", clog.strip()[:500])
    if not ok:
        return {"gcc_ok": False, "gate": "fail", "reason": "gcc build failed", "compile_log": clog}

    s0 = S0_Y
    s1 = compose_lambda_y(s0, 0b111)
    t0 = time.time()
    i1 = i1_resultant(s0, s1)
    t1 = time.time()
    i2 = i2_resultant(s0, s1, 17)
    t2 = time.time()
    run.log("fixture I1", i1)
    run.log("fixture I2", i2)
    ag = agree(i1, i2)
    gate = gcc_ok and os.path.isfile(I1_BIN) and ag
    return {
        "gcc_ok": gcc_ok,
        "i1_exists": os.path.isfile(I1_BIN),
        "i2_exists": True,
        "named_fixture": {
            "n": 17, "d": 2, "lambda": "X^2 + X + 1", "lambda_bits": 7,
            "I1": {"deg": i1[0], "zero": i1[1], "poly_hex": format(i1[2], "x") if not i1[1] else "0",
                   "wall": round(t1 - t0, 6)},
            "I2": {"deg": i2[0], "zero": i2[1], "poly_hex": format(i2[2], "x") if not i2[1] else "0",
                   "wall": round(t2 - t1, 6)},
            "agree": ag,
        },
        "gate": "pass" if gate else "fail",
        "reason": "I1/I2 agree on named fixture" if gate else "fixture disagreement or missing engine",
    }


def stage1(run: Run) -> dict:
    expanded = expand_s3_at_xi1()
    identity = expanded == S0_Y
    run.log("expanded_form_identity", identity, expanded, S0_Y)
    cells = []
    all_ok = identity
    for n in (17, 23):
        for d, lst in LAMBDAS.items():
            for bits, poly in lst:
                s0 = S0_Y
                s1 = compose_lambda_y(s0, bits)
                dx0, dy0 = per_variable_degrees(s0)
                dx1, dy1 = per_variable_degrees(s1)
                ok = dx0 == 2 and dy0 == 2 and dx1 == 2 * d and dy1 == 2 * d
                if not ok:
                    all_ok = False
                cells.append({
                    "n": n, "d": d, "lambda_bits": bits, "lambda": poly,
                    "n_prime": (n + 1) // 2,
                    "S0_deg_X": dx0, "S0_deg_Y": dy0,
                    "S1_deg_X": dx1, "S1_deg_Y": dy1,
                    "degree_gate": ok,
                })
                run.log("deg", n, d, poly, dx0, dy0, dx1, dy1, ok)
    return {
        "expanded_form_identity": identity,
        "cells": cells,
        "gate": "pass" if all_ok else "fail",
        "reason": "all chain cells degree 2 and 2d" if all_ok else "degree mismatch",
    }


def peak_rss_bytes() -> int:
    """High-water RSS after the work, matching runlib: max(self, children)."""
    ru = resource.getrusage(resource.RUSAGE_SELF)
    ruc = resource.getrusage(resource.RUSAGE_CHILDREN)
    return max(ru.ru_maxrss, ruc.ru_maxrss) * 1024


def measure_pair(s0, s1, n):
    t0 = time.time()
    i1 = i1_resultant(s0, s1)
    i2 = i2_resultant(s0, s1, n)
    wall = time.time() - t0
    i3 = None
    if i1[1] or i2[1]:
        i3 = has_nonconstant_common_factor(s0, s1)
    return i1, i2, i3, wall, peak_rss_bytes()


def g1_g2(med2, med3, rows_n):
    """Official G2/G1 at one n. v2: undefined median is not G2 by itself."""
    zeros = [r for r in rows_n if r["identically_zero"]]
    all_zero = len(zeros) == len(rows_n) and all(r["I3_common_factor"] for r in zeros)
    g2 = False
    if med2 is not None and med3 is not None and med2 < 0.25 and med3 < 0.25:
        g2 = True
    if all_zero:
        g2 = True
    g1 = False
    if med2 is not None and med3 is not None and med3 < med2 / 2:
        g1 = True
    return g1, g2, all_zero


def stage2(run: Run) -> dict:
    rows = []
    opened_n = []
    stop_reason = None
    disagreements = []
    unexplained_zeros = []
    for n in (17, 23):
        opened_n.append(n)
        batch = []
        for d, lst in LAMBDAS.items():
            for bits, poly in lst:
                s0 = S0_Y
                s1 = compose_lambda_y(s0, bits)
                i1, i2, i3, wall, rss = measure_pair(s0, s1, n)
                row = cell_row(n, d, bits, poly, s0, s1, i1, i2, i3, wall, rss)
                row["object_class"] = "chain"
                if not agree(i1, i2):
                    disagreements.append(row)
                if row["identically_zero"] and not i3:
                    row["invalid_zero_without_I3"] = True
                    unexplained_zeros.append(row)
                batch.append(row)
                rows.append(row)
                run.log("cell", n, d, poly, "I1", i1[0], i1[1], "I2", i2[0], i2[1], "I3", i3)
        r2 = [r for r in batch if r["d"] == 2]
        r3 = [r for r in batch if r["d"] == 3]
        m2, m3 = median_rho(r2), median_rho(r3)
        g1, g2, az = g1_g2(m2, m3, batch)
        run.log("n_summary", n, "median_d2", m2, "median_d3", m3, "G1", g1, "G2", g2)
        if g1 or g2:
            stop_reason = "G1" if g1 else "G2"
            run.log("STOP further n:", stop_reason, "at n", n)
            break
    # Invalidation: a zero without I3 invalidates that cell (S4/M7) and, if
    # it recurs, the stage. Other lambdas are still measured before the gate.
    if disagreements:
        gate, reason = "fail", "C3 disagreement"
    elif len(unexplained_zeros) >= 2:
        gate, reason = "fail", "identically-zero without I3 recurred; stage invalid"
    elif unexplained_zeros:
        gate, reason = "fail", "identically-zero without I3; cell invalid"
    else:
        gate, reason = "pass", "chain cells measured"
    return {
        "rows": rows,
        "opened_n": opened_n,
        "unopened_n": [x for x in (17, 23) if x not in opened_n],
        "stop_reason": stop_reason,
        "disagreements": [
            {"n": r["n"], "d": r["d"], "lambda": r["lambda"],
             "I1": r["I1_deg_elim"], "I2": r["I2_deg_elim"]}
            for r in disagreements
        ],
        "invalid_zeros_without_I3": [
            {"n": r["n"], "d": r["d"], "lambda": r["lambda"]}
            for r in unexplained_zeros
        ],
        "gate": gate,
        "reason": reason,
    }


def stage3(run: Run, opened_n: list[int]) -> dict:
    rows = []
    disagreements = []
    # C2a, C2b at opened n
    for n in opened_n:
        for bits, poly, d, label in ((0b10, "X", 1, "C2a"), (0b11, "X + 1", 1, "C2b")):
            s0 = S0_Y
            s1 = compose_lambda_y(s0, bits)
            i1, i2, i3, wall, rss = measure_pair(s0, s1, n)
            row = cell_row(n, d, bits, poly, s0, s1, i1, i2, i3, wall, rss)
            row["object_class"] = label
            if label == "C2a":
                row["forced_zero"] = True
                row["C2a_ok"] = bool(i1[1] and i2[1])
            if not agree(i1, i2):
                disagreements.append(row)
            rows.append(row)
            run.log(label, n, poly, "I1", i1[0], i1[1], "I2", i2[0], i2[1])
        for d in (2, 3):
            stream = "20260917:C1:n=%d:d=%d" % (n, d)
            f, i = random_bivariate(2, 2, stream + ":f", 0)
            g, j = random_bivariate(2 * d, 2 * d, stream + ":g", 0)
            phi = compose_lambda_y(f, 0b111)
            tries = 0
            while g == phi and tries < 100:
                g, j = random_bivariate(2 * d, 2 * d, stream + ":g", j)
                tries += 1
            i1, i2, i3, wall, rss = measure_pair(f, g, n)
            row = cell_row(n, d, None, "C1-null", f, g, i1, i2, i3, wall, rss)
            row["object_class"] = "C1"
            row["C1_stream"] = stream
            row["S0_deg_X"], row["S0_deg_Y"] = per_variable_degrees(f)
            row["S1_deg_X"], row["S1_deg_Y"] = per_variable_degrees(g)
            if not agree(i1, i2):
                disagreements.append(row)
            rows.append(row)
            run.log("C1", n, d, "I1", i1[0], i1[1], "I2", i2[0], i2[1])
    c2a_ok = all(r.get("C2a_ok", True) for r in rows)
    return {
        "rows": rows,
        "disagreements": disagreements,
        "C2a_ok": c2a_ok,
        "gate": "fail" if disagreements or not c2a_ok else "pass",
    }


def stage4(run: Run, chain_rows: list, ctrl_rows: list, opened_n: list, unopened: list, stop_reason) -> dict:
    comparisons = []
    g1_any = False
    g2_any = False
    for n in opened_n:
        r2 = [r for r in chain_rows if r["n"] == n and r["d"] == 2]
        r3 = [r for r in chain_rows if r["n"] == n and r["d"] == 3]
        m2, m3 = median_rho(r2), median_rho(r3)
        g1, g2, az = g1_g2(m2, m3, [r for r in chain_rows if r["n"] == n])
        ratio = None if (m2 in (None, 0) or m3 is None) else (m3 / m2)
        comparisons.append({
            "n": n,
            "median_rho_paper_d2": m2,
            "median_rho_paper_d3": m3,
            "ratio_d3_over_d2": ratio,
            "G1": g1,
            "G2": g2,
            "all_zero_with_I3": az,
            "per_lambda_d2": [{"lambda": r["lambda"], "deg_elim": r["I1_deg_elim"],
                               "rho_paper": r["rho_paper"], "zero": r["identically_zero"]} for r in r2],
            "per_lambda_d3": [{"lambda": r["lambda"], "deg_elim": r["I1_deg_elim"],
                               "rho_paper": r["rho_paper"], "zero": r["identically_zero"]} for r in r3],
        })
        g1_any = g1_any or g1
        g2_any = g2_any or g2
        run.log("compare", n, m2, m3, ratio, "G1", g1, "G2", g2)
    obstruction = None
    if g1_any or g2_any:
        obstruction = {
            "statement": "scoped m=2 H1 deficit at the opened n (G1 and/or G2). No (E') claim.",
            "quantity": "median_rho_paper(d=3) / median_rho_paper(d=2) and/or both medians vs 1/4",
            "value": comparisons,
            "units": "dimensionless degree ratio",
            "measured_by": [RUN_IDS[2], RUN_IDS[4]],
            "scope": "m=2, opened n=%s, xi=1, named lambda class, I1/I2 Sylvester" % opened_n,
            "resource_check": {
                "examined": True,
                "reading": "A growing or identically-far-below eliminant degree is an obstruction to H1 at these cells; it is also the hypothesis of a collapse-as-asset theory (cheaper eliminant). No successor experiment is spawned by this executor.",
                "spawned_ids": [],
            },
        }
    return {
        "opened_n": opened_n,
        "unopened_n": unopened,
        "unopened_named_as": "unfinished-by-stop" if stop_reason else "none",
        "stop_reason": stop_reason,
        "comparisons": comparisons,
        "G1_any": g1_any,
        "G2_any": g2_any,
        "obstruction": obstruction,
        "M_E_paper_modeled": {2: 8, 3: 12, 1: 4},
        "M_E_note_modeled": {2: 16, 3: 36, 1: 4},
        "no_interpretation": "This report does not interpret H-QSP-645a07, (E'), or kappa.",
    }


def main() -> int:
    os.makedirs(RUNS_DIR, exist_ok=True)
    # Stage 0
    r0 = Run(RUN_IDS[0], "stage_0",
             "python3 experiments/EXP-QSP-82a906/implementation/driver.py",
             {"stage": 0, "named_fixture": "n=17 d=2 lambda=X^2+X+1"})
    s0 = stage0(r0)
    st0 = "completed_valid" if s0.get("gate") == "pass" else "completed_invalid"
    r0.finish(s0, st0, s0.get("reason", ""))
    if s0.get("gate") != "pass":
        _write_exec_report("Stage 0 gate fail: infrastructure. Stages 1-4 not run.", s0, None, None, None)
        return 2

    r1 = Run(RUN_IDS[1], "stage_1",
             "python3 experiments/EXP-QSP-82a906/implementation/driver.py",
             {"stage": 1, "cells": "20 chain degree checks"})
    s1 = stage1(r1)
    st1 = "completed_valid" if s1.get("gate") == "pass" else "completed_invalid"
    r1.finish(s1, st1, s1.get("reason", ""))
    if s1.get("gate") != "pass":
        _write_exec_report("Stage 1 degree gate fail: builder defect. Stage 2+ not run.", s0, s1, None, None)
        return 2

    r2 = Run(RUN_IDS[2], "stage_2",
             "python3 experiments/EXP-QSP-82a906/implementation/driver.py",
             {"stage": 2, "n": [17, 23], "d": [2, 3]})
    s2 = stage2(r2)
    st2 = "completed_valid" if s2.get("gate") == "pass" else "completed_invalid"
    r2.finish(s2, st2, s2.get("reason", ""))
    if s2.get("gate") != "pass":
        if s2.get("disagreements"):
            msg = "C3 disagreement: run invalid (F5)."
        else:
            msg = "identically-zero without I3: cell invalid" + (
                "; stage invalid (recurred)." if len(s2.get("invalid_zeros_without_I3") or []) >= 2
                else ".")
        _write_exec_report(msg, s0, s1, s2, None)
        return 2

    r3 = Run(RUN_IDS[3], "stage_3",
             "python3 experiments/EXP-QSP-82a906/implementation/driver.py",
             {"stage": 3, "opened_n": s2["opened_n"]})
    s3 = stage3(r3, s2["opened_n"])
    st3 = "completed_invalid" if s3.get("gate") != "pass" else "completed_valid"
    r3.finish(s3, st3, "controls measured" if st3 == "completed_valid" else "C2a or C3 fail")
    if s3.get("gate") != "pass":
        _write_exec_report("Stage 3 control fail.", s0, s1, s2, s3)
        return 2

    r4 = Run(RUN_IDS[4], "stage_4",
             "python3 experiments/EXP-QSP-82a906/implementation/driver.py",
             {"stage": 4, "opened_n": s2["opened_n"]})
    s4 = stage4(r4, s2["rows"], s3["rows"], s2["opened_n"], s2["unopened_n"], s2["stop_reason"])
    r4.finish(s4, "completed_valid", "report extracted; no H1 interpretation")
    _write_exec_report("all opened stages completed", s0, s1, s2, s3, s4)
    return 0


def _write_exec_report(summary, s0, s1=None, s2=None, s3=None, s4=None):
    path = os.path.join(EXP_DIR, "execution-report.yaml")
    opened = (s2 or {}).get("opened_n")
    unopened = (s2 or {}).get("unopened_n")
    doc = {
        "execution_report": {
            "experiment_id": "EXP-QSP-82a906",
            "task_id": "TASK-20260917-66ec2b",
            "contract": "specification.yaml v1 as modified by amendments/v2.yaml",
            "summary": summary,
            "stages": {
                "0": {"ran": s0 is not None, "gate": (s0 or {}).get("gate"), "run_id": RUN_IDS[0]},
                "1": {"ran": s1 is not None, "gate": (s1 or {}).get("gate") if s1 else "not run", "run_id": RUN_IDS[1]},
                "2": {"ran": s2 is not None, "opened_n": opened, "unopened_n": unopened,
                      "stop_reason": (s2 or {}).get("stop_reason"), "run_id": RUN_IDS[2]},
                "3": {"ran": s3 is not None, "gate": (s3 or {}).get("gate") if s3 else "not run", "run_id": RUN_IDS[3]},
                "4": {"ran": s4 is not None, "G1_any": (s4 or {}).get("G1_any"),
                      "G2_any": (s4 or {}).get("G2_any"), "run_id": RUN_IDS[4]},
            },
            "observations_only": True,
            "no_interpretation_of": ["H-QSP-411d8f truth", "H-QSP-645a07", "(E')"],
        }
    }
    try:
        import yaml
        with open(path, "w") as fh:
            yaml.safe_dump(doc, fh, sort_keys=False)
    except Exception:
        with open(path, "w") as fh:
            json.dump(doc, fh, indent=2)


if __name__ == "__main__":
    sys.exit(main())
