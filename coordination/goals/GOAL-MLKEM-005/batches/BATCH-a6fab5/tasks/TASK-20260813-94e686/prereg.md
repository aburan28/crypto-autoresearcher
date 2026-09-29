# PREREG-5 — BATCH-a6fab5 FROZEN PRE-REGISTRATION

    goal        GOAL-MLKEM-005
    batch       BATCH-a6fab5
    task        TASK-20260813-94e686 (Coordinator, pre-registration only)
    notarized by TASK-20260813-d63082 (snapshot archive, runs alone, before any
                measuring task)
    authority   DEC-20260813-1aae44 (the closing decision of BATCH-6e08fe,
                whose `next_actions` field this document discharges), and the
                current, correctly-set `ledger/goals/GOAL-MLKEM-005.yaml`
                `next_action` field (verified consistent with
                DEC-20260813-1aae44 section 11 at authoring time -- no
                staleness correction is needed this time, unlike the prior
                two batches)
    claim tier  TOY, UNCONDITIONALLY

**THIS TEXT IS FROZEN AT NOTARIZATION AND IS NEVER EDITED.** A correction is a
superseding record under a new identifier, never an edit here. No measuring
task of `BATCH-a6fab5` may be dispatched until this file is committed by
`TASK-20260813-d63082` and that commit contains **zero** producer artifacts.
That is the split-producer notarization pattern, retained unchanged; it has
now worked eight times and has been verified in both directions by
independent sessions each time.

---

## 0. WHAT THIS BATCH DISCHARGES, AND WHY IT IS SCOPED TO `hkz` ALONE

`DEC-20260813-1aae44` closed `BATCH-6e08fe` (`T-INDVERIFY-ARTIFACT-PARTIAL`,
Validator verdict `passed`, Red Team one MAJOR objection) and set **exactly
one** `next_action`, quoted here because every clause of this document
discharges it:

> Commission a bounded successor task, as a new batch's lead measurement
> governed by a fresh pre-registration (PREREG-5), that builds a GENUINELY
> HKZ-QUALITY (not LLL-quality) independent ROUTE-I'' for `hkz` at
> `L7`/`L9`/`L11`, using the SAME frozen `ROUTE-P` values and the SAME
> `PREREG-3` 3.3 comparison formula, at the SAME 6 currently-covered `hkz`
> cells.

