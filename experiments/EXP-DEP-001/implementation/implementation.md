# EXP-DEP-001 implementation notes

Driver: `experiments/EXP-DEP-001/implementation/dep001_driver.py`
sha256 `c83e9e9f4c04ba52a8f4b4768d6a4eeb4ee316e0f149a1d6c9a278d819aef3d8`

Binding contract: `experiments/EXP-DEP-001/specification.yaml`, sha256
`e4a977f2117b190fef2baa95e2fbb7791d601b5a42c783b82d835222d9c9e20d`, hash-bound
at commit `36141a951a09bb340a19dc68406f98628294ad71`.

Authorship task: TASK-20260801-035 (Phase A). Execution: RUN-DEP-001-calib
(Phase B). Archived by TASK-20260801-036.

This file records implementation decisions, recording policies, protocol
deviations and unexpected observations. It states no disposition and
interprets nothing.

## 1. What the driver is and is not

The driver has exactly two entry points, selected by `--mode`:

- `--mode calib` — RUN-DEP-001-calib, the non-evidential calibration on NULL
  and PLANT-MACHINERY objects only: DEP-CAL-A through DEP-CAL-F. **Executed at
  TASK-20260801-035.**
- `--mode measure` — RUN-DEP-001-measure, the three ladders plus DIAG-DEP-DUP.
  **Authored complete and NOT INVOKED at TASK-20260801-035.** ATS-DEP-1.5
  binds this file's sha256 at the TASK-20260801-036 snapshot and
  TASK-20260801-042 must execute the identical file with no edit.

The measurement entry point is guarded and refuses to start unless BOTH gates
are supplied on the command line:

1. `--approval-receipt` pointing at a JSON receipt whose
   `APPROVAL_DETERMINATION` is the literal `APPROVED` (the TASK-20260801-041
   snapshot receipt), and
2. `--reading-rule` pointing at an existing frozen RR-DEP-1.

Both refusals were exercised against scratch inputs outside the repository
before the calibration ran (missing receipt, and a receipt carrying `REVISE`).
Each refused with `status: failed_infrastructure`,
`failure_class: specification_error`, an empty payload, no arm computed, no
result file emitted and the real-object tripwire still false. Those two scratch
invocations wrote their run packages to a scratch directory outside the
repository and are disclosed here for completeness; they are not part of any
run package.

The driver contains no factorization, no largest prime factor, no smoothness
indicator, no Dickman evaluation, no u ladder, no search arm, no relation
harvest, no charged unit, no cost identity and no R. `wall_seconds` is recorded
for budget accounting only and is not a decision variable.

## 2. CTRL-DEP-EQDHASH: nothing is re-implemented

INT-2 and the four statistics of STAT-DEP-1 are **imported read-only** from
`experiments/EXP-EQD-001/implementation/eqd001_driver.py` via
`importlib.util.spec_from_file_location`, after that file's sha256 is verified
equal to `bdb2601b195f314a4430fa80fcf8ab15ec0b605335a8386a93c2b9b3c7d7b02f`
and the archived null-replicate array's sha256 equal to
`284ca32143b386beefe80bae5ae05419a2b2f9286c96e3450e09c33e0fdca019`. A mismatch
aborts before any arm is computed.

Imported and used unchanged: `int2_fibre_invariants`, `stat_chi`, `stat_ks1`,
`all_two_sample_statistics`, `flat_two_sample_values`, `_cell_index`, `Cell`
(including `draw_null_factor_base`, `enumerate_factor_base` and the
reject-and-redraw x-collision policy), `Stream`, `modinv_arr`, `write_json`,
`yaml_dump`, `environment_block`.

No file under `experiments/EXP-EQD-001/` is written, edited, renamed, moved,
appended to or staged. `eqd_tree_unmodified` is recorded in the run package and
was `true`: `git status --porcelain -- experiments/EXP-EQD-001` was empty and
both hash-bound files still carried their contract hashes after the run.

Written afresh here, because EXP-EQD-001 has no equivalent: the three plant
families, CTRL-DEP-MARG, DIAG-DEP-RHO, the Clopper-Pearson bounds, the
uniform-random CTRL-DEP-S3 variant, and DIAG-DEP-DUP.

