# TASK-20260727-024 — adversarial notes

Red Team, independent non-originating session. Snapshot under review:
`c79e3a8d6cb429c7a9c876b5e0272f46145ab919` (parent `92268c9e`, which froze
`experiments/EXP-STR-003/specification.yaml` before execution). Both commits
verified against Git in this session. Worktree
`/Volumes/Volume/crypto-autoresearcher-worktrees/ecdlp-batch006`.

Companion record: `red_team_report.yaml` in this directory. These notes carry
the falsification routes and the long-form arguments; the report carries the
objections, the transition and the scope test.

---

## 0. What I am not doing

I am not defending TASK-20260727-017. Its central comparative claim was
falsified by a frozen, pre-registered experiment and I restate it nowhere. I
am also not treating its report as durable: at this commit
`coordination/.../BATCH-007/reviews/TASK-20260727-016/` and `.../017/` are
**untracked working-tree files** (`git ls-files` under BATCH-007 returns only
`dispatch_queue.json` and `tasks/TASK-20260727-013/census_report.yaml`). I read
them because they are in my read scope and the frozen contract quotes them. No
conclusion here rests on them.

I ran two diagnostic probes in this session. They were run from a scratch
directory outside the repository, read-only, and they are **not evidence**.
They are labelled as such everywhere they appear, and every conclusion I reach
is independently supported by numbers in the committed
`results/ablation_summary.json`. The failure mode of this batch was citing an
unarchived probe as a result; I am not repeating it.

---

## 1. The strongest case that the ablation proves nothing and
## DEC-20260726-006 stands unchanged

This is the reconstruction the handoff requires, argued at full strength before
anything else.

**1.1 Arm E is a strawman.** Its appended rows are index permutations of
incidence vectors over a factor base that is not φ-invariant. They are images of
nothing. They satisfy no equation. They are, in the contract's own words,
"mathematically worthless as relations". Measuring their displacement rank and
concluding something about a metric applied to real relations is a category
error, and the fact that arm E *lost* — 11 against 9 at B = 27, 29 against 1 at
B = 397 — makes the point twice over: the strawman does not even win.

**1.2 Arm B handicaps a method nobody would run.** φ is an automorphism. For a
φ-invariant factor base, φ(R) is a genuine relation whenever R is, and
φ(target) = λ·target with λ the eigenvalue on the order-n subgroup, so the
orbit images come with correct scalar bookkeeping and cost nothing. Discarding
them is strictly worse engineering. The frozen contract concedes this in
advance in `known_objection_recorded_in_advance` and says arm B "must never be
reported instead of" arm E. So the ablation's headline — "no separation once the
appended rows are removed" — is a statement about a method no attacker would
use.

**1.3 The numbers are real.** Arm A reproduced `phi_alpha` 9, 2, 4, 1 exactly
at all four instances and `misaligned_row_count` 9, 5, 4, 1 exactly. CTRL-8
against the one overlapping committed record
(`RUN-STR-phi-b12-s1-m2/raw-result.json`) agrees on B, n, phi_hits,
phi_attempts and phi_alpha. `cost_ratio` 0.011 is exact arithmetic on α = 1 and
B = 397: `1·397·ceil(log2 397) / (2·397²) = 3573/315218 = 0.01133`. Nothing was
fabricated. An absent-artifact finding invites the suspicion of invention, and
this experiment refutes that suspicion at every headline instance.

**1.4 The red team's own decisive control turned on it.** F1 fired. The
pre-registered consequence is binding: OBS-1/RT-OBJ-1 withdrawn or rescoped,
`DEC-20260727-009` may not rest on them, metric **UNADJUDICATED**. The
prosecution's case collapsed on the prosecution's own test.

**Where this case actually lands.** 1.1 and 1.2 are correct and were both
pre-conceded by the contract before any outcome was seen. 1.3 is correct as to
the φ arm and *false as to the random arm* (§4). 1.4 is correct and I accept it
without reservation. What the case does not do is establish the converse. The
contract itself blocks that: "the Coordinator must treat the as-committed metric
as UNADJUDICATED rather than as refuted." And crucially, none of 1.1–1.4
touches the three findings that carry my recommendation (§3, §4, §5), none of
which involves arm E or F1.

---

## 2. Why arm E diverged — the mechanism, then the diagnosis

### 2.1 What α actually is, read off the committed code

