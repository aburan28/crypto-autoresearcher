# Weil Bound Yield Upper Bound for Semaev Index Calculus

**Task**: TASK-20260804-073  
**Batch**: BATCH-067  
**Role**: Mathematical Analyst  
**Decision context**: DEC-20260804-f320c2 (BGS closed, Weil bound direction proposed)  
**Recorded**: 2026-08-04

---

## Setup

### The objects

Let `E` be a prime-order elliptic curve over `F_p` with `#E(F_p) = N` prime, `N ≈ p`
(so `E(F_p) ≅ Z/N`).

**Arithmetic factor base**:
```
F = {P ∈ E(F_p) : x(P) < t}   for threshold t = B_frac × p
```
By Hasse's theorem / Weil equidistribution, `|F| = B` where
`B ≈ 2 B_frac × N` with an `O(√p)` correction. This is the only place the Weil
bound is directly useful; see §3.

**Semaev m=2 yield for a uniformly random target** `T ∈ E(F_p)`:
```
Yield(T) := #{(P₁, P₂) ∈ F² : P₁ + P₂ = T} = r(T)
```
`r(T) > 0` means `T` is decomposable over `F`. The heuristic prediction is
`E[r(T)] = B²/N` (trivially correct by counting).

**The question**: does the Weil bound imply the POINTWISE inequality
`r(T) ≤ B²/N + (small)` for all `T`?

### Identification with Z/N

Fix a generator `G` of `E(F_p)`. Every point `P` has a **discrete log**
`DL(P) ∈ Z/N` defined by `P = DL(P) · G`. The group isomorphism `E(F_p) ≅ Z/N`
maps EC addition to integer addition mod `N`.

Under this identification:
- `F` corresponds to `S := {DL(P) : P ∈ F} ⊆ Z/N` (a set of `B` residues mod `N`)
- `r(T)` for `T ↔ τ = DL(T)` equals the **additive representation count**:
  `r(τ) = #{(s₁, s₂) ∈ S² : s₁ + s₂ ≡ τ (mod N)}`
- `F + F` in `E(F_p)` corresponds to the **sumset** `S + S` in `Z/N`

The entire yield question reduces to: how is `r(τ)` distributed as `τ` varies over
`Z/N`?

---

## Fourier analysis of the indicator function F+F

### Fourier transform on Z/N

For any function `f : Z/N → C`, its discrete Fourier transform is:
```
f̂(k) = Σ_{s ∈ Z/N} f(s) e^{2πi ks/N}    (k = 0, 1, ..., N-1)
```

For the indicator `1_S` of `S ⊆ Z/N`:
```
1̂_S(k) = Σ_{s ∈ S} e^{2πi ks/N}
```

**Key Fourier identity for the representation count:**

The convolution theorem gives:
```
r(τ) = (1_S * 1_S)(τ) = (1/N) Σ_{k=0}^{N-1} [1̂_S(k)]² e^{-2πi kτ/N}
```

Separating the `k = 0` term:

```
r(τ) = B²/N  +  (1/N) Σ_{k=1}^{N-1} [1̂_S(k)]² e^{-2πi kτ/N}
       ────────   ──────────────────────────────────────────────
       heuristic         error term E(τ)
```

The heuristic `B²/N` is exact as an *average* (it is the `k=0` Fourier term).
Everything interesting lies in the error term `E(τ)`.

**Parseval identity** for `1_S`:
```
Σ_{k=0}^{N-1} |1̂_S(k)|² = N × Σ_s |1_S(s)|² = N × B
```
so:
```
Σ_{k=1}^{N-1} |1̂_S(k)|² = N×B − B²
```

**Trivial error bound** (the Parseval upper bound on `|E(τ)|`):
```
|E(τ)| ≤ (1/N) Σ_{k=1}^{N-1} |1̂_S(k)|² = B − B²/N ≈ B
```

Therefore `r(τ) ≤ B²/N + B`, which gives `r(τ) ≤ 2B`. This is
completely trivial — it is worse than the direct bound `r(τ) ≤ B` (for each
`P₁ ∈ F` there is at most one `P₂ = T − P₁`).

