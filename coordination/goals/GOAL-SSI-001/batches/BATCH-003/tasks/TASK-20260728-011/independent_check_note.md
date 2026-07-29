# Independent check of the BATCH-002 review debt: D1, Lemma 4'(b), RC4, RC5

Task `TASK-20260728-011` · Goal `GOAL-SSI-001` · Batch `BATCH-003` · Role: red-team

**Independent session.** I authored no part of `TASK-20260728-005` (the v1
derivation), `TASK-20260728-007` (the review), or `TASK-20260728-009` (the
erratum). I read all three for the first time in this task. Every verdict below
rests on algebra performed in this session and displayed where a reader can
check it, not on preferring one prior session's statement to another's.

**Epistemic label: `derivation` + `literature`.** Claim tier `theory`.
**Zero curve computation.** No isogeny evaluated, no `j`-invariant computed, no
graph sampled, no experiment run, no timing measured.

**This is not a cryptanalytic result.** Nothing here breaks anything, moves an
exponent, or establishes bit security for any parameter set.

---

## 0. Verdict summary

| Item | Verdict | One-line reason |
|---|---|---|
| **D1** (`C = ω(M)` vs the review's `C = Θ(M)`) | **CONFIRMED** for the erratum, with two riders | `C/M = Θ(p^{ε}) → ∞` at the restated sizing, under every reading of `M` I tried |
| **D1 downstream weight** | **NIL** | Nothing consumes `C`; Lemma 5' consumes `k`, which comes from 4'(b). The disagreement is bookkeeping. |
| **Lemma 4'(b)** (usable fraction `1/2 − o(1)`) | **CONFIRMED IN CONCLUSION, PROOF REFUTED AS WRITTEN** | The stated side-bit independence claim is false; the conclusion survives via a different, correct argument I supply in §2.3 |
| **New objection O1** | H1' as *numbered* is too weak for three downstream steps | TV smallness does not control a pairwise collision probability; concrete counterexample in §1.3 |
| **New objection O2** | The erratum's §3.2 descent needs `ε > 1/2`, not `ε > 0` | Derived in §4; **no exponent moves**, so this sharpens rather than breaks |
| **RC4** | **PARTIALLY CLOSED**, and it goes **against** the erratum | Primary text says *one long walk*, not restarts (§5). Quantitative `p^{1/4}` still **not** obtained; two fetches returned **two different abstracts**. |
| **RC5** | **FAILED — REMAINS OPEN** | Four attempts, all recorded (§6). `closed_within_SSI_FC_2026` is confirmed narrow-and-correct and must not be widened. |
| **KN-TECH-056** | **ADMIT** (recommendation to gate R2) | Id free; every figure has a locator I read myself (§7) |

---

## 1. D1 — is `C = ω(M)` or `C = Θ(M)` at the restated sizing?

### 1.1 The two claims

`RT-20260728-007` F2 `note_on_lemma_4_robustness` states that Lemma 4's
conclusion `C = Θ(M)` *"holds both in the near-bijective regime the note
actually sits in and in the repaired regime."*

`TASK-20260728-009` §2.4 and §5 item 1 assert that the second half of that is
wrong: at the repaired sizing `C = Θ(p^{1+2ε})` while `M = Θ(p^{1+ε})`, hence
`C = ω(M)`.

Nobody had checked either. Here is my own derivation.

### 1.2 Setting and derivation

Restated sizing (erratum §2.2): walk length `d = (1+ε)·log_ℓ p` for a fixed
`ε > 0`; per-side index space `I` with `|I| = Θ(ℓ^d) = Θ(p^{1+ε})`;
`D = {1,2} × I`, so `M := |D| = 2|I| = Θ(p^{1+ε})`; vertex set `V` of
supersingular `j`-invariants over `F_{p^2}`, `n_V = Θ(p)`.

Write `μ_1, μ_2` for the endpoint laws on `V` of the length-`d` non-backtracking
walk from `E_1` and from `E_2`, and `e_i := μ_i − U` where `U` is uniform on `V`.
Then `Σ_v e_i(v) = 0`.

A **cross-side claw** is a pair `(y, y') ∈ (\{1\}×I) × (\{2\}×I)` with
`g(y) = g(y')`. There are `|I|²` such pairs, and by linearity of expectation

```
E[C] = |I|² · Pr[ g(y) = g(y') ]  =  |I|² · Σ_v μ_1(v) μ_2(v)
     = |I|² · ( 1/n_V + <e_1, e_2> ).
```

By Cauchy–Schwarz `|<e_1,e_2>| ≤ ||e_1||_2 · ||e_2||_2`. The rigorous ingredient
the erratum itself displays in §2.1(i) — the Ramanujan `L²` bound for the
length-`d` non-backtracking walk — gives `||e_i||_2 ≤ poly(d)·ℓ^{-d/2}`, hence

```
|<e_1,e_2>|  ≤  poly(d)² · ℓ^{-d}  =  poly(log p) · Θ( p^{-(1+ε)} )  =  o( 1/n_V ),
```

because `n_V = Θ(p)` and `poly(log p) ≪ p^{ε}`. Therefore

```
E[C] = (1 ± o(1)) · |I|² / n_V = Θ( p^{2+2ε} / p ) = Θ( p^{1+2ε} ),
```

and against `M = Θ(p^{1+ε})`,

```
C / M = Θ( p^{1+2ε} / p^{1+ε} ) = Θ( p^{ε} ) → ∞.        ∎
```

**`C = ω(M)`. The erratum is right and the review's `note_on_lemma_4_robustness`
is wrong on its "repaired regime" half.** The review's *near-bijective* half is
correct: at v1's sizing `|I| = Θ(n_V)`, the same formula gives
`C = Θ(n_V²/n_V) = Θ(n_V) = Θ(M/2) = Θ(M)`. So the review's error is precisely
the one the erratum names, no more and no less.

I checked the alternative reading of `M`, since the review's F2 also proposes
replacing the birthday parameter by `M' := |im f| = Θ(n_V) = Θ(p)`. Under that
reading `C/M' = Θ(p^{2ε}) → ∞` as well. **`C = Θ(M)` is not recoverable under
either reading of `M`.**

### 1.3 Rider 1 — the erratum's stated justification does not license its own constant (objection O1)

The erratum derives `Pr[g(y)=g(y')] = (1+o(1))/n_V` *"under H1'"*, and H1' as
numbered in §2.2 is a **total-variation** statement: `TV(μ_i, U) ≤ p^{-Ω(1)}`.
**TV smallness does not control a pairwise collision probability.** Concrete
counterexample, pen and paper: let `μ_1 = μ_2 = μ` place mass `1/n_V + δ` on one
distinguished vertex `v_0` and redistribute the deficit uniformly. Then
`TV(μ, U) ≈ δ`, which satisfies H1' for `δ = p^{-1/4}` (that is `p^{-Ω(1)}`), yet

```
Σ_v μ(v)²  ≈  1/n_V + δ²  =  Θ(p^{-1}) + Θ(p^{-1/2})  =  Θ(p^{-1/2}),
```

a collision probability inflated by a factor `Θ(p^{1/2})` over `1/n_V`. So a
distribution satisfying H1' *as stated* can inflate `C` by a polynomial factor.

This does **not** overturn D1 — the true bound is the `L²` one I used above, and
that bound is already displayed inside the erratum's §2.1(i) as the *proof* of
H1'. But downstream lemmas cite **H1', not its proof**, and H1' as numbered is
strictly weaker than what §2.4 uses. That is a heuristic-inventory defect of
exactly the kind `agents/red-team.md` item 1 exists to catch.

**Required control RC8 (new, cheap, pen-and-paper):** restate H1' in `L²` /
collision (Rényi-2) form — `||μ_d − U||_2 ≤ poly(log p)·ℓ^{-d/2}`, from which
the TV form follows by Cauchy–Schwarz but not conversely. Three downstream steps
need the `L²` form and not the TV form: Lemma 4'(a) (§1.2 above), Lemma 4'(b)
cause 1 (§2.2 below), and the descent hitting probability (§4 below). Cost: one
paragraph. No compute.

### 1.4 Rider 2 — `C` is definitionally unstable, and nothing downstream consumes it

`C` is stable only once one fixes *what is counted*. Under the erratum's
pair-counting definition (the one the van Oorschot–Wiener bookkeeping consumes,
since golden-collision multiplicity is a count of pairs), `C = Θ(p^{1+2ε})` and
`C = ω(M)`. But under the natural alternative reading — the number of **distinct
vertices** hit from both sides — the answer is `Θ(n_V) = Θ(p)`, since with
`|I| = p^{1+ε}` draws each side covers all but a vanishing fraction of `V`; that
is `Θ(M/p^{ε}) = o(M)`. So the *direction* of the failure of `C = Θ(M)` flips
with the definition, while `C = Θ(M)` itself is wrong under both.

I record this because it bounds the importance of D1. **Neither Lemma 5' nor
Lemma 7' consumes `C`.** What Lemma 5' consumes is `k`, the number of detected
collisions that must be sifted, and `k = Θ(1/ρ)` where `ρ` is the usable
fraction of Lemma 4'(b). `C` appears in the artifact only as a qualitative
statement that claws are abundant, and that statement is true on every reading.

**Consequence for `note_on_lemma_4_robustness`:** it should be recorded as
**withdrawn**, not merely narrowed. The erratum's decision to retire `C = Θ(M)`
rather than carry it is correct. But the erratum's framing — "this is the one
substantive point on which I differ from the review" — overstates the stake.
It is a bookkeeping correction with no downstream consequence, and the genuinely
load-bearing item is 4'(b), which no session had checked at all.

---

## 2. Lemma 4'(b) — is a `Θ(1)` fraction of detected `f`-collisions usable?

This is the load-bearing item. The memory-independence conclusion — the
artifact's genuine content — is exactly the statement `k = Θ(1)`, and `k = Θ(1)`
is exactly Lemma 4'(b).

### 2.1 The claim and the construction it lives in

`f = h ∘ g : D → D` with `h(v) = (b(v), i(v))`, `b` a one-bit PRF output and `i`
a PRF output in `I`, both keyed on a canonical encoding of `j(v)` (erratum §2.3).
A detected `f`-collision is a pair `y ≠ y'` of covered points with
`f(y) = f(y')`. It is a **usable cross-side claw** when `g(y) = g(y')` and `y`,
`y'` carry opposite side bits.

Note at the outset: **`b` is a design element this program specified in §2.3**,
not a property of any published algorithm. Confirming 4'(b) confirms internal
consistency of this repository's Algorithm 2. It corroborates nothing about
supersingular isogenies as such, and I say so again in §8.

### 2.2 Step one — the two disjoint causes. **Holds, modulo O1.**

For `y ≠ y'` covered, `f(y) = f(y')` iff `h(g(y)) = h(g(y'))`, which splits
disjointly into

- **cause 1**, `g(y) = g(y')`: probability `(1 ± o(1))/n_V = Θ(p^{-1})`;
- **cause 2**, `g(y) ≠ g(y')` but `h` maps them to the same element of `D`:
  probability `1/|D| = 1/(2|I|) = Θ(p^{-1-ε})` under the PRF model for `h`.

Ratio `Θ(p^{-ε})`, so a `1 − O(p^{-ε})` fraction of detected `f`-collisions have
cause 1. **I confirm this step.** Cause 1's rate again needs the `L²` form of
H1', not the TV form (objection O1); with that substitution the step is sound.

I add a robustness check the erratum does not make, because the step looks
fragile in `ε`: at `ε = 0` the two causes have *comparable* rates
(`≈ 12/p` against `≈ 1/(2p)` with `n_V ≈ p/12`), so the genuine fraction falls to
a constant strictly below 1 but is **still `Θ(1)`**. The `Θ(1)` conclusion is
therefore not an artifact of taking `ε` bounded away from 0. Good.

### 2.3 Step two — side-bit independence. **The argument as written is FALSE. The conclusion survives via a different argument.**

The erratum writes: *"Among genuine claws the two sides are opposite with
probability `1/2 − o(1)`, because each covered point's side bit is `b(·)`
evaluated at its predecessor's endpoint and is therefore independent of the
endpoint that collides."*

**That independence claim is false.** Let `u := g(pred(y))` and
`u' := g(pred(y'))`. Then `y = h(u) = (b(u), i(u))`, so `side(y) = b(u)` — and
`g(y)` is *the endpoint of walk `i(u)` starting from `E_{b(u)}`*. The colliding
endpoint `g(y)` is therefore a **function of `b(u)`**: change the side bit and
you are walking from a different base curve entirely. `side(y)` and `g(y)` are
dependent, not independent. The one-line justification does not survive.

**The conclusion does survive, by conditioning rather than by independence.**
Condition on `(b(u), b(u')) = (β, β') ∈ {1,2}²`. Given that, `g(y)` is the
length-`d` walk endpoint from `E_β` at index `i(u)`, and `g(y')` likewise from
`E_{β'}` at index `i(u')`; under the PRF model for `h` the indices `i(u), i(u')`
are independent and near-uniform on `I`, and `u ≠ u'` (if `u = u'` then
`y = h(u) = h(u') = y'`, excluded). Hence, by the `L²` computation of §1.2
applied to the pair `(μ_β, μ_{β'})`,

```
Pr[ g(y) = g(y') | b(u) = β, b(u') = β' ]  =  (1 ± o(1)) / n_V     for all four (β, β').
```

The conditional collision probability is thus the **same to relative `o(1)` for
all four side configurations**. Bayes then gives

```
Pr[ β ≠ β' | g(y) = g(y') ]  =  Pr[ β ≠ β' ] · (1 ± o(1))  =  1/2 − o(1).
```

Combining with §2.2,

```
ρ := Pr[ a detected f-collision is a usable cross-side claw ]  =  1/2 − o(1)  =  Θ(1).  ∎
```

**Verdict: CONFIRMED IN CONCLUSION, PROOF REFUTED AS WRITTEN.** The number
`1/2 − o(1)` is right. The reason given for it is not, and the correct reason is
a *uniformity-across-conditionings* argument, not an independence argument. The
difference matters for falsification: what would break 4'(b) is not a
correlation between a side bit and its own endpoint — that correlation is
present and harmless — but a **side-dependent bias in the collision rate**, i.e.
`Pr[collision | 1,2]` differing from `Pr[collision | 1,1]` by more than a
`1 + o(1)` factor. That is a different experiment from the one the erratum's
falsification condition names, and it is the one that should be pre-registered.

Two smaller gaps I close rather than treat as objections:

- **Trail heads.** Points that begin a trail have no predecessor, so their side
  bit comes from the start distribution rather than from `b`. They are a `1/L`
  fraction of covered points and the argument applies to them under a uniform
  start. No effect.
- **Degenerate pairs.** `β = β'` and `i(u) = i(u')` gives `y = y'`, excluded by
  hypothesis. Same-side genuine claws (`β = β'`, distinct indices) are the other
  half; they certify a non-scalar endomorphism-like cycle at `E_β`, not a path
  `E_1 → E_2`, and are correctly discarded. The loss is exactly the factor 2.

### 2.4 What breaks if 4'(b) fails (gate D2 requires this explicitly)

Let `ρ` be the true usable fraction, so `k = Θ(1/ρ)` detected collisions must be
sifted. Feed that into Lemma 5', `T(k) = √(2 M' k)` for `k ≤ w/2` and
`T(k) = 2k√(M'/w)` for `k ≥ w/2`, with `M' = Θ(p)`:

- **`ρ = Θ(1)` (the claim):** `k = Θ(1)`, so for **every** `w ≥ 2` we are in the
  first branch and `T = Θ(√M') = Θ(p^{1/2})`, `w`-free. Memory-independence
  **holds**.
- **`ρ = 1/polylog(p)`:** `k = polylog`. For every `w ≥ 2k = polylog`, still the
  first branch, `T = Θ(√(M'k)) = p^{1/2+o(1)}`. Memory-independence **degrades**
  to "independent of `w` for `w` above a polylog floor"; the exponent is
  unchanged. Survives in substance.
- **`ρ = p^{-δ}` for some `δ > 0`:** `k = p^{δ}`. At polylog `w` we are in the
  second branch and `T = Θ(p^{1/2+δ} / √w)` — **explicitly `w`-dependent**, and
  worse than `p^{1/2}` at polylog memory. Memory-independence **falls**, and one
  needs `w ≳ p^{2δ}` memory merely to recover `p^{1/2+o(1)}`.

So the load-bearing threshold is sharp and stateable: **memory-independence
requires `ρ ≥ 1/polylog(p)`, and fails exactly when `ρ` is polynomially small.**
My derivation puts `ρ = 1/2 − o(1)`, comfortably above the threshold with a
polynomial margin. This is the one place in the artifact where an error would
have cost an exponent, and it does not.

**Narrowest valid conclusion if 4'(b) were to fail anyway.** Only the *in-place
derivation* of a `p^{1/2+o(1)}` polynomial-memory algorithm would fall. The
existence of one survives **by citation**: `inputs/P13-WESOLOWSKI-2026/
paper_fulltext.md` line 39, read by me in this session, says *"the classic
p^{1/2+o(1)} algorithms with polynomial memory like [21]"*. A failure of 4'(b)
would be a failure of this repository's reconstruction, not of the baseline.

---

## 3. Cost bookkeeping check (red-team item 5)

I re-checked that the artifact multiplies per-attempt cost by inverse success
probability rather than quoting per-attempt cost alone.

- Lemma 5' does this correctly: `T(k) = √(2M'k)` is `√(2M')` per collision times
  the `√k` from the birthday accumulation, not a per-attempt figure.
- Lemma 7' composes `k = Θ(1)` (from 4'(b)) with Lemma 5'. Correct.
- Algorithm 3' §3.2 composes `p^{1/2+o(1)}` expected restarts with `Θ(log p)`
  steps each. Correct — this is the inverse-success-probability multiplication
  done explicitly.

I found **no** instance of per-attempt cost quoted as total expected cost.

---

## 4. Objection O2 — the descent needs `ε > 1/2`, not `ε > 0` (derived in place)

Erratum §3.2 argues each restart hits `V_p` with probability
`(1 + o(1))·S/n_V = p^{-1/2+o(1)}` *"under H1'"*, with `S = |V_p| = p^{1/2+o(1)}`.
Check the error term. With `e = μ_d − U`,

```
| μ_d(V_p) − S/n_V |  =  | Σ_{v ∈ V_p} e(v) |  ≤  √S · ||e||_2
                      ≤  √( p^{1/2} ) · poly(log p) · ℓ^{-d/2}
                      =  poly(log p) · p^{1/4} · p^{-(1+ε)/2}
                      =  poly(log p) · p^{-1/4 - ε/2}.
```

For this to be `o(S/n_V) = o(p^{-1/2})` one needs `1/4 + ε/2 > 1/2`, i.e.

```
ε > 1/2,     equivalently     d > (3/2)·log_ℓ p.
```

At `ε` just above 0 the error term **dominates** the quantity being estimated,
and the hitting probability is not controlled at all by the bound H1' rests on.
The same objection hits the TV route harder still: `TV ≤ poly·p^{-ε/2}` is
`≫ p^{-1/2}` for every `ε < 1`.

**Impact: none on any exponent.** `d = (3/2 + δ)·log_ℓ p` is still `Θ(log p)`
and is absorbed in the same `o(1)` as `(1+ε)·log_ℓ p`. The correction is to the
*quantifier*, exactly as the erratum's own `c > 1` correction was to v1. But it
is a real defect: the erratum fixed v1's unquantified `c` and then reintroduced
an insufficient quantifier one section later. **Required control RC9:** restate
the descent at `d ≥ (3/2 + δ)·log_ℓ p`, or state the hitting-probability
requirement as its own numbered heuristic separate from H1'.

---

## 5. RC4 — Delfs–Galbraith from the primary source

### 5.1 Every attempt, recorded

| # | Target | Outcome |
|---|---|---|
| 1 | `https://arxiv.org/abs/1310.7789` | **Returned.** Title, authors and an abstract, verbatim. |
| 2 | `https://arxiv.org/pdf/1310.7789` | **Failed.** PDF retrieved (325.2 KB) but the fetch tool could not extract text from the FlateDecode streams. |
| 3 | `https://ar5iv.org/abs/1310.7789` | **Redirect**, 301 to `ar5iv.labs.arxiv.org`. |
| 4 | `https://ar5iv.labs.arxiv.org/abs/1310.7789` | **Returned**, summary form. |
| 5 | `https://ar5iv.labs.arxiv.org/html/1310.7789` | **Returned**, with verbatim quotation of the passages requested. |

### 5.2 (b) — the descent: **CLOSED, and it contradicts the erratum's §3.2**

Quoted from the §4 passage returned by attempt 5:

> "Run random walks in the graph from E0 and E1 until we hit a supersingular
> curve defined over 𝔽p."

> "Since the graph is an expander, we expect the walks to quickly be sampling
> uniformly from the graph, and so we expect to select a vertex in the subset of
> j∈𝔽p with probability approximately p^(1/2)/p=1/p^(1/2)."

and, offered as an alternative rather than as the algorithm:

> "there should be a short path to the subset of j∈𝔽p of length (1/2)log(p) so
> one could distribute a depth-first search through all short paths from E0."

**Finding.** The published descent is **one long random walk** — *"until we
hit"* — not the erratum's restart form. The erratum's §3.2 restart repair is
therefore an **in-repo substitute, not what the authors do**, which is precisely
the disjunction RC4 was written to settle. The paper's own *alternative*
suggestion (a distributed depth-first search over all short paths) is closer in
spirit to the restart form, but it is hedged (*"there should be"*, *"one
could"*) and is not the stated algorithm.

**Consequence, and its limit.** This vindicates the erratum's decision to
relabel C-α `CITED` rather than `DERIVED`, and it strengthens rather than
weakens the erratum's memory objection: a single walk that must be composed is
exactly the object the erratum's Proposition 10 prices at `Θ(p^{1/2})` memory,
and **the returned text states no memory profile for the descent at all**. What
this does **not** license is any claim that Delfs–Galbraith is wrong. The stated
`Õ(p^{1/4})` is a *bit-operations* claim; whether the authors intend the descent
walk to be stored, recomputed, or handled some third way is **not settled by
what I retrieved**, and I do not settle it.

### 5.3 (a) — the inner `F_p` search memory: **PARTIALLY CLOSED**

The returned text calls Algorithm 1 of §3 a *"high-storage bi-directional-search
algorithm"* maintaining two sets `S_0`, `S_1` of visited vertices and testing
their intersection. So the inner search is **high-storage by the paper's own
wording** — it is a stored meet-in-the-middle, not a low-memory method.

**But the quantitative figure was not obtained.** Attempt 5 reports explicitly
that *"the paper contains no explicit statement about Algorithm 1's
memory/storage requirements"* beyond that phrase. The `O(p^{1/4})` storage
figure in attempt 4's reply was the fetch summariser's inference, not a
quotation, and I do **not** adopt it.

### 5.4 A sourcing red flag I did not expect: two different abstracts

Attempt 1 returned an abstract ending *"We give an algorithm to construct
isogenies between such supersingular elliptic curves that works faster than the
usual algorithm."* — **containing no `p^{1/4}` at all.** Attempt 4 quoted an
abstract containing *"works in O~(p^{1/4}) bit operations."*

These are not the same abstract. The most likely explanation is an arXiv version
difference between the 2013 preprint and the 2016 DCC version, but **I did not
verify that** and I will not assert it. What follows is what matters here:
`KN-LIT-078` records its `p^{1/2}` / `p^{1/4}` figures as *"relayed from the
abstract"*, and **the abstract is not a stable object across the identifiers
that entry lists.** That is a stronger sourcing defect than the one the erratum
recorded.

### 5.5 (c) — the `F_p`-rationality criterion: **UNRESOLVED, two fetches disagree**

Attempt 4 reported a Proposition 2.4 reading *"E is defined over 𝔽p ⟺
ℤ[√−p] ⊆ End E"*. Attempt 5 reported that *"the paper does not explicitly state
how F_p-rationality is tested in Algorithm 1"*. I record the disagreement rather
than picking a side. I also note that *"defined over `F_p`"* and *"`j ∈ F_p`"*
are **not the same condition**, and the erratum's §3.2 tests the latter; whether
that matches the published criterion is **unverified**.

### 5.6 RC4 disposition

**PARTIALLY CLOSED.** (b) closed with a finding contrary to the erratum;
(a) closed qualitatively, open quantitatively; (c) unresolved; the `p^{1/4}`
figure **not** obtained from primary text. **No `F_p` confidence label is
changed by this session.** `confidence: relayed_from_abstract` stands, and after
§5.4 it is if anything generous. RC4 stays **OPEN** on (a)-quantitative, (c),
and the headline figure. The `F_p` *ranking* is unaffected, as the card
anticipated: this was a precision control and it behaved like one.

---

## 6. RC5 — Wiener on BSGS: **FAILED, REMAINS OPEN**

| # | Target | Outcome |
|---|---|---|
| 1 | WebSearch, `Wiener full cost ... n^{2/3} optimum table size` | Returned candidate locations only. The engine's own summary restated `n^{2/3+o(1)}` — **a search summary is not the paper and I take no figure from it.** |
| 2 | `https://cr.yp.to/2005-590/wiener.pdf` | **Failed.** `Parse Error: Content-Length can't be present with Transfer-Encoding`. |
| 3 | `http://cr.yp.to/2005-590/wiener.pdf` (retry over http) | **Failed**, identical error. |
| 4 | `https://www.cs.haifa.ac.il/~orrd/BlockCipherSeminar/IlyaEfanov.pdf` | **Retrieved (956.5 KB) and DISCARDED.** I opened pages 1–2 directly: it is a student seminar slide deck, *"The Full Cost of Cryptanalytic Attacks / Michael J. Wiener / Presented by Ilya Efanov / 02.06.2013"*. **Third-party presentation, not the paper.** No figure taken from it. |
| 5 | `https://link.springer.com/content/pdf/10.1007/s00145-003-0213-5.pdf` | **Failed.** 303 redirect to `idp.springer.com/authorize` — paywall. |

**Nothing was obtained from Wiener's own text in this session.** The question
RC5 asks — whether `n^{2/3}` is framed as a textbook square-root balance or as
an optimum over the table size `m` — is **exactly as open as before**.

One in-repository observation that costs nothing and supports leaving it open:
`KN-LIT-094` carries `confidence: established` and `citation_verified: read`,
but its own *"Not verified here"* says the abstract and the introduction's
Shanks-versus-rho passage were read while *"the per-attack derivations in
Sections 3 onward were not re-derived"*. **The corpus does not itself claim to
have read the BSGS derivation.** So the attribution question was never closed
in-repo either.

**Verdict on the erratum's wording.** `closed_within_SSI_FC_2026; external
attribution pending RC5` is **confirmed as narrow-and-correct**. It should be
kept verbatim and must not be widened to `closed`. I add one point the erratum
does not make: the erratum's §1.5 recovers `n^{2/3}` *as the optimum over `m`*
under this repository's W2 convention, and `KN-LIT-094` reports `n^{2/3+o(1)}`
under Wiener's own wiring model. **Those are two different cost models reaching
the same exponent, so agreement of the numbers is not evidence that the framings
agree.** Coincidence of exponents across models is weak evidence of attribution,
and the erratum was right not to lean on it.

---

## 7. KN-TECH-056 — draft and recommendation

`tools/allocate_id.py --check KN-TECH-056` run in this session:

```
identifier: KN-TECH-056
  well-formed: YES -- no pattern is enforced for KN-* in validate_ledger.ID_PATTERNS; well-formedness NOT checked
  occurrences across the union (8175 files scanned): 0

OK: well-formed and free across the union.
```

**The id is free.** No collision; `TASK-20260728-014` need not amend its declared
paths on this ground.

I read `inputs/P13-WESOLOWSKI-2026/paper_fulltext.md` lines 1–45 **myself** in
this session and every quotation in the draft carries a line locator I verified
personally rather than relayed from the erratum. The draft is at
`KN-TECH-056-draft.md` in this directory and is written in final corpus format
for verbatim copying.

**Recommendation to gate R2: ADMIT.** Reasons: the id is free; `KN-TECH-029` is
superseded by a new entry and is not edited; every quoted figure has a
file-and-line locator I checked; the conditionality on Heuristic 1 and the
disclosed superpolynomial `o(1)` are carried inline in the front-matter and in
the body; the unconditional tier is stated as unchanged at `p^{1/2+o(1)}`; and
the entry claims no exponent it does not source. It is a **corpus-currency
supersession sourced to archived primary text**, not a `KN-FIND` promotion of an
internal finding, so the mandatory-promotion trigger is neither fired nor
blocked.

---

## 8. Limits, and what this session does not establish

- **Zero curve computation.** No empirical claim at any tier or scale arises.
- **Not a cryptanalytic result.** Nothing is broken; no exponent moves; no bit
  security is established for any parameter set.
- **Rigorous / model-internal / reading.** §1.2, §1.3, §2.2, §2.3 and §4 are
  algebra internal to the stated models (Ramanujan `L²` bound, PRF model for
  `h`) — *model-internal, conditional on those models*, not unconditional
  theorems. §5 and §6 are **readings of retrieved text**, and §5.2's contrast
  with the erratum is a reading of three quoted sentences, not a proof about
  the published algorithm.
- **A web fetch is not an archived artifact.** Everything in §5 and §6 was
  retrieved live in this session. Until `TASK-20260728-012` commits this note,
  none of it is durable, and no committed record should cite it as archived.
  The retrieved PDFs sit in a session scratch directory outside the repository
  and are **not** evidence.
- **4'(b) is about a construction, not about nature.** The side bit `b` is this
  repository's §2.3 design choice. Its `1/2` factor is the same factor the
  standard van Oorschot–Wiener meet-in-the-middle loses by the same device;
  nothing here is new, and nothing here beats a baseline.
- **Absence of evidence, not impossibility.** I found no further defect in
  §§2.1–2.7 within this bound. That is one bounded read by one session, not a
  clearance.
- **Session, not model, independence.** This session resolves to the same model
  as the producer, the reviewer and the erratum author. Four sessions, one
  model. No `GOAL-SSI-001` closure attestation may count them as distinct.
- **Not reached inside the 480-second cap:** the RC4 quantitative memory figure
  and the `F_p`-rationality criterion (§5.3, §5.5); the whole of RC5 (§6); an
  independent re-derivation of erratum §1 (RC1 / MITM) and §2.5 (Lemma 5'),
  which I read and did not re-derive; and any check of erratum §2.6, §4 or §7.

---

## 9. Provenance

Requested policy `review-adversarial`, `reasoning_effort: xhigh`,
`fallback_allowed: false`, `degraded_allowed: false`,
`independent_session_required: true`.
Resolved model `claude-opus-5` (runtime self-report).
`model_verified: false` — I ran no `python3 -m orchestration.adapter doctor
--probe` and no `adapter resolve`; per `AGENTS.md` the identifier is unverified
configuration.
`fallback_used: false` as far as this session can tell; no adapter resolution
record was produced, so this is a self-report, not a receipt.
`independent_session: true` — no shared lineage with `TASK-20260728-005`,
`-007`, `-009` or `-010`.
`model_independence: NOT ACHIEVED`, for the reason recorded verbatim in the
BATCH-003 queue's `model_independence_record`: the adapter resolves
`review-adversarial` to `claude-opus-5` on the anthropic backend and refuses
`glm-5.2` on zai because that binding's reasoning-effort ceiling is `high` while
the policy requires `xhigh` and the handoff permits no fallback; the zai backend
is in any case credential-less. I did not re-run the adapter and I claim no
probe of my own.

Tools used: file reads; `python3 tools/allocate_id.py --check KN-TECH-056`;
read-only `git log` / `git status`; five `WebFetch` calls and one `WebSearch`,
all itemised in §5.1 and §6. No commit. No official state changed. No ledger,
knowledge, evidence, decision or hypothesis record created or edited.
`knowledge/techniques/KN-TECH-029.md` was read and **not** modified. Nothing
written outside
`coordination/goals/GOAL-SSI-001/batches/BATCH-003/tasks/TASK-20260728-011/`.
