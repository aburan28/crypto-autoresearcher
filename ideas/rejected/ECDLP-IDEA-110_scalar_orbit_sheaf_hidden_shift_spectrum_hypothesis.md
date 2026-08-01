# ECDLP-IDEA-110 — Scalar-orbit sheaf hidden-shift spectrum

## Status and claim labels

- Class: representation-changing spectral channel, preserved merged rejection.
- Risk band: high.
- Top lane: `-`.
- Cohort: `20260717-f`.
- State: `merged_rejected_spectral_full_rank`.
- Approval: `unapproved`.
- Evidence scale: no run; any finite-field spectrum experiment is `toy` until a complete generic cost audit exists.
- Cost claims: `heuristic` and `model-bound`; exact character construction, spectrum output, and state preparation are not free.
- Novelty: `novelty-unverified`; no public sparse scalar-orbit sheaf spectrum is known here.
- Breakthrough claim: **none**; detecting a correlation, validating a shift identity, or recovering a toy shift does not establish a better-than-rho ECDLP algorithm.

## Falsifiable hypothesis

For \(G=\langle P\rangle\subset E(\mathbb F_p)\) of prime order \(N\) and \(Q=[x]P\), define public scalar-orbit functions

\[
F(k)=\psi(h([k]P)),\qquad G_Q(k)=\psi(h([k]P+Q)),
\]

where \(h\) is a precommitted rational/sheaf trace observable and \(\psi\) is a precommitted exact additive or multiplicative character. Since \(G_Q(k)=F(k+x)\), the hypothesis is that the associated trace sheaf has a public Fourier decomposition supported on \(N^{s}\) modes with \(s<1/2\), computable and matchable without enumerating \(k\). A second load-bearing part of the same operation is a precommitted scalar-blind spectral atomizer \(D_S\) that maps the exact sparse signature to every signed factor-base tuple, thereby supporting complete decompositions and blind target descent with full exponents below \(1/2\). It is false if the scalar-index Fourier spectrum is generically full rank/flat, if evaluating the needed modes entails \(N^{1/2-o(1)}\) orbit work, if \(D_S\) is the original source search, or if exact shift recovery requires materializing an \(N\)-entry table.

## Mechanism-new operation

The proposed new operation is a **scalar-orbit trace-sheaf hidden-shift transform**: pull a bounded-conductor sheaf observable back along \(k\mapsto[k]P\), derive its scalar-index Fourier modes symbolically, and recover a translation by matching exact phase ratios rather than searching points. The obstruction-removing claim is not “use another character”; it is a proved sparse mode theorem tied to the multiplication orbit.

For the factor-base path, the transform must also instantiate \(D_S\), an exact source atomizer defined before target queries. Sparse modes or a recovered shift without this inverse are not silently converted into decomposition tuples.

The strict duplicate/control boundary is: additive-character filters, Fourier filters over enumerated point tables, alternative observables, more samples, solver substitutions, post-hoc frequency selection, or dense resultants are duplicates/controls unless a new sheaf-theoretic operation proves and computes sub-rho sparse support on the scalar index. Relation-only spectral certificates are controls unless they complete the source, rank, factor-log, and blind descent path. In the absence of that sparse theorem, this candidate merges with the recorded full-rank spectral negatives.

## Assumptions

- \(N\) is prime, \(P\) generates \(G\), and scalar indexing is not already exposed by the input representation.
- \(h\), \(\psi\), the sheaf model, conductor bound, transform convention, support threshold, and factor-base predicate are frozen before seeing \(Q\).
- The sparse modes can be derived from public \((E,P)\) without enumerating \([k]P\), knowing \(x\), or importing fixed-curve advice.
- Character values are represented exactly or with certified precision; phase/root-of-unity recovery and extension-field costs are charged.
- The transform returns complete witnesses, not a post-hoc correlation peak, and all EC relations are verified exactly.
- Failed modes, spectral leakage, support output, ambiguity, rank deficiency, target descent, and memory are included in the comparison.
- Classical resource accounting is primary; a quantum state-preparation claim is a separate model and cannot borrow free QRAM or oracle access.

## Semantic fingerprint

`prime_order_scalar_orbit | rational_sheaf_trace_observable | symbolic_scalar_index_Fourier_transform | sparse_exact_modes | phase_ratio_hidden_shift | exact_spectral_source_atomizer | target-independent_factor_base | B_plus_sigma_rank | blind_masked_descent | full_output_and_memory_charge`

