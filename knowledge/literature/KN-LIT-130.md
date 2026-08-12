---
id: KN-LIT-130
type: literature
title: Orientations and the Supersingular Endomorphism Ring Problem
authors: [Wesolowski Benjamin]
year: 2022
venue: 'Advances in Cryptology - EUROCRYPT 2022, Part III, LNCS 13277, pages 345-371, Springer'
identifiers:
  eprint: iacr:2021/1583
  doi: 10.1007/978-3-031-07082-2_13
  url: https://eprint.iacr.org/2021/1583
tags: [supersingular, endomorphism-ring, orientation, oriented-curve, class-group-action, isogeny-path, reduction, equivalence, grh, hardness-foundation, post-quantum, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-25
superseded_by: null
---

## Contribution
Relates two families of problems in isogeny-based cryptography: computing the
endomorphism ring of a supersingular elliptic curve, and inverting the action of
class groups on **oriented** supersingular curves. The paper proves these
families are closely related through polynomial-time reductions, assuming the
generalised Riemann hypothesis, and identifies two classes of essentially
equivalent problems — the first corresponding to computing the endomorphism ring
of oriented curves.

## Key claims (as reported)
- Endomorphism-ring computation and class-group-action inversion on oriented
  curves are connected by polynomial-time reductions, **under GRH**.
- Two classes of essentially equivalent problems are identified; the first is the
  oriented-curve endomorphism-ring problem.
- The reductions are structural results about problem hardness, not attacks: they
  say where hardness may be transported, not that any instance is broken.

## Relevance to this program
`RQ-SSI-001` lists "orientation, torsion, and other auxiliary-structure
exploitation" as an in-scope method, and before this entry the corpus had **no**
orientation entry at all — `oriented curve` returned zero hits across all 190
entries, while `orientation` appeared only as narrative prose inside CSIDH and
Deuring entries. That was a direct hole under an explicitly declared scope line.

Its value to `GOAL-SSI-001` is as a **hardness map**. The goal is scoped to three
surviving assumptions, and reductions of this kind determine whether an advance
against one transfers to another. It extends `KN-LIT-074` (isogeny path and
endomorphism ring equivalent) to the oriented setting, and it is the theoretical
bridge between the CSIDH line (`KN-LIT-069`, `KN-LIT-070`, `KN-TECH-027`) and the
endomorphism-ring line (`KN-LIT-072`-`075`, `KN-TECH-028`), which the corpus
previously carried as two separate stories.

The GRH assumption should travel with every use of this result. A reduction that
holds under GRH is not the same object as an unconditional one, and the program's
own claim-tier discipline requires the conditionality to be stated wherever the
reduction is invoked.

## Not verified here
Verification was by web search surfacing primary-index listings (IACR ePrint
2021/1583, Springer/ACM DOI 10.1007/978-3-031-07082-2_13, EUROCRYPT 2022 Part III
/ LNCS 13277 / pp. 345-371, plus a HAL deposit); direct fetches returned HTTP 403
under this session's egress policy. The full citation including volume and page
range was corroborated by a search result giving it explicitly.

NOT verified here: the precise statements of the problems in each equivalence
class, the direction and tightness of each reduction, exactly which results
require GRH, and what the second equivalence class is. The summary above
paraphrases an abstract returned by search and must not be cited for a specific
reduction.