**`lam1n` IS OUT OF SCOPE FOR THIS BATCH, EXPLICITLY.** `BATCH-6e08fe`
already discharged `lam1n`'s independent-verification question in full:
`T-INDVERIFY-CONFIRMED` fired for `lam1n`'s 6 covered cells
(`EV-MLKEM-5aa471.lam1n_confirmed_discharge`), a THIRD, independently-built
implementation (the Validator's own) corroborated it at `L7`/`L9`, and
`DEC-20260813-1aae44` closed that question without a stated revisit
condition. Building a further `lam1n` route here would not discharge any
open uncertainty and is not commissioned. This document's entire content is
`hkz`-only.

**WHY `hkz` SPECIFICALLY, RESTATED FROM `DEC-20260813-1aae44`'S OWN
REASONING, NOT MERELY CITED.** `BATCH-6e08fe`'s own convergent finding
(Validator section 6, Red Team section 3/7, `KN-FIND-7de6b6`) showed that its
`ROUTE-I'` for `hkz` was genuinely non-code-shared but NOT quality-matched --
LLL(delta=0.99)-only, against `ROUTE-P`'s genuinely HKZ-quality
(BKZ-block=`d` + explicit HKZ sweep + independent per-index enumeration
verification) pipeline. `DEC-20260813-1aae44` section 3 ruled, as a
Coordinator-level judgment going beyond what either review literally
recommended, that this quality mismatch means the revisit condition's
antecedent (a GENUINE, quality-matched test of whether code-independence
alone changes the answer) was NOT satisfied for `hkz`, so its consequent
(flagging `BATCH-fbb639`'s `hkz` `EXCEEDS` verdicts methodologically
unsupported) did NOT fire. `hkz`'s status was left EXACTLY as
`BATCH-fbb639` qualified it -- neither newly confirmed nor newly flagged.
This document commissions the ONE measurement that would actually settle
that open question: a route matched to `ROUTE-P`'s own reduction FIDELITY,
not merely independent of its CODE.

---

## 1. INFRASTRUCTURE SIGNAL RECORDED SINCE `DEC-20260813-1aae44` -- TO BE
##    INDEPENDENTLY RE-VERIFIED BY THE LEAD, NEVER ASSUMED FROM THIS TEXT

`DEC-20260813-1aae44`'s `next_action` named, as its first, cheap sub-step,
attempting `pip install fpylll` as an up-front infrastructure check. **This
has since been done, by the session dispatching this batch, in ITS OWN
environment**: `pip install fpylll` succeeded (`fpylll 0.6.4`), and after
also installing its missing transitive dependency `cysignals`
(`pip install cysignals`, `cysignals 1.12.5`), `import fpylll`,
`from fpylll import IntegerMatrix, LLL, BKZ` and a basic LLL reduction all
worked correctly in that session. **This is recorded here PLAINLY AS
INFRASTRUCTURE SIGNAL -- NOT a negative or positive research result of any
kind, an environment fact only**, and it is the FIRST time in three dedicated
checks across this campaign's history (`BATCH-fbb639`'s original attempt,
`BATCH-6e08fe`'s from-scratch fallback, and this out-of-band check) that
`fpylll` has been confirmed installable and functional anywhere in this
harness's execution environment.

**THIS DOES NOT LICENSE THE LEAD TO ASSUME `fpylll` IS AVAILABLE IN ITS OWN
SESSION.** Environments can and have differed between sessions and
containers of this harness (`PREREG-4` section 5's own independence note;
`AGENTS.md` rule 12). **THE LEAD'S FIRST ACT, BEFORE ANY OTHER CODE IS
WRITTEN, IS TO INDEPENDENTLY RE-VERIFY THIS IN ITS OWN SESSION**: attempt
`pip install fpylll` (and `pip install cysignals` if the first attempt fails
on the same missing-transitive-dependency error), then
`import fpylll; from fpylll import IntegerMatrix, LLL, BKZ, GSO, Enumeration`,
and report the outcome PLAINLY, either way, as infrastructure signal, before
choosing which branch of section 2.2 it uses. A prior session's success is a
POINTER that the attempt is now worth making promptly, never a substitute
for the lead's own check, and never evidence in either direction about
`hkz`.

---

## 2. THE LEAD MEASUREMENT: A GENUINELY HKZ-QUALITY, NON-CODE-SHARED SECOND
##    ROUTE FOR `hkz`, AT THE SAME 6 COVERED CELLS

### 2.0 What is being asked, restated precisely

`BATCH-6e08fe`'s `ROUTE-I'` for `hkz` answered "is a code-independent route
that uses LLL-quality reduction close to `ROUTE-P`'s HKZ-quality values?" --
and the convergent answer was "no, by `0.015`-`0.223`, substantially
attributable to the reduction-quality gap, not to code-sharing"
(`hkz_qualification_citable_wording`, `EV-MLKEM-5aa471`). This document asks
a DIFFERENT, narrower and more decisive question: **does a genuinely
non-code-shared route that ALSO matches `ROUTE-P`'s reduction FIDELITY (not
merely its code-independence) still show `s_c^fib > D_route''` at the cells
it can reach?** This is **not** a new dispersion criterion, **not** a gate,
and **not** a re-litigation of `T-C3LANE-OPEN-PARTIAL` or of
`T-INDVERIFY-ARTIFACT-PARTIAL` itself (section 2.7 below re-derives why, not
merely cites it) -- it is the ONE remaining control both of `BATCH-6e08fe`'s
reviews independently named as decisive and neither could build
(`VAL-20260813-71d65d` section 6 `conclusion_on_the_crux`; `RT-20260813-7930a6`
section 9 `next_concrete_action`), and it is the exact successor
`DEC-20260813-1aae44` section 11 commissions.

### 2.1 Frozen objects -- carried, not re-declared

    q          = 3329                          (carried, PREREG-1 2.1)
    N_BASES    = up to 8 (basis index i = 0..7), matching whatever ROUTE-P's
               own per-basis array provides at each cell -- UNCHANGED FROM
               PREREG-3/PREREG-4.
    Lattices and betas in scope for this batch, and ONLY these -- EXACTLY the
    6 cells BATCH-6e08fe's own obligation 0 found COVERED for hkz, carried
    BY REFERENCE from results_route_reimpl.json.R_IV_OUT_1 and
    EV-MLKEM-5aa471.termination_branch, NOT RE-DERIVED (BATCH-6e08fe's own
    obligation-0 coverage table for these 6 cells was independently
    re-derived by BOTH of that batch's reviews and is not reopened here):
        hkz/L7_b5   (d=20, k=6,  beta=5)
        hkz/L7_b15  (d=20, k=6,  beta=15)
        hkz/L9_b7   (d=30, k=9,  beta=7)
        hkz/L9_b22  (d=30, k=9,  beta=22)
        hkz/L11_b10 (d=40, k=12, beta=10)
        hkz/L11_b30 (d=40, k=12, beta=30)
    Candidate: hkz ONLY. lam1n is OUT OF SCOPE (section 0). rawtail remains
    out of scope for the same reason PREREG-4 2.1 gave (no ROUTE-I of any
    kind exists for it anywhere in the committed corpus).
    The 6 middle-beta cells (L7_b10, L9_b15, L11_b20) REMAIN GENUINELY
    UNCOVERED, unchanged from BATCH-6e08fe's own finding (results_relvar.json's
    G_REL1 block has no per-basis ground truth there) -- this document does
    NOT re-attempt them and does not ask the lead to.

    ROUTE-P  ("primary / committed pipeline route") -- UNCHANGED FROM
             PREREG-3/PREREG-4. The value of hkz at lattice L, beta b, basis
             i as computed by the FROZEN, ALREADY-COMMITTED measure_relvar.py
             pipeline of BATCH-9e3584, committed at
             coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/
             TASK-20260809-cda2f6/results_relvar.json. THIS IS AN
             ALREADY-ARCHIVED VALUE. It is READ, never recomputed, never
             re-derived, and NEVER re-run.

    ROUTE-P's ONLY VALID SOURCE, UNCHANGED FROM PREREG-4 2.1: results_relvar.json's
             OWN G_REL1.hkz.<lattice>.per_basis array. results_l7l8.json and
             results_am4.json REMAIN EXPLICITLY EXCLUDED AS A SOURCE OF
             ROUTE-P VALUES, for the identical reason PREREG-4 2.1 gave: both
             are ROUTE-I-family artifacts under F-1/RT-1's finding.

    ROUTE-I' ("BATCH-6e08fe's own LLL-quality independent route") -- READ
             ONLY, for context and comparison in the lead's own report; NEVER
             used as a source of ROUTE-P values, and NEVER copied as a source
             of the reduction/enumeration code for ROUTE-I'' (section 2.2
             below). Its basis-construction helper (make_A_indep/
             build_basis_indep) MAY be reused or re-derived under the SAME
             license PREREG-4 2.2(3) already grants for reconstructing the
             numeric matrix A -- this was never the part either review
             questioned.

    ROUTE-I'' ("genuinely HKZ-quality, non-code-shared re-implementation
             route") -- THE OBJECT THIS TASK BUILDS. Defined operationally in
             section 2.2. Computed by the lead, once, for hkz at exactly the
             6 cells named above. NEVER READ FROM ANY COMMITTED FILE -- this
             is the one genuinely new computation in this batch.

    Fibre dispersion at binary64, s_c^fib(hkz, L, b): the ALREADY-ARCHIVED
             float_sd value, at the JSON path BATCH-6e08fe's own obligation 0
             actually resolved it to (not PREREG-4's stated path, which does
             not exist verbatim in the committed file):
             results_relvar.json.G_VAR.per_candidate.hkz.per_cell.<L>_<b>.float_sd
             -- carried from report_route_reimpl.md's own path-resolution
             note, independently un-contested by both of BATCH-6e08fe's
             reviews. READ, never recomputed.

### 2.2 What "genuinely non-code-shared AND HKZ-quality" means, operationally
###     -- A CHECKABLE CLAIM, NOT AN ASSERTION

A `ROUTE-I''` implementation satisfies this document's independence AND
fidelity requirement if and only if **all** of the following hold, and the
lead's report states, explicitly and BEFORE any `D_route''` number is
computed, which choice it made, in which branch, and why:

1. **No transcription of the barred kernel.** The code that (a) turns the
   frozen instance matrix `A` into a basis object ready for reduction, and
   (b) performs the reduction/enumeration and extracts `hkz`, is NOT copied,
   adapted, wrapped, or structurally paraphrased from `make_A`,
   `build_basis` or `hkz_profile` as they appear in `measure_am4.py`,
   `measure_relvar.py`, `replicate_l7l8.py`, or ANY descendant (this
   explicitly includes `BATCH-4ed139`'s `replicate_l7l8.py`, exactly as
   `PREREG-4` 2.2 point 1 barred). **THIS DOCUMENT ADDS ONE FURTHER BAR,
   NEW TO THIS LINEAGE:** the reduction/enumeration code of `BATCH-6e08fe`'s
   own `ROUTE-I'` (`measure_route_reimpl.py`'s `lll_reduce`/`enumerate_svp`)
   is likewise NOT to be copied, adapted or structurally paraphrased for
   `ROUTE-I''`'s own reduction/enumeration step -- `ROUTE-I''` must be a
   FRESH implementation of the HKZ-quality step, not a quality-upgrade patch
   applied to `ROUTE-I'`'s own LLL code. (The basis-construction helper is a
   narrow, explicitly licensed exception -- see point 3.)
