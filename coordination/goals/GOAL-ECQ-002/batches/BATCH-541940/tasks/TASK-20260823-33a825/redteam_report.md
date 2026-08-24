# RT-20260823-33a825 — Red Team, joints J3 and J4

TASK-20260823-33a825 · BATCH-541940 · GOAL-ECQ-002 · H-ECQ-8b600d
Snapshot read: `b6e071e03f84361ae1b6da3055ffaeb5ca1c8685`, receipt
`coordination/goals/GOAL-ECQ-002/batches/BATCH-541940/archives/TASK-20260823-1f16e5/receipt.yaml`.
Requested policy `review-adversarial`; answered by **`claude-opus-5`**, reasoning effort `xhigh`,
`fallback_used: false`, `degraded_requirements: []`, `model_verified: false` (no
`adapter doctor --probe` in this session). No sibling report was opened. No MCP retrieval tool was
exposed to this session; corpus checks were direct reads of `knowledge/`.

Structured record: `objections.yaml` in this directory. This file is the argument.

---

## Verdicts

| joint | verdict |
| --- | --- |
| **J3** — does tuple choice really move the envelope, or is the spread an artifact of tuple size or selection | **breaks in part.** The lever is real and is *not* a size artifact — that half I could not break, and I tried. The stratification table built on top of it breaks on two counts. |
| **J4** — is the required null adequate, and would anything satisfy C1' honestly | **breaks.** The bottom rung of the ladder is not a null object, and the reading the producer draws from it is inverted. Nothing satisfies C1'; the negative is true but narrower than framed. |

---

## 1. What I could not break

Three things survived everything I pointed at them, and they should be carried forward with
confidence rather than hedged.

**The height definition is right.** `h = log max(|c4|³, c6²)` on the minimal model reproduces the
frozen board's own `naive_height` to `0.0` on seven curves spanning ranks 1 to 30 (ids 42, 55, 50,
157, 244, 276, 273). The comparison in §4 is definitionally aligned with ICARM.

**The four candidates are right.** I wrote my own implementation of the construction from the
statement in H-ECQ-8b600d (`p = q(x−T)q(x+T)`, `g` the monic degree-6 truncation with
`deg(p − g²) ≤ 5`, `r = g² − p`), imported none of the producer's modules, and recomputed from the
*tuple and t alone*:

```
[0,20,40,45,52,77] t=23  -> 86.7736939094   (report 86.7737)
[0,1,53,55,64,67]  t=9   -> 74.1214782342   (report 74.1215)
[0,1,29,32,33,37]  t=10  -> 61.1273905394   (report 61.1274)
[0,2,44,49,51,58]  t=4   -> 68.6386346419   (report 68.6386)
[0,1,2,5,6,7]      t=1   -> 25.4297385256   (report 25.4297)
(-17,-16,10,11,14,17) t=4 -> 79.6237719007  (published tuple A control; BATCH-f2341e got 79.6)
```

Minimal a-invariants match exactly in every case. `surface.py` is also correct: my independent
fibre census reproduces `sum_m_v_minus_1`, the ceiling, the full place-and-type list and the Euler
check `Σ deg·v(Δ) = 24 = 12d` on six tuples across four ceiling classes.

**The bookkeeping is right.** Snapshot sha256 `118db069…cadc59` recomputed and matching; 13391 is
exactly the deduplicated union of the three scans (5627 + 7603 + 292 − 131 overlaps); 16 108 764 =
3 819 816 + 12 288 948; 13 624 = 5817 + 7807; the 1489 and the 46 both reproduce exactly. Every
frontier value is read at run time. There is no transcription defect and no arithmetic defect in
this batch.

**So the negative is a TRUE negative.** 86.7737 really does miss 79.329 by +7.4447 and 69.3389 by
+17.4349. I looked for the false-negative story the Coordinator's own failure-mode note warned me
about and there is not one. What is wrong in this batch is the *explanation* attached to the
negative.

---

## 2. J3, first half: the lever is real and it is not tuple size

The literal question is whether the 220-unit spread is an artifact of tuple size or of selection.
It is neither.

**Size.** A pure size statistic explains R² = 0.19 (log P₂) or 0.27 (log spread) of the envelope
variance. That leaves most of it unexplained, but a low R² over a wide covariate range can still
hide a size story, so I did the direct thing and looked *inside* narrow content bands:

