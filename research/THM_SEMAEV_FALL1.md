# THM_SEMAEV_FALL1 — Decidable attribution of degree falls in Weil-descended Semaev systems

- **ID:** THM-SEMAEV-FALL1
- **Task:** theory track for RQ-DREG-bd6c86 (ledger/questions/RQ-DREG-bd6c86.yaml), whose constraints require that "each attributed degree fall must be traced to an explicit syzygy class (symmetry, Frobenius, field equation) or recorded as unexplained"
- **Author:** top-level session (theory track), 2026-09-16
- **Reads:** ledger/questions/RQ-DREG-bd6c86.yaml, knowledge/literature/KN-LIT-7605.md (last fall degree of Weil descent systems), formal/README.md, formal/targets/README.md
- **Verification artifact:** none yet. This note exists to make three claims precise enough to formalize; no Lean build has been run, and `formal/setup.sh` has not been executed in the authoring session (no `elan`/`lean` on PATH).

## 0. Result summary

1. **PROVED (Lemma 1, Frobenius collapse):** over `K = F_{q^n}` with field equations imposed, `q`-th powering coincides with coefficientwise Frobenius. This is a two-line identity, and it is the exact structural reason the Weil-descended Semaev systems are not semi-regular: their Frobenius conjugates are redundant modulo `q`-th powers and field equations, so degree falls are available for free at a degree that does not grow with `n`.
2. **PROVED (Lemma 2, symmetrization):** rewriting a symmetric summation polynomial in elementary symmetric coordinates preserves *weighted* degree and does not increase *total* degree. The Gröbner-basis gain observed by FGHR is **not** proved here and is not implied by Lemma 2.
3. **PROVED, trivially (Lemma 3, certificate soundness):** the decomposition-certificate predicate is total and decidable given the curve's group law, so it is checkable by a proof assistant rather than only by a script.
4. **NOT PROVED AND NOT PROVABLE BY THIS ROUTE (§4):** that a given degree fall is *unexplained*. Lemmas 1–3 give a sound attribution procedure, never a complete one. A Lean check that passes certifies the fall this syzygy produces; a Lean check that fails certifies nothing about the existence of other syzygies.
5. **OUT OF SCOPE:** the growth law itself. No statement here bounds the solving degree, the degree of regularity, or the last fall degree as a function of `m, n', n, q`. That is RQ-DREG-bd6c86's open question and there is no proof in the literature to formalize.

## 1. Setup

Let `p` be prime, `q = p^e`, `K = F_{q^n}`, and let `phi : K -> K` be the `q`-power Frobenius, `phi(c) = c^q`, whose fixed field is `F_q`.

Let `R = K[x_1, ..., x_M]` and let

    I_q = (x_1^q - x_1, ..., x_M^q - x_M)

be the **field-equation ideal**, which cuts out the `F_q`-rational points of affine `M`-space. In the Weil-descent setting `M = m * n'`: the `m` summands of a decomposition each contribute `n'` coordinates with respect to a fixed `F_q`-basis of the subspace `V` of dimension `n'`.

For `g = sum_alpha c_alpha x^alpha` in `R`, write `g^phi = sum_alpha phi(c_alpha) x^alpha` for the coefficientwise twist. Note `deg(g^phi) = deg(g)`, since `phi` is injective and so moves no coefficient to zero.

## 2. Statements and proofs

### Lemma 1 (Frobenius collapse) — PROVED

For every `g` in `R`:

    g^q  ≡  g^phi   (mod I_q).

*Proof.* `R` has characteristic `p` and `q = p^e`, so `y |-> y^q` is a ring endomorphism of `R` (the `e`-fold composite of the Frobenius endomorphism). Writing `g = sum_alpha c_alpha x^alpha`, additivity of `q`-th powering gives

    g^q = sum_alpha c_alpha^q (x^alpha)^q = sum_alpha phi(c_alpha) x^(q*alpha).

Each generator `x_i^q - x_i` of `I_q` gives `x_i^q ≡ x_i`, hence `x^(q*alpha) ≡ x^alpha` for every exponent vector `alpha`. Substituting,

    g^q ≡ sum_alpha phi(c_alpha) x^alpha = g^phi   (mod I_q).  ∎

### Corollary 1 (the free degree fall) — PROVED

Let `J` be an ideal of `R` containing `I_q`, and let `g` be in `J` with `d = deg(g) >= 1`. Then `g^phi` is in `J`, and it is obtained as the reduction modulo `I_q` of the degree-`q*d` element `g^q`. The reduction therefore realises a degree drop of `(q - 1) * d`.

*Proof.* `g` in `J` implies `g^q` in `J`; `I_q` is contained in `J`, so Lemma 1 puts `g^phi` in `J`. Degrees: `deg(g^q) = q * d` because `R` is a domain, and `deg(g^phi) = d`. ∎

### Remark 1 (why this makes the systems non-random) — INTERPRETATION, NOT A THEOREM

The descended Semaev system is built from a single equation `f` over `K` together with its Frobenius conjugates `f^phi, f^(phi^2), ..., f^(phi^(n-1))`, all imposed on `F_q`-rational coordinates. Corollary 1 says each conjugate is already reachable from the previous one through a `q`-th power and a field-equation reduction, at a degree governed by `deg(f)` and `q` and **not** by `n`. A support-matched random system with the same multidegree and the same field equations has no such relation between its members. This is the mechanism behind the bounded last-fall-degree results recorded in `KN-LIT-7605`.

