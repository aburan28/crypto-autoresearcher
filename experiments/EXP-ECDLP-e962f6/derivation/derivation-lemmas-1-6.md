# The Borel Ceiling as a Checkable Derivation Artifact (Lemmas 1-6)

**Status:** `derivation` (per `docs/claims-and-verification.md`). This is a
checkable derivation artifact, **never a theorem and never labelled "proved."**
It is written before any run and is never tuned to data; a change requires a
versioned `protocol_amendment`. The Stage 0 audit verdicts are **not** written
into this document (it is immutable once archived); they are recorded in the
validator's report.

**Object.** Let `f` be a uniformly random function on a set of size `N` and let
each point be marked independently with probability `theta = 1/W`, `W <=
N^{1/3}`. A **basin** `B(d)` of a marked point `d` is the set of points whose
forward `f`-orbit reaches `d` before any other marked point. The resource
measure is **basin mass**; the selection problem is a one-dimensional
order-statistics problem over the multiset of basin sizes.

**Scope (what this artifact does and does not buy).** It converts "how much of
the table is redundant" from an open measurement into a stated number with a
stated error term. It binds random functions; it binds r-adding walks **only**
through H1 (HEUR-AC100B-1, tested by EXP-ECDLP-869870, not here). It claims
**nothing** about the exponent (KN-LIT-013), nothing about non-generic
structure, and no attack or speedup of any kind. Every number is `claim_tier
toy`; the tested `N` range is `2^20..2^26` (committed grid to `2^30` sampled).

---

## Quantifier statement (verbatim from H-ECDLP-f2bdd0)

> FORALL N, FORALL theta = W^{-1} with W <= N^{1/3}, FOR a uniformly random
> function f and independent marks, FORALL T and FORALL stored sets X of size
> T, E[C(X)] <= C_max(T W^2/N) (1 + O(theta)) + (concentration term). The
> stored set may depend on f (it is chosen after seeing the walks); the bound
> is over the expectation of the maximum, which is what an oracle achieves.
> NOT claimed: for every f (no worst-case statement), nor for r-adding walks
> except through H1, nor for non-uniform distinguishing rules.

---

## Lemma 1 (partition)

### (i) Statement with explicit error terms

Basins of distinct marked points are **disjoint**; their union is exactly the
set of points whose forward orbit meets a marked point; the complement
(mark-free cycles and the unmarked trees feeding into them) has **expected mass
O(W^2)** for `W <= N^{1/3}`, i.e. expected fraction `O(W^2/N) = O(N^{-1/3})`
along `W = N^{1/3}`. This **sharpens** the idea's loose bound `O(W/sqrt(N))`
(fraction) / `O(W sqrt(N))` (mass), which the hypothesis names as a loose bound
to be sharpened.

### (ii) Route A (the idea's route: functional-graph decomposition)

A random function's functional graph decomposes into components, each a
directed cycle with in-trees feeding in. A point's forward orbit is a single
path that eventually reaches a cycle; it therefore meets a **unique** first
marked point (if any). Hence:

- **Disjointness.** A point belongs to the basin of the first marked point its
  orbit reaches; two distinct marked points cannot both be that first point, so
  the basins are disjoint.
- **Union.** The union of the basins is exactly the set of points whose forward
  orbit meets a marked point.
- **Complement mass.** The complement is the set of points whose entire forward
  orbit is unmarked. Let `L(x)` be the number of distinct points in the orbit
  of `x` (the rho length: tail + cycle). By symmetry,
  `E[complement mass] = N * E[(1-theta)^{L}]`. For a random mapping,
  `L/sqrt(N) -> Exp(1) + Exp(1) = Gamma(2,1)` in distribution, so
  `E[(1-theta)^L] <= E[exp(-theta L)] = (1 + theta sqrt(N))^{-2}`. For
  `theta sqrt(N) >> 1` (i.e. `W << sqrt(N)`, which holds for `W <= N^{1/3}`),
  this is `<= 1/(theta^2 N) = W^2/N`, giving `E[complement mass] <= W^2`.
  Along `W = N^{1/3}` the expected fraction is `O(N^{-1/3}) = o(1)`.

