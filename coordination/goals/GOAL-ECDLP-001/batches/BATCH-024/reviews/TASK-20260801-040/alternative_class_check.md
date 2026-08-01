# ALTERNATIVE-CLASS CHECK — ALT-CLASS-DEP-1, AGAINST THE DRIVER SOURCE

TASK-20260801-040, reviewer duty 3, including the **mandatory DESIGN-TRAP-1
re-derivation**. Verdict carried in `contract_review.yaml` (**REVISE**).

This is the duty the batch exists for. BATCH-023 certified against a plant that
moved only the e₁ marginal and then spoke of "power against dependence"; the
whole point of EXP-DEP-001 is not to repeat that. So this document does not
accept a single structural claim as written. Everything below is re-derived from
`experiments/EXP-DEP-001/implementation/dep001_driver.py` and then re-tested by
executing the driver's own functions.

---

## 1. The DESIGN-TRAP-1 invariance statement, derived independently

**Setup.** An arm is `n = 130816` pairs `(e1_i, e2_i)`. The two chi-square
statistics read the joint contingency table

  `N_K[b][c] = #{ i : bin_K(e1_i) = b, bin_K(e2_i) = c }`,  `bin_K(e) = (e*K)//p`,

for `K ∈ {16, 64}` (`EQD._cell_index`). Every plant leaves `e1` untouched and
replaces `e2` by a rearrangement of the **same multiset**.

**Step 1.** Let `S_1, …, S_r` partition the record indices and let `σ` permute
`e2` values only within each `S_j`. Then for every `j` the multiset
`{ e2_i : i ∈ S_j }` is unchanged, hence so is `{ bin_K(e2_i) : i ∈ S_j }`.

**Step 2.** If each `S_j` is *contained in* a single `e1` bin at resolution `K` —
i.e. the strata **refine** the `e1` binning — then each row of `N_K` is a
disjoint union of strata lying in it, and by step 1 each such row's column
multiset is unchanged. **`N_K` is exactly invariant, entry by entry.**

**Step 3 — the tautology.** All four statistics are functions of the two arms
only through `N_K` (the chi-squares) and through the one-dimensional empirical
distributions of `e1` and of `e2` (the KS statistics), all invariant. So the
planted arm returns the *same statistic values as its source arm*, and comparing
it against a fresh null is distributionally a null-versus-null comparison. The
exceedance rate is the nominal false-rejection rate **at every rung, by
construction**. Such a "power curve" measures the threshold, not the power — it
would read as a finding of zero power while measuring nothing. This is exactly
the contract's DESIGN-TRAP-1 statement, and I obtain it independently.

**Step 4 — the resolution lattice, which the trap statement does not spell out.**
`floor(floor(e·64/p)/4) = floor(e·64/(4p)) = floor(e·16/p)`, so **the K = 64 grid
refines the K = 16 grid exactly**. Therefore invariance at K = 64 *implies*
invariance at K = 16 (marginalise four-by-four), while invariance at K = 16 does
**not** imply invariance at K = 64. The trap has two depths: strata equal to the
K = 16 e₁ bins are invariant at K = 16 only; strata equal to the K = 64 e₁ bins
are invariant at both. The handoff is right to require both resolutions be
checked separately.

**Numerical confirmation of my own derivation.** I built both trap plants on an
independent synthetic arm (p = 46663, n = 130816):

| trap construction | K = 16 cells moved / TV | K = 64 cells moved / TV |
|---|---|---|
| permute e₂ within e₁-**K16** strata | **0 / 0.000000** | 11283 / 0.086251 |
| permute e₂ within e₁-**K64** strata | **0 / 0.000000** | **0 / 0.000000** |

Exact invariance, and the one-sided implication between resolutions, both
confirmed.

---

## 2. C1, C2, C3 — each actually constructed, checked at source

