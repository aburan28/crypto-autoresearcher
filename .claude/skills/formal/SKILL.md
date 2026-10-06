---
name: formal
description: "Inspect or maintain Lean theorem targets, formalization task specs, proof obligations, axiom audits and verification receipts. Use for formal proof work or a supplied theorem verification request. Existing formal task execution goes through run; official mathematical conclusions require review-evidence."
---

# Formal proof work

Read `formal/README.md`, `formal/targets/README.md`, and `orchestration/formal/cli.py`. Use `tools/formal_task.py` and `tools/verify_formal_targets.py` within their documented task/receipt interfaces.

1. Bind the exact theorem statement, hypotheses, task spec, source revision, Lean/toolchain version and artifact path. A nearby theorem is not the requested theorem.
2. Inspect existing source and target coverage. Distinguish engine-generated output from Lean-verified output; preserve compile logs, theorem identity and axiom audit.
3. Check `sorry`, axioms, imports, statement strengthening/weakening, and dependency pins. A successful build only certifies the stated formal object under those assumptions.
4. Keep proof-source edits and verification receipts separate; use fresh receipt paths and preserve failed attempts. Route existing frozen-task execution through run, without authoring a new target as a launch preflight.
5. Return the statement, verification state, artifact identities, open mathematical gaps and toolchain impediments. Proof generation/MathCode or model calls may spend tokens; use current runtime policies and never select Bedrock.
6. Leave promotion, contradiction and breakthrough review to the existing Coordinator/review lifecycle.

Follow current `AGENTS.md` authority, provenance and immutable-record rules. This profile adds no prerequisite to `run`; preserve explicit execution requests.
