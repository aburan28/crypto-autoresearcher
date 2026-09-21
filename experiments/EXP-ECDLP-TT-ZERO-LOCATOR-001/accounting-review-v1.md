# Direct five-source TT accounting review v1

## Handoff: frozen preflight v1 accounting audit

### Claim or task

Audit frozen `preflight-v1.md` at SHA256
`5db581dae9305fe43190f766ac3a450bd17830adeaab0c1118859988cb52c720`
against the strict storage, work, traffic, advice, and comparator gates.

### Status

`REVISE`.

The equality scalar, finite-field indicator, final cut-rank theorem, and scoped
entry-oracle rejection are sound. The artifact remains fail-closed and does
not authorize implementation, but the accounting repairs below are required.

### Assumptions

- Five modes have size `B`, `K=F_(p^2)`, and `p=Theta(B^5)`.
- Hadamard products are materialized as exact TT cores and normalized by exact
  finite-field rank factorization.
- Fixed-curve advice is target-independent.
- Canonical byte accounting is required wherever a gate is stated in bytes.
- Exact D2+D3 is a complete task-matched comparator, not a lower bound.

### Evidence so far

For Hadamard stage `j`, let operand bonds be `u_(j,k),v_(j,k)` and define the
actual raw bonds

```text
pi_(j,k)=u_(j,k)*v_(j,k).
```

The exact dense Kronecker-core allocation in field words is

```text
S_j=B*(pi_(j,1)+pi_(j,1)*pi_(j,2)
       +pi_(j,2)*pi_(j,3)+pi_(j,3)*pi_(j,4)+pi_(j,4)).
```

If all operand bonds equal `r`, this is `B*(2*r^2+3*r^4)`. This is an exact
construction count, not a lower bound for every possible product
representation.

Let `m=1+ell(p-1)=Theta(log B)` include the norm product and one exact
addition chain for `p-1`. Vilmart's exact arbitrary-field normalizer runs in
`O(r*s)` for input maximum TT rank `r` and input core size `s`; for raw maximum
bond `P`, this gives the coarse classical schedule `O(B*P^3)`. If normalized
operands have uniform rank at most `r`, then `P<=r^2`, and the route-specific
cumulative sufficient condition is

```text
O(m*B*r^6)=o(B^2),
r=o((B/m)^(1/6)).
```

This is a sufficient gate for the specified normalizer, not a necessary TT-rank
lower bound. The exact cumulative ledger is

```text
sum_j (S_j+N_j)+N_(1-minus)+W_locate=o(B^2),
```

with traffic and peak liveness reported separately.

Let

```text
b_K=2*ceil(log2(p)/8)
```

be canonical uncompressed bytes per `K` element. Byte gates multiply every
word allocation, read, write, and advice record by `b_K` plus metadata. In the
saturated uniform raw-product case, `b_K*S_j=o(B^2)` requires
`r=o((B/b_K)^(1/4))` for state.

The dense final-core allocation

```text
S_TT=B*(rho_1+rho_1*rho_2+rho_2*rho_3
        +rho_3*rho_4+rho_4)
```

passes the word-storage gate exactly when the sum in parentheses is `o(B)`.
Equivalently, all five nonnegative terms are `o(B)`. A uniform sufficient byte
gate is `max rho_k=o((B/b_K)^(1/2))`.

Rank-preserving Frobenius still reads, conjugates, and writes the `g_Q` cores.
Constructing `1-h_Q^(p-1)` uses raw direct-sum bonds `d_k=r_k+1` followed by
another exact normalization. Leading-index recovery also requires an explicit
work and traffic formula before implementation.

Offline reporting must separate advice size, preprocessing operations,
preprocessing writes and traffic, and peak preprocessing workspace. Every
`Q`-dependent core, power, pivot, transcript, suffix basis, and certificate is
online.

The exact D2+D3 comparator uses support sizes `N2=|D2|` and `N3=|D3|`:

```text
S_D2D3=N2*b_D2+N3*b_D3,
T_D2D3(Q)<=N2 EC subtractions and D3 probes,
```

plus witness verification. Only a collision-light specialization permits the
summary `N2=Theta(B^2),N3=Theta(B^3)`. It is an output-equivalent comparator,
not a universal floor.

### Failure modes

- Promoting an upper-bound normalizer model to a necessary rank condition.
- Losing `log B` in cumulative exponentiation work.
- Passing a word-count gate while failing canonical-byte traffic or state.
- Checking only the middle final-core product.
- Treating Frobenius, final subtraction, or leading-index recovery as free.
- Mixing fixed-online advice with a single-instance total claim.
- Calling D2+D3 a floor or assuming collision-light support without evidence.

### Next concrete action

Issue v2 with a per-stage `pi_(j,k)` ledger, cumulative normalizer and byte
gates, complete final-core inequalities, tier-separated preprocessing, and the
exact `N2,N3` comparator.

### Artifact paths

- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/preflight-v1.md`
- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/object-dimension-ledger.md`
- `notes/ecdlp_relation_preprocessing_accounting_20260718.md`
- `experiments/EXP-ECDLP-OUTER-TRANSLATOR-001/contract.md`
