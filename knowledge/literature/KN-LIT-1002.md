---
id: KN-LIT-1002
type: literature
title: "Meet-in-the-Middle"
authors:
  - "Lingyue Qin"
  - "Jialiang Hua"
  - "Xiaoyang Dong"
year: 2022
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2022/171"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2022/171"
tags: [cryptanalysis, hash, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Meet-in-the-Middle (MitM) attack has been widely applied to preimage attacks on Merkle-Damgård (MD) hashing. In this paper, we introduce a generic framework of the MitM attack on spongebased hashing.

## Key claims (as reported)
- We find certain bit conditions can significantly reduce the diffusion of the unknown bits and lead to longer MitM characteristics.
- To find good or optimal configurations of MitM attacks, e.g., the bit conditions, the neutral sets, and the matching points, we introduce the bit-level MILP-based automatic tools on Keccak, Ascon and Xoodyak.
- To reduce the scale of bit-level models and make them solvable in reasonable time, a series of properties of the targeted hashing are considered in the modelling, such as the linear structure and CP-kernel for Keccak, the Boolean expression of Sbox for Ascon.
- Finally, we give an improved 4-round preimage attack on Keccak-512/SHA3, and break a nearly 10 years’ cryptanalysis record.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14004026 (1).pdf`
- `downloads/14004026.pdf`
