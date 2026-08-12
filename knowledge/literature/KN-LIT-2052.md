---
id: KN-LIT-2052
type: literature
title: "A Framework for Achieving KDM-CCA Secure Public-Key Encryption"
authors:
  - "Fuyuki Kitagawa"
  - "Keisuke Tanaka"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose a framework for achieving a public-key encryption (PKE) scheme that satisfies key dependent message security against chosen ciphertext attacks (KDM-CCA security) based on projective hash function. Our framework can be instantiated under the decisional diffiehellman (DDH), quadratic residuosity (QR), and decisional composite residuosity (DCR) assumptions.

## Key claims (as reported)
- The constructed schemes are KDMCCA secure with respect to affine functions and compatible with the amplification method shown by Applebaum (EUROCRYPT 2011).
- Thus, they lead to PKE schemes satisfying KDM-CCA security for all functions computable by a-priori bounded size circuits.
- They are the first PKE schemes satisfying such a security notion in the standard model using neither non-interactive zero knowledge proof nor bilinear pairing.
- The above framework based on projective hash function captures only KDM-CCA security in the single user setting.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/11272177 (1).pdf`
- `downloads/11272177.pdf`
