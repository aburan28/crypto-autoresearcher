---
id: KN-LIT-2880
type: literature
title: "Chopsticks: Fork-Free Two-Round Multi-Signatures from Non-Interactive Assumptions"
authors:
  - "Jiaxin Pan"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, pairing, provable-security, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Multi-signatures have been drawing lots of attention in recent years, due to their applications in cryptocurrencies. Most early constructions require three-round signing, and recent constructions have managed to reduce the round complexity to two.

## Key claims (as reported)
- However, their security proofs are mostly based on non-standard, interactive assumptions (e.g. one-more assumptions) and come with a huge security loss, due to multiple uses of rewinding (aka the Forking Lemma).
- This renders the quantitative guarantees given by the security proof useless.
- In this work, we improve the state of the art by proposing two efficient two-round multi-signature schemes from the (standard, non-interactive) Decisional Diffie-Hellman (DDH) assumption.
- Both schemes are proven secure in the random oracle model without rewinding.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14004058 (1).pdf`
- `downloads/14004058.pdf`
