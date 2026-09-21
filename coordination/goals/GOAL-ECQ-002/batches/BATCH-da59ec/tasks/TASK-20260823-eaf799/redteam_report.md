# Red team report — TASK-20260823-eaf799 (joints J3, J4)

BATCH-da59ec · GOAL-ECQ-002 · H-ECQ-a609f8 · red-team
snapshot read: `0cb0165024b3280e83dc7974918d6d82af5039b4` (only committed state at that sha)
requested policy `review-adversarial`; answered by `claude-opus-5` (no fallback, no downgrade)
budget 3600 s / 3 GB; used ~35 min wall clock, peak RSS well under 1 GB
blind to TASK-20260823-72505a; no sibling report read; no file written outside my `write_scope`;
nothing committed.

**Verdicts on my joints.**

| joint | verdict |
| --- | --- |
| **J3** target choice | **BREAKS.** The re-aim moved from one unreachable cell to three that are *harder in absolute terms and held by a single live, advancing program*. The Coordinator's method-class explanation is refuted at its load-bearing premise by the retrieved primary source, and its supporting statistic is a free-text-classifier artifact that flips by 127.5 at the very rank the claim is made. The A2 premise is **not** shown wrong at the root; a *different*, derivable obstruction is. |
| **J4** provenance and C1' | **HOLDS, with two corrections.** Nagao is genuinely unrepresented *as a specialised family*, but the board carries a Nagao curve (#74) and the incumbents use Nagao's sieve throughout, so the hypothesis's phrasing is loose. Nothing in this batch satisfies C1' and nothing accidentally could — verified against all four conditions. Separately, the frozen baseline is missing a metric the live board scores, which is a preregistration defect that must be repaired before any C1' claim is judgeable. |

The batch's **measured result — all three boxes empty — survives everything I threw at it, and I
strengthened it by a factor of 248 in search volume.** That is reported first, below, because a red
team that only reports breaks is not reporting.

---

## 0. What I ran (controls, not commentary)

All compute is mine, from committed inputs, on a code path that imports nothing from
TASK-20260823-f88f54 and never touches its I/J Weierstrass model.

