# P1532 R1 independent row-batch audit

## Record status

- Candidate root: `ECDLP-IDEA-003`
- Focus experiment: `P1532`
- Producer artifact:
  `ideas/artifacts/ECDLP-IDEA-003/p1532_batched_type2_label_spec.md`
- Artifact class: independent theorem-only reconstruction and scope correction
- Decision:
  `INDEPENDENT_SCOPED_AUDIT_PASS__INCONCLUSIVE__REVISE_TO_COLLISION_RESULTANT`
- Evidence scale: symbolic cost and interface audit; no experiment
- Claim labels: `model-bound`, `novelty-unverified`
- Breakthrough claim: none
- Contract authorization: none
- Solver or elliptic fixture: none

The producer's batch rectangle and rho controls reconstruct, but its output gate is
strictly stronger than Gallant recovery needs. Returning all `K` labels in row order is
sufficient, not necessary. An unordered characteristic polynomial or a direct
multiset-intersection certificate can also work if it supports exact source-index
recovery. This correction does not supply such a certificate. It closes the admitted
row-materialization lane inconclusive and reranks the weaker collision-resultant
question separately.

## Reconstructed batch rectangle

Retain the P1531 notation

```text
ell-1=A*D,                 A=ell^(1-alpha+o(1)),
|H|=D,                    K=ceil(sqrt(A)),
BASE[i]=L([a^(i*K)]P),    TARGET[j]=L([a^(-j)]Q).
```

The outer table or collision work and the inner `H` search have exponents

```text
kappa=(1-alpha)/2,        delta=alpha/2.
```

If `c_B` and `b_B` are the complete base and target batch exponents, then

```text
lambda_B=max(c_B,b_B,kappa,delta,final verification).
```

Thus strict sub-rho time requires `c_B,b_B<1/2`. At `alpha=1/2`, the producer's
hypothetical `sqrt(KD)` operation has exponent `3/8`, while `K` independent
square-root Velu evaluations have exponent

```text
kappa+alpha/2=1/2.
```

This accounting passes. Explicit rows also impose a `K`-word state floor unless they
are streamed into a charged collision procedure.

## Scope correction: rows are not logically necessary

Let `z` be a public hash of one three-coordinate tagged P1531 label into `F_p`. For a
pole-free setup one may take

```text
z_eta(R)=eta_1*L_(c_1)(R)+eta_2*L_(c_2)(R)+eta_3*L_(c_3)(R),
```

with public uniform `eta in F_p^3`. Tagged poles can instead be represented by
denominator/numerator pairs or rejected by an explicitly charged aggregate bad-setup
test. For unequal triples, one random affine hash collides with probability at most
`1/p`. Across the `K^2` cross pairs, the union bound is

```text
Pr[one false cross collision] <= K^2/p
                              = ell^(-alpha+o(1)).
```

Final scalar verification rejects every false candidate. Repetition can reduce this
error, but every repeat belongs in the cost.

For one batch side and an index set `I`, define the characteristic certificate

```text
C_(R,I)(Z)=product_(i in I) (Z-z_eta([r_i]R)).
```

The complete base and target certificates share a root exactly when the hashed label
multisets intersect. A gcd or a direct resultant can expose that intersection without
returning the rows in order. Source indices can then be recovered by recursively
testing the common root or the intersection predicate on deterministic halves. If a
size-`n` subset certificate costs `sqrt(nD)^(1+o(1))`, the geometric recovery sum is

```text
sqrt(KD) * (1+1/sqrt(2)+1/2+...) = O(sqrt(KD)).
```

Therefore a certificate family for the full set and its deterministic subdivisions is
an exact Gallant interface. A single union orbit product, checksum, or collision bit
without this source-recovery interface remains insufficient.

No such characteristic polynomial, direct resultant, or subdivision oracle is derived
here. The correction only prevents the harness from rejecting one before its costs are
examined.

## Constant-recurrence audit

Write the complete quotient sequence for one public `c` as

```text
U_j(c)=L_c([a^j]R),       0<=j<A,
```

where rows are indexed modulo `F_ell^*/H`. For a generator `R`, different quotient
rows have disjoint pole sets in the variable `c`: a pole of `U_j` is
`x([a^j h]R)` for `h in H/{+1,-1}`, and equality with a pole in row `j'` would put
`a^(j-j')` in `H`.

