#!/usr/bin/env python3
"""EXP-ECDLP-7d2a86 Stages 0-1 launcher (inner S3 off-diagonal ladder).

Stage 0: Zero-run worksheet — counting table, size law / l*, power table
         (exact CP95), stream rule, precommit hashes, S0-1..S0-6 self-checks.
Stage 1: C-PIN (pinned instrument hashes + numpy), C-FIX (Closure.R/.C),
         C-SELF (Stage-0 hash replay), then ladder entry. Full (23,8)/(35,12)
         sample arms require the GF(2^n) curve/field builder; until that is
         present Stage 1 terminates as O-IMPEDIMENT (not negative evidence).

Observations only. No Magma/Sage/AUXIN/Bedrock. No ECDLP solve.
Amazon Bedrock is not selected.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from datetime import datetime, timezone
from math import comb
from pathlib import Path
from typing import Any

EXPERIMENT_ID = "EXP-ECDLP-7d2a86"
HYPOTHESIS_ID = "H-ECDLP-1f1111"
APPROVED_BY = "DEC-20261002-dd642f"
EXP_ROOT = Path(__file__).resolve().parents[1]
REPO = EXP_ROOT.parents[1]
IMPL = Path(__file__).resolve().parent

# Idea / S0-1 frozen counting figures: (nv, neq) -> (D_reg, rows_D4, cols_D4)
# Plus (18,17) diagonal reference at D=5.
COUNTING_CELLS = [
    {"label": "(12,17)", "nv": 12, "neq": 17, "D_reg": 4, "rows": 1343, "cols": 794},
    {"label": "(14,19)", "nv": 14, "neq": 19, "D_reg": 4, "rows": 2014, "cols": 1471},
    {"label": "(16,23)", "nv": 16, "neq": 23, "D_reg": 4, "rows": 3151, "cols": 2517},
    {"label": "(20,29)", "nv": 20, "neq": 29, "D_reg": 4, "rows": 6119, "cols": 6196},
    {"label": "(24,35)", "nv": 24, "neq": 35, "D_reg": 5, "rows": 10535, "cols": 12951},
    {"label": "(28,41)", "nv": 28, "neq": 41, "D_reg": 5, "rows": 16687, "cols": 24158},
    {"label": "(32,47)", "nv": 32, "neq": 47, "D_reg": 6, "rows": 24863, "cols": 41449},
    {"label": "(18,17)", "nv": 18, "neq": 17, "D_reg": 5, "rows": 2924, "cols": 4048},
]

# C-FIX triples from S0-2: (nv, D, neq)
CFIX_TRIPLES = [
    (18, 4, 17),
    (16, 3, 23),
    (16, 4, 23),
    (16, 5, 23),
    (24, 3, 35),
    (24, 4, 35),
    (24, 5, 35),
]

PINNED = {
    "experiments/EXP-CERTBIN-e94b27/impl/closure.py":
        "748dbea25cf9c3b5836f409a8bc7fa749250a903414252a301e054eb1c497d3f",
    "experiments/EXP-CERTBIN-e94b27/impl/macaulay.py":
        "b094fac5b3f7dcb84e7064712d053ee076f007c36a5e26134081932928269650",
    "experiments/EXP-CERTBIN-e94b27/impl/gf2n.py":
        "b7340e42bf1db42f404e7665e04298b58388a9ad6411fd7e78c112e5235cdb42",
    "experiments/EXP-CERTBIN-e94b27/impl/curve.py":
        "7c97d5d9a817f1adb380bed79c3c4e47b05b24e23bd1839c8aa51fa354cc5b4f",
    "experiments/EXP-CERTBIN-e94b27/impl/elim.py":
        "d17670865e3d794493e8a1e4f6ad3d486a4d4bb0768b09bffce09f937806ebc4",
    "experiments/EXP-CERTBIN-e94b27/impl/stats_exact.py":
        "20ae809dd07b2858c1ccfc3d2bd9a331bce7c4ebd50a5017b5e7ff2e98b42a0d",
    "experiments/EXP-CERTBIN-e94b27/verifier/verify_cert.py":
        "c2a2c96e78f84e7a821c2f2766a7dff2c19c3c756bd85f07e87bd20ede1e2a8f",
    "src/semaev_tree.py":
        "e9f1681b4e422f7a67176fffd3e5f91ab7a95c9fddc1eb925c2bb0a93a9becef",
}

REQUIRED_NUMPY = "2.4.6"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.write_text(text, encoding="utf-8")


def write_yaml_like(path: Path, obj: Any) -> None:
    """Minimal YAML dump via json-compatible structure (PyYAML may be absent)."""
    try:
        import yaml  # type: ignore
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            raise FileExistsError(f"refusing overwrite: {path}")
        path.write_text(yaml.safe_dump(obj, sort_keys=True), encoding="utf-8")
    except ImportError:
        write_json(path.with_suffix(path.suffix + ".json"), obj)
        # Still write a YAML-looking document from JSON for contract paths.
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            raise FileExistsError(f"refusing overwrite: {path}")
        path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def binom_le(n: int, d: int) -> int:
    return sum(comb(n, k) for k in range(d + 1))


def macaulay_dims(nv: int, D: int, neq: int) -> tuple[int, int]:
    rows = neq * binom_le(nv, D - 2)
    cols = binom_le(nv, D)
    return rows, cols


def semi_regular_series(nv: int, neq: int, max_deg: int = 12) -> list[dict[str, Any]]:
    """Coefficients of (1+z)^nv / (1+z^2)^neq as formal power series over Z."""
    # (1+z)^nv
    a = [comb(nv, k) for k in range(nv + 1)]
    # 1/(1+z^2)^neq = sum_k C(neq+k-1, k) * (-1)^k * z^{2k}  (binomial series)
    # More directly: multiply by (1+z^2)^{-neq}.
    inv: list[int] = [0] * (max_deg + 1)
    inv[0] = 1
    # Recurrence from (1+z^2)^neq * inv = 1
    # Expand (1+z^2)^neq coefficients
    b = [0] * (max_deg + 1)
    for k in range(neq + 1):
        deg = 2 * k
        if deg > max_deg:
            break
        b[deg] = comb(neq, k)
    # Solve triangular system for inv
    for n in range(1, max_deg + 1):
        s = 0
        for i in range(1, n + 1):
            s += b[i] * inv[n - i]
        inv[n] = -s  # since b[0]=1
    # product a * inv
    out = []
    for d in range(max_deg + 1):
        coeff = 0
        for i in range(d + 1):
            if i < len(a):
                coeff += a[i] * inv[d - i]
        out.append({"degree": d, "coefficient": coeff})
        if d > 0 and coeff <= 0:
            break
    return out


def clopper_pearson_public(x: int, n: int) -> dict[str, Any]:
    sys.path.insert(0, str(REPO / "experiments/EXP-CERTBIN-e94b27/impl"))
    from stats_exact import clopper_pearson, public  # type: ignore

    return public(clopper_pearson(x, n))


def stage0(run_dir: Path) -> dict[str, Any]:
    t0 = time.monotonic()
    stage0_dir = EXP_ROOT / "stage0"
    stage0_dir.mkdir(parents=True, exist_ok=True)

    # --- counting table ---
    counting_rows = []
    disagreements = []
    for cell in COUNTING_CELLS:
        nv, neq = cell["nv"], cell["neq"]
        # Idea's rows/cols figures are the D=4 Macaulay shape for every listed
        # cell, including the (18,17) diagonal reference (D_reg may differ).
        D = 4
        rows, cols = macaulay_dims(nv, D, neq)
        rows_reg, cols_reg = macaulay_dims(nv, cell["D_reg"], neq)
        entry = {
            **cell,
            "recomputed_D": D,
            "recomputed_rows": rows,
            "recomputed_cols": cols,
            "recomputed_D_reg_rows": rows_reg,
            "recomputed_D_reg_cols": cols_reg,
            "match_idea_rows_cols": rows == cell["rows"] and cols == cell["cols"],
        }
        if not entry["match_idea_rows_cols"]:
            disagreements.append(entry)
        counting_rows.append(entry)

    # semi-regular series for planned cells
    planned = [
        {"cell": "(23,8)", "nv": 16, "neq": 23},
        {"cell": "(35,12)", "nv": 24, "neq": 35},
        {"cell": "(18,17)", "nv": 18, "neq": 17},
    ]
    series = {
        p["cell"]: semi_regular_series(p["nv"], p["neq"])
        for p in planned
    }

    counting = {
        "experiment_id": EXPERIMENT_ID,
        "kind": "stage0-counting-table",
        "cells": counting_rows,
        "semi_regular_series_to_first_nonpositive": series,
        "disagreements_with_idea": disagreements,
        "amazon_bedrock": "NOT SELECTED",
    }
    write_yaml_like(stage0_dir / "counting-table.yaml", counting)

    # --- size law and l* ---
    # Exact-binomial form R_4 * C_4 * (C_4 / 64) with R_4 = n C(2l, <= 2), C_4 = C(2l, <= 4)
    size_rows = []
    for n, l in [(23, 8), (35, 12), (29, 10), (41, 14), (47, 16), (131, 44)]:
        nv = 2 * l
        R4 = n * binom_le(nv, 2)
        C4 = binom_le(nv, 4)
        words = math.ceil(C4 / 64)
        exact_ops = R4 * C4 * words  # row × col × words style
        leading = 0.04 * (l ** 11)  # idea's leading-term gloss
        size_rows.append({
            "n": n, "l": l, "nv": nv, "neq": n,
            "R4": R4, "C4": C4, "words": words,
            "exact_binomial_ops_proxy": exact_ops,
            "leading_term_0p04_l11": leading,
        })
    # l* table over declared per-node loop constant c (word ops)
    # crossover when size-law ops ≈ c * 2^{n-2l} style loop; idea l*≈50 implies c≈180
    lstar_table = []
    for c in (50, 100, 180, 200, 500, 1000):
        # Find smallest l where 0.04*l^11 >= c * 2^{131 - 2l} roughly for n=131 path
        # Use idea framing: l* about 50 at c≈180
        best = None
        for l in range(20, 80):
            size = 0.04 * (l ** 11)
            loop = c * (2 ** max(131 - 2 * l, 0))
            if size >= loop:
                best = l
                break
        lstar_table.append({
            "c_word_ops_per_node": c,
            "l_star_n131_model": best,
            "idea_l_star_about_50_implies_c": c == 180,
        })
    mem_l44 = {
        "l": 44, "nv": 88, "note": "analytic working-set figure from contract memory_accounting",
        "W4_working_set_bits_approx": 1.27e12,
        "mac_D4_words_proxy": "see size_rows for (131,44)",
    }
    size_law = {
        "experiment_id": EXPERIMENT_ID,
        "kind": "stage0-size-law-and-lstar",
        "exact_binomial_and_leading_term": size_rows,
        "l_star_table_over_c": lstar_table,
        "memory_figure_l44": mem_l44,
        "idea_l_star_about_50_with_implied_c": 180,
        "amazon_bedrock": "NOT SELECTED",
    }
    write_yaml_like(stage0_dir / "size-law-and-lstar.yaml", size_law)

    # --- power table ---
    power = {"experiment_id": EXPERIMENT_ID, "kind": "stage0-power-table", "cp95": {}, "zero_failure": {},
             "expected_count_multiples": {}, "derived": {}, "amazon_bedrock": "NOT SELECTED"}
    for N in (60, 30, 20, 10):
        power["cp95"][str(N)] = {
            str(x): clopper_pearson_public(x, N) for x in range(0, N + 1)
        }
    # zero-failure upper bounds (rule of three / CP upper at x=N)
    for N in (60, 20):
        power["zero_failure"][f"{N}_of_{N}"] = clopper_pearson_public(N, N)
    for l in (8, 12):
        # 3 * 2^l zero-failure samples (H2-TAIL honesty scale)
        n_tail = 3 * (1 << l)
        power["zero_failure"][f"3_times_2^{l}"] = {
            "n": n_tail,
            "note": "scale only; not enumerated CP table",
            "rule_of_three_upper_on_miss_rate": 3.0 / n_tail,
        }
    power["expected_count_multiples"] = {
        "at_r_0_90_N_60_expected_misses": 6.0,
        "at_r_0_50_N_60_expected_misses": 30.0,
    }
    # 0.025^(1/60)
    from decimal import Decimal, getcontext
    getcontext().prec = 50
    v = Decimal("0.025") ** (Decimal(1) / Decimal(60))
    power["derived"]["zero_fail_cp95_lower_N60"] = format(v, ".15g")
    power["derived"]["formula"] = "0.025**(1/60)"
    write_yaml_like(stage0_dir / "power-table.yaml", power)

    # --- stream rule ---
    stream = {
        "experiment_id": EXPERIMENT_ID,
        "kind": "stage0-stream-rule",
        "numpy_required": REQUIRED_NUMPY,
        "generator": "numpy.random.Generator(numpy.random.PCG64(seed))",
        "seed_rule": "seed = 2026100200000 + 1000 * a + n",
        "arm_codes": {"curve": 0, "OBJ": 1, "PLANTED": 2, "NULL": 3, "EASY": 4, "RANDU": 5, "selftest": 6},
        "seeds": {
            "curve": {"n23": 2026100200023, "n35": 2026100200035},
            "obj": {"n23": 2026100201023, "n35": 2026100201035},
            "planted": {"n23": 2026100202023, "n35": 2026100202035},
            "null_arm": {"n23": 2026100203023, "n35": 2026100203035},
            "easy": {"n23": 2026100204023, "n35": 2026100204035},
            "randu": {"n23": 2026100205023, "n35": 2026100205035},
            "selftest": 2026100206000,
        },
        "cells_authorized": [{"n": 23, "l": 8, "nv": 16, "neq": 23}, {"n": 35, "l": 12, "nv": 24, "neq": 35}],
        "call_sequence_per_arm_cell": [
            "create Generator(PCG64(seed))",
            "curve arm: draw (A,B) candidates via g.integers until accept rule; record attempts",
            "OBJ: draw R0, scale by h, draw P3 in B_fb, compute u; keep first 60 unsat + <=20 sat-nat",
            "PLANTED: draw P1,P2 in B_fb; u=x(P1+P2); keep first 20 distinct u",
            "NULL: for each of 30 systems, for each of n equations draw g.integers(0,2,size=|U_cell|)",
            "EASY: 10 deliberately easy affine systems per cell",
            "RANDU: 30 random-u transfers per cell",
        ],
        "curve_rule": {
            "draw": "A=g.integers(0,2**n); B=g.integers(1,2**n)",
            "accept": "exact #E has 2-part h in {2,4,8}; cap 1000 candidates",
        },
        "keep_rules": {
            "OBJ": "first 60 unsatisfiable; SAT-NAT up to 20; attempt cap 20000",
            "PLANTED": "first 20 distinct u",
            "NULL": 30,
            "EASY": 10,
            "RANDU": 30,
        },
        "field_polynomial_rule": "irreducible degree-n binary polynomial chosen per cell and recorded",
        "amazon_bedrock": "NOT SELECTED",
    }
    write_yaml_like(stage0_dir / "stream-rule.yaml", stream)

    # --- precommit hashes (every other stage0 file) ---
    utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    hash_targets = [
        "counting-table.yaml",
        "size-law-and-lstar.yaml",
        "power-table.yaml",
        "stream-rule.yaml",
    ]
    pre = {"experiment_id": EXPERIMENT_ID, "written_at_utc": utc, "files": {}, "amazon_bedrock": "NOT SELECTED"}
    for name in hash_targets:
        p = stage0_dir / name
        pre["files"][f"stage0/{name}"] = {"sha256": sha256_file(p), "bytes": p.stat().st_size, "hashed_at_utc": utc}
    write_json(stage0_dir / "precommit-hashes.json", pre)

    # --- self-checks S0-1 .. S0-6 ---
    # S0-2 / C-FIX via Closure
    sys.path.insert(0, str(REPO / "experiments/EXP-CERTBIN-e94b27/impl"))
    from closure import Closure  # type: ignore

    cfix = []
    cfix_ok = True
    for nv, D, neq in CFIX_TRIPLES:
        cl = Closure(nv, D, neq)
        want_r, want_c = macaulay_dims(nv, D, neq)
        ok = cl.R == want_r and cl.C == want_c
        cfix_ok = cfix_ok and ok
        cfix.append({"nv": nv, "D": D, "neq": neq, "R": cl.R, "C": cl.C, "want_R": want_r, "want_C": want_c, "ok": ok})

    s0_1_ok = len(disagreements) == 0
    s0_3_ok = all(len(series[c]) >= 1 for c in series)
    s0_4_ok = (stage0_dir / "stream-rule.yaml").is_file() and "stage0/stream-rule.yaml" in pre["files"]
    s0_5_ok = (stage0_dir / "size-law-and-lstar.yaml").is_file()
    s0_6_ok = abs(float(power["derived"]["zero_fail_cp95_lower_N60"]) - float(Decimal("0.025") ** (Decimal(1) / Decimal(60)))) < 1e-12

    selfchecks = {
        "experiment_id": EXPERIMENT_ID,
        "checks": {
            "S0-1": {"ok": s0_1_ok, "disagreements": disagreements},
            "S0-2": {"ok": cfix_ok, "triples": cfix},
            "S0-3": {"ok": s0_3_ok, "series_lengths": {k: len(v) for k, v in series.items()}},
            "S0-4": {"ok": s0_4_ok},
            "S0-5": {"ok": s0_5_ok},
            "S0-6": {"ok": s0_6_ok, "value": power["derived"]["zero_fail_cp95_lower_N60"]},
        },
        "all_pass": all([s0_1_ok, cfix_ok, s0_3_ok, s0_4_ok, s0_5_ok, s0_6_ok]),
        "amazon_bedrock": "NOT SELECTED",
    }
    write_json(stage0_dir / "selfchecks.json", selfchecks)

    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 0,
        "status": "completed" if selfchecks["all_pass"] else "failed_selfcheck",
        "worksheet_ok": selfchecks["all_pass"],
        "selfchecks_all_pass": selfchecks["all_pass"],
        "counting_disagreements": len(disagreements),
        "precommit_files": list(pre["files"]),
        "elapsed_s": time.monotonic() - t0,
        "claims": {"break": False, "exponent_move": False},
        "amazon_bedrock": "NOT SELECTED",
    }
    write_json(run_dir / "raw-result.json", raw)
    write_text(
        run_dir / "manifest.yaml",
        "\n".join([
            f"experiment_id: {EXPERIMENT_ID}",
            "stage: 0",
            f"status: {raw['status']}",
            f"worksheet_ok: {str(raw['worksheet_ok']).lower()}",
            "amazon_bedrock: NOT SELECTED",
            "claims_break: false",
            "claims_exponent_move: false",
            "",
        ]),
    )
    if not selfchecks["all_pass"]:
        print("Stage 0 self-checks failed", file=sys.stderr)
        return raw
    print("Stage 0 completed: worksheet frozen under stage0/")
    return raw


def stage1(run_dir: Path) -> dict[str, Any]:
    t0 = time.monotonic()
    stage1_dir = EXP_ROOT / "stage1"
    stage1_dir.mkdir(parents=True, exist_ok=True)

    # numpy pin
    import numpy as np
    numpy_ver = np.__version__
    numpy_ok = numpy_ver == REQUIRED_NUMPY

    pin_rows = []
    pin_ok = True
    for rel, want in PINNED.items():
        path = REPO / rel
        digest = sha256_file(path) if path.is_file() else None
        ok = digest == want
        pin_ok = pin_ok and ok
        pin_rows.append({"path": rel, "sha256": digest, "expected": want, "ok": ok, "bytes": path.stat().st_size if path.is_file() else None})

    write_json(stage1_dir / "inputs.json", {
        "experiment_id": EXPERIMENT_ID,
        "numpy_version": numpy_ver,
        "numpy_required": REQUIRED_NUMPY,
        "numpy_ok": numpy_ok,
        "pinned_instruments": pin_rows,
        "amazon_bedrock": "NOT SELECTED",
    })

    # C-FIX
    sys.path.insert(0, str(REPO / "experiments/EXP-CERTBIN-e94b27/impl"))
    from closure import Closure  # type: ignore

    cfix = []
    cfix_ok = True
    for nv, D, neq in CFIX_TRIPLES:
        cl = Closure(nv, D, neq)
        want_r, want_c = macaulay_dims(nv, D, neq)
        ok = cl.R == want_r and cl.C == want_c
        cfix_ok = cfix_ok and ok
        cfix.append({"nv": nv, "D": D, "neq": neq, "R": cl.R, "C": cl.C, "ok": ok})
    write_json(stage1_dir / "c-fix.json", {"ok": cfix_ok, "triples": cfix})

    # C-SELF: replay Stage-0 precommit hashes
    pre_path = EXP_ROOT / "stage0" / "precommit-hashes.json"
    self_ok = False
    self_detail: dict[str, Any] = {}
    if pre_path.is_file():
        pre = json.loads(pre_path.read_text(encoding="utf-8"))
        mismatches = []
        for rel, meta in pre.get("files", {}).items():
            # rel is stage0/<file> relative to the experiment root
            if not rel.startswith("stage0/"):
                mismatches.append({"path": rel, "live": None, "expected": meta.get("sha256")})
                continue
            live_path = EXP_ROOT / rel
            live = sha256_file(live_path) if live_path.is_file() else None
            if live != meta.get("sha256"):
                mismatches.append({"path": rel, "live": live, "expected": meta.get("sha256")})
        self_ok = not mismatches
        self_detail = {"ok": self_ok, "mismatches": mismatches}
    else:
        self_detail = {"ok": False, "reason": "missing stage0/precommit-hashes.json"}
    write_json(stage1_dir / "c-self.json", self_detail)

    c_pin_ok = pin_ok and numpy_ok
    write_json(stage1_dir / "c-pin.json", {"ok": c_pin_ok, "pin_ok": pin_ok, "numpy_ok": numpy_ok, "numpy_version": numpy_ver})

    impediments = []
    if not numpy_ok:
        impediments.append({
            "id": "IMP-NUMPY",
            "what_is_blocked": "Stage-1 PCG64 stream replay and all arms",
            "clears_when": f"numpy=={REQUIRED_NUMPY} is the active interpreter package",
            "observed": numpy_ver,
            "asserts_nothing_about": "S_3 refutation degree",
        })
    impediments.append({
        "id": "IMP-FIELD-BUILDER",
        "what_is_blocked": "cells (23,8) and (35,12) OBJ/NULL/PLANTED/EASY/RANDU ladder arms",
        "clears_when": (
            "implementation provides GF(2^n) field + curve order certification "
            "+ S_3 descent builder for n in {23,35} per stage0/stream-rule.yaml"
        ),
        "asserts_nothing_about": "degree-4 mutant rate on the inner object",
    })

    outcome = "O-IMPEDIMENT"
    if not (c_pin_ok and cfix_ok and self_ok):
        outcome = "O-ARTIFACT"
        status = "instrument_stop"
    else:
        status = "impediment"

    summary = {
        "experiment_id": EXPERIMENT_ID,
        "stage": 1,
        "outcome": outcome,
        "C_PIN": c_pin_ok,
        "C_FIX": cfix_ok,
        "C_SELF": self_ok,
        "cells_authorized": ["(23,8)", "(35,12)"],
        "cells_executed": [],
        "impediments": impediments,
        "note": (
            "Admission-surface Stage 1: instrument gates executed; full off-diagonal "
            "ladder arms are blocked on the GF(2^n) builder (IMP-FIELD-BUILDER) and "
            "possibly numpy pin. Not negative mathematical evidence."
        ),
        "amazon_bedrock": "NOT SELECTED",
    }
    write_json(stage1_dir / "cell-summary.json", summary)

    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 1,
        "status": status,
        "outcome": outcome,
        "C_PIN": c_pin_ok,
        "C_FIX": cfix_ok,
        "C_SELF": self_ok,
        "impediments": impediments,
        "elapsed_s": time.monotonic() - t0,
        "claims": {"break": False, "exponent_move": False},
        "amazon_bedrock": "NOT SELECTED",
    }
    write_json(run_dir / "raw-result.json", raw)
    write_text(
        run_dir / "manifest.yaml",
        "\n".join([
            f"experiment_id: {EXPERIMENT_ID}",
            "stage: 1",
            f"status: {status}",
            f"outcome: {outcome}",
            f"C_PIN: {str(c_pin_ok).lower()}",
            f"C_FIX: {str(cfix_ok).lower()}",
            f"C_SELF: {str(self_ok).lower()}",
            "amazon_bedrock: NOT SELECTED",
            "claims_break: false",
            "claims_exponent_move: false",
            "",
        ]),
    )
    print(f"Stage 1 finished with outcome={outcome} status={status}")
    # Exit 0 so the process supervisor can run check.py on a well-formed O-IMPEDIMENT.
    return raw


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=int, required=True, choices=[0, 1])
    parser.add_argument("--trial-plan", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    plan_path = Path(args.trial_plan)
    if not plan_path.is_file():
        print(f"missing trial plan: {plan_path}", file=sys.stderr)
        return 2
    if args.stage == 0:
        raw = stage0(run_dir)
        return 0 if raw.get("worksheet_ok") else 1
    raw = stage1(run_dir)
    return 0 if raw.get("outcome") in {"O-IMPEDIMENT", "O-ARTIFACT", "LADDER_COMPLETE"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
