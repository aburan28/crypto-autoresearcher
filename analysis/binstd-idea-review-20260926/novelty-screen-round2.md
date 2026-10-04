# Frontier-map novelty screen of the round-2 proposals (2026-09-26 ids, filed 2026-09-28; re-run after the lanes' prior_art additions)

Command per record: `python3 tools/build_frontier_map.py --match "<title + claim>" --limit 5`. A screen, not a verdict: a matching row means a reviewer reads that row against the record before any novelty label above `unverified`; no match is not evidence of novelty. Each record's `prior_art.rows_checked` is listed beside the top hits; after the send-back round every top hit is cited.

## IDEA-20260926-0d1d74 (RQ-CERTBIN-836ce2, algorithm)
rows_checked: ['KR-IC-081a58', 'KR-IC-1fcdbc', 'KR-IC-46d822', 'KR-IC-49c882', 'KR-IC-5931ee', 'KR-IC-5a43e5', 'KR-IC-73db3f', 'KR-IC-a4dd54', 'KR-IC-b0fcda', 'KR-RHO-13bf67']

```
KR-IC-5a43e5  score=32  [known_mechanism/proven]  Semaev summation polynomials
KR-IC-73db3f  score=28  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
KR-RHO-13bf67  score=25  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
KR-IC-f5c584  score=22  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
KR-IC-49c882  score=19  [known_bound/conjectured]  Quasi-subfield polynomials
```

## IDEA-20260926-120d6a (RQ-BINSTD-b6f698, control)
rows_checked: ['KR-IC-081a58', 'KR-IC-1fcdbc', 'KR-IC-5a43e5', 'KR-IC-73db3f', 'KR-IC-8b9daa', 'KR-IC-955fd6', 'KR-IC-b0fcda', 'KR-IC-fbdb61', 'KR-RHO-037e22']

```
KR-IC-73db3f  score=52  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
KR-IC-955fd6  score=31  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
KR-IC-5a43e5  score=28  [known_mechanism/proven]  Semaev summation polynomials
KR-IC-f5c584  score=26  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
KR-IC-b0fcda  score=24  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
```

## IDEA-20260926-197ecf (RQ-FROB-7d8dd4, mechanism)
rows_checked: ['KR-IC-1fcdbc', 'KR-IC-5765d2', 'KR-IC-5a43e5', 'KR-IC-73db3f', 'KR-IC-955fd6', 'KR-IC-b0fcda', 'KR-IC-f5c584', 'KR-RHO-037e22', 'KR-RHO-13bf67', 'KR-RHO-18cc42']

```
KR-IC-73db3f  score=28  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
KR-IC-5ea2f8  score=24  [known_mechanism/proven]  GHS Weil descent and cover attacks
KR-IC-f5c584  score=24  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
KR-IC-5a43e5  score=23  [known_mechanism/proven]  Semaev summation polynomials
KR-RHO-037e22  score=23  [known_mechanism/proven]  Frobenius classes on Koblitz curves: sqrt(2m)
```

## IDEA-20260926-1ddce2 (RQ-ICPERF-94c86e, control)
rows_checked: ['KR-IC-1fcdbc', 'KR-IC-5765d2', 'KR-IC-5a43e5', 'KR-IC-73db3f', 'KR-IC-889857', 'KR-IC-8b9daa', 'KR-IC-e847d1', 'KR-IC-f5c584', 'KR-IC-fbdb61', 'KR-RHO-18cc42']

```
KR-IC-f5c584  score=27  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
KR-IC-73db3f  score=26  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
KR-IC-5a43e5  score=24  [known_mechanism/proven]  Semaev summation polynomials
KR-IC-955fd6  score=22  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
KR-IC-fbdb61  score=17  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
```

## IDEA-20260926-201e86 (RQ-BINSTD-b6f698, mechanism)
rows_checked: ['KR-IC-0d2021', 'KR-IC-5931ee', 'KR-IC-73db3f', 'KR-IC-b0fcda', 'KR-RHO-037e22', 'KR-RHO-13bf67']

