# Independent Red Team report — TASK-20260802-215

## Verdict

**REVISE.** The affine-label producer-output argument supports a narrow,
average-case ordinary generic-group lower bound after modest formal repair, and
the graded-tower construction is algebraically well typed as a purely
conditional oracle theorem. The package is not proof-complete as written.
Lemma 6 and PO-213-08 conflate a collision-free producer transcript with a
collision-free combined producer/verifier transcript. Consequently, their
perfect- and statistical-soundness bounds omit verifier-generated labels and
are false under the stated verifier interface. The exact preprocessing
tradeoff also drops additive terms, and several Pareto `dominated_by` and delta
fields do not follow from the artifact's own dominance rule.

This is an independent objection and repair report only. It makes no
experiment, implementation, official-state, closure, support, SOTA, novelty,
or breakthrough decision.

## Immutable review basis

I reviewed the TASK-213 sources from Git commit
`7516d91c156a662aed73c4acc6bb17a088c70370`, whose sole parent is
`59b50c5c2594b7b9ab7343feef9a8c23416f68d5`. I did not interpret mutable queue
text as a source. Before interpretation, each supplied blob reproduced its
declared SHA-256:

| Snapshot path | SHA-256 |
|---|---|
| `tasks/TASK-20260802-213/ordinary-acquisition-analysis.md` | `74138505d7f92b4a194ab9bbd42ee00ac20b2e926191334bd927620c3ce128e3` |
| `tasks/TASK-20260802-213/proof-obligations.yaml` | `509eea888f8bcd0ccb49c61ca50a69ccfbf4d190f767ea83f27f90d377555308` |
| `tasks/TASK-20260802-213/escape-interfaces.yaml` | `3491898539f1c403f64eeff5c45b8ec9d3e5797777065c2122b5602e05672a62` |
| `tasks/TASK-20260802-213/pareto-frontier.yaml` | `befc5c2006c36ab595c82cc8af21d3962d98aac493e542c2ede8d82b09df1545` |
| `tasks/TASK-20260802-213/provenance.yaml` | `979c9c4586c556b36d611112e28d398f16fa5a38248c8376151eb29b406afd7f` |
| `archives/TASK-20260802-214/snapshot_commit_receipt.json` | `9fd3e277d58c1dd86027be61143803ba39dc9bdf8c5eda704e83f94cf8e597fa` |

The TASK-214 receipt is intentionally non-self-referential (`commit_sha` and
`parent_sha` are null in that blob); the commit and parent above were checked
directly from Git. I also checked the cited primary implementation paper,
Sakemi et al., *Solving a Discrete Logarithm Problem with Auxiliary Input on a
160-bit Elliptic Curve*, PKC 2012,
https://www.iacr.org/archive/pkc2012/72930594/72930594.pdf.

## Independent reconstruction

### 1. Ordinary model and affine labels

Let the input be `sigma(1)` and `sigma(alpha)` for uniform
`alpha in F_r^*`, with `sigma` a random injection. Before a collision between
distinct formal expressions, the permitted point operations map

`(a+bX, c+dX) -> (a+c)+(b+d)X`,

with negation and disclosed-scalar multiplication as special cases. Thus every
oracle-produced point label stays in `span_F_r{1,X}`. Branches on fresh raw
encodings do not alter that span: after fixing algorithm coins and a symbolic
lazy-sampling transcript, those strings are independent of the numerical
value of `alpha` until a formal collision equation is met.

For a fixed symbolic transcript, equality of two distinct affine labels has at
most one root in `alpha`. With `P` preprocessed constant handles and `L`
online affine labels including `Q`, the producer's candidate collision-root set
has size at most

`B(P,L) = (P+1)L + binom(L,2)`.

This is better justified as a fixed-symbolic-transcript root-set union bound.
The payload's sentence that conditions successively on excluded values does
not by itself justify retaining denominator `r-1`, because the conditional
sample space shrinks. Fixing the symbolic transcript before sampling the
semantic `alpha` supplies the required argument.

### 2. Output agreement and `rho_f`

On the no-collision branch, an oracle-issued output has some affine label
`a+bX`. Hence, subject to the output-handle convention noted below,

`Pr[R=f(alpha)G] <= (B(P,L)+rho_f)/(r-1)`.

