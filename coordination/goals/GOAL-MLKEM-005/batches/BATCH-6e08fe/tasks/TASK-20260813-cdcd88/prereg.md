# PREREG-4 — BATCH-6e08fe FROZEN PRE-REGISTRATION

    goal        GOAL-MLKEM-005
    batch       BATCH-6e08fe
    task        TASK-20260813-cdcd88 (Coordinator, pre-registration only)
    notarized by TASK-20260813-e24ad9 (snapshot archive, runs alone, before any
                measuring task)
    authority   DEC-20260813-28d7b2 (the closing decision of BATCH-fbb639,
                whose `next_actions` field this document discharges in full),
                the corrected `ledger/goals/GOAL-MLKEM-005.yaml` `next_action`
                field (superseding a stale value by proper supersession,
                commit `442159165`), and KN-FIND-9b5df0
    claim tier  TOY, UNCONDITIONALLY

**THIS TEXT IS FROZEN AT NOTARIZATION AND IS NEVER EDITED.** A correction is a
superseding record under a new identifier, never an edit here. No measuring
task of `BATCH-6e08fe` may be dispatched until this file is committed by
`TASK-20260813-e24ad9` and that commit contains **zero** producer artifacts.
That is the split-producer notarization pattern, retained unchanged; it has
now worked seven times and has been verified in both directions by
independent sessions each time.

---

## 0. WHAT THIS BATCH DISCHARGES, AND WHY ITS PARTS TRAVEL TOGETHER

`DEC-20260813-28d7b2` closed `BATCH-fbb639` (`T-C3LANE-OPEN-PARTIAL`,
Validator verdict `incomplete`) and set **exactly one** `next_action`, in two
parts that must travel together in this successor pre-registration, per that
decision's own text (and the identical text now carried, correctly, in
`ledger/goals/GOAL-MLKEM-005.yaml` `research_goal.next_action`):

* **(a) DISCHARGE RT-2** — a superseding record correcting `R-C-OUT-0`'s
  coverage table for the 4 cells the Red Team named: `hkz/L9_b15` and
  `hkz/L11_b20` restated as genuinely **UNCOVERED**, and `hkz/L9_b22` /
  `hkz/L11_b30` restated with the corrected TRUE `beta_hi`-based `D_route`
  source, numerically unchanged at `0.0`. **NO NEW COMPUTATION** — both
  corrected values are already computed in the Red Team's own committed probe
  (`probe_coverage_beta_mismatch.py` / `_output.json`), carried verbatim.
* **(b) THE LEAD MEASUREMENT** — a genuinely non-code-shared
  re-implementation of `ROUTE-I` for `lam1n` and `hkz` at `L7` (`d=20`), `L9`
  (`d=30`) and `L11` (`d=40`), re-running `PREREG-3` §3.3's exact `D_route`
  comparison against the SAME already-archived `ROUTE-P` values
  (`results_relvar.json`), at the SAME frozen lattices, betas and
  `N_BASES = 8` fibre family, with **no new reduction above `d = 40`**.

**(a) IS BOOKKEEPING AND IS FROZEN HERE AS A MECHANICAL CORRECTION.** It
requires no re-run and no judgement by the lead beyond carrying the frozen
text below into its own report verbatim, attributed to this document. **(b) is
the substantive measurement of this batch** and its termination clause is
frozen in full in §2.6 before any cell is read.

**WHY THE TWO TRAVEL TOGETHER.** `DEC-20260813-28d7b2`'s rationale states:
(i) deferring (a) risks a successor citing the uncorrected `18/27` figure or
the two mislabelled-source cells, and `PREREG-3` 3.2 itself designates
`R-C-OUT-0` a first-class deliverable; (ii) (b) is the ONE thing that would
let a future batch cite this goal's `EXCEEDS` verdicts without the central
finding's (F-1/RT-1) qualification — both reviews of `BATCH-fbb639`
independently named it as the decisive, not-yet-run follow-up; (iii) doing
only (a) would leave the goal's actual blocking uncertainty about C3's
candidate observables — whether their measured fibre content is a real
signal or an artifact of this corpus's universal code-sharing — untouched,
which the Red Team's own corpus-wide search (no non-target candidate with
genuine, non-algebraically-forced dispersion exists anywhere in this corpus)
shows cannot be resolved any other way inside the existing corpus.

---

## 1. PART (a) — RC-3: THE COVERAGE-TABLE CORRECTION, FROZEN AND MECHANICAL