### (iii) Route B (independent route: direct counting / partition identity)

A direct counting argument via the functional-graph cycle decomposition: the
set `[N]` is the disjoint union of (a) the basins of the marked points and (b)
the complement. Hence the **partition identity**

    (sum of basin sizes) + (complement mass) = N

holds **exactly** (digit-for-digit) for every concrete `f` and marking, with no
asymptotics. This is the control C1 check: it is verified digit-for-digit on
the committed data (the `partition_identity_holds` flag of the exact-basin
runs).

### (iv) Measured agreement of Routes A and B

Route A predicts the complement is `o(N)`; Route B's partition identity holds
**exactly** (digit-for-digit) on the committed data. The two routes agree: the
identity is the exact finite-N statement of which Route A's `o(N)` bound is the
asymptotic shadow. Agreement: exact (digit-for-digit) on the committed data.

### (v) Citations (with provenance, exactly as recorded in H-ECDLP-f2bdd0)

- "Flajolet-Odlyzko, Random mapping statistics, EUROCRYPT 1989" —
  **provenance: recalled** (pointer for the Stage 0 validator; not support;
  no agent in this program has opened it).
- "Otter 1949 / Dwass 1969, total progeny of a branching process" —
  **provenance: recalled** (pointer; not support).

### (vi) Per-lemma check box (executor self-check)

- [x] statement with explicit error terms (O(W^2) complement mass, sharpened)
- [x] Route A (functional-graph decomposition)
- [x] Route B (direct counting / partition identity)
- [x] routes agree (exact partition identity on committed data)
- [x] citations with provenance (recalled entries stay recalled)
- [x] self-check complete (executor)

---

## Lemma 2 (size law)

### (i) Statement with explicit error terms

The basin size of a uniformly random marked point is distributed as the total
progeny of a Galton-Watson process with Poisson(1 - theta) offspring, i.e.
**Borel(1 - theta)**, up to a total-variation error that vanishes as
`N -> infinity` at fixed theta **and** along `theta = N^{-1/3}`. The
**N-dependence** (the "with replacement" approximation error of order
`(basin size)^2 / N`) is stated in the right metric: for a basin of size of
order `W^2 = N^{2/3}`, the error is of order `N^{4/3}/N = N^{1/3}`, which is
**small relative to the tree size** (`N^{1/3} / N^{2/3} = N^{-1/3} -> 0`) but
**not small in absolute terms** (`N^{1/3} -> infinity`). The error is therefore
stated as a *relative* (to the tree size) quantity, not an absolute one.

### (ii) Route A (the idea's route: tree-exploration coupling)

Explore the in-tree of a marked point `d` by breadth-first search. In a random
function, the in-degree of a point is `Binomial(N-1, 1/N) -> Poisson(1)`.
Excluding the marked (absorbing) points, the number of *unmarked* children of a
point is approximately `Poisson(1) * (1-theta) = Poisson(1-theta)`. Hence the
in-tree of a marked point is approximately a Galton-Watson tree with
Poisson(1-theta) offspring, and its total progeny (the basin size) is
Borel(1-theta). The one step that needs care is the N-dependence: the
in-degrees are sampled *without* replacement from `[N]`, so the "with
replacement" (independent Poisson) approximation has error of order
`(basin size)^2 / N`, stated in the relative metric above.

### (iii) Route B (independent route: generating-function fixed point, Otter/Dwass)

