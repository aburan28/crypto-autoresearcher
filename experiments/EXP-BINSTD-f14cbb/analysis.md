# Analysis — EXP-BINSTD-f14cbb / H-BINSTD-41d8b2

Review plan: `experiments/EXP-BINSTD-f14cbb/review/review-plan.yaml`
(`REVIEW-BINSTD-f14cbb-20261001`). Producer: `TASK-20261001-109e55`
(package tip at review start ~`840401d7d`; implementation commit
`079c3612d`). Evidence: `EV-BINSTD-2a4191`. Decision:
`DEC-20261001-d92cdc`.

Class: **structural_certificate / arithmetic measurement** (torus-row
certificate for KN-OPEN-095df5: cyclotomic divisor census, Phi_130(2)
valuation, Lemma L toys at n=17 and n=131). No ECDLP attack, no break,
no factor-base construction, no rho competitiveness, no
exponent-moving claim. Couveignes–Lercier primary text remains unread
(scope obligation).

---

## Observation

**Validity.** Three runs, all `completed_valid`; `invalid: []`,
`failed: []`:

| Run | Stage | Status | Primary metrics |
| --- | --- | --- | --- |
| `RUN-BINSTD-59f5ad` | 0-cyclotomic | `completed_valid` | k-set {130,17030}; phi 48/6240; v_131=1; p17 {8,136,2312} |
| `RUN-BINSTD-aeaa1b` | 1-lemma-L-n17 | `completed_valid` | dim=8; stable; equals ker m_t; random-b 0/10; basis-relabel OK |
| `RUN-BINSTD-9fcb73` | 2-lemma-L-n131 | `completed_valid` | dim=130 equals T_0; analytic unknowns/slot 17030; ~28.4s wall |

Manifest metrics agree with `raw-result.json` and stage YAML summaries.
`n_runs=3 ≤ maximum_runs=8`. Stage 0 is seed-free; Stage 1/2 seed
`20261001` with Stage-1 replication seed `20261002` folded into
`aeaa1b` (disclosed producer deviation). All manifests use
`certificate.kind: none` with `verified: true` on the structural
verifier. No Bedrock. Producer and stage artifacts set no break/rho
claim. Required Stage 0/1/2 artifacts present; Stage 0
`preregistered-predictions.yaml` and `methodological-note.md` written
before Stage 1/2 claims. `implementation_commit`
`079c3612d34cab81a1fcf732cf3fc052019f0439` bound on the execution
report. Manifests record `dirty: true` at write under producer commit
`a8524f00b` (disclosed).

**Stage 0.** Measured k-set `{130, 17030}` matches frozen expectation;
phi values `{130: 48, 17030: 6240}`; Phi_130(2)=`409368176241571` with
cofactor `3124947910241`, `v_131=1`, product check and
`(2^65+1)/(8193×11)` cross-check ok; modulus-swap p=17 →
`{8, 136, 2312}`; no unexpected-k inspection items. Method note:
Moebius valuation of `(2^d−1)` via modular lifting for the census
(exact Phi_130 still uses integer Moebius product + cross-check) —
disclosed protocol deviation, not a mismatch.

**Stage 1.** n=17 toy: dim=8, Frobenius-stable, equals ker m_t(sigma);
both Phi_17 irreducible factors found; V equals ker only for the
matching factor; dim in subset-sum set `{0,1,8,9,16,17}`; random-b
stable_count=`0/10` (≤1 prior); order-15 nulls all unstable /
`hilbert_relation_holds=false` with explicit "do not claim Lemma L"
note; basis-relabel invariant under seed `20261002`; replication seed
`20261002` also reports dim=8, stable, equals ker, random-b 0,
basis-relabel OK. Field impl: `composite_field`.

