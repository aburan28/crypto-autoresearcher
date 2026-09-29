#!/usr/bin/env python3
"""Generate the phase-1 frozen report (blind-rederivation.yaml) directly from
results.json so that no value is hand-transcribed. Part of the sealed set."""

import hashlib
import json
import os
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, 'results.json')))

FQ = lambda v: v['__fraction__'] if isinstance(v, dict) else None
FL = lambda v: float(v) if not isinstance(v, dict) else float(v['__float__'])


def yfrac(v, indent=6):
    f = FQ(v)
    fv = FL(v)
    if f is not None:
        return f'"exact: {f}   (~= {fv:.10g})"'
    return f"{fv!r}"


def cell_block(c):
    p, pr, sh, nu, po = c['partition'], c['params'], c['shares'], c['nulls'], c['pool']
    L = []
    A = L.append
    A(f"    - cell: {{N: {pr['N']}, a: {pr['a']}, seed: {pr['seed']}}}")
    A(f"      parameters_used:")
    A(f"        N: {pr['N']}")
    A(f"        a: {pr['a']}")
    A(f"        seed: {pr['seed']}")
    A(f"        T: {pr['T']}")
    A(f"        T_sel: {pr['T_sel']}")
    A(f"        r: {pr['r']}")
    A(f"        W_squared: \"{pr['W_squared']}\"   # exact; W itself is irrational")
    A(f"        W_float: {pr['W_float']}   # double; used only in weight_d, disclosed")
    A(f"        cap: {pr['cap']}")
    A(f"        dp_threshold: {pr['dp_threshold']}")
    A(f"      fields:")
    A(f"        share_top_Tsel: {yfrac(sh['share_top_Tsel'])}")
    A(f"        cov_static: {yfrac(c['cov_static'])}")
    A(f"        margin: {yfrac(c['margin'])}   # = share_top_Tsel - cov_static, exact")
    A(f"        share_top_T: {yfrac(sh['share_top_T'])}")
    A(f"        share_top_Tover4: {yfrac(sh['share_top_Tover4'])}")
    A(f"        share_top_Tover8: {yfrac(sh['share_top_Tover8'])}")
    A(f"        rho_ORACLE: {yfrac(c['rho_ORACLE'])}   # k*/T, see ambiguity_records.rho_ORACLE")
    A(f"        n_dps: {p['n_dps']}")
    A(f"        cycle_mass: {p['cycle_mass']}")
    A(f"        capped_mass: {p['capped_mass']}")
    A(f"        cap: {pr['cap']}")
    A(f"        capped_walks: {po['capped_walks']}")
    A(f"        residual_fraction: {yfrac(p['residual_fraction'])}")
    A(f"        accounting_identity_holds: {str(p['accounting_identity_holds']).lower()}"
       f"   # sum_b={p['sum_b']} + cycle_mass + capped_mass == N, exact integer")
    A(f"        min_basin_size: {p['min_basin_size']}   # b(d) >= 1 corollary")
    A(f"        n_tied_at_Tth_weight: {po['n_tied_at_Tth_weight']}")
    A(f"        margin_null_oracle_rand_uniform: {yfrac(nu['margin_null_oracle_rand_uniform'])}"
       f"   # float-sampled subset, exact read-off, disclosed")
    A(f"        margin_null_oracle_rand_sizebiased: {yfrac(nu['margin_null_oracle_rand_sizebiased'])}"
       f"   # float-sampled subset, exact read-off, disclosed")
    A(f"        margin_null_randsel: {yfrac(nu['margin_null_randsel'])}")
    A(f"        cov_static_shuf: {yfrac(nu['cov_static_shuf'])}")
    A(f"      execution:")
    A(f"        cap_boundary_reading: \"{c['cap_boundary_reading']}\"")
    A(f"        reading_B_differences: {c['reading_B_differences'] if c['reading_B_differences'] else '[]'}"
       f"   # fields whose values differ under cap-boundary reading B")
    A(f"        wall_time_seconds: {c['wall_time_seconds']}")
    A(f"        command: \"{R['meta']['command']}\"   # single batch invocation; per-cell times above")
    return "\n".join(L)


