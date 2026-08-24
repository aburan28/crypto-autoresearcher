#!/usr/bin/env python3
"""V3 planted-correlation control arm for EXP-HQC-982268 / OPEN-6.

TASK-20260806-e1700f (executor) / BATCH-f8050e / GOAL-HQC-001.

WHAT THIS IS
------------
A single-instrument check, NOT a measurement about HQC. It replaces V2's
(TASK-20260806-047535) two fixed, hand-searched, worst-case templates with a
genuinely heterogeneous per-position, per-trial content ensemble, built by
REJECTION SAMPLING: for every block position with intended label L, draw a
fresh 128-bit i.i.d. Bernoulli(0.35) candidate, decode it with the REAL
stage_a.py decode_blocks (sha256-pinned, unmodified), and accept it only if
the true decode matches L; otherwise redraw. This keeps S_t = M_t exactly
(design.md Section 2/3) while making the realized bit content genuinely
heterogeneous, unlike V2's {S_TEMPLATE, FAIL_TEMPLATE} pair.

TWO DISTINCT DELIVERABLES, produced by two separate --mode invocations:
  --mode main       -> planted_results.json: the same MATCH/MISMATCH check
                        against the closed-form log2_A_k(k) V1/V2 performed.
  --mode detection   -> detection_results.json: a SEPARATE experiment that
                        measures a boundary-shift defect DETECTION RATE (not
                        merely its possibility), with a confidence interval,
                        directly comparable to the Red Team's independently
                        measured ~8.8%/~19.6% natural flip-rate baselines
                        (EV-HQC-9a30d3, red_team_report.md Section 2).

See design.md for the full derivation, calibration, and honesty disclosures
(Section 7, including the un-closed rejection-sampling-bias question).

WHAT IT IS NOT
--------------
Not a statement about HQC, A17, A5, any decoding-failure rate, or any
standardized parameter set. Not a re-run of PS-R3. Not a full test of
stage_a.py's cryptographic (T)-sampler (CTRStream, fixed_weight_support,
ring_mul_sparse/dense are never invoked). Claim tier: TOY.

A timeout, crash, missing dependency or budget exhaustion is an
INFRASTRUCTURE outcome and is never evidence about the mathematics
(AGENTS.md rule 5).

FAIL-CLOSED INTEGRITY CHECKS
-----------------------------
Before importing measure.py or stage_a.py, this script hashes each and
ABORTS (SystemExit) if the hash does not match the pinned constant below.
The planted-law closed form is re-derived and checked against design.md's
frozen table. Every accepted block is individually verified (by
construction) against the real decode_blocks; the full-trial self-check
(F == block_fail) is asserted on every batch. A deliberate-mismatch dry run
demonstrating fail-closed abort is documented in run_manifest.yaml.

Re-run:
    PYTHONDONTWRITEBYTECODE=1 python3 planted_arm_v3.py --mode main --out-dir .
    PYTHONDONTWRITEBYTECODE=1 python3 planted_arm_v3.py --mode detection --out-dir .
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
STAGE_A_PY = os.path.join(
    REPO, "coordination", "goals", "GOAL-HQC-001", "batches", "BATCH-6fddee",
    "tasks", "TASK-20260806-64b506", "stage_a.py")

# sha256 of measure.py and stage_a.py, identical pins to V1/V2 (unchanged
# files, verified independently by this task at run time).
MEASURE_PY_EXPECTED_SHA256 = (
    "a4fd1ecb63f0ddc83c02ef45f2c65ab31cf13d13e7ae94f500e67465b24f5dc8")
STAGE_A_PY_EXPECTED_SHA256 = (
    "06a0a618432c00fe26c72ecf05a8d89489db61c5183931fdb76a378717681405")

TASK_ID = "TASK-20260806-e1700f"
SEED_PREFIX_MAIN = f"{TASK_ID}/PLANTED-ARM-V3/main/v1"
SEED_PREFIX_DETECTION = f"{TASK_ID}/PLANTED-ARM-V3/detection/v1"

# ---------------------------------------------------------------------------
# parameters -- order-matched to PS-R3 / V1 / V2 (design.md Section 1)
# ---------------------------------------------------------------------------
N_E = 56
N_2 = 128
DUP = 1
N = N_E * N_2                       # 7168
M_PRESPEC = 17                       # narrative parity only
K_MAX = 18
KS = list(range(2, K_MAX + 1))       # 17 cells, k = 2..18
N_JACK_BATCHES = 200
P_CONTENT = 0.35                     # Bernoulli(p) content proxy, design.md Section 3

SUPPORT = [17, 18, 19]
WEIGHTS = [Fraction(1, 3), Fraction(1, 3), Fraction(1, 3)]

# frozen table from design.md Section 2.1 -- identical to V1/V2's.
DESIGN_TABLE_LOG2_A = {
    2: -0.05332724412846135, 3: -0.16394044463458357, 4: -0.3363079856368989,
    5: -0.5755089290487359, 6: -0.8873624322504217, 7: -1.2785962698872737,
    8: -1.7570703364157492, 9: -2.3320793631074803, 10: -3.0147730405328055,
    11: -3.8187560346206517, 12: -4.76097481483005, 13: -5.8630844320447935,
    14: -7.153668398603774, 15: -8.672097148069227, 16: -10.47587716111893,
    17: -12.65660891751783, 18: -15.382583727766058,
}
DESIGN_Q = 0.32142857142857145

# T's, MATCH_SE_MULTIPLIER, budget allocation -- design.md Section 6.
T_MAIN_PLANNED = 500_000
SUB_CHUNK_MAIN = T_MAIN_PLANNED // N_JACK_BATCHES     # 2,500

T_DET_A_PLANNED = 2_000_000          # interior-position component, design.md 5.2
SUB_CHUNK_DET_A = 100_000
T_DET_B_PLANNED = 100_000            # full-ensemble component, design.md 5.3
SUB_CHUNK_DET_B = 2_500

MATCH_SE_MULTIPLIER = 3.0

CORE_SECOND_BUDGET_TOTAL = 1800.0
CORE_SECOND_BUDGET_MAIN = 1000.0
CORE_SECOND_BUDGET_DETECTION = 800.0
WALL_BUDGET_MAIN = 1800.0
WALL_BUDGET_DETECTION = 1500.0
WALL_AUTHORIZED_TOTAL = 3600.0

MARGIN_CONDITION_THRESHOLD = 4       # V2's templates' margin / Red Team's own
                                      # conditioning threshold, design.md 5.2
INTERIOR_POSITIONS = (9, 10)         # design.md Section 5.2
MAX_REJECTION_ROUNDS = 1000


# ---------------------------------------------------------------------------
# provenance helpers (identical pattern to V1/V2)
# ---------------------------------------------------------------------------

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def sha256_bits(bits) -> str:
    arr = np.asarray(bits, dtype=np.uint8)
    return hashlib.sha256(arr.tobytes()).hexdigest()


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


def derive_seed(prefix: str, purpose: str, n: int) -> int:
    s = f"{prefix}|{purpose}|{n}"
    return int.from_bytes(hashlib.sha256(s.encode()).digest()[:8], "big")


def load_module(path: str, expected_sha256: str, name: str, module_name: str):
    actual = sha256_file(path)
    if actual != expected_sha256:
        raise SystemExit(
            f"FAIL-CLOSED: {name} sha256 mismatch. expected={expected_sha256} "
            f"actual={actual}. This task reuses {name} read-only and refuses "
            f"to proceed if the file on disk differs from what design.md was "
            f"written against.")
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)                         # imported UNMODIFIED
    return mod, actual


# ---------------------------------------------------------------------------
# planted law: closed form (design.md Section 2, unchanged from V1/V2)
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


def check_planted_law_reproduction(law):
    mismatches = []
    for k in KS:
        if abs(law["cells"][k]["planted_log2_A_k"] - DESIGN_TABLE_LOG2_A[k]) > 1e-12:
            mismatches.append(k)
    if abs(law["q_float"] - DESIGN_Q) > 1e-15:
        mismatches.append("q")
    return mismatches


# ---------------------------------------------------------------------------
# position-marking mechanism (design.md Section 2, identical to V1/V2)
# ---------------------------------------------------------------------------

def draw_block_fail(rng: np.random.Generator, n_trials: int, n_e: int) -> np.ndarray:
    """Returns (n_trials, n_e) bool: intended F label per position per trial.
    M_t ~ Uniform{17,18,19}; uniform random M_t-subset of n_e positions."""
    m0 = rng.integers(SUPPORT[0], SUPPORT[-1] + 1, size=n_trials)
    keys = rng.random((n_trials, n_e))
    ranks = np.argsort(np.argsort(keys, axis=1), axis=1)
    return ranks < m0[:, None]


# ---------------------------------------------------------------------------
# rejection-sampling content construction (design.md Section 3)
# ---------------------------------------------------------------------------

def decode_single_blocks(decode_blocks_fn, blocks: np.ndarray, n_2: int = N_2,
                         dup: int = DUP):
    """blocks: (B,128) uint8, each an independent block. Uses the fact that
    decode_blocks decodes blocks independently (design.md Section 3.1): one
    B=1, n_e=B call is equivalent to B independent single-block decodes."""
    B = blocks.shape[0]
    F, W, ties = decode_blocks_fn(blocks.reshape(1, B * n_2), B, n_2, dup)
    return F.reshape(B), W.reshape(B), ties.reshape(B)


def rejection_sample_content(rng: np.random.Generator, labels_flat: np.ndarray,
                             decode_blocks_fn, p: float = P_CONTENT,
                             max_rounds: int = MAX_REJECTION_ROUNDS):
    """labels_flat: (B,) bool, intended F label per position. Returns
    (content (B,128) uint8, draws (B,) int64, rounds:int, total_decode_calls:int)
    -- design.md Section 3.1/3.2, vectorized redraw-only-rejected."""
    B = labels_flat.shape[0]
    content = np.empty((B, 128), dtype=np.uint8)
    pending = np.ones(B, dtype=bool)
    draws = np.zeros(B, dtype=np.int64)
    total_calls = 0
    rounds = 0
    while pending.any():
        rounds += 1
        if rounds > max_rounds:
            raise SystemExit(
                f"FAIL-CLOSED: rejection sampling exceeded {max_rounds} rounds "
                f"with {int(pending.sum())}/{B} blocks still pending -- "
                f"aborting rather than silently truncating (design.md Section 6).")
        idx_pending = np.flatnonzero(pending)
        n_pend = idx_pending.size
        cand = (rng.random((n_pend, 128)) < p).astype(np.uint8)
        Fc, _, _ = decode_single_blocks(decode_blocks_fn, cand)
        total_calls += n_pend
        ok = (Fc == labels_flat[idx_pending])
        acc = idx_pending[ok]
        content[acc] = cand[ok]
        draws[idx_pending] += 1
        pending[acc] = False
    return content, draws, rounds, total_calls


def generate_full_ensemble_batch(rng: np.random.Generator, n_trials: int,
                                 decode_blocks_fn):
    """design.md Section 4, steps 1-3: full 56-position rejection-sampled
    trial batch. Returns (bits (n_trials,N) uint8, block_fail (n_trials,n_e)
    bool, draws (n_trials*n_e,) int64, rounds:int, total_calls:int)."""
    block_fail = draw_block_fail(rng, n_trials, N_E)
    flat_labels = block_fail.reshape(-1)
    content, draws, rounds, calls = rejection_sample_content(
        rng, flat_labels, decode_blocks_fn)
    bits = content.reshape(n_trials, N)
    return bits, block_fail, draws, rounds, calls


def margin_batch(sa_mod, blocks: np.ndarray) -> np.ndarray:
    """(B,128) uint8 -> (B,) int, top1-top2 |WHT coefficient| gap. Reuses
    stage_a.py's wht128 directly, sha256-pinned (design.md Section 5.2 step 3)."""
    v = (1 - 2 * blocks.astype(np.int32))
    t = sa_mod.wht128(v.copy())
    av = np.abs(t)
    part = np.partition(av, -2, axis=1)
    return (part[:, -1] - part[:, -2]).astype(np.int64)


