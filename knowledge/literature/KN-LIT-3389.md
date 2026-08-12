---
id: KN-LIT-3389
type: literature
title: "Design in Type-I, Run in Type-III: Fast and Scalable Bilinear-Type Conversion using Integer Programming"
authors:
  - "Masayuki Abe"
  - "Fumitaka Hoshino"
  - "Miyako Ohkubo"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, mov-fr, pairing, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Bilinear type conversion is to convert cryptographic schemes designed over symmetric groups instantiated with imperilled curves into ones that run over more secure and efficient asymmetric groups. In this paper we introduce a novel type conversion method called IPConv using 0-1 Integer Programming.

## Key claims (as reported)
- Instantiated with a widely available IP solver, it instantly converts existing intricate schemes, and can process large-scale schemes that involves more than a thousand variables and hundreds of pairings.
- Such a quick and scalable method allows a new approach in designing cryptographic schemes over asymmetric bilinear groups.
- Namely, designers work without taking much care about asymmetry of computation but the converted scheme runs well in the asymmetric setting.
- We demonstrate the usefulness of conversion-aided design by presenting somewhat counterintuitive examples where converted DLIN-based Groth-Sahai proofs are more compact than manually built SXDH-based proofs.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/98160374 (1).pdf`
- `downloads/98160374.pdf`
