---
id: KN-LIT-2789
type: literature
title: "Breaking and Repairing GCM Security Proofs"
authors:
  - "Tetsu Iwata"
  - "Keisuke Ohashi"
  - "Kazuhiko Minematsu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, provable-security, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we study the security proofs of GCM (Galois/Counter Mode of Operation). We first point out that a lemma, which is related to the upper bound on the probability of a counter collision, is invalid.

## Key claims (as reported)
- Both the original privacy and authenticity proofs by the designers are based on the lemma.
- We further show that the observation can be translated into a distinguishing attack that invalidates the main part of the privacy proof.
- It turns out that the original security proofs of GCM contain a flaw, and hence the claimed security bounds are not justified.
- A very natural question is then whether the proofs can be repaired.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/74170032 (1).pdf`
- `downloads/74170032 (2).pdf`
- `downloads/74170032 (3).pdf`
- `downloads/74170032 (4).pdf`
- `downloads/74170032 (5).pdf`
- `downloads/74170032.pdf`
