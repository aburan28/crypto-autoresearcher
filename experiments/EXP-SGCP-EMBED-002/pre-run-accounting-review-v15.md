Verdict: `REVISE`.

Commit `8adba3ad4ddf7055cc098831dff2a33e1e469810` is clean, detached, and has the requested parent `232db54d54257afde467d6680552fed048dc7440`. The nine hashes, five-counter accounting vector, V1–V14 routing, path-containment implementation, record count, artifact inventory within the stated repair scope, and zero execution authority all check out. No producer, verifier, validator, test, experiment, row, plan, or runner was executed or created.

## Findings, ordered by severity

1. **Medium — the V15 current-state repair remains stale and contradicts its own committed evidence.**

   The active handoff still instructs the coordinator to complete validation, freeze hashes, and commit V15 ([handoff.md:71](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/handoff.md:71)). The active ledger likewise says V15 is “under validation” and its next action is “Validate and commit” ([research_ledger.md:29](/private/tmp/sgcp-v15-review-8adba3a/research_ledger.md:29)).

   Those statements conflict with the same commit’s log of completed focused validation, 17-record validation, index comparison, repository unittest run, and frozen hashes ([development-test-log-v15.md:39](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/development-test-log-v15.md:39), [development-test-log-v15.md:71](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/development-test-log-v15.md:71), [development-test-log-v15.md:77](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/development-test-log-v15.md:77)). The revision response also says fresh exact-commit review is now the next action, but later repeats “Validate and commit” first ([revision-response-v15.md:62](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/revision-response-v15.md:62), [revision-response-v15.md:84](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/revision-response-v15.md:84)).

   This does not widen execution authority, but it means one of V15’s three primary repair objectives is not durably complete.

2. **Low — “repository-wide suite” overstates the committed test scope.**

   The recorded command is `unittest discover`, not an all-framework repository suite ([development-test-log-v15.md:83](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/development-test-log-v15.md:83)). Static counting confirms exactly 225 `unittest.TestCase` methods and 81 focused SGCP methods, so those counts are coherent. However, 27 module-level pytest-style tests are not collected by that command, including [test_outer_translator_floor.py:101](/private/tmp/sgcp-v15-review-8adba3a/tests/test_outer_translator_floor.py:101) and [test_outer_translator.py:62](/private/tmp/sgcp-v15-review-8adba3a/tests/test_outer_translator.py:62).

   Therefore, “224 of 225 unittest methods passed historically” is the proper boundary. The observed runtimes and pass/failure outcomes remain committed historical claims; they were not rerun in this review.

3. **Low — accepted-state normalized-alias control is slightly narrower than its strongest wording.**

   The test passes the raw alias to `output_path`, `publication_receipt_path`, pre-publication `publication_status`, and the writer ([test_sgcp_embed_family.py:4609](/private/tmp/sgcp-v15-review-8adba3a/tests/test_sgcp_embed_family.py:4609)). After publication, however, production and standalone attribution are checked using the normalized path, not the raw alias ([test_sgcp_embed_family.py:4632](/private/tmp/sgcp-v15-review-8adba3a/tests/test_sgcp_embed_family.py:4632)). This is narrower than the combined accepted-pair control language in [specification.json:172](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/specification.json:172).

   Static source inspection shows that `publication_status(raw_alias)` would follow the same normalized path, so no implementation escape was found. A direct post-publication raw-alias assertion is still needed to close the evidence gap.

## Exact SHA-256 audit

All nine logged values match exact Git blob bytes:

| Artifact | SHA-256 | Result |
|---|---|---|
| Producer | `45997a75438a477a4503944fb130f4ee079ae72be50fffae48ab20426a3ed6e3` | Match |
| Verifier | `0c3338234fd182ec08952005259f22f0184d540c35bc4a492c388bcfb215a023` | Match |
| Focused tests | `0a330ef3decd637fc9ae7d7e8ccd3909e8cf9d65fbb2b003d1d53b1ae913530f` | Match |
| Hypothesis | `97f5f8461e8e674df455886590a404aec0126494bf2e0c399b4dbda8ab72c95f` | Match |
| Specification | `7d9549c7984ab3aaf947465f9609228dc2f9546d21f8896a9b176986ca23d9f5` | Match |
| Contract | `1a72ce64a8cfd206ba9e17f3827282376f9256d64c4e1b88ea9bdcfda9d19d64` | Match |
| V15 amendment | `042d112fbb1825d0c0bb71a3139dac8cd89614c6215f23bd0b6a8adcd6327ba2` | Match |
| V15 revision response | `a402d76241294852332ea3d939d114d2c5f47e0829c7c0c1a8426ef4a36bee43` | Match |
| V15 self-review | `f6bdcd7723f26f30c628ebcab5f450d92cb6f4b59a8d67d065a6da91df5066d2` | Match |

