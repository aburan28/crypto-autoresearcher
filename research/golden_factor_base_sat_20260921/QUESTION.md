# Factor base and decomposition co-design

User request: keep working on finding a golden factor base with a corresponding point decomposition that is easy to solve, possibly by SAT. This is a scoped continuation with ideation, exact finite controls, and execution of the cheapest complete discriminating protocol; it is not a new goal or a request to publish remotely.

Find a construction whose membership, useful relation yield, and decomposition search jointly improve. A small membership formula or high coverage alone is insufficient. Candidate constructions must be target-independent unless the full target-dependent construction cost and its role are explicit. No target-specific join table may be hidden as SAT preprocessing.

The immediate deliverable is three distinct falsifiable proposals and one selected bounded experiment. Candidate directions to examine, not prescriptions or conclusions:

1. Choose a binary subspace or affine seed by the structure of the descended products and partial-assignment constraints, comparing with the same-sized ordinary polynomial subspace and deterministic random controls. Replacing a basis without changing the point set is an encoding control, not a new base.
2. Co-design trace-compatible two-torsion quotient domains with explicit lifting and exceptional branches. Do not confuse a nonlinear Frobenius union with a linear subspace, or membership in 2E with membership in a selected prime-order subgroup.
3. Encode representative-pair/relative-Frobenius support in a factor graph so partial assignments propagate before complete endpoint tuples are chosen. Retain the exact direct meet-in-the-middle control and all preprocessing costs.

The currently accepted cold N53 IC remains slower than matched strengthened rho (RUN-KIC-a15078 paired median 3.2945816805). That result motivates this change of research direction; the previous own-PID profiling proposal is deferred by the user's explicit new mathematical priority. No new claim about full IC speed is to be made from a decomposition-only test.

Earlier exact finite work on K1/F(2^19) found a four-orbit base [6685,8461,25103,32881] with 6257/6909 target-orbit coverage by at most three points, uniquely optimal among the frozen 37-orbit pool. This is an internal bounded reference; inspect the copied exact report. Membership-only, support compression, and implicit S5 formula results did not establish cheap coupled extraction. Prior n41/n53 conflict-capped SAT outcomes remain UNKNOWN.

For the new finite experiment, require exact point-set membership, actual curve/group lifting, an independent direct decomposition oracle, and every model checked against CNF/XOR and group equations. Cover satisfiable, truly unsatisfiable and exceptional/repeated-summand cases. Capped solver outcomes are censored. Record construction, encoding, solve, decoding/verification, memory, success probability/coverage, conflicts/decisions, and a meaningful measure of partial-assignment pruning. Keep selection and confirmation targets separate. Check every declared frontier row across time, memory and data/query cost before assigning dominated_by; uncertainty must be explicit.

Scope: public synthetic curve points and known-answer controls only. No imported or unknown targets, private scalar recovery, or key-breaking claims. No asymptotic improvement is presumed. If a proposal is proof-oriented, include the four proof-search audits and identify a suitable Lean obligation or the exact reason formalization is not yet useful.

All current local inputs are committed-source snapshots under inputs/source_bindings.json. Knowledge-base MCP search is unavailable; the CLI query failed because its configured in-memory collection is absent. That is not evidence of prior-art absence.

Primary literature retrieved and opened by root in this turn:

- Trimoska, Ionica and Dequen, A SAT-Based Approach for Index Calculus on Binary Elliptic Curves, https://eprint.iacr.org/2019/313.pdf. Retrieved provenance. It studies a subspace factor base, XOR-aware SAT and symmetry breaking; improved decomposition timings there do not establish an advantage over generic methods on prime-degree binary fields.
- Point Decomposition Problem in Binary Elliptic Curves, https://eprint.iacr.org/2015/319.pdf. Retrieved provenance. Its auxiliary-variable S3 decomposition is a relevant control for degree versus variable count. Read the precise construction before relying on any stronger claim.

Native model routing follows the repository's OpenAI policy bindings: research-deep uses sol/high; Coordinator uses terra/high; independent review uses a fresh sol/xhigh session. Serving-model probe status must be disclosed truthfully. Executor policy may need the already-used scoped sol/high resolution; record it before execution. Bedrock is prohibited.