For `f(X)=X^d`, `X^d-bX-a` is a nonzero polynomial of degree `d<r`, so the
root bound gives `rho_f<=d`. Because `d | r-1`, taking `a=1,b=0` shows in fact
`rho_f=d`. For fixed `0<delta<1` and `d=N^(delta+o(1))`, this is `o(N)`, so the
bound is nonvacuous in the sub-collision regime for every such fixed `delta`.
If `delta` is allowed to vary with `N`, the theorem must instead retain the
explicit premise `d=o(N)`.

The `d/(r-1)` term is accidental correctness, but it is not intrinsically
unrecognizable: an ordinary verifier can recognize it by solving a DLP and
checking the relation. What is true is that no *sub-rho recognizer has been
provided*. Its full recognition cost must be charged.

### 3. Cheapest counterexample to Lemma 6 / PO-213-08

Take a producer with `P=0` and no group-oracle result beyond the inputs. It
outputs `R=G` and an empty (or trivial) certificate. Let the public verifier
use deterministic baby-step/giant-step in the declared ordinary generic
interface to recover `z=dlog_G(Q)`, and accept exactly when `R=z^d G`.

- The verifier is finite and perfectly sound for every instance and encoding.
- The producer has no informative collision.
- For each of the `d` values satisfying `alpha^d=1`, the verifier accepts the
  collision-free producer output.
- With `L=1`, the claimed statistical formula at soundness error zero gives at
  most `B(0,1)/(r-1)=1/(r-1)`, while actual accepted-correct probability is
  `d/(r-1)>1/(r-1)`.

The verifier obtains its information through its own generic collisions. If
those verifier labels are included in `L`, the counterexample disappears, but
then Lemma 6 lower-bounds combined producer-plus-verifier work, not
`C_acquire` separately. If they are not included, the lemma and its statistical
variant are false. Coupling verifier coins does not fix omitted verifier oracle
responses.

Arbitrary certificate scalars create a second formal obligation. On a
collision-free producer transcript, every emitted scalar must be shown to be a
function only of public constants, producer coins, and coupled encoding
strings, so it is identical across coupled `alpha` values. The certificate's
scalar/handle length and every verification access must also be charged.
Otherwise “finite certificate” leaves an unbounded, unpriced data channel.

The cheapest repair is proof-only: derive the producer acquisition lower bound
directly from the already stated uncertified output bound (Lemma 5), which does
not need verifier soundness. Retain a separate certificate lemma only after
including all verifier labels, oracle calls, comparisons, certificate symbols,
randomness, and statistical error, and state its conclusion for total
producer-plus-verifier work.

### 4. Preprocessing, online work, and memory

If `q_g` counts online group-oracle results, then `L<=q_g+1`, so the exact
constant-success consequence is

`P(q_g+1) + (q_g+1)^2 = Omega(N)`,

up to constant factors, not literally `P q_g + q_g^2=Omega(N)` when `q_g=0`.
Equivalently, define `q:=q_g+1>=1` before writing the shorter formula. Handle
comparisons, accessed preprocessed handles, and certificate traffic are
additional charged work and cannot reduce this lower bound.

For a single instance, constructing `P` handles and producing `q_g` online
labels gives charged work at least `P+q_g`; the corrected relation implies
`P+q_g+1=Omega(sqrt(N))`. This is enough for the claimed exponent-one-half
producer-output barrier. It does not prove a positive memory lower bound, and
the payload correctly avoids one. If preprocessing is shared over `K`
instances under the same encoding, report all of `P`, `P/K`, online work,
comparisons/accesses, and peak retained memory `Omega(P)`; a per-instance time
below one half can be bought with a larger shared table and is not a
single-instance contradiction.

For expected work, Markov truncation is valid for a Las Vegas producer: a run
of expectation `T` truncated after `2T` succeeds with probability at least
one half. For a general constant-success variable-time producer, the truncation
constant must be chosen relative to its declared success probability. For
restart strategies, total expected cost includes attempt generation,
recognition, certificate production and verification, all multiplied by the
appropriate inverse success probability.

### 5. Cheon composition

The primary paper's DLPwAI input is exactly
`G, alpha G, alpha^d G`, with `d | r-1`, and it gives two-stage time

`O(sqrt((r-1)/d) + sqrt(d))`.

