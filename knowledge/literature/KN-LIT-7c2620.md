---
id: KN-LIT-7c2620
type: literature
title: "Careful with the Ring: Enhanced Hybrid Decoding Attacks against Module/Ring-LWE"
authors: []
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/366"
  doi: null
  arxiv: null
  url: https://eprint.iacr.org/2026/366
tags: [ring-lwe, module-lwe, hybrid-attack, decoding-attack, sparse-secret, ternary-secret, fhe-parameters, lattice-estimator, concrete-security, 128-bit-security, bootstrapping-cost, unread-primary-source, rq-fhe-001]
confidence: unverified
citation_verified: web
added: "2026-08-01"
superseded_by: null
---

## Contribution
As reported: an enhanced hybrid **decoding** attack against Module/Ring-LWE that
exploits the **ring structure** to accelerate both the guessing and the decoding
phases of the classical hybrid attack. The reported improvement is a factor of
**O(N) in the sparse-secret setting** relative to the prior hybrid decoding attack,
and **up to 13 bits** of complexity improvement over the best previously known
attacks.

The consequence reported for practice: applied to recent sparse Ring-LWE parameter
sets used in FHE schemes, **12 of 16 examined parameter sets fall below their
targeted 128-bit security level**. Parameter sources are referred to in the retrieved
summary by the labels `JM22`, `CCKS23`, `BCKS24`, `CHKS25`, and `AKP25`; this program
has **not** resolved those labels to citations and does not guess at them.

## Relevance to this program
This is the anchor entry for `RQ-FHE-001` and the reason that question exists.

Three reasons it matters beyond FHE:

- **Sparse secrets are load-bearing, not incidental.** Small-Hamming-weight secrets
  are chosen precisely to make bootstrapping affordable. A security loss that is
  specific to the sparse regime therefore cannot be repaired by a free parameter
  tweak — the repair is paid for in bootstrapping throughput. Any record citing
  this entry must cost the repair, not just report the bit loss.
- **It is adjacent to work this program already has open.** `RQ-MLKEM-001` lists
  "hybrid and decoding attacks" and "module and ring structure exploitation" in
  scope. The technique family is shared even though the target parameters are not:
  ML-KEM does not use sparse secrets in the FHE sense, so a result here does **not**
  transfer to ML-KEM, and no record may use this entry to argue about ML-KEM.
- **The verification architecture transfers unmodified.** A recovered sparse secret
  is checkable against the public samples by independent recomputation, exactly as a
  claimed discrete log is checkable by recomputing `k*P`
  (`docs/claims-and-verification.md`). Whatever this program does here, it can
  certify.

Context that makes the timing sharp, itself unverified and recorded only as
motivation: the HomomorphicEncryption.org Standard v1.1 (2024) is reported to specify
**no** concrete sparse-secret parameters, on the stated grounds that their security
is not yet well understood, and ISO/IEC DIS 28033-1 is reported to be near
publication. If both are true, there is no agreed sparse-secret parameter table for
this attack to be measured against.

## Not verified here
**The paper has not been read.** `eprint.iacr.org` is unreachable from this harness's
network policy — proxy CONNECT returns 403, confirmed against
`$HTTPS_PROXY/__agentproxy/status` on 2026-08-01 — so not even the abstract page was
retrieved. Every claim above is relayed from **web-search result summaries**, which is
one step weaker than the abstract-level `reported` provenance used elsewhere in this
corpus. Hence `confidence: unverified`.

NOT verified here, and not to be cited as established by any record:

- **The author list is unknown to this program.** `authors` is deliberately empty
  rather than guessed.
- The O(N) sparse-secret speedup, the 13-bit figure, and the 12-of-16 count — none
  has been checked against the paper, and the retrieved summary does not state the
  ring degrees, moduli, Hamming weights, or memory model behind them.
- Whether the 16 parameter sets are **shipped library defaults** or parameter sets
  that appear only in papers. This distinction decides whether the result touches
  deployed systems at all, and the summary does not settle it.
- Whether any recovery was **demonstrated at any scale**, or the bit counts are
  estimator output. An estimator recount and an executed attack are different claims;
  this entry asserts neither.
- Whether the work is peer-reviewed. It is recorded as an ePrint preprint with no
  venue.

Reading this paper is a blocking prerequisite for `RQ-FHE-001` and requires either a
network-policy change permitting `eprint.iacr.org` or out-of-band delivery of the PDF.
