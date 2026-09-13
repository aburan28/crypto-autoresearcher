#!/usr/bin/env python3
"""EXP-ICPERF-66fd51 harness: measure every declared engine on every shipped Trimoska
S_4 PDP instance, certify every SAT answer against the curve, and write results
incrementally so a watchdog stop leaves a partial artifact rather than nothing.

Usage:
  python3 bench.py --run-dir RUNDIR [--phases A,B,C,D,E] [--dry-run]

Phases (ordered so a stop leaves the most valuable data first):
  A  certificates for all 30 S instances; WDSat default / core-order / symmetry / GE on all
     60 instances; WDSat default on matched random null objects for 3 S + 3 U templates per cell
  B  CryptoMiniSat on the CNF-XOR form, all 60
  C  Macaulay2 F4 (ZZ/2 + field equations): all 20 n15l5; 3 S + 3 U per l=6 cell
  D  CryptoMiniSat / CaDiCaL / MiniSat on the pure-CNF form (regenerated with the vendored
     XORtoCNF.sh and hash-checked against the upstream manifest): 5 S + 5 U per cell
  E  Singular std (GF(2) + field equations): 2 S + 2 U of n15l5

Every engine invocation is a child process under a wall-clock timeout and an address-
space limit; wall, CPU (user+sys), peak RSS, exit status, stdout/stderr paths and the
1-minute load average at launch are recorded per run in results.jsonl.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import resource
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
BENCH = REPO / "inputs/TRIMOSKA-ECICB-2024/upstream/benchmarks"
XOR2CNF = REPO / "inputs/TRIMOSKA-ECICB-2024/upstream/XORtoCNF.sh"
UPSTREAM_SUMS = REPO / "inputs/TRIMOSKA-ECICB-2024/UPSTREAM_SHA256SUMS.txt"
WDSAT_SRC = REPO / "inputs/TRIMOSKA-WDSAT-2024/upstream/src"

sys.path.insert(0, str(HERE))
from binec import InfoFile, bits_to_int  # noqa: E402
from convert import (_parse_anf_equation, anf_null_object, anf_shape, magma_to_m2,  # noqa: E402
                     magma_to_singular, parse_anf_header)

CELLS = [(15, 5), (17, 6), (19, 6)]
M = 3  # factor-base points per decomposition (generator's m-1)
MEM_LIMIT_GB = 6
TIMEOUTS = {"wdsat": 600, "wdsat_null": 180, "wdsat_noncore": 120, "cms_xor": 300, "m2_f4_l5": 600,
            "m2_f4_l6": 1800, "cnf_generic": 300, "singular_std": 900}
NONCORE_PER_LABEL = 5  # noncore_first runs on the first 5 S + 5 U of each cell
NULL_SEED_BASE = 20260913


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def instances():
    for n, l in CELLS:
        for i in range(1, 21):
            label = "S" if i <= 10 else "U"
            yield {"n": n, "l": l, "id": i, "label": label, "cell": f"n{n}l{l}",
                   "stem": f"n{n}l{l}-{i}-{label}",
                   "info": BENCH / f"INFOn{n}l{l}-{i}-{label}.dimacs",
                   "anf": BENCH / f"Xn{n}l{l}-{i}-{label}.anf",
                   "xor": BENCH / f"Xn{n}l{l}-{i}-{label}.dimacs",
                   "magma": BENCH / f"n{n}l{l}-{i}-{label}.in"}


def subset(insts, per_label):
    out = []
    for cell in {i["cell"] for i in insts}:
        for lab in ("S", "U"):
            out += [i for i in insts if i["cell"] == cell and i["label"] == lab][:per_label]
    return sorted(out, key=lambda i: (i["n"], i["id"]))


class Runner:
    def __init__(self, run_dir: Path, dry: bool):
        self.run_dir = run_dir
        self.dry = dry
        self.logs = run_dir / "logs"
        self.logs.mkdir(parents=True, exist_ok=True)
        self.results = run_dir / "results.jsonl"
        self.done = set()
        if self.results.exists():
            for ln in self.results.read_text().splitlines():
                try:
                    r = json.loads(ln)
                    self.done.add((r["instance"], r["engine"], r["config"]))
                except Exception:
                    pass

    def record(self, rec: dict):
        rec["recorded_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with open(self.results, "a") as f:
            f.write(json.dumps(rec, sort_keys=True) + "\n")
        self.done.add((rec["instance"], rec["engine"], rec["config"]))

    def already(self, inst, engine, config) -> bool:
        return (inst, engine, config) in self.done

    def run(self, argv, tag: str, timeout: int, stdin_path: Path | None = None) -> dict:
        """Run argv as a child under timeout and RLIMIT_AS; return measurements."""
        out_p, err_p = self.logs / f"{tag}.out", self.logs / f"{tag}.err"
        if self.dry:
            return {"dry_run": True, "argv": argv}
        before = resource.getrusage(resource.RUSAGE_CHILDREN)
        load1 = os.getloadavg()[0]

        def limits():
            lim = MEM_LIMIT_GB * (1 << 30)
            resource.setrlimit(resource.RLIMIT_AS, (lim, lim))

        t0 = time.monotonic()
        timed_out = False
        with open(out_p, "wb") as fo, open(err_p, "wb") as fe:
            stdin = open(stdin_path, "rb") if stdin_path else subprocess.DEVNULL
            try:
                p = subprocess.run(argv, stdout=fo, stderr=fe, stdin=stdin, timeout=timeout,
                                   preexec_fn=limits, check=False)
                rc = p.returncode
            except subprocess.TimeoutExpired:
                timed_out, rc = True, None
            finally:
                if stdin_path:
                    stdin.close()
        wall = time.monotonic() - t0
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        return {"argv": argv, "wall_s": round(wall, 4), "timed_out": timed_out, "returncode": rc,
                "cpu_s": round((after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime), 4),
                "max_rss_kb_children_highwater": after.ru_maxrss,
                "loadavg1_at_start": round(load1, 2), "timeout_s": timeout,
                "stdout": str(out_p.relative_to(self.run_dir)), "stderr": str(err_p.relative_to(self.run_dir))}


# ----------------------------------------------------------------------------- WDSat

def anf_sizing(anf_path: Path) -> dict:
    src = anf_path.read_text()
    nv, ne = parse_anf_header(src)
    monos, maxdeg, maxterms = set(), 1, 0
    for ln in src.splitlines():
        t = ln.split()
        if t and t[0] == "x":
            terms, _ = _parse_anf_equation(t[1:-1])
            maxterms = max(maxterms, len(terms))
            for m in terms:
                if len(m) > 1:
                    monos.add(tuple(m))
                    maxdeg = max(maxdeg, len(m))
    max_id = nv + len(monos)
    return {"MAX_ANF_ID": nv + 1, "MAX_DEGREE": maxdeg + 1, "MAX_ID": max_id,
            "MAX_EQ": sum(len(m) + 1 for m in monos) + 64, "MAX_EQ_SIZE": maxdeg + 2,
            "MAX_XEQ": ne + 1, "MAX_XEQ_SIZE": max_id, "n_unary": nv, "n_eqs": ne,
            "n_nonunary_monomials": len(monos), "max_terms_per_eq": maxterms}


def build_wdsat(run_dir: Path, sizing: dict, buffer_size: int) -> Path:
    """Build WDSat from the vendored source with an exact static configuration."""
    consts = {k: sizing[k] for k in ("MAX_ANF_ID", "MAX_DEGREE", "MAX_ID", "MAX_EQ", "MAX_EQ_SIZE", "MAX_XEQ", "MAX_XEQ_SIZE")}
    consts["MAX_BUFFER_SIZE"] = buffer_size
    sig = "_".join(f"{k}{v}" for k, v in sorted(consts.items()))
    bdir = run_dir / "builds" / f"wdsat_{hashlib.sha1(sig.encode()).hexdigest()[:10]}"
    exe = bdir / "wdsat_solver"
    if exe.exists():
        return exe
    shutil.copytree(WDSAT_SRC, bdir / "src")
    cfg = bdir / "src" / "config.h"
    text = cfg.read_text()
    # Replace the single active (uncommented) block: every '#define __X__ value' line that is
    # not inside a /* ... */ comment.  We rewrite by removing all active defines of the sized
    # constants and appending our own block; the XG_ENHANCED switch is left as shipped.
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
    out.append("/* EXP-ICPERF-66fd51 exact sizing (derived from the instance ANF) */")
    for k, v in consts.items():
        out.append(f"#define __{k}__ {v}")
    cfg.write_text("\n".join(out) + "\n")
    (bdir / "config_used.json").write_text(json.dumps(consts, indent=1))
    log = subprocess.run(["make"], cwd=bdir / "src", capture_output=True, text=True)
    (bdir / "make.log").write_text(log.stdout + "\n--- stderr ---\n" + log.stderr)
    if log.returncode != 0 or not exe.exists():
        raise RuntimeError(f"WDSat build failed in {bdir}")
    return exe


def parse_wdsat(out_text: str) -> dict:
    lines = [ln.strip() for ln in out_text.splitlines() if ln.strip()]
    res = {"status": "unknown", "conflicts": None, "assignment": None, "solver_notes": []}
    for ln in lines:
        if ln.startswith("!!!"):
            res["solver_notes"].append(ln)
    if any(ln.startswith("UNSAT") for ln in lines):
        res["status"] = "UNSAT"
        idx = max(i for i, ln in enumerate(lines) if ln.startswith("UNSAT"))
        if idx + 1 < len(lines) and lines[idx + 1].lstrip("-").isdigit():
            res["conflicts"] = int(lines[idx + 1])
        return res
    bitlines = [i for i, ln in enumerate(lines) if re.fullmatch(r"[01]{8,}", ln)]
    if bitlines:
        i = bitlines[-1]
        res["status"] = "SAT"
        res["assignment"] = lines[i]
        if i + 1 < len(lines) and lines[i + 1].lstrip("-").isdigit():
            res["conflicts"] = int(lines[i + 1])
    return res


def verify_assignment_bits(info: InfoFile, bits: str) -> dict:
    """Interpret the first m*l bits as x_1 | x_2 | x_3 (low-degree-first) and check on the curve."""
    ml = M * info.l
    if len(bits) < ml:
        return {"verified": False, "why": "assignment shorter than m*l"}
    xs = tuple(bits[k * info.l:(k + 1) * info.l] for k in range(M))
    ok, why = info.check_certificate(xs)
    return {"verified": ok, "why": why, "x_bits": list(xs),
            "matches_shipped_certificate_as_set": (info.cert_bits is not None and sorted(xs) == sorted(info.cert_bits))}


def parse_dimacs_model(out_text: str) -> dict:
    status = "unknown"
    vals = {}
    for ln in out_text.splitlines():
        if ln.startswith("s "):
            if "UNSAT" in ln:
                status = "UNSAT"
            elif "SAT" in ln:
                status = "SAT"
        elif ln.startswith("v "):
            for t in ln.split()[1:]:
                v = int(t)
                if v != 0:
                    vals[abs(v)] = 1 if v > 0 else 0
    return {"status": status, "vals": vals}


def parse_cms_stats(err_text: str, out_text: str) -> dict:
    stats = {}
    for ln in (out_text + "\n" + err_text).splitlines():
        m = re.match(r"c\s+(conflicts|decisions|propagations)\s*:\s*(\d+)", ln)
        if m:
            stats[m.group(1)] = int(m.group(2))
    return stats


def model_bits(vals: dict, ml: int) -> str:
    return "".join(str(vals.get(i, 0)) for i in range(1, ml + 1))


# ----------------------------------------------------------------------------- phases

def phase_A(R: Runner, insts):
    # A.1 certificates (independent arithmetic)
    for inst in insts:
        info = InfoFile.parse(inst["info"])
        if inst["label"] == "S" and not R.already(inst["stem"], "certificate", "shipped"):
            ok, why = info.check_certificate()
            R.record({"phase": "A", "instance": inst["stem"], "cell": inst["cell"], "label": inst["label"],
                      "engine": "certificate", "config": "shipped", "verified": ok, "why": why,
                      "certificate": list(info.cert_bits)})
    # A.2 WDSat four configurations on every instance
    # core_order is a prefix of WDSat's default order (1..N), so it must match
    # default exactly: it is the identity check on the -g wiring (P3a).
    # noncore_first is the real order control (P3b): a full permutation with the
    # N-ml e-variables ahead of the ml core variables, so the search stays
    # complete but propagation from the core is lost.
    configs = {
        "default": lambda inst, s: [],
        "core_order": lambda inst, s: ["-g", ",".join(str(i) for i in range(1, M * inst["l"] + 1))],
        "noncore_first": lambda inst, s: ["-g", ",".join(
            str(i) for i in list(range(M * inst["l"] + 1, s["n_unary"] + 1)) + list(range(1, M * inst["l"] + 1)))],
        "symmetry": lambda inst, s: ["-b", "-m", str(M), "-l", str(inst["l"])],
        "gauss_elim": lambda inst, s: ["-x"],
    }
    # noncore_first pilots (pre-run smoke) took 2 s / 109 s / >300 s where default took
    # 0.005 s / 0.2 s / 2.3 s, so it runs on a 5+5 subset per cell under its own
    # timeout; its timeouts are right-censored lower bounds, which summary.py uses.
    noncore_stems = {i["stem"] for i in subset(insts, NONCORE_PER_LABEL)}
    for inst in insts:
        info = InfoFile.parse(inst["info"])
        sizing = anf_sizing(inst["anf"])
        for cname, extra in configs.items():
            if R.already(inst["stem"], "wdsat", cname):
                continue
            if cname == "noncore_first" and inst["stem"] not in noncore_stems:
                continue
            to = TIMEOUTS["wdsat_noncore"] if cname == "noncore_first" else None
            rec = run_wdsat(R, inst["anf"], sizing, extra(inst, sizing), f"wdsat_{cname}_{inst['stem']}", timeout=to)
            rec.update({"phase": "A", "instance": inst["stem"], "cell": inst["cell"], "label": inst["label"],
                        "engine": "wdsat", "config": cname})
            if rec.get("status") == "SAT":
                rec["verification"] = verify_assignment_bits(info, rec["assignment"])
            R.record(rec)
    # A.3 matched random null objects, WDSat default: 3 S + 3 U templates per cell
    # (smoke runs showed 35-600+ s per null object against <3 s structured; the
    # timeout is a recorded budget stop and a LOWER BOUND, never a measurement)
    null_dir = R.run_dir / "null_objects"
    null_dir.mkdir(exist_ok=True)
    for inst in subset(insts, 3):
        if R.already(inst["stem"], "wdsat", "default_on_null_object"):
            continue
        seed = NULL_SEED_BASE * 1000 + inst["n"] * 100 + inst["id"]
        src = inst["anf"].read_text()
        null_src = anf_null_object(src, seed)
        null_p = null_dir / f"NULL-{inst['stem']}.anf"
        null_p.write_text(null_src)
        shape_ok = anf_shape(src) == anf_shape(null_src)
        sizing = anf_sizing(null_p)
        rec = run_wdsat(R, null_p, sizing, [], f"wdsat_null_{inst['stem']}", timeout=TIMEOUTS["wdsat_null"])
        rec.update({"phase": "A", "instance": inst["stem"], "cell": inst["cell"], "label": inst["label"],
                    "engine": "wdsat", "config": "default_on_null_object", "null_seed": seed,
                    "null_object": str(null_p.relative_to(R.run_dir)), "shape_matches_template": shape_ok,
                    "null_sizing": sizing})
        R.record(rec)


def run_wdsat(R: Runner, anf: Path, sizing: dict, extra: list, tag: str, timeout: int | None = None) -> dict:
    buffer_size = 60000
    timeout = timeout or TIMEOUTS["wdsat"]
    for attempt in range(4):
        exe = build_wdsat(R.run_dir, sizing, buffer_size)
        m = R.run([str(exe), "-i", str(anf)] + extra, tag, timeout)
        if R.dry:
            return m
        out = (R.run_dir / m["stdout"]).read_text(errors="replace")
        err = (R.run_dir / m["stderr"]).read_text(errors="replace")
        if "__MAX_BUFFER_SIZE__" in err and not m["timed_out"]:
            buffer_size *= 2
            continue
        parsed = parse_wdsat(out)
        m.update(parsed)
        m["wdsat_build"] = str(exe.parent.relative_to(R.run_dir))
        m["wdsat_constants"] = json.loads((exe.parent / "config_used.json").read_text())
        m["stderr_head"] = err[:300]
        if m["timed_out"]:
            m["status"] = "budget_stop_timeout"
        elif m["returncode"] not in (0, 1) and m["status"] == "unknown":
            m["status"] = f"infrastructure_exit_{m['returncode']}"
        return m
    m["status"] = "infrastructure_buffer_sizing_failed"
    return m


def phase_B(R: Runner, insts):
    for inst in insts:
        if R.already(inst["stem"], "cryptominisat5", "cnf_xor"):
            continue
        info = InfoFile.parse(inst["info"])
        m = R.run(["cryptominisat5", "--verb", "1", str(inst["xor"])], f"cms_xor_{inst['stem']}", TIMEOUTS["cms_xor"])
        m.update({"phase": "B", "instance": inst["stem"], "cell": inst["cell"], "label": inst["label"],
                  "engine": "cryptominisat5", "config": "cnf_xor"})
        finish_dimacs_record(R, m, info, inst)
        R.record(m)


def finish_dimacs_record(R: Runner, m: dict, info: InfoFile, inst: dict):
    if R.dry:
        return
    out = (R.run_dir / m["stdout"]).read_text(errors="replace")
    err = (R.run_dir / m["stderr"]).read_text(errors="replace")
    parsed = parse_dimacs_model(out)
    m["status"] = "budget_stop_timeout" if m["timed_out"] else parsed["status"]
    m["stats"] = parse_cms_stats(err, out)
    if parsed["status"] == "SAT":
        bits = model_bits(parsed["vals"], M * inst["l"])
        m["assignment_core_bits"] = bits
        m["verification"] = verify_assignment_bits(info, bits)


def pure_cnf(R: Runner, inst: dict) -> Path:
    """Regenerate the pure-CNF form with the vendored XORtoCNF.sh and hash-check it."""
    cdir = R.run_dir / "pure_cnf"
    cdir.mkdir(exist_ok=True)
    target = cdir / f"{inst['stem']}.dimacs"
    if target.exists():
        return target
    work = cdir / f"work_{inst['stem']}"
    work.mkdir(exist_ok=True)
    nvars = int(inst["xor"].read_text().splitlines()[0].split()[2])
    offset = subprocess.run(["bash", str(XOR2CNF), str(nvars), str(inst["xor"])], cwd=work,
                            capture_output=True, text=True, check=True).stdout.strip().splitlines()[-1]
    norm = (work / "F_3_norm.dimacs").read_text().splitlines()
    new_nvars = int(offset) - 1
    new_nlines = len(norm) - 1
    target.write_text(f"p cnf {new_nvars} {new_nlines}\n" + "\n".join(norm[1:]) + "\n")
    shutil.rmtree(work)
    expected = None
    for ln in UPSTREAM_SUMS.read_text().splitlines():
        h, p = ln.split(None, 1)
        if p.strip() == f"./benchmarks/{inst['stem']}.dimacs":
            expected = h
    (cdir / f"{inst['stem']}.hashcheck.json").write_text(json.dumps(
        {"regenerated_sha256": sha256(target), "upstream_sha256": expected, "match": sha256(target) == expected}))
    return target


def phase_D(R: Runner, insts):
    sub = subset(insts, 5)
    engines = {"cryptominisat5": lambda p: ["cryptominisat5", "--verb", "1", str(p)],
               "cadical": lambda p: ["cadical", "-q", str(p)],
               "minisat": lambda p: ["minisat", "-verb=0", str(p), "MODEL_OUT"]}
    for inst in sub:
        info = InfoFile.parse(inst["info"])
        cnf = pure_cnf(R, inst)
        hc = json.loads((cnf.parent / f"{inst['stem']}.hashcheck.json").read_text())
        for ename, mk in engines.items():
            if R.already(inst["stem"], ename, "pure_cnf"):
                continue
            argv = mk(cnf)
            model_out = None
            if "MODEL_OUT" in argv:
                model_out = R.logs / f"{ename}_cnf_{inst['stem']}.model"
                argv = [model_out.__str__() if a == "MODEL_OUT" else a for a in argv]
            m = R.run(argv, f"{ename}_cnf_{inst['stem']}", TIMEOUTS["cnf_generic"])
            m.update({"phase": "D", "instance": inst["stem"], "cell": inst["cell"], "label": inst["label"],
                      "engine": ename, "config": "pure_cnf", "pure_cnf_hashcheck": hc})
            if model_out is not None and model_out.exists() and not R.dry:
                # minisat writes "SAT\n<lits> 0" or "UNSAT" to the model file
                txt = model_out.read_text()
                lines = txt.splitlines()
                fake = ("s SATISFIABLE\nv " + lines[1] + "\n") if lines and lines[0].startswith("SAT") else "s UNSATISFIABLE\n"
                (R.run_dir / m["stdout"]).write_text(fake + "\n--- original stdout ---\n" + (R.run_dir / m["stdout"]).read_text())
            finish_dimacs_record(R, m, info, inst)
            if ename == "cadical" and m.get("status") == "unknown" and not m["timed_out"] and not R.dry:
                # cadical -q prints s/v lines; if suppressed, fall back on exit code 10/20
                m["status"] = {10: "SAT", 20: "UNSAT"}.get(m["returncode"], "unknown")
            R.record(m)


def phase_C(R: Runner, insts):
    plan = [i for i in insts if i["cell"] == "n15l5"] + subset([i for i in insts if i["l"] == 6], 3)
    sdir = R.run_dir / "scripts"
    sdir.mkdir(exist_ok=True)
    for inst in plan:
        if R.already(inst["stem"], "macaulay2_F4_ZZ2_fieldeqs", "grevlex"):
            continue
        script = sdir / f"{inst['stem']}.m2"
        script.write_text(magma_to_m2(inst["magma"].read_text(), "F4"))
        to = TIMEOUTS["m2_f4_l5"] if inst["l"] == 5 else TIMEOUTS["m2_f4_l6"]
        m = R.run(["M2", "--script", str(script)], f"m2_{inst['stem']}", to)
        m.update({"phase": "C", "instance": inst["stem"], "cell": inst["cell"], "label": inst["label"],
                  "engine": "macaulay2_F4_ZZ2_fieldeqs", "config": "grevlex", "script": str(script.relative_to(R.run_dir))})
        if not R.dry:
            out = (R.run_dir / m["stdout"]).read_text(errors="replace") + (R.run_dir / m["stderr"]).read_text(errors="replace")
            g = re.search(r"RESULT gb_size=(\d+) cpu_s=([\d.]+) maxdeg_gb=(\d+) is_unit=(true|false)", out)
            if m["timed_out"]:
                m["status"] = "budget_stop_timeout"
            elif g:
                m.update({"gb_size": int(g.group(1)), "engine_cpu_s": float(g.group(2)), "maxdeg_gb": int(g.group(3)),
                          "unit_ideal": g.group(4) == "true"})
                m["status"] = "UNSAT_certified_unit_ideal" if m["unit_ideal"] else "consistent_proper_ideal"
            else:
                m["status"] = f"infrastructure_exit_{m['returncode']}"
        R.record(m)


def phase_E(R: Runner, insts):
    plan = subset([i for i in insts if i["cell"] == "n15l5"], 2)
    sdir = R.run_dir / "scripts"
    sdir.mkdir(exist_ok=True)
    for inst in plan:
        if R.already(inst["stem"], "singular_std_GF2_fieldeqs", "dp"):
            continue
        script = sdir / f"{inst['stem']}.sing"
        script.write_text(magma_to_singular(inst["magma"].read_text(), "std"))
        m = R.run(["Singular", "-q", str(script)], f"singular_{inst['stem']}", TIMEOUTS["singular_std"])
        m.update({"phase": "E", "instance": inst["stem"], "cell": inst["cell"], "label": inst["label"],
                  "engine": "singular_std_GF2_fieldeqs", "config": "dp", "script": str(script.relative_to(R.run_dir))})
        if not R.dry:
            out = (R.run_dir / m["stdout"]).read_text(errors="replace")
            g = re.search(r"RESULT gb_size=(\d+) cpu_ticks=(\d+) ticks_per_sec=(\d+) vdim=(-?\d+) maxdeg_gb=(\d+)", out)
            if m["timed_out"]:
                m["status"] = "budget_stop_timeout"
            elif g:
                m.update({"gb_size": int(g.group(1)), "engine_cpu_s": int(g.group(2)) / int(g.group(3)),
                          "vdim": int(g.group(4)), "maxdeg_gb": int(g.group(5))})
                m["status"] = "UNSAT_certified_unit_ideal" if m["vdim"] == 0 else f"consistent_vdim_{m['vdim']}"
            else:
                m["status"] = f"infrastructure_exit_{m['returncode']}"
        R.record(m)


def environment() -> dict:
    def ver(argv):
        try:
            return subprocess.run(argv, capture_output=True, text=True, timeout=60).stdout.strip().splitlines()[0]
        except Exception as e:  # noqa: BLE001
            return f"unavailable: {e}"
    return {"python": sys.version.split()[0], "platform": platform.platform(), "cpu_count": os.cpu_count(),
            "gcc": ver(["gcc", "--version"]), "M2": ver(["M2", "--version"]), "Singular": ver(["Singular", "--version"]),
            "cryptominisat5": ver(["cryptominisat5", "--version"]), "cadical": ver(["cadical", "--version"]),
            "minisat": "2.2.1 (apt; prints no version)", "loadavg_at_start": os.getloadavg(),
            "mem_limit_gb_per_child": MEM_LIMIT_GB, "timeouts_s": TIMEOUTS,
            "benchmark_manifest_sha256": sha256(UPSTREAM_SUMS),
            "wdsat_src_sha256": {p.name: sha256(p) for p in sorted(WDSAT_SRC.iterdir())}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--phases", default="A,B,C,D,E")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="smoke testing only: first N instances per label per cell")
    a = ap.parse_args()
    run_dir = Path(a.run_dir).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    R = Runner(run_dir, a.dry_run)
    insts = list(instances())
    if a.limit:
        insts = subset(insts, a.limit)
    for inst in insts:
        for k in ("info", "anf", "xor", "magma"):
            if not inst[k].exists():
                raise SystemExit(f"missing input {inst[k]}")
    (run_dir / "environment.json").write_text(json.dumps(environment(), indent=1, default=str))
    (run_dir / "plan.json").write_text(json.dumps({"phases": a.phases, "cells": CELLS, "instances": len(insts),
                                                   "timeouts_s": TIMEOUTS, "mem_limit_gb": MEM_LIMIT_GB}, indent=1))
    phases = {"A": phase_A, "B": phase_B, "C": phase_C, "D": phase_D, "E": phase_E}
    for ph in a.phases.split(","):
        t0 = time.time()
        phases[ph](R, insts)
        with open(run_dir / "phase_log.txt", "a") as f:
            f.write(f"{ph} finished at {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} after {time.time() - t0:.1f}s\n")


if __name__ == "__main__":
    main()