## 3. The three plant families, and DESIGN-TRAP-1

All three leave `e_1` untouched and permute `e_2`, so both marginals are
exactly invariant by construction; CTRL-DEP-MARG then verifies that
empirically on every arm rather than trusting the construction.

- **C1, PRIMARY — `plant_copula` (OBJ-PLANT-DEP-rho).** `Z1` is the ascending
  vector `Phi_inv((k + 0.5) / n)` indexed by the ties-by-index ranks of `e_1`;
  `W` is standard normal from the declared copula stream;
  `Z2 = rho * Z1 + sqrt(1 - rho^2) * W`; `e2_new[i] = sorted_e2[rank(Z2)[i]]`.
  `Phi_inv` is `statistics.NormalDist().inv_cdf` from the standard library (no
  new dependency), evaluated once per `n` and cached.
- **C2 — `plant_cell` (OBJ-PLANT-DEP-CELL-eps).** `floor(eps * n / 2)` disjoint
  index pairs with **different K = 16 `e_1` bins**, exchanging `e2[u]` and
  `e2[v]`. "Uniformly at random subject to the constraint" is implemented as: a
  uniform random permutation of the `n` indices read as `n/2` consecutive
  disjoint candidate pairs, discard candidates whose two `e_1` bins coincide,
  take the first `floor(eps * n / 2)` survivors. Consecutive pairs of a uniform
  permutation are an exchangeable uniform pairing, so the retained pairs are a
  uniform sample of admissible disjoint pairs and disjointness holds by
  construction. About 15/16 of candidates survive, so one permutation suffices
  for every rung of DEP-LADDER-CELL; a guard draws further permutations if not.
- **C3 — `plant_block` (OBJ-PLANT-DEP-BLOCK-q).** Two strata split at the
  median of `e_1` by ties-by-index rank (exactly `n/2` and `n - n/2`), a
  uniformly random fraction `q` chosen within each stratum, and an independent
  uniform random permutation applied to the chosen `e_2` values within each
  stratum.
- **Anchor — `plant_comonotone` (OBJ-PLANT-DEP-EXTREME).**
  `e2_new[i] = sorted_e2[rank(e1)[i]]` exactly, no noise.
- **Plant-machinery null — OBJ-PLANT-DEP-0** is `plant_copula` at `rho = 0.0`
  exactly, which degenerates to a uniform random permutation of `e_2`. It is
  the same code path as C1 and not a separate construction.

DESIGN-TRAP-1 is the reason the copula family is primary and the block strata
are coarse. Permuting `e_2` **within** strata that coincide with the chi-square
bins leaves the K x K contingency table exactly invariant, because the multiset
of `bin(e_2)` inside each `e_1` bin is unchanged; detection would then return
the nominal rate at every rung by construction. Neither implemented family
permutes within a grid bin: C1 reorders globally by a rank statistic that is
not measurable with respect to the `e_1` bin partition, C2 exchanges only
between records whose K = 16 `e_1` bins **differ** (enforced explicitly in
code), and C3 permutes within two strata that are 8 times coarser than K = 16
and 32 times coarser than K = 64. The independent re-derivation of this
invariance argument is a named duty of TASK-20260801-040 and this note is not a
substitute for it.

`DIAG-DEP-RHO` is the empirical check that the plant actually moved the joint
law: the measured Spearman rank correlation on source and plant arms, and the
K = 16 joint total variation distance between them, on **every** planted arm.
Spearman uses average ranks (the standard tied definition), implemented
vectorised and checked at startup against a slow reference implementation.

## 4. CTRL-DEP-MARG recording policy

The check itself is performed on **every planted arm without exception**, and
the count-by-count histogram comparison is always performed on the full
histograms. What is *archived* differs by stage, purely for artifact size:

- Calibration (440 planted arms): four sorted-marginal sha256 digests, the four
  **source** histograms in full, source and plant histogram digests, and the
  four count-by-count equality booleans, for every arm.
- Measurement (7200 planted arms, dormant): the same, except that the full
  source histograms are archived for replicate 0 of each rung and every other
  arm keeps digests plus the equality booleans. `full_histograms_archived` is
  recorded per arm.

