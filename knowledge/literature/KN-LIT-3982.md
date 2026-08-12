---
id: KN-LIT-3982
type: literature
title: "Fully Deniable Interactive Encryption 1 2"
authors:
  - "Ran Canetti"
  - "Sunoo Park"
  - "Oxana Poburinnaya"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, protocol, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Deniable encryption (Canetti et al., Crypto 1996) enhances secret communication over public channels, providing the additional guarantee that the secrecy of communication is protected even if the parties are later coerced (or willingly bribed) to expose their entire internal states: plaintexts, keys and randomness. To date, constructions of deniable encryption  and more generally, interactive deniable communication  only address restricted cases where only one party is compromised (Sahai and Waters, STOC 2014).

## Key claims (as reported)
- The main question  whether deniable communication is at all possible if both parties are coerced at once  has remained open.
- We resolve this question in the a rmative, presenting a communication protocol that is fully deniable under coercion of both parties.
- Our scheme has three rounds, assumes subexponentially secure indistinguishability obfuscation and one-way functions, and uses a short global reference string that is generated once at system set-up and su ces for an unbounded number of encryptions and decryptions. o-the-record deniability, which protects parties even when their claimed internal states Of independent interest, we introduce a new notion called are inconsistent (a case not covered by prior de nitions).
- Our scheme satis es both standard deniability and o-the-record deniability.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12171389 (1).pdf`
- `downloads/12171389.pdf`
