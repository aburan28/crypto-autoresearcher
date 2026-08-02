# Red-Team Review: Scheme-Aware Point DAG V1

## Handoff: Expanded Root-Product Boundary

### Claim or task

Audit whether the fixed-toy packet establishes exact four-cycle semantics and
a valid scoped negative for the expanded oriented root-product representation.

### Status

`REVISE INTERPRETATION`.

- cycle definitions and arithmetic: `OBSERVATION`, independently reproduced;
- expanded-polynomial degree: `RESTRICTED THEOREM`;
- implementation counts: `TOY-EVIDENCE`, `MODEL-BOUND`;
- negative result: valid only for the fully expanded univariate root product;
- retained witness DAG, complete live-state accounting, and normalized rho
  comparison: not established.

### Assumptions

- fixed curve over `F_971`, prime subgroup order `q=953`;
- one nested prefix per family and `B=2..5`;
- unique-D2 means distinct D2 image points after D2 route multiplicity is
  discarded;
- infinity is a separate typed counter, not an affine polynomial root;
- product work uses the producer's eager balanced schedule and schoolbook
  multiplication.

### Evidence so far

The committed hashes matched the reviewed source and artifacts. The verifier
reran byte-exact. A fresh producer run matched the normalized scientific
payload; only resource telemetry changed.

An independent reconstruction of the `B=5` scalar-progression cell found:

| cycle | degree | support | infinity | finite polynomial degree |
|---|---:|---:|---:|---:|
| reduced | 29 | 29 | 1 | 28 |
| canonical | 70 | 29 | 3 | 67 |
| ordered | 625 | 29 | 28 | 597 |
| reduced-D2 pair | 91 | 29 | 3 | 88 |

All four cycle and polynomial digests matched. Ordered multiplicities also
matched an independent multinomial derivation. Every first witness replayed,
membership was exact over all 953 group elements, and `delta=2` was confirmed
nonsquare.

For an effective point cycle `C`, the actual restricted theorem is

`degree(Phi_C) = degree(C) - multiplicity_C(O)`,

where

`Phi_C(T) = product_(P != O) (T - (x(P)+omega*y(P)))^multiplicity_C(P)`.

The dense vector therefore has exactly `d_f+1` extension-field coefficients,
or `2(d_f+1)` base-field elements.

### Failure modes

1. **HIGH: no DAG witness descent.** Positive queries read the witness directly
   from the already-materialized cycle map. The polynomial tree retains no
   leaf/source edges. This proves known-hit replay, not query-to-source descent
   from the polynomial.
2. **HIGH: accounting is not verifier-covered.** The verifier reconstructs
   cycles and polynomials but does not derive the recorded product tree,
   operations, live state, baselines, resource fields, row parameters, or
   claim status. Its mutation suite tests only the envelope.
3. **HIGH: live state is partial and schedule-specific.** The peak coefficient
   counter excludes cycle maps, routes, multiplicities, roots, query state,
   Python object overhead, and traffic. It is not total memory or a lower
   bound.
4. **HIGH: the rho comparison is dimensionally invalid.** `sqrt(q)` is a rho
   work scale, not a storage count. Base-field elements, group records, and
   group operations cannot be compared without a declared encoding and cost
   model. Same-function support dictionaries and reduced-D2 MITM are stronger
   baselines.
5. **MEDIUM: support equality is definitional.** With reduced D2 image support,
   all four constructions have the same set support in any abelian group. The
   informative distinction is coefficient multiplicity, for example infinity
   coefficients `1,3,28,3` in the scalar `B=5` cell.
6. **MEDIUM: unique-D2 is reduced-image symmetric squaring.** It is
   `+_* Sym^2(S_2,reduced)`, not the pushforward of the canonical D2 cycle.
7. **MEDIUM: multiplicity is encoded but not queried.** Boolean polynomial
   evaluation tests support only; no Hasse-derivative or repeated-root
   interface was implemented.
8. **MEDIUM: infinity is external.** The affine polynomial plus counter is not
   one unified characteristic object for the complete cycle.
9. **MEDIUM: first witnesses are replay evidence only.** Deterministic
   first-witness selection is not evidence of downstream relation rank or
   target descent.
10. **LOW: scaling evidence is absent.** One fixed curve, nested prefixes, and
    one seed per family support a semantic preflight, not an exponent fit.

### Corrected conclusion

> The affine oriented encoding plus a separate infinity counter exactly
> reconstructs each tested fully expanded monic root polynomial. Fully
> expanding this particular polynomial cannot compress below its finite
> degree. The measured schoolbook product-tree work is implementation-specific.
> This is not a scheme-theoretic pushforward, retained witness DAG, total-memory
> lower bound, or rho-cost comparison.

### Next concrete action

Implement a retained divided-power tree that deletes direct root
support-to-route lookup during queries, descends through child cycles to four
source indices, charges every retained point and route, and compares against
reduced-D2 MITM and an exact support dictionary.

### Artifact paths

- `contract.md`
- `analysis.md`
- `raw-result.json`
- `verification.json`
- `../../src/scheme_aware_point_dag.py`
- `../../src/verify_scheme_aware_point_dag.py`
