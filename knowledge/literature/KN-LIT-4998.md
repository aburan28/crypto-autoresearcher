---
id: KN-LIT-4998
type: literature
title: "Multi-key Fully-Homomorphic Encryption in the Plain Model"
authors:
  - "Prabhanjan Ananth"
  - "Abhishek Jain"
  - "Zhengzhong Jin"
  - "Giulio Malavolta"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, mpc, pairing, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The notion of multi-key fully homomorphic encryption (multikey FHE) [López-Alt, Tromer, Vaikuntanathan, STOC’12] was proposed as a generalization of fully homomorphic encryption to the multiparty setting. In a multi-key FHE scheme for n parties, each party can individually choose a key pair and use it to encrypt its own private input.

## Key claims (as reported)
- Given n ciphertexts computed in this manner, the parties can homomorphically evaluate a circuit C over them to obtain a new ciphertext containing the output of C, which can then be decrypted via a decryption protocol.
- The key efficiency property is that the size of the (evaluated) ciphertext is independent of the size of the circuit.
- Multi-key FHE with one-round decryption [Mukherjee and Wichs, Eurocrypt’16], has found several powerful applications in cryptography over the past few years.
- However, an important drawback of all such known schemes is that they require a trusted setup.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12550227 (1).pdf`
- `downloads/12550227.pdf`