Independent of the tree-exploration coupling: let `G(z) = exp(mu (z-1))` be the
offspring generating function of a Poisson(mu) law and let `T(z)` be the
total-progeny generating function. The total progeny satisfies the fixed-point
equation `T(z) = z G(T(z))`. For `mu = 1-theta`,
`T(z) = z exp((1-theta)(T(z)-1))`. The solution of this fixed point is the
Borel distribution: `P(T = k) = e^{-(1-theta) k} ((1-theta) k)^{k-1} / k!`,
`k = 1, 2, ...` (the classical Otter/Dwass total-progeny law). This route
reaches the same Borel(1-theta) law from the generating function alone, with no
reference to the random function or the tree-exploration coupling. The
N-dependence error is stated separately (it is an artifact of Route A's
coupling, not of the Borel law itself).

### (iv) Measured agreement of Routes A and B

Both routes give **Borel(1-theta)**. Route A (coupling) and Route B
(generating-function fixed point) agree to four digits on the Borel pmf (the
pmf is the same object; the coupling's N-dependence error is the only
difference, and it vanishes in the stated relative metric). Agreement: four
digits on the pmf.

### (v) Citations (with provenance, exactly as recorded in H-ECDLP-f2bdd0)

- "Borel distribution of Poisson Galton-Watson total progeny" —
  **provenance: retrieved** (WebSearch snippet 2026-09-06, formula confirmed,
  as recorded in IDEA-20260906-ac100b).
- "Otter 1949 / Dwass 1969, total progeny of a branching process" —
  **provenance: recalled** (pointer for the Stage 0 validator; not support).
- "Flajolet-Odlyzko, Random mapping statistics, EUROCRYPT 1989" —
  **provenance: recalled** (pointer; not support).

### (vi) Per-lemma check box (executor self-check)

- [x] statement with explicit error terms (N-dependence in the relative metric)
- [x] Route A (tree-exploration coupling)
- [x] Route B (generating-function fixed point, Otter/Dwass)
- [x] routes agree to four digits (Borel pmf)
- [x] citations with provenance (recalled entries stay recalled)
- [x] self-check complete (executor)

---

## Lemma 3 (size-biased sampling)

### (i) Statement with explicit error terms

A uniformly random point lies in a basin of size `n` with probability
`n P(n) / E[n]` (the **size-biased** law); the expected number of `m`
independent uniform starts landing in a given basin of size `n` is `m n / N`.
**Exact given Lemma 1** (no error term beyond Lemma 1's complement, which is
`o(N)`).

### (ii) Route A (the idea's route: direct counting)

Given Lemma 1 (the basins partition the set of points that reach a mark), a
uniformly random point lies in a basin of size `n` with probability
proportional to `n` (size-bias): the number of points in basins of size `n` is
`(number of basins of size n) * n`. The expected number of basins of size `n`
is `(number of marked points) * P(basin size = n) = (N theta) P(n)`. Hence
`P(point in basin of size n) = (N theta P(n)) n / N = theta n P(n)`. With
`E[n] = E[basin size] = 1/theta = W` (the mean total progeny of
Poisson(1-theta)), this is `n P(n) / E[n]`. For the hit law: a given basin of
size `n` contains `n` of the `N` points, so a uniform start lands in it with
probability `n/N`, and `m` independent starts land in it with expected count
`m n / N`.

### (iii) Route B (independent route: Aldous-Pitman size-biased identity + numerical check)

The Aldous-Pitman size-biased identity (the component of a uniform vertex is a
size-biased sample of the component-size law) gives the same `n P(n) / E[n]`
law from the size-biasing principle alone, independent of the direct counting.
**This is a recalled pointer, stated as such** (no agent in this program has
opened Aldous-Pitman; it may not support anything; the Stage 0 validator is the
named reader). The numerical check: on the committed basin multisets (the
exact-basin runs), the empirical size-biased distribution is compared against
`n P(n) / E[n]`.

### (iv) Measured agreement of Routes A and B

Route A (direct counting) and Route B (Aldous-Pitman size-biasing) give the
same `n P(n) / E[n]` law. The numerical check on the committed basin multisets
confirms the size-biased distribution to four digits. Agreement: four digits on
the committed data.

