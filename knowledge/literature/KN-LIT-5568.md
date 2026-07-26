---
id: KN-LIT-5568
type: literature
title: "On the Security of Cryptosystems with Quadratic Decryption: The Nicest Cryptanalysis"
authors:
  - "Guilhem Castagnos"
  - "Fabien Laguillaumie"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [class-group, cryptanalysis, factoring, number-theory, protocol, provable-security, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We describe the first polynomial time chosen-plaintext total break of the NICE family of cryptosystems based on ideal arithmetic in imaginary quadratic orders, introduced in the late 90’s by Hartmann, Paulus and Takagi [HPT99]. The singular interest of these encryption schemes is their natural quadratic decryption time procedure that consists essentially in applying Euclid’s algorithm.

## Key claims (as reported)
- The only current specific cryptanalysis of these schemes is Jaulmes and Joux’s chosenciphertext attack to recover the secret key [JJ00].
- Originally, Hartmann et al. claimed that the security against a total break attack relies only on the difficulty of factoring the public discriminant ∆q = −pq 2 , although the public key was also composed of a specific element of the class group of the order of discriminant ∆q , which is crucial to reach the quadratic decryption complexity.
- In this article, we propose a drastic cryptanalysis which factors ∆q (and hence recovers the secret key), only given this element, in cubic time in the security parameter.
- As a result, performing our cryptanalysis on a cryptographic example takes less than a second on a standard PC.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/54790261 (1).pdf`
- `downloads/54790261 (2).pdf`
- `downloads/54790261 (3).pdf`
- `downloads/54790261.pdf`
