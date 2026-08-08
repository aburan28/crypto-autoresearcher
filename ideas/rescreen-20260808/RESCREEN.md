# Targeted novelty re-screen — KN-FIND-006 and KN-FIND-a8990a

Red Team, 2026-08-08. Adversarial re-screen requested by the Coordinator after the
`KNOWLEDGE_BARRIERS.txt` block-scalar extraction defect.

## Snapshot reviewed

- Repo: `/tmp/wt-ideas-100`, branch `ideas/bulk-portfolio-20260808`.
- **HEAD moved during this review.** At first read HEAD was `6e000e0f8` and six
  proposals (`IDEA-20260808-3fdef7`, `-5ee6b4`, `-ba4e37`, `-ceca08`, `-d830c6`,
  `-ea3b4f`) were untracked working-tree files. They were committed mid-review as
  `61f8062e5` ("ideas: +6 (E3b) -> 116 total"). **All verdicts below are against
  `61f8062e5`, 116 tracked proposals.** Nothing in this report rests on a
  working-tree-only artifact. No repo file was written or committed.
- Barrier records read in full: `knowledge/findings/KN-FIND-006.md`,
  `KN-FIND-a8990a.md`, `KN-FIND-a1f3c2.md`, `knowledge/techniques/KN-TECH-057.md`.

## Three findings the Coordinator should read before the table

**1. The extraction defect is FIVE records, not four.** Line 117 of
`KNOWLEDGE_BARRIERS.txt` reads `- KN-TECH-057: >-` — the literal block-scalar
token, not a title. KN-TECH-057 is "Full-cost matched baselines for classical
supersingular path-finding (Wiener 3D wiring model applied to MITM,
Delfs-Galbraith, and van Oorschot-Wiener collision search on the isogeny
graph)". **19 of the 116 proposals touch that ground**; 12 of the 19 cite
KN-TECH-057 anyway, 7 do not. That surface is outside my assignment and I have
not adjudicated it. `IDEA-20260808-3fdef7` — filed by a generator in this same
batch — independently found this defect and names all five records. It is
correct and should be actioned.

**2. The blast radius of the defect on these two barriers is smaller than
feared, because generators went around the corpus.** 8 of 116 proposals cite
`KN-FIND-006` (093497, 11b8c7, 3fdef7, 6a2b50, afe4ce, b188d0, d25ea7, fc5e3e);
5 cite `KN-FIND-a8990a` (093497, 11b8c7, 3fdef7, 481e07, da1428). Several read
the source `.md` in full and quote its internals correctly. The dedup corpus was
damaged; the `knowledge/` tree was not, and at least six generators used it.

**3. The most serious screening failure in this batch is not caused by your
defect.** `IDEA-20260808-2e14f7` duplicates `IDEA-20260807-fed641`, which was
**fully visible** in `EXISTING_PROPOSALS.txt` (line 454) and which 2e14f7's own
`novelty_screen` claims to have read ("all RQ-MODEL-e61cb2 ... rows"). See the
per-proposal entry. Fixing the extractor will not catch that class of miss.

## Does KN-FIND-a8990a add a constraint KN-FIND-a1f3c2 did not?

Yes, four, and one of them is a correction to a1f3c2 itself.

| Added by a8990a | Present in a1f3c2? |
|---|---|
| Derivation uses only (P1) `pi` finite separable of degree 2 with `K(E)/K(x)` Galois, and (P2) inversion ≠ id — so it holds in **every** characteristic including 2 and 3, and for every model | No. a1f3c2's sketch is prime-field `p>3` and uses `y_i^2 = f(x_i)` explicitly |
| Non-collision step: `sum_{i in S} eps_i P_i in E[2]` is a proper closed subscheme avoided by the generic point | **No — `CORR-20260807-652652` records that a1f3c2 skipped exactly this step.** a1f3c2 alone was an incomplete sketch, not a sound barrier |
| Theorem B: exact factorization dichotomy (totally split, or `2^{m-3}` quadratics, nothing else); all factor degrees equal; exact class counts `S^k N^{n-k} + N^k S^{n-k}`; split density within `31(m-1)^2/(2^{m-1} q)` of `2^{-(m-2)}`; **the trace cancels at first order at every m** | No |
| Discriminant corollary: `disc_T S_m` is a **square** for `m >= 4`, non-square only at `m = 3` — so any statistic built on the discriminant's character is **vacuous for m >= 4** | No |
| Theorem C strengthened into the **census obstruction**: any factorization-type / cycle-type / Frobenius-class statistic is *identically constant* on the factor-base locus, at every m, for every curve | Weaker form only ("Frobenius acts as the identity on the factor-base locus") |

