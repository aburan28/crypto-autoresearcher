---
id: KN-LIT-4433
type: literature
title: "Improved Security for Linearly Homomorphic Signatures: A Generic Framework"
authors:
  - "David Mandell Freeman"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, prime-field, provable-security, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose a general framework that converts (ordinary) signature schemes having certain properties into linearly homomorphic signature schemes, i.e., schemes that allow authentication of linear functions on signed data. The security of the homomorphic scheme follows from the same computational assumption as is used to prove security of the underlying signature scheme.

## Key claims (as reported)
- We show that the following signature schemes have the required properties and thus give rise to secure homomorphic signatures in the standard model: – The scheme of Waters (Eurocrypt 2005), secure under the computational Diffie-Hellman asumption in bilinear groups. – The scheme of Boneh and Boyen (Eurocrypt 2004, J.
- Cryptology 2008), secure under the q-strong Diffie-Hellman assumption in bilinear groups. – The scheme of Gennaro, Halevi, and Rabin (Eurocrypt 1999), secure under the strong RSA assumption. – The scheme of Hohenberger and Waters (Crypto 2009), secure under the RSA assumption.
- Our systems not only allow weaker security assumptions than were previously available for homomorphic signatures in the standard model, but also are secure in a model that allows a stronger adversary than in other proposed schemes.
- Our framework also leads to efficient linearly homomorphic signatures that are secure against our stronger adversary under weak assumptions (CDH or RSA) in the random oracle model; all previous proofs of security in the random oracle model break down completely when faced with our stronger adversary.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/72930697 (1).pdf`
- `downloads/72930697 (2).pdf`
- `downloads/72930697 (3).pdf`
- `downloads/72930697.pdf`
