---
id: KN-LIT-3492
type: literature
title: "Dynamic Ad Hoc Clock Synchronization"
authors:
  - "Christian Badertscher"
  - "Peter Gaži"
  - "Aggelos Kiayias"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr, mpc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Clock synchronization allows parties to establish a common notion of global time by leveraging a weaker synchrony assumption, i.e., local clocks with approximately the same speed. Despite intensive investigation of the problem in the fault-tolerant distributed computing literature, existing solutions do not apply to settings where participation is unknown, e.g., the ad hoc model of Beimel et al.

## Key claims (as reported)
- [EUROCRYPT 17], or is dynamically shifting over time, e.g., the fluctuating/sleepy/dynamic-availability models of Garay et al.
- [CRYPTO 17], Pass and Shi [ASIACRYPT 17] and Badertscher et al.
- We show how to apply and extend ideas from the blockchain literature to devise synchronizers that work in such dynamic ad hoc settings and tolerate corrupted minorities under the standard assumption that local clocks advance at approximately the same speed.
- We discuss both the setting of honest-majority hashing power and that of a PKI with honest majority.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/126960155 (1).pdf`
- `downloads/126960155.pdf`
