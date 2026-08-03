# Scheme-Aware Point DAG V1 Analysis

## Status

`RESTRICTED THEOREM`, `OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`,
scoped `NEGATIVE RESULT`.

The oriented `F_(p^2)` characteristic-polynomial representation preserves
all four requested cycle semantics, infinity multiplicities, membership, and
stored first source witnesses. Its polynomial degree tracks the finite
explicit cycle degree exactly. No compressed representation, resultant, or
query-to-source DAG descent was constructed.

## Exact Run

- source commit:
  `972a7e3171995f3c644ae172bfdcd0f625584e86`;
- fixed curve: `p=971`, `q=953`;
- `B in {2,3,4,5}`;
- x-interval candidate;
- scalar-progression compression control;
- random-x subgroup control;
- source-PRF-x solvable-x control;
- four typed cycles per cell;
- cells: 16;
- producer wall time/RSS: 0.43 seconds / 30,883,840 bytes;
- independent verifier wall time/RSS: 0.39 seconds / 36,175,872 bytes;
- zero support, degree, polynomial, query, infinity, or witness mismatch;
- dropped-row, duplicate-row, summary, and row-validity mutations rejected.

The verifier independently reconstructs every point cycle, multiplicity,
first witness, oriented characteristic polynomial, and sampled
positive/negative query. It does not certify the recorded product-tree
accounting, baselines, resource telemetry, or claim-status fields; see
`red-team-review.md`.

## Typed Semantics

For every cell:

- reduced, canonical, ordered, and unique-D2-pair cycles have identical point
  support;
- canonical total degree is `binomial(B+3,4)`;
- ordered total degree is `B^4`;
- unique-D2-pair total degree is
  `binomial(|supp(D2)|+1,2)`;
- reduced degree is the canonical point-support size;
- finite `x+omega*y` encodings are injective;
- infinity is split and counted separately;
- every sampled positive root retrieves a stored source route and replays;
- every sampled negative is a nonroot.

Support equality is definitional for these four constructions in an abelian
group. The informative distinction is that equal support does not imply equal
cycle coefficients.

## B=5 State

`sqrt(q)=30.87`.

| family | cycle | degree | point support | serialized Fp elements | peak live coefficients |
|---|---|---:|---:|---:|---:|
| x-interval | reduced | 69 | 69 | 140 | 242 |
| x-interval | canonical | 70 | 69 | 142 | 245 |
| x-interval | unique-D2-pair | 120 | 69 | 242 | 420 |
| x-interval | ordered | 625 | 69 | 1,252 | 2,188 |
| random-x | reduced/canonical | 70 | 70 | 142 | 245 |
| source-PRF-x | reduced | 55 | 55 | 110 | 189 |
| scalar progression | reduced | 29 | 29 | 58 | 98 |
| scalar progression | canonical | 70 | 29 | 136 | 235 |
| scalar progression | ordered | 625 | 29 | 1,196 | 2,090 |

Even the scalar control's reduced oriented polynomial needs 58 base-field
elements. Coordinate-family reduced polynomials need 110–142. These are
representation sizes, not rho storage costs; comparing them directly with
the `sqrt(q)` rho work scale is dimensionally invalid.

Naive balanced product work also follows degree. At `B=5`, ordered cycles use
184,274–201,644 extension-field coefficient multiplications, versus
1,800–2,954 for reduced coordinate cycles. These are implementation counts,
not lower bounds.

## Strongest Valid Conclusion

> For each tested effective point cycle `C`, the affine encoding
> `iota(x,y)=x+omega*y`, together with a separate infinity counter, reconstructs
> the fully expanded monic polynomial
> `Phi_C(T)=product_(P != O)(T-iota(P))^m_C(P)`. Its degree is exactly
> `degree(C)-m_C(O)`, and its dense coefficient vector has `d_f+1`
> `F_(p^2)` coefficients. Fully expanding this root product cannot compress
> below its finite degree.

This is a scoped negative for the fully expanded univariate root product.
The observed schoolbook product-tree work is implementation-specific. The
result is not a retained witness DAG, total-memory lower bound, or normalized
rho comparison. It does not rule out:

- factored or straight-line resultants that avoid coefficient expansion;
- quotient-algebra norms with reusable structure;
- divided-power DAG compression;
- transposed multipoint or batched modular composition;
- low-displacement-rank operators;
- alternative oriented point ideals;
- many-target amortization.

No normalized rho/BSGS runtime claim follows. The run lacks multi-seed
fixed-q sweeps, complete memory traffic, blind target descent, relation rank,
and linear algebra. The exact same-function baselines are an explicit support
dictionary, sorted support, and reduced-D2 MITM.

## Next Concrete Action

Do not expand the explicit root polynomial to larger `q`. Implement a
factored canonical divided-power tree on the same `p=971`, `B<=5` cells:

1. retain child cycles and source routes without using a direct root
   support-to-route lookup during query;
2. measure hash-cons reuse, node/edge count, live state, and target
   specialization;
3. implement child extraction and exact source witness descent;
4. compare against reduced-D2 MITM, a support dictionary, sorted support,
   and separately reported BSGS/rho work;
5. falsify the route if retained advice or one-target build/query/descent
   loses to the same-function baselines.
