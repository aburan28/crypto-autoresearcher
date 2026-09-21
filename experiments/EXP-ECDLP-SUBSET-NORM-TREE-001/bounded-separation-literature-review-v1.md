# Bounded-separation literature review v1

## Handoff: exact contraction and locator boundary

### Claim or task

Determine whether primary literature supplies an exact three-source scalar norm
or equivalent zero locator with strict `o(B^2)` target cost, `o(B^3)` fixed
advice, exact first-witness recovery, and ordinary prime-field EC semantics.

### Status

`OPEN`, `NOVELTY-UNVERIFIED`. No exact match was located. This is a targeted
literature-match statement, not a lower bound or novelty claim.

### Assumptions

- The split source algebra has dimension `Theta(B^3)` and the D2 node degree is
  `n=Theta(B^2)`.
- Logical scalar output is distinguished from internal representation size.
- Fixed preprocessing, target work, traffic, live state, identity routes, and
  signed source provenance are all charged.
- Strict `o(B^2)` does not include `soft-O(B^2)`.

### Evidence so far

#### Special resultants and root products

- Bostan, Flajolet, Salvy, and Schost, [Fast computation of special
  resultants](https://doi.org/10.1016/j.jsc.2005.07.001), JSC 41(1), 2006,
  compute degree-`mn` composed sums/products in `O(M(mn))` under their stated
  characteristic hypotheses. With two degree-B sources, the output already
  has `B^2` coefficients. A third source produces a degree-B3 root polynomial.
  This is an exact output-linear analogy, not a strict sub-B2 scalar algorithm.
- D'Andrea and Sombra, [A Poisson formula for the sparse
  resultant](https://doi.org/10.1112/plms/pdu069), PLMS 110(4), 2015, justify
  exact product-over-roots and boundary-factor semantics, not the required
  specialization cost or witness locator.
- Jeronimo and Sabia, [Sparse resultants and straight-line
  programs](https://doi.org/10.1016/j.jsc.2017.05.005), JSC 87, 2018, show that
  dense coefficient output is not universally necessary. Their SLP bounds do
  not instantiate strict sub-B2 work for this EC norm or return source labels.

#### Tensor trains over exact fields

- Oseledets, [Tensor-Train
  Decomposition](https://doi.org/10.1137/090752286), SIAM JSC 33(5), 2011,
  gives TT storage `sum_k r_(k-1)n_k r_k`; Hadamard products multiply ranks.
  Standard practical rounding is approximate and cannot certify an exact
  finite-field zero predicate.
- Vilmart, [A Unique Normal Form for Tensor Trains over Arbitrary
  Fields](https://doi.org/10.48550/arXiv.2607.06271), arXiv:2607.06271, 2026,
  is a current preprint. It supplies exact reduction, zero-tensor testing, and
  a leading nonzero index over arbitrary fields. It does not by itself compute
  a product of all entries or locate an entry equal to zero.

For three B-sized modes and uniform exact TT rank `r`, the repository cost
inference is:

```text
state:             O(B*r^2),
coarse reduction:  O(B*r^3).
```

Thus the strict state gate needs `r=o(B^(1/2))`, and the per-reduction work gate
needs `r=o(B^(1/3))` before logarithms and circuit length. These thresholds are
an inference from the representation costs, not a rank theorem for the EC
tensor.

#### Fixed-polynomial preprocessing

- Kedlaya and Umans, [Fast Polynomial Factorization and Modular
  Composition](https://doi.org/10.1137/08073408X), SIAM J. Comput. 40(6),
  2011, give near-linear fixed-polynomial preprocessing and polylogarithmic
  exact evaluation query time in their bit model. This decisively prevents a
  universal claim that degree n forces n online coefficient reads.
- The theorem does not directly solve this interface. Evaluating at one element
  of `A_123` changes the finite-ring description size to
  `log(|K|^Theta(B^3))=Theta(B^3*log|K|)`, while coordinatewise use requires
  B3 scalar queries.
- Paterson and Stockmeyer, [On the Number of Nonscalar Multiplications
  Necessary to Evaluate Polynomials](https://doi.org/10.1137/0202007), SIAM
  J. Comput. 2(1), 1973, reduce nonscalar multiplications to `O(sqrt(n))` but do
  not remove n scalar coefficient operations or the A123 representation.
- Neiger, Rosenkilde, and Solomatov, [Generic bivariate multi-point evaluation,
  interpolation and modular composition with
  precomputation](https://doi.org/10.1145/3373207.3404032), ISSAC 2020, return
  all n outputs in quasi-linear time with an explicit `+n` term. The fixed and
  varying inputs also do not match the present target specialization.

#### New synthesis: exact TT zero locator

`CONJECTURE`, repository inference rather than a literature claim. For an exact
finite-branch tensor `G_Q in K^(d_1*d_2*d_3)`, define componentwise

```text
Z_Q = 1-G_Q^(|K|-1).
```

Fermat's identity gives `Z_Q[x]=1` exactly when `G_Q[x]=0`. Therefore an exact
TT normal form for `Z_Q` is the zero tensor iff no registered source triple
hits the finite D2 node, and its leading nonzero index is a source-triple
locator. A D2 dictionary probe then returns the remaining two signed leaves.
The root-only D2 identity route remains the charged factor scan.

This removes the logical gap between compact TT representation and zero-entry
localization. It does not solve construction cost. Computing a dense degree-N2
`G_Q` by Horner, canonical CP enumeration, or a D2 factor product already uses
`Omega(B^2)` disclosed steps. The exponentiation also needs `O(log |K|)` exact
Hadamard products and reductions. A positive result therefore requires a
fixed-node compiler for `G_Q` plus rank bounds below the thresholds above.

No located source combines that compiler, exact EC branch semantics, the TT
indicator, and signed witness recovery.

### Failure modes

- Calling BFSS output-linear work strict subquadratic.
- Applying Kedlaya-Umans with ring size `|K|` when the query element lives in
  the B3-dimensional product algebra.
- Treating approximate TT rounding as exact.
- Confusing a TT zero-tensor test with zero-entry location without constructing
  the exact Fermat indicator.
- Counting the `O(log |K|)` indicator exponentiation but omitting construction
  of `G_Q`.
- Treating a located quotient component as five signed public identifiers
  without the source registry and D2 witness lookup.

### Next concrete action

Write a zero-run paper preflight for the exact TT indicator that dimensions the
complete construction of `G_Q`, every Hadamard rank and reduction, the
`O(log |K|)` indicator chain, leading-index recovery, identity routes, and the
D2 witness lookup; reject it before implementation if total work or traffic is
not strict `o(B^2)` or exact TT rank breaches the derived thresholds.

### Artifact paths

- `bounded-separation-preflight-v3.md`
- `nested-source-norm-literature-review-v1.md`
- `root-operator-preflight-v1.md`
- `object-dimension-ledger.md`
