---
id: KN-LIT-d0370b
type: literature
title: "New Exchanged Boomerang Distinguishers for 5-Round AES"
authors:
  - "Hanbeom Shin"
  - "Seonkyu Kim"
  - "Byoungjin Seok"
  - "Dongjae Lee"
  - "Deukjo Hong"
  - "Jaechul Sung"
  - "Seokhie Hong"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/248"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/248"
tags: [cryptanalysis, symmetric, aes, distinguisher, boomerang, exchanged-boomerang, yoyo]
confidence: reported
citation_verified: read
added: "2026-09-10"
superseded_by: null
supersedes: KN-LIT-1424
---

## Contribution

Secret-key distinguishers for 5-round AES built from the *exchanged boomerang*
(exchange / yoyo mixing on an inverse diagonal of a ciphertext pair so that
←q = r = 1 and pb collapses to →p · ←p). Two constructions:

1. **Massive exchanged boomerang** — friend pairs + four inverse-diagonal
   exchanges suppress the random probability that returned pairs are
   fully-active-or-inactive on every diagonal, while the AES trail probability
   stays 2^-22.
2. **Multiple exchanged boomerang** — cluster four trails that share the same
   Din (one active diagonal) and D′in (one inactive diagonal), raising the
   union boomerang probability above the random one-diagonal-inactive rate.

## Key claims (as reported; not verified by this program)

| Distinguisher | Data / time | Success (theory) | Success (expt, n=1000) |
| --- | --- | --- | --- |
| Massive exchanged boom. | 2^31 ACC / 2^31 M | 70% | 71.6% |
| Multiple exchanged boom. | 2^27.1 ACC / 2^27.1 M | 79.6% | 78.45% |

Prior 5-round secret-key figures they cite (POINTER only under RQ-AES-003 R3):
multiple-of-8 [GRR17] 2^32 CP; exchange [BR19] 2^30 CP; yoyo [MRSA23]
2^29.95 ACPC @55% / 2^30.65 ACPC @81%.

### Massive trail (reported)

- Din: one active diagonal; Dout: one inverse diagonal after E0 (3 inactive
  bytes after first-round MC) with →p = 4 · 2^-24 = 2^-22; ←p = 1.
- Random fully-active-or-inactive-per-diagonal ≈ 2^-0.09 per pair; four
  exchanges → 2^-0.36; with 2^6 friend pairs → ≈ 2^-23.1 < 2^-22.
- Structure size 2^11.5; 2^22 pairs × 2^6 friends; λ_AES ≈ 1.46 vs λ_rand ≈ 0.46.

### Multiple trail cluster (reported)

| Trail | Dout activity | →p | ←p | pb |
| --- | --- | --- | --- | --- |
| 1 | 1 inv. diag. | 2^-22 | 2^-6 | 2^-28 |
| 2 | 2 inv. diag. | 2^-13.4 | 2^-14 | 2^-27.4 |
| 3 | 3 inv. diag. | 2^-6 | 2^-22 | 2^-28 |
| 4 | 4 inv. diag. | 1 | 2^-30 | 2^-30 |

Union pb = 2^-26.1 vs random 4 · 2^-32 = 2^-30. Structure ≈ 2^12.55;
λ_AES ≈ 1.066 vs λ_rand ≈ 0.066.

## Relevance to this program

Seeds GOAL-AES-003 / RQ-AES-003 ideation for *program-adjudicable*
distinguishers (measured FPR vs matched random-permutation control; REF-A/B/C
only). Under claim_tier_ceiling R3, this entry is a POINTER: it must not be
used to assert that a local result beats or falls short of the published
frontier. Related later POINTER: KN-LIT-1848 (Yan–Tan–Qi ePrint 2026/1039)
reports ACP 2^23.32-class 5-round figures and a 7-round distinguisher claim —
also unadjudicable here as a margin.

Local proposals that take friend-pair suppression and/or trail clustering as
ingredients: IDEA-20260910-321d6a, IDEA-20260910-c5d0e5, IDEA-20260910-4b25eb.

## Not verified here

No independent re-derivation of the truncated probabilities, no re-run of
their experiments, no adjudication of “best-known” language. Upgrade path:
an EXP under GOAL-AES-003 that instruments the multiple-exchanged ACCEPT rule
against a 10-round AES control and records measured FPR + cost under CM-3.

## Local copies

- `downloads/2025-248.pdf` (if present from bulk seed)
- ePrint PDF: https://eprint.iacr.org/2025/248.pdf
