# Mechanism screen — GOAL-SSI-001 BATCH-007

Task `TASK-20260729-001` · access date 2026-07-29  
Resolved model: `GPT-5.6 Sol` (`research-sol-max` unavailable; fallback authorized by `inference-amendment-TASK-20260729-001.yaml`)  
Disposition: **ADMIT_CANDIDATE_FOR_REVIEW** → provisional `IDEA-20260729-001`

## 1. Target survivor and open problem

- **Survivor assumption:** CSIDH vectorization in the free, transitive class-group
  action, with no SIDH-style torsion images (`KN-TECH-027`, `KN-LIT-069`).
- **Open problem:** `KN-OPEN-014` asks for concrete Kuperberg/collimation-sieve
  cost and parameter sizing while charging query count, memory, and the coherent
  class-group-action circuit.
- **Candidate type:** an accounting/control mechanism, not a new hidden-shift
  algorithm and not a cryptanalytic break. It makes a later numerical comparison
  admissible only if one source-consistent resource vector can be filled.
- **Closed / forbidden reopen:** classical path-finding re-baselining
  (`IDEA-20260725-001`), orientation residuals (`IDEA-20260725-002`), and
  SQI-FS-T0 (`IDEA-20260725-003`). No SIDH torsion mechanism is imported.

## 2. Frozen cost convention

**Convention name:** `CSIDH-COLLIMATION-FC0`.

The convention fixes the following before any numerical security statement.

### 2.1 Instance and algorithm identity

The instance tuple is

\[
I=(p,\mathcal O,G=\mathrm{Cl}(\mathcal O),N=|G|,
G\text{-decomposition},E_0,E_1=[s]E_0,\mathcal B,\Lambda,\mathrm{enc}),
\]

where \(\mathcal B\) is the named ideal-generator basis, \(\Lambda\) its relation
lattice, and `enc` fixes the canonical curve/group encodings. A numerical row
must cite the exact parameter and class-group data revision.

The attack is the **binary** (\(r=2\)) collimation sieve in the final
2020-02-23 version of Peikert, IACR ePrint 2019/725, with:

- \(\alpha=1/2\);
- \(S=L\);
- punctured regularization;
- \(\widetilde L_{\max}=8L\);
- the nine-lookup, minimum-QRACM implementation of Equation (3.5);
- the reported recovery target of all but \(b_{\rm tail}=56\) secret bits,
  followed by a separately charged classical tail;
- sequential oracle scheduling \(P_{\rm oracle}=1\) for the canonical row.
  Any parallel row is a different schedule and must report its width and depth.

The paper's CSIDH-512 point
\(\log_2 N=257.1,\log_2 L=31.3,d=8,\log_2 Q_{\rm model}=15.7\),
and \(\log_2 M_{\rm QRACM}=40\) is a **reported query/memory anchor**, not an
adopted full-attack or security estimate. Its circuit column depends on an
oracle assumption that this gate tests rather than grants.

### 2.2 Query unit

One query is one invocation of a complete labeled-state oracle
\(U_{\rm HS}\): uniform superposition over the pinned group domain, coherent
selection of the \(E_0/E_1\) branch, coherent class-group action, output
canonicalization, label production, all required inverse calls/uncomputation,
and explicit failure handling. A call to a cheaper distribution-specific
action circuit is not silently one \(U_{\rm HS}\) query.

Define:

- \(Q_{\rm model}(I,L,d)\): Peikert's total modeled calls needed to recover all
  but \(b_{\rm tail}\) bits under the frozen sieve settings;
- \(\rho_{\rm run}\): cited single-run useful-output probability;
- \(\epsilon_{\rm target}\): declared total attack failure target;
- \(R_{\rm succ}=\lceil\log(\epsilon_{\rm target})/
  \log(1-\rho_{\rm run})\rceil\), when independent repetition is the cited
  amplification rule;
- \(Q_{\rm HS}=R_{\rm succ}Q_{\rm model}\).

No logarithmic query figure is a security claim until \(\rho_{\rm run}\), all
discard/retry multipliers, and the meaning of \(Q_{\rm model}\) are reconciled
with the cited simulator/table.

### 2.3 Quantum memory

QRACM and coherent logical qubits are different resources and remain separate.
For every sieve node \(v\), the nine-lookup variant fixes

\[
R_v=\widetilde L_{\max,v}\cdot
\left\lceil\max\left\{
\tfrac32\log_2(S_{0,v}/S_v),
\log_2\widetilde L_{\max,v}\right\}\right\rceil
\quad\text{QRACM bits},
\]

and \(M_{\rm QRACM}=\max_v R_v\), because the memory is reusable.

The separate coherent width is

\[
W_{\rm logical}=\max\{W_{U_{\rm HS}},W_{\rm coll},W_{\rm post},W_{\rm tail}\}
\]

