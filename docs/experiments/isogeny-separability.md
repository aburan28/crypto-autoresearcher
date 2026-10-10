# Isogeny separability and conductor-gap experiments

## Implemented executable smoke experiment
`tools/isogeny_separability_experiment.sage` generates ordinary characteristic-2 elliptic curves, constructs relative Frobenius maps and searches rational odd-prime-degree separable isogenies with Sage. It verifies homomorphism behavior and point-count preservation, and emits JSONL receipts, including searches yielding zero edges. A stdlib summary tool and a unit test accompany it.

```bash
sage tools/isogeny_separability_experiment.sage --degree 5 --samples 4 --ell 3 5 7 --output /tmp/iso.jsonl
python tools/analyze_isogeny_separability.py /tmp/iso.jsonl
python -m unittest tests.test_analyze_isogeny_separability
```

**Not yet executed here.** SageMath must be installed to run the generator. This smoke test does not calculate endomorphism conductors, volcano levels, explicit ECDLP transport overhead, or relation-solving costs; it must not be presented as evidence of hardness separation.

## Hypotheses to track
H1: Odd-degree separable isogenies in characteristic 2 connect ordinary curves with different endomorphism orders, and their conductor changes can be certified.
H2: The construction and evaluation cost of separable conductor-changing paths differs systematically from cheap inseparable relative Frobenius.
H3: Frobenius compositions or alternative paths reduce practical transport overhead for selected curve pairs.
H4: Different conductor levels show reproducible differences in degree of regularity, verified relation yield or end-to-end attack cost under matched solver settings.

## Next experiments and required gates
1. Extend the generator with independently certified endomorphism-ring conductors, isogeny kernel certificates, dual maps and volcano level labels. Distinguish the characteristic 2 from the odd isogeny prime ell.
2. Record explicit map evaluation and path-construction time separately. Verify transport on prime-order subgroups; do not claim a reduction for maps that kill the chosen subgroup.
3. Compare paired same-field/same-trace/same-order curves at different certified conductor levels. Include within-isomorphism and same-conductor controls.
4. Run existing F4/F5/SAT relation pipelines, with matching factor bases, solver budgets and seeds; count failed attempts, duplicates, preprocessing, verification, rank increments and timeouts.
5. Analyze per-independent-relation costs with paired intervals and censored failures. Report no finding when data are insufficient.

Important: relative Frobenius E -> E^(2) is generally not a conductor-changing volcano descent. An inseparable isogeny can have a separable component; Frobenius is purely inseparable. Distinguish structural graph reachability, map evaluation cost and ECDLP attack complexity.
