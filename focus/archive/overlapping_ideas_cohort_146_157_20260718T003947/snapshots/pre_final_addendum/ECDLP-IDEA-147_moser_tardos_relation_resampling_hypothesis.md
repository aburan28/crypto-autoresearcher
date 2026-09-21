# ECDLP-IDEA-147 — Moser–Tardos relation resampling

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `rejected_rare_satisfaction_not_local_bad_event_avoidance`
- Cohort: `20260718-a`
- Evidence scale: paper mechanism audit only; no experiment ran
- Contract posture: rejected archival record; no execution contract
- Scale labels: every prospective finite test is `toy`; complexity projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; termination, a valid tuple, or a relation is not an ECDLP break.

## Falsifiable hypothesis

Five factor-base leaves and projective addition intermediates can be exposed as independent random variables with locally checkable bad events satisfying a constructive Lovász Local Lemma criterion. Moser–Tardos resampling would then terminate at an exact target decomposition, with enough source-complete relations and blind masked-target decompositions to beat rho and BSGS.

## Mechanism-new operation

The proposed operation is **endpoint-conditioned witness-generating resampling**: identify one violated local addition or membership event, resample only its dependency neighborhood, and retain the final exact leaf assignment. It is not generic random tuple sampling or a solver substitution. It is mechanism-new only if the bad-event family and violation oracle are public and local before a satisfying source is known.

## Assumptions

1. `E/F_p`, `<P>`, `N`, `Q`, and a public factor base `F` of size `B=N^beta` are frozen.
2. The projective five-source addition chain has a target-uniform product probability space and a bounded-dependency family of public bad events.
3. Event probabilities and dependencies satisfy an explicit asymmetric LLL witness with no conditioned completion oracle.
4. A violated event is located and resampled without enumerating source completions or using hidden scalar labels.
5. Termination returns an exact signed tuple, including repetition and infinity cases, rather than only a relation-existence certificate.
6. Restarts, failures, random bits, event checks, output, rank, factor logs, blind descent, verification, and memory are charged.

## Semantic fingerprint

`elliptic_addition_chain_events | endpoint_conditioned_Moser_Tardos_resampling | public_local_violation_oracle | terminating_exact_source_assignment | masked_target_reuse`

The removal test is an LLL-valid local event system for the actual rare endpoint condition. A supplied completion predicate or global endpoint resampling is the original source search.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `P1434`, the unresolved public source-fiber generator that a violation oracle may silently assume.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H676`, which asks for a public pair/four-sum source generator transposed across the relation batch.
3. `ledger/FINDING-PF-IC-001.md` — imported `P1476`, the conditional five-term query boundary that any resampling schedule must satisfy.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1477`, where complete serial-`S3` states densify and do not expose a cheap local completion rule.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1471`, where altered occupancy does not provide the needed cycle/rank advantage over controls.

## Closest primary literature

- Moser and Tardos, [A constructive proof of the general Lovász Local Lemma](https://doi.org/10.1145/1667053.1667060), construct witnesses by resampling avoidable bad events but do not convert rare elliptic endpoint satisfaction into such an event family.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), gives the neighboring relation equations but no LLL resampling oracle.

No checked primary source supplies the required rare-satisfaction conversion. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,Q,F,B,beta`, random-variable domains, event scopes, dependency graph, resampling table, masks, and verifier.
2. For a public endpoint `R`, initialize the declared product distribution and expose only public locally violated events.
3. Resample dependency neighborhoods until termination, then decode the final leaf assignment to an exact signed factor-base tuple.
4. Verify every tuple by curve membership and direct elliptic addition; retain restarts, misses, false outputs, and ambiguity.
5. Repeat identically on known `R_j=[r_j]P` until `B+sigma` verified rows have rank `B`.
6. Solve and independently verify all factor-base logarithms.
7. Run the same resampler on fresh `Q+[t]P`, substitute logs, subtract `t`, and enumerate every candidate.
8. Accept only `[x]P=Q` and report complete operations, random bits, output, time, and peak memory.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` expected time with constant state; BSGS costs `N^(1/2+o(1))` time and memory. Let `B=N^beta`; event-system construction cost `N^a,N^a_m`; reciprocal relation and target densities `N^delta,N^delta_t`; one complete resampling/source query `N^q,N^q_m`; output and ambiguity `N^o,N^u`; and factor-log linear algebra `N^ell,N^ell_m`. The complete exponents are

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

With `beta=0.20` and constant densities/output, promotion needs `q<=0.25`. Uniform random five-tuples hit one fixed group target with probability about `1/N`, so unstructured resampling costs `N` per accepted tuple before the relation campaign.

## Likely fatal obstruction

The endpoint equation is rare satisfaction, not avoidance of sparse bad events. Encoding mismatch as one event gives probability near one and violates the LLL criterion; splitting it into local events either loses equivalence or requires a conditioned completion/violation oracle that is the missing source generator. Resampling then degenerates to random tuple search or dense serial-state propagation.

## Proof track

Construct an equivalent bounded-dependency event family, prove an LLL witness and public violation oracle, bound expected total resamplings and exact source output, and carry the bound through rank, factor logs, and blind descent.

## Disproof track

Prove that every equivalent event family contains a high-probability or high-dependency target event, that local violation detection solves P1434 completion, or that expected resampling work is `N^(1/2)` or larger after full campaign costs.

## Positive and negative controls

- Planted bounded-degree LLL instances with known Moser–Tardos termination.
- Elliptic instances supplied with a completion oracle, labelled strictly as inadmissible positive controls.
- Uniform random tuple rejection sampling with exact `1/N` endpoint probability.
- Dense serial-`S3` propagation and generalized-birthday baselines.
- Known-log and blind unknown-log targets with matched rho and BSGS accounting.

## Quantitative promotion and falsification gates

This mechanism is rejected at the rare-satisfaction/source-oracle boundary. A fresh ID requires an explicit equivalent event family with a frozen asymmetric or lopsided witness assignment, at most `B^1.25` expected complete work per target for `beta=0.20`, `100%` exact-source recovery and `0` false outputs on exhaustive fixtures, and complete `lambda,mu<=0.45`. Falsify on a proved dependency-graph obstruction or failure of every preregistered witness assignment, a conditioned completion oracle, one source miss, or complete time or memory exponent at least `0.50`; the symmetric expression `p(1+d)` alone is not a general LLL criterion.

## Artifact plan

- Scoped LLL audit: `ideas/artifacts/ECDLP-IDEA-147/resampling_lll_scope_audit.md`
- Event schema: `ideas/artifacts/ECDLP-IDEA-147/event_schema.md`
- Frozen fixtures: `ideas/artifacts/ECDLP-IDEA-147/fixtures.json`
- Independent verifier: `ideas/artifacts/ECDLP-IDEA-147/independent_verifier.py`
- Complete cost receipt: `ideas/artifacts/ECDLP-IDEA-147/cost_analysis.md`

All paths are prospective; no run or experiment artifact exists.

## Interpretation boundary

This is rejected, novelty-unverified algorithm evidence. Any finite test would be toy, and all scaling claims remain heuristic and model-bound. Termination or a correct tuple would prove only scoped functionality, not a generic ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-147/resampling_lll_scope_audit.md` deriving the event probabilities, dependency degrees, and hidden completion-oracle boundary for the frozen five-source schema without implementing a resampler.