**READING ADOPTED.** This document adopts the Red Team's own already-computed
correction, RT-2 of `EV-MLKEM-965a37`, sourced directly from
`coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/reviews/TASK-20260813-6ab893/probes/probe_coverage_beta_mismatch.py`
and its committed `_output.json` (both committed at
`coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/archives/TASK-20260813-e5254a/`,
per that archive's `path_sha256` block). This correction is hereafter labelled
**RC-3** (the third recorded correction in this goal's `RC-*` lineage, after
`BATCH-fbb639`'s RC-1 and RC-2).

**FROZEN CORRECTION TEXT, TO BE CARRIED VERBATIM INTO THE LEAD'S REPORT:**

> `BATCH-fbb639`'s coverage table (`R-C-OUT-0` of `results_c3lane.json`) falsely
> marks `hkz/L9_b15` and `hkz/L11_b20` as `COVERED` (`route_i_available: true`).
> `results_am4.json`'s `gates.hkz.G_REL1.all` block reports `hkz` only at the two
> `REL1_PAIR` endpoint betas per lattice (`L9`: 7 and 22; `L11`: 10 and 30) —
> **never** the middle beta either lattice's 3-point grid uses (`L9`: 15;
> `L11`: 20), and `measure_c3lane.py` never reads `X_hi`. **`hkz/L9_b15` and
> `hkz/L11_b20` are restated as UNCOVERED**, not `COVERED`. Two further cells,
> `hkz/L9_b22` and `hkz/L11_b30`, cite the WRONG beta's value as their
> `D_route` source (the beta_lo comparison was reused instead of the true
> beta_hi comparison). **`hkz/L9_b22` and `hkz/L11_b30` are restated with the
> corrected TRUE `beta_hi`-based `D_route` source** — `am4_X_hi` compared
> against `relvar`'s own `G_REL1` `X_b` at basis 0 — **numerically UNCHANGED at
> exactly `0.0`** for both cells (`probe_coverage_beta_mismatch_output.json`,
> `per_cell_beta_coverage_audit["hkz/L9_b22"].TRUE_beta_hi_comparison` and
> `["hkz/L11_b30"].TRUE_beta_hi_comparison`, `true_abs_deviation: 0.0` in both).
> `lam1n`'s equivalent beta reuse is verified LEGITIMATE and is explicitly
> excluded from this correction: `lam1n`'s `X_lo == X_hi` exactly at both
> lattices, so any beta's comparison genuinely is "the" comparison for it.
> **GENUINE COVERAGE NARROWS FROM 18 TO 16 OF 27**: `lam1n` 9/9 unaffected,
> `hkz` 7/9 genuinely covered (`L7` all 3: `b5`/`b10`/`b15`; `L9`: `b7`/`b22`;
> `L11`: `b10`/`b30`). **THIS SUPERSEDES THE `18/27` COVERAGE FRACTION** and
> the per-cell source attribution for these 4 named cells wherever either is
> quoted without this correction in the same sentence.

**WHAT IS UNCHANGED, restated so it is not lost in the correction.** Both
reviews of `BATCH-fbb639` independently confirmed this narrowing does **not**
change the fired termination branch: all 16 genuinely-covered cells still
verdict `EXCEEDS`, `SOME-EXCEEDS` still holds, and `T-C3LANE-OPEN-PARTIAL`
remains the branch that fired — the `-PARTIAL` suffix was already applied
(`18 < 27`) and remains applicable at `16 < 27`. **This correction does not
reopen, reduce or extend `T-C3LANE-OPEN-PARTIAL`'s license** (§2 of
`DEC-20260813-28d7b2`; unchanged here).

**NO RE-RUN IS REQUIRED, AND NONE IS PERMITTED HERE.** `measure_c3lane.py`,
`results_c3lane.json` and `report_c3lane.md` are **immutable committed
artifacts** (`TASK-20260813-7ac7cd`,
`391f811e7b6b23fb40235a0608aebeb05b5b9c4a`) and are **not edited, not re-run,
and not vendored**. The Red Team's probe files are likewise immutable,
committed at `TASK-20260813-e5254a`
(`a2148c6035420e609f576fdaaac3f8d819dbe277`). The lead producer of this batch
carries the frozen text above into its own report **by quotation**, attributed
to `PREREG-4` §1, and does **not** recompute anything.

---

## 2. PART (b) — THE LEAD MEASUREMENT: A GENUINELY NON-CODE-SHARED SECOND ROUTE

### 2.0 What is being asked, restated precisely

`BATCH-fbb639`'s central finding (F-1 Validator / RT-1 Red Team, convergent,
`EV-MLKEM-965a37`) showed that `PREREG-3`'s named "`ROUTE-I`" — `results_l7l8.json`
(`L7`) and `results_am4.json` (`L9`/`L11`) — shares its core numerical kernel
(`make_A`, `build_basis`, `hkz_profile`) **verbatim** with `ROUTE-P`
(`results_relvar.json`) across the chain `measure_am4.py` →
`measure_relvar.py` → `replicate_l7l8.py`, and for `L7` the two "routes"
additionally ran on the **same host**. `D_route = 0.0` at all 18 (now 16,
per RC-3) covered cells is therefore explained by SAME-CODE, CROSS-ENVIRONMENT
REPRODUCIBILITY, not by independent-algorithm cross-validation. Whether the
`EXCEEDS` verdicts of `BATCH-fbb639` would still fire under **genuine**
algorithmic independence was left explicitly OPEN by both reviews and by
`EV-MLKEM-965a37`.

