# EXP-SGCP-EMBED-002 V16 Fresh Pre-Run Accounting and Evidence-Boundary Review

Artifact name: `pre-run-accounting-review-v16.md`

## Findings ordered by severity

1. **Critical — no finding exists.** No mathematical widening, canonical execution, generated curve-family density row, run artifact, budget increase, approval, or attack claim appears in the parent-to-HEAD delta. The contract remains explicitly toy/model-bound and excludes relation yield, rank, descent, preprocessing crossover, rho improvement, and ECDLP conclusions (`experiments/EXP-SGCP-EMBED-002/contract.md:626-631`; `experiments/EXP-SGCP-EMBED-002/hypothesis.json:77-88`).

2. **High — no finding exists.** No public first-party route was found that can produce a generated family row or launch an official run under the current state. Producer gates remain fail-closed (`src/sgcp_embed_family.py:404-410`, `1311-1324`, `1463-1506`, `2099-2102`, `2123-2131`), and the repository runner rejects `review_required` experiments before launch (`src/crypto_autoresearcher/runner.py:1423-1442`).

3. **Medium — no finding exists.** The V15 leading-`//`, stale-current-state, title, suite-scope, and raw-alias objections are all closed in V16. The only substantive executable delta is a narrower output-path admission policy; no curve, predicate, compiler, optimizer, gate, counter formula, reservation formula, or canonical grid changed.

4. **Low — no finding exists.** The nine logged hashes match exact Git bytes; static suite and record counts reconcile. Historical outcomes, timings, index identity, and the recorded single unrelated failure were not rerun and remain historical claims.

Residual resource and evidence limitations below are material launch-plan inputs, but they are disclosed limitations rather than defects in this no-run preflight.

## Outcome

`GO for separate launch-plan design only`

This outcome authorizes neither a generated curve-family density row nor execution. A launch would still require the remaining independent reviews, a separately reviewed hash-complete plan, hard external resource limits, coordinator approval, and nonzero budgets.

## Exact Git identity and review boundary

| Item | Exact value |
|---|---|
| Requested checkout | `/tmp/sgcp-v16-review-d8ea562` |
| Git-resolved root | `/private/tmp/sgcp-v16-review-d8ea562` |
| HEAD | `d8ea562f1890ef07fd48b2bfeef41289599575e9` |
| Parent | `d0a8ab5ad9f9385276ff061a520a0a07844f7bc5` |
| HEAD tree | `5e015c30df3aaae68aa9d6d830fea8c6221280c1` |
| Parent tree | `3c7c0a49cf1d9bf35503b89881f5cf9f166468f3` |
| Checkout state | Clean, detached `HEAD` |
| Commit subject | `Harden SGCP V16 POSIX path policy` |

The parent-to-HEAD diff changes 13 paths, with 783 insertions and 303 deletions. It adds the four V16 records, updates the contract/hypothesis/specification/handoff and ledgers, relabels producer/verifier schemas to V16, narrows path handling, and extends focused controls. It adds no path under `runs/` or `development/` and no raw result, manifest, execution plan, runner, or launch-plan artifact.

No producer, verifier, experiment, test, validator, indexer, or runner was executed. The only non-Git computation was a standalone, unpersisted SHA-256/arithmetic reconstruction that imported no repository module.

## V15 finding disposition

The V15 decision records the five relevant objections at `decision-v15.json:14-18`.

| V15 objection | V16 evidence | Disposition |
|---|---|---|
| Exactly two leading POSIX separators remain a distinct `//` anchor | Public admission rejects that anchor before normalization (`src/verify_sgcp_embed_family.py:7064-7082`); the descriptor walker independently repeats the rejection (`7085-7103`); the table control covers leading-double rejection (`tests/test_sgcp_embed_family.py:4701-4745`). | **Closed** |
| Current handoff/ledger/actions were stale | Handoff now requests exact-commit reviews (`handoff.md:70-74`); active ledger does the same (`research_ledger.md:29`); V16 log no longer requests validation/commit work (`development-test-log-v16.md:127-131`). | **Closed** |
| Contract title still said V14 | Title is V16 (`contract.md:1`), with a committed consistency assertion across amendment, specification, ledger, producer, verifier, and title (`tests/test_sgcp_embed_family.py:1228-1259`). | **Closed** |
| “Repository-wide suite” overstated unittest collection | The section is now explicitly “Repository-wide unittest-discover suite” and excludes the 27 module-level functions (`development-test-log-v16.md:89-105`). | **Closed** |
| Accepted-state attribution was not checked through the raw alias | Publication occurs through the raw combined alias (`tests/test_sgcp_embed_family.py:4648-4677`), followed by production and standalone attribution through every admitted spelling (`4683-4699`). | **Closed** |

