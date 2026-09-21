# Red Team Report — BATCH-b3f591

**Task:** TASK-20260806-a6ebe1 (Independent Red Team)
**Batch:** BATCH-b3f591
**Goal:** GOAL-ECDLP-001
**Policy:** review-adversarial (xhigh reasoning, independent session)
**Date:** 2026-08-06

---

## Summary

Four producer artifacts reviewed. Each carries at least one interpretation attack
or cheapest-falsification route. No artifact is fatally flawed, but none is
immune to misreading under the stated cost model, control structure, or proof
status.

---

## Objection 1 — Producer A: O_D ≡ O_x equivalence is cost-model-relative

**Artifact:** `halving_query_equivalence.md` (TASK-20260806-bf2364)

**Claim under attack:** "O_D and O_x are algebraically equivalent over any
odd-order prime subgroup."

**Objection.** The equivalence is stated as an algebraic identity between oracle
response functions, but its cryptographic consequence — "any sub-rho or no-sub-rho
result for one oracle applies identically to the other" — holds only under a
specific cost model: the GGM where scalar multiplication by any constant is free.

The halving direction requires computing H = [(q+1)/2]Q, which is a scalar
multiplication by (q+1)/2. In the GGM this is O(1) (free). In any cost model
where scalar multiplication is charged — e.g., a model counting group operations,
or a model where the adversary's computational budget is bounded — the halving
query costs O(log q) group operations. The forward direction (O_x → O_D via
rational function evaluation) costs O(1) field operations.

**Cheapest falsification route.** Construct a cost model M where:
- O_x queries cost c_x field operations (c_x = O(1)).
- O_D queries cost c_D = O(log q) group operations (for the halving scalar mult).
- Sub-rho is defined relative to M's cost unit.

Then show that the sub-rho power of O_x under M diverges from the sub-rho power
of O_D under M when c_D >> c_x. This is a one-line argument: the equivalence is
information-theoretic, not complexity-theoretic. The producer's §3.3 consequence
("any sub-rho result for one applies identically to the other") is false under M.

**Interpretation attack.** The equivalence is correctly stated as an algebraic
identity, but its §5 non-claims do not adequately scope the cost-model dependence.
A reader could conclude that O_D and O_x are interchangeable for all cryptographic
purposes, when they are interchangeable only for information-content purposes
under a GGM cost model. The record should explicitly state: "This equivalence is
cost-model-relative. Under any cost model where scalar multiplication is charged,
O_D and O_x have different computational costs, and their sub-rho power may
diverge."

---

## Objection 2 — Producer C: o(1) branch disposition may over-narrow the duality

**Artifact:** `hpseudo_o1_branch_disposition.md` (TASK-20260806-ad94be)

**Claim under attack:** "Reading 2 (notation artifact) is the more defensible
preliminary disposition."

**Objection.** The disposition's rationale rests on the bound β_1 ≥ B - B^2/N
being "continuous in B" and only giving β_1 ≥ Ω(sqrt(N)) when B ≥ sqrt(N). But
this is exactly the operationally relevant regime: for B < sqrt(N), the factor
base is too small to support a sub-rho chain complex (the complex would have
β_1 ≥ B ≥ sqrt(N) trivially). The duality's claim is not that it holds for all B,
but that it holds in the regime where sub-rho is possible.

The disposition's §"Deciding Evidence" observation 2 — "The proof uses
rank(∂_2) ≤ r_2(R), which is an upper bound on the rank" — is correct, but the
duality's forward direction (sub-rho → yield above heuristic) only requires an
upper bound on rank, not a lower bound. The backward direction (yield above
heuristic → sub-rho) would require a lower bound, and that direction is indeed
open. The disposition conflates the two directions.

**Alternate reading.** Reading 1 (genuine structural alternative) is defensible
in the regime B ≥ N^{1/2+ε}, where the bound β_1 ≥ B - B^2/N gives β_1 ≥
N^{1/2+ε} - N^{1+2ε}/N = N^{1/2+ε} - N^{2ε} >> sqrt(N) for small ε. In this
regime, the o(1) yield case is a genuine structural branch: the complex is
non-sub-rho, and the duality partitions the space cleanly. The disposition's
recommendation to treat the o(1) leaf as a "proof-technique artifact" is correct
only if the duality is claimed to hold universally for all B; if the duality is
claimed to hold in the operationally relevant regime B ≥ sqrt(N), then Reading 1
is defensible.