To achieve the form `r(τ) ≤ B²/N + o(B²/N)`, we would need:
```
(1/N) Σ_{k≠0} |1̂_S(k)|² ≤ o(B²/N)
i.e.  Σ_{k≠0} |1̂_S(k)|² ≤ o(B²)
```
By Parseval this equals `NB − B² ≈ NB` for `B ≪ N`, which is `≫ B²`.
**Parseval alone is insufficient regardless of the structure of F.**

For a useful pointwise bound, we need:
```
max_{k ≠ 0} |1̂_S(k)| ≤ M   with  M × √(NB) ≪ B²/N
i.e.  M ≪ B^{3/2}/N
```
(using Cauchy-Schwarz: `Σ|1̂_S| ≤ √N × (Σ|1̂_S|²)^{1/2} = √N × √(NB) = N√B`,
then `|E(τ)| ≤ (M/N) × N√B = M√B`, requiring `M√B ≪ B²/N`, i.e. `M ≪ B^{3/2}/N`).

For `B = N^α`:
```
M ≪ N^{3α/2 − 1}
```

For `B = N^{1/2}` (birthday-scale factor base): `M ≪ N^{−1/4}`, a sub-constant bound.  
For `B = N^{1/3}`: `M ≪ N^{−1/2}`.

These are stringent requirements. We now ask whether the Weil bound can provide them.

---

## Applying the Weil bound to the error term

### What the Weil bound actually bounds

The **Weil bound for elliptic curves** (over F_p, in its exponential sum form) states:
for any nontrivial additive character `ψ` of `F_p` and rational function `f` on `E`
(of degree `d`):
```
|Σ_{P ∈ E(F_p)} ψ(f(P))| ≤ (2d − 2 + 2g) × √p ≤ O(d √p)
```
where `g` is the genus of a related cover. For `f(P) = x(P)` (the x-coordinate):
```
|Σ_{P ∈ E(F_p)} ψ(x(P))| ≤ 2√p
```

**The relevant Fourier coefficient is:**
```
1̂_S(k) = Σ_{P ∈ F} e^{2πi k · DL(P)/N}   (k ≠ 0)
```

This is a sum over points `P ∈ E(F_p)` satisfying `x(P) < t`, of the group character
`χ_k(P) = e^{2πi k · DL(P)/N}`.

### The circularity obstruction

The character `χ_k(P) = e^{2πi k · DL(P)/N}` is a character of the **abelian group**
`E(F_p) ≅ Z/N`, not an additive character of the **field** `F_p`. These are
fundamentally different objects:

| Character type | Formula | Bounded by Weil? |
|---|---|---|
| Field additive character | `ψ(x(P)) = e^{2πi a·x(P)/p}` for `a ∈ F_p` | YES, by `2√p` |
| Field multiplicative character | `χ(x(P))` for `χ : F_p^× → S¹` | YES, by `O(√p)` |
| **Group character of E(F_p)** | `χ_k(P) = e^{2πi k·DL(P)/N}` | **NO** |

The Weil bound bounds sums of **algebraic** characters — functions expressible as
polynomials or rational functions of the coordinates `(x(P), y(P))` over `F_p`. The
group character `χ_k(P) = e^{2πi k · DL(P)/N}` is **not** an algebraic function of
`(x(P), y(P))`. If it were, one could compute ECDLP by evaluating a polynomial, which
would collapse the cryptographic assumption.

**Stated more sharply**: The map `P ↦ DL(P)` is a group isomorphism `E(F_p) → Z/N`.
The preimage of any subinterval `[a, b] ⊆ Z/N` under this map is a set of EC points
with no algebraic characterization over `F_p`. By contrast, the preimage of `[a, b]`
under `x : E(F_p) → F_p` is defined by the algebraic inequality `a ≤ x(P) ≤ b`,
which is where the Weil bound applies.