2. **A genuinely HKZ-quality implementation of the reduction/enumeration
   step**, chosen from EXACTLY ONE of the following two branches, named and
   justified in the report, selected only after the section 1 re-verification
   above:
   **BRANCH A -- `fpylll` (or an equivalent independently-maintained
   lattice-reduction library) IS AVAILABLE in the lead's own session.** Use
   `fpylll`'s OWN public reduction/enumeration API directly --
   `fpylll.IntegerMatrix`, `fpylll.GSO.Mat`, `fpylll.LLL.reduction` (or
   `.Reduction`), `fpylll.BKZ.Param`/`fpylll.BKZ.reduction` (or
   `.BKZReduction`), and `fpylll.Enumeration` -- writing a FRESH wrapper that
   calls this public API, matching `ROUTE-P`'s own algorithm description AS
   CLOSELY AS AN INDEPENDENTLY-WRITTEN WRAPPER ALLOWS: one BKZ pass at
   `block_size = d` via `BKZReduction`, explicit HKZ sweeps reading the
   Gram-Schmidt norms off the reduced basis, and an INDEPENDENT PER-INDEX
   ENUMERATION VERIFICATION step -- exactly the three-part structure both of
   `BATCH-6e08fe`'s reviews independently confirmed `ROUTE-P`'s own
   `hkz_profile` performs (`VAL-20260813-71d65d` OR-1: *"one BKZ pass at
   block_size=d via BKZReduction, explicit HKZ sweeps via Mg.get_r/
   Enumeration(Mg).enumerate, and an independent per-index verification
   enumeration"*). Using the SAME underlying library `ROUTE-P` uses is
   EXPLICITLY LICENSED and is NOT what F-1/RT-1 or `KN-FIND-7de6b6`
   criticized -- both `PREREG-4` 2.2(2)(ii) and this document's own text bar
   only the campaign's own hand-written WRAPPER functions (`make_A`,
   `build_basis`, `hkz_profile`), never the library itself. This branch is
   the INTENDED, PRIMARY path, given the infrastructure signal in section 1.
   **BRANCH B -- `fpylll` REMAINS UNAVAILABLE in the lead's own session
   (and no equivalent library is found).** Build a from-scratch, full
   HKZ-quality implementation in pure Python/numpy: BKZ at `block_size = d`
   (not merely LLL), an explicit HKZ sweep, and an independent per-index
   enumeration verification step -- matching `ROUTE-P`'s own three-part
   algorithm structure as closely as a from-scratch implementation allows,
   bounded to `d <= 40` exactly as every reduction this goal has ever run.
   **A NAMED CAUTION FOR THIS BRANCH ONLY, NOT A CONSTRAINT:** the
   dispatching session's own due-diligence pass on `BATCH-6e08fe`'s archived
   `measure_route_reimpl.py` found (and reverted, per rule 15 -- archived
   artifacts are immutable) an unauthorized external edit targeting a real
   theoretical asymmetry in that script's Schnorr-Euchner zig-zag enumeration
   order (`enumerate_svp` always tries the `c0-1` offset before `c0+1`
   regardless of which side of the rounded center the true fractional center
   falls on, so a `break` on a failing negative offset can in principle skip
   a still-viable, strictly closer positive offset). Adversarial empirical
   testing (23,000+ random trials at small dimensions against exhaustive
   brute-force ground truth) found ZERO cases where this produced an
   actually-wrong answer, but this is empirical, not a proof. **If Branch B
   is used and the lead writes its own enumeration routine, it should be
   aware of this concern rather than blindly copying that exact zig-zag
   ordering** -- this is a CAUTION, not a bar on any particular
   enumeration-order choice, and it is MOOT under Branch A, where
   `fpylll.Enumeration` (a mature, independently-maintained library routine,
   not this campaign's hand-rolled one) is used directly.
3. **The frozen instance itself may be reconstructed from its own published
   formula, and the basis-construction helper may be reused across routes.**
   Building the SAME numeric matrix `A` from the declared, already-public
   seed formula (`default_rng([1, d, k, i]).integers(0, q, (k, d-k))`) is NOT
   code-sharing, per `PREREG-4` 2.2(3), carried unchanged. The block-matrix
   embedding `B = [[I_k,A],[0,qI_{d-k}]]` may likewise be reconstructed
   identically to `ROUTE-I'`'s own `build_basis_indep` (or written fresh --
   either is licensed), since this step is a deterministic,
   zero-degrees-of-freedom function of `A` and the lattice's own public
   definition, exactly as `VAL-20260813-71d65d` OR-1 and `RT-20260813-7930a6`
   section 1 both independently found for `ROUTE-I'`. What must be
   independent, per points 1 and 2, is the CODE PATH that performs the
   reduction/enumeration and extracts `hkz`, not the numeric input or its
   embedding.
