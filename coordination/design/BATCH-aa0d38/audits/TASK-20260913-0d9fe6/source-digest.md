# Source digest: Fouvry–Kowalski–Michel–Sawin, "Bilinear forms with trace functions" (arXiv:2511.09459v1)

Prepared for TASK-20260913-0d9fe6 (idea-generator role, research/reporting only).
Feeds the follow-on executor task that will fill EXP-CRYPTO-6505c6's 160-cell
obligation matrix and 400-cell chart-coverage matrix. **This document is not
itself an audit artifact and certifies nothing.**

## 0. How to read this document

- Text inside `> "..."` blocks, tagged **[QUOTE, §X]**, is reported as the
  paper's own words, extracted via repeated `WebFetch` calls against
  `https://arxiv.org/html/2511.09459v1`. Every such call routes the raw page
  through a small summarizing model before I see the answer — I have **no
  direct rendered or raw-HTML view of the paper myself**. Treat every quote
  as "LLM-mediated transcription of the source," not as a hand-verified
  photograph of the text. Where two independent fetches reproduced the same
  wording I say so (higher confidence); where I could get only one pass, or
  a wording looked suspicious, I flag it explicitly (§7).
- Text tagged **[INFERENCE]** is my own reasoning connecting the paper's
  content to `specification.yaml`'s objects. It is not in the paper and must
  not be copied into a certificate as if it were a citation.
- Text tagged **[NOT FOUND]** or **[OUT OF SCOPE]** records a deliberate
  negative check (searched for, not present, or not addressed by this
  source), which is itself load-bearing information for the audit.

## 1. Paper structure (outline)

**[QUOTE-derived outline, from repeated fetches, consistent across passes]**

1. Introduction
   - 1.1 Bilinear sums of trace functions
   - 1.2 General statements
   - 1.3 An exceptional case
   - 1.4 Cubic toroidal moments
   - 1.5 Outline of the paper
2. Algebro-geometric preliminaries
3. Around Goursat's Lemma
   - 3.1 Goursat's Lemma
   - 3.2 A criterion for vanishing of coinvariants
   - 3.3 The orthogonal case
   - 3.4 A property of gallant sheaves
   - 3.5 The case of oxozonic sheaves
   - 3.6 Diagonal estimates
4. General estimates for bilinear forms
   - 4.1 Reduction to complete sums
   - 4.2 Proof of Proposition [unnumbered subsection title as retrieved]
   - 4.3 Reduction to a stratification statement
5. Moment estimates for gallant sheaves
6. Stratification for gallant sheaves and conclusion of the proof
7. Bounds for trilinear sums with monomial arguments
8. The oxozonic case
9. Ubiquity of gallant sheaves
   - 9.1 Bountiful sheaves
   - 9.2 Birationality
   - 9.3 Forms of exponential sums
   - 9.4 Change of variable
   - 9.5 Tannakian operations
   - 9.6 Hypergeometric sheaves
   - 9.7 Hypergeometric sheaves with finite monodromy
   - 9.8 Other examples with finite monodromy
   - 9.9 Further examples
   - 9.10 The rank one case

**[NOT FOUND / gap]**: I could not get the actual content of Sections 5 and 6
through `WebFetch` — two separate targeted attempts returned "content not
present in the retrieved excerpt" from the tool's own summarizing pass. This
is a real, disclosed gap, not a negative finding about the paper: Sections 5–6
are exactly where the paper (a) proves the moment estimate for gallant
sheaves that feeds Theorem 2.4's hypothesis, and (b) shows how Theorem 2.4 is
applied to conclude Theorem 1.1. See §7 and §8.

## 2. The four sheaf families named in specification.yaml

### 2.1 Family K ("Quadratic Kummer sheaf")

`specification.yaml.families.K.definition`: *"Quadratic Kummer sheaf L_chi on
Gm, extended by zero at 0 and infinity; compatible quadratic norm characters
over finite extensions."*

**What the paper actually contains:**

- **[QUOTE, §2, final paragraph before §3]**: *"For a finite field k, an
  ℓ-adic additive character ψ of k or an ℓ-adic multiplicative character χ,
  we use the usual notation L_ψ or L_χ for the associated Artin–Schreier or
  Kummer sheaf, with trace functions x ↦ ψ(x) or x ↦ χ(x)."*
- This is the **only** appearance of "Kummer sheaf" I could find. It is
  introduced purely as **standard notation**, with **no construction given**
  (no Lang-torsor/Artin–Schreier covering description, no statement of rank,
  ramification, purity, or extension-by-zero convention). Confirmed by a
  dedicated negative search **[QUOTE-search result]**: *"The term 'Kummer
  sheaf' does not appear [elsewhere]... the paper does mention multiplicative
  characters and associated sheaves"* only via this one sentence.
