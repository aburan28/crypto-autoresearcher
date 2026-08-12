# Review notes — TASK-20260724-P13-REV (Reviewer_P13REV)

Independent review of Wesolowski, "The supersingular isogeny problem in time and
memory p^{1/3+o(1)}" (ePrint 2026/1486), frozen copy
`inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`.

**Inference**: requested_policy `review-xhigh`; resolved_model "kimi-work
subagent (exact model identifier not exposed by runtime)"; fallback_used: true;
fallback_reason: "GPT-5.6 policy aliases not resolvable in the Kimi Work
harness; recorded explicitly per AGENTS.md rule 11."

## 0. Provenance incident (read first)

The frozen file (350 lines per the initial `wc -l`) was read successfully for
lines 1–200. Mid-session it became unreadable: the directory
`inputs/P13-WESOLOWSKI-2026/` no longer exists, `git ls-files inputs/` contains
no such path, and no copy exists in the workspace (glob/grep/find checks).
Dispatch records (`coordination/current_dispatch_p13.json`) still reference it.

Consequences for this review:

- Lines 1–200 reviewed verbatim from the frozen text: abstract; intro; Thm 1.1
  statement; Cor 1.2; §1.1–1.5 incl. **Heuristic 1**, Def 1.3, **Thm 1.4
  (Canfield–Erdős–Pomerance)**, **Thm 1.5 ([4])**; §2 preliminaries; Def 3.1;
  **Lemma 3.2**; **Algorithm 1**; **Lemma 3.3**; **Algorithm 2**; **Lemma 3.4**;
  **Lemma 3.5**; **Remark 1**; start of the **Thm 1.1 proof** (choice of
  `B = e^{(1/3)√log(p/2)}`, the `n = O(log p)` mixing claim, start of
  Algorithm 3).
- Lines 201–350 (rest of Thm 1.1's cost computation, §4 experiments, §4.1
  estimates, bibliography) were **not available**. Nothing about those lines is
  asserted from memory (AGENTS.md rule 9). Tail-dependent items were handled by
  independent recomputation from parameters stated in lines 1–200 plus sources
  fetched this session.

### Sources actually fetched this session

1. `https://eprint.iacr.org/2026/1486` — abstract + metadata (received
   2026-07-20, approved 2026-07-23, CC BY, category "Attacks and
   cryptanalysis"). The PDF itself returned Cloudflare 403 to every available
   fetch path (curl, both fetch services); a Wayback save attempt failed
   (HTTP 520, no snapshot).
2. `https://bweso.com/papers.php` — author's list; the paper links only to the
   ePrint page.
3. `https://arxiv.org/html/2309.10432v2` — Page–Wesolowski arXiv v2 full text.
4. `https://inria.hal.science/hal-04209824v2/document` — Page–Wesolowski
   **published Eurocrypt 2024** text (numbering used for the Cor 1.2 check).
5. `https://yx7.cc/files/p-one-third.py` — Lorenz Panny's proof-of-concept
   (107 lines), the implementation referenced in the frozen text.

---

## 1. Lemma 3.2 — `#L(E,X,B) ≤ Ψ(X,B)·X(log X + 2)` — SOUND

Exact count re-derived independently (reference [2, Lemma 5.7] not fetched):

For `x = ∏ ℓ_i^{e_i}`, cyclic subgroups of order `ℓ^e` in `E[ℓ^e] ≅ (Z/ℓ^e)²`
number `ℓ^e + ℓ^{e-1} = ℓ^e(1 + 1/ℓ)`. The count is multiplicative over coprime
factors, so the number of cyclic-kernel degree-`x` isogenies from `E` is

```
I(x) = x · ∏_{ℓ|x} (1 + 1/ℓ).
```

Bound check:

```
I(x) = x · ∏_{ℓ|x}(1 + 1/ℓ) ≤ x · ∏_{ℓ^e‖x}(1 + 1/ℓ + … + 1/ℓ^e) = σ(x)
     ≤ x · H_x ≤ x (ln x + 1) ≤ x (log x + 2).
```

(`σ(x) ≤ x·H_x` since `σ(x) = Σ_{d|x} x/d ≤ x Σ_{k≤x} 1/k`.) So the paper's
bound holds with slack (a factor `+1` vs `+2`). Then

```
#L(E,X,B) = Σ_{x ∈ S(X,B)} I(x) ≤ Ψ(X,B) · X(log X + 2).  ✓
```

The bound is loose by design; nothing in the paper's later use requires
tightness. The citation [2, Lemma 5.7] was not independently verified, but the
claim is correct regardless.

## 2. Lemma 3.3 — cost of Algorithm 1/2 — GAP (minor defects, cost model OK)

### 2a. Presentation bug in Algorithm 1 (the main finding here)

Frozen pseudocode:

```
1. L ← ∅;
2. for ℓ ≤ B:
3.   for i = 1,…,⌊log_ℓ(X)⌋:
4.     for ψ ∈ L such that ℓ deg(ψ) ≤ X:
       … L ← L ∪ {η ◦ ψ | η ∈ L_{E′,ℓ}}
```

`L` starts empty and is only ever extended from entries already in `L`. **As
literally written the inner loop never executes and Algorithm 1 returns ∅.** It
must be seeded with the identity isogeny (`L ← {id_E}`) or the base case must
be special-cased. Corroboration from Panny's implementation (fetched this
session): the generator seeds with the length-0 chain —