4. **The choice is declared and justified in the report, prominently, BEFORE
   the `D_route''` table is presented** -- naming the exact library/routine
   used, which branch (A or B) was taken and why, and stating explicitly that
   the reduction/enumeration code does not derive from the named barred
   lineage OR from `ROUTE-I'`'s own reduction/enumeration code, so a reviewer
   can check the claim against the actual committed script rather than trust
   the prose.

**THIS BOUNDARY DOES NOT ITSELF SPECIFY A NEW DISPERSION CRITERION, GATE OR
THRESHOLD** -- it specifies what counts as a valid `ROUTE-I''` SOURCE for
this one measurement, exactly as `PREREG-4` 2.2 specified for `ROUTE-I'`.

### 2.3 Obligation 0 -- coverage, CARRIED BY REFERENCE, not re-derived

Unlike `PREREG-4` 2.3, this document does NOT ask the lead to re-derive
coverage from scratch: the 6 covered `hkz` cells are frozen in section 2.1
above, carried by reference from `BATCH-6e08fe`'s own obligation-0 table,
independently re-derived and confirmed by BOTH of that batch's reviews
(`VAL-20260813-71d65d` AC-8; `RT-20260813-7930a6` section 1, Third target).
**THE LEAD'S OWN FIRST ACT IS THE SECTION 1 INFRASTRUCTURE RE-VERIFICATION,
NOT A COVERAGE AUDIT.** The lead MUST, however, confirm by direct read of
`results_relvar.json`'s own `G_REL1.hkz` block that per-basis ground truth
genuinely exists at all 6 named cells before computing against them (a
cheap, one-line sanity check against a value this document asserts rather
than re-derives from scratch) and report the exact basis count found at
each cell (expected 8; report the actual count, never assume).

### 2.4 Obligation 1 -- the independent computation and the `D_route''`
###     comparison, per covered cell

For each of the 6 named cells:

1. Builds its own `ROUTE-I''` value of `hkz` at that (lattice, beta, basis),
   for every matched basis (up to 8, matching whatever `ROUTE-P`'s own
   per-basis array provides at that cell -- report the exact subset size
   used), using the implementation choice declared and justified per 2.2.
2. Computes, **using `PREREG-3` §3.3's own, already-frozen formula,
   verbatim, applied to this route pair, EXACTLY as `PREREG-4` §2.4 reused
   it**:

       D_route''(hkz, L, b) = max over the matched bases i of
                               | hkz_ROUTE-P(L, b, i) - hkz_ROUTE-I''(L, b, i) |

       VERDICT''(hkz, L, b) = "EXCEEDS"          if  s_c^fib(hkz,L,b) >  D_route''(hkz,L,b)
                             = "DOES NOT EXCEED" if  s_c^fib(hkz,L,b) <= D_route''(hkz,L,b)

   **Ties resolve to `"DOES NOT EXCEED"`**, unchanged. **THIS IS NOT A NEW
   COMPARISON RULE** -- it is `PREREG-3` §3.3's own rule, reused a second
   time (the first being `PREREG-4` §2.4), applied now to a route that is
   both independent AND fidelity-matched.
