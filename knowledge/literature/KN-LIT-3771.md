---
id: KN-LIT-3771
type: literature
title: "Failing gracefully: Decryption failures and the Fujisaki-Okamoto transform"
authors:
  - "Kathrin Hövelmanns"
  - "Andreas Hülsing"
  - "Christian Majenz"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pqc, provable-security, quantum, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In known security reductions for the Fujisaki-Okamoto transformation, decryption failures are handled via a reduction solving the rather unnatural task of finding failing plaintexts given the private key, resulting in a Grover search bound. Moreover, they require an implicit rejection mechanism for invalid ciphertexts to achieve a reasonable security bound in the QROM.

## Key claims (as reported)
- We present a reduction that has neither of these deficiencies: We introduce two security games related to finding decryption failures, one capturing the computationally hard task of using the public key to find a decryption failure, and one capturing the statistically hard task of searching the random oracle for key-independent failures like, e.g., large randomness.
- As a result, our security bounds in the QROM are tighter than previous ones with respect to the generic random oracle search attacks: The attacker can only partially compute the search predicate, namely for said key-independent failures.
- In addition, our entire reduction works for the explicit-reject variant of the transformation and improves significantly over all of its known reductions.
- Besides being the more natural variant of the transformation, security of the explicit reject mechanism is also relevant for side channel attack resilience of the implicit-rejection variant.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137910138 (1).pdf`
- `downloads/137910138.pdf`