```python
def isogs(smooth, max_deg, chain):
    yield chain                       # identity chain first
    ...
for _, chain in enumerate(isogs(B, X, [E.j_invariant()])):
```

Trivially fixable; but a reader transcribing the pseudocode gets an empty
algorithm, and Lemma 3.4's hypotheses then cannot be met. Recorded as GAP-1.

### 2b. The non-backtracking / cyclicity condition is exactly right

Claim to check: extending `ψ : E → E′` (cyclic kernel, deg `m`) by an
ℓ-isogeny `η : E′ → E′′` yields a cyclic-kernel composition iff
`ker(η) ⊄ ker(ψ̂)`.

- If `ℓ ∤ m`: `ker(η ◦ ψ) ≅ ker(ψ) ⋊ (order-ℓ part)` is automatically cyclic
  (coprime components), and `ker(η) ⊄ ker(ψ̂)` holds vacuously since
  `|ker ψ̂| = m` is coprime to `ℓ`. All `ℓ+1` choices valid.
- If `ℓ | m`: `ker(η◦ψ)` (order `ℓm`) is cyclic iff it does not contain
  `E[ℓ]`. `ker(η◦ψ) ⊃ E[ℓ]` iff `η(ψ(E[ℓ])) = 0`. Since `ker ψ̂` is cyclic of
  order `m` (duality preserves cyclicity), it has a **unique** order-ℓ
  subgroup, which equals `ψ(E[ℓ])`. So the composition fails cyclicity for
  exactly one of the `ℓ+1` choices of `η` — precisely the backtracking
  direction (dual of the last step). Excluded by `ker(η) ⊄ ker(ψ̂)`. ✓

Corroborated by Panny's counting function:

```python
num = l + (l != degs[-1])   # ℓ+1 choices for a new prime, ℓ when repeating
```

and by his j-level backtracking skip (`j == chain[-3]`).

### 2c. Enumeration completeness and uniqueness

Every cyclic-kernel B-smooth isogeny of degree `d = ∏ ℓ_j^{a_j}` is generated
exactly once: with primes processed in increasing order and the degree
monotone along the walk, intermediate kernels are the unique subgroups of the
final cyclic kernel, and the check `ℓ deg(ψ) ≤ X` never rejects a prefix of a
degree-≤-X target. ✓

### 2d. Cost accounting

- One `Φ_ℓ(j(E′),·)` instantiation + root-finding per (entry, prime) pair:
  ≤ `#L · π(B)` computations, each `(B + log p)^{O(1)}` (computing an
  instantiated classical modular polynomial and its `ℓ+1` roots over
  `F_{p²}` is polynomial in `ℓ ≤ B` and `log p`; the paper's footnote honestly
  leaves the `O(1)` exponent uninvestigated).
- Total: `#L · B · (B + log p)^{O(1)}`
  `= Ψ(X,B) · X^{1+o(1)} · B^{O(1)} · (log p)^{O(1)}`.
