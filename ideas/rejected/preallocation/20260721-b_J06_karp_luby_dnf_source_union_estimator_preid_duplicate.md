# Pre-ID duplicate draft — Karp–Luby–Madras DNF source-union estimator

## Status and claim labels

- Prospect: `20260721-b-J06`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: randomized_approximate_counting / conservative / conservative pre-ID screen.
- State: merged_rejected_supplied_DNF_and_approximate_count.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: no dispatchable contract.
- Labels: all finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; an FPRAS estimate, accepted sample, or valid relation is not an ECDLP result.

## Falsifiable hypothesis

Represent endpoint-conditioned source existence as a compact union of source cylinders in DNF, decide restricted emptiness by a charged exact term-consistency scan, and use Karp–Luby–Madras estimation/sampling on nonempty restrictions to return one exact signed tuple with complete cost below rho and BSGS.

## Mechanism-new operation

The native operation samples a supplied DNF term and assignment with overlap correction to estimate union size. It counts only if the DNF is derived from endpoints without listing source cylinders, a charged exact term-consistency scan decides emptiness, and KLM sampling returns a source occurrence from each nonempty restriction; sampling a supplied formula is a control.

## Assumptions

1. One frozen target-parametric DNF schema is endpoint-derived once, while every target-specific term, literal, weight, sampler, and restricted rebuild is constructed and charged online.
2. Term consistency, counts, overlap evaluations, and samplers are computable without enumerating source tuples.
3. Exact emptiness is decided by a charged consistency scan over the instantiated terms, while sampling reaches singleton and rare nonempty fibers with charged confidence.
4. Accepted samples lift to labelled factor-base occurrences across all strata.
5. Relation density, dependence, and fresh-target coverage remain favorable after retries.

## Semantic fingerprint

`public_endpoint_source_DNF | Karp_Luby_Madras_overlap_corrected_sampling | restricted_union_mass_estimate | accepted_assignment_to_signed_occurrence | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact negative answers and replay are required.
2. `ideas/rejected/ECDLP-IDEA-079_zero_free_partition_conditioning_hypothesis.md` — approximate partition conditioning lacks exact rare-source return.
3. `ideas/rejected/ECDLP-IDEA-200_hypergraph_container_relation_router_hypothesis.md` — unions/containers consume represented source sets.
4. `ideas/rejected/preallocation/20260720-a_E02_minhash_bottomk_source_resemblance_preid_duplicate.md` — samples estimate supplied set overlap rather than exact emptiness.
5. `ideas/rejected/preallocation/20260721-a_I05_sensitivity_coreset_source_fiber_preid_duplicate.md` — uniform rare-singleton coverage can force source-sized support/state and still lacks labelled replay.

## Closest primary literature

- Karp, Luby, and Madras, [Monte-Carlo approximation algorithms for enumeration problems](https://doi.org/10.1016/0196-6774(89)90038-2), gives relative approximation for a supplied DNF/union representation.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), does not give a compact source-cylinder DNF.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source constructs the ECDLP DNF and term-consistency machinery or elliptic occurrence replay; application novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, source cylinders, restrictions, charts, sampling seed policy, and verifier.
2. Construct the target-independent schema from endpoints only, then charge each target's DNF instantiation, total literal scan, term weights/samplers, overlap evaluations, and every adaptive restricted rebuild in online work.
3. For known-log targets, make at most `5 ceil(log_2 B)+O(1)` restricted queries, require exact nonemptiness semantics, sample and replay a labelled tuple, and verify point equality.
4. Collect at least `max(d_FB+32,1000)` verified rows, charge misses/dependencies, require rank `d_FB`, and solve factor logs.
5. Reuse unchanged state for `Q+[t]P`, recover a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and independently verify `[x]P=Q`.
6. Charge DNF construction, term counts, each sample, overlap checks, confidence amplification, negative queries, replay, rank, logs, descent, bit time, and memory.

## Full rho/BSGS cost model

Charge only the frozen target-independent schema in `a,a_m`. Charge each target's `T_DNF(R)+L_R+sum_j(T_count(j)+T_sampler(j))`, every restricted rebuild, all term-consistency and overlap evaluations, the optimistic `O(m*epsilon^-2*log(1/eta))` sample count, retries, and replay in `q,q_m`; `L_R` is total instantiated literal traffic. For `beta=1/5`, density exponents `delta,delta_t`, rank credit `r`, output `o`, ambiguity `u`, and log costs `ell,ell_m`, charge `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, total sampling failure `<=2^-80`, and `lambda,mu<=0.45`; rho/BSGS are `0.50`.

## Likely fatal obstruction

The estimator assumes an explicit DNF and term samplers; these are source incidence in another syntax. For an explicit DNF, exact emptiness is available by scanning for a consistent term and the Karp–Luby–Madras coverage guarantee samples even a singleton in time polynomial in the explicit formula size. That does not remove the obstruction: constructing and scanning a source-sized DNF pays the missing traffic. An implicit endpoint schema lacks the explicit-set coverage guarantee and still needs a restriction-stable term-consistency oracle and samplers—the original predicate in new syntax. Overlap correction returns an assignment only after a source-bearing term is supplied.

## Proof track

Construct a compact endpoint DNF, prove exact zero certification and lower-bounded positive mass under all restrictions, and bound source sampling, rank, and descent.

## Disproof track

Trace each instantiated term, literal, consistency test, overlap evaluation, and sampler to source data; compare the polynomial-in-explicit-size KLM path with an implicit schema and charge full formula construction plus scan traffic.

## Positive and negative controls

- Positive: supplied DNFs with balanced terms, known union size, and labelled satisfying assignments.
- Negative: empty formulas, one rare assignment, heavily overlapping terms, duplicate sources, adversarial restrictions, and fresh targets.
- Baselines: exact DNF scan, MinHash, coresets, hypergraph containers, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Promote only with an endpoint-only reusable schema, charged per-target terms/literals/samplers, exact consistency semantics, four sizes, zero false decisions, sampling failure at most `2^-80`, full rank, 100 fresh descents, both caps, and `lambda,mu<=0.45`. Falsify on supplied terms, hidden target-specific construction, source-sized formula/scan traffic, lift failure, or exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-b/j06_dnf_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-b/j06_union_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-b/j06_cost_analysis.md`

## Interpretation boundary

This rejects the exact source-oracle transplant, not the Karp–Luby–Madras estimator. Finite results remain toy, heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record to an independent `review-xhigh` Red Team; do not construct or run an experiment.
