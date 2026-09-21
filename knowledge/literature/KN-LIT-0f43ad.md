---
id: KN-LIT-0f43ad
type: literature
title: "Finding the permutation between equivalent linear codes: The support splitting algorithm"
authors:
  - "Nicolas Sendrier"
year: 2000
venue: "IEEE Transactions on Information Theory"
identifiers:
  eprint: null
  doi: "10.1109/18.850662"
  arxiv: null
  url: null
tags: [code-based, mceliece, structural-attack, key-recovery, support-splitting, code-equivalence, permutation-recovery, foundational]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
The **support splitting algorithm** (SSA): finds the permutation between two
equivalent linear codes, using a permutation-invariant signature (built from
hulls and punctured subcodes) computed per coordinate and refined until
coordinates are distinguished. Efficient for codes with small hull — which is
the generic case.

## Key claims (as reported)
- The permutation between equivalent linear codes can be found efficiently when the hull is small.
- The algorithm is a general tool for code equivalence, not tied to one code family.

## Relevance to this program
The definitive answer to "why is McEliece's secret permutation not the security
argument": for generic codes, **SSA finds it**. McEliece's security rests on not
knowing the *underlying Goppa structure*, and the permutation contributes
essentially nothing on its own.

That is a design lesson of the first order, and it generalises past codes: a
trapdoor that hides a structured object under a group action is only as strong
as the difficulty of the corresponding **equivalence problem**, which is a
different — and often much easier — question than the underlying hardness
assumption. Any proposal in this program that hides structure under a
relabelling must state which equivalence problem it is betting on, and cite what
is known about it.

Held with [[KN-LIT-b777d1]] and [[KN-LIT-d1a453]] as the code-equivalence
cluster.

## Not verified here
citation verified against the Crossref record (DOI 10.1109/18.850662).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The algorithm's complexity, its dependence on hull dimension, and the classes
where it fails are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
