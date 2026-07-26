---
id: KN-LIT-2913
type: literature
title: "Circular-Secure Encryption from Decision Diffie-Hellman"
authors:
  - "Dan Boneh"
  - "Shai Halevi"
  - "Mike Hamburg"
  - "Rafail Ostrovsky"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We describe a public-key encryption system that remains secure even encrypting messages that depend on the secret keys in use. In particular, it remains secure under a “key cycle” usage, where we have a cycle of public/secret key-pairs (pki , ski ) for i = 1, . . . , n, and we encrypt each ski under pk(i mod n)+1 .

## Key claims (as reported)
- Such usage scenarios sometimes arise in key-management systems and in the context of anonymous credential systems.
- Also, security against key cycles plays a role when relating “axiomatic security” of protocols that use encryption to the “computational security” of concrete instantiations of these protocols.
- The existence of encryption systems that are secure in the presence of key cycles was wide open until now: on the one hand we had no constructions that provably meet this notion of security (except by relying on the random-oracle heuristic); on the other hand we had no examples of secure encryption systems that become demonstrably insecure in the presence of key-cycles of length greater than one.
- Here we construct an encryption system that is circular-secure against chosen-plaintext attacks under the Decision Diffie-Hellman assumption (without relying on random oracles).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/51570109 (1).pdf`
- `downloads/51570109 (2).pdf`
- `downloads/51570109 (3).pdf`
- `downloads/51570109.pdf`
