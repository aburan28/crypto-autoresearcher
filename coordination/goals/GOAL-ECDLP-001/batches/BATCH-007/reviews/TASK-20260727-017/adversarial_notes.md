# TASK-20260727-017 — adversarial notes

Companion to `red_team_report.yaml` (RT-20260727-003). Snapshot under review:
commit `6eb3779987c6c0d3608193eff69df83c410f8cd1`, receipt validated against git.

This file does the job the Red Team contract asks for in the harder direction:
it argues **against** the census finding, and then **against my own OBS-1
verdict**, as forcefully as the evidence permits, before saying where each
argument actually lands. Nothing below is a cryptanalytic result and nothing
below is above toy tier.

---

## Part 1 — The strongest case FOR H-STR-002 and AGAINST the census

### 1.1 The mechanism is correct and nobody has touched it

φ(x, y) = (ζ₃x, y) is a genuine automorphism of a j = 0 curve over F_p with
p ≡ 1 mod 3. It is a group homomorphism. So if F is a union of φ-orbits and
R = P_{j1} + P_{j2} with both summands in F, then φ(R) = φ(P_{j1}) + φ(P_{j2})
is a relation with all summands in F. This is not a modelling assumption; it is
a one-line consequence of φ being an endomorphism. H-STR-002's `mechanism`
block is mathematically sound and **no finding in the census, and nothing in my
report, contradicts it.** Any reader who comes away thinking the endomorphism
idea was refuted has misread both documents.

### 1.2 Appending φ-images is correct practice, not fabrication

The census flagged (OBS-1) that lines 292–304 append φ-shifted rows and then
measure φ-structure on the same list. Stated that baldly it sounds like
circularity. But an actual attacker holding a φ-invariant factor base *would*
append those rows — they are free relations, and refusing to use them would be
strictly worse engineering. Discarding them (my arm B) handicaps the method
relative to how it would really be run. So arm B, taken alone, is **not** a
fair measurement of what the technique can do, and a report that led with arm B
alone would be committing the mirror of the error it complains about.

### 1.3 The inline measurements were real — and I proved it

The census could not settle whether the nine inline rows were ever measured.
It was scrupulous about this (`what_is_NOT_established` explicitly refuses to
claim they were never made). I settled it in the affirmative. Executing the
committed measurement functions at commit 6eb3779 reproduces **every one of the
nine `phi_alpha` values exactly**, including both `-` entries:

| bits | seed | B | n | claimed φ_α | reproduced φ_α |
|---:|---:|---:|---:|---:|---:|
| 12 | 1 | 27 | 733 | 9 | **9** |
| 12 | 2 | 55 | 3061 | 2 | **2** |
| 12 | 3 | 27 | 751 | 2 | **2** |
| 16 | 1 | 24 | 613 | 6 | **6** |
| 16 | 2 | 52 | 2791 | 27 | **27** |
| 16 | 3 | 204 | 41617 | 4 | **4** |
| 20 | 1 | 16 | 271 | – | **– (0 relations)** |
| 20 | 2 | 107 | 11527 | 20 | **20** |
| 20 | 3 | 397 | 158071 | 1 | **1** |

Every `n` and every `B` reproduces too. **The measurements happened.** Anyone
building a downstream record that hints at invention would be wrong, and the
census was right to refuse that inference on the evidence it had.

### 1.4 The declared ablation, when finally run, behaves as the spec predicted

`specification.yaml:36-39` declared a φ-ablation (same φ-invariant F, random
shift operator) and predicted α should "return to ~B". Census F9 established it
was never implemented. I implemented it. It does exactly what the specification
predicted: α = 27, 54, 196, 383 at B = 27, 55, 204, 397 — i.e. ~B. Taken on its
own, **the missing control comes back in the hypothesis's favour.**

### 1.5 The relation-density prediction holds, and the record understates it

H-STR-002 predicted density penalty < B/α. Measured penalty is 0.94–1.00 at
every instance — there is essentially **no** hit-rate cost to the φ-orbit
constraint. Charged properly (searches per relation row) the φ arm is *cheaper*
than random by 2.62×–3.21×. The "~2–3× penalty" in EV-STR-002 and
DEC-20260726-006 is not merely unsourced, it is **pessimistic**: it invents a
cost against the hypothesis that the data does not show.

### 1.6 So the honest verdict on the census's framing, from this side

Its finding-class (`artifact_integrity`) is right; its refusal to allege
fabrication is right and is now vindicated; its scope discipline is exemplary.
Where it goes wrong it goes wrong by being **too generous to the conclusion**,
not too harsh — see Part 3.

---

## Part 2 — The strongest case AGAINST my own OBS-1 verdict

I ruled OBS-1 fatal to the primary metric. Here is the best attack on that
ruling, and why each line of it fails.

