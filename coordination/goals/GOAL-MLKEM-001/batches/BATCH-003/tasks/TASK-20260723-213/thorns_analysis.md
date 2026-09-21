# ePrint 2026/1022 (“Thorns”) and ML-KEM

Task `TASK-20260723-213` · literature/theory analysis only · no official state
transition

Inference: `research-sol-max` requested; resolved as
`gpt-5.6-sol-xhigh`, reasoning effort `xhigh`, fallback used, adapter
`cursor-subagent-2026-07`.

## Bottom line

The paper proves an informative but narrow result: for one product of two
polynomials whose coefficients are independent continuous Gaussians, and for a
fixed power-of-two ring dimension, conditioning on an increasingly large
Euclidean norm forces the product direction toward one of \(n/2\) fixed real
two-dimensional Fourier planes. It also gives exact signed-permutation and
partial-sum identities that explain the known constant-sign and alternating
patterns in the Guo et al. LAC failure attack.

That does **not** transfer as a theorem to FIPS 203. ML-KEM uses bounded
CBD(2)/CBD(3) coefficients, \(2k\) principal convolution products, dependent
compression errors, arithmetic modulo \(3329\), coefficientwise decoding, and
fixed \(n=256\). The paper computes none of the three standardized failure
probabilities, constructs no ML-KEM failure oracle, and gives no passive
public-key-only attack. It does not quantify an improvement to conditional
failure boosting. Its present ML-KEM value is a candidate modeling mechanism,
not a changed FIPS bound or attack cost.

There is also a material internal scale issue. With the paper's displayed
\(\mathcal{CN}(0,\sigma^2)\) convention, its true product-amplitude density has
second moment \(\sigma^4\), while its displayed Gaussian-surrogate amplitude
density has second moment \(4\sigma^2\). They are not an
“identical-standard-deviation” comparison at the plotted \(\sigma=10\).
Accordingly, Figure 4 and the broad claim that independence “systematically
underestimates the noise norm” should not be used quantitatively before this
normalization is resolved.

## Source freeze and artifact search

The current ePrint record was checked on 2026-07-23.

- Paper: Dongshu Cai, Yijian Liu, Jiabo Wang, and Xianhui Lu, *Thorns in
  Polynomial Convolution: Correlation, Large Deviations, and Applications*,
  ePrint 2026/1022.
- Current revision: 2026-07-19, version timestamp `20260719:093516`;
  version-specific record
  <https://eprint.iacr.org/2026/1022/20260719:093516>.
- Received/first version: 2026-05-21, version timestamp
  `20260521:154554`; version-specific record
  <https://eprint.iacr.org/2026/1022/20260521:154554>.
- The full current 34-page PDF was fetched through the document extractor.
  The fetcher supplied converted text rather than the binary PDF. The full
  extracted text has SHA-256
  `fcd895e7e19e1ea7dcf2eb38527aa2f62b2d26d450c3ac4eeca6b9a48c13e655`
  (69,700 bytes, 1,497 lines). This is an extraction hash, not a PDF hash.
- The ePrint record lists only PDF. The paper contains no code/data URL, and
  targeted title/author/GitHub searches found no supplement or repository.
  This is a bounded search result, not proof that no later or private artifact
  exists.

FIPS 203 was checked in full. The referenced Kyber failure scripts were pinned
at `pq-crystals/security-estimates`
commit `75c26949a902ca297b181375bfb7cfaf22cce784`.

The theorem statements, displayed equations, FIPS parameters, and estimator
code paths below were verified directly. Figure trends, the paper's
“moderate effort” language, and all cited attack success/cost claims are
reported claims and were not reproduced. The FIPS Table 1 probabilities were
verified as normative listed values, not independently recalculated. No
empirical run was performed.

## The mathematical model

The paper works over

\[
K_{\mathbb R}\simeq \mathbb R[x]/(x^n+1),
\]

with \(n\) a power of two. If \(\tau(a)\) is the real coefficient vector and
\(\sigma(a)\) the canonical embedding, then
\(\tau(a)V=\sigma(a)\). Multiplication is negacyclic convolution in the
coefficient basis and componentwise multiplication in the embedding:

