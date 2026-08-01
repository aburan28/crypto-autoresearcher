# IDEA-121 Translated-Product Common-Norm V3 Independent Audit

Status: `PASS_SCOPED_NEGATIVE_AND_SOURCE_JET_IDENTITY__NO_LOCATOR__NO_RUN`

Audited producer:

```text
ideas/artifacts/ECDLP-IDEA-121/translated_product_common_norm_v3.md
SHA-256 ce24397ea1686d081dac51b790fcfdf09f17e0a714dc0e8fef399fbb97c2d551
```

This is a theorem-only independent reconstruction. It does not execute a
contract, solver, fixture, timing run, relation campaign, factor-log solve,
target descent, or ECDLP instance.

## 1. Independent reconstruction

Set `M=B^2` and regroup the six coloured lists as

```text
X = T-A_1,
Y = A_2+A_3,
Z = A_4+A_5.
```

All three occurrence decks have size `M`. A campaign row is exactly
`x+y+z=O`. In the additive-line control,

```text
C_(Y,Z)(U)
  = Res_V(f_Y(V),(-1)^M f_Z(-U-V))
  = product_(y,z)(U+y+z).
```

Hence `gcd(f_X,C_(Y,Z))` has precisely the participating `X` endpoints. On the
curve, the coordinate-free object is the effective divisor

```text
gcd_divisor(X,[-1]_*mu_*(Y x Z)),
```

so the producer's correction does not assume a nonexistent global additive
coordinate on `E`.

For occurrence multiplicities, independent local valuation gives

```text
ord_x(C_(Y,Z)) = sum_(y+z=-x)m_Y(y)m_Z(z),
ord_x(gcd)      = min(m_X(x),ord_x(C_(Y,Z))).
```

The endpoint gcd therefore cannot encode all source-row multiplicity by itself.

## 2. Source-jet check

Perturb each occurrence-local zero factor by

```text
s_0+c_Y(y)s_Y+c_Z(z)s_Z.
```

At fixed participating endpoint `x`, all nonzero factors are units. The first
nonzero marker-Hasse form is consequently the unit times the product of these
linear marker factors over exactly the source pairs above `x`. For a simple
fibre, dividing the `s_Y` and `s_Z` derivatives by the `s_0` derivative returns
the two codes. For a multiple fibre, factoring the first nonzero homogeneous
form returns the multiset of code pairs and multiplicities.

This argument is valid only after splitting folded x-coordinate sign branches
into the frozen complete signed charts. The producer now states that condition.
The identity is exact; constructing it for the unknown participating endpoints
remains the missing operation.

## 3. Degree and represented-dimension check

Independent exponent substitution gives:

```text
deg f_X = deg f_Y = deg f_Z = M=B^2,
deg C_(Y,Z) = M^2=B^4,
dim K[U,V]/(f_X,f_Y) = M^2=B^4.
```

Bostan-Flajolet-Salvy-Schost is quasi-linear in the full composed-sum output
degree, so its positive bound is `B^(4+o(1))` here. Moroz-Schost with
truncation order and input degree both `M` is also soft-`O(M^2)=B^(4+o(1))`.
Neither result is an output-sensitive intersection algorithm.

The original P1513 presentation has two degree-`B^3` norms rather than the
degree-`B^4` pair-pair sum divisor. The producer correctly treats the
three-pair normal form as an exact identity but a worse standard expansion.

## 4. Newton and logarithmic-derivative mutation check

Let `D=M^2`, `f_X=U^M-1`, `R_0=U^D-1`, and `R_1=U^D`. Since `M|D` and the
campaign characteristic satisfies `p>D`, the power sums of the roots of both
`R_0` and `R_1` vanish for orders `1,...,D-1`. Nevertheless,

```text
gcd(f_X,R_0)=f_X,
gcd(f_X,R_1)=1.
```

