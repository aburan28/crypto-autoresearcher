# Findings

No critical, high, medium, or low-severity launch-plan-design defects found in the exact committed V13 bytes.

Repository identity is correct:

- `HEAD`: `e44edde4231604abd76e481b7b4ed90359e42d09`
- Required parent: `4386d9722468fde9d963e1bc7e39fca7935463cb`
- Detached HEAD: confirmed
- Worktree: clean; `git status --porcelain=v1 --untracked-files=all` returned zero entries
- Files modified: none

# Independent accounting derivation

The derivation used the fixed domains, canonical JSON encoding, curve acceptance predicates, and canonical grid in [sgcp_embed_family.py](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py:278), not the development log.

The eight accepted transcripts were:

| bits | seed | accepted draw | accepted-prefix length | nonsingular draws | admissible roots | Möbius attempts |
|---:|---:|---:|---:|---:|---:|---:|
| 5 | 101 | 11 | 12 | 12 | 15 | 9 |
| 5 | 211 | 48 | 49 | 47 | 9 | 10 |
| 6 | 101 | 3 | 4 | 4 | 18 | 10 |
| 6 | 211 | 14 | 15 | 14 | 23 | 9 |
| 7 | 101 | 10 | 11 | 11 | 53 | 9 |
| 7 | 211 | 7 | 8 | 8 | 41 | 9 |
| 8 | 101 | 2 | 3 | 3 | 105 | 9 |
| 8 | 211 | 9 | 10 | 10 | 69 | 9 |

Therefore:

- Prime candidates: `2 × (16 + 32 + 64 + 128) = 480`.
- Accepted-prefix draws: `12+49+4+15+11+8+3+10 = 112`.
- Curve hashes: three domains per draw, `3 × 112 = 336`.
- Nonsingular enumeration count: each nonsingular draw is enumerated independently for rejection and then by the accepted/rejected bundle path, giving `2 × (12+47+4+14+11+8+3+10) = 218`.
- Möbius attempts: `74`; three hashes per attempt gives `222`.
- Null-root hashes: four replicates for each of three `B` values, hence `12 × (15+9+18+23+53+41+105+69) = 3,996`.
- Predicate hashes: `222 + 3,996 = 4,218`.

This matches the verifier’s transcript-derived equality rule at [verify_sgcp_embed_family.py:637](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:637).

# State lifecycle and work accounting

The lifecycle is sound for the stated ordinary-process boundary:

- Each public call creates fresh state containing actual work, reservation, registered-curve cache, owner thread, worker state, and closed flag ([lines 504–515](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:504)).
- The state is installed with a `ContextVar` token; `closed=True` is set before exact token restoration in a `finally` block ([lines 7048–7058](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7048)).
- Nested public calls install independent state and restore the exact outer token.
- Escaping exceptions still close and restore state.
- Copied-context cross-thread use fails the owner-thread check; post-close copied contexts fail the closed check ([lines 537–547](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:537)).
- Direct path-worker re-entry is rejected. The body additionally requires identity equality with the invocation’s worker token, which is cleared in `finally` ([lines 6854–6862](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:6854), [7030–7045](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7030)).
- Work charges reject Boolean, zero, negative, float, string, and null amounts before mutation by requiring `type(amount) is int and amount > 0` ([lines 560–570](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:560)).
- Reservation is state-owned and established before semantic rows ([lines 6492–6501](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:6492)).
- Completed graph/expansion and provenance/predicate paths require equality, not merely upper-bound dominance.
- Exceptions mark actual work incomplete while retaining already charged lower-bound work and the reservation.
- Validity requires complete work, reservation dominance, exact cache misses/entries and lookup counts, and exact point-enumeration counts ([lines 6087–6221](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:6087)).

# Publication state machine

The two-object protocol has the following states:

1. Neither object: absent.
2. Data incomplete or data complete without receipt: unaccepted orphan.
3. Receipt path exists but is partial or malformed: unaccepted invalid receipt.
4. Complete receipt with absent or mismatched payload: unaccepted receipt mismatch.
5. Canonical receipt plus matching payload snapshot: accepted.

For temporary-file publication, object data becomes complete after `_write_all`, file `fsync`, regular-file size confirmation, and close ([lines 7261–7267](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7261)). It becomes visible at the destination when exclusive rename succeeds or the hard link succeeds ([lines 7136–7159](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7136)).

For direct `O_EXCL` fallback, content is complete when `_write_all` finishes ([line 7182](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7182)). Later file-fsync, fstat, and close failures become warnings.

The receipt becomes the logical content commit when its exclusive rename/link succeeds or its direct `_write_all` completes. All real operations after that point are warning-only:

- Hard-link temporary cleanup is warning-only.
- Parent-directory fsync is warning-only.
- Direct file fsync, fstat, and close are warning-only.
- Output-parent close is warning-only.
- Receipt publication warnings are aggregated with data warnings and returned.

