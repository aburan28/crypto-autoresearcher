---
id: KN-LIT-4984
type: literature
title: "Multi-Identity and Multi-Key Leveled FHE from Learning with Errors"
authors:
  - "Michael Clear"
  - "Ciarán McGoldrick"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, mpc, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Gentry, Sahai and Waters recently presented the first (leveled) identity-based fully homomorphic (IBFHE) encryption scheme (CRYPTO 2013). Their scheme however only works in the single-identity setting; that is, homomorphic evaluation can only be performed on ciphertexts created with the same identity.

## Key claims (as reported)
- In this work, we extend their results to the multi-identity setting and obtain a multi-identity IBFHE scheme that is selectively secure in the random oracle model under the hardness of Learning with Errors (LWE).
- We also obtain a multi-key fullyhomomorphic encryption (FHE) scheme that is secure under LWE in the standard model.
- This is the first multi-key FHE based on a wellestablished assumption such as standard LWE.
- The multi-key FHE of López-Alt, Tromer and Vaikuntanathan (STOC 2012) relied on a nonstandard assumption, referred to as the Decisional Small Polynomial Ratio assumption.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92160237 (1).pdf`
- `downloads/92160237 (2).pdf`
- `downloads/92160237.pdf`