The three V15 review hashes also independently match `independent-review-provenance-v15.json:16-37`:

| V15 review | Git-byte SHA-256 |
|---|---|
| Theory | `ade02d877d3aab98c292cadd7e626382bf69523c5df44ca4afe363b58c54dc60` |
| Accounting | `03c63432516b1734bc8365f9ab8155decf8a2483f09706428f5d92f630b529a6` |
| Red team | `6b8fb1e1fffb2896d645e12f58ad8b820fd3b9827cedbb251176f4b7dc28e2ab` |

Their static-review and shared-model limitations remain accurately recorded at `independent-review-provenance-v15.json:39-43`.

## Parent-to-HEAD mathematical and work-surface audit

The producer diff is nine additions and nine deletions, all V15-to-V16 schema, diagnostic, or protocol labels. Its curve generation, factor-base predicates, representative compiler, graph construction, optimizer, objective, and family-gate mathematics are unchanged.

The verifier diff consists of:

- routing V15 into the legacy-schema set and making V16 current (`src/verify_sgcp_embed_family.py:30-52`);
- mechanical V15-to-V16 function/diagnostic/schema renames;
- explicit leading-`//` rejection and independent normalized containment in `output_path` and `_open_output_parent` (`7064-7103`).

No accounting-counter set or formula changed. Completed graph/expansion formulas remain at `608-628`; completed provenance/predicate formulas remain at `640-677`; reservations remain at `5947-6087`; exact/dominance checks remain at `6090-6224`.

Therefore:

- **Mathematical surface:** unchanged.
- **Structural accounting surface:** unchanged.
- **Parser work surface:** unchanged apart from V16 labels.
- **Publication mechanism:** unchanged.
- **Path-admission surface:** intentionally narrowed to close the V15 anchor defect.
- **Authority surface:** unchanged at zero.

## Independent nine-hash audit

Hashes were recomputed by streaming `git show HEAD:<path>` bytes directly into SHA-256.

| Artifact | Logged SHA-256 | Independent result |
|---|---|---|
| `src/sgcp_embed_family.py` | `7af442bb69e06b2e36453353e100bb103086c8f791ce8a5434e1ffe54afa93d9` | Match |
| `src/verify_sgcp_embed_family.py` | `40eb3d503122ece701841004207f7f60311f5e0992baa0d450dd8fdd4cf5ae9f` | Match |
| `tests/test_sgcp_embed_family.py` | `0e4a368bd9a1be2634d94a98c582a07ae2a9416cfae5f214c132e4ac09b67383` | Match |
| `hypothesis.json` | `9a7600ce7bcbd02cfdf08be228bd498c07f94ea18239ba1926804171bcbe30d5` | Match |
| `specification.json` | `d298e18078a632d6b387d98d7057138fdbed0bb6ffbdbd1dca1c3d986a81cffa` | Match |
| `contract.md` | `4526ebcbb62b60d2a01718e185ab891b77a8702e37f74b3f4fb9116b0b9ecc33` | Match |
| `protocol-amendment-v16.json` | `30c63bc705a9bbf48c0a0d1a3c980eba8f54490bddf78bb8808b218f0d83bf3a` | Match |
| `revision-response-v16.md` | `34e4376ff11646e87620d9e75cbe6c90b1f0137d9d5d4267a7e99c330fb2bf73` | Match |
| `source-self-review-v16.md` | `d26932f93971bb03ea21cb31c2dd2541a449eda7e6b8f7197650269d739f7497` | Match |

