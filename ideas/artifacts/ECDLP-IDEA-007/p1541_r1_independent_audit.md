# P1541 R1 independent Miller S-unit support-coset audit

## Status and claim boundary

- Record type: independent theorem-only audit
- Root hypothesis: `ECDLP-IDEA-007`
- Candidate: `P1541`
- Claim: `CLM-P1541-S-UNIT-SUPPORT-COSET-DECODER`
- Evidence scale: exact divisor-class, lattice, counting, and differential statements;
  no experiment
- Contract state: no contract was drafted, approved, revised, or executed
- Breakthrough claim: none
- Disposition:
  `INDEPENDENTLY_VERIFIED_SCOPED_NO_GO__SUPPORTED_PRINCIPAL_DIVISORS_ARE_THE_ABEL_JACOBI_KERNEL__MOVING_TARGETS_ARE_AFFINE_KERNEL_COSETS__ANCHORED_FULL_KERNEL_REVEALS_FACTOR_LOGS__MILLER_PROGRAMS_CONSUME_A_KNOWN_COSET_REPRESENTATIVE__CANDIDATE_MASS_BOUND_RECONSTRUCTS__CARTIER_DLOG_LOSES_AN_INVISIBLE_P_MULTIPLE_DIVISOR_CLASS__EVALUATION_LINEARIZATION_REQUIRES_FIELD_LOGS__NO_STRUCTURED_DECODER__INCONCLUSIVE`

The producer's exact kernel, affine-coset, full-kernel, Miller-program, and
candidate-mass statements reconstruct. Independent review also instantiates the most
plausible algebraic escape: logarithmic differentials and Cartier invariance can
linearize residues in characteristic `p`, but residues see a divisor only modulo `p`.
The invisible `p`-multiple divisor class carries the original prime-to-`p` syndrome.

No target-independent operation is supplied that outputs one admissible affine-coset
representative without known support, candidate enumeration, complete factor-log state,
a generic group decomposition, or another order-`N` DLP. P1541 is therefore terminal
inconclusive within this scope. This is not a lower bound against every coordinate-aware
function-field decoder.

## Hash-bound inputs

- `ideas/ECDLP-IDEA-007_miller_s_unit_descent_hypothesis.md`:
  `f87ad5d20669dc6e00eb9ab935d3945444999f899555caf4646da3fc7cfd74a0`
- `ideas/artifacts/ECDLP-IDEA-007/p1541_s_unit_support_coset_gate.md`:
  `1d6ded9cdeedc411eda8d22c4c1b05c8fe1ed9409191e4f6ed0788d75471c7c5`
- `ledger/H-FB-001.yaml`:
  `5c63043f9f97e38a15aeb93c755bd9c4316884e45331ba583f027f3467d90f95`
- `ledger/EV-FB-001.yaml`:
  `2165d310ff41b9d575f7427ecc8465adcff391ed4ba11faaab8ab8ceba4f3f5b`
- `ledger/H-REP-001.yaml`:
  `55fa62651d57b3bd860c1e15ec60657ad5d502874d813f0d0e1288ff7ce6b483`

## Independent reconstruction of the kernel theorem

Let `E/F_p` be an elliptic curve with identity `O`, let `G=<P>` have prime order
`N`, and choose nonzero public support points `F_i=[a_i]P`. The degree-zero divisor

```text
D(e)=sum_i e_i*((F_i)-(O))
```

maps under `Pic^0(E)~=E` to

```text
theta(e)=sum_i [e_i]F_i.
```

Abel's theorem gives the biconditional

```text
D(e) is principal  iff  theta(e)=O.
```

Thus the fixed-support principal-divisor lattice is exactly

```text
L=ker(theta:Z^B -> G).
```

Any nonzero `F_i` generates the prime-order group, so `theta` is surjective and

```text
Z^B/L ~= Z/NZ,
[Z^B:L]=N.
```

For a full-rank integer basis matrix of `L`, the absolute determinant is therefore
`N`. Modulo constants, functions with divisors in `L` are precisely the rational
fixed-support S-units. These identities are representation independent.

## Independent reconstruction of the moving-target coset

For `R=[r]P`, consider

```text
D_R(e)=(R)-(O)+D(e).
```

Its Abel-Jacobi image is `R+theta(e)`, so

```text
D_R(e) is principal  iff  theta(e)=-R.
```

Since `theta` is surjective, a solution exists. If `e_0` is one solution, then

```text
{e:D_R(e) is principal}=e_0+L.
```

This proves the producer's key distinction. The precomputed S-unit group is the
homogeneous kernel. The moving-target functions are a torsor over that group.
Multiplication by a fixed-support S-unit changes `e_0` by an element of `L`; it cannot
derive `e_0` from the target syndrome.

The simplest specialization displays the circularity without proving a lower bound.
With support `{P}`, a decoder for unrestricted coefficients must output

```text
e=-r mod N
```

from `R=[r]P`. That is the ECDLP. A decoder restricted to a larger special support or
bounded coefficient family might exploit more structure, but that structure and its
cost are the entire candidate operation.

