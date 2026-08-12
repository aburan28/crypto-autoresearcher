---
red_team_report:
  id: RT-20260802-202
  task_id: TASK-20260802-202
  claim_under_review: >-
    TASK-20260802-201's OBSTRUCTED_IN_SCOPE feasibility verdict, its
    field-DLP-inclusive and matched-rho accounting, certificate boundary,
    Pareto/sota_delta claims, and IDEA-20260802-201-01.
  verdict: REVISE
  narrowest_supported_statement: >-
    For the frozen non-special prime-field source and the three registered
    target predicates, no admissible transfer can create anomalous order,
    change ord_N(p), or create a proper subfield. This is a derivation about
    that exact target list, not evidence from rho_special=0 and not a closure
    of isogeny-assisted ECDLP. The proposed quotient-rho successor does not
    obtain its claimed state-space reduction as written.
  counterexample_or_mutation: >-
    Replace each logical group element by M labeled isomorphic copies and use
    the proposed equivalence relation, which identifies only copies carrying
    the same affine label. The physical set has MN encodings but its quotient
    has N classes, not N/M. Exhaustive counting at any small prime N and
    M>1 is the cheapest executable control; the cardinality argument already
    decides the stated mechanism without a run.
  next_concrete_action: >-
    Retain only the bounded invariant obstruction; correct the cost and
    certificate language; remove unsupported Pareto-complete/null claims; and
    replace or reformulate the successor so that it identifies distinct
    original logical elements by certified recoverable relations, with the
    quotient cardinality and success probability proved before execution.
  artifact_paths:
    - coordination/goals/GOAL-ECDLP-001/batches/BATCH-031/tasks/TASK-20260802-202/red-team-report.md
    - coordination/goals/GOAL-ECDLP-001/batches/BATCH-031/tasks/TASK-20260802-202/verdict.yaml
    - coordination/goals/GOAL-ECDLP-001/batches/BATCH-031/tasks/TASK-20260802-202/provenance.yaml
---

# Independent Red Team report

## Verdict

**REVISE.** The producer's narrow non-special-source obstruction survives
independent reconstruction, and its treatment of the observed zero events is
appropriately bounded. The package does not pass as written because its
required exponent-first successor rests on a false quotient-cardinality and
constant-success premise. Several cost, certificate, and Pareto statements
also require narrower wording. None of these findings changes official state,
asserts closure, or supplies a breakthrough attestation.

## Review boundary and snapshot integrity

Substantive interpretation began only after all four producer artifacts were
checked against both the verified snapshot commit and the hash binding in
`dispatch_queue.json`.

| Artifact | SHA-256 in queue, commit, and working tree |
|---|---|
| `feasibility-rerank.md` | `60b7dbf88285ba2595f8a6412ae309e774262a8c0a1bd92effa0b283e9da7a8a` |
| `pareto-frontier.yaml` | `bfda9201c2d17936373db45ce338875c43598d2483bde99c00f807e2fb63ce89` |
| `successor-proposal.yaml` | `35a6317f05ca180ab4fd39adea32faac6489ee02a749c10258a4d091cc9ef831` |
| `provenance.yaml` | `afffab0cdbb9228890a5ed34ddabaecb593d4334fa39850010dbdf5028e50257` |

Snapshot commit
`801524409339d0b4a49faed09f6c5dd2e83e4769` is reachable from `HEAD`, has
the recorded parent `37dc2c6b4f417241b336bf1b01b5275ce6ff70c3`, and changes exactly the
four source artifacts plus the TASK-203 receipt. `git diff` found no difference
between the four reviewed working-tree paths and their committed versions. The
receipt itself hashes to
`36ffa1e9f8e54ecbdbf9fa2ffb7e7e9b9b35b0a6e1ab98e1667f444b1bda48cc`.

The explicit handoff's `maximum_runs: 0` was treated as binding even though the
coordination queue contains the older value `1`. No experiment was executed.
The arithmetic and finite-set cardinality calculations below are independent
derivations, not run evidence.

## Independent reconstruction of the frozen obstruction

Let the original subgroup be (G=\langle P\rangle\subset E(\mathbf F_p)) of
prime order (N), and require an evaluated isogeny whose degree is coprime to
(N). Its restriction to (G) is injective. The three target cases reduce as
follows.

### Anomalous target

