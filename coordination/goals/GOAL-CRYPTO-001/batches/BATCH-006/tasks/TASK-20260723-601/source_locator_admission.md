# SOURCE-LOCATOR-OPEN repaired admission

## Verdict and boundary

`NO_ADMISSIBLE_OPERATION`.

The first failed requirement is
`requirement_1_explicit_semantically_distinct_operation`. No checked item
defines a new public operation with typed inputs, outputs, coefficient
provenance, subset semantics, and exact signed occurrence-level source output.
The later simulator, replay, rank, online-query, and total-cost requirements
also fail independently.

This is a zero-compute, non-operational academic mathematics review. It
contains no software, real key, deployed target, standardized-curve execution
plan, or empirical result. It does not claim a breakthrough or an
impossibility theorem.

## Established facts, derivation, and speculation

Established facts:

1. In the generic group model, prime-order discrete logarithm requires
   \(\Omega(\sqrt N)\) generic group operations. Pollard rho matches the
   \(N^{1/2+o(1)}\) work exponent with \(N^{o(1)}\) serial memory.
2. P1552/P1553 give an exact six-list Abel--Jacobi normal form. Their
   determinant, pair-wedge, and Abel-endpoint predicates verify supplied
   source tuples or endpoints; they do not locate signed occurrences.
3. EV-CRYPTO-002 weakens only the compact \(z_R\)/common-factor constructor
   sheet. EV-CRYPTO-005 records only a checked-snapshot no-candidate
   disposition.
4. The current explicit source-labelled control costs
   \(B^{3+o(1)}\) for a complete campaign and for direct fresh-target descent.

Derivation:

\[
B=N^{1/5},\quad
B^{5/4}=N^{0.25},\quad
B^{9/4}=N^{0.45},\quad
B^{5/2}=N^{0.50},\quad
B^3=N^{0.60}.
\]

Thus the existing \(B^3\) control fails both the campaign threshold and the
fresh-query rectangle. The \(0.50\) exponent is only the rho baseline;
anything above \(0.45\) fails campaign admission.

Speculation is narrower than a candidate: a coordinate-sensitive,
target-dependent source locator outside the checked endpoint, determinant,
compact-factor, and zero-minor interfaces could remain logically possible.
No such operation or cost proof is present.

## Repaired requirements

### 1. Semantically distinct explicit operation — FAIL first

An admissible operation must state its public inputs, output, coefficient and
advice provenance, admitted strata, subset-restriction law, and exact signed
occurrence semantics. Nothing checked meets this definition:

- direct \(3+3\) matching is the known generic \(B^3\) control;
- a determinant or three pair wedges give a predicate for supplied tuples;
- Abel endpoint projection leaves endpoint three-sum and source unranking;
- a compact \(z_R\), common factor, translated product, or source dictionary
  is the excluded IDEA-20260723-001 interface unless explicitly constructed;
- an unnamed zero-minor or hyperplane-signature locator is a free oracle; and
- supplied residues, sources, scalars, \(B^3\) provenance, target-fitted
  coefficients, and hidden advice assume the missing operation.

An exception listed as open in P1553 is not itself an operation.

### 2. Exact \(O(1)\)-overhead GGM-simulator exclusion — FAIL

The required relation transcript would be, in known-log mode,

\[
\bigl(j;(i_1,s_1),\ldots,(i_5,s_5);
      \sum_{h=1}^{5}s_h A_{h,i_h}=R_j\bigr),
\]

and, for a fresh scalar-blind mask,

\[
\bigl(\mathsf{fresh};(i_1,s_1),\ldots,(i_5,s_5);
      \sum_{h=1}^{5}s_h A_{h,i_h}=Q+[t]P\bigr).
\]

The occurrence labels and signs are part of the transcript; an unlabelled
endpoint or existence bit is not enough.

The exact target-dependent transcript claimed to be unavailable to an
\(O(1)\)-overhead generic simulator is **absent**. There is no candidate
output distribution against which such a simulator could be compared. For a
supplied tuple, the existing determinant/pair-wedge zero bit is equivalent on
the admitted stratum to checking the group sum, which a generic simulator
reproduces with a constant number of group operations and one equality test.
The direct match is itself generic.

Coordinate erasure is therefore insufficient: naming coordinate reads that
cease to typecheck does not prove that those reads produce a target-dependent
source relation unavailable to a constant-overhead simulator. No non-generic
advantage receives credit.

### 3. Subset-stable occurrence replay — FAIL

Each source entry must remain an occurrence record

\[
(\text{colour},\text{label},\text{sign},\text{public point}).
\]

Equal public points retain distinct labels. A restriction acts on labels,
not on deduplicated endpoints.

Conditionally, if an exact rectangular restricted-existence operation
\(\operatorname{Exists}(S_1,\ldots,S_k;R)\) existed, deterministic replay
could use a frozen depth-first binary partition:

1. query the root box;
2. split one occurrence-label interval;
3. query both children and recurse only into positive children;
4. at every singleton positive leaf, emit the signed tuple and independently
   verify its group equality.

For one six-list relation leaf, the depth is

\[
D_6=\sum_{h=1}^{6}\lceil\log_2 |S_h|\rceil=O(\log B).
\]

Enumerating \(s\) relation tuples uses at most \(1+2sD_6\) restricted calls.
For one fixed fresh target, the analogous bound is
\(1+2s_tD_5\), where
\(D_5=\sum_{h=1}^{5}\lceil\log_2 |S_h|\rceil\).
This traversal does not delete an occurrence shared by other rows.

Every root, positive child, empty sibling, coefficient rebuild, translated
target, source output, and verification is charged. The live state contains
the candidate's persistent setup, the largest restricted-query workspace,
an \(O(\log B)\)-descriptor depth-first stack, the current signed tuple, and
the \(\Theta(B)\) sparse verified rows. Cached coefficients, breadth-first
frontiers, source dictionaries, or ambiguity lists add live state.

This enumerates the accounting obligation, not an operation. No checked
candidate supplies the required subset-stable call.

### 4. Rank yield and rejected batches — FAIL

The campaign needs rank
\(\rho_\star=\Theta(B)\) over the actual factor columns. Expected
\(\Theta(B)\) endpoint incidences do not imply this rank.

An admissible route must give either:

- a deterministic guarantee that every accepted campaign batch has rank at
  least \(\rho_\star\); or
- a proved bound
  \[
  \Pr[\operatorname{rank}\geq\rho_\star]
    \geq N^{-\eta_{\rm rank}+o(1)}.
  \]

In the second case, expected work is multiplied by
\(N^{\eta_{\rm rank}+o(1)}\). Every deficient batch pays its complete
location, replay, miss, ambiguity, verification, rank-computation, rebuild,
discarded-state, and memory-traffic costs.

The checked material has neither guarantee. Rank verification detects a bad
batch but does not pay for replacing it. Hence positive rank credit is zero
and \(\eta_{\rm rank}\) is unknown, not zero.

### 5. Fresh scalar-blind query — FAIL

The complete online cost includes target-dependent setup, target misses,
every restricted replay call, occurrence output, ambiguity, sign/orientation
handling, unmasking, and final public group-equality verification. It must be
at most

\[
B^{5/4+o(1)}=N^{0.25+o(1)}.
\]

No checked source inverse supplies this path. The direct endpoint control is
\(B^{3+o(1)}=N^{0.60+o(1)}\).

### 6. Complete \(\lambda,\mu\) threshold — FAIL

Let \(\beta=1/5\). For a future candidate define:

- \(a,a_m\): setup work and retained-state exponents;
- \(q_{\rm rel},q_{\rm rel,replay},q_{\rm rel,m}\): base relation call,
  restricted replay call, and query workspace;
- \(o_{\rm rel}\): verified occurrence-output exponent;
- \(r\): proved independent rank-yield exponent per accepted batch;
- \(\delta_{\rm rel}\): reciprocal semantic-success exponent;
- \(\eta_{\rm rank}\): reciprocal full-rank acceptance exponent;
- \(\ell,\ell_m\): factor-log solve work and memory;
- \(q_t,q_{t,\rm replay},o_t,\delta_t,u_t\): fresh target query, replay,
  output, miss, and ambiguity/orientation exponents; and
- \(b_w,b_m\): explicit bit-operation, memory-traffic, and bit-memory
  exponents.

The repaired terms are

