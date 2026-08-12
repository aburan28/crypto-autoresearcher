# Balanced-Primary Sign-Oblivious Isogeny Identification

Date: 2026-07-20

## Claim status

- Balanced-primary uniqueness: `RESTRICTED THEOREM`
- End-to-end ordinary ascending recovery: `OBSERVATION / TOY-EVIDENCE / MODEL-BOUND`
- Additive-plus-curve-identity comparison: `NEGATIVE RESULT` for a toy speed claim
- Novelty: `NOVELTY-UNVERIFIED`; the arithmetic complement criterion was not
  found explicitly, but phase retrieval supplies the abstract sign-partition
  architecture
- Deployed cryptographic impact: `OPEN`; no deployed break is claimed

## Result in one paragraph

Suppose a degree-`d` isogeny is known on one generator of each of several
pairwise-coprime odd primary subgroups, but each image is known only up to an
independent sign.  Let the generator orders be `n_1,...,n_r`.  For every sign
partition `S`, form the sum of complementary products

```text
N_S + N_complement,
N_S = product_{i in S} n_i,
```

and let `beta` be the minimum over all partitions.  If `beta>4d`, the data
identify the degree-`d` isogeny up to one global sign.  This criterion gives a
strictly smaller sample threshold than raw additive Kummer-orbit
interpolation.  On a genuine degree-5 ascent over `F_34651`, actual
Frobenius-oriented self-pairings at orders `3,7,11` give `beta=32>20` but only
9 additive rows, short of the 10-row linear-interpolation threshold.  A public
three-row Schoof/Velu decoder recovered the unique kernel in three
acquisition-seed runs.  A stronger nine-row baseline then imposed the public
codomain curve identity on the interpolation pencil and recovered the same
map faster.  A zero-row source-only enumerator was faster still because the
toy source has one rational degree-5 edge.  The surviving result is a
compressed-generator identification criterion and interface validation, not a
measured runtime or protocol break.

## Setup

Let `K` be a field of characteristic different from `2`, and let

```text
phi, psi : E0 -> E1
```

be isogenies of the same degree `d`, with `gcd(d,char(K))=1`.  Let
`P_i in E0(Kbar)` have pairwise-coprime odd exact orders `n_i`, all prime to
`char(K)*d`.  The points may live in different extension fields.

Define

```text
N_S = product_{i in S} n_i,
beta(n_1,...,n_r) = min_S (N_S + N_complement),
```

where an empty product is one.

## Balanced-primary theorem

### Theorem

Assume

```text
x(phi(P_i)) = x(psi(P_i))
```

for every `i`.  If

```text
beta(n_1,...,n_r) > 4d,
```

then `psi=phi` or `psi=-phi`.

Equivalently, one sign-free generator image per primary identifies at most one
degree-`d` x-map between the marked endpoints.

### Proof

Equality of target x-coordinates gives a local sign

```text
phi(P_i) = epsilon_i psi(P_i),  epsilon_i in {+1,-1}.
```

Let `S` contain the indices with sign `+1`.  For `i in S`, the point `P_i`
lies in `ker(phi-psi)`; for `i` outside `S`, it lies in `ker(phi+psi)`.
Because the orders are pairwise coprime, the subgroups generated in each
kernel have orders `N_S` and `N_complement`.  These orders are prime to the
characteristic, so they are reduced subgroup schemes and their orders are at
most the degrees of the corresponding nonzero homomorphisms.

If neither `phi-psi` nor `phi+psi` is zero, the degree parallelogram identity
gives

```text
deg(phi-psi) + deg(phi+psi)
  = 2 deg(phi) + 2 deg(psi)
  = 4d.
```

Hence `N_S+N_complement<=4d`, contradicting the definition of `beta`.  One of
the two homomorphisms is therefore zero, which gives `psi=phi` or `psi=-phi`.

The argument does not require `phi+psi` or `phi-psi` to be separable.  It only
uses their prime-to-characteristic reduced kernel subgroups.

## Strict separation from additive interpolation

Let

```text
C_ram = sum_i (n_i-1)/2.
```

For every subset `S`,

```text
N_S >= 1 + sum_{i in S}(n_i-1).
```

Applying this to both sides of a partition gives

```text
beta >= 2 + sum_i(n_i-1) = 2 + 2*C_ram.
```