In the square branch (`endomorphism_la.py:233-242`, taken whenever rows ≥ B,
and taken in all 16 measured cells), `Z @ M_sq @ Z_inv` evaluates to
`M[σ(i)][σ(j)]`, so

```
D[i][j] = M[i][j] − M[σ(i)][σ(j)],   σ(3j+k) = 3j + ((k+1) mod 3)
```

Row *i* of D vanishes exactly when `M[σ(i)] == shift_row(M[i])`. Both arm A's
append rule (`:292-304`) and arm E's synthetic closure emit `r, s(r), s²(r)` in
consecutive positions, which makes that identity hold **identically** — until an
emission is skipped. A skip shifts the phase of the entire downstream stream by
one position, and rows stay misaligned until a later skip restores the phase
mod 3.

So α is a **phase-tracking statistic of the emission stream**. Its value depends
on *where* the skips fall, not on how many there are. That is why 12 skips at
arm E/I4 produce 29 misaligned rows while 6 skips at arm A/I1 produce 9.

### 2.2 The two arms cannot have matched skip patterns

Read from the committed records:

| | I1 (B=27) | I2 (B=55) | I3 (B=204) | I4 (B=397) |
|---|---|---|---|---|
| arm A base rows consumed | 15 | 22 | 72 | 136 |
| arm A dedup suppressed | 6 | 0 | 2 | 0 |
| arm A misaligned / α | 9 / 9 | 5 / 2 | 4 / 4 | 1 / 1 |
| arm E base rows processed | 37 | 65 | 214 | 407 |
| arm E dedup suppressed | 20 | 4 | 0 | 12 |
| arm E misaligned / α | 11 / 11 | 1 / 1 | 0 / 0 | 29 / 29 |

Two structural reasons the skip processes differ:

- **Different base-row budgets.** Arm A's appends count against the
  `num_targets` quota, so it consumes 15/22/72/136 base rows. Arm E closes arm
  C's *full* collection: 37/65/214/407. Same rule, 2.5×–3.0× the opportunities.
- **Different skip causes.** Arm A's shifted row is built by mapping each
  support element `x ↦ ζ₃^s·x` and looking the image up in F; a miss **drops**
  that coordinate. `_build_phi_invariant_factor_base` returns `xs[:B]`, so when
  `B mod 3 ≠ 0` the last orbit is truncated and its element has no image in F.
  Arm E's shift is a positional permutation and is weight-preserving; it can
  never drop a coordinate, so every one of its skips is a duplicate hit.

The table confirms it: arm A at I2 and I4 has **zero** suppression yet 5 and 1
misaligned rows — misalignment with no dedup event at all, at exactly the two
`B mod 3 = 1` instances. Only the truncated-orbit mechanism explains that.

### 2.3 The diagnosis (probe — NOT EVIDENCE)

Running the frozen arm-E construction outside the repository reproduces the
committed cells exactly (suppressed 20/4/0/12, α 11/1/0/29). A variant that
emits each σ-orbit **once** and never suppresses returns α = **0, 1, 0, 1** —
the pre-registered prediction, exactly, at all four instances. The random factor
bases have 0, 0, 2 and 1 elements out of B whose ζ₃-image lies in F, so arm E's
"zero endomorphism content" premise is sound.

**These numbers are not evidence and must not be cited.** They are diagnosis.
The mechanism in §2.1–2.2 is established from committed data alone.

### 2.4 The verdict on arm E

Arm E as frozen was a **valid existence control and a mis-specified comparative
control**. The contract told the driver to mirror the harness dedup "term for
term", and the driver did exactly that — faithfully, correctly, no defect. But
that imports a *pathology of the committed harness* into the control, and the
prior probe evidently emitted clean orbits instead. Both constructions are
φ-free. The metric returns 1 for one and 29 for the other at B = 397 with the
mathematics — which is to say, nothing — held fixed.

A quantity that swings 29× under a change of bookkeeping convention at fixed and
zero endomorphism content is not measuring endomorphism content. But that
observation **cannot rescue S1**, because the same variance is what makes a
cross-arm inequality unpredictable. S1/F1 tested a proposition strictly stronger
than OBS-1's content: OBS-1 is a *within-arm* claim ("α is a statistic of the
insertion rule") and S1 was a *cross-arm* inequality on an uncontrolled nuisance
variable. The right test was CTRL-5 (α ≤ misaligned count), and it **passed**,
4 of 4.

### 2.5 The verdict machinery could not express what happened