The nine-file set does not include the active handoff, either ledger, or the test log itself. The exact Git commit currently binds those bytes, but a later “hash-complete” launch-plan review must bind the complete governance and evidence surface, not only these nine files.

## Operation-vector reconstruction

A standalone deterministic reimplementation, importing no repository producer or verifier code, reproduced the eight accepted transcripts and the vector:

- Accepted-prefix draws: `12+49+4+15+11+8+3+10 = 112`.
- Prime candidates: `2 × (16+32+64+128) = 480`.
- Curve hashes: `3 × 112 = 336`.
- Nonsingular draws: `12+47+4+14+11+8+3+10 = 109`; each is enumerated twice, giving `218`.
- Admissible-root counts: `15,9,18,23,53,41,105,69`.
- Möbius attempts: `9,10,10,9,9,9,9,9`, totalling `74`.
- Predicate hashes: `3×74 + 12×333 = 222+3996 = 4218`.

The source charging rule agrees: transcript-derived expectations are defined at [verify_sgcp_embed_family.py:639](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:639), curve charges at [verify_sgcp_embed_family.py:1004](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:1004), and predicate charges at [verify_sgcp_embed_family.py:1136](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:1136).

This is an exact five-counter provenance/predicate vector, not group operations, field operations, CPU work, memory, or end-to-end attack cost.

## Schema, path, inventory, and authority audit

- Producer emits V15 and retains hard construction gates ([sgcp_embed_family.py:25](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py:25), [sgcp_embed_family.py:404](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py:404), [sgcp_embed_family.py:1502](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py:1502)).
- Verifier enumerates V1–V14 as legacy and V15 as current ([verify_sgcp_embed_family.py:30](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:30)). Legacy schemas return with no row reports or mathematical checks ([verify_sgcp_embed_family.py:6972](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:6972)).
- `output_path` retains explicit `..` long enough to reject it, normalizes `.` and repeated separators, enforces lexical containment, and rejects the root itself ([verify_sgcp_embed_family.py:7063](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7063)).
- The descriptor walker repeats `..` rejection and opens each normalized parent with `O_DIRECTORY|O_NOFOLLOW` from the resolved development root ([verify_sgcp_embed_family.py:7080](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7080)).
- Receipt path, status, and writer all invoke admission internally ([verify_sgcp_embed_family.py:7350](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7350), [verify_sgcp_embed_family.py:7588](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7588), [verify_sgcp_embed_family.py:7638](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7638)). No normalized-alias or parent-symlink escape was found.
- Static record selection is exactly 17 records: research question, hypothesis, specification, and decisions V1–V14. The committed ledger has version 15, `review_required`, and `runs: []` ([ledger.json:126](/private/tmp/sgcp-v15-review-8adba3a/ledger.json:126)).
- The four V7 records and complete V14 review/provenance/decision set are present in the durable ledger ([research_ledger.md:224](/private/tmp/sgcp-v15-review-8adba3a/research_ledger.md:224), [research_ledger.md:285](/private/tmp/sgcp-v15-review-8adba3a/research_ledger.md:285)).
- Active canonical budgets are exactly zero for runs, wall time, CPU, and memory ([specification.json:208](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/specification.json:208)); `approved_by` remains null ([specification.json:358](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/specification.json:358)); and launch-plan authority is false ([protocol-amendment-v15.json:35](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/protocol-amendment-v15.json:35)). The `900s/4GB` values are only proposed future per-role ceilings ([hypothesis.json:68](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/hypothesis.json:68)).

## Benchmark and scaling estimate

| Comparator | Time | Memory | Current comparison |
|---|---:|---:|---|
| Pollard rho with negation and any available automorphism/endomorphism; van Oorschot–Wiener for parallel search | `Θ(√q)` expected aggregate group operations | Small per worker plus distinguished-point coordination | Strongest general baseline; V15 has no end-to-end DLP cost to compare |
| BSGS/MITM | `Θ(√q)` group operations | `Θ(√q)` group elements | Relevant time-memory baseline; no crossover evidence |
| Semaev/Gröbner/SAT/crossbred or index calculus | Requires an instantiated relation system, collection model, matrix, and descent | Solver- and matrix-dependent | Not instantiated here |
| SGCP V15 | Structural toy preflight only | Unmeasured end-to-end | Relation collection, rank, linear algebra, and target descent absent |

