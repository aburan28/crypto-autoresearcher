---
id: KN-LIT-6117
type: literature
title: "Rai-Choo! Evolving Blind Signatures to the Next Level"
authors:
  - "Lucjan Hanzlik"
  - "Julian Loss"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, mov-fr, pairing, provable-security, quantum, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Blind signatures are a fundamental tool for privacy-preserving applications. Known constructions of concurrently secure blind signature schemes either are prohibitively inefficient or rely on non-standard assumptions, even in the random oracle model.

## Key claims (as reported)
- A recent line of work (ASIACRYPT ‘21, CRYPTO ‘22) initiated the study of concretely efficient schemes based on well-understood assumptions in the random oracle model.
- However, these schemes still have several major drawbacks: 1) The signer is required to keep state; 2) The computation grows linearly with the number of signing interactions, making the schemes impractical; 3) The schemes require at least five moves of interaction.
- In this paper, we introduce a blind signature scheme that eliminates all of the above drawbacks at the same time.
- Namely, we show a round-optimal, concretely efficient, concurrently secure, and stateless blind signature scheme in which communication and computation are independent of the number of signing interactions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14004125 (1).pdf`
- `downloads/14004125.pdf`
