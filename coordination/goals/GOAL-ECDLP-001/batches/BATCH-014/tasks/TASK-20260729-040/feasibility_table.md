# TASK-20260729-040 — EXP-STR-004 feasibility table

**Mandated by** the BATCH-014 execution gate (`RC-14`, pre-freeze requirement:
"A FEASIBILITY TABLE IS MANDATORY (DEFER-BATCH009-003 carried)") and by
constraint "WRITE THE FEASIBILITY TABLE" of the `TASK-20260729-040` dispatch
card. Two obligations, both discharged below:

1. For **every invalidation rule**, show the arithmetic that evaluates it at the
   exact declared cells and mark it **CAN FIRE** or **CANNOT FIRE**. A rule that
   **CANNOT FIRE** is removed or replaced **before the freeze**, with the removal
   recorded — section 4.
2. For **every criterion F-1 to F-5**, show at which named cells it is evaluable
   and state what makes it evaluable there — section 5.

**Nothing in this document is a measurement.** No cell has been run. Every
figure below is either declared by the contract, or exact arithmetic on declared
figures, or a structural bound. Where a quantity depends on `p` or `n` — which
the driver **computes** and which no record here transcribes — the entry says so
and gives a bound instead of a number. The authoring session had **no shell**
and ran nothing.

---

## 1. Per-cell arithmetic (all declared, all exact)

`q = B // 3`; `R_base = ceil(B/3)`, a function of `B` alone, identical across
the two arms; `emitted = 3 * R_base`; `tail index e = 3q` where `B mod 3 == 1`;
`T_max(B) = 5 * max(10, B + 10)` is the attempted-distinct-target cap, inherited
from the committed loop bound at `harness/endomorphism_la.py:269` with
`num_targets = max(10, B + 10)`.

| cell | curve | B | m | B mod 3 | q | e | R_base | emitted | emitted ≥ B | min base rows for the square branch | T_max | \|T(cell)\| ceiling = 2q+1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L12   | J12S1 | 12  | 2 | 0 | 4  | —   | 4  | 12  | 12 = 12 ✓  | 4  | 110  | 0 (T is empty) |
| L13   | J12S1 | 13  | 2 | 1 | 4  | 12  | 5  | 15  | 15 > 13 ✓  | 5  | 115  | 9 |
| L24   | J12S1 | 24  | 2 | 0 | 8  | —   | 8  | 24  | 24 = 24 ✓  | 8  | 170  | 0 |
| L25   | J12S1 | 25  | 2 | 1 | 8  | 24  | 9  | 27  | 27 > 25 ✓  | 9  | 175  | 17 |
| L48   | J12S1 | 48  | 2 | 0 | 16 | —   | 16 | 48  | 48 = 48 ✓  | 16 | 290  | 0 |
| L49   | J12S1 | 49  | 2 | 1 | 16 | 48  | 17 | 51  | 51 > 49 ✓  | 17 | 295  | 33 |
| L96   | J12S1 | 96  | 2 | 0 | 32 | —   | 32 | 96  | 96 = 96 ✓  | 32 | 530  | 0 |
| L97   | J12S1 | 97  | 2 | 1 | 32 | 96  | 33 | 99  | 99 > 97 ✓  | 33 | 535  | 65 |
| L192  | J12S1 | 192 | 2 | 0 | 64 | —   | 64 | 192 | 192 = 192 ✓| 64 | 1010 | 0 |
| L193  | J12S1 | 193 | 2 | 1 | 64 | 192 | 65 | 195 | 195 > 193 ✓| 65 | 1015 | 129 |
| X96   | J16S3 | 96  | 2 | 0 | 32 | —   | 32 | 96  | 96 = 96 ✓  | 32 | 530  | 0 |
| X97   | J16S3 | 97  | 2 | 1 | 32 | 96  | 33 | 99  | 99 > 97 ✓  | 33 | 535  | 65 |
| A12M3 | J12S1 | 12  | 3 | 0 | 4  | —   | 4  | 12  | 12 = 12 ✓  | 4  | 110  | 0 |
| A13M3 | J12S1 | 13  | 3 | 1 | 4  | 12  | 5  | 15  | 15 > 13 ✓  | 5  | 115  | 9 |

