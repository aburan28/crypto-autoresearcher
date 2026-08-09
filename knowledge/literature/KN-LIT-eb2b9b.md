---
id: KN-LIT-eb2b9b
type: literature
title: "NIST IR 8545: Status Report on the Fourth Round of the NIST Post-Quantum Cryptography Standardization Process"
authors:
  - "Gorjan Alagic"
  - "Maxime Bros"
  - "Pierre Ciadoux"
  - "David Cooper"
  - "Quynh Dang"
  - "Thinh Dang"
  - "John Kelsey"
  - "Jacob Lichtinger"
  - "Yi-Kai Liu"
  - "Carl Miller"
  - "Dustin Moody"
  - "Rene Peralta"
  - "Ray Perlner"
  - "Angela Robinson"
  - "Hamilton Silberg"
  - "Daniel Smith-Tone"
  - "Noah Waller"
authors_note: >-
  PROVENANCE OF THIS LIST, because an author list is exactly the field that gets
  invented: it is copied from TASK-20260803-f3aece's proposed-entry draft, which
  states it was transcribed from the title page of the PDF that task retrieved
  (sha256 d802f484…). It is NOT quoted in any transcription deliverable and was
  NOT re-verified by TASK-20260808-f9374d, which fetched nothing. It is carried
  because discarding a recorded transcription is also a loss; it is flagged
  because it is the least-corroborated field in this entry.
year: 2025
venue: "NIST Internal Report, March 2025"
identifiers:
  eprint: null
  doi: "10.6028/NIST.IR.8545"
  arxiv: null
  url: "https://nvlpubs.nist.gov/nistpubs/ir/2025/NIST.IR.8545.pdf"
  sha256: "d802f4849a52d18001533cef86e0950f31350643cc06881ee62b2382e1ea0e9d"
tags: [pqc, standardization, nist, mceliece, bike, hqc, code-based, primary-source]
confidence: reported
citation_verified: web
citation_verified_note: >-
  NOT `read`. This report was retrieved and read by TASK-20260803-f3aece
  (BATCH-001) on 2026-08-03 — HTTP 200, 588999 bytes, sha256 d802f484…, 34
  pages, `source_access_log.yaml` seq 14, reached via the csrc.nist.gov landing
  page at seq 13 — and the Classic McEliece passage is quoted at length in that
  task's `standardization_status.md`. TASK-20260808-f9374d, which files this
  entry, performed NO retrieval and read no PDF. Per RQ-MCE-e65b3c's inherited
  caution from KN-OPEN-3f7a21, a `read` this task cannot attest is not claimed.
  NOTE ON ROUTE RISK: that retrieval succeeded against an inherited program
  record of NIST domains as UNREACHABLE (f3aece observation O1), so the route is
  NOT known to be stable and a re-fetch may fail. A failed re-fetch would be a
  recorded outcome, never evidence about the document.
added: "2026-08-08"
superseded_by: null
---

## Contribution

NIST's own status report closing the fourth round of the PQC standardization
process. It is the authoritative primary statement of Classic McEliece's standing
in the NIST process — the deciding body's own text, rather than an inference from
a project website's menu structure.

## Key claims (as reported)

All quoted from `TASK-20260803-f3aece/standardization_status.md` §2, which
reproduces the Classic McEliece passage at length from the PDF at sha256
`d802f484…`. Not re-read in this environment.

- *"Classic McEliece is no longer under consideration for standardization as part
  of the current NIST PQC Standardization Process."*
- **The stated reasons are not security-based.** *"the interest expressed in
  Classic McEliece was limited, and having more standards to implement adds
  complexity to protocols and PQC migration"*, and *"Concurrent standardization
  of Classic McEliece by NIST and ISO risks the creation of incompatible
  standards."*
- The report also records interest in the scheme: better performance than BIKE or
  HQC where a public key is transferred once and reused for several
  encapsulations (file encryption, VPNs), and *"some interest in Classic McEliece
  based on the perception that it is a conservative choice."*
- A door is left explicitly open: *"After the ISO standardization process has been
  completed, NIST may consider developing a standard for Classic McEliece based
  on the ISO standard."*
- As of March 2025 the report describes Classic McEliece as *"currently under
  consideration for standardization by the International Organization for
  Standardization (ISO)"*.

## Relevance to this program

Settles the `standardization_status` field that `GOAL-MCE-001` and
`RQ-MCE-e65b3c` both marked UNVERIFIED. `RQ-MCE-e65b3c` currently asserts that
status *"transcribed from the Classic McEliece project's own site structure … and
is UNVERIFIED here — neither page was fetched"*; this entry is the primary text
that requirement asked for. **Updating that ledger record is a separate
Coordinator act and is not performed by filing this entry.**

**The scoping consequence is the important part, and it cuts against a tempting
misreading:** NIST's non-selection carries **no** security implication in this
document. It must not be cited as evidence for or against the scheme's strength,
in either direction. `RQ-MCE-e65b3c`'s calibration argument — that the 1978
construction stands while every structured variant proposed for efficiency was
broken — is untouched by this report.

## Not verified here

- **This task read nothing.** `TASK-20260808-f9374d` fetched no URL and computed
  no hash.
- Only the Classic McEliece passage and the title page were read even by
  `TASK-20260803-f3aece`. **The report's BIKE, HQC and SIKE analyses were not
  read by anyone in this program**, and no claim about them is made here. A
  statement about SIKE that appeared in the BATCH-001 proposed-entry draft has
  been **deliberately dropped**: it is traceable to no quotation in any
  transcription deliverable and sits inside the same draft's own admission that
  the SIKE analysis was not read. Relaying it would have been an unsupported
  citation.
- Whether NIST has acted further since March 2025 is **not established**: no
  later NIST document was fetched, and the ISO completion this program's
  BATCH-001 artifacts discuss postdates this report.
- The **ISO standard's designation number was NOT obtained.** Two `iso.org`
  endpoints returned HTTP 403 on 2026-08-03 and were not circumvented; that is a
  recorded outcome, not evidence (AGENTS.md rule 5). The ISO fact currently rests
  on the designers' own statement, not on ISO's catalogue.
- The `bike` and `hqc` tags reflect the report's declared scope, not a read of
  those sections.

## Local copies

None. Not committed to this repository. The `sha256` in `identifiers` is the
integrity anchor.