The table agrees with `development-test-log-v16.md:21-31`.

The nine-file set does not hash the handoff, ledgers, or test log itself. Exact commit identity binds those bytes for this review, but the future launch plan must bind the complete governance and evidence surface.

## Independent provenance/predicate-vector reconstruction

A standalone implementation independently reproduced the SHA-256-derived curves, acceptance filters, admissible two-point fibers, and Möbius nondegeneracy attempts without importing repository producer or verifier code.

| Bits | Seed | Accepted draw, zero-based | Draws charged | Accepted `(p,a,b,q)` | Admissible roots | Nonsingular draws |
|---:|---:|---:|---:|---|---:|---:|
| 5 | 101 | 11 | 12 | `(29,4,28,31)` | 15 | 12 |
| 5 | 211 | 48 | 49 | `(23,2,17,19)` | 9 | 47 |
| 6 | 101 | 3 | 4 | `(47,17,20,37)` | 18 | 4 |
| 6 | 211 | 14 | 15 | `(43,35,37,47)` | 23 | 14 |
| 7 | 101 | 10 | 11 | `(89,69,72,107)` | 53 | 11 |
| 7 | 211 | 7 | 8 | `(89,36,83,83)` | 41 | 8 |
| 8 | 101 | 2 | 3 | `(199,55,163,211)` | 105 | 3 |
| 8 | 211 | 9 | 10 | `(131,58,79,139)` | 69 | 10 |

Derivation:

- Prime-interval candidates:
  `2 × (16 + 32 + 64 + 128) = 480`.
- Draws:
  `12 + 49 + 4 + 15 + 11 + 8 + 3 + 10 = 112`.
- Curve-coordinate hashes:
  `3 × 112 = 336`.
- Nonsingular draws:
  `12 + 47 + 4 + 14 + 11 + 8 + 3 + 10 = 109`.
- Registered-curve point enumerations:
  `2 × 109 = 218`.
- Admissible roots:
  `15 + 9 + 18 + 23 + 53 + 41 + 105 + 69 = 333`.
- There are 72 preregistered Möbius maps across eight curves, three `B` values, and three maps per curve-`B` combination. Independent nonce derivation required 74 total attempts.
- Möbius predicate hashes:
  `3 × 74 = 222`.
- Hash-null predicate hashes:
  `3 B values × 4 replicates × 333 roots = 3,996`.
- Total predicate hashes:
  `222 + 3,996 = 4,218`.

Thus the exact completed vector is:

```text
480 prime candidates
112 curve draws
336 curve hashes
218 registered-curve point enumerations
4218 predicate hashes
```

This agrees with the contract’s completed expectations (`contract.md:301-310`) and test-log claim (`development-test-log-v16.md:66-68`). It is a provenance/predicate invocation vector, not a field-operation, group-operation, CPU, memory, or end-to-end attack cost.

## Exact, reserved, and partial accounting

| Class | V16 treatment | Boundary |
|---|---|---|
| Completed provenance/predicate vector | Equality-derived from all verified public transcripts (`src/verify_sgcp_embed_family.py:640-688`). | Exact only after every row completes semantic reconstruction. |
| Completed graph candidate evaluations | Must equal the reconstructed candidate count (`614-627`). | Exact per completed row. |
| Completed eligible conflict checks | Must equal `binom(eligible_count,2)` (`614-627`). | Exact per completed row. |
| Completed pair-output cells | Must equal `eligible_count²` (`614-627`). | Exact per completed row. |
| Expansion cells | Must equal the degree 1/2/4/8 multiset total (`618-621`). | Exact per completed row. |
| Cache lookups/misses and point enumerations | Exact on complete paths through reservation equality checks (`6186-6223`). | Exact only for the listed dimensions. |
| Replay/proof nodes, cache insertions, retained-model calls/cells | Charged as observed and constrained by source-owned upper bounds (`5947-6087`, `6112-6175`). | Reservation-dominated; not all have independent completed equality. |
| Canonical JSON byte receipts | Recomputed from exact serialized objects (`5881-5898`). | Nested measures overlap and are nonadditive. |
| Raw charge type | `type(amount) is int` and `amount > 0` (`563-573`). | Boolean, zero, negative, float, string, and null are rejected before mutation. |
| Ordinary exceptions | Preserve already charged work, set `actual_work_complete=false`, retain reservation, and fail the unit/report (`6521-6552`). | Lower-bound partial accounting, not completed equality. |
| Process-level interruption | `KeyboardInterrupt`, `SystemExit`, termination, power loss, memory exhaustion, and hostile monkeypatching remain outside reconciliation (`contract.md:250-259`). | No totality claim. |
| Phase closure | Successful reports must match the exact ordered phase sequence and close every expected unit with zero failures (`6661-6703`). | Suppressed or incomplete units invalidate success. |