def shift_read_one_early_batch(blocks: np.ndarray, foreign_last_bit: np.ndarray) -> np.ndarray:
    """(B,128) uint8, (B,) uint8 -> (B,128) uint8. design.md Section 5.1,
    identical definition to V2's shift_read_one_early, vectorized over B."""
    out = np.empty_like(blocks)
    out[:, 0] = foreign_last_bit
    out[:, 1:] = blocks[:, :-1]
    return out


def distinct_check(content_sample: np.ndarray) -> dict:
    """design.md Section 3.3: confirms the ensemble is genuinely
    heterogeneous, not a disguised small fixed set."""
    flat = np.ascontiguousarray(content_sample)
    view = flat.view([("", flat.dtype)] * flat.shape[1]).reshape(-1)
    uniq = np.unique(view)
    n = content_sample.shape[0]
    return dict(sample_size=int(n), distinct_values=int(uniq.shape[0]),
               duplicate_fraction=1.0 - uniq.shape[0] / n if n else None)


def wilson_and_normal_ci(k: int, n: int) -> dict:
    if n == 0:
        return dict(k=0, n=0, phat=None, se_normal_approx=None,
                   wilson95_lo=None, wilson95_hi=None,
                   normal_3se_lo=None, normal_3se_hi=None)
    phat = k / n
    se = math.sqrt(max(phat * (1 - phat), 0.0) / n)
    z95 = 1.959963984540054
    denom = 1 + z95 ** 2 / n
    center = (phat + z95 ** 2 / (2 * n)) / denom
    half = (z95 * math.sqrt(phat * (1 - phat) / n + z95 ** 2 / (4 * n ** 2))) / denom
    return dict(k=int(k), n=int(n), phat=phat, se_normal_approx=se,
               wilson95_lo=center - half, wilson95_hi=center + half,
               normal_3se_lo=phat - 3 * se, normal_3se_hi=phat + 3 * se)