**Does this change any verdict? No — but it changes two reasons.** None of the
three monodromy-adjacent proposals proposes a factorization-type census or a
discriminant statistic at `m >= 4` (I grepped the whole batch: 7 files mention
"discriminant", all in unrelated isogeny/CM contexts; 6 mention split
density/cycle type/Chebotarev, none proposing a summation-fibre census). What
a8990a does change:

- It makes `2e14f7`'s **scope** argument correct — a degree-`d` non-Galois map
  genuinely fails (P1), so neither a1f3c2 nor a8990a covers it — while
  simultaneously supplying the reason the escape leads somewhere strictly worse.
  See below.
- It makes `481e07` a legitimate "consequence the entry does not draw" rather
  than a restatement — which is why its verdict is not DUPLICATE even though its
  arithmetic is wrong.

---

## Verdict table

### Against KN-FIND-006 (Semaev/Weil-descent Macaulay rank deficit)

The 12 proposals my grep (`syzygy|macaulay|rank deficit`, substantive hits only)
returns are the 6 you named plus `d25ea7, fc5e3e, da1428, ec2128, afe4ce,
6a2b50`. Eleven further files match the grep on incidental use of the word
"Macaulay" in UOV/SNOVA/Goppa/MITM contexts (`040db9, 2b4581, 2ef5c8, 348896,
3d3be9, 51e40f, 778f82, d07cd4, f0dd08, 3fdef7, 481e07`); I read their claim
fields and none touches 006's object. No action for those.

| ID | Verdict | Action |
|---|---|---|
| IDEA-20260808-093497 | NOVEL | none for 006; **separate correction needed** (see 481e07) |
| IDEA-20260808-bfa0b9 | NOVEL | optional source_ref to a8990a Thm C |
| IDEA-20260808-b188d0 | NOVEL | already discriminated; one caveat |
| IDEA-20260808-f104a2 | **PARTIAL-OVERLAP** | add `discriminated_from` (text below) |
| IDEA-20260808-9ef88c | **PARTIAL-OVERLAP** | add `discriminated_from` (text below) |
| IDEA-20260808-5e257f | NOVEL | none |
| IDEA-20260808-d25ea7 | NOVEL | already discriminated; scope the D=3 arm honestly |
| IDEA-20260808-fc5e3e | NOVEL | premise defect flagged, not a novelty defect |
| IDEA-20260808-da1428 | NOVEL | none |
| IDEA-20260808-ec2128 | NOVEL | re-state one novelty_screen sentence |
| IDEA-20260808-afe4ce | NOVEL | none |
| IDEA-20260808-6a2b50 | NOVEL | specificity gap flagged |

### Against KN-FIND-a8990a (Semaev summation cover monodromy)

| ID | Verdict | Action |
|---|---|---|
| IDEA-20260808-2e14f7 | **DUPLICATE** (of IDEA-20260807-fed641, not of the barrier) | withdraw, or reduce to the scope residue |
| IDEA-20260808-11b8c7 | NOVEL | fix two citation errors |
| IDEA-20260808-481e07 | PARTIAL-OVERLAP, **and its headline claim is refuted** | do not dispatch as filed |

---

## Per-proposal reasoning

### IDEA-20260808-2e14f7 — DUPLICATE. Recommend withdrawal.

