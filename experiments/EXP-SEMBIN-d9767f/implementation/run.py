#!/usr/bin/env python3
"""EXP-SEMBIN-d9767f trial driver (H-SEMBIN-106967): minimal refuting
mutant-closure degree D_W of chained-S_3 descended decomposition systems.

    run.py --run-dir RUN_DIR --run-id RUN --trial-id T --seed S --plan PLAN

Reads the trial's cell list from the frozen trial plan, builds the pilot
sources from implementation/ into RUN_DIR/build (build.sh), and for every cell:
picks the curves, builds V, draws x(2P) targets from the seeded stream, labels
every target with two independent enumerators and the point check, runs the
closures M_3, W_3, M_4, W_4 (W_5 where C(N,<=5) <= 40000) with both GF(2)
eliminators where both apply, the block-local L2adj1 arm, the nulls and the
controls the plan names. One worker process at a time; a job exceeding the
per-job RSS or wall cap is recorded as censored, never as a result.

Outputs in RUN_DIR: raw-result.json (sembin.closure_degree.result.v1, with the
build environment under /environment), results.jsonl (raw per job),
instances.json (labels and solutions), manifest.yaml; environment.json only
when absent (under the supervisor it is the supervisor's own record). The
progress log goes to stdout (the supervisor's stdout.log).
Exit 0 on completion, 3 on an implementation error. Python 3 stdlib + numpy.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
import platform
import random
import resource
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

SCHEMA = "sembin.closure_degree.result.v1"
EXPERIMENT_ID = "EXP-SEMBIN-d9767f"
HYPOTHESIS_ID = "H-SEMBIN-106967"
IMPL = Path(__file__).resolve().parent
DEFAULTS = {
    "curves": {"rule": "pick_curve_seeds", "seeds": [0, 1, 2]},
    "max_targets_per_curve": 150,
    "min_unsat_per_curve": 30,
    "min_unsat_null": 10,
    "min_labelled_dense": 10,
    "closure_degrees": [3, 4],
    "w5_max_columns": 40000,
    "independent_primary_above_columns": 50000,
    "m4ri_max_columns": 100000,
    "job_rss_cap_gb": 6,
    "job_wall_cap_s": 1800,
    "solution_cap": 256,
    "skip_after_consecutive_censored": None,
}
INSTANCE_FIELDS = ["instance_id", "cell", "m", "n", "k", "v_type", "family", "curve_b", "label", "nsol",
                   "closure_kind", "D", "eliminator", "contains_one", "rank", "cols", "rows", "codim",
                   "iterations", "ops_proxy", "wall_s", "peak_rss_mb", "censored", "elimination_faults",
                   "evalcheck_mismatch"]
DETERMINISM_EXCLUDED = ["wall_s", "peak_rss_mb"]


class ImplementationError(Exception):
    pass


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def comb_le(N: int, D: int) -> int:
    return sum(math.comb(N, d) for d in range(D + 1))


def clopper_pearson(x: int, n: int, alpha: float = 0.05) -> list | None:
    """Exact binomial interval by bisection on the binomial tail (stdlib only)."""
    if n == 0:
        return None

    def tail_ge(p):  # P[X >= x]
        return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(x, n + 1))

    def tail_le(p):  # P[X <= x]
        return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, x + 1))

    def solve(f, target):
        lo, hi = 0.0, 1.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if f(mid) < target:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    lower = 0.0 if x == 0 else solve(tail_ge, alpha / 2)
    upper = 1.0 if x == n else 1.0 - solve(lambda p: tail_le(1 - p), alpha / 2)
    return [round(lower, 6), round(upper, 6)]


# ----------------------------------------------------------------------------
# build and library loading
# ----------------------------------------------------------------------------

def build(run_dir: Path) -> tuple[Path, dict]:
    bdir = run_dir / "build"
    if bdir.exists():
        shutil.rmtree(bdir)
    r = subprocess.run(["sh", str(IMPL / "build.sh"), str(IMPL), str(bdir)], capture_output=True, text=True)
    info_path = bdir / "build-info.json"
    if r.returncode != 0 or not info_path.is_file():
        raise ImplementationError(f"build.sh failed rc={r.returncode}: {r.stderr[-500:]}")
    info = json.loads(info_path.read_text())
    info["build_log"] = (bdir / "build.log").read_text()[-2000:]
    return bdir, info


def load_libs(bdir: Path):
    sys.path.insert(0, str(bdir))
    import pilot_lib as L  # noqa: PLC0415
    import pilot2_lib as P  # noqa: PLC0415
    import pilot3  # noqa: PLC0415  (blocks / parse_variant for the block-local arm)
    return L, P, pilot3


# ----------------------------------------------------------------------------
# curves, V, targets
# ----------------------------------------------------------------------------

def pick_curves(L, n: int, rule: dict) -> list[dict]:
    out, seen = [], set()
    if rule["rule"] == "pick_curve_seeds":
        seeds = list(rule["seeds"])
        extra = max(seeds) + 1
        for s in seeds:
            cv = L.pick_curve(n, s)
            while cv["b"] in seen:  # two seeds hit one curve: take the next unseen seed
                cv = L.pick_curve(n, extra)
                s = extra
                extra += 1
            cv["pick_seed"] = s
            seen.add(cv["b"])
            out.append(cv)
    elif rule["rule"] == "b_upward":
        modulus, _ = L.boolsys.modulus_for(n)
        F = L.Field(n, modulus)
        b = 2
        while len(out) < int(rule["count"]):
            E = L.Curve(F, 1, b)
            order = E.count_points()
            if order % 2 == 0 and L.is_prime(order // 2):
                out.append({"F": F, "E": E, "a": 1, "b": b, "order": order, "q": order // 2, "h": 2,
                            "modulus": modulus, "tries": b - 1, "pick_seed": None})
            b += 1
    else:
        raise ImplementationError(f"unknown curve rule {rule}")
    return out


def rank_gf2(rows: list[int]) -> int:
    piv = []
    for v in rows:
        for p in piv:
            v = min(v, v ^ p)
        if v:
            piv.append(v)
    return len(piv)


def random_basis(n: int, k: int, seed: int, curve_index: int) -> list[int]:
    """Uniform full-rank k x n F_2 matrix; subspace seed = first 8 bytes of
    sha256('V|seed|curve_index') (design memo / trial plan)."""
    h = hashlib.sha256(f"V|{seed}|{curve_index}".encode()).digest()[:8]
    rng = random.Random(int.from_bytes(h, "big"))
    while True:
        rows = [rng.getrandbits(n) for _ in range(k)]
        if rank_gf2(rows) == k:
            return rows


# ----------------------------------------------------------------------------
# labelling
# ----------------------------------------------------------------------------

def count_dense(P, system, sol_cap=4096):
    """count_dense over all 2^N assignments (no N <= 26 assertion; the plan
    limits the dense null to N <= 30)."""
    import ctypes  # noqa: PLC0415
    from array import array  # noqa: PLC0415
    N, eqs = system["N"], system["equations"]
    ptr = array("q", [0]); masks = array("Q")
    for e in eqs:
        masks.extend(e); ptr.append(len(masks))
    sol = (ctypes.c_uint64 * sol_cap)()
    ns = ctypes.c_long(0)
    pb = (ctypes.c_long * len(ptr)).from_buffer(ptr)
    mb = (ctypes.c_uint64 * max(1, len(masks))).from_buffer(masks)
    tot = P._cc.count_dense(N, len(eqs), ctypes.addressof(pb), ctypes.addressof(mb), sol, sol_cap, ctypes.byref(ns))
    return int(tot), sorted(int(sol[i]) for i in range(ns.value))


def eq_sha256(eqs) -> str:
    return sha256_text(canonical([sorted(e) for e in eqs]))


def label_s3(L, P, cv, V, basis, m, n, k, z, cap):
    t0 = time.time()
    sols = P.chain_solutions(cv["F"], V, cv["b"], z, m)
    t1 = time.time()
    sysm = P.build_chain(n, k, m, basis, cv["b"], z, cv["modulus"])
    cnt, bsols = P.boolean_count_chain(sysm)
    t2 = time.time()
    agree = (cnt == len(sols)) and (bsols == sols[:len(bsols)])
    eval_ok = all(not any(L.eval_system(sysm["equations"], s)) for s in sols[:cap])
    pc = [bool(P.point_check(cv, V, m, s, z)) for s in sols[:4]]
    return sysm, {"nsol": len(sols), "nsol_boolean": int(cnt), "enum_agree": bool(agree), "eval_ok": bool(eval_ok),
                  "point_check": pc, "solutions": sols[:cap], "enum_curve_s": round(t1 - t0, 4),
                  "enum_bool_s": round(t2 - t1, 4)}


def label_m2(L, cv, V, basis, n, k, z, cap):
    t0 = time.time()
    sols = L.m2_solutions(cv["F"], V, cv["b"], z)
    t1 = time.time()
    sysm = L.build_m2(n, k, basis, cv["b"], z, cv["modulus"])
    sysm["m"] = 2
    cnt, bsols = L.boolean_count_m2(sysm)
    t2 = time.time()
    agree = (cnt == len(sols)) and (sorted(bsols) == sols[:len(bsols)])
    eval_ok = all(not any(L.eval_system(sysm["equations"], s)) for s in sols[:cap])
    return sysm, {"nsol": len(sols), "nsol_boolean": int(cnt), "enum_agree": bool(agree), "eval_ok": bool(eval_ok),
                  "point_check": [], "solutions": sols[:cap], "enum_curve_s": round(t1 - t0, 4),
                  "enum_bool_s": round(t2 - t1, 4)}


# ----------------------------------------------------------------------------
# closure jobs
# ----------------------------------------------------------------------------

class JobRunner:
    def __init__(self, bdir: Path, run_dir: Path, cfg: dict, m4ri: bool, results_path: Path):
        self.bdir, self.run_dir, self.cfg, self.m4ri = bdir, run_dir, cfg, m4ri
        self.jobdir = run_dir / "build" / "jobs"
        self.jobdir.mkdir(exist_ok=True)
        self.results = results_path.open("a")
        self.njobs = 0
        self.consecutive_censored: dict[tuple, int] = {}

    def close(self):
        self.results.close()

    def _spawn(self, script: str, job: dict, tag: str) -> dict:
        jp, op = self.jobdir / f"{tag}.json", self.jobdir / f"{tag}.out.json"
        jp.write_text(json.dumps(job))
        lim = int(self.cfg["job_rss_cap_gb"] * (1 << 30))

        def pre():
            resource.setrlimit(resource.RLIMIT_AS, (lim, lim))
            os.setsid()
        t0 = time.time()
        proc = subprocess.Popen([sys.executable, str(self.bdir / script), str(jp), str(op)],
                                stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, preexec_fn=pre, cwd=self.bdir)
        try:
            _, err = proc.communicate(timeout=self.cfg["job_wall_cap_s"])
            rc = proc.returncode
            err = err.decode(errors="replace")
            if rc == 0 and op.is_file():
                o = json.loads(op.read_text())
                o["status"] = o.get("status", "completed")
            else:
                mem = ("MemoryError" in err or "Cannot allocate" in err or "std::bad_alloc" in err
                       or rc in (-signal.SIGKILL, -signal.SIGABRT, -signal.SIGSEGV, 137))
                o = {"status": "censored_rss" if mem else f"worker_rc{rc}", "stderr_tail": err[-400:]}
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except OSError:
                pass
            proc.wait()
            o = {"status": "censored_timeout"}
        o["outer_wall_s"] = round(time.time() - t0, 3)
        if o.get("status") == "unreached_memory_cap":
            o["status"] = "censored_mem_cap"
        for p in (jp, op):
            try:
                p.unlink()
            except OSError:
                pass
        return o

    def run(self, inst: dict, system: dict, kind: str, D: int, eliminator: str, variant: str | None,
            blocks=None) -> dict:
        """kind: M | W; eliminator: m4ri | independent; variant: None or L2adj1."""
        eqs = system["equations"]
        N = system["N"]
        key = (inst["cell_key"], kind, D, eliminator, variant)
        skip = self.cfg.get("skip_after_consecutive_censored")
        row = {"instance_id": inst["instance_id"], "cell_key": inst["cell_key"], "closure_kind": variant or kind,
               "D": D, "eliminator": eliminator, "N": N, "neq": len(eqs), "mem_cap_gb": self.cfg["job_rss_cap_gb"],
               "timeout_s": self.cfg["job_wall_cap_s"]}
        if skip and self.consecutive_censored.get(key, 0) >= skip:
            o = {"status": "censored_skipped_after_consecutive_censoring", "outer_wall_s": 0.0}
        elif variant:
            lo, hi, nb = blocks
            Lmax, adj = variant_params(variant, nb)
            job = {"N": N, "equations": eqs, "D": D, "lo": lo, "hi": hi, "Lmax": Lmax, "adj": adj,
                   "stop_at_one": 1, "witnesses": inst["solutions"][:16]}
            o = self._spawn("worker3.py", job, f"{inst['instance_id']}-{variant}")
            row.update({"Lmax": Lmax, "adj": adj})
        else:
            wk = kind if eliminator == "m4ri" else "my" + kind
            job = {"N": N, "equations": eqs, "kind": wk, "D": D, "mem_cap_gb": float(self.cfg["job_rss_cap_gb"]),
                   "witnesses": inst["solutions"][:64],
                   "evalcheck": bool(inst["solutions"]) and eliminator == "m4ri"}
            o = self._spawn("worker.py", job, f"{inst['instance_id']}-{wk}{D}")
        self.njobs += 1
        row.update(o)
        row["censored"] = str(o.get("status", "")).startswith("censored")
        row["completed"] = o.get("status") == "completed"
        if row["censored"]:
            self.consecutive_censored[key] = self.consecutive_censored.get(key, 0) + 1
        elif row["completed"]:
            self.consecutive_censored[key] = 0
        if row["completed"]:
            row["codim"] = int(o["ncols"]) - int(o["rank"])
            if eliminator == "m4ri" and isinstance(o.get("iterations"), list):
                row["n_iterations"] = len(o["iterations"])
                row["ops_proxy"] = int(sum(int(it["rows"]) * int(o["ncols"]) for it in o["iterations"]))
            else:
                row["n_iterations"] = 1
                row["ops_proxy"] = int(o.get("rows", 0)) * int(o["ncols"])
            row["evalcheck_mismatch"] = int(o.get("ech_evalcheck_mismatch") or 0) + int(sum(o.get("eval_rows_not_vanishing") or []))
            row["elimination_faults"] = int(o.get("elimination_faults") or 0)
        self.results.write(json.dumps(row, sort_keys=True) + "\n")
        self.results.flush()
        return row


def variant_params(variant: str, nblocks: int) -> tuple[int, int]:
    Lmax, adj = nblocks, -1
    s = variant
    if s.startswith("L"):
        num = ""
        s = s[1:]
        while s and s[0].isdigit():
            num += s[0]; s = s[1:]
        Lmax = int(num)
    if s.startswith("adj"):
        adj = int(s[3:]); s = ""
    if s:
        raise ImplementationError(f"bad block-local variant {variant}")
    return Lmax, adj


def flatten(inst: dict, row: dict) -> dict:
    completed = bool(row.get("completed"))
    return {
        "instance_id": inst["instance_id"], "cell": inst["cell"], "m": inst["m"], "n": inst["n"], "k": inst["k"],
        "v_type": inst["v_type"], "family": inst["family"], "curve_b": inst["curve_b"], "label": inst["label"],
        "nsol": inst["nsol"], "closure_kind": row["closure_kind"], "D": row["D"], "eliminator": row["eliminator"],
        "contains_one": bool(row["contains_one"]) if completed else None,
        "rank": int(row["rank"]) if completed else None,
        "cols": int(row["ncols"]) if completed else None,
        "rows": int(row.get("rows")) if completed and row.get("rows") is not None else None,
        "codim": row.get("codim") if completed else None,
        "iterations": row.get("n_iterations") if completed else None,
        "ops_proxy": row.get("ops_proxy") if completed else None,
        "wall_s": round(float(row.get("wall_s", row.get("outer_wall_s", 0.0))), 4),
        "peak_rss_mb": round(float(row.get("peak_rss_mb", 0.0)), 2),
        "censored": bool(row["censored"]),
        "elimination_faults": row.get("elimination_faults", 0) if completed else 0,
        "evalcheck_mismatch": row.get("evalcheck_mismatch", 0) if completed else 0,
        # descriptive extras (not in the frozen field list, never used by the criteria)
        "status": row.get("status"), "cell_key": inst["cell_key"], "rep": inst.get("rep", 0),
        "curve_index": inst["curve_index"], "z": inst["z"], "N": inst["N"],
    }


# ----------------------------------------------------------------------------
# one cell
# ----------------------------------------------------------------------------

def cell_key_of(spec: dict) -> str:
    fam = spec.get("family", "S3")
    key = f"{spec['cell']}-{spec['v_type']}"
    if fam != "S3":
        key += f"-{fam}"
    if spec.get("role") in ("c1_pilot_gate", "c6_replicate"):
        key += f"-{spec['role']}"
    return key


def run_cell(spec: dict, cfg: dict, seed: int, L, P, pilot3, runner: JobRunner, instances_out: list,
             flat_out: list, log) -> dict:
    m, n, k = int(spec["m"]), int(spec["n"]), int(spec["k"])
    v_type, family = spec["v_type"], spec.get("family", "S3")
    role = spec.get("role", "primary")
    cell_key = cell_key_of(spec)
    cell_seed = int(spec.get("seed", seed))
    target_seed = int(spec.get("target_seed", cell_seed))
    reps = int(spec.get("replicates", 1))
    cap = cfg["solution_cap"]
    degrees = list(spec.get("closure_degrees", cfg["closure_degrees"]))
    arms = list(spec.get("arms", []))
    eliminators_cfg = spec.get("eliminators", ["m4ri", "independent"])
    N = (m - 2) * n + m * k if m >= 3 else 2 * k
    if comb_le(N, 5) <= cfg["w5_max_columns"] and 5 not in degrees and family != "M2CTRL":
        degrees.append(5)
    curves = pick_curves(L, n, spec.get("curves", cfg["curves"]))
    blocks = pilot3.blocks(n, k, m) if arms and m >= 3 else None
    summary = {"cell_key": cell_key, "cell": spec["cell"], "m": m, "n": n, "k": k, "v_type": v_type, "family": family,
               "role": role, "N": N, "columns_D4": comb_le(N, 4), "degrees": degrees, "arms": arms,
               "curves_used": [], "replicates": reps, "seed": cell_seed, "target_seed": target_seed,
               "n_instances": 0, "n_jobs": 0}
    rep_rows: list[list[dict]] = []
    for rep in range(reps):
        rows_this_rep: list[dict] = []
        for ci, cv in enumerate(curves):
            basis = [1 << j for j in range(k)] if v_type == "poly" else random_basis(n, k, cell_seed, ci)
            V = L.VSpace(cv["F"], basis)
            if rep == 0:
                summary["curves_used"].append({"curve_index": ci, "pick_seed": cv.get("pick_seed"), "b": cv["b"],
                                               "a": cv["a"], "order": cv["order"], "q": cv["q"],
                                               "modulus": cv["modulus"], "basis": basis})
            zs = L.subgroup_targets(cv, int(spec.get("max_targets_per_curve", cfg["max_targets_per_curve"])),
                                    target_seed)
            seen: set[int] = set()
            labelled: list[dict] = []
            for ti, z in enumerate(zs):
                dup = z in seen
                seen.add(z)
                if dup:
                    continue
                if family == "M2CTRL":
                    sysm, lab = label_m2(L, cv, V, basis, n, k, z, cap)
                else:
                    sysm, lab = label_s3(L, P, cv, V, basis, m, n, k, z, cap)
                if not lab["enum_agree"] or not lab["eval_ok"]:
                    log(f"ENUMERATOR DISAGREEMENT cell={cell_key} curve={ci} target={ti} z={z}: {lab}")
                iid = f"{cell_key}-c{ci}-S3-{ti:04d}" if family != "M2CTRL" else f"{cell_key}-c{ci}-M2-{ti:04d}"
                if rep:
                    iid += f"-rep{rep}"
                inst = {"instance_id": iid, "cell_key": cell_key, "cell": spec["cell"], "m": m, "n": n, "k": k,
                        "v_type": v_type, "family": "S3" if family in ("S3", "NULL", "NULL2") else family,
                        "role": role, "rep": rep, "curve_index": ci, "curve_b": cv["b"], "curve_a": cv["a"],
                        "modulus": cv["modulus"], "basis": basis, "z": z, "target_index": ti, "N": sysm["N"],
                        "neq": len(sysm["equations"]), "equations_sha256": eq_sha256(sysm["equations"]),
                        "label": "UNSAT" if lab["nsol"] == 0 else "SAT", **lab}
                if spec.get("pilot_id_prefix"):
                    inst["pilot_id"] = f"{spec['pilot_id_prefix']}{ti:04d}"
                labelled.append((inst, sysm))
            # selection of the source S3 (or M2) instances
            if family in ("S3", "M2CTRL"):
                want_unsat = int(spec.get("min_unsat_per_curve", cfg["min_unsat_per_curve"]))
                unsat = [x for x in labelled if x[0]["nsol"] == 0][:want_unsat]
                sat = [x for x in labelled if x[0]["nsol"] > 0]
                selected = unsat + sat
            elif family == "NULL":
                want = int(spec.get("min_unsat_null", cfg["min_unsat_null"]))
                selected, got = [], 0
                for src, sysm in labelled:
                    if got >= want:
                        break
                    nl = P.support_null(sysm, src["instance_id"].replace(f"-rep{rep}", ""))
                    cnt, bs = P.boolean_count_chain(nl)
                    ok = all(not any(L.eval_system(nl["equations"], s)) for s in bs)
                    inst = {**src, "instance_id": src["instance_id"].replace("-S3-", "-NULL-"), "family": "NULL",
                            "null_source": src["instance_id"], "null_seed": src["instance_id"].replace(f"-rep{rep}", ""),
                            "nsol": int(cnt), "nsol_boolean": int(cnt), "enum_agree": True, "eval_ok": bool(ok),
                            "point_check": [], "solutions": bs[:cap], "equations_sha256": eq_sha256(nl["equations"]),
                            "label": "UNSAT" if cnt == 0 else "SAT", "neq": len(nl["equations"])}
                    selected.append((inst, nl))
                    got += cnt == 0
            elif family == "NULL2":
                want = int(spec.get("min_labelled_dense", cfg["min_labelled_dense"]))
                selected = []
                for i, (src, sysm) in enumerate(labelled[:want]):
                    tag = f"{EXPERIMENT_ID}-{src['instance_id'].replace(f'-rep{rep}', '')}"
                    nl = P.dense_null(sysm, tag, i)
                    cnt, bs = count_dense(P, nl)
                    ok = all(not any(L.eval_system(nl["equations"], s)) for s in bs)
                    inst = {**src, "instance_id": src["instance_id"].replace("-S3-", "-NULL2-"), "family": "NULL2",
                            "null_source": src["instance_id"], "null_seed": tag, "null_draw": i,
                            "nsol": int(cnt), "nsol_boolean": int(cnt), "enum_agree": True, "eval_ok": bool(ok),
                            "point_check": [], "solutions": bs[:cap], "equations_sha256": eq_sha256(nl["equations"]),
                            "label": "UNSAT" if cnt == 0 else "SAT", "neq": len(nl["equations"])}
                    selected.append((inst, nl))
            else:
                raise ImplementationError(f"unknown family {family}")
            log(f"cell {cell_key} rep {rep} curve {ci} b={cv['b']}: labelled {len(labelled)} unique targets, "
                f"selected {len(selected)} ({sum(1 for x in selected if x[0]['nsol'] == 0)} UNSAT)")
            # closures
            for inst, sysm in selected:
                instances_out.append(inst)
                summary["n_instances"] += 1
                for D in degrees:
                    cols = comb_le(sysm["N"], D)
                    elims = []
                    if "m4ri" in eliminators_cfg and runner.m4ri and cols <= cfg["m4ri_max_columns"]:
                        elims.append("m4ri")
                    if "independent" in eliminators_cfg:
                        elims.append("independent")
                    if cols > cfg["independent_primary_above_columns"]:
                        elims = [e for e in elims if e == "independent"] + [e for e in elims if e != "independent"]
                    kinds = spec.get("kinds_by_degree", {}).get(str(D), ("M", "W") if D != 5 else ("W",))
                    for kind in kinds:
                        for el in elims:
                            row = runner.run(inst, sysm, kind, D, el, None)
                            summary["n_jobs"] += 1
                            fl = flatten(inst, row)
                            flat_out.append(fl)
                            rows_this_rep.append(fl)
                            log(f"  {inst['instance_id']} {kind}_{D} {el} {inst['label']} -> {row.get('status')} "
                                f"one={row.get('contains_one')} cols={row.get('ncols')} rank={row.get('rank')} "
                                f"wall={fl['wall_s']} rss={fl['peak_rss_mb']}")
                            if fl["label"] == "SAT" and fl["contains_one"]:
                                log(f"FALSE REFUTATION on {inst['instance_id']} {kind}_{D} {el}")
                for arm in arms:
                    if blocks is None:
                        continue
                    row = runner.run(inst, sysm, "W", 4, "independent", arm, blocks)
                    summary["n_jobs"] += 1
                    fl = flatten(inst, row)
                    flat_out.append(fl)
                    rows_this_rep.append(fl)
                    log(f"  {inst['instance_id']} {arm} {inst['label']} -> {row.get('status')} one={row.get('contains_one')} "
                        f"cols={row.get('ncols')} dropped={row.get('products_dropped')} wall={fl['wall_s']}")
        rep_rows.append(rows_this_rep)
    if reps > 1:
        def canon(rows):
            out = []
            for r in rows:
                r2 = {kk: v for kk, v in r.items() if kk not in DETERMINISM_EXCLUDED and kk != "rep"}
                r2["instance_id"] = r2["instance_id"].split("-rep")[0]
                out.append(r2)
            return canonical(out)
        digests = [sha256_text(canon(rows)) for rows in rep_rows]
        summary["c6"] = {"replicates": reps, "identical": len(set(digests)) == 1, "digests": digests,
                         "rows_compared": len(rep_rows[0]), "excluded_fields": DETERMINISM_EXCLUDED}
    return summary


# ----------------------------------------------------------------------------
# aggregation
# ----------------------------------------------------------------------------

def aggregate_cell(summary: dict, flat: list[dict]) -> dict:
    key = summary["cell_key"]
    rows = [r for r in flat if r["cell_key"] == key and r["rep"] == 0]
    s = dict(summary)
    w4 = [r for r in rows if r["closure_kind"] == "W" and r["D"] == 4]
    w4u = [r for r in w4 if r["label"] == "UNSAT" and not r["censored"] and r["status"] == "completed"]
    # primary eliminator per instance: independent above the threshold, else m4ri where it ran
    by_inst: dict[str, dict] = {}
    for r in w4u:
        prev = by_inst.get(r["instance_id"])
        if prev is None or (r["eliminator"] == "independent" and (r["cols"] or 0) > 50000) \
                or (prev["eliminator"] == "independent" and r["eliminator"] == "m4ri" and (r["cols"] or 0) <= 50000):
            by_inst[r["instance_id"]] = r
    refuted = sum(1 for r in by_inst.values() if r["contains_one"])
    total = len(by_inst)
    s["unsat_instances"] = len({r["instance_id"] for r in rows if r["label"] == "UNSAT"})
    s["sat_instances"] = len({r["instance_id"] for r in rows if r["label"] == "SAT"})
    s["unsat_w4_run"] = total
    s["unsat_w4_refuted"] = refuted
    s["r_4"] = (refuted / total) if total else None
    s["r_4_cp95"] = clopper_pearson(refuted, total)
    s["unsat_w4_censored"] = len({r["instance_id"] for r in w4 if r["label"] == "UNSAT" and r["censored"]}
                                 - set(by_inst))
    s["false_refutations"] = sum(1 for r in rows if r["label"] == "SAT" and r["contains_one"])
    s["m4_refutations"] = sum(1 for r in rows if r["closure_kind"] == "M" and r["D"] == 4 and r["label"] == "UNSAT"
                              and r["contains_one"])
    s["m3_w3_refutations"] = {"M_3": sum(1 for r in rows if r["closure_kind"] == "M" and r["D"] == 3
                                         and r["label"] == "UNSAT" and r["contains_one"]),
                              "W_3": sum(1 for r in rows if r["closure_kind"] == "W" and r["D"] == 3
                                         and r["label"] == "UNSAT" and r["contains_one"])}
    # D_W distribution: per UNSAT instance the minimal D among W_D runs with 1 in W_D
    dw: dict[str, int] = {}
    max_d_run: dict[str, int] = {}
    for r in rows:
        if r["label"] != "UNSAT" or r["closure_kind"] != "W":
            continue
        if r["status"] == "completed":
            max_d_run[r["instance_id"]] = max(max_d_run.get(r["instance_id"], 0), r["D"])
            if r["contains_one"]:
                dw[r["instance_id"]] = min(dw.get(r["instance_id"], 99), r["D"])
    dist: dict[str, int] = {}
    for iid in {r["instance_id"] for r in rows if r["label"] == "UNSAT"}:
        label = str(dw[iid]) if iid in dw else (f"not_refuted_at_max_D_{max_d_run[iid]}" if iid in max_d_run
                                                else "no_completed_W")
        dist[label] = dist.get(label, 0) + 1
    s["D_W_distribution"] = dict(sorted(dist.items()))
    s["not_refuted_unsat_instances"] = sorted(iid for iid in max_d_run if iid not in dw)
    # eliminator agreement
    pairs = agree = disagree = 0
    seen: dict[tuple, dict] = {}
    for r in rows:
        if r["status"] != "completed" or r["closure_kind"] not in ("M", "W"):
            continue
        kk = (r["instance_id"], r["closure_kind"], r["D"])
        if kk in seen:
            other = seen[kk]
            pairs += 1
            if other["contains_one"] == r["contains_one"] and (other["contains_one"] or other["rank"] == r["rank"]):
                agree += 1
            else:
                disagree += 1
        else:
            seen[kk] = r
    s["eliminator_pairs"] = pairs
    s["eliminator_agreements"] = agree
    s["eliminator_disagreements"] = disagree
    s["elimination_faults"] = sum(int(r["elimination_faults"] or 0) for r in rows)
    s["evalcheck_mismatches"] = sum(int(r["evalcheck_mismatch"] or 0) for r in rows if r["label"] == "SAT")
    sat_w4 = [r for r in rows if r["label"] == "SAT" and r["closure_kind"] == "W" and r["D"] == 4
              and r["status"] == "completed"]
    s["sat_w4_codim_checked"] = len(sat_w4)
    s["sat_w4_codim_equals_nsol"] = sum(1 for r in sat_w4 if r["codim"] == r["nsol"])
    s["censored_jobs"] = sum(1 for r in rows if r["censored"])
    s["censored_job_list"] = [{"instance_id": r["instance_id"], "closure_kind": r["closure_kind"], "D": r["D"],
                               "eliminator": r["eliminator"], "status": r["status"], "wall_s": r["wall_s"],
                               "peak_rss_mb": r["peak_rss_mb"], "columns": comb_le(r["N"], r["D"])}
                              for r in rows if r["censored"]]
    s["worker_errors"] = sum(1 for r in rows if not r["censored"] and r["status"] != "completed")
    for arm in summary.get("arms", []):
        a = [r for r in rows if r["closure_kind"] == arm and r["status"] == "completed"]
        au = [r for r in a if r["label"] == "UNSAT"]
        ar = sum(1 for r in au if r["contains_one"])
        full = {r["instance_id"]: r for r in by_inst.values()}
        both = [r for r in au if r["instance_id"] in full]
        s[f"arm_{arm}"] = {"unsat_run": len(au), "unsat_refuted": ar, "r_4": (ar / len(au)) if au else None,
                           "r_4_cp95": clopper_pearson(ar, len(au)),
                           "false_refutations": sum(1 for r in a if r["label"] == "SAT" and r["contains_one"]),
                           "median_cols": sorted(r["cols"] for r in a)[len(a) // 2] if a else None,
                           "full_w4_median_cols": sorted(full[r["instance_id"]]["cols"] for r in both)[len(both) // 2]
                           if both else None,
                           "same_instances_full_w4_refuted": sum(1 for r in both if full[r["instance_id"]]["contains_one"]),
                           "same_instances_arm_refuted": sum(1 for r in both if r["contains_one"]),
                           "same_instances": len(both),
                           "censored": sum(1 for r in rows if r["closure_kind"] == arm and r["censored"])}
    if summary.get("role") == "c1_pilot_gate":
        s["c1"] = {"w4_unsat_refuted": f"{refuted}/{total}", "false_refutations": f"{s['false_refutations']}/"
                   f"{len({r['instance_id'] for r in rows if r['label'] == 'SAT'})}",
                   "pass": (refuted == total == 60 and s["false_refutations"] == 0
                            and len({r['instance_id'] for r in rows if r['label'] == 'SAT'}) == 8)}
    return s


def write_yaml(obj, indent=0) -> str:
    """Tiny block-YAML writer for the manifest (strings quoted; no yaml dependency)."""
    pad = "  " * indent
    lines = []
    if isinstance(obj, dict):
        if not obj:
            return pad + "{}\n"
        for kk, v in obj.items():
            if isinstance(v, (dict, list)) and v:
                lines.append(f"{pad}{kk}:\n{write_yaml(v, indent + 1)}")
            else:
                lines.append(f"{pad}{kk}: {scalar(v)}\n")
        return "".join(lines)
    if isinstance(obj, list):
        if not obj:
            return pad + "[]\n"
        for v in obj:
            if isinstance(v, (dict, list)) and v:
                body = write_yaml(v, indent + 1)
                first, rest = body.split("\n", 1)
                lines.append(f"{pad}- {first.strip()}\n{rest}" if rest else f"{pad}- {first.strip()}\n")
            else:
                lines.append(f"{pad}- {scalar(v)}\n")
        return "".join(lines)
    return pad + scalar(obj) + "\n"


def scalar(v) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, (dict, list)):
        return json.dumps(v)
    return json.dumps(str(v))


def git_commit(repo: Path) -> tuple[str, bool]:
    try:
        c = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True, timeout=30)
        d = subprocess.run(["git", "-C", str(repo), "status", "--porcelain", "--untracked-files=no"],
                           capture_output=True, text=True, timeout=60)
        if c.returncode == 0 and len(c.stdout.strip()) == 40:
            return c.stdout.strip(), bool(d.stdout.strip())
    except (OSError, subprocess.SubprocessError):
        pass
    try:
        head = (repo / ".git" / "HEAD").read_text().strip()
        if head.startswith("ref: "):
            ref = repo / ".git" / head[5:]
            if ref.is_file():
                return ref.read_text().strip(), False
            packed = repo / ".git" / "packed-refs"
            if packed.is_file():
                for line in packed.read_text().splitlines():
                    if line.endswith(" " + head[5:]):
                        return line.split()[0], False
        elif len(head) == 40:
            return head, False
    except OSError:
        pass
    return "unknown", False


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--trial-id", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--plan", required=True)
    args = ap.parse_args()
    run_dir = Path(args.run_dir).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    started = now_iso()
    t_start = time.time()
    def log(msg):
        print(f"[{now_iso()}] {msg}", flush=True)

    plan_path = Path(args.plan)
    plan_bytes = plan_path.read_bytes()
    plan = json.loads(plan_bytes)
    plan_sha = hashlib.sha256(plan_bytes).hexdigest()
    repo = plan_path.resolve().parents[2]
    status, invalid_reason, exit_code = "completed_valid", None, 0
    manifest_written = False
    bdir = None
    try:
        trial = next((t for t in plan["trials"] if t["id"] == args.trial_id), None)
        if trial is None:
            raise ImplementationError(f"trial {args.trial_id} not in plan")
        if trial["run_id"] != args.run_id:
            raise ImplementationError(f"run id {args.run_id} does not match the plan's {trial['run_id']}")
        if plan.get("experiment_id") != EXPERIMENT_ID:
            raise ImplementationError("plan experiment_id mismatch")
        cfg = {**DEFAULTS, **(plan.get("defaults") or {}), **(trial.get("overrides") or {})}
        cells = trial["cells"]
        bdir, binfo = build(run_dir)
        log(f"build ok m4ri_available={binfo['m4ri_available']} ({binfo['libm4ri_dev_package']})")
        L, P, pilot3 = load_libs(bdir)
        import numpy  # noqa: PLC0415
        env = {"host": platform.node(), "platform": platform.platform(), "machine": platform.machine(),
               "python": sys.version.split()[0], "numpy": numpy.__version__, "cpu_count": os.cpu_count(),
               "compiler": binfo["compiler"], "libm4ri_dev_package": binfo["libm4ri_dev_package"],
               "m4ri_available": binfo["m4ri_available"], "m4ri_library": None, "cflags": binfo["cflags"],
               "build_sha256": binfo["sha256"], "rlimit_as": list(resource.getrlimit(resource.RLIMIT_AS)),
               "job_rss_cap_gb": cfg["job_rss_cap_gb"], "job_wall_cap_s": cfg["job_wall_cap_s"],
               "started_at": started}
        if binfo["m4ri_available"]:
            import ctypes  # noqa: PLC0415
            lib = ctypes.CDLL(str(bdir / "vendor" / "libclosure.so"))
            lib.closure_m4ri_library.restype = ctypes.c_char_p
            lib.closure_elimination.restype = ctypes.c_char_p
            env["m4ri_library"] = lib.closure_m4ri_library().decode()
            env["m4ri_elimination"] = lib.closure_elimination().decode()
        if not (run_dir / "environment.json").exists():  # under the supervisor that file is its own record
            (run_dir / "environment.json").write_text(json.dumps(env, indent=1, sort_keys=True) + "\n")
        results_path = run_dir / "results.jsonl"
        if results_path.exists():
            results_path.unlink()
        runner = JobRunner(bdir, run_dir, cfg, binfo["m4ri_available"], results_path)
        instances: list[dict] = []
        flat: list[dict] = []
        summaries = []
        for spec in cells:
            log(f"=== cell {cell_key_of(spec)} ===")
            summaries.append(run_cell(spec, cfg, args.seed, L, P, pilot3, runner, instances, flat, log))
        runner.close()
        cells_out = [aggregate_cell(s, flat) for s in summaries]
        inst_rows = [{f: r[f] for f in INSTANCE_FIELDS} | {kk: r[kk] for kk in ("status", "cell_key", "rep",
                                                                                 "curve_index", "z", "N")}
                     for r in flat]
        canon_rows = [{kk: v for kk, v in r.items() if kk not in DETERMINISM_EXCLUDED} for r in inst_rows]
        enum_disagree = sum(1 for i in instances if not i["enum_agree"] or not i["eval_ok"])
        summary = {
            "false_refutations": sum(c["false_refutations"] for c in cells_out),
            "m4_refutations": sum(c["m4_refutations"] for c in cells_out),
            "eliminator_pairs": sum(c["eliminator_pairs"] for c in cells_out),
            "eliminator_disagreements": sum(c["eliminator_disagreements"] for c in cells_out),
            "elimination_faults": sum(c["elimination_faults"] for c in cells_out),
            "evalcheck_mismatches": sum(c["evalcheck_mismatches"] for c in cells_out),
            "enumerator_disagreements": enum_disagree,
            "point_check_failures": sum(1 for i in instances for v in i.get("point_check", []) if not v),
            "censored_jobs": sum(c["censored_jobs"] for c in cells_out),
            "worker_errors": sum(c["worker_errors"] for c in cells_out),
            "jobs": len(flat), "instances": len(instances),
            "r4_by_cell": {c["cell_key"]: c["r_4"] for c in cells_out},
            "r4_cp95_by_cell": {c["cell_key"]: c["r_4_cp95"] for c in cells_out},
            "unsat_w4_run_by_cell": {c["cell_key"]: c["unsat_w4_run"] for c in cells_out},
            "c1": next((c["c1"] for c in cells_out if "c1" in c), None),
            "c6": next((c["c6"] for c in cells_out if "c6" in c), None),
            "sat_w4_codim_mismatches": sum(c["sat_w4_codim_checked"] - c["sat_w4_codim_equals_nsol"] for c in cells_out),
            "m4ri_available": binfo["m4ri_available"],
            "c5_eliminator_crosscheck": "run" if binfo["m4ri_available"] else "not_run_libm4ri_absent",
        }
        reasons = []
        if summary["false_refutations"]:
            reasons.append(f"{summary['false_refutations']} false refutation(s)")
        if summary["eliminator_disagreements"] or summary["elimination_faults"]:
            reasons.append("eliminator disagreement or elimination fault")
        if summary["enumerator_disagreements"]:
            reasons.append("enumerator disagreement")
        if summary["evalcheck_mismatches"]:
            reasons.append("evaluation-check mismatch")
        if summary["c1"] is not None and not summary["c1"]["pass"]:
            reasons.append("C1 pilot gate failed")
        if summary["c6"] is not None and not summary["c6"]["identical"]:
            reasons.append("C6 determinism replicate differs")
        if summary["sat_w4_codim_mismatches"]:
            reasons.append("codim(W_4) != nsol on a SAT instance")
        if summary["worker_errors"]:
            reasons.append(f"{summary['worker_errors']} worker error(s)")
        if reasons:
            status, invalid_reason = "completed_invalid", "; ".join(reasons)
        finished = now_iso()
        result = {
            "schema": SCHEMA, "experiment_id": EXPERIMENT_ID, "hypothesis_id": HYPOTHESIS_ID,
            "trial_id": args.trial_id, "run_id": args.run_id, "seed": args.seed, "plan_sha256": plan_sha,
            "config": cfg, "environment": env, "cells": cells_out, "instances": inst_rows,
            "instances_canonical_sha256": sha256_text(canonical(canon_rows)),
            "determinism_excluded_fields": DETERMINISM_EXCLUDED,
            "summary": summary,
            "definitions": {
                "r_4": "UNSAT instances with 1 in W_4 (primary eliminator: independent above 50,000 columns, else "
                       "M4RI where it ran) / UNSAT instances whose W_4 completed; censored jobs excluded",
                "ops_proxy": "M4RI: sum over closure iterations of rows x cols; independent eliminator: rows (products "
                             "inserted) x cols, one iteration",
                "evalcheck_mismatch": "M4RI: rows not vanishing at a known zero before/after an elimination "
                                      "(-DECH_EVALCHECK); both: basis rows not vanishing at a known solution",
                "eliminator_agreement": "same contains_one; same rank where contains_one is false (both eliminators "
                                        "stop as soon as 1 enters, so the rank at refutation is not canonical)",
                "censored": "job exceeded the per-job RSS cap, the closure memory cap or the per-job wall cap; "
                            "never a result",
            },
            "status": status, "invalid_reason": invalid_reason,
            "started_at": started, "finished_at": finished, "elapsed_seconds": round(time.time() - t_start, 3),
        }
        (run_dir / "raw-result.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
        (run_dir / "instances.json").write_text(json.dumps(
            {"schema": "sembin.closure_degree.instances.v1", "run_id": args.run_id, "trial_id": args.trial_id,
             "seed": args.seed, "solution_cap": cfg["solution_cap"], "instances": instances},
            indent=None, sort_keys=True, separators=(",", ":")) + "\n")
        log(f"done: {len(flat)} jobs, {len(instances)} instances, status {status}")
    except Exception as exc:  # noqa: BLE001
        status, invalid_reason, exit_code = "failed_implementation", f"{type(exc).__name__}: {exc}", 3
        log(f"IMPLEMENTATION ERROR: {invalid_reason}")
        import traceback  # noqa: PLC0415
        print(traceback.format_exc(), file=sys.stderr, flush=True)
    finally:
        try:
            commit, dirty = git_commit(repo)
            code_sha = {}
            for p in sorted(IMPL.rglob("*")):
                if p.is_file() and p.suffix in (".py", ".c", ".sh") and "__pycache__" not in p.parts:
                    code_sha[p.relative_to(IMPL).as_posix()] = sha256_file(p)
            ru = resource.getrusage(resource.RUSAGE_CHILDREN)
            ru_self = resource.getrusage(resource.RUSAGE_SELF)
            artifacts = [n for n in ("raw-result.json", "results.jsonl", "instances.json") if (run_dir / n).exists()]
            manifest = {"run": {
                "id": args.run_id, "experiment_id": EXPERIMENT_ID, "hypothesis_id": HYPOTHESIS_ID,
                "task_id": plan.get("task_id"), "trial_id": args.trial_id, "role": "executor",
                "recorded_at": started[:10], "status": status,
                "validity": {"status": status, "reason": invalid_reason or "run.py recorded no invalidation; "
                             "check.py and independent review decide validity", "failure_class": None},
                "code": {"commit": commit, "dirty": dirty, "branch": None,
                         "command": " ".join([sys.executable, *sys.argv]),
                         "code_sha256": code_sha, "trial_plan_sha256": plan_sha,
                         "working_directory": os.getcwd()},
                "environment": {"host": platform.node(), "operating_system": platform.platform(),
                                "python_version": sys.version.split()[0], "processor_count": os.cpu_count(),
                                "source": "raw-result.json /environment"},
                "inputs": {"curve_id": None, "seed": args.seed,
                           "parameters": {"trial_id": args.trial_id, "plan": str(plan_path),
                                          "cells": [cell_key_of(c) for c in (trial or {}).get("cells", [])]
                                          if exit_code == 0 else []}},
                "timing": {"started_at": started, "finished_at": now_iso(),
                           "wall_seconds": round(time.time() - t_start, 3)},
                "resources": {"peak_rss_bytes": int(max(ru.ru_maxrss, ru_self.ru_maxrss) * 1024),
                              "cpu_seconds": round(ru.ru_utime + ru.ru_stime + ru_self.ru_utime + ru_self.ru_stime, 3)},
                "result": {"metrics": {"raw_result": "raw-result.json"} if exit_code == 0 else {},
                           "valid": status == "completed_valid", "invalid_reason": invalid_reason,
                           "raw_result": "raw-result.json" if exit_code == 0 else None,
                           "certificate": {"kind": "none", "verified": True, "verifier": "no-claim",
                                           "note": "degree measurement on toy synthetic systems; no discrete "
                                                   "logarithm, no relation and no speedup is claimed"}},
                "artifacts": artifacts,
            }}
            (run_dir / "manifest.yaml").write_text(write_yaml(manifest))
            manifest_written = True
        finally:
            if bdir is not None and bdir.exists():
                shutil.rmtree(bdir, ignore_errors=True)
    return exit_code if manifest_written else 3


if __name__ == "__main__":
    raise SystemExit(main())