- **[NOT FOUND]**: the phrase "quadratic character" does not appear anywhere
  in the paper (dedicated search, negative). So the paper never specializes
  χ to the quadratic character, never states L_χ's rank (it is classically
  1), purity, or its zero-extension convention at 0, ∞.
- **[INFERENCE]**: `L_χ` for χ quadratic is exactly the paper's generic
  `L_χ` notation with a specific classical χ substituted in. The paper
  explicitly treats `L_χ` as a background/classical object it borrows
  notation for, not something it defines or whose properties (rank 1,
  purity weight 0, ramification only at {0,∞}, quadratic-norm-compatibility
  under base change) it proves or even states. **Verdict: family K is a
  classical object the paper takes as given background; its
  definition/rank/purity/trace-normalization/zero-extension facts must come
  from a different, more foundational source (e.g. Katz's standard Kummer
  sheaf references) or an independent derivation — not from this paper.**

### 2.2 Family L ("Legendre R¹")

`specification.yaml.families.L.definition`: *"R¹ of the Legendre family
v²=z(z-1)(z-u) over u≠0,1,∞, normalized by a compatible unramified Weil
twist."*

**What the paper actually contains:**

- **[NOT FOUND]**, confirmed by a dedicated negative search:
  *"The term 'Legendre' does not appear in this paper, nor is the Legendre
  family of elliptic curves mentioned."* I ran this as an explicit
  yes/no search (not embedded in a broader question) to reduce the risk of
  the summarizing model inventing a plausible-sounding but false answer.
- **Verdict: Family L is entirely absent from this paper — not defined, not
  named, not used as an example anywhere I could find (including the
  worked-example catalogue of §9.1–9.10, which lists hypergeometric sheaves,
  "bountiful" sheaves, birational/change-of-variable/Tannakian constructions,
  and finite-monodromy hypergeometric examples, but no elliptic-fibration
  R¹π_* example by name).** Whatever generic theorems the paper offers
  (Theorem 2.4's abstract moment-to-stratification lemma, or Theorem 1.1/1.3
  if `L` can be shown to be "gallant") could in principle still apply to `L`
  if its hypotheses are independently verified for `L` (rank 2, monodromy
  SL₂ up to the standard classical facts about the Legendre family), but the
  paper does not do this verification and does not mention the object at
  all. This is a full independent-derivation obligation, not a
  paper-supplied fact.

### 2.3 Families C1, C2 (constant-sheaf controls)

`specification.yaml.families.C1/C2`: constant rank-1 / constant rank-2
direct-sum sheaves on P¹, "negative cancellation control."

**[NOT FOUND / OUT OF SCOPE]**: constant sheaves are not discussed in the
paper as objects of study (they would trivially fail the paper's own
irreducibility requirement — see Definition 1.2 quoted in §4 below, which
requires the geometric monodromy group's action on the underlying
representation to be **irreducible**; a nonzero constant sheaf's monodromy
representation is trivial, hence not irreducible unless rank 1 trivial is
considered "irreducible" degenerately, and in any case has trivial, not
simple-or-quasisimple, image). **[INFERENCE]**: this is exactly why C1/C2
are useful known-false controls for the audit — they are named precisely
because they sit **outside** the class of objects ("gallant," per Definition
1.2) for which the paper's cancellation machinery (Theorem 1.1, 1.3, 1.4)
could possibly apply, so any correlation argument that fails to reject them
is provably using an insufficient hypothesis. The paper itself states no
opinion about constant sheaves; this reasoning is mine, built from
Definition 1.2's irreducibility clause, not a paper claim.

**Summary table for §2:**

