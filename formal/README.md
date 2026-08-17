# Formal research workspace

This directory is the default Lean workspace for the formal research lane.
The lane treats a theorem prover as an experimental instrument: models may
propose statements and proofs, but only tool-produced build/audit evidence is
accepted as machine-verification evidence.

Candidate sources are written here by `MathCodeFormalizer`
(`docs/mathcode-integration.md`), which runs the MathCode engine in a
throwaway directory under `.formal-attempts/` and copies in only a file that
passes a pre-stage scan. **Nothing containing `sorry` ever lands here**, by
design: the worker's forbidden-construct scan covers every `.lean` file in this
workspace, so one unfinished candidate left behind would invalidate every later
task run against it. Unfinished candidates stay in their attempt directory and
are reported as proof obligations.

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

Check that this machine can do any of that, and run one task end to end, with:

```bash
autoresearch formal doctor
autoresearch formal formalize --task-id ... --claim-id ... --claim-file ... \
    --theorem-name ... --theorem-file ...
```

## CVP reference pattern

The initial design is inspired by Mira-acc/cvp: keep the executable formal
proof, a human-readable argument, a pinned toolchain/dependency graph, and a
separate axiom audit. We reuse that verification discipline rather than
copying CVP-specific lattice definitions into the autoresearcher.
