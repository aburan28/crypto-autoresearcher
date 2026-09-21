---
id: KN-LIT-7590
type: literature
title: Degenerating Discriminants
authors:
  - "Viktoriia Borovik"
  - "Clara Briand"
year: 2026
venue: 'arXiv preprint arXiv:2607.17966 [math.AG]'
identifiers:
  eprint: null
  doi: null
  arxiv: '2607.17966'
  url: https://arxiv.org/abs/2607.17966
tags: [groebner-degeneration, discriminant, dual-variety, conormal-variety, whitney-stratification, mixed-discriminant, polynomial-system, elimination, algebraic-geometry, proof-technique]
confidence: reported
citation_verified: web
added: "2026-07-27"
superseded_by: null
---

## Contribution
Studies how projective dual varieties and discriminants behave under flat degenerations.
For **Gröbner degenerations**, shows the conormal variety admits a Gröbner degeneration
with opposite weights on the dual coordinates, and describes the irreducible components
and multiplicities of the special fiber — hence of the limiting dual hypersurface.

## Key claims (as reported)
- Gröbner degeneration of the conormal variety carries **opposite weights** on the dual
  coordinates.
- Using Whitney stratifications and Sabbah's formula, the components and multiplicities of
  the special fiber of that degeneration are described.
- The results extend to higher associated hypersurfaces in Grassmannians.
- Applications: recovering classical formulas for hypersurfaces with isolated
  singularities; analysing degenerations of generic complete intersections and reciprocal
  linear spaces; relating the theory to **mixed discriminants of parametrized polynomial
  systems**.

## Relevance to this program
Recorded as a low-priority technique pointer, on the strength of two contact points with
machinery the program already uses. Neither is a result about the ECDLP and neither has
been checked to transfer.

1. **Gröbner degeneration as a cost-of-elimination lens.** The program's difficulty
   indicator for summation-polynomial systems is Gröbner solving degree (`KN-TECH-004`,
   `KN-TECH-011`, `KN-OPEN-002`). A Gröbner degeneration replaces a system by its initial
   system with respect to a weight, and the question of which structure survives that
   degeneration is close to the question of what a solver is actually paying for. This
   paper tracks a specific invariant — the dual variety/discriminant — through exactly
   that degeneration, with explicit multiplicities.

2. **Mixed discriminants of parametrized polynomial systems.** This is the sharper hook.
   `KN-OPEN-004` asks whether support-aware (BKK / mixed-volume) elimination undercuts
   dense resultants for prime-field summation-polynomial systems. Mixed *discriminants* are
   the discriminantal counterpart of mixed volumes, and the program's interest in BKK-type
   sparse methods is precisely an interest in invariants that see the support rather than
   the dense degree. A paper connecting discriminant degeneration to mixed discriminants of
   parametrized systems is, at minimum, adjacent to that question.

The honest limits. Summation polynomials are not mentioned; elliptic curves are not
mentioned; nothing here is about solving, only about the geometry of discriminants under
degeneration. The corpus records `KN-OPEN-004` as **open**, and this entry does not move
it — it flags a body of machinery that a future attempt on `KN-OPEN-004` should be aware
exists. Filed at the same confidence as any unread preprint.

No entry status changes and nothing is superseded.

## Not verified here
Full paper not read; all claims relayed from the official arXiv abstract retrieved from
the arXiv API on 2026-07-27 (hence `confidence: reported`). arXiv metadata: submitted
2026-07-20, primary category math.AG (cross-listed math.AC), 33 pages per the author
comment. Preprint — not peer-reviewed, no DOI or venue as of this entry.

NOT verified here: the opposite-weights result for conormal varieties; the component and
multiplicity description via Whitney stratifications and Sabbah's formula; the Grassmannian
extension; and every stated application, including the mixed-discriminant connection that
is this entry's main reason for existing. **No relevance to summation-polynomial systems,
to `KN-OPEN-004`, or to any ECDLP question has been established** — the two contact points
above are this program's speculative reading of the abstract, not claims made by the
paper, and must not be cited as results.
