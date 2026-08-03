---
id: KN-LIT-7620
type: literature
title: "NIST IR 8610: Status Report on the Second Round of the Additional Digital Signature Schemes for the NIST Post-Quantum Cryptography Standardization Process"
authors:
  - "Gorjan Alagic (NIST)"
  - "Maxime Bros (NIST, IZUM, Inc.)"
  - "Pierre Ciadoux (NIST)"
  - "Quynh Dang (NIST)"
  - "Thinh Dang (NIST)"
  - "John Kelsey (NIST)"
  - "Jacob Lichtinger (NIST)"
  - "Yi-Kai Liu (NIST)"
  - "Carl Miller (NIST)"
  - "Dustin Moody (NIST)"
  - "Rene Peralta (NIST)"
  - "Ray Perlner (NIST)"
  - "Angela Robinson (NIST)"
  - "Hamilton Silberg (NIST)"
  - "Daniel Smith-Tone (NIST)"
  - "Noah Waller (NIST)"
year: 2026
venue: 'NIST Internal Report (NIST IR 8610), final; DOI 10.6028/NIST.IR.8610'
identifiers:
  eprint: null
  doi: 10.6028/NIST.IR.8610
  arxiv: null
  url: https://csrc.nist.gov/pubs/ir/8610/final
tags: [nist, pqc, additional-digital-signatures, round-3, status-report, standardization, faest, primary-source]
confidence: reported
citation_verified: true
added: "2026-07-31"
superseded_by: null
---

## Citation (verified against the CSRC publication page)

Gorjan Alagic et al. (16 NIST authors, listed in frontmatter). *Status
Report on the Second Round of the Additional Digital Signature Schemes for
the NIST Post-Quantum Cryptography Standardization Process.* NIST Internal
Report 8610, final. **Published May 2026; document history: 05/14/26: IR
8610 (Final).** DOI: 10.6028/NIST.IR.8610. Download URL:
https://nvlpubs.nist.gov/nistpubs/ir/2026/NIST.IR.8610.pdf

## What it says (verified from the CSRC abstract)

This is the report that announces the selection of the **nine Round-3
candidates** of the Additional Digital Signatures process, based on public
feedback and internal reviews of the second-round candidates: **FAEST,
HAWK, MAYO, MQOM, QR-UOV, SDitH, SNOVA, SQIsign, and UOV**. It describes the
evaluation criteria and selection process of the Second Round. Any scheme
eventually selected will augment FIPS 204 (ML-DSA), FIPS 205 (SLH-DSA),
FIPS 186-5 (DSS), and SP 800-208.

## Naming precision (important for citing)

The handoff that created this entry (TASK-20260731-012) called IR 8610 the
"Round-3 status report". The report's exact title is the status report on
the **Second Round**; it is the document that *announces and justifies* the
Round-3 selection. Cite it as the second-round status report, not as a
report on Round-3 results (Round-3 has only just begun; tweaks due
2026-08-14, per NIST's announcement of 2026-05-14).

## Verification performed

- `https://csrc.nist.gov/pubs/ir/8610/final` — fetched 200. Title, full
  author list, abstract, DOI, PDF download URL, keywords, and document
  history read from the primary CSRC publication page.
- `https://csrc.nist.gov/projects/pqc-dig-sig/round-3-additional-signatures`
  — fetched 200 (this is the fallback source named in the handoff; it was
  reachable, so IR 8610 is the primary entry and this page is corroborating
  context). The page confirms FAEST under "Symmetric-based Signatures" with
  the 12-member Round-3 submitter list (matching faest.info/authors.html),
  and notes the HAWK withdrawal visible at fetch time.
- The IR 8610 PDF itself was not downloaded (only its metadata page); the
  abstract and roster above are page-level verified.

## Notes for this program

- Corrects RQ-FAEST-001 provenance: it recorded that csrc.nist.gov and
  nist.gov were unreachable from this harness (proxy CONNECT 403). In this
  session both `csrc.nist.gov/pubs/ir/8610/final` and the round-3 program
  page were fetched successfully (HTTP 200). The network obstruction
  recorded in RQ-FAEST-001 is no longer observed; re-verify if it matters
  for later tasks.
- FAEST's advancement to Round 3 on 2026-05-14 and the 2026-08-14 tweaks
  deadline (both already recorded in GOAL-FAEST-001 / RQ-FAEST-001) are
  confirmed by this primary source.

## Limits

- `citation_verified: true` covers the bibliographic identity, abstract, and
  history as served by the primary CSRC page on 2026-07-31. The full report
  text was not read; no per-scheme technical claims from inside IR 8610 are
  asserted here.
