# Incremental Miller/Z evaluation: derivation and known-answer prototype

TASK-20261029-7c9190, 2026-10-29. This is source inspection, a mathematical derivation and known-answer software checking. It contains **no new cohort evaluation, benchmark, old-cohort reanalysis, scientific trial or scientific status decision**. The proposed empirical comparison is separate and unapproved. The previous cohort describes its fixed circuits and sampled curves; it does not settle broader arithmetic, statistical or algorithmic leads.

## Object and prior work

The tracked state is `(R,Z(R))`, under public doubling or public addition with a known tracked point. Keeping R makes this an augmented arithmetic representation, not a lossy quotient or a newly discovered scalar-information primitive. Removing repeated reconstruction can still improve an implemented procedure, and is a concrete thing to test.

Internal IDEA-20261016-09fd08 already states that the additive zeta defect can be tracked on affine walks using slopes computed by the group law. Its unreviewed predictions about scalar correlation are not evidence for or against the present implementation. The existing ordered-root note derives the normalized Miller coefficient and its cocycle. Current `constructor.py`, `curve.py`, `compute.py` and `verify.py` were read directly. Their source hashes and immutable locators are in `sources.json`.

Voloch's [1997 paper, Sections 1–2 and Proposition 2](https://www.math.canterbury.ac.nz/~f.voloch/Pdfs/zeta3.pdf) supplies the characteristic-p zeta addition law and its universal-extension setting. That rational function lives on the Frobenius-twisted curve; this report does not silently identify its whole-curve domain with this subgroup implementation. The finite subgroup identity below follows using the stated normalized divisor functions. The author-hosted PDF was read through the web tool; an additional byte-download request returned HTTP403, so no original-PDF content hash is asserted. Miller's [2024 retrospective, Sections 1–3](https://drops.dagstuhl.de/storage/00lipics/lipics-vol291-fun2024/LIPIcs.FUN.2024.34/LIPIcs.FUN.2024.34.pdf) distinguishes compact straight-line evaluation from expanded rational expressions; it is contextual prior art, not a proof of this prototype.

Bounded live GitHub searches covered all three repositories. Inspected `crypto` pairing/Kummer implementations and `cryptanalysis` Tate code evaluate ordinary Miller line functions. They are not this normalized-Z sequence implementation. Empty exact-symbol queries do not establish implementation absence or novelty; branches, alternate names and unindexed files remain gaps. Knowledge-index MCP tools were unavailable. The local frontier, proposals and lead atlas were consulted after materialization.

## Derived identity and exceptions

Let `p>3`, E be a nonsingular short Weierstrass curve, and G a subgroup of odd prime order `r != p`. For nonzero R in G, normalize the divisor function using `t=-x/y`:

`div(f_r,R)=r[R]-r[O]`, `f_r,R=t^(-r)(1+C_r(R)t+...)`, `Z(R)=-C_r(R)/r`.

For an ordinary chord/tangent addition, the normalized line/vertical quotient has first Laurent coefficient equal to the group-law slope lambda. Divisors and normalization give

`f_r,R+S = f_r,R * f_r,S / g_R,S^r`,

hence `C_r(R+S)=C_r(R)+C_r(S)-r*lambda(R,S)` and

`Z(R+S)=Z(R)+Z(S)+lambda(R,S)`.

Take `Z(O)=0`. Identity additions have lambda zero; inverse-point additions use the normalized vertical coefficient zero and oddness `Z(-R)=-Z(R)`. Nonidentity doubling in an odd-order subgroup cannot be vertical or reach O. A two-torsion tangent would be vertical, but nonzero two-torsion is outside this domain. The source's subgroup check in the initial Miller chain rejects an inconsistent declared subgroup. Dividing by r requires `r != p`; the anomalous case is not covered by this construction.

Thus `Z(2R)=2Z(R)+lambda(R,R)`. An induction proves exact state propagation once the initial Z is correct. Uniqueness follows because two such normalized primitives differ by a homomorphism from the r-group to the additive p-group, which is zero when r and p are coprime. This derivation concerns the primitive, not any correlation of its character with scalar ordering.

## Prototype and actual software checks

`prototype.py` initializes Z once per public attempt using the unchanged `normalized_miller_coefficient`. It shares the slope from the reduction's existing `add_with_slope(current,current)` call. It then applies the same fixed circuit and Legendre character. No scalar labels, orbit table, target search, persistent cache, RNG or scientific CLI enter its public API.

The matched primary reference is **`compute.py::ungated_attempt`**. The legacy `constructor.py::conditional_recover` exits early and is not the reference. The prototype keeps all L=`bit_length(r)+1` calls, including calls after a zero-numerator `UNDEFINED`, and retains all non-counter fields: query points, Z/numerator/anchor/normalized values, bits/status/reasons, interval, candidates, inverse multiplier, and both public checks. Setup-level undefined and wrong-root controls retain their original evaluation branches. State is local to each attempt and resets automatically. Original source files were not edited.

Actual command, Python version, return code, complete stdout/stderr and tested source hashes are in `software-checks.json`. The single invocation passed **11 software tests** on disclosed F11 and F23/order17 fixtures. These test assertions cover original A/A equality, exact non-counter witness equality, the historical public recovery, a fixed nontrivial public blinding, undefined setup, zero numerator with continued calls, identity/inverse conventions, malformed/off-subgroup rejection, state reset, and a deliberately wrong-sign recurrence. The wrong-sign test requires a mismatch rather than counting it as a prototype failure. No initial failed invocation was produced or discarded.

Two hand-derived checks anchor the arithmetic independently of baseline-output equality:

- On F11, `P=(2,7)`, `Z(P)=3`, tangent lambda=8, so correct `Z(2P)=3`; subtracting the slope instead gives9. The mutation test detects this exact difference before interpreting recovery.
- On `E/F23:y²=x³+11x+5`, `r=17`, `P=(5,22)`, the r-chain has tangent slopes3,4,1,21 followed by a vertical addition and coefficient D=17. Thus `Z(P)=-17/17=22`. Successive doubled queries have Z values22,1,6,13,1,22, and the fixed circuit2.a1 bits are0,0,1,0,1,1. These are named software fixtures, not a new scalar-success panel.

The test counter assertions check this source instrument on known cases. They do **not** independently qualify operation-counter execution or elapsed-time advantage. The unittest duration retained verbatim is software-run telemetry, not an algorithm benchmark. The prototype also imports the original arithmetic and interval/conversion helpers; it is not an independent arithmetic implementation or a production runner.

## Derived cost prediction and retained work

For a ready candidate on nonzero r-subgroup targets, put b=`bit_length(r)`, h=`popcount(r)`, L=b+1. The binary Miller function makes `C_r=b+h-2` group-add calls per target evaluation. Original evaluation uses L chains. Incremental evaluation uses one chain and L-1 updates `2z+lambda`, with the slope shared from the same reduction doubling.

The prediction therefore removes `(L-1)*C_r` group-add calls from the repeated-Miller component. Each state update is separately charged as a field multiplication by2, field addition, their reductions, and an update event. Initial-chain normalization and every operation actually executed remain counted. Setup/preparation, target blinding, membership, circuit arithmetic, Legendre powers, RNG, scalar inversion/conversion, interval logic, public checks and common fixture work remain visible. The new `state_updates` vector is additive: do not also charge its shared slope as a second group operation.

This is a source-level component prediction. Each unchanged Legendre character still uses O(log p) field multiplications across L queries. Neither a total speed ratio nor a new p-exponent follows from the removed group calls. End-to-end Pareto dominance is unassessed; matched original recovery and working BSGS remain comparison references. `sota_delta`: no qualified end-to-end increment measured in this task.

## Next discriminating experiment

`experiment-design.json` specifies a **proposal**, not `experiment.protocol/v1` or execution authority. Before trials, independently inspect the prototype and derive the primitive on held-out cases; implement an independent counter-replay instrument; freeze exact source, input generation, arms, case count, public schedules, analysis and runtime; obtain actual admission through the existing route.

Require exact paired trace equivalence and preserve all undefined/failed/zero outcomes. A mismatch is an implementation discrepancy to isolate; it does not refute the family. Equivalent traces with smaller, equal or larger charged totals are all reportable observations. Counter or isolation gaps leave cost or timing unqualified, rather than assigning a mathematical negative. The fresh panel can confirm implementation behavior on its declared sampling frame, not scalar-ordering universality or novelty.

A later distinct variant can compute Z(Q) once per target and propagate it through public blinding chains before the doubled queries. Charge target preparation T(Q) separately: `S_curve + T(Q) + E_online/q`. This could help a public-multiplier list decoder's query budget without implying predictor bias or recovery gain. Shared-circuit portfolios would need explicitly common public query schedules and full portfolio setup costs; the historical independent arm streams cannot be retroactively repriced. An unresolved symbolic question is whether the fixed character numerator itself admits a cheaper update; no such identity is supplied here, and failure of a bounded ansatz would concern only that ansatz.

No canonical graph or historical report changes follow from these software checks. Parent synthesis will supply the search-round diagram/PDF; all historical evidence, hypotheses and goal statuses remain unchanged.
