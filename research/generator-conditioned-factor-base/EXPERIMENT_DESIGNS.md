# Generator-conditioned factor bases — pre-registration draft
Date: 2026-10-19
Status: DESIGN ONLY. Requires Coordinator approval/frozen protocol before canonical experiment execution. No result is asserted.

## Common definitions and reproducibility
E/F_p: y^2=x^3+Ax+B, discriminant nonzero. Use prime-order E(F_p) for initial trials; later use verified prime-order subgroup and reject off-subgroup points. P generator, Q=[x]P unknown to solver. F subset E(F_p)\{O}. R=[a]P+[b]Q with a,b uniform modulo n and b nonzero. For each fixed Q and P, uniform a ensures R uniform; pre-register PRNG seeds 20261019, 20261020, 20261021, 20261022, 20261023. Keep x hidden from solver and avoid using target logs to manufacture relations.

Curve cohort: discover deterministic first 10 nonsingular prime-order curves with 97<=p<=509, n>=80, sorted by (p,A,B); then 10 in 509<p<=4093 where feasible. Freeze actual curve identities, subgroup order, factor base, solver versions, and hashes before timing. Run at least 5 seeds per curve/arm; randomize arm execution order. For algebraic timing compare at identical p, curve, F, target R and hardware.

Definitions: hit(R,F,m)=1 if R equals sum of m points of F (with repetitions allowed, explicit sign convention). H_F(R)=number of ordered m-tuples in F^m summing to R. Rank=rank over Z/nZ of accumulated verified relations (including Q coefficient), after removing exact duplicates and endomorphism-orbit dependencies. Record median, p95, memory, timeout count, setup, construction, per-relation CPU seconds, full-rank time, and estimated total cost. Record exact counts separately from solver success rates.

## EXP-GCF-01: planted-generator null control
**Claim tested:** enforcing P=A+B+C raises success for R=P but not for uniform R with fixed F.
**Arms:** C0 fixed coordinate-restricted F and arbitrary generator; C1 same F and conditioned P in 3F; C2 same F and arbitrary generator with matched sampled targets; C3 deliberately biased targets R=[k]P with small k (positive leakage control, excluded from attack claims).
**Procedure:** enumerate F and every ordered triple, build exact H_F over all R; select P from nonzero 3F, and distinct control P'. Evaluate all R=[k]P for k=0..n-1 and [k]P'. Assert histograms identical. Repeat seeded Q,a,b.
**Acceptance:** exact equality is required; any inequality is a bug or changed F/target distribution. Planting must yield H_F(P)>=1. The experiment cannot demonstrate a speedup.

## EXP-GCF-02: jointly designed F(P) versus matched controls
**Claim tested:** an efficiently constructible generator-dependent F(P) yields lower *total* cost per independent relation for uniform R than a generator-independent F.
**Arms:** F0={T:x(T) in S} for frozen S; F1(P) formed from a preregistered coordinate condition anchored to x(P), with |F1|=|F0|; F2 a size-matched random subset; F3 known-log small multiples [k]P (trap control).
**Procedure:** generate F(P) using only public P, curve parameters, and frozen randomness; forbid using x=log_P Q or conditioning on test targets. Freeze bases before generating Q. Test m=2,3,4 on independent R; exact census at toy sizes and solver-based discovery beyond census range.
**Metrics:** base-construction time, number of distinct factor-base points, target hit probability, decomposition discovery time, rank per CPU-hour, full-system solve cost. For F3 count its target-dependent relation search cost rather than free planted equations.
**Decision:** candidate only if replicated reduction in setup-inclusive total cost, not just hits at P. Stratify by |F| and subgroup membership.