\[
\sigma(ab)=\sigma(a)\odot\sigma(b).
\]

For the reduced nonredundant embedding \(\rho\), exact Gaussian coefficient
vectors

\[
\tau(a),\tau(b)\stackrel{\mathrm{iid}}{\sim}N(0,\sigma^2 I_n)
\]

map to independent coordinates

\[
\rho(a)_j,\rho(b)_j\stackrel{\mathrm{iid}}{\sim}
\mathcal{CN}(0,n\sigma^2).
\]

This exact independence is a Gaussian fact: covariance and
pseudocovariance determine a jointly Gaussian law. For CBD inputs the same
Fourier coordinates can be uncorrelated without being independent.

### Product laws

For independent \(X_1,X_2\sim N(0,\sigma^2)\), the real product
\(P=X_1X_2\) has density

\[
f_P(t)=\frac{1}{\pi\sigma^2}K_0\!\left(\frac{|t|}{\sigma^2}\right).
\]

For independent \(Z_1,Z_2\sim\mathcal{CN}(0,\sigma^2)\),
\(W=Z_1Z_2\) has planar and radial densities

\[
f_W(z)=\frac{2}{\pi\sigma^4}
K_0\!\left(\frac{2|z|}{\sigma^2}\right),\qquad
f_{|W|}(r)=\frac{4r}{\sigma^4}
K_0\!\left(\frac{2r}{\sigma^2}\right).
\]

Its phase is uniform and independent of its magnitude. The Bessel asymptotic
makes the far radial tail exponential in \(r\), rather than Gaussian in
\(r^2\). Independent coordinates with that radial law therefore prefer to
make a large norm through one exceptional coordinate. “Thorn” denotes this
axis-directed joint tail.

## Reconstructed theorem statements

### Theorem 1: conditional spherical LDP

Let \(X\) have a two-dimensional density on \(\mathbb C\) whose radial tail is
bounded above and below, up to arbitrary exponential slack, by
\(\exp(-c|z|)\). For \(Z=(X_1,\ldots,X_n)\) with independent copies, consider
the direction conditioned on \(\lVert Z\rVert_2>R\). For fixed \(n\) and
\(R\to\infty\), the conditional directional laws obey a large-deviation
principle with speed \(R\) and rate

\[
I(u)=c(\lVert u\rVert_1-1),\qquad \lVert u\rVert_2=1.
\]

The denominator has exponential rate \(-c\); the numerator in a direction
\(u\) pays rate \(-c\lVert u\rVert_1\).

There is a local gap in the written lower-bound proof. Its polydisc centered
at \(Ru\) is claimed to lie inside \(\{\lVert z\rVert_2>R\}\), but it includes
inward perturbations with smaller norm. Centering the same fixed-radius
polydisc at \((R+C)u\), for fixed sufficiently large \(C\), appears to repair
the containment without changing the speed-\(R\) exponent. The theorem is
therefore plausible and readily repairable, but the proof is not literally
complete as printed.

### Corollaries 1 and 2: axes and Gaussian products

The rate vanishes exactly when \(u\) has one nonzero complex coordinate.
Outside any fixed \(\varepsilon\)-neighborhood of those axes, conditional mass
is at most

\[
\exp(-c_\varepsilon R+o(R)).
\]

For a product of two \(\mathcal{CN}(0,\tau^2)\) variables, the theorem applies
with \(c=2/\tau^2\). No explicit finite-\(R\) constant is supplied.

### Lemma 1 and Theorem 2: inverse embedding gives Fourier planes

The reduced embedding of an iid real Gaussian coefficient vector has iid
\(\mathcal{CN}(0,n\sigma^2)\) entries. The inverse transform is, up to scale,
an isometry taking complex axis \(i\) to

\[
P_i=\operatorname{span}_{\mathbb R}
\{(\cos(s\theta_i))_{s=0}^{n-1},
  (\sin(s\theta_i))_{s=0}^{n-1}\},
\quad \theta_i=\frac{(2i-1)\pi}{n}.
\]

