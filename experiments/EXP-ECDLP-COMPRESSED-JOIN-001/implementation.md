# Implementation note

`src/compressed_join.py` reuses only the clean-curve, factor-base, rho, and fixed-base BSGS primitives from `EXP-ECDLP-FIXED-COMPILER-001`. Its join representation is new:

1. enumerate the exact unique `D2=F+F` support with one canonical pair witness;
2. enumerate `D2+D2` once and retain the exact `D4` support for audit;
3. compile only distinct bucket triples `(h(a+b),h(a),h(b))` plus D2 bucket contents;
4. recover D4 witnesses by route-guided candidate additions;
5. scan the final factor-base point to obtain five-term witnesses;
6. use inherited factor-base logs to execute randomized toy individual descent;
7. execute fixed-base BSGS under the same full advice-bit budget.

The scalar-interval router requires an exhaustive private toy DLP table. It is marked `positive_control_only`, its scalar table is not serialized, and candidate routers receive `scalar_index=None`.

`src/verify_compressed_join.py` performs an exact deterministic replay and then independently recomputes curve orders, subgroup membership, `D2`, `D4`, `D5`, factor witnesses, and recovered challenge scalars using a separate affine implementation.

Two post-result audits preserve rather than overwrite v1:

- `src/audit_fiber_null.py` replaces the full-point random label with eight public random `x`-fiber hashes satisfying `h(P)=h(-P)`;
- `src/audit_materialized_baseline.py` executes the exact materialized-D4 query on the same supported D5 target schedule.

The generator does not charge coordinate hash arithmetic, especially Legendre exponentiations. That omission favors the router and therefore cannot rescue the negative comparisons; it prohibits a positive cost claim.
