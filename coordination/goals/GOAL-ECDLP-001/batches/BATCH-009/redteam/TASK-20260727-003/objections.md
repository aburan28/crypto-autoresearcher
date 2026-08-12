# Red-team objections — `BAR-PATHDYN-CONDTAIL-D2`

- **Task:** TASK-20260727-003 (GOAL-ECDLP-001, BATCH-009), authorized by DEC-20260727-002
- **Reviewer role:** red-team, non-originating independent session
- **Snapshot reviewed:** branch `research/ecdlp-solve-20260727`, HEAD `ce09d2f5`
- **Target:** `PATHDYN:BAR-PATHDYN-CONDTAIL-D2`, `research/idea_generation_20260727_claude_candidates.yaml:315-331`;
  narrative copy at `research/idea_generation_20260727_claude.md:278-284`
- **Date:** 2026-07-27

## 0. Preliminaries the reader should hold onto

**Nothing in this document is evidence for or against ECDLP hardness.** It is a paper review of a
written argument. It contains no attack, no improvement, no cost figure, and no claim about any
curve.

**This task ran no measurement.** No experiment, no script, no solver, no sampling. Every number
below is either quoted from a repository file (with path and line) or is elementary arithmetic on a
formula the candidate itself states; each such arithmetic step is labelled and is hand-checkable.
No number here is measured data, and none may be cited as such.

**Independence attestation.** I did not author `research/idea_generation_20260727_claude.md`
(Report 94), `research/idea_generation_20260727_claude_candidates.yaml`, `BAR-PATHDYN-CONDTAIL-D2`,
`BAR-PATHDYN-CHARP-D1`, or `RT-1476-SUBRES-A1`. This is a fresh session. I did not read, open, or
coordinate with the output directory of the concurrent TASK-20260727-002 review.

**Corpus-access limitation, declared up front.** The candidate argues against "the 95-file corpus"
and cites `report85` and `NORMAL-PRS-BETA-BARRIER-D3`. Neither string occurs anywhere in this
snapshot outside Report 94's own two files (checked by recursive grep over the working tree). My
novelty screen is therefore against the 352 markdown files present in `inputs/` and `research/`
here, and I say explicitly where a citation could not be resolved rather than assuming it is wrong.

## 1. What the candidate actually claims

Quoting the mechanism field verbatim (`..._candidates.yaml:322`):

> (P1) At the balanced m=5 sizing L = q^{1/5} already used by the program, the probability that a
> random 5-tuple decomposes tends to 1/5! = 1/120 — a CONSTANT. The corpus already records this
> probability but never draws the consequence. (P2) Under BAR-PATHDYN-CHARP, the unconditional event
> {beta < 3/10} is a large deviation of the degree-drop path: it needs the cumulative drop to exceed
> its mean by Theta(L), so it has probability exp(-Theta(L)) = q^{-Theta(1)}. CONCLUSION, by the
> elementary Bayes bound P(A|S) <= P(A)/P(S): P(beta < 3/10 | success) <= 120 * q^{-Theta(1)}.
> ... Hence the beta < 3/10 gate is closed on the SUCCESSFUL SUBSET too — unless P(success) itself
> decays like a power of q, in which case the index calculus loses on relation YIELD instead. A
> strict either/or, and the first argument in the 95-file corpus that attacks the conditioning
> loophole rather than the aggregate.

Its own recorded status is `unrefuted-not-endorsed` with killer objection "NOT adversarially
refuted. Refutation was capped at the first six candidates per family" (`:330-331`). It is therefore
a proposal, not a result, and this review is the first adversarial pass over it.

## 2. Ranked objections

Severity scale: **CRITICAL** = defeats the barrier's headline claim on its own terms;
**HIGH** = defeats the candidate's operationalization or a load-bearing premise as written;
**MEDIUM** = the claim needs restatement or a control before it can be evaluated;
**LOW** = accuracy/citation defect that must be corrected before any promotion.

---

### O1 — CRITICAL — The novelty claim is false against the very document that defines the gate

Candidate text targeted (`:322`):

> The corpus already records this probability but **never draws the consequence**. ... **the first
> argument in the 95-file corpus that attacks the conditioning loophole rather than the aggregate.**

The consequence is drawn, in the same document that created the successful-subset instruction.
`inputs/idea_generation_20260718_batch2.md:1388-1397` — the red-team pass on candidate A1, which is
`RT-1476-SUBRES-A1` — reads:

> **A1 — cost-negative unless the success-subset exponent is measured.** ... because **early abort
> only helps the non-relation fraction** (`≈` constant), *not* the relation-producing fraction,
> which is exactly where RT-1476's `α<3/2` must hold. Prediction: the exponent `β→3/2` from above.
> **This forces a contract change:** A1 must fit `β` on the **successful-membership subset only**
> (relations found), not the aggregate — otherwise the abort speedup masquerades as a win.

That note contains all three of CONDTAIL's moving parts: (i) the success/failure split is by a
fraction that is `≈ constant`; (ii) therefore the success-subset exponent is not separable from the
aggregate exponent; (iii) therefore the predicted success-subset exponent is `β→3/2`, i.e. the gate
is not reached. CONDTAIL adds a Bayes inequality and a large-deviation vocabulary on top of an
argument already in the corpus, and then claims the underlying fact was "never drawn".

