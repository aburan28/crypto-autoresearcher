# Prym experimental design brief

Owner request: devise experiments for issue #2414. This is design work; no
scientific execution or claim-changing review is authorized by this brief.
Base: d0f70c0a0905a5d4d2fc7c082b6dd85e43094026. Parent intake is
`research/prym_relation_followup_20261019/README.md`.

Use the existing proposal IDEA-20260909-4c5ee9. Preserve every historical
contract and the scoped P1546 disposition. Design four sequential experiments:

1. **Geometry and transfer screen** H-ECDLP-9e7a19 / EXP-ECDLP-da4ba3.
   Deterministically generate eight squarefree quadratic h=(x-a)(x-b), with
   gcd(h,x^3+7)=1, at each p in [11,13,17,19,23,31,43,59]. Enumerate sorted
   pairs a<b lexicographically; take the first eight. These are 64 NEW toy
   covers, not the unsourced historical 32. Count E, H and D over Fp/Fp2;
   derive degree-2/4 Frobenius polynomials, factor gcd over Q and check point
   count identities. Do not describe two trace checks as a complete independent
   Frobenius verification for genus-3 D. Synthetic shared/coprime polynomial
   controls test the screen but certify no geometric transfer map. Implemented
   pilot covers this arithmetic only; Jacobian map checks remain a separate
   implementation obligation if included. No ECDLP advantage from this stage.

2. **Public source-witness and native-rank audit** H-ECDLP-51f052 /
   EXP-ECDLP-ad0ffe. Define exact constructor APIs, public known-source rows,
   unknown-log factor-base atoms, canonical distinct norm columns and rank mod
   r. Start with explicitly documented PO-transfer-003 generator as calibration;
   it is not the missing new router. Include positive planted correctness,
   duplicate/sign columns, zero rows, post-hoc kernel residual, tuple-first
   unknown-source-scalar and known-false source labels. Separate historical
   fixtures from fresh holdouts. Blind Q goes only to the attack process; a
   challenge process alone holds k. Meaningful rank target derives from the
   actual number of distinct unknown columns, not a universal B-1 claim.

3. **Paired auxiliary-Prym ablation** H-ECDLP-7cd883 / EXP-ECDLP-5e7e74.
   Freeze a public candidate stream, baseline pipeline and exact Prym selector
   bytes BEFORE trials. Define identity-selector A/A, real companion selector,
   permuted companion labels and split-product control. Same memory allowance,
   factor base, target and amortization. Charge generation of labels, selector
   training/tuning if any, all rejects, row normalization and independent rank.
   The prospective candidate below supplies an explicit selector component;
   its integration with the generator, baseline and launcher is still needed.
   Never call a generic interface or isolated component a runnable experiment.
   A fixed-pool census estimates precision/recall only; rerun the full paired
   pipeline for cost, charging the skipped baseline work appropriately.

4. **Blind full-pipeline recovery and scaling** H-ECDLP-ad8992 /
   EXP-ECDLP-e193fa. Conditional on the source/rank and ablation gates, freeze
   fresh prime-subgroup toy sizes [11,13,15,17] bits (r, not p), deterministic
   public curves, ten independent instances per size and three paired seeds.
   Instance generation itself must have a frozen deterministic search rule,
   charged failures, and exact constants archived BEFORE approval. Until that
   exists, keep review_required. Complete S, memory, verification and rho gap;
   success is an independently verified improvement over the CURRENT matched
   IC baseline (not historical PO003 and not mandatory sub-rho). Synthetic
   k must be absent from attack inputs and logs until sealed recovery output.

All protocols need variable_ledger, A/A, honest prediction_provenance (historical
PO003 and chat F43 were seen), transfer obligations with typed draft assessment,
controls, metrics/units, sample sizes, deterministic stopping/invalidation,
decision impact and artifacts. No measured gains, asymptotic exponent or
secp256k1/P-256 insecurity claim. No old IDEA-002 matrix execution.

Reserve runtime approval for native preapproval approvable=true. All four
start review_required, approved_by:null. Missing exact baseline, selector,
launcher/admission or immutable challenge set is a named blocker, not an
empirical failure. Budget estimates advisory; one science worker and 2GiB
headroom guard. Statistical design: curve/instance is the independent unit;
within-instance seeds paired, not independent evidence. Predefine confidence
interval and multiple-size decision rule; do not claim a power guarantee
without an expected-effect/variance model.

Coordinator design task writes only the four hypothesis YAMLs, four experiment
specification YAMLs and `protocol_summary.json` named on its handoff. It may
read but must not change AGENTS, goals, prior records, intake, renderer or git.
No nested agents; no scientific trials; no approval or official transition.

## Prospective selector candidate (design addendum)

Use PO003 C:y²=x6+A*x²+B and auxiliary quotient
E2:V²=W³+A*W²+B², (W,V)=(B/x²,B*y/x³). For the four interpolation points
(negative public source lift and three signed FB lifts), form their E2 sum S.
For S at infinity use a dedicated bin; otherwise bin by
(Legendre(W), floor(16*W/p)), using the canonical integer W. This is a public
feature, not a theorem that it predicts smoothness. Its cost may exceed the
residual quadratic check. Reject exceptional x=0, infinite inputs and repeated
interpolation abscissae by a fixed rule and charge each rejection.

Before looking at acceptance, split full canonical candidate identities by
SHA-256 parity (last hex nibble even=train, odd=holdout). Identity fields are
curve_uid, source_scalar, lambda, signed_fb_lift_ids; no unknown logarithms.
Obtain 2^16 distinct tuples in each partition, with no cross-partition repeats.
Insufficient finite support is inconclusive, not permission to change the
sample. Train each nonempty bin's rate (hits+1)/(attempts+2). Hits require both
residual E1 endpoints in the exact FB and a valid source-labelled row. Retain
ceil(nonempty bins/4) highest rates; ties by canonical bin string; reject unseen
bins. Freeze the model before holdout. Label-permutation controls use identical
counts, training effort and a frozen permutation. Charge training, maps, group
operations, selection, all rejects and recovery in the full paired test.

The components in companion_selector.py implement the map, addition, bins,
split and model rule, with software-only tests. Integration is still absent.
This is an engineering ablation of a fixed generator, not an operation outside
P1546 and not a new asymptotic attack. The compact source-labelled router
remains a separate open problem. Historical tiny cells are calibration only;
fresh independent curves, not tuple counts, are the inferential units.
