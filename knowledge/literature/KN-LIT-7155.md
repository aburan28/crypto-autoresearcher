---
id: KN-LIT-7155
type: literature
title: "Tightly-Secure Authenticated Key Exchange, Revisited"
authors:
  - "Tibor Jager"
  - "Eike Kiltz"
  - "Doreen Riepel"
  - "Sven Schäge"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, protocol, provable-security, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce new tightly-secure authenticated key exchange (AKE) protocols that are extremely efficient, yet have only a constant security loss and can be instantiated in the random oracle model both from the standard DDH assumption and a subgroup assumption over RSA groups. These protocols can be deployed with optimal parameters, independent of the number of users or sessions, without the need to compensate a security loss with increased parameters and thus decreased computational efficiency.

## Key claims (as reported)
- We use the standard “Single-Bit-Guess” AKE security (with forward secrecy and state corruption) requiring all challenge keys to be simultaneously pseudo-random.
- In contrast, most previous papers on tightly secure AKE protocols (Bader et al., TCC 2015; Gjøsteen and Jager, CRYPTO 2018; Liu et al., ASIACRYPT 2020) concentrated on a non-standard “Multi-Bit-Guess” AKE security which is known not to compose tightly with symmetric primitives to build a secure communication channel.
- Our key technical contribution is a new generic approach to construct tightly-secure AKE protocols based on non-committing key encapsulation mechanisms.
- The resulting DDH-based protocols are considerably more efficient than all previous constructions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/126960088 (1).pdf`
- `downloads/126960088.pdf`
