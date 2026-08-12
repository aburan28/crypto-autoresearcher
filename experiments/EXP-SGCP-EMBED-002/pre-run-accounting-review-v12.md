# Findings

No Critical, High, Medium, or blocking accounting defects were found.

1. **Low — The committed record does not substantiate the claimed real-exFAT observation.**

   `revision-response-v12.md:23-26` and `development-test-log-v12.md:67-70` state that an actual exFAT volume returned `ENOTSUP` for hard-link and macOS `RENAME_EXCL` publication. The committed test instead injects `ENOTSUP` by replacing `_publish_no_replace`; it does not exercise or record either filesystem primitive on exFAT (`tests/test_sgcp_embed_family.py:4198-4225`). No committed command, stdout/stderr, filesystem identity, or syscall trace supports the stronger environmental claim.

   This is a documentation/evidence defect, not a static defect in the fallback implementation. The wording should say the test *simulates* an unsupported-filesystem response unless the real exFAT probe and output are preserved separately.

2. **Informational — Publication acceptance depends partly on protocol, not an on-disk marker.**

   The direct `O_EXCL` fallback can leave a partial final path after interruption (`src/verify_sgcp_embed_family.py:7115-7140,7189-7205`). The documents correctly define such a path as unaccepted and permanently unusable (`revision-response-v12.md:28-32`; `protocol-amendment-v12.json:27`). Enforcement of “unaccepted” therefore depends on successful writer return and downstream verification of the complete self-hashed report. This is appropriate for launch-plan design but must become an explicit runner rule.

# Independent accounting derivation

The canonical grid has eight unique generated curves: four bit sizes and two seeds. Each curve is reused across its 21 rows: three `B` values multiplied by three coordinate families plus four null replicates. Thus the completed matrix has `8 × 3 × 7 = 168` rows (`src/verify_sgcp_embed_family.py:61-70,86-91`).

Independent reconstruction of the domain-separated SHA-256 transcript produced:

| `(bits, seed)` | Accepted `(p,a,b,q)` | Draws | Nonsingular draws | Mobius attempts | Two-Mobius attempts | Null hashes |
|---|---:|---:|---:|---:|---:|---:|
| `(5,101)` | `(29,4,28,31)` | 12 | 12 | 3 | 6 | 180 |
| `(5,211)` | `(23,2,17,19)` | 49 | 47 | 3 | 7 | 108 |
| `(6,101)` | `(47,17,20,37)` | 4 | 4 | 3 | 7 | 216 |
| `(6,211)` | `(43,35,37,47)` | 15 | 14 | 3 | 6 | 276 |
| `(7,101)` | `(89,69,72,107)` | 11 | 11 | 3 | 6 | 636 |
| `(7,211)` | `(89,36,83,83)` | 8 | 8 | 3 | 6 | 492 |
| `(8,101)` | `(199,55,163,211)` | 3 | 3 | 3 | 6 | 1,260 |
| `(8,211)` | `(131,58,79,139)` | 10 | 10 | 3 | 6 | 828 |

The calculations are:

- Prime candidates: each unique `(bits,seed)` scans the full interval of size `2^(bits-1)` (`src/verify_sgcp_embed_family.py:984-990`). Therefore  
  `2 × (2^4 + 2^5 + 2^6 + 2^7) = 2 × 240 = 480`.

- Curve draws: accepted draw index plus one gives  
  `12 + 49 + 4 + 15 + 11 + 8 + 3 + 10 = 112`.

- Curve hashes: `p`, `a`, and `b` each require one domain-separated hash per draw (`src/verify_sgcp_embed_family.py:993-998`), hence  
  `3 × 112 = 336`.

- Registered-curve point enumerations: every nonsingular draw is enumerated once during rejection analysis and once for its independent recount (`src/verify_sgcp_embed_family.py:919-942,1003-1015`). Singular draws are not enumerated. Thus  
  `2 × (12 + 47 + 4 + 14 + 11 + 8 + 3 + 10)`  
  `= 2 × 109 = 218`.