**Cheapest falsification route.** Tighten the bound β_1 ≥ B - B^2/N to a
lower bound on β_1 (not just an upper bound on rank) in the regime B ≥ sqrt(N).
If the lower bound gives β_1 ≥ Ω(sqrt(N)) when yield is o(1), then Reading 1 is
correct and the o(1) leaf is a genuine structural branch. If no such lower bound
exists, then Reading 2 is correct and the o(1) leaf is an artifact. This is a
one-lemma proof obligation, not a full re-formalization.

---

## Objection 3 — Producer D: x-oracle experiment's MITM control is imperfect

**Artifact:** `experiment_design.md` (TASK-20260806-a01d5a)

**Claim under attack:** "Arms B and C are run-matched: same code path, same
branching, same number of queries, same hash-table lookups. The only difference
is the response value."

**Objection.** The MITM structure's yield improvement depends on the hash-table
hit rate. In arm B (x-oracle), the hash table H maps x(P_3 + P_4) → list of
right-half tuples. The hit rate depends on the distribution of x-coordinates of
sums P_3 + P_4, which is determined by the curve geometry.

In arm C (random predictor), the hash table H maps PRNG(key‖P) → list of
right-half tuples. The "x-coordinates" in H are deterministic pseudo-random field
elements, not actual x-coordinates of curve points. The hit rate in arm C depends
on the probability that a random field element matches a random field element,
which is 1/p per query.

The hit rates in arms B and C are therefore different by construction: arm B's
hit rate is determined by the curve's x-coordinate distribution, while arm C's
hit rate is 1/p. The Δ = Y_B - Y_C metric conflates the oracle's information
content with the hit-rate difference.

**Interpretation attack.** If Y_B > Y_C, the producer concludes "x-oracle
improves yield." But the alternative explanation "MITM structure with a
curve-distributed hash table improves yield more than MITM with a uniform-random
hash table" is not ruled out. The design's "Strategy-artifact" outcome
classification (Y_B ≈ Y_C but both > Y_A) addresses the case where MITM itself
improves yield, but it does not address the case where MITM + curve-distributed
hash table improves yield more than MITM + random hash table.

**Cheapest falsification route.** Add a fourth arm D: MITM structure with a
hash table populated by x-coordinates of random curve points (not the actual
right-half tuples). This arm isolates the "curve-distributed hash table" effect
from the "oracle-guided enumeration" effect. If Y_D ≈ Y_C, then the hash-table
distribution is not the cause, and the oracle's information content is. If Y_D >
Y_C, then the hash-table distribution is a confound. This is one additional arm,
not a redesign.

**Misreading risk under corridor corrections.** The corridor corrections
(DEC-20260806-26c0e8, DEC-20260806-bba4bf) establish that the rescue window is
empty at the tested parameters. The experiment's §9 corridor reconciliation
accepts this and does not test the rescue window. However, a reader could misread
a positive Δ (Y_B > Y_C) as evidence that the x-oracle "rescues" Semaev index
calculus from the corridor emptiness, when in fact the experiment only tests
whether the x-oracle improves yield at toy scale — not whether it enables sub-rho
ECDLP or circumvents the corridor. The design's §0 scope statement is clear, but
the §8 outcome classification's "Oracle-exploitable" label could be misread as
"oracle enables sub-rho" rather than "oracle improves yield at toy scale."

---

## Objection 4 — Producer D: Cheapest route around the proposed design

**Artifact:** `experiment_design.md` (TASK-20260806-a01d5a)

**Claim under attack:** The three-arm design (no-oracle, x-oracle, random
predictor) is the cheapest way to discriminate the x-oracle's effect.

**Objection.** The design requires 240 arm-runs (80 config-run combinations × 3
arms). The cheapest route to the same discrimination is a two-arm design:
- Arm A: no-oracle, exhaustive enumeration.
- Arm B: x-oracle, MITM enumeration.

If Y_B > Y_A with statistical significance, the x-oracle improves yield. The
random predictor arm C is a control for the MITM structure's contribution, but
the MITM structure's contribution can be isolated more cheaply by comparing arm B
to a variant of arm B where the oracle is replaced by a constant function (e.g.,
always return 0). This "constant-oracle" arm has the same MITM structure and hash
table as arm B, but the oracle provides no information. If Y_B > Y_constant, the
oracle's information content is the cause.

The constant-oracle arm is cheaper than the random predictor arm because it does
not require a PRNG, collision-free checks, or per-query keying. It is a simpler
null object.

**Cheapest route.** Replace arm C (random predictor) with arm C' (constant
oracle). This reduces the implementation complexity and the control-check burden
(no PRNG collision checks). The discrimination is the same: Δ' = Y_B - Y_C'
measures the oracle's information content above a trivial null.

