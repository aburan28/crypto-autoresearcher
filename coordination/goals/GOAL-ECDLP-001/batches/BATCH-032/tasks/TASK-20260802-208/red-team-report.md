# Independent Red Team Report — TASK-20260802-208

```yaml
red_team_report:
  id: RT-20260802-208
  task_id: TASK-20260802-208
  claim_under_review: "The fixed-field barrier, quotient correction, expected-cost model, Pareto frontier, and auxiliary-power escape in the committed TASK-20260802-206 package."
  verdict: REVISE
  objections:
    - RT-208-O1-low-memory-comparator-omitted
    - RT-208-O2-public-scalar-setup-missing
    - RT-208-O3-exact-cost-and-data-units
    - RT-208-O4-ordinary-acquisition-boundary
    - RT-208-O5-balanced-family-remains-open
    - RT-208-O6-heuristic-transfer-remains-conditional
  required_controls:
    - RT-208-C1-typed-collision-proof
    - RT-208-C2-low-memory-torsor-comparator
    - RT-208-C3-generic-span-acquisition-argument
    - RT-208-C4-divisor-and-generator-certificate
    - RT-208-C5-independent-auxiliary-null
  counterexample_or_mutation: "Replace the table stages by Pollard kangaroo/rho vectorization on the same two scalar-action torsors. It has the same time exponent tau and memory exponent 0, so it dominates PF-206-05 under the package's own exponent-level axes."
  baseline_comparison: "The fixed-field and quotient statements survive. The augmented-input time exponent is algebraically attainable up to polylogarithmic factors, but the table row is not Pareto-optimal. No ordinary-input advantage survives without a charged, independently justified source of A."
  heuristic_challenges:
    - "H-206-01 is a conditional uniform-label model, not a demonstrated property of a concrete quotient."
    - "H-206-02 has no mixing theorem or matched-null evidence; it remains a birthday-model assumption."
  cost_model_challenges:
    - "Known-scalar actions cost O(log N) elliptic-curve additions in the stated units, so the reader-checkable bound is soft-O or N^(tau+o(1)), not literal O(sqrt(e)+sqrt(d)) group additions."
    - "A point encoding is Theta(log p) bits unless log p=Theta(log N) is made an explicit family assumption."
    - "Generator discovery/order certification and factorization assumptions must be charged or supplied as public target-independent setup."
  reduction_and_scope_challenges:
    - "The tuple (P,Q,A,d) alone does not identify certified generators for the two exact scalar-action domains."
    - "In the ordinary generic group model, producing A from (P,Q) is nonlinear in the hidden scalar and has no supplied sub-rho route."
    - "The balanced one-quarter row is only conditional on an unexhibited divisor family."
  narrowest_supported_statement: "Within the frozen fixed-field boundary, the named anomalous, lower-embedding-degree, and prime-field-subfield weaknesses are not manufactured, and the quotient/inverse-success correction is valid under its stated uniform-fiber and random-mapping assumptions. For augmented input (P,Q=[x]P,A=[x^d]P,d), plus certified public scalar generators, a two-stage scalar-action search has time N^(tau+o(1)); this does not improve ordinary ECDLP, and the table implementation is dominated by its low-memory randomized variant."
  next_concrete_action: "Archive a corrected proof-only successor that adds the scalar generator/order certificate, the explicit two-stage relations below, soft-O operation counts, the low-memory Pareto row, Theta(log p) data accounting, and a generic-group acquisition lemma. Do not run an experiment or promote a claim."
  artifact_paths:
    - coordination/goals/GOAL-ECDLP-001/batches/BATCH-032/tasks/TASK-20260802-208/red-team-report.md
    - coordination/goals/GOAL-ECDLP-001/batches/BATCH-032/tasks/TASK-20260802-208/verdict.yaml
    - coordination/goals/GOAL-ECDLP-001/batches/BATCH-032/tasks/TASK-20260802-208/provenance.yaml
```

## 1. Snapshot integrity gate

Interpretation began only after the following checks passed.

- Reviewed commit: `dbd03c4b26e48a5a093e6740588044c4f666aa4a`.
- Reachability: the reviewed commit is an ancestor of `HEAD`.
- Sole parent: `d015ae4e7b663505de14c22b92d7a136535b4dee`.
- Changed-path count: exactly six, comprising the five TASK-206 producer files and the TASK-207 receipt.
- The recomputed SHA-256 values agree with the Coordinator's post-commit archive record:

| Committed path | SHA-256 |
|---|---|
| `barrier-and-escape-analysis.md` | `5ff487bba290d58d3eab2e23fc85700efe22dba689c413b1b01b455d97f68e65` |
| `proof-obligations.yaml` | `fae824fc0168eabebe9ec32f2830efb1cab0e14f4efa1bb1b491b5e9ca0c863e` |
| `pareto-frontier.yaml` | `8bdf3a7a5fc92a075a8d2a40a7254621e73449b0789f44f1fa1694c75b55c2cf` |
| `successor-proposal.yaml` | `51e9debf199c43787d1f31b9f98bc9e74e89d5010b767c591c106dda0662bd20` |
| `provenance.yaml` | `7e1ad74728a89f8fcd0b1681fe4611e02efd8ebfe98936898305cd02f6123e8b` |
| `snapshot_commit_receipt.json` | `1a5f76df99efb496226999e69618162bf9895a9229c536f1d41f3896633c0015` |

The receipt deliberately contains null self-referential commit/hash fields; the
external post-commit archive entry supplies the values checked above. No
working-tree version of a producer artifact was used for interpretation.

## 2. Independent reconstruction of the surviving barrier

Let (G=\langle P\rangle\subset E(\mathbb F_p)) have prime order (N), and
fix (Q=[x]P).

1. An isogeny defined over (\mathbb F_p) preserves the Frobenius
   characteristic polynomial, hence (p+1-t) and the rational point count.
2. If (\gcd(\deg\phi,N)=1), then (\phi(R)=O) for (R\in G) implies
   ([\deg\phi]R=\hat\phi\phi(R)=O), hence (R=O). The order-(N)
   subgroup is therefore carried injectively to an order-(N) subgroup.
3. With (p) and (N) fixed, (\operatorname{ord}_N(p)) is fixed. Moving
   inside the class cannot lower that embedding degree.
4. A prime field has no proper subfield, so movement among curves over the
   same prime field does not create the named proper-subfield descent.

This proves only the admission barrier stated by TASK-206. It says nothing
against order-changing correspondences, field-changing reductions,
extension-field constructions, non-prime-to-(N) maps, or extra information.

For the quotient, an (NM)-element set partitioned into exact (M)-element
classes has (N), not (N/M), classes. If a different projection really has
(N/M) retained states and accepts one of (M) conditionally uniform labels,
then

\[
T_{\rm attempt}=N^{\gamma+(1-\delta)/2+o(1)},\qquad
p_{\rm success}=N^{-\delta+o(1)},
\]

and therefore

\[
T_{\rm expected}=N^{\gamma+(1+\delta)/2+o(1)}.
\]

The arithmetic is correct. Its scope remains conditional on H-206-01 and
H-206-02; neither heuristic has been transferred to a concrete quotient.

## 3. APR-206 reconstructed from first principles

The named APR step is not a type error, but the committed tuple omits public
scalar setup needed for the exact bound. Add a certified primitive scalar
(g\in\mathbb F_N^*\), or equivalent certified generators of the two domains.
Write

\[
n=N-1=de,\qquad h=g^d\ (\operatorname{ord}(h)=e),\qquad
\omega=g^e\ (\operatorname{ord}(\omega)=d).
\]

For (x\ne0), there is a unique (k\in\mathbb Z_n) with (x=g^k), and

\[
A=[x^d]P=[h^k]P.
\]

### Stage I: recover (k\bmod e)

Let (m_I=\lceil\sqrt e\rceil). Form the typed point tables

\[
B_j=[h^j]P,quad 0\le j<m_I,
\]

and

\[
C_i=[h^{-i m_I}]A,quad
0\le i<\left\lceil e/m_I\right\rceil.
\]

Every bracket contains a public scalar acting on a group point. A collision
(C_i=B_j) is equivalent to

\[
h^{k-i m_I}=h^j,
\]

so it yields (k_0=i m_I+j\pmod e). The rectangular ranges cover every
residue modulo (e). This is vectorization in an (e)-element scalar-action
torsor, not a full (N)-element ECDLP and not an application of the nonlinear
map (R\mapsto R^d) to a point.

### Stage II: recover the (d)-element fiber

