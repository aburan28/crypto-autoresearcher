# Prospective second review round for the concrete Semaev witness

The earlier [three-joint round](../BATCH-semaev-concrete-20261031/review-plan.yaml) produced useful source, Lean and blind finite-model evidence, but its committed plan fails the [independence checker](../../../problems/semaev-concrete-review-independence-plan-invalid.md). This is a new plan, frozen before any new reviewer dispatch. It does not relabel the earlier reports or treat their attestations as if they were made under this plan.

This round keeps the exact source claim at commit `ad91212179e737d829076ca593d608261590ba89` and the 14 input hashes in `input-bindings.json`. `blind-input.yaml` is byte-identical to the first round's result-free parameter card. New native `TASK-*` IDs were allocated and checked free across the repository before use.

Three independent joints are assigned: source/archive binding (J1), named Lean type and meaning (J2), and a blind derivation from the parameter card (J3). The J3 reader must receive only `blind-input.yaml` and governance until its report, raw values and read attestation are frozen. The complete claim-changing synthesis requires the declared false-case controls and an exact `check_review_independence.py` pass on all new attestations.

A structural preflight of `check(review_plan, [])` reports only the four expected missing-attestation findings, one for each joint and the assigned blind reviewer. That is not an independence pass. Dispatch, blind-history hygiene, machine receipt checks, report archival and the final diagram/PDF remain future work. No scientific experiment or local Lean build is started by this plan.

## Blind isolation

The ordinary `main` history fails the protected-literal history check: commit `15522cd58` exposes two recorded outcomes. J3 must therefore clone only `blind-snapshot.bundle` into a new directory and must not fetch or inspect `main` until its blind report is frozen. The bundle has a single neutral commit `e0bd0ab45882cd65a3de481b45c15ad5447ea844`, six tracked files (the result-free card, task text and governance), no remote and no producer source or prior review. `check_blind_history('HEAD', protected_hashes(batch.yaml), repo=isolated_snapshot)` returned zero findings for six declared values; the bundle verified as a complete Git history. Its SHA-256 is `953d984272eb185b681b05361a50549adaa96c649f12a393411a785eb08eaf7e`. An independent reviewer must record its actual reads and computed results; this packaging check is not their verdict.
