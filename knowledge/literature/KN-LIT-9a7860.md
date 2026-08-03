---
id: KN-LIT-9a7860
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
year: 2025
venue: "NIST Internal Report, March 2025"
identifiers:
  eprint: null
  doi: "10.6028/NIST.IR.8545"
  arxiv: null
  url: "https://nvlpubs.nist.gov/nistpubs/ir/2025/NIST.IR.8545.pdf"
source_artifact:
  url: "https://nvlpubs.nist.gov/nistpubs/ir/2025/NIST.IR.8545.pdf"
  sha256: "d802f4849a52d18001533cef86e0950f31350643cc06881ee62b2382e1ea0e9d"
  retrieved_by: TASK-20260803-f3aece
  committed_locally: false
tags: [pqc, standardization, nist, mceliece, bike, hqc, sike, code-based, primary-source]
confidence: reported
citation_verified: read
citation_verified_note: >-
  `read` is earned by TASK-20260803-f3aece, which fetched this PDF on
  2026-08-03 (HTTP 200; URL, byte count and sha256 in that task's
  source_access_log.yaml) after csrc.nist.gov and nvlpubs.nist.gov proved
  REACHABLE, contrary to the expectation recorded in RQ-HQC-001.provenance.
  Validator TASK-20260803-409c5e re-acquired it and reproduced the quoted
  passage exactly, in full. The agent that drafted this entry
  (TASK-20260803-a53f73) did NOT read the document. Author list transcribed
  from the title page, not from recall. No local copy is committed.
added: "2026-08-03"
superseded_by: null
---

## Contribution
NIST's own status report closing the fourth round of the PQC standardization
process. The authoritative primary statement of Classic McEliece's standing in
the NIST process.

## Key claims (as reported)
- *"Classic McEliece is no longer under consideration for standardization as part
  of the current NIST PQC Standardization Process."*
- **The stated reasons are explicitly NOT security-based:** *"the interest
  expressed in Classic McEliece was limited, and having more standards to
  implement adds complexity to protocols and PQC migration"*, plus *"Concurrent
  standardization of Classic McEliece by NIST and ISO risks the creation of
  incompatible standards."*
- *"After the ISO standardization process has been completed, NIST may consider
  developing a standard for Classic McEliece based on the ISO standard."*
- As of March 2025 the report describes Classic McEliece as *"currently under
  consideration for standardization by the International Organization for
  Standardization (ISO)"*.
- The report also records that SIKE was broken early in the fourth round and
  removed from consideration.

## Relevance to this program
Settles the `standardization_status` that `GOAL-MCE-001` and `RQ-MCE-e65b3c` both
marked UNVERIFIED, and does so from the deciding body's own text rather than from
an inference about a project website's menu structure.

**Scoping consequence, and it cuts both ways.** NIST's non-selection carries **no
security implication in this document**, so it must not be cited as evidence for
or against the scheme's strength. Equally, this document does not confirm the ISO
completion the designers' site claims for June 2026 — it **predates** it and
describes ISO consideration as ongoing.

## Not verified here
Only the Classic McEliece passage and the title page were read closely; the
report's BIKE, HQC and SIKE analyses were **not**. **Whether NIST has acted
further since March 2025 was NOT established** — no later NIST document was
fetched. The ISO standardization claimed for June 2026 **postdates this report**
and rests on the designers' own site alone, with `iso.org` returning 403 twice
and the designation number not obtained (`EV-MCE-332f99` O-7). No local copy is
committed.