**Consequences of the table, all exact:**

* **The square branch is taken at every cell**, because `emitted >= B` at all
  fourteen. The rectangular limb of
  `harness/endomorphism_la.py:220-232` is never reached under a full base-row
  budget, so the derivation note's Lemma 1 applies everywhere.
* **A shortfall of ONE base row flips the branch at EVERY cell.** At a
  `B mod 3 == 0` cell, `3*(R_base - 1) = B - 3 < B`; at a `B mod 3 == 1` cell,
  `3*(R_base - 1) = B - 1 < B`. This is what makes `IV-12` fire on real
  arithmetic rather than on a hypothetical.
* **`B` spans 12 to 192, a factor of 16, at a FIXED curve** — the
  independence-of-B lever. Residues: 12, 24, 48, 96, 192 are all `0 mod 3`;
  13, 25, 49, 97, 193 are all `1 mod 3`. No declared cell has `B mod 3 == 2`,
  which is why the derivation note's closed form is stated for residues 0 and 1
  only (its condition C-8).
* **The static ceiling on `alpha` at the residue-1 cells GROWS WITH B**
  (`2q + 1`: 9, 17, 33, 65, 129 up the ladder). Nothing in the construction
  bounds the number of tail-touching base rows by 3, so `F-5` is reachable, and
  its non-firing would be informative rather than automatic. See section 5.
* **654 base-row certificates.** `654` is a count and its terms are named:
  `2 arms × (4+5+8+9+16+17+32+33+64+65 + 32+33 + 4+5) = 2 × 327`.

---

## 2. What each pre-flight check evaluates

| id | evaluates | can it stop the run? |
|---|---|---|
| PF-1 | the exact `sage --version` string, captured once | **YES** — absent binary, nonzero exit, or a string not naming SageMath 10.9 / 2026-05-04. Infrastructure signal. |
| PF-2 | the four harness sources against their HEAD blobs | **YES** — the object of measurement would not be the committed object. |
| PF-3 | free space on the volume, exact figure, before the first write | **YES** below 5 GiB. Two inconsistent host figures are on record (1.6 Ti available now; ~30 GiB free when the queue was written); the check is binding regardless of which a reader believes, because the Executor measures it. |
| PF-4 | tracked-tree dirty state outside `experiments/EXP-STR-004/` | **YES** — stopping here is strictly better than producing 28 runs that `IV-1` invalidates. |
| PF-5 | pre-existence of any of the 28 run directories | **YES** — `write_run` refuses to overwrite (`harness/runner.py:109-112`); the refusal is reported, never renamed around. |
| PF-6 | contract and derivation-note blobs against the `TASK-20260729-041` commit | **YES** — a difference means the contract was edited after the freeze. |

---

## 3. Invalidation rules: arithmetic and firing status

Each rule is classed by its firing mechanism. **Environmental** = fires on a
state of the host or repository the contract does not control. **Arithmetic** =
fires on a numeric condition evaluable from the declared cells.
**Defect-detecting** = its only firing mechanism is an implementation defect in
the driver or a disagreement between two implementations; such a rule **CAN
FIRE**, and each entry below names the concrete defect it guards against rather
than asserting the class in the abstract. Five contract or driver defects are
already on record in this campaign (`EV-STR-003` `O-5`, `O-12` defects 1 and 2,
`UC-3`, `UC-4`), so a defect-detecting rule is not vacuous here.

