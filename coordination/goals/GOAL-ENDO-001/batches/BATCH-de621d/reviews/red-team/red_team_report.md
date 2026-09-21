# Red-team review of DEC-20260810-2c7e3c (L9 lane closure, RQ-CANL-63098f)

`RT-20260810-3f7ca3` · `TASK-20260810-ea4965` · GOAL-ENDO-001 · BATCH-de621d
Snapshot read: **a651a83f6** (`GOAL-ENDO-001 BATCH-de621d: snapshot DEC-20260810-2c7e3c
(L9 lane closure, pre-review)`). Every artifact below was read at that commit via
`git show a651a83f6:<path>`, not from the working tree.

## VERDICT

**closure CONFIRMED WITH SCOPE CORRECTION.**

Lane L9 is genuinely closed within its declared boundary, and the record is well above
the fatigue-report standard `docs/inventor-protocol.md` forbids. But **it is not closed
by the argument it names as load-bearing.** The norm-form gap (Lemma 1 + Lemma 2) is
valid only for a *cyclic/free* O-module and only for `|D_E| > 4 C_0^2`. Both carve-outs
contain objects of cryptographic interest: the second contains secp256k1 (the record
says so); the first contains roughly **half of all ideal classes at every discriminant**
(the record does not say so, and nor does any draft). What actually holds the lane closed
is (i) the target-independence counting gate of EXP-CANL-1064e0 and (ii) the constancy of
`C_0` and `r` at fixed arity. Both survive every objection below, which is why the verdict
is a correction and not a refutation.

Nothing here asserts anything about ECDLP hardness in either direction. `claim_tier: toy`,
`sota_delta: 0`, zero runs executed under any EXP-CANL-* contract.

---

## Material findings by attack surface

### A1 — WHICH ORDER IS `D_E`? · the named failure mode is NOT committed; two derived gaps are

**The conflation the task card warned about does not occur.** I checked every use of a
discriminant in the decision and in the four drafts it leans on:

- Lemma 1 is applied throughout to `D_E = disc End(Ẽ) = disc End(E)` (Serre–Tate:
  `End(Ẽ) = End(E)`), never to `disc Z[pi]` as a substitute.
- The one place `4p - t^2` appears (Answer 1; EXP-CANL-86c465 mechanism STEP 2) is
  explicitly conditioned on **"a curve at the bottom of its volcano"** — precisely the
  locus where `End(E) = Z[pi]`, so the substitution is *entitled* there.
- secp256k1 is handled separately and correctly at `|D_E| = 3` (`j = 0` forces
  `End(E) = O_{-3}`, since `j = 0` is the root of `H_{-3}`), which is exactly the case the
  card said a conflated argument would get wrong. The GLV endomorphism of norm 1 is not
  denied anywhere.

**A1-a (material, unnamed).** The attacker's freedom to move on the volcano is never
composed with Lemma 1's hypothesis. `|D_E| = f_E^2 |D_0|` with `f_E | f`; ascending
divides `|D_E|` by up to `f^2`, i.e. by up to ~`4p/|D_0|`. The saving fact — `D_0` is an
invariant of `(p, t)`, so `|D_E| >= |D_0|` and the small-`|D_E|` regime **cannot be
manufactured**, only inherited — exists in the record but only inside the *reachability*
item (a), phrased about class numbers `h(disc End)`, and is never composed with Answer 1.
One sentence closes it. Until it is written, "whenever `|D_E| > 4 C_0^2`" is a hypothesis
about a quantity the attacker partially controls, stated as if it were fixed.

**A1-b (material, dropped from the cited source).** EXP-CANL-86c465's own `tail_checks`
says: *"Non-maximal orders. For f_E > 1, Ẽ(H) need not be a projective O-module and
r_Z = 2 r_O can fail. Every measurement is stratified by f_E and the f_E > 1 cells are
reported separately, never pooled."* The decision imports `m >= r_Z/2 + 1` (Answer 1) and
"the 2 r_O-dimensional lattice" (Answer 3) **unconditionally**, and drops the stratification.
Note the decision's own headline instantiation — the volcano floor — is the case
`f_E = f`, i.e. inside the flagged cells whenever the volcano has any height. The error
direction is defender-favourable (less module structure = less attacker gain), so the
verdict is untouched; what is over-stated are the two *positive* deliverables the decision
credits to CM ("points-to-lift halved", "effective rank `r_O`").

### A2 — THE EXCLUDED REGIME · excluded from *Lemma 1* by argument, included in the *rejection*, and populated

The small-`|D_E|` regime is **not** excluded from the closure's scope — the scope statement
rejects the L9 decision target over "ordinary curves E/F_p" with no discriminant condition,
so `j = 0` and `j = 1728` are inside the rejection. That is the right call; excluding them
would be the premature closure the protocol forbids, and the record says so explicitly.

It is handled **by argument, not assertion**. I re-derived EXP-CANL-3c4af4's arithmetic
independently and it holds: `O` has covolume `sqrt(|D_E|)/2` in `C`, so
`#{alpha : N(alpha) <= C_0^2} ≈ pi C_0^2 / (sqrt(|D_E|)/2) = 2 pi C_0^2 / sqrt(|D_E|)`;
`2 pi / sqrt(3) = 3.628` at `|D_E| = 3` and `pi = 3.142` at `|D_E| = 4`, both as printed;
and the net factor `(3.6/4)^{r_Z/2} * 3.6 * C_0/2` recomputes exactly. The conclusion
"constant at fixed arity, so `I = N^{1-o(1)}`" is valid.

**But a curve of the highest cryptographic interest sits in the regime where the
load-bearing lemma is silent**, and over that regime the closure rests on constant-factor
accounting conditioned on `C_0` absolute and `2 <= r <= 9` — i.e. on G6 — not on the
norm-form gap. Answer 1's own text is correctly conditioned (`whenever |D_E| > 4 C_0^2`);
the closure narrative, the `refutation_artifact` framing and the snapshot commit message
are not. **This is the first half of the required scope correction.**