- **Sloppiness (GAP-3):** the lemma's statement writes `B^{O(1)}` where the
  proof yields `(B + log p)^{O(1)}`. Absorption of `(log p)^{O(1)}` into
  `B^{O(1)}` is valid only at the final choice
  `B = e^{(1/3)√log p}` (then `log B ≫ log log p`). Harmless for Thm 1.1.
- Final scan in Algorithm 2: `#L` conjugate computations (`(E′)^{(p)}` is
  coefficient-wise Frobenius, polylog) + hash lookups: `O(#L · polylog)`,
  dominated. Hash-table construction `O(#L)` (GAP-5) also dominated. ✓

Note also the lemma is *labeled* as bounding Algorithm 2's total time (list
construction via Algorithm 1 + final scan), which is consistent with its
proof; the task brief described it as "cost of Algorithm 1" — same content.

## 3. Lemma 3.4 — correctness of Algorithm 2 — SOUND

**(a) Minimality ⇒ cyclic kernel.** If `ker φ` is non-cyclic, then for some
prime `ℓ`, `E[ℓ] ⊂ ker φ`, so `φ = φ′ ◦ [ℓ]` with
`φ′ : E → E^{(p)}`, `deg φ′ = deg φ / ℓ² < deg φ` — contradicting minimality
of `φ : E → E^{(p)}`. ✓ (Sub-isogenies of a cyclic-kernel isogeny have cyclic
kernel: subgroups and quotients of cyclic groups are cyclic.)

**(b) Balancing at `X = B^{1/2}(p/2)^{1/6}`.** Write
`deg φ = ∏_{i=1}^n ℓ_i ≤ (p/2)^{1/3}` (Thm 1.5), `k` maximal with
`deg ψ = ∏_{i≤k} ℓ_i ≤ X`. If `k < n`:

```
deg ψ · ℓ_{k+1} > X   ⟹   deg ψ > X / ℓ_{k+1} ≥ X / B
deg η = deg φ / deg ψ ≤ (p/2)^{1/3} · B / X
      = B (p/2)^{1/3} / (B^{1/2} (p/2)^{1/6}) = B^{1/2} (p/2)^{1/6} = X.  ✓
```

`X² = B(p/2)^{1/3}` is exactly the minimal choice making both factors ≤ X —
consistent with the acknowledgement that Basso suggested replacing `B` by `√B`
in `X`. (Panny's implementation uses the older `X = B·(p/2)^{1/6}` —
consistent with that acknowledgement.)

**(c) `χ = η̂^{(p)} ∈ L(E,X,B)`.** `η : E′ → E^{(p)}` (codomain of `η` =
codomain of `φ`). Then `η̂ : E^{(p)} → E′`; Frobenius-twisting:
`χ = η̂^{(p)} : E^{(p²)} → E′^{(p)}`, and `E^{(p²)} = E` because `E` is defined
over `F_{p²}`. ✓ `deg χ = deg η` (twist preserves degree) is B-smooth, ≤ X;
`ker χ` cyclic (duals and twists preserve cyclicity — the paper compresses
this to "hence ψ and η also have cyclic kernel" plus membership of `χ`; the
implication chain holds). So `(E′^{(p)}, χ)` is an entry of the table. ✓

**(d) Returned map lands on `E^{(p)}` and is separable.** `χ̂ : E′^{(p)} → E`,
so `χ̂^{(p)} : E′ → E^{(p)}`, and `χ̂^{(p)} ◦ ψ : E → E^{(p)}`. ✓ Its degree
`deg χ · deg ψ ≤ X²` divides a B-smooth integer with `B < p` (the algorithm's
Require clause), hence is coprime to `p`, hence the isogeny is separable. ✓
(The paper doesn't write the separability argument; `B < p` makes it
immediate.) Any matching pair — not only the one arising from the minimal `φ`
— yields a valid separable isogeny `E → E^{(p)}`, so returning the first match
is correct. ✓

## 4. Lemma 3.5 + Remark 1 — SOUND

Heuristic 1 is stated **directly about the smallest isogeny**, so Lemma 3.5 is
a one-line set inclusion: `{Algorithm 2 succeeds} ⊇ {smallest isogeny is
B-smooth}`, and the heuristic lower-bounds the RHS probability by
`u^{-u(1+o(1))}`. No hidden conditioning; ties in minimal degree are harmless
(the event concerns the degree). ✓

