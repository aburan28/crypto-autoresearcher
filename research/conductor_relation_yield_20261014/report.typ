#set page(paper: "a4", margin: 17mm)
#set text(size: 9.5pt)
#set heading(numbering: "1.")

= Prospective conductor-step relation-yield experiment

*Design, 2026-10-14. No new yield measurements are reported here.*

We will compare native three-summand relation occupancy on two certified prime-field crater/floor pairs. P29 uses prime conductor step 8209 at $p = 320092037$ and subgroup order $r = 320091991$. P37 uses step 131101 at $p = 81640512137$ and order $r = 81640511861$. Both endpoints within a pair share $p$, trace and prime subgroup order. The complete coefficients and generator coordinates are in `README.md` and the frozen source specs it names.

The exact group-law two-sum oracle measures mathematical relation availability. It does not measure Semaev/Gröbner solver speed or complete index-calculus cost.

#figure(image("panel.svg", width: 100%), caption: [The two prospective same-class comparisons. Blue lines denote the certified conductor-step relationship; no point evaluator is claimed.])

== What will be counted

For each endpoint, a factor base contains both signs at the first 256 rational abscissae in P29 or first 1600 in P37. A sealed scalar defines a public $Q=[k]G$; the collector cannot read $k$. For each of 32768 seeded native uniform subgroup targets $R_i=[a_i]G+[b_i]Q$, with nonzero $b_i$, the oracle will count all unordered triples from that base summing to the target. The primary yield is the fraction of targets with a verified useful triple: distinct point IDs, no opposite pair and a canonical nonzero row. Raw occupancy, multiplicity, ordered count, duplicate rows and rank-increasing rows modulo $r$ are recorded separately. The exact raw ordered-target mean $|F|^3/r$ is a conservation identity and is not a success probability.

A deduplicated two-sum table makes the 37-bit panel feasible in principle: at most $3200^2 = 10240000$ ordered pair entries before compression. The rough random-group nonempty probabilities are 0.067 and 0.065, after dividing typical distinct-triple permutations by six. These are planning calculations, not measurements.

== Controls and decision

The design includes same-cardinality random-point bases, an isomorphic-presentation null, planted triples, an independent replay subset and a fixed target-generation stream. Any transported-base arm requires an explicit map and must conserve targetwise counts; absent such a map, only native marginal comparisons are reported. We will form two within-pair floor/crater contrasts with 99% target-sampling intervals and report rank-usefulness contrasts. A lead requires both intervals to exclude one in the same direction, both point estimates to exceed 20%, and controls to pass. One purposive floor per class cannot support a population law.

The older 457-curve `GF(2^19)` arity-2 census and `GF(2^16)` four-level panel are calibration records, not new trials. The certified `GF(2^51)` 271-edge selection is a later scale panel that needs a separate feasible arity-3 oracle and explicit map work for a transport comparison. The next gate is a frozen launcher with exact triple counting, independent verification, rank accounting, resource receipts and output seals; only then can this prospective plan run.

== Provenance

All source references are internal repository artifacts, linked by path in `README.md`: `crypto/research/conductor_gap_cm_pairs_20261010`, `crypto/research/ecbench_conductor_gap_20261012`, `cryptanalysis/experiments/volcano-ic`, `research/isogeny_stratified_ml_blueprint_triage_20261010`, `research/volcano-relations-20260924`, and `research/isogeny_volcano_m51_deep_scan_20261013`. This PDF contains proposed design and derived planning arithmetic only.
