# TASK-20260722-012 — schedule-to-receipt-to-rank derivation

## Terminal verdict

`CONTRACT_COMPLETE_REVIEW_REQUIRED`

The versioned contract in `certificate_contract.yaml` satisfies every
schema-construction obligation in the handoff. No scoped no-go trigger was
reached at theory/schema time. This says only that the proposed certificate is
precise enough for independent review. It does not say that an implementation
exists, that any fixture passes, or that the assumptions hold for an ECDLP
relation source.

No implementation or experiment was authorized or performed. The maximum claim
is conservation for a later sealed toy/public campaign under one frozen field,
column schema, resource boundary, and explicitly accepted probability model.
This is not an attack improvement, ECDLP lower bound, cryptographic result,
solution, or breakthrough. The P1553 R4 target-label common-factor operation is
outside this work.

## Runtime and authorization gate

- requested policy: `research-sol-max`
- resolved model: `gpt-5.6-sol-high`
- reasoning effort: `high`
- available reasoning effort: `high`
- fallback used: `true`
- authorization: `DEC-20260722-004`
- adapter version: `unavailable_not_exposed_by_cursor_runtime`
- adapter version available: `false`
- adapter/runtime availability: the Cursor agent runtime was available, but its
  adapter version value was not exposed to this session
- equivalence to the unavailable requested policy: not claimed

These values exactly match the authorized fallback. A mismatch would have
stopped this task before construction.

## 1. Why a pre-execution schedule is necessary

Let \(S\) be the finite set of attempt IDs in a schedule and \(T\) the multiset
of attempt IDs in terminal receipts. Uniqueness checks over \(T\) alone cannot
detect an attempt omitted before its ID is emitted. Completeness is meaningful
only relative to an independently sealed \(S\).

The contract therefore requires the Coordinator to archive the canonical JSON
schedule before any attempt is activated. The schedule hash binds:

- every root and possible retry, explicit 256-bit seed, ordinal, worker slot,
  public fixture, and per-attempt budget;
- the complete retry forest and each frozen activation predicate;
- the exhaustive terminal vocabulary;
- the prime field, ordered column schema, point encodings, and row format;
- resource-counter conventions and ownership rules;
- the statistical strata, calibration provenance, alpha allocations, and
  unconditional probability cohort.

All possible retries are nodes in the sealed forest. A retry whose activation
predicate is false receives one `NOT_ACTIVATED` receipt with zero
attempt-owned counters. Consequently, dynamic retry behavior does not create
an ID outside the precommit.

The schedule/receipt condition is the conjunction

\[
\operatorname{set}(S)=\operatorname{set}(T),\qquad
|S|=|T|,\qquad
\forall a\in S:\operatorname{multiplicity}_T(a)=1.
\]

Each receipt must also echo the sealed seed, ordinal, parent, fixture, worker,
budget, and schema hashes. The verifier recomputes activation in ordinal order.
Thus equality of ID sets cannot hide a seed substitution, undeclared retry,
changed budget, or false activation.

A hash alone does not prove temporal ordering. The trust root is the accepted
Coordinator snapshot receipt and Git ordering before activation; timestamps
are only corroborating metadata. If that pre-execution archival gate is absent,
this version has a scoped no-go: it cannot certify attempt completeness for the
named campaign.

## 2. Relation-to-row binding

The public toy fixture supplies a prime-order subgroup of order \(\ell\), an
ordered array of named factor-base points \(P_1,\ldots,P_d\), and canonical
point encodings. The verifier independently checks that \(\ell\) is prime,
that each point is valid, and that \(\ell P_j=O\).

For one decomposition certificate

\[
P_t=\sum_{u\in L}P_u,
\]

define the coefficient of column \(j\) by

\[
a_j=\#\{u\in L:u=j\}-\mathbf 1[j=t]\pmod{\ell},
\quad 0\le a_j<\ell.
\]

The independent verifier checks the group equality from the public fixture and
derives \((a_1,\ldots,a_d)\) without using producer solver state. Each
coefficient is serialized in exactly
\(\lceil\operatorname{bitlength}(\ell-1)/8\rceil\) unsigned big-endian bytes,
in the sealed column order. The row hash includes the schema hash as a domain
separator.

This gives three distinct checks:

1. the group certificate is valid;
2. the independently derived canonical row equals the declared row;
3. the field and column schema are the sealed ones.

A valid group equality paired with a row from different summands therefore
becomes `RELATION_INVALID`, consumes its full resource vector, and receives
zero rank credit. A wrong-field producer rank cannot pass because the
independent verifier performs elimination over the sealed \(\mathbb F_\ell\).

## 3. Exact incremental-rank conservation

Let \(M_0\) be the sealed initial matrix, independently reparsed and ranked over
\(\mathbb F_\ell\). Process receipt candidates in schedule-ordinal order. For
attempt \(i\), let \(M_i\) be the matrix after inserting its row only when the
receipt is `RELATION_VALID` and its independent row binding passes. Define

\[
\Delta_i=\operatorname{rank}_{\mathbb F_\ell}(M_i)
         -\operatorname{rank}_{\mathbb F_\ell}(M_{i-1}).
\]

Appending one row changes rank by either zero or one, so
\(\Delta_i\in\{0,1\}\). A receipt with no eligible row has
\(\Delta_i=0\). A valid row has:

- `independent` when \(\Delta_i=1\);
- `exact_duplicate` when its canonical row hash appeared earlier and
  \(\Delta_i=0\);
- `dependent_nonduplicate` when it is new by hash but lies in the prior row
  span.

Telescoping gives the conservation identity

\[
\operatorname{rank}(M_f)-\operatorname{rank}(M_0)
=\sum_{i=1}^{|S|}\Delta_i=:R_{\rm gain}.
\]

No successful-only denominator is possible: invalid, absent, duplicate, and
dependent rows remain in the schedule and resource totals, while only an
independently verified \(\Delta_i=1\) earns rank credit. If
\(R_{\rm gain}=0\), every component of a “resource per rank” report is
infinite/undefined as declared; no finite scalar is fabricated.

## 4. Correct finite-budget probability gate

The earlier expression \(\lceil r/p_L\rceil\) cannot be called a lower bound on
required attempts. Under fixed IID Bernoulli yield \(p\), the number \(N_r\) of
trials to obtain \(r\) successes has

\[
\mathbb E[N_r]=r/p.
\]

On an event where \(p\ge p_L>0\),
\(\mathbb E[N_r]\le r/p_L\). Thus \(r/p_L\) is an upper bound on conditional
expected trials, not a lower bound and not a high-probability completion
budget.

For a declared tail risk \(\alpha_{\rm tail}\), the contract instead chooses
the least integer \(n_\star\ge r\) satisfying

\[
\Pr[\operatorname{Binomial}(n_\star,p_L)\ge r]
=\sum_{k=r}^{n_\star}\binom{n_\star}{k}
 p_L^k(1-p_L)^{n_\star-k}
\ge 1-\alpha_{\rm tail}.
\]

Equivalently,
\(\Pr[N_r\le n_\star]\ge1-\alpha_{\rm tail}\) under the negative-binomial
view. The finite sum is evaluated as exact rational arithmetic from a finite
decimal \(p_L\). If \(r>0\) and \(p_L=0\), no finite budget follows.

For each prespecified stratum \(s\), a disjoint, fixed-size calibration sample
has \(m_s\) trials and \(x_s\) verified rank-increment successes. The one-sided
Clopper--Pearson lower endpoint is

\[
p_{L,s}=
\begin{cases}
0,&x_s=0,\\
\operatorname{Beta}^{-1}(\alpha_{{\rm est},s};
 x_s,m_s-x_s+1),&x_s>0.
\end{cases}
\]

Because an inverse-beta endpoint is generally not rational, the schedule stores
a finite decimal no greater than a directed-rounding certified lower endpoint.
The tail is evaluated at that serialized, possibly more conservative value.

This version permits only a prespecified stratified fixed-IID model:

- strata and membership are fixed before outcomes;
- each probability-cohort attempt is an unconditional root;
- within a stratum, rank-increment indicators are IID Bernoulli with one fixed
  unknown \(p_s\);
- calibration and evaluation are disjoint;
- calibration stopping, seeds, exclusions, and strata are outcome-independent;
- retries and adaptive attempts are excluded from the tail guarantee.

No cross-stratum independence is asserted. The campaign uses the union bound