No accounting defect was found in these boundaries.

## Static test and record accounting

No test or validator was run. Counts were reconstructed from exact Git source structure.

| Claim | Independent static count | Evidence boundary |
|---|---:|---|
| Focused SGCP unittest methods | 81 | `tests/test_sgcp_embed_family.py` contains 81 class-level `test_*` methods and invokes `unittest.main()` at `5223-5224`. The recorded `OK` is historical (`development-test-log-v16.md:33-45`). |
| Repository unittest-discover methods | 225 | Exact class-level `test_*` method count across `tests/*.py`. The recorded 224-pass/one-failure outcome is historical (`development-test-log-v16.md:89-112`). |
| Excluded module-level pytest-style functions | 27 | 16 in `tests/test_outer_translator.py` and 11 in `tests/test_outer_translator_floor.py`; these are outside unittest discovery, as disclosed at `development-test-log-v16.md:103-105`. |
| Validator-selected records | 18 | Fifteen `decision-v1.json` through `decision-v15.json`, plus `research-question.json`, `hypothesis.json`, and `specification.json`. The selector is defined at `src/crypto_autoresearcher/records.py:184-209`. |
| Preserved unrelated failure | 1 | `tests/test_sgcp_embed.py:627-640` fails if committed `RUN-SGCP-EMBED-001` already exists; that immutable directory is present. The repository runner independently refuses an existing run ID at `src/crypto_autoresearcher/runner.py:1527-1529`. |

The recorded generated-index byte identity (`development-test-log-v16.md:83-87`) was not recomputed because running the indexer was prohibited. The current checked-in ledger entry is internally coherent at `ledger.json:127-132`.

## Budget and authority audit

| Authority or budget | Current value | Reference |
|---|---:|---|
| Experiment status | `review_required` | `specification.json:5-8`; `ledger.json:127-132` |
| `wall_clock_seconds_per_run` | `0` | `specification.json:208-212` |
| `total_cpu_hours` | `0` | `specification.json:208-212` |
| `maximum_memory_gb` | `0` | `specification.json:208-212` |
| `maximum_runs` | `0` | `specification.json:208-212`; `contract.md:613-620` |
| `approved_by` | `null` | `specification.json:367-368` |
| Launch-plan authorized | `false` | `protocol-amendment-v16.json:37-46` |
| Development rows consumed historically | `17` of `18` | `specification.json:112-116`; `contract.md:604-611` |
| Additional V16 development curve rows | `0` | `specification.json:112-116` |
| Generated curve-family density rows | `0` | `protocol-amendment-v16.json:38-43` |
| Canonical runs recorded | none | `ledger.json:127-132` |
| Proposed future per-role limits | `900 s`, `4 GiB` | `hypothesis.json:68-69`; proposals only, not active authority |

Route audit:

- `generated_curve` always raises before generated work (`src/sgcp_embed_family.py:404-410`).
- Public `build_legacy_row` always raises (`1311-1324`).
- Public `build_density_row` admits only exact frozen `p=19`, `B=4`, least-x control input (`1463-1506`).
- Development-document and producer CLI paths always raise (`2099-2102`, `2123-2131`).
- Direct verifier row APIs return invalid without mathematical work (`src/verify_sgcp_embed_family.py:2292-2297`, `5311-5328`).
- Internal semantic helpers require the invocation-local path permit and worker token (`540-550`, `7033-7061`).
- The official repository runner rejects `review_required` before launch and subsequently enforces positive budgets and maximum runs (`src/crypto_autoresearcher/runner.py:1423-1471`, `1538-1542`).

