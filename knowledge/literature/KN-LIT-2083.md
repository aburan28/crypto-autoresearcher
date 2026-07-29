---
id: KN-LIT-2083
type: literature
title: "A Holistic Approach Towards Side-Channel Secure Fixed-Weight Polynomial Sampling"
authors:
  - "Markus Krausz"
  - "Georg Land"
  - "Jan Richter-Brockmann"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, elliptic-curve, implementation, lattice, pqc, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The sampling of polynomials with fixed weight is a procedure required by round-4 Key Encapsulation Mechanisms (KEMs) for PostQuantum Cryptography (PQC) standardization (BIKE, HQC, McEliece) as well as NTRU, Streamlined NTRU Prime, and NTRU LPRrime. Recent attacks have shown in this context that side-channel leakage of sampling methods can be exploited for key recoveries.

## Key claims (as reported)
- While countermeasures regarding such timing attacks have already been presented, still, there is no comprehensive work covering solutions that are also secure against power side channels.
- To close this gap, the contribution of this work is threefold: First, we analyze requirements for the different use cases of fixed weight sampling.
- Second, we demonstrate how all known sampling methods can be implemented securely against timing and power/EM side channels and propose performance-enhancing modifications.
- Furthermore, we propose a new, comparison-based methodology that outperforms existing methods in the masked setting for the three round-4 KEMs BIKE, HQC, and McEliece.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/13940048 (1).pdf`
- `downloads/13940048.pdf`
