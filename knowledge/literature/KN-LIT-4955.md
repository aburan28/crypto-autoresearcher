---
id: KN-LIT-4955
type: literature
title: "More Efficient Constant-Round Multi-Party Computation from BMR and SHE"
authors:
  - "Yehuda Lindell"
  - "Nigel P. Smart"
  - "Eduardo Soria-Vazquez"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, mpc, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a multi-party computation protocol in the case of dishonest majority which has very low round complexity. Our protocol sits philosophically between Gentry’s Fully Homomorphic Encryption based protocol and the SPDZ-BMR protocol of Lindell et al (CRYPTO 2015).

## Key claims (as reported)
- Our protocol avoids various inefficiencies of the previous two protocols.
- Compared to Gentry’s protocol we only require Somewhat Homomorphic Encryption (SHE).
- Whilst in comparison to the SPDZ-BMR protocol we require only a quadratic complexity in the number of players (as opposed to cubic), we have fewer rounds, and we require less proofs of correctness of ciphertexts.
- Additionally, we present a variant of our protocol which trades the depth of the garbling circuit (computed using SHE) for some more multiplications in the offline and online phases.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/99850108 (1).pdf`
- `downloads/99850108.pdf`