Part (b) answers that question, and **only** that question: does a genuinely
non-code-shared, independently implemented second route, run against the SAME
frozen `ROUTE-P` values this goal has always used, still show
`s_c^fib > D_route` at the cells it can reach? This is **not** a new
dispersion criterion, **not** a gate, and **not** a re-litigation of
`T-C3LANE-OPEN-PARTIAL` (§2.7 states why in full — carried, not new,
verification of a specific, already-fired measurement's second route).

### 2.1 Frozen objects — carried, not re-declared

    q          = 3329                          (carried, PREREG-1 2.1)
    N_BASES    = 8 (basis index i = 0..7)      (carried, PREREG-3 3.1)
    Lattices in scope for this batch, and ONLY these three, exactly as
    PREREG-3 3.1 declared them:
        L7  (d=20, k=6)    beta grid {5, 10, 15}
        L9  (d=30, k=9)    beta grid {7, 15, 22}
        L11 (d=40, k=12)   beta grid {10, 20, 30}
    Candidates: lam1n, hkz ONLY. (rawtail is OUT OF SCOPE for part (b): no
    ROUTE-I of any kind — code-shared or otherwise — exists for it anywhere
    in the committed corpus, per BATCH-fbb639's own obligation-0 search and
    both of its reviews; this document does not ask the lead to build one.)

    ROUTE-P  ("primary / committed pipeline route") — UNCHANGED FROM PREREG-3.
             The value of candidate X at lattice L, beta b, basis i as computed
             by the FROZEN, ALREADY-COMMITTED measure_relvar.py pipeline of
             BATCH-9e3584, committed at
             coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/
             TASK-20260809-cda2f6/results_relvar.json.
             THIS IS AN ALREADY-ARCHIVED VALUE. It is READ, never
             recomputed, never re-derived, and NEVER re-run.

    ROUTE-P's ONLY VALID SOURCE FOR PART (b): results_relvar.json's OWN
             G_REL1.<candidate>.<lattice>.per_basis array (fields X_a at
             beta_lo, X_b at beta_hi, 8 entries, one per basis index 0..7).
             results_l7l8.json and results_am4.json ARE EXPLICITLY EXCLUDED
             AS A SOURCE OF ROUTE-P VALUES FOR THIS MEASUREMENT, even where
             they report their own internal comparison against
             results_relvar.json: both are ROUTE-I-family artifacts under
             F-1/RT-1's finding (replicate_l7l8.py CARRIES VERBATIM the
             kernel measure_am4.py and measure_relvar.py share), so any
             "route disagreement" figure computed INSIDE them inherits the
             same code-sharing this measurement exists to route around. Using
             either as ROUTE-P here would reproduce exactly the defect this
             batch corrects for. This is stated explicitly because
             PREREG-3's own obligation_0_l7l8() used results_l7l8.json's
             OWN internal comparison for L7's D_route — a choice that was
             legitimate for PREREG-3's question (does the corpus's existing
             pipeline disagree with itself across a route split) but is NOT
             legitimate for part (b)'s question (does a genuinely
             independent computation disagree with ROUTE-P).

    ROUTE-I' ("genuinely independent re-implementation route") — THE OBJECT
             THIS TASK BUILDS. Defined operationally in §2.2. Computed by
             the lead, once, for every (candidate, lattice, beta, basis)
             cell obligation 0 (§2.3) finds ROUTE-P per-basis data for.
             NEVER READ FROM ANY COMMITTED FILE — this is the one genuinely
             new computation in this batch.

    Fibre dispersion at binary64, s_c^fib(X, L, b):
             the ALREADY-ARCHIVED float_sd value at
             results_relvar.json.per_candidate.<X>.per_cell.<L>_<b>.float_sd
             — UNCHANGED FROM PREREG-3 3.1. READ, never recomputed.

**WHY THE COVERAGE OF PART (b) IS EXPECTED TO BE NARROWER THAN PREREG-3's 27
CELLS, STATED IN ADVANCE.** `results_relvar.json`'s `G_REL1` block, this
Coordinator's own read (weaker than a measurement — see §2.9), reports
per-basis data ONLY at each lattice's two `REL1_PAIR` endpoint betas
(`beta_lo`, `beta_hi`), never at the middle beta of any of the three lattices'
own 3-point grids — the SAME structural gap RC-3 (§1) just corrected for
`ROUTE-I`'s own coverage table now appears, independently, on `ROUTE-P`'s
side: `results_relvar.json` itself has no per-basis ground truth at `L7 b10`,
`L9 b15` or `L11 b20` for either candidate. **THE LEAD MUST VERIFY THIS BY ITS
OWN OBLIGATION-0 READ (§2.3) RATHER THAN TAKE THIS PARAGRAPH AS FINAL** —
exactly as `PREREG-3` 3.1 required of its own coverage expectations. If the
lead's own read finds per-basis data this Coordinator's search missed, it is
used; if it confirms this Coordinator's expectation, the middle-beta cells of
each lattice are reported `UNCOVERED` for part (b), never defaulted to
either verdict.

### 2.2 What "genuinely non-code-shared" means, operationally — THIS IS A CHECKABLE CLAIM, NOT AN ASSERTION

A `ROUTE-I'` implementation satisfies this document's independence
requirement if and only if **all** of the following hold, and the lead's
report states, explicitly and BEFORE any `D_route'` number is computed, which
choice it made and why:

1. **No transcription of the shared kernel.** The code that (a) turns the
   frozen instance matrix `A` into a basis object ready for reduction, and
   (b) performs the reduction/enumeration and extracts `lam1n`/`hkz`, is NOT
   copied, adapted, wrapped, or structurally paraphrased from `make_A`,
   `build_basis` or `hkz_profile` as they appear in `measure_am4.py`,
   `measure_relvar.py`, `replicate_l7l8.py`, or ANY descendant that carries
   them (this explicitly includes `BATCH-4ed139`'s P-L1 rider
   `replicate_l7l8.py`, which the central finding shows IS such a
   descendant, and which is therefore NOT a valid model for `ROUTE-I'`
   either, even though `PREREG-3` treated it as `ROUTE-I` for `L7`).
