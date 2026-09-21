---
id: KN-LIT-7573
type: literature
title: Generic ordinarity for abelian coverings of the projective line
authors: [Blache Regis]
year: 2026
venue: 'arXiv preprint (math.AG, math.NT)'
identifiers:
  eprint: null
  doi: null
  arxiv: '2607.21033'
  url: https://arxiv.org/abs/2607.21033
tags: [abelian-covering, projective-line, ordinary, mu-ordinary, newton-polygon, hurwitz-space, torelli, shimura-variety, l-function, character-sums, finite-field, monodromy, semaev-cover]
confidence: reported
citation_verified: web
added: 2026-07-26
superseded_by: null
---

## Contribution
Shows that abelian coverings of the projective line of order prime to `p` are
**generically `mu`-ordinary in characteristic `p`**. The route: images of the
irreducible components of Hurwitz spaces of such coverings under the Torelli morphism
lie in certain Shimura varieties whose Newton-polygon stratification is known; the
paper shows the generic Newton polygon for the Hurwitz space coincides with the
generic (`mu`-ordinary) Newton polygon of the smallest Shimura variety containing its
image. This requires computing generic Newton polygons for **`L`-functions attached to
multiplicative character sums over the projective line**.

## Key claims (as reported)
- Abelian coverings of `P^1` of order prime to `p` are generically `mu`-ordinary in
  characteristic `p`.
- Images under Torelli of the irreducible components of the relevant Hurwitz spaces lie
  in Shimura varieties whose Newton-polygon stratification is known.
- The Hurwitz-space generic Newton polygon equals the `mu`-ordinary Newton polygon of
  the smallest containing Shimura variety.
- Generic Newton polygons are computed for `L`-functions associated to multiplicative
  character sums over `P^1`.

## Relevance to this program
Pure arithmetic geometry, with **no cryptographic content and no ECDLP claim** — but
it lands on the machinery behind one specific open problem in the corpus.

`KN-OPEN-009` asks whether the geometric monodromy of the `m`-th Semaev summation
cover is the full symmetric/wreath group for generic ordinary curves, or whether there
is an exceptional locus with smaller monodromy giving deviant relation rates. That
question is about **covers of a base, families over a moduli/Hurwitz-type space, and
generic-versus-exceptional behaviour in characteristic `p`** — the same shape of
question this paper answers for a different family. Three specific points of contact:

- **The generic/exceptional dichotomy is the object of study.** The paper's result form
  — "generic member of the family is `mu`-ordinary, exceptional loci are the
  complement" — is exactly the form an answer to `KN-OPEN-009` would take. It is
  evidence that this question type is tractable by identifying the smallest ambient
  structure (there, a Shimura variety) that the family's image sits inside.
- **Hurwitz spaces of coverings are the right ambient object.** `KN-OPEN-009` is
  currently posed informally; this paper is a template for posing it as a statement
  about a Hurwitz space of covers and its image under a period/Torelli-type map.
- **`L`-functions of multiplicative character sums.** The technical input overlaps with
  `KN-TECH-016` (sum-product / additive combinatorics over `F_p`) and with
  `KN-LIT-7569` in this same gather. The recurring instrument is: attach an
  `L`-function to a character sum, read off the Newton polygon, conclude generic
  equidistribution.

The caveat matters more than the connection: **abelian coverings are the commutative,
highly structured case.** Semaev summation covers are not abelian coverings of `P^1`,
and `KN-OPEN-009` explicitly hypothesizes *full symmetric or wreath* monodromy — the
opposite extreme. So this paper supplies technique and framing, **not** a result about
the program's covers, and must not be cited as bearing on relation rates.

## Not verified here
Full paper not read; all claims relayed from the official arXiv abstract retrieved via
the arXiv API on 2026-07-26 (hence `confidence: reported`). Submitted 2026-07-23,
primary category math.AG, cross-listed math.NT. A preprint: no DOI, journal reference,
or peer review recorded on arXiv as of this entry.

NOT verified here: all mathematical content — the `mu`-ordinarity theorem, the Torelli
image claim, the Newton-polygon coincidence, and the `L`-function computations. The
definitions of `mu`-ordinary and of the relevant Shimura varieties were not checked.
**The entire "Relevance" section is this entry's own reading**; the paper makes no
claim about summation polynomials, ECDLP, cryptography, or `KN-OPEN-009`, and no
transfer of its results to Semaev covers has been established or attempted here.