# ---------------------------------------------------------------------------
# provenance/report scaffolding shared by both modes
# ---------------------------------------------------------------------------

def base_record(mode: str) -> dict:
    return {
        "task_id": TASK_ID,
        "role": "executor",
        "experiment_id": "EXP-HQC-982268",
        "hypothesis_id": "H-HQC-18d1b4",
        "goal": "GOAL-HQC-001",
        "batch": "BATCH-f8050e",
        "mode": mode,
        "claim_tier": "toy",
        "design_doc": "design.md (written and frozen before this run; see "
                      "run_manifest.yaml for the file-timestamp ordering "
                      "evidence)",
        "started_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def load_pipeline(R):
    measure, measure_sha = load_module(MEASURE_PY, MEASURE_PY_EXPECTED_SHA256,
                                       "measure.py", "measure_frozen_v3")
    sa, sa_sha = load_module(STAGE_A_PY, STAGE_A_PY_EXPECTED_SHA256,
                             "stage_a.py", "stage_a_frozen_v3")
    R["reused_pipeline"] = dict(
        measure_py=dict(
            source_path=os.path.relpath(MEASURE_PY, REPO),
            source_task="TASK-20260806-cde749",
            sha256_expected=MEASURE_PY_EXPECTED_SHA256, sha256_actual=measure_sha,
            integrity_check_passed=(measure_sha == MEASURE_PY_EXPECTED_SHA256),
            reused_symbols=["comb_matrix", "log2_A_from_hists", "N_JACK_BATCHES",
                            "jackknife/batch-histogram computation (lines "
                            "730-739, copied verbatim with local variable names)"]),
        stage_a_py=dict(
            source_path=os.path.relpath(STAGE_A_PY, REPO),
            source_task="TASK-20260806-64b506",
            sha256_expected=STAGE_A_PY_EXPECTED_SHA256, sha256_actual=sa_sha,
            integrity_check_passed=(sa_sha == STAGE_A_PY_EXPECTED_SHA256),
            reused_symbols=["decode_blocks (line 286, called directly on "
                            "every accepted block AND every assembled "
                            "trial, not reimplemented)",
                            "wht128 (line 270, called directly for margin "
                            "computation, and internally by decode_blocks)"],
            not_reused_symbols=["CTRStream", "fixed_weight_support",
                                "ring_mul_sparse", "ring_mul_dense",
                                "support_to_int*", "rm17_codewords",
                                "brute_force_decode (design.md Section 8: "
                                "not needed here -- every accepted block is "
                                "individually decode-verified at generation "
                                "time, a per-block guarantee stronger than "
                                "V2's per-template one)",
                                "_t_shard", "_null_m_shard",
                                "every phase_* function", "main"]))
    if measure.N_JACK_BATCHES != N_JACK_BATCHES:
        raise SystemExit("FAIL-CLOSED: N_JACK_BATCHES mismatch between this "
                         "task's constant and measure.py's.")
    return measure, sa


def check_and_record_planted_law(R):
    law = planted_law()
    mismatches = check_planted_law_reproduction(law)
    R["planted_law"] = dict(
        construction="design.md Section 2: M_t ~ Uniform{17,18,19}, blocks "
                     "chosen as a uniform random size-M_t subset of n_e=56 "
                     "POSITIONS; S_t = M_t exactly. Content per position is "
                     "REJECTION-SAMPLED from Bernoulli(0.35), conditioned "
                     "only on matching the position's intended label; this "
                     "does not change the marginal law of S_t (design.md "
                     "Section 0/2).",
        support=SUPPORT, weights=["1/3", "1/3", "1/3"],
        q_exact=law["q_exact"], q_float=law["q_float"],
        cells=[law["cells"][k] for k in KS],
        design_md_reproduction_check=dict(
            mismatched_keys=mismatches,
            verdict="PASS" if not mismatches else "FAIL"))
    return law, mismatches


def write_json(obj, path):
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=1, default=str)


