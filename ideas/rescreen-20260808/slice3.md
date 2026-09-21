# Adversarial re-screen — slice3 (19 records)

Reviewer: red-team. Repo read-only at `/tmp/wt-ideas-100` (main). No repo file edited.
**External novelty is UNADJUDICATED for all 19 records**: per the brief web search is expected
unavailable and I made no attempt. Every verdict below is an internal-corpus / internal-soundness
verdict. Where a record's own numbers were cheaply checkable I computed them; every number quoted
as "measured" below is real output from a run shown in this session.

## Verdict table

| ID | verdict | one-line reason |
|---|---|---|
| IDEA-20260808-76260d | **REFUTED** | LP relaxation of its own active-S-box program has optimum **r** (=4 at r=4), not 25; g(4) ≥ 6.25, so "g=1 for all r" is false and by weak duality **no** dual can certify 25 |
| IDEA-20260808-bba3dc | **REFUTED** | both headline predictions fail at the record's own declared parameters: 55–65% of levels satisfy k(M) ≤ (ln p)² (predicted <1%), and the count grows linearly in π(X) (predicted O(1)) |
| IDEA-20260808-486ae2 | **PARTIAL-OVERLAP** | its mechanism §, prediction 2 and `constructive_transforms` contain the entire claim of same-day sibling d6d973; neither cites the other. Also: headline "0.500 → 0.400 at memory N^0.16" is 0.360 by its own β |
| IDEA-20260808-d6d973 | **PARTIAL-OVERLAP** | claim (i)+(ii)+"interior optimum at c~√m" is restated verbatim in content inside 486ae2; `discriminated_from` omits it |
| IDEA-20260808-e40da2 | **SCOPE-INFLATED** | the class-wide sample "lower bound" is not a lower bound under the record's own two constraints — it is the memory-balanced operating point; violated by 11.2 bits at N=160, 22.3 at N=384 |
| IDEA-20260808-28361d | **REFUTED (corollary C1)** | C1 ("g=1 never helps, at any c, not even c=0") contradicts the T5 sentence the record itself quotes: reaching a *specified* curve is vectorization at ~√h ~ p^{1/4} ≪ 0.886√N |
| IDEA-20260808-e8586d | NOVEL | sound; two notes (`dominated_by` field misused; deliverable is a gated reproduction) |
| IDEA-20260808-e7ba81 | **REFUTED (two internal contradictions)** | HA-1's "rank = number of distinct error values" is false (rank = number of leaves with nonzero error; a level-1 node gives rank D/2 — as the record's own `claim` field says); and "below the threshold no number of signatures helps at fixed eps" contradicts its own T_crit = D/ε² |
| IDEA-20260808-cbb848 | **REFUTED (argument, not conclusion)** | negative association bounds every joint moment but does **not** bound the upper tail by the binomial tail; exact counterexamples inside its own multivariate-hypergeometric model, including at the very cell it proposes as the verification |
| IDEA-20260808-3d3be9 | NOVEL | measurement is sound and well-controlled; one note — the null side of "resolving power" is decidable by arithmetic in advance, not 0.45 |
| IDEA-20260808-5a748c | **REFUTED (mandatory control)** | the blocking "independent-t0 null" is identical in distribution to the treatment row, so it cannot be "UNSOLVABLE at any beta" while the treatment has finite Δβ |
| IDEA-20260808-4854f8 | **SCOPE-INFLATED** | "gap up to 8 bits" requires κ ≈ 1/p ≈ 2^147 (near-total coupling), whose only plausible mechanism is per-key norm dispersion = catalogue M2-1, the record it discriminates itself *from*; its own stated mechanism gives ≈2^{-140} relative |
| IDEA-20260808-d8510c | NOVEL | cleanest record in the slice; two controls to add |
| IDEA-20260808-0cdd09 | **PARTIAL-OVERLAP / defective fixture** | its frozen 6-value fixture is not reproducible to 4 decimals (8.1984 vs 8.1980; Δ=0.998 not 1.002; ratio 2.713 not 2.724), and the ratio it weights highest has **zero** power against its own declared c=1 null |
| IDEA-20260808-a7872e | NOVEL (one flagged inconsistency) | "unknowns rise from w+1 to w+d" contradicts claim (A)'s own product-subvariety framing; a monic d-split has exactly w unknowns |
| IDEA-20260808-19876e | NOVEL (arithmetic error in prediction 1) | min over θ of the identity is **max(1/3, γ_F)**, not "1/3 at γ≥1/3 and strictly below when γ<1/3"; the sentence also contradicts its own next clause |
| IDEA-20260808-8a6cb5 | NOVEL (design defect) | pre-registered lag range k ≤ 30 exceeds the usable range (~18–20) named in its own confounder, where the Ramanujan envelope is still 0.33 |
| IDEA-20260808-f0dd08 | NOVEL (feasibility defect) | dominance inequality verified exactly correct, but the minimal test asks to "solve to completion, count solutions" on varieties of 16^10–16^15 points, and k* is defined ignoring the cost its own confounder says decides |
| IDEA-20260808-b8e2d4 | **REFUTED** | pre-registered VARIANT-2 ratio "~600" is 0.606 by its own formula and **measured 1.15 / 0.99 / 0.99**; every proposed cell has B³/(6N) > 1 so the yield model is out of range; VARIANT 2 is a tautology; the decay control is stated backwards |

---

## Non-NOVEL verdicts, with the specific claim and the specific computation

### IDEA-20260808-76260d — REFUTED

Claim (i): *"The classical 4-round bound of 25 active S-boxes is EXACTLY the value of an explicit
DUAL-FEASIBLE weighting."* Claim (ii): *"The INTEGRALITY GAP g(r) … is 1 for the single-key
byte-oriented program at all r."* Reproduction gate: *"the dual must certify exactly 25 at r=4
before any other value is reported."*

I built the program the record specifies — binary `x_{i,j}`, one branch-number-5 disjunction per
MixColumns column over its 4 input + 4 output bytes, objective `sum x`, plus the standard
nonzero-trail constraint — and solved the LP relaxation with HiGHS:

```
r= 2: LP relaxation optimum =   2.0000
r= 3: LP relaxation optimum =   3.0000
r= 4: LP relaxation optimum =   4.0000   classical integer bound = 25  -> g = 6.250
r= 6: LP relaxation optimum =   6.0000
r=10: LP relaxation optimum =  10.0000
```

The LP optimum is exactly `r`. The witness is explicit and needs no solver: set **every**
`x_{i,j} = 1/16` and every column indicator `d = 1/16`. Column constraint `8/16 ≥ 5/16` holds;
`x_k ≤ d` holds with equality; each round has total activity 1 so the nonzero-trail constraint
holds; objective `= 16r/16 = r`.

This is not an artifact of a weak MILP encoding. The same point lies in the **exact convex hull**
of each column disjunction `conv({0} ∪ {w ∈ {0,1}^8 : |w| ≥ 5})`: the all-`t` vector is the convex
combination of the 8 cyclic shifts of a weight-5 pattern at weight `t/5` each plus `0` at weight
`1 − 8t/5`, valid for any `t ≤ 5/8`, and `t = 1/16`. Verified symbolically in exact rationals —
all eight coordinates come out `1/16`, total convex weight `1/10 ≤ 1`.

