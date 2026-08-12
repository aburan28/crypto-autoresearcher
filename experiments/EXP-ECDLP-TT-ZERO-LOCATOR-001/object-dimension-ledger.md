# Direct five-source TT object-dimension ledger

All dimensions are over `K=F_(p^2)` unless stated otherwise. `B` is the number
of registered signed public point identifiers, `q=Theta(B^5)` is the subgroup
order, `rho_k` is TT cut rank, and all target gates are strict.

| Object | Logical dimensions | Target-dependent | Explicit representation and cost | Status |
|---|---:|---|---|---|
| Signed point registry | `B` identifiers and projective triples | no | `Theta(B)` fixed field words | allowed fixed input |
| Five-mode index domain | `B^5` ordered tuples | no | implicit only | full materialization rejected |
| Broadcast input coordinate | `B x 1 x 1 x 1 x 1`, or a mode permutation | no | rank-one TT, `Theta(B)` words per coordinate/mode | exact |
| Complete five-point sum `(X:Y:Z)` | `B^5` components | no | fixed arithmetic circuit; CP rank bounded by constants `C_X,C_Y,C_Z` | exact existence bound |
| Projective equality scalar `g_Q` | `B^5` components | yes, `O(1)` target scalars | CP/TT rank at most constant `R_0` before the indicator | exact |
| Frobenius conjugate `g_Q^p` | `B^5` components | yes | coefficient conjugation; same TT ranks | exact |
| Norm tensor `h_Q=g_Q*g_Q^p` | `B^5` components | yes | raw Hadamard cut ranks at most `R_0^2` | exact upper bound |
| Exponent-chain state | `B^5` components per state | yes | `Theta(log p)` Hadamard gates; cut ranks may reach ambient `B,B^2,B^2,B` | open/fatal risk |
| Raw product of rank-`r` TT operands | order five | yes | ranks at most `r^2`; `O(B*r^4)` core words | charged before reduction |
| Exact normalizer transcript | algorithm-dependent | yes | must include pivots, rank factorizations, reads, writes, and peak raw cores | open |
| Boolean indicator `Zcal_Q` | `B^5` bits represented in `K` | yes | final `rho_k=m_(k,Q)`, the number of matching partial sums at cut `k` | restricted theorem |
| Final exact TT cores | five cores | yes | `B*(rho_1+rho_1*rho_2+rho_2*rho_3+rho_3*rho_4+rho_4)` words | compact only if rank products pass |
| Generic entry-oracle TT skeleton | queried components | yes | exact arbitrary sparse recovery can require `B^5` queries even at rank one | model-bound rejection |
| Suffix spaces and prefix tests | at most five levels and `5B` children | yes | polynomial in adjacent TT ranks; exact schedule required | open accounting |
| Positive witness | five registry identifiers | yes | `O(1)` identifiers plus independent EC replay | required output |
| Negative certificate | canonical zero cores or equivalent | yes | at least final core and normalization certificate size | open accounting |
| Pair-sum fixed table | up to `B^2` entries | no or target-shifted | reaches the strict online/state boundary if exposed per target | baseline/boundary |
| Triple-sum fixed table | up to `B^3` entries | no | not strict `o(B^3)` advice; equality at the boundary is insufficient | rejected by strict advice gate |

## Required cumulative gates

```text
offline advice and workspace = o(B^3),
sum target field operations  = o(B^2),
sum target words transferred = o(B^2),
peak target live words       = o(B^2),
success probability and supported targets reported separately.
```

Passing final-core storage alone is insufficient. The cumulative ledger must
include every intermediate Hadamard core, exact normalizer, suffix basis,
prefix-child test, certificate, and independent replay.
