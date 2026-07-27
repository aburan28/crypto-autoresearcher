---
id: KN-LIT-7344
type: literature
title: "Unbounded Quadratic Functional Encryption and More from Pairings"
authors:
  - "Junichi Tomida"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose the first unbounded functional encryption (FE) scheme for quadratic functions and its extension, in which the sizes of messages to be encrypted are not a priori bounded. Prior to our work, all FE schemes for quadratic functions are bounded, meaning that the message length is fixed at the setup.

## Key claims (as reported)
- In the first scheme, encryption takes P {xi }i∈Sc , key generation takes {ci,j }i,j∈Sk , and decryption outputs i,j∈Sk ci,j xi xj if and only if Sk ⊆ Sc , where the sizes of Sc and Sk can be arbitrary.
- Our second scheme is the extension of the first scheme to partially-hiding FE that computes an arithmetic branching program on a public input and a quadratic function on a private input.
- Concretely, encryption takes a public input u in addition to {xi }i∈Sc , a secret key is associated with P arithmetic branching programs {fi,j }i,j∈Sk , and decryption yields i,j∈Sk fi,j (u)xi xj if and only if Sk ⊆ Sc .
- Both our schemes are based on pairings and secure in the simulation-based model under the standard MDDH assumption.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14004111 (1).pdf`
- `downloads/14004111.pdf`
