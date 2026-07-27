---
id: KN-LIT-2718
type: literature
title: "BiTR: Built-in Tamper Resilience"
authors:
  - "Seung Geol Choi"
  - "Aggelos Kiayias"
  - "Tal Malkin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, provable-security, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The assumption of the availability of tamper-proof hardware tokens has been used extensively in the design of cryptographic primitives. For example, Katz (Eurocrypt 2007) suggests them as an alternative to other setup assumptions, towards achieving general UC-secure multi-party computation.

## Key claims (as reported)
- On the other hand, a lot of recent research has focused on protecting security of various cryptographic primitives against physical attacks such as leakage and tampering.
- In this paper we put forward the notion of Built-in Tamper Resilience (BiTR) for cryptographic protocols, capturing the idea that the protocol that is encapsulated in a hardware token is designed in such a way so that tampering gives no advantage to an adversary.
- Our definition is within the UC model, and can be viewed as unifying and extending several prior related works.
- We provide a composition theorem for BiTR security of protocols, impossibility results, as well as several BiTR constructions for specific cryptographic protocols or tampering function classes.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/70730732 (1).pdf`
- `downloads/70730732 (2).pdf`
- `downloads/70730732 (3).pdf`
- `downloads/70730732.pdf`