| id | rule | class | arithmetic / mechanism at the declared cells | status |
|---|---|---|---|---|
| **IV-1** | manifest records `code.dirty` true → run invalid | environmental | `code.dirty` is `git status --porcelain --untracked-files=no` non-empty (`harness/runner.py:44`). It is a per-run boolean, both values are reachable, and the branch this executes on was reported five commits behind `origin/main` with co-drivers moving `main`. `PF-4` exists because this state is reachable. | **CAN FIRE** |
| **IV-2** | any of the six per-run files missing → run invalid | environmental | 28 runs × 6 files = **168** paths must exist. `write_run` writes them sequentially at `harness/runner.py:185-194`, so an interruption after `manifest.yaml` and before `raw-result.json` leaves a set of 1–5. Reachable via `SR-1` (per-run 900 s), `SR-3` (memory), `SR-6`/`SR-7` (disk), or an uncaught exception. | **CAN FIRE** |
| **IV-3** | recorded factor-base length ≠ declared `B` → run invalid | arithmetic | Arm A-prime needs `q` or `q+1` accepted orbits (4→65 up the ladder) within `50B + 1000` candidate draws (1600 at `B=12`, 10 600 at `B=192`, 10 650 at `B=193`); an orbit is accepted only if its three members are pairwise distinct, none already present, and **all three lift** to curve points. Arm E-prime needs `B` distinct liftable x-coordinates within the same bound. Both builders **return a short list rather than raising** (`endomorphism_la.py:114`, `semaev.py:73`), and `B <= (number of distinct on-curve x-coordinates) <= p` is a necessary condition this contract does not verify in advance because it does not transcribe `p`. Nothing guarantees success at the top two rungs. | **CAN FIRE** |
| **IV-4** | `rows_final ≠ 3 × base_rows_collected` → run invalid | defect-detecting | Declared `emitted` is 12, 15, 24, 27, 48, 51, 96, 99, 192, 195, 96, 99, 12, 15. Guards the single most likely closure defect: emitting one shifted row instead of two, or emitting the base row twice. | **CAN FIRE** |
| **IV-5** | nonzero `suppression_count` → run invalid | defect-detecting | Pre-registered as **0** at all 28 (arm, cell) pairs, by construction. **This is the most likely driver defect in the whole contract**: the driver copies its closure from `harness/endomorphism_la.py:294-304`, where the `sum(shifted_row) > 0` filter and the `shifted_row not in relations` dedup are *present in the source being copied*. A copy that retains lines 303–304 reproduces EXP-STR-003 arm A, not arm A-prime, and this rule is what catches it. | **CAN FIRE** |
| **IV-6** | a base-row certificate fails the independent Sage re-verification → `completed_invalid`, `certificate_failed` | environmental / cross-implementation | **654** certificates are checked; the rule fires if any one fails. The mechanism is a disagreement between `harness/toycurve.py` arithmetic and Sage's own — sign conventions in `lift_x`, the `None` representation of the point at infinity, or a coordinate that is on the curve for one and not the other. Detecting exactly that is the purpose of `CTRL-2`; a rule that could not fire would make the control decorative. | **CAN FIRE** |
| **IV-7** | `determinism_check` failed at L12, L13, A12M3 or A13M3 → run invalid | defect-detecting | 4 cells × 2 arms = **8** rechecks. `matrix_rank_mod` copies its input (`endomorphism_la.py:146`), but the driver's own `MIS` computation walks the same row list; a row list mutated in place between the two `alpha` calls would show up here and nowhere else. | **CAN FIRE** |
| **IV-8** | `code_hashes` disagree across runs → run invalid **and SET invalid** | environmental | 4 harness sources × 28 runs = **112** hashes must fall into one block. The execution window is up to 7200 s; a concurrent agent checking out a branch, or any edit under `harness/`, splits it. The queue records that `main` has moved during this batch's lifetime. | **CAN FIRE** |
| **IV-9** | `raw-result.json` disagrees with the matching `sweep_summary.json` cell → **SUMMARY** invalid, run valid | defect-detecting | 28 cells × (alpha, MIS, T, symmetric difference, suppression count, base-row count, 2 hashes) compared pairwise. The summary is assembled in a separate pass, which is where transcription slips live; `RT31-5`'s deviation count is the recorded precedent. Note the asymmetry: **the raw record governs**, and the summary is regenerated. | **CAN FIRE** |
| **IV-10** | run count ≠ **28**, or an id outside `run_inventory` → SET invalid pending adjudication | arithmetic | Cancelled and failed runs still write all six files, so budget stops alone do **not** move the count off 28. It moves below 28 on `PF-1`/`PF-3`/`PF-4`/`PF-6` stopping before any write, on `SR-8` halting mid-experiment, or on `SR-11` `instance_unavailable`; it moves above 28 if a stray suffix is written. Both directions reachable. | **CAN FIRE** |
| **IV-11** | `alpha` obtained other than from the committed `_measure_displacement_rank` → cell invalid | defect-detecting | The precedent is in this exact lineage: `EV-STR-003` `UC-3` records that EXP-STR-003's `rank_M` at I3 and I4 "rests on the driver's vectorised implementation alone", i.e. a driver in this program has already substituted its own linear algebra for the committed path. At `B = 192, 193` the committed pure-Python elimination is the slowest step in the contract, so the temptation recurs under time pressure. | **CAN FIRE** |
| **IV-12** | recorded `shift_type ≠ "phi"`, or recorded `branch == "rectangular"` → run invalid | arithmetic | **Exact, per cell:** the branch is `"square"` iff `rows >= B`. With the full budget `rows = emitted >= B` at all fourteen cells; with one base row missing, `rows = 3(R_base − 1)`, which is `B − 3` at the seven residue-0 cells and `B − 1` at the seven residue-1 cells — **below `B` at every one of the fourteen**. So a shortfall of a single base row at, e.g., L193 (64 rows found of 65 → `rows = 192 < 193`) flips the branch and fires this rule. The `shift_type` limb guards against passing `"random"`, which is the operator the committed `main()` uses at line 439 and which this contract forbids. | **CAN FIRE** |
| **IV-13** | `derived_seed` mismatch against the generator, or across the two arms of a cell, or attempted-target-list mismatch across the arms → both runs invalid | defect-detecting | Per cell the two arms must record the **same** `derived_seed = requested_seed*100 + offset` and the **same** ordered attempted-target list, because the target recurrence `k = (t_idx+1) * max(2, derived_seed % max(2, n−3)) % (n−1) + 1` (`endomorphism_la.py:272`) depends on neither the arm nor `B`. The concrete defect it guards: passing the **requested** seed (1 or 3) instead of `inst.seed` into a builder or into the target recurrence — a one-token slip, and the two seeds differ by construction. | **CAN FIRE** |
| **IV-14** | `factor_base_sha256` or `row_list_sha256` missing → run invalid | defect-detecting | 28 runs × 2 hashes = **56** required values. Under `SR-6` (2 MiB per-run cap) the full dumps may be omitted at named cells; the hashes may **not**, because they are the whole of the `UC-6` repair. A driver that omits both under size pressure reproduces exactly the EXP-STR-003 gap this contract was supposed to close. | **CAN FIRE** |
| **IV-15** | `sage_version_string` in a manifest differs from the one in `certificate_verification.json` → run invalid, SET certificate status invalid | defect-detecting | 28 manifests must carry one identical string. The guarded defect is named in the dispatch card itself: capturing `sage --version` per run — "28 independent probes asserted as 28" — instead of once. | **CAN FIRE** |

