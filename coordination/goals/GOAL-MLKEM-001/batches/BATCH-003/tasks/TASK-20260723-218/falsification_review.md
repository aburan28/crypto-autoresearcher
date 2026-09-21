# BATCH-003 independent falsification review

Task `TASK-20260723-218` · Red Team · source cutoff and review date
2026-07-23 · no official state change

Inference: requested policy `review-xhigh`; resolved model
`gpt-5.6-sol-xhigh`; reasoning effort `xhigh`; fallback `false`; adapter
`cursor-subagent-2026-07`.

## Review basis

The only producer evidence reviewed is the six-artifact snapshot at commit
`7393bb5b2ca09bbc1b55edcccea1ff313d52a668`, parent
`3076dbe0335c4eb7e4fe8a370ca7010438d43c25`. Git shows that the commit is
reachable and changes exactly the six producer artifacts plus
`TASK-20260723-216/snapshot-receipt.json`. Every producer file matches the
receipt's SHA-256 value.

The primary sources independently inspected include the current PDFs and
records for ePrint 2026/1022 and 2026/1465, FIPS 203, the pinned Kyber failure
scripts, the pinned R07 source, the closest DFR/failure-attack papers, every
nonirrelevant triage record, and a risk-based sample of lattice/LWE/KEM
exclusions.

## Decision

No new paper currently changes an ML-KEM security conclusion.

* ePrint 2026/1022 supplies a useful Gaussian one-product geometry. It does not
  supply an exact FIPS marginal, an ML-KEM failure probability, an observable
  failure oracle, or an end-to-end attack.
* ePrint 2026/1465 supplies exact pair probabilities in iid isotropic models.
  It does not supply a practical-list distribution, a changed sieve exponent,
  or a complete attack-cost bridge.
* The 69-paper classification is useful lead triage. The defensible negative
  statement is only “no third lead identified at triage depth,” not “60 papers
  proved irrelevant.”

The narrowed Thorns audit is cheaper and more claim-relevant than the proposed
R07 rewrite. It should run first.

## Source-error taxonomy

| Issue | Classification | Consequence |
|---|---|---|
| Thorns Theorem 1 polydisc at \(Ru\) | Genuine local proof flaw; apparently repairable | Printed proof is incomplete; theorem is not falsified |
| Thorns Section 5.4 use of \(\sigma\) | Mathematical normalization inconsistency, unless an unstated notation change exists | Figure 4 and universal norm-underestimation language cannot be used quantitatively |
| Sieve Lemma 1 `min` | Genuine source notation error, independently reproduced; not a parser artifact | The printed local event is wrong, while the `max`-rule formulas and proofs survive |
| Sieve non-uniform asymptotic | Missing uniform-integrability/tail argument | Pointwise kernel limit is not by itself a complete proof under the unbounded integral |
| Producer's “exact lifted” ML-KEM identity | Potential agent overclaim | Exact modulo \(q\); an integer lift needs representatives and wrap terms |

No material objection below is inferred merely from damaged PDF extraction.

## 1. ePrint 2026/1022: theorem reconstruction

### 1.1 What survives

The paper's complex product density is consistent with its declared
\(\mathcal{CN}(0,\sigma^2)\) convention:

\[
f_W(z)=\frac{2}{\pi\sigma^4}K_0\!\left(\frac{2|z|}{\sigma^2}\right),
\qquad
f_{|W|}(r)=\frac{4r}{\sigma^4}K_0\!\left(\frac{2r}{\sigma^2}\right).
\]

Theorem 1's intended rate

\[
I(u)=c(\lVert u\rVert_1-1)
\]

is credible for fixed dimension and \(R\to\infty\). The upper bound and
denominator exponential rate are structurally sound. Lemma 1's Gaussian
Fourier-coordinate independence is also sound: for a jointly Gaussian vector,
the vanishing covariance and pseudocovariance establish independent circular
coordinates. Theorem 2 then maps complex axes to real Fourier planes through
the scaled unitary inverse embedding. Theorem 4's change of variables for one
Gaussian product is dimensionally consistent.

