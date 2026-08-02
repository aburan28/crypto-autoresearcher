# ECDLP relation and preprocessing accounting

**Prepared:** 2026-07-18

## Status

`MODEL-BOUND`, shared benchmark contract. These formulas normalize the two
paper preflights. They do not authorize implementation and do not convert a
relation oracle into a discrete-log algorithm.

## Support and rank

Let `B` count signed public factor identifiers and let `n=B^5` at the five-term
balance. Define finite distinct supports

```text
N_j = |D_j^fin| <= min(n-1, binom(B+j-1,j)).
```

Using `N_2=Theta(B^2)` or `N_3=Theta(B^3)` requires a measured collision-light
assumption for the registered factor base. Uniform-target relation probability
is

```text
epsilon_rel = |D_5|/n.
```

A supported-target schedule cannot estimate this probability.

Let `r_star` be required matrix rank, `r_0` an independently justified initial
rank, and `R_req=r_star-r_0`. Let `eta_r` be the conditional probability that an
accepted relation increases rank from `r` to `r+1`. Then

```text
E[A] = sum from r_0 to r_star-1 of 1/(epsilon_rel(r)*eta_r).
```

Under stationary `epsilon_rel` and `eta`, this becomes

```text
E[A] = R_req/(epsilon_rel*eta).
```

For a rank-dependent high-confidence budget, preregister `alpha`, define
`p_r=epsilon_rel(r)*eta_r`, and model the waiting time for the next independent
row as `G_r~Geom(p_r)`. Under independent conditional waiting times, use

```text
A_(1-alpha) = min {a :
  Pr[sum_(r=r_0)^(r_star-1) G_r <= a] >= 1-alpha}.
```

If only a uniform lower bound `p_min<=p_r` is justified, the conservative budget
is

```text
A_(1-alpha) = min {a :
  Pr[Binomial(a,p_min) >= R_req] >= 1-alpha}.
```

The earlier binomial expression with `p_min=epsilon_rel*eta` is the stationary
iid specialization. These are model-based budgets, not deterministic exact
counts. The exponent formulas below assume `log(1/alpha)=B^o(1)`; otherwise the
confidence oversampling exponent is charged separately.

If

```text
R_req       = Theta(B^rho)
epsilon_rel = Theta(B^-delta_epsilon)
eta         = Theta(B^-delta_eta),
```

then

```text
A = Theta(B^(rho+delta_epsilon+delta_eta)).
```

An independent attempt of cost `B^tau` can fit a sub-rho relation stage only if

```text
tau+rho+delta_epsilon+delta_eta < 2.5.
```

For `rho=1`, this is `tau<1.5-delta_epsilon-delta_eta`. A true batch law
`B^u*A^v` must satisfy

```text
u+v*(rho+delta_epsilon+delta_eta) < 2.5.
```

## Advice tiers

For every tier, total advice includes factor registry, D2, tree, node operators,
terminal lift, metadata, pointers, page cache, and accelerator-resident state.

### Finite continuation

A measured `0.8x` byte or operation ratio is only a finite engineering screen.
It establishes no asymptotic tier.

### Fixed-curve online Tier A

```text
S_A,total = S_F+S_D2+S_tree+S_D3+S_op+S_lift = O(B^3)
T_online  = o(B^2)
TargetLive= o(B^2).
```

All quantities use actual canonical bytes and field-normalized operation and
traffic vectors. Advice beyond `O(B^3)` is a separate high-advice tier with an
equal-advice comparator.

### Compressed fixed-curve Tier B

```text
S_B,total        = o(B^3)
PeakWorkspace_pre= o(B^3)
T_online         = o(B^2)
TargetLive       = o(B^2).
```

An empirical Tier B claim requires an upper-confidence B-slope below 3; a
constant `0.8x` ratio is insufficient.

### One-instance sub-rho candidate

```text
S_total,
P_factorbase+P_compiler,
PeakWorkspace_pre,
AdviceWrites,
actual relation batch,
sparse linear algebra,
individual descent
    = o(B^2.5)
```

under one common success and target distribution. Explicit D3 advice fails this
gate even when online work is tiny.

## Equal-byte fixed-base BSGS

Let `S_bits` be the candidate's immutable-advice bit cap. Measure
`b_BSGS,rec(n)`, the complete bits per BSGS record including point key,
exponent, hash-table metadata, allocator overhead, and load-factor slack. Define

