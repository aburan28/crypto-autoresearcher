# H-PSEUDO: Mathematical Connection Analysis

**Task**: TASK-20260804-084  
**Batch**: BATCH-072  
**Goal**: GOAL-ECDLP-001  
**Decision context**: DEC-20260804-1b22b2 (BATCH-067: Weil bound blocked by DL circularity)  
**Recorded**: 2026-08-04

---

## Setup: the precise H-PSEUDO conjecture

Fix a prime-order elliptic curve `E/F_p` with `#E(F_p) = N` (N prime, N ≈ p), and
a generator `G ∈ E(F_p)`. Define:

```
F = { P ∈ E(F_p) : x(P) < t }    where t ~ B·p/N, so |F| ≈ B.
```

The discrete logarithm map `DL: E(F_p) → Z/N` sends `P = [n]G ↦ n`.

**H-PSEUDO**: For all `k ≢ 0 (mod N)`,

```
|hat{1_F}(k)| := |Σ_{P ∈ F} e^{2πi k·DL(P)/N}| ≤ C · √B
```

for a universal constant `C` independent of `p`, `E`, `G`, and `k`.

**Equivalent reformulation**: Let `f: Z/N → {0,1}` be the indicator `f(n) = 1_{x([n]G) < t}`.
Then `hat{1_F}(k) = Σ_{n=0}^{N-1} e^{2πikn/N} · f(n)` is simply the DFT of `f` in
the DLP-index variable `n`. H-PSEUDO says that the indicator of small-x points, viewed
as a subset of `Z/N` via the DLP, has Fourier coefficients of order `√B` — the same
as a uniformly random subset of size `B`.

**Why it matters**: Given H-PSEUDO, the Semaev relation yield satisfies

```
r(B, m) = B^m/(m! · N)  +  O(B^{m/2} / N^{m/2 - 1/2})
```

which makes the heuristic yield formula rigorous and closes the gap between empirical
observation (BATCH-062/063: EV-YIELD-e1adbf, EV-YIELD-ca4b02) and theory.

---

## Approach 1: Michel-Venkatesh equidistribution — does it apply?

### What Michel-Venkatesh proves

The Michel-Venkatesh paper (2010, Annals) establishes equidistribution of CM points and
Heegner points in Shimura varieties using ergodic methods and the theory of automorphic
L-functions. Birch (1968) established an earlier equidistribution result for rational
points on conics. Both results bound sums of the form:

```
Σ_{P ∈ S} f(P)
```

where `S` is a geometrically defined set (CM points, Heegner points, rational points on
an algebraic variety), and `f` is a **geometrically defined** function — a character of
the Galois representation, a Hecke eigenform value, or an algebraic function of the
coordinates.

### The fundamental obstruction

H-PSEUDO requires bounding `Σ_{P ∈ F} e^{2πi k·DL(P)/N}`. The character
`P ↦ e^{2πi k·DL(P)/N}` is **not a geometric function of P**. Specifically:

1. `DL(P)` is defined by `P = [DL(P)]·G`, which depends on the choice of generator `G`,
   the group structure of `E(F_p)`, and the solution to an NP-hard problem.
2. There is no rational map `ψ: E → G_m` (over `F_p` or its algebraic closure) such
   that `ψ(P) = e^{2πi k·DL(P)/N}`. If such a map existed, it would be an algebraic
   character of the elliptic curve group, which would factor through the group law —
   but `e^{2πi k·n/N}` for `n = DL(P)` is a character of the abstract group `Z/N`,
   and the group isomorphism `E(F_p) ≅ Z/N` is NOT an algebraic map (it is defined
   by counting and group structure, not by a polynomial).
3. The "equidistribution" Michel-Venkatesh proves is of geometric families in algebraic
   parameter spaces. The set `F = {P : x(P) < t}` is geometrically defined (a
   half-space in x-coordinate), but the weight function `e^{2πi k·DL(P)/N}` is not.

