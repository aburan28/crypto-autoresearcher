## Findings

1. **Medium — the required current-state repair remains incomplete.** V15 says the active handoff and ledger were refreshed and that fresh review is now the next action ([protocol-amendment-v15.json:13](/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/protocol-amendment-v15.json:13), [revision-response-v15.md:62](/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/revision-response-v15.md:62)). Instead, the handoff still directs validation, hash freezing, and committing V15 ([handoff.md:71](/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/handoff.md:71)), and the active ledger still says “under validation” and “Validate and commit” ([research_ledger.md:29](/tmp/sgcp-v15-review-8adba3a/research_ledger.md:29)). The test log repeats that obsolete next action ([development-test-log-v15.md:115](/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/development-test-log-v15.md:115)). This does not authorize execution, but it repeats the exact workflow-state defect V15 was meant to close and blocks launch-plan design review.

2. **Low, but blocking for an exact contract — the V15 contract still self-identifies as version 14.** Its title says `version 14` ([contract.md:1](/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/contract.md:1)), while the specification and executable protocol are V15 ([specification.json:5](/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/specification.json:5), [sgcp_embed_family.py:25](/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py:25)). This is not mathematical widening, but an internally inconsistent hash-bound contract should not feed a hash-complete plan.

No Critical or High findings.

The static audit otherwise confirms:

- Mathematical invariance from V14: the curve grid, predicates, compiler, graph, objective, thresholds, and classification are unchanged ([protocol-amendment-v15.json:19](/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/protocol-amendment-v15.json:19)).
- The Path claim is accurately narrowed and implemented as normalized in-root aliases plus explicit `..` rejection ([contract.md:226](/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/contract.md:226), [verifier:7063](/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7063), [tests:4601](/tmp/sgcp-v15-review-8adba3a/tests/test_sgcp_embed_family.py:4601)).
- V1–V14 are registered as legacy and routed to rejection without row reports ([verifier:30](/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:30), [verifier:7007](/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7007), [tests:3749](/tmp/sgcp-v15-review-8adba3a/tests/test_sgcp_embed_family.py:3749)).
- `TOY-EVIDENCE`, `MODEL-BOUND`, and `NOVELTY-UNVERIFIED` remain explicit, with rank, descent, rho, scaling, and ECDLP conclusions excluded ([hypothesis.json:7](/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/hypothesis.json:7), [contract.md:620](/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/contract.md:620)).
- Active wall, CPU, memory, and run budgets remain zero ([specification.json:208](/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/specification.json:208)); the ledger has no runs ([ledger.json:127](/tmp/sgcp-v15-review-8adba3a/ledger.json:127)); and all public producer routes remain gated ([producer:404](/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py:404), [producer:1463](/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py:1463), [producer:2123](/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py:2123)).
- All nine logged SHA-256 values match the committed files. Recorded tests were not rerun and remain historical evidence.

## Handoff: EXP-SGCP-EMBED-002 V15 theory review

### Claim or task

Independent read-only theory review of exact commit `8adba3ad4ddf7055cc098831dff2a33e1e469810`, parent `232db54d54257afde467d6680552fed048dc7440`.

### Status

`REVISE` before launch-plan design review. Mathematical, routing, containment, claim-boundary, and zero-authority checks pass; committed record consistency does not.

### Assumptions

- Historical test-log outcomes were inspected but not rerun.
- The review covers this exact clean detached commit only.
- No theorem or cryptographic-scale inference is drawn from frozen or prospective toy rows.

### Evidence so far

- HEAD and parent were confirmed; final worktree status remained clean and detached.
- The producer/verifier mathematical delta is protocol-label-only; the substantive change is the accurately narrowed path policy.
- All nine V15 logged hashes match.
- No generated family row, run, runner, plan, or authority increase appears in the parent diff or current ledger.
- Counterexample route remains a complete valid exact matrix failing the gate; invalid or incomplete evidence remains `INCONCLUSIVE` ([specification.json:237](/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/specification.json:237)).
- Model-escape routes remain other compilers, quotients, transformations, or source-recoverable non-tree operations—not ruled out by this protocol ([contract.md:593](/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/contract.md:593)).

### Failure modes

- Active records misstate already-completed validation and commit work.
- The contract carries a stale version identifier.
- Frozen B4 remains the only structurally separate complete five-field oracle; B6/B8 feasibility and external resources remain unmeasured.
- Nothing establishes relation generation, rank, target descent, preprocessing advantage, or an ECDLP improvement.

### Next concrete action

Create one no-run record-only successor correcting the contract title and updating the active handoff and research-ledger row to the committed V15 review state; preserve every zero budget and mathematical byte, then obtain fresh exact-commit reviews.

### Artifact paths

- [contract.md](/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/contract.md:1)
- [specification.json](/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/specification.json:1)
- [protocol-amendment-v15.json](/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/protocol-amendment-v15.json:1)
- [handoff.md](/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/handoff.md:1)
- [research_ledger.md](/tmp/sgcp-v15-review-8adba3a/research_ledger.md:29)
- [producer](/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py:1)
- [verifier](/tmp/sgcp-v15-review-8adba3a/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:1)
- [tests](/tmp/sgcp-v15-review-8adba3a/tests/test_sgcp_embed_family.py:1)

**Final decision: `REVISE`**
