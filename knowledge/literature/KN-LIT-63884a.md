---
id: KN-LIT-63884a
type: literature
title: "Key-recovery fault injection attack on the Classic McEliece KEM"
authors:
  - "Sabine Pircher"
  - "Johannes Geier"
  - "Julian Danner"
  - "Daniel Mueller-Gritschneder"
  - "Antonia Wachter-Zeh"
year: 2022
venue: null
identifiers:
  eprint: "iacr:2022/1529"
  doi: "10.1007/978-3-031-29689-5_3"
  arxiv: null
  url: "https://eprint.iacr.org/2022/1529"
tags: [side-channel, code-based, classic-mceliece, implementation-attack, fault-injection, key-recovery, kem]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
A **key-recovery fault injection attack** on the Classic McEliece KEM. Fault
attacks are active: the attacker perturbs the computation and reasons from the
faulty output, rather than passively observing.

## Key claims (as reported)
- Injected faults during Classic McEliece operation enable key recovery.
- Active attack model.

## Relevance to this program
Held with [[KN-LIT-4912]] (laser fault injection, already in the corpus) as the
fault-attack pair. The active model raises a distinct question from passive
leakage — **integrity of the computation**, not confidentiality of its
intermediate values — and the countermeasures differ accordingly.

For this program the analogue is the integrity of its own execution pipeline:
this is why run manifests record their inputs and why certificates are
re-verified rather than trusted from the run that produced them.

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2022/1529 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.1007/978-3-031-29689-5_3).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The fault model, injection method and success rate are NOT recorded here. Note
that this paper is distinct from Cayrel et al.'s laser fault injection attack
[[KN-LIT-4912]]; an automated title match conflated them and they were separated
by hand during dedup.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