**All fifteen retained invalidation rules CAN FIRE.** No retained rule is
vacuous at the declared cells.

---

## 4. Rules removed or replaced before the freeze, with the removal recorded

Three candidate rules were evaluated against the declared cells and found unable
to fire. Each is recorded here and in the specification under
`invalidation_rules_removed_before_the_freeze_with_the_removal_recorded`, with
its replacement.

### REMOVED-1 — "any run recording `alpha == -1` is invalid" — **CANNOT FIRE**

*Arithmetic.* The `-1` sentinel is assigned **only** inside
`harness.endomorphism_la.main()`, at lines 434 and 439 (`... if phi_rels else -1`).
`main()` is a forbidden entry point (`SR-9`) and is never invoked.
`_measure_displacement_rank` itself returns **0**, not `-1`, on an empty row list
(line 134). `R_base >= 4` at all fourteen cells, and any shortfall is disposed of
by `SR-4`. There is no path at any declared cell on which the value `-1` can be
recorded.

*Replaced by* `SR-4` (base-row shortfall: recorded naming the cell and the arm,
cell excluded from the comparative criteria, verdict `incomplete`) and `IV-3`
(factor-base length), which catch the underlying condition the sentinel stood in
for.

### REMOVED-2 — "seed integrity of sampled quantities" — **CANNOT FIRE**

