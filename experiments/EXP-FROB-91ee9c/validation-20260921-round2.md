# Validator report — independent audit of DEC-20260921-d5e997 / EV-FROB-576872 (J3/J4)

TASK-20260921-aac8e7, joint J-VALIDATOR. Independent session; no red-team
report was read before or during the writing of this report (blindness
respected).

## 1. Independent re-read of RUN-FROB-91ee9c-51bc02/metrics.json (`measured`)

Read `metrics.json`'s `measured` object directly (not `report.md`, not
`cost-model.json`) for every `status: "ok"` partition, every arm, both
cells. Full raw rows transcribed below exactly as stored.

**FROB-SPLIT-q11n5 (N=10061)**

| arm | seed | partition | block_sizes | prod_tuple_count | distinct_targets | U_neg | p_m denom |
|---|---|---|---|---|---|---|---|
| object | — | m=1 [4] | [820] | 820 | 820 | 410 | 10060 |
| object | — | m=2 [2,2] | [10,10] | 100 | 100 | 20 | 10060 |
| C2 | — | m=1 | [968] | 968 | 968 | 484 | 10060 |
| C2 | — | m=2 [2,2] | [6,6] | **36** | **18** | 6 | 10060 |
| C3 | 2026091401 | m=1 | [820] | 820 | 820 | 410 | 10060 |
| C3 | 2026091401 | m=2 [2,2] | [10,10] | 100 | 100 | 20 | 10060 |
| C3 | 2026091402 | (identical to seed …01) | | | | | |
| C4 (N'=10079) | 2026091401 | m=1 | [820] | 820 | 820 | 410 | 10078 |
| C4 | 2026091401 | m=2 [2,2] | [10,10] | 100 | 100 | 20 | 10078 |
| C4 | 2026091402 | (identical to seed …01) | | | | | |

**FROB-EQDEG-q19n5 (N=117991)**

| arm | seed | partition | block_sizes | prod_tuple_count | distinct_targets | U_neg | p_m denom |
|---|---|---|---|---|---|---|---|
| object | — | m=1 [4] | [6150] | 6150 | 6150 | 3075 | 117990 |
| object | — | m=2 [2,2] | [10,30] | 300 | 300 | 20 | 117990 |
| C2 | — | m=1 | [6156] | 6156 | 6156 | 3078 | 117990 |
| C2 | — | m=2 [2,2] | [24,24] | **576** | **288** | 12 | 117990 |
| C3 | both seeds | m=1 | [6150] | 6150 | 6150 | 3075 | 117990 |
| C3 | both seeds | m=2 [2,2] | [10,30] | 300 | 300 | 20 | 117990 |
| C4 (N'=123833) | both seeds | m=1 | [6150] | 6150 | 6150 | 3075 | 123832 |
| C4 | both seeds | m=2 [2,2] | [10,30] | 300 | 300 | 20 | 123832 |

**Answers to the questions posed:**

- Does C2's `[2,2]` partition show `distinct_targets < prod_tuple_count`
  (a collision) on both cells? **Yes.** SPLIT: 18 < 36. EQDEG: 288 < 576.
  Both are exact 2-to-1 collisions (every reported target hit by exactly
  two of the tuples: 36/18 = 2, 576/288 = 2 — not sporadic, a perfectly
  uniform halving in both cells; see the anomaly note in §7 below).
- Does the object/C3/C4 `[2,2]` partition show
  `distinct_targets == prod_tuple_count` (zero collisions) on both cells?
  **Yes, in every one of the ten rows above** (object ×1, C3 ×2 seeds, C4
  ×2 seeds, per cell): 100=100 (SPLIT), 300=300 (EQDEG).

**Compared against DEC-20260921-d5e997 / EV-FROB-576872's stated numbers:**
"FROB-SPLIT-q11n5: C2 block product 36→18 targets; object/C3/C4 block
product 100, zero collisions" and "FROB-EQDEG-q19n5: C2 block product
576→288 targets; object/C3/C4 block product 300, zero collisions" —
**both statements match the raw `metrics.json` data exactly, digit for
digit.** No discrepancy found.

I then recomputed every `cost_ratio_neg` and `spread` from these raw
`(U_neg, p_m)` pairs by hand-equivalent exact-rational arithmetic
(Python `fractions.Fraction`, used only as a calculator on numbers already
read directly off the raw JSON — not as a substitute for reading the raw
data, and not trusting any pre-computed `derived_from_measured` value):

| cell | arm | spread (recomputed) | DEC/EV stated | match |
|---|---|---|---|---|
| SPLIT | object | 2055/451 | 2055/451 | exact |
| SPLIT | C2 | 4365/1936 | 4365/1936 | exact |
| SPLIT | C3 (both seeds) | 2055/451 | 2055/451 | exact |
| SPLIT | C4 (both seeds) | 2055/451 | 2055/451 | exact |
| EQDEG | object | 6152/861 | 6152/861 | exact |
| EQDEG | C2 | 24632/2223 | 24632/2223 | exact |
| EQDEG | C3 (both seeds) | 6152/861 | 6152/861 | exact |
| EQDEG | C4 (both seeds) | 6152/861 | 6152/861 | exact |

Zero discrepancies across all 8 spread values (16 underlying m=1/m=2
ratios). J1/J2/J4's mechanical claims in EV-FROB-576872 are independently
confirmed.

## 2. The "m=1-forced-tie" claim, worked from specification.yaml's own definitions

**Definitions used (verbatim from `specification.yaml` `metrics.primary`,
not from `analysis.md`'s prose):**
`p_m(P) = |{R in <G>\{O} : R = Q_1 + ... + Q_m, Q_j in B_j}| / (N-1)`,
obtained by exhaustive enumeration; `U_neg = |B|/2`;
`cost_ratio_neg = (U_neg + 1 + extra)/p_m`.

**Proof, at m=1, in my own words:**

At m=1 there is exactly one slot, V_1, and exactly one block, B_1 = {Q in
<G>\{O} : x(Q) in V_1}. The set of "R expressible as Q_1 + ... + Q_m with
Q_j in B_j" at m=1 is literally `{Q_1 : Q_1 in B_1}` — a sum of *one* term
is that term itself. The map from "1-tuples" to "targets" is therefore the
**identity map on the set B_1**, not a genuine combining/summing
operation. An identity map is injective by definition: two different
inputs Q_1 ≠ Q_1' cannot map to the same output, because the output *is*
the input. There is no possible "collision" at m=1 — not "unlikely," not
"rare," but **structurally excluded by the arity of the sum**, because a
collision requires at least two *distinct combinations* of inputs
(generally: distinct tuples) landing on the same sum, and at m=1 the
"tuple" and the "target" are the same object.

Consequently: `prod_tuple_count(m=1) = |B_1|` (trivially, by definition of
the product over one factor), and `distinct_targets(m=1) = |{Q_1 : Q_1 in
B_1}| = |B_1|` (since B_1 is a *set*, no internal duplication, and the
identity map cannot merge two of its elements). So
`prod_tuple_count(m=1) == distinct_targets(m=1)` **always**, and
`p_1 = |B_1|/(N-1)` is an **exact identity in the single integer |B_1|,
with no enumeration/collision-counting content whatsoever** — this holds
for **any** subset B_1 of `<G>\{O}` of a given cardinality, regardless of
which specific points it contains, whether it is Frobenius-stable, random,
or drawn from an entirely different curve. Nothing about the elliptic
curve, the Frobenius action, or the number field enters this argument: it
is a fact about functions and sets (`|image of the identity map| = |domain|`,
full stop).

**Checked against the raw data — every single m=1 row, both cells, every
arm** (10 rows total, both cells combined): `prod_tuple_count == distinct_targets`
holds in **all 10** (820=820 object/C3-both-seeds/C4-both-seeds SPLIT;
968=968 C2 SPLIT; 6150=6150 object/C3-both-seeds/C4-both-seeds EQDEG;
6156=6156 C2 EQDEG). This is not a special property of the
cardinality-matched arms — it holds for **C2 too**, which is *not*
Frobenius-stable, exactly as the proof predicts (the identity has nothing
to do with Frobenius stability). The proof is confirmed with no gap, no
edge case, and no gap in generality.

**Consequence for C3/C4's coarse endpoint.** Since C3 constructs each slot
at cardinality *exactly* `|B_j|` (specification.yaml's own text) and there
is only one slot at m=1, C3's m=1 ratio is `(|B_1|/2 + 1)/(|B_1|/(N-1))` —
identical, term for term, to the object's, for *any* set of that
cardinality. This holds *before* any run, for any seed, on any cell: it is
not something the run "happened to observe," it is something the run
**could not have shown otherwise**, and I confirm this reading of the
decision's own "m=1-forced-tie" claim is exactly right, with no
overstatement and no gap.

## 3. Extending the argument to the *whole* spread statistic — the corrected, stronger fact (and a correction to my own first attempt)

The handoff's `proves_too_much` note asks explicitly whether the algebra
supports something *stronger* than "the m=1 endpoint is forced" — namely
whether no cardinality-matched control could *ever* show a smaller spread
on a two-partition cell. I worked this through, made an arithmetic-direction
error on my first pass, caught it by testing a concrete counterfactual
number, and report the corrected result here rather than the wrong one,
because getting the direction backwards here is exactly the kind of error
this audit exists to catch.

**The exact, verified relationship.** Write R1 = ratio at m=1 (identical
for C3, and equal to the object's ratio times a fixed positive scalar
`k=(N'-1)/(N-1)` for C4, both established in §2), and R2 = ratio at the
one achievable m=2 partition. Since `cost_ratio_neg = (U_neg+1)(N-1)/distinct_targets`,
R2 is a **decreasing** function of `distinct_targets`: *more* collisions
(lower `distinct_targets`) make R2 **larger** (worse). Because C3 (and C4,
whose slots are built "by the C3 construction inside E'" per
specification.yaml) match every slot's cardinality to the object's, their
`prod_tuple_count` at the fine partition is **identical** to the object's
in every cell (36→36 is not the comparison here — C3/C4 match the
*object's* [10,10]/[10,30] configuration, not C2's [6,6]/[24,24]).
Since the object's own `distinct_targets` at the fine partition **already
equals its `prod_tuple_count` exactly** (zero collisions — confirmed
directly in §1, both cells), the object has already attained the
*maximum possible* `distinct_targets` obtainable by any construction
sharing that `prod_tuple_count`. A cardinality-matched control can
therefore never exceed it: `distinct_targets_ctrl <= distinct_targets_obj`
always, hence `R2_ctrl >= R2_obj` always (control's fine-partition ratio
can only tie or be worse, never better).

Combined with R1 fixed (or fixed-scaled for C4), and given R1 > R2 holds
comfortably for the object in both cells (so `spread = R1/R2`, confirmed
by the flip-point computation below), this yields an **exact, one-directional
bound**:

> **spread(C3) <= spread(object), and spread(C4) <= spread(object),
> in every cell where the object's own finest achievable partition is
> collision-free** — with equality **iff** the control's draw is *also*
> exactly collision-free, and *strict* inequality (i.e., clause (6)
> **satisfied**) the moment the control shows even a single collision the
> object does not have.

This is genuinely **stronger** than "the m=1 endpoint alone is forced": it
extends the certainty to the *entire* two-point spread statistic, in one
direction — a cardinality-matched control on these cells could **never**
have shown a *larger* spread than the object (matching what was observed:
no C3/C4 row anywhere shows a spread exceeding the object's). This is an
exact fact, not a probabilistic one, given only the already-independently-confirmed
input that the object's own fine partition has zero collisions.

**But — and this is the correction — it does NOT mean clause (6) was
unsatisfiable for C3/C4, and I want to flag this explicitly because a
superficial reading of the "m=1-forced-tie" argument invites exactly the
wrong stronger conclusion.** The bound above cuts only one way: it forbids
`spread(control) > spread(object)`; it does *not* forbid
`spread(control) < spread(object)`. Quite the opposite: **clause (6)
would have been satisfied automatically by C3/C4 the instant either
control's random draw showed even one collision that the object does not
have** (a strictly *smaller* spread was the "easy" outcome here, not an
impossible one). I checked this on a concrete counterfactual: if
FROB-SPLIT-q11n5's C3 draw had instead produced `distinct_targets=90`
(10 collisions instead of 0) at its `[2,2]` partition, its ratio there
would rise to 110660/90 ≈ 1229.6 (vs. the object's 1106.6), giving
`spread(C3) ≈ 5042.27/1229.6 ≈ 4.10 < 4.557 = spread(object)` — clause
(6) **passes** in that counterfactual. So the observed exact ties are not
a structural inevitability of the metric; they are the *specific,
empirical* outcome that **all four independent draws in each cell (C3 ×2
seeds, C4 ×2 seeds; eight draws total across both cells) happened to also
land on zero collisions**, matching the object's own zero exactly.

**Why that coincidence is unsurprising (a new, quantitative observation
not in the existing records).** Under a naive uniform-random-mapping
("birthday") heuristic, the expected number of collisions for
`prod_tuple_count` tuples landing in a target space of size `N-1` is
roughly `prod_tuple_count^2 / (2(N-1))`. For the tested fine partitions:
SPLIT ≈ 100²/(2·10060) ≈ 0.50; EQDEG ≈ 300²/(2·117990) ≈ 0.38. Both are
comfortably below 1, meaning a *zero-collision* outcome is the
statistically unsurprising, plausible-by-chance result for *essentially
any* reasonably-sized random negation-closed subset at these specific
cardinality-to-(N-1) ratios — independent of Frobenius structure. This
gives a precise, quantitative reason (rather than the qualitative "reduces
to a single collide/don't-collide comparison" already in the record) for
why the observed ties carry little information: at these specific
parameter choices, the fine-partition comparison had a fairly high prior
probability of tying *before any draw was made*, for reasons unrelated to
Frobenius-stability.

**A related, quantitative flag on C2 (offered as a mechanical observation,
not an interpretive verdict — that is red-team's joint).** C2's own
collision counts are the opposite kind of surprise: SPLIT's C2 shows an
*exact* 2-to-1 collision (36→18, a uniform halving, not a sporadic one) against
a birthday-estimate of ≈0.06 expected collisions — roughly 280× the naive
estimate. EQDEG's C2 shows the same exact 2-to-1 pattern (576→288) against
a birthday estimate of ≈1.4 — roughly 200× the naive estimate. Both cells'
C2 collision rate is *exactly* 50%, not merely "elevated" — a suspiciously
clean ratio that looks more like a systematic pairing internal to the
specific "lexicographically first non-pi-stable subspace" construction
than like ordinary birthday noise. I surface this because it is directly
readable off the raw numbers already reported (no new computation needed,
just the ratio), and because it is relevant context for interpreting
PTM-2, but forming a verdict on what it implies about clause (6)/(c) or
about C2's construction is outside the scope of this joint.

**Flip-point sanity check (bounding my own "always" claim honestly).** The
one-directional bound above (`spread(control) <= spread(object)`) assumes
R1 remains the *larger* of the two ratios for the control too. I checked
where that assumption would break: for SPLIT, R2_ctrl would have to rise
to exceed R1 only if `distinct_targets` fell below ≈22 (a ≈78% collision
rate) out of 100; for EQDEG, below ≈42 (a ≈86% collision rate) out of 300.
Both are far outside anything observed (0% in every row) or plausible
under the birthday estimates above, but I record the boundary explicitly
rather than asserting an unconditional bound with no stated domain.

**A precise wording point for the record (not a verdict-changing defect).**
EV-FROB-576872 and DEC-20260921-d5e997 both state that C3/C4's capacity to
show a strictly smaller spread "reduces entirely to whether the ONE finest
(argmin) partition shows more collisions **on the object than on the
control**." My derivation shows the condition that would actually flip a
tie into a clause-(6) *pass* is the **control** showing more collisions
than the **object** (not the reverse — the object, having zero, cannot by
definition show "more" collisions than anything). I read this as an
imprecision in the prose's direction, not a computational error (every
number the prose reports is exact and correct, as confirmed in §1), and I
flag it so that a future reader citing this passage — e.g. for the NA-2
resource_check follow-up — does not inherit an inverted condition. It does
not change J3's resolution: the actually-measured outcome is an exact tie
in every row, which fails clause (6) regardless of which direction the
"what would have made it pass" condition points.

## 4. Artifact hash-bindings (manifest.yaml vs. disk)

Recomputed sha256 and byte count for **all 21** artifacts declared in
`RUN-FROB-91ee9c-51bc02/manifest.yaml`'s `run.artifacts` block (every file,
not a sample): `aggregate.py`, `certificates.json`, `checker.py`,
`command.txt`, `cost-model.json`, `environment.json`, `fixtures.json`,
`implementation.py`, `metrics.json`, `raw-result.json`, `report.md`,
`stderr.log`, `stdout.log`, `work/FROB-EQDEG-q19n5.err.log`,
`work/FROB-EQDEG-q19n5.out.json`, `work/FROB-SPLIT-q11n5.err.log`,
`work/FROB-SPLIT-q11n5.out.json`, `work/checker-report.json`,
`work/checker-run1.log`, `work/core.py`, `work/lattice.py`.

**Result: 0 mismatches.** Every declared `bytes` and `sha256` value matches
the file currently on disk exactly. Also recomputed
`specification_sha256` (`9d66c4f7914250a09a5083a3e97c85af9f26ba04755b906105c200d41c75daa4`)
against `experiments/EXP-FROB-91ee9c/specification.yaml` on disk: exact
match. Also checked `code.commit` (`e2703b0d465906f86e477503f7628723da91450c`):
this is a real commit object in the repository and is an ancestor of the
branch's current HEAD (`git merge-base --is-ancestor` confirms reachability),
consistent with the manifest's `dirty_at_execution_start: false` claim.

## 5. checker.py independence

```
$ grep -n '^import\|^from' checker.py
39:import sys, os, json, itertools
40:from fractions import Fraction
```

Grepping for `import` anywhere in the file (not just at line start) finds
only these two lines plus a docstring sentence *describing* the exclusion
("Deliberately does NOT import implementation.py, work/core.py,
work/lattice.py..."). **Confirmed: no import of `implementation.py`,
`core.py`, or `lattice.py` from either run directory, and no SageMath
import.** I also read the checker's own header comment and enough of its
body to confirm this is not merely an absence of imports but a genuine
from-scratch reimplementation: it reconstructs the field modulus, does its
own point-order counting (full brute force for the small SPLIT field,
disclosed as skipped for the larger EQDEG field), and reverifies every
`cost_ratio_neg`/spread from the **raw `work/<cell>.out.json`** driver
output (a more primitive artifact than `metrics.json`/`cost-model.json`,
which are produced by `aggregate.py` downstream of it) — so its agreement
with the aggregated files is not circular.

## 6. Cross-check against work/checker-report.json

`work/checker-report.json`'s own independently-recomputed
`independent_spreads` block: SPLIT `{object: 2055/451, C2: 4365/1936, C3:
2055/451 both seeds, C4: 2055/451 both seeds}`; EQDEG `{object: 6152/861,
C2: 24632/2223, C3: 6152/861 both seeds, C4: 6152/861 both seeds}`. These
match my own independent hand-equivalent recomputation in §1 **exactly**,
digit for digit, and match DEC-20260921-d5e997/EV-FROB-576872's stated
values exactly. `cost_ratio_all_match: true` and
`C3_C4_U_neg_matched_cardinality_ok: true` on both cells, `0`
`cost_ratio_mismatches` out of 12 reverifications per cell. No
discrepancy found anywhere across the four independent sources I compared
(raw `metrics.json`, my own recomputation, `work/checker-report.json`,
DEC/EV's stated numbers).

## 7. Other checks performed

- Confirmed `experiments/EXP-FROB-91ee9c/amendments/DEC-20260921-e81e25.yaml`
  leaves controls C1–C8 "exactly as specified... no redefinition of any
  control's design, isolation claim or claim_limit" — so the C3/C4 designs
  my proof in §2/§3 relies on are the frozen, unamended designs.
- Re-derived `I(FROB-SPLIT-q11n5)=2055/451` and `I(FROB-EQDEG-q19n5)=6152/861`
  independently from the raw pairs (they equal the object-arm spreads
  above, since only two partitions are `ok` in each cell) — both reproduce
  round 1's already-established values exactly, on this separate run's raw
  data.

## review_attestation

```yaml
review_attestation:
  joints_owned: [J-VALIDATOR]
  sources_read:
    - AGENTS.md
    - agents/validator.md
    - ledger/handoffs/TASK-20260921-aac8e7.yaml
    - ledger/hypotheses/H-FROB-d93575.yaml
    - experiments/EXP-FROB-91ee9c/specification.yaml
    - experiments/EXP-FROB-91ee9c/amendments/DEC-20260921-e81e25.yaml
    - experiments/EXP-FROB-91ee9c/analysis.md (Round 1 and Round 2 sections)
    - ledger/evidence/EV-FROB-576872.yaml
    - ledger/decisions/DEC-20260921-d5e997.yaml
    - experiments/EXP-FROB-91ee9c/runs/TASK-20260921-51bc02/manifest.yaml
    - experiments/EXP-FROB-91ee9c/runs/TASK-20260921-51bc02/metrics.json (measured object, read directly)
    - experiments/EXP-FROB-91ee9c/runs/TASK-20260921-51bc02/checker.py
    - experiments/EXP-FROB-91ee9c/runs/TASK-20260921-51bc02/work/checker-report.json
    - every artifact byte-for-byte in experiments/EXP-FROB-91ee9c/runs/TASK-20260921-51bc02/ (hash recomputation, 21 files)
  read_sibling_reports: false
  blindness_respected: true
  verdict: holds
```

## Overall verdict

**CONFIRMS WITH QUALIFICATION.** Every mechanical/numeric claim under this
joint — every collision count, every `cost_ratio_neg` and `spread` value,
every artifact hash, `checker.py`'s independence, and the core
"m=1-forced-tie" claim as literally phrased — is **independently confirmed
exactly**, with zero discrepancies found across five independent
cross-checks (raw `metrics.json`, my own hand-equivalent recomputation,
`work/checker-report.json`, `report.md`'s stated values, and
DEC-20260921-d5e997/EV-FROB-576872's stated values). No defect changes the
decision (`weaken`) or the strength (`preliminary`); both remain fully
supported, independent of everything below.

What changes, precisely, per the handoff's `proves_too_much` instruction:

1. **The m=1-forced-tie claim generalizes further than stated, in one
   exact direction:** given the (independently confirmed) fact that the
   object's own finest achievable partition is collision-free in *both*
   tested cells, `spread(C3) <= spread(object)` and `spread(C4) <=
   spread(object)` **exactly and unconditionally** on these cells — a
   cardinality-matched control could never have shown a *larger* spread
   than the object here (matching what was observed). This is a genuine,
   verified strengthening of the record's own structural argument, and it
   is what makes C2 — not being cardinality-matched — the *only* arm free
   to exceed the object's spread, exactly as observed on FROB-EQDEG-q19n5.
2. **The record should NOT be read (and I initially, wrongly, almost read
   it) as implying C3/C4 could never have shown a strictly *smaller*
   spread.** The opposite is true: any single collision in a C3/C4 draw
   that the object does not have would have satisfied clause (6)
   immediately. The observed exact ties are a genuine but, given the
   birthday-style estimate of ≈0.4–0.5 expected collisions at these
   specific cardinality-to-N ratios, statistically unsurprising
   coincidence across all eight independent draws — not a structural
   forcing of the *whole* statistic, only of its m=1 endpoint. This
   sharpens, and partially corrects the framing of, EV-FROB-576872's
   `resource_check.reading` and DEC-20260921-d5e997's own rationale
   bullet about "bounding how much information any tie here can carry":
   the correct bound is one-directional and the residual randomness is
   low-power (not zero-power, and not symmetric) at these specific
   cardinalities.
3. **A directional wording point** in both EV-FROB-576872 and
   DEC-20260921-d5e997 ("more collisions on the object than on the
   control") states the passing condition backwards relative to the
   algebra (it should read "more collisions on the control than on the
   object"); worth correcting the next time this text is revisited (e.g.
   for NA-2), but immaterial to J3's resolution since the actual measured
   outcome is an exact tie either way.
4. A mechanical observation for context, not a verdict: C2's collision
   pattern is an *exact* 2-to-1 halving in both cells (≈200–280× a naive
   birthday estimate), suggesting a systematic construction effect rather
   than ordinary sampling noise — offered to whichever review next
   revisits PTM-2 or C2's subspace-selection rule, not asserted as part of
   this joint's verdict.

None of the above reopens J1, J2, or J4's mechanical findings (all
independently reconfirmed exact in §1–§6), and none of it licenses any
attack, speedup, or claim beyond `EXP-FROB-91ee9c`'s own zero-claims
ceiling.