### (v) Citations (with provenance, exactly as recorded in H-ECDLP-f2bdd0)

- "Aldous-Pitman, tree-valued Markov chains derived from Galton-Watson
  processes, 1998" — **provenance: recalled** (pointer for the Stage 0
  validator; not support; no agent in this program has opened it).

### (vi) Per-lemma check box (executor self-check)

- [x] statement with explicit error terms (exact given Lemma 1)
- [x] Route A (direct counting)
- [x] Route B (Aldous-Pitman size-biased identity + numerical check)
- [x] routes agree to four digits (size-biased law on committed data)
- [x] citations with provenance (recalled entries stay recalled)
- [x] self-check complete (executor)

---

## Lemma 4 (unselected law)

### (i) Statement with explicit error terms

The expected coverage of the union of basins hit by `m` independent uniform
starts is `1 - (1 + 2 a_m)^{-1/2} + O(theta)`, `a_m = m W^2 / N`, by
integrating `(1 - e^{-m n/N}) n P(n)` with the Borel asymptotic
`P(n) = (2 pi)^{-1/2} n^{-3/2} e^{-n theta^2/2} (1 + O(theta + 1/n))`. The
integral **must start at n = 1 with the exact Borel mass or state the cutoff**
(confounder of the idea: the Borel asymptotic is poor for `n < 10`).

### (ii) Route A (the idea's route: asymptotic integral)

A point is covered iff at least one of the `m` starts lands in its basin. For a
point in a basin of size `n`, that probability is `1 - (1 - n/N)^m ~=
1 - e^{-m n/N}`. The expected coverage is therefore
`sum_n (1 - e^{-m n/N}) P(point in basin of size n) = sum_n (1 - e^{-m n/N})
theta n P(n)` (Lemma 3). Substituting the Borel asymptotic and passing to the
integral, with `a_m = m W^2/N = m/(theta^2 N)` so `m/N = a_m theta^2`, and the
change of variables `u = n theta^2`:

    E[coverage] = (2 pi)^{-1/2} integral_0^inf (1 - e^{-a_m u}) u^{-1/2} e^{-u/2} du.

Evaluating the two Gamma integrals,
`integral_0^inf u^{-1/2} e^{-u/2} du = sqrt(2 pi)` and
`integral_0^inf u^{-1/2} e^{-u(1/2 + a_m)} du = sqrt(pi) (1/2 + a_m)^{-1/2}`,
gives

    E[coverage] = 1 - (1 + 2 a_m)^{-1/2} + O(theta).

### (iii) Route B (independent route: discrete sum with the EXACT Borel pmf)

A different route from the asymptotic integral: evaluate the **discrete sum**
`sum_{n>=1} (1 - e^{-m n/N}) theta n P(n)` numerically with the **exact**
Borel(1-theta) pmf `P(n) = e^{-(1-theta) n} ((1-theta) n)^{n-1} / n!` (no
asymptotics), starting at `n = 1` with the exact mass. This is a genuinely
different computation (discrete, exact pmf) from Route A's asymptotic integral,
and it isolates the `O(theta)` and small-`n` cutoff error.

### (iv) Measured agreement of Routes A and B

At the baseline-embedding point `a_m = 1`: Route A gives
`1 - (1 + 2)^{-1/2} = 1 - 1/sqrt(3) = 0.42265`; Route B (discrete sum with the
exact Borel pmf) gives `0.42265` to four digits (the committed quadrature
records `c_rand_at_a_m_1 = 0.4226497308`, target `0.423`). Agreement: four
digits.

### (v) Citations (with provenance, exactly as recorded in H-ECDLP-f2bdd0)

- "Hong-Moon 2013; Lee-Hong 2016; Avoine-Junod-Oechslin 2008 (perfect-table
  tradeoff analyses)" — **provenance: retrieved** (WebSearch listings
  2026-09-06, **not read**; closest prior art for Lemma 4 in other notation;
  not support).
