---
id: KN-LIT-1689
type: literature
title: "Impact of Post-Quantum Signatures on InnoDB"
authors:
  - "Seung-Won Lee"
  - "Min-Seo Kim"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/987"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/987"
tags: [ecdsa, elliptic-curve, hash, lattice, pairing, pqc, protocol, quantum, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The transition to post-quantum cryptography (PQC) digital signatures poses an unexpected threat to the storage structure of relational databases. At the same security level, the AIMer-192f signature reaches 13,056 B, which is more than 13 times that of RSA-7680 (960 B).

## Key claims (as reported)
- Storing it inline in MySQL InnoDB causes the B+ -Tree fan-out to collapse from the theoretically predicted value of 167 to a measured value of 1.
- This result experimentally reveals that the off-page storage model in the MySQL official manual has a factor of 167 error in this case.
- To address this problem, we propose an architecture that combines a split-table schema with a Merkle Tree-based batch signing approach.
- The proposed architecture (B = 512) restores the collapsed fan-out to 41, reduces the number of leaf pages by 97%, and improves insertion throughput by 28.1×.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-987.pdf`
