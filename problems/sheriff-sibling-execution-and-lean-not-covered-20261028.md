# Deep sheriff re-audit could not execute sibling code or Lean

- **Status:** open
- **Kind:** environment and permission impediment
- **Affected work:** case `SHF-20261028-0f3f64` (`research/sheriff/SHF-20261028-0f3f64/`): claims C-LEAN-1 and C-STARK-1..5 (test execution), C-KOB-2 (`analyze_v2.py` rerun), C-DEF-2 (workflow states)
- **Next action owner:** an operator who can attach `isogeny-labs/crypto` and `isogeny-labs/cryptanalysis` with execution allowed, and install elan
- **Last updated:** 2026-10-28

## Problem

The cloud session could not attach the sibling repositories with `add_repo` (refused by the permission policy). Read-only partial clones of the public repositories were used instead. Running `cargo test --release --lib zk::stark`, installing elan, and rerunning cryptanalysis `analyze_v2.py` were refused as execution of external code. Consequences recorded in the case: no mutation controls ran against the STARK verifier, no Lean build or axiom audit of `formal/CryptoResearch/Quotient/TranslationDescent.lean`, and the sibling-repo sweep checkers did not run.

## Evidence and uncertainty

An impediment is never negative evidence (AGENTS.md rule 5). The affected claims are `not_covered` or carry a code-reading-only scope in `findings.yaml`. Nothing here says the tests fail or the Lean module does not build.

## Resolution gate

Run in an environment with both siblings checked out and execution allowed:
`cargo test --release --lib zk::stark -- --include-ignored` in crypto; `./formal/setup.sh && lake build CryptoResearch.Quotient.TranslationDescent && lake env lean AxiomAudit.lean` in `formal/`; `python3 tools/sheriff.py sweep --target all --deep`. A new case records the result.
