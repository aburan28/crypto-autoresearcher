# ePrint 2026/1465: sieve-probability reconstruction and ML-KEM scope

Task `TASK-20260723-214` · source cutoff/access date **2026-07-23**  
Inference: `research-sol-max` requested; `gpt-5.6-sol-xhigh`, `xhigh`,
fallback used, adapter `cursor-subagent-2026-07`.

## Result

Stevens and Yonli prove that replacing the standard sphere model by their
uniform- or non-uniform-ball models changes pair-reduction probability by a
constant factor, not by a factor exponential in dimension [P1]. Every displayed
asymptotic probability retains

\[
p_n=\frac{(3/4)^{n/2}}{\sqrt{3\pi n/8}},
\qquad
-\log_2p_n
=\frac n2\log_2\frac43+\frac12\log_2\frac{3\pi n}{8}+o(1).
\]

Thus the canonical list exponent remains
\(\frac12\log_2(4/3)=0.2075187496\). The paper can increase expected
reducing-pair counts at fixed list size, and it can motivate different constant
or polynomial prefactors in a declared list heuristic. It does **not** change a
classical or quantum sieve exponent, provide a practical BKZ/SVP benchmark, or
revise any ML-KEM attack estimate.

The factors \(1.5\) through \(8\) are local probability ratios. Their logarithms
are not security-bit reductions. In particular, the paper's factor \(8\) is a
global, optimized-sign, non-uniform-ball probability divided by the
**fixed-sign** sphere probability. The matched optimized-sign ratio is \(4\),
and even \(\log_2 4=2\) remains only a log probability ratio until an entire
estimator is rebuilt.

## Source status

The current ePrint record is the initial version received 2026-07-17 and
approved 2026-07-21. The archive freezes its sole and current PDF update as
`20260717:191956`; no later revision entry was visible [P1]. Full PDF text was
obtained. The 45,198-byte, 1,315-line parser extraction has SHA-256
`f9dc5d99bd93bdaafb6eb8369e94ecac6d3383a2cfa63ae22008fd9bf481fdeb`.
That is not a PDF hash: direct binary retrieval returned HTTP 403, so a source
PDF SHA-256 was not recoverable.

No public code or data artifact was linked from the ePrint page or paper, and
none was found in exact-title/author searches of GitHub, Zenodo, IACR
artifacts, or the author's software page. This is a checked-surface statement,
not proof that no artifact exists.

The internal `knowledge/` corpus and `ledger/hypotheses/` had no match for the
paper, title, identifier, or ball-model terminology before this analysis. The
claims below are classified as a known result of [P1], not as a new proposal.

## 1. Four reduction cases

Scale the active radius to one and define

\[
D_-(x,y)=\|x-y\|,\qquad
D_\pm(x,y)=\min(\|x-y\|,\|x+y\|).
\]

The paper crosses these distance choices with two replacement rules:

* `G-`, `G±`: global reduction, \(D(x,y)\le1\);
* `L-`, `L±`: local reduction,
  \(D(x,y)\le\max(\|x\|,\|y\|)\), so the longer input can be replaced.

The parsed statement of Lemma 1 displays `min` of the two input norms in its
two local probabilities. That conflicts with the paper's local-rule
definition, Section 2 CDF, Lemma 3, and the proofs in Sections 3.4–3.5, all of
which use `max`. The exact formulas and \(1.5/3\) constants below are the
`max`-rule results actually proved. They must not be cited for a `min` rule
without a new derivation.

The constants themselves confirm the typo. For uniform-ball scaled depths
\(W_X,W_Y\stackrel{\rm iid}{\sim}{\rm Exp}(1)\),
\(|W_X-W_Y|\sim{\rm Exp}(1)\). Relative to the sphere cap, the `max` rule
contributes

\[
\mathbb E[e^{|W_X-W_Y|/3}]=\frac32,
\]

whereas the printed `min` rule would contribute

\[
\mathbb E[e^{-|W_X-W_Y|/3}]=\frac34.
\]

Thus a literal `min` rule has fixed-/optimized-sign constants \(0.75p_n\) and
\(1.5p_n\), not the paper's \(1.5p_n\) and \(3p_n\).

