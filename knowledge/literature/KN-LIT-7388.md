---
id: KN-LIT-7388
type: literature
title: "Universal Padding Schemes for RSA"
authors:
  - "Gemplus Card International"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [factoring, provable-security, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A common practice to encrypt with RSA is to first apply a padding scheme to the message and then to exponentiate the result with the public exponent; an example of this is OAEP. Similarly, the usual way of signing with RSA is to apply some padding scheme and then to exponentiate the result with the private exponent, as for example in PSS.

## Key claims (as reported)
- Usually, the RSA modulus used for encrypting is different from the one used for signing.
- The goal of this paper is to simplify this common setting.
- First, we show that PSS can also be used for encryption, and gives an encryption scheme semantically secure against adaptive chosenciphertext attacks, in the random oracle model.
- As a result, PSS can be used indifferently for encryption or signature.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/24420226 (1).pdf`
- `downloads/24420226 (2).pdf`
- `downloads/24420226.pdf`
