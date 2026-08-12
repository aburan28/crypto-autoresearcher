---
id: KN-LIT-1567
type: literature
title: "Batched Attribute-Based Encryption from Bilinear Pairings"
authors:
  - "Ramprasad Sarkar"
  - "Shayeef Murshid"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1454"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1454"
tags: [mpc, pairing, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Batched identity-based encryption (batched IBE), introduced by Agarwal, Fernando, and Pinkas (CRYPTO 2025), enables a key authority to issue a single succinct key that decrypts an entire batch of ciphertexts. However, existing batched encryption protocols support only identity-based access control and do not accommodate expressive attributebased policies.

## Key claims (as reported)
- We are the first to introduce Batched Attribute-Based Encryption (B-ABE), a generalization of batched encryption to the attributebased setting.
- In B-ABE, ciphertexts are associated with attribute sets and batch labels, while a single batch key is bound to an access policy and a public digest of the batch.
- The key decrypts exactly those ciphertexts in the batch whose attributes satisfy the policy, and its size is independent of the batch size.
- We construct B-ABE in asymmetric bilinear groups and prove security under the standard Decisional Bilinear Diffie-Hellman (DBDH) assumption in the random oracle model.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1454.pdf`