Thus a short generic Newton prefix does not determine the desired intersection.
The same pair has logarithmic derivatives agreeing at infinity through the
short prefix while the gcds differ. This is only an interface mutation: it is
not asserted to be an elliptic norm pair or an unrestricted lower bound.

The double-pole characterization of
`(N_T'/N_T)(N_F'/N_F)` is also correct for squarefree inputs. Extracting its
repeated-pole denominator remains an unsupplied rational-reconstruction/gcd
operation.

## 5. Low-rank update check

On the squarefree endpoint quotient, multiplication is diagonal over a
splitting field. The difference between target-translated multiplication
operators has one diagonal entry `q(y+c)-q(y)` per endpoint. For generic deck,
nonzero shift, and product `q`, all but at most a lower-dimensional exceptional
set are nonzero, so the rank is `M=B^2`. This verifies the producer's statement
only for the natural quotient/multiplication-matrix realization. It is not a
lower bound against an exceptional elliptic representation.

## 6. Source-unranking and target-query check

Given only `Theta(B)` endpoint roots, scanning one `M=B^2` pair deck per root
costs `B^3`. The direct marked quotient has dimension
`B*M=B^3`. Therefore the regrouped equation-(13) gcd is not source-complete
unless its locator carries the marker Hasse form during the recurrence.

For a fresh target, `|X_Q|=B`. The same explicit scan and standard quotient
again cost `B*M=B^3`, materializing `Y+Z` costs `B^4` setup, and the natural
target update has rank `B^2`. None meets the frozen `B^(5/4)` query cap.

This does not refute a source-aware P1513 algorithm that works directly on the
two original transition circuits. It rejects only crediting an endpoint gcd or
a batch-only identity as that algorithm.

## 7. Literature and scope audit

The checked primary references support the producer's comparisons:

- composed sums are fast in their full degree-`mn` output;
- truncated resultants cost soft-`O(kd)` in the stated regime;
- current 3SUM-indexing improvement applies at state at least about
  `n^(3/2)`, while this campaign grants `n^(9/8)` for `n=M`;
- current unknown/preprocessed-universe 3SUM controls retain quadratic
  preprocessing;
- generic circuit-GCD theorems do not construct the two P1513 norm circuits;
  and
- the 2026 sparse-GCD hardness result concerns arbitrary sparse monomial
  inputs, not this fixed elliptic family.

The producer explicitly preserves specialized product circuits,
determinant-value-sensitive algorithms, nonhomomorphic data structures,
special deck families, and unrestricted circuit/cell-probe models. The
negative is therefore scoped to the named representations.

## 8. Mutation requirements

The receipt must be rejected if any successor:

1. treats the degree-`B^4` composed sum as a degree-`B` output;
2. counts one operation in the `B^4` tensor quotient as one base-field
   operation;
3. infers an arbitrary gcd from only `B` generic Newton or log-derivative
   moments;
4. applies Woodbury without proving a sublinear-rank elliptic update;
5. returns an endpoint gcd while omitting multiplicity or the marker Hasse
   form;
6. charges the known-target batch identity as a `B^(5/4)` fresh-target query;
7. cites sparse-GCD hardness as an elliptic circuit lower bound; or
8. presents the exact support/source-jet identities as an ECDLP speedup.

## 9. Independent decision

```text
coordinate-free translated-product identity: pass
multiplicity calculation:                     pass
simple/multiple source-jet calculation:        pass
degree and quotient exponents:                 pass
Newton/log-derivative mutation:                pass in generic interface
natural Woodbury rank control:                 pass in stated model
post-hoc source cost:                          B^3, fail
fresh-target standard recurrence:              absent
passing campaign locator:                      absent
complete ECDLP path:                           absent
independent disposition:                       terminal scoped inconclusive
breakthrough:                                  none
```

The producer may be indexed as a hash-bound scoped negative and exact
source-jet identity. It does not justify P1554, an experiment, or promotion of
`ECDLP-IDEA-121`.
