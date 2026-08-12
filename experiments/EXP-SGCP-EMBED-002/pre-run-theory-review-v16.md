# EXP-SGCP-EMBED-002 V16 Independent Pre-Run Theory Review

## Findings, ordered by severity

**Critical:** No finding exists.

**High:** No finding exists.

**Medium:** No finding exists.

**Low:** No finding exists.

The V15 blockers are closed at the reviewed commit:

1. **POSIX path-policy mismatch — closed.** Exact `//` anchors and explicit `..` components reject before absolute normalization; internal repeated separators and dot components are aliases; three or more leading separators collapse to `/` on the controlled POSIX runtime; normalized root and outside paths reject ([contract.md:226](/tmp/sgcp-v16-review-d8ea562/experiments/EXP-SGCP-EMBED-002/contract.md:226), [verifier:7064](/tmp/sgcp-v16-review-d8ea562/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7064), [tests:4640](/tmp/sgcp-v16-review-d8ea562/tests/test_sgcp_embed_family.py:4640)).

2. **Raw-alias attribution gap — closed.** Publication uses the combined raw alias, and production plus standalone status attribution is checked through every admitted spelling after publication ([tests:4675](/tmp/sgcp-v16-review-d8ea562/tests/test_sgcp_embed_family.py:4675)).

3. **Stale current-state records — closed.** The live handoff and active research-ledger row identify V16 as awaiting exact-commit review and prohibit launch-plan design or execution meanwhile ([handoff.md:1](/tmp/sgcp-v16-review-d8ea562/experiments/EXP-SGCP-EMBED-002/handoff.md:1), [research_ledger.md:29](/tmp/sgcp-v16-review-d8ea562/research_ledger.md:29)).

4. **Stale contract version — closed.** Contract, specification, ledger, producer, and verifier all identify version 16 ([contract.md:1](/tmp/sgcp-v16-review-d8ea562/experiments/EXP-SGCP-EMBED-002/contract.md:1), [specification.json:5](/tmp/sgcp-v16-review-d8ea562/experiments/EXP-SGCP-EMBED-002/specification.json:5), [ledger.json:127](/tmp/sgcp-v16-review-d8ea562/ledger.json:127), [producer:25](/tmp/sgcp-v16-review-d8ea562/experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py:25), [verifier:47](/tmp/sgcp-v16-review-d8ea562/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:47)).

5. **Test-scope overstatement — closed.** The log now says “repository-wide unittest-discover suite,” records its one failure, and explicitly excludes module-level pytest-style functions ([development-test-log-v16.md:89](/tmp/sgcp-v16-review-d8ea562/experiments/EXP-SGCP-EMBED-002/development-test-log-v16.md:89)).

## Outcome

`GO for separate launch-plan design only`

This is one theory-review outcome. It does not itself authorize launch-plan design, a generated row, a canonical matrix, a runner, execution, or any budget increase. The separately required accounting and red-team outcomes and coordinator decision remain outstanding.

## Exact-commit identity

- Requested and observed HEAD: `d8ea562f1890ef07fd48b2bfeef41289599575e9`
- Parent: `d0a8ab5ad9f9385276ff061a520a0a07844f7bc5`
- Tree: `5e015c30df3aaae68aa9d6d830fea8c6221280c1`
- Checkout: `/tmp/sgcp-v16-review-d8ea562`, resolving to `/private/tmp/sgcp-v16-review-d8ea562`
- State before and after review: detached and clean
- Review operations: static inspection and read-only Git/hash commands only
- Not run: producer, verifier, experiment, tests, record validator, index generator, or runner
- Created or modified: nothing

The V15 provenance accurately binds three separate review artifacts to `8adba3ad4ddf7055cc098831dff2a33e1e469810`; their recorded hashes also match the current Git blobs ([independent-review-provenance-v15.json:2](/tmp/sgcp-v16-review-d8ea562/experiments/EXP-SGCP-EMBED-002/independent-review-provenance-v15.json:2)). Decision `DEC-SGCP-EMBED-002-015` records unanimous revision and the exact V16 repair requirements ([decision-v15.json:3](/tmp/sgcp-v16-review-d8ea562/experiments/EXP-SGCP-EMBED-002/decision-v15.json:3)).

## Independent nine-hash verification

