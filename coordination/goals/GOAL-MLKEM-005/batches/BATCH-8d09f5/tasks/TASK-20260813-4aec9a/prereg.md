# PREREG-6 — BATCH-8d09f5 FROZEN PRE-REGISTRATION

    goal        GOAL-MLKEM-005
    batch       BATCH-8d09f5
    task        TASK-20260813-4aec9a (Coordinator, pre-registration only)
    notarized by TASK-20260813-62cd6b (snapshot archive, runs alone, before
                any measuring task)
    authority   DEC-20260813-894568 (the closing decision of BATCH-a6fab5),
                whose single `next_actions` entry this document discharges,
                and the current, correctly-set `ledger/goals/GOAL-MLKEM-005.yaml`
                `next_action` field (read fresh at authoring time and found
                consistent with DEC-20260813-894568, word for word)
    claim tier  TOY, UNCONDITIONALLY

**THIS TEXT IS FROZEN AT NOTARIZATION AND IS NEVER EDITED.** A correction is
a superseding record under a new identifier, never an edit here. No
measuring task of `BATCH-8d09f5` may be dispatched until this file is
committed by `TASK-20260813-62cd6b` and that commit contains **zero**
producer artifacts. That is the split-producer notarization pattern,
retained unchanged; it has now worked nine times and been verified in both
directions by independent sessions each time.

---

## 0. WHAT THIS BATCH DISCHARGES, AND WHAT KIND OF EXPERIMENT IT IS

`DEC-20260813-894568` closed `BATCH-a6fab5` (`T-HKZINDEP-CONFIRMED`,
Validator verdict `passed`, Red Team two MAJOR objections plus one MODERATE
and one MINOR, neither disputing the branch call) and set **exactly one**
`next_action`, quoted here because every clause of this document discharges
it:

> Commission a bounded successor task, as a new batch's lead measurement
> governed by a fresh pre-registration (PREREG-6), that builds a
> MUTATION-TESTING (positive) control on the `D_route''` / `D_route`
> instrument itself for `hkz`, rather than a further iteration of the
> `ROUTE-P`-vs-`ROUTE-I''`-style comparison. THE TASK: create a COPY of the
> shared basis-construction/definitional code path that PREREG-5 2.2 point 3
> licenses both `ROUTE-P` and `ROUTE-I''` to share ..., deliberately inject a
> single, small, precisely-described defect into that COPY ..., and confirm
> whether the EXISTING `D_route''`/`D_route` comparison mechanism (PREREG-3
> 3.3's formula, unchanged) actually detects it.

**THIS IS NOT A FOURTH ROUTE-COMPARISON ATTEMPT.** `DEC-20260813-894568`
ruling_3 rules, on an independent re-derivation of PREREG-5 2.7's own
three-part test (not by citation), that PREREG-5 2.8's third-attempt
boundary bars a fourth `ROUTE-P`-vs-`ROUTE-I'''`-style comparison for `hkz`,
but does **not** bar a structurally different instrument-calibration
positive control. This document builds exactly that different thing: a
**mutation test** with a **known, injected ground truth**, not a further
measurement of an unknown lattice quantity. Its outcome is a statement about
the `D_route` comparison mechanism's own sensitivity, never a re-score of
`hkz`'s admissibility, `T-HKZINDEP-CONFIRMED`'s own firing, or any lattice.

**WHY THIS SPECIFIC CONTROL, RESTATED FROM `DEC-20260813-894568` AND
`KN-FIND-d29ece`, NOT MERELY CITED.** Both of `BATCH-a6fab5`'s reviews
independently found, via genuinely different built controls (a from-scratch
dual-route reimplementation isolating the residual to a downstream formula
choice; a same-code-rerun null baseline plus a third, independently-structured
implementation), that `T-HKZINDEP-CONFIRMED`'s near-machine-epsilon agreement
is close to a *mathematical certainty* for any two correctly-converged
HKZ-quality implementations, **regardless of code-level independence** — so
the existing `D_route''` mechanism has demonstrated power against
wrapper-level/reduction-quality defects but **near-zero, untested power**
against a defect in code the two routes are *licensed, or required, to
share* (the seed-formula reconstruction of matrix `A`, the block-matrix
embedding, the `hkz` observable's own definition). `KN-FIND-d29ece` names the
mutation-testing control as "the decisive further check this failure mode
calls for" and "the cheapest available check that closes this gap." This
document is that check, built for the first time anywhere in this campaign.

---

## 1. INFRASTRUCTURE RE-VERIFICATION, PERFORMED FRESH IN THE LEAD'S OWN SESSION

Exactly the same discipline as `PREREG-5` section 1, restated because it
binds again: `BATCH-a6fab5`'s lead, Validator and Red Team **all three**
independently confirmed `fpylll 0.6.4` / `cysignals 1.12.5` available and
functional in their own sessions. **THIS DOES NOT LICENSE THE LEAD OF THIS
BATCH TO ASSUME `fpylll` IS AVAILABLE IN ITS OWN SESSION.** The lead's first
act, before any other code is written, is to independently re-verify this in
its own session exactly as `PREREG-5` section 1 required, and report the
outcome plainly, either way, as infrastructure signal only.

**THIS BATCH USES BRANCH A ONLY (`fpylll`'s own public API), REUSING THE
LICENSED, ALREADY-REVIEWED REDUCTION/ENUMERATION SHAPE OF
`measure_hkz_indep.py` UNMODIFIED, WITH EXACTLY ONE MUTATED LINE IN A COPIED
BASIS-CONSTRUCTION HELPER (section 2.2).** A from-scratch Branch-B
contingency (building an entire new pure-Python HKZ implementation solely to
test one seed-index defect) is **not** commissioned by this document — it
would not be the cheap, bounded control this batch is designed to be, per
`DEC-20260813-894568`'s own reasoning (iv): "cheap by this campaign's own
established standard." **If `fpylll` is unavailable in this task's own
session, that fires `T-MUTCTRL-NODATA` branch (a) directly (section 2.6)** —
recorded plainly as infrastructure signal, never as a negative result about
the instrument, and a from-scratch mutant is a decision for a later,
separately-commissioned document if ever warranted, not an automatic
fallback here.

---

## 2. THE LEAD MEASUREMENT: A MUTATION-TESTING (POSITIVE) CONTROL ON THE
##    `D_route`/`D_route''` COMPARISON MECHANISM, FOR `hkz` ONLY

### 2.0 What is being asked, restated precisely

`BATCH-a6fab5` answered "does a genuinely non-code-shared, HKZ-quality-matched
route agree with `ROUTE-P`?" — and the answer was yes, to within `{0, 2^-50,
2^-49}`, which both reviews showed is close to guaranteed for two correct
implementations regardless of independence. This document asks a
**structurally different** question: **if the code the two routes are
*licensed to share* (the seed-formula reconstruction of matrix `A`) actually
contained a small, precisely-described defect, would the EXISTING
`D_route`/`VERDICT` mechanism (unchanged from `PREREG-3` 3.3) actually flag
it?** This is a calibration check with a **known ground truth constructed by
the Coordinator**, not a measurement of an unknown lattice quantity. It is
**not** a new dispersion criterion, **not** a gate, and **not** a
re-litigation of `T-HKZINDEP-CONFIRMED`, `T-C3LANE-OPEN-PARTIAL` or
`T-INDVERIFY-ARTIFACT-PARTIAL` (section 2.7 below re-derives why, for a
fifth time in this lineage, not merely cites it).

### 2.1 Frozen objects — carried, not re-declared

    q          = 3329                           (carried, PREREG-1 2.1)
    N_BASES    = 8                               (carried; confirmed 8/8 at
               every one of the 6 hkz cells by BATCH-a6fab5's own obligation
               0, itself carried by reference from BATCH-6e08fe)

    THE TWO TARGET CELLS FOR THIS DOCUMENT, AND ONLY THESE TWO — a small
    subset of the 6 cells `BATCH-a6fab5` covered, chosen to bound cost
    (`DEC-20260813-894568`'s own example: "one L7 and one L11 cell") AND to
    bracket both lattice DIMENSION (d=20 vs d=40, so the injected defect's
    predicted per-dimension effect, section 2.3, is checked at two different
    scales) and MARGIN (the tightest and a looser predicted
    signal-to-s_c^fib ratio among the 6 covered cells, so the test is not
    accidentally calibrated to its easiest case alone):

        hkz/L7_b5   (d=20, k=6,  beta=5,  field X_a)
        hkz/L11_b30 (d=40, k=12, beta=30, field X_b)

    The other 4 of the 6 `BATCH-a6fab5`-covered cells (`L7_b15`, `L9_b7`,
    `L9_b22`, `L11_b10`) are explicitly NOT attempted by this document,
    deliberately, to bound cost. This is a declared scope limit, not a
    defect (`declared_gaps` G-4 analog, dispatch queue).

    `lam1n` remains OUT OF SCOPE, unchanged from every prior document in
    this lineage. `rawtail` remains out of scope, unchanged.

    ROUTE-P ("primary / committed pipeline route") — UNCHANGED FROM
             PREREG-3/4/5. The value of hkz at lattice L, beta b, basis i as
             already committed in `results_relvar.json`'s own
             `G_REL1.hkz.<lattice>.per_basis[i].<X_a|X_b>` field
             (`coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/
             tasks/TASK-20260809-cda2f6/results_relvar.json`, sha256
             `c5b2918dccf1b58261eed1e9d221f1074ae6143f2a8fc5c0f42ff475646ccd6d`,
             independently re-verified bit-exact by both `BATCH-a6fab5`
             reviews' RECOMP-2/probe3). READ ONLY, never recomputed, never
             re-run — exactly as every document in this lineage requires.

    ROUTE-I'' ("BATCH-a6fab5's own correct, unmutated, already-reviewed
             HKZ-quality route") — READ ONLY, for context; its own committed
             `measure_hkz_indep.py`
             (`coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/
             tasks/TASK-20260813-c0ec71/measure_hkz_indep.py`, committed at
             `3d3f5fde552f1a4783616a624f602917719701e8`) is **FROZEN AND MUST
             NOT BE EDITED, IMPORTED FROM, OR HAVE ANY OF ITS OWN LINES
             CHANGED IN PLACE**, per rule 15 and per this document's own
             design (section 2.2). It is a licensed *reading* reference for
             what to copy, nothing more.

    ROUTE-MUT ("the deliberately mutated copy") — THE OBJECT THIS TASK
             BUILDS. Defined operationally in section 2.2. Computed by the
             lead, once, for `hkz` at exactly the 2 cells named above.

    Fibre dispersion at binary64, `s_c^fib(hkz, L, b)`: THE SAME
             already-archived value used throughout this lineage —
             `results_relvar.json.G_VAR.per_candidate.hkz.per_cell.<L>_<b>.float_sd`
             — READ, never recomputed:

        s_c^fib(hkz/L7_b5)   = 0.023888 (to the precision reported in
                                          BATCH-a6fab5's own table; the
                                          executor reads and reports the
                                          full-precision value directly)
        s_c^fib(hkz/L11_b30) = 0.003818 (same note)

### 2.2 The injected defect — a checkable claim, not an assertion

**WHICH CODE PATH.** The seed-formula reconstruction of matrix `A`
(`route_ii_make_A` in `measure_hkz_indep.py`), which `PREREG-5` 2.2 point 3
explicitly licenses `ROUTE-P` and `ROUTE-I''` to share as a deterministic,
zero-degrees-of-freedom function of the frozen instance:

    def route_ii_make_A(d, k, q, i):
        rng = np.random.default_rng([1, d, k, i])
        return rng.integers(0, q, size=(k, d - k), dtype=np.int64)

**THE MUTATION, EXACT AND FROZEN, NAMED HERE BEFORE ANY RUN.** In a NEW,
self-contained file (never editing `measure_hkz_indep.py`), the lead writes
a byte-for-byte COPY of every function `measure_hkz_indep.py` uses to build
`ROUTE-I''` (`route_ii_make_A`, `route_ii_build_basis`, `hkz_route_ii`,
`route_ii_hkz_value`), with **EXACTLY ONE line changed**, in the copy of
`route_ii_make_A` only:

    def route_ii_make_A_mut(d, k, q, i, n_bases=N_BASES):
        rng = np.random.default_rng([1, d, k, (i + 1) % n_bases])   # MUTATED
        return rng.integers(0, q, size=(k, d - k), dtype=np.int64)

This is **an off-by-one in the seed-formula index tuple** — exactly the
second example `DEC-20260813-894568`'s `next_action` names. It is small
(one integer literal changed to `(i + 1) % n_bases`), it is a plausible
real bug (a classic loop-index/fencepost error — using the *next* basis's
seed instead of the current one, e.g. from an off-by-one in a
zero-vs-one-indexed loop), and it is precisely described and checkable: a
reviewer diffs the mutant file against `measure_hkz_indep.py` and confirms
**exactly this one line differs**, nothing else.

**WHY THIS DEFECT, NOT A SIGN FLIP OR A LOGDET CONSTANT.** Two other example
defects were available (`DEC-20260813-894568`'s own examples: a sign error
in the block-matrix embedding; a wrong constant in the closed-form logdet
term). The logdet-constant option was rejected on the merits: `BATCH-a6fab5`
item 4 / `RT-9` established that `ROUTE-P`'s *actual, as-run* `hkz`
computation does **not** use the closed-form logdet at all (it uses the
empirical, GSO-summed `0.5*sum(log(r))`) — so a defect injected into the
closed form alone would not be testing code genuinely shared with
`ROUTE-P`'s real computation, undermining the point of the control. A
sign-flip in the block-matrix embedding was rejected because its predicted
effect size cannot be stated in closed form from already-archived data
alone (it would require asserting an order-of-magnitude guess, not a
frozen, checkable number) — it remains a candidate for a future,
separately-commissioned mutation-testing document, not this one. The
seed-index off-by-one was chosen because **its predicted effect is
computable EXACTLY, in advance, from already-archived, already-reviewed
`ROUTE-P` data alone** (section 2.3) — the strongest, most falsifiable form
of "the exact expected magnitude ... stated in advance" `DEC-20260813-894568`
requires.

**WHAT THE MUTATION DOES, MECHANICALLY.** `route_ii_make_A_mut(d, k, q, i)`
returns the SAME matrix that `route_ii_make_A(d, k, q, i+1 mod N_BASES)`
would return — i.e., basis slot `i`'s mutant computation is secretly
computing the true HKZ profile of basis slot `(i+1) mod N_BASES`, mislabeled
as slot `i`. Every other function (`route_ii_build_basis_mut`,
`hkz_route_ii_mut`, `route_ii_hkz_value_mut`) is copied VERBATIM from
`measure_hkz_indep.py`, unchanged, so the entire measured effect is
attributable to this one line and nothing else — no other source of
divergence is introduced.

**THIS BOUNDARY DOES NOT ITSELF SPECIFY A NEW DISPERSION CRITERION, GATE OR
THRESHOLD** — it specifies exactly what code is mutated and how, for this
one calibration check, exactly as `PREREG-5` 2.2 specified what counted as
`ROUTE-I''`.

### 2.3 Obligation 0 — the frozen, pre-computed prediction

**COMPUTED HERE, BY DIRECT ARITHMETIC ON ALREADY-ARCHIVED, ALREADY-REVIEWED
`ROUTE-P` DATA, BEFORE ANY NEW REDUCTION RUNS.** Because `route_ii_make_A_mut`
at slot `i` computes what a *correctly-converged* route would compute for
slot `(i+1) mod N_BASES`, and because `BATCH-a6fab5`'s own convergence
result (all 48 (cell, basis) pairs agreeing to `~1.776e-15`) shows a
correctly-converged HKZ-quality route lands on the same value as `ROUTE-P`
to within machine epsilon, the predicted mutant value at slot `i` is
`ROUTE-P`'s own already-archived value at slot `(i+1) mod N_BASES`, **to
within the same ~2^-49 floor `BATCH-a6fab5` established for genuine
convergence** (HEURISTIC-M1, stated explicitly below). Therefore:

    predicted D_route_mut(cell) ~= max over i of
        | ROUTE-P_hkz(cell, i) - ROUTE-P_hkz(cell, (i+1) mod N_BASES) |

computed **directly from `results_relvar.json`'s own already-committed,
already-reviewed per-basis arrays** — no new reduction is needed to STATE
this prediction; the executor's own task recomputes it independently as a
cheap sanity check (section 2.4 point 1) before running anything new.

**THE ARITHMETIC, PERFORMED BY THIS (SHELL-LESS) COORDINATOR SESSION BY
DIRECT READ, STATED AS SUCH (section 7):**

`hkz/L7_b5` — `G_REL1.hkz.L7.per_basis[i].X_a`, i=0..7:
`-0.17267425560428773, -0.1929579968533437, -0.23882977009594697,
-0.17224042118823757, -0.18649226890643344, -0.22425794699744994,
-0.20262184823098472, -0.21193896956714386`. Cyclic adjacent differences
`|X_a[i] - X_a[(i+1) mod 8]|`: `0.02028, 0.04587, 0.06659, 0.01425, 0.03777,
0.02164, 0.00932, 0.03926` (5 significant figures shown; full precision in
the executor's own recomputation). **Max = `0.0665893489077094`**, at
`i=2` (`|X_a[2] - X_a[3]|`).

`hkz/L11_b30` — `G_REL1.hkz.L11.per_basis[i].X_b`, i=0..7:
`-0.13095122117764646, -0.14043123103100097, -0.13653887191980907,
-0.1367940260437619, -0.13152831554793032, -0.13139726240604777,
-0.136548162091505, -0.1400381890590845`. Cyclic adjacent differences:
`0.00948, 0.00389, 0.00026, 0.00527, 0.00013, 0.00515, 0.00349, 0.00909`.
**Max = `0.00948000985335451`**, at `i=0` (`|X_b[0] - X_b[1]|`).

**FROZEN PREDICTIONS, STATED BEFORE ANY RUN OF THIS BATCH:**

| cell | predicted `D_route_mut` | `s_c^fib` | predicted margin | predicted `VERDICT_mut` |
|---|---|---|---|---|
| `hkz/L7_b5`   | `0.0665893489077094`  | `0.023888` | ~2.79x | `DOES NOT EXCEED` (detected) |
| `hkz/L11_b30` | `0.00948000985335451` | `0.003818` | ~2.48x | `DOES NOT EXCEED` (detected) |

**HEURISTIC-M1, NAMED EXPLICITLY.** This prediction assumes the mutant's
shifted-seed HKZ-quality reduction converges as reliably as `BATCH-a6fab5`'s
own unmutated route did (all 48/48 bases converged, matched to `~1.776e-15`).
This is a reasonable extrapolation from that record, not a certainty: the
mutant runs on genuinely different, freshly-drawn matrices (the same family,
different seed draws), and `fpylll`'s convergence behavior on a specific
matrix cannot be guaranteed in advance from behavior on a different one. If
any basis fails to converge within budget, it is reported as `NOT COMPUTED:
budget exhausted`, exactly as `PREREG-5` 3.2 requires, never silently merged
or defaulted. **This prediction is NOT the pre-registered success criterion**
— section 2.6's frozen termination clause is decided by the ACTUAL measured
`D_route_mut`/`VERDICT_mut`, not by whether the measured value matches this
prediction. The prediction exists so that a wildly divergent actual result
(e.g., `D_route_mut` orders of magnitude smaller than predicted, or
convergence failing at every basis) is flagged as a finding about
`HEURISTIC-M1` or about the run itself, distinct from a finding about the
instrument's power — the two are not to be conflated in the report.

### 2.4 Obligation 1 — build, run, and compare, per target cell

For each of the 2 named cells, the lead:

1. **Independently recomputes section 2.3's prediction** directly from
   `results_relvar.json`'s own per-basis arrays (never trusting this
   document's arithmetic uncritically — a cheap, one-line sanity check
   before writing the mutant), and reports whether its own recomputation
   matches the numbers stated above. A mismatch is reported as a finding
   about THIS document, not silently corrected or silently used instead.
2. **Writes the mutant file** (section 2.2) as a byte-for-byte copy of
   `measure_hkz_indep.py`'s four `ROUTE-I''`-building functions with
   exactly the one named line changed, and includes in its report a literal,
   machine-generated unified diff (e.g. `difflib.unified_diff` or
   equivalent) between `measure_hkz_indep.py` and the mutant file, so a
   reviewer can confirm mechanically, not by trusting prose, that exactly
   one functional line differs (plus any purely cosmetic renames the lead
   judges necessary for clarity, which must ALSO be shown in the diff and
   named as cosmetic).
3. **Computes `ROUTE-MUT`'s `hkz` value** for every matched basis (up to 8,
   matching whatever `ROUTE-P`'s own per-basis array provides at that cell)
   at each of the 2 named cells, using Branch A (`fpylll`'s own public API,
   the same licensed shape as `measure_hkz_indep.py`, unmutated except for
   the one named line) per section 1.
4. **Computes, using `PREREG-3` §3.3's own, already-frozen formula, verbatim,
   applied to this route pair, EXACTLY as `PREREG-4` §2.4 and `PREREG-5`
   §2.4 each reused it before**:

       D_route_mut(hkz, L, b) = max over the matched bases i of
                                 | hkz_ROUTE-P(L, b, i) - hkz_ROUTE-MUT(L, b, i) |

       VERDICT_mut(hkz, L, b) = "EXCEEDS"          if  s_c^fib(hkz,L,b) >  D_route_mut(hkz,L,b)
                               = "DOES NOT EXCEED" if  s_c^fib(hkz,L,b) <= D_route_mut(hkz,L,b)

   **Ties resolve to `"DOES NOT EXCEED"`**, unchanged. **THIS IS NOT A NEW
   COMPARISON RULE** — it is `PREREG-3` §3.3's own rule, reused a third time,
   applied now to a route with a KNOWN, deliberately injected defect.

5. **STATES THE DETECTION MAPPING EXPLICITLY, BECAUSE IT IS EASY TO GET
   BACKWARDS AND THIS IS THE MOST CONSEQUENTIAL SENTENCE OF THIS
   DOCUMENT.** `VERDICT_mut = "DOES NOT EXCEED"` at a cell means the
   injected defect pushed `D_route_mut` far enough above `s_c^fib` that the
   ordinary comparison correctly signals a route disagreement — **this is
   the DETECTED outcome, the one section 2.3 predicts, the one that would
   demonstrate the instrument has real power against this defect class.**
   `VERDICT_mut = "EXCEEDS"` at a cell means `s_c^fib` still swamps
   `D_route_mut` despite the injected defect — **this is the NOT-DETECTED
   outcome: the instrument would silently pass this specific shared-code
   defect through as agreement**, exactly the failure mode `KN-FIND-d29ece`
   names as untested.
6. Reports, per cell: `D_route_mut`, `s_c^fib`, the number of matched
   bases, `VERDICT_mut`, whether it matches this document's frozen
   prediction (section 2.3), and the detected/not-detected reading per
   point 5.

### 2.5 Obligation 2 — the aggregate reading

Let `COVERED` = the (up to 2) cells at which `ROUTE-MUT` was actually
computed within budget for at least one matched basis and a `D_route_mut`
was produced.

    DETECTED_SET     : {cells in COVERED where VERDICT_mut = "DOES NOT EXCEED"}
    NOT_DETECTED_SET : {cells in COVERED where VERDICT_mut = "EXCEEDS"}

Report the exact membership of each set and `|COVERED|` out of 2 as the
coverage fraction, in the same sentence as any aggregate reading.

### 2.6 THE FROZEN TERMINATION CLAUSE — frozen before any cell is read,
###     FRESH, NOT A REUSE OF `T-HKZINDEP-*`

This is a positive-control/mutation-testing experiment, a genuinely
different KIND of experiment from every prior `T-HKZINDEP-*`/`T-INDVERIFY-*`
branch in this lineage, per `DEC-20260813-894568`'s own instruction that
this document "design the branch names and structure fresh, appropriate to
a mutation-testing/positive-control experiment specifically" rather than
force a `NODATA`/`ARTIFACT`/`CONFIRMED`-shaped three-way branch onto it.
**Exactly one of the following four fires, in this precedence order.**

**`T-MUTCTRL-NODATA`** — **FIRES WHEN EITHER (a)** `COVERED` is empty (no
cell of the 2 could be computed against within this task's budget), **OR
(b)** the lead's own section-1 re-verification finds `fpylll` genuinely
unavailable in its own session (per section 1, Branch B is not commissioned
by this document, so this fires directly rather than attempting a
contingency). **MEANS:** this attempt at the mutation-testing control did
not produce usable data, for a reason OTHER than the instrument's own power.
**LICENSES:** recording this plainly as infrastructure signal
(`AGENTS.md` rule 5), never as a negative or positive result about the
instrument in either direction. **FORBIDS:** any claim about `D_route`'s
power to detect a shared-code defect, in either direction; any claim about
`hkz`'s admissibility; retroactively touching `T-HKZINDEP-CONFIRMED`'s own,
separately-fired, unaffected branch in `BATCH-a6fab5`; closing, pausing or
completing `GOAL-MLKEM-005`.

**`T-MUTCTRL-DETECTED`** (suffixed `-PARTIAL` if `|COVERED| = 1`) —
**FIRES WHEN** `COVERED` is non-empty and `VERDICT_mut = "DOES NOT EXCEED"`
at EVERY cell in `COVERED`. **MEANS:** the `D_route`/`D_route''` comparison
mechanism, applied unchanged, demonstrated real power to flag this specific,
deliberately injected defect (a one-line seed-index off-by-one in the
shared basis-construction helper) at the cell(s) tested. **LICENSES:**
citing this as a positive calibration result for the `D_route` mechanism
against THIS defect class, at THIS approximate magnitude, at the cell(s)
tested — narrowly. It answers, for this one defect class, the open question
`KN-FIND-d29ece` named: the instrument is not blind to every conceivable
shared-code defect, at least not one of this shape and size. **FORBIDS:**
generalizing to any OTHER defect class (a sign flip, a logdet-constant
error, a defect at the `fpylll` C-library level itself, which this document
explicitly does not and cannot test — see section 6), to any UNCOVERED cell
of the 6, to any claim about `hkz`'s own admissibility or about
`T-HKZINDEP-CONFIRMED`'s own correctness (which tested the CORRECT,
unmutated code and is not re-litigated by this document either way); any
`ML-KEM`/FIPS 203/attack-cost/cost-model claim; closing, pausing or
completing `GOAL-MLKEM-005`.

**`T-MUTCTRL-NOT-DETECTED`** (suffixed `-PARTIAL` if `|COVERED| = 1`) —
**FIRES WHEN** `COVERED` is non-empty and `VERDICT_mut = "EXCEEDS"` at
EVERY cell in `COVERED`. **MEANS:** the `D_route`/`D_route''` comparison
mechanism, applied unchanged, would have silently passed this specific,
deliberately injected defect through as agreement, at the cell(s) tested —
a significant, surprising methodological finding (surprising relative to
section 2.3's own frozen prediction, which is not the same thing as the
prediction being wrong about the *mechanism*: an unconverged mutant basis,
per `HEURISTIC-M1`, is a distinct, separately-reportable possibility, see
section 2.4 point 1). **LICENSES:** recording this plainly as a substantive,
demonstrated limitation of the `D_route` mechanism specifically against
this defect class, to be cited alongside any FUTURE use of
`T-HKZINDEP-CONFIRMED` or any structurally similar branch in this goal.
**FORBIDS:** retroactively reopening, reversing, or re-scoring
`T-HKZINDEP-CONFIRMED`'s own firing in `BATCH-a6fab5` (which measured the
CORRECT, unmutated code; a defect-detection failure here is a statement
about the instrument's power against an INJECTED, KNOWN defect, not a
statement that `BATCH-a6fab5`'s own measured `D_route''=1.776e-15` was
itself wrong or fabricated); generalizing to any OTHER defect class or any
UNCOVERED cell; any `ML-KEM`/FIPS 203/attack-cost/cost-model claim; closing,
pausing or completing `GOAL-MLKEM-005`; treating this as grounds to declare
`hkz`'s admissibility unresolved or reopened — the correct reading is that
THIS INSTRUMENT'S power against THIS defect class is now known to be weak,
which is itself the useful, actionable result this document exists to
produce, per `AGENTS.md`'s closure standard (a named obstruction, not a
vague doubt).

**`T-MUTCTRL-MIXED`** — **FIRES WHEN** `|COVERED| = 2` and the two cells'
`VERDICT_mut` disagree (one `DOES NOT EXCEED`, one `EXCEEDS`). **MEANS:**
the instrument's power against this defect class is cell/dimension/margin
-dependent within the narrow range tested (`d=20` vs `d=40`, ~2.79x vs
~2.48x predicted margin). **LICENSES:** reporting PER CELL ONLY, exactly
which cell detected and which did not, with no aggregate claim stronger
than "mixed, cell-dependent, at this sample size of two." **FORBIDS:**
identical to `T-MUTCTRL-DETECTED`'s and `T-MUTCTRL-NOT-DETECTED`'s FORBIDS
lists, applied per cell; no averaging or majority-vote reading across the
two cells is licensed.

**PRECEDENCE, STATED EXPLICITLY.** `T-MUTCTRL-NODATA` dominates (fires
alone, no suffix). Among the remaining three, `T-MUTCTRL-MIXED` requires
`|COVERED| = 2` with disagreement and is checked first when `|COVERED| = 2`;
`T-MUTCTRL-DETECTED`/`T-MUTCTRL-NOT-DETECTED` fire (unsuffixed) when
`|COVERED| = 2` and both cells agree; either fires suffixed `-PARTIAL` when
`|COVERED| = 1`, read off that single cell's `VERDICT_mut` (`MIXED` is
undefined and cannot fire at `|COVERED| = 1`).

**A DECLARED FORWARD BOUNDARY, NAMED NOW SO IT BINDS A LATER SESSION
INCLUDING A LATER ONE OF THE COORDINATOR'S OWN.** This is the FIRST
mutation-testing control ever built in this campaign. If `T-MUTCTRL-DETECTED`
(full or `-PARTIAL`) or `T-MUTCTRL-MIXED` fires, **no further
mutation-testing control of this SAME defect class (seed-index off-by-one)
at these SAME two cells is licensed by this document alone** — a genuinely
DIFFERENT defect class (e.g. the sign-flip or logdet-constant options this
document declined, section 2.2) is a NEW question requiring its own,
separately-commissioned Coordinator decision, not an automatic successor.
If `T-MUTCTRL-NOT-DETECTED` (full or `-PARTIAL`) fires, **this document does
not pre-authorize either a repeat or an escalation** — it requires only that
the outcome be recorded plainly, per `AGENTS.md` rule 5 and rule 8, and a
future Coordinator decision, informed by that record, decides what if
anything follows. This boundary does not itself specify a criterion or
gate (section 2.7).

### 2.7 WHY THIS DOES NOT TRIGGER `PREREG-2` §7.5'S REPAIR BAR, AND IS NOT
###     AN ELEVENTH-THROUGH-TWELFTH CONSECUTIVE GATE REPAIR — RE-DERIVED
###     FOR A FIFTH TIME IN THIS LINEAGE, NOT MERELY CITED

`PREREG-2` 7.5 bars a further dispersion criterion, fibre clause or gate
repair in this goal unless six conditions hold, plus an absolute bar on an
eighth consecutive gate repair. `PREREG-3` 3.6 (1st), `PREREG-4` 2.7 (2nd),
`PREREG-5` 2.7 (3rd) and `DEC-20260813-894568` ruling_7 (4th, applied to
that decision's own acts) each independently re-derived that their own
measurement or acts were not such a repair, keeping the count at SEVEN.
Applying the identical three-part test to THIS document's own measurement,
for a fifth time, independently:

1. **It specifies no criterion, clause or gate.** §2.4's comparison is
   `PREREG-3` §3.3's OWN formula, re-applied a THIRD time (after
   `PREREG-4`'s and `PREREG-5`'s own re-applications) verbatim — not a new
   rule, not a new threshold, and not an amendment to `A-1` or to any
   candidate's admissibility. §2.6's four branches license a recorded
   finding about THIS INSTRUMENT'S OWN CALIBRATION against a KNOWN,
   deliberately injected defect — never a working assumption, never a gate,
   and never a claim about any lattice.
2. **It measures a genuinely DIFFERENT object, not a fourth iteration of
   the already-attempted comparison.** `BATCH-fbb639`, `BATCH-6e08fe` and
   `BATCH-a6fab5` each asked "does an independent route agree with
   `ROUTE-P` on an UNKNOWN lattice quantity?" This document asks "does the
   comparison mechanism detect a KNOWN, Coordinator-constructed defect?" —
   a calibration question about the instrument, not a further attempt at
   the underlying route-comparison question, per `DEC-20260813-894568`
   ruling_3's own independent re-derivation, which this document does not
   merely cite but re-applies to its own, now fully specified, design.
3. **Its outcome is a verification result about the INSTRUMENT's own
   power, never a repaired gate's pass/fail.** Every one of section 2.6's
   four branches, whichever fires, licenses no new claim about `hkz`, `A-1`,
   or any candidate's admissibility — it characterizes only the `D_route`
   mechanism's demonstrated sensitivity to one named, injected defect class.

**THE SEVEN-CONSECUTIVE-INSTRUMENT-BATCH COUNT REMAINS SEVEN, NOT EIGHT,
NINE OR TEN**, for the identical structural reason `PREREG-3` 3.6,
`PREREG-4` 2.7, `PREREG-5` 2.7 and `DEC-20260813-894568` ruling_7 each
independently gave: this document's own measurement is not a gate-repair
attempt, by the same three-part test, applied fresh.

### 2.8 WHAT THIS DOCUMENT DOES NOT LICENSE, STATED BEFORE ANY RUN

This document does **not** re-litigate `T-HKZINDEP-CONFIRMED`'s own firing
in `BATCH-a6fab5` — that branch fired correctly and mechanically on
UNMUTATED, correct code, independently re-derived by both of that batch's
reviews, and nothing in this document's outcome, whichever branch fires,
touches it. This document does **not** test `hkz`'s own admissibility,
`A-1`, or any in-scope candidate of `PREREG-2` 2.4. This document's outcome,
whichever of section 2.6's four branches fires, does **not** close, pause
or complete `GOAL-MLKEM-005` — this batch is TOY-tier instrument
calibration, explicitly not a blocking dependency for this goal's actual
mechanism-search objective (best-of-M ciphertext selection against a shared
BKZ-reduced basis, `RQ-MLKEM-001`), per `DEC-20260813-894568`'s own
reasoning (v).

---

## 3. GUARDS AND COULD-NOT-FAIL ARRANGEMENTS, NAMED BEFORE THE RUN

### 3.1 Could-not-fail check on the `D_route_mut` comparison

Would hold if `D_route_mut` were fixed by construction to guarantee either
verdict regardless of measurement. **WE ARE NOT**, for the identical reason
`PREREG-4` 3.1 and `PREREG-5` 3.1 gave: `D_route_mut` is a MEASURED max
absolute deviation between `ROUTE-P`'s already-archived values and a
FRESHLY, GENUINELY COMPUTED mutant route on a numerically DIFFERENT input
(a different, validly-drawn matrix `A`, not the same one) — it is not fixed
by construction in either direction. Section 2.3's prediction is a prior
expectation derived from a DIFFERENT already-archived quantity (`ROUTE-P`'s
own basis-to-basis dispersion), not a guarantee baked into the mutant's own
computation; the mutant's ACTUAL measured value could diverge from the
prediction (HEURISTIC-M1), and the frozen termination clause (2.6) is read
off the ACTUAL measured value, never the prediction. `s_c^fib` is an
unrelated, already-archived dispersion computation with no shared
construction with either.

### 3.2 Could-not-complete guard

Identical in shape to `PREREG-5` 3.2. If this task's hard wall-clock cap
is reached before every one of the 2 named cells has a computed
`D_route_mut`, this is INFRASTRUCTURE SIGNAL (`AGENTS.md` rule 5), reported
per-cell, distinguishing "NOT COMPUTED: budget exhausted" from a genuinely
computed value — never silently merged, never defaulted to either verdict.
An empty `COVERED` fires `T-MUTCTRL-NODATA` branch (a); a single covered
cell fires the appropriate `-PARTIAL` branch.

### 3.3 The section-1 re-verification guard

If the lead's own `fpylll` re-verification (section 1) fails, this fires
`T-MUTCTRL-NODATA` branch (b) directly — no Branch-B contingency is
commissioned by this document (section 1).

### 3.4 No reduction above `d = 40`, anywhere, for any reason

Unchanged from every document in this lineage. The two named cells are
`d=20` and `d=40`; no cell of this document reaches above `d=40`.

---

## 4. OUTCOME ROWS

| row | what it records |
|---|---|
| `R-MC-OUT-0` | section 1's infrastructure re-verification, fresh in this task's own session |
| `R-MC-OUT-0b` | obligation 1 point 1: the lead's own independent recomputation of section 2.3's frozen prediction, and whether it matches this document's stated numbers |
| `R-MC-OUT-1` | the machine-generated diff confirming exactly one functional line differs between the mutant file and `measure_hkz_indep.py` |
| `R-MC-OUT-2` | obligation 1 (§2.4): per covered cell, `D_route_mut`, `s_c^fib`, matched-basis count, `VERDICT_mut`, and the detected/not-detected reading |
| `R-MC-OUT-3` | obligation 2 (§2.5): `DETECTED_SET`/`NOT_DETECTED_SET`, coverage fraction |
| `R-MC-OUT-4` | the termination branch read off `R-MC-OUT-1`(sic, `R-MC-OUT-3`)/`R-MC-OUT-2` under §2.6's frozen precedence, with `-PARTIAL` suffix applied per its own rule |

---

## 5. BINDING CARRIES — IN FORCE, NOT RE-LITIGATED

Carried in full from `PREREG-2` §§10/10.1, `PREREG-3` §7, `PREREG-4` §5 and
`PREREG-5` §5, without restatement of every line here — the lead, the
reviews and the ledger archive are bound exactly as those documents state,
plus the following, specific to this batch:

* **CLAIM TIER TOY, UNCONDITIONALLY.**
* **`AM-3` IS NOT RETIRED.** `AM-10` through `AM-18` and their carries are
  in force. No prior batch of this goal (`BATCH-a44d08` through
  `BATCH-a6fab5`) is rescored or revalidated in any respect by anything in
  this document.
* `T-HKZINDEP-CONFIRMED` (`BATCH-a6fab5`), `T-C3LANE-OPEN-PARTIAL`
  (`BATCH-fbb639`) and `T-INDVERIFY-ARTIFACT-PARTIAL` (`BATCH-6e08fe`) ARE
  NOT REOPENED, RE-SCORED OR REVERSED by anything in this document, by
  whichever of section 2.6's four branches fires.
* **`KN-FIND-7d098b`, `KN-FIND-9d44b4`, `KN-FIND-9b5df0`, `KN-FIND-7de6b6`
  AND `KN-FIND-d29ece` ARE PROMOTED — NOT RESTATED AS NEW** anywhere in
  this document. `KN-FIND-d29ece`'s own content (the confound this batch's
  own measurement operationally tests) is cited, not repeated.
* `lam1n`'s `T-INDVERIFY-CONFIRMED` discharge (`BATCH-6e08fe`) IS NOT
  REOPENED, RE-SCORED OR REVISITED. `lam1n` is out of scope.
* The split-producer notarization pattern is retained unchanged. The
  receipt-with-`commit_sha: null`-inside-its-own-commit archive pattern is
  MANDATORY. Every run emits durable `command.txt`, `stdout.log` and
  `stderr.log`, with no path inside a folded YAML scalar, and lists every
  path it wrote in its report.
* `knowledge/INDEX.md` must NOT be written, regenerated or staged.
* **`AGENTS.md` rule 12 is UNMET AND UNWAIVED.** Every producer and reviewer
  of this batch records `model_verified: false` with its reason, its host
  and its stack. THIS BINDS THIS BATCH'S OWN REVIEWS EXACTLY AS MUCH AS IT
  BINDS THE PRODUCER.
* **`PD-4` remains OPEN.** Each review's own report and probes sit
  uncommitted across a dispatch window and are the sole carriers of their
  own evidence until the ledger archive commits them.
* No prior batch's immutable, committed or cancelled artifacts
  (`BATCH-6e08fe`, `BATCH-7033ee`, `BATCH-fbb639`, `BATCH-a6fab5`, or any
  earlier batch) are touched, edited, or remapped by anything in this
  document.

---

## 6. SCOPE, INDEPENDENCE, AND WHAT THIS BATCH CANNOT DO

**SCOPE.** `q = 3329`; `d in {20, 40}` (`L7`, `L11` ONLY — `L9` is not
attempted by this document); `hkz` ONLY; exactly the 2 named cells
(`L7_b5`, `L11_b30`); up to `N_BASES = 8` per cell; `binary64` only. **NO
REDUCTION ABOVE `d = 40`, ANYWHERE, FOR ANY REASON.**

**THIS BATCH'S OWN SCOPE, CARRIED AT EVERY QUOTATION.** This measurement
tests ONE defect class (a one-line seed-index off-by-one) in ONE licensed
-shared code path (the basis-construction helper), at ONE approximate
magnitude, at TWO cells. It says NOTHING about: whether the SAME mechanism
would catch a DIFFERENT defect class (a sign flip, a wrong constant, a bug
inside `fpylll`'s own C/Cython Enumeration or BKZ kernel — this document
explicitly does not and, given it reuses `fpylll`'s library code unmodified,
structurally cannot test a defect INSIDE that library); a SMALLER or
LARGER-magnitude defect than the one tested; any UNCOVERED cell (the other
4 of `BATCH-a6fab5`'s 6, or any middle-beta cell); `A-1`; any in-scope
candidate of `PREREG-2` 2.4; `ML-KEM`; any FIPS 203 parameter set; any
attack cost; any cost model. Its most favourable branch
(`T-MUTCTRL-DETECTED`) licenses citing a narrow, positive calibration
result for THIS defect class at THESE cells — nothing stronger.

**INDEPENDENCE IS PROCEDURAL AND NEVER MODEL-LEVEL.** `AGENTS.md` rule 12
is UNMET AND UNWAIVED in this goal and is not waived here — this binds this
batch's own reviews too.

**THIS BATCH DOES NOT RE-LITIGATE `T-HKZINDEP-CONFIRMED`'s OWN FIRING, DOES
NOT TEST `hkz`'s ADMISSIBILITY, AND ITS OUTCOME EITHER WAY DOES NOT
CLOSE, PAUSE OR COMPLETE `GOAL-MLKEM-005`**, restated here a final time so
it is not missed at close.

---

## 7. AUTHORSHIP GAP, DECLARED RATHER THAN NARRATED CLOSED

The Coordinator session that wrote this file **held no shell**. It ran no
git command and computed no hash. It DID read committed repository files
directly with a read-only tool (never a shell) and performed the
arithmetic in section 2.3 BY HAND, from those directly-read numbers — this
is a weaker claim than a measurement: it is one session's arithmetic on
committed files at one point in time, offered so the lead can check it
independently (obligation 1 point 1, section 2.4), not offered as this
batch's own evidence. If the lead's own independent recomputation disagrees
with section 2.3's stated numbers, that disagreement is reported as a
finding about THIS document, not silently corrected, and not treated as
evidence about the instrument.

`prereg_sha256.txt` is generated and committed by `TASK-20260813-62cd6b`,
by a session that has a shell, exactly as every prior `PREREG-*` of this
goal required for its own hash file.

**END OF FROZEN TEXT.**