| class | object | driver function | lines | marginals |
|---|---|---|---|---|
| C1 | OBJ-PLANT-DEP-rho | `plant_copula` | 426–445 | e₁ untouched; e₂ a permutation of its own multiset |
| C2 | OBJ-PLANT-DEP-CELL-eps | `plant_cell` | 455–501 | same |
| C3 | OBJ-PLANT-DEP-BLOCK-q | `plant_block` | 504–529 | same |

All three exist, all three are wired into `run_measurement` (which references
`LADDER_RHO`, `LADDER_CELL`, `LADDER_BLOCK` and all three plant functions), and
each implements its 034-contract prose faithfully. Marginal bit-identity is not
merely by construction: `plant_arm` returns `e1s.copy()` so the CTRL-DEP-MARG e₁
digest comparison is a real comparison of two separately computed digests, and
`marginal_integrity` compares four sorted-array sha256 digests plus four
histograms at both resolutions count by count, on **every** arm. Measured: 440
planted calibration arms, `CTRL_DEP_MARG_all_ok = true`, `marg_mismatch_locations
= []` at both cells.

**Both marginals bit-identical: confirmed for all three, at source and in the
archive.**

---

## 3. Does each move the K = 16 and K = 64 joint tables? — and the second trap

### 3.1 Table movement (the literal DESIGN-TRAP-1 criterion)

Measured by me on the same synthetic arm, using the driver's own plant functions:

| construction | K16 cells moved / TV | K64 cells moved / TV |
|---|---|---|
| C1 rho = 0.0025 | 2997 / 0.022910 | 12981 / 0.099231 |
| C1 rho = 0.05 | 3724 / 0.028467 | 13048 / 0.099743 |
| C1 rho = 1.00 | 120572 / 0.921692 | 126816 / 0.969423 |
| C1 rho = 0 (OBJ-PLANT-DEP-0) | 3022 / 0.023101 | 12972 / 0.099162 |
| anchor (comonotone) | **120572 / 0.921692** | **126816 / 0.969423** |
| C2 eps = 0.005 | 234 / 0.001789 | 551 / 0.004212 |
| C2 eps = 0.02 | 418 / 0.003195 | 1601 / 0.012239 |
| C2 eps = 0.25 | 1593 / 0.012177 | 6355 / 0.048580 |
| C3 q = 0.05 | 640 / 0.004892 | 2756 / 0.021068 |
| C3 q = 0.25 | 1485 / 0.011352 | 6386 / 0.048817 |
| C3 q = 1.00 | 2965 / 0.022665 | 12707 / 0.097136 |

**Per construction, at what resolution the reordering moves mass and why it is
not invariant:**

* **C1** — `e2_new[i] = sort(e2)[rank(z2)_i]` with `z2 = ρ·Z1 + √(1−ρ²)·W`. The
  rearrangement is a **global rank matching** over all n indices, confined to no
  stratum at any resolution, and it depends on the ranks of e₂ (through
  `sort(e2)`) as well as on e₁. Step 2 of the derivation never applies. To first
  order in ρ, the cell deviation from independence is ρ times the product of the
  two per-cell Hermite-1 integrals, nonzero on every cell whose rank-range is not
  symmetric about ½ — and no cell of either grid is, since ½ is a bin boundary at
  both K. **Not invariant at K = 16, not invariant at K = 64.**
* **C2** — line 489 is `keep = bins[u] != bins[v]` with `bins = (e1*16)//p`. The
  constraint is the **exact negation of the trap**: the driver *requires* the two
  records to lie in different e₁ strata where the trap would have required the
  same one. A transposition fails to move the K = 16 table only if
  `bin16(e2[u]) = bin16(e2[v])` (probability ≈ 1/16); at the smallest rung
  eps = 0.005 that is 327 transpositions all landing in that sub-case
  simultaneously. Different K = 16 rows ⇒ different K = 64 rows, since K = 64
  refines K = 16, so the K = 64 table moves too (per-pair failure ≈ 1/64).
  **Not invariant at either.** Charge added: the effective mass moved at K = 16
  is ≈ (15/16)·eps, not eps.
