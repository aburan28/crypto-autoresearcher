---
id: KN-LIT-131
type: literature
title: The Supersingular Endomorphism Ring and One Endomorphism Problems are Equivalent
authors: [Page Aurel, Wesolowski Benjamin]
year: 2024
venue: 'Advances in Cryptology - EUROCRYPT 2024, Springer'
identifiers:
  eprint: iacr:2023/1399
  doi: 10.1007/978-3-031-58751-1_14
  url: https://eprint.iacr.org/2023/1399
tags: [supersingular, endomorphism-ring, one-endomorphism, reduction, equivalence, hardness-foundation, sqisign, isogeny-path, post-quantum, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-25
superseded_by: null
---

## Contribution
Proves that the supersingular **Endomorphism Ring** problem (compute all
endomorphisms of a given supersingular elliptic curve) and the **One
Endomorphism** problem (find a single non-scalar endomorphism) are equivalent
under probabilistic polynomial-time reductions. The Endomorphism Ring problem's
presumed hardness is foundational for isogeny-based cryptography, so the result
says that finding one non-scalar endomorphism is already as hard as finding the
whole ring.

## Key claims (as reported)
- Endomorphism Ring and One Endomorphism are equivalent under probabilistic
  polynomial-time reductions.
- The Endomorphism Ring problem's presumed hardness is foundational for
  isogeny-based cryptography — the paper frames the result as consolidating that
  foundation.
- This is a hardness-equivalence result, not an attack.

## Relevance to this program
The corpus's **first 2024 entry**, and it lands on the exact foundation
`GOAL-SSI-001` is scoped to. `KN-OPEN-013` asks how hard the supersingular
endomorphism-ring / isogeny-path problem is and whether it is a sound
post-quantum foundation after the SIDH break; this is part of the answer the
literature has since given, and the corpus did not have it.

Operationally it closes off a proposal shape. An idea that aims to attack a
surviving supersingular assumption by "only" recovering a single non-scalar
endomorphism — a natural-looking weakening, and the kind of relaxation this
program's ideation generates — is, by this result, no easier than the full
problem. That is a boundary a novelty screen should surface before compute is
spent, and it is why this entry belongs in the corpus rather than in a batch
report.

Together with `KN-LIT-074` (path and ring equivalent) and `KN-LIT-130` (oriented
setting), the corpus now carries the three reductions that make the
endomorphism-ring problem the load-bearing assumption of the surviving schemes.

## Not verified here
Verification was by web search surfacing primary-index listings (IACR ePrint
2023/1399, DBLP `conf/eurocrypt/PageW24`, ACM/Springer DOI
10.1007/978-3-031-58751-1_14, a HAL deposit, and an arXiv mirror at 2309.10432);
direct fetches returned HTTP 403 under this session's egress policy. Title,
authors, year and venue are corroborated across independent results.

NOT verified here: the reduction's construction, its cost, whether it is
unconditional or carries assumptions such as GRH, and what heuristics if any it
relies on. **The conditionality question is material** given that the closely
related `KN-LIT-130` and `KN-LIT-074` results are GRH-conditional, and it must be
checked against the paper before this entry is used to close `KN-OPEN-013`.
