---
id: KN-LIT-931
type: literature
title: "Supersingular Isogeny-Based Ring Signature?"
authors:
  - "Maryam Sheikhi Garjan"
  - "N. Gamze Orhon Kılıç"
  - "Murat Cenk"
year: 2021
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2021/1318"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2021/1318"
tags: [dlp, elliptic-curve, endomorphism, factoring, hash, isogeny, lattice, pairing, pqc, provable-security, quantum, rsa, sidh-csidh, signature, supersingular, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A ring signature is a digital signature scheme that allows identifying a group of possible signers without revealing the identity of the actual signer. In this paper, we first present a post-quantum sigma protocol for a ring that relies on the supersingular isogeny-based interactive zero-knowledge identification scheme proposed by De Feo, Jao, and Plût in 2014.

## Key claims (as reported)
- Then, we construct a ring signature from the proposed sigma protocol for a ring by applying the Fiat-Shamir transform.
- In order to reduce the size of exchanges, we use Merkle trees and show that the signature size increases logarithmically in the size of the ring.
- The security proofs and complexity analyses of the proposed protocols are also provided.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2021-1318.pdf`
