---
id: KN-LIT-3536
type: literature
title: "Efficient Chosen-Ciphertext Security via Extractable Hash Proofs"
authors:
  - "Hoeteck Wee"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [elliptic-curve, lattice, pairing, quantum, rsa, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce the notion of an extractable hash proof system. Essentially, this is a special kind of non-interactive zero-knowledge proof of knowledge system where the secret keys may be generated in one of two modes to allow for either simulation or extraction. – We show how to derive efficient CCA-secure encryption schemes via extractable hash proofs in a simple and modular fashion.

## Key claims (as reported)
- Our construction clarifies and generalizes the recent factoring-based cryptosystem of Hofheinz and Kiltz (Eurocrypt ’09), and is reminiscent of an approach proposed by Rackoff and Simon (Crypto ’91).
- We show how to instantiate extractable hash proof system for hard search problems, notably factoring and computational Diffie-Hellman.
- Using our framework, we obtain the first CCA-secure encryption scheme based on CDH where the public key is a constant number of group elements and a more modular and conceptually simpler variant of the Hofheinz-Kiltz cryptosystem (though less efficient). – We introduce adaptive trapdoor relations, a relaxation of the adaptive trapdoor functions considered by Kiltz, Mohassel and O’Neil (Eurocrypt ’10), but nonetheless imply CCA-secure encryption schemes.
- We show how to construct such relations using extractable hash proofs, which in turn yields realizations from hardness of factoring and CDH.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/62230313 (1).pdf`
- `downloads/62230313 (2).pdf`
- `downloads/62230313 (3).pdf`
- `downloads/62230313.pdf`
