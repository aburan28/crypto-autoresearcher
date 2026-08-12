---
id: KN-LIT-3313
type: literature
title: "Cryptographic Shallots: A Formal Treatment of Repliable Onion Encryption"
authors:
  - "Megumi Ando"
  - "Anna Lysyanskaya"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, quantum, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Onion routing is a popular, efficient, and scalable method for enabling anonymous communications. To send a message m to Bob via onion routing, Alice picks several intermediaries, wraps m in multiple layers of encryption — a layer per intermediary — and sends the resulting onion to the first intermediary.

## Key claims (as reported)
- Each intermediary peels off a layer of encryption and learns the identity of the next entity on the path and what to send along; finally Bob learns that he is the recipient and recovers the message m.
- Despite its wide use in the real world, the foundations of onion routing have not been thoroughly studied.
- In particular, although two-way communication is needed in most instances, such as anonymous Web browsing or anonymous access to a resource, until now no definitions or provably secure constructions have been given for two-way onion routing.
- Moreover, the security definitions that existed even for one-way onion routing were found to have significant flaws.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/130420134 (1).pdf`
- `downloads/130420134.pdf`
