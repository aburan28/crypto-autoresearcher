---
id: KN-LIT-7c6f53
type: literature
title: "Cryptanalysis of the original McEliece cryptosystem"
authors:
  - "Anne Canteaut"
  - "Nicolas Sendrier"
year: 1998
venue: "Asiacrypt"
identifiers:
  eprint: null
  doi: "10.1007/3-540-49649-1_16"
  arxiv: null
  url: "https://www.rocq.inria.fr/secret/Anne.Canteaut/Publications/Canteaut_Sendrier98.pdf"
tags: [isd, syndrome-decoding, code-based, mceliece, canteaut-chabaud, cryptanalysis, original-parameters, record]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
Cryptanalysis of the **original McEliece parameters** (`n = 1024`, `k = 524`,
`t = 50`), using the authors' improved minimum-weight-word algorithm
([[KN-LIT-f390dc]]). Establishes that McEliece's 1978 parameter choice
([[KN-LIT-141bac]]) no longer provides adequate security, while leaving the
system itself standing at larger parameters.

## Key claims (as reported)
- The original 1978 parameter set is attackable with then-feasible resources; the work factor is far below its intended level.
- The attack is generic decoding — it does not exploit Goppa structure, so the conclusion is about parameters, not about the trapdoor.

## Relevance to this program
The textbook example of the distinction this program is required to preserve
under rule 4: **parameters fell; the system did not.** A scoped negative result
about one parameter set is not a break of the underlying problem, and reporting
it as one would be overclaiming.

It is also the historical reason Classic McEliece's parameters are as
conservative as they are — the design absorbed this attack by moving
parameters, which is exactly what a well-scoped cryptanalytic result is
supposed to enable.

## Not verified here
citation verified against the Crossref record (DOI 10.1007/3-540-49649-1_16).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The claimed work factor and the machine-time estimate are NOT recorded here.
Note that an automated title match against [[KN-LIT-3281]] ("Cryptanalysis of
the Sidelnikov cryptosystem") was checked by hand and rejected — different
paper.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
