# P1511 scoped-negative independent audit

Status: `PASS_SCOPED_P1510_PRODUCT_GRAMMAR_NEGATIVE`

This is a non-run theorem-audit receipt. It independently checks
`p1511_factorized_semijoin_derivation.md`; it is not an approved experiment, does not
claim a lower bound for arbitrary arithmetic circuits, and does not change the generic
ECDLP state of the art.

## Audited claim

The exact IDEA-117 fingerprint instantiates one source-marked bounded-degree
pair-resultant leaf for each `(target,i,j)` on the A2 side and each `(k,l,m)` on the A3
side. For `s=Theta(r)` targets and a factor base of size `r`, the unfolded grammar has

`s*r^2 + r*r^2 = Theta(r^3)`

labelled leaf occurrences. Generating or explicitly serializing those occurrences costs
`Omega(r^3)` words, or `Omega(r^3 log r)` bits when source labels are charged. Streaming
may reduce peak memory and does not require a literal persistent backpointer per leaf;
the scoped lower bound is on generation/traffic and therefore setup time, not on
unconditional peak memory.

On the frozen family `q=Theta(r^5)`, Pollard rho costs `Theta(r^(5/2))`. Thus the
unfolded input/rho ratio is `Theta(sqrt(r))`, and the declared grammar fails before gcd,
factorization, rank, or target descent.

## Algebra checks

For polynomials over `F_p[W]`, resultant multiplicativity gives

`Res_V(product_i a_i, product_j b_j) = product_(i,j) Res_V(a_i,b_j)`.

The equality justifies the pair-resultant product grammar. It does not imply that an
arbitrary equivalent arithmetic circuit must expose every leaf.

Before identifying common factors with accepted semijoin keys, each endpoint polynomial
must be squarefree-normalized and stripped of known-return, exceptional-denominator, and
nonaccepted-support factors. Under the random-support campaign model, the accepted batch
gcd degree is expected to be `Theta(r)` after those filters. The cubic unfolded-leaf
generation floor occurs before filtering and is not removed by that normalization.

If the normalized gcd has degree `g`, the corresponding Sylvester map has corank `g`;
a marked determinant vanishes to order at least `g`. Consequently a constant-order
marker truncation cannot expose an expected `g=Theta(r)` batch without first isolating
the factors. This is a secondary obstruction; the cubic generation floor is already
decisive for the declared grammar.

## Exact deterministic synthetic control

For each `r in {4,6,8,12,16,24,32}`, work over `F_65537`. Define A-side labelled roots

`a(t,i,j) = 1 + t*r^2 + i*r + j`

for `0<=t,i,j<r`. Define the K-side root at `(k,0,0)` to be `a(k,0,0)`. Enumerate every
other `(l,m)!=(0,0)` by

`rank(l,m) = l*r + m - 1`

and define

`b(k,l,m) = r^3 + 1 + k*(r^2-1) + rank(l,m)`.

All A roots are distinct. All nonshared K roots are distinct and exceed every A root.
The maximum root at `r=32` is `2*r^3-r=65504<65537`. Hence the two monic products have
degree exactly `r^3`; their squarefree gcd consists exactly of the `r` roots
`a(k,0,0)`; and every common root has the unique labelled source pair
`((k,0,0),(k,0,0))`.

| `r` | Leaves/degree per side `r^3` | GCD degree | Thin control `r^2` | Leaf/rho ratio `sqrt(r)` |
|---:|---:|---:|---:|---:|
| 4 | 64 | 4 | 16 | 2.000 |
| 6 | 216 | 6 | 36 | 2.449 |
| 8 | 512 | 8 | 64 | 2.828 |
| 12 | 1,728 | 12 | 144 | 3.464 |
| 16 | 4,096 | 16 | 256 | 4.000 |
| 24 | 13,824 | 24 | 576 | 4.899 |
| 32 | 32,768 | 32 | 1,024 | 5.657 |

These equalities are direct consequences of the displayed injective root maps; no
probabilistic or numerical assumption is needed. Expanding the products would require
`r^3+1` coefficients per side, but that is a dense-route peak-state statement, not a
peak-memory lower bound against streaming implementations.

## Independent verdict

Two independent read-only reviews agree that the exact IDEA-117 arm is scoped-falsified:

1. the unfolded P1510 grammar has a source-labelled `Theta(r^3)` generation/traffic
   floor;
2. `Theta(r^3)/Theta(r^(5/2))=Theta(sqrt(r))` grows;
3. dense batch gcd, remainder trees, quotient modules, and all surface-pair spellings do
   not erase their charged input; and
4. the deterministic planted-root family checks exact degree, source recovery, and the
   scope of the argument.

This closes only the explicitly instantiated P1510 product-circuit representation. A
target-uniform or succinct object constructed before pair-resultant leaf emission is a
mechanism-new representation and requires a new idea ID, fingerprint, contract, and
full rho/BSGS audit.
