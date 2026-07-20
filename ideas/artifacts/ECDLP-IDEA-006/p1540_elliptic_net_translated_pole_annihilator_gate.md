# P1540 elliptic-net translated-pole annihilator gate

## Status and claim boundary

- Record type: theorem-only producer gate
- Root hypothesis: `ECDLP-IDEA-006`
- Candidate: `P1540`
- Claim: `CLM-P1540-ELLIPTIC-NET-TARGET-ANNIHILATOR`
- Evidence scale: exact symbolic statements plus literature controls; no experiment
- Review state: `unreviewed`
- Contract state: `ideas/contracts/ECDLP-EXP-CONTRACT-006_elliptic_net_rank_preflight.yaml`
  remains `review_required` and was not executed
- Breakthrough claim: none
- Disposition:
  `UNREVIEWED_SCOPED_SYMBOLIC_NO_GO__STANDARD_HANKEL_DISPLACEMENT_RANK_IS_TAUTOLOGICAL__CONSECUTIVE_TRANSLATED_X_BLOCKS_HAVE_LINEAR_COMPLEXITY_AT_LEAST_(M-2)/3__FULL_ORBIT_ORDER_AT_LEAST_(N-3)/3__TARGET_SPECIFIC_NONLINEAR_LOCATOR_UNSUPPLIED__OPEN`

This receipt does not prove a lower bound against every elliptic-net algorithm. It
separates three objects that the current hypothesis and frozen contract conflate:

1. the nonlinear elliptic-net recurrence;
2. the standard displacement rank of a Hankel container; and
3. the constant-coefficient linear complexity needed for an annihilator.

The first computes values, the second is at most two for every scalar sequence, and the
third is linear in the length of every consecutive finite translated-coordinate block.
A qualifying survivor must therefore specify a different target-specific nonlinear or
variable-coefficient locator and a direct index decoder.

## Hash-bound inputs

- `ideas/ECDLP-IDEA-006_elliptic_net_short_annihilator_hypothesis.md`:
  `a87796ff5d484574110a438eadfa9a6afbecdafe485667490bbeb32b86906bde`
- `ideas/contracts/ECDLP-EXP-CONTRACT-006_elliptic_net_rank_preflight.yaml`:
  `64dbd7389d693378909eb17dd9f25b5d598099ea51eed961345c8738eac70f3f`
- `ideas/ECDLP-IDEA-011_scalar_orbit_elliptic_period_descent_hypothesis.md`:
  `560ce9a5b8f154f57e91a61c96fd7edc2420c8da511defb9d2a50f34e47f78f3`
- `ideas/artifacts/ECDLP-IDEA-003/p1530_r1_r2_independent_audit.md`:
  `e7dfae990f357da7d1f3f8503c06d6334323d925244d3803f2a002888081c402`
- `ideas/artifacts/ECDLP-IDEA-003/p1531_r1_independent_audit.md`:
  `67561fc763a2909c71ba6ca5017deb59d3be302e385a391dca18b07ef0bddc61`
- `ideas/artifacts/ECDLP-IDEA-003/p1532_r1_independent_audit.md`:
  `fec71dc29a264a08e19208e41195f2fb25922b0ccfa2e51038f384e521b6d2e5`
- `ideas/artifacts/ECDLP-IDEA-003/p1533_r1_independent_audit.md`:
  `0de12da09c1bc49aa577431cff5ac09a264a367bce57aa1699c495015c28803f`

## Focused rerank: IDEA-011 is already consumed

IDEA-011 proposes

```text
I_H(R) = sum_(h in H) x([h]R)
```

or another coefficient of the scalar-orbit polynomial. Let

```text
F_(H,R)(Z) = product_(h in H/{+1,-1}) (Z - x([h]R))
```

when `-1 in H`; use the corresponding unquotiented multiset otherwise. The first
elementary symmetric coefficient of `F_(H,R)` is the signed sum of the orbit
coordinates. If IDEA-011's sum ranges over both `h` and `-h`, it is twice that
coefficient outside characteristic two. Thus the proposed invariant is not merely
similar to the P1530-P1533 family: it is one of its frozen orbit-polynomial
coefficients.

The subgroup-chain refinement is the relative-trace tower of the same orbit algebra.
P1530-P1533 already admitted and audited:

- a scalar-orbit type-1 or type-2 distinguisher;
- Cauchy/logarithmic-derivative labels of the orbit polynomial;
- row-preserving batches and Fourier-mode controls;
- relative norms and direct or deformed resultants; and
- collision-multiset recovery with complete source-label and cost accounting.

Changing the coefficient, chain parameters, batch layout, or solver does not add a new
mathematical operation. IDEA-011 therefore receives no P1540 slot. Its exact open
exception remains the same one already preserved by P1530-P1533: a compact separating
orbit evaluator with a complete index decoder and end-to-end exponent below one half.

## Exact elliptic-net interface

Let `E/K` be a nonsingular Weierstrass elliptic curve, let `P,Q in E(K)`, and let

```text
W(a,b) = Psi_(a,b)(P,Q)
```

be the rank-two elliptic net obtained by evaluating Stange's net polynomials. For
vectors `v,w in Z^2`, Stange's Lemma 4.2 gives the rational-function identity

```text
Psi_v^2 Psi_w^2 (X_v - X_w) = -Psi_(v+w) Psi_(v-w).
```

On every nonexceptional specialization this becomes

```text
x([v_1]P+[v_2]Q) - x([w_1]P+[w_2]Q)
  = -W(v+w) W(v-w) / (W(v)^2 W(w)^2).
```

In particular, with `v=(n,1)` and `w=(m,1)`,

```text
x(Q+[n]P) - x(Q+[m]P)
  = -W(n+m,2) W(n-m,0)
      / (W(n,1)^2 W(m,1)^2).
```

The quotient is invariant under the quadratic rescalings that define elliptic-net
scale equivalence because it is exactly a coordinate difference. It therefore gives a
gauge-invariant bridge from a source-complete net block to the translated coordinate
orbit. Vanishing denominators are relation locations and must be represented in a
complete projective chart rather than dropped.

For `Q=[x]P`, the same net also has

```text
W(a,1)=0  iff  [a]P+Q=O  iff  a=-x mod N
```

under the usual nondegeneracy hypotheses. Fast evaluation of `W(a,1)` is consequently
not index recovery: the missing operation is locating its unique relation index without
testing an order-`N` set or transferring the label to another order-`N` DLP.

## Nonlinear recurrence is not an annihilator

An elliptic net satisfies a quartic recurrence of the form

```text
W(p+q+s)W(p-q)W(r+s)W(r)
+ W(q+r+s)W(q-r)W(p+s)W(p)
+ W(r+p+s)W(r-p)W(q+s)W(q) = 0.
```

This recurrence supports fast evaluation from a bounded initial region. It does not
give constants `c_0,...,c_r` satisfying

```text
sum_(j=0)^r c_j s_(n+j) = 0
```

on the translated sequence, and it does not identify the index of a supplied block.
Lauter and Stange define width-`s` EDS Discrete Log as exactly this index-location
problem. Their width-three perfectly-periodic problem belongs to the same
subexponential-hardness equivalence class as ECDLP. This is a prior-art and circularity
control, not an unconditional polynomial or square-root lower bound.

## Standard Hankel displacement rank is tautological

For an arbitrary scalar sequence `(s_i)`, form the `m by n` Hankel matrix

```text
H_(i,j) = s_(i+j),  0<=i<m, 0<=j<n.
```

Let `Z_m` and `Z_n` be the lower shift matrices. Then

```text
Delta(H) = Z_m H - H Z_n^T
```

vanishes away from the first row and first column. Therefore

```text
rank(Delta(H)) <= 2
```

for every sequence: random, planted, elliptic, or otherwise. Measuring this quantity
cannot distinguish a short recurrence or compress the target shift. It is the ordinary
Hankel data layout, not an elliptic-net property.

By contrast, low ordinary Hankel rank or a short kernel valid on all required windows
is equivalent to low constant-coefficient linear complexity. The contract's phrase
`exact minimal displacement order r` must be replaced by one exact operator and one
decoder before any experiment. Giving credit for `rank(Delta(H))<=2` would make the
random-sequence negative control pass identically.

## Translated-pole theorem

Let `P` have order `N>=5`. Write `x` for the Weierstrass x-coordinate as a rational
function on `E`; its only pole is a double pole at `O`. For `n in Z/NZ`, define

