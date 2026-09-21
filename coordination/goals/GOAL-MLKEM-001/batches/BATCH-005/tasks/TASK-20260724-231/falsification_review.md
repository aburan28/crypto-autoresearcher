# Independent falsification review of EXP-MLKEM-002

Task `TASK-20260724-231`  
Machine-readable verdict: `red_team_report.yaml` (`RT-20260724-001`)  
Role: independent Red Team; no official state change; write scope only

## Scope and evidence basis

This review attacks the claim that EXP-MLKEM-002's outcome class
`suite_is_discriminating` is justified. It does not change hypothesis,
experiment, evidence, or decision status.

Reviewed snapshot: commit `28608fb8a48ffbb8291c82810f2867553d3fe6f1`
(parent `e829ef7c26549dc3ee62796c89f16b1d1ac2500b`), archived by
`TASK-20260724-229`. All 39 `artifact_sha256` values in
`archives/TASK-20260724-229/snapshot-receipt.json` matched
`git show 28608fb:<path>`. Receipt `commit_sha` is null by convention;
Git subject/parent bind the archive. Unarchived `/tmp` build trees are not
treated as durable evidence, but were used for independent source inspection.

Inference: requested `review-xhigh`; resolved `cursor-grok-4.5-high` with
`fallback_used: true` and `independent_session: true` per
`inference-amendment-TASK-20260724-231.yaml`.

## Verdict

**`suite_is_discriminating` should stand** under the frozen experiment
definition. **ORS-025 and ORS-026 do not require correction** for presence,
versions, PRs, or byte/fraction claims. Surviving objections narrow scope
(integration semantics, null-result strength, direct-symbol vs Decapsulate,
missing `vectors/`, weak KAT anchor). None flips the outcome class.

## Attack line 1 — fabrication and provenance (defeated)

### Verification commands (executed 2026-07-24)

```bash
PREFIX=/tmp/exp-mlkem-002/wolfssl-5.9.1
POSTFIX=/tmp/exp-mlkem-002/wolfssl-5.9.2
git -C "$PREFIX" rev-parse HEAD   # 1d363f3adceba9d1478230ede476a37b0dcdef24
git -C "$POSTFIX" rev-parse HEAD  # ac01707f552c611fbd135cc723b2682b3e7f80f2
# AVX2: prefix ends at vmovdqu 1504(%rdi); postfix adds vmovdqu 1536(%rdi)
sed -n '16588,16755p' "$PREFIX/wolfcrypt/src/wc_mlkem_asm.S" | rg 'vmovdqu|vpxor'
sed -n '15378,15548p' "$POSTFIX/wolfcrypt/src/wc_mlkem_asm.S" | rg 'vmovdqu|vpxor'
# NEON: ins v9.b[0], v8.b[1]  ->  ext v9.16b, v8.16b, v8.16b, #8
sed -n '8910,8960p' "$PREFIX/wolfcrypt/src/port/arm/armv8-mlkem-asm.S"
sed -n '8922,8972p' "$POSTFIX/wolfcrypt/src/port/arm/armv8-mlkem-asm.S"
sha256sum "$PREFIX/wolfcrypt/src/wc_mlkem_asm.S" \
          "$PREFIX/wolfcrypt/src/port/arm/armv8-mlkem-asm.S" \
          "$POSTFIX/wolfcrypt/src/wc_mlkem_asm.S" \
          "$POSTFIX/wolfcrypt/src/port/arm/armv8-mlkem-asm.S"
# matches experiments/EXP-MLKEM-002/source-lock.yaml
```

