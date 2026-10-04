"""
Stage-1 own-enumeration data generation for EXP-RELN-141a86 (TASK-20260907-8fd098).

PROTOCOL DEVIATION, DISCLOSED (see implementation.md): specification.yaml
assigns own-enumeration to "Stage 0e", a separate stage with its own run
directory and budget. This handoff's write_scope authorizes ONLY
experiments/EXP-RELN-141a86/runs/RUN-RELN-141a86-stage1*/ and source/, not a
new stage0e run directory. Because (a) sibling_enumeration's primary source
(EXP-RELN-f202be) was checked and found field-incompatible (different
convention: m=2 x-class signed energy/forced-negation-gap statistics, not the
Delta/E_m/R_k field set this contract's adapter validates against -- see
implementation.md for the specific fields checked and found absent), and
(b) EXP-FB3-001 has no N=2^20 run at all, the ONLY way to get real held-out
2^20 data for ANY arm in this dispatch is to generate it here, inside the
Stage-1 run, using the already-frozen, already-written count_vectors.py
(exact FFT-based cyclic convolution, Stage-0b/0e module, unmodified). This
module is new (written for this dispatch) but calls count_vectors.py
unchanged.

IMPORTANT SCOPE HONESTY: own enumeration in Z/N (a plain cyclic group) is a
valid, honest surrogate ONLY for arms whose definition does not depend on
genuine elliptic-curve x-coordinate/group-law structure:
  - matched_random / ZN_random_relabelled (a uniformly random B-subset of a
    group of order N): HEUR-H1's random-base model is stated group-agnostic
    to leading order, so a random subset of Z/N is a legitimate stand-in for
    a random subset of E(F_p), and this is exactly what the contract's own
    held_out_transfer_anchor control asks for ("INV-A1 evaluated on the
    RANDOM arms at 2^20").
  - ZN_interval_1_to_B (the arithmetic-progression-in-Z/N positive control):
    this IS defined natively in Z/N; no surrogate needed.
  - small_multiples_log_space_with_decay_ladder: log-space construction, not
    reproduced here (deferred; see execution-report.md/implementation.md).
This module does NOT attempt to synthesize E_x_interval_high_bit_interval,
E_small_height, or E_coset_union data: those are elliptic-curve-native
constructions (x-coordinates of curve points under the curve group law); a
Z/N arithmetic interval is qualitatively DIFFERENT structure (it IS the
ZN_interval positive control, which the contract predicts and requires to
depart from INV-A1) and substituting it for the E-arms would be exactly the
"convention mismatch resolved by rescaling"/geometry-substitution the
invalidation_rules forbid. Consequence, stated plainly: the E x-interval
arms (fb3_unsigned_m3 pack, high_bit_interval/small_height/coset_union
geometries) have NO available held-out 2^20 data in this run -- their
Pareto front is fitted on committed FB3 N<=2^18 training data only, and
every held-out field for those rows is reported as
"not_available_no_2^20_fb3_data", never estimated or substituted.

Determinism: every random draw (matched-random null draws, the 4 curve-
analog replicate draws) is seeded by
sha256('EXP-RELN-141a86|stage1-own-enum|' + arm + '|' + N + '|' + B + '|' +
draw_role + '|' + draw_index) truncated to 32 bits, per this contract's own
replication.seeds pattern (adapted for this new arm/table rather than
reusing a different seed already assigned to a different table).
"""
from __future__ import annotations

import hashlib
import math
import random
import statistics
from typing import Dict, List

import count_vectors as cv

# Rungs: nextprime(2**e) so every dilation of Z/N is a bijection (N prime),
# per specification.yaml's own_enumeration convention clause.
RUNG_PRIMES = {14: 16411, 16: 65537, 18: 262147, 20: 1048583}
TRAINING_RUNGS = (14, 16, 18)
HELD_OUT_RUNG = 20
M_ARITY = 3  # this contract's fixed m=3 own-enumeration convention
N_NULL_DRAWS = 200
N_CURVE_REPLICATES = 4


def _seed_int(*parts) -> int:
    s = "EXP-RELN-141a86|stage1-own-enum|" + "|".join(str(p) for p in parts)
    h = hashlib.sha256(s.encode("utf-8")).digest()
    return int.from_bytes(h[:4], "big")


def b_ladder(N: int) -> Dict[str, int]:
    b0 = math.ceil((6 * N) ** (1.0 / 3.0))
    return {"B_half": max(2, round(b0 / 2)), "B0": b0, "B_double": 2 * b0}