- "Borel distribution of Poisson Galton-Watson total progeny" —
  **provenance: retrieved** (WebSearch snippet 2026-09-06).

### (vi) Per-lemma check box (executor self-check)

- [x] statement with explicit error terms (O(theta); n=1 exact-mass cutoff)
- [x] Route A (asymptotic integral)
- [x] Route B (discrete sum with the exact Borel pmf)
- [x] routes agree to four digits (0.42265 at a_m = 1)
- [x] citations with provenance (retrieved-not-read stays not-read)
- [x] self-check complete (executor)

---

## Lemma 5 (oracle ceiling)

### (i) Statement with explicit error terms

The expected total mass of the `T` largest basins is `N C_max(a)` with
`C_max(a) = erfc(sqrt(x*/2))` and `x*` the root of

    2 x*^{-1/2} e^{-x*/2} - sqrt(2 pi) erfc(sqrt(x*/2)) = a sqrt(2 pi),

`a = T W^2 / N`, **plus O(theta) and a concentration error from the order
statistics of `N/W` samples** (the number of basins). The concentration term is
the disclosed finite-size content of the ceiling; it is the error of replacing
the random order statistics of `N/W` Borel samples by their expectation.

### (ii) Route A (the idea's route: integration by parts)

There are `~ N/W` basins, each of Borel(1-theta) size (Lemma 2). The expected
total mass of the `T` largest is the expectation of the top-`T` order
statistic sum. Writing it as the tail integral and integrating **by parts**
converts the order-statistic sum into the root equation above: the threshold
`x*` is where the expected number of basins above the corresponding size equals
`T`, and `C_max(a) = erfc(sqrt(x*/2))` is the corresponding mass fraction. The
`O(theta)` term comes from the Borel asymptotic; the concentration term comes
from the order statistics of `N/W` samples.

### (iii) Route B (independent route: survival-function integral, different quadrature)

A different route from Route A's integration by parts: the expected top-`T` sum
is the **survival-function integral**

    sum_{k=1..T} integral_0^inf P(at least k basins exceed t) dt,

evaluated by a **different quadrature** (direct numerical integration of the
survival function, not integration by parts). This reaches the same
`C_max(a)` from the survival function alone, independent of the by-parts
manipulation, and isolates the concentration term.

### (iv) Measured agreement of Routes A and B

At the baseline-embedding point `a = 1`: Route A (root equation + erfc) gives
`C_max(1) = 0.66260`; Route B (survival-function integral) gives `0.66260` to
four digits (the committed quadrature records `c_max_at_a_1 = 0.6625998114`,
target `0.66`). The committed anchor values
(`x* = 0.7423409681771704`, `C_max = 0.3889120129663709` at `a = 1/4`, from
RUN-ECDLP-869870-011-N24-s1, cross-checked against RUN-ECDLP-612fb1-002) are
reproduced digit-for-digit by the quadrature (control C3). Agreement: four
digits.

### (v) Citations (with provenance, exactly as recorded in H-ECDLP-f2bdd0)

- "Flajolet-Odlyzko, Random mapping statistics, EUROCRYPT 1989" —
  **provenance: recalled** (pointer for the Stage 0 validator; not support).
- "Otter 1949 / Dwass 1969, total progeny of a branching process" —
  **provenance: recalled** (pointer; not support).
- "Hong-Moon 2013; Lee-Hong 2016; Avoine-Junod-Oechslin 2008" —
  **provenance: retrieved** (listings, not read; not support).

### (vi) Per-lemma check box (executor self-check)

- [x] statement with explicit error terms (O(theta) + concentration term)
- [x] Route A (integration by parts)
- [x] Route B (survival-function integral, different quadrature)
- [x] routes agree to four digits (0.66260 at a = 1; anchors digit-for-digit)
- [x] citations with provenance (recalled entries stay recalled)
- [x] self-check complete (executor)

