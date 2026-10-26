# Native weighted joint-smallroot implementation contract

2026-10-26. GOAL-PFDR-fd09e0; BATCH-ee839d. This additive implementation
specification preserves the mathematical workload in the completed
BATCH-3cfef2 design. It does not approve a scientific experiment. No native
port, theorem applicability, root recovery, or IC improvement is established.

## Ownership and executable architecture

The implementation belongs to `isogeny-labs/crypto`, based on
`e8fcadf62cd0b674c40ebc4e76dfe88e26e71f5c`. Reserve exactly
`experiments/joint-smallroot-native/` through an actual owner Conductor task
before editing. A previous `check` returning allow is not a reservation. Read
the owner's AGENTS and active card; if `.conductor/WORKFLOW.md` is absent,
record that fact and follow the real installed task workflow, without creating
a substitute permission file. No shared tools or owner legacy probes are in
scope. The local coordination queue cannot reserve files in another repository;
the owner card and its reservation receipt supply that distinct gate.

Use C++17, GMP exact integers/rationals, native Singular 4.4.1 for ideal/normal
form operations, and a pinned native cddlib/GMP rational polyhedron component.
These are selected dependencies, not a claim that all are provisioned. Build
and lock the actual compiler, flags, libraries, binary SHA-256s and licenses.
Singular input scripts may be generated and run as native CAS programs. No
Sage, Python research process, compiled Python wrapper, or relocated Python
implementation is permitted. The pinned cuso source is read-only reference.
Different backends may have different cost; no performance equivalence follows
from mathematical compatibility.

Suggested owner files, all under the single reserved directory: `CMakeLists.txt`,
`src/main.cpp`, `src/exact_polynomial.cpp`, `src/order.cpp`,
`src/ideal_backend.cpp`, `src/optimal_shifts.cpp`, `src/polytope.cpp`,
`src/statistics.cpp`, `src/supervisor.cpp`, corresponding headers,
`tests/structural.cpp`, `spec/`, `LICENSES/`, `README.md`. This is the full write
scope, not an instruction to edit existing owner build files. Place the standalone
build inside that directory. A required scope expansion returns to Coordinator
before editing outside it.

## Exact object and finite plan

The authoritative design input is
`coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-3cfef2/tasks/TASK-20261025-b7e32e/`
at snapshot `d1387a9d7f6bb31840a26cde4d5213cb737e05ea`. Keep its files immutable.
The native backend is an additive change to the old Sage dependency preview;
the final prospective protocol must identify this change and stay
`review_required`, `approved_by: null` until its later runnable approval.

Implement, over QQ,

```
S(A,B,C)=(A-B)^2*C^2-2*((A+B)*(A*B+a)+2*b)*C+(A*B-a)^2-4*b*(A+B)
F1=S(c1+z1,c2+z2,d1+h1)
F2=S(c3+z3,c4+z4,d2+h2)
F3=S(d1+h1,d2+h2,q)
```

Freeze `a=2,b=3,q=5`, centers `(11,13,17,19,23,29)`, coordinate order
`(z1,z2,z3,z4,h1,h2)`, formal ring order `(p,z1,z2,z3,z4,h1,h2)`.
`p` is a polynomial variable in characteristic zero, never an assigned prime
for these symbolic cells. `J=(p,F1,F2,F3)^mu`, `J_inf=(0)`, divisor bound 1,
all relation and modulus degrees 1. Exponent tuples always include the leading
modulus coordinate. For E the union of exact nonzero supports, enumerate
`conv({0} union {mu*e:e in E}) intersect Z_nonnegative^6`, using seven-coordinate
vertices `(0,mu*e)` including zero. Do not substitute the archived discrete
Minkowski support for this initial integral convex domain.

The ordered cells remain `(r,mu)=(2,1),(2,2),(4,1),(4,2)`, each with ordered
arms `F1_single,F2_single,F3_single,joint_A,joint_AA,nearby_A`: exactly 24 cold
symbolic calls, none executed by this implementation task. Single blocks use
only active coordinates and project bounds/domain by the same construction;
F3 has two unknowns. A/A has byte-identical canonical algebra input/options
in a separate process. Freeze nearby coefficients by the exact SHA256 rule in
the original report; retain supports. No new ray, mu, order, generator reversal,
t-shift, retry, root search or parameter search is authorized.

