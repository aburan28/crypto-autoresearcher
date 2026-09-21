# PREREG-3 — BATCH-fbb639 FROZEN PRE-REGISTRATION

    goal        GOAL-MLKEM-005
    batch       BATCH-fbb639
    task        TASK-20260813-0eb5a3 (Coordinator, pre-registration only)
    notarized by TASK-20260813-6ad846 (snapshot archive, runs alone, before any
                measuring task)
    authority   DEC-20260813-c60bba (the closing decision of BATCH-6b6e78, whose
                `next_actions` — ONE action in three parts — this document
                discharges in full), applying AM-18 of DEC-20260812-781961,
                AM-17 of DEC-20260812-7c4a1e, AM-15/AM-16 of DEC-20260809-afe29b
                and AM-10..AM-14 of DEC-20260808-05b684
    claim tier  TOY, UNCONDITIONALLY

**THIS TEXT IS FROZEN AT NOTARIZATION AND IS NEVER EDITED.** A correction is a
superseding record under a new identifier, never an edit here. No measuring task
of BATCH-fbb639 may be dispatched until this file is committed by
TASK-20260813-6ad846 and that commit contains **zero** producer artifacts. That
is the split-producer notarization pattern, retained unchanged; it has now
worked six times and has been verified in both directions by independent
sessions each time.

---

## 0. WHAT THIS BATCH DISCHARGES, AND WHY ITS PARTS TRAVEL TOGETHER

`DEC-20260813-c60bba` closed `BATCH-6b6e78` (`T-A1-FALSIFIED-PARTIAL`, Validator
verdict `incomplete`) and set **exactly one** `next_action`, in three parts that
must travel together in this successor pre-registration:

* **(a) DISCHARGE RC-1** — supersede `PREREG-2`'s headline count of 1,416
  `VAR-F`-verdict-changing cells, which the Validator's blind re-derivation from
  the frozen text alone gives as 1,313 under `PREREG-2` 2.6's own **declared**
  `route_provenance`.
* **(b) DISCHARGE RC-2** — supersede the false "`P-A12a` mis-scored `HELD` ...
  left unedited" narrative of `report_a1.md` §10 and the `TASK-20260813-48240d`
  archive commit message. The committed `results_a1.json` was, and always was,
  `FALSIFIED`.
* **(c) THE LEAD MEASUREMENT** — at `d <= 40` (`L7` `d=20`, `L9` `d=30`, `L11`
  `d=40` — no reduction above `d = 40`), measure whether the
  REDUCTION-DEPENDENT observables `lam1n`, `hkz`, `rawtail` (out of `A-1`'s
  scope by `PREREG-2` 2.5, and the half of the candidate list that matters for
  `C3`) have their **own** fibre dispersion at `binary64` exceeding their
  **two-route disagreement**.

**(a) and (b) ARE BOOKKEEPING AND ARE FROZEN HERE AS MECHANICAL CORRECTIONS.**
Neither requires a re-run, a new computation, or any judgement by the lead
producer beyond carrying the frozen text below into its own report verbatim,
attributed to this document. **(c) is the substantive measurement of this
batch** and its termination clause is frozen in full in §3 before any cell is
read.

**WHY THE THREE TRAVEL TOGETHER.** `DEC-20260813-c60bba`'s rationale (i) states
that deferring (a)/(b) risks a successor citing the not-yet-admissible 1,416
count or the false narrative; (ii) states that (c) is the one place `A-1`'s
answer could ever have mattered for what `C3` needs, because `A-1`'s own scope
(`PREREG-2` 2.5) excludes every reduction-dependent observable, which is the
half of this goal's candidate list that `C3` actually needs; (iii) states that
doing only (a) and (b) would leave that blocking uncertainty untouched. This
document does all three, in that order, because (a)/(b) are prerequisites a
reader of (c) must not have to reconstruct.

---

## 1. RC-1 — THE HEADLINE-COUNT CORRECTION, FROZEN AND MECHANICAL

**READING ADOPTED, AND WHY.** `PREREG-3` adopts the **1,313 reading**: the
headline is restated as **1,313 changing `VAR-F` cells**, under `PREREG-2`
2.6's own **declared** `route_provenance` ("the committed float64 expressions
with the cast to `np.float64` replaced by a cast to `np.float32` **and nothing
else changed**"). This is the reading `EV-MLKEM-4ba196.finding_2_headline_count`
reports as the Validator's **blind** re-derivation from the frozen text alone,
**before** reading any producer code (`EV-MLKEM-4ba196` finding F-1; Red Team
`O-5`, independently).

**WHY THIS READING AND NOT THE OTHER.** `DEC-20260813-c60bba` left both readings
open and required this document to pick one, unambiguously, and say why —
naming the gap `PREREG-2` 2.6 itself left (`EV-MLKEM-4ba196`
`finding_2_headline_count.root_cause`). Two readings are defensible from
`PREREG-2`'s frozen text; only one — 1,313 — **matches what the record's own
`route_provenance` field already declares**. Adopting it requires **no new
declaration** and **no retroactive amendment** of what `route_provenance`
meant; adopting 1,416 instead would require writing, **after the number is
already known**, a new declaration that the binary32 Gram is formed by
float-accumulation rather than by the exact-int64-cast-once route the text as
written already says — which is exactly the ordering `AM-18(a)` exists to
forbid in a different but structurally identical place (a definition written
to fit an outcome already seen). 1,313 is also the more conservative of the two
numbers. **Both facts are stated so a later reader can check the reasoning, not
just the conclusion.**