The planted arm is materialised as an **independent copy** of `e_1`
(`plant_arm`) rather than as an alias of the source array, so the `e_1` digest
comparison is a real comparison of two separately computed digests and not a
comparison of an object with itself.

A mismatch raises immediately, records the family, rung, replicate index and
cell in `marg_mismatch_locations`, and turns the run `invalid` with
`failure_class: invalid_measurement`. It is instrument failure and never a
result. No mismatch occurred in RUN-DEP-001-calib.

## 5. Thresholds

The primary rejection thresholds are the **archived EXP-EQD-001 CAL-1
thresholds**, recomputed at run time as the 199th ascending order statistic of
each named 200-element array in the hash-verified archived artifact, with
rejection **strictly greater than** the threshold. All eight were reproduced
exactly, at absolute difference 0.0.

The driver **freezes no threshold**. The fresh secondary null distribution
measured at DEP-CAL-A is reported with its own 199th order statistic and never
replaces the primary thresholds. TASK-20260801-038 owns the freeze.

In `--mode measure`, if RR-DEP-1 states thresholds they are **checked for exact
equality** against the recomputed archived values and a disagreement aborts the
run as an integrity failure. A reading rule therefore cannot substitute a
different number — it can only disagree. This closes a tuning route through the
reading-rule file. RR-DEP-1's only hard requirement from this driver is a
top-level `reading_rule:` mapping; an optional `thresholds:` block keyed by
field bits and statistic id is cross-checked if present.

## 6. Clopper-Pearson bounds, and one observation

No new dependency was added, so the exact bounds are obtained by bisection on
the exact binomial tail (lgamma-based terms, `math.fsum`) rather than from a
beta quantile. Startup self-checks substitute the returned bounds back into
their defining tail equations (residuals < 1e-15) and check the closed form
`alpha^(1/n)` for the `x = n` case.

**Observation, recorded and not acted on.** The contract's DET-DEP-1 rationale
quotes "190 of 200 gives a one-sided lower bound of about 0.9145". The exact
one-sided 95% lower Clopper-Pearson bound at 190/200 is 0.9166648489336275;
0.9099724622986483 is the exact **two-sided** 95% lower bound at the same
count. Both are above the DET-DEP-1 floor of 0.90, so the bar remains
attainable and non-vacuous either way, and nothing in the frozen rule depends
on which figure the prose meant. Both numbers are recorded in the run package
in `selfchecks.clopper_pearson`. No frozen quantity was adjusted.

## 7. Streams

Seeds are `2301 + offset + bits` with offsets: calibration_null 60000,
source_null_for_plants 70000, copula_noise 80000, cell_transfer 90000,
block_permutation 110000, apparatus_identity 120000, faithfulness_sample
130000. All 14 seeds are recorded with hashes in the manifest and verified
disjoint from the archived EXP-EQD-001 seeds (offsets 10000, 20000, 30000,
40000, 50000); a collision aborts.

**Recorded implementation choice.** The contract declares a stream for the
source null of the plants but none for the *second, fresh comparison* null arm
that each planted arm is tested against. DEP-CAL-C and DEP-CAL-D draw that
comparison arm from the same `source_null_for_plants` stream at the next draw
index, so no draw index is ever reused, every arm remains individually
addressable from its recorded seed, and no additional stream is invented.
`--mode measure` draws its own arms from that stream starting at index
1000000, so it can never re-consume a calibration draw index.

## 8. CTRL-DEP-S3

1000 half-tuples per cell, sampled **uniformly at random without replacement
from the full enumeration** of C(512, 2) = 130816 — not as a prefix. This is
the RANK 6 cheap repair the BATCH-023 close ranked; EXP-EQD-001's own
`ctrl_eqd_s3` takes a prefix, so a separate function was written rather than
modifying anything under EXP-EQD-001. Verification is by independent point
arithmetic on E(F_p) via `harness.toycurve` and does not reuse the coefficient
formula. Result: 1000/1000 verified at both cells.

## 9. DIAG-DEP-DUP — implemented, deliberately NOT run here