**Emphasis inversion (presentation defect that will mislead citers).** Answer 2 spends most
of its length on the unit tautology (`P + zeta_3 P + zeta_3^2 P = O` reducing to `0 = 0`)
plus the KN-FIND-003/008 consilience. That argument is correct — norm-1 elements of an
imaginary quadratic order are exactly the units — but by the source's own accounting it
removes `|O^*| <= 6` elements from a set of size `~3.63 C_0^2`, i.e. **nothing
asymptotically**. EXP-CANL-3c4af4 (D) says so plainly ("the `Theta(C_0)` enlargement
survives after deleting the O(1) units … it is a genuine improvement and it must be stated
as one"). The load in Answer 2 is carried entirely by the constancy of `C_0` and `r`. A
reader will mis-locate it.

### A3 — DOES THE COMPOSITION HOLD? · yes for free modules; NOT in general — the main finding

**What checks out.**
- Lemma 1's inequality is correct by inspection: `O = Z[w]`, `w = (D_E + sqrt(D_E))/2`,
  `alpha = a + b w` gives `N(alpha) = (a + b D_E/2)^2 + (b^2/4)|D_E| >= |D_E|/4` for
  `b != 0`. No hypothesis needed. ✔
- `hhat(alpha P) = deg(alpha) hhat(P) = N(alpha) hhat(P)` is the standard Néron–Tate
  statement for an endomorphism (canonical height for the symmetric divisor class; `deg`
  = norm form on a CM order). Correctly labelled "standard, cited, not re-derived". Its own
  machine check (EXP-CANL-86c465 STAGE 1) has never been run. ✔ (as a citation)
- **The multi-generator extension, which the record asserts without proof, is true in the
  free case.** For `v = sum_i (a_i + b_i w) P_i = x + w y` with `x, y in Z^{r_O}` and Gram
  matrix `G`: `hhat(v) = |x + (D/2) y|_G^2 + (|D|/4) |y|_G^2`, so `y != 0` forces
  `hhat(v) >= (|D_E|/4) lambda_1(M)^2`. I checked this because cancellation between distinct
  generators is the usual way short vectors appear; here the square completes cleanly and
  the record is right. ✔

**A3-a (defect, harmless direction).** The decision restates Lemma 1's equality clause as
"equality iff `|b| = 1` and `a = -b D_E/2`. **No hypothesis is used.**" — dropping the
source's parenthetical *"(possible only for D_E even)"*. As restated in the decision the
clause is **false** for `D_E ≡ 1 (mod 4)`: at `D_E = -3`, `b = 1`, the minimum off-`Z` norm
is `1 = (|D|+1)/4`, not `|D|/4 = 3/4`. The inequality actually used is unaffected. Worth
recording because EXP-CANL-86c465 STAGE 0 — the falsifier the decision names for its own
lemma and does not run — is exactly the check that would flag it.

**A3-b (MATERIAL — the norm-form gap is a property of the principal class, not of the order).**
The decision states the composition for the *cyclic* module (`"the O-module generated by a
lifted point P~ … spanned by P~ and omega P~"` — cyclic, hence free, hence fine) and then
generalises without qualification:

> THE O-MODULE STRUCTURE INFLATES THE Z-RANK WITHOUT PLACING A SINGLE NEW VECTOR INSIDE ANY
> BALL OF RADIUS o(sqrt(p)) TIMES THE LATTICE MINIMUM

and uses the general form in Answer 3 ("the second half of the `2 r_O`-dimensional lattice
is longer by `sqrt(|D_E|)/2`"). A projective rank-1 O-module is an **ideal class** `a`, and
when `h(O) > 1` the generic Steinitz class is non-principal — in the floor regime
`h(O) ≈ sqrt(p)`. For `aP` with `hhat(alpha P) = N(alpha) hhat(P)`, writing the class's
reduced form `(a_Q, b, c)`, `4 a_Q c - b^2 = |D|`: the minimum is `a_Q`, attained at the
*rational* element, and the second successive minimum is `c`, attained at an *irrational*
element — so the ratio is `c / a_Q`, **not** `|D|/4`. For a balanced class
(`a_Q ≈ c ≈ sqrt(|D|)/2`, permitted since `a_Q <= sqrt(|D|/3)`) the ratio is `O(1)` and the
gap is gone at arbitrarily large `|D_E|`.

Reviewer-side arithmetic (my own check of my own objection; **not a run, not evidence, no
artifact claimed**), enumerating *all* reduced forms of each discriminant:

| `D` | `h` | Lemma-1 gap `|D|/4` | `min(c/a)` | `median(c/a)` | classes with `c/a <= 4` |
|---|---|---|---|---|---|
| −2003 | 9 | 501 | 1.42 | 6.33 | 4/9 = 44% |
| −10007 | 77 | 2502 | 1.04 | 4.42 | 38/77 = 49% |
| −100003 | 39 | 25001 | 1.15 | 2.50 | 24/39 = 62% |
| −1000003 | 105 | 250001 | 1.03 | 3.79 | 56/105 = 53% |

Counting the coefficient window **relative to the class's own minimum** at `C_0 = 3`:
principal class `(1,1,c)` gives exactly `6 = 2C_0` (Lemma 1 reproduced); the median class
gives **14–16**, i.e. `Theta(C_0^2)`. Lemma 1 bounds `N(alpha)` *absolutely*; the operative
Xedni quantity is smallness *relative to the module's own minimum*, and the two coincide
only for the free/cyclic case.

**Why this does not refute the closure.** The escape it opens is arithmetically the *same*
`Theta(C_0^2)`-per-slot constant as Answer 2's small-`|D_E|` escape (measured 14–16 vs 6 at
`C_0 = 3`). With `C_0` and `r` absolute constants the instance count stays `N^{1-o(1)}` and
the exponent stays 1 against rho's 1/2. The conclusion survives; the *stated argument for
it* does not, universally. **This is the second half of the required scope correction.**

**Consequence for the drafts (cheapest control available, zero compute).**
EXP-CANL-86c465's pre-registered `success_criterion` — *"ratio of minima >= sqrt(|D_E|)/2 …
must track sqrt(|D_E|) with slope 0.5 in log-log across at least 5 values of |D_E|"* — is
false as a universal prediction and holds only for the principal class. As written, an
executor whose lift lands in a balanced non-principal class measures a **flat** ratio and,
per that contract's `falsification_criterion` item 3, must conclude *"either the height
implementation or Lemma 2 is wrong"*. The contract would misdiagnose a **correct**
measurement as instrument failure. This is the inventor-protocol §3 decay test running
backwards: the quantity that "should grow with `|D_E|`" legitimately does not, for half the
inputs, and the contract has no stratifier that can tell that apart from a bug.

**A3-c (field of definition dropped).** EXP-CANL-86c465 (B) is careful — *"Over the ring
class field H of O, the group Ẽ(H) is an O-MODULE"*. The decision never names a field. This
matters twice: (i) over `Q` the CM action is not defined at all (for `j = 0` it needs
`Q(zeta_3)`), so `r_Z` and `r_O` are ranks over `H`, not over `Q`; (ii) "a point of
canonical height `B` has x-coordinate of bit-size `Theta(B)`" is a `Q`-rational statement
and needs `[H:Q] = 2h(O)` bookkeeping over `H` — and `h(O) ≈ sqrt(p)` in the floor regime.
Both cut in the defender's favour, so no verdict change; but Answer 3's numbers
(`r_Z > 4 → r_Z > 8`; "Z-rank >= 6, >= 8 with margin") are **unusable as forward guidance**
until the field over which `r_Z` is measured is stated.

**Is the budget the one JKSST actually quantified? Unresolved, and nobody in this repository
has read the paper.** `knowledge/literature/KN-LIT-021.md` carries `confidence: reported`,
`citation_verified: web`, and its own *"Not verified here: Full paper not read; the
coefficient-bound argument and experimental conclusion relayed from the abstract and
secondary sources."* It describes the mechanism as *"an **absolute** bound on the size of the
coefficients"*, while `DECOMPOSITION.md` L9 and `RQ-CANL-63098f.decision_target` state it as
*"lifted points have height ~N"*. The decision then uses the **absolute** reading in Answer 1
(`N(alpha_i) <= C_0^2`, with the explicit equivalence "the Z-case bound `|a_i| <= C_0` is
exactly `N(a_i) <= C_0^2`") and the **relative** reading in Answer 3 (balls of radius
`sqrt(B)` measured against `hhat_min`), and never reconciles them. The two readings are not
interchangeable once the module is non-free: under the absolute reading the non-free case
makes the coefficient set *empty* (min `N(alpha) = N(a) a_Q ≈ |D|/4 ≈ p` for balanced
classes) and the closure is *stronger*; under the relative reading A3-b applies. The
decision's `limitations` flags the Sutherland and Hindry–Silverman relays but **not the
JKSST relay — the obstruction the entire lane is closed on.**

### A4 — IS `Theta(N)` THE RIGHT CONCLUSION? · yes as an instance count, but two quantities travel under one name, and two of Answer 4's three legs do not hold

**A4-a. The pre-registered quantity and the delivered quantity are different.** The
obstruction as pre-registered is a **height** ("lifted points have height ~N"); the
decision's conclusion is an **instance count** (`I = N/(2C_0+1)^{r+1} = Theta(N)`). The
decision's own Answer 3 derives the height budget as `B = Theta(N^{2/r})`, and
EXP-CANL-8687b3 (B) tabulates it: `N^{0.667}` at `r = 3` down to `N^{0.222}` at `r = 9`.
So the closure's own supporting analysis **contradicts the pre-registered kill criterion by
a factor `r/2` in the exponent** for every `r >= 3`, and the record never says so. Since the
criterion reads *"any lane variant must state how CM changes that specific quantity or it is
closed on arrival"*, the gate's own quantity is misstated — that is a defect in the gate, not
only in this record, and it should be corrected in `DECOMPOSITION.md` L9 / RQ-CANL-63098f by
a superseding record rather than silently inherited by the next lane.

**A4-b. Reproduction vs substitution.** The exponent-1 formula is *inherited* from the
internal reconstruction ECFG-P1543-R1 of an unread paper; the CM work is a *substitution* of
a recomputed coefficient count into it. That is a legitimate comparative computation and it
does not assume its conclusion (the CM count is computed independently in two regimes). But
the decision's *"reproducible by an independent reader from the cited records alone"* is true
relative to the internal reconstruction only.

**A4-c (MATERIAL). The decision's self-declared "sharpest single statement the lane
produced" is quantitatively vacuous, by arithmetic on the record's own formulas.** Answer 4
(iii): Lang's height floor `hhat(P~) >= c log|Delta| ≈ 2c log(mp)` grows **logarithmically**
in the search parameter `m`; the budget it must exceed is `B = Theta(N^{2/r_O})`,
**exponential** in the security parameter. The floor binds only at
`m ≈ exp(N^{2/r_O} / 2c)`. At any feasible search depth it is smaller than the budget by
tens of orders of magnitude. The source proposal states this itself and the decision drops
it: IDEA-20260807-13c821 `survival_score` reads *"DIES: at the point where log|Delta| growth
makes the Lang floor exceed the height budget B ~ N^{2/r_O}, which is computable and is where
the search must stop."* The anti-correlation is real and it is negligible; calling it "an
obstruction to the only free quantifier the lane has" is not supported.

**A4-d (MATERIAL). Answer 4 (ii) is an unmeasured cost model presented as settled.** *"a rank
lower bound needs a point search of cost `B^{r/2}`, which is the same search the attack itself
needs, so screening saves nothing"* — but the attack needs a point of height `Theta(N^{2/r})`
above a **prescribed** residue, whereas a rank lower bound needs *any* `r` independent points,
whose heights are governed by the curve's regulator and which are found by descent, not by
naive search. The source does not claim this is settled: IDEA-20260807-13c821 STEP 4 and STEP
5 **pre-register measuring** the density of high-rank members and testing for a cheap goodness
predictor, and its OUTCOME 2 is written as a supersession condition. The knob is closed here
on an experiment that was scheduled and not run.

**A4-e. What actually holds.** With (iii) vacuous and (ii) unmeasured, the closure's weight
rests where it is soundest and where the decision under-advertises it: the **target-independence
gate** of EXP-CANL-1064e0 — for any construction definable from `(E, O, K)` alone with
`p^{o(1)}` output, `S` is fixed before `Q` is seen, so `Pr[Q in red(S)] <= |S|/N = p^{-1+o(1)}`
for a uniform target. Two lines, correct, independent of every height, rank, coefficient and CM
consideration above, and honestly scoped: route L5 (target-dependent) is excluded and reappears
as G3. Together with the constancy of `(C_0, r)`, that is the closure.

### A5 — IS ANY DRAFT MISREAD? · no attribution is invented; five conditions are dropped; one corroboration claim is inflated

Spot-checked in full: **EXP-CANL-86c465 mechanism STEP 1** (the load-bearing citation) and
**EXP-CANL-3c4af4**; plus EXP-CANL-8687b3 (A)–(E), EXP-CANL-1064e0 (A)–(C), and
IDEA-20260807-13c821 (B), (C2), (C3), (D), `survival_score`. Also verified the decision's
factual claims about lane state at the snapshot: seven contracts, all `status: draft` with
`approved_by: null`, one `specification.yaml` each, no `runs/` directory, **no `RUN-CANL-*`
record anywhere** (the string occurs only in the task card and in the decision itself), and
**12** proposals citing RQ-CANL-63098f. All confirmed.

Every number I could check reproduces: `2 pi C_0^2 / sqrt(|D_E|)` and its values 3.63/3.14;
the net factor `(3.6/4)^{r_Z/2} · 3.6 · C_0/2`; the semicircle fraction — I recomputed
`(1/2πp) ∫_{-√p}^{√p} sqrt(4p - t^2) dt = 8p[π/12 + sin(π/3)/4]/(2πp) = 0.6090`, matching the
printed 0.609…; `V_r B^{r/2} Reg^{-1/2}` and `B >= (N sqrt(Reg)/V_r)^{2/r}`;
`hhat ≈ h_x/2` giving bit-size `Theta(B)`; the `Theta(N^{2/r})` table at `r = 2,3,4,5,8,9`;
`Pr[Q in red(S)] <= |S|/N`; "Z-rank >= 6, >= 8 with margin".

**No draft is misread** in the sense of a claim attributed that the draft does not make. Five
*conditions* are dropped in transcription, all in the direction of strengthening the closure:
(1) "(possible only for `D_E` even)" from Lemma 1's equality clause [A3-a]; (2) the semicircle
qualification behind the word "generic" (the source says 60.9% of curves, not all); (3) the
`survival_score` threshold behind the Lang floor [A4-c]; (4) the ring class field `H` [A3-c];
(5) the `f_E > 1` tail check [A1-b].

**One characterisation I dispute, and it is load-bearing for *timing*.** The decision justifies
closing now rather than pausing a fifth time partly on *"five independent proposals reach the
same exponent-1 verdict from five different directions"*. They are not five independent
directions: three of them (fd5a24 → Answer 1; 6533fd (D) → Answer 3; cfe576 route L2) all run
through the **same** Lemma 1 + Lemma 2 composition, and 6533fd (D) cites fd5a24 by ID for it.
The genuinely independent legs are the target-independence count and fd2d89's `k^2` size bound.
Three restatements of one lemma are not three-fold corroboration — and per A3-b that one lemma
is the step with the scope defect.

### A6 — FORWARD GUIDANCE SUFFICIENCY · present and mostly concrete; three gaps

Obstruction named (two of them), argument given, G1–G6 each citing the record it comes from, a
named successor with a home (G2 → L11 / RQ-MODEL-e61cb2, correctly identified as a
representation question rather than a CM one), a revisit condition, remaining uncertainty
(i)–(iv), budget spent, test boundary, an explicit rejected/not-rejected scope, and — creditably —
a **named falsifier of its own load-bearing lemma** costing minutes. This clears
`docs/inventor-protocol.md` §4 and CLAUDE.md rule 9. Three gaps:

1. **G6 is excluded from the revisit condition.** G6 ("any regime in which `C_0` is not an
   absolute constant") is described as invalidating the coefficient-set step, yet the revisit
   condition reopens only on G1–G4. G5's exclusion is deliberate and stated; G6's is not.
   Since A2 and A3-b both show the closure at small `|D_E|` **and** in non-principal classes
   rests entirely on `C_0` being constant, G6 is the most load-bearing of the six.
2. **A pre-registered supersession condition from a cited source is missing.**
   IDEA-20260807-13c821 OUTCOME 2 — Z-rank ≥ 6 members of `y^2 = x^3 + (b + mp)` found at a
   density making the search cheaper than `N^{1/2}` rank computations — supersedes that record
   by its own terms, and the decision relies on that knob being closed (Answer 4) without
   carrying its supersession condition forward.
3. **A missing G7 implied by A3-b:** *a CM lift whose Mordell–Weil O-module lies in a
   non-principal class with balanced reduced form* is a regime where the norm-form gap fails at
   **any** `|D_E|`. It appears nowhere in the scope statement or the reopening list.

---

## Required scope correction (what a superseding record must say)

Replace the closure's headline with the two-regime, two-argument form it actually has:

> Within `prime fields / ordinary E/F_p / canonical lift and global CM models / 2 <= r <= 9 with
> C_0 an absolute constant / the twelve enumerated mechanism families`, CM does not move the
> Xedni instance-count exponent off 1. The argument is **not** uniform. (i) For a **cyclic or
> free** O-module and `|D_E| > 4 C_0^2`, the norm-form gap gives coefficient-set equality with
> the Z-case. (ii) Otherwise — `|D_E| <= 4 C_0^2` (contains `j = 0`, `j = 1728`, hence
> secp256k1) **or** a non-principal module class with balanced reduced form (roughly half of all
> classes, at any `|D_E|`) — the coefficient set enlarges to `Theta(C_0^2)` per slot and the
> closure rests on `C_0` and `r` being absolute constants (G6), not on the norm-form gap.
> (iii) Independently of both, the target-independence bound `Pr[Q in red(S)] <= |S|/N` closes
> four of the five point-lifting routes; the fifth is G3 and is explicitly not closed.

Also: state the field (`H`) over which every rank is measured; flag the JKSST relay in
`limitations` beside the other two; and record that Answer 4 (iii) is a log-vs-exponential
comparison that does not bind at feasible search depths.

## Baseline comparison

The decision compares against Pollard rho at `0.886 sqrt(N)` (KN-TECH-001/006) and reports
exponent 1 vs 1/2 — the right comparator for a lift attack — and BSGS appears in gate (a) as
the memory comparator (`p^{1/2+o(1)}` space vs the class-polynomial bill). One omission: the
**closest specialised baseline is the automorphism-discounted rho on CM curves (KN-TECH-018)**,
which `RQ-CANL-63098f.constraints` makes a *mandatory* control and which the drafts carry in
their `controls`, but which the decision's own comparison never uses. Answer 2's regime
(`j = 0`) is exactly where the discount applies, and Answer 2's gain is exactly a constant, so
the honest comparison there is constant-vs-constant against the **discounted** baseline. Not
verdict-changing (constants against exponents), but it must be stated before any KN-FIND
promotion. `dominated_by` is not applicable in the usual sense — no candidate algorithm is
proposed — and `sota_delta` is correctly zero on time, memory and data.

## One next concrete action

**Run EXP-CANL-86c465 STAGE 0 exactly as pre-registered, extended by one stratifier — ideal
class, not only `|D_E|` — before any KN-FIND promotion or any approval of these contracts.**
Minutes of compute; it is the falsifier the decision itself names. Falsifiable predictions,
stated here in advance:

- STAGE 0 **confirms** `N(alpha) >= |D_E|/4` for all `alpha in O \ Z`, and **refutes** the
  decision's equality clause for `D_E ≡ 1 (mod 4)` [A3-a].
- The stratified extension shows the ratio-of-minima law (`>= sqrt(|D_E|)/2`, slope 0.5) holds
  for the **principal** class and stays `O(1)` for roughly half the non-principal classes at
  every `|D_E|` [A3-b].

If that is the outcome, EXP-CANL-86c465's `success_criterion` and `falsification_criterion`
item 3 must be re-scoped to the principal class *before* the contract is ever approved,
otherwise the contract converts a correct measurement into a declared instrument failure.

## What I could not check

- **JKSST (KN-LIT-021) itself.** Not read here; no full text in the repository. Whether `C_0`
  bounds coefficients absolutely or relative to the lattice is therefore **unresolved**, and it
  is the single largest unverified input to this closure. Unchecked, not passed.
- **ECFG-P1543-R0/R1's own derivation** (`ledger/FINDING-PF-IC-001.md`): I read the sections the
  decision cites and confirmed the quoted strings exist, but did not re-derive the `C_0/p`
  reconstruction.
- **Hindry–Silverman, Coates–Wiles/Rubin, Sutherland, Gross–Zagier**: relays, flagged as such by
  their source records; not verified here. My A4-c objection does not depend on Lang's constant
  `c` beyond its being a positive absolute constant.
- **Whether Mordell–Weil O-modules of actual canonical lifts realise non-principal balanced
  classes.** My A3-b result is about the coefficient ring and is exact; whether the physically
  realised modules land there is unchecked by me and by every record in this lane, and is
  precisely what the stratified STAGE 0 would settle.
- **The retrieval index** (`search_knowledge`): not available in this session's tool surface, the
  same limitation the decision records for itself. Absence of a search is not evidence either way.
- **G2, G3, G4, G5** on their merits: out of scope for this review, which was asked to attack the
  closure argument, not to adjudicate the reopening conditions.
- **RQ-ICINV-475b5e / EXP-ICINV-4d33aa**: deliberately untouched per SC-4. Not read, not reasoned
  about, not cited.

---

```yaml
red_team_report:
  id: RT-20260810-3f7ca3
  task_id: TASK-20260810-ea4965
  goal_id: GOAL-ENDO-001
  batch_id: BATCH-de621d
  question_id: RQ-CANL-63098f
  target_of_review: ledger/decisions/DEC-20260810-2c7e3c.yaml
  snapshot_commit: a651a83f6
  verdict: closure_confirmed_with_scope_correction
  claim_under_review: >-
    Lemma 1 (norm-form gap) N(alpha) >= |D_E|/4 for alpha in O off Z, composed with
    hhat(alpha P) = deg(alpha) hhat(P) = N(alpha) hhat(P), places every CM-generated
    companion vector OUTSIDE the Xedni height budget, leaving the instance count at
    Theta(N), so lane L9 closes on the JKSST obstruction rather than clearing it.
  objections:
  - id: A1-a
    severity: material
    statement: >-
      The attacker's volcano freedom is never composed with Lemma 1's hypothesis.
      |D_E| = f_E^2 |D_0|; ascending divides |D_E| by up to f^2. The saving fact that
      D_0 is invariant under (p,t) so |D_E| >= |D_0| appears only in the reachability
      item (a), phrased about class numbers, and never beside Answer 1.
    verdict_impact: none (fixable in one sentence)
  - id: A1-b
    severity: material
    statement: >-
      EXP-CANL-86c465 tail_checks states that for f_E > 1 the O-module structure and
      r_Z = 2 r_O can fail, and requires stratification by f_E. The decision imports both
      unconditionally, and its own headline instantiation (volcano floor) is the f_E = f
      case. Error direction is defender-favourable; the over-stated items are the two
      POSITIVE deliverables credited to CM.
    verdict_impact: none on the verdict; the CM positives are over-stated
  - id: A2
    severity: scope
    statement: >-
      The |D_E| <= 4 C_0^2 regime is inside the rejection scope and contains secp256k1
      (j=0, |D_E|=3) and j=1728. It is handled BY ARGUMENT (EXP-CANL-3c4af4 lattice count,
      re-derived and correct), but by a DIFFERENT and weaker argument than the headline:
      constant-factor accounting conditioned on C_0 and r absolute, i.e. on G6. Answer 1
      is correctly conditioned; the closure narrative and the snapshot commit message are not.
    verdict_impact: scope correction required
  - id: A2-b
    severity: presentation
    statement: >-
      Answer 2 gives the unit tautology and the KN-FIND-003/008 consilience most of its
      length, but units are |O^*| <= 6 of ~3.63 C_0^2 elements; the source itself says the
      Theta(C_0^2) gain SURVIVES deleting them. The load is carried by C_0, r constant.
    verdict_impact: none; will mislead citers
  - id: A3-a
    severity: minor
    statement: >-
      The decision restates Lemma 1's equality clause dropping the source's parenthetical
      "(possible only for D_E even)" and adds "No hypothesis is used". As restated the
      equality clause is FALSE for D_E = 1 mod 4 (D=-3: min off-Z norm is 1, not 3/4).
      The inequality actually used is unaffected.
    verdict_impact: none
  - id: A3-b
    severity: material_load_bearing
    statement: >-
      The composition is valid for a CYCLIC/FREE O-module (the decision's own phrasing) and
      is then generalised universally and used in that general form in Answer 3. For a
      non-principal rank-1 projective module (ideal class a), the Z-lattice aP has
      successive-minima ratio c/a_Q of the class's reduced form, not |D|/4, and for balanced
      classes (a_Q <= sqrt(|D|/3), permitted) the ratio is O(1) at arbitrarily large |D_E|.
      Reviewer arithmetic over all reduced forms: 44/49/62/53 percent of classes have
      c/a <= 4 at D = -2003/-10007/-100003/-1000003; the C_0-window count relative to the
      class's own minimum is 14-16 at C_0=3 versus 6 in the principal class. The norm-form
      gap is a property of the PRINCIPAL CLASS, not of the order. Lemma 1 bounds N(alpha)
      absolutely; the operative quantity is smallness relative to the module's own minimum.
    verdict_impact: >-
      Conclusion survives (the escape is the same Theta(C_0^2) constant as A2, so the
      exponent stays 1), the stated argument does not. Scope correction required.
  - id: A3-c
    severity: material
    statement: >-
      EXP-CANL-86c465 states the module structure over the ring class field H; the decision
      names no field. Over Q the CM action is not defined; over H, [H:Q] = 2h(O) ~ sqrt(p)
      in the floor regime and the "height B implies bit-size Theta(B)" step needs that
      bookkeeping. Answer 3's thresholds (r_Z > 4 -> r_Z > 8; Z-rank >= 6, >= 8 with margin)
      are unusable as forward guidance until the field is stated.
    verdict_impact: none on verdict; forward guidance is unusable as written
  - id: A3-d
    severity: material
    statement: >-
      The record uses an ABSOLUTE-norm coefficient criterion in Answer 1 and a
      RELATIVE-to-lambda_1 criterion in Answer 3 and never reconciles them. KN-LIT-021
      (confidence reported, "full paper not read") describes JKSST's mechanism as an
      absolute coefficient bound, while DECOMPOSITION.md L9 states it as a height ~N. The
      two readings are not interchangeable once the module is non-free. The JKSST relay is
      NOT flagged in limitations although Sutherland and Hindry-Silverman are, and it is the
      obstruction the lane is closed on.
    verdict_impact: unresolved; largest unverified input
  - id: A4-a
    severity: material
    statement: >-
      The pre-registered obstruction is a HEIGHT (~N); the delivered conclusion is an
      INSTANCE COUNT (Theta(N)). The decision's own Answer 3 gives the height budget as
      Theta(N^{2/r}) (N^0.667 at r=3 down to N^0.222 at r=9), contradicting "~N" for every
      r >= 3, and never says so. The lane's kill criterion is therefore stated against a
      quantity that the closure's own analysis corrects.
    verdict_impact: >-
      none on the verdict; DECOMPOSITION.md L9 and RQ-CANL-63098f decision_target should be
      corrected by a superseding record rather than inherited by the next lane.
  - id: A4-c
    severity: material
    statement: >-
      Answer 4 (iii), which the decision calls "the sharpest single statement the lane
      produced", is quantitatively vacuous. The Lang floor c log|Delta| ~ 2c log(mp) grows
      logarithmically in the search parameter; the budget it must exceed is
      B = Theta(N^{2/r_O}), exponential in the security parameter; it binds only at
      m ~ exp(N^{2/r_O}/2c). The source states this threshold in its own survival_score
      ("DIES: at the point where log|Delta| growth makes the Lang floor exceed the height
      budget") and the decision drops it.
    verdict_impact: none on the verdict; the claim as written is not supported
  - id: A4-d
    severity: material
    statement: >-
      Answer 4 (ii) ("a rank lower bound needs a point search of cost B^{r/2}, the same
      search the attack needs") is an unmeasured cost model presented as settled. The attack
      needs a point above a PRESCRIBED residue at height Theta(N^{2/r}); a rank lower bound
      needs any r independent points and descent is the standard method. The source
      pre-registers this as a MEASUREMENT (STEP 4, STEP 5) with OUTCOME 2 as a supersession
      condition.
    verdict_impact: none on the verdict; the m-knob is closed on a scheduled, unrun experiment
  - id: A5
    severity: material
    statement: >-
      "Five independent proposals reach the same exponent-1 verdict from five different
      directions" is inflated: three of them run through the SAME Lemma 1 + Lemma 2
      composition and one cites the other by ID for it. Two legs are genuinely independent
      (target-independence counting; the k^2 size bound). This claim is load-bearing for the
      decision's timing argument (close now rather than pause a fifth time).
    verdict_impact: none on the verdict; the corroboration count is over-stated
  - id: A6
    severity: material
    statement: >-
      Forward guidance clears the closure standard but has three gaps: (1) G6 is described as
      invalidating the load-bearing step yet excluded from the revisit condition, which
      reopens only on G1-G4; (2) IDEA-20260807-13c821 OUTCOME 2 (density of Z-rank >= 6
      members making the search cheaper than N^{1/2} rank computations) is a pre-registered
      supersession condition from a cited source and is not carried forward; (3) no G7 for
      the module-class regime of A3-b.
    verdict_impact: forward guidance incomplete
  required_controls:
  - >-
    EXP-CANL-86c465 STAGE 0 as pre-registered, EXTENDED to stratify by ideal class and not
    only by |D_E|. Zero-risk integer arithmetic, minutes. Predicted: confirms the inequality,
    refutes the equality clause for D = 1 mod 4, and shows the ratio-of-minima law holds for
    the principal class and stays O(1) for roughly half the non-principal classes.
  - >-
    EXP-CANL-86c465 STAGE 1 (numerical hhat(alpha P) = N(alpha) hhat(P) with the
    multiplication-by-m known-answer check). No measurement in this campaign has ever
    confirmed Lemma 2.
  - >-
    Before any KN-FIND promotion: read KN-LIT-021, or state the absolute-vs-relative reading
    of C_0 as an explicit numbered assumption of the closure.
  - >-
    State the field (ring class field H) over which every rank in Answer 3 is measured, and
    stratify by f_E per EXP-CANL-86c465's own tail check.
  counterexample_or_mutation: >-
    Mutation that breaks the load-bearing step while holding |D_E| fixed and large: replace
    the free/cyclic O-module O.P~ by a non-principal ideal class a.P~ with balanced reduced
    form (a_Q ~ c ~ sqrt(|D|)/2). Lemma 1 is untouched and true; the conclusion drawn from it
    is false. Measured at C_0 = 3: 14-16 coefficients in the window versus 6 in the principal
    class, at D as large as -1000003 where Lemma 1 predicts a gap of 250001. The
    discriminating control is the ideal-class stratifier above; the observation-fiber attack
    that produced it is holding the invariant (disc) fixed and varying the object (module class).
  baseline_comparison: >-
    Pollard rho 0.886 sqrt(N) (KN-TECH-001/006) and BSGS memory p^{1/2+o(1)} are used and are
    the right comparators; exponent 1 vs 1/2 stands under every objection above. OMISSION: the
    closest specialised baseline, automorphism-discounted rho on CM curves (KN-TECH-018), is a
    MANDATORY control under RQ-CANL-63098f.constraints and is carried in the drafts' controls
    but is never used in the decision's own comparison - although Answer 2's regime (j=0) is
    exactly where the discount applies and Answer 2's gain is exactly a constant.
  heuristic_challenges:
  - >-
    "C_0 is an absolute constant at fixed arity" is the single hypothesis the closure rests on
    in BOTH escape regimes (A2, A3-b). It is imported from KN-LIT-021 via ECFG-P1543-R1, is
    relayed from an abstract, is correctly flagged in EXP-CANL-86c465's tail_checks, and is
    named as G6 - which is then omitted from the revisit condition.
  - >-
    "Under the semicircle law for the trace" (EXP-CANL-86c465 STEP 2, giving 0.609) is a
    distributional assumption stated in the draft and dropped behind the word "generic" in the
    decision. The 0.609 integral itself re-derives exactly.
  - >-
    Random-model transfer: a minimal-norm element of an ideal class is not a uniformly random
    element of O, which is precisely how A3-b arises. The cheapest computation exposing the
    deviation is the ideal-class stratifier, and it costs seconds.
  cost_model_challenges:
  - >-
    Per-attempt x inverse-success bookkeeping is present and correct in EXP-CANL-86c465 STEP 5
    (T = cost(lift of r_Z/2 + 1 points) * N/(2C_0+1)^{r_Z/2+1}); success probability is never
    silently set to 1.
  - >-
    Memory is charged only in the reachability item (class polynomial p^{1/2+o(1)} space,
    matching BSGS). No time-memory interpolation is offered because no candidate algorithm is
    proposed; that is appropriate here.
  - >-
    A4-c and A4-d: one leg of the m-knob closure is a log-vs-exponential comparison the record
    never performs, and another is a naive-search cost model contradicted by descent.
  reduction_and_scope_challenges:
  - >-
    Scope is stated exactly and is not inflated: no ECDLP claim, supersingular curves,
    non-prime fields and anomalous N = p excluded, sota_delta zero, claim_tier toy, no attack
    on any deployed curve claimed or implied. Verified against the record's own text.
  - >-
    The one scope defect is understatement of the argument's conditions, not overstatement of
    its conclusions: the closure covers regimes (small |D_E|; non-principal module classes)
    that its named load-bearing lemma does not reach, on a different and weaker argument.
  proof_architecture_challenges:
  - >-
    Observation-fiber: holding disc(O) fixed and varying the module class puts two preimages on
    opposite sides of the conclusion. Missing separator: the Steinitz class / freeness of the
    Mordell-Weil O-module.
  - >-
    Quantifier order: Lemma 1 is "for all alpha in O off Z" and is sound; the failure is at the
    next quantifier, "for all CM-generated companion vectors", which ranges over a module the
    argument only controls when it is free.
  - >-
    Boundary/strictness: the Z-case is correctly embedded as the boundary (the coefficient set
    equals the Z one), and the perturbation is shown to be non-strict - which is the closure.
  - >-
    Nearby object: the closest object where the desired conclusion fails is exactly the
    balanced non-principal class, and the record does not distinguish it.
  narrowest_supported_statement: >-
    Within prime fields, ordinary E/F_p, the Serre-Tate canonical lift and global CM models
    reducing to it, fixed arity 2 <= r <= 9 with C_0 an absolute constant, and the twelve
    enumerated mechanism families: no CM-specific mechanism examined in lane L9 moves the
    Xedni instance-count exponent off 1 against Pollard rho's 1/2. The support is (i) the
    target-independence bound Pr[Q in red(S)] <= |S|/N = p^{-1+o(1)} for the four
    (E,O,K)-definable point-lifting routes, and (ii) the fact that every coefficient-set
    enlargement CM can produce is a function of C_0 and r alone. The norm-form gap supports
    this only for cyclic/free O-modules with |D_E| > 4 C_0^2. Nothing is asserted about ECDLP
    hardness, about route L5 (G3), or about any construction outside the enumerated families.
    Derivational, zero runs, claim_tier toy, sota_delta zero.
  next_concrete_action: >-
    Dispatch a minimal confirmation task running EXP-CANL-86c465 STAGE 0 and STAGE 1 as
    pre-registered, EXTENDED by an ideal-class stratifier, before any KN-FIND promotion and
    before any of the seven contracts is approved. Minutes of compute. If it returns the
    predicted split (law holds for the principal class, flat for balanced non-principal
    classes), supersede DEC-20260810-2c7e3c with the two-regime scope correction above and
    re-scope EXP-CANL-86c465's success_criterion and falsification_criterion item 3 to the
    principal class, so the contract cannot convert a correct measurement into a declared
    instrument failure.
  unchecked:
  - KN-LIT-021 (JKSST) primary text - not in repository, not read; absolute-vs-relative C_0 unresolved
  - ECFG-P1543-R1's own C_0/p reconstruction - quoted strings verified, derivation not re-derived
  - Hindry-Silverman, Coates-Wiles/Rubin, Sutherland, Gross-Zagier - relays, flagged by their sources
  - whether Mordell-Weil O-modules of actual canonical lifts realise non-principal balanced classes
  - retrieval index (search_knowledge) - not in this session's tool surface
  - G2, G3, G4, G5 on their merits - out of scope for this review
  - RQ-ICINV-475b5e and experiments/EXP-ICINV-4d33aa - deliberately untouched per SC-4
  artifact_paths:
  - coordination/goals/GOAL-ENDO-001/batches/BATCH-de621d/reviews/red-team/red_team_report.md
  records_read_at_snapshot:
  - ledger/decisions/DEC-20260810-2c7e3c.yaml
  - ledger/questions/RQ-CANL-63098f.yaml
  - ledger/handoffs/TASK-20260810-ea4965.yaml
  - analysis/endomorphism-isogeny-decomposition/DECOMPOSITION.md (section L9)
  - experiments/EXP-CANL-86c465/specification.yaml (full)
  - experiments/EXP-CANL-3c4af4/specification.yaml (full)
  - experiments/EXP-CANL-8687b3/specification.yaml (objective A-E)
  - experiments/EXP-CANL-1064e0/specification.yaml (objective A-C)
  - ledger/proposals/IDEA-20260807-13c821.yaml (B, C2, C3, D, survival_score)
  - knowledge/literature/KN-LIT-021.md
  - ledger/FINDING-PF-IC-001.md (cited sections)
  - experiments/EXP-CANL-{108f26,50a70f,751d2b}/specification.yaml (status fields only)
  runs_executed: 0
  claim_tier: toy
  sota_delta: 0
  dominated_by: not_applicable_no_algorithm_proposed
  inference:
    requested_policy: review-adversarial
    resolved_model_id: claude-opus-5
    reasoning_effort: null
    fallback_used: true
    fallback_reason: >-
      This Claude Code harness cannot resolve policy aliases (CLAUDE.md, "Model policy note"):
      subagent frontmatter cannot express a policy, so review-adversarial resolves to the single
      model the session runs on. Recorded, never silently substituted (AGENTS.md rule 11). No
      requirement of review-adversarial is known to be unmet by the resolved model;
      reasoning_effort could not be verified from inside the session and is left null rather
      than asserted. degraded_allowed remains false.
    degraded_allowed: false
    degraded_requirements: []
    model_verified: false
    model_verified_reason: >-
      No `python3 -m orchestration.adapter doctor --probe` receipt was obtained for this session.
      The identifier is the session's declared identity, not a probe result.
    independent_session: true
    independence_limitation: >-
      This review and DEC-20260810-2c7e3c resolve to models on the same backend (this harness has
      only one). "Independent" here means independent context and a fresh adversarial reading of a
      committed snapshot, NOT independent judgement from a different model. This is the standing
      limitation on every review in this campaign under the suspended closure quorum, and it is
      recorded, not worked around.
  authority_note: >-
    This report changes no research status. DEC-20260810-2c7e3c, the seven EXP-CANL-* contracts,
    RQ-CANL-63098f and the GOAL-ENDO-001 record are unedited and uncommitted by this task. Nothing
    here is durable evidence until the Coordinator's ledger archive commits it.
```
