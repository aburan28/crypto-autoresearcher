# INPUT CAPSULE — TASK-20260802-231

Relay this file verbatim. It is the complete authorized repository input for a
filesystem-free Idea Generator.

## Objective

Repair only the BATCH-034 producer-output theorem (TASK-224, DEC-20260802-209,
B034-S1) by closing its binding proof-model defect RT-226-F1. Determine
whether the constant-excess producer-only generic lower bound can be re-proved
when every retained encoding/equality-recognition record is either counted in
`P` or otherwise charged with an explicit advice term, under the exact model
below.

Do not restore, weaken, or polish the false certificate lemma of BATCH-033.
Separate:

1. correctness and work of the producer;
2. work of any verifier or certificate mechanism.

No experiment, implementation, Executor, status change, knowledge promotion,
closure, support, novelty, SOTA, or breakthrough claim.

## Durable provenance

- TASK-224 producer snapshot:
  `79008962c5649785c9b0b60eb8f8a904c0e62890`, parent
  `14763e911251898fae4a3d825c97931fe6114bbd`.
- RT-226 review snapshot:
  `65280e54c5649785c9b0b60eb8f8a904c0e62890`, parent
  `79008962c5649785c9b0b60eb8f8a904c0e62890`.
- BATCH-034 synthesis ledger (DEC-20260802-209):
  `7fcced5ca225a6661849a1f9485172827a5d9123`, parent
  `65280e54c5649785c9b0b60eb8f8a904c0e62890`.
- Binding opening decision: DEC-20260802-210.

## Prior-art ceiling

Cheon DLP with auxiliary input is known prior art:

https://www.iacr.org/archive/pkc2012/72930594/72930594.pdf

It assumes `G, alpha*G, alpha^d*G`, with `d | (r-1)`, and costs
`O(sqrt((r-1)/d)+sqrt(d))`. Ordinary input does not supply `alpha^d*G`.

Generalized nonlinear-target generic hardness and related target-assumption
classifications are also prior art:

- https://www.iacr.org/archive/asiacrypt2008/53500495/53500495.pdf
- https://eprint.iacr.org/2007/360.pdf
- https://eprint.iacr.org/2017/343.pdf
- https://static.aminer.org/pdf/PDF/000/314/734/variations_of_diffie_hellman_problem.pdf

The repaired formulation cannot be called novel, first, SOTA, or a
breakthrough. Its ordinary-ECDLP time, memory, and data/query SOTA deltas are
zero.

## Mandatory first mutation: RT-226-C1

Before proposing any lemma, instantiate this control:

- preprocess encodings for known constants and retain an exact
  encoding-to-scalar recognition structure;
- discard the handle objects themselves;
- decide whether every retained record still contributes to `P`.

State explicitly:

1. If a retained encoding/equality-recognition record can be classified
   outside `P`, then equation (1) of TASK-224
   (`s <= (P n + binom(n,2) + d)/N`) is false: the producer can branch on
   recognized `Q = c G` and issue `c^d G` for one extra root per stored
   constant without adding any root to `C_PO`. Construct that success-set
   violation concretely.
2. If every retained record must be counted in `P`, serialize that definition
   as a model rule and re-run the fixed-transcript proof with every record
   counted.
3. Either way, require external advice to be independent of the random
   injection `xi`, or add explicit preprocessing-query and advice-state terms
   to the success inequality.

Do not state the repaired theorem while the advice-state classification is
undefined.

## Exact model to formalize

Let the group have prime order `r`; set `N=r-1`. The hidden scalar is sampled
from the stated domain (normally `F_r^*`) and `Q=alpha*G`. Declare the target
function, including the allowed `d` and `alpha` domain, exactly.

The ordinary generic interface supplies opaque random encodings, equality,
addition, inversion, and multiplication by disclosed scalars. Any advice or
preprocessing must be independent of the challenge `alpha` AND of the random
injection `xi` (or be charged through an explicit advice-state term); charge
its construction and storage. Define:

- `P`: number and construction cost of challenge-independent preprocessed
  handles or records, INCLUDING every retained encoding/equality-recognition
  record;
- `q_g`: online producer generic operations;
- the `q_g+1` online-label boundary, including the challenge-derived starting
  label or output candidate exactly once;
- every access, comparison, branch, and data movement;
- peak memory and any amortization domain.

No pairing, endomorphism, correspondence, extension-field oracle, nonlinear
map, verifier, or certificate oracle exists unless separately declared and
charged. This batch is not a search for such an escape interface.

## Fixed symbolic transcript

Construct a lazy-sampling symbolic game whose transcript schedule, coins,
advice, and formal branch decisions are fixed independently of `alpha` before
evaluating root events. Each oracle-issued handle carries an affine formal
label `a+bX` until an informative collision.

You must handle both kinds of control flow:

1. equality branches between issued handles;
2. branches on raw opaque encoding bits or strings.

Under the repaired model, advice and recognition records are either counted in
`P` or charged through an explicit advice-state term; state which. Re-derive
why the fixed symbolic transcript remains valid under that definition. Add
every raw-encoding coincidence, guess, or exceptional event needed for the
bound.

Adaptive execution must be reduced to fixed transcripts without conditioning
on an `alpha`-dependent branch. State the conditioning and averaging argument,
or leave the exact step as an open proof obligation.

## Exact root union

Define, as sets rather than only a loose count:

- every collision-root set for distinct formal labels that can be compared or
  assigned the same encoding;