## EXP-GCF-03: f4 algebraic specialness persistence
**Claim tested:** choosing P with a guaranteed f4 root changes generic target polynomial solving degree or cost.
**Arms:** conditioned P in 3F; random P; matched conditioned target R=P (positive control); independent uniform R (primary); random permuted x_R (diagnostic, not necessarily a curve point).
**Procedure:** build f3 over F_p and f4 via resultant, impose x_i in S via vanishing polynomials or enumerate coordinate restrictions as appropriate; verify f4 roots by lifting y signs and checking A+B+C=R. Use identical Sage/Singular polynomial order, solver version, CPU, timeouts, and targets; log GB degree profile, maximal degree, intermediate term count, memory, CPU/wall time. Record any preprocessing that uses P and charge its cost.
**Primary outcome:** paired difference in CPU seconds per verified independent target relation for independent R, with failures included as censored. A speedup only for R=P falsifies the persistence mechanism.
**Caveat:** f4(x1,x2,x3,x_R)=0 encodes a zero sum up to signs; x-coordinate roots alone are insufficient.

## EXP-GCF-04: endomorphism-equivariant F
**Claim tested:** a nontrivial efficient endomorphism phi with phi(P)=[lambda]P can reduce independent relation collection costs when F is phi-stable.
**Inputs:** small curves with independently verified explicit phi and lambda; reject trivial +/-1-only symmetry as primary cohort; phi(F)=F.
**Arms:** orbit-closed F, same-size randomly sampled F, and orbit-closed F with symmetry processing disabled.
**Procedure:** for each verified relation R=sum F_i, transform under phi; canonicalize orbit; measure raw relation count versus rank; deduplicate and charge orbit enumeration, map evaluation, and linear algebra. Hold group order and target distribution fixed.
**Success:** reduction in setup-inclusive cost to full rank, not merely more orbit-derived rows. If only dependent rows grow, null.

## EXP-GCF-05: whole-pipeline scale gate
**Claim tested:** any positive mechanism survives end-to-end accounting as p increases.
**Inputs:** only constructions passing EXP-GCF-02 or 03 or 04; use same fixed solver/hardware with >=3 increasing field sizes, frozen seeds, independent Q.
**Cost:** T_total=T_curve_and_generator_search + T_base + T_precompute + T_relation + T_filter + T_linear_algebra + T_target_descent. Report amortized and one-target totals separately; use the best verified same-size baseline from repo, plus rho estimate with stated model. Show gap to rho and uncertainty; do not claim transfer to P-192/P-224 without complexity proof.
**Stop:** stop individual runs at preregistered per-run watchdog and RAM limit; classify as censored, never as mathematical failure.

## Statistical/reporting plan
Paired target sets within each curve/arm; exact counts where feasible. For timing, report per-curve paired ratios, bootstrap 95% intervals across target instances, and seed-level variability; distinguish descriptive toy trends from asymptotic evidence. Minimum 5 independent seeds and 10 curves in first cohort, except where deterministic enumeration yields fewer (disclose). Log excluded instances and reasons. Never optimize thresholds on evaluation targets; reserve held-out seeds 20261024 and 20261025 for replication.

## Implementation and review gates
1. Coordinator approves exact instance list, metrics, stopping rules, and baseline revision.
2. Executor creates immutable specifications and implementations in experiments/EXP-...; preserves environment, git SHA, command, raw outputs, stdout/stderr, and failures.
3. Validator independently replays exact group-law and f4 lift/sign checks, and checks histograms and ranks.
4. Reviewer challenges selection bias, unknown-log leakage, and total-cost omissions.
5. Coordinator alone transitions hypothesis status; proposal itself grants no status change.

## Proof obligations
- Prove fixed-F generator invariance under uniform target sampling (elementary permutation argument).
- Identify an algebraic property that persists for generic x_R rather than a single planted x_P; otherwise treat H2 as unsupported.
- Demonstrate any endomorphism-derived equations contribute new rank or measurable computational savings after quotienting.
- State whether any improvement is curve-specific, subgroup-specific, solver-specific, or truly asymptotic.

## Suggested artifact schema per arm
JSON: curve{p,A,B,n}, generator_coordinates, factor_base_definition, factor_base_hash, target_seed, hidden_target_commitment, m, algorithm, solver_version, git_sha, hardware, construction_seconds, relation_seconds, linear_algebra_seconds, total_seconds, peak_rss_bytes, target_count, hit_count, verified_relation_count, independent_rank, timeouts, invalid_lifts, verdict_scope. Avoid storing the secret scalar in solver-visible inputs; validator may retain it in sealed test metadata.
