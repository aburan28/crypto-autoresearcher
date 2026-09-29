# Implementation notes and protocol deviations — RUN-RELN-141a86-stage0bcde

Stage 0b (control tables), Stage 0c (both-engine recovery on the five
controls plus the two positive controls), Stage 0d (P2 zero-compute
check). Continuation of the frozen, approved EXP-RELN-141a86 contract per
TASK-20260907-a3097e, following the archived Stage 0a freeze
(RUN-RELN-141a86-stage0a, hash re-verified identical, see below).

All source changes below are to `experiments/EXP-RELN-141a86/source/`
(this task's write scope). No frozen `specification.yaml` value, grammar,
node-counting rule, candidate list, or threshold was edited. Two are bug
fixes to `grammar_engine.py` (extending, per the handoff's own allowance
"unless a defect requires a versioned amendment" — these are defects in the
*implementation*, not the frozen semantics; the node-counting rule,
operator set, leaf sets and enumeration order are byte-identical to
Stage 0a's `grammar.yaml`). The rest are new modules (count_vectors.py,
controls_m2_exhaustive_and_convolution.py, adapters_fb3_dreg_enum.py,
recovery_check.py, structural_presence.py) implementing Stage 0b/0c/0d
logic that did not yet exist after Stage 0a.

## 1. Hash re-verification (before reading any measured table)

Recomputed sha256 over the concatenation of `candidate-list.yaml` +
`grammar.yaml` + `environment.lock.json` (in that order, no separators)
from `RUN-RELN-141a86-stage0a/`. Result:
`f1aec620f8cb19318e6d6459174bd79b80daf6dd46fdacf6afdf2468c7cac7f2`,
IDENTICAL to the value recorded in the handoff and in
`candidate-list-hash.txt`. Proceeded per the contract's ordering_control.

## 2. grammar_engine.py bugfix A: pow/binomial magnitude cap (hang risk)

`numeric_fingerprint`'s float-based evaluation of `pow` could construct a
tower-exponential intermediate (`pow(pow(x,e1),e2)`-style nesting on the
grammar's own leaf/CONST sample grid) whose magnitude, when subsequently
fed into a further `pow` or `binomial`, made evaluation computationally
unbounded (near-infinite bignum growth / hang) rather than merely large.
Confirmed empirically: a plain enumeration of the smallest available leaf
pack (`degree_table`, 4 leaves) hung past a 60–120s timeout at complexity
7 before this fix, immediately after a `TypeError: complex` crash was
independently observed at complexity 6–7 on `pow` of a negative base to a
non-integer exponent. Fix: `pow` now (a) returns `None` (domain-invalid,
the same convention already used for division-by-zero) if either operand's
magnitude on the fixed fingerprint grid exceeds `1e6`, and (b) returns
`None` instead of raising/crashing on a non-integer power of a negative
base (previously produced a Python `complex` that then crashed
`float()`). `binomial` got the same magnitude guard. This changes ONLY
the fingerprinting/dedup pass; node counts, canonical forms, and the
grammar's enumerable expression set are unaffected — this only prevents
the dedup pass from hanging on a pathological intermediate value that
would never appear in any real fit anyway (constant_fit.py's actual
recovery evaluation, used for the real numeric checks below, is entirely
separate code and was not touched).

## 3. grammar_engine.py bugfix B: shared single CONST value in fingerprinting

**This one materially affected a scientific result and is the more
important of the two.** The original `numeric_fingerprint` bound every
`CONST` leaf in a tree to the SAME single value (`env["CONST"] =
Fraction(1,1)`), for every occurrence. The frozen `constant_fitting`
clause explicitly permits "at most two free constants per expression" —
i.e. two INDEPENDENT `CONST` occurrences are a normal, expected shape (see
candidate-list.yaml's own INV-A4 coverage law,
`div(binomial(add(B,CONST[2]),CONST[3]),N)`, and INV-8's d_reg law, each
with two independent constants). Binding both occurrences to the same
value made the dedup fingerprint spuriously conflate expressions that are
only numerically equal to some OTHER, structurally different expression
when both constants happen to equal 1 — silently discarding the genuinely
distinct, correct expression from the enumerated candidate set.

**Confirmed empirically, before the fix**: the true INV-A4 coverage law
`div(binomial(add(B,CONST),CONST),N)` (needs CONST=2 and CONST=3) was
ABSENT from the exhaustively enumerated `enum_zn_and_sidon` complexity-7
candidate set, even though its subtree `add(B,CONST)` and the leaf `CONST`
were each individually present at their own complexities — it was dropped
during the complexity-7 registration step because
`binomial(add(B,CONST),CONST)` evaluated (with CONST=1 in both places) to
a value that happened to match binomial's non-integer-argument domain
check identically to some other invalid expression, giving both the same
all-`None` fingerprint (see 3b below for the mechanism actually
responsible).

Fix: each CONST leaf now receives a DISTINCT fingerprint value, assigned
by left-to-right traversal order via a small mutable counter
(`_CONST_STREAM` / `_CONST_STREAM_IDX` in the evaluation environment),
sourced from `_CONST_STREAM_VALUES`. This is applied ONLY inside
`numeric_fingerprint` (the dedup pass); it does not change node counts,
canonical string form, enumeration order, or the grammar's semantics — the
real numeric verification of any candidate expression against measured
data (see `recovery_check.py`) always uses its own independent per-
expression constant search, never the fingerprint's placeholder values.

### 3b. Sub-defect: fractional CONST-stream values break integer-arg operators

The first attempt at the fix used distinct small RATIONAL values (e.g.
3/2, 7/3) for successive CONST occurrences. This made every expression
with a CONST feeding directly into `binomial`'s or `pow`'s integer-domain
check evaluate to `None` on every grid point (since `binomial` requires
integer arguments), so ALL such "always-undefined" expressions collided on
the same all-`None` fingerprint and were deduplicated against each other —
the exact same class of bug, just moved. Fixed by using distinct small
POSITIVE INTEGERS (2, 3, 5, 7, 11, 13, 17) for the CONST stream instead,
which keeps every occurrence evaluable. Re-verified: INV-A4's coverage law
and Delta law are now both present in the enumerated set at their
canonical complexities (7 and 3 respectively), with EXACT node-for-node
canonical-string identity to the hand-built target (see
`recovery-controls.json`).

## 4. Structural-presence check uses fingerprint equivalence, not string identity

The frozen contract's own recovery rule accepts "an algebraically
equivalent form ... after symbolic simplification". Confirmed on INV-A6:
the hand-built target `sub(add(div(conc,mu),CONST),mu)` canonicalizes to a
DIFFERENT tree shape than the earlier-registered, algebraically identical
`sub(CONST,sub(mu,div(conc,mu)))` (both compute `conc/mu + CONST - mu`).
Since the enumeration engine's own dedup already collapses algebraic
duplicates to one representative per numeric-fingerprint class, the
correct "is this target recoverable" test is fingerprint equivalence
against the enumerated set (`structural_presence.find_equivalent`), not
exact canonical-string match. Both give the same complexity (7), so this
changes no node-count claim, only which representative string is reported.

## 5. INV-1 conservation-mean control restricted to "untyped" whole-group geometries

specification.yaml's own construction clause reads "all whole-group
UNTYPED cells". The committed FB3 whole-group geometries are
`{high_bit_interval, small_height, coset_union, mixed_two_base,
mixed_two_base__secondary_typing, asymmetric_sizing}`. Empirically (not
assumed): the conservation-mean identity `mean == binomial(B+2,3)/N` holds
to `1e-9` relative on ALL 144 cells of the first three geometries and on
ZERO of the 144 cells of the latter three (their names — "typed", "mixed
two base", "asymmetric sizing" — indicate a structured/typed base
convention under which the recorded "B" is not the unconstrained size fed
into an unconstrained `C(B+2,3)` count). `UNTYPED_GEOMETRIES =
{high_bit_interval, small_height, coset_union}` in
`adapters_fb3_dreg_enum.py` encodes this, verified programmatically (see
`control-tables/inv1-conservation-mean-table.json`, 144/144 match).

## 6. P2 check: rung-level curve-cluster SE, not the raw per-draw null_sd

The committed FB3 `metrics.<stat>.null_detail.null_sd` field is the
standard deviation of the null distribution ACROSS the 200 matched-random
draws for cell-vs-null outlier testing — a different quantity from the
PRECISION of the null MEAN estimate used to test Delta_null against a
fixed theoretical prediction. Using the raw `null_sd` directly as "the SE"
for the P2 comparison gives an SE far too large (visually: <1 SE agreement
even against the trivial `1-1/N` prediction, which the contract predicts
should be rejected by >10 SE at 2^14). Also discovered: the null draws are
literally SHARED across the three untyped geometries at matched
`(curve_index, rep_seed)` (identical `null_mean`/`null_sd` values,
confirmed by direct comparison) — so the genuine independent-replicate
count at a rung is 16 (4 curves × 4 rep_seeds), not 48 (× 3 geometries).
Fix: `build_p2_check` deduplicates by `(curve_index, rep_seed)` and reports
`delta_null_curve_cluster_se = SD(16 independent Delta_null draws) /
sqrt(16)`, matching the "curve-cluster bootstrap ... error bar" convention
stated in the contract's own `replication` clause. Result: diff-vs-INV-A1
= 0.30–0.42 SE (well within 3 SE) and diff-vs-trivial = 21.0 SE at 2^14
(> 10 SE, matching the contract's PRE-STATED prediction almost exactly) —
this is strong internal cross-validation that the curve-cluster SE
convention, not the raw per-draw null_sd, is the one the frozen
`preregistered_prediction` text was written against. The raw per-draw
value is still reported per-cell, labeled informational, never used for
the gate.

## 7. INV-7 x-class realization: direct Z/N combinatorics, not an actual EC

The x-class convention (V a random B-subset of the n=(N-1)/2 x-classes of
a prime-order curve, loop counted) is realized DIRECTLY in Z/N
combinatorics: an x-class is exactly the orbit `{r, -r mod N}` of the
point-negation involution, the same abstract structure whether or not the
ambient group is literally an EC point group. N is generated as an actual
random (Miller-Rabin) prime of the requested bit size, so N is a genuine
prime for every arithmetic purpose this control exercises; only the
(x,y)-coordinate embedding is not constructed, and the closed-form target
`1 - C(n-B,B)/C(n,B)` is a statement purely about the n abstract classes.
This is disclosed, not silent.

## 8. Bose-Chowla B_3 construction (INV-A4)

Implemented from scratch: `GF(q^3)` via a randomly-searched irreducible
monic cubic over `GF(q)` (a cubic with no root in `GF(q)` cannot factor as
linear×linear×linear or linear×quadratic, hence is irreducible — sufficient
test for degree 3), a verified multiplicative generator `theta` (order
`q^3-1`, checked against every prime factor of `q^3-1` by trial-division
factorization), a discrete-log table built by repeated multiplication by
`theta`, and the classical construction `D = {log(x + c) : c in GF(q)}`
(x the field's own degree-1 generator, not `theta`), giving a genuine
`|D| = q` set. Verified for q in {29, 41, 67, 101}: `max_count == 1` in
every case (an exact B_3 / Sidon-for-3-sums set), and both `coverage` and
`Delta` match their closed forms to machine precision (see
`control-tables/inva4-bose-chowla-table.json`).

## 9. Recovery-check CONST fitting: disclosed small rational search grid

`recovery_check.verify_expression_on_table` fits the (≤2) free `CONST`
placeholders of a SPECIFIC, already-known target expression by searching
`CONST_SEARCH_GRID` (all `p/q` with `q in 1..4`, `p in -8..12`; 84 values,
7056 pairs for 2-constant expressions) for an assignment achieving zero
max residual across every row of the real numeric table. This is NOT a
general nonlinear least-squares fit of every enumerated candidate (which,
at the enumerated-candidate-set sizes measured in Stage 0c — hundreds of
thousands to tens of millions — is computationally infeasible; see
Stage-0c note below) — it is a real, exact, disclosed verification of the
SPECIFIC target expressions named in candidate-list.yaml against real
generated/measured data.

## 10. Combinatorial explosion: exhaustive enumeration at complexity 9–11 for 6-leaf packs

Measured directly (not estimated): `enumerate_expressions` candidate counts
per complexity level grow ~6–8× per level. Small pack (`degree_table`, 4
leaves): level 6 = 12,505 (0.9s), level 7 = 85,143 (7.8s), level 8 =
531,795 (53s) [pre-CONST-fix timings; post-fix sizes are similar order].
Larger 6-leaf packs (`fb3_unsigned_m3_and_enum_unsigned_m3`,
`enum_xclass_signed_m2`, `enum_zn_and_sidon`) reach 300,000–500,000
canonical forms already at level 7 (measured: `enum_zn_and_sidon` level 7
= 427,569 forms, 251.6s). A full attempt to reach complexity 9 for the
6-leaf `fb3_unsigned_m3_and_enum_unsigned_m3` pack (INV-1's target
complexity) and complexity 9 for `enum_xclass_signed_m2` (INV-7's p_fail
target complexity) was launched as a real, timed background process;
after ~9 minutes of wall-clock CPU time each process had reached 1.5–1.7
GB resident memory and was still climbing, well short of completion, and
was terminated to avoid risking an out-of-memory crash of the shared host
(15 GB total RAM, well under the contract's advisory 16 GB ceiling once
three such processes run concurrently). `degree_table` (INV-8's pack, only
4 leaves) was allowed to continue to completion or its own resource limit;
see `recovery-controls.json` for its outcome. This is reported as
`resource_exhaustion` for the STRUCTURAL (blind-search) portion of the
INV-1 and INV-7 recovery checks specifically — never as a negative or
positive result — per the contract's own invalidation_rules ("Timeout,
out-of-memory, solver or tool crash ... is failed_infrastructure for that
stage or arm, never a negative or positive result"). The NUMERIC identity
of INV-1's and INV-7's target expressions against real generated data was
independently verified exactly (zero residual) regardless — see
`recovery-controls.json`.

## 11. Z/N interval and small-multiples positive controls

Z/N interval: computed EXACTLY (deterministic base `[1..B]`, direct
combinatorial enumeration via `count_vectors.count_vector_direct`, m=3) at
N,B matching the three FB3 rungs. Small-multiples: read directly from the
already-committed `RUN-FB3-001-{N14,N16,N18}` `exploratory[]` arrays
(arm `small_multiples_H017`), no new computation needed; the decay-ladder
(q in {0, 0.25, 0.5, 0.75, 1}) extension of this control requires
own-enumeration (Stage 0e) that was NOT built in this dispatch (out of
scope given the priority order in the handoff); only the q=0 (pure
small-multiples base) point is reported.