Thus, for independent Gaussian polynomials \(a,b\), conditioned on
\(\lVert\tau(ab)\rVert_2>R\), the normalized coefficient vector approaches
\(\bigcup_{i=1}^{n/2}(P_i\cap S^{n-1})\). The probability outside an
\(\varepsilon\)-neighborhood is
\(\exp(-\kappa_\varepsilon R+o(R))\).

The limit is tail radius \(R\to\infty\) with dimension fixed. It is not a
dimension-asymptotic theorem.

### Theorem 3: exact signed cyclic partial sums

For every odd embedding index \(t\), multiplication of coefficient indices by
\(t\) modulo \(n\), together with the sign from crossing \(x^n=-1\), produces
a signed permutation \(b^{(t)}\) such that

\[
\sigma_t(e)=\sum_{j=0}^{n-1}b^{(t)}_j\zeta^j.
\]

After any cyclic cut \(s\), Abel summation rewrites the same magnitude in
terms of signed cyclic partial sums. This is an exact identity for arbitrary
coefficients. It explains which signed order can make an embedding coordinate
large; it does not give the probability of that event or a failure.

### Proposition 1: coherent ternary intervals

For \(e_j\in\{-1,0,1\}\), suppose an embedding-adapted interval of length
\(L\) has \(\ell\) nonzero entries, all of one sign. Its coherent contribution
has magnitude at least

\[
\ell\cos\!\left(\frac{(L-1)\pi}{2n}\right).
\]

The full embedding magnitude is at least this value minus the residual
magnitude outside the interval. The paper does not probabilistically bound
that residual. Constant-sign and alternating blocks are the \(t=1\) and
last-reduced-coordinate special cases.

### Theorem 4: norm density of one Gaussian product

For one product \(c=ab\), define

\[
g(x)=\frac{2}{n^2\sigma^4}
K_0\!\left(\frac{2\sqrt{x}}{n\sigma^2}\right).
\]

Then

\[
f_{\lVert\tau(c)\rVert}(r)
=nr\,g^{*(n/2)}\!\left(\frac{nr^2}{2}\right),\qquad r\ge0.
\]

This follows because the \(n/2\) reduced embedding coordinates are independent
products and Parseval transfers their squared magnitudes to the coefficient
norm. It is not the density of a sum of ML-KEM's noise terms.

## The norm-underestimation claim needs repair

Section 5.4 is not a numbered theorem. The displayed independence surrogate is

\[
f_{\rm assum}(r)=\frac{r}{2\sigma^2}
\exp\!\left(-\frac{r^2}{4\sigma^2}\right).
\]

Under the paper's earlier convention,

\[
\mathbb E|Z_1Z_2|^2=\sigma^4,
\]

whereas this Rayleigh law has

\[
\mathbb E R^2=4\sigma^2.
\]

An equal-second-moment complex Gaussian surrogate would instead have

\[
f_{\rm eq}(r)=\frac{2r}{\sigma^4}
\exp\!\left(-\frac{r^2}{\sigma^4}\right).
\]

The difference is material at the plotted \(\sigma=10\). A silent change in
the meaning of \(\sigma\) could repair the notation, but the paper does not
state one.

Even after equalizing scale, heavier far tails do not establish that one norm
stochastically dominates the other at every radius. The paper itself says the
radial densities cross. If an independence approximation preserves every
coefficient marginal, then

\[
\mathbb E\lVert c\rVert_2^2
=\sum_j\mathbb E[c_j^2]
\]

is identical with or without coefficient independence. A narrower claim—that
the independent Gaussian surrogate underestimates a specified far-tail
probability—may be true, but it needs a scale-correct threshold statement and
a finite-regime bound.

## What the experiments establish

The paper cleanly separates neither theorem evidence nor cryptographic
execution in its abstract, so the distinctions matter:

| Item | Evidence | What it shows | What it does not show |
|---|---|---|---|
| Figure 1 | synthetic 3D Gaussian samples; top 64 norms highlighted | visual axis thorns | cryptographic dimension or DFR |
| Figure 2 | analytic 2D product density | independent coordinates can have axis-directed joint tails | convolution attack |
| Figure 3 | 4,096 samples per violin; ternary \(1/4,1/2,1/4\); planted Type 1/1b segments; polynomial dimension not stated in Section 5.2/caption | longer planted patterns align products with \(P_1\) or \(P_{n/2}\) | CBD(2/3), \(n=256\) failure tails, compression, or key recovery |
| Figure 4 | plotted formulas at \(\sigma=10\) | claimed true/surrogate radial contrast | a scale-matched comparison or DFR |

The Figure 3 ternary law is CBD(1), not any FIPS 203 noise law. No decryption,
failure count, query count, target count, secret recovery, or standardized
parameter run is reported. No code or seeds are available.

## Decryption-failure attack interpretation

The paper maps Guo et al.'s LAC patterns as follows:

- Type 1/2 constant-sign blocks enlarge the first embedding coordinate.
- Type 1b/2b alternating blocks enlarge the last reduced coordinate.
- If both the secret and error polynomial are large in the same embedding
  coordinate, their product lies near the corresponding thorn plane.

The exact signed-permutation identities support that explanation. The broader
abstract language—existing attacks succeed “precisely” by forcing thorns—is
stronger than the formal result. The paper does not prove an if-and-only-if
failure theorem, bound the residual in the coherent-block proposition, or
show that every successful candidate is close to a thorn.

Its proposed extension is to search all embedding indices for simultaneous
large magnitudes instead of enumerating four hand-designed pattern families.
That is a candidate-selection principle. The paper gives no algorithm for
finding an unknown secret's large coordinate, no success advantage, and no
query/preprocessing/memory comparison. The overlapping-author ePrint 2026/802
already supplies a dependency-based proxy and claims improved LAC
failure-finding. The current paper should therefore be read primarily as a
geometric explanation, not as a new costed attack.

### Cited failure-attack lineage

The paper cites a broad failure literature, but formally specializes only the
LAC pattern attack:

- Guo–Johansson–Yang, LAC, ePrint 2019/1308: detailed Type 1/2 and
  Type 1b/2b reinterpretation.
- D'Anvers et al., PKC 2019, DOI
  `10.1007/978-3-030-17259-6_19`: general IND-CCA lattice failure attacks
  (duplicated as references 6 and 10 in the bibliography).
- D'Anvers–Rossi–Virdia, EUROCRYPT 2020, DOI
  `10.1007/978-3-030-45727-3_1`: bootstrapping the search for failures
  (duplicated as references 7 and 11).
- D'Anvers–Batsleer, ePrint 2021/193: multitarget failure boosting for Saber
  and Kyber.
- Guo–Johansson, ASIACRYPT 2020, DOI
  `10.1007/978-3-030-64837-4_12`: HQC; the current paper gives only a DFT
  analogy.
- Howgrave-Graham et al., CRYPTO 2003, DOI
  `10.1007/978-3-540-45146-4_14`: NTRU decryption-failure attacks.
- The FHE context is Li–Micciancio ePrint 2020/1533, Checri et al. ePrint
  2024/116, Cheon et al. ePrint 2024/127, and Liu–Wang–Fisch ePrint
  2025/1627.

Except for the LAC identities and the informal HQC analogy, the Thorns paper
does not rederive these works' failure probabilities, oracle assumptions, or
attack costs.

## Exact FIPS 203 transfer

FIPS fixes \(R_q=\mathbb Z_{3329}[x]/(x^{256}+1)\). Its parameters are:

| Set | \(k\) | \(\eta_1\) | \(\eta_2\) | \(d_u\) | \(d_v\) |
|---|---:|---:|---:|---:|---:|
| ML-KEM-512 | 2 | 3 | 2 | 10 | 4 |
| ML-KEM-768 | 3 | 2 | 2 | 10 | 4 |
| ML-KEM-1024 | 4 | 2 | 2 | 11 | 5 |

The secret \(s\), public-key error \(e\), and encryption randomness \(y\) have
coefficientwise CBD(\(\eta_1\)) laws. The ciphertext errors \(e_1,e_2\) have
CBD(\(\eta_2\)) laws.

For \(-\eta\le j\le\eta\),