Thus for `d=N^(delta+o(1))`, the downstream exponent is
`chi(delta)=max((1-delta)/2,delta/2)`, minimized at `1/4` when
`delta=1/2`. The paper implements both searches with rho walks and
distinguished points; its memory reduction has a distinguished-point spacing
parameter and an additive walk overhead. An exponent-zero memory row is
reasonable only with that time/memory choice made explicit. The experimental
implementation itself also used precomputation tables and distinguished-point
databases, so it is not evidence of literally zero storage.

Once the corrected producer-output lower bound gives single-instance
acquisition work `Omega(sqrt(N))`, adding Cheon's downstream work cannot make
ordinary generic total time sub-rho. This narrow composition does not depend
on the defective certificate lemma. For a theorem over arbitrary primes, the
cost or input status of the required multiplicative-group generator/order
factorization should be declared; the implementation paper simply states that
the generator can be found efficiently and uses a structured known instance.

### 6. Graded-tower typing and query count

Under the stated axioms

`e_(i,j)(x T_i,y T_j)=xy T_(i+j)`, `i+j<=d`,

the types are correct. Let `ell(n)` be an addition-chain length. One can build
`T_d` in `ell(d)` maps, build `D_d=alpha^d T_d` in another `ell(d)` maps,
build `T_(d-1)` in `ell(d-1)` maps, and obtain
`A_d=e_(1,d-1)(Q,T_(d-1))` in one map. Therefore the explicit bound is at most
`2 ell(d)+ell(d-1)+1=O(log d)` interface calls. All of
`T_d,A_d,D_d` lie in the same order-`r` group `H_d`, satisfying Cheon's
orientation.

This count assumes direct uniform access to every required `e_(i,j)` and reuse
of intermediate nodes. It is not a construction-cost bound. A sound cost model
must additionally charge:

- a uniform description or an explicit table of the group/map family;
- setup and authentication of the common order, generators and map laws;
- level indices and the number of materialized levels;
- element encodings and ordinary group operations in `H_d` needed by Cheon;
- map-evaluation cost as a function of `i,j,d`, not just call count;
- setup/certificate soundness error and inverse setup success;
- parameter and data movement, retained memory, certificate length, and
  verifier work; and
- any required scalar-field factorization/order data for Cheon's two stages.

An explicit `Theta(d)` setup/description at balanced `d=N^(1/2+o(1))` removes
strict time gain. Reaching level `d` does **not** by itself prove such a lower
bound: a genuinely uniform succinct family could name levels in `O(log d)`
bits. The payload therefore has only a tautologically valid conditional oracle
theorem—if all charged acquisition and target-group costs have exponent below
one half, composition is sub-rho in time. It supplies no ordinary elliptic-curve
instantiation and no reason to believe the cost premise holds.

Memory must remain a separate Pareto axis. A tower can be sub-rho in time yet
use memory exponent at least one half; that is not a Pareto improvement over
constant-memory Pollard rho.

## Pareto audit

The frontier is explicitly local to six rows, so it supports no global SOTA or
closure claim. Within that list:

- `PF-213-01`: `dominated_by: null` is supported within the declared list.
- `PF-213-02`: `dominated_by: PF-213-01` is not supported by the stated
  exponent-only dominance rule. Both rows have identical values on every
  listed numeric and assumption dimension. The extra downstream stage may
  worsen constants/workflow, but no listed dimension records that strict
  difference. Mark this as a tie with `dominated_by: null`, or add and quantify
  a primitive-work/constant dimension.
- `PF-213-03`: conditional time delta `-1/4` is correct for the supplied exact
  auxiliary point, and null dominance is defensible because the input
  assumption is incomparable with ordinary input. Its “ordinary delta” should
  be `not_applicable`, not numeric zero.
- `PF-213-04`: Pollard dominates it: equal time/memory exponents and a strictly
  weaker interface assumption. This row is correct.
- `PF-213-05`: null dominance is only valid in the branch
  `kappa_tower<1/2`. When `kappa_tower>=1/2`, Pollard is no slower and has the
  strictly weaker interface, with no worse baseline memory/data/setup axes;
  the row is dominated. Split the row or make `dominated_by` piecewise. Include
  target-group operation and setup-description costs before evaluating the
  branch.
- `PF-213-06`: the same piecewise issue applies. When
  `max(kappa_L,lambda/2)>=1/2`, ordinary Pollard is no slower and assumes no
  leakage; below one half the rows are incomparable. Split or condition the
  dominance field.

