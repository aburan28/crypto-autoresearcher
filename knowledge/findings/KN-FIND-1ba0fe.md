---
id: KN-FIND-1ba0fe
type: internal_finding
title: "ECDLP-IDEA-436's D1 coordinate-valuation profile collapses exactly to the +/-fibre indicator on a toy instance, confirming Proposition E and its canonical-lift mechanism"
tags: [lifting, local-torsion, p-adic, valuation, ecdlp, prime-field, toy-verified, ecdlp-idea-436, rc-1, negation-map]
confidence: preliminary
internal_refs: [H-ECDLP-a40416, EXP-ECDLP-c373eb, RUN-ECDLP-c373eb-1, EV-ECDLP-f5c698, DEC-20260901-34e038]
knowledge_refs: [KN-TECH-73630e, KN-OPEN-3417fc, KN-TECH-005, KN-TECH-006]
proof_status: empirical_only
proof_refs: [experiments/EXP-ECDLP-c373eb/runs/RUN-ECDLP-c373eb-1/raw-result.json]
added: 2026-09-01
superseded_by: null
---

## Finding

`ECDLP-IDEA-436`'s coordinate/valuation functional D1 (disjunct D1 of its
disjunctive hypothesis H), predicted by `Proposition E`
(`ideas/artifacts/ECDLP-IDEA-436/ggm_simulability_gate_erratum_20260831.md`
section C.2) to collapse to the `<S>/{+/-1}` fibre indicator with zero
information and zero computational leverage beyond what Pollard rho's
negation map already exploits, is **confirmed by a toy-scale measurement**
(`RC-1`, `RUN-ECDLP-c373eb-1`), exhaustively on the tested instance:

- **Instance:** `E/F_p`, `p = 1009`, `y^2 = x^3 + x + 1` (ordinary, good
  reduction, `#E(F_p) = 1034 = 2 * 11 * 47`), `S = (286, 680)` of prime
  order `n = 47`, canonical order-`n` prime-to-`p` torsion lift `S-hat` at
  `p`-adic precision `r = 8`.
- **Order-`n` certificate:** `n * S-hat` equals the exact projective
  identity mod `p^8` (the full precision cap) — independently re-verified
  by the Coordinator via a separate, from-scratch Jacobian-coordinate
  implementation.
- **Primary tabulation (exhaustive, all 1035 pairs `1 <= j < k < 47`):**
  `D1(j,k) = v_p(x([k]S-hat) - x([j]S-hat))` truncated at `r=8` takes
  **exactly** the two values `{0, >=8}` — `0` on all 1012 off-fibre pairs,
  `>=8` on all 23 on-fibre pairs (`k = n-j`) — with **zero exceptions**.
  Independently re-verified by the Coordinator for five pairs (both
  on- and off-fibre) via a second, independent implementation; all matched.
- **Discriminating null-lift control:** the identical tabulation on a
  different, non-order-`n` Hensel lift of `S` shows image `{0, 1}` —
  genuinely different from `{0, 8}` — ruling out the alternative explanation
  that the observed flatness is a `p`-adic-library precision artifact rather
  than a consequence of the canonical lift's order-`n` (group-isomorphism)
  property.
- **`RTF-1` rigidity probe:** the Vandermonde (rigid, three-pairwise-
  difference) functional matches D1's own two-valued pattern exactly on the
  tested triples, consistent with the rigidity reading. The non-rigid
  three-point functional's image was `{0}` on the six tested triples — this
  is **statistically underpowered**, not a confirming or refuting result,
  since a generic non-rigid functional's mod-`p` coincidence is expected
  only with probability roughly `1/p` per triple.

## What this establishes

For this tested instance, `ECDLP-IDEA-436` disjunct D1 offers **zero
information and no computational leverage** beyond the `<S>/{+/-1}` quotient
already available for free in `E(F_p)` via a single `x`-coordinate
comparison, and already exploited by Pollard rho's negation map
(`KN-TECH-006`). This is a **negative result for this specific candidate**,
consistent with — and a fresh, independently confirmed instance of — this
program's existing structured-hardness baseline (`KN-TECH-005`).

## What this does NOT establish

- **Not replicated.** This is a single toy instance (one curve, one `n`);
  it has not been repeated on a second curve or a different `n`. Confidence
  is recorded as `preliminary`, not `strong` or `replicated`.
- **Not a closure of `KN-OPEN-3417fc`.** That open problem quantifies over
  *any* computable non-group-theoretic coordinate or valuation invariant;
  this finding concerns exactly one named functional family (D1), the one
  `KN-OPEN-3417fc` itself names as its headline worked example, not the
  question in general.
- **Not a disposition of `ECDLP-IDEA-436` disjunct D2** (a single-point
  coordinate-digit statistic, a different mathematical object from D1's
  two-point difference), which remains open.
- **Not a retiering of `KN-FIND-002` or `KN-FIND-b7e091`.** Objections
  against their recorded tier/justification remain routed to their own,
  still-unopened `review-breakthrough` round.
- **No cryptographic-scale claim.** Toy tier only
  (`docs/claims-and-verification.md`); no transfer argument to
  cryptographic-scale curves is made.
- **No information-theoretic novelty.** This is fully consistent with, and
  in fact a direct consequence of, `KN-TECH-73630e`'s prior result that the
  canonical torsion lift is information-theoretically empty.

## Forward guidance

A second toy instance (different curve, different `n`) would move this
finding from `preliminary` toward `replicated`. The `RTF-1` non-rigid probe
needs either a larger sample or a deliberately constructed triple exhibiting
a mod-`p` coincidence to be genuinely informative. `RC-3` (a held-out oracle
class outside `KN-FIND-002`/`KN-FIND-b7e091`) and `RC-4` (a frozen
regression fixture against `experiments/EXP-GGM-001/simulability_test.py`)
remain queued and undischarged, per `DEC-20260831-a9716f`.

## Provenance

- `ledger/hypotheses/H-ECDLP-a40416.yaml` (internal — the tested hypothesis)
- `experiments/EXP-ECDLP-c373eb/specification.yaml`,
  `experiments/EXP-ECDLP-c373eb/runs/RUN-ECDLP-c373eb-1/` (internal — the
  frozen specification and the run's manifest, raw results, and script)
- `ledger/evidence/EV-ECDLP-f5c698.yaml` (internal — the composed evidence
  record, including the Coordinator's independent re-verification)
- `ledger/decisions/DEC-20260901-34e038.yaml` (internal — this finding's
  promoting decision)
- `ideas/artifacts/ECDLP-IDEA-436/ggm_simulability_gate_erratum_20260831.md`
  (internal — Proposition E, the mechanism this finding measures)
- `knowledge/techniques/KN-TECH-73630e.md` (internal — the isomorphism fact
  underlying the canonical lift)
- `knowledge/open-problems/KN-OPEN-3417fc.md` (internal — the broader open
  question this finding narrows one instance of, without closing)