Take the canonical (0\le k_0<e) and set (c=g^{k_0}). There is a unique
(\ell\in\mathbb Z_d) such that

\[
x=c\omega^\ell.
\]

Let (m_F=\lceil\sqrt d\rceil). Form

\[
D_j=[c\omega^j]P,quad 0\le j<m_F,
\]

and

\[
E_i=[\omega^{-i m_F}]Q,quad
0\le i<\left\lceil d/m_F\right\rceil.
\]

A collision (E_i=D_j) gives

\[
x\omega^{-i m_F}=c\omega^j,
\]

hence (\ell=i m_F+j\pmod d). Return
(x=c\omega^\ell\), then verify both (Q=[x]P) and (A=[x^d]P).
The case (Q=O) returns (x=0) and additionally requires (A=O).

This derivation avoids (d)-th-root extraction: Stage I retains the exponent
class (k_0), which itself supplies a representative of the fiber. It also
shows exactly why (A) is useful in the generic group model. Without (A),
generic labels are affine in (x); with (A), labels may be linear
combinations of (1,x,x^d), and Stage I deliberately compares a public scalar
with a public multiple of the (x^d) handle.

The table counts are (O(\sqrt e+\sqrt d)). In the report's stated unit of
elliptic-curve additions, applying a general known scalar costs
(O(\log N)) additions. The supported statement is consequently

\[
\widetilde O(\sqrt e+\sqrt d)
=N^{\max\{(1-\delta)/2,\delta/2\}+o(1)},
\]

unless a unit-cost scalar-action oracle is added. Table memory has the same
exponent and also stores scalar indices/hash metadata. The exponent survives;
the literal operation count in TASK-206 does not.

## 4. Decisive Pareto objection

The committed frontier omitted the closest specialized comparator. The two
stages above are scalar-action vectorization problems. A Pollard
kangaroo/rho-style walk uses the invariants

\[
R_P=[h^u]P,\qquad R_A=[h^v]A=[h^{v+k}]P.
\]

A cross-walk collision gives (k=u-v\pmod e). Repeating the same construction
with (cP,Q,\omega) gives (\ell\pmod d). Standard distinguished-point or
kangaroo stopping/restart accounting gives expected
(\widetilde O(\sqrt e+\sqrt d)) known-scalar actions with memory exponent
zero. The walk is heuristic/randomized, but TASK-206 already treats ordinary
Pollard rho as dominating deterministic BSGS after success is charged, so
determinism cannot selectively exclude this matched row.

The corrected exponent-level comparison is:

| Row | Matched contract | Online time | Memory | Preprocessing | Aux data / solve queries | Correct disposition |
|---|---|---:|---:|---:|---|---|
| Ordinary Pollard rho | (P,Q) | (1/2) | (0) | (0) | (0/0) | ordinary frontier |
| Ordinary BSGS | (P,Q) | (1/2) | (1/2) | (0) | (0/0) | dominated by ordinary rho |
| Lossy unlabelled quotient | (P,Q) | (\gamma+(1+\delta)/2) | (\ge0) | (\ge0) | (0/0) | dominated by ordinary rho for (\gamma\ge0,\delta>0) |
| Augmented rho ignoring (A) | (P,Q,A,d,g) | (1/2) | (0) | (0) | (1/0) | dominated by low-memory two-stage search |
| Two-stage table MITM | (P,Q,A,d,g) | (\tau) | (\tau) | (0) | (1/0) | dominated by low-memory two-stage search |
| Augmented BSGS ignoring (A) | (P,Q,A,d,g) | (1/2) | (1/2) | (0) | (1/0) | dominated |
| Two-stage kangaroo/rho | (P,Q,A,d,g) | (\tau) | (0) | (0) | (1/0) | conditional augmented frontier |
| Ordinary-to-augmented | initial (P,Q) | (\max(a,\tau)) only if (a) is total expected acquisition cost | acquisition-dependent | acquisition-dependent | acquisition-dependent | unresolved; dominated by ordinary rho when (a\ge1/2) and other axes are no better |

Here (\tau=\max\{(1-\delta)/2,\delta/2\}). Relative to augmented rho that
ignores (A), the corrected low-memory row has

\[
\Delta_T=-\frac{\min(\delta,1-\delta)}2,
\qquad \Delta_M=0,
\]