under \(P_{\rm oracle}=1\), with every ancilla and live input/output register
counted. The QROM construction contributes \(\lceil\log_2
\widetilde L_{\max,v}\rceil\) ancillae per lookup implementation, but this does
not discharge the still-to-be-derived \(W_{U_{\rm HS}}\). QRACM bits may not be
reported as ordinary qubits or omitted as "classical memory."

### 2.4 Circuit and full-cost equations

The circuit metric is logical Clifford+T with **T-count, T-depth, and logical
width reported separately**. Clifford gates are not assigned zero physical
cost; they are recorded separately and may be scalarized only by a named
fault-tolerant architecture. For the source-level logical convention:

\[
T_{\rm full}=T_{\rm qpre}/K+
Q_{\rm HS}T_{U_{\rm HS}}+
T_{\rm sieve}+T_{\rm post}+T_{\rm tail},
\]

where \(K=1\) is the default number of attacked public keys sharing
precomputation. Any \(K>1\) is an explicitly amortized row.
\(T_{\rm qpre}\) counts quantum preprocessing only; classical preprocessing is
reported separately in \(C_{\rm classical}\) and \(M_{\rm classical}\).

\[
T_{U_{\rm HS}}=
a_{\rm act}T_{\rm act}^{\rm uniform}
+T_{\rm group\ prep}+T_{\rm branch}+T_{\rm canon}
+T_{\rm label/QFT}+T_{\rm fail}+T_{\rm uncompute}.
\]

Here \(a_{\rm act}\), every \(T_*\), the action-input distribution, and the
failure probability are named constant parameters until derived from a cited
reversible circuit. In particular, the BLMP ePrint 2018/1059 count for bounded
secret-key-distribution exponent vectors is not substituted for
\(T_{\rm act}^{\rm uniform}\) without a charged coherent map from the uniform
group superposition.

For the fixed nine-lookup QROM convention, Peikert's Equation (4.1) pins the
non-oracle sieve term to

\[
T_{\rm sieve}=36\widetilde L\left(\frac{2}{1-\delta}\right)^d,
\]

using nine lookups and \(4\widetilde L\) T gates per lookup. The row must pin
\(\delta\) and the applicable \(\widetilde L\); `FC0` uses the paper's
\(\delta=0.02\) comparison point unless a distinct row is declared.

The full resource result is the vector

\[
(Q_{\rm HS},M_{\rm QRACM},W_{\rm logical},T_{\rm full},T{\rm-depth},
C_{\rm classical},M_{\rm classical},\epsilon_{\rm total}),
\]

not a single "bits of security" number. Classical relation-lattice/group
precomputation, sieve work, storage, and the \(2^{56}\)-scale tail are charged.
The error budget must satisfy a cited composition rule, at minimum the union
bound
\(\epsilon_{\rm total}\le Q_{\rm HS}\epsilon_{U_{\rm HS}}+
\epsilon_{\rm sieve}+\epsilon_{\rm post}+\epsilon_{\rm tail}\).

## 3. Typed candidate mechanism

The mechanism is **resource-vector composition with a hard oracle boundary**:

1. Freeze the instance and c-sieve row before selecting a favorable query/memory
   point.
2. Count complete \(U_{\rm HS}\) invocations, not bare action calls.
3. Keep QRACM bits, coherent width, T-count, T-depth, and classical resources
   typed rather than converting them silently.
4. Permit a numerical security comparison only after the uniform-superposition
   action, success amplification, preprocessing, and tail are all instantiated
   in the equations above.

This discriminates two explanations for the spread in concrete CSIDH estimates:

- **Accounting-reconciliation explanation:** the source components can be
  connected under one fixed oracle and error convention; a later numerical
  comparison is meaningful.
- **Oracle-boundary explanation:** the cheap query count is real as a black-box
  count, but the uniform coherent oracle is not costed by the
  distribution-specific circuit estimate; a full security number remains
  inadmissible.

## 4. Predictions

1. **Untyped-field count:** a source-reconciliation worksheet can reduce
   `untyped_required_fields` to zero only if it supplies
   \(\rho_{\rm run},a_{\rm act},T_{\rm act}^{\rm uniform},W_{U_{\rm HS}}\),
   preprocessing, tail, and error composition. Missing any one blocks a numeric
   claim.
2. **Oracle dominance, conditional:** if a cited coherent uniform-action circuit
   instantiates \(T_{U_{\rm HS}}\) near the source's optimistic action estimate,
   then \(Q_{\rm HS}T_{U_{\rm HS}}>T_{\rm sieve}\) for the frozen CSIDH-512 row.
   Failure of this inequality means QRACM/sieve work was not negligible under
   the pinned convention.
3. **Distribution mismatch:** directly substituting the BLMP
   bounded-secret-distribution action count for
   \(T_{\rm act}^{\rm uniform}\) leaves at least one uncharged map or assumption.
   A cited reversible map with cost and width falsifies this prediction.

