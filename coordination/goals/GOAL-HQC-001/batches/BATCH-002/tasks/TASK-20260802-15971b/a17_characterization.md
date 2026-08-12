# Assumption A17 — formal statement, distinguishable readings, and load-bearing trace

**Task**: `TASK-20260802-15971b` (executor) · **Batch**: `BATCH-002` ·
**Goal**: `GOAL-HQC-001` · **Question**: `RQ-HQC-001`
**Produced**: 2026-08-02 · **Repo commit at start**: `7f8a78d47bd35298cd140838381872d65bb2c0f1` (clean tree)
**Primary input**: `…/BATCH-001/tasks/TASK-20260802-6344ed/dfr_model_transcription.md` (A17)
**Sources**: SPEC `174186cb…` and RMRS `cbb7dbd6…`, re-acquired and hash-verified — `proof_search_log.md` §0.2

---

## 0. What this document is, and what it is not

This is a **characterization of one assumption in an already-obtained text**. It
states A17 formally, enumerates every reading it can distinguish, traces which
transcribed results depend on it, and checks it against a null object.

It is **not an experiment design**. It contains no protocol, no parameter
selection, no trial count, no seed strategy, no success criterion, no
measurement plan, and no stopping rule. `RQ-HQC-001.constraints[0]` forbids
experiment design until the primary sources are **filed** as `KN-LIT` entries;
filing is the concurrent sibling task `TASK-20260802-63b16a` and this document
assumes nothing about its outcome.

It makes **no security claim about HQC in either direction.** That A17 is
unproved in two documents is a statement about **the literature**, not about
HQC. Claim-tier ceiling: **toy**. `certificate.kind: none`. Nothing here is
admissible toward an `AGENTS.md` rule 13 closure quorum: this session is an
independent *session* on the same backend as every other task in this goal.

**Inference**: `requested_policy: executor-implementation`,
`resolved_model_id: claude-opus-5`, `fallback_used: true`,
`model_verified: false`, `independent_session: true`.

### 0.1 Headline, stated before the argument so it cannot be mis-summarised

1. A17 is **genuinely load-bearing**: Theorem 6.1 has no other engine, Theorem
   6.1 is the sole numeric source of the δ that enters the IND-CCA2 bound, and
   nothing downstream supersedes it (§4).
2. Neither primary source proves, weakens, or even acknowledges it, and the
   citation chain that could carry a proof is two links long and exhausted
   (`proof_search_log.md` §8).
3. **But A17 is not a second, independent assumption.** It is a *logical
   consequence* of A5 (coordinate independence) applied to disjoint blocks, plus
   a symmetry that is provable outright. The red team's framing — *"a second,
   independent use of an independence assumption, stacked on A5's"* — is right
   about **use** and wrong about **assumption**, and the difference decides what
   the eventual target should be (§3.5, §5.4).
4. What is genuinely open is **not a logical gap but an evidential one**: A5's
   published support measures the *global* weight of `e′` and the weight inside
   *one* inner block, while A17's use requires the *joint* law across all `n_e`
   blocks — specifically a `(δ_e+1)`-way co-failure probability. No published
   statistic in either source constrains that quantity beyond its first moment
   (§5.5).
5. Therefore A17 **is** a defensible target, but the sharper object is
   `μ_{δ_e+1}` (§3.3, `a17_sensitivity.yaml`), and a **cheaper and larger**
   competing item exists in the same trace: A19, worth **10.6 / 8.0 / 16.8 bits**
   at NIST-1/3/5, settled by *reading* rather than by measuring (§6.1).

---

## 1. The object: notation, fixed once

All symbols are the sources' own; where this document introduces a symbol the
sources lack, it is marked **[new here]** — the sources have no name for a
concatenation block (`proof_search_log.md` §6.4), so some new notation is
unavoidable.