**Not of the barrier — of a corpus proposal that was visible the whole time.**
2e14f7 claims (i) the factor base may be taken as `u_D^{-1}(W)` for any degree-`d`
map `E -> P^1`, (ii) this escapes KN-FIND-a1f3c2 because the fibre monodromy
becomes `S_d` not `C_2`, and (iii) "higher `d` gives larger fibres per window
element... the fibre multiplicity `d` buys factor-base size that does not consume
bound budget. That is a genuinely different trade... the mechanism's only free
lunch." Its `discriminated_from` asserts the RQ-MODEL lane "classif[ies]
DEGREE-2 maps" only.

That assertion is false. `IDEA-20260807-fed641` is titled "THE FACTOR BASE IS
DEFINED BY THE COORDINATE, SO ASK WHAT A COARSER COORDINATE BUYS — a degree-n
coordinate names n geometric points per coordinate value... **the RATIONAL count
is what matters and it is g\*d with g the rational deck order**". Its section (C)
computes the degree-`n > 2` trade in both regimes:

> (C1) f Galois with deck group inside Aut(E,O), |Gamma| = n. Then deg_t S_m^f =
> n^(m-2) and the Bezout number at geometric factor-base size B = n\*d is
> B^(m-1)/n. Larger n is better — but n is bounded by |Aut(E,O)| <= 6.
> (C2) f non-Galois of degree n. Then deg_t S_m^f = n^(m-1) and the Bezout number
> is B^(m-1). **Strictly worse than (C1) with n = 2 by a factor 2, for every n.**
> The Hessian x is the worked instance.

That is 2e14f7's mechanism, computed, with the opposite conclusion, in a record
2e14f7's screen scope explicitly covers. 2e14f7's degree-3 map (the `y`-coordinate
or `|3(O)|`) is fed641's case (C2).

**I measured the free lunch. It is zero.** For a transitive degree-`d` cover the
expected number of rational points in a fibre is the number of Frobenius orbits,
which averages to 1 by Burnside — the same Chebotarev equidistribution 2e14f7
cites as HA-1's rigorous ingredient. Direct count over `E(F_p)`, 40 random
windows per cell:

```
p= 10007  B= 200   |V|/|W| x-map (d=2): 1.020   y-map (d=3): 0.994
p= 10007  B= 800   |V|/|W| x-map (d=2): 1.016   y-map (d=3): 1.004
p= 20011  B= 200   |V|/|W| x-map (d=2): 0.993   y-map (d=3): 0.995
p= 20011  B= 800   |V|/|W| x-map (d=2): 1.004   y-map (d=3): 1.012
p= 50021  B= 200   |V|/|W| x-map (d=2): 1.018   y-map (d=3): 0.999
p= 50021  B= 800   |V|/|W| x-map (d=2): 1.019   y-map (d=3): 1.013
   [2e14f7 prediction 1 predicts 2.000 and 3.000]
```

The prediction fails its own `d = 2` calibration, where the answer is known. It
is robust to the convention: if instead `W` is restricted to values with a
nonempty rational fibre, the `x`-map gives 2 points per usable window element and
a generic degree-3 map gives `1/(1 - 1/3) = 1.5` — still worse, never better.
The `S_d` monodromy is not an escape, it is the *cause* of the loss: a bigger
monodromy group means a smaller totally-split fraction, and a8990a Theorem C is
exactly the statement that `d = 2` gives complete splitting on the factor-base
locus at every `m` for free (which `IDEA-20260808-093497` correctly banks as its
HA-2). 2e14f7 charges `d^m` per candidate as a constant-factor tax but never
charges the rationality loss.

*Residue that is genuinely not covered by any barrier*: the Galois group of a
degree-`d > 2` summation cover is not computed anywhere in the corpus, and
a8990a's `(P1)`/`(P2)` framing makes precise why neither a1f3c2 nor a8990a
extends to it. That is a one-paragraph scope note, not a design lever, and it
does not carry `recommended_priority: medium` or "the only design lever left
after the corpus's closures".