It is a mechanism, not a bound. Corollary 1 exhibits falls; it does not show they propagate, and propagation is exactly what the first-fall-degree assumption asserts and what Kosters–Yeo disputed. Nothing here supports a subexponential claim.

### Lemma 2 (symmetrization) — PROVED

Let `S` in `R` be symmetric in `x_1, ..., x_m`, and let `T` be the unique polynomial with `S = T(e_1, ..., e_m)`, where `e_i` is the `i`-th elementary symmetric polynomial. Give `e_i` the weight `i`. Then:

(a) the weighted degree of `T` equals `deg(S)`;
(b) the total degree of `T` is at most `deg(S)`.

*Proof.* (a) is the degree-preserving form of the fundamental theorem of symmetric polynomials: `e_i` is homogeneous of degree `i`, so substituting `e_i` into a weighted-homogeneous component of weighted degree `d` yields a homogeneous polynomial of degree `d`; the substitution is a graded isomorphism onto the symmetric subalgebra, so no cancellation between components occurs and the weighted degree is exactly `deg(S)`. (b) follows since every weight is at least 1, so total degree is bounded by weighted degree. ∎

### Remark 2 (what Lemma 2 does not say) — SCOPE

Lemma 2 bounds the degree of the *representation*. It says nothing about the Gröbner solving degree of the symmetrized ideal, which is the quantity FGHR measured and the one that matters. Treating (b) as an explanation of the observed speedup would be exactly the lossy projection `docs/inventor-protocol.md` warns about.

### Lemma 3 (certificate soundness) — PROVED (trivially), and DECIDABLE

Let `E/K` be a Weierstrass curve, `V` a declared `F_q`-subspace of `K` with a fixed basis, `R` a point of `E(K)`, and let a **decomposition certificate** be a tuple of affine points `P_1, ..., P_m` of `E(K)`. The predicate

    Valid(P_1, ..., P_m; R)  :=  (each P_i lies on E)  and  (x(P_i) is in V for each i)  and  (P_1 + ... + P_m = R)

is total and decidable: the first conjunct is an equality in `K`, the second is membership in the span of a finite declared basis, i.e. solving an `F_q`-linear system, and the third is a finite sequence of group-law operations followed by an equality test.

*Proof.* Each conjunct is a decidable predicate over a finite field with decidable equality, and a finite conjunction of decidable predicates is decidable. ∎

### Remark 3 (why Lemma 3 is worth formalizing despite being trivial) — RATIONALE

AGENTS rule 4 requires that any claimed solve or relation carry a certificate that the run wrapper re-verifies independently. Today that re-verification is a script sharing a language, a library stack, and frequently an author with the code that produced the claim. Lemma 3 says the check is exactly the kind of total decidable predicate a proof assistant settles, which removes the shared-implementation failure mode rather than duplicating it. The value is the independence of the checker, not the depth of the statement.

## 3. Formalization targets that follow

Each is a **per-instance identity or decision procedure**, not a growth statement, and each is decidable without Gröbner-basis machinery — which matters because Mathlib does not carry Macaulay-matrix or Buchberger theory, and the Huang–Kosters–Petit–Yeo last-fall-degree theorem is therefore out of reach at present cost.

| target | statement | needs |
| --- | --- | --- |
| `semaev-frobenius-collapse` | Lemma 1 | `MvPolynomial`, `frobenius`, char-`p` freshman's dream |
| `semaev-decomposition-certificate` | Lemma 3 | `WeierstrassCurve.Affine.Point` and its group law |
| `semaev-symmetrization-degree` | Lemma 2(b) | symmetric polynomials, `esymm`, degree lemmas |

## 4. The completeness gap — STATED SO IT IS NOT MISREAD

Lemmas 1–3 give a **sound** attribution procedure: a passing check certifies that the named syzygy class does produce the observed fall. They do not give a **complete** one. A failing check does not establish that no syzygy explains the fall; it establishes only that the one that was tried does not.

Consequently, under RQ-DREG-bd6c86 the "unexplained" bucket is defined by the attribution attempts actually made, and must be reported that way — as a list of classes tried and rejected, never as a claim that the fall is structurally novel. A Lean artifact that is read as certifying novelty would be a stronger claim than any lemma here supports, and would be the precise error the claim tiers in `docs/claims-and-verification.md` exist to prevent.

## 5. Open gaps

- **(G1)** Propagation. Corollary 1 exhibits falls at a degree independent of `n`; whether enough independent falls appear at each subsequent degree to keep the solving degree near the first fall degree is the open question, and is what RQ-DREG-bd6c86 proposes to measure rather than prove.
- **(G2)** The last-fall-degree bound of `KN-LIT-7605` is a genuine theorem and the natural Lean target after Mathlib grows Gröbner/Macaulay support. It is specced nowhere yet because a faithful statement needs that support to exist first.
- **(G3)** The null object. The support-matched multihomogeneous semi-regular Hilbert series is a generating-function computation, not an identity, and sits between tiers: formalizable in principle, but only worth it once the measurement protocol has frozen which null it uses.
