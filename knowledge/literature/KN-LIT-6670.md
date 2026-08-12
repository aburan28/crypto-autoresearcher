---
id: KN-LIT-6670
type: literature
title: "Simpler Statistically Sender Private Oblivious Transfer from Ideals of Cyclotomic Integers ?"
authors:
  - "Daniele Micciancio"
  - "Jessica Sorrell"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mov-fr, mpc, number-theory, provable-security, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a two-message oblivious transfer protocol achieving statistical sender privacy and computational receiver privacy based on the RLWE assumption for cyclotomic number fields. This work improves upon prior lattice-based statistically sender-private oblivious transfer protocols by reducing the total communication between parties by a factor O(n log q) for transfer of length O(n) messages.

## Key claims (as reported)
- Prior work of Brakerski and Döttling uses transference theorems to show that either a lattice or its dual must have short vectors, the existence of which guarantees lossy encryption for encodings with respect to that lattice, and therefore statistical sender privacy.
- In the case of ideal lattices from embeddings of cyclotomic integers, the existence of one short vector implies the existence of many, and therefore encryption with respect to either a lattice or its dual is guaranteed to “lose” more information about the message than can be ensured in the case of general lattices.
- This additional structure of ideals of cyclotomic integers allows for efficiency improvements beyond those that are typical when moving from the generic to ideal lattice setting, resulting in smaller message sizes for sender and receiver, as well as a protocol that is simpler to describe and analyze.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12491398 (1).pdf`
- `downloads/12491398.pdf`
