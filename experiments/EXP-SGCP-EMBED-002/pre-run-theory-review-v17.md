# EXP-SGCP-EMBED-002 V17 Independent Pre-Run Theory Review

## Findings

### Blocking findings

None.

### Residual limitations

1. **LOW — The finite grammar governs Python path objects, not raw shell argument bytes after upstream coercion.**

   `_raw_output_path` classifies exact strings before `Path` construction and normalization (`experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7065-7092`). The verifier CLI, however, parses `--output` with `type=Path`, so terminal syntax supplied through shell `argv` is already erased before `output_path` sees it (`experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7784-7795`).

   This does not reopen the V16 Python-API defect because the boundary is explicitly disclosed: a preconstructed `Path` cannot preserve terminal `/` or `/.`, and portability is limited to the controlled POSIX runtime (`experiments/EXP-SGCP-EMBED-002/contract.md:226-240`; `experiments/EXP-SGCP-EMBED-002/handoff.md:21-26,68-73`). A future launch plan must bind a canonical output argument and must not claim preservation of raw CLI spelling.

2. **INFORMATIONAL — Git-object byte binding carries the standard Git object-integrity assumption.**

   The path-name digest intentionally binds names only; exact Git commit/tree verification binds file modes, names, blob identifiers, and bytes (`experiments/EXP-SGCP-EMBED-002/review-surface-manifest-v17.json:6-20,58-73`). This is correct under ordinary Git object semantics and hash-integrity assumptions, but is not a formal collision-free theorem.

3. **INFORMATIONAL — Recorded tests remain historical evidence.**

   The focused and validation receipts are recorded as passing, while repository-wide unittest discovery records one preserved unrelated immutable-run-guard failure (`experiments/EXP-SGCP-EMBED-002/development-test-log-v17.md:36-117`). They were not rerun. Static source counts independently corroborate 81 focused unittest methods, 225 repository unittest methods, and 27 module-level pytest-style functions.

4. **THEORY RESIDUAL — The cryptanalytic obligations remain open.**

   Outside frozen B4, the secondary four objective fields are deterministic replay checks rather than a structurally separate complete oracle (`experiments/EXP-SGCP-EMBED-002/contract.md:93-111`). Relation generation, factor-base logarithms, rank, sparse linear algebra, target descent, preprocessing crossover, rho comparison, scaling, and attack complexity remain unproved and unmeasured (`experiments/EXP-SGCP-EMBED-002/contract.md:595-619,651-656`).

## Exact review receipt

- Requested checkout: `/tmp/sgcp-v17-review-d6b642d`
- Physical path: `/private/tmp/sgcp-v17-review-d6b642d`
- Commit: `d6b642defccddab7629678ee3514c48228844bfa`
- Parent: `574b4c67a894e48715107e730c0b7b33b9fab1c5`
- Tree: `f27c736a2660155521b6da913bb1e7e0f3a9bffc`
- Subject: `Harden SGCP V17 raw path grammar`
- State before review: detached and clean, `## HEAD (no branch)`
- State after review: detached and clean, `## HEAD (no branch)`
- Parent-to-HEAD `git diff --check`: clean
- Proposed artifact path: `experiments/EXP-SGCP-EMBED-002/pre-run-theory-review-v17.md`
- Artifact written by this review: no

Inspection used Git commit/tree blobs only. No producer, verifier, test, record validator, indexer, runner, or experiment was executed.

## 1. V16 path-domain closure

V17 closes the exact V16 red-team findings within its stated Python-object and controlled-POSIX model.

The grammar:

- obtains `os.fspath` before normalization;
- accepts only an exact `str` result;
- rejects empty strings, embedded NUL, relative strings, terminal separators, terminal dot components, exact double-separator anchors, and explicit parent traversal;
- then performs normalized development-root containment (`experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7065-7107`);
- repeats the grammar and containment in direct descriptor-parent admission (`experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7110-7125`).

