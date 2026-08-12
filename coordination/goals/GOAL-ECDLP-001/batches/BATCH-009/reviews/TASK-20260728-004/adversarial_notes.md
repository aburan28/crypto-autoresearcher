# Adversarial notes — the strongest case against EXP-ENDO-001 as frozen

Task TASK-20260728-004. Contract commit `a6b5ca60b99f115e0e74b0d2932b19bd63084785`.
Verdict in `review_report.yaml`: **REVISE**.

This file states the case against the design as strongly as I can make it. It is
a design critique written before any execution. It contains no measurement, no
evidence, and no cryptanalytic claim. Two scratch scripts are referenced; they
are unarchived, are **not evidence**, and no argument below depends on them —
each load-bearing claim is settled on paper.

---

## 0. What is actually good, stated first so the criticism is not mistaken for dismissal

The pre-registration is real and checkable. `experiments/EXP-ENDO-001/` contains
`specification.yaml` and nothing else at `a6b5ca60`, at its parent, at `HEAD`,
and in the working tree. No `driver/`, no `results/`, no `runs/`. The contract
precedes measurement in commit order and any third party can verify it in one
`git ls-tree`. That is the strongest property of this submission and the campaign
should keep doing exactly this.

The basis labelling works. I went looking for the BATCH-007 failure mode — a
pre-registered number silently lifted from a scratchpad script — and did not find
it. Every number in the contract is either an arithmetic consequence of the
stated box rule, the classical birthday constant, or a declared tolerance. That
failure mode did not recur.

`CTRL-COLLAPSE` and `CTRL-CERT` are genuinely well designed, and the clause that
forbids reading any outcome into H-STR-002 or H-IC-001 should be kept verbatim.

Everything below is about the design.

---

## 1. The headline: the contract's own arithmetic makes `confirmed` unreachable

S3 requires the measured cost ratio to sit within a factor 2 of `2^(r+1)` **at
every rank, at every completed field size, for every family**. The contract
derives that prediction from `X = ceil(N^(1/(2r)))` and then reports only the
asymptotic simplification. The exact derived quantity is

```
rho(r) = 2 (2*ceil(N^(1/(2r))) + 1)^r / sqrt(N)
```

and its ratio to `2^(r+1)` is `((2*ceil(y)+1) / (2y))^r` with `y = N^(1/(2r))`.
At small `y` the ceiling is a large relative inflation raised to the `r`-th
power. Recomputed across the admissible `N` range (`N >= 2^(field_bits-4)`):

| bits | r=1 | r=2 | r=3 | r=4 |
|---|---|---|---|---|
| 16 | 1.00–1.02 | 1.06–1.41 | **1.55–2.60** | **1.60–3.81** |
| 20 | 1.00–1.01 | 1.03–1.20 | 1.27–1.65 | **1.74–3.57** |
| 24 | 1.00 | 1.02–1.10 | 1.10–1.49 | 1.27–1.93 |
| 28 | 1.00 | 1.01–1.05 | 1.14–1.31 | 1.49–1.99 |

Anything above 2.00 violates the pre-registered band. Those cells are at 16 bits
`r >= 3` and 20 bits `r = 4` — and the pre-registered degradation order drops
**28-bit cells first and 16-bit cells last**. The cells that fail
deterministically are exactly the cells that always survive.

So S3 cannot pass, so S1–S5 cannot all hold, so `confirmed` is unreachable —
for reasons contained in the contract, with no mathematical content whatsoever.

The campaign asked me to check for the `EXP-IC-001` v3 defect, a criterion that
could not fail. This is its dual: a criterion that cannot succeed. Both are the
same underlying error — pre-registering a threshold without evaluating it against
the contract's own arithmetic at the sizes to be run.

S5 closes the door independently. `CTRL-BASELINE` specifies "matched Pollard rho
**with negation**", which is `|Aut| = 2`. S5 and F4 calibrate against
`0.886 sqrt(N/|Aut|)` with `|Aut| = 6` and `4`. If the executor implements what
is written, the ratio is `sqrt(3) = 1.73` on J0 and `sqrt(2) = 1.41` on J1728 —
both outside the 20 % band, S5 fails, `confirmed` is blocked again, and F4 does
*not* fire because it requires a deviation on the low side. Outcome: `mixed`.

---

## 2. F1 — the one outcome anyone cares about — cannot fire for the stated reason

Split the meet-in-the-middle cost:

- **list build**: `(2X+1)^r` entries. A deterministic function of `(N, r)`. No
  curve, no eigenvalue, no `k`. **Identical by construction in arms A, B and D.**
- **collision search**: expected position about `N / |L1| = sqrt(N) / 2^r`.

The structure-sensitive term's share of the total is about `4^(-r)`:

| r | share of total cost that any structural effect could touch |
|---|---|
| 2 | 6.25 % |
| 3 | 1.6 % |
| 4 | 0.4 % |

The monotonicity tolerance is 15 %. So an *oracle* that hit a witness on the
first probe of the second list would move `rho(r)` by less than the tolerance at
every `r >= 2`. No structural effect confined to the search stage can fire F1.
This also makes `CTRL-RANDSUB` vacuous against the thing it is supposed to
control: arm D has no curve, so its `mitm_cost` is a simulated enumeration count
— the same arithmetic as the dominant term of arms A and B. Its "match within the
acceptance band" is an arithmetic identity, not an empirical agreement. Its one
real job is absorbing the ceiling artifact, which it does.

The list-build term shrinks only if `(a_i) -> sum a_i lambda_i` is non-injective
on the box, i.e. only if a small-coefficient integer relation exists among the
eigenvalues. There is exactly one place in the design where that happens, and the
contract calls it genuine. Which brings us to the priority question.

---

## 3. The synthetic-cell problem is worse than the Coordinator's own correction says

`INT-BATCH009-M` caught that `r = 4` at j = 0 is synthetic and stopped one step
short. Here is the step it stopped short of.

For an ordinary elliptic curve over a prime field, `End(E) ⊗ Q` is an imaginary
quadratic field, so the **Z-module generated by the efficiently computable
eigenvalues has rank exactly 2**. The specification sets `genuine_r_bound: 3` for
J0 because three distinct *scalars* exist — `1`, `lambda`, `lambda^2`. Distinct
scalars are not Z-independent coordinates, and `r` in this design is a coordinate
count.

Concretely, with no computation at all: the two roots of `L^2 + L + 1 = 0 mod N`
sum to `-1` by Vieta. Therefore `1 + lambda_2 + lambda_3 = 0 mod N` **identically,
on every J0 instance**, and

```
(1, 1, 1, 0, 0, 0) ∈ W_3     ⇒     lambda_1^inf(W_3) = 1 exactly, for every N
```

against a predicted `N^(1/6)` — about 25 at 28 bits. The relation persists at
`r = 4`. The specification *states* this relation in `synthetic_rank_rule`
(`lambda_3 = -1 - lambda_2`) and then labels the cell genuine. H-ENDO-001's own
`interpretation_limits` note that the supersingular endomorphism ring has rank 4,
which presupposes the ordinary rank-2 fact that contradicts `genuine_r_bound: 3`.
The record contains its own refutation.

Four consequences, all in cells the contract calls genuine:

1. **S2/F3.** Forty J0 cells (`r = 3` and `r = 4`, four sizes, five seeds) enter
   the shrinkage regression at `y = log_N(1) = 0` against predicted `1/6` and
   `1/8`. They are not filtered out by the exact-enumeration restriction — with
   first minimum 1, enumeration is instantaneous.
2. **Cost and memory.** The scalar map factors through a two-dimensional
   quantity, so the P-side list has at most `(4X+1)^2` distinct images rather
   than `(2X+1)^3`: about 11,025 at 28 bits against a predicted peak of
   `2^3 sqrt(N) = 131,072`. A factor 12 miss.
3. **HEUR-1.** `W_3` contains the whole rank-2 family `{(t,t,t,u,u,u)}`, so the
   box census counts about `(2cX+1)^2` trivial witnesses and the Poisson
   chi-square rejects — an artifact of the CM relation, not of equidistribution.
   Arm F has no criterion that can say so (see §5).
4. **F1's false-positive route.** If the driver enumerates *distinct scalar
   images* rather than coefficient vectors, `rho(3)` on J0 collapses far below
   `rho(2)`, `CTRL-RANDSUB` does not reproduce the drop, and F1's stated
   conditions are met exactly. The pre-registered reading — "the endomorphism
   lane carries exploitable structure beyond the pinned index … would collapse
   the load-bearing exit-map claim of IDEA-20260727-005" — would be precisely
   backwards. The trigger is a **redundant coordinate**: the opposite of
   exploitable structure.