### 2.1 "Your arm E is a strawman: it appends rows that are not relations"

**The attack.** In arm E I take a random factor base and synthetically permute
incidence vectors under the block-of-3 index shift. Those permuted rows are not
images of any relation under any map of the curve — `E.add` of the shifted
points does not equal the shifted target. So arm E's matrix is *fake*, and of
course a fake matrix can be made to look structured. Comparing a fake to a real
one and declaring the real one artifactual is a category error.

**Why it fails.** This is the strongest objection available and it inverts on
inspection. Arm E is not offered as a competing *method*; it is a **positive
control on the null**. The metric `phi_alpha` claims to detect a property of
the *matrix* — that it is nearly C₃-equivariant. Arm E exhibits a matrix that
scores better on that metric while possessing none of the *causal* property
(φ-invariance of F) the hypothesis says produces it. That is precisely what a
control is for. The fact that arm E's rows are mathematically worthless is the
**point**: the metric cannot tell worthless rows from genuine ones, so a low
score carries no information about whether genuine φ-structure is present.

A metric that assigns α = 0 to a matrix built by permuting arbitrary bit
vectors is not measuring the endomorphism. It is measuring the permuting.

### 2.2 "Arm B is unfair, so your 'no separation' claim is unfair"

**The attack.** Section 1.2 above: an attacker keeps the free rows, so arm B's
27/52/197/386 describe a method nobody would run.