For the frozen canonical grid:

- `168` rows and `672` cap cells.
- Degree-four candidate bound `M=binom(B+3,4)`, hence `M=35,126,330` for `B=4,6,8`.
- Registered-envelope totals include 27,496 candidate evaluations, 3,514,280 conflict-check upper-bound cells, 7,056,056 pair-output upper-bound cells, and 473,928 expansion cells.
- Replay ceiling: `672×2,000,000 = 1.344×10^9` nodes.
- Independent-primary ceiling: `672×5,000,000 = 3.36×10^9` nodes.

The structural graph and degree-eight surfaces scale as `O(B^8)`; exact subset optimization remains exponential in `Θ(B^4)` candidates in the worst case. Curve registration scans a full `n`-bit interval and point enumeration is linear in `p`, so those toy setup paths scale as `Θ(2^n)` time and substantial `Θ(2^n)` storage. These are ceilings and asymptotic drivers, not observed V15 runtime.

## Hidden-cost audit

Correctly disclosed but unmeasured:

- Producer and verifier CPU, wall time, peak RSS, parser/allocator retention, disk I/O, cache traffic, and memory bandwidth ([contract.md:384](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/contract.md:384)).
- Prime-list construction, primality-test cost, point-enumeration field work, SHA-256 byte/compression work, sorting, and Python object overhead.
- Optimizer, replay, proof, and cache memory at the billion-node aggregate ceilings.
- Canonical serialized size, repeated canonicalization/hash traffic, 256-MiB input-limit feasibility, and external artifact-store capacity.
- External-store upload/download bandwidth, retention, replication, and storage durability receipts.
- Offline preflight tests and review work: the zero canonical budget does not mean those development activities consumed zero resources.
- Relation collection, sparse linear algebra, rank failure, individual logarithms, and target descent. Until these exist, no rho/BSGS or index-calculus win is defined.

## Handoff: EXP-SGCP-EMBED-002 V15 accounting and evidence-boundary review

### Claim or task

Independent read-only review of exact commit `8adba3ad4ddf7055cc098831dff2a33e1e469810` against parent `232db54d54257afde467d6680552fed048dc7440`.

### Status

`REVISE`

No execution, row, matrix, runner, plan, or budget authority is granted.

### Assumptions

- Standard `pathlib` and descriptor-relative POSIX behavior.
- Controlled workspace without hostile same-user or same-process mutation.
- Historical test, validator, index, and timing results were inspected but not rerun.
- The five-counter vector is prospective completed canonical-transcript accounting, not an observed canonical run.

### Evidence so far

- Clean detached exact commit and parent confirmed.
- All nine V15 SHA-256 values match exact Git bytes.
- Independent deterministic reconstruction reproduced `480/112/336/218/4218`.
- V1–V14 routing, normalized-alias semantics, explicit parent rejection, descriptor traversal, inventory repair, and zero budgets are statically coherent.
- No generated V15 row, canonical matrix, launch plan, runner, or run artifact exists.

### Failure modes

- Active handoff and research ledger remain stale after the recorded V15 validation and commit.
- “Repository-wide” describes only the unittest-discover scope and excludes 27 pytest-style functions.
- Accepted-state status attribution was not directly exercised through the raw alias.
- End-to-end runtime, memory, storage, bandwidth, relation, rank, linear-algebra, and descent costs remain absent.

### Next concrete action

Create one no-run successor that updates the active handoff and research ledger to the exact committed/reviewed state, narrows the suite wording to its actual unittest scope, and adds a post-publication raw-alias status/standalone-attribution control. Preserve every zero budget and obtain fresh exact-commit review before any launch-plan design.

### Artifact paths

- [V15 test log](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/development-test-log-v15.md:1)
- [V15 handoff](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/handoff.md:1)
- [V15 specification](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/specification.json:1)
- [Verifier](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:1)
- [Focused tests](/private/tmp/sgcp-v15-review-8adba3a/tests/test_sgcp_embed_family.py:1)
- [Research ledger](/private/tmp/sgcp-v15-review-8adba3a/research_ledger.md:24)
- [V14 decision](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/decision-v14.json:1)

`REVISE`