Remark 1 is qualitatively correct: success only requires *some* cyclic-kernel
B-smooth isogeny of degree ≤ (p/2)^{1/3} (the balancing needs
`deg ≤ X²/B = (p/2)^{1/3}`); multiples `[m] ◦ φ′` of a small smooth `φ′` give
extra non-cyclic representatives; the improvement is absorbed in the `o(1)`. ✓

## 5. Theorem 1.1 — recomputed asymptotics — SOUND (tail not verified as written)

The tail of the proof is in the missing lines 201–350. Everything below is
**independently recomputed** from the parameters stated in lines 1–200.

Set `L := √log(p/2)`, `B = e^{(1/3)√log(p/2)} = e^{L/3}`, so `log B = L/3`
and `B = p^{o(1)}` ✓ (as the paper notes).

**u:**
```
u = log(p/2) / (3 log B) = L² / (3 · L/3) = L = √log(p/2).
```

**Range check for Heuristic 1 / Thm 1.4 (CEP):**
`u = (log p)^{1/2}(1+o(1))` satisfies `(log p)^ε < u < (log p)^{1−ε}` for any
`ε < 1/2`. Inside the uniformity range. ✓ (This is the classic break point for
such arguments; here it is fine — see §8.)

**Success probability per attempt and repetition count:**
```
P0 ≥ u^{−u(1+o(1))} = e^{−(1+o(1))·L·log L} = e^{−O(√(log p)·log log p)} = p^{−o(1)}
w  = 1/P0 = u^{u(1+o(1))} = p^{o(1)}.
```

**Smooth count at X:**
```
log X = ½ log B + (1/6) log(p/2) = L/6 + L²/6 ~ L²/6
u_X   = log X / log B ~ (L²/6)/(L/3) = L/2 = u/2
Ψ(X,B) = X · u_X^{−u_X(1+o(1))} = X · e^{−O(√(log p) log log p)} = X · p^{o(1)}-factor.
```

**Per-attempt cost (Lemma 3.3):**
```
T = Ψ(X,B) · X^{1+o(1)} · B^{O(1)}
  = X² · u_X^{−u_X(1+o(1))} · X^{o(1)} · B^{O(1)}
  = B·(p/2)^{1/3} · p^{o(1)}
  = p^{1/3} · e^{L/6} · p^{o(1)}
  = p^{1/3 + o(1)}.   ✓
```

**Total expected time:**
```
w · T = u^{u(1+o(1))} · p^{1/3+o(1)} = p^{o(1)} · p^{1/3+o(1)} = p^{1/3+o(1)}.  ✓
```

**Memory:** table size `#L ≤ Ψ(X,B)·X^{1+o(1)} = X²·p^{o(1)} = p^{1/3+o(1)}`
entries, each of polynomial size (a path of `O(log X)` j-invariants). ✓

**Random-walk mixing `n = O(log p)`:** standard for the Ramanujan
supersingular ℓ-isogeny graph (Pizer-type spectral gap); citations [37] and
[6, Lemma 14] not independently fetched, but the claim is standard. Walk cost:
`w · n · polylog(p) = p^{o(1)}`, absorbed. Statistical distance of the walked
curve from uniform perturbs `P0` negligibly. Pullback of the non-scalar
endomorphism through the walk isogeny `ω`: if `ω̂ α′ ω = [m]` then
`α′ = [m/deg ω]`, contradiction, so the pulled-back endomorphism is
non-scalar. ✓

**Non-scalar argument (inseparable degree):** `φ : E → E^{(p)}` separable of
degree `d`; Frobenius `ϕ : E^{(p)} → E` purely inseparable of degree `p`.
`ϕ ◦ φ ∈ End(E)` has inseparable degree `p^1`. A scalar `[m]` with
`m = p^a m′`, `p ∤ m′`, has inseparable degree `p^{2a}` — an **even** power of
`p`, i.e. a square. `p^1` is not a square, so `ϕ ◦ φ ∉ Z`. ✓ (The paper's
parenthetical "(which is not square)" is the right argument, minimally
stated.)

**Las Vegas:** repeat-until-success with geometric trial count of mean `w`;
output correctness is by construction (table key match on `E′^{(p)}`).
Consistent with the claimed "expected time and memory". ✓

