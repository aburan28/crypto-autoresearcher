# TASK-20260802-201 feasibility rerank

## Verdict

**OBSTRUCTED_IN_SCOPE**

Within the frozen H-IT-001/BATCH-030 boundary, no admissible certificate-bearing transfer from a non-special prime-field ECDLP instance to the named anomalous, low-embedding-degree, or subfield/Weil-descent targets can beat matched Pollard rho. The obstruction is structural, not the count of censored BATCH-030 cells:

> **Frozen-invariant target obstruction.** An ordinary \(\mathbf F_p\)-rational isogeny of degree coprime to \(N\) transports the order-\(N\) subgroup isomorphically but cannot change the Frobenius trace, the embedding degree \(\operatorname{ord}_N(p)\), or the prime base field. Each registered “special” property is therefore either already present at the source or unreachable by the admissible path.

If the property is already present, the corresponding direct special-family attack avoids all isogeny construction, traversal, certificate, and pullback costs and weakly dominates the transfer. If it is absent, the path-hit probability is zero by the invariant argument, making expected transfer cost unbounded. This conclusion is restricted to the frozen candidate class; it is not a universal ECDLP or isogeny-lane closure.

## Frozen boundary used

The analysis preserves these supplied fields without amendment:

- Source: \(E/\mathbf F_p\), with a prime-order subgroup \(G=\langle P\rangle\) of order \(N\).
- Candidate targets: anomalous \(N=p\), low-embedding-degree MOV/Frey–Rück, and subfield/Weil-descent-friendly families.
- Admissible map: an actually evaluated ordinary-isogeny path whose total degree is coprime to \(N\), followed by a special-family solve, pullback/scaling, and final verification \([k]P=Q\) on the original instance.
- Matched baseline:
  \[
  C_\rho=0.886\sqrt{N_\star}.
  \]
- Total expected transfer cost:
  \[
  C_{\rm xfer}
   =C_{\rm set}
    +\frac{C_{\rm attempt}}{p_{\rm success}}
    +C_{\rm field\ DLP}
    +C_{\rm cert}
    +C_{\rm pullback}
    +C_{\rm verify},
  \]
  with preprocessing, memory, data/oracle queries, parallelism, retries, and material hidden terms charged.
- A transfer beats rho only if, at matched success and resources,
  \[
  C_{\rm xfer}<0.886\sqrt{N_\star}.
  \]

An isogeny or codomain requiring a changed base field or an uncharged extension-field boundary would amend the frozen problem and is not silently admitted here.

## Evidence labels

- **Derivation:** consequences of isogeny/Frobenius and embedding-degree invariance, cost inequalities, and dominance relations.
- **Observation:** persisted BATCH-030 measurements and review findings.
- **Heuristic:** HEUR-ISO-1 and any unmeasured path-density claim.
- **Conjecture:** the successor mechanism proposed separately.

No experimental result is produced by this task.

## Candidate-family audit

### 1. Anomalous target

#### Transfer and certificate semantics

A valid certificate would contain:

1. Every isogeny edge, kernel description, degree, and composition order.
2. Verification that the total degree is coprime to \(N\).
3. Evaluated images \(P'=\phi(P)\) and \(Q'=\phi(Q)\).
4. A target-curve certificate showing \(\#E'(\mathbf F_p)=p\), equivalently trace \(t'=1\).
5. The anomalous-curve solver transcript and recovered scalar.
6. The pullback/scaling relation induced by \(\phi\).
7. Final verification \([k]P=Q\) on the original non-special instance.

This proves that the stated path and subgroup map were evaluated, that the target is anomalous, and that the returned scalar solves the original instance. A direct BSGS transcript plus \([k]P=Q\) proves only the scalar and is not a transfer certificate.

#### Derivation

For an \(\mathbf F_p\)-rational isogeny \(E\to E'\), the curves have the same Frobenius characteristic polynomial and hence the same trace and point count:
\[
\#E(\mathbf F_p)=\#E'(\mathbf F_p)=p+1-t.
\]

Therefore a path reaches a trace-one anomalous curve only if the source already has trace one. Moreover, for cryptographic-size \(p\), if a subgroup of order \(N=p\) lies in \(E(\mathbf F_p)\), Hasse’s bound excludes a larger positive multiple of \(p\), so the source is already anomalous.

Thus:

- Non-anomalous source: \(p_{\rm success}=0\) by derivation, so \(C_{\rm attempt}/p_{\rm success}=+\infty\).
- Anomalous source: the direct anomalous attack is already available. Adding a path gives
  \[
  C_{\rm xfer}=C_{\rm direct\ anomalous}+C_{\rm path}+C_{\rm cert}+C_{\rm pullback},
  \]
  with every added term nonnegative.

#### Feasible inequality

The required inequality
\[
C_{\rm direct\ anomalous}+C_{\rm overhead}<C_\rho
\]
can hold on an anomalous source, but it is not evidence for isogeny transfer: removing the nonnegative transfer overhead yields an equal-or-better direct attack. Such a source is not a genuine non-special transfer instance.

#### Pareto result

- Non-special source: dominated by rho because expected transfer work is unbounded.
- Already anomalous source: transfer dominated by the direct anomalous solver on time, memory, and data/query axes.
- `dominated_by`: `matched_pollard_rho` for the admissible non-special row; `direct_anomalous_solver` for the special-source control row.

### 2. Low-embedding-degree MOV/Frey–Rück target

#### Transfer and certificate semantics

A valid certificate would contain:

1. The complete evaluated isogeny path and its coprime-to-\(N\) degree proof.
2. \(P'=\phi(P)\) and \(Q'=\phi(Q)\).
3. The claimed embedding degree \(k\), with checks that \(N\mid p^k-1\) and that no proper divisor of \(k\) has the same property.
4. A valid auxiliary order-\(N\) pairing point and the two pairing outputs.
5. The complete field-DLP generation cost and a check such as \(g^x=h\).
6. Pullback/scaling data.
7. Final verification \([x]P=Q\).

The exponent check can make the field-DLP result independently verifiable, but it does not remove the field-DLP generation cost.

#### Derivation

The embedding degree is
\[
k=\operatorname{ord}_N(p).
\]
It depends only on \(p\) and \(N\), not on the curve representative inside an \(\mathbf F_p\)-isogeny class. An isogeny cannot turn a high-embedding-degree source subgroup into a low-embedding-degree target subgroup while preserving the frozen \(p,N\) boundary.

Thus:

- High-\(k\) source: a low-\(k\) target is unreachable and \(p_{\rm success}=0\).
- Low-\(k\) source: MOV/Frey–Rück is already applicable directly, so transfer adds nonnegative path and certificate overhead.

The complete inequality is
\[
C_{\rm set}
+\frac{C_{\rm path-attempt}}{p_{\rm success}}
+C_{\rm pairing}
+C_{\mathbf F_{p^k}^{\times}\text{-DLP}}
+C_{\rm cert}
+C_{\rm pullback}
+C_{\rm verify}
<0.886\sqrt{N_\star}.
\]

For a non-special source, the left side is infinite because \(p_{\rm success}=0\). For an already-low-\(k\) source, any advantage comes from the field-DLP algorithm already available on the source, not from isogeny transfer.

#### Frozen planted-cell accounting

The executed substitution
\[
C_{\rm special}= \lceil k\log_2p\rceil=22
\]
gave \(R_{\rm xfer}=0.1107\), but it omitted the dominant field DLP and is void.

Using the frozen v3 charge:
\[
C_{\rm path}=9,\quad
C_{\rm pullback}=40,\quad
C_{\rm special}=1284,
\]
so
\[
R_{\rm xfer}=\frac{9+40+1284}{641.609}\approx2.08.
\]
This is approximately
\[
\log_2(2.08)\approx1.06
\]
bits more time than matched rho.

The capsule separately supplies a field-DLP-inclusive \(k=1\) toy charge of about \(2\sqrt{N_\star}=1448\). If that charge replaces the v3 special cost, then
\[
R_{\rm xfer}\approx\frac{9+40+1448}{641.609}\approx2.33,
\]
or about
\[
\log_2(2.33)\approx1.22
\]
bits more time than rho. The capsule does not reconcile the two frozen field-DLP approximations, so this analysis does not silently choose between them. Both are adverse.

The asymptotic power exponent remains \(1/2\) under either supplied generic field-DLP charge, so
\[
\Delta\alpha=\alpha_\rho-\alpha_{\rm xfer}=0.
\]
The candidate loses on its constant factor.

If BSGS realizes the approximately \(1448\)-operation charge, its table is on the order of \(\sqrt{N_\star}\approx724\) entries. Against an \(O(1)\)-state rho implementation, this is at least about
\[
\log_2(724)\approx9.50
\]
bits more stored group-element units under the one-state normalization. Exact byte ratios are unresolved because representation sizes were not supplied. A constant-memory field-rho implementation removes that table but retains the adverse time charge.

#### Pareto result

- Frozen planted row: dominated by matched rho in time and by constant-memory rho in memory; it also carries path/certificate data absent from rho.
- Already-low-\(k\) special source: transfer dominated by direct MOV/Frey–Rück using the same field-DLP algorithm.
- `dominated_by`: `matched_pollard_rho` for the frozen planted accounting; `direct_mov_frey_ruck` for any special-source transfer control.

### 3. Subfield/Weil-descent-friendly target

#### Transfer and certificate semantics

A valid certificate would need:

1. The full evaluated isogeny path and subgroup images.
2. A certified field tower or subfield embedding.
3. The descent equations, factor base or relation system, and all data/query costs.
4. The special-family solve transcript.
5. Pullback/scaling data.
6. Final verification on the original prime-field instance.

#### Derivation

The frozen source field is the prime field \(\mathbf F_p\), which has no proper subfield. An \(\mathbf F_p\)-isogeny changes neither the base field nor its subfield lattice. It also preserves the Frobenius action relevant to the transported subgroup.

Therefore an ordinary isogeny cannot create a proper-subfield representation for a genuinely prime-field source. Passing to \(\mathbf F_{p^m}\), changing representations, or charging a Weil restriction would introduce a new extension degree, new ambient group sizes, and new field-DLP/descent costs outside the frozen boundary.

Within scope:

- Non-descent-friendly prime-field source: \(p_{\rm success}=0\).
- Any already-available descent representation: the same descent can be attempted without the isogeny, so direct descent weakly dominates transfer.

#### Pareto result

- Non-special source: dominated by rho because expected transfer work is unbounded.
- Already descent-friendly source: dominated by direct descent with the transfer overhead removed.
- `dominated_by`: `matched_pollard_rho` or `direct_descent`, depending on source classification.

## Common end-to-end cost and success argument

Let \(S\) be the named special set and let \(I(E)\) denote the tuple
\[
I(E)=\bigl(t(E),\operatorname{ord}_N(p),\text{base field}\bigr).
\]
Every admissible frozen path preserves \(I(E)\). Membership in each registered target family is determined by a component of this tuple:

- anomalous: \(t=1\);
- MOV/Frey–Rück: small \(\operatorname{ord}_N(p)\);
- subfield descent: a nontrivial subfield structure, absent for \(\mathbf F_p\).

For a non-special source, the reachable isogeny component has empty intersection with the corresponding registered special set. Hence
\[
p_{\rm success}
=\Pr[\text{an admissible path reaches }S]
=0
\]
by derivation, independently of the observed BATCH-030 hit count.

Consequently,
\[
C_{\rm xfer}
=C_{\rm set}+\frac{C_{\rm attempt}}{0}+\cdots
=+\infty.
\]

For a source already satisfying the property, write \(C_{\rm special}\) for the complete direct special-family solver cost. Then
\[
C_{\rm xfer}
=C_{\rm special}+H,
\qquad H\ge0,
\]
where \(H\) contains path construction, evaluation, certificate generation, pullback, extra verification, retries, and any special-set search. Therefore the transfer is weakly dominated by the direct special solver on every resource axis for which it uses the same solver.

Parallelism does not reverse either result. Equal parallel resources can be applied to rho or the direct special solver, while the transfer retains its invariant impossibility or nonnegative overhead. No transfer-specific preprocessing is allowed to be free; amortization would require the same number of target instances and equivalent preprocessing assumptions for rho.

## Audit of `rho_special=0`

The observed values are not used as an impossibility premise.

- The 20- and 24-bit zeros apply only to primes 2097169 and 33554467.
- The 28-bit zero is from a 50,000-class sample and has a one-sided 95% upper bound of approximately \(6\times10^{-5}\).
- There were zero uncensored unplanted transfers, so no KS or tail comparison was available.
- `F_hit=0` and measured `p_success=0` make the BATCH-030 run’s empirical expected-cost estimate unbounded.
- They do not prove that an unregistered special subset has mathematical density zero.
- HEUR-ISO-1 remains unmeasured, not falsified.

The obstruction verdict instead follows from invariance of the three frozen target properties. It does not extend to a newly specified special property that varies within an isogeny class.

## Certificate and control deficiencies in BATCH-030

The planted record cannot satisfy the admissible class because:

- the certificate was direct BSGS rather than an evaluated isogeny pullback;
- the walk returned to the special start;
- the recovered edge joined two special curves;
- the dominant field DLP was omitted in the executed cost;
- the identical-shape null did not run;
- the null edge ledger was empty;
- recomputation was not independent;
- special-set construction, expected retries, memory, data/query costs, and tradeoffs were absent.

These findings invalidate the observed transfer interpretation. They are not the mathematical obstruction and are not counted as rejected mechanisms.

## Pareto and `sota_delta` summary

Convention:
\[
\Delta\alpha=\alpha_\rho-\alpha_{\rm candidate};
\]
positive values favor the candidate.

- Matched rho: \(\alpha=1/2\), normalized time ratio \(1\), \(O(1)\) memory, and no transfer-specific data/query requirement.
- Admissible non-special transfer rows: expected time \(+\infty\); no finite candidate exponent or finite log-time ratio exists.
- Frozen planted MOV row: \(\alpha=1/2\), \(\Delta\alpha=0\), and \(\log_2\) time ratio approximately \(+1.06\) under v3 or \(+1.22\) under the separately supplied \(2\sqrt{N_\star}\) field-DLP charge.
- A special-source direct attack may have a lower exponent, but the corresponding transfer has the same special solver plus nonnegative overhead. It is therefore dominated by the direct attack and does not establish transfer advantage.
- Exact log-memory and log-data ratios are unavailable where byte sizes or zero-query denominators were not supplied. They are reported as unresolved rather than invented.

The matched-rho row has `dominated_by: null` only after checking every in-scope candidate across time, memory, and data/query axes. No admissible candidate has lower time with no worse memory and data/query use.

## Narrow conclusion and redirection

The frozen lane is obstructed because its three target properties do not vary along the admissible prime-field isogeny paths. A repair that merely supplies a better certificate, a live null, or a more complete field-DLP implementation would improve experimental validity but would not create a non-special-to-special path.

This is not a claim that:

- every isogeny-assisted ECDLP mechanism is impossible;
- every special subset of an isogeny class is invariant;
- HEUR-ISO-1 is false;
- rho is universally optimal;
- H-IT-001 should receive any official status transition.

The useful redirection is to replace “hit an invariant special solver family” with an exponent-first mechanism in which the isogeny structure itself enlarges a certified equivalence class of DLP representations and reduces collision search space. That proposal is supplied in `successor-proposal.yaml`.
