---
id: KN-LIT-6024
type: literature
title: "Public-Key Encryption Indistinguishable Under Plaintext-Checkable Attacks"
authors:
  - "Michel Abdalla"
  - "Fabrice Benhamouda"
  - "David Pointcheval"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, protocol, provable-security, quantum, rsa, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Indistinguishability under adaptive chosen-ciphertext attack (IND-CCA) is now considered the de facto security notion for publickey encryption. However, the security guarantee that it offers is sometimes stronger than what is needed by certain applications.

## Key claims (as reported)
- In this paper, we consider a weaker notion of security for public-key encryption, termed indistinguishability under plaintext-checking attacks (IND-PCA), in which the adversary is only given access to an oracle which says whether or not a given ciphertext encrypts a given message.
- After formalizing the IND-PCA notion, we then design a new public-key encryption scheme satisfying it.
- The new scheme is a more efficient variant of the Cramer-Shoup encryption scheme with shorter ciphertexts and its security is also based on the plain Decisional Diffie-Hellman (DDH) assumption.
- Additionally, the algebraic properties of the new scheme also allow for proving plaintext knowledge using Groth-Sahai non-interactive zeroknowledge proofs or smooth projective hash functions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/90200159 (1).pdf`
- `downloads/90200159 (2).pdf`
- `downloads/90200159 (3).pdf`
- `downloads/90200159 (4).pdf`
- `downloads/90200159.pdf`
