---
id: KN-LIT-a85246
type: literature
title: "Multi-instance security degradation of code-based KEMs"
authors:
  - "Alexander May"
  - "Gabriel Sá Diogo"
year: 2026
venue: null
identifiers:
  eprint: "iacr:2026/517"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/517"
tags: [isd, syndrome-decoding, code-based, mceliece, concrete-security, multi-target, kem, classic-mceliece, bike, hqc, provable-security]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
Studies how the security of code-based KEMs degrades when an attacker faces
**many instances at once** rather than one. The multi-instance (multi-user /
multi-target) setting is the practically relevant one for a deployed KEM, and
the question is whether attacking `N` independent instances costs `N` times a
single attack or meaningfully less.

## Key claims (as reported)
- Security of code-based KEMs degrades in the multi-instance setting — the paper's title states degradation, not its absence.
- Framed against code-based KEMs generically rather than one scheme.

## Relevance to this program
Directly relevant as **methodology**, not as a code-based result. The
single-instance-to-multi-instance gap is a standard way real deployed cost
diverges from the headline security level, and it is one of the omitted
end-to-end costs the red-team role is meant to look for.

The code-based analogue of Sendrier's "decoding one out of many"
([[KN-LIT-0258c8]]) is the classical statement of this effect; this is the 2026
KEM-level treatment.

For the ECDLP the corresponding effect is well known (batch/multi-target
discrete logarithm, where `N` targets cost roughly `sqrt(N)` times one), so the
transferable content here is the accounting discipline, not the bound.

## Not verified here
Citation verified against the IACR ePrint record for report 2026/517 (title and author list checked) on 2026-08-03.

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The size of the claimed degradation, whether it applies to Classic McEliece
specifically or only to some code-based KEMs, and the model in which it is
proven are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