\[
\Pr[\mathrm{CBD}_\eta=j]
=2^{-2\eta}\binom{2\eta}{\eta+j},
\qquad
\operatorname{Var}(\mathrm{CBD}_\eta)=\eta/2.
\]

Thus CBD(2) and CBD(3) have supports \([-2,2]\) and \([-3,3]\), respectively.
For a fixed output coordinate, negacyclic multiplication is

\[
(a*b)_\ell
=\sum_{i=0}^{\ell}a_i b_{\ell-i}
 -\sum_{i=\ell+1}^{n-1}a_i b_{n+\ell-i}.
\]

The scalar pairs in this one coordinate are independent when the two
coefficient arrays are independent; the joint dependence across output
coordinates comes from reusing those arrays.

Let

\[
\begin{aligned}
c_u&=\operatorname{Decompress}_{d_u}
       (\operatorname{Compress}_{d_u}(A^Ty+e_1))-(A^Ty+e_1),\\
c_v&=\operatorname{Decompress}_{d_v}
       (\operatorname{Compress}_{d_v}(t^Ty+e_2+\mu))-(t^Ty+e_2+\mu).
\end{aligned}
\]

Before the exact modular decoding step, the lifted cancellation gives

\[
\nu=e^Ty+e_2+c_v-s^Te_1-s^Tc_u.
\]

At embedding index \(t\), a necessary starting equation for any thorn
specialization is

\[
\rho_t(\nu)=
\sum_{j=1}^k\rho_t(e_j)\rho_t(y_j)
-\sum_{j=1}^k\rho_t(s_j)\rho_t(e_{1,j}+c_{u,j})
+\rho_t(e_2+c_v).
\]

This identity does not make the quantization errors independent. Also, the
complex canonical embedding used by the paper is not FIPS's finite-field NTT:
because \(3329\) has primitive 256th but no primitive 512th roots, the FIPS
NTT splits \(x^{256}+1\) into 128 quadratic factors rather than into the
paper's complex coordinates.

This differs from the paper's one-product model in six material ways.

1. **CBD, not Gaussian.** CBD(2) and CBD(3) are bounded and discrete, so they
   have no continuous exponential radial tail. For fixed \(n\), the event in
   the paper's \(R\to\infty\) limit eventually has probability zero. A central
   limit approximation describes a bulk limit as dimension grows; it does not
   import the paper's rare-tail LDP at fixed \(n=256\).
2. **Embedding dependence.** A unitary Fourier transform preserves covariance,
   but non-Gaussian Fourier coordinates are not independent merely because
   their covariance and pseudocovariance vanish.
3. **Multiple products.** \(e^Ty\) and \(s^Te_1\) already contain \(2k\)
   polynomial products. Theorem 4 covers one.
4. **Compression.** \(s^Tc_u\) adds \(k\) products with data-dependent
   quantization error. \(c_u\) shares \(y,e_1\) with other terms, while \(c_v\)
   depends on \(t=As+e\), \(y\), \(e_2\), and the message representative.
5. **Modular representatives.** The paper uses real number-field arithmetic.
   It does not analyze reduction modulo \(3329\), centered lifts, wraparound,
   or exact Compress\(_1\) boundary behavior.
6. **Failure functional.** ML-KEM decodes 256 individual bits. A failure occurs
   when at least one coefficient enters the wrong modular decision region.
   FIPS does not use a Euclidean-norm error-correcting decoder.

The paper's Gaussian theorem can plausibly motivate a new finite-\(n\)
importance sampler, but it is not itself a bound or approximation for this
\(\nu\).

With \(\mu=\operatorname{Decompress}_1(m)\), the exact event that must be
specialized is

\[
\mathcal F=
\left\{\exists\ell:
\operatorname{Compress}_1((\mu+\nu)_\ell\bmod q)\ne m_\ell
\right\}.
\]

The usual \(q/4\) expression is a decision-boundary shorthand used by the
estimator, not a Euclidean-norm criterion.

## Why the listed FIPS DFP values do not change

FIPS 203 lists:

- ML-KEM-512: \(2^{-138.8}\);
- ML-KEM-768: \(2^{-164.8}\);
- ML-KEM-1024: \(2^{-174.8}\).

The pinned `Kyber_failure.py` constructs a one-coefficient error law from
centered-binomial product laws, scalar convolutions, and compression-error
laws. It then returns

```text
n * tail_probability(F, q/4)
```

This last step is a union bound:

\[
\Pr[\max_j|\nu_j|\ge T]
\le \sum_{j=0}^{255}\Pr[|\nu_j|\ge T].
\]

It does not assume that the 256 output coefficients are independent.
Convolution-induced correlation can change the slack of this bound, but cannot
invalidate the inequality. This is especially important because the Thorns
paper primarily challenges the joint directional law and Euclidean norm.

The estimator still has assumptions worth auditing: its one-coordinate law
combines scalar inputs and uniform compression-error laws as independent.
ePrint 2022/212 also studies concrete-key dependence and reports a wide
distribution of conditional failure rates. But ePrint 2026/1022 does not model
the exact FIPS compression variables, produce a larger one-coordinate tail, or
show that the estimator's marginal is optimistic. It therefore gives no basis
for revising FIPS Table 1.

The algorithms and approved parameter sets are normative. Table 1 is a listed
DFP calculation under the standard's random-function heuristic and cited
scripts; this preprint neither amends the standard nor supplies a replacement
calculation. Any numerical revision would have to derive or bound the exact
one-coordinate law with shared compression variables, preserve modular
decoding, and then control the 256-coordinate union.

## Five separate implication verdicts

| Question | Verdict | Scope |
|---|---|---|
| (a) Honest DFR estimation | No numerical or normative change | The paper warns about Gaussian joint tails, but does not alter the exact CBD one-coordinate law, invalidate the union bound, or specialize compression/module sums/modular decoding. The \(2^{-138.8},2^{-164.8},2^{-174.8}\) claims stay unchanged. |
| (b) Failure-boosting geometry | Conceptual generalization only | The score \(|\sigma_t(s)|\,|\sigma_t(e)|\) unifies known LAC patterns and suggests searching all frequencies. There is no ML-KEM target/query/precomputation model or boosted probability. BATCH-002 ORS-002 is unchanged. |
| (c) Conditional DF-oracle attacks | No query or end-to-end cost change | No visible DF bit is created, and thorn distance is not mapped to the accuracy law consumed by LDPC, inequality, or soft-oracle backends. The conditional 2,400/2,950-query figures and separate oracle-construction costs do not change. |
| (d) Passive MLWE hardness | No change | There is no public-key-only distinguisher, key recovery, lattice-cost reduction, standardized solve, or certificate. |
| (e) Protocol/implementation guidance | Analysis guidance only | Audit exact rare-event laws and keep failure channels separately charged. Do not alter standardized sampling, parameters, or compression, and do not add trimming/rejection without a new specification and proof. Preserve exact integer compression, full re-encryption comparison, implicit rejection, internal-interface restrictions, and implementation-specific leakage/fault testing. |

This preserves the BATCH-002 boundary: an honest failure probability is not a
public failure bit. Even a correct conditional booster would still need an
oracle construction, target pool, adaptive queries, protocol confirmation,
and postprocessing charged separately.

## Claim-by-claim assessment

- **Product-Gaussian exponential radial tails:** proved in the stated model.
- **Axis concentration under a large norm:** proved asymptotically for fixed
  dimension and continuous iid embedding coordinates.
- **Axes map to fixed coefficient-space planes:** proved for the
  power-of-two Gaussian model.
- **Discrete CBD transfer:** not proved; the paper supplies only planted
  CBD(1)-like experiments.
- **Exact LAC patterns align with thorns:** supported by deterministic
  identities and finite experiments.
- **Every successful failure attack is precisely a thorn attack:** not proved
  as an if-and-only-if statement.
- **Theorem 4 is a decryption-noise law:** false for ML-KEM; it is a one-product
  Gaussian law.
- **Independence universally underestimates norm:** overstated and affected by
  the displayed variance mismatch.
