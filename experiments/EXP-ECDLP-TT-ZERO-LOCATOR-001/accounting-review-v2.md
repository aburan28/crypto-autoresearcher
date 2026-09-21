# Direct five-source TT accounting review v2

## Handoff: frozen preflight v2 accounting audit

### Claim or task

Audit `preflight-v2.md` at SHA256
`b90c09448b740d198b52afbf9743735e0fca12dc51a0011352610fb2fdf49ce1`
and `object-dimension-ledger-v2.md` at SHA256
`92435885c64f912627e7a212712561f907aa84485c0f326d818e245d4b9fe9fa`.

### Status

`REVISE`.

All v1 algebraic and raw-rank repairs pass. Three accounting surfaces remain:
cumulative byte traffic, dimensionally complete Tier A/C definitions, and
rank-dependent relation-attempt accounting.

### Assumptions

- Standard dense TT Hadamard construction over `K=F_(p^2)`.
- Vilmart's model counts operations over the represented field.
- Canonical bytes, field/group operations, and peak state remain separate
  dimensions.
- D2+D3 is a complete task-matched comparator, not a lower bound.

### Evidence so far

The v2 definitions of actual raw bonds, exact dense allocation, saturated
uniform allocation, `Theta(log B)` chain length, route-specific sixth-root
work gate, `b_K` storage factor, complete final-core gate, Frobenius traffic,
final direct-sum normalization, target-dependent online objects, central-rank
failure gate, and exact `N2,N3` supports all pass.

Vilmart's exact normalizer uses `O(r*s)` field operations for input maximum TT
rank `r` and core size `s`. For raw maximum bond `P` and size `S_j`,
`O(P*S_j)` is contained in `O(B*P^3)`. This is an arithmetic bound, not a byte-
traffic theorem.

The target byte gate must be explicit:

```text
T_Q_bytes = b_K*(T_Frob
                 +sum_j(T_H_j+T_N_j)
                 +T_1minus+T_sweep+T_locate)
            +T_metadata
          = o(B^2).
```

If the naive exact schedule is conservatively charged at `O(P*S_j)` word
accesses and normalized operand ranks are at most `r`, a sufficient traffic
condition is

```text
b_K*m*B*r^6=o(B^2),
r=o((B/(b_K*m))^(1/6)).
```

A proved cache-aware schedule may improve this bound but cannot omit it.

Tier A must have a declared ceiling rather than arbitrary advice:

```text
fixed advice/preprocessing footprint = O(B^3) in each declared dimension,
online work and traffic               = o(B^2),
online peak state                     = o(B^2).
```

Anything larger is a separately labeled high-advice result with a byte-matched
comparator.

Tier C cannot add unlike units. Require separately:

```text
total retained/advice state bytes       = o(B^2.5),
preprocessing operations                = o(B^2.5),
peak preprocessing and advice writes    = o(B^2.5) bytes,
relation work and traffic                = o(B^2.5) in their units,
linear-algebra work and traffic          = o(B^2.5) in their units,
descent work and traffic                 = o(B^2.5) in their units.
```

Let the required rank increments be `R_req=r_star-r_0`. If the support and
rank-increment probabilities at current rank `r` are `epsilon_r` and `eta_r`,
then

```text
E[A]=sum_(r=r_0)^(r_star-1) 1/(epsilon_r*eta_r).
```

Under stationary values, `E[A]=R_req/(epsilon*eta)`. A confidence budget uses
the quantile of the corresponding sum of geometric waiting times or a justified
binomial lower bound, not merely its expectation.

If

```text
R_req=Theta(B^rho),
epsilon=Theta(B^-delta_epsilon),
eta=Theta(B^-delta_eta),
W_Q=Theta(B^tau),
```

then Tier C relation collection requires

```text
tau+rho+delta_epsilon+delta_eta<2.5.
```

For `rho=1`, the fixed-online condition `tau<2` is insufficient; Tier C needs
`tau<1.5-delta_epsilon-delta_eta`.

For D2+D3, disclose preprocessing candidate additions/probes, advice writes,
`N2` D2 reads and D3 probes per target, and exact record bytes. Full D2+D3 is
not automatically equal-advice to a compressed candidate; use a byte-capped
variant or label the advice mismatch.

### Failure modes

- Treating Vilmart's arithmetic bound as a byte-traffic theorem.
- Calling arbitrary-advice preprocessing Tier A.
- Summing bytes, operations, and peak memory into one Tier C quantity.
- Reporting `epsilon,eta_r` without charging the resulting attempt count.
- Calling full D2+D3 equal-advice without enforcing a byte cap.

### Next concrete action

Preserve v2 and issue v3 with the cumulative byte equation, exact tier vectors,
rank-dependent attempt quantiles/exponents, and an explicitly byte-capped or
advice-mismatched comparator.

### Artifact paths

- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/preflight-v2.md`
- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/object-dimension-ledger-v2.md`
- `notes/ecdlp_relation_preprocessing_accounting_20260718.md`