| log P₂ band | n | min env | max env | spread | IQR |
| --- | --- | --- | --- | --- | --- |
| 5.00–5.25 | 32 | 38.52 | 102.23 | 63.71 | 25.29 |
| 6.00–6.25 | 164 | 38.62 | 130.74 | 92.12 | 25.60 |
| 7.00–7.25 | 769 | 45.56 | 155.91 | 110.35 | 31.55 |
| 7.50–7.75 | 1659 | 46.92 | 167.17 | 120.25 | 33.54 |
| 8.00–8.25 | 2551 | 53.09 | 168.83 | 115.74 | 32.06 |

At essentially fixed coefficient content the envelope still spans 90 to 120 log units with an
interquartile range of 25 to 34. Tuple choice moves the envelope on its own.

**Selection.** The one exact symmetry that could manufacture spread is the scaling
`a_i → L·a_i, T → L·T`, which the scan quotients out. I measured the envelope of `L·(0,1,2,5,6,7)`
over the identical 73-value T-box for L = 1, 2, 3, 5, 7 with my own code. All five give
**25.429739**, at `t = L`. The quotient is exactly information-preserving on this control. Recorded
as a cleared objection, not a finding.

**Therefore prior P1 was right, and right by more than it predicted** — 220 rather than the ~30 it
bracketed — and it was not a prior you designed the measurement to satisfy. I say this first
because everything after it is critical.

**But P1's disbelief instruction was mis-specified, and I am holding you to that.**
"ANY REPORTED ENVELOPE BELOW 79.329" compares a rank-*unconditioned* envelope minimum against a
*rank-12* board record. Followed literally it flags 1489 non-events: the 25.4297 minimum is a rank-2
curve, and the frozen r ≥ 1 and r ≥ 2 cells sit at 11.6136 and 13.5255, so it beats nothing. The
correct target — "any reported height below the frozen frontier value *at the certified rank
claimed*" — has zero hits. The second half of the instruction, "check it is not simply a board curve
rediscovered," did fire on a real case; see §5.

---

## 3. J3, second half: the stratification table

This is the batch's central structural claim and it is what a future batch would be aimed by. It
breaks twice.

### 3.1 The stratifying column is mislabelled for 99.64 % of rows

The table's first column is headed "fibre at T = inf" with values I_14, I_12, I_10, I_8, I_6, I_4,
and §3 says in words: *"exactly one multiplicative fibre at T = infinity, and the type of THAT fibre
decides everything."*

That column is not a measurement. It is `I_(Σ+1)` computed from the row's own `Σ(m_v − 1)`. I read
the producer's own `fibre_types` field — whose last entry is the place `infinity` — and
cross-tabulated:

| Σ(m_v−1) | ceiling | **actual** fibre at ∞ | n | report's label |
| --- | --- | --- | --- | --- |
| 3 | 15 | I_4 | 14 | I_4 ✓ |
| 5 | 13 | I_4 | 48 | I_6 ✗ |
| 5 | 13 | I_6 | 34 | I_6 ✓ |
| 7 | 11 | I_6 | 5 | I_8 ✗ |
| 9 | 9 | **I_4** | **13257** | I_10 ✗ |
| 11 | 7 | I_4 | 16 | I_12 ✗ |
| 13 | 5 | I_4 | 17 | I_14 ✗ |

The actual fibre at T = ∞ is **I_4 in 13 352 of 13 391 families (99.71 %)** and I_6 in the other 39.
It is a near-constant. It stratifies nothing. The label is correct for 48 rows — 0.36 %.

What actually varies is the number of **reducible finite** fibres:

```
ceiling 15 (n=14)    : 20 finite I_1, nothing reducible          -> Σ_finite = 0
ceiling 13 (n=82)    : 18 I_1, or 16 I_1 + two I_2               -> Σ_finite = 0 or 2
ceiling 11 (n=5)     : 14 I_1 + two I_2                          -> Σ_finite = 2
ceiling  9 (n=13257) : six finite I_2                            -> Σ_finite = 6
ceiling  7 (n=16)    : four I_2 + two I_3, or eight I_2          -> Σ_finite = 8
ceiling  5 (n=17)    : four I_2 + two I_4                        -> Σ_finite = 10
```

