---
id: KN-LIT-7637
type: literature
title: "FAEST: Algorithm Specifications (v2.0, latest published; no Round-3 specification exists as of 2026-07-31)"
authors:
  - "Carsten Baum"
  - "Ward Beullens"
  - "Lennart Braun"
  - "Cyprien Delpech de Saint Guilhem"
  - "Michael Klooß"
  - "Christian Majenz"
  - "Shibam Mukherjee"
  - "Emmanuela Orsini"
  - "Sebastian Ramacher"
  - "Christian Rechberger"
  - "Lawrence Roy"
  - "Peter Scholl"
year: 2024
venue: 'NIST Additional Digital Signatures Round-2 submission specification, published at faest.info'
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: https://faest.info/faest-spec-v2.0.pdf
tags: [faest, vole-in-the-head, mpc-in-the-head, digital-signatures, aes, post-quantum, nist-pqc, additional-signatures, specification, primary-source]
confidence: reported
citation_verified: true
added: "2026-07-31"
superseded_by: null
---

## What this entry is

The **latest published FAEST specification document**. Per the official FAEST
site (https://faest.info/resources.html, fetched 2026-07-31), the document
history is:

- **v2.0** — `/faest-spec-v2.0.pdf` — included in the FAEST **Round-2**
  submission to NIST. Main changes over v1.1: improved batch vector
  commitments (smaller opening, faster AES-based leaf commitments); degree-3
  constraints to prove AES in zero-knowledge (further reducing signature
  size); improved security analysis including a **tight QROM proof**.
- v1.1 — `/faest-spec-v1.1.pdf` — fixes to the Round-1-era document
  (performance tables, author order, one-way-function description and
  security estimates).
- v1.0 — `/faest-spec-v1.0.pdf` — Round-1 submission specification.

## Round-3 status — read this before citing

**No FAEST Round-3 specification has been published as of 2026-07-31.** The
handoff that created this entry (TASK-20260731-012) asked for the "Round-3
specification"; fetching the primary source (faest.info) shows that the
latest published specification is **v2.0, the Round-2 submission document**.
NIST's Additional Digital Signatures Round-3 program gives teams until
**2026-08-14** to submit Round-3 "tweaks" (updated specifications and
implementations); as of this entry's date those tweaks are not public.
Consequently:

- Any experiment designed now must be specified against **spec v2.0**
  (verified), with the Round-3 tweak pending explicitly tracked.
- This entry is **not** a Round-3 document; citing it as one would be wrong.

## Verification performed

- `https://faest.info` (landing page) — fetched 200; confirms design
  (AES-128/192/256 one-way function, VOLE-in-the-head, Even-Mansour variant,
  tau communication-computation tradeoff, s/f settings per level).
- `https://faest.info/resources.html` — fetched 200; spec version list and
  Round-2/1 submission links (Round-2 submission bundle on Google Drive,
  49 MB, "includes specification, source code and test vectors").
- `https://faest.info/faest-spec-v2.0.pdf` — fetched 200; served as a real
  PDF (`%PDF-1.5` header observed in the raw bytes). The PDF body text was
  NOT extractable in this session (no text layer produced by the fetch
  pipeline; full binary dump saved by the runtime), so content-level claims
  above are taken from the official resources page, not from reading the
  PDF.
- `https://faest.info/authors.html` — fetched 200; team roster of 12 matches
  the NIST Round-3 submitter list for FAEST (cross-verified, see KN-LIT-7620).

## Limits

- `citation_verified: true` applies to the **v2.0 document's existence and
  identity** at the recorded URL only. The internal text of the PDF was not
  read; all content summaries in this entry come from the official site's
  own descriptions.
- Year is recorded as 2024 (Round-2 submission period per NIST process);
  the v2.0 document's exact publication date was not verifiable from the
  fetched pages and should not be quoted.
- Author list: the 12-member FAEST team as listed on faest.info/authors.html
  and on NIST's Round-3 page (identical). The paper-author subset (7
  authors) is recorded in KN-LIT-7638.
