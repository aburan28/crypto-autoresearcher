---
id: KN-LIT-6270
type: literature
title: "Revisiting the Indifferentiability of the Sum of Permutations"
authors:
  - "Aldo Gunsing"
  - "Ritam Bhaumik"
  - "Ashwin Jha"
  - "Bart Mennink"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The sum of two n-bit pseudorandom permutations is known to behave like a pseudorandom function with n bits of security. A recent line of research has investigated the security of two public n-bit permutations and its degree of indifferentiability.

## Key claims (as reported)
- (INDOCRYPT 2010) proved 2n/3-bit security, Mennink and Preneel (ACNS 2015) pointed out a non-trivial flaw in their analysis and re-proved (2n/3 − log2 (n))-bit security.
- Bhattacharya and Nandi (EUROCRYPT 2018) eventually improved the result to n-bit security.
- Recently, Gunsing at CRYPTO 2022 already observed that a proof technique used in this line of research only holds for sequential indifferentiability.
- We revisit the line of research in detail, and observe that the strongest bound of n-bit security has two other serious issues in the reasoning, the first one is actually the same non-trivial flaw that was present in the work of Mandal et al., while the second one discards biases in the randomness influenced by the distinguisher.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850099 (1).pdf`
- `downloads/140850099.pdf`
