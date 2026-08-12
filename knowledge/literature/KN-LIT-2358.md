---
id: KN-LIT-2358
type: literature
title: "Adaptively Secure, Universally Composable, Multiparty Computation in Constant Rounds"
authors:
  - "Dana Dachman-Soled"
  - "Jonathan Katz"
  - "Vanishree Rao"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Cryptographic protocols with adaptive security ensure that security holds against an adversary who can dynamically determine which parties to corrupt as the protocol progresses—or even after the protocol is finished. In the setting where all parties may potentially be corrupted, and secure erasure is not assumed, it has been a long-standing open question to design secure-computation protocols with adaptive security running in constant rounds.

## Key claims (as reported)
- Here, we show a constant-round, universally composable protocol for computing any functionality, tolerating a malicious, adaptive adversary corrupting any number of parties.
- Interestingly, our protocol can compute all functionalities, not just adaptively well-formed ones.
- The protocol relies on indistinguishability obfuscation, and assumes a common reference string.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/90150586 (1).pdf`
- `downloads/90150586.pdf`