The public path verifier can inspect an externally supplied document, but it neither constructs a source row nor creates an official canonical run. A direct invocation lacks immutable runner, approval, run-directory, and coordinator evidence and therefore cannot satisfy the canonical launch gate.

**Conclusion:** no public first-party generated-row or official-run bypass was found.

## Parser, publication, and path boundaries

- Input admission opens the final component with nonblocking/no-follow flags, requires a regular file, checks the 256 MiB ceiling before allocation, fills one exact-size bytearray, hashes that same buffer, and checks stable identity and length (`src/verify_sgcp_embed_family.py:787-837`).
- Lexical ASCII/token/depth/string/scalar checks precede JSON object construction, and the bytearray is cleared during decoding (`700-784`).
- Source-sized collection checks and generic bounded traversal precede schema semantics (`6857-6960`).
- Exactly two leading separators are rejected; explicit `..` is rejected; dot and internal repeated separators normalize; three or more leading separators are host-normalized before containment (`7064-7103`).
- Output parents are opened descriptor-relative with `O_DIRECTORY|O_NOFOLLOW` (`7104-7131`).
- Receipt path, status, and writer all invoke path admission (`7366-7368`, `7604-7637`, `7654-7662`).
- The completion receipt binds protocol, experiment, random attempt identifier, destination, relative path, payload size/hash, and self-digest (`7430-7447`).
- Exact-attempt terminal reconciliation is implemented for ordinary post-receipt exceptions (`7697-7738`).
- Receipt and payload snapshots remain sequential rather than pair-atomic; the receipt is unkeyed and does not authenticate against a hostile same-user actor (`contract.md:261-268`).
- Input parent symlink traversal is allowed and disclosed; output parent symlinks are rejected. The standalone parser is not a filesystem-race oracle.

No path-policy or publication-boundary defect blocking plan design was found.

## Benchmark and scaling estimate

Let `r` denote the target prime-order subgroup and `B` the SGCP factor-base size.

| Comparator | Correct cost model | Memory/parallelism | V16 comparison |
|---|---|---|---|
| Pollard rho with negation and any available automorphism/endomorphism | Expected `Θ(√(r/|A|))` effective group operations when a valid automorphism quotient of size `|A|` is available | Small per worker | Strongest generic single-target baseline. V16 supplies no end-to-end DLP path or group-operation comparison. |
| van Oorschot–Wiener parallel collision search | Approximately `Θ(√r/W)` wall-time scaling for `W` effective workers, while aggregate work remains birthday-scale, adjusted for usable automorphisms | Distinguished-point storage, coordination, communication, and load balance must be charged | V16 has no parallel implementation or coordination model. |
| BSGS/MITM | `Θ(√r)` group operations | `Θ(√r)` stored group elements; time-memory tradeoffs apply | No equal-memory or equal-advice crossover is established. |
| Index-calculus/PDP components | Factor-base setup, relation probability and collection, matrix construction/rank, sparse linear algebra, individual logarithm, and target descent | Solver/matrix/storage/parallelism dependent | V16 reaches only a toy factor-base/embedding-support preflight. No relation system, rank, logarithms, linear algebra, or descent exists. |
| SGCP V16 | Fixed toy structural reconstruction plus exact combinatorial optimization | End-to-end CPU, memory, and bandwidth unmeasured | Not an attack and not comparable to rho/BSGS at an attack boundary. |

Canonical structural dimensions:

- Rows: `4 bit sizes × 2 seeds × 3 B values × 7 family/replicate choices = 168`.
- Cap cells: `168 × 4 = 672`.
- Degree-four candidate bound:
  `M(B)=binom(B+3,4)=35,126,330` for `B=4,6,8`.
