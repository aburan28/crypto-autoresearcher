"""GOAL-MD5-001 BATCH-ebac02, TASK-20260822-767bb1 -- phase 1 measurement.

RC-1 fixed-word-seed sweep + RC-4 static mask check + RC-5 null-object
control, on the batch-5 corrected construction (R1_SEP10: i_word=2,
j_word=12, S=8, p=3, m=12, k=20) which PASSED the GATE-PO2 two-directional
dependence gate and then FAILED CTL-PO5 at 8 raw pre-certificate candidates
against a declared ceiling of 4 (DEC-20260822-40bf14).

The construction is NOT redesigned here: the step algebra, split point, and
matching quantity are reused verbatim from harness/run_md4_ceiling_v2 (READ-
ONLY import). Only the fixed-word seed varies.

Terms (a)-(h) of DEC-20260822-40bf14 next_actions item 3 are binding; see
the module docstrings and the manifest for where each is applied.

caveat_refs (SC-5 lineage) are emitted in every manifest from the start.
"""

import hashlib
import json
import os
import platform
import random
import sys
import time

from harness.run_md4_ceiling_v2 import (
    _IV, _M32, _f, _rotl, _rotr, _r1_tables,
    ConstructionParams, HELD_FIXED_INDICES, R1_SEP10,
    code_path_fingerprint, component_step, fixed_word_generation,
    forward_full_round1, forward_step, backward_step, generate_target,
    mitm_search,
)

CAVEAT_REFS = [
    "KN-TECH-bb7e9f (ANOM-1: the batch-4 S=9 declared matching quantity is "
    "proven independent of one free word; the detecting control and the "
    "design-pitfall boundary are recorded there)",
    "DEC-20260821-1215e5 F-4 (binding forward-citation constraint on "
    "uncaveated machine-readable metrics from BATCH-af29f6)",
    "DEC-20260822-40bf14 (batch 5 close: GATE-PO2 passed on all nine "
    "clauses; CTL-PO5(b) failed at 8 raw candidates against ceiling 4)",
]

# The batch-5 corrected construction (frozen by the batch 5 gate decision).
BASE_PARAMS = dict(R1_SEP10)  # i_word=2, j_word=12, S=8, p=3, m=12, k=20

# Declared before acquisition (term a): the injectivity criterion is
#   distinct >= (1 - EPS) * 2^k_window   at BOTH 32-bit and window/m-bit
#   resolution, with k_window = k1 = k2 = 4 (16 window values per direction).
EPS = 0.25
INJ_THRESHOLD = int((1 - EPS) * 16)  # = 12 of 16, both resolutions

# Declared before acquisition (term b): an observed integer departs from its
# pre-registered prediction beyond TOLERENCE when |obs - pred| > TOLERENCE.
TOLERANCE = 1

# The uniformity premise, numbered (term d): the fixed-word draws and the
# target low draws across the seed schedule behave uniformly at the
# granularity the sweep depends on.
HEUR_H3 = ("HEUR-H3: the 100 fixed-word generations (seed schedule below) "
           "and the 100 paired target low draws (target_seed := fixed-word "
           "seed) have no pathological duplication or non-uniformity at the "
           "4-bit granularity the sweep measures. Justification: seeds are "
           "consecutive integers and random.Random(seed).getrandbits(32) has "
           "no published bias at this granularity; TEST: duplicate counts at "
           "the 4-bit low level and at the full-32-bit high-mask level, "
           "recorded in the raw output (a duplicate high mask or an anomalous "
           "low-draw histogram falsifies the premise at this n).")

# Seed schedule, declared before acquisition: 100 consecutive fixed-word
# seeds 20260821..20260919; target_seed := the same integer (declared
# pairing, deterministic).
SEEDS = list(range(20260821, 20260921))
FREE_BITS = 4  # the batch-5 gate scale, unchanged


def _params(primitive: str, k1: int, k2: int) -> ConstructionParams:
    return ConstructionParams(primitive=primitive, k1=k1, k2=k2,
                              **BASE_PARAMS)


# ---------------------------------------------------------------------------
# Null object (term h / RC-5): the SAME step structure with F replaced by a
# non-multiplexer mixer of the same shape (three inputs, one output, one
# 32-bit value per step): the additive mixer.
# ---------------------------------------------------------------------------

