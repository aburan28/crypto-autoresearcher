# Pre-ID duplicate draft — Wang–Landau source density of states

## Status and claim labels

- Provisional ID: `PREID-20260723-b-S04`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_energy_bins_and_aggregate_histogram`.
- Class/risk/lane: measurement / high-risk / secondary pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a flat histogram, density estimate, or verified relation is not an ECDLP break.

## Falsifiable hypothesis

An endpoint-only elliptic source energy has a sub-rho number of levels and a Wang–Landau walk can
estimate their density of states while forcing visits to the exact zero-energy relation level.
A charged occurrence lift would then yield full-rank relations and 100 blind descents with
complete time and memory exponents at most `0.45`.

## Mechanism-new operation

Wang–Landau sampling performs an adaptive random walk over supplied energy levels, updating a
density-of-states estimate to flatten the energy histogram. It counts only if endpoints compile
the energy, bins, and moves without source state, convergence/hit bounds are proved, and a visited
zero-energy state replays exact signed occurrences. A histogram over enumerated sources is a
measurement control.

## Assumptions

1. A compact endpoint energy has an exact zero level biconditional with valid relation sources.
2. Energy bins do not merge empty and nonempty fibres or signs/repeated exceptional strata.
3. Adaptive modification, flatness checks, mixing, restarts, and failure probability satisfy caps.
4. Density-of-states information supports a charged exact state/occurrence inverse.
5. Frozen energy/move rules apply to fresh masked targets without target-trained bins.

## Semantic fingerprint

`public_endpoint_discrete_energy | adaptive_flat_histogram_density_update | zero_energy_relation_visit | state_to_signed_occurrence_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260720-d_H08_simulated_annealing_source_energy_preid_duplicate.md` — the useful energy already contains the missing relation semantics.
2. `ideas/rejected/preallocation/20260720-d_H07_metropolis_hastings_source_chain_preid_duplicate.md` — local moves and target ratios still need public construction and mixing bounds.
3. `ideas/rejected/preallocation/20260721-e_M08_misra_gries_source_heavy_hitter_cancellation_preid_duplicate.md` — aggregate frequency state does not preserve rare occurrence identity.
4. `ideas/rejected/preallocation/20260723-a_R04_hutchinson_trace_source_estimator_preid_duplicate.md` — an aggregate estimate can agree while exact supports differ.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact zero/nonzero restrictions and signed replay remain the live owner.

## Closest primary literature

- Wang and Landau, [Efficient, Multiple-Range Random Walk Algorithm to Calculate the Density of States](https://doi.org/10.1103/PhysRevLett.86.2050), adaptively estimates a supplied system's energy density through flat-histogram walks.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations but no compact exact energy or source-state inverse.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic comparison.

No checked source supplies the required energy compiler, zero-level hit theorem, occurrence lift,
or descent. Novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, energy, bins, local moves, modification schedule, flatness rule, restrictions, lift, strata, masks, seeds, and verifier.
2. Compile target-independent energy/move state within `B^(9/4+o(1))`, forbidding source catalogues, target-fitted bins, scalar logs, dense resultants, and Query2P1.
3. For known-log targets, charge every move, rejection, histogram update, convergence epoch, restart, and lift; verify signed point sums before admitting relation rows.
4. Retain all failures/dependencies, collect at least `max(d_FB+32,1000)` verified rows, require rank `d_FB`, and solve all factor logs.
5. Reuse byte-identical eligible state on 100 fresh `Q+[t]P`, visit and lift relation states, subtract masks, and verify every scalar.
6. Charge construction, energy calls, bins, histogram memory, adaptation bias, density, mixing, replay, rank, logs, bit work, and peak state.

## Full rho/BSGS cost model

For `beta=1/5`, let setup/state be `N^a,N^a_m`; reciprocal relation/target
densities `N^delta,N^delta_t`; walk/update/lift work and workspace `N^q,N^q_m`;
rank credit `N^r`; output `N^o`; convergence/failure amplification `N^u`; and
factor-log costs `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, and fresh work/workspace `<=B^(5/4+o(1))`.
Rho expected time and BSGS time/memory remain exponent `0.50`.

## Likely fatal obstruction

The method estimates counts by energy, not the identities of states. Equal density-of-states
histograms can hide different or empty exact source fibres, and a zero-energy visit is meaningful
only after an exact source energy and move graph are supplied. Retaining state identities or an
inverse histogram restores the forbidden source catalogue.

## Proof track

Prove a compact endpoint-only exact energy/move compiler, restriction-uniform zero-level semantics,
subcap convergence/hit bounds, occurrence replay, full rank/logs, blind descent, and sub-rho costs.

## Disproof track

Construct equal histograms with different source support, expose a source-derived energy/move,
show a false zero bin or nonconvergence, lose occurrence identity, or reach complete exponent
at least `0.50`.

## Positive and negative controls

- Positive: a supplied finite energy landscape with labelled zero-energy sources and known density.
- Negative: equal histograms/different supports, rare singleton levels, flat or disconnected moves, empty fibres, repeated strata, shuffled labels, and blind targets.
- Baselines: annealing, replica exchange, trace/frequency sketches, P1553 R4, rho, and BSGS.
- Histogram flatness or a correct density estimate is only toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with exact public energy and replay theorems, zero errors at four sizes/all strata, total miss probability at most `2^-80`, full rank/logs, 100 blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on one equal-histogram source collision, source-bearing energy/move, cap breach, or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260723-b/s04_energy_bin_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260723-b/s04_equal_histogram_cases.json`
- `ideas/rejected/preallocation/artifacts/20260723-b/s04_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the specified ECDLP transplant, not Wang–Landau sampling. A flat histogram, accurate
density, or one verified relation remains `toy`, `heuristic`, `model-bound`,
`novelty-unverified`, and not a breakthrough.

## Exactly one next executable action

1. Enumerate a smallest equal-density-of-states pair with different exact relation support and test whether any endpoint-only energy-bin refinement separates it below source-table size.
