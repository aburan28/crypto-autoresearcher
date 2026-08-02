# V24 Read-Only Recovery Review

## Handoff: V24 recovery protocol rejected before authorization

### Claim or task

Review one immutable, zero-run protocol for read-only validation of the consumed
V23 fixed public development-test artifacts and creation of a separate recovery
seal.

### Status

NEGATIVE RESULT

### Assumptions

- Git object and direct-ref semantics are trusted within the stated model.
- The protected source and test are not parsed, imported, compiled, or executed.
- `input.tar` remains opaque and is not extracted.
- No same-UID adversary mutates artifacts, objects, or refs concurrently.

### Evidence so far

- Protocol commit P:
  `3a7d9551f42e65e556813f79ea85e60c7a0d64c2`
- P tree:
  `b50d56b70f31751077e39d1f5aca803e66d539c3`
- Sole parent:
  `5e9b0f5d803805bacfa35ab4f5060618d1ee45e2`
- Parent tree:
  `f912e5234673044c3e5d362f49f4223cf32feda7`
- P adds exactly five mode-`100644` files.
- Recovery authorization A: absent.
- Recovery consumption and result refs: absent.
- Recovery directory: absent.
- Original V23 result ref: absent.
- All 53 V23 source-manifest file tuples, the sole mode-`555`
  `evidence-input` directory, and the three required-absent paths matched during
  read-only review. The archive was not extracted.
- Three fresh reviewers returned `REVISE`:
  - theory: `019faf0c-bf1c-7561-a90b-757061e12d48`
  - accounting: `019faf0c-da49-7ec1-9c40-4689a99aabc3`
  - red team: `019faf0c-f3e3-7351-af12-0e015a5f0f46`

Bound P artifacts:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| authorization validator | 4,887 | `fe5c6e27ed399843421a987eb7884795cbf08de47d5059e84a4e06dc549fddd5` |
| host runner | 34,632 | `076759bfa9f3299b847f3b4c1b9b96482400d9a611b01624744d2643cc24194c` |
| recovery protocol | 21,184 | `1bd09f1e21963f0f0c95a1c7ef6a8926fb985ca851d4b911793e8d86f2e8b885` |
| result validator | 11,456 | `20e23a2fb56108343d2235876db9aee5064fb994adf8d3311f634543b3ee3ff8` |
| source manifest | 7,755 | `c1f1f53ce5bb69a886c5f3d8432287e2aaf3f919caa2767f3711b35d9082dbc2` |

### Failure modes

1. `BLOCKING`: Git emits P paths in authorization-validator, host-runner,
   protocol, result-validator, source-manifest order. The protocol and host
   expected protocol before host-runner, so the exact preclaim always fails.
2. `BLOCKING`: the exact recovery seal omits an immutable preprocessing and
   fixed-overhead accounting nonclaim.
3. `HIGH`: `verify_ref_absent` treats every nonzero `show-ref` outcome as
   absence instead of requiring exactly status 1 with empty output.
4. `HIGH`: reviewer IDs are only UUID-shaped and nonexcluded; they are not
   pinned in P before review.
5. `MEDIUM`: source branch and consumption refs are resolved to objects without
   separately rejecting symbolic refs.

These are protocol defects only. V24 executed nothing, consumed no authority,
created no recovery ref, and makes no cryptanalytic claim.

### Next concrete action

Create a V25 successor that uses canonical Git delta order, adds exact
preprocessing/fixed-overhead nonclaims, requires exact ref-absence status,
rejects symbolic source refs, and pins three fresh orchestrator-issued reviewer
IDs in P before exact-commit review.

### Artifact paths

- `experiments/EXP-SGCP-SECANT-REP-001/development-test-recovery-protocol-v24.json`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-recovery-host-runner-v24.zsh`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-recovery-authorization-validator-v24.jq`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-recovery-result-validator-v24.jq`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-recovery-source-manifest-v24.json`
