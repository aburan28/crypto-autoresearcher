# Pinned Lean workspace build continuation (2026-10-27 UTC)

This directory preserves four local `lake build` attempts against the pinned
Lean 4.35.0-rc1 formal workspace on PR #2599, starting from commit
`b2ff94a736b6b9cd387c581e10ca2c9ad5cfe177`. The exact input and
dependency revisions, successful **named-module** build, and imported axiom
audit are recorded in `../lake-named-20261027/lake-named-validation.json`.

The first attempt (`binstd-lake-root-20261027`) was bounded at 300 seconds
and returned 124. Its log already reports that the generated
`formal/CryptoResearch.lean` root was missing. Lake continued compiling
independent modules until the timeout. The second attempt used a 480-second
bound, reported the same missing root, and was deliberately terminated with
143 once that deterministic problem was identified.

`python3.11 tools/rebuild_formal_root.py` then generated the ignored root
from the 48 theorem modules on disk; `--check` passed. Its exact bytes are in
`generated-root.lean`. The formal CLI's `verify` path invokes the same
`rebuild_root` function automatically. The third direct root build, now with
the root present, returned 124 at its 420-second bound. It **did compile**
`CryptoResearch.Semaev.BooleanParityDegreeThreeRankCertificate` in 343
seconds and wrote the corresponding `.olean`. The 30-second incremental
fourth pass built `CryptoResearch.Semaev.ConcreteFirstFallWitness`, then
returned 124 before the remaining root jobs completed. These are bounded
incomplete builds, not mathematical counterexamples or a full-workspace pass.

No `lake update` ran. No target verifier or project-wide `AxiomAudit.lean`
was run after these attempts. The requested BINSTD claim remains supported
only by the earlier named-module Lake build, imported named axiom audit and
the separate independent finite-claim reviews. The full workspace and exact
formal-target gate remain open. Hosted Actions on this PR also fail before
runner assignment due the account payment/spending-limit gate, so this local
continuation does not authorize a merge or Pages publication.

Run `python3.11 make_receipt.py --check` from this directory to recompute the
hashes and assertions in `workspace-build-receipt.json`. The receipt is local
execution evidence; it does not claim an independent runner or a kernel
recheck of every project theorem.