**Reason to withdraw:** the headline mechanism is refuted at zero compute by a
control the record itself specifies, and the surrounding analysis duplicates
IDEA-20260807-fed641 (C1)/(C2). If it is kept rather than withdrawn, it must be
reclassified `novelty_class: reproduction`, `recommended_priority: low`, the
"free lunch" claim deleted, and this text added:

> `discriminated_from`: IDEA-20260807-fed641 already computes the coarse-coordinate
> trade for degree-n > 2 maps in both regimes — (C1) Galois with deck group in
> Aut(E,O), gain capped at |Aut| <= 6; (C2) non-Galois, deg_t S_m^f = n^{m-1} and
> the Bezout number strictly worse than n = 2 for every n — and states the
> refutation this record's HA-1 needs: the rational fibre count is governed by the
> rational deck order g, not by the map degree n. Measured |V|/|W| ~ 1.0 at d = 2
> and d = 3. THIS RECORD RETAINS ONLY the scope observation that the Galois group
> of a degree-d > 2 summation cover is computed nowhere in the corpus, and that
> KN-FIND-a8990a's derivation from (P1) degree-2-Galois + (P2) inversion-nontrivial
> does not extend to it. No cost advantage is claimed.

*Separate artifact-integrity note:* 2e14f7's `dominated_by`, `estimated_cost`,
`memory_exponent`, `best_known_baseline` and `time_memory_tradeoff` fields
contain leaked serializer output (a literal `>-` inside `dominated_by`, and
values wrapped in embedded double quotes). Whatever produced this record
mis-serialized it; that is worth checking across the batch independently of the
novelty question.

### IDEA-20260808-481e07 — PARTIAL-OVERLAP on novelty; headline claim REFUTED on the merits.

**Novelty:** genuinely not a duplicate. a8990a Theorem C fixes the fibre
arithmetic and the record explicitly says the entry does not draw the degree-axis
consequence — correct, it does not. The record cites a8990a in full and
discriminates properly from `IDEA-20260803-ff7415`, `-9d47e2`, `-a9a95d`,
`-add964`. As a *novelty* matter it should stand.

**On the merits it should not be dispatched as filed.** Its claim is that the
`F_p`-point count of `V(I_R)` "exceeds the number of group-theoretic
decompositions by a factor... [that] equals `2^{m-1}` on the generic stratum",
and it nominates the `m = 2` case as its "KNOWN-ANSWER EDGE: at m = 2 the factor
is 2 and can be checked by hand on a single curve."

I ran that edge. Ordered decompositions `R = Q_1 + ... + Q_m` with `Q_i` in the
`±`-lift of `V`, against `x`-tuples in `V^m` satisfying the Semaev condition
(with the `S_3` polynomial cross-checked against the group law on 4500 random
triples, zero disagreements):

```
p=101/211/307, B=24, m=2, 5 seeds each:  group/ideal = 1.000 in 15 of 15 cells
p=101/211/307, B=18, m=3, 5 seeds each:  group/ideal = 1.000 in 11 of 15 cells,
                                         1.04-1.31 in the other 4
TOTALS (30 cells): ideal = 4112, group = 4366, overall ratio 1.062
                   481e07 predicts 2 (m=2) and 4 (m=3)
```

The reason is elementary: `S_{m+1}(x_1..x_m, x_R) = 0` holds iff some signed
combination equals `±R`, and generically the `2^m` signed sums are distinct, so
exactly one sign vector realises `R` — the map from ordered group decompositions
to `x`-tuples is a bijection on the generic stratum. The `2^{m-1}` in a8990a is
the **fibre** count in the *last* variable (`deg_T S_{m+1} = 2^{m-1}`), which is
a different object from the solution count of `I_R` in `m` variables; the record
transports it across that boundary.