So the sentence "Each has 18–20 I_1 fibres over the finite T-line" is true only of the 48 families
at ceiling 13 or 15, and false of the 13 257-family class it is used to describe. My independent
re-derivation confirms every *number* in the table — only the causal attribution on top of them is
wrong. A batch aimed at "control the fibre at infinity" would be aimed at a constant.

**The correct restatement, which is better guidance than the wrong one:** every admissible Mestre
family carries an I_4 (or, rarely, I_6) at T = ∞, so the construction's own Shioda-Tate cap is **15,
never 18** — a tuple-independent fact that the hypothesis and the report are both still reasoning
against 18 about. The steerable quantity is whether the discriminant acquires repeated roots over
the finite T-line.

### 3.2 The min-envelope column does not survive the report's own §6 protocol

§3 reads the sequence 29.77 → 50.45 → 70.26 (ceilings 11 → 13 → 15) as "the two classes that can
host rank 12 are the two classes whose envelopes sit 20 to 40 log units above everything else."
§6 knows perfectly well that you cannot compare populations at unmatched content; §3 does not apply
that knowledge, and it also compares a minimum over 13 257 draws with a minimum over 14.

Both classes are unmatched. Minimum log P₂ is 2.862 at ceiling 9, 4.965 at ceiling 13, **7.082** at
ceiling 15. The high-ceiling classes simply live at larger content, which the report's own
regression prices at ~14.7 log units per unit of log P₂.

Applying the §6 protocol to the §3 table — restrict every class to the common log P₂ window
[7.0824, 8.1209], then subsample the ceiling-9 population to each class's size 20 000 times:

| ceiling | n in window | observed min | size-matched ceiling-9 null, median [5 %, 95 %] | P(null ≤ observed) |
| --- | --- | --- | --- | --- |
| 5 | 5 | 47.188 | 84.19 [62.31, 108.13] | **0.001** |
| 7 | 5 | 53.356 | 84.33 [62.34, 108.22] | **0.004** |
| 11 | 2 | 64.079 | 97.49 [68.61, 129.66] | **0.026** |
| 13 | 37 | 53.033 | 66.14 [54.17, 78.33] | **0.033** |
| 15 | 7 | 72.168 | 80.52 [60.37, 100.99] | 0.255 |

Every high-ceiling class is at or *below* the size-matched generic minimum. Ceiling 13 beats 96.7 %
of size-38 draws from the generic class. Ceiling 15 is indistinguishable from the null. The
"20-to-40 log units above everything else" reading is produced by content mismatch and by
min-of-*n*, and it reverses when both are controlled. Independently, the pooled regression I fitted
on the null-ladder rows gives `envelope = 12.14 + 13.82·log P₂ − 0.30·ceiling`: after adjusting for
content, the ceiling coefficient carries the **opposite sign** to the claimed mechanism.

**Proves-too-much, run unassigned:** the mechanism already fails inside its own table between rows 3
and 4. Ceiling 11, with *fewer* reducible fibres, has min envelope 29.773 — *lower* than ceiling 9's
30.323. The report calls that pair "within the noise of very unequal class populations" and then
treats a pair of exactly the same kind (ceiling 11 vs 13) as the decisive jump. One standard of
evidence for the comparisons that contradict the mechanism, another for the one that supports it.
And the 29.773 anchoring the "noise" row is a published Elkies–Watkins curve (§5), so that row is
not a measurement of this construction's reach at all.

### 3.3 The negative that carries the interpretive move is at 37 % coverage

§2's pivot — "That reading is the wrong one" — rests on: *"none of those 46 produced a certified
rank-12 fibre inside the searched T-box."* The scoping words are present and correct, and §8 states
the direction of the bias honestly. What is missing is the number.

Reconstructed from the three rank-search run records:

- Of the **46** families with envelope < 79.329 and ceiling ≥ 12, **six were never rank-searched at
  all**, and across the other 40 the search covered **1244 of 3358** available (family, t) pairs =
  **37.0 %**.
- Class coverage: **38 of 82** ceiling-13 families at **19.8 %** of their fibres; **3 of 14**
  ceiling-15 families at **8.5 %** of their fibres.