*Arithmetic.* There is **no sampled quantity anywhere in this contract**. Under
`RC-8` every quantity is `DETERMINED`: the instance, `zeta3`, both factor bases,
the target sequence, the base rows, both closures, `MIS`, `T`, `T_E` and `alpha`
are deterministic functions of `(field_bits, requested_seed, B, m)` and the
committed sources. The seeded random shift permutation of
`harness/endomorphism_la.py:185-193` is never used — `shift_type` is `"phi"` at
all 28 (arm, cell) pairs. A rule quantified over sampled quantities has an empty
domain here.

*Replaced by* `IV-13` (derived-seed and target-sequence agreement across the two
arms of each cell) and `CTRL-5` (intra-run determinism recheck at four cells,
eight rechecks).

### REMOVED-3 — the EXP-STR-003 partner-equality rules and the arm-D `--out` rule — **CANNOT FIRE**

*Arithmetic.* (a) EXP-STR-003 `IV-5`/`IV-6` invalidate an arm whose factor base
or base-row list fails an equality assertion against its partner arm. Here the
two arms use **deliberately different** factor bases — that is the independent
variable — hence deliberately different base-row lists. There is no
partner-equality invariant to violate, and asserting one would assert the
negation of the design. (b) EXP-STR-003 `IV-4` invalidates an arm-D run whose
`--out` path lies inside the repository. **There is no arm D**: this contract
invokes no subprocess of the committed program and has no `--out` path, because
`main()` is forbidden. The rule's subject does not exist.

*Replaced by*, for (a), `IV-13` plus `CTRL-3` — which fix the variables that
*are* held constant across the arms (derived seed, target sequence) — and
`CTRL-6`, which fixes what is held constant across `B` (factor-base prefix
nesting). For (b), nothing: a rule with no subject is deleted, not replaced.

---

## 5. Criteria F-1 to F-5: where each is evaluable, and what makes it so

**What makes any of them evaluable at all.** Every input is `DETERMINED` and
computed from archived artifacts: `alpha` from the committed measurement
function, `MIS` from the final row list by definition, `T` from the factor base
and the base row list by the closed-form rule of `derivation_note.md` §8.1.
No criterion depends on a threshold over an unmeasured quantity, on a
distributional assumption, or on a comparison against an unarchived probe. Each
is a finite **set equality over named cells**, so it is decided by listing
members — which is what `PRED-ID-STR` requires and what makes
`cardinality_only_agreement` a detectable outcome rather than an invisible one.

| criterion | evaluable at | count | what makes it evaluable there | what makes it **not** evaluable |
|---|---|---|---|---|
| **F-1** set identity | all 14 cells for arm A-prime; all 14 for arm E-prime | 28 pairs | Arm A-prime's predicted set is fixed by `P-1` (empty at the 7 residue-0 cells) or `P-2` (`T(cell)`, computed from artifacts that exist before `alpha`). Both the predicted and the measured set are sorted member lists, so equality, symmetric difference and `cardinality_only_agreement` are all decidable. | A cell where the arm's run is invalid under any `IV-*`, or excluded by `SR-4`. **For arm E-prime additionally:** its predicted set is `MIS(A-prime, cell)` — the only set prediction `P-3` makes for it — so arm E-prime's `F-1` at a cell requires arm A-prime's run at that cell to be valid. For arm E-prime `F-1` and `F-4` therefore coincide by construction; the contract states this rather than leaving it to be noticed. |
| **F-2** static bound | all 14 cells, both arms | 28 pairs | `alpha` and `\|MIS\|` are both recorded per (arm, cell); the comparison is an integer inequality. Corollary 2b of the derivation note makes it exact linear algebra over the field `F_n`, so a firing localises an implementation defect in `matrix_rank_mod` or in the driver's `MIS` computation. It is reported, and it does **not** invalidate the run — a criterion may not delete the evidence that fired it. | Any cell whose run is invalid. |
| **F-3** ladder | the 10 ladder cells, arm A-prime only | 10 | Requires all ten arm-A-prime ladder runs valid and unexcluded, then compares `{cells where alpha(A-prime) = 0}` against `{L12, L24, L48, L96, L192}` — exactly the residue-0 subset (12, 24, 48, 96, 192 ≡ 0 mod 3; 13, 25, 49, 97, 193 ≡ 1 mod 3). | **Not evaluable at X96, X97, A12M3, A13M3 by design** — they are not ladder cells. Any shortfall on the ladder makes the whole criterion `incomplete` rather than partially evaluated. |
| **F-4** diagnosticity | all 14 cells | 14 | Requires **both** arms valid at a cell; compares `{cells where alpha(E-prime) = alpha(A-prime)}` against the full fourteen. The direction of each inequality is recorded per differing cell, which is what distinguishes `instrument_artifact_falsified` (some cell with `alpha(E-prime) > alpha(A-prime)`) from the opposite direction. | Any cell where either arm is invalid or shortfall-excluded. |
| **F-5** B-independence of the bound | the 10 ladder cells, **per arm** | 10 per arm, 20 total | Compares `{ladder cells where alpha <= 3}` against the full ten-cell ladder set, separately for each arm. The threshold 3 is `r`, taken verbatim from H-STR-002's own prediction text ("alpha <= r = 3 ... at all tested B") and not fitted. | Not evaluable off the ladder; `incomplete` if any ladder cell is missing for that arm. |