*Preserve the narrowest valid conclusion:* the direction is right and the effect
is nonzero. The measured excess is 0% on the generic stratum and 4–31% on
degenerate strata at `B = 18, m = 3` on toy curves — i.e. the correction is
stratum-driven and small, not a uniform `2^{m-1}`. The record's own falsification
condition 1 covers this outcome, so the honest disposition is a restatement, not
a rejection.

**Required edit:** delete the `2^{m-1}` headline; restate as (a) the audit
deliverable ("record which count each archived artifact used"), and (b) an open
question "what is the ideal-to-group count ratio, per stratum" with the generic
answer given as 1 and the degenerate excess to be measured. `honest_prior_of_survival`
0.85 must come down. **Caveat on my instrument:** I count `F_p`-points of
`V(I_R)` set-theoretically, which is what the record says it means and what a
Macaulay corank threshold sees; if someone intends the scheme-theoretic degree
with multiplicity the number differs, and that distinction is what would settle
any residual disagreement.

**This error has already propagated.** `IDEA-20260808-093497`'s confounder list
carries: "#solutions counted in the ideal includes all sign variants (`2^{m-1}`
of them by KN-FIND-a8990a); the corank threshold must use the ideal-theoretic
count". Same error, same attribution to a8990a, in a `recommended_priority: high`
record. Fix both or neither.

### IDEA-20260808-11b8c7 — NOVEL. Two citation errors to fix.

A topology-matched null (hold the chaining graph fixed, randomise the node
polynomials) is not in the corpus: every existing null is support- or
column-matched, and `IDEA-20260805-f49efb` argues the null is wrong without
constructing an alternative. 006 does not contain this control, and the record
cites 006 and a8990a in full. Verdict stands.

Three defects, none fatal:

1. **Misquotes the barrier.** "KN-FIND-a8990a's NULL-B... rejected at 48.9 per
   cent". a8990a's table reads "NULL-B (S_4 with elliptic structure removed) |
   48.9% of 595 — **rejected**": 48.9% is the fraction that *obeyed* the law, so
   the rejection rate is 51.1%, exactly as a8990a's own `confidence_note` says
   ("null controls the same instrument rejects at 86% and 51%"). The move does
   have discriminating power (100% vs 48.9%), so the argument survives — but a
   number copied wrong in a `discriminated_from` field propagates.
