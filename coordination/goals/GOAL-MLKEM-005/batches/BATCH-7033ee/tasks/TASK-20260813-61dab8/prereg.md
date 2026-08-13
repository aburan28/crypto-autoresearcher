# PREREG-4 — BATCH-7033ee FROZEN PRE-REGISTRATION

    goal        GOAL-MLKEM-005
    batch       BATCH-7033ee
    task        TASK-20260813-61dab8 (Coordinator, pre-registration only)
    notarized by TASK-20260813-30cdca (snapshot archive, runs alone, before any
                measuring task)
    authority   DEC-20260813-28d7b2 (the closing decision of BATCH-fbb639, whose
                `next_action` — ONE action in two parts that must travel
                together — this document discharges in full), applying the
                binding carries of PREREG-3 §7 (itself carrying PREREG-2 §10/10.1
                and AM-10..AM-18)
    claim tier  TOY, UNCONDITIONALLY

**THIS TEXT IS FROZEN AT NOTARIZATION AND IS NEVER EDITED.** A correction is a
superseding record under a new identifier, never an edit here. No measuring
task of BATCH-7033ee may be dispatched until this file is committed by
TASK-20260813-30cdca and that commit contains **zero** producer artifacts —
the split-producer notarization pattern, retained unchanged; it has now worked
seven times and has been verified in both directions by independent sessions
each time.

---

## 0. WHAT THIS BATCH DISCHARGES, AND WHY ITS PARTS TRAVEL TOGETHER

`DEC-20260813-28d7b2` closed `BATCH-fbb639` (decision `revise`; termination
branch `T-C3LANE-OPEN-PARTIAL` at 18 of 27 declared cells covered, `D_route =
0.0` exactly at every covered cell against strictly positive fibre dispersion,
so every covered cell verdicted `EXCEEDS`; both independent reviews
re-derived the full 27-cell audit from the frozen text with zero producer
import and confirmed the branch, robust under two stricter coverage
readings) and set **exactly one** `next_action`, in two parts that must travel
together in this successor pre-registration:

* **(a) DISCHARGE RT-2's required correction** — restate `R-C-OUT-0`'s
  coverage table for four named cells: `hkz/L9_b15` and `hkz/L11_b20` as
  genuinely `UNCOVERED` (not `COVERED`), and `hkz/L9_b22` / `hkz/L11_b30`
  with the corrected `TRUE` `beta_hi`-based `D_route` source, **numerically
  unchanged at `0.0`**. No new computation is required; both corrected
  values are already computed and reported in the Red Team's own probe
  (`probe_coverage_beta_mismatch.py` / `_output.json`), which this document
  reads and carries verbatim below.
* **(b) THE LEAD MEASUREMENT** — commission a **genuinely non-code-shared
  re-implementation** of `ROUTE-I` for `lam1n` and `hkz` at `L7` (`d=20`),
  `L9` (`d=30`) and `L11` (`d=40`), written **without importing or
  transcribing** `make_A`, `build_basis` or `hkz_profile` from
  `measure_am4.py` / `measure_relvar.py` / `replicate_l7l8.py` or any of
  their descendants, and re-run `PREREG-3` 3.3's exact `D_route` comparison
  against the **same** already-archived `ROUTE-P` values
  (`results_relvar.json`), at the **same** frozen lattices, betas and
  `N_BASES = 8` fibre family. No reduction above `d = 40`.

**(a) IS BOOKKEEPING AND IS FROZEN HERE AS A MECHANICAL CORRECTION.** It
requires no re-run, no new computation, and no judgement by the lead beyond
carrying the frozen text below into its own report verbatim, attributed to
this document. **(b) is the substantive measurement of this batch** and its
termination clause is frozen in full in §2 before any cell is measured.

**WHY THE TWO TRAVEL TOGETHER.** `DEC-20260813-28d7b2`'s rationale states:
(i) part (a) is a cheap, correct, already-computed defect, and deferring it
risks a successor citing the uncorrected 18/27 figure or the two
mislabelled-source cells — `PREREG-3` 3.2 designates `R-C-OUT-0` a
first-class deliverable; (ii) part (b) is the one thing that would let a
future batch cite `BATCH-fbb639`'s `EXCEEDS` verdicts **without**
`KN-FIND-9b5df0`'s code-sharing qualification — it is the decisive,
not-yet-run follow-up both `BATCH-fbb639` reviews independently named
(Validator L-1; Red Team's "Next concrete action" item 3); (iii) doing only
(a) would leave the goal's actual blocking uncertainty — whether the measured
fibre content of `lam1n`/`hkz` is a real signal or an artifact of this
corpus's universal code-sharing — untouched, which the Red Team's own
corpus-wide search (no non-target candidate with genuine, non-algebraically-
forced dispersion exists anywhere in this corpus) shows cannot be resolved
any other way inside the existing corpus. This document does (a) first, as a
prerequisite a reader of (b) must not have to reconstruct, then (b) in full.

---

## 1. RC-3 — THE COVERAGE-TABLE CORRECTION, FROZEN AND MECHANICAL

**BACKGROUND, READ FIRST.** `BATCH-fbb639`'s `report_c3lane.md` /
`results_c3lane.json` (`R-C-OUT-0`) reported 18 of 27 cells as `COVERED` by a
valid `ROUTE-I`. The Red Team's `probe_coverage_beta_mismatch.py` (committed
at `coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/reviews/
TASK-20260813-6ab893/probes/`) found that `measure_c3lane.py`'s
`basis0_bit_identical_check` reads `results_am4.json`'s `X_lo` field (the
`beta_lo` comparison) for **every** cell of a lattice's beta grid, rather
than the field matching each cell's own beta — because `results_am4.json`'s
own `REL1`-pair structure stores comparisons at only two betas per lattice
(`beta_lo`, `beta_hi`), not at the middle beta. `lam1n` is unaffected by this
defect (verified beta-independent by construction — `am4`'s `X_lo == X_hi`
exactly at both lattices — so reusing the `beta_lo` comparison for every beta
of a lattice is a legitimate read of the one true value, not a beta
mismatch). `hkz` **is** beta-dependent, so the defect has two distinct
effects on `hkz` cells only:

**FROZEN CORRECTION TEXT, TO BE CARRIED VERBATIM INTO THE LEAD'S REPORT:**

> `BATCH-fbb639`'s `R-C-OUT-0` coverage table is corrected at four `hkz`
> cells, per the Red Team's `probe_coverage_beta_mismatch_output.json`
> (`TASK-20260813-6ab893`), read directly and carried without recomputation:
>
> 1. **`hkz/L9_b15` and `hkz/L11_b20` are restated as genuinely
>    `UNCOVERED`, not `COVERED`.** Beta 15 (`L9`) and beta 20 (`L11`) are the
>    *middle* beta of each lattice's three-point grid and are **not**
>    `REL1`-pair endpoints in `results_am4.json` — `am4_has_a_genuine_value_
>    at_this_beta: false` for both, confirmed against that file's own
>    declared `beta_lo`/`beta_hi` fields (`L9`: lo=7, hi=22; `L11`: lo=10,
>    hi=30). The value `measure_c3lane.py` read and reported as this cell's
>    `ROUTE-I` comparison was in fact the `beta_lo` comparison of a
>    **different** beta, silently substituted with no genuine second-route
>    value existing for the cited beta.
> 2. **`hkz/L9_b22` and `hkz/L11_b30` are restated with the corrected `TRUE`
>    `beta_hi`-based `D_route` source.** Both cells *are* genuine `REL1`-pair
>    endpoints (`beta_hi`), but `measure_c3lane.py`'s check reads only
>    `am4_row['X_lo']` unconditionally, so the reported `D_route` for these
>    two `beta_hi` cells was in fact computed against the **wrong** endpoint
>    of the pair (the `beta_lo` value, not the `beta_hi` value the cell
>    itself is at). The corrected, genuinely-`beta_hi`-sourced comparison is:
>
>    | cell | am4 `X_hi` | relvar `X` (basis 0) | true `D_route` |
>    |---|---|---|---|
>    | `hkz/L9_b22`  | -0.11249180258058367 | -0.11249180258058367 | 0.0 |
>    | `hkz/L11_b30` | -0.13095122117764646 | -0.13095122117764646 | 0.0 |
>
>    **`D_route` is numerically unchanged at exactly `0.0` for both cells**
>    under the corrected source — this is a **provenance-labelling**
>    correction (which stored value was cited as the cell's comparison), not
>    a correction that changes any reported number or verdict.
>
> **Corrected coverage fraction.** `lam1n`'s 9 cells are unaffected by this
> correction (all remain `COVERED` at 9/9, per the beta-independence
> argument above). `hkz`'s corrected coverage is 7 of 9 cells (`L7` b5/b10/
> b15; `L9` b7, b22; `L11` b10, b30), with `hkz/L9_b15` and `hkz/L11_b20`
> restated `UNCOVERED`. The corrected total across `lam1n` + `hkz` is **16 of
> 18**, not 18 of 18 as `BATCH-fbb639` reported (`rawtail`'s coverage —
> `ROUTE-W` only, never counted — is untouched by this correction).
>
> **This supersedes `BATCH-fbb639`'s `R-C-OUT-0` coverage table at exactly
> these four cells and its "18 of 27" coverage-fraction statement wherever
> quoted without this correction in the same sentence. It does not change
> `results_c3lane.json`'s `D_route` value at any cell, and it does not
> change the fired termination branch.**

**EFFECT ON THE FIRED TERMINATION BRANCH — STATED, NOT RE-ARGUED.** Per the
Red Team's own probe output, `T-C3LANE-OPEN-PARTIAL` still fires after this
correction: 16 genuinely-covered cells (all 9 `lam1n` cells plus `hkz`'s 7
genuinely-covered cells) still show `EXCEEDS`, `SOME-EXCEEDS` still holds
over the corrected `COVERED` set, and the `-PARTIAL` suffix was already
applicable at 18/27 and remains applicable at the corrected, smaller
coverage count. **This correction narrows and corrects the coverage table;
it does not overturn the branch, and this document does not re-litigate
that conclusion** — it is carried here as background so RC-3's scope is
clear, and restated as committed, citable text by this batch's ledger
archive exactly as `PREREG-3` 3.7 required for RC-1/RC-2.

**NO RE-RUN IS REQUIRED, AND NONE IS PERMITTED HERE.** `measure_c3lane.py`,
`results_c3lane.json` and `report_c3lane.md` are **immutable committed
artifacts** (`TASK-20260813-7b3039`, archived at `TASK-20260813-7ac7cd`) and
are **not edited, not re-run, and not vendored**. The lead producer of this
batch carries the frozen text above into its own report **by quotation**,
attributed to `PREREG-4` §1, and does **not** recompute anything for RC-3.

**THE LEDGER ARCHIVE'S OBLIGATION FOR RC-3**, exactly as `PREREG-3` 3.7
required for RC-1/RC-2: this batch's ledger archive must carry §1's frozen
correction text into a new evidence and/or decision record so it exists as
committed, citable ledger text and not only inside this pre-registration.

