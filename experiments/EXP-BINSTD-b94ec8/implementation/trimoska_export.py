#!/usr/bin/env python3
"""Export Semaev m=4 CNF-XOR/ANF via vendored TRIMOSKA Weil_descent C generator.

Wraps inputs/TRIMOSKA-ECICB-2024/upstream/Weil_descent (weill) + assemble_*.sh.
Produces the sparse ANF/DIMACS dialect WDSat expects. Factor-base model is the
polynomial window {deg < l} only — Frobenius-stable bases use semaev_export.py.

No Magma/Sage/AUXIN/Bedrock.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
WEIL_SRC = REPO_ROOT / "inputs" / "TRIMOSKA-ECICB-2024" / "upstream" / "Weil_descent"


def int_to_low_first_bits(v: int, width: int) -> str:
    return "".join("1" if (v >> i) & 1 else "0" for i in range(width))


def _sync_weil_sources(work: Path) -> None:
    """Copy vendored Weil_descent sources into work/ once."""
    if not WEIL_SRC.is_dir():
        raise FileNotFoundError(f"missing vendored Weil_descent at {WEIL_SRC}")
    if (work / "main.c").is_file():
        return
    for p in WEIL_SRC.iterdir():
        dest = work / p.name
        if p.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(p, dest)
        else:
            shutil.copy2(p, dest)


def _build_weill(work: Path) -> Path:
    """Compile weill in work/. Must be re-run after action 22 (rewrites terms.h)."""
    c_files = sorted(p.name for p in work.glob("*.c"))
    log = subprocess.run(
        ["gcc", "-O2", *c_files, "-o", "weill"],
        cwd=work,
        capture_output=True,
        text=True,
        check=False,
    )
    with (work / "build_weill.log").open("a", encoding="utf-8") as fh:
        fh.write((log.stdout or "") + "\n---\n" + (log.stderr or "") + f"\nrc={log.returncode}\n")
    exe = work / "weill"
    if log.returncode != 0 or not exe.is_file():
        raise RuntimeError(f"weill build failed rc={log.returncode}")
    return exe


def export_window_instance(
    *,
    n: int,
    l: int,
    modulus: int,
    xR: int,
    work_dir: Path,
    formats: tuple[str, ...] = ("anf", "cnfxor"),
) -> dict[str, Any]:
    """Run weill actions 2/22/3 (rebuild between steps) and assemble ANF + CNF-XOR."""
    work_dir.mkdir(parents=True, exist_ok=True)
    _sync_weil_sources(work_dir)
    out = work_dir / "out"
    out.mkdir(exist_ok=True)
    # Clear previous assemble outputs
    for pat in ("*.fordimacs", "*.forxorDand", "weil.anf", "weil.dimacs", "magma.in"):
        for f in out.glob(pat):
            f.unlink()

    rbits = int_to_low_first_bits(modulus, n + 1)
    xbits = int_to_low_first_bits(xR, n)
    # script_benchmarks.sh rebuilds after each action: action 22's create_semaev()
    # rewrites terms.h, which action 3 must be linked against. Cache the
    # (n,l,modulus) skeleton (actions 2+22) so only action 3 re-runs per xR.
    stamp = work_dir / f".skeleton_n{n}_l{l}_m{modulus:x}.ok"
    if not stamp.is_file():
        for action in (2, 22):
            exe = _build_weill(work_dir)
            cmd = [
                str(exe),
                "-a",
                str(action),
                "-n",
                str(n),
                "-l",
                str(l),
                "-r",
                rbits,
                "-x",
                xbits,
                "-o",
                "dimacs",
            ]
            proc = subprocess.run(
                cmd, cwd=work_dir, capture_output=True, text=True, check=False
            )
            if proc.returncode != 0:
                raise RuntimeError(
                    f"weill -a {action} failed rc={proc.returncode}: {proc.stderr[:400]}"
                )
        # Compile once with post-22 terms.h for subsequent action-3 runs.
        _build_weill(work_dir)
        stamp.write_text("ok\n", encoding="utf-8")

    exe = work_dir / "weill"
    if not exe.is_file():
        exe = _build_weill(work_dir)
    cmd = [
        str(exe),
        "-a",
        "3",
        "-n",
        str(n),
        "-l",
        str(l),
        "-r",
        rbits,
        "-x",
        xbits,
        "-o",
        "dimacs",
    ]
    proc = subprocess.run(cmd, cwd=work_dir, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(
            f"weill -a 3 failed rc={proc.returncode}: {proc.stderr[:400]}"
        )

    formats_out: dict[str, str] = {}
    if "anf" in formats:
        a = subprocess.run(
            ["bash", "assemble_anf.sh"],
            cwd=out,
            capture_output=True,
            text=True,
            check=False,
        )
        if a.returncode != 0 or not (out / "weil.anf").is_file():
            raise RuntimeError(f"assemble_anf failed: {a.stderr[:400]}")
        formats_out["anf"] = (out / "weil.anf").read_text(encoding="utf-8")
    if "cnfxor" in formats:
        d = subprocess.run(
            ["bash", "assemble_dimacs.sh"],
            cwd=out,
            capture_output=True,
            text=True,
            check=False,
        )
        if d.returncode != 0 or not (out / "weil.dimacs").is_file():
            raise RuntimeError(f"assemble_dimacs failed: {d.stderr[:400]}")
        formats_out["cnfxor"] = (out / "weil.dimacs").read_text(encoding="utf-8")

    header = (formats_out.get("anf") or formats_out.get("cnfxor") or "").splitlines()[:1]
    n_vars = n_eq = None
    if header and header[0].startswith("p cnf"):
        toks = header[0].split()
        n_vars, n_eq = int(toks[2]), int(toks[3])

    return {
        "exporter": "trimoska_weil_descent_c",
        "source": str(WEIL_SRC.relative_to(REPO_ROOT)),
        "n": n,
        "l": l,
        "m_fb": 3,
        "arity_m": 4,
        "basis_kind": "window_deg",
        "modulus": modulus,
        "xR": xR,
        "n_vars": n_vars,
        "n_equations": n_eq,
        "formats": formats_out,
    }
