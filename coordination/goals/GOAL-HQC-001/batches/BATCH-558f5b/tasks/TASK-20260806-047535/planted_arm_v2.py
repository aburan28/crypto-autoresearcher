#!/usr/bin/env python3
"""V2 planted-correlation control arm for EXP-HQC-982268 / OPEN-6.

TASK-20260806-047535 (executor) / BATCH-558f5b / GOAL-HQC-001.

WHAT THIS IS
------------
A single-run instrument check, NOT a measurement about HQC. It closes two
gaps the Red Team (TASK-20260806-21c8da) found in the V1 arm
(TASK-20260806-e19f6c): (1) it imports and calls stage_a.py's ACTUAL
decode_blocks (the real WHT/Reed-Muller-fold argmax decoder), not a
hand-rolled majority threshold, and (2) it uses two fixed, heterogeneous,
decision-boundary-adjacent 128-bit templates (verified, before any trial is
sampled, to genuinely decode to their intended label AND to have a
demonstrated non-zero chance of flipping under the campaign's named V1/V3
boundary-index-shift defect classes -- see design.md Section 3), instead of
V1's homogeneous all-0/all-1 blocks.

The joint law of WHICH block positions are planted-fail is unchanged from
V1: an exchangeable mixture (M_t ~ Uniform{17,18,19}, a uniform random
M_t-subset of the n_e=56 positions), so log2_A_k(k) remains exactly
closed-form (design.md Section 2) -- the marginal law of S_t depends only on
WHICH positions are marked fail, never on WHAT bit content realizes "fail"
vs. "succeed" at a position.

WHAT IT IS NOT
--------------
Not a statement about HQC, A17, A5, any decoding-failure rate, or any
standardized parameter set. Not a re-run of PS-R3. Not a full test of
stage_a.py's cryptographic (T)-sampler (CTRStream, fixed_weight_support,
ring_mul_sparse/dense are never invoked -- see design.md Section 6.2). Claim
tier: TOY.

A timeout, crash, missing dependency or budget exhaustion is an
INFRASTRUCTURE outcome and is never evidence about the mathematics
(AGENTS.md rule 5).

FAIL-CLOSED INTEGRITY CHECKS
-----------------------------
Before importing measure.py or stage_a.py, this script hashes each and
ABORTS (SystemExit) if the hash does not match the pinned constant below.
Both templates are re-verified against the REAL decode_blocks (and
independently against brute_force_decode / rm17_codewords) before any trial
is generated, and the planted-law closed form is re-derived and checked
against design.md's frozen table. Every one of these actually reads the
value/field it guards (demonstrated by a deliberate-mismatch dry run; see
run_manifest.yaml).

Re-run:
    PYTHONDONTWRITEBYTECODE=1 python3 planted_arm_v2.py --out-dir .
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

# sha256 of measure.py and stage_a.py AS READ by this task at design time
# (2026-08-06). FAIL-CLOSED: load_module() below actually reads these
# constants and compares them against a freshly computed hash of each file
# on disk, raising SystemExit on any mismatch (not a differently-named or
# differently-nested field -- the defect named in EV-HQC-b71230's
# unresolved_confounds).
MEASURE_PY_EXPECTED_SHA256 = (
    "a4fd1ecb63f0ddc83c02ef45f2c65ab31cf13d13e7ae94f500e67465b24f5dc8")
STAGE_A_PY_EXPECTED_SHA256 = (
    "06a0a618432c00fe26c72ecf05a8d89489db61c5183931fdb76a378717681405")

TASK_ID = "TASK-20260806-047535"
SEED_PREFIX = f"{TASK_ID}/PLANTED-ARM-V2/v1"

# ---------------------------------------------------------------------------
# parameters -- order-matched to PS-R3 / V1 (design.md Section 1)
# ---------------------------------------------------------------------------
N_E = 56
N_2 = 128
DUP = 1
N = N_E * N_2                       # 7168
M_PRESPEC = 17                       # narrative parity only
K_MAX = 18
KS = list(range(2, K_MAX + 1))       # 17 cells, k = 2..18
T_CEILING = 10_000_000               # what PS-R3/V1 used; not reachable here
N_JACK_BATCHES = 200

# the planted mixture law (design.md Section 2) -- unchanged from V1
SUPPORT = [17, 18, 19]
WEIGHTS = [Fraction(1, 3), Fraction(1, 3), Fraction(1, 3)]

# frozen table from design.md Section 2.1 -- computed BEFORE any sampling,
# reproduces V1's table exactly (same construction; see design.md Section 0).
DESIGN_TABLE_LOG2_A = {
    2: -0.05332724412846135, 3: -0.16394044463458357, 4: -0.3363079856368989,
    5: -0.5755089290487359, 6: -0.8873624322504217, 7: -1.2785962698872737,
    8: -1.7570703364157492, 9: -2.3320793631074803, 10: -3.0147730405328055,
    11: -3.8187560346206517, 12: -4.76097481483005, 13: -5.8630844320447935,
    14: -7.153668398603774, 15: -8.672097148069227, 16: -10.47587716111893,
    17: -12.65660891751783, 18: -15.382583727766058,
}
DESIGN_Q = 0.32142857142857145

# The two real-decoder templates (design.md Section 3.3), verified there
# BEFORE any trial generation. Index 0 of TEMPLATES = S_TEMPLATE (intended
# F=0, succeed); index 1 = FAIL_TEMPLATE (intended F=1, fail).
S_TEMPLATE = [1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1,
              1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1,
              0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0,
              0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0,
              0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0,
              0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0]
FAIL_TEMPLATE = [0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1,
                 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0,
                 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0,
                 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0,
                 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1,
                 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 1,
                 1, 1]
assert len(S_TEMPLATE) == 128 and len(FAIL_TEMPLATE) == 128

CORE_SECOND_BUDGET = 1800.0
WALL_BUDGET = 3300.0                 # authorized 3600s; reserve 300s margin
MATCH_SE_MULTIPLIER = 3.0            # design.md Section 8: adopted, not verbatim

# T for the authorized run: see design.md Section 5 (real-decoder throughput
# forces a 10x reduction from PS-R3/V1's T=1e7). Sized so estimated cost
# (~834 core-seconds at the calibrated 1198 trials/core-second) stays well
# inside the 1800 core-second budget with headroom for every other stage.
T_PLANNED = 1_000_000
SUB_CHUNK = T_PLANNED // N_JACK_BATCHES     # 5,000: one generation call per
                                             # jackknife batch (design.md S4)


# ---------------------------------------------------------------------------
# provenance helpers
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


def derive_seed(purpose: str, n: int) -> int:
    """Newly written for this task (design.md Section 7). Distinct prefix
    from both V1's ('TASK-20260806-e19f6c/PLANTED-ARM/v1') and measure.py's
    ('EXP-HQC-982268/v3/INV-NULL'), so no random stream can collide."""
    s = f"{SEED_PREFIX}|{purpose}|{n}"
    return int.from_bytes(hashlib.sha256(s.encode()).digest()[:8], "big")


# ---------------------------------------------------------------------------
# FAIL-CLOSED import of measure.py and stage_a.py (read-only reuse)
# ---------------------------------------------------------------------------

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
# planted law: closed form (design.md Section 2, unchanged from V1)
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
# real-decoder template verification (design.md Section 3.4/3.5) -- MUST run
# and PASS before any trial is generated.
# ---------------------------------------------------------------------------

def shift_read_one_early(block: np.ndarray, foreign_last_bit) -> np.ndarray:
    """The V1/V3 'read one index early' operation, worked out exactly
    (design.md Section 3.5): the block drops its own true last bit and gains
    a foreign bit (from the preceding block's last position) at the front."""
    out = np.empty_like(block)
    out[0] = foreign_last_bit
    out[1:] = block[:-1]
    return out


def shift_read_one_late(block: np.ndarray, foreign_first_bit) -> np.ndarray:
    """Mirror-image direction (not a named campaign defect, checked as an
    additional sanity probe -- design.md Section 3.5)."""
    out = np.empty_like(block)
    out[:-1] = block[1:]
    out[-1] = foreign_first_bit
    return out


def wht_margin(sa_mod, block128: np.ndarray) -> dict:
    v = (1 - 2 * block128.astype(np.int32))
    t = sa_mod.wht128(v.reshape(1, 128).copy()).reshape(128)
    av = np.abs(t)
    order = np.argsort(-av, kind="stable")
    return dict(top1=int(av[order[0]]), top2=int(av[order[1]]),
                margin=int(av[order[0]] - av[order[1]]),
                idx0=int(order[0]), val0=int(t[order[0]]))


def decode_one(sa_mod, block128: np.ndarray):
    b = block128.reshape(1, 128).astype(np.uint8)
    F, W, ties = sa_mod.decode_blocks(b, 1, 128, 1)
    return bool(F[0, 0]), int(W[0, 0]), bool(ties[0, 0])


def verify_templates(sa_mod) -> dict:
    """The one-time, pre-trial-generation verification this task's
    completion gate requires (design.md Section 3.4/3.5). Aborts fail-closed
    if any template's TRUE decode disagrees with its intended label under
    EITHER of the two independent decoders."""
    S = np.array(S_TEMPLATE, dtype=np.uint8)
    Fl = np.array(FAIL_TEMPLATE, dtype=np.uint8)

    out = dict(
        S_TEMPLATE_sha256=sha256_bits(S), FAIL_TEMPLATE_sha256=sha256_bits(Fl))

    # 1. decode_blocks (the real, production decoder)
    S_F, S_W, S_ties = decode_one(sa_mod, S)
    Fl_F, Fl_W, Fl_ties = decode_one(sa_mod, Fl)
    out["decode_blocks"] = dict(
        S_TEMPLATE=dict(F=S_F, W=S_W, ties=S_ties, intended_F=False,
                        matches_intended=(S_F == False)),
        FAIL_TEMPLATE=dict(F=Fl_F, W=Fl_W, ties=Fl_ties, intended_F=True,
                           matches_intended=(Fl_F == True)))

    # 2. brute_force_decode -- INDEPENDENT algorithm, exhaustive minimum
    #    distance search over rm17_codewords()'s 256 duplicated RM(1,7)
    #    codewords. Exercises rm17_codewords() directly.
    both = np.stack([S, Fl], axis=0)
    bf = sa_mod.brute_force_decode(both, dup=1)
    out["brute_force_decode_rm17_codewords"] = dict(
        S_TEMPLATE=dict(F=bool(bf[0]), matches_intended=(bool(bf[0]) == False),
                        agrees_with_decode_blocks=(bool(bf[0]) == S_F)),
        FAIL_TEMPLATE=dict(F=bool(bf[1]), matches_intended=(bool(bf[1]) == True),
                           agrees_with_decode_blocks=(bool(bf[1]) == Fl_F)),
        n_codewords_searched=int(sa_mod.rm17_codewords().shape[0]))

    # 3. WHT margin (design.md Section 3.1/3.2)
    out["margin"] = dict(S_TEMPLATE=wht_margin(sa_mod, S),
                         FAIL_TEMPLATE=wht_margin(sa_mod, Fl))

    # 4. boundary-index-shift sensitivity (design.md Section 3.5): the exact
    #    perturbation V1/V3 inject, tested on both templates, both directions,
    #    both same-label and different-label neighbor scenarios.
    scenarios = {}
    for name, blk, other, expect in (("S_TEMPLATE", S, Fl, False),
                                     ("FAIL_TEMPLATE", Fl, S, True)):
        for direction, fn, foreign_same, foreign_diff in (
            ("early", shift_read_one_early, blk[-1], other[-1]),
            ("late", shift_read_one_late, blk[0], other[0]),
        ):
            for neighbor, foreign in (("same", foreign_same), ("diff", foreign_diff)):
                perturbed = fn(blk, foreign)
                F, W, ties = decode_one(sa_mod, perturbed)
                key = f"{name}_{direction}_{neighbor}"
                scenarios[key] = dict(unperturbed_F=expect, perturbed_F=F,
                                      flipped=(F != expect), W=W, ties=ties)
    out["boundary_shift_sensitivity"] = scenarios
    out["any_flip_observed"] = any(v["flipped"] for v in scenarios.values())

    all_ok = (out["decode_blocks"]["S_TEMPLATE"]["matches_intended"]
              and out["decode_blocks"]["FAIL_TEMPLATE"]["matches_intended"]
              and out["brute_force_decode_rm17_codewords"]["S_TEMPLATE"]["matches_intended"]
              and out["brute_force_decode_rm17_codewords"]["FAIL_TEMPLATE"]["matches_intended"])
    out["verdict"] = "PASS" if all_ok else "FAIL"
    return out


# ---------------------------------------------------------------------------
# the block-partition / real-decode generator (design.md Section 4)
# ---------------------------------------------------------------------------

def run_batch(rng: np.random.Generator, n_trials: int, n_e: int, N_bits: int,
             n_2: int, dup: int, templates: np.ndarray, decode_blocks_fn):
    """One jackknife batch, generated in ONE call (n_trials == SUB_CHUNK by
    construction; design.md Section 4). Steps:
      1. draw M_t ~ Uniform{17,18,19}                          (design.md 2)
      2. draw a uniform random size-M_t subset of n_e blocks     (design.md 2)
      3. build the flat (n_trials, N) bit array by indexing the  (design.md 4,
         (2, 128) template table with block_fail                  step 2)
      4. call decode_blocks -- THE REAL DECODER, which performs   (design.md 4,
         its own bits.reshape(B, n_e, n_2)                        step 3)
      5. assert F == block_fail (fail-closed self-check)          (design.md 4,
                                                                    step 4)
      6. S_t = F.sum(axis=1), accumulate into this batch's histogram
    Returns (hist, block_fail_last, F_last) for diagnostics.
    """
    m0 = rng.integers(SUPPORT[0], SUPPORT[-1] + 1, size=n_trials)
    keys = rng.random((n_trials, n_e))
    ranks = np.argsort(np.argsort(keys, axis=1), axis=1)
    block_fail = (ranks < m0[:, None])                          # (b, n_e) bool

    flat = templates[block_fail.astype(np.int64)]                # (b, n_e, 128)
    bits = flat.reshape(n_trials, N_bits)

    F, W, ties = decode_blocks_fn(bits, n_e, n_2, dup)

    if not np.array_equal(F, block_fail):
        n_mismatch = int(np.count_nonzero(F != block_fail))
        raise SystemExit(
            "FAIL-CLOSED: block-partition/real-decode self-check failed -- "
            f"the REAL decode_blocks output disagrees with the planted "
            f"block_fail pattern on {n_mismatch}/{block_fail.size} block "
            f"decisions. Aborting rather than reporting a result from a "
            f"construction whose premise (design.md Section 3.4's template "
            f"verification) has failed at run time (design.md Section 4, "
            f"step 4).")

    S = F.sum(axis=1)
    hist = np.bincount(S, minlength=n_e + 1)[:n_e + 1]
    return hist, ties.sum()


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=HERE)
    ap.add_argument("--trials", type=int, default=T_PLANNED)
    ap.add_argument("--batches", type=int, default=N_JACK_BATCHES)
    args = ap.parse_args(argv)

    if args.trials % args.batches != 0:
        raise SystemExit("FAIL-CLOSED: --trials must divide evenly into "
                         "--batches for the one-call-per-jackknife-batch "
                         "generation used here (design.md Section 4).")
    sub_chunk = args.trials // args.batches

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
        "batch": "BATCH-558f5b",
        "claim_tier": "toy",
        "what_this_is": (
            "V2 planted-correlation control arm for OPEN-6. Imports and "
            "calls stage_a.py's REAL decode_blocks (sha256-pinned, "
            "unmodified) on two fixed, heterogeneous, decision-boundary- "
            "adjacent 128-bit templates (verified before any trial is "
            "sampled -- see design.md Section 3), tiled at n_e=56 positions "
            "chosen via the same exchangeable position-marking mechanism "
            "V1 used. Reports MATCH/MISMATCH per k -- observations only, no "
            "conclusion about A17, HQC's DFR, or any standardized parameter "
            "set."),
        "design_doc": "design.md (written and frozen before this run; see "
                       "run_manifest.yaml for the file-timestamp ordering "
                       "evidence)",
        "started_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    # ---------------- phase 0: provenance -----------------------------
    cw0 = time.time(); cc0 = core_seconds()
    R["git"] = git_state()
    R["environment"] = dict(
        python=sys.version.split()[0], numpy=np.__version__,
        platform=platform.platform(), processor=platform.machine(),
        cpu_count=os.cpu_count())
    stage_end("provenance", cw0, cc0)

    # ---------------- phase 1: FAIL-CLOSED integrity + import ----------
    cw0 = time.time(); cc0 = core_seconds()
    measure, measure_sha = load_module(MEASURE_PY, MEASURE_PY_EXPECTED_SHA256,
                                       "measure.py", "measure_frozen")
    sa, sa_sha = load_module(STAGE_A_PY, STAGE_A_PY_EXPECTED_SHA256,
                             "stage_a.py", "stage_a_frozen")
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
            reused_symbols=["decode_blocks (line 286, called directly, not "
                            "reimplemented)", "rm17_codewords (line 310, via "
                            "brute_force_decode)", "brute_force_decode (line 323)",
                            "wht128 (line 270, called internally by decode_blocks)"],
            not_reused_symbols=["CTRStream", "fixed_weight_support",
                                "ring_mul_sparse", "ring_mul_dense",
                                "support_to_int*", "_t_shard", "_null_m_shard",
                                "every phase_* function", "main"]))
    if measure.N_JACK_BATCHES != N_JACK_BATCHES:
        raise SystemExit("FAIL-CLOSED: N_JACK_BATCHES mismatch between this "
                         "task's constant and measure.py's.")
    stage_end("fail_closed_integrity_and_import", cw0, cc0)

    # ---------------- phase 2: planted law (closed form) ----------------
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
                     "chosen as a uniform random size-M_t subset of n_e=56 "
                     "POSITIONS; S_t = M_t exactly. Content per label is "
                     "fixed (S_TEMPLATE / FAIL_TEMPLATE); this does not "
                     "change the marginal law of S_t (design.md Section 0).",
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

    # ---------------- phase 3: real-decoder template verification -------
    # design.md Section 3.4/3.5: MUST run and PASS before any trial is
    # generated. Uses the REAL decode_blocks and the INDEPENDENT
    # brute_force_decode / rm17_codewords cross-check.
    cw0 = time.time(); cc0 = core_seconds()
    tv = verify_templates(sa)
    R["template_verification"] = tv
    if tv["verdict"] != "PASS":
        R["validity"] = dict(
            status="failed_implementation",
            reason="A near-boundary template's TRUE decode (via the real "
                   "decode_blocks and/or the independent brute_force_decode) "
                   "disagreed with its intended label. Aborting before any "
                   "trial generation, per this task's binding constraint "
                   "that a mismatching template must be discarded or fixed, "
                   "never silently used.")
        json.dump(R, open(os.path.join(args.out_dir, "planted_results.json"), "w"),
                  indent=1, default=str)
        raise SystemExit("FAIL-CLOSED: template verification failed")
    print(f"[templates] verdict={tv['verdict']}  "
          f"S margin={tv['margin']['S_TEMPLATE']['margin']}  "
          f"FAIL margin={tv['margin']['FAIL_TEMPLATE']['margin']}  "
          f"any_boundary_shift_flip={tv['any_flip_observed']}", flush=True)
    stage_end("real_decoder_template_verification", cw0, cc0)

    # ---------------- phase 4: block-partition / real-decode generation -
    n_e = N_E
    L = N // n_e                              # RULE-2: L = N/n_e, never n_2*dup
    if L != N_2:
        raise SystemExit(f"FAIL-CLOSED: L=N/n_e={L} != N_2={N_2}.")
    templates = np.array([S_TEMPLATE, FAIL_TEMPLATE], dtype=np.uint8)  # (2,128)
    ks = KS
    C = measure.comb_matrix(n_e, ks)          # REUSED VERBATIM (measure.py)

    cw0 = time.time(); cc0 = core_seconds()
    bh = np.zeros((args.batches, n_e + 1), dtype=np.int64)
    batch_seeds = []
    total_ties = 0
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
        bh[i], ties_i = run_batch(rng, sub_chunk, n_e, N, N_2, DUP, templates,
                                  sa.decode_blocks)
        total_ties += int(ties_i)
        if i % 40 == 0 or i == args.batches - 1:
            print(f"[batch] {i + 1}/{args.batches} done, cum core-s="
                  f"{core_seconds() - c0:.1f}", flush=True)
    stage_end("block_partition_real_decode_generation", cw0, cc0)

    batches_completed = (args.batches if not truncated else truncated_at_batch)
    T_ach = int(bh[:batches_completed].sum())
    R["generation"] = dict(
        n_e=n_e, N=N, n_2=N_2, dup=DUP, L=L,
        L_formula="L = N // n_e (RULE-2 corrected; NOT n_2*dup); equals the "
                  "n_2 decode_blocks itself uses for its own reshape",
        real_decode_blocks_used=True,
        trials_planned=args.trials, batches_planned=args.batches,
        trials_per_batch=sub_chunk,
        batches_completed=batches_completed, trials_achieved=T_ach,
        achieved_equals_planned=(T_ach == args.trials),
        truncated_by_wall_budget=truncated,
        truncated_at_batch=truncated_at_batch,
        block_partition_self_check_note=(
            "Every one of the above batches passed the F == block_fail "
            "assertion in run_batch() -- computed by the REAL decode_blocks, "
            "not a hand-rolled reduce; a single failure would have aborted "
            "the run (fail-closed, design.md Section 4 step 4)."),
        ties_observed_total=total_ties,
        ties_observed_note=(
            "Count of individual block decisions where decode_blocks' own "
            "'ties' flag fired (a genuine |WHT| tie for the argmax, broken "
            "deterministically toward the lowest index by numpy argmax). "
            "Expected to be occasionally nonzero given the near-boundary "
            "templates (design.md Section 3.5 shows some perturbed variants "
            "produce ties); does not by itself indicate a defect."),
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
                  indent=1, default=str)
        raise SystemExit("INFRASTRUCTURE: wall-clock budget exhausted before "
                         "the planned T was reached")

    # ---------------- phase 5: estimator + jackknife (REUSED VERBATIM) --
    # Reproduces measure.py lines 730-739 verbatim (variable names retained:
    # bh, hist, point, loo, jmean, jse), applied to THIS arm's histograms.
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
        what="Recovered log2_Ahat_k on the V2 real-decoder planted-"
             "correlation control arm, against the closed-form planted "
             "value, using measure.py's own estimator and jackknife code "
             "applied to this arm's histogram (built from the REAL "
             "decode_blocks output).",
        estimator="REUSED VERBATIM from measure.py: log2_Ahat_k = "
                  "log2((sum_s C(s,k) H_s)/(T C(n_e,k))) - k log2((sum_s s H_s)/(T n_e))",
        comparison_rule=(f"MATCH iff planted_log2_A_k(k) is within "
                         f"[point_k - {MATCH_SE_MULTIPLIER:.0f}*jackknife_se_k, "
                         f"point_k + {MATCH_SE_MULTIPLIER:.0f}*jackknife_se_k]; "
                         f"adopted for this task per design.md Section 8, not "
                         f"a verbatim rule from measure.py."),
        T_planned_at_PSR3_scale=T_CEILING,
        T_reduced_reason="real decode_blocks throughput (~1198 trials/core-"
                         "second, calibrated) vs. V1's hand-rolled reduce "
                         "(~64700 trials/core-second) does not fit T=1e7 in "
                         "the 1800 core-second budget; see design.md Section 5.",
        T_achieved=T_ach, q_hat_measured=q_meas, q_planted_exact=law["q_float"],
        cells=cells_out, cells_reported=len(cells_out),
        cells_match=n_match, cells_mismatch=len(cells_out) - n_match)
    print(f"[MEASUREMENT] {n_match}/{len(cells_out)} cells MATCH within "
          f"{MATCH_SE_MULTIPLIER:.0f} jackknife SE", flush=True)

    # ---------------- close out ------------------------------------------
    spent = core_seconds() - c0
    wall = time.time() - t_wall0
    R["budget"] = dict(
        core_seconds_authorized=CORE_SECOND_BUDGET, core_seconds_spent=round(spent, 3),
        core_seconds_remaining=round(CORE_SECOND_BUDGET - spent, 3),
        within_core_second_budget=spent <= CORE_SECOND_BUDGET,
        wall_seconds=round(wall, 3), wall_authorized=3600.0,
        within_wall_budget=wall <= 3600.0,
        peak_rss_mb_self=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0,
        stages=stages,
        subsample_used=False,
        subsample_note="No stage of THIS run was forced onto a subsample of "
                       "its own planned T; achieved T equals planned T "
                       "(see generation.achieved_equals_planned). The "
                       "planned T itself (1,000,000, not PS-R3/V1's 1e7) is "
                       "a pre-registered, budget-driven reduction -- see "
                       "design.md Section 5 and MEASUREMENT.T_reduced_reason.")
    ok = (R["reused_pipeline"]["measure_py"]["integrity_check_passed"]
          and R["reused_pipeline"]["stage_a_py"]["integrity_check_passed"]
          and tv["verdict"] == "PASS"
          and not mismatches
          and not truncated
          and R["generation"]["achieved_equals_planned"]
          and spent <= CORE_SECOND_BUDGET and wall <= 3600.0)
    R["validity"] = dict(
        status="valid_measurement" if ok else "invalid_measurement",
        reason=("All fail-closed gates passed (measure.py/stage_a.py "
                "integrity, template verification, planted-law "
                "reproduction, block-partition self-check), T achieved "
                "equals T planned, and the run stayed within its core-"
                "second and wall-clock budget." if ok
                else "See gate/budget fields above."),
        scoped_to="ONE V2 planted-correlation instance, order-matched to "
                  "PS-R3's n_e/n_2/dup/m, k=2..18, real decode_blocks, "
                  "T=1,000,000 (budget-reduced from 1e7 -- see design.md "
                  "Section 5). Claim tier: toy. See design.md Section 6 for "
                  "what this arm does NOT exercise.")
    R["finished_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    out = os.path.join(args.out_dir, "planted_results.json")
    with open(out, "w") as fh:
        json.dump(R, fh, indent=1)
    print(f"[done] {out}  core-s={spent:.1f}/{CORE_SECOND_BUDGET} "
          f"wall={wall:.0f}s  validity={R['validity']['status']}", flush=True)
    return R


if __name__ == "__main__":
    main()
