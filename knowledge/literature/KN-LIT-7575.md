---
id: KN-LIT-7575
type: literature
title: Status Report on the Fourth Round of the NIST Post-Quantum Cryptography Standardization Process
authors: []
year: 2025
venue: NIST Interagency Report NIST IR 8545
identifiers:
  eprint: null
  doi: null
  url: https://nvlpubs.nist.gov/nistpubs/ir/2025/NIST.IR.8545.pdf
tags: [code-based, hqc, bike, mceliece, pqc, standardization, parameter-selection, survey]
confidence: reported
citation_verified: web
added: 2026-07-27
superseded_by: null
---

## Contribution
NIST's report concluding round 4 of the PQC standardization process. Announced
2025-03-11: HQC is selected for standardization as a backup KEM to ML-KEM;
BIKE and Classic McEliece are not standardized in this round. SIKE, the fourth
round-4 candidate, had already been broken.

## Key claims (as reported)
- HQC was preferred over BIKE on the grounds of a more mature security analysis
  -- specifically a better-understood decoding failure story.
- Classic McEliece was not standardized despite being regarded as conservatively
  secure; the stated obstacle is its public key size and consequent limited
  adoption prospects, not a cryptanalytic concern.
- A draft HQC standard is projected for 2026 with finalization around 2027.

## Relevance to this program
Fixes the external state of play for the code-based branch, which the corpus
otherwise only sees through attack papers. The important reading for this
program is the asymmetry NIST drew: BIKE lost on *analysis maturity* (an
epistemic property, KN-OPEN-022) and Classic McEliece lost on *engineering
cost* (KN-LIT-7573), while neither lost on a broken security claim. Those are
three distinct verdicts and the corpus should not flatten them into "not
selected."

## Not verified here
The report PDF was not fetched -- nvlpubs.nist.gov returned HTTP 403 to the
fetch tool used. Report number, title, year, URL, the 2025-03-11 announcement
date, and the selection rationale summarized above were confirmed via search
against NIST-hosted and reputable secondary coverage, not read from the report.
The author list is left empty because it was not confirmed; fill it before this
entry is cited for attribution. The 2026/2027 schedule is a projection reported
at announcement time and may have moved.
