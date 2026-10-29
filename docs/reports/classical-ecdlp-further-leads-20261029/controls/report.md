# Controls for public Miller predicates and their decoders

2026-10-29. TASK-20261029-7958b2, BATCH-07e7ab, GOAL-ECDLP-e70832.

This is a source-grounded derivation and prospective experimental design. It includes one disclosed F11 software check, not a new scientific cohort, reanalysis of the completed cohort, timing benchmark, or scientific conclusion. The existing fixed-circuit study is discovery context. No direction is closed and no hypothesis status changes here.

## What must be distinguished

A public scalar witness establishes that one proposed answer works. It does not identify why the procedure found it, establish a population recovery probability, validate an error independence assumption, or qualify its cost. The next studies should distinguish:

1. Exact implementation equivalence of the existing and incremental procedures.
2. A change in costs under identical inputs and output traces.
3. Recovery from imperfect predicates under a specified decoder and list limit.
4. Attribution of a predicate pattern beyond oddness, anchoring, coverage and coordinate covariance.
5. Replication on a prespecified fresh population.

The primary algorithm comparison is the current working `compute.py::ungated_attempt` procedure versus the proposed new procedure. Working BSGS and uniform-candidate arms remain additional references. The historical early-exit `constructor.py::conditional_recover` is not the actual fixed-L study procedure.

## Derived covariance: fixed coefficients already transport

Take a nonsingular short Weierstrass curve over F_p, p>3, with an odd prime-order subgroup of order r different from p. For u nonzero let

`phi_u(x,y)=(u^2*x,u^3*y)`, `a'=u^4*a`, `b'=u^6*b`.

Use the source convention that the chord/tangent coefficient is its affine slope and is zero for identity/vertical additions. Then `lambda'(phi_u R,phi_u S)=u*lambda(R,S)`. The normalized Miller coefficient recurrence consequently gives

`Z'(phi_u R)=u*Z(R)`.

This also follows from the Laurent parameter: `t'=-x'/y'=u^-1*t`, so the first normalized coefficient has weight +1. Write `c=Z(P)/y(P)` and

`g(R)=Z(R)+c*y(R)*(alpha+beta*c*(x(R)-x(P)))`.

Then `c'=u^-2*c`, `c'*(x'-x(P'))=c*(x-x(P))`, `g'=u*g`, and `anchor'=(1+alpha)*Z(P')=u*anchor`. The normalized character input is unchanged with **the same alpha and beta**. Zeros, setup failures caused by zero quantities, and the identity convention also transport under a valid isomorphism. For a ready arm with nonzero anchor, bit/status/reason and the complete scalar recovery trace must transport. Coordinate values with weight +1 are compared after applying that weight, not by raw integer equality. Counter values are not claimed invariant.

An earlier draft mixed the forward and inverse coordinate conventions and suggested changing beta. That was incorrect. Under the inverse convention `x'=u^-2*x,y'=u^-3*y`, the corresponding weights are `Z'=u^-1*Z,c'=u^2*c`; `c*dx` is still invariant. This correction is a derived source check, not an independent review of the new producer reports.

**Known-answer software check, actual exit code 0.** On the already disclosed F11 curve `y^2=x^3+x+6`, r=13, P=(2,7), the already disclosed point 2P=(5,2), u=2 and `(alpha,beta)=(1,-4)`:

| Quantity | Original chart | Correctly transformed chart |
| --- | ---: | ---: |
| Curve (a,b) | (1,6) | (5,10) |
| P | (2,7) | (8,1) |
| 2P | (5,2) | (9,5) |
| Z(P), c | 3, 2 | 6, 6 |
| Z(2P), g(2P), anchor | 3, 10, 6 | 6, 9, 1 |
| Normalized g, bit | 9, 0 | 9, 0 |

The deliberately wrong rule `beta'=u^2*beta` gives normalized value 5 rather than 9, while the bit remains 0. A bit-only comparison misses this error. The actual software check command and exact output are embedded in `experiment-design.json` under `known_answer_software_check`; it imported only current public `constructor.py` and `curve.py`, with bytecode writes disabled. It generated no new curve or target and evaluated no cohort panel.

## Compatible control hierarchy

Let M be the defined/undefined mask on the subgroup for one fixed ready arm. On nonidentity points, Z and g are odd. Since p=3 mod4, `chi(-1)=-1`, so defined bits obey `B(-R)=1-B(R)`. The mask is symmetric under negation. The anchor enforces `B(P)=0,B(-P)=1`; identity is separately fixed to bit 0.

