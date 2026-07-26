---
id: KN-LIT-2421
type: literature
title: "All-But-Many Encryption A New Framework for Fully-Equipped UC Commitments"
authors:
  - "Eiichiro Fujisaki"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a general framework for constructing non-interactive universally composable (UC) commitment schemes that are secure against adaptive adversaries in the non-erasure model under a re-usable common reference string. Previously, such “fully-equipped” UC commitment schemes have been known only in [5, 6], with strict expansion factor O(κ); meaning that to commit λ bits, communication strictly requires O(λκ) bits, where κ denotes the security parameter.

## Key claims (as reported)
- Efficient construction of a fully-equipped UC commitment scheme is a long-standing open problem.
- We introduce new abstraction, called all-but-many encryption (ABME), and prove that it captures a fully-equipped UC commitment scheme.
- We propose the first fully-equipped UC commitment scheme with optimal expansion factor Ω(1) from our ABME scheme related to the DCR assumption.
- We also provide an all-but-many lossy trapdoor function (ABM-LTF) [18] from our DCR-based ABME scheme, with a better lossy rate than [18].

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/88730227 (1).pdf`
- `downloads/88730227 (2).pdf`
- `downloads/88730227 (3).pdf`
- `downloads/88730227.pdf`