## Anchored complete-kernel theorem

Include `F_0=P` and define

```text
Theta:Z^(B+1) -> G,
Theta(e_0,...,e_B)=[e_0]P+sum_i [e_i]F_i.
```

Let `L_P=ker(Theta)`. A full integer basis for `L_P` gives the quotient map
`Z^(B+1)/L_P ~= Z/NZ` by Smith normal form. Any quotient isomorphism differs by
multiplication by a unit `c mod N`. The image of the first standard basis vector is
`c`, so rescaling it to `1` fixes the ambiguity. The remaining standard basis vectors
then map to

```text
a_i=log_P(F_i) mod N.
```

Hence complete anchored S-unit-kernel construction reveals all factor-base logarithms
with polynomial postprocessing in the explicit basis size. Its construction, output,
coefficient growth, Smith form, and storage are already factor-log preprocessing.

This theorem does not apply to a partial sampled relation set. A partial set remains
valid evidence only after its collection cost, rank, dependencies, and separate target
descent are charged.

## Miller programs reconstruct after support is known

The standard addition function for points `A,B` has divisor

```text
(A)+(B)-(A+B)-(O).
```

Once the multiset represented by `D_R(e)` is known to sum to `O`, an addition tree
composes these functions into a straight-line program whose divisor is `D_R(e)`.
Replaying the elementary divisors verifies the program, every multiplicity and vertical
exception, and the terminal group relation.

This is exact and useful, but the program consumes the coefficient vector and addition
tree. It does not select the leaves or solve `theta(e)=-R`. Different addition chains
for the same divisor change construction constants and representation size without
changing the affine coset or its witness density.

The 2024 publication of Miller's short-program manuscript confirms this prescribed-
divisor interface. It supplies no hidden-support decoder.

## Candidate-mass theorem

Let `C subset Z^B` be a finite target-independent admissible coefficient family and

```text
M_R=|{e in C:theta(e)=-R}|.
```

Each `e` contributes to exactly one target `R=-theta(e)`. Therefore

```text
sum_(R in G) M_R=|C|,
E_R[M_R]=|C|/N.
```

Markov's inequality at threshold one gives

```text
Pr_R[M_R>=1] <= min(1,|C|/N).
```

This applies identically to uniform relation inputs and to `Q+[t]P` for uniform blind
`t`, because the latter is uniform in `G`. For vectors of support at most `k` and
nonzero coefficients in `[-H,H]`,

```text
|C| <= sum_(j=0)^k binom(B,j)*(2H)^j.
```

The theorem bounds witness availability, not decoding work. When `|C|>=N`, many
witnesses may exist. A compact structured decoder might locate one without enumerating
`C`; no unconditional query lower bound is inferred.

## Independent logarithmic-differential route screen

### The apparent linearization

For a nonzero rational function `f` in characteristic `p`,

```text
omega=dlog(f)=df/f
```

has residue

```text
res_T(omega)=ord_T(f) mod p
```

at every point `T`. Logarithmic differentials are Cartier fixed, and standard Cartier
theory characterizes them locally in the etale topology. One might therefore try to
choose unknown residues at `R,F_1,...,F_B,O`, solve linear or semilinear Cartier
conditions, and read the support coefficients without a combinatorial search.

This is a mechanism-distinct enough route to audit. It does not survive the exact
divisor-output gate.

### Invisible `p`-multiple correction

Even grant that the computed differential is the global `dlog(f)` of a rational
function. Choose integral representatives of its visible residues and call their
degree-zero divisor `D_res`. The complete divisor has the form

```text
div(f)=D_res+p*D_hidden
```

for an integral degree-zero divisor `D_hidden`; points with multiplicity divisible by
`p` are invisible to every residue. Since `div(f)` is principal,

```text
[D_res]+[p]*[D_hidden]=0 in Pic^0(E).
```

In the generic prime-to-characteristic lane, `gcd(p,N)=1`, so multiplication by `p` is
an automorphism of `G`. For every visible target syndrome in `G`, there is a unique
`N`-primary class

```text
[D_hidden]=-[p^(-1)]*[D_res].
```

The hidden correction can therefore absorb the entire ECDLP class. Cartier invariance
of residues does not imply `[D_res]=0`, and a differential with visible residue `1` at
`R` does not prove an exact principal divisor on the frozen support.

Requiring `D_hidden=0`, or reconstructing and cancelling it, restores the original
support-coset problem. Bounding visible residues below `p` does not help unless every
invisible point and multiplicity in the complete divisor is also excluded and verified.
That exclusion is not supplied by the local Cartier condition.

This is a prime-to-`p` scope statement. Anomalous `p`-primary groups and formal-log
phenomena remain separate positive controls and are not generic prime-field evidence.

## Other implicit-decoder route screens

### Evaluation codes and multiplicative syndromes

Evaluating precomputed S-units at public places maps an exponent vector to products

```text
prod_j g_j(T)^(z_j) in F_(p^k)^*.
```

