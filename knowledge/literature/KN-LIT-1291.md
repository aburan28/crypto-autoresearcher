---
id: KN-LIT-1291
type: literature
title: "Radical √ N élu Isogeny Formulae"
authors:
  - "Thomas Decru"
year: 2024
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2024/878"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2024/878"
tags: [class-group, curve-arithmetic, elliptic-curve, isogeny, number-theory, pqc, protocol, sidh-csidh, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We provide explicit radical N -isogeny formulae for all odd integers N . The formulae are compact closed-form expressions which require one N th root computation and O(N ) basic field operations.

## Key claims (as reported)
- The formulae are highly efficient to compute a long chain of N -isogenies, and have the potential to be extremely beneficial for speeding up certain cryptographic protocols such as CSIDH.
- Unfortunately, the formulae are conjectured, but we provide ample supporting evidence which strongly suggests their correctness.
- For CSIDH-512, we notice an additional 35% speed-up when using radical isogenies up to N = 199, compared to the work by Castryck, Decru, Houben and Vercauteren, which uses radical isogenies up to N = 19 only.
- The addition of our radical isogenies also speeds up the computation of larger class group actions in a comparable fashion.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2024-878.pdf`