To apply the Weil bound to `1̂_S(k)`, we would need to write:
```
Σ_{P ∈ F} e^{2πi k·DL(P)/N} = Σ_{P ∈ E(F_p)} f_k(x(P), y(P)) × 1_{x(P) < t}
```
for some polynomial or rational function `f_k`. No such `f_k` exists, because `DL(P)`
has no algebraic expression in `(x(P), y(P))`.

**This is the principal obstruction.** It is not a technical gap that might be filled by
a more careful application of Weil-type machinery; it is a conceptual barrier. The
character sum `1̂_S(k)` inherently involves the discrete log, and the Weil bound cannot
be applied to it without first solving or substantially constraining ECDLP.

### What about the Weil bound for factor base size?

There is one place Weil genuinely applies: the **size** of `F`.

The x-coordinates of `E(F_p)` are equidistributed over `F_p` with discrepancy `O(√p/N)`.
Precisely, by the Weil bound for the "interval indicator" as an exponential sum:
```
|F| = #{P ∈ E(F_p) : x(P) < t}
    = 2t/p × N  +  O(√p × log p)
    = 2 B_frac × N  +  O(√p × log p)
```

This is the **only** direct application of the Weil bound to the factor base. It tells
us `|F| = B ≈ 2 B_frac N` with an additive error `O(√p log p)`, which is negligible
for `B ≫ √p log p`, i.e., `B_frac ≫ (log p)/(2√p)`. For any practically relevant
factor base this holds.

No further Weil-type bound on the yield follows from this.

### The Shparlinski-type bound gap

Shparlinski and collaborators have studied character sums over structured subsets of
elliptic curves. The results of the form:

```
|Σ_{P ∈ F} ψ(x(P))| ≤ C √p       (additive character of x-coordinate)
|Σ_{P ∈ F} χ(y(P))| ≤ C √p       (character of y-coordinate)
```

These give equidistribution of x-coordinates or y-coordinates within `F`, which is a
statement about the geometry of `F` in the affine plane, not about the distribution
of DL values in `Z/N`.

To bound `1̂_S(k)`, one would need a result of the form:

```
|Σ_{P ∈ F} e^{2πi k · DL(P)/N}| ≤ C × (something ≪ B)
```

No such result appears in the literature, and none is expected: the DL function has no
algebraic structure exploitable by classical exponential-sum techniques.

---

## Main result: yield ≤ heuristic + Weil error

### Theorem (the only honest statement)

**Theorem (average yield from counting)**: For any factor base `F ⊆ E(F_p)` with
`|F| = B`:
```
E_{T uniform over E(F_p)}[r(T)] = B²/N
```

*Proof*: `Σ_T r(T) = #{(P₁, P₂, T) : P₁ + P₂ = T, P₁, P₂ ∈ F} = B²`. Divide by `N`.
No Weil bound is required or used. ∎

**This is the ONLY unconditional statement that can be extracted.** The Weil bound
does not improve it.

### What the Fourier analysis establishes

The representation count satisfies:
```
r(τ) = B²/N + E(τ)
```
where the error term satisfies:

1. **Average error is zero**: `E_τ[E(τ)] = 0` (by orthogonality of characters).
2. **Parseval bound**: `|E(τ)| ≤ B − B²/N ≈ B` (useless).
3. **Variance bound**: `Var_τ(r) = (1/N²) Σ_{k≠0} |1̂_S(k)|⁴`.

For (3): if `|1̂_S(k)| ≤ M` for all `k ≠ 0`, then:
```
Var_τ(r) ≤ (1/N²) × M² × Σ_{k≠0} |1̂_S(k)|² = M²(B − B²/N)/N ≈ M²B/N
```
Standard deviation `≈ M √(B/N)`.

For `r(τ)` to concentrate near `B²/N` (confirming the heuristic), we need
`M √(B/N) = o(B²/N)`, i.e., `M = o(B^{3/2}/N^{1/2})`.