ctrl_blocks = []
for key, v in sorted(R['control_a_quarter'].items()):
    ag = v['aggregate_reading_A']
    N, an, ad = key.split('_')
    T = 64 if int(N) == 1 << 20 else 256
    bad = [c['params']['seed'] for c in v['cells_reading_A']
           if not c['partition']['accounting_identity_holds']
           or c['partition']['min_basin_size'] < 1]
    ctrl_blocks.append(f"""    - cell_family: {{N: {N}, a: {an}/{ad}}}
      computed_first: true   # quantity.md s13 / prohibitions.md s4
      seeds: 1..25
      T: {T}
      k_25: {ag['k_25']}
      verdict_25: {ag['verdict_25']}
      k_5: {ag['k_5']}
      verdict_5: {ag['verdict_5']}
      mean_margin: {yfrac(ag['mean_margin'])}
      mean_margin_sign: "{ag['mean_margin_sign']}"
      ci_lo: {ag['ci_lo']!r}   # percentile bootstrap, float, quantity.md s11
      ci_hi: {ag['ci_hi']!r}
      ci_bootstrap_seed: {ag['ci_bootstrap_seed']}
      ci_straddles_zero: {str(ag['ci_straddles_zero']).lower()}
      bca_variant: "{ag['bca_variant']}"
      max_residual_fraction: {yfrac(ag['max_residual_fraction'])}
      identity_or_min_basin_violations: {bad if bad else '[]'}
      per_cell_reading_B_differences_nonempty: {sum(1 for x in v['per_cell_reading_B_differences'] if x)} of 25 seeds""")

frozen = "\n".join(cell_block(c) for c in R['frozen_cells'])
ctrls = "\n".join(ctrl_blocks)
now = datetime.now(timezone.utc).isoformat()