An anomalous target over (mathbf F_p) has group order (p). To apply its
solver to the transported order-(N) subgroup requires (N\mid p), hence
(N=p). But the source already contains an order-(p) subgroup. For the stated
20-bit-and-larger regime, Hasse's interval contains no positive multiple of
(p) other than (p), so the source itself has order (p) and is anomalous.
Thus a genuinely non-anomalous source cannot become an admissible anomalous
solver instance. This argument does not need the empirical hit count.

For an explicitly (mathbf F_p)-rational isogeny, the producer's stronger
trace/point-count invariance statement is also correct. Rationality of every
map, or equivalently the target-solver rationality of the transported points,
must remain explicit: an extension-defined map cannot be admitted while its
extension evaluation and solver domain are left uncharged.

### MOV/Frey--Ruck target

The embedding degree of the order-(N) subgroup is

\[
k=\operatorname{ord}_N(p).
\]

It depends only on the frozen pair ((p,N)). Moving to another curve over the
same field while retaining that subgroup order cannot change (k). If (k) is
high, the registered low-(k) target is unreachable. If (k) is already low,
the source already admits a pairing reduction in principle. An isogeny may
still change constant costs of curve arithmetic or auxiliary-point handling;
therefore strict direct-source Pareto dominance needs a matched constant-cost
argument, but no non-special-to-low-(k) transfer exists.

### Subfield/Weil-descent target

The prime field (mathbf F_p) has no proper subfield. An isogeny over the
frozen base field does not create one. Passing to an extension, applying Weil
restriction, or evaluating an extension-defined map introduces a different
ambient representation, solver domain, field arithmetic, data, and
certificate boundary. Those terms cannot be treated as a hit inside the
frozen prime-field target.

### Consequence

For each registered predicate, a genuinely non-special source has an empty
reachable admissible target set. Hence its path-hit probability is exactly
zero by derivation, and any positive-cost repeated-search formulation has
unbounded expected search cost. This supports `OBSTRUCTED_IN_SCOPE` only for
the exact registered target list. It says nothing about a property that varies
within an isogeny class, HEUR-ISO-1 in a different target model, or generic
ECDLP optimality.

The producer's additional claim that an already-special source is weakly
dominated by its direct special solver is valid at the property/exponent level,
but is too strong as a blanket constant-resource Pareto claim. If solver costs
depend on the curve model, the needed inequality is

\[
C_{\rm direct,source}
\le C_{\rm path}+C_{\rm solver,target}+C_{\rm cert}+C_{\rm verify}.
\]

Invariance alone does not prove it. These already-special controls are outside
the genuine non-special transfer row, so this repair does not reverse the
bounded obstruction.

## End-to-end cost reconstruction

For preprocessing (P), positive per-attempt work (A), hit probability
(q), and success-only work (S), the expected cost is

\[
C_{\rm expected}=P+\frac{A}{q}+S.
\]

If some nominally success-side task is actually performed on every attempt,
it belongs in (A), not (S). Conversely, dividing a final certificate by
(q) is an overcharge when that certificate is generated only after a hit.
The placement must be specified term by term. Precomputation must be divided
by an explicitly matched number of targets only when the baseline receives
the same amortization opportunity.

For the non-special frozen rows, (q=0) makes the result unbounded regardless
of field-DLP constants. For the persisted but inadmissible planted row, the
producer arithmetic recomputes:

\[
\frac{9+1284+40}{641.609}=2.077589310624,
\qquad
\log_2(2.077589310624)=1.054910496358,
\]

and with the supplied BSGS-like (1448) charge,

\[
\frac{9+1448+40}{641.609}=2.333196697677,
\qquad
\log_2(2.333196697677)=1.222307937327.
\]

Those are ratios in the frozen charged-operation proxy, not demonstrated
wall-clock ratios. The package adds an elliptic-curve path count, a field-group
DLP count, and pullback work without an explicit common unit calibration or
the registered factor-ten sensitivity. Calling the logarithms “bits more
time” is therefore too strong.

The closest generic field-DLP comparator acts in the order-(N) subgroup, not
automatically in the entire (p^k-1) ambient group. If one uses the same
(0.886\sqrt N=641.609) generic-rho charge and temporarily assumes common
units, the same planted proxy is still adverse but much closer:

\[
\frac{9+641.609+40}{641.609}=1.076370499790,
\qquad \log_2(\cdot)=0.106174756524.
\]

At larger low embedding degree, the closest specialized finite-field DLP
algorithm may instead have substantial preprocessing, relation collection,
descent, memory, and data costs. Those costs and their amortization must be
shown explicitly. The invariant argument makes them irrelevant to
non-special reachability, but the numeric planted `sota_delta` cannot be sold
as an algorithm-independent lower bound.

Retries, tails, preprocessing, and parallelism do not rescue the frozen
non-special rows. For already-special rows, matched parallel rho and direct
special algorithms must be included rather than granting transfer-only
parallelism or precomputation.

## Certificate admissibility and scalar orientation

For a composed isogeny (phi) of degree (D) with (gcd(D,N)=1), a minimal
admissible certificate must bind the edge kernels, domains/codomains, fields of
definition, composition order, (D), and the evaluated values

\[
P'=\phi(P),\qquad Q'=\phi(Q).
\]

If the special solver returns (x) with (Q'=[x]P'), injectivity on (G)
implies (Q=[x]P). The discrete-log scalar itself is not multiplied by the
isogeny degree. If a dual-isogeny pullback is included, then

\[
\widehat\phi(P')=[D]P,\qquad
\widehat\phi(Q')=[D]Q,
\]

and (D^{-1}\bmod N) is used to recover points; that is where degree scaling
appears. TASK-201's generic “pullback/scaling relation” should be replaced by
this exact orientation so the harness cannot multiply the recovered DLP by an
extra degree factor.

For MOV/Frey--Ruck, an exponent check (g^x=h) verifies a field-DLP output but
does not pay for producing it and does not prove the pairing inputs came from
the evaluated path. Generation and verification require separate terms, as do
auxiliary order-(N) point construction, non-degeneracy checks, pairing
evaluation, finite-field precomputation, individual logarithm/descent, and the
final original-curve check. Certificate bytes and verifier queries also belong
on the data/query axis.

The BATCH-030 direct-BSGS transcript remains a non-transfer proxy for the
reasons TASK-201 lists. None of the producer's certificate discussion repairs
that old artifact, and the report correctly does not claim otherwise.

## Zero-event and confidence audit

TASK-201 does not launder `rho_special=0` into impossibility. For zero events in
50,000 independent Bernoulli trials, the exact one-sided 95% upper bound is

\[
1-0.05^{1/50000}=5.991285062\times10^{-5},
\]

consistent with the reported (6\times10^{-5}). The 20- and 24-bit zeros are
fixed-prime observations, not density laws; there are no uncensored samples
for a KS or tail test; and HEUR-ISO-1 remains unmeasured. This part passes.

## Pareto and `sota_delta` audit

The two sign conventions used by the producer are internally consistent:

- (Delta\alpha=\alpha_\rho-\alpha_{\rm candidate}>0) favors the candidate.
- (log_2(C_{\rm candidate}/C_\rho)>0) is adverse to the candidate.

The units and completeness assertions do not fully pass.

1. The planted values `+1.06` and `+1.22` are log ratios of a frozen mixed
   operation-count proxy, not calibrated elapsed time.
2. `pareto_check.complete: true` for the baseline is not backed by an explicit
   inventory of the closest field-DLP algorithms, BSGS, serial and parallel
   rho tradeoffs, preprocessing/amortization regimes, and direct special
   solvers. `dominated_by: null` may be true for serial constant-memory rho,
   but the required every-row audit is not shown.
3. Strict dominance of already-special transfer controls by a direct source
   solver needs the constant-cost inequality above; invariance proves no
   exponent advantage but not every constant on every resource axis.
4. The successor's hypothetical `target_state.dominated_by: null` is not an
   admissible current frontier row. It is an unimplemented target and, more
   decisively, its claimed exponent is derived from the cardinality error
   below. The current successor row is correctly marked dominated by rho.

The bounded repair is to retain qualitative dominance for unreachable rows,
label planted ratios as frozen proxy units, mark strict constant dominance
unresolved where source/target solver costs are unmatched, and remove every
`complete: true`/`dominated_by: null` that lacks a named full frontier audit.

## Decisive successor falsification

IDEA-20260802-201-01 defines a representation as ((E_i,R_i)), where (R_i)
is the image of the **same** affine combination (aP+bQ) under a certified
isogeny path. Let (G) have (N) elements and let (i\in\{1,\ldots,M\})
index the available representations. The physical encoding set is

\[
X=G\times\{1,\ldots,M\},\qquad |X|=MN.
\]

The proposed canonicalization relation is

\[
(R,i)\sim(R,j)
\]

for copies of the same logical element (R). Therefore

\[
|X/\!\sim|=|G|=N,
\]

not (N/M). Canonicalizing representations removes the artificial factor
(M) introduced by making copies; ordinary Pollard rho already walks over the
(N) logical group elements.

For (T) approximately uniform canonical logical samples, the birthday
probability is

\[
\Pr[\text{collision by }T]
\approx 1-\exp\!\left(-\frac{T(T-1)}{2N}\right).
\]

At the proposal's (T=\Theta(\sqrt{N/M})), this is
(Theta(1/M)), not (Omega(1)). With (M=N^\delta), a restart analysis
gives

\[
C_{\rm attempt}=N^{\gamma+(1-\delta)/2+o(1)},\qquad
s=N^{-\delta+o(1)},
\]

and hence

\[
\frac{C_{\rm attempt}}{s}
=N^{\gamma+(1+\delta)/2+o(1)},
\]

before preprocessing, memory, data, certificates, and verification. Running
long enough for constant success instead restores
(N^{\gamma+1/2+o(1)}). Either way, the claimed (3/8) exponent does not
follow. If the (M) copies are used as processors or distinguished-point
tables instead, matched parallel rho receives the same resource and no
unmatched exponent gain has been shown.

This falsifies the stated mechanism and P2/P5 derivation, not every possible
isogeny-orbit quotient. A viable mutation would have to identify (M)
**distinct original logical elements** by known, recoverable affine relations,
prove that collision recovery remains non-degenerate, and account for the
information needed to generate, canonicalize, store, and certify those
relations. That is a materially different proposal and must confront generic-
group lower bounds or state precisely which new oracle/structure escapes them.

The proposal's simultaneous targets (M=N^{1/3}), memory exponent zero, and
data/query exponent zero also lack a construction showing how (M) certified
representations are made available without enumeration, storage, or hidden
oracle data. The proposal names this as an unknown but nevertheless uses the
unearned (N/M) state size in its predictions.

## Cheapest falsification route

No Executor run is needed before repair. The cheapest discriminator is the
finite-set quotient calculation above. If an executable regression control is
later desired, use one tiny prime-order cyclic group, for example (N=101),
construct (M\in\{1,4,16\}) labeled isomorphic copies, transport identical
affine labels, and exhaustively emit:

- the (MN) physical encodings;
- the canonical key for every encoding;
- the number of distinct canonical keys;
- collision work under the exact same walk schedule for each (M); and
- an identical-shape random-bijection null.

The decisive prediction is `distinct_keys = N` for every (M), with logical
collision work independent of (M) after matched sampling. Any implementation
reporting (N/M) keys must expose which distinct original elements it merged
and the certified relations that permit DLP recovery. This proposed control is
toy-only and was not run in this task.

## Exact repairs required

1. Keep `OBSTRUCTED_IN_SCOPE` only as the registered-target, non-special-source
   reachability statement. State map rationality/solver-domain assumptions and
   do not infer broader lane closure.
2. Separate frozen ledger proxy compliance from a closest-algorithm cost model.
   Normalize EC, isogeny, pairing, and field-DLP work to a common unit; include
   the factor-ten sensitivity, preprocessing, retries, tails, memory, data,
   and matched parallelism; relabel the `+1.06/+1.22` figures as proxy ratios.
3. Replace “degree scaling” ambiguity with the exact injectivity and dual-
   isogeny equations, and separate certificate generation from verification.
4. Reissue the Pareto table with a named frontier inventory. Remove the
   successor target's `dominated_by: null`; qualify already-special constant
   dominance unless its solver-cost inequality is established.
5. Withdraw the successor's (N/M), (M^{-1/2}), constant-success, (3/8),
   and `+1/8` claims as written. Either stop at the cardinality falsification or
   propose a new certified relation that merges distinct logical elements and
   redo per-attempt-cost times inverse-success accounting from its proved
   quotient size.

These are revisions to analytical artifacts for Coordinator disposition. They
are not official status changes and do not authorize an experiment.