def _f_null(x: int, y: int, z: int) -> int:
    return (x + y + z) & _M32


def _forward_step_f(state, xk, s, t, add_b, func):
    a, b, c, d = state
    rotated = _rotl((a + func(b, c, d) + xk + t) & _M32, s)
    new_a = ((b + rotated) & _M32) if add_b else rotated
    return (d, new_a, b, c)


def _backward_step_f(state_next, xk, s, t, add_b, func):
    a2, b2, c2, d2 = state_next
    old_b, old_c, old_d = c2, d2, a2
    new_a = b2
    rotated = ((new_a - old_b) & _M32) if add_b else new_a
    old_a = (_rotr(rotated, s) - func(old_b, old_c, old_d) - xk - t) & _M32
    return (old_a, old_b, old_c, old_d)


def _chunk1_f(w_a, words_template, params, func):
    """chunk1_observable with the step function parameterized (func is _f
    for the primary object, _f_null for the RC-5 null object). The word
    template is the FULL 16-word list with the free words at their high
    values; word[i_word] is set to w_a."""
    shifts, consts, add_b = _r1_tables(params.primitive)
    words = list(words_template)
    words[params.i_word] = w_a
    state = _IV
    for i in range(params.S):
        state = _forward_step_f(state, words[i], shifts[i % 4], consts[i],
                                add_b, func)
    return state[params.p]


def _chunk2_f(w_b, Y, words_template, params, func):
    shifts, consts, add_b = _r1_tables(params.primitive)
    words = list(words_template)
    words[params.j_word] = w_b
    state = tuple(Y)
    for i in range(15, params.S - 1, -1):
        state = _backward_step_f(state, words[i], shifts[i % 4], consts[i],
                                  add_b, func)
    return state[params.p]


def _forward_full_round1_f(word_list, primitive, func):
    shifts, consts, add_b = _r1_tables(primitive)
    states = [_IV]
    state = _IV
    for i in range(16):
        state = _forward_step_f(state, word_list[i], shifts[i % 4],
                                consts[i], add_b, func)
        states.append(state)
    return states, state


def _mitm_search_f(params, fixed, target, words_template, func):
    """mitm_search with the step function parameterized (null object)."""
    mmask = (1 << params.m) - 1
    kmask = (1 << params.k) - 1
    hi_i = fixed["high"][params.i_word]
    hi_j = fixed["high"][params.j_word]
    table = {}
    for low_a in range(1 << params.k1):
        v = _chunk1_f(hi_i | low_a, words_template, params, func)
        table.setdefault(v & mmask, []).append((hi_i | low_a, v & kmask))
    window_hits = 0
    raw_solutions = []
    for low_b in range(1 << params.k2):
        v = _chunk2_f(hi_j | low_b, target["Y"], words_template, params, func)
        bucket = table.get(v & mmask)
        if not bucket:
            continue
        for w_a, low_k_fwd in bucket:
            window_hits += 1
            if low_k_fwd == (v & kmask):
                raw_solutions.append((w_a, hi_j | low_b))
    return {"raw_solution_count": len(raw_solutions),
            "raw_solutions": raw_solutions,
            "matching_window_hits": window_hits}


def _generate_target_f(target_seed, fixed, params, words_template, func):
    """generate_target with the step function parameterized (null object).
    The draw procedure is IDENTICAL (same rng, same order)."""
    rng = random.Random(target_seed)
    low_i = rng.getrandbits(params.k1)
    low_j = rng.getrandbits(params.k2)
    word_list = list(words_template)
    word_list[params.i_word] = fixed["high"][params.i_word] | low_i
    word_list[params.j_word] = fixed["high"][params.j_word] | low_j
    states, state16 = _forward_full_round1_f(word_list, params.primitive,
                                              func)
    component = states[params.S][params.p]
    return {"Y": tuple(state16),
            "component_lowk": component & ((1 << params.k) - 1),
            "target_lowk": component & ((1 << params.k) - 1),
            "true_word_i": word_list[params.i_word],
            "true_word_j": word_list[params.j_word]}


# ---------------------------------------------------------------------------
# RC-4 -- the static per-F-application mask check (pre-run, no search).
# ---------------------------------------------------------------------------

