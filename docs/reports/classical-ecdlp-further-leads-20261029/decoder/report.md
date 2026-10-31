# Imperfect-predicate recovery: three discriminating decoder leads

2026-10-29 · TASK-20261029-10ac72 · GOAL-ECDLP-e70832 · BATCH-07e7ab.

This is source inspection, symbolic derivation and a proposed empirical design. **No curve panel, old-cohort reanalysis, decoder evaluation, timing benchmark or scientific query was run for this report.** The three procedures below are unimplemented here. Their hypotheses and costs remain to be tested; the completed fixed-circuit study does not close them.

## What is already on record

**Internal, read:** EXP-ECDLP-7c0b1e / RUN-ECDLP-0b7dd5 implemented unlabelled coarse-state transition training, approximate multiview Markov scores, and beam widths 1/8. Its report distinguishes 69 witness cases from the union of 44 target IDs across 12–16 configurations and 54–72 checks per target. That pooled union is not one beam-eight success rate. The proposed radius decoder does not train those transition kernels or assume a projected Markov law.

**Internal, read:** IDEA-20260901-a66d70 already describes the two-sparse-Fourier frequency-ratio route. IDEA-20260904-f68c7f distinguishes known-frequency phase estimation from unknown-frequency discovery and flags its external assumptions. LEAD-EXO-hnp-advice-leakage and H-ECDLP-a4be60 connect coordinate statistics to recovery conversions. Their historical absence-of-bias language is not a new observation about the current fixed Miller circuits. The current working-scope report explicitly separates two failed half-bit truth values on the F23/order17 domain from valid partial recovery. It supplies a reason to measure the remaining structure, not a general guarantee.

