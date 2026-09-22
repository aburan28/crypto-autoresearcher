# RUN-FROB-91ee9c-ba442e report

**Experiment:** EXP-FROB-91ee9c
**Handoff:** ledger/handoffs/TASK-20260921-ba442e.yaml
**Amendments executed:** DEC-20260921-e81e25 (v2), DEC-20260921-2f89d4 (v3,
corrected C2 pool construction), DEC-20260921-f93b43 (v4, this run's
authorizing amendment)
**Scope:** FULL COMPLETION of cell `FROB-EXT-q13n7` (q=13, n=7), curve index
0 only (A=0, B=1, N=5,230,261) -- independent object-curve search/
verification, the object arm across all achievable partitions, and the full
control battery C1-C7 (C8 is satisfied by this run's own `checker.py`).
Curve index 1 is explicitly OUT OF SCOPE.
**Certificate:** `kind: none`. Pure combinatorial measurement; no discrete
log solved, no key recovered.
**Terminal status: `completed_ok`** (cell_status: `ok`). This was NOT a
`not_run_resource` outcome: the prior probe's 540-second self-imposed
checkpoint was corrected by this amendment's 3-hour advisory budget, and the
full battery completed in 1,266 seconds wall-clock (~21 minutes), well
inside budget.

This report states measured observations only. It does not conclude
anything about H-FROB-d93575's status (FROB-EXT-q13n7 is explicitly
non-load-bearing for that hypothesis's success/falsification criteria per
SR-4) -- that judgment is a separate `/review-evidence` decision.

## 1. Verified object curve

Independent re-derivation via `object_search` (work/core.py), which performs
the FULL `object_selection` eligibility test including the Frobenius scalar
condition, was run from scratch (not merely checked against the prior
probe's candidate) with `want_curves=1` (curve index 1 explicitly out of
scope, so the search was stopped after the first eligible curve was found
and fully verified):

| field | value |
|---|---|
| A | 0 |
| B | 1 |
| N | 5,230,261 (prime) |
| j-invariant | 0 |
| cofactor | 12 |
| #E(F_13^7) | 62,763,132 |
| generator G | x = `11*z^6 + 7*z^5 + 4*z^4 + 11*z^3 + 4*z^2 + 11*z + 9`, y = `9*z^6 + 9*z^5 + 7*z^4 + 11*z^2 + 11*z + 11` |
| ord(G) | 5,230,261 (independently confirmed) |
| mu (Frobenius scalar) | 5,058,495 |
| ord_N(mu) | 7 = n (independently confirmed) |

**This exactly reproduces the prior probe's recorded candidate**
(`curve_search_matches_prior_probe: true`), and additionally performs the
mu-scalar verification (`pi(G) == mu*G` by independent point arithmetic) the
probe explicitly did not attempt ("object-search-only probe"). No
discrepancy was found; no fallback re-scan was needed.

`checker.py` independently re-confirms, via its OWN point arithmetic (not
importing Sage or the driver): the generator lies on the curve, `N*G` is the
point at infinity, `pi(G) == mu*G`, and `mu` has multiplicative order 7 mod
N -- all via cheap O(log N) double-and-add scalar multiplication, not a full
subgroup reenumeration (see Section 8).

## 2. Achievable-partition table and the central finding

`x^7 - 1` over F_13 factors as `(x-1) * f1 * f2 * f3`, each `f_i` degree 2
(`x^2+3x+1`, `x^2+5x+1`, `x^2+6x+1`), confirming the frozen
`expected_factorisation` for this cell exactly. This gives Bell(3) = 5 total
set-partitions of `{f1,f2,f3}`, collapsing to 3 distinct slot-dimension
multisets:

| partition | slot_dims | object-arm status | block sizes |
|---|---|---|---|
| `{f1,f2,f3}` (m=1) | `[6]` | **ok** | 401,100 |
| `{f1},{f2,f3}` (m=2) | `[4,2]` | `empty_base` | `[0, 2058]` |
| `{f1,f2},{f3}` (m=2) | `[4,2]` | `empty_base` | `[2436, 0]` |
| `{f2},{f1,f3}` (m=2) | `[4,2]` | `empty_base` | `[0, 2310]` |
| `{f1},{f2},{f3}` (m=3) | `[2,2,2]` | `empty_base` | `[0, 0, 0]` |

