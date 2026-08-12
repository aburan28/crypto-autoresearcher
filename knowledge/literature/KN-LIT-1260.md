---
id: KN-LIT-1260
type: literature
title: "LIT-SiGamal: An efficient isogeny-based PKE based on a LIT diagram"
authors:
  - "Tomoki Moriya"
  - "Miha Stopar"
year: 2024
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2024/521"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2024/521"
tags: [abelian-variety, dlp, elliptic-curve, isogeny, pqc, protocol, sidh-csidh, signature, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose LIT-SiGamal, a novel isogeny-based public key encryption (PKE) scheme that combines the structure of SiGamal with the recently introduced LIT diagram framework. While SiGamal relies on a commutative CSIDH-based diagram involving an auxiliary point, LIT-SiGamal replaces this with a LIT diagram – a commutative diagram consisting of large-degree horizontal isogenies and relatively low-degree vertical isogenies.

## Key claims (as reported)
- LIT-SiGamal is an efficient and secure isogeny-based PKE scheme.
- Our analysis suggests that it is more efficient than QFESTA, proposed by Nakagawa and Onuki.
- Although LIT-SiGamal appears to be less efficient than POKÉ, proposed by Basso and Maino, it offers stronger security guarantees.
- Moreover, we provide a Rust implementation of LITSiGamal, which represents the first low-level language implementation of an isogeny-based PKE scheme developed after the break of SIDH.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2024-521.pdf`