Thus the old condition `C_ram>=2d` implies the new condition, but the converse
can fail.  For

```text
d=13,  (n_i)=(3,5,7,11),
```

the additive capacity is `11<26`, while the minimizing partition is
`(3*11,5*7)` and `beta=33+35=68>52`.

If `m=product_i n_i`, AM-GM also gives

```text
beta >= 2*sqrt(m).
```

Therefore `m>4d^2` is a cheap sufficient condition.  Exact `beta` can be
computed by a meet-in-the-middle search over subset products.  Since the
empty partition gives `beta<=1+m`, the theorem still requires `m>4d-1`; it
does not create a new small-product torsion region.

### Asymptotic separation

The strict improvement is asymptotic, not only numerical.  Fix
`epsilon>0`.  Suppose four pairwise-coprime odd orders satisfy

```text
(sqrt(2)+epsilon)*sqrt(d) < n_i < C*sqrt(d)
```

for a fixed constant `C`.  For sufficiently large `d`, every two-versus-two
partition has sum greater than `4d`; every one-versus-three and empty-versus-
four partition is larger still.  Hence `beta>4d`.  Meanwhile

```text
C_ram = sum_i(n_i-1)/2 = O(sqrt(d)) = o(d).
```

Thus four sign-free generator images can identify the degree-`d` x-map in a
family where the additive rational-interpolation criterion remains short by a
linear factor.  This is an information improvement, not a low-torsion one:
the product of the four orders is `Theta(d^2)`.

## Arbitrary-target decoder

The theorem is information-theoretic.  The proof-of-concept constructor uses
the one-parameter Schoof kernel family and adds one unknown target scale.

For short Weierstrass models in sufficiently large characteristic, write

```text
phi(x,y) = (R(x), c*y*R'(x)),
lambda = c^2,
R = lambda*U.
```

Then `U` is normalized to

```text
Ebar : y^2 = x^3 + (A1/lambda^2)x + B1/lambda^3.
```

If the monic kernel polynomial begins

```text
F(X)=X^s+T*X^(s-1)+...,  s=(d-1)/2,
```

Schoof's formal expansion expresses every remaining coefficient in
`K(T,lambda)`.  Modified Velu formulas give the normalized x-map `N/D`.
A sign-free sample `(u_i,z_i)=(x(P_i),x(phi(P_i)))` yields

```text
lambda*N(u_i) - z_i*D(u_i) = 0.
```

After clearing powers of `lambda`, each residual has bidegree at most `(d,d)`
in `(T,lambda)`.  When two residuals have a nonzero resultant in `T`, its
`lambda`-degree is at most `2d^2`.  Factoring that polynomial, intersecting
the specialized `T` roots from all rows, and verifying subgroup, endpoint,
degree, and map identities produces a finite verified list.

This is a restricted constructor, not yet a general fast-recovery theorem.
A chosen pair of residuals can have zero resultant or exceptional
specializations; a complete implementation must try additional rows or add
the exact differential/codomain equations.  Dense bivariate elimination is
polynomial in `d` but is not competitive with compact higher-dimensional
representations when an explicit `Theta(d)`-coefficient map is unnecessary.

## Exact evidence

The producer and separate verifier both pass.

### Genuine ordinary ascending recovery

The frozen instance is

```text
p=34651, trace=2, D_pi=-138600=(-616)*15^2,
E0: y^2=x^3+15912x+20007, conductor 15,
E1: y^2=x^3+16688x+3859, conductor 3,
d=5, primary orders=(3,7,11).
```

The unique rational degree-5 edge ascends from `E0` to `E1`.  Separate fields
of degrees `3,7,11` supply primitive Frobenius-oriented pairings whose roots
are `{1,2}`, `{2,5}`, and `{2,9}`.  The three sign-free generator rows give

```text
beta=32>20=4d,
C_ram=9<10=2d.
```

The public decoder recovered

```text
F(X)=X^2+9768X+21203,
lambda=16205.
```

Three acquisition seeds produced the same normalized candidate.  Three
executions of the same separate verifier reconstructed the pairings and, only
after the producer payloads were frozen, enumerated the unique withheld edge
and matched its kernel and x-map.  All registered mutations rejected.  These
executions share Sage and are not independent implementations.

