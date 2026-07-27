---
id: KN-FIND-001
type: internal_finding
<<<<<<< HEAD
title: Decomposition-yield conservation — factor-base geometry cannot change mean yield, only redistribute it
tags: [index-calculus, factor-base, decomposition-yield, coverage, point-decomposition, conservation, ecdlp, toy-scale]
confidence: established
proof_status: derivation
proof_refs:
  - experiments/EXP-FB3-001/conservation.md
  - experiments/EXP-FB3-001/analysis.md
  - coordination/goals/GOAL-ICLIFT-001/batches/BATCH-001/tasks/TASK-20260724-232/validation_notes.md
  - coordination/goals/GOAL-ICLIFT-001/batches/BATCH-001/tasks/TASK-20260724-233/objections.md
internal_refs: [H-FBG-001, RQ-FBG-001, EV-FBG-001, DEC-20260724-007, RUN-FB3-001-N18]
claim_tier: toy
=======
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
>>>>>>> origin/main
added: 2026-07-24
superseded_by: null
---

<<<<<<< HEAD
## Statement

Let `G` be a finite abelian group of order `N` and `D ⊆ G \ {0}` a factor base of
`B` distinct elements. For `m ≥ 1` and `r ∈ G`, let `c_D(r)` be the number of
size-`m` multisets from `D` summing to `r`. Then

```
sum over r in G of c_D(r)  =  binomial(B + m - 1, m)
```

exactly, because every size-`m` multiset sums to exactly one target. Hence the
mean per-target decomposition yield is

```
E_r[c_D(r)] = binomial(B + m - 1, m) / N
```

for **every** base of size `B`, independently of how `D` is chosen.

## Consequences (all confirmed against measurement in EXP-FB3-001)

1. **Mean yield is not a design lever.** The yield ratio of any structured base
   against a matched random base of the same size is exactly 1. Measured over
   144 cells at `N ~ 2^14/2^16/2^18`, the maximum absolute deviation of the exact
   cell mean from `binomial(B+2,3)/N` was exactly 0.
2. **Any "growth with N" clause on mean yield is identically satisfied at slope
   zero.** A hypothesis of the form "some geometry's mean-yield advantage grows
   with N" is refuted by arithmetic before any experiment runs.
3. **Only the distribution is free.** Coverage (the fraction of targets with at
   least one decomposition) obeys `coverage ≤ min(1, mean)`, with equality iff no
   target has two decompositions. Additive structure that creates repeated sums
   therefore *lowers* coverage at matched size: the H017 small-multiples base
   collapses to a coverage ratio of 0.0021 at `2^18` while its concentration
   statistic reaches 1224x.
4. **Typing is a fixed penalty, not a lever.** For typed decompositions with
   sub-base sizes `B1 + B2 + B3 = B`, the total is `B1·B2·B3 ≤ (B/3)^3 = B^3/27`,
   strictly below the untyped `binomial(B+2,3) ≈ B^3/6`. Measured penalty at a
   balanced split: 4.817x.

## What this does not say

- It does **not** say structured bases cannot beat random bases. Coverage headroom
  up to `min(1, mean)` is real and reachable: a Bose–Chowla `B_3` (Sidon) base
  attains it exactly, with a measured coverage ratio of 1.1071, and a whole-group
  low-collision greedy reaches 1.0269 at the parameters of the tested battery.
  The headroom ceiling is about +54%.
- The cost benefit of that headroom is bounded. Under a harvest-all solve, the
  relations obtained per solve equal the mean and are exactly geometry-invariant.
  Under one-relation-per-target, the gain is at most
  `min(1, μ)/(1 − e^{−μ}) ≤ 1.582`, maximised at `μ = 1`.
- It says nothing about the **cost of finding** a decomposition (the
  summation-polynomial / point-decomposition solve) or about the linear-algebra
  stage — which is where the index-calculus cost actually sits.
- It is **consistent with index calculus working**: the Gaudry–Diem `1/n!`
  decomposition probability over extension fields *is* this conservation mean.
  The extension-field advantage lives in the solve, not in the yield.
- Relation rank and independence are not captured: the mean scores a
  rank-deficient base as tied with a random base of the same size.

## Why it is worth recording

The identity is a one-line double count, but the repository had budgeted 24 CPU
hours and 96 runs for a battery (`EXP-FB3-001`, approved by `DEC-20260717-002`)
whose primary metric it makes vacuous, and the earlier scoped negative
`EV-FB-001` reported "yield tracks the combinatorial `|FB|³/N`" as an empirical
observation without noting that it cannot do otherwise. Recording it converts a
recurring empirical null into a screening rule: **a factor-base proposal that
promises higher mean yield at matched size is refuted on sight; only proposals
that argue about coverage, relation rank, recognizability, or solve cost are
worth measuring.**

## Provenance

Pre-registered in `experiments/EXP-FB3-001/amendment-001.yaml` and committed in
the protocol snapshot (`81d9e9f`) *before* any cell was measured, then confirmed
by the battery (`68e375f`), independently recomputed by the validator without
importing executor code, and bounded by the red team's Sidon and corrected-greedy
probes. Toy scale: `N ≤ 2^18`, 12 generated prime-order curves, `m = 3`.
=======
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
>>>>>>> origin/main
