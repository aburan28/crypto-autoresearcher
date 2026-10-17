"""wdsat_io.py -- m4-sat-cost-pilot. EXPLORATORY, hypothesis-generating; not program evidence.

ANF export of a boolsys Boolean system (list of equations, each a list of monomial
bitmasks over variables 0..N-1 in the boolsys layout u_0..u_{m-3}, x_0..x_{m-1}) to the
WDSat ANF format read by dimacs.c (dimacs_read_formula, `p cnf <nv> <ne>` header, lines
`x [T] [v | .d v1 .. vd]* 0`), with the variables RENUMBERED so that the m factor-base
unknowns come first (x_0 bits, x_1 bits, ..., then u_0 bits, ...). This is the paper's
convention (Trimoska-Ionica-Dequen 2019: x variables first, l bits each) and what the
`-b` symmetry-breaking mode of WDSat assumes (it branches on the first m*l variables).

Also: exact static sizing of the WDSat build per instance (the solver uses static
arrays, as in EXP-ICPERF-66fd51/code/bench.py:anf_sizing), a patched build that adds two
counters to the solver's own `conf` counter (nodes = branch points opened, fails =
failed branch inferences), running with a timeout, and output parsing.
"""
from __future__ import annotations

import hashlib
import json
import re
import resource
import shutil
import subprocess
import time
from pathlib import Path

WDSAT_SRC = Path("/tmp/claude-0/-home-user/f42055f8-3588-569d-b7d9-926d696d2468/scratchpad/iterate/tools/wdsat_987b7f5ef9")
BUILD_ROOT = Path("/tmp/claude-0/-home-user/f42055f8-3588-569d-b7d9-926d696d2468/scratchpad/m4sat/build")


def permutation(n, k, m):
    """boolsys variable index -> 1-based WDSat id, x's first then u's."""
    N = (m - 2) * n + m * k
    perm = [0] * N
    for i in range(m):
        for j in range(k):
            perm[(m - 2) * n + i * k + j] = i * k + j + 1
    for i in range(m - 2):
        for j in range(n):
            perm[i * n + j] = m * k + i * n + j + 1
    assert sorted(perm) == list(range(1, N + 1))
    return perm


def export_anf(system):
    """Returns (text, meta). WDSat's convention (dimacs.c, and the Trimoska files under
    inputs/TRIMOSKA-ECICB-2024/upstream/benchmarks/) is that an `x ... 0` line is an XOR
    clause that must be TRUE, with `T` the constant 1. An equation f = 0 is therefore
    written as the terms of f with T toggled: f + 1 = 1. Zero equations (0 = 0) are
    dropped; an equation that is the constant 1 becomes the empty clause `x 0`.
    Checked (dbg): the known solutions of SAT instances satisfy the export and WDSat's
    models verify against the boolsys system."""
    n, k, m, N = system["n"], system["k"], system["m"], system["N"]
    perm = permutation(n, k, m)
    lines = []
    monos = set()
    maxdeg, maxterms = 1, 0
    for e in system["equations"]:
        if not e:
            continue
        pieces = ["x"]
        if 0 not in e:
            pieces.append("T")      # f = 0  <=>  (f + 1) = TRUE ; f has no constant, so add it
        for mask in e:
            if mask == 0:
                continue            # f = 0 with constant 1 in f  <=>  (f - 1) = TRUE ; drop it
            vs = sorted(perm[j] for j in range(mask.bit_length()) if (mask >> j) & 1)
            if len(vs) == 1:
                pieces.append(str(vs[0]))
            else:
                pieces.append(f".{len(vs)}")
                pieces.extend(str(v) for v in vs)
                monos.add(tuple(vs))
                maxdeg = max(maxdeg, len(vs))
        maxterms = max(maxterms, len(e))
        pieces.append("0")
        lines.append(" ".join(pieces))
    ne = len(lines)
    text = f"p cnf {N} {ne}\n" + "\n".join(lines) + "\n"
    max_id = N + len(monos)
    sizing = {"MAX_ANF_ID": N + 1, "MAX_DEGREE": maxdeg + 1, "MAX_ID": max_id,
              "MAX_EQ": sum(len(mo) + 1 for mo in monos) + 64, "MAX_EQ_SIZE": maxdeg + 2,
              "MAX_XEQ": ne + 1, "MAX_XEQ_SIZE": max_id + 1}
    meta = {"n_unary": N, "n_eqs": ne, "n_nonlinear_monomials": len(monos), "max_degree": maxdeg,
            "max_terms_per_eq": maxterms, "sizing": sizing, "anf_sha256": hashlib.sha256(text.encode()).hexdigest()}
    return text, meta


