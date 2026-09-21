---
id: KN-LIT-2530
type: literature
title: "Analysis of the Non-linear Part of Mugi"
authors:
  - "Alex Biryukov⋆"
  - "Adi Shamir"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, implementation, pairing, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper presents the results of a preliminary analysis of the stream cipher Mugi. We study the nonlinear component of this cipher and identify several potential weaknesses in its design.

## Key claims (as reported)
- While we can not break the full Mugi design, we show that it is extremely sensitive to small variations.
- For example, it is possible to recover the full 1216-bit state of the cipher and the original 128-bit secret key using just 56 words of known stream and in 214 steps of analysis if the cipher outputs any state word which is different than the one used in the actual design.
- If the linear part is eliminated from the design, then the secret nonlinear 192-bit state can be recovered given only three output words and in just 232 steps.
- If it is kept in the design but in a simplified form, then the scheme can be broken by an attack which is slightly faster than exhaustive search.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/35570314 (1).pdf`
- `downloads/35570314 (2).pdf`
- `downloads/35570314 (3).pdf`
- `downloads/35570314.pdf`
