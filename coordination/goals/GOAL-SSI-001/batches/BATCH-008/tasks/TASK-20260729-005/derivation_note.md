# FC0-R1 source-reconciliation derivation — GOAL-SSI-001 BATCH-008

Task `TASK-20260729-005` · worksheet `FC0-R1-WORKSHEET-001`  
Worksheet count: **one** · curve/isogeny/circuit computation: **zero**  
Convention: **CSIDH-COLLIMATION-FC0-R1**

## 1. Question and decision rule

The worksheet asks whether one source-compatible resource vector can be
instantiated for the final Peikert binary c-sieve row under the repaired R1
equations.

The decision order is typed:

1. First require a source-reconciled attack query/recovery schedule and memory
   row, including every top-level sieve invocation and retry.
2. Only after that passes, ask whether the complete uniform-superposition
   \(U_{\rm HS}\) channel has a charged circuit, width, and composable error.
3. A later numerical review is eligible only if both stages and all remaining
   typed fields pass.

This order prevents an unresolved aggregate query schedule from being hidden
by the separately unresolved oracle circuit.

## 2. Sources used without mixing revisions

### Peikert c-sieve source

Chris Peikert, *He Gives C-Sieves on the CSIDH*, IACR ePrint 2019/725,
paper dated 2020-02-23:

- Equation (3.3) models oracle queries for one recursion-tree sieve run.
- Section 3.4 permits discard/retry during regularization and describes
  extracting expected secret information from punctured phase vectors.
- Equation (3.5) gives the reusable QRACM requirement for binary collimation.
- Figure 1 defines \(\widetilde Q_{\rm total}\) as total oracle queries to
  recover all but the 56-bit classical residual, and uses
  \(\widetilde L_{\max}=8L\) for QRACM.
- Equation (4.1) is the non-oracle T-count of one full binary sieve traversal
  and takes an upper bound on typical phase-vector length.

### BLMP oracle source

Daniel J. Bernstein, Tanja Lange, Chloe Martindale, and Lorenz Panny,
*Quantum circuits for the CSIDH: optimizing quantum evaluation of isogenies*,
IACR ePrint 2018/1059, revision 2019-03-05:

- Section 2.1 states that hidden-shift algorithms require a uniform
  superposition over class-group elements.
- The natural exponent-vector map is surjective but far from injective.
- A uniform set of unique short representatives requires a deterministic
  reduction map plus class-group/relation-lattice preprocessing.
- The paper's reported favorable action cost uses the constructive
  distribution as a best-conceivable illustration, not a completed cost for
  that uniform unique-representative channel.
- Its action failure analysis is distribution-dependent and does not by itself
  supply the diamond-norm complete-channel guarantee required by R1.

### Independent convention cross-check

Xavier Bonnetain and André Schrottenloher, *Quantum Security Analysis of
CSIDH*, IACR ePrint 2018/537, revision 2020-03-06, is used only to check
resource typing. It treats the hidden-shift routine and action oracle as
separate components and uses a different hidden-shift memory posture.
Accordingly, none of its constants are imported into the Peikert binary
QRACM row.

`KN-TECH-051` locates R1 on the Peikert unconstrained-collimation side of the
resource-memory dispute. `KN-LIT-127`–`KN-LIT-129` establish the dispute's
scope but do not authorize a resource-constrained/SQALE substitution.

## 3. Single derivation worksheet

