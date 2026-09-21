# ECDLP-IDEA-009 — Nonequivariant trace-zero transfer

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- State: `proposed_unapproved`
- Evidence scale: `toy` preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an injective transfer or valid relation in a trace-zero variety is not an attack unless the complete relation/base-log/target-descent cost beats rho.

## Falsifiable hypothesis

For a prime-order subgroup \(G=\langle P\rangle\subset E(\mathbb F_p)\), \(|G|=N\asymp p\), there is a fixed or slowly growing extension \(K=\mathbb F_{p^k}\), a trace-zero variety
\[
  T_k(E)=\ker\!\left(\operatorname{Tr}_{K/\mathbb F_p}:E(K)\to E(\mathbb F_p)\right),
\]
and an explicit **Frobenius-nonequivariant scalar-compatible transfer**
\[
  \tau:G\longrightarrow T_k(E)[N],\qquad \tau([a]P)=[a]\tau(P),
\]
whose image lies in a publicly recognizable low-complexity locus \(Z\subset T_k(E)\). Decompositions of random points in \(\langle\tau(P)\rangle\) over a target-independent replacement base on \(Z\), followed by separate descent of \(\tau(Q)\), have total exponent below \(1/2\). The hypothesis explicitly excludes ordinary base extension \(i:E(\mathbb F_p)\hookrightarrow E(K)\), because \(\operatorname{Tr}\circ i=[k]\) and hence \(i(G)\cap T_k(E)=\{O\}\) when \(N\nmid k\). It is `toy`, `heuristic`, `model-bound`, and `novelty-unverified`.

## Mechanism-new operation

The new operation is a constructed map that moves the rational Frobenius-fixed \(N\)-torsion line into a Frobenius-nontrivial trace-zero direction while preserving hidden scalars, plus a low-complexity image locus that changes decomposition density. It is not the scalar base-extension/trace map, a coordinate rewrite, a same-field isogeny, or generic trace-zero index calculus. A transfer without a new decomposable locus, or a locus without an explicit target-compatible transfer, is only a control. The recorded obstruction is removed only if nonequivariance and efficient construction are proved rather than assumed.

## Assumptions

1. \(E/\mathbb F_p\), \(P\), and prime \(N=\operatorname{ord}(P)\asymp p\) are public; \(k\), \(K\), the trace-zero representation, and all cofactors are explicit.
2. \(N\nmid k\), so the ordinary inclusion is provably excluded; any exceptional choice with \(N\mid k\) is costed and may not use an extension degree of size \(N^{1-o(1)}\).
3. \(\tau\) is evaluable from a point, not from its scalar, and its scalar compatibility, injectivity on \(G\), trace-zero membership, and image-locus membership are independently verifiable.
4. The data causing nonequivariance is public and target-independent; construction of extension fields, eigenvectors, distortion-like maps, correspondences, and descent data is fully charged.
5. A replacement base \(\mathcal B=\{B_1,\ldots,B_{N^{\beta+o(1)}}\}\subset Z\) is generated before \(Q\), and accepted decompositions include pushforward/group-law certificates inside \(T_k(E)\).
6. Relation and target-descent reciprocal densities, extension-field arithmetic, coefficient growth, matrix rank/density, base logs, conversion, verification, and memory are all measured.
7. No source or extension-field DLP, hidden endomorphism-ring oracle, target-dependent branch, or post-hoc image selector is available.

## Semantic fingerprint

`prime-field rational torsion line -> explicit scalar-compatible Frobenius-nonequivariant transfer -> trace-zero eigendirection and low-complexity image locus -> replacement-base decompositions -> trace-zero base logarithms -> separate transferred-target descent`

The indispensable operations are both the **nonequivariant scalar transfer** and the **decomposition-changing image locus**. Ordinary trace, conorm/base inclusion, a coordinate model of \(T_k\), or generic relations in the full trace-zero variety is a duplicate/control.

## Five closest ledger entries

