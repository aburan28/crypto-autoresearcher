# Independent Benchmark Review

Reviewer task `019fafa3-9273-7663-a285-7e6626daf952` audited exact commit
`30793d7d676014f8c044073d7b12e679c4ed694f`.

Decision: `REVISE`; narrow functional `GO`, no exponent promotion.

The fresh rerun matched the committed result after removing timing fields,
with normalized SHA-256
`60e9f782f6b141d393431a1bd7371cc8b6c3a70a37923dc592d3c8281ea9dac7`.
The review also replayed an exact `D2+D2` join and reached full quotient rank
in every row.

Materialized finite comparators have asymptotic `(P,S,T)` exponents:

| compiler | exponents |
|---|---:|
| materialized `D4` | `(.8,.8,.2)` |
| `R` plus materialized `D3` | `(.6,.6,.4)` |
| `D2+D2` | `(.4,.4,.6)` |

None is a one-target sub-rho route. The executed dense quotient solver also
has asymptotic exponent `3/5`; the proposed sparse `2/5` solver remains
unexecuted.

Writing `c=1/5`, online exponent `t`, support loss `u`, rank-yield penalty
`r`, witness exponent `w`, advice exponent `s`, and peak-memory exponent `m`,
a sufficient gate needs:

- complete build exponent `<1/2`;
- `s,m<1/2`;
- `c+u+r+max(t,w)<1/2`;
- executed linear algebra exponent `<1/2`;
- arbitrary-target descent `u+max(t,w,c)<1/2`;
- matched parallel-resource accounting.

At `c=t=w=1/5`, the missing strict condition is `u+r<1/10`.
