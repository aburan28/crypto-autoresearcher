---
id: KN-LIT-8aff72
type: literature
title: "EcGFp5: a Specialized Elliptic Curve (read at source)"
authors: [Thomas Pornin]
year: 2022
venue: IACR Cryptology ePrint Archive, Report 2022/274
identifiers:
  eprint: "2022/274"
  doi: null
  arxiv: null
  url: https://eprint.iacr.org/2022/274
  source_package: inputs/PORNIN-2022-274-ECGFP5
tags: [ecgfp5, goldilocks, quintic-extension, elliptic-curve, miden, stark,
  gaudry, diem, ghs, index-calculus, pfp5, primary-source, retrieved]
confidence: reported
citation_verified: read
provenance: retrieved
frozen_source: inputs/PORNIN-2022-274-ECGFP5/
source_record: SRC-PORNIN-2022-274-ECGFP5
verified_by: cloud-agent session on branch cursor/gfpn-ideas-intake-dcc3, 2026-09-20; frozen bytes and hashes in inputs/PORNIN-2022-274-ECGFP5/provenance.json
added: 2026-09-20
superseded_by: null
---

## Why this record exists

GFPN intake cites EcGFp5 design numbers (field, Gaudry lower bound ≥ 2^142,
Diem/Gaudry references). Under AGENTS.md rule 9 those numbers support nothing
until the PDF is frozen and read. This record is that freeze.

## What was read

Full extracted text of ePrint 2022/274 (`paper_fulltext.md`). Construction:
curve over `GF(p^5)` with `p = 2^64 - 2^32 + 1`, group of non-`n`-torsion
points with neutral `(0,0)` (the unique order-2 point), sum `P ⊕ Q = P + Q + N`.
Security section costs Gaudry's attack at k = 5 as total theoretical complexity
at least `2^142`, "well beyond the target 128-bit level", and cites Diem on
odd-characteristic GHS recommending prime extension degree.

## What this record does not assert

No measured PDP cost, no oracle-assisted static-DH analysis, no claim about
EcMasFp5. The ≥ 2^142 figure is the paper's theoretical lower bound under its
stated model, not a measurement by this program.
