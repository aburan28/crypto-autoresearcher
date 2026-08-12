---
id: KN-LIT-1205
type: literature
title: "Bitsliced Jasmin Implementation of the Mayo Signature Scheme"
authors:
  - "Samyuktha M"
  - "Pallavi Borkar"
  - "Chester Rebeiro"
year: 2024
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2024/1893"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2024/1893"
tags: [hash, implementation, lattice, pqc, provable-security, quantum, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a Jasmin bitsliced implementation of Mayo2, a multivariate quadratic(MQ) based signature scheme. Mayo overcomes the disadvantage of the Unbalanced oil and vinegar(UOV) scheme by whipping the UOV map to produce public keys of sizes comparable to ML-DSA.

## Key claims (as reported)
- The Round 2 C reference implementation employs a nibblesliced representation of GF(16), packing two field elements per byte across four 64-bit limbs.
- In contrast, our Jasmin implementation adopts a bitsliced representation, decomposing each GF(16) element across four separate 64-bit bit planes, enabling 64 simultaneous field operations.
- Our Jasmin implementation of Mayo2 takes 10.55 ms for keygen, 8.21 ms for sign, 0.17 ms for verify based on an average of 1000 runs of the implementation on a 13th Gen Intel Core i7-13700 processor (max turbo frequency 5.2 GHz) with 16 GB RAM.
- To this end, we have a multivariate quadratic based signature implementation that is amenable for verification of constant-time, correctness, proof of equivalence properties using Easycrypt.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2024-1893.pdf`