def rc4_bit_sensitivity(params: ConstructionParams, words_template: list,
                        func) -> dict:
    """Which of the free word's low FREE_BITS bits survive into the declared
    component (state_S[p])? Two parts, both static (pre-run, no search):

    (1) MEASURED: for each low-bit position r, evaluate the observable at
    low = 1<<r and low = 0 (all other low bits 0) and record whether ANY
    output bit changes. This bounds the distinct count at 32-bit resolution
    by 2^(number of surviving bits) and names exactly which bits die.

    (2) MODELED: a carry-free (GF(2), first-order) linearization of the step
    algebra, linearized on the concrete low=0 trajectory. The step is
        new_state = (d, new_a, b, c)
        new_a = (b +) rotl(a + F(b,c,d) + xk + t, s)
    so the register layout is (a, b, c, d) = (0, 1, 2, 3) with
        F(x, y, z) = (x&y) | (~x&z),  x := b, y := c, z := d,
    and the per-bit survival coefficients at an F application are
        x-argument (register b): y_p XOR z_p  == (c ^ d)
        y-argument (register c): x_p          ==  b
        z-argument (register d): 1 - x_p      == ~b
        a-argument (register a): direct addend, full (all ones).
    Position update per step: 0->1 (sum), 1->1 (b-addend, MD5 only) AND
    1->2 (register), 2->3 (register), 3->0 (register). Contributions that
    enter the sum are rotated by the step's shift; register paths are not.
    Masks of co-located contributions combine by XOR (carry-free). The free
    word enters at step i_word as xk: bit r lands in new_a at bit
    (r + s_i) mod 32 with coefficient 1.

    The model PREDICTS the per-bit survival mask into state_S[p]; the
    two-point sensitivity MEASURES it. Disagreement is expected and
    informative (the model is carry-free; carries and higher-order terms are
    precisely what it omits) and is recorded per bit as a MODELED-vs-
    MEASURED adjudication (term b), labeled as such.

    NOTE ON LINEAGE: the first implementation of this trace mapped the
    registers to the wrong F arguments (tuple position 1 was labeled the
    y-argument and position 0 the select) and used an incorrect tag-update
    rule. It was corrected before any run of it was archived; no committed
    record contains the first version. The correction is disclosed in the
    execution report (DEV-5).
    """
    kmask_low = (1 << FREE_BITS) - 1
    hi_i = words_template[params.i_word]
    hi_j = words_template[params.j_word]

    def obs(low_i):
        wt = list(words_template)
        wt[params.i_word] = hi_i | (low_i & kmask_low)
        return _chunk1_f(wt[params.i_word], wt, params, func)

    base = obs(0)
    surviving, dying = [], []
    for r in range(FREE_BITS):
        if obs(1 << r) != base:
            surviving.append(r)
        else:
            dying.append(r)

    # ---- MODELED: carry-free first-order survival on the low=0 trajectory
    shifts, consts, add_b = _r1_tables(params.primitive)
    words = list(words_template)
    words[params.i_word] = hi_i  # low = 0
    is_null = func is _f_null
    trace = []
    final_masks = {}
    for r in range(FREE_BITS):
        s_i = shifts[params.i_word % 4]
        entries = {1: 1 << ((r + s_i) % 32)}  # position -> 32-bit mask
        state = _IV
        for i in range(params.S):
            a, b, c, d = state
            if i > params.i_word:
                b_reg, c_reg, d_reg = b, c, d
                s_j = shifts[i % 4]
                new = {}
                for q, m in entries.items():
                    if m == 0:
                        continue
                    if q == 0:
                        sum_mask = m
                        arg, mask_val, expr = "a (direct addend)", _M32, "1"
                    elif q == 1:
                        sum_mask = m & (c_reg ^ d_reg)
                        if add_b:
                            sum_mask ^= m  # the b-addend carries it verbatim
                        arg, mask_val, expr = "x (select b)", c_reg ^ d_reg, \
                            "(c ^ d) [+ b-addend verbatim]"
                    elif q == 2:
                        sum_mask = m & b_reg
                        arg, mask_val, expr = "y (register c)", b_reg, "b"
                    else:
                        sum_mask = m & ((~b_reg) & _M32)
                        arg, mask_val, expr = "z (register d)", \
                            (~b_reg) & _M32, "~b"
                    if is_null:
                        # affine mixer x+y+z: every argument contributes
                        # verbatim; the multiplexer masks do not exist
                        sum_mask = m
                        arg, mask_val, expr = "affine (all args verbatim)", \
                            _M32, "1"
                    if sum_mask:
                        new[1] = new.get(1, 0) ^ \
                            _rotl(sum_mask, s_j) & _M32
                    if q == 1:
                        new[2] = new.get(2, 0) ^ m
                    elif q == 2:
                        new[3] = new.get(3, 0) ^ m
                    elif q == 3:
                        new[0] = new.get(0, 0) ^ m
                    trace.append({
                        "input_bit": r, "step_0indexed": i,
                        "register_position_before_step": q,
                        "tagged_register_F_argument": arg,
                        "entry_mask_hex": format(m & _M32, "08x"),
                        "concrete_mask_value_hex": format(
                            mask_val & _M32, "08x"),
                        "mask_expression": expr,
                        "sum_contribution_hex": format(
                            sum_mask & _M32, "08x"),
                    })
                entries = {k: v for k, v in new.items() if v}
            state = _forward_step_f(state, words[i], shifts[i % 4],
                                    consts[i], add_b, func)
        final_masks[r] = entries.get(params.p, 0)

    predicted_surviving = [r for r in range(FREE_BITS)
                           if final_masks[r] != 0]
    predicted_dying = [r for r in range(FREE_BITS) if final_masks[r] == 0]
    adjudications = []
    for r in range(FREE_BITS):
        same = (r in surviving) == (r in predicted_surviving)
        if not same:
            adjudications.append({
                "quantity": f"rc4_bit_survival_bit_{r}",
                "measured": "surviving" if r in surviving else "dying",
                "modeled": "surviving" if r in predicted_surviving
                           else "dying",
                "note": ("carry-free first-order linearization vs exact "
                         "two-point sensitivity; disagreement is the "
                         "expected signature of omitted carries / "
                         "higher-order terms, recorded per term (b)"),
            })
    return {
        "low_bit_positions_surviving_into_component": surviving,
        "low_bit_positions_dying_before_component": dying,
        "surviving_bit_count": len(surviving),
        "implied_distinct_32bit_bound": min(1 << params.k1,
                                            1 << len(surviving)),
        "modeled_predicted_surviving_bits": predicted_surviving,
        "modeled_predicted_dying_bits": predicted_dying,
        "modeled_final_component_masks_hex": {
            str(r): format(final_masks[r] & _M32, "08x")
            for r in range(FREE_BITS)},
        "modeled_vs_measured_adjudications": adjudications,
        "mask_trace_on_forward_path": trace,
        "component_tuple_position": params.p,
        "note": ("Sensitivity is MEASURED (two-point per bit, deterministic, "
                 "no search). The survival model is MODELED: carry-free "
                 "first-order linearization on the low=0 trajectory with "
                 "the concrete (c^d)/b/~b masks per F application "
                 "(F(x,y,z)=(x&y)|(~x&z), x:=b, y:=c, z:=d; the additive "
                 "null object is affine, all arguments verbatim)."),
    }


