# Pre-ID duplicate draft — Count–Min source-frequency sketch

## Status and claim labels

- Prospect: `20260719-d-D02`; no canonical ECDLP idea ID was allocated
- Class / risk / lane: `streaming_frequency_sketch` / `conservative` / pre-ID screen
- State: `merged_rejected_supplied_stream_and_one_sided_frequency_collisions`
- Evidence: complete ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: none
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`; Breakthrough claim: **none**

## Falsifiable hypothesis

Hash public partial-sum endpoint events into a Count–Min array and use one-sided frequency estimates across dyadic restrictions to distinguish zero from nonzero target-label support. Conservative updates and stored XOR satellites would replay one signed source tuple for relation collection and fresh blind descent below rho and BSGS.

## Mechanism-new operation

Count–Min takes coordinatewise minima across nonnegative hashed counters to estimate point frequencies. It counts only if the event stream is endpoint-derived without enumerating source incidences and if exact zero/nonzero support plus point ancestry survives collisions; sketching an explicit relation stream is a control.

## Assumptions

1. Every valid signed source tuple emits a public target-label event without an explicit tuple enumerator.
2. Hashing, counter updates, collision probability, restrictions, zero tests, satellites, replay, rank, logs, descent, bit time, and memory are charged.
3. A one-sided estimate is exact at zero for all adaptive restricted queries and identifies an occurrence when positive.
4. The same frozen hashes and arrays serve known-log and fresh scalar-blind targets.
5. No false-positive cleanup table, post-hoc selector, dense target vector, or source-provided stream is admitted.

## Semantic fingerprint

`endpoint_event_stream | Count_Min_hashed_nonnegative_counters | exact_restricted_zero_test | collision_free_occurrence_satellite | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-P1553-ZR-R4`: exact restricted existence rather than approximate frequency is required.
2. `inputs/ledger_inventory_20260719.json` — imported `ECFG-H675`: a compact endpoint-to-source circuit remains missing.
3. `inputs/ledger_inventory_20260719.json` — imported `ECFG-H676`: source generation cannot be assumed as the input stream.
4. `inputs/ledger_inventory_20260719.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`: explicit streamed events cross the source boundary.
5. `inputs/ledger_inventory_20260719.json` — imported `ECFG-NR-1479`: compact public features have not supplied factor-log recovery.

## Closest primary literature

- Cormode and Muthukrishnan, [An improved data stream summary: the Count–Min sketch and its applications](https://doi.org/10.1016/j.jalgor.2003.12.001), estimates frequencies from a supplied update stream and permits positive collision error.
- Charikar, Chen, and Farach-Colton, [Finding frequent items in data streams](https://doi.org/10.1007/3-540-45465-9_29), is the occupied CountSketch-style aggregate control, not an exact source constructor.
- Semaev's [summation-polynomial paper](https://eprint.iacr.org/2004/031) supplies endpoint equations; Shoup's [generic lower bound](https://www.shoup.net/papers/dlbounds1.pdf) supplies the baseline.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, charts, event definition, hashes, counters, restrictions, and verifier.
2. Build target-independent sketch state within `B^(9/4+o(1))` without enumerating relation events.
3. Answer exact restricted existence and replay five labelled occurrences for known-log targets.
4. Collect at least `B` independent verified rows and solve factor-base logarithms while retaining failures and dependencies.
5. Reuse unchanged state on fresh scalar-blind `Q+[t]P`, recover and verify a tuple, remove `t`, and verify `[x]P=Q`.
6. Charge all stream construction, hashes, updates, negative queries, collision cleanup, output, rank, logs, descent, bit work, and peak memory.

For explicit scalar semantics, write each recovered factor-base occurrence as `A_i=[alpha_i]P` with sign `epsilon_i in {+1,-1}`. A known-log relation target `R=[kappa]P` yields the checked row `sum_i epsilon_i alpha_i = kappa (mod N)`. Source replay uses at most `5 ceil(log_2 B)+O(1)` charged positive-parent/negative-child restriction queries plus singleton checks. For a fresh masked target `R=Q+[t]P=[x+t]P`, a verified tuple yields `x=sum_i epsilon_i log_P(A_i)-t (mod N)`; the final check is `[x]P=Q`. Every failed restriction branch and scalar verification is charged.

## Full rho/BSGS cost model

Let `a,a_m` be the charged time/state exponents for endpoint-event construction, every Count–Min update, counters, hashes, and satellites; let `q,q_m` cover one target/restriction, including any target-dependent updates, collision cleanup, bisection, and replay. Let `delta,delta_t` be reciprocal verified relation/target-success densities after collisions, `o` the emitted-row exponent, `r` verified independent-rank credit, `u` ambiguity plus collision-failure amplification/rebuild cost, and `ell,ell_m` factor-log time/state.

For `B=N^beta`, `beta=1/5`, use `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, with `0<=r<=o`. Setup/state must be `<=B^(9/4+o(1))`, total fresh online construction/restriction/replay/verification `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`; rho time and BSGS time/memory are exponent-`0.50` controls. A supplied update stream is charged in `a` or `q`, never free input.

## Likely fatal obstruction

Count–Min begins with the update stream, which is already source incidence here. Nonnegative collisions preserve zero only for buckets that receive no unrelated events; a point estimate can be positive when the queried target label is absent. Making false positives impossible for all restrictions or attaching exact satellites restores a perfect source dictionary. This merges with IDEAs `053/191/347/380`, pre-ID `B11/C11`, and P1553 R4.

## Proof track

Construct the event stream endpoint-only and prove collision-free exact zero tests plus occurrence replay for all restrictions within the caps.

## Disproof track

Give two source streams with the same Count–Min arrays but different restricted support, or expose any source-enumerating update generator.

## Positive and negative controls

- Positive: a supplied nonnegative stream with isolated keys must reproduce exact planted frequencies and satellites.
- Negative: colliding absent/present keys, equal sketches with different rare sources, arbitrary restrictions, exceptional charts, and blind targets.
- Baselines: IDEAs `053/191/347/380`, pre-ID `B11/C11`, exact dictionaries, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only updates, zero false positives/negatives in every restriction, exact replay, `1,000` independent rows, `100` blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on one supplied update, one colliding support mismatch, target rebuild, cap violation, or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260719-d/d02_stream_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260719-d/d02_collision_controls.json`
- `ideas/rejected/preallocation/artifacts/20260719-d/d02_cost_analysis.md`

## Interpretation boundary

This rejects exact-source use of Count–Min, not its streaming guarantees. A small error bar or correct toy count is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/rejected/preallocation/artifacts/20260719-d/d02_stream_provenance.md` and expand every proposed update into the endpoint or source data needed to emit it.
