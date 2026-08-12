---
id: KN-LIT-827
type: literature
title: "Towards Post-Quantum Key-Updatable Public-Key Encryption via Supersingular Isogenies"
authors:
  - "Edward Eaton"
  - "David Jao"
  - "Chelsea Komlo"
  - "Youcef Mokrani"
year: 2020
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2020/1593"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2020/1593"
tags: [class-group, dlp, isogeny, lattice, number-theory, pqc, protocol, sidh-csidh, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present the first post-quantum secure Key-Updatable Public-Key Encryption (UPKE) construction. UPKE has been proposed as a mechanism to improve the forwardsecrecy and post-compromise security of secure messaging protocols, but the hardness of all existing constructions rely on discrete logarithm assumptions.

## Key claims (as reported)
- We focus our assessment on isogeny-based cryptosystems due to their suitability for performing a potentially unbounded number of update operations, a practical requirement for secure messaging where user conversations can occur over months, if not years.
- We begin by formalizing two UPKE variants in the literature as Symmetric and Asymmetric UPKE, which differ in how encryption and decryption keys are updated.
- We argue that Asymmetric UPKE constructions in the literature cannot be straightforwardly instantiated using SIDH nor CSIDH.
- We then describe a SIDH construction that partially achieves the required security notions for Symmetric UPKE, but due to existing mathematical limitations, cannot provide fine-grained forward secrecy.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2020-1593.pdf`
