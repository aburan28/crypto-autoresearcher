# FC0 revision note — GOAL-SSI-001 BATCH-008

Task `TASK-20260729-005` · access date 2026-07-29  
Revised convention: **CSIDH-COLLIMATION-FC0-R1**  
Resource-memory posture: **Peikert unconstrained collimation with explicitly
reported QRACM** (not resource-constrained/SQALE-style)

## 1. Revision boundary

`CSIDH-COLLIMATION-FC0-R1` remains a logical-resource accounting control for
the final Peikert binary collimation-sieve row. It does not select a physical
architecture or produce a scalar security label. The instance tuple, binary
arity, punctured regularization, nine-lookup QRACM variant, classical residual
search, and sequential-oracle canonical schedule remain as in FC0 unless
changed below.

R1 uses the Peikert side of the `KN-TECH-051` resource dispute: it chooses a
collimation-sieve tradeoff point and reports its QRACM, coherent width, query,
and circuit resources, but imposes no exogenous cap on quantum-accessible
memory. Choosing the minimum-QRACM nine-lookup implementation is an algorithmic
tradeoff choice, not a SQALE-style resource bound. A resource-constrained row
would require a separately named convention and cannot borrow R1 values.

## 2. Typed symbols

Let \(\mathcal I_{\rm src}\) be the ordered multiset of top-level sieve
invocations required by the source recovery schedule. A discard, failed
postprocessing attempt that requires a fresh sieve, or externally repeated
attack is a separate member of \(\mathcal I_{\rm src}\). For each
\(i\in\mathcal I_{\rm src}\):

- \(Q_i\) is the number of complete labeled-state \(U_{\rm HS}\) calls;
- \(T_{{\rm sieve},i}\) and \(T_{{\rm post},i}\) are logical T-counts for that
  invocation;
- \(C_{{\rm sieve},i}\) and \(C_{{\rm post},i}\) are classical work;
- \(R_{i,v}\) is QRACM bits at node \(v\);
- \(\mathsf{Live}_i(t)\) is the set of coherent registers live at schedule
  time \(t\).

The source anchor is retained under its source name:

\[
Q_{\rm attack}:=\widetilde Q_{\rm total}
  =\sum_{i\in\mathcal I_{\rm src}}Q_i .
\tag{R1-Q}
\]

Peikert Figure 1 defines \(\widetilde Q_{\rm total}\) as the total oracle
queries used to recover all but the residual secret bits. Therefore R1 has no
generic \(R_{\rm success}\widetilde Q_{\rm total}\) multiplier. An external
repetition factor is admissible only if a cited source leaves a statistically
independent repetition outside \(\widetilde Q_{\rm total}\); it must then add
new members to \(\mathcal I_{\rm src}\), not multiply queries alone.

## 3. O1 — aggregate queries and repeated sieve work

### Concrete equation change

FC0's scalar equation is replaced by the per-invocation ledger

\[
\begin{aligned}
T_{\rm full}
  &= T_{\rm qpre}/K
   +\sum_{i\in\mathcal I_{\rm src}}
      \left(
        \sum_{j=1}^{Q_i}T_{U_{\rm HS},i,j}
        +T_{{\rm sieve},i}
        +T_{{\rm post},i}
      \right),\\
C_{\rm classical}
  &= C_{\rm cpre}
   +\sum_{i\in\mathcal I_{\rm src}}
      \left(C_{{\rm sieve},i}+C_{{\rm post},i}\right)
   +C_{\rm tail}.
\end{aligned}
\tag{R1-FULL}
\]

The shorthand \(Q_iT_{U_{\rm HS}}\) is allowed only after proving all calls in
that invocation have the same charged oracle implementation. The default is
\(K=1\); any amortized \(K>1\) still requires a reusable-output proof and a
declared target population.

### Source-reconciliation consequence

