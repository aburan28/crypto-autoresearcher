# RT-20260823-123bd6 — Red Team, TASK-20260823-07a54b

**Goal** GOAL-ECQ-002 · **Batch** BATCH-f2341e · **Hypothesis under attack** H-ECQ-d60d07
**Joints owned** 3 (is the r≥15 cell SOFT?) and 4 (is the pre-registration real, and is
the method novel?) · **Snapshot read** `ab0aa5404319796966241478dc44e25592139b44`

**Blindness.** I did not read anything under `TASK-20260823-6040d1` and hold no
knowledge of the Validator's findings. The arithmetic joints are theirs; I attacked
the framing, as instructed.

**Inference provenance.** Requested policy `review-adversarial`
(`independent_session_required: true`, `fallback_allowed: false`,
`degraded_allowed: false`). Answered by `claude-opus-5` at reasoning effort `xhigh`,
which is the binding for `review-adversarial` in `orchestration/model-policies.yaml`
as carried into `.claude/agents/red-team.md`. No fallback, no degraded requirement,
nothing downgraded. `model_verified: false` — no `adapter doctor --probe` ran in this
session, so the identifier is configuration this session did not confirm against a
backend.

---

## Verdicts

| joint | verdict | one line |
|---|---|---|
| **3 — is the r≥15 cell SOFT?** | **BREAKS** | The jump is real and is *not* a submission-count artifact, but it is fully explained by which *search program* contributed at which rank. Conditioned on program, p goes 0.00003 → **0.217**. Within the campaign's own method class, 118.77 is the **global minimum over every rank 12–20**. The cell is the hardest cell on the board for the method the campaign proposes. |
| **4a — pre-registration** | **BREAKS** | C1 as written is satisfiable by typing a curve out of Cremona's tables. I ran the exhaustive control: **three** textbook curves beat the frozen r≥1 naive-height cell, the best being 43a1 at h = 11.2696. C1 also lets the rank threshold, the metric, and the frontier-vs-live-board comparison all be chosen after the search. |
| **4b — is the method novel?** | **BREAKS** | The r≥15 incumbent *is* a rank-12 Mestre Q(T) family specialised at the small integer parameter T = 176. Its own commentary reports 4.21 × 10¹⁰ subsets enumerated in 87 s on 24 threads, and states that the record fibres are **not** top Mestre–Nagao scorers. Expected edge is not near zero; it is negative on family rank, on compute, and on selection criterion. |

Every number below is reproduced by
`analysis/redteam_controls.py` (stdlib only, seed 20260823), which re-verifies the
snapshot's declared `sha256 118db069…cadc59` before it computes anything. It reads
only `coordination/goals/GOAL-ECQ-002/baseline/icarm_database_20260823.json`.

---

## JOINT 3 — the r≥15 cell is not soft. It is a method boundary.

### 3.1 The Coordinator's stated alternative is arithmetically unavailable

The task card offers "an artifact of how few rank-15 curves anyone has submitted".
That specific explanation is dead on arrival, and it should be retired rather than
carried forward as an unresolved worry:

- the r≥15 cell is a minimum over **115** curves; the r≥14 cell over **125**. Ten
  extra draws is not a small-sample regime;
- there are **more** curves of rank exactly 15 (15) than of rank exactly 14 (**10**).

The counting story predicts the opposite of what is observed. It is not the
explanation.

### 3.2 The jump is statistically real

The medians of the rank-13/14/15 groups are 141.8 / 144.3 / 145.3 — flat — so rank
labels are close to exchangeable across those three groups, and a permutation test
needs no trend model. Over 200 000 relabelings (seed 20260823):

| statistic | value |
|---|---|
| P(step at r=15 ≥ 33.58) | **0.0147** |
| P(min of the rank-15 group ≥ 118.77) | **0.0162** |
| P(min of the rank-14 group ≤ 85.19) | **0.624** |

So the Coordinator's related question — *is the r≥15 incumbent unusually LARGE, or is
r≥14's #244 unusually SMALL?* — has a clean answer under this null: **#244 is
entirely unremarkable (p = 0.62); the r≥15 incumbent is the high one (p = 0.016).**

