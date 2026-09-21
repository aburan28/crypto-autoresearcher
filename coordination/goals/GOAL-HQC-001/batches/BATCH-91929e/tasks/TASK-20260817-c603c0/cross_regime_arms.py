#!/usr/bin/env python3
"""PART A -- confound-breaking 2x2 (shard x transition regime) local-exponent
factorial on fresh, fully disjoint trial ranges.

TASK-20260817-c603c0 (executor) / BATCH-91929e / GOAL-HQC-001 /
EXP-HQC-982268.  Authorized by DEC-20260815-176614.  Pre-registered design in
design.md, WRITTEN AND FROZEN BEFORE THIS SCRIPT WAS RUN ON REAL DATA.

Shards 5000 and 8002, each at BOTH transition regimes, from ONE
n_trials=75000 call per (shard, variant).  Never split into separate calls:
a second call restarts trial indexing at 0 and would silently re-derive an
already-consumed domain.

stage_a.py, measure.py and matched_pair.py are imported READ-ONLY through a
fail-closed sha256-pinned loader and are never modified.  The estimator and
sampler are IMPORTED, not rebuilt (design.md Section 1); the four bootstrap
utilities sha256_file / core_seconds / git_state / load_module_fail_closed are
locally re-defined for the disclosed chicken-and-egg reason (EV-HQC-469c08
O10) and for no other.

Claim tier: TOY, hard ceiling.  PS-R3 only.  Nothing here is a statement
about HQC, A17, A5, its decoding-failure rate, or any standardized parameter
set.  OBSERVATIONS ONLY: no reading rule is applied and no conclusion drawn.

A timeout, crash, missing dependency or budget exhaustion is an
INFRASTRUCTURE outcome and is never evidence about the mathematics
(AGENTS.md rule 5).

Re-run:
    PYTHONDONTWRITEBYTECODE=1 python3 cross_regime_arms.py --out-dir .
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

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *([".."] * 7)))

STAGE_A_PY = os.path.join(
    REPO, "coordination", "goals", "GOAL-HQC-001", "batches", "BATCH-6fddee",
    "tasks", "TASK-20260806-64b506", "stage_a.py")
MEASURE_PY = os.path.join(
    REPO, "coordination", "goals", "GOAL-HQC-001", "batches", "BATCH-0a65c0",
    "tasks", "TASK-20260806-cde749", "measure.py")
MATCHED_PAIR_PY = os.path.join(
    REPO, "coordination", "goals", "GOAL-HQC-001", "batches", "BATCH-412513",
    "tasks", "TASK-20260809-a79e4f", "matched_pair.py")
A79E4F_RESULTS = os.path.join(
    REPO, "coordination", "goals", "GOAL-HQC-001", "batches", "BATCH-412513",
    "tasks", "TASK-20260809-a79e4f", "matched_pair_results.json")
BBDD2_RESULTS = os.path.join(
    REPO, "coordination", "goals", "GOAL-HQC-001", "batches", "BATCH-0e126d",
    "tasks", "TASK-20260814-8bbdd2", "matched_pair_repeat_results.json")
E61CCA_RESULTS = os.path.join(
    REPO, "coordination", "goals", "GOAL-HQC-001", "batches", "BATCH-174014",
    "tasks", "TASK-20260815-e61cca", "shard_8001_8002_discard_prefix_results.json")

STAGE_A_PY_EXPECTED_SHA256 = (
    "06a0a618432c00fe26c72ecf05a8d89489db61c5183931fdb76a378717681405")
MEASURE_PY_EXPECTED_SHA256 = (
    "a4fd1ecb63f0ddc83c02ef45f2c65ab31cf13d13e7ae94f500e67465b24f5dc8")
MATCHED_PAIR_PY_EXPECTED_SHA256 = (
    "66266a6178eb46e0b37ec0afdb2620064db56bff82318498e2dd83af1bd1c821")

SET_ID = "PS-R3"
M = 17
K_RANGE_AUTHORIZED = list(range(2, 27))

SHARD_A = 5000
SHARD_B = 8002
START_INDEX = 30_000
N_TOTAL_PER_CALL = 75_000
N_VERIFICATION = 10_000

# frozen windows, identical for both shards (design.md Section 2.2)
WINDOWS = [
    ("P1", 30_000, 35_000),
    ("P2", 35_000, 45_000),
    ("N1", 45_000, 55_000),
    ("N2", 55_000, 75_000),
]
REGIMES = {"P": ("P1", "P2"), "N": ("N1", "N2")}

EXPECTED_HIGH_WATER = {SHARD_A: 15_000, SHARD_B: 30_000}

ARMB_TOLERANCE_RELATIVE = 1e-9

CORE_SECOND_BUDGET = 900.0
WALL_SECOND_BUDGET = 1800.0

HISTORICAL_CITED = {
    "shard_5000_regime_P": {"alpha": 2.836, "source": "EV-HQC-469c08 O6"},
    "shard_6000_regime_P": {"alpha": 1.402, "source": "EV-HQC-469c08 O6"},
    "shard_8001_regime_N": {"alpha": -0.2682495157085447,
                            "source": "EV-HQC-927899 O3"},
    "shard_8002_regime_N": {"alpha": -0.8662355237627483,
                            "source": "EV-HQC-927899 O4"},
}


# --------------------------------------------------------------------------
# bootstrap utilities -- LOCALLY RE-DEFINED, and only these four.
# matched_pair.py's own loader cannot be used to load matched_pair.py itself.
# Disclosed in design.md Section 1 in the same breath as the reuse claim
# (the documentation-accuracy defect EV-HQC-469c08 O10 recorded).
# --------------------------------------------------------------------------

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
        except Exception as exc:                                  # noqa: BLE001
            return f"<unavailable: {exc}>"
    porcelain = run("git", "status", "--porcelain")
    return dict(commit=run("git", "rev-parse", "HEAD"),
                branch=run("git", "rev-parse", "--abbrev-ref", "HEAD"),
                dirty=bool(porcelain), dirty_paths=porcelain.splitlines()[:60])


def load_module_fail_closed(path: str, expected_sha256: str, name: str,
                            module_name: str):
    actual = sha256_file(path)
    if actual != expected_sha256:
        raise SystemExit(
            f"FAIL-CLOSED: {name} sha256 mismatch. expected={expected_sha256} "
            f"actual={actual}. This task reuses {name} read-only and refuses "
            f"to proceed if the file on disk differs from what design.md was "
            f"written against.")
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, actual


def _f(x):
    x = float(x)
    return None if not math.isfinite(x) else x


def log(msg):
    print(msg, flush=True)


# --------------------------------------------------------------------------

def scan_for_raw_arrays(obj, min_len: int, path="", found=None):
    """Mechanically determine whether a committed results JSON persists any
    raw per-trial-length integer array.  Never assumed -- determined."""
    if found is None:
        found = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            scan_for_raw_arrays(v, min_len, f"{path}/{k}", found)
    elif isinstance(obj, list):
        if len(obj) >= min_len and all(isinstance(x, int) for x in obj[:50]):
            found.append(dict(path=path, length=len(obj)))
        else:
            for i, v in enumerate(obj[:8]):
                scan_for_raw_arrays(v, min_len, f"{path}[{i}]", found)
    return found


def two_point_alpha(se_lo, se_hi, t_lo, t_hi):
    if se_lo is None or se_hi is None or se_lo <= 0 or se_hi <= 0:
        return None
    return -(math.log(se_hi) - math.log(se_lo)) / (math.log(t_hi) - math.log(t_lo))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=HERE)
    args = ap.parse_args(argv)
    out_main = os.path.join(args.out_dir, "cross_regime_arms_results.json")
    out_disj = os.path.join(args.out_dir, "disjointness_proof_results.json")

    t0, c0 = time.time(), core_seconds()
    R = {
        "task_id": "TASK-20260817-c603c0",
        "role": "executor",
        "part": "A",
        "experiment_id": "EXP-HQC-982268",
        "hypothesis_id": "H-HQC-18d1b4",
        "goal": "GOAL-HQC-001",
        "batch": "BATCH-91929e",
        "authorized_by": "DEC-20260815-176614",
        "claim_tier": "toy",
        "scope_statement": (
            "TOY, hard ceiling. PS-R3 only (n=7187, n_e=56, n_2=128, dup=1, "
            "N=7168, k 2..26, m=17). One defect class (V3, "
            "last-block-window-read-early), one injection point "
            "(decode_blocks's block window, LAST BLOCK ONLY). Shards 5000 and "
            "8002 INDIVIDUALLY -- NO cross-shard pooling anywhere in this "
            "script. Trial indices [30000,75000) retained per shard; the "
            "discarded prefix [0,30000) is COMPUTED, never skipped, because it "
            "carries the disjointness proof. NOTHING here is a statement about "
            "HQC, A17, A5, any decoding-failure rate, or any standardized "
            "parameter set."),
        "observations_only_note": (
            "THE EXECUTOR CONCLUDES NOTHING. batch.yaml's frozen four-branch "
            "reading rule is NOT applied here; it is the Coordinator's to "
            "apply at the ledger archive."),
        "design_reference": "design.md, frozen before this run",
        "started_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "command": " ".join([sys.executable] + sys.argv),
        "git": git_state(),
        "environment": dict(
            python=sys.version, python_executable=sys.executable,
            platform=platform.platform(), machine=platform.machine(),
            numpy=np.__version__, cpu_count=os.cpu_count()),
        "constants": dict(
            shards=[SHARD_A, SHARD_B], start_index=START_INDEX,
            n_total_per_call=N_TOTAL_PER_CALL,
            n_verification=N_VERIFICATION,
            discarded_prefix="[0:30000)",
            windows={w: f"[{a}:{b})" for w, a, b in WINDOWS},
            window_T={w: b - a for w, a, b in WINDOWS},
            regimes={"P": "P1->P2 (batch 25->50)", "N": "N1->N2 (batch 50->100)"},
            primary_cell_k=M, k_range_reported=K_RANGE_AUTHORIZED,
            analysis_calls=4, verification_calls=2, warmup_per_run_arm=300),
    }
    D = {"task_id": R["task_id"], "part": "A",
         "what_this_file_is": (
             "The two per-arm disjointness proofs, the F[:, 0:n_e-1] "
             "structural invariant, the high-water re-derivation, the window "
             "disjointness assertions and the one-call-vs-two-call batch "
             "structure check, separated out so a reviewer can audit the "
             "validity gates without reading the statistics.")}

    # ---- window arithmetic, asserted before anything is generated --------
    wins = {w: (a, b) for w, a, b in WINDOWS}
    pair_disjoint = True
    for i, (w1, a1, b1) in enumerate(WINDOWS):
        for (w2, a2, b2) in WINDOWS[i + 1:]:
            if not (b1 <= a2 or b2 <= a1):
                pair_disjoint = False
    above_prefix = all(a >= START_INDEX for _, a, _ in WINDOWS)
    union_ok = (min(a for _, a, _ in WINDOWS) == START_INDEX
                and max(b for _, _, b in WINDOWS) == N_TOTAL_PER_CALL)
    D["window_arithmetic"] = dict(
        windows={w: dict(start=a, stop=b, T=b - a, jack_batch_size=(b - a) // 200)
                 for w, a, b in WINDOWS},
        pairwise_disjoint=pair_disjoint,
        all_above_discarded_prefix=above_prefix,
        union_is_start_index_to_n_total=union_ok,
        verdict="PASS" if (pair_disjoint and above_prefix and union_ok) else "FAIL")
    log(f"[windows] {D['window_arithmetic']['verdict']}")
    if D["window_arithmetic"]["verdict"] != "PASS":
        raise SystemExit("FAIL-CLOSED: window arithmetic assertion failed.")

    # ---- high-water re-derivation from the COMMITTED records -------------
    with open(A79E4F_RESULTS) as fh:
        prior1 = json.load(fh)
    with open(BBDD2_RESULTS) as fh:
        prior_bbdd2 = json.load(fh)
    with open(E61CCA_RESULTS) as fh:
        prior_e61cca = json.load(fh)

    hw5000 = prior_bbdd2["n_total_per_call"]
    hw8002 = prior_e61cca["n_total_per_call"]
    a79_stage1_len = len(prior1["stage_1"]["per_trial_S"]["shard_5000_defected"])
    a79_stage2_T_8002 = prior1["stage_2"]["stage2_sizing_applied"]["T2_shard_8002"]
    D["high_water_rederivation"] = dict(
        shard_5000=dict(
            consumed_by_TASK_20260809_a79e4f_stage1=f"[0:{a79_stage1_len})",
            consumed_by_TASK_20260814_8bbdd2=(
                f"[{prior_bbdd2['n_discard_prefix']}:{hw5000}) retained, "
                f"[0:{prior_bbdd2['n_discard_prefix']}) discarded-but-generated"),
            derived_high_water=hw5000, task_card_states=EXPECTED_HIGH_WATER[SHARD_A],
            match=(hw5000 == EXPECTED_HIGH_WATER[SHARD_A])),
        shard_8002=dict(
            consumed_by_TASK_20260809_a79e4f_stage2=f"[0:{a79_stage2_T_8002})",
            consumed_by_TASK_20260815_e61cca=(
                f"[{prior_e61cca['n_discard_prefix']}:{hw8002}) retained, "
                f"[0:{prior_e61cca['n_discard_prefix']}) discarded-but-generated"),
            derived_high_water=hw8002, task_card_states=EXPECTED_HIGH_WATER[SHARD_B],
            match=(hw8002 == EXPECTED_HIGH_WATER[SHARD_B])),
        start_index_strictly_above_both=(START_INDEX >= max(hw5000, hw8002)),
        verdict=("PASS" if (hw5000 == EXPECTED_HIGH_WATER[SHARD_A]
                            and hw8002 == EXPECTED_HIGH_WATER[SHARD_B]
                            and START_INDEX >= max(hw5000, hw8002)) else "FAIL"))
    log(f"[high_water] {D['high_water_rederivation']['verdict']} "
        f"5000={hw5000} 8002={hw8002}")
    if D["high_water_rederivation"]["verdict"] != "PASS":
        raise SystemExit(
            "STOP -- high-water re-derivation differs from the task card's "
            "stated constants. Reported as a finding; constants NOT adjusted "
            "silently. derived: "
            f"5000={hw5000}, 8002={hw8002}.")

    # ---- determine (never assume) whether 8bbdd2 persisted a raw array ----
    bbdd2_raw = scan_for_raw_arrays(prior_bbdd2, 5000)
    D["task_20260814_8bbdd2_raw_array_determination"] = dict(
        method=("mechanical recursive scan of the committed "
                "matched_pair_repeat_results.json for any integer list of "
                "length >= 5000"),
        found=bbdd2_raw,
        raw_per_trial_S_array_present=bool(bbdd2_raw),
        top_level_keys=sorted(prior_bbdd2.keys()),
        per_trial_S_related_keys=[k for k in prior_bbdd2
                                  if "per_trial" in k.lower()],
        per_trial_S_retained_tail_length_value=prior_bbdd2.get(
            "per_trial_S_retained_tail_length"),
        consequence=(
            "The additional [5000:15000) bit-identity check against "
            "TASK-20260814-8bbdd2 CANNOT be performed and is recorded as "
            "ABSENT-BY-DETERMINATION rather than skipped: that task persisted "
            "only DERIVED statistics plus an integer tail LENGTH, never a raw "
            "per-trial S array. Arm A's direct proof therefore rests on "
            "TASK-20260809-a79e4f stage 1's committed [0:5000) arrays alone, "
            "which is the strong cross-run/cross-process/cross-session check "
            "the task card specifies."))
    log("[8bbdd2 raw array] present="
        f"{D['task_20260814_8bbdd2_raw_array_determination']['raw_per_trial_S_array_present']}")

    # ---- selftests, BEFORE any real module load or real trial ------------
    mp, mp_sha = load_module_fail_closed(
        MATCHED_PAIR_PY, MATCHED_PAIR_PY_EXPECTED_SHA256, "matched_pair.py",
        "matched_pair_frozen_c603c0")
    R["fail_closed_selftests"] = {
        "sha256_pin_mismatch": mp.selftest_fail_closed_sha_mismatch()}
    log("[selftest] sha256 pin mismatch: "
        f"{R['fail_closed_selftests']['sha256_pin_mismatch']['verdict']}")
    if R["fail_closed_selftests"]["sha256_pin_mismatch"]["verdict"] != "PASS":
        raise SystemExit("FAILED_IMPLEMENTATION: sha256 pin fail-closed "
                         "selftest did not pass; refusing to proceed.")

    sa, sa_sha = load_module_fail_closed(
        STAGE_A_PY, STAGE_A_PY_EXPECTED_SHA256, "stage_a.py",
        "stage_a_frozen_c603c0")
    measure, me_sha = load_module_fail_closed(
        MEASURE_PY, MEASURE_PY_EXPECTED_SHA256, "measure.py",
        "measure_frozen_c603c0")

    R["provenance"] = dict(
        stage_a_path=os.path.relpath(STAGE_A_PY, REPO), stage_a_sha256=sa_sha,
        stage_a_sha256_match=(sa_sha == STAGE_A_PY_EXPECTED_SHA256),
        measure_path=os.path.relpath(MEASURE_PY, REPO), measure_sha256=me_sha,
        measure_sha256_match=(me_sha == MEASURE_PY_EXPECTED_SHA256),
        matched_pair_py_path=os.path.relpath(MATCHED_PAIR_PY, REPO),
        matched_pair_py_sha256=mp_sha,
        matched_pair_py_sha256_match=(mp_sha == MATCHED_PAIR_PY_EXPECTED_SHA256),
        prior_a79e4f_results_sha256=sha256_file(A79E4F_RESULTS),
        prior_8bbdd2_results_sha256=sha256_file(BBDD2_RESULTS),
        prior_e61cca_results_sha256=sha256_file(E61CCA_RESULTS),
        stage_a_modified=False, measure_modified=False,
        matched_pair_py_modified=False,
        local_loader_agrees_with_mp_sha256_file=all([
            mp.sha256_file(STAGE_A_PY) == sa_sha,
            mp.sha256_file(MEASURE_PY) == me_sha,
            mp.sha256_file(MATCHED_PAIR_PY) == mp_sha]),
        bootstrap_utility_functions_note=(
            "sha256_file, core_seconds, git_state and load_module_fail_closed "
            "are LOCALLY RE-DEFINED here, not imported via mp.*, for the "
            "bootstrap chicken-and-egg reason TASK-20260814-8bbdd2 and "
            "TASK-20260815-e61cca disclosed (EV-HQC-469c08 O10): "
            "matched_pair.py's own loader cannot load matched_pair.py. "
            "Behavioural byte-identity of the local loader's hashing is "
            "verified by local_loader_agrees_with_mp_sha256_file above. "
            "make_defected_decode_blocks, matched_pair_stats, arm_hists, cell, "
            "run_arm and both selftests ARE genuinely imported via mp.*, never "
            "re-derived."))

    ps = [p for p in sa.PARAM_SETS if p["id"] == SET_ID][0]
    n_e, n_2 = ps["n_e"], ps["n_2"]
    R["parameter_set"] = {k: ps[k] for k in
                          ("id", "role", "n", "n_e", "n_2", "dup", "omega",
                           "omega_r", "omega_e", "N")}
    R["parameter_set"]["m_load_bearing_order"] = M

    R["fail_closed_selftests"]["injection_invariant_mismatch"] = (
        mp.selftest_injection_invariant_fail(n_e, n_2))
    log("[selftest] injection invariant deliberate break: "
        f"{R['fail_closed_selftests']['injection_invariant_mismatch']['verdict']}")
    if R["fail_closed_selftests"]["injection_invariant_mismatch"]["verdict"] != "PASS":
        raise SystemExit("FAILED_IMPLEMENTATION: injection-invariant "
                         "fail-closed selftest did not pass; refusing to "
                         "proceed.")

    original_decode_blocks = sa.decode_blocks
    defected = mp.make_defected_decode_blocks(original_decode_blocks, n_2)
    R["injection"] = dict(
        defect_class="V3 (last-block-window-read-early)",
        injection_point=("decode_blocks's block window, LAST BLOCK ONLY "
                         "(index n_e - 1), shifted left by exactly one bit "
                         "position; decode_blocks itself called unmodified"),
        wrapper_calls_unmodified_function=(
            defected.__wrapped_original_id__ == id(original_decode_blocks)),
        wrapped_original_qualname=defected.__wrapped_original_qualname__,
        mechanism="design.md Section 0/2, fixed before this run")

    NB = sa.N_JACK_BATCHES
    VAR = {"defected": defected, "undefected": original_decode_blocks}

    call_timings = []
    hard_inv = {}

    def call(tag, shard, n_trials, variant):
        tw, tc = time.time(), core_seconds()
        r = mp.run_arm(sa, ps, shard, n_trials, VAR[variant],
                       original_decode_blocks)
        dt_w, dt_c = time.time() - tw, core_seconds() - tc
        call_timings.append(dict(tag=tag, shard=shard, variant=variant,
                                 n_trials_requested=n_trials,
                                 n_trials_done=r["trials_done"],
                                 truncated=bool(r["truncated"]),
                                 wall_seconds=round(dt_w, 3),
                                 core_seconds=round(dt_c, 3),
                                 includes_warmup_300=True))
        hard_inv[tag] = dict(D2_violations=int(r["d2_fail"]),
                             D3_violations=int(r["d3_fail"]),
                             D3_cap=int(r["d3_cap"]),
                             D3_max_w=int(r["d3_max_w"]),
                             truncated=bool(r["truncated"]),
                             trials_requested=n_trials,
                             trials_done=int(r["trials_done"]))
        log(f"[call] {tag} shard={shard} n={n_trials} done={r['trials_done']} "
            f"trunc={r['truncated']} wall={dt_w:.1f}s")
        return r

    # =====================================================================
    # STEP 1 of Arm B's adapted proof: the two dedicated verification calls,
    # made BEFORE and separately from the analysis calls.
    # =====================================================================
    ver = {}
    for variant in ("defected", "undefected"):
        r = call(f"verification_8002_{variant}", SHARD_B, N_VERIFICATION, variant)
        ver[variant] = r["F"].sum(axis=1).astype(np.int64)

    Hv_d, Bv_d = mp.arm_hists(sa, ver["defected"], n_e, NB)
    Hv_u, Bv_u = mp.arm_hists(sa, ver["undefected"], n_e, NB)
    ks_v = sorted(set(sa.evaluable_k(Hv_d, n_e)) & set(sa.evaluable_k(Hv_u, n_e))
                  & set(K_RANGE_AUTHORIZED))
    stats_v = mp.matched_pair_stats(measure, n_e, ks_v,
                                    measure.comb_matrix(n_e, ks_v),
                                    Hv_d, Bv_d, Hv_u, Bv_u)

    committed_8002 = prior1["stage_2"]["matched_pair"]["per_shard"]["shard_8002"]
    committed_hi = prior1["stage_2"]["hard_invariants"]
    float_fields = ["point_defected", "point_undefected", "diff", "se_paired",
                    "se_unpaired", "z_paired", "z_unpaired",
                    "unpaired_over_paired_ratio"]
    field_report = {}
    all_bit_identical = True
    all_within_tol = True
    max_rel = 0.0
    max_rel_where = None
    for f in float_fields:
        got = stats_v[f]
        exp = committed_8002[f]
        bit = (len(got) == len(exp)
               and all((g is None and e is None)
                       or (g is not None and e is not None
                           and np.float64(g).tobytes() == np.float64(e).tobytes())
                       for g, e in zip(got, exp)))
        rels = []
        for kk, (g, e) in zip(stats_v["ks"], zip(got, exp)):
            if g is None or e is None:
                rels.append(None)
                continue
            rel = abs(g - e) / abs(e) if e != 0 else abs(g - e)
            rels.append(rel)
            if rel > max_rel:
                max_rel, max_rel_where = rel, (f, kk)
        within = all(r is not None and r <= ARMB_TOLERANCE_RELATIVE for r in rels)
        all_bit_identical &= bit
        all_within_tol &= within
        field_report[f] = dict(bit_identical=bool(bit), within_tolerance=bool(within),
                               max_relative_deviation=(max(r for r in rels if r is not None)
                                                       if any(r is not None for r in rels) else None))
    ks_match = (stats_v["ks"] == committed_8002["ks"])
    nb_match = (stats_v["n_batches"] == committed_8002["n_batches"])
    int_match = all(
        hard_inv[f"verification_8002_{v}"][fld] == committed_hi[f"shard_8002_{v}"][fld]
        for v in ("defected", "undefected")
        for fld in ("D2_violations", "D3_violations", "D3_cap", "D3_max_w"))

    step1_pass = ks_match and nb_match and int_match and (all_bit_identical or all_within_tol)
    D["arm_B_adapted_disjointness_proof"] = dict(
        strength=("WEAKER than Arm A's, and stated as such. TASK-20260809-a79e4f "
                  "stage 2 persisted only DERIVED statistics and D2/D3 counts for "
                  "shards 8001/8002 -- no raw per-trial S array -- so the direct "
                  "check is unavailable on shard 8002."),
        step_1=dict(
            what=("dedicated n_trials=10000 verification call per (8002, variant), "
                  "made prior to and separately from the analysis calls; D2/D3/"
                  "D3_cap/D3_max_w and matched_pair_stats at k=2..26 recomputed and "
                  "compared against TASK-20260809-a79e4f stage 2's committed "
                  "shard_8002 values"),
            evaluable_k_recomputed=stats_v["ks"],
            evaluable_k_committed=committed_8002["ks"],
            evaluable_k_match=bool(ks_match),
            n_batches_match=bool(nb_match),
            hard_invariant_integers_exact_match=bool(int_match),
            hard_invariants_recomputed={
                f"shard_8002_{v}": hard_inv[f"verification_8002_{v}"]
                for v in ("defected", "undefected")},
            hard_invariants_committed={
                f"shard_8002_{v}": committed_hi[f"shard_8002_{v}"]
                for v in ("defected", "undefected")},
            float64_bit_identity_all_fields=bool(all_bit_identical),
            tolerance_used=(None if all_bit_identical else ARMB_TOLERANCE_RELATIVE),
            tolerance_fallback_fired=bool(not all_bit_identical),
            all_within_stated_tolerance=bool(all_within_tol),
            max_relative_deviation_observed=(None if max_rel == 0.0 else max_rel),
            max_relative_deviation_at=(None if max_rel_where is None
                                       else dict(field=max_rel_where[0], k=max_rel_where[1])),
            per_field=field_report,
            environment_difference_disclosed=(
                "The committed comparator values were produced on Linux x86_64 / "
                "CPython 3.11.15 / numpy 2.4.6; this run is macOS arm64 / CPython "
                f"{platform.python_version()} / numpy {np.__version__}. Exact "
                "float64 bit-identity was attempted FIRST. If the tolerance "
                "fallback fired, that shortfall is DISCLOSED AS A FINDING here "
                "and is never silently accepted."),
            verdict="PASS" if step1_pass else "FAIL"))
    log(f"[armB step1] {'PASS' if step1_pass else 'FAIL'} "
        f"bit_identical={all_bit_identical} max_rel={max_rel}")

    # =====================================================================
    # the four analysis calls -- EXACTLY ONE per (shard, variant), n=75000
    # =====================================================================
    S = {}
    F = {}
    for shard in (SHARD_A, SHARD_B):
        for variant in ("defected", "undefected"):
            r = call(f"analysis_{shard}_{variant}", shard, N_TOTAL_PER_CALL, variant)
            S[(shard, variant)] = r["F"].sum(axis=1).astype(np.int64)
            F[(shard, variant)] = r["F"]

    # ---- ARM A: DIRECT disjointness proof, fail-closed -------------------
    committed_S = prior1["stage_1"]["per_trial_S"]
    checks_a = []
    for variant in ("defected", "undefected"):
        comm = np.array(committed_S[f"shard_5000_{variant}"], dtype=np.int64)
        got = S[(SHARD_A, variant)][:len(comm)]
        el = bool(np.array_equal(got, comm))
        hist_id = bool(np.array_equal(sa.hist_of(got, n_e), sa.hist_of(comm, n_e)))
        checks_a.append(dict(key=f"shard_5000_{variant}",
                             committed_length=int(len(comm)),
                             prefix_length=int(len(got)),
                             length_match=bool(len(got) == len(comm)),
                             elementwise_per_trial_S_bit_identical=el,
                             S_histogram_bit_identical=hist_id,
                             elements_compared=int(len(comm)),
                             verdict="PASS" if (el and hist_id) else "FAIL"))
    arm_a_pass = all(c["verdict"] == "PASS" for c in checks_a)
    D["arm_A_direct_disjointness_proof"] = dict(
        strength=("STRONG -- cross-run, cross-process, cross-session and (here) "
                  "cross-machine/cross-platform: the committed comparator was "
                  "produced on Linux x86_64 / CPython 3.11 and this run is macOS "
                  "arm64 / CPython 3.13."),
        rule=("The [0:5000) prefix of Arm A's own n_trials=75000 analysis call "
              "must be bit-identical, elementwise, to TASK-20260809-a79e4f stage "
              "1's COMMITTED per_trial_S array for the same (shard, variant), and "
              "the S-histograms of both must be bit-identical."),
        source=os.path.relpath(A79E4F_RESULTS, REPO),
        checks=checks_a,
        additional_5000_to_15000_check=(
            D["task_20260814_8bbdd2_raw_array_determination"]["consequence"]),
        additional_5000_to_15000_check_performed=False,
        additional_5000_to_15000_check_reason="ABSENT-BY-DETERMINATION (see above)",
        overall_status="PASS" if arm_a_pass else "FAIL")
    log(f"[armA direct] {'PASS' if arm_a_pass else 'FAIL'}")
    if not arm_a_pass:
        D["abort"] = ("Arm A direct disjointness proof FAILED. AGENTS.md rule 5: "
                      "infrastructure_error / invalid_measurement, never "
                      "mathematical evidence. Aborted before any Arm A statistic.")
        with open(out_disj, "w") as fh:
            json.dump(D, fh, indent=1)
        raise SystemExit("FAIL-CLOSED ABORT: Arm A disjointness proof failed.")

    # ---- ARM B step 2: analysis prefix vs verification call --------------
    checks_b2 = []
    for variant in ("defected", "undefected"):
        got = S[(SHARD_B, variant)][:N_VERIFICATION]
        el = bool(np.array_equal(got, ver[variant]))
        checks_b2.append(dict(key=f"shard_8002_{variant}",
                              elements_compared=int(N_VERIFICATION),
                              elementwise_bit_identical=el,
                              verdict="PASS" if el else "FAIL"))
    step2_pass = all(c["verdict"] == "PASS" for c in checks_b2)
    D["arm_B_adapted_disjointness_proof"]["step_2"] = dict(
        what=("the n_trials=75000 analysis call's [0:10000) prefix must be "
              "bit-identical, elementwise, to the dedicated verification call's "
              "own raw per-trial S"),
        checks=checks_b2, verdict="PASS" if step2_pass else "FAIL")
    arm_b_pass = step1_pass and step2_pass
    D["arm_B_adapted_disjointness_proof"]["step_3_fail_closed"] = dict(
        rule="either step failing on either variant ABORTS Arm B",
        overall_status="PASS" if arm_b_pass else "FAIL")
    D["arm_B_adapted_disjointness_proof"]["step_4_required_correction"] = (
        "BINDING, and this task's own scheduled carry-forward "
        "(DEC-20260815-176614 next_actions item (2)). THE GENUINE RESIDUAL RISK "
        "IS THE SAME-PROCESS-vs-CROSS-PROCESS GAP: the adapted proof shows only "
        "that the n_trials=75000 analysis call is self-consistent with a "
        "verification call made inside THIS SAME task's own process, plus a "
        "match against previously committed DERIVED statistics. It does NOT "
        "compare the analysis call's raw trial stream against independently "
        "generated or previously committed RAW data, because no such raw data "
        "exists for shard 8002. IT IS NOT numpy RNG drift or platform drift: "
        "BATCH-174014's Red Team traced CTRStream directly and confirmed a pure "
        "SHA-256 counter-mode construction has no numpy-RNG or "
        "platform-dependent component, so TASK-20260815-e61cca design.md "
        "Section 3 Step 4's example was wrong and is CORRECTED here per "
        "DEC-20260815-176614.")
    D["arm_B_adapted_disjointness_proof"]["step_5_honest_narrowing"] = (
        "Arm A's direct check supplies a genuine cross-process, cross-machine "
        "determinism datum on this machine for this decoder path. That NARROWS "
        "Arm B's gap; it does NOT CLOSE it, because shard 5000 is a DIFFERENT "
        "shard with a different CTRStream key and a different trial stream. "
        "This task does not close Arm B's gap and does not upgrade the check.")
    log(f"[armB step2] {'PASS' if step2_pass else 'FAIL'}")
    if not arm_b_pass:
        D["abort"] = ("Arm B adapted disjointness proof FAILED. AGENTS.md rule 5: "
                      "infrastructure_error / invalid_measurement, never "
                      "mathematical evidence. Aborted before any Arm B statistic.")
        with open(out_disj, "w") as fh:
            json.dump(D, fh, indent=1)
        raise SystemExit("FAIL-CLOSED ABORT: Arm B disjointness proof failed.")

    # ---- F[:, 0:n_e-1] structural invariant, all eight combinations ------
    f_checks = []
    for shard in (SHARD_A, SHARD_B):
        Fd, Fu = F[(shard, "defected")], F[(shard, "undefected")]
        for w, a, b in WINDOWS:
            sub_d = Fd[a:b, 0:n_e - 1]
            sub_u = Fu[a:b, 0:n_e - 1]
            mism = int(np.count_nonzero(sub_d != sub_u))
            f_checks.append(dict(shard=shard, window=w, index_range=f"[{a}:{b})",
                                 trials_checked=int(b - a),
                                 blocks_checked_per_trial=int(n_e - 1),
                                 total_elements_checked=int((b - a) * (n_e - 1)),
                                 mismatch_count=mism,
                                 shapes_match=bool(sub_d.shape == sub_u.shape),
                                 verdict="PASS" if mism == 0 else "FAIL"))
    f_pass = all(c["verdict"] == "PASS" for c in f_checks)
    D["f_structural_invariant"] = dict(
        rule=("F[:, 0:n_e-1] (all blocks except the last) must be bit-identical, "
              "elementwise, between the defected and undefected decode of the "
              "SAME trial on the SAME shard, on every retained trial of every "
              "retained window (EV-HQC-3a0372 O11)."),
        coverage="all eight (shard, window) combinations",
        checks=f_checks, overall_status="PASS" if f_pass else "FAIL")
    log(f"[F invariant] {'PASS' if f_pass else 'FAIL'}")

    # ---- one-call vs two-call batch structure check ----------------------
    bs_checks = []
    for shard in (SHARD_A, SHARD_B):
        for variant in ("defected", "undefected"):
            for w, a, b in WINDOWS:
                sl = S[(shard, variant)][a:b]
                standalone = np.array(sl.tolist(), dtype=np.int64)
                bh_slice = sa.batch_hists(sl, n_e, NB)
                bh_alone = sa.batch_hists(standalone, n_e, NB)
                T = b - a
                edges = np.linspace(0, T, NB + 1).astype(int)
                widths = np.diff(edges)
                bs_checks.append(dict(
                    shard=shard, variant=variant, window=w, T=int(T),
                    n_batches=int(NB),
                    batch_hists_slice_equals_standalone_copy=bool(
                        np.array_equal(bh_slice, bh_alone)),
                    all_batch_widths_equal=bool(len(set(widths.tolist())) == 1),
                    batch_width=int(widths[0]),
                    batch_width_equals_T_over_200=bool(int(widths[0]) == T // NB)))
    bs_pass = all(c["batch_hists_slice_equals_standalone_copy"]
                  and c["all_batch_widths_equal"]
                  and c["batch_width_equals_T_over_200"] for c in bs_checks)
    D["one_call_vs_two_call_batch_structure_check"] = dict(
        what=("For each retained window: (a) sa.batch_hists applied to a "
              "standalone np.array COPY of that window's per-trial S must be "
              "bit-identical to sa.batch_hists applied to the slice view taken "
              "out of the 75000-length array; (b) the batch-edge vector "
              "np.linspace(0, T, 201).astype(int) must give 200 batches all of "
              "width exactly T/200, which is the batch structure a dedicated "
              "T-trial call would produce."),
        checks=bs_checks, overall_status="PASS" if bs_pass else "FAIL",
        limitation_named_regardless=(
            "DECLARED LIMITATION, INDEPENDENT OF THIS CHECK'S OUTCOME. In every "
            "historical cell the two T-points of a local exponent came from "
            "DIFFERENT calls in DIFFERENT tasks and processes; in all four fresh "
            "cells both T-points are sliced from ONE call in ONE process. The "
            "check above shows the batch STRUCTURE is the same; it does not and "
            "cannot show the two procedures are identical in every respect."))
    log(f"[batch structure] {'PASS' if bs_pass else 'FAIL'}")

    # =====================================================================
    # statistics -- per shard, per window; NO cross-shard pooling
    # =====================================================================
    per_shard = {}
    p_calibration_mean_S = None
    for shard in (SHARD_A, SHARD_B):
        per_window = {}
        for w, a, b in WINDOWS:
            Sd = S[(shard, "defected")][a:b]
            Su = S[(shard, "undefected")][a:b]
            Hd, Bd = mp.arm_hists(sa, Sd, n_e, NB)
            Hu, Bu = mp.arm_hists(sa, Su, n_e, NB)
            ks = sorted(set(sa.evaluable_k(Hd, n_e)) & set(sa.evaluable_k(Hu, n_e))
                        & set(K_RANGE_AUTHORIZED))
            st = mp.matched_pair_stats(measure, n_e, ks,
                                       measure.comb_matrix(n_e, ks),
                                       Hd, Bd, Hu, Bu)
            per_window[w] = dict(
                index_range=f"[{a}:{b})", start=a, stop=b, T=int(b - a),
                jack_batch_size=int((b - a) // NB), n_batches=int(NB),
                evaluable_k=ks, m_reachable=(M in ks),
                mean_per_trial_S_defected=float(np.mean(Sd)),
                mean_per_trial_S_undefected=float(np.mean(Su)),
                S_histogram_defected=[int(x) for x in Hd],
                S_histogram_undefected=[int(x) for x in Hu],
                per_k=st,
                primary_cell_k17=(mp.cell(st, M) if M in st["ks"] else None))
            if shard == SHARD_A and w == "P2":
                p_calibration_mean_S = float(np.mean(Su))
        per_shard[f"shard_{shard}"] = per_window
    R["per_shard_per_window"] = per_shard
    R["no_cross_shard_pooling_note"] = (
        "NO POOLED statistic appears anywhere in this file. Part A never pools "
        "across shards.")

    # ---- the four fresh local exponents ---------------------------------
    def se17(shard, w):
        c = per_shard[f"shard_{shard}"][w]["primary_cell_k17"]
        return None if c is None else c["se_paired"]

    cells = {}
    for shard in (SHARD_A, SHARD_B):
        for reg, (wlo, whi) in REGIMES.items():
            tlo = wins[wlo][1] - wins[wlo][0]
            thi = wins[whi][1] - wins[whi][0]
            se_lo, se_hi = se17(shard, wlo), se17(shard, whi)
            cells[f"alpha_{shard}_{reg}"] = dict(
                shard=shard, regime=reg,
                window_lo=wlo, window_lo_range=per_shard[f"shard_{shard}"][wlo]["index_range"],
                window_hi=whi, window_hi_range=per_shard[f"shard_{shard}"][whi]["index_range"],
                T_lo=tlo, T_hi=thi,
                jack_batch_size_lo=tlo // NB, jack_batch_size_hi=thi // NB,
                se_paired_k17_lo=se_lo, se_paired_k17_hi=se_hi,
                diff_k17_lo=per_shard[f"shard_{shard}"][wlo]["primary_cell_k17"]["diff"],
                diff_k17_hi=per_shard[f"shard_{shard}"][whi]["primary_cell_k17"]["diff"],
                local_exponent_alpha=two_point_alpha(se_lo, se_hi, tlo, thi),
                method=("alpha = -[log(SE_hi) - log(SE_lo)] / [log(T_hi) - "
                        "log(T_lo)] on se_paired at k=17; the identical 2-point "
                        "OLS-in-log-log method TASK-20260814-8bbdd2 and "
                        "TASK-20260815-e61cca used. Not re-derived, not varied."),
                cross_regime=(reg == "N" if shard == SHARD_A else reg == "P"))

    aP = [cells[f"alpha_{SHARD_A}_P"]["local_exponent_alpha"],
          cells[f"alpha_{SHARD_B}_P"]["local_exponent_alpha"]]
    aN = [cells[f"alpha_{SHARD_A}_N"]["local_exponent_alpha"],
          cells[f"alpha_{SHARD_B}_N"]["local_exponent_alpha"]]
    a5 = [cells[f"alpha_{SHARD_A}_P"]["local_exponent_alpha"],
          cells[f"alpha_{SHARD_A}_N"]["local_exponent_alpha"]]
    a8 = [cells[f"alpha_{SHARD_B}_P"]["local_exponent_alpha"],
          cells[f"alpha_{SHARD_B}_N"]["local_exponent_alpha"]]
    R["four_fresh_local_exponents"] = cells
    R["preregistered_contrasts"] = dict(
        regime_main_effect=dict(
            definition="mean(P cells) - mean(N cells)",
            value=_f(np.mean(aP) - np.mean(aN)),
            mean_P_cells=_f(np.mean(aP)), mean_N_cells=_f(np.mean(aN))),
        shard_main_effect=dict(
            definition="mean(5000 cells) - mean(8002 cells)",
            value=_f(np.mean(a5) - np.mean(a8)),
            mean_5000_cells=_f(np.mean(a5)), mean_8002_cells=_f(np.mean(a8))),
        interaction=dict(
            definition=("(alpha(5000,P) - alpha(5000,N)) - "
                        "(alpha(8002,P) - alpha(8002,N))"),
            value=_f((a5[0] - a5[1]) - (a8[0] - a8[1]))))
    R["historical_cells_cited_never_recomputed"] = HISTORICAL_CITED
    R["replication_comparisons"] = dict(
        note=("FIRST fresh-range replications of an existing cell at the same "
              "(shard, regime) in this task family. Reported as observations; "
              "no adjudication is made here."),
        shard_5000_regime_P=dict(
            fresh=cells[f"alpha_{SHARD_A}_P"]["local_exponent_alpha"],
            historical_cited=HISTORICAL_CITED["shard_5000_regime_P"]["alpha"],
            source=HISTORICAL_CITED["shard_5000_regime_P"]["source"],
            fresh_minus_historical=_f(
                cells[f"alpha_{SHARD_A}_P"]["local_exponent_alpha"]
                - HISTORICAL_CITED["shard_5000_regime_P"]["alpha"])),
        shard_8002_regime_N=dict(
            fresh=cells[f"alpha_{SHARD_B}_N"]["local_exponent_alpha"],
            historical_cited=HISTORICAL_CITED["shard_8002_regime_N"]["alpha"],
            source=HISTORICAL_CITED["shard_8002_regime_N"]["source"],
            fresh_minus_historical=_f(
                cells[f"alpha_{SHARD_B}_N"]["local_exponent_alpha"]
                - HISTORICAL_CITED["shard_8002_regime_N"]["alpha"])))

    # ---- Part B's calibration input, measured here ----------------------
    R["part_b_p_calibration_input"] = dict(
        rule=("p = (mean per-trial S of the REAL, UNDEFECTED arm of shard 5000 "
              "on window P2, indices [35000:45000), T=10000) / n_e, n_e=56. "
              "Frozen in design.md before any Part B replicate."),
        mean_per_trial_S_real_undefected_5000_P2=p_calibration_mean_S,
        n_e=n_e,
        p=(None if p_calibration_mean_S is None else p_calibration_mean_S / n_e))

    R["hard_invariants"] = hard_inv
    R["call_timings"] = call_timings
    d2d3_clean = all(v["D2_violations"] == 0 and v["D3_violations"] == 0
                     for v in hard_inv.values())
    no_trunc = all(not v["truncated"] and v["trials_done"] == v["trials_requested"]
                   for v in hard_inv.values())

    all_cells_finite = all(
        per_shard[f"shard_{s}"][w]["primary_cell_k17"] is not None
        and per_shard[f"shard_{s}"][w]["primary_cell_k17"]["se_paired"] is not None
        and per_shard[f"shard_{s}"][w]["primary_cell_k17"]["se_paired"] > 0
        and per_shard[f"shard_{s}"][w]["primary_cell_k17"]["diff"] is not None
        for s in (SHARD_A, SHARD_B) for w, _, _ in WINDOWS)

    spent_core, spent_wall = core_seconds() - c0, time.time() - t0
    R["budget"] = dict(
        core_seconds_authorized=CORE_SECOND_BUDGET,
        core_seconds_spent_part_A=round(spent_core, 3),
        wall_seconds_authorized=WALL_SECOND_BUDGET,
        wall_seconds_spent_part_A=round(spent_wall, 3),
        within_core_second_budget=spent_core <= CORE_SECOND_BUDGET,
        within_wall_budget=spent_wall <= WALL_SECOND_BUDGET,
        measured_not_estimated=True)

    ok = (R["fail_closed_selftests"]["sha256_pin_mismatch"]["verdict"] == "PASS"
          and R["fail_closed_selftests"]["injection_invariant_mismatch"]["verdict"] == "PASS"
          and R["injection"]["wrapper_calls_unmodified_function"]
          and R["provenance"]["stage_a_sha256_match"]
          and R["provenance"]["measure_sha256_match"]
          and R["provenance"]["matched_pair_py_sha256_match"]
          and arm_a_pass and arm_b_pass and f_pass and d2d3_clean and no_trunc
          and all_cells_finite
          and D["window_arithmetic"]["verdict"] == "PASS"
          and D["high_water_rederivation"]["verdict"] == "PASS")
    R["validity"] = dict(
        status="valid_measurement" if ok else "invalid_measurement",
        failure_class=(None if ok else "invalid_measurement"),
        gates=dict(arm_A_direct_disjointness="PASS" if arm_a_pass else "FAIL",
                   arm_B_adapted_disjointness="PASS" if arm_b_pass else "FAIL",
                   f_structural_invariant="PASS" if f_pass else "FAIL",
                   d2_d3_clean_all_six_calls=bool(d2d3_clean),
                   no_call_truncated=bool(no_trunc),
                   batch_structure_check="PASS" if bs_pass else "FAIL",
                   all_eight_cells_finite_positive_se=bool(all_cells_finite)),
        reason=("All pre-registered mechanically-sound criteria met (design.md "
                "Section 5)." if ok else
                "One or more pre-registered mechanically-sound criteria "
                "(design.md Section 5) were not met -- see gates above. Per "
                "AGENTS.md rule 5 a gate failure is an infrastructure/"
                "measurement outcome, never mathematical evidence."))
    D["validity_summary"] = R["validity"]["gates"]
    D["one_call_vs_two_call_batch_structure_check"]["overall_status"] = (
        "PASS" if bs_pass else "FAIL")

    R["finished_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    D["finished_at_utc"] = R["finished_at_utc"]
    with open(out_main, "w") as fh:
        json.dump(R, fh, indent=1)
    with open(out_disj, "w") as fh:
        json.dump(D, fh, indent=1)
    log(f"[done] PART A -> {out_main}, {out_disj}  "
        f"core-s={spent_core:.2f}/{CORE_SECOND_BUDGET} "
        f"wall={spent_wall:.1f}s/{WALL_SECOND_BUDGET}s "
        f"validity={R['validity']['status']}")
    for key, c in cells.items():
        log(f"[alpha] {key} = {c['local_exponent_alpha']}")
    log(f"[contrasts] {json.dumps({k: v['value'] for k, v in R['preregistered_contrasts'].items()})}")
    log(f"[p_calibration] mean_S={p_calibration_mean_S} "
        f"p={R['part_b_p_calibration_input']['p']!r}")
    return R


if __name__ == "__main__":
    main()