# ---------------------------------------------------------------------------
# Per-seed measurement (primary object).
# ---------------------------------------------------------------------------

def measure_seed(primitive: str, seed: int, deadline_t0: float,
                 deadline_s: float) -> dict:
    k1 = k2 = FREE_BITS
    k_ctl = 6  # the batch-5 declared CTL-PO5 scale, unchanged
    params = _params(primitive, k1, k2)
    params_ctl = _params(primitive, k_ctl, k_ctl)
    free_idx = (params.i_word, params.j_word)
    fixed = fixed_word_generation(seed, free_idx, FREE_BITS)
    words = fixed["words"]

    if time.monotonic() - deadline_t0 > deadline_s:
        raise TimeoutError(f"armed deadline ({deadline_s}s) hit before seed "
                           f"{seed} ({primitive})")

    # RC-4 FIRST (static, pre-run, no search).
    rc4 = rc4_bit_sensitivity(params, words, _f)

    # Direction A (term e: the held-fixed value is APPLIED INSIDE the word
    # template for each repetition, so CTL-PO3 byte-identity is a genuine
    # check rather than an inert label).
    rows_a = []
    for hb in HELD_FIXED_INDICES:
        wt = list(words)
        wt[params.j_word] = fixed["high"][params.j_word] | hb
        vals = [_chunk1_f(fixed["high"][params.i_word] | low, wt, params, _f)
                for low in range(1 << k1)]
        rows_a.append({
            "held_fixed_free_word_B_low": hb,
            "distinct_fwd_32bit": len(set(vals)),
            "distinct_fwd_12bit": len({v & ((1 << params.m) - 1)
                                       for v in vals}),
            "values_32bit": vals,
        })
    sig_a = [json.dumps(r["values_32bit"]) for r in rows_a]
    po3_identical = len(set(sig_a)) == 1

    # Direction B: target regenerated per held-fixed index (the batch-5
    # procedure), target_seed := seed (declared pairing).
    rows_b = []
    for ha in HELD_FIXED_INDICES:
        t_a = generate_target(seed, fixed, params, override_low_i=ha)
        vals = [_chunk2_f(fixed["high"][params.j_word] | low, t_a["Y"],
                          words, params, _f)
                for low in range(1 << k2)]
        rows_b.append({
            "held_fixed_free_word_A_low": ha,
            "distinct_bwd_32bit": len(set(vals)),
            "distinct_bwd_12bit": len({v & ((1 << params.m) - 1)
                                       for v in vals}),
        })

    # CTL-PO5 at the batch-5 declared scale k1=k2=6 (raw pre-certificate
    # candidate count -- the quantity that failed at 8 vs ceiling 4).
    target6 = generate_target(seed, fixed, params_ctl)
    mitm6 = mitm_search(params_ctl, fixed, target6)
    raw_wa = sorted({w_a for (w_a, _) in mitm6["raw_solutions"]})
    raw_wb = sorted({w_b for (_, w_b) in mitm6["raw_solutions"]})

    if time.monotonic() - deadline_t0 > deadline_s:
        raise TimeoutError(f"armed deadline ({deadline_s}s) hit during seed "
                           f"{seed} ({primitive})")

    return {
        "seed": seed,
        "primitive": primitive,
        "fixed_high_i": fixed["high"][params.i_word],
        "fixed_high_j": fixed["high"][params.j_word],
        "rc4": rc4,
        "direction_A_rows": rows_a,
        "direction_A_PO3_byte_identical": po3_identical,
        "direction_B_rows": rows_b,
        "ctl_po5_k1_k2_6": {
            "raw_candidate_count": mitm6["raw_solution_count"],
            "distinct_wA_in_raw_set": len(raw_wa),
            "distinct_wB_in_raw_set": len(raw_wb),
            "window_size": 1 << k_ctl,
            "expected_raw_count_modeled": 1 + (1 << (k_ctl + k_ctl)) / 2 ** 20,
        },
    }