1. `ledger/H-ISO-001.yaml` — closest map-based hypothesis; ordinary same-field isogenies commute with Frobenius and do not move the rational torsion line into trace zero.
2. `ledger/EV-ISO-001.yaml` — closest empirical negative showing small isogenous neighbors did not alter relation yield.
3. `ledger/FINDING-PF-IC-001.md` — closest full prime-field index-calculus cost boundary, including decomposition density and target descent.
4. `ledger/H-FB-001.yaml` — closest structured-factor-base hypothesis; the locus \(Z\) must change the mechanism, not only the base labels.
5. `ledger/SYNTHESIS-20260716.md` — governing scoped-negative and full-accounting requirements.

## Closest primary literature

- Elisa Gorla and Maike Massierer, [Index calculus in the trace zero variety](https://arxiv.org/abs/1405.1059), provides the closest direct trace-zero index-calculus construction and its summation-polynomial costs; it does not transfer a large rational prime-order subgroup nonequivariantly.
- Claus Diem and Nils Naumann, [On the structure of Weil restrictions of abelian varieties](https://arxiv.org/abs/math/0504359), gives the relevant Weil-restriction and trace-kernel structural setting.
- Pierrick Gaudry, [Index calculus for abelian varieties and the elliptic curve discrete logarithm problem](https://doi.org/10.1016/j.jsc.2008.08.005), supplies the decomposition/relation framework whose complete cost must be charged after transfer.
- Yan Bo Tian, [A cryptanalytic application of Weil descent](https://arxiv.org/abs/2012.07173), is a nearby primary example of a cover/Weil-descent transfer for elliptic curves over extension fields, not a generic prime-field nonequivariant map.
- Victor Shoup, [Lower Bounds for Discrete Logarithms and Related Problems](https://www.shoup.net/papers/dlbounds1.pdf), is the generic baseline. None of these sources proves the claimed transfer from \(E(\mathbb F_p)[N]\), so novelty remains `novelty-unverified`.

## Complete factor-base-to-target-descent path

1. Freeze \((E,P,N)\), an extension degree \(k\), a representation of \(T_k(E)\), the public transfer data for \(\tau\), and a proof/test that \(\operatorname{Tr}(\tau(P))=O\) while \(\tau(P)\ne O\).
2. Define the low-complexity locus \(Z\), construct \(B=N^{\beta+o(1)}\) target-independent base elements \(B_i\in Z\cap\langle\tau(P)\rangle\) or certified projected atoms, and record the cost of finding their source-group relation coordinates when needed.
3. For uniform public \(a\), compute \(R=[a]\tau(P)=\tau([a]P)\), run the frozen trace-zero decomposition procedure, and accept only a complete certificate \(R=\sum_i e_iB_i\) in \(T_k(E)\).
4. Collect enough independent relations to solve for \(\log_{\tau(P)}(B_i)\), charging extension-field arithmetic, failed decompositions, dependencies, coefficient reduction, and measured sparse/dense linear algebra.
5. After the base-log phase is immutable, sample independent \(t\), transfer \(Q+[t]P\), and decompose \(\tau(Q)+[t]\tau(P)\) using the unchanged \(Z\), base, and solver.
6. From a verified target decomposition recover \(x\equiv-t+\sum_i e_i\log_{\tau(P)}(B_i)\pmod N\), with signs fixed by the certified relation convention.
7. Accept only if \([x]P=Q\), and report transfer construction, relation collection, linear algebra, target descent, conversion, and memory separately.

## Full rho/BSGS cost model

Let \(B=N^{\beta+o(1)}\). Let construction of \(K\), \(T_k\), nonequivariant data, \(\tau\), and \(Z\) cost \(N^{c+o(1)}\). Let extension degree/representation have explicit exponent \(k=N^{\kappa+o(1)}\) when it is not constant, and let one transfer plus decomposition attempt cost \(N^{u+o(1)}\), including all \(k\)-dependent field operations. Let relation and target reciprocal densities be \(N^{\delta+o(1)}\) and \(N^{\delta_t+o(1)}\); let certificate/conversion verification cost \(N^{v+o(1)}\), and memory use \(N^{s+o(1)}\) bits, including extension-field and coefficient representations.

- Generic rho: \(T_{\rho}=N^{1/2+o(1)}\), \(M_{\rho}=N^{o(1)}\).
- BSGS: \(T_{\rm BSGS}=N^{1/2+o(1)}\), \(M_{\rm BSGS}=N^{1/2+o(1)}\).
- Transfer/variety/base preprocessing: \(T_{\rm pre}=N^{\max(c,\beta+u_0,\kappa)+o(1)}\), where \(u_0\) is the per-base-element construction exponent.
- Relation collection: \(T_{\rm rel}=N^{\beta+u+\delta+o(1)}\).
- Linear algebra: \(T_{\rm LA}=N^{2\beta+o(1)}\), \(M_{\rm LA}=N^{\beta+o(1)}\) for a genuinely sparse Wiedemann model; dense fallback is \(N^{3\beta+o(1)}\), and the measured applicable exponent is charged.
- Target descent: \(T_{\rm desc}=N^{u+\delta_t+o(1)}\).
- Verification/conversion over accepted base relations contributes \(N^{\beta+v+o(1)}\); one final transfer/scalar verification contributes \(N^{v+o(1)}\).

The optimistic sparse total is
\[
 \lambda=\max\{c,\beta+u_0,\kappa,\beta+u+\delta,2\beta,\beta+v,u+\delta_t,v\},
\]
with \(2\beta\) replaced by \(3\beta\) if the matrix is dense. The memory exponent is
\[
 \mu=\max\{s,\beta,\kappa\}.
\]
Any work to find an \(N\)-torsion eigenvector, distortion-like map, or image-locus branch is part of \(c\), not free advice. A fixed \(k\) has \(\kappa=0\), but that alone does not improve the density terms.

## Likely fatal obstruction

The standard inclusion \(i:E(\mathbb F_p)\to E(K)\) obeys \(\operatorname{Tr}\circ i=[k]\); for prime \(N\nmid k\), its \(N\)-torsion image cannot be trace zero. More generally, every \(\mathbb F_p\)-defined morphism commutes with Frobenius and preserves the Frobenius-fixed rational line. On an ordinary curve, the geometric endomorphism algebra is commutative with Frobenius, so a distortion-like map between Frobenius eigenspaces is not normally available. Constructing data over \(K\) that breaks equivariance may therefore require finding an unavailable eigenvector/endomorphism, may fail to descend to a public map, or may be DLP-equivalent. Even if \(\tau\) exists, its image is still a cyclic subgroup of size \(N\), and generic trace-zero decomposition or dense summation-polynomial elimination can restore an exponent of at least \(1/2\).

## Proof track

1. Exhibit an explicit public construction of \(\tau\) and prove scalar compatibility, injectivity, trace-zero membership, nonequivariance, and target independence.
2. Prove that \(Z\) contains \(\tau(G)\) or a positive-density recognizable part and that its replacement-base decomposition law has the claimed density without solving a DLP.
3. Prove complete relation and descent correctness under the chosen trace-zero coordinates, including exceptional orbits, sign ambiguity, and extension-field descent.
4. Bound \((c,\kappa,\beta,u_0,u,\delta,\delta_t,v,s)\) and derive \(\lambda<1/2-\varepsilon\) under an explicitly applicable sparse/dense linear-algebra model.

## Disproof track

1. Symbolically verify \(\operatorname{Tr}\circ i=[k]\) and test every candidate transfer for Frobenius equivariance; reject scalar base-extension variants immediately.
2. Compute toy endomorphism/Frobenius eigenspaces and determine whether constructing \(\tau\) needs a forbidden distortion direction, target scalar, or extension degree with exponent at least \(1/2\).
3. Compare decomposition yield on \(Z\) with equal-size random trace-zero and source-curve bases; reject if the locus supplies no statistically significant exponent change.
4. Fit full relation, rank, linear-algebra, and target-descent costs; reduce the successful transfer path to ordinary trace-zero/prime-field index calculus if its measured behavior is unchanged.

## Positive and negative controls

- Positive structural control: exhaustive toy torsion where both Frobenius eigenspaces are explicitly known; an oracle-labeled map between them validates trace, scalar-compatibility, and certificate code only.
- Positive algorithm control: generated trace-zero decompositions with known coefficients must verify and recover the injected scalar through the complete base-log/descent pipeline.
- Negative control: the ordinary inclusion \(i\) with \(N\nmid k\) must always fail trace-zero membership except at \(O\); accepting it invalidates the implementation.
- Negative control: every \(\mathbb F_p\)-defined isogeny/endomorphism control must remain in the Frobenius-fixed direction and must not be relabeled nonequivariant.
- Negative control: shuffled coordinates, one altered Frobenius conjugate, or a wrong trace-zero equation must invalidate the certificate.
- Leakage control: blind and permute targets; forbid target-derived eigenvectors, post-hoc \(Z\), and hidden source/extension DLPs.

## Quantitative promotion and falsification gates

Promotion requires zero false trace/transfer/decomposition certificates; an explicit non-oracle \(\tau\) on every frozen instance; at least 200 independent accepted relations and 100 independent target descents on each of the three largest toy sizes; matrix rank at least \(0.95B\); a 95% upper confidence bound on fitted \(\lambda\) below \(0.50\) with point estimate \(\lambda\le0.45\); measured \(\mu\le0.45\); and a statistically significant decomposition-rate improvement over equal-size source and random trace-zero controls at \(p<0.01\) with preregistered test. Any promoted result remains `toy`, `heuristic`, `model-bound`, and `novelty-unverified`.

Falsify or demote if \(\tau\) is ordinary inclusion/trace, commutes with Frobenius in a way that keeps the image fixed, needs a source or extension DLP, requires \(\kappa\ge0.50\), produces no usable low-complexity locus, has relation/descent density yielding \(\lambda\ge0.50\), triggers dense algebra at exponent \(0.50\), or differs from the representation/factor-base controls by less than 10% across the frozen ladder.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-009/contract.yaml` — frozen curve/extension ladder, torsion conditions, transfer interface, locus, controls, and gates.
- `ideas/artifacts/ECDLP-IDEA-009/trace_zero_transfer_preflight.sage` — Frobenius/trace computations, candidate transfer construction, eigenspace audit, and certificate verifier.
- `ideas/artifacts/ECDLP-IDEA-009/decomposition_probe.sage` — replacement-base relation and separate target-descent probe.
- `ideas/artifacts/ECDLP-IDEA-009/runs/<run_id>/transfers.jsonl` — transfer, trace, locus, equivariance, and rejection evidence.
- `ideas/artifacts/ECDLP-IDEA-009/runs/<run_id>/costs.tsv` — construction, extension, density, rank, linear algebra, descent, verification, and memory.
- `ideas/artifacts/ECDLP-IDEA-009/analysis.md` — obstruction audit, fitted exponents, controls, and scoped decision.

## Interpretation boundary

A valid trace-zero point, a scalar-compatible toy transfer, a relation on \(T_k(E)\), or a recovered toy scalar is not a breakthrough. Ordinary inclusion is closed by \(\operatorname{Tr}\circ i=[k]\), and a candidate survives only if it constructs a genuinely nonequivariant map and changes the full decomposition/descent exponent. Claims remain `toy`, `heuristic`, `model-bound`, and `novelty-unverified` until independently verified.

## Exactly one next executable action

1. Draft and structurally validate the bounded eigenspace-and-trace obstruction contract at `ideas/artifacts/ECDLP-IDEA-009/contract.yaml`, requiring explicit public transfer families before any execution.
