# Candidate A — RCF-Bind reduced-characteristic fiber

Task: `TASK-20261008-ba8247`  
Proposal: `IDEA-20261008-305a07`  
Hypothesis: `H-SSI-0e38a2`  
Status: **typed obstruction**

RCF-Bind asks whether the reduced characteristic polynomial of a noncentral
endomorphism can provide the public binding relation required by the current
EndRing-PKE funnel. It is not a PKE, security result, novelty claim, parameter
proposal, or implementation. No experiment, benchmark, formalization, or
network retrieval was performed.

## Relation

Let `E/F_(p^2)` be the canonically encoded bare curve supplied by the declared
EndRing challenge. An input

```text
x = (alpha, alpha_dual)
```

contains normalized rational maps for a primitive noncentral separable
endomorphism and its dual, of degree at most the public polynomial bound `D`.
An output is

```text
y = (t,n),                 Delta = t^2 - 4n < 0.
```

The public relation `R_E(x,y)` verifies rational-map validity and the exact
identities

```text
alpha_dual o alpha = [n],       alpha o alpha_dual = [n],
alpha + alpha_dual = [t].
```

It also recomputes the degree, checks primitivity, bounds, canonical grammar,
and negative discriminant. Thus `Z^2-tZ+n` is the reduced characteristic
polynomial of `alpha`. Equality is equality of normalized rational maps, never
agreement on a finite tuple of points.

The proposed public equivalence is the whole accepted fiber of fixed `(E,y)`.
Conditional on the standard but unverified-in-this-packet quaternion statement,
two noncentral elements of `B_(p,infinity)` with the same reduced
characteristic polynomial are conjugate by `B_(p,infinity)^*`. Hence every
accepted preimage belongs to one rational quaternion-conjugacy class. This is
not equality as maps, conjugacy by an efficiently known automorphism of `E`,
or an efficiently supplied conjugator.

The central object is a global rational-map characteristic relation. It is not
a walk endpoint, lexicographic path, parity mask, or finite point-evaluation
tuple.

## Required algorithms and first obstruction

`Eval(E,x)` is public: validate the maps, compute `n=deg(alpha)`, verify the
dual identities, and emit canonical `(t,n)`. Its proposed cost is polynomial
in the explicit rational-map length and `log p`; coefficient normalization is
charged.

The required sampler is

```text
SampleNoncentralEnd(E,D; rho) -> (x, Eval(E,x)).
```

It must use only bare `E` and public coins, run in polynomial time, and succeed
with inverse-polynomial probability. This packet has no such algorithm.
Public multiplication maps and immediate isogeny/dual backtracks are scalar,
have `Delta=0`, and fail the domain. Calling a noncentral generator here would
assume a OneEnd-like solution before the binding game begins. This is the
first missing required public polynomial algorithm, so the packet stops as a
typed obstruction rather than inventing a sampler.

For completeness, the required secret inverse would be

```text
Inv(E,B,(t,n)) -> (alpha,alpha_dual)
```

for **every** complete evaluable saturated basis `B` of `End(E)`. It expands
`alpha=sum z_i beta_i`, imposes reduced trace `t` and norm `n`, and solves the
resulting integral quadratic equation. Finite bounded enumeration defines a
search, but its cost can be exponential in the bit length of `n`. No uniform
polynomial representation solver, map-conversion bound, or honest-fiber
success theorem is supplied. Thus even after the public-sampling obstruction,
the every-basis inverse remains open.

## Any-basis quantifier

The required claim is

```text
for every E in D_ER,
for every honest (x0,y) output by Sample(E),
for every valid complete evaluable basis B of End(E),
Inv(E,B,y) returns x with R_E(x,y)=1 in poly(lambda),
except with one explicitly bounded, basis-independent failure probability.
```

If `B'=BU` for any `U in GL_4(Z)`, coefficient vectors transform by `U^-1`
but trace and norm remain intrinsic. A valid inverse may return a different
conjugate. It may not use a planted basis, short-vector tie rule,
lexicographic path, or secret alignment. No algorithm in this packet proves
runtime or output-law invariance under arbitrary large unimodular changes.

## Binding versus actual-message recovery

Binding alone is not PKE functionality. A message adapter must define `Rec`
such that

```text
Rec(E,x,c) = Rec(E,x',c)
```

for every valid ciphertext `c` and every two accepted `x~_y x'`. No such
nonpublic recovery operation is supplied. Any function only of `(t,n)` is
fiber-invariant but is already public. A function of a particular rational
map may distinguish conjugate representatives and needs a separate invariance
theorem. Therefore RCF-Bind does not recover a selected plaintext and does not
discharge PKE correctness or functionality.

The scalar nearby object makes the issue explicit. If central maps `[a]` were
allowed, `y=(2a,a^2)` has one accepted preimage in a division algebra, so the
relation is perfectly binding—but `a` and `[a]` are publicly recoverable.
Binding without asymmetric recovery proves too little.

## Smaller-witness audit

One accepted preimage embeds the quadratic order

```text
Z[Z] / (Z^2 - tZ + n)
```

into `End(E)`. That single embedding is sufficient to invert one RCF challenge.
It is not a rank-four saturated basis of the maximal order. The proposed
inverse therefore factors as

