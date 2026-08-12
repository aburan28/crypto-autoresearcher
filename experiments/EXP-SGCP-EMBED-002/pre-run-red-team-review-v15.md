Verdict: `REVISE`. No containment escape, accounting defect, mathematical change, budget widening, or generated-row/run route was found. Two V15 repair claims remain false, however, and the exact-current-state records are inconsistent.

## Risk list

1. **MEDIUM — “Repeated separators normalize” is broader than the implementation and control.**

The contract says equivalent repeated separators normalize to one destination at [contract.md:226](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/contract.md:226), and the amendment describes in-root repeated separators as aliases at [protocol-amendment-v15.json:9](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/protocol-amendment-v15.json:9).

Clean counterexample on this host:

```text
//private/tmp/.../development/nested//alias.json
```

Python preserves exactly two leading POSIX separators. Consequently, `abspath()` retains the `//` anchor and `relative_to(root)` rejects it at [verify_sgcp_embed_family.py:7063](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7063), even though resolving that spelling on this host produces the ordinary in-root `/private/...` path. The V15 control exercises only an internal `nested//alias.json` separator at [test_sgcp_embed_family.py:4610](/private/tmp/sgcp-v15-review-8adba3a/tests/test_sgcp_embed_family.py:4610).

This is not an escape; it is a claim/control mismatch. Narrow the policy to “non-leading repeated separators,” and explicitly reject or separately classify the POSIX `//` anchor.

2. **MEDIUM — The committed-current-state repair remains stale.**

The active ledger still says V15 is “under validation” and instructs validating and committing it at [research_ledger.md:29](/private/tmp/sgcp-v15-review-8adba3a/research_ledger.md:29). The primary handoff likewise instructs validation, hash freezing, and committing before review at [handoff.md:71](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/handoff.md:71).

That contradicts the revision response’s claim that these records were repaired at [revision-response-v15.md:17](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/revision-response-v15.md:17) and that exact-commit review is now the next action at [revision-response-v15.md:62](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/revision-response-v15.md:62). At the reviewed commit, validation, nine-hash freezing, and commit are already recorded as completed evidence.

3. **LOW — Contract title remains routed as V14.**

The contract begins `version 14` at [contract.md:1](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/contract.md:1), although its body, source constants, schema, protocol, and frozen hash are V15. Source routing itself is correct: V15 is current and V1–V14 are legacy at [verify_sgcp_embed_family.py:30](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:30).

4. **LOW — “Repository-wide suite” overstates the recorded test scope.**

The recorded command is specifically `unittest discover` at [development-test-log-v15.md:83](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/development-test-log-v15.md:83). Static AST counting confirms 225 unittest class methods and 81 focused methods, but also finds 27 module-level pytest-style tests beginning at [test_outer_translator.py:62](/private/tmp/sgcp-v15-review-8adba3a/tests/test_outer_translator.py:62) and [test_outer_translator_floor.py:101](/private/tmp/sgcp-v15-review-8adba3a/tests/test_outer_translator_floor.py:101), which `unittest discover` does not collect.

The exact command and `225` count are honest; rename this “repository-wide unittest-discover suite,” or separately record the pytest scope.

## Controls that held