2. **A genuinely different implementation choice for the reduction/enumeration
   step** — the step `hkz_profile` performs. Any ONE of the following
   satisfies this, and the lead names which:
   (i) a different lattice-reduction library entirely (e.g. any independently
   maintained lattice-reduction package other than the campaign's own
   wrapper code, if one is available in the run environment without a new
   install exceeding this task's budget);
   (ii) `fpylll`'s OWN public reduction API called directly
   (`fpylll.LLL.reduction`, `fpylll.BKZ.reduction`/`fpylll.BKZ.Param`, or
   `fpylll.IntegerMatrix`/`fpylll.GSO.Mat` used directly) — i.e. `fpylll` the
   library MAY be used (every route in this corpus, including `ROUTE-P`,
   depends on a lattice-reduction library, and using the same underlying
   library is not what F-1/RT-1 criticized), but the campaign's own
   hand-written wrapper functions may not be called, imported, or have their
   internal call sequence reproduced;
   (iii) a from-scratch HKZ/enumeration routine in pure Python/numpy, written
   without consulting the three named functions' source, feasible at this
   task's small scale (`d <= 40`).
3. **The frozen instance itself may be reconstructed from its own published
   formula.** Building the SAME numeric matrix `A` from the declared,
   already-public seed formula (`default_rng([1, d, k, i]).integers(0, q,
   (k, d-k))`) is NOT code-sharing in the sense F-1/RT-1 criticized —
   producing an identical, publicly-declared deterministic input from its own
   formula, independently, is legitimate and is what every route in this
   corpus (including `ROUTE-P`) already does; comparing two INDEPENDENTLY
   built instances that happen to be numerically identical by construction is
   exactly what this comparison is FOR. What must be independent is the CODE
   PATH that turns that instance into a reduced basis and extracts the
   observable, not the numeric input.
4. **The choice is declared and justified in the report, prominently, BEFORE
   the `D_route'` table is presented** — naming the exact library/routine
   used and stating explicitly that it does not derive from the named
   lineage, so a reviewer can check the claim against the actual committed
   script rather than trust the prose.

**THIS BOUNDARY DOES NOT ITSELF SPECIFY A NEW DISPERSION CRITERION, GATE OR
THRESHOLD** — it specifies what counts as a valid `ROUTE-I'` SOURCE for this
one measurement, exactly as `PREREG-3` 3.2's construction-comparability check
specified what counted as a valid `ROUTE-I` source for that measurement.

### 2.3 Obligation 0 — coverage audit, BEFORE any new reduction is run

**THE LEAD'S FIRST ACT**, before writing or running any reduction code: read
(not recompute) `results_relvar.json`'s `G_REL1` block for `lam1n` and `hkz`
at `L7`, `L9`, `L11`, and report, per (candidate, lattice), the `beta_lo` and
`beta_hi` values it declares, whether either coincides with the lattice's own
middle beta (it will not, per §2.1's stated expectation, but VERIFY rather
than assume), and the number of per-basis entries available (expected 8,
VERIFY rather than assume). **THE OUTPUT IS A COVERAGE TABLE**: for each of
the 18 cells (2 candidates × 3 lattices × 3 betas), whether genuine
`ROUTE-P` per-basis ground truth exists, at how many bases, and its exact
path (`results_relvar.json` only — §2.1). **A cell with no genuine
`ROUTE-P` per-basis ground truth is `UNCOVERED` for part (b), full stop, and
is NEVER computed against by `ROUTE-I'` regardless of whether a new reduction
at that cell would be cheap** — there is nothing to compare it against.
**THIS TABLE IS A FIRST-CLASS DELIVERABLE**, exactly as `PREREG-3` 3.2's
`R-C-OUT-0` was. A run that computes `D_route'` without first producing and
reporting this table has not discharged obligation 0.

### 2.4 Obligation 1 — the independent computation and the D_route' comparison, per covered cell

For every cell obligation 0 finds covered, and ONLY for those cells, the lead:

1. Builds its own `ROUTE-I'` value of the candidate at that (lattice, beta,
   basis), for every matched basis (up to 8, matching whatever `ROUTE-P`'s
   own per-basis array provides at that cell — report the exact subset size
   used), using the implementation choice declared and justified per §2.2.
2. Computes, **using PREREG-3 §3.3's own, already-frozen formula, verbatim,
   applied to this route pair**:

       D_route'(X, L, b) = max over the matched bases i of
                            | X_ROUTE-P(L, b, i) - X_ROUTE-I'(L, b, i) |

       VERDICT'(X, L, b) = "EXCEEDS"          if  s_c^fib(X, L, b) >  D_route'(X, L, b)
                          = "DOES NOT EXCEED" if  s_c^fib(X, L, b) <= D_route'(X, L, b)

   **Ties resolve to `"DOES NOT EXCEED"`**, exactly as `PREREG-3` 3.3 states —
   the same conservative direction, unchanged. **THIS IS NOT A NEW
   COMPARISON RULE.** It is `PREREG-3` §3.3's own rule, re-applied to a
   `D_route` that is now, for the first time in this goal, computed from a
   genuinely independent second route rather than a code-shared one. Reusing
   it rather than inventing a new threshold is deliberate (§2.7).
3. Reports, per cell: `s_c^fib`, `D_route'`, the number of matched bases, the
   implementation choice used (§2.2), `VERDICT'`, and — because
   `BATCH-fbb639`'s own `EXCEEDS` verdict exists at every one of these cells
   already (per RC-3's corrected coverage, §1) — **whether `VERDICT'` agrees
   with `BATCH-fbb639`'s original `EXCEEDS`** (`VERDICT' = EXCEEDS`: the
   original verdict SURVIVES independent verification at this cell;
   `VERDICT' = DOES NOT EXCEED`: the original verdict is FLAGGED
   methodologically unsupported at this cell — §2.6/§2.8).

### 2.5 Obligation 2 — the aggregate reading

Let `COVERED` = the set of cells obligation 0 found genuine `ROUTE-P`
per-basis ground truth for (up to 18; expected narrower per §2.1).

    ALL-SURVIVE  :  VERDICT'(X, L, b) = "EXCEEDS" for EVERY cell in COVERED
    SOME-ARTIFACT:  VERDICT'(X, L, b) = "DOES NOT EXCEED" for AT LEAST ONE cell in COVERED

Mutually exclusive, exhaustive of `COVERED` whenever non-empty. Report the
exact count and list of cells on each side, and `|COVERED|` out of 18 as the
coverage fraction, stated in the same sentence as any aggregate reading.

### 2.6 THE FROZEN TERMINATION CLAUSE FOR PART (b) — frozen before any cell is read

**Exactly one of the following three fires, in this precedence order.**

**T-INDVERIFY-NODATA** — **FIRES WHEN** `COVERED` is empty (no cell of the 18
has genuine `ROUTE-P` per-basis ground truth, or none could be computed
against within this task's budget — see §4's could-not-complete guard).
**MEANS:** part (b)'s question cannot be answered this batch. **LICENSES:** a
decision recording this as an infrastructure/corpus gap — never a scientific
result in either direction. **FORBIDS:** any claim about whether
`BATCH-fbb639`'s `EXCEEDS` verdicts survive independent verification, in
either direction; closing, pausing or completing `GOAL-MLKEM-005`.

**T-INDVERIFY-ARTIFACT** — **FIRES WHEN** `COVERED` is non-empty and
`SOME-ARTIFACT` holds. **MEANS**, quoted from `DEC-20260813-28d7b2`'s
`next_actions` verbatim: *"if D_route grows toward s_c^fib's scale, the
EXCEEDS verdicts reported in \[BATCH-fbb639\] were a methodological artifact
of code-sharing, not a finding about lam1n/hkz, and that must be recorded as
such rather than argued away."* **LICENSES:** exactly and only, per the
revisit condition `DEC-20260813-28d7b2`/the goal record's `next_action`
declared in advance: **the flagged cell(s)'** `EXCEEDS` verdict FROM
`BATCH-fbb639` must be recorded as methodologically unsupported in a
superseding record, and no successor may cite that cell's `EXCEEDS` verdict
without that flag. **FORBIDS:** retroactively changing
`T-C3LANE-OPEN-PARTIAL` itself, which remains `BATCH-fbb639`'s own,
correctly-read, frozen-clause outcome (the flag attaches to what the verdict
can be READ TO SUPPORT, exactly as F-1/RT-1 already did for the code-sharing
qualification — it does not un-fire the branch); any claim about `ML-KEM`,
any FIPS 203 parameter set, any attack cost or any cost model; closing,
pausing or completing `GOAL-MLKEM-005`.

**T-INDVERIFY-CONFIRMED** — **FIRES WHEN** `COVERED` is non-empty and
`ALL-SURVIVE` holds. **MEANS**, quoted from `DEC-20260813-28d7b2`'s
`next_actions` verbatim: *"if D_route stays at or near machine epsilon under
genuine algorithmic independence, that is real, citable evidence the
observables are numerically well-behaved and the EXCEEDS verdicts of
\[BATCH-fbb639\] survive independent verification, discharging \[that\]
batch's central-finding qualification for the cells checked."* **LICENSES:**
exactly that — for the covered cells only, `BATCH-fbb639`'s `EXCEEDS`
verdicts may be cited WITHOUT F-1/RT-1's "not under independent verification"
qualification. **FORBIDS:** extending that discharge to any UNCOVERED cell
(the qualification continues to apply there, unchanged); any claim about
`ML-KEM`, any FIPS 203 parameter set, any attack cost or any cost model;
closing, pausing or completing `GOAL-MLKEM-005`; treating this as `A-1` held
for `lam1n`/`hkz` (unchanged from `PREREG-3` 3.5 — this measurement is a
verification of a route, not a statement about `A-1`).

**THE `-PARTIAL` SUFFIX**, applied to whichever of `T-INDVERIFY-ARTIFACT` /
`T-INDVERIFY-CONFIRMED` fires, **WHENEVER** `|COVERED| < 18` — expected,
per §2.1's stated expectation that the three middle-beta cells (`L7 b10`,
`L9 b15`, `L11 b20`) lack genuine `ROUTE-P` per-basis ground truth regardless
of what `ROUTE-I'` computes. The suffixed branch reports the substantive
reading over `COVERED` **and** the coverage fraction **and** the list of
uncovered cells, none of which is decided in either direction. A missing
`ROUTE-P` ground truth is never read as either `VERDICT'` by default.