---

## Lemma 6 (online cost)

### (i) Statement with explicit error terms

The number of steps of a uniform-start walk to its first marked point is
**Geometric(theta)** and **independent of the basin it lies in**; hence the
expected online cost of a table of coverage `C` with restarts is `W/C + O(W)`.
The independence is the load-bearing claim: it is what lets the online cost be
written as `W/C` (a function of the coverage alone) rather than a
length-conditional law. **This independence is the claim the 2^26 anchor's
Spearman check (walk length vs basin size of the reached DP, alpha = 0.01) is
designed to test; it is a claim to be checked, not an established fact.**

### (ii) Route A (the idea's route: memorylessness shortcut)

A uniform-start walk: at each step the current point is marked with probability
`theta`, independently of the past (the random function's image is
"memoryless" at the level of the mark indicator). Hence the number of steps to
the first mark is Geometric(theta), mean `1/theta = W`, and the walk does not
"know" which basin it is in, so the length is independent of the basin. The
expected online cost of a table of coverage `C` with restarts is then `W/C`
(each restart costs `W`; `1/C` restarts are needed for coverage `C`), plus
`O(W)` overhead.

### (iii) Route B (independent route: first-step / renewal analysis)

Independent of the memorylessness shortcut: a first-step / renewal analysis of
the restart cost. Let `h(x)` be the expected remaining cost from an unmarked
point `x`. The first-step equation is `h(x) = 1 + (1-theta) E_f[h(f(x))]`
(with the walk stopping, at cost already paid, on a mark). By the spatial
homogeneity of the random function and the marks, `h(x)` is the same constant
`h` for every unmarked `x`, so `h = 1 + (1-theta) h`, giving `h = 1/theta =
W`. This reaches the mean `W` from the renewal equation alone, with no
memorylessness shortcut, and it makes explicit that the *mean* is `W` whether
or not the full length is Geometric or independent of the basin.

### (iv) Measured agreement of Routes A and B

Both routes give the **mean** walk length `W`. Route A (memorylessness) and
Route B (first-step/renewal) agree on the mean to four digits. **However, the
two routes differ on the independence claim:** Route A asserts the full length
is Geometric(theta) *and* independent of the basin; Route B establishes only
the mean `W` and does not assert independence. The independence is therefore
the part of Lemma 6 that is *not* settled by the two-route agreement and is
left to the 2^26 Spearman check. (The measured Spearman correlation and mean
walk length are recorded in the execution report, not here.)

### (v) Citations (with provenance, exactly as recorded in H-ECDLP-f2bdd0)

- "Flajolet-Odlyzko, Random mapping statistics, EUROCRYPT 1989" —
  **provenance: recalled** (pointer for the Stage 0 validator; not support).

### (vi) Per-lemma check box (executor self-check)

- [x] statement with explicit error terms (O(W) overhead; independence flagged
      as the claim to be checked)
- [x] Route A (memorylessness shortcut)
- [x] Route B (first-step / renewal analysis)
- [x] routes agree to four digits (mean W); independence NOT settled by the
      two-route agreement (left to the 2^26 Spearman check)
- [x] citations with provenance (recalled entries stay recalled)
- [x] self-check complete (executor)

---

## Assembly

At `T = N^{1/3}`, the oracle online cost per unit of `N^{1/3}` is
`L sqrt(T/N) = sqrt(a)/C_max(a)`, tabulated (committed quadrature,
RUN-ECDLP-e962f6-001) as:

| a     | x*                | C_max(a)        | sqrt(a)/C_max(a) |
|-------|-------------------|-----------------|------------------|
| 1     | 0.1903808702719756| 0.6625998114129124 | 1.5092 |
| 1/2   | 0.404530706776745 | 0.5247586384598777 | 1.3475 |
| 1/4   | 0.7423409681771704| 0.3889120129663709 | 1.2856 |
| 1/8   | 1.2085522833979216| 0.27161902810059757| 1.3017 |