| Control | What it preserves | What it can test, and what it cannot |
| --- | --- | --- |
| A/A full recomputation | Inputs, schedule, full answers and source path | Detects transport/state/bookkeeping errors; no mathematical attribution. |
| Public anchored wrong-root circuit | A valid coordinate root, oddness and anchor under its stated domain | Shows that those properties do not imply scalar ordering. It does not match candidate holes or circuit costs. |
| Odd-anchor random function | Negation and anchor | Descriptive shape reference only; the historical 16-function family does not match coverage or covariance. |
| Odd-anchor plus exact candidate mask | Negation, anchor and all candidate undefined locations | Separates labels from that fixed coverage pattern under an explicitly synthetic conditional random-function model. |
| Same mask-matched assignment transported across charts | Above constraints plus the specified public isomorphism covariance | Validates transport compatibility. Any function can be transported this way; this alone supplies no scalar-order information. |
| Error-placement stress controls | A declared error/erasure count, with IID-like versus clustered placement when feasible | Tests dependence assumptions used by a decoder. Truth-aided controls are validator-only. |
| Full identical cocycle primitive, same g formula | Every primitive addition identity | Degenerate: it reproduces the same primitive and predicate. It cannot be presented as a nontrivial randomized null. |

**Exact compatible null size, derived.** Let D be the number of defined nonidentity unordered pairs `{R,-R}`. The anchor pair is defined for a ready arm. Fix the mask and assign one fair orientation bit to each of the D-1 other defined pairs; fill its negative by complementation. There are exactly `2^(D-1)` assignments. If D=1 the family is a singleton; if setup is undefined, retain an all-undefined control and do not invent a valid anchor. A nonsymmetric mask or undefined anchor invalidates this construction and must be reported. This is a validator reference function, not an unpriced public scalar solver. Enumerating a table, lazy random-function storage, hashing/PRNG assumptions, mask evaluation and lookups must be declared and charged to the appropriate control instrumentation.

Covariance is compatible by choosing one assignment on a reference chart and transporting it. Do not redraw a hash of each chart's raw coordinates: that is a different function. In the pointed odd-order setting, a curve automorphism fixing a nonidentity generator fixes the entire subgroup, so no conflicting subgroup labels arise from its stabilizer. Broader models or point families require their own stabilizer check. Isomorphic copies are repeated views of one curve, never independent curves.

**Why the full-cocycle null is degenerate, derived.** If Z1 and Z2 have the same full cocycle and normalization, their difference is additive. For every subgroup point, `r*(Z1-Z2)(R)=(Z1-Z2)(rR)=0`. Since r is invertible in F_p, the difference is zero. This uses the full stipulated identity; it is not a new proof that a candidate implementation satisfies it. Requiring the same Z primitive and same g recipe therefore leaves no sign randomization. Demanding only binary covariance is much weaker and does not create this degeneracy.

Joint arm controls need an explicit coupling rule. Independent random functions per arm do not match the actual shared Z, anchors or base relations. One primary fixed arm avoids pretending to have a joint familywise null; additional arm-wise references remain separately labeled. Selecting the best null seed, base, circuit or chart is prohibited.

## Dependence and statistical interpretation

For a uniformly blinded nonzero scalar s, doubling is a permutation modulo odd r. If eta is the unconditional one-query probability of either a wrong bit or an erasure, the fixed L trace's all-correct probability q0 satisfies the elementary bounds

`max(0,1-L*eta) <= q0 <= 1-eta`.

No independent-bit assumption is used. The often-assumed `(1-eta)^L` requires an additional joint error law. Error sets concentrated along doubling cycles and dispersed sets can have the same eta but different trace recovery. A null that conditions on being defined must not be compared with an unconditional solver denominator. Report coverage, correct/wrong/erased rates, trace error/erasure histograms, and the actual capped decoder outputs separately.

