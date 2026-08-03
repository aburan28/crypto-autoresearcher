# TASK-20260802-016 theorem-ingredient literature map

## Disposition

**`ZERO_VIABLE_INGREDIENTS` across four exact theorem families.** This is a
bounded pre-ID screen, not a closure of the literature, the object taxonomy,
`RQ-ECDLP-002`, `GOAL-ECDLP-001`, or generic ordinary prime-field ECDLP. No
canonical IDEA id is warranted and no experiment is proposed.

The screened theorems are real and load-bearing in their native settings. Each
fails at a different interface when converted to the target instance
`Q=[k]P` in a prime-order subgroup of an ordinary `E/F_p`:

| Handle | Primary theorem | Native gain | Prime-field applicability failure |
|---|---|---|---|
| `B22-T01` | Cheon Theorems 1/2, DLP with auxiliary scalar powers | `N^1/4` time/memory at the favorable granted-advice point | requires the unavailable target-specific nonlinear point `[k^d]P` (or `2d` powers) |
| `B22-T02` | Diem main extension-field theorem | `(q^n)^o(1)` expected time for `n -> infinity`, `n/log q -> 0` | a prime field has `n=1`; the proper-subfield factor base disappears |
| `B22-T03` | Fiat–Naor function inversion; Hellman permutation specialization | exact source-free inversion after advice | for `a -> [a]P`, `ST≈N`; balanced time/memory is exponent `0.50`, and setup still costs |
| `B22-T04` | Koutis Theorems 2.4/2.5, odd multilinear detection | constant-overhead detection for fixed degree once a circuit is supplied | the exact all-strata source circuit and witness inverse are precisely the missing operations |

Supported SOTA delta is zero on time, memory, data/query, and security-bit
axes. Pollard rho remains the complete low-memory baseline.

## Frontier read before scouting

The complete BATCH-026 producer and independent review were read together with
`EV-ECDLP-015`, `DEC-20260802-003`, the committed BATCH-027 queue/plan, the
P1552 mechanism frontier, `KN-OPEN-019`, and the current focused claim matrix.
The operation-level map is:

| Occupied family | Tracked object | Operation | Persistent obstruction |
|---|---|---|---|
| Generic collision/orbit | affine scalar labels on a walk | group addition and collision | Shoup square-root boundary in the generic model |
| Relation decomposition | factor-base sources or endpoint aggregate | sum, unrank, eliminate | density, exact source output, rank, logs, and descent |
| Scalar/orientation return | scalar power, character, sheet, period, orientation | lift, separate, invert, return | nonlinear advice, order-`N` dictionary/DLP, or rho-scale return |
| Source-preserving transform | labelled circuit, tensor, module, path, row | contract, detect, factor | deleting labels leaves an aggregate; retaining them pays construction |
| Global cover/correspondence | point/relation image on another object | transport, decompose, pull back | fixed degree changes constants; growing state and return restore cost |
| Public augmented invariant | jet, net, spectrum, incidence, predicate | deterministic evaluation/update | simulator-visible without quantified non-generic density and source use |

This remains a partial map toward `KN-OPEN-019`, not a closed taxonomy.

The five BATCH-026 scoped failures were also frozen before searching:

1. `B21-P01`: short orbit words have average fibre at least
   `N/2^(sw)`; isolating words still need the scalar inverse.
2. `B21-P02`: unordered Kummer decks alias `X` and `-X` although their
   `+P` successors generally differ.
3. `B21-P03`: endpoint jets have no source-tuple interface, exact recall,
   selectivity, rank, logs, or descent.
4. `B21-P04`: degree-coprime isogenies are injective on the subgroup and
   equal-total pullback gives no proved density or independent-rank gain.
5. `B21-P05`: an exact source-complete separator-rank theorem is assumed,
   not supplied.

Longer windows/decks, higher jets, additional bounded-degree charts, tensor
format swaps, and BATCH-020 instrumentation were therefore excluded unless a
theorem changed their information flow. None of the four theorems does so for
the standard instance.

## `B22-T01` — Cheon auxiliary-scalar-power inversion

