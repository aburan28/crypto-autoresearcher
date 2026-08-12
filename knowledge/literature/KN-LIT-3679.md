---
id: KN-LIT-3679
type: literature
title: "Encryption Switching Protocols Revisited: Switching modulo p"
authors:
  - "Guilhem Castagnos"
  - "Laurent Imbert"
  - "Fabien Laguillaumie"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [factoring, fhe, mpc, pairing, provable-security, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
At CRYPTO 2016, Couteau, Peters and Pointcheval introduced a new primitive called encryption switching protocols, allowing to switch ciphertexts between two encryption schemes. If such an ESP is built with two schemes that are respectively additively and multiplicatively homomorphic, it naturally gives rise to a secure 2-party computation protocol.

## Key claims (as reported)
- It is thus perfectly suited for evaluating functions, such as multivariate polynomials, given as arithmetic circuits.
- Couteau et al. built an ESP to switch between Elgamal and Paillier encryptions which do not naturally fit well together.
- Consequently, they had to design a clever variant of Elgamal over Z/nZ with a costly shared decryption.
- In this paper, we first present a conceptually simple generic construction for encryption switching protocols.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10401180 (1).pdf`
- `downloads/10401180.pdf`
