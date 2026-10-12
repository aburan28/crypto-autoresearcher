#!/usr/bin/env python3
"""Per-run driver for EXP-FROB-30006a (frozen protocol: specification.yaml, approved by
DEC-20260920-cf8ded).  One invocation = one RUN directory with the reproduction package
(manifest.yaml, command.txt, environment.json, stdout.log, stderr.log, raw-result.json,
instance ANF/JSON, certificates, WDSat build config_used.json, per-process logs).

  run_trial.py --trial TRIAL_ID --run-id RUN-FROB-xxxxxx --run-dir DIR

Trials (enumerated in TRIALS; the frozen trial-plan.json lists the same ids):
  regression-gate     C-REG: shipped Trimoska Xn15l5-11-U.anf, conflicts within 2x of the archived
                      reference (RUN-ICPERF-305ca3: default 31257, gauss_elim 21488); plus the
                      independent certifier on that instance and on a shipped SAT instance.
  pipeline-control    planted-SAT and small certified-UNSAT instances at n in {17, 23, 31}: WDSat
                      status must agree with the certifier; SAT assignments are decoded and verified
                      on the curve; small-cell conflict counts vs 2^{ml}/m! are recorded as context.
  n41-stable-k        primary cell, stable arm, seed k (k = 1..3): first certified-UNSAT candidate of
  n41-random-k        the seed's target stream; WDSat -x (primary) and default (secondary, watchdog).
  n43-stable-f0       decisive cell, capacity gate: one attempt, stable V = ker g_0(sigma), seed 1.

Solver configurations measured on every instance:
  gauss_elim : wdsat_solver -i ANF -x      (XORGAUSS Gaussian elimination; the module WDSat is
               built around -- __XG_ENHANCED__ is compiled in for both)
  default    : wdsat_solver -i ANF         (XOR unit propagation only)
Both are reported; the frozen contract names the solver but not its flag.  Nothing here selects
a verdict: r_s, r_r are reported per configuration for the Reviewer.

Machine protection (declared, not research budget): a resident-set watchdog of RSS_LIMIT_GB over
the child's process group and a per-process wall-clock watchdog with a reason recorded in
raw-result.json.  A killed process is `resource_exhaustion`; it is never UNSAT and never a ratio.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import random
import resource
import signal
import subprocess
import sys
import time
from fractions import Fraction
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
EXP_DIR = HERE.parent
EXP_ID = "EXP-FROB-30006a"
sys.path.insert(0, str(HERE))
from gf2n import GF2n, KoblitzCurve, semaev_s3, semaev_s4  # noqa: E402
from frob_basis import in_span  # noqa: E402
import gen_instance  # noqa: E402
from wdsat_build import anf_sizing, build_wdsat, parse_wdsat_output, verify_vendored_source, sha256_file  # noqa: E402

ECICB = REPO / "inputs/TRIMOSKA-ECICB-2024/upstream/benchmarks"
ECICB_SUMS = REPO / "inputs/TRIMOSKA-ECICB-2024/UPSTREAM_SHA256SUMS.txt"
ARCHIVED_REFERENCE = REPO / "experiments/EXP-ICPERF-66fd51/runs/RUN-ICPERF-305ca3/results.jsonl"
SPEC = EXP_DIR / "specification.yaml"
ENUM_BIN = HERE / "bin" / "pdp_enum"

RSS_LIMIT_GB = 5.5
RSS_POLL_S = 0.25
DEFAULT_CFG_WATCHDOG_S = 600
DEFAULT_CFG_WATCHDOG_REASON = ("machine protection: the default (no -x) configuration's tree grows like 2^{ml} "
                               "in the small-cell series, i.e. days at ml = 40; a 600 s cap bounds session time. "
                               "A kill is resource_exhaustion for that configuration only.")
N43_WATCHDOG_S = 3 * 3600
N43_WATCHDOG_REASON = ("machine protection / capacity gate (spec decisive_cell.capacity_gate): one stable-V attempt "
                       "under a 3 h wall-clock cap and the resident-set limit; exhaustion is an impediment, not evidence.")
SMALL_WATCHDOG_S = 600

INFERENCE = {"requested_policy": "executor-implementation", "reasoning_effort": None,
             "resolved_model_id": "claude-fable-5.1 (Cursor cloud agent; model selected by the user in the launching session)",
             "model_provenance": "launching-session selection; no orchestration/adapter resolution",
             "model_verified": False,
             "model_verified_note": "no adapter backend is credentialed in this environment; identifier is unverified configuration",
             "fallback_used": False, "fallback_allowed": False, "degraded_allowed": False, "degraded_requirements": [],
             "bedrock_prohibition_observed": True}

PRIMARY_SEEDS = [2026092001, 2026092002, 2026092003]
RANDOM_V_SEED = 2026092010          # declared here; the random arm's V is a function of this seed only
N43_SEED = 2026092001

TRIALS = {
    "regression-gate": {"kind": "regression"},
    "pipeline-control": {"kind": "pipeline"},
    "n41-stable-1": {"kind": "cell", "n": 41, "m": 2, "l": 20, "vkind": "stable", "vindex": 0, "seed": PRIMARY_SEEDS[0]},
    "n41-stable-2": {"kind": "cell", "n": 41, "m": 2, "l": 20, "vkind": "stable", "vindex": 0, "seed": PRIMARY_SEEDS[1]},
    "n41-stable-3": {"kind": "cell", "n": 41, "m": 2, "l": 20, "vkind": "stable", "vindex": 0, "seed": PRIMARY_SEEDS[2]},
    "n41-random-1": {"kind": "cell", "n": 41, "m": 2, "l": 20, "vkind": "random", "vseed": RANDOM_V_SEED, "seed": PRIMARY_SEEDS[0]},
    "n41-random-2": {"kind": "cell", "n": 41, "m": 2, "l": 20, "vkind": "random", "vseed": RANDOM_V_SEED, "seed": PRIMARY_SEEDS[1]},
    "n41-random-3": {"kind": "cell", "n": 41, "m": 2, "l": 20, "vkind": "random", "vseed": RANDOM_V_SEED, "seed": PRIMARY_SEEDS[2]},
    "n43-stable-f0": {"kind": "cell", "n": 43, "m": 3, "l": 14, "vkind": "stable", "vindex": 0, "seed": N43_SEED, "decisive": True},
}


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def null_conflicts(m: int, l: int) -> Fraction:
    import math
    return Fraction(2 ** (m * l), math.factorial(m))


# ----------------------------------------------------------------------------- process supervision

PAGE_KB = os.sysconf("SC_PAGE_SIZE") // 1024


def pgid_rss_kb(pgid: int) -> int:
    total = 0
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        try:
            data = open(f"/proc/{entry}/stat", "rb").read()
            rest = data[data.rindex(b")") + 2:].split()
            if int(rest[2]) != pgid:
                continue
            total += int(open(f"/proc/{entry}/statm", "rb").read().split()[1]) * PAGE_KB
        except (OSError, ValueError, IndexError):
            continue
    return total


def kill_group(pgid: int, proc: subprocess.Popen) -> None:
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(pgid, sig)
        except (ProcessLookupError, PermissionError):
            pass
        try:
            proc.wait(timeout=5)
            return
        except subprocess.TimeoutExpired:
            continue


def mem_available_kb() -> int:
    for ln in open("/proc/meminfo"):
        if ln.startswith("MemAvailable"):
            return int(ln.split()[1])
    return -1


def run_process(argv, out_path: Path, err_path: Path, watchdog_s: int | None, watchdog_reason: str | None) -> dict:
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    rec = {"argv": [str(a) for a in argv], "started_at": now(), "loadavg_at_start": [round(x, 2) for x in os.getloadavg()],
           "mem_available_kb_at_start": mem_available_kb(), "watchdog_s": watchdog_s, "watchdog_reason": watchdog_reason,
           "rss_limit_gb": RSS_LIMIT_GB, "rss_poll_interval_s": RSS_POLL_S}
    limit_kb = int(RSS_LIMIT_GB * (1 << 20))
    t0 = time.monotonic()
    timed_out = breached = False
    peak_kb = 0
    with open(out_path, "wb") as fo, open(err_path, "wb") as fe:
        p = subprocess.Popen([str(a) for a in argv], stdout=fo, stderr=fe, stdin=subprocess.DEVNULL, start_new_session=True)
        pgid = p.pid
        while True:
            rc = p.poll()
            rss = pgid_rss_kb(pgid)
            peak_kb = max(peak_kb, rss)
            if rc is not None:
                break
            if rss > limit_kb:
                breached = True
                kill_group(pgid, p)
                rc = p.returncode
                break
            if watchdog_s is not None and time.monotonic() - t0 > watchdog_s:
                timed_out = True
                kill_group(pgid, p)
                rc = p.returncode
                break
            try:
                rc = p.wait(timeout=RSS_POLL_S)
            except subprocess.TimeoutExpired:
                continue
            break
    wall = time.monotonic() - t0
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    rec.update({"finished_at": now(), "wall_s": round(wall, 3), "returncode": rc, "timed_out": timed_out,
                "rss_limit_breached": breached, "peak_rss_kb_observed": peak_kb,
                "cpu_s": round((after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime), 3),
                "stdout": out_path.name, "stderr": err_path.name})
    return rec


# ----------------------------------------------------------------------------- WDSat on one ANF

def wdsat_row(run_dir: Path, anf: Path, config: str, tag: str, watchdog_s: int | None, reason: str | None) -> dict:
    sizing = anf_sizing(anf)
    logs = run_dir / "logs"
    logs.mkdir(exist_ok=True)
    buffer = None
    for attempt in range(5):
        exe, used = build_wdsat(run_dir / "builds", sizing, buffer)
        extra = ["-x"] if config == "gauss_elim" else []
        rec = run_process([exe, "-i", anf] + extra, logs / f"{tag}.{config}.out", logs / f"{tag}.{config}.err", watchdog_s, reason)
        err = (logs / f"{tag}.{config}.err").read_text(errors="replace")
        if "__MAX_BUFFER_SIZE__" in err and not rec["timed_out"]:
            buffer = 2 * used["constants"]["MAX_BUFFER_SIZE"]
            rec["note"] = f"buffer too small ({used['constants']['MAX_BUFFER_SIZE']}); rebuilt with {buffer}"
            continue
        break
    out = (logs / f"{tag}.{config}.out").read_text(errors="replace")
    parsed = parse_wdsat_output(out)
    rec.update({"config": config, "anf": str(anf.relative_to(run_dir)) if anf.is_relative_to(run_dir) else str(anf),
                "anf_sha256": sha256_file(anf), "wdsat_build": str(exe.parent.relative_to(run_dir)),
                "wdsat_constants": used["constants"], "STATIC_CLAUSE_STRING_SIZE": used["STATIC_CLAUSE_STRING_SIZE"],
                "wdsat_binary_sha256": used["binary_sha256"], "max_id_anf_match": used["constants"]["MAX_ID"] == sizing["MAX_ID"],
                "sizing": sizing, "stderr_head": err[:300], "solver_notes": parsed["solver_notes"]})
    if rec["timed_out"]:
        rec["status"] = "resource_exhaustion_wall_clock"
        rec["conflicts"] = None
    elif rec["rss_limit_breached"]:
        rec["status"] = "resource_exhaustion_rss"
        rec["conflicts"] = None
    elif parsed["status"] in ("SAT", "UNSAT"):
        rec["status"] = parsed["status"]
        rec["conflicts"] = parsed["conflicts"]
        rec["assignment"] = parsed["assignment"]
        rec["unsat_on_xorgauss_init"] = parsed.get("unsat_on_xorgauss_init", False)
    else:
        rec["status"] = f"infrastructure_error_exit_{rec['returncode']}"
        rec["conflicts"] = None
    return rec


def decode_and_verify_sat(inst: dict, bits: str) -> dict:
    """Decode the x-block of a WDSat assignment into X_i = sum x_{i,k} v_k and check the summation
    polynomial on the field (independent of WDSat and of the ANF)."""
    n, m, l = inst["n"], inst["m"], inst["l"]
    F = GF2n(n, int(inst["field"]["modulus_hex"], 16))
    V = [int(h, 16) for h in inst["V"]["basis_rref_hex"]]
    xr = int(inst["target"]["R_x_hex"], 16)
    if len(bits) < m * l:
        return {"verified": False, "why": "assignment shorter than m*l"}
    xs = []
    for i in range(m):
        X = 0
        for k in range(l):
            if bits[i * l + k] == "1":
                X ^= V[k]
        xs.append(X)
    val = semaev_s3(F, xs[0], xs[1], xr) if m == 2 else semaev_s4(F, xs[0], xs[1], xs[2], xr)
    # rational geometric check as well (m = 2 only: P1 +- P2 == R)
    geo = None
    if m == 2:
        E = KoblitzCurve(F, inst["curve"]["a"])
        P1s, P2s = E.lift_x(xs[0]), E.lift_x(xs[1])
        geo = any(E.add(P1, P2) is not None and E.add(P1, P2)[0] == xr for P1 in P1s for P2 in P2s)
    return {"verified": val == 0, "summation_polynomial_value_hex": hex(val), "x_hex": [hex(x) for x in xs],
            "all_in_V": all(in_span(V, x) for x in xs), "rational_geometric_decomposition": geo}


def certify(inst_dir: Path, limit: int | None = None) -> dict:
    argv = [sys.executable, str(HERE / "certify.py"), str(inst_dir), "--enum-bin", str(ENUM_BIN)]
    if limit is not None:
        argv += ["--limit", str(limit)]
    subprocess.run(argv, check=True, capture_output=True, text=True)
    return json.loads((inst_dir / "certificate.json").read_text())


# ----------------------------------------------------------------------------- trials

def trial_cell(run_dir: Path, t: dict) -> dict:
    n, m, l, seed = t["n"], t["m"], t["l"], t["seed"]
    null = null_conflicts(m, l)
    result = {"cell": {"n": n, "m": m, "l": l, "ml": m * l, "vkind": t["vkind"], "vindex": t.get("vindex"), "vseed": t.get("vseed"),
                       "seed": seed, "null_formula": "2^{ml}/m!", "null_conflicts_exact": f"{null.numerator}/{null.denominator}",
                       "null_conflicts_float": float(null)},
              "candidates": [], "instance": None, "certificate": None, "wdsat": {}, "ratios": {}}
    inst_dir = None
    for k in range(64):
        d = run_dir / "candidates" / f"candidate-{k}"
        inst = gen_instance.generate(n, m, l, t["vkind"], t.get("vindex", 0), t.get("vseed"), seed, k, False, d)
        cert = certify(d)
        row = {"candidate_index": k, "dir": str(d.relative_to(run_dir)), "R_x_hex": inst["target"]["R_x_hex"],
               "xr_in_V": inst["target"]["xr_in_V"], "certificate_kind": cert["certificate_kind"],
               "verdict": (cert["result"] or {}).get("verdict"), "certifier_elapsed_s": (cert["result"] or {}).get("elapsed_s"),
               "n_algebraic_witnesses": (cert["result"] or {}).get("n_algebraic_witnesses")}
        result["candidates"].append(row)
        if cert["certificate_kind"] == "exhaustive_enumeration_unsat" and not inst["target"]["xr_in_V"]:
            inst_dir = d
            result["instance"] = inst
            result["certificate"] = cert
            break
    if inst_dir is None:
        result["status"] = "instrument_failure_no_certified_unsat_candidate"
        return result
    anf = inst_dir / "instance.anf"
    decisive = t.get("decisive", False)
    configs = [("gauss_elim", N43_WATCHDOG_S if decisive else None, N43_WATCHDOG_REASON if decisive else None)]
    if not decisive:
        configs.append(("default", DEFAULT_CFG_WATCHDOG_S, DEFAULT_CFG_WATCHDOG_REASON))
    for cfg, wd, reason in configs:
        row = wdsat_row(run_dir, anf, cfg, f"n{n}-{t['vkind']}", wd, reason)
        if row["status"] == "SAT":
            row["sat_verification"] = decode_and_verify_sat(result["instance"], row["assignment"])
            row["scored"] = False
            row["not_scored_reason"] = "SAT row on an instance the certifier declared UNSAT: instrument disagreement, recorded, not scored"
        elif row["status"] == "UNSAT" and row["conflicts"] is not None and row["max_id_anf_match"]:
            r = Fraction(row["conflicts"]) / null
            row["scored"] = True
            row["conflict_ratio"] = float(r)
            row["conflict_ratio_exact"] = f"{r.numerator}/{r.denominator}"
            row["log2_conflicts"] = round(__import__("math").log2(row["conflicts"]), 4) if row["conflicts"] > 0 else None
            result["ratios"][cfg] = float(r)
        else:
            row["scored"] = False
            row["not_scored_reason"] = ("resource_exhaustion is never UNSAT and never a ratio (EX-4)" if row["status"].startswith("resource_exhaustion")
                                        else ("MAX_ID mismatch (C-SIZE)" if not row["max_id_anf_match"] else row["status"]))
        result["wdsat"][cfg] = row
    result["certified_unsat"] = True
    result["status"] = "completed"
    return result


def trial_regression(run_dir: Path, t: dict) -> dict:
    sums = {}
    for ln in ECICB_SUMS.read_text().splitlines():
        h, p = ln.split(None, 1)
        sums[p.strip()] = h
    rows = [json.loads(ln) for ln in ARCHIVED_REFERENCE.read_text().splitlines()]
    ref = {}
    for r in rows:
        if r.get("instance") == "n15l5-11-U" and r.get("engine") == "wdsat" and r.get("config") in ("default", "gauss_elim"):
            ref[r["config"]] = r["conflicts"]
    others = sorted({(r["engine"], r["config"], r["status"]) for r in rows if r.get("instance") == "n15l5-11-U" and r.get("engine") != "wdsat"})
    result = {"archived_reference": {"path": str(ARCHIVED_REFERENCE.relative_to(REPO)), "sha256": sha256_file(ARCHIVED_REFERENCE),
                                     "instance": "n15l5-11-U", "wdsat_conflicts": ref,
                                     "independent_engines_on_that_row_in_archive": [list(x) for x in others]},
              "inputs": {}, "wdsat": {}, "gate": {}}
    inst_dir = run_dir / "shipped"
    inst_dir.mkdir(exist_ok=True)
    for stem in ("Xn15l5-11-U.anf", "INFOn15l5-11-U.dimacs", "Xn15l5-1-S.anf", "INFOn15l5-1-S.dimacs"):
        src = ECICB / stem
        dst = inst_dir / stem
        dst.write_bytes(src.read_bytes())
        result["inputs"][stem] = {"sha256": sha256_file(dst), "upstream_manifest_sha256": sums.get(f"./benchmarks/{stem}"),
                                  "match": sha256_file(dst) == sums.get(f"./benchmarks/{stem}")}
    # WDSat on the shipped UNSAT instance, both configurations
    for cfg in ("default", "gauss_elim"):
        row = wdsat_row(run_dir, inst_dir / "Xn15l5-11-U.anf", cfg, "reg-n15l5-11-U", SMALL_WATCHDOG_S, "machine protection: regression row expected in < 2 s")
        row["archived_conflicts"] = ref.get(cfg)
        row["within_2x"] = (row["status"] == "UNSAT" and row["conflicts"] is not None and ref.get(cfg) is not None
                            and ref[cfg] / 2 <= row["conflicts"] <= 2 * ref[cfg])
        result["wdsat"][cfg] = row
    # WDSat on the shipped SAT instance (default) -- the assignment must verify on Trimoska's curve
    row = wdsat_row(run_dir, inst_dir / "Xn15l5-1-S.anf", "default", "reg-n15l5-1-S", SMALL_WATCHDOG_S, "machine protection")
    info_s = trimoska_info(inst_dir / "INFOn15l5-1-S.dimacs")
    if row["status"] == "SAT":
        row["sat_verification"] = verify_trimoska_assignment(info_s, row["assignment"])
    result["wdsat"]["shipped_sat_default"] = row
    # independent certifier on both shipped instances (Trimoska's field, curve a = 1, V = span{1..t^{l-1}})
    result["certifier_on_shipped"] = {}
    for stem, info_name in (("Xn15l5-11-U.anf", "INFOn15l5-11-U.dimacs"), ("Xn15l5-1-S.anf", "INFOn15l5-1-S.dimacs")):
        info = trimoska_info(inst_dir / info_name)
        d = inst_dir / f"certify-{stem[:-4]}"
        d.mkdir(exist_ok=True)
        write_trimoska_instance_json(info, d)
        cert = certify(d)
        result["certifier_on_shipped"][stem] = {"label": info["label"], "verdict": (cert["result"] or {}).get("verdict"),
                                                "certificate_kind": cert["certificate_kind"],
                                                "witnesses": (cert["result"] or {}).get("witnesses"),
                                                "shipped_certificate_x_hex": info.get("cert_x_hex"),
                                                "shipped_certificate_found_as_set": (
                                                    info.get("cert_x_hex") is not None and any(
                                                        sorted(int(x, 16) for x in w[:3]) == sorted(int(x, 16) for x in info["cert_x_hex"])
                                                        for w in (cert["result"] or {}).get("witnesses", [])))}
    gate_ok = all(result["wdsat"][c]["within_2x"] for c in ("default", "gauss_elim"))
    result["gate"] = {"C-REG": "PASS" if gate_ok else "FAIL",
                      "rule": "shipped Trimoska certified-UNSAT row n15l5-11-U; conflicts within 2x of the archived reference, per configuration",
                      "default": result["wdsat"]["default"]["within_2x"], "gauss_elim": result["wdsat"]["gauss_elim"]["within_2x"]}
    result["status"] = "completed" if gate_ok else "regression_gate_failed"
    return result


def trimoska_info(path: Path) -> dict:
    lines = [ln.strip() for ln in path.read_text().splitlines() if ln.strip()]
    n, l = (int(x) for x in lines[0].split())
    bits_to_int = lambda s: sum(1 << i for i, c in enumerate(s) if c == "1")
    info = {"n": n, "l": l, "modulus": bits_to_int(lines[1]), "xr": bits_to_int(lines[2]), "label": lines[3]}
    if info["label"] == "S":
        parts = lines[4].split("-")
        info["cert_x_hex"] = [hex(bits_to_int(p)) for p in parts]
    return info


def write_trimoska_instance_json(info: dict, d: Path) -> None:
    from frob_basis import rref
    F = GF2n(info["n"], info["modulus"])
    V = rref([1 << k for k in range(info["l"])])
    H = gen_instance.parity_check_rows(F, V)
    inst = {"n": info["n"], "m": 3, "l": info["l"], "field": {"modulus_hex": hex(info["modulus"])}, "curve": {"a": 1},
            "target": {"R_x_hex": hex(info["xr"])}, "V": {"basis_rref_hex": [hex(v) for v in V]},
            "V_parity_check_rows_hex": [hex(h) for h in H], "anf": {"sha256": None},
            "note": "Trimoska shipped instance: curve y^2+xy=x^3+x^2+1 (Sage EllipticCurve(K,[1,1,0,0,1])), V = span{1,t,..,t^(l-1)}"}
    (d / "instance.json").write_text(json.dumps(inst, indent=1))


def verify_trimoska_assignment(info: dict, bits: str) -> dict:
    F = GF2n(info["n"], info["modulus"])
    l = info["l"]
    xs = [sum(1 << k for k in range(l) if bits[i * l + k] == "1") for i in range(3)]
    val = semaev_s4(F, xs[0], xs[1], xs[2], info["xr"])
    return {"verified": val == 0, "x_hex": [hex(x) for x in xs], "matches_shipped_certificate_as_set": sorted(xs) == sorted(int(h, 16) for h in info.get("cert_x_hex", []))}


def trial_pipeline(run_dir: Path, t: dict) -> dict:
    """Planted-SAT and certified-UNSAT controls at small n, both V kinds, both configurations."""
    plan = [
        # (label, n, m, l, vkind, vindex/vseed, seed, plant)
        ("plant-n17-m2-stable", 17, 2, 8, "stable", 0, 101, True),
        ("plant-n17-m2-random", 17, 2, 8, "random", 2026092011, 102, True),
        ("plant-n23-m3-random", 23, 3, 5, "random", 2026092012, 103, True),
        ("plant-n31-m3-stable", 31, 3, 5, "stable", 0, 104, True),
        ("unsat-n17-m2-stable", 17, 2, 8, "stable", 0, 111, False),
        ("unsat-n17-m2-random", 17, 2, 8, "random", 2026092013, 112, False),
        ("unsat-n23-m2-stable", 23, 2, 11, "stable", 0, 113, False),
        ("unsat-n23-m2-random", 23, 2, 11, "random", 2026092014, 114, False),
        # n = 31: ord(2 mod 31) = 5, so the only single-factor stable subspaces have dimension 5
        # (RUN-FROB-bb2096 aborted asking for dimension 15 here; see implementation.md)
        ("unsat-n31-m2-stable", 31, 2, 5, "stable", 0, 115, False),
        ("unsat-n31-m2-random", 31, 2, 5, "random", 2026092015, 116, False),
        # ml = 33 bridge toward the n = 43, m = 3 decisive cell (ml = 42): certifier cost 2^22 pairs.
        # ml > n here, so a random target is expected to have ~2^{ml}/(m! 2^n) ~ 170 decompositions and
        # certified-UNSAT targets are rare; every candidate's witness count is recorded (candidate_survey).
        ("unsat-n23-m3-stable", 23, 3, 11, "stable", 0, 119, False),
        ("unsat-n23-m3-random", 23, 3, 11, "random", 2026092017, 120, False),
        ("unsat-n31-m3-stable", 31, 3, 5, "stable", 1, 117, False),
        ("unsat-n31-m3-random", 31, 3, 5, "random", 2026092016, 118, False),
    ]
    result = {"rows": [], "agreement": {"checked": 0, "disagreements": []}, "row_errors": []}
    for label, n, m, l, vkind, vsel, seed, plant in plan:
        try:
            pipeline_row(run_dir, result, label, n, m, l, vkind, vsel, seed, plant)
        except (Exception, SystemExit):  # keep every completed row; the run is still an implementation_error
            import traceback
            result["row_errors"].append({"label": label, "exception": traceback.format_exc()})
    if result["row_errors"]:
        result["status"] = "implementation_error"
    else:
        result["status"] = "completed" if not result["agreement"]["disagreements"] else "instrument_disagreement"
    return result


def pipeline_row(run_dir: Path, result: dict, label, n, m, l, vkind, vsel, seed, plant) -> None:
    d = run_dir / "instances" / label
    vindex = vsel if vkind == "stable" else 0
    vseed = vsel if vkind == "random" else None
    row = {"label": label, "n": n, "m": m, "l": l, "ml": m * l, "vkind": vkind, "seed": seed, "planted": plant,
           "null_conflicts_float": float(null_conflicts(m, l)), "candidate_survey": []}
    chosen = None
    for k in range(32):
        inst = gen_instance.generate(n, m, l, vkind, vindex, vseed, seed, k, plant, d / f"candidate-{k}")
        cert = certify(d / f"candidate-{k}", limit=None)
        cr = cert["result"] or {}
        verdict = cr.get("verdict")
        row["candidate_survey"].append({"k": k, "R_x_hex": inst["target"]["R_x_hex"], "xr_in_V": inst["target"]["xr_in_V"],
                                        "verdict": verdict, "n_algebraic_witnesses": cr.get("n_algebraic_witnesses"),
                                        "n_geometric_rational_witnesses": cr.get("n_geometric_rational_witnesses"),
                                        "certifier_elapsed_s": cr.get("elapsed_s")})
        if plant or (verdict == "UNSAT" and not inst["target"]["xr_in_V"]):
            chosen = (inst, cert, k)
            break
    if chosen is None:
        row["status"] = "no_certified_unsat_among_32_candidates"
        row["note"] = "no WDSat row: nothing to compare against a certificate here; the survey above is the record"
        result["rows"].append(row)
        return
    inst, cert, k = chosen
    row["status"] = "completed"
    row.update({"candidate_index": k, "certifier_verdict": (cert["result"] or {}).get("verdict"),
                "certificate_kind": cert["certificate_kind"], "instance_dir": str((d / f"candidate-{k}").relative_to(run_dir)),
                "anf_sha256": inst["anf"]["sha256"], "planted_witness": inst.get("planted_witness")})
    if plant:
        pw = inst["planted_witness"]["x_hex"]
        row["planted_witness_found_by_certifier"] = any(sorted(int(x, 16) for x in w[:m]) == sorted(int(x, 16) for x in pw)
                                                        for w in (cert["result"] or {}).get("witnesses", []))
    row["wdsat"] = {}
    for cfg in ("gauss_elim", "default"):
        w = wdsat_row(run_dir, d / f"candidate-{k}" / "instance.anf", cfg, label, SMALL_WATCHDOG_S,
                      "machine protection: small-cell control; a kill is recorded as resource_exhaustion for that configuration")
        if w["status"] == "SAT":
            w["sat_verification"] = decode_and_verify_sat(inst, w["assignment"])
        if w["status"] == "UNSAT" and w["conflicts"] is not None:
            w["conflict_ratio"] = float(Fraction(w["conflicts"]) / null_conflicts(m, l))
        row["wdsat"][cfg] = {kk: w[kk] for kk in ("status", "conflicts", "wall_s", "cpu_s", "peak_rss_kb_observed", "timed_out",
                                                     "wdsat_constants", "max_id_anf_match", "conflict_ratio", "sat_verification",
                                                     "unsat_on_xorgauss_init") if kk in w}
        row["wdsat"][cfg]["log"] = w["stdout"]
        if w["status"] in ("SAT", "UNSAT"):
            result["agreement"]["checked"] += 1
            if w["status"] != row["certifier_verdict"]:
                result["agreement"]["disagreements"].append({"label": label, "config": cfg, "wdsat": w["status"], "certifier": row["certifier_verdict"]})
            if w["status"] == "SAT" and not w["sat_verification"]["verified"]:
                result["agreement"]["disagreements"].append({"label": label, "config": cfg, "wdsat": "SAT", "assignment_fails_on_curve": True})
    result["rows"].append(row)


# ----------------------------------------------------------------------------- manifest

def environment() -> dict:
    gcc = subprocess.run(["gcc", "--version"], capture_output=True, text=True).stdout.splitlines()[0]
    head = (REPO / ".git" / "HEAD").read_text().strip()
    commit = head
    if head.startswith("ref: "):
        refp = REPO / ".git" / head[5:]
        commit = refp.read_text().strip() if refp.exists() else None
        if commit is None:
            packed = REPO / ".git" / "packed-refs"
            for ln in packed.read_text().splitlines() if packed.exists() else []:
                if ln.endswith(" " + head[5:]):
                    commit = ln.split()[0]
    impl_files = {str(p.relative_to(REPO)): sha256_file(p) for p in sorted(HERE.iterdir()) if p.is_file()}
    impl_files[str((HERE / "bin" / "pdp_enum").relative_to(REPO))] = sha256_file(HERE / "bin" / "pdp_enum")
    return {"python": sys.version.split()[0], "platform": platform.platform(), "cpu_count": os.cpu_count(),
            "cpu_model": next((ln.split(":", 1)[1].strip() for ln in open("/proc/cpuinfo") if ln.startswith("model name")), None),
            "mem_total_kb": int(next(ln.split()[1] for ln in open("/proc/meminfo") if ln.startswith("MemTotal"))),
            "mem_available_kb_at_start": mem_available_kb(), "loadavg_at_start": [round(x, 2) for x in os.getloadavg()],
            "gcc": gcc, "pyyaml": yaml.__version__,
            "git": {"head_ref": head, "commit": commit,
                    "dirty_tree": True,
                    "dirty_tree_note": ("determined without invoking git (card: run no git command): the working tree carries this task's "
                                        "uncommitted implementation/ and runs/ artifacts; every implementation file that ran is hashed below"),
                    "implementation_sha256": impl_files},
            "specification_sha256": sha256_file(SPEC), "wdsat_vendored_source": verify_vendored_source(),
            "rss_limit_gb": RSS_LIMIT_GB, "rss_poll_interval_s": RSS_POLL_S, "rlimit_as_set": False}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trial", required=True, choices=sorted(TRIALS))
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--run-dir", required=True)
    a = ap.parse_args()
    t = TRIALS[a.trial]
    run_dir = Path(a.run_dir).resolve()
    # stdout.log / stderr.log are the caller's redirection targets and may already exist (empty)
    if run_dir.exists() and any(p.name not in ("stdout.log", "stderr.log") for p in run_dir.iterdir()):
        raise SystemExit(f"refusing to write into a non-empty run directory {run_dir} (runs are immutable)")
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "command.txt").write_text(" ".join([sys.executable] + sys.argv) + f"\ncwd: {os.getcwd()}\n")
    started = now()
    env = environment()
    (run_dir / "environment.json").write_text(json.dumps(env, indent=1))
    if not ENUM_BIN.exists():
        raise SystemExit("pdp_enum binary missing; build it first (see implementation.md)")
    print(f"[{started}] trial {a.trial} run {a.run_id} -> {run_dir}", flush=True)
    result = {"schema": "EXP-FROB-30006a.raw_result.v1", "experiment_id": EXP_ID, "run_id": a.run_id, "trial_id": a.trial,
              "trial": t, "started_at": started}
    try:
        if t["kind"] == "regression":
            result.update(trial_regression(run_dir, t))
        elif t["kind"] == "pipeline":
            result.update(trial_pipeline(run_dir, t))
        else:
            result.update(trial_cell(run_dir, t))
    except (Exception, SystemExit):  # SystemExit too: a generator refusal must still leave a manifest (RUN-FROB-bb2096)
        import traceback
        result["status"] = "implementation_error"
        result["exception"] = traceback.format_exc()
    result["finished_at"] = now()
    # Build products are not run records: keep src/, makefile, make.log and config_used.json (which carries
    # binary_sha256) and drop the compiled binary, matching the EXP-ICPERF-e21835 builds/ convention.
    for exe in (run_dir / "builds").glob("*/wdsat_solver"):
        exe.unlink()
    (run_dir / "raw-result.json").write_text(json.dumps(result, indent=1, default=str))
    manifest = build_manifest(a, t, env, result, run_dir)
    (run_dir / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False, width=110, allow_unicode=True))
    yaml.safe_load((run_dir / "manifest.yaml").read_text())
    print(f"[{now()}] status={result.get('status')}", flush=True)
    return 0 if result.get("status") == "completed" else 3


def classify(result: dict) -> tuple[str, bool, str | None]:
    st = result.get("status")
    if st == "completed":
        return "completed_valid", True, None
    if st == "regression_gate_failed":
        return "invalid_measurement", False, "regression gate failed: procedure defect, not evidence"
    if st == "implementation_error":
        return "implementation_error", False, "driver raised; see raw-result.json exception"
    if st == "instrument_disagreement":
        return "invalid_measurement", False, "WDSat and the independent certifier disagree on a control instance"
    if st and st.startswith("instrument_failure"):
        return "invalid_measurement", False, st
    return st or "unknown", False, st


def build_manifest(a, t, env, result, run_dir) -> dict:
    validity, valid, reason = classify(result)
    files = sorted(str(p.relative_to(run_dir)) for p in run_dir.rglob("*") if p.is_file() and "builds" not in p.parts[:1])
    m = {"run": {"id": a.run_id, "experiment_id": EXP_ID, "hypothesis_id": "H-FROB-a5bf86", "goal_id": "GOAL-FROB-6333a9",
                 "task_id": "TASK-20260920-66a30e", "trial_id": a.trial, "status": validity, "valid": valid,
                 "invalid_reason": reason, "started_at": result["started_at"], "finished_at": result["finished_at"]},
         "protocol": {"specification": "experiments/EXP-FROB-30006a/specification.yaml", "specification_sha256": env["specification_sha256"],
                      "approved_by": "DEC-20260920-cf8ded", "heuristic_under_test": "HEUR-FROB-WDSAT-NULL (new prior; NOT attributed to IDEA-20260906-a77711, DEC-20260920-f1e672)",
                      "class": "measurement", "claim_tier": "toy"},
         "command": {"argv": [sys.executable] + sys.argv, "cwd": os.getcwd(), "driver": "experiments/EXP-FROB-30006a/implementation/run_trial.py"},
         "code": env["git"], "environment": {k: env[k] for k in ("python", "platform", "cpu_count", "cpu_model", "mem_total_kb",
                                                                  "mem_available_kb_at_start", "loadavg_at_start", "gcc", "pyyaml",
                                                                  "rss_limit_gb", "rss_poll_interval_s", "rlimit_as_set")},
         "wdsat_source_verified_against_upstream_manifest": env["wdsat_vendored_source"]["ok"],
         "randomness": randomness_block(t, result),
         "inference": INFERENCE,
         "certificate": certificate_block(t, result),
         "result_summary": summary_block(t, result),
         "artifacts": files,
         "notes": ["Observations only; no verdict under the decision_rule is asserted here.",
                   "A killed process is resource_exhaustion, never UNSAT and never a ratio (EX-4).",
                   "Both WDSat configurations (-x Gaussian elimination and default) are reported; the frozen contract names the solver but not the flag."]}
    return m


def randomness_block(t, result) -> dict:
    if t["kind"] == "cell":
        return {"target_seed": t["seed"], "target_draw_rule": "random.Random(seed): k-th uniform random affine point; first candidate certified UNSAT (and with x_R not in V) is the target",
                "candidates_examined": len(result.get("candidates", [])),
                "random_V_seed": t.get("vseed"), "stable_V": "deterministic: ker g_vindex(sigma)",
                "wdsat": "deterministic (no randomness in WDSat)", "certifier": "deterministic enumeration"}
    if t["kind"] == "pipeline":
        return {"seeds": "per row in raw-result.json (target seed, planted-point seed = seed ^ 0x5A17, random-V seed)", "wdsat": "deterministic"}
    return {"seeds": "none: shipped Trimoska instances and deterministic solver", "wdsat": "deterministic"}


def certificate_block(t, result) -> dict:
    if t["kind"] == "cell" and result.get("certificate"):
        c = result["certificate"]
        return {"kind": "exhaustive_enumeration_unsat", "tool": "implementation/pdp_enum.c (independent of WDSat and of the ANF generator)",
                "path": str(Path(result["candidates"][-1]["dir"]) / "certificate.json"), "enum_bin_sha256": c["enum_bin_sha256"],
                "verdict": c["result"]["verdict"], "complete": c["result"]["complete"], "elapsed_s": c["result"]["elapsed_s"],
                "predicate": "exists X_1..X_m in V with S_{m+1}(X_1..X_m, x_R) = 0 over GF(2^n) (the predicate the ANF encodes)",
                "re_verified_independently_of_solver": True}
    if t["kind"] == "cell":
        return {"kind": "none", "why": result.get("status")}
    return {"kind": "none", "why": "control run; per-instance certificates are under the run directory and summarised in raw-result.json"}


def summary_block(t, result) -> dict:
    if t["kind"] == "cell":
        s = {"status": result.get("status"), "certified_unsat": result.get("certified_unsat", False),
             "null_conflicts_exact": result["cell"]["null_conflicts_exact"], "per_config": {}}
        for cfg, row in result.get("wdsat", {}).items():
            s["per_config"][cfg] = {k: row.get(k) for k in ("status", "conflicts", "conflict_ratio", "conflict_ratio_exact", "log2_conflicts",
                                                            "scored", "not_scored_reason", "wall_s", "cpu_s", "peak_rss_kb_observed",
                                                            "timed_out", "watchdog_s", "max_id_anf_match", "loadavg_at_start")}
            s["per_config"][cfg]["MAX_ID"] = row["wdsat_constants"]["MAX_ID"]
        return s
    if t["kind"] == "regression":
        return {"status": result.get("status"), "gate": result.get("gate"),
                "measured_conflicts": {c: result["wdsat"][c].get("conflicts") for c in ("default", "gauss_elim") if c in result.get("wdsat", {})},
                "archived_conflicts": result.get("archived_reference", {}).get("wdsat_conflicts"),
                "certifier_on_shipped": {k: {kk: v[kk] for kk in ("label", "verdict", "shipped_certificate_found_as_set")} for k, v in result.get("certifier_on_shipped", {}).items()}}
    return {"status": result.get("status"), "agreement": result.get("agreement"),
            "rows": [{k: r.get(k) for k in ("label", "certifier_verdict", "planted_witness_found_by_certifier")} | {
                "wdsat": {c: {kk: w.get(kk) for kk in ("status", "conflicts", "conflict_ratio", "wall_s")} for c, w in r.get("wdsat", {}).items()}}
                     for r in result.get("rows", [])]}


if __name__ == "__main__":
    raise SystemExit(main())