These results remain restricted to one continuous Gaussian product. Zero
covariance does not give independent Fourier coordinates for CBD inputs.

### 1.2 Theorem 1's printed lower bound is not valid as written

The proof takes

\[
Q_R=\prod_j\{z_j:|z_j-Ru_j|\le\varepsilon\}
\]

and claims \(Q_R\subset\{\lVert z\rVert_2>R\}\) for large \(R\). An inward
perturbation contradicts that containment. This is a genuine proof defect.

A fixed shift appears sufficient:

\[
\widetilde Q_R=
\prod_j\{z_j:|z_j-(R+C)u_j|\le\varepsilon\},
\]

with \(C\) larger than the maximum possible inward norm loss. Its direction
still converges to \(u\), and
\(\lVert z\rVert_1=(R+C)\lVert u\rVert_1+O(1)\), so the speed-\(R\) exponent
is unchanged. This repair must be written and independently checked; it should
not be silently attributed to the paper.

### 1.3 The attack interpretation is only one-way

The signed-permutation/partial-sum identity is exact. It explains why the
constant-sign and alternating LAC blocks amplify selected embeddings. The
coherent-interval bound, however, subtracts an unbounded residual, and a large
Fourier coefficient need not imply one unique contiguous pattern. The paper
does not prove:

* an if-and-only-if characterization of successful failure ciphertexts;
* that all successful samples are close to a thorn in the required metric;
* a method to find the useful coordinate of an unknown ML-KEM secret;
* a changed candidate rate, query count, target count, or recovery cost.

The narrow result is geometric explanation and candidate scoring for the
paper's model, not a recovered key.

## 2. The Section 5.4 normalization defect

The displayed “real” product amplitude satisfies

\[
\mathbb E R_{\rm real}^2=\sigma^4.
\]

The displayed independent Gaussian amplitude

\[
f_{\rm assum}(r)=\frac{r}{2\sigma^2}
e^{-r^2/(4\sigma^2)}
\]

satisfies

\[
\mathbb E R_{\rm assum}^2=4\sigma^2.
\]

Their ratio is \(4/\sigma^2\), so at the plotted \(\sigma=10\) the surrogate
has only \(1/25\) of the second moment. The equal-second-moment circular
Gaussian amplitude is instead

\[
f_{\rm eq}(r)=\frac{2r}{\sigma^4}e^{-r^2/\sigma^4}.
\]

The source explicitly defines \(\mathcal{CN}(0,\sigma^2)\) and does not state a
new convention in Section 5.4. The best charitable alternative is an unstated
notation change; absent that clarification, the printed comparison is
mathematically inconsistent. This does not invalidate Theorem 4, but it is
fatal to using Figure 4 as quantitative evidence.

Even after matching moments, two density crossings do not prove first-order
stochastic dominance, and heavier asymptotic tails do not prove
“systematic” norm underestimation at every threshold. A valid replacement
claim must name a threshold regime and compare equal-scale tail probabilities.

## 3. FIPS 203 transfer and DFR

### 3.1 The producer's cancellation identity needs a modulo-\(q\) qualifier

With compression errors \(c_u,c_v\), cancellation gives

\[
\nu\equiv e^Ty+e_2+c_v-s^Te_1-s^Tc_u\pmod q.
\]

That is exact in \(R_q\). It is not automatically an equality between chosen
integer representatives. A rigorous tail derivation must first freeze
centered lifts and include any \(q\)-multiple wrap variables. Otherwise a
representative change can masquerade as a tail change.

### 3.2 The union-bound step survives convolutional dependence

The pinned `Kyber_failure.py` computes a one-coordinate law and returns

\[
n\,p_{\rm tail}.
\]

This is a union bound. It does not use independence among the 256 output
coefficients. Convolutional dependence can change its slack and the exact
probability that any coefficient fails, but cannot invalidate
\[
\Pr\!\left[\bigcup_\ell F_\ell\right]\le\sum_\ell\Pr[F_\ell].
\]

