---
id: KN-LIT-3678
type: literature
title: "Encryption Switching Protocols"
authors:
  - "Geoffroy Couteau"
  - "Thomas Peters"
  - "David Pointcheval"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [factoring, fhe, mpc, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We formally define the primitive of encryption switching protocol (ESP), allowing to switch between two encryption schemes. Intuitively, this two-party protocol converts given ciphertexts from one scheme into ciphertexts of the same messages under the other scheme, for any polynomial number of switches, in any direction.

## Key claims (as reported)
- Although ESP is a special kind of two-party computation protocol, it turns out that ESP implies general two-party computation (2-PC) under natural conditions.
- In particular, our new paradigm is tailored to the evaluation of functions over rings.
- Indeed, assuming the compatibility of two additively and multiplicatively homomorphic encryption schemes, switching ciphertexts makes it possible to efficiently reconcile the two internal laws.
- Since no such pair of public-key encryption schemes appeared in the literature, except for the non-interactive case of fully homomorphic encryption which still remains prohibitive in practice, we build the first multiplicatively homomorphic ElGamal-like encryption scheme over (Zn , ×) as a complement to the Paillier encryption scheme over (Zn , +), where n is a strong RSA modulus.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/98140300 (1).pdf`
- `downloads/98140300.pdf`