def _random_subset(N: int, B: int, seed: int) -> List[int]:
    rng = random.Random(seed)
    return rng.sample(range(N), B)


def _interval_subset(N: int, B: int, offset: int = 0) -> List[int]:
    return [(offset + i) % N for i in range(B)]


def _cell_statistics(D: List[int], N: int) -> Dict[str, float]:
    counts = cv.count_vector_convolution(D, N, M_ARITY)
    st = cv.stats_from_count_vector(counts, N)
    mean = st["mean"]
    conc = st["concentration"]
    delta = cv.dispersion_delta(mean, conc)
    e3 = N * (conc + mean)
    r_k = {f"R_{k}": sum(1 for c in counts if c >= k) for k in range(1, 9)}
    out = {"Delta": delta, "E_3": e3, "coverage": st["coverage"], **r_k}
    return out


def _null_distribution(N: int, B: int, arm: str) -> Dict[str, Dict[str, float]]:
    """200 matched-random draws -> {statistic: {null_mean, null_sd}}."""
    samples: Dict[str, List[float]] = {}
    for i in range(N_NULL_DRAWS):
        seed = _seed_int(arm, N, B, "null", i)
        D = _random_subset(N, B, seed)
        stats = _cell_statistics(D, N)
        for k, v in stats.items():
            samples.setdefault(k, []).append(v)
    out = {}
    for k, vals in samples.items():
        mean_v = statistics.fmean(vals)
        sd_v = statistics.pstdev(vals) if len(vals) > 1 else 0.0
        out[k] = {"null_mean": mean_v, "null_sd": sd_v}
    return out


def _atomic_append_jsonl(path: str, obj: Dict) -> None:
    import json
    with open(path, "a") as f:
        f.write(json.dumps(obj) + "\n")
        f.flush()
        import os
        os.fsync(f.fileno())


def _load_jsonl_keys(path: str, key_fn):
    import json
    import os
    done = set()
    rows = []
    if not os.path.exists(path):
        return done, rows
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue  # a torn last line from a kill mid-write; skip, never guess
            rows.append(obj)
            done.add(key_fn(obj))
    return done, rows


def build_own_enumeration_rows_resumable(cache_path: str, progress_cb=None) -> List[Dict]:
    """
    Same rows as build_own_enumeration_rows(), but each completed row is
    appended to `cache_path` (JSONL) immediately and durably (write+flush+
    fsync), and rows already present in `cache_path` from a prior (killed)
    attempt are loaded and skipped rather than recomputed -- this is the
    Stage-1 data-generation analogue of grammar_engine_checkpoint.py's
    per-level checkpointing, at per-row granularity, so a container restart
    loses at most the one row in flight.
    """
    def key_fn(r):
        return (r["arm"], r["N"], r["B"], r["curve_index"])

    done_keys, cached_rows = _load_jsonl_keys(cache_path, key_fn)
    rows: List[Dict] = list(cached_rows)

    for rung, N in RUNG_PRIMES.items():
        held_out = (rung == HELD_OUT_RUNG)
        ladder = b_ladder(N)
        for b_label, B in ladder.items():
            M = math.comb(B + M_ARITY - 1, M_ARITY)
            mu = M / N
            plan = [("ZN_interval", None, 0)]
            plan += [("ZN_random_relabelled", "curve", ci) for ci in range(N_CURVE_REPLICATES)]
            plan += [("E_matched_random_analog", "curve", ci) for ci in range(N_CURVE_REPLICATES)]
            # skip null-distribution recompute if every plan row for this
            # (rung, b_label) is already cached
            need_null = any(("__null_needed__", N, B, ci) not in done_keys for _, _, ci in plan)
            all_cached = all((arm, N, B, ci) in done_keys for arm, _, ci in plan)
            null_dist = None
            for arm, role, ci in plan:
                key = (arm, N, B, ci)
                if key in done_keys:
                    continue
                if null_dist is None:
                    if progress_cb:
                        progress_cb(f"building null distribution rung={rung} b={b_label} N={N} B={B}")
                    null_dist = _null_distribution(N, B, arm=f"null_{rung}_{b_label}")
                if arm == "ZN_interval":
                    D = _interval_subset(N, B, offset=0)
                elif role == "curve":
                    seed = _seed_int(arm, N, B, "curve", ci)
                    D = _random_subset(N, B, seed)
                else:
                    raise AssertionError(f"unknown plan entry {arm!r}/{role!r}")
                stats = _cell_statistics(D, N)
                null_sd = {k: null_dist[k]["null_sd"] for k in stats}
                null_mean = {k: null_dist[k]["null_mean"] for k in stats}
                row = {
                    "convention": "enum_zn_m3", "arm": arm,
                    "N": N, "B": B, "m": M_ARITY, "M": M, "mu": mu,
                    "rung_log2N": rung, "b_ladder_label": b_label,
                    "held_out": held_out, "curve_index": ci,
                    "statistics": stats, "null_mean": null_mean, "null_sd": null_sd,
                    "source": "own_enumeration_stage1_inline",
                }
                _atomic_append_jsonl(cache_path, row)
                rows.append(row)
                done_keys.add(key)
                if progress_cb:
                    progress_cb(f"row done: arm={arm} rung={rung} b={b_label} ci={ci}")
    return rows