```
KR-RHO-13bf67  score=34  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
KR-IC-b0fcda  score=31  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
KR-IC-5931ee  score=27  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
KR-IC-73db3f  score=27  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
KR-IC-9e610d  score=26  [textbook_fact/reported]  Survey consensus (2016)
```

## IDEA-20260926-20ba8f (RQ-BINSTD-b6f698, mechanism)
rows_checked: ['KR-IC-081a58', 'KR-IC-46d822', 'KR-IC-5931ee', 'KR-RHO-13bf67', 'KR-RHO-18cc42', 'KR-RHO-46c2c6', 'KR-RHO-7d93f6', 'KR-RHO-ea34b8']

```
KR-IC-5931ee  score=32  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
KR-RHO-13bf67  score=30  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
KR-IC-a4dd54  score=27  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
KR-RHO-46c2c6  score=27  [known_bound/proven]  Multi-target and batch discrete logarithms
KR-RHO-ea34b8  score=26  [known_bound/proven]  Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
```

## IDEA-20260926-3c6a19 (RQ-CERTBIN-836ce2, mechanism)
rows_checked: ['KR-IC-0d2021', 'KR-IC-1fcdbc', 'KR-IC-46d822', 'KR-IC-5931ee', 'KR-IC-5a43e5', 'KR-IC-fbdb61', 'KR-RHO-13bf67']

```
KR-IC-5931ee  score=24  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
KR-IC-a4dd54  score=23  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
KR-IC-46d822  score=22  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
KR-IC-1fcdbc  score=20  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
KR-RHO-18cc42  score=20  [record/reported]  ECC2K-130: expected work and 2009–2010 implementation rates
```

## IDEA-20260926-3cc0b8 (RQ-ICPERF-94c86e, control)
rows_checked: ['KR-IC-73db3f', 'KR-IC-ae532f', 'KR-RHO-18cc42', 'KR-RHO-6239aa', 'KR-RHO-7d93f6', 'KR-RHO-cb1c58', 'KR-RHO-e7f98e']

```
KR-IC-73db3f  score=24  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
KR-RHO-18cc42  score=23  [record/reported]  ECC2K-130: expected work and 2009–2010 implementation rates
KR-RHO-e7f98e  score=22  [record/reported]  GPU Pollard rho: academic state of the art is thin
KR-RHO-cd86f5  score=20  [known_mechanism/measured]  r-adding walks and the walk constant
KR-RHO-13bf67  score=17  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
```

## IDEA-20260926-5c26f9 (RQ-BINSTD-b6f698, measurement)
rows_checked: ['KR-IC-49c882', 'KR-IC-5ea2f8', 'KR-IC-73db3f', 'KR-IC-a4dd54', 'KR-IC-b0fcda', 'KR-IC-f5c584']

```
KR-IC-f5c584  score=26  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
KR-IC-fbdb61  score=25  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
KR-RHO-13bf67  score=25  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
KR-RHO-755e35  score=25  [textbook_fact/proven]  Isogenous curves are equally hard; isogeny walks do not find weak curves
KR-IC-73db3f  score=22  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
```

## IDEA-20260926-6f2601 (RQ-BINSTD-b6f698, control)
rows_checked: ['KR-IC-49c882', 'KR-IC-73db3f', 'KR-IC-b0fcda', 'KR-IC-f5c584']

```
KR-IC-73db3f  score=28  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
KR-IC-5a43e5  score=24  [known_mechanism/proven]  Semaev summation polynomials
KR-RHO-13bf67  score=24  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
KR-IC-f5c584  score=23  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
KR-IC-5931ee  score=19  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
```

## IDEA-20260926-80209d (RQ-BINSTD-b6f698, control)
rows_checked: ['KR-IC-1fcdbc', 'KR-IC-73db3f', 'KR-IC-a4dd54', 'KR-IC-b0fcda']

```
KR-IC-73db3f  score=25  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
KR-IC-5931ee  score=24  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
KR-RHO-755e35  score=23  [textbook_fact/proven]  Isogenous curves are equally hard; isogeny walks do not find weak curves
KR-RHO-037e22  score=22  [known_mechanism/proven]  Frobenius classes on Koblitz curves: sqrt(2m)
KR-IC-5a43e5  score=21  [known_mechanism/proven]  Semaev summation polynomials
```