**Why it fails — and this is the load-bearing step of the whole report.** I do
not need arm B. Arm E grants the *same* free extra rows, in the *same*
quantity, by the *same* insertion rule, and differs only in whether the factor
base is φ-invariant. Arm E scores **equal or better** (0, 1, 0, 1 against the
φ arm's 9, 2, 4, 1). So the free-rows advantage and the low α are separable,
and the low α tracks the free rows, not φ. Arm B is corroboration; arm E alone
would suffice. A defender who rejects arm B must still answer arm E.

### 2.3 "α = 9 at B = 27 disproves your own theory — construction would force α = 0"

**The attack.** I claim the append rule forces D ≡ 0. But the committed B = 27
run reports α = 9, not 0. If the construction really forced the answer, that
number could not exist. My theory over-predicts.

**Why it fails.** The theory predicts α ≤ (number of positions where the append
lost alignment), not α = 0 unconditionally. Alignment is broken by the dedup at
line 303 (`shifted_row not in relations`), by the `sum(shifted_row) > 0`
filter, and by truncated tail orbits when B ≢ 0 mod 3. Measured misalignment
counts against measured α:

| B | misaligned positions | α |
|---:|---:|---:|
| 27 | 9 | **9** |
| 55 | 5 | 2 |
| 204 | 4 | **4** |
| 397 | 1 | **1** |

Tight in three of four; the bound holds in the fourth. α = 9 at B = 27 is not a
counterexample to the theory — it *is* the theory: nine dedup collisions, nine
units of displacement rank. This table is the single most compressed statement
of what the primary metric actually measures.

### 2.4 "A C₃-equivariant matrix genuinely is easier to solve — you are denying real structure"

**The attack.** If α = 0 then M is exactly equivariant under the simultaneous
row/column action of σ, and that *is* real structure with real algorithmic
value.

**Why it partly succeeds, and where it stops.** It is correct, and I say so in
the report: an exactly C₃-equivariant matrix block-diagonalises over the group
algebra into 3 blocks of size B/3, so a dense solve costs 3·(B/3)² = B²/3. That
is a real saving of **exactly a factor r = 3** — which is also exactly the
saving the automorphism literature already gives, and exactly the 2.62×–3.21×
I measure in relation collection. Where the attack stops is the cost model:
α²·B·log B is the *Toeplitz-like* superfast-solver cost, whose displacement
operator must be built from the **nilpotent** lower shift (Z^B = 0). A
permutation of **order 3** generates equivariance, not Toeplitz-likeness. The
two structures are not interchangeable and the O(α²B log B) solver does not
apply. The claimed saving at B = 397 is B/(α² log B) ≈ 44×; the honest ceiling
is 3×. The 15× excess is the artifact.

The reductio settles it: at α = 0 the model prices a B × B solve at **zero
operations**. The harness papers over this with a `-1` sentinel at line 472
rather than treating it as a contradiction. A cost model that charges nothing
for the case its hypothesis most wants is not a cost model, and arm E reaches
α = 0 at B = 204.

### 2.5 "You ran unarchived probes and are now treating them as evidence"

**The attack.** My scratchpad scripts have no manifest, no seed record, no
environment block. By this repository's own rules that is exactly the defect I
am accusing EV-STR-002 of.

**Why it partly succeeds, and how I handled it.** It succeeds, and I concede it
without reservation. That is why my `next_concrete_action` is not "record my
numbers" but "have an independent Validator re-execute them from a clean
checkout and archive the result as a proper run package under a new EXP id".
My probes are falsification probes whose only claim is *reproducibility in
under fifteen minutes*; they are labelled as non-records throughout the report;
and none of them may be promoted to evidence without that re-execution. The
asymmetry with EV-STR-002 is not that my numbers are cleaner — it is that I am
not asking anyone to change a hypothesis status on them.

### 2.6 "The IndexError proves nothing about the numbers"

**The attack.** So `main()` crashes at line 451 for B ≢ 0 mod 3. The α values
still reproduce from the measurement functions, which run *before* the crash
point. So the crash is a cosmetic bug in a metric nobody cares about, and my
"the producing code is not in the tree" claim is overblown.

**Why it partly succeeds.** The α values are indeed genuine — I say so
repeatedly. The crash does not impugn them. What it does establish is narrower
and still matters: the committed end-to-end path **cannot** emit a run record
for B = 52, 55, 107 or 397, so those rows came from a driver that is not in the
repository, which is an independent reproducibility gap the census did not
find. And it *does* resolve census F6, which explicitly declined to determine
why the archive stops mid-instance at (12, 2): the rho record is written at
line 425, the φ arm dies at line 451, and (12, 2) is B = 55. No git archaeology
needed. If anyone later "fixes" line 451 and re-runs, that is a code change
requiring a recorded amendment — it cannot be slipped in as a re-run of the
same frozen experiment.

---

## Part 3 — Where the census's framing is too generous

The census says the finding is *not* a refutation because H-STR-002's
falsification condition requires **absence** of separation, and B = 27 shows
9 vs 27. Two problems.

**First, it quotes one of four conditions.** `H-STR-002.yaml:69-82` lists four.
Condition 4 — *"the fully-charged total cost (including penalty) exceeds
matched rho for all tested B and m"* — is met on committed data plus arithmetic,
with no new run required. Matched rho **solves** these same instances with
independently verified `discrete_log` certificates in 24, 156, 237 and 1104
group operations. The index-calculus arm at n = 158071 spends ≈ 2.5 × 10⁷
`s3_eval` on relation collection alone, forms no augmented system, measures no
rank, and solves nothing. Relation collection alone is 7×–79× the *entire*
modelled linear-algebra step, and that ratio grows with B. Condition 3 is not
met but is untestable as instrumented (`commutation_holds` is `True` by default
and `True` by construction — the four committed B = 2 records report it `true`
on runs with **zero relations**). Condition 1 is met under the ablation.

**Second, the separation it credits is the artifact it flagged.** The census
recorded OBS-1 and then leaned on the 9-vs-27 separation as its reason for
withholding refutation. Those two moves are in tension: having put the number in
question, it could not simultaneously rely on it. Arm B shows the separation is
27 vs 27 once the appended rows are removed; arm E shows a factor base with no
φ content scores 0.

**This is a scope *deflation*, not inflation.** The census understated its own
finding. That is the right direction to err, and it is still an error worth
correcting before TASK-20260727-018.

---

## Part 4 — What survives, stated as narrowly as the data permits

On nine j = 0 prime-field toy curves with p ≤ 877 879, n ≤ 158 071, B ≤ 397,
arity m = 2, at commit 6eb3779:

- **Survives:** the mechanism (φ(R) is a relation; the system is C₃-equivariant).
- **Survives:** a factor of **2.62×–3.21× ≈ r = 3** fewer relation-collection
  searches per relation row on a φ-invariant factor base. This is the known
  automorphism saving, correctly sized, appearing where theory says it should.
- **Survives:** essentially no relation-density penalty (0.94–1.00), contrary to
  the "~2–3×" in the records.
- **Does not survive:** `phi_alpha` as a measurement of φ-structure.
- **Does not survive:** the α²·B·log B vs 2B² comparison, its α = 0 degeneracy,
  and the "crossover at B ≈ 55".
- **Does not survive:** "structured beats Wiedemann by 3×–90×". Under the
  ablation the same model gives 67.5×, 147.5×, 761× and 1689× **worse**.
- **Never existed:** any end-to-end path. No RHS, no rank measurement, no target
  descent, no source recovery, no solve.

A factor of 3 is a constant factor. Under the governing target-result profile
rule A1 — the document is **absent** at this commit and is cited as policy, not
as a present file — constant-factor and log-cofactor improvements are not
target-class. Nothing here is a cryptanalytic result, an attack, an attack
improvement, a closure, or an impossibility claim, and nothing extends beyond
toy tier, beyond j = 0 curves, beyond arity 2, or beyond B = 397.