def measure_seed_null(primitive: str, seed: int, deadline_t0: float,
                      deadline_s: float) -> dict:
    """RC-5: the identical measurement with F replaced by the additive
    non-multiplexer mixer of the same shape (the null object)."""
    k1 = k2 = FREE_BITS
    k_ctl = 6
    params = _params(primitive, k1, k2)
    params_ctl = _params(primitive, k_ctl, k_ctl)
    free_idx = (params.i_word, params.j_word)
    fixed = fixed_word_generation(seed, free_idx, FREE_BITS)
    words = fixed["words"]

    rc4 = rc4_bit_sensitivity(params, words, _f_null)

    rows_a = []
    for hb in HELD_FIXED_INDICES:
        wt = list(words)
        wt[params.j_word] = fixed["high"][params.j_word] | hb
        vals = [_chunk1_f(fixed["high"][params.i_word] | low, wt, params,
                          _f_null) for low in range(1 << k1)]
        rows_a.append({
            "held_fixed_free_word_B_low": hb,
            "distinct_fwd_32bit": len(set(vals)),
            "distinct_fwd_12bit": len({v & ((1 << params.m) - 1)
                                       for v in vals}),
        })
    sig_a = [json.dumps(r["distinct_fwd_32bit"]) for r in rows_a]
    po3_identical = len(set(sig_a)) == 1

    rows_b = []
    for ha in HELD_FIXED_INDICES:
        t_a = _generate_target_f(seed, fixed, params, words, _f_null)
        vals = [_chunk2_f(fixed["high"][params.j_word] | low, t_a["Y"],
                          words, params, _f_null)
                for low in range(1 << k2)]
        rows_b.append({
            "held_fixed_free_word_A_low": ha,
            "distinct_bwd_32bit": len(set(vals)),
            "distinct_bwd_12bit": len({v & ((1 << params.m) - 1)
                                       for v in vals}),
        })

    target6 = _generate_target_f(seed, fixed, params_ctl, words, _f_null)
    mitm6 = _mitm_search_f(params_ctl, fixed, target6, words, _f_null)
    raw_wa = sorted({w_a for (w_a, _) in mitm6["raw_solutions"]})
    raw_wb = sorted({w_b for (_, w_b) in mitm6["raw_solutions"]})

    return {
        "seed": seed,
        "primitive": primitive,
        "object": "null (F replaced by the additive non-multiplexer mixer "
                  "_f_null, same step shape)",
        "rc4": rc4,
        "direction_A_rows": rows_a,
        "direction_A_PO3_byte_identical": po3_identical,
        "direction_B_rows": rows_b,
        "ctl_po5_k1_k2_6": {
            "raw_candidate_count": mitm6["raw_solution_count"],
            "distinct_wA_in_raw_set": len(raw_wa),
            "distinct_wB_in_raw_set": len(raw_wb),
            "window_size": 1 << k_ctl,
            "expected_raw_count_modeled": 1 + (1 << (k_ctl + k_ctl)) / 2 ** 20,
        },
    }


