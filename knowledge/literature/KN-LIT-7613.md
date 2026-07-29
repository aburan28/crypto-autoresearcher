---
id: KN-LIT-7613
type: literature
title: "Explicit height bounds on modular polynomials for the elliptic j-invariant, cube root of j, and Weber modular function f"
authors:
  - "Abraham Zhang"
year: 2026
venue: 'arXiv preprint arXiv:2607.22214 [math.NT]'
identifiers:
  eprint: null
  doi: null
  arxiv: '2607.22214'
  url: https://arxiv.org/abs/2607.22214
tags: [modular-polynomial, j-invariant, weber-function, height-bound, explicit-constants, isogeny-computation, class-polynomial, cost-model, isogeny, adjacent]
confidence: reported
citation_verified: web
added: "2026-07-29"
superseded_by: null
---

## Contribution
Improves the explicit upper bound on the height of the classical modular polynomial
`Φ_N` due to Breuer, Gómez, and Pazuki, and proves **new** explicit height bounds for
the modular polynomials of the **cube root of `j`** and the **Weber modular function
`f`**.

The abstract is unusually short and states no numerical constants, so the size of the
improvement is not recoverable from it.

## Relevance to this program
Modular polynomials are the standard vehicle for computing `ℓ`-isogenies between
elliptic curves, and their **coefficient height is what determines the bit-complexity**
of instantiating them — the cost is driven by how large the integers actually are, not
by the degree alone. Explicit (as opposed to asymptotic) height bounds are therefore a
direct input to any honest cost accounting of an isogeny-based routine.

This connects to two live threads:

- `KN-TECH-050` and `KN-TECH-057` price supersingular isogeny path-finding under
  full-cost models. Modular-polynomial height feeds the per-step cost in any variant
  that instantiates `Φ_N` explicitly.
- The **Weber function `f`** bound is the practically interesting one. Weber
  polynomials are the standard small-height substitute for `j` in class-polynomial and
  CM computations precisely because their coefficients are dramatically smaller;
  having an *explicit* bound is what makes a costed claim about that substitution
  possible rather than folkloric.

The bearing is on **cost accounting for isogeny/CM machinery**, which the program tracks
because its target-profile exemplar (Wesolowski, `p^{1/3+o(1)}`) lives in that domain.
It says nothing about prime-field ECDLP, provides no algorithm, and moves no exponent —
these are sharpened constants in existing bounds. **Does not bear on the ECDLP.**

## Not verified here
Full paper not read; claims relayed from the arXiv abstract retrieved from the arXiv
API on 2026-07-29 (hence `confidence: reported`). arXiv metadata: submitted
2026-07-24, primary category math.NT. Preprint — not peer-reviewed, no DOI or venue as
of this entry.

NOT verified here: the improved `Φ_N` bound or its margin over Breuer–Gómez–Pazuki;
the new cube-root-of-`j` and Weber bounds; and any downstream cost consequence. **No
numerical constants are recorded here because the abstract states none** — the actual
magnitude of the improvement is unknown to this entry and must be read off the paper
before any cost claim cites it. No revision to `KN-TECH-050` or `KN-TECH-057` is
asserted.
