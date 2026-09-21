# PO-transfer-003 Result: Bielliptic Norm-Interpolation Transfer

Date: 2026-07-13

## Result

Status: `NEGATIVE RESULT / POSITIVE MECHANICAL SIGNAL / TOY-EVIDENCE / MODEL-BOUND`.

Candidate name: **Bielliptic Norm-Interpolation Transfer (BNIT)**.

BNIT constructs the split genus-2 cover

```text
C: y^2 = x^6 + A*x^2 + B
```

with elliptic quotients

```text
E1: Y^2 = U^3 + A*U + B
pi1(x,y) = (x^2,y)

E2: V^2 = W^3 + A*W^2 + B^2
pi2(x,y) = (B/x^2,B*y/x^3).
```

For a cubic `v(x)`, it pushes the principal divisor of `y-v(x)` through
`pi1`.  Interpolating `v` through a lift of `-lambda*Q` and three public
factor-base lifts couples the relation to the original ECDLP target before the
remaining quadratic is factored.

This is a real native function-field relation source and not a raw divisor-list
MITM.  It recovers the original toy target on all four cells after streaming
large-prime elimination.  It does **not** beat rho, BSGS, or `PO-transfer-002`.

## Restricted Relation Theorem

Status: `RESTRICTED THEOREM`.

Let the field have odd characteristic, let `C` be smooth, and let
`H_v(x)=v(x)^2-(x^6+A*x^2+B)` have degree six with six distinct rational
roots `r_i`.  Then

```text
sum_i pi1(r_i,v(r_i)) = O_E1
sum_i pi2(r_i,v(r_i)) = O_E2
```

when none of the `r_i` is zero for the second map.

Proof: `div_C(y-v(x))` is the six affine zeros minus the pole divisor at the
two points at infinity.  Both quotient maps send the infinity support to their
elliptic identities.  Pushforward preserves principal divisors, so the affine
images sum to the identity in each elliptic Picard group.

This theorem proves relation correctness.  It does not prove useful relation
probability or a sub-rho algorithm.

## Frozen Cells

| p | #E1 | A | B | #E2 | FB | fixture k |
|---:|---:|---:|---:|---:|---:|---:|
| 101 | 97 | 42 | 60 | 107 | 8 | 17 |
| 211 | 199 | 127 | 142 | 215 | 10 | 29 |
| 431 | 433 | 62 | 120 | 459 | 12 | 37 |
| 4099 | 4021 | 4041 | 4067 | 4135 = 5*827 | 16 | 137 |

The fixture scalar creates public `Q=kG` outside relation collection.  The
collector receives only public curve data, `G`, `Q`, factor-base points, and
known multiples of `Q`.  It computes no factor-base discrete logarithms.

## Variant Results On F_4099

| Variant | Mechanism | Kernels | Target rows | Rank | Recover | Charged/rho | Memory/sqrt(n) |
|---|---|---:|---:|---:|:---:|---:|---:|
| `003` | direct residuals only | 172,480 | 5 | 6/16 | no | 3147.35x | 1.45x |
| `003b` | retain all one-large-prime collisions | 172,480 | 238 | 16/16 | yes | 3596.16x | 103.47x |
| `003c` | pair/delete, online rank, target first | 31,184 | 15 | 16/16 | yes | 695.68x | 20.26x |
| `003d` | `003c` with cap 9 | 171,447 | 11 | 16/16 | yes | 3375.96x | 3.90x |

The direct source is memory-light but rank-deficient.  One-large-prime
elimination repairs rank but creates a large table.  Online rank plus early
stop cuts work, while a cap of nine repairs memory at the cost of nearly full
enumeration.

For comparison, `PO-transfer-002` first recovered the same `F_4099` target at
`178.04x` rho and `16.54*sqrt(n)` memory.  Thus `003c` is about `3.91x` more
charged work, and bounded-memory `003d` is about `18.96x` more charged work.

## Bounded-Cache Sweep

| Anchor cap | Rank | Recover | Charged/rho | Memory/sqrt(n) |
|---:|---:|:---:|---:|---:|
| 4 | 10/16 | no | 3392.62x | 2.48x |
| 8 | 15/16 | no | 3394.71x | 3.66x |
| 9 | 16/16 | yes | 3375.96x | 3.90x |
| 10 | 16/16 | yes | 2714.83x | 4.05x |
| 11 | 16/16 | yes | 2714.96x | 4.18x |
| 12 | 16/16 | yes | 2715.08x | 4.31x |

This cap was selected on the anchor.  It is exploratory selection evidence,
not held-out confirmation.

## Four-Cell Cap-9 Sweep

| p | Kernels | Target rows | Rank | Recover | Charged/rho | Memory/sqrt(n) |
|---:|---:|---:|---:|:---:|---:|---:|
| 101 | 204 | 5 | 8/8 | yes | 86.64x | 15.53x |
| 211 | 422 | 6 | 10/10 | yes | 86.89x | 12.48x |
| 431 | 3,706 | 7 | 12/12 | yes | 341.93x | 9.80x |
| 4099 | 171,447 | 11 | 16/16 | yes | 3375.96x | 3.90x |

The toy fit for `kernel_attempts/rank` is approximately `n^1.687`.  It mixes
different curves and factor-base sizes and is not an asymptotic claim, but it is
strongly adverse evidence against this insertion-order bounded-cache model.

## Independent Public Replay

`po_transfer_003_verify.sage` does not consume fixture secrets or factor-base
logs.  For the frozen cap-9 artifact it:

- matched the generator source hash;
- reconstructed every cubic from its four interpolation constraints;
- checked residual roots and direct rows;
- replayed both partial rows and the signed cancellation for every large-prime
  row;
- verified 46 final public rows;
- recomputed ranks `8/8`, `10/10`, `12/12`, and `16/16`;
- recovered `17`, `29`, `37`, and `137` and checked each public equation
  `kG=Q`.

The wrong-sign large-prime negative control was nonzero in every cell.  Public
verification failures were zero.

## Cost Interpretation

The reported charged value is an optimistic accounting floor for this
prototype, not a calibrated equivalence between field operations and EC group
operations.  It charges factor-base scans, interpolation kernels, public row
verification, retained matrix entries, rank tests, and large-prime anchors.
Polynomial interpolation, gcd, factorization, and square-root work is also
reported as a field-operation proxy.

The negative conclusion is robust because relation-kernel attempts alone are
already far above rho on the recovering anchor.

## Literature And Novelty Boundary

The broad algorithmic ingredients are known:

- Semaev summation polynomials characterize elliptic point-sum relations:
  <https://eprint.iacr.org/2004/031>.
- Petit, Kosters, and Messeng use rational-map factor bases and low-degree map
  decompositions for prime-field ECDLP:
  <https://christophe.petit.web.ulb.be/files/16PKC_primeECDLP.pdf>.
- Cover attacks transfer extension-field ECDLPs to Jacobians; Tian gives a
  prime-order extension-field instance:
  <https://arxiv.org/abs/2012.07173>.
- Split Jacobians and transfers between Jacobian representations are classical;
  a nearby arithmetic reference is Bruin and Doerksen:
  <https://doi.org/10.4153/CJM-2011-039-3>.

Novelty status: `OPEN`.  The checked sources did not establish that this exact
target-interpolated bielliptic sampler has appeared before, but that is not a
novelty proof.  After projection, each accepted row is a six-point elliptic
relation and may eliminate to a Semaev/Petit-style system.  BNIT is therefore a
new local candidate combination, not a claimed novel cryptanalytic algorithm.

## Narrow Negative Result

Status: `NEGATIVE RESULT`.

On the four frozen toy curves, cubic interpolation over the degree-2
bielliptic quotient, with direct residuals, one-large-prime elimination, online
rank, target-first ordering, and insertion-order bounded caches, did not beat
rho.  The bounded-memory recovering variant had adverse toy scaling.

This does not rule out other function families, batch residual sieves,
double-large-prime graph cycles, Prym-assisted filters, `(3,3)` split
correspondences, or other cover/Jacobian transfers.

## Next Three Theories

1. `CONSERVATIVE`: add double-large-prime graph cycles with external sorting or
   distinguished endpoints; test whether rank can be recovered at `O(sqrt(n))`
   total work without storing all partial rows.
2. `REPRESENTATION CHANGE`: construct an explicit Kani-Rosen `(3,3)` split
   correspondence and search for a native function family whose pushed
   residual degree is lower than BNIT's quadratic residual.
3. `HIGH-RISK`: replace triple enumeration by a Plucker/incidence sieve.  For a
   fixed target lift, target plus four cover points lie on one cubic exactly
   when their rows `(1,x,x^2,x^3,y)` are dependent.  Hash pairwise 2-planes in
   the four-dimensional quotient by the target row and search for orthogonal
   wedge pairs, aiming to turn `B^3` interpolation into a batch `B^2` relation
   source.

Priority: theory 3, because it attacks the measured bottleneck rather than only
moving the time/memory tradeoff.

## Handoff: PO-transfer-003 BNIT branch

### Claim or task

Construct and test a native correspondence relation source that couples to the
original prime-field target without a divisor MITM table.

### Status

NEGATIVE RESULT

### Assumptions

- controlled prime-order toy curves only;
- public target and public factor base;
- optimistic charged floor compared with rho;
- no deployment or novelty claim.

### Evidence so far

- native principal-divisor relations verified on both elliptic quotients;
- target recovery publicly replayed on four toy sizes;
- bounded-memory anchor recovery at `3.90*sqrt(n)`;
- every recovering variant remains far above rho;
- bounded-cache attempts-per-rank trend is adverse.

### Failure modes

- cubic tuple enumeration dominates;
- one-large-prime rank repair trades time for memory;
- the projected relation may collapse to known six-point Semaev/rational-map
  structure;
- cap 9 was selected on the anchor rather than held out.

### Next concrete action

Implement `PO-transfer-004` as a Plucker-pair batch incidence sieve for the
target-plus-four-point co-cubic condition, with random-incidence and planted
relation controls, then charge pair-table memory, rank, and target recovery
against rho and BNIT.

### Artifact paths

- `research/PO_transfer_003_contract.md`
- `research/PO_transfer_003b_contract.md`
- `research/PO_transfer_003c_contract.md`
- `research/PO_transfer_003d_contract.md`
- `experiments/ecdlp_isogeny/po_transfer_003_bielliptic_norm_interpolation.sage`
- `experiments/ecdlp_isogeny/po_transfer_003_verify.sage`
- `experiments/ecdlp_isogeny/po_transfer_003_result.json`
- `experiments/ecdlp_isogeny/po_transfer_003b_result.json`
- `experiments/ecdlp_isogeny/po_transfer_003c_result.json`
- `experiments/ecdlp_isogeny/po_transfer_003d_result.json`
- `experiments/ecdlp_isogeny/po_transfer_003d_verify.json`

