# BATCH-037 verbatim input capsule

Relay this file verbatim to one Idea Generator. It is the complete authorized
task input; do not substitute the stale goal-record next action or any
uncommitted BATCH-036 draft.

## Objective

For a prime-order subgroup `<G> ⊂ E(F_q)` of order `r`, let `N=r-1`, let
`α` be uniform in `F_r*`, and let the ordinary ECDLP input be
`G,Q=[α]G`. Track one explicitly represented, generically finite algebraic
correspondence `C_d ⊂ E×E`, for an exactly stated family with `d|N` and
`d=N^(1/2+o(1))`.

Either:

1. construct and publicly certify `Z=[α^d]G` with fully charged expected
   single-instance acquisition plus downstream solve exponent below `1/2`; or
2. prove a named obstruction for the exact representation class and state
   forward guidance naming what the proof does not cover.

One tracked object and one proof candidate only. No experiment or
implementation.

## Durable authority

- DEC-20260802-209 at BATCH-034 synthesis commit
  `63f32893fd308df2427357eb851912645d738b2d` selected this lane.
- CORR-20260802-002 and DEC-20260802-211 at
  `1f2095c9c104b34ef5dd7792f47c1b6f6829e041` superseded the contradictory
  BATCH-035 controls before any worker ran.
- TASK-20260802-236 in that same commit records live-probed exact OpenAI
  bindings: `research-deep → gpt-5.6-sol/high` and the later independent
  `review-adversarial → gpt-5.6-sol/xhigh`, without fallback or degradation.
- BATCH-033 TASK-213 named EI-213-04 as an open non-generic escape interface;
  it did not instantiate a construction.

## Known downstream baseline

Cheon's DLP with auxiliary input is prior art. It assumes
`G, [α]G, [α^d]G` with `d|(r-1)` and costs
`O(sqrt((r-1)/d)+sqrt(d))`; balanced downstream time is
`N^(1/4+o(1))`. Ordinary ECDLP input does not provide `[α^d]G`. The batch's
entire question is whether the auxiliary point can be acquired and certified
cheaply enough that the complete composed exponent is below `1/2`.

Primary source:
https://www.iacr.org/archive/pkc2012/72930594/72930594.pdf

Do not claim novelty for Cheon's route, for generic nonlinear-target hardness,
or for standard facts about elliptic-curve morphisms.

## Exact representation obligations

Define `C_d` by explicit equations, a circuit, or another checkable finite
description. State:

- base field, curve, subgroup, input and output encodings;
- normalization and irreducible components used;
- projections `π1,π2` and exact generic degrees `b1,b2`;
- ramification and every exceptional fiber relevant to success;
- setup and any advice, including whether it depends on `α`;
- evaluator, fiber enumeration, branch selection, and failure behavior;
- certificate object and a verifier that does not reconstruct the hidden
  answer by doing omitted rho-scale work;
- success probability for a fixed instance and across any declared randomness;
- all time, memory, data/query, and preprocessing costs.

The output must be `Z=[α^d]G`. It may not be supplied as auxiliary input,
hidden in alpha-dependent setup, or obtained from an undeclared nonlinear
oracle.

## Mandatory ordered control 1 — functional graph rigidity

First isolate any component or branch that gives a rational map `E ⇢ E`.
State the exact hypotheses under which this is true.

Stacks Project Lemma 53.2.2, tag 0BXZ, says rational maps from a normal curve to
a proper variety extend to morphisms:
https://stacks.math.columbia.edu/tag/0BXZ

Milne 1986, Corollary 2.2, supplies the translation-plus-homomorphism structure
for morphisms of abelian varieties under its stated hypotheses:
https://www.jmilne.org/math/articles/1986b.pdf

State every extra assumption needed to make the branch preserve `<G>` and act
affinely on its scalar coordinate. Then compute the exact number of `α` for
which an affine function can equal `α^d`, including exceptional cases. Do not
apply this theorem to an arbitrary multivalued correspondence.

## Mandatory ordered control 2 — genuinely multivalued escape

If the object is not a functional graph, do not assume its normalization splits
into explicitly listed graph branches. Prove how a point over `Q` is found,
how the correct point is distinguished, and why a malicious wrong branch
cannot pass the public certificate. Charge projection degree, branch count,
root finding, field extension, ramification, exceptional fibers, and data
movement.

## Mandatory symbolic mutations

Apply all six:

1. functional-graph rigidity;
2. high-degree interpolation table — serialize the target values and charge
   its construction, storage, access, and data movement;
3. random same-shape null correspondence — distinguish algebraic signal from
   representation/certificate artifacts;
4. branch permutation — the certificate must identify the semantic target,
   not merely a branch index;
5. certificate-oracle removal — remove any verifier ability that performs the
   omitted acquisition and recompute soundness;
6. explicit `Theta(sqrt(N))` setup/data boundary — any such cost restores rho
   scale even if online evaluation is cheap.

These are proof controls, not empirical runs.

## Complete cost and Pareto accounting

Report construction and setup, equation/circuit size, field and group
operations, normalization/root finding, evaluator and branch search,
certificate generation and verification, inverse success, retries, reuse,
peak memory, persistent data, and downstream Cheon cost. Separate rebuilding
setup on each attempt from reuse once. Fresh challenges are not retries for a
fixed instance.

Every row states `dominated_by` after checking time, memory, and data/query.
Every row states quantitative `sota_delta`; rows that are not complete ordinary
ECDLP solvers use `not_applicable`, not numeric zero. Necessary boundary
profiles must be labeled profiles, never achieved algorithms.

## Required five artifacts

Write exactly beneath `tasks/TASK-20260802-252/`:

1. `correspondence-dichotomy.md`
2. `proof-obligations.yaml`
3. `cost-and-branch-bound.yaml`
4. `pareto-frontier.yaml`
5. `provenance.yaml`

The report must separate speculation, derivation, observation, and conclusion.
Every proposed mechanism states predictions, test boundary, and falsification.
Proof obligations separate representation size, correctness, success, runtime,
memory, data, and downstream composition.

The provenance artifact records requested policy `research-deep`, resolved
model `gpt-5.6-sol`, high effort, live verification, no fallback, no degraded
requirements, one invocation, zero experiments, zero implementations, and the
exact write scope.

## Stop rules and claim ceiling

Stop after one object. Return `REVISE` or an explicit obstruction if the map
hypotheses, branch algorithm, certificate semantics, parameter family, or
complete costs remain underspecified. Do not broaden into a taxonomy.

No official status change, evidence record, knowledge promotion, support,
rejection, novelty, SOTA, closure, or breakthrough. A positive-looking
construction advances only to immutable snapshot and independent Red Team.