```text
f_n(R) = x(R+[n]P) in K(E).
```

### Theorem 1: symbolic orbit dimension

The `N` functions `f_0,...,f_(N-1)` are linearly independent over `K`.

Proof. The function `f_n` has one pole, of order two, at `R=-[n]P`. These `N`
points are distinct. In a relation `sum_n c_n f_n=0`, inspect the pole at
`R=-[j]P`. No term except `c_j f_j` has a pole there, so `c_j=0`. This holds for
every `j`. QED.

Consequently the translation operator `T_P:f(R)->f(R+P)` has a cyclic subspace of
dimension `N` generated by `x`. No nonzero target-independent constant-coefficient
annihilator of order below `N` holds as a rational-function identity. This statement
does not require semisimplicity or a Fourier splitting field.

### Theorem 2: finite consecutive-block linear complexity

Let

```text
s_i = x(R+[i]P),  0<=i<M,
```

where all `M` points are finite and distinct, and let `r<M` be the order of a
nonzero constant-coefficient recurrence valid on every available window:

```text
sum_(j=0)^r c_j s_(i+j) = 0,  0<=i<M-r.
```

Then

```text
r >= ceil((M-2)/3).
```

Proof. Define the nonzero rational function

```text
F_R0(Z) = sum_(j=0)^r c_j x(Z+[j]P).
```

It is nonzero by Theorem 1, since `r<N`. It has at most `r+1` distinct double
poles, hence pole degree at most `2(r+1)`. The recurrence gives `M-r` distinct
zeros at `Z=R+[i]P`; the assumption that the whole block is finite keeps these
zeros away from every contributing pole. A nonzero rational function has equal
zero and pole degrees, so

```text
M-r <= 2(r+1),
```

which rearranges to the stated bound. QED.

Taking the complete finite subgroup orbit

```text
s_i=x([i]P),  1<=i<=N-1
```

gives

```text
r >= ceil((N-3)/3).
```

The coefficients may be selected after seeing `P`, `Q`, or the sequence: once fixed
they are constants in `K`, and the same pole count applies. Thus an exact
constant-coefficient full-orbit annihilator of order `N^(rho+o(1))` with
`rho<=0.18` does not exist. More generally, the annihilator order of a consecutive
finite block is linear in that block's length, so a low order relative to the sampled
window cannot be attributed to elliptic-net structure.

### Exact scope of the theorem

The pole count closes only:

- constant-coefficient recurrences on translated x-coordinate blocks;
- ordinary low-Hankel-rank claims that imply such recurrences; and
- source-complete gauge-invariant net representations whose claimed compression is
  exactly such a translated-coordinate annihilator.

It does not close:

- a variable-coefficient recurrence whose coefficient construction is itself compact;
- a nonlinear target-specific state machine;
- a short local signature paired with a separately proved global index locator;
- another net observable that does not reduce to translated x-coordinate linear
  complexity; or
- a quantum, non-generic, low-embedding-degree, anomalous, or special-curve attack.

Each exception must still expose its construction, target dependence, ambiguity, output,
time, memory, and direct index decoder.

## Fourier and eigenvalue label boundary

Assume `N` is prime to `char(K)` and pass to a field containing a primitive `N`-th
root of unity `zeta`. A cyclic shift by the hidden scalar acts on Fourier mode `j` by

```text
hat(t)_j / hat(s)_j = zeta^(j*x)
```

whenever the denominator is nonzero. For prime `N` and `j!=0`, labeling that eigenvalue
is an order-`N` discrete logarithm in the root-of-unity subgroup. Multiple modes verify
the same label but do not turn exponent recovery into root finding.

If the root-of-unity subgroup lies in a small extension field, this is the familiar
pairing/MOV-style transfer boundary and the extension construction plus finite-field DLP
must be charged. On a generic ordinary prime-field family no small embedding degree may
be assumed. An annihilator that returns only `zeta^x` has therefore moved, not solved,
the index problem.

## Full cost gate for a surviving operation

Let a proposed replacement use state size `r=N^(rho+o(1))`, construction exponent
`a`, structured-algebra exponent `omega_s`, target evaluation exponent `q`, direct
index-location and ambiguity exponent `tau`, and memory exponent `mu`. Charge

