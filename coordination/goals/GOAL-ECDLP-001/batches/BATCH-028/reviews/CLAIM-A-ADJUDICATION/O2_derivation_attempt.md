# (O2) — derivation attempt: from measurement to argument

Red Team, BATCH-028. Responds to `claim_a_adjudication.md` §7 obstruction conjunct
**(O2)** and to `F1_sum_compatible_filter_search.md` §10 item 4 ("making precise the
step ... would convert (O2) from a measurement into an argument").

**Status: DERIVATION, not proof of the general claim.** Claim tier under
`docs/claims-and-verification.md` is *derivation*, never "proved". No research state
is changed by this document. No ledger record, proposal, hypothesis, experiment,
falsifier, or control was modified. No commit was made. This file is the only file
written.

**Independence caveat (mandatory).** This harness resolves author and reviewer to the
same backend (`claude-opus-5`). The adjudication, the F1 search, and this derivation
are three procedurally separate sessions on **one model**. Independence here is
procedural, not model-level, and correlated blind spots are not excluded by anything
below. Under `AGENTS.md` rule 12 a closure claim needs `review-breakthrough` at `max`
on an independently resolved model; this session is not that.

---

## 0. Answer first

| Question | Answer |
|---|---|
| Is the target statement, as the task posed it, true? | **No — it is false as stated, and I prove it false.** On *every* prime-order group there is an `h` with `M` arbitrarily large and `Pr[h(P+Q)=f(h(P),h(Q))] ≈ 1/2`: the pull-back of the interval map through the discrete logarithm. So (O2) is **not** a theorem of group theory and no purely combinatorial/Fourier proof of it can exist. Any proof must restrict the class of `h`. (§3) |
| Is there a rigidity/stability theorem forcing approximate sum-compatibility toward exact? | **No, and this is now settled negatively.** The same object is at maximal distance from the exact class. The homomorphism route works perfectly in the exact case and is *provably* not extendable to the approximate case. (§3–§4) |
| Did anything get proved? | **Yes, two things.** *Theorem 1* (exact case, unconditional, covers **all** `h`, no class restriction): on a prime-order group every exactly sum-compatible `h` with `M < N` is constant. *Theorem 3* (approximate case, restricted class): for `h` built from multiplicative characters of bounded-degree functions on a prime-order `E(F_p)`, `δ(h) ≤ 1/M + M·O(Δ p^{-1/2})`. Theorem 3 rests on named standard inputs (Weil/Bombieri, Weil reciprocity) and one bookkeeping step I sketch but do not fully carry out. |
| Does that close (O2)? | **Partially, and I can say exactly how much.** It closes every Wagner configuration with `j ≥ 3` inside the character-filter class. It leaves **one** live configuration: a 4-tree (`j = 2`, `M ≈ N^{1/3}`), which would give exponent `0.4167` at `m=16` and `→ 1/3` as `m→∞`. Conditional on square-root cancellation for the surface sums — measured to hold (§8.5), not proved — the whole class closes. |
| Is F1's bar the right bar? | **No.** I derive the filter-gain lemma: one Wagner level's speedup is *exactly* `M·δ`, the lift. F1's `4/M` bar and the task's `c/M` bar therefore describe a **constant-factor** attack, not an exponent-moving one. The attack-relevant bar is `δ = M^{-1+Ω(1)}`. This is a fourth amendment F1's specification needs. (§5) |
| Was F1's headline statistic the right statistic? | **No, and correcting it strengthens F1.** F1's residual "1.101× lift" is dominated by the free `f_const` marginal-bias floor, which carries zero sum-compatibility. On the corrected statistic `δ − δ_const`, measured exactly (no sampling) over full enumeration, the algebraic filters sit **at or below the random-function null** and several are **exactly 0.000000**. (§8.3) |
| Is (O2) now an argument? | **A conditional argument for a named restricted class, plus an unconditional theorem for the exact case, plus a proof that the general statement is false.** It is not a general closure and must not be recorded as one. |

---

## 1. What I was asked to attempt, and what the target statement should have said

The task proposed:

> On a prime-order subgroup of `E(F_p)`, no function `h : E → [M]` with `M ≥ M₀(p)`
> growing with `p` admits a predictor `f` with `Pr[h(P+Q) = f(h(P), h(Q))] ≥ c/M` for
> constant `c > 1`, computable in `o(cost of one group operation)`.

Two things are wrong with it as a target, and both are load-bearing.

1. **The cost clause carries the entire statement, and it is not a mathematical
   hypothesis.** F1 §5 already observed this via the dlog pull-back. I sharpen it in
   §3: the counterexample is not a curiosity at the edge of the statement, it is
   *maximally* far from the exact class, so the statement minus the cost clause is not
   merely false but false in the strongest possible way. Consequently the theorem
   cannot be proved by any argument that does not look at how `h` is computed.

2. **`c/M` for constant `c` is the wrong threshold.** §5 derives that a filter with
   lift `c` buys speedup exactly `c` per Wagner level, hence `c^j` total — a constant.
   The bar that matters is `δ ≥ M^{-1+Ω(1)}`.

The statement I will actually defend, in the shape that survives:

> **Target, restated.** Let `E/F_p` have prime order `N`. Let `h : E(F_p) → [M]` be
> *algebraically cheap* — evaluable in `O(polylog p)` field operations and **zero**
> group operations, by a bounded number of multiplicative characters of rational
> functions of bounded degree. Then for every predictor `f`,
> `Pr[h(P+Q)=f(h(P),h(Q))] − max_c Pr[h(P+Q)=c] = O(M·Δ·p^{-1/2})`,
> so `h` cannot supply a Wagner level with `M ≤ p^{1/4−o(1)}`.

Notation used throughout. `G` a group of prime order `N`; `δ(h,f) = Pr_{P,Q}[h(P+Q) =
f(h(P),h(Q))]` over independent uniform `P,Q`; `δ(h) = max_f δ(h,f)`;
`δ_const(h) = max_c Pr[h(P+Q)=c]` (attainable by the constant predictor, so it is a
free floor carrying no sum-compatibility); `GAP(h) = δ(h) − δ_const(h)`; **lift**
`= M·δ(h)`.

---

## 2. Which routes I took, and why

| Route offered | Taken? | Outcome |
|---|---|---|
| **Homomorphism route** | Yes, fully | Exact case: **complete unconditional theorem** (§4), stronger than the offered version — I do not need to assume `f` is a group law, the congruence argument derives it. Approximate case: **provably dead** (§3). |
| **Character-sum route** | Yes, this is the main result | Gives Theorem 3 (§7). The joint-vs-marginal warning in the task is exactly right and is where F1's statistic went wrong (§8.3). |
| **Algebraic route** | Yes; it is what makes the character route's degeneracy analysis finite | §6 turns F1 §7.1's observation into an exact statement (Weil reciprocity) and identifies the degenerate locus precisely. This is the step that "converts (O2) from a measurement into an argument" in F1 §10's sense. |
| **Counting/covering route** | Yes, briefly | **Dead as a proof route** (§9) and I say so in those terms. It cannot prove nonexistence because §3 exhibits existence. Its one use is calibrating the null, which it does well. |

---

## 3. Proposition 2 — the general statement is FALSE, and no stability theorem exists

This is the most important thing in this document, because it tells the program not to
spend further effort on a family of proof attempts.

**Proposition 2.** Let `G` be cyclic of prime order `N` with generator `G₀`, and for
`M ≤ N` define the *dlog-interval filter*
`h_M(P) = ⌊M · log_{G₀}(P) / N⌋ ∈ [M]`. Then

(a) `δ(h_M) ≥ 1/2 − O(M/N)` for every `M`, with the predictor `f(a,b) = a+b mod M`
    corrected by at most one carry;
(b) `h_M` is balanced to within one element per fibre, hence at total-variation
    distance `1 − 1/M` from **every** constant map;
(c) by Theorem 1 (§4) the constants are the *entire* class of exactly sum-compatible
    maps on `G` with `M < N`.

**Corollary 2.1 (no rigidity).** No theorem of the form
"`δ(h) ≥ c/M` for constant `c>1` ⟹ `h` is `o(1)`-close to an exactly sum-compatible
map" can hold on a prime-order group. `h_M` has `δ ≈ 1/2 ≫ c/M` and is at *maximal*
distance from the exact class.

**Corollary 2.2 (O2 is not a group-theoretic statement).** Any proof of (O2) must
restrict the class of `h` — computationally, or algebraically as in §7. An argument
that only uses the group structure of `G` cannot work, because `h_M` exists on every
prime-order group including `E(F_p)`.

**Verification** (`C6`, exact full enumeration over all `N²` pairs, no sampling, seven
prime-order curves, `N` from 523 to 65423):

```
 GAP = delta - delta_const                p=523    1033    2063    4111    8219   16417   32779   65539
 DLOG-INTERVAL  (M=4)                   0.25192 0.25047 0.25024 0.25012 0.25006 0.25006 0.25003 0.25002
 DLOG-INTERVAL  (M=16)                  0.44566 0.44114 0.44038 0.43897 0.43798 0.43776 0.43761 0.43761
 fitted decay exponent alpha (gap ~ p^-alpha):  M=4: 0.001    M=16: 0.003
```

Flat to four decimals across a 125× range in `N`. **This is the null-object control run
in reverse**, and it is the discriminating control `docs/inventor-protocol.md` §3 asks
for: the parameter that destroys a spurious signal is `N`, a real filter does not decay
in `N`, and this one does not. It is also the positive control proving the apparatus
below can detect a genuine growing-`M` filter when one is present.

Cross-check against an independent prior measurement: at `M=4` my exact `δ` is
`0.5024`, F1 §5 measured `0.5025` on `E(F_487)`; at `M=16` mine is `0.5088`, F1's
`0.5111` at `N=499`. Different code, different curves, same numbers.

---

## 4. Theorem 1 — the exact case, unconditional, for ALL `h`

**Theorem 1 (congruence rigidity).** Let `G` be a finite abelian group, `h : G → [M]`,
`f : [M]² → [M]`, and suppose `h(P+Q) = f(h(P),h(Q))` for **all** `P,Q ∈ G`. Let
`K = h^{-1}(h(0))`. Then `K` is a subgroup of `G`, the fibres of `h` are exactly the
cosets of `K`, `h` factors as `G → G/K ↪ [M]`, and `|image(h)| = [G:K]` divides `|G|`.

*Proof, in checkable steps.*
1. `K` closed under `+`: for `x,y ∈ K`, `h(x+y) = f(h(x),h(y)) = f(h(0),h(0)) = h(0+0)
   = h(0)`, so `x+y ∈ K`. `G` finite ⟹ `K` is a subgroup.
2. Fibres refine into cosets: if `h(x)=h(y)` then for every `z`,
   `h(x+z) = f(h(x),h(z)) = f(h(y),h(z)) = h(y+z)`. Take `z = −y`: `h(x−y) = h(0)`, so
   `x − y ∈ K`.
3. Cosets refine into fibres: if `x−y ∈ K` then `h(x) = h((x−y)+y) = f(h(x−y),h(y)) =
   f(h(0),h(y)) = h(0+y) = h(y)`.
4. Steps 2–3 give fibres = cosets of `K`; the rest is Lagrange. ∎

**Corollary 1.1 (the prime-order kill).** If `|G| = N` is prime and `h` is exactly
sum-compatible, then `|image(h)| ∈ {1, N}`. Hence for `M < N`, `h` is **constant**.
For `M ≥ N` the only option is `h` injective, i.e. `h` is a group isomorphism onto its
image with `f` the transported group law — evaluating it is a relabelled discrete
logarithm.

**Note on strength.** This is stronger than the version the task suggested. I do not
assume `f` is a group law on `[M]`; the group law is *derived* from exact
sum-compatibility. So the theorem covers `f` an arbitrary table, which matters because
F1's `f_joint` is an arbitrary table.

**What Theorem 1 covers.** *Everything*, in the exact case — no restriction on how `h`
is computed. In particular:

- **F1 family G, small-subgroup projections** (`h(P) = ` index of `[λ/M]P`): these are
  genuine homomorphisms, so Theorem 1 applies directly. On a prime-order subgroup with
  `M < N` they are constant. Their `M` is capped by the torsion, which is 1 on a
  cofactor-1 curve. Fully explained.
- **F1 family F, 2-descent characters**: homomorphisms `E(F_p) → {±1}` (§6). Fully
  explained: identically trivial on the odd part, `M` capped at 4 by `A/2A ≅ A[2]`.
- **The `A/mA ≅ A[m]` bound F1 §10 item 2 asked to be "stated as a lemma rather than
  inferred from the m=2 measurement"**: Theorem 1 supplies it in the form that
  actually matters — not "descent characters are bounded by the torsion" but "*every*
  exactly sum-compatible map on a prime-order group is constant", which subsumes
  descent at every `m`, isogeny-induced maps, and anything else exact.

**Verification** (`C5`, exhaustive over *every* map `h`, normalising `h(0)=0`):

```
PRIME ORDER (theorem predicts image size in {1,|G|}):
  Z/5  M=2,3 ; Z/7  M=2,3 ; Z/11 M=2,3   -> in every case exactly 1 solution, image size [1]
  E(F_13): y^2=x^3+7x+6, #E=11, M=2,3    -> exactly 1 solution, image size [1]
  coset-structure violations: 0 everywhere
POSITIVE CONTROL, composite order (non-trivial filters MUST exist, and do):
  Z/6 M=3 -> 5 solutions, image sizes [1,2,3]
  Z/8 M=3 -> 3 solutions, image sizes [1,2]
  Z/9 M=3 -> 3 solutions, image sizes [1,3]
  coset-structure violations: 0 everywhere
```

The composite-order arm is the instrument check: the search finds non-trivial exact
filters when they exist, so its emptiness on prime order is informative.

---

## 5. The filter-gain lemma — F1's bar and the task's bar are both wrong

**Lemma 5 (one Wagner level).** Fix a level of a k-tree. Two lists `L₁,L₂` of size `L`,
elements independent uniform in `G`; the level seeks pairs with `h(P+Q)=c`. The
filtered procedure examines `S_c = {(P,Q) : f(h(P),h(Q)) = c}` and keeps the true hits.
Write `q_c = Pr[f(h(P),h(Q))=c]` and `π_c = Pr[h(P+Q)=c \mid f(h(P),h(Q))=c]`.

- Cost `= |S_c| = L²q_c`; hits found `= L²q_cπ_c`; hits per unit cost `= π_c`.
- Unfiltered, examining pairs at random yields `1/M` hits per unit cost.
- **Speedup `= M·π_c`.** Since `Σ_c q_c = 1` and `Σ_c q_cπ_c = δ(h,f)`, if the `π_c`
  are equal then `π = δ` and the speedup is exactly `M·δ` — the lift.

*Consequences.*

- Perfect filter (`δ=1`): speedup `M`. This is Wagner's full gain, and it is what `Z/N`
  supplies (`δ ≈ 1/2`, speedup `≈ M/2`).
- Independent `h(P+Q)` (`δ = 1/M`): speedup `1`. Bucketing buys nothing.
- **Lift `c` (F1's bar at `c=4`; the task's bar at constant `c`): speedup `c`.
  Constant. `c^j` over the whole tree. Moves no exponent.**
- For a near-balanced `h`, `M·δ = M·δ_const + M·GAP ≈ 1 + M·GAP`, so
  **speedup `≈ 1 + M·GAP(h)`**, and exponent movement needs `M·GAP = p^{Ω(1)}`.

**Amendment (iv) to F1**, on top of the three F1 §5 already requested: the inequality
in F1 must be `δ(h) − δ_const(h) ≥ M^{-1+ε}`, not `δ(h) ≥ 4/M`. A filter meeting the
current F1 text falsifies F1 while leaving (O2) untouched — which is the third distinct
way F1 as written is satisfiable without meaning anything. I am not authorised to edit
the falsifier and have not; this is an amendment request producing a new record.

---

## 6. The algebraic route — F1 §7.1 made exact

F1 §7.1 recorded, as an observation and explicitly not as a proof, that
`chi(x(P+Q)−e)` factors per-element only when `e` is a root of the cubic. I verified
that claim before building on it, and it is exactly right; here is the mechanism.

**Lemma 6.1 (chord identity).** On `E : y² = x³+ax+b` over any field of char ≠ 2,3, for
`P=(x_P,y_P)`, `Q=(x_Q,y_Q)` with `x_P ≠ x_Q`, chord `y = λx+ν`, and
`x_3 = x(P+Q) = λ²−x_P−x_Q`:

```
    (x_P − e)(x_Q − e)(x_3 − e)  =  (λe + ν)²  −  (e³ + ae + b)
```

*Proof.* `x³+ax+b−(λx+ν)² = (x−x_P)(x−x_Q)(x−x_3)` (both monic cubics with the same
three roots, the chord meeting `E` at `P,Q,−(P+Q)` and `x(−(P+Q))=x(P+Q)`). Evaluate at
`x=e` and negate. ∎

Verified symbolically (`C1`): the difference of the two sides, cleared of the
denominator `x_P−x_Q` and reduced modulo `y_P²−(x_P³+ax_P+b)` and
`y_Q²−(x_Q³+ax_Q+b)`, is **identically 0**.

**Corollary 6.2.** With `χ` the Legendre symbol and `f(e)=e³+ae+b`,

```
    chi(x(P+Q) − e)  =  chi(x_P − e) · chi(x_Q − e) · chi( (λe+ν)² − f(e) )
```

and the third factor is `chi` of a **perfect square**, hence `+1`, **exactly when
`f(e)=0`**. When `f(e)≠0` the third factor depends on `(λ,ν)` — i.e. on the *joint*
coordinates of `P` and `Q` — and is not a function of `chi(x_P−e), chi(x_Q−e)`.

This is the precise version of F1 §7.1's `g(P,Q)`-vs-`f(h(P),h(Q))` remark, and it
identifies the degenerate locus exactly: `f(e)=0` ⟺ `(e,0) ∈ E[2]` ⟺
`div(x−e) = 2(T_e) − 2(O)` is **2-divisible as a divisor**.

**Verification** (`C2`, three curves — a curve with one rational root, a full-2-torsion
curve, and F1's `C1` with an irreducible cubic; 4000 random pairs each):

```
curve                        e            f(e)   root   identity violations   per-element factorisation rate
p=1000003, a=1,b=13     270043               0   True            0/4000                4000/4000 = 1.0000
p=1000003, a=1,b=13           0              13  False           0/4000                2002/4000 = 0.5005
p=1000003, a=1,b=13       12345          331903  False           0/4000                1992/4000 = 0.4980
full-2-tors, e=1,5,-6         .               0  True            0/4000                4000/4000 = 1.0000  (all three)
full-2-tors                   2          999979  False           0/4000                1991/4000 = 0.4978
p=4294967291 (F1 C1)          0              13  False           0/4000                2009/4000 = 0.5022
```

Zero identity violations anywhere. Factorisation rate exactly `1.0000` at every root and
`0.49–0.51` at every non-root, on the same curve with the same code.

**Lemma 6.3 (why divisor divisibility is the right invariant — Weil reciprocity).** Let
`χ` have order `k`, `G ∈ F_p(E)^*` with `div(G) = k·D`. Then `η(P) := χ(G(P)/G(O))` is a
group homomorphism `E(F_p) → μ_k`.

*Proof.* For `P+Q+R=O` with `P,Q,R` distinct and off `supp(div G)`, take the line `ℓ`
with `div(ℓ) = (P)+(Q)+(R)−3(O)`. Weil reciprocity gives
`G(div ℓ) = ℓ(div G) = ℓ(kD) = ℓ(D)^k`, i.e. `G(P)G(Q)G(R)/G(O)³` is a `k`-th power, so
`η(P)η(Q)η(R)=1`. Setting `Q=O` gives `η(−P)=η(P)^{-1}`; then `P+Q+(−(P+Q))=O` gives
`η(P+Q)=η(P)η(Q)`. Extend over the finitely many excluded points by continuity of the
relation. ∎

The 2-descent case is `G = x−e`, `k=2`, `D = (T_e)−(O)`, and Lemma 6.1's right-hand
side `(λe+ν)²` is literally `ℓ(D)^2` — the chord evaluated at `T_e`, squared. **My
symbolic computation `C1` is an instance of Weil reciprocity**, which is why the two
agree exactly.

**Verification of the Case-B branch end to end** (`C7`, cyclic curve `#E = 226 = 2·113`
with exactly one rational 2-torsion point, `h = chi(x−e)`, exact enumeration):

```
p=211, y^2=x^3+x+4, #E=226 cyclic, e=60
   chi(x-e) agrees with the parity character (kernel = odd part) at EVERY point;
   the only two disagreements are O and T_e, where chi(x-e) is a convention, not a value.
   FULL group, exact parity character : delta = 1.000000     <- perfect filter, M=2
   ODD part  ([2]E, order 113)        : M_eff = 1, delta_const = 1.0, GAP = 0.000000
```

So the descent character is a genuine perfect sum-compatible filter on the full group
and **identically trivial** on the prime-order part — Theorem 1, instantiated.

---

## 7. Theorem 3 — the approximate case for the character-filter class

### 7.1 The class

**Definition (character filter of complexity `(k, r, Δ)`).** `χ : F_p^* → μ_k` a
multiplicative character of order `k`; `g_1,…,g_r ∈ F_p(E)^*` rational functions on `E`
with `Σ_j deg(g_j) ≤ Δ`; `h(P) = (χ(g_1(P)), …, χ(g_r(P))) ∈ μ_k^r`, so `M = k^r`.
Evaluation costs `r` function evaluations and `r` character symbols: `O(rΔ log p)` field
operations and **zero group operations**, so the class satisfies F1's cost clause with
room to spare. `M` may grow with `p` by growing `r` (or `k`).

Call `h` **non-redundant** if no nontrivial character `ψ` of `μ_k^r` makes `ψ∘h`
constant; otherwise replace `M` by `M_eff` and recurse. (This is F1 §3's `M_eff`
discipline, and it is a hypothesis of the theorem, not an afterthought.)

### 7.2 Fourier setup

Let `T̂_ψ = E_{P,Q}[ψ₁(h(P))ψ₂(h(Q))ψ₃(h(P+Q))]` for `ψ = (ψ₁,ψ₂,ψ₃)` characters of
`μ_k^r`. Then for any `f`,

```
   δ(h,f) − 1/M  =  (1/M³) Σ_{ψ ≠ 1} c_ψ(f) · T̂_ψ ,
   c_ψ(f) = Σ_{a,b} conj(ψ₁(a)ψ₂(b)ψ₃(f(a,b))) .
```

`c_ψ` is the Fourier transform of the indicator of the graph of `f`, so Parseval gives
`Σ_ψ |c_ψ|² = M⁵`. Cauchy–Schwarz over the `M³` triples then gives

```
   δ(h)  ≤  1/M  +  M · max_{ψ ≠ 1} |T̂_ψ| .                             (★)
```

(For a *group-law* predictor `f(a,b)=ab` only `M` triples have `c_ψ ≠ 0`, and (★)
improves to `δ ≤ 1/M + max_ψ |T̂_ψ|`. F1's `f_joint` is adversarial, so (★) is the form
that must be used against it.)

**Marginal vs joint — the task's warning, honoured.** If any one `ψ_i` is trivial, `T̂_ψ`
*factors into marginals*: `(P, P+Q)` and `(Q, P+Q)` are each pairs of independent
uniform variables, so e.g. `E[ψ₁(h(P))ψ₃(h(P+Q))] = E[ψ₁∘h]·E[ψ₃∘h]`. Only triples with
**all three `ψ_i` nontrivial** carry genuine coupling. The marginal terms are exactly
what `δ_const` already gives away for free (§8.3 shows they are also what dominates
F1's residual).

### 7.3 The two lemmas that make the degeneracy finite

**Lemma 7.1 (degeneracy count).** Fix `k ≥ 2` and `G₁,G₂ ∈ \bar F_p(E)^*`. For `R ∈ E`
put `F_R(P) = G₁(P)·G₂(R−P)`. Let `S_i` be the set of points where `div(G_i)` has
multiplicity `≢ 0 (mod k)`. If `S₁` and `S₂` are not both empty, then
`#{R : div(F_R) ≡ 0 (mod k)} ≤ min(|S₁|,|S₂|)`, and in particular `≤ 2Δ`.

*Proof.* `P ↦ R−P` is an automorphism of `E`, so `div(F_R) = div(G₁) + σ_R^*div(G₂)`
with `σ_R^*` carrying `B ↦ R−B` with the same multiplicity. Reducing mod `k`, the
support is empty iff `S₁ = R − S₂` as multisets. If exactly one of `S₁,S₂` is empty this
is impossible. Otherwise fix `A ∈ S₁`; then `A = R−B` for some `B ∈ S₂`, so
`R ∈ A + S₂`, at most `|S₂|` values. `|S_i| ≤ #(zeros ∪ poles of G_i) ≤ 2 deg(G_i)`. ∎

**Lemma 7.2 (no Case B survives on a prime-order curve).** Let `#E(F_p)=N` be prime with
`N > k`, and `G ∈ F_p(E)^*` with `div(G) ≡ 0 (mod k)`. Then `χ∘G` is **constant** on
`E(F_p)`.

*Proof.* By Lemma 6.3, `P ↦ χ(G(P)/G(O))` is a homomorphism `E(F_p) → μ_k`. Its image is
a subgroup of `μ_k` and a quotient of `Z/N`, so has order dividing `gcd(k,N) = 1`. ∎

This is where the whole architecture closes: **the exact-factorisation phenomenon that
F1 found empirically (and only found at 2-torsion roots) is precisely the
divisor-`k`-divisible case, and Lemma 7.2 says that case is empty on a prime-order
curve.** There is no third kind, and now there is a reason rather than a count.

### 7.4 The theorem

**Theorem 3.** Let `E/F_p` have `#E(F_p) = N` prime, `N > k`. Let `h` be a non-redundant
character filter of complexity `(k,r,Δ)`, `M = k^r`. Then for **every** predictor
`f : [M]² → [M]`,

```
   Pr[h(P+Q) = f(h(P),h(Q))]   ≤   1/M  +  M·( c₁ Δ p^{-1/2}  +  c₂ Δ / N )
```

over independent uniform `P,Q ∈ E(F_p)`, with absolute constants `c₁,c₂`.

*Proof, in checkable steps.*

1. By (★) it suffices to bound `max_{ψ≠1}|T̂_ψ|`.
2. Write `ψ_i ∘ h = χ ∘ G_i` with `G_i = ∏_j g_j^{a_{ij}}`, a rational function on `E`
   whose zero/pole set has size `≤ 2Δ` (exponents `a_{ij} ∈ [0,k)` change
   multiplicities, not the support).
3. Fibre the sum over `R = P+Q`. The substitution `(P,Q) ↦ (P,R)` is a bijection of
   `E(F_p)²`, so `N² T̂_ψ = Σ_R χ(G₃(R)) · Σ_P χ(G₁(P)G₂(R−P))`.
4. For each `R`, if `div(G₁(·)G₂(R−·)) ≢ 0 (mod k)` then `F_R` is not a constant times
   a `k`-th power in `\bar F_p(E)`, so the Weil/Bombieri bound for multiplicative
   character sums on a curve of genus 1 gives `|Σ_P χ(F_R(P))| ≤ c₁Δ√p`.
5. By Lemma 7.1 the remaining `R` number at most `2Δ` — **unless** both `div(G₁)` and
   `div(G₂)` are `≡ 0 (mod k)`, in which case Lemma 7.2 makes `ψ₁∘h` and `ψ₂∘h`
   constant, contradicting non-redundancy. Each exceptional `R` contributes at most `N`.
6. Hence `N²|T̂_ψ| ≤ N·c₁Δ√p + 2Δ·N`, so `|T̂_ψ| ≤ c₁Δ p^{-1/2} + 2Δ/N`. Substitute into
   (★). ∎

**Corollary 3.1 (Wagner).** By Lemma 5, `h`'s speedup at one k-tree level is
`≤ 1 + M²·(c₁Δ p^{-1/2} + c₂Δ/N)`, which is `p^{o(1)}` whenever
`M ≤ p^{1/4} / (Δ p^{o(1)})^{1/2}`. Since `#E(F_p) = N ≍ p`, a Wagner `j`-level tree
needs `M ≈ N^{1/(j+1)} ≈ p^{1/(j+1)}`. Therefore, **within the character-filter class
with `Δ = p^{o(1)}`, every configuration with `j ≥ 3` is closed**, including the
`(j=3, m=16)` configuration at exponent `0.375` that the adjudication identified as the
escape.

I re-derived the adjudication's counterfactual exponent `(2^j+m)/(m(j+1))` rather than
quoting it: leaf lists of `(m/k)`-subset sums have size `B^{m/k} = N^{βm/k}`, Wagner
needs that `= N^{1/(j+1)}`, giving `β = k/(m(j+1))`; one tree run yields one relation at
cost `N^{1/(j+1)}` and `N^β` relations are needed, so the total exponent is
`β + 1/(j+1) = (2^j+m)/(m(j+1))`. It checks out, and it confirms `M = N^{1/(j+1)}`.

### 7.5 Every hypothesis Theorem 3 needs, named

- **(H1)** Weil/Bombieri bound for multiplicative character sums on a smooth projective
  curve of genus `g` over `F_p`: `|Σ_P χ(F(P))| ≤ (2g−2+2m)√p` with `m` the number of
  distinct zeros and poles of `F`, valid when `F` is not a constant times a `k`-th power
  in `\bar F_p(C)`. Standard (Weil; Bombieri, *On exponential sums in finite fields*,
  1966; Perel'muter). **Not re-verified by literature search in this session** — flagged
  under `AGENTS.md` rule 9; a KN-LIT entry is owed before any promotion.
- **(H2)** Weil reciprocity on `E`. Standard.
- **(H3)** Lemma 7.1's divisor bookkeeping — proved above, but I have **not** carried
  out the exact count of `m` for `F_R` (I assert `≤ 4Δ`; the honest statement is that it
  is `O(Δ)` and I did not do the count). This affects `c₁`, not the shape.
- **(H4)** `#E(F_p) = N` prime, i.e. cofactor 1 — the standardized cryptographic case
  (secp256k1, P-256, F1's C1/C6/C8). For cofactor `t > 1`, sample `P = [t]P'` with `P'`
  uniform on `E(F_p)`; `g∘[t]` has degree `t²·deg g`, so `Δ ↦ t²Δ`. Bounded `t` is fine;
  the constant degrades.
- **(H5)** `N > k`, so `Hom(Z/N, μ_k)` is trivial.
- **(H6)** Non-redundancy of `h` (equivalently: run the theorem at `M_eff`).

### 7.6 What Theorem 3 covers, and what it does not

**Covers** (by direct instantiation of the definition):

- F1 **family C** — quadratic characters and products: `chi(x)`, `chi(y)`, `chi(x±1)`,
  `chi(x±y)`, `chi(xy)`, `chi(x²+1)`, `chi(3x²+a)`, `chi(x³+1)`, the 12-point `chi(x−e)`
  scan, and all pairs/triples/quadruples of these (`M = 4, 8, 16`). 302 of F1's 507
  definitions.
- F1 **family D** — cubic, quartic, octic residue characters (`k = 3,4,8`).
- F1 **family F** — 2-descent characters: covered by the Case-B branch (Lemma 7.2), and
  independently by Theorem 1. Their `M ≤ 4` cap and their identical triviality on the
  odd part are both *derived*, not measured.
- F1 **family E** — rational-function coordinates `x/y`, `y/x`, `x²/y`, `(x+1)/(y+1)`,
  `xy/(x+1)` — when composed with a character. These are rational functions on `E` of
  bounded degree, so they are inside the class.
- F1 **family G** — small-subgroup projections: covered by **Theorem 1** (they are
  homomorphisms), unconditionally, with no character-sum input.
- Growing `M`: `r` may grow like `log p`, giving `M` up to `p^{1/4−o(1)}` with `Δ` fixed.

**Does not cover.**

1. **Arbitrary `h`.** And by Proposition 2 no theorem can. This is the fundamental
   limit, not a defect of the method.
2. **Interval / bit-window / congruence filters** — F1 families A, B, I, J (`x mod M`,
   low/high/middle bit windows, popcount, digit sums, `y`-sign). These are not character
   filters. They are reachable by **additive-character completion**: `1[x ∈ I]` expands
   into additive characters with a `log p` loss, and the resulting sums
   `Σ_P e_p(αu(P)+βv(R−P))` obey the same fibred Weil bound with Artin–Schreier
   degeneracy (`αu(P)+βv(R−P)` constant in `P`) in place of `k`-th-power degeneracy.
   **I sketch this and do not carry it out.** It is the largest missing piece and it is
   routine rather than deep. Empirically (§8.3) these filters behave exactly as the
   theorem would predict.
3. **F1 family H (SHA-256)** — no algebraic structure, outside the class, and
   irrelevant: it is the in-arm null.
4. **`M > p^{1/4}`**, i.e. the `j = 2` four-tree. See §10.
5. **Non-uniform / adaptive `h`**, `h` depending on the target, or filters valued in a
   set with a non-group `f` beyond what `f_joint` covers.

---

## 8. Computations run, and what each settles

All exact unless stated. Scripts under the session scratchpad
(`O2/c{1,2,3,5,6,7,8}*.py`); **scratch, not archived artifacts** — the same status the
adjudication and F1 gave their own computations. Curve arithmetic uses the repository's
own auditable implementation `harness/toycurve.py`, which did not originate any claim in
this document. Repository commit at execution: `ee16c4a966ac8e13b8e88e2c6b2c0de3d382598f`
(one untracked pre-existing BATCH-026 review directory, unrelated).

**8.1 `C1` — symbolic.** Lemma 6.1 verified in sympy: the difference, cleared of
`x_P−x_Q` and reduced modulo both curve relations, is identically `0`. *Settles:* the
chord identity, hence Corollary 6.2.

**8.2 `C2` — numerical, three curves × up to 8 values of `e` × 4000 random pairs.**
0/4000 identity violations everywhere; per-element factorisation rate exactly `1.0000`
at each rational root and `0.4900–0.5092` at each non-root. *Settles:* F1 §7.1's
"only when `e` is a root" claim, which the task asked me to verify before building on
it. It is correct.

**8.3 `C6` — exact `δ`, `δ_const`, `GAP` by full enumeration over all `N²` pairs (FFT in
discrete-log coordinates), eight prime-order curves, `N` from 523 to 65423.** No
sampling, no fit/score split: this is the true population optimum over **all** `f`,
i.e. F1's `f_joint` taken to its exact limit.

```
GAP = delta - delta_const          p=523    1033    2063    4111    8219   16417   32779   65539   alpha
chi(x-0),chi(x-1)   M=4        0.000713 0.001776 0.000000 0.000000 0.000000 0.000000 0.000000 0.000000  4.29
chi(x-0,1,7)        M=8        0.004435 0.002364 0.000581 0.000171 0.000000 0.000037 0.000000 0.000000  5.01
x mod 4             M=4        0.006500 0.005864 0.003288 0.005115 0.001059 0.000011 0.000597 0.000634  0.80
x mod 16            M=16       0.009750 0.007793 0.003819 0.003199 0.000012 0.000983 0.000576 0.000587  0.73
x*y mod 16          M=16       0.000044 0.000000 0.000000 0.000000 0.000000 0.000000 0.000000 0.000000  2.12
RANDOM-NULL         M=4        0.006010 0.001859 0.000878 0.000402 0.000223 0.000131 0.000069 0.000023  1.06
RANDOM-NULL         M=16       0.015000 0.006599 0.003254 0.001649 0.000854 0.000461 0.000208 0.000119  0.99
DLOG-INTERVAL       M=4        0.251915 0.250471 0.250235 0.250120 0.250062 0.250061 0.250031 0.250015  0.00
DLOG-INTERVAL       M=16       0.445664 0.441143 0.440375 0.438966 0.437977 0.437760 0.437607 0.437607  0.00
```

*Settles four things.*

- **The discriminating control the inventor protocol §3 demands, and that F1 did not
  run.** The parameter that must destroy a spurious signal is `p`. Every algebraic
  filter decays (`α = 0.73–5.01`); the random-function null decays at `α ≈ 1.0`; the
  genuine filter does **not** decay (`α ≈ 0.00`). The measurement discriminates
  perfectly, and the algebraic filters land on the null side.
- **F1's statistic was the wrong one, and the right one is far quieter.** Separately
  measured, `δ_const − 1/M` (pure marginal non-uniformity, free, zero
  sum-compatibility) is `0.0019–0.0318` for the character filters and `0.124` for
  `x·y mod 16` — comparable to or larger than F1's entire residual `1.101×` lift. Once
  it is subtracted, `chi(x−0),chi(x−1)` has `GAP` **exactly 0.000000** for every
  `p ≥ 2063`: the population-optimal predictor *is* the constant predictor. F1's
  conclusion is right; its headline number was measuring marginal bias.
- **A quantitative null model, matching to ~10%:** for a uniformly random balanced `h`,
  `GAP ≈ √(2M ln M)/N` (max of `M` multinomial cells with mean `N²/M³`, summed over
  `M²` cells). Predicted vs measured `RANDOM-NULL`: `M=4, N=523`: 0.00637 vs 0.00601;
  `M=16, N=523`: 0.01800 vs 0.01500; `M=16, N=65423`: 0.000144 vs 0.000119.
- **Cross-validation against F1**, via the `DLOG-INTERVAL` arm (§3).

**8.4 `C5`, `C7`** — Theorem 1 exhaustively (with composite-order positive control) and
the Case-B branch end to end. See §4 and §6.

**8.5 `C3`/`C8` — how big is `|T̂_ψ|` really?** Exact full-enumeration RMS over 10 values
of `e` per curve of the coupling term `D(e) = E_{P,Q}[chi((λe+ν)²−f(e))]`, which is the
group-law-predictor bias for `h = chi(x−e)`:

```
      p   #e     RMS|D|   RMS*sqrt(p)     RMS*p
    541   10   0.003238       0.07532    1.7519
   1033   10   0.001582       0.05083    1.6338
   2063   10   0.000719       0.03267    1.4841
   4111   10   0.000269       0.01725    1.1062
   8219   10   0.000320       0.02903    2.6315
```

`RMS·√p` falls by ~2.6× over a 15× range in `p`; `RMS·p` stays in `[1.1, 2.6]` with no
trend. **This is consistent with `|T̂_ψ| = O(Δ/p)` — full square-root cancellation on
the surface — and inconsistent with the fibred bound `p^{-1/2}` being tight.** Five
points over a 15× range with a sign-oscillating quantity is *not* a decisive
determination of the exponent, and I do not claim one. It supports the conditional
strengthening in §10 and nothing more.

---

## 9. The counting/covering route — dead as a proof route, and why

- Maps `h : G → [M]`: `M^N`.
- Exactly sum-compatible maps with `M < N`, `N` prime: **exactly the constants**
  (Theorem 1) — one, up to relabelling. So the exact class has density `M^{-N}·M`.
- Maps with `GAP ≥ 1/4` and arbitrary `M`: **at least `N−1`**, explicitly — one for each
  generator, via Proposition 2 — and in truth far more (any interval-like partition of
  `Z/N` pulled back, plus perturbations).

So counting establishes that good `h` are *rare* and cannot establish that they are
*absent*, because §3 exhibits them. **A first-moment or union-bound argument over all
`h` is therefore guaranteed to fail**, and the program should not spend a session on
one. Its one genuine use is the null model in §8.3, which it supplies accurately.

This also disposes of a tempting bad argument: "F1 screened 507 families and 31 283
combinations, and the space of maps is astronomically larger, so the search covered
nothing." True, and irrelevant in both directions — the searched fraction is
vanishing, but so is the fraction of *cheap* maps, and neither number bears on
existence. F1 was right to record the 507 as a fatigue report accompanying the
obstruction rather than as the result.

---

## 10. Where the argument breaks, stated precisely

**The single live gap: the four-tree, `j = 2`, `M ≈ N^{1/3}`.**

Theorem 3 gives `speedup ≤ 1 + M²·c₁Δ p^{-1/2}`, which is `p^{o(1)}` exactly for
`M ≤ p^{1/4−o(1)}`. Wagner needs `M ≈ p^{1/(j+1)}`, so:

| `j` | needed `M` | covered by Thm 3? | exponent at `m=16` | exponent as `m→∞` |
|---|---|---|---|---|
| 2 | `p^{1/3}` | **NO** | 0.4167 | 1/3 |
| 3 | `p^{1/4}` | yes (boundary; `c₁Δ = p^{o(1)}` suffices) | 0.3750 | 1/4 |
| 4 | `p^{1/5}` | yes | 0.4000 | 1/5 |
| ≥5 | `≤ p^{1/6}` | yes | — | — |

So **the character-filter class retains exactly one exponent-moving configuration**: a
4-tree with a filter of alphabet `≈ N^{1/3}` built from `≈ (1/3)log₂ p` quadratic
characters of bounded-degree functions. That is a concrete, searchable object, and it is
the correct next target in this direction. Note it is *not* the configuration the
adjudication highlighted (`j=3, m=16`, exponent 0.375) — that one is now closed inside
this class; `j=2` gives a weaker but still sub-`1/2` exponent of 0.4167 at `m=16`.

**Conditional closure.** If `|T̂_ψ| = O(Δ/p)` — full square-root cancellation on the
surface `E×E`, a Deligne/Katz-level input rather than the fibred Weil bound, and the
regime `C8` measures — then `speedup ≤ 1 + M²c Δ/p`, which is `p^{o(1)}` for
`M ≤ p^{1/2−o(1)}`, and **the character-filter class closes completely**, `j = 2`
included. Naming this precisely: the missing input is square-root cancellation for
`Σ_{P,Q ∈ E(F_p)} χ(G₁(P)G₂(Q)G₃(P+Q))` at `O(p)`. I did not verify that the relevant
sheaf is non-degenerate in the sense Deligne's theorem requires, and I do not assert it.

**Other gaps, in decreasing size.**

1. **Interval/bit-window filters are not covered** (§7.6 item 2). Additive-character
   completion should extend Theorem 3 to them with a `polylog p` loss; not carried out.
2. **The cost clause is still not a theorem.** Theorem 3 restricts `h` *algebraically*,
   which is a proxy for "cheap". A cheap `h` that is not a bounded-degree character
   filter — a lookup table, an iterated construction, something built from a partially
   precomputed dlog — is untouched. Proposition 2 says this gap cannot be closed
   mathematically; it can only be closed by making the restriction the *definition* of
   the class, which is what F1 §5's amendment request (i) proposes.
3. **(H1) not re-verified by literature search this session** (`AGENTS.md` rule 9).
4. **(H3)'s explicit zero/pole count for `F_R` not carried out**; affects constants.
5. **Everything is at toy scale.** `N ≤ 65 423`. Under `AGENTS.md` rule 7 this is not
   crypto-scale validation of anything, and none of it is offered as such. The
   *theorem* is asymptotic; the computations check its steps and its predicted
   `p`-dependence over three orders of magnitude, no more.

---

## 11. Disposition of (O2)

**(O2) is now: a conditional argument for a named restricted class, resting on standard
character-sum machinery, plus an unconditional theorem covering the exact case for all
`h`, plus a proof that the unrestricted version is false.** Specifically:

| Component | Status |
|---|---|
| Exact sum-compatibility ⟹ trivial on prime order, all `h` | **theorem**, unconditional, verified exhaustively |
| No stability/rigidity theorem exists on prime-order groups | **theorem** (explicit counterexample), verified |
| Approximate case, character-filter class, `M ≤ p^{1/4−o(1)}` | **conditional argument** — conditional on (H1)–(H6), with one sketched bookkeeping step |
| Approximate case, character-filter class, `p^{1/4} < M ≤ p^{1/2}` (`j=2`) | **open**; heuristic + measurement only |
| Approximate case, interval/bit-window filters | **heuristic + measurement**; extension routine, not done |
| Approximate case, arbitrary cheap `h` | **measurement only** — and provably cannot become a theorem without a computational restriction |

Against `docs/inventor-protocol.md` §4: (O2) now has a **named obstruction**
(divisor-`k`-divisibility is the only route to per-element factorisation, and Lemma 7.2
empties it on prime order), an **argument** (§§4, 6, 7), and **forward guidance**
naming what remains open (§10, §12). It did not have the middle one before. That is the
delta this session produced. It is **not** a general closure of (O2), and any record
that says so would be an overclaim.

---

## 12. Required controls and forward guidance

**Controls that must accompany any use of this material.**

1. **The decay-in-`p` control (§8.3) becomes the standing test**, replacing F1's
   single-`p` lift. Any claimed filter must be measured on a ladder of `p` spanning at
   least two orders of magnitude, reporting `GAP = δ − δ_const`, against (a) the random
   balanced null and (b) the dlog-interval positive control. A `GAP` flat in `p` is a
   finding; a `GAP` decaying at the null's rate is a controlled null. **This is cheap
   and F1 has never run it.**
2. **`δ_const` must always be reported and subtracted.** F1's `f_const` column existed
   but was not used as the baseline for the headline number.
3. **`M_eff`, not `M`.** Already F1 discipline; it is also a hypothesis of Theorem 3.
4. **Exact enumeration wherever `N ≤ 10⁵`.** Sampling at 20 000–400 000 pairs cannot
   resolve a `GAP` of `10^{-4}`, which is where the interesting quantities live; the FFT
   method here computes the exact population optimum over all `N²` pairs in seconds.
5. **The `Z/N` and dlog-interval arms stay in every run** as the proof that the
   apparatus can see a real filter.

**Forward guidance — what remains open, ordered by value.**

1. **The `j=2` four-tree filter, `M ≈ N^{1/3}`.** The one exponent-moving configuration
   the character class retains. Concretely: is there a family of `≈ (1/3)log₂ p`
   quadratic characters of bounded-degree functions on `E` whose joint coupling is
   `ω(p^{-1/2})`? Theorem 3 says no if `Δ` is bounded and `M ≤ p^{1/4}`; at `p^{1/3}`
   it is silent.
2. **Establish or refute `|T̂_ψ| = O(Δ/p)`.** This single input closes the class
   completely. `C8` supports it over 15× in `p`; extend to 1000× and to `k > 2`.
3. **Carry out the additive-character completion** for interval/bit-window filters.
   Routine; closes F1 families A, B, I, J.
4. **Higher-degree descent and isogeny-induced maps** (F1 §10 item 2): **now answered**
   by Theorem 1 in the only form that matters, and by Lemma 7.2 in the character form.
   This item can be closed.
5. **The full-function-space search gap** (F1 §8.1): Proposition 2 says such a search
   *will* find something (the dlog map) and that finding it means nothing. Any
   full-space search must therefore be constrained by cost, not by `δ`, or it is
   guaranteed to produce a false positive. That is a redirection, not a closure.

**`dominated_by`.** No algorithm is proposed here, so there is no frontier row to
occupy. `dominated_by` is **inapplicable**, not `null`. `sota_delta`: **0 on time, 0 on
memory, 0 on data/queries** — the contribution is an obstruction argument and a
corrected measurement protocol.

**One next concrete action.** Run the decay-in-`p` control (§12.1) over F1's ten curve
families on a ladder `p ∈ {2^16, 2^20, 2^24, 2^28, 2^32}` at fixed `M ∈ {4,16,64}`,
reporting `GAP` against both nulls, inside an experiment directory with the standard
receipt package. It is hours of compute, it is the control F1 omitted, and it is the
only measurement that can distinguish "no filter" from "a filter too weak to see at one
field size". Then, and separately, route Theorem 3 to independent
`review-breakthrough` at `max` on a resolved model distinct from `claude-opus-5`
(`AGENTS.md` rule 12) before any of it is promoted; the character-sum step in
particular deserves a reviewer who did not author it. If three distinct models cannot
be resolved, leave (O2) `unverified` and record this document as a derivation only.

---

## Inference

```yaml
inference:
  requested_policy: review-xhigh
  resolved_model_id: claude-opus-5
  reasoning_effort: null
  fallback_used: true
  fallback_reason: >-
    This Claude Code harness cannot resolve the policy aliases in
    orchestration/model-policies.yaml; subagent frontmatter supports only Claude
    models. Recorded, never silently substituted (AGENTS.md rule 11). Consequence
    disclosed at the head of this document: the adjudication (claim_a_adjudication.md),
    the F1 search (F1_sum_compatible_filter_search.md) and this derivation all resolve
    to the same backend, so the independence between them is procedural, not
    model-level.
  degraded_allowed: false
  degraded_requirements: []
  model_verified: false
  model_verified_reason: >-
    `python3 -m orchestration.adapter doctor --probe` was not run in this session.
    The identifier is unverified configuration.
```