Report 94 itself cites this note twice — at `research/idea_generation_20260727_claude.md:233`
(`PATHDYN-A2` killed as duplicate of "the early-abort statement ... already written down at
idea_generation_20260718_batch2.md:1391"), and again in `PATHDYN-A2`'s reference to "the red-team's
own instruction to charge the successful-membership subset only". So the report reached that exact
line, used it to kill a sibling candidate as a duplicate, and did not apply the same test here.

Report 94's own anti-duplication rule is `research/idea_generation_20260727_claude.md:266`:
"anti-duplication is scored by mechanism, not by family label". Scored by mechanism —
constant success fraction ⇒ success-subset exponent inherits the aggregate exponent ⇒ `β→3/2` —
`BAR-PATHDYN-CONDTAIL-D2` is a **REJECTED-duplicate** of `idea_generation_20260718_batch2.md:1388-1397`
under the report's own standard.

This is not a duplicate of the generic Shoup `1/2` cap (CONDTAIL is about a specific eliminant
degree, not a generic-group lower bound), and not of the family's Bernoulli-path barrier (that is
`BAR-PATHDYN-CHARP-D1`, which CONDTAIL cites rather than repeats). The duplication is specific and
local, and it is with the gate's own contract document.

---

### O2 — CRITICAL — P2 is a three-link chain of unestablished claims, and Report 94 itself rules the middle link inapplicable to this object

Candidate text targeted (`:322`):

> (P2) **Under BAR-PATHDYN-CHARP**, the unconditional event {beta < 3/10} is a large deviation of
> the degree-drop path

P2 is not proved and is not claimed to be proved; it is asserted conditional on
`BAR-PATHDYN-CHARP-D1`. Trace the chain:

1. **Link 1 — CHARP-D1 is itself unreviewed.** `..._candidates.yaml:312-314`: verdict `UNREFUTED`,
   killer objection "NOT adversarially refuted. Refutation was capped at the first six candidates
   per family", status `unrefuted-not-endorsed`. A barrier conditional on a barrier nobody has
   attacked is conditional, and the conditionality must be carried in every downstream statement.
   CONDTAIL's mechanism, prediction, and `dominant_exponent` fields all state the conclusion
   unconditionally ("pins alpha >= 3/2", "the beta < 3/10 gate is closed").