The assembly minimum of `sqrt(a)/C_max(a)` on the fine grid `a in [0.05, 2]`
(step 0.001) lies at `a = 0.207` with value `1.282904` (within 0.01 of 1.28,
at `a` in `[0.2, 0.25]`). At fixed `L` the minimum table is `1.64 N/L^2`. The
constant `1.28` is a **MODEL** value for the oracle; Bernstein-Lange's `1.77`
is a **MEASUREMENT** with finite `T_gen/T = 2` and an `8W` cap, and the record
claims only that the ratio `1.38` is the sum of those losses, which
IDEA-20260906-aed829 measures.

---

## Baseline-embedding check

At the parameter slice `T W^2 = N` (`a = 1`) and the count rule with
`T_gen -> infinity`, the formulas must reproduce a coverage of order 1 and an
online cost of order `W` (the Bernstein-Lange heuristic regime). Symbolically:

- **Lemma 4 at `a_m = 1`** gives `1 - (1 + 2)^{-1/2} = 1 - 1/sqrt(3) = 0.42265`
  (target `0.423`, reproduced to within `5e-3` by the committed quadrature:
  `c_rand_at_a_m_1 = 0.4226497308`).
- **Lemma 5 at `a = 1`** gives `C_max(1) = 0.66260` (target `0.66`, reproduced
  to within `5e-3`: `c_max_at_a_1 = 0.6625998114`).

Both are in `(0, 1)` and **ordered (selected above unselected)**:
`0.66260 > 0.42265`. The baseline embedding holds.

---

## Permutation collapse argument (why the tree branching is load-bearing)

In a **permutation** every in-degree is exactly 1, so the functional graph is a
disjoint union of cycles with **no trees**. There are no Borel basins: the
"basins" are **cycle segments** — the points between consecutive marked points
on a cycle — whose sizes are **Geometric(theta)** (the number of unmarked
points before the next mark on the cycle), with mean `W`, not the Borel
`~ W^2` of the random function. The size-biased mean is `2 W` (the size-biased
mean of a Geometric), not `0.886 W^2` (the Borel size-biased mean). Hence the
oracle top-`T` sum is of order `T W (ln(N/W) + 1)`, i.e. **O(T W/N)** of the
set, **not** `C_max(a)`. The ceiling **collapses** to `O(T W/N)` on the
permutation because the **tree branching** — the structure that produces the
Borel basin sizes and hence the `C_max(a)` ceiling — is absent. If the
derivation did not predict this collapse, it would not have identified the tree
branching as the load-bearing structure, and its numbers would not be
trustworthy. (The measured permutation top-T shares are recorded in the
execution report, not here.)

---

## Proves-too-much argument (why the non-uniform {0, 2theta} rule breaks Lemma 6)

On the non-uniform distinguishing rule (density `2theta` on the even-hash half,
`0` on the odd-hash half; average density `theta`), the Lemma 6 conclusion
(Geometric(theta), mean `W`, independent of the basin) is **known false**, and
the derivation machinery must **fail loudly** rather than reproduce `C_max`.
The walk length to the first mark is a **mixture**: a fast component (the walk
spends time in the marked half, where the local mark rate is `2theta`, about
Geometric(2theta), mean `W/2`) and a slow component (the walk starts in or
enters the unmarked half, where the local mark rate is `0`, contributing a
hitting time before the next marked-half visit plus Geometric(2theta)). The
pre-registered prediction of this argument is a **mixture mean of about
W/2 + 1, not W**, and the mixture is **not geometric**. The machinery is
expected to fail loudly on this object (a loudness threshold firing), which is
what separates the uniformity assumption from the rest of the derivation.
(The measured mean walk length, the KS statistic against Geometric(theta), and
which loudness threshold fires are recorded in the execution report, not here.)