So: F1 is either unreachable (driver enumerates coefficient vectors) or reachable
only with a false interpretation attached (driver enumerates scalar images).
Either way the campaign's designated "single most informative outcome" does not
work.

**Is this the phi_alpha defect from BATCH-007?** Yes, same class, with an
aggravation. There a metric turned out to count row-insertion bookkeeping. Here
the primary *cost* metric is, on its dominant term, a deterministic function of
`(N, r)` with no curve in it — so on synthetic cells arms A, B and D are the same
computation performed three times — and the primary *geometric* metric collapses
to the constant 1 on cells labelled genuine. The difference, and it is a real
credit to the contract, is that this design declares the synthetic limitation
honestly and forbids attack claims from those cells. It simply drew the line one
rank too high.

**Cheapest discriminating control (RC-1).** A random-sublattice arm whose
eigenvalues are drawn uniformly but *forced to satisfy the same relation*
(`lambda_1 + lambda_2 + lambda_3 = 0 mod N`) with no CM origin. If arms A at
`r >= 3` and this control agree, any F1 firing is coordinate redundancy and not
endomorphism structure. It costs a variant of an existing lattice-only arm.

---

## 4. `2^r` versus `sqrt(N)`: the Coordinator's Q4 confound, answered

They do **not** collapse in the ratio `rho(r)`, which is the primary metric. But a
worse degeneracy occurs in the same cells.

At 16 bits the subgroup rule permits `N` as small as `2^12`. The `r = 4` list is
then `9^4 = 6561 > N = 4096`: the enumeration covers **more scalars than the group
contains**, a collision is guaranteed trivially, and the cost exceeds exhaustive
search. Those cells are not in the birthday regime at all; they are saturated,
and `rho(4)/rho(1)` there is a ratio of two saturated quantities.

Add the ceiling inflation of 2.1×–4.4× from §1 and the verdict is: the separation
between meet-in-the-middle cost and birthday cost is clean at 24 and 28 bits,
degenerate at 16 bits for `r >= 3`, and marginal at 20 bits for `r = 4`.

And the design degrades in the wrong direction. The pre-registered order drops
28-bit cells first, 24-bit second, so under any budget pressure the run set
collapses onto exactly the sizes where the confound is worst. The declared
consequence (S3 `INCONCLUSIVE` below four sizes) is honest but converts a budget
shortfall into a guaranteed non-answer rather than repairing anything.

---

## 5. Criteria that turn on choices the contract never makes

A pre-registration whose verdict depends on unstated analysis choices is not a
pre-registration. Five such choices, each of which flips a criterion:

| unpinned choice | what it flips |
|---|---|
| S2 pooled across arms vs per family | J0-only fit ≈ 1.30 (F3 fires); pooled ≈ 1.05 with R² at the 0.90 floor |
| S3 aggregation over the five seeds (mean? median? per seed?) | within-cell scatter from the ceiling is 2–3×, so the readings disagree |
| MITM early termination | full lists ⇒ `r=1` cost `4 sqrt(N)` vs BSGS `1.5–2 sqrt(N)`, ratio 2.0–2.67 against `CTRL-GENJ`'s "within a factor 2" — at or over threshold with zero slack; streamed ⇒ ≈ `2.5 sqrt(N)`, passes |
| BSGS counted worst-case or expected | changes the `CTRL-GENJ` ratio by a third |
| rho's stored-entry count `w` | F6's threshold divides by it; with Floyd (`w=2`) F6 can never fire, with distinguished points `w` is a free knob. **F6 as written is undecidable.** |

Two of eight arms have no criterion at all: `RUN-ENDO-001-F-H1` and
`RUN-ENDO-001-G-H2` validate HEUR-1 and HEUR-2 and appear in no S or F clause.
They will produce numbers no criterion consumes — an open invitation to post-hoc
reading, guaranteed to be exercised because §3 shows the HEUR-1 census *will*
fail on the J0 cells.

Arm G is also aimed at the wrong statistic: it KS-tests `lambda_2/N` against
uniform, but the property that controls the first minimum is the **absence of
small integer relations** among the `lambda_i`. Arm G would pass on the
maximally degenerate configuration §3 exhibits.

---

## 6. A finite-size term the S2 band does not allow for