# ---------------------------------------------------------------------------
# mode: main (design.md Section 4)
# ---------------------------------------------------------------------------

def run_main(args):
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

    R = base_record("main")
    R["what_this_is"] = (
        "V3 planted-correlation control arm, MAIN RUN (MATCH/MISMATCH "
        "deliverable). Content at every one of n_e=56 positions in every "
        "trial is rejection-sampled from Bernoulli(0.35), individually "
        "verified against the REAL decode_blocks to match its intended "
        "label before use -- genuinely heterogeneous, unlike V2's two "
        "fixed templates. Reports MATCH/MISMATCH per k -- observations "
        "only, no conclusion about A17, HQC's DFR, or any standardized "
        "parameter set.")

    cw0 = time.time(); cc0 = core_seconds()
    R["git"] = git_state()
    R["environment"] = dict(
        python=sys.version.split()[0], numpy=np.__version__,
        platform=platform.platform(), processor=platform.machine(),
        cpu_count=os.cpu_count())
    stage_end("provenance", cw0, cc0)

    cw0 = time.time(); cc0 = core_seconds()
    measure, sa = load_pipeline(R)
    stage_end("fail_closed_integrity_and_import", cw0, cc0)

    cw0 = time.time(); cc0 = core_seconds()
    law, mismatches = check_and_record_planted_law(R)
    if mismatches:
        R["validity"] = dict(status="failed_implementation",
                             reason=f"recomputed planted law diverges from "
                                    f"design.md's frozen table at {mismatches}")
        write_json(R, os.path.join(args.out_dir, "planted_results.json"))
        raise SystemExit("FAIL-CLOSED: planted-law reproduction check failed")
    print(f"[law] q={law['q_float']:.6f}, {len(KS)} cells, design.md "
          f"reproduction PASS", flush=True)
    stage_end("planted_law_derivation", cw0, cc0)

    n_e, n_2, dup = N_E, N_2, DUP
    L = N // n_e
    if L != n_2:
        raise SystemExit(f"FAIL-CLOSED: L=N/n_e={L} != N_2={n_2}.")
    C = measure.comb_matrix(n_e, KS)

    cw0 = time.time(); cc0 = core_seconds()
    bh = np.zeros((args.batches, n_e + 1), dtype=np.int64)
    batch_seeds = []
    total_ties = 0
    total_decode_calls_rejection = 0
    total_draws_sum = 0
    total_draws_count = 0
    max_draws_seen = 0
    truncated = False
    truncated_at_batch = None
    sample_content_for_distinct_check = None
    for i in range(args.batches):
        if time.time() - t_wall0 > WALL_BUDGET_MAIN - 60:
            truncated = True
            truncated_at_batch = i
            print(f"[budget] wall-clock budget nearly exhausted at batch {i}/"
                  f"{args.batches}; stopping (INFRASTRUCTURE outcome, not a "
                  f"result).", flush=True)
            break
        seed = derive_seed(SEED_PREFIX_MAIN, "batch", i)
        batch_seeds.append(seed)
        rng = np.random.Generator(np.random.PCG64(seed))
        bits, block_fail, draws, rounds, calls = generate_full_ensemble_batch(
            rng, args.sub_chunk, sa.decode_blocks)
        total_decode_calls_rejection += calls
        total_draws_sum += int(draws.sum())
        total_draws_count += draws.size
        max_draws_seen = max(max_draws_seen, int(draws.max()))

        if i == 0:
            sample_content_for_distinct_check = bits.reshape(
                args.sub_chunk * n_e, 128)[:10000].copy()

        F, W, ties = sa.decode_blocks(bits, n_e, n_2, dup)
        if not np.array_equal(F, block_fail):
            n_mismatch = int(np.count_nonzero(F != block_fail))
            R["validity"] = dict(
                status="failed_implementation",
                reason=(f"FAIL-CLOSED: block-partition/real-decode "
                        f"self-check failed at batch {i} -- the REAL "
                        f"decode_blocks output disagrees with the planted "
                        f"block_fail pattern on {n_mismatch}/"
                        f"{block_fail.size} block decisions, despite every "
                        f"accepted block having been individually verified "
                        f"at rejection-sampling time. This would indicate "
                        f"decode_blocks is not block-independent under this "
                        f"arm's call pattern -- itself a reportable "
                        f"finding. Aborting."))
            write_json(R, os.path.join(args.out_dir, "planted_results.json"))
            raise SystemExit("FAIL-CLOSED: full-trial self-check failed")
        total_ties += int(ties.sum())
        S = F.sum(axis=1)
        bh[i] = np.bincount(S, minlength=n_e + 1)[:n_e + 1]
        if i % 20 == 0 or i == args.batches - 1:
            print(f"[batch] {i + 1}/{args.batches} done, cum core-s="
                  f"{core_seconds() - c0:.1f}, mean_draws_so_far="
                  f"{total_draws_sum / max(total_draws_count,1):.3f}", flush=True)
    stage_end("rejection_sample_generation_and_self_check", cw0, cc0)

    batches_completed = args.batches if not truncated else truncated_at_batch
    T_ach = int(bh[:batches_completed].sum())
    distinct = distinct_check(sample_content_for_distinct_check) \
        if sample_content_for_distinct_check is not None else None
    R["generation"] = dict(
        n_e=n_e, N=N, n_2=n_2, dup=dup, L=L,
        L_formula="L = N // n_e (RULE-2 corrected; NOT n_2*dup)",
        real_decode_blocks_used=True,
        content_distribution="i.i.d. Bernoulli(0.35) per bit, rejection-"
                             "sampled per position/trial conditioned on "
                             "matching the intended decode label "
                             "(design.md Section 3)",
        trials_planned=args.trials, batches_planned=args.batches,
        trials_per_batch=args.sub_chunk,
        batches_completed=batches_completed, trials_achieved=T_ach,
        achieved_equals_planned=(T_ach == args.trials),
        truncated_by_wall_budget=truncated,
        truncated_at_batch=truncated_at_batch,
        rejection_sampling_stats=dict(
            total_decode_calls=total_decode_calls_rejection,
            total_positions=total_draws_count,
            mean_draws_per_accepted_block=(total_draws_sum / total_draws_count
                                           if total_draws_count else None),
            max_draws_observed_any_block=max_draws_seen,
            note="mean draws per accepted block ~2.38 expected from "
                 "design.md Section 3.2's calibration; reported here as "
                 "the actual authorized-run measurement, which is itself "
                 "the finding about how 'natural' vs. 'searched' this "
                 "ensemble is."),
        ensemble_distinctness_check=distinct,
        block_partition_self_check_note=(
            "Every completed batch passed the F == block_fail assertion, "
            "computed by the REAL decode_blocks on the FULL assembled "
            "56-block trial; a single failure would have aborted the run "
            "(fail-closed, design.md Section 4 step 5)."),
        ties_observed_total=total_ties,
        seed_derivation=f"{SEED_PREFIX_MAIN}|batch|<i>, SHA-256, first 8 "
                        f"bytes big-endian",
        first_5_batch_seeds=[int(s) for s in batch_seeds[:5]])
    if truncated:
        R["validity"] = dict(
            status="invalid_measurement",
            reason=(f"Wall-clock budget forced truncation at batch "
                    f"{truncated_at_batch}/{args.batches} "
                    f"({T_ach}/{args.trials} trials achieved). This is an "
                    f"INFRASTRUCTURE/BUDGET outcome, never a negative "
                    f"observation (AGENTS.md rule 5)."))
        write_json(R, os.path.join(args.out_dir, "planted_results.json"))
        raise SystemExit("INFRASTRUCTURE: wall-clock budget exhausted before "
                         "the planned T was reached")

    cw0 = time.time(); cc0 = core_seconds()
    hist = bh.sum(axis=0)
    point = measure.log2_A_from_hists(hist[None, :], n_e, KS, C)[0]
    loo = np.array([measure.log2_A_from_hists((hist - bh[i])[None, :], n_e, KS, C)[0]
                    for i in range(args.batches)])
    jmean = loo.mean(axis=0)
    jse = np.sqrt((args.batches - 1) / args.batches
                  * ((loo - jmean) ** 2).sum(axis=0))

    ssum = float((hist.astype(np.float64) * np.arange(n_e + 1)).sum())
    q_meas = ssum / (T_ach * n_e)

    cells_out = []
    n_match = 0
    for j, k in enumerate(KS):
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
        what="Recovered log2_Ahat_k on the V3 rejection-sampled "
             "heterogeneous-ensemble planted-correlation control arm, "
             "against the closed-form planted value, using measure.py's "
             "own estimator and jackknife code applied to this arm's "
             "histogram (built from the REAL decode_blocks output on "
             "genuinely heterogeneous per-position content).",
        estimator="REUSED VERBATIM from measure.py: log2_Ahat_k = "
                  "log2((sum_s C(s,k) H_s)/(T C(n_e,k))) - k log2((sum_s s H_s)/(T n_e))",
        comparison_rule=(f"MATCH iff planted_log2_A_k(k) is within "
                         f"[point_k - {MATCH_SE_MULTIPLIER:.0f}*jackknife_se_k, "
                         f"point_k + {MATCH_SE_MULTIPLIER:.0f}*jackknife_se_k]; "
                         f"identical rule to V1/V2, design.md Section 4."),
        T_achieved=T_ach, q_hat_measured=q_meas, q_planted_exact=law["q_float"],
        cells=cells_out, cells_reported=len(cells_out),
        cells_match=n_match, cells_mismatch=len(cells_out) - n_match)
    print(f"[MEASUREMENT] {n_match}/{len(cells_out)} cells MATCH within "
          f"{MATCH_SE_MULTIPLIER:.0f} jackknife SE", flush=True)

    spent = core_seconds() - c0
    wall = time.time() - t_wall0
    R["budget"] = dict(
        core_seconds_allocated=CORE_SECOND_BUDGET_MAIN,
        core_seconds_authorized_total_task=CORE_SECOND_BUDGET_TOTAL,
        core_seconds_spent=round(spent, 3),
        core_seconds_remaining_in_allocation=round(CORE_SECOND_BUDGET_MAIN - spent, 3),
        within_core_second_allocation=spent <= CORE_SECOND_BUDGET_MAIN,
        wall_seconds=round(wall, 3), wall_allocated=WALL_BUDGET_MAIN,
        within_wall_allocation=wall <= WALL_BUDGET_MAIN,
        peak_rss_mb_self=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0,
        stages=stages)
    ok = (R["reused_pipeline"]["measure_py"]["integrity_check_passed"]
          and R["reused_pipeline"]["stage_a_py"]["integrity_check_passed"]
          and not mismatches
          and not truncated
          and R["generation"]["achieved_equals_planned"]
          and spent <= CORE_SECOND_BUDGET_MAIN and wall <= WALL_BUDGET_MAIN)
    R["validity"] = dict(
        status="valid_measurement" if ok else "invalid_measurement",
        reason=("All fail-closed gates passed (measure.py/stage_a.py "
                "integrity, planted-law reproduction, per-batch "
                "block-partition self-check), T achieved equals T "
                "planned, and the run stayed within its allocated "
                "core-second and wall-clock budget." if ok
                else "See gate/budget fields above."),
        scoped_to="ONE V3 planted-correlation instance, order-matched to "
                  "PS-R3's n_e/n_2/dup/m, k=2..18, real decode_blocks, "
                  "REJECTION-SAMPLED heterogeneous content, "
                  f"T={T_ach}. Claim tier: toy. See design.md Section 7 "
                  "for what this arm does NOT exercise.")
    R["finished_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    out = os.path.join(args.out_dir, "planted_results.json")
    write_json(R, out)
    print(f"[done] {out}  core-s={spent:.1f}/{CORE_SECOND_BUDGET_MAIN} "
          f"wall={wall:.0f}s  validity={R['validity']['status']}", flush=True)
    return R


# ---------------------------------------------------------------------------
# mode: detection (design.md Section 5)
# ---------------------------------------------------------------------------

def run_detection(args):
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

    R = base_record("detection")
    R["what_this_is"] = (
        "V3 planted-correlation control arm, DETECTION-RATE EXPERIMENT "
        "(separate from the MAIN MATCH/MISMATCH run). Measures the "
        "FRACTION of positions whose decoded label flips under the "
        "campaign's V1/V3 boundary-index-shift 'read one index early' "
        "perturbation, applied to the SAME rejection-sampled heterogeneous "
        "ensemble the main run uses, with a confidence interval -- directly "
        "comparable to the Red Team's independently measured ~8.8% "
        "(unconditional) / ~19.6% (margin<=4-conditioned) natural flip-rate "
        "baselines (EV-HQC-9a30d3, red_team_report.md Section 2).")

    cw0 = time.time(); cc0 = core_seconds()
    R["git"] = git_state()
    R["environment"] = dict(
        python=sys.version.split()[0], numpy=np.__version__,
        platform=platform.platform(), processor=platform.machine(),
        cpu_count=os.cpu_count())
    stage_end("provenance", cw0, cc0)

    cw0 = time.time(); cc0 = core_seconds()
    measure, sa = load_pipeline(R)
    stage_end("fail_closed_integrity_and_import", cw0, cc0)

    cw0 = time.time(); cc0 = core_seconds()
    law, mismatches = check_and_record_planted_law(R)
    if mismatches:
        R["validity"] = dict(status="failed_implementation",
                             reason=f"recomputed planted law diverges from "
                                    f"design.md's frozen table at {mismatches}")
        write_json(R, os.path.join(args.out_dir, "detection_results.json"))
        raise SystemExit("FAIL-CLOSED: planted-law reproduction check failed")
    stage_end("planted_law_derivation", cw0, cc0)

    RED_TEAM_BASELINE = dict(
        unconditional=0.088, margin_conditioned=0.196,
        margin_threshold=MARGIN_CONDITION_THRESHOLD,
        source="EV-HQC-9a30d3 / red_team_report.md Section 2 "
               "(TASK-20260806-ae74c4), 300,000-sample Bernoulli(0.35) "
               "natural single-position read-one-early flip-rate "
               "measurement against V2's construction")
    R["red_team_baseline_v2"] = RED_TEAM_BASELINE

    # ---------------- Component A: interior single-position rate --------
    cw0 = time.time(); cc0 = core_seconds()
    pos_a, pos_b = INTERIOR_POSITIONS       # position_b is the target (10),
                                            # position_a is its predecessor (9)
    total_A = 0
    flips_paired = 0
    flips_indep = 0
    flips_paired_margin = 0
    n_margin = 0
    flips_indep_margin = 0
    margins_all = []
    a_batches = 0
    a_truncated = False
    n_a_batches_planned = -(-args.trials_a // args.sub_chunk_a)  # ceil div
    for i in range(n_a_batches_planned):
        if time.time() - t_wall0 > WALL_BUDGET_DETECTION - 90:
            a_truncated = True
            print(f"[budget] wall-clock budget nearly exhausted during "
                  f"Component A at batch {i}; stopping.", flush=True)
            break
        n_trials_this = min(args.sub_chunk_a, args.trials_a - total_A)
        if n_trials_this <= 0:
            break
        seed = derive_seed(SEED_PREFIX_DETECTION, "detA_batch", i)
        rng = np.random.Generator(np.random.PCG64(seed))
        block_fail_full = draw_block_fail(rng, n_trials_this, N_E)
        labels_a = block_fail_full[:, pos_a]
        labels_b = block_fail_full[:, pos_b]
        content_a, draws_a, _, _ = rejection_sample_content(
            rng, labels_a, sa.decode_blocks)
        content_b, draws_b, _, _ = rejection_sample_content(
            rng, labels_b, sa.decode_blocks)

        margins = margin_batch(sa, content_b)
        margins_all.append(margins)

        # paired_neighbor: foreign bit = position a's own accepted last bit
        foreign_paired = content_a[:, -1]
        perturbed_paired = shift_read_one_early_batch(content_b, foreign_paired)
        F_paired, _, _ = decode_single_blocks(sa.decode_blocks, perturbed_paired)
        flip_paired = (F_paired != labels_b)

        # independent_foreign_bit: fresh, unconditioned Bernoulli(0.35) draw
        foreign_indep = (rng.random(n_trials_this) < P_CONTENT).astype(np.uint8)
        perturbed_indep = shift_read_one_early_batch(content_b, foreign_indep)
        F_indep, _, _ = decode_single_blocks(sa.decode_blocks, perturbed_indep)
        flip_indep = (F_indep != labels_b)

        margin_mask = margins <= MARGIN_CONDITION_THRESHOLD

        total_A += n_trials_this
        flips_paired += int(flip_paired.sum())
        flips_indep += int(flip_indep.sum())
        n_margin += int(margin_mask.sum())
        flips_paired_margin += int((flip_paired & margin_mask).sum())
        flips_indep_margin += int((flip_indep & margin_mask).sum())
        a_batches += 1
        if i % 5 == 0:
            print(f"[detA] batch {i+1}/{n_a_batches_planned} total_A={total_A} "
                  f"cum core-s={core_seconds()-c0:.1f}", flush=True)
    stage_end("component_A_interior_position", cw0, cc0)

    margins_concat = np.concatenate(margins_all) if margins_all else np.array([], dtype=np.int64)
    comp_a = dict(
        positions=dict(target=pos_b, neighbor=pos_a),
        T_achieved=total_A, truncated_by_wall_budget=a_truncated,
        target_block_margin_stats=dict(
            min=int(margins_concat.min()) if margins_concat.size else None,
            median=float(np.median(margins_concat)) if margins_concat.size else None,
            mean=float(margins_concat.mean()) if margins_concat.size else None,
            max=int(margins_concat.max()) if margins_concat.size else None,
            fraction_margin_le_threshold=(float(n_margin) / total_A
                                          if total_A else None),
            threshold=MARGIN_CONDITION_THRESHOLD,
            red_team_v2_unconditioned_comparison=dict(
                min=0, median=8.0, mean=10.70, max=60,
                fraction_margin_le_4=0.388,
                source="red_team_report.md Section 2, UNCONDITIONED "
                       "Bernoulli(0.35), no rejection sampling"),
            honesty_note="This arm's content is rejection-sampled "
                         "(conditioned on matching the intended decode "
                         "label); the Red Team's figures are from an "
                         "UNCONDITIONED Bernoulli(0.35) draw. A "
                         "difference between these two margin "
                         "distributions is the expected, disclosed "
                         "signature of rejection-sampling conditioning "
                         "(design.md Section 7.2 item 3), not necessarily "
                         "an error."),
        paired_neighbor=dict(
            description="foreign bit = neighbor position's own accepted "
                        "(rejection-sampled) last bit, same trial -- the "
                        "ensemble-faithful variant",
            unconditional=wilson_and_normal_ci(flips_paired, total_A),
            margin_conditioned=wilson_and_normal_ci(flips_paired_margin, n_margin)),
        independent_foreign_bit=dict(
            description="foreign bit = fresh, unconditioned Bernoulli(0.35) "
                        "draw -- replicates the Red Team's own stated "
                        "methodology as closely as this arm's record of it "
                        "allows",
            unconditional=wilson_and_normal_ci(flips_indep, total_A),
            margin_conditioned=wilson_and_normal_ci(flips_indep_margin, n_margin)),
    )
    print(f"[detA] T={total_A} paired_neighbor unconditional phat="
          f"{comp_a['paired_neighbor']['unconditional']['phat']:.4f}  "
          f"independent_foreign_bit unconditional phat="
          f"{comp_a['independent_foreign_bit']['unconditional']['phat']:.4f}",
          flush=True)

    # ---------------- Component B: full-ensemble global / last-block -----
    cw0 = time.time(); cc0 = core_seconds()
    total_B = 0
    global_flips = 0
    global_total_positions = 0
    lastblock_flips = 0
    b_truncated = False
    n_b_batches_planned = -(-args.trials_b // args.sub_chunk_b)
    for i in range(n_b_batches_planned):
        if time.time() - t_wall0 > WALL_BUDGET_DETECTION - 30:
            b_truncated = True
            print(f"[budget] wall-clock budget nearly exhausted during "
                  f"Component B at batch {i}; stopping.", flush=True)
            break
        n_trials_this = min(args.sub_chunk_b, args.trials_b - total_B)
        if n_trials_this <= 0:
            break
        seed = derive_seed(SEED_PREFIX_DETECTION, "detB_batch", i)
        rng = np.random.Generator(np.random.PCG64(seed))
        bits, block_fail, draws, rounds, calls = generate_full_ensemble_batch(
            rng, n_trials_this, sa.decode_blocks)
        content = bits.reshape(n_trials_this, N_E, N_2)

        # self-check: unperturbed content must match intended labels
        F0, _, _ = sa.decode_blocks(bits, N_E, N_2, DUP)
        if not np.array_equal(F0, block_fail):
            n_mismatch = int(np.count_nonzero(F0 != block_fail))
            R["validity"] = dict(
                status="failed_implementation",
                reason=f"Component B self-check failed at batch {i}: "
                       f"{n_mismatch} mismatches. Aborting.")
            write_json(R, os.path.join(args.out_dir, "detection_results.json"))
            raise SystemExit("FAIL-CLOSED: Component B self-check failed")

        # global: every position's foreign bit = predecessor's own last bit
        # (circular, matching the V1-named "global off-by-one" class,
        # design.md Section 5.3).
        perturbed_global = np.empty_like(content)
        perturbed_global[:, :, 1:] = content[:, :, :-1]
        foreign_last = np.roll(content[:, :, -1], shift=1, axis=1)
        perturbed_global[:, :, 0] = foreign_last
        Fg, _, _ = sa.decode_blocks(
            perturbed_global.reshape(n_trials_this, N), N_E, N_2, DUP)
        flip_g = (Fg != block_fail)
        global_flips += int(flip_g.sum())
        global_total_positions += flip_g.size

        # last-block-only: only position 55 perturbed (V3-named class).
        perturbed_lb = content[:, N_E - 1, :].copy()
        foreign_lb = content[:, N_E - 2, -1]
        perturbed_lb = shift_read_one_early_batch(perturbed_lb, foreign_lb)
        F_lb, _, _ = decode_single_blocks(sa.decode_blocks, perturbed_lb)
        flip_lb = (F_lb != block_fail[:, N_E - 1])
        lastblock_flips += int(flip_lb.sum())

        total_B += n_trials_this
        if i % 5 == 0:
            print(f"[detB] batch {i+1}/{n_b_batches_planned} total_B={total_B} "
                  f"cum core-s={core_seconds()-c0:.1f}", flush=True)
    stage_end("component_B_full_ensemble", cw0, cc0)

    comp_b = dict(
        T_achieved=total_B, truncated_by_wall_budget=b_truncated,
        global_offbyone=dict(
            description="V1-named class: shift_read_one_early applied to "
                        "EVERY one of the 56 positions simultaneously "
                        "(circular; foreign bit = predecessor position's "
                        "own accepted last bit, same trial)",
            n_position_observations=global_total_positions,
            n_trials=total_B,
            rate=wilson_and_normal_ci(global_flips, global_total_positions)),
        last_block_early=dict(
            description="V3-named class: shift_read_one_early applied only "
                        "to position 55 (foreign bit = position 54's own "
                        "accepted last bit, same trial)",
            n_trials=total_B,
            rate=wilson_and_normal_ci(lastblock_flips, total_B)),
    )
    print(f"[detB] T={total_B} global phat="
          f"{comp_b['global_offbyone']['rate']['phat']:.4f} "
          f"last_block phat={comp_b['last_block_early']['rate']['phat']:.4f}",
          flush=True)

    R["component_A_interior_position"] = comp_a
    R["component_B_full_ensemble"] = comp_b

    spent = core_seconds() - c0
    wall = time.time() - t_wall0
    R["budget"] = dict(
        core_seconds_allocated=CORE_SECOND_BUDGET_DETECTION,
        core_seconds_authorized_total_task=CORE_SECOND_BUDGET_TOTAL,
        core_seconds_spent=round(spent, 3),
        core_seconds_remaining_in_allocation=round(CORE_SECOND_BUDGET_DETECTION - spent, 3),
        within_core_second_allocation=spent <= CORE_SECOND_BUDGET_DETECTION,
        wall_seconds=round(wall, 3), wall_allocated=WALL_BUDGET_DETECTION,
        within_wall_allocation=wall <= WALL_BUDGET_DETECTION,
        peak_rss_mb_self=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0,
        stages=stages)

    ok = (R["reused_pipeline"]["measure_py"]["integrity_check_passed"]
          and R["reused_pipeline"]["stage_a_py"]["integrity_check_passed"]
          and not mismatches
          and not a_truncated and not b_truncated
          and spent <= CORE_SECOND_BUDGET_DETECTION and wall <= WALL_BUDGET_DETECTION)
    R["validity"] = dict(
        status="valid_measurement" if ok else "invalid_measurement",
        reason=("All fail-closed gates passed, neither component was "
                "wall-clock-truncated, and the run stayed within its "
                "allocated core-second and wall-clock budget." if ok
                else "See component/budget fields above; a truncated "
                     "component's T_achieved and rate are still reported, "
                     "as an honestly smaller-sample measurement, not "
                     "discarded (AGENTS.md rule 5)."),
        scoped_to="ONE V3 detection-rate experiment: Component A "
                  f"(T={total_A}, positions {pos_a}/{pos_b}), Component B "
                  f"(T={total_B}, full 56-position ensemble). Claim tier: "
                  "toy. See design.md Section 5.4/7 for what this does "
                  "NOT establish.")
    R["finished_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    out = os.path.join(args.out_dir, "detection_results.json")
    write_json(R, out)
    print(f"[done] {out}  core-s={spent:.1f}/{CORE_SECOND_BUDGET_DETECTION} "
          f"wall={wall:.0f}s  validity={R['validity']['status']}", flush=True)
    return R


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["main", "detection"], required=True)
    ap.add_argument("--out-dir", default=HERE)
    ap.add_argument("--trials", type=int, default=T_MAIN_PLANNED,
                    help="mode=main: total planted trials")
    ap.add_argument("--batches", type=int, default=N_JACK_BATCHES,
                    help="mode=main: jackknife batches")
    ap.add_argument("--trials-a", type=int, default=T_DET_A_PLANNED,
                    help="mode=detection: Component A total trials")
    ap.add_argument("--sub-chunk-a", type=int, default=SUB_CHUNK_DET_A,
                    help="mode=detection: Component A batch size")
    ap.add_argument("--trials-b", type=int, default=T_DET_B_PLANNED,
                    help="mode=detection: Component B total trials")
    ap.add_argument("--sub-chunk-b", type=int, default=SUB_CHUNK_DET_B,
                    help="mode=detection: Component B batch size")
    args = ap.parse_args(argv)

    if args.mode == "main":
        if args.trials % args.batches != 0:
            raise SystemExit("FAIL-CLOSED: --trials must divide evenly into "
                             "--batches (design.md Section 4).")
        args.sub_chunk = args.trials // args.batches
        return run_main(args)
    else:
        return run_detection(args)


if __name__ == "__main__":
    main()