## 6. Corollary 1.2 — GAP (citation defective; claim salvageable via [33])

Fetched the **published** Page–Wesolowski Eurocrypt 2024 text
(HAL hal-04209824v2). Published numbering:

- **Theorem 1.1** (intro; body reduction Theorem 7.2): *EndRing and OneEnd are
  equivalent under probabilistic polynomial-time reductions.* → supports the
  EndRing half of Corollary 1.2. Reduction overhead is polynomial in `log p`
  in time and memory; the oracle's `p^{1/3+o(1)}` dominates. ✓
- **Proposition 8.4** (*Isogeny reduces to EndRing*): "**Assuming the
  generalised Riemann hypothesis**, the problem Isogeny_λ reduces to EndRing
  in probabilistic polynomial time…"
- **Theorem 8.5** (*EndRing reduces to Isogeny*): unconditional, but the
  **converse direction** — not what Corollary 1.2 needs.
- **There is no Proposition 8.5** in the published version (Section 8 contains
  Theorems 8.1, 8.2, 8.4(Isogeny≤EndRing→mislabeled? no—Prop 8.4), 8.5 and
  Proposition 8.4; the arXiv v2 numbering differs again: Prop 13 = Isogeny ≤
  EndRing under GRH; Thm 8.4 = EndRing ≤ Isogeny).

So `[35, Proposition 8.5]` (i) does not exist as numbered, and (ii) the
intended result — Isogeny ≤ EndRing — is **GRH-conditional in [35]**, while
Corollary 1.2 states an unconditional (modulo Heuristic 1) Las Vegas
`p^{1/3+o(1)}` algorithm. The claim is nonetheless **true in 2026**: the
unconditional equivalency network of **[33]** (Le Merdy–Wesolowski,
"Unconditional foundations…", arXiv:2502.17010 — itself cited in the frozen
text at line 127 for exactly this network) gives Isogeny ≤ EndRing
unconditionally in probabilistic polynomial time, with polynomial memory, so
both time and memory `p^{1/3+o(1)}` are preserved. Required fix: cite [33]
(or state GRH). Recorded as GAP-2.

Also verified: the OneEnd solver of Thm 1.1 works for *arbitrary* input curves
(it internally re-randomizes via the walk), so the reductions' oracle
queries (which need not be uniform) are covered. ✓

## 7. Section 4.1 methodology — UNVERIFIABLE-AS-WRITTEN (text in missing tail)

Assessment of the claims as posed in the task brief:

- "**number of degree-d isogenies is at least d**": TRUE for cyclic-kernel
  counts — `I(d) = d·∏_{ℓ|d}(1+1/ℓ) ≥ d`. ✓
- "**M = Ψ(X,B)·X is a lower bound**" on `#L = Σ_{d∈S(X,B)} I(d)`: requires
  `Σ_{d∈S} d ≥ X·Ψ(X,B)`, i.e. average smooth `d ≥ X` — false. In the paper's
  regime (`u_X → ∞`), `Ψ(X/2,B)/Ψ(X,B) → 1/2` (since
  `u′ = log(X/2)/log B = u_X − log2/log B = u_X(1−o(1))`, so
  `u′^{−u′}/u_X^{−u_X} → 1`), hence
  `Σ_{d∈S} d ≥ (X/2)(Ψ − Ψ(X/2,B)) ~ XΨ/4`. So `M` overstates any rigorous
  lower bound by a constant factor (~2–4×). As an order-of-magnitude memory
  estimate: fine, and the frozen introduction explicitly hedges §4.1 as
  tentative/optimistic (line 43). But "lower bound" is the wrong label
  (GAP-9).
- **Optimizing B for best time** with `M(B)`, `P0(B)` both B-dependent:
  legitimate numerical minimization of `w(B)·T(B)` subject to the CEP range
  and `B < p`; standard and does not contaminate the asymptotic proof. ✓

## 8. Heuristic 1 — statement audit — SOUND WITH CAVEATS

- **Quantifiers**: uniformly random supersingular `E/F_{p²}`; event = degree
  of the smallest isogeny `E → E^{(p)}` is B-smooth; bound
  `≥ u^{−u(1+o(1))}` with `u = log(p/2)/(3 log B)`; uniformity
  `p → ∞`, `(log p)^ε < u < (log p)^{1−ε}`. Coherent. ✓