| symbol | meaning | source |
|---|---|---|
| `n` | ambient length; smallest primitive prime `> n₁n₂` | SPEC §4.1 |
| `n₁ = n_e` | length of the external (shortened Reed–Solomon) code, in `F₂₅₆` symbols | SPEC §4.1, Table 5 |
| `n₂ = n_i` | length of the internal (duplicated Reed–Muller) code, in bits | SPEC §4.1, Table 5 |
| `k_e, d_e, δ_e` | RS dimension, minimum distance, correction capacity; `d_e = 2δ_e + 1` | SPEC Table 3, Thm 6.1 |
| `d_i` | minimum distance of the duplicated RM code; `n₂ = 2d_i` | SPEC §6.1.2 |
| `x, y, r₁, r₂, e` | uniform independent fixed-weight vectors, weights `ω, ω, ω_r, ω_r, ω_e` | SPEC §6.1.1 (A1) |
| `e′ = x·r₂ − r₁·y + e ∈ F₂ⁿ` | the error vector | SPEC §6.1 |
| `p̃`, `p⋆` | per-coordinate Bernoulli parameters | Props 6.1.1, 6.1.2, Eq. (2) |
| `p_i` | the internal-code DFR **upper bound** of Prop 6.1.3 (per Thm 6.1's text) or Prop 6.1.4 (per Table 11's header) | SPEC §6.1.2 (see A19) |
| `ẽ ∈ F₂^{n₁n₂}` **[new here]** | `e′` truncated to its first `n₁n₂` coordinates (A23) | SPEC §3.5, p.34 |
| `B_j = {j·n₂, …, (j+1)·n₂ − 1}`, `j = 0…n_e−1` **[new here]** | the `j`-th inner block's coordinate set | implicit in SPEC §3.4.1 |
| `ẽ^{(j)} = ẽ|_{B_j} ∈ F₂^{n₂}` **[new here]** | the error restricted to block `j` | — |
| `D_i` **[new here]** | the inner maximum-likelihood decoder (Hadamard, SPEC §3.4.3) | SPEC §3.4.1, A12 |
| `F_j = 1{D_i(ẽ^{(j)}) ≠ 0}` **[new here]** | indicator that inner block `j` decodes to the wrong RM codeword, hence to the wrong `F₂₅₆` symbol | — |
| `S = Σ_{j=0}^{n_e−1} F_j` **[new here]** | number of erroneous symbols entering the outer RS decoder | — |
| `q = P[F_j = 1]` **[new here]** | the **true** per-block failure probability. `q ≤ p_i`; `q ≠ p_i` | — |
| `μ_k = P[F_{j₁} = ⋯ = F_{j_k} = 1]` **[new here]** | `k`-way joint failure probability, well defined by Lemma L1 | — |
| `m = δ_e + 1` **[new here]** | the smallest number of symbol errors that defeats the outer decoder | Thm 6.1's summation limit |

By linearity of the inner code and translation-invariance of minimum-distance
decoding, inner block `j` decodes correctly **iff** `D_i(ẽ^{(j)}) = 0`, so `F_j`
is a function of `ẽ^{(j)}` alone (plus the decoder's tie-breaking, see R-tie in
§3.6). Under A18, the outer bounded-distance RS decoder succeeds **iff**
`S ≤ δ_e`. Hence

```
DFR  =  P[ S > δ_e ]  =  P[ S ≥ m ].
```

**The whole of §6.1.3 is the problem of computing `P[S ≥ m]`.**

---

## 2. DUTY 1 — A17 stated formally

### 2.1 The two probability spaces, which the sources never separate

This is the single most important disambiguation in the document, and it is
prior to every reading in §3.

Two distinct probability spaces are in play, and every statement below is
ambiguous until one is chosen:

- **Space (T) — the true space.** `(x, y, r₁, r₂, e)` are drawn uniformly and
  independently from their fixed-weight sets (A1, SPEC §6.1.1 verbatim);
  `e′ = x·r₂ − r₁·y + e`; `ẽ` is its truncation. This is the distribution
  `δ`-correctness is actually about (SPEC Eq. (12) conditions the probability on
  exactly these sampling calls).
- **Space (M) — the model space.** `ẽ ∼ Bernoulli(p⋆)^{⊗n₁n₂}`, i.e. the binary
  symmetric channel that A5 substitutes for (T): *"In other words we modelize the
  error vector as a binary symmetric channel with parameters p∗"* (SPEC §6.1.1,
  verbatim; the sentence is SPEC's own addition and is absent from RMRS's
  otherwise identical paragraph).

**On (M), A17 is a theorem — it needs no assumption at all.** The `B_j` are
disjoint, `F_j` is a function of `ẽ^{(j)}`, and functions of disjoint blocks of
independent coordinates are independent. On (M) the `F_j` are exactly i.i.d.

**On (T), A17 is an unproved assertion**, because the coordinates of `ẽ` on (T)
are demonstrably *not* independent — `x, y, e` have exactly fixed weights, and
the sources' own simulations show the weight of `e′` is under-dispersed relative
to the binomial (SPEC Table 10; RMRS Tables 2, 3; quantified at
`proof_search_log.md` §7.5: variance ratio 0.61–0.74 across three published
tables and four tail depths).

**Neither source states at which step it changes space.** SPEC §6.1.1 announces
the substitution for *"the weight distributions of `e′`"* — a **scalar**
functional. Props 6.1.3/6.1.4 then use (M) restricted to **one block**. Theorem
6.1 uses (M) **jointly across all `n_e` blocks**. The last of those three uses
is the widest, is never announced, and is A17.

**Formally A17 is the assertion that the substitution (T) → (M) is valid for the
functional `S`, or at least conservative for the event `{S ≥ m}`.**

### 2.2 A17, primary formal statement

