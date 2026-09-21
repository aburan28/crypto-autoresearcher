#!/usr/bin/env python3
"""Planted-correlation control arm for EXP-HQC-982268 / OPEN-6.

TASK-20260806-e19f6c (executor) / BATCH-4b8ad3 / GOAL-HQC-001.

WHAT THIS IS
------------
A single-run instrument check, NOT a measurement about HQC. It builds an
instance whose TRUE joint block-failure law -- and hence its log2_A_k(k) for
k = 2..18 -- is derived in closed form in design.md BEFORE any trial is
sampled (see design.md Section 2), pushes that instance through the block-
partition / index-map path (Section 3), and then through the IDENTICAL
estimator + jackknife code TASK-20260806-cde749/measure.py used to produce
the PS-R3 measurement in EV-HQC-b71230. It reports MATCH or MISMATCH per k:
whether the recovered log2_Ahat_k falls inside the pipeline's own jackknife
interval around the known planted value.

WHAT IT IS NOT
--------------
Not a statement about HQC, A17, A5, any decoding-failure rate, or any
standardized parameter set. Not a re-run of PS-R3. Not an argument about
whether PS-R3's anti-correlation is real -- only about whether THIS pipeline
recovers a KNOWN answer on THIS known-answer instance. Claim tier: TOY.

A timeout, crash, missing dependency or budget exhaustion is an
INFRASTRUCTURE outcome and is never evidence about the mathematics
(AGENTS.md rule 5).

FAIL-CLOSED INTEGRITY CHECK
----------------------------
Before importing measure.py, this script hashes it and ABORTS (raises
SystemExit) if the hash does not match MEASURE_PY_EXPECTED_SHA256. This
check actually reads the value it compares (no top-level/nested-field
mismatch of the kind that made the prior executor's check fail-open; see
EV-HQC-b71230 unresolved_confounds).

Re-run:
    PYTHONDONTWRITEBYTECODE=1 python3 planted_arm.py --out-dir .
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import platform
import resource
import subprocess
import sys
import time
from fractions import Fraction

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *([".."] * 7)))

MEASURE_PY = os.path.join(
    REPO, "coordination", "goals", "GOAL-HQC-001", "batches", "BATCH-0a65c0",
    "tasks", "TASK-20260806-cde749", "measure.py")
# sha256 of measure.py as read by this task at design time (2026-08-06).
# FAIL-CLOSED: load_measure_module() below actually reads this constant and
# compares it against a freshly computed hash of the file on disk, and
# raises SystemExit on any mismatch. It does not check a differently-named
# or differently-nested field (the prior executor's defect).
MEASURE_PY_EXPECTED_SHA256 = (
    "a4fd1ecb63f0ddc83c02ef45f2c65ab31cf13d13e7ae94f500e67465b24f5dc8")

TASK_ID = "TASK-20260806-e19f6c"
# Distinct seed prefix from measure.py's ("EXP-HQC-982268/v3/INV-NULL"), so
# the two tasks' random streams cannot collide or be mistaken for one
# another. Newly written for this task (design.md Section 4).
SEED_PREFIX = f"{TASK_ID}/PLANTED-ARM/v1"

# ---------------------------------------------------------------------------
# parameters -- order-matched to PS-R3 (design.md Section 1)
# ---------------------------------------------------------------------------
N_E = 56
N_2 = 128
DUP = 1
N = N_E * N_2                       # 7168, matches PS-R3's N
M_PRESPEC = 17                       # kept for narrative parity with PS-R3 only
K_MAX = 18
KS = list(range(2, K_MAX + 1))       # 17 cells, k = 2..18, matches PS-R3
T_PLANNED = 10_000_000               # matches PS-R3's allocation
N_JACK_BATCHES = 200                 # must equal measure.N_JACK_BATCHES (asserted)

# the planted mixture law (design.md Section 2)
SUPPORT = [17, 18, 19]
WEIGHTS = [Fraction(1, 3), Fraction(1, 3), Fraction(1, 3)]

# frozen table from design.md Section 2.1 -- computed BEFORE any sampling.
# planted_law() below recomputes this from the same closed form and this
# script asserts bit-for-bit agreement before proceeding (a run-time
# reproduction check in the spirit of measure.py's own INV-NULL gate).
DESIGN_TABLE_LOG2_A = {
    2: -0.05332724412846135, 3: -0.16394044463458357, 4: -0.3363079856368989,
    5: -0.5755089290487359, 6: -0.8873624322504217, 7: -1.2785962698872737,
    8: -1.7570703364157492, 9: -2.3320793631074803, 10: -3.0147730405328055,
    11: -3.8187560346206517, 12: -4.76097481483005, 13: -5.8630844320447935,
    14: -7.153668398603774, 15: -8.672097148069227, 16: -10.47587716111893,
    17: -12.65660891751783, 18: -15.382583727766058,
}
DESIGN_Q = 0.32142857142857145

CORE_SECOND_BUDGET = 1800.0
WALL_BUDGET = 2700.0
MATCH_SE_MULTIPLIER = 3.0   # design.md Section 5: adopted, not verbatim from measure.py


# ---------------------------------------------------------------------------
# provenance helpers
# ---------------------------------------------------------------------------

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def core_seconds() -> float:
    a = resource.getrusage(resource.RUSAGE_SELF)
    b = resource.getrusage(resource.RUSAGE_CHILDREN)
    return a.ru_utime + a.ru_stime + b.ru_utime + b.ru_stime


def git_state():
    def run(*a):
        try:
            return subprocess.run(a, cwd=REPO, capture_output=True, text=True,
                                  timeout=60).stdout.strip()
        except Exception as exc:                                   # pragma: no cover
            return f"<unavailable: {exc}>"
    return dict(commit=run("git", "rev-parse", "HEAD"),
                branch=run("git", "rev-parse", "--abbrev-ref", "HEAD"),
                dirty=bool(run("git", "status", "--porcelain")),
                dirty_paths=run("git", "status", "--porcelain").splitlines()[:40])


def derive_seed(purpose: str, n: int) -> int:
    """Newly written for this task (design.md Section 4). Structurally similar
    to measure.py's derive_seed but a DISTINCT prefix/function -- not copied,
    not sharing state."""
    s = f"{SEED_PREFIX}|{purpose}|{n}"
    return int.from_bytes(hashlib.sha256(s.encode()).digest()[:8], "big")


# ---------------------------------------------------------------------------
# FAIL-CLOSED import of measure.py (RULE-4-style read-only reuse)
# ---------------------------------------------------------------------------

def load_measure_module():
    actual = sha256_file(MEASURE_PY)
    if actual != MEASURE_PY_EXPECTED_SHA256:
        # This branch is reachable and tested: see run_manifest.yaml's
        # fail_closed_check_verification for a deliberate-mismatch dry run.
        raise SystemExit(
            "FAIL-CLOSED: measure.py sha256 mismatch. expected="
            f"{MEASURE_PY_EXPECTED_SHA256} actual={actual}. This task reuses "
            "measure.py's estimator verbatim and refuses to proceed if the "
            "file on disk differs from what design.md was written against.")
    spec = importlib.util.spec_from_file_location("measure_frozen", MEASURE_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)                         # imported UNMODIFIED
    return mod, actual


# ---------------------------------------------------------------------------
# planted law: closed form (design.md Section 2)
# ---------------------------------------------------------------------------

def planted_law():
    q_exact = sum(w * v for w, v in zip(WEIGHTS, SUPPORT)) / Fraction(N_E)
    cells = {}
    for k in KS:
        num = sum(w * math.comb(v, k) for w, v in zip(WEIGHTS, SUPPORT))
        mu_exact = num / Fraction(math.comb(N_E, k))
        mu_f = float(mu_exact)
        l2A = math.log2(mu_f) - k * math.log2(float(q_exact))
        cells[k] = dict(k=k, mu_bar_k_exact=str(mu_exact), mu_bar_k_float=mu_f,
                        planted_log2_A_k=l2A)
    return dict(q_exact=str(q_exact), q_float=float(q_exact), cells=cells)


# ---------------------------------------------------------------------------
# the block-partition / index-map generator (design.md Section 3)
# ---------------------------------------------------------------------------

def run_batch(rng: np.random.Generator, n_trials: int, n_e: int, L: int,
             sub_chunk: int):
    """One jackknife batch. Exercises, per sub-chunk:
      1. draw M_t ~ Uniform{17,18,19}                       (design.md 2)
      2. draw a uniform random size-M_t subset of n_e blocks  (design.md 2)
      3. expand to a flat length-(n_e*L) bit vector            (design.md 3.2)
      4. RESHAPE to (batch, n_e, L) with L = N // n_e          (design.md 3.3, RULE-2)
      5. REDUCE each block via majority threshold to recover F (design.md 3.4)
      6. assert F == block_fail (fail-closed self-check)       (design.md 3.5)
      7. S_t = F.sum(axis=1), accumulate into this batch's histogram
    Returns (hist, sub_chunks_checked).
    """
    hist = np.zeros(n_e + 1, dtype=np.int64)
    remaining = n_trials
    checked = 0
    while remaining > 0:
        b = min(sub_chunk, remaining)
        m0 = rng.integers(SUPPORT[0], SUPPORT[-1] + 1, size=b)   # {17,18,19}, unbiased
        keys = rng.random((b, n_e))
        ranks = np.argsort(np.argsort(keys, axis=1), axis=1)
        block_fail = (ranks < m0[:, None])                        # (b, n_e) bool

        flat = np.repeat(block_fail.astype(np.uint8), L, axis=1)   # (b, n_e*L) = (b, N)
        blk = flat.reshape(b, n_e, L)                              # THE block-partition step
        blocksum = blk.sum(axis=2, dtype=np.int32)
        F = blocksum > (L // 2)                                    # THE reduce step

        if not np.array_equal(F, block_fail):
            raise SystemExit(
                "FAIL-CLOSED: block-partition self-check failed -- recovered "
                "F does not equal the planted block_fail pattern. Aborting "
                "rather than reporting a result from a broken partition path "
                "(design.md Section 3, step 5).")
        checked += 1

        S = F.sum(axis=1)
        hist += np.bincount(S, minlength=n_e + 1)[:n_e + 1]
        remaining -= b
    return hist, checked


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=HERE)
    ap.add_argument("--sub-chunk", type=int, default=10_000)
    ap.add_argument("--batches", type=int, default=N_JACK_BATCHES)
    ap.add_argument("--trials", type=int, default=T_PLANNED)
    args = ap.parse_args(argv)

    t_wall0 = time.time()
    c0 = core_seconds()
    stages = []

    def stage_end(name, cw0, cc0):
        rec = dict(stage=name, core_seconds=round(core_seconds() - cc0, 3),
                   wall_seconds=round(time.time() - cw0, 3))
        stages.append(rec)
        print(f"[stage] {name}: {rec['core_seconds']}s core, {rec['wall_seconds']}s wall",
              flush=True)
        return rec

    R = {
        "task_id": TASK_ID,
        "role": "executor",
        "experiment_id": "EXP-HQC-982268",
        "hypothesis_id": "H-HQC-18d1b4",
        "goal": "GOAL-HQC-001",
        "batch": "BATCH-4b8ad3",
        "claim_tier": "toy",
        "what_this_is": (
            "A planted-correlation control arm for OPEN-6 (EV-HQC-b71230). "
            "An instance whose true joint block-failure law is derived in "
            "closed form in design.md BEFORE any trial is sampled, pushed "
            "through the block-partition path and then through the "
            "IDENTICAL estimator/jackknife code TASK-20260806-cde749/"
            "measure.py used for PS-R3. Reports MATCH/MISMATCH per k -- "
            "observations only, no conclusion about A17, HQC's DFR, or any "
            "standardized parameter set."),
        "design_doc": "design.md (written and frozen before this run; see "
                       "run_manifest.yaml for the file-timestamp ordering "
                       "evidence)",
        "started_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    # ---------------- phase 0: provenance ---------------------------------
    cw0 = time.time(); cc0 = core_seconds()
    R["git"] = git_state()
    R["environment"] = dict(
        python=sys.version.split()[0], numpy=np.__version__,
        platform=platform.platform(), processor=platform.machine(),
        cpu_count=os.cpu_count())
    stage_end("provenance", cw0, cc0)

    # ---------------- phase 1: FAIL-CLOSED integrity check + import -------
    cw0 = time.time(); cc0 = core_seconds()
    measure, measure_sha_actual = load_measure_module()
    R["reused_pipeline"] = dict(
        source_path=os.path.relpath(MEASURE_PY, REPO),
        source_task="TASK-20260806-cde749",
        sha256_expected=MEASURE_PY_EXPECTED_SHA256,
        sha256_actual=measure_sha_actual,
        integrity_check_passed=(measure_sha_actual == MEASURE_PY_EXPECTED_SHA256),
        n_jack_batches_in_measure_py=measure.N_JACK_BATCHES,
        reused_symbols=["comb_matrix", "log2_A_from_hists", "N_JACK_BATCHES",
                        "jackknife/batch-histogram computation (lines 730-739, "
                        "copied verbatim with local variable names)"])
    if measure.N_JACK_BATCHES != N_JACK_BATCHES:
        raise SystemExit("FAIL-CLOSED: N_JACK_BATCHES mismatch between this "
                         "task's constant and measure.py's -- would silently "
                         "change the jackknife construction.")
    stage_end("fail_closed_integrity_and_import", cw0, cc0)

    # ---------------- phase 2: planted law (closed form) -------------------
    cw0 = time.time(); cc0 = core_seconds()
    law = planted_law()
    mismatches = []
    for k in KS:
        if abs(law["cells"][k]["planted_log2_A_k"] - DESIGN_TABLE_LOG2_A[k]) > 1e-12:
            mismatches.append(k)
    if abs(law["q_float"] - DESIGN_Q) > 1e-15:
        mismatches.append("q")
    R["planted_law"] = dict(
        construction="design.md Section 2: M_t ~ Uniform{17,18,19}, blocks "
                     "chosen as a uniform random size-M_t subset of n_e=56; "
                     "S_t = M_t exactly.",
        support=SUPPORT, weights=["1/3", "1/3", "1/3"],
        q_exact=law["q_exact"], q_float=law["q_float"],
        cells=[law["cells"][k] for k in KS],
        design_md_reproduction_check=dict(
            mismatched_keys=mismatches,
            verdict="PASS" if not mismatches else "FAIL"))
    if mismatches:
        R["validity"] = dict(status="failed_implementation",
                             reason=f"recomputed planted law diverges from "
                                    f"design.md's frozen table at {mismatches}")
        json.dump(R, open(os.path.join(args.out_dir, "planted_results.json"), "w"),
                  indent=1)
        raise SystemExit("FAIL-CLOSED: planted-law reproduction check failed")
    print(f"[law] q={law['q_float']:.6f}, {len(KS)} cells, design.md "
          f"reproduction PASS", flush=True)
    stage_end("planted_law_derivation", cw0, cc0)

    # ---------------- phase 3: block-partition generation ------------------
    n_e = N_E
    L = N // n_e                              # RULE-2: L = N / n_e, never n_2*dup
    if L != N_2:
        raise SystemExit(f"FAIL-CLOSED: L=N/n_e={L} != N_2={N_2}; parameter "
                         f"mismatch, aborting rather than proceeding on an "
                         f"unintended block length.")
    ks = KS
    C = measure.comb_matrix(n_e, ks)          # REUSED VERBATIM (measure.py)

    if args.trials % args.batches != 0:
        raise SystemExit("FAIL-CLOSED: --trials must divide evenly into "
                         "--batches for the jackknife-batch-per-generation-"
                         "chunk construction used here.")
    per_batch = args.trials // args.batches

    cw0 = time.time(); cc0 = core_seconds()
    bh = np.zeros((args.batches, n_e + 1), dtype=np.int64)
    batch_seeds = []
    sub_chunks_checked_total = 0
    truncated = False
    truncated_at_batch = None
    for i in range(args.batches):
        if time.time() - t_wall0 > WALL_BUDGET - 60:
            truncated = True
            truncated_at_batch = i
            print(f"[budget] wall-clock budget nearly exhausted at batch {i}/"
                  f"{args.batches}; stopping (INFRASTRUCTURE outcome, not a "
                  f"result).", flush=True)
            break
        seed = derive_seed("batch", i)
        batch_seeds.append(seed)
        rng = np.random.Generator(np.random.PCG64(seed))
        bh[i], checked = run_batch(rng, per_batch, n_e, L, args.sub_chunk)
        sub_chunks_checked_total += checked
        if i % 40 == 0 or i == args.batches - 1:
            print(f"[batch] {i + 1}/{args.batches} done, cum core-s="
                  f"{core_seconds() - c0:.1f}", flush=True)
    stage_end("block_partition_generation", cw0, cc0)

    batches_completed = (args.batches if not truncated else truncated_at_batch)
    T_ach = int(bh[:batches_completed].sum())
    R["generation"] = dict(
        n_e=n_e, N=N, L=L, L_formula="L = N // n_e (RULE-2 corrected; NOT n_2*dup)",
        trials_planned=args.trials, batches_planned=args.batches,
        trials_per_batch_planned=per_batch, sub_chunk=args.sub_chunk,
        batches_completed=batches_completed, trials_achieved=T_ach,
        achieved_equals_planned=(T_ach == args.trials),
        truncated_by_wall_budget=truncated,
        truncated_at_batch=truncated_at_batch,
        sub_chunks_block_partition_self_check_passed=sub_chunks_checked_total,
        self_check_note=("Every one of the above sub-chunks passed the "
                         "F == block_fail assertion in run_batch(); a single "
                         "failure would have aborted the run (fail-closed, "
                         "design.md Section 3 step 5)."),
        seed_derivation=f"{SEED_PREFIX}|batch|<i>, SHA-256, first 8 bytes big-endian",
        first_5_batch_seeds=[int(s) for s in batch_seeds[:5]])
    if truncated:
        R["validity"] = dict(
            status="invalid_measurement",
            reason=(f"Wall-clock budget forced truncation at batch "
                    f"{truncated_at_batch}/{args.batches} "
                    f"({T_ach}/{args.trials} trials achieved). This is an "
                    f"INFRASTRUCTURE/BUDGET outcome, never a negative "
                    f"observation (AGENTS.md rule 5)."))
        json.dump(R, open(os.path.join(args.out_dir, "planted_results.json"), "w"),
                  indent=1)
        raise SystemExit("INFRASTRUCTURE: wall-clock budget exhausted before "
                         "the planned T was reached")

    # ---------------- phase 4: estimator + jackknife (REUSED VERBATIM) -----
    # The following block reproduces measure.py lines 730-739 verbatim
    # (variable names retained: bh, hist, point, loo, jmean, jse), applied to
    # THIS arm's own histograms. See comparison_report.md for the line-by-
    # line citation.
    cw0 = time.time(); cc0 = core_seconds()
    hist = bh.sum(axis=0)
    point = measure.log2_A_from_hists(hist[None, :], n_e, ks, C)[0]
    loo = np.array([measure.log2_A_from_hists((hist - bh[i])[None, :], n_e, ks, C)[0]
                    for i in range(args.batches)])
    jmean = loo.mean(axis=0)
    jse = np.sqrt((args.batches - 1) / args.batches
                  * ((loo - jmean) ** 2).sum(axis=0))
    # -------- end verbatim block --------

    ssum = float((hist.astype(np.float64) * np.arange(n_e + 1)).sum())
    q_meas = ssum / (T_ach * n_e)

    cells_out = []
    n_match = 0
    for j, k in enumerate(ks):
        v = float(point[j])
        se = float(jse[j])
        planted = law["cells"][k]["planted_log2_A_k"]
        lo, hi = v - MATCH_SE_MULTIPLIER * se, v + MATCH_SE_MULTIPLIER * se
        match = bool(lo <= planted <= hi) if math.isfinite(se) else None
        n_match += int(bool(match))
        cells_out.append(dict(
            k=k, is_prespecified_cell_parity_only=(k == M_PRESPEC),
            recovered_log2_Ahat_k=v,
            jackknife_se=se, jackknife_batches=args.batches,
            planted_log2_A_k=planted,
            interval_multiplier=MATCH_SE_MULTIPLIER,
            interval=[lo, hi],
            distance_planted_minus_recovered=planted - v,
            distance_in_jackknife_se=((planted - v) / se) if se > 0 else None,
            verdict=("MATCH" if match else "MISMATCH") if match is not None
                    else "UNDEFINED (non-finite jackknife SE)"))
    stage_end("estimator_and_jackknife_reused_verbatim", cw0, cc0)

    R["MEASUREMENT"] = dict(
        what="Recovered log2_Ahat_k on the planted-correlation control arm, "
             "against the closed-form planted value, using measure.py's own "
             "estimator and jackknife code applied to this arm's histogram.",
        estimator="REUSED VERBATIM from measure.py: log2_Ahat_k = "
                  "log2((sum_s C(s,k) H_s)/(T C(n_e,k))) - k log2((sum_s s H_s)/(T n_e))",
        comparison_rule=(f"MATCH iff planted_log2_A_k(k) is within "
                         f"[point_k - {MATCH_SE_MULTIPLIER:.0f}*jackknife_se_k, "
                         f"point_k + {MATCH_SE_MULTIPLIER:.0f}*jackknife_se_k]; "
                         f"adopted for this task per design.md Section 5, not "
                         f"a verbatim rule from measure.py."),
        T_achieved=T_ach, q_hat_measured=q_meas, q_planted_exact=law["q_float"],
        cells=cells_out, cells_reported=len(cells_out),
        cells_match=n_match, cells_mismatch=len(cells_out) - n_match)
    print(f"[MEASUREMENT] {n_match}/{len(cells_out)} cells MATCH within "
          f"{MATCH_SE_MULTIPLIER:.0f} jackknife SE", flush=True)

    # ---------------- close out --------------------------------------------
    spent = core_seconds() - c0
    wall = time.time() - t_wall0
    R["budget"] = dict(
        core_seconds_authorized=CORE_SECOND_BUDGET, core_seconds_spent=round(spent, 3),
        core_seconds_remaining=round(CORE_SECOND_BUDGET - spent, 3),
        within_core_second_budget=spent <= CORE_SECOND_BUDGET,
        wall_seconds=round(wall, 3), wall_authorized=WALL_BUDGET,
        within_wall_budget=wall <= WALL_BUDGET,
        peak_rss_mb_self=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0,
        stages=stages,
        subsample_used=False,
        subsample_note="No stage of this run was forced onto a subsample of "
                       "the planned T=1e7; achieved T equals planned T "
                       "(see generation.achieved_equals_planned).")
    ok = (R["reused_pipeline"]["integrity_check_passed"]
          and not mismatches
          and not truncated
          and R["generation"]["achieved_equals_planned"]
          and R["generation"]["sub_chunks_block_partition_self_check_passed"] > 0
          and spent <= CORE_SECOND_BUDGET and wall <= WALL_BUDGET)
    R["validity"] = dict(
        status="valid_measurement" if ok else "invalid_measurement",
        reason=("All fail-closed gates passed, T achieved equals T planned, "
                "and the run stayed within its core-second and wall-clock "
                "budget." if ok else "See gate/budget fields above."),
        scoped_to="ONE planted-correlation instance, order-matched to PS-R3's "
                  "n_e/n_2/dup/m, k=2..18, T=1e7, run through measure.py's "
                  "estimator/jackknife code unmodified. Claim tier: toy. "
                  "See design.md Section 3.2 for what this arm does NOT "
                  "exercise.")
    R["finished_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    out = os.path.join(args.out_dir, "planted_results.json")
    with open(out, "w") as fh:
        json.dump(R, fh, indent=1)
    print(f"[done] {out}  core-s={spent:.1f}/{CORE_SECOND_BUDGET} "
          f"wall={wall:.0f}s  validity={R['validity']['status']}", flush=True)
    return R


if __name__ == "__main__":
    main()