Rename success leaves no temporary cleanup. Hard-link success precedes cleanup and cannot be contradicted by cleanup failure. Forced `ENOTSUP` removes the unpublished temporary before attempting direct `O_EXCL`; partial direct data remains an orphan, while partial direct receipt remains invalid and neither is reusable. No post-receipt-commit cleanup, fsync, stat, or close path raises a contradictory publication failure ([lines 7229–7325](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7229), [7536–7584](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7536)).

# Receipt validator

The validator correctly enforces:

- Deterministic adjacent filename derived from the exact destination-name bytes ([lines 7328–7335](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7328)).
- Exact seven-key schema and exact field types.
- Canonical ASCII JSON plus one newline.
- Self-digest over the six non-self fields.
- Destination-name, experiment, and protocol binding.
- Payload byte length and SHA-256 binding.
- Descriptor-relative `O_NOFOLLOW` regular-file reads.
- Separate receipt and report byte ceilings.
- Stable `(device, inode, size, mtime_ns, ctime_ns)` identity across each snapshot.
- Distinct absent, path, orphan, invalid-receipt, receipt-mismatch, and accepted classifications ([lines 7338–7533](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7338)).
- No overwrite or reuse through exclusive destination creation/publication.
- Lexical containment below the development root and descriptor-walked no-follow output parents ([lines 7061–7108](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7061)).

# Scope and claim accounting

The committed records consistently preserve the required boundary:

- V13 accepts only its current schema; V1–V12 route to unsupported-legacy rejection without row verification ([lines 6970–7017](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:6970)).
- One frozen `p=19,a=2,b=9,q=23,B=4` density document is the sole density control.
- Exactly three transient, noncanonical frozen legacy controls exist at `B=4,6,8`.
- No generated V13 density row, matrix, runner, launch plan, or run is committed.
- A committed-tree search found zero V13 density-schema artifacts under the experiment’s development or run areas.
- `maximum_runs=0`, generated development rows `=0`, and `launch_plan_authorized=false` remain explicit ([protocol-amendment-v13.json:33](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/protocol-amendment-v13.json:33), [specification.json:206](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/specification.json:206)).
- The receipt excludes warnings; warnings exist only in the publication result.
- The receipt is correctly described as an unkeyed logical content record, not durability proof or authentication against a hostile same-user actor.
- CPU, wall time, RSS, disk, I/O, allocator, cache-traffic, and external artifact-store costs remain future runner obligations.
- Forced `ENOTSUP` is explicitly limited to fallback state-transition coverage and is not represented as a real exFAT observation ([protocol-amendment-v13.json:25](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/protocol-amendment-v13.json:25)).
- Claims remain toy-, model-, compiler-, and matrix-bound; no relation generation, rank, descent, rho, exponent, deployment, or ECDLP result is asserted ([hypothesis.json:76](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/hypothesis.json:76)).

# Hash check

All nine SHA-256 values in [development-test-log-v13.md:18](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/development-test-log-v13.md:18) match exact `HEAD` blobs:

| Artifact | Independently recomputed SHA-256 |
|---|---|
| `src/sgcp_embed_family.py` | `bdab1fe6766553438932ae938cf6b33b5a2c56f32d1caccceaacbc4d3a177122` |
| `src/verify_sgcp_embed_family.py` | `a12d733ceb0faed254452891d73da5f53db53833013977694eac913e463d94dc` |
| `tests/test_sgcp_embed_family.py` | `6700ee5d44377b759a7e32040fa5a46cac6414b249e53a15e9f53a5c742c79a9` |
| `hypothesis.json` | `0cc2466c4fe132ff9f52261d080fec4bb1c370b0aa501e6c618c74269eff147a` |
| `specification.json` | `2d2363d94c1b16ffa12e071af75a8ad666f44f68e25f74c0d4f3205be80b2ce6` |
| `contract.md` | `c23a5a7cea1d131ad57d1d4c68f41dece506cacf6081ee33e48b7cf0469319ea` |
| `protocol-amendment-v13.json` | `639a2a85e67c6157948287eef87f9b2db13fe932bc795bb40f11f10d48217628` |
| `revision-response-v13.md` | `21b4584b2bff5c9064051351e2a3e912085ed105b455ae0d33f26fa10c4f46da` |
| `source-self-review-v13.md` | `830ecf7838ff1c827319e9a3e8e9a0697dd9a819538f34087b2eed78297058f9` |

# Limitations

This was static committed-byte inspection plus independent read-only arithmetic. Per instruction, I did not execute the producer, verifier, focused tests, repository tests, record validation, or any experiment. Consequently, historical run/test observations in the development log were not treated as independently reproduced runtime evidence.

The approval is limited to designing a separately reviewed launch plan. It authorizes no generated rows, canonical matrix, runner, launch plan artifact, execution, resource budget, or ECDLP claim.

# Handoff

Accounting review of exact commit `e44edde4231604abd76e481b7b4ed90359e42d09` finds V13 ready for launch-plan design review only. Coordinator authority, separate theory and red-team decisions, a hash-complete plan, external resource containment, and a later explicit execution decision remain required. Preserve `maximum_runs=0`.

GO for launch-plan design only