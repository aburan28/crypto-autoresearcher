---
id: KN-LIT-3026
type: literature
title: "Composing Quantum Protocols in a Classical Environment"
authors:
  - "Serge Fehr"
  - "Christian Schaffner"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mpc, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose a general security definition for cryptographic quantum protocols that implement classical non-reactive two-party tasks. The definition is expressed in terms of simple quantum-informationtheoretic conditions which must be satisfied by the protocol to be secure.

## Key claims (as reported)
- The conditions are uniquely determined by the ideal functionality F defining the cryptographic task to be implemented.
- We then show the following composition result.
- If quantum protocols π1 , . . . , π` securely implement ideal functionalities F1 , . . . , F` according to our security definition, then any purely classical two-party protocol, which makes sequential calls to F1 , . . . , F` , is equally secure as the protocol obtained by replacing the calls to F1 , . . . , F` with the respective quantum protocols π1 , . . . , π` .
- Hence, our approach yields the minimal security requirements which are strong enough for the typical use of quantum protocols as subroutines within larger classical schemes.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/54440346 (1).pdf`
- `downloads/54440346 (2).pdf`
- `downloads/54440346 (3).pdf`
- `downloads/54440346.pdf`