- Predicate hashes:

  - Least-x rows perform no predicate hash.
  - The 24 single-Mobius rows require one successful attempt each: `24 attempts × 3 hashes = 72`.
  - The 24 two-Mobius rows contain 48 maps. Their attempts total `50`—two curves have one map requiring a second nonce—so `50 × 3 = 150`.
  - Each null row hashes every admissible two-point root (`src/sgcp_embed_family.py:549-568`). For these odd prime-order curves the admissible-root count is `(q−1)/2`. There are `3 B × 4 replicates = 12` null rows per curve, giving:
    `12 × Σ((q−1)/2)`  
    `= 12 × (15+9+18+23+53+41+105+69)`  
    `= 12 × 333 = 3,996`.
  - Total: `72 + 150 + 3,996 = 4,218`.

This independently reproduces the completed vector:

`480 / 112 / 336 / 218 / 4,218`

The verifier derives the same values only from semantically verified public transcripts (`src/verify_sgcp_embed_family.py:619-656`) and checks equality only after all row semantics succeed (`src/verify_sgcp_embed_family.py:6497-6551`). The test pins all five values and injects one-unit undercharge and overcharge for every field (`tests/test_sgcp_embed_family.py:3270-3347`).

# State and routing audit

Each public `verify_document` creates a fresh `_VerificationState`, installs it through a `ContextVar`, and restores the exact prior token in `finally` (`src/verify_sgcp_embed_family.py:499-513,7007-7013`). Actual work, reservation, and registered-curve cache are owned by that state (`:500-506`).

Consequences from static control flow:

- **Successive calls:** each receives a newly constructed state.
- **Nested/callback-reentrant calls:** the inner state shadows the outer state; token reset restores the outer object.
- **Concurrent threads and asynchronous contexts:** `ContextVar` separates contexts, while each call’s mutable state object is newly allocated rather than inherited.
- **Exceptional exits:** the outermost `finally` always resets the token.
- **Reset order:** path verification clears its invocation cache, resets work, and clears the reservation before processing (`:6836-6842`). V12 semantic entry repeats cache-clear then work/reservation reset (`:6313-6321`); this is redundant but safe.
- **Reservation ownership:** the source-derived reservation is assigned to the active state before semantic work and is preserved across semantic exceptions.
- **Registered-cache ownership:** lookup, miss, and cached bundles operate exclusively through the active state (`:970-1038`).
- **Completed equality:** the five provenance/predicate counters require exact transcript equality, not merely reservation dominance (`:619-669,6538-6550`).
- **Dominance:** every source-mapped counter is checked against its reservation; complete paths additionally require exact cache, lookup, and point-enumeration counts (`:6069-6203`). Successful phase closure requires both completed equality and dominance (`:6640-6682`).
- **Interrupted work:** relevant charges precede attempted hashes/enumerations; exception boundaries mark the receipt incomplete and retain already charged work (`:926-927,994-995,1012-1014,1121-1125,6508-6523,6962-6971`). Completed transcript equality is omitted after semantic failure.
- **Charge types:** `type(amount) is int and amount > 0` is enforced before state lookup or mutation, rejecting `bool`, float, zero, negative, string, and null (`:546-555`). The committed test checks all those cases without mutation (`tests/test_sgcp_embed_family.py:4053-4067`).

The synchronized-concurrency and nested callback tests compare complete reports against a serial baseline and verify restoration to no active state (`tests/test_sgcp_embed_family.py:4069-4150`). Partial cap, mid-function, graph, predicate, and enumeration interruption tests substantiate incomplete-work behavior (`:3004-3189,3349-3466`).

Path-only routing is identity-based: semantic entry requires both an active state and `state.path_permit is _PATH_VERIFICATION_PERMIT` (`src/verify_sgcp_embed_family.py:509-534`). Registered-curve, legacy-row, density-row, document-value, test-wrapper, and path-worker entry points are tested without a permit (`tests/test_sgcp_embed_family.py:4028-4051`).