**FROZEN CORRECTION TEXT, TO BE CARRIED VERBATIM INTO THE LEAD'S REPORT:**

> The headline count of `BATCH-6b6e78`'s `PREREG-2` measurement is **1,313**
> changing `VAR-F` cells, not 1,416. The 1,416 figure in the committed
> `results_a1.json` and `report_a1.md` of `TASK-20260813-2ce014` arose because
> `measure_a1.py`'s binary32 route `R4` accumulates the Gram at the **working
> precision** (`Bf @ Bf.T` with `Bf = B.astype(dt)`), which does not match what
> its own `route_provenance` field **declares** it does (form the Gram in exact
> int64 and cast once). Under the declared provenance the count is **1,313**.
> **This supersedes the 1,416 figure and its by-route / by-candidate /
> by-fibre-family decompositions, the `FC-3a` count of 868 (or 867), the `R4`
> binary32 `K`-interval endpoints `5.272e+06` / `1.750e+04`, and the binary32
> "6 of 38" diagnostic wherever any of them is quoted without this correction
> in the same sentence.**

**WHAT IS UNCHANGED, restated so it is not lost in the correction.** The
qualitative headline — 49 of 330 blocks change verdict; concentration on routes
`R4` and `R2` only; zero contribution from `R0`, `R1`, `R3`, `R5` — is
**invariant under both readings** and is **not** touched by this correction
(`EV-MLKEM-4ba196.finding_2_headline_count.what_is_unchanged`). Route `R2`'s
own contribution of exactly 20 is unaffected; it is computed at `binary64`
only, where the two Gram-formation readings are bit-identical (every entry is
an integer below `2**53`). **Neither this correction nor its predecessor
touches `T-A1-FALSIFIED-PARTIAL`, which remains the branch that fired.**

**NO RE-RUN IS REQUIRED, AND NONE IS PERMITTED HERE.** `measure_a1.py`,
`results_a1.json` and `report_a1.md` are **immutable committed artifacts**
(`TASK-20260813-48240d`, `4e466c6bf221ea002fe84311baccdb816081a8cd`) and are
**not edited, not re-run, and not vendored**. The lead producer of this batch
carries the frozen text above into its own report **by quotation**, attributed
to `PREREG-3` §1, and does **not** recompute anything.

---

## 2. RC-2 — THE NARRATIVE CORRECTION, FROZEN AND MECHANICAL

**FROZEN CORRECTION TEXT, TO BE CARRIED VERBATIM INTO THE LEAD'S REPORT:**

> `report_a1.md` §10 of `TASK-20260813-2ce014`, and the archive commit message
> the parent harness session wrote for `TASK-20260813-48240d`
> (`4e466c6bf221ea002fe84311baccdb816081a8cd`), both state that "the automated
> `P-A12a` register line in `results_a1.json` is mis-scored `HELD`; corrected to
> `FALSIFIED` ... with the JSON left unedited." **THAT CLAIM IS FALSE AGAINST
> THE COMMITTED ARTIFACT.** `results_a1.json`'s
> `PREDICTION_REGISTER.items["P-A12a"].OUTCOME` reads `"FALSIFIED"`, not
> `"HELD"` — the string `"HELD"` does not occur against `P-A12a` anywhere in the
> committed file, confirmed independently by the Coordinator that decided
> `DEC-20260813-c60bba` and by the Validator's finding F-2
> (`EV-MLKEM-4ba196.finding_1_narrative_correction`). **`P-A12a`'s committed
> `OUTCOME` is, and always was, `FALSIFIED`.** This is a correction of a
> **description**, never of a **measurement**: the substantive value —
> `FALSIFIED` at 22 cells (`X_null` 12, `rdet` 10, both route `R2_QR_of_BT`) —
> was correct throughout, in both the JSON and `report_a1.md`'s own corrected
> table, and needs no correction.

**WHAT IS NOT EDITED, AND WHERE THE CORRECTION MUST APPEAR.** The commit
`4e466c6bf221ea002fe84311baccdb816081a8cd` and its message are **immutable
history and are not touched** (`AGENTS.md` rules 2 and 5). The correction above
is not written into that commit; it is written into **this pre-registration**
and must additionally appear, verbatim or by unambiguous restatement, in the
new evidence record this batch's ledger archive produces (§3.7 below), so a
reader who reaches either record independently is corrected. **No further
carrier is required or permitted**: report_a1.md and results_a1.json
themselves are not edited either — both are immutable committed artifacts, and
`results_a1.json`'s own field was already correct.

**NO RE-RUN IS REQUIRED.** This obligation is discharged by carrying the frozen
text above into the lead's report and into the ledger archive's evidence
record; no code is executed for RC-2.

---

## 3. PART (c) — THE LEAD MEASUREMENT

### 3.0 What is being asked, restated precisely

