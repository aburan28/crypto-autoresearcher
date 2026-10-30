#set document(title: "Split-count null and held-out test", date: datetime(year: 2026, month: 10, day: 29))
#set page(paper: "a4", margin: (x: 2cm, y: 2cm))
#set text(size: 10pt)
#set par(justify: true)
#show heading: set text(weight: "regular", size: 13pt)
#show strong: it => underline(it.body)

= Small-prime split counts of the NIST/ANSI seed curves: null, sweep, held-out test

*Study* `research/nist_seed_split_null_20261029`, 29 October 2026 UTC. Manuscript draft: `papers/nist-seed-split-null/`. Procedural deviations D1--D3 are in `DEVIATIONS.md`.

*Question.* Do the published prime-field curves have fewer split primes (odd $ell <= 691$ with $t^2 - 4p$ a nonzero square mod $ell$) than unpublished prime-order seed candidates?

*Prime-order confound (derived).* All 19 named curves have prime order. The exact Chebotarev null conditioned on prime order has mean 59.7--60.2 and s.d. 5.5. Prime order moves the mean by only 0.5--1.4 splits, and small factors of the twist order force 0--4 splits per curve. A 48-bit SEA check matches the null (KS D = 0.023); its rerun with rows kept reproduces exactly and passes an independent audit (D2 resolved).

*Cutoff, exploratory, on the named 19.* The 25/25 within-field score holds only for $B in {691, 701, 709, 769}$. Choosing B over 655 prime cutoffs gives $p = 0.0055$ (Monte Carlo, n = 20,000) or $0.0065$ (exact permutation, 4,480 allocations). That correction does not cover the earlier choice of statistic.

*Held-out test, preregistered in Markdown before data (`bd5d146b`).* Over 42 unpublished draft-eligible curves outside the named eleven, held-out curves exceed published ones in *0.574 of 102 within-field pairs*, one-sided permutation $p = 0.29$. *The association does not replicate.* The held-out percentiles fit the null: KS $D = 0.153$ against a 5% critical value of 0.210, n = 42. One unpublished 192-bit curve has 44 splits. The one surviving extreme is prime239v1 (42 splits, 0.06th percentile), with a null tail of about 0.05 among the 61 eligible curves examined.

#figure(image("fig_heldout.svg", width: 100%), caption: [Split counts at $B = 691$ by field. Source: `runs/heldout.json`, `runs/rows.jsonl`. Drawn by `figures.py`.])

*Scope.* No hypothesis status changes, and no ECDLP mechanism is known. The selection-rule problem stays open.
