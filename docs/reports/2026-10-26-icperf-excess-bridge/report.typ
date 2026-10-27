#set page(paper: "us-letter", margin: 0.72in)
#set text(font: "Arial", size: 10pt)
#show raw: set text(font: "Arial")
#set par(justify: true, leading: 0.56em)

= Linearization excess and elite binary factor bases
Preparatory source assessment · 26 October 2026

The source-reported two-summand PDP fit uses `e = n - ℓ - dim(V²)` and predicts *solving degree* `2 + [e < -3.5] + [e < -8.5]` over 656 tested bases, with mean absolute error 0.06. Its homogeneous degree of regularity is `ℓ+1`. The product-space theorem of Bachoc, Serra and Zémor identifies geometric progressions in prime-degree extensions when the product span attains its minimum below dimension `n-1`. Neither statement predicts the charged cost of a chained three- or four-summand S3 system by itself.

#image("figure.svg", width: 100%)

Figure 1. Source-reported exact counts from crypto `d51b908a`, `run-20261016T1705Z`: four unsatisfiable draws per cell, all saturated through degree 4. These are random-subspace arms; `n` and `ℓ` both change. No elite-base comparison was run.

== Transfer boundary

The cryptanalysis PDP study uses direct and symmetric formulations, while the crypto closure study reconstructs a chained S3 system from saved random `v_basis` and target coordinates. The proposed bridge is a target-blind scan of equal-dimension subspaces, followed by top-`e`, median-`e` and random-control comparisons on one exact curve, system builder and held-out target list. Record actual usable-point count and cofactor class, product dimensions, construction, input density, solving degree, closure cost, censoring and certified relations. Measure novel rank and complete cost separately; equal dimension does not imply equal factor-base size or relation yield.

The pinned cryptanalysis paired MXL table reports random/structured operation ratios for symmetric `m=3` of 11.7 per query and 6.6 per derived relation across eligible small-field cells; its direct `m=3` table reports 1.46 and 1.01 on a different cell set. These are source-reported PDP stages, so the next protocol must compare formulations on the same bases and targets before transferring a cost ratio.

This is a proposed test boundary, not an approved protocol or a new performance measurement. The complete 50–63-bit prime, Koblitz and ordinary-binary arity grid remains open.

== Sources

Cryptanalysis PDP heuristics, commit `e7cf096b`; crypto chained closure results, commit `d51b908a`; Bachoc–Serra–Zémor, arXiv:1501.00602; Faugère–Perret–Petit–Renault, EUROCRYPT 2012. Full paths, blob hashes, assumptions and links are in the accompanying README.
