# ECDLP-IDEA-044 — p-adic stationary-phase witness extraction

## Status and claim labels

- Class: `algorithm`
- Risk band: `high-risk`
- State: `proposed_unapproved`
- Evidence scale: `toy` preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an exponential-sum identity, count, critical point, or valid relation is not a break.

## Falsifiable hypothesis

For a generic ordinary prime-field curve and a frozen algebraic factor-base indicator,
the target-conditioned elliptic addition exponential sum has a uniformly sparse family
of nondegenerate `p`-adic critical strata. A stationary-phase decomposition enumerates
those strata and Hensel-lifts them to complete factor-base atom decompositions, including
all branches and misses, with relation and separate target-descent time and bit-memory
exponents below `1/2`. The claim is toy, heuristic, model-bound, and novelty-unverified.

## Mechanism-new operation

The proposed operation is **critical-stratum enumeration followed by certified local
witness lifting**. It does not posit low spectral rank (`001`), return only an aggregate
count (`012`), use Cartier syndromes (`020`), change a solver, or compute a dense
resultant. The stationary-phase formula must partition the full target-conditioned
incidence object into explicitly bounded local cells, and each accepted cell must emit
all factor-base atoms. If it estimates only a sum, chooses cells after seeing success, or
invokes the original membership solver within each cell, it merges with `001/012`.

## Assumptions

- `E(F_p)` contains a public prime subgroup `<P>` of order `N=p^(1+o(1))`, with `Q=[x]P`.
- The phase, additive character, factor-base equations, chart cover, and resolution rule
  are frozen without `Q`.
- Degenerate critical loci, singular charts, exceptional denominators, multiplicities,
  and every Hensel branch are retained and charged.
- Atom membership and sum relations are verified independently of the stationary-phase code.
- Cell construction, precision, coefficient size, failed targets, lifting, output, and
  bit memory are included in the cost.
- Toy finite-size scaling remains heuristic and model-bound.

## Semantic fingerprint

`elliptic_addition_exponential_phase | p_adic_critical_stratification | sparse_local_cells | Hensel_complete_atom_witnesses | relation_and_masked_target_descent`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — gives the membership-quotient cost obstruction this operation must remove.
2. `ledger/H-FB-001.yaml` — prevents an algebraic factor-base shape alone from counting as new.
3. `ledger/EV-FB-001.yaml` — supplies the matched yield and structure-invariance control.
4. `ledger/H-REP-001.yaml` — distinguishes local critical extraction from another equation representation.
5. `ledger/SYNTHESIS-20260716.md` — requires full relation, descent, memory, and rho accounting.

## Closest primary literature

