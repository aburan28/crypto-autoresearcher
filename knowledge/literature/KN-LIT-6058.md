---
id: KN-LIT-6058
type: literature
title: "QCCA-Secure Generic Transformations in the Quantum Random Oracle Model"
authors:
  - "Tianshu Shan"
  - "Jiangxia Ge"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, pqc, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The post-quantum security of cryptographic schemes assumes that the quantum adversary only receives the classical result of computations with the secret key. Further, it is unknown whether the postquantum secure schemes still remain secure if the adversary can obtain a superposition state of the results.

## Key claims (as reported)
- In this paper, we formalize one class of public-key encryption schemes named oracle-masked schemes.
- Then we define the plaintext extraction procedure for those schemes and this procedure simulates the quantumaccessible decryption oracle with a certain loss.
- The construction of the plaintext extraction procedure does not need to take the secret key as input.
- Based on this property, we prove the IND-qCCA security of the Fujisaki-Okamoto (FO) transformation in the quantum random oracle model (QROM) and our security proof is tighter than the proof given by Zhandry (Crypto 2019).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/13940133 (1).pdf`
- `downloads/13940133.pdf`