The candidate survives semantic deduplication only if both the symbolic sparse-support theorem and exact source atomizer exist. Changing \(h\), \(\psi\), sample count, or transform backend while retaining a full-rank spectrum or the original source search is not mechanism-new.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H663`, the scalar-orbit/character spectral direction closest to the proposed hidden-shift encoding.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H664`, the spectral observable variant whose pointwise correlation does not by itself lower scalar-search cost.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H665`, where multiplication by the exact scalar EC-subtraction phase is compiled into confluent-Cauchy power operators; it is a structured phase-transform control, not a sheaf/trace result, and still does not grant sparse scalar-index support.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-P1422-EXACT-CHARACTER-FILTER-CONTROL`, the exact-character positive control showing how to validate filters without promoting them.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1422-ADDITIVE-CHARACTER-NO-PROMOTION`, the no-promotion result for additive-character filtering without end-to-end scalar recovery.

## Closest primary literature

- Lange and Shparlinski bound particular exponential sums and study random walks on elliptic curves, providing a cancellation control but not a generic full-support theorem: [T. Lange and I. Shparlinski, *Certain exponential sums and random walks on elliptic curves*](https://doi.org/10.4153/CJM-2005-015-8).
- Shparlinski and Stange study character sums over elliptic curves and related scalar sequences: [I. Shparlinski and K. Stange, *Character sums with division polynomials*](https://arxiv.org/abs/0912.5246).
- Banks, Friedlander, Garaev, and Shparlinski analyze elliptic-curve exponential sums relevant to spectral cancellation: [*Double Character Sums over Elliptic Curves and Finite Fields*](https://intlpress.com/site/pub/files/_fulltext/journals/pamq/2006/0002/0001/PAMQ-2006-0002-0001-a008.pdf).

These sources motivate cancellation bounds; none proves the required public sparse scalar-index spectrum. The novelty claim therefore remains `novelty-unverified`.

## Complete factor-base-to-target-descent path

- **Freeze the public channel:** hash \((E,P,N)\), \(h\), \(\psi\), sheaf model, exact arithmetic, symbolic transform, support threshold, and a target-independent factor-base predicate. Construct \(F=\{F_1,\dots,F_B\}\) with \(B=N^\beta\).
- **Symbolic support construction:** derive the claimed support \(S\subset\widehat{\mathbb Z/N\mathbb Z}\), its exact coefficients, conductor evidence, and the full computation transcript without enumerating the scalar orbit. Charge \(|S|\), rejected modes, coefficient precision, and output.
- **Source relations:** for known random \(s\), compute \(R=[s]P\). Use the sparse phase signature to return a complete factor-base tuple \((e_i)\) with \(R=\sum_i e_iF_i\); a shift estimate or character equality alone is insufficient. Verify on the curve, then record \(s=\sum_i e_i\log_P(F_i)\pmod N\).
- **Rank and solve:** obtain at least \(B+\sigma\) independently generated verified rows, publish the exact sparse matrix and generation logs, prove/recompute rank \(B\) over \(\mathbb F_N\), solve for all factor logs, and verify \([\log_P(F_i)]P=F_i\).
- **Blind masking:** an independent process selects hidden \(t\), forms \(R_t=Q+[t]P\), and gives only \(R_t\) to the unchanged spectral descent.
- **Target descent:** compute the exact phase ratios for \(R_t\), account for all candidate shifts and collisions, return a complete verified decomposition \(R_t=\sum_i d_iF_i\), and derive \(\hat x=\sum_i d_i\log_P(F_i)-t\pmod N\).
- **Final check:** reveal \(t\), verify \([\hat x]P=Q\), and retain all wrong, ambiguous, or timed-out cases. Direct phase recovery of \(x\), if claimed, must still be costed against this complete pipeline rather than counted as a free bypass.

## Full rho/BSGS cost model

Let \(B=N^\beta\) and let the exact spectral support have size \(N^s\). Define \(N^a,N^{a_m}\) as sheaf/transform setup time and memory; \(N^f,N^{f_m}\) as factor-base construction; \(N^c,N^{c_m}\) as work and memory per materialized mode; \(N^q,N^{q_m}\) as non-mode per-query work; \(N^o\) as output per complete relation; \(N^u\) as blind-shift ambiguity work; \(N^v,N^{v_m}\) as exact EC verification; \(N^\delta,N^{\delta_t}\) as reciprocal relation and target-descent densities; and \(N^\ell,N^{\ell_m}\) as rank/linear-algebra time and memory. Symbolic support construction itself costs at least \(N^{s+c}\) unless a compressed representation and its query cost are proved.

The complete expected exponents are

\[
\lambda=\max\{a,f,s+c,\beta+\delta+s+c+q+o+v,\ell,\delta_t+s+c+q+o+u+v\},
\]

\[
\mu=\max\{a_m,f_m,s+c_m,q_m,\ell_m,\beta+o,o+u,v_m\}.
\]

If the same support can be streamed rather than rebuilt per attempt, replace repeated \(s+c\) only after charging its setup and stored-memory term; no exponent may simply disappear. Dense linear algebra has \(\ell\ge2\beta\), \(\ell_m\ge\beta\) absent proved exploitable structure. Pollard rho uses expected time exponent \(1/2\) and negligible serial memory, with parallel collision infrastructure charged. BSGS uses time exponent \(1/2\) and memory exponent \(1/2\). Classical, quantum-query, and QRAM models must be reported separately; a model-bound hidden-shift query count is not a classical wall-clock comparison.

## Likely fatal obstruction

Pulling a bounded-complexity observable back along a generic prime-order scalar orbit is expected to produce cancellation, not sparse scalar-index Fourier support. Exact character-sum bounds are consistent with essentially all modes being nonzero and comparable, while specifying or evaluating enough phases to distinguish \(N\) shifts has full-rank/output cost. Any observable that is itself an eigenfunction of every translation would effectively encode the unknown scalar character and require constructing the very level-\(N\) data sought. Thus the new operation is expected either not to exist or to hide \(N^{1/2-o(1)}\) work in orbit evaluation, mode output, or state preparation.

## Proof track

- Construct the trace sheaf on the scalar index and prove a target-independent support bound \(|S|=N^{s+o(1)}\) with \(s<1/2\), including an algorithm to enumerate/evaluate it below rho cost.
- Prove exact phase-ratio identifiability of every shift, with collision and precision bounds, without a precomputed \(N\)-entry orbit table.
- Convert the spectral oracle into complete verified factor-base relations and blind decompositions, proving densities and matrix rank rather than only correlation.
- Instantiate every term in \((\lambda,\mu)\) under a declared classical model and independently reproduce blind target recovery.

## Disproof track

- Prove a lower bound on Fourier support/rank for every bounded-conductor nonconstant public observable on a generic scalar orbit.
- Show that exact support evaluation reduces to enumerating \([k]P\), computing an \(N\)-division object, or outputting \(N^{1/2-o(1)}\) coefficients.
- Exhaustively compute toy spectra under precommitted observables and compare their support, entropy, phase collisions, and shift recovery with random functions.
- Replace the true scalar ordering by a random permutation; any surviving claimed advantage is an observable/filter artifact rather than an ECDLP channel.

## Positive and negative controls

- **Positive implementation control:** a synthetic cyclic signal with exactly \(N^s\) planted Fourier modes and a planted translation; the pipeline must recover the shift and report the planted support cost.
- **Positive exactness control:** imported `ECFG-P1422-EXACT-CHARACTER-FILTER-CONTROL`, reproduced without treating its valid filter as scalar recovery.
- **Negative control:** a random complex/finite-field signal with the same length and marginal distribution as \(F\), evaluated under identical thresholds.
- **Negative structural control:** random relabeling of \(k\mapsto[k]P\), plus an independently sampled generic ordinary curve at each size.
- **Duplicate control:** alternate characters, observables, solvers, and post-hoc top-frequency selectors with no sparse-support theorem.

## Quantitative promotion and falsification gates

Reopening requires a reviewed sparse-support and computability theorem before benchmarking. A subsequent preregistered `toy` study must use at least 20 fresh curves at each of 14, 16, 18, and 20 subgroup bits, exhaustive spectra and scalar truth through 18 bits, and at the two largest sizes at least 1,000 exact verified source relations plus 100 blind masked descents per size. It must show zero relation/scalar errors, no target-conditioned mode choice, audited rank at least \(0.80B\) before solve and exactly \(B\) at solve, and bootstrap 95% upper confidence bounds \(\lambda\le0.45\) and \(\mu\le0.45\) with support materialization and failed candidates included.

The mechanism is falsified if the proved or observed support is \(N^{1/2-o(1)}\) or larger, if a random relabeling preserves the claimed gain, if any accepted exact relation or blind scalar fails verification, if state/orbit preparation is omitted, or if preregistered scaling gives a 95% lower confidence bound \(\lambda\ge0.50\) or \(\mu\ge0.50\). The currently closest spectral results support the latter boundary, so this record remains merged/rejected.

## Artifact plan

If a new theorem reopens the record, preserve it at `ideas/artifacts/ECDLP-IDEA-110/scalar_spectrum_no_go.md`, freeze the observable/sheaf/support and cost model at `ideas/artifacts/ECDLP-IDEA-110/spectral_model.yaml`, and place independent spectra, ranks, controls, and blind-descent analysis at `ideas/artifacts/ECDLP-IDEA-110/analysis.md`. Planned paths are not evidence and no empty artifact directory should be created.

## Interpretation boundary

The hidden-shift identity \(G_Q(k)=F(k+x)\) is algebraically correct but does not provide cheap access to a useful spectrum. Exact character values, a correlation peak, a correct toy shift, or valid relation rows establish scoped correctness only. Heuristic cancellation, model-bound query complexity, novelty-unverified sheaf claims, and quantum-oracle results cannot be reported as a classical ECDLP breakthrough. Promotion requires complete source, output, rank, factor-log, blind descent, verification, and memory costs below rho/BSGS.

## Exactly one next executable action

1. Write a theorem-or-no-go note for scalar-index Fourier support of bounded-conductor public trace observables at `ideas/artifacts/ECDLP-IDEA-110/scalar_spectrum_no_go.md`, without running a parameter search or creating the artifact directory unless the note proves a sub-rho computable support family.
