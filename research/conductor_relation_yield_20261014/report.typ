#set page(paper: "a4", margin: 15mm)
#set text(size: 8.8pt)
#set heading(numbering: "1.")

= Prospective conductor-step relation-yield experiment

*Design, 2026-10-14. No new yield measurements are reported here.*

We will compare native three-summand relation occupancy on two certified prime-field crater/floor pairs. P29 uses prime conductor step 8209 at $p = 320092037$ and subgroup order $r = 320091991$. P37 uses step 131101 at $p = 81640512137$ and order $r = 81640511861$. Both endpoints within a pair share $p$, trace and prime subgroup order. P29 floor E1 remains primary; archived E2 and E3 are declared same-conductor sensitivity arms. Coefficients and generator coordinates are in `README.md` and its source specs.

The exact group-law two-sum oracle measures mathematical relation availability. It does not measure Semaev/Gröbner solver speed or complete index-calculus cost.

#figure(image("panel.svg", width: 100%), caption: [The two primary crater/floor comparisons and the secondary P29 floor checks. Lines denote a certified isogeny class, not an evaluated point map.])

== What will be counted

For each endpoint, a factor base contains both signs at the first 256 rational abscissae in P29 or first 1600 in P37. The random-base control samples the same number of distinct liftable x-values uniformly, then includes both signs. An OS-random seed is drawn only after code is frozen; its hash and target-vector digests are committed before collection. A separately held scalar defines public $Q=[k]G$. For each of 32768 distinct nonidentity targets $R_i=[a_i]G+[b_i]Q$, with nonzero $b_i$, the oracle counts unordered triples summing to that target. Primary yield is the fraction with a verified useful triple: distinct point IDs and no opposite pair. Raw occupancy, multiplicity and ordered count are separate. The exact all-target raw ordered mean $|F|^3/r$ is a conservation identity, not a success probability.

A deduplicated two-sum table needs up to 5121600 unordered pair entries for P37. The rough random-group useful-occupancy probabilities are 0.067 and 0.065. These are planning calculations, not measurements. The known generator log is removed from unknown matrix columns; if $Q$ is itself a base point, its column is merged. Report rank after target prefixes 512, 2048, 8192 and 32768, since final rank can saturate.

== Controls and decision

The design includes random signed-pair bases, planted triples, independent replay, exact targetwise equality under a transported-base $u=2$ isomorphism, and a separate rebuilt-native-base $u=2$ coordinate-sensitivity arm. Without an explicit isogeny point map, the crater/floor comparisons use independent native marginal targets. Invert exact hypergeometric tails for each primary endpoint at 99.75% coverage; Bonferroni gives at least 99% simultaneous coverage over four endpoints. Form floor/crater ratio intervals from those bounds. A fixed-pair lead requires both intervals to exclude one in the same direction, both observed ratios to shift by at least 20%, and validity controls to pass. P29 E2/E3, coordinate sensitivity and rank prefixes remain visible even if they disagree. This convenience panel cannot isolate conductor causality or establish a general law.

The older 457-curve `GF(2^19)` arity-2 census and `GF(2^16)` four-level panel are calibration records, not new trials. The certified `GF(2^51)` 271-edge selection is a later scale panel needing its own feasible oracle and explicit map work. The next gate is a frozen launcher with exact triple counting, independent verification, rank accounting, resource receipts and output seals; only then can this prospective plan run. The implementation gap is indexed at `problems/prime-field-arity3-relation-oracle.md`.

== Provenance

All source references are internal repository artifacts, linked by path in `README.md`: `crypto/research/conductor_gap_cm_pairs_20261010`, `crypto/research/ecbench_conductor_gap_20261012`, `cryptanalysis/experiments/volcano-ic`, `research/isogeny_stratified_ml_blueprint_triage_20261010`, `research/volcano-relations-20260924`, and `research/isogeny_volcano_m51_deep_scan_20261013`. This PDF contains proposed design and derived planning arithmetic only.
