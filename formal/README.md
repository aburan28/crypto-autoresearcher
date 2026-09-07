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
lake build +CryptoResearch.YourModule
lake env lean AxiomAudit.lean
# The worker also generates and runs an audit of the exact requested theorem.
```

and rejects proof sources containing `sorry`, `admit`, custom `axiom`
declarations, or `unsafe` declarations.

Bring the workspace up (needs network and `elan`), then check and run:

```bash
./formal/setup.sh                 # writes lean-toolchain + lake-manifest.json
autoresearch formal doctor
autoresearch formal formalize --task-file formal/targets/ncp-affine-normal-form.yaml
```

`targets/` holds the frozen task specs; `CryptoResearch.lean` is a generated
root module (`tools/rebuild_formal_root.py`) and is not committed.

## CVP reference pattern

The initial design is inspired by Mira-acc/cvp: keep the executable formal
proof, a human-readable argument, a pinned toolchain/dependency graph, and a
separate axiom audit. We reuse that verification discipline rather than
copying CVP-specific lattice definitions into the autoresearcher.

For existing proofs, use `autoresearch formal verify --task-file <spec>
--artifact-out <new-receipt>` without MathCode. See
[the direct Lean workflow](../docs/formal-research-lane.md#running-lean-directly).
The pinned dependency-free `smoke/` project and `tests/test_lean_live.py` qualify
the verifier using real positive and negative controls before research use.