This protects against ordinary API misuse and accidental direct semantic calls. It is not protection against a hostile same-process Python adversary able to introspect module globals, replace functions, manufacture state, or obtain the sentinel. That distinction is explicitly and correctly stated (`protocol-amendment-v12.json:26`; `handoff.md:18-21`).

# Publication audit

Output containment is lexical below the resolved development root (`src/verify_sgcp_embed_family.py:7016-7027`). Publication then:

1. Opens the development root with `O_DIRECTORY|O_NOFOLLOW`.
2. Traverses or creates each parent component relative to the current directory descriptor and reopens it with `O_NOFOLLOW` (`:7030-7061`).
3. Allocates an unpredictable same-directory temporary with `O_CREAT|O_EXCL|O_NOFOLLOW` (`:7143-7172`).
4. Writes fully, fsyncs, and verifies regular-file type and exact size (`:7174-7181`).
5. Publishes without replacement using:
   - macOS `renameatx_np(..., RENAME_EXCL)` (`:7073-7103`), or
   - same-directory hard link followed by temporary unlink (`:7105-7112`).
6. On `ENOTSUP`/`EOPNOTSUPP` only, removes the temporary and opens the final destination descriptor-relatively with `O_CREAT|O_EXCL|O_NOFOLLOW` (`:7183-7202`).
7. The fallback fully writes, fsyncs, and validates final inode size (`:7115-7140`).
8. Fsyncs the containing directory after successful publication (`:7203-7205`).
9. Closes descriptors and removes any still-unpublished temporary after failure (`:7206-7218`).

No path performs an overwrite. Existing destinations and destinations created between temporary creation and publication cause exclusive publication failure. Component substitution is contained by the already-open directory descriptors, while symlink components fail `O_NOFOLLOW`.

Interruption semantics are coherent:

- Before exclusive final open: no destination remains.
- During temporary write: the unpublished inode is cleaned up.
- During fallback final write: a partial final inode may remain, but it cannot be replaced by a later call.
- After publication but before successful return: the complete path exists but remains protocol-unaccepted; reuse still fails closed.

The committed test covers successful publication, preexisting destination, publication race, temporary cleanup, forced fallback interruption, second-call refusal, and parent symlink rejection (`tests/test_sgcp_embed_family.py:4152-4250`). It does not substantiate the claimed real-exFAT syscall observation identified above.

# Scope and claim audit

Schema constants route only candidate V12 and verification V12 (`src/verify_sgcp_embed_family.py:29-45`). V1 through V11 are enumerated as legacy schemas and rejected without row verification (`:6982-6989`).

Control scope is exact:

- One frozen `p=19,a=2,b=9,q=23,B=4`, least-x density row/document control is the only public density-row association admitted (`src/sgcp_embed_family.py:1463-1506`).
- Public generated-curve and legacy-row construction remain disabled (`:404-410,1311-1324`).
- Exactly three transient legacy semantic controls are constructed at `B=4,6,8`, with row count, zero density rows, and three row digests recorded in the in-test receipt (`tests/test_sgcp_embed_family.py:682-709,1099-1124`).
- Noncanonical `B` values reject before curve work (`:826-843`).
- Canonical and development execution entry points remain closed (`src/sgcp_embed_family.py:2123-2131`).
- The specification permits zero additional V12 curve rows and explicitly distinguishes the one B4 density control from the three legacy rows (`specification.json:112-118`).
- Budgets remain wall clock `0`, CPU `0`, memory `0`, and `maximum_runs=0` (`specification.json:199-204`; `protocol-amendment-v12.json:32-40`).
- No generated V12 curve-family density artifact, canonical matrix, runner, launch plan, or run appears in the committed tree.

The mathematical boundary is not widened: V12 changes verifier state, routing, charging, publication, and scope disclosure, while preserving curve grid, predicates, compiler, graph, objective, and gate (`protocol-amendment-v12.json:19-23`). The documents expressly disclaim relation generation, rank, linear algebra, descent, preprocessing crossover, rho improvement, exponent, deployment, and ECDLP results (`revision-response-v12.md:34-44`; `hypothesis.json:76-87`).