The focused control table covers:

- exact string, `pathlib.Path`, and custom exact-string `os.PathLike`;
- internal dot and repeated-separator aliases;
- three, four, and seven leading separators;
- relative in-root and escaping spellings;
- terminal `/` and `/.`;
- bytes, byte-valued `PathLike`, string subclass, empty, NUL, null, root, outside, parent traversal, and exact leading `//`;
- output admission, receipt path, status, standalone status, writer, and direct descriptor entry (`tests/test_sgcp_embed_family.py:4752-4950`).

The contract limits the three-or-more-leading-separator rule to the controlled POSIX runtime and expressly disclaims raw-spelling preservation (`experiments/EXP-SGCP-EMBED-002/contract.md:226-250`). The handoff identifies a portability claim as a failure mode (`experiments/EXP-SGCP-EMBED-002/handoff.md:68-73`). No universal portability claim was found.

### Restricted theorem candidate: V17 object-domain path admission

**Status:** `RESTRICTED THEOREM` candidate.

**Model:** The committed Python implementation, an available strict development root, ordinary `os.fspath`, and the controlled POSIX `abspath` behavior.

**Claim:** Every input reaching `_raw_output_path` either belongs to the admitted exact-string grammar and then undergoes root containment, or fails before filesystem creation.

**Proof sketch:** Exhaust the ordered branches at verifier lines 7065-7092; admitted values then pass lines 7095-7107. Writer entry calls admission before payload or parent creation at lines 7673-7681.

**Counterexample routes:** alternate path flavor, upstream `Path` coercion, custom `PathLike` side effects or exceptions, hostile same-process mutation, or different three-or-more-leading-separator behavior.

## 2. Cross-artifact consistency

The active artifacts agree:

| Requirement | Static evidence |
|---|---|
| V17 producer/verifier identity | Producer schema/version at `src/sgcp_embed_family.py:25-28`; verifier schemas/version at `src/verify_sgcp_embed_family.py:30-53` |
| V1–V16 rejection before row semantics | Verifier routing at `src/verify_sgcp_embed_family.py:6974-7021`; control at `tests/test_sgcp_embed_family.py:3894-3936`; contract at `contract.md:181-185` |
| Finite raw grammar | `contract.md:226-250`; `specification.json:69`; `protocol-amendment-v17.json:8-19`; `revision-response-v17.md:26-44` |
| Zero new V17 generated curve-family rows | Producer gates at `src/sgcp_embed_family.py:404-410,1311-1324,1463-1506,2099-2131`; specification at `specification.json:112-118,215-220` |
| Zero canonical runs | `ledger.json:126-133`; `review-surface-manifest-v17.json:62-67` |
| `maximum_runs=0` | `specification.json:209-214`; `contract.md:630-637`; manifest at `review-surface-manifest-v17.json:62-67` |
| Exact-commit review is the only current next stage | `handoff.md:86-91`; `revision-response-v17.md:69-74`; `development-test-log-v17.md:131-136`; `protocol-amendment-v17.json:63` |
| No current plan/execution authority | `handoff.md:12-15`; `research_ledger.md:29`; `review-surface-manifest-v17.json:62-73` |

“Zero generated rows” is correctly scoped to V17 generated curve-family density rows. Historical V1 development artifacts and frozen/transient controls remain in the tree and are explicitly classified as noncanonical (`hypothesis.json:76-86`; `contract.md:621-628`). No `EXP-SGCP-EMBED-002/runs/` path and no V17-schema development result exists.

All ten SHA-256 values recorded at `development-test-log-v17.md:16-34` independently match their exact Git blobs.

## 3. Review-surface manifest

The manifest is non-self-referential in the relevant sense:

- it contains neither a predicted commit/tree nor its own byte hash;
- its own fixed path name is included once in the path inventory;
- its digest covers only the canonical sorted path-name list;
- the externally verified exact Git tree binds the manifest’s bytes and all other committed bytes (`review-surface-manifest-v17.json:6-20,22-73`).