**This is the central measured finding of this run.** For this specific
curve/generator, every individual atomic-factor kernel V_{f_i} (dimension 2)
has **zero** points of the order-N subgroup whose x-coordinate lands purely
in it (`B_j = 0` for each single-factor block `{f1}`, `{f2}`, `{f3}`
individually); the pairwise-merged dimension-4 blocks are each nonempty
(2058, 2436, 2310 respectively) but never appear together with a nonempty
complementary dimension-2 block, so **all four non-coarsest partitions are
`empty_base`** and only the coarsest `[6]` partition (m=1, the full
non-trivial-factor block) reaches `ok`. Consequently:

- `n_ok_partitions = 1` for the object arm; `I = 1/1` and `spread = 1/1` **by
  construction**, not because of a small-but-real variation.
- The achievable slot-dimension table (Section 2 above) still matches the
  divisor lattice `{0, 2, 4, 6}` exactly (`divisor_lattice_dims`), so there
  is no disagreement between the two -- the emptiness is a property of THIS
  curve's subgroup structure, not a factorisation-table error.

This was independently verified: `checker.py`'s own re-derivation of the
object-arm summary (`I=1`, `spread=1`, single `ok` partition at `[6]`)
matches the driver's exactly.

## 3. Consequence for C2's "richest test of the fix"

DEC-20260921-f93b43's rationale anticipated FROB-EXT-q13n7's `[2,2,2]`
partition as "the richest test yet" of the corrected C2 per-slot pool
construction (three mutually distinct dimension-2 subspaces). **That test
could not be exercised on this curve**, because C2's per-dimension pool is
built only for dimensions appearing in an `ok` object-arm partition
(`C2_max_multiplicity_by_dim: {"6": 1}` -- dimensions 2 and 4 never appear,
since the `[4,2]` and `[2,2,2]` object partitions are `empty_base`, not
`ok`). This is not a code shortcut introduced by this run: the same
`ok`-gated construction (verbatim, unchanged from TASK-20260921-819bc0) is
what all three prior runs on this experiment use, and it is mathematically
appropriate for C3/C4 (a "matched cardinality of an empty set" is trivially
empty regardless of construction) -- but for C2, which builds a NEW subspace
independent of the object's own emptiness, this cell's specific curve simply
never presents the multi-slot-of-equal-dimension case the amendment
expected. **This is recorded as an honest negative/structural observation,
not a resource or instrument failure**: `cell_status: ok`, the object arm
and every control computed cleanly and passed every check; the richer
`[2,2,2]` test the amendment hoped for is a fact about this one curve's
subgroup structure that a full, successful run discloses rather than one
that a truncated run merely failed to reach.

Only the `[6]` partition (m=1, a single non-pi-stable dimension-6 subspace,
`basis_indices = [0,1,2,3,4,5]`) was available to exercise C2 at all; its
pool has exactly one entry, trivially pairwise-distinct.
`C2_222_three_subspaces_distinct` is therefore reported as
`{"status": "no_ok_222_partition_found"}` rather than a distinctness
verdict -- there is no `[2,2,2]` `ok` entry to check three subspaces on.

## 4. Object-arm / C2 / C3 / C4 spread and strictly-smaller verdicts

All values exact rationals; `extra=0`.