`A-1` (`PREREG-2` §1) is stated **only** over the in-scope candidates of
`PREREG-2` 2.4 — the determinant-only class and `X_gso_k`. `lam1n`, `hkz` and
`rawtail` are **declared out of scope** for `A-1` by `PREREG-2` 2.5, because
this goal's `d <= 40` no-new-reduction constraint made a two-precision
evaluation of them impossible in `BATCH-6b6e78`. That scope exclusion is the
**half of this goal's candidate list that matters for `C3`** — `A-1`, held or
falsified, says nothing about them in either direction.

Part (c) asks the **narrower and different** question `A-1` was never asked:
**does each of `lam1n`, `hkz`, `rawtail` have its own fibre dispersion at
`binary64` — measured exactly as `A-1.2`/`A-1.3` measure it for the in-scope
candidates, `s_c^fib` over the `N_BASES = 8` fibre family — that EXCEEDS its
own two-route disagreement**, i.e. the gap between two independently
computed values of the same observable at the same cell? This is **not** a
new dispersion criterion, **not** a gate, and **not** a replacement for `A-1`
(§3.6 states why in full). It is a diagnostic measurement, exactly in the
spirit of `PREREG-2` §3's "no gate, no threshold" diagnostic section, applied
to the one candidate class `A-1` could never reach.

### 3.1 Frozen objects — carried, not re-declared

    q          = 3329                          (carried, PREREG-1 2.1)
    N_BASES    = 8                              (basis index i = 0..7, carried)
    Lattices in scope for this batch, and ONLY these three:
        L7  (d=20, k=6)    beta grid {5, 10, 15}
        L9  (d=30, k=9)    beta grid {7, 15, 22}
        L11 (d=40, k=12)   beta grid {10, 20, 30}
    (L1, L2, L4, L5, L8, L10, L12 are OUT OF SCOPE for this batch: L1/L2/L4/L5
    exceed d = 40; L8/L10/L12 are the mirror partners of L7/L9/L11 and add
    nothing part (c) needs — they are not measured here.)

    ROUTE-P  ("primary / committed pipeline route")
             the value of candidate X at lattice L, beta b, basis i as computed
             by the FROZEN, ALREADY-COMMITTED measure_relvar.py pipeline of
             BATCH-9e3584, committed at
             coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/
             TASK-20260809-cda2f6/results_relvar.json
             (task TASK-20260809-cda2f6, notarized under prereg sha256
             190cf4740b0ecefdbe7d1da0868a6258352b044ae5e99da470060f94049c70ea,
             per that file's own governed_by block). THIS IS AN
             ALREADY-ARCHIVED VALUE. It is READ, never recomputed, never
             re-derived, and NEVER re-run.

    ROUTE-I  ("independent replication route"), DECLARED PER CANDIDATE:
        lam1n, hkz  at L7 ONLY, beta in {5, 10, 15}:
             the ALREADY-COMMITTED independent re-measurement of
             BATCH-4ed139 rider (iii) (TASK-20260812-0e930c, "P-L1"), which
             installed fpylll 0.6.4 into a FRESH virtualenv, rebuilt the 8
             frozen L7 bases from their declared construction, ran the frozen
             HKZ pipeline once per basis, and reported hkz and lam1n at beta
             in {5, 10, 15} against the committed per-basis values, committed
             at
             coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/
             TASK-20260812-0e930c/results_l7l8.json
             (attributed: EV-MLKEM-aa39ad OBS-11 reports this comparison as
             MAX ABSOLUTE DEVIATION 0.0 over 96 comparisons spanning L7 AND
             L8; this document does not assume that figure decomposes to L7
             alone and REQUIRES the lead to read the L7-only subset directly
             from results_l7l8.json rather than carry the combined number).
             THIS IS ALSO AN ALREADY-ARCHIVED VALUE. It is READ, never
             recomputed, never re-run.
        rawtail  at every cell:
             NO ROUTE-I OF THIS KIND IS KNOWN TO EXIST IN THE COMMITTED CORPUS.
             This Coordinator's own pre-dispatch read of
             results_relvar.json's forced_arithmetic block found exactly one
             related but NON-EQUIVALENT quantity — see ROUTE-W below — and
             found nothing else. THE LEAD MUST VERIFY THIS BY ITS OWN SEARCH
             (§3.2 obligation 0) RATHER THAN TAKE THIS SENTENCE AS FINAL.
        lam1n, hkz  at L9, L11:
             NO ROUTE-I IS KNOWN TO EXIST FOR THESE LATTICES from the P-L1
             rider (which covered L7/L8 only). A DIFFERENT CANDIDATE SOURCE IS
             FLAGGED FOR THE LEAD TO CHECK, NOT ASSUMED VALID: this
             Coordinator's read-only search found the keys "lam1n" and "hkz"
             at "L9" and "L11" inside
             coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/tasks/
             TASK-20260808-2a9085/results_am4.json
             (an earlier, differently-governed AM-4 measurement). THIS
             COORDINATOR DID NOT VERIFY that file's lattice construction,
             seeds or frozen-family identity against PREREG-1 2.2/2.3's F0 —
             it may use a different (d,k) construction, a different modulus
             block, or predate the frozen family entirely. §3.2 obligation 0
             makes checking this, and reporting the verdict either way, a
             completion-gate item. IT MUST NOT BE TREATED AS A VALID ROUTE-I
             UNTIL THE LEAD CONFIRMS, BY READING BOTH FILES' OWN DECLARED
             CONSTRUCTION, THAT IT SCORES THE SAME FROZEN OBJECT.

    ROUTE-W  ("weak / non-equivalent proxy"), rawtail ONLY, ONE CELL:
             results_relvar.json's own
             forced_arithmetic.rawtail_T1_ambient_isometry_residual_beta5
             = 5.808686864838819e-13 (attributed, read directly by this
             Coordinator from the committed file). THIS IS NOT A ROUTE-I: per
             measure_relvar.py's own construction (read directly by this
             Coordinator), it compares Gram-Schmidt logs computed on the RAW,
             UNREDUCED basis B0 under an ambient isometry H against the same
             on B0 directly — it is a numerical-stability control on the GSO
             computation itself, not an independent computation of the actual
             POST-REDUCTION rawtail statistic reported elsewhere in this
             corpus. It is REPORTED, LABELLED AS SUCH, AND NEVER COUNTED
             toward the substantive coverage or verdict of §3.4 — exactly as
             PREREG-2 5 reported CONSISTENCY CHECKS separately from
             PREDICTIONS.

    Fibre dispersion at binary64, s_c^fib(X, L, b):
             the ALREADY-ARCHIVED float_sd value at
             results_relvar.json.per_candidate.<X>.per_cell.<L>_<b>.float_sd
             — sd over the N_BASES = 8 fibre-family bases, exactly the same
             statistic A-1.2/A-1.3 consume for the in-scope candidates. READ,
             never recomputed.

