---
id: KN-LIT-7570
type: literature
title: "Finding the permutation between equivalent linear codes: the support splitting algorithm"
authors: [Sendrier Nicolas]
year: 2000
venue: IEEE Transactions on Information Theory, 46(4):1193-1203
identifiers:
  eprint: null
  doi: 10.1109/18.850662
  url: https://doi.org/10.1109/18.850662
tags: [code-based, code-equivalence, support-splitting, structural-attack, hull, cryptanalysis]
confidence: reported
citation_verified: web
added: 2026-07-27
superseded_by: null
---

## Contribution
An algorithm that recovers the permutation between two permutation-equivalent
linear codes. It computes a permutation-invariant signature for each coordinate;
when the signature is fully discriminant the code's support splits into
singletons and the permutation falls out. Complexity is polynomial in the code
length and exponential in the dimension of the code's hull (its intersection
with its dual).

## Key claims (as reported)
- Code equivalence is easy for codes with small hull -- which is the generic
  case -- and hard only when the hull is large (e.g. weakly self-dual codes).
- Total complexity: polynomial in length, exponential in hull dimension.

## Relevance to this program
Two consequences the program should keep distinct. (1) As an attack primitive:
if a scheme's secret is only a permutation of a *known* code, support splitting
recovers it, which is why McEliece-type systems must hide the code itself and
not merely permute a public one. (2) As a hardness source: the hull-dimension
dependence is what makes code equivalence usable as an assumption for signature
schemes (LESS-style) rather than only as an attack. This dual role is recorded
in KN-TECH-059.

## Not verified here
Primary paper not fetched. Author, title, venue, volume/issue/pages, year, and
DOI confirmed via search against DBLP, IEEE Xplore, and the ACM DL record. The
hull-dimension complexity statement is relayed from the abstract as surfaced in
search, not read from the full text.