### 5.1 Two-sided reachability — why none of these is a foregone conclusion

`F-3` and `F-5` are **set identities**, not one-sided inequalities, so each can
fire from either side. That is deliberate and it is what makes the `mixed` branch
reachable (repairing the defect `EV-STR-003` `O-5` names). Exact reachability
arguments, from the derivation note and the table in section 1:

* **`F-3` fires if a residue-1 cell also measures `alpha = 0`.** By §8.1 of the
  derivation note, `T(cell)` at a residue-1 cell is empty exactly when no base
  row among the first `R_base` has a nonzero coordinate at the tail index `e`
  **and** the last base row `r_{q+1}` is `S`-invariant. The tail index is 1 of
  `B` coordinates and a base row has at most `m + 1` nonzero coordinates, so
  neither branch is forced at L13, L25, L49, L97, L193, X97 or A13M3. Nothing
  here asserts which occurs.
* **`F-5` fires if `alpha > 3` at any ladder cell.** At residue-0 cells `alpha = 0`
  is derived, so a firing can only come from a residue-1 cell — where the static
  ceiling `\|T\| <= 2q + 1` is **9, 17, 33, 65, 129** at L13, L25, L49, L97, L193.
  Three or more tail-touching base rows at L193 would give `\|T\| >= 6`, and
  nothing in the construction bounds that count by 3. So `F-5` is genuinely
  reachable and its non-firing would be informative rather than automatic.
* **`F-4` non-firing is reachable** — it is forced at the seven residue-0 cells
  by Theorem 1 (both arms `MIS = {}`, `alpha = 0`) and possible at residue-1
  cells whenever no arm-A-prime base row touches the tail.
* **`F-4` firing is reachable** — the derivation predicts it at any residue-1
  cell where some arm-A-prime base row does touch the tail.
* **All four verdict branches are therefore reachable.**
  `instrument_artifact_confirmed` needs `F-1` silent on both arms and `F-4`
  silent; `mixed` needs the `F-4` agreement set to be a non-empty proper subset
  of the fourteen, which the derivation makes the most likely outcome; and
  `instrument_artifact_falsified` needs a named cell with
  `alpha(E-prime) > alpha(A-prime)`, which §8.2 shows is reachable only through
  the last-row branch (`r_{q+1}` `S`-invariant for arm A-prime but not for arm
  E-prime, with no tail-touching arm-A-prime base row) — narrow, but available,
  and recorded as available rather than dismissed.

### 5.2 The interpretive trap this table exists to expose, stated before execution

The derivation predicts that an `F-4` or `F-5` firing localised to
`B mod 3 == 1` cells, with direction `alpha(A-prime) >= alpha(E-prime)`, is a
**factor-base truncation artifact** — a coordinate dropped because a phi-image
left the `xs[:B]`-truncated factor base — and **not** endomorphism content. It is
the same mechanism `EV-STR-003` observation `O-4` identifies as arm A's skip
cause. Reading such a firing as "the phi-invariant factor base is doing something
mathematical" is forbidden in advance, by the contract's
`interpretation_limits` and by this table. Symmetrically, a clean ladder — `F-5`
silent for arm A-prime — is **not** support for H-STR-002 if `F-4` is also
silent, because a bound of 3 that a construction with zero endomorphism content
satisfies identically is a property of the closure convention.

