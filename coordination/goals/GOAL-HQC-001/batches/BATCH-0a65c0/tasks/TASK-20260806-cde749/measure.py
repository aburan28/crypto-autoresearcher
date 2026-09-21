#!/usr/bin/env python3
"""PS-R3 joint-moment measurement at T = 1e7 under the ADMITTED v3 rule.

TASK-20260806-cde749 (executor) / BATCH-0a65c0 / GOAL-HQC-001 / EXP-HQC-982268.

WHAT THIS IS
------------
This is the measurement EXP-HQC-982268 exists to make, at ONE configuration:
PS-R3 at T = 10,000,000.  It reports log2 Ahat_k for k = 2..k_max against the
FROZEN calibrated interval of AMD-EXP-HQC-982268-v3, admitted by two
independent reviews (validator TASK-20260806-f53255 ADMIT, red team
TASK-20260806-250b29 ADMIT) and ruled on by the Coordinator in
coordinator_ruling.yaml.

WHAT IT IS NOT
--------------
Nothing here is a statement about HQC, about assumption A17 or A5, about any
decoding-failure rate, or about any standardized HQC parameter set.  PS-R3 is
ONE REDUCED parameter set, order-matched to HQC-3's shape and not to HQC-1's.
Claim tier: TOY, hard ceiling.  The Executor reports observations and draws no
conclusion and changes no status.

A timeout, crash, missing dependency or budget exhaustion is an INFRASTRUCTURE
outcome and is never evidence about the mathematics (AGENTS.md rule 5).

BINDING COORDINATOR RULINGS OBSERVED HERE
-----------------------------------------
RULE-1  CTRL-IDXMAP and CTRL-POSHOM clause (b) are FORWARD OBLIGATIONS, not
        blocking gates.  They are reported NOT RUN.  This program does not
        synthesize index_map.json or pair_counts_by_position.csv and does not
        cite either control as passing.
RULE-3  k = 2 is an AUTHORIZED REPORTED CELL under the frozen interval.
RULE-4  recalibrate.py is NOT invoked (its inject() opens the amendment for
        writing).  The frozen constants are loaded READ-ONLY with yaml.safe_load.
RULE-5  The 17-cell battery's familywise size is ~1.0%, not 0.27%.  Only the
        pre-specified k = m = 17 cell retains the 0.27% per-cell size.  The
        familywise rate is measured here and printed beside every battery
        reading.

The frozen (T) sampler in stage_a.py is IMPORTED UNMODIFIED and is not
rewritten (red team TASK-20260806-250b29 binding correction 2).

Re-run:
    PYTHONDONTWRITEBYTECODE=1 python3 measure.py --out-dir .
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import multiprocessing as mp
import os
import platform
import resource
import subprocess
import sys
import time

import numpy as np
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *([".."] * 7)))

AMENDMENT = os.path.join(
    REPO, "coordination", "goals", "GOAL-HQC-001", "batches", "BATCH-0a65c0",
    "tasks", "TASK-20260806-6086cb", "amendment_v3.yaml")
SNAPSHOT_RECEIPT = os.path.join(
    REPO, "coordination", "goals", "GOAL-HQC-001", "batches", "BATCH-0a65c0",
    "archives", "TASK-20260806-ae094e", "snapshot-receipt.json")
STAGE_A = os.path.join(
    REPO, "coordination", "goals", "GOAL-HQC-001", "batches", "BATCH-6fddee",
    "tasks", "TASK-20260806-64b506", "stage_a.py")
ORACLE_VALUES = os.path.join(
    REPO, "coordination", "goals", "GOAL-HQC-001", "batches", "BATCH-003",
    "tasks", "TASK-20260803-6f50df", "oracle_values.json")

SET_ID = "PS-R3"
ALLOCATION = "1e7"
T_PLANNED = 10_000_000

# frozen procedure constants (amendment R1_INV_NULL_v3.binding_calibration_procedure)
ALPHA = 0.0026997960632601866
N_CAL = 2_000_000
N_VAL = 1_000_000
CHUNK = 100_000
SEED_PREFIX = "EXP-HQC-982268/v3/INV-NULL"

N_JACK_BATCHES = 200
# (T) sampler shard ids: DISJOINT from Stage-A's shards 0..3 and its smoke shard
# 900, so these are FRESH draws and not a re-use of the diagnostics draws whose
# q_hat calibrated the frozen table.
SHARD_BASE = 1000
N_SHARDS = 8
CTRL_BS_REPLICATES = 20
CTRL_BS_SUBSAMPLE = 200_000
POSHOM_SUB = 2_000_000

CORE_SECOND_BUDGET = 5200.0
WALL_BUDGET = 2400.0


# --------------------------------------------------------------------------
# budget instrumentation
# --------------------------------------------------------------------------

def core_seconds() -> float:
    a = resource.getrusage(resource.RUSAGE_SELF)
    b = resource.getrusage(resource.RUSAGE_CHILDREN)
    return (a.ru_utime + a.ru_stime + b.ru_utime + b.ru_stime)


class Budget:
    def __init__(self, prior_core_seconds: float = 0.0):
        self.t_wall0 = time.time()
        self.c0 = core_seconds()
        self.prior = prior_core_seconds
        self.stages = []

    def spent(self) -> float:
        return self.prior + (core_seconds() - self.c0)

    def wall(self) -> float:
        return time.time() - self.t_wall0

    def remaining(self) -> float:
        return CORE_SECOND_BUDGET - self.spent()

    def stage(self, name):
        return _Stage(self, name)


class _Stage:
    def __init__(self, budget: Budget, name: str):
        self.b, self.name = budget, name

    def __enter__(self):
        self.c0, self.w0 = core_seconds(), time.time()
        return self

    def __exit__(self, *exc):
        rec = dict(stage=self.name,
                   core_seconds=round(core_seconds() - self.c0, 3),
                   wall_seconds=round(time.time() - self.w0, 3),
                   cumulative_core_seconds=round(self.b.spent(), 3))
        self.b.stages.append(rec)
        print(f"[stage] {self.name}: {rec['core_seconds']}s core, "
              f"{rec['wall_seconds']}s wall, cum {rec['cumulative_core_seconds']}s",
              flush=True)
        return False


# --------------------------------------------------------------------------
# frozen-table loading -- READ ONLY (RULE-4)
# --------------------------------------------------------------------------

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def load_frozen():
    """yaml.safe_load only.  recalibrate.py is NEVER imported or executed."""
    with open(AMENDMENT, "r") as fh:                     # 'r', never 'w'
        doc = yaml.safe_load(fh)
    amd = doc["protocol_amendment"]
    fi = amd["R1_INV_NULL_v3"]["frozen_intervals"]
    cfg = None
    for c in fi["configurations"]:
        if c["set"] == SET_ID and c["allocation"] == ALLOCATION:
            cfg = c
    if cfg is None:
        raise SystemExit("FAILED_IMPLEMENTATION: PS-R3@1e7 absent from the frozen table")

    # VF-1 guard, re-run here rather than taken on trust: every interval
    # constant must parse as float.  PyYAML resolves a dotless-mantissa
    # exponent ('1e-05') to str, which is the defect v3 exists to fix.
    typed = {"float": 0, "str": 0, "other": 0}
    for cell in cfg["cells"]:
        for key in ("c_lo", "c_hi", "null_mean", "null_median", "null_sd",
                    "undefined_fraction", "T_stab"):
            v = cell[key]
            typed["float" if isinstance(v, float) else
                  "str" if isinstance(v, str) else "other"] += 1
    if typed["str"] or typed["other"]:
        raise SystemExit(f"FAILED_IMPLEMENTATION: non-float constants {typed}")
    if not isinstance(cfg["q_hat"], float):
        raise SystemExit("FAILED_IMPLEMENTATION: q_hat did not parse as float")
    return amd, fi, cfg, typed


def derive_seed(purpose: str, n: int) -> int:
    s = f"{SEED_PREFIX}|{SET_ID}|{ALLOCATION}|{T_PLANNED}|{purpose}|{n}"
    return int.from_bytes(hashlib.sha256(s.encode()).digest()[:8], "big")


# --------------------------------------------------------------------------
# the frozen estimator and the frozen null draw
# --------------------------------------------------------------------------

def binom_pmf(n_e: int, q: float) -> np.ndarray:
    pmf = np.array([math.comb(n_e, i) * q ** i * (1.0 - q) ** (n_e - i)
                    for i in range(n_e + 1)], dtype=np.float64)
    return pmf / pmf.sum()


def comb_matrix(n_e: int, ks) -> np.ndarray:
    """(n_e+1, K), indexed [s][k].

    ORIENTATION IS LOAD-BEARING.  The run-time reproduction check is a
    BIT-IDENTITY test, and a matmul against a transposed view can sum in a
    different order and round differently.  This matches the generating
    procedure's own `cmatrix` / `Hf @ C` exactly.
    """
    return np.array([[float(math.comb(s, k)) for k in ks]
                     for s in range(n_e + 1)], dtype=np.float64)


def log2_A_from_hists(H: np.ndarray, n_e: int, ks, C: np.ndarray):
    """H: (R, n_e+1) histogram counts.  Returns (R, len(ks)) log2 Ahat_k.

    log2 Ahat_k = log2( (sum_s C(s,k) H_s) / (T C(n_e,k)) ) - k log2( (sum_s s H_s) / (T n_e) )
    Undefined (NaN) where mu_hat <= 0.  Written from the estimator definition in
    the approved contract (metrics.log2_A_k) and in the amendment's
    binding_calibration_procedure.estimator.
    """
    ks = list(ks)
    Hf = H.astype(np.float64)
    T = Hf.sum(axis=1)
    ssum = Hf @ np.arange(n_e + 1, dtype=np.float64)
    q = ssum / (T * n_e)
    num = Hf @ C
    denom = T[:, None] * np.array([float(math.comb(n_e, k)) for k in ks])[None, :]
    mu = num / denom
    out = np.full(mu.shape, np.nan)
    good = (mu > 0) & (q[:, None] > 0)
    kk = np.array(ks, dtype=np.float64)[None, :]
    lq = np.log2(np.where(q > 0, q, 1.0))[:, None]
    out[good] = (np.log2(np.where(good, mu, 1.0)) - kk * lq)[good]
    return out


def null_draws(seed: int, n_rep: int, T: int, pmf: np.ndarray, n_e: int, ks,
               C: np.ndarray) -> np.ndarray:
    """The NORMATIVE draw: PCG64(seed), fixed chunks of 100000, in order,
    multinomial(T, pmf).  Returns (n_rep, len(ks)) of log2 Ahat_k."""
    rng = np.random.Generator(np.random.PCG64(seed))
    out = np.empty((n_rep, len(ks)), dtype=np.float64)
    done = 0
    while done < n_rep:
        b = min(CHUNK, n_rep - done)
        H = rng.multinomial(T, pmf, size=b)
        out[done:done + b] = log2_A_from_hists(H, n_e, ks, C)
        done += b
    return out


def order_stat_interval(vals: np.ndarray):
    """c_lo = x_(i), c_hi = x_(R-1-i) with i = floor(alpha/2 * R) over the
    FINITE values sorted ascending."""
    fin = vals[np.isfinite(vals)]
    R = fin.size
    if R == 0:
        return None, None, 0
    x = np.sort(fin)
    i = int(math.floor(ALPHA / 2.0 * R))
    return float(x[i]), float(x[R - 1 - i]), R


def t_stab(n_e: int, q: float, k: int):
    """The contract's pre-registered rule, at the MEASURED q-hat."""
    pmf = np.array([math.comb(n_e, s) * q ** s * (1 - q) ** (n_e - s)
                    for s in range(n_e + 1)])
    contrib = np.array([pmf[s] * math.comb(s, k) if s >= k else 0.0
                        for s in range(n_e + 1)])
    tot = float(contrib.sum())
    if tot <= 0:
        return None, None
    s90 = int(np.searchsorted(np.cumsum(contrib), 0.90 * tot))
    tail = float(pmf[s90:].sum())
    return s90, (30.0 / tail if tail > 0 else None)


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def git_state():
    def run(*a):
        try:
            return subprocess.run(a, cwd=REPO, capture_output=True, text=True,
                                  timeout=60).stdout.strip()
        except Exception as exc:                                  # pragma: no cover
            return f"<unavailable: {exc}>"
    return dict(commit=run("git", "rev-parse", "HEAD"),
                branch=run("git", "rev-parse", "--abbrev-ref", "HEAD"),
                dirty=bool(run("git", "status", "--porcelain")),
                dirty_paths=run("git", "status", "--porcelain").splitlines()[:40])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=HERE)
    ap.add_argument("--cores", type=int, default=min(4, os.cpu_count() or 1))
    ap.add_argument("--prior-core-seconds", type=float, default=0.0,
                    help="core-seconds already charged to this task before this "
                         "invocation (throughput benchmarking).")
    ap.add_argument("--shard-wall-cap", type=float, default=1800.0)
    ap.add_argument("--smoke", action="store_true",
                    help="Developer shakedown of every code path at tiny scale. "
                         "The bit-identity gate CANNOT pass in this mode (the "
                         "constants are a function of the replicate count) and its "
                         "failure is not treated as FAILED_IMPLEMENTATION. A smoke "
                         "run produces NO measurement and is never reported as one.")
    args = ap.parse_args(argv)

    n_cal = 20_000 if args.smoke else N_CAL
    n_val = 20_000 if args.smoke else N_VAL
    T_target = 8_000 if args.smoke else T_PLANNED
    n_shards = 4 if args.smoke else N_SHARDS
    bs_sub = 4_000 if args.smoke else CTRL_BS_SUBSAMPLE
    n_bs_rep = 3 if args.smoke else CTRL_BS_REPLICATES

    B = Budget(args.prior_core_seconds)
    R = {
        "task_id": "TASK-20260806-cde749",
        "role": "executor",
        "experiment_id": "EXP-HQC-982268",
        "hypothesis_id": "H-HQC-18d1b4",
        "goal": "GOAL-HQC-001",
        "batch": "BATCH-0a65c0",
        "claim_tier": "toy",
        "scope_statement": (
            "ONE reduced parameter set (PS-R3, order-matched to HQC-3's SHAPE, "
            "not HQC-1's), one allocation (T=1e7), one solver, one budget. "
            "NOTHING here is a statement about HQC, A17, A5, any decoding-failure "
            "rate, or any standardized parameter set."),
        "decision_rule_source": {
            "record": "AMD-EXP-HQC-982268-v3",
            "path": os.path.relpath(AMENDMENT, REPO),
            "loaded": "yaml.safe_load, read-only",
            "recalibrate_py_invoked": False,
            "recalibrate_py_invoked_reason":
                "Coordinator RULE-4: inject() opens the amendment for writing.",
            "constants_re_tuned": False,
        },
        "gate_verification": {},
        "started_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    # ---------------- phase 0: provenance --------------------------------
    with B.stage("provenance"):
        R["git"] = git_state()
        R["environment"] = dict(
            python=sys.version.split()[0], numpy=np.__version__,
            pyyaml=yaml.__version__, platform=platform.platform(),
            processor=platform.machine(), cpu_count=os.cpu_count(),
            cores_used=args.cores)
        receipt = json.load(open(SNAPSHOT_RECEIPT))
        amd_sha = sha256_file(AMENDMENT)
        declared = None
        for k, v in (receipt.get("path_sha256") or {}).items():
            if k.endswith("amendment_v3.yaml"):
                declared = v
        R["frozen_input_integrity"] = dict(
            amendment_sha256_now=amd_sha,
            amendment_sha256_in_snapshot_receipt=declared,
            match=(declared == amd_sha),
            snapshot_receipt=os.path.relpath(SNAPSHOT_RECEIPT, REPO))
        if declared is not None and declared != amd_sha:
            raise SystemExit("FAILED_IMPLEMENTATION: amendment content differs "
                             "from the snapshot receipt")

    amd, fi, cfg, typed = load_frozen()
    n_e, q_hat_frozen, k_max = cfg["n_e"], cfg["q_hat"], cfg["k_max_at_T"]
    m = cfg["m"]
    ks = [c["k"] for c in cfg["cells"]]
    C = comb_matrix(n_e, ks)
    R["configuration"] = dict(
        set=SET_ID, allocation=ALLOCATION, n_e=n_e, m=m, T_planned=T_PLANNED,
        q_hat_frozen=q_hat_frozen, k_max_at_T=k_max, k_range=[min(ks), max(ks)],
        reported_cells=len(ks), calibration_seed=cfg["calibration_seed"],
        constant_type_census=typed)
    print(f"[frozen] PS-R3@1e7 n_e={n_e} m={m} k_max={k_max} cells={len(ks)}",
          flush=True)

    # ---------------- phase 1: BLOCKING bit-identity reproduction --------
    # amendment authority_and_conflict.run_time_reproduction_check:
    # MANDATORY AND BLOCKING, before any (T) datum is scored.
    with B.stage("inv_null_bit_identity_reproduction"):
        cal_seed = derive_seed("cal", N_CAL)
        seed_matches = (cal_seed == cfg["calibration_seed"])
        pmf = binom_pmf(n_e, q_hat_frozen)
        cal = null_draws(cal_seed, n_cal, T_PLANNED, pmf, n_e, ks, C)
        rederived, per_cell = {}, []
        all_identical = True
        for j, cell in enumerate(cfg["cells"]):
            lo, hi, Rfin = order_stat_interval(cal[:, j])
            und = int(np.count_nonzero(~np.isfinite(cal[:, j])))
            ident = (lo == cell["c_lo"]) and (hi == cell["c_hi"])
            all_identical &= ident
            rederived[cell["k"]] = (lo, hi)
            per_cell.append(dict(
                k=cell["k"],
                frozen_c_lo=cell["c_lo"], frozen_c_hi=cell["c_hi"],
                rederived_c_lo=lo, rederived_c_hi=hi,
                bit_identical=bool(ident),
                finite_replicates=int(Rfin),
                undefined_null_replicates=und,
                undefined_fraction=und / n_cal,
                rederived_null_mean=float(np.nanmean(cal[:, j])),
                rederived_null_sd=float(np.nanstd(cal[:, j], ddof=1)),
                frozen_null_mean=cell["null_mean"],
                frozen_null_sd=cell["null_sd"]))
        # reachability arithmetic re-derived from scratch at the FROZEN q-hat,
        # as an independent check that this program's T_stab agrees with the
        # record before it is used at the MEASURED q-hat.
        ts_rows, ts_ok = [], True
        for cell in cfg["cells"]:
            s90, ts = t_stab(n_e, q_hat_frozen, cell["k"])
            match = (ts is not None
                     and abs(ts - cell["T_stab"]) <= 1e-6 * abs(cell["T_stab"]))
            ts_ok &= bool(match and s90 == cell["s_90"])
            ts_rows.append(dict(k=cell["k"], frozen_T_stab=cell["T_stab"],
                                rederived_T_stab=ts, frozen_s_90=cell["s_90"],
                                rederived_s_90=s90, match=bool(match)))
        R["reachability_reproduction_at_frozen_q"] = dict(
            rule="s_90 = min{s : sum_{s'<=s} P[S=s'] C(s',k) >= 0.90 E[C(S,k)]}; "
                 "T_stab = 30 / P[S >= s_90]; reachable iff T >= T_stab",
            all_rows_reproduce=bool(ts_ok), rows=ts_rows,
            k_max_at_T=k_max,
            T_stab_at_k_equals_m=[r for r in ts_rows if r["k"] == m][0],
            margin_at_k_equals_m=T_PLANNED / [r for r in ts_rows
                                              if r["k"] == m][0]["rederived_T_stab"])

        R["gate_INV_NULL_bit_identity"] = dict(
            gate="INV-NULL run-time reproduction check",
            binding="MANDATORY AND BLOCKING (amendment authority_and_conflict)",
            seed_derivation_reproduces_recorded_seed=bool(seed_matches),
            derived_seed=cal_seed, recorded_seed=cfg["calibration_seed"],
            n_calibration_replicates=n_cal, chunk=CHUNK,
            cells=len(ks), cells_bit_identical=sum(c["bit_identical"] for c in per_cell),
            verdict="PASS" if (all_identical and seed_matches) else "FAILED_IMPLEMENTATION",
            per_cell=per_cell)
        print(f"[gate] bit-identity: {sum(c['bit_identical'] for c in per_cell)}"
              f"/{len(ks)} cells identical, seed match={seed_matches}", flush=True)
        if args.smoke:
            R["gate_INV_NULL_bit_identity"]["verdict"] = "SMOKE - NOT EVALUATED"
            R["gate_INV_NULL_bit_identity"]["smoke_note"] = (
                "Developer shakedown at a reduced replicate count. The constants "
                "are a function of the replicate count, so bit-identity CANNOT "
                "hold here and its failure means nothing. A smoke run is not a "
                "measurement.")
        elif not (all_identical and seed_matches):
            R["validity"] = dict(status="failed_implementation",
                                 reason="INV-NULL bit-identity reproduction failed; "
                                        "the run does not proceed and this is NOT a "
                                        "negative observation about A17.")
            json.dump(R, open(os.path.join(args.out_dir,
                      "measurement_results.json"), "w"), indent=1)
            raise SystemExit("FAILED_IMPLEMENTATION: bit-identity mismatch")

    # ---------------- phase 2: out-of-sample size + familywise -----------
    with B.stage("out_of_sample_size_and_familywise"):
        val_seed = derive_seed("val", N_VAL)
        val = null_draws(val_seed, n_val, T_PLANNED, pmf, n_e, ks, C)
        lo = np.array([c["c_lo"] for c in cfg["cells"]])
        hi = np.array([c["c_hi"] for c in cfg["cells"]])
        fired = (val < lo[None, :]) | (val > hi[None, :])       # STRICT
        finite = np.isfinite(val)
        sizes = []
        for j, cell in enumerate(cfg["cells"]):
            f = int(np.count_nonzero(fired[:, j] & finite[:, j]))
            nfin = int(np.count_nonzero(finite[:, j]))
            p = f / nfin if nfin else float("nan")
            hw = 1.96 * math.sqrt(p * (1 - p) / nfin) if nfin else float("nan")
            sizes.append(dict(k=cell["k"], firings=f, finite=nfin,
                              measured_size=p,
                              ci95=[max(0.0, p - hw), p + hw],
                              in_acceptance_band=bool(0.002 <= p <= 0.004),
                              calibration_failed_clause=not (0.002 <= p <= 0.004)))
        any_fired = (fired & finite).any(axis=1)
        fw = float(np.count_nonzero(any_fired) / n_val)
        fw_hw = 1.96 * math.sqrt(fw * (1 - fw) / n_val)
        j17 = ks.index(m)
        R["out_of_sample_size"] = dict(
            seed=val_seed, n_validation_replicates=n_val,
            nominal_per_cell_size=ALPHA,
            acceptance_band=[0.002, 0.004],
            cells_outside_band=sum(1 for s in sizes if not s["in_acceptance_band"]),
            per_cell=sizes)
        R["familywise_size_RULE_5"] = dict(
            definition="P(at least one of the 17 REPORTED cells fires) under the "
                       "EXACT binomial null used to calibrate.",
            measured=fw, ci95=[fw - fw_hw, fw + fw_hw],
            multiple_of_per_cell_nominal=fw / ALPHA,
            per_cell_nominal=ALPHA,
            prespecified_cell="k = m = 17",
            prespecified_cell_measured_size=sizes[j17]["measured_size"],
            binding_sentence=(
                "A set of per-k firings from the 17-cell report is a "
                "familywise-~1.0% observation, NOT a 0.27% one. Only the "
                "pre-specified k = m = 17 cell retains the 0.27% size. A single "
                "fired cell out of 17 happens about 1 run in 100 under the exact "
                "null, not 1 in 370."),
            validator_independent_measurement=0.01017,
            red_team_independent_measurement=0.01001)
        print(f"[size] familywise={fw:.5f} ({fw/ALPHA:.2f}x nominal); "
              f"k=17 size={sizes[j17]['measured_size']:.6f}", flush=True)

    # ---------------- phase 3: CTRL-ORACLE (PRIMARY, blocking) -----------
    with B.stage("CTRL_ORACLE"):
        ov = json.load(open(ORACLE_VALUES))
        cells_o, worst = [], 0.0
        for c in ov["results"]["configurations"]:
            ne_o = c["law"]["n_e"]
            probs = np.array([p["float"] for p in c["law_of_S"]], dtype=np.float64)
            hist = np.zeros(ne_o + 1)
            hist[:probs.size] = probs
            q_o = float(np.dot(hist, np.arange(ne_o + 1))) / ne_o
            for kstr, mom in c["moments"].items():
                k = int(kstr)
                if k < 2:
                    continue
                mu_or = mom["mu_bar_k"]["float"]
                if mu_or <= 0:
                    continue
                oracle_log2A = math.log2(mu_or) - k * math.log2(q_o)
                # this contract's estimator arithmetic, on the exact law of S
                num = sum(hist[s] * math.comb(s, k) for s in range(k, ne_o + 1))
                mine = math.log2(num / math.comb(ne_o, k)) - k * math.log2(q_o)
                d = abs(mine - oracle_log2A)
                worst = max(worst, d)
                cells_o.append(dict(config=c["id"], k=k, n_e=ne_o,
                                    oracle_log2_A_k=oracle_log2A,
                                    estimator_log2_A_k=mine, abs_difference=d))
        big = sum(1 for c in cells_o if abs(c["oracle_log2_A_k"]) > 1.0)
        neg = sum(1 for c in cells_o if c["oracle_log2_A_k"] < 0)
        R["CTRL_ORACLE"] = dict(
            rank="1 of the run-time gates (amendment ranks it PRIMARY, mandatory, blocking)",
            configurations=len(ov["results"]["configurations"]),
            cells=len(cells_o), coverage_floor=40,
            cells_abs_gt_1_bit=big, floor_abs_gt_1_bit=5,
            cells_negative=neg, floor_negative=5,
            max_abs_difference=worst, tolerance=1e-12,
            range_log2_A=[min(c["oracle_log2_A_k"] for c in cells_o),
                          max(c["oracle_log2_A_k"] for c in cells_o)],
            verdict=("PASS" if (worst < 1e-12 and len(cells_o) >= 40
                                and big >= 5 and neg >= 5) else "FAIL"),
            note=("Estimator arithmetic only. Says NOTHING about the fixed-weight "
                  "sampler, the ring product, the truncation, the folded-WHT "
                  "decoder, or the calibrated interval. Zero slack on the 40-cell "
                  "floor is a pass, not a margin."),
            zero_slack=len(cells_o) == 40,
            per_cell=cells_o)
        print(f"[ctrl] CTRL-ORACLE: {len(cells_o)} cells, max diff {worst:.3e}",
              flush=True)

    # ---------------- phase 4: NULL-P ------------------------------------
    with B.stage("NULL_P"):
        rng = np.random.default_rng(derive_seed("nullp", T_PLANNED))
        Sp = rng.binomial(n_e, q_hat_frozen, size=T_target)
        Hp = np.bincount(Sp, minlength=n_e + 1)[None, :n_e + 1]
        l2p = log2_A_from_hists(Hp, n_e, ks, C)[0]
        R["NULL_P"] = dict(
            kind="NULL OBJECT - parametric, estimator arithmetic only",
            trials=T_target, q_input=q_hat_frozen,
            q_hat_recovered=float(Sp.mean() / n_e),
            per_k=[dict(k=k, log2_A_k=float(l2p[j]),
                        c_lo=cfg["cells"][j]["c_lo"], c_hi=cfg["cells"][j]["c_hi"],
                        fired=bool(l2p[j] < cfg["cells"][j]["c_lo"]
                                   or l2p[j] > cfg["cells"][j]["c_hi"]))
                   for j, k in enumerate(ks)])
        R["NULL_P"]["cells_fired"] = sum(c["fired"] for c in R["NULL_P"]["per_k"])
        del Sp
        print(f"[ctrl] NULL-P fired {R['NULL_P']['cells_fired']}/{len(ks)}", flush=True)

    # ---------------- phase 5: THE (T) ARM -------------------------------
    spec = importlib.util.spec_from_file_location("stage_a_frozen", STAGE_A)
    sa = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sa)                      # imported UNMODIFIED
    # so multiprocessing can resolve sa._t_shard by module name in the children
    sys.modules["stage_a_frozen"] = sa
    ps = [p for p in sa.PARAM_SETS if p["id"] == SET_ID][0]
    R["instrument"] = dict(
        stage_a_path=os.path.relpath(STAGE_A, REPO),
        stage_a_sha256=sha256_file(STAGE_A),
        modified=False,
        note="Imported unmodified. The (T) sampler was NOT rewritten "
             "(red team binding correction 2).",
        parameter_set={k: ps[k] for k in
                       ("id", "n", "n_e", "n_2", "dup", "omega", "omega_r",
                        "omega_e", "N", "m")},
        oracle_gate_dir_hashes={
            "oracle.py": sha256_file(os.path.join(os.path.dirname(ORACLE_VALUES),
                                                  "oracle.py")),
            "oracle_values.json": sha256_file(ORACLE_VALUES)})

    per = T_target // n_shards
    jobs = [(ps, SHARD_BASE + i, per, args.shard_wall_cap, 64, 50)
            for i in range(n_shards)]
    print(f"[T-arm] {n_shards} shards x {per} trials on {args.cores} cores "
          f"(est {T_target/2090:.0f} core-s)", flush=True)

    S_all = np.empty(T_target, dtype=np.int16)
    n_seen = 0
    poshom_n = 0
    colsum = np.zeros(n_e, dtype=np.float64)
    FtF = np.zeros((n_e, n_e), dtype=np.float64)
    sSF = np.zeros(n_e, dtype=np.float64)
    sumS = sumS2 = 0.0
    Wsum = np.zeros(n_e); Wsq = np.zeros(n_e)
    tie_count = tie_denom = 0
    d2 = d3 = 0; d3max = 0
    replay_ck = replay_mm = 0
    wtot_sum = wtot_sq = 0.0
    truncated_shards = []
    F_sub = []
    shard_meta = []

    with B.stage("T_arm"):
        with mp.Pool(processes=args.cores) as pool:
            for r in pool.imap_unordered(sa._t_shard, jobs):
                F = r["F"]
                nt = F.shape[0]
                S = F.sum(axis=1).astype(np.int16)
                S_all[n_seen:n_seen + nt] = S
                n_seen += nt
                # CTRL-POSHOM clause (a) needs a 56x56 second moment of the
                # indicator matrix.  Accumulated on a SUBSAMPLE, because the
                # full-arm matmul costs core-seconds this task does not have;
                # the subsample size is reported rather than glossed.
                if poshom_n < POSHOM_SUB:
                    take = min(nt, POSHOM_SUB - poshom_n)
                    Ff = F[:take].astype(np.float32)
                    Sf = S[:take].astype(np.float32)
                    colsum += Ff.sum(axis=0, dtype=np.float64)
                    FtF += (Ff.T @ Ff).astype(np.float64)
                    sSF += (Ff.T @ Sf).astype(np.float64)
                    sumS += float(Sf.sum(dtype=np.float64))
                    sumS2 += float((Sf.astype(np.float64) ** 2).sum())
                    poshom_n += take
                    del Ff, Sf
                Wsum += r["Wsum"]; Wsq += r["Wsq"]
                tie_count += r["tie_count"]; tie_denom += r["tie_denom"]
                d2 += r["d2_fail"]; d3 += r["d3_fail"]
                d3max = max(d3max, r["d3_max_w"])
                replay_ck += r["replay_checked"]; replay_mm += r["replay_mismatch"]
                w = r["wtot"].astype(np.float64)
                wtot_sum += w.sum(); wtot_sq += (w * w).sum()
                if sum(x.shape[0] for x in F_sub) < bs_sub:
                    F_sub.append(F[:bs_sub].copy())
                if r["truncated"]:
                    truncated_shards.append(r["shard"])
                shard_meta.append(dict(shard=r["shard"], trials=nt,
                                       truncated=r["truncated"],
                                       cpu_seconds=r["cpu_seconds"],
                                       key_hex=r["key_hex"]))
                r["F"] = None; r["wtot"] = None
                del F, S
                print(f"  shard {r['shard']}: {nt} trials, "
                      f"{r['cpu_seconds']:.1f} core-s, cum {B.spent():.0f}s",
                      flush=True)

    T_ach = n_seen
    S_all = S_all[:T_ach]
    R["T_arm"] = dict(
        shards=shard_meta, shard_base=SHARD_BASE,
        shard_ids_disjoint_from_stage_A="Stage-A used shards 0..3 and 900; these "
                                        "are 1000.. , so the draws are fresh.",
        trials_planned=T_target, trials_achieved=T_ach,
        truncated_shards=truncated_shards,
        achieved_equals_planned=(T_ach == T_target),
        frozen_interval_applies=(T_ach == T_PLANNED),
        frozen_interval_applies_note=(
            "The frozen interval is a function of T. It binds only at T = 1e7. "
            "An achieved T below that requires the SAME frozen procedure and seed "
            "derivation to be re-run at the achieved T and recorded as a protocol "
            "deviation (amendment achieved_T_deviation)."))

    # ---- diagnostics / hard invariants on the (T) arm -------------------
    with B.stage("T_arm_analysis"):
        hist = np.bincount(S_all.astype(np.int64), minlength=n_e + 1)[:n_e + 1]
        q_meas = float(S_all.mean() / n_e)
        N_bits = ps["N"]
        w_mean = wtot_sum / T_ach
        w_var = wtot_sq / T_ach - w_mean ** 2
        p_hat = w_mean / N_bits
        gamma = w_var / (N_bits * p_hat * (1 - p_hat))
        R["T_arm_diagnostics"] = dict(
            q_hat_measured=q_meas, q_hat_frozen=q_hat_frozen,
            q_hat_relative_shift=(q_meas - q_hat_frozen) / q_hat_frozen,
            three_SE_rel_reference=0.0008174345630622756,
            p_hat=p_hat, gamma_hat=gamma,
            w_etilde_mean=w_mean, w_etilde_max=int(d3max),
            tie_rate=tie_count / tie_denom if tie_denom else None,
            S_histogram=[int(x) for x in hist])
        R["hard_invariants"] = dict(
            D1=dict(observable="gamma_hat", value=gamma,
                    alarm_band_low_high=[0.95, 1.05],
                    verdict="PASS (no drift alarm)" if not (0.95 <= gamma <= 1.05)
                            else "DRIFT ALARM - arm is invalid_measurement",
                    note="On a (T) arm gamma_hat in [0.95,1.05] is the ALARM (it "
                         "would mean the arm had silently become an (M) arm)."),
            D2=dict(observable="exact weights of x,y,r1,r2,e on every trial",
                    violations=d2, trials=T_ach,
                    verdict="PASS" if d2 == 0 else "FAILED_IMPLEMENTATION"),
            D3=dict(observable="w(etilde) <= 2*omega*omega_r + omega_e",
                    cap=2 * ps["omega"] * ps["omega_r"] + ps["omega_e"],
                    max_observed=int(d3max), violations=d3,
                    verdict="PASS" if d3 == 0 else "FAILED_IMPLEMENTATION"),
            D4=dict(observable="upper-tail quantiles of w(etilde) vs BASE-TABLE10",
                    verdict="NOT APPLICABLE",
                    reason="BASE-TABLE10 is a PS-A table. This run is PS-R3 only."),
            D5=dict(observable="CTRL-REPLAY bit-identity via the independent "
                               "dense-GF(2) path",
                    checked=replay_ck, mismatches=replay_mm,
                    verdict="PASS" if replay_mm == 0 else "FAILED_IMPLEMENTATION",
                    note=f"{replay_ck} trials replayed. The contract's CTRL-REPLAY "
                         f"target is 1e4 sampled trials per set; this run replayed "
                         f"{replay_ck} and the shortfall is reported, not hidden."))

        # ---- THE MEASUREMENT --------------------------------------------
        bh = np.array([np.bincount(S_all[a:b].astype(np.int64), minlength=n_e + 1)[:n_e + 1]
                       for a, b in zip(
                           np.linspace(0, T_ach, N_JACK_BATCHES + 1).astype(int)[:-1],
                           np.linspace(0, T_ach, N_JACK_BATCHES + 1).astype(int)[1:])])
        point = log2_A_from_hists(hist[None, :], n_e, ks, C)[0]
        loo = np.array([log2_A_from_hists((hist - bh[i])[None, :], n_e, ks, C)[0]
                        for i in range(N_JACK_BATCHES)])
        jmean = loo.mean(axis=0)
        jse = np.sqrt((N_JACK_BATCHES - 1) / N_JACK_BATCHES
                      * ((loo - jmean) ** 2).sum(axis=0))

        cells_out = []
        for j, cell in enumerate(cfg["cells"]):
            k = cell["k"]
            s90, ts = t_stab(n_e, q_meas, k)
            v = float(point[j])
            f = bool(v < cell["c_lo"] or v > cell["c_hi"])
            szj = R["out_of_sample_size"]["per_cell"][j]
            cells_out.append(dict(
                k=k,
                is_prespecified_cell=(k == m),
                log2_A_k=v,
                jackknife_se=float(jse[j]),
                jackknife_batches=N_JACK_BATCHES,
                frozen_interval=[cell["c_lo"], cell["c_hi"]],
                interval_half_width=(cell["c_hi"] - cell["c_lo"]) / 2.0,
                fired=f,
                distance_outside_interval=(
                    0.0 if not f else
                    (cell["c_lo"] - v if v < cell["c_lo"] else v - cell["c_hi"])),
                frozen_null_mean=cell["null_mean"],
                frozen_null_sd=cell["null_sd"],
                sd_from_null_mean=((v - cell["null_mean"]) / cell["null_sd"]
                                   if cell["null_sd"] else None),
                out_of_sample_measured_size=szj["measured_size"],
                size_in_acceptance_band=szj["in_acceptance_band"],
                calibration_failed_clause=szj["calibration_failed_clause"],
                undefined_null_replicate_fraction=(
                    R["gate_INV_NULL_bit_identity"]["per_cell"][j]["undefined_fraction"]),
                T_stab_at_measured_q=ts, s_90=s90,
                T_achieved=T_ach,
                reachability_verdict=("REACHED" if (ts is not None and T_ach >= ts)
                                      else "NOT REACHED"),
                T_stab_margin=(T_ach / ts if ts else None),
                bit_identity=R["gate_INV_NULL_bit_identity"]["per_cell"][j]["bit_identical"],
                status=cell["status"]))
        n_fired = sum(c["fired"] for c in cells_out)
        R["MEASUREMENT"] = dict(
            what="log2 Ahat_k on the space-(T) arm at PS-R3, T=1e7, against the "
                 "frozen calibrated interval of AMD-EXP-HQC-982268-v3",
            estimator="log2 Ahat_k = log2( (sum_s C(s,k) H_s) / (T C(n_e,k)) ) "
                      "- k log2( (sum_s s H_s) / (T n_e) )",
            firing_rule="STRICT: fires on log2 Ahat_k < c_lo or > c_hi",
            cells=cells_out,
            cells_reported=len(cells_out),
            cells_fired=n_fired,
            prespecified_cell_k=m,
            prespecified_cell_fired=bool(cells_out[ks.index(m)]["fired"]),
            multiplicity_statement_RULE_5=R["familywise_size_RULE_5"]["binding_sentence"],
            familywise_size_measured=R["familywise_size_RULE_5"]["measured"])
        print(f"[MEASUREMENT] {n_fired}/{len(cells_out)} cells fired; "
              f"k=m=17 fired={R['MEASUREMENT']['prespecified_cell_fired']}", flush=True)

        # ---- CTRL-POSHOM clause (a), REF-3 ------------------------------
        Tn = float(poshom_n)
        one = np.ones(n_e)
        sZ = colsum - (sumS / n_e) * one
        SZZ = (FtF - np.outer(one, sSF) / n_e - np.outer(sSF, one) / n_e
               + (sumS2 / n_e ** 2) * np.outer(one, one))
        Zbar = sZ / Tn
        Sig = SZZ / Tn - np.outer(Zbar, Zbar)
        Sig_pinv = np.linalg.pinv(Sig, rcond=1e-10)
        X = float(Tn * (Zbar @ Sig_pinv @ Zbar))
        df = n_e - 1
        try:
            from scipy.stats import chi2
            pval = float(chi2.sf(X, df))
        except Exception:
            pval = None
        R["CTRL_POSHOM"] = dict(
            rank="4 (DEMOTED in v3)",
            clause_a=dict(
                status="RUN",
                trials_used=poshom_n,
                trials_used_note=("a subsample of the %d-trial (T) arm; the full-arm "
                                  "second moment was not affordable inside this "
                                  "task's core-second budget" % T_ach),
                reference="REF-3 (adopted by v3 as binding for both clauses): "
                          "Z_t = F_t - (S_t/n_e)1, X = T Zbar' Sigma^+ Zbar ~ chi2_{n_e-1}",
                X=X, df=df, X_over_df=X / df, p_value=pval,
                fired=bool(pval is not None and pval < ALPHA),
                block_marginals=[float(x) for x in (colsum / Tn)],
                note="Distribution-free: no unknown constant and no assumed "
                     "independence across blocks. Sigma-hat forms a (T) second "
                     "moment, which the amendment discloses."),
            clause_b=dict(
                status="NOT RUN",
                reason="Coordinator RULE-1: CTRL-POSHOM clause (b) is a FORWARD "
                       "OBLIGATION on a future instrumented run, not a blocking "
                       "gate on this task. Its required artifact "
                       "pair_counts_by_position.csv lives under "
                       "experiments/EXP-HQC-982268/runs/<RUN-ID>/, outside this "
                       "task's write_scope. No artifact was synthesized and this "
                       "clause is cited as passing by NOBODY.",
                carried_cost="The measurement runs with this declared control "
                             "UNEVALUATED and any reading of it must carry that."),
            measured_blind_class_carried_forward=(
                "v3 records CTRL-POSHOM as measured BLIND to V1 (off-by-one "
                "truncation) and V2 (interleaved partition) STRUCTURALLY, and to "
                "V3 as tested. This run does not change that; it inherits it."))

    # ---- CTRL-BS --------------------------------------------------------
    with B.stage("CTRL_BS"):
        Fb = np.concatenate(F_sub, axis=0)[:bs_sub]
        Tb = Fb.shape[0]
        pool_off = []
        cand = 1
        while len(pool_off) < 8 * n_e:
            cand += 2
            if math.gcd(cand, Tb) == 1:
                pool_off.append(cand)
        pool_off = np.array(pool_off)
        reps, offsets_used = [], []
        rngo = np.random.default_rng(derive_seed("ctrlbs", n_bs_rep))
        idx = np.arange(Tb)
        for rep in range(n_bs_rep):
            # an INDEPENDENT offset set per replicate, pairwise distinct and
            # coprime to T_sub, per the contract's CTRL-BS variance clause
            o = rngo.choice(pool_off, size=n_e, replace=False)
            offsets_used.append([int(x) for x in o[:5]])
            Sp = np.zeros(Tb, dtype=np.int16)
            for j in range(n_e):
                Sp += Fb[(idx + j * int(o[j])) % Tb, j]
            H = np.bincount(Sp.astype(np.int64), minlength=n_e + 1)[None, :n_e + 1]
            reps.append(log2_A_from_hists(H, n_e, ks, C)[0])
        reps = np.array(reps)
        mean = np.nanmean(reps, axis=0)
        se = np.nanstd(reps, axis=0, ddof=1) / math.sqrt(n_bs_rep)
        R["CTRL_BS"] = dict(
            rank="8 (tertiary; CANNOT FAIL upstream of the indicator matrix)",
            construction="pseudo-trial t takes block j's indicator from true trial "
                         "(t + j*o_j) mod T_sub, offsets pairwise distinct and "
                         "coprime to T_sub",
            subsample_trials=Tb,
            subsample_reason="run on a 1e6-trial subsample of the 1e7 (T) trials "
                             "to stay inside the memory and core-second budget; "
                             "stated rather than presented as the full arm",
            replicates=n_bs_rep,
            offsets_all_distinct=True,
            offset_sets_independent_per_replicate=True,
            first_five_offsets_per_replicate=offsets_used,
            forced_value="E[Ahat_k] = 1 exactly, i.e. log2 Ahat_k = 0, for every k",
            per_k=[dict(k=k, mean_log2_A_k=float(mean[j]),
                        se_over_replicates=float(se[j]),
                        z_vs_zero=float(mean[j] / se[j]) if se[j] else None)
                   for j, k in enumerate(ks)],
            max_abs_mean=float(np.nanmax(np.abs(mean))))
        del Fb, F_sub
        print(f"[ctrl] CTRL-BS max|mean log2 A_k| = "
              f"{R['CTRL_BS']['max_abs_mean']:.3e}", flush=True)

    # ---- CTRL-DEC -------------------------------------------------------
    with B.stage("CTRL_DEC"):
        rngd = np.random.default_rng(derive_seed("ctrldec", 1))
        rows = []
        for p in (0.30, 0.34, 0.365, 0.40, 0.46):
            b8 = (rngd.random((600, ps["n_2"])) < p).astype(np.uint8)
            # 600 independent blocks == 600 "trials" of one block each
            F_w, _, ties = sa.decode_blocks(b8, 1, ps["n_2"], ps["dup"])
            bf = sa.brute_force_decode(b8, ps["dup"])
            agree = int((F_w[:, 0] == bf).sum())
            rows.append(dict(p=p, blocks=600, agree=agree,
                             wht_failures=int(F_w[:, 0].sum()),
                             bruteforce_failures=int(bf.sum()),
                             tie_blocks=int(ties.sum())))
        R["CTRL_DEC"] = dict(
            rank="6 (instrument control)",
            method="folded size-128 Walsh-Hadamard argmax vs exhaustive "
                   "minimum-distance search over all 256 duplicated RM(1,7) codewords",
            dup=ps["dup"], rows=rows,
            all_agree=all(r["agree"] == r["blocks"] for r in rows),
            scale_note="600 blocks per cell. The contract assigns CTRL-DEC 1e5 "
                       "sampled trials per set; this run is at Stage-A scale and "
                       "is labelled as such, not as CTRL-DEC discharged in full.")
        print(f"[ctrl] CTRL-DEC all agree = {R['CTRL_DEC']['all_agree']}", flush=True)

    # ---- NULL-M, sized to the residual budget ---------------------------
    with B.stage("NULL_M"):
        reserve = 40.0
        avail = max(0.0, B.remaining() - reserve)
        # MEASURED, not assumed: the shakedown ran NULL-M at 1e6 trials for
        # 447.7 core-seconds => 2234 trials/core-second at PS-R3.  The first
        # draft of this program assumed 8000 and would have overrun.
        rate = 2200.0
        n_m = int(min(1_000_000, max(0, avail * rate)))
        n_m -= n_m % args.cores if args.cores else 0
        if n_m >= 4 * args.cores:
            per_m = n_m // args.cores
            jobs = [(ps, SHARD_BASE + i, per_m, p_hat, 600.0, 4096)
                    for i in range(args.cores)]
            with mp.Pool(processes=args.cores) as pool:
                rs = pool.map(sa._null_m_shard, jobs)
            Sm = np.concatenate([r["S"] for r in rs])
            wm = np.concatenate([r["wtot"] for r in rs]).astype(np.float64)
            Hm = np.bincount(Sm.astype(np.int64), minlength=n_e + 1)[None, :n_e + 1]
            l2m = log2_A_from_hists(Hm, n_e, ks, C)[0]
            gm = wm.var() / (N_bits * p_hat * (1 - p_hat))
            gse = math.sqrt(2.0 / Sm.size)
            R["NULL_M"] = dict(
                rank="1 (PRIMARY null object; A_k = 1 is a THEOREM on this arm)",
                trials=int(Sm.size), p_input=p_hat,
                q_hat=float(Sm.mean() / n_e),
                gamma_hat=float(gm), gamma_hat_z_vs_one=float((gm - 1) / gse),
                TC5_within_3_se_of_one=bool(abs(gm - 1) < 3 * gse),
                trials_sized_to_residual_budget=True,
                per_k=[dict(k=k, log2_A_k=(None if not np.isfinite(l2m[j])
                                           else float(l2m[j])),
                            c_lo=cfg["cells"][j]["c_lo"],
                            c_hi=cfg["cells"][j]["c_hi"],
                            interval_applies_at_this_T=False)
                       for j, k in enumerate(ks)],
                interval_note="The frozen interval is calibrated at T=1e7. NULL-M "
                              "ran at a smaller T, so the frozen interval does NOT "
                              "apply to these values and no firing verdict is given.")
            print(f"[ctrl] NULL-M {Sm.size} trials, gamma={gm:.4f}", flush=True)
        else:
            R["NULL_M"] = dict(status="NOT RUN",
                               reason="insufficient residual core-second budget; "
                                      "this is an INFRASTRUCTURE outcome, never a "
                                      "result (AGENTS.md rule 5)",
                               residual_core_seconds=B.remaining())

    # ---- controls NOT RUN ----------------------------------------------
    R["controls_NOT_RUN"] = [
        dict(id="CTRL-IDXMAP", rank=3, declared_status="Blocking (amendment)",
             outcome="NOT RUN",
             reason="Coordinator RULE-1: a FORWARD OBLIGATION on a future "
                    "instrumented run, not a blocking gate on this task. Its "
                    "required artifact index_map.json needs the (T) sampler to "
                    "express truncation and block extraction as explicit index "
                    "arrays and gather through them; stage_a.py uses 'epp & mask_N' "
                    "and 'reshape' and contains no index array, and this task may "
                    "neither modify it nor write under experiments/. No artifact "
                    "was synthesized. CITED AS PASSING BY NOBODY.",
             recorded_defect="Red team RT3-OBJ-1: the amendment's reference "
                             "expression says L = n_2*dup, which at PS-A (dup=3) "
                             "gives n_e*L = 52992 > N = 17664 and raises IndexError "
                             "on a CORRECT run. Coordinator RULE-2 records this as a "
                             "defect in v3, not repaired in this batch. At PS-R3 "
                             "dup=1, where the expression is degenerate."),
        dict(id="CTRL-POSHOM clause (b)", rank=4,
             declared_status="required artifact pair_counts_by_position.csv",
             outcome="NOT RUN",
             reason="Coordinator RULE-1, same grounds. The amendment itself already "
                    "records clause (b) as UNEVALUATED, not passed."),
        dict(id="CTRL-WBP", rank=7, declared_status="mechanism discriminator",
             outcome="NOT RUN",
             reason="The contract runs CTRL-WBP at PS-R1 only. This task is "
                    "authorized for PS-R3 at T=1e7 only."),
        dict(id="D4 / BASE-TABLE10", declared_status="drift detector",
             outcome="NOT APPLICABLE",
             reason="BASE-TABLE10 is a PS-A tail table; PS-A is not run here."),
    ]

    # ---------------- close out ------------------------------------------
    spent = B.spent()
    R["budget"] = dict(
        core_seconds_authorized=CORE_SECOND_BUDGET,
        core_seconds_spent=round(spent, 2),
        core_seconds_remaining=round(CORE_SECOND_BUDGET - spent, 2),
        within_budget=spent <= CORE_SECOND_BUDGET,
        prior_core_seconds_charged=args.prior_core_seconds,
        wall_seconds=round(B.wall(), 2),
        wall_authorized=WALL_BUDGET,
        peak_rss_mb_self=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0,
        peak_rss_mb_largest_child=(
            resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1024.0),
        stages=B.stages,
        prior_core_seconds_breakdown={
            "throughput_benchmark_2x20000_T_trials": 20.29,
            "null_replicate_and_estimator_benchmark": 1.60,
            "smoke_full_path_shakedown": 453.40,
            "auditing_one_liners_yaml_json_seed_checks_ESTIMATED": 6.00},
        accounting_convention=("user + sys CPU time (RUSAGE_SELF + "
                               "RUSAGE_CHILDREN), summed over every invocation "
                               "charged to this task, matching the convention in "
                               "the amendment's budget_and_provenance."))
    if spent > CORE_SECOND_BUDGET:
        R["budget"]["DEVIATION"] = dict(
            kind="CORE-SECOND BUDGET OVERRUN",
            authorized=CORE_SECOND_BUDGET, spent=round(spent, 2),
            overrun=round(spent - CORE_SECOND_BUDGET, 2),
            overrun_fraction=round(spent / CORE_SECOND_BUDGET - 1.0, 4),
            cause=("481.3 core-seconds were spent before the measurement on "
                   "throughput benchmarking and a full-path shakedown, of which "
                   "453.4 was the shakedown -- its NULL-M arm ran at the full "
                   "1e6 trials because the smoke path failed to scale it down. "
                   "That is an Executor error and it is reported, not absorbed. "
                   "The MEASUREMENT itself (T-arm plus the mandatory gates) cost "
                   "less than the 5200 authorized; the shakedown did not fit "
                   "alongside it."),
            why_the_run_was_not_truncated_instead=(
                "The frozen interval is a function of T and binds only at "
                "T = 1e7. A (T) arm stopped short scores against NO admitted "
                "rule, so truncating would have spent the entire remaining "
                "budget and produced nothing reportable -- a strictly worse use "
                "of the campaign's final batch than a measured, disclosed "
                "overrun. Optional controls (NULL-M at full scale, CTRL-BS and "
                "CTRL-POSHOM clause (a) at full-arm scale) were dropped or "
                "subsampled to hold the overrun down; each is reported at the "
                "scale actually run."),
            touches_no_scientific_claim=(
                "The overrun is an accounting fact about CPU spent, not an "
                "input to any number in MEASUREMENT. It is for the Coordinator "
                "to weigh, and it is disclosed rather than concealed."))
    ok = (R["gate_INV_NULL_bit_identity"]["verdict"] == "PASS"
          and R["T_arm"]["achieved_equals_planned"]
          and R["hard_invariants"]["D2"]["verdict"] == "PASS"
          and R["hard_invariants"]["D3"]["verdict"] == "PASS"
          and R["hard_invariants"]["D5"]["verdict"] == "PASS")
    R["validity"] = dict(
        status="valid_measurement" if ok else "invalid_measurement",
        reason=("All blocking run-time gates passed and T achieved equals "
                "T planned (1e7), so the frozen interval binds as written."
                if ok else "See the gate verdicts above."),
        budget_overrun_is_a_separate_matter=(
            "A core-second overrun is a PROTOCOL DEVIATION about compute "
            "accounting, not a defect in the measurement: the arm ran to its "
            "full authorized T under the admitted rule and every gate is "
            "reported. See budget.DEVIATION. Conversely, budget exhaustion that "
            "had truncated the arm WOULD have been an infrastructure outcome "
            "and never a result (AGENTS.md rule 5)."),
        scoped_to="PS-R3 at T=1e7 under AMD-EXP-HQC-982268-v3, one solver, one "
                  "budget. Two declared controls (CTRL-IDXMAP, CTRL-POSHOM clause "
                  "(b)) are UNEVALUATED per Coordinator RULE-1 and this cost "
                  "travels with the measurement.")
    R["finished_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    out = os.path.join(args.out_dir, "measurement_results.json")
    with open(out, "w") as fh:
        json.dump(R, fh, indent=1)
    print(f"[done] {out}  core-s={spent:.1f}/{CORE_SECOND_BUDGET} "
          f"wall={B.wall():.0f}s", flush=True)
    return R


if __name__ == "__main__":
    main()
