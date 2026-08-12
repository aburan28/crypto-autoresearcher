# Development-Test Execution Review V5

## Handoff: sealed-state cleanup and inventory counterexamples

### Claim or task

Determine whether V5 safely authorizes exactly one immutable, isolated run of
the five hash-bound public development tests under its explicit trusted-local
model.

### Status

NEGATIVE RESULT

### Assumptions

- Static review at exact commit
  `e86dfe1b537ce8f2a04cb80a3bcb93c0672853d9`.
- No protected source/test was parsed by Python, imported, compiled, tested, or
  executed; no repository runner was invoked.
- Inert Docker, Git, and synthetic JSON probes contained no protected input.
- Cryptanalytic baselines, relation collection, rank, descent, and ECDLP
  performance remain outside this development-control review.

### Evidence so far

- Reviewed tree:
  `1ecbc2ebafb48ac1546c9c2457326e9496d799e0`.
- Sole parent:
  `c0460d0c97557b0349a508630519e42124587675`.
- Protocol SHA-256:
  `21b46b3d01ee7737e758e6900ab888d6b3ab532f525d9cf94d4611f1fa2121ca`.
- Host-runner SHA-256:
  `e0aab362c15c18add2a0a638c805addd2f6197349677355b8a0ca11a74c503e8`.
- Authorization-validator SHA-256:
  `04b64d326921e3c0990b73fe0e0db9690f8c72c566fe973970596c44835f3830`.
- Result-validator SHA-256:
  `924eef7a3bfd4050043e6a0066556303d8c879527656a643683d447cde9d7f95`.
- Inherited container runner SHA-256:
  `8ab5ae9c6495a430badcb803956cca1a02593a510a0b1def5e2c5d065d3e5cf5`.
- Protected source/test hashes remained
  `8b8781d688188afa41e87f33e15a306fc5a9f5326b8e93316247263ee8f933bd`
  and
  `2b0e34524f22cf5d2dd70c3eff857b186c10c9d8882bb2893999febc1352417a`.
- Theory principal `019fad8a-d56e-7122-98f0-68387c273f5c`,
  accounting principal `019fad8a-ec55-7882-8d27-1383728e043e`, and
  red-team principal `019fad8b-1821-7912-9030-e41220cf87b0` all returned
  `REVISE`.
- Synthetic authorization/result fixtures confirmed canonical-byte rejection of
  wrong-name, floating-number, and duplicate-key inputs. Inert controls
  confirmed Docker `--cidfile`, exact security projection, Git C/R topology,
  zero-old-value CAS replay rejection, and hostile-filter detection without
  executing the filter.

### Failure modes

- `CLEANUP_BEFORE_SEAL_GAP`: after Docker cleanup or absence proof fails, the
  runner can downgrade the classification and still install R. Cleanup is
  structurally required only for the valid classification.
- `SEALED_INCOMPLETE_STATE`: the fallback accepts and seals
  `INCOMPLETE_INFRASTRUCTURE_FAILURE`, contradicting the protocol predicate that
  incomplete means C exists and R is absent.
- `POST_CAS_SUCCESS_GAP`: the result-created flag is set before fallible
  post-CAS verification. A later verification failure can retain a successful
  terminal classification.
- `ANCESTOR_SYMLINK_GAP`: the experiment path and its ordinary ancestors are
  not proved to be nonsymlink physical directories before inventory and run
  path construction.
- `ARTIFACT_UNIVERSE_GAP`: visible regular-file/directory globs omit dotfiles
  and do not reject every FIFO, socket, device, or other nonregular object.
- `CLEANUP_BYTE_NORMALIZATION`: command substitution strips trailing newlines,
  so the claimed exact one-LF Docker absence receipts are not byte-exact.
- `GIT_COMMAND_CONFIG_GAP`: local-scope filter checks omit worktree-scope
  configuration and command-capable archive keys such as
  `tar.<format>.command`.
- `ELAPSED_SCOPE_OVERCLAIM`: `host_elapsed_seconds` is finalized before
  manifest construction and result sealing even though the protocol says it
  includes that work.
- `RESOURCE_TEXT_CAVEAT`: `resource.txt` is retained and hash-bound but not
  semantically validated; cgroup JSON is the stronger resource receipt.

### Strongest valid statement

V5 materially improves canonical authorization/result binding, immutable C/R
topology, Docker-create recovery, exact source/test identity, and isolated
five-test semantics. It does not authorize execution because terminal result
sealing can occur without proved cleanup, and path/artifact/config predicates
do not yet establish the claimed closed filesystem and command surface.

This is a restricted negative result for the V5 host-controller state machine.
It is not evidence against the SGCP mathematical hypothesis, index calculus, or
prime-field ECDLP.

### Next concrete action

Create V6 with cleanup and exact name/ID absence as a prerequisite for every R,
no sealed incomplete classification, preverified result objects with CAS as the
last fallible seal operation, physical nonsymlink ancestry, NUL-safe all-type
artifact inventory, byte-exact cleanup comparisons, local/worktree
filter/archive-command rejection, and accurately scoped elapsed accounting.

### Artifact paths

- `experiments/EXP-SGCP-SECANT-REP-001/development-test-execution-protocol-v5.json`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-host-runner-v5.zsh`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-authorization-validator-v5.jq`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-result-validator-v5.jq`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-review-v5.md`

No development-test or experiment-execution authority is granted.