| # | control | result |
| --- | --- | --- |
| C-A | **Blind re-derivation of the height.** Committed `candidate_families.json` quartic → PARI `ellfromeqn` → `ellminimalmodel` → `h = log max(\|c4\|³, c6²)`. Ten fibres. | **Agrees to 1e-10 on all ten** (t = 0, 1, 2, 3, ±58, ±62, −50, 703). The producer's heights are right. |
| C-B | **The uncovered region.** The declared box is \|num t\| ≤ 60 / den ≤ 6 (so \|t\| ≤ 60); the wide probe is den = 1 only. The measured minimum sits at \|t\| = 62 — **on the seam between the two probes.** I swept 40 ≤ t ≤ 200 at every denominator ≤ 12 (7 361 fibres). | **Nothing below 109.505165.** Denominator monotonically *hurts*: min per den = 109.51, 117.79, 135.84, 134.43, 148.10, 144.16, 156.18, 151.07, 162.21, 156.42, 167.03, 160.80. |
| C-C | **Volume attack.** Integers 1…20 000 (20 000 fibres) plus rationals 30 ≤ t ≤ 140 at every denominator ≤ 60 (121 221 fibres). **141 221 fibres against the producer's 569 distinct.** | **Global minimum still exactly 109.505165 at t = ±62.** Second lowest 109.531002. The lower envelope does not descend. |
| C-D | **Fourth metric.** The Coordinator's multimetric doc names four board metrics and checks three, because the frozen frontier file has no discriminant cell. I derived the log\|Δ\| frontier from the frozen snapshot and validated it against the board's own commentary (#276 says log\|D\| = 108.6915; I compute 108.6915). | **No cell taken on the fourth metric either.** Gaps +27.83 (t=1, r≥14) to +87.21 (t=0, r≥6). The Coordinator's conclusion survives the metric it did not check. |
| C-E | **Null-object control for the program-conditioned signal.** Within-rank permutation of program labels at ranks exactly 12/13/14, N = 200 000. | A real signal: P(Elkies lineage holds the minimum at all three ranks under the null) = **0.0031**. But the *magnitude* that carries the Coordinator's inference collapses from 247.6 to 82.7 total under a second, equally defensible classifier. |
| C-F | **Source retrieval of the load-bearing `recalled` citation.** Fetched and text-extracted `abel.math.harvard.edu/~elkies/Elkies_JMM23.pdf` — the URL the board's own commentary cites for all three incumbents. | **Refutes the Coordinator's premise.** See §2. Provenance: `retrieved`. |
| C-G | **Decay test.** Named the parameter that should destroy the empty box (search volume) and asked what the measurement should do. | It does the right thing: the envelope *flattens* (109.531 at 569 fibres → 109.505 at 141 221). This is a controlled null, not a failure to decay. The empty box is not an artifact tell. |

**Consequence.** The narrowest supported statement is now much stronger than the batch's:
over **141 221 distinct fibres** spanning the entire crossover region and every denominator ≤ 60,
NAGAO-1994's minimal-model naive height has lower envelope **109.505165**, attained at t = ±62,
against targets 69.34 / 75.76 / 85.19. It is still a bounded-search negative, but a much better
bounded one.

---

## 1. J3 — the re-aim moved to harder targets, not softer ones

### 1.1 The three new cells are more anomalous in the *wrong* direction

Frontier steps, computed from the frozen file:

```
r>=11  61.507
r>=12  69.339   +7.832    <- new target
r>=13  75.760   +6.421    <- new target
r>=14  85.189   +9.429    <- new target
r>=15 118.770  +33.581    <- ABANDONED target
r>=16 125.334   +6.563
```

r ≥ 15 is the single largest step anywhere below rank 17 — it is the one *outlier* cell, the one
whose incumbent is furthest above the frontier's own trend, and therefore the softest cell in the
range on the criterion the goal record itself used ("jumps 85.19 → 118.77 ... against steps of 9.4
and 6.6 on either side" — both verify exactly). The Coordinator abandoned the outlier and re-aimed
at three on-trend cells whose absolute values are **33.6 to 49.4 lower**, i.e. strictly harder for
any method.

Two different notions of "soft" were conflated. The BATCH-f2341e red team showed r ≥ 15 was hard
*for the Mestre method class specifically* (118.77 is that class's global best across all ranks).
That is a statement about one method. "Soft" in the goal record is a statement about the frontier's
shape. Replacing an outlier cell with three on-trend cells fixes the first and destroys the second,
and no record in this batch notices the trade.

### 1.2 Who actually holds r ≥ 12/13/14 — and the predecessor's claim, checked

Classifying the 289 frozen curves by their commentary, the Elkies low-conductor lineage on the
board is exactly five curves:

```
#88  r=12  h= 73.590  2026-06-11    #157 r=12 h= 69.339  2026-06-24
#89  r=13  h= 79.413  2026-06-11    #158 r=13 h= 75.760  2026-06-24
#244 r=14  h= 85.189  2026-07-06
```

They hold **first AND second place at r ≥ 12 and at r ≥ 13, and first at r ≥ 14.**

The predecessor's claim "#244 is the only rank-14 output of the Elkies JMM23 program, which stops
at 14" is **half right and the wrong half is load-bearing.** On this snapshot #244 *is* the only
rank-14 output — I confirm that. But "stops at 14" is a property of the *snapshot*, not of the
method, and this is the exact failure mode the inventor protocol names: a count of what a program
has published so far is a fatigue report about the board, not a statement about the program. The
evidence against it is in the record itself and in the primary source:

* the retrieved January 2023 slides list candidates for **r = 12 and r = 13 only**;
* #244 (r = 14) was created **2026-07-06**, i.e. the program gained a rank *inside the window the
  board covers*, and #157/#158 (2026-06-24) beat #88/#89 (2026-06-11) at the same ranks two weeks
  later;
* Elkies' own closing slide lists as still to be done: *"Massive runs, extensive statistics."*

So the three cells the Coordinator pre-declared are **the current output frontier of a live,
actively advancing program that improved twice inside the two months this board covers.** They are
the worst available choice of target on the live-board risk that C1' explicitly cares about: their
values are more likely to move before submission than any other cells on the board.

Worth stating plainly: the same lineage (Elkies, and Elkies–Watkins 2004) holds the minimum naive
height at **every threshold from r ≥ 5 to r ≥ 14** — ten consecutive cells (24.32, 30.38, 35.78,
41.83, 47.97, 54.35, 61.51, 69.34, 75.76, 85.19). The frozen slides' own table for r ≤ 11 *is* the
Elkies–Watkins list. The campaign has been aiming at one research program's home turf since the
goal was written.

### 1.3 The Coordinator's method-class hypothesis: premise refuted by the primary source

`COORDINATOR-multimetric-check.md` states:

> the small-curve cells appear to be held by **direct search over small curves**, which buys size
> cheaply and cannot reach high rank. If that is right, then NO amount of work on the
> specialisation axis takes those cells, and this campaign's entire A2 premise ... is wrong at the
> root.

The premise is checkable and it is false. The board's commentary for all three incumbents cites one
URL; nobody in this program had opened it. I did (C-F), and the method is described in the author's
own words:

> *"We could not approach r = 11 by searching all E up to height H: too many such (∼ H^{4+6} =
> H^{10})."*

It is **not** direct search — the author explicitly rules direct search out as infeasible. It is an
algebraic construction: parametrise the moduli space **M_{1,k+1}** of genus-1 curves with k+1
marked points (weighted projective models for k ≤ 4; the Grassmannian of lines in P⁴ for k = 5),
cutting the count from H^{10} to H^{10−k} and "already k = 5 gives H^5". Then:

> *"for each of our parametrizations, pick H, compute E for all parameter values of height ≤ H,
> then compute an approximate **Mestre–Nagao product** ... and send the top scorers to further
> testing: use `ellratpoints` ... and compute the rank of the group they generate."*

Three consequences.

1. **The claimed dichotomy does not exist.** Both sides of the Coordinator's "different method
   classes" are algebraic-construction-plus-parameter-search. There is no "direct search" class on
   the board at these ranks.
2. **The incumbent uses the very heuristic this campaign was told is unvalidated.** Mestre–Nagao
   scoring is the incumbent's selection stage. H-ECQ-a609f8 describes it as "NEITHER validated NOR
   refuted" and demotes it behind an exact height gate. That is defensible as internal discipline,
   but the record should not imply the incumbents avoid it — they run on it.
3. **The identification is exact, not inferred.** The slides' r = 12 row gives
   N = 26145292874820119408329144 and a₄ = −932733487; board #88 has exactly that conductor and
   `ainvs = [0,0,0,-932733487,11052354147250]`. Likewise r = 13 → #89. #88/#89 *are* the slide
   curves; #157/#158/#244 are the "improved version" that beat them.

**There is a real structural difference, and it is not the one written.** Elkies parametrises
`(E, P₁,…,P_k)` — a curve *together with* k small independent integral points — so smallness is
built into the parametrisation and rank emerges from the points. Mestre/Nagao parametrise a curve
over Q(t) of guaranteed generic rank and specialise — rank is built in and size emerges. That is a
genuine "different lever" statement and it is defensible. It is also *not* what the document says,
and it does **not** support "no amount of work on the specialisation axis takes those cells".

### 1.4 The supporting statistic is a classifier artifact, and it flips by 127.5

The Coordinator's quantitative support is the per-rank Mestre-class minima
`206.81(12) 136.69(13) 134.43(14)`, inherited from BATCH-f2341e. Those numbers are not in any
record's derivation; they come from a free-text classifier over board commentary, and the
classifier is underdetermined at exactly the ranks in question.

The board's rank-12 runner-up-but-three is **#1, h = 79.329**, commentary: *"Found by Mestre
(1982). A historical rank ≥ 12 record, via Dujella's elliptic-curve rank-records tables."* At rank
14, **#3, h = 96.986**: *"Found by Mestre (1986)."*

* Classifier **V1** (predecessor-style) keys on *"via Dujella"* — the board's **sourcing** — and
  files these as `DUJELLA_HISTORICAL`.
* Classifier **V2** keys on *"Found by Mestre"* — the **method** — and files them as construction
  class.

| rank | V1 construction min | V2 construction min | Δ | Elkies cell | V2 gap to cell |
| --- | --- | --- | --- | --- | --- |
| 12 | 206.812 | **79.329** | **127.48** | 69.339 | **+9.99** |
| 13 | 136.687 | 136.687 | 0.00 | 75.760 | +60.93 |
| 14 | 134.427 | **96.986** | **37.44** | 85.189 | **+11.80** |
| 15–20 | — | identical | 0.00 | — | — |

The disagreement is confined to the two ranks where the conclusion is drawn. The Coordinator's
hypothesis is about **method classes**; V2 is the classifier that answers that question and V1 is
not. Under V2 the construction class sits **+9.99 and +11.80** from two of the three cells — not
+137 and +49. "No amount of work on the specialisation axis takes those cells" is contradicted by
the board's own data at a distance of ten log units.

Null control (C-E): the program-conditioned signal is real (p = 0.0031 that the Elkies lineage
holds all three minima by chance; p < 1e-4 on the summed gap under both classifiers). What is not
robust is the *magnitude*, which is the only part the inference uses.

*Provenance note.* My reading of #1/#3 as construction-class rests on the board's attribution "Found
by Mestre (1982)/(1986)" plus my own recollection of Mestre's method; I have **not** read Mestre
1982/1986 and mark that step `recalled`. The finding does not depend on it: the classifier is
demonstrably underdetermined either way, and §1.3 refutes the premise independently from a
`retrieved` source.

### 1.5 So: are r ≥ 12/13/14 reachable in principle by any method?

**Not established either way, and the batch does not establish it.** What is established:

* They are **not** structurally closed to construction/specialisation: two board curves from that
  class sit within +9.99 (r = 12) and +11.80 (r = 14).
* They are held by a live program that improved twice in two months and whose author says more
  compute is coming.
* NAGAO-1994 specifically is 30.2 *worse* than Mestre's own 1982 curve at rank 12 (109.505 vs
  79.329) — so this batch's failure is a **family-choice failure, not a structural one**.

**The A2 premise is not wrong at the root. It is wrong in a narrower, derivable way**, and I can
give the obstruction as a measured quantity rather than as an attribution (§3).

---

## 2. J4 — provenance and C1'

### 2.1 Is NAGAO-1994 unrepresented on the board?

The hypothesis's mechanism says: *"the board's own commentary attributes its high-rank small curves
to Mestre and Fermigier families — Nagao is not visibly represented, so the (a, b) it carries is
unmeasured by the incumbents rather than already optimised by them."*

Checked. The word "Nagao" appears in board commentary in two distinct roles:

1. **Nagao as a source of a curve** — board **#74**, r ≥ 21, h = 255.693: *"Provenance: Nagao-Kouya
   (1994), 'An example of elliptic curve over Q with rank ≥ 21,' as reproduced in Nagao,
   'Construction of high-rank elliptic curves.'"* This is Nagao's rank-21 **example curve**, not a
   specialisation of the rank-12 Q(t) family. So "Nagao is not visibly represented" is **false as
   written** and true in the sense that matters.
2. **Nagao as a sieve** — "Mestre–Nagao stage sieve", "native M = 6000 Nagao rescore",
   "Nagao–Mestre prime-sum sieve", and (per §1.3) the Elkies pipeline's own scoring stage. The
   incumbents run on Nagao's rank heuristic throughout.

**Verdict: substantially true, loosely stated, and the inference drawn from it is weak.** No board
curve is a specialisation of Nagao's rank-12 Q(t) family, so its height budget was genuinely
unmeasured. But "the incumbents did not use it, therefore it is an unexploited lever" is the
nobody-tried-it inference, and the alternative reading — Mestre/Fermigier families have been tuned
for exactly this for forty years and Nagao's has not been because it is worse — is equally
consistent with the same fact. The measurement has now settled it in the second direction:
109.505 versus Mestre's own 79.329 at rank 12.

### 2.2 Could anything in this batch satisfy C1'?

C1' has four conjunctive conditions. Checked independently against the frozen snapshot:

| condition | status for the four certified curves (t = 0, 1, 2, 62) |
| --- | --- |
| not present in the frozen ICARM snapshot | **PASS.** I intersected all nine available `curve_key` values against the 289 frozen keys: empty. |
| not a Cremona-table curve | **PASS.** Conductors have 25, 43, 33, 40 digits; Cremona's tables reach N ≤ 500 000 (6 digits). |
| takes a **pre-declared** cell vs the frozen frontier | **FAIL.** Gaps +40.17 / +34.35 / +49.71 / +94.02 on naive height. |
| takes it vs the live board re-read at submission | **N/A.** Nothing was submitted; no live re-read was performed. Correctly, since nothing was eligible. |

**Nothing satisfies C1' and nothing accidentally could.** The exclusions hold: nothing here touches
r ≥ 15 or r ≥ 1. I extend the check to my own 141 221-fibre search (C-C): its minimum is the same
109.505165, so no fibre anywhere in that far larger volume is eligible either.

### 2.3 A preregistration defect that must be fixed before any C1' claim is judgeable

`COORDINATOR-multimetric-check.md` correctly says the board keeps a record per (rank threshold ×
metric) and names four metrics: naive height, Faltings height, log conductor, **discriminant**. It
then tabulates three. The reason is that `frontier_20260823.json` contains only
`min_naive_height`, `min_faltings_height`, `min_log_conductor` — **there is no discriminant cell in
the frozen baseline at all**, while the board plainly scores it: #276's own commentary reads
*"Rank-15 records in naive height, log\|D\| and Faltings: ... log\|D\| = 108.6915 (beats
110.5171)"*.