`S_i = ¬F_i` for i = 1,2,3, so `obs1_confirmed` and `obs1_falsified` are exact
complements and the `mixed` branch is **unreachable by construction**. Yet S1
held at I2 and I3 and failed at I1 and I4 — two each way, the literal definition
of `mixed`, whose declared disposition is Coordinator `inconclusive` on the
instrument question, "and saying so plainly is the required outcome". The
Executor applied the rule correctly. The label must not be read as vindication.

And the power is asymmetric: 4-of-4 to confirm, 1-of-4 to falsify, on an
uncontrolled per-instance variable. To the contract's credit, that means the
falsifying outcome was genuinely available — the opposite of a rigged design.
It also means the test could not settle the question in either direction.

---

## 3. Falsification route A — the one-variable comparison, which survives everything

CTRL-4 measured every arm under **both** shift operators. That yields the
comparison the original claim never ran: same φ shift operator, same collection
rule, same no-append convention, changing only the factor base.

| | I1 | I2 | I3 | I4 |
|---|---|---|---|---|
| arm B — φ-invariant F, φ shift | 27 | 52 | 197 | 386 |
| arm C — random F, φ shift (alternate) | 27 | 52 | 199 | 387 |

Differences 0, 0, 2, 1 on values of order B. **φ-invariance of the factor base
moves the metric by nothing.** No arm E, no F1, no dependence on the instrument
question.

This directly contradicts EV-STR-002's inference sentence, "endomorphism-invariant
factor bases induce O(1) displacement rank". The factor base induces nothing; the
appended rows do, and they do so *by construction* — closing a row list under σ
makes the matrix σ-equivariant, which is a derivation, not a measurement.

**The counter I hold myself to.** H-STR-002 falsification condition 1 reads
"…the block-circulant structure does not survive relation collection." On the
natural reading (what collection produces) it is met at 4 of 4. On the
defender's reading — the appends live *inside* `_collect_relations`, so closure
*is* collection — it is not met. I record the ambiguity instead of resolving it
in my own favour. It is a drafting defect in FC-1, and it is one of the three
reasons the transition is capped at `weaken`.

The φ-free arm reproduces the original signature too: arm E measured under both
shifts gives 11 vs 26, 1 vs 53, 0 vs 200, 29 vs 391 — the same qualitative
separation DEC-20260726-006 called evidence for H-STR-002, at every instance,
from a construction with no endomorphism in it. F1 does not touch this: it is a
within-arm, one-variable comparison.

---

## 4. Falsification route B — half the headline numbers do not reproduce

EV-STR-002 and DEC-20260726-006 record `rand_alpha` = 53 (B=55), 200 (B=204),
387 (B=397).

Arm C is byte-for-byte the computation the committed `main()` performs for
`rand_alpha`: same constructor, same `_collect_relations` call, same
`_measure_displacement_rank(rels, len(fb), "random", ζ₃, p, n, seed=inst.seed)`.
It measures **54, 201, 382**. Three comparisons, three mismatches. For
completeness, the φ-shift measurement of the same arm-C rows gives 52, 199, 387,
so the recorded values match *neither* committed computation across all three.

Meanwhile every `phi_alpha` reproduces exactly. So "the numbers reproduced" is
true of exactly half the headline pairs. The producing script for the nine
"inline" extended measurements is absent from every ref (census, validated
PASS), and its random-arm output is not reproducible from the committed harness
under either shift convention. I do not speculate on the cause. The fact of
non-reproduction follows from two committed artifacts and arithmetic.

Add S4, which is measured and archived in four run records: the committed
`main()` exits 1 with `IndexError` at `endomorphism_la.py:451` at both
`B mod 3 ≠ 0` instances (B = 55 and B = 397) and exits 0 at both `B mod 3 == 0`
instances. Line 451 computes `shifted_idx = (idx//3)*3 + ((idx%3)+1)%3` and
assigns into a list of length B; the final partial orbit drives it to B. The
crash occurs **after** `phi_alpha` and `rand_alpha` are computed and **before**
the metrics dict is built, so no record is written and neither value is printed.
The claimed producing path cannot have produced those two rows.

---

## 5. Falsification route C — there is no end-to-end path at all

`_collect_relations` builds rows as bare incidence vectors
(`row[factor_base.index(sx)] = 1`). The target's scalar multiple k is **never
recorded in any row**. No linear system with a right-hand side is ever
assembled, in EXP-STR-002 or EXP-STR-003. Nothing is ever solved.

