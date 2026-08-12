---
id: KN-LIT-2086
type: literature
title: "A Key-Recovery Attack against Mitaka in the t-Probing Model"
authors:
  - "Thomas Prest"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, lattice, pairing, pqc, provable-security, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Mitaka is a lattice-based signature proposed at Eurocrypt 2022. A key advertised feature of Mitaka is that it can be masked at high orders efficiently, making it attractive in scenarios where side-channel attacks are a concern.

## Key claims (as reported)
- Mitaka comes with a claimed security proof in the t-probing model.
- We uncover a flaw in the security proof of Mitaka, and subsequently show that it is not secure in the t-probing model.
- For any number of shares d ≥ 4, probing t < d variables per execution allows an attacker to recover the private key efficiently with approximately 221 executions.
- Our analysis shows that even a constant number of probes suffices (t = 3), as long as the attacker has access to a number of executions that is linear in d/t.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/13940192 (1).pdf`
- `downloads/13940192.pdf`