## IDEA-20260926-9c5694 (RQ-CERTBIN-836ce2, control)
rows_checked: ['KR-IC-1fcdbc', 'KR-IC-5a43e5', 'KR-IC-73db3f', 'KR-IC-8b9daa', 'KR-IC-955fd6', 'KR-IC-b0fcda', 'KR-IC-f3da82', 'KR-RHO-037e22']

```
KR-IC-73db3f  score=30  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
KR-RHO-755e35  score=29  [textbook_fact/proven]  Isogenous curves are equally hard; isogeny walks do not find weak curves
KR-RHO-037e22  score=24  [known_mechanism/proven]  Frobenius classes on Koblitz curves: sqrt(2m)
KR-IC-5a43e5  score=22  [known_mechanism/proven]  Semaev summation polynomials
KR-IC-b0fcda  score=21  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
```

## IDEA-20260926-9cc043 (RQ-CERTBIN-836ce2, measurement)
rows_checked: ['KR-IC-0d2021', 'KR-IC-1fcdbc', 'KR-IC-5a43e5', 'KR-IC-73db3f', 'KR-IC-889857', 'KR-IC-f5c584', 'KR-IC-fbdb61']

```
KR-IC-73db3f  score=26  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
KR-IC-5a43e5  score=25  [known_mechanism/proven]  Semaev summation polynomials
KR-IC-1fcdbc  score=23  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
KR-IC-955fd6  score=22  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
KR-IC-f5c584  score=21  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
```

## IDEA-20260926-b11cb1 (RQ-SATIC-1ae57a, measurement)
rows_checked: ['KR-IC-1fcdbc', 'KR-IC-5765d2', 'KR-IC-73db3f', 'KR-IC-e847d1', 'KR-IC-f5c584', 'KR-RHO-13bf67']

```
KR-IC-5765d2  score=37  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
KR-IC-73db3f  score=27  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
KR-IC-f5c584  score=25  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
KR-IC-fbdb61  score=23  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
KR-RHO-13bf67  score=22  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
```

## IDEA-20260926-bbf2ed (RQ-CERTBIN-836ce2, representation)
rows_checked: ['KR-IC-1fcdbc', 'KR-IC-5765d2', 'KR-IC-5a43e5', 'KR-IC-73db3f', 'KR-IC-b0fcda', 'KR-IC-f5c584', 'KR-IC-fbdb61', 'KR-RHO-037e22', 'KR-RHO-13bf67', 'KR-RHO-18cc42']

```
KR-IC-73db3f  score=46  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
KR-IC-f5c584  score=41  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
KR-IC-b0fcda  score=32  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
KR-IC-5931ee  score=28  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
KR-IC-5a43e5  score=23  [known_mechanism/proven]  Semaev summation polynomials
```

## IDEA-20260926-bc1cab (RQ-QSP-f9bbdb, control)
rows_checked: ['KR-IC-49c882', 'KR-IC-5ea2f8', 'KR-IC-64659b', 'KR-IC-73db3f', 'KR-IC-b0fcda', 'KR-RHO-13bf67', 'KR-RHO-18cc42']

```
KR-IC-49c882  score=21  [known_bound/conjectured]  Quasi-subfield polynomials
KR-RHO-755e35  score=16  [textbook_fact/proven]  Isogenous curves are equally hard; isogeny walks do not find weak curves
KR-RHO-13bf67  score=15  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
KR-RHO-53c89f  score=15  [textbook_fact/proven]  Transfer attacks apply only to special curves
KR-IC-73db3f  score=13  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
```

## IDEA-20260926-beb5b6 (RQ-BINSTD-b6f698, control)
rows_checked: ['KR-IC-5931ee', 'KR-IC-5a43e5', 'KR-IC-73db3f', 'KR-RHO-037e22', 'KR-RHO-13bf67', 'KR-RHO-18cc42', 'KR-RHO-38be82', 'KR-RHO-46c2c6', 'KR-RHO-6239aa', 'KR-RHO-7d93f6', 'KR-RHO-ea34b8']