> **A17 (primary form).** Let `ẽ` be distributed as in space (T). Let
> `F_j = 1{D_i(ẽ^{(j)}) ≠ 0}` for `j = 0, …, n_e − 1`. Then `F_0, …, F_{n_e−1}`
> are **mutually independent** and **identically distributed**, with common
> failure probability equal to `p_i` (Prop 6.1.3 or 6.1.4; see A19).
> Equivalently, for every `J ⊆ {0, …, n_e−1}`,
> `P[⋀_{j∈J} F_j = 1] = p_i^{|J|}`, whence
> `S ∼ Binomial(n_e, p_i)` and
> `P[S ≥ m] = Σ_{l=m}^{n_e} C(n_e, l) p_i^l (1−p_i)^{n_e−l}`,
> which is Theorem 6.1's expression **as an equality**.

That is the assumption the formula literally encodes. It is also **too strong to
be what the theorem means**, because the theorem says *"can be upper bounded
by"* and `p_i` is itself an upper bound on `q`. §3 resolves this.

### 2.3 Where in the chain A17 is applied

At exactly one step, and it is a step neither source writes down:

```
SPEC 6.1.1  ──►  per-coordinate law of e'_k                    [proved, Prop 6.1.2]
             │
             ├── A5: (T) -> (M) for weight functionals         [assumed, hedged H1-H3, simulated]
             ▼
SPEC 6.1.2  ──►  q <= p_i  for ONE block                       [proved on (M), Props 6.1.3/6.1.4]
             │
             ├── A17: the n_e blocks' outcomes are i.i.d.       <== HERE. Not stated. Not proved.
             ▼                                                     Not acknowledged. Not cited.
SPEC 6.1.3  ──►  Theorem 6.1: binomial tail                    [stated; NO PROOF in either source]
             │
             ├── A18: outer RS fails iff S > delta_e
             ▼
SPEC 6.2.2  ──►  delta := that number                          [A20, A21]
             ▼
SPEC 6.2.2  ──►  Adv^{IND-CCA2} <= ... + (q_RO + q_D)*delta + ...   [Theorem 6.3]
```

---

## 3. DUTY 1 (continued) — every distinguishable reading

The transcription's phrasing of A17 is a **reconstruction from a formula**, not
a quotation, because there is no prose to quote. That makes disambiguation
mandatory: an ambiguous assumption cannot be tested. Six axes are
distinguishable. Each is stated as a self-contained proposition, with what
follows from it and which reading the surrounding text supports.

### 3.1 R1 — literal i.i.d. at `p_i` (the formula's face value)

> `F_0, …, F_{n_e−1}` i.i.d. Bernoulli(`p_i`).

**Makes Theorem 6.1 an equality.** **Not supported by the surrounding text**:
Theorem 6.1 says *"can be upper bounded by"*, §6.1.2's lead-in calls the Props
*"a lower bound on the decoding probability"*, and §6.1.3's lead-in says *"Using
the lower bound `p_i`"*. All three phrasings mean `p_i` is an over-estimate of
the true per-block failure rate, and SPEC Table 11's own simulation confirms it
(bound `−10.79` vs observed `−10.96` at NIST-1). R1 is what the formula says and
is **not** what the theorem claims.

### 3.2 R2 — i.i.d. at the true `q`, plus `q ≤ p_i`, plus monotonicity (the reading the text supports)

> (i) `F_0, …, F_{n_e−1}` are mutually independent;
> (ii) they are identically distributed with common failure probability `q`;
> (iii) `q ≤ p_i`;
> (iv) `x ↦ Σ_{l≥m} C(n_e,l) x^l (1−x)^{n_e−l}` is non-decreasing on `[0,1]`.

Then `P[S ≥ m] =_(i),(ii) Tail(n_e, m; q) ≤_(iii),(iv) Tail(n_e, m; p_i)`, which
is Theorem 6.1 **as an upper bound**. This is what the theorem asserts and what
its lead-in describes.

Of the four clauses:

- **(iv) is a true lemma, not an assumption.** `Tail(n, m; x) = P[Bin(n,x) ≥ m]`
  is non-decreasing in `x` by the standard coupling `Bin(n,x) ≼ Bin(n,x′)` for
  `x ≤ x′`. Neither source states it. It costs nothing and is recorded only for
  completeness.
- **(iii) is proved on space (M)**, by Props 6.1.3/6.1.4, and is supported on
  space (T) restricted to one block by RMRS Remark 4.2 (support length 256).
- **(ii) is a theorem, not an assumption** — see Lemma L1 below.
- **(i) is the whole of A17's substance.**