Primary source: Jung Hee Cheon, [*Discrete Logarithm Problems with Auxiliary
Inputs*](https://doi.org/10.1007/s00145-009-9047-0), Journal of Cryptology 23
(2010), 457–476; [author-hosted full text](https://www.math.snu.ac.kr/~jhcheon/publications/2010/StrongDH_JoC_Final2.pdf).

### Exact theorem and hypotheses

Theorem 1 takes an abelian group of prime order `N`, generator `P`, a positive
divisor `d | (N-1)`, and the three supplied points

```text
P, Q=[k]P, Q_d=[k^d]P.
```

It deterministically recovers `k` in

```text
O(sqrt((N-1)/d) + sqrt(d))
```

group exponentiations and stores the maximum of those two table sizes. Theorem
2 handles `d | (N+1)` under ERH, but requires every `[k^i]P` for
`1 <= i <= 2d` and costs `O(sqrt((N+1)/d)+d)` exponentiations.

### Exact target object and operation

The useful object is not another coordinate system for `Q`; it is the nonlinear
target-specific point `Q_d`. Cheon uses the multiplicative structure of the
scalar field, splits a coset search, collides baby and giant group
exponentiations, and reconstructs `k`.

For `d=N^(theta+o(1))`, the Theorem 1 core costs

```text
time = memory = N^(max((1-theta)/2,theta/2)+o(1)).
```

At `theta=1/2`, granted advice gives exponent `0.25`. It directly outputs `k`,
so relation sources, rank, factor logs, and blind descent are genuinely bypassed;
verification is one `[k]P=Q` check.

### Applicability and complete cost

The theorem does not construct `Q_d` from the standard input. Ordinary generic
group combinations of `P` and `Q` carry affine scalar labels `a+bk`, not
`k^d`. A pairing/CDH oracle, trusted transcript, or party that knows `k` would
change the input model and its data/communication must be charged. Thus the
complete cost is

```text
construct(P,Q -> [k^d]P) + Cheon core + verify,
```

and the first term has no applicable sub-rho theorem. Declaring it free changes
standard ECDLP into DLP with auxiliary inputs. This is the occupied
`ECDLP-IDEA-003`/`008` lane, not a new proposal.

Cheon does not contradict Shoup: the nonlinear auxiliary input is information
outside ordinary generic DLP. It also has no current structured-generic
`delta`-oracle interpretation.

Cheapest falsification: replace `Q_d` by a random group element, and audit any
constructor for knowledge of `k`, a DLP/CDH call, a pairing return, or
target-specific advice. Reopen only for an explicit public constructor whose
complete time and memory are below `N^0.45`.

## `B22-T02` — Diem algebraic factor base over a growing extension

Primary source: Claus Diem, [*On the discrete logarithm problem in elliptic
curves*](https://doi.org/10.1112/S0010437X10005075), Compositio Mathematica 147
(2011), 75–104.

### Exact theorem and hypotheses

For every sequence of prime powers `q_i` and positive integers `n_i` satisfying

```text
n_i -> infinity,
n_i / log(q_i) -> 0,
```

the main theorem solves ECDLP on elliptic curves over `F_(q_i^n_i)` in expected
time `(q_i^n_i)^o(1)`. The algorithm constructs a degree-two cover
`phi:E -> P^1` satisfying the paper's condition, uses the algebraic factor base

```text
{R in E(F_(q^n)) : phi(R) in P^1(F_q)},
```

and solves multivariate systems to return decomposition sources. Relation
collection, linear algebra, and the individual logarithm step are part of the
native route.

### Exact target object and operation

The proper subfield supplies a real non-permutation membership condition:
many extension-field points map through `phi`, but only the points landing in
`P^1(F_q)` form the source alphabet. This is load-bearing extension-field
structure, not merely another bounded isogeny chart.

### Applicability and complete cost

For the target field `F_p`, the extension degree over its prime subfield is
`n=1`. The hypotheses `n -> infinity` and the proper-subfield factor-base
geometry do not exist. Artificially embedding `E(F_p)` into `E(F_(p^n))`
changes the ambient size and leaves the original subgroup sparse; the theorem
does not give original-`N` bounds for setup, relation probability, independent
rank, factor logs, or blind descent below `N^0.5`.

Consequently no prime-field end-to-end exponent can be assembled. This is
consistent with Diem's theorem and with the prime-field summation-polynomial
boundary in Amadori–Pintore–Sala, [*On the discrete logarithm problem for
prime-field elliptic curves*](https://eprint.iacr.org/2017/609). The latter
improves a Gröbner-basis subtask but does not establish a complete sub-rho
prime-field algorithm.

Cheapest falsification: set `n=1` explicitly and show what remains of the
factor base. For any artificial extension proposal, measure costs in original
`N` units, require original-group source replay and blind descent, and compare
separately with rho in both the original and ambient groups.

This theorem therefore redirects the search: find a directly prime-field
algebraic subset with a proved source decomposition and rank theorem. It does
not license relabelling `F_p` as a growing extension.

## `B22-T03` — Fiat–Naor/Hellman source-free inversion

Primary source: Amos Fiat and Moni Naor, [*Rigorous Time/Space Trade-offs for
Inverting Functions*](https://doi.org/10.1137/S0097539795280512), SIAM Journal
on Computing 29(3), 790–803.

### Exact theorem and hypotheses

For a supplied evaluable function `f:[N]->[N]`, the paper gives the tradeoffs

```text
T*S^2 = N^3*q(f),
T*S^3 = N^3  (arbitrary function, arbitrary point),
```

where `q(f)` is the collision probability of two uniform inputs. In the
permutation case, the classic Hellman specialization has `S*T≈N` after
function-dependent preprocessing.

### Exact target object and operation

Define the public permutation

```text
f(a) = canonical_encode([a]P),
y = canonical_encode(Q).
```

Advice stores chain endpoints/checkpoints. Online inversion traverses chains,
handles merges, replays a candidate chain, returns the scalar preimage, and
verifies it. This really is a nonhomomorphic source-free inverse: no source
label is supplied with `Q`.

### Applicability and complete cost

Write `S=N^sigma`. Even optimistically ignoring advice construction,

```text
T=N^(1-sigma+o(1)).
```

The complete campaign rectangle would require both `sigma<=0.45` and
`1-sigma<=0.45`, which is impossible. The balanced point is
`T=S=N^(0.5+o(1))`, matching BSGS; rho dominates at negligible memory. Advice
construction consists of public scalar-to-point evaluations and must be
charged for a single target rather than amortized over an undeclared population.
Coverage failure and replay amplification also remain charged.

The real-curve object uses no encoding-specific elliptic structure beyond the
same permutation exposed by a random encoding. It therefore sits at, rather
than escapes, the Shoup boundary. It is exactly the occupied
`ECDLP-IDEA-374` function-inversion lane and is also adjacent to the BATCH-026
orbit-word inverse obstruction.

Cheapest falsification: build the identical index for a matched random
permutation, record preprocessing separately, freeze the target count before
amortization, and compare full time/memory/coverage. A successor needs a
theorem that beats this matched `ST=N` control due to concrete elliptic
encoding—not another chain schedule, orbit word, or deck.

## `B22-T04` — Koutis odd-multilinear detection

Primary source: Ioannis Koutis, [*Faster algebraic algorithms for path and
packing problems*](https://doi.org/10.1007/978-3-540-70575-8_47), ICALP 2008;
[author-hosted full text](https://www.cs.cmu.edu/~jkoutis/papers/MultilinearDetection.pdf).

### Exact theorem and hypotheses

Theorem 2.4 is a one-sided detector. Given an arithmetic-circuit polynomial,
if no degree-`k` multilinear term exists it always returns no; if a qualifying
odd-coefficient term exists it returns yes with probability greater than
`1/4`. Theorem 2.5 says that if the `n`-variable circuit evaluates over the
integers modulo `2^(k+1)` in time `t` and space `s`, detection costs

```text
O((nk+t)2^k) time,
O(nk+s) space.
```

The hypotheses are crucial: the circuit is already supplied, desired sources
already correspond to square-free monomials, and coefficient parity must not
cancel them.

### Exact target object and operation

The required ECDLP object would be a circuit `C_R` with `6B` occurrence
variables (`B=N^(1/5)`) whose degree-six multilinear monomials are exactly the
coloured tuples

```text
A1+A2+A3+A4+A5-R=O
```

on every repeated, sign, and infinity stratum. With `k=6` fixed, Koutis would
detect an odd solution in `O(t+B)` time after `C_R` exists. Repeated restricted
calls could recover source labels only if the circuit is restriction-stable
and source-addressable.

### Applicability and complete cost

Koutis supplies the detector, not `C_R`. Constructing an exact circuit by the
known explicit `3+3` separator costs `B^3=N^0.6`, while the desired
`B^(9/4)=N^0.45` compact circuit is precisely the missing source-complete
separator theorem in `B21-P05`/P1552. Theorems 2.4/2.5 also do not provide:

- a biconditional all-strata elliptic support proof;
- a parity-isolation theorem for repeated solution monomials;
- exact source output;
- duplicate-normalized independent relation rank;
- factor-base logarithms;
- the identical `Q+[t]P` blind descent; or
- a complete memory/data/communication bound.

Thus the attractive constant-overhead detector cannot be turned into a
complete exponent without assuming the theorem the scout was meant to find.
It is already recorded by `ECDLP-IDEA-280` and the exterior/tensor owners
`050`, `052`, and `056`.

Cheapest falsification: use positive, negative, and duplicated-even-parity
circuits; require all-strata source replay; compare exact ranks and full
pipeline cost against a dimension/marginal/pair-collision-matched random
six-list circuit and explicit `3+3`/`2+2+2` enumerators. Stop on one missed
source or if `C_R` construction exceeds `B^(9/4)`.

## Matched lower-bound and Pareto boundary

The lower bounds are controls, not universal closures:

- Victor Shoup, [*Lower Bounds for Discrete Logarithms and Related
  Problems*](https://www.shoup.net/papers/dlbounds1.pdf), gives the classical
  generic square-root boundary. Cheon lies outside it only because extra
  nonlinear target advice is supplied; Diem lies outside it only in the
  proper-subfield regime; Fiat–Naor matches it; Koutis would lie outside it
  only after a compact elliptic circuit were proved.
- Corrigan-Gibbs, Henzinger, and Wu, [*The Structured Generic-Group
  Model*](https://eprint.iacr.org/2026/384), give
  `Omega(min(sqrt(N),1/delta))` in their defined model. None of the four
  screens supplies an applicable public prime-field structure oracle and
  quantified `delta`; the theorem is not used as a turnkey rejection.

Pareto accounting:

```text
dominated_by: n/a (no result claimed)
supported time-exponent improvement: 0.00
supported memory-exponent improvement: 0.00
supported data/query improvement: 0
cryptographic security bits reduced: 0
```

Cheon's `-0.25` time delta is conditional on changing the input by granting
`[k^d]P`; Diem's subexponential bound is conditional on a field regime absent
from `F_p`; Koutis's near-linear detection is conditional on a missing exact
source circuit. None receives supported SOTA credit.

## Scoped obstructions and forward guidance

These four screens establish named, narrow obstructions:

1. Nonlinear auxiliary-input inversion is powerful, but the auxiliary point is
   the missing operation.
2. Proper-subfield factor bases are powerful, but their load-bearing geometry
   vanishes at prime-field extension degree one.
3. Black-box source-free inversion exists, but its permutation tradeoff is the
   square-root frontier after memory and setup are charged.
4. Multilinear detection is powerful on a supplied circuit, but it neither
   constructs the elliptic source circuit nor returns its witness.

What remains open is correspondingly precise:

- a non-permutation correspondence defined directly over `F_p`, with a proved
  source-valid density/rank gain after construction and equal-total-source
  accounting;
- an encoding-specific source-free inverse strictly beating the matched random
  permutation tradeoff including advice construction; or
- an exact compact Abel–Jacobi separator/circuit theorem that is biconditional,
  all-strata, restriction-stable, and witness-recoverable.

The search should continue in those theorem classes. The absence of a survivor
in four primary-source screens is not evidence that those classes, the
literature, or the ECDLP search space are exhausted.
