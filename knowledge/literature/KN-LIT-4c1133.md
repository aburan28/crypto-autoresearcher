---
id: KN-LIT-4c1133
type: literature
title: Compact HQC with new (un)balance
authors: [Guan Chaofeng, Luo Lan, Jiang Haodong, Hou Jianhua, Yu Tong, Wang Hong, Li Kangquan, Qu Longjiang]
year: 2026
venue: 'Cryptology ePrint Archive, Paper 2026/461 (Preprint; received 2026-03-05, approved 2026-03-07)'
identifiers:
  eprint: iacr:2026/461
  doi: null
  arxiv: null
  url: https://eprint.iacr.org/2026/461
tags: [hqc, uhqc, code-based, kem, decryption-failure, decoding-failure-rate, dfr, information-set-decoding, unbalanced-errors, parameter-selection, quasi-cyclic, syndrome-decoding, pqc, adjacent, out-of-declared-scope]
confidence: reported
citation_verified: web
added: 2026-08-02
superseded_by: null
---

## Scope flag carried forward from acquisition
**This source was NOT in the declared target list of the task that found it.** It
surfaced during an ePrint title search run for a different target
(`TASK-20260802-6344ed`, BATCH-001, attempt 12) and was segregated in that task's
access log under `undeclared_discoveries` rather than retro-fitted into
`sources_sought`. The flag is preserved here because a target list that grows to
match what was found is not a target list. It is filed as a **lead**, at abstract
level only.

## Contribution (as reported by the abstract)
Argues that HQC's current bandwidth/efficiency/security balance rests on two
restrictions — that "the decryption-failure-rate (DFR) is directly configured to be
less than 2^{-λ} … rather than carefully determined by choosing conservative
parameters to resist known attacks as the Kyber team did in the design of NIST FIPS
203", and that "the error distribution in the underlying quasi-cyclic syndrome
decoding problem is restricted to be balanced" — and proposes quantitatively
evaluating the effect of removing both.

## Key claims (as reported)
Every claim below is the authors' own, relayed from the ePrint abstract at their own
hedging level. None has been checked by this program.

- "we first formalize the best-known decryption-failure attack against HQC, and derive
  an upper bound on the probability that an adversary triggers a decryption-failure
  event under realistic query and time limits, enabling an attack-aware upper bound on
  the secure DFR."
- "Second, we quantify how the weight distribution of (r₁, r₂, e) (the random
  low-weight polynomials used in encryption) affects the concrete cost of ISD attacks
  and DFR. This yields an *unbalanced* weight strategy that strictly lowers the DFR
  without sacrificing the targeted bit security, leading to a new variant called
  *Unbalanced HQC (UHQC)*."
- "By combining these analyses, we provide optimized parameters for UHQC. Across all
  NIST security levels, UHQC reduces bandwidth by 10-12% and improves runtime by
  6-8%."
- Framing: the abstract describes HQC as "recently selected by NIST for
  standardization". Category: public-key cryptography. Keywords as listed by the
  authors: code-based cryptography, Hamming Quasi-Cyclic, decryption failure,
  information set decoding, unbalanced errors.

## Relevance to this program
Directly adjacent to `GOAL-HQC-001` lane 1: an external reconsideration of the same
DFR-configuration choice that goal targets, including an explicit
attack-aware-DFR-bound proposal. Recording it means a later `/propose-ideas` pass on
`RQ-HQC-001` screens against it rather than rediscovering it. It also touches the ISD
costing lane (`TASK-20260802-0100a5`, `GOAL-SDITH-001`) by claiming that the weight
distribution of (r₁, r₂, e) changes concrete ISD cost.

**Forecloses**: nothing, at this provenance level. A proposal that overlaps its stated
claims should be screened against it and the PDF read before any novelty judgment is
made.

## Not verified here
- **Abstract only — the PDF was not fetched.** `citation_verified: web` is the honest
  ceiling under `knowledge/SEEDING.md`. Everything above is a search-free but
  abstract-level relay.
- The figures 10-12% and 6-8% are the authors' claims relayed verbatim; neither has
  been checked, and this program asserts nothing about whether the paper's analysis is
  correct, nor about what it would imply for HQC's security in either direction.
- The paper's own "best-known decryption-failure attack against HQC" baseline was not
  identified or checked, and its relationship to `KN-LIT-2141` (Guo–Johansson,
  ASIACRYPT 2020) was not examined.
- **Preprint status.** The ePrint metadata records "Preprint" with no publication
  info; not peer-reviewed as of this entry, and no DOI.

## Provenance
- ePrint abstract page fetched by `TASK-20260802-6344ed` on 2026-08-02
  (HTTP 200, 18 845 B, sha256
  `b325dd2bac7131a814ae0469010bc0637527953d98a7cd63f24295f0f46e0f8b`),
  re-fetched byte-identically by `TASK-20260802-b8d69f` (validator) and again by
  `TASK-20260802-63b16a` (this filing), which read every quoted sentence above off its
  own copy.
- ePrint History block: "2026-03-07: approved / 2026-03-05: received". BATCH-001's
  proposal described 2026-03-05 as "last updated"; that is the *received* date, and
  the last recorded event is 2026-03-07. Corrected here before filing.
- The page is dynamically served, so its sha256 pins what these three sessions
  received and is not guaranteed stable over time. No PDF is committed.
