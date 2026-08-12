---
id: KN-LIT-7598
type: literature
title: "A lower bound for the distance between CM points on Shimura curves"
authors:
  - "Daniel Rodriguez"
year: 2026
venue: 'arXiv preprint arXiv:2607.23270 [math.NT]'
identifiers:
  eprint: null
  doi: null
  arxiv: '2607.23270'
  url: https://arxiv.org/abs/2607.23270
tags: [cm-points, shimura-curve, quaternion-algebra, endomorphism-ring, discriminant, diophantine-approximation, liouville, separation-bound, adjacent]
confidence: reported
citation_verified: web
added: "2026-07-28"
superseded_by: null
---

## Contribution
A quantitative Diophantine-approximation result: an explicit **lower bound on how close
CM points on a Shimura curve `X(D,1)` can get to a fixed CM point**, in terms of the
discriminant of the endomorphism rings involved.

## Key claims (as reported)
- For a sequence of CM points `P_n` converging to a fixed CM point `P` on `X(D,1)`, the
  distance between the corresponding fixed points `τ_n` and `τ` in the upper half-plane is
  bounded below by a positive constant times a **negative power of the discriminant**.
- Proof ingredients: the complex geometry of the Fuchsian uniformization, the explicit
  matrix representation of the underlying quaternion algebra, and Liouville's inequality.
- Presented as a Shimura-curve analogue of a result of Habegger on singular moduli and
  modular curves.

## Relevance to this program
Adjacent, and recorded for a specific reason rather than on keyword match. Quaternion
algebras and endomorphism-ring discriminants are the arithmetic of the supersingular
world (`KN-TECH-028`, `KN-TECH-029`), and **separation bounds are the kind of ingredient
that turns an approximate search into an exact one**: knowing that distinct objects cannot
be closer than some explicit function of their discriminant is what licenses rounding a
numerical computation to an exact answer, and it is what bounds the precision a search has
to carry. That is the generic shape by which an analytic estimate becomes an algorithmic
one.

Whether that shape is realizable here is **entirely unestablished**. This is a statement
about archimedean distance in the upper half-plane on a complex Shimura curve; the
isogeny-graph and endomorphism-ring computations this program cares about are `p`-adic
and finite-field objects. **No connection to any isogeny or ECDLP algorithm is claimed by
the paper or asserted here** — the entry is a pointer for whoever next works on
endomorphism-ring computation, not a technique with a demonstrated route in.

## Not verified here
Full paper not read; all claims relayed from the official arXiv abstract retrieved from
the arXiv API on 2026-07-28 (hence `confidence: reported`). arXiv metadata: submitted
2026-07-25, primary category math.NT. Preprint — not peer-reviewed, no DOI or venue as of
this entry.

NOT verified here: the lower bound and its explicit exponent in the discriminant, the
proof via Fuchsian uniformization and Liouville's inequality, and the attribution of the
modular-curve analogue to Habegger. **Whether any separation bound of this kind is usable
in an algorithm over finite fields has not been checked and is explicitly not claimed.**
