---
id: KN-LIT-7675
type: literature
title: "Revisiting the Security of Approximate FHE with Noise-Flooding Countermeasures"
authors: []
year: 2025
venue: "PKC 2025"
identifiers:
  eprint: "iacr:2024/424"
  doi: "10.1007/978-3-031-91832-2_4"
  arxiv: null
  url: https://eprint.iacr.org/2024/424
tags: [fhe, ckks, approximate-fhe, noise-flooding, smudging, ind-cpa-d, key-recovery, bootstrapping-failure-probability, precision-loss, countermeasure-gap, unread-primary-source, rq-fhe-001]
confidence: unverified
citation_verified: web
added: "2026-08-01"
superseded_by: null
---

## Contribution
As reported: key-recovery attacks against approximate FHE schemes (CKKS) that
**do** deploy noise-flooding countermeasures, where the flooding variance was
calibrated from **non-worst-case noise estimation** rather than from the provably
sufficient bound.

The setup being attacked, as relayed: Li, Micciancio, Schultz and Sorrell proved that
adding Gaussian noise of sufficiently high variance before releasing a decrypted value
restores security for CKKS. The variance that provable security demands is very large,
and paying it costs a correspondingly large loss of message precision — so
implementations have incentive to calibrate flooding against *estimated* rather than
*worst-case* noise. This work is reported to show that shortcut is attackable, and
that the attack applies when the **bootstrapping failure probability is not
sufficiently low**.

## Relevance to this program
This is the "the countermeasure is also a parameter choice" entry, and it completes
the threat picture for `RQ-FHE-001` alongside `KN-LIT-7673` and `KN-LIT-7674`.

- **The pattern generalizes past FHE.** A proof-backed countermeasure exists; its
  provably-sufficient parameterization is too expensive to use; implementations ship a
  cheaper calibration justified by average-case reasoning; the average-case
  justification is where the attack lands. That is the same structural failure this
  program guards against when it forbids reporting a cost model's optimistic
  assumptions as if they were bounds
  (`docs/evidence-and-reproducibility.md`, baseline discipline).
- **It puts a third parameter axis in scope.** `KN-LIT-7673` concerns secret sparsity;
  this concerns flooding variance and bootstrapping failure probability. All three are
  tuned for performance, and all three are reported to have security consequences that
  the headline "128-bit" figure does not capture. A `RQ-FHE-001` deliverable that
  reports only lattice bit-security while ignoring these would be incomplete.
- Recorded explicitly as an **approximate-FHE** result: it does not transfer to exact
  schemes, where the corresponding handle is correctness failure (`KN-LIT-7674`).

## Not verified here
**The paper has not been read.** `eprint.iacr.org` and the Springer/ACM pages are
unreachable from this harness's network policy (proxy CONNECT 403, 2026-08-01).
Claims are relayed from web-search result summaries only. Hence
`confidence: unverified`.

NOT verified here:

- **The author list is unknown to this program and `authors` is deliberately empty.**
  The names Li, Micciancio, Schultz and Sorrell appear in the retrieved summary as
  authors of the **prior** noise-flooding security proof that this work revisits —
  attributing them as authors of *this* paper would be a fabrication, and this entry
  does not do it.
- The attack's model: what oracle access is assumed, how many queries, and whether
  recovery is of the full secret key or partial.
- What "not sufficiently low" bootstrapping failure probability means numerically,
  and whether shipped library defaults sit above or below that threshold. This is the
  single most decision-relevant unknown in the entry.
- Whether any library actually calibrates flooding the way the attack assumes. The
  summary asserts an incentive, not an observed implementation.
- Whether the ePrint version (2024/424) and the PKC 2025 proceedings version state
  the same results. The DOI and venue come from search-result metadata and are
  unconfirmed.