Figure 1 and Section 4.1 pin \(\widetilde Q_{\rm total}\), the expected bits
recovered per run, and the residual classical search. They do not expose an
exact \(\mathcal I_{\rm src}\) with every fresh-sieve discard, recovery
invocation, and stopping event. Therefore Equation (R1-Q) is source-typed, but
the separate sums of Equation (R1-FULL) cannot yet be instantiated without
inventing a schedule. This is an explicit unresolved field, not permission to
charge one sieve traversal.

## 4. O2 — classical-tail type

The canonical R1 tail is classical:

\[
Q_{\rm tail}=T_{\rm tail}=D_{\rm tail}=W_{\rm tail}=0.
\tag{R1-TAIL-Q}
\]

Let \(\mathcal X_{\rm tail}\) be the source-defined residual candidate set,
\(n_{\rm act}^{\rm tail}\) the number of classical action evaluations under a
declared enumeration and stopping rule, and \(C_{\rm act}^{\rm cl}\) their
unit cost. The charged tail is

\[
\begin{aligned}
C_{\rm tail}
  &= C_{\rm enumerate}
    +n_{\rm act}^{\rm tail}C_{\rm act}^{\rm cl}
    +C_{\rm verify},\\
M_{\rm tail}
  &= \max_t M_{\rm tail}(t).
\end{aligned}
\tag{R1-TAIL-C}
\]

The stopping rule must say whether search ends at a uniquely verified
candidate or after exhaustive failure, and must define its resulting
\(\epsilon_{\rm tail}\). Until these source fields are supplied,
\(C_{\rm tail}\), \(M_{\rm tail}\), and \(\epsilon_{\rm tail}\) remain named
unknowns. A quantum residual search is a separately named schedule with its
own query, T-count, depth, width, and error row.

## 5. O3 — composable oracle correctness

For oracle call \((i,j)\), let \(\mathcal U_{i,j}\) be the ideal complete
labeled-state channel, including a fixed `ok` flag and clean work registers,
and let \(\widetilde{\mathcal U}_{i,j}\) be the implemented channel including
all success/failure flag branches. R1 requires the composable metric

\[
\eta_{i,j}:=\tfrac12
 \left\|\widetilde{\mathcal U}_{i,j}-\mathcal U_{i,j}\right\|_\diamond .
\tag{R1-ORACLE-ERR}
\]

A scalar average failure probability for an action circuit does not instantiate
\(\eta_{i,j}\). Measuring a flag and conditioning or retrying is rejected
unless a source proves that the complete map is distribution-preserving,
input-independent on the uniform representative domain, injectivity-safe, and
fully uncomputed. Under the diamond-norm contract, the adaptive/repeated-call
hybrid bound is

\[
\epsilon_{\rm total}\le
\sum_{i\in\mathcal I_{\rm src}}\sum_{j=1}^{Q_i}\eta_{i,j}
+\sum_{i\in\mathcal I_{\rm src}}
  \left(\epsilon_{{\rm sieve},i}+\epsilon_{{\rm post},i}\right)
+\epsilon_{\rm tail}.
\tag{R1-ERR}
\]

If the implementation exposes only an input-correlated flag probability, the
corresponding \(\eta_{i,j}\) is unresolved and the row fails the oracle gate.

## 6. O4 — coherent register liveness

Local ancilla counts are replaced by a schedule-level definition:

\[
W_{\rm logical}:=
\max_{i,t}\sum_{r\in\mathsf{Live}_i(t)}w(r).
\tag{R1-WIDTH}
\]

The canonical sequential schedule must instantiate this table:

| Stage | Registers that must be included in \(\mathsf{Live}_i(t)\) |
| --- | --- |
| Leaf / \(U_{\rm HS}\) | public instance and branch controls; every phase state retained on the recursion frontier; oracle input/output and label; action, canonicalization, failure, and uncomputation scratch |
| Binary collimation | public instance; retained frontier states; both child phase states; output phase state while children remain live; index, measurement, permutation, QROM-lookup, and uncomputation scratch |
| Final postprocessing | public instance; final phase vector(s); puncturing/regularization state; QFT/output register; verification and uncomputation scratch |
| Retry boundary | all registers from an unfinished invocation plus the next invocation if overlap is allowed; otherwise a proof that prior coherent state is measured or cleanly uncomputed before reuse |

