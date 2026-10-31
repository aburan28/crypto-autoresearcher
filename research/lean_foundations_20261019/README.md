# Lean foundation retrofit

This builds on the preserved 2026-10-18 producer and independent review, using
stable Lean 4.35.0 and exact Mathlib cfc55fc58714a59dc06e6e79edc6d1d95140d3c2.
The [claim note](theory.md) states the precise scope; [scope.md](scope.md) records
the integration bases and publication boundary. New independent review is
pending; existing verdicts are never attributed to these new proofs.

| Obligation | Implementation |
| --- | --- |
| Full frozen NCP reachability iff, constructive witness and minimum length | `formal/CryptoResearch/NCP/Reachability.lean` |
| Actual additive-group point action, chronological composition and scalar encoding | `formal/CryptoResearch/NCP/PointAction.lean` |
| Companion kernel witness outside the two-sided commutator ideal | `formal/CryptoResearch/NCP/CommutatorCompanion.lean` |
| Empty bases, mixed signs, insufficient depth and operation-order controls | `formal/CryptoResearch/NCP/ReachabilityControls.lean` |
| Canonical cyclic encoding, both actual-point rho collision branches and explicit coprime inverse | `aburan28/crypto-lean`, `CryptoLean/Group/{CyclicEncoding,RhoCollision,CoprimeTransport}.lean` |

The integrated pre-retrofit baseline built and audited 498 declarations; the
first NCP additions built and audited 539. These are actual machine-audit
counts, not the number of independently reviewed research claims. Fresh named
target receipts and independent semantic reports will be linked here when
produced. Older receipts retain their original toolchain and verifier scope.

The unrelated inherited validation failure was a scope-producer step reading
its own unavailable outputs. Its removal retains downstream fail-closed scope
checks; existing scope-selection controls pass. Stable Mathlib additionally
requires `fieldEqGens` to be noncomputable; its mathematical definition is the
same set.

All original failed proof attempts and complete local verification inputs are
retained locally with digests. Published evidence is scoped to public source,
compact reports and relevant checks. No all-history or cryptanalytic advantage
claim follows from this retrofit.