For the small-x factor base, we have no bound on `M` better than the trivial `M ≤ B`
(from `|Σ_S e(·)| ≤ |S|`). This gives `Var ≤ B³/N`, i.e., standard deviation `≤ B^{3/2}/N^{1/2}`,
consistent with Poisson fluctuations but not a useful upper bound on individual `r(τ)`.

### The pseudorandom heuristic (conditional)

**Heuristic assumption H-PSEUDO**: The discrete logs `{DL(P) : P ∈ F}` behave as a
pseudorandom subset of `Z/N` of size `B`, in the sense that `|1̂_S(k)| ≤ C √B` for
all `k ≠ 0`.

If H-PSEUDO holds, then:
```
|E(τ)| ≤ (1/N) × C√B × Σ_{k≠0} |1̂_S(k)|
       ≤ (1/N) × C√B × √N × √(NB)    (Cauchy-Schwarz)
       = C B/√N × √N = CB
```

This is still the trivial bound! The correct conditional bound is:

```
Var(r) ≤ C²B/N × B = C²B²/N
```
`std(r) ≤ CB/√N`.

For `B = N^α`:
- `B²/N = N^{2α-1}` (main term)
- `CB/√N = CN^{α-1/2}` (standard deviation)
- Ratio: `CB/√N / (B²/N) = C N^{1/2-α} / N^{α} = CN^{1/2-2α}`

For `α > 1/4` (i.e. `B > N^{1/4}`): `std/mean → 0` as `N → ∞` under H-PSEUDO.

**Conditional conclusion**: Under H-PSEUDO, the yield `r(τ)/(B²/N)` concentrates
around 1 for most targets `τ`. This confirms the heuristic is accurate "on average"
but does not rule out rare outlier targets.

**H-PSEUDO is unproven** for the small-x factor base. It is consistent with the
empirical evidence (EV-YIELD-e1adbf, EV-YIELD-ca4b02: yield ≈ heuristic at toy scale)
but that evidence does not constitute a proof, and toy-scale measurements cannot be
extrapolated to crypto scale (AGENTS.md rule 7).

---

## Does this close the arithmetic factor base gap?

**No.** The Weil bound approach fails to close the arithmetic factor base gap for
the following reasons, ordered by severity:

### Reason 1: DL circularity (decisive obstruction)

The Fourier error term `E(τ) = (1/N) Σ_{k≠0} 1̂_S(k)² e^{-2πi kτ/N}` requires
bounding `1̂_S(k) = Σ_{P ∈ F} e^{2πi k · DL(P)/N}`. This sum involves `DL(P)`, which
is the very quantity ECDLP asks to compute. The Weil bound cannot be applied without
an algebraic formula for `DL(P)` in terms of coordinates.

This is not a missing theorem; it is a structural barrier. A bound
`|1̂_S(k)| ≤ C p^{α}` for any `α < 1/4` (better than square-root cancellation in the
x-coordinate count) would constitute a nontrivial constraint on the distribution of
ECDLP solutions — which is an open problem orthogonal to classical exponential sums.

### Reason 2: Average vs. pointwise

Even if we could show `r(τ) ≤ B²/N + ε B²/N` for a specific (or generic) `τ`, this
would establish an **upper bound** on yield, not a lower bound. The question of whether
yield achieves the heuristic for an attacker (i.e., whether `r(τ) ≥ ε B²/N` for most
`τ`) is equally important for the index-calculus analysis and equally out of reach.

### Reason 3: Wrong direction for the gap question

The "gap" question in GOAL-ECDLP-001 is whether the arithmetic factor base yield can
EXCEED the heuristic `B²/(2N)` — i.e., whether `r(τ) > B²/N` is possible for some
structured target `τ`. A Weil-based upper bound `r(τ) ≤ B²/N + δ` (if it existed)
would **support** the hypothesis that the heuristic is tight, but this is not the same
as closing the gap.

The relevant closure result would be: "no arithmetic factor base F and no target T
can achieve yield exceeding `B²/N × (1 + ε)`." This requires a LOWER bound on the
error: showing `|E(τ)|` is small for the specific T an attacker might choose. The
Weil bound approach provides upper bounds; it says nothing about the error being
small for adversarially chosen T.