\[
\alpha_{\rm total}
\le\sum_s\left(\alpha_{{\rm est},s}+\alpha_{{\rm tail},s}\right)
\le\alpha_{\rm campaign}.
\]

Incremental-rank yield can vary with current rank, matrix occupancy, or source
adaptation. If those effects make within-stratum IID indefensible, the first
failed probability obligation is named and this version emits no finite
completion guarantee. That is a scoped no-go for this probability subclaim,
not a no-go for other sequential models and not a mathematical statement about
ECDLP.

## 5. Resource conservation without illicit scalar sums

The contract keeps unlike resources as a vector. Additive coordinates are:

\[
(\text{CPU ns},\ \text{group operations by type},\
\text{I/O read bytes},\ \text{I/O write bytes},\
\text{communication sent bytes},\
\text{communication received bytes}).
\]

Wall time, peak memory, and retained bytes use different aggregation laws:

- campaign elapsed wall time is the span from the first activated start to the
  last activated finish on one monotonic clock;
- active wall time is the measure of the union of intervals, not the sum of
  overlapping worker durations;
- per-domain memory peaks and a separately observed campaign peak are
  preserved, never summed;
- retained bytes are summed once per unique content hash, not once per
  reference.

Every exclusive work ID has exactly one attempt or named-stage owner. Every
shared work ID has one campaign-registry entry with one measured vector and
exact rational attribution weights summing to one. Receipt references to that
entry do not add it again. Double-owned and unowned shared work are both fatal
to resource conservation. Setup, relation collection, linear algebra, descent,
verification, receipt creation, and independent audit overhead remain named
partitions even when a toy fixture has zero work in a partition.

There is no scalar “total cost.” Coordinatewise comparison is allowed only
when both campaigns use identical counter coverage and conventions, with wall
and memory caps declared separately. Otherwise they are incomparable. This
prevents parallel elapsed time from silently replacing CPU, communication,
I/O, retained storage, or group operations.

## 6. Reader-checkable planted controls

The contract has a decisive expected result for every required corruption:

- omit one sealed receipt: `BIJECTION_MISSING_RECEIPT`;
- duplicate an attempt ID: `BIJECTION_DUPLICATE_ID`;
- create a retry-parent cycle: `SCHEDULE_RETRY_CYCLE`;
- change field, column order, or schema digest:
  `FIELD_OR_SCHEMA_MISMATCH`;
- charge one shared work item twice: `SHARED_WORK_DOUBLE_COUNT`;
- leave referenced shared work unowned: `SHARED_WORK_UNOWNED`;
- pair a valid certificate with a row from different summands:
  `CERTIFICATE_ROW_MISMATCH_AND_ZERO_RANK`;
- compute producer rank over another field: `INDEPENDENT_RANK_MISMATCH`.

A clean control passes only if every conservation gate passes. These controls
are fixture descriptions, not executed observations.

## 7. Scoped no-go order

An independent reader can stop at the first unsatisfied obligation in this
order:

1. runtime metadata matches authorization;
2. the pre-execution schedule is sealable;
3. the finite retry graph is acyclic;
4. terminal codes are exhaustive;
5. field, columns, and canonical row are exact;
6. the schedule/receipt bijection is reconstructible;
7. relation and row are independently verifiable;
8. exact incremental rank is reconstructible;
9. resource ownership is complete without scalarization;
10. probability assumptions and tail gate are explicit;
11. every planted control has a decisive expected result.

At schema-construction time, none failed. A later failure would establish only
that the named contract version cannot certify the named toy/public campaign
under its declared boundary. It would not establish ECDLP hardness, a lower
bound, universal impossibility, or absence of a different methodology.

## Public documentation boundary

Public methodology documentation was consulted on 2026-07-22:

- RFC 8785, JSON Canonicalization Scheme:
  <https://www.rfc-editor.org/rfc/rfc8785>
- Boost negative-binomial distribution documentation:
  <https://www.boost.org/doc/libs/1_46_0/libs/math/doc/sf_and_dist/html/math_toolkit/dist/dist_ref/dists/negative_binomial_dist.html>
- SLSA provenance v1.1:
  <https://slsa.dev/spec/v1.1/provenance>