> **Lemma L1 (the "identically distributed" half is free).** On space (T) the
> `F_j` are exchangeable, hence identically distributed.
>
> *Argument.* `x, y, r₁, r₂, e` are drawn uniformly from fixed-weight sets in
> `R = F₂[X]/(Xⁿ − 1)`, which are invariant under cyclic shift, and the map
> `(x,y,r₁,r₂,e) ↦ x·r₂ − r₁·y + e` commutes with cyclic shift. Hence the law of
> `e′` is invariant under the cyclic group of order `n`. The blocks `B_j` are
> cyclic translates of `B_0` by `j·n₂`, so `ẽ^{(j)} ∼ ẽ^{(0)}` for every `j`, and
> `F_j ∼ F_0`. ∎
>
> *Caveat, stated because it is load-bearing for the argument's exactness.*
> `n > n₁n₂`, and A23 truncates `ℓ = n − n₁n₂` trailing coordinates (`ℓ = 5` at
> HQC-1, `n = 17 669`, `n₁n₂ = 17 664`). Truncation breaks the cyclic symmetry of
> the *index set*, but every `B_j` for `j ≤ n_e − 1` remains a translate of `B_0`
> **within** the retained window, so the conclusion is unaffected. The argument
> gives **exchangeability of the `F_j`**, not independence, and this is exactly
> the distinction the sources elide.

**Consequence: the entire content of A17 is clause (i), independence.** The
"identically distributed" half is provable and the substitution of `p_i` for `q`
is a lemma. This narrows the target usefully.

### 3.3 R3 — the weakest sufficient condition (what actually has to be true)

Independence is far more than Theorem 6.1 needs. The weakest condition this
document can identify that preserves the bound is:

> **R3 (negative upper-orthant dependence).** `μ_k ≤ q^k` for all
> `k ∈ {m, …, n_e}` and all index sets of size `k`, together with `q ≤ p_i`.

`a17_sensitivity.yaml` derivation steps 1–2 show that at the published
parameters the `l = m` term carries **≥ 99.90 %** of the Theorem 6.1 tail
(0.999006 / 0.999880 / 0.999245 at HQC-1/3/5), so to leading order
`P[S ≥ m] ≈ C(n_e, m)·μ_m` and the bound survives whenever `μ_m ≤ q^m`.

**R3 is strictly weaker than R2(i) and is what a proof would actually target.**
Neither source states it, and this document does not claim it holds.

### 3.4 R4 — block-vector independence (the mechanism, and it is A5)

> `ẽ^{(0)}, …, ẽ^{(n_e−1)}` are mutually independent random vectors in `F₂^{n₂}`,
> each with the law of `n₂` i.i.d. Bernoulli(`p⋆`) coordinates.

R4 ⟹ R2(i) and R2(ii) immediately (§3.6 for the tie-breaking rider). R4 is
**precisely A5 restricted to the `n₁n₂` retained coordinates** — it is not a new
assumption, it is A5 read at block granularity. This is the finding in §0.1
item 3 and it is developed in §5.4.

### 3.5 R5 — the "conservative substitution" reading

> The substitution (T) → (M) is not claimed to be exact for `S`, only
> conservative: `P_T[S ≥ m] ≤ P_M[S ≥ m]`.

This is the reading most consonant with the specification's **stated intent**,
because A6/H2/H3 assert exactly that shape for the model as a whole:
*"our computations of decoding error probabilities and DFRs can only be upper
bounds on their real values."* Under R5 the theorem is fine even if the `F_j`
are dependent, provided the dependence pushes the right way.

**R5 is the reading a reviewer should hold the model to, and it is also the one
with the least support**, because the justification offered for it
(SPEC §6.1.1's *"conditioned on abnormally many others equalling 1 can
realistically only be ≤ p∗"*, plus the simulations) is an argument about the
**upper tail of the scalar `ω(e′)`**, not about the joint law of `n_e`
decoder outcomes. See §5.5.

### 3.6 R-tie — the decoder's tie-breaking randomness

`F_j` is a function of `ẽ^{(j)}` *and* of whatever resolves ties in the inner
decoder. SPEC §3.4.3's Hadamard decoder *"take[s] the maximum value in F̂"*
(deterministic, implementation-defined on ties); A13/Prop 6.1.4 model ties as
resolved *uniformly at random* (`P(E|A′) = 1/2`). Under the A13 model, A17
additionally requires the per-block tie-breaks to be independent across blocks —
trivially true for a randomized decoder with fresh randomness, and **not**
automatic for the deployed deterministic one, where the tie-break is a function
of the block content and therefore carries no extra dependence either.
**Verdict: R-tie is a genuine but negligible rider.** Recorded so the formal
statement is complete, not because it is a candidate target.

### 3.7 R-p — which `p_i` (this is A19, and it is an ambiguity of the same sentence)

Theorem 6.1's own text says *"`p_i` is defined as in proposition 6.1.3"* (the
simple union bound); Table 11's column header says *"DFR from 6.1.4"*; §6.1.3's
lead-in points at *"Section 6.1.2"*, which contains both. Under R2 either choice
keeps the theorem **true** (both are upper bounds on `q`), so R-p is an
ambiguity of **tightness**, not of validity. Its size is computed in §6.1 and it
is large.

### 3.8 Summary of readings