---

## 2. PART (b) — THE LEAD MEASUREMENT: A GENUINELY NON-CODE-SHARED `ROUTE-I2`

### 2.0 What is being asked, restated precisely

`KN-FIND-9b5df0` (promoted at `BATCH-fbb639`'s own ledger archive) shows that
`BATCH-fbb639`'s named `ROUTE-I` is **not algorithmically independent** of
`ROUTE-P`: `make_A`, `build_basis` and `hkz_profile` are shared **verbatim**
across `measure_am4.py` → `measure_relvar.py` → `replicate_l7l8.py`
(self-declared "CARRIED VERBATIM" in each downstream docstring), and for
`L7` the two "routes" additionally ran on the **same host**. `D_route = 0.0`
at all 18 (16, corrected) covered cells is therefore evidence of **same-code,
cross-environment reproducibility**, not of independent-algorithm
cross-validation — this changes no number and not the fired branch, but
qualifies its license.

Part (b) asks the **narrower, sharper** question `KN-FIND-9b5df0` leaves
open: **under a re-implementation that shares no code with `ROUTE-P`'s
kernel, does `D_route` stay near machine epsilon (supporting that the
`EXCEEDS` verdicts reflect real, independently-confirmable fibre dispersion),
or does it grow toward `s_c^fib`'s scale (indicating the `EXCEEDS` verdicts
were an artifact of comparing one implementation against itself)?** This is
**not** a new dispersion criterion, **not** a gate, and **not** a
replacement for `PREREG-3`'s part (c) (§3 below states why in full). It is a
diagnostic measurement of the exact same numerical quantities `PREREG-3`
already froze, run through a second, independently-written kernel.

### 2.1 Frozen objects — carried from PREREG-3 §3.1, restated for this batch

    q          = 3329                          (carried, PREREG-1 2.1)
    N_BASES    = 8                              (basis index i = 0..7, carried)
    Lattices and beta grids IN SCOPE, and ONLY these:
        L7  (d=20, k=6)    beta grid {5, 10, 15}
        L9  (d=30, k=9)    beta grid {7, 15, 22}
        L11 (d=40, k=12)   beta grid {10, 20, 30}
    Candidates IN SCOPE for this batch, and ONLY these two:
        lam1n, hkz     (rawtail is OUT OF SCOPE for part (b) — no ROUTE-I of
                        any kind is known to exist for it in this corpus, per
                        PREREG-3 3.1/3.2, and this batch does not attempt to
                        build one; ROUTE-W, if cited, remains labelled and
                        never counted, exactly as PREREG-3 froze it)

    THE FROZEN F0 BASIS CONSTRUCTION, restated here as a MATHEMATICAL
    SPECIFICATION (never a code excerpt) so the lead can implement it fresh
    without transcribing measure_relvar.py:
        For lattice (d, k) and basis index i in {0..7}:
          A_i  = an integer matrix, k rows x (d-k) columns, whose entries are
                 drawn i.i.d. uniform on {0, 1, ..., q-1}, using
                 numpy.random.default_rng([1, d, k, i]).integers(0, q,
                 size=(k, d-k), dtype=np.int64) AS THE FROZEN, DECLARED
                 SOURCE OF RANDOMNESS (PREREG-1 2.2/2.3's F0; this seed
                 formula is a FROZEN INPUT SPECIFICATION, not the algorithm
                 under test, and using it exactly is REQUIRED so ROUTE-I2
                 measures the SAME basis as ROUTE-P, not a different one).
          B_i  = the d x d integer matrix
                     [ I_k    A_i  ]
                     [ 0   q * I_{d-k} ]
                 in EXACT integer arithmetic (never float, never a generator
                 approximation).
        THE LEAD MUST WRITE ITS OWN CODE THAT REALIZES THIS SPECIFICATION
        (e.g. by calling numpy.random.default_rng directly and assembling the
        block matrix itself) RATHER THAN IMPORTING OR COPYING make_A /
        build_basis FROM ANY COMMITTED FILE. Producing a bit-identical B_i
        this way is EXPECTED and is not itself evidence of code-sharing — it
        is what correctly implementing the same public formula from its own
        prose specification looks like.

    THE TWO OBSERVABLES, restated as MATHEMATICAL DEFINITIONS (read directly
    by this Coordinator from measure_relvar.py's committed source, cited so
    the lead can verify independently, and stated here as formulas to
    implement fresh, never as code to copy):
        Let B_i be reduced by ANY genuinely independent HKZ-style reduction
        and enumeration procedure (see 2.2 below) to obtain, for each GSO
        index j = 0..d-1, the squared Gram-Schmidt norm r_j = ||b*_j||^2 of
        the REDUCED basis, satisfying the HKZ property (each r_j is the
        minimum squared norm achievable in the j-th projected sublattice,
        i.e. r_j <= lambda_1(pi_j(L))^2 for every j, up to the enumeration
        procedure's own reported tolerance/violation).
        logdet   = 0.5 * sum_j( ln(r_j) )
        lam1n    = exp( 0.5*ln(r_0) - logdet/d )              [beta-independent]
        hkz(beta)= mean_{j >= d-beta}( 0.5*ln(r_j) ) - logdet/d

    ROUTE-P  ("primary / committed pipeline route") — UNCHANGED from PREREG-3
             3.1: the value of candidate X at lattice L, beta b, basis i as
             already computed and committed by measure_relvar.py
             (BATCH-9e3584, results_relvar.json), READ, never recomputed.
             THE EXACT LOCATION OF THE PER-BASIS ROUTE-P VALUE, VERIFIED BY
             THIS COORDINATOR'S OWN READ OF THE COMMITTED FILE (attributed,
             not measured by this document): results_relvar.json's
             G_REL2 block stores per-basis, per-beta values for BOTH lam1n
             and hkz at all three betas of every lattice pair (L7/L8,
             L9/L10, L11/L12), under
                 rel2["lam1n"]["<Lx>/<Ly>"]["<beta>"]["per_basis"][i]["X_a"]
                 rel2["hkz"]["<Lx>/<Ly>"]["<beta>"]["per_basis"][i]["X_a"]
             (X_a is the L7/L9/L11-side member of each mirrored pair; X_b is
             the L8/L10/L12-side mirror partner and is OUT OF SCOPE for this
             batch, exactly as PREREG-3 excluded L8/L10/L12). THIS GIVES FULL
             18-CELL (2 candidates x 3 lattices x 3 betas) ROUTE-P COVERAGE —
             wider than PREREG-3's own part (c), which additionally needed a
             ROUTE-I at the middle beta and found none; ROUTE-I2 (below) is
             commissioned exactly to fill that gap with a genuine second
             route rather than PREREG-3's substitute-source workaround.
             THE LEAD MUST VERIFY THIS LOCATION AND EVERY VALUE ITSELF
             (obligation 0, §2.3) RATHER THAN TRUST THIS PARAGRAPH.

    ROUTE-I2 ("genuinely independent second route") — THE NEW OBJECT THIS
             BATCH COMMISSIONS: lam1n and hkz at L7, L9, L11, all three betas
             each, all 8 fibre bases each, computed by a NEWLY WRITTEN
             implementation satisfying §2.2's independence requirements.
             THIS DOES NOT YET EXIST. It is the lead's deliverable, not an
             already-archived value.

    Fibre dispersion at binary64, s_c^fib(X, L, b) — UNCHANGED from PREREG-3
             3.1: the ALREADY-ARCHIVED float_sd value at
             results_relvar.json.per_candidate.<X>.per_cell.<L>_<b>.float_sd,
             sd over the N_BASES = 8 fibre-family bases. READ, never
             recomputed.