* **C3** — two strata at the e₁ rank median, uniform permutation of chosen e₂
  within each. The strata are **coarser** than the grid — roughly eight K = 16
  bins and thirty-two K = 64 bins each — so they do not refine the e₁ binning and
  step 2 does not apply. A permuted record's e₂ lands in a different e₁ bin with
  probability ≈ 7/8 at K = 16 and ≈ 31/32 at K = 64. **Not invariant at either.**

**Verdict on the literal criterion: no construction is invariant at K = 16 or at
K = 64, and none is invariant at one resolution and not the other. DESIGN-TRAP-1
in its stated form has NOT recurred.** The contract's prose reason for each — "moves
mass across e₁ bins", the `!=` constraint, "strata far coarser than the grid" —
is accurate against source.

### 3.2 …but the trap recurs by a second route — **TRAP-DISTRIBUTIONAL**

DESIGN-TRAP-1 is stated as *exact table invariance*. C2 and C3 escape that and
land in the identical tautology by distribution.

**Derivation.** In both `plant_cell` and `plant_block` the permutation σ is built
from **e₁ and fresh randomness only, never from e₂**: `plant_cell`'s admissible
pairs are constrained by `bins`, a function of e₁, and its candidate pairs come
from `rng.permutation`; `plant_block`'s strata are e₁ ranks and its choices and
within-stratum permutations are `rng` draws. If the source records are i.i.d. and
e₂ is independent of e₁, then conditional on the e₁ vector the e₂ vector is
**exchangeable**, and applying any e₂-independent σ leaves the joint law
**exactly unchanged**. C2 and C3 are dependence-**destroying**, never
dependence-creating; the largest deviation either can produce is bounded by the
dependence the source already carries.

C1 is the exception, and this is the structural reason it is the sound
construction: `sort(e2)[rank(z2)]` re-assigns the **order statistics** of e₂ by a
rank that is correlated with e₁, so it *imposes* a coupling that the source need
not have had.

**The cheapest discriminating control, run.** 40 paired replicates at
p = 46663, n = 130816, on an exactly independent synthetic source, comparing
plant-versus-fresh-null against source-versus-fresh-null through the driver's own
`statistics_of` and the imported EXP-EQD-001 code path. Mean shift in null σ:

| arm | STAT-CHI-16 | STAT-CHI-64 | STAT-KS1-E1 |
|---|---|---|---|
| C1 rho = 0.05 | **+7.33** | **+1.96** | 0.000 |
| C1 rho = 1.00 | **+10182** | **+2554** | 0.000 |
| **C2 eps = 0.25 (top rung)** | **+0.21** | **+0.16** | 0.000 |
| **C3 q = 1.00 (top rung)** | **+0.15** | **+0.19** | 0.000 |

**C2 and C3 at the very top of their ladders are indistinguishable from the
null.**

**Does this transfer to the real source?** The archived calibration says yes, on
this instrument, at these two cells. The *maximally* destructive member of that
family — the uniform permutation, OBJ-PLANT-DEP-0, which the file's own D5 block
classifies correctly as dependence-destroying — produces on the real INT-2 source
a K = 16 joint TV of **0.023457 / 0.023241** (the multinomial noise floor for two
130816-sample tables over 256 cells), plant Spearman **−0.000045 / +0.000091**,
source Spearman **0.00034 / 0.00023** on the representative draws, and exceedance
counts at the nominal level (2, 1, 5, 2 and 1, 6, 0, 2 of 200 — all recounted by
me). **Total destruction of the source's dependence is undetectable on this
instrument, as measured.** Every C2 rung and every C3 rung destroys a subset of
what that permutation destroys.

**The right question, asked of the right parameter** (inventor protocol §3):
what should the K = 16 joint TV do as eps increases across DEP-LADDER-CELL? It
should rise. On the analysis and the measurement above it will stay flat at the
noise floor. A quantity that stays flat when the parameter meant to move it
increases is the artifact tell — and here the correct disposition of that flat
curve is **D-1**, not a detection floor.

**Consequences.**

1. `eps_det = NONE_ON_LADDER` is **forced by construction**, not measured as low
   power. D-4's mandated ratio `eps_det / 0.02` **cannot be produced under any
   outcome**.
