# Independent Algorithm Review

Reviewer task `019fafb4-9288-7280-a695-66102a2e21d6` ranked constructive
successors to the exact rank-24/48 factorization.

## Status

`OPEN`, with one restricted batched algorithm, two testable hypotheses, and
one high-risk conjecture. None is a single-target sub-rho result today.

## Candidate Ranking

| rank | candidate | fixed advice | batch/query | current verdict |
|---:|---|---:|---:|---|
| 1 | orbit-diagonal batched MITM | `B^2` | `B^3+B(T+B)` | amortized aligned-target lead |
| 2 | degree-16 section/root index | `B^2` | about `B^3` | correctness oracle, not rho win |
| 3 | collision-compressed sparse `D3` | `B^2+B|D2|` | `B^2` | needs strong low doubling |
| 4 | implicit elliptic resultant circuit | hoped `B^(2+o(1))` | hoped `B^(2+o(1))` | high-risk open route |

Here `B=q^(1/5)`.

## Orbit-Diagonal Batch

For

`A_i=P0+iD` and `Q_t=Q0+tD`,

a witness satisfies

`r2+r3+r4 = (Q0-P0)+(t-i)D-r1`.

Writing `k=t-i` reduces `TB^2` target-left keys to `(T+B)B`.

The exact algorithm:

1. materialize unique `D2=R+R` with witnesses;
2. hash `(Q0-P0)+kD-r1` for all relevant `k,r1`;
3. enumerate `D2+R` once;
4. on a hit, recover every valid `(t,i)` with `t-i=k` and replay.

Costs are:

- fixed construction/advice: `Theta(B^2)`;
- batch specialization: `Theta(B(T+B))`;
- batch scan: at most `Theta(B^3)`;
- peak memory: `Theta(B^2+B(T+B))`;
- witness replay: constant per report.

For `T=B^alpha`, amortized work is

`B^(3-alpha)+B+B^(2-alpha)`.

It beats `B^2.5` per aligned target when `alpha>1/2`, while memory remains
below `B^2.5` when `alpha<3/2`. This is a nonempty many-target window, not a
one-instance exponent break. Rank yield and communication remain untested.

## Section/Root Oracle

The degree-16 coordinate-ring factor has affine form

`f_V(x,y)=a_V(x)+y b_V(x)`,

with `deg(a)<=24` and `deg(b)<=22`. Eliminating `y` gives

`G_V(x)=a_V(x)^2-(x^3+a_E x+b_E)b_V(x)^2`,

of degree at most 48. Its rational roots contain every orthogonal left point.

This turns each explicit right triple into at most 48 point candidates and
reduces exhaustive `B^5` dot products to `B^3` fixed-degree factorizations.
It is valuable as a constructive factor oracle but remains above rho and is
likely slower than ordinary point MITM.

## Sparse-Core Threshold

For `K2=|R+R|` and `K3=|R+R+R|`, materializing unique sums and querying
`A+R` can beat rho only if both

`K2=o(B^1.5)` and `K3=o(B^2.5)`.

The first condition charges attempted transitions; a small final `D3` does not
help if constructing it still costs `B*K2=B^3`. Existing coordinate families
look generic-size, while scalar progressions are only a positive control.

## High-Risk Resultant Route

Represent `R` by its exact point ideal and compose EC addition images as a
hash-consed resultant/subresultant DAG. A one-target `q^(2/5+o(1))` route
would require construction, advice, batch evaluation, and witness
back-substitution all near `B^(2+o(1))`.

The likely obstruction is output degree: generic `R+R+R` has `Theta(B^3)`
distinct roots, forcing DAG size, traffic, or witness data back to `B^3`.

## Next Concrete Experiments

1. Implement the direct coordinate-section factor as a correctness oracle.
2. Benchmark orbit-diagonal batching at
   `T in {ceil(B^1/2), B, ceil(B^3/2)}` and measure independent quotient-row
   yield.
3. Preserve the exact `K2/K3` thresholds as a kill screen.
4. Attempt the resultant route only if a control exhibits normalized circuit
   growth below `B^3`.