### Model assumptions and omissions

The paper uses the Gaussian heuristic to motivate a continuous isotropic model;
it does not prove that a practical sieve list is iid. Each modeled pair has
independent, identically distributed radii, independent uniform directions,
and active radius scaled to one. A local step replaces the longer pair member;
a global step replaces the largest list element after finding a combination of
norm at most one. The optimized-sign case tests both \(x-y\) and \(x+y\).
The non-uniform global limit additionally requires a finite exponential moment
\(M_f\).

The model omits lattice discreteness, duplicate vectors, dependent pair
selection, survivor carryover, replenishment and stopping rules,
nearest-neighbor/filter implementation, bucket occupancy, memory traffic,
routing, BKZ integration, and the outer ML-KEM optimizer. These omissions are
why a pair-probability result is not an attack-cost result.

## 2. Sphere model

Let

\[
A_n=I_{3/4}\!\left(\frac{n+1}{2},\frac12\right),\qquad
B_n=I_{3/4}\!\left(\frac{n-1}{2},\frac12\right).
\]

For independent uniform \(X,Y\in S^{n-1}\), the exact fixed-sign probability is

\[
s_n=\Pr[\|X-Y\|\le1]=\frac12 B_n.
\]

Optimizing the sign gives \(s_n^\pm=B_n=2s_n\). There is no local/global
distinction when both input norms equal one. The fixed-sign asymptotic is
\(s_n\sim p_n\).

The complete sphere output law is also explicit. If
\(a=(n-1)/2\), then for \(0\le z\le2\),

\[
\begin{aligned}
F^{G-}_{\rm sphere}(z)
  &=I_{z^2/4}(a,a),\\
f^{G-}_{\rm sphere}(z)
  &=\frac{z^{n-2}(1-z^2/4)^{(n-3)/2}}{B(a,1/2)}.
\end{aligned}
\]

For \(0\le z\le\sqrt2\),
\(F^{G\pm}_{\rm sphere}(z)=2F^{G-}_{\rm sphere}(z)\) and
\(f^{G\pm}_{\rm sphere}(z)=2f^{G-}_{\rm sphere}(z)\). The coordinate laws used
to derive these are

\[
F_{U_1}(t)=I_{(t+1)/2}(a,a),\qquad
F_{|U_1|}(t)=I_{t^2}(1/2,a).
\]

## 3. Uniform-ball model

For independent uniform \(X,Y\in B^n\), the radius has CDF \(r^n\) and PDF
\(nr^{n-1}\). Lemma 3 gives exact CDF/PDF expressions for all output lengths.
Writing \(F_G,f_G\) for the fixed-sign global law, the complete formulas are

\[
\begin{aligned}
F_G(z)
 &=z^n I_{1-z^2/4}\!\left(\frac{n+1}{2},\frac12\right)
   +I_{z^2/4}\!\left(\frac{n+1}{2},\frac{n+1}{2}\right),\\
f_G(z)
 &=nz^{n-1}I_{1-z^2/4}\!\left(\frac{n+1}{2},\frac12\right),
\qquad 0\le z\le2.
\end{aligned}
\]

With \(F_G(t)=1,f_G(t)=0\) for \(t>2\),

\[
\begin{aligned}
F_{G\pm}(z)
 &=2F_G(z)-\frac{z^{2n}}{2^n}\bigl(2F_G(2/z)-1\bigr),\\
f_{G\pm}(z)
 &=2f_G(z)-\frac{nz^{2n-1}}{2^{n-1}}\bigl(2F_G(2/z)-1\bigr)
   +\frac{z^{2n-2}}{2^{n-2}}f_G(2/z),
\quad 0\le z\le\sqrt2,\\
F_L(z)
 &=F_G(z)-\frac12z^{2n}A_n,\\
f_L(z)
 &=f_G(z)-nz^{2n-1}A_n,\qquad 0\le z\le1,\\
F_{L\pm}(z)&=2F_L(z),\qquad f_{L\pm}(z)=2f_L(z).
\end{aligned}
\]

These are analytic distributions, not fitted curves. At threshold one they
simplify to:

| Case | Exact probability |
|---|---:|
| `G-` | \(\frac32A_n\) |
| `G±` | \(3A_n-2^{-n}\) |
| `L-` | \(A_n\) |
| `L±` | \(2A_n\) |

Consequently, the exact ratios to the fixed-sign sphere probability \(s_n\)
are:

| Case | Exact ratio to \(s_n\) | Limit |
|---|---:|---:|
| `G-` | \(3A_n/B_n\) | \(9/4=2.25\) |
| `G±` | \((6A_n-2^{1-n})/B_n\) | \(9/2=4.5\) |
| `L-` | \(2A_n/B_n\) | \(3/2=1.5\) |
| `L±` | \(4A_n/B_n\) | \(3\) |

The sign-matched comparison is the one relevant when the control algorithm
already considers both \(x-y\) and \(x+y\):

| Case | Exact matched-sign ratio | Limit |
|---|---:|---:|
| `G-` | \(3A_n/B_n\) | \(2.25\) |
| `G±` | \((3A_n-2^{-n})/B_n\) | \(2.25\) |
| `L-` | \(2A_n/B_n\) | \(1.5\) |
| `L±` | \(2A_n/B_n\) | \(1.5\) |

The factor-two difference between the two tables is a sign convention, not a
new ball-model advantage.

An independent evaluation of these exact beta-function ratios at BATCH-002's
memory-routing dimensions gives:

| \(d\) | Global matched ratio | \(\log_2\) ratio | Local matched ratio | \(\log_2\) ratio |
|---:|---:|---:|---:|---:|
| 375 | 2.244107 | 1.166142 | 1.496071 | 0.581179 |
| 586 | 2.246205 | 1.167490 | 1.497470 | 0.582527 |
| 829 | 2.247308 | 1.168198 | 1.498206 | 0.583236 |

These values check convergence to \(2.25\) and \(1.5\); they are not cost
deltas.

## 4. Non-uniform-ball model and output lengths

The general finite-\(n\) model starts from
\(X,Y\stackrel{\rm iid}{\sim}R\,U(S^{n-1})\), with arbitrary radial PDF
\(f_R\) on \([0,1]\). Define

\[
g(x,y,z)=\frac{x^2+y^2-z^2}{2xy},\qquad
E_n(x,y,z)=
\frac{z}{xy}
\frac{(1-g(x,y,z)^2)^{(n-3)/2}}{B((n-1)/2,1/2)}.
\]

All four output PDFs have the common form

\[
f_D^\star(z)=c_\star
\iint_{\mathcal R_\star(z)}
f_R(x)f_R(y)E_n(x,y,z)\,dx\,dy,
\]

with the following constants and regions:

| Case | \(c_\star\) | \(\mathcal R_\star(z)\) |
|---|---:|---|
| `G-` | 1 | \(-1<g<1\) |
| `G±` | 2 | \(0<g<1\) |
| `L-` | 1 | \(-1<g<1\) and \(\max(x,y)\ge z\) |
| `L±` | 2 | \(0<g<1\) and \(\max(x,y)\ge z\) |

The corresponding angular CDF kernels are

\[
H_-(g)=
\begin{cases}
0&g\ge1,\\
I_{(1-g)/2}((n-1)/2,(n-1)/2)&-1<g<1,\\
1&g\le-1,
\end{cases}
\]

and

\[
H_\pm(g)=
\begin{cases}
0&g\ge1,\\
I_{1-g^2}((n-1)/2,1/2)&0<g<1,\\
1&g\le0.
\end{cases}
\]

Write a radius as \(r=1-W/n\), where \(W\ge0\) is scaled depth. Let the two
input depths be iid with PDF \(f\), and define

\[
M_f=\int_0^\infty f(w)e^{w/3}\,dw.
\]

When \(M_f\) exists and is finite, [P1, Lemma 6, Proposition 1] shows that the
unnormalized global-output depth density is asymptotically proportional to

\[
M_f^2e^{-2w/3}.
\]

After conditioning on a reduction, both `G-` and `G±` therefore have

\[
W_{\rm out}\ \Longrightarrow\ {\rm Exp}(2/3),\qquad
f_{\rm out}(w)=\frac23e^{-2w/3}.
\]