The measured quantity is `log_N(lambda_1) = 1/(2r) + ln(c)/ln(N)`, where `c` is
the O(1) constant by which the actual first minimum misses the Minkowski bound.
At 16–28 bits `ln(N)` is 11 to 19, so an ordinary `c` in `[0.2, 0.8]` displaces
`y` by 0.02–0.09 — and the displacement is **largest at `r = 1`**, where the
constant sits furthest from 1, which systematically *depresses* the fitted slope.
A rough estimate puts the clean-design slope near 0.79 at 16 bits and 0.88 at 28
bits, straddling the 0.85 floor.

The band `[0.85, 1.15]` is centred on the asymptotic value and pre-registers no
finite-size allowance. F3 is therefore at material risk of firing, and F3's
pre-registered reading — "the Minkowski minimum is not being attained, the box is
the wrong size, and the cost comparison is UNINTERPRETABLE" — would be a false
diagnosis of a normalization choice. F3 *overrides* a partial confirmation.

Note the two artifacts pull in opposite directions: §3's zeros push the slope up,
§6's finite-size term pushes it down, and which wins depends on the pooling
choice the contract never makes. The S2 verdict is a coin flip between two
artifacts.

Fix: fit `lambda_1 = c_r * N^(1/(2r))` with a free per-rank constant — regress
`log lambda_1` on `log N` within each rank — and band the **exponent**.

---

## 7. The mechanism the contract offers is not the mechanism that is true

STEP 5 says: the determinant never moved, therefore shortness bought by adding
coordinates is not shortness that can be searched for more cheaply. And if
`rho(r)` falls, "either the determinant is not pinned or the balanced split is
not the best decomposition."

That dichotomy omits the true third explanation, and it is the important one.
**`W_r` cannot be constructed by an attacker.** Its congruence coefficients are
`(lambda_i, k*lambda_i)` and involve the unknown `k`. If `W_2` could be written
down, LLL in dimension 4 returns a witness of norm about `3.4 * N^(1/4)` in
polynomial time, and `k = -A/B mod N` follows immediately — which would break
ECDLP outright. So the pinned determinant emphatically does **not** protect
anything; non-constructibility does. The enumeration cost is set by the box side
and the split, not by the determinant at all.

This matters for what gets written down afterwards. A `confirmed` verdict would
attach a true observation (cost does not fall with `r`) to a false mechanism (the
determinant is why). And it matters for P1's value: `index = N` is a one-line
consequence of `End(Z/N) ≅ Z/N`, it needs no experiment, and it is *irrelevant to
the attack's cost*. On synthetic and RANDSUB cells `CTRL-EIGEN` degenerates to
`[lambda]P = [lambda]P`, so S1 there is a self-test of the HNF routine over the
integers — correct to run, not a test of anything at issue.

Which undercuts the rerank rationale. The snapshot message says this experiment
"gates IDEA-20260727-005's classification barrier". It cannot. The load-bearing
part of that barrier is which homomorphisms are **efficiently computable** — a
computational statement. This design fixes the eigenvalues by fiat and no arm
searches for an unexpected exit map. The gating value that outranked the
COMMITTED `EXP-STR-004` is not delivered by the design as frozen. That is not by
itself a reason to reverse the rerank, but it must not be repeated in
`EV-ENDO-001`.

---

## 8. Where this sits against the real baselines

| algorithm | time | memory |
|---|---|---|
| Pollard rho with negation | ≈ `0.886 sqrt(N/2)` | `O(w)`, linear parallel speedup (van Oorschot–Wiener) |
| rho with automorphism quotient (Wiener–Zuccherato; Duursma–Gaudry–Morain) | ≈ `0.886 sqrt(N/|Aut|)`, at most `sqrt(6) = 2.449×` better | `O(w)`; degraded by fruitless cycles unless handled |
| BSGS | ≈ `1.5–2 sqrt(N)` | `sqrt(N)` |
| **the algorithm under test** | `2 (2 ceil(N^(1/(2r)))+1)^r` ≈ `2^(r+1) sqrt(N)` | `2^r sqrt(N)` |

Dominated by BSGS by about `2^r` in **both** time and memory at every rank —
including `r = 1`, where the derived cost is exactly 2× BSGS — and dominated
absolutely by rho on memory. There is no time–memory point where it wins:
shrinking the stored list to `w` forces the join to scan about `N/w`, the
classical Shanks line, strictly worse than rho's `sqrt(N)/m` parallel line for
`w < sqrt(N)`.

Consequence: **no outcome of this experiment, F1 included, can be an attack
improvement.** The lane sits above the known Pareto frontier at every point. Nor
can it be target-class under the governing rule A1 — the only positive quantity
available is a `sqrt(6)` constant, which the contract already excludes itself.