def unpermute_assignment(bits, n, k, m):
    """WDSat assignment string (unary vars 1..N in file order) -> boolsys mask."""
    perm = permutation(n, k, m)
    mask = 0
    for j, wid in enumerate(perm):
        if bits[wid - 1] == "1":
            mask |= 1 << j
    return mask


PATCH_HELPERS = r"""
/* m4-sat-cost-pilot counters (added): nodes = branch points opened, fails = failed branch inferences */
long long wd_nodes = 0, wd_fails = 0;
static inline bool wd_infer_counted(const int_t x) { bool r = wdsat_infer(x); if (!r) wd_fails++; return r; }
static inline bool wd_set_true_counted(const int_t x) { bool r = wdsat_set_true(x); if (!r) wd_fails++; return r; }
"""


def patch_source(src_dir: Path, variant="stock"):
    """Add node/fail counters to the branching code without touching the solver's conf counter.
    variant == "symfull": the -b (symmetry-breaking) search no longer stops after the first m*l
    variables; the lexicographic pruning of the m x-blocks is kept for h < m*l and the remaining
    (u) variables are branched plainly, so the search is complete for chained systems whose
    u-blocks are not linear once the x's are fixed (m >= 4). Stock -b is incomplete there."""
    w = src_dir / "wdsat.c"
    text0 = w.read_text()
    if variant == "symfull":
        a1 = "wdsat_solve_rest_XG_sym(0, m * l - 1, true, conf)"
        a2 = "\tif(h % l == 0)\n\t\tsearch_prune_point = true;\n\tif(search_prune_point)\n\t{\n\t\tif((h - l < 0) || _cnf_is_false(set[h - l]))\n\t\t{\n\t\t\t_cnf_breakpoint;\n\t\t\t_xorset_breakpoint;\n\t\t\t_xorgauss_breakpoint;"
        assert text0.count(a1) == 1 and text0.count(a2) == 1, (text0.count(a1), text0.count(a2))
        text0 = text0.replace(a1, "wdsat_solve_rest_XG_sym(0, nb_min_vars - 1, true, conf)")
        text0 = text0.replace(a2, a2.replace("if(h % l == 0)", "if(h < m * l && h % l == 0)").replace("if(search_prune_point)\n", "if(search_prune_point && h < m * l)\n"))
    lines = text0.splitlines()
    out = []
    in_branching = False
    for ln in lines:
        s = ln.strip()
        if s.startswith("bool wdsat_solve_rest(") or s.startswith("bool go_left(") or s.startswith("bool wdsat_solve_rest_XG("):
            in_branching = True
        if s.startswith("bool wdsat_infer(const int_t l)") or s.startswith("bool wdsat_infer_unitary"):
            in_branching = False
        if in_branching and "wdsat_solve(" not in s:
            ln = ln.replace("wdsat_infer(", "wd_infer_counted(").replace("wdsat_set_true(", "wd_set_true_counted(")
            ln = ln.replace("conf[0]++;", "conf[0]++; wd_nodes++;")
        if s.startswith("bool wdsat_solve(int_t n"):
            in_branching = False
        ln = ln.replace('printf("UNSAT\\n");printf("%lld\\n",conf[0]);',
                        'printf("UNSAT\\n");printf("%lld\\n",conf[0]); printf("c stats nodes=%lld fails=%lld\\n", wd_nodes, wd_fails);')
        out.append(ln)
    text = "\n".join(out) + "\n"
    # final SAT exit: the last 'printf("%lld\n",conf[0]);' before 'return (true);'
    text = text.replace('\tprintf("%lld\\n",conf[0]);\n\t\n\treturn (true);',
                        '\tprintf("%lld\\n",conf[0]);\n\tprintf("c stats nodes=%lld fails=%lld\\n", wd_nodes, wd_fails);\n\treturn (true);')
    assert "c stats" in text, "patch anchor not found"
    # helpers after the wdsat_set_true definition (which precedes all branching code)
    idx = text.index("bool wdsat_set_true(const int_t l) {")
    end = text.index("\n}\n", idx) + 3
    text = text[:end] + PATCH_HELPERS + text[end:]
    w.write_text(text)