---

## Objection 5 — Producer B: KN promotion candidates' confidence levels

**Artifact:** `knowledge_candidates.md` (TASK-20260806-a4b58a)

**Claims under attack:**
1. KN-FIND-194294: confidence "proved", evidence_level "theorem"
2. KN-FIND-ac28ed: confidence "proved", evidence_level "theorem"
3. KN-FIND-ff4a46: confidence "proved", evidence_level "theorem"

**Objection 1 (overclaim).** KN-FIND-194294's confidence "proved" and
evidence_level "theorem" are too strong for a hand derivation. The equivalence
O_D ≡ O_x is derived via algebraic manipulation and verified on one toy curve
(p = 1009, q = 17). This is a derivation, not a machine-checked proof. The
proof_status "derivation" is correct, but the confidence "proved" implies a
higher standard of verification than a hand derivation with one numeric check.

**Underclaim risk.** If the equivalence is actually a theorem (which it likely
is — the algebra is straightforward), then the confidence "proved" is appropriate,
but the evidence_level "theorem" requires a formal proof or a peer-reviewed
publication. The candidate is an internal finding, not a published theorem. The
evidence_level should be "internal_derivation" or "hand_proof", not "theorem".

**Objection 2 (overclaim).** KN-FIND-ac28ed's claim that K*(standard) = 2000
(not 2001) and the m=4 cell = 125 (not 126) due to IEEE-float ceil artifacts is
plausible but not independently verified in this record. The candidate states the
corrections but does not show the exact-arithmetic computation. A reader must
trust the producer's claim that "exact rational arithmetic" gives 2000 and 125.

**Cheapest falsification route.** Compute K*(standard) and the m=4 cell under
exact rational arithmetic (e.g., using Python's `fractions.Fraction` or a CAS)
and verify the values 2000 and 125. This is a one-line computation. If the
values match, the candidate is correct. If they do not, the candidate is wrong
and the corrections are invalid.

**Objection 3 (underclaim).** KN-FIND-ff4a46's repair changes the orientation
from "H-PSEUDO is the exact condition for sub-rho" to "sub-rho requires failure
of H-PSEUDO baseline." This is a meaningful semantic shift: the original claims
H-PSEUDO is necessary AND sufficient; the repair claims it is only necessary.

If the biconditional (sub-rho ↔ H-PSEUDO fails) actually holds in the
operationally relevant regime (as suggested by Objection 2 above), then the
repair underclaims the result. The repair's "non-claims" section states "No
claim in either direction about the sub-rho question," but if the biconditional
holds, then H-PSEUDO's failure is both necessary and sufficient for sub-rho, and
the repair should state this.

**Cheapest falsification route.** Determine whether the backward direction
(H-PSEUDO fails → sub-rho) holds in the regime B ≥ sqrt(N). If it does, the
repair underclaims and the original's "exact condition" framing is correct (with
a regime restriction). If it does not, the repair is correct and the original
overclaims. This is the same proof obligation as Objection 2's cheapest
falsification route.

---

## Synthesis

| Artifact | Strongest attack | Cheapest falsification |
|---|---|---|
| Producer A (equivalence) | Cost-model relativity not scoped | Construct cost model M where c_D >> c_x |
| Producer C (o(1) branch) | Conflates forward/backward directions | Tighten β_1 lower bound in B ≥ sqrt(N) regime |
| Producer D (experiment) | MITM control imperfect; hit-rate confound | Add arm D (curve-distributed random hash table) |
| Producer D (design) | Three-arm design not cheapest | Replace arm C with constant-oracle arm C' |
| Producer B (KN candidates) | Confidence levels mismatch evidence | Verify K* corrections with exact arithmetic |

No artifact is fatally flawed. All are defensible with the stated scope and
non-claims. The objections above are interpretation attacks and cheapest-falsification
routes, not refutations. The Coordinator should weigh these against the producer's
stated scope and decide whether the artifacts are ready for promotion or require
revision.

---

## Non-claims

- No hypothesis status transition is proposed.
- No DEC or LEMMA id is minted.
- No fabricated bounds, citations, or run ids.
- This report is adversarial by design; the objections are stress-tests, not
  necessarily correct interpretations.

---

*Red team report by TASK-20260806-a6ebe1, BATCH-b3f591, GOAL-ECDLP-001.*
*Policy: review-adversarial (xhigh reasoning, independent session).*
*Artifacts reviewed: TASK-20260806-bf2364, TASK-20260806-a4b58a, TASK-20260806-ad94be, TASK-20260806-a01d5a.*