For one no-compression product coordinate, negacyclic convolution pairs each
coefficient of one independent input with one coefficient of the other. Those
scalar products are independent within that fixed coordinate. The Thorns
joint-direction theorem therefore gives no new one-coordinate law.

### 3.3 The real open marginal is compression, not thorns

The pinned script models modulus-switching errors by a uniform error law and
combines terms independently. Exact FIPS compression errors are
data-dependent and share \(A,s,e,y,e_1,e_2\) with the cancellation terms.
The script's `round` behavior also needs to be checked against FIPS's exact
rational tie convention. These are legitimate audit targets, but ePrint
2026/1022 neither models them nor proves that their one-coordinate tail is
optimistic.

FIPS 203 lists \(2^{-138.8}\), \(2^{-164.8}\), and \(2^{-174.8}\) under its
random-function heuristic and cites the scripts. This review does not upgrade
those listed rates to exact rigorous bounds, and it finds no basis in the
Thorns paper for changing them.

### 3.4 No end-to-end failure attack

The missing path includes:

1. an externally observable bit or calibrated leakage surface;
2. valid chosen-ciphertext construction under complete re-encryption;
3. acquisition of targets with a useful secret embedding coordinate;
4. conditional failure probability and target-pool size;
5. adaptive query count and protocol confirmation;
6. rank or uniqueness of the recovered constraints;
7. preprocessing and memory;
8. full source recovery and key validation.

Guo–Johansson–Yang gives the closer costed LAC pattern attack.
D'Anvers–Batsleer gives the closer costed Kyber multitarget failure-boosting
baseline. The new paper improves no charged term in either path.

## 4. ePrint 2026/1465: probability ratios

### 4.1 Exact uniform-ball results survive for the `max` local rule

Let
\[
A_n=I_{3/4}((n+1)/2,1/2),\qquad
B_n=I_{3/4}((n-1)/2,1/2).
\]

The exact sphere probabilities are \(B_n/2\) for fixed sign and \(B_n\) for
optimized sign. The uniform-ball threshold-one probabilities are:

| Case | Probability | Matched-sign ratio |
|---|---:|---:|
| global, fixed | \(3A_n/2\) | \(3A_n/B_n\to2.25\) |
| global, optimized | \(3A_n-2^{-n}\) | \((3A_n-2^{-n})/B_n\to2.25\) |
| local, fixed | \(A_n\) | \(2A_n/B_n\to1.5\) |
| local, optimized | \(2A_n\) | \(2A_n/B_n\to1.5\) |

The factors \(4.5\), \(3\), and \(8\) in headline comparisons include an
unmatched factor two from sign optimization. The stable global distribution's
matched ratio is four, not eight.

Every stated fixed-law asymptotic retains
\[
p_n=\frac{(3/4)^{n/2}}{\sqrt{3\pi n/8}}.
\]
The exponential coefficient remains
\(\tfrac12\log_2(4/3)=0.2075187496\). No classical or quantum sieve exponent
changes.

### 4.2 `min` is a genuine source typo

The PDF's introductory Lemma 1 prints
\[
D(X,Y)\le\min(\lVert X\rVert,\lVert Y\rVert)
\]
for the local cases. The paper's local-rule definition, Section 2 CDF,
Lemma 3, and Sections 3.4–3.5 all use `max`. Independent search extraction also
returns `min` in Lemma 1, excluding the proposed parser-artifact explanation.

The constants diagnose the same error. With iid
\(W_X,W_Y\sim\mathrm{Exp}(1)\), the `max` rule contributes
\[
\mathbb E e^{|W_X-W_Y|/3}=3/2,
\]
whereas the printed `min` rule contributes
\[
\mathbb E e^{-|W_X-W_Y|/3}=3/4.
\]
Thus the paper's \(1.5,3\) constants belong to `max`; the literal `min`
statement would give \(0.75,1.5\) against fixed-sign \(p_n\).

### 4.3 The non-uniform global limit needs a rigor control

