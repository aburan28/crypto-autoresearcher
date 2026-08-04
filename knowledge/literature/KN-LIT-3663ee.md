---
id: KN-LIT-3663ee
type: literature
title: "Equivalent Goppa codes and trapdoors to McEliece's public key cryptosystem"
authors:
  - "J. Keith Gibson"
year: 1991
venue: "Eurocrypt"
identifiers:
  eprint: null
  doi: "10.1007/3-540-46416-6_46"
  arxiv: null
  url: null
tags: [code-based, mceliece, structural-attack, key-recovery, goppa, equivalent-keys, key-space, foundational]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
**Equivalent Goppa codes and trapdoors** to McEliece's cryptosystem: many
distinct secret keys yield the same or equivalent public keys, so the effective
key space is smaller than the parameter description suggests, and a trapdoor
need not be *the* secret key to be usable.

## Key claims (as reported)
- Distinct Goppa parameter choices can yield equivalent codes.
- The effective key space is therefore smaller than the naive count.
- An attacker needs any equivalent trapdoor, not the original secret.

## Relevance to this program
Contains the single most transferable idea in this section: **an attacker needs
any equivalent trapdoor, not the specific secret.** Security arguments that
count secrets rather than equivalence classes overstate the difficulty, and the
gap can be large.

The direct application here is to brute-force baselines — [[KN-LIT-f1073f]] is
the 2025 paper still working out the honest count — and, more generally, to any
claim this program makes about the size of a search space. Under
`docs/inventor-protocol.md` the null-object control is meant to catch exactly
this: is the space you are searching the space that actually matters, or a
labelled cover of it?

## Not verified here
citation verified against the Crossref record (DOI 10.1007/3-540-46416-6_46).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The size of the equivalence classes and the resulting key-space reduction are
NOT recorded here. No online copy listed.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