Because r = 15 was chosen *after* looking at the table for the biggest jump, I ran the
look-elsewhere correction rather than quoting the local p. Trend-corrected
(log h = 3.5549 + 0.0974·r on ranks 10–20, i.e. ×1.102 per rank), calibrated min-p
over the ten thresholds 11…20, 30 000 draws: local p < 3.3 × 10⁻⁵, and
**look-elsewhere-corrected p < 3.3 × 10⁻⁵ as well**. The jump survives the
multiplicity correction. It is a real feature of the board.

**That is as far as the Coordinator's justification got, and it is where it should
not have stopped.** "Real" and "an opportunity" are different claims.

### 3.3 The discriminating control: what should destroy this signal?

The parameter that ought to destroy an apparent softness is *conditioning on who
produced the curve*. The board ships that covariate in its own `commentary` field,
and the campaign never read it.

Classifying every curve at ranks 10–20 by the search program its commentary names
gives this incidence table:

```
ELKIES_JMM23       {12: 2, 13: 2, 14: 1}                                   <- stops at 14
KLAGSBRUN          {12: 1, 13: 1, 14: 1, 16: 1, 20: 1}                     <- SKIPS 15
MESTRE_SPEC        {11: 3, 12: 7, 13: 5, 14: 6, 15: 12, 16: 29, 17: 17, 18: 14, 19: 6, 20: 6}
ELKIES_MORDELL     {13: 1, 15: 1, 16: 2, 17: 1}
ELKIES_WATKINS     {10: 8, 11: 5}
HISTORICAL_RECORD  {10: 2, 11: 2, 12: 1, 13: 1, 14: 2, 15: 2, 17: 2, 18: 3, 19: 2, 20: 1}
```

Re-run the identical measurement with the identical trend, permuting height residuals
**within each program only** so that the program × rank incidence is preserved:

| null | p(step at r=15 ≥ observed) |
|---|---|
| unconditional exchangeability | **< 3.3 × 10⁻⁵** |
| conditioned on generative program | **0.2175** |

The signal disappears at the 22nd percentile. The "soft spot" measures which search
programs happened to submit at which ranks, not a property of rank 15.

### 3.4 Which programs, concretely

The frontier restricted to each program:

```
  r      ALL      MESTRE_SPEC     ELKIES_JMM23        KLAGSBRUN
 12    69.34           118.77            69.34            85.30
 13    75.76           118.77            75.76            86.84
 14    85.19           118.77            85.19            90.66
 15   118.77           118.77                -           125.33
 16   125.33           136.79                -           125.33
```

- The r≥12, r≥13 and r≥14 cells — 69.34, 75.76, **85.19** — are all held by curves
  whose commentary reads *"Found by Noam D. Elkies in June 2026, using an improved
  version of the methods described in his JMM 2023 talk"* (ids 157, 158, **244**,
  submitted by Andrew Sutherland). That program contributed **five** curves in this
  rank window and **none at rank ≥ 15**.
- The next tier down at 12/13/14 — 85.30, 86.84, 90.66 — plus 125.33 at rank 16 is a
  four-curve batch attributed to Zev Klagsbrun, submitted **within 73 seconds of each
  other** on 2026-06-24. It covers ranks 12, 13, 14 and **16**, and skips 15. The
  geometric interpolation of its own 14 → 16 entries lands at **≈ 106.6**, comfortably
  below 118.77.

So the 85.19 → 118.77 step is the seam between two search programs that stop at (or
step over) rank 15 and one that does not.

### 3.5 The finding that guts the campaign's justification

Restrict to `MESTRE_SPEC` — Mestre/Fermigier family specialisation, which is
*precisely* the mechanism H-ECQ-d60d07 proposes — and take the minimum naive height at
each **exact** rank:

```
  r=12: n= 7  min = 206.81      r=17: n=17  min = 136.79
  r=13: n= 5  min = 136.69      r=18: n=14  min = 159.97
  r=14: n= 6  min = 134.43      r=19: n= 6  min = 166.83
  r=15: n=12  min = 118.77  <-- r=20: n= 6  min = 200.28
  r=16: n=29  min = 141.59
```