The source expands the scaled-depth kernel pointwise for fixed
\((w_x,w_y,w_z)\), obtains a factor
\[
e^{w_x/3}e^{w_y/3}e^{-2w_z/3},
\]
and places that limit under an integral over \([0,\infty)^2\). It states the
moment condition
\[
M_f=\int_0^\infty f(w)e^{w/3}\,dw<\infty,
\]
but does not display a uniform envelope or a truncate-then-limit argument.

The condition may be sufficient; the objection is proof completeness, not a
counterexample. Before promoting the arbitrary-input theorem, supply a
dominated-convergence proof controlling depths that grow with \(n\).
The exact finite uniform-ball formulas are independent of this issue.

### 4.4 A local probability is not an attack cost

At fixed list size \(N\), changing \(p\) to \(Cp\) changes
\(\mathbb E[\binom N2p]\) by \(C\). It does not determine a list-size rule.
Depending on the separately assumed balance:

* one expected pair gives \(N_{\rm new}\sim N/\sqrt C\);
* a constant neighbors-per-vector heuristic gives \(N_{\rm new}\sim N/C\).

Neither is an end-to-end theorem. Round count, vector replenishment,
deduplication, filters, false negatives, memory traffic, routing, BKZ, and the
outer attack optimizer remain missing.

## 5. Why the R07 rewrite is not the first gate

The pinned R07 source confirms that its model is coupled:

* `C(d,pi/3)` sets the sphere reduction probability;
* list size uses `2/((1-eta)*C)`;
* `W`/`Wmatched`, `ngr`, and `eta` set conditional bucket success;
* popcount pass probabilities depend on the angular law;
* list and bucket sizes drive memory, sorting, recursive misses, and routing.

For variable radii, the reduction angle threshold depends on
\((r_x,r_y)\). A coherent treatment must integrate the joint
\((r_x,r_y,\theta,\text{filter outcome})\) law. Multiplying only `C` by
1.496071 is an intentionally invalid mutation.

The rewrite also assumes iid uniform-ball list radii without observed R07 or
G6K list data. It is a useful same-model sensitivity experiment only after an
applicability control. It is not a replication of a result already supplied
by the paper, and the producer's 8–16 hour estimate is optimistic for a
source-wide joint-kernel rewrite plus outer reoptimization.

## 6. The 69-paper triage

Independent checks support the following narrow conclusions:

* 2026/026 is AES-only masking work; transfer to masked ML-KEM is a new
  instantiation.
* 2026/1462 attacks HQC's fixed-weight sampler, which ML-KEM does not have.
* 2026/1468 attacks asymmetric XOR leakage, but reports no ML-KEM target.
* 2026/1448 is an ML-DSA signing-fault/MILP attack, not ML-KEM decapsulation.
* 2026/155 supplies MLWE/IP-M-EDCP reductions but no solver.
* 2026/1098 is expressly pedagogical.
* 2026/1467 directly reports migration measurements, but its replication URL
  returned HTTP 404 and external predictive validation remains future work.
* Risk-based checks of SIS, decomposed-LWE construction, NTRU-IBKEM,
  NTRU-FHE, HQC, and PQ-signature exclusions found no hidden ML-KEM attack.

This does not validate sixty full-text negative claims. `irrelevant` should be
read as a queue disposition at abstract depth. It must not become negative
security evidence.

After the sibling reviews, 2026/1022 is better labeled an adjacent ML-KEM
modeling lead unless an exact marginal or oracle bridge survives.
2026/1465 is a direct sieve-model sensitivity lead, not direct ML-KEM attack
evidence.

## 7. Baselines and complete-path check

Pollard-rho and BSGS are inapplicable because this is not a generic-group
discrete-log target.

The closest specialized baselines are:

| Claim | Closest baseline | New paper's missing bridge |
|---|---|---|
| Honest ML-KEM DFR | FIPS-cited scalar convolution plus \(np\); Fang–Wang–Zhao concrete-key analysis | Exact compression marginal and full modular event |
| Failure boosting | D'Anvers–Batsleer Kyber multitarget costing | Target rate, oracle, queries, memory, recovery |
| LAC pattern recovery | Guo–Johansson–Yang | Improved charged candidate/recovery cost |
| Concrete memory-routing sieve | pinned R07 | Joint radial/filter kernel, list dynamics, memory/routing and outer reoptimization |
| Practical BKZ/SVP | fitted Pump/progressive-primal models | Refit or benchmark, tours, final search and optimizer |