Measured rank deficiency `B − rank_M` of the φ arm's own row list:

| | I1 | I2 | I3 | I4 |
|---|---|---|---|---|
| arm A (φ-invariant, appended) | 4 | 6 | 30 | **67** |
| arm E (the "worthless" arm) | 0 | 0 | 0 | 1 |

At the headline instance the φ arm's system is 67 short of full rank; the
construction the contract calls mathematically worthless is full rank. Whatever
the linear algebra would cost, there is no solvable system to apply it to, and
no source recovery, target descent or scalar orientation exists anywhere in this
line of work.

This is why the cost comparison is empty even before RT-CM-1's objection about
the operator class: `α²·B·log B` versus `2B²` compares two models of solving a
system that has never been assembled.

---

## 6. Does "the instrument is confounded" imply "the evidentiary basis fails"?

**No — not by that route, and saying otherwise is how this batch went wrong.**
After F1 the premise is UNADJUDICATED. Any record reasoning "`phi_alpha` is an
artifact, therefore DEC-20260726-006 fails" is repeating the error that produced
this task.

The evidentiary basis fails on three grounds independent of the instrument
question, of arm E, and of F1:

- **R1 — Artifacts.** `run_ids: []`; no run record at B ≥ 55 in any ref (census
  over 247 refs and 47,983 objects, validated PASS); the claimed producing path
  crashes at two of four headline instances (§4); half the headline numbers do
  not reproduce (§4); and `5de2db97` rewrote `EV-STR-002.yaml`,
  `DEC-20260726-006.yaml` and `EXP-STR-002/analysis.md` **in place**, adding
  zero run records — an AGENTS core rule 4 violation.
- **R2 — The one-variable comparison.** §3, 4 of 4.
- **R3 — No cost path.** §5, plus RT-CM-1..6 untested and no archived rho or
  BSGS baseline at n = 41617 or n = 158071.

**The gap, stated plainly.** R1 is an evidence-integrity failure, not a
mathematical one. R2 is open to the defender's reading of FC-1. R3 is an absence,
not a refutation. None of them, alone or together, shows the mechanism is wrong,
and none licenses rejection.

---

## 7. Does reproduction rehabilitate DEC-20260726-006?

**For:** arm A reproduces exactly 4 of 4; CTRL-8 matches the one overlapping
committed record on all five fields; `cost_ratio` 0.011 is exact arithmetic on
(α = 1, B = 397); the computation is deterministic, so (contract, code, seed)
determines the output and the run directory is bookkeeping around a function
evaluation; and nothing was fabricated.

**Against:** the reproduction was performed by a *different program* under a
*different experiment id*, so the numbers belong to EXP-STR-003's run records and
do not retroactively populate `run_ids: []`; the stated producing path is
falsified for two of four headline rows; the random-arm half does not reproduce
at all; the in-place rewrite is an immutability violation that reproducing a
number cannot cure; and the record's content is not the integers but the
inference, which §3 contradicts at 4 of 4 and §5 empties.

**Settled: no.** Reproducing the numbers rehabilitates the arithmetic and the
good faith of whoever computed it. It does not rehabilitate the record. An
evidence record is a claim *plus* its artifacts *plus* its inference. Cite
EXP-STR-003's run records for the alphas going forward; supersede EV-STR-002.
Never edit it, and never treat a later reproduction as a retroactive artifact —
that would make the artifact policy unenforceable, because any absent record
could be cured after the fact by re-running the computation it should have
archived.

---

## 8. The transition, and why the others are unavailable

**`weaken`.** H-STR-002 `supported` → `weakened`; DEC-20260726-006 marked
superseded by a **new** decision; EV-STR-002 superseded by a **new** evidence
record carrying the EXP-STR-003 run ids; plus a correction in the
CORR-20260727-005/002 form for the `5de2db97` in-place rewrite. New records
only. Nothing edited.

- **`replicate` — unavailable.** TASK-20260727-023 does not exist in this tree.
  The frozen contract caps EXP-STR-003 at `preliminary` and forbids calling it
  replicated until that report exists. And EXP-STR-003 replicates an
  *instrument*; no arm measures the mechanism, so it could not replicate
  H-STR-002 even if re-run.
- **`inconclusive` — understates.** Right if the only finding were the
  UNADJUDICATED instrument question. It is not: R1 is a validated artifact
  failure and R2 is a measured 4-of-4 contradiction of the record's own
  inference sentence. `inconclusive` would leave the ledger silent about both
  and let a future reader re-derive `supported` from the same unreproducible
  record.