Turning these products into linear equations requires finite-field discrete logarithms
or an equivalent character label. Without labels they can verify a proposed exponent
vector but do not output one. Favorable small embedding degree is a charged
Frey-Ruck/MOV transfer, not a generic-prime assumption.

### Riemann-Roch interpolation

Given the complete divisor bounds or chosen multiplicities, Riemann-Roch linear algebra
can construct the corresponding function space and test principality. If support points
or multiplicities are unknown, selecting their vanishing conditions is the original
affine-coset/decomposition problem. Materializing every supported condition restores the
candidate mass or an existing summation-polynomial/source table.

### Generic lattice and subset-sum solvers

The kernel has determinant `N`, and a target asks for an inhomogeneous coset vector.
LLL, BKZ, CVP, nearest-plane, meet-in-the-middle, generalized birthday, and
summation-polynomial solvers are controls unless a point-derived lattice geometry proves
a new complete exponent. A homogeneous short vector is a relation, not a target coset
representative.

### Generic-group walk

The public group operation supplies a verification oracle for `theta(e)=-R`. A rho walk
over coefficient states locates collisions at exponent one half. Shoup's lower bound
applies to that generic oracle route. It does not rule out additional coordinate-aware
function-field operations; P1541 supplies none that survive the screens above.

## Complete relation-to-descent cost

Retain the producer notation:

```text
B=N^beta,
setup=N^c,
one decoder attempt=N^u,
reciprocal relation and target densities=N^delta,N^delta_t,
verification=N^v,
stored state=N^s.
```

The optimistic sparse path is

```text
lambda=max(c,beta+u+delta,2*beta,beta+v,u+delta_t,v),
mu=max(s,beta).
```

Dense factor-log rows replace `2*beta` by `3*beta`. For a frozen family
`|C|=N^(gamma+o(1))`, the candidate-mass theorem gives

```text
delta,delta_t >= max(0,1-gamma).
```

This does not add an enumeration term automatically. Any actual decoder must report its
construction and query term. Complete anchored-kernel construction is charged in `c`
and `s`; finite-field label recovery is charged in `u` or `c`; hidden Cartier divisor
recovery is charged as target support output.

No explicit decoder supplies values for these terms with `lambda,mu<=0.45`. The current
hypothesis's instruction to draft a toy contract would test prescribed-divisor
construction and generic support solvers rather than a specified mechanism-new decoder.

## Literature boundary

1. Victor S. Miller, *Short Programs for Functions on Curves: A STOC Rejection*,
   <https://doi.org/10.4230/LIPIcs.FUN.2024.34>. This is the prescribed-divisor
   short-program control.
2. Pierrick Gaudry, *Index calculus for abelian varieties of small dimension and the
   elliptic curve discrete logarithm problem*,
   <https://doi.org/10.1016/j.jsc.2008.08.005>. This is the divisor-decomposition and
   factor-base control.
3. Gerhard Frey and Hans-Georg Ruck, *A remark concerning m-divisibility and the
   discrete logarithm in the divisor class group of curves*,
   <https://doi.org/10.1090/S0025-5718-1994-1218343-6>. This is the pairing and
   finite-field transfer control.
4. Pierre Cartier's operator and the logarithmic de Rham sequence are standard; the
   local fixed-form boundary is represented by the exact Cartier sequence in
   Milne-style flat/etale cohomology treatments. The audit uses only the elementary
   global consequence `res_T(df/f)=ord_T(f) mod p` and explicitly grants global
   integrability before exposing the hidden-divisor obstruction.
5. Victor Shoup, *Lower Bounds for Discrete Logarithms and Related Problems*,
   <https://www.shoup.net/papers/dlbounds1.pdf>. This controls the group-oracle route,
   not every coordinate-aware function-field algorithm.

No cited source or audited artifact supplies the required implicit target support-coset
decoder. Novelty of such a future operation is unverified.

## Independent decision

The P1541 review trigger is satisfied within its stated scope:

- the Abel-Jacobi kernel, index-`N`, affine-coset, anchored Smith-form, Miller-program,
  and candidate-mass statements reconstruct;
- full-kernel preprocessing is correctly charged as factor-log state;
- the strongest explicit residue/Cartier linearization loses an invisible `p`-multiple
  divisor whose class carries the original prime-to-`p` syndrome;
- evaluation linearization transfers to a finite-field DLP, and Riemann-Roch, lattice,
  subset-sum, summation-polynomial, and generic walks retain their known support-search
  costs; and
- no exact decoder returns a target coefficient vector with complete sub-rho costs.

P1541 is terminal inconclusive. IDEA-007 remains open only for a mechanism-new
inhomogeneous decoder outside the audited classes. No contract, implementation, curve
fixture, S-unit basis, lattice run, relation campaign, factor-log solve, or blind descent
is authorized by this receipt.

## Exactly one next action

Rerank outside fixed-support S-units, Miller prescribed-divisor programs,
logarithmic-differential residues, generic lattice/subset-sum decomposition, pairing
evaluation, and prior elliptic-net/orbit families. Admit one successor only if it names
an exact mechanism-distinct construction or degree operation with a complete
factor-base-to-target path and sub-rho cost gate.