- Adolphson and Sperber, [Exponential sums and Newton polyhedra](https://doi.org/10.1090/S0273-0979-1987-15518-2), gives the nearby Newton-polyhedron and nondegeneracy framework.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031.pdf), gives the target addition variety.
- Stevens and de Zeeuw, [An improved point-line incidence bound over arbitrary fields](https://arxiv.org/abs/1609.06284), is a nearby incidence-complexity boundary rather than a witness algorithm.

No checked source supplies an output-sensitive stationary-phase decoder for prime-field
ECDLP decompositions. This is not a novelty proof.

## Complete factor-base-to-target-descent path

- Freeze arity, factor-base equations, affine charts, phase, character normalization,
  precision, and critical-locus resolution.
- Construct the target-independent critical-cell data without materializing all factor-base tuples.
- Process a frozen batch of known-scalar targets `[r]P`; enumerate every critical and
  degenerate cell and Hensel-lift all branches.
- Accept only explicit atoms in the factor base whose sum independently verifies to `[r]P`.
- Collect full-rank rows and solve factor-base logarithms.
- Process `Q+[t]P` with the unchanged cells and precision, recover verified atoms,
  substitute logs, remove `t`, and verify `[x]P=Q`.

## Full rho/BSGS cost model

Let base size `B=N^beta`; target-independent stratification build `N^a`; number of stored
critical-cell/precision bits `N^s`; reciprocal relation and target densities `N^delta`
and `N^delta_t`; and let `N^q_rel` be the **total** cost of processing the complete
`N^(beta+delta)` known-target batch, while `N^q_t` is the total cost of the complete
`N^delta_t` masked-target batch. Both batch exponents include degenerate cells, all Hensel
branches, misses, witness output, and verification.

- Pollard rho: `N^(1/2+o(1))` group operations and `N^o(1)` memory.
- BSGS: `N^(1/2+o(1))` time and memory.
- Critical stratification: `N^(a+o(1))`.
- Complete relation batch: `N^(q_rel+o(1))`.
- Sparse linear algebra: `N^(2*beta+o(1))` time and `N^beta` memory; dense fallback is `N^(3*beta)`.
- Complete target batch: `N^(q_t+o(1))`.

Thus the optimistic sparse time exponent is `lambda=max(a,q_rel,2*beta,q_t)` and full
bit-memory exponent is `mu=max(s,beta)`. A per-cell cost that omits the number of cells,
precision, or branch multiplicity is invalid.

## Likely fatal obstruction

Generic addition phases may have `N^(1/2-o(1))` critical complexity, while the factor-base
indicator can create large degenerate loci. Resolving or lifting those loci may reconstruct
the original degree-`B` membership quotient. Cheap cancellation in the exponential sum
may reveal a count without identifying any atom tuple.

## Proof track

Prove a target-uniform stationary-phase decomposition, a sub-square-root bound on all
critical and degenerate cells, and a complete Hensel witness algorithm. Then prove
relation rank and masked-target recovery with `lambda,mu<1/2`.

## Disproof track

Show critical/degenerate cell count is `N^(1/2-o(1))`, local lifting reconstructs the
membership quotient, counts fail to yield witnesses, or every complete batch-cost fit
has lower confidence bound `lambda>=1/2`.

## Positive and negative controls

- Positive control: a planted nondegenerate phase with known sparse critical points and liftable witnesses.
- Instrumentation control: exhaustive tuple truth through the frozen bit boundary.
- Negative control: random phases with matched Newton polytope and density.
- Mechanism control: ordinary Semaev membership-quotient solving on identical inputs.
- Count-only control: stationary sums without atom witnesses cannot enter promotion metrics.
- Leakage control: blind target labels and reject target-selected phases, cells, or precision.

## Quantitative promotion and falsification gates

The preflight uses ordinary curves at 10–18 bits, arities 3 and 4, at least 24 curves per
size, deterministic factor bases of sizes 16 through 256, exhaustive truth through 16
bits, and three frozen character normalizations. Promotion requires exact exhaustive
counts, zero false accepted witnesses, at least 500 relation witnesses and 100 target
descents per largest completed cell, upper 95% `a<=0.40`, `q_rel<=0.45`, `q_t<=0.45`,
and `lambda,mu<=0.45`. Falsify the scoped hypothesis if any validated count mismatch
occurs, no non-oracle witnesses are emitted, critical-state size has lower 95% exponent
at least `0.50`, or all complete-cost fits have lower 95% `lambda>=0.50`.

## Artifact plan

- Contract: `ideas/contracts/ECDLP-EXP-CONTRACT-044_stationary_phase_witness_preflight.yaml`
- Planned implementation: `ideas/artifacts/ECDLP-IDEA-044/stationary_phase_witness.sage`
- Planned exhaustive oracle: `ideas/artifacts/ECDLP-IDEA-044/exhaustive_truth.sage`
- Planned runs: `ideas/artifacts/ECDLP-IDEA-044/runs/<run-id>/`
- Planned raw cells: `ideas/artifacts/ECDLP-IDEA-044/runs/<run-id>/critical_cells.jsonl`
- Planned analysis: `ideas/artifacts/ECDLP-IDEA-044/analysis.md`

## Interpretation boundary

This is a toy, heuristic, model-bound, novelty-unverified high-risk hypothesis. A correct
sum, low critical count, Hensel lift, relation, or toy scalar is not a breakthrough.
Only complete non-oracle target descent with all batches and memory below rho/BSGS can promote.

## Exactly one next executable action

1. After coordinator approval, execute the frozen stationary-phase witness preflight in `ideas/contracts/ECDLP-EXP-CONTRACT-044_stationary_phase_witness_preflight.yaml` over its complete finite toy matrix.
