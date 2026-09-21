# Red Team Report — BATCH-c3a501 (KN-FIND Promotions + Smoke Test)

**Task:** TASK-20260807-9754a2 (Independent Red Team)
**Batch:** BATCH-c3a501
**Goal:** GOAL-ECDLP-001
**Policy:** review-adversarial (xhigh reasoning, independent session)
**Date:** 2026-08-07
**Model:** fireworks-ai/accounts/fireworks/models/qwen3p7-plus

---

## Summary

Three KN-FIND promotions and one smoke test reviewed. Each carries at least one
interpretation attack or cheapest-falsification route. The KN-FIND promotions
overclaim confidence levels relative to their evidence base. The smoke test's
primary metric is misaligned with its stated objective, and its "x-oracle
advantage" is a misreading of the random model's prediction.

---

## Objection 1 — KN-FIND-194294: "proved" confidence exceeds evidence base

**Artifact:** `knowledge/findings/KN-FIND-194294.md`

**Claim under attack:** confidence "proved", evidence_level "theorem"

**Objection.** The halving-query equivalence O_D ≡ O_x is derived via algebraic
manipulation and verified on one toy curve (p = 1009, q = 17). This is a hand
derivation with a single numeric check, not a machine-checked proof or a
peer-reviewed publication. The proof_status "derivation" is correct, but the
confidence "proved" and evidence_level "theorem" imply a higher standard of
verification than what is present.

The previous red team (TASK-20260806-a6ebe1) identified the cost-model relativity
objection: the equivalence holds only under a GGM cost model where scalar
multiplication is free. Under any cost model where scalar multiplication is
charged, O_D and O_x have different computational costs, and their sub-rho power
may diverge. The KN-FIND's §"Non-claims" does not adequately scope this
cost-model dependence.

**Overclaim.** The KN-FIND states "O_D inherits the classification of O_x: it is
NON-SIMULABLE (Tier 3) in the GGM sense." This is correct under GGM, but the
classification is cost-model-relative. A reader could conclude that O_D and O_x
are interchangeable for all cryptographic purposes, when they are interchangeable
only for information-content purposes under a GGM cost model.

**Cheapest falsification route.** Construct a cost model M where:
- O_x queries cost c_x = O(1) field operations.
- O_D queries cost c_D = O(log q) group operations (for the halving scalar mult).
- Sub-rho is defined relative to M's cost unit.

Then show that the sub-rho power of O_x under M diverges from the sub-rho power
of O_D under M when c_D >> c_x. This is a one-line argument: the equivalence is
information-theoretic, not complexity-theoretic. The KN-FIND's consequence
("any sub-rho result for one applies identically to the other") is false under M.

**Required repair.** Add to the Non-claims section: "This equivalence is
cost-model-relative. Under any cost model where scalar multiplication is charged,
O_D and O_x have different computational costs, and their sub-rho power may
diverge. The equivalence holds only under a GGM cost model where scalar
multiplication by any constant is free."

---

## Objection 2 — KN-FIND-ac28ed: Exact-arithmetic corrections not independently verified

**Artifact:** `knowledge/findings/KN-FIND-ac28ed.md`

**Claim under attack:** K*(standard) = 2000 (not 2001), m=4 cell = 125 (not 126)

**Objection.** The KN-FIND states these corrections are due to "IEEE-float ceil
artifacts" and claims the values verify under "exact rational arithmetic." However,
the record does not show the exact-arithmetic computation. A reader must trust the
producer's claim that exact rational arithmetic gives 2000 and 125.

The previous red team (TASK-20260806-a6ebe1) noted this needs independent
verification. The confidence "proved" and evidence_level "theorem" are too strong
for a claim that has not been independently recomputed in this record.

**Overclaim risk.** If the exact-arithmetic computation is incorrect (e.g., the
producer made an error in the rational arithmetic), then the corrections are
invalid and the KN-FIND is wrong. The "proved" confidence implies a higher
standard than a single producer's computation.

**Cheapest falsification route.** Compute K*(standard) and the m=4 cell under
exact rational arithmetic using Python's `fractions.Fraction` or a CAS:

```python
from fractions import Fraction
# K*(standard) = ceil(200 / 0.1) under exact arithmetic
# 0.1 in exact arithmetic is 1/10
# 200 / (1/10) = 2000 exactly
# ceil(2000) = 2000
# Under IEEE float: 200 / 0.1 = 2000.0000000000005, ceil = 2001
```

This is a one-line computation. If the values match (2000 and 125), the KN-FIND
is correct. If they do not, the KN-FIND is wrong and the corrections are invalid.

**Required repair.** Include the exact-arithmetic computation in the KN-FIND, or
downgrade confidence to "derived" and evidence_level to "internal_derivation"
until independent verification is performed.

---

## Objection 3 — KN-FIND-ff4a46: Wording repair may underclaim if biconditional holds

**Artifact:** `knowledge/findings/KN-FIND-ff4a46.md`

**Claim under attack:** Repaired corollary states "sub-rho requires failure of
H-PSEUDO baseline" (necessary condition only), not "H-PSEUDO failure is necessary
and sufficient for sub-rho."

**Objection.** The repair changes the orientation from "H-PSEUDO is the exact
condition for sub-rho" to "sub-rho requires failure of H-PSEUDO baseline." This
is a meaningful semantic shift: the original claims H-PSEUDO is necessary AND
sufficient; the repair claims it is only necessary.

The previous red team (TASK-20260806-a6ebe1) noted that if the biconditional
(sub-rho ↔ H-PSEUDO fails) actually holds in the operationally relevant regime
B ≥ sqrt(N), then the repair underclaims the result. The repair's "non-claims"
section states "No claim in either direction about the sub-rho question," but if
the biconditional holds, then H-PSEUDO's failure is both necessary and sufficient
for sub-rho, and the repair should state this.

**Underclaim risk.** If the backward direction (H-PSEUDO fails → sub-rho) holds
in the regime B ≥ sqrt(N), then the repair's "necessary condition only" framing
is too weak. A reader could conclude that H-PSEUDO failure is not sufficient for
sub-rho, when in fact it is (in the operationally relevant regime).

**Cheapest falsification route.** Determine whether the backward direction
(H-PSEUDO fails → sub-rho) holds in the regime B ≥ sqrt(N). If it does, the
repair underclaims and the original's "exact condition" framing is correct (with
a regime restriction). If it does not, the repair is correct and the original
overclaims. This is the same proof obligation as the o(1) branch disposition
(TASK-20260806-ad94be).

**Required repair.** Either:
1. Add a regime restriction to the repaired corollary: "In the regime B ≥ N^{1/2+ε},
   H-PSEUDO failure is necessary and sufficient for sub-rho."
2. Or, if the backward direction does not hold, state explicitly: "The backward
   direction (H-PSEUDO fails → sub-rho) is open; this record claims only the
   forward direction (sub-rho → H-PSEUDO fails)."

---

## Objection 4 — Smoke test: "Yield advantage" is a misreading of the random model

**Artifact:** `experiments/EXP-SEMAEV-f48dd1/runs/RUN-SEMAEV-f48dd1-smoke/raw-result.json`

**Claim under attack:** Manifest note: "The x-oracle demonstrates a clear yield
advantage over the random predictor."

**Objection.** The smoke test's primary metric is "yield = relations_found /
tuples_enumerated." For Arm B (x-oracle), tuples_enumerated = candidates_verified
(52), not all possible tuples (1728). For Arm A (no-oracle), tuples_enumerated =
all tuples (1728). These are different denominators, so the yields are not
comparable.

Arm B's yield of 0.5 (26/52) is the **precision** of the x-oracle MITM: the
fraction of candidates that are true relations. Arm A's yield of 0.015 (26/1728)
is the **absolute yield**: the fraction of all tuples that are relations.

The x-oracle did not find more relations than the no-oracle baseline; both found
exactly 26 relations. The x-oracle's benefit is computational efficiency (fewer
verifications needed), not increased relation yield.

**Misreading.** The manifest's note "The x-oracle demonstrates a clear yield
advantage" conflates precision with absolute yield. A reader could conclude that
the x-oracle finds more relations, when in fact it finds the same relations with
fewer verifications.