`duplicate_decomposition()` and `run_duplicate_decomposition()` are authored
complete and are reachable **only** from `--mode measure`.

Mechanism: for a 2-torsion point `T = (t, 0)`, translating **both** points of a
half-tuple by `T` fixes `P + Q` and `P - Q`, hence fixes `(e_1, e_2)` exactly.
On x-coordinates, `x(P + T) = (t*x + 2*t^2 + a) / (x - t) mod p`; the closed
form is checked against actual point arithmetic on E(F_p) at run time
(`_selfcheck_translate`). Colliding invariant pairs are counted as
`sum_v C(multiplicity(v), 2)`, the same reading STAT-DUP uses. A collision
between half-tuples `{i, j}` and `{k, l}` is **translate-explained** when some
nontrivial 2-torsion `T` maps `{x_i, x_j}` onto `{x_k, x_l}` inside the factor
base. Emitted machine-readable fields, exactly as the contract names them:
`dup_translate_explained`, `dup_residual` (pre-registered at zero) and
`dup_orbit_decomposition` (two-torsion x-coordinates, group order,
translate-closed subset size, free-orbit count, orbit-size histogram, internal
half-tuple count).

**Protocol conflict, resolved in favour of the frozen contract, and reported
rather than resolved silently.** The TASK-20260801-035 dispatch instruction as
relayed to the Executor asked for the DIAG-DEP-DUP decomposition to be produced
in this task. The frozen contract forbids it here twice over:
`calibration_protocol.forbidden_in_the_calibration_stage` states that no
OBJ-REAL sample and **no DIAG-DEP-DUP output** may appear in the calibration
package, `OBJ-REAL` is declared MEASUREMENT STAGE ONLY, and the frozen handoff
in `dispatch_queue.json` says "emit NO duplicate decomposition". DIAG-DEP-DUP
necessarily enumerates the deterministic factor base, which would trip
ATS-DEP-1.3 and fire branch D-0. The diagnostic is therefore **implemented in
full and not executed**; running it is TASK-20260801-042's, under the
measurement authorization. The KN-CAND-BATCH023-A promotion trigger is
consequently **not discharged by this run**, and no deliverable of this task
may claim otherwise.

Note on the two-torsion structure, stated as a property of the curve instances
and not as a result: at bits 16 the cubic has exactly one root in F_p (one
nontrivial 2-torsion point); at bits 20 the curve order is odd and there is no
nontrivial 2-torsion, so at that cell no collision can be translate-explained
and any collision at all would land in `dup_residual`. That is a prediction of
the pre-registered integrity tell's behaviour, not a measurement — nothing was
measured on OBJ-REAL here.

## 10. Non-evidential status and prohibitions honoured

RUN-DEP-001-calib is expressly non-evidential about H-DEP-001, H-EQD-001,
H-SMTH-001 and HEUR-DS-1 in either direction. No statistic of OBJ-REAL against
any null was computed; the tripwire `calibration_saw_real_object` is `false`
and both the local tripwire and the imported EXP-EQD-001 module's own
`_REAL_DATA_TOUCHED` were asserted false at the end of the run. No ladder rung
was run (`ladder_rungs_executed` is empty). No threshold was frozen, no reading
rule was applied, no branch was selected and `interpretation` is `NONE`.

Scratch unit tests of the plant functions were run on **synthetic uniform
random arrays** (no curve, no factor base, no OBJ-NULL-RFB arm, no comparison
against any threshold) in a scratch directory outside the repository, to verify
marginal preservation and that the joint table moves. They are development
tests, are not archived in the run package, and are disclosed here.

## 11. Deviations from the approved protocol

None, with the two recorded items above stated explicitly for the reviewer:

1. **DIAG-DEP-DUP not executed** (section 9) — the frozen contract forbids it
   in the calibration stage; the relayed instruction asked for it. The contract
   governs. The code exists; the artifact does not.
2. **Comparison-null stream index** (section 7) — the contract names no stream
   for the second fresh null arm of a planted comparison; the source stream is
   used at the next unused draw index rather than a new stream being invented.

Neither changes any statistic, threshold, ladder, cut, decision variable or
branch.
