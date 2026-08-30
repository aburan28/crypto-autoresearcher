# Implementation note: EXP-MONO-2a13d7 (Stage 0 + Stage 1 + Stage 3)

Handoff: `ledger/handoffs/TASK-20260830-5b8033.yaml`. Contract:
`experiments/EXP-MONO-2a13d7/specification.yaml` (frozen, `approved_by:
coordinator`, `2026-08-30`). This note is implementation-and-observation
only; it renders no verdict on `H-MONO-0f9170`.

## Layout

All code lives under `experiments/EXP-MONO-2a13d7/implementation/`, pure
Python 3 standard library (`grep -n "^import\|^from"` across every file
shows only `json, os, sys, time, platform, resource, subprocess, csv,
hashlib, math, __future__` -- no `sympy`, `sage`, `numpy`, `g6k`, or
`fpylll`, confirmed and recorded in `environment.json` of each run).

- `fp_common.py` -- Legendre symbol, modular inverse, and Tonelli-Shanks
  square root. **No F_{p^2}/F_{p^4} arithmetic anywhere in this
  experiment's code** -- unlike the sibling `EXP-MONO-4c7479`, this
  contract's inert-case classification is decided by a single F_p
  Legendre symbol of `c0`, computed directly from `(e1,e2)`.
- **Modular square root**: GENERAL TONELLI-SHANKS, used UNCONDITIONALLY
  for both tested primes. p=101 = 1 mod 4 (the p=3-mod-4 shortcut is
  unavailable there), so the general routine is required; per the
  contract's own consistency requirement ("use the SAME one for both
  tested primes"), the p%4==3 fast-path branch was deliberately NOT
  implemented at all, so p=211 also runs the full general algorithm
  rather than the shortcut it could otherwise use.
- `stage0.py` -- the O(p) character-sum curve-invariant sweep
  (`curve_invariants`), full enumeration (`enumerate_curves`), (t,Z)
  grouping, the O(1)-per-pair isomorphism test (`isomorphic`), the
  streaming matched-pair census (`matched_pair_census`), and the seven
  closed-form counts (`closed_form_seven_tuple`).
- `stage1.py` -- exhaustive per-base-point classification
  (`classify_panel_curve`): split case via Tonelli-Shanks + two Legendre
  symbols of `f(t1),f(t2)`; inert case via one Legendre symbol of `c0`
  computed directly from `(e1,e2,A,B)` per the spec's polynomial, with
  **no lift to F_{p^2}** anywhere.
- `run_experiment.py` -- the driver: per-prime Stage 0 (enumeration,
  matched-pair census/selection, panel construction), per-curve
  pre-registration + Stage 1 census (Stage 3's controls computed from the
  same Stage-1 output), and all required artifacts.

## Confirmation: the REQUIRED O(p) point-counting method was used, not O(p^2)

`stage0.curve_invariants` performs exactly ONE pass `for x in range(p)`
per curve, computing `f(x)`, its Legendre symbol (folded into the trace
sum and the `Z` count), and `psi_3(x)` (folded into the SAME loop for the
order-3 root search) -- never a second pass, never a loop over
`(x,y)` pairs. Measured wall-clock evidence, from `RUN-MONO-2a13d7-1`
(`runs/RUN-MONO-2a13d7-1/p*/timings.json` and `raw-result.json`):

| prime | curves enumerated | `stage0_enumeration_seconds` (measured) |
|---|---|---|
| p=101 | 10,100 (of 10,201 (A,B) pairs; exactly 101 = p singular) | 0.337 s |
| p=211 | 44,310 (of 44,521 (A,B) pairs; exactly 211 = p singular) | 3.229 s |

Both are far below the spec's own conservative O(p) estimate ("30-50
seconds" for p=211) and consistent with O(p) per curve -- an O(p^2)
method (testing all p^2 (x,y) pairs per curve for group order) at
p=211 would cost roughly `p^2` times more per curve (i.e. hours, not
seconds) and was not used anywhere in this implementation (confirmed by
code inspection: `curve_invariants`'s only loop over the field is the
single `for x in range(p)`).

## Confirmation: pre-registration-before-enumeration ordering

`run_experiment.preregister_and_run_stage1` computes and appends the
pre-registered closed-form entry (`prereg_records.append(...)`, with a
`preregistered_at` timestamp and an explicit `ordering_marker:
"PRE_ENUMERATION"`) for a panel curve, THEN calls
`classify_panel_curve` for that SAME curve, per-curve in a single loop
iteration -- never batched across curves and never reordered. Each
`p*/preregistration.json` file's entries all carry
`ordering_marker: "PRE_ENUMERATION"` and a timestamp; `p*/timings.json`'s
`stage1_per_curve_seconds` confirms Stage-1 census work happened after
pre-registration was already appended to the in-memory list (the write to
disk happens once, in `write_artifacts`, after the whole prime's Stage 0
+ Stage 1 loop completes, but the archived JSON is exactly and only the
in-memory record built by the pre-register-then-classify sequence — no
Stage-1 number is ever fed back into `preregister_and_run_stage1`'s
closed-form computation, which reads only `(p, t, Z)` from the Stage-0
table).