### The algebraic vs. non-algebraic distinction is sharp

The Weil bound and its generalizations (Deligne's theorem, Michel-Venkatesh) bound sums
of the form `Σ_{x ∈ V(F_p)} χ(F(x))` where:
- `V/F_p` is a variety.
- `F: V → A^1` is a rational map.
- `χ: F_p → C` is a character (additive or multiplicative).

The character `e^{2πi k·DL(P)/N}` does NOT factor as `χ(F(P))` for any algebraic `F`
and character `χ`, because `DL(P)` encodes the order of an element in an abstract group,
not a polynomial function of its coordinates.

### ECCG duality (what Weil CAN give)

The ECCG literature (Shparlinski and collaborators; KN-LIT-1769) does provide Weil-type
bounds for the DUAL sum:

```
Σ_{n=0}^{N-1} e^{2πi m·x([n]G)/p}    (additive character of x-coordinates)
```

By Weil bounds for elliptic curves:
```
|Σ_{P ∈ E(F_p)} e^{2πi m·x(P)/p}| ≤ C · √p
```

But H-PSEUDO asks for the **dual** in the DLP index:
```
Σ_{n: x([n]G) < t} e^{2πi k·n/N}      (additive character of DLP indices)
```

These are Fourier-dual objects. The Weil bound controls the x-coordinate DFT; H-PSEUDO
asks about the DLP-index DFT. Converting one to the other requires inverting the DLP map,
which is the ECDLP.

**Verdict**: Michel-Venkatesh does not apply to H-PSEUDO. The obstruction is categorical:
the sum involves a non-algebraic character, and no existing equidistribution theorem for
algebraic varieties handles non-algebraic weights.

---

## Approach 2: Mock characters — existence and applicability

### The mock character idea

Suppose there exists a function `f: E(F_p) → C`, computable from `(x(P), y(P))`,
such that `|f(P) - e^{2πi k·DL(P)/N}| ≤ ε` for all `P`. Then:

```
|Σ_{P ∈ F} e^{2πi k·DL(P)/N}| ≤ |Σ_{P ∈ F} f(P)| + ε · |F| = |Σ_{P ∈ F} f(P)| + εB
```

If `f` is algebraic (a rational function of `x(P), y(P)` over `F_p`), the Weil bound
applies to `|Σ_{P ∈ F} f(P)|`, potentially giving a `√B` bound. We need `εB ≪ √B`, i.e.,
`ε ≪ B^{-1/2}`.

### Why no mock character can achieve the required precision

**Computational hardness argument**: A function `f(x(P), y(P))` approximating
`e^{2πi k·DL(P)/N}` with precision `ε ≪ B^{-1/2}` per point would satisfy:

```
|arg(f(P)) / (2π) - k · DL(P)/N| ≤ ε / (2π)    (mod 1)
```

This determines `DL(P) mod N` up to `ε · N/(2πk)` ≈ `ε · N/k`. For `ε = B^{-1/2}` and
`B = p^δ`, this narrows DL(P) to an interval of length `N / (k · B^{1/2})`. For any
`k = O(1)` and `B = p^{δ}`, this is an interval of length `≈ p^{1-δ/2}`. Computing
f(x(P), y(P)) from coordinates without knowing the DLP would therefore constitute a
coarse DLP solver — contradicting ECDLP hardness.

**Information-theoretic argument**: The map `P ↦ DL(P)` is a bijection `E(F_p) → Z/N`.
For a fixed `k ≠ 0`, the character `e^{2πi k·DL(P)/N}` takes `N` distinct values as `P`
ranges over `E(F_p)`. For a function `f(x(P), y(P))` to approximate this with precision
`ε`, it must distinguish approximately `1/ε` bins among the DLP values. At precision
`ε = B^{-1/2}`, this requires `B^{1/2}` distinguishable values, meaning `f` encodes
`(log B)/2` bits of the DLP.

**Characteristic-0 construction and its limits**: Over `C`, the Weierstrass
parametrization `P = (℘(z), ℘'(z))` for `z ∈ C/Λ` does provide a "mock DLP"
approximation: `DL(P)/N ≈ Re(z) / Re(ω_1)` where `ω_1` is the real period. But:

1. This requires a lift of `E(F_p)` to `E(C)`, which is a non-canonical choice.
2. Different lifts give different DLP approximations; no canonical lift exists.
3. The Tate/p-adic Weierstrass parametrization (for curves with multiplicative reduction
   at p) gives a p-adic analog, but cryptographic ECDLP curves have **good** reduction
   at p, so no Tate curve structure is available.

**Verdict**: No mock character approach can work. Any function `f(x(P), y(P))` achieving
precision `ε ≪ B^{-1/2}` per point would be a partial DLP oracle, making its existence
equivalent to breaking ECDLP to logarithmic precision. The characteristic-0 construction
is non-canonical and non-algebraic. This approach does not give H-PSEUDO.

---

## Approach 3: Average-over-primes via L-functions

### The average-over-primes formulation

For a curve `E/Q` (with good reduction at most primes), define the average H-PSEUDO as:

```
(1/π(X)) Σ_{p ≤ X} |hat{1_{F_p}}(k_p)| ≤ C · √B
```

where `F_p = {P ∈ E(F_p) : x(P) < t_p}`, `B_p ≈ t_p · N_p / p`, and `k_p` is a
non-trivial character index.

Alternatively, the squared average:
```
(1/π(X)) Σ_{p ≤ X} (1/N_p) · |hat{1_{F_p}}(k_p)|² ≤ C
```

### What L-function methods can and cannot give

**Fouvry-Murty (1996)** proves the Lang-Trotter conjecture on average: for fixed `t`,
```
Σ_{p ≤ X} #{P ∈ E(F_p) : a_p(E) = t} ≈ C_t · X / log X
```
This concerns the distribution of `|E(F_p)|` across primes, not DLP values.

**Murty-Gupta** work (Ram Murty, Vijaya Kumar Gupta; 1980s–1990s) on DLP character sums
focuses on **multiplicative** characters of DLP values:
```
Σ_{P ∈ E(F_p)} χ(DL_p(P))
```
for Dirichlet characters χ. Their approach uses:
1. The Weil bound for multiplicative character sums on elliptic curves.
2. The factorization of `L(E ⊗ χ, s)` into Hecke L-functions.

H-PSEUDO requires an **additive** character `e^{2πi k·DL(P)/N}`, which is structurally
different. The L-function for additive characters of DLP would encode something like:
```
L(E/F_p, k) = Σ_{n=0}^{N-1} e^{2πi kn/N} · a_n(E)
```
where `a_n` encodes some invariant of the DLP-indexed point. No such L-function exists in
the standard automorphic forms framework.

### Sato-Tate and equidistribution of DLP indices

The Sato-Tate theorem (Taylor et al., 2011) gives equidistribution of `a_p / (2√p) = cos(θ_p)`
with the semicircle measure as `p` varies. This is equidistribution of the **trace of Frobenius**,
not equidistribution of DLP indices.

A "DLP Sato-Tate" statement would require: as `p` varies, the sequence `n ↦ x([n]G_p)/p`
equidistributes in `[0,1]` in a sense controlled by L-functions. This would be an analog
of the known equidistribution for **Frobenius eigenvalues**, but for **DLP orbits**. No
such result appears in the literature.

### ECCG discrepancy and the Erdős-Turán connection

The elliptic curve congruential generator (ECCG) theory (Shparlinski; see KN-LIT-1769)
provides the closest existing technology. The ECCG sequence is `x_n = x([n]G)/p ∈ [0,1]`
for `n = 0, ..., N-1`. The **discrepancy** of this sequence satisfies (by Weil bounds):

```
D_N := sup_{[a,b] ⊂ [0,1]} |#{n : x_n ∈ [a,b]}/N - (b-a)| ≤ C · p^{1/2+ε} / N
```

By the Erdős-Turán inequality:
```
D_N ≤ C/H + Σ_{m=1}^{H} (1/m) · |(1/N) Σ_{n=0}^{N-1} e^{2πi m · x_n}|
```

The character sums here are `e^{2πi m · x([n]G)/p}` (additive character of x-coordinate),
which the Weil bound controls.

H-PSEUDO asks about the **DUAL** discrepancy: the discrepancy of `{DL(P)/N : P ∈ F}` as
a subset of `[0,1]`. These are Fourier-dual objects. The ECCG bounds control the DFT of
the sequence in the **x-direction** (`m · x_n`); H-PSEUDO needs the DFT in the
**n-direction** (`k · n`). Converting one to the other requires the DLP map, and no
conversion technique is known.

### Can the squared average be proved unconditionally?

By the Parseval identity on `Z/N`:
```
Σ_{k=1}^{N-1} |hat{1_F}(k)|² = |F| · (N - |F|) / N = B(N-B)/N ≈ B
```

This is exact and unconditional. It shows the **average** of `|hat{1_F}(k)|²` over `k ≠ 0`
is `B/N · (N-B)/(N-1) < B`. So "most" Fourier modes satisfy `|hat{1_F}(k)| ≤ O(√B)`.
However, H-PSEUDO requires the bound for **all** `k ≠ 0` (a max bound, not an average).

For the average over primes of the max over `k`:
```
(1/π(X)) Σ_{p ≤ X} max_{k ≠ 0} |hat{1_{F_p}}(k)|
```

Parseval guarantees the RMS is `O(√B)` but says nothing about the maximum. A pointwise
max bound over k requires more: either that the Fourier spectrum of `1_F` is "flat"
(no single k dominates), or that the DLP indices of small-x points are pseudorandom.
Both are versions of H-PSEUDO, not consequences of currently known techniques.

**GRH-conditional**: Under GRH for all relevant Artin L-functions, the distribution
of Frobenius elements in division fields gives strong bounds on some EC point statistics.
However, DLP indices in `Z/N` are not directly encoded in Frobenius eigenvalues, and GRH
does not appear to give a uniform bound on `max_k |hat{1_F}(k)|` for the small-x factor base.

**Verdict**: The average-over-primes version of H-PSEUDO is likely not provable by current
L-function techniques. The Parseval identity gives an average-over-k bound unconditionally
but not the all-k bound H-PSEUDO needs. Fouvry-Murty and Murty-Gupta methods do not
apply because they concern different quantities (multiplicative characters, Frobenius
traces). The ECCG discrepancy literature provides the closest analog, but the dual
direction (DLP-index DFT) is out of reach.

---

## Overall assessment: Is H-PSEUDO a known open problem?

### Status

H-PSEUDO does not appear in the literature as a named conjecture. It is, however,
a precisely formulated statement whose content can be compared to known problems.

**What H-PSEUDO IS equivalent to (up to Parseval duality)**:

> The sequence `{DL(P)/N : P ∈ F}` (DLP indices of factor-base points, normalized)
> equidistributes in `Z/N` with discrepancy `O(1/√B)`.

Or equivalently: the DFT of the indicator function `1_F` on `Z/N` (where F is
identified with its set of DLP indices) has all non-trivial Fourier coefficients
bounded by `O(√B)`.

This is precisely a **DLP-discrepancy** statement for the factor base.

**Connection to ECCG discrepancy**: The ECCG discrepancy theory (Shparlinski,
Friedlander, Niederreiter; see KN-LIT-1769) studies the x-coordinate Fourier transform
of the DLP-index sequence. H-PSEUDO asks for the DLP-index Fourier transform of the
x-coordinate indicator. These are Fourier-dual problems; solving either by direct
algebraic methods requires the other as input.

**Connection to ECDLP hardness**: If H-PSEUDO were false for some specific `k` and `B`,
i.e., if `|hat{1_F}(k)| ≫ √B`, then the factor base `F` would be "structured" in `Z/N`
in a way that the Semaev yield deviates from heuristic. BATCH-062/063 yield measurements
(EV-YIELD-e1adbf, EV-YIELD-ca4b02) are empirically consistent with H-PSEUDO holding,
but this does not constitute a proof.

**The DL circularity obstruction (DEC-20260804-1b22b2)**: The reason H-PSEUDO cannot be
proved by classical methods is stated precisely in DEC-20260804-1b22b2: any bound on
`Σ_{P ∈ F} e^{2πi k·DL(P)/N}` must reference `DL(P)`, which is the unknown computed
by ECDLP. This is not a heuristic observation — it is a formal statement that the
character sum H-PSEUDO involves a non-algebraic function of P, making algebraic character
sum bounds inapplicable.

### Three independent non-applicability results

| Approach | Obstruction | Status |
|---|---|---|
| Michel-Venkatesh equidistribution | Character `e^{2πi k·DL(P)/N}` is non-algebraic; MV bounds algebraic characters only | Categorical non-applicability |
| Mock character approximation | Precision `ε ≪ B^{-1/2}` per point ⟹ partial DLP oracle; contradicts ECDLP hardness | Reduction to ECDLP |
| Average-over-primes L-functions | Parseval gives average-over-k bound; max-over-k bound requires ECCG dual not in reach; Fouvry-Murty/Murty-Gupta concern different quantities | Out of current reach |

### Is H-PSEUDO implied by any known conjecture?

- **Birch-Swinnerton-Dyer**: No. BSD concerns ranks and L-values, not DLP indices.
- **Sato-Tate**: No. ST concerns trace of Frobenius distribution, not DLP structure.
- **Lang-Trotter**: No. LT concerns primes with specified Frobenius trace, not DLP values.
- **Generalized Riemann Hypothesis**: No direct implication. GRH for Artin L-functions
  controls Frobenius distribution in division fields, but DLP indices in `E(F_p)` are
  not encoded in those L-functions.
- **Extended Artin conjecture (Murty-Gupta)**: Gives results for multiplicative
  characters of DLP, not additive characters. Extension to additive characters is open.
- **ECDLP pseudorandomness assumptions** (informal): H-PSEUDO is a precise mathematical
  formulation of "DLP values of small-x points are pseudorandom." It is logically
  independent from ECDLP hardness (hardness says no efficient algorithm; H-PSEUDO says
  the specific character sum is small) but is in the same spirit.

### Precise boundary of current techniques

The program has precisely located the boundary:

```
PROVED:        Weil bound → algebraic character sums → bounds on Σ_P χ(x(P))
BLOCKED:       Weil bound → DLP character sums → H-PSEUDO
REASON:        DL(P) is not algebraic over F_p; the isomorphism E(F_p) ≅ Z/N is
               defined by group theory, not by a rational map.
NEW TECHNIQUE: H-PSEUDO ⟺ a bound for the ECCG-dual character sum; proving this
               would require either a fundamentally new algebraic geometry input
               (expressing DLP via a geometric object) or an analytic number theory
               advance connecting DLP orbits to automorphic L-functions.
```

---

## Proposed next step

### Immediate (this task cycle)

Record H-PSEUDO as a precisely stated open problem in the knowledge corpus:

1. **Formulate the ECCG dual connection** as a knowledge item:
   H-PSEUDO ⟺ DLP-index discrepancy for the ECCG sequence ⟺ bounding the DFT of
   `n ↦ 1_{x([n]G) < t}` at non-zero frequencies. This gives a concrete research target:
   prove or disprove that the ECCG sequence has this dual property.

2. **Record the three non-applicability results** as a closure record (with named
   obstructions, arguments, and forward guidance — as per KN-TECH-056 §7 standard).

### Potentially tractable successor (new mechanism search)

The dual ECCG formulation suggests a concrete, falsifiable research direction:

- **Small-scale experiment**: For small `p` (e.g., `p ∼ 10^4–10^6`), directly measure
  `max_{k ≠ 0} |hat{1_F}(k)|` for random curves and factor bases, and compare to
  `C · √B`. If the max consistently tracks `√B` with a small constant `C`, this
  strengthens the empirical support for H-PSEUDO and gives an estimate of `C`.
  
- **Conditional approach**: Is H-PSEUDO implied by (or equivalent to) any known
  assumption in computational number theory (e.g., the hardness of distinguishing
  x-coordinate distributions, or a random oracle assumption for the DLP map)?
  A conditional proof of H-PSEUDO from a standard cryptographic assumption would be
  a significant theoretical finding even if the assumption is not proved.

- **Moment approach**: Rather than bounding `max_k |hat{1_F}(k)|`, can the second
  moment `(1/N) Σ_k |hat{1_F}(k)|^2 = B(N-B)/N` (trivially) be sharpened to a fourth
  moment bound `(1/N) Σ_k |hat{1_F}(k)|^4 ≤ C · B^2`? A sub-Gaussian fourth moment
  would imply a max bound by standard large-deviation arguments. The fourth moment
  involves counting `|{(P_1, P_2, P_3, P_4) ∈ F^4 : DL(P_1) + DL(P_2) = DL(P_3) + DL(P_4)}|`,
  which is the additive energy of the factor base in `Z/N`. This is directly related
  to the sumset `F + F` in `Z/N`, a combinatorial quantity potentially accessible via
  Fourier methods if DLP structure is invoked.

### Research disposition

H-PSEUDO should be recorded as:
- Status: `proposed` (falsifiable conjecture, not hypothesis — it is a mathematical statement
  about a specific quantity, not a claim about a mechanism for breaking ECDLP)
- Evidence: empirical support from BATCH-062/063 yield measurements
- Obstructions to proof: DL circularity (DEC-20260804-1b22b2), confirmed by three independent
  non-applicability results above
- Value: the gap between empirical yield and rigorous bound reduces EXACTLY to H-PSEUDO;
  proving it would be a genuine theoretical advance separating "empirically random DLP"
  from "provably random DLP"

---

## Summary of findings

1. **H-PSEUDO is not equivalent to any known conjecture in number theory**. It is a
   new, precisely stated statement about the distribution of DLP values of structured
   EC point sets. It resembles ECCG discrepancy in a dual form but does not follow from
   known ECCG bounds.

2. **The average-over-primes version (Approach 3) is the most accessible but still
   out of reach**. The Parseval identity gives the average-over-k version unconditionally;
   the max-over-k version (which is what H-PSEUDO requires) needs a new connection
   between DLP orbits and automorphic L-functions that does not currently exist.

3. **There are indirect approaches but none that avoid the DL circularity**:
   - The ECCG dual formulation is precise and measurable.
   - A conditional proof from computational assumptions is plausible.
   - A fourth-moment / additive-energy approach might give partial progress.
   - No algebraic geometry technique (Weil, Michel-Venkatesh, Katz-Sarnak) applies because
     all such techniques require algebraic characters, and the DLP character is non-algebraic.

4. **The DL circularity obstruction** (DEC-20260804-1b22b2) is confirmed to be the
   fundamental barrier. It is not an artifact of a specific method but a structural
   property: any bound on the DLP character sum must reference DL(P), which is the
   quantity ECDLP asks to compute.

---

*Artifact status: mathematical analysis, no computation performed, no fabricated results.  
Authority: analyst-role, under Coordinator direction.  
Claim tier: theory, not validated by experiment.*