| Required field | Source equation or statement | R1 transcription | Result |
| --- | --- | --- | --- |
| Algorithm/revision | Peikert binary c-sieve, punctured regularization | One fixed final-paper row; no cross-revision constants | PASS |
| Per-run query model | Peikert Eq. (3.3) | \(Q_i\) for one source-scheduled invocation | PASS symbolically |
| Attack aggregate queries | Figure 1: \(\widetilde Q_{\rm total}\) already totals queries through recovery to the classical residual | \(Q_{\rm attack}=\sum_iQ_i=\widetilde Q_{\rm total}\); no generic \(R_{\rm success}\) multiplier | PASS as aggregate |
| Invocation and retry ledger | Section 3.4 has fresh-sieve discard/retry and expected information per run, but Figure 1 does not enumerate every top-level invocation or stopping event | Require explicit \(\mathcal I_{\rm src}\), including all fresh-sieve retries and recovery invocations | **BLOCKED** |
| Repeated non-oracle work | Eq. (4.1) counts one full sieve traversal | Charge \(T_{{\rm sieve},i}\) and \(T_{{\rm post},i}\) for every \(i\in\mathcal I_{\rm src}\) | **BLOCKED by missing \(\mathcal I_{\rm src}\)** |
| QRACM | Eq. (3.5), reusable QRACM, hard \(\widetilde L_{\max}=8L\) in Figure 1 | \(M_{\rm QRACM}=\max_{i,v}R_{i,v}\) under a non-overlap proof; QRACM is not coherent width | PASS symbolically |
| Equation (4.1) length | Upper bound on typical length; separate hard cell cap in Figure 1 | Conservative \(\widetilde L^{(4.1)}_{\rm ub}:=\widetilde L^{\rm QRACM}_{\max}\), with factor-eight sensitivity retained | PASS as an upper-bound rule |
| Classical residual search | Figure 1/Section 4.1 assign the remainder to classical brute force | Set quantum tail resources to zero; require \(C_{\rm tail},M_{\rm tail},\epsilon_{\rm tail}\), action unit, and stopping certificate | TYPED; values unresolved |
| Uniform oracle representative map | BLMP Section 2.1 distinguishes uniform unique representatives from favorable bounded exponent vectors | Require deterministic coherent map, preprocessing, cost, width, failure handling, and uncomputation | **BLOCKED** |
| Oracle error composition | BLMP reports action failure under an input distribution | Require complete-channel diamond error \(\eta_{i,j}\) and sum it over adaptive calls | **BLOCKED** |
| Coherent width | No cited source supplies the R1 whole-attack live-register schedule | Use \(\max_{i,t}\sum_{r\in\mathsf{Live}_i(t)}w(r)\), including recursion-frontier states and caller registers | TYPED; values unresolved |
| Resource-memory posture | Peikert uses classical memory readable in superposition; Bonnetain–Schrottenloher and SQALE occupy different resource positions | Unconstrained Peikert collimation, QRACM explicitly reported, no exogenous memory cap | PASS |

## 4. Controls

### Aggregate-query mutation

Apply an extra repetition multiplier to
\(\widetilde Q_{\rm total}\). R1 rejects it because the source quantity is
already attack-aggregate. Duplicate a top-level sieve invocation while leaving
\(T_{\rm sieve}\) and \(T_{\rm post}\) unchanged; Equation (R1-FULL) rejects
the row.

### Distribution mutation

Substitute the BLMP favorable bounded-exponent action directly for the uniform
complete \(U_{\rm HS}\). R1 rejects the substitution until the deterministic
coherent representative map and all of its resources are supplied.

### Memory mutation

Relabel QRACM cells as ordinary coherent qubits or omit QROM T-count and
ancillae. R1 rejects both type changes.

### Failure-bias mutation

Make the action failure flag depend on a representative-vector region while
preserving the same average scalar failure probability. The scalar remains the
same, but the complete-channel diamond error and conditioned distribution can
change, so R1 rejects the scalar union-bound substitution.

### Liveness mutation

Retain recursion-frontier phase states while invoking the next oracle. R1
includes those states in \(\mathsf{Live}_i(t)\); a callee-local maximum that
omits them fails Equation (R1-WIDTH).

All controls are source/equation checks. None was executed as a curve,
isogeny, simulator, or quantum-circuit run.

## 5. Derivation result

The query/QRACM anchor comes from one Peikert row and is type-compatible, but
the source aggregate \(\widetilde Q_{\rm total}\) does not provide the exact
\(\mathcal I_{\rm src}\) needed to charge Equation (4.1), postprocessing, and
classical work once per recovery/retry invocation. Inferring that ledger from
expected bits per run would invent a stopping distribution and retry count.

The uniform-oracle circuit and composable error are also unresolved, but they
are a second-stage boundary. Under the decision order in Section 1, the
first-stage query/recovery ledger failure determines the single disposition:

**FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED**

Forward guidance: a later worksheet would need a source- or code-derived
top-level invocation trace whose \(\sum_iQ_i\) reconciles exactly with
\(\widetilde Q_{\rm total}\), while separately summing every sieve,
postprocessing, and classical-tail event. Only after that trace exists is the
uniform-oracle boundary the decisive remaining gate.

## 6. Interpretation limits

- This is one zero-compute derivation worksheet, not an experiment.
- The result blocks only a later numeric row under
  `CSIDH-COLLIMATION-FC0-R1`; it does not establish or refute the hardness of
  CSIDH vectorization.
- No parameter recommendation, scalar security estimate, breakthrough, or
  GOAL-completion conclusion is made.
- No result transfers to SIDH/SIKE, CGL/SQIsign path finding, ECDLP, or the
  closed `IDEA-20260725-001/002/003` lanes.