- in-toto link attestation predicate:
  <https://github.com/in-toto/attestation/blob/main/spec/predicates/link.md>

They support canonical hash binding, provenance patterns, and the distinction
between fixed-trial binomial and fixed-success negative-binomial semantics.
They do not supply or validate an ECDLP improvement.

## Relied-upon repository input binding

Observed repository HEAD:
`0fd1f431f0ab5364516026196c837d26fc526a15`.

```text
f21afaab25ac6f2c74a7a36cb67b76bde313be14ac78077e72abc76031dc493b  AGENTS.md
33f3c8084fa67a76e74fd016195ab1225601053e0b025c715cfdc7c6f9259dcb  CLAUDE.md
a3d710e1be2ee9b7c5404c41212a525d09cd6ca97182941a37102c6b7eeae7d7  agents/idea-generator.md
0025826e758db9d2e175a85f130d5545c6573b9e0b0ebcf07c32f173da146bdd  orchestration/model-policies.yaml
37ccef40827b51c744831f571fc7f852626262596ad153a06ec923995db31d3d  ledger/handoffs/TASK-20260722-012.yaml
6b5323f6d05ae77de284489c6db0f7c52d2d5ea2e8c995ba6b64c96f65738df1  ledger/evidence/EV-ECDLP-002.yaml
159092ca5079cfe609f986841490ef14a03c1f5592a70ccb96eb408285b8c8be  ledger/decisions/DEC-20260722-002.yaml
4a1c8c3c075de4d762cee80bb476b928c1257b684982273c2429eb18e7aee7a4  ledger/decisions/DEC-20260722-004.yaml
e1b9d86c2fc556d77479cc61f6945e817cbb2fc2557e4e149a0906e8b3312415  coordination/goals/GOAL-ECDLP-001/batches/BATCH-001/tasks/TASK-20260721-008/methodology_frontier.yaml
a81e28c53c8802c3240dc09d8401e8fd323b738bab06a29a978c2ad2f013b2a2  coordination/goals/GOAL-ECDLP-001/batches/BATCH-001/tasks/TASK-20260721-008/cost_audit.md
e5f0505a23d1305b2f2c7bd8b73bd8ed0f3e235dd62b28a46a197788445b488e  coordination/goals/GOAL-ECDLP-001/batches/BATCH-001/reviews/TASK-20260722-002/review_report.yaml
b817d91b862ed6739f04b26ebc2c4ca8764f4377fb695dd35337763328476454  coordination/goals/GOAL-ECDLP-001/batches/BATCH-001/reviews/TASK-20260722-002/adversarial_notes.md
37fd8d21d97fdcb429c19b7d29c72dfca7d893f608a9f66f5cc0eb53d5c20d29  docs/claims-and-verification.md
e184c6a307c8f1127399356b1f7483fc05a58974e6968a04b1ac7072c4814490  docs/task-lifecycle.md
2b03510a53fa97b5079fabf109aaf8af3d440e18b53324c48b91684c4dc4c43d  docs/evidence-and-reproducibility.md
37cdc5d7ff60c45465e8ef88e1a800f3d9df06f7035fc9ea1f1552e7bf1ebf9a  docs/dynamic-subagent-dispatch.md
8ba64525354917ab0cf9995955e87d11d86bbf42b147b28b36ae7a43b0c2347e  docs/focused-autoresearch-loop.md
a390605329527d92a3bc97d2cd9e73cd63a626fdb6d7a588df3d6c9e28a578dc  templates/research-records.md
432c1008490a0849c49858071732bdf03316fec201ce5d1258e201bee31de5d7  templates/subagent-task-queue.json
7c8fa3f33ebba021a3c4caca6207378c5c88cac585b5d665bdc0692c75ab5d0e  harness/runner.py
a0699ac3564bd20f96e283027484b4eca2b100ed5f0109087ed7dcd7bb9efffc  tools/validate_ledger.py
c32f380d5bd9c18a5dd903365e214c29d08366fed4c20bbc35d723a37ed13c9f  tools/research_dispatch.py
```

## Exactly one recommended next action

Archive these two `TASK-20260722-012` artifacts through
`TASK-20260722-013` and submit only that immutable snapshot to the independent
`TASK-20260722-014` review; authorize no implementation or experiment.
