# Direct five-source TT object-dimension ledger v4

All dimensions are over `K=F_(p^2)` unless stated otherwise. `B` is the number
of registered signed public point identifiers, `q=Theta(B^5)` is the subgroup
order, `rho_k` is TT cut rank, and all target gates are strict. Canonical byte
counts use `b_K=2*ceil(log2(p)/8)` bytes per uncompressed `K` element plus
metadata.

| Object | Logical dimensions | Target-dependent | Explicit representation and cost | Status |
|---|---:|---|---|---|
| Signed point registry | `B` identifiers and projective triples | no | `Theta(B)` fixed field words | allowed fixed input |
| Five-mode index domain | `B^5` ordered tuples | no | implicit only | full materialization rejected |
| Broadcast input coordinate | `B x 1 x 1 x 1 x 1`, or a mode permutation | no | rank-one TT, `Theta(B)` words per coordinate/mode | exact |
| Complete five-point sum `(X:Y:Z)` | `B^5` components | no | four left-associated calls to RCB Algorithm 1; CP rank bounded by constants `C_X,C_Y,C_Z` | exact bound on odd-order subgroup |
| Projective equality scalar `g_Q` | `B^5` components | yes, `O(1)` target scalars | CP/TT rank at most constant `R_0` before the indicator | exact |
| Target `g_Q` construction | bound RCB cores plus equality residual | yes | charge `W_g,T_g`, core writes, and target scalars | required resource term |
| Frobenius conjugate `g_Q^p` | `B^5` components | yes | coefficient conjugation; same TT ranks; one full core read and write | exact and charged |
| Norm tensor `h_Q=g_Q*g_Q^p` | `B^5` components | yes | raw Hadamard cut ranks at most `R_0^2` | exact upper bound |
| Exponent-chain state | `B^5` components per state | yes | `Theta(log p)` Hadamard gates; cut ranks may reach ambient `B,B^2,B^2,B` | open/fatal risk |
| Raw Hadamard stage `j` | order five | yes | raw bonds `pi_(j,k)=u_(j,k)*v_(j,k)`; dense allocation `S_j=B*(pi_1+pi_1*pi_2+pi_2*pi_3+pi_3*pi_4+pi_4)` words | exact construction count |
| Saturated raw product of uniform rank-`r` operands | order five | yes | dense allocation `B*(2*r^2+3*r^4)` words or `b_K` times this many bytes | conditional exact count |
| Exact normalizer stage | algorithm-dependent | yes | Vilmart reduction `O(P*S_j)=O(B*P^3)` for raw maximum bond `P`; charge pivots, reads, writes, and peak cores | route-specific upper bound |
| Boolean indicator `Zcal_Q` | `B^5` bits represented in `K` | yes | final `rho_k=m_(k,Q)`, the number of matching partial sums at cut `k` | restricted theorem |
| Final dense TT cores | five cores | yes | `B*(rho_1+rho_1*rho_2+rho_2*rho_3+rho_3*rho_4+rho_4)` words | standard dense allocation, not an information lower bound |
| Generic entry-oracle TT skeleton | queried components | yes | exact arbitrary sparse recovery can require `B^5` queries even at rank one | model-bound rejection |
| First sweep and leading-index locator | five levels | yes | sweep charged separately; leading index `O(5*B*r)` after a valid first sweep | exact cited bound, rank-dependent |
| Positive witness | five registry identifiers | yes | `O(1)` identifiers plus independent EC replay | required output |
| Negative certificate | canonical zero cores or equivalent | yes | at least final core and normalization certificate size | open accounting |
| Certificate and replay | IDs or exact zero certificate plus EC operations | yes | charge `W_cert,T_cert,W_replay,T_replay` | required resource terms |
| Target-support statistics | up to `q` targets conceptually | yes by target class | report `epsilon=|D5|/q`, canonical row yield, and rank-increment yield `eta_r` | conjunctive promotion gate |
| Relation-attempt budget | `R_req` rank increments | yes by full accepted-span history | exact geometric equality only under conditionally IID rank states; otherwise history-uniform `p_r_min` bounds and a preregistered quantile | required total-resource multiplier |
| Pair-sum support | `N2=|D2|<=B^2` distinct records | no or target-shifted | exact records and `b_D2` bytes each | task-matched comparator |
| Triple-sum support | `N3=|D3|<=B^3` distinct records | no | exact records and `b_D3` bytes each | task-matched comparator |
| D2+D3 target lookup | at most `N2` subtractions/probes | yes | report full-advice mismatch or instantiate a byte-capped variant; preserve witness semantics and collisions | comparator, not lower bound |
| D2+D3 preprocessing | `B^2+B*N2` candidate events | no | group additions/probes plus `N2+N3` complete-record writes | exact support-aware comparator surface |

## Required cumulative gates

```text
Tier A:
  fixed advice bytes                  = O(B^3),
  preprocessing field operations      = O(B^3),
  preprocessing bytes transferred     = O(B^3),
  peak preprocessing workspace bytes  = O(B^3),
  sum target field operations         = o(B^2),
  sum target bytes transferred        = o(B^2),
  peak target live bytes              = o(B^2).

Tier B:
  fixed advice bytes                 = o(B^3),
  preprocessing field operations     = o(B^3),
  preprocessing bytes transferred    = o(B^3),
  peak preprocessing workspace bytes = o(B^3),
  sum target field operations         = o(B^2),
  sum target bytes transferred        = o(B^2),
  peak target live bytes              = o(B^2).

Tier C, each in its own unit:
  retained/advice bytes                    = o(B^2.5),
  preprocessing operations                 = o(B^2.5),
  preprocessing traffic/workspace bytes    = o(B^2.5),
  actual relation work and traffic         = o(B^2.5),
  filtering/linear-algebra work and traffic= o(B^2.5),
  individual descent work and traffic      = o(B^2.5).
```

The explicit target byte equation is

```text
T_Q_bytes = b_K*(T_g+T_Frob+sum_j(T_H_j+T_N_j)
                 +T_1minus+T_sweep+T_locate+T_cert+T_replay)
            +T_metadata
          = o(B^2).
```

The matching target work equation includes

```text
W_Q=W_g+W_Frob+sum_j(S_j+N_j)
    +W_1minus+W_sweep+W_locate+W_cert+W_replay=o(B^2).
```

For `R_req=Theta(B^rho)`, valid history-uniform stationary exponents
`epsilon=Theta(B^-delta_epsilon)`, `eta=Theta(B^-delta_eta)`, and cumulative
per-attempt resource `d` of size `B^tau_d`, Tier C relation collection requires

```text
tau_d+rho+delta_epsilon+delta_eta<2.5
```

for work and cumulative traffic separately. Peak state passes a maximum gate
and is not multiplied by the attempt count.

Passing final-core storage alone is insufficient. The cumulative ledger must
include all `Theta(log B)` Hadamard stages, every exact normalizer, Frobenius
traffic, final direct-sum normalization, locator sweep, certificate, and
independent replay. Promotion also requires correct `epsilon`, canonical
relation yield, and `eta_r`; ordered permutations and duplicate labels do not
count as independent relations. A marginal or empirically averaged success
rate is not a history-uniform conditional lower bound.
