# Independent technical review — TASK-20260722-203

Role: independent Reviewer  
Producer: `TASK-20260722-201`, snapshot commit `f94da7203a708fd33fc0e7791f8247134d260143`  
Candidate: `IDEA-20260722-001`  
Review type: literature and theory only; no empirical evidence and no authority to change official state.

## Verdict

The candidate is not ready for experiment design. Its basic module-isometry identity is correct, but four necessary links are missing:

1. the orbit statistics have not been shown to be anything other than relabeled scores from rotated dual vectors;
2. the orbit action has not been composed with LaMS's p-adic layer state, signed carries, and modulus-switching map;
3. effective covariance rank does not establish distinguishing power or corrected false-positive tails;
4. the frozen 2-bit comparison uses a stale, buggy Ogilvie cost table.

A symbolic derivation task could still be useful. The proposed `n=32` experiment is premature because its two principal arms—“plain LaMS layer scoring” and the composed orbit scorer—are not yet reproducibly defined.

## 1. Primary-source and baseline review

### 1.1 Material correction to the claimed strongest baseline

The producer accurately transcribed Table 2 of Ogilvie, ePrint 2026/279:

| Set | `C0` | `CC` | `CN` |
|---|---:|---:|---:|
| Kyber/ML-KEM-512 | 118.8 | 137.1 | 132.2 |
| Kyber/ML-KEM-768 | 170.2 | 192.7 | 186.9 |
| Kyber/ML-KEM-1024 | 234.8 | 257.2 | 252.4 |

Those values are present in the primary paper, but they are not a sound current baseline at the stated 2026-07-22 cutoff.

Hou and Jiang, ePrint 2026/366, Section 1.2 and Table 1.1, report that Ogilvie's implementation called `lambda_2` with a mismatched parameter. Their footnote says the issue was confirmed by Ogilvie and caused the 2–3-bit improvements to be overestimated. Their corrected reproduction is:

| Set | corrected LWE `CC` | corrected isometric MLWE `CC` | corrected `CC` gap |
|---|---:|---:|---:|
| 512 | 139.3 | 139.1 | 0.2 |
| 768 | 194.7 | 194.7 | 0.0 |
| 1024 | 259.6 | 259.0 | 0.6 |

The maximum corrected gap in any of their three models is 0.8 bit (`CN`, 768), not 2–3 bits. This is reinforced by the originating repository: Ogilvie's `TabOg/CodedDualAttack` commit `77efa3150a2c19809b5499e504bf7c2eab374935`, dated 2026-04-28, is titled “fix bug in probability calculation; better R search.”

Therefore these producer statements are incorrect:

- `137.1/192.7/257.2` as the strongest *current* CC baseline;
- that “Ogilvie's later table” supersedes Hou–Jiang's 0–0.8-bit result. The chronology and correction run the other way.

The error is conservative for some proposed pass thresholds because 137.1 is lower than the corrected 139.1, but that does not make it an admissible baseline. A comparison must use correct values and pinned code.

### 1.2 Li–Zheng and the model-matched lower envelope

Li and Zheng, ePrint 2026/1400, Table 3, does support the producer's quoted minima:

| Set | minimum `C0` | minimum `CC` | minimum `CN` |
|---|---:|---:|---:|
| 512 | 118.09 | 139.20 | 134.42 |
| 768 | 172.36 | 194.02 | 189.36 |
| 1024 | 238.12 | 259.40 | 253.68 |

The paper also explicitly says short-vector sampling dominates its total costs, while its FFT and decoding subcosts improve by roughly 1–6 and 2–7 bits. Its `CC` model ignores memory-access cost.

Using only corrected Hou–Jiang and Li–Zheng `CC` values gives the following provisional lower envelope:

| Set | provisional corrected `CC` comparator | 2-bit target |
|---|---:|---:|
| 512 | 139.1 | at most 137.1 |
| 768 | 194.02 | at most 192.02 |
| 1024 | 259.0 | at most 257.0 |

This is not yet a fully charged baseline: the estimator assumptions, success targets, memory treatment, and LaMS cost model still need reconciliation.

### 1.3 LaMS

The primary ePrint 2026/1326 landing record supports these scoped claims:

- LaMS fixes one small prime \(p\);
- it recovers a guessed secret component digit by digit in a \(p\)-adic expansion;
- each recovered digit is subtracted before targeting the next digit;
- its reported 22/31/41-bit reductions are relative to the *corrected CRT-based Qu–Xu comparator* for 512/768/1024.

Those deltas are not reductions from Carrier, Li–Zheng, corrected Ogilvie, or an end-to-end best-known baseline. The producer generally says this correctly.