| reading | statement | makes Thm 6.1 | text support | status |
|---|---|---|---|---|
| **R1** | i.i.d. at `p_i` | an equality | **contradicted** by *"upper bounded by"*, *"lower bound `p_i`"*, Table 11 | the formula's face value; not the claim |
| **R2** | independent + i.d. at `q`, `q ≤ p_i`, tail monotone | an upper bound | **supported** — matches §6.1.2 and §6.1.3 lead-ins | **the intended reading** |
| **R3** | `μ_k ≤ q^k` (NUOD) + `q ≤ p_i` | an upper bound to leading order | not stated anywhere | **weakest sufficient; the real target** |
| **R4** | block *vectors* independent, each BSC(`p⋆`) | an upper bound | this **is** A5 | the mechanism; not a new assumption |
| **R5** | substitution merely conservative for `S` | an upper bound | matches A6/H2/H3's *intent* | the honest reading; least supported |
| **R-tie** | tie-breaks independent across blocks | — | none | complete-statement rider, negligible |
| **R-p** | `p_i` = 6.1.3 or 6.1.4 | tightness only | **three inconsistent cross-references** | = A19; worth 10.6–16.8 bits (§6.1) |

---

## 4. DUTY 4 — the load-bearing trace

Which transcribed results depend on A17, in any reading. `proof_search_log.md`
§3, §4, §6 record where each was read.

| transcribed result | depends on A17? | why |
|---|---|---|
| Prop 6.1.1 (per-coordinate law of `x·r`) | **no** | exact, proved (SPEC p.33). Uses A2 only. |
| Eq. (1); Prop 6.1.2; Eq. (2) | **no** | exact per-coordinate law, proved. Uses A1, A3, A4. |
| Eq. (3) (binomial weight model) | **no** | this **is** A5 |
| **Prop 6.1.3** (simple upper bound) | **no** | single block. Uses A5-within-one-block (A8), A9, A10, A11, A12. Proved. |
| **Prop 6.1.4** (improved upper bound) | **no** | single block. Adds A13–A16. Proved. |
| SPEC Table 11 / RMRS Table 4 | **no** | single-block simulation under a BSC |
| **Theorem 6.1 / RMRS Theorem 4.3** | **YES — entirely** | A17 is the *only* route from `p_i` to a binomial tail. **No proof exists in either source**, and RMRS's two-item bibliography is cited on no page of the proof region (`proof_search_log.md` §6.3). Remove A17 and the theorem has no derivation, not a weaker one. |
| SPEC Table 5's `DFR` column (`< 2⁻¹²⁸/2⁻¹⁹²/2⁻²⁵⁶`) | **YES**, via Thm 6.1 | the only quantitative DFR the specification states |
| Def 6.2.1 (δ-correct PKE) | **no** | a definition; A17-free |
| SPEC Eqs. (11), (12) — the δ join | **no** as a *derivation*; **YES** for the *value* | Eqs. (11)/(12) rest on A20 (`failure ⟺ ω(e′) > ∆`). The **number** substituted for δ is Theorem 6.1's, hence A17's (A21). |
| **Theorem 6.3 (IND-CCA2)** | **YES**, transitively and **linearly** | δ enters as the additive term `(q_RO + q_D)·δ` (SPEC p.44). A multiplicative distortion `A` on the DFR is a distortion `A` on that term, to first order in δ. |
| §6.2.3 sampler correction (Prop 6.2.1, Lemma 6.4, Table 12) | **no** | multiplies δ by at most `(τ^{ω_r}_max)³ ≈ 1.00045` at NIST-1; orthogonal to A17 |

### 4.1 Is Theorem 6.1 superseded by anything?

**No.** It is terminal: nothing downstream recomputes the concatenated DFR by
another route, and no later section improves it. This matters because the
handoff explicitly warns that *"an assumption that only affects an intermediate
bound which Theorem 6.1 supersedes is NOT the target it appears to be."*

The trace shows that description **does** fit other assumptions in the same
list, and it is worth naming them so the contrast is concrete:

- **A9** (union bound over the 255 RM codewords) and **A10** (dropping the
  weight-128 codeword) live inside Prop 6.1.3, whose value **is** superseded by
  Prop 6.1.4 for every reported number (Table 11's column header, and only 6.1.4
  reproduces the tabulated values — BATCH-001 red team §3, reproduced
  independently at `proof_search_log.md` §7.1).
- **A17** is in the opposite position: it is the engine of the one result nothing
  supersedes.

### 4.2 A17 does not affect Props 6.1.3/6.1.4 at all

Worth stating explicitly because it bounds the target. If A17 fails, the inner
bounds `p_i` are **unaffected** — they are per-block statements proved from A5
restricted to one block, and RMRS Remark 4.2 is direct (single-block) evidence
for that restriction. A failure of A17 moves **only** the stage-2 → stage-3
transfer, and it moves it by the factor derived in `a17_sensitivity.yaml`.

---

## 5. DUTY 5 — null-object check (controls before belief)

`docs/inventor-protocol.md` §3: *"Any apparent signal is an artifact until a
control says otherwise."* The signal here is *"A17 matters"*. The control is:
**what does an assumption that is merely conventional bookkeeping look like in
this same trace, and does A17 look like one?**