```text
lambda = max(a, omega_s*rho, q, tau).
```

Promotion still requires all of:

- an exact public block built from `(E,P,Q)` without `x`;
- a gauge/projective invariant definition across zeros and exceptional charts;
- a state operation not equal to standard Hankel displacement rank;
- no constant-coefficient translated-x annihilator contradicted by Theorem 2;
- `rho<=0.18` only for an actually useful state, not a boundary generator;
- measured or proved `omega_s<=2.2`, `a<=0.30`, `q<=0.20`, and `tau<=0.40`;
- complete `lambda<=0.45` and `mu<=0.45` including failed targets and setup;
- direct recovery of `x mod N`, with every ambiguity independently checked; and
- no order-`N` group or finite-field DLP in eigenvalue labeling.

Because this is a direct ECDLP route, a passing decoder would not separately need an
index-calculus relation matrix, factor-log solve, or blind descent. It must instead
recover the supplied target scalar end to end under the complete direct-route cost.

## Controls and falsifiers

### Required positive controls

- A planted linearly recurrent sequence must recover its known minimal polynomial and
  hidden shift.
- A projectively rescaled rank-two net must produce the same coordinate-difference and
  index output.
- Exhaustive small groups must retain every exceptional zero and signed candidate.

### Required negative controls

- A random matched sequence must also show standard Hankel displacement rank at most two;
  this metric receives zero promotion credit.
- The ordinary nonlinear elliptic-net recurrence may predict values but must fail the
  index-output gate unless a separate locator is supplied.
- A Fourier/eigenvalue output is rejected unless its exponent label is recovered and
  charged.
- A short block selected after the known toy scalar is rejected as target advice.

### Immediate falsifiers for the current formulation

- The measured quantity is only `rank(ZH-HZ^T)` or an equivalent boundary rank.
- The proposed full-orbit constant recurrence has order `o(N)`.
- The block state is not invariant under a valid quadratic net rescaling.
- The decoder outputs a root of unity, field eigenvalue, or candidate set whose labeling
  costs an order-`N` DLP or `N^(1/2+o(1))` search.
- The implementation reads the known toy shift outside the independent verifier.

## Literature boundary

1. Katherine E. Stange, *Elliptic Nets and Elliptic Curves*,
   <https://arxiv.org/abs/0710.1316>. Lemma 4.2 supplies the exact net-to-coordinate
   identity; Corollary 5.2 supplies the zero/relation interface; Section 6 records
   quadratic scale equivalence and normalization.
2. Kristin E. Lauter and Katherine E. Stange, *The elliptic curve discrete logarithm
   problem and equivalent hard problems for elliptic divisibility sequences*,
   <https://arxiv.org/abs/0803.0728>. The width-three EDS Discrete Log problem is in the
   same subexponential-solvability class as ECDLP, and eigenvalue-style reductions can
   return a finite-field DLP rather than the index.
3. Thomas Kailath, Sun-Yuan Kung, and Martin Morf, *Displacement ranks of matrices and
   linear equations*, <https://doi.org/10.1016/0022-247X(79)90124-0>. This is the
   classical structured-matrix context for distinguishing displacement rank from
   ordinary rank and recurrence complexity.

These sources do not contain Theorem 2 in the exact P1540 formulation claimed here; its
proof is included in full and requires independent checking before it can alter the
candidate's status.

## Producer decision

The current IDEA-006 contract cannot execute as written. Its central metric permits a
tautological rank-two answer, while the meaningful constant-linear-annihilator reading
is excluded at sublinear full-orbit order by the translated-pole theorem. No code,
fixture, solver, or toy rank sweep should be built until the operation is replaced.

P1540 remains queued and unverified because a target-specific nonlinear or
variable-coefficient elliptic-net locator is not ruled out and has not been supplied.
This is a sharper falsifiable boundary, not a better-than-rho algorithm, a Shoup-bound
improvement, or a breakthrough.

## Exactly one next action

Independently reconstruct the net-to-coordinate identity, the Hankel displacement
calculation, and both translated-pole theorems; then either name one gauge-invariant
target-specific nonlinear or variable-coefficient net operation with a direct index
decoder and complete `lambda,mu<=0.45`, or return P1540 as terminal inconclusive. Do not
execute or revise the `review_required` IDEA-006 contract during that audit.