3. Reports, per cell: `s_c^fib`, `D_route''`, the number of matched bases,
   the implementation choice used (branch A or B, section 2.2), `VERDICT''`,
   and -- because `BATCH-fbb639`'s original `EXCEEDS` verdict exists at every
   one of these 6 cells and `BATCH-6e08fe`'s `T-INDVERIFY-ARTIFACT` flag
   already applies to all 6 -- **whether `VERDICT''` reads toward discharge
   (`EXCEEDS`, matching `lam1n`'s own discharge pattern) or toward confirming
   the flag (`DOES NOT EXCEED`, matching `BATCH-6e08fe`'s own LLL-quality
   finding)** (section 2.6/2.8).

### 2.5 Obligation 2 -- the aggregate reading

Let `COVERED` = the (up to 6) cells at which section 2.3's sanity check
confirms genuine `ROUTE-P` per-basis ground truth AND at which `ROUTE-I''`
was actually computed within budget (section 3.2's guard).

    ALL-SURVIVE  :  VERDICT''(hkz, L, b) = "EXCEEDS" for EVERY cell in COVERED
    SOME-ARTIFACT:  VERDICT''(hkz, L, b) = "DOES NOT EXCEED" for AT LEAST ONE cell in COVERED

Mutually exclusive, exhaustive of `COVERED` whenever non-empty. Report the
exact count and list of cells on each side, and `|COVERED|` out of 6 as the
coverage fraction, stated in the same sentence as any aggregate reading.

### 2.6 THE FROZEN TERMINATION CLAUSE -- frozen before any cell is read

**Exactly one of the following three fires, in this precedence order.**

**T-HKZINDEP-NODATA** -- **FIRES WHEN EITHER (a)** `COVERED` is empty (no
cell of the 6 could be computed against within this task's budget -- section
3.2's could-not-complete guard), **OR (b)** the lead's own section 1
re-verification finds `fpylll` (and every equivalent library) genuinely
unavailable in its own session AND a from-scratch full HKZ implementation
(Branch B) is judged INFEASIBLE within this task's budget (not merely slow --
genuinely not completable as a correct HKZ-quality implementation within the
hard cap), so `ROUTE-I''` cannot be built by EITHER branch of section 2.2.
**MEANS:** this THIRD dedicated attempt at `hkz`'s independent-verification
question did not reach genuinely HKZ-quality independence, for a reason
OTHER than a simple, cheap coverage gap. **LICENSES:** recording this
PLAINLY, per `DEC-20260813-1aae44` section 11's own declared boundary, quoted
verbatim: *"that outcome should be recorded PLAINLY as a standing
infrastructure-limited open question for hkz specifically, rather than used
to justify a FOURTH iteration of the same measurement without a change in
available tooling."* Branch (a) (budget-exhaustion-only, `fpylll` still
untried or inconclusive) may be reported as ordinary infrastructure signal
without triggering the fourth-attempt boundary if a repeat at a larger
budget alone would plausibly resolve it; branch (b) (both routes genuinely
infeasible) triggers the fourth-attempt boundary explicitly. The report MUST
distinguish which of (a)/(b) fired, and why, rather than merging them.
**FORBIDS:** any claim about whether `BATCH-fbb639`'s `hkz` `EXCEEDS`
verdicts survive independent, quality-matched verification, in either
direction; closing, pausing or completing `GOAL-MLKEM-005`; commissioning a
FOURTH iteration of this exact measurement absent a change in available
tooling (per `DEC-20260813-1aae44` section 11's boundary, carried here
without alteration).

**T-HKZINDEP-ARTIFACT** -- **FIRES WHEN** `COVERED` is non-empty and
`SOME-ARTIFACT` holds. **MEANS**, quoted from `DEC-20260813-1aae44` section
11 verbatim: *"If it shows D_route' still growing toward s_c^fib's scale
even at matched HKZ fidelity, THAT is the genuine test PREREG-4 2.8's
revisit condition anticipated, and ITS consequent (flagging BATCH-fbb639's
hkz EXCEEDS verdicts methodologically unsupported) SHOULD fire at that
point, on that evidence -- not on this batch's confounded one."*
**LICENSES:** exactly and only that -- the flagged cell(s)' `EXCEEDS`
verdict FROM `BATCH-fbb639` must be recorded as methodologically unsupported
in a superseding record (discharging `PREREG-4` 2.8's revisit condition on
ITS OWN evidentiary terms this time, not on `BATCH-6e08fe`'s confounded
one), and no successor may cite that cell's `EXCEEDS` verdict without that
flag. **FORBIDS:** retroactively changing `T-C3LANE-OPEN-PARTIAL` or
`T-INDVERIFY-ARTIFACT-PARTIAL` themselves, which remain `BATCH-fbb639`'s and
`BATCH-6e08fe`'s own, correctly-read, frozen-clause outcomes (the flag
attaches to what the verdict can be READ TO SUPPORT, exactly as the
code-sharing qualification already did one level back -- it does not un-fire
either branch); any claim about `ML-KEM`, any FIPS 203 parameter set, any
attack cost or any cost model; closing, pausing or completing
`GOAL-MLKEM-005`.

**T-HKZINDEP-CONFIRMED** -- **FIRES WHEN** `COVERED` is non-empty and
`ALL-SURVIVE` holds. **MEANS**, quoted from `DEC-20260813-1aae44` section 11
verbatim: *"if the HKZ-quality ROUTE-I'' shows D_route' staying at or near
machine epsilon at the covered cells, that DISCHARGES hkz's status to
T-INDVERIFY-CONFIRMED-equivalent for those cells, exactly as lam1n's
discharged here, superseding the 'neither confirmed nor flagged' status this
decision leaves hkz in."* **LICENSES:** exactly that -- for the covered
cells only, `BATCH-fbb639`'s `hkz` `EXCEEDS` verdicts may be cited WITHOUT
EITHER `EV-MLKEM-965a37`'s F-1/RT-1 code-sharing qualification OR
`EV-MLKEM-5aa471`'s reduction-quality qualification -- the SAME discharge
`lam1n` already received in `BATCH-6e08fe`, extended to `hkz` on this
batch's own, quality-matched evidence. **FORBIDS:** extending that discharge
to any UNCOVERED cell (the qualification continues to apply there,
unchanged); any claim about `ML-KEM`, any FIPS 203 parameter set, any attack
cost or any cost model; closing, pausing or completing `GOAL-MLKEM-005`;
treating this as `A-1` held for `hkz` (unchanged from `PREREG-3` 3.5 and
`PREREG-4` 2.6 -- this measurement is a verification of a route, not a
statement about `A-1`).

**THE `-PARTIAL` SUFFIX**, applied to whichever of `T-HKZINDEP-ARTIFACT` /
`T-HKZINDEP-CONFIRMED` fires, **WHENEVER** `|COVERED| < 6`. Since this
document targets exactly the 6 already-covered cells and attempts no
previously-uncovered cell, a `-PARTIAL` suffix here would result ONLY from a
budget-exhaustion or per-basis-timeout shortfall within the 6 named cells
(section 3.2), never from a coverage question already settled by
`BATCH-6e08fe`. The suffixed branch reports the substantive reading over
`COVERED` **and** the coverage fraction **and** the list of not-computed
cells, none of which is decided in either direction.

**PRECEDENCE, STATED EXPLICITLY, UNCHANGED FROM `PREREG-4` 2.6.**
`T-HKZINDEP-NODATA` dominates (fires alone, no `-PARTIAL` suffix). Between
`T-HKZINDEP-ARTIFACT` and `T-HKZINDEP-CONFIRMED`, `SOME-ARTIFACT` takes
precedence over `ALL-SURVIVE` whenever both could otherwise be read from the
same data -- i.e. a single artifact-flagged cell is sufficient to fire
`T-HKZINDEP-ARTIFACT`, matching this campaign's established convention
(`PREREG-3` 3.5; `PREREG-4` 2.6) of resolving a single adverse cell toward
the more conservative, harder-to-argue-away branch. **A batch reporting
`SOME-ARTIFACT` at some cells and `ALL-SURVIVE`-consistent behavior at others
reports BOTH, per-cell** -- this document expects, but does not require, a
single uniform reading across all 6 `hkz` cells (unlike `BATCH-6e08fe`,
where `lam1n` and `hkz` genuinely diverged; here there is only one
candidate), and if the 6 cells split, the per-cell "reports BOTH" discipline
`PREREG-4` 2.6 established applies identically.