2. DDV-3 over DEP-LADDER-BLOCK measures the nominal rate at every rung.
3. **C3 has no guard at all.** D-1 has a Spearman leg for the RHO ladder and a TV
   leg for the CELL ladder, and **no leg for the BLOCK ladder**; DEP-LADDER-BLOCK
   has no calibration endpoint (the file discloses the missing endpoint, but not
   the missing guard); yet ALT-CLASS-DEP-1 contemplates certifying C3 "at the
   fractions measured" on a valid run. A certification with no null-object
   control and no artifact-tell guard is exactly what `docs/inventor-protocol.md`
   §3 forbids.
4. The one guard that does bite is D-1's CELL-ladder TV leg, which will correctly
   fire. The design's precedence therefore *works* — the honest outcome of the
   measurement arm as frozen is `inconclusive` on the instrument.

### 3.3 A third structural blindness: two of four statistics cannot move

`STAT-KS1-E1 = stat_ks1(e1_a, e1_b)` reads only the e₁ arrays, which every plant
leaves bit-identical. `STAT-KS1-E2 = stat_ks1(e2_a, e2_b)` is a function of the
empirical distribution of e₂ only, and every plant returns a permutation of the
same e₂ multiset. **Both take identical values on a plant arm and on its source
arm, for every family and every rung, deterministically.**

Verified by execution: bitwise equality of both KS values for copula rho = 0.5,
the comonotone anchor, cell eps = 0.25 and block q = 1.00, while STAT-CHI-16 on
the same arms moved by factors 24.9, 308.6, 1.005 and 1.119.

So the effective certifying set is **two**, not three. STAT-KS1-E1 is named a
certifying statistic by CERT-DEP-1 and has exactly the null distribution at every
rung of every ladder. The specification's rationale for *retaining* STAT-KS1-E2
here — "a dependence-only plant permutes e₂, so an e₂ marginal probe is a
MEANINGFUL member of the family here" — is **wrong**: permuting e₂ is precisely
the operation a KS statistic on e₂ cannot see. And the file's report that
STAT-KS1-E2 "did not fire even at maximal monotone dependence … RECORDED AND NOT
EXPLAINED" has a complete deterministic explanation, supplied here.

This is why `attainability_check.md` finds ATTAIN-RR-DEP-1's D-2, D-3 and D-4
entries evidentially unsound: each cites a KS non-detection as though it were
information about a dependence-only object.

---

## 4. Does the certified list overstate what the ladders reach?

**No — and on this the file is exemplary.** `certified_deviation_classes_after_calibration: []`,
`certified_rung_set_after_calibration: []`, `rho_det` and `eps_det` the literal
`UNDETERMINED_NO_LADDER_RUN`. C1, C2, C3 each carry "UNCERTIFIED AS AT THIS
FREEZE". The anchor is stated to certify nothing. The naming obligation states
that the honest form of any power statement names **no** class. C0 is correctly
labelled a carried-forward **e₁-marginal** class, not a dependence class. I
searched the file for any statement implying a class it has not earned and found
none.

**But the certified list is under-scoped for the future**, and the amendment
should fix it before any run:

* C2 and C3 should not be certifiable at all under the present constructions
  (§3.2), whatever the ladder returns.
* Any C1 certification should say **two** effective certifying statistics, not
  three (§3.3).
* The `eps_det / 0.02` ratio should carry the caveat that eps counts exchanged
  pairs of a *destroying* relabeling while delta counts re-randomised e₁
  coordinates of a *marginal-moving* plant, and that ≈ 1/16 of C2's exchanges are
  table-neutral at K = 16. It is not the like-for-like comparison the contract
  calls it.

---

## 5. U1 through U6 — is anything under them silently claimed?

**Nothing is.** No deliverable statement in the frozen file claims power against
anything on any of these axes.

