---
name: solver
description: "Diagnose existing Groebner, SAT, Macaulay, GF(2), rank, certificate and solver-worker artifacts; plan solver integration or check correctness and accounting. Use for solver-stage questions and supplied synthetic systems. Use ic for relation semantics, review-evidence for official conclusions, and run for trials."
---

# Solver diagnostics

Read `groebner_compare/README.md`, `src/crypto_autoresearcher/gf2/README.md`, and the selected solver source/manifest. Inspect `harness/macaulay_fp/` for prime-field presentations and `tools/smallroot_reach.py` only within its documented model.

1. Bind characteristic, ring, variable order, Boolean quotient rules, equation digest, target instance and requested output. Never substitute another ring or drop constraints silently.
2. Identify adapter and dependencies. SymPy, PolyBoRi, repository F5B, Julia workers, native GF(2), and GPU updates are distinct implementations. Read the worker contract before exchanging JSONL.
3. Inspect independent correctness certificates: roots satisfy original equations; a claimed basis satisfies the required ideal checks; rank/nullspace outputs verify against the original matrix. A returned candidate or small matrix is not a complete certificate.
4. Count matrix construction, columns, fill-in, elimination, failed attempts, tracing, learn/apply setup, verification and memory. Report solving degree separately from wall time and relation yield.
5. Preserve timeout/crash/incompatible outcomes and raw worker logs. Do not report an unavailable solver or an unresolved variable as a mathematical obstruction.
6. Return exact input/adapter/certificate identities and a stage-specific diagnosis. Use bench for paired comparisons, gpu for kernel correctness, and run for existing trial execution.

Follow current `AGENTS.md` authority, provenance and immutable-record rules. This profile adds no prerequisite to `run`; preserve explicit execution requests.