with zero exponent changes in preprocessing, supplied auxiliary elements, and
solve-time queries. At (\delta=1/2), the deltas are (-1/4) in time and
(0) in memory. Thus `PF-206-05.dominated_by: null`, the stated augmented
frontier membership, and the (+\tau) memory `sota_delta` are false. This is a
revision, not evidence against the auxiliary-input time exponent.

## 5. Acquisition, setup, divisor family, and certificate audit

### Acquisition from ordinary ECDLP

In the plain generic group model, starting from (P) and (Q=[x]P), every
computed point before an informative collision has the form

\[
[a+bx]P
\]

for known (a,b\in\mathbb F_N). Group addition, negation, and multiplication
by known scalars preserve this affine span. Producing ([x^d]P) for (d>1)
is nonlinear. Equality between distinct affine labels gives a linear equation
that reveals (x); the generic birthday bound requires rho-scale work for a
constant-probability informative collision. A fixed affine output can equal
(x^d) on at most (d) field values, so for random (x) its unverified
success is at most (d/N). At the balanced (d=N^{1/2+o(1)}), that is not a
constant-success acquisition route.

This is the cheapest proof route to falsify an ordinary-ECDLP interpretation.
It does not exclude a non-generic pairing, multilinear, leakage, or oracle
source; any such source must be specified, typed, and charged. The exponent
(a) must mean total expected cost of outputting a correct (A), including
its inverse success probability. If (a) is merely per-attempt cost, the
formula (\max(a,\tau)) is incomplete.

### Public setup and balanced divisors

Exact coverage requires known orders (e) and (d) and certified generators
(h,\omega), conveniently derived from a primitive (g). The package supplies
only (d\mid N-1). It must either add (g) and an order certificate/factorization
to the public contract or charge their construction as target-independent
preprocessing.

The one-quarter row additionally requires a family with

\[
d\mid N-1,\qquad d=N^{1/2+o(1)},\qquad (N-1)/d=N^{1/2+o(1)}.
\]

No such target family is exhibited. TASK-206 correctly labels it open, so the
row may remain only as a conditional algebraic optimization, not a realized
SOTA comparison.

### Data and certificates

The scalar certificate is sound: checking (Q=[x']P) proves the ordinary
answer, and checking (A=[(x')^d]P) proves augmented-input consistency. Both
use public scalars and (N^{o(1)}) operations. The encoded auxiliary point is
(\Theta(\log p)) bits, not automatically (\Theta(\log N)); the latter
needs the missing family assumption (\log p=\Theta(\log N)). The auxiliary
element count remains exactly one and target-specific, so no cross-target
amortization is available.

## 6. Cheapest falsification controls — proposals only

No experiment was executed. The following are ordered from cheapest to more
expensive.

1. **Typed proof check (candidate):** require every table/walk state to carry
   one of the four invariants displayed in Section 3 or 4. A collision not
   implying the stated congruence falsifies APR-206 immediately.
2. **Hand-checkable algebraic unit instance:** use
   (N=13,d=3,e=4,g=2,h=8,\omega=3,x=11=g^7). Then
   (A=[5]P), Stage I returns (k_0=3\pmod4), and Stage II returns
   (\ell=1\pmod3), hence (x=8\cdot3=11\pmod{13}). This is a proposed
   unit control, not executed evidence.
3. **Low-memory comparator:** instantiate identical hash/jump rules on the two
   torsors and pre-register expected stopping, restart, group-addition, and
   memory counts. This tests the Pareto correction, not the algebraic theorem.
4. **Correlation null:** replace (A) by a uniform independent nonzero group
   element or permute (A) across instances. Full verifier acceptance should
   occur only when the accidental scalar equals (x^d), probability
   (1/(N-1)), up to sampling details.
5. **Generic-span acquisition proof:** formalize the affine-label invariant and
   collision bound before considering any ordinary-input implementation.
6. **Family gate:** factor or otherwise certify the advertised (N-1) and
   reject the balanced row unless both domain sizes have exponent (1/2+o(1)).

## 7. Final scope

`REVISE` is required because the Pareto `dominated_by` and quantitative memory
delta are wrong and because the exact input/setup and operation units are
incomplete. The narrow fixed-field barrier and quotient correction should be
preserved. The auxiliary-power idea is a valid augmented-input mechanism once
its public scalar setup is added; it is not an ordinary-ECDLP improvement, a
status transition, a closure result, or a breakthrough claim.