def build(sizing: dict, buffer_size=200000, variant="stock") -> Path:
    consts = dict(sizing); consts["MAX_BUFFER_SIZE"] = buffer_size
    sig = variant + "_" + "_".join(f"{k}{v}" for k, v in sorted(consts.items()))
    bdir = BUILD_ROOT / f"wdsat_{hashlib.sha1(sig.encode()).hexdigest()[:10]}"
    exe = bdir / "wdsat_solver"
    if exe.exists():
        return exe
    if bdir.exists():
        shutil.rmtree(bdir)
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
            in_comment = True; out.append(ln); continue
        mm = re.match(r"#define __(\w+)__\s", s)
        if mm and mm.group(1) in consts:
            continue
        out.append(ln)
    out.append("/* m4-sat-cost-pilot exact sizing (derived from the instance ANF) */")
    out += [f"#define __{k}__ {v}" for k, v in consts.items()]
    cfg.write_text("\n".join(out) + "\n")
    patch_source(bdir / "src", variant)
    consts["variant"] = variant
    (bdir / "config_used.json").write_text(json.dumps(consts, indent=1))
    log = subprocess.run(["make"], cwd=bdir / "src", capture_output=True, text=True)
    (bdir / "make.log").write_text(log.stdout + "\n--- stderr ---\n" + log.stderr)
    if log.returncode != 0 or not exe.exists():
        raise RuntimeError(f"WDSat build failed in {bdir}")
    return exe


def parse_output(out: str) -> dict:
    lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
    res = {"status": "unknown", "conflicts": None, "nodes": None, "fails": None, "assignment": None, "notes": []}
    for ln in lines:
        if ln.startswith("!!!"):
            res["notes"].append(ln)
        mm = re.match(r"c stats nodes=(\d+) fails=(\d+)", ln)
        if mm:
            res["nodes"], res["fails"] = int(mm.group(1)), int(mm.group(2))
    if any(ln.startswith("UNSAT on XORGAUSS init") for ln in lines):
        res["status"] = "UNSAT"; res["conflicts"] = 0; res["notes"].append("unsat_on_init"); return res
    if any(ln.startswith("UNSAT") for ln in lines):
        idx = max(i for i, ln in enumerate(lines) if ln.startswith("UNSAT"))
        res["status"] = "UNSAT"
        if idx + 1 < len(lines) and lines[idx + 1].isdigit():
            res["conflicts"] = int(lines[idx + 1])
        return res
    bl = [i for i, ln in enumerate(lines) if re.fullmatch(r"[01]{8,}", ln)]
    if bl:
        i = bl[-1]
        res["status"] = "SAT"; res["assignment"] = lines[i]
        if i + 1 < len(lines) and lines[i + 1].isdigit():
            res["conflicts"] = int(lines[i + 1])
    return res


def run(exe: Path, anf_path: Path, flags: list[str], timeout: float) -> dict:
    r0 = resource.getrusage(resource.RUSAGE_CHILDREN)
    t0 = time.time()
    try:
        p = subprocess.run([str(exe), "-i", str(anf_path)] + flags, capture_output=True, text=True, timeout=timeout)
        out, err, rc, to = p.stdout, p.stderr, p.returncode, False
    except subprocess.TimeoutExpired as ex:
        out = (ex.stdout or b"").decode(errors="replace") if isinstance(ex.stdout, bytes) else (ex.stdout or "")
        err, rc, to = "", None, True
    wall = time.time() - t0
    r1 = resource.getrusage(resource.RUSAGE_CHILDREN)
    res = parse_output(out)
    res.update({"wall_s": wall, "cpu_user_s": r1.ru_utime - r0.ru_utime, "cpu_sys_s": r1.ru_stime - r0.ru_stime,
                "returncode": rc, "timed_out": to, "stderr_head": err[:300]})
    if to:
        res["status"] = "censored_timeout"
    elif rc not in (0, 1) and res["status"] == "unknown":
        res["status"] = f"solver_exit_{rc}"
    return res