### 5.1 The null profile, declared before A17 is scored against it

An assumption in this chain is **conventional bookkeeping** if it satisfies at
least one of:

- **N1 — no numeric effect.** Removing or negating it changes no reported number
  beyond reporting precision.
- **N2 — superseded.** The result it supports is replaced downstream by a result
  that does not use it.
- **N3 — not an assumption.** It is a true statement (a lemma, a construction
  fact, or a consequence of an assumption already made), so it carries no
  independent risk.
- **N4 — insensitive.** Its violation moves the terminal bound by `o(1)` bits
  across any violation magnitude the surrounding evidence leaves open.

### 5.2 Named null objects that are actually present in the same trace

Not hypothetical. Each is scored with a computed number
(`proof_search_log.md` §7.4).

| assumption | null criterion met | measured effect |
|---|---|---|
| **A10** — drop the weight-128 codeword, round 254 → 255 | **N1, N4** | `log₂(255/254) = 0.00567` bits on `p_i`; `≈ m × 0.00567 =` **0.091 / 0.096 / 0.170** bits on Theorem 6.1. Pure bookkeeping. |
| **A2, A3, A4** — independence of `x, y, r₁, r₂, e` | **N3** | true **by construction** of `SampleFixedWeightVect$`, which draws them independently. Not assumptions in the uniform-sampler model at all. |
| **A23** — truncate `ℓ = n − n₁n₂` trailing bits | **N3, N1** | definitional; `ℓ = 5` at HQC-1 out of `n = 17 669` |
| **A9** — union bound inside Prop 6.1.3 | **N2** | superseded by Prop 6.1.4 for every reported value |
| **A16** — the `min[C(n,ω), …]` cap in Prop 6.1.4 | **NONE** | cap is **active** in 219 of 289 summands (HQC-1) and 354 of 481 (HQC-3 and HQC-5, which share `d_i = 320`); removing it moves `p_i` by **0.374** bits at HQC-1 and **0.290** at HQC-5, i.e. `≈ m ×` that `=` **6.0** and **8.7** bits on Theorem 6.1 (HQC-3 not computed for this row). **Fails the null.** |

**A16 is the reason this control is informative.** A null profile that classifies
everything as bookkeeping would be a rubber stamp. This one discriminates: it
passes A10, A2–A4, A23 and A9, and it **fails** A16 — an assumption BATCH-001
recorded in the same undifferentiated list, which turns out to carry ~6–9 bits.

### 5.3 A17 scored against the null

| criterion | A17 | verdict |
|---|---|---|
| **N1** — no numeric effect | Removing A17 does not perturb Theorem 6.1's value; it **deletes Theorem 6.1's derivation**. There is no residual expression. | **fails** |
| **N2** — superseded | Theorem 6.1 is terminal (§4.1). | **fails** |
| **N3** — not an assumption | **PARTIALLY MET — and this is the twist.** On space (M), A17 *is* a theorem, following from A5 by block disjointness; and the identically-distributed half is provable outright on space (T) (Lemma L1). | **partially met** |
| **N4** — insensitive | Sensitivity coefficient `K = C(m,2)(1−q)/q = 2¹⁷·⁷⁰ / 2²¹·²³ / 2²⁰·⁰⁹`. An inter-block failure correlation of `≈ 4.7×10⁻⁶` (HQC-1) already moves the bound by one bit; `≈ 4.8×10⁻³` moves it by ten. | **fails decisively** |

### 5.4 What the control actually found — reported, not softened

**A17 is not conventional bookkeeping (N1, N2, N4 all fail decisively), and it is
also not a second independent assumption (N3 partially fires).**

The correct characterization is:

> **A17 is a logically redundant restatement of A5 at block granularity,
> carrying an evidential gap that A5's own published support does not cover.**

This *corrects* the framing this task inherited. The BATCH-001 red team wrote
(O10) that A17 is *"a second, independent use of an independence assumption,
stacked on A5's coordinate-level one"*. **The word "use" is right and the
implication of a second independent assumption is wrong**: assuming A5 and then
assuming A17 is not assuming two things. Anyone attacking A17 as an independent
proposition would be attacking A5 in disguise, and would find — correctly — that
A5 is explicitly stated, explicitly hedged (H1–H3), and simulation-supported,
and might conclude the lead was weaker than advertised.

**It is not weaker. The lead survives the control, in a different place.**

### 5.5 The evidential null — where A17 genuinely fails

Apply the same control on the evidence axis. **What would an assumption look
like whose supporting evidence covers the functional it is used for?** It would
be one where the measured quantity and the used quantity are the same object.