**Random model prediction.** Under the random model, x-coordinates are uniformly
distributed. The x-oracle MITM finds candidates where x(P1) = x(P2+P3), which
means P1 = ±(P2+P3). If P1 = -(P2+P3), then P1+P2+P3 = O (relation). If
P1 = P2+P3, then P1+P2+P3 = 2P1 ≠ O (false positive). Under the random model,
these two cases are equally likely, so the expected precision is 1/2.

The observed precision is 26/52 = 0.5, which matches the random model prediction
exactly. The x-oracle's precision is consistent with the random model, not
evidence of structural advantage.

**Cheapest falsification route.** Compute the expected precision of the x-oracle
MITM under the random model:
- For each candidate (x(P1) = x(P2+P3)), the probability that P1 = -(P2+P3) is
  1/2 (under the random model).
- Expected precision = 1/2 = 0.5.
- Observed precision = 0.5.
- Conclusion: the x-oracle's precision is consistent with the random model.

To show a structural advantage, the observed precision must exceed the random
model prediction. At this scale (p=101, B=6), the observed precision matches the
random model exactly, so there is no evidence of structural advantage.

**Required repair.** The manifest's note should state: "The x-oracle's precision
(0.5) matches the random model prediction (0.5), consistent with no structural
advantage at this scale. The x-oracle's benefit is computational efficiency
(fewer verifications), not increased relation yield."

---

## Objection 5 — Smoke test: Control checks are vacuous at this scale

**Artifact:** `experiments/EXP-SEMAEV-f48dd1/runs/RUN-SEMAEV-f48dd1-smoke/raw-result.json`

**Claim under attack:** Control checks pass (query_count_match, prng_collision_free,
baseline_consistency).

**Objection.** The three control checks are vacuous at this scale:

1. **Query count match (B=C=12):** Guaranteed by construction, since both arms
   iterate over the same factor base (12 points). This is not a meaningful control.

2. **PRNG collision free:** Arm C generates 12 outputs from SHA-256 mod 101. The
   probability of at least one collision is approximately 12^2 / (2*101) ≈ 0.71,
   so the probability of no collision is ≈ 0.29. The observed "no collision" is
   plausible but not guaranteed. However, this control does not test whether the
   PRNG is a good null object; it only tests whether the PRNG outputs are distinct.
   A bad PRNG (e.g., one that always returns 0) would fail this check, but a
   mediocre PRNG (e.g., one with slight biases) would pass.

3. **Baseline consistency:** Arm A's yield Y_A = 0.015 is within factor 4 of
   expected 1/N = 0.0098. This is a trivially weak check at this scale. The
   expected number of relations is |F|^m / N = 12^3 / 102 ≈ 17.3, and the
   observed 26 is within a factor of 1.5. This is consistent with the random
   model, but the "factor 4" margin is so wide that almost any result would pass.

**Misreading risk.** A reader could conclude that the smoke test's controls
validate the implementation, when in fact the controls are too weak to detect
implementation errors at this scale.

**Cheapest falsification route.** Strengthen the control checks:
1. Replace "query count match" with a check that the hash-table hit distribution
   in Arm C matches the expected uniform distribution (e.g., chi-squared test).
2. Replace "PRNG collision free" with a check that the PRNG outputs pass a
   statistical randomness test (e.g., frequency test, runs test).
3. Replace "baseline consistency within factor 4" with a check that the observed
   number of relations is within 2 standard deviations of the expected value under
   the binomial distribution (|F|^m trials, probability 1/N).

**Required repair.** The smoke test's control checks should be strengthened to
detect implementation errors at this scale, or the smoke test should be run at a
larger scale where the controls are non-vacuous.

---

## Objection 6 — Smoke test: Factor base selection may introduce structure

**Artifact:** `experiments/EXP-SEMAEV-f48dd1/implementation/smoke_test.py`

**Claim under attack:** Factor base selection: "first 6 on-curve x-coordinates
in [0, p) in increasing order."