**PRECEDENCE, STATED EXPLICITLY.** `T-INDVERIFY-NODATA` dominates (fires
alone, no `-PARTIAL` suffix). Between `T-INDVERIFY-ARTIFACT` and
`T-INDVERIFY-CONFIRMED`, `SOME-ARTIFACT` takes precedence over `ALL-SURVIVE`
whenever both could otherwise be read from the same data — i.e. a single
artifact-flagged cell is sufficient to fire `T-INDVERIFY-ARTIFACT`, matching
this campaign's established convention (`PREREG-3` 3.5: `SOME-EXCEEDS`
dominates `ALL-CLEAR`) of resolving a single adverse cell toward the more
conservative, harder-to-argue-away branch. **A batch that fires
`T-INDVERIFY-ARTIFACT` at some cells and would independently have fired
`T-INDVERIFY-CONFIRMED` at others reports BOTH: the flagged cells under
`T-INDVERIFY-ARTIFACT`'s license, the surviving cells under
`T-INDVERIFY-CONFIRMED`'s** — this is a per-cell finding, not a single binary
verdict over the whole covered set, precisely because `lam1n` and `hkz` have
already shown different beta-dependence behaviour in this corpus (§1) and may
show different independent-route behaviour too.

### 2.7 WHY THIS DOES NOT TRIGGER PREREG-2 §7.5's REPAIR BAR, AND IS NOT AN EIGHTH OR NINTH CONSECUTIVE GATE REPAIR — RE-DERIVED, NOT ONLY CITED

