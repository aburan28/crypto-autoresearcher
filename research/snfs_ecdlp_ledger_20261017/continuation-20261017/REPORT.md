# Continuing the SNFS leads — 2026-10-17

This round advances E3 implementation, reconciles D1 candidate inputs and prepares additive admission. It creates no scientific approval, rank result, speedup claim or hypothesis transition. The original 23 full campaigns remain incomplete. The preceding tracking PR, [#2382](https://github.com/aburan28/crypto-autoresearcher/pull/2382), merged at `fd49e52ff70a859a09febf52112f3cfae0ec9455`; this continuation starts from those immutable records.

## E3: a denominator-inclusive system and a complete-kernel check

**Implemented, fixture-checked:** [section_encoding.py](e3-projective/section_encoding.py) constructs coefficient equations for `Y²=X³+A X Z⁴+B Z⁶`, with monic-denominator charts, finite Bezout saturation, infinity primitivity, smooth affine targets and identity targets. It treats `D` as an encoding degree, not a canonical height. Its primary variable count is `5(D+chi)+e+2`, before saturation auxiliaries. Every chart and degree contributes to a future search workload; polynomial sections alone are insufficient. [Detailed conventions](e3-projective/README.md).

**Implemented, fixture-checked:** [kernel_recovery.py](e3-projective/kernel_recovery.py) verifies supplied integer-coordinate images and relations, requires full rank and integer index exactly `ell`, calibrates the quotient against the supplied generator, and verifies the final scalar. A proper full-rank sublattice is refused. Finding the sections, their coordinates, and enough relations remains unimplemented; this verifier is not an efficient attack.

The [13 deterministic fixture checks](e3-projective/fixture-checks.json) pass, including the rational section obtained by doubling `(1,t)` on `y²=x³+t x+t²-t-1` over `F_31(t)`, identity specialization at finite and infinite base parameters, and an explicitly known-answer order-19 group over `F_17`. Sage's separate group-law implementation checks the doubled-section formula. These are software fixtures, not the E3 scientific campaign or independent claim-tier review. Earlier import/setup and singular-target development failures remain in separate logs.

**Next discriminating protocol:** freeze the surface before selecting random/planted targets; bind the model's actual minimality/height convention; include all denominator charts and auxiliary variables; measure coverage separately from counts. The complete-operation boundary must include construction of the system, solving and censoring, section verification, integer-coordinate recovery, relation independence/index, quotient solving and final scalar verification. Match controls to actual equation degrees and variable counts. Charge generator discovery/setup and separate oracle access. No blind solver measurement was performed this round.

## D1: the separate 30-point candidate is now located

**Source reconciliation and exact arithmetic:** [two public source snapshots](d1-inputs/fetch-record.json) supply 30 and 31 indexed rational coordinate pairs. The parser checks nonsingularity and all 61 curve-equation memberships using exact rational arithmetic. The rank-31 model and points match the archived ICARM snapshot exactly. [Prepared inputs and limitations](d1-inputs/README.md), [literal checks](d1-inputs/input-reconciliation.json), [two refusal controls](d1-inputs/parser-refusal-controls.json).

These checks certify equation membership only. The earlier rank campaign's validator and red-team reports retain the numerical-regulator limitation and correct the executor's erroneous factor-10^10 discrepancy. No certified interval Gram matrix, saturation certificate or new independence proof was created. The next D1 obligation is a reproducible matrix constructor with height conventions and error treatment, followed by an approved finite count/coverage workload for the actual generated subgroup.

## Admission and runtime: narrower, concrete obligations

**Engineering proposal:** the [additive admission prototype](../../../coordination/design/SNFS-ADDITIVE-ADMISSION-20261017/README.txt) passes 28 synthetic fixtures. It preserves original source/scientific fields, separates fresh retry identities, binds predecessor failures and exercises refusal cases. It is isolated from production admission and does not authorize a run. Production integration, explicit additive-plan selection, exact committed amendment approval and live published ownership remain necessary.

**Observed readiness:** a network-enabled [native Codex doctor](../../../coordination/design/SNFS-ADDITIVE-ADMISSION-20261017/native-doctor-readiness.json) returned zero and reported authentication/HTTP reachability working, with a WebSocket warning. No inference/session probe ran. This refines the older configured-API credential observation; it does not verify a model or this session. The exact-session probe still needs a supported genuine SQLite/rollout persistence route with scoped writable paths and exact metadata checks. Home variables, model bindings and scientific authority were not changed.

E3 and D4 admission refusals and the G1 infrastructure failure remain unchanged. Their next runs require the concrete integration and authority steps above; this round does not overwrite, relabel or duplicate them. `problems/experiment-preapproval-readiness-cycle.md` and `problems/prime-field-arity3-relation-oracle.md` carry the updated obstruction evidence.

## Record and limits

The diagram distinguishes fixture-checked components from missing solver/coordinate stages. Existing canonical graphs, original reports, imported hashes, proposal statuses and the original terminal receipts remain unchanged because there is no new reviewed scientific finding. KB retrieval tools were unavailable in this session; the report cites the actual inspected repository artifacts and fetched source bytes, and makes no literature-novelty claim. No deployed-key recovery or NFS sieving occurred. There is no quantitative attack-cost or performance claim.