The full 2026/1326 PDF was blocked by the source's bot challenge in this runtime. I could verify the primary metadata and indexed primary abstract, but not its exact internal formulas, absolute tables, or code link. Consequently, any absolute LaMS cost and any assertion that it is already expressed in the same `CC` model are **unverified** here. The producer supplies neither.

### 1.4 Ducas–Pulles and closest prior work

Ducas and Pulles, *Journal of Cryptology* 39:8 (2026), verify that the independent-score heuristic used in earlier dual-sieve analyses is invalid in relevant regimes. The paper identifies the target, particularly its norm, as a confounder shared by all individual scores. It develops conditional score-distribution models and analyzes false positives and negatives.

It does **not** establish that estimating a covariance matrix and applying generalized least squares repairs the tails. The producer's phrase “Ducas–Pulles correction” is sound only if it means that dependence and wrong-candidate tails must be modeled; it does not support the proposed GLS rule.

The closest direct prior work is stronger than the producer's novelty discussion suggests:

- Wu and Xu, ePrint 2022/1661, prove that one short dual vector yields \(n-1\) same-length rotations and use all rotations in the distinguisher. They explicitly discuss correlation, though their near-orthogonality treatment remains heuristic. The producer incorrectly attributes this paper to “Wang et al.”
- Ogilvie 2026/279 reuses the same expensive short-vector pool while changing the isometry and zero-pattern event. Its correctness bound includes a false-positive term across all trials.
- Hou–Jiang 2026/366 uses the same module identity in hybrid decoding and gives the corrected ML-KEM estimates above.
- Li–Zheng 2026/1400 already batches candidate score evaluation by FFT after modulus switching and lossy coding.

The exact phrase “p-adic layers plus covariance-weighted isometry orbit” was not located. That absence does not establish substantive novelty when the orbit algebra and batching reduce to known constructions.

## 2. Module-matrix orbit algebra

Let

\[
R_q=\mathbb Z_q[X]/(X^n+1),\qquad
\mathbf b=\mathbf A\mathbf s+\mathbf e,
\]

with \(\mathbf A\in R_q^{m\times k}\). For \(r=X^j\), commutativity of \(R_q\) gives

\[
r\mathbf b
=r(\mathbf A\mathbf s+\mathbf e)
=\mathbf A(r\mathbf s)+r\mathbf e.
\]

Multiplication by \(X^j\) is a negacyclic signed coefficient permutation. Let \(P_j\) be its \(n\times n\) coefficient matrix, and let \(\bar A\) be the flattened \(mn\times kn\) block-negacyclic matrix. The precise intertwining identity is

\[
P_j^{(m)}\bar A=\bar A P_j^{(k)},\qquad
P_j^{(m)}\bar b
=\bar A P_j^{(k)}\bar s+P_j^{(m)}\bar e,
\]

where \(P_j^{(u)}=I_u\otimes P_j\). This is more precise than saying a single square matrix “commutes with \(A\),” because the row and column spaces can have different dimensions.

For ML-KEM's i.i.d. centered-binomial coefficients, signed permutation preserves the joint secret and error distributions exactly. This part of the producer mechanism is supported.

### 2.1 Information versus relabeling

Every orbit target is a deterministic, invertible function of \(\bar b\). If the identity rotation is included,

\[
I(\mathbf s;\bar b,\{P_j^{(m)}\bar b\}_j\mid \bar A)
=I(\mathbf s;\bar b\mid\bar A).
\]

Thus the orbit creates no new Shannon information. It can only expose existing information more cheaply to a restricted attack.

The score identity is even more direct. For the standard cosine score

\[
f_W(t)=\sum_{w\in W}\cos\!\left(\frac{2\pi}{q}\langle w,t\rangle\right),
\]

orthogonality of a signed permutation gives

\[
f_W(P_jt)
=\sum_{w\in W}\cos\!\left(\frac{2\pi}{q}
  \langle P_j^Tw,t\rangle\right)
=f_{P_j^TW}(t).
\]

Therefore evaluating all rotated targets with one vector pool is exactly evaluating the original target with the rotated vector sets. Negacyclic convolution may compute these correlations efficiently, but it does not make them independent observations. This is the algebraic core of Wu–Xu's rotated-vector construction.

There are only two possible gains:

1. **computational reuse:** rotated vectors or targets are cheaper to obtain than fresh reduction/sieving outputs;
2. **coverage:** a rotation moves a favorable secret pattern into a partition that a fixed reduced lattice can exploit, as in Ogilvie.

