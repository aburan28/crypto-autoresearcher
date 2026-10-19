# L1 build (sheriff re-audit)

Built in a scratch copy of crypto-autoresearcher `formal/` at origin/main ea8a9f6f1d,
never in the producer tree.

- toolchain: `formal/lean-toolchain` (leanprover/lean4:v4.35.0-rc1) via elan 4.2.4
- packages: shallow clones at the exact revs in `formal/lake-manifest.json`
  (`formal-packages-at-manifest-revs.txt`)
- Mathlib oleans: `lake exe cache get .lake/packages/mathlib/Mathlib/Tactic/Abel.lean`
  (the theorem's only import; 586 files)
- `lake build CryptoResearch.Quotient.TranslationDescent` -> `translation-descent-build.log`
  (exit 0; 2 unreachable-tactic linter warnings: the `first` fallbacks never run)
- `lake env lean AxiomAuditTranslationDescent.lean` (formal/AxiomAudit.lean with the root
  import narrowed to this module, plus `#print axioms`) -> `axiom-audit.out`
- `lake env lean ProvesTooMuch.lean` (same proof script, false statements 3•T and T=0)
  -> `proves-too-much.out` (must fail; it does)

Not done: the whole-workspace `lake build` + `tools/verify_formal_targets.py`
(disk: a full Mathlib cache does not fit), and lean4checker.