| Family | Paper defines it? | Paper's own content |
|---|---|---|
| K (quadratic Kummer) | No — only generic `L_χ` notation, no properties stated | §2, one sentence |
| L (Legendre R¹) | No — term does not appear at all | absent |
| C1 (constant rank 1) | No — not discussed | absent (relevant only via Def. 1.2's irreducibility requirement, which is my inference) |
| C2 (constant rank 2, direct sum) | No — not discussed | absent, same reasoning |

## 3. Theorem 2.4: full statement, hypotheses, and my effectiveness finding

### 3.1 Location and exact hypothesis

**[QUOTE, §2, Theorem 2.4]** (reconstructed from two independent fetch
passes that agreed on wording; math symbols as rendered by the tool, cleaned
of stray LaTeX macro noise):

> "Let k be a finite field and ℓ a prime number different from the
> characteristic of k. Let X be a quasiprojective variety with a locally
> closed embedding in **P**^d_k for some integer d ⩾ 0. Let M be an object of
> D^b_c(X, **Q̄**_ℓ) which is mixed of *integral* weights.
>
> Assume that there exists a positive integer m, a real number A and a real
> number B ⩾ 1 such that
>
> ∑_{x∈X(k_n)} |t_M(x,k_n)|^{2m} ⩽ B·|k_n|^A
>
> for all integers n ⩾ 1."

Then (conclusion, four numbered parts, quoted separately below in §3.2).

**Hypotheses required, enumerated explicitly:**

1. `k` a finite field, `ℓ` a prime ≠ char(k).
2. `X` quasiprojective, with a **fixed, a priori** locally closed embedding
   into **P**^d_k for some integer `d ⩾ 0` — this embedding and its `d` are
   fixed **before** the quantifier over `n` in the moment hypothesis below,
   which matches `specification.yaml`'s own quantifier-order requirement
   ("fix sheaf/normalization and n-independent complexity data before
   requiring the target for every n≥1").
3. `M ∈ D^b_c(X, Q̄_ℓ)` — an object of the bounded derived category of
   constructible ℓ-adic sheaves on `X`, **[QUOTE]** "mixed of *integral*
   weights" (i.e. all weights appearing lie in **Z**, not just **Q**).
4. Existence of `m` (positive integer), `A` (real), `B ⩾ 1` (real) such that
   the `2m`-th moment of `t_M` over all `k_n`-points, for **every** `n ⩾ 1`,
   is bounded by `B·|k_n|^A`. This is exactly the shape of
   `specification.yaml.main_transfer_target.moment` (`m: 2, A: 5` there),
   confirming the specification's obligation is stated in the same
   parametrization as the paper's own hypothesis — **[INFERENCE]**: the
   specification is asking the audit to *supply* this hypothesis for the
   specific correlation complex `M` it builds (not asking Theorem 2.4 to
   prove it; Theorem 2.4 *assumes* it).

**[NOT FOUND]** — I searched explicitly and found **no additional stated
restriction** on `n`, on the size of `q = |k|`, or on finite-vs-infinite
monodromy attached to Theorem 2.4 itself. Theorem 2.4 is a fully general,
monodromy-agnostic statement about any mixed-integral-weight complex
satisfying the moment hypothesis; it does not mention "gallant," "light," or
any monodromy-group condition at all. (Those enter only through Definition
1.2 and the later theorems 1.1/1.3/1.4/1.6 that *use* Theorem 2.4 as a tool —
see §4.)

### 3.2 The four conclusions, quoted

**[QUOTE, §2, Theorem 2.4 conclusion]**, from a fetch pass targeted
specifically at reproducing this list verbatim:

> "(1) We have X^(w) ⊂ X^(w−1) for all w."
>
> "(2) We have dim X^(w) ⩽ ⌊A⌋ − m·w for all w."
>
> "(3) Each X^(w) is a union of subvarieties of total degree bounded only in
> terms of n and c(M)."
>
> "(4) For all n ⩾ 1 and x ∈ (X∖X^(w+1))(k_n), we have t_M(x,k_n) ≪ |k_n|^{w/2},
> where the implicit constant depends only on d and c(M)."

`X^(w)` itself is **[QUOTE, definition located inside the proof of Theorem
2.4, not a separate numbered definition preceding it]**: *"We then define
X^(w), for w ∈ Z, to be the union over i of the connected components of
dimension ⩽ A − m·w of [a family of subschemes Y_i built in the proof]."*
I could not get a fully clean rendering of the `Y_i`/`Y_{i-1}` construction
itself (§7); the stratification `X^(w)` is a decreasing (by conclusion (1))
family of closed subvarieties defined purely from the numerical data
`(A, m, d, c(M))`, not from an independently-chosen "exceptional locus."

**Flag — possible transcription defect in conclusion (3):** two independent
fetches both rendered conclusion (3) with the word **"n"** ("bounded only in
terms of **n** and c(M)"), not "d". I explicitly asked the tool to
double-check this against a possible misreading of "d" and it held to "n"
both times, while itself noting the inconsistency looks suspicious ("this
appears inconsistent... this seems like a potential typo in the paper
itself — the bound should logically depend on d, not an undefined n in this
context" — its own hedge, not mine). I did **not** get an independent visual
inspection of the source HTML/MathML myself (I have no such tool), so I
cannot resolve whether the paper's actual glyph is "n" or "d" here, whether
"n" is even meant as a bound on the extension degree (which would be a very
different and stronger/stranger claim — degree bounded uniformly in the
extension index rather than in the fixed ambient dimension), or whether this
is purely an artifact of the LLM-mediated extraction. **This must be
resolved by a human or tool with direct access to the actual arXiv HTML/PDF
before any O04/O08 cell that depends on conclusion (3)'s exact dependency
set is marked CERTIFIED** — do not silently pick "d" because it looks more
sensible; that would be inventing text.

### 3.3 Effectiveness — my own independent finding

**Prior finding to check (per handoff)**: TASK-20260913-4e7c6d's
`coordinator_correction_20260913` reports that a prior idea-generator pass
found Theorem 2.4 stated *ineffectively*, quoting Remark 1.2's "not
polynomial... due to the use of qualitative results in Quantitative Sheaf
Theory" and Theorem 2.4's own "implicit constant depends only on d and
c(M)" with no explicit formula anywhere.

**My independent re-read, this session:**

- **[QUOTE, §1.2, Remark 1.2, immediately after Theorem 1.1]**, reproduced
  consistently across two separate fetches with matching wording: *"Our
  method is in one respect less efficient than that of [Pisa]: whereas the
  latter provides estimates where the dependency on the complexity (when it
  applies) is polynomial, this is not the case in this paper, due to the use
  of qualitative results in Quantitative Sheaf Theory."*
- **[QUOTE, §2, Theorem 2.4(4)]** (§3.2 above): *"...where the implicit
  constant depends only on d and c(M)"* — a dependency statement with **no
  accompanying explicit formula, numeric bound, or algorithm** anywhere in
  what I could retrieve of the paper for computing that constant from `d`
  and `c(M)`.
- **[QUOTE, §2, on c(M)]**: *"Sawin defined the complexity c_u(M) of objects
  of D^b_c(X, Q̄_ℓ) (see [qst, Def. 6.3]). This is a non-negative integer
  which controls quantitatively most invariants of M."* — c(M) is itself
  cited to an external reference ("qst" = Sawin's Quantitative Sheaf Theory)
  for its definition; the paper does not reprove or re-derive an explicit
  numeric recipe for it in-line, consistent with Remark 1.2's framing that
  the paper's own contribution leans on *qualitative* results from that
  external theory.

**My conclusion: I land in the same place as the prior finding.** Theorem
2.4's bound is stated with a dependency on `(d, c(M))` but **without an
explicit formula for the implicit constant**, and Remark 1.2 explicitly
disclaims polynomial (or any other concretely effective) dependency for
*this* paper's method, in contrast to a cited prior work ("[Pisa]") that the
authors say does achieve polynomial dependency. I did not find, anywhere in
the sections I could retrieve, an explicit numeric formula, algorithm, or
computable bound discharging Theorem 2.4's implicit constant in terms of
`d` and `c(M)`. **I therefore corroborate, independently, that Theorem 2.4
as stated in this paper is ineffective for the purposes of
`specification.yaml`'s `main_transfer_target.effective_B` obligation** (which
explicitly requires "an explicit computable uniform function/formula" and
states that "ineffective existence does not discharge this target").

**Caveat on my own corroboration**: this is still an LLM-mediated read of
the paper (§0), not a from-source, symbol-by-symbol verification by a human
or a tool with direct text access. Two independent people/sessions now
report the same conclusion using overlapping but not identical quote sets,
which raises confidence, but neither constitutes a citation-grade primary
verification. I did **not** locate and read the cited external reference
"[Pisa]" (uncited in full by title/author in what I retrieved — likely a
short-form citation key, not the paper's own claim, so I cannot state what
"[Pisa]" actually proves; I only report that this paper says it achieves
polynomial dependency where this paper does not).

## 4. Exclusions and degenerate cases around Theorem 2.4 / gallant framework

### 4.1 Definition of "gallant" (Definition 1.2)

**[QUOTE, §1.2, Definition 1.2]**, on the core structural requirement:

> "The action of G on E^r is irreducible and moreover one of the following:
> (1) the identity component G⁰ is a simple algebraic group; (2) the group G
> is finite and contains a quasisimple normal subgroup N acting irreducibly."

And, on the additional condition for **gallant and light**:

> "We say that F is *gallant and light* if F is gallant and moreover is
> mixed of *integral* weights ⩽ 0 and its restriction to some open dense
> subset is pure of weight 0."

So "gallant" itself already **includes both regimes** — infinite monodromy
with simple identity component (1), *and* finite quasisimple monodromy (2) —
inside one definition; there is no separate infinite-vs-finite split stated
as an *exclusion* near Theorem 2.4 (Theorem 2.4 doesn't reference "gallant"
at all, per §3.1). The finite/infinite split instead appears as a proof-
technique bifurcation in Section 3.4: **[QUOTE, §3.4]**: *"We will
distinguish the cases where G is finite or infinite. The former is
significantly more involved"* — i.e., inside the *proof* of a property of
gallant sheaves, not as a hypothesis restriction on the main theorems
themselves.

### 4.2 The SO4 / "sulfatic" exceptional case

This is the "gallant/SO4" exceptional case the handoff asks about, under
**Section 1.3, "An exceptional case"**.

**[QUOTE, §1.3]**, verified by a dedicated confirmatory search that returned
matching wording twice:

> "We will say that F is *sulfatic* if the geometric monodromy group of F is
> isomorphic to **SO**₄ [and] *oxozonic* if it is isomorphic to **O**₄ and
> has the property that the subgroup **SO**₄ acts [irreducibly / with a
> stated additional property that I could not fully reproduce verbatim —
> see gap note below]."

**[QUOTE, §1.3]**, on why this is exceptional:

> "A sheaf F with geometric monodromy group isomorphic to either **O**₄ or
> **SO**₄ will not be gallant because the algebraic group **SO**₄ is not
> simple."

**[INFERENCE]**: **SO**₄ ≅ (SL₂ × SL₂)/μ₂ is a classical isomorphism (not
something I have a paper quote for in this pass) — it has simple *factors*
but is not itself a simple algebraic group, hence violates Definition 1.2(1)
directly. This is presumably *why* the paper needs a dedicated named
exception ("sulfatic"/"oxozonic") and a separate treatment: **Section 3.5
("The case of oxozonic sheaves")** and **Section 8 ("The oxozonic case")**
exist specifically to handle this excluded case with separate arguments
rather than folding it into the main gallant machinery.

**Range restriction found for this exceptional case:**

**[QUOTE, from a fetch targeting Theorem 1.6]**: *"Assume that
K_{a,b,εc} is either gallant or oxozonic... Theorem 1.3 holds for F if c is
odd."* — i.e. the paper does have a named theorem (rendered to me as
"Theorem 1.6," **unverified against a second independent fetch — see gap
note in §7**) extending the main bilinear-sum conclusion to the oxozonic case
under an explicit parity condition ("c odd"). I was not able to independently
re-confirm the "Theorem 1.6" numbering or get its full exact statement in a
second pass; treat the theorem number as tentative and the "c odd" condition
as the one piece I'm more confident about, since it appeared as a specific,
unusual, checkable detail rather than boilerplate.

**[INFERENCE, flagged clearly as speculative connection, not a paper
claim]**: this SO4/sulfatic exceptional case is structurally the kind of
thing that could become relevant to `specification.yaml`'s family **L**
(Legendre, rank 2) if the audit's correlation construction ever produces a
tensor or fiber product of *two* independent rank-2 objects whose combined
monodromy sits inside O₄ or SO₄ (e.g., two copies of an SL₂-monodromy sheaf
combined via the shared-locus/coinvariant analysis specification.yaml's O05
calls for). **This is my own speculative structural observation for the
audit team to check, not a fact the paper states about elliptic curves or
about family L** — the paper never mentions Legendre sheaves, and I have no
paper-level argument that the specific correlation complex the specification
builds actually lands in this exceptional case. It is flagged here only so
the audit does not have to discover the SO4 possibility from a blank start
when it reaches O05/O08 for family L.

### 4.3 No stated range restriction on Theorem 2.4 itself

As already noted in §3.1: Theorem 2.4 carries no `q ⩾ q_0`, no `n` upper
bound, and no monodromy-finiteness condition. The finite/infinite split and
the SO4 exclusion are conditions on **which sheaves the paper's main
bilinear-sum theorems (1.1, 1.3, 1.4, 1.6) apply to**, not conditions
attached to the abstract moment-to-stratification lemma (Theorem 2.4) that
`specification.yaml`'s `stratification` obligation explicitly invokes by
name.

## 5. Other background machinery in the paper relevant to the audit (not requested by name, but load-bearing)

**[INFERENCE-framed pointer, with quotes where I have them]**:

- **Duality/conjugate-trace convention (relevant to O03's "dagger/dual"
  obligation)**: the paper's own notation is `F^∨` (Verdier-style dual), not
  a dagger symbol. **[QUOTE, §2]**: *"The dual of F is defined to be the
  sheaf F^∨ = Hom̄(F, Q̄_ℓ); it is lisse on U and coincides there with the
  lisse sheaf associated to the contragredient of the representation
  corresponding to F. In particular, if F is pure of weight 0 on U, then the
  trace function of F^∨ on U is (under ι) the complex conjugate of the trace
  function of F."* Note the **purity-of-weight-0 hypothesis** attached to
  this conjugate-trace fact — `specification.yaml`'s `F^dagger` must
  therefore either establish that whichever sheaf is used is pure of weight
  0 on the relevant open set, or find a different source for the
  conjugate-trace identification when it is not.
- **Zero-extension convention (relevant to O01/O02's boundary
  obligations)**: **[QUOTE, §2]**: *"...the arithmetic (resp. geometric)
  monodromy group of F coincides with that of the sheaf j_!j*F. This allows
  us to assume in many proofs that F is the extension by zero of a lisse
  sheaf on some dense open subset of X."* — confirms the paper does use
  `j_!` (zero-extension) as a standing convention, matching
  `specification.yaml`'s `candidate_complex`'s use of `j_!F`, but only as a
  general working assumption for its own proofs, not as a definition
  transferable automatically to the elliptic-addition setting.
- **Middle-extension sheaf, defined [QUOTE, §2]**: *"A middle-extension
  sheaf is an ℓ-adic sheaf F on X such that for some (equivalently, for any)
  open dense subset U ⊂ X with open immersion j: U → X, the natural
  adjunction morphism F → j_*j*F is an isomorphism."* "Lisse" and "pure of
  weight w" are used in §2 but **[NOT FOUND]** — not formally (re)defined
  there; the paper assumes these as known from prior literature (Deligne,
  Katz-style conventions), consistent with the general pattern that §2 is a
  preliminaries section citing/recalling rather than re-deriving foundations.
- **Goursat's Lemma machinery (Section 3, esp. 3.1–3.2, directly relevant to
  O05's "geometric constituents/coinvariants, diagonal and residual shared
  loci")**: the section titles alone — "Goursat's Lemma," "A criterion for
  vanishing of coinvariants," "The orthogonal case," "A property of gallant
  sheaves" — describe exactly the kind of tool (classifying subgroups of a
  product of two monodromy groups, and when the resulting representation has
  no invariants/coinvariants) that a shared-constituent analysis of two
  independently pulled-back sheaves (as `specification.yaml`'s O05 requires
  for `E_Q × E_R`) would need to invoke. **I was not able to retrieve the
  actual statements of 3.1/3.2 verbatim in this pass** (see §7); I only have
  the section titles and the general framing from the outline fetch. This is
  a concrete, named gap for the follow-on to close by a further targeted
  fetch or a direct read, not something I can respond to from a title alone.
- **Complexity `c(M)` is intrinsic to the complex, not a free external
  parameter [INFERENCE from a direct quote]**: **[QUOTE, from the Section
  4.3 targeted fetch]**: *"The paper does not specify an a priori fixed
  degree/complexity bound C before quantifying over n. Instead, Theorem 2.4
  states that the stratification X^(w) involves subvarieties 'of total
  degree bounded only in terms of n [see the n/d flag in §3.2] and c(M)',
  where c(M) is the complexity of the complex M itself. Complexity is thus
  an output of the algebraic object, not a pre-fixed external parameter."*
  (This particular passage is itself already the tool's paraphrase rather
  than a paper quote — flagged as **[INFERENCE, tool-paraphrased]**, not a
  direct quote, even though it reports back on quoted material; I include it
  because it correctly identifies an important consequence for
  `specification.yaml`'s `main_transfer_target.complexity_C`: `C` there must
  be defined as (a bound on) the `c(M)` of the specific correlation complex
  the audit constructs, not chosen freely in advance of that construction.

## 6. Obligation columns O01–O10: explicit in-scope / out-of-scope calls for this source

For each column, "in scope" means the paper states content directly usable
as a citation; "partial" means the paper gives generic/background material
relevant to the column but not the specific elliptic-addition instance;
"out of scope" means the paper says nothing bearing on the column at all for
this target.

- **O01** (exact family/base/domain, extension compatibility, normalization,
  source obligations) — **partial**. The paper gives generic conventions
  (mixed integral weights, `j_!` zero-extension, middle-extension, purity/
  duality with conjugate trace under purity) applicable to *any* sheaf, and
  states `L_χ`/Kummer as bare notation (§2.1). It supplies **no** family-
  specific facts for K or L (rank, ramification locus, purity weight,
  boundary trace value) and **no** facts about C1/C2 at all. A different
  source (or an independent derivation) is required for the family-specific
  content; the paper supplies only the generic conventions layer.
- **O02** (25 ordered chart-pair compatibility/emptiness, global map
  coverage, zero-boundary certificates) — **out of scope**. Nothing in the
  paper concerns elliptic-curve addition-law charts; this is pure
  elliptic-curve/algebraic-geometry bookkeeping external to this source.
- **O03** (correlation-to-pushforward trace, dagger/dual, integral-weight
  conventions) — **partial**. The paper gives the general duality/
  conjugate-trace fact (§5 above, with its purity-of-weight-0 caveat) and
  the mixed-integral-weights convention used throughout, both directly
  reusable as generic citations. It does **not** state a trace formula for
  the specific correlation sum `S_F,n(Q,R)` or verify the "dagger" identity
  for the specific `F^dagger` the specification constructs — that
  identification is an independent obligation.
- **O04** (rank/Artin/Swan/embedded-derived complexity, operation costs,
  n-independent uniform bounds) — **partial, and see the effectiveness
  finding in §3.3**. The paper's whole apparatus is built around a
  complexity invariant `c(M)` (cited to Sawin's Quantitative Sheaf Theory)
  that is explicitly claimed to "control quantitatively most invariants of
  M," but its dependence in the paper's own applications is **qualitative,
  not effective** (Remark 1.2). I could not retrieve Sections 5–6, where the
  paper's own operation-cost bookkeeping (for gallant sheaves specifically)
  would live (§1, §7 gap). Do not treat "the paper has a complexity theory"
  as equivalent to "the paper supplies computable Artin/Swan-conductor-level
  operation-cost formulas" — I found no such explicit formula anywhere I
  could retrieve.
- **O05** (geometric constituents/coinvariants, diagonal and residual shared
  loci) — **partial, promising but unretrieved in detail**. Section 3
  ("Around Goursat's Lemma," "A criterion for vanishing of coinvariants,"
  "The orthogonal case") is titled exactly on-point for this obligation's
  subject matter, but I was unable to retrieve the actual statements in this
  pass (§7 gap) beyond the SO4/sulfatic exceptional-case material in §4.2.
  This is the single most promising unexploited lead in the paper for O05
  and should be the first thing a follow-on fetch pass targets.
- **O06** (all-extension fourth-moment statement and effective B(C), or
  exact counterexample/open obligation) — **in scope for the *shape* of the
  obligation, ineffective for the *content***. Theorem 2.4 states exactly
  this kind of hypothesis (moment bound ⇒ stratification) in the abstract,
  but (a) it takes the moment bound as a **hypothesis to be supplied**, not
  something it proves for an arbitrary complex — the paper's own moment
  *proof* for gallant sheaves is in the unretrieved Section 5 — and (b) per
  §3.3, the resulting implicit constant is **ineffective** as stated. Per
  `specification.yaml`'s own text ("ineffective existence does not discharge
  this target"), **O06 cannot be marked CERTIFIED from this paper alone**;
  at best it can be marked OPEN with the specific missing prerequisite named
  (an explicit formula for the Theorem 2.4 implicit constant in terms of
  `d, c(M)`, and — separately — a proof, not just a hypothesis, of the
  moment bound for the specific elliptic-addition correlation complex).
- **O07** (source theorem hypothesis-by-hypothesis match; no unproved
  monomial-to-addition identification) — **in scope as a checklist source,
  not as a completed match**. §3.1 above gives the exact, complete,
  enumerable hypothesis list Theorem 2.4 requires; the paper does not itself
  attempt or claim any elliptic-addition identification (it never mentions
  elliptic curves), so the actual match-checking is entirely the audit's own
  work using this paper only as the target checklist.
- **O08** (exceptional dimension/degree, off-locus residual correlation,
  effective constants, exact scope) — **partial, ineffective**. Theorem
  2.4's conclusions (2)–(4) are exactly this obligation's content in the
  abstract (dimension bound `⌊A⌋ − mw`, degree bound "in terms of [n or d
  flagged in §3.2] and c(M)," pointwise bound with implicit constant
  depending on `d, c(M)`), but the same ineffectiveness finding (§3.3)
  applies: no explicit numeric bound is given anywhere I could retrieve.
  The SO4/sulfatic exceptional-case material (§4.2) is also relevant here
  if the audit's shared-locus analysis produces an SO4-type monodromy, but
  that connection is presently only my own speculative flag (§4.2), not
  something established by the paper for this setting.
- **O09** (matched rank/ramification null validity, coarse-observable
  collisions, known-false/control classification) — **out of scope for the
  specific control mechanics**, but Definition 1.2's irreducibility
  requirement (§4.1, §2.3) gives the one paper-level fact that actually
  *explains why* the constant-sheaf controls C1/C2 should fail any
  gallant-based cancellation argument (they are not irreducible, hence not
  gallant, hence outside the class of objects the paper's machinery even
  claims to control). Everything else in O09 (translated-pullback matching,
  local inertia/tame/Swan data comparison for the audit's own matched-null
  cases) is elliptic-curve-specific bookkeeping the paper does not address.
- **O10** (certificate dependency/soundness audit, quantifier closure,
  measured work/resources, open-obligation ledger) — **out of scope**. This
  is a meta-level property of the audit process itself, not mathematical
  content any source paper could supply.

## 7. Data-quality caveats and what I could NOT verify

Listed here explicitly and separately, per the completion gate's requirement
to state plainly what was not covered:

1. **Sections 5 and 6 are unretrieved.** Two independent, differently-worded
   `WebFetch` attempts targeting these sections both returned an explicit
   "not present in retrieved excerpt" response from the tool rather than any
   content, real or fabricated. This means: the paper's actual moment-bound
   proof for gallant sheaves (which would give the real values or bounding
   strategy for `m, A, B` and their dependence on `c(M)` in the gallant
   case), and the actual sentence(s) applying Theorem 2.4 to conclude
   Theorem 1.1, are **not covered by this digest at all**. This is the
   single largest gap — I recommend the follow-on task budget at least one
   more dedicated attempt (possibly via a different retrieval path, e.g. the
   PDF, an ar5iv mirror, or splitting the query further) before assuming
   this content is permanently inaccessible.
2. **Sections 3.1–3.2 (Goursat's Lemma, coinvariants criterion) were named
   but not quoted.** I have only the section titles from the outline pass; I
   was not able to get their actual statements in the time/call budget of
   this session. This is the second-largest gap, and directly affects O05 —
   flagged in §6.
3. **The "n vs. d" ambiguity in Theorem 2.4 conclusion (3)** (§3.2) is
   unresolved. I asked the tool to specifically double-check this and it
   held to "n" while itself flagging the result as suspicious. I have no way
   to independently verify glyph-level rendering without a direct-access
   tool.
4. **"Theorem 1.6" and its exact SO4/oxozonic extension statement** (§4.2)
   rests on a single fetch pass; I was not able to get independent
   confirmation of its number or a full verbatim statement (only the "c
   odd" condition and the quoted fragment given). Treat the numbering as
   tentative.
5. **I did not open or read "[Pisa]"**, the comparison work Remark 1.2 cites
   for having polynomial complexity dependence. I only know it exists as a
   citation and what this paper claims about it; I make no claim about what
   [Pisa] itself actually proves.
6. **The precise definitions of "lisse" and "pure of weight w"** are used
   throughout but, per my search, not (re)stated in Section 2 itself; the
   paper assumes them from prior literature. I did not chase down which
   prior work the paper implicitly relies on for these (this is presumably
   standard Deligne/Katz material available elsewhere, not something absent
   from mathematics generally — just absent *from this specific paper's own
   text*).
7. **Sections 1.4 ("Cubic toroidal moments"), 4.1/4.2, 7 ("trilinear sums
   with monomial arguments"), and most of Section 9's worked examples**
   (beyond the subsection titles and the Kummer/Legendre negative search)
   were not read in this pass at all. I do not know whether any of these
   contain material relevant to families K/L that I have missed; I flag this
   as an open possibility rather than asserting these sections are
   irrelevant.
8. **General method caveat**: every quote in this document was produced by
   routing the arXiv HTML page through `WebFetch`'s own summarizing model,
   repeatedly, with different targeted prompts. I have no independent way in
   this session to view the raw page myself. I built confidence by (a)
   re-asking the same factual question in differently-worded follow-up
   prompts and checking for stable answers (done for: the "sulfatic" term,
   the Remark 1.2 text, Theorem 2.4's hypothesis and conclusions, the
   Kummer/Legendre negative results), and (b) explicitly asking the tool to
   flag its own uncertainty (done for the n/d ambiguity). This is a real
   mitigation, not a substitute for a from-source read. Anyone with direct
   access to the arXiv page (HTML or PDF) should spot-check at minimum
   Theorem 2.4's exact conclusion (3) and the Section 5/6 content this
   digest could not retrieve at all.

## 8. Fetch log (for the record)

Thirteen `WebFetch` calls were made against `https://arxiv.org/html/2511.09459v1`
in this session:

1. Attempted full verbatim reproduction of abstract/§1/Theorem 2.4/headings —
   **declined by the tool's own content policy** as excessive verbatim
   reproduction; no content obtained from this call.
2. Outline (all section/subsection headings), Theorem 1.1 paraphrase +
   short quote, Definition 1.2 paraphrase + quote, Remark 1.2 effectivity
   quote, "mixed of integral weights" usage survey.
3. Theorem 2.4 full hypothesis + conclusion attempt, `c(M)` definition,
   implicit-constant dependence, range restrictions, exceptional-locus
   mention.
4. Theorem 2.4's four numbered conclusions verbatim (repeat/refine of call
   3), Remark 1.2 full text (repeat/confirm of call 2).
5. `X^(w)` definition location, "n vs d" check on conclusion (3), search for
   a Grothendieck-style trace-formula sentence near Theorem 2.4.
6. Section 1.3 exceptional case (sulfatic/oxozonic definitions and why
   excluded), Definition 1.2 gallant/light detail, finite-vs-gallant
   monodromy question.
7. Dedicated confirmatory search for the literal string "sulfatic" (to rule
   out fabrication) and confirmation of "oxozonic."
8. Kummer/Legendre sheaf search (both negative/positive as reported),
   Section 9 worked-example subsection contents.
9. Exact sentence and surrounding context for `L_ψ`/`L_χ` notation in §2;
   "quadratic character" negative search.
10. Section 5/6 moment-estimate and stratification-application content —
    **no content retrieved**; finite/infinite monodromy split quote found
    incidentally in Section 3.4 instead.
11. Retry of Section 5 alone, more narrowly worded — **no content
    retrieved**, tool explicitly stated it could not find it.
12. Section 4.3 ("reduction to a stratification statement") key statement,
    connection to Theorem 2.4, and the complexity-`C`-as-output-not-input
    finding.
13. Section 2 duality (`F^∨`) notation and quote, Grothendieck trace-formula
    negative search, "lisse"/"middle-extension"/"pure of weight" definition
    search, `j_!` zero-extension usage quote.

No code was executed. No numerical computation was performed. No ledger
record was created or modified by this task. Nothing was written under
`experiments/EXP-CRYPTO-6505c6/`.