```text
complete ring basis
  -> trace/norm representation solver
  -> one quadratic-order embedding
  -> accepted preimage.
```

No non-factorization theorem or reconstruction theorem reverses this arrow.
Repeated accepted preimages can be adversarially correlated and may generate
only a proper quadratic suborder. The packet does not multiply per-call
success probabilities or assert a positive saturation probability. Failure to
derive such a bound is not proof that its infimum is zero.

## Repeated-use game

The first intended game is `OW-RCF`. The challenger samples bare `E`, runs
`Sample(E)` to obtain `(x,y)`, gives `(E,y)` to a classical PPT adversary, and
accepts an output `x'` exactly when `R_E(x',y)=1`. For `q(lambda)` adaptive
uses, all sampler coins would be fresh, but adversary outputs and later actions
may depend on the full ordered transcript. The public view contains curve and
field bytes, `D`, all parser/relation code, every `y`, every evaluation and
rejection response, input lengths, and query order. The sampler is required to
be stateless; the game records public history. QPT/QROM, timing, side channels,
and hidden state are outside scope.

This game is presently uninstantiable because `SampleNoncentralEnd` is missing.
An unavailable algorithm aborts the game and supplies no evidence.

## Correct security direction

A solver for bare EndRing must receive only `E`, use the scheme/interface
attacker, and output a complete evaluable basis. The desired quantitative
statement would have the form

```text
Adv_OW-RCF(A)
    <= L(lambda) * Succ_EndRing(S) + delta(lambda),
```

with polynomial `L`, negligible `delta`, polynomial runtime, and every abort
charged. No such values exist here.

The reduction stops twice:

1. Challenge embedding cannot generate honest `y` from bare `E` without the
   missing public sampler.
2. A successful attacker returns one quadratic-order embedding, not a complete
   maximal-order basis. Rank growth, index, discriminant, and saturation are
   not forced by the relation.

The reverse implication—complete EndRing knowledge can search its trace/norm
lattice—is only an attack route. It is not the required security reduction,
and even that inverse is not shown polynomial.

## Controls

- Leaking `alpha` or an embedding certificate makes inversion public and must
  not imply EndRing.
- A hypothetical public inverse gives OW success one while the complete-ring
  extractor is still absent.
- The scalar subdomain is uniquely binding and publicly invertible.
- Replacing the relation by a walk endpoint restores ordinary many-to-one
  ambiguity and is outside this candidate.
- Replacing rational-map identities by finite point evaluations triggers the
  CEST/RWCT finite-witness regression.
- Adding an orientation, torsion basis, connecting ideal, or secret tag changes
  the problem from bare EndRing and fails T1.
- Distinct accepted rational maps with fixed `y` are the collision test. If
  they are not quaternion-conjugate, binding fails; if a proposed `Rec`
  differs on them, message invariance fails.

## Obligation summary

| Gate | Producer status | Reason |
|---|---|---|
| T1 / O1 | open | Bare distribution remains symbolic; public sampling is missing. |
| T2 / O2 | breaks for this packet | No polynomial Sample and no polynomial every-basis Inv. |
| T3 | breaks for complete-ring necessity | One quadratic-order embedding is the smallest known sufficient witness. |
| T4 / O5 | breaks for this packet | Both challenge generation and preimage-to-complete-ring extraction are absent. |
| T5 / O6 | proposed, unreviewed | Grammar, failures, repetition and controls are explicit. |
| O3 / O4 | open/breaks | No actual-message PKE adapter or nonpublic fiber-invariant recovery exists. |
| C1--C6 | open | No primary-source novelty audit, complete PKE, implementation, cost table, or independent review. |

The method ceiling is narrow: reduced trace and norm may bind accepted maps to
one rational conjugacy class. They do not provide bare-curve sampling,
efficient every-basis inversion, asymmetric message recovery, complete-ring
necessity, IND-CPA, or EndRing security.

## Prior-art and overlap boundary

The four KB files read here are abstract/first-pages pointers. They describe
Séta torsion-attack inversion, SiGamal public-point action, isogeny UPKE, and a
LIT diagram. RCF-Bind instead uses a global rational-map characteristic fiber,
but this comparison is insufficient for novelty. Novelty remains unverified.

The required local frontier command's highest displayed hits were
`KR-RHO-53c89f` (score 17) and `KR-IC-f5c584` (15), followed by unrelated
ECDLP trace/index-calculus rows. No displayed hit matched the claimed
interface, but that is not an exhaustive literature search. CEST, ER-McE,
UTTK, RWER, and the four named remote proposals were screened only through the
frozen methodology and predecessor report because their full records were not
in this blind task's read scope. Absence of a verified overlap is not a
non-duplication result.

## Named formalization blocker and next action

`FORMAL-BLOCK-RCF-CONJUGACY-INVARIANCE`:

> Formalize the exact theorem that `R_E`'s accepted trace/norm fiber is one
> `B_(p,infinity)^*`-conjugacy class under the declared rational-map grammar,
> and determine whether any publicly specified, nonpublic message-recovery
> functional is constant on that class.

This blocker is downstream of the first algorithmic obstruction. The immediate
next action is a proof-level audit of whether any bare-curve polynomial sampler
can produce a noncentral member without already solving a OneEnd-like problem.
It must not implement or benchmark the undefined sampler.