- Aggregate candidate evaluations: `27,496`.
- Aggregate conflict-check reservation: `3,514,280`.
- Aggregate pair-output reservation: `7,056,056`.
- Aggregate degree-1/2/4/8 expansion cells: `473,928`.
- Replay-node ceiling: `672 × 2,000,000 = 1.344×10^9`.
- Independent-primary ceiling at the admitted five-million-node maximum:
  `672 × 5,000,000 = 3.36×10^9`.
- Derived aggregate metric-cache-entry reservation at that maximum:
  `9,464,535,808`.
- Derived retained-model-call reservation:
  `4,732,268,576`.
- Derived retained-model-cell reservation:
  `234,199,407,524,320`.

The last three are source-owned admission ceilings, not measured consumption or proof of feasibility.

Asymptotically:

- `M(B)=Θ(B^4)`.
- Candidate-pair and degree-eight surfaces are `Θ(B^8)`.
- Exact subset optimization is worst-case exponential in `Θ(B^4)` candidates.
- Registered prime-interval scanning is `Θ(2^n)` in the bit size `n`.
- Point enumeration is linear in `p` in these implementations, with substantial field work and storage.
- Four tiny bit sizes and fixed `B∈{4,6,8}` do not support a fitted cryptographic exponent (`hypothesis.json:77-83`).

## Hidden-cost audit

The following costs are unmeasured or only partially instrumented:

- **CPU and wall time:** producer, verifier, optimizer, canonicalization, parser, publication, and review overhead. The proposed 900-second role limit is unvalidated.
- **Group operations:** complete producer-plus-verifier EC additions, doublings, formal evaluations, pair sums, and replay/proof duplication.
- **Field operations:** modular additions, multiplications, squarings, inversions, exponentiations, point-enumeration work, primality tests, and Möbius scoring. Limited producer counters are not a complete end-to-end field-operation model.
- **Memory:** Python object overhead; point tables; representative, closure, conflict and pair-output structures; replay and primary caches; allocator retention; parser object graph; simultaneous buffer/object residency; peak RSS.
- **Memory bandwidth/cache traffic:** graph scans, cache lookups, canonicalization passes, and retained-model cell traffic.
- **Disk and storage:** canonical matrix bytes, temporary files, receipts, logs, external immutable-store capacity, replication, and retention.
- **I/O bandwidth:** filesystem reads/writes, immutable-store upload/download, synchronization, and role-to-role artifact transfer.
- **Parsing:** lexical scan, ASCII decoding, duplicate-key handling, object allocation, and diagnostics. A 256 MiB input ceiling is not a 256 MiB RSS ceiling.
- **Hashing:** the `336` and `4,218` counters count selected invocations, not input bytes or SHA-256 compression blocks. Row/document/nested digests, canonicalization, file hashing, receipt hashing, path-name hashing, and report hashing remain outside that vector.
- **Linear algebra and rank:** no relation matrix, density model, rank test, rank-failure probability, sparse elimination, Wiedemann/Lanczos cost, or matrix storage exists.
- **Relation collection:** no relation probability, collection throughput, duplicate handling, large-prime variant, or independence model exists.
- **Individual logarithms and descent:** absent.
- **Fixed-curve preprocessing:** no amortization model, advice lifetime, many-target analysis, or crossover against rho/BSGS exists.
- **Parallelism:** no worker model, communication cost, distinguished-point traffic, contention, scheduling, or aggregate-versus-wall normalization exists.
- **Durability/security:** no hostile same-user authentication, pair-atomic payload/receipt snapshot, executed-code attestation, or proof that every `fsync` succeeded.
- **B6/B8 feasibility:** serialized size, cache occupancy, runtime, and peak memory remain unmeasured; only frozen B4 has a structurally separate complete five-field oracle.

These omissions prevent any attack-performance claim, but they are appropriate inputs to a separate launch-plan design.

## Assumptions

