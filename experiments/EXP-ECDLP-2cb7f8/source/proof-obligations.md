# EXP-ECDLP-2cb7f8 implementation derivation obligations

TASK-20260907-73cd8f; implementation-only material for Coordinator readback.
No scientific run, proof checker, exhaustive finite case, or independent semantic
review was performed. These are explicit derivation notes and review obligations,
not a theorem-status or hypothesis-status change. Source authority is the frozen
specification SHA256 `e7ea730e68d674a4de0ef6cdbc159d98ff4473a9b9539f9b18b1da52c936659e`.
The inherited primary-source attributions are in `primary-sources.json`; this
Executor read the internal specification, not the external pages.

## L1 — charts and inverse

Use a symbolic curve constant B in y^2=x^3+x+B. The four original cases set B=1;
the explicitly specified N0 curve sets B=2. With X0=1 the first quadric sets
X3=x^2 and the second becomes the original cubic. With X0=0 the quadrics force
X1=X2=0; the nonzero-vector condition leaves O. `projective_inverse` rejects the
zero vector, noncanonical residues and either nonzero quadric residual before
returning an affine point or O.

On X3=1 write w=X0/X3, u=X1/X3 and v=X2/X3. Then w=u^2 and
v^2=u+u*w+B*w^2=u+u^3+B*u^4. This derivation fixes the N0 infinity recurrence
without silently using B=1 there. In the O chart v=t, u0=w0=0. The coefficient
of each new u_k in t^2-u-u^3-B*u^4 is -1, so the successive coefficients are
unique. The numerical implementation recomputes the residual through t^4.
Future finite checks must verify both charts and the inverse on every point.

## L2 — basis and total degree

The frozen standard ingredients assign pole orders 0,2,3,4 at O to 1,x,y,x^2.
Distinct pole orders make these four functions linearly independent. The positive
degree genus-one Riemann–Roch dimension gives dim L(4O)=4. A nonzero section has
div(f)+4[O] effective of total degree four. This is the inherited standard
geometric premise that still needs semantic review; no lower complexity follows.

The O trivialization evaluates (w,u,t,1). The formal recurrence starts u=t^2
modulo higher terms and w=t^4 through the specified precision. Thus the section
can have order four without having a zero affine function. The implementation
checks the O order even when the pole deficit is zero, and reconciles rational
plus unresolved degree against four. It does not infer exhaustion from ordinary
point-incidence rows.

## L3 — multiplicity, rank and descent of coefficients

For D of degree four, the vanishing section space is L(4O-D). A degree-zero
divisor class has a nonzero section precisely when it is principal; in that case
the section space has dimension one. The standard curve/Pic0 identification
relates this class condition to the group sum. Consequently the geometric
expectation is matrix rank three on relations and four on nonrelations.
Rank below three is retained as an anomaly rather than treated as success.

The numerical matrix has exactly four rows, one for each prescribed local
coefficient j<m at each support point. Repeated evaluation rows are not used.
All coefficients lie in the base field, so ordinary extension of scalars does
not alter matrix rank; a one-dimensional kernel admits a normalized base-field
vector. Exact modular elimination returns the entire kernel basis and RREF.
The caller separately computes A_D*c, recovers the section divisor without
oracle input, and retains the full recovery certificate.

The oracle implementation is independently structured affine chord/tangent
arithmetic and never imports the incidence module. Only the orchestration code
compares its sum-zero decisions with already computed incidence outputs.
Independent Validator replication is still required after a future run snapshot.

## L4 — recovery and exceptional multiplicities

When c2 is nonzero, quotienting the affine coordinate ring by the section permits
substitution y=-h(x)/c2, leaving F=h^2-c2^2*(x^3+x+B). Local quotient lengths
are preserved by this elimination. Thus repeated division of F by x-a records
affine intersection multiplicity, including a ramified finite point. If c3 is
nonzero F has degree four; otherwise the cubic coefficient is nonzero and its
degree is three. The infinity multiplicity is the remaining degree deficit.

When c2=0, h is a nonzero polynomial of degree 0,1 or 2. A rational root a of
multiplicity e contributes e at each of two nonzero opposite y values, or 2e
at a ramified y=0 point. A nonsquare right side contributes unresolved degree
2e. A residual nonconstant h contributes twice its degree. Infinity contributes
4-2*deg(h). A nonzero constant section therefore has no affine zero.