# ---------------------------------------------------------------------------
# Pre-registered predictions (term b) -- computed from the RC-4 check,
# declared in the manifest BEFORE the sweep numbers are read.
# ---------------------------------------------------------------------------

def predicted_distinct(rc4: dict) -> dict:
    r = rc4["surviving_bit_count"]
    bound = min(1 << FREE_BITS, 1 << r)
    return {"predicted_distinct_32bit": bound,
            "predicted_distinct_12bit": bound,
            "basis": "2^(surviving low-bit count), capped at the window "
                     "size 2^4=16 (RC-4 mask analysis; MODELED from the "
                     "static check, not a fresh random draw)"}


def adjudicate(observed: int, predicted: int) -> dict:
    dep = abs(observed - predicted)
    return {"observed": observed, "predicted": predicted,
            "departure": dep,
            "beyond_declared_tolerance": dep > TOLERANCE,
            "tolerance": TOLERANCE}


# ---------------------------------------------------------------------------
# Run driver.
# ---------------------------------------------------------------------------

def _code_fingerprint(primitive: str, func_name: str) -> dict:
    base = code_path_fingerprint(_params(primitive, FREE_BITS, FREE_BITS))
    base["sweep_observables"] = {
        "chunk1": f"{__name__}._chunk1_f (func={func_name})",
        "chunk2": f"{__name__}._chunk2_f (func={func_name})",
        "mitm": f"{__name__}._mitm_search_f (func={func_name})"
        if func_name != "_f" else
        "harness.run_md4_ceiling_v2.mitm_search (reused verbatim)",
    }
    base["caveat_refs"] = CAVEAT_REFS
    return base


def environment_json() -> dict:
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "dependencies": {"stdlib_only": True},
    }


def sweep_run(primitive: str, seeds: list, object_kind: str,
              deadline_s: float = 120.0) -> dict:
    """One run: the full seed sweep for one primitive and one object.

    object_kind: "primary" (F = the primitive's Round-1 F, reused verbatim)
    or "null" (F = _f_null, the RC-5 null object).
    """
    t0 = time.monotonic()
    func = _f if object_kind == "primary" else _f_null
    func_name = "_f (primitive Round-1 F, verbatim)" if object_kind == \
        "primary" else "_f_null (additive non-multiplexer mixer)"
    fp = _code_fingerprint(primitive,
                           "_f" if object_kind == "primary" else "_f_null")
    fp["sweep_observables"]["func"] = func_name

    per_seed = []
    for seed in seeds:
        rec = (measure_seed if object_kind == "primary" else measure_seed_null)
        per_seed.append(rec(primitive, seed, t0, deadline_s))

    wall = time.monotonic() - t0
    return {
        "primitive": primitive,
        "object": object_kind,
        "seed_schedule": seeds,
        "seed_count": len(seeds),
        "construction": {**BASE_PARAMS, "k_gate": FREE_BITS,
                         "k_ctl_po5": 6},
        "declared_eps": EPS,
        "injectivity_threshold": INJ_THRESHOLD,
        "declared_tolerance": TOLERANCE,
        "heuristics": {"HEUR-H3": HEUR_H3},
        "code_path_fingerprint": fp,
        "armed_deadline_seconds": deadline_s,
        "wall_seconds": round(wall, 6),
        "halted_at_deadline": wall > deadline_s,
        "per_seed": per_seed,
        "summary": _summarize(per_seed),
    }


