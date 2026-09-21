---
id: KN-LIT-3617
type: literature
title: "Efficient Public-Key Cryptography with Bounded"
authors:
  - "Tamper Resilience"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [finite-field, pairing, provable-security, quantum, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We revisit the question of constructing public-key encryption and signature schemes with security in the presence of bounded leakage and tampering memory attacks. For signatures we obtain the first construction in the standard model; for public-key encryption we obtain the first construction free of pairing (avoiding non-interactive zero-knowledge proofs).

## Key claims (as reported)
- Our constructions are based on generic building blocks, and, as we show, also admit efficient instantiations under fairly standard numbertheoretic assumptions.
- The model of bounded tamper resistance was recently put forward by Damgård et al.
- (Asiacrypt 2013) as an attractive path to achieve security against arbitrary memory tampering attacks without making hardware assumptions (such as the existence of a protected self-destruct or key-update mechanism), the only restriction being on the number of allowed tampering attempts (which is a parameter of the scheme).
- This allows to circumvent known impossibility results for unrestricted tampering (Gennaro et al., TCC 2010), while still being able to capture realistic tampering attacks.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10031257 (1).pdf`
- `downloads/10031257.pdf`
