---
id: KN-LIT-5095
type: literature
title: "New Chosen-Ciphertext Attacks on NTRU"
authors:
  - "Nicolas Gama"
  - "Phong Q. Nguyen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, dlp, lattice, mov-fr, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present new and efficient key-recovery chosen-ciphertext attacks on NTRUencrypt. Our attacks are somewhat intermediate between chosen-ciphertext attacks on NTRUencrypt previously published at CRYPTO ’00 and CRYPTO ’03.

## Key claims (as reported)
- Namely, the attacks only work in the presence of decryption failures; we only submit valid ciphertexts to the decryption oracle, where the plaintexts are chosen uniformly at random; and the number of oracle queries is small.
- Interestingly, our attacks can also be interpreted from a provable security point of view: in practice, if one had access to a NTRUencrypt decryption oracle such that the parameter set allows decryption failures, then one could recover the secret key.
- For instance, for the initial NTRU-1998 parameter sets, the output of the decryption oracle on a single decryption failure is enough to recover the secret key.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/44500089 (1).pdf`
- `downloads/44500089 (2).pdf`
- `downloads/44500089 (3).pdf`
- `downloads/44500089.pdf`
