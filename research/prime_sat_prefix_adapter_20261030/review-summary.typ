#set page(paper: "a4", margin: (x: 16mm, y: 14mm), numbering: "1")
#set text(font: "DejaVu Sans", size: 9.2pt)
#set par(justify: false, leading: 0.42em)
#set heading(numbering: none)
#text(size: 19pt, weight: "bold")[Prefix transcripts now have an arithmetic-validated adapter]

#text(fill: rgb("#235a3a"), weight: "bold")[DEC-20261030-676356 · scoped software acceptance]

All *seven independent joints hold*. One independently authored suite executed *148 named cases and 1,887 assertion evaluations*, all passing, with zero forbidden solver/search calls. The four fixed curve arms agree with the original exhaustive verifier. Acceptance covers this implementation and fixed checking behavior; no measured solver advantage follows.

The additive APIs are `verify_transcript(...)` and `verify_encoding_search(cell, arm, answer)`. The original encoding, arithmetic core and prefix utility remain unchanged. There is no operational expected-census argument, solver invocation or historical PNEXT replay.

#table(columns: (1.35fr,0.4fr,3.25fr), inset: 4pt, stroke: 0.4pt + rgb("#c5d1db"),
 table.header([*Joint: holds*],[*Cases*],[*Actual fixed observation*]),
 [Canonical schema],[66],[Malformed scalars, masks/aliases, coefficients, containers and missing fields fail. Invalid records after a closing proof are still checked.],
 [Prefix identities],[18],[Separate variable-set arithmetic confirms the nonconstant identity; corrupted coefficients, restrictions and clauses fail.],
 [Model/fiber scope],[9],[Models and bounds are checked, repeated projections rejected, and four full roots correctly yield two returned projections.],
 [Exact domain],[19],[Numeric bounds agree with tiny CNF oracles. Missing, repeated, below-bound, partial and projected clauses fail, including malformed empty-domain records.],
 [Coverage/censoring],[5],[A hole rejects complete status. Covered censored input stays censored. The n=256 constant-refutation fixture uses one prefix/node.],
 [Legacy integration],[28],[All four fixed arms match old verification for complete/censored acceptance and five prescribed negative mutations.],
 [Execution/custody],[3],[One actual successful suite; source/harness hashes unchanged; no guard-sentinel call or post-execution repair.],
)

#v(3pt)
#image("review-summary.svg", width: 100%)
#text(size: 7.7pt)[Fixed software observations, not a benchmark. Source: adapter.py; independent test_independent_adapter.py, independent-results.json and review.md under TASK-20261030-8e7037/. Exact inputs, commands and hashes: review-inputs.json.]

#pagebreak()
#text(size: 16pt, weight: "bold")[Projected completeness, with explicit boundaries]

Every generator and multiplier is parsed canonically. Each restricted identity must equal one; every model must satisfy the original equations and supported domain. Repeated projections are rejected. Only then are refuted prefixes and valid model-projection cylinders given to the trie. Any actual root avoids a refuted cylinder, so complete coverage puts its *projection* in the returned set. One model does not make every auxiliary assignment in its cylinder a root.

The supported domain is the full cube or the exact legacy full-width auxiliary-range CNF. Shape, distinct excluded values and cardinality establish the range without enumerating missing assignments. Arbitrary CNF is unsupported. `cover_complete` records coverage; `projected_model_set_complete` additionally requires declared complete. Censored remains censored. A coverage gap is not an arithmetic SAT witness.

For the fixed *p=5, a=b=1, s=2, R=(0,1)* cell, the separate curve/group oracle yields pairs *(2,3), (3,2), (3,3)* and packed projections *11,14,15* in all four arms. Full canonical witnesses are 11,14,15 for quartic/membership and 11,14,79 for quadratic variants. The known P=(2,4), Q=(3,4) witness sums to R. Missing model14, missing invalid leaf0, corrupted multiplier, invalid model0 and duplicate projection14 are rejected by both old and new interfaces.

Tiny enumeration is confined to the fixed generic n≤5 cases and this n≤7 compatibility fixture. The synthetic n=256 constant-one refutation has no enumeration oracle and is *not a 256-bit curve or ECDLP result*. Raising sentinels guard solver/refutation/search entry points; none fired. Source inspection also finds no cube loop in the adapter’s completeness phase.

Generic identities are checked modulo integer p≥2 with `prime_field_verified=false`. The EC interpretation assumes mathematical primality and the wrapper’s curve/target/digit premises. Decoded-mask aliases are rejected; raw JSON duplicate-identical-key parsing is outside the API.

#text(weight: "bold")[Costs remain separated.]
Parsing, restriction, identity term-pair arithmetic, model checks, domain validation and trie counts are separate from construction/reconstruction. Input/trie work follows the number of prefixes plus total depth, with at most one plus that depth sum allocated nodes; integer/input/output costs are additional. Certificates may be large, range CNF may contain 2^w−p clauses, and membership construction still builds its truth table. Its fixed fixture records 32 curve tests and 64 transform subtractions as construction costs. Only certificate-completeness checking removes the old explicit 2^n exhaustion loop; no whole-pipeline or timing claim follows.

#text(weight: "bold")[Evidence and qualifications.]
Producer receipts retain successful attempts of 239 then 242 assertions; the second added three already specified rejection checks before snapshot, without changing adapter or fixtures. Independent evidence contains 148 named cases and 1,887 evaluations in one invocation. These are different units: no sum, ratio or independent-sample interpretation.

Coordinator verified actual hashes, embedded harness bytes, all case outcomes and per-joint tallies. The unchanged native gate passed at *2026-10-30 02:14:17 UTC*. Formatting-only receipt compaction was independently checked against both the disclosed original pretty-file SHA and canonical digest; no extra execution occurred. The manifest embeds the actual gate receipt and full custody details.

One independent reviewer read permitted target code but not producer new tests/results. This is software execution independence, not blind theorem derivation. Disclosed procedure qualifications concern a missing policy path, a restored policy read before execution but after harness drafting, and a mandatory non-scientific external runtime-policy read. No mathematical unblinding or target edit was reported. Serving model/effort and opaque session identity remain unauthenticated.

Root’s scoped hygiene/artifact checks passed; full ledger validation refused *155,609 off-disk tracked paths*, without bypass. A prior-branch in-progress checkpoint/readback passed, with no restore test. Root records final PDF inspection, ten-path archive and final checkpoint outcomes separately. Historical diagrams and statuses remain unchanged.

Finite tests establish no universal correctness, formal proof, novelty, degree gain, runtime speedup or scalar recovery. *GOAL-PFDR-fd09e0 remains active*; no H/EV/KN transition and no rewrite of historical PNEXT invalid_output. Future arbitrary-trail clauses need a different completeness interface or explicit prefix restriction. Partial-trail search, local membership construction and modular coefficient-root checks remain unadmitted follow-ons.