```text
M_B = min(n,floor(S_bits/b_BSGS,rec(n))).
```

If `M_B<1`, the equal-byte table comparator is unavailable; it does not receive
one uncharged record. Otherwise charge the strongest total-work comparator under
the cap:

```text
P_BSGS(m) = Theta(m) group operations and writes
T_BSGS(Q;m) <= ceil(n/m)-1 giant steps, lookups, and verification
C_BSGS^*(K) = min_(1<=m<=M_B) [P_BSGS(m)+sum_Q T_BSGS(Q;m)].
```

Ignoring ceilings and constants, `m^*(K)=min(M_B,Theta(sqrt(K*n)))`. Selecting
`m=M_B` remains valid only for an explicitly online-only, fixed-advice frontier.
For `M_B=B^3`, one-target total work is optimized near `m=B^2.5`, while `K=B`
is optimized near `m=B^3`; forcing the comparator to consume all available
advice would weaken the one-target kill screen. BSGS solves the full DLP, so it
is a stronger-output comparator rather than an output-equivalent relation
baseline.

## Constructive generic preprocessing

Measure a separate complete record size `b_G,rec(n)` for the constructive
generic algorithm, including endpoint label, known logarithm, hash description,
metadata, allocation overhead, and load-factor slack. Define

```text
M_G = min(n,floor(S_bits/b_G,rec(n)))
```

and let `calM_G` contain only `1<=m<=M_G` satisfying the cited construction's
parameter hypotheses. For a fixed valid `m` and fixed-generator DLP success
`epsilon_DLP`, the matching tradeoff scale is

```text
T_G = soft-Theta(sqrt(epsilon_DLP*n/m))
P_G = soft-Theta(m*T_G)
    = soft-Theta(sqrt(epsilon_DLP*n*m)).
```

For `K` independent targets, the strongest end-to-end comparator under the byte
cap is

```text
C_G^*(K) = min_(m in calM_G) [P_G(m)+K*T_G(m)],
```

unless an actual batch implementation is supplied. Report generic queries, RAM
work, writes, canonical advice bytes, and traffic separately. At constant
success and fixed `m=B^sigma`,

```text
T_G = B^((5-sigma)/2)
P_G = B^((5+sigma)/2).
```

At `m=B^3`, online work is `B` and preprocessing is `B^4`. Choosing `m=M_G` to
minimize online work is an online-only fixed-advice frontier. Omitting `P_G` or
failing to optimize over valid `m` does not define the total-work comparator.

## Generic theorem boundary

For the Corrigan-Gibbs-Kogan preprocessing theorem, record separately:

```text
S_bits      immutable target-independent advice bits
S_group     advice converted to complete generic-group records
T_G         online generic-group oracle queries only
P_G         preprocessing generic-group queries
T_field     concrete coordinate field-operation vector
Traffic     probes, reads, writes, and bytes
epsilon_DLP probability of returning the discrete log of a uniform target.
```

Only theorem-aligned generic DLP algorithms may report the bit-advice ratio

```text
R_ST,bits = (S_bits+O(log n))*T_G^2/(epsilon_DLP*n).
```

After declaring a complete generic-record encoding,
`S_group*T_G^2/(epsilon_DLP*n)` is an exponent-normalized diagnostic, not the
exact bit-advice theorem. Also report the preprocessing-query diagnostic

```text
R_PT = (P_G*T_G+T_G^2)/(epsilon_DLP*n),
```

where `P_G,T_G` are generic-group query counts. Both diagnostics require the
fixed-generator, random-injective-label generic model and uniform-target DLP
output. Field operations, traffic, relation probability, coordinate structure,
or multi-target sharing cannot be inserted into either ratio. For a concrete
relation compiler, any analogous ratio is labeled `MODEL-BOUND engineering
diagnostic`, and full pipeline costs remain separate.

## Exact amortization

For candidate `I` and output-equivalent comparator `C`, define

```text
K_star = inf {K>=1 : P_I+U_I(K) <= P_C+U_C(K)},
```

where `U(K)` is measured actual batch work. Relation collection requires
`K_star<=A_(1-alpha)`, not merely `K_star<=B`, unless constant support, constant
rank yield, and `R_req=Theta(B)` have been established.

## Next concrete action

Every experiment contract must instantiate these variables with measured
supports, a frozen target distribution, confidence level, exact advice bytes,
and output-equivalent plus stronger-output comparators before source review.
