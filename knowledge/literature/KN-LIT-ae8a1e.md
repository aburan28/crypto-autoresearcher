---
id: KN-LIT-ae8a1e
type: literature
title: "A modular analysis of the Fujisaki-Okamoto transformation"
authors:
  - "Dennis Hofheinz"
  - "Kathrin Hövelmanns"
  - "Eike Kiltz"
year: 2017
venue: "TCC"
identifiers:
  eprint: "iacr:2017/604"
  doi: "10.1007/978-3-319-70500-2_12"
  arxiv: null
  url: "https://eprint.iacr.org/2017/604"
tags: [cca, kem, provable-security, code-based, fujisaki-okamoto, hhk, qrom, foundational, transform]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
**HHK**: a modular analysis of the Fujisaki–Okamoto transformation, decomposing
it into separate steps (`T`, `U^⊥`, `U^≠`, …) each with its own security
statement, so that a scheme designer can select the variant matching their
primitive's properties — perfect correctness or not, deterministic or not,
implicit or explicit rejection.

## Key claims (as reported)
- The FO transformation decomposes into modular components with individually provable security.
- Different variants suit different primitive properties; the choice is not cosmetic.

## Relevance to this program
The reference that Classic McEliece's KEM construction — and most of the NIST
PQC field — is analysed against. Held as the standard for how a **composition**
should be handled: rather than one monolithic proof, a decomposition whose parts
can be recombined and whose conditions are explicit.

That is the same structure this program's records are meant to have. A decision
cites the evidence records supporting it; each evidence record carries its own
scope; and the composed claim is only as strong as the weakest cited part. HHK
is the published exemplar of that discipline in security proofs.

Held with [[KN-LIT-7156]] (SXY), [[KN-LIT-7141]] (Bindel et al.) and
[[KN-LIT-7216]] (Bernstein–Persichetti), all already in the corpus.

## Not verified here
Citation verified against the IACR ePrint record for report 2017/604 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.1007/978-3-319-70500-2_12).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The individual transform statements and their tightness are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
