# Reinforcement-learning search over an isogeny class for a cheaper point-decomposition presentation

**Status: analysis note and instrument design, not an evidence record.**
Nothing here transitions a hypothesis, closes a lane, or claims a speedup.
`sota_delta`: zero. Claim tier of every number in this note: **toy**. The
demonstration runs in section 6 are smoke runs of the instrument, not
`RUN-*` records, and carry no evidential weight until an approved `EXP-*`
contract re-runs them under the run wrapper.

Instruments: [`harness/rl_isogeny/`](../../harness/rl_isogeny/) (environment,
reward meter, agents, controls; standard library plus the repository's own
`harness/macaulay_fp` and `tools/isogeny_dreg_search`; the PPO agent alone
needs `torch`, optional extra `rl`) and
[`tools/rl_isogeny_search.py`](../../tools/rl_isogeny_search.py) (driver).
Tests: [`tests/test_rl_isogeny.py`](../../tests/test_rl_isogeny.py).
Run outputs: `analysis/rl-isogeny-search/runs/`.
Predecessor: [`analysis/isogeny-dreg-search/DESIGN.md`](../isogeny-dreg-search/DESIGN.md)
(the certified exhaustive search, `IDEA-20260903-47f358`, lane `RQ-ICINV-475b5e`).

---

## 0. The request and its honest instantiation

The brief: *build an ML / RL training solution that looks for elliptic curves
with faster Gröbner-basis / root computation over generic prime fields — an
isogeny that lands on a curve with easier summation polynomials or point
decomposition, where the Gröbner basis does not explode.*

Three facts fix what such a search can and cannot be, and all three are
already measured in this repository.

1. **An isogeny changes the presentation, not the relations.** For an
   ordinary curve `E / F_p` of prime order `N`, every `F_p`-rational isogeny
   is a bijection on `E(F_p)`, so the set of decompositions
   `R = P_1 + … + P_m` is the same on every curve of the isogeny class; what
   changes is the summation polynomial `S_3` of the codomain model and the
   pull-back of the factor base (`analysis/isogeny-dreg-search/DESIGN.md` §0).
2. **Degree-type functionals of `S_3` alone are class-constant.** The
   certified exhaustive search measured monomial support, the first-fall
   degree with a subgroup factor base, and the fibre root statistic of the
   power map `x = u^k` on every member of certified classes from `2^13` to
   `2^40` (551,304 models at 40 bits) and found all three constant on the
   class and equal to their values on random curves of a different trace.
   A reward that is any of those is a constant function, and an agent
   trained on it learns nothing because there is nothing to learn.
3. **Mean decomposition yield is conserved.** `KN-FIND-007`: for any factor
   base of size `B`, the mean number of `m`-fold decompositions per target is
   `C(B+m-1, m)/N` exactly, independent of the base's geometry. A reward that
   is a yield or root-count statistic rewards sampling noise.