Finite charts use the exact formal recurrences with checked denominators 2b or
3a^2+1. No factorial division occurs. Every rational support multiplicity is
checked against independently reconstructed B and I local sections through t^4.
Every rational root, division quotient, residual polynomial, square witness,
O order and unresolved degree is serialized. An exception carries the exact
input c or D in the anomaly stream and invalidates affected instrument use.

## L5 — quotient and ordered count

The raw input divisor is a sorted four-index multiset; each distinct support
point retains its multiplicity. Its orbit weight is 4!/product(m!). This weight
restores an ordered count, not any particular original ordering. An independent
oracle-only ordered-triple loop determines the fourth point and builds a full
canonical orbit histogram. It is compared with each accepted divisor set and
its weights. The symbolic group-size expectation already frozen in the protocol
is retained; no new group-invariant formula is supplied here or substituted for
future blind Red Team derivation.

## L6 — complete presentation compiler and conventions to review

The compiler uses sparse polynomials over each declared field. It constructs
all five-coefficient curve equations, all prescribed section jets, inverse
constraints, distinctness branches and rationality equations for every variable.
It uses fixed chart substitutions only. I retains its independent z or w
coefficient variables and equations. No Groebner elimination, solved-variable
substitution, asymmetrical optimization or occupancy pruning occurs.

The implementation makes the following serialization choices explicit so the
Coordinator can accept them or issue an additive amendment before a lock:

- Integer partitions are in descending multiplicity order. Support slots are
  serialized by descending multiplicity and then canonical point index; input
  and recovered divisors themselves remain sorted point-index lists. Every chart
  assignment with at most one O is emitted, including empty templates. Equal
  multiplicities retain the canonical point-index tie order in occupancy.
- The first nonzero coefficient chart substitutes c_i=0 for i<k and c_k=1;
  remaining coefficients are variables. No extra scaling variable exists after
  this frozen normalized-chart substitution. Similarly y=t fixes b=0 on the
  ramified chart; its zero equation is omitted and no unfixed b is introduced.
- Monomial normalization uses descending lexicographic exponent vectors over
  lexicographically sorted variable names, scales the leading coefficient to
  one, and removes exact duplicate equations only within a branch.
- `recovery_case_count` counts the twelve explicitly emitted named decision
  branches: five section-degree branches, three y-root outcomes, two residual
  factor outcomes and two O-presence outcomes. They are a decision-tree inventory,
  not twelve disjoint terminal combinations. Both arms share the identical
  inventory. The frozen text does not specify whether its scalar case count
  instead intends terminal combinations; this semantic ambiguity requires
  Coordinator resolution before using that coordinate or locking the metric.

The last point is an exact unresolved metric convention, not a measured result.
The code exposes every named branch and its condition so resolution is concrete.
The primary full-polynomial count includes rationality; finite-field-typed
counts and maximum degrees are reported separately. Full branch equations and
occupancy are streamed to one JSON artifact to avoid retaining the entire
expanded inventory in memory.

## L7 — accounting and execution boundary

Each arithmetic subsystem counts additions (including subtraction),
multiplications, inversions and field equality tests through explicit arithmetic
methods. Inversion is counted as a field operation; its implementation and
verification still contribute to measured CPU and wall time. Python indexing,
sorting, hashing, tuple comparisons, serialization and symbolic monomial
bookkeeping contribute to timings and memory, not invented field-op counts.
There is no amortization or reuse discount. Setup/group controls, B and I forward
work, shared inverse work, group verification and symbolic compilation are
separate accounting entries; complete arm comparisons must add shared costs to
each arm. Raw branch compiler operation counters are retained as measured work,
not a factoring-cost model.

The future canonical wrapper must enforce one worker and 8 GiB, verify the real
source/lock/claim/environment, record total setup/package CPU and wall costs,
capture stdout/stderr and create the repository-compatible immutable manifest.
Current CLI refusal makes this unresolved interface visible and prevents a
candidate plan from being mistaken for a LOCKED authorization. The prototype
instrument function cannot be treated as an independently validated runner.

The Lean semantic bridge remains deferred exactly as in the frozen protocol:
local section coefficients, rational effective divisors and serialized finite
group points need pinned compatible definitions and an admitted target. Generic
matrix-nullity compilation would not discharge the full correspondence.