### Reason 4: Empirical evidence scope

EV-YIELD-e1adbf and EV-YIELD-ca4b02 show yield ≤ heuristic at toy scale (p ≤ 9001).
This is consistent with the heuristic being tight but:
- Does not establish the upper bound for crypto-scale primes (AGENTS.md rule 7)
- Does not identify a mechanism (the measurements are consistent with both H-PSEUDO
  and other explanations)
- Does not prove the gap cannot be exploited by a non-uniform attacker

---

## Caveats and remaining open questions

### Caveat 1: The Weil bound does apply, but to the wrong quantity

The Weil bound is a theorem about algebraic geometry over finite fields. It applies
exactly to exponential sums of algebraic functions of `(x(P), y(P))`. The factor base
size `|F|` is one such application (the x-coordinate cumulative distribution), and it
is correctly bounded with error `O(√p log p)`. This is a legitimate, useful result.

The error in applying the Weil bound to the yield comes from conflating:
1. Weil bound on `Σ_P ψ(x(P))` (field character of x-coordinate — algebraic) ✓
2. Weil bound on `Σ_P χ_k(P)` (group character involving DL — NOT algebraic) ✗

DEC-20260804-f320c2 correctly identified the potential but under-specified the
algebraic obstruction. The obstruction is not just "requires a new idea" — it is
that the character sum involves an inherently transcendental function.

### Caveat 2: MOV/Weil pairing does not resolve this

For **supersingular** curves, the Weil pairing defines an algebraic map connecting
group characters to field characters (`e : E[n] × E[n] → μ_n ⊆ F_{p^k}`). This is
the basis of the MOV reduction. However:
- Prime-order curves over `F_p` are **ordinary** (not supersingular) with embedding
  degree `k ≫ log p`, making the pairing computationally intractable
- Even for supersingular curves, the Weil pairing gives a character sum bound in the
  EXTENSION FIELD, not in `F_p`; it does not convert group characters to analyzable
  field characters in the prime-field setting

### Caveat 3: The conditional result is worth recording

Under H-PSEUDO (DL values of small-x points pseudorandom in Z/N), the yield
concentrates around `B²/N` with fluctuations `O(B/√N)`. This implies:
```
Pr[r(τ) > B²/N + CB/√N] → 0   as N → ∞
```
for C large enough, and similarly for the lower tail. This conditional theorem would
be a genuine contribution IF H-PSEUDO could be proved. The proof would require a new
technique — essentially showing that the discrete log restricted to "small x" points
equidistributes in Z/N with exponential-sum discrepancy `O(√B)`. No such result is
known, and it would constitute a significant advance in the theory of ECDLP.

### Open question 1: Discrepancy of DL on small-x points

**OQ-1**: Let `F = {P ∈ E(F_p) : x(P) < t}` and `S = {DL(P) : P ∈ F} ⊆ Z/N`.
What is the exponential-sum discrepancy `D(S) := max_{k≠0} |1̂_S(k)| / B`?

Known: `D(S) ≤ 1` (trivial). Conjectured: `D(S) = O(N^{-1/2} \log N)` (Gaussian
pseudorandomness). The empirical evidence is consistent with this. A proof would
close the yield question.

**Status**: Open. No Weil-based approach is applicable. May require new algebraic
structure theorems or sieve methods for EC points.

### Open question 2: Additive energy of F under EC group law

**OQ-2**: What is `E⁺(F) = #{(P₁, P₂, Q₁, Q₂) ∈ F⁴ : P₁ + P₂ = Q₁ + Q₂}`?

For a random set: `E⁺(F) ≈ 2B³/N + B²`. This controls `Var(r)` directly.
Sum-product theory (Bourgain, Green-Ruzsa-Tao) bounds additive energy for sets in
fields or groups, but these bounds are in terms of `|F + F|` or `|F − F|`, not
`|F + F|` in the ECDLP sense (which maps to `|S + S|` in `Z/N`, and `|S|` is
determined by the DL structure). As analyzed in BATCH-066 (TASK-20260804-071), the
sum-product structure of x-coordinates in `F_p` does not transfer to the EC group
law.

