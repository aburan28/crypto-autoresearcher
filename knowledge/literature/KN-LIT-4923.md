---
id: KN-LIT-4923
type: literature
title: "Mind the Gap: Modular Machine-checked"
authors:
  - "Yassine Lakhnech"
  - "Benedikt Schmidt"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, elliptic-curve, protocol, provable-security, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Using EasyCrypt, we formalize a new modular security proof for one-round authenticated key exchange protocols in the random oracle model. Our proof improves earlier work by Kudla and Paterson (ASIACRYPT 2005) in three significant ways: we consider a stronger adversary model, we provide support tailored to protocols that utilize the Naxos trick, and we support proofs under the Computational DH assumption not relying on Gap oracles.

## Key claims (as reported)
- Furthermore, our modular proof can be used to obtain concrete security proofs for protocols with or without adversarial key registration.
- We use this support to investigate, still using EasyCrypt, the connection between proofs without Gap assumptions and adversarial key registration.
- For the case of honestly generated keys, we obtain the first proofs of the Naxos and Nets protocols under the Computational DH assumption.
- For the case of adversarial key registration, we obtain machine-checked and modular variants of the well-known proofs for Naxos, Nets, and Naxos+.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/90560219 (1).pdf`
- `downloads/90560219.pdf`
