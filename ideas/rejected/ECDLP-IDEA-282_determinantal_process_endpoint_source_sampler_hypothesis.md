# ECDLP-IDEA-282 — Determinantal-process endpoint source sampler

## Status and claim labels

- Class: `algorithm`
- Risk band: `high_risk`
- Top lane: `-`
- State: `merged_rejected_determinantal_kernel_requires_source_support_and_sampling_pays_density`
- Cohort: `20260718-k`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a determinantal sample, nonzero principal minor, valid relation, recovered subset, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

For each ECDLP relation endpoint there is a compact determinantal point-process kernel on signed factor-base points whose supported subsets are exactly valid source decompositions and whose determinant weights concentrate on recoverable witnesses.  Exact DPP sampling would then emit independent relation rows and factor decompositions of fresh masked targets below rho and BSGS.

## Mechanism-new operation

The screened operation is **compile an endpoint-conditioned kernel, use principal minors to assign zero weight to invalid source subsets and amplified weight to valid ones, and sample an exact determinantally distributed subset that decodes to factor points**.  This is a negatively dependent sampling mechanism, not post-hoc selection, explicit large-prime tabulation, or an ordinary polynomial solver.  Standard DPP algorithms assume a positive contraction kernel or `L`-ensemble and can sample after its eigendecomposition; they do not produce a kernel whose support realizes an arbitrary elliptic addition constraint.  A kernel with zero/nonzero principal minors exactly matching every source tuple embeds the hard incidence predicate and may require source-deck rank/state.  If valid subsets retain their baseline mass, sampling merely pays the reciprocal relation or target density; if they dominate, constructing the reweighting is the missing source selector.  The proposal merges with determinant/row-norm, materialized-product, and source-sampler negatives after kernel construction, normalization, output, and rejected draws are charged.

## Assumptions

1. Public source equations and each endpoint canonically determine a Hermitian positive semidefinite contraction kernel or exact `L`-ensemble without enumerating valid factor tuples.
2. Its positive principal minors coincide with valid signed source subsets on every cardinality, multiplicity, and exceptional stratum.
3. Exact sampling and subset-to-ordered-factor decoding have sub-rho cost, ambiguity, and rejection density for both relations and fresh targets.
4. Kernel entries, rank, eigendecomposition, normalization, random bits, rejected samples, subset output, factor logs, descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`prime_field_ECDLP | endpoint_conditioned_DPP_kernel | valid_source_principal_minor_support | exact_determinantal_sampling | factor_subset_return`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator and sampler support oracle.
2. `inputs/ledger_inventory.json` — imported `P1478`, the dense composed source-state frontier.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1426-MATERIALIZED-PRODUCT-NO-PROMOTION`, the materialized source-product control.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1428-SHARED-ROW-NORM-NO-PROMOTION`, the determinant/norm aggregate that loses source labels.
5. `inputs/ledger_inventory.json` — imported `ECFG-H674`, the exact witness, factor-log, and fresh-target descent boundary.

## Closest primary literature

- Hough, Krishnapur, Peres, and Virag, [Determinantal processes and independence](https://arxiv.org/abs/math/0503110), develops the probabilistic structure and sampling representation of determinantal point processes motivating the endpoint kernel.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the finite-field source constraints whose valid subsets the kernel support would have to recognize.

No checked source constructs a compact positive determinantal kernel for generic elliptic source fibers or proves density-free exact factor return and descent; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the finite-field instance, source equations, signed factor-base ground set, kernel compiler, DPP normalization and sampler, subset decoder, masks, and verifier.
2. Construct exact endpoint-conditioned kernels for known-log relation endpoints and certify positive contraction, rank, and normalization without enumerating valid source subsets.
3. Draw with the frozen exact sampler, retain every emitted subset and ordering branch, and map accepted samples to exact signed factor points.
4. Verify the resulting relations, collect independent rows, solve every factor log, and verify all recovered logs.
5. Apply the identical frozen kernel compiler, sampler, and decoder to fresh masked targets `Q+[t]P` without post-hoc reweighting or source advice.
6. Retain every sampled witness, return a complete factor decomposition or scalar residue, remove the mask, and verify the reconstructed endpoint.
7. Accept only exact `[x]P=Q`, charging kernel construction and storage, spectral decomposition, normalization, random bits, all rejected/invalid samples, subset ambiguity, rows, factor logs, fresh-target descent, verification, and live memory.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.  Let setup time and memory be `N^a,N^a_m`, factor-base size be `N^beta`, reciprocal relation and target success densities be `N^delta,N^delta_t`, one kernel/sample/subset-return attempt cost `N^q,N^q_m`, independent-rank gain be `N^r`, sampled-subset output be `N^o`, sampler or ordering ambiguity be `N^u`, and factor-log completion be `N^ell,N^ell_m`.  Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every ground-set label, kernel entry, principal-minor or positivity certificate, eigenpair, normalization term, random bit, rejected draw, subset ordering, failed return, row, factor log, verifier step, and live byte is charged.

## Likely fatal obstruction

A DPP is a sampler for a distribution already encoded by its kernel, not a mechanism for discovering an arbitrary constraint-defined support.  Families of ECDLP-valid factor subsets need not satisfy the negative-dependence and principal-minor identities of a determinantal measure.  Forcing invalid subsets to determinant zero requires a kernel whose linear dependencies encode the full endpoint-conditioned source incidence; low rank then creates unwanted zeroes or collisions, while source-faithful rank/state materializes the deck.  Without that support oracle, valid subsets occur only at the original relation/target density, so exact sampling cannot beat the charged density term.

## Proof track

Construct a target-uniform positive kernel of exponent at most `0.45` with exact valid-source support and amplified mass, prove exact subset-to-factor return on every stratum, and certify both complete exponents at most `0.45`.

## Disproof track

Show the valid-subset family violates a determinantal/negative-dependence identity, prove source-faithful kernel rank or state at least `N^0.50`, show kernel compilation imports the incidence oracle, measure unchanged target density, or derive either complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied small projection DPP with a known kernel, exact eigen-sampler, and labelled supported subsets.
- Negative controls: a valid-subset family violating negative association, low-rank kernels with support collisions, random endpoint kernels, kernels fitted after source enumeration, determinant/row-norm aggregates, uniform subset sampling, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires an endpoint-only source-faithful positive kernel and exact sampler of exponent at most `0.45`, exact all-strata subset and factor return, full row rank and verified factor logs, blind fresh-target descent, and complete `lambda,mu<=0.45`.  Invalid support, source-fitted kernels, baseline success density, kernel/output/state at least `N^0.50`, or either exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-282/determinantal_source_sampler_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-282/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-282/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-282/cost_analysis.md`

All four paths are prospective; no artifact root exists and no experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative high-risk algorithm proposal.  Every finite DPP sample would be toy and projections heuristic and model-bound.  A valid determinantal distribution, nonzero minor, relation, or recovered toy subset does not establish a generic-prime ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-282/determinantal_source_sampler_theorem.md` proving a compact exact valid-support kernel with amplified mass or the determinantal-family/kernel-rank/density obstruction.