A conditional random-function ensemble is a proposed model, not a theorem that random elliptic curves induce exchangeable signs. Synthetic reference percentiles are descriptive unless that null model and its invariance assumptions are explicitly adopted and justified. [Hemerik and Goeman (2018), Sections 2–3](https://arxiv.org/pdf/1411.7565) require an appropriate transformation group and null distribution invariance for their random-permutation guarantees; a convenient constrained shuffle does not automatically qualify. Include identity, declare replacement and ties, and do not use a randomization group whose action leaves the target statistic unchanged as evidence for a mechanism.

For an applicable exchangeable Monte Carlo construction with m simulated references, use the conservative tie-inclusive rank `(1+# reference statistics >= observed)/(m+1)`, rather than a possibly zero fraction. Its assumptions and discreteness must be retained; [Phipson and Smyth (2010), Sections 4–6](https://gksmyth.github.io/pubs/PermPValuesPreprint.pdf) and Hemerik–Goeman address different sampling details. This report authorizes no p-value for the current ECDLP observations. If valid marginal tests are later preregistered, multiplicity correction must cover the full tested family; a joint max-statistic method additionally needs the actual joint null coupling.

## Proposed independent confirmation and isolation

A concrete proposed observational panel is 128 fresh distinct (p,j) curves: 32 each in 10-,13-,16-,19-bit prime-subgroup strata, excluding every prior discovery/validation curve. Eligibility, proposal cap and failure behavior must be locked before sampling. Feasibility and a proposal-cap refusal remain design/operational matters, not negative mathematics. Keep the two existing circuits and four public multipliers unchanged. Primary contrast: fixed `circuit2.a1` versus its exact-mask odd-anchor descriptive reference, with all seven other configurations secondary; the currently observed favorable F23 domain stays labeled discovery data. Proposed per-curve workload: 64 fixed public targets, four independent public blinding values per target, 1,023 complete reference functions (or a separately frozen resource-justified alternative), with no adaptive null count or stopping. These numbers are a proposed design, not a frozen or admitted protocol.

The generalization unit is the curve, with generators, targets, restarts, paired charts and null functions nested below it. Report each curve's candidate/reference contrast and its distribution; increasing attempts or null functions does not increase the number of independent curves. A 128-curve panel is descriptive: for a contrast in [-1,1], the distribution-free 95% mean half-width bound is `sqrt(2*ln(40)/128)`, about 0.24. It does not promise to resolve a small gain. A future confirmatory size must be computed from the frozen precision/effect target and justified model; for example half-width 0.05 under that bound requires at least `ceil(2*ln(40)/0.05^2)=2952` independent curve draws. Sampling distinct curves without replacement needs its appropriate finite-population justification rather than an unexamined IID claim. Fixed-curve blinding uncertainty and population-of-curves uncertainty are separate.

Use `public/curves.jsonl`, `public/targets.jsonl`, `public/query-schedule.json`, and public domain certificates as the candidate input allowlist. Keep `private/targets.truth.jsonl` and `private/target-generation.seed` in a checker-owned 0700 directory, inaccessible to the candidate UID. A public target-generation seed leaks a target scalar whenever generation uses `Q=[s]P`; it must not be confused with a public blinding/query seed. Do not pass truth in arguments, environment, inherited file descriptors, filenames, target ordering, logs or model-fitting state. Candidate processes run without the truth mount or credentials, with network disabled and closed inherited descriptors. Before measurements, candidate-UID probes must demonstrate denial for the truth files and checker process environment, and an allowlist/parser check must reject extra target columns. Failed probes stop the trial as an isolation failure.

Each arm starts in a separate fresh process/work directory, with explicit cache/setup policy and matched public schedules. A/A replay and reordered/interleaved target checks detect state contamination and stale caches. No candidate may retain truth-derived or sibling-arm state. Independently verify all returned scalars, all planned outcome IDs and the full trace semantics. Preserve operational failures, undefined results, capped lists, zero successes and source/input binding errors distinctly.

Measure setup, optional per-target preparation, every failed/successful query, list generation, public conversion and both public checks, scalar/RNG/field/group costs, memory and common fixture work. Report success events and unique-target coverage separately. A repeated-trial model may use `S_curve+T_target+E[C_online]/q` only under its stated restart law and with q uncertainty; the observed batch cost per success event is a separate descriptive quantity. Source-emitted counters require independent operation replay before an advantage is qualified. Runtime comparisons require a separately qualified isolation/clock plan. Correct witnesses and custody hashes establish neither qualification.

## Boundaries carried forward

The 2026-10-24 transfer lead's planned implication from a marginal 1/p-rate observation to closure is stronger than that observation would justify. It does not settle joint structure, a different coordinate circuit, or a decoder. The older HNP lead's statement that no measured log-bit advantage exists is a dated portfolio premise, not a current universal result. Neither phrase is adopted here. The prior records remain unchanged.

Next concrete check: independently challenge this control construction and the incremental prototype, then freeze a source-bound paired experiment with exact query/witness equivalence and the proposed control hierarchy. A trace mismatch resolves an implementation question. A null mismatch resolves a stated reference comparison. A scientifically valid zero or inconclusive effect preserves the tested boundary and leaves the remaining leads explicit.