### 2.7 WHY THIS DOES NOT TRIGGER `PREREG-2` §7.5'S REPAIR BAR, AND IS NOT AN
###     EIGHTH THROUGH TENTH CONSECUTIVE GATE REPAIR -- RE-DERIVED FOR A
###     THIRD TIME, NOT MERELY CITED

`PREREG-2` 7.5 bars a further dispersion criterion, fibre clause or gate
repair in this goal unless six conditions hold, plus an absolute bar on an
eighth consecutive gate repair. `PREREG-3` 3.6 and `PREREG-4` 2.7 each
independently re-derived that their own measurements were not such repairs,
keeping the count at seven. `DEC-20260813-1aae44` section 4 extended that
re-derivation to `BATCH-6e08fe`'s own close, restating it explicitly rather
than only citing it, and noted the count remains SEVEN, unaffected by
`BATCH-fbb639`'s part (c) or `BATCH-6e08fe`'s part (b). Applying the
identical three-part test to THIS document's own measurement, for a third
time, independently:

1. **It specifies no criterion, clause or gate.** §2.4's comparison is
   `PREREG-3` §3.3's OWN formula, re-applied a second time (after
   `PREREG-4`'s first re-application) verbatim -- not a new rule, not a new
   threshold, and not an amendment to `A-1` or to any candidate's
   admissibility. §2.6's three branches license a recorded flag on a
   SPECIFIC PAST VERDICT (`T-HKZINDEP-ARTIFACT`) or a discharge of a
   SPECIFIC PAST QUALIFICATION (`T-HKZINDEP-CONFIRMED`) -- never a working
   assumption and never a gate.
2. **It re-verifies a measurement already made, on a route already
   attempted twice, rather than measuring a new class of object.**
   `BATCH-fbb639` and `BATCH-6e08fe` already ran two versions of this
   comparison for `hkz`; this document is a SECOND replication under a
   further-corrected (fidelity-matched) independence assumption, not a first
   look at a new candidate class. `PREREG-2` 7.5's repair bar governs
   criteria that decide FUTURE candidates; this document decides nothing
   about any future candidate.
3. **Its outcome is a verification result about `hkz`'s OWN prior
   measurement, not a repaired gate's pass/fail.** Even `T-HKZINDEP-CONFIRMED`,
   its most favourable branch, licenses only citing an EXISTING verdict
   without an EXISTING qualification -- it manufactures no new claim about
   any lattice, and it does not touch `A-1`, extend it, or replace it.

**THE SEVEN-CONSECUTIVE-INSTRUMENT-BATCH COUNT REMAINS SEVEN, NOT EIGHT,
NINE OR TEN**, for the identical structural reason `PREREG-3` 3.6,
`PREREG-4` 2.7 and `DEC-20260813-1aae44` section 4 each independently gave:
none of `BATCH-fbb639`'s part (c), `BATCH-6e08fe`'s part (b), or this
document's own measurement is a gate-repair attempt.

### 2.8 THE REVISIT CONDITION AND THE DECLARED BOUNDARY -- CARRIED VERBATIM
###     FROM `DEC-20260813-1aae44` SECTION 11, NOT RE-LITIGATED

Both of the following are quoted verbatim from `DEC-20260813-1aae44` section
11 and bind this document without amendment; section 2.6 above operationalizes
them as this document's own termination clause.