## 5. Full-cost / oracle boundary

**Charged:** all complete labeled-state queries; coherent uniform-group
preparation; conversion to short exponent vectors; action, inverse work, and
uncomputation; QROM lookups; logical width; T-count and T-depth; classical
preprocessing and memory; sieve/postprocessing; tail search; retries; and
failure probability.

**Not collapsed into the logical row:** physical error correction, routing,
factory area, wall-clock time, and energy. These are not free; they require a
separate named architecture and cannot be inferred from T-count alone.

**Forbidden:** free QRACM; free relation-lattice/class-group data; replacing a
uniform-superposition action by a key-distribution action without a charged
map; multiplying approximate query and oracle figures from incompatible paper
revisions; or calling a T-count alone "NIST security."

## 6. Novelty screen

- Repository corpus search found only the asymptotic/reporting spine
  (`KN-OPEN-014`, `KN-TECH-027`, `KN-LIT-069`, `KN-LIT-071`) and no CSIDH
  hypothesis record. It does not already freeze a query unit, QRACM formula,
  coherent width, circuit boundary, or error composition.
- Primary-source web checking found that the components are known:
  Peikert 2019/725 gives the binary c-sieve query/QRACM trade-off, nine-lookup
  Equation (3.5), and non-oracle T-count Equation (4.1);
  Bonnetain–Schrottenloher 2018/537 gives alternative hidden-shift/circuit
  trade-offs and explicitly separates oracle memory; BLMP 2018/1059 analyzes
  the action circuit and warns that its favorable input distribution is not the
  complete uniform hidden-shift oracle.
- Therefore `novelty_status: adaptation`. `CSIDH-COLLIMATION-FC0` is a new
  program control object, not a new quantum algorithm, constant, or literature
  result.
- It does not reopen `IDEA-20260725-001`: no classical path-finding baseline or
  `KN-TECH-050` comparison is changed. It is the distinct KN-OPEN-014 quantum
  convention explicitly nominated by `DEC-20260725-007`.

## 7. Cheapest falsification / derivation gate

Perform one zero-curve-compute, two-source-plus-oracle derivation worksheet:

1. Transcribe the frozen CSIDH-512 c-sieve row and Equations (3.5), (4.1) from
   final Peikert 2019/725, including success/retry semantics.
2. Expand one \(U_{\rm HS}\) into the terms in Section 2.4 and map each term to
   final BLMP 2018/1059 or mark it unresolved; use final
   Bonnetain–Schrottenloher 2018/537 as an independent convention cross-check,
   not as a source of mix-and-match constants.
3. Fill the complete resource vector, provenance, and error budget without a
   numerical security label.
4. Emit exactly one of:
   - `FC0_PIN_COMPLETE_FOR_LATER_NUMERIC_REVIEW`;
   - `FC0_UNIFORM_ORACLE_BOUNDARY_UNRESOLVED`;
   - `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`.

**Falsifies this candidate's admission to a later numerical gate** if any
required field can be filled only by silently changing the algorithm revision,
action-input distribution, query unit, memory type, success target, or
amortization count. The residual open question is then the concrete reversible
cost and width of the complete uniform-superposition \(U_{\rm HS}\), not a
new CSIDH security number.

## 8. Interpretation limits

- Admission is a cost-convention/derivation candidate only; it is not an
  experiment run, CSIDH break, parameter recommendation, or GOAL completion.
- The reported CSIDH-512 query/memory anchor is literature context, not newly
  verified evidence. No curve or isogeny computation was performed.
- No numeric security claim is made because
  \(T_{\rm act}^{\rm uniform}\), \(W_{U_{\rm HS}}\), success amplification, and
  the complete error budget have not yet passed the gate.
- Same-lineage fallback weakens independence. Independent review must challenge
  the query unit, the QRACM multiplication/formula, the distribution boundary,
  and whether every classical/quantum resource is charged.

## 9. Sources checked

- Repository: `KN-OPEN-014`, `KN-TECH-027`, `KN-TECH-050`,
  `KN-LIT-069`, `KN-LIT-071`, `KN-LIT-079`,
  `DEC-20260725-007`, `EV-SSI-006`, and closed
  `IDEA-20260725-001/002/003`.
- Chris Peikert, *He Gives C-Sieves on the CSIDH*, final ePrint 2019/725
  (2020-02-23), <https://eprint.iacr.org/2019/725>.
- Xavier Bonnetain and André Schrottenloher, *Quantum Security Analysis of
  CSIDH*, final ePrint 2018/537 (2020-03-06),
  <https://eprint.iacr.org/2018/537>.
- Daniel J. Bernstein, Tanja Lange, Chloe Martindale, and Lorenz Panny,
  *Quantum circuits for the CSIDH: optimizing quantum evaluation of isogenies*,
  revised ePrint 2018/1059 (2019-03-05),
  <https://eprint.iacr.org/2018/1059>.