Public records checked: [CVE-2026-10097](https://nvd.nist.gov/vuln/detail/CVE-2026-10097),
[CVE-2026-6330](https://nvd.nist.gov/vuln/detail/CVE-2026-6330). Both exist;
byte/half-input descriptions, version windows, and PR 10430 / PR 10192 align
with ORS-025/ORS-026 and with the assembly.

**Corroborated:** CVE IDs; AVX2 1536/1568 and indices 1536–1567; NEON
half-input class; affected ranges; fix in 5.9.2; function names and
instruction-level diffs; file hashes in `source-lock.yaml`.

**Uncorroborated (already labelled vendor/CNA in ORS-025):** ~350 chosen
ciphertexts and ~98% success. This experiment did not re-test them and they
are irrelevant to `suite_is_discriminating`.

**ORS correction verdict:** no fabrication correction required. Optional
wording only: ORS-026's "half" matches NVD and the measured counts
384/544/784, but the defect is reduction (`ins` vs `ext`), not a half-length
loop — already stated in `premise_verdicts.yaml`.

## Attack line 2 — attestation and dispatch (survives as narrowing)

`comparison_probe.c` selects backends with harness macros and calls
`mlkem_cmp_avx2` / `mlkem_cmp_neon` directly. Library Decapsulate uses
`mlkem_cmp` (`wc_mlkem.c` ~1566), which applies AVX2 only after
`IS_INTEL_AVX2` CPUID (and always NEON on aarch64+ARMASM).

Attestation in RUN-006/008 (equal/unequal self-test; AVX2 nm/objdump
`vpxor`/`vmovdqu`; `USE_INTEL_SPEEDUP` / `WOLFSSL_ARMASM` macros) binds the
linked symbol, not every normal Decapsulate dispatch.

Mitigant for AVX2: RUN-007 Algorithm-18 accepts on silent mutations prove the
live Decapsulate path ignored those bytes on this host for 43/64 pairs.
NEON: grids ran under `qemu-aarch64-static -L /usr/aarch64-linux-gnu` with
**no** integration checks in RUN-007. NEON findings remain primitive-level
under emulation.

This does not select `invalid_harness_or_dispatch`: backends were attested as
required; it narrows API-boundary transfer for NEON.

## Attack line 3 — silent-set semantics (survives as narrowing; does not flip class)

Primitive grid: mutate equal-length buffers and call the comparison symbol.
Integration: mutate a valid ciphertext and call Decapsulate.

For ML-KEM-1024, indices 1536–1567 lie in compressed `v`. A mutation can
change decrypted `m'`, so re-encryption differs in compared bytes 0–1535 and
FO rejects even though the optimized compare would ignore the mutated byte
when comparing two buffers that differ only there.

RUN-007: 43 true / 21 false; per index, 20 both-seed accept, 9 both-seed
reject, 3 seed disagreements (1539, 1544, 1564).

- **Does 43/64 undercut `suite_is_discriminating`?** No. Frozen experiment
  definition requires nonempty primitive silent sets matching source omissions,
  not universal integration accept.
- **Does it undercut the stronger H-MLKEM-002 prediction?** Yes, as written
  (`integration_oracle_observed` / "matching integration accept"). The
  executor already recorded the anomaly without exploitation.
- **Is the explanation adequate?** Yes: mechanism-consistent; prior BATCH-002
  red team already warned end-to-end mutation is not a complete primitive test.

## Attack line 4 — null-result strength (survives as narrowing)

Post-fix zero silent bytes / zero scalar disagreements are real under the
declared generator (xor 0x01/0xff × all indices × 2 keys × equal length ×
functional equality). They do **not** prove absence of multi-byte,
length-dependent, alignment-coupled, rare key-dependent, scalar-shared, or
timing-only defects. H-MLKEM-002 `interpretation_limits` already states this;
readers must not upgrade the null to "the comparison is correct."

## Attack line 5 — scope inflation (largely defeated)

`execution-report.yaml` `scope_statement` and H-MLKEM-002
`interpretation_limits` explicitly exclude key recovery, oracle construction,
exploitation, other libraries/versions, deployed systems, timing/physical
channels, and MLWE/passive security. No sentence in the execution report was
found that a careful reader must take as a security or attack claim.

Residual wording risk only: metric id `integration_oracle_observed` could be
misread; surrounding prose denies oracle construction.

## Attack line 6 — reproducibility (survives as low-severity narrowing)

`experiments/EXP-MLKEM-002/vectors/` is absent. However RUN-006/007 raw JSON
records `ct_sha256_seed1/2` (and KAT `ss_sha256`), and `SEED_MATERIAL` is
hardcoded in `comparison_probe.c`. An independent party can rebuild the tagged
wolfSSL trees, re-run the probe, and verify digests and silent tables. Exact
ciphertext blobs are not archived — inconvenience, not proof of fabrication.

## Outcome class against frozen precedence

| Class | Why not selected |
| --- | --- |
| `invalid_harness_or_dispatch` | Negative harness detected; backends attested; four terminal runs |
| `premise_unverified` | Both CVEs present with line-level asm evidence |
| `positive_control_undetected` | Silent sets nonempty and match source |
| `residual_patched_disagreement` | Post-fix disagreements all zero at coverage 1.0 |
| `suite_is_discriminating` | **Selected; stands** |

## Narrowest defensible claim

On wolfSSL peeled commits `1d363f3` (v5.9.1-stable) and `ac01707`
(v5.9.2-stable), a byte-complete single-byte xor differential suite applied
directly to the ML-KEM comparison primitives, with a detected
harness-truncated negative control, discriminated the source-verified AVX2
tail omission (indices 1536..1567 on ML-KEM-1024) and the source-verified
NEON reduction defect (silent counts 384/544/784 under qemu-aarch64) from the
corresponding post-fix backends, which showed zero silent indices and zero
scalar-versus-optimized disagreements at full coverage for the three FIPS
parameter sets and two seeds tested. Algorithm-18 integration on pre-fix AVX2
silent indices accepted on 43/64 pairs (mechanism-consistent, not universal).
Laboratory functional discrimination for these builds and this generator only —
not all-input correctness, not native-ARM NEON API attestation, not
exploitability, not other libraries, and not MLWE or passive ML-KEM security.

## Next concrete action

Coordinator may keep `suite_is_discriminating` while binding OBJ-001..005 as
scope limits on H-MLKEM-002 support language. Optional cheapest follow-ups
(not required for the outcome class): message-stability annotation of the 21
non-accepting AVX2 integration cells; small NEON Decapsulate sample.