**THE REVISIT CONDITION:** *"if the HKZ-quality ROUTE-I'' shows D_route'
staying at or near machine epsilon at the covered cells, that DISCHARGES
hkz's status to T-INDVERIFY-CONFIRMED-equivalent for those cells, exactly as
lam1n's discharged here, superseding the 'neither confirmed nor flagged'
status this decision leaves hkz in. If it shows D_route' still growing
toward s_c^fib's scale even at matched HKZ fidelity, THAT is the genuine
test PREREG-4 2.8's revisit condition anticipated, and ITS consequent
(flagging BATCH-fbb639's hkz EXCEEDS verdicts methodologically unsupported)
SHOULD fire at that point, on that evidence -- not on this batch's confounded
one."*

**THE DECLARED BOUNDARY, BINDING A LATER SESSION INCLUDING A LATER ONE OF
THE COORDINATOR'S OWN:** *"This is the THIRD dedicated attempt at hkz's
independent-verification question (BATCH-fbb639's original code-shared
comparison; BATCH-6e08fe's LLL-quality re-implementation; this commissioned
HKZ-quality attempt). If this third attempt ALSO fails to reach genuinely
HKZ-quality independence -- fpylll still unavailable in every checked
environment AND a from-scratch full HKZ implementation judged infeasible
within a reasonable budget at d<=40 -- that outcome should be recorded
PLAINLY as a standing infrastructure-limited open question for hkz
specifically, rather than used to justify a FOURTH iteration of the same
measurement without a change in available tooling."* This boundary is
operationalized as `T-HKZINDEP-NODATA` branch (b) in section 2.6 above. **IF
THIS BOUNDARY FIRES, THE LEDGER ARCHIVE OF THIS BATCH MUST NOT COMMISSION A
FOURTH ATTEMPT** -- the next action in that case is recording the standing
open question and, if a future session judges available tooling has
genuinely changed (e.g. a DIFFERENT reduction library becomes available, or
budget policy changes to license a substantially larger from-scratch
implementation effort), a NEW Coordinator decision naming that changed
condition explicitly, not a routine successor batch.

### 2.9 Prediction register -- restated, not withheld this time

| id | statement | falsifier | class | open at notarization |
|---|---|---|---|---|
| P-V-a | `fpylll` (or an equivalent library) is available in the lead's own session, given the out-of-band confirmation in section 1 | `fpylll` and every alternative are confirmed unavailable in the lead's own re-verification | PREDICTION -- grounded in the section 1 infrastructure signal, explicitly NOT asserted as certain (environments differ across sessions of this harness) | OPEN |
| P-V-b | `COVERED` is non-empty (at least one of the 6 named cells produces a computed `D_route''` within budget) | `COVERED` is empty | PREDICTION -- these 6 cells already have confirmed `ROUTE-P` per-basis ground truth (BATCH-6e08fe's own obligation 0); the only failure mode is budget exhaustion or infrastructure, not missing data | OPEN |

**P-V-c (the direction -- `ALL-SURVIVE` vs `SOME-ARTIFACT`) IS DELIBERATELY
NOT STATED AS A PREDICTION, FOR THE IDENTICAL REASON `PREREG-4` 2.9 GAVE FOR
`P-IV-b`.** This measurement's entire purpose is to learn whether `hkz`'s
disagreement persists once BOTH code-sharing AND reduction-quality mismatch
are removed as confounds; `DEC-20260813-1aae44` and `EV-MLKEM-5aa471` both
record this as explicitly, genuinely OPEN. Stating a directional prediction
here would presuppose the answer this batch exists to find. Withholding it
is the more conservative, more honest choice.

---

## 3. GUARDS AND COULD-NOT-FAIL ARRANGEMENTS, NAMED BEFORE THE RUN

### 3.1 Could-not-fail check on the `D_route''` comparison

Would hold if `D_route''` were defined so large, or `s_c^fib` so small by
construction, that `"DOES NOT EXCEED"` (hence `T-HKZINDEP-ARTIFACT`) were
guaranteed regardless of measured values, or so tightly bound to zero that
`"EXCEEDS"` (hence `T-HKZINDEP-CONFIRMED`) were guaranteed instead. **WE ARE
IN NEITHER**, for the identical reason `PREREG-4` 3.1 gave: `D_route''` is a
**measured** max absolute deviation between two genuinely different code
paths (this time ALSO matched in reduction fidelity) on nominally identical
numeric inputs -- it is not fixed by construction in either direction.
`s_c^fib` at every cell this measurement reaches is an already-archived,
independently computed value from an unrelated computation (dispersion
across up to 8 fibre bases) -- there is no shared construction between it and
`D_route''` that forces the comparison's direction either way.

### 3.2 Could-not-complete guard -- an explicit budget-exhaustion outcome

Like `PREREG-4` part (b), this document requires genuinely NEW reduction
(bounded to `d <= 40`). **If this task's hard wall-clock cap (§ task card, §4
dispatch queue) is reached before every one of the 6 named cells has a
computed `D_route''`:** this is INFRASTRUCTURE SIGNAL (`AGENTS.md` rule 5),
reported as such, per-cell, distinguishing "NOT COMPUTED: budget exhausted"
from a genuinely computed value -- **never** silently merged, and **never**
read as either `VERDICT''` by default. A budget-exhaustion outcome at every
attempted cell fires `T-HKZINDEP-NODATA` branch (a) if it leaves `COVERED`
(as actually computed) empty; a partial completion is reported with the
`-PARTIAL` suffix and the exact list of not-computed cells named separately.

### 3.3 The section-1 re-verification guard, new to this document

If the lead's own `fpylll` re-verification (section 1) fails, Branch B
(section 2.2) is attempted within the SAME overall task budget, not a fresh
one. If Branch B is ALSO judged infeasible (not merely slow -- a from-scratch
correct HKZ implementation is not achievable within the remaining budget),
this fires `T-HKZINDEP-NODATA` branch (b), triggering the declared boundary
of section 2.8. The lead's report must state explicitly, and with reasoning,
why Branch B was judged infeasible rather than merely slow, if that
determination is made -- "infeasible" is a stronger claim than "did not
finish in time" and the two are not to be conflated.

---

## 4. OUTCOME ROWS

| row | what it records |
|---|---|
| `R-V-OUT-0` | section 1's infrastructure re-verification: `fpylll` (or equivalent) available or not, in the lead's own session, and which branch (A/B) was consequently taken |
| `R-V-OUT-1` | section 2.3's sanity confirmation that genuine `ROUTE-P` per-basis ground truth exists at the 6 named cells, and the exact basis count per cell |
| `R-V-OUT-2` | obligation 1 (§2.4): per covered cell, the declared implementation branch (§2.2), `s_c^fib`, `D_route''`, matched-basis count, `VERDICT''`, and reading relative to `BATCH-fbb639`'s original `EXCEEDS` |
| `R-V-OUT-3` | obligation 2 (§2.5): `ALL-SURVIVE` / `SOME-ARTIFACT`, coverage fraction, cell lists |
| `R-V-OUT-4` | the termination branch read off `R-V-OUT-1`/`R-V-OUT-3` under §2.6's frozen precedence, with the `-PARTIAL` suffix applied per its own rule, and, if `T-HKZINDEP-ARTIFACT` fired at any cell, that cell named explicitly for the revisit condition (§2.8), OR, if `T-HKZINDEP-NODATA` branch (b) fired, the declared boundary (§2.8) stated explicitly |

---

## 5. BINDING CARRIES -- IN FORCE, NOT RE-LITIGATED

Carried in full from `PREREG-2` §§10/10.1, `PREREG-3` §7 and `PREREG-4` §5,
without restatement of every line here -- the lead, the reviews and the
ledger archive are bound exactly as those documents state, plus the
following, specific to this batch:

* **CLAIM TIER TOY, UNCONDITIONALLY.**
* **`AM-3` IS NOT RETIRED.** `AM-10` through `AM-18` and their carries are in
  force. `BATCH-a44d08`, `BATCH-4ed139`, `BATCH-9e3584`, `BATCH-cbe023`,
  `BATCH-6b6e78`, `BATCH-fbb639` and `BATCH-6e08fe` are NOT RESCORED OR
  REVALIDATED in any respect by anything in this document.
* **NEITHER SUB-6x COUNT IS CITABLE.** "A factor of 6 to 31" is FALSE; the
  citable range is 4.87x to 31.03x. "Genuinely cross-platform" is NOT
  citable; the citable form is a PORTABILITY result across three textually
  distinct implementations with `fpylll` pinned at 0.6.4 (where applicable).
* `AM4-OBS-1` cited ONLY through `KN-FIND-f38a89`. `AM-9`: `fpylll`'s `k`
  counts the q-scaled rows, NOT the identity block. THE `G-VAR` REFUSAL IS
  CITED ONLY AS CONDITIONAL ON THE FROZEN FAMILY `F0`.
* **`KN-FIND-7d098b`, `KN-FIND-9d44b4`, `KN-FIND-9b5df0` AND `KN-FIND-7de6b6`
  ARE PROMOTED -- NOT RESTATED AS NEW** anywhere in this document.
  `KN-FIND-7de6b6`'s own content (the fidelity-matching precondition this
  batch's own measurement operationally answers) is cited, not repeated.
* `T-C3LANE-OPEN-PARTIAL` (`BATCH-fbb639`) and `T-INDVERIFY-ARTIFACT-PARTIAL`
  (`BATCH-6e08fe`) ARE NOT REOPENED, RE-SCORED OR REVERSED by anything in
  this document; §2.6/§2.8 state precisely and only what this batch's own
  outcome can attach to either.
* `lam1n`'s `T-INDVERIFY-CONFIRMED` discharge (`BATCH-6e08fe`) IS NOT
  REOPENED, RE-SCORED OR REVISITED by anything in this document. `lam1n` is
  out of scope (section 0).
* The split-producer notarization pattern is retained unchanged. The
  receipt-with-`commit_sha: null`-inside-its-own-commit archive pattern is
  MANDATORY. Every run emits durable `command.txt`, `stdout.log` and
  `stderr.log`, with no path inside a folded YAML scalar, and lists every
  path it wrote in its report.
* `knowledge/INDEX.md` must NOT be written, regenerated or staged.
* **`AGENTS.md` rule 12 is UNMET AND UNWAIVED.** Every producer and reviewer
  of this batch records `model_verified: false` with its reason, its host
  and its stack. THIS BINDS THIS BATCH'S OWN REVIEWS EXACTLY AS MUCH AS IT
  BINDS THE PRODUCER, restated here because `DEC-20260813-1aae44` names this
  irony explicitly for `BATCH-6e08fe` and it does not lapse at the batch
  boundary.
* **`PD-4` remains OPEN.** Each review's own report and probes sit
  uncommitted across a dispatch window and are the sole carriers of their
  own evidence until the ledger archive commits them.
* **A SEPARATE CONCURRENT-WORKTREE COLLISION WAS RECORDED, NOT SILENTLY
  WORKED AROUND, IN `DEC-20260813-1aae44` LIMITATIONS** (`BATCH-7033ee`,
  cancelled). This document does not touch `BATCH-7033ee`'s immutable,
  cancelled artifacts and does not reuse or remap any of its identifiers.

---

## 6. SCOPE, INDEPENDENCE AND WHAT THIS BATCH CANNOT DO

**SCOPE.** `q = 3329`; `d in {20, 30, 40}` (`L7`, `L9`, `L11` ONLY); `hkz`
ONLY (`lam1n` explicitly out of scope, section 0; `rawtail` out of scope,
section 2.1); exactly the 6 named cells (`L7_b5`, `L7_b15`, `L9_b7`,
`L9_b22`, `L11_b10`, `L11_b30`); up to `N_BASES = 8` per cell, narrower where
`ROUTE-P`'s own per-basis ground truth or this task's own per-basis
enumeration/reduction completion is narrower; `binary64` only. **NO
REDUCTION ABOVE `d = 40`, ANYWHERE, FOR ANY REASON.**

**THIS BATCH'S OWN SCOPE, CARRIED AT EVERY QUOTATION.** This measurement
says nothing about `A-1`, about the in-scope candidates of `PREREG-2` 2.4,
about `X_gso_k`, or about any determinant-only candidate. It says nothing
about `ML-KEM`, any FIPS 203 parameter set, any attack cost, or any cost
model. Its most favourable branch (`T-HKZINDEP-CONFIRMED`) licenses citing
an EXISTING verdict without an EXISTING qualification, for the 6 cells
checked -- nothing stronger, and nothing about any UNCOVERED (middle-beta)
cell.

**INDEPENDENCE IS PROCEDURAL AND NEVER MODEL-LEVEL.** `AGENTS.md` rule 12 is
UNMET AND UNWAIVED in this goal and is not waived here -- see §5's explicit
note that this binds this batch's own reviews too.

**THE THIRD-ATTEMPT BOUNDARY, RESTATED ONE FINAL TIME SO IT IS NOT MISSED.**
If `T-HKZINDEP-NODATA` branch (b) fires, this batch's own close records a
standing infrastructure-limited open question for `hkz` and does NOT
commission a fourth iteration of this exact measurement absent a change in
available tooling, per `DEC-20260813-1aae44` section 11.

---

## 7. AUTHORSHIP GAP, DECLARED RATHER THAN NARRATED CLOSED

The Coordinator session that wrote this file **held no shell**. It ran no
git command and computed no hash. It DID read committed repository files
directly with a read-only tool (never a shell), and every number attributed
to "this Coordinator" above (the 6-cell coverage carried from
`results_route_reimpl.json`/`EV-MLKEM-5aa471`, the `s_c^fib` path
resolution, `ROUTE-P`'s own three-part algorithm structure as independently
confirmed by `VAL-20260813-71d65d` OR-1) was read that way from the exact
cited path, not computed, not estimated, and not carried from any prose
summary beyond direct quotation. **This is a weaker claim than a
measurement**: it is one session's reading of committed files at one point
in time, offered so the lead can check it independently, not offered as this
batch's evidence. The lead producer's own section 1 re-verification and
section 2.3 sanity check are the batch's actual, attributed infrastructure
and coverage confirmations.

**THE `fpylll`/`cysignals` INSTALLATION AND FUNCTIONAL-CHECK RESULT RECORDED
IN SECTION 1 WAS PERFORMED BY THE DISPATCHING SESSION, WHICH DOES HOLD A
SHELL, OUTSIDE THIS COORDINATOR SESSION'S OWN AUTHORING OF THIS TEXT.** It is
recorded here as infrastructure signal reported to this Coordinator, not
independently verified by this Coordinator's own (shell-less) session, and
the lead is instructed to re-verify it regardless, per section 1.

`prereg_sha256.txt` is generated and committed by `TASK-20260813-d63082`, by
a session that has a shell, exactly as every prior `PREREG-*` of this goal
required for its own hash file.

**END OF FROZEN TEXT.**