| assumption | functional it is *used* for | functional the published evidence *measures* | match? |
|---|---|---|---|
| A5 (as used by Props 6.1.3/6.1.4) | weight of `ẽ` inside **one** block, `n₂ ∈ {384, 640}` | RMRS Fig. 4 / Remark 4.2: weight of `e′` restricted to **one** RM support, length **256** | **yes** (near-match; different length, same object class) |
| A5 (as used by A6/H3's "upper bound" claim) | upper tail of the **scalar** `ω(e′)` | SPEC Table 10, RMRS Tables 2/3, Figs. 2/3: upper tail of the **scalar** `ω(e′)` | **yes** |
| **A17** | the **`n_e`-fold joint** law of `(F_0,…,F_{n_e−1})`, and specifically `μ_m` with `m = δ_e+1 ∈ {16, 17, 30}` | **nothing.** No table, figure or remark in either source examines two or more blocks jointly (`proof_search_log.md` §3, §5.4, §6, §6.5) | **no** |

**That is the finding.** The gap is not logical — A5 implies A17 — it is that
the evidence marshalled for A5 measures two functionals (a global scalar, and a
single block) and A17 consumes a third (an `n_e`-fold joint moment) that neither
measurement constrains beyond its first moment.

The structural tell `docs/inventor-protocol.md` §3 asks for is present: RMRS's
own hedge on the one piece of block-level evidence — *"a **small proportion** of
HQC bits do behave as i.i.d Bernoulli variables"* — **names its own scope, and
A17's use lies outside it**. The source is more careful about its evidence than
the downstream use of that evidence is.

---

## 6. Is A17 the right target? Competing items in the same trace

The handoff asks for willingness to conclude it is not, and to name a better one.
My answer: **A17 is a defensible target and is not the best-value one, and the
object worth targeting is sharper than "A17" as stated.**

### 6.1 A19 / R-p — cheaper, larger, and settled by reading

Theorem 6.1's own sentence says `p_i` is Prop **6.1.3**; the only place SPEC
gives a numeric `p_i` is Table 11, whose header says Prop **6.1.4**. Computing
Theorem 6.1 both ways at the published parameters
(`proof_search_log.md` §7, exact arithmetic):

| set | Thm 6.1 with `p_i` from 6.1.4 | with `p_i` from 6.1.3 | **gap** |
|---|---|---|---|
| HQC-1 | 2⁻¹³²·⁸⁹ | 2⁻¹²²·²⁸ | **10.61 bits** |
| HQC-3 | 2⁻¹⁹³·⁸⁶ | 2⁻¹⁸⁵·⁹⁰ | **7.96 bits** |
| HQC-5 | 2⁻²⁶⁰·⁶⁰ | 2⁻²⁴³·⁸¹ | **16.79 bits** |

**16.8 bits at NIST-5 for a cross-reference**, versus a dependence-induced
movement that requires an unmeasured joint moment to even sign. A19 is settled by
*reading the source and the reference implementation*, needs no measurement, and
is larger than the built-in conservatism budget (§6.3). It is not glamorous and
it is the better first move. It is also the one item this program can close
without any new capability.

### 6.2 A20 / X9 — the more fundamental formal gap

SPEC §6.2.2 declares decryption failure occurs *"if and only if"*
`ω(x·r₂ − r₁·y + e) > ∆` with `∆ = ⌊(d−1)/2⌋` — a **bounded-distance** condition
on the concatenated code — while §6.1 computes the failure probability of the
**two-stage ML-then-algebraic** decoder. These are different events, related by
containment in **neither** direction in general: the two-stage decoder can fail
on error vectors of weight `≤ ∆` (an unlucky per-block distribution), and can
succeed on error vectors of weight `> ∆` (weight concentrated inside `≤ δ_e`
blocks). If the *"if and only if"* is read literally, δ-correctness is asserted
for one event while the number substituted for δ is computed for another.

This is BATCH-001's X9 and the red team's second-ranked lead. It bears on
`RQ-HQC-001.scope.targets[1]` directly. **It is a textual/formal question, and it
is arguably prior to A17**, because it decides *which* probability Theorem 6.1
is supposed to be bounding. Not resolved here — outside this task's objective.

### 6.3 The slack budget, which any A17 result must clear

SPEC Table 11 measures the inner bound's own conservatism: `p_i` exceeds the
observed inner DFR by **0.17 / 0.25 / 0.18** bits per block. Over `m = δ_e+1`
blocks that is **2.72 / 4.25 / 5.40 bits** of built-in headroom in the stage-3
number (`proof_search_log.md` §7; the observed values are the sources' own).

Therefore **a dependence-induced amplification must exceed 2².⁷² / 2⁴.²⁵ / 2⁵.⁴⁰
before Theorem 6.1's number stops being an upper bound on the model-space
truth.** At the first-order sensitivity of `a17_sensitivity.yaml`, that
corresponds to inter-block failure correlations of `2.6×10⁻⁵ / 7.4×10⁻⁶ /
3.7×10⁻⁵` — still very small numbers, but they are the bar, and any future
statement about A17 that does not clear this bar has not moved the published
claim. **Stating this bar is part of not overclaiming the lead.**

### 6.4 Recommendation to the Coordinator

Not a decision — the Coordinator alone decides.

1. **Retarget from "A17" to `μ_{δ_e+1}`**, the `(δ_e+1)`-way inner-block
   co-failure probability, stated on space (T). That is the quantity Theorem 6.1
   is sensitive to, it is well defined, and it is not confounded with A5.
2. **Resolve A19 first.** Larger, cheaper, needs no measurement, and it changes
   which `p_i` any later work must use.
3. **Carry X9/A20 as a separate formal item**, since it decides what Theorem 6.1
   is bounding.
4. If A17 is pursued, pursue it as an **evidential** question about a joint
   moment, not as a logical question about independence — the logical question
   is already answered (A5 ⟹ A17) and pursuing it would rediscover A5.

---

## 7. Forward guidance: proof routes that would discharge A17 without measurement

`docs/inventor-protocol.md` §4 requires a negative to name what remains open.
These are **proof routes**, offered as open directions. None is an experiment
design, none is claimed to succeed, and this document does not assert any of
them holds.

> **Lemma L2 (proved here; the hinge for route (a)).** For a binary linear code
> `C` with minimum-distance decoding, the event bounded by Props 6.1.3/6.1.4 —
> *"some non-zero codeword is at least as close to the received word as the
> transmitted one"* — is an **increasing** event in `supp(e)`.
>
> *Proof.* The event is `{∃ c ≠ 0 : |e ⊕ c| ≤ |e|}`. Since
> `|e ⊕ c| = |e| + |c| − 2|e ∧ c|`, it equals `{g(e) ≤ 0}` with
> `g(e) = min_{c≠0} (|c| − 2|e ∧ c|)`. Adding a coordinate `i` to `supp(e)`
> increases `|e ∧ c|` by 1 when `i ∈ supp(c)` and leaves it unchanged otherwise,
> so every term `|c| − 2|e ∧ c|` is non-increasing, hence `g` is non-increasing
> and `{g ≤ 0}` is upward-closed. ∎

- **(a) Negative association.** If the coordinates of `ẽ` on space (T) are
  negatively associated (Joag-Dev–Proschan), then by Lemma L2 the `F_j` are
  increasing functions of **disjoint** coordinate blocks, hence negatively
  associated, hence `μ_k ≤ q^k` — which is exactly R3, and Theorem 6.1 survives
  to leading order in the **conservative** direction. **Neither source proves
  negative association of `ẽ`'s coordinates, and this program does not claim
  it.** Proving it would discharge A17 in the safe direction by argument alone.
  Known obstruction: `ẽ` is a *product* in a cyclic ring plus a fixed-weight
  vector, and negative association is not preserved by such products in general,
  so this is a real theorem to prove, not a formality.
- **(b) Fixed-weight conditioning.** A weaker, possibly easier route: show that
  conditioning on `ω(e′)` induces the sampling-without-replacement structure,
  for which negative association *is* classical, and then control the mixture
  over `ω(e′)` — noting that the mixture works in the **opposite** direction
  (`a17_sensitivity.yaml` derivation step 4) so the two must be compared
  quantitatively, not merely named.
- **(c) A union bound over blocks.** Replace independence with a crude union
  bound over the `C(n_e, m)` failing block sets. This needs only `μ_m`, not
  independence, and it is where any partial result would attach.
- **(d) External literature.** A general theorem on concatenated-code error
  probability under a *memoryless* inner channel would be unsurprising to exist
  and would apply verbatim on space (M) — but the open question is on space (T),
  where the channel is **not** memoryless, so such a theorem would relocate the
  gap rather than close it. Recorded as a route with its own ceiling already
  visible.

---

## 8. Scope limits

- **Two documents, two hashes.** Everything above is about SPEC `174186cb…` and
  RMRS `cbb7dbd6…`. `proof_search_log.md` §8 lists by name what the search does
  **not** cover (the reference implementation, the NIST submission archives,
  earlier specification revisions, `[1]` Aguilar-Melchor et al. 2018, and the
  general concatenated-coding literature).
- **No measurement of HQC was performed.** No decoding trial, no simulation, no
  sampling, no seed. Every number is either transcribed from a published table,
  recomputed by exact arithmetic from a published formula at published
  parameters, or derived under a model that is named where it is used.
- **No experiment is designed here**, and the absence is deliberate:
  `RQ-HQC-001.constraints[0]`.
- **No security claim about HQC in either direction.** In particular: nothing
  above asserts that HQC's published DFR is wrong, optimistic, or unsafe.
  `a17_sensitivity.yaml` records the direction question as **undetermined**.
- **Claim tier: toy.** `proof_status`: this document's own results — Lemma L1,
  Lemma L2, the trace in §4, and the null check in §5 — are `derivation`
  (checkable arguments), never `certificate`. `certificate.kind: none`.
- **Not admissible toward an `AGENTS.md` rule 13 closure quorum.**
- **I made no status transition**, edited no ledger record, no knowledge entry,
  no queue, and no sibling task artifact. My only writes are the three files in
  this task's directory.