Each digest was recomputed from `git show d8ea562f1890ef07fd48b2bfeef41289599575e9:<path>` bytes. All nine match [development-test-log-v16.md:21](/tmp/sgcp-v16-review-d8ea562/experiments/EXP-SGCP-EMBED-002/development-test-log-v16.md:21).

| Artifact | Recomputed SHA-256 | Result |
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

## Theory-question determinations

### 1. POSIX path-policy exactness

**No finding.** The claim is exact within the controlled Python/POSIX model:

- Exactly two leading separators survive as the distinct `//` anchor and are rejected using `Path.anchor` before `abspath` ([verifier:7064](/tmp/sgcp-v16-review-d8ea562/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7064)).
- Dot components and internal repeated separators are normalized aliases.
- Three or more leading separators collapse to the ordinary `/` anchor and then undergo containment.
- Explicit `..` remains visible in `Path.parts` and rejects before normalization.
- The development root itself and normalized outside paths reject; absolute in-root paths are admitted.
- The descriptor walker repeats anchor, traversal, root, and containment checks and opens each parent with `O_DIRECTORY|O_NOFOLLOW` ([verifier:7085](/tmp/sgcp-v16-review-d8ea562/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7085)).
- A symlinked output parent may pass lexical admission but fails production writer/status descriptor traversal. The standalone parser is expressly outside that filesystem-race claim ([contract.md:563](/tmp/sgcp-v16-review-d8ea562/experiments/EXP-SGCP-EMBED-002/contract.md:563), [tests:4574](/tmp/sgcp-v16-review-d8ea562/tests/test_sgcp_embed_family.py:4574)).

The tests exercise exactly three leading separators rather than every possible count. Static source semantics nevertheless cover every count of at least three; this remains runtime-sensitive and must be repinned if the runtime or path flavor changes.

### 2. Agreement among source, tests, contract, specification, and governance

**No finding.** The records agree on:

- V16 schema and protocol;
- the exact path policy;
- frozen-only public density-row construction;
- V1–V15 rejection;
- the current `review_required` state;
- zero generated V16 rows and zero runs;
- `maximum_runs=0`;
- no launch authority.

The active ledger has `runs: []`, `status: review_required`, and version 16 ([ledger.json:127](/tmp/sgcp-v16-review-d8ea562/ledger.json:127)). The durable inventories include all V15 reviews, provenance, decision, and the four V16 records ([specification.json:345](/tmp/sgcp-v16-review-d8ea562/experiments/EXP-SGCP-EMBED-002/specification.json:345), [research_ledger.md:295](/tmp/sgcp-v16-review-d8ea562/research_ledger.md:295)).

### 3. Mathematical, objective, gate, accounting, or budget changes

**No finding.** The exact parent-to-HEAD diff changes protocol labels, path-policy implementation, controls, and governance records only.

Unchanged objects include:

- curve grid `bits={5,6,7,8}`, seeds `{101,211}`, and `B={4,6,8}`;
- three coordinate families and four hash-null replicates;
- factor-base fiber rule;
- representative compiler `lexicographically_least_formal_per_nonidentity_2F_output_v2`;
- ordering digest `8114bd7d…12359`;
- candidate/conflict graph;
- four caps;
- five-field lexicographic objective;
- family-gate thresholds and negative classification;
- completed provenance/predicate vector `480/112/336/218/4218`;
- all canonical and development-row budgets.

These are frozen in [hypothesis.json:37](/tmp/sgcp-v16-review-d8ea562/experiments/EXP-SGCP-EMBED-002/hypothesis.json:37), [specification.json:9](/tmp/sgcp-v16-review-d8ea562/experiments/EXP-SGCP-EMBED-002/specification.json:9), and [protocol-amendment-v16.json:20](/tmp/sgcp-v16-review-d8ea562/experiments/EXP-SGCP-EMBED-002/protocol-amendment-v16.json:20).

### 4. V1–V15 legacy routing

**No finding.** All fifteen schema strings are present in `LEGACY_SCHEMAS` ([verifier:30](/tmp/sgcp-v16-review-d8ea562/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:30)). The routing branch returns an unsupported-legacy receipt with zero row reports and no mathematical checks ([verifier:6973](/tmp/sgcp-v16-review-d8ea562/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:6973)).

Bounded parsing and source-shape checks occur before routing, but no curve, graph, replay, proof, or row semantics occur. The control relabels a valid V16 body under every legacy schema and requires zero rows and no graph checks ([tests:3782](/tmp/sgcp-v16-review-d8ea562/tests/test_sgcp_embed_family.py:3782)).