`PREREG-2` 7.5 bars a further dispersion criterion, fibre clause or gate
repair in this goal unless six conditions hold, plus an absolute bar on an
eighth consecutive gate repair. `PREREG-3` 3.6 already established that
`BATCH-fbb639`'s part (c) was not such a repair, keeping the count at seven.
Applying the same three tests to part (b) independently, rather than only
citing that conclusion:

1. **It specifies no criterion, clause or gate.** §2.4's comparison is
   `PREREG-3` §3.3's OWN formula, re-applied verbatim to a route that is now
   independent — not a new rule, not a new threshold, and not an amendment to
   `A-1` or to any candidate's admissibility. Nothing here is scored against
   a future candidate; §2.6's three branches license a recorded flag on a
   SPECIFIC PAST VERDICT (`T-INDVERIFY-ARTIFACT`) or a discharge of a SPECIFIC
   PAST QUALIFICATION (`T-INDVERIFY-CONFIRMED`) — never a working assumption
   and never a gate.
2. **It re-verifies a measurement already made, on a route already claimed,
   rather than measuring a new class of object.** `BATCH-fbb639` already ran
   the comparison this document reruns; part (b) is a REPLICATION under a
   corrected independence assumption, not a first look at a new candidate
   class (contrast `BATCH-fbb639`'s own part (c), which reached a class `A-1`
   had never touched — a different, and already-settled, justification).
   `PREREG-2` 7.5's repair bar governs criteria that decide FUTURE candidates;
   this document decides nothing about any future candidate.
3. **Its outcome is a verification result about THIS batch's own prior
   measurement, not a repaired gate's pass/fail.** Even `T-INDVERIFY-CONFIRMED`,
   its most favourable branch, licenses only citing an EXISTING verdict
   without an EXISTING qualification — it manufactures no new claim about any
   lattice, and it does not touch `A-1`, extend it, or replace it, exactly as
   `PREREG-3` 3.5's `T-C3LANE-OPEN` did not.

**THE SEVEN-CONSECUTIVE-INSTRUMENT-BATCH COUNT REMAINS SEVEN, NOT EIGHT OR
NINE**, for the same structural reason `PREREG-3` 3.6 gave for keeping it at
seven: neither `BATCH-fbb639`'s part (c) nor this document's part (b) is a
gate-repair attempt. Both reviews of `BATCH-fbb639` independently concurred
with the identical reasoning applied to that batch (Validator
`RULING-PREREG-2-7.5-REPAIR-BAR`; Red Team RT-3); nothing in this document's
own re-derivation departs from that ruling.

### 2.8 THE REVISIT CONDITION, DECLARED NOW SO IT BINDS A LATER SESSION

If `T-INDVERIFY-ARTIFACT` fires at any cell: that cell's `EXCEEDS` verdict
from `BATCH-fbb639` **must** be flagged as methodologically unsupported in a
superseding record, and **no successor may cite it without that flag**. This
does **NOT** retroactively change `T-C3LANE-OPEN-PARTIAL`, which remains
`BATCH-fbb639`'s own, correctly-read, frozen-clause outcome — exactly as
`DEC-20260813-28d7b2`'s own revisit condition states, quoted and carried
here without alteration.

### 2.9 Prediction register — ONE prediction stated, ONE explicitly withheld