2. **"arm support-null (0 by construction)"** — 006 records the support-matched
   null deficit as **measured** 0 at n = 12, 15, 17, 18, every replicate. Calling
   it "by construction" deletes the one property that made it evidence, and 006's
   own text leans on it ("Any sem-arm deficit is therefore real structure, not
   predictor bias").
3. **The D = 3 arm is a known-answer check, not content.** 006 already attributes
   the degree-3 fall to the descent ("The Semaev-specific content is the
   degeneration; the support-matched null admits none (degree-3 kernel 0)").
   Only D = 4 and D = 5 carry new information, which is where the `8k-1` law
   lives. State that so a D=3 reproduction is not read as a result.

### IDEA-20260808-f104a2 — PARTIAL-OVERLAP. Add a `discriminated_from`.

Different scheme (MAYO), different object; none of 006's numbers apply and it is
not a duplicate. But claim (A) is the *same measurement under the same
methodological barrier*: "at every degree D >= 2 the whipped system's Macaulay
rank is strictly below that of a uniformly random quadratic system with the same
(kn, m, q, D), and **the deficit is a function of k alone**." 006 is this
program's own precedent that a Macaulay rank deficit which is bounded in the
system size — and whose relative size decays, 4.49% to 1.37% — supplies no
asymptotic leverage. A deficit that is a function of `k` alone, at MAYO's fixed
spec `k`, is bounded in the security parameter and is a vanishing fraction of
`binom(kn + D, D)`. The record must reach that conclusion up front, not discover
it after a battery.

Related internal tension worth resolving in the same edit: claim (A) says the
deficit is a function of `k` alone (constant in `n`), while the falsification list
says "The deficit fails to grow with k... recorded as evidence the measurement is
broken". Those are compatible only if `k` is a swept parameter — but MAYO's `k`
is fixed by the specification, so the artifact tell is being applied to a
parameter that does not vary in the object of interest. Per inventor-protocol §3
the parameter that is supposed to destroy the signal here is `n` (system size),
and the record does not sweep it.

> `discriminated_from`: KN-FIND-006 measures the corresponding quantity for
> Weil-descended Semaev systems over GF(2) — deficit(3) = 1, deficit(4) = 8k-1,
> cumulative 8*dim(V) — and records the standing methodological consequence that a
> deficit bounded in system size, whose relative share decays (4.49% -> 1.37% as
> the system grows ~5x), supplies NO asymptotic leverage. This record's claim (A)
> is a deficit that is a function of k alone and therefore bounded in n; by the
> KN-FIND-006 precedent it cannot move an exponent, and the record's deliverable is
> restricted accordingly to the SHAPE of the deficit as an instrument for
> separating whipped structure from the two nulls. The objects differ (MAYO whipped
> trace system versus binary descended Semaev) so no numeric transfer is claimed in
> either direction; what transfers is the boundedness verdict.

### IDEA-20260808-9ef88c — PARTIAL-OVERLAP. Add a one-line `discriminated_from`.

The multiplicative-coset membership ideal, its lattice-ideal Groebner basis, and
the twisted-circulant/DFT diagonalisation are not in the corpus. Prime field,
designed factor base, derived (not measured) solving degree `B-1`. Novel object.

The overlap is one sentence in `sota_delta`: "**the first computable violation of
the semi-regular null in this lane**". KN-FIND-006 is a computable violation of
the semi-regular null — an exactly-closed-form one (`deficit(3) = 1`,
`deficit(4) = 8k-1`, exact for k = 3..7), with a matched null returning exactly 0.
"This lane" is doing load-bearing work in that sentence and should be made
explicit rather than left to the reader.

> `discriminated_from`: KN-FIND-006 already exhibits a computable, exactly-closed-
> form violation of the Bardet-Faugere-Salvy semi-regular prediction — deficit(3) =
> 1, deficit(4) = 8k-1 exact for k = 3..7, against a support-matched null measured
> at exactly 0 — for Weil-descended Semaev systems over GF(2) at membership degree
> 2. This record's calibration point differs on three axes: prime field rather than
> binary, membership degree B rather than 2, and a DESIGNED factor base whose
> solving degree is derived in closed form from the binomial (lattice) ideal rather
> than measured against a null. The claim "first computable violation" is scoped to
> the prime-field decomposition lane; KN-FIND-006 holds the binary one.

### IDEA-20260808-093497 — NOVEL against 006.

Explicitly and correctly discriminated: 006 and KN-LIT-7605/7607 concern binary
Weil-descent systems at membership degree 2; this computes a prime-field
semi-regular null for membership degree `B`, where the linear-in-`B` slope `m/2`
is the entire content and is invisible in the boolean case. It honours
KN-LIT-7607's standing consequence (does not claim a semi-regularity violation as
new for those systems). The three-outcome pre-registration and the
`B^{m(omega-1)+1}` ratio are consistent as I checked them
(`B^{m·omega}/B^{m-1} = B^{m(omega-1)+1}`). Its HA-2 instantiates a8990a
Theorem C correctly: all `m` fixed coordinates are `x`-coordinates of rational
points, so complete splitting applies and the fibre carries `2^{m-1}` roots.

The only required edit is the inherited `2^{m-1}` solution-count error in the
confounder list — see IDEA-20260808-481e07 above. That is a correction, not a
`discriminated_from`.

### IDEA-20260808-bfa0b9 — NOVEL against 006.

Batching `T` targets into one decomposition ideal via `g_T(y)`. No contact with
006's object (no syzygy content; "Macaulay" appears twice, incidentally). No
`discriminated_from` needed. One optional improvement: its cost model M1 turns on
the solution count of the batched ideal, which is where a8990a Theorem C and the
481e07 count question both bite; adding `KN-FIND-a8990a` to `source_refs` would
let the M1/M2 discrimination be stated more sharply. Not required.

### IDEA-20260808-b188d0 — NOVEL against 006, already discriminated.

The `m`-dependence of the last-fall-degree bound on the Petit-Quisquater
diagonal is a quantifier audit of two published statements, and its existing
`discriminated_from` states the relation to 006 accurately ("KN-FIND-006 measures
a deficit over k = 3..7 that KN-LIT-7605 proves for all n at fixed m... This
record does not re-tread that: it asks a question about m").

One caveat to add to prediction 3. It proposes to check "whether the transcribed
statement predicts deficit(3) = 1 and deficit(4) = 8k-1" and calls resolving it
"a standing open item". 006 is explicit that `8*dim(V)` is **measured-exact over
k = 3..7, not derived**, and that two derivation hypotheses were already refuted
(generator-level Frobenius as the source; alpha-orbit invariance under the naive
companion-matrix action, which "fails even on the universal generic space"). 006
also names the favoured open route — a direct count of the degeneracy subspace
`{c : deg(sum c_i f_i) < max deg}`. A literature transcription is unlikely to
produce the low-degree counts, and the record should say the null result there is
the expected one.

### IDEA-20260808-d25ea7 — NOVEL, and the closest to the barrier without duplicating it.

Replacing the syzygy count by the fall image `W_D` is the other side of the
rank-nullity identity, computed from the same archived matrices with one extra
rank. 006 measures the kernel; nothing in the corpus measures the image. The
`discriminated_from` against `IDEA-20260805-d38a8c` (ratio-of-counts, still
kernel-side) and `IDEA-20260803-202a15` (closed form for the magnitudes) is
correct. Cites 006 in full and respects its scope notes (excludes n = 9 and
n = 17 as deficient cells; reports degree-resolved rather than cumulative).

Honesty edit: the primary hypothesis `dim W_3 = 1` is essentially *exhibited* by
006 already — 006 gives one fall polynomial (`P*(1+P) = 0`) and `deficit(3) = 1`.
The record concedes this in its prior (0.8) but the claim field presents it as a
prediction. The novel content is entirely at D = 4 and D = 5, where the question
"does an `8k-1`-dimensional kernel produce an `O(1)`-dimensional image" is
genuinely open. Say so, so a D = 3 confirmation is scored as plumbing.

### IDEA-20260808-fc5e3e — NOVEL against 006; premise defect flagged.

Crossbred on the descended Semaev system with a chaining-subtree variable split
is not in the corpus (KN-TECH-053 records the technique and never instantiates it
here), it cites 006 in full, and it correctly restricts to full-system cells
n ∈ {12, 15, 18}. `novelty_status: unverified` is the right label given the
unrun literature check.

**Premise defect, not a novelty defect.** Its mechanism asserts "this corpus
already measured the object the condition depends on: KN-FIND-006's exact
deficits... are statements about which rows are dependent at low degree, i.e.
exactly the rows crossbred needs to count." That is not what 006 measures. 006
records a *rank* deficit against a semi-regular prediction; crossbred
admissibility needs the **k-degree profile** of independent rows under a chosen
variable split, which 006 records nowhere. The record's own confounder concedes
it ("Committed rank artifacts... may not record k-degree profiles"). The
"evaluate at zero compute from committed artifacts" step is therefore likely to
return UNRUN, and the estimated cost should reflect that.

### IDEA-20260808-6a2b50 — NOVEL, and the sharpest challenge *to* 006 in the batch.

Asking whether the measured solving degree is a coordinate artifact, and whether
006's and GOAL-SIG-001's deficits need restating in a generic frame, is not in the
corpus. It is a proposal to attack a barrier rather than to walk around one, which
is what the inventor protocol asks for.

**Specificity gap that decides whether it has content against 006 at all.** For a
*homogeneous* system, a generic linear change of variables acts invertibly on
each graded piece, so the degree-`D` Macaulay rank — and hence 006's `deficit(D)`
— is frame-invariant and the record has nothing to say about those numbers. The
claim can only bite for the *inhomogeneous* system, where the degree-`D` row space
is not preserved. 006's systems are inhomogeneous (n quadrics + n cubics over
GF(2) with field equations), so the claim probably survives — but the record does
not distinguish the two cases, and which one it means is the cheapest thing that
settles whether it is a restatement obligation or a no-op. Add that as an explicit
step-0 before any frame battery.

### IDEA-20260808-da1428, -ec2128, -afe4ce, -5e257f — NOVEL against 006, no action beyond one note.

- **da1428** (hybrid guess-and-determine optimum is full guessing, prime field):
  no contact with 006's object. Cites a8990a. Novel.
- **afe4ce** (prime-field last-fall-degree FLOOR from the description degree of
  `V`): opposite direction to 006 and to KN-LIT-7605 (a lower bound over prime
  fields, not an upper bound over binary). Novel.
- **5e257f** (censored binary → ordinal `D_reached`): a statistics record with no
  contact with 006's content. Novel. Worth adding 006 as a *supporting* citation,
  not a discrimination: 006's own scope note — "a fixed-degree cross-section is
  the wrong instrument... Do not extrapolate a fixed-D deficit series" — is the
  program's existing precedent for exactly 5e257f's argument that the lane's
  instrument discards its own ordering information.
- **ec2128** (multi-graded Hilbert series for UOV/MAYO/QR-UOV/SNOVA intersection
  systems): different schemes, different object; 006 is a singly-graded GF(2)
  rank deficit, not a multi-graded Hilbert series. Novel. **But** its
  `novelty_screen` asserts "KNOWLEDGE_BARRIERS.txt (no KN-FIND touches
  multi-graded Hilbert series)" — an assertion made against the damaged corpus,
  and therefore unsupported by the evidence it cites even though it happens to be
  true. Re-state it as screened against `knowledge/findings/` directly, or drop
  the parenthetical.

