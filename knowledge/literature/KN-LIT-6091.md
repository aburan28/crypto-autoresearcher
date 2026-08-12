---
id: KN-LIT-6091
type: literature
title: "Quantum Indistinguishability of Random Sponges"
authors:
  - "Jan Czajkowski"
  - "Andreas Hülsing"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, hash, pairing, pqc, provable-security, quantum, rsa, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this work we show that the sponge construction can be used to construct quantum-secure pseudorandom functions. As our main result we prove that random sponges are quantum indistinguishable from random functions.

## Key claims (as reported)
- In this setting the adversary is given superposition access to the input-output behavior of the construction but not to the internal function.
- Our proofs hold under the assumption that the internal function is a random function or permutation.
- We then use this result to obtain a quantum-security version of a result by Andreeva, Daemen, Mennink, and Van Assche (FSE’15) which shows that a sponge that uses a secure PRP or PRF as internal function is a secure PRF.
- This result also proves that the recent attacks against CBC-MAC in the quantum-access model by Kaplan, Leurent, Leverrier, and NayaPlasencia (Crypto’16) and Santoli, and Schaffner (QIC’16) can be prevented by introducing a state with a non-trivial inner part.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/116940225 (1).pdf`
- `downloads/116940225.pdf`
