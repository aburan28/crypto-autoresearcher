# Scoped obstruction proofs

This dependency-free project pins Lean 4.22.0 and uses the repository's existing
formal verifier. It currently proves the odd-torsion translation statement
under explicit additive laws. Independent semantic-fidelity review and any
bridge to a concrete elliptic curve remain separate obligations.

```sh
cd formal/scoped-obstructions
lake build
lake env lean AxiomAudit.lean
cd ../..
python3 -m orchestration.formal.cli --repo-root . verify \
  --task-file formal/targets/scoped-odd-torsion-translation.yaml \
  --artifact-out /absolute/fresh-verification.json
```

The audit fails if any requested declaration is absent, is not a theorem, or
has any global axiom dependency. The repository verifier additionally checks
the exact requested theorem, source hashes, forbidden constructs and pinned
versions. A passing build alone is not a semantic review or ledger decision.

The model uses only associative commutative addition and a two-sided zero;
it is weaker than an abelian group. An explicit two-element XOR model makes
the hypotheses non-vacuous and supplies an even-scalar counterexample to a
stronger statement without oddness. See the
[derivation and model boundary](../../research/ten-lead-evidence/torsion-proof-note.md).
