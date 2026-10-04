# Blind CM transport, multiplicity, and finite-cost derivation

Task: `TASK-20260908-3bc02e`  
Owned joint: corrected CM transport/multiplicity and fully charged finite-panel cost definitions  
Owned-joint verdict: **breaks**  

This report derives only the assigned quantity from the curated complete
statement. It performs no scientific search, fixture census, interval search,
control timing, panel run, or future-run invocation. It does not review producer
code or approve a protocol, launch, research conclusion, or claim transition.

## 1. Scalar and coordinate transport

Let (C_0=\langle G_0\rangle\) be the rational subgroup of prime order (r).
The conditions (v_r(\#E_0(\mathbb F_p))=1), (r\ne p), and (r\ne3) make
this the unique rational order-(r) subgroup and make every degree-three
isogeny injective on it. Since (\iota) is rational, it preserves (C_0), so
there is a unique scalar (\lambda\pmod r) selected by

\[
    \iota(G_0)=[\lambda]G_0,\qquad \lambda^2\equiv-1\pmod r.
\]

For a normalized degree-three quotient (\phi_K:E_0\to E_K) and its exact
dual (\psi_K),

\[
 \psi_K\phi_K=[3]_{E_0},\qquad \phi_K\psi_K=[3]_{E_K}.
\]

Every point (Q\) in the transported subgroup is (Q=\phi_K(P)) for a unique
(P\in C_0). Therefore

\[
\begin{aligned}
 \beta_K(Q)
 &=\phi_K\iota\psi_K\phi_K(P)\\
 &=\phi_K\iota([3]P)\\
 &=\phi_K([3\lambda]P)\\
 &=[3\lambda]Q.
\end{aligned}
\]

The scalar is consequently

\[
    m\equiv3\lambda\pmod r,
\]

without cancellation by (3^{-1}). Squaring gives

\[
    \beta_K^2=[m^2]=[9\lambda^2]=[-9]
\]

on the transported order-(r) subgroup. The static illustration is internally
consistent: for (r=149\), (\lambda=44\), one has (44^2\equiv-1\),
(m=132\), and (132^2\equiv140\equiv-9\pmod{149}). Both the wrong factor
(44) and wrong sign (17=-132\pmod{149}) differ from (132) and must fail
on every nonzero point of this subgroup.

For the coordinate isomorphism (\rho_u), the correctly transported maps are

\[
    \phi_{K,u}=\rho_u\phi_K,
    \qquad
    \psi_{K,u}=\psi_K\rho_u^{-1}.
\]

Thus

\[
    \beta_{K,u}=\rho_u\beta_K\rho_u^{-1},
\]

so it again acts as ([m]). Omitting the inverse destroys the conjugation except
in accidental cases. A valid known-false control must therefore use a
nonidentity coordinate such as (u=2) or (u=3); (u=1) cannot detect this
error.

## 2. Four kernels and two target classes

Full rational (E_0[3]\cong\mathbb F_3^2) has

\[
    \frac{3^2-1}{3-1}=4
\]

one-dimensional subspaces, hence four distinct cyclic order-three kernels.
They are four labeled endpoints and may never be replaced by two kernels.

At (j=1728), with (p\equiv1\pmod4), the rational automorphism group contains
(\iota). Modulo (±1), its action on the four lines of
(\mathbb P^1(\mathbb F_3)) is represented by

\[
    J=\begin{pmatrix}0&-1\\1&0\end{pmatrix},
    \qquad J^2=-I.
\]

The four canonical lines may be written

\[
 (1,0),\ (0,1),\ (1,1),\ (1,2).
\]

The action swaps the first pair and swaps the second pair. It has no fixed
line because (X^2+1) has no root over (\mathbb F_3). Consequently there are
two automorphism orbits of size two. Kernels in one orbit give isomorphic
quotient endpoints, which yields two target isomorphism classes with
multiplicities (2,2), subject to the contract's explicit forward and inverse
(\mathbb F_p)-isomorphism certificates. Treating all four endpoints as four
independent classes is the known-false model.

The conductor interpretation needs every condition, jointly:

1. (\operatorname{End}(E_0)=\mathbb Z[i]).
2. (D_\pi=t^2-4p=-4f_\pi^2) for an integer (f_\pi), with
   (v_3(f_\pi)=1).
3. (E_0[3]\) is fully rational and all four kernels and normalized maps are
   exact.
4. Each quotient has certified endomorphism order
   (\mathbb Z+3\mathbb Z[i]), discriminant (-4\cdot3^2=-36), and exactly one
   rational ascending edge to the source.
5. The four endpoints have an explicit certified partition into two
   (\mathbb F_p)-isomorphism classes, with two labels per class.

Under these conditions, inertness of (3) in (\mathbb Q(i)) is consistent
with four descending source edges and a depth-one floor. This task did not
retrieve the cited primary literature, so it does not elevate that conditional
volcano statement into independently sourced support. Missing or inconsistent
certificates make the fixture unavailable; they are not negative mathematical
evidence.

## 3. Matrix and panel cardinalities

The declared dimensions rederive as follows:

| Quantity | Product | Count |
|---|---:|---:|
| Main endpoint-arm workloads before blocks | (6\cdot4\cdot3\cdot2\cdot4\cdot7) | 4,032 |
| Main timing rows | (4{,}032\cdot7) | 28,224 |
| Baseline-selection workloads | (9\cdot8\cdot6) | 432 |
| Baseline-selection timing rows | (432\cdot7) | 3,024 |
| Confirmation cells at (q=4096) | (6\cdot2\cdot3) | 36 |
| Class-coordinate cells across four q values | (6\cdot2\cdot3\cdot4) | 144 |
| Top-control rows | (6\cdot3\cdot2\cdot4\cdot2\cdot7) | 2,016 |
| Identity-control rows | same dimensions as top control | 2,016 |
| Dual-composition assertions | (6\cdot4\cdot3\cdot(129+129)) | 18,576 |

The nine selection strata are the three prime intervals crossed with the three
coordinates. Each stratum pools two fixtures times four endpoints, hence eight
endpoints. It excludes fixture, kernel, class, confirmation seed, and all q
values except (q=256). Seed 606101 chooses one winner among arms 2 through 7;
the winner is frozen before seed 606103, reused for every q and every endpoint
in the stratum, and may not be replaced by a confirmation or oracle minimum.

## 4. Correct endpoint weighting and charges

For fixture (f), certified class (c), coordinate (u), and q value, let
(K_0,K_1) be the two labeled endpoints in (c). After exact allocation, the
primary class statistic is

\[
 R[f,c,u,q]=
 \frac{T_{\rm scalar}[f,K_0,u,q]+T_{\rm scalar}[f,K_1,u,q]}
      {T_{\rm transport}[f,K_0,u,q]+T_{\rm transport}[f,K_1,u,q]}.
\]

These are equal endpoint weights applied before division. Dividing numerator
and denominator by two leaves the ratio unchanged. The statistic is generally
different from

\[
 \tfrac12\left(
 T_{\rm scalar}[K_0]/T_{\rm transport}[K_0]
 +T_{\rm scalar}[K_1]/T_{\rm transport}[K_1]
 \right).
\]

For the fixed vectors scalar ([1,1,9,9]) and transport ([1,1,3,3]), the
ratio of totals is (20/8=2.5), while the mean of endpoint ratios is (2.0).
The latter is descriptive only and cannot decide a cell.

Each fixed-q normalized view must include allocated shared-source work in both
strategy totals; all transport discovery, point count/factorization, kernels,
maps, duals, level/class certificates, eigenvalue/sign selection,
normalization, setup, warmup, evaluation, and verification on the transport
side; and all six (q=256) selection campaigns plus selected-arm setup,
per-point tables, library setup, warmup, multiplication, and verification on
the scalar side. Separately reported scaffolding remains outside the ratio.
Each q view contains setup once and is an alternative cold-total view; q views
must never be summed.

Omitting charges can change a decision. Two fixed examples are:

- Scalar workload 120 and transport workload 100 gives an apparent ratio 1.20.
  Charging transport setup 30 changes it to (120/130=12/13<1).
- Scalar workload 100 and transport total 110 gives (10/11\le1). Charging
  scalar selection cost 30 changes it to (13/11), between 1 and 1.20.

## 5. Breaking cost-definition findings

### COST-ALLOC-1: reconciliation key conflict

A single 120 ns shared source raw item is split over four labels and three
coordinates with weight (1/12) in each strategy view. This produces twelve
10 ns allocations totaling 120 ns in the scalar view and another twelve
totaling 120 ns in the transport view. The weights sum to one per view but two
globally. The statement simultaneously requires:

- shared source costs in both strategy totals;
- reconciliation separately in each strategy view;
- one allocation record per raw item;
- weights for each raw item to sum exactly one; and
- allocated component cost to sum to the raw cost.

These conditions are inconsistent unless the last two invariants are keyed by
`(raw_cost_row_id, strategy_view)` and the phrase "one record per raw cost item"
means coverage rather than uniqueness. The exact key must be frozen.

### COST-ALLOC-2: one-off events have no total typed representation

The raw tensor requires non-null fixture, endpoint, class, coordinate, seed,
q, arm, block, repetition, component, and stage indices for every charged row.
One-off discovery, certificate, selection, setup, table construction, library
initialization, and warmup events do not naturally possess all those indices.
The statement provides no typed `not_applicable` value and no separate raw
event table. Its allocation rules also fail to name exact targets for
selected-arm setup, every per-point table, library setup, and both warmups,
although the strategy equations require all of them.

This is decision-relevant. Assigning a one-off setup event to every q or block
duplicates actual campaign cost; assigning it to one arbitrary q or block
makes other normalized views omit it; leaving an index null violates the tensor;
and an undeclared sentinel changes the schema. A corrected definition should
separate immutable raw events from derived per-view allocations and give every
registered component one exhaustive allocation rule.

### BASELINE-1: campaign-cost argmin is not a fastest-arm argmin

The selection score sums every actual adaptive repetition, but the workload
used in normalized totals is cost divided by repetition count. These orderings
can disagree. In the fixed mock:

- arm A costs 3,000,000 ns per q-list and repeats 34 times, scoring 102,000,000 ns;
- arm B costs 100,100,000 ns per q-list and repeats once, scoring 100,100,000 ns.

The declared selection chooses B even though its normalized workload is more
than 33 times slower. Therefore this argmin can define the cheapest charged
selection campaign, but it cannot define the `fastest_declared_scalar_baseline`
used by replay. The robust repair is to select by the frozen normalized
per-workload statistic while charging the full cost of all six selection
campaigns separately. If the campaign-cost argmin is retained, all downstream
labels and interpretations must state that narrower baseline.

## 6. Finite decision and crossover quantifiers

At governing seed 606103 and (q=4096), there are exactly 36 primary cells.
After a deterministic stability reducer exists:

- Positive finite-panel signal: all 36 cells are resolved; every full ratio is
  at least 1.20; every full and leave-one-block-out reduction remains at least
  1.20; the full panel and top control are valid; and every required charge is
  present.
- Scoped negative finite cost gap: all 36 cells are resolved; every ratio is at
  most 1.00; every full and leave-one-out reduction remains at most 1.00; and
  the panel is complete and valid.
- Otherwise the result is inconclusive. This includes a mixture of the first
  two classifications, any value strictly between 1 and 1.20, any missing or
  below-resolution datum, an invalid certificate or control, unstable block
  reduction, invalid cost reconciliation, unresolved baseline stratum, or
  infrastructure stop.

Equality belongs to the adjacent closed gate: 1.00 is eligible for the scoped
negative and 1.20 is eligible for the positive gate. A panel containing cells
at both boundaries is mixed and inconclusive because neither universal gate
holds.

For each primary cell, the q-star function has the only consistent typed
reading:

1. Scan (q\in[1,16,256,4096]) in order.
2. Return the first q whose ratio is resolved and at least 1, only if every
   earlier ratio is resolved and strictly below 1.
3. If every q is resolved and below 1, return `greater_than_4096`.
4. If any value needed to establish the first crossing or no crossing is
   unresolved, return `unresolved`.
5. Never interpolate.

Fixed cases returned q-star values 1, 256, `greater_than_4096`, and
`unresolved` for the four corresponding branches.

### REDUCER-1: leave-one-out median is undefined

The full estimator is the median of seven normalized blocks. Each
leave-one-block-out reduction has six blocks, and no even-sample median is
defined. It is also unspecified whether a reduction removes the same numbered
block jointly from the two endpoints and both strategy totals.

For remaining scalar block values ([1,1,1,2,2,2]) and unit transport, the
lower median is 1, the average of the two central values is 1.5, and the upper
median is 2. The lower convention satisfies the negative threshold; the other
two satisfy the positive threshold. Stability is therefore not a deterministic
function of the frozen panel. This alone breaks readiness of the assigned cost
joint.

## 7. Static-case record

Two fixed Python invocations were made with `/usr/bin/time -p`; both were
single-process and had a 10-second outer tool watchdog. They performed no file
or network I/O and invoked no project runner.

The first invocation attempted C01 through C10. C01-C09 passed. C10 failed
because the review script reused a matrix helper reducing modulo 149 when the
test required modulo 3. The invocation stopped at that assertion:

```text
AssertionError: ('C10_iota_square_minus_identity', 'J^2=-I modulo 149 matrix model')
real 0.08
user 0.03
sys 0.01
```

The second invocation reran C10 with a dedicated modulo-3 helper and then ran
C11-C31 and C33-C40. All 30 attempts passed:

```text
C10 iota square                         PASS  ((2,0),(0,2)) over F3
C11 no fixed projective line            PASS
C12 two projective orbits               PASS
C13 each orbit has size two             PASS
C14 four independent classes rejected   PASS
C15 conductor-3 discriminant             PASS  -36
C16 multiplicities total four           PASS  4
C17 main workloads                      PASS  4032
C18 main rows                           PASS  28224
C19 selection workloads                 PASS  432
C20 selection rows                      PASS  3024
C21 primary cells                       PASS  36
C22 top-control rows                    PASS  2016
C23 dual assertions                     PASS  18576
C24 ratio of totals                     PASS  5/2
C25 mean of ratios                      PASS  2
C26 aggregators differ                  PASS
C27 strata                              PASS  9
C28 endpoints per stratum               PASS  8
C29 omitted transport setup flips gate  PASS  6/5 -> 12/13
C30 omitted selection flips gate        PASS  10/11 -> 13/11
C31 global shared allocation sums two   PASS  2
C33 even median alternatives            PASS  1, 3/2, 2
C34 median convention changes gate      PASS
C35 selector can choose slower arm      PASS  102000000 vs 100100000 ns
C36 q-star at first rung                PASS  1
C37 q-star at third rung                PASS  256
C38 no crossing                         PASS  greater_than_4096
C39 unresolved prior rung               PASS  unresolved
C40 missing cell                        PASS  inconclusive
real 0.04
user 0.02
sys 0.00
```

Total attempted cases, including the one rerun, were exactly 40: 39 passing
attempts and one review-harness failure. Aggregate measured script time was
0.12 wall seconds and 0.06 CPU seconds. The failure was corrected locally in
the static test expression and asserts nothing about the mathematical object.
No further rerun was made.

Administrative source verification used:

```sh
shasum -a 256 AGENTS.md templates/research-records.md \
  docs/task-lifecycle.md docs/dynamic-subagent-dispatch.md \
  docs/research-budget-policy.md docs/evidence-and-reproducibility.md \
  coordination/experiment-reserve/BATCH-45b4d5/review-plan-TASK-20260908-8d5e9e.yaml \
  agents/red-team.md \
  coordination/experiment-reserve/BATCH-45b4d5/blind-input-TASK-20260908-3bc02e.yaml
```

All nine hashes matched the handoff bindings. Hash checks were administrative
and are not included in the 40-case scientific/static budget.

## 8. Blindness and scope attestation

No path in the plan's `blind_from` list was read. In particular, this task did
not read producer source, tests, plans, notes, reports, implementation
directories, snapshot narratives, prior CM review directories, or the sibling
report. It used no external citation.

There were two declared read-scope deviations. The required harness skill was
read as an operating contract. Also, before the blind input was opened, the
session's mandatory memory quick pass searched `MEMORY.md` and returned generic
prior CM topic summaries. Those summaries were not used as evidence and did not
contain the task-specific corrected cost reducer, but their presence prevents a
claim of isolation from every prior CM summary. The exact deviation is recorded
in `review.yaml` for Coordinator adjudication.

The verdict `breaks` applies only to the owned joint. The algebraic correction
and two-class model survive the worked attacks under their stated certificates;
the fully charged finite decision does not, because its allocation and
stability reducer are not yet total deterministic definitions. Both files
remain pending Coordinator archive `TASK-20260908-a6c313` and adjudication.
