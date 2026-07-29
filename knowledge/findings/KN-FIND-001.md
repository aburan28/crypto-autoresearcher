---
id: KN-FIND-001
type: internal_finding
title: Byte-complete differential probing of the ML-KEM comparison primitive discriminates incomplete re-encryption comparisons at fix boundaries
tags: [ml-kem, fips-203, implicit-rejection, re-encryption-comparison, conformance-testing, differential-testing, wolfssl, avx2, neon, defensive, post-quantum]
confidence: reported
internal_refs: [EV-MLKEM-005, DEC-20260724-018, H-MLKEM-002, EXP-MLKEM-002]
proof_status: empirical_only
proof_refs:
  - experiments/EXP-MLKEM-002/execution-report.yaml
  - experiments/EXP-MLKEM-002/analysis/premise_verdicts.yaml
  - experiments/EXP-MLKEM-002/analysis/coverage_maps.json
  - coordination/goals/GOAL-MLKEM-001/batches/BATCH-005/tasks/TASK-20260724-230/validation_report.yaml
  - coordination/goals/GOAL-MLKEM-001/batches/BATCH-005/tasks/TASK-20260724-231/red_team_report.yaml
evidence_refs: [EV-MLKEM-005]
decision_ref: DEC-20260724-018
experiment_refs: [EXP-MLKEM-002]
run_refs: [RUN-MLKEM-005, RUN-MLKEM-006, RUN-MLKEM-007, RUN-MLKEM-008]
source_refs: [KN-LIT-080]
claim_tier: laboratory_implementation_conformance
added: 2026-07-24
superseded_by: null
---

## Finding

FIPS 203 Algorithm 18 returns the genuine shared secret only when the
re-encrypted ciphertext equals the received ciphertext in **every** byte. An
optimized comparison that reads fewer bytes than the ciphertext length is
functionally silent on valid known-answer tests, because valid ciphertexts agree
everywhere including the compared prefix. Probing the comparison primitive
directly with a byte-complete single-byte differential grid turns that omission
into a deterministic, per-index observable.

Applied to wolfSSL at peeled commits `1d363f3` (`v5.9.1-stable`) and `ac01707`
(`v5.9.2-stable`), the gate:

- detected the x64 AVX2 tail omission exactly, silent set `{1536..1567}` on
  ML-KEM-1024, matching `mlkem_cmp_avx2` in `wolfcrypt/src/wc_mlkem_asm.S`
  ending at `vmovdqu 1504(%rdi)` and thus covering 1536 of 1568 bytes;
- detected the aarch64 NEON defect, silent cardinalities 384 / 544 / 784 across
  the three parameter sets, matching the horizontal reduction
  `ins v9.b[0], v8.b[1]` in `wolfcrypt/src/port/arm/armv8-mlkem-asm.S`;
- produced zero silent indices and zero scalar-versus-optimized disagreements on
  both post-fix backends at complete byte coverage;
- flagged its own deliberately truncated negative control with exactly the
  omitted ranges, which is what makes the post-fix null interpretable.

## What makes the gate trustworthy

Four design elements did the work, and a conformance suite missing any of them
produces a null that means nothing:

1. **A negative harness reported first.** A truncated harness-side comparator
   must be flagged with exactly its omitted range before any library result is
   read. Otherwise a clean sweep is indistinguishable from a broken generator.
2. **Backend attestation.** A null on a supposedly optimized backend is
   meaningless if runtime dispatch quietly selected the scalar path. Every
   measurement must name the code path that actually ran.
3. **Primitive-level probing.** Testing at the API boundary alone conflates
   comparison completeness with the FO re-encryption that precedes it.
4. **Separation of length from content.** Malformed-length rejection is not
   equal-length implicit rejection and must never be counted as an omission.

## Mechanism note: primitive silence is not universal API accept

Algorithm-18 integration on the pre-fix AVX2 silent indices accepted a mutated
ciphertext on 43 of 64 index/seed pairs, not 64 of 64. This is what the
mechanism predicts. A mutation inside the uncompared tail of the compressed `v`
sometimes flips the decrypted message; the re-encryption then differs inside the
**compared** prefix, and the FO comparison rejects anyway. Accepts occur exactly
for message-stable mutations. Any future report must keep the primitive silent
set and the integration-accept table as separate columns.

Related clarification: the vendor description of the NEON defect as ignoring
"half of its input" is accurate as to effect, but the mechanism is a defective
horizontal reduction (`ins` replaced by `ext` in the fix), not a half-length
loop bound.

## Limits of applicability

- Scoped to the two audited commits, the backends built and attested, three
  parameter sets, two seeds, and a single-byte xor generator.
- The post-fix null does **not** prove comparison correctness. Untested defect
  classes include multi-byte and coordinated mutations, alignment or lane
  coupling, length-dependent paths, key-dependent behavior, defects shared by
  scalar and optimized code (a differential is blind to those), and anything
  timing-only or microarchitectural.
- NEON measurements were made under `qemu-aarch64` at the primitive level, with
  no Algorithm-18 integration check and no native-silicon attestation.
- The conformance anchor used was deterministic encapsulate/decapsulate
  self-consistency plus scalar cross-commit equality, the weakest anchor the
  protocol accepts. Naming NIST ACVP or in-tree KATs would strengthen it.
- This is a defensive functional-conformance result. It is not an attack, an
  oracle, an exploitability finding, or evidence about MLWE hardness or passive
  ML-KEM security. Vendor-reported exploitation figures for CVE-2026-10097 were
  not re-executed by this program and keep their vendor label.