The strongest additive baseline changes the interpretation.  All nine local
half-orbit rows give a `9 x 11` matrix of rank `9` and nullity `2`.  Imposing
the public source/target curve identity on that rational-map pencil yields a
degree-one parameter gcd and the same unique map.  Its measured solve time was
`0.006--0.011 s`, faster than the three-row decoder's `0.043--0.059 s`.
Therefore the experiment proves a strict raw-linear-interpolation rank deficit
and a compressed-generator separation, but not an acquisition or speed
advantage over a structure-aware additive baseline.  A 30-repetition
source-only ablation also recovered the same unique edge with zero rows
(median `0.00190 s`), so this fixture cannot show that self-pairing data improve
recovery.

### Arbitrary-target fixtures

| degree | field | residual bidegree | resultant degree | verified pairs |
|---:|---:|---:|---:|---:|
| 3 | `F_101` | `(3,1)` | 6 | 1 |
| 5 | `F_191` | `(5,5)` | 50 | 1 |
| 7 | `F_269` | `(7,7)` | 98 | 1 |
| 13 | `F_30029` | `(13,13)` | 338 | 1 |

The degree-13 source is

```text
E0/F_30029 : y^2=x^3+x+12,
```

with primary points of exact orders `3,5,7,11`.  The recovered data are

```text
T=321,
lambda=289,
F(X)=X^6+321X^5+28082X^4+8827X^3
     +9401X^2+17638X+10027.
```

The constructor found one algebraic pair and one verified map.  The verifier
reimplemented the recurrence with Sage power series, recovered the same pair,
checked the x-map on every rational source point, and independently enumerated
all rational degree-13 kernels, finding one matching map.  Mutating one image
x-coordinate leaves zero verified candidates.

Candidate acceptance uses only the source, marked target, degree, supplied
rows, finite-subgroup check, and target-scaling equations.  The withheld map
is used only afterward for the labeled whole-group audit and cannot remove an
algebraic candidate.

### Below-threshold counterexample

Over `F_157`, let `E:y^2=x^3+x` and let `i` be the order-four automorphism.
The endomorphisms

```text
phi=3+5i,  psi=3-5i
```

both have degree 34 and are neither equal nor negatives.  Their x-images agree
on exact-order 3 and 5 points, using opposite local sign patterns.  Here

```text
beta(3,5)=8 <= 136=4d,
deg(phi-psi)=100,
deg(phi+psi)=36.
```

This is a concrete non-uniqueness control below the theorem threshold.

Earlier supplied-row regression payload hashes (not the central ascending run):

```text
contract: c0a44da324af18de0a96388bdc87cc7c20de5e63335851f5e0cf7ac90bb0ac62
producer: ed65062be9f9cd2deef4314ea1051baf31b6605c717ed753546cd995720fd48e
verifier: d3f3a4c7419f0b88e4581a9f89aca4446d675b664ef7a16786bc88931ebbaa4b
```

## Cryptographic implications

Ramified self-pairings can reveal each primary image as

```text
phi(P_i)=+/- alpha_i Q_i.
```

The x-coordinate removes each local sign.  The balanced theorem shows that
when `beta>4d`, those nominally independent signs cannot correspond to two
different degree-`d` isogenies.  In that regime the local `2^r` ambiguity is
not information-theoretic protection.

For implementations or parameter generation, the audit should record:

1. every accessible odd ramified primary order `n_i`;
2. its torsion-field degree and pairing/DLP cost;
3. the exact or lower-bounded value of `beta(n_1,...,n_r)`; and
4. the cost and output format of the reconstruction backend.

If `beta>4d`, a verified direct Kummer decoder can avoid explicit local-root
enumeration.  This is not automatically a `2^r` runtime saving: existing
higher-dimensional methods reuse work across roots, and a replacement decoder
has different arithmetic and output costs.  Torsion construction,
extension-field arithmetic, self-pairing DLPs, and the `Omega(d log q)`
explicit-output size remain charged.

The asymptotic four-primary family illustrates the tradeoff sharply: generator
sample count is constant, additive orbit count is only `O(sqrt(d))`, and the
product-order requirement is `Theta(d^2)`.  It is potentially useful when the
protocol already exposes or cheaply supports those primary actions; it is not
a reason to treat degree-`Theta(sqrt(d))` torsion fields as free.

No current SCALLOP, PEARL-SCALLOP, SQIsign, or ECDLP break follows from the
present evidence.  The immediate value is a parameter-audit criterion and a
full-path toy interface validation, together with negative results against the
strongest tested additive baseline and a source-only zero-row baseline.

