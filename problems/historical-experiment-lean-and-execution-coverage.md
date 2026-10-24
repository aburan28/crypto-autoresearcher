# Historical experiment claims lack complete Lean and execution coverage

- **Status:** open
- **Kind:** proof gap, semantic-review gap, execution-evidence gap
- **Affected work:** [October 24 three-repository sheriff case](../research/sheriff/SHF-20261024-46b7da/REPORT.md), [formal target registry](../formal/targets), and the [execution-proof-chain problem](execution-proof-chain-not-enforced.md)
- **Next action owner:** Coordinator for claim-by-claim inventory and handoffs; independent Validator for theorem meaning and run evidence
- **Last updated:** 2026-10-24

## Problem

The existing Lean targets verify selected mathematical declarations, while the historical crypto, cryptanalysis and auto researcher records contain many more experiment and run claims. There is no complete source-bound mapping from each claim to a theorem with reviewed premises, nor from its claimed observation to independently verified execution. The requested conclusion that every past result is valid and proved therefore remains unestablished.

Mathematical identities, curve properties and cost inequalities can have Lean statements. A measured runtime, sampled success count or hardware result additionally needs a frozen workload, complete raw evidence, a checked computation or execution certificate, and an independent interpretation of the units and controls. A theorem over recorded numbers alone cannot establish that the numbers were measured as claimed.

## Evidence and uncertainty

- **Observed:** At auto researcher `4647b1d072ffaebbbb85127bdc60343bbd372ec4`, the [source inventory](../research/sheriff/SHF-20261024-46b7da/scripts/source-inventory.json) counts 2,753 `EXP-` directories and 3,726 run IDs. The [exact-link audit](../research/sheriff/SHF-20261024-46b7da/scripts/formal-claim-link-audit.json) checks all 84 target specs, byte-identical Lean sources, machine-verification receipts and 29 distinct source files. Those specs and sources explicitly name five experiment IDs and five full run IDs; each named run has a source-hashed manifest. No run ID appears in a target spec. Textual pointers do not prove theorem meaning or run execution.
- **Observed:** The pinned crypto corpus has 617 `ecbench.session/v1` directories. The [status correction](../research/sheriff/SHF-20261024-46b7da/scripts/ecbench-status-correction.json) finds 590 complete-status bound integrity passes, 13 interrupted-status bound checks for retained records, ten interrupted unbound archives and four declared-complete pilots lacking required inputs. These are archive checks, not fresh timing measurements.
- **Observed:** A subsequent [BINSTD per-target replay](../research/sheriff/SHF-20261024-46b7da/scripts/binstd-per-target-replay.py) at the pinned published head used each amended run's archived authority commit and reconstructed all 160 target points. Its four source-hashed receipts reproduce the recorded tau/open counts 16/40, 40/40, 20/40 and 40/40 with a separate exhaustive pair-sum EC oracle and triple witnesses for each hit. The archive stored aggregate results, so the replay cannot compare to an original per-target trace or certify the original host's timing.
- **Observed:** The sheriff inventory counts 335 top-level cryptanalysis experiment directories. Six named theorems in two selected cryptanalysis chains were rebuilt and axiom-inspected; the complete 94-file native proof gate and statement-fidelity review remain open in the [case report](../research/sheriff/SHF-20261024-46b7da/REPORT.md).
- **Derived:** The 84 checked target declarations cannot, by count or textual reference, certify all historical results. The exact coverage denominator for individual scientific claims across the three repositories has not yet been constructed; directory and run counts are inventories, not a proof-coverage percentage.
- **Suspected explanation:** none required. Missing claim mapping, semantic review and execution verification are observed gaps.
- **Missing capability:** a cross-repository claim ledger with exact artifact hashes, theorem obligations, assumption checks, experiment/run citations, execution verdicts and independent reviewers; a full native cryptanalysis proof gate; the required execution-proof integration.
- **What this evidence does not establish:** a false theorem, a refutation of every historical result, a complete inventory of claims, or an ECDLP speedup.

## What would unblock it

- [ ] Enumerate every historical claim-bearing record at fixed source heads in all three repositories. Bind its exact source bytes and identify whether it is mathematical, computed, measured or interpretive; record omitted and inaccessible artifacts rather than inferring validity.
- [ ] For every mathematical claim presented as proved, bind a Lean statement to the exact source claim, prove it under pinned toolchains, audit axioms and forbidden constructs, test non-vacuity or negative controls where applicable, and obtain independent review of the theorem's meaning and premises.
- [ ] For every empirical or execution claim presented as valid, verify the frozen workload, inputs, complete raw outputs, replay or execution certificate, controls, cost accounting and source/run hashes under the applicable validation gate. Preserve interrupted and missing-input statuses.
- [ ] Publish a machine-checkable claim-to-theorem-to-run matrix with no unreviewed row called validated; complete the 94-file cryptanalysis native gate and reconcile all open sheriff findings before any universal validity statement.

These conditions are necessary for the requested full-scope conclusion. Individual passing claims may be reported at their exact scope while the full matrix remains open.

## Next discriminating step

- **Action or proof obligation:** use the existing BINSTD experiment `EXP-BINSTD-8bdf86` as the first end-to-end claim row. The four deterministic per-target replays now match the archived aggregate counts. Independently review the source-version and EC arithmetic assumptions, seek an original per-target execution trace if one exists, and compare the verified counts with the exact premises and interpretation of conditional `YieldCeiling.lean` and the separate x17 product theorem.
- **Inputs and controls:** the pinned experiment specification, four archived arms, frozen target list, positive known-answer EC checks and a deliberately altered observation that the validator must reject. Existing receipts are preserved.
- **Execution limits and stop condition:** first audit the committed bytes; a new scientific run requires its own frozen protocol, admission and budget rules. Stop promotion if any target lacks a replayable oracle or exact input.
- **Outcomes and next actions:** reviewed arithmetic and theorem premises can close only the computational BINSTD claim at their stated scope; original host execution and timing need their own evidence. A discrepancy yields a scoped correction; missing evidence keeps the corresponding part unverified; infrastructure failure is retained without a mathematical inference.
- **Recheck trigger:** a new source-bound claim matrix, native proof receipt, independent semantic review or execution certificate.

## Resolution and history

Unresolved. The October 24 sheriff case now separates interrupted ecbench sessions from completed ones, adds exact theorem/source/run pointers, and retains four deterministic BINSTD per-target replays. None proves every historical experiment.
