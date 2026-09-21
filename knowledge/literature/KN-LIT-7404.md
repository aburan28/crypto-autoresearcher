---
id: KN-LIT-7404
type: literature
title: "Universally Composable Relaxed"
authors:
  - "Password Authenticated Key Exchange"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, protocol, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Protocols for password authenticated key exchange (PAKE) allow two parties who share only a weak password to agree on a cryptographic key. We revisit the notion of PAKE in the universal composability (UC) framework, and propose a relaxation of the PAKE functionality of Canetti et al. that we call lazy-extraction PAKE (lePAKE).

## Key claims (as reported)
- Our relaxation allows the ideal-world adversary to postpone its password guess until after a session is complete.
- We argue that this relaxed notion still provides meaningful security in the password-only setting.
- As our main result, we show that several PAKE protocols that were previously only proven secure with respect to a “game-based” definition of security can be shown to UC-realize the lePAKE functionality in the random-oracle model.
- These include SPEKE, SPAKE2, and TBPEKE, the most efficient PAKE schemes currently known.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12171357 (1).pdf`
- `downloads/12171357.pdf`