**Status**: Open. Empirical evidence (EV-YIELD-e1adbf, EV-YIELD-ca4b02) gives
`E⁺(F) ≈ random` at toy scale, but this is unproven.

### Open question 3: Does any structured factor base beat heuristic?

**OQ-3**: Does there exist ANY choice of `F ⊆ E(F_p)` with `|F| = B` and yield
exceeding `B²/(2N) × (1 + ε)` for `ε` independent of `N`?

The empirical evidence and the theory both suggest NO, but no proof exists. This is
a weaker version of KN-OPEN-001 (prime-field ECDLP open question).

---

## Verdict summary

| Claim | Status | Derivable from Weil? |
|---|---|---|
| `\|F\| = 2 B_frac N ± O(√p log p)` | TRUE | YES — direct Weil equidistribution of x-coords |
| `E_T[r(T)] = B²/N` | TRUE | No Weil needed — pure counting |
| `r(T) ≤ B` for all T | TRUE | No Weil needed — direct bound |
| `r(T) ≤ B²/N + o(B²/N)` | UNKNOWN | NO — requires bounding DL character sums |
| `r(T) = B²/N ± O(B/√N)` (conditional) | Conditional on H-PSEUDO | NO — H-PSEUDO unproven |
| Weil bound closes arithmetic FB gap | FALSE | N/A |

**Principal finding**: The Weil bound approach does **not** provide a theorem that
the arithmetic factor base yield is bounded by `B²/N + small`. The Fourier analysis
of the yield reduces to bounding character sums `1̂_S(k)` that involve the discrete
log — a circular dependency. The Weil bound (and all classical exponential-sum
machinery) applies to algebraic characters of the coordinates, not to group characters
involving the DL.

The only unconditional result is the trivial `E[r] = B²/N`. Everything beyond this
is either heuristic (H-PSEUDO assumed) or requires a new technique to prove
equidistribution of DL values for structured EC point sets.

**Research disposition**: The "Weil bound yield upper bound" direction identified in
DEC-20260804-f320c2 is **blocked by DL circularity**. The obstacle is mathematical
and provably non-circular: any proof that `|1̂_S(k)| ≤ o(B)` for the small-x factor
base would be equivalent to a non-trivial statement about the distribution of ECDLP
solutions, which is exactly what GOAL-ECDLP-001 is studying. This does not preclude
the direction in principle — a proof of H-PSEUDO would be a genuine breakthrough — but
it means the direction cannot be completed by a routine application of existing
Weil-bound technology. It requires a new approach.

**What this direction CAN contribute (narrowly)**: Recording H-PSEUDO as a formal
conjecture with a clear falsification condition (OQ-1: measure `D(S)` experimentally
at scaling primes) would be a useful intermediate result. If `D(S)` decays as
predicted by H-PSEUDO across p-sizes, that is supporting evidence. But it remains
empirical until a proof is found.

---

## References

- Weil (1948): "Sur les courbes algébriques et les variétés qui s'en déduisent"
- Hasse (1936): Point count bound for EC over finite fields
- Shparlinski (2001+): Distribution of EC discrete logs, exponential sums over EC points
- EV-YIELD-e1adbf, EV-YIELD-ca4b02: m=2, m=3 yield ≈ heuristic (BATCH-062/063)
- DEC-20260804-f320c2: BGS closed, Weil bound direction proposed (BATCH-066)
- TASK-20260804-071 / bgs_analysis.md: BGS obstruction and sum-product analysis (BATCH-066)
- KN-OPEN-001: Prime-field index calculus vs. Pollard rho (open)
- KN-OPEN-009: Semaev summation cover monodromy (open)
- AGENTS.md rule 7: Toy-curve evidence must not be presented as crypto-scale validation