Bounds weights are `(1,1,1,1,r,r)`, `bounds_guess=weights/20`,
`beta=delta,gamma=r*delta`. The ring's weighted degree then lex order uses
`round(1000*(1,bounds_guess))`; for joint cells this is exactly
`(1000,50,50,50,50,50*r,50*r)`. All t-shifts are false, `skip_reduce=false`.
The order must be implemented and audited, rather than inferred from the
name of a Singular order. A candidate Singular representation is
`(a(weights),lp)`; confirm its exponent comparisons against the pinned
Sage `wdeglex` definition and seal hand-derived comparison fixtures first.
Any mismatch is an interface failure, not grounds to choose another order.

## Native algorithm and compatibility joints

Map each stage to pinned cuso commit
`fb2747d2105a8e48499bf10a3a717cf80c14d079` and record file hashes.

1. **Exact polynomial layer:** sparse ordered exponent tuples with reduced
   GMP rational coefficients; combine equal terms, remove zero coefficients,
   and serialize rational numerator/positive denominator in decimal strings.
   Retain exact expanded equations, support union, vertices and projected
   variable maps. Separate modulus powers from stripped monomials exactly as
   `symbolic/utils.py` does. Its leading-coefficient selection and polynomial
   comparisons must be reproduced literally, including ties and signs; do not
   replace them by a numeric size heuristic.
2. **Ideal layer:** generate every degree-mu product of the four generators
   and obtain the reduced ordered QQ Gröbner basis in native Singular. Retain
   generator and basis order, full rational coefficients, normal forms and
   options. Verify the actual reference normalization/ordering from static
   source; ideal equality alone does not establish identical later choices.
   Empty `J_inf` has no unravel constraints in this restricted first panel.
3. **Finite domain:** obtain rational H-representation in its affine span with
   cddlib/GMP. Enumerate nonnegative integer coordinate bounding boxes and
   retain points satisfying every exact rational facet/equality. The leading
   p exponent is zero. Preserve the complete ordered point list and facets.
   No floating hull, nearest-point approximation or sampling is allowed.
   A costly enumeration is guarded and reported, not silently truncated.
4. **Optimal-shift closure:** follow `symbolic/optimal.py`: ascending sorted
   initial M and FIFO queue; for m choose dividing stripped-leading-monomial
   basis candidates, then the reference minimum leading coefficient;
   `h=(m/lm_no_N(g))*g`; `h'=lt(h)+NF_J(h-lt(h))`. Append every newly seen
   stripped monomial in the reference order, preserving `M_bar` and `S_bar`.
   Do not replace this with arbitrary multiples, a Gröbner basis alone or
   normal-form reduction of the whole h.
5. **Echelon intersection:** coefficient entries are polynomials in p over QQ,
   embedded in the full polynomial ring. Build B with the original M prefix
   in `M_bar`; reverse rows and columns, apply the reference default
   constant-pivot row reduction, then reverse both back. This is *not*
   fraction-field RREF or row Hermite form. Installed Sage 10.9
   `matrix_mpolynomial_dense.pyx:_echelonize_row_reduction` scans columns,
   chooses the first available nonzero constant pivot, normalizes it by a
   rational scalar, eliminates that column from all other rows, and refreshes
   which remaining entries are constants. A column with no constant pivot is
   skipped. Native port must retain the exact pivot/row-operation trace.
   Keep only rows with zero entries outside the original M prefix; reconstruct
   S exactly, preserving zero-row behavior or classifying any failure.
6. **Augmented statistics:** port `shift_set_properties.py` literally for
   empty `G_inf`, zero t-shifts. Form the convex hull of stripped supports of
   S, include integral points, and build the dominated leading-p-exponent
   valuation map as in `AugPolyhedron.from_polytope`. Preserve reference
   duplicate-key overwrite order. Construct k-fold point sums and valuations
   by exact pairwise convolution and minima; retain distinct point sets and
   maps. Do not replace their discrete sums with convex hull refilling.
   For each k retain dimension/count, each coordinate exponent sum, and p
   exponent sum. Record the affine hull dimension d actually used.
7. **Interpolation/limit:** with no t-shifts, evaluate exactly at
   `k=1,...,d+3` and use rational Lagrange interpolation. Enforce degrees
   `s_dim<=d`, `s_x_i<=d+1`, `s_C<=d+1`; a violation is a retained failure.
   Form exactly `(k*s_dim-s_C/mu)/sum_i(weights_i*s_x_i/mu)` for these pure
   linear bounds (general constants remain zero). Retain numerator,
   denominator, cancellations, degrees and leading terms; unequal degrees or
   zero denominator follow the reference failure path. Otherwise retain the
   exact leading-coefficient ratio as uncapped `delta_star` and zero
   `tau_cuso`. Report its domain cap `0<delta<1/r` with strict-endpoint
   semantics, then beta, gamma, `V=4*beta+2*gamma` and `V/3`. Do not confuse
   tau_cuso with an attack-cost exponent. Retain each denominator coprimality
   condition from S and all specialization obligations.