\[
\begin{aligned}
c_{\rm rel}
  &=\max(q_{\rm rel},q_{\rm rel,replay}+o_{\rm rel},o_{\rm rel}),\\
L_{\rm rel}
  &=\max(0,\beta-r)+\delta_{\rm rel}
    +\eta_{\rm rank}+c_{\rm rel},\\
\tau
  &=\delta_t+u_t+
    \max(q_t,q_{t,\rm replay}+o_t,o_t),\\
\lambda
  &=\max(a,L_{\rm rel},\ell,\tau,\beta,b_w).
\end{aligned}
\]

Peak memory is

\[
\mu=\max(a_m,q_{\rm rel,m},\beta,\ell_m,
         m_{\rm replay},m_{\rm output},b_m).
\]

The constraints are

\[
0\leq r\leq o_{\rm rel},\qquad
\tau\leq0.25,\qquad
\lambda\leq0.45,\qquad
\mu\leq0.45.
\]

Unknown terms fail admission rather than receiving exponent zero.

## Fully charged current control and matched baselines

| Stage | Work | Live state | \(N\)-exponent |
|---|---:|---:|---:|
| Factor decks | \(B^{1+o(1)}\) | \(B^{1+o(1)}\) | \(0.20/0.20\) |
| Source-labelled pair state | \(B^{2+o(1)}\) | \(B^{2+o(1)}\) | \(0.40/0.40\) |
| First generic campaign hit | \(B^{5/2+o(1)}\) | schedule-dependent | \(0.50/-\) |
| Complete explicit campaign | \(B^{3+o(1)}\) | \(B^{3+o(1)}\) direct | \(0.60/0.60\) |
| Optimistic factor-log solve | \(B^{2+o(1)}\) | \(B^{1+o(1)}\) | \(0.40/0.20\) |
| Fresh masked-target control | \(B^{3+o(1)}\) | reusable \(B^{2+o(1)}\) | \(0.60/0.40\) |
| \(\Theta(B)\) row output and verification | \(B^{1+o(1)}\) | \(B^{1+o(1)}\) | \(0.20/0.20\) |
| Final public certificate | \(O(\log N)\) | \(N^{o(1)}\) | \(0/0\) |

The complete control has certifiable work exponent at least \(0.60\) before
unknown rank-rejected batches are added. Direct materialization has memory
exponent \(0.60\). Even granting an unproved streaming state of exponent
\(0.40\) does not reduce campaign or fresh-query work.

Matched comparisons:

- Pollard rho: \(N^{1/2+o(1)}\) expected work and \(N^{o(1)}\) serial memory.
- Baby-step/giant-step: \(N^{1/2+o(1)}\) work and memory.
- Closest specialized source-labelled six-list control:
  \(N^{0.60+o(1)}\) complete campaign and fresh-target work.

The current explicit route is therefore worse than rho in work. A
hypothetical \(\lambda\) or \(\mu\) in \((0.45,0.50]\) would still fail this
campaign's admission threshold.

## Outcome interpretation and limits

- A future explicit operation passing every requirement would become only an
  unfiled theorem candidate for independent review.
- An \(O(1)\)-overhead GGM-simulable operation receives no non-generic
  advantage credit.
- An absent rank tail sets \(r=0\), leaves rank retries unassigned, and fails.
- A complete fresh online exponent above \(0.25\) fails even if the aggregate
  campaign exponent were below \(0.45\).
- A hidden payload, target-fitted advice, or unnamed locator fails before
  cost scoring.

This sheet proves no unrestricted arithmetic-circuit, cell-probe, kSUM,
incidence, GGM, or ECDLP lower bound. It does not close coordinate-sensitive
operations outside the checked interfaces. No novelty claim is made;
`novelty_status` remains `unverified` because no operation exists to classify.

## Ranking rationale and handoff

The repaired sheet is the cheapest valid discriminator because the missing
object is an explicit identity and source operation, not an implementation
effect. Requirement 1 fails at zero compute; the independent simulator,
rank-tail, replay, and online-cost failures show why an open exception cannot
be promoted by assigning missing terms zero. I would apply this same sheet
first to any future claimed locator because it rejects oracle restatements
before deeper theorem review or experimentation.

Return exactly `admission_report.yaml` and `source_locator_admission.md` to the
Coordinator for TASK-20260723-602 snapshot archival and subsequent independent
TASK-20260723-603 review. Do not file a proposal, open an experiment, or
change any goal, hypothesis, evidence, or decision state.
