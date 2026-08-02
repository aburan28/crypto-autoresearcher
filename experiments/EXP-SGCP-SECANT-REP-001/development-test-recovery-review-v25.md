# V25 Read-Only Recovery Review

## Handoff: V25 rejected on pinned-zsh semantics

### Claim or task

Review the immutable V25 successor for one read-only validation and separate
recovery seal of the consumed V23 fixed public development-test artifacts.

### Status

NEGATIVE RESULT

### Assumptions

- The exact pinned zsh 5.9 binary defines the runtime shell semantics.
- The protected source and test are not parsed, imported, compiled, or executed.
- `input.tar` remains opaque and is not extracted.
- No same-UID adversary mutates artifacts, objects, or refs concurrently.

### Evidence so far

- Protocol P:
  `742fd17d73e90c93ec0a57eb517e83e0cd9afbac`
- P tree:
  `5a7ec0fc7d5586076b691ade29d59a9052d5cee1`
- Sole parent:
  `eb8e263e15bf623744c446a98b94d8365dbc820a`
- Parent tree:
  `1c1d9f62c015c6d0ae0aaf31cdf000b256bac87f`
- Exact five-file delta order matches both the protocol and host preclaim.
- The five V24 findings were repaired in the immutable package.
- Three role-specific reviewer IDs were preallocated and pinned in P.
- All three pinned reviewers returned `REVISE`:
  - theory: `019faf1a-2a4d-7a42-bfa5-cf838994c250`
  - accounting: `019faf1a-3a03-75b3-a1f4-48ac199f3f69`
  - red team: `019faf1a-4f41-7253-befc-32f1f40b4c98`
- Recovery authorization A: absent.
- Recovery consumption and result refs: absent.
- Recovery directory: absent.
- Original V23 result ref: absent.

Bound P artifacts:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| authorization validator | 4,997 | `6e6fa12edb122b5e8c004ee25031ac154867c7f89a73e63053c228baf221c071` |
| host runner | 35,209 | `4d5f2fd7b6f8c32167b2980f9dbf78e994fad15848ac90b79e27919291dc94ea` |
| recovery protocol | 22,363 | `6347cbb6b7aa7b435ff0bb09ee7093ac173d49bffc81c56fd6af34acbfc7632b` |
| result validator | 11,737 | `c1645ba882cb4124f987202f8f6c732f10308cb643ccbe26b264479b595a2c51` |
| source manifest | 7,755 | `faa89ee0ce722a9d5ade319d6b6fcb162bfcf3ee77da428b8caa2c632bfc9ada` |

### Failure modes

`BLOCKING`: `status` is a read-only special parameter in the pinned zsh.
Assignments fail both at top level and after `local status`.

Affected surfaces:

- canonical bootstrap producer-status capture;
- host `verify_ref_absent`;
- host `capture_current_absence`.

The bootstrap therefore exits before executing a host byte. Even if bypassed,
the first absent-ref check fails before recovery-directory or ref creation.
This is a fail-closed protocol defect and not cryptanalytic evidence.

### Next concrete action

Create V26 with fresh refs and principals. Rename every shell variable named
`status`, proactively rename every local `path` tied to zsh's special `path`
array, and run isolated pinned-zsh outcome controls for return codes 0, 1, and
128 plus bootstrap marker retention before exact-commit review.

### Artifact paths

- `experiments/EXP-SGCP-SECANT-REP-001/development-test-recovery-protocol-v25.json`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-recovery-host-runner-v25.zsh`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-recovery-authorization-validator-v25.jq`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-recovery-result-validator-v25.jq`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-recovery-source-manifest-v25.json`