Input \(f\) controls the total reduction mass through \(M_f^2\), but not the
normalized limiting output shape.

For \(f_a(w)=ae^{-aw}\), convergence requires \(a>1/3\), and

\[
M_f=\frac{3a}{3a-1}.
\]

The global probabilities are

\[
\Pr[G-]\sim p_n\left(\frac{3a}{3a-1}\right)^2,\qquad
\Pr[G\pm]\sim2p_n\left(\frac{3a}{3a-1}\right)^2.
\]

Two cases highlighted by the paper are:

| Input depth | `G-` / \(p_n\) | `G±` / \(p_n\) | Matched-sign ratio |
|---|---:|---:|---:|
| \({\rm Exp}(1)\), uniform ball | \(9/4\) | \(9/2\) | \(9/4\) |
| \({\rm Exp}(2/3)\), stable output | \(4\) | \(8\) | \(4\) |

The stable-input advantage over the uniform input is \(16/9\), whose base-two
logarithm is \(0.830075\).

This is not a stationarity theorem for a complete sieve. The derivation
conditions on the output of one independent model pair. A practical list also
contains unreduced vectors and correlated lattice points and is affected by
deduplication, saturation, filters, update policy, and repeated rounds. The
paper also proves the asymptotic output-shape statement only for the two
global cases, whereas practical Gauss-style replacement is local.

At kernel level, the limit used is

\[
(1-\widehat g(W_X,W_Y,W_Z)^2)^{(n-3)/2}
\sim
\left(\frac34\right)^{(n-3)/2}
e^{W_X/3}e^{W_Y/3}e^{-2W_Z/3}.
\]

Hence the unnormalized global output-density coefficient is

\[
\frac{c_\star(3/4)^{(n-3)/2}}
     {nB((n-1)/2,1/2)}
M_f^2e^{-2w/3},
\]

where \(c_\star=1\) for `G-` and \(2\) for `G±`.

## 5. Empirical evidence and verification boundary

The paper contains no new benchmark, simulation, measured pair probability,
list-size trace, round count, timing, memory result, or attack execution.
Figure 1 is a schematic of the four integration regions. Table 1 gives
algebraic polynomial specializations at \(n=3,5\); it is not empirical.
The introduction's statement that practical sieves outperform sphere-model
predictions is reported motivation inherited from cited prior work.

No code, data, seeds, or supplemental artifact is linked. Exact-title,
author, GitHub, Zenodo, and IACR-artifact searches found none as of
2026-07-23. This bounded absence claim is not evidence against the model.

“Verified” in this report means reconstructed from the current primary text
and checked algebraically or against pinned source, not independently
peer-reviewed or experimentally confirmed. The following were checked:

* sphere, uniform-ball, and arbitrary-isotropic-ball formulas;
* all threshold-one constants and sign-matched ratios;
* the `min`/`max` inconsistency;
* finite beta-function ratios at dimensions 375, 586, and 829;
* the \({\rm Exp}(a)\) moment and preservation of the
  \((3/4)^{n/2}/\sqrt n\) scale;
* R7/R10 sphere-cap, list, pair, filter, and routing dependencies;
* the corrected dual lineage's hard-coded \(2^{0.2075\beta}\) short-vector
  supply and uniform-ball radial score integrals.

Not verified empirically are the applicability of either ball law to a
complete sieve and the claimed practical sphere-model gap. The paper supplies
no finite-\(n\) convergence bound for the non-uniform output limit and no
filter, list, round, memory, BKZ, or ML-KEM rerun.

## 6. What changes for pairs and lists

For a fixed iid list of \(N\) vectors and pair probability \(p\),

\[
\mathbb E[R]=\binom N2p.
\]

Changing \(p\) to \(Cp\) therefore multiplies the expected number of reducing
unordered pairs by exactly \(C\). Independent pair draws need \(1/(Cp)\)
trials in expectation.

There are two different list-size questions:

1. To preserve one fixed expected pair,
   \[
   N_{\rm new}
   =\frac{1+\sqrt{1+4N(N-1)/C}}2
   \sim\frac{N}{\sqrt C}.
   \]
