---
id: KN-LIT-5703
type: literature
title: "Overtaking VEST"
authors:
  - "Antoine Joux"
  - "Jean-René Reinhard"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
VEST is a set of four stream cipher families submitted by S. Landman to the eSTREAM call for stream cipher proposals of the European project ECRYPT.

## Key claims (as reported)
- The state of any family member is made of three components: a counter, a counter diffusor and a core accumulator.
- We show that collisions can be found in the counter during the IV Setup.
- Moreover they can be combined with a collision in the linear counter diffusor to form collisions on the whole cipher.
- As a consequence, it is possible to retrieve 53 bits of the keyed state of the stream cipher by performing a chosen IV attack.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/45930055 (1).pdf`
- `downloads/45930055 (2).pdf`
- `downloads/45930055 (3).pdf`
- `downloads/45930055.pdf`
