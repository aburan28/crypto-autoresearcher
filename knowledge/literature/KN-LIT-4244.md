---
id: KN-LIT-4244
type: literature
title: "Honey Encryption: Security Beyond the Brute-Force Bound"
authors:
  - "Ari Juels"
  - "Thomas Ristenpart"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce honey encryption (HE), a simple, general approach to encrypting messages using low min-entropy keys such as passwords. HE is designed to produce a ciphertext which, when decrypted with any of a number of incorrect keys, yields plausible-looking but bogus plaintexts called honey messages.

## Key claims (as reported)
- A key benefit of HE is that it provides security in cases where too little entropy is available to withstand brute-force attacks that try every key; in this sense, HE provides security beyond conventional brute-force bounds.
- HE can also provide a hedge against partial disclosure of high min-entropy keys.
- HE significantly improves security in a number of practical settings.
- To showcase this improvement, we build concrete HE schemes for password-based encryption of RSA secret keys and credit card numbers.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/84410181 (1).pdf`
- `downloads/84410181 (2).pdf`
- `downloads/84410181 (3).pdf`
- `downloads/84410181.pdf`
