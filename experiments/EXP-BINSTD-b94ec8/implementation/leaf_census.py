#!/usr/bin/env python3
"""Leaf/conflict census over Semaev m=4 ANF instances.

Primary instrument: vendored WDSat on TRIMOSKA-style ANF (`-i file -x`).
Fallback instrument: numpy exhaustive SAT table + chronological conflict count
for dense direct-encoding ANF (stable bases) when WDSat cannot allocate.

No Magma/Sage/AUXIN/Bedrock.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Iterable

import numpy as np


def median(xs: Iterable[int | float]) -> float | None:
    vals = sorted(float(x) for x in xs)
    if not vals:
        return None
    n = len(vals)
    mid = n // 2
    if n % 2:
        return vals[mid]
    return 0.5 * (vals[mid - 1] + vals[mid])


def build_wdsat(src_dir: Path, build_dir: Path) -> dict[str, Any]:
    """Build WDSat sized for n=31 TRIMOSKA weill ANF (IC-S4-ish caps)."""
    out: dict[str, Any] = {
        "build_ok": False,
        "binary": None,
        "binary_sha256": None,
        "error": None,
        "config": None,
    }
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True)
    shutil.copytree(src_dir, build_dir / "src")
    consts = {
        "MAX_ANF_ID": 64,
        "MAX_DEGREE": 8,
        "MAX_ID": 2048,
        "MAX_BUFFER_SIZE": 200000,
        "MAX_EQ": 8192,
        "MAX_EQ_SIZE": 9,
        "MAX_XEQ": 256,
        "MAX_XEQ_SIZE": 2048,
    }
    cfg = build_dir / "src" / "config.h"
    # Fresh minimal config (avoid stacked commented blocks).
    cfg.write_text(
        "\n".join(
            [
                "#define __XG_ENHANCED__",
                "/* EXP-BINSTD-b94ec8 Stage-2 Semaev census WDSat */",
                *[f"#define __{k}__ {v}" for k, v in consts.items()],
                "",
            ]
        ),
        encoding="utf-8",
    )
    out["config"] = consts
    (build_dir / "config_used.json").write_text(
        __import__("json").dumps(consts, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    objs = [
        "main.c",
        "wdsat_utils.c",
        "dimacs.c",
        "cnf.c",
        "xorset.c",
        "xorgauss.c",
        "wdsat.c",
    ]
    src = build_dir / "src"
    compile_log = []
    for c in objs:
        r = subprocess.run(
            ["gcc", "-O2", "-c", c],
            cwd=src,
            capture_output=True,
            text=True,
            check=False,
        )
        compile_log.append(f"## {c}\n{r.stdout}\n{r.stderr}\nrc={r.returncode}\n")
        if r.returncode != 0:
            out["error"] = f"compile failed: {c}"
            (build_dir / "make.log").write_text("\n".join(compile_log), encoding="utf-8")
            return out
    link = subprocess.run(
        ["gcc", "-O2", *[o.replace(".c", ".o") for o in objs], "-o", "../wdsat_solver", "-lm"],
        cwd=src,
        capture_output=True,
        text=True,
        check=False,
    )
    compile_log.append(f"## link\n{link.stdout}\n{link.stderr}\nrc={link.returncode}\n")
    (build_dir / "make.log").write_text("\n".join(compile_log), encoding="utf-8")
    exe = build_dir / "wdsat_solver"
    if link.returncode != 0 or not exe.is_file():
        out["error"] = "link failed or binary missing"
        return out
    import hashlib

    h = hashlib.sha256()
    with exe.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    out["build_ok"] = True
    out["binary"] = str(exe)
    out["binary_sha256"] = h.hexdigest()
    return out


def run_wdsat(binary: Path, anf_path: Path, timeout_s: float = 180.0) -> dict[str, Any]:
    t0 = time.time()
    proc = subprocess.run(
        [str(binary), "-i", str(anf_path), "-x"],
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout_s,
    )
    wall = time.time() - t0
    text = (proc.stdout or "") + "\n" + (proc.stderr or "")
    sat = None
    conflicts = None
    # WDSat prints SAT assignment line(s) or UNSAT, then a conflict count line.
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for ln in lines:
        if ln == "UNSAT":
            sat = False
        elif ln == "SAT":
            sat = True
        elif re.fullmatch(r"\d+", ln):
            conflicts = int(ln)
        elif re.fullmatch(r"[01]+", ln) and len(ln) >= 8:
            sat = True
    # Some builds print only the bitstring on SAT (no 'SAT' token).
    if sat is None and any(re.fullmatch(r"[01]+", ln) and len(ln) >= 8 for ln in lines):
        sat = True
    return {
        "instrument": "wdsat",
        "returncode": proc.returncode,
        "wall_clock_seconds": wall,
        "sat": sat,
        "conflicts": conflicts,
        "stdout_tail": "\n".join(lines[-12:]),
        "ok": conflicts is not None and sat is not None,
    }


def _eqs_to_masks(
    eqs: list[set[frozenset[int]]],
) -> list[tuple[list[int], int]]:
    meqs: list[tuple[list[int], int]] = []
    for eq in eqs:
        masks: list[int] = []
        const = 0
        for m in eq:
            if len(m) == 0:
                const ^= 1
            else:
                mask = 0
                for v in m:
                    mask |= 1 << v
                masks.append(mask)
        meqs.append((masks, const))
    return meqs


def numpy_conflict_census(
    n_vars: int,
    eqs: list[set[frozenset[int]]],
) -> dict[str, Any]:
    """Chronological conflict count via full satisfying-assignment table."""
    t0 = time.time()
    meqs = _eqs_to_masks(eqs)
    N = 1 << n_vars
    assign = np.arange(N, dtype=np.uint32)
    sat = np.ones(N, dtype=bool)
    for masks, const in meqs:
        s = np.full(N, const, dtype=np.uint8)
        for m in masks:
            s ^= ((assign & m) == m).astype(np.uint8)
        sat &= s == 0
    n_sat = int(sat.sum())

    # Chronological DPLL conflicts: trying a bit whose subdomain has no sat.
    conflicts = 0
    # Walk like a DFS counting dead children; use sat prefix masks.
    # prefix of length k with value p covers indices p << (n-k) ... 

    def any_sat(prefix: int, depth: int) -> bool:
        shift = n_vars - depth
        lo = prefix << shift
        hi = lo + (1 << shift)
        return bool(sat[lo:hi].any())

    def dfs(prefix: int, depth: int) -> bool:
        nonlocal conflicts
        if not any_sat(prefix, depth):
            return False
        if depth == n_vars:
            return True
        found = False
        for bit in (0, 1):
            child = (prefix << 1) | bit
            if any_sat(child, depth + 1):
                if dfs(child, depth + 1):
                    found = True
                    # For conflict counting we still explore? WDSat stops at first SAT.
                    # Match WDSat default: stop at first SAT.
                    return True
            else:
                conflicts += 1
        return found

    if n_sat == 0:
        # Whole space unsat: one root-level conflict (search refuses every branch).
        conflicts = 1
        is_sat = False
    else:
        is_sat = dfs(0, 0)
    return {
        "instrument": "numpy_dpll_sat_table",
        "n_vars": n_vars,
        "n_equations": len(eqs),
        "sat": bool(is_sat),
        "n_sat_assignments": n_sat,
        "conflicts": conflicts,
        "wall_clock_seconds": time.time() - t0,
        "ok": True,
    }
