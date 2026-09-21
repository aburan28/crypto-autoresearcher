# B1 — Supersingular endomorphism-ring / isogeny-path finding: idea catalogue

Slice: Deuring correspondence, quaternion maximal orders, CGL hash, SQIsign
foundations, oriented / CM-endowed curves, Delfs–Galbraith and variants.
Anchors: `KN-OPEN-013`, `KN-OPEN-024`. Related: `KN-OPEN-015`, `KN-OPEN-028`.
Session date: 2026-08-05. Author role: idea-generator.

**This file proposes. It asserts no result, creates no ledger record, changes no
status, and mints no identifier.** Every derivation below marked *(session
derivation, unverified)* was produced in this session from the frozen full text
at `inputs/P13-WESOLOWSKI-2026/paper_fulltext.md` plus corpus records; none has
been independently checked, and none may be cited as a program finding.

---

## 0. Frame

### 0.1 Matched baselines actually on the frontier (as recorded in this corpus)

| Problem / regime | Best known | Memory | Source record |
|---|---|---|---|
| OneEnd / EndRing / Isogeny, general `E/F_{p^2}` | `p^{1/3+o(1)}` time, **conditional on Heuristic 1**, `o(1)` superpolynomial | `p^{1/3+o(1)}` | `KN-LIT-7563`, frozen text §1, §3 |
| Same, step count, classical, `F_{p^2}` | `Õ(p^{1/2})` (Delfs–Galbraith / CGL-era) | poly | `KN-TECH-029`, `KN-TECH-057` |
| Same, **Wiener 3D full cost**, `F_{p^2}` | VW distinguished-point `p^{1/2}` | poly | `KN-TECH-057` |
| Path-finding, both endpoints `F_p`-rational | `Õ(p^{1/4})` step count; `p^{1/3}` full cost (DG), `p^{1/4}` full cost (VW, conditional on unproven `F_p` mixing) | `p^{1/4}` / poly | `KN-TECH-057` |
| Quantum, general | `Õ(p^{1/4})` reported, **different machine model** | model-dependent | `KN-LIT-079` |
| Time–memory interpolation for the `p^{1/3}` claw | `p^{1/2+o(1)}/w^{1/2}` at memory `w` (van Oorschot–Wiener) | `w` | frozen text §1.1 |
| Concrete, NIST-I (`log2 p ≈ 256`) | `≥ 2^{106.5}` `F_{p^2}`-ops, `≥ 2^{92.5}` memory (author-flagged optimistic) | — | frozen text §4.1 |

`KN-TECH-057` predates the `p^{1/3}` result and does **not** price it. That gap
is B1-6.

### 0.2 Established families declared off-limits as the primary lens (inventor-protocol §1)

1. Delfs–Galbraith subfield search, and its terminal-enlarging variants
   (`KN-LIT-7580` CM terminals, `KN-LIT-7655` `(2,ε)`-structures) — both
   reported as constant-factor.
2. Endpoint-`j`-invariant MITM / claw finding on the full `ℓ`-isogeny graph.
3. KLPT and quaternion-ideal-to-isogeny translation treated as a solved
   subroutine to be re-tuned.
4. Torsion-image / Kani higher-dimensional embedding attacks — **out of scope
   as a positive target by goal charter**; CGL, CSIDH and SQIsign publish no
   torsion images (`KN-OPEN-015`).
5. CSIDH hidden-shift / Kuperberg / collimation, and the FC0 / CollimationSieve
   lane (`GOAL-SSI-001` BATCH-020..042).
6. Orientation vectorization with an independently published bounded `α`
   (`IDEA-20260725-002`, closed as a scoped residual, `EV-SSI-004`).
7. SQIsign transcript sufficiency testing against Kani/Petit necessary
   conditions (`IDEA-20260725-003` / SQI-FS-T0, closed negative, `EV-SSI-006`).
8. Wesolowski's own construction *as a lens*. Ideas below that touch it are
   marked **successor** and must state the delta.

Also not to be duplicated: `IDEA-20260804-170692` (local `ℓ`-adic transport
signatures), `IDEA-20260804-4c9ac0` (kernel-Frobenius type profiles),
`IDEA-20260804-84328c` (Frobenius-orbit bucket keys). B1-7 and B1-8 are marked
successors to `-84328c` with the delta stated in place.

### 0.3 Candidate tracked objects enumerated for this slice

This is a **sketch, not a taxonomy** — `KN-OPEN-019` (the written
object-enumeration) does not exist, and per `docs/inventor-protocol.md` §1 no
family-to-object mapping here may be treated as complete.

| # | Object | Lossy? | Propagates? | Used by |
|---|---|---|---|---|
| O1 | Successive-minima profile `(λ_1..λ_4)` of `Hom(E,E^{(p)})` under `deg` | yes — discards the isogenies, the order, the curve | not under isogeny steps; sampled i.i.d. per instance | B1-1, B1-2 |
| O2 | **Frobenius displacement** `δ(E) = min deg(E → E^{(p)})`, one integer per vertex | yes — a single integer from a rank-4 lattice | one-step: `δ(E') ≤ ℓ^2 δ(E)` (dual-sandwich bound) | B1-7 |
| O3 | Partner-map displacement law: the exponent pair `(γ_σ, θ_σ)` in `#{E : δ_σ(E) ≤ D} ≈ D^{γ_σ} p^{1-θ_σ}` | yes — a two-number summary of a whole graph map | n/a (a statistic of `σ`, not of a state) | B1-8 |
| O4 | Divisor-window membership of `deg φ` (has a divisor in `[deg φ/X, X]`) — **weaker than smoothness** | yes — discards the factorization | multiplicative | B1-3, B1-4 |
| O5 | Table index → isogeny map for `L(E,X,B)` (an addressing scheme, not a state) | n/a — it is an oracle, audited as such | poly-time evaluable? that is the question | B1-5 |
| O6 | Per-vertex membership filter for `A_M = {E : ∃α ∈ End(E)\Z, Nrd α ≤ M}` | yes — one bit per vertex | n/a | B1-9 |
| O7 | Dimension-`g` displacement `δ_g(A) = min deg(A → A^{(p)})` on superspecial `A` | yes | n/a | B1-10 |
| O8 | Presentation type of a left `M_g(O)`-ideal | yes | n/a | B1-11 |
| O9 | Quaternion-side invariant vector of a *public* curve (`λ_1(P)`, theta head, `δ`) | yes | n/a | B1-12 |

**Lossy-projection test, applied.** O2 is the sharpest case and is worth stating
explicitly because it is the one most likely to be mistaken for a change of
coordinates. `δ(E)` is a single integer extracted from a rank-4 lattice whose
full isometry class is (reportedly) a complete invariant of `End(E)`; distinct
maximal orders share a `δ` value in bulk (there are `~p/12` curves and
`δ ≤ (p/2)^{1/3}` always, so the fibres have average size `~p^{2/3}`). It
discards the lattice, the isogeny, and the order. What it retains propagates
compatibly with one graph operation: if `φ: E → E'` is an `ℓ`-isogeny then
`\hat{φ}^{(p)} ∘ (E' → E'^{(p)}) ∘ φ` witnesses `δ(E) ≤ ℓ^2 δ(E')`, and
symmetrically — so `δ` is `2 log ℓ`-Lipschitz on the graph in log scale. That
is a genuine lossy, deterministically-constrained projection. O1 by contrast is
*not* lossy in the dangerous direction — the full profile plus the Gram data
recovers the lattice — which is why B1-2 tracks only the profile and its tail,
never the lattice, and why B1-2 is honestly labelled a distribution measurement
rather than a new attack object.

### 0.4 Tooling reality (binding on every entry below)

- **SageMath is unavailable and uninstallable.** No idea below requires it.
- **eprint / arXiv are unreachable.** Every literature attribution below is a
  recollection or a corpus relay and is marked. `novelty_status` for this whole
  catalogue is `unverified`; nothing here is claimed new and nothing is
  dismissed as known.
- **The single most consequential tooling fact this session found:** the
  crypto-scale sampling shortcut used in the frozen text §4.2 is *pure
  quaternion-lattice arithmetic* — sample a random maximal order `O ⊂ B_{p,∞}`
  up to conjugation, form the two-sided ideal `P` of reduced norm `p`, take the
  shortest vector of `(P, Nrd/p)`. **It touches no elliptic curve and needs no
  computer-algebra system**: 4×4 integer HNF, exact 4-dimensional SVP by
  LLL-then-enumerate, and integer smoothness testing. That is implementable in
  pure Python. This is what makes B1-1, B1-2 and B1-12 crypto-scale-capable
  here rather than blocked, and it is the reason B1-1 is a prerequisite rather
  than a formality.
- Independent verification of that sampler against a second implementation is
  **not** available. B1-1 therefore substitutes internal consistency checks
  (Eichler mass formula `Σ 1/|Aut| = (p−1)/24`; `disc(O) = p`; `P^2 = pO`; Gram
  determinant), and its ceiling is capped accordingly.

---

## 1. The twelve ideas

### B1-1. SageMath-free crypto-scale Deuring sampler, validated by reproducing the Heuristic-1 experiment