**Stage 2.** n=131 via composite field: ambient_bits=17030; dim=130;
`equals_T0` / `equals_T0_ker_mt` / `equals_ker_Tr` true;
Frobenius-stable; torsor relation verified; `termination_reason=
completed` (~28.4s wall; peak RSS reported ~16 MiB). Analytic
unknowns/slot lower bound `17030` vs `131` one-hot bits
(`measured_vs_modeled: modeled/analytic`; comparison holds). No
infrastructure stop.

---

## Comparison

Blind re-derivation this review session (from hypothesis /
specification parameters; without reading producer implementation or
stage YAMLs for the quantities):

| Quantity | Predicted / frozen | Recomputed | Match |
| --- | --- | --- | --- |
| Phi_130(2) Moebius | 409368176241571 | 409368176241571 | yes |
| (2^65+1)/(8193×11) | 409368176241571 | 409368176241571 | yes |
| cofactor / v_131 | 3124947910241 / 1 | same; 131∤cofactor | yes |
| phi(130), phi(17030) | 48, 6240 | 48, 6240 | yes |
| k-set p=131 (lemma) | {130,17030} | {130,17030} | yes |
| k-set p=17 (lemma) | {8,136,2312} | {8,136,2312} | yes |
| analytic unknowns | 130×131=17030 | 17030 | yes |

Producer Stage 0/1/2 measured columns agree with the above for every
preregistered exact quantity. Random-b `0/10` is within the HEUR-H1
modeled prior (`≤1/10`); the prior itself remains modeled, not a
measured probability. Stage 2 unknowns column remains labeled
modeled/analytic.

Controls: modulus-swap p=17 matches; random-b null passes; order-15
null reported without Lemma L claim; basis-relabel invariant;
Phi_130 cross-check ok; certificate.kind vocabulary held; no-break
guard held.

---

## Inference

All three stages match the pre-registered Outcome A / DO-A path:

- Part 1 cyclotomic set and phi values hold on `k≤20000`.
- Phi_130(2) valuation `v_131=1` with cofactor check holds.
- Lemma L toy at n=17: dim=8, stable, equals ker m_t(sigma); nulls ok.
- n=131 image: dim=130 equals T_0; analytic unknowns/slot 17030 vs 131.

Official reading: **support** the scoped torus-row certificate with
numbers **48 / T_0 / 17030**, at evidence strength **preliminary**
(Coordinator-direct PD-1; single producer package; dual-seed Stage 1
replication present but not an independent-session replication).
Hypothesis `approved → supported`. Experiment `approved → analyzed`.
No break; no rho; no exponent. Couveignes–Lercier primary-text scope
obligation survives. KN-FIND promotion not warranted at preliminary
strength; ranked next work may include independent validator check of
Lemma L and a possible KN-OPEN-095df5 superseding note once strength
or independent review clears the gate.

Maps cleanly to hypothesis `DO-A-torus-row-certificate`. Not Outcome B
(toy fails), not Outcome C (unexpected low-phi k), not DO-D instrument
bug, not DO-E infrastructure.

---

## Limitation

- Scope: structural certificate for tori / Lemma L toys at n=17 and
  n=131 over F_2 with cyclotomic census `k≤20000`; not a curve attack.
- Analytic 17030 unknowns/slot is MODELED/analytic rank count — not a
  measured solver observation.
- HEUR-H1 is null calibration only (`0/10`); not a universal Lemma L
  proof.
- Couveignes–Lercier primary text unread — placement of the torus
  smoothness basis remains a scope obligation.
- IDEA-20260926-6f2601 claim text remains immutable/proposed.
- Coordinator-direct review without independent validator/red-team
  (PD-1) → strength capped at preliminary.
- Manifests dirty-at-write; Stage-1 seed-20261002 folded into one RUN
  id (disclosed).
- Peak RSS reported identically (~16 MiB) across stages — plausible
  getrusage granularity; not load-bearing.
- No break; no factor-base; no rho; no exponent; no ECC2K-130 cost claim.
- Transfer of certificate numbers into an attack construction is an
  explicit non-claim (`dominated_by` KN-FIND-47da4e on unknowns).