Consequences, both fatal to the record as written:

1. `g(4) ≥ 25/4 = 6.25`, not 1. Claim (ii) is false at the record's own baseline slice, and
   `falsification_conditions` bullet 2 ("g(r) exceeds 1 for the single-key byte-oriented program")
   fires immediately.
2. By **weak duality**, any dual-feasible vector certifies a value `≤` the LP optimum `= 4`.
   So no dual-feasible weighting of any size can certify 25, and claim (i) is not merely unproved
   but impossible. The record's own reproduction gate ("The hand dual does not certify 25 at
   r = 4 — construction wrong, stop") is therefore guaranteed to fire.

The load-bearing error is the identification of the wide-trail argument with LP duality. The
classical `5×5 = 25` argument is a *two-round-superbox* counting argument that multiplies branch
numbers; multiplication is not a nonnegative linear combination of the column inequalities, so it
is not a dual certificate for this program. The record's `honest_prior_of_survival` of 0.75 for the
r=4 dual is misplaced. What survives: the *capability question* ("how much bound strength does a
solver-free machine forfeit") is real, and the answer this computation already gives is
"a factor 6.25 at r=4 for the naive program" — which is a usable, if unflattering, first number.
The record should be refiled as "measure the integrality gap", with claim (i) deleted.

### IDEA-20260808-bba3dc — REFUTED (predictions; obstruction half salvageable)

Prediction 1: *"the fraction of M with k(M) ≤ (log p)² is below 1% at every tested curve."*
Prediction 2: *"max over toy curves of #{M ≤ X : k(M) ≤ (log p)²} … predicted: O(1) and not growing
with X."* Minimal test as specified: `10^3` random ordinary curves, `p ∈ [2^20, 2^40]`, `M` prime
`≤ 500`, `k(M) = ord(π mod M)` in `Z[π]/M`.

I ran exactly that (companion matrix of `x² − tx + p` in `GL_2(Z/M)`, order computed by factoring
`|GL_2(F_M)|`), 5 random ordinary curves per size:

```
p ~ 2^20 (ln p)^2=140.6 : 28-29 / 94 levels satisfy k(M)<=(ln p)^2   =  29-31 %
p ~ 2^30 (ln p)^2=422.6 : 38-54 / 94                                 =  40-57 %
p ~ 2^40 (ln p)^2=722.8 : 54-61 / 94                                 =  57-65 %
```

Predicted `<1%`; measured 29–65%. And growth in X, on a single curve at `p ~ 2^40`:

```
X= 50: 12/14   X=100: 18/24   X=200: 30/45   X=300: 39/61   X=400: 50/77   X=499: 60/94
```

Not `O(1)` — linear in `π(X)`.

The cause is structural and should have been foreseen. For `M` **split** in `O` (i.e. `D = t²−4p`
a QR mod `M`), `π` is diagonalisable with eigenvalues in `(Z/M)^*`, so `k(M) | M−1 ≤ 498`. Measured
`max k` over split primes: 490, versus `max k` over inert primes: 157608 and 229440 at the two
sizes. `(ln p)² > 500` for all `p > e^{√500} = 2^{32.3}`, i.e. over most of the record's *own*
declared range `[2^20, 2^40]`. So once `p` clears 2^32, **every split level `M ≤ 500` passes the
criterion automatically**, for pure arithmetic reasons and with no escape family present.

This matters because it is a false-positive generator in the dangerous direction: the record's
falsification condition reads *"A nonempty, enumerable family of ordinary prime-field curves with
polynomially bounded lcm-torsion degree at a useful level ⇒ the obstruction has an escape … (a
positive, and surprising, outcome)."* Run as specified, the test returns ~60% of levels passing and
would be read as a large escape family. The record's own confounder 1 already names the fix — the
required degree is the **lcm** over the levels, not the per-prime order — but the predictions are
stated on the per-prime statistic, which is the one that saturates.

Part (A), the obstruction itself, is fine and worth keeping: `E[M] ⊆ E(F_{p^k})` iff `π^k ≡ 1` in
`(O/MO)^*` is correct, and the median `k/M` I measured is ≈ 1, consistent with the record's
"of size ~M". Required rewrite: state the prediction on `lcm_{M ≤ X} k(M)` against `p^{poly}` at
levels `M > deg`, and choose the test scale so `(log p)²` is far below the smallest level tested,
which the toy range cannot do.

### IDEA-20260808-486ae2 and IDEA-20260808-d6d973 — PARTIAL-OVERLAP (each with the other)

Same day, same goal (`GOAL-ECDLP-001`), same question (`RQ-ECDLP-002`), and neither `novelty_screen`
nor `discriminated_from` mentions the other (`grep -c` returns 0 in both directions). This is the
`2e14f7` failure mode: an asserted screen that was not performed against the parallel batch.

486ae2's mechanism paragraph already states d6d973's entire claim:

> "The tree parameter exists because eliminating an internal node doubles per-variable degree
> (S_{m+1} has degree 2^{m-1}) while keeping it as a windowed variable multiplies the yield by
> B''/p; the small-root reach degrades roughly like 1/degree, so the optimum is interior. Grouping
> the m leaves into g groups of c = m/g balances the two degrees at 2^{sqrt(m)-1} instead of
> 2^{m-1} …"

and 486ae2's prediction 2 states d6d973's corollary that the fully windowed extreme is dead
("the yield constraint forces window size ≥ p^{1/2}, hence B² ≥ p and the linear algebra exceeds
N^{1/2}"), and its `constructive_transforms.representation_reduction.predicted_gain` states the
trade ("degree 2^{m-1} → 2^{sqrt(m)-1} at a yield cost of (B'/p) per retained internal node").

I verified the shared technical content is correct: `resultant(S_3(x1,x2,u), S_3(x3,x4,u), u)` has
per-variable degree exactly 4, matching `deg S_{m+1} = 2^{m-1}` and d6d973's "confirm 4, 8, 16";
and `eps* = m/(2(m-1))` reproduces `{0.75, 0.667, 0.625, → 0.5}` as 486ae2 states.

Required `discriminated_from` text (for **d6d973**, and a mirror for 486ae2):

> IDEA-20260808-486ae2 (same goal, same day) states the same degree-versus-yield trade over the same
> binary-addition-tree family, including the (B'/p) per retained node factor, the 2^{m-1} → 2^{√m−1}
> grouping optimum, and the "fully windowed extreme is dead by arithmetic" corollary, as the
> mechanism supporting its small-root exponent claim. This record's independent content is limited
> to (a) the exact closed form (B'/p)^{|S|} as a measurable quantity with a toy validation design and
> Poisson error bars, and (b) HA-1's equidistribution ingredient. It does not restate 486ae2's
> eps(m, tree) derivation and must not be counted as independent evidence for it.

Separate arithmetic defect in **486ae2**: `target_complexity.time_exponent` gives two formulas
(`N^{2ε/m}` and `N^{1−ε(m−1)/m}`) which agree only at `ε = m/(m+1)`, and then prints a third number.
At its own `(m=5, ε=0.8, β = ε/m = 0.16)`:

```
LA exponent 2beta = 0.3200 | relation exponent 1-(m-1)beta = 0.3600 | TOTAL = max = 0.3600
record prints 0.400 (both in target_complexity and in sota_delta: "from 0.500 to 0.400 ... at memory N^{0.16}")
```

0.400 is `2ε/m` evaluated at `ε = 1`, not 0.8. The error is in the record's own favour by being
*conservative*, so it is not an overclaim — but the headline number is not reproducible from the
record's own parameters and must be corrected to 0.360 before any promotion.

### IDEA-20260808-e40da2 — SCOPE-INFLATED

The k_max machinery is arithmetically **correct** — I reproduced every cell (`|sinc(1/2)| = 0.6366198`,
coefficient `1.3030·2^k`; N=160 k=4 OK / k=5 fails; N=256 k=5 OK / k=6 fails; N=384 k_max=5;
N=256,l=2 k_max=6, Q=2^42.57; N=48 k_max=3, Q=2^15). That part is sound.

The defect is the quantifier. `quantifier_order` claims:

> "FOR ALL attacks A in class BD and FOR ALL (N, l), if A succeeds per round then A's parameters
> satisfy (*), hence A uses at least 2^{k_max + N/(k_max+1)} raw samples."

But `(*)` is derived by first *imposing* `s = t = N/(k+1)`, which the mechanism section justifies as
"Balancing memory between the list store 2^s and the FFT table 2^t". That is a memory-optimality
convention, not a feasibility constraint. The record's stated constraint set is only
`DETECTION: s ≥ 2·2^k·log2(1/|sinc|)` and `REDUCTION: t = N − k·s ≥ 0`. Minimising `Q = 2^{k+s}`
subject to those two alone, at the same `k_max`:

```
N=160 l=1: record's Q = 2^36.00 ; unbalanced at k=4, s=20.85, t=76.61 -> Q = 2^24.85  (-11.15 bits)
N=256 l=1: record's Q = 2^47.67 ; unbalanced at k=5, s=41.70, t=47.52 -> Q = 2^46.70  (-0.97 bits)
N=384 l=1: record's Q = 2^69.00 ; unbalanced at k=5, s=41.70, t=175.5 -> Q = 2^46.70  (-22.30 bits)
N=256 l=2: record's Q = 2^42.57 ; unbalanced at k=6, s=19.39, t=139.7 -> Q = 2^25.39  (-17.18 bits)
```

So "Q ≥ 2^{k_max + N/(k_max+1)}" is false inside class BD as the record defines it. The honest
statement is a **(samples, FFT-size) Pareto frontier**, with the balanced point one row on it, and
the headline — *"the 1-bit boundary at deployed size is a SAMPLE-ACQUISITION wall and not a compute
wall"* — is exactly the trade the frontier makes: within the class you buy samples down by paying
FFT size up. `time_memory_tradeoff` half-sees this ("raising s beyond N/(k+1) trades FFT memory for
list memory and raises Q") but never considers *lowering* s, which is the direction that breaks the
bound.

This also undermines the record's single strongest novelty argument. `honest_prior_of_survival` says
*"The internal reproduction of the relayed 2^36 at N = 160 from a parameter-free formula is genuinely
surprising and is the main reason the prior is not lower."* The formula is not parameter-free: it
contains one hidden discrete choice, `s = t`. At `N=160, l=1, k=4` the *unbalanced* minimum is
`2^{24.85}` — which is essentially the **other** relayed published row the record itself quotes in
`best_known_baseline` ("2^25 samples / 824 min / 1939 GiB, lattice-with-predicate lineage"). A
constraint set that reproduces 2^36 under one convention and 2^25 under another has not explained
either. The 2^36 agreement should be downgraded from "genuinely surprising" to "one of two values
the model can produce depending on an unstated convention".

### IDEA-20260808-28361d — REFUTED on corollary C1

Corollary C1: *"g = 1 (a single exceptional curve) NEVER helps, at any c, not even c = 0, because
the search alone costs sqrt(N) * polylog."*

The record's own summary of T5, quoted in its claim field, is *"reaching a SPECIFIED curve is
vectorization and costs about sqrt(h) = p^{1/4}"*. I read the source. `analysis/endomorphism-isogeny-decomposition/DECOMPOSITION.md`
line 95-96 says verbatim:

> "But reaching a **specified** curve is the vectorization problem underlying CSIDH: *hard*,
> `~sqrt(h) ~ p^{1/4}` classically at best."

`p^{1/4}` is *below* the rho budget `0.886·sqrt(N) ≈ p^{1/2}`, not above it. So for a single good
curve whose address the attacker knows, total cost is `~p^{1/4} + c`, which beats rho for any
`c < p^{1/2}` — and at `c = 0` beats it by a full `p^{1/4}`. C1 as stated ("at any c, not even
c = 0") is false in precisely the case T5 carved out.

The mechanism error is that the record's inequality `(h/g)·τ + c` prices exactly one strategy —
blind walk-and-test — and then asserts it as the minimum over all strategies. T5's dichotomy has
three cases (common enough to random-walk / locally detectable / identifiable only by a global
address); the record collapses the third into the first and thereby *loses* the cheapest route.
`dominated_by` says "As a GATE … it is dominated by nothing, because DECOMPOSITION.md T5 … is
qualitative and, this record argues, wrong in its central dichotomy" — but the thing it is dominated
by is a cost route stated in T5 itself.

What survives, and should be refiled: the density inequality is the right gate **for the
non-identifiable case**, and (C3) — that whole-class enumeration sits at `p^{1/2+o(1)}` time with
`p^{1/2+o(1)}` memory and is Pareto-dominated by rho — is correct and worth recording. The correct
T5′ is a *two-branch* statement: `g > τ·polylog·√r/0.886` when goodness is undetectable, and
`p^{1/4} + c < 0.886√(N/r)` when the good curve has a computable address. The second branch is the
interesting one and the record deletes it.

(Directional note, not a defect: the record's `honest_prior_of_survival` of 0.9 for `R = h/√N` landing
in a polylog window is well founded — `h ≈ √|D|·L(1,χ)/π` with `|D| ≈ Θ(p)` gives `R ≈ 0.5–0.64·L(1,χ)`.
The measurement is worth doing; it is the inference from it that is wrong.)

### IDEA-20260808-e7ba81 — REFUTED (two internal contradictions)

**(a) HA-1's rigorous ingredient is a false linear-algebra statement.** HA-1 says:

> "Any deviation is therefore EXACTLY a sum of rank-one terms indexed by leaves … **The rank of the
> perturbation is the number of DISTINCT error values, and that is a fact about the code, not a
> heuristic.**"

For orthonormal `u_i` (Gram–Schmidt directions, normalised), `rank(Σ_i c_i u_i u_i^T) = #{i : c_i ≠ 0}`,
not the number of distinct values of `c`. Measured at D = 64:

```
one level-1 node bad (D/2 leaves share ONE error value):  #distinct = 1   actual rank = 32
one level-2 node bad (D/4 leaves share ONE error value):  #distinct = 1   actual rank = 16
3 distinct error values over D/2+D/4+D/8 leaves:          #distinct = 3   actual rank = 56
one single leaf bad:                                      #distinct = 1   actual rank =  1
```

The record's own `claim` field agrees with the measurement and contradicts HA-1: it writes
`Cov(z) = σ²(I + Σ_{j≤r} ε_j P_j)` with "P_j orthogonal projectors of **rank D/2^{level(j)}**".
So the record specifies a perturbation of rank up to `D/2` and then applies **rank-one** BBP to it.
The mechanism sentence *"the deviation … is LOW RANK when the errors are shared across a subtree"*
is exactly backwards: errors shared across a subtree give rank equal to the subtree size.

The consequence is not that the record is worthless — for a spike of rank `k = αD` the model is a
two-point population spectrum and the sample spectrum has a second **bulk**, which is *easier* to
detect than a BBP edge excursion — but the stated detector (largest eigenvalue) and the stated
threshold are then the wrong instrument and a pessimistic curve. `validation_route` for HA-1
("count DISTINCT relative errors … If that count is O(D) rather than O(log D), HA-1 is false")
measures the wrong integer; it should count leaves with nonzero error.

**(b) The headline sharpness claim contradicts the record's own formula.** Title and claim:
*"a SHARP threshold — below which no number of signatures helps the top-eigenvalue statistic at all"*
and *"BELOW that threshold the top eigenvalue carries asymptotically ZERO information no matter how
many more signatures are collected at fixed eps"*, alongside `T_crit = D/ε²`. At fixed `D` — which is
the case for a fixed scheme, D ∈ {1024, 2048} — collecting more signatures reduces `γ = D/T` and
crosses the threshold:

```
D=1024, eps=0.05: T_crit = 409,600.  T=102,400 -> sqrt(gamma)=0.100 > eps (no detection)
                                     T=409,600 -> sqrt(gamma)=0.050 = eps (boundary)
                                     T=1,638,400 -> sqrt(gamma)=0.025 < eps (DETECTION)
```

"No number of signatures helps" is a statement about the ray `D, T → ∞ at fixed γ`, and it is false
in the regime the goal cares about. `T_crit = D/ε²` is precisely the number of signatures that
suffices; the two sentences cannot both stand. Since the record's stated `sota_delta` is "converts an
uncalibratable test into one with … a closed-form power curve", the power curve is the salvageable
part and the phase-boundary rhetoric must be deleted.

Minor, and worth fixing in the same pass: `claim` defines `ε` on the **covariance** while prediction 2
sweeps a **width** multiplier `(1+ε)`. Since `σ_i → σ_i(1+δ)` gives `σ_i² → σ_i²(1+2δ+δ²)`, the
transition in prediction 2 sits at `ε/√(D/T) = 0.5`, not 1.

### IDEA-20260808-cbb848 — REFUTED (the argument; the conclusion may still hold)

Claim (i): *"NEGATIVELY ASSOCIATED, which bounds E[prod_j f_j(W_j)] ≤ prod_j E[f_j(W_j)] for ALL
increasing f_j and hence bounds the joint moment of EVERY order from above by its independent
counterpart — so the conditional term can only make Theorem 6.1's binomial tail CONSERVATIVE."*

The implication "every joint moment bounded above ⇒ the upper tail bounded above" is invalid.
`P[N ≥ m] = Σ_{j≥m} (−1)^{j−m} C(j−1, m−1) S_j` is an **alternating** sum, so a one-sided bound on
every `S_j` does not sign the tail. Exact computations inside the record's own model (uniform
`W`-subsets of a partitioned ground set ⇒ multivariate hypergeometric block weights; block failure
= `1{W_j ≥ thresh}`), all in exact rationals:

```
n_e blen  W thr m |     p    | all S_j <= indep? | P[N>=m]   BinTail   verdict
  2   1   1   1  1 | 0.50000  |      True         | 1.000000  0.750000  ANTI-CONSERVATIVE
  3   1   1   1  1 | 0.33333  |      True         | 1.000000  0.703704  ANTI-CONSERVATIVE
  4   2   2   1  1 | 0.46429  |      True         | 1.000000  0.917637  ANTI-CONSERVATIVE
  6   2   3   1  2 | 0.45455  |      True         | 1.000000  0.841983  ANTI-CONSERVATIVE
  6   8   6   2  1 | 0.25825  |      True         | 0.978638  0.833444  ANTI-CONSERVATIVE
```

The last row is **the record's own proposed verification**: *"Verify the NA step numerically at a
scale where brute force is possible — n_e = 6 blocks of length 8, all weight allocations enumerated —
by checking E[prod 1[W_j ≥ t]] ≤ prod E[1[W_j ≥ t]] exactly."* That check **passes** while the
conclusion it is supposed to license **fails**. A control that passes in a cell where the conclusion
is false does not test the load-bearing step.

Being fair to the record: HQC sits in the far upper tail (`m = δ_e+1 ≫ n_e p_i`), and there the
conclusion does appear to hold. Exact DP over the same model:

```
n_e blen  W thr m |      p     n_e*p |   P[N>=m]     BinTail    ratio   verdict
  46  20  30   4  3 | 3.101e-03  0.143 | 9.4309e-05  4.0976e-04  0.2302  conservative
  46  20  30   4  5 | 3.101e-03  0.143 | 8.3265e-10  3.5369e-07  0.0024  conservative
  46  50  60   5  5 | 8.787e-03  0.404 | 2.3199e-06  5.3199e-05  0.0436  conservative
```

So the record is probably **right** and its proof is **wrong**. Two consequences the record must
absorb. First, the valid route in the far tail is Bonferroni's first inequality
`P[N ≥ m] ≤ S_m ≤ S_m^{ind} = C(n_e,m)p^m`, plus an explicit accounting of the `(1−p)^{n_e−m}` factor
separating `C(n_e,m)p^m` from the binomial tail — not "all joint moments bounded". Second, the
record's prior is quantitatively off: it predicts *"the NA deficit for n_e = 46 nearly-independent
blocks is tiny"*, whereas the matched-shape toy above shows a deficit of **8.7 bits** at
`n_e = 46, m = 5`. The missing control: the parameter that should destroy the NA deficit is the block
length `n_2` at fixed density (hypergeometric → independent as `n_2 → ∞`); the record must show the
deficit decaying in `n_2` and extrapolate to HQC's `n_2`, not assert it is small.

### IDEA-20260808-5a748c — REFUTED (mandatory blocking control is degenerate)

`controls[0]`: *"Independent-t0 null (mandatory before any Delta beta is believed)."*
`predictions[1]`: *"the independent-t0 null (t0 resampled independently of the key so t1 carries no
information about s1) … The null must be UNSOLVABLE at any beta; a finite beta for the null means the
pipeline scores noise and every row is void."*

`predictions[0]` defines the treatment row as: *"Primal block size for the MLWE instance with error
(s2 − t0), **t0 uniform on the exact Power2Round range**."*

These are the same instance distribution. If you resample `t0` independently and publish
`t1 = (A s1 + s2 − t0')/2^d`, then `2^d t1 = A s1 + (s2 − t0')` with `t0'` independent uniform — which
is exactly the MLWE instance the treatment row models, and it *does* carry information about `s1`.
The parenthetical "so t1 carries no information about s1" is false. So the null must return the same
finite `β` as the treatment, and the record's own falsification condition ("The null returns a finite
comparable beta … instrument failure, nothing interpretable") fires on a correct pipeline.

The intended null is presumably "resample `t1` uniformly at random, independent of the key". As
written, the blocking control cannot be run.

There is a second, related modelling issue the record should carry: `t0` is a **deterministic**
function of `(s1, s2)`, so the t1-only instance is Learning-With-Rounding, not LWE with independent
wide error. Treating it as the latter is the conservative-for-the-defender direction and is standard,
but it is an unnamed heuristic doing real work in a record whose entire deliverable is `Δβ`. HA-1
covers only "variance-only summary", not "deterministic → independent".

The rest of the arithmetic checks out: `sd(t0) = 2^12/√3 = 2364.9`; `sd(s2) = √2 = 1.414` at η=2 and
`√(60/9) = 2.582` at η=4; `log2(q/σ)` moves `22.50 → 11.79`. Direction of `Δβ > 0` is right.

### IDEA-20260808-4854f8 — SCOPE-INFLATED

Claim: *"the gap, bounded above by log2(256) = 8 bits for ML-KEM and log2(64) = 6 bits for Frodo, is
a systematic attacker-favourable bias in every published failure-boosting cost."*

The bound `DFR_union / DFR_true ≤ n` is correct (Boole), but it is nowhere near attainable under the
record's own stated mechanism. With `κ(lag) = P[fail_i ∧ fail_j]/(p_i p_j)` as the record defines it,
the first inclusion–exclusion correction relative to the union bound is `(n−1)κp/2`. At ML-KEM-512's
`δ ≈ 2^{-139}` (so `p ≈ 2^{-147}`):

```
kappa=2^0   : correction/union = 7.15e-43  -> gap 0.000 bits
kappa=2^40  : correction/union = 7.86e-31  -> gap 0.000 bits
kappa=2^100 : correction/union = 9.06e-13  -> gap 0.000 bits
kappa=2^130 : correction/union = 9.73e-04  -> gap 0.001 bits
kappa=2^139 : correction/union = 4.98e-01  -> gap 0.994 bits
```

A **1-bit** gap needs `κ ≈ 2^{139}`, i.e. `P[coord j fails | coord i fails] ≈ 1/128`; the record's
`honest_prior_of_survival` puts `P(gap > 3 bits) ≈ 0.2`, which needs `κ ≈ 2^{141.5}`, i.e. near-total
coupling. The record's *stated* mechanism — "different coefficients … are sums over the SAME multiset
of multiplicands, re-paired … uncorrelated at second order and dependent at fourth order" — predicts
`κ = 1 + O(small)`, hence a gap of order `2^{-140}` relative, i.e. numerically zero.

The only channel that can plausibly deliver `κ ≈ 1/p` is **per-key dispersion**: conditional on any
failure the secret has anomalously large norm, so other coordinates fail too. That is catalogue
**M2-1** ("per-key DFR dispersion — DFR as a random variable over KEYS"), which the record's
`discriminated_from` explicitly disclaims ("M2-1 varies the key; this fixes the key and varies the
coordinate pair").

That disclaimer also contradicts the record's own minimal test. Step (2) computes "the exact joint law
of `(w_i, w_j)` per lag by convolving over shared multiplicands" — i.e. **marginalising over the key**,
not fixing it. So the experiment as designed will measure the M2-1 channel and attribute it to
negacyclic re-pairing. Required fix: report `κ` both conditioned on a fixed key and marginalised, and
route the difference to M2-1. Without that split the record cannot distinguish its claimed mechanism
from the one it says it is not about.

Also note the mechanism is not needed for the sign: `P[∪ A_i] ≤ Σ P[A_i]` holds regardless of the sign
of association, so "strictly positive **because** … POSITIVELY associated" over-derives a trivial fact.

### IDEA-20260808-0cdd09 — PARTIAL-OVERLAP / defective frozen fixture

Two defects, both in fields the record itself designated as gates.

**(1) The frozen fixture does not reproduce.** `proof_search_map.baseline_embedding.reproduction_check`:
*"FROZEN FIXTURE: the six intermediate values (8.1980, 3.4157, 53.845, 8.3134, 3.4308, 54.847) must be
reproduced to four decimals by an independent implementation before any observed number is read."*
Independent implementation, `f(b) = (b ln2)^{1/3}(ln(b ln2))^{2/3}`, `c = (64/9)^{1/3}`:

```
b=795: (b ln2)^(1/3)=8.1984  (ln(b ln2))^(2/3)=3.4154  c*f=53.845
b=829: (b ln2)^(1/3)=8.3137  (ln(b ln2))^(2/3)=3.4305  c*f=54.843
c*f(829)-c*f(795) = 0.9982  (record: 1.002)
sieving ratio exp(delta) = 2.7133  (record: 2.724)
matrix ratio             = 1.6472  (record: 1.650)
```

Four of the six values fail at the fourth decimal, and the record's own six numbers are mutually
inconsistent: `8.1980 × 3.4157 × 1.922999 = 53.847`, not the 53.845 it also states. The residuals are
far inside the ±25% pass band so no conclusion changes, but a gate that the record's own numbers fail
is a gate that will be quietly widened. Fix the fixture before dispatch.

**(2) The ratio it weights highest has zero power against its own declared null.** The record's
mandatory `POWER CHECK` is: *"a wrong-exponent null with c = 1 predicts a sieving ratio
exp(1.002/1.923) = 1.67. If the pass band admits both 2.72 and 1.67 the test has no power and must be
tightened or abandoned."* For the sieving ratio this works (c=1 gives 1.68, outside `[2.18, 3.41]`).
For the **matrix** ratio it does not, because `β` enters and `c` cancels:

```
matrix ratio with c=(64/9)^(1/3) : 1.6472
matrix ratio with c=1, beta held : 1.6472   <-- IDENTICAL
```

Yet the record says *"THE MATRIX RATIO IS THE SHARPER OF THE TWO … It is weighted higher for that
reason."* By the record's own criterion the matrix ratio "must be tightened or abandoned". Relatedly,
because `β/c = (8/64)^{1/3} = 1/2` exactly, `matrix ratio = sqrt(sieving ratio)` identically
(`√2.7133 = 1.6472`) — the two are not two independent predictions of the model but one prediction
plus a deterministic relation. That relation is worth testing, but the record should say so rather
than count two tests. A coherent `c=1` null (with `β = c/2`) gives matrix ratio 1.298, only just
outside the `[1.32, 2.06]` band — genuinely marginal power.

Third, minor: *"extrapolation error to 2048 bits grows like residual^{(2048−829)/34} = residual^{35.9}"*
is linear in **bits**; linear in `f`, which is what `ε·f` differences actually compose in, gives
`(f(2048)−f(829))/(f(829)−f(795)) = 26.22`. The record labels this "the crudest linear model", so it
is a note rather than a defect, but the honest exponent is 26, not 36.

### IDEA-20260808-b8e2d4 — REFUTED

This record should not have been filed, on four independent grounds.

**(1) The pre-registered VARIANT-2 number is wrong by three orders of magnitude.** `predictions[1]`:
*"Predicted (6 * N) / B^3, which is exponentially large. At p = 101, B = 10, this is ~ 600. A ratio
< 10 indicates the oracle is not providing the predicted advantage."* Computed:
`6N/B³ = 6·101/1000 = 0.606`. The record appears to have evaluated `6N` and dropped `/B³`.

**(2) Every proposed cell is outside the range of the record's own yield model.** `Y_exhaust = B³/(6N)`
is asserted to be a probability. At the twelve cells `p ∈ {101,103,107,211} × B ∈ {10,20,50}`:

```
p=101 B=10: Y_exh=1.650   p=101 B=20: 13.20   p=101 B=50: 206.3
p=211 B=10: Y_exh=0.790   p=211 B=20:  6.32   p=211 B=50:  98.7
```

Eleven of twelve exceed 1. Using the exact multiset count `C(B+2,3)/N` instead, `P_dec = 1.000` in all
twelve, so the **maximum possible** ratio `Y_full/Y_exhaust` is 1.000 in every cell.

**(3) The experiment, actually run, gives ratio ≈ 1.** I built a prime-order curve
`y² = x³+2x+21 / F_101` (N = 107 prime), took `V` a random size-B subset, computed the exact set of
targets decomposable over `V` at arity ≤ 3, and measured all three yields over 4000 trials per cell:

```
 B   Y_exh    Y_v1     Y_v2     ratio_v1  ratio_v2   record's predicted ratio_v2
10   0.8628   0.8590   0.9932    0.996     1.151      0.642  (record says ~600)
20   1.0000   0.9890   0.9858    0.989     0.986      0.080
50   1.0000   0.9910   0.9912    0.991     0.991      0.005
```

VARIANT 1 behaves as predicted (≈1, the record's null is fine). VARIANT 2 measures **1.15, 0.99, 0.99**.
The record's falsification condition *"VARIANT 2 yields ratio < 10. The instrument is broken"* fires in
every cell — but the instrument is not broken; the prediction is.

**(4) VARIANT 2 is a tautology, and would produce a useless relation even if it "worked".** VARIANT 2
draws `P_1..P_m` uniformly **from V**, sets `R = P_1+…+P_m`, then "checks whether R decomposes over V".
It does, by construction. That is not a relation for index calculus: the resulting identity
`ΣP_i − ΣP_i = 0` is a zero row in the relation matrix and carries no information about the discrete
log, because `R` was not a target `aP + bQ`. Index calculus needs `R` sampled from `⟨P⟩` independently
of `V`; the moment you sample it from `V`'s subset sums you have assumed away the problem.

**(5) The decay control is stated backwards.** `null_object_control`: *"DECAY PARAMETER: B/p over the
ladder {2^-6, 2^-4, 2^-2, 2^-1}. For VARIANT 2, the ratio Y_full / Y_exhaust must **GROW**
exponentially with B/p (since it is ~ (m! N) / B^m)."* `(m!N)/B^m` is monotonically **decreasing** in
`B`; over that ladder `B` rises 32× so the record's own formula falls by 32768×. The mandatory control
would therefore reject a correct implementation.

Also, schema: `b8e2d4` is one of a family of seven same-day records (`3f8a2b, 7c4e9d, a3f7c1, c5f9a2,
4f3ef4, 621df3`) all with `goal_id: None`. Across the 126 records dated 2026-08-08 it is missing four
fields present in ≥94% of the cohort — `goal_id` (119/126), `controls` (119/126),
`discriminated_from` (119/126), `why_not_a_renamed_known_approach` (118/126) — and carries
`null_object_control` (3/126) and `id_allocation_provenance` (4/126) instead. The absent
`discriminated_from` is not cosmetic: its nearest same-day neighbours by title are `a3f7c1`
(Jaccard 0.26, y-coordinate oracle) and `c5f9a2` (Jaccard 0.41, endomorphism-image oracle), which are
the same "oracle variant N" template.

---

## Notes attached to the NOVEL verdicts

**IDEA-20260808-e8586d (FAEST split optimum) — NOVEL.** Recall of `2^126.1` as the matched AES-128
baseline is right. Two notes. (a) `dominated_by` is not a Pareto check — "IDEA-20260731-002 … dominates
it only in the sense of supplying the model this record optimises within" is a dependency, not
domination; the field should either name a real competing frontier row or say `n/a (no attack-cost
result claimed)` as several siblings do. (b) The record's own prior for the interesting branch is 0.08
and the deliverable is blocked on RSF-5 (unread spec). That is honestly stated; `medium` priority is
the right call and should not be raised.

**IDEA-20260808-3d3be9 (square-code defect at deployed parameters) — NOVEL.** The measurement is
well-designed and the positive-control-first discipline is exactly right. One correction:
`honest_prior_of_survival` says *"about 0.45 that the statistic has any resolving power at these
dimensions rather than being saturated for everything"*. The null side of that is decidable in advance
by arithmetic, not a 0.45 coin flip:

```
mceliece348864  n=3488 mt= 768  C(mt+1,2)=  295,296   C/n =  84.7
mceliece460896  n=4608 mt=1248  C(mt+1,2)=  779,376   C/n = 169.1
mceliece6688128 n=6688 mt=1664  C(mt+1,2)=1,385,280   C/n = 207.1
mceliece6960119 n=6960 mt=1547  C(mt+1,2)=1,197,378   C/n = 172.0
mceliece8192128 n=8192 mt=1664  C(mt+1,2)=1,385,280   C/n = 169.1
```

`min(n, C(mt+1,2)) = n` at every set by an 85–207× margin, so "defect zero on null 1" is an identity,
not an observation. The only live question is whether the *structured* square also reaches `n`, and the
record should say so up front rather than presenting the null as a measurement. The "about 10^6
products" estimate is right (2.95e5 to 1.39e6). The convention control (over `F_2`, `x*x = x`, so
`C^{*2} ⊇ C` and the count is `C(mt+1,2)`) is correct and rarely stated — good.

**IDEA-20260808-d8510c (Heuristic-1 second moment) — NOVEL.** The cleanest record in the slice: it
consumes a named in-repo gap, states a specific object, and pre-registers a composition-family positive
control (`n = m k²`) that must fire before any negative is reportable. Two additions I would require.
(a) The `dominated_by` is `n/a`, which is right, but the record inherits `p^{1/3+o(1)}` time **and
memory** from KN-TECH-058 without the full-cost charge; under KN-TECH-057's Wiener 3D model a table of
`p^{1/3}` entries has `τ = p^{1/9}`, so the tier's full cost is `p^{4/9} = p^{0.444}` against the VW
polynomial-space baseline `p^{1/2}` — a margin of `p^{1/18}`, not `p^{1/6}`. That does not affect this
record's deliverable but it should be the number quoted whenever the tier is cited. (b) The null object
("random integral ternary forms of determinant p/4 that are not ideal forms") is right; add the
parameter that should destroy the signal — the excess correlation over the null must **shrink** as `p`
grows if the Poisson/near-independence picture is right, and the record's own falsification bullet
already says a correlation that *grows* with `p` is the reportable negative. Make that the primary
readout rather than the raw ratio.

**IDEA-20260808-a7872e (SDitH d-split) — NOVEL, one inconsistency to fix.** `mechanism` says
*"unknowns rise from w + 1 to w + d"*. If `Q` is monic of degree `w` it has `w` unknown coefficients,
and if it is forced to factor as `d` **monic** polynomials of degree `b = w/d` the unknowns are
`d·b = w` — the same count. The split is a constraint on which of the `q^w` monic `Q` are admissible
(roots confined to block-`j` evaluation points), which is a solution-count statement — i.e. exactly
`cbd93d`'s entropy ratio, the thing claim (B) says the split goes beyond. Claim (A)'s genuine content
must therefore be that substituting `Q = Π Q_j` into `S Q = P F` raises the system's **degree in the
unknowns** from 1 to `d`, which is a change in the ideal but plausibly in the *unfavourable*
direction for Gröbner at fixed `b`. The "each block's subsystem decouples onto n/d evaluation points"
step additionally needs the code itself to split, which is not established and which the record's own
assumption list marks as recalled-from-memory against an unread spec. Required control: before the `b`
sweep, verify on one toy cell that the block subsystems actually decouple; if they do not, the whole
`b`-dependence claim is about a system nobody solves.

**IDEA-20260808-19876e (SQIsign distinguisher → set-shrinker) — NOVEL, arithmetic error.**
`predictions[0]` states the minimisation result as *"min over theta of (1/2 − 3θ/2) + max(γ_F, θ) which
is 1/3 at γ_F ≥ 1/3 and strictly below only when γ_F < 1/3"*. Computed over a fine θ grid:

```
gamma_F=0.0000: min = 0.3333   gamma_F=0.1000: min = 0.3333   gamma_F=0.3333: min = 0.3333
gamma_F=0.4000: min = 0.4000   gamma_F=0.5000: min = 0.5000        i.e.  min = max(1/3, gamma_F)
```

Both halves of the stated sentence are wrong (at `γ_F < 1/3` the min is exactly 1/3, never below; at
`γ_F > 1/3` it is `γ_F`, strictly above), and the sentence contradicts its own next clause ("a FREE
constant-advantage distinguisher still gives 1/3"). The two reproduction gates do pass
(`(1/3,0,1/3) → 1/3` and `(1/4,0,1/4) → 3/8` exactly), and the substantive conclusion (`s = 0 ⇒ no
exponent change`) is unaffected — but a record whose `falsification_conditions[0]` is "the reproduction
gate fails" must state the reproduction correctly. Also: `dominated_by` claims "ROWS CHECKED:
KN-TECH-057's four full-cost rows", yet the baseline `p^{1/3+o(1)}` **time and memory** is quoted
uncharged; see the KN-TECH-057 note under d8510c above.

**IDEA-20260808-8a6cb5 (S_B autocorrelation vs Ramanujan) — NOVEL, design defect.** The rate is right
(`2√2/3 = 0.94281`, below 0.05 by k = 51, record says ~50). The defect is that the pre-registered
range exceeds the usable range the record itself names. Its confounder says the diameter of a
`|V| ≤ 611` graph is `~2 log2 611 ≈ 18.5` so "lags beyond ~20 are saturated and carry no information";
its prediction says "consistent with the Ramanujan envelope at **all k ≤ 30**". Envelope values:

```
k= 5: 0.745   k=10: 0.555   k=15: 0.413   k=18: 0.346   k=20: 0.308   k=30: 0.171
```

Inside the usable range the envelope has only fallen to ~0.33, so "consistent with the envelope" is
satisfied by almost any decaying curve, and the discrimination the record wants (Ramanujan rate vs
"materially more slowly") is being asked of 18 lags spanning a factor-3 decay. Second, the record's own
confounder 2 concedes `S_B` may be near-constant at toy `p` and that "the B grid must be chosen so that
`S_B` has non-degenerate variance" — choosing `B` after inspecting the archived `δ_E` labels is a
post-hoc choice that defeats pre-registration. Required fix before dispatch: pre-commit the `B` grid
from the archived `δ_E` marginal (which already exists under `EXP-SSIQ-a85692`), restate the prediction
on `k ≤ 15`, and state the estimator's standard error at `|V| ≤ 611` so "materially slower" is a number.

**IDEA-20260808-f0dd08 (UOV component dominance) — NOVEL, feasibility defect.** The inequality is
exactly right and I re-derived it: `k·o > k(n−o) − C(k,2)o ⟺ n/o < 2 + (k−1)/2`; thresholds
`2.5, 3, 3.5, 4, 4.5` for `k = 2..6`; `uov-Ip 112/44 = 2.5455 → k* = 3`; excess at `k=2` is
`2(112−44) − 44 − 88 = 4`, so `q^4 = 2^32`, all reproduced. `k*` for SNOVA (5.8 → 9) and QR-UOV
(3.9 → 5) reproduce; MAYO at `n/o = 8` gives `k* = 14`, not the stated "≥ 15" (at `n/o = 10` it is 18).
The GL_k symmetry noted in the confounders is genuinely correct
(`P_a(Σc_i x_i) = Σc_i²P_a(x_i) + Σ_{i<j}c_i c_j P'_a(x_i,x_j) = 0`), which is a sign of care.

Two problems. (a) `minimal_test` says *"build the k-tuple system, solve it to completion, count
solutions, and classify each as in O^k or junk"*. Junk dimensions at the proposed cells:

```
(16,10,4) k=2 junk dim  8  -> 16^8  = 4.3e9   solutions
(16,11,4) k=2 junk dim 10  -> 16^10 = 1.1e12
(16,12,4) k=2 junk dim 12  -> 16^12 = 2.8e14
(16,13,4) k=2 junk dim 14  -> 16^14 = 7.2e16
(16,13,4) k=3 junk dim 15  -> 16^15 = 1.2e18
```

Three of four cells at `k=2` and most at `k=3` cannot be enumerated. The measurable quantity is the
*dimension* (via the saturation the confounders already name), not the solution count, and the
prediction should be restated on dimensions.
(b) Claim (ii) — *"the binding attack order k* is therefore the smallest k with n/o < 2 + (k−1)/2, and
the published cost model must be evaluated at k*, not at k=2"* — defines `k*` **ignoring cost**, while
confounder 3 says *"the solve cost can swamp the dominance gain; total charged cost, not solving
degree, is the deciding metric"*. Those cannot both stand, and the MAYO row (`k* = 14`, a system in
`14n` variables) shows the dominance-only definition is not selecting an attack. Rename `k*` to
"the dominance threshold" and make the binding order the argmin of charged cost, as confounder 3
already says. Also: the toy sweep `n/o ∈ {2.5, 2.75, 3.0, 3.25}` never puts a cell strictly **below**
the `k=2` threshold (2.5), so the predicted "fraction → 1" side of the `k=2` transition is never
observed; add a cell at `n/o = 2.25`.

---

## What I actually checked

**Corpus files read:** `/tmp/ideas-ctx/RESCREEN_BRIEF.md`, `slice3.txt`, `KNOWLEDGE_BARRIERS.txt`
(confirmed `KN-TECH-057`, `KN-FIND-720727`, `KN-FIND-860118` are blank at lines 117, 40, 43),
`EXISTING_PROPOSALS.txt`, `EXISTING_HYPOTHESES.txt`, `REJECTED_TITLES.txt`, `CATALOGUE_TITLES.txt`
(topic greps for all 19 subjects; no hits indicating duplication against pre-existing records).

**In-repo records read in full:** `knowledge/techniques/KN-TECH-057.md`,
`knowledge/findings/KN-FIND-720727.md`, `knowledge/findings/KN-FIND-860118.md`,
`analysis/endomorphism-isogeny-decomposition/DECOMPOSITION.md` lines 86–115 (T5 verbatim),
all 19 assigned proposals in full. Confirmed existence of the cross-referenced records
`IDEA-20260801-021`, `IDEA-20260803-e2f5bd` (486ae2's `|F_p| ≤ 3d_p` citation checks out verbatim),
`IDEA-20260805-250e50`, `IDEA-20260808-a3f7c1`, `IDEA-20260807-7270d1`, `IDEA-20260807-070d03`,
`H-XOR-d1a480`, `DEC-20260808-6a7ac4`.

**KN-TECH-057 (blanked, 19 of 126 proposals touch this ground).** Five records in this slice touch
isogeny path-finding baselines: `19876e` (cites it explicitly — so at least one generator read the
repo record, not just the barriers file), `8a6cb5`, `d8510c`, `bba3dc`, `28361d`. None restates it,
so no duplication. The recurring gap is that the conditional `p^{1/3+o(1)}` **time-and-memory** tier is
quoted uncharged; under KN-TECH-057's own Wiener 3D model its full cost is `p^{1/3}·(p^{1/3})^{1/3} =
p^{4/9}` against the VW polynomial-space matched baseline `p^{1/2}`. `8a6cb5` is the only one that
engages the vOW curve explicitly ("a movement along the vOW curve and must be reported as such").
**KN-FIND-720727** (ML-DSA formal proofs cover cryptographic adversaries only) and **KN-FIND-860118**
(ML-KEM break-claim correction): neither is duplicated or contradicted by any record in this slice —
`5a748c` is a lattice-estimator record with no fault-injection or formal-proof content, and `4854f8`
is a DFR-correctness record that makes no quantum or PIP claim.

**Computations run (all output shown above, none fabricated):**
1. AES active-S-box LP built from the record's own constraint description and solved with
   `scipy.optimize.linprog` (HiGHS) at `r ∈ {2,3,4,5,6,8,10}`; plus an exact-rational verification
   that the all-`1/16` point lies in the convex hull of each column disjunction.
2. `ord(π mod M)` for the companion matrix of `x² − tx + p` in `GL_2(Z/M)` over 15 ordinary curves at
   `p ~ 2^20, 2^30, 2^40` and the 94 primes `3 ≤ M < 500`; split/inert stratification via
   `jacobi(D, M)`; growth of the count in `X`.
3. Full enumeration of the class-BD feasible region `(k, s, t)` under e40da2's two stated constraints
   at `(N,l) ∈ {(160,1),(256,1),(384,1),(256,2),(48,1)}`.
4. Rank of `Σ_i c_i u_i u_i^T` for orthonormal `u_i` at `D = 64` under four subtree-error patterns;
   BBP threshold crossing at fixed `D = 1024` as `T` grows.
5. Exact-rational multivariate-hypergeometric block-weight computation (full enumeration for small
   cells, DP for `n_e = 46`): joint moments `S_j` vs independent counterparts, and `P[N ≥ m]` vs the
   binomial tail, in both the near tail and the far tail.
6. Elliptic curve `y² = x³+2x+21 / F_101` (N = 107 prime) built from scratch; exact arity-≤3
   decomposable set over random `V`; 4000-trial yields for b8e2d4's three oracle variants at
   `B ∈ {10,20,50}`; plus the `B³/(6N)` and `C(B+2,3)/N` tables at all twelve proposed cells.
7. NFS `f(b) = (b ln2)^{1/3}(ln(b ln2))^{2/3}` at `b ∈ {795, 829, 2048}` and both ratios, `c = 1` null
   for both ratios.
8. `min_θ [(1/2 − 3θ/2)_+ + max(γ_F, θ)]` on a 200001-point grid for `γ_F ∈ {0, 0.1, 1/3, 0.4, 0.5}`;
   both of 19876e's reproduction gates.
9. UOV dominance dimensions, `k*` table, and junk-component point counts at the four toy cells.
10. `C(mt+1,2)` vs `n` at the five Classic McEliece parameter sets.
11. Inclusion–exclusion correction magnitude for ML-KEM as a function of `κ` at `δ = 2^{-139}, 2^{-164}`.
12. Semaev `S_4 = res_u(S_3(x1,x2,u), S_3(x3,x4,u))` per-variable degree via sympy (= 4, confirming
    d6d973's `2^{m-1}`).
13. Field-presence census over all 126 records dated 2026-08-08 (yaml load) for the b8e2d4 schema
    check; token-Jaccard title collision scan of my 19 against all 126.

**What I could not verify, and what would settle it.**
- *All external novelty*, for all 19 records. Would be settled by a literature check; the highest-risk
  named candidates are: e40da2 (a class-level Bleichenbacher parameter bound may be published),
  e7ba81 (spiked-covariance/BBP applied to Gaussian-sampler distinguishing), 486ae2 (Semaev's original
  interval-factor-base proposal may contain part B), f0dd08 (Beullens Eurocrypt 2021 may already select
  `k` by a dominance criterion), 0cdd09 (the NFS simulation methodology may already contain a
  cross-size validation).
- *a7872e's modelling*: whether SDitH's `S Q = P F` system decouples across the `d` blocks. The record
  itself flags the spec as unread. Settled by one read of the Round-3 specification.
- *e8586d, 5a748c, 3d3be9*: all gated on primary-source parameter reads (RSF-5, FIPS 204, KAT keys).
  Those are acquisition blocks, not mathematical results (AGENTS rule 5), and I did not treat them as
  evidence either way.
- *cbb848's HQC-scale conclusion*: my far-tail cells use block lengths 20–50 against HQC's `n_2 ≈ 384`.
  Settled by extending the DP sweep in `n_2` at fixed density and confirming the NA deficit decays.

## One concrete next action

Route the six substantively defective records back to their generators with the specific
counter-computation attached, and gate the two that would otherwise consume compute:

**Hold `IDEA-20260808-b8e2d4` and `IDEA-20260808-76260d` from any producer slot until amended.**
b8e2d4's minimal test cannot produce its predicted contrast in any proposed cell (measured 1.15/0.99/0.99
against a predicted ~600) and its VARIANT 2 relation is a tautology; 76260d's reproduction gate is
provably unreachable (LP optimum 4 at r=4, so weak duality forbids any dual certifying 25). Both should
be superseded rather than run. The single highest-value amendment across the rest is to **e40da2**:
replace the claimed class-wide sample lower bound with the `(samples, FFT-size)` frontier, and re-state
the `N=160` baseline reproduction as "the balanced-memory point of the frontier reproduces 2^36, and the
minimum-sample point of the same frontier reproduces 2^24.85 — which is the other relayed published
row" — because that single sentence converts the record's weakest claim into its most useful one.
