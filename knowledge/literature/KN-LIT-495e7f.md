---
id: KN-LIT-495e7f
type: literature
title: "Structural cryptanalysis of McEliece schemes with compact keys"
authors:
  - "Jean-Charles Faugère"
  - "Ayoub Otmani"
  - "Ludovic Perret"
  - "Frédéric de Portzamparc"
  - "Jean-Pierre Tillich"
year: 2016
venue: "Designs, Codes and Cryptography"
identifiers:
  eprint: "iacr:2014/210"
  doi: "10.1007/s10623-015-0036-z"
  arxiv: null
  url: "https://eprint.iacr.org/2014/210"
tags: [code-based, mceliece, structural-attack, key-recovery, compact-keys, quasi-cyclic, quasi-dyadic, algebraic-cryptanalysis, variant-break]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
**Structural cryptanalysis of McEliece schemes with compact keys** — the journal
treatment of the attacks on quasi-cyclic and quasi-dyadic variants, whose
selling point was replacing McEliece's large public key with a compact
structured one.

## Key claims (as reported)
- The added structure enabling compact keys also enables structural key recovery.
- Applies to the quasi-cyclic and quasi-dyadic compact-key families, not to plain Goppa McEliece.

## Relevance to this program
The definitive statement of this sweep's most repeated lesson. McEliece's
large key is its most-criticised property; every serious attempt to fix it by
adding algebraic structure has been attacked
([[KN-LIT-2395]], [[KN-LIT-2d9edb]], [[KN-LIT-5792]], [[KN-LIT-19cf36]],
[[KN-LIT-b9bba7]]).

The transferable principle for this program's idea generator, stated plainly:
**structure introduced to improve efficiency is the first thing an attacker
looks for.** A proposal here that gains efficiency from added structure must
carry the corresponding null-object control — show the structure does not also
give the attacker something — before it is worth implementing.

**Does not bear on the ECDLP**, but the curve-side history of special
structures weakening instances is the same story.

## Not verified here
Citation verified against the IACR ePrint record for report 2014/210 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.1007/s10623-015-0036-z).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

Which parameter families fall and which survive is NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