def _summarize(per_seed: list) -> dict:
    def dist(key_path):
        vals = []
        for rec in per_seed:
            if key_path == "fwd32":
                vals.append(rec["direction_A_rows"][0]["distinct_fwd_32bit"])
            elif key_path == "fwd12":
                vals.append(rec["direction_A_rows"][0]["distinct_fwd_12bit"])
            elif key_path == "bwd32_max":
                vals.append(max(r["distinct_bwd_32bit"]
                                for r in rec["direction_B_rows"]))
            elif key_path == "bwd32_min":
                vals.append(min(r["distinct_bwd_32bit"]
                                for r in rec["direction_B_rows"]))
            elif key_path == "bwd12_max":
                vals.append(max(r["distinct_bwd_12bit"]
                                for r in rec["direction_B_rows"]))
            elif key_path == "po5":
                vals.append(rec["ctl_po5_k1_k2_6"]["raw_candidate_count"])
        s = sorted(vals)
        n = len(s)
        hist = {}
        for v in s:
            hist[v] = hist.get(v, 0) + 1
        return {
            "min": s[0], "max": s[-1], "median": s[n // 2],
            "histogram": {str(k): v for k, v in sorted(hist.items())},
            "fraction_at_or_above_injectivity_threshold":
                sum(1 for v in s if v >= INJ_THRESHOLD) / n,
        }
    po5 = dist("po5")
    return {
        "distinct_fwd_32bit": dist("fwd32"),
        "distinct_fwd_12bit": dist("fwd12"),
        "distinct_bwd_32bit_max_over_held_fixed": dist("bwd32_max"),
        "distinct_bwd_32bit_min_over_held_fixed": dist("bwd32_min"),
        "distinct_bwd_12bit_max_over_held_fixed": dist("bwd12_max"),
        "ctl_po5_raw_candidate_count": po5,
        "ctl_po5_fraction_at_or_above_ceiling_4":
            sum(1 for rec in per_seed
                if rec["ctl_po5_k1_k2_6"]["raw_candidate_count"] >= 4)
            / len(per_seed),
        "po3_byte_identical_all_seeds": all(
            rec["direction_A_PO3_byte_identical"] for rec in per_seed),
        "rc4_surviving_bit_count_histogram": _hist(
            rec["rc4"]["surviving_bit_count"] for rec in per_seed),
        "rc4_modeled_vs_measured_adjudication_count": sum(
            len(rec["rc4"]["modeled_vs_measured_adjudications"])
            for rec in per_seed),
        "adjudications": _all_adjudications(per_seed),
    }


def _hist(gen) -> dict:
    h = {}
    for v in gen:
        h[v] = h.get(v, 0) + 1
    return {str(k): v for k, v in sorted(h.items())}


def _all_adjudications(per_seed: list) -> list:
    out = []
    for rec in per_seed:
        pred = predicted_distinct(rec["rc4"])
        for res, row in (("fwd", rec["direction_A_rows"][0]),):
            for bit in ("32bit", "12bit"):
                a = adjudicate(row[f"distinct_fwd_{bit}"],
                               pred[f"predicted_distinct_{bit}"])
                if a["beyond_declared_tolerance"]:
                    out.append({"seed": rec["seed"], "quantity":
                                f"distinct_{res}_{bit}", **a})
        for i, row in enumerate(rec["direction_B_rows"]):
            a = adjudicate(row["distinct_bwd_32bit"],
                           pred["predicted_distinct_32bit"])
            if a["beyond_declared_tolerance"]:
                out.append({"seed": rec["seed"],
                            "quantity": f"distinct_bwd_32bit_held_{i}",
                            **a})
        po5 = rec["ctl_po5_k1_k2_6"]
        a = adjudicate(po5["raw_candidate_count"],
                       int(round(po5["expected_raw_count_modeled"])))
        if a["beyond_declared_tolerance"]:
            out.append({"seed": rec["seed"],
                        "quantity": "ctl_po5_raw_candidate_count", **a,
                        "note": ("expected_raw_count_modeled is a Poisson-"
                                 "type MODELED value (1 + 4096/2^20); the "
                                 "batch-5 declared ceiling is 4. Departures "
                                 "beyond the tolerance are recorded; the "
                                 "ceiling is a stopping value, not a "
                                 "prediction.")})
    return out


def _main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--primitive", choices=["md4", "md5"], required=True)
    ap.add_argument("--object", choices=["primary", "null"],
                    required=True)
    ap.add_argument("--seeds", type=int, nargs="+", default=None,
                    help="default: the declared 100-seed schedule")
    ap.add_argument("--deadline", type=float, default=120.0)
    ap.add_argument("--out-root", required=True)
    ap.add_argument("--run-suffix", required=True)
    ap.add_argument("--command", default=sys.argv[0])
    args = ap.parse_args(argv)

    seeds = args.seeds if args.seeds is not None else SEEDS
    run_id = f"RUN-MDFIVE-b6-{args.object}-{args.primitive}-{args.run_suffix}"
    out_dir = os.path.join(args.out_root, "runs", run_id)
    os.makedirs(out_dir, exist_ok=True)

    t0 = time.monotonic()
    try:
        result = sweep_run(args.primitive, seeds, args.object,
                           args.deadline)
        status = "completed_valid"
        stderr_tail = ""
    except TimeoutError as e:
        status = "halted_at_deadline"
        result = {"halted": str(e)}
        stderr_tail = str(e)

    wall = time.monotonic() - t0
    run = {
        "run": {
            "id": run_id,
            "experiment_id": "EXP-MDFIVE-b6-phase1",
            "task_id": "TASK-20260822-767bb1",
            "status": status,
            "started_wall_seconds_ago_of_manifest": round(wall, 6),
            "inputs": {
                "parameters": {
                    "primitive": args.primitive,
                    "object": args.object,
                    "construction": {**BASE_PARAMS, "k_gate": FREE_BITS,
                                      "k_ctl_po5": 6},
                    "seed_schedule": seeds,
                    "declared_eps": EPS,
                    "injectivity_threshold": INJ_THRESHOLD,
                    "declared_tolerance": TOLERANCE,
                    "armed_deadline_seconds": args.deadline,
                    "caveat_refs": CAVEAT_REFS,
                },
                "code_path_fingerprint": _code_fingerprint(
                    args.primitive,
                    "_f" if args.object == "primary" else "_f_null"),
                "random_seeds": {"fixed_word_seeds": seeds,
                                 "target_seed_rule": "target_seed := "
                                 "fixed-word seed (declared pairing)"},
            },
            "cost_model": {
                "declared_ceiling_seconds": args.deadline,
                "measured_wall_seconds": round(wall, 6),
                "caveat_refs": CAVEAT_REFS,
            },
        },
    }

    with open(os.path.join(out_dir, "command.txt"), "w") as f:
        f.write(" ".join(args.command.split()) + "\n")
    with open(os.path.join(out_dir, "environment.json"), "w") as f:
        json.dump(environment_json(), f, indent=2)
    import yaml as _yaml
    with open(os.path.join(out_dir, "manifest.yaml"), "w") as f:
        _yaml.safe_dump(run, f, sort_keys=False, width=10000)
    with open(os.path.join(out_dir, "raw-result.json"), "w") as f:
        json.dump(result, f, indent=1)
    with open(os.path.join(out_dir, "stdout.log"), "w") as f:
        f.write(json.dumps(result.get("summary", {}), indent=1,
                           default=str) + "\n")
    with open(os.path.join(out_dir, "stderr.log"), "w") as f:
        f.write(stderr_tail + "\n")
    print(json.dumps({"run": run_id, "status": status,
                      "wall_seconds": round(wall, 6),
                      "summary": result.get("summary", {})},
                     indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
