---
id: KN-LIT-7135
type: literature
title: "Tight Security Bounds for Micali’s SNARGs"
authors:
  - "Alessandro Chiesa"
  - "Eylon Yogev"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, pqc, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Succinct non-interactive arguments (SNARGs) in the random oracle model (ROM) have several attractive features: they are plausibly post-quantum; they can be heuristically instantiated via lightweight cryptography; and they have a transparent (public-coin) parameter setup. The canonical construction of a SNARG in the ROM is due to Micali (FOCS 1994), who showed how to use a random oracle to compile any probabilistically checkable proof (PCP) with sufficiently-small soundness error into a corresponding SNARG.

## Key claims (as reported)
- Yet, while Micali’s construction is a seminal result, it has received little attention in terms of analysis in the past 25 years.
- In this paper, we observe that prior analyses of the Micali construction are not tight and then present a new analysis that achieves tight security bounds.
- Our result enables reducing the random oracle’s output size, and obtain corresponding savings in concrete argument size.
- Departing from prior work, our approach relies on precisely quantifying the cost for an attacker to find several collisions and inversions in the random oracle, and proving that any PCP with small soundness error withstands attackers that succeed in finding a small number of collisions and inversions in a certain tree-based information-theoretic game.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/130420149 (1).pdf`
- `downloads/130420149.pdf`
