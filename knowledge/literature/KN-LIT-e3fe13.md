---
id: KN-LIT-e3fe13
type: literature
title: "An IND-CCA2 attack against the 1st- and 2nd-round versions of NTS-KEM"
authors:
  - "Tung Chou"
year: 2020
venue: "SecITC"
identifiers:
  eprint: null
  doi: "10.1007/978-3-030-69255-1_11"
  arxiv: null
  url: "https://tungchou.github.io/papers/ntskem_cca2.pdf"
tags: [cca, kem, provable-security, code-based, nts-kem, ind-cca2, nist-pqc, attack]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
An **IND-CCA2 attack against the first- and second-round versions of NTS-KEM**,
a NIST post-quantum candidate closely related to Classic McEliece. The attack
targets the CCA transform, not the underlying code problem: the one-way
primitive was fine, and the conversion to a CCA-secure KEM was not.

## Key claims (as reported)
- The round-1 and round-2 NTS-KEM specifications do not achieve IND-CCA2.
- The failure is in the KEM construction, not in the hardness of decoding.

## Relevance to this program
The concrete justification for this bibliography having a chosen-ciphertext
section at all. A scheme reached round 2 of a global standardisation process
with a broken CCA transform — **review at that level of scrutiny still missed
it.**

The lesson this program takes is about composition: the security of a system is
not the security of its hardest component. This program's own conclusions are
required to cite the specific experiment and evidence IDs supporting them
(rule 6) precisely so that a claim about one layer is never silently read as a
claim about the composed system.

## Not verified here
citation verified against the Crossref record (DOI 10.1007/978-3-030-69255-1_11).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The attack's mechanism and its cost are NOT recorded here. Whether the final
NTS-KEM specification repaired it is likewise not assessed. Note that Classic
McEliece is a **different** submission; nothing in this entry states anything
about Classic McEliece's CCA security.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
