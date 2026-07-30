---
id: KN-LIT-751
type: literature
title: "Efficient Montgomery-like formulas for general"
authors:
  - "Huff ’s"
  - "Huff ’s elliptic curves"
year: 2020
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2020/526"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2020/526"
tags: [curve-arithmetic, elliptic-curve, isogeny, provable-security, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper for elliptic curves provided by Huff’s equation Ha,b : ax(y 2 − 1) = by(x2 − 1) and general Huff’s equation Ga,b : x(ay 2 − 1) = y(bx2 − 1) and degree 2 compression function f (x, y) = xy on these curves, herein we provide formulas for doubling and differential addition after compression, which for Huff’s curves are as efficient as Montgomery’s formulas for Montgomery’s curves By 2 = x3 + Ax2 + x. For these curves we also provided point recovery formulas after compression, which for a point P on these curves allows to compute [n]f (P ) after compression using the Montgomery ladder algorithm, and then recover [n]P .

## Key claims (as reported)
- Using formulas of Moody and Shumow for computing odd degree isogenies on general Huff’s curves, we have also provide formulas for computing odd degree isogenies after compression for these curves.
- Moreover, it is shown herein how to apply obtained formulas using compression to the ECM algorithm.
- In the appendix, we present examples of Huff’s curves convenient for the isogeny-based cryptography, where compression can be used.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2020-526.pdf`