## Closest prior work and novelty boundary

- Galbraith, Gilchrist, and Robert provide the ramified self-pairing data and
  recover by an auxiliary quotient plus higher-dimensional isogenies.
- Balan, Casazza, and Edidin use the same abstract sum/difference partition in
  the complement-property characterization of real phase retrieval.  The
  isogeny-specific step is to replace spanning by torsion-subgroup capacity
  and the linear norm by the degree quadratic form.
- Castryck and collaborators' interpolation framework gives the general
  order/point-count threshold, but does not in the inspected material state
  the complementary-product sign-partition criterion.
- Bostan, Morain, Salvy, and Schost reconstruct normalized isogenies from
  endpoint data in quasi-linear time in the degree.
- Takahashi, Kudo, Fukasaku, Ikematsu, Yasuda, and Yokoyama use Schoof's
  one-parameter kernel family in algebraic isogeny recovery and explicitly
  discuss a direct one-variable variant.

No explicit antecedent for the arithmetic complementary-product criterion was
found in the public primary sources inspected as of 2026-07-20, but this is
not an absolute priority certificate.  The Schoof/Velu decoder is best treated
as the constructive backend and experimental witness, not as an independently
established novelty claim.

## Limitations

- The theorem is sufficient, not necessary, and no sharp converse is claimed.
- Pairwise coprimality and exact point orders are essential to the product
  lower bound.
- The constructor is tested only over toy prime fields and large enough
  characteristic.
- The end-to-end experiment covers one degree and one ordinary ascending
  isogeny class; it does not establish decoder scaling.
- The additive nullspace-pencil baseline recovers the same map faster on the
  toy fixture.
- The source-only zero-row baseline recovers the unique toy edge faster still.
- The dense resultant implementation is output-sensitive and has no claimed
  advantage over compact Kani/HD representations outside the balanced regime.
- Special target automorphisms and small characteristic require separate model
  handling.
- Absence from the inspected literature is not an absolute priority proof.

## Next concrete action

Build a multi-degree family of genuine ramified-orientation fixtures and
compare, on identical rows, the direct Kummer decoder, the additive
curve-identity solver, and GGR's root-enumerating Kani/theta route with shared
work, memory, torsion fields, DLPs, and output costs charged.

## Artifact paths

- `experiments/ecdlp_isogeny/iso_kernel_coefficient_scaling_decoder_contract.md`
- `experiments/ecdlp_isogeny/iso_kernel_coefficient_scaling_decoder.sage.py`
- `experiments/ecdlp_isogeny/iso_kernel_coefficient_scaling_decoder.json`
- `experiments/ecdlp_isogeny/iso_balanced_primary_threshold_sweep_result.json`
- `experiments/ecdlp_isogeny/iso_balanced_primary_threshold_sweep_verify.json`
- `experiments/ecdlp_isogeny/iso_balanced_primary_ramified_fixture_search_result.json`
- `experiments/ecdlp_isogeny/iso_balanced_primary_ramified_recovery_result.json`
- `experiments/ecdlp_isogeny/iso_balanced_primary_ramified_recovery_verify.json`
- `experiments/ecdlp_isogeny/iso_balanced_primary_ramified_recovery_seed20260721.json`
- `experiments/ecdlp_isogeny/iso_balanced_primary_ramified_recovery_seed20260721_verify.json`
- `experiments/ecdlp_isogeny/iso_balanced_primary_ramified_recovery_seed20260722.json`
- `experiments/ecdlp_isogeny/iso_balanced_primary_ramified_recovery_seed20260722_verify.json`
- `experiments/ecdlp_isogeny/iso_balanced_primary_zero_row_ablation_contract.md`
- `experiments/ecdlp_isogeny/iso_balanced_primary_zero_row_ablation.sage.py`
- `experiments/ecdlp_isogeny/iso_balanced_primary_zero_row_ablation_result.json`
- `experiments/ecdlp_isogeny/iso_kernel_coefficient_scaling_decoder_verify.sage.py`
- `experiments/ecdlp_isogeny/iso_kernel_coefficient_scaling_decoder_verify.json`
- `research/kernel_coefficient_two_row_linear_failure.md`
- `research/trace_dual_hom_recovery_scope_note.md`
