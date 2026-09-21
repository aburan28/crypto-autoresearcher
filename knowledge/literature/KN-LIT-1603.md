---
id: KN-LIT-1603
type: literature
title: "Constant-Online PVSS from CCA2-Secure Threshold Encryption: A Generic Framework"
authors:
  - "Liang Zhang"
  - "Dongliang Cai"
  - "Haibin Kan"
  - "Jiheng Zhang"
  - "Moti Yung"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1009"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1009"
tags: [mov-fr, mpc, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Publicly Verifiable Secret Sharing (PVSS) is widely used in distributed systems. Existing schemes usually incur at least O(n) online cost: the dealer encrypts, proves, and publishes n shareholder-dependent objects, which public verification must process.

## Key claims (as reported)
- In this work, we present a generic framework that transforms publicly verifiable CCA2-secure threshold encryption (CCATE) into constant-online PVSS, with distribution and public- verification costs independent of the number of shareholders.
- The framework moves the share-generation work into a reusable setup phase: once threshold keys and public verification material are fixed, online sharing amounts to a single publicly verifiable threshold encryption.
- We instantiate the framework with two CCATE constructions: 1) a pairing-free instantiation using standard Threshold ElGamal encryption under a committee-based setup assumption; and 2) a silent-setup scheme leveraging non-interactive key generation via a Power-of-Tau ceremony, eliminating inter-party coordination during setup.
- Furthermore, we discuss epoch-based membership updates under the corresponding setup assumptions, clarifying the security boundary of reconfiguration.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1009.pdf`