- Runs 006 and 011 also carried `--max-families 60`, `--t-per-family 40`/`30` and `--height-cap
  120`/`130`, so the searched box was smaller than the declared T-box by design as well as by
  budget. Both hit wall clock; three PARI `alarm`s fired.
- Observed hit rate: 12 certified rank-12 fibres in 1391 searched ceiling-≥13 fibres ≈ 0.9 %. The
  2114 unsearched fibres among the 46 are not obviously empty.

A timeout is never negative mathematical evidence. This conclusion is carrying more weight than
37 % coverage can bear, and the coverage fraction appears nowhere in the report.

### 3.4 What of §3 does survive

The **rank** half of the coupling holds and should be kept. Across all 5169 searched fibres with a
computed ceiling, **zero** exceeded their family's ceiling and only 7 attained it; all 12 certified
rank-12 fibres lie in ceiling-13 or ceiling-15 families; per fibre searched, the high-ceiling classes
did far better (12 hits in 1391) than the generic class (0 in 3454). The ceiling really does bind
attainable rank at the tested scale.

One caveat, in the program's own words. KN-FIND-6b3e17 already narrows this quantifier: Shioda-Tate
caps the *base* rank over Q̄(t) and caps nothing about a specialisation over Q, and the published
record ladder "is built from `extra` of order +10 to +12 on higher surfaces." The report flags this
once and then leans on the ceiling filter as if it were binding. `extra ≤ 0` here across 5169
fibres — but that is 0.36 % coverage of the ceiling-9 class and only |t| ≤ 800. Keep the filter as
an efficient heuristic with its measured support, never as a structural impossibility for the
discarded 1443.

---

## 4. J4: the null

### 4.1 The k = 0 rung is not a null object, and the reading is inverted

`null_ladder.py`'s docstring says `k = 0 -> 0 sections (generic rank 0 by construction)`. §6 then
observes that k = 0 families reached certified ranks 6, 5, 5, 4, 4 at their envelope minima against
the treatment's 8, 6, 5, 5, 5, and concludes: *"the rank that is actually there is largely not coming
from the construction's sections."*

That sentence has no null object behind it, so I ran one — the control this batch owes and does not
have anywhere. **79 random elliptic curves** `y² = x³ + Ax + B` sampled at matched naive height,
measured with the **same instrument** (PARI `ellrank` under an alarm):

| band | n | resolved | rank distribution | max | mean |
| --- | --- | --- | --- | --- | --- |
| h ≈ 60 | 25 | 25 | {0: 13, 1: 12} | 1 | 0.48 |
| h ≈ 70 | 30 | 30 | {0: 12, 1: 16, 2: 2} | 2 | 0.67 |
| h ≈ 93 | 25 | 24 | {0: 10, 1: 14} | 1 | 0.58 |

**Zero of 79 random curves reached rank ≥ 3.** The k = 0 rung's 15 certified curves sit at
h = 69.05–103.62 and give **12 of 15 at rank ≥ 3, 5 of 15 at rank ≥ 4, and one at rank 6**, with
`ellrank` returning `r_low = r_high` in 14 of 15 — i.e. proven ranks. Under the hypothesis that
k = 0 curves behave like random curves of the same height, that outcome is not close to possible.

So the k = 0 families carry **large forced rational rank**, and the mechanism is sitting in the
construction: with three irreducible quadratic factors the twelve geometric sections occur in
**Galois-conjugate pairs, and the trace P + Pσ of a conjugate pair is a rational point.**
`n_sections` counts *rational roots* and therefore reports 0; the rational Mordell-Weil rank is not
0. The ladder's contrast is roughly 11 → 5, not 11 → 0.

The producer's sentence is therefore exactly backwards. The rank at the envelope minima **is** coming
from the construction — from the part the ladder failed to remove. And a secondary confound makes
the comparison unreadable anyway: the k = 6 certified curves span h = 25.43–66.24 and the k = 0
curves span h = 69.05–103.62, so "comparable ranks" is asserted across a 30-log-unit height gap in
data where rank rises steeply with height.

The cheapest confirmation of the mechanism I name costs one number-field arithmetic call: take one
k = 0 family at its envelope argmin, form the trace of one conjugate section pair, and check it is a
rational point of infinite order on the minimal model.

