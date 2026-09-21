---
id: KN-LIT-6735
type: literature
title: "Solving a 676-bit Discrete Logarithm Problem in GF(36n ) Takuya Hayashi1"
authors:
  - "Masaaki Shirase"
  - "Tsuyoshi Takagi⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [binary-field, dlp, elliptic-curve, mov-fr, pairing, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Pairings on elliptic curves over finite fields are crucial for constructing various cryptographic schemes. The ηT pairing on supersingular curves over GF(3n ) is particularly popular since it is efficiently implementable.

## Key claims (as reported)
- Taking into account the Menezes-Okamoto-Vanstone (MOV) attack, the discrete logarithm problem (DLP) in GF(36n ) becomes a concern for the security of cryptosystems using ηT pairings in this case.
- In 2006, Joux and Lercier proposed a new variant of the function field sieve in the medium prime case, named JL06-FFS.
- We have, however, not yet found any practical implementations on JL06-FFS over GF(36n ).
- Therefore, we first fulfill such an implementation and we successfully set a new record for solving the DLP in GF(36n ), the DLP in GF(36·71 ) of 676bit size.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/60560355 (1).pdf`
- `downloads/60560355 (2).pdf`
- `downloads/60560355 (3).pdf`
- `downloads/60560355 (4).pdf`
- `downloads/60560355.pdf`
