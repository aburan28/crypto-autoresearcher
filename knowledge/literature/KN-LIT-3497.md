---
id: KN-LIT-3497
type: literature
title: "Dynamic Group Diffie-Hellman Key Exchange under Standard Assumptions"
authors:
  - "Emmanuel Bresson"
  - "Olivier Chevassut"
  - "David Pointcheval"
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
Authenticated Diffie-Hellman key exchange allows two principals communicating over a public network, and each holding public/private keys, to agree on a shared secret value. In this paper we study the natural extension of this cryptographic problem to a group of principals.

## Key claims (as reported)
- We begin from existing formal security models and refine them to incorporate major missing details (e.g., strong-corruption and concurrent sessions).
- Within this model we define the execution of a protocol for authenticated dynamic group Diffie-Hellman and show that it is provably secure under the decisional Diffie-Hellman assumption.
- Our security result holds in the standard model and thus provides better security guarantees than previously published results in the random oracle model.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/GroupDH_StandardModel (1).pdf`
- `downloads/GroupDH_StandardModel (2).pdf`
- `downloads/GroupDH_StandardModel.pdf`
