---
id: KN-LIT-5896
type: literature
title: "Privacy Amplification in the Isolated Qubits Model Yi-Kai Liu"
authors:
  - "Computational Mathematics Division"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mov-fr, mpc, pairing, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Isolated qubits are a special class of quantum devices, which can be used to implement tamper-resistant cryptographic hardware such as one-time memories (OTM’s). Unfortunately, these OTM constructions leak some information, and standard methods for privacy amplification cannot be applied here, because the adversary has advance knowledge of the hash function that the honest parties will use.

## Key claims (as reported)
- In this paper we show a stronger form of privacy amplification that solves this problem, using a fixed hash function that is secure against all possible adversaries in the isolated qubits model.
- This allows us to construct single-bit OTM’s which only leak an exponentially small amount of information.
- We then study a natural generalization of the isolated qubits model, where the adversary is allowed to perform a polynomially-bounded number of entangling gates, in addition to unbounded local operations and classical communication (LOCC).
- We show that our technique for privacy amplification is also secure in this setting.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/90560211 (1).pdf`
- `downloads/90560211.pdf`