### 2.2 Independence requirements for ROUTE-I2 — BINDING, CHECKED BY BOTH REVIEWS

1. **NO IMPORT, NO TRANSCRIPTION.** The lead's implementation of basis
   construction and of the reduction/enumeration pipeline that produces
   `r_j` must not import, `exec`, copy-paste, or mechanically transliterate
   `make_A`, `build_basis` or `hkz_profile` (or any helper each of them
   calls: `gram_int`, the `fpylll` `Strategy`/`BKZReduction`/`Enumeration`
   call sequence as sequenced in `measure_relvar.py`) from `measure_am4.py`,
   `measure_relvar.py`, `replicate_l7l8.py`, or any file that itself carries
   any of those functions verbatim. Writing fresh code that implements the
   **same public mathematical formula** (§2.1's basis specification) is
   REQUIRED, not merely permitted, for the basis; for the reduction and
   enumeration step, a **different algorithmic path** is required — a
   different reduction library (e.g. not `fpylll`, or a different call
   sequence within it if no alternative library is available in this
   environment), or a from-scratch LLL + local-block enumeration routine
   written for this task, is explicitly stated by the goal record's
   `next_action` to be **sufficient** at this scale (`d <= 40`).
2. **A DIFFERENT ALGORITHMIC PATH, NOT MERELY A DIFFERENT FILE.** Re-running
   `measure_relvar.py`'s own functions from a new driver script, or copying
   its `fpylll` call sequence into a differently-named function, does
   **not** satisfy this requirement — this is exactly the pattern
   `KN-FIND-9b5df0` found and disqualified for `ROUTE-I`. The lead's report
   must state, explicitly, which algorithmic choices differ from the
   `hkz_profile` pipeline (e.g.: different LLL delta, different block
   enumeration strategy, a different or no `fpylll` dependency, a
   differently-ordered reduction loop) — a report that cannot name at least
   one genuine algorithmic difference has not discharged this obligation.
3. **THE SAME FROZEN INPUT.** `ROUTE-I2` must consume the **same** `B_i`
   `PREREG-1` 2.2/2.3's `F0` specifies (§2.1) — using a different basis
   would make any resulting agreement or disagreement uninterpretable
   against `ROUTE-P`. Matching `B_i` is checked by construction (same public
   seed formula) and is not itself a code-sharing violation (§2.1's own
   text states why).
4. **HKZ, NOT MERELY LLL/BKZ-REDUCED.** `hkz_profile`'s own docstring states
   that `fpylll`'s `svp_call` alone does not reach true HKZ and requires an
   independent per-index enumeration reporting `hkz_violation`. `ROUTE-I2`'s
   implementation must likewise report, per basis and lattice, a violation
   or optimality diagnostic for its own reduction (however it is computed)
   so a reviewer can judge whether `r_j` is close enough to the true HKZ
   profile for the comparison in §2.4 to be meaningful, and must report this
   diagnostic **even if it differs in kind** from `hkz_violation`.
5. **NO NEW REDUCTION ABOVE `d = 40`.** Matches `PREREG-3`'s own scope
   exactly. `L7`, `L9`, `L11` only; no `L1`, `L2`, `L4`, `L5`, `L8`, `L10`,
   `L12`.
6. **DISCLOSURE OF PROVENANCE.** The lead's report states, for every
   dependency it installs or imports (reduction library, enumeration
   routine, RNG), its exact name and version, and confirms none of them is
   `fpylll` version-pinned to reproduce `measure_relvar.py`'s own
   environment unless a genuinely different call path within it is used and
   named per requirement 2.

### 2.3 Obligation 0 — verify ROUTE-P, BEFORE ROUTE-I2 is built

**THE LEAD'S FIRST ACT.** Before writing any reduction code, the lead reads
(not recomputes) `results_relvar.json`'s `G_REL2` block and independently
confirms, for `lam1n` and `hkz`, all 18 cells (`L7`/`L9`/`L11` x 3 betas
each) have a per-basis `ROUTE-P` value at `X_a` for all 8 fibre bases,
reporting the exact JSON path used and any cell (if any) where a per-basis
value is missing, `null`, or the `per_basis` array has fewer than 8 entries.
**A search that finds full coverage is reported as having found it; a
search that finds a gap is reported as a gap, never silently patched.** This
mirrors `PREREG-3` 3.2's obligation-0 discipline exactly, applied to the
`ROUTE-P` side rather than the (not-yet-existing) `ROUTE-I` side, because
`ROUTE-I2` does not exist yet for this batch's coverage audit to search for.

### 2.4 Obligation 1 — implement ROUTE-I2 and compute the comparison

For every one of the 18 cells (`lam1n`/`hkz` x `L7`/`L9`/`L11` x each
lattice's 3-beta grid), for every one of the 8 fibre bases:

1. Build `B_i` per §2.1's specification.
2. Reduce `B_i` and enumerate to obtain `r_j` per §2.2's independence
   requirements, reporting the violation/optimality diagnostic per basis.
3. Compute `lam1n` and `hkz(beta)` per §2.1's formulas.
4. Report the resulting `ROUTE-I2` value alongside the `ROUTE-P` value read
   in obligation 0, and

       D_route_independent(X, L, b) = max over the 8 matched bases i
                                       of | X_ROUTE-P(L, b, i) - X_ROUTE-I2(L, b, i) |

       VERDICT(X, L, b) = "EXCEEDS"        if s_c^fib(X, L, b) >  D_route_independent(X, L, b)
                         = "DOES NOT EXCEED" if s_c^fib(X, L, b) <= D_route_independent(X, L, b)

   using the **same** tie rule as `PREREG-3` 3.3 (a tie is `"DOES NOT
   EXCEED"`) and the **same** `s_c^fib` source (`results_relvar.json`'s
   `float_sd`, read, never recomputed).

If any of the 18 cells cannot be computed (timeout, dependency failure,
numerical breakdown flagged by the reduction's own diagnostic), report it as
`UNCOVERED` for `ROUTE-I2`, with the reason — **never** as a comparison
value, and **never** silently omitted from the coverage count.

### 2.5 Obligation 2 — the aggregate comparison against ROUTE-P and against PREREG-3's ROUTE-I

Report, once obligation 1 completes:

1. The count and list of the 18 cells where `D_route_independent` was
   successfully computed (`COVERED2`), and its complement (`UNCOVERED2`).
2. Over `COVERED2`: the count of `"EXCEEDS"` vs. `"DOES NOT EXCEED"` cells,
   and the full per-cell table (`D_route_independent`, `s_c^fib`, verdict).
3. **A direct numerical comparison, per cell, of `D_route_independent`
   against `PREREG-3`'s own `D_route` (`0.0`, or the RC-3-corrected `0.0`
   value at the two relabelled cells) at the same cell where both exist** —
   reporting whether the genuinely independent route's disagreement is of
   the same order (near machine epsilon, `1e-12`..`1e-15` scale, consistent
   with `EV-MLKEM-aa39ad` `OBS-1`'s own `rdet` residual `3.865e-12`), or
   materially larger, at each cell.
4. The overall summary statistic: `max` and `median` of `D_route_independent`
   over `COVERED2`, and the same over `s_c^fib` at the same cells, so a
   reader can see both distributions side by side without recomputing them.

### 2.6 THE FROZEN TERMINATION CLAUSE FOR PART (b)

**Exactly one of the following three fires, in this precedence order.**

**T-INDEP-NODATA** — **FIRES WHEN** `COVERED2` is empty (no cell of the 18
could be computed by `ROUTE-I2` — e.g. because no reduction library or
enumeration routine could be brought up in this environment within budget,
or every attempt hit the diagnostic's own breakdown flag). **MEANS:** a
genuinely independent second route could not be built or run this batch, for
infrastructure reasons — this is `AGENTS.md` rule 5 territory: **never**
read as evidence about `lam1n`/`hkz`'s dispersion in either direction.
**LICENSES:** a decision recording this as an infrastructure/tooling gap and
naming what a successor would need (a specific missing dependency, a longer
budget, or a different-still algorithmic path) before this measurement
becomes runnable; `KN-FIND-9b5df0`'s qualification remains exactly as
written, neither strengthened nor discharged. **FORBIDS:** any claim that
the `EXCEEDS` verdicts are or are not artifacts; closing, pausing or
completing `GOAL-MLKEM-005`; flagging any `BATCH-fbb639` cell's verdict as
methodologically unsupported (§2.7's revisit condition is **not** triggered
by `NODATA` — there is no measurement to trigger it).

**T-INDEP-CONFIRMS** — **FIRES WHEN** `COVERED2` is non-empty and, over
`COVERED2`, `D_route_independent` stays **at or near machine epsilon**
(operationally: every cell's `D_route_independent <= 1e-8`, four orders of
magnitude below the smallest `s_c^fib` value reported anywhere in
`results_relvar.json`'s `per_candidate` block for `lam1n`/`hkz` at these
lattices, so no genuine ambiguity is created at this specific threshold —
the lead reports the exact smallest such `s_c^fib` value alongside this
check so the margin is checkable, not asserted) — i.e. essentially the same
scale as `PREREG-3`'s already-archived route-disagreement figures, under
genuine algorithmic independence this time. **MEANS:** the observables are
numerically well-behaved under a second, independently-written kernel; the
`EXCEEDS` verdicts `BATCH-fbb639` reported survive independent verification
at the cells checked. **LICENSES:** a statement, citable without
`KN-FIND-9b5df0`'s qualification **for exactly the cells this batch
covered**, that `lam1n`/`hkz`'s measured fibre dispersion at those cells
exceeds two independently computed routes' disagreement — discharging
`BATCH-fbb639`'s central-finding qualification **for the cells checked, and
no others**. **FORBIDS:** extending this to `rawtail` (no `ROUTE-I2` was
built for it); extending this to any cell `ROUTE-I2` did not cover; any
claim about `ML-KEM`, any FIPS 203 parameter set, any attack cost or cost
model; closing, pausing or completing `GOAL-MLKEM-005`.

**T-INDEP-UNDERMINES** — **FIRES WHEN** `COVERED2` is non-empty and, over
`COVERED2`, `D_route_independent` grows toward `s_c^fib`'s own scale at **at
least one** covered cell (operationally: `D_route_independent >= 0.1 *
s_c^fib` at that cell, or the cell's `VERDICT` under §2.4 flips from
`"EXCEEDS"` to `"DOES NOT EXCEED"` relative to `PREREG-3`'s reported verdict
— either condition is independently sufficient and the lead reports which
fired). **MEANS:** the `EXCEEDS` verdict `BATCH-fbb639` reported at that
cell was a methodological artifact of comparing one code path against
itself, not a finding about `lam1n`/`hkz`'s own dispersion. **LICENSES:** a
superseding record, per §2.7's revisit condition, flagging that specific
`BATCH-fbb639` cell's `EXCEEDS` verdict as methodologically unsupported —
and **only** that cell (or cells), never every covered cell by association.
**FORBIDS:** treating this as evidence that `A-1` (in-scope candidates) is
affected — `lam1n`/`hkz`/`rawtail` remain out of `A-1`'s scope entirely, per
`PREREG-2` 2.5; retroactively changing `T-C3LANE-OPEN-PARTIAL`, which
remains `BATCH-fbb639`'s own, correctly-read, frozen-clause outcome; any
claim about `ML-KEM`, any FIPS 203 parameter set, any attack cost or cost
model; closing, pausing or completing `GOAL-MLKEM-005`.

**THE `-PARTIAL` SUFFIX**, applied to whichever of `T-INDEP-CONFIRMS` /
`T-INDEP-UNDERMINES` fires, **WHENEVER** `|COVERED2| < 18`. The suffixed
branch reports the substantive result over `COVERED2` **and** the coverage
fraction **and** the list of uncovered cells with reasons, none of which is
decided in either direction. **A cell `ROUTE-I2` could not compute is never
read as `CONFIRMS` or `UNDERMINES` by default — it is `UNCOVERED2`, full
stop.**

**PRECEDENCE, STATED EXPLICITLY.** `T-INDEP-NODATA` dominates (fires alone,
with no `-PARTIAL` suffix — there is nothing partial about zero coverage).
Between `T-INDEP-CONFIRMS` and `T-INDEP-UNDERMINES`, a single cell firing
`UNDERMINES`'s condition is **sufficient** to fire `T-INDEP-UNDERMINES` and
**prevents** `T-INDEP-CONFIRMS` from being read over the whole `COVERED2`
set — matching this goal's established convention (`PREREG-3` 3.5: a single
exceeding cell is sufficient to fire the less favourable-to-closure branch)
applied to this measurement's two possible readings. A batch may therefore
report `T-INDEP-UNDERMINES-PARTIAL` at one cell while `T-INDEP-CONFIRMS`
would otherwise describe the rest — in that case `T-INDEP-UNDERMINES-PARTIAL`
is the branch that fires for the whole batch, and the report states,
per-cell, which cells individually confirm and which individually undermine,
so no information is lost inside the aggregate branch name.

### 2.7 THE REVISIT CONDITION — declared now so it binds a later session

Carried verbatim from `ledger/goals/GOAL-MLKEM-005.yaml`'s `next_action`: if
part (b) shows `D_route_independent` growing toward `s_c^fib`'s scale at any
cell under genuine independence (i.e. `T-INDEP-UNDERMINES` fires at that
cell), that cell's `EXCEEDS` verdict from `BATCH-fbb639` **must** be flagged
as methodologically unsupported in a superseding record, and no successor
may cite it without that flag. **This does NOT retroactively change
`T-C3LANE-OPEN-PARTIAL`**, which remains `BATCH-fbb639`'s own,
correctly-read, frozen-clause outcome — the flag qualifies what that outcome
is entitled to support at the affected cell, exactly as `KN-FIND-9b5df0`
already qualifies it at every covered cell, and does not undo it.

### 2.8 WHY `PREREG-2` 7.5'S REPAIR BAR DOES NOT APPLY HERE — STATED EXPLICITLY

Exactly as `PREREG-3` 3.6 stated for its own part (c), and for the same
three structural reasons:

1. **It specifies no criterion, clause or gate.** §2.6's branches license
   either a scope-limited confirmation (citable only at the cells checked)
   or a scope-limited flag on a **specific prior cell's verdict** — never a
   threshold, a pass/fail rule, or anything a future candidate is scored
   against.
2. **It re-measures an existing measurement's second route, not a new
   dispersion criterion.** `PREREG-3`'s part (c) already asked "does
   dispersion exceed route disagreement"; part (b) asks "is the reported
   route disagreement itself trustworthy," a question about **instrument
   validity**, not about a new candidate class or a new gate.
3. **Its outcome, at best, discharges an existing qualification; at worst,
   it narrows an existing verdict to a named cell.** Neither outcome
   proposes, extends, or repairs any gate — `A-1` is untouched either way.

**THIS IS NOT A GATE-REPAIR BATCH AND DOES NOT ADVANCE ANY CONSECUTIVE-
GATE-REPAIR COUNT.**

---

## 3. PREDICTION REGISTER

**Both items below were OPEN at the moment of notarization.**

| id | statement | falsifier | class | open at notarization |
|---|---|---|---|---|
| P-I2a | `COVERED2` is non-empty (at least one of the 18 cells yields a computed `ROUTE-I2` value) | `COVERED2` is empty (`T-INDEP-NODATA`) | PREDICTION | OPEN |
| P-I2b | over `COVERED2`, `D_route_independent` stays near machine epsilon at every cell (`T-INDEP-CONFIRMS`, no `-PARTIAL` exception firing `UNDERMINES`) | at least one covered cell fires `T-INDEP-UNDERMINES`'s condition | PREDICTION | OPEN |

**THIS COORDINATOR STATES NO ATTRIBUTED BASIS FOR EITHER DIRECTION OF
P-I2b**, unlike `PREREG-3` 3.4's `P-C3b` (which had an already-visible
comparison to cite). No `ROUTE-I2` value exists anywhere in the committed
corpus at the time this document is written — this is a genuinely open
question about a measurement that has never been run, not a restatement of
an already-visible number. **This is stated so a later reader does not
mistake §2's careful specification for a disguised prediction of its own
outcome.**

---

## 4. GUARDS AND COULD-NOT-FAIL ARRANGEMENTS, NAMED BEFORE THE RUN

### 4.1 Could-not-fail check on P-I2b

Would hold if `D_route_independent`'s threshold in §2.6 were set so loosely
that `T-INDEP-CONFIRMS` were guaranteed regardless of measured values, or so
tightly that `T-INDEP-UNDERMINES` were guaranteed. **Checked:** the
`1e-8`/`10%`-of-`s_c^fib` thresholds in §2.6 are chosen relative to two
**independently sourced** reference points fixed **before** any `ROUTE-I2`
number exists — `EV-MLKEM-aa39ad` `OBS-1`'s already-archived `rdet` residual
(`3.865e-12`, four orders below `1e-8`) as the "near machine epsilon" anchor,
and `results_relvar.json`'s own smallest reported `s_c^fib` for `lam1n`/`hkz`
at these lattices as the "same scale as dispersion" anchor — neither of
which this document computed from `ROUTE-I2` itself, so the threshold cannot
have been tuned to a `ROUTE-I2` outcome that did not yet exist.

### 4.2 Could-not-run check on the independence requirement

Would hold if no alternative reduction path were available in this
environment at all, forcing a disguised re-use of `fpylll`'s exact call
sequence. **Guarded structurally, not assumed:** §2.2 requirement 1
explicitly permits a from-scratch LLL + local-block enumeration routine
written for this task as sufficient at `d <= 40`, so the independence
requirement is satisfiable **without any new external dependency**, at the
cost of the lead writing more of the reduction pipeline itself; if the lead
nonetheless cannot satisfy §2.2 within budget, `T-INDEP-NODATA` is the
correctly frozen outcome, not a disguised repetition of `ROUTE-I`.

---

## 5. OUTCOME ROWS

| row | what it records |
|---|---|
| `R-B-OUT-0` | RC-3: the frozen §1 correction text, carried verbatim, with the lead's own confirmation that it read the correction from `PREREG-4` and recomputed nothing |
| `R-B-OUT-1` | obligation 0 (§2.3): the `ROUTE-P` verification table — 18 cells, `G_REL2` path, per-basis coverage confirmed or a named gap |
| `R-B-OUT-2` | obligation 1 (§2.4): per cell, `ROUTE-I2`'s value at every basis, `D_route_independent`, `s_c^fib`, verdict, and the reduction diagnostic |
| `R-B-OUT-3` | obligation 2 (§2.5): the `COVERED2`/`UNCOVERED2` split, the aggregate comparison against `PREREG-3`'s `D_route`, and the summary statistics |
| `R-B-OUT-4` | the termination branch read off `R-B-OUT-1`..`R-B-OUT-3` under §2.6's precedence, with the `-PARTIAL` suffix applied per its own rule |
| `R-B-OUT-5` | if `T-INDEP-UNDERMINES` fired at any cell: the exact cell list to be flagged under §2.7's revisit condition (this row is empty, and reported as empty, if it did not fire) |

---

## 6. BINDING CARRIES — IN FORCE, NOT RE-LITIGATED

Carried in full from `PREREG-3` §7 (itself carrying `PREREG-2` §10/10.1),
without restatement of every line here — the lead, the reviews and the
ledger archive are bound by `PREREG-3` §7 **exactly as it states**, plus the
following, specific to this batch:

* **`AM-3` IS NOT RETIRED.** `BATCH-a44d08` IS NOT RESCORED IN ANY RESPECT.
  `BATCH-4ed139`, `BATCH-9e3584`, `BATCH-cbe023`, `BATCH-6b6e78` and
  `BATCH-fbb639` are NOT REVALIDATED by anything in this batch, INCLUDING
  §2.3's read of `results_relvar.json`'s `G_REL2` block, which is read
  **only** to extract already-committed per-basis numbers, never to
  re-score `BATCH-9e3584`'s own verdicts. `T-C3LANE-OPEN-PARTIAL` is not
  reopened; only its qualification (`KN-FIND-9b5df0`) is what part (b)
  addresses.
* **`KN-FIND-9b5df0` IS NOT RESTATED AS NEW**, and this batch's producer is
  not credited with its content — this batch is the **response** to it, not
  a restatement of it. `KN-FIND-7d098b` and `KN-FIND-9d44b4` remain likewise
  not restated.
* Any sub-threshold count in this goal must name all four axes (reading,
  normalization, boundary rule, threshold) plus its summation algorithm in
  the same sentence. Not otherwise triggered by this batch's own content,
  but binding if any prior number is quoted.
* "A factor of 6 to 31" is FALSE; the citable range is 4.87x to 31.03x.
  "Genuinely cross-platform" is NOT citable; the citable form is a
  PORTABILITY result across three textually distinct implementations with
  `fpylll` pinned at 0.6.4 — and this batch's own `ROUTE-I2`, if it uses
  `fpylll` at all, must NOT be described as "cross-platform" on that basis
  alone; the operative property this batch requires is algorithmic
  independence (§2.2), not merely a different host or a different pin.
* The split-producer notarization pattern is retained unchanged. The
  receipt-with-`commit_sha: null`-inside-its-own-commit archive pattern is
  MANDATORY. Every run emits durable `command.txt`, `stdout.log` and
  `stderr.log`, with no path inside a folded YAML scalar, and lists every
  path it wrote in its report.
* `knowledge/INDEX.md` must NOT be written, regenerated or staged.
* **`AGENTS.md` rule 12 is UNMET AND UNWAIVED.** Every producer and reviewer
  of this batch records `model_verified: false` with its reason, its host
  and its stack.
* **`PD-4` IS OPEN.** Each review's own report and probes sit uncommitted
  across a dispatch window and are the sole carriers of their own evidence
  until the ledger archive commits them.
* **CLAIM TIER STAYS TOY**, unconditionally, throughout.

---

## 7. SCOPE, INDEPENDENCE AND WHAT THIS BATCH CANNOT DO

**SCOPE.** `q = 3329`; `d in {20, 30, 40}` (`L7`, `L9`, `L11` ONLY);
candidates `lam1n` and `hkz` ONLY (`rawtail` is out of scope for part (b));
the frozen beta grids of §2.1; `N_BASES = 8`; `binary64` only. **NO
reduction above `d = 40` is performed by this batch, at any lattice, for any
reason.** Every `ROUTE-P` number this batch's lead reads is read directly
from an already-committed file; every `ROUTE-I2` number is a fresh
computation under §2.2's independence requirements; every comparison is an
elementary arithmetic function (max, absolute difference, comparison) of
those two kinds of numbers. **Every conclusion is scoped to exactly that and
transports nowhere.**

**PART (b)'S OWN SCOPE, CARRIED AT EVERY QUOTATION.** This measurement says
nothing about `A-1`, about the in-scope candidates of `PREREG-2` 2.4, about
`X_gso_k`, about `rawtail`, or about any determinant-only candidate. It says
nothing about `ML-KEM`, any FIPS 203 parameter set, any attack cost, or any
cost model. `T-INDEP-CONFIRMS`, if it fires, licenses citing `EXCEEDS`
**without** `KN-FIND-9b5df0`'s qualification **only at the cells this batch
covered** — never at `rawtail`, never above `d = 40`, and never as a claim
that independence has been established for any observable this batch did
not measure.

**INDEPENDENCE IS PROCEDURAL AND NEVER MODEL-LEVEL.** `AGENTS.md` rule 12 is
UNMET AND UNWAIVED in this goal and is not waived here. **ALGORITHMIC
independence of `ROUTE-I2` from `ROUTE-P` (§2.2) is a DIFFERENT axis from
SESSION/MODEL independence of the reviews from the producer — both are
tracked, and satisfying one says nothing about the other.**

---

## 8. AUTHORSHIP GAP, DECLARED RATHER THAN NARRATED CLOSED

The Coordinator session that wrote this file held a read-only file-access
tool (`Read`/`Grep`) and a shell (used only for `git fetch`/`merge`, ID
minting via `tools/allocate_id.py`, and inspection commands — never to
compute a measurement, run a reduction, or install a dependency for this
batch's substantive content). Every number attributed to "this Coordinator"
above (`-0.11249180258058367`, `-0.13095122117764646`, the `G_REL2` JSON
path structure, the `lam1n`/`hkz` formulas, the `3.865e-12` anchor) was read
directly from the cited committed file at the cited path, not computed, not
estimated, and not carried from any prose summary — **this is a weaker
claim than a measurement**: it is one session's reading of committed files
at one point in time, offered so the lead can check it independently, not
offered as this batch's evidence. The lead producer's own obligations 0-2
(§2.3-2.5) are the batch's actual, attributed measurement.

`prereg_sha256.txt` is generated and committed by `TASK-20260813-30cdca`, by
a session that has a shell, exactly as `PREREG-2` 2.9's closing paragraph
required and `PREREG-3` §9 carried forward for its own hash file.

**END OF FROZEN TEXT.**
