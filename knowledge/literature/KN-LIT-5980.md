---
id: KN-LIT-5980
type: literature
title: "Provably Secure Threshold Password-Authenticated Key Exchange?"
authors:
  - "Mario Di Raimondo"
  - "Rosario Gennaro"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [protocol, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present two protocols for threshold password authenticated key exchange. In this model, the password is not stored in a single authenticating server but rather shared among a set of n servers so that an adversary can learn the password only by breaking into t + 1 of them.

## Key claims (as reported)
- The protocols require n > 3t servers to work.
- The goal is to protect the password against hackers attacks that can break into the authenticating server and steal password information.
- All known centralized password authentication schemes are susceptible to such an attack.
- Ours are the first protocols which are provably secure in the standard model (i.e. no random oracles are used for the proof of security).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/26560507 (1).pdf`
- `downloads/26560507 (2).pdf`
- `downloads/26560507.pdf`