- Ordinary `.`, internal repeated separators, and absolute in-root paths normalize as intended.
- Explicit `..`, root itself, and normalized outside-root destinations reject at [verify_sgcp_embed_family.py:7063](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7063).
- Descriptor traversal uses `O_DIRECTORY|O_NOFOLLOW` at [verify_sgcp_embed_family.py:7080](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7080); the symlink-parent control is present at [test_sgcp_embed_family.py:4540](/private/tmp/sgcp-v15-review-8adba3a/tests/test_sgcp_embed_family.py:4540).
- Receipt path, status, and writer all pass through `output_path`; destination and receipt names are preflighted together at [verify_sgcp_embed_family.py:7663](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7663).
- The standalone parser does not call production status/canonicalization helpers and independently checks receipt/payload attribution at [test_sgcp_embed_family.py:73](/private/tmp/sgcp-v15-review-8adba3a/tests/test_sgcp_embed_family.py:73). Its sequential, unauthenticated boundary is accurately disclosed.
- All nine recorded SHA-256 values at [development-test-log-v15.md:20](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/development-test-log-v15.md:20) match the committed blobs.
- The durable inventory now includes the missing V7 records and complete V14/V15 record sets at [research_ledger.md:224](/private/tmp/sgcp-v15-review-8adba3a/research_ledger.md:224) and [specification.json:336](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/specification.json:336).
- The recorded `17` validation objects are consistent with the selector: 14 decision records plus research question, hypothesis, and specification.
- Fresh static arithmetic reproduces `480/112/336/218/4218`; the derivation is enforced from verified transcripts at [verify_sgcp_embed_family.py:639](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:639).
- The parent diff contains no curve-grid, predicate, compiler, optimizer, objective, or gate change.
- Memory and external costs remain honestly excluded at [contract.md:384](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/contract.md:384).
- Budgets remain zero at [specification.json:208](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/specification.json:208), approval is null at [specification.json:359](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/specification.json:359), and `ledger.json` records no runs at [ledger.json:126](/private/tmp/sgcp-v15-review-8adba3a/ledger.json:126).
- Public generated-curve and legacy-row construction are disabled, density construction admits only frozen p=19/B=4, and development/canonical entry points refuse execution at [sgcp_embed_family.py:404](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py:404), [sgcp_embed_family.py:1463](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py:1463), and [sgcp_embed_family.py:2099](/private/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py:2099).

No repository test, producer, verifier, validator, runner, or experiment was executed. The detached worktree remained clean at exact HEAD `8adba3ad4ddf7055cc098831dff2a33e1e469810`, parent `232db54d54257afde467d6680552fed048dc7440`.

## Required controls and next falsification tests

- Add a table-driven policy control covering internal `//`, leading `//`, `.`, absolute in-root, explicit `..`, root itself, ordinary outside paths, and symlinked parents across writer, receipt-path, status, and descriptor-walker entries.
- Add a committed-state consistency check aligning contract title, specification version, ledger version, and handoff/active-ledger next action.
- Relabel the recorded suite or separately validate the 27 pytest-style tests during a later authorized validation cycle.
- Re-freeze affected hashes and obtain fresh exact-commit theory, accounting, and red-team reviews. Do not design or execute a launch plan beforehand.

## Handoff: EXP-SGCP-EMBED-002 V15 adversarial review

### Claim or task

Falsify the exact-commit V15 path, record, inventory, accounting, and zero-authority repair using read-only evidence.

### Status

`OBSERVATION`

### Assumptions

- Controlled macOS/POSIX workspace semantics.
- No hostile same-user filesystem actor or hostile same-process monkeypatching.
- Historical test observations were inspected but not rerun.

### Evidence so far

- No containment escape or generated density-row/run path was found.
- The leading-`//` counterexample falsifies the blanket repeated-separator claim.
- Current handoff/ledger state, contract title, and repository-wide test wording remain inaccurate.
- Hashes, inventory, operation vector, accounting boundary, schema routing, and zero budgets otherwise reconcile.

### Failure modes

- Treating exact `//` as an ordinary repeated separator despite Python’s distinct POSIX anchor.
- Mistaking precommit handoff language for committed-current-state evidence.
- Treating unittest discovery as collection of every repository test.

### Next concrete action

Prepare one no-run successor correcting the path policy/control, current-state records, contract title, and suite-scope wording; preserve zero budgets and request fresh exact-commit reviews.

### Artifact paths

- `experiments/EXP-SGCP-EMBED-002/`
- `research_ledger.md`
- `ledger.json`
- `tests/test_sgcp_embed_family.py`

REVISE
