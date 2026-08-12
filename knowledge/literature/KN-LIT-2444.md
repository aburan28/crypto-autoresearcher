---
id: KN-LIT-2444
type: literature
title: "Amplification of Chosen-Ciphertext Security"
authors:
  - "Huijia Lin"
  - "Stefano Tessaro"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [provable-security, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A central question in the theory of public-key cryptography is to determine which minimal assumptions are sufficient to achieve security against chosen-ciphertext attacks (or CCA-security, for short). Following the large body of work on hardness and correctness amplification, we investigate how far we can weaken CCA security and still be able to efficiently transform any scheme satisfying such a weaker notion into a fully CCA-secure one.

## Key claims (as reported)
- More concretely, we consider a weak CCA-secure bit-encryption scheme with decryption error (1 − α)/2 where an adversary can distinguish encryptions of different messages with possibly large advantage β < 1 − 1/poly.
- We show that whenever α2 > β, the weak correctness and security properties can be simultaneously amplified to obtain a fully CCAsecure encryption scheme with negligible decryption error.
- Our approach relies both on a new hardcore lemma for CCA security as well as on revisiting the recently proposed approach to obtain CCA security due to Hohenberger et al (EUROCRYPT ’12).
- We note that such amplification results were only known in the simpler case of security against chosen-plaintext attacks.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/78810501 (1).pdf`
- `downloads/78810501 (2).pdf`
- `downloads/78810501 (3).pdf`
- `downloads/78810501.pdf`