### 4.2 The ladder is unmatched on the variable §3 declares dominant

§3 says the ceiling stratification "explains far more of the variance" than content. §6 matches on
content alone. Ceiling composition per rung, read from the run record:

| rung | n | ceiling distribution |
| --- | --- | --- |
| k6 (treatment) | 150 | **147 at ceiling 9**, 1 each at 5, 7, 13 |
| k4 | 68 | 2 at 7, 4 at 9, 1 at 11, **57 at 13**, 4 at 15 |
| k2 | 72 | 35 at 9, 25 at 13, 12 at 15 |
| k0 | 150 | 95 at 9, 45 at 13, 10 at 15 |

The treatment arm is essentially the generic ceiling-9 population; the null arms are majority
high-ceiling. The cause is the generation scheme, not k: for k = 6 admissibility is obtained by
**rejection** (0.15 % of tuples survive φ = 0), for k < 6 by **solving** the last quadratic's
constant term for φ = 0 (`solve_last_n`), and solved families land in the no-finite-collision
stratum far more often.

This produces an internal contradiction the report does not notice. Under §3's own mechanism the
k = 4 rung — mostly ceiling 13 — should have been *worse* than the mostly-ceiling-9 treatment. It is
better. §3 and §6 cannot both be read as written.

### 4.3 The matching statistic is not a size for three of the four rungs

`content_P2` is the sum of squares of the **centred roots**. That is a size only when the roots are
real. The null rungs have irreducible quadratic factors with complex-conjugate roots, for which
P₂ = s² − 2n can be zero or negative. It is:

| rung | rows with content_P2 ≤ 0 |
| --- | --- |
| k6 | 0 / 150 |
| k4 | 2 / 68 |
| k2 | 16 / 72 |
| k0 | **34 / 150** |

`matched_null` takes `math.log(content_P2)` and keeps only positive rows, so **52 of 440 null rows
are dropped from every content-matched comparison** — 23 % of the rung the report calls "clearly
worse" — with no disclosure. The exclusion is not random: it selects on the root configuration,
which is the manipulated variable.

**Narrowest true conclusion, and I checked rather than assumed:** the dropped rows have similar
envelopes (k0 dropped median 134.36 vs kept 136.64; k2 108.49 vs 112.91). This is a disclosure and
construct-validity defect, **not** a result-changing one.

### 4.4 Differential attrition of >50 % on two rungs, unrecorded

`generation` records `n_generated: 150` for each of k4, k2, k0. The measured rungs are **68, 72 and
150**. So 82 of 150 k = 4 families and 78 of 150 k = 2 families were generated and then failed
measurement, against zero attrition on k = 0 and on the treatment. `null_ladder.py` keeps only rows
with `status == 'measured'`, so the lost families are recorded nowhere and the loss cannot be audited
for bias. The rung carrying the report's most surprising claim is 45 % of its intended sample, and
the report gives its n as 68 and 44 with no mention that 150 were drawn.

### 4.5 No uncertainty is reported anywhere, so I computed it

In-window bootstrap, 20 000 resamples:

```
median(k6) − median(k4) = +21.56   95% CI [ +8.59, +32.78]
median(k6) − median(k2) = −10.04   95% CI [−23.64,  +4.89]
median(k6) − median(k0) = −35.27   95% CI [−46.27, −29.09]
```

After adjusting for **both** content and ceiling (pooled OLS, n = 337), mean residual by rung:

```
k6  −11.41  [−14.58,  −8.19]
k4  −17.53  [−24.64, −10.08]
k2   −0.86  [ −7.74,  +6.28]
k0  +25.95  [+21.18, +30.63]
```

**Both of the producer's directional readings survive my adjustment** as statements about the
measured populations: k = 0 is much worse, k = 4 is not worse than k = 6. What does not survive is
what either one *means*, because of §4.1 and §4.2.

### 4.6 Prior P3

**Held at the bottom rung only, and for a smaller rank contrast than the plan supposed.** k = 0 is
worse by ~37 log units of adjusted mean residual with a clean interval, so the premise does not
collapse. The ladder is not monotone. And because the bottom rung retains roughly half the
construction's rank, "rank buys something" is demonstrated for the step 11 → ~5 and is **untested**
for the step to 0. P3's `if_contradicted` branch — "the entire A2 premise collapses" — is **not**
triggered and must not be reported as triggered.