**WHY ABSOLUTE UNITS, NOT `A-1`'s RELATIVE `rho`.** `A-1`'s `rho = s_c/|m_c|`
is a relative statistic; the archived route-disagreement figures this section
relies on (`0.0` bit-identical; `5.8e-13`) are reported in **absolute** units
in their own sources. Comparing `s_c^fib` (absolute) against `D_route`
(absolute, defined next) avoids introducing a **new** normalization choice
this document does not need; the comparison is unit-consistent because both
sides are the same candidate's own value in the same units at the same cell.

### 3.2 Obligation 0 — coverage audit, BEFORE any comparison is computed

**THE LEAD'S FIRST ACT.** Before computing any dispersion-vs-disagreement
comparison, the lead **reads** (not recomputes):

1. `results_relvar.json` (`per_candidate` block) for `s_c^fib` of `lam1n`,
   `hkz`, `rawtail` at every cell of `L7`, `L9`, `L11`'s beta grids —
   9 cells per candidate, 27 cells total.
2. `results_l7l8.json` for the `L7`-only subset of the `lam1n`/`hkz` P-L1
   comparison, and reports the **max absolute deviation restricted to `L7`**
   (not the combined `L7`+`L8` figure) at each of the 3 `L7` betas, per
   candidate.
3. `results_am4.json` (`BATCH-cbe023`), checking whether its `L9`/`L11`
   `lam1n`/`hkz` entries use the **same** frozen construction (`q = 3329`, the
   same `(d,k)` pairs, the same modulus-block / `PIN-DET` construction as
   `PREREG-1` 2.2/2.3's `F0`) as `results_relvar.json`. **REPORT THE VERDICT
   EXPLICITLY, either way**: if the construction differs in any declared
   respect, `results_am4.json` is **NOT** a valid `ROUTE-I` for this batch and
   is excluded, with the specific mismatch named; if it matches, it becomes a
   valid `ROUTE-I` for `L9`/`L11` and is used in §3.4 exactly as the `L7`
   `ROUTE-I` is.
4. `results_relvar.json`'s `forced_arithmetic` block for any further
   `rawtail`, `lam1n` or `hkz` residual this Coordinator's own search may have
   missed, and any other already-committed artifact under
   `coordination/goals/GOAL-MLKEM-005/` the lead's read scope reaches that
   independently computes any of the three candidates at `L7`, `L9` or `L11`
   on the frozen construction. **A FOUND SOURCE IS REPORTED WITH ITS PATH AND
   USED; A SEARCH THAT FINDS NOTHING IS REPORTED AS HAVING FOUND NOTHING,
   NEVER SILENTLY ASSUMED.**

**THE OUTPUT OF OBLIGATION 0 IS A COVERAGE TABLE**: for each of the 27 cells
(3 candidates x 3 lattices x 3 betas), whether a valid `ROUTE-I` exists, its
source path, and — for `rawtail` only — whether `ROUTE-W` applies (labelled,
never substituted for a missing `ROUTE-I`). **THIS TABLE IS A FIRST-CLASS
DELIVERABLE.** A run that computes the comparison of §3.4 without first
producing and reporting this table has not discharged obligation 0.

### 3.3 Obligation 1 — the dispersion-vs-disagreement comparison, per covered cell

For every cell where obligation 0 found a valid `ROUTE-I`:

    D_route(X, L, b) = max over the matched bases i (i = 0..7, or the subset
                       both routes actually cover — report the subset size)
                       of | X_ROUTE-P(L, b, i) - X_ROUTE-I(L, b, i) |

    VERDICT(X, L, b) = "EXCEEDS"        if  s_c^fib(X, L, b) >  D_route(X, L, b)
                      = "DOES NOT EXCEED" if s_c^fib(X, L, b) <= D_route(X, L, b)

Report, per cell: `s_c^fib`, `D_route`, the number of matched bases, the
verdict, and the source path of `ROUTE-I`. **Ties (`s_c^fib == D_route`
exactly) are `"DOES NOT EXCEED"`** — the inequality is strict in the direction
that would license a lane closure, matching this campaign's convention of
resolving a definitional tie toward the more conservative (harder-to-falsify)
branch (cf. `PREREG-2` 1.3's `precision_degenerate` rule, which is exempting
rather than falsifying at its own tie).

For `rawtail` cells where only `ROUTE-W` applies: report `s_c^fib`,
`D_ROUTE-W` (`|rawtail_ROUTE-P - rawtail_ROUTE-W_construction|` at the ONE
matched cell, `L7 beta=5`, basis-index-0 only per the source's own
construction), and the comparison — **labelled `ROUTE-W (non-equivalent
proxy, NOT counted)`** and excluded from §3.4's substantive tally.

For every other cell: report `"NO ROUTE-I: UNCOVERED"`, with the reason
(no independent computation of this candidate at this cell exists in the
committed corpus, per obligation 0's search).

### 3.4 Obligation 2 — the aggregate verdict and its coverage

Let `COVERED` = the set of the 27 cells for which obligation 0 found a valid
`ROUTE-I` (excluding `ROUTE-W` cells, which are never counted here).

    ALL-CLEAR   :  VERDICT(X, L, b) = "DOES NOT EXCEED" for EVERY cell in COVERED
    SOME-EXCEEDS:  VERDICT(X, L, b) = "EXCEEDS" for AT LEAST ONE cell in COVERED

These are mutually exclusive and exhaust `COVERED` whenever `COVERED` is
non-empty. Report the exact count and list of cells on each side, and report
`|COVERED|` out of 27 (or 26, if `ROUTE-W` is excluded as designed) as the
**coverage fraction**, stated in the same sentence as any aggregate verdict.

### 3.5 THE FROZEN TERMINATION CLAUSE FOR PART (c)

**Exactly one of the following four fires, in this precedence order.**

**T-C3LANE-NODATA** — **FIRES WHEN** `COVERED` is empty (no cell of the 27 has
a valid `ROUTE-I`). **MEANS:** this batch's committed corpus contains no
independent second computation of `lam1n`, `hkz` or `rawtail` at `L7`, `L9` or
`L11` without a new reduction, so the measurement `DEC-20260813-c60bba`'s
`next_action` asks for **cannot be run this batch at all**. **LICENSES:** a
decision recording this as an **infrastructure/corpus gap** — not a scientific
result in either direction — and naming what a successor would need to commit
(an independently re-run `ROUTE-I` at `L9`/`L11`, gated behind a fresh install
exactly as `BATCH-4ed139`'s `TASK-20260812-0e930c` was) before this measurement
becomes runnable. **FORBIDS:** any claim about dispersion exceeding or not
exceeding anything; closing, pausing or completing `GOAL-MLKEM-005`; closing
the admissibility-gate lane (there is no measurement to close it on).

**T-C3LANE-OBSTRUCTED** — **FIRES WHEN** `COVERED` is non-empty and
`ALL-CLEAR` holds (dispersion does **not** exceed route disagreement at
**every** covered cell). **MEANS:** on the covered cells, the reduction-
dependent observables cannot be resolved to better precision than their own
route-to-route disagreement already provides — the same numerical floor that
made `A-1` untestable on them is present in their own measured behaviour.
**LICENSES**, exactly as `DEC-20260813-c60bba`'s `next_action` and `PREREG-2`
7.2 for `T-UNSTATABLE` require: **CLOSING THE ADMISSIBILITY-GATE LANE**, with
"the observables `C3` needs cannot be evaluated to better than their own fibre
variation by any declared route" as its **named obstruction**, in its **own**
committed Coordinator decision carrying evidence, budget, test boundary,
remaining uncertainty and a concrete successor or revisit condition — **never**
in this batch's own close, which only reports the measurement. **FORBIDS:**
closing, pausing or completing `GOAL-MLKEM-005` — closing the LANE retires the
LANE, never the goal; treating an `UNCOVERED` cell as contributing to this
branch in either direction; any claim about `ML-KEM`, any FIPS 203 parameter
set, any attack cost or any cost model.

**T-C3LANE-OPEN** — **FIRES WHEN** `COVERED` is non-empty and `SOME-EXCEEDS`
holds (dispersion exceeds route disagreement at **at least one** covered
cell). **MEANS:** at that cell, the reduction-dependent observable carries
measurable fibre content **beyond** what its two committed routes disagree
about — the numerical floor that blocked `A-1` for the in-scope candidates is
**not** shown to block this one. **LICENSES:** a statement that "a successor
assumption analogous to `A-1`, restricted to the reduction-dependent
candidates and to the covered cells/routes, has a domain worth stating" — and
**nothing stronger**. **FORBIDS:** treating this as `A-1` **held** for
`lam1n`/`hkz`/`rawtail` (`A-1` was never stated over them and this measurement
does not state it now); specifying any dispersion criterion, fibre clause or
gate on the strength of this branch alone; any claim about `ML-KEM`, any FIPS
203 parameter set, any attack cost or any cost model; closing, pausing or
completing `GOAL-MLKEM-005`.

**THE `-PARTIAL` SUFFIX**, applied to whichever of `T-C3LANE-OBSTRUCTED` /
`T-C3LANE-OPEN` fires, **WHENEVER** `|COVERED| < 27` (i.e. essentially always,
given §3.2's coverage audit is expected to find `lam1n`/`hkz` covered at `L7`
only and `rawtail` covered nowhere in the strict `ROUTE-I` sense — this
expectation is **stated so it is not discovered as a surprise**, and it does
**not** pre-determine `ALL-CLEAR` vs `SOME-EXCEEDS`, which depends on the
**actual measured values** at whichever cells **are** covered). The suffixed
branch reports the substantive verdict over `COVERED` **and** the coverage
fraction **and** the list of uncovered cells, none of which is decided in
either direction. **A missing `ROUTE-I` is never read as `"EXCEEDS"` or
`"DOES NOT EXCEED"` by default — it is `UNCOVERED`, full stop**, exactly as
`PREREG-2` 7.6 treats a timeout or missing dependency as infrastructure signal
rather than a falsifier.

**PRECEDENCE, STATED EXPLICITLY.** `T-C3LANE-NODATA` dominates (fires alone,
with no `-PARTIAL` suffix — there is nothing partial about zero coverage).
Between `T-C3LANE-OBSTRUCTED` and `T-C3LANE-OPEN`, `SOME-EXCEEDS` (hence
`T-C3LANE-OPEN`) takes precedence over `ALL-CLEAR` whenever both could
otherwise be read from the same data — i.e. a single exceeding cell is
sufficient to fire `T-C3LANE-OPEN` and **prevents** `T-C3LANE-OBSTRUCTED`,
matching `A-1`'s own falsifier logic (any one of `FC-2a`/`FC-2b`/`FC-3a`/`FC-3b`
firing is independently sufficient) applied to this measurement's two
possible readings.

### 3.6 WHY `PREREG-2` 7.5'S REPAIR BAR DOES NOT APPLY HERE — STATED EXPLICITLY

`PREREG-2` 7.5 bars a further **dispersion criterion, fibre clause or gate
repair** in this goal unless six conditions hold, plus an absolute bar on an
eighth consecutive gate repair. **Part (c) is none of those things, and this
is stated so a later reader does not mistake this measurement for an eighth
consecutive gate repair:**

1. **It specifies no criterion, clause or gate.** §3.5's branches license a
   LANE CLOSURE (an admission that a class of observables cannot be resolved
   this way) or a bare statement that a domain is worth stating for a future
   assumption — **never** a threshold, a pass/fail rule, or anything a future
   candidate would be scored against. `A-1` itself is not amended, extended or
   replaced by anything in this document.
2. **It measures a class of objects `A-1` never touched.** `A-1` is stated
   over `PREREG-2` 2.4's in-scope candidates only; `lam1n`, `hkz`, `rawtail`
   are declared out of scope by `PREREG-2` 2.5 for a **structural** reason (no
   new reduction permitted), not because they were tested and failed. This is
   not a repair of a gate that already existed for them — no such gate has
   ever existed for them in this goal.
3. **Its outcome is a measurement result, not a repaired gate's pass/fail.**
   Even `T-C3LANE-OPEN`, its most favourable-to-a-future-gate branch, licenses
   only a statement that a domain is "worth stating" — an observation about
   where a future assumption **might** be built, not a working assumption
   itself, and explicitly not `A-1` extended.

**THE SEVEN-CONSECUTIVE-INSTRUMENT-BATCH COUNT REMAINS SEVEN, NOT EIGHT**,
because part (c) is not a further gate-repair attempt; it is the measurement
`DEC-20260813-c60bba` names as the one place `A-1`'s answer could ever have
mattered for `C3`, run **once**, with a termination clause that can only
close a lane or note an open domain — never propose a ninth candidate
criterion.

### 3.7 The ledger archive's obligation for RC-1/RC-2

The ledger archive of this batch (its identifier reserved but not yet supplied
— see the dispatch queue's `declared_gaps`) **must** carry §1's and §2's frozen
correction text into a new evidence record (`EV-MLKEM-965a37`, reserved) and/or
decision record (`DEC-20260813-28d7b2`, reserved), so that both corrections
exist as **committed, citable ledger records** and not only inside this
pre-registration. **RC-1 and RC-2 are discharged only when that record commits
and the verifier accepts it** — this document freezes the text; the ledger
archive publishes it.

---

## 4. PREDICTION REGISTER (`AM-15(a)` and `AM-15(c)`)

**Both items below were OPEN at the moment of notarization.**

| id | statement | falsifier | class | open at notarization |
|---|---|---|---|---|
| P-C3a | `COVERED` is non-empty (at least one of the 27 cells has a valid `ROUTE-I`) | `COVERED` is empty (`T-C3LANE-NODATA`) | PREDICTION — grounded in this Coordinator's own pre-dispatch read of `results_l7l8.json`, but not measured by this document | OPEN |
| P-C3b | over `COVERED`, `ALL-CLEAR` holds (dispersion does not exceed route disagreement anywhere covered) | at least one covered cell has `s_c^fib > D_route` | PREDICTION | OPEN |

**BASIS FOR STATING `P-C3b` IN THIS DIRECTION, ATTRIBUTED AND NOT MEASURED
HERE.** At the one place this Coordinator could check both quantities directly
— `lam1n`/`hkz` at `L7`, where `ROUTE-I` (`results_l7l8.json`, attributed via
`EV-MLKEM-aa39ad` OBS-11) reports **bit-identical** agreement (max absolute
deviation `0.0`) while `results_relvar.json`'s own archived `s_c^fib` at `L7`
is **non-zero** for both candidates (`lam1n`: `0.0434` at `b5/b10/b15`; `hkz`:
`0.0239` at `b5`, `0.0106` at `b10` — read directly by this Coordinator from
the committed file and cited so the lead can check them independently rather
than trust this sentence), the arithmetic of §3.3 gives `"EXCEEDS"` at those
three cells **before any new computation is run**, since any positive number
exceeds zero. **THE LEAD COMPUTES AND REPORTS THIS ITSELF FROM THE COMMITTED
FILES RATHER THAN TAKING THIS PARAGRAPH'S WORD** — this paragraph exists so
the prediction is falsifiable and attributed, exactly as `PREREG-2` 3.5's
`P-SEP` prediction was. **A single already-visible exceeding cell does not
by itself decide `P-C3b` for cells this Coordinator did not check** (`L9`,
`L11`, and `rawtail` everywhere) — those remain genuinely open per §3.2's
coverage audit, which this Coordinator did not complete (no shell; read-only
tool access only, itself not exhaustive).

---

## 5. GUARDS AND COULD-NOT-FAIL ARRANGEMENTS, NAMED BEFORE THE RUN

### 5.1 Could-not-fail check on `P-C3b`

Would hold if `D_route` were defined so large, or `s_c^fib` so small by
construction, that `"DOES NOT EXCEED"` were guaranteed regardless of measured
values. **WE ARE NOT IN IT:** `D_route` at the one already-visible `ROUTE-I`
cell class (`lam1n`/`hkz` at `L7`) is measured `0.0` (bit-identical), the
tightest possible value, and `s_c^fib` there is a genuinely measured non-zero
number from an unrelated computation (dispersion across 8 independently drawn
fibre bases) — there is no shared construction that forces the comparison's
direction. The reverse arrangement — `D_route` defined so large that
`"EXCEEDS"` could never fire — is also checked: `D_route` is a **measured** max
absolute deviation between two independently run pipelines on nominally
identical inputs, not a fixed constant, and `PREREG-1`/`PREREG-2`'s own history
in this goal (`OBS-1` of `EV-MLKEM-aa39ad`: `rdet`'s `T1` residual `3.865e-12`)
shows such residuals are measured near machine epsilon, not manufactured to be
large.

### 5.2 Could-not-PASS the coverage audit

Would hold if obligation 0 (§3.2) could not possibly find any valid `ROUTE-I`
regardless of what exists, e.g. because the read scope excludes the relevant
directories. **Guarded structurally:** the lead's `read_scope` in the dispatch
queue includes all of `coordination/goals/GOAL-MLKEM-005`, which contains
every batch this document names as a candidate `ROUTE-I` source.

---

## 6. OUTCOME ROWS

| row | what it records |
|---|---|
| `R-C-OUT-0` | obligation 0: the coverage table — 27 cells, valid `ROUTE-I` source path or `NONE FOUND`, `ROUTE-W` applicability for `rawtail`, and the `BATCH-cbe023` construction-comparability verdict |
| `R-C-OUT-1` | obligation 1: per covered cell, `s_c^fib`, `D_route`, matched-basis count, verdict, source path |
| `R-C-OUT-2` | obligation 2: `ALL-CLEAR` / `SOME-EXCEEDS`, coverage fraction, cell lists |
| `R-C-OUT-3` | the termination branch read off `R-C-OUT-0`/`R-C-OUT-2` under §3.5's precedence, with the `-PARTIAL` suffix applied per its own rule |
| `R-C-OUT-4` | RC-1: the frozen §1 text, carried verbatim, with the lead's own confirmation that it read the correction from `PREREG-3` and recomputed nothing |
| `R-C-OUT-5` | RC-2: the frozen §2 text, carried verbatim, with the same confirmation |

---

## 7. BINDING CARRIES — IN FORCE, NOT RE-LITIGATED

Carried in full from `PREREG-2` §10 and §10.1, without restatement of every
line here — the lead, the reviews and the ledger archive are bound by
`PREREG-2` §10/10.1 **exactly as `PREREG-2` itself states them**, plus the
following, specific to this batch:

* **`AM-3` IS NOT RETIRED.** `BATCH-a44d08` IS NOT RESCORED IN ANY RESPECT and
  its Section C verdict and detection floors stay VOID IN BOTH DIRECTIONS.
  `BATCH-4ed139`, `BATCH-9e3584`, `BATCH-cbe023` and `BATCH-6b6e78` are NOT
  REVALIDATED by anything in this batch, INCLUDING §3.2's read of
  `results_am4.json` and `results_l7l8.json`, which are read **only** to
  extract already-committed numbers, never to re-score their own batches'
  verdicts.
* **"A factor of 6 to 31" is FALSE; the citable range is 4.87x to 31.03x.**
  **"Genuinely cross-platform" is NOT citable**; the citable form is a
  PORTABILITY result across three textually distinct implementations with
  fpylll pinned at 0.6.4 — carried unchanged, and directly relevant here since
  `results_l7l8.json` is one of those three implementations.
* Any sub-threshold count in this goal must name all four axes (reading,
  normalization, boundary rule, threshold) plus its summation algorithm in
  the same sentence. Not otherwise triggered by this batch's own content, but
  binding if any prior number is quoted.
* `AM4-OBS-1` cited ONLY through `knowledge/findings/KN-FIND-f38a89.md`.
  `AM-9`: fpylll's `k` counts the q-scaled rows, NOT the identity block —
  directly relevant to §3.2's `results_am4.json` comparability check.
  THE `G-VAR` REFUSAL IS CITED ONLY AS CONDITIONAL ON THE FROZEN FAMILY `F0`.
* **`KN-FIND-7d098b` and `KN-FIND-9d44b4` ARE NOT RESTATED AS NEW.** Neither
  is this batch's producer credited with either finding's content.
* The split-producer notarization pattern is retained unchanged. The
  receipt-with-`commit_sha: null`-inside-its-own-commit archive pattern is
  MANDATORY. Every run emits durable `command.txt`, `stdout.log` and
  `stderr.log`, with no path inside a folded YAML scalar, and lists every
  path it wrote in its report.
* `knowledge/INDEX.md` must NOT be written, regenerated or staged.
* **`AGENTS.md` rule 12 is UNMET AND UNWAIVED.** Every producer and reviewer
  of this batch records `model_verified: false` with its reason, its host and
  its stack.
* **`PD-4` IS OPEN.** Each review's own report and probes sit uncommitted
  across a dispatch window and are the sole carriers of their own evidence
  until the ledger archive commits them.
* **CLAIM TIER STAYS TOY**, unconditionally, throughout.

---

## 8. SCOPE, INDEPENDENCE AND WHAT THIS BATCH CANNOT DO

**SCOPE.** `q = 3329`; `d in {20, 30, 40}` (`L7`, `L9`, `L11` ONLY — `L1`, `L2`,
`L4`, `L5`, `L8`, `L10`, `L12` are out of scope for this batch); the frozen
beta grids of §3.1; `N_BASES = 8`; `binary64` fibre dispersion only (this
batch does not evaluate `binary32` for these candidates — that two-precision
comparison remains out of scope exactly as `PREREG-2` 2.5 declared, because it
would require new reduction). **NO reduction of any kind is performed by this
batch, at any lattice, for any reason.** Every number this batch's lead
produces is either (i) read directly from an already-committed file, or (ii)
an elementary arithmetic function (max, absolute difference, comparison) of
numbers read that way. **Every conclusion is scoped to exactly that and
transports nowhere.**

**PART (c)'S OWN SCOPE, CARRIED AT EVERY QUOTATION.** This measurement says
nothing about `A-1`, about the in-scope candidates of `PREREG-2` 2.4, about
`X_gso_k`, or about any determinant-only candidate. It says nothing about
`ML-KEM`, any FIPS 203 parameter set, any attack cost, or any cost model. Its
`T-C3LANE-OPEN` branch, if it fires, licenses a bare statement that a domain
is worth stating — **not** a working assumption, **not** a criterion, and
**not** a claim that `lam1n`/`hkz`/`rawtail` are usable observables for `C3`.

**INDEPENDENCE IS PROCEDURAL AND NEVER MODEL-LEVEL.** `AGENTS.md` rule 12 is
UNMET AND UNWAIVED in this goal and is not waived here.

---

## 9. AUTHORSHIP GAP, DECLARED RATHER THAN NARRATED CLOSED

The Coordinator session that wrote this file **held no shell**. It ran no git
command and computed no hash. It DID read committed repository files directly
with a read-only tool (never a shell), and every number attributed to "this
Coordinator" above (`0.0434`, `0.0239`, `0.0106`, `5.808686864838819e-13`, the
`results_am4.json` key locations, the `TASK-20260812-0e930c` path) was read
that way from the exact cited path, not computed, not estimated, and not
carried from any prose summary. **This is a weaker claim than a measurement**:
it is one session's reading of one file at one point in time, offered so the
lead can check it independently, not offered as this batch's evidence. The
lead producer's own obligation 0 (§3.2) is the batch's actual, attributed
measurement of what the corpus contains.

`prereg_sha256.txt` is generated and committed by `TASK-20260813-6ad846`, by a
session that has a shell, exactly as `PREREG-2` 2.9's closing paragraph
required for its own hash file.

**END OF FROZEN TEXT.**
