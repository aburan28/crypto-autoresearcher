---
id: KN-LIT-7654
type: literature
title: "On the higher algebraic K-groups of arithmetically equivalent number fields"
authors:
  - "Ryo Komiya"
year: 2026
venue: "arXiv preprint arXiv:2607.26685 [math.NT, math.KT]"
identifiers:
  eprint: null
  doi: null
  arxiv: "2607.26685"
  url: "https://arxiv.org/abs/2607.26685"
tags: [arithmetic-equivalence, k-theory, zeta-function, galois-representation, class-group, number-theory, invariant, lossy-projection, etale-cohomology, methodology]
confidence: reported
citation_verified: web
added: "2026-08-01"
superseded_by: null
---

## Contribution
Introduces **`K`-equivalence** and **almost `K`-equivalence** — equivalence relations
between number fields defined by the structure of the **higher algebraic `K`-groups of
their rings of integers** — and relates them to **arithmetical equivalence** and local
integral equivalence.

Using the **Rost–Voevodsky theorem** (Quillen–Lichtenbaum) at odd primes `p`, the paper
analyses `K`-groups within continuous étale cohomology and, via **permutation
representations of global Galois groups** and **local decomposition group** data,
refines earlier results of Komatsu in the range `p ≠ 2`, giving conditions for number
fields to be (almost) `K`-equivalent.

## Key claims (as reported)
- New relations `K`-equivalence and almost `K`-equivalence, with conditions
  characterizing them.
- Refinement of Komatsu's results for `p ≠ 2`; the `p = 2` case is outside the stated
  range.
- Connections drawn to special values of zeta functions and to Galois representations.

## Relevance to this program
**No algorithmic or cryptographic content whatsoever.** Ingested for one methodological
reason, and the entry should not be cited for anything else.

**Arithmetic equivalence is the cleanest naturally occurring instance of a lossy
invariant.** Two number fields are arithmetically equivalent when they share a
**Dedekind zeta function** — yet they may be non-isomorphic, and may have **different
class numbers and different unit groups**. This is the exact structure
`docs/inventor-protocol.md` and [[KN-TECH-056]] call the **lossy-projection test**:
a canonical, computable, natural-looking invariant that provably fails to determine the
object. Here mathematics supplies a worked example with a century of refinement — a
whole tower of invariants (zeta function ⇒ arithmetic equivalence; `K`-groups ⇒
`K`-equivalence; local integral data) each capturing part of the field and each with a
known deficiency.

Why this program should hold it: the corpus's isomorphism-problem thread
([[KN-LIT-7648]], [[KN-LIT-7652]]) turns entirely on *which invariants separate orbits
and which do not*. Arithmetic equivalence is the textbook case where that question has
been studied for its own sake, and it is a useful antidote in both directions — against
assuming an invariant is complete, and against assuming a distinguishing invariant must
exist.

**Does not bear on the ECDLP**, and no attack, algorithm, or cost follows from it.

## Not verified here
Full paper not read. Claims relayed from the arXiv API abstract for 2607.26685,
retrieved 2026-08-01 (hence `confidence: reported`). arXiv metadata: submitted
2026-07-29, categories math.NT and math.KT, single author. Preprint — not peer-reviewed,
no DOI or venue as of this entry.

NOT verified here: the definitions of `K`-equivalence and almost `K`-equivalence; the
refinement of Komatsu; the use of Rost–Voevodsky; and any of the zeta-value or Galois
representation connections. **The background statements about arithmetic equivalence in
"Relevance" (equal zeta functions, possible non-isomorphism, possible differing class
numbers) are standard results attributed to the Perlis-era literature; they are stated
here from general knowledge and are `established`-level textbook material, but they were
not re-checked against a source during this entry's creation and do not come from this
paper's abstract.**