## Confirmation: excluded-strata accounting

The double-root stratum, `A4_ramified_A`, and `B2_ramified_B` are three
separate keys in `stage1.classify_panel_curve`'s `tallies` dict, are
reported in their own fields in `seven_count_tables.json`, and enter the
internal sum checks (`r3.case_A_sum`, `r3.case_B_sum`) exactly once each,
never pooled with each other or with the five primary classes
(`A1_identity, A2_sigma_i, A3_sigma1sigma2, B1_block_swap,
B3_four_cycle`) anywhere in the code (`grep -n "A4_ramified_A\|B2_ramified_B"
stage1.py run_experiment.py` shows each name used consistently as its
own dict key throughout).

## A protocol deviation caught and fixed before the archived runs: matched-pair-census memory

A first implementation of `matched_pair_census` materialized every
non-isomorphic pair found (as a Python list of 6-tuples) across the
entire exhaustive per-cell pairwise test. At p=211 this produced
**14,733,075** non-isomorphic pairs in memory simultaneously, driving
measured peak RSS to **~3092 MB** in a throwaway pre-run smoke test --
a clear breach of the frozen 1 GB `maximum_memory_gb` budget. This was
caught in an interactive smoke test BEFORE either of the two archived
runs (`RUN-MONO-2a13d7-1`, `RUN-MONO-2a13d7-2`) was executed; neither
archived run ever used the memory-unsafe version of the code. The fix
(now the only version of `stage0.matched_pair_census` in this
experiment's tree) tracks two running minima (the lexicographically
smallest qualifying candidate overall, and the smallest touching a
preferred sibling/Z-coverage curve) in a single streaming pass, without
ever materializing the full pair list; the exhaustive-testing REQUIREMENT
of the spec (every pair in every cell IS still tested; `pairs_tested` and
`non_iso_pairs_count` per cell, and `non_iso_pairs_total` per prime, are
exact counts from that exhaustive test) is preserved -- only the
accumulation strategy changed. Measured peak RSS in the archived runs:
**84.8 MB** (`RUN-MONO-2a13d7-1`) and **85.1 MB** (`RUN-MONO-2a13d7-2`),
both far inside the 1 GB budget. This is recorded here per the Executor's
obligation to record every deviation and infrastructure-adjacent event,
not silently absorb it; it is an implementation-defect-caught-and-fixed
event, not a run outcome, and voids nothing (no archived run ever
breached the budget).

## A second correction found and fixed before the archived runs: Z-coverage panel selection

The first working version of Z-coverage curve selection (spec step 5)
searched the FULL table for the lexicographically smallest `(A,B)` with
a given uncovered `Z`, without excluding `A=0` (`j=0`) or `B=0`
(`j=1728`) curves. At p=211 this selected `(A=0,B=1)` (a `j=0` curve) as
the Z=3 coverage curve -- a direct violation of `curve_panel_note`, which
excludes j=0/1728 curves from Stage-1 PANEL SELECTION generally (not only
from the matched-pair role). This was caught by inspecting the panel
selection transcript before the archived runs and fixed by adding the
same `is_special(A,B,p)` (A==0 or B==0) exclusion already used for the
matched-pair candidate filter to the Z-coverage search loop. The archived
panel transcripts (`runs/*/p211/panel_selection_transcript.json`) show
the corrected selection: `(A=1,B=2)`, `j != 0,1728`, for p=211's Z=3
coverage role. Recorded for the same reason as the memory deviation
above: caught pre-archival, never present in an archived run, but worth
recording as an interpretation/implementation correction rather than
silently absorbing it.

## Declared interpretation of the spec's forward-referencing matched-pair preference clause

`stage0_curve_enumeration_and_prereg` step 4 says to select the
lexicographically smallest qualifying matched-pair tuple "preferring (if
any qualify) a cell containing one of the Z-coverage curves selected in
the NEXT step" -- a forward reference from step 4 to step 5. This
implementation resolves the forward reference by computing sibling curves
and Z-coverage curves FIRST (both depend only on the Stage-0 table, not
on the matched-pair search), forming `preferred_ab = sibling_ab |
z_coverage_ab`, and then running the matched-pair census with two
streaming minima: the lexicographically smallest candidate touching
`preferred_ab` (used if one exists) and the lexicographically smallest
candidate overall (used as fallback). This is a declared reading of an
underspecified ordering, not a silent choice: at both tested primes a
preferred candidate existed (the matched pair found at each prime touches
the `(A=1,B=1)` sibling curve), so the fallback branch was never
exercised by either archived run.

## Isomorphism test: verified against brute force, not merely asserted