- **Passive or standardized ML-KEM attack:** absent.
- **Quantified conditional-boosting improvement:** absent.

## Novelty position

Exact-title and mechanism searches found no duplicate in `knowledge/`,
`ledger/hypotheses/`, or `ledger/proposals/`. The broader topic is established:
D'Anvers et al. studied coefficient dependencies; Guo et al. exploited LAC
failure patterns; Fang–Wang–Zhao analyzed concrete-key Kyber DFP; and the
overlapping-author ePrint 2026/802 gives a norm decomposition, attack proxy,
and trimming framework.

The honest classification is `adaptation`: the paper adds a
canonical-embedding LDP and Fourier-plane interpretation to a known
correlation/DFR mechanism. This review does not claim exhaustive novelty.

## Cheapest gate

Test `GATE-THORNS-FIPS-001` first: an equal-scale and FIPS-estimator derivation
audit.

1. Integrate the two displayed radial laws, check normalization and second
   moments, and repeat the comparison with an equal-variance Gaussian
   surrogate.
2. Derive \(\nu\) directly from FIPS Algorithms 13–15, recording every shared
   variable, compression error, representative, and decision boundary.
3. Reconstruct the pinned script's one-coordinate law and distinguish the
   valid \(np\) union bound from the independence formula
   \(1-(1-p)^n\).
4. As the only implementation step, exactly enumerate a toy \(n=8\)
   no-compression CBD control and a compressed variant. Stop unless compression
   creates a one-coordinate discrepancy rather than only a joint-distribution
   difference.

The controls are a Gaussian one-product case reproducing Theorem 4, an exact
no-compression CBD dynamic program, modular/rounding normalization checks, and
the deliberately wrong independence formula. Required metrics are density
integrals, radial second moments, one-coordinate tail probability, exact
any-coordinate failure probability, union-bound slack, and a term-dependency
graph.

There are three discriminating outcomes:

- **Joint geometry only:** marginals match and only joint dependence changes.
  The paper remains a mechanism; FIPS's union bound survives.
- **Exact FIPS marginal gap:** compression/shared-variable dependence changes
  the one-coordinate tail. Freeze a bounded \(n=256\) importance-sampling
  protocol next.
- **Paper scale artifact:** the reported norm contrast materially changes
  after equalizing variance. Figure 4 cannot support extrapolation.

This gate costs roughly 4–8 analyst hours, under 1 GB memory, and negligible
compute. It ranks above \(n=256\) Monte Carlo because directly observing a
\(2^{-138.8}\) or smaller event is infeasible and uninterpretable before the
scale and estimator identities are settled.

## Sources

- Cai, Liu, Wang, Lu, ePrint 2026/1022, current PDF update
  `20260719:093516`, revised 2026-07-19,
  <https://eprint.iacr.org/2026/1022/20260719:093516>.
- NIST, FIPS 203, published 2024-08-13,
  <https://doi.org/10.6028/NIST.FIPS.203>.
- `pq-crystals/security-estimates`, commit
  `75c26949a902ca297b181375bfb7cfaf22cce784`,
  <https://github.com/pq-crystals/security-estimates/tree/75c26949a902ca297b181375bfb7cfaf22cce784>.
- CRYSTALS-Kyber round-three specification,
  <https://pq-crystals.org/kyber/data/kyber-specification-round3.pdf>.
- Liu et al., ePrint 2026/802, *A Primer on Dependency in Polynomial Product*,
  <https://eprint.iacr.org/2026/802>.
- Fang, Wang, Zhao, ePrint 2022/212, *Tight Analysis of Decrypton Failure
  Probability of Kyber in Reality*, <https://eprint.iacr.org/2022/212>.
- D'Anvers and Batsleer, ePrint 2021/193, multitarget failure boosting,
  <https://eprint.iacr.org/2021/193>.
- BATCH-002 oracle/cost reports and independent Reviewer/Red-Team reports
  listed in `thorns_report.yaml`.

All URLs above were accessed 2026-07-23. All no-attack, no-code, and
no-revision-change statements are restricted to the checked sources and that
access date. A failed download or unavailable artifact is not mathematical
evidence.
