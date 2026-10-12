---
id: KN-LIT-0d9d28
type: literature
title: "On Index Calculus Algorithms for Subfield Curves"
authors:
  - "Steven D. Galbraith"
  - "Robert Granger"
  - "Simon-Philipp Merz"
  - "Christophe Petit"
year: 2021
venue: "LNCS (2021), pp. 115-138; ePrint 2020/1315"
identifiers:
  eprint: "iacr:2020/1315"
  arxiv: null
  doi: "10.1007/978-3-030-81652-0_5"
  url: null
tags: [index-calculus, koblitz, subfield-curves, frobenius, factor-base, linear-algebra, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

For Koblitz/subfield curves E/F_q with ECDLP in E(F_{q^n}), constructs Frobenius-invariant factor bases so that far fewer polynomial systems must be solved. This also shrinks the linear algebra and improves symmetry breaking, answering how Frobenius can speed up index calculus on subfield curves. Relevant to ECC2K-130-type curves on the IC side.

## Key claims (as reported)

- Up to 1/n fewer systems (the best possible) and linear algebra faster by a factor n^2.

## Relevance to this program

Frobenius-invariant factor bases for subfield (Koblitz) curves: up to 1/n fewer systems and n^2 faster linear algebra. IDEA-20260915-8fe0ef re-derived this mechanism while the paper sat in the corpus as a stub (KN-LIT-796; DEC-20260916-3c0cf5). The crypto repo cites its Lemma 4.1 (not re-read here) for the fact that no intermediate Frobenius-stable subspaces exist at n = 131, since ord_131(2) = 130 (research/notes/ecc2k130/NEXT_EXPERIMENT_DECISIONS_20260925.md).

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
Supersedes KN-LIT-796 (bulk stub or misattributed entry; see that file's `superseded_by`).
