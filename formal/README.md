# Formal research workspace

This directory is the default Lean workspace for the formal research lane.
The lane treats a theorem prover as an experimental instrument: models may
propose statements and proofs, but only tool-produced build/audit evidence is
accepted as machine-verification evidence.

A formal result is **not** authoritative research state. A successful Lean
build must still receive an independent semantic-fidelity review confirming
that the formal proposition matches the human claim and is not vacuous or
weakened by hidden assumptions. Only the canonical Coordinator may promote a
reviewed artifact into official claim/ledger state.

## Expected workspace contract

A concrete Lean project placed here should contain:

- `lean-toolchain`
- `lakefile.toml` or `lakefile.lean`
- a pinned `lake-manifest.json`
- theorem source files
- `AxiomAudit.lean`

The worker runs:

```bash
lake build
lake env lean AxiomAudit.lean
```

and rejects proof sources containing `sorry`, `admit`, custom `axiom`
declarations, or `unsafe` declarations.

## CVP reference pattern

The initial design is inspired by Mira-acc/cvp: keep the executable formal
proof, a human-readable argument, a pinned toolchain/dependency graph, and a
separate axiom audit. We reuse that verification discipline rather than
copying CVP-specific lattice definitions into the autoresearcher.