```
KR-IC-5931ee  score=41  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
KR-RHO-6239aa  score=37  [known_mechanism/proven]  Parallel collision search with distinguished points
KR-RHO-46c2c6  score=35  [known_bound/proven]  Multi-target and batch discrete logarithms
KR-IC-73db3f  score=31  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
KR-RHO-13bf67  score=28  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
```

## IDEA-20260926-c98e92 (RQ-ICPERF-94c86e, measurement)
rows_checked: ['KR-IC-1fcdbc', 'KR-IC-5765d2', 'KR-IC-5a43e5', 'KR-RHO-13bf67', 'KR-RHO-18cc42', 'KR-RHO-825bca', 'KR-RHO-cb1c58']

```
KR-RHO-cb1c58  score=23  [known_mechanism/proven]  Simultaneous (batched) inversion
KR-RHO-53c89f  score=21  [textbook_fact/proven]  Transfer attacks apply only to special curves
KR-IC-f5c584  score=20  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
KR-RHO-13bf67  score=19  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
KR-IC-955fd6  score=18  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
```

## IDEA-20260926-d06324 (RQ-CERTBIN-836ce2, control)
rows_checked: ['KR-IC-73db3f', 'KR-IC-f5c584', 'KR-RHO-037e22', 'KR-RHO-13bf67', 'KR-RHO-38be82', 'KR-RHO-5b1c0a', 'KR-RHO-cd86f5', 'KR-RHO-fb88e6']

```
KR-IC-f5c584  score=30  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
KR-RHO-037e22  score=29  [known_mechanism/proven]  Frobenius classes on Koblitz curves: sqrt(2m)
KR-IC-b0fcda  score=27  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
KR-IC-5931ee  score=26  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
KR-IC-1fcdbc  score=24  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
```

## IDEA-20260926-d1adfc (RQ-ICPERF-94c86e, measurement)
rows_checked: ['KR-IC-0d2021', 'KR-IC-1fcdbc', 'KR-IC-5765d2', 'KR-IC-5931ee', 'KR-RHO-93979e', 'KR-RHO-cd86f5']

```
KR-IC-5931ee  score=24  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
KR-IC-1fcdbc  score=23  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
KR-RHO-13bf67  score=23  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
KR-IC-a4dd54  score=21  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
KR-IC-46d822  score=20  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
```

## IDEA-20260926-d3c5a5 (RQ-CERTBIN-836ce2, tooling)
rows_checked: ['KR-IC-1fcdbc', 'KR-IC-46d822', 'KR-IC-5a43e5', 'KR-IC-73db3f', 'KR-RHO-13bf67', 'KR-RHO-5b1c0a', 'KR-RHO-cb1c58', 'KR-RHO-fbd582']

```
KR-IC-5a43e5  score=30  [known_mechanism/proven]  Semaev summation polynomials
KR-IC-73db3f  score=29  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
KR-IC-5931ee  score=26  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
KR-RHO-cb1c58  score=23  [known_mechanism/proven]  Simultaneous (batched) inversion
KR-IC-1fcdbc  score=22  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
```

## IDEA-20260926-dacb83 (RQ-ICPERF-94c86e, measurement)
rows_checked: ['KR-IC-0d2021', 'KR-IC-46d822', 'KR-IC-a4dd54', 'KR-IC-b0fcda', 'KR-RHO-18cc42', 'KR-RHO-6239aa', 'KR-RHO-7d93f6', 'KR-RHO-ea34b8']

```
KR-RHO-6239aa  score=33  [known_mechanism/proven]  Parallel collision search with distinguished points
KR-RHO-46c2c6  score=20  [known_bound/proven]  Multi-target and batch discrete logarithms
KR-RHO-ea34b8  score=20  [known_bound/proven]  Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
KR-IC-f5c584  score=19  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
KR-RHO-e7f98e  score=19  [record/reported]  GPU Pollard rho: academic state of the art is thin
```
