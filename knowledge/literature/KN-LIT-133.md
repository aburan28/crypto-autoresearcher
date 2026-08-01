---
id: KN-LIT-133
type: literature
title: 'SQIsignHD: New Dimensions in Cryptography'
authors: [Dartois Pierrick, Leroux Antonin, Robert Damien, Wesolowski Benjamin]
year: 2024
venue: 'Advances in Cryptology - EUROCRYPT 2024, Springer'
identifiers:
  eprint: iacr:2023/436
  doi: null
  url: https://eprint.iacr.org/2023/436
tags: [sqisign, sqisignhd, signature, higher-dimensional-isogeny, kani, endomorphism-ring, deuring, supersingular, isogeny, constructive, post-quantum, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-25
superseded_by: null
---

## Contribution
A post-quantum signature scheme inspired by SQIsign that **exploits the
algorithmic breakthrough underlying the SIDH attack** — the ability to represent
an isogeny of arbitrary degree as a component of a higher-dimensional isogeny.
Reported to overcome SQIsign's main drawbacks and to scale well to high security,
at the cost of verification now requiring an isogeny computation in dimension 4,
whose optimised cost the authors describe as still uncertain. An experimental
SageMath verification implementation is reported at around 600 ms.

## Key claims (as reported)
- The technique that **broke** SIDH (higher-dimensional isogeny representations,
  the Kani-style machinery of `KN-LIT-067`, `KN-LIT-068`, `KN-TECH-026`) is here
  turned into a **constructive** tool.
- SQIsignHD overcomes the main drawbacks of SQIsign and scales well to high
  security.
- Verification requires computing an isogeny in **dimension 4**, and its
  optimised cost "is still uncertain."
- An experimental SageMath verification runs in roughly 600 ms, which the authors
  present as indicating the cryptographic interest of dimension-4 isogenies after
  optimisation and low-level implementation.

## Relevance to this program
`KN-OPEN-015` asks what the SIDH break teaches — when publishing auxiliary
structure collapses an assumption, and which schemes are safe. This entry adds
the half of the answer the corpus was missing: the break's machinery did not only
destroy, it became a construction technique. Any synthesis this program writes
about the lesson of SIDH is incomplete without it.

For `GOAL-SSI-001` it is scope-defining. The goal targets *surviving*
assumptions, and the SQIsign line is named as one of them via its
endomorphism-ring foundation. The corpus's SQIsign entry (`KN-LIT-072`) is 2020
and predates this entire redesign, so a novelty screen run against the corpus as
it stood would have assessed proposals against a scheme generation that has since
been superseded — the precise failure mode flagged in §6.1 of
`docs/knowledge-review-20260725.md`. The post-2023 line is broader than this one
paper: search also surfaced SQIsign2D-East (ASIACRYPT 2024), SQIPrime, and
SQIsign2DPush, none of which are yet in the corpus.

Note also the honest uncertainty in the source itself — verification cost in
dimension 4 "still uncertain" — which is a cost-model open question inside a
constructive proposal, and exactly the kind of hedge `SEEDING.md` requires be
preserved rather than smoothed away.

## Not verified here
Verification was by web search surfacing primary-index listings (IACR ePrint
2023/436, EUROCRYPT 2024, HAL deposits `hal-04056062` and `inria.hal-04562459`,
and the authors' SQIsignHD implementation repository); direct fetches returned
HTTP 403 under this session's egress policy. The Springer DOI was not confirmed
and is null.

NOT verified here: the scheme's construction, its signature and key sizes, its
security reduction and assumptions, the precise sense in which it "scales well",
and the conditions of the 600 ms measurement. The related 2024 SQIsign2D papers
are recorded above as leads only — their bibliographic details have not been
verified and no entry should be written for them from this note.