Neither paper supplies relation collection, rank/uniqueness, source recovery,
target descent, final secret validation, or a standardized solve certificate.

## 8. Cheapest decisive controls

Run the narrowed Thorns audit:

1. Normalize both Section 5.4 radial laws and compute moments.
2. Repeat every tail comparison with the equal-second-moment surrogate.
3. Write the shifted-polydisc proof repair.
4. Derive the ML-KEM decryption identity first in \(R_q\), then with frozen
   centered representatives and wrap variables.
5. Check exact FIPS rational rounding against the pinned script.
6. Reproduce one no-compression CBD coefficient by direct dynamic programming.
7. Add a compressed toy enumerator only if a concrete marginal ambiguity
   remains.

Predeclared outcomes:

* **Scale artifact and joint geometry only:** no FIPS update; stop.
* **Exact marginal mismatch:** freeze a new bounded finite-\(n\) protocol.
* **Representative or rounding artifact:** repair the estimator comparison;
  do not attribute it to thorns.
* **Failed control or infrastructure:** invalid/inconclusive, not negative
  mathematical evidence.

Only after this should the Coordinator reconsider R07. The first R07 control
must be a sphere identity plus one complete radial-angle-filter integral and
evidence for the selected radial law.

## Narrowest supported statement

At the reviewed revisions and cutoff:

* Thorns establishes, subject to a small lower-bound proof repair, a
  fixed-dimension large-deviation geometry for one continuous Gaussian
  polynomial product and gives one-way deterministic geometry for known LAC
  patterns.
* The sieve paper establishes exact finite-dimensional uniform-ball
  probabilities for the `max` local rule and constant-factor asymptotics
  inside its iid isotropic model.
* Neither changes ML-KEM DFR, passive hardness, failure-oracle cost, a matched
  lattice-cost row, or a standardized solve.
* The paper list produces no third lead at triage depth; it is not an
  exhaustive negative literature result.

## Scope limits

No empirical ML-KEM failure run, sieve, BKZ execution, or attack was performed.
No 404, missing code, parser behavior, or timeout is mathematical evidence.
No full-text review of all sixty abstract-level exclusions was performed.
Toy and symbolic checks cannot establish an \(n=256\) rare-event probability.
No official hypothesis, evidence, decision, cost row, or goal state is
changed.

## Primary sources

* Cai, Liu, Wang, Lu, ePrint 2026/1022, current revision 2026-07-19:
  <https://eprint.iacr.org/2026/1022>.
* Stevens and Yonli, ePrint 2026/1465, revision `20260717:191956`:
  <https://eprint.iacr.org/2026/1465>.
* NIST FIPS 203: <https://doi.org/10.6028/NIST.FIPS.203>.
* Kyber failure scripts, pinned
  `75c26949a902ca297b181375bfb7cfaf22cce784`:
  <https://github.com/pq-crystals/security-estimates/tree/75c26949a902ca297b181375bfb7cfaf22cce784>.
* Jaques memory-routing estimator, pinned
  `d197843ddb406102ba101f426ea5a59e8a8a306f`:
  <https://github.com/sam-jaques/sieve-memory-estimates/tree/d197843ddb406102ba101f426ea5a59e8a8a306f>.
* Fang, Wang, Zhao, ePrint 2022/212:
  <https://eprint.iacr.org/2022/212>.
* D'Anvers and Batsleer, ePrint 2021/193:
  <https://eprint.iacr.org/2021/193>.
* Guo, Johansson, Yang, ePrint 2019/1308:
  <https://eprint.iacr.org/2019/1308>.
* Liu et al., ePrint 2026/802:
  <https://eprint.iacr.org/2026/802>.