- **`correction-without-status-change` — insufficient.** It repairs the rewrite
  and the missing run ids while leaving `supported` standing on a record whose
  extended rows have no artifacts, whose random-arm numbers do not reproduce,
  and whose producing path crashes at half its headline instances. A status must
  not outlive its evidence. The correction is necessary and not sufficient.
- **`reject_scoped` — forbidden, and I concur.** No instance is exhibited on
  which the mechanism fails. The mechanism is a one-line consequence of φ being
  an automorphism. The refutation artifact achieved is `empirical_only` and
  unreplicated, which by `docs/claims-and-verification.md` takes `weaken` plus
  replication. Rejecting would convert a bounded instrument ablation into an
  impossibility claim, which the Red Team contract prohibits.

**Refutation artifact.** Strongest class this result *admits*: **derivation** —
the identity in §2.1 plus the append rule plus the `xs[:B]` truncation is
self-contained and checkable line by line, and S3 confirms it 4 of 4. Strongest
class it currently *supports*: **`empirical_only`** — because no derivation note
is archived; the only place that argument exists is inside an untracked file,
and the doc requires the artifact to be snapshot-committed *before* the decision
that relies on it. A counterexample certificate is not available: every run
carries `certificate {kind: none}`.

---

## 9. Cost model — untouched, and it must be said so

The frozen contract states it itself, in `metrics.explicitly_not_measured`:

> No cost ratio, no structured_cost, no wiedemann_cost, no density_penalty and
> no crossover claim. This contract measures an instrument; the cost model is
> not under test here and RT-CM-1..RT-CM-6 remain open objections that no arm of
> this experiment addresses.

Confirmed against the run records: no cell reports any cost quantity, and no
wall-time comparison of any solver exists in this repository. **RT-CM-1 through
RT-CM-6 are untouched and no downstream record may describe them as settled,
tested or addressed.**

Two updates that belong with them:

- **The order-3 objection stands untested.** `α²·B·log B` is the superfast-solver
  cost for a Toeplitz-*like* matrix whose displacement operator is the nilpotent
  lower shift. Here Z is a permutation of **order 3** (`:174-183`), so small
  `rank(M − ZMZ⁻¹)` means near C₃-*equivariance* — a different structure. An
  exactly equivariant system block-diagonalises into 3 blocks of size B/3, giving
  `3·2·(B/3)² = (2/3)B²` against Wiedemann's `2B²`: an honest ceiling of factor
  **r = 3**, not 44×–90×. The decomposition needs a cube root of unity mod n,
  i.e. `3 | n−1`; `n−1 = 732, 3060, 41616, 158070` are all divisible by 3, so the
  ceiling is available at all four instances and r = 3 is the right comparison.
- **One correction to the prior session's supporting example.** RT-CM-2 argued
  the model prices a B×B solve at zero as α → 0 and that line 472 papers over it
  with a `−1` sentinel. That is a code-reading fact and it stands. Its
  illustration — "arm E produced α = 0 at B = 27 and B = 204" — is now
  **falsified at B = 27** (measured 11) and confirmed at B = 204 (measured 0).
  The objection survives on the arithmetic, not on the example.

Recomputing the committed model on the ablated α (arm B: 27, 52, 197, 386, now
backed by committed run records) gives `cost_ratio` 67.5, 147.5, 761.0, 1688.9 —
two to three orders of magnitude *worse* than Wiedemann at every headline B. That
is a model evaluation on measured inputs, not a measurement, and it is quoted
only to show how completely the headline depends on the appended rows.

---

## 10. Baselines

Committed rho, with verified `discrete_log` certificates: `RUN-STR-rho-b12-s1`
solves n = 733 in 24 group operations; `RUN-STR-rho-b12-s2` solves n = 3061 in
156. BSGS arithmetic: `2√n` ≈ 54, 111, 408, 795 at the four instances, with `√n`
stored points.

Against this, the index-calculus arm at n = 158071 spent 314 decomposition
attempts, each an arity-2 double loop over the factor base of order
`B(B+1)/2 = 79,003` s3_eval calls — roughly 2.5 × 10⁷ field-level operations —
to produce a matrix 67 short of full rank, formed no system and solved nothing.
Three to four orders of magnitude, widening with B. Neither EV-STR-002 nor
DEC-20260726-006 compares against rho or BSGS anywhere.