Consequently the `A` rational functions `U_j(c)` are linearly independent over the
constant field. Equivalently, after adjoining the required roots of unity, every
Fourier mode of this cyclic sequence is nonzero as a rational function of `c`. Any
constant-coefficient cyclic recurrence valid symbolically for the full sequence has
order at least `A`; a lower-order relation would be a nontrivial constant linear
combination of functions with disjoint poles.

This excludes the producer's low-order constant-recurrence interpretation. It does not
exclude a variable-coefficient recurrence, but such a recurrence must construct its
coefficients without already encoding the `A` row functions. Generic q-holonomic
square-root `N`-th-term algorithms do not provide that elliptic recurrence and do not
emit the required batch.

## Transposed and summation-polynomial audit

The formal row tag is not a scalar parameter over `F_p`. The multiplier `a^j` lives in
`F_ell`, while the coordinates and label values live in characteristic `p`; there is no
field embedding `F_ell -> F_p` when `ell != p`. Substituting a formal row variable into
`[a^j]R` therefore does not produce a low-degree bivariate scalar-multiplication map.

A Semaev construction can attach one explicit addition or multiplication chain to each
row, but retaining those chains leaves `K` row branches and `K*D` orbit leaves. Dense
elimination, a degree-`K*D` eliminant, or a product-ring computation is the frozen
payload control. No transposed identity in the audited sources removes this payload
while retaining row coefficients or a recoverable multiset intersection.

This is a scoped no-candidate result, not an impossibility theorem for all arithmetic
circuits.

## Balanced CRT control

If the quotient order admits a restricted balanced coprime split

```text
A=A_1*A_2,                gcd(A_1,A_2)=1,
A_1,A_2=ell^((1-alpha)/2+o(1)),
```

then Gallant's exponent decomposition may use the complete subgroups

```text
J_1=<a^(A_2)>,            J_2=<a^(A_1)>.
```

Both batches are then complete multiplicative-subgroup orbits rather than one subgroup
and one interval. This is a useful algebraic normalization for a future resultant, but
it is a restricted curve/order family and not a speedup by itself.

Replacing the `H` label by a direct label for `H*J_i` costs `sqrt(DK)` even under a
favorable square-root evaluator. Searching the remaining quotient of size `K` costs
another `sqrt(K)` queries, giving

```text
sqrt(K)*sqrt(DK)=sqrt(D*K^2)=sqrt(A*D)=sqrt(ell).
```

Thus simple subgroup nesting conserves the rho exponent. Only a joint intersection or
relative-resultant operation that avoids those independent quotient queries could use
the balanced split.

## Route dispositions

| Route | Independent disposition |
|---|---|
| Direct tagged rows | `K*D` term traffic; above rho |
| `K` square-root Velu rows | Exact rho exponent `1/2` |
| Product-ring packing | Pays `K` base-field operations per coefficient-ring operation |
| All Fourier row tags | Every mode is nonzero; materialization or hidden type-1 orientation remains |
| Constant-coefficient quotient recurrence | Exact order floor `A` from disjoint poles |
| Variable-coefficient q-holonomic recurrence | No elliptic recurrence or coefficient-construction bound supplied |
| Tagged Semaev elimination | Retains `K*D` leaves or an equivalent dense eliminant |
| Nonhomomorphic cyclic algebra | No compact encoder below the invariant-coordinate payload supplied |
| Balanced CRT subgroup nesting | Better structure, but independent quotient search is exactly rho |
| Collision-recovering multiset resultant | Semantically valid corrected interface; no operation supplied |

## Full-path decision

No audited row-producing operation has `c_B,b_B<1/2`, and no experiment is authorized.
The row-output necessity claim is corrected because Gallant only needs a recoverable
collision. The scoped disposition is

```text
INDEPENDENT_SCOPED_AUDIT_PASS__INCONCLUSIVE__REVISE_TO_COLLISION_RESULTANT
```

Exactly one next action: freeze a theorem-only P1533 collision-recovering multiset
resultant interface, including randomized compression, pole handling, deterministic
source recovery, balanced-CRT control, and complete time and memory gates; then either
derive one explicit direct resultant below rho or sign a scoped no-candidate receipt.
Do not authorize a contract, solver, or toy fixture.

This audit verifies only the P1532 scoped disposition. It is not an ECDLP algorithm, a
generic-order result, a Shoup-bound improvement, or a breakthrough.