2. Under a saturation heuristic requiring a constant number of neighbors per
   vector, \(Np=\Theta(1)\), so \(N_{\rm new}\sim N/C\).

Only the second route produces a hypothetical list-log change
\(-\log_2C\). It is a separate sieve heuristic, not a conclusion of [P1].
Even then, an all-pairs term would scale as \(1/C^2\) only if every other cost
were held fixed. Filter hits, false positives, vector generation, list updates,
memory, routing, and the number of rounds are not fixed in a real estimator.

For reference:

| \(C\) | \(\log_2 C\) |
|---:|---:|
| \(1.5\) | 0.584963 |
| \(2.25\) | 1.169925 |
| \(3\) | 1.584963 |
| \(4\) | 2 |
| \(4.5\) | 2.169925 |
| \(8\) | 3 |

The right column is deliberately labelled a probability multiplier in log
units, not a security reduction.

The requested impact classification is therefore:

| Quantity | Result from [P1] |
|---|---|
| Local pair-reduction probability | changed by an explicit constant |
| Polynomial factor | unchanged; every probability retains \(n^{-1/2}\) |
| Concrete constant | changed: sign-matched \(1.5,2.25,\) or \(4\) |
| List size | not derived; at most a constant under an explicit balance heuristic |
| Number of rounds | not derived; one conditional global output has an \({\rm Exp}(2/3)\) limit |
| Memory | no direct result; a constant is possible only through a proved list bridge |
| Exponential sieve exponent | unchanged |

## 7. Comparison with BATCH-002

### Progressive primal and practical BKZ

BATCH-002 records progressive-primal RAM-gate estimates
141.4/204.3/276.5 for ML-KEM-512/768/1024 [B2]. PSSearch's practical Pump
model is fitted to implemented sieving, with a \(0.367\) time exponent and a
\(0.2075\) memory exponent plus implementation overhead [S3]. Because the fit
comes from practical sieve behavior, it may already absorb the observed
sphere-model constant gap. Adding any \(\log_2C\) from [P1] would be
double-counting unless the Pump fit, BKZ schedule, final SVP step, and outer
strategy search are rebuilt.

The paper does not alter the root-Hermite-factor requirement, selected block
size, dimensions-for-free rule, progressive-tour count, or final uSVP success
condition. It therefore supplies no update to a practical BKZ or SVP cost.

### `C0`, `CC`, and `CN` dual estimates

`C0` suppresses lower-order exponent and constant terms by definition. A
constant change in pair probability is invisible to this abstraction.

The detailed `CC` and `CN` source lineage is more subtle. Carrier's code uses
fitted sphere-filter costs and short-vector supply
\[
N=(\sqrt{4/3})^{\beta}=2^{0.2075\beta},
\]
but its score integrals use the uniform-ball radial density through terms of
the form
\(\beta\int_0^1 t^{\beta-1}(\cdots)\,dt\) [R3]. This agrees with the
uniform-ball sieve-output heuristic in Ducas–Pulles [S6], rather than putting
all dual vectors on one sphere.

Accordingly, the paper does not newly insert “the ball model” into the
corrected Hou–Jiang values. Its \({\rm Exp}(2/3)\) conditional-output result
could motivate a different radial score integral, but only after showing that
the complete supplied short-vector list follows that distribution. A valid
update would then have to recompute short-vector count and lengths, conditional
filter probabilities, correct- and wrong-score laws, `CC`/`CN` costs, and the
outer ML-KEM optimizer at one success target.

The corrected BATCH-002 values therefore remain:

| Model | ML-KEM-512 | ML-KEM-768 | ML-KEM-1024 |
|---|---:|---:|---:|
| `C0` | 121.9 | 173.0 | 237.4 |
| `CC` | 139.1 | 194.7 | 259.0 |
| `CN` | 134.5 | 188.7 | 254.1 |

The provable-dual and QRS rows use BKZ, discrete-Gaussian sampling, and
guessing formulas. [P1] neither replaces those samplers nor supplies the
missing corrected QRS rerun.

### Memory routing

This is the closest BATCH-002 bridge. At pinned revision
`d197843ddb406102ba101f426ea5a59e8a8a306f`, the Jaques estimator uses the
sphere-cap probability `C(d, pi/3)`, list size

