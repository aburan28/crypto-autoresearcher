---
id: KN-LIT-6373
type: literature
title: "Scalable Protocols for Authenticated Group Key Exchange"
authors:
  - "Jonathan Katz"
  - "Moti Yung"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, protocol, provable-security, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We consider the fundamental problem of authenticated group key exchange among n parties within a larger and insecure public network. A number of solutions to this problem have been proposed; however, all provably-secure solutions thus far are not scalable and, in particular, require n rounds.

## Key claims (as reported)
- Our main contribution is the first scalable protocol for this problem along with a rigorous proof of security in the standard model under the DDH assumption; our protocol uses a constant number of rounds and requires only O(1) modular exponentiations per user (for key derivation).
- Toward this goal and of independent interest, we first present a scalable compiler that transforms any group key-exchange protocol secure against a passive eavesdropper to an authenticated protocol which is secure against an active adversary who controls all communication in the network.
- This compiler adds only one round and O(1) communication (per user) to the original scheme.
- We then prove secure — against a passive adversary — a variant of the two-round group keyexchange protocol of Burmester and Desmedt.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/27290110 (1).pdf`
- `downloads/27290110 (2).pdf`
- `downloads/27290110.pdf`