**118.77 at rank 15 is the smallest curve this method has ever produced at any rank on
this board.** The campaign selected, as its "soft" target, the single point at which
its own chosen method has performed best. Read the other way: the r≥14 cell at 85.19 —
where `MESTRE_SPEC`'s best is 134.43 — is 48.6 naive-height units *softer* for our
method than the cell we picked, and we did not notice because we compared cells
instead of comparing methods.

### 3.6 What I am NOT concluding

Per `docs/inventor-protocol.md` and my prohibitions, a bounded finding is not an
impossibility result. Three things remain genuinely open and are the useful residue:

1. **A rank-15 curve below 118.77 very probably exists and is reachable.** The
   Klagsbrun batch's own 14 → 16 interpolation puts it near 106.6. The gap is a
   *submission* gap in someone else's dataset, and it is evidence *for* attainability.
2. The Elkies-JMM23 program reached 85.19 at rank 14 and published its method. Whether
   it extends to 15 is unmeasured and is the highest-value open question here.
3. Nothing above bears on **C2**, the base-rank axis, which is internal, carries the
   research content, and is untouched by any of this.

### 3.7 Two hazards the softness framing hid

- **The margin at r≥15 is the second-thinnest in its rank window.** Incumbent 118.770
  vs runner-up 120.642 — a margin of 1.872 (**1.58 %**), against 4.8 %, 6.4 %, 9.1 %,
  7.1 %, 8.2 %, 3.5 % at r≥13, 14, 16, 17, 19, 20; only r≥18 (0.42 %) is thinner in
  the 13–20 window. Across all 29 thresholds it ranks sixth-thinnest, behind r≥8
  (0.03 %), r≥18 (0.42 %), r≥6 (0.82 %), r≥10 (0.84 %) and r≥29 (1.39 %). A cell
  whose top two entries are 1.6 % apart is a contested cell, not an abandoned one.
- **The cell is moving fast and moved two days before the freeze.** Its history:
  214.16 (2026-05-27) → 131.75 (05-29) → 127.13 (06-11) → 125.33 (06-24) → 120.64
  (06-26) → **118.77 (2026-08-21 08:28Z)**. The pre-registered snapshot was taken
  2026-08-23 00:43Z, i.e. **41 hours after the incumbent landed**. A 10 % improvement
  in 84 days is the ambient rate a multi-batch campaign is racing.

---

## JOINT 4a — the pre-registration is honest but the goalposts are not nailed down

The freeze itself is done right: a frozen file, a declared sha256 that I recomputed
and which **matches**, a stated rationale, and an explicit refusal to re-baseline. The
frontier reproduces exactly from the 289 curves. None of my objections is that the
snapshot was fudged. They are that **C1's success predicate is far weaker than the
campaign's thesis**, in five separable ways.

### 4a.1 The 53a1 incident is a hollow closure, and it is worse than reported

I ran the exhaustive control rather than arguing about it. Over **all** minimal
Weierstrass models with `a1 ∈ {0,1}`, `a2 ∈ {−1,0,1}`, `a3 ∈ {0,1}`, `a4, a6 ∈
[−12,12]` (a range that provably contains every model under the target height, since
`|c4| ≤ 44` forces `|b4| ≤ 2` and `|c6| ≤ 296` forces `|b6| ≤ 3`), keeping those with
naive height below the frozen r≥1 cell 11.613603, and certifying a rational point of
infinite order in exact `Fraction` arithmetic with non-torsion proved against Mazur's
theorem:

| naive height | a-invariants | c4 | c6 | Δ | infinite-order point |
|---|---|---|---|---|---|
| **11.269579** | `[0, 1, 1, 0, 0]` (43a1) | 16 | −280 | −43 | (−1, 0) |
| 11.387464 | `[1, −1, 1, 0, 0]` (53a1) | −15 | −297 | −53 | (0, 0) |
| 11.550443 | `[1, 1, 1, 1, 0]` (83a1) | −47 | 199 | −83 | (0, 0) |
| *11.613603* | *`[0,0,1,−1,0]` (37a1) = the frozen "record"* | 48 | −216 | −37 | — |