Neither is new information. The proposed control comparing true rotations with arbitrary signed permutations is not matched: a generic signed permutation does not satisfy
\(P^{(m)}\bar A=\bar A P^{(k)}\), so it need not preserve the attack lattice or even define a valid same-\(A\) MLWE target.

### 2.2 Partitioned dual lattices remain an obligation

For an unpartitioned module matrix, the intertwining identity is enough. A hybrid attack fixes column sets \(I_{\rm lat},I_{\rm fft},I_{\rm enu}\), and its short vectors are valid for a lattice built from the selected submatrix. Arbitrary rotation need not preserve those column sets.

Ogilvie addresses this by rotating the target/secret while retaining a carefully defined fixed lattice and changing the tested zero-pattern event. Wu–Xu instead constructs a lattice whose vectors have valid rotations. The candidate does neither derivation for LaMS. “Same \(A\)” alone is insufficient to conclude that one short-vector pool is valid for every orbit score after puncturing, modulus switching, and digit guessing.

## 3. LaMS composition is not yet defined

Write the guessed secret block in \(p\)-adic form

\[
s_g=d_0+p d_1+\cdots+p^{L-1}d_{L-1}.
\]

After recovering the first \(t\) digits, let

\[
h_t=\sum_{\ell<t}p^\ell d_\ell,\qquad
u_t=(s_g-h_t)/p^t.
\]

For a split \(A=(A_g\mid A_r)\), the residual target is

\[
b_t=b-A_gh_t
=A_gp^tu_t+A_rs_r+e\pmod q.
\]

LaMS applies its modulus-switching dual subroutine so that the next digit of \(u_t\) modulo \(p\) can be recovered. A valid orbit composition must show, for every \(P_j\),

\[
P_jb_t
=\bar A\,P_j(s-h_t)+P_je
\]

and must identify the exact candidate, partition, rounding error, and dual lattice used after switching.

The following are missing:

- whether \(P_jh_t\) is available in the representation expected by the next layer;
- how negacyclic signs act on ordinary \(p\)-adic digits. Negation is not digitwise without borrow/carry handling;
- whether all rotations target one common correct digit or different candidate coordinates;
- whether the same switched dual-vector distribution is valid across layers;
- whether early-layer mistakes, orbit multiplicity, and retries preserve LaMS's proof conditions.

If scores are inverse-rotated so that they refer to one common candidate, Section 2.1 shows that they become rotated-vector scores on the original target. If they are not aligned, only a subset may represent a correct candidate and GLS averaging can dilute the signal. Either way, a formal layer invariant is required before implementation.

## 4. Statistical review

Ducas–Pulles use the individual score

\[
f_w(t)=\cos(2\pi\langle t,w\rangle)
\]

and show why treating \(\{f_w(t)\}_{w\in W}\) as independent can badly mispredict the total score. Scaling or changing the norm of the target moves many inner products together, which creates a shared confounder and heavy wrong-candidate behavior.

The producer proposes

\[
r_{\rm eff}=\frac{(\operatorname{tr}\Sigma)^2}
{\operatorname{tr}(\Sigma^2)}.
\]

This is a spectral participation ratio. It says how many covariance eigenvalues are appreciable. It says nothing by itself about separation between correct and wrong candidates. A pure relabeling can have large \(r_{\rm eff}\), and a high-rank statistic can have zero mean separation.

Let

\[
\delta_\mu=\mathbb E[Z\mid\mathrm{correct}]
-\mathbb E[Z\mid\mathrm{wrong}].
\]

Under a common Gaussian covariance model, the relevant linear-discrimination quantity would be

\[
\mathrm{SNR}^2=\delta_\mu^T\Sigma^{-1}\delta_\mu,
\]

not \(r_{\rm eff}\). The usual GLS weights
\(w\propto\Sigma^{-1}\mathbf1\) are justified only when the signal has a common-mean direction proportional to \(\mathbf1\). That condition is not established and is doubtful when only some rotations satisfy a layer guess or zero pattern.

Even a Mahalanobis calculation would not settle the Ducas–Pulles objection. The attack needs conditional tail control over:

- all orbit elements;
- all \(p^{k_{\rm fft}}\) or \(q^{k_{\rm fft}}\) FFT candidates;
- all p-adic layers;
- all retries after an early wrong digit;
- every orbit-subset and weight model considered during training.

Ogilvie's corresponding success lower bound explicitly includes
\[
\eta P_{\rm good}(1-\mu)-R q^{k_{\rm fft}}P_{\rm wrong}.
\]
The candidate has no analogous multiplicity term.