2. **Link 2 — CHARP-D1's literature basis is self-flagged as unverified.** Report 94's own family
   verdict (`..._candidates.yaml:34`): "One literature-claim flag: the i.i.d.-geometric
   partial-quotient law for F_q((1/X)) (Artin's function-field continued fractions) was **NOT
   verified against a primary source in this session** — it must be checked before any ledger
   promotion, and no theorem number should be cited on my say-so."

3. **Link 3 — Report 94 rules that this law does not transfer to the object CONDTAIL applies it
   to.** The killer objection that kills `PATHDYN-A1` (`..._candidates.yaml:217`):

   > the closed-form derivation establishes the geometric law for **Haar-random univariate Laurent
   > series - a DIFFERENT object from the conditioned multivariate Semaev PRS the barrier is about**
   > - so promoting it would upgrade a named open lever into a theorem it has not earned.

   CONDTAIL's P2 applies the geometric law to the degree-drop path of the serial-S3 backward-3-sum
   Semaev PRS — the "conditioned multivariate Semaev PRS" — which is exactly the transfer the same
   report declares invalid one page earlier.

4. **Corroboration inside the same family.** `PATHDYN-C1` exists precisely to ask whether Semaev
   structure makes the path non-Bernoulli (`..._candidates.yaml:272-273`), and its killer objection
   (`:281`) says: "**proving the induced path measure Bernoulli IS the open question**." P2 assumes
   the answer to a proposition the same report labels open.

Per `agents/red-team.md` I do not reject a claim merely for being conditional on a stated heuristic.
The objection here is stronger than conditionality: the conditioning barrier is (a) unreviewed,
(b) resting on an unverified literature claim, and (c) applied to an object the same report
adjudicates it does not cover. Any restatement of CONDTAIL must carry all three qualifications in
its headline, not only in a footnote.

---

### O3 — CRITICAL — The "strict either/or" is refuted by RT-1476's own recorded optimization

Candidate text targeted (`:322`):

> unless P(success) itself decays like a power of q, **in which case the index calculus loses on
> relation YIELD instead. A strict either/or**

RT-1476 as recorded in `inputs/main_research_ledger.md:2497`:

> Restricted m-ary model: `L=q^ell`, support probability `min(1,L^m/q)`, query `L^alpha`,
> `Theta(L)` rows, sparse linear algebra `L^2`, same backend for descent. | **Exact optimization
> gives `ell=1/(m+1-alpha)`, total `2/(m+1-alpha)` for `alpha<=1`; above linear cost the optimum is
> `ell=1/m`, total `(1+alpha)/m`.** Thus m<=3 has no nonnegative sub-rho alpha, m4 requires
> `alpha<1`, and m5 requires `alpha<3/2`.

The theorem has two branches:

- **Branch A (`alpha <= 1`):** the optimum is `ell = 1/(m+1-alpha) < 1/m`, hence
  `L^m/q = q^{m·ell - 1} < 1` — the support probability **decays as a power of q by construction** —
  and the total exponent is `2/(m+1-alpha)`, which at `m=5, alpha=1` equals `2/5 < 1/2`, i.e.
  **sub-rho**.
- **Branch B (`alpha > 1`):** the optimum is `ell = 1/m`, support probability `min(1, 1) = 1`, total
  `(1+alpha)/m`, sub-rho iff `alpha < 3/2`.

CONDTAIL's either/or asserts that a power-law-decaying `P(success)` means "the index calculus loses
on relation YIELD". Branch A is a counterexample **inside the theorem the gate belongs to**:
decaying support probability is not a loss there, it is the optimum, and it is sub-rho. The
candidate's dichotomy is an artifact of evaluating only Branch B.

Consequence for the barrier's reach: P1's constancy is a property of the operating point `ell=1/m`,
which is optimal only when `alpha > 1`. So even granting every premise, the barrier can close at
most the window `alpha ∈ (1, 3/2)`. The gate as written in `inputs/main_research_ledger.md:9` is
`alpha < 3/2` with no lower bound, and the whole of `alpha <= 1` — the strictly better regime, and
the one a successful backend would move into — is outside the barrier's reach and outside its own
declared scope (`cost_accounting`, `:327`: "scoped to the m=5 backward-3-sum serial-S3 route at
L = q^{1/5}; other arities or sizings need their own P(success) measurement"). The candidate states
the scope restriction and then states a conclusion broader than it.

---

### O4 — HIGH — The candidate's own minimal test measures `deg ≤ 1`, not the gate

Candidate text targeted (`minimal_test`, `:325`):

> (b) the final eliminant degree, giving **beta_hat = log(deg)/log(L)** with the normalization
> stated explicitly in the frozen contract

and (`falsification`, `:326`):

> OR the unconditional **{beta_hat < 0.30}** event is observed at a p-stable, non-vanishing rate

The threshold `0.30` and the statistic `log(deg)/log(L)` live on different scales. The corpus fixes
the conversion in three places:

- `inputs/idea_generation_20260718_batch2.md:1292` (frozen contract hypothesis): "degree
  `Theta(q^beta)` in the shared Kummer coordinate u with `beta < 0.3`" — `beta` is normalized by
  `log q`.
- `inputs/idea_generation_20260718_batch2.md:1303` (frozen contract metrics): "fitted
  `beta = d log(ops_success)/d log(q)`" — again `log q`.
- Report 94 itself, `research/idea_generation_20260727_claude.md:546` and `:596`:
  "the gate is `alpha < 3/2` (equivalently `beta < 3/10`)" and "`alpha = 5*beta`".

So `alpha = log_L(query cost)` and `beta = log_q(·)`, with `alpha = 5 beta`. `log(deg)/log(L)` is on
the **alpha** scale; the threshold that belongs to it is `3/2`, not `0.30`. Comparing it to `0.30`
tests an event five times stricter in the exponent than the gate.

At the candidate's own sizes this is not a mild slippage; it degenerates. The minimal test specifies
`p in {101,211,431,809,1601,3001,10007}` and `L = ceil(p^{1/5})`. Exact integer arithmetic
(`2^5=32`, `3^5=243`, `4^5=1024`, `5^5=3125`, `6^5=7776`, `7^5=16807`):

| p | 101 | 211 | 431 | 809 | 1601 | 3001 | 10007 |
|---|---|---|---|---|---|---|---|
| `L = ceil(p^{1/5})` | 3 | 3 | 4 | 4 | 5 | 5 | 7 |

The tested event `log(deg)/log(L) < 0.30` is equivalent to `deg^{10} < L^3`. With `L ≤ 7` we have
`L^3 ≤ 343 < 1024 = 2^{10}`, so `deg ≥ 2` is impossible: **the event the candidate proposes to
observe is `deg ∈ {0,1}` — the eliminant being constant or linear — at every prime in its own
sweep.** That is a degeneracy event, not the RT-1476 gate, under any reading of the normalization.
(This is arithmetic on the candidate's stated parameters, not a measurement.)

Second defect in the same field: the frozen contract's `beta` is a **field-op count** exponent
(`d log(ops_success)/d log(q)`, `:1303`), not an eliminant-degree exponent. The candidate measures
degree. The contract's own "Expected failure modes" (`:1316`) name "coefficient blow-up dominating
even if degree small", i.e. the corpus already records that degree does not determine ops. A degree
measurement cannot certify the gate quantity. The transfer the barrier needs runs in the safe
direction (`ops ≥ deg` would give `deg ≥ q^{0.3} ⇒ beta_ops ≥ 0.3`), but the candidate never states
that inequality, and without it P2 (about degrees) does not reach the gate (about ops).

---

### O5 — HIGH — P1 names the wrong event, and misreports what the corpus records

Candidate text targeted (`:322`):

> the probability that **a random 5-tuple decomposes** tends to 1/5! = 1/120

Three problems.

**(a) A random 5-tuple of factor-base elements always "decomposes".** It *is* a decomposition of its
own sum. The standard `1/m!` heuristic is a statement about a random *point*: with `|F| = L` and
`L = q^{1/m}`, the expected number of unordered `m`-subsets of `F` summing to a given point is
`L^m/(m! q) = 1/m!`. The candidate has swapped the roles of the point and the tuple. That matters
because the event actually being conditioned on in this route is neither: per the contract's
algorithmic path (`inputs/idea_generation_20260718_batch2.md:154-156`), relation generation is
"forward table of `S3(x1,x2,u)` roots `u` for all `(x1,x2)` pairs; backward PRS test each
`(x3,x4,x5)` for a shared `u`", and the candidate's own success label (`:325`) is "the eliminant has
an F_p root yielding a valid decomposition certificate". Those are three different events with three
different probabilities, and the barrier uses one number for all of them.

**(b) The corpus records a different formula.** The candidate says "The corpus already records this
probability". What the corpus records is `min(1, L^m/q)` — `inputs/main_research_ledger.md:2497`
(RT-1476's model: "support probability `min(1,L^m/q)`") and `inputs/idea_generation_20260718_batch2.md:158`
("Relation probability: `min(1, L^5/q)` per 5-tuple (unchanged from RT-1476 model)"). At the
operating point `ell = 1/5` that expression equals **1**, not `1/120`: the `m!` is absorbed as an
`O(1)` factor and does not appear. So P1's "load-bearing and previously undrawn fact" — the
`fingerprint` field (`:323`) calls it "the CONSTANCY of P(success) at balanced m=5 sizing — the
load-bearing and previously undrawn fact" — is the constancy that RT-1476's own model row asserts
by writing `min(1, L^m/q)` and then optimizing `ell`. It is neither undrawn nor new; and under the
corpus's literal formula the conditioning event has probability 1, which would make the entire
barrier vacuous rather than sharp.

**(c) `P(success)` is not degree-free.** On the route as contracted, a query succeeds when the
backward eliminant in `u` shares a root with the forward table. The number of candidate roots is at
most the eliminant degree; the forward table occupies `O(L^2)` of the `q` possible `u` values. Under
any uniform-hit model, `P(success | deg = d) ≲ d·L^2/q`, i.e. success probability is *increasing* in
the eliminant degree. `P(success)` is therefore a marginal over a quantity coupled to the very
statistic being conditioned, not an independent constant. I flag the direction honestly: this
coupling biases the successful subset toward *larger* degrees, which favours the barrier's
conclusion. But it destroys the barrier's premise *structure* — P1 and P2 are not separable, the
either/or of O3 is not a dichotomy over independent axes, and the correct figure of merit is
cost-per-relation `= (query cost)/P(success)`, which is exactly the composite RT-1476's two-branch
optimization already handles. A barrier that treats a coupled pair as separable is not citable as
written even when its conclusion points the right way.

---

### O6 — HIGH — The large-deviation apparatus is asserted, and its stated rate contradicts its stated conclusion

Candidate text targeted (`:322`):

> it needs the cumulative drop to exceed its mean by **Theta(L)**, so it has probability
> **exp(-Theta(L)) = q^{-Theta(1)}**

**(a) The equation is false as written.** With `L = q^{1/5}`, `exp(-Theta(L)) = exp(-Theta(q^{1/5}))`,
which is superpolynomially small in `q`; `q^{-Theta(1)} = exp(-Theta(log q))`. These are not equal
and not of the same order. The error is conservative for the conclusion (the smaller quantity still
gives `120 · exp(-Theta(L)) → 0`), so it does not by itself flip the verdict — but it shows the rate
was not derived. The candidate does not know which of the two rates it is asserting, and the
difference is exactly what its own falsification test would have to resolve.

**(b) The deviation scale `Theta(L)` is unjustified.** The relevant scale for "the cumulative drop
exceeds its mean" is set by the *degree* of the object being reduced, not by the factor-base size.
If the adverse prior is the generic Bezout degree `Θ(q)` (`inputs/idea_generation_20260718_batch2.md:182`:
"The backward 3-sum eliminant in `u` almost certainly has degree `Θ(q)`"), then reaching `q^{3/10}`
requires a deficit of order `q`, not of order `L = q^{1/5}`. Under the candidate's own i.i.d.
geometric model that would be `exp(-Θ(q))`. The candidate supplies no rate function, no Legendre
transform, and no statement of the path length; `PATHDYN-B2` in the same family does write the rate
function down (`:258`, `I(beta) = Legendre transform of log lambda(s)`), which makes the omission
here a choice rather than an oversight.

**(c) A large-deviation claim requires hypotheses the candidate never checks.** A rate function of
the form `exp(-n I(x))` needs independence, stationarity, or a mixing/Gärtner-Ellis condition on the
increments. That is precisely what `PATHDYN-C1` asks about and what its killer objection calls "the
open question" (`:281`). P2 assumes the hypothesis it needs.

**(d) The claim is untestable at the specified sizes.** From O4's table, `L` ranges over
`{3,3,4,4,5,5,7}` across the entire sweep. No functional form in `L` — `exp(-cL)`, `exp(-cq)`,
`q^{-c}`, or a constant — is distinguishable over `L ∈ [3,7]`. A large-deviation rate claim whose
only proposed test lives on a three-to-seven range is not falsifiable by that test.

---

### O7 — MEDIUM — The Bayes step is valid, and it does not test the barrier; the candidate's own test can only test its premises

Candidate text targeted (`:322`):

> CONCLUSION, by the elementary Bayes bound P(A|S) <= P(A)/P(S)

**I grant this.** `P(A|S) = P(A∩S)/P(S) ≤ P(A)/P(S)` holds for any events, with no independence
assumption. The bound is valid even though `A` and `S` are strongly dependent by construction (O5c).
And the direction the gate needs works: if `A` is a per-sample event and `1-o(1)` of successful
samples fall outside `A`, then a mean or quantile estimator on the successful subset inherits the
lower bound. That part of the argument is correct and I could not break it.

Three qualifications, all of which the candidate must carry:

1. **`A` must be a per-sample event.** The frozen contract's `beta` is a cross-size fitted slope
   (`d log(ops_success)/d log(q)`, `:1303`), not a per-sample random variable. The candidate makes
   `beta` per-sample only by silently redefining it as `log(deg)/log(L)` in its `minimal_test`
   (O4). The redefinition is what makes the Bayes step applicable, and it is unannounced.

2. **The estimator must be one the bound controls.** A quantile or a mean of a nonnegative statistic
   is controlled from below; a min, a best-case, an early-abort-optimized selector, or a
   trend-in-`q` statistic is not automatically. The contract's `beta` is a slope of an aggregate,
   and no argument is given that a fixed-threshold per-sample tail bound at each `q` controls a
   slope across `q`. It plausibly does under a uniform-in-`q` version of P2; the candidate does not
   state the uniformity it needs.

3. **The candidate's own minimal test cannot test the conclusion.** Its `minimal_test` (`:325`)
   concedes this: "the theorem's bound cannot be violated by Bayes while P(success) stays constant".
   Correct — and it means the proposed experiment can only measure P1 (is `P(success)` constant?)
   and P2 (is the low-`beta` event rare?), never the inference. Since the inference is the only part
   that is sound, the experiment is aimed exclusively at the two parts that are not established.
   That is the right target, but the candidate should not describe the design as testing "the
   barrier".

---

### O8 — MEDIUM — The proposed instrument has no sampling randomness at six of seven sizes, and cannot support an asymptotic claim at any of them

Candidate text targeted (`:325`):

> `N = 10^4 random 5-tuples per prime; seeds 20260727..20260731` ... `NEGATIVE CONTROL: shuffled
> success labels, which must destroy any apparent conditioning effect.`

With `L = ceil(p^{1/5})` from O4, the population of ordered 5-tuples of factor-base x-coordinates is
`L^5 ∈ {243, 243, 1024, 1024, 3125, 3125, 16807}`. Drawing `N = 10^4` "random 5-tuples" exceeds the
entire population at six of the seven primes (by a factor of ~41 at `p = 101`). At those sizes the
draw is an exhaustive enumeration with multiplicity, the five seeds see the same population, and the
seed-to-seed error model the design inherits from `PATHDYN-A1`/`B1` (`:212`, `:244`, the "400-resample
control envelope") has essentially nothing to resample. Error bars computed that way would be
meaningless, and the shuffled-label negative control degenerates too.

Separately: `p ≤ 10007` is 14 bits. Per `docs/claims-and-verification.md:70-85` that is `toy` tier,
which "may NOT assert ... anything about medium or cryptographic curves", and per AGENTS.md rule 7
toy-curve evidence must never be presented as crypto-scale validation. The barrier's claim is an
**asymptotic statement in `q`** (`tends to`, `Theta(L)`, `q^{-Theta(1)}`). No toy-tier measurement
can establish it. The most such a run can produce is a `toy`-tier, `empirical_only` observation
about seven small primes.

---

### O9 — MEDIUM — P1's own falsification clause is predicted to fire, for a discretization reason

Candidate text targeted (`prediction`, `:324` and `falsification`, `:326`):

> Measured P_hat(success) is p-stable near 1/120 with no power-law decay:
> **|d log P_hat(success) / d log p| < 0.02** across the size sweep.

> EITHER P_hat(success) **decays as a power of p with exponent > 0.02** — this breaks premise P1

Take the candidate's own finite-size model, `P(success) ≈ L^5/(5! q)` with `L = ceil(p^{1/5})`. The
ceiling makes `L^5/q` sawtooth. Exact fractions (arithmetic on the candidate's stated model; not a
measurement):

| p | 101 | 211 | 431 | 809 | 1601 | 3001 | 10007 |
|---|---|---|---|---|---|---|---|
| `L^5/q` | 243/101 | 243/211 | 1024/431 | 1024/809 | 3125/1601 | 3125/3001 | 16807/10007 |
| ≈ | 2.41 | 1.15 | 2.38 | 1.27 | 1.95 | 1.04 | 1.68 |

The ratio is non-monotone and spans a factor greater than 2.28 (`(243/101)/(3125/3001)`), driven
entirely by where each prime falls relative to a fifth power. The two-endpoint log-slope alone,
`ln(1.68/2.41)/ln(10007/101)`, is approximately `-0.078` — about four times the candidate's own
`0.02` tolerance — and the sign and size of any fitted slope depend on which side of the ceiling the
endpoints land on, not on mathematics.

So the candidate's own P1 test, applied to the candidate's own model at the candidate's own sizes,
is predicted to trigger the candidate's own falsification clause for premise P1, artifactually.
Meanwhile, under the *corpus's* formula `min(1, L^5/q)` (O5b) every entry in the table exceeds 1, so
`P(success) = 1` exactly at all seven sizes, the slope is 0, and the conditioning is vacuous. The
two available models give opposite artifacts and neither gives "p-stable near 1/120". The design
cannot decide P1 as specified.

---

### O10 — LOW/MEDIUM — Scope inflation from a stage-2 bound to an end-to-end verdict and a status recommendation

Candidate text targeted (`cost_accounting`, `:327`, versus `fingerprint`/`prediction`, `:323`/`:324`):

> A barrier: NO stages charged, all seven OMITTED. What it BOUNDS is **stage (2) relation collection
> only** ... and **must not be quoted as if it did** [bound the others].

versus, in the same record:

> dominant cost exponent: pins alpha >= 3/2, hence m=5 IC >= q^{1/2}, **hence no rho crossing on
> this route.**

> the standing conservative winner **should be re-classified from OPEN GATE to
> CLOSED-pending-verification.**

The `cost_accounting` field is exemplary and the `fingerprint`/`prediction` fields immediately
violate it. "No rho crossing on this route" is an end-to-end claim built from a stage-2 bound.
Additionally, `research_goals_20260723.md:90` (G30-001) states that any claimed sub-rho attack "is
only meaningful against a fully charged comparator" and G30-001's own header (`:5`) states "All cost
comparisons are void until G30-001's GOE cost ruler exists" — so the `>= q^{1/2}` / `0.886*sqrt(n)`
comparison in `dominant_exponent` is a figure the program's own governance says cannot yet be
stated. Finally, recommending a record's status re-classification is a Coordinator action under
AGENTS.md rule 12; a candidate record may name the evidence it would take, not the transition.

---

### O11 — LOW — Two load-bearing citations are unresolvable in this snapshot, and one attribution appears incorrect

Candidate text targeted (`:322`):

> Report85's A1 (RT-1476-SUBRES-A1) ... is kept alive by exactly ONE argument, **quoted from its
> 'Why not already killed' line**: it measures the SUCCESSFUL-membership subset rather than the
> generic worst-case eliminant **that the first-fall barrier bounds**.

- `report85` occurs nowhere in this snapshot outside Report 94's own two files. I cannot verify the
  quotation or that the "exactly ONE argument" characterization is faithful.
- `NORMAL-PRS-BETA-BARRIER-D3`, which Report 94 uses to kill `PATHDYN-A1` as a duplicate "in two
  corpus files" (`:217`), likewise occurs nowhere in this snapshot outside Report 94's own two files.
- The section actually titled "Why existing negatives do not already kill it" for A1
  (`inputs/idea_generation_20260718_batch2.md:174-179`) says something different from the
  paraphrase: the surviving argument there is that A1 does **not form the composed resultant** and
  that "subresultant PRS with early-abort reads off the degree of the *smallest* nonzero
  subresultant, which can be far below the product degree". The successful-subset instruction comes
  from a *different* place — the red-team note at `:1388-1397` (O1). So "exactly ONE argument" is
  itself inaccurate against this snapshot: there are two recorded arguments, and the barrier attacks
  only one of them.
- No barrier bounding the RT-1476 backward-3-sum eliminant by a *first-fall degree* is recorded in
  this snapshot. The recorded adverse prior is the batch-2 red-team's PRS-cost argument
  ("PRS on a degree-`q` object is `Ω(q^{3/2})` field ops", `:1390-1391`), which is a cost argument,
  not a first-fall-degree theorem. The attribution should be corrected before any promotion.

---

## 3. Baseline comparison

The candidate is a negative claim, so the honest baseline framing is what it would and would not
move.

| baseline | status under the candidate | assessment |
|---|---|---|
| **Pollard rho** (`0.886·sqrt(n)` group ops, single target) | candidate asserts it is "undisplaced" (`dominant_exponent`, `:328`) | Correct as a statement of the status quo, and unmoved either way: a surviving barrier would leave rho where it is, and a broken barrier is not an improvement over rho. Per G30-001 no "× rho" figure is admissible in this program before the GOE cost ruler exists, so the `>= q^{1/2}` comparison should not be quoted as a cost figure at all. |
| **BSGS** (`q^{1/2}` time and `q^{1/2}` memory) | not mentioned by the candidate | Not engaged. Note that RT-1476's model already charges memory implicitly through `Theta(L)` rows and `L^2` linear algebra; the barrier charges nothing (`:327`) and therefore says nothing about the time/memory trade-off that separates BSGS from rho. |
| **Closest specialized baseline: Gaudry–Diem summation-polynomial index calculus over prime fields** | implicitly the object being bounded | For prime fields no sub-rho index calculus is known; the candidate's conclusion is the field's status quo. So even a fully surviving barrier moves no baseline — it removes a hypothesis, which is legitimate but must not be reported as progress against any baseline. |
| **The candidate's own route (`RT-1476-SUBRES-A1` / serial-S3 backward 3-sum)** | claimed pinned at `alpha >= 3/2` | Not established (O2, O3, O6). Also note the route's descent stage is inherited and, in this family's siblings, explicitly "unchanged and UNRESOLVED" (`:258`, `:274`); RT-1476's model assumes "same backend for descent". Neither the barrier nor the gate settles descent. |

**End-to-end check (red-team.md item 3).** The barrier charges no stage and omits relation
collection cost, rank, memory, source recovery, target descent, and scalar orientation by explicit
declaration (`:327`). That is the correct posture for a barrier. It means, though, that the barrier
cannot bear on the end-to-end path, and its "no rho crossing on this route" phrasing (O10) must be
struck.

## 4. Required controls before any of this becomes evidence

These are specifications, **not run**, and nothing below was executed.

1. **C1 — normalization control (zero compute).** Any future measurement must report the statistic
   on both scales explicitly: `beta_q = log(·)/log(q)` against threshold `3/10` and
   `alpha = log(·)/log(L)` against threshold `3/2`, with `alpha = 5·beta_q` verified numerically per
   sample. This is the control that would have caught O4.
2. **C2 — quantity control (zero compute).** Report both the eliminant degree and the field-op count
   on the success subset, since the frozen contract's gate is on ops (`:1303`) and the contract's own
   failure mode list names "coefficient blow-up dominating even if degree small" (`:1316`).
3. **C3 — coupling control.** Report `P̂(success | deg = d)` as a function of `d`, not only the
   marginal `P̂(success)`. If it is monotone in `d`, P1's "constant" is a marginal over a coupled
   pair and the either/or of O3 is void.
4. **C4 — population control.** Choose `N ≪ L^5` so that the draw is a sample. At the candidate's
   sizes this is impossible; it forces larger `L` (see the check in §6).
5. **C5 — discretization control.** Either choose primes with `p` close to `L^5` for a fixed ladder
   of `L`, or report `P̂(success)·q/L^5` rather than `P̂(success)`, so the ceiling sawtooth of O9 is
   divided out before any slope is fitted.
6. **C6 — instrument controls already specified by the candidate, retained.** Planted low-`beta`
   subpopulation as positive control; shuffled success labels as negative control (`:325`). Both are
   good and should be kept, with the caveat from O8 that at `N > L^5` the shuffle control is weak.
7. **C7 — literature control (zero compute).** Verify the i.i.d.-geometric partial-quotient law for
   `F_q((1/X))` against a primary source before any downstream use, as Report 94's own family
   verdict demands (`:34`). No theorem number may be cited without it.

## 5. Strongest form I could not break, and strongest form I broke

**Could not break (grant this, and only this):**

> Let `S` be the membership-success event and suppose `P(S) ≥ c > 0` with `c` independent of `q`.
> Let `A` be any per-sample event. Then `P(A | S) ≤ P(A)/c`. Consequently, an argument of the form
> "the estimator is computed on the successful subset rather than on the aggregate" cannot, **by
> itself and with no further input**, convert an unconditionally `exp(-ω(log q))`-rare per-sample
> event into a typical one; and a success-subset estimator that is a quantile or a mean of a
> nonnegative statistic inherits the unconditional lower tail up to the factor `1/c`.

This is elementary, correct, and I could not break it. It is also weak: it is an implication whose
antecedent (`P(A)` exponentially small unconditionally) is exactly the disputed proposition. If we
already knew the unconditional low-`beta` event were that rare, the aggregate gate would already be
settled and the conditional statement would be a corollary. The statement therefore transfers no
information from the known to the unknown; it only says which *kind* of argument the successful-subset
appeal is not.

**Broke:** the candidate's headline — "the beta < 3/10 gate is closed on the SUCCESSFUL SUBSET too",
"pins alpha >= 3/2", and "should be re-classified from OPEN GATE to CLOSED-pending-verification".
Broken on four independent grounds, none of which is "it is conditional":

- O1 — the load-bearing fact and its consequence are already in `idea_generation_20260718_batch2.md:1388-1397`,
  which is the gate's own contract document; scored by mechanism per Report 94's own rule, it is a
  duplicate.
- O3 — the "strict either/or" is contradicted by RT-1476's recorded two-branch optimization
  (`main_research_ledger.md:2497`), which makes decaying support probability the sub-rho optimum in
  the `alpha ≤ 1` branch.
- O4 — the operationalization tests `deg ≤ 1` at every prime in its own sweep and measures degree
  where the contract's gate is on field-ops.
- O6 — the stated rate `exp(-Theta(L)) = q^{-Theta(1)}` is internally inconsistent and the deviation
  scale `Theta(L)` is asserted rather than derived.

**What remains standing after the break:** (i) the boxed statement above; (ii) the observation, which
is genuinely useful even though not new, that the successful-subset appeal has a bounded-reweighting
structure whenever `P(success)` is `Θ(1)`, so the appeal cannot on its own be worth more than an
`O(1)` factor — but only in the `alpha ∈ (1, 3/2)` window where `ell = 1/m` is the optimum; (iii) the
correct and well-written `cost_accounting` scope disclaimer at `:327`, which the candidate's own
headline then violates.

## 6. Cheapest decisive check (specified as a contract, NOT run)

Two checks, in cost order. **Neither was run. No number below is a measurement.**

### CHECK-A (zero compute, decides O3 and O5c)

A derivation note answering: *on the serial-S3 backward-3-sum route as contracted, is the membership
success event statistically independent of the backward-eliminant degree?* Inputs are already in the
repository (`inputs/idea_generation_20260718_batch2.md:152-165`, `inputs/main_research_ledger.md:2497`).
Deliverable: a one-page argument computing `P(success | deg = d)` under the route's own model and
stating whether it is constant in `d`. **Falsification condition:** if `P(success | deg = d)` is
non-constant in `d`, premise P1 is a marginal over a coupled pair, the strict either/or is void, and
the barrier must be restated as a joint statement about `(deg, success)`. This costs no compute and
should precede any measurement.

### CHECK-B (the measurement, if CHECK-A leaves the barrier standing)

- **Question decided:** is the success-conditioned low-`beta` mass a bounded reweighting of the
  unconditional low-`beta` mass, on the contract's own quantity and scale?
- **Sizes:** `L ∈ {16, 20, 24, 32}` with `p` the least prime `> L^5` for each (so `p` ranges roughly
  `10^6`–`3.4·10^7`, still ≤ 32 bits and therefore still `toy` tier). Rationale: `L ≥ 16` is the
  minimum at which a rate in `L` is nominally estimable (O6d) and at which `N ≪ L^5` is achievable
  (O8). Curves per the frozen contract's family: ordinary prime-order `E/F_p`, `j ∉ {0,1728}`,
  non-anomalous.
- **Sampling:** `N = 10^4` per size with `N/L^5 < 10^{-2}` at every size; 5 seeds; seed list recorded
  in the frozen contract before execution.
- **Primary statistics, both reported per sample:** `beta_q = log(deg)/log(q)` and
  `alpha = log(deg)/log(L)`, plus the field-op count `ops` and `beta_ops = log(ops)/log(q)`.
  Thresholds reported against `beta < 3/10` and `alpha < 3/2` simultaneously (control C1).
- **Discriminating quantity:** `R(t) = P̂(beta_q < t | S) / P̂(beta_q < t)` for `t` on a grid, plotted
  against the Bayes ceiling `1/P̂(S)`; plus `P̂(success | deg = d)` as a function of `d` (control C3);
  plus `P̂(success)·q/L^5` (control C5).
- **Controls:** positive — planted subpopulation with `beta_q = 0.2` at 5% of successes, which the
  instrument must recover; negative — shuffled success labels, which must drive `R(t) → 1`; second
  negative — random-polynomial arm matched in degree profile, as in `PATHDYN-C1`'s ARM R.
- **Falsification condition for the barrier:** the barrier's premise P2 fails if the unconditional
  `{beta_q < 3/10}` event is observed at a rate that is stable or growing across the four sizes.
  Its premise P1 fails if `P̂(success)·q/L^5` (not raw `P̂(success)`) has a fitted `d log/d log p`
  slope outside `±0.02` with the discretization divided out. The barrier's *inference* is not
  testable by this or any experiment (O7.3) and must not be reported as tested.
- **Explicitly out of scope:** this contract decides nothing about `alpha ≤ 1`, about arities other
  than `m = 5`, about sizings other than `ell = 1/5`, about descent, linear algebra, memory, or
  multi-target amortization, and nothing at medium or cryptographic scale.
- **Budget note:** this is strictly more expensive than the candidate's own minimal test. If budget
  forbids it, the correct action is to run nothing and record the barrier as demoted on the paper
  grounds above, not to run the cheaper design that O4/O8/O9 show cannot decide anything.

## 7. Ceiling on any future record about this barrier

- `claim_tier`: **`toy`** at most (all proposed sizes ≤ 32 bits; `docs/claims-and-verification.md:83`).
  No record may assert medium or crypto behaviour, and none may assert universal impossibility
  (`:76-79`).
- `proof_status`: **`derivation`** for the present paper-level analysis (this document is a
  derivation note in the sense of `docs/claims-and-verification.md:101-106` — a self-contained
  checkable argument, not a machine-verified proof, and explicitly not a counterexample certificate).
  Any future measured record about the barrier is **`empirical_only`** unless it ships a
  counterexample certificate the run wrapper independently re-verifies.
- No `KN-FIND` promotion asserting that `RT-1476-SUBRES-A1` is closed may cite this barrier or this
  review. A `KN-OPEN` entry recording the conditioning question as open would be defensible.

## 8. Implication for `RT-1476-SUBRES-A1`

`BAR-PATHDYN-CONDTAIL-D2` does not survive this review. **A broken barrier is not a positive result
for `RT-1476-SUBRES-A1`. The gate is merely still open.** Nothing in this document is evidence that
`beta < 3/10` is reachable, that `alpha < 3/2` is achievable, that the serial-S3 backward-3-sum
route can produce a sub-rho `m=5` index calculus, or that the successful-subset argument is
*correct* — only that the specific attack on it recorded as `BAR-PATHDYN-CONDTAIL-D2` does not
establish what it claims. The strong adverse prior on the gate is unchanged and is recorded
independently of this barrier at `inputs/idea_generation_20260718_batch2.md:1393` ("Prediction: the
exponent `β→3/2` from above") and `:1413-1417` ("the most likely value (`β≈1`) makes it a scoped
negative"); if anything, O5c's coupling observation points the same adverse way.

**This task does not close the gate, and it does not open it.** Closing a live gate is a closure
result under AGENTS.md rule 12 and requires its own independent `review-breakthrough` review at
`max` effort plus a Coordinator decision record; this task is a `review-adversarial` barrier review
and is not authorized to make that transition. To close `RT-1476-SUBRES-A1` negatively the program
would need: an evidence record from an executed run of the **frozen** contract at
`inputs/idea_generation_20260718_batch2.md:1286-1319` — measuring `beta = d log(ops_success)/d log(q)`
on the successful-membership subset with the contract's stated positive and negative controls — plus
the refutation artifact required by `docs/claims-and-verification.md:90-127` (counterexample
certificate, else derivation note, else declared `empirical_only`), plus a rule-12 review, plus a
Coordinator decision. To close it positively it would need, in addition, an end-to-end charged cost
path including descent, linear algebra, memory, and amortization, against a comparator that does not
exist until G30-001 ships. **Recommended status for `RT-1476-SUBRES-A1`: unchanged — remains an open
gate.** I changed no record.