```text
2 / ((1 - eta) * C)
```

and an expected-pair term

```text
C * N * (N - 1) / 2.
```

Its filters additionally depend on spherical wedge probabilities `W`,
conditional reduction probability `ngr`, false-negative parameter `eta`,
bucket loads, and recursive hit probabilities [R7]. The BATCH-002 outputs
145.7/216.5/273.6 are then obtained after memory and two-dimensional
routing/sorting charges.

This means [P1] is relevant to an explicit source assumption, but replacing
only `C` is incoherent. A ball treatment also needs radial versions of `W`,
`ngr`, `eta`, pair supply, bucket occupancy, and recursive filter behavior,
with a matched sign convention. Only then can routing and the optimizer be
rerun.

### Quantum estimates

The same firewall applies:

* `Q0` suppresses constants, so it does not change.
* `QN` and `GE19` inherit spherical list/filter probabilities, fitted
  finite-dimensional costs, and QRACM assumptions. [P1] gives no revised
  query, gate, QRACM-construction, or outer dual cost.
* The \(2^{0.2571d+o(d)}\) quantum-sieve result remains unchanged because
  [P1] changes no exponential coefficient.
* The dimension-400 physical spherical-LSF case study needs a new compiled
  list/filter/routing architecture before any time or qubit change could be
  stated. It is not an end-to-end ML-KEM attack in the first place.

No BATCH-002 quantum row can be changed by subtracting
\(\log_2(1.5)\), \(\log_2(4)\), or \(\log_2(8)\).

## 8. Claim verdicts

| Claim | Verdict |
|---|---|
| Sphere-to-ball reduction-probability gap is asymptotically constant | Supported under iid isotropic assumptions |
| Uniform-ball finite-\(n\) probabilities are exact | Supported; local statement must use the proved `max` rule |
| Conditional global output depth tends to \({\rm Exp}(2/3)\) | Supported under the moment condition |
| A complete practical sieve has stationary \({\rm Exp}(2/3)\) radii | Not established |
| Classical or quantum sieve exponents change | Not supported |
| Factor \(8\) is a matched eightfold practical speedup | Not supported |
| A local ratio is an ML-KEM bit reduction | Invalid without an end-to-end bridge |
| A current BATCH-002 estimate changes | No |

There is no new standardized solve, no attack certificate, and no empirical
run. `EV-MLKEM-002` remains a model-separated literature map.

## 9. Cheapest valid gate

The first test should be a coherent radial rewrite of the pinned memory-routing
estimator [R7], starting only with its ML-KEM-512 sieve dimension \(d=375\).
This source is the cheapest target because it exposes the sphere cap,
conditional wedge, list, expected-pair, bucket, memory, and routing quantities
that a valid bridge must cover.

The task-local candidate is `IDEA-20260723-001`
(`GATE-SIEVE-BALL-R07-001`); it is not filed in the proposal ledger and changes
no official state. Its novelty class is `adaptation`: both ingredients are
known, and corpus, ledger, and web checks found no prior record of this specific
R7 rewrite.

Protocol:

1. Reproduce the pinned sphere control at \(d=375\), routing constant
   \(2^{-12.8}\), within 0.1 log unit of the reported 145.7.
2. Add one radial-law switch consistently to `C`, `W`/`Wmatched`, `ngr`,
   `eta`, list size, expected solutions, bucket loads, and routing.
3. Check the uniform-ball local probability against the exact Lemma 3 ratio
   \(1.4960714399\) at \(d=375\), and attest that optimized signs are not
   counted twice.
4. Rerun the complete \(d=375\) hardware-time optimization with all success,
   routing, geometry, and non-sieve settings fixed.
5. Run \(d=586,829\) only if the treatment moves an optimizer choice or at
   least 0.25 log unit.

Assumptions are frozen in advance: R7 revision `d197843…` and its
two-dimensional routing model are the control; the first treatment is the
paper's exact uniform-ball **local** rule, not its global
\({\rm Exp}(2/3)\) limit; signs, success target, routing constant, optimizer
bounds, and non-sieve terms stay fixed; and every comparison remains labelled
as R7.

Predeclared interpretations:

* If controls pass, the final shift is \(O(1)\), and the slope remains stable,
  [P1] is an estimator-intercept refinement only.
* If controls pass but conditional filters and reoptimization produce a
  dimension-dependent shift, that is a new filter/dynamics interaction not
  implied by [P1]; it needs independent review and practical list-distribution
  validation.
* If the sphere control fails, the treatment changes only `C`, signs are
  mismatched, or actual list data reject both candidate radial laws, no
  BATCH-002 update is admissible.

These outcomes distinguish three explanations: a local-constant-only effect;
an optimizer-coupled concrete effect through filters, buckets, and routing; or
failure of the iid uniform-ball model to apply to operational lists.

The required outputs are reduction probability, list vectors/bits, expected
pairs, conditional hit/false-negative probabilities, code/filter count,
bucket occupancy, routing/sorting cost, total sieve and extrapolated full
primal cost, and selected optimizer parameters. This is a medium
implementation/compute estimator sensitivity test, estimated at 8–16 analyst
hours and under 4 GB memory. It remains specific to the
pinned memory-routing model and is not evidence for `C0`, `CC`, `CN`, `QN`,
`Q0`, `GE19`, QRS, or a physical machine.

Ranking rationale: this gate has the best expected information gain per cost
because R7 is the only BATCH-002 path where the paper's sphere probability is
an explicit, inspectable dependency all the way into list and routing terms.
PSSearch is empirically fitted, the corrected dual family already models
uniform-ball radii in its scores, and the quantum/physical paths add further
unbridged assumptions. One controlled \(d=375\) replay is therefore the
cheapest valid discriminator between “local constant only” and “same-model
reoptimization changes a complete cost.”

## Sources

* **[P1]** Stevens and Yonli, *On Reduction Probability Models in Lattice
  Sieving*, ePrint 2026/1465, PDF revision `20260717:191956`, approved
  2026-07-21. Landing page: <https://eprint.iacr.org/2026/1465>. PDF:
  <https://eprint.iacr.org/2026/1465.pdf>. Version history:
  <https://eprint.iacr.org/archive/versions/2026/1465>. Frozen version:
  <https://eprint.iacr.org/archive/2026/1465/20260717:191956>.
* **[FIPS203]** NIST, *Module-Lattice-Based Key-Encapsulation Mechanism
  Standard*. <https://doi.org/10.6028/NIST.FIPS.203>
* **[EV2]** `ledger/evidence/EV-MLKEM-002.yaml`.
* **[B2]** `TASK-20260722-206`, BATCH-002 corrected cost baseline:
  `cost_baseline_report.yaml` and `cost_landscape.md`.
* **[R3]** Carrier code-based-dual estimator, pinned
  `9c1367f85d26038244bc83c025d84c0b7006f2ee`.
  <https://github.com/kevin-carrier/CodedDualAttack/tree/9c1367f85d26038244bc83c025d84c0b7006f2ee>
* **[R7]** Jaques memory-routing estimator, pinned
  `d197843ddb406102ba101f426ea5a59e8a8a306f`.
  <https://github.com/sam-jaques/sieve-memory-estimates/tree/d197843ddb406102ba101f426ea5a59e8a8a306f>
* **[R10]** Base AGPS/MATZOV sieve-cost implementation, pinned
  `a4d3a53fe1f428fe3b4402bd63ee164ba6cc571c`.
  <https://github.com/jschanck/eprint-2019-1161/tree/a4d3a53fe1f428fe3b4402bd63ee164ba6cc571c>
* **[AGPS]** Albrecht et al., *Estimating Quantum Speedups for Lattice
  Sieves*. <https://eprint.iacr.org/2019/1161>
* **[BDGL]** Becker et al., *New Directions in Nearest Neighbor Searching
  with Applications to Lattice Sieving*.
  <https://eprint.iacr.org/2015/1128>
* **[S3]** Xia et al., *Refined Strategy for Solving LWE in Two-step Mode*.
  <https://eprint.iacr.org/2022/1343>
* **[S6]** Ducas and Pulles, *Accurate Score Prediction for Dual-Sieve
  Attacks*. <https://doi.org/10.1007/s00145-025-09560-7>
