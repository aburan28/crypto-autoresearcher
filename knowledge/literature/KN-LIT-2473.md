---
id: KN-LIT-2473
type: literature
title: "An Efficient CDH-based Signature Scheme"
authors:
  - "With a Tight Security Reduction"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, elliptic-curve, factoring, hash, pairing, provable-security, quantum, rsa, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
At Eurocrypt ’03, Goh and Jarecki showed that, contrary to other signature schemes in the discrete-log setting, the EDL signature scheme has a tight security reduction, namely to the Computational Diffie-Hellman (CDH) problem, in the Random Oracle (RO) model. They also remarked that EDL can be turned into an off-line/on-line signature scheme using the technique of Shamir and Tauman, based on chameleon hash functions.

## Key claims (as reported)
- In this paper, we propose a new signature scheme that also has a tight security reduction to CDH but whose resulting signatures are smaller than EDL signatures.
- Further, similarly to the Schnorr signature scheme (but contrary to EDL), our signature is naturally efficient on-line: no additional trick is needed for the off-line phase and the verification process is unchanged.
- For example, in elliptic curve groups, our scheme results in a 25% improvement on the state-of-the-art discrete-log based schemes, with the same security level.
- This represents to date the most efficient scheme of any signature scheme with a tight security reduction in the discrete-log setting.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/36210507 (1).pdf`
- `downloads/36210507 (2).pdf`
- `downloads/36210507 (3).pdf`
- `downloads/36210507.pdf`
