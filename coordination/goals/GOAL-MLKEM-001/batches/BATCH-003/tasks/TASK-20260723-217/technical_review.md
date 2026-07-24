# Independent technical review — TASK-20260723-217

Role: independent Reviewer; no official state change.  
Inference: `review-xhigh` requested; `gpt-5.6-sol-xhigh` resolved at
`xhigh`; no fallback; adapter `cursor-subagent-2026-07`.

## Outcome

The BATCH-003 bottom line is supported, with two important qualifications:

1. ePrint 2026/1022 has both a genuine Gaussian-surrogate scale error and a
   real local gap in Theorem 1's printed proof. The proof gap has a simple
   fixed-shift repair; the scale error does not. Neither issue yields an exact
   ML-KEM failure calculation.
2. The proposed R07 bridge for ePrint 2026/1465 is a coherent research control
   only after its joint radial-angular equations are frozen. A scalar
   replacement of the sphere reduction probability is not coherent.

Neither paper changes a FIPS 203 decapsulation-failure rate, passive MLWE
hardness, a conditional failure-oracle cost, or any BATCH-002 cost row. The
69-paper screen contains no material false inclusion or exclusion. The papers
motivate bounded controls only.

## Immutable snapshot and source versions

The six producer files were reviewed from snapshot commit
`7393bb5b2ca09bbc1b55edcccea1ff313d52a668`. Its parent is the receipt's
declared `3076dbe0335c4eb7e4fe8a370ca7010438d43c25`. The commit changes exactly
the six producer files and `TASK-20260723-216/snapshot-receipt.json`; all six
producer SHA-256 values match the receipt. The receipt leaves its own
`commit_sha` null to avoid self-reference, while the dispatch queue binds it to
`7393bb5`.

The current primary versions checked on 2026-07-23 are:

* Cai–Liu–Wang–Lu, ePrint
  [2026/1022](https://eprint.iacr.org/2026/1022), current PDF update
  `20260719:093516` from 2026-07-19. The complete extracted text hash is
  `fcd895e7e19e1ea7dcf2eb38527aa2f62b2d26d450c3ac4eeca6b9a48c13e655`.
* Stevens–Yonli, ePrint
  [2026/1465](https://eprint.iacr.org/2026/1465), sole PDF update
  `20260717:191956`; the record was approved on 2026-07-21 and has no later PDF
  revision. The complete extracted text hash is
  `f9dc5d99bd93bdaafb6eb8369e94ecac6d3383a2cfa63ae22008fd9bf481fdeb`.

These are parser-text hashes, not binary-PDF hashes.

## 1. ePrint 2026/1022

### Model actually proved

The paper's main theorem concerns one product \(c=ab\) in
\(\mathbb R[x]/(x^n+1)\), with \(n\) a power of two and

\[
\tau(a),\tau(b)\stackrel{\mathrm{iid}}{\sim}N(0,\sigma^2I_n).
\]

The reduced embeddings are independent
\(\mathcal{CN}(0,n\sigma^2)\) coordinates, so multiplication becomes
coordinatewise products. This Gaussian independence does not transfer from
zero covariance alone to transformed CBD inputs.

For \(Z_1,Z_2\stackrel{\mathrm{iid}}{\sim}\mathcal{CN}(0,\sigma^2)\), the
product \(W=Z_1Z_2\) has radial density

\[
f_{\rm real}(r)=\frac{4r}{\sigma^4}
K_0\!\left(\frac{2r}{\sigma^2}\right),\qquad r\ge0.
\]

Its exponential radial tail drives the fixed-dimension, \(R\to\infty\)
concentration on complex axes. The inverse reduced embedding maps those axes
to the paper's \(n/2\) real Fourier planes. This is a valid and useful
Gaussian-model mechanism, not a fixed-\(n\) CBD theorem.

### The Gaussian-surrogate mismatch is real

The paper defines \(\mathcal{CN}(0,\sigma^2)\) so that
\(\mathbb E|Z|^2=\sigma^2\). Therefore

\[
\mathbb E|Z_1Z_2|^2=\sigma^4.
\]

Section 5.4 instead displays

\[
f_{\rm assum}(r)=\frac{r}{2\sigma^2}
\exp\!\left(-\frac{r^2}{4\sigma^2}\right),
\]

whose second moment is \(4\sigma^2\). The claimed equal-standard-deviation
comparison is thus false under the paper's own notation. At the plotted
\(\sigma=10\), the surrogate-to-product second-moment ratio is \(0.04\).

The equal-second-moment circular-Gaussian radial law would be

\[
f_{\rm eq}(r)=\frac{2r}{\sigma^4}
\exp\!\left(-\frac{r^2}{\sigma^4}\right).
\]

This correction is not cosmetic: Figure 4 compares scales differing by a
factor \(25\) in second moment. It also does not rescue the broad claim that
independence “systematically” underestimates the norm. At equal scale, the
densities cross. If a coefficientwise surrogate preserves every marginal
second moment, then

\[
\mathbb E\|c\|_2^2=\sum_j\mathbb E[c_j^2]
\]

is unchanged by discarding joint dependence. A specified far-tail inequality
may hold, but neither density crossing nor a heavier asymptotic tail proves
first-order stochastic dominance of the norm.

The producer's variance objection is therefore confirmed.

### Theorem 1 has a local, repairable proof gap

The paper claims an LDP for the conditional direction of
\(Z=(X_1,\ldots,X_n)\), with speed \(R\) and

\[
I(u)=c(\|u\|_1-1),\qquad \|u\|_2=1.
\]

The upper bound and denominator exponent are sound under the stated
pointwise exponential-tail assumption. The lower-bound proof is not literally
correct: the fixed-radius polydisc

\[
Q_R=\prod_j\{z_j:|z_j-Ru_j|\le\varepsilon\}
\]

contains inward perturbations and is not contained in
\(\{\|z\|_2>R\}\).

The repair proposed by `TASK-20260723-213` works. Center the same polydisc at
\((R+C)u\), with \(C>\sqrt n\,\varepsilon\). Then

\[
\|z\|_2\ge R+C-\sqrt n\,\varepsilon>R,
\]

the direction still converges uniformly to \(u\), and

\[
\|z\|_1\le R\|u\|_1+O(1).
\]

After approximating the target direction by one with no zero coordinates, the
density lower bound applies on every coordinate. The \(O(1)\) shift vanishes at
speed \(R\). Thus the theorem is plausibly valid after a short written repair,
but “proved as printed” would be inaccurate.

### Exact FIPS 203 transfer fails

FIPS 203 uses coefficientwise centered binomials

\[
\Pr[\mathrm{CBD}_\eta=j]
=2^{-2\eta}\binom{2\eta}{\eta+j},\qquad
\operatorname{Var}(\mathrm{CBD}_\eta)=\eta/2,
\]

with bounded support \([-\eta,\eta]\), \(n=256\), and \(q=3329\). It also uses
multiple module products, compression, modular representatives, and
coefficientwise bit decoding. None is in the theorem above.

Let

\[
\begin{aligned}
u_0&=A^Ty+e_1,\\
v_0&=t^Ty+e_2+\mu,\\
c_u&=\operatorname{Decompress}_{d_u}
       (\operatorname{Compress}_{d_u}(u_0))-u_0,\\
c_v&=\operatorname{Decompress}_{d_v}
       (\operatorname{Compress}_{d_v}(v_0))-v_0,
\end{aligned}
\]

where \(\mu=\operatorname{Decompress}_1(\operatorname{ByteDecode}_1(m))\).
Using \(t=As+e\), the lifted pre-decoding noise is exactly

\[
\nu=e^Ty+e_2+c_v-s^Te_1-s^Tc_u.
\]

The exact message error event is

\[
\mathcal F=
\{\exists\ell:
\operatorname{Compress}_1((\mu+\nu)_\ell\bmod q)\ne m_\ell\}.
\]

This identity exposes the transfer failure:

* \(e^Ty\) and \(s^Te_1\) already contain \(2k\) products, not one.
* \(c_u\) and \(c_v\) are data-dependent quantization errors sharing variables
  with the product terms.
* The decoder uses modular representatives and 256 coefficient decisions, not
  a real Euclidean-norm threshold.
* A fixed-\(n\), unbounded continuous-tail theorem cannot be imported through a
  bulk CLT into bounded CBD rare tails.

The paper therefore supplies no replacement FIPS marginal or end-to-end
failure probability.

### The final \(n\)-fold step is a union bound

At the FIPS-cited `pq-crystals/security-estimates` revision
`75c26949a902ca297b181375bfb7cfaf22cce784`,
`Kyber_failure.py` constructs one scalar error law and returns

```text
n * tail_probability(F, q/4)
```

This is

\[
\Pr\!\left[\bigcup_{\ell=0}^{n-1}\mathcal F_\ell\right]
\le \sum_{\ell=0}^{n-1}\Pr[\mathcal F_\ell]=np.
\]

It does not require independence among output coefficients. The formula
\(1-(1-p)^n\), which would require independence, is not used. Joint thorn
geometry can change union-bound slack but cannot invalidate the inequality.

The script's scalar law still models modulus-switching errors as independent
uniform variables. That assumption deserves an exact audit, but 2026/1022
does not identify a wrong scalar marginal or derive a larger one. Consequently,
the FIPS-listed \(2^{-138.8}\), \(2^{-164.8}\), and \(2^{-174.8}\) values are
not revised by this paper.

### Attack scope

The signed-permutation and coherent-interval identities do explain why known
LAC constant-sign and alternating patterns enlarge selected embedding
coordinates. They do not prove the abstract's stronger “precisely” language as
an if-and-only-if end-to-end attack theorem. No ML-KEM failure bit, passive
public-key distinguisher, key recovery, query reduction, target reduction, or
attack certificate is supplied.

## 2. ePrint 2026/1465

### Sign-matched probability ratios

Write

\[
A_n=I_{3/4}\!\left(\frac{n+1}{2},\frac12\right),\qquad
B_n=I_{3/4}\!\left(\frac{n-1}{2},\frac12\right).
\]

The fixed-sign and optimized-sign sphere probabilities are \(B_n/2\) and
\(B_n\), respectively. At threshold one, the exact uniform-ball probabilities
are

\[
\Pr[G-]=\frac32A_n,\quad
\Pr[G\pm]=3A_n-2^{-n},\quad
\Pr[L-]=A_n,\quad
\Pr[L\pm]=2A_n.
\]

The proper sign-matched ratios are therefore

\[
\frac{3A_n}{B_n},\quad
\frac{3A_n-2^{-n}}{B_n},\quad
\frac{2A_n}{B_n},\quad
\frac{2A_n}{B_n}.
\]

Their uniform-ball limits are \(2.25,2.25,1.5,1.5\). For the global
\(\operatorname{Exp}(2/3)\) input law, the optimized-sign matched ratio is
\(4\), not \(8\). The larger \(4.5,3,\) and \(8\) factors compare an
optimized-sign numerator with a fixed-sign sphere denominator.

The producer's exact and asymptotic ratio accounting is correct.

### `min` versus `max`

The paper defines local reduction by

\[
D(x,y)\le\max(\|x\|,\|y\|),
\]

and Sections 2, 3.4, 3.5, and Lemma 3 consistently use this rule. Lemma 1 alone
prints `min`. The constants identify this as a definite typo, not an alternate
rule.

For uniform-ball scaled depths \(W_x,W_y\sim\operatorname{Exp}(1)\),
\(|W_x-W_y|\sim\operatorname{Exp}(1)\). The max rule perturbs the sphere cap by
\(\exp(|W_x-W_y|/3)\), giving

\[
\mathbb E[e^{|W_x-W_y|/3}]=\frac32.
\]

The literal min rule instead gives

\[
\mathbb E[e^{-|W_x-W_y|/3}]=\frac34.
\]

Thus the paper's local \(1.5\) and \(3\) factors belong to `max`; they must not
be quoted for `min`.

### Constant, not exponent

All of the paper's admissible fixed-law asymptotics preserve

\[
p_n=\frac{(3/4)^{n/2}}{\sqrt{3\pi n/8}}.
\]

The exponential list coefficient remains

\[
\frac12\log_2(4/3)=0.20751874963942185.
\]

The \(n^{-1/2}\) factor also remains. The paper changes a pair-probability
constant inside its iid isotropic model; it does not derive an operational list
size, a number of sieve rounds, filter costs, routing, BKZ behavior, or an
outer ML-KEM optimizer. Subtracting \(\log_2(1.5)\), \(\log_2(4)\), or
\(\log_2(8)\) from a security estimate is invalid.

No classical or quantum sieve exponent and no BATCH-002 row changes.

### Is R07 a coherent next bridge?

Yes, but only as a new, same-model sensitivity control with a symbolic stage
before implementation. The pinned R07 source
`d197843ddb406102ba101f426ea5a59e8a8a306f` exposes:

* the sphere reduction cap \(C_0=C(d,\pi/3)\);
* list size and expected reducing pairs;
* directional cap and wedge probabilities;
* conditional reduction, popcount false negatives, and recursive hits;
* bucket memory, sorting/routing, and optimizer choices.

That makes R07 inspectable, but it also shows why replacing only \(C_0\) is
wrong. Under an isotropic ball law, a direction-only cap probability
\(C(d,\theta)\) is unchanged. What changes is the reduction event, because its
angle threshold depends on both radii. The current product
`W0 * C0` must therefore become one joint integral for “the pair reduces and
shares a bucket.” The same law must be used for `ngr`, `eta`, pair supply, and
recursive hits. After cap conditioning and projection, a recursive subproblem
does not automatically retain the original uniform-ball radial law.

A valid first stage is therefore:

1. freeze these joint radial-angular kernels and their sphere limits;
2. prove which direction-only terms remain unchanged;
3. reproduce the original sphere result at \(d=375\);
4. apply the exact uniform-ball **local** rule consistently;
5. propagate lists, buckets, recursion, sorting, routing, and reoptimization.

The global \(\operatorname{Exp}(2/3)\) output theorem is not a local
steady-state theorem and should not be inserted into R07. Even a passing
\(d=375\) treatment would update only the pinned R07 sensitivity model, not
`C0`, `CC`, `CN`, `QN`, `Q0`, `GE19`, QRS, or a physical model.

## 3. The 69-paper triage

All 69 supplied identifiers occur in the current primary ePrint eight-day
listing, and their titles and abstracts were screened independently. The
producer's partition is coherent:

* 2 claim-changing *candidates*: 2026/1022 and 2026/1465;
* 6 adjacent methods: 2026/026, 2026/1462, 2026/1467, 2026/1468,
  2026/1448, and already-covered 2026/155;
* 1 pedagogical item: 2026/1098;
* 60 irrelevant to the scoped ML-KEM map.

No third supplied paper contains an ML-KEM passive solver, exact FIPS DFR
revision, matched lattice-cost rerun, or directly transferred implementation
attack. The adjacent papers remain methods or lessons without an instantiated
ML-KEM backend. Treating 2026/155 as adjacent/already covered is appropriate:
it gives MLWE/IP-M-EDCP reductions but no efficient solver.

There is one metadata wording issue, not a relevance error. For newly approved
ePrint records, the approval date is a history event and can be later than the
frozen PDF timestamp. Calling every approval date a “current revision” is
imprecise. The 2026/1465 producer report correctly distinguishes its
2026-07-21 approval from PDF update `20260717:191956`.

No material false inclusion or exclusion was found.

## 4. Research-map consequence

| Scoped quantity | Review verdict |
|---|---|
| FIPS 203 DFR | unchanged |
| Passive MLWE hardness | unchanged |
| Conditional DF-oracle cost | unchanged |
| BATCH-002 cost rows | unchanged |
| Standardized passive solve | none |
| 2026/1022 value | Gaussian joint-tail mechanism plus bounded exact-transfer control |
| 2026/1465 value | iid isotropic pair-probability constants plus bounded estimator-sensitivity control |

The two justified next controls are:

1. an equal-scale radial-law check plus exact FIPS one-coordinate,
   compression, and union-bound audit for 2026/1022; and
2. a frozen joint radial-angular kernel derivation followed, only if it passes,
   by a sphere-controlled R07 local-ball sensitivity replay for 2026/1465.

Toy enumeration cannot revise the \(n=256\) FIPS values, and a same-R07
sensitivity result cannot be transferred to another cost model. This review
records no experiment, solve, or official state transition.

## Primary references

* Cai, Liu, Wang, Lu, ePrint
  [2026/1022](https://eprint.iacr.org/2026/1022), current PDF update
  `20260719:093516`.
* Stevens, Yonli, ePrint
  [2026/1465](https://eprint.iacr.org/2026/1465), current PDF update
  `20260717:191956`.
* NIST, [FIPS 203](https://doi.org/10.6028/NIST.FIPS.203).
* `pq-crystals/security-estimates`,
  revision `75c26949a902ca297b181375bfb7cfaf22cce784`.
* `sam-jaques/sieve-memory-estimates`,
  revision `d197843ddb406102ba101f426ea5a59e8a8a306f`.
* BATCH-002 `TASK-20260722-206` model-separated cost baseline.
