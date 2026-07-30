---
id: KN-LIT-2541
type: literature
title: "Anonymity of NIST PQC Round-3 KEMs"
authors:
  - "Keita Xagawa"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, pqc, protocol, provable-security, sidh-csidh]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper investigates anonymity of all NIST PQC Round 3 KEMs: Classic McEliece, Kyber, NTRU, Saber, BIKE, FrodoKEM, HQC, NTRU Prime (Streamlined NTRU Prime and NTRU LPRime), and SIKE. We show the following results: – NTRU is anonymous in the quantum random oracle model (QROM) if the underlying deterministic PKE is strongly disjoint-simulatable.

## Key claims (as reported)
- NTRU is collision-free in the QROM.
- A hybrid PKE scheme constructed from NTRU as KEM and appropriate DEM is anonymous and robust.
- (Similar results for BIKE, FrodoKEM, HQC, NTRU LPRime, and SIKE hold except one of three parameter sets of HQC.) – Classic McEliece is anonymous in the QROM if the underlying PKE is strongly disjoint-simulatable and a hybrid PKE scheme constructed from it as KEM and appropriate DEM is anonymous. – Grubbs, Maram, and Paterson pointed out that Kyber and Saber have a gap in the current IND-CCA security proof in the QROM (EUROCRYPT 2022).
- We found that Streamlined NTRU Prime has another technical obstacle for the IND-CCA security proof in the QROM.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/132760209 (1).pdf`
- `downloads/132760209.pdf`