### 5. Current-state, version, and test-scope truth

**No finding.**

Static counts independently confirm:

- 81 focused `unittest.TestCase` methods;
- 225 repository `unittest.TestCase` methods;
- 27 module-level pytest-style functions;
- 18 validator-selected records: 15 decisions plus research question, hypothesis, and specification.

The historical outcomes were not rerun in this review. Their exact scope is correctly reported: focused `81/81`; record validation `18`; index comparison reported equal; repository unittest discovery `225` with one preserved unrelated immutable-run-guard failure and 224 passing ([development-test-log-v16.md:33](/tmp/sgcp-v16-review-d8ea562/experiments/EXP-SGCP-EMBED-002/development-test-log-v16.md:33), [development-test-log-v16.md:70](/tmp/sgcp-v16-review-d8ea562/experiments/EXP-SGCP-EMBED-002/development-test-log-v16.md:70), [development-test-log-v16.md:89](/tmp/sgcp-v16-review-d8ea562/experiments/EXP-SGCP-EMBED-002/development-test-log-v16.md:89)).

### 6. Route around `maximum_runs=0`

**No authorized or public first-party route was found.**

- `generated_curve` raises before generated-curve work ([producer:404](/tmp/sgcp-v16-review-d8ea562/experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py:404)).
- `build_legacy_row` raises ([producer:1311](/tmp/sgcp-v16-review-d8ea562/experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py:1311)).
- `build_density_row` admits only exact frozen `p=19`, `B=4` ([producer:1463](/tmp/sgcp-v16-review-d8ea562/experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py:1463)).
- Development-document and canonical CLI paths raise ([producer:2099](/tmp/sgcp-v16-review-d8ea562/experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py:2099), [producer:2123](/tmp/sgcp-v16-review-d8ea562/experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py:2123)).
- The tree contains no V16 density row, canonical matrix, runner, launch plan, or run artifact.
- Budgets remain zero and approval remains null ([specification.json:208](/tmp/sgcp-v16-review-d8ea562/experiments/EXP-SGCP-EMBED-002/specification.json:208), [specification.json:367](/tmp/sgcp-v16-review-d8ea562/experiments/EXP-SGCP-EMBED-002/specification.json:367)).

Arbitrary Python introspection, monkeypatching, manual assembly from low-level helpers, or submission of an externally constructed canonical document lies outside the governance and same-process threat model. The verifier can inspect a supplied canonical document; that is not generation or launch authority.

### 7. ECDLP or launch-authority overclaim

**No finding.**

The records consistently classify the candidate as `HYPOTHESIS`, `TOY-EVIDENCE`, `MODEL-BOUND`, and `NOVELTY-UNVERIFIED` ([hypothesis.json:7](/tmp/sgcp-v16-review-d8ea562/experiments/EXP-SGCP-EMBED-002/hypothesis.json:7)). They exclude relation generation, rank, linear algebra, target descent, preprocessing crossover, rho improvement, exponent, deployment, and prime-field ECDLP conclusions ([contract.md:626](/tmp/sgcp-v16-review-d8ea562/experiments/EXP-SGCP-EMBED-002/contract.md:626)).

This complies with the governing constitution’s separation of toy, structured-generic, heuristic, and attack-level claims ([AGENTS.md:54](/Volumes/Volume/autolab/AGENTS.md:54), [AGENTS.md:205](/Volumes/Volume/autolab/AGENTS.md:205)) and the exact checkout’s rules against overinterpreting toy evidence ([tracked AGENTS.md:15](/tmp/sgcp-v16-review-d8ea562/AGENTS.md:15)).

## Assumptions and model boundaries

- **Path model:** Python `pathlib.Path` and `os.path.abspath` under the controlled POSIX path flavor.
- **Filesystem model:** controlled workspace; no hostile same-user mutation or hostile same-process monkeypatching.
- **Publication model:** sequential payload/receipt snapshots, unkeyed receipts, and ordinary synchronous `Exception` reconciliation only.
- **Cryptanalytic model:** finite structured-generic embedding probe on generated 5–8-bit prime-order curves with fixed `B`.
- **Evidence model:** static exact-commit inspection plus Git-object hash verification. Historical tests were inspected, not rerun.
- **Not proved:** no generic-group lower bound, structured-generic class-wide lower bound, algebraic lower bound, smoothness estimate, Semaev degree-growth claim, relation-generation theorem, rank theorem, descent theorem, or attack complexity theorem.
- **Outside all current claims:** alternative compilers, formal quotients, model transformations, source-recoverable non-tree operations, other coordinate families, cryptographic scaling, and non-generic attacks.

