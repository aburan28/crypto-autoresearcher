---
id: KN-LIT-3759
type: literature
title: "Efficient Circuit-Size Independent Public Key Encryption with KDM Security"
authors:
  - "Tal Malkin"
  - "Isamu Teranishi"
  - "Moti Yung"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Key Dependent Message (KDM) secure encryption is a new area which has attracted much research in recent years. Roughly speaking, a KDM secure scheme w.r.t. a function set F provides security even if one encrypts a key dependent message f (sk ) for any f ∈ F .

## Key claims (as reported)
- We present a construction of an efficient public key encryption scheme which is KDM secure with respect to a large function set F.
- Our function set is a function computable by a polynomial-size Modular Arithmetic Circuit (MAC); we represent the set as Straight Line Programs computing multi-variable polynomials (an extended scheme includes all rational functions whose denominator and numerator are functions as above).
- Unlike previous schemes, our scheme is what we call flexible: the size of the ciphertext depends on the degree bound for the polynomials, and beyond this all parameters of the scheme are completely independent of the size of the function or the number of secret keys (users).
- We note that although KDM security has practical applications, all previous works in the standard model are either inefficient feasibility results when dealing with general circuits function sets, or are for a small set of functions such as linear functions.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/66320511 (1).pdf`
- `downloads/66320511 (2).pdf`
- `downloads/66320511 (3).pdf`
- `downloads/66320511.pdf`