---

## 6. Defects and unmet requirements found while building this table

Recorded here and in the specification's integrity notes; reported to the
Coordinator in `task_report.md`. None is repaired by this card.

1. **`tools/allocate_id.py --check` was run, but AFTER the first write rather
   than before it** (`SPEC-STR-004-C`). All 31 identifiers were checked and the
   output is verbatim in `task_report.md`. 30 return free. `EXP-STR-004` returns
   `REFUSE: taken` naming one occurrence — `experiments/EXP-STR-004/specification.yaml`,
   the deliverable itself — because `occurrences()` matches a **parent directory
   name** over the glob `experiments/*/specification.yaml`. Read-only git puts the
   pre-write count at **zero** (`git ls-files experiments/EXP-STR-004` empty,
   directory untracked at HEAD `f5139200`), so the id was free when allocated and
   **nothing was renamed**. The ordering requirement was still missed, and
   `EV-STR-004` and `DEC-20260729-004` are the two that must still come back free
   when the check is re-run.
2. **The specification was machine-parsed and probed for truncation**
   (`SPEC-STR-004-D`). `yaml.safe_load` succeeds, 487 string scalars load, and
   the count of source lines carrying content before a `" #"` — the construct
   that silently truncates a scalar — is **zero**; the 42 hash-bearing lines are
   all deliberate full-line banners. Structure counts were verified from the
   parsed document: 2 arms, 14 cells, 8 controls, 4 predictions, 5 falsifiers, 15
   invalidation rules, 3 recorded removals, 28 run ids, 12 stopping rules, 6
   pre-flight checks, `review_required`, `approved_by: null`. The card's phrase
   "both YAML files" resolves to one file here: the other two deliverables are
   markdown.
3. **The derivation and the queue's `P-3` disagree at the seven residue-1
   cells** (`SPEC-STR-004-E`). `P-3` is carried unchanged; the derivation is
   carried beside it; both predate every measurement; the Coordinator disposes.
4. **The queue's disk figure is stale.** `artifact_size_budget` and
   `operational_hazards` state 99 percent capacity with about 30 GiB free; the
   dispatching session's fresh observation is 1.8 Ti total, 208 Gi used, 1.6 Ti
   available, 12 percent. Both are recorded in the contract, neither is deleted,
   and the mandatory pre-flight disk check (`PF-3`) is binding either way. The
   `git fsck` timeout is carried unretracted.
5. **A `._*` AppleDouble sidecar exists in this task directory, and it is
   git-ignored.** `coordination/.../TASK-20260729-040/._task_card.md` (4096 bytes,
   mtime 14:38, created by the volume when the dispatching session wrote
   `task_card.md`) is one of **4170** such sidecars repo-wide. `.gitignore:9`
   matches `._*`, so none can be staged, and `git status --untracked-files=all`
   over both write-scope directories lists exactly the three deliverable files and
   nothing else. **This session created no sidecar**, and none exists beside any
   of the three deliverables. Recorded because the card names `._*` files
   explicitly and because `tools/allocate_id.py:68` skips them, so their existence
   is load-bearing for tooling even though it is benign for the archive.
6. **Queue/mirror comparison: no disagreement found.** The mirror at
   `coordination/goals/GOAL-ECDLP-001/batches/BATCH-014/tasks/TASK-20260729-040/task_card.md`
   was compared against the authoritative `tasks[]` entry on every load-bearing
   item — role, dependencies, archiving task, budget, inference policy, write
   scope, artifact paths, the two arms, the fourteen cells and their `B` values,
   PRED-ID-STR, the matched base-row budget, the derivation-note requirements,
   certificate discipline, the budget and stopping-rule figures, the `mixed`
   branch, `RC-7`/`RC-8`/`RC-D`, `RT21-1`, the no-commit rule and the completion
   gate. **They agree.** The mirror is a strict abridgement; it omits detail (for
   instance it does not restate `T_max`, the `X96`/`X97` curve label, or the
   `L`-cell naming) but contradicts nothing.
