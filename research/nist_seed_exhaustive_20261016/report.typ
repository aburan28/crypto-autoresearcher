#set page(paper: "a4", margin: 1.4cm)
#set text(size: 9pt)
#set par(justify: true)

= A first search of the NIST prime-curve seed orbit

_16 October 2026. Bounded seed-stream extension and a disjoint numeric state shard. Exact scope, source hashes, and raw receipts are in #link("report.md")[the full report]._

The recovered 48-bit generator has 2^46 possible first states for consecutive 20-draw prime-curve seed blocks. We built a scanner that addresses those states without overlap by setting the first state to 4i + 1, for 0 <= i < 2^46. We also extended each of the six recovered timestamp streams by 1,024 blocks after its last published seed.

#figure(image("pipeline.svg", width: 94%), caption: [The two screening stages and the historical decision that this search does not observe.])

== Observed curves

The six extensions generated 6,144 seeds. Of these, 3,072 passed the coefficient square-root precheck. PARI/GP processed 2,151 candidates; 921 candidates in P-521 and P-384 remain censored by local point-counting stops. P-239, P-192, P-256, and P-224 completed their declared 1,024-block extensions.

One P-239 curve passed the recorded prime-order, bit-length, non-anomalous, and embedding-degree screens. It is block 3391 after srand48(863711343), seed d069603c0e4a2aed7fade42cf4be32702ef27a62. Its prime group order and curve coefficient are in #link("runs/run-20261016T2329Z/verify_863711343_3391.json")[the verification receipt]. An independent Python group-law check verified a nonidentity point killed by the reported prime order; Hasse's bound fixes the full order. The twist order is divisible by 29. This curve lies after the published prime239v3 block; the historical program's later actions are unknown.

P-192 block 6402 and P-224 block 7449 also have independently checked prime group orders, but those orders have 193 and 225 bits respectively, exceeding their fixed field sizes by one bit. The P-224 extension also has two GP-reported prime-order twists at blocks 7166 and 8008. The complete P-256 extension produced no final-screen survivor.

#figure(image("coverage.svg", width: 94%), caption: [Processed point-counter rows per fixed field. Pale bars show root-admitting candidates. Amber rows are censored local computations, not rejected curves.])

== Direct numeric shard and limits

The first P-256 state shard covered indices 0 through 65,535, exactly 2^-30 of the strict orbit. It found 32,835 root-admitting coefficients and 32,701 nonsquares. This stage did not compute group orders. All ten published prime-field seeds regenerated as controls at their recovered state indices. The observed local wall time was 139.0 seconds for this Python/macOS implementation; it is a measurement for this shard, not a forecast for optimized hardware.

The run retained two initial launcher/interrupt attempts and the final P-521 and P-384 partial files. The missing historical keep/skip rule remains unresolved: further generated curves add no labels for what the original program evaluated. The next computation requires a resumable per-candidate point counter for the 921 unfinished rows and a specified property before much larger orbit scans.

_Sources:_ #link("https://www.anthropic.com/research/ecdsa-curve-origins")[Anthropic, recovered generator] (retrieved); #link("https://words.filippo.io/seeds-solved/")[Valsorda, candidate screens] (retrieved); #link("report.md")[full local report and immutable run records] (internal).