---

## 5. Would anything here satisfy C1' honestly?

No, and the negative is correctly established on every number I could re-derive. Three additions.

**A board curve *was* rediscovered, and it is not in the report.** §4 says "none of the four is a
board curve rediscovered," which is true of the four curves it displays. But `best_candidates.json`
carries **twelve** `records`, and three of them — the best certified curves at rank thresholds 3, 4
and 5 — have `already_on_the_frozen_icarm_board: true`. The curve is `[1,-1,0,-415,3481]`,
`curve_key 19929:-2917917`, h = 29.772761127041008 = ICARM snapshot **id 108**, whose commentary
reads: *"From the tables of Elkies–Watkins 2004, 'Elliptic curves of large rank and small conductor'
(ANTS-VI, arXiv:math/0403374)."* So the §3 table's ceiling-11 row minimum **is a published curve**.

Your P1 instruction to "check it is not simply a board curve rediscovered" fired on a real case and
the firing was not surfaced. Read the other way — which the report also does not do — this is the
batch's strongest **positive control**: the pipeline independently rediscovered an Elkies–Watkins
curve at its exact board height, and the claim is unmade.

**No Cremona check was performed.** Only the ICARM snapshot was checked, by `curve_key` and by
a-invariants. C1' names both. Immaterial for the four large candidates; material at the low-envelope
end, where the curves are small enough to be tabulated (the 25.4297 minimum is
`[1,0,0,-100,375]`, discriminant 559 625).

**The submission-format artifact drops its best descent evidence.** C1' clause (b) is acceptance by
the ICARM verifier via exact 2-descent. The rank-12 candidate's *run record* carries
`pari_ellrank_r_low = pari_ellrank_r_high = 12` — a descent-based *determination* of the rank, the
single most relevant field for that clause. `best_candidates.json` reports only `rank_lower_bound`.
The material exists; the ICARM-format record loses it.

**One scope correction to the task card, not to the producer.** The frozen frontier carries 30
thresholds; `best_candidates.json` compares **twelve**, because thresholds 13–30 have no certified
curve to compare. "No cell taken at any of 30 rank thresholds" overstates the tested scope. The
honest wording is "no cell taken at the 12 thresholds where this batch certified a curve, and no
curve at all at thresholds 13–30." Same operational conclusion; narrower claim. The producer's own
report says twelve.

---

## 6. Does the batch license the aim it appears to license?

You asked me to test this failure mode specifically. **No.**

§3 reads as *"Axis A2's premise runs straight into a structural obstruction."* The obstruction it
names — the fibre at infinity, and a ceiling that costs envelope — is not the one the data measure
(§3.1, §3.2). Under `docs/inventor-protocol.md` §4 a closure needs a named obstruction, an argument,
and forward guidance; this one names an object that turns out to be a constant.

The obstruction that *is* measured, stated with a quantity, a value and a scope:

1. **Density.** In an exhaustive census of admissible canonical 6-tuples of spread ≤ 74 (n = 13 077),
   only **90 (0.69 %)** have ceiling ≥ 13, and of those exactly **one** has log P₂ < 5, two below 6,
   twelve below 7. High-ceiling *and* low-content tuples are rare in the box searched.
2. **Rate.** Among 296 searched ceiling-≥13 fibres below h = 80, **zero** reached rank 12 and four
   reached rank 11, against P(rank ≥ 12) = 0.002 at h ∈ [80, 90], 0.006 at [90, 100] and 0.044 at
   [100, 120].

That obstruction's forward guidance is *"the search was cut off, finish it and change what you
enumerate"* — not *"the lever is dead."* A count of tuples that turned out to have the wrong fibre
configuration is a fatigue report about an enumeration order, not a statement about Mestre's
construction.

**The resource re-reading the producer missed.** The universal I_4 at T = ∞ is a hard,
tuple-independent cap of **15** on rank MW over Q̄(T) for this whole construction — worth stating on
its own, since the hypothesis and the report are still reasoning against 18. Its complement is a
**free pre-filter**: a tuple can host rank 12 only if its discriminant is squarefree (or nearly so)
over the finite T-line, and that is one resultant on a degree-20 polynomial — microseconds, no
height evaluation, no `ellrank`. In the exhaustive box it cuts the measurement set from 13 077 to 90.
Charging the filter's own cost, as `KN-LIT-7593` requires, does not change this: the resultant is
cheaper than a single one of the 73 height evaluations it replaces. **This batch spent essentially
its entire measurement budget on families that structurally could not host the target rank, and the
filter that would have prevented that is free.**