Thirty seeds per dimension, further divided into training and holdout, are not enough to estimate rare false-positive tails or validate a fourfold vector reduction without a precomputed power analysis. “Two times lower false-positive rate” is also undefined when the baseline event may occur zero times in such a small holdout.

## 5. Fully charged 2-bit threshold

The declared material threshold—two bits in one matched total-cost model—is reasonable in principle. The intermediate fourfold vector-count prediction is not sufficient.

Let the baseline total cost be

\[
C_{\rm base}=S+U,
\]

where \(S\) is the subcost affected by the proposal and \(U\) is unchanged work. If the affected work falls by a factor \(f\) and the proposal adds overhead \(H\),

\[
C_{\rm new}=\frac Sf+U+H.
\]

A two-bit gain requires

\[
\log_2(C_{\rm base}/C_{\rm new})\ge2
\quad\Longleftrightarrow\quad
\frac Sf+U+H\le\frac{S+U}{4},
\]

or

\[
S\left(\frac14-\frac1f\right)\ge\frac{3U}{4}+H.
\]

If \(f=4\), the left side is zero. Any positive unchanged work or overhead makes a full two-bit reduction impossible. The vector or score subcost must fall by *more* than fourfold, reduce another dominant term, or induce a favorable global reoptimization.

The candidate must charge:

- basis construction and all reduction/sieving or DGS work;
- every saved and rotated vector;
- layer-specific target updates and rounding;
- orbit selection and covariance training;
- transforms, precision conversion, and memory traffic;
- false-positive candidate verification;
- full success amplification after layer errors.

The existing `n=32` gate measures none of the exponential estimator terms reliably and cannot bridge to \(n=256\). It may test code equality, but it cannot validate the 2-bit claim.

## 6. Cheapest decisive next gate

Do not implement the current toy experiment. First produce a bounded symbolic derivation with these deliverables:

1. Define one LaMS layer completely: target, switched modulus, dual lattice/vector distribution, score, candidate space, and update.
2. Define the orbit action on the layer state, including signed \(p\)-adic carries and all hybrid partitions.
3. Prove that every reused vector is valid for every claimed orbit statistic.
4. Reduce the orbit statistic algebraically. If it equals \(f_{P_j^TW}(t)\), compare it directly with Wu–Xu and corrected Ogilvie and identify the claimed non-overlapping cost.
5. State \(\delta_\mu\), the conditional covariance or joint model, and a family-wise false-positive bound; do not use effective rank as the pass metric.
6. Regenerate the corrected comparator table from pinned commits and derive the end-to-end condition \(C_{\rm new}\le C_{\rm baseline}/4\).

Fail this gate if the statistic is only rotated-vector relabeling, if the layer and orbit actions do not commute, if pool validity fails, or if a lower-bound cost decomposition cannot reach two bits. Pass only if the derivation identifies a non-equivalent statistic or amortization not already charged by the closest prior work.

This gate is cheaper and more decisive than the proposed implementation. A pass would justify experiment design, not a standardized-parameter attack claim.

## Sources independently checked

- Tabitha Ogilvie, *On the Concrete Hardness Gap Between MLWE and LWE*, ePrint 2026/279: <https://eprint.iacr.org/2026/279>
- Jianhua Hou and Haodong Jiang, *Careful with the Ring*, ePrint 2026/366: <https://eprint.iacr.org/2026/366>
- Ogilvie estimator correction, commit `77efa315...`: <https://github.com/TabOg/CodedDualAttack/commit/77efa3150a2c19809b5499e504bf7c2eab374935>
- Rui-Jie Wang et al., *LaMS*, ePrint 2026/1326: <https://eprint.iacr.org/2026/1326>
- Léo Ducas and Ludo N. Pulles, *Accurate Score Prediction for Dual-Sieve Attacks*, J. Cryptology 39:8 (2026): <https://doi.org/10.1007/s00145-025-09560-7>
- Han Wu and Guangwu Xu, *Enhancing the Dual Attack against MLWE*, ePrint 2022/1661: <https://eprint.iacr.org/2022/1661>
- Yechen Li and Qunxiong Zheng, *What Happens When integrating Modulus Switching and Lossy Source Coding*, ePrint 2026/1400: <https://eprint.iacr.org/2026/1400>
- Kevin Carrier et al., *Assessing the Impact of a Variant of MATZOV's Dual Attack on Kyber*, ePrint 2022/1750: <https://eprint.iacr.org/2022/1750>

All web checks were performed on 2026-07-22. Claims marked unverified remain unverified; no missing source content was inferred as a successful check.