**U1 is restated in full, not merely referenced**, at
`alternative_class_declaration_restated.status_of_each_class_as_it_stands_after_this_calibration.U1.restated_in_full_rather_than_referenced`,
and it names the load-bearing case correctly: a two-sample design is blind by
construction to any deviation both arms share, because both arms carry it and the
statistics compare the arms to each other, so it cancels identically; the INT-2
fibre-invariant map induces whatever dependence it induces on the null arm **and**
on every plant's source arm, so dependence intrinsic to the map is invisible to
every member of STAT-DEP-1. I verified this against source: both arms are drawn
by `draw_null_arm` through the same code path, and `statistics_of` compares them
to each other. The statement that no increase in R_REPS, no grid refinement and
no ladder extension can change it is correct.

**A sharpening the file does not make, and should.** U1 and §3.2 are the same
phenomenon seen from two sides. U1 says a deviation shared by both arms is
invisible; §3.2 says C2 and C3 can only *remove* a deviation the source already
has, and the source's own deviation is exactly the shared one U1 declares
invisible. **C2 and C3 are therefore attempts to detect, by subtraction, a
quantity U1 declares undetectable.** The file carries both statements and does
not connect them. Connecting them is the single cheapest way to see why the CELL
and BLOCK ladders cannot work as designed.

* **U2** — carried, with the correct smallest CELL rung eps = 0.005. Given §3.2
  the honest scope of U2 is much wider than stated.
* **U3** — carried and accurate.
* **U4** — carried, and the file itself notes the sting: STAT-KS1-E2, the only
  statistic that probes e₂ directly, is non-certifying. §3.3 sharpens this: it is
  not merely non-certifying, it is **incapable of moving**, so U4 is closed by
  this design in neither direction and could not be.
* **U5** — carried; claim tier toy; two toy instances, Bfb = 512, arity 4, INT-2.
* **U6** — carried as unattacked; RT049-CTRL-2 is not run here.

---

## 6. Verdict on this duty

* C1, C2, C3 each actually constructed: **yes**.
* Each leaves both marginals bit-identical: **yes**, at source and in 440
  measured arms.
* Each measurably moves the K = 16 **and** K = 64 joint tables: **yes** — no
  construction is exactly invariant at either resolution, and none is invariant
  at one and not the other. **DESIGN-TRAP-1 as stated has not recurred.**
* Certified list overstates nothing: **correct as at this freeze**.
* Nothing under U1–U6 silently claimed; U1 restated in full: **correct**.

**But the duty is a gap check, and there are three gaps:** C2 and C3 are
distribution-preserving relabelings against a source measured at the independence
coupling (§3.2); two of the four statistics cannot move at all (§3.3); and the
rho = 1.00 rung is bit-identically the anchor
(`attainability_check.md` §3.1). Each is a REVISE on its own terms. **A GAP IS A
REVISE.**

---

## 7. Forward guidance — what remains open

This is not a closure and the lane is not dead.

* **C1 is sound.** It genuinely creates dependence, its ladder is guarded by
  D-1's Spearman leg, and it has both calibration endpoints. The rho ladder is
  worth running once D-5 is repaired.
* **The cheapest experiment that would settle C2 and C3 in one step**, and the
  control this calibration owes them: run OBJ-PLANT-DEP-CELL-eps at eps = 0.25
  and OBJ-PLANT-DEP-BLOCK-q at q = 1.00, 200 replicates per cell, against the
  archived thresholds, **before any ladder**. Two rungs, roughly one-twentieth of
  the measurement arm's budget. If the detection rate is nominal at the top rung,
  the ladder below it cannot inform anything and should not be run.
* **A dependence-creating replacement for C2 exists** and is worth designing: a
  cell-transfer plant whose transposition targets are chosen using **e₂ bins as
  well as e₁ bins**, so that σ depends on e₂ and the exchangeability argument in
  §3.2 no longer applies. That would give a genuine local-mass-transfer class in
  units still comparable with delta, which is what C2 was for.
* **C3 needs a D-1 leg** before it can be certified at all: a monotonicity
  requirement on some induced quantity across DEP-LADDER-BLOCK, and a calibration
  endpoint of its own.
