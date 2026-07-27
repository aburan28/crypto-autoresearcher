---
id: KN-LIT-4803
type: literature
title: "Lower Bound on SNARGs in the Random Oracle Model"
authors:
  - "Iftach Haitner"
  - "Daniel Nukrai"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, hash, pairing, pqc, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Succinct non-interactive arguments (SNARGs) have become a fundamental primitive in the cryptographic community. The focus of this work is constructions of SNARGs in the Random Oracle Model (ROM).

## Key claims (as reported)
- Such SNARGs enjoy post-quantum security and can be deployed using lightweight cryptography to heuristically instantiate the random oracle.
- A ROM-SNARG is (t, ε)-sound if no t-query malicious prover can convince the verifier to accept a false statement with probability larger than ε.
- Recently, Chiesa-Yogev (CRYPTO ’21) presented a ROMSNARG of length Θ(log(t/ε)·log t) (ignoring log n factors, for n being the instance size).
- This improvement, however, is still far from the (folklore) lower bound of Ω(log(t/ε)).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/135070142 (1).pdf`
- `downloads/135070142.pdf`
