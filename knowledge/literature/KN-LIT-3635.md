---
id: KN-LIT-3635
type: literature
title: "Efficient Simultaneous Broadcast"
authors:
  - "Sebastian Faust"
  - "Emilia Käsper"
  - "Stefan Lucks"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, rsa, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present an efficient simultaneous broadcast protocol ν-SimCast that allows n players to announce independently chosen values, even if up to t < n2 players are corrupt. Independence is guaranteed in the partially synchronous communication model, where communication is structured into rounds, while each round is asynchronous.

## Key claims (as reported)
- The ν-SimCast protocol is more efficient than previous constructions.
- For repeated executions, we reduce the communication and computation complexity by a factor O(n).
- Combined with a deterministic extractor, ν-SimCast provides a particularly efficient solution for distributed coin-flipping.
- The protocol does not require any zero-knowledge proofs and is shown to be secure in the standard model under the Decisional Diffie Hellman assumption.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/49390181 (1).pdf`
- `downloads/49390181 (2).pdf`
- `downloads/49390181 (3).pdf`
- `downloads/49390181.pdf`