Independent reconstruction from `git ls-tree` produced:

- repository exact paths: 7;
- repository glob paths: 28;
- static experiment paths: 144;
- total: **179**;
- canonical path-name SHA-256:  
  `bc8034d20ac3d092270d749b6cb363df4f8f4531bccc0dd9a6616120f51de952`.

This exactly matches `review-surface-manifest-v17.json:58-60`. All five excluded future V17 review/closeout outputs are absent from the reviewed tree.

### Restricted theorem candidate: manifest receipt correctness

**Status:** `RESTRICTED THEOREM`.

**Claim:** Applying the manifest’s finite selection rules to tree `f27c736a2660155521b6da913bb1e7e0f3a9bffc` yields exactly the stated 179-path canonical sequence and SHA-256 receipt.

**Proof sketch:** Enumerate tree paths, apply exact paths, one-level globs, recursive experiment suffix rules and exclusions, sort as repository-relative POSIX names, append one newline per path, and hash.

**Limitation:** The theorem binds path selection and receipt arithmetic. Byte integrity is delegated to the exact Git tree.

## 4. Mathematical and cryptanalytic boundary

No accidental mathematical widening was found.

The parent-to-HEAD producer delta changes only protocol/schema labels and refusal messages; curve generation, predicates, factor bases, representative compilation, graph construction, optimizer, objective, thresholds, family gate, and accounting formulas are unchanged.

The retained mathematical object remains:

- a generated 5–8-bit prime-order curve grid;
- symmetric x-fiber factor bases;
- the fixed lexicographically least nonidentity degree-two representative compiler;
- degree-four order ideals and pair-conflict independence;
- private final `A4+A4` support with no public final-layer edge (`contract.md:30-57`);
- an explicit, charged public label-to-formal source table, not an inversion algorithm (`contract.md:59-70`; `specification.json:96-100`);
- 168 rows and 672 cap cells with the unchanged six-pair family gate (`contract.md:330-378`);
- finite exactness bounded to the fixed compiler, order-ideal construction, and stated oracle/replay architecture.

The hypothesis remains `HYPOTHESIS`, `TOY-EVIDENCE`, `MODEL-BOUND`, and `NOVELTY-UNVERIFIED` (`hypothesis.json:5-13`; `handoff.md:12-15`). Success would be only a toy coordinate-structure signal, while failure narrows only the exact predicate-plus-compiler construction (`contract.md:595-619`).

### Missing lemmas and model-escape routes

- A relation-generation theorem with charged success probability is absent.
- Factor-base logarithm acquisition and matrix-rank behavior are absent.
- Sparse linear algebra and individual-log target descent are absent.
- No fixed-curve preprocessing crossover against rho/BSGS is established.
- No scaling inference is permitted from four tiny bit sizes.
- Alternate compilers, formal quotients, model transformations, source-recoverable non-tree operations, and non-generic attacks remain outside the tested model (`contract.md:616-619`).
- A complete valid matrix in which every fixed family-cap pair fails is the scoped counterexample to this hypothesis; it is not a counterexample to coordinate-specific structured embeddings generally (`contract.md:604-619`).

## 5. Authorization boundary

No artifact at this commit authorizes launch-plan design or execution.

Independent gates include:

- experiment status `review_required` and null approver (`specification.json:5-8,378-380`);
- wall, CPU, memory, and run budgets all zero (`specification.json:209-214`);
- empty official run ledger (`ledger.json:126-133`);
- disabled producer generation and CLI routes (`src/sgcp_embed_family.py:404-410,1463-1506,2099-2131`);
- manifest authority fields all zero or false (`review-surface-manifest-v17.json:62-67`);
- generic runner rejection of any status other than approved or draft (`src/crypto_autoresearcher/runner.py:1422-1442`);
- independent positive-budget checks (`src/crypto_autoresearcher/runner.py:1457-1471`);
- independent exhaustion at zero `maximum_runs` (`src/crypto_autoresearcher/runner.py:1538-1542`).

