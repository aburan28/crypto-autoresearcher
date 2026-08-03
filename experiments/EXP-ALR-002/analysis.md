# Analysis - AutoLab R183 sparse-projector Prony locator

## Observation

For each source point `P` and squarefree target chart `B_r=F[u]/W_r`, R183
defines

```text
m_P = sum_r Tr_Br(1-M_RP^(p-1)).
```

On every split chart component this equals `sum_r deg gcd(W_r,R_P)`. Since
total target degree is below the characteristic, `m_P` is nonzero exactly for
candidate source components. If `c` is the candidate count, the moments

```text
s_k = sum_P m_P x(P)^k,  0 <= k < 2c
```

recover the exact candidate locator by Berlekamp-Massey and coefficient
reversal.

The package contains all twelve R182 controls and a new strided divisor family
at seed `18307`:

```text
selected source degree sum:                         411
unique target degree sum:                            84
candidate / noncandidate sources:              256 / 155
target-gcd multiplicity sum:                        414
weighted moment count:                              512
represented source-target slots:                  2,997
```

All projector traces, gcd degrees, direct group-law multiplicities, candidate
supports, Hankel ranks, recurrence orders, and candidate locators agree
exactly. An `F_101` source-row swap preserves all tested global target power
sums while changing the candidate locator, so source-blind target traces are
label-incomplete.

## Cost Interpretation

The `2c` moment output, Prony recovery, and candidate verification are below
the `B^(5/2)` rho proxy once the moments are available. No compact constructor
is supplied. The represented tensor projector and A-linear target Krylov output
retain `nN=B^(7/2)`, above rho. This closes those represented routes only.

## Claim Boundary

- Claim tier: toy.
- The finite exactness, collision, and rank controls are not an asymptotic lower bound.
- No general nonlinear trace, SLP, circuit, resultant, RAM, or data-structure lower bound follows.
- No compact nested-moment constructor, factor logs, identical fresh-target descent, complete ECDLP attack, Pollard-rho improvement, Shoup improvement, or breakthrough is present.
- The source package passed 19 of 28 obligations; lane admission and all attack flags remain false.

## Surviving Direction

Construct or refute an SLP-direct nested projector-moment operator that consumes
compact `U,V`, target charts, and the signed line-product SLP, emits the `2c`
weighted source moments, and avoids every represented `nN` remainder,
projector, or A-valued Krylov body in softly `O(n+N+c)` work. Seed `18308` and a
second strided divisor family are the next bounded controls.