**Literature-reported, primary source read:** Akavia, Goldwasser and Safra, *Proving Hard-Core Predicates Using List Decoding* (2003), defines multiplication codes for segment predicates, explicitly includes elliptic-curve exponentiation, and gives query-access list-decoding and heavy-Fourier learning results. Sections 3–5 and 7 were read. The bounded-complex result is Theorem 5; the explicit Boolean running-time bound is Theorem 6. This is established conversion machinery, not a novel ECDLP algorithm discovered here. [Primary PDF](https://www.cs.tau.ac.il/~safra/PapersAndTalks/hardcore.pdf).

The live three-repository search is pinned in sources.json. The crypto HNP correction note also records why numerical failures must not be promoted into curve properties. The cryptanalysis benchmark document distinguishes allocation isolation, A/A calibration and physical-host exclusivity. These documentary reads do not independently reproduce their experiments. Bounded search absence is not a novelty certificate; the knowledge MCP tools were unavailable.

## Lead 1: an exact bounded-error/erasure list

**Derived, conditional.** Let P have odd prime order r, Q=[x]P with x nonzero, and H(s)=0 for 0≤s≤(r−1)/2 and 1 otherwise. Fix L=bit_length(r)+1 and D=2^L. The sequence H(s),H(2s mod r),…,H(2^(L−1)s mod r) is the binary word

    V(s) = floor(D*s/r).

The half-open interval [rV/D, r(V+1)/D) has length r/D<1 and contains at most one canonical integer. For each proposed word V, compute k=ceil(rV/D), retain only 0≤k<r and D*k<r*(V+1), then perform the public equation. In the transformed procedure also retain the known a,b conversion and both original/transformed equations. The strict upper interval check matters: use compute.py::ungated_attempt, not the older constructor.py::conditional_recover helper, which has different interval and undefined handling.

Given e erased positions, enumerate every assignment to those positions and all changes to at most t defined bits. There are at most

    N(L,t,e) = 2^e * sum(j=0..min(t,L−e), binomial(L−e,j))

words. Every word and every empty interval remains charged. Do not stop querying after an erasure: collect the same L public queries as the baseline. Define an erasure cap e_max before data; exceeding it returns a visible capped outcome. No hidden fallback or all-r candidate list is allowed.

If the correct word is within this complete set and no cap prunes it, the public scalar is recovered. Conversely, strict interval uniqueness means a recovered scalar's unique word must have been included. Therefore, for a fixed prepared predicate,

    q_t = #{s∈{1,…,r−1}: errors(s)≤t and erasures(s)≤e_max}/(r−1).

This is a finite conditional identity, not a measured value here. Under a fresh uniform nonzero b and known nonzero a, s=b*x/a mod r is uniform for every nonidentity target. Thus this particular complete-list procedure has the same q_t for every target on the fixed domain. It requires neither independent errors along the trace nor a claim that a mean predictor bias implies q_t. A beam that prunes words does not inherit this guarantee.

**Derived negative control, abstract Z/7 only.** Use L=4, exact H, and flip the fixed error set {2,5}. It is a negation-symmetric, anchor-preserving error set. Its marginal accuracy on nonzero scalars is 2/3. Doubling has cycles {1,2,4} and {3,6,5}; every length-four trace visits an erroneous position. The uncorrected exact-word success is therefore zero, although an independent-flip model with the same marginal error would predict (2/3)^4. This is a hand-derived scalar control, not a claimed public coordinate implementation or an actual curve result.

**Cost obligation.** Record setup S, query work, all word/list construction, integer interval work, every failed branch, scalar conversions, every public check, RNG and memory. A standalone expected retry model is S+E[online]/q_t under independent fresh restart draws; observed batch work per success event is a different quantity. At qhat=0, an empirical ratio is undefined and true q_t is not proved zero.

For t≈ηL, e≈ζL and η/(1−ζ)≤1/2, the list bound has leading exponent ζ+(1−ζ)H2(η/(1−ζ)) in r. A retry exponent and setup/query/verification costs must be added. This is a conditional size calculation, not an observed ECDLP exponent. Constant-radius decoding is small but does not automatically tolerate a constant error fraction as L grows.

### Optional verification reuse, not implemented

Write T=rV+D−1, k=floor(T/D), z=T mod D. Precompute a_j=floor(r*2^j/D), b_j=r*2^j mod D and [a_j]P. Toggling bit j upward changes k by a_j+1_{z+b_j≥D}; toggling downward changes it by −a_j−1_{z<b_j}. A public point can therefore be updated with at most two additions per bit toggle after charged initialization. Both transformed and original verification points need their own correctly converted increments.

A bounded-weight revolving-door traversal could change at most a few bits per word. Its enumerator must be independently checked for completeness, uniqueness and exact count. Scanning all 2^L words to obtain a small Hamming ball would defeat the stated bound. Walking empty intervals still costs work. This is a proposed implementation optimization; it supplies no extra scalar information and no measured improvement.

## Lead 2: noisy half-predicate multiplication codes

**Derived interface; literature conversion.** For every public point R, define F_P(R)=+1 for a defined BIT0, −1 for BIT1, and 0 for UNDEFINED. Fix F_P(O)=0. Never discard, resample or condition away erased answers. With Q=[x]P, query

    g_Q(a)=F_P([a]Q),  a∈Z/rZ.

The comparator code is C_x(a)=(-1)^H(ax mod r). Multiplication by nonzero x permutes the nonzero residues, so its full nonzero-population correlation with g_Q equals the prepared predicate's correlation with the scalar half. Measure

    Delta = Pr(defined and correct) − Pr(defined and wrong),

not accuracy conditional on being defined. Delta and exact-trace recovery q_t are different observables. Under this model the error function can be deterministic and correlated; the necessary distance/correlation and query-access conditions still have to be established for the actual predicate.

The encoding is ternary, hence the relevant stated source result is AGS Theorem 5 for bounded complex-valued functions. Theorem 6 is Boolean; its bound cannot simply be attributed to this ternary implementation without an explicit checked reduction. No such implementation or reduction is supplied here. The same qualification applies to floating Fourier arithmetic and threshold decisions.

## Lead 3: two frequency lists without requiring half ordering

**Derived exact identity, prior internal route.** Keep the same prepared base P, circuit and normalization in

    f(t)=F_P([t]P),   g(t)=F_P([t]Q)=f(x*t mod r).

For the transform convention fhat(alpha)=E_t f(t)*exp(−2*pi*i*alpha*t/r), ghat(beta)=fhat(beta/x). Thus a shared nonzero heavy component gives beta=alpha*x and x=beta/alpha mod r. Recover candidates from the two lists, deduplicate, then publicly verify. Re-preparing an evaluator with base Q changes the function and destroys this identity; that is a mandatory negative control. This identity is valid for any identical fixed public rule, including its undefined mask, but it does not show that a useful heavy component exists or can be found cheaply.

Remove DC from candidate generation. For the odd Miller response on nonzero points, F_P(O)=0 is its natural odd extension and avoids adding an identity delta. This is not a universal spike-removal rule: if a finite-point function is the nonzero constant c, assigning zero at O creates a puncture. Then every nonzero Fourier coefficient is −c/r. The constant/DC-only control must use c at all r residues; separately include the punctured-constant and identity-only-delta controls, whose nonzero amplitudes are |c|/r and |d|/r respectively. Those functions are explicit calibration oracles, not evidence of scalar structure. With bounded outputs of magnitude at most one, require a preregistered amplitude threshold a_min≥1/r+eta_num+eta_est+mu, where eta_num is a justified numerical error bound, eta_est is the learner estimation-error allowance at its declared failure probability, and mu>0 is a fixed margin. Its Fourier-weight threshold is tau=a_min². No validated numerical bound or executable threshold is supplied here; obtaining them is an admission obligation. The same identical identity convention on both f and g preserves the exact dilation relation. Random odd-table controls are truth-aided validator context with construction/table costs; they are not free public attack baselines.

Use tau for Fourier **weight** |fhat|^2 and epsilon for amplitude. The explicit AGS Boolean bound is O(log r * ln^2(1/delta)/tau^5.5); substituting an amplitude epsilon would make that particular dependence epsilon^(-11). This is a warning about the cited bound, not a lower bound on other learners. Unknown-frequency discovery cannot borrow the epsilon^(-2) sampling cost of an already-known-frequency phase estimator. For ternary values, use the bounded-complex theorem's actual implemented query costs rather than claiming that Boolean expression automatically applies.

An initial Z(Q), addition-chain cocycle updates, and repeated-query caching may reduce oracle arithmetic. Every initial chain, precomputation, cache lookup, duplicate query, memory allocation and independent verification remains priced. A dense full DFT or scalar-orbit census is charged diagnostic work, never a scalable decoder or uncharged frequency advice.

## A bounded empirical design to freeze next

The adjacent experiment-design.json is a proposal, not experiment.protocol/v1, approval or execution authority. Its primary procedure is fixed circuit2.a1 with t=1/e_max=2. A complete six-cell factorial uses t in {0,1,2} and e_max in {0,2}; t=0/e_max=0 is the exact matched original reference. The erasure-only and flip-only cells isolate those changes rather than conflating them. This choice is disclosed as informed by the exposed F23 finding. No coefficient, base multiplier, radius, threshold or target-dependent orientation is fitted on confirmation data.

The proposed sequence uses 12 discovery and 12 validation curves, followed by two independently seeded confirmation panels of 12 fresh curves each. Each stage spans 10/13/16-bit prime subgroup orders; (p,j) keys are disjoint across all stages and all previously exposed cohorts. Calibration measures all eight frozen circuit/a arms without turning their maximum into a primary result. Confirmation has 24 curves, 64 public targets and eight fresh blindings per target: 12,288 complete query traces and 73,728 decoder-cell outcomes. The six outcomes share each trace; they are not six independent query samples. The three L values give 172,032 physical predicate evaluations for those traces, before separately counted controls and references.

For calibration, 1,800 uniform nonzero point draws per curve are scored on all eight arms. Across 24 discovery/validation curves there are K=192 correlation cells. For scores in [−1,1], the fixed rule 2K*exp(−m*0.1^2/2)<0.05 gives simultaneous ±0.1 precision under the stated independent-draw model. A true Delta≥0.25 then has at least the declared familywise probability of a positive lower bound; smaller effects remain unresolved at this design. This is precision for each fixed curve, not confidence that another curve has the same Delta. An additional fixed 128 calibration starts per curve/arm supplies trace error and erasure histograms; it is not used to choose confirmation parameters.

Each confirmation curve has 512 independently blinded trace attempts. The planning event scale is q=0.02, not a prediction. The probability of missing every event is (1−q)^512 for a fixed domain under the stated independent restart model. Simultaneous one-sided zero-event upper bounds use alpha/144 for 24 curves times six decoder cells. This detects ordinary finite rates but cannot precisely resolve the sparse 13-bit rates seen previously. Do not pool heterogeneous curves to claim an iid sample of 12,288. Report per-curve estimates, both confirmation panels, and prespecified curve-level summaries. There is no exponent fit.

Controls include A/A traces, scalar-truth-only perfect and deliberately broken oracle channels, independent and clustered errors of matched marginal rate, wrong-root, constant, a structure/coverage-matched null specified with the controls lane, and candidate-budget matched uniform lists. The original procedure and BSGS use the same public targets. BSGS native memory is reported; a separate frozen memory-capped implementation is required before a matched-memory claim. Full arithmetic replay is independent of public-witness verification; timing remains operational unless the isolation/calibration contract independently qualifies it.

**Execution success:** complete planned records, correct controls, independent equations, complete cost vectors and preserved failures. **A scoped informative outcome:** stable differences in error structure or registered recoveries/costs relative to the named reference, reported with uncertainty. **Failure of an implementation:** control, equation, source, isolation, coverage or replay mismatch; this does not reject the mathematics. **An unresolved outcome:** wide intervals, insufficient event rates, threshold/numerical ambiguity or heterogeneous panels. None of these outcomes closes all noisy-predicate or Miller constructions.

## Remaining work

Implement and independently check the radius list and its exact t=0 embedding first. Freeze sampler, exclusion list, point/seed broker, count instrumentation, controls, inference code, source/runtime pins and experiment.protocol/v1 before any future data. Keep candidate and truth-holder processes in separate enforced access domains; this report claims no such isolation has already occurred. The SFT routes need separate learner implementations, numerical/error budgets and priced query plans before admission. The optional floor-carry verifier needs a separate equivalence test before it can replace direct public scalar checks. All proposed leads remain open to empirical investigation at their stated scope.
