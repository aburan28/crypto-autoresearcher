# EXP-JMV-004 branch (a) — scouting result

**STATUS: SCOUTING. Not an approved run, no run record, no independent validation.**
EXP-JMV-004 is `status: draft`, `approved_by: null`, and under Coordinator review
(`TASK-20260726-001`). Nothing here may be cited as evidence.

Script: `experiments/EXP-JMV-004/cost_model.py` — moved in from the scratchpad
once branch (a) was approved under DEC-20260726-001. Deterministic arithmetic;
no seeds, no sampling. Note the spec's `proof_refs` points at the *run's*
`cost_model.md`, which does not exist yet; this is the implementation only.

## What was computed

Corollary 1.2 gives `polylog(q)` **oracle queries**. This converts that to field
operations using only quantities from the paper:

```
m = (log q)^(2+δ)                             Thm 1.1
k = λ_triv ≈ #{split p ≤ m} ≈ π(m)/2          §4.3
c = C · m^(1/2) · log|mD|,  |D| ≤ 4q          Lemma 4.1
r ≥ log(2h/|S|^(1/2)) / log(k/c)              Prop 3.1
h ≈ sqrt(q)                                    class number, order of magnitude
cost = r × (per-step isogeny cost at typical ℓ ≈ m)
```

`C` is Lemma 4.1's implied constant. The paper states only that it is absolute
and never gives a value; pinning it needs the Bach–Sorenson constants (ref [2]).
**It is swept, not assumed.** Both `log` conventions (bits / natural) are computed.

## Result 1 — the proven separation is vacuous for small δ at 2^256

`k/c` at `q = 2^256`; VACUOUS means the proven bound yields no expansion at all.

| convention | δ=0.25 | δ=0.5 | δ=1 | δ=2 | δ=3 |
|---|---|---|---|---|---|
| bits, C=1 | VACUOUS | VACUOUS | VACUOUS | 7.72 | 95.1 |
| bits, C=4 | VACUOUS | VACUOUS | VACUOUS | 1.93 | 23.8 |
| natural, C=1 | VACUOUS | VACUOUS | VACUOUS | 4.01 | 41.2 |

Any `δ > 0` is asymptotically valid — the theorem only asserts *some* polynomial
`p(x)`. Concretely at 256 bits, **δ must be ≳ 1–2 before the proven bound says
anything at all**, and that choice is what makes `m` (and so the per-step cost)
large. The freedom in "there exists a polynomial" is not free at deployed sizes.

## Result 2 — under the paper's own per-step cost, the reduction is infeasible at 2^256

Cheapest admissible δ (minimising cost subject to `k/c > 1`), `C = 1`, bits convention:

| per-step model | δ* | walk length r | total cost | vs rho = 2^128 |
|---|---|---|---|---|
| `O(ℓ³)` — JMV §4.1, modular polynomials | 1.25 | 222 | **2^85.8** | cheaper, but infeasible in absolute terms |
| `O(ℓ)` — plain Vélu | 1.35 | 102 | 2^33.5 | practical |
| `O(√ℓ)` — √élu (BDLS 2020) | 1.55 | 49 | 2^19.8 | trivial |

`2^85.8` field operations is comparable to a ~171-bit ECDLP. So under the cost
model **the paper itself cites**, Corollary 1.2 is polynomial-time and cheaper
than rho, yet still far beyond any feasible computation at 256 bits.

## Result 3 — below ~160 bits the reduction costs more than the problem it reduces

`C = 1`, cheapest admissible δ per size, bits convention:

| bits | rho `√n` | `O(ℓ³)` | `O(ℓ)` | `O(√ℓ)` |
|---|---|---|---|---|
| 64 | 2^32 | **2^72** | 2^28 | 2^16 |
| 128 | 2^64 | **2^79** | 2^31 | 2^18 |
| 160 | 2^80 | 2^81 | 2^31 | 2^18 |
| 192 | 2^96 | 2^83 | 2^32 | 2^19 |
| 256 | 2^128 | 2^86 | 2^33 | 2^20 |

Under `O(ℓ³)` the crossover sits near **160 bits**. At 64 bits the reduction is
`2^40` times more expensive than simply solving the instance. The asymptotic
statement only becomes meaningful because rho grows faster, not because the
reduction is cheap.

## The load-bearing caveat

**The `O(ℓ)` and `O(√ℓ)` rows are optimistic lower bounds, not established costs
for this setting.** Both assume a kernel point is in hand. In CSIDH that is
arranged by choosing `ℓ | p+1` so the `ℓ`-torsion is rational; here `ℓ` ranges
over *all* split primes `≤ m`, and for a general such `ℓ` the `ℓ`-torsion is not
rational over `F_p`, so a kernel generator is not cheaply sampleable. Finding the
neighbour is exactly what the modular-polynomial step does. The applicable model
in the general ordinary setting is therefore the `O(ℓ³)` row, improvable toward
`O(ℓ²)` by Elkies-style methods — **not** `O(√ℓ)`.

So the honest reading is the *range*, and the fact that the verdict is entirely
determined by which per-step algorithm applies.

## Why this is worth a reviewed run

The provisional headline is not "JMV is wrong" — the theorem is untouched. It is
that **the concrete standing of the reduction is decided by a per-step cost the
paper fixes at `O(ℓ³)` and never revisits**, and under that figure the reduction
is infeasible at every cryptographic size and actively worse than the attack
below ~160 bits. That is a precise, checkable statement about a result routinely
cited as justification for selecting curves by order alone.

It also sharpens the case for EXP-JMV-003: every VACUOUS cell above comes from
the *proven* bound. The true spectral gap is very likely far better, which would
permit a much smaller `m` and collapse the `O(ℓ³)` cost. Measuring `C` is what
separates "concretely unproven" from "concretely false", and only the first of
those is currently supported.

## Limits

- `C` unpinned; every figure is conditional on the sweep.
- `h ≈ √q` is order-of-magnitude; a `polylog` factor does not move the verdicts.
- Cost is in field operations under the stated model only. **Nothing here bears
  on GRH, on real attack cost, or on the hardness of any dlog instance, and this
  is not an attack or an attack-cost improvement.**
- Scouting: unreplicated, unreviewed, no run record.