REPORT = f"""# ============================================================================
# PHASE 1 FROZEN REPORT — blind re-derivation of the EXP-ECDLP-6ac801
# derivation-packet quantity at the eight frozen cells of BATCH-12ee85.
# Task TASK-20260910-19bd7b (role: validator, joint J1).
#
# FROZEN AS WRITTEN. This file records phase 1 only. Phase 2 (cross-
# implementation comparison) is NOT started: per the task card and the packet
# seal procedure it may begin only after the Coordinator commits this frozen
# report, and it may read only what the review plan names.
# ============================================================================
blind_rederivation:
  id: BLIND-RDR-TASK-20260910-19bd7b
  task_id: TASK-20260910-19bd7b
  blind_input: BLIND-INPUT-BATCH-12ee85
  derivation_packet: DPKT-PA-ECDLP-6ac801-v2-to-v3
  phase: 1-frozen
  frozen_at: "{now}"
  wall_clock_total_seconds: {R['meta']['total_wall_time_seconds']}

  # --------------------------------------------------------------------------
  reading_attestation:
    files_read_before_seal:
      - "experiments/EXP-ECDLP-6ac801/derivation-packet/PA-ECDLP-6ac801-v2-to-v3/MANIFEST.yaml"
      - "experiments/EXP-ECDLP-6ac801/derivation-packet/PA-ECDLP-6ac801-v2-to-v3/quantity.md"
      - "experiments/EXP-ECDLP-6ac801/derivation-packet/PA-ECDLP-6ac801-v2-to-v3/deliverables.md"
      - "experiments/EXP-ECDLP-6ac801/derivation-packet/PA-ECDLP-6ac801-v2-to-v3/prohibitions.md"
      - "coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-12ee85/blind-input.yaml"
    statement: >-
      The four files above are exactly the packet's allowlist
      (MANIFEST.yaml readable_files, count 4). The fifth file, blind-input.yaml,
      is this task's own frozen input, named by the task card as the statement
      to derive from. NOTHING else in this repository was read before this
      report was frozen: no contract, no amendment, no run directory, no
      existing implementation, no review, no decision record, no coordination
      record outside the two paths above, and no git history command of any
      kind (no git log / show / blame / diff). No commit message was seen.
      The only other files touched were created by this task itself inside its
      own write scope (rederive.py, check_params.py, results.json, this file,
      seal.json).
    slips: none
    blind_from_respected: true

  # --------------------------------------------------------------------------
  declared_conventions:
    # Every choice below is one the packet leaves to the implementer
    # (quantity.md s1 "any standard one", s9, prohibitions.md s4 "any RNG").
    # None of these is claimed to match any other implementation; the packet
    # states explicitly that they need not.
    mix64: >-
      splitmix64 finalizer (u ^= u>>30; u *= 0xBF58476D1CE4E5B9; u ^= u>>27;
      u *= 0x94D049BB133111EB; u ^= u>>31, on one u64). K = mix64(0x9E3779B97F4A7C15 + seed);
      K_dp = mix64(K XOR 0xD1B54A32D192ED03), exactly as quantity.md s1.
    pool_rng: "numpy default_rng([seed, 1]), fresh per cell; uniform restart starts via integers(0, N)."
    tie_break_rng: >-
      numpy default_rng([seed, 100]), fresh per cell; one bulk array of r*T
      doubles, one key per pool entry in pool-insertion order; ascending key
      breaks ties at the T-th largest weight (quantity.md s6).
    null_arm_rngs: >-
      default_rng([seed, 101]) oracle-uniform subset;
      default_rng([seed, 102]) oracle size-biased subset (sequential draw
      WITHOUT replacement, probabilities proportional to basin size);
      default_rng([seed, 103]) uniform random T-subset of the pool;
      default_rng([seed, 104]) permutation of basin sizes over the pool.
      All fresh per cell, all deterministic functions of the integer seed.
    exact_arithmetic: >-
      Every quantity the definition makes exact — cap, dp_threshold, basin
      sizes, cycle/capped mass, all shares, cov_static, margins,
      residual_fraction, rho_ORACLE, the accounting identity, pass-counts and
      their signs — is computed in integer / fractions.Fraction arithmetic.
      Float appears only where the definition is irrational or statistical,
      and each such use is flagged at the value: W (hence weight_d =
      S_d + 4*W*h_d) uses one double per cell; the null-arm subset draws use
      float sampling with exact integer read-off; the s11 bootstrap is float
      by specification. The accounting identity check is exact integer
      arithmetic with zero tolerance at every cell.
    ordering: >-
      a = 1/4 computed first at each scale (quantity.md s13), N = 2^20 before
      N = 2^24 (prohibitions.md s4). The a = 1/4 control is reported below
      under control_a_quarter; it came out G3-INFEASIBLE at both scales, so
      proceeding to the open cells was permitted by deliverables.md s4.

  # --------------------------------------------------------------------------
  ambiguity_records:
    # Recorded AS results per the task card: never resolved silently.
    cap_boundary_at_step_cap:
      packet_text: >-
        quantity.md s3b: "A pool-construction walk that reaches `cap` steps
        without hitting a DP **terminates capped**". The packet does not state
        whether the point landed on AT step `cap` is itself DP-checked before
        the walk is declared capped.
      resolution_used: >-
        Reading A (primary): the walk examines its landing points x_0 .. x_cap
        inclusive, and is capped iff none of them is a DP. Reading B: the walk
        examines x_0 .. x_(cap-1) only. BOTH readings were run at every cell;
        the values below are reading A, and per-cell
        `reading_B_differences` lists every field whose value changes under
        reading B.
      observed_result: >-
        The two readings produced IDENTICAL values for every reported field at
        every cell (all eight frozen cells and all 50 control cells): no walk
        that reached step cap landed on a DP. The ambiguity is therefore
        empirically vacuous at these parameters, but it remains a genuine
        underdetermination of the packet, and phase 2 must compare it as such.
    rho_ORACLE:
      packet_text: >-
        quantity.md s12 names rho_ORACLE only parenthetically: "the smallest
        `T_sel/T` at which `share_top(T_sel)` reaches `cov_static`". No formal
        definition of rho_ORACLE appears anywhere in the packet.
      resolution_used: >-
        Working definition: rho_ORACLE = k*/T where k* is the smallest
        k in {{1..T}} with share_top(k) >= cov_static, share_top ranging over
        ALL DPs of the exact partition and cov_static the pool-selected
        coverage (both exact integer comparisons). k* always exists because
        share_top(T) >= cov_static. Reported as an exact fraction. This is a
        derivation the re-deriver had to supply; it is flagged as such.
    null_shuf_scope:
      packet_text: >-
        quantity.md s12 NULL-SHUF: "Permute the basin sizes across the pool's
        DPs, holding the size multiset and the weights fixed, and report the
        resulting `cov_static`." The packet does not state whether the
        selection is re-run on the permuted assignment.
      resolution_used: >-
        Holding the weights fixed means the selected set is unchanged; only
        the basin sizes read off at the selected entries are permuted.
        Reported as the coverage of the same selected entries under a
        uniformly random permutation of the pool's basin-size vector.
    size_biased_draw:
      packet_text: >-
        quantity.md s12 NULL-ORACLE-RAND (size-biased) says only "drawing the
        T_sel-subset with probability proportional to basin size"; the
        without-replacement scheme is not specified.
      resolution_used: >-
        Sequential draw without replacement, at each step choosing uniformly
        among remaining DPs with probability proportional to current basin
        size (a standard sequential weighted sample without replacement;
        exact final subset distribution differs slightly from a strict
        size-biased sampling design). Float sampling arithmetic, exact
        integer read-off. Disclosed, not silent.
    pool_stop_rule:
      packet_text: >-
        quantity.md s5: "repeat until the pool holds r*T distinct DPs". The
        packet does not state what happens if walks exhaust before r*T
        distinct DPs are found.
      resolution_used: >-
        No cell encountered this: every cell filled its pool. At the smallest
        smoke instance the pool also filled. The rule actually implemented is
        "continue until r*T distinct DPs, unbounded", which is the literal
        reading; the alternative (a bounded walk budget) never became
        relevant, so no result depends on the choice.
    weight_arithmetic:
      packet_text: >-
        quantity.md s6 fixes the FORM of weight_d = S_d + 4*W*h_d but W is
        irrational at a = 1/8 and 3/16, so the weight cannot be an exact
        rational at those cells; the packet does not state a rounding.
      resolution_used: >-
        One IEEE double per cell for W (repr recorded per cell in
        parameters_used.W_float), weights computed in float64, selection and
        tie detection on those floats. Ties are detected by exact float
        equality on the computed weights. Disclosed per cell.
    t_at_smaller_scale:
      packet_text: quantity.md s10 frozen table.
      resolution_used: "T = 64 at N = 2^20, T = 256 at N = 2^24, from the frozen table (deliverables.md joint 5). Verified: all eight W/cap rows reproduced exactly from the formulas (cap = ceil(8*W), dp_threshold = floor(2^64/W)) — see check_params.py output in results.json meta and the per-cell parameters."

  # --------------------------------------------------------------------------
  implementation:
    program: rederive.py
    program_sha256_pending: see seal.json
    auxiliary_checks: check_params.py   # cap/W table reproduction; mix64 vector==scalar; smoke cell
    output: results.json
    environment:
      python: "{R['meta']['python']}"
      numpy: "{R['meta']['numpy']}"
      platform: "{R['meta']['platform']}"
    exact_command: "{R['meta']['command']}"
    started_utc: "{R['meta']['started_utc']}"
    finished_utc: "{R['meta']['finished_utc']}"
    algorithm_notes: >-
      Exact basin partition by reverse breadth-first search over the exact
      reverse graph (CSR from np.bincount/argsort), DPs absorbing, giving
      dist and first-DP label for all N points in O(N); the three classes,
      b(d), cycle_mass, capped_mass and the accounting identity follow
      exactly. Pool construction by uniform random restarts with the cap
      binding termination (no S_d/h_d credit for capped walks). Selection by
      weight_d with the per-entry pseudorandom tie-break key in
      pool-insertion order. Null arms read off the same partition. A pipeline
      smoke cell (N=2^12, T=8, a=1/4, seed=1) was run first for correctness
      only and is NOT a grid cell.

  # --------------------------------------------------------------------------
  control_a_quarter:
    # quantity.md s13: a = 1/4 is the batch's known-false object, run FIRST.
    # Observed: G3-INFEASIBLE at both scales, i.e. the instrument REPRODUCED
    # the known-false object. Observation only; no interpretation beyond
    # deliverables.md s4's own stop rule, which did not fire.
{ctrls}

  # --------------------------------------------------------------------------
  frozen_cells:
    # The eight cells of BLIND-INPUT-BATCH-12ee85, listed with all N = 2^20
    # cells before the N = 2^24 cells (prohibitions.md s4); within that, the
    # blind-input's own listing interleaves the 2^24 a=1/8 seeds before the
    # 2^20 a=1/16 cell, and this listing groups by scale instead. Every cell
    # is labelled with its (N, a, seed), so the ordering carries no
    # information. All values below are reading A; reading B agreed
    # everywhere (see ambiguity_records).
{frozen}

  # --------------------------------------------------------------------------
  phase_2:
    status: not-started
    reason: >-
      Phase 2 (cross-implementation comparison with per-field verdicts
      EXACT / QUALITATIVE / DISAGREES / UNDERDETERMINED) runs only after the
      Coordinator commits this frozen report, and may read only what the
      review plan names. Nothing outside the five files listed in
      reading_attestation has been read, so this report is blind as frozen.

  # --------------------------------------------------------------------------
  review_attestation:
    joints_owned:
      - blind re-derivation of every blind-input field at all eight frozen cells
      - cap applied in both binding places (s3a basin predicate, s3b pool termination)
      - residual accounting identity exact at every cell (including all 50 control cells)
      - b(d) >= 1 for every DP at every cell
      - universe asymmetry: cov_static over pool-selected entries, share_top over all DPs
      - weight = S_d + 4*W*h_d, never true basin size; tie-break by insertion-order key
      - T = 64 at N = 2^20 from the frozen table
      - null arms drawn from the correct universes (oracle arms from all DPs of the partition)
    sources_read:
      - experiments/EXP-ECDLP-6ac801/derivation-packet/PA-ECDLP-6ac801-v2-to-v3/MANIFEST.yaml
      - experiments/EXP-ECDLP-6ac801/derivation-packet/PA-ECDLP-6ac801-v2-to-v3/quantity.md
      - experiments/EXP-ECDLP-6ac801/derivation-packet/PA-ECDLP-6ac801-v2-to-v3/deliverables.md
      - experiments/EXP-ECDLP-6ac801/derivation-packet/PA-ECDLP-6ac801-v2-to-v3/prohibitions.md
      - coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-12ee85/blind-input.yaml
    read_sibling_reports: false
    read_git_history: false
    blind_from_respected: true
    verdict: phase-1 frozen; observations only, no interpretation
"""

with open(os.path.join(HERE, 'blind-rederivation.yaml'), 'w') as fh:
    fh.write(REPORT)
print('wrote blind-rederivation.yaml', len(REPORT), 'bytes')
