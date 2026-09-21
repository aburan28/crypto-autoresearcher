# Recursive D2 Complement Preflight V1: RUN-001

## Result

`SCOPED NEGATIVE`, `TOY-EVIDENCE`, `MODEL-BOUND`.

The exact recursive `D2+D2` complement operator, the `R+D3` operator, and
the materialized `D4` lookup all returned identical canonical four-source
witness sets on 36 target queries across 12 curve/family cells. The
independent verifier replayed all 12 rows exactly and rejected all five
mutations.

## Advice/query frontier

Across the tested rows:

| Route | Advice words | Online work |
|---|---:|---:|
| `D2+D2` | 58-220 | 630-3,886 |
| `R+D3` | 165-1,100 | 247-859 |
| materialized `D4` | 390-4,282 | 36-104 |

The recursive route therefore reduces retained advice relative to explicit
`D3/D4`, but its target work is the full D2 scan for every `A` value. It does
not provide the required `q^(1/5+o(1))` target specialization for the typed
`A+4R` relation path. The charged witness payload is included in advice
words and witness replay additions are included in online work.

The largest recorded `S*T^2/q` diagnostic was approximately `213,195` for
`D2+D2`, `52,087` for `R+D3`, and `2,972` for materialized `D4`. These are
finite toy diagnostics, not generic-group lower bounds.

## Interpretation

This is a useful exact fixed-curve frontier measurement: recursive D2 advice
is valid and witness-bearing, but the query cost rises enough to erase the
benefit for one-target or typed relation collection. It is a scoped negative
for this D2 complement operator, not for all nonlinear target selectors,
quotient states, or batch preprocessing.

The next positive question must avoid scanning all D2 states per `A`: find a
target-conditioned nonlinear complement index that keeps the D2-scale advice
while reducing the complement work, with exact witness lift and full rank/
descent accounting.

## Accounting

- D2 build point additions: 848;
- D3 build point additions: 4,500;
- D4 build point additions: 17,840;
- producer wall time: 0.31 seconds;
- producer peak RSS: 27,115,520 bytes;
- verifier wall time: 0.14 seconds;
- verifier peak RSS: 27,738,112 bytes.

## Evidence hashes

- contract: `704b699a0b084855c388a369b81928919d39b1b9513989ca1bc00d6a9d676407`
- producer: `136f7eef3b0004de46fff2615b5c0ef9c8f8dec8aaa1f828fc26574d1a9ea3e8`
- verifier: `ebd78098a82daf36fa5e243532438c7eef45f1b54b1bfc7b49a1727d340fd3fa`
- immutable input: `c7476f8aeff640ea2690c70218252186a8c657bf1d6db76baa01c55e2289fa3c`
- raw result: `1582adb7ad4ca9833568f89ea73209b8a989d7722f746416248310aed9fdac32`
- verification: `2e2d3f1277814fb4824d724128aa8244d757695e3d65781fcdc2a994615abfa7`
- producer stderr: `cd20907a1c5c7ae84b368da2ce7f2fa32f1a722446f87370740d20427f61344f`
- verifier stderr: `e914de354d40e9a5e8f8c1860c5b6856414269b5cd6df4c4d285f22e40dc8305`
