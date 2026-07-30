---
id: KN-LIT-1183
type: literature
title: "Two Remarks on Torsion-Point Attacks in Isogeny-Based Cryptography"
authors:
  - "Francesco Sica"
year: 2023
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2023/1229"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2023/1229"
tags: [elliptic-curve, endomorphism, finite-field, isogeny, pairing, pqc, sidh-csidh, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We fix an omission in [8] on torsion point attacks of isogenybased cryptosystems akin to SIDH, also reprised in [2, 4]. In these works, their authors represent certain integers using a norm equation to derive a secret isogeny.

## Key claims (as reported)
- However, this derivation uses as a crucial ingredient [8, Section 4.3, Lemma 6], which we show to be incorrect.
- We then state sufficient conditions allowing to prove a modified version this lemma.
- A further idea of parametrizing solutions of the norm equation will show that these conditions can be fulfilled under the same heuristics of these previous works.
- Our contribution is a theoretical one.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2023-1229.pdf`
