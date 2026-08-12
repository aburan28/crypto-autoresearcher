---
id: KN-LIT-3957
type: literature
title: "From Fixed-Length to Arbitrary-Length RSA Encoding Schemes Revisited"
authors:
  - "Julien Cathalo"
  - "Jean-Sébastien Coron"
  - "David Naccache"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, provable-security, quantum, rsa, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
To sign with RSA, one usually encodes the message m as μ(m) and then raises the result to the private exponent modulo N . In Asiacrypt 2000, Coron et al. showed how to build a secure RSA encoding scheme μ0 (m) for signing arbitrarily long messages from a secure encoding scheme μ(m) capable of handling only fixed-size messages, without making any additional assumptions.

## Key claims (as reported)
- However, their construction required that the input size of μ be larger than the modulus size.
- In this paper we present a construction for which the input size of μ does not have to be larger than N .
- Our construction shows that the difficulty in building a secure encoding for RSA signatures is not in handling messages of arbitrary length, but rather in finding a secure encoding function for short messages, which remains an open problem in the standard model.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/33860236 (1).pdf`
- `downloads/33860236 (2).pdf`
- `downloads/33860236 (3).pdf`
- `downloads/33860236.pdf`