---

## 7. Narrowest supported statement

Over 13 391 admissible Mestre families (an exhaustive census of canonical admissible integer
6-tuples of spread ≤ 74, plus 312 sampled to spread 600, plus the two published tuples), each
measured on one fixed 73-value T-box with |t| ≤ 800, the minimal-model naive-height envelope varies
by 220 log units, and by 90–120 log units even at fixed coefficient content, so **tuple choice is a
real lever on the envelope**. Of those families, 90 in the exhaustive box (0.69 %) have a
Shioda-Tate ceiling of 13 or 15; **every** one of the 13 391 has a multiplicative fibre at T = ∞, of
type I_4 or I_6, capping the construction at 15 rather than 18. A rank search covering 5169
(family, t) pairs — 37 % of the load-bearing 46 families, 19.8 % of the ceiling-13 class, 8.5 % of
the ceiling-15 class, with three runs stopped by wall clock — certified rank 12 at twelve fibres, the
smallest at h = 86.7737, missing the frozen r ≥ 12 cell (69.3389) by +17.4349 and the published
construction-class best (79.3287) by +7.4447. No cell was taken at any of the twelve thresholds
where this batch certified a curve, and no curve was certified at thresholds 13–30.

**Not supported at this scale:** that the fibre at T = ∞ varies or explains anything; that a higher
Shioda-Tate ceiling costs envelope; that families of ceiling ≤ 11 cannot host a rank-12
specialisation; that the required null contrasts rank 11 against rank 0; and that the rank present at
the envelope minima is not coming from the construction.

---

## 8. Next concrete action

Before any re-aim of GOAL-ECQ-002, run **one** bounded job that settles the only live question this
batch leaves:

> Enumerate admissible canonical 6-tuples with the **free squarefree-discriminant pre-filter applied
> first**, over a spread box large enough to yield a few hundred ceiling-≥13 families at log P₂
> below 6; then rank-search all of them **plus the 2114 unsearched fibres of the existing 46** across
> the full declared T-box with no height cap; and report the coverage fraction reached and the
> certified-rank-versus-height curve **with the random-curve null beside it**.

That job tests the tuple lever exactly where it has never been tested — high ceiling at *low*
content — and it completes the truncated negative in the same pass. If it returns no rank-12 fibre
below 79.329 at full coverage, the lever is closed with a measured obstruction. If it returns one,
the batch's central interpretive move was wrong. Either way it is one job, and it is the same job.

Owed controls, in priority order: **RT-CONTROL-4** (finish the truncated search), **RT-CONTROL-2**
(a bottom rung that really has no rational sections — take q irreducible with full Galois group),
**RT-CONTROL-5** (stratify or match the ladder on ceiling), **RT-CONTROL-3** extended to n = 200 and
to h ≈ 80 and 100.

---

## 9. Attestation

Joints owned: **J3, J4**. Verdicts: J3 *breaks in part*, J4 *breaks*. `read_sibling_reports: false`
— no file under any sibling review task directory was opened, listed for content, or searched; the
only sibling-adjacent path read was the batch-level `review_plan.yaml`, which the task card names as
an input. Full path list, blindness statement, and the honest limits of my re-derivations (RT-RD1 is
blind in the strong sense; RT-RD2 and RT-RD3 use my own implementation but I had already read
`surface.py` and `measure.py`, so knowledge of their approach cannot be excluded) are in
`objections.yaml` under `review_attestation`.

Own budget: ~2600 s wall clock of 3600, 9 runs of 40, well inside 3 GB. My first random-null
invocation was killed at a 600 s timeout and its partial output was **discarded, not used**; the
restarted run was stopped at n = 79 rather than a target of 200, so §4.1's null is reported as a
bound and not as a distribution. Those are infrastructure outcomes of *my* task and are not
mathematical evidence either.

No ledger record, hypothesis status, goal status, or producer artifact was modified. Nothing was
committed.