The source-to-native function map, Sage comparator/normal-form/basis-order
semantics and literal coefficient-map behavior are deliverables. If any is
not established, return a partial implementation with an explicit gap and a
minimal repair test; never claim compatibility from compilation or a banner.
No joint algorithm may be executed just to fill this gap during this task.

## Controls, validation boundary and execution protection

Prepare the original exact F_101 sign/tree/divisibility/corruption control:
P=(1,39), T=(3,6), R=(41,15), all eight sign triples, repeated leaves
P,T,P,T, internals R,R, target 2R, zero deviations about centers
(1,3,1,3,41,41). `F1+1` must fail at the planted tree. This source is prepared
but its scientific control invocation is deferred to the later frozen panel.
Bind the already published univariate `delta*=1/3` calibration as historical;
do not rerun Sage or assert that the native port has reproduced it. Exact
polynomial zeros alone do not certify y-lifts, sign compatibility, subgroup
membership, root extraction or verified DLP recovery.

Allowed implementation checks: compiler/link checks and fixed hand-derived
codec, exponent-order, rational arithmetic, facet-membership and constant-pivot
matrix unit fixtures, outside the panel. Seal their expected values before
invocation; retain commands and failures. Forbidden here: any joint/single-block
scientific cell, ideal/shift bound measurement, univariate bound computation,
lattice reduction, root extraction or numerical tuning. Unit fixtures cannot
be reported as scientific observations or native cuso equivalence.

Prepare a native supervisor requiring cgroup-v2 delegation; set memory.max to
8589934592 bytes, record memory.peak and memory.events, require at least 12 GiB
host MemAvailable, and launch one cold process at a time. The process tree
belongs to the cgroup. Use a monotonic 1800-second per-call watchdog; on expiry
kill the whole cgroup/process group and retain partial artifacts. If actual
delegation/guards are unavailable, mark infrastructure-not-started; do not
substitute parent-RSS polling or an unguarded launch. These are protections,
not a campaign spending cap. No automatic retry or parameter escalation.

Archive per call: canonical input and digest; environment/dependency lock;
generated Singular source; stdout/stderr, exceptions/exit/signal; every stage
start/stop, wall/CPU measurement and memory field with unavailable values
explicit; basis/ideals, M/M_bar, shifts, row operations, valuations,
interpolation samples/polynomials and denominators; supervisor receipt and
failure checkpoint. Prepare all 24 status slots and record complete, failed,
censored or not_started with reason. Failed exact control stops the panel;
other algorithm errors retain costs and proceed only if the guard is healthy.
Reduction and extraction status is `not_requested`, never a zero-cost success.

The producer prepares source, trialplan, supervisor, variable ledger, formal
transfer assessment, archive coverage, exact prospective protocol/packet and
compile-mode Director request. It does not approve or run them. Native source
and dependency hashes must be committed and pushed in crypto before its
programme snapshot and independent review dispatch. Reviewers receive a
content-bound implementation manifest and sealed blind statement first;
normalization review opens the implementation only after sealing its own
derivation. The full Ryan paper, Algorithm 3/Lemma 7 and theorem assumptions
remain an explicit literature gap until actually retrieved/read independently.

## Evidence and original request

Sources inspected statically: frozen report/applicability/contract/next-handoffs;
readiness manifest and finite audit review; the selected lead atlas entry;
cuso `asymptotic.py`, `ideal.py`, `utils.py`, `optimal.py`, `polytope.py`,
`shift_set_properties.py`, `polynomial.py`, `limit.py`, and `COPYING.LESSER`;
installed Sage 10.9 matrix source. These support an implementation
specification, not theorem applicability or novelty. Preserve LGPL-3.0-or-later
and any other applicable source/license obligations in the native port.

Original requirements remain open: establish the joint-system reach-cost
tradeoff, then demonstrate a verified improvement over a named frozen current
prime-field IC baseline. The first symbolic panel addresses only the
construction/weighted reach observation. Future root extraction, success and
full cost, matched curve/subgroup/target identities, end-to-end IC baseline,
matched rho gap, independent replay and progress-fidelity claims remain
required. This implementation handoff neither replaces nor satisfies them.
