---
id: KN-LIT-2612
type: literature
title: "Attacking the Knudsen-Preneel Compression Functions"
authors:
  - "Onur Özen"
  - "Thomas Shrimpton"
  - "Martijn Stam"
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, hash, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Knudsen and Preneel (Asiacrypt’96 and Crypto’97) introduced a hash function design in which a linear error-correcting code is used to build a wide-pipe compression function from underlying blockciphers operating in Davies-Meyer mode. In this paper, we (re)analyse the preimage resistance of the Knudsen-Preneel compression functions in the setting of public random functions.

## Key claims (as reported)
- We give a new non-adaptive preimage attack, beating the one given by Knudsen and Preneel, that is optimal in terms of query complexity.
- Moreover, our new attack falsifies their (conjectured) preimage resistance security bound and shows that intuitive bounds based on the number of ‘active’ components can be treacherous.
- Complementing our attack is a formal analysis of the query complexity (both lower and upper bounds) of preimage-finding attacks.
- This analysis shows that for many concrete codes the time complexity of our attack is optimal.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/61470096 (1).pdf`
- `downloads/61470096 (2).pdf`
- `downloads/61470096 (3).pdf`
- `downloads/61470096.pdf`