`stage0.isomorphic` uses an O(1) algebraic shortcut for the generic case
(`A,B,A2,B2` all nonzero): from `A2=u^4 A, B2=u^6 B` it derives the
necessary condition `s^2 = r^3 mod p` (`r=A2/A, s=B2/B`) and, if that
holds, tests whether `w = s/r` (representing `u^2`) is a square mod p --
sufficient because any square root `u0` of `w` automatically satisfies
`u0^4 = w^2 = r` and `u0^6 = u0^4 u0^2 = r w = s`. Edge cases (`A=0` or
`B=0`, i.e. `j=0` or `j=1728`) fall back to a direct O(p) brute-force
search over `u`, since the algebraic shortcut requires `r,s` invertible.
Before use, this was verified EXHAUSTIVELY against a brute-force
reference implementation (`for u in range(1,p): check both equations
directly`) for every ordered pair of non-singular `(A,B),(A2,B2)` at
p=13: **24,336 pairs checked, 0 mismatches.** The order-3 point count and
the character-sum trace were separately cross-checked at p=13 against a
from-scratch naive elliptic-curve group-law implementation (point
doubling/addition, no shortcuts): **132 curves checked for order-3 count
(0 mismatches)**, and the first 50 curves' traces matched a naive
`#E(F_p)` count exactly. None of this verification code is part of the
archived experiment's implementation (it is throwaway scratch code used
only to build confidence before the real runs); it is reported here as
part of the Executor's own diligence, not as a certificate or an
additional required artifact.

## Stage 0 result summary (measured, `RUN-MONO-2a13d7-1`; bit-identical in `RUN-MONO-2a13d7-2` -- see `execution_report.yaml`)

| prime | curves | (t,Z) cells with >=2 curves | non-isomorphic pairs found (exhaustive) | matched pair selected |
|---|---|---|---|---|
| 101 | 10,100 | 51 | 1,112,500 | (A=1,B=1) vs (A=1,B=48), t=-3, Z=0 |
| 211 | 44,310 | 74 | 14,733,075 | (A=1,B=1) vs (A=1,B=94), t=-11, Z=0 |

Both matched pairs pass the non-vacuity control (differ on `j`; equal
`order3_count` in both cases, so the control is satisfied via `j` alone
at both primes) and both agree exactly on all seven stratum counts (R2=0
on all seven, both primes).

## Stage 1/3 result summary (both runs)

- R1 (per-stratum residual against the closed forms): **0 on every
  stratum, every panel curve, both primes** (`r1_all_residuals_zero:
  true` in both runs' `raw-result.json`, and every entry of every
  `p*/seven_count_tables.json`'s `residuals` block is 0).
- R3 (internal sum checks): case-A sums to `C(p,2)`, case-B sums to
  `p(p-1)/2`, double-root count exactly `p` -- **exact on every panel
  curve, both primes** (`r3_all_sum_checks_ok: true`).
- Baseline reproduction (`S^2+N^2-(p-Z)` against KN-FIND-a8990a Theorem
  B, via `2*(A1_measured+A3_measured)`): **exact agreement on all 3
  sibling curves, both primes** (`baseline_reproduction_all_ok: true`;
  see `runs/*/p*/baseline_reproduction.json`).
- R2 (matched-pair seven-tuple equality): **0 difference on all seven
  strata**, at both primes, with the non-vacuity control passing (j
  differs) at both primes.
- Anomalies (order-3 root coinciding with a 2-torsion point,
  `f(x0)=psi_3(x0)=0`): **0 at both primes** (`anomalies.json` empty in
  both runs).

## Replication

Both runs (`RUN-MONO-2a13d7-1`, `RUN-MONO-2a13d7-2`) were executed from
the identical implementation and inputs. Every substantive artifact
(curve-invariant tables, matched-pair census, panel-selection transcript,
pre-registered closed forms modulo their timestamp field, per-base-point
classification logs, seven-count tables, R1/R2/R3 results, baseline
reproduction) is byte-identical between the two runs; only wall-clock
timing fields, peak-RSS measurements, `preregistered_at` timestamps, and
the run-directory path embedded in `command.txt` differ, exactly as
`replication.interpretation` predicts for a fully deterministic,
seed-free contract. This comparison was performed directly (a Python
script diffing every archived file tree, with the expected exceptions
enumerated above) rather than merely asserted.

## Budget

Measured wall-clock: **20.32 s** (`RUN-MONO-2a13d7-1`) and **20.65 s**
(`RUN-MONO-2a13d7-2`) total across both primes -- far inside the
1800-second-per-run cap, consistent with the spec's own cost estimate.
Measured peak RSS: **84.8 MB** and **85.1 MB** respectively -- far inside
the 1 GB cap.

## What this implementation does NOT do (deliberately, per scope)

No p=1009 (Stage 2), no cross-prime decay prediction, no j=0/1728/CM/
full-2-torsion matched-pair search leg, no F_{p^2}/F_{p^4} arithmetic
anywhere, no relation-rate/ECDLP/cost claim of any kind. No hypothesis,
experiment, or goal status was changed by this Executor.
