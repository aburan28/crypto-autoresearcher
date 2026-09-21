---
id: KN-LIT-6620
type: literature
title: "Side-Channel Attacks on Textbook RSA and ElGamal Encryption Ulrich Kühn"
authors:
  - "Dresdner Bank"
  - "Information Security"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [quantum, rsa, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper describes very efficient attacks on plain RSA encryption as usually described in textbooks. These attacks exploit side channels caused by implementations that, during decryption, incorrectly make certain assumption on the size of message.

## Key claims (as reported)
- We highlight different assumptions that are easily made when implementing plain RSA decryption and present corresponding attacks.
- These attacks make clear that plain RSA is a padding scheme that has to be checked carefully during decryption instead of simply assuming a length of the transported message.
- Furthermore we note that the attacks presented here do also work against a similar setting of ElGamal encryption with only minimal changes.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/25670324 (1).pdf`
- `downloads/25670324 (2).pdf`
- `downloads/25670324.pdf`
