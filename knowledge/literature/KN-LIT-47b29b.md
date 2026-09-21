---
id: KN-LIT-47b29b
type: literature
title: "Progressive sieving-style information-set decoding algorithm"
authors:
  - "Tong Yu"
  - "Haodong Jiang"
  - "Hong Wang"
  - "Rongmao Chen"
  - "Qingfeng Cheng"
  - "Xinyi Huang"
  - "Yuefei Zhu. 2026"
year: 2026
venue: null
identifiers:
  eprint: "iacr:2026/633"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/633"
tags: [isd, syndrome-decoding, code-based, mceliece, concrete-security, sieving, classic-mceliece, cost-model]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
Proposes a **progressive** variant of sieving-style information-set decoding.
Sieving-style ISD (introduced by Guo–Johansson–Nguyen, [[KN-LIT-01f731]])
replaces the birthday/meet-in-the-middle inner step of the BJMM/MMT family with
a sieve over a list of near-collision candidates. "Progressive" is the standard
device of running the search with a gradually relaxed parameter rather than
committing to one optimised choice up front, so that easy instances terminate
early and the expected cost falls below the worst-case optimum.

## Key claims (as reported)
- An improved sieving-style ISD algorithm, positioned against the existing sieving-style line rather than against plain BJMM.
- The improvement is claimed as a *progressive* strategy — the paper's own framing — which by construction affects average-case running time rather than the asymptotic exponent alone.

## Relevance to this program
Held as current state of the art tracking for the ISD family. This program's
interest in ISD is methodological rather than direct: ISD is the best-studied
example of a cryptanalytic family where a **long series of constant-factor and
low-order improvements did not move the security exponent much**, which is the
comparison class `docs/target-result-profile.md` uses when judging whether a
proposed ECDLP result is exponent-moving or merely constant-factor.

A "progressive" reformulation is exactly the kind of average-case-versus-
worst-case distinction this program must state explicitly in its own evidence
records: a speedup on easy instances is not a security-exponent claim.

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2026/633 (title and author list checked) on 2026-08-03.

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The magnitude of the claimed improvement, the parameter regime in which it
holds, and whether it changes any Classic McEliece parameter set's security
estimate are NOT recorded here — the entry was written without the paper.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