**Claim.** The frozen text §4.2 validation of Heuristic 1 — 100,000 samples at
`p = 5·2^248 − 1` (SQIsign NIST-I), largest prime factor of `λ_1(P, Nrd/p)`
compared against Dickman–de Bruijn `ρ(u)`, `u = log(p/2)/(3x)` — is reproducible
in this environment with pure-Python quaternion arithmetic, and its reproduction
either validates or invalidates the one instrument on which every crypto-scale
measurement in this slice depends. This is the inventor-protocol §8 audit 1
(exact baseline reproduction), run before any expensive experiment.

**Mechanism.** Fix `p ≡ 3 mod 4`; start from the special extremal order
`O_0 = ⟨1, i, (i+j)/2, (1+k)/2⟩` in `B_{p,∞} = (−1,−p)`. Sample a uniform-up-to-
conjugation maximal order by a non-backtracking random walk of length
`n = c·log p` in the `2`-ideal graph: repeatedly pick a left `O`-ideal of norm 2
and replace `O` by its right order, with the mixing bound taken from the same
Ramanujan citation the frozen text uses for its curve-side walk (frozen text
§3, proof of Thm 1.1: `n = O(log p)`). Compute the unique two-sided `P` with
`Nrd(P) = p`; reduce `(P, Nrd/p)` (LLL on the 4×4 Gram, then exact enumeration —
dimension 4, so exact SVP is cheap); factor `λ_1` far enough to record its
largest prime factor. Plot the empirical CDF of `log(largest prime factor)`
against `ρ(u)`.

**Minimal discriminating test.** Three-stage, each with a distinct verdict.
(a) *Instrument*: at toy `p` (`p < 2^20`), check `disc(O) = p` on every sample,
`P^2 = pO`, and the Eichler mass `Σ 1/|Aut(O)| = (p−1)/24` over the full type
set enumerated by exhaustive walk — mass agreement to exact rational equality or
the sampler is wrong. (b) *Mixing*: walk-length sweep `n ∈ {1, log p, 2 log p,
4 log p}`; the empirical distribution of `λ_1` must be stationary from
`n ≈ log p` onward. (c) *Reproduction*: 10^4–10^5 samples at
`p = 5·2^248 − 1`; report the CDF, and the two tail checks the frozen text
reports (smoothest of 100,000 is 12589-smooth vs predicted `ρ(u) ≈ 1/69232`).

**Null object / control.** Two nulls, both required. (i) *Random-integer null*:
draw integers uniformly from `[1, (p/2)^{1/3}]` and run the identical
largest-prime-factor pipeline. `ρ(u)` will fit this too — so **agreement with
`ρ(u)` alone is not evidence of supersingular structure**, and the discriminating
statistics are the *scale* of `λ_1` (predicted `≈ p^{1/3}`, not `p^{1/2}`) and
the left tail. (ii) *Random-lattice null*: random rank-4 positive-definite
integral lattices of the same determinant, to test whether `λ_1 ≈ p^{1/3}`
requires the arithmetic of `P` or follows from the determinant alone.

**Falsifier (reachable).** Mass formula fails at toy `p`; or `λ_1` distribution
is not stationary in `n` by `4 log p`; or the NIST-I CDF departs from `ρ(u)`
beyond the sampling error of 10^4 draws in a direction the random-integer null
does not reproduce. Any of these blocks B1-2 and B1-12 at crypto scale and is
recorded as an instrument failure, **not** as evidence against Heuristic 1.

**Cost.** Implementation **high** (ideal arithmetic, right orders, HNF, exact
4-dim SVP, Pollard-rho + a small-ECM largest-factor routine). Compute
**medium**: 10^4 samples at 256-bit `p`; the largest-prime-factor extraction
dominates and can be degraded to a smoothness-grid (`B` on a log grid) if ECM in
pure Python proves too slow, at the cost of CDF resolution — declare which was
used.

**Ceiling.** `control` / instrument-validation. It reproduces a published
experiment. It supports **no** new claim about Heuristic 1 and must never be
reported as independent confirmation of the `p^{1/3+o(1)}` theorem.

**Kills it early.** Toy-`p` Eichler mass disagreement (one afternoon). Second
cheapest kill: if `λ_1` at 256-bit `p` lands near `p^{1/2}` rather than
`p^{1/3}`, the `P`-construction is wrong (most likely the `Nrd/p` normalisation
or the ideal index `[O:P] = p^2`) — stop and repair before any sampling run.

---

### B1-2. The successive-minima profile of `Hom(E,E^{(p)})` — quantifying Remark 1's slack at crypto scale

**Claim.** *(session derivation, unverified)* The lattice `(P, Nrd/p)` has
covolume `≈ p/4` yet always satisfies `λ_1 ≤ (p/2)^{1/6}` in Euclidean length
(degree `≤ (p/2)^{1/3}`, the Aubry–Oyono–Vincent bound the frozen text imports as
Theorem 1.5). It is therefore **systematically skew**, with predicted degree
profile `≈ (p^{1/3}, p^{1/3}, p^{2/3}, p^{2/3})` — the last two matching the
standard "smallest non-scalar endomorphism has degree `≈ p^{2/3}`". If the
profile is as predicted, the number of isogenies `E → E^{(p)}` of degree `≤ T`
grows like `T/p^{1/3}` (a rank-2 regime), and Remark 1's "there are generally
multiple small isogenies, any one of which suffices" is worth a factor
`p^{o(1)}` only — closing the multi-chance route as exponent-moving while
possibly changing the concrete-cost table. If the profile is *not* as predicted
— specifically if `λ_2` is much larger than `λ_1` (rank-1 regime), or if the
count grows like `T^2/p^{2/3}` — the accounting changes and so does the optimal
`B`.

**Mechanism.** Compute all four successive minima of `(P, Nrd/p)` per sample
(exact, dimension 4), plus the theta head `#{φ : deg φ ≤ T}` on a `T`-grid
spanning `[p^{1/3}, B·p^{1/3}]`, plus the largest prime factor of each of the
`k` smallest degrees rather than only the smallest. Fit the growth exponent.

**Minimal discriminating test.** Same sampler as B1-1 at `p = 5·2^248 − 1` and
`p = 27·2^500 − 1`; `10^4` and `10^3` samples. Metrics: the four minima; the
fitted exponent `a` in `#{deg ≤ T} ∝ T^a`; and `P_k = Pr[at least one of the k
smallest degrees is B-smooth]` on a `(k, B)` grid, versus the frozen text's
`P_0 = ρ(u)` single-degree bound. Report the ratio `P_k/P_0` at the frozen
text's own optimal `B` and the resulting shift in the NIST-I/III/V concrete
numbers.

**Null object / control.** Random rank-4 lattices of determinant `p/4` **without**
the skew constraint (these should give `λ_1 ≈ p^{1/4}` Euclidean, degree
`≈ p^{1/2}`) — if the sampled `P` matches this null, either the AOV bound is
being violated by the sampler or the normalisation is wrong, and the run is an
instrument failure. Second null: random rank-4 lattices constructed with an
*imposed* skew of the predicted shape but random arithmetic, to separate "the
profile shape" from "the arithmetic of `P`" in the `P_k/P_0` measurement.

**Falsifier (reachable).** `P_k/P_0` is within `p^{o(1)}` of 1 across the grid
at both primes ⇒ Remark 1's slack is confirmed cofactor-level, and the
"more-chances" route is closed with a measured mechanism. Or the fitted `a` is
`≈ 2` at both primes ⇒ the skew prediction is wrong, and the session derivation
above is refuted (a useful negative that also re-opens the optimal-`B` question).

**Cost.** Implementation **medium** on top of B1-1 (adds enumeration of the
short-vector shell and a `k`-smallest routine). Compute **medium**.

**Ceiling.** `crypto-scale distribution measurement`, cofactor-level for the
exponent, decision-relevant for the concrete-cost table. It is **not** an
exponent claim and must not be promoted as one; per `docs/target-result-profile.md`
A1 it is explicitly the non-target class, and its priority is as a **building
block** — it is the cheapest measurement that can move the NIST-I number that
parameter choices depend on, and it re-uses B1-1's instrument at near-zero
marginal cost.

**Kills it early.** If B1-1's exact-SVP routine cannot produce all four minima
reliably at 256-bit `p` within budget, degrade to `λ_1, λ_2` only and state the
reduced claim; if even that fails, the idea is blocked, not negative.

---

### B1-3. Divisor-in-a-window, not smoothness: is the superpolynomial `o(1)` an artifact of the enumeration rather than of the mathematics?

**Claim.** *(session derivation, unverified — this is the highest-stakes entry
in the catalogue.)* Lemma 3.4 of the frozen text does not actually require
`B`-smoothness of `deg φ`. Re-reading its proof: the correctness argument needs
exactly that `deg φ ≤ X^2` and that `deg φ` **has a divisor `d` in the window
`[deg φ / X, X]`**, so that `φ = η ∘ ψ` splits with both halves of degree `≤ X`
and both halves lie in the table. `B`-smoothness is used only as a *sufficient*
condition for such a divisor to exist (the maximal-prefix argument) **and** as
the condition that makes the table constructible by cheap small-degree walks.
Separating those two roles is the whole idea. The density of integers `n ≤ N`
with a divisor in a window of fixed multiplicative width is
`≍ (log N)^{−δ}(log log N)^{−3/2}` with `δ = 1 − (1+log log 2)/log 2 ≈ 0.086`
(Ford's theorem on `H(x,y,2y)`; **recollection, unverifiable here — eprint and
journals unreachable — and it must be treated as a named external ingredient to
be confirmed before any use**). That is `1/polylog(p)`, versus the frozen text's
`P_0 = u^{−u(1+o(1))} = p^{−o(1)}` with `u = √log(p/2)`. **If** the table could
be enumerated at amortised `p^{o(1)}` cost per entry *without* the smoothness
restriction, the entire superpolynomial `o(1)` — the overhead the author
explicitly flags as "much larger than the previous `(log p)^{O(1)}` cofactor" —
would collapse to a polylogarithmic cofactor, and the NIST-I estimate would move
from `≥ 2^{106.5}` toward `≈ p^{1/3}·polylog ≈ 2^{88}`.

