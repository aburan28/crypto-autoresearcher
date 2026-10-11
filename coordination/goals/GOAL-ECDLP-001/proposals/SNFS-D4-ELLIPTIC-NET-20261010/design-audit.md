# Design audit: SNFS-D4 elliptic-net kernel lattice

## Decision record

- **Idea:** `IDEA-20261009-8d09c0`
- **Goal:** `GOAL-ECDLP-001`
- **Proposal:** `SNFS-D4-ELLIPTIC-NET-20261010`
- **Task:** `T-977`
- **Fencing epoch:** `1`
- **Current idea status:** `proposed`
- **Audit disposition:** keep `proposed`; no approval; no dispatch
- **Priority:** medium, conditional on the repairs below
- **Claim ceiling:** finite correlation measurement only. This audit does not support an algorithmic, asymptotic, smoothness, independence, or cryptanalytic claim.

This is a design audit, not an experiment result. It records no run, timing,
zero count, mutual-information estimate, smoothness statistic, or solution.
No idea, experiment, or goal status is changed by this file.

## Audit basis

The audit is bounded to the idea and the following named materials:

- `KN-TECH-009`
- `KN-OPEN-005`
- `experiments/EXP-ECDLP-COORD-EXPANSION-001/development/ELLIPTIC-NET-BLOCK-ZERO-V1/analysis.md`

Those materials are treated as design context and prior-art context, not as a
substitute for the missing controls or for a future independent measurement.

## Novelty classification

The proposed ingredients do not have a single novelty status:

1. **Elliptic-net/kernel-lattice representation — prior.** Encoding elliptic-net or related recurrence information and studying an integer kernel/lattice is a prior representation pattern. The proposal must name the exact new object, map, or reduction if it intends to claim novelty beyond that representation.
2. **HNF zero-lattice validation — preflight.** Computing or checking a Hermite-normal-form description of an integer kernel is a correctness and boundary preflight. It can establish that the implemented lattice and its finite enumeration agree; it is not itself a new attack or an independent cryptanalytic measurement.
3. **Cross-prime mutual-information test — distinct measurement successor.** A preregistered cross-prime dependence test can be a distinct successor measurement, provided its variables, null model, estimator, holdout, and multiplicity policy are frozen before observation. It must not be presented as implied by the representation or as evidence of a transfer mechanism without a validated map.
4. **Dickman smoothness study — split required.** Smoothness is a separate statistical/modeling question with separate objects, assumptions, controls, and artifacts. It must be removed from the zero-lattice/MI contract and specified as a separate addendum.

## Mathematical and protocol defects

### 1. A finite box is not the full integer lattice

Intersecting a kernel with a bounded coefficient box produces a finite sample
of lattice points, not the full lattice. A zero found or missed in that box
does not establish the rank, saturation, index, basis, or absence of other
integer relations. The HNF must be computed from the exact integer map and
checked against the chosen basis, with the finite box treated only as a
separately parameterized enumeration window. Any conclusion must state the
box, norm, boundary convention, and what is and is not inferred outside it.

### 2. Sparse zeros are an expected null outcome

The expected number of exact zeros can be small because of the map's rank,
the dimension of the sampled coefficient region, residue constraints, and
the chosen normalization. A sparse or empty zero set is therefore compatible
with the null model and is not by itself evidence of structure, dependence,
or an attack. The preflight needs a shaped null object and an expected-count
calculation or simulation plan before interpreting zero density.

### 3. Subgroup image is not the full group order

The recurrence or point sequence is generated from a specified point and
therefore probes an image/subgroup (and possibly a quotient or coordinate
projection), not automatically all of `E(F_p)`. Knowing or measuring the full
group order does not identify the order of the sampled point, the image of the
map, the index, or the coordinates used by the zero predicate. The protocol
must bind the point, subgroup order, cofactor handling, image definition, and
zero predicate, and must not replace those with the full group order.

### 4. One fixed integral model and good reductions are mandatory

Cross-prime comparisons require one fixed integral model and a fixed integral
input description. Its discriminant and every reduction used by the test must
be checked for good reduction. The protocol must record the reductions of the
same points and parameters, exclude bad primes before measurement, and state
whether a reduction changes the subgroup, denominator domain, or recurrence
branch. Switching models or silently accepting a bad reduction can create
prime-dependent behavior that is indistinguishable from the proposed signal.

### 5. Denominator, normalization, and p-factor leakage are unresolved

The protocol must define whether net values are represented as rational
values, cleared integers, projective coordinates, valuations, or normalized
residues. Clearing denominators and rescaling can introduce factors of `p` or
other prime-dependent factors; valuations and exceptional denominators can then
make a zero test or MI statistic leak the prime by construction. The repair
must freeze a normalization, track denominators and p-adic valuations, test
equivalent rescalings, and include a leakage control in which the prime label
cannot be recovered from representation artifacts alone.

