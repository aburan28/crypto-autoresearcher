---
id: KN-LIT-5677ae
type: literature
title: "Security analysis of the Classic McEliece, HQC and BIKE schemes in low memory"
authors:
  - "Yu Li"
  - "Li-Ping Wang"
year: 2023
venue: "Journal of Information Security and Applications"
identifiers:
  eprint: "iacr:2023/428"
  doi: "10.1016/j.jisa.2023.103651"
  arxiv: null
  url: "https://eprint.iacr.org/2023/428"
tags: [isd, syndrome-decoding, code-based, mceliece, concrete-security, classic-mceliece, bike, hqc, memory-constrained, nist-pqc, cost-model]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
Security analysis of **Classic McEliece, HQC and BIKE under low-memory
constraints** — that is, re-costing the standard ISD attacks when the attacker
cannot afford the memory the best variants assume. The practical question is
whether the published security levels rest on memory nobody would actually
build.

## Key claims (as reported)
- Security of the three NIST code-based candidates is analysed under explicit memory limits.
- Applies to the standardised/round-4 parameter sets, not to toy instances.

## Relevance to this program
The most directly load-bearing of the low-memory entries, because it is stated
against the **actual deployed parameter sets** rather than asymptotically.
Under this program's tier rules that is the difference between a crypto-scale
and a toy-scale claim, and it is the standard `docs/target-result-profile.md`
holds this program's own results to: validate at cryptographic scale or say
plainly that you did not.

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2023/428 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.1016/j.jisa.2023.103651).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The specific memory bounds imposed, the resulting security estimates, and
whether they move any parameter set's claimed level are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