# Hash check

SHA-256 was recomputed over exact `HEAD:<path>` blob bytes. All nine values match `development-test-log-v12.md:17-27`.

| Artifact | Recomputed SHA-256 | Result |
|---|---|---|
| `src/sgcp_embed_family.py` | `a0287723c447b4db29eed495e80ea06fda03a21d90159c01dd96f26aa9f9380e` | Match |
| `src/verify_sgcp_embed_family.py` | `a203016c22f45fde84a245d611cac035cf62ddfd933cb6526621a195274207ad` | Match |
| `tests/test_sgcp_embed_family.py` | `454693a4cce435949b07b39b531c14efaab5e918733afdcbb90645ba365f4fcc` | Match |
| `hypothesis.json` | `fac5fb25b3d46afaee7290687f564205ea7d965fe74406bb9384f265c3bcbd82` | Match |
| `specification.json` | `98e2d5a78aeee8f9dc7c2497f4ecbbfa191cae61750832039ff21301d8596a51` | Match |
| `contract.md` | `49b44860fc63da06d15e605aab69ef55c11ae2db3baaf28e691ca7e53a990f94` | Match |
| `protocol-amendment-v12.json` | `dca7fef2dfa8aa0548a2084a3735369209d2e51e3a4217f7517637b7cc014858` | Match |
| `revision-response-v12.md` | `f30b442dde20fff87b8f5e200ec623eb816d633e564a31dd704e73edfe2f9af5` | Match |
| `source-self-review-v12.md` | `0850dafa892c084d10c917ad4cde47cd4084963001c5d1df00044ae51e4fc74e` | Match |

# Limitations

The clean detached worktree was confirmed at exact HEAD `9c170f70d6f4b7aafc20b5adfe70f22a702b5d8b`, with exact parent `0d5d541e344818fa84ec18279ced3c2b19324423`.

This review used committed blobs, static inspection, SHA-256 calculation, and an independent implementation of the fixed transcript arithmetic. It did not execute the producer, verifier, test suite, experiment, or recorded commands. Consequently:

- Recorded test success and repository-suite results were inspected, not reproduced.
- The claimed real-exFAT environment and `ENOTSUP` behavior were not independently established.
- Context isolation was audited for ordinary supported use, not hostile same-process mutation or introspection.
- CPU, wall time, RSS, allocator/parser memory, disk I/O, cache traffic, and memory bandwidth remain unmeasured.
- Launch-plan design readiness does not establish execution readiness or canonical B6/B8 feasibility.

# Handoff

```yaml
handoff:
  id: TASK-20260723-001
  from: accounting-reviewer
  to: coordinator
  objective: >
    Use the exact-commit V12 accounting review solely to decide whether a
    separate hash-complete launch-plan design may begin.
  inputs:
    - "HEAD 9c170f70d6f4b7aafc20b5adfe70f22a702b5d8b"
    - "parent 0d5d541e344818fa84ec18279ced3c2b19324423"
    - "completed vector 480/112/336/218/4218"
    - "nine matching committed-blob SHA-256 values"
  constraints:
    - "maximum_runs=0"
    - "Do not generate a curve-family density row or canonical matrix."
    - "Do not create or execute a runner or launch plan."
    - "Do not increase any budget."
    - "Do not make a mathematical, asymptotic, deployment, or ECDLP claim."
    - "Correct or qualify the unsupported real-exFAT wording."
  deliverables:
    - "A separately reviewed hash-complete launch-plan design, if all required reviewers issue scoped GO decisions."
    - "Explicit external hard-limit and resource-receipt requirements."
    - "Explicit fail-closed handling for any partial O_EXCL fallback destination."
  budget:
    wall_clock_seconds: 0
    memory_gb: 0
    maximum_runs: 0
  completion_gate:
    - "Fresh theory, accounting, and red-team GO decisions on the same committed bytes."
    - "Coordinator approval limited to plan design."
    - "No execution authority implied."
```

GO for launch-plan design only