**Three** curves in Cremona's tables beat the frozen r≥1 naive-height cell, and the
batch's incidental 53a1 is not even the best of them. Every discriminant is a
squarefree prime, so each model is minimal and the heights are the board's own
quantity — I re-derived the convention independently and it reproduces ids 42, 244 and
276 to 0.0 × 10⁰.

**Verdict: submitting any of these would be a hollow closure and the protocol should
forbid it.** It satisfies C1's letter while saying nothing whatever about
H-ECQ-d60d07, which is a statement about rank ≥ 15 at height < 118.770. A criterion
that a 1980s table entry satisfies is not measuring this program's contribution; it is
measuring the leaderboard's coverage of small conductors. (I did **not** compute
Faltings heights or conductors for 43a1/83a1, so I make no claim about the other two
r≥1 cells. 37a1 plausibly holds the log-conductor cell on its own merits; that is
`recalled`, not checked here.)

**What C1 should say instead.** Replace "at least one record cell" with a conjunction
that cannot be met by a known curve:

> C1′. A curve **first exhibited by this program** — not present in the frozen
> snapshot, not obtainable from Cremona/LMFDB/Dujella tables by lookup, with its
> provenance traced to a specific family, parameter and run id — is accepted by the
> ICARM verifier and takes the **pre-declared target cell (rank threshold ≥ 15,
> metric = naive height)** against **both** the frozen frontier **and** the live board
> re-read at submission time. Taking any *other* cell is recorded as a secondary
> outcome and never as C1 satisfaction.

### 4a.2 Ninety cells, one of which needs to fall

The frozen frontier is 30 rank thresholds × 3 metrics = **90** cells. C1 requires
"at least one". Since a curve of rank r competes in every threshold ≤ r and in all
three metrics, one certified rank-15 curve enters **45** cells at once. The
probability that a large search takes *some* cell is not the probability that the
campaign's thesis is right, and C1 does not distinguish them.

### 4a.3 The rank threshold is not pre-registered — only the frontier is

The goal's AXIS A2 names r≥15; **C1 does not name any threshold.** A curve certified at
rank 12 that beats 69.34 would satisfy C1 while falsifying H-ECQ-d60d07, whose
falsification clause is explicitly about failing to reach rank ≥ 15 under 118.770.
Freezing the *board* without freezing the *cell* leaves the goalpost on wheels. And
§3.5 shows exactly which way it would roll: our method's own deficit is smallest at
ranks 12–14, so a post-hoc threshold choice would drift downward — toward the cells
where a hit says least about the hypothesis.

### 4a.4 The frozen frontier can only get easier

C1's operative test is "relative to the PRE-REGISTERED frontier above". The live-board
re-read is required for *reporting*, not for *satisfaction*. Given §3.7's measured
rate, a curve at, say, 119.5 could satisfy C1 against a stale frontier while being
beaten on the live board. The goal's own rationale ("a cell open here and closed by
someone else before we submit is a real outcome to report") is right; C1's wording
does not implement it.

### 4a.5 One cell is not the campaign

C1 and H-ECQ-d60d07 are not the same claim, and nothing in the goal record says which
governs a headline. This should be written down before a result exists, not after.

---

## JOINT 4b — the incumbents already do exactly this. The answer is yes.

The frozen database ships submitter commentary and it is unambiguous. I read it
rather than inferring from names.

**The r≥15 incumbent itself (id 276, h = 118.770, 2026-08-21):**

> *"Mestre rank-12 quartic family on the integer sextuple {−114,−112,44,55,57,70} at
> **T = 176** … Found by enumerating the Mestre locus 12·p5 = 5·p2·p3 exhaustively over
> the integers rather than parametrizing it … all 59479 primitive centered sextuples
> with |a_i| ≤ 500 come out of **4.21e10 subsets in 87 s on 24 threads**. Each was
> scanned over T = m/n (n ≤ 8, m/n capped per sextuple by exact height), **gating on
> exact naive height or log|D| already under the standing record before any
> Mestre–Nagao scoring: record fibres are downward height fluctuations at fixed
> T-scale, not top Nagao scorers.** … **the gain is exhaustive coverage at this scale,
> not a new family.** … Found with Claude Opus 5 (Anthropic)."*

Line by line against H-ECQ-d60d07:

| H-ECQ-d60d07 says | the incumbent already did |
|---|---|
| "a published elliptic family of generic rank r > 8 over Q(t)" | Mestre rank-**12** quartic family |
| "specialised at SMALL rational parameters" | T = **176**, integer |
| "certified by exact descent" | `ellrank` returns `[15,15,0]` — rank **exactly** 15, not a lower bound |
| "generic rank bought from the base rather than from the sieve is the lever" | *"the gain is exhaustive coverage at this scale, not a new family"* |
| MN as an ordering prefilter | *"record fibres … not top Nagao scorers"* — they gate on **exact height first** |

This is not one submitter. Across ranks 12–20, **106 of 158** curves are Mestre-family
specialisations, and every naive-height cell from r≥15 to r≥20 is held by one:
#276 (T = 176), #235 (T = 162), #86 (T = 1043/2, Fermigier's rank-12 family, staged
Nagao sieve over ~1.9 M specialisations), #159 (T = 2454), #241 (u = −1/2, v = 7/2,
T = 429/2), #240, #275 (T = 10239/176).

**Consequences the Coordinator should take, in the terms the task card asked for.**
The expected edge is not near zero; it is **negative** on every axis I could measure:

1. **Family rank.** They use a rank-12 Mestre family and enumerate its locus
   exhaustively. TASK-20260823-d1cb76 recommends `MESTRE-1991-QT11` (rank ≥ 11), whose
   *"exact coefficients were not computed in this session"*, and whose one transcribed
   competitor (Nagao) **failed** the report's own two-coefficient consistency check.
   We are proposing a weaker family we do not yet possess.
2. **Compute.** 4.21 × 10¹⁰ subsets in 87 s on 24 threads, versus a campaign budget of
   21 600 s total with `max_concurrent: 2` on a 4-core box.
3. **Selection criterion.** They gate on exact naive height *before* MN scoring and say
   in print that this is necessary. Our pipeline orders by MN and measures height
   afterwards — see the next section, where our own control found the same thing.
4. **Adversary class.** The three cells immediately below ours are Elkies'. The
   incumbent one is another LLM-driven agent that landed 41 hours before our freeze.

`dominated_by` for the C1 axis of this campaign, as it stands, is **not** `null` and
must not be recorded as such: it is `{icarm_curve_276 (rank-12 Mestre family at
T=176, exhaustive locus enumeration, 24 threads); icarm_curves_157/158/244 (Elkies
JMM23 program)}`. `sota_delta` on the r≥15 naive-height cell is **0** — nothing has
moved — and on method it is negative as itemised above.

**This does not close the lane.** It relocates it. §3.5's table says our method's
largest deficit-to-frontier is at ranks 12–14, where a *different* program holds the
record — which means the honest questions are "can a Mestre-family search beat 134.43
at rank 14?" (our method's own best there) and "what does the Elkies-JMM23 method do
at rank 15?", neither of which the campaign has asked.

---

## The Mestre–Nagao control: consistent with GOAL-ECQ-001, and under-powered rather than negative

The task card asks whether the executor's `+0.633 mean rank, p = 0.068` is consistent
with GOAL-ECQ-001's `p = 6.1e-8`. **It is, and the apparent conflict is a comparison
error.**

- GOAL-ECQ-001's `6.1e-8` is **top-60 vs bottom-20** (28/29 vs 0/9 reaching rank ≥ 9).
  The contrast comparable to the executor's is **top vs random**: 28/29 vs 16/25.
  I recomputed that Fisher exact: **p = 3.4 × 10⁻³ two-sided**, not 6.1 × 10⁻⁸. The
  five orders of magnitude live in the bottom arm, which BATCH-f2341e never ran.
- **The overlap flaw understates the effect, it does not inflate it.** With 47 points
  in the box and 15 per arm, E[shared] = 15²/47 = **4.79**, i.e. 32 % of the random
  arm is drawn from the ordered arm. Then μ_top − μ_all = (47−15)/47 · (μ_top −
  μ_rest), an attenuation of **0.681**. The disjoint-arm contrast implied by the
  executor's own number is **+0.930** mean certified rank, not +0.633.
- **Power.** p = 0.067 two-sided is |z| = 1.83, so SE ≈ 0.346. At the same effect,
  n = 69 per arm reaches p < 0.05; at the attenuation-corrected effect, **n = 32** does.
  The executor ran 60. This is an under-powered design, not a null result, and
  `H-ECQ-d60d07`'s standing licence for MN as an *ordering* prefilter is not disturbed.

**But the ordering step is still not earning its place in *this* pipeline**, for a
reason that has nothing to do with significance:

- The campaign's target is a **joint** (rank ≥ 15 **and** height < 118.770). MN is a
  marginal **rank** proxy. The executor measured height directly: difference −2.59,
  **p = 0.76**, and *the smallest curve of each family came as often from the random
  arm* (min 15.72 ordered vs **11.39** random).
- The r≥15 incumbent's own commentary reaches the same conclusion independently and
  states it as the reason its search is structured the way it is: *"record fibres are
  downward height fluctuations at fixed T-scale, not top Nagao scorers."*

Two independent measurements — ours and the incumbent's — say MN ordering does not
select for the coordinate this campaign needs. The recommendation is not to drop it
but to **reorder the pipeline**: gate on exact naive height first (it is cheap — the
executor's `falsifier_height.py` measures (a, b) in seconds), then use MN to order
*within* the height-admissible set. That is the incumbent's architecture, arrived at
by our own control.

---

## Cheapest control that falsifies the soft-cell claim — RUN

**Named, run, and reported above:** *permute naive-height residuals within generative
search program, preserving the program × rank incidence, and recompute the r=15 step.*
Cost: ~40 s of stdlib Python on the already-frozen snapshot; no new curves, no descent,
no network. Result: p 0.00003 → **0.2175**. It is cheaper than any mathematical
experiment the campaign has proposed and it should have run before the batch.

The complementary control, also run: exhaustive enumeration of small minimal
Weierstrass models with a certified infinite-order point, which falsifies the r≥1 cell
in ~15 minutes and generalises to any low-rank cell.

---

## Narrowest supported statement

> On the pre-registered ICARM snapshot of 2026-08-23 (sha256 118db069…cadc59, 289
> curves), the step in minimum naive height from the r≥14 cell (85.189) to the r≥15
> cell (118.770) is statistically real under an exchangeability null
> (look-elsewhere-corrected p < 3.3 × 10⁻⁵) and is **not** explained by submission
> counts — the r≥15 cell is a minimum over 115 curves and there are more curves of
> rank exactly 15 (15) than of rank exactly 14 (10). It **is** explained by the search
> programs that produced the curves: conditioning the same permutation on the
> program × rank incidence disclosed in the board's own commentary raises p to 0.2175.
> The r≥14 incumbent (#244) is unremarkable within its rank window (p = 0.62); the
> r≥15 incumbent (#276) is the high one (p = 0.016). Restricted to Mestre-family
> specialisation — the mechanism H-ECQ-d60d07 proposes — 118.770 at rank 15 is the
> minimum over all ranks 12–20, so the cell is that method's best result, not its
> soft target. Separately, three curves in Cremona's tables (43a1 h = 11.2696, 53a1
> 11.3875, 83a1 11.5504), each certified here by an exhibited infinite-order point in
> exact arithmetic, beat the frozen r≥1 naive-height cell of 11.6136, so C1 read
> literally is satisfiable without any new mathematics.
>
> **Scope.** These are statements about one frozen snapshot of one leaderboard and
> about the method attributions its commentary field discloses. They are not
> statements about the difficulty of constructing a rank-15 curve of naive height
> below 118.770, and nothing here shows that such a curve does not exist or cannot be
> found — the Klagsbrun-batch interpolation is positive evidence that it can. The
> program classification is derived from free-text commentary on 250 of 289 curves;
> 39 curves carry none and land in `OTHER`. The permutation nulls assume height
> residuals are exchangeable after a log-linear rank trend, within group or within
> program respectively; that is an approximation calibrated on this dataset alone.

---

## Next concrete action

**Re-aim the C1 axis at rank 14 before spending another batch on rank 15, and rewrite
C1 to C1′ before any curve exists.**

Justification is one row of §3.5: at rank 14 the campaign's own method class
(`MESTRE_SPEC`) stands at 134.43 against a cell at 85.19 — a 48.6-unit deficit held by
a *different* program (Elkies JMM23) — whereas at rank 15 the same method class already
*holds* the cell at 118.77 and the runner-up is 1.6 % away. If Mestre-family
specialisation at small parameters is the lever, rank 14 is where the lever has room
and rank 15 is where it has none. A single measurement decides it, costs minutes, and
needs no new family: take the *existing* Mestre/Fermigier sextuples already named in
the board's commentary (#276's {−114,−112,44,55,57,70}, #235's {0,7,133,136,430,434},
#86's Fermigier {0,55,314,378,1007,1036}), run the batch's own
`falsifier_height.py` to get (a, b) per sextuple, and report the height-admissible
parameter box at the r≥14 target 85.189 next to the box at the r≥15 target 118.770.
If both boxes are empty, C1 is out of reach for this method and the honest deliverable
is the measured (rank, height) frontier plus that statement — which is a real result
and should be recorded as one.

Do not change any hypothesis or goal status on this report. It is one blinded
reviewer's finding on two joints; the Coordinator composes.

---

## Artifacts

- `coordination/goals/GOAL-ECQ-002/batches/BATCH-f2341e/tasks/TASK-20260823-07a54b/redteam_report.md` (this file)
- `coordination/goals/GOAL-ECQ-002/batches/BATCH-f2341e/tasks/TASK-20260823-07a54b/objections.yaml`
- `coordination/goals/GOAL-ECQ-002/batches/BATCH-f2341e/tasks/TASK-20260823-07a54b/analysis/redteam_controls.py`
  — **not named in the handoff's `artifact_paths`.** It reproduces every number above
  and is the only durable record of the controls. The Coordinator must either add it
  to TASK-20260823-d26c06's declared set or accept that the numbers are reproducible
  only from this narrative. Flagged rather than assumed.

## Review attestation

```yaml
review_attestation:
  task_id: TASK-20260823-07a54b
  role: red-team
  joints_owned: [3, 4]
  verdicts: {joint_3: breaks, joint_4a: breaks, joint_4b: breaks}
  independent_session: true
  requested_policy: review-adversarial
  resolved_model_id: claude-opus-5
  reasoning_effort: xhigh
  fallback_used: false
  degraded_requirements: []
  model_verified: false
  model_verified_note: no `adapter doctor --probe` ran in this session
  snapshot_commit_read: ab0aa5404319796966241478dc44e25592139b44
  read_sibling_reports: false
  paths_read:
    - AGENTS.md
    - agents/red-team.md
    - ledger/handoffs/TASK-20260823-07a54b.yaml
    - ledger/goals/GOAL-ECQ-002/goal.yaml
    - ledger/hypotheses/H-ECQ-d60d07.yaml
    - coordination/goals/GOAL-ECQ-002/baseline/frontier_20260823.json
    - coordination/goals/GOAL-ECQ-002/baseline/icarm_database_20260823.json
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-f2341e/archives/TASK-20260823-744c38/receipt.yaml
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-f2341e/tasks/TASK-20260823-01d3d9/report.md
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-f2341e/tasks/TASK-20260823-d1cb76/report.md
    - coordination/goals/GOAL-ECQ-001/batches/BATCH-7e06d3/tasks/TASK-20260822-53748a/red_team_report.md
  paths_deliberately_not_read:
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-f2341e/tasks/TASK-20260823-6040d1/**
  computations_run_independently:
    - frontier reproduction from the 289-curve snapshot (30 thresholds, exact match)
    - naive-height convention re-derivation, ids 42/244/276, agreement 0.0e0
    - permutation nulls (untrended, trend-corrected, look-elsewhere, program-conditioned)
    - exhaustive small-model search with exact non-torsion certification (C6)
    - Fisher exact recomputation of GOAL-ECQ-001's top-vs-random contrast
```
