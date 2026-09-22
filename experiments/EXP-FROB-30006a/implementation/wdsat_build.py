#!/usr/bin/env python3
"""Size and build WDSat (vendored SRC-ICPERF-TRIMOSKA-WDSAT-2024 source) for ONE ANF.

WDSat allocates statically from compile-time constants in src/config.h; every
constant here is derived from the ANF the binary will solve (C-SIZE: MAX_ID must
equal the ANF-derived value or the run is invalid).  The same discipline as
EXP-ICPERF-66fd51/e21835 `bench.py::anf_sizing/build_wdsat`, re-implemented and
extended with the line-length constant __STATIC_CLAUSE_STRING_SIZE__
(wdsat_utils.h, shipped 30000 bytes) which the dense descended equations of the
n = 43 cell exceed.

  MAX_ANF_ID      = unary variables + 1          (README: "always add +1")
  MAX_DEGREE      = max monomial degree + 1
  MAX_ID          = unary variables + distinct non-unary monomials  (exact: the solver
                    itself reports this number when the constant is wrong)
  MAX_EQ          = sum over non-unary monomials of (degree + 1) + 64   (OR-clauses)
  MAX_EQ_SIZE     = MAX_DEGREE + 1
  MAX_XEQ         = XOR equations + 1
  MAX_XEQ_SIZE    = MAX_ID   (XOR clauses can grow to every variable under Gaussian elimination)
  MAX_BUFFER_SIZE = 60000, doubled by the caller when the solver reports it is too small
  STATIC_CLAUSE_STRING_SIZE = max(30000, longest ANF line + 4096)
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

REPO = Path(__file__).resolve().parents[3]
WDSAT_SRC = REPO / "inputs/TRIMOSKA-WDSAT-2024/upstream/src"
UPSTREAM_SUMS = REPO / "inputs/TRIMOSKA-WDSAT-2024/UPSTREAM_SHA256SUMS.txt"
SIZED = ("MAX_ANF_ID", "MAX_DEGREE", "MAX_ID", "MAX_EQ", "MAX_EQ_SIZE", "MAX_XEQ", "MAX_XEQ_SIZE", "MAX_BUFFER_SIZE")


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify_vendored_source() -> dict:
    """Every file under upstream/src must hash to its UPSTREAM_SHA256SUMS.txt entry."""
    sums = {}
    for ln in UPSTREAM_SUMS.read_text().splitlines():
        h, p = ln.split(None, 1)
        sums[p.strip()] = h
    report = {"checked": 0, "mismatches": [], "files": {}}
    for p in sorted(WDSAT_SRC.iterdir()):
        key = f"./src/{p.name}"
        h = sha256_file(p)
        report["files"][p.name] = h
        report["checked"] += 1
        if sums.get(key) != h:
            report["mismatches"].append(p.name)
    report["ok"] = not report["mismatches"] and report["checked"] == 15
    return report


def parse_anf_equation(tokens: List[str]) -> Tuple[List[Tuple[int, ...]], bool]:
    terms: List[Tuple[int, ...]] = []
    const = False
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t == "T":
            const = not const
            i += 1
        elif t.startswith("."):
            d = int(t[1:])
            terms.append(tuple(sorted(int(v) for v in tokens[i + 1:i + 1 + d])))
            i += 1 + d
        else:
            terms.append((int(t),))
            i += 1
    return terms, const


def anf_sizing(anf_path: Path) -> dict:
    src = anf_path.read_text()
    nv = ne = None
    monos = set()
    maxdeg, maxterms, maxline, n_eq, total_terms = 1, 0, 0, 0, 0
    for ln in src.splitlines():
        if ln.startswith("p cnf"):
            _, _, a, b = ln.split()
            nv, ne = int(a), int(b)
            continue
        t = ln.split()
        if not t or t[0] != "x":
            continue
        n_eq += 1
        maxline = max(maxline, len(ln))
        terms, _ = parse_anf_equation(t[1:-1])
        maxterms = max(maxterms, len(terms))
        total_terms += len(terms)
        for m in terms:
            if len(m) > 1:
                monos.add(m)
                maxdeg = max(maxdeg, len(m))
    if nv is None or n_eq != ne:
        raise ValueError(f"{anf_path}: header/equation-count mismatch ({n_eq} vs {ne})")
    max_id = nv + len(monos)
    max_eq = sum(len(m) + 1 for m in monos) + 64
    # MAX_BUFFER_SIZE holds every XOR atom and every OR-clause atom (dimacs.c asserts on it);
    # the initial value is derived from the ANF and the caller still doubles on failure.
    buffer = max(60000, 4 * total_terms + max_eq * (maxdeg + 2))
    return {"MAX_ANF_ID": nv + 1, "MAX_DEGREE": maxdeg + 1, "MAX_ID": max_id,
            "MAX_EQ": max_eq, "MAX_EQ_SIZE": maxdeg + 2,
            "MAX_XEQ": ne + 1, "MAX_XEQ_SIZE": max_id, "MAX_BUFFER_SIZE_initial": buffer,
            "STATIC_CLAUSE_STRING_SIZE": max(30000, maxline + 4096),
            "n_unary": nv, "n_eqs": ne, "n_nonunary_monomials": len(monos),
            "max_terms_per_eq": maxterms, "total_terms": total_terms, "max_line_chars": maxline}


def static_memory_estimate_bytes(c: dict) -> dict:
    """Rough size of the largest static arrays (bytes) for the given constants, from the
    declarations in dimacs.c / xorgauss.c / xorset.c (int_t = 8 bytes)."""
    id_size = c["MAX_ID"] + 1
    sz_gauss = id_size // 64 + 1
    est = {
        "xorgauss_equivalency_history": c["MAX_ANF_ID"] * id_size * sz_gauss * 8,
        "xorgauss_mask_list": id_size * (id_size + 1) * 8,
        "xorgauss_equivalency+mask": 2 * id_size * sz_gauss * 8,
        "monomials_to_column": c["MAX_ANF_ID"] * id_size * (c["MAX_DEGREE"] - 1) * 8,
        "xorset_history_s_u": 2 * id_size * c["MAX_XEQ_SIZE"] * 8,
        "xor_equation_x2": 2 * c["MAX_XEQ"] * c["MAX_XEQ_SIZE"] * 8,
        "dimacs_boolean_equation": c["MAX_EQ"] * c["MAX_EQ_SIZE"] * 8,
        "xorgauss_current_degree_history": c["MAX_ANF_ID"] * id_size,
        "xorgauss_equivalent_history": c["MAX_ANF_ID"] * id_size,
        "xorgauss_assignment_buffer_history": c["MAX_ANF_ID"] * 2 * id_size,
    }
    est["total_estimate"] = sum(est.values())
    return est


def _rewrite_config(text: str, consts: Dict[str, int], tag: str) -> str:
    """Drop every ACTIVE (non-commented) #define of a sized constant and append ours;
    the __XG_ENHANCED__ switch and all commented example blocks are left as shipped."""
    out = []
    in_comment = False
    for ln in text.splitlines():
        stripped = ln.strip()
        if in_comment:
            out.append(ln)
            if "*/" in stripped:
                in_comment = False
            continue
        if stripped.startswith("/*") and "*/" not in stripped:
            in_comment = True
            out.append(ln)
            continue
        m = re.match(r"#define __(\w+)__\s", stripped)
        if m and m.group(1) in consts:
            continue
        out.append(ln)
    out.append(f"/* {tag}: exact static sizing derived from the instance ANF */")
    for k in SIZED:
        out.append(f"#define __{k}__ {consts[k]}")
    return "\n".join(out) + "\n"


def build_wdsat(build_root: Path, sizing: dict, buffer_size: int | None = None, tag: str = "EXP-FROB-30006a") -> Tuple[Path, dict]:
    consts = {k: sizing[k] for k in SIZED if k != "MAX_BUFFER_SIZE"}
    consts["MAX_BUFFER_SIZE"] = buffer_size if buffer_size is not None else sizing["MAX_BUFFER_SIZE_initial"]
    clause_len = sizing["STATIC_CLAUSE_STRING_SIZE"]
    sig = "_".join(f"{k}{v}" for k, v in sorted(consts.items())) + f"_CLAUSE{clause_len}"
    bdir = build_root / f"wdsat_{hashlib.sha1(sig.encode()).hexdigest()[:10]}"
    exe = bdir / "wdsat_solver"
    if exe.exists():
        return exe, json.loads((bdir / "config_used.json").read_text())
    shutil.copytree(WDSAT_SRC, bdir / "src")
    cfg = bdir / "src" / "config.h"
    cfg.write_text(_rewrite_config(cfg.read_text(), consts, tag))
    utils = bdir / "src" / "wdsat_utils.h"
    utext = utils.read_text()
    if clause_len != 30000:
        new_utext, nsub = re.subn(r"#define __STATIC_CLAUSE_STRING_SIZE__ 30000",
                                  f"#define __STATIC_CLAUSE_STRING_SIZE__ {clause_len}", utext)
        if nsub != 1:
            raise RuntimeError("could not locate __STATIC_CLAUSE_STRING_SIZE__ in wdsat_utils.h")
        utils.write_text(new_utext)
    gcc = subprocess.run(["gcc", "--version"], capture_output=True, text=True).stdout.splitlines()[0]
    log = subprocess.run(["make"], cwd=bdir / "src", capture_output=True, text=True)
    (bdir / "make.log").write_text(log.stdout + "\n--- stderr ---\n" + log.stderr)
    used = {"constants": consts, "STATIC_CLAUSE_STRING_SIZE": clause_len,
            "compile_flags_from_makefile": "gcc -O3 -Wall -c <file>.c ; gcc *.o -o ../wdsat_solver -lm",
            "XG_ENHANCED_defined": "#define __XG_ENHANCED__" in cfg.read_text(),
            "compiler": gcc, "make_returncode": log.returncode,
            "source_sha256_as_shipped": verify_vendored_source()["files"],
            "config_h_sha256_used": sha256_file(cfg), "wdsat_utils_h_sha256_used": sha256_file(utils),
            "binary_sha256": sha256_file(exe) if exe.exists() else None,
            "static_memory_estimate_bytes": static_memory_estimate_bytes(consts),
            "max_id_anf_match": consts["MAX_ID"] == sizing["MAX_ID"]}
    (bdir / "config_used.json").write_text(json.dumps(used, indent=1))
    if log.returncode != 0 or not exe.exists():
        raise RuntimeError(f"WDSat build failed in {bdir}: {log.stderr[-500:]}")
    # keep the exact sources that were compiled; drop objects
    for o in (bdir / "src").glob("*.o"):
        o.unlink()
    return exe, used


def parse_wdsat_output(out_text: str) -> dict:
    lines = [ln.strip() for ln in out_text.splitlines() if ln.strip()]
    res = {"status": "unknown", "conflicts": None, "assignment": None, "solver_notes": [ln for ln in lines if ln.startswith("!!!")]}
    if any(ln.startswith("UNSAT") for ln in lines):
        idx = max(i for i, ln in enumerate(lines) if ln.startswith("UNSAT"))
        res["status"] = "UNSAT"
        if idx + 1 < len(lines) and lines[idx + 1].lstrip("-").isdigit():
            res["conflicts"] = int(lines[idx + 1])
        elif "XORGAUSS init" in lines[idx]:
            # wdsat.c:475: inconsistency found by the initial Gaussian elimination, before any branching
            res["conflicts"] = 0
            res["unsat_on_xorgauss_init"] = True
        return res
    bit_idx = [i for i, ln in enumerate(lines) if re.fullmatch(r"[01]{4,}", ln)]
    if bit_idx:
        i = bit_idx[-1]
        res["status"] = "SAT"
        res["assignment"] = lines[i]
        if i + 1 < len(lines) and lines[i + 1].lstrip("-").isdigit():
            res["conflicts"] = int(lines[i + 1])
    return res


if __name__ == "__main__":
    import sys
    p = Path(sys.argv[1])
    s = anf_sizing(p)
    print(json.dumps({"sizing": s, "memory_estimate": static_memory_estimate_bytes({**s, "MAX_BUFFER_SIZE": s["MAX_BUFFER_SIZE_initial"]})}, indent=1))
