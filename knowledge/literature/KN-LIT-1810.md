---
id: KN-LIT-1810
type: literature
title: "Practical Amortized Bootstrapping for NTRU-Based FHE"
authors:
  - "Wun-Ting Lin"
  - "Ja-Ling Wu"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/068"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/068"
tags: [fhe, lattice, pairing, quantum, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Fully homomorphic encryption (FHE) enables computation on encrypted data. NTRU-based FHE offers compact ciphertexts—a single ring element rather than a tuple—but FINAL, the leading NTRU-based scheme, represents its ciphertexts and decryption in matrix form that hides the polynomial-ring structure on which recent automorphism-based amortized bootstrapping relies.

## Key claims (as reported)
- We reformulate FINAL in the standard polynomial-ring setting and express its decryption as coefficient-wise inner products compatible with FHEW-style accumulators.
- This preserves the required ring automorphisms and lets us adapt monomial-bypolynomial amortized bootstrapping to NTRU ciphertexts with sparse secret keys: for a secret of Hamming weight h, the dominant per-coefficient work drops from O(nlQ ) to O(hlpos ) external-product operations, where lQ and lpos denote the gadgetdecomposition lengths of the standard and position-based bootstrapping keys, respectively.
- Concrete parameters are selected by a joint optimization that combines a refined average-case noise analysis with security validation via NTRU fatigue analysis and the Lattice Estimator under sparse-secret distributions.
- Our highly optimized single-threaded C++ implementation based on Intel HEXL bootstraps a message coefficient in 2.68 ms at n = 8192—45× faster than FINAL and 2.6× faster than TFHE-rs.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-068.pdf`
