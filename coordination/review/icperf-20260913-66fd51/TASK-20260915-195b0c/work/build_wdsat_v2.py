#!/usr/bin/env python3
"""Independent WDSat build for TASK-20260915-195b0c (validator, joint V2).

Rewrites the vendored src/config.h static-allocation block with sizing constants
derived by work/anf_check.py from the instance ANF, then runs `make`.  Written
from the vendored makefile and config.h; it does not import bench.py.

The active (uncommented) `#define __X__ v` lines for the sized constants are
dropped and replaced by an explicit block; `__XG_ENHANCED__` is left exactly as
shipped, because changing it would change the solver's branching set.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

WDSAT_SRC = Path("/workspace/inputs/TRIMOSKA-WDSAT-2024/upstream/src")
SIZED = ("MAX_ANF_ID", "MAX_DEGREE", "MAX_ID", "MAX_EQ", "MAX_EQ_SIZE",
         "MAX_XEQ", "MAX_XEQ_SIZE", "MAX_BUFFER_SIZE")


def build(consts: dict, root: Path) -> Path:
    consts = {k: consts[k] for k in SIZED}
    sig = "_".join(f"{k}{v}" for k, v in sorted(consts.items()))
    bdir = root / f"v2_{hashlib.sha1(sig.encode()).hexdigest()[:10]}"
    exe = bdir / "wdsat_solver"
    if exe.exists():
        return exe
    shutil.copytree(WDSAT_SRC, bdir / "src")
    cfg = bdir / "src" / "config.h"
    out, in_comment = [], False
    for ln in cfg.read_text().splitlines():
        s = ln.strip()
        if in_comment:
            out.append(ln)
            if "*/" in s:
                in_comment = False
            continue
        if s.startswith("/*") and "*/" not in s:
            in_comment = True
            out.append(ln)
            continue
        m = re.match(r"#define __(\w+)__\s", s)
        if m and m.group(1) in consts:
            continue
        out.append(ln)
    out.append("/* TASK-20260915-195b0c independent sizing */")
    out += [f"#define __{k}__ {v}" for k, v in consts.items()]
    cfg.write_text("\n".join(out) + "\n")
    (bdir / "config_used.json").write_text(json.dumps(consts, indent=1))
    log = subprocess.run(["make"], cwd=bdir / "src", capture_output=True, text=True)
    (bdir / "make.log").write_text(log.stdout + "\n--- stderr ---\n" + log.stderr)
    if log.returncode != 0 or not exe.exists():
        raise SystemExit(f"build failed in {bdir}\n{log.stderr[-2000:]}")
    return exe


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    from anf_check import parse_anf, sizing  # noqa: E402

    anf, root = Path(sys.argv[1]), Path(sys.argv[2])
    s = sizing(parse_anf(anf))
    s["MAX_BUFFER_SIZE"] = 60000          # the frozen contract's value
    exe = build(s, root)
    print(json.dumps({"anf": str(anf), "exe": str(exe),
                      "consts": {k: s[k] for k in SIZED},
                      "sha256": hashlib.sha256(exe.read_bytes()).hexdigest()}, indent=1))