The stated delta convention is “candidate exponent minus ordinary baseline.”
Overriding that formula with zero for every ordinary-inadmissible row is not a
quantitative delta; it conflates “not admissible” with “no improvement.” Use
`ordinary_*_delta: not_applicable` and retain a separately labeled conditional
delta. Likewise, the scalar `input_assumption_rank` must not be used as an
ordering between an exact correlated point, a graded map family, and interval
leakage; those are a partial order and the prose already treats them as
incomparable.

## Critical defects and required repairs

1. **RT-215-C1 — certificate/verifier collision omission (critical).** Lemma 6,
   its statistical formula, PO-213-08, and the inference that
   `exp(C_acquire)>=1/2` from that lemma are invalid as written. Apply the
   counterexample above. Repair with Lemma 5 for producer correctness, or add
   verifier labels and weaken the conclusion to total work.
2. **RT-215-C2 — adaptive game not fully formalized (major).** Replace the
   shrinking-denominator deferred-decision sentence with a symbolic-transcript
   experiment fixed independently of `alpha`; explicitly include raw-string
   branches, arbitrary certificate scalars, verifier coins, and every collision
   root relevant to the claimed game.
3. **RT-215-C3 — exact tradeoff drops terms (major).** Use
   `P(q_g+1)+(q_g+1)^2=Omega(N)` or define an online-label count at least one.
   Keep comparisons, accesses, preprocessing construction, amortization and
   memory on separate charged axes.
4. **RT-215-C4 — output/certificate channel underspecified (major).** Lemma 5
   assumes an already issued handle. State that output must be oracle-issued,
   or add the probability of guessing an unused valid encoding as a function
   of `lambda`. Charge every certificate scalar/handle and its bit length.
5. **RT-215-C5 — tower cost premise incomplete (major).** Add uniform map-family
   description, level materialization, target-group Cheon operations,
   setup-law certification, scalar order/factorization data, and soundness /
   inverse-success terms. Do not infer an ordinary construction from the
   symbolic exponents.
6. **RT-215-C6 — Pareto fields violate their own rule (major).** Correct
   `PF-213-02`, make `PF-213-05` and `PF-213-06` piecewise, and use
   `not_applicable` rather than zero for inadmissible ordinary deltas.

## Strongest defensible narrow result

Subject to a formal symbolic lazy-sampling game and an oracle-issued-output
convention, an ordinary generic producer that receives `G,alpha G`, uses `P`
charged alpha-independent constant handles, encounters `L` online affine
labels, and emits one point satisfies

`Pr[R=f(alpha)G] <= ((P+1)L+binom(L,2)+rho_f)/(r-1)`.

For `f(X)=X^d`, `d|r-1`, and fixed `0<delta<1`, `rho_f=d=o(N)`. Constant
producer correctness therefore forces
`P(q_g+1)+(q_g+1)^2=Omega(N)` and charged single-instance producer work
`Omega(sqrt(N))`. Composing that scoped ordinary generic acquisition with
Cheon's known DLPwAI algorithm cannot beat time exponent one half. This is a
known-style scoped generic-model result, not a novelty, global closure, SOTA,
ordinary-curve, or non-generic impossibility claim.

The graded bilinear tower separately yields a correctly typed Cheon triple in
`O(log d)` map calls under its axioms, but remains an uninstantiated conditional
interface. Coordinate algorithms, pairings, correspondences, leakage,
alpha-dependent advice, quantum computation, high-affine-agreement targets,
and succinct certified nonlinear maps remain outside the narrow barrier.

## Cheapest falsification / repair route

No experiment is needed. First put the `R=G` / exact generic-DLP verifier
counterexample into the proof review; it falsifies the current certificate
lemma at essentially zero implementation cost. Then make the smallest repair:
base the acquisition theorem on Lemma 5, redefine `q` as the number of online
labels including `Q`, and reserve a separate combined-work certificate lemma
whose collision set includes verifier work. A proof checker can then audit one
fixed symbolic transcript and its at-most-`B+rho_f` exceptional alpha set.

Only after that proof repair should a theory task specify a concrete uniform
graded family. Its cheapest falsifier is a description-size/access audit: list
the exact bytes and primitive costs needed to instantiate every addition-chain
level and the `H_d` Cheon oracle at balanced `d`; any unavoidable
`Omega(d)` setup, accessed data, verification, or target-group work eliminates
strict sub-rho time for that instantiation while leaving other non-generic
interfaces open.