def build_own_enumeration_rows() -> List[Dict]:
    """
    Builds rows for three arms, all convention 'enum_zn_m3' (Z/N native, m=3):
      - ZN_interval          (arithmetic-progression positive control)
      - ZN_random_relabelled (structure-destruction null, 4 curve-analog draws)
      - E_matched_random_analog (random-base HEUR-H1 anchor; NOT an E-arm
        claim -- an explicitly-labeled Z/N surrogate used only for the
        held_out_transfer_anchor control's "INV-A1 evaluated on the RANDOM
        arms at 2^20" requirement)
    at rungs 14/16/18 (training) and 20 (held out), full B-ladder.
    Every row carries its own null_mean/null_sd per statistic from a
    200-draw matched-random null built at that exact (N, B).
    """
    rows: List[Dict] = []
    for rung, N in RUNG_PRIMES.items():
        held_out = (rung == HELD_OUT_RUNG)
        ladder = b_ladder(N)
        for b_label, B in ladder.items():
            M = math.comb(B + M_ARITY - 1, M_ARITY)
            mu = M / N
            null_dist = _null_distribution(N, B, arm=f"null_{rung}_{b_label}")

            def make_row(arm, convention, D, curve_index):
                stats = _cell_statistics(D, N)
                null_sd = {k: null_dist[k]["null_sd"] for k in stats}
                null_mean = {k: null_dist[k]["null_mean"] for k in stats}
                return {
                    "convention": convention,
                    "arm": arm,
                    "N": N, "B": B, "m": M_ARITY, "M": M, "mu": mu,
                    "rung_log2N": rung, "b_ladder_label": b_label,
                    "held_out": held_out,
                    "curve_index": curve_index,
                    "statistics": stats,
                    "null_mean": null_mean,
                    "null_sd": null_sd,
                    "source": "own_enumeration_stage1_inline",
                }

            # ZN_interval: single deterministic base, offset 0 -- but the
            # contract's replication clause disallows resampling a
            # deterministic geometry, so this is ONE replicate, curve_index
            # fixed to 0 and reported as such (not averaged with random draws).
            rows.append(make_row(
                "ZN_interval", "enum_zn_m3",
                _interval_subset(N, B, offset=0), curve_index=0))

            # ZN_random_relabelled: 4 independent random draws (curve-analog).
            for ci in range(N_CURVE_REPLICATES):
                seed = _seed_int("ZN_random_relabelled", N, B, "curve", ci)
                D = _random_subset(N, B, seed)
                rows.append(make_row("ZN_random_relabelled", "enum_zn_m3", D, ci))

            # E_matched_random_analog: 4 independent random draws, DISTINCT
            # seed stream from both the null draws and the relabelled-arm
            # draws above (no reuse across roles).
            for ci in range(N_CURVE_REPLICATES):
                seed = _seed_int("E_matched_random_analog", N, B, "curve", ci)
                D = _random_subset(N, B, seed)
                rows.append(make_row("E_matched_random_analog", "enum_zn_m3", D, ci))

    return rows


if __name__ == "__main__":
    import json
    import sys
    import time

    t0 = time.time()
    rows = build_own_enumeration_rows()
    dt = time.time() - t0
    print(f"own-enumeration self-test: {len(rows)} rows built in {dt:.1f}s", file=sys.stderr)
    by_arm: Dict[str, int] = {}
    for r in rows:
        by_arm[r["arm"]] = by_arm.get(r["arm"], 0) + 1
    print(json.dumps(by_arm, indent=2), file=sys.stderr)
    print("own_enumeration_stage1.py self-test: OK (no exceptions)", file=sys.stderr)