- **CEP range for the chosen B**: `u = √(log(p/2))` (computed in §5) —
  satisfies the range for any `ε < 1/2`. **No violation.** The second use of
  Thm 1.4 (cost analysis at `X`) uses `u_X = u/2`, also in range relative to
  `log X ~ (1/6)log p`. ✓
- **Structural caveats** (acknowledged by the paper, inherent to the
  heuristic): the degree of the *smallest* isogeny is a
  minimum-over-a-large-family statistic, not a uniform integer; the heuristic
  asserts the random model anyway. Thm 1.5 is only a worst-case bound, so if
  typical minimal degrees are smaller, true smoothness probability is *larger*
  — the heuristic is directionally conservative. The assumption is unproven by
  design and correctly labeled.

## 9. Unjustified / unstated needs (list)

1. **GAP-1** Algorithm 1 never seeds `L` — returns ∅ as written (see §2a).
2. **GAP-2** Cor 1.2 citation `[35, Prop 8.5]`: nonexistent number; intended
   Prop 8.4 is GRH-conditional (see §6).
3. **GAP-3** Lemma 3.3: `B^{O(1)}` vs `(B + log p)^{O(1)}` (see §2d).
4. **GAP-4** Efficient-representation conversion of the final isogeny (Vélu
   per step + interpolation) is mentioned in Algorithm 2's note but never
   costed; it is `poly(B, log p) = p^{o(1)}` (number of steps ≤ `log₂(deg) =
   O(log p)`, each step `poly(ℓ, log p)`), so asymptotically harmless — but
   unjustified in the text.
5. **GAP-5** Hash-table construction cost `O(#L)` unstated (dominated).
6. **GAP-6** "The algorithm parallelizes perfectly" (line 39): attempts are
   independent, but *each* parallel instance needs the full `p^{1/3+o(1)}`
   memory; memory is the binding constraint, and the claim does not commute
   with the van Oorschot–Wiener tradeoff in the same paragraph. Asserted, not
   justified.
7. **GAP-7 (load-bearing)** Thm 1.5 ([4]) — existence of an isogeny
   `E → E^{(p)}` of degree `≤ (p/2)^{1/3}` — is the crux external input; the
   `1/3` exponent comes directly from it. Bibliography unavailable (missing
   tail); [4] could not be identified or verified this session. The whole
   result inherits the correctness of [4].
8. **GAP-8** Unverified citations: [2, Lemma 5.7] (re-derived independently —
   claim correct), [6, Lemma 14]/[37] (mixing — standard), [10] (standard
   CEP), [27, §25.2] (modular-polynomial roots — standard).
9. **GAP-9** §4.1's `M = Ψ(X,B)·X` "lower bound" is off by a constant factor
   (see §7).
10. **GAP-10 (provenance)** Frozen input disappeared mid-review; lines 201–350
    unverified as written. Coordinator should restore the frozen file and
    schedule a scoped re-review of the tail if it contains material beyond
    what was independently recomputed here.

## 10. Summary of verdicts

| # | Item | Verdict |
|---|------|---------|
| 1 | Lemma 3.2 | SOUND |
| 2 | Lemma 3.3 | GAP (presentation bug in Algorithm 1; `B^{O(1)}` sloppiness; cost model otherwise correct) |
| 3 | Lemma 3.4 | SOUND |
| 4 | Lemma 3.5 + Remark 1 | SOUND |
| 5 | Thm 1.1 proof | SOUND (asymptotics independently recomputed = `p^{1/3+o(1)}`; tail text not verified as written) |
| 6 | Cor 1.2 | GAP (citation misnumbered + hidden GRH; claim salvageable via [33]) |
| 7 | §4.1 methodology | UNVERIFIABLE-AS-WRITTEN (`I(d) ≥ d` true; `M = Ψ·X` lower bound off by constant factor; B-optimization legitimate) |
| 8 | Heuristic 1 | SOUND WITH CAVEATS (chosen `u = √log(p/2)` inside CEP range; assumption unproven by design) |

**Overall**: core mathematics sound (conditional on Heuristic 1 and the
unverified external Thm 1.5/[4]); presentation-level gaps recorded above. No
mathematical ERROR found in any verifiable part.