**Mechanism.** Two separable obligations, and the idea is designed so that
either answer is a result.
*(A) Correctness under the weakened condition.* Restate Lemma 3.4 with
`L(E,X) = {cyclic ψ : E → E′, deg ψ ≤ X}` (no smoothness) and prove or refute:
if `deg φ ≤ X^2` and `deg φ` has a divisor in `[deg φ/X, X]`, Algorithm 2 with
that table returns `φ`. This is a paper-and-pencil re-derivation of the
degree-split inequality with `B` removed.
*(B) Enumeration cost — the real bottleneck.* The table has
`Σ_{d≤X} ψ(d) ≈ X^2/2 ≈ p^{1/3}/2` entries at `X = (p/2)^{1/6}`, the **same size**
as the smooth table `Ψ(X,B)·X = p^{1/3−o(1)}`. But reaching a codomain at
prime-degree `ℓ ≈ X ≈ p^{1/6}` requires an `ℓ`-isogeny step, and the cheapest
known route (evaluating `Φ_ℓ(j, ·)` and root-finding, `Õ(ℓ^2)` time / `Õ(ℓ)`
space in the recollection of Sutherland's evaluation method — unverified) costs
`≥ ℓ` per neighbour even amortised. Formalise as: total cost
`= (table size) × (amortised per-entry construction cost `c(X)`) / P_0`, and
determine the exponent of `c(X)`.

**Minimal discriminating test.** Zero compute. Write the cost function
`T(β) = X^2 · ρ(u(β)) · B^{κ} / ρ(u_0(β))` with `B = p^β`,
`X = p^{1/6+β/2}`, `u = 1/(6β) + 1/2`, `u_0 = 1/(3β)`, and `κ` the per-entry
construction exponent; then evaluate the exponent of `T` at (i) `κ = 1`
(pay `Ω(ℓ)` per `ℓ`-step) and (ii) `κ = 0` (hypothetical free large-degree
steps). Numerically minimise over `β` at `log2 p ∈ {256, 384, 512}` and report
the concrete `F_{p^2}`-operation counts beside the frozen text's `2^{106.5} /
2^{157.5} / 2^{204.2}`.

**Null object / control.** The `κ = 1, β → 0` corner **must reproduce the frozen
text's own optimisation** — same `B = e^{(1/3)√log(p/2)}`, same
`p^{1/3+o(1)}`, same concrete numbers to within the author's stated rounding.
That is the baseline-reproduction control; a cost function that does not
reproduce it is instrumented wrong and its `κ=0` value is meaningless. Second
control: run the same optimisation with `ρ(u)` replaced by a *constant* density
and confirm the exponent then reads `1/3 + β(1+κ)`, isolating where the
`p^{−o(1)}` enters.

**Falsifier (reachable).** *(i)* Obligation (A) fails — some step of Lemma 3.4
silently uses smoothness beyond the divisor window (a plausible candidate: the
cyclicity of both halves, or the requirement that `χ = \hat{η}^{(p)}` be in the
same table) — the idea dies immediately and the closure is a named,
recorded obstruction. *(ii)* Obligation (B) resolves at `κ ≥ 1` with a lower
bound argument (writing down the `ℓ+1` neighbours of a vertex is `Ω(ℓ)` output,
and the algorithm needs all of them) ⇒ **the superpolynomial `o(1)` is
conditionally necessary for this algorithm shape**, which is a first-class
closure with forward guidance (isogeny-evaluation lower bounds become the crux).
*(iii)* The Ford density recollection is wrong or the constant differs ⇒ the
quantitative upside shrinks and must be restated.

**Cost.** Implementation **low** (a numeric optimiser over a 1-parameter cost
function). Compute **negligible**. This is the cheapest entry with exponent-
adjacent stakes in the catalogue.

**Ceiling.** `derivation`. Best case it identifies where a superpolynomial
overhead lives and states the exact condition to remove it; it does not remove
it. Any claim past that requires an actual enumeration algorithm, which is not
proposed here.

**Kills it early.** Read Lemma 3.4's proof line by line against the weakened
hypothesis before touching the optimiser. One hour. If `B` is load-bearing
twice, stop.

---

### B1-4. One-large-prime variation of the smooth-isogeny table

**Claim.** Between the frozen text's fully-smooth table (`P_0 = p^{−o(1)}`,
cheap per entry) and B1-3's unrestricted table (`P_0 = 1/polylog`, expensive per
entry) sits the classical index-calculus **large-prime variation**: admit
degrees of the form `d_1 · ℓ · d_2` with `d_1, d_2` `B`-smooth and one prime
`ℓ ≤ L` for a second parameter `L ≫ B`. The claim to be decided is whether the
resulting two-parameter optimisation `(B, L)` moves the **exponent** (it almost
certainly does not) or moves the **concrete NIST-I/III/V cost** by a stated
factor (it may). Stating which, with numbers, is the deliverable.

**Mechanism.** The success probability becomes `Pr[deg φ is (B, L)-semismooth]`,
which for `u_0 = log(p^{1/3})/log B` and `v = log L/log B` follows the
Bach–Peralta `σ(u,v)`-type two-dimensional density (recollection, unverified)
and exceeds `ρ(u_0)` by a factor that grows with `L`. The cost per entry
acquires an `Õ(L)` term for the single large step, but only on the
`Ψ_2(X,B,L)/Ψ(X,B)` fraction of entries that use one. Total
`= (table size) × (mixed per-entry cost) / P_0(B,L)`; optimise in two
parameters.

**Minimal discriminating test.** Zero compute beyond a 2-D numeric optimisation.
Report: (a) the optimal `(B, L)` at `log2 p ∈ {256, 384, 512}`; (b) the
`F_{p^2}`-operation and memory counts beside the frozen text's; (c) the fitted
exponent of `T(p)` over `log2 p ∈ [256, 1024]` — if it is `1/3 + o(1)` with the
`o(1)` numerically smaller, say exactly that and label it cofactor-level.

**Null object / control.** Set `L = B` and confirm the optimiser returns the
frozen text's own parameters and cost figures. A large-prime variation that does
not degenerate to the baseline at `L = B` is mis-implemented.

**Falsifier (reachable).** The optimal `L` is `Θ(B)` at all three parameter
sets ⇒ the large-prime variation buys nothing here and the route is closed with
its mechanism (the `Õ(L)` per-step charge dominates the semismooth density gain
because, unlike index calculus, there is no relation-combining step that lets
two large-prime partials cancel — **that absence is the named obstruction**, and
it is worth recording because it is exactly the disanalogy with index calculus
that makes the transfer fail).

**Cost.** Implementation **low**. Compute **negligible**.

**Ceiling.** `derivation`, cofactor-level by design. Priority justified only as
a concrete-cost input to B1-6's table and as the cheap constructive
counterexample-or-confirmation for B1-3's `κ` question.

**Kills it early.** Check first whether two large-prime partial relations can be
combined at all in this setting. In index calculus they can (the large primes
cancel across relations); here each table entry is an isogeny, not a relation in
a group, so there is nothing to cancel. If that argument holds, the idea is
closed on paper in under an hour, and *that closure is the deliverable*.

---

### B1-5. Quantum claw-finding on the `p^{1/3}` table, with every quantum resource charged

**Claim.** The frozen text's §1.1 quantum remark points only at van
Oorschot–Wiener in the quantum setting ("quantum computation may only be
advantageous to reduce the amount of memory, with the same time complexity") and
does **not** analyse quantum search over the table `L(E,X,B)` itself. Under a
charging model that grants unit-cost quantum-accessible classical memory
(QRACM), Grover search over the `N = p^{1/3+o(1)}` table entries checking
membership of the Frobenius conjugate gives `p^{1/6+o(1)}` quantum time with
`p^{1/3+o(1)}` QRACM; under an element-distinctness / Tani quantum walk with no
QRACM but `N^{2/3}` quantum-accessible storage, `p^{2/9+o(1)}` time. Both are
below the reported `Õ(p^{1/4})` quantum baseline (`KN-LIT-079`). **The entire
question is whether those advantages survive an honest charge**, which
`GOAL-SSI-001`'s completion criteria explicitly require ("absence of uncharged
oracle, torsion-image, preprocessing, memory, or quantum-query costs").

**Mechanism.** Three obligations, each a separate verdict.
*(O5 audit — the load-bearing one.)* Quantum search needs the table as an
**oracle**, not as a built list: an index `i ↦ ψ_i` computable in `p^{o(1)}`
time. Candidate scheme: index by (a multiset of primes `≤ B` with product
`≤ X`, and for each step a choice among the `≤ ℓ` non-backtracking neighbours);
evaluation walks `≤ log X` steps of degree `≤ B` each, at `poly(B, log p) =
p^{o(1)}` per step. If that scheme is sound, the oracle exists and the table
never has to be materialised — which is a *stronger* statement than the quantum
speedup itself, since it would also bear on the classical memory question of
B1-6.
*(Charging ladder.)* Price the algorithm in four named models: (1) unit-cost
QRACM; (2) quantum walk with `N^{2/3}` quantum data structure; (3) circuit model
with no free memory, charging a table lookup at `Ω(size)` gates; (4) Wiener 3D
wiring (`KN-TECH-057`), charging `τ = S^{1/3}` per access. Report the crossover
points and which models leave anything below `p^{1/4}`.
*(Uniqueness.)* The table has `p^{1/3}` entries mapping into `≈ p/12` vertices,
so spurious claws number `≈ p^{2/3}/p = p^{−1/3}`: **the claw is unique with
probability `1 − o(1)`.** State whether that helps (no golden-collision penalty)
or hurts (no amplitude amplification over many targets).

**Minimal discriminating test.** Zero compute. Write the index scheme
explicitly, prove or refute poly-time evaluability (the non-backtracking
constraint couples consecutive steps — that is the thing to check), then fill
the four-model charging table.

**Null object / control.** Apply the identical ladder to the *classical*
baseline — Grover replaced by exhaustive search, QRACM by RAM — and confirm it
returns `p^{1/3}` in model (1) and `p^{4/9}` in model (4). A ladder that does
not reproduce the classical numbers is mis-specified. Second control: apply the
same ladder to a generic claw between two structureless lists of size `p^{1/3}`
— if the isogeny setting gives the same answer, the arithmetic contributed
nothing and the result is about claw finding, not about isogenies.

**Falsifier (reachable).** The index scheme is not poly-time evaluable (e.g. the
non-backtracking condition forces the ancestor path to be carried, or distinct
indices collide so badly that the effective domain is not `N`) ⇒ the table must
be materialised, quantum access is charged at materialised-table rates, and the
advantage is bounded by model (3)/(4) ⇒ closure with a named obstruction. Or:
models (3) and (4) both exceed `p^{1/4}` ⇒ no quantum exponent improvement
survives honest charging, which is itself a clean, reportable answer to
`KN-OPEN-014`-adjacent questions.

**Cost.** Implementation **none**. Compute **none**. Derivation only.

**Ceiling.** `derivation`. Even the best outcome is a conditional quantum
complexity claim resting on an unimplemented oracle and a named memory model;
it would require independent `review-breakthrough` before any promotion, and it
claims nothing about deployed parameters without a concrete-cost table.

**Kills it early.** Check the non-backtracking indexability first. If a table
entry's validity depends on its ancestor's kernel, the oracle needs the path and
the whole ladder collapses to model (3).

---

### B1-6. Wiener-3D full-cost repricing of the `p^{1/3+o(1)}` algorithm — the successor to `KN-TECH-057`'s baseline table

**Claim.** `KN-TECH-057` sets this program's matched classical baselines (VW
`p^{1/2}` full cost at `F_{p^2}`; DG `p^{1/3}` full cost, VW `p^{1/4}`
conditional, at `F_p`) and **predates the `p^{1/3+o(1)}` result, which it does
not price**. Under `KN-TECH-057`'s own model (full cost `= W × τ`, `τ = S^{1/3}`
for a shared table of `S` entries), the new algorithm's full cost is
`p^{1/3} × (p^{1/3})^{1/3} = p^{4/9}` if the table is randomly accessed, but
`p^{1/3}` if it can be restructured so the shared table is touched only at
distinguished points (the exact reasoning `KN-TECH-057` already uses to give VW
`τ = O(1)`). **Which of `p^{4/9}` and `p^{1/3}` is correct decides what every
future candidate in this lane must beat**, and the program is currently
screening against a superseded number.

**Mechanism.** Algorithm 2 is a claw between `L` and `L^{(p)}`, and every one of
the `p^{1/3}` entries is looked up — there is no distinguished-point
amortisation as written. The question is whether an equivalent algorithm exists
in which lookups are rare. Two sub-questions: (a) can the claw be found by a
distinguished-point walk (see also B1-7's `δ`-steering)? The obstruction, stated
plainly: `L(E,X,B)` is defined *relative to `E`* and is **not closed under any
natural self-map**, so a rho-style walk has no invariant set to iterate on — the
named obstruction for why the memory cannot be traded. (b) What does van
Oorschot–Wiener's `p^{1/2+o(1)}/w^{1/2}` interpolation cost under the 3D model,
and where does it cross `p^{4/9}`?

**Minimal discriminating test.** Zero compute. Produce: (i) the full-cost
exponent of the `p^{1/3}` algorithm in the `KN-TECH-057` model, with the
`τ`-derivation shown; (ii) the revised matched-baseline table (all five rows,
both regimes, step-count *and* full-cost columns); (iii) the VW-interpolation
curve under the same model with the crossover `w`; (iv) a scope restatement
including the **EndRing → CGL-collision conversion charge** — the frozen text's
Corollary 1.2 gives an isogeny of smooth composite degree, whereas a CGL
collision requires a non-backtracking `2`-power path of admissible length, so
the conversion costs an extra KLPT-shaped step whose charge and output length
must be stated rather than assumed free.

**Null object / control.** Re-derive `KN-TECH-057`'s three existing rows (MITM
`p^{2/3}`, DG `p^{1/3}`, VW `p^{1/2}`) from scratch with the same instrument
before adding the fourth. Disagreement on any existing row means the instrument
drifted, not that the baseline moved.

**Falsifier (reachable).** The re-derivation reproduces `KN-TECH-057`'s rows and
places the `p^{1/3}` algorithm at `p^{4/9}` ⇒ it is still the best full-cost
classical algorithm and the baseline moves from `p^{1/2}` to `p^{4/9}`, tightening
the screen for every later candidate. Or a distinguished-point restructuring is
exhibited ⇒ `p^{1/3}` full cost, a stronger statement. Or VW at optimal `w`
dominates in this model ⇒ `KN-TECH-057`'s recommendation survives unchanged and
the new algorithm is *not* the full-cost baseline — an outcome worth having,
since the program would otherwise mis-screen.

**Cost.** Implementation **none**. Compute **none**.

**Ceiling.** `derivation` / cost-model correction. This is explicitly **not** an
attack and not an improvement; it is the yardstick. It must be run in the same
batch as B1-3 and B1-5, whose "gains" are meaningless without it.

**Kills it early.** Nothing kills it — the deliverable exists in every branch.
That is precisely why it is cheap and why it goes first alongside B1-3.

---

### B1-7. The Frobenius displacement field `δ(E)` — marginal law, autocorrelation, and whether it can be steered

**Claim.** Define `δ(E) = min{deg φ : φ : E → E^{(p)} separable}` — one integer
per vertex, `δ ≤ (p/2)^{1/3}` always. Two facts make it the natural tracked
object for this whole lane, and both are checkable: **(i)** `δ(E) = 1` iff
`j(E) ∈ F_p`, i.e. **the diagonal of Wesolowski's claw is exactly
Delfs–Galbraith's terminal condition** — the two algorithms are the same search
at two thresholds, `δ ≤ 1` and `δ ≤ X^2/B`; **(ii)** `δ` is Lipschitz on the
graph (`δ(E) ≤ ℓ^2 δ(E')` for `ℓ`-neighbours, by sandwiching with the isogeny
and its Frobenius-dual). The claim to decide: does `δ` have exploitable spatial
structure — long-range correlation, or a cheaply estimable gradient — that would
permit a **steered** walk toward small-`δ` vertices in fewer than the
`p^{1/2}` steps a blind Delfs–Galbraith walk needs? If yes, that is a new
algorithm with polynomial memory. If no, the null result closes the steering
route with a measured mechanism and simultaneously delivers the first
measurement of the `δ`-field this program has.

**Mechanism.** Predicted marginal (session derivation, unverified, from Hurwitz
class numbers): `#{E : δ(E) ≤ D} ≈ Σ_{d≤D} H(4dp) ≈ D^{3/2} p^{1/2}`, hence
`Pr[δ ≤ D] ≈ D^{3/2} p^{−1/2}`, hence `min_E δ = 1` at `D^{3/2}p^{1/2} = p^{1/2}`
(the `F_p`-locus, `≈ p^{1/2}` vertices ✓) and `max_E δ ≈ p^{1/3}` (the AOV bound
✓). Both endpoints of that prediction are independently known, which makes it a
genuinely falsifiable fit rather than a curve-fitting exercise. Autocorrelation:
compute `E[δ(E)δ(E')]` as a function of graph distance and compare with the
Ramanujan mixing prediction (decay to independence in `O(log p)` steps).

**Minimal discriminating test.** Toy scale, pure Python, exhaustive. For
`p ≡ 3 mod 4` with `p` up to `~10^4`: build the full supersingular `2`-isogeny
graph over `F_{p^2}` from `j = 1728` using the explicit `Φ_2`; build the left
`O_0`-ideal graph on the quaternion side; match them by simultaneous BFS from
the base point to realise the Deuring correspondence explicitly; then compute
`δ(E)` exactly for **every** vertex as `λ_1(P_O, Nrd/p)`. Measure: the marginal
CDF versus `D^{3/2}p^{−1/2}`; the distance-`r` autocorrelation for
`r = 1..4 log p`; and the success of three steering rules (greedy descent on
`δ`; descent on a cheap proxy; random walk as control) measured as steps-to-
reach-`δ ≤ D` at several `D`.

**Null object / control.** *(a)* A shape-matched random `3`-regular Ramanujan
graph on the same vertex count with a random fixed-point-free involution `σ`,
and `δ_σ` defined identically — this is the **critical** control, because it
isolates arithmetic from graph shape (see B1-8). *(b)* The same real graph with
the `δ`-labels randomly permuted across vertices, preserving the marginal and
destroying the spatial structure: any steering advantage that survives this
permutation is an artifact of the marginal, not of the field. *(c)* Radius-zero
control: greedy descent with the proxy replaced by a constant must reproduce the
random-walk numbers exactly.

**Falsifier (reachable).** Autocorrelation decays to the null envelope within
`O(log p)` steps at every tested `p`, and greedy descent is statistically
indistinguishable from the random walk after label permutation ⇒ **steering is
closed with a mechanism** (the field decorrelates at the graph's mixing rate, so
no local gradient exists), with forward guidance to non-local statistics. Or the
marginal departs from `D^{3/2}p^{−1/2}` ⇒ the class-number derivation is wrong
and B1-8's entire framework must be re-derived.

**Cost.** Implementation **high** (two graphs plus an explicit Deuring matching;
this is the most implementation-heavy toy instrument in the catalogue, and it is
reused by B1-8 and B1-9). Compute **low** (`p ≤ 10^4` is `≈ 10^3` vertices).

**Ceiling.** `toy`. Exhaustive enumeration at `p ≤ 10^4` supports statements
about those graphs and nothing else. The marginal law has a crypto-scale
counterpart via B1-1's sampler (which gives the `δ` marginal directly), but the
**autocorrelation does not** — there is no known shortcut for sampling a *ball*
around a curve on the quaternion side, and this must be stated in any write-up.

**Kills it early.** Verify on the smallest `p` that `δ(E) = 1` exactly on the
`F_p`-rational vertices, and that the vertex count matches `⌊p/12⌋ + ε_p`. If
either fails, the Deuring matching is wrong; stop.

**Delta versus `IDEA-20260804-84328c`.** That record tracks the unordered orbit
`{j(E), j(E)^p}` as a **bucket key** for two-stage collision search. This one
tracks a **scalar arithmetic invariant** `δ(E)` — a minimal degree, not an
identity key — measures its spatial law, and tests a steering algorithm. The
objects, the propagation rules, and the falsifiers are disjoint. This is a
successor in lane, not in object.

---

### B1-8. The partner-map exponent `θ_σ/γ_σ` as a one-number screen for "is there a better map than Frobenius?"

**Claim.** Every algorithm in this family — Delfs–Galbraith, the Frobenius-
conjugate line `[24, 26, 40]`, and the `p^{1/3}` algorithm — is the same
procedure applied to a **partner map** `σ` on the supersingular set, thresholded
on `δ_σ(E) = min deg(E → σ(E))`. If
`#{E : δ_σ(E) ≤ D} ≈ D^{γ_σ} · p^{1−θ_σ}`, then the minimum displacement over
the graph is `D_min = p^{θ_σ/γ_σ}`, the meet-in-the-middle table has size
`≈ D_min`, and the algorithm costs `p^{θ_σ/γ_σ}`. **The search for a better
algorithm in this family collapses to minimising a single scalar `θ_σ/γ_σ` over
candidate partner maps**, which turns an open-ended design question into a
measurable screen. Known points: Frobenius has `(γ, θ) = (3/2, 1/2)` giving
`1/3` ✓; a random fixed-point-free involution has `(2, 1)` giving `1/2` ✓ (and
recovers the pre-2026 exponent, confirming the frame); "has a small
endomorphism" (`σ = id`) has `(3/2, 1)` giving `2/3` ✓ (the standard "smallest
non-scalar endomorphism has degree `p^{2/3}`"). Three independent known values
fit — that is what makes it a screen rather than a story.

**Mechanism.** The `θ = 1/2` boost for Frobenius is arithmetic, not
combinatorial: the composite `ϕ ∘ φ` is an endomorphism of norm `d·p`, so the
factor `p` is **free**, and the relevant class number is `H(4dp) ≈ √(dp)` rather
than `H(4d) ≈ √d`. That factor `p` is the ramification of `B_{p,∞}` at `p`.
Since `B_{p,∞}` is ramified only at `p` and `∞`, **there is no second free
factor available inside `End(E)` alone** — which is the named obstruction, and
which points the search at exactly two escape routes: auxiliary level structure
(Eichler orders, `X_0(N)`-points, Atkin–Lehner `w_N`) and higher dimension
(`M_g(O)`, B1-10).

**Minimal discriminating test.** Two halves.
*(A) Derivation, zero compute.* Compute `(γ_σ, θ_σ)` for the candidate list:
`σ = w_N ∘ Frob` on supersingular points of `X_0(N)`; `σ = Frob` composed with
a fixed small-degree isogeny; the `(2,ε)`-structure map of `KN-LIT-7655`; the
opposite-order map `O ↦ O^{op}`. *(Session derivation for the first, unverified:*
the class number becomes `H(4dpN) ≈ √(dpN)` but the object count becomes `≈ pN`,
so `D_min = (pN)^{1/3} ≥ p^{1/3}` — level structure is **exponent-neutral**,
because the boost and the object count scale together.*)*
*(B) Measurement, toy scale, on B1-7's instrument.* For each `σ` realisable on
the toy graph, measure `(γ_σ, θ_σ)` by regression on the exhaustive
`δ_σ`-histogram across three graph sizes, and check that Frobenius returns
`(3/2, 1/2)` and the random involution returns `(2, 1)`.

**Null object / control.** The random fixed-point-free involution **with a
matched number of fixed points** (`≈ p^{1/2}`, to match the `F_p`-locus) — this
is the sharp control, because an involution with the right number of fixed
points but random elsewhere isolates precisely how much of the `3/2` exponent is
the `F_p`-locus and how much is the full class-number law. Second control: the
regression run on synthetic histograms drawn from the predicted law, to
establish that three graph sizes suffice to distinguish `γ = 3/2` from `γ = 2`.

**Falsifier (reachable).** Every candidate `σ` returns `θ_σ/γ_σ ≥ 1/3` ⇒ a
closure at the `docs/inventor-protocol.md` §4 standard: named obstruction (one
finite ramified prime, so one free factor), argument (the boost-vs-count
scaling), forward guidance (level structure is neutral — proved in (A); higher
dimension is untested — B1-10; non-involutive `σ` and correspondences rather
than maps are unexamined). Or the regression fails to recover the two known
points ⇒ the framework is mis-specified and must be withdrawn.

**Cost.** Implementation **low** given B1-7's instrument; **medium** standalone.
Compute **low**. Derivation half is free.

**Ceiling.** `derivation` + `toy`. The exponent pairs for `σ` other than
Frobenius are unverified session derivations; the toy measurement supports
claims about the toy graphs only. This screens candidates; it certifies nothing.

**Kills it early.** Compute `(γ, θ)` for `w_N ∘ Frob` on paper first. If the
level-neutrality argument holds, the most attractive candidate is gone in an
hour and the closure is already worth recording.

---

### B1-9. Cost curve for any per-vertex terminal filter: what a polynomial-memory `p^{1/3}` would require

**Claim.** A Delfs–Galbraith-shaped walk with terminal set
`A_M = {E : ∃ α ∈ End(E)\Z, Nrd(α) ≤ M}` (size `≈ min(M^{3/2}, p)`) costs
`p · C(M) / M^{3/2}` **with polynomial memory**, where `C(M)` is the per-vertex
membership-test cost. Hence: **any filter with `C(M) = M^{o(1)}` at
`M = p^{4/9}` gives `p^{1/3}` time and polynomial memory**, dominating the
`p^{1/3+o(1)}` algorithm on the memory axis — the axis the frozen text §1.1
names as "a serious obstacle for any deployment". The claim to decide is
whether *any* statistic computable from `j(E)` alone is enriched on `A_M` at
all. The idea is deliberately framed as a cost curve so that every candidate
filter, including ones not yet imagined, is scored by the same number.

**Mechanism.** Candidate per-vertex statistics computable from `j(E)` alone:
`Φ_ℓ(j, j^p)` and its valuation pattern for small `ℓ`; the norm/trace of
`j − j^p` in `F_{p^2}/F_p`; the `F_{p^2}`-factorisation type of `Φ_ℓ(j, X)`;
small-torsion group structure over small extensions; Weil/Tate pairing values on
small torsion; the cokernel pairing of `KN-LIT-7658` on `E(F_{p^2})/[m]`. One of
these is already known to be vacuous and should be recorded as such rather than
tested: **the Elkies–Atkin split type carries zero information here**, because
every supersingular `j` lies in `F_{p^2}` and `Φ_ℓ(j, X)` splits into `ℓ+1`
linear factors for *every* supersingular `E` — the type is constant across the
graph *(session derivation, unverified, but it follows directly from
`(ℓ+1)`-regularity and full `F_{p^2}`-rationality)*.

**Minimal discriminating test.** On B1-7's toy instrument, where `A_M` is known
exactly for every `M` (since `δ` and the full minima profile are computed for
every vertex): for each candidate statistic, measure the enrichment
`Pr[stat | E ∈ A_M] / Pr[stat]` across `M` on a log grid and across three graph
sizes, together with the measured `C(M)` in field operations. Plot the resulting
`p·C(M)/M^{3/2}` curve against the `p^{1/3}` line.

**Null object / control.** The shape-matched random Ramanujan graph with a
randomly assigned terminal set of identical density — any statistic showing
enrichment there is measuring bucket geometry. Second: label-permutation of the
terminal set on the real graph. Third: the `M = O(1)` corner must reproduce
plain Delfs–Galbraith's `p^{1/2}` step count exactly, as the baseline embedding.

**Falsifier (reachable).** No candidate statistic separates `A_M` from its
complement beyond the null envelope at any tested `M` and size ⇒ closure with a
named obstruction (**per-vertex invariants computable from `j` alone are
constant or near-constant on the `(ℓ+1)`-regular, fully `F_{p^2}`-rational
supersingular graph**), and forward guidance: information can only come from
*pairs* — `Φ_ℓ(j, j^p)` is the cheapest genuinely two-vertex statistic — or from
statistics aggregated over a neighbourhood. Or: some statistic *is* enriched,
`C(M)` is measured, and the cost curve either crosses `p^{1/3}` (a lead worth a
crypto-scale follow-up) or does not (a quantified, honest negative).

**Cost.** Implementation **medium** given B1-7 (the statistics are individually
cheap; the harness is the work). Compute **low**.

**Ceiling.** `toy`. A statistic enriched at `p ≤ 10^4` says nothing at `2^256`;
the deliverable at best is a *candidate* filter plus a measured cost curve, and
promotion would require a crypto-scale enrichment measurement that does not
currently have a sampling shortcut.

**Kills it early.** Confirm the Elkies–Atkin vacuity argument before building
anything — it removes the most obvious candidate at zero cost, and if it is
*wrong* that is itself the most interesting outcome in the entry.

---

### B1-10. Dimension-`g` displacement: does `g ≥ 2` beat `θ/γ = 1/3`?

**Claim.** B1-8's framework applied to superspecial abelian varieties. For
`g = 2`: walk in the `(2,2)`-isogeny graph from `E^2` to a random superspecial
principally polarised surface `A`, find a `(d,d)`-isogeny `A → A^{(p)}`, pull
back to get a non-scalar element of `End(E^2) = M_2(End E)`, and descend to
`End(E)`. Cost `= p^{θ_2/γ_2}` with `#{A : δ_2(A) ≤ D} ≈ D^{γ_2}·N_2^{1−θ_2'}`
and `N_2 ≈ p^3/2880`. **If `θ_2/γ_2 < 1/3`, this is an exponent improvement on
OneEnd / EndRing / Isogeny for elliptic curves**, cascading through the
published polynomial-time reductions exactly as the frozen text's Corollary 1.2
does. This is the operational form of `KN-OPEN-024`'s geometric reading ("does
the endomorphism ring of `E^g` give away more than that of `E`").

**Mechanism.** The two competing scalings, both to be computed rather than
guessed: the ball around `A` grows faster (`Σ_{d≤D} d^3 ≈ D^4` maximal isotropic
subgroups, versus `D^2` in `g = 1`), which helps; but the object count grows
faster too (`p^3` versus `p`), which hurts. The free-factor argument of B1-8
suggests the Frobenius boost in `g = 2` should involve `p^2` (the degree of
Frobenius on a surface), so `θ_2` may exceed `1/2` — but the mass formula that
fixes it is the Hashimoto–Ibukiyama class number of the quaternion hermitian
lattice, which this corpus does not hold and which cannot be retrieved here.
**Stating exactly which number is missing is half the deliverable.**

**Minimal discriminating test.** Two routes, run in order.
*(A) Derivation.* Write `#{A superspecial : ∃ (d,d)-isogeny A → A^{(p)}}` in
terms of the genus-2 mass formula and the count of `(d,d)`-isogenies, leaving
the mass constant symbolic; solve for `θ_2/γ_2` as a function of that constant;
determine **which values of the constant would give `< 1/3`** and how far they
are from the plausible range. If no value in the plausible range beats `1/3`,
the route closes without the literature.
*(B) Toy measurement, fallback.* At small `p`, enumerate superspecial surfaces
via Richelot `(2,2)`-isogenies on genus-2 curves and measure `(γ_2, θ_2)`
directly. Implementation is heavy and this is explicitly the fallback.

**Null object / control.** Route (A)'s `g = 1` specialisation must return
`(3/2, 1/2)` and `1/3`; a symbolic derivation that does not reproduce the known
case is wrong. For route (B): the random-involution control on a shape-matched
graph with `p^3` vertices and degree `≈ 15` (the `(2,2)`-graph degree), which
should return `θ/γ = 3/4`.

**Falsifier (reachable).** Route (A) shows `θ_2/γ_2 ≥ 1/3` for every mass
constant in the plausible range ⇒ closure with mechanism (higher dimension buys
ball volume and pays object count at least as fast), plus forward guidance
naming `g ≥ 3` and non-principally-polarised targets as untested. Or the descent
step `End(E^2) → End(E)` turns out to cost more than the search ⇒ the route dies
at the descent, which is a different and equally recordable obstruction.

**Cost.** Route (A): implementation **none**, compute **none**. Route (B):
implementation **very high**, compute **medium** — and it is the one entry in
this catalogue whose fallback may be beyond budget; say so rather than starting
it.

**Ceiling.** `derivation`, and **partially source-blocked**: the mass constant
is a literature quantity that cannot be fetched here. The deliverable must be
explicitly conditional on it, with the exact citation needed named so a later
session with network access can close it in minutes.

**Kills it early.** Do the `g = 1` specialisation check first. Ten minutes.

---

### B1-11. `KN-OPEN-024` descent audit: what input does the `M_g(O)` PIP algorithm actually need, and where is the circularity?

**Claim.** `KN-LIT-7641` reports heuristic expected polynomial time for the
principal ideal problem in `M_g(O)`, `g ≥ 2`, `O ⊂ B_{p,∞}` maximal, plus an
auxiliary method for finding endomorphisms of superspecial abelian varieties
with **prescribed kernel**. `KN-TECH-081` and `KN-OPEN-024` record the `g = 1`
case as unknown to this corpus. The audit to run is narrow and answerable
without the paper body: **what is the algorithm's input, and is that input
obtainable from `j(E)` alone in polynomial time?** Either it is (in which case a
route to EndRing exists and must be costed under `GOAL-SSI-001`'s charging
rules), or it is not (in which case the exact circularity is named, and the
entry stops being "two abstracts appear adjacent").

**Mechanism.** PIP takes an ideal *presented by a `Z`-basis*. On the geometric
side, a left `M_2(O)`-ideal corresponds to an isogeny of superspecial abelian
surfaces with known kernel. So the audit reduces to: can a `Z`-basis of a left
`M_2(O)`-ideal be written down from `j(E)` without already knowing
`O = End(E)`? The near-certain answer is no — `M_2(O)` cannot even be written
down without `O` — and the useful question is therefore the *contrapositive*
one: does the auxiliary prescribed-kernel result let one construct an
endomorphism of `E^2` from geometric data (a kernel subgroup of `E^2[N]`) that
is *not* already an endomorphism of `E`? That is the only non-circular door,
and it is exactly what a torsion-free attacker can or cannot walk through.

**Minimal discriminating test.** Zero compute. Produce a table with one row per
input of the reported algorithm: what it is, whether it is derivable from
`j(E)`, and if not, what would have to be computed first and at what cost.
Conclude with either (i) a costed non-circular route, or (ii) a named
circularity plus the exact list of facts that must be read from
`iacr:2026/454` to close the question (this list is the deliverable that
survives the network blackout).

**Null object / control.** Run the identical audit against the **commutative**
case (`KN-TECH-046`: cyclotomic PIP, quantum polynomial; short-generator
recovery via the log-unit lattice) where the answer is known, and confirm the
audit correctly reproduces the known two-stage structure — including that
Soliloquy died at stage 2, not stage 1. An audit instrument that flattens the
PIP / SG-PIP distinction is not fit for purpose; `KN-TECH-081` is explicit that
conflating them is "the easiest available way for this program to make a false
novelty or false-hardness call."

**Falsifier (reachable).** The audit finds the input requires `End(E)` ⇒ named
circularity, `KN-OPEN-024`'s (Q1) is untouched by any elliptic-curve attack
route, and forward guidance points at the prescribed-kernel auxiliary result as
the only non-circular door. Or it finds a door ⇒ a costed route that must then
be charged and red-teamed before any claim.

**Cost.** Implementation **none**. Compute **none**. Literature access
**blocked** — the audit is therefore explicitly conditional on abstracts, and
must say so in every sentence of its output.

**Ceiling.** `derivation`, source-blocked. It cannot resolve `KN-OPEN-024`; at
best it converts it from a two-abstract adjacency into a precise question with a
named missing fact. `KN-TECH-081`'s own limit applies unchanged: no hardness
assessment is made in either direction.

**Kills it early.** If the first row of the table ("a `Z`-basis of a left
`M_2(O)`-ideal") is not derivable from `j(E)`, the audit is complete and the
answer is the circularity. That is a one-page deliverable, and it is a real one.

---

### B1-12. Quaternion-side distribution test on *public* objects: SQIsign keygen output versus uniform maximal orders

**Claim.** SQIsign's security argument treats the public-key curve as
indistinguishable from a uniformly random supersingular curve. That is a
*distributional* assumption about a **public** object, and B1-1's sampler makes
it testable at crypto scale on the quaternion side: compare the invariant vector
`(λ_1(P), λ_2(P), theta head, largest prime factor of λ_1)` between (a) orders
produced by a keygen-model ideal walk and (b) orders produced by the
uniform-up-to-conjugation procedure. Outcome (i): a measurable divergence ⇒ a
scoped non-uniformity lead with a stated conversion path (a keygen-biased `λ_1`
lowers the `p^{1/3}` algorithm's effective per-attempt success probability by the
measured factor, which is a *charged* cost change, not a break). Outcome (ii):
no divergence at stated power ⇒ **a measured bound on keygen non-uniformity at
cryptographic scale**, which would be this program's first crypto-scale result
in the SSI lane.

**Delta versus SQI-FS-T0 (`IDEA-20260725-003` / `EV-SSI-006`), stated
precisely — required, or this is a duplicate.** SQI-FS-T0 froze the **signing
transcript** `T0` (commitment isogeny, challenge, response) from `KN-TECH-028` /
`KN-LIT-072` / `KN-LIT-073` and **classified** it against the Kani and Petit
*necessary conditions*, concluding
`T0_FAILS_KANI_AND_PETIT_NECESSARY_CONDITIONS`. This idea differs on all four
axes: **object** — the maximal order attached to the public *key*, not the
transcript; **data** — only what a key publishes, no signatures at all, so no
transcript model is needed and the SQI-FS-T0 freeze is not reused; **method** —
a two-sample distributional test on quaternion-lattice invariants, not a
necessary-condition classification; **verdict space** — a measured divergence or
a measured bound with stated power, not a binary classification. It is likewise
distinct from `IDEA-20260801-020`, which is a toy-scale transcript-vs-baseline
independence test under `RQ-SQISIGN-001`. A scope check against
`GOAL-SQISIGN-001` is required before dispatch so the two goals do not both
claim this lane.

**Mechanism.** Both distributions are generated as random ideal walks from a
special extremal order; they differ (if at all) in the norm profile and length
of the walk. Non-uniformity, if present, shows up first in `λ_1(P)` because that
is the quantity the `p^{1/3}` algorithm's success probability depends on.

**Minimal discriminating test.** `10^4` samples per arm at
`p = 5·2^248 − 1`; two-sample Kolmogorov–Smirnov and a permutation test on each
invariant; report `p`-values, the minimum detectable divergence at that sample
size, and the implied change in `1/P_0`.

**Null object / control.** *(a)* Two independent runs of the **same** sampler —
must not reject (calibrates the test). *(b)* A deliberately under-mixed walk
(length `1`, `log p / 4`) — **must** reject (establishes power). Without both,
a non-rejection is uninterpretable. *(c)* A shape-matched random-integer arm to
confirm the test is not merely detecting the `ρ(u)` shape.

**Falsifier (reachable).** The under-mixed positive control fails to reject ⇒
the test has no power and the run is void (instrument failure, not evidence).
The two-independent-runs control rejects ⇒ the sampler is not reproducible and
B1-1 is retroactively in question. Real arms reject with controls behaving ⇒ a
non-uniformity lead. Real arms do not reject with controls behaving ⇒ a bound.

**Cost.** Implementation **medium** on top of B1-1. Compute **medium**.

**Ceiling.** `crypto-scale distribution measurement` on a **model** of keygen.
**Source-blocked in part**: no SQIsign Round-3 specification is obtainable here
(`GOAL-SQISIGN-001` pause condition). The fallback is to declare the walk model
explicitly and label every output as a statement about *the declared model*, not
about SQIsign. Presenting a model result as a SQIsign result would violate
`AGENTS.md` rules 4 and 9; the model declaration is mandatory, not optional.

**Kills it early.** Run the two calibration controls before either real arm. If
power is inadequate at `10^4` samples, either raise the sample size or report the
detectability floor and stop — a floor is a legitimate deliverable.

---

## 2. Batches

Constraints honoured: at most three concurrent non-archive tasks per batch;
disjoint repository-relative write scopes; each batch decides something stated
in advance. Batch A carries no dependency and should launch first.

### Batch A — "What is the yardstick, and is the `o(1)` real?" (zero compute)

- **Ideas:** B1-3, B1-5, B1-6.
- **Objective.** Fix the program's post-2026 matched baseline and determine
  whether the two largest slack terms in the best-known algorithm — the
  superpolynomial `o(1)` and the memory axis — are mathematical or artifactual.
- **Grouping rationale.** All three are pure derivations over the same frozen
  text, they share no code, and B1-3's and B1-5's "gains" are uninterpretable
  without B1-6's charging model. Running them apart would produce two numbers
  measured on different rulers.
- **Budget.** No compute. Three derivation tasks; a small numeric optimiser for
  B1-3 only. Write scopes: one task directory each.
- **Decides.** (a) Whether `KN-TECH-057`'s baseline table must be superseded and
  by which exponent (`p^{4/9}` or `p^{1/3}` full cost). (b) Whether the
  superpolynomial `o(1)` is forced by isogeny-enumeration cost or removable in
  principle — and if removable, the exact enumeration obligation. (c) Whether any
  quantum exponent below `p^{1/4}` survives a charged memory model, and in which
  of four named models.

### Batch B — "Do we have a crypto-scale instrument at all?" (sequential inside)

- **Ideas:** B1-1 → B1-2 (dependent), B1-4 (independent, parallel).
- **Objective.** Build and validate the SageMath-free Deuring sampler by
  reproducing the frozen text's own Heuristic-1 experiment, then use it for the
  first new crypto-scale measurement in this lane.
- **Grouping rationale.** B1-2 is meaningless before B1-1's mass-formula and
  mixing checks pass, so they are sequential; B1-4 shares no code and fills the
  third slot without contention.
- **Budget.** Highest compute in the catalogue. Gate B1-2 on B1-1's stage-(a)
  and stage-(b) verdicts; do not spend the 256-bit sampling budget until the
  toy-scale mass formula agrees exactly.
- **Decides.** (a) Whether this program can measure anything at cryptographic
  scale in this lane without SageMath — a capability question that gates B1-12
  and any future heuristic validation. (b) The size of Remark 1's slack, and
  hence whether the "multiple small isogenies" route is exponent-moving (almost
  certainly not) or concrete-cost-moving (possibly). (c) Whether the
  large-prime variation is worth anything, or fails for the stated disanalogy
  with index calculus.

### Batch C — "Is there structure in the displacement field?" (toy scale)

- **Ideas:** B1-7 → {B1-8 measurement half, B1-9} (both dependent on B1-7's
  instrument).
- **Objective.** Build the explicit toy-scale Deuring matching, measure the
  `δ`-field's marginal law and autocorrelation, screen partner maps by
  `θ_σ/γ_σ`, and score per-vertex terminal filters on a cost curve.
- **Grouping rationale.** One shared instrument, three consumers. B1-8's
  derivation half is free and can run in Batch A's slack; only its measurement
  half belongs here.
- **Budget.** Implementation-heavy, compute-light (`p ≤ 10^4`). Cap the graph
  sizes in advance and pre-register the three sizes used for every regression.
- **Decides.** (a) Whether `δ` can be steered — i.e. whether a polynomial-memory
  algorithm better than the blind `p^{1/2}` walk exists in this family. (b)
  Whether any partner map beats Frobenius's `1/3`, or the one-ramified-prime
  obstruction closes the family. (c) Whether any statistic computable from
  `j(E)` alone enriches on `A_M`, or the `(ℓ+1)`-regularity obstruction closes
  per-vertex filters and pushes the search to pair statistics.

### Batch D — "Higher dimension and scheme scope" (mixed, partly source-blocked)

- **Ideas:** B1-10 (route A only), B1-11, B1-12.
- **Objective.** Test whether `g ≥ 2` offers a better displacement exponent,
  name the circularity (if any) in the `M_g(O)` PIP descent, and either bound or
  detect keygen-model non-uniformity at crypto scale.
- **Grouping rationale.** All three anchor `KN-OPEN-024` or the scheme-scope
  half of `KN-OPEN-013`, and all three are partly source-blocked — grouping them
  keeps the "what we could not fetch" accounting in one place instead of
  scattering caveats across the campaign. B1-12 depends on Batch B's sampler and
  must not launch before it.
- **Budget.** B1-10 route A and B1-11 are free. B1-12 inherits Batch B's
  compute. **Do not launch B1-10 route B** without an explicit budget decision;
  it is the one entry whose fallback may exceed what this campaign should spend.
- **Decides.** (a) Whether the `g = 2` route can beat `1/3` for any plausible
  mass constant, or closes without the literature. (b) Whether the `M_g(O)`
  result has a non-circular door to EndRing, and exactly which facts must be read
  from `iacr:2026/454` to settle it. (c) Whether the keygen-model curve
  distribution is distinguishable from uniform at `10^4` samples, or a
  detectability floor is the honest answer.

---

## 3. Honest accounting (`docs/inventor-protocol.md` §5)

**Objects considered.** O1–O9 of §0.3. The one that survives the
lossy-projection test most cleanly is **O2, the Frobenius displacement `δ(E)`**:
it is a single integer extracted from a rank-4 lattice, its fibres have average
size `≈ p^{2/3}`, and it propagates with a proved one-step Lipschitz constraint
`δ(E) ≤ ℓ^2 δ(E')`. O1 is explicitly *not* claimed as a new object — the full
minima profile plus Gram data recovers the lattice, so it is a change of
coordinates, and B1-2 is labelled a distribution measurement accordingly. O5 is
an oracle, not a state, and is audited as such.

**Depth of verified structure.** Zero. No experiment was run, no measurement
taken, no literature verified. Every derivation in this file is labelled
*(session derivation, unverified)*, and three of them (the AOV-forced skewness of
`(P, Nrd/p)`; the `D^{3/2}p^{1/2}` displacement count; Ford's
`δ ≈ 0.086` divisor-window density) are load-bearing for B1-2, B1-8 and B1-3
respectively and **must be checked before those ideas are dispatched**. Three
independent known points fit the B1-8 framework (Frobenius `1/3`, random
involution `1/2`, identity `2/3`), which is evidence the frame is right and is
not evidence any conclusion drawn in it is.

**`dominated_by`.** `n/a (no result claimed)` — no idea in this catalogue
asserts an algorithm, bound, or improvement. For completeness, the frontier every
proposal here would have to beat, checked row by row: `p^{1/3+o(1)}` time and
memory conditional on Heuristic 1 (`KN-LIT-7563`); `p^{1/2}` VW full cost with
polynomial memory (`KN-TECH-057`); `p^{1/4}` step count / `p^{1/3}` DG full cost
for `F_p`-rational instances (`KN-TECH-057`, VW variant conditional on unproven
`F_p` mixing); `Õ(p^{1/4})` quantum in a different machine model
(`KN-LIT-079`); `p^{1/2+o(1)}/w^{1/2}` at memory `w` (van Oorschot–Wiener, frozen
text §1.1). Every proposal above is dominated by at least one of these rows on
every axis, because none of them exists yet.

**`sota_delta`.** Zero. Quantitatively: the conditional targets named in the
catalogue are B1-3 (removal of a superpolynomial `o(1)`, worth roughly `2^{18}`
at NIST-I against the frozen text's `2^{106.5}` *if* both of its obligations
resolved favourably — they are unresolved), B1-5 (`p^{1/6}` or `p^{2/9}` quantum
versus `p^{1/4}`, i.e. `1/12` or `1/36` of exponent, *conditional on a charging
model that may not be defensible*), B1-8/B1-10 (any `θ_σ/γ_σ < 1/3`), and
B1-9 (`p^{1/3}` time at polynomial memory, no time gain but a memory-axis
domination). None is claimed. The measured delta today is `0`.

**Enumerated closures** — each with obstruction, argument, and forward guidance,
all *(session derivation, unverified)*; each is a candidate for the record, not a
record.

1. **Enlarging `X` (equivalently `B`) does not move the exponent.** Obstruction:
   the cost is `X^2 · ρ(u) · B^{κ} / ρ(u_0)`, and raising `X` by `p^ε` costs
   `p^{2ε}` in table size while buying at most `p^{o(1)}` in success
   probability, because the smoothness density is already `p^{−o(1)}`. Argument:
   the exponent is stationary at `ε = 0`; this trade *is* the `B`-optimisation
   the frozen text already performs. Forward guidance: only the per-entry cost
   `κ` and the success-probability *model* are movable — B1-3 and B1-4.
2. **Re-randomising until the minimal degree is small (rather than smooth) does
   not move the exponent.** Obstruction: `Pr[δ ≤ p^{1/3−ε}] ≈ p^{−3ε/2}` while
   the table shrinks only to `p^{1/3−ε}`, giving `p^{1/3+ε/2}`. Argument: the
   `3/2` in the class-number count is precisely the balance point. Forward
   guidance: only a partner map with a different `(γ, θ)` escapes — B1-8.
3. **Level structure is exponent-neutral.** Obstruction: on `X_0(N)` the
   class-number boost `√(pN)` and the object count `pN` scale together, giving
   `D_min = (pN)^{1/3} ≥ p^{1/3}`. Argument: the boost originates in
   ramification, and adding level adds objects at the same rate. Forward
   guidance: higher dimension (B1-10) and non-involutive correspondences remain
   untested; a *determined* rather than *chosen* level might break the scaling,
   but no construction is known.
4. **There is no second free factor inside `End(E)` alone.** Obstruction:
   Frobenius's `θ = 1/2` boost is the ramification of `B_{p,∞}` at `p`, and
   `B_{p,∞}` is ramified only at `p` and `∞`. Argument: the composite
   `ϕ ∘ φ` has norm `d·p` with the `p` free, which is what turns `H(4d)` into
   `H(4dp)`. Forward guidance: escapes require auxiliary structure (closed by
   closure 3) or higher dimension (open, B1-10).
5. **Elkies–Atkin split types carry zero information here.** Obstruction: every
   supersingular `j` lies in `F_{p^2}` and `Φ_ℓ(j, X)` splits into `ℓ+1` linear
   factors for every supersingular `E`, so the factorisation type is constant
   across the graph. Argument: `(ℓ+1)`-regularity plus full `F_{p^2}`-rationality.
   Forward guidance: two-vertex statistics — `Φ_ℓ(j, j^p)` first — and
   neighbourhood aggregates are untouched by this argument (B1-9).
6. **Known-`End` anchor sets do not reproduce the Frobenius advantage.**
   Obstruction: MITM between a ball of radius `X` around `E` and a ball of
   radius `Y` around an anchor set of size `p^a` balances at `p^{1/2}`; only
   `|A| ≥ p^{2/3}` with *free* recognition helps. Argument: a generic anchor set
   has no class-number boost, so `γ = 2, θ = 1`. Forward guidance: this is
   exactly the polynomial-memory question of B1-9, and it is open, not closed.
7. **The `p^{1/3}` table has no invariant set for a rho-style walk.**
   Obstruction: `L(E, X, B)` is defined relative to `E` and is closed under no
   natural self-map, so distinguished-point collision search has nothing to
   iterate on. Argument: this is why the memory cannot be traded by the usual
   route, and it is the mechanism behind the frozen text's own "it is currently
   unclear how to reduce the memory cost." Forward guidance: B1-6 sub-question
   (a) and B1-9's polynomial-memory route are the two live escapes.

Each of these is a statement about a *mechanism*, not a count of screened
candidates, and each names what remains open — the `docs/inventor-protocol.md`
§4 standard. None declares any direction impossible.

**Open directions for the next session.**

- The three load-bearing recollections above (AOV-forced skewness; the
  `D^{3/2}p^{1/2}` count; Ford's divisor-window density and its constant) need
  verification the moment network access exists. Until then B1-2, B1-3 and B1-8
  are conditional on them and must say so.
- `KN-OPEN-019` — the written object enumeration — remains unwritten. §0.3 above
  is a nine-row sketch for the *isogeny* side only, produced as a by-product;
  it is not the ECDLP taxonomy `KN-OPEN-019` asks for and must not be cited as
  one.
- The `(2,ε)`-structure line (`KN-LIT-7655`) and the CM-terminal line
  (`KN-LIT-7580`) are, per `KN-LIT-7655`'s own note, two independent 2026
  attacks on the same Delfs–Galbraith bottleneck. B1-8's screen gives them a
  common scalar. Running it on both is cheap and has not been done.
- `KN-LIT-7656`'s "forensic categories" axiomatisation is, read adversarially, a
  list of the structural properties SQIsign requires of the Deuring
  correspondence — i.e. a list of computations to price. Nothing in this
  catalogue uses it. That is a deliberate omission for scope, not a judgement,
  and it is the most obvious unexplored entry point for the next session.
- `KN-LIT-7658`'s cokernel pairing gives a non-degenerate bilinear form on
  `E(F_q)/[m]E(F_q)`, an object no family in §0.3 tracks. It appears in B1-9's
  candidate list only; whether it is a tracked object in its own right is
  untested.
- The "unusually easy instance" transform of `KN-OPEN-028` (Q2) — re-randomise
  the instance *representation* until a tractable instance appears — is
  instantiated in this catalogue only in the form the frozen text already uses
  (walk until smooth). Whether a second re-randomisation axis exists in the
  isogeny setting is open and was not resolved here.

**Novelty status for this entire catalogue: `unverified`.** The corpus
(`knowledge/`) and ledger (`ledger/proposals/`) were read for prior art and
duplicates, and the off-limits list of §0.2 plus the explicit deltas in B1-7 and
B1-12 record what that check found. External literature could not be checked:
eprint and arXiv are unreachable from this environment. Nothing here is claimed
new; nothing here is dismissed as known.