### 6. CRT independence is unjustified

Different reductions of a common integral model are not independent merely
because their residue fields have different characteristics. They share the
same model, inputs, recurrence, coefficient box, seeds, and often the same
integer numerator/denominator before reduction. Any CRT or product null must
state the random variables and prove or test the required independence claim;
otherwise it must be described as a shared-source correlation measurement.
CRT reconstruction also needs an explicit modulus, lift range, and failure
rule rather than an implicit independence assumption.

### 7. The MI measurement lacks bias, power, holdout, and multiplicity controls

Mutual information is estimator-dependent and biased at finite sample sizes,
especially for sparse or discretized variables. The successor must freeze the
variable definitions, binning or estimator, bias correction, permutation or
other null calibration, sample-size/power target, and minimum effect size. It
must reserve an independent holdout set, avoid selecting the estimator or bins
after looking at outcomes, and correct for every tested prime pair, window,
normalization, subgroup, and statistic. A point estimate without a calibrated
interval or a prespecified decision rule is descriptive only.

### 8. Stopping rules and seeds are inconsistent unless frozen in advance

The same stopping rule, sample budget, seed schedule, coefficient-box rule,
prime-selection rule, and failure handling must apply to observed and null
objects. Optional stopping after a promising zero or MI value invalidates the
nominal error rate. Seeds must be recorded per replicate and separated between
development, calibration, and holdout data; a rerun with a changed seed is a
new observation, not a silent confirmation.

### 9. The Dickman smoothness model is unsupported in this contract

The Dickman heuristic cannot be applied without first defining the exact
integer whose smoothness is measured, its size parameter, the smoothness
bound, the factor-base policy, and the range in which the approximation is
being used. Shared factors, algebraic construction, denominator clearing,
conditioning on zeros, and cross-prime reuse can all violate the independence
and size assumptions needed for a Dickman comparison. The proposed zero/MI
design does not establish those assumptions. Smoothness must therefore be a
separate addendum with its own nulls, controls, and claim ceiling.

## Bounded repair path

The idea is repairable only as three separately reviewable deliverables.

### A. Zero-lattice preflight

Specify the fixed integral model, exact integer map, point and subgroup image,
good-prime filter, denominator/normalization convention, p-factor leakage
control, HNF computation, saturation/index checks, finite-box definition, and
expected sparse-zero null. The output is a preflight record that says whether
the implemented finite enumeration is consistent with the declared lattice.
It does not promote the idea or establish a cryptanalytic effect.

Required future artifact:
`coordination/goals/GOAL-ECDLP-001/proposals/SNFS-D4-ELLIPTIC-NET-20261010/zero-lattice-preflight.yaml`

### B. Cross-prime MI successor

After the preflight is accepted, specify the cross-prime variables and shared
source, null construction, estimator and finite-sample calibration, power
target, independent holdout, seed schedule, stopping rule, and multiplicity
correction. Report a finite-scope correlation result with uncertainty and all
negative or inconclusive outcomes. Do not use it to infer CRT independence,
full-group behavior, smoothness, or an algorithmic gain.

Required future artifact:
`coordination/goals/GOAL-ECDLP-001/proposals/SNFS-D4-ELLIPTIC-NET-20261010/mi-successor.yaml`

### C. Smoothness addendum

Define the integer object, exact bit-length/size measurement, smoothness bound,
factor-base and denominator policy, conditioning rules, null comparison,
Dickman applicability range, and independent validation. This addendum must
have a separate experiment identifier and separate analysis artifact; it may
not inherit conclusions from the zero-lattice or MI work.

Required future artifact:
`coordination/goals/GOAL-ECDLP-001/proposals/SNFS-D4-ELLIPTIC-NET-20261010/smoothness-addendum.md`

## Coordinator disposition and next action

Keep `IDEA-20261009-8d09c0` **proposed**. Do not approve it, dispatch it, or
change any hypothesis, experiment, or goal status. Rank it medium only after
the author supplies the three bounded contracts above and the Coordinator
confirms that each is runnable and has a separate review boundary.

**Next action:** record the repair requirement in the Coordinator queue; when
the three artifacts exist, review the preflight first, then create the bounded
MI successor and independent smoothness addendum as separate handoffs.

**Exact future command (not run by this audit):**
`python3 tools/research_dispatch.py --ready-only`

The command may be used only after the Coordinator has approved runnable
handoffs. Until then, the exact future artifact path for this audit remains:
`coordination/goals/GOAL-ECDLP-001/proposals/SNFS-D4-ELLIPTIC-NET-20261010/design-audit.md`.