- every preprocessing-versus-online root set, using the exact `P` by
  `q_g+1` boundary with the repaired `P` definition;
- every online-versus-online root set;
- every producer-output agreement root set between an allowed output label and
  the nonlinear target polynomial or function;
- every raw-encoding exceptional set, if applicable;
- every advice-state root or query set introduced by the repair.

Take one explicit union, remove identically equal polynomial pairs, bound the
number of distinct roots over the declared `alpha` domain, and identify any
overlap or double counting. Do not silently replace `q_g+1` by `q_g`.

If the producer may output an arbitrary string not issued by the oracle, add
an explicit encoding-guess probability term based on the encoding space and
number of issued encodings. Prefer the cleaner theorem convention that the
producer must return an oracle-issued handle, but state the convention in the
theorem.

## Correctness, success, and cost

Prove or isolate separately:

1. affine-label closure before the exact bad-event union;
2. the probability of the collision union;
3. the probability of output agreement outside collisions;
4. producer correctness for an oracle-issued output;
5. the implication, if any, from constant producer correctness to
   `P*(q_g+1)+binom(q_g+1,2)=Omega(N)` under the repaired `P` definition;
6. the resulting work bound after preprocessing construction and accesses are
   charged.

Do not infer certificate soundness. A verifier may be discussed only in a
separate section with its own labels, collisions, queries, memory, data, and
success. A combined producer-plus-verifier lower bound must be labeled
combined work and cannot be substituted for the producer theorem.

For randomized or restartable algorithms, report:

    expected work
      = per-attempt charged work * inverse per-attempt success probability.

Disclose whether preprocessing is single-instance or amortized. Single-
instance preprocessing is fully charged. An amortized row states the number
and independence of instances and is not an ordinary single-instance row.
Split rebuild-each-attempt from reuse-once preprocessing: a reuse-once row
uses `C_pre + E[W_online]/s`, never `C_pre/s` divided from online work.

## Pareto requirements

Create piecewise rows over the relevant regimes of `P`, `q_g`, success, and
amortization. Every row must contain:

- scope and admissibility;
- time exponent and full expected-work expression;
- peak-memory exponent;
- data/query/access exponent;
- preprocessing construction and amortization assumptions;
- `dominated_by` after comparison against every local row;
- quantitative `sota_delta` fields, with `ecdlp_solver`, `comparison_admissible`,
  and `not_applicable` used consistently: a row with `ecdlp_solver: false`
  must set `comparison_admissible: false` and all ordinary SOTA deltas to
  `not_applicable`, never numeric zero;
- explicit statement that lower-bound profiles are profiles, not an achieved
  frontier.

The ordinary single-instance baseline is Pollard rho or kangaroo:

    time exponent: 0.5
    memory exponent: 0.0
    ordinary sota_delta_time: 0.0
    ordinary sota_delta_memory: 0.0
    ordinary data_or_query_delta: 0.0

Use `not_applicable`, not zero, for ordinary SOTA deltas of rows inadmissible
for ordinary input. Do not claim a global frontier.

## Required artifacts

Return exactly four UTF-8 payloads and no commentary outside these markers:

    ---BEGIN ARTIFACT: repaired-producer-bound.md---
    [payload]
    ---END ARTIFACT: repaired-producer-bound.md---
    ---BEGIN ARTIFACT: proof-obligations.yaml---
    [payload]
    ---END ARTIFACT: proof-obligations.yaml---
    ---BEGIN ARTIFACT: pareto-frontier.yaml---
    [payload]
    ---END ARTIFACT: pareto-frontier.yaml---
    ---BEGIN ARTIFACT: provenance.yaml---
    [payload]
    ---END ARTIFACT: provenance.yaml---

The Coordinator materializes them verbatim beneath
`BATCH-035/tasks/TASK-20260802-231/`.

`proof-obligations.yaml` must mark each obligation `PROVED`, `REFUTED`, or
`OPEN`, cite the exact section, and give a falsification condition. In
particular, re-list PO-224-05, PO-224-06, PO-224-08, PO-224-12, PO-224-14,
PO-224-16, and PO-224-18 under their BATCH-035 IDs and state their disposition
against the repaired advice definition.
`pareto-frontier.yaml` must include the piecewise fields above.
`provenance.yaml` records the actual session data and zero experiment runs.

## Completion outcomes and stop rule

- Candidate: the producer-only theorem is re-proved with the advice-state
  defect closed, every retained record counted or explicitly charged, and the
  corrected expected-work and Pareto accounting. Status remains an unverified
  theorem candidate.
- Refuted: a named counterexample defeats the repaired producer route (the
  RT-226-C1 classification question is the cheapest one).
- Inconclusive: name the exact missing symbolic-transcript, root-count,
  encoding, success, or cost lemma and the cheapest falsification control.

Stop after one complete candidate or one exact obstruction. Every outcome is
snapshotted and independently red-teamed. No outcome changes official status.

## Inference provenance

    requested_policy: research-deep
    reasoning_effort: xhigh
    fallback_allowed: false
    degraded_allowed: false
    independent_session_required: false
    wall_clock_seconds: 1800
    memory_gb: 2
    maximum_runs: 1
    experiment_run_budget: 0

Record actual runtime, resolved model identifier, verification status,
timestamps, and any adapter receipt exactly as supplied; otherwise use
`not_reported`. Any model, effort, or capability mismatch invalidates the
attempt.
