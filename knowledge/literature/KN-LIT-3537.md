---
id: KN-LIT-3537
type: literature
title: "Efficient Circuit-based PSI with Linear Communication"
authors:
  - "Benny Pinkas"
  - "Thomas Schneider"
  - "Oleksandr Tkachenko"
  - "Avishay Yanai"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a new protocol for computing a circuit which implements the private set intersection functionality (PSI). Using circuits for this task is advantageous over the usage of specific protocols for PSI, since many applications of PSI do not need to compute the intersection itself but rather functions based on the items in the intersection.

## Key claims (as reported)
- Our protocol is the first circuit-based PSI protocol to achieve linear communication complexity.
- It is also concretely more efficient than all previous circuit-based PSI protocols.
- For example, for sets of size 220 it improves the communication of the recent work of Pinkas et al.
- (EUROCRYPT’18) by more than 10 times, and improves the run time by a factor of 2.8x in the LAN setting, and by a factor of 5.8x in the WAN setting.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/114760352 (1).pdf`
- `downloads/114760352.pdf`
