---
id: KN-LIT-7644
type: literature
title: "The discrete logarithm problem in cokernels of O_K-matrices"
authors:
  - "Isaac Rajagopal"
year: 2026
venue: "arXiv preprint arXiv:2607.03594 [math.NT]"
identifiers:
  eprint: null
  doi: null
  arxiv: "2607.03594"
  url: "https://arxiv.org/abs/2607.03594"
tags: [dlp, class-group, number-theory, ring-of-integers, module, sandpile, broken-platform, cryptanalysis, complexity, negative-result]
confidence: reported
citation_verified: web
added: "2026-08-01"
superseded_by: null
---

## Contribution
Generalizes the Blackburn (2009) and Shokrieh (2010) result that the discrete logarithm
is **easy in sandpile groups of graphs** — hence that sandpile groups are unsuitable as
DLP platforms — from `Z` to the **ring of integers `O_K` of a number field `K`**.

For `M ∈ M_{n×m}(O_K)`, the paper gives an algorithm computing discrete logarithms in
the cokernel `cok(M) = O_K^n / M·O_K^m`, viewed either as an `O_K`-module or as an
abelian group, in time `Õ((m+n)^{ω+1})` where `ω` is a matrix-multiplication exponent.
When `M` is **Hermitian** with respect to a Galois involution `σ` and nonsingular, the
bound improves to `Õ(n^ω)`.

The stated obstacle overcome is that when `K` has **nontrivial class group**, `O_K` is
not Euclidean, and the previous methods depended on the Euclidean algorithm.

## Key claims (as reported)
- Polynomial-time DLP in `cok(M)` for `M` over `O_K`, at `Õ((m+n)^{ω+1})`, in both the
  module and the group interpretation.
- Improved `Õ(n^ω)` for nonsingular `σ`-Hermitian `M`.
- Nontrivial class group is handled; failure of the Euclidean algorithm is not a
  barrier.
- This is a **negative result for cryptography**: it removes a candidate platform
  family rather than attacking a deployed one. The abstract presents it that way.

## Relevance to this program
Three reasons this is worth holding, none of them "a new attack":

1. **It is a clean instance of the lossy-projection pattern** the inventor protocol
   (`docs/inventor-protocol.md`, [[KN-TECH-056]]) makes central. A group presented as
   `O_K^n / M·O_K^m` looks opaque, but the presentation *is* the trapdoor: the matrix
   `M` carries enough structure to invert the projection. Any future proposal in this
   program that builds a DLP platform from a **quotient of a module by a presented
   relation matrix** should be checked against this entry first — it is very likely
   `known`, not novel.
2. **Class-group obstruction as a non-obstruction.** The natural hope — "`O_K` is not
   Euclidean when `h_K > 1`, so the reduction breaks" — is exactly what the paper
   defeats. That failure mode (assuming an algebraic obstruction protects a
   construction, when it only complicates the algorithm) is a recurring one, and this
   is a documented case of it.
3. **Corpus coverage.** The `class-group`/`ring-of-integers` algorithmic thread is
   comparatively thin relative to the isogeny and index-calculus threads. See also
   [[KN-LIT-7645]] for the function-field/curve analogue of class-group computation.

**Does not bear on the ECDLP.** No elliptic curve appears; the groups are finite
abelian groups presented by module relations, and their DLP being easy says nothing
about `E(F_p)`.

## Not verified here
Full paper not read. Claims relayed from the arXiv API abstract for 2607.03594,
retrieved 2026-08-01 (hence `confidence: reported`). arXiv metadata: submitted
2026-07-03, sole category math.NT, single author. Preprint — not peer-reviewed, no DOI
or venue as of this entry.

NOT verified here: the algorithms; the complexity exponents or the model `ω` is taken
in; the Hermitian improvement; the attributions to Blackburn and Shokrieh; and whether
`Õ` hides factors in `log|disc K|` or in the class number, which the abstract does not
say and which would matter for any concrete instance.