---

## What I checked, and what I did not

Checked: both barrier records in full plus KN-FIND-a1f3c2 and KN-TECH-057; the
15 named proposals in full; the 8 further proposals returned by the
`syzygy|macaulay|rank deficit` and `monodromy|galois|summation cover` greps
across all 116; the claim fields of the 11 incidental-match files; the two
closest priors `IDEA-20260807-fed641` and `-8027a2` in full from the repo; the
truncated rows for 14 further priors in `EXISTING_PROPOSALS.txt`; citation
coverage of both barriers across all 116; the damaged-line inventory in
`KNOWLEDGE_BARRIERS.txt`. Two claims were tested by direct computation rather
than argued (the `481e07` count ratio and the `2e14f7` fibre gain); the scripts
are at
`/private/tmp/claude-501/-Volumes-SSD990-research/470d7176-1bcc-451c-9995-1ef445a7ca69/scratchpad/count_check.py`
and are ~40 lines of self-contained Python with no dependencies.

Not checked, and it would change conclusions if wrong:

- **External novelty.** Every generator recorded "WEB SEARCH UNAVAILABLE" or
  "WEB NOT CHECKED", and a8990a itself records that `eprint.iacr.org` returns 403
  from this environment, including Semaev's own 2004/031. a8990a's own novelty is
  explicitly **not adjudicated**. Nothing in this re-screen adjudicates external
  novelty for anything; all verdicts are internal-corpus only.
- **The 19 proposals touching KN-TECH-057.** Outside my assignment.
- **`IDEA-20260808-2e14f7` vs. published generalised summation polynomials.** Its
  own `novelty_status: unverified` names this gap. My DUPLICATE verdict is
  against the internal corpus and does not depend on it.
- **Whether the `S_d`-monodromy scope residue in 2e14f7 is worth a separate
  record.** I judge not, on the reasoning above, but that is a Coordinator call
  and the residue is real.
