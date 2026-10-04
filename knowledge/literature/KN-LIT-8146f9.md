---
id: KN-LIT-8146f9
type: literature
title: "Security Analysis of Elliptic Curves over Sextic Extension of Small Prime Fields"
authors:
  - "Robin Salen"
  - "Vijaykumar Singh"
  - "Vladimir Soukharev"
year: 2022
venue: "IACR ePrint 2022/277"
identifiers:
  eprint: "iacr:2022/277"
  arxiv: null
  doi: null
  url: null
tags: [index-calculus, extension-field, cheetah, zk-curves, security-analysis, weil-descent, ecdlp]
confidence: reported
citation_verified: read
added: "2026-09-26"
superseded_by: null
---

## Contribution

Designs Cheetah, a curve over a sextic extension of a 64-bit prime field for STARK use. The analysis covers Weil descent through the towers F_p < F_{p^3} < F_{p^6} and F_p < F_{p^2} < F_{p^6}, genus-2/genus-3 cover attacks and GHS applicability. It is the closest published sibling analysis to ecGFp5.

## Key claims (as reported)

- Generic (rho on the ~256-bit subgroup): 127.3 bits. Joux-Vitse 2012 decomposition on Jac(H)[F_{p^2}]: >= (5/3)*64 ~ 106.67 bits ignoring constants (so not by itself sufficient). Weil descent (genus 2/3): >= 2^136. Genus-2 covers and hyperelliptic genus-3 covers do not apply because #E(K) = 2 mod 4 (one rational 2-torsion point, the same 2-torsion shape as double-odd ecGFp5). Non-hyperelliptic genus-3 cover: >= 135 bits.

## Relevance to this program

Security analysis of the Cheetah curve over a sextic extension of a 64-bit prime field: the closest published sibling of an ecGFp5 index-calculus analysis (GOAL-GFPN-380702). Its Joux–Vitse estimate (≥106.67 bits, constants ignored) shows the style of argument an ecGFp5 note must match.

## Not verified here

The full text was read during the 2026-09-26 ECDLP literature sweep. Numbers are quoted from it, not re-derived or reproduced.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
