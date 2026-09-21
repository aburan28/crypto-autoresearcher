---
id: KN-LIT-2d9edb
type: literature
title: "An algebraic attack against McEliece-like cryptosystems based on BCH codes"
authors:
  - "Freja Elbro"
  - "Christian Majenz"
year: 2023
venue: "ITW"
identifiers:
  eprint: "iacr:2022/1715"
  doi: "10.1109/itw55543.2023.10161620"
  arxiv: null
  url: "https://eprint.iacr.org/2022/1715"
tags: [code-based, mceliece, structural-attack, key-recovery, bch-codes, algebraic-cryptanalysis, variant-break]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
An algebraic attack against **McEliece-like cryptosystems based on BCH codes**.
BCH codes have more algebraic structure than Goppa codes and had been proposed
as a way to shrink keys; the attack exploits that structure.

## Key claims (as reported)
- An algebraic key-recovery attack against BCH-based McEliece variants.
- Scoped to BCH instantiations, not to Goppa-based Classic McEliece.

## Relevance to this program
One entry in the long list of **structure-for-efficiency variants that fell**:
BCH here, quasi-cyclic and quasi-dyadic in [[KN-LIT-2395]] and
[[KN-LIT-495e7f]], wild McEliece over quadratic extensions in [[KN-LIT-5792]],
GRS codes in [[KN-LIT-19cf36]].

Classic McEliece's design answer — keep plain binary Goppa codes and accept the
large key — is the conservative choice vindicated by that list. The general
principle is the one this program's lossy-projection test encodes: **added
structure is an attack surface, and the burden is on the variant to show its
structure is not usable.**

**Does not bear on the ECDLP**, though the analogous curve-side statement —
special structure chosen for efficiency has repeatedly weakened instances — is
the same lesson.

## Not verified here
Citation verified against the IACR ePrint record for report 2022/1715 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.1109/itw55543.2023.10161620).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

Which BCH parameters are attacked and at what cost is NOT recorded here. The
companion long-form treatment is Elbro's thesis, [[KN-LIT-b03de7]].

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