| id | statement | falsifier | class | open at notarization |
|---|---|---|---|---|
| P-IV-a | `COVERED` is non-empty for part (b) (at least one of the 18 cells has genuine `ROUTE-P` per-basis ground truth in `results_relvar.json`'s `G_REL1` block) | `COVERED` is empty (`T-INDVERIFY-NODATA`) | PREDICTION — grounded in this Coordinator's own read of `results_relvar.json`'s `G_REL1` structure (§2.1), not measured by this document | OPEN |

**P-IV-b (the direction — `ALL-SURVIVE` vs `SOME-ARTIFACT`) IS DELIBERATELY
NOT STATED AS A PREDICTION.** `PREREG-3`'s own `P-C3b` was stated with a
reasoned direction because this Coordinator had DIRECTLY OBSERVED both
quantities at one cell class before that batch ran (bit-identical `ROUTE-I`
agreement, non-zero `s_c^fib`). No equivalent direct observation is possible
here: this measurement's entire purpose is to learn whether that same
agreement persists once the code-sharing that produced it is removed, and
`EV-MLKEM-965a37`/`KN-FIND-9b5df0` both record this as explicitly, genuinely
OPEN — not merely unmeasured but of unknown direction. Stating a directional
prediction here would presuppose the answer this batch exists to find.
Withholding it is the more conservative, more honest choice, and is itself
reported so a later reader does not mistake the omission for an oversight.

---

## 3. GUARDS AND COULD-NOT-FAIL ARRANGEMENTS, NAMED BEFORE THE RUN

### 3.1 Could-not-fail check on the D_route' comparison

Would hold if `D_route'` were defined so large, or `s_c^fib` so small by
construction, that `"DOES NOT EXCEED"` (hence `T-INDVERIFY-ARTIFACT`) were
guaranteed regardless of measured values, or so tightly bound to zero that
`"EXCEEDS"` (hence `T-INDVERIFY-CONFIRMED`) were guaranteed instead. **WE ARE
IN NEITHER:** `D_route'` is a **measured** max absolute deviation between two
genuinely different code paths on nominally identical numeric inputs — it is
not fixed, and this goal's own history (`OBS-1` of `EV-MLKEM-aa39ad`: `rdet`'s
`T1` residual `3.865e-12`, a genuinely small but non-zero cross-computation
residual measured in this exact corpus) shows such residuals, when a real
route split exists, are measured near machine epsilon rather than
manufactured to be large OR forced to be exactly zero. `s_c^fib` at every
cell this measurement can reach is an already-archived, independently
computed value (`0.0038`–`0.0848` per `EV-MLKEM-965a37`'s
`termination_branch.read_off`) from an unrelated computation (dispersion
across 8 fibre bases) — there is no shared construction between it and
`D_route'` that forces the comparison's direction either way.

### 3.2 Could-not-complete guard — an explicit budget-exhaustion outcome

Part (b) requires genuinely NEW reduction (up to `d = 40`), unlike every
obligation of `PREREG-3` and RC-3 above, which read only. **If this task's
hard wall-clock cap (§ task card, §4 dispatch queue) is reached before every
cell in `COVERED` has a computed `D_route'`:** this is INFRASTRUCTURE SIGNAL
(`AGENTS.md` rule 5), reported as such, per-cell, distinguishing
"UNCOVERED: no ROUTE-P ground truth" (§2.3) from "NOT COMPUTED: budget
exhausted" (this guard) — **never** silently merged, and **never** read as
either `VERDICT'` by default. A budget-exhaustion outcome at every attempted
cell fires `T-INDVERIFY-NODATA` if it leaves `COVERED` (as actually computed)
empty; a partial completion is reported with the `-PARTIAL` suffix and the
exact list of not-computed cells named separately from genuinely uncovered
ones.

---

## 4. OUTCOME ROWS

| row | what it records |
|---|---|
| `R-IV-OUT-0` | RC-3 (§1): the frozen coverage-table correction text, carried verbatim, with the lead's own confirmation that it read the correction from `PREREG-4` and recomputed nothing |
| `R-IV-OUT-1` | obligation 0 (§2.3): the part-(b) coverage table — 18 cells, genuine `ROUTE-P` per-basis ground truth or `NONE FOUND`, exact basis count per covered cell |
| `R-IV-OUT-2` | obligation 1 (§2.4): per covered cell, the declared implementation choice (§2.2), `s_c^fib`, `D_route'`, matched-basis count, `VERDICT'`, agreement/disagreement with `BATCH-fbb639`'s original `EXCEEDS` |
| `R-IV-OUT-3` | obligation 2 (§2.5): `ALL-SURVIVE` / `SOME-ARTIFACT`, coverage fraction, cell lists |
| `R-IV-OUT-4` | the termination branch read off `R-IV-OUT-1`/`R-IV-OUT-3` under §2.6's frozen precedence, with the `-PARTIAL` suffix applied per its own rule, and, if `T-INDVERIFY-ARTIFACT` fired at any cell, that cell named explicitly for the revisit condition (§2.8) |

---

## 5. BINDING CARRIES — IN FORCE, NOT RE-LITIGATED

Carried in full from `PREREG-2` §§10/10.1 and `PREREG-3` §7, without
restatement of every line here — the lead, the reviews and the ledger archive
are bound exactly as those documents state, plus the following, specific to
this batch:

* **CLAIM TIER TOY, UNCONDITIONALLY.**
* **`AM-3` IS NOT RETIRED.** `AM-10` through `AM-18` and their carries are in
  force. `BATCH-a44d08`, `BATCH-4ed139`, `BATCH-9e3584`, `BATCH-cbe023`,
  `BATCH-6b6e78` and `BATCH-fbb639` are NOT RESCORED OR REVALIDATED in any
  respect by anything in this document, including its own reads of
  `results_relvar.json`, `results_l7l8.json` and `results_am4.json`, which
  extract already-committed numbers only.