So the only honest object for a learned search is the **product space**
`(class member) × (presentation)`, where the presentation ranges over
factor-base constructions — the direction `analysis/isogeny-dreg-search/DESIGN.md`
§8 names as the live one ("other factor-base maps `x = g(u)`, searched jointly
over `(member, c)`"; "chained systems at `m = 3`") — scored by the **exact
Gröbner-shape cost of the resulting polynomial system relative to a matched
null**. That is where an exhaustive enumeration stops being the obvious tool
(the product is large, and at cryptographic `p` the class alone is `≈ 2^128`),
and where a reward can register a needle if one exists. The pre-registered
prior, from facts 1–3, is that on a generic class the null-relative part of
the reward is zero everywhere; the instrument is built so that this null is
*measured with controls that would have caught a needle*, not argued.

The lossy-projection test (`docs/inventor-protocol.md` §2), applied before
computing: the tracked object is the pair `(model, factor-base pull-back)`;
the projection kept is the degree-graded shape of the ideal it presents
(first-fall degree, fall dimensions by degree, Macaulay size at the fall);
what is discarded (the point set) is discarded compatibly by fact 1.

## 1. State, actions, reward

**State.** A curve model `E' : y^2 = x^3 + a'x + b'` in the `F_p`-isogeny
class of the input curve (identified up to `F_p`-isomorphism by `iso_key`,
so a state is an isomorphism class) together with a presentation
`spec = (family, m, k, c, B)`:

| component | values (medium grid) | meaning |
| --- | --- | --- |
| `family` | `direct`, `digit` | `direct`: unknowns `u_i` are free variables with membership `f_V(u_i) = ∏_{v<B}(u_i − v)`; `digit`: `x_i = Σ_j a_{i,j} 2^j` with squarefree digits (`B = 2^s`), the EXP-PFDR digit presentation of `harness/macaulay_fp` |
| `m` | 2, 3 | `m = 2`: `{ S_3(x_1, x_2, x_R) }`; `m = 3`: `{ S_3(x_1, x_2, w), S_3(w, x_3, x_R) }` chained through an internal node `w` |
| `k`, `c` | `k ∈ {1, 2}`, `c ∈ {0, c_1}` | factor-base map `x_i = u_i^k + c u_i` (`c_1` a seeded random residue) |
| `B` | 8 | box size `|V|`; the grid holds `|F| ≈ B` fixed across presentations so they are costed at matched factor-base size |

**Actions** (masked): `stay`; step along the `i`-th rational `ℓ`-isogeny of
the current model for `ℓ ∈ {2, 3, 5, 7}` (kernel polynomials by factoring
`ψ_ℓ`, codomain by Vélu, every codomain order-checked — a failure raises, it
is never a result); set one presentation component to a grid value. Sixteen
steps per episode from the input curve with the default presentation.

**Reward.** Potential-based: `r_t = Φ(s_{t+1}) − Φ(s_t)` with `Φ = score`
(plus the planted bonus in the planted control), so an episode's return is
exactly `score(final) − score(start)` whatever the path, and

```
score = −( log2 nnz(M_{D*})  +  log2 max(1, m! N / B^m) )
        + w_excess  · ( d_ff(null) − d_ff(real) )
        + w_deficit · min(cap, Σ_{D ≤ D*} max(0, fall_real(D) − fall_null(D)))
```

* `nnz(M_{D*})`: nonzero entries of the degree-`D*` Macaulay layer of the
  real system, `D*` the null's first-fall degree — the size of the linear
  algebra the solver does before anything falls. Shape, rows, columns and
  sparsity in one number; this is the term the known levers move (`k`, `c`,
  `m`, digit vs direct, and the sparser `S_3` at `j ∈ {0, 1728}`).
* `m! N / B^m`: expected decomposition trials per relation, the conservation
  mean of `KN-FIND-007`. A formula, not a measurement, because the mean is
  provably not a lever; it is there so `m = 2` and `m = 3` sit on one cost
  scale.
* `d_ff(null) − d_ff(real)`: **the prize.** A real system that falls earlier
  than a null of identical shape. The null is a different-trace random curve
  at the same `p` in the same presentation (`other_trace`, the matched null
  of the exhaustive design; two curves, the reading is the minimum fall and
  the maximum fall dimension over them) or, optionally, the same generators
  with their curve-carrying coefficients scrambled (`curve_scramble`).
* the deficit term counts extra fall dimensions at or below `D*`, capped.

All ranks are exact over `F_p` (`harness/macaulay_fp`, per-layer
convention); no Gröbner basis is computed and no timing is a metric. The
degree cap of the scan is the pre-registered structural fall of the direct
family, `d_ff = B + 2k` (from `u_1^{B−2k} F − lc·(…)·f_V(u_1)`), extended two
degrees at a time while the null shows no fall; the real system is scanned
one degree past the null's fall. Scores are cached per
`(isomorphism class, presentation)`, so revisits are free and the exhaustive
oracle and the agents read the same numbers.

**Observation** (44 floats): rational-isogeny count class per `ℓ` (volcano
position), Legendre symbols of `a', b'` and the `a' = 0` / `b' = 0` flags,
`S_3` support, steps taken and remaining, one-hot presentation, score
relative to the start, best score so far, the fibre coverage estimate
(reported, never rewarded), and eight hash bits of the isomorphism class
(identity features, so a policy can remember where in a class it has been;
`--no-identity` removes them).

## 2. Agents

| agent | what it is | dependencies |
| --- | --- | --- |
| `random` | uniform over valid actions; **the paired baseline every claim is measured against** | none |
| `tabular_q` | Q-learning on the discrete state key (isogeny-count pattern, Legendre flags, presentation indices, identity bits), ε from 0.5 to 0.05 | none |
| `ppo` | clipped PPO with GAE, two-layer MLP policy and value, action masking by logit suppression, deterministic on CPU for a seed | `torch` |

Each is trained for the same number of episodes on the same environment and
seed, then evaluated greedily.

## 3. Controls (inventor protocol §3, before belief)

| control | what it catches |
| --- | --- |
| **paired random baseline** — same environment, seed and episode budget | a learned advantage that is really the budget |
| **permuted reward** (`--permuted`) — the agent is handed state-independent Gaussian noise; the true score is still recorded | leakage: a policy that beats random when trained on noise means the evaluation, not the reward, carries the signal (the C2 control of `EXP-REPL-1d1287`) |
| **planted needle** (`--planted`) — one reachable `(member, presentation)` chosen by a seeded random walk carries a bonus | a search that cannot find a needle when one is planted is not a search (C3 of `EXP-REPL-1d1287`) |
| **exhaustive oracle** (`--oracle`) — the whole class enumerated and certified against `H(4p − t^2)` (`tools/isogeny_dreg_search`), every `(member, presentation)` scored with the same meter | the true optimum and each agent's regret; and the pre-registered reading, *is the score constant across the class for every presentation?* |
| **structural positive control** — a `D_0 = −3` class (`--p 1009 --a 0 --b 7`, `j = 0` members present) | the one within-class degeneration known to exist (`S_3` support 7 at `j = 0`) must move the shape term |
| **order check** on every codomain, **census** in the oracle | a Vélu, kernel-polynomial or isomorphism-key bug becoming a "finding" |
| **conservation guard** | the yield term is a formula and the coverage estimate is a feature only; no statistic that `KN-FIND-007` proves conserved enters the reward |

## 4. Pre-registered outcomes

* **Generic class, oracle certified, `excess_fall = 0` and `deficit_excess = 0`
  on every state** (expected): the null-relative part of the reward is
  constant; the score varies only through the shape term, and the oracle
  shows it varying only across presentations, not across members. An agent
  that beats random then beats it on the shape term alone — it has learned
  the known lever ordering (`k = 1` over `k = 2`, `c = 0` over `c ≠ 0`,
  `m = 2` over `m = 3` at this `B`), which is a demonstration that the loop
  works, not a research result. This is a scoped negative with a measured
  obstruction at `(p, grid, B)`.
* **Planted needle found by the trained agents at a rate far above random,
  and permuted-reward agents at the random rate**: the instrument validates.
  Both must hold before any reading of the generic run is believed.
* **A state with `excess_fall > 0` on a certified class of a generic curve**:
  the interesting case, and *not a claim*. Next step is `/design-experiment`:
  reproduce with independent seeds and null curves, verify the fall
  symbolically, and measure whether it survives at larger `B`. A one-degree
  fall at fixed `B` is a constant factor until shown otherwise.
* **Positive control class**: the `j = 0` members must carry the best shape
  score in the class under at least one presentation, and the agents must
  reach them.

## 5. Why a positive is unlikely, said plainly

Facts 1–3 of section 0 and section 4 of the exhaustive design predict the
negative: the direct presentation's first fall is pinned at `B + 2k` by the
leading terms alone, the chained one at the `w`-resultant, and the digit
presentation's at the squarefree collapse of `S_3`; none of these sees the
curve coefficients except through coincidences of measure zero at generic
`(a', b')`. The search is built anyway for the reason the exhaustive design
gives: an argued negative is `unverified`, a measured one with controls that
demonstrably catch needles is a closure with numbers in it, and the numbers
are reusable by the next presentation family added to the grid.

## 5b. Exhaustiveness: what is settled for every prime, and what an enumeration to 2^48–2^56 would add

The request that followed the first runs was that the search be *exhaustive*,
to `2^48`–`2^56`. Three readings, with what each costs and what each can find:

| reading | object | cost | what it can find for the grid's presentations |
| --- | --- | --- | --- |
| **every curve of an `F_p`-isogeny class, `p ≈ 2^48` … `2^56`** | class of size `≈ √p/π · L(1,χ)`: `≈ 2^23` members at 48 bits, `≈ 2^27` at 56 bits | the fast engine (`tools/isogeny_dreg_search_fast.py`, python-flint, certified census) does `≈ 17 ms` CPU per member: **`≈ 3.5 h` on 12 workers at 48 bits, `≈ 2.4 days` and an out-of-core member table at 56 bits** | only rank-drop coincidences, expected count `2^27 · O(deg/p) ≈ 0` (see the certificate) |
| **every rational isogeny of degree `< 2^56` from one crypto-size curve** | the smooth-degree ball, `≈ 2^56` nodes | not enumerable on one machine at any per-node cost above nanoseconds; prime degrees `ℓ ≈ 2^56` are not computable at all without `Φ_ℓ` | nothing the class reading cannot |
| **every presentation of the grid, on every curve over every prime field** | the leading forms of the systems | **zero: it is a lemma, checked mechanically** | settles `excess_fall > 0` as impossible at every scale |

The third reading is the one this note delivers, because it is strictly
stronger than the first two for the question asked. The lemma
(`harness/rl_isogeny/leading_forms.py`, docstring): the degree-4 part of
`S_3(x_1, x_2, x_3)` is `(x_1 − x_2)^2 x_3^2 − 2 x_1 x_2 (x_1 + x_2) x_3 + x_1^2 x_2^2`;
the curve constants `a, b` sit in degrees `≤ 3`; substituting `x_i = u_i^k + c u_i`
or the digit expansion keeps them below the top degree, and the membership
polynomials carry no curve at all. So the **leading forms of every generator
are the same for every curve**, the syzygy space `K_D` of the leading forms —
which is exactly the set of row combinations that can fall at degree `D` — is
class-constant, and

```
fall_dim(D) = dim K_D − #(syzygies of the full system at D),
d_ff(real)  ≥  first D with K_D ≠ 0  =  d_ff(generic)  =  d_ff(null),
```

with equality unless every remainder vanishes on that curve, a proper
Zariski-closed condition on `(a', b', x_R)` met with probability `O(deg/p)`
per member. Consequences: `excess_fall > 0` is impossible for these
presentations for every curve over every prime field; the only
curve-dependent event is a rank *drop*, which is rarer as `p` grows; and an
enumeration to `2^56` can only confirm the toy enumerations with fewer
coincidences. A within-class effect needs a presentation whose leading forms
depend on the curve, and no polynomial-parametrised factor base has one.

The lemma is verified rather than assumed. `tools/rl_isogeny_search.py --certify`
builds every presentation of the grid on three random curves at each of four
primes — `7127`, `4294967291`, `281474976710597` (48-bit), `72057594037927931`
(56-bit) — and checks (i) the leading forms agree coefficient-by-coefficient
across curves, (ii) the predicted first fall (first degree at which the
leading forms alone admit a syzygy with exact-degree multipliers, or a
squarefree collapse) equals the measured first fall of the full system on
every curve. Result (`runs/leading-form-certificate-medium.json`): **16 of 16
presentations hold at all four primes**; the direct `m = 2` family falls at
`B + 2k` exactly as pre-registered, the chained family at 8 (the
`w`-resultant, for `k = 1`) or `B + 2k − 2`, the digit family at 5–7. The
48- and 56-bit rows of that certificate are the exhaustive statement at the
requested scale; the curve never entered the quantity being searched.

What an enumeration at `2^44`–`2^48` still adds is the *census* — that the
class is what the class-number formula says, with every codomain
order-checked — and the predecessor's `F1`/`F2`/`F3` readings on every
member. That layer is run with the fast engine and reported in section 6;
the `2^56` row is costed above and not run, because the expected number of
members it could flag is zero and the two days would buy a smaller number.

## 6. Demonstration runs

All runs: `B = 8`, medium grid (16 presentations) unless stated, 16 steps
per episode, every episode starting from the **most expensive presentation
of the grid on the input curve** (`--start-spec worst`, the chained
`x = u^2 + c u` system) so that reaching the optimum is a search and not the
start state; agents trained for 300–400 episodes, evaluated on 10 greedy and
10 stochastic episodes; `random` is the paired baseline. Files in `runs/`.

**Oracle readings (the pre-registered negative, enumerated).**

| run | `p` | class (certified) | states scored | `excess_fall`/`deficit_excess` | shape spread across the class | optimum |
| --- | --- | --- | --- | --- | --- | --- |
| `generic-13bit-worst-start` (3 seeds) | 7127 | 24 (yes, `H(4p−t²)` met) | 384 per seed | 0 on every state, every seed | ≤ 0.018 bits (digit family; coefficient coincidences at random `x_R`), 0 on the direct family | `direct(m=2, x=u, B=8)`, class-constant |
| `generic-16bit-seed7-worst-start` | 35933 | 176 (yes; primes 2, 5; 528 order checks, 176 `Φ_2` checks) | 2816 | 0 on every state | ≤ 0.027 bits | same, class-constant |
| `jzero-fullgrid-oracle-p1009` (`D_0 = −3`) | 1009 | 17 (yes) | 272 | 0 on every state | **0.28 bits on the chained `m = 3` presentations, at the `j = 0` members** (the 7-monomial `S_3`); 0 on direct `m = 2` where the specialisation at `x_R` erases the difference | `direct(m=2, x=u, B=8)`, class-constant |

The null-relative terms never fired, on any member of any class, which is
what section 5b proves must happen. The shape term ordered the presentations
identically on every member: `k = 1` over `k = 2`, `c = 0` over `c ≠ 0` for
`k = 2` (denser rows), `m = 2` over `m = 3` at `B = 8`, direct over digit;
the one within-class difference is the known `j = 0` sparsity, visible only
where `S_3` is not specialised.

**Agents against the oracle** (fraction of evaluation episodes ending at
the class optimum; greedy / stochastic policy):

| run | random | tabular Q | PPO |
| --- | --- | --- | --- |
| generic 13-bit, 3 seeds | 0.20 / 0.07 | **1.00** / 0.97 | **1.00** / 1.00 |
| generic 16-bit | 0.30 / 0.00 | **1.00** / 0.50 | 0.00 / 0.00 (stalls at `digit(m=3, u²+cu)`, −0.35 bits) |
| `j = 0` class, full grid | 0.10 / 0.10 | 0.00 / 0.10 (stalls at `digit(m=3, u²)` on `j = 0`, −0.30 bits) | **1.00** / 1.00 |
| `j = 0` class, chained grid, start at a generic member (`--p 1009 --a 752 --b 190 --grid chained`, 4 seeds) | 0.00 / 0.00 | **1.00** / 0.95 | **1.00** / 0.73 |

The last row is the structural positive control: the optimum is the `j = 0`
member under `x = u^2`, 0.28 bits above the generic members, three isogeny
steps away; both learners walk to it on every seed, the random walk ends
there in 0 of 40 episodes. Neither learner is uniformly reliable — each
stalls on one instance at a local optimum a few tenths of a bit below the
class optimum — which is a statement about 300-episode budgets, not about
the landscape.

**Instrument controls** (8 seeds each, planted needle three isogeny steps
from the start in a random presentation, bonus +6; evaluation hit rate,
greedy / stochastic):

| control | random | tabular Q | PPO |
| --- | --- | --- | --- |
| `planted-13bit-8seeds` | 0.16 / 0.13 | **1.00 / 1.00** (8 of 8 seeds) | **0.88 / 0.86** (7 of 8 seeds; the eighth learned the presentation but not the walk) |
| `permuted-13bit-8seeds` (same targets, reward replaced by noise) | 0.16 / 0.13 | 0.13 / 0.13 (1 of 8 seeds, a chance hit) | 0.00 / 0.18 |

Paired best-score differences against the random agent: `+4.4` (tabular)
and `+3.1` (PPO) on the planted control, `−0.4` and `−0.3` on the permuted
control. The search finds needles when they are there and nothing when the
reward carries no signal; the evaluation protocol does not leak.

**PPO learning rate.** At `lr = 3·10⁻⁴` the sampled policy reached the
planted needle 90% of the time while its argmax stalled at the start (hit
0.0); at `10⁻³` both reach it. The default is `10⁻³`; both evaluation modes
are always reported.

**Leading-form certificate** (`runs/leading-form-certificate-medium.json`,
section 5b): 16 of 16 presentations hold at `p = 7127`, a 32-bit, a 48-bit
and a 56-bit prime, 3 random curves each; predicted and measured first
falls agree on every curve.

**Certified class enumeration beyond the toy layer** (fast engine, seed 7,
12 workers, the predecessor's ladder extended):

| `log₂ p` | `p` | class mass (certified) | order / `Φ` checks | wall (12 workers) | F1 support | F2 `d_ff` class / null | F3 class mean ± sd | F3 null mean ± sd | flagged at 64 samples |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 44 | 13275171841363 | 1358080 = `H(4p − t²)` (yes) | 12222342 / 1358038 | 31.7 min | 13–13 | 8–8 / 8–8 (`h = 6`, `h + 2 = 8`) | 1.000 ± 0.177 (max 2.0625) | 0.938 ± 0.178 | 1 |

Seed 7, `k = 4`, 64 samples per member, 8 different-trace nulls;
trace `-2582635`, discriminant `-46430683822227` (conductor 1), census
11 s, enumeration and measurement 1903 s. The one flag —
`j = 2667519855300`, F3 mean 2.0625 at 64 samples, 4.0 pooled standard errors
past the null mean — was re-measured at 1024 samples with a fresh seed alongside
20 random non-flagged members and the 8 nulls
(`runs/recheck-44bit-seed7.json`): survivor **1.039**, controls
0.990 ± 0.041, nulls 1.003 ± 0.061.
A signal that vanishes when the sampling that produced it is increased was sampling; the flag is not a candidate, exactly as the ten flags at 36 bits were not.
The reading is the predecessor's — `F2 = h + 2` on every one of the 1358080 members and
on every null, `F1 = 13` everywhere, F3 inside the null band — now at `2^44`,
the largest certified class in the repository. Per section 5b the `2^48` row
(`≈ 4 h` at this rate, with the checkpoint dump growing to `≈ 3 GB` for a
`10^7`-member table) and the `2^56` row (`≈ 3 days`, out-of-core) can only
repeat it.

## 7. Cost and scale

Per state the meter costs 3–50 ms at `B = 8` (the chained `m = 3`
presentations are the expensive end); an episode of sixteen steps costs a
few hundred milliseconds cold and nothing warm. At cryptographic `p` the
class is `≈ 2^128` and no exhaustive layer exists; the smooth-degree ball
(`analysis/isogeny-dreg-search/DESIGN.md` §5) is enumerable and a learned
policy is, in principle, the only thing that could do better than a random
walk over it. Whether that is worth running is decided by section 5b, not by
compute: for the grid's presentations the null-relative reward is
class-constant by the leading-form lemma, so a crypto-scale walk would be
searching a constant function at `≈ 20 ms` a step. The environment itself
builds and runs at 48- and 56-bit primes in well under a second per episode
(trace by baby-step giant-step, kernel polynomials by factoring `ψ_ℓ`, the
meter's cost independent of `p`), so the search side is scale-ready the day
a presentation family fails the certificate.

## 8. Open directions (what the next session should try, not what this one claims)

1. **Presentation families whose leading forms depend on the curve.** By
   section 5b this is the *only* place a within-class needle can live, and
   no polynomial-parametrised factor base has one: any membership polynomial
   is monic and the top form of `S_3` carries no curve constant. Candidates
   that break the pattern are presentations in which the curve enters the
   top degree — a weighted grading that puts `a x_1 x_3` on the same level
   as `x_1^2 x_2^2` (which is not the grading F4 uses, so its cost model
   must be argued separately), a factor base pulled back through the
   isogeny itself (`x' = f_φ(x)`, whose denominator carries the kernel),
   or the eliminated Edwards `y`-only `S_3` (`IDEA-20260807-78eafe`, never
   measured). Add them to `build_presentation`, run `--certify` first: a
   family that fails the certificate is the first one worth an oracle run.
   `m = 4` through `S_4` stays polynomial-parametrised and is expected to
   certify (use `experiments/EXP-ECTD-001/driver/semaev.py`'s resultant
   `S_4`, never `harness/semaev.py:s4_expr`, `KN-OPEN-5b3a08`).
2. **Composite-order classes.** On a class of even order the group structure
   varies across members (rational 2- and 4-torsion), which is a genuine
   within-class lever for the symmetrized models of Faugère–Gaudry–Huot–
   Renault; a quotient presentation in the `T`-invariant coordinate would
   make it visible to the shape term. Not cryptographic, but the one
   within-class positive control that is real rather than planted.
3. **The smooth-degree ball at crypto `p`** as a screening walk, only if a
   toy-scale oracle ever shows within-class variance of the null-relative
   term.
4. **Turn the obstruction over**: a provably class-constant score is a class
   invariant; note it as a tool for *identifying* classes and move on.

## 9. Reproduction

```bash
python3 -m pytest -q tests/test_rl_isogeny.py
# the scale-free statement: leading forms at 7127, 32-, 48-, 56-bit primes
python3 tools/rl_isogeny_search.py --certify --p 7127 --a 3 --b 5 --grid medium \
    --out analysis/rl-isogeny-search/runs/leading-form-certificate-medium.json
# the certified class enumeration beyond the toy layer (needs python-flint)
python3 tools/isogeny_dreg_search_fast.py --ladder 44 --seed 7 --workers 12 \
    --outdir analysis/isogeny-dreg-search/runs --checkpoint-dir /tmp/ck44 --members-limit 0
python3 tools/rl_isogeny_search.py --p 7127 --a 3 --b 5 --seed 1 --seeds 3 --episodes 300 --start-spec worst --oracle \
    --out analysis/rl-isogeny-search/runs/generic-13bit-worst-start.json
python3 tools/rl_isogeny_search.py --bits 16 --seed 7 --episodes 300 --start-spec worst --oracle \
    --out analysis/rl-isogeny-search/runs/generic-16bit-seed7-worst-start.json
python3 tools/rl_isogeny_search.py --p 7127 --a 3 --b 5 --seed 1 --seeds 8 --episodes 400 --start-spec worst --planted \
    --out analysis/rl-isogeny-search/runs/planted-13bit-8seeds.json
python3 tools/rl_isogeny_search.py --p 7127 --a 3 --b 5 --seed 1 --seeds 8 --episodes 400 --start-spec worst --planted --permuted \
    --out analysis/rl-isogeny-search/runs/permuted-13bit-8seeds.json
python3 tools/rl_isogeny_search.py --p 1009 --a 752 --b 190 --seed 1 --seeds 4 --episodes 300 --grid chained --oracle \
    --out analysis/rl-isogeny-search/runs/jzero-walk-control-p1009.json
python3 tools/rl_isogeny_search.py --p 1009 --a 0 --b 7 --seed 1 --episodes 200 --start-spec worst --oracle \
    --out analysis/rl-isogeny-search/runs/jzero-fullgrid-oracle-p1009.json
```
All of the above run with `--eval-episodes 10 --max-steps 16`; together they
take about six minutes on one machine, the certificate ten seconds.

Every run is deterministic in `--seed` (the PPO agent on CPU included). The
committed JSON is a **summary**, in the convention of the predecessor's
ladder files: the environment summary, per-agent training statistics and
learning curves by decile, the evaluation outcomes per mode (histograms of
the final and best states, per-episode scores and hits, no trajectories),
the paired comparison against the random agent,
and the oracle's per-presentation statistics, best state and any state with
excess. The per-state oracle table and the per-episode training records are
regenerable from the seed and are not committed; `--full-out PATH` writes
them alongside, the summary records that file's SHA-256, and
`--summarize-full PATH --out SUMMARY` rebuilds the summary from it without
recomputing anything.