**Objection.** The factor base is the first 6 on-curve x-coordinates: [0, 2, 4,
5, 9, 10]. This is a deterministic selection that may introduce structure into
the factor base. For example, these x-coordinates are all small (≤ 10), which
means the factor base points are clustered in a small region of the curve.

If the x-oracle's precision depends on the factor base's structure (e.g., the
x-coordinates of sums P2+P3 are more likely to match x(P1) when the factor base
is clustered), then the observed precision (0.5) may be specific to this factor
base, not a general property of the x-oracle MITM.

**Cheapest falsification route.** Run the smoke test with a different factor base
selection rule:
1. Random selection: choose 6 on-curve x-coordinates uniformly at random.
2. Spread selection: choose 6 on-curve x-coordinates that are maximally spread
   out (e.g., every 17th x-coordinate).

If the x-oracle's precision changes significantly under different factor base
selection rules, then the precision is factor-base-structure-dependent, not
oracle-inherent.

**Required repair.** The smoke test should report the factor base selection rule
and discuss whether the observed precision is specific to this factor base or
generalizes to other selection rules.

---

## Synthesis

| Artifact | Strongest attack | Cheapest falsification |
|---|---|---|
| KN-FIND-194294 | "proved" confidence exceeds evidence base; cost-model relativity not scoped | Construct cost model M where c_D >> c_x |
| KN-FIND-ac28ed | Exact-arithmetic corrections not independently verified | Compute K* under exact rational arithmetic (one-line) |
| KN-FIND-ff4a46 | Wording repair may underclaim if biconditional holds in B ≥ sqrt(N) regime | Determine if backward direction holds in B ≥ sqrt(N) |
| Smoke test (yield) | "Yield advantage" is a misreading; precision matches random model | Compute expected precision under random model (0.5) |
| Smoke test (controls) | Control checks are vacuous at this scale | Strengthen controls with statistical tests |
| Smoke test (factor base) | Factor base selection may introduce structure | Run with different factor base selection rules |

No artifact is fatally flawed. All are defensible with the stated scope and
non-claims. The objections above are interpretation attacks and cheapest-falsification
routes, not refutations. The Coordinator should weigh these against the producer's
stated scope and decide whether the artifacts are ready for promotion or require
revision.

---

## Narrowest supported statement

**KN-FIND-194294:** The halving-query oracle O_D is algebraically equivalent to
the x-coordinate oracle O_x under a GGM cost model where scalar multiplication
is free. Under any cost model where scalar multiplication is charged, O_D and O_x
have different computational costs, and their sub-rho power may diverge. The
equivalence is information-theoretic, not complexity-theoretic.

**KN-FIND-ac28ed:** The BKK K* table contains two off-by-one errors (K*(standard)
= 2001 → 2000, m=4 cell = 126 → 125) due to IEEE-float ceil artifacts, pending
independent verification under exact rational arithmetic.

**KN-FIND-ff4a46:** The repaired wording for KN-FIND-9d2f56 states that sub-rho
requires failure of the H-PSEUDO baseline (necessary condition only). Whether the
backward direction (H-PSEUDO fails → sub-rho) holds in the operationally relevant
regime B ≥ sqrt(N) is open.

**Smoke test:** The x-oracle MITM achieves precision 0.5 at toy scale (p=101,
B=6, m=3), matching the random model prediction exactly. The x-oracle's benefit
is computational efficiency (fewer verifications), not increased relation yield
or structural advantage. The control checks are too weak to detect implementation
errors at this scale.

---

## Non-claims

- No hypothesis status transition is proposed.
- No DEC or LEMMA id is minted.
- No fabricated bounds, citations, or run ids.
- This report is adversarial by design; the objections are stress-tests, not
  necessarily correct interpretations.

---

*Red team report by TASK-20260807-9754a2, BATCH-c3a501, GOAL-ECDLP-001.*
*Policy: review-adversarial (xhigh reasoning, independent session).*
*Model: fireworks-ai/accounts/fireworks/models/qwen3p7-plus.*
*Artifacts reviewed: KN-FIND-194294, KN-FIND-ac28ed, KN-FIND-ff4a46, EXP-SEMAEV-f48dd1 smoke test.*