* **NEITHER SUB-6x COUNT IS CITABLE.** "A factor of 6 to 31" is FALSE; the
  citable range is 4.87x to 31.03x. "Genuinely cross-platform" is NOT
  citable; the citable form is a PORTABILITY result across three textually
  distinct implementations with `fpylll` pinned at 0.6.4.
* `AM4-OBS-1` cited ONLY through `KN-FIND-f38a89`. `AM-9`: `fpylll`'s `k`
  counts the q-scaled rows, NOT the identity block. THE `G-VAR` REFUSAL IS
  CITED ONLY AS CONDITIONAL ON THE FROZEN FAMILY `F0`.
* **`KN-FIND-7d098b`, `KN-FIND-9d44b4` AND `KN-FIND-9b5df0` ARE PROMOTED —
  NOT RESTATED AS NEW** anywhere in this document. `KN-FIND-9b5df0`'s own
  content (the instrument-design lesson this batch's part (b) operationally
  answers) is cited, not repeated.
* `T-C3LANE-OPEN-PARTIAL` (the branch `BATCH-fbb639` fired) IS NOT REOPENED,
  RE-SCORED OR REVERSED by anything in this document; §2.6/§2.8 state
  precisely and only what part (b)'s own outcome can attach to it.
* The split-producer notarization pattern is retained unchanged. The
  receipt-with-`commit_sha: null`-inside-its-own-commit archive pattern is
  MANDATORY. Every run emits durable `command.txt`, `stdout.log` and
  `stderr.log`, with no path inside a folded YAML scalar, and lists every
  path it wrote in its report.
* `knowledge/INDEX.md` must NOT be written, regenerated or staged.
* **`AGENTS.md` rule 12 is UNMET AND UNWAIVED.** Every producer and reviewer
  of this batch records `model_verified: false` with its reason, its host
  and its stack. THIS BINDS THIS BATCH'S OWN REVIEWS EXACTLY AS MUCH AS IT
  BINDS THE PRODUCER WHOSE INDEPENDENCE CLAIM THEY ARE CHECKING — stated here
  because `DEC-20260813-28d7b2` names this irony explicitly for itself and it
  does not lapse at the batch boundary: two reviews of THIS batch, checking
  whether the LEAD's `ROUTE-I'` is genuinely code-independent, are themselves
  two sessions on ONE MODEL and (absent a probe receipt showing otherwise)
  likely one host — the identical shape of dependence this batch's own
  measurement exists to test on the producer side.
* **`PD-4` remains OPEN.** Each review's own report and probes sit
  uncommitted across a dispatch window and are the sole carriers of their own
  evidence until the ledger archive commits them.

---

## 6. SCOPE, INDEPENDENCE AND WHAT THIS BATCH CANNOT DO

**SCOPE.** `q = 3329`; `d in {20, 30, 40}` (`L7`, `L9`, `L11` ONLY);
`lam1n`, `hkz` ONLY (`rawtail` out of scope for part (b), §2.1); the frozen
beta grids of §2.1; up to `N_BASES = 8` per covered cell, narrower where
`ROUTE-P`'s own per-basis ground truth is narrower; `binary64` only. **NO
REDUCTION ABOVE `d = 40`, ANYWHERE, FOR ANY REASON.** Part (b) performs NEW
reduction, unlike `PREREG-3`'s read-only part (c) — this is deliberate and is
the one genuinely new computation this batch authorizes, bounded to
`d <= 40` exactly as every reduction this goal has ever run.

**PART (b)'S OWN SCOPE, CARRIED AT EVERY QUOTATION.** This measurement says
nothing about `A-1`, about the in-scope candidates of `PREREG-2` 2.4, about
`X_gso_k`, or about any determinant-only candidate. It says nothing about
`ML-KEM`, any FIPS 203 parameter set, any attack cost, or any cost model. Its
most favourable branch (`T-INDVERIFY-CONFIRMED`) licenses citing an EXISTING
verdict without an EXISTING qualification, for the cells checked — nothing
stronger, and nothing about any UNCOVERED cell.

**INDEPENDENCE IS PROCEDURAL AND NEVER MODEL-LEVEL.** `AGENTS.md` rule 12 is
UNMET AND UNWAIVED in this goal and is not waived here — see §5's explicit
note that this binds this batch's own reviews too.

---

## 7. AUTHORSHIP GAP, DECLARED RATHER THAN NARRATED CLOSED

The Coordinator session that wrote this file **held no shell**. It ran no git
command and computed no hash. It DID read committed repository files
directly with a read-only tool (never a shell), and every number attributed
to "this Coordinator" above (the `G_REL1` per-basis structure and its
beta_lo/beta_hi-only coverage, the `results_relvar.json`/`results_l7l8.json`/
`results_am4.json` path locations, the `probe_coverage_beta_mismatch_output.json`
`true_abs_deviation: 0.0` values for `hkz/L9_b22` and `hkz/L11_b30`) was read
that way from the exact cited path, not computed, not estimated, and not
carried from any prose summary. **This is a weaker claim than a
measurement**: it is one session's reading of one file at one point in time,
offered so the lead can check it independently, not offered as this batch's
evidence. The lead producer's own obligation 0 (§2.3) is the batch's actual,
attributed audit of what `ROUTE-P` genuinely covers.

`prereg_sha256.txt` is generated and committed by `TASK-20260813-e24ad9`, by
a session that has a shell, exactly as every prior `PREREG-*` of this goal
required for its own hash file.

**END OF FROZEN TEXT.**