This is repairable and I repaired it (C-D): the frozen `icarm_database_20260823.json` carries a
`discriminant` field per curve, so the missing cells are **derivable from the authoritative
snapshot**, and my derivation validates against the board's own number to four decimals. Derived
cells: r ≥ 12 → 61.2909 (#157), r ≥ 13 → 65.8371 (#158), r ≥ 14 → 77.1267 (#244), r ≥ 15 →
108.6915 (#276).

Until those cells are written into a superseding baseline record, a discriminant-cell claim is
**unjudgeable against the frozen frontier** — which is precisely the failure mode
`preregistered_baseline.why` was written to prevent. Nothing hangs on it this round (all gaps are
+27.8 to +87.2). It would hang on it the moment a curve got close.

---

## 3. The obstruction the batch should have measured, derived rather than attributed

H-ECQ-a609f8's carried-forward mechanism is:

> the height ... grows only LOGARITHMICALLY in the parameter (h ~ a + b log H(t)), so the binding
> constraint is the family's own (a, b)

and the batch reports (a, b) = (135.9758, 0.3875) with R² = 0.000418.

**The functional form is wrong and the reported b is an artifact of where the box was placed.** The
true law is piecewise, and I measured both arms:

```
small |t| :  h = 119.42 + 0.062 log|t|    R^2 = 0.00005   (n = 40)
large |t| :  h =  11.32 + 24.14 log|t|    R^2 = 0.891     (n = 77, t = 1000..20000)
crossover at |t| ~ 89 ; observed argmin at |t| = 62
```

The producer fitted one line across a **V** whose vertex lies at the edge of its own box, entirely
inside the flat arm. R² ≈ 0.0004 is not "the parameter explains none of the variation" — it is the
signature of the wrong model. (The producer's own note that the fit "is not the deciding number"
saves the *conclusion*; the (a, b) pair itself is meaningless as reported, and the hypothesis's
mechanism rests on it.)

The asymptotic slope is not an accident. For an elliptic surface of degree d over P¹ the minimal
Weierstrass model has deg a₄ ≤ 4d, deg a₆ ≤ 6d, so
`h(E_t) = log max(|c₄|³, c₆²) = 12d·log|t| + O(1)`. Here deg(a₄, a₆) = (8, 12), d = 2, **12d = 24**
— against a measured 24.14. Shioda–Tate caps generic rank at 10d − 2, so generic rank r forces
d ≥ ⌈(r+2)/10⌉ and hence

> **slope ≥ 1.2·(r + 2).**

That is the obstruction, and it is a *derived* statement about the specialisation lever, with no
free-text program attribution anywhere in it:

* buying generic rank r ≥ 9 forces d ≥ 2, which at least doubles the growth rate of the fibre
  height in the Weil height of the parameter;
* so the useful fibres are only those of **small Weil height**, of which there are ~e^{2H} up to
  height H — the small-parameter lever the mechanism relies on is real but *exhausts in a bounded
  region*, which is exactly what C-C measured: 141 221 fibres, envelope flat at 109.505;
* and inside that bounded region the height is dominated by the family's own O(1) constant.

**Resource re-reading** (inventor-protocol §"obstructions are re-read as resources"; role contract
item 8). The same measurement says the binding quantity for the A2 axis is *the O(1) constant of a
minimal-degree-d family*, not the parameter. Two readings the batch does not take:

1. Among surfaces of the **same** d, the constant varies enormously — Mestre's 1982 rank-12 curve
   is 30.2 below Nagao's best fibre. So "search over families at fixed d, minimising the constant"
   is a live and untried direction, and is a strictly better-posed version of A2 than "specialise
   at small t".
2. The measured 109.505165 is an **invariant of Nagao's K3 surface**, not of the transcription: any
   other Weierstrass model of the same surface differs by (x, y) → (u²x + …, u³y + …) with u ∈ Q(t)*,
   so each specialised fibre is Q-isomorphic and its *minimal* model — hence its height — is
   unchanged. This is worth recording because it means the number is reusable and comparable, and
   because it independently confirms that the transcription-scaling defect in §4.1 changes nothing.

Also observed and unremarked in the batch: **every one of the eighteen lowest fibres has even t**
(62, 58, 64, 56, 52, 50, 68, 46, 44, 70, 40, …), with the best odd fibre at 117.80 — a systematic
2-adic saving of ≈ 8.3 in naive height. Structure of that kind is what a congruence-restricted
search would exploit. It is worth 8, and the smallest gap to a target is 24.3, so it does not
rescue this family; it is the right *shape* of idea for the next one.

---

## 4. Attacks on the two Coordinator documents, as instructed

### 4.1 `CORRECTION-predeclared-target-values.md`

**The "changes no conclusion" claim is correct — I verified it — but the reasoning offered for it
is backwards, and the correction misses a live instance of its own root cause.**

*What holds.* Gaps of 24.3–40.2 against transcription errors of 6e-5 and 5.3e-4 — four to five
orders of magnitude. No conclusion moves. The disposition ("the baseline wins", do not edit
H-ECQ-a609f8, derive future targets by computation and record the file's sha256) is right.

*What is backwards.* The correction praises the producer for using the pre-declared values because
they were "the stricter of the two" and therefore conservative. Stricter is conservative for a
**claim** ("we took the cell"). This round's operative test is a **falsification**: clause 1 of
H-ECQ-a609f8 says the hypothesis is FALSIFIED if the box is empty. A *lower* target makes the box
*more* likely empty, so the stricter gate is **anti-conservative for the test that was actually
run** — it biases toward the Coordinator's own recorded prior P1. It does not matter at 24–40. It
would matter at 0.001, and "it changes no conclusion here" is exactly the sentence the correction
itself argues is not good enough.

*What else was transcribed rather than derived and is still wrong.* Two findings, one of them a
direct instance of the correction's own root cause:

* **The transcribed Nagao quartic is 1557504 = 1248² times the published equation.** Every one of
  the thirteen distinct integer coefficients in `candidate_families.json` is *exactly* divisible by
  1557504 (14017536/S = 9, 330112972800/S = 211950, 6473450277365760000/S = 4156297690000, …). So
  the transcription equals `1557504 · Q₀` for an integral Q₀, and the **published** section
  `((t+703)/15, N(t)/75)` lies on `y² = Q₀` exactly, as published, with no modification.
  Consequently the batch's §1 narrative is wrong in its diagnosis: BATCH-f2341e's "FAILS" was not a
  false negative caused by using the wrong y-coordinate — it was a correct verdict on a quartic
  that is not the published one, and the fix is to divide the equation by 1248², not to multiply
  the point by 1248. Numerically harmless (1248² is a square, so `y ↦ 1248y` is a Q-isomorphism and
  every minimal model, height, rank, conductor and discriminant is identical) — but the record now
  says "the point lies exactly on the transcribed quartic" and "source retrieval remains owed",
  when in fact **the transcription is provably not the published equation**, and that is a stronger
  and more useful statement than the one recorded.
* **"1137 distinct fibres" is 569.** a₄ and a₆ contain **only even powers of t** (a₄: 8,6,4,2,0;
  a₆: 12,10,8,6,4,2,0), so `E_t` and `E_{−t}` are the *same* Weierstrass equation. I verified this
  empirically with zero exceptions: the 1137 union parameters produce exactly **569** distinct
  naive heights and 569 distinct (naive, Faltings) pairs, and every ± pair agrees to 12 decimals.
  The JSON deliverables are careful to say `n_distinct_parameters_measured`, which is right; but
  `cell_reachability.json`'s three `deciding_number` strings and `report.md` both say "over 1137
  distinct **fibres**", and the headline reads "Zero of 1137 distinct measured fibres". The search
  volume is overstated by exactly 2×. This is the same class of error as the 1258 → 1137 fix the
  batch already made and, notably, it is one the corrected run did not catch. It changes no
  conclusion (0 of 569 is still 0) but falsification clause 3 requires a bounded-search negative to
  "be reported with the volume covered", and the volume covered is half what is reported.

### 4.2 `COORDINATOR-multimetric-check.md`

**The table is right; the hypothesis attached to it is not supported, and its convenience for the
Coordinator is the correct thing to be suspicious of.**

*What holds.* I reproduced all three metric columns exactly and added the fourth (C-D). No cell is
taken, on any metric, at any rank threshold, by any of the four certified curves — and none by the
141 221 fibres I measured. Deciding to run a multimetric check at all was right, and disclosing it
to both reviewers (`COORDINATOR-open-items-settled.md`) instead of leaving it ambient was right.

*What does not hold.*

1. **The premise is factually refuted** by the primary source the board itself cites (§1.3). The
   incumbents do not use direct search; the author explicitly rules it out.
2. **The supporting statistic is classifier-dependent** and flips by 127.48 at rank 12 and 37.44 at
   rank 14 (§1.4) — the only two ranks where the claim is drawn.
3. **The two families compared are not comparable evidence.** "NAGAO min naive height in box:
   109.505, flat" is one Weierstrass model, one campaign, 569 distinct fibres. "MESTRE_SPEC min by
   rank" is a hundred-plus curves from many programs over decades. Reading the pair as two
   observations of a method-class dichotomy is a category error, and n = 2 is not a basis for "wrong
   at the root" regardless.
4. **The scope check.** "NO amount of work on the specialisation axis takes those cells" is a claim
   over all families, all parameters, all future work, supported by two families. Under
   `docs/inventor-protocol.md` §4 a closure needs a named obstruction, an argument, and forward
   guidance; the document names an obstruction that turns out not to exist. §3 above supplies one
   that does, and it is *narrower*: it forbids the small-parameter lever from descending, not the
   specialisation axis from succeeding.

*On the convenience.* The document turns a null result into a structural discovery, and it was
written by the party whose target choice the null result reflects on. To the document's credit it
says so itself, at length, and asked to be attacked. Attacked: **the data do not support it as
written.** What the data support is (i) a real but modest program-conditioned signal (p = 0.0031),
(ii) a genuine difference in *what gets parametrised* (§1.3), and (iii) a derivable slope
obstruction (§3) that is narrower than the document's claim and does not need the board's
commentary at all. The negative result stands as a negative result: **NAGAO-1994 was the wrong
family, chosen for the wrong reason ("nobody used it"), and aimed at three cells that were harder
than the one abandoned.** That is a smaller and more useful finding than "the premise is wrong at
the root", and it is the one the evidence carries.

---

## 5. The Coordinator's recorded priors, held to

**P1 — "I expect the box to be EMPTY at all three targets."** *Confirmed, and I treated it as the
first thing to disbelieve.* The instruction is right that a prediction confirmed by its own designer
is weak evidence, so I attacked the measurement design on every axis named:

| design choice | attack | outcome |
| --- | --- | --- |
| box choice | The minimum sits at \|t\| = 62, **on the seam** between the declared box (\|t\| ≤ 60) and the wide probe (den = 1). The region 60 < \|t\| at den > 1 was never measured. | **Ran it (C-B, C-C). 141 221 fibres. Nothing below 109.505165.** The box was, by luck or judgement, placed on the true minimum. |
| height gate | Recompute the gate quantity from a-invariants by an independent path. | **C-A: agrees to 1e-10 on ten fibres.** |
| "distinct fibre" | a₄, a₆ even in t ⇒ E_t = E_{−t}. | **Broken: 1137 parameters are 569 fibres.** Conclusion unaffected; reported volume is 2× overstated. |
| the 1137 union count | 457 + 801 − 121 (integers −60…60) = 1137. | **Arithmetically correct**, and I reproduce 1137 distinct parameter strings exactly. |
| the fit | Is the fitted model right? | **No** — it is a line through a V (§3). The conclusion does not use it; the hypothesis's mechanism does. |
| decay test | Name the parameter that should destroy the signal and check it behaves. | **Passes.** Envelope flattens under 248× more volume. Controlled null, not artifact. |

Net: **P1 survives a much harder test than the one that produced it.** The empty box is real.

**P2 — "I expect minimalisation to strip a lot."** *Holds, and it is the reason the whole thing is
close enough to be worth measuring.* Stripping is 98.7–120.2. I add the missing explanation: the
model before minimalisation is ≈ 231.45 at small t (set by the constant terms, 32 and 48 digits)
and ≈ 128.6 + 24 log\|t\| at large t; the observed minimum at \|t\| = 62 is the crossover of those
two arms, which is *why* the argmin is at moderate rather than small t. The batch reports the
observation ("small t is not optimal here") without the mechanism.

**P3 — "I expect certified rank ≥ 12 at small t."** *Met at t = 62 (rank ≥ 12) and exceeded at
t = 1 (rank ≥ 14).* I did not re-run descent — that is the validator's joint J1 and I am blind to
it — and I record that I am relying on the producer's certificates for rank only, not for height.
One scoping point that belongs on the record regardless of who checks it: the deciding number
109.505165 is the global minimum **over all fibres irrespective of rank**, while the r ≥ 14 cell
requires a rank-14 fibre. Using the unconditional minimum is the conservative choice for concluding
emptiness and is correct here; it would be the *wrong* number for any positive claim.

---

## 6. Pareto / `dominated_by`

The batch makes no performance claim and correctly asserts no cell. For the record, and because an
unchecked `null` is a fabrication under AGENTS rule 5: **NAGAO-1994 as measured is dominated on
every axis of the frozen frontier at every rank threshold it reaches.** Checked exhaustively across
all four metrics (naive height, Faltings height, log conductor, log\|Δ\|) at each curve's own
certified threshold — 16 comparisons, 16 losses, minimum margin +2.57 (t = 1, Faltings, r ≥ 14).
`dominated_by` is not null; it is `{r>=12: #157, r>=13: #158, r>=14: #244, r>=11: #50, r>=6: #56}`
depending on the cell.

The eliminated-dimension check (`KN-LIT-7593`) applies to my own even-in-t finding: the ± symmetry
halves the search space, but computing the symmetry costs nothing (it is visible in the committed
polynomial), so the saving is real — and it is a saving in *cost*, not a step toward a cell.

---

## 7. Narrowest supported statement

> Over 141 221 distinct fibres of the transcribed NAGAO-1994 quartic — spanning integer t up to
> 20 000, all rationals with 30 ≤ t ≤ 140 of denominator ≤ 60, and all rationals with
> 40 ≤ t ≤ 200 of denominator ≤ 12, on a code path independent of the producer's — the minimal-model
> naive height has lower envelope **109.505165**, attained at t = ±62 and nowhere lower, against
> pre-declared targets 69.339 / 75.760 / 85.189. The height law is piecewise
> (h ≈ 119.4 flat for \|t\| ≲ 89, h ≈ 11.3 + 24.14 log\|t\| beyond), with the asymptotic slope equal
> to the 12d = 24 forced by the surface's K3 degree. No cell is taken on any of the board's four
> metrics, including the discriminant metric absent from the frozen baseline. **This scopes a family
> and a lever, not a method class**: the board's own rank-12 and rank-14 construction-class curves
> sit 9.99 and 11.80 from their cells, and the incumbent method that holds all three pre-declared
> cells is, per its cited primary source, an algebraic moduli-space parametrisation scored by a
> Mestre–Nagao product — not the direct search the Coordinator's analysis assumes.

---

## 8. One next concrete action

**Re-aim by measuring the constant, not by arguing about method classes.** Before any further
sieving or any new family is adopted, run the single cheap measurement that decides the A2 axis:
for each candidate family of generic rank ≥ 9 (Mestre's rank-11/12 loci, Fermigier, Kihara,
Kulesz–Stahlke, and Nagao as the now-measured control), compute the **lower envelope of the
minimal-model naive height over the crossover band** — the same C-A/C-C procedure, ~2 seconds and
~10⁵ fibres per family on this machine — and rank families by that envelope rather than by generic
rank. The comparison target is not the board cell but **Mestre 1982's 79.329 at rank 12**: a family
whose envelope beats 79.329 at certified rank ≥ 12 is 9.99 from an actual cell and is worth a
batch; a family that does not is a family-choice failure that this measurement catches in seconds
instead of a batch. Nagao's envelope, 109.505, would have been rejected by this gate before the
batch was dispatched.

---

## 9. `review_attestation`

```yaml
review_attestation:
  task_id: TASK-20260823-eaf799
  role: red-team
  joints_owned: [J3, J4]
  verdicts: {J3: breaks, J4: holds_with_corrections}
  independent_session: true
  requested_policy: review-adversarial
  resolved_model_id: claude-opus-5
  fallback_used: false
  degraded_requirements: []
  read_sibling_reports: false
  snapshot_sha_read: 0cb0165024b3280e83dc7974918d6d82af5039b4
  paths_read:
    - AGENTS.md
    - agents/red-team.md
    - ledger/handoffs/TASK-20260823-eaf799.yaml
    - ledger/hypotheses/H-ECQ-a609f8.yaml
    - ledger/goals/GOAL-ECQ-002/goal.yaml
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-da59ec/review_plan.yaml
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-da59ec/COORDINATOR-multimetric-check.md
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-da59ec/CORRECTION-predeclared-target-values.md
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-da59ec/COORDINATOR-open-items-settled.md
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-da59ec/archives/TASK-20260823-452f5f/receipt.yaml
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-da59ec/tasks/TASK-20260823-f88f54/report.md
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-da59ec/tasks/TASK-20260823-f88f54/cell_reachability.json
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-da59ec/tasks/TASK-20260823-f88f54/nagao_height_budget.json
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-da59ec/tasks/TASK-20260823-f88f54/results/*.json
    - coordination/goals/GOAL-ECQ-002/baseline/frontier_20260823.json
    - coordination/goals/GOAL-ECQ-002/baseline/icarm_database_20260823.json
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-f2341e/tasks/TASK-20260823-d1cb76/candidate_families.json
  external_sources_retrieved:
    - url: https://abel.math.harvard.edu/~elkies/Elkies_JMM23.pdf
      provenance: retrieved
      note: >-
        fetched (HTTP 200, 126560 bytes) and text-extracted from the FlateDecode streams;
        cited by the board commentary of curves #88, #89, #157, #158, #244. Slide table
        matched to board #88/#89 on conductor and a4 exactly.
  paths_NOT_read:
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-da59ec/tasks/TASK-20260823-72505a/**
  compute_performed_by_me: 141221 fibre height evaluations + 200000 permutation replicates
  wrote_only_within_write_scope: true
  committed_anything: false
  changed_hypothesis_or_goal_status: false
```