Define

\[
M_{\rm QRACM}:=\max_{i,v}R_{i,v}
\tag{R1-QRACM-PEAK}
\]

only for the non-overlapping sequential schedule. QRACM cells, coherent
logical qubits, QROM T-count/ancillae, and classical backing storage remain
different types.

## 7. O5 — Equation (4.1) phase-vector length

R1 separates:

- \(\widetilde L^{\rm QRACM}_{\max,i,v}=8L_{i,v}\), the source's enforced hard
  number of indexable cells for Equation (3.5); and
- \(\widetilde L^{(4.1)}_{{\rm ub},i}\), an upper bound on the typical
  phase-vector length used only by Equation (4.1).

For the conservative R1 row,

\[
\widetilde L^{(4.1)}_{{\rm ub},i}
 := \max_v\widetilde L^{\rm QRACM}_{\max,i,v},
\qquad
T_{{\rm sieve},i}^{\rm ub}
 :=36\widetilde L^{(4.1)}_{{\rm ub},i}
 \left(\frac{2}{1-\delta_i}\right)^{d_i}.
\tag{R1-4.1}
\]

This deliberately uses the enforced hard cap as a conservative upper bound; it
does not identify a typical length with a QRACM cell type. For a same-row
interval \([\ell_i,u_i]\) later justified from the source or simulator, R1 must
report the corresponding interval

\[
36\ell_i\left(\frac{2}{1-\delta_i}\right)^{d_i}
\le T_{{\rm sieve},i}\le
36u_i\left(\frac{2}{1-\delta_i}\right)^{d_i}.
\tag{R1-4.1-SENS}
\]

Replacing \(L_i\) by the enforced \(8L_i\) cap changes this term by a factor of
eight, which must remain visible rather than being absorbed into a security
label.

## 8. O1–O5 mapping summary

| Objection | R1 repair | Addressed as a convention change? | Source value complete? |
| --- | --- | --- | --- |
| O1 | Equations (R1-Q) and (R1-FULL); no automatic success multiplier; every invocation charges query, sieve, postprocessing, and classical work | Yes | No — exact invocation/stopping ledger is absent |
| O2 | Equations (R1-TAIL-Q) and (R1-TAIL-C); classical tail removed from quantum T/depth/width | Yes | No — classical unit cost and stopping certificate remain unpinned |
| O3 | Diamond-norm complete-channel contract and adaptive composition in (R1-ORACLE-ERR)/(R1-ERR) | Yes | No — cited action source does not instantiate the uniform complete channel |
| O4 | Schedule-level live-register maximum (R1-WIDTH) and mandatory liveness table | Yes | No — source-level circuit widths are not supplied |
| O5 | Distinct hard-cell and Equation (4.1) length types, with conservative cap and interval sensitivity | Yes | Yes for the conservative symbolic upper-bound rule |

All five objections are mapped to concrete equation or typing changes. That
does not make all required source fields numerically or operationally complete.

## 9. Scope controls

- No curve, isogeny, quantum-circuit, or simulator computation was performed.
- The BLMP bounded-distribution action count is not substituted for the
  uniform complete \(U_{\rm HS}\).
- Bonnetain–Schrottenloher is used only as an independent convention
  cross-check, not as a source of constants mixed into the Peikert row.
- `IDEA-20260725-001`, `IDEA-20260725-002`, and `IDEA-20260725-003` remain
  closed and are not analyzed or reopened here.
- R1 supports no parameter recommendation, scalar security claim,
  breakthrough claim, or GOAL-completion claim.