The nonzero `900`-second and `4`-GiB values in `hypothesis.json:68-69` are explicitly proposed future role estimates, not active budget or authority. The verifier CLI’s existence is likewise not execution approval.

## Final verdict

**GO for separate launch-plan design only**

This is one theory-lane prerequisite. It does not itself change the commit’s current plan-design prohibition; the remaining independent reviews and coordinator gate still apply. It authorizes neither execution nor any mathematical, asymptotic, cryptanalytic, deployment, or ECDLP claim.

## Handoff: EXP-SGCP-EMBED-002 V17 independent pre-run theory review

### Claim or task

Independently determine whether exact commit `d6b642defccddab7629678ee3514c48228844bfa` closes V16’s path-domain findings without changing the mathematical claim or creating launch authority.

### Status

`OBSERVATION`

No blocking theory finding was identified within the finite Python-object, controlled-POSIX, exact-Git, toy, and model-bound scope.

### Assumptions

- Exact detached Git object state at the stated commit, parent, and tree.
- Ordinary Git object-integrity semantics.
- Controlled POSIX path behavior for three-or-more leading separators.
- No hostile same-process monkeypatching or hostile same-user filesystem mutation.
- Recorded tests are historical receipts and were not rerun.
- Preconstructed `Path` and raw shell-argument spelling are distinct ingress models.
- No cryptographic-scale inference is drawn.

### Evidence so far

- Detached and clean status confirmed before and after.
- Commit, parent, and tree exactly match the requested values.
- All ten recorded V17 blob hashes match.
- The 179-path manifest receipt independently reproduces exactly.
- V1–V16 route to zero-row legacy rejection.
- V17 path classes are checked before normalization for exact-string inputs.
- Producer, specification, ledgers, and runner retain independent zero-authority gates.
- Mathematical source, source-recovery boundary, objective, gate, and interpretation remain unchanged.
- No launch plan, approval lock, V17 generated curve-family row, canonical run, or run directory exists.

### Failure modes

- Raw CLI syntax can be erased by `argparse` `Path` coercion before the Python-object grammar.
- Other operating systems or path flavors may not share the controlled POSIX behavior.
- Git byte binding assumes ordinary object-hash integrity.
- Outside frozen B4, secondary objective exactness is replay-confirmed rather than separately oracle-proved.
- Relation generation, rank, linear algebra, target descent, crossover, and attack complexity remain open.
- Historical tests do not substitute for future exact launch-plan and runtime validation.

### Next concrete action

Obtain fresh independent accounting and red-team reviews of exact commit `d6b642defccddab7629678ee3514c48228844bfa`; only after all required reviews and coordinator action may a separate hash-complete launch-plan design begin, with canonical raw-argv/path handling made explicit.

### Artifact paths

- `experiments/EXP-SGCP-EMBED-002/pre-run-theory-review-v17.md` — proposed preservation path; not created by this review
- `experiments/EXP-SGCP-EMBED-002/review-surface-manifest-v17.json`
- `experiments/EXP-SGCP-EMBED-002/protocol-amendment-v17.json`
- `experiments/EXP-SGCP-EMBED-002/revision-response-v17.md`
- `experiments/EXP-SGCP-EMBED-002/source-self-review-v17.md`
- `experiments/EXP-SGCP-EMBED-002/development-test-log-v17.md`
- `experiments/EXP-SGCP-EMBED-002/contract.md`
- `experiments/EXP-SGCP-EMBED-002/hypothesis.json`
- `experiments/EXP-SGCP-EMBED-002/specification.json`
- `experiments/EXP-SGCP-EMBED-002/handoff.md`
- `experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `tests/test_sgcp_embed_family.py`
- `ledger.json`
- `research_ledger.md`
