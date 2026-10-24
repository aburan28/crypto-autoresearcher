---
id: KN-FIND-921fbf
type: internal_finding
title: Withdrawal of the growing-with-m BKK speedup law (KN-FIND-2a8b7e); per-decomposition (m+1)/2 retained
tags: [bkk, semaev, sparse-relation, correction, withdrawal, confound, prime-field, index-calculus]
confidence: established
evidence_level: toy_measurement
source_refs: [EV-FALSIFY-67150b, KN-FIND-2a8b7e, KN-FIND-c7d31e, KN-FIND-f8c290]
internal_refs: [EV-FALSIFY-67150b, EXP-FALSIFY-d770c1]
proof_status: empirical_only
proof_refs: []
added: '2026-10-24'
superseded_by: null
---

## Finding

This entry supersedes the growing-with-m speedup claim of KN-FIND-2a8b7e
("3 to 5x at crypto scale", geometric growth 2^{m-1} x gamma_m). That claim is
withdrawn as a growing law. Its gamma column and its m = 6, 7, 8 extrapolations
must not be cited.

## Basis

EV-FALSIFY-67150b (2026-08-08, direction: contradicts) shows at p = 1009,
B in {10, 12, 18, 24, 54}, m in {2..5}:

- The decay attributed to m is produced by the simultaneous reduction of B. At
  fixed B the per-step ratio does not decay (B = 12, 18, 24 give ratios that
  rise toward and past 1.0).
- The fitted law contradicts the proved linear law of KN-FIND-c7d31e
  (speedup (m+1)/2). The two diverge with m.

## What survives

Per-decomposition BKK sparse-check retention equals (m+1)/2^m. This is proved
(KN-FIND-c7d31e) and reproduced at every B tested. No claim is made here about
the true speedup at cryptographic parameters, in either direction.

## Recording

Correction record: CORR-20261024-851c82. Scope: toy scale, m <= 5, p = 1009.