---

## 9. Budget

About 17 M point additions across arms A and B (28-bit `r=4` is `25^4 = 390,625`
entries per side, 781,250 additions per cell, ×5 seeds). In CPython with one
modular inverse per affine addition that is roughly 50–140 s of arithmetic,
realistically 150–600 s with interpreter and hash overhead. It fits inside
1800 s/arm and 7200 s total, and 390,625 dictionary entries is well inside 8 GB.

But only under the incremental one-addition-per-entry convention, which appears
**only in derivation prose**. With a fresh scalar multiplication per entry (≈ 42
additions at 28 bits) arm A alone is ~40× more expensive and blows both caps. The
binding risk is implementation convention, not CPU.

Two secondary gaps: `8 × 1800 s` exceeds the 7200 s total, so the global cap can
be reached before arms G and H start, and nothing covers an arm that never
begins (S5 on zero data is undefined); and arm order is unspecified even though
F4's own text makes calibration gate the interpretation of every other number —
`H-RHOCAL` should be pre-registered to run first.

---

## 10. What I am **not** claiming

- No hypothesis status moves. H-STR-002 and H-IC-001 remain `weakened`; nothing
  here touches them.
- No evidence or decision record is created, and no execution is authorized.
- The endomorphism lane is **not** refuted by this review. The lane's question is
  legitimate; the instrument as frozen cannot answer it.
- The design is **not** rejected. Every blocking objection is repairable by text
  changes plus one extra control arm — which is why the verdict is REVISE and not
  REJECT/FAIL.
- Nothing here is a cryptanalytic result, a hardness result, a lower bound, a
  closure, or an impossibility claim, and no claim above toy tier (≤ 28 bits) is
  available from this contract under any outcome.
- I checked the receipt-ordering gap (`INT-BATCH009-C`) rather than routing
  around it: the receipt was committed separately in `64dc636e`, which touches
  only the receipt. It does not weaken the pre-registration. No hash was
  fabricated anywhere in this review.
- Filename note: the dispatch card declares `contract_review.yaml`; the launching
  task specified `review_report.yaml` and `adversarial_notes.md`. I followed the
  launching task exactly and created no third file. The Coordinator must
  reconcile `artifact_paths` before `TASK-20260728-009` runs.

---

## 11. The single recommended action

Issue `protocol_amendment` **EXP-ENDO-001 v2** before `TASK-20260728-005`
executes, and keep that task blocked until v2 is snapshot-committed and
independently re-reviewed — per `INT-BATCH009-E` the dispatcher will not enforce
this, so it is the Coordinator's gate. The amendment carries, and only carries:

- **(a)** `genuine_r_bound: 2` for both CM families; every `r >= 3` cell labelled
  synthetic; controls **RC-1** (relation-matched random sublattice) and **RC-3**
  (reject synthetic draws admitting a relation `sum c_i lambda_i = 0` with
  `max|c_i| <= X`). *[§3]*
- **(b)** S3 rebanded on the exact per-cell formula
  `2 (2 ceil(N^(1/(2r)))+1)^r / sqrt(N)`; `2^(r+1)` relabelled
  derived-**asymptotically**. *[§1]*
- **(c)** rho variant pinned per arm and calibrated against its own `|Aut|`, with
  fruitless-cycle handling pre-registered. *[§1]*
- **(d)** enumeration convention pinned; F1 required to survive RC-1; **RC-4**
  (distinct-scalar-image counter reported per cell) added. *[§2, §3]*
- **(e)** S2 pooling, S3 seed aggregation, MITM termination, BSGS counting and
  rho's `w` all pinned in criterion text; **RC-5** (report the van
  Oorschot–Wiener time–memory line for both algorithms). *[§5]*
- **(f)** S2 refitted as `lambda_1 = c_r N^(1/(2r))` with a free per-rank
  constant, band on the exponent. *[§6]*
- **(g)** acceptance criteria for arms F and G; pre-registered arm order with
  `H-RHOCAL` first; **RC-2** (known-answer test for the first-minimum routine —
  the J0 `r = 3` lattice supplies one for free, with `lambda_1 = 1` provable from
  Vieta). *[§5, §9]*

If only one of these can be done, do **(a)**: it is the defect that reaches a
cell the contract calls genuine, and it is the one that could turn a bookkeeping
artifact into a reported reopening of the endomorphism lane.
