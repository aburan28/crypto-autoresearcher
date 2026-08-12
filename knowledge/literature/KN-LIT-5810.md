---
id: KN-LIT-5810
type: literature
title: "Post-Quantum Security of the Even-Mansour Cipher"
authors:
  - "Gorjan Alagic"
  - "Chen Bai"
  - "Jonathan Katz"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, cryptanalysis, pairing, pqc, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Even-Mansour cipher is a simple method for constructing a (keyed) pseudorandom permutation E from a public random permutation P : {0, 1}n → {0, 1}n . It is secure against classical attacks, with optimal attacks requiring qE queries to E and qP queries to P such that qE · qP ≈ 2n .

## Key claims (as reported)
- If the attacker is given quantum access to both E and P , however, the cipher is completely insecure, with attacks using qE , qP = O(n) queries known.
- In any plausible real-world setting, however, a quantum attacker would have only classical access to the keyed permutation E implemented by honest parties, while retaining quantum access to P .
- Attacks in this setting with qE · qP2 ≈ 2n are known, showing that security degrades as compared to the purely classical case, but leaving open the question as to whether the Even-Mansour cipher can still be proven secure in that natural, “post-quantum” setting.
- We resolve this question, showing that any attack in that setting requires 2 ≈ 2n .

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/132760162 (1).pdf`
- `downloads/132760162.pdf`