- The review is confined to exact Git objects at `d8ea562f1890ef07fd48b2bfeef41289599575e9`.
- Historical V15 and V16 test, validator, index, and timing statements are records, not newly observed outcomes.
- Standard controlled macOS/POSIX and Python path semantics apply; no cross-platform claim is made.
- No hostile same-user filesystem mutation or hostile same-process monkeypatching is assumed.
- The standalone vector reconstruction followed the committed canonical-JSON and SHA-256 derivation rules but imported no repository module.
- Structural counts are interpreted as source-defined combinatorial units, not machine instructions or complete field/group-operation totals.
- All attack interpretations remain `TOY-EVIDENCE`, `MODEL-BOUND`, and `NOVELTY-UNVERIFIED`.

## Limitations

- This is an accounting/evidence-boundary review, not the required independent theory or red-team review.
- No runtime behavior, filesystem race behavior, test outcome, validator result, or index identity was re-executed.
- No canonical B6/B8 resource feasibility is established.
- No relation generation, rank, linear algebra, descent, preprocessing crossover, rho comparison, exponent, deployment relevance, or prime-field ECDLP result is established.
- The nine-file development hash set is not sufficient for a future launch; the separate plan must bind all governance, source, test, review, approval, environment, command, and external-resource artifacts.
- Exact-commit review does not attest to future executed bytes.

## Handoff: EXP-SGCP-EMBED-002 V16 accounting and evidence-boundary review

### Claim or task

Independently audit exact commit `d8ea562f1890ef07fd48b2bfeef41289599575e9` for V15 finding closure, completed/reserved/partial accounting correctness, zero execution authority, and readiness for separately governed launch-plan design.

### Status

`OBSERVATION`

No row, matrix, runner, plan, execution, budget increase, or attack claim is authorized by this review.

### Assumptions

- Exact clean detached Git bytes only.
- Controlled POSIX path semantics.
- Historical validation outcomes were inspected but not rerun.
- Structural counters are not complete runtime or cryptanalytic costs.
- Toy/model-bound claim limits remain mandatory.

### Evidence so far

- Exact HEAD, parent, and tree identities were confirmed.
- All nine V16 logged hashes match Git bytes.
- Independent reconstruction reproduced `480/112/336/218/4218`.
- Static counts reproduce 81 focused methods, 225 unittest methods, 27 excluded module-level functions, and 18 validator-selected records.
- Every V15 path/current-state/title/suite/raw-alias objection is closed.
- Mathematical and structural-accounting surfaces are unchanged.
- Active budgets remain zero, approval remains null, and the ledger contains no run.
- No public generated-row or official-run bypass was found.
- End-to-end attack costs remain absent and honestly excluded.

### Failure modes

- Treating structural cells or hash invocations as field/group operations or CPU.
- Treating historical test logs as fresh execution evidence.
- Treating the proposed 900-second/4-GiB role limits as demonstrated feasibility.
- Omitting parser, cache, memory-bandwidth, storage, or immutable-publication costs.
- Advancing without hash-binding the complete governance and execution surface.
- Interpreting a future toy family-gate result as relation generation, rank, descent, rho improvement, or an ECDLP break.

### Next concrete action

Obtain independent theory and red-team reviews of this exact commit; only after all three scoped reviews agree should a separate hash-complete launch-plan design specify immutable roles, hard external CPU/RSS/storage/bandwidth limits, fail-closed publication, and zero execution until a later coordinator approval changes the budgets.

### Artifact paths

- `experiments/EXP-SGCP-EMBED-002/pre-run-accounting-review-v16.md`
- `experiments/EXP-SGCP-EMBED-002/contract.md`
- `experiments/EXP-SGCP-EMBED-002/hypothesis.json`
- `experiments/EXP-SGCP-EMBED-002/specification.json`
- `experiments/EXP-SGCP-EMBED-002/protocol-amendment-v16.json`
- `experiments/EXP-SGCP-EMBED-002/revision-response-v16.md`
- `experiments/EXP-SGCP-EMBED-002/source-self-review-v16.md`
- `experiments/EXP-SGCP-EMBED-002/development-test-log-v16.md`
- `experiments/EXP-SGCP-EMBED-002/handoff.md`
- `experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `tests/test_sgcp_embed_family.py`
- `research_ledger.md`
- `ledger.json`