## Counterexample and model-escape routes

- A complete valid exact matrix in which every fixed family-cap pair fails is the scoped counterexample to the empirical hypothesis. It does not refute coordinate-specific embeddings generally ([contract.md:587](/tmp/sgcp-v16-review-d8ea562/experiments/EXP-SGCP-EMBED-002/contract.md:587)).
- The narrower `COLLAPSE` result requires every family to fall below the strict `1/10` persistence boundary in at least three strata.
- Missing rows, unresolved optima, resource exhaustion, malformed types, failed controls, or verifier disagreement remain `INCONCLUSIVE`.
- The path-policy counterexample route is a different runtime/path flavor or a spelling whose Python anchor/parts behavior differs from the controlled POSIX model.
- Mathematical model escapes remain another compiler, quotient, transformation, or source-recoverable non-tree operation ([contract.md:599](/tmp/sgcp-v16-review-d8ea562/experiments/EXP-SGCP-EMBED-002/contract.md:599)).
- Attack relevance still requires relation generation, factor-base logarithms, matrix rank, linear algebra, individual logarithms, target descent, and a fully charged comparison with rho/BSGS.

## Handoff: EXP-SGCP-EMBED-002 V16 theory review

### Claim or task

Independent read-only theory review of exact commit `d8ea562f1890ef07fd48b2bfeef41289599575e9` against the unanimous V15 revision findings and governing research constitutions.

### Status

`OBSERVATION`

No V16 theory blocker was found within the controlled Python/POSIX, structured-generic, toy-evidence, and zero-authority boundaries. The exact outcome is limited to separate launch-plan-design readiness.

### Assumptions

- Exact clean detached Git bytes at the stated commit.
- Standard controlled Python/POSIX path semantics.
- No hostile same-process or same-user mutation.
- Historical test outcomes were inspected but not rerun.
- Private/manual Python composition is not an authorization mechanism.
- No cryptographic-scale or ECDLP inference is drawn.

### Evidence so far

- Exact HEAD, parent, tree, detached state, and cleanliness confirmed.
- All required V16 and V15 artifacts inspected.
- All nine V16 test-log hashes match exact Git object bytes.
- All three V15 review hashes match their provenance record.
- V15’s five repair obligations are implemented and reflected in tests and governance.
- Mathematical parameters, objective, gate, accounting vector, claim boundary, and budgets are unchanged.
- V1–V15 reject before row semantics.
- No authorized generated-row, matrix, runner, plan, or run route exists.
- No ECDLP or launch-authority overclaim exists.

### Failure modes

- A different runtime may not share the recorded POSIX normalization behavior.
- Arbitrary same-process introspection or manual object assembly is not sandboxed.
- Filesystem receipts are unauthenticated and sequential rather than pair-atomic.
- Canonical B6/B8 feasibility and external resource use remain unmeasured.
- Frozen B4 remains the only structurally separate complete five-field oracle.
- Relation generation, rank, linear algebra, target descent, crossover, and attack complexity remain open.

### Next concrete action

Obtain fresh independent accounting and red-team reviews of exact commit `d8ea562f1890ef07fd48b2bfeef41289599575e9`; do not design a launch plan or authorize execution unless both are scoped GO and the coordinator separately advances the state.

### Artifact paths

- `experiments/EXP-SGCP-EMBED-002/pre-run-theory-review-v16.md` — intended preservation path for this returned Markdown; not created by this review
- `experiments/EXP-SGCP-EMBED-002/contract.md`
- `experiments/EXP-SGCP-EMBED-002/hypothesis.json`
- `experiments/EXP-SGCP-EMBED-002/specification.json`
- `experiments/EXP-SGCP-EMBED-002/protocol-amendment-v16.json`
- `experiments/EXP-SGCP-EMBED-002/revision-response-v16.md`
- `experiments/EXP-SGCP-EMBED-002/development-test-log-v16.md`
- `experiments/EXP-SGCP-EMBED-002/source-self-review-v16.md`
- `experiments/EXP-SGCP-EMBED-002/handoff.md`
- `experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `tests/test_sgcp_embed_family.py`
- `research_ledger.md`
- `ledger.json`