| arm | `[6]` cost_ratio_neg | spread | strictly smaller than object? |
|---|---|---|---|
| object | 2,497,461,603 / 955 (~2,615,143) | 1/1 | n/a |
| C2 (corrected) | 29,150,999,395 / 11,147 (~2,615,073) | 1/1 | **False** (1/1 is not `<` 1/1) |
| C3 seed 2026091401 | 2,497,461,603 / 955 (identical to object: U_neg matched by construction) | 1/1 | **False** |
| C3 seed 2026091402 | 2,497,461,603 / 955 | 1/1 | **False** |
| C4 (null curve A'=z, B'=z+7, N'=5,703,307) seed 2026091401 | 27,233,421,943 / 9,550 (~2,851,668) | 1/1 | **False** |
| C4 seed 2026091402 | 27,233,421,943 / 9,550 | 1/1 | **False** |

Every arm has exactly one `ok` partition, so every spread is trivially 1/1
and no arm is strictly smaller than the object's (equal is not smaller).
This is a direct, mechanical consequence of Section 2's finding, not an
independent negative result about Frobenius stability: with only one
achievable configuration, no arm can show internal variation to compare.

## 5. C1-C7 pass/fail

| control | result |
|---|---|
| C1 (closed-form baseline) | **PASS**: `closed_form_U_neg = 401100/2`, `closed_form_p_1 = 401100/5230260`, both agree exactly with the enumerator's m=1 output (`agree: true`). |
| C2 (corrected per-slot pool) | Computed for the only dimension the object arm reached (`d=6`, `k=1`); pool pairwise-distinct trivially (`C2_dim2_pool_pairwise_distinct: true` over an empty dim-2 pool, vacuously). See Section 3 for why dims 2/4 were never exercised. |
| C3 (random matched-cardinality) | **PASS** for both declared seeds (2026091401, 2026091402); `U_neg` identical to the object arm's for the one matched partition, confirmed by `checker.py`. |
| C4 (matched null curve) | **PASS**: null curve A'=z, B'=z+7 found (order-count wall time 0.0021s -- see Section 6), N'=5,703,307 within [N/2, 2N], generator found and verified, both seeds computed. |
| C5 (trace identity) | **PASS**: `T_equals_hM: true`; `dim_ker_T = 6 = n-1`; direct-sum of the three nontrivial kernels certified (`direct_sum_certified: true`) and set-equal to ker T (`set_equality_sum_eq_kerT: true`); `ker_x1_subset_kerT: false` as expected (`p_divides_n: false`, 13 mod 7 != 0). |
| C6 (known-false configs) | **PASS**: repeated-subspace and overlapping-index-set configurations both correctly refused; `V={0}` triggers the denominator-zero rule (`p_m=[0, 5230260]`); `V=F_{q^n}` at m=1 gives `p_1 = 5230260/5230260 = 1` exactly. |
| C7 (denominator-zero rule) | **PASS**: `cost_ratio()` returns `None` (never 0, never a finite placeholder) on the `p_m=0` configuration; the reported ratio object carries `denominator_zero: true` and retains the exact numerator `[0, 2]`, with no `value` key present. |
| C8 (independent recheck) | **PASS**: see Section 8; `checker.py`'s `all_independent_checks_pass: true`. |

## 6. C4 null-curve point-counting timing

Per the handoff's explicit instruction to budget and report real time for
C4's independent point-counting call over the full 62,748,517-element field:
Sage's `EK.order()` on the null curve (A'=z, B'=z+7) completed in
**0.00214 seconds** wall-clock -- SEA-based order computation is indeed fast
at this scale, confirmed rather than assumed, as instructed. (7 candidate
`(a,b)` pairs were rejected before this curve was accepted; see
`C4_rejected` in the raw output for reasons.)

## 7. Observed wall-clock and memory against budget

| quantity | value | budget | within budget? |
|---|---|---|---|
| total wall-clock (driver subprocess) | 1,265.94 s (~21.1 min) | 10,800 s (3 h, advisory) | **Yes**, by a wide margin (~11.7% of budget) |
| object-curve search | 0.058 s | -- | -- |
| generator search | 0.0005 s | -- | -- |
| object-arm enumeration (1 full N-pass) | 246.5 s | -- | -- |
| C2 pool search (subspace certification only) | 0.108 s | -- | -- |
| C2 membership passes (1 full N-pass, since only d=6 needed) | 945.2 s | -- | -- |
| C4 null-curve search + order count | 0.027 s | -- | -- |
| peak RSS (`peak_rss_bytes_self`) | 1,173,782,528 bytes (~1.09 GiB) | 8 GiB (8,589,934,592 bytes) | **Yes** (~13.7% of cap) |
| CPU seconds | 1,267.23 s | -- | matches wall-clock closely (single-threaded) |
| maximum_workers | 1 (after correcting a launch deviation, see below) | 1 | **Yes** |

The actual cost (2 full N-passes: one object-arm enumeration + one C2
membership pass, since the object arm only ever reached `d=6`, needing just
1 pool entry) was far cheaper than the amendment's "5-7 full passes"
estimate, which anticipated the `[2,2,2]` partition's 3-subspace C2 pool
actually being built. Because that pool was never built (Section 3), only
2 full passes were needed instead of 5-7, explaining the ~21-minute
completion versus the 60-90 minute point estimate.

**Protocol deviation, disclosed:** at launch, an initial `cd DIR && nohup
... &` compound backgrounded the `cd` together with the subprocess (a bash
parsing artifact of combining `&&` and a trailing `&` on one line), starting
a first sage subprocess (PID 566) via the subshell's own `cd`. A second,
corrected launch (separating `cd` onto its own line) started a duplicate
subprocess (PID 582) a few seconds later. This was caught before either
process produced any output (both `work/FROB-EXT-q13n7.{out.json,err.log}`
were still 0 bytes): PID 566 was killed via `kill -9` immediately, leaving
only PID 582 (the one recorded in `work/FROB-EXT-q13n7.pid`) running for the
remainder of the computation, satisfying `maximum_workers: 1`. No output was
ever produced by the killed process; no file was written by two processes.
Full detail recorded in `environment.json`.

## 8. Independent checker summary (C8)

`checker.py` (pure stdlib Python; does not import `implementation.py`,
`work/core.py`, `work/lattice.py`, or any Sage module) independently
re-derived:

- the field modulus (`x^7 + 10*x^6 + 1`, matches);
- N's primality (Miller-Rabin) and that N divides the recomputed curve order
  to exponent exactly 1;
- via its own from-scratch elliptic-curve point arithmetic (double-and-add,
  O(log N) operations, **not** a full subgroup reenumeration): that the
  reported generator lies on the curve, that `N*G` is the point at infinity
  (confirming `ord(G)=N` together with N's primality), that `pi(G) == mu*G`
  (the Frobenius eigenvalue condition), and that `mu` has multiplicative
  order exactly `n=7` modulo N (`ord_N(mu)=n`);
- every reported `cost_ratio_neg` value (6 checked: object, C2, C3 x2 seeds,
  C4 x2 seeds, all at the single `[6]` partition) against the raw
  `(U_neg, p_m)` pairs via the frozen formula, using only Python
  `fractions.Fraction` -- **zero mismatches**;
- the object-arm `I` and `spread` independently -- both match the driver's
  reported values exactly;
- that C3/C4's `U_neg` is identical to the object arm's for the matched
  partition (the defining structural guarantee of those constructions) --
  **zero mismatches**;
- the C2 pool's pairwise distinctness (trivially, for the single dimension
  reached);
- C1's closed-form agreement and C6's refusal/degenerate-endpoint facts from
  raw data.

**A full point-by-point reenumeration of the N=5,230,261-element subgroup in
pure, non-vectorised Python is disclosed as skipped for scale** (this
field, 13^7=62,748,517, is larger than every prior cell in this experiment,
including FROB-EQDEG-q19n5's 19^5=2,476,099, which TASK-20260921-51bc02's
checker already disclosed-skipped for the identical reason) -- consistent
with, not a departure from, that established discipline.

`checker.py`'s own summary field: `"all_independent_checks_pass": true`.
Full JSON: `work/checker-report.json`, echoed into `work/checker-run1.log`.

## 9. Instrument invalidation

**None.** `cell_status: ok` was reached; no `instrument_invalidation` or
`instrument_finding_curve_mismatch` branch was taken. FROB-EXT-q13n7 has no
prior `CONSISTENCY_TARGETS` entry (this is the first attempt at any
measurement on this cell), so no cross-run consistency check applied or was
expected.

## 10. Protocol deviations, summary

One disclosed deviation (Section 7: a duplicate background-launch artifact,
caught and corrected before any output was produced, no scientific or
resource consequence). No other protocol deviation or infrastructure
failure occurred. The `[2,2,2]`-partition three-subspace richness the
amendment anticipated did not materialize for this specific curve (Section
3) -- this is a measured, disclosed structural fact about the curve, not a
deviation from the frozen protocol or this run's own methodology.

## 11. Out of scope, explicitly

Per the handoff and amendment: FROB-EXT-q13n7 curve index 1 was not
searched for or computed. No other cell in this experiment was touched. No
prior run directory was modified.