**Closest specialized baseline.** Automorphism exploitation is solved and
quantified: Wiener–Zuccherato and Duursma–Gaudry–Morain give rho a `√r = √3 ≈
1.73×` speedup on a curve with an order-3 automorphism; quotienting an index
calculus factor base by an order-r automorphism gives a factor r in collection
and an r-fold block decomposition in the linear algebra. The committed data
reproduce exactly that and nothing beyond it — searches per relation row, φ arm
vs random arm, are 0.692/1.811, 0.364/1.154, 0.383/1.136, 0.770/2.466, i.e.
ratios **2.62×, 3.17×, 2.97×, 3.20×**, ≈ r = 3 at every instance. That constant
factor is the real, reproducible, archived effect here. It is already known, and
it is not target-class.

**No archived baseline exists at n = 41617 or n = 158071** — the two instances
carrying the headline claims. Arm D's child process did run rho at those sizes,
but its records were written outside the repository and the contract forbids
citing them.

---

## 11. Cheapest next experiments

1. **Arm A′ — dedup disabled** (append the shifted row unconditionally). The
   derivational limb predicts **α = 0 exactly** at every `B mod 3 == 0` instance,
   and α equal to the number of rows touching the truncated tail otherwise. Two
   lines of new code, committed harness otherwise untouched, sharp pass/fail, no
   arm E required. If α ≠ 0 at I1 or I3, the derivational limb fails too and the
   whole objection family collapses — which is the reason to run it.
2. **Arm E′ — orbit-clean φ-free closure** (emit each σ-orbit once, never
   suppress). Explains F1 directly and converts my probe into evidence.
   Prediction from the unarchived probe, to be tested and never cited: 0, 1, 0, 1.
3. **Matched-nuisance design** — truncate arm E's base list to 15/22/72/136 rows
   so the first B emitted rows of each arm derive from the same number of base
   rows, and report α *conditional on* suppression count. Any future criterion of
   the S1 form must control this variable or it is untestable.
4. **Assemble a real system** — add the right-hand side, report rank, attempt a
   solve with a certificate. Until then no cost model on either side compares
   anything real.
5. **Archive** sha256 of the factor base and the final row list per cell; archive
   rho and BSGS baselines at n = 41617 and n = 158071 inside the repository.

---

## 12. Scope

Everything above is confined to: four deterministically generated j = 0
(a = 0, CM discriminant −3) prime-field toy curves with p ≡ 1 mod 3 at
field_bits 12, 12, 16, 20; n ∈ {733, 3061, 41617, 158071}; B = ⌈√n⌉ ∈ {27, 55,
204, 397}; decomposition arity m = 2 only; `num_targets = max(10, B+10)`;
φ(x,y) = (ζ₃x, y) with r = 3; Python 3.13.1 / numpy 2.4.0 on macOS arm64; 20
runs in 132.595 s of a declared 5400 s, peak RSS 0.107 GB of 8 GB; no linear
system solver of any kind was run.

Claim tier **toy** (max field bits 20 ≤ 32). Not a cryptanalytic result, not an
attack, not an attack improvement, not a closure, not an impossibility claim. No
asymptotic-complexity claim is made in either direction: four toy points do not
establish α = O(1), and nothing here asserts α must grow. Negative findings close
exactly the four tested instances. Nothing extends to arity 3, to B > 397, to
j ≠ 0 curves, to generic curves, or to index calculus in general.
`docs/target-result-profile.md` is absent at this commit; it governs as an
instruction and is not cited as a present document. Under its rule A1,
constant-factor and log-cofactor improvements are not target-class, and the only
reproducible effect measured here is the constant factor r = 3.

---

## 13. Probe status

**RED-TEAM DIAGNOSTIC PROBES — NOT RUN RECORDS, NOT EVIDENCE.** Two scripts
(`armE_diag.py`, `armE_diag2.py`) were run in this session from a scratch
directory outside the repository, importing the committed harness read-only and
writing nothing into the repository or into `experiments/`. They carry no
manifest, no run id, no seed record and no environment block. Their outputs
appear in §2.3 as diagnosis only. They must not be cited as evidence by any
downstream record, must not enter any ledger record, and become evidence only if
re-executed and archived under a frozen contract (§11 item 2). No conclusion or
recommendation in this report depends on them: the mechanism in §2.1–2.2 is
established from committed data alone.

No commit was made. No committed artifact was modified. No status was changed.
No evidence, decision or correction record was created.
