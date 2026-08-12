---
id: KN-LIT-2818
type: literature
title: "Building Lossy Trapdoor Functions from Lossy Encryption"
authors:
  - "Brett Hemenway"
  - "Rafail Ostrovsky"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mpc, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Injective one-way trapdoor functions are one of the most fundamental cryptographic primitives. In this work we show how to derandomize lossy encryption (with long messages) to obtain lossy trapdoor functions, and hence injective one-way trapdoor functions.

## Key claims (as reported)
- Bellare, Halevi, Sahai and Vadhan (CRYPTO ’98) showed that if Enc is an IND-CPA secure cryptosystem, and H is a random oracle, then x 7→ Enc(x, H(x)) is an injective trapdoor function.
- In this work, we show that if Enc is a lossy encryption with messages at least 1-bit longer than randomness, and h is a pairwise independent hash function, then x 7→ Enc(x, h(x)) is a lossy trapdoor function, and hence also an injective trapdoor function.
- The works of Peikert, Vaikuntanathan and Waters and Hemenway, Libert, Ostrovsky and Vergnaud showed that statistically-hiding 2-round Oblivious Transfer (OT) is equivalent to Lossy Encryption.
- In their construction, if the sender randomness is shorter than the message in the OT, it will also be shorter than the message in the lossy encryption.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/82700242 (1).pdf`
- `downloads/82700242 (2).pdf`
- `downloads/82700242 (3).pdf`
- `downloads/82700242.pdf`
