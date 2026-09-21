---
id: KN-LIT-3515
type: literature
title: "Efficient Adaptively-Secure IB-KEMs and VRFs via Near-Collision Resistance?"
authors:
  - "Tibor Jager"
  - "Rafael Kurek"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, lattice, pairing, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct more efficient cryptosystems with provable security against adaptive attacks, based on simple and natural hardness assumptions in the standard model. Concretely, we describe: – An adaptively-secure variant of the efficient, selectively-secure LWEbased identity-based encryption (IBE) scheme of Agrawal, Boneh, and Boyen (EUROCRYPT 2010).

## Key claims (as reported)
- In comparison to the previously most efficient such scheme by Yamada (CRYPTO 2017) we achieve smaller lattice parameters and shorter public keys of size O(log λ), where λ is the security parameter. – Adaptively-secure variants of two efficient selectively-secure pairingbased IBEs of Boneh and Boyen (EUROCRYPT 2004).
- One is based on the DBDH assumption, has the same ciphertext size as the corresponding BB04 scheme, and achieves full adaptive security with public parameters of size only O(log λ).
- The other is based on a qtype assumption and has public key size O(λ), but a ciphertext is only a single group element and the security reduction is quadratically tighter than the corresponding scheme by Jager and Kurek (ASIACRYPT 2018). – A very efficient adaptively-secure verifiable random function where proofs, public keys, and secret keys have size O(log λ).
- As a technical contribution we introduce blockwise partitioning, which leverages the assumption that a cryptographic hash function is weak near-collision resistant to prove full adaptive security of cryptosystems.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/127110187 (1).pdf`
- `downloads/127110187.pdf`
