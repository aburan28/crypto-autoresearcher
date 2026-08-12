---
id: KN-LIT-7148
type: literature
title: "Tightly Secure CCA-Secure Encryption without Pairings"
authors:
  - "Romain Gay"
  - "Dennis Hofheinz"
  - "Eike Kiltz"
  - "Hoeteck Wee"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present the first CCA-secure public-key encryption scheme based on DDH where the security loss is independent of the number of challenge ciphertexts and the number of decryption queries. Our construction extends also to the standard k-Lin assumption in pairing-free groups, whereas all prior constructions starting with Hofheinz and Jager (Crypto ’12) rely on the use of pairings.

## Key claims (as reported)
- Moreover, our construction improves upon the concrete efficiency of existing schemes, reducing the ciphertext overhead by about half (to only 3 group elements under DDH), in addition to eliminating the use of pairings.
- We also show how to use our techniques in the NIZK setting.
- Specifically, we construct the first tightly simulation-sound designated-verifier NIZK for linear languages without pairings.
- Using pairings, we can turn our construction into a highly optimized publicly verifiable NIZK with tight simulation-soundness.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/96650288 (1).pdf`
- `downloads/96650288.pdf`
