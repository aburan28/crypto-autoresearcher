---
id: KN-FIND-14f145
type: internal_finding
title: Selected secp256k1 compact known-CM prime-degree M44497 endpoint independently
  replayed
tags:
- isogeny
- known-cm
- secp256k1
- mersenne
- native-replay
- bounded-endpoint
confidence: established
internal_refs:
- EV-ISOU-263837
- DEC-20261016-b60d77
- EXP-ISOU-0c7e60
- H-ISOU-ffa8b0
proof_status: certificate
proof_refs:
- coordination/goals/GOAL-ISOU-f30a07/m44497/execution/TASK-20261016-6db186/native-evidence.tar.gz
- coordination/goals/GOAL-ISOU-f30a07/m44497/reviews/TASK-20261016-4bad89/report.md
- experiments/EXP-ISOU-0c7e60/runs/RUN-ISOU-384b62/raw-result.json
evidence_refs:
- EV-ISOU-263837
decision_ref: DEC-20261016-b60d77
experiment_refs:
- EXP-ISOU-0c7e60
run_refs:
- RUN-ISOU-bb340e
- RUN-ISOU-384b62
claim_tier: crypto
added: '2026-10-16'
superseded_by: null
---

# Finding

Exact secp256k1 admits the selected compact known-CM separable self-isogeny of prime degree 2^44497-1, with unreduced Eisenstein coefficients, independent native primality/norm/source/point/dual replay and declared trusted SEC2 field/order primality.

Certificate SHA25685b5db3665a52a8fd04554964c03a6ed208bbb7ad1749770f5fa9d528b77f5d1 (63615 bytes),13 native entries11PASS+2trusted qualifiers. Native operation83029/351050ms; supervisor83051/351076ms; sampledpeak5406720/5341184B. This is endpoint evidence, not a timing ratio.

# Scope and limits

One selected compact known-CM endpoint; no global record, novelty, expanded-map score, all-curve transfer or security claim.

SEC2 p/n primality is trusted-standard, not a self-contained primality certificate. Universal degree rests on the reviewed endomorphism/dual theorem plus exact norm; finite points alone do not prove degree.

IDC1hf56b3716b0a7eb8b proof is null: finite evaluated supplement, distinct from two native exact-Z expansions and the reviewed theorem.

Replicated describes independently recomputed endpoint via distinct native arithmetic paths on the same certificate, not independent instance/population/timing replication. One measurement per phase; no A/A, speedup ratio, uncertainty interval or cold-campaign total.

Sampled worker RSS is not an OS hard cap, total wrapper RSS or live disk quota. Actual CPU is separately recorded; sealed canonical cpu_seconds:null remains unchanged.

Verifier OS real351.04s is36ms below supervisor351.076s; instruments are separate, discrepancy unresolved. Internal LL/Cornacchia/point/serialization subphase timings unavailable.

Build/control/custody/session costs excluded from target operation totals. No prescribed-execution proof, external settlement or total-campaign cost certificate.

Earlier M8191 rejection/nonstart and P19250341 censors preserved; no presumed LL defect, independent compositeness conclusion, or larger expanded construction approved.

The earlier M8191 reject is preserved as its native observation, without an independent compositeness conclusion or inferred source bug. Primary expanded replay optimization remains next; this compact finding cannot promote an expanded-map board.
