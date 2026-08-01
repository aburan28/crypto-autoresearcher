---
id: KN-LIT-2320
type: literature
title: "Adapting Density Attacks to Low-Weight Knapsacks"
authors:
  - "Phong Q. Nguy ̃ên"
  - "Jacques Stern"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, lattice, provable-security, quantum, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Cryptosystems based on the knapsack problem were among the first public-key systems to be invented. Their high encryption/decryption rate attracted considerable interest until it was noticed that the underlying knapsacks often had a low density, which made them vulnerable to lattice attacks, both in theory and practice.

## Key claims (as reported)
- To prevent low-density attacks, several designers found a subtle way to increase the density beyond the critical density by decreasing the weight of the knapsack, and possibly allowing non-binary coefficients.
- This approach is actually a bit misleading: we show that low-weight knapsacks do not prevent efficient reductions to lattice problems like the shortest vector problem, they even make reductions more likely.
- To measure the resistance of low-weight knapsacks, we introduce the novel notion of pseudo-density, and we apply the new notion to the Okamoto-Tanaka-Uchiyama (OTU) cryptosystem from Crypto ’00.
- We do not claim to break OTU and we actually believe that this system may be secure with an appropriate choice of the parameters.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/041 (1).pdf`
- `downloads/041 (2).pdf`
- `downloads/041 (3).pdf`
- `downloads/041.pdf`
