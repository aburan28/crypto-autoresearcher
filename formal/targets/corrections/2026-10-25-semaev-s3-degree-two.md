# Semaev S₃ target: trace cancellation and first-fall correction

**Correction recorded:** 25 October 2026

**Frozen target:** [`TASK-20260916-43505c`, `FFD-SEMAEV-MEASUREMENT1-THM-WITNESS`](../semaev-s3-degree2-fall-witness.yaml) at source commit `9e0431cfcea350dac1f50f96419f0ac8d4a189f6`

**Reviewed theorem:** `CryptoResearch.Semaev.trace_witness_annihilates_degree_two_part`

**Evidence:** [three-joint independent review](https://github.com/aburan28/crypto-autoresearcher/blob/7ddca6b514409d789c239dcb81b62a14a3c8069d/docs/reports/2026-10-25-semaev-semantic-review/composition.md), batch `BATCH-1a3355`

The frozen target's `source_status: PROVED` is accurate only for its narrower trace-cancellation identity. Its notes and final claim sentence infer a **uniform nontrivial first fall at degree two** for every admissible `n`, `n′`, and basis `V` with nonzero target `x_R`. The reviewed Lean theorem proves that a conditional trace expression vanishes; it has no S₃ equation-family, Boolean row-space or lower-row-space nonmembership conclusion. Cancellation does not imply a *new* class in `V₂∩R_{≤1}` outside `V₁`. This record withdraws that uniform first-fall inference while preserving the field identity.

The independent finite control uses `F₂[t]/(t⁴+t+1)`, `n=n′=4`, `x_R=1`, `a₆=1`, and encoded basis `[9,3,2,12]`. For degrees one, two and three, the reviewed row-space dimensions are `1, 11, 53`, and the low-degree intersections are `0, 1, 12`. The new-fall counts are therefore `0, 0, 1`: **degree two has no new class**, while degree three has one explicit witnessed class. The premise `x_R≠0` holds. This refutes the frozen universal consequence in the stated finite Boolean model; it does not establish a general first-fall distribution or ECDLP cost.

The historical multiplier used set union where Boolean multiplication over `F₂` needs parity cancellation: masks `1`, `17`, and `129` occur twice and must vanish. The archived aggregate `70/10` degree-two/degree-three counts remain reproducible for that original code. A later source-bound replay with corrected parity gives `68/12` on the same 80 Semaev draws, with seven degree-three draws having nonzero `x_R`. The three-joint review independently checked the stated finite sample and source/parity joint; it did **not** authenticate an earlier per-draw matrix that was never archived or independently re-run all 80 draws in this round.

The abstract Lean trace theorem's elaborated type and standard axiom set were checked in the independent review. The concrete degree-three witness theorem and finite equation theorem have earlier pinned-build receipts and source-level review. A fresh elaborated type and axiom query for the concrete theorem timed out during this review; that extra check remains open. A generic positive first-fall theorem would require an explicit equation-to-row-space map and proof that the residual lies outside the lower row space under stated hypotheses.

The original target, producer note and raw aggregate are preserved at their named revisions. This correction supersedes only the target's uniform degree-two first-fall interpretation. The [dated producer correction](https://github.com/aburan28/crypto-autoresearcher/pull/2504) already withdrew the same inference in the research note. Any graph or dashboard must distinguish the archived `70/10` observation from corrected Boolean `68/12` values, cite their different computation methods, and avoid presenting this finite review as a performance result.
