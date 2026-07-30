---
id: KN-LIT-7101
type: literature
title: "Three’s Compromised Too: Circular Insecurity for Any Cycle Length from (Ring-)LWE"
authors:
  - "Navid Alamati"
  - "Chris Peikert"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A public-key encryption scheme is k-circular secure if a cycle of k encrypted secret keys (Encpk1 (sk2 ), Encpk2 (sk3 ), . . . , Encpkk (sk1 )) is indistinguishable from encryptions of zeros. Circular security has applications in a wide variety of settings, ranging from security of symbolic protocols to fully homomorphic encryption.

## Key claims (as reported)
- A fundamental question is whether standard security notions like IND-CPA/CCA imply k-circular security.
- For the case k = 2, several works over the past years have constructed counterexamples—i.e., schemes that are CPA or even CCA secure but not 2-circular secure—under a variety of well-studied assumptions (SXDH, decision linear, and LWE).
- However, for k > 2 the only known counterexamples are based on strong general-purpose obfuscation assumptions.
- In this work we construct k-circular security counterexamples for any k ≥ 2 based on (ring-)LWE.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/98150646 (1).pdf`
- `downloads/98150646.pdf`
