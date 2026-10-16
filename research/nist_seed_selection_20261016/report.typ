#set page(paper: "us-letter", margin: (x: 0.72in, y: 0.68in))
#set text(font: "New Computer Modern", size: 10pt)
#set par(justify: true)
#set heading(numbering: "1.")

= Reconstructed curve-seed selection window

Evidence report · 16 October 2026 · Cross-checked six-stream census

The recovered `lrand48` coordinates regenerate 31,945 named target/index
pairs, representing 22,073 distinct stream positions and including all fourteen
published anchors. The host C library independently replayed every seed.
Published-family-profile arithmetic is complete for the four binary streams
and P-192. A merged six-stream prime-order census covers all 21,753 prime
stream positions; our independent checker confirms its candidate-index set,
accepted lists, 11 omitted orders, ten published orders, and 9,275 retained
prefix rows.

== What the completed streams show

#table(
  columns: (1fr, 0.9fr, 0.9fr, 1.4fr),
  align: (left, center, center, center),
  inset: 6pt,
  [*Stream*], [*Earlier seeds*], [*Published cofactor profile*], [*X9 reference subset*],
  [B-233], [154], [0], [13],
  [B-283], [31], [0], [0],
  [B-409], [59], [0], [1],
  [B-571], [72], [0], [2],
  [P-192], [138], [0], [4],
)

The X9 column uses a 255-smooth cofactor, the minimum subgroup bounds, MOV
degrees 1–20, and the anomalous exclusion. The P-192 entry counts only
published-compatible coefficients that also match the draft's strict seed
formula; the distinct strict-formula curves still require their own counts.

#image("selection_counts.svg", width: 100%)

#pagebreak()
== Complete prime-order selection window

The retrospective selected-root screen gives 21 accepted entries: ten
published and eleven unpublished. It requires prime group order, group-order
bit length no greater than field bit length, nonanomalous order, and MOV
nontriviality for degrees below 1024. Its width test is not a minimum rule
found in the accessible September 1998 X9.62 draft; this is a reconstruction
of a reported screen, not an authenticated 1997–1998 stopping rule.

The broader cofactor-one published-family profile admits either seeded root,
uses the public minimum subgroup-size and MOV-20 tests, and applies no
unsourced order-width cap. It gives 69 seed-level entries: ten published,
eleven screen skips, seventeen wider prime-order cases, and 31 cases where
only the opposite seeded root has prime order. P-224's twist-only cases are
outside its seeded sign pair. Published P-384 has prime order on both curve
and twist; it is counted once. Independent affine-scalar and Hasse checks
certify the claimed full group order on all 82 eligible root branches.

#image("full_prime_window.svg", width: 100%)

The eleven screen skips are 239-bit indices 36, 1562, 2491, 2682, 2863;
192-bit 2198, 5405; P-256 876; and P-224 777, 1485, 5736. Shared ANSI
streams are counted once. Full candidate lists, field orders, and source
hashes are in `raw/full_census_crosscheck_v4.json`.

#pagebreak()
== Prime-family prefix: independent exact checks

The frozen pre-retry snapshot has exact results for the following earlier
indices. These partial results agree with the completed imported census on
their observed ranges. Shared ANSI streams are shown once; prime192v2 index 139
is the already published P-192 curve.

#table(
  columns: (1.1fr, 1fr, 0.8fr),
  align: (left, center, center),
  inset: 5pt,
    [*Representative stream*], [*Earlier indices evaluated*], [*Eligible seeds seen in prefix*],
  [P-224], [2,500 / 7,025], [5],
  [P-256], [1,541 / 1,841], [5],
  [P-384], [845 / 2,687], [1],
  [P-521], [230 / 1,135], [0],
  [prime239v3], [1,500 / 3,047], [5],
  [prime192v2], [2,500 / 6,012], [9],
)

#image("prefix_family.svg", width: 100%)

All thirty accepted root branches in this snapshot have an independent
affine scalar and Hasse-uniqueness certificate. The partial source files are
retained with hashes; later completed and partial P-256 retry rows are bound
in the campaign stop record and checked separately.

== Specific earlier choices

P-256 index 876 is prime order and passes the tested published cofactor-one
profile on the same exponentiation root as the published coefficient. The
published index is 1842. The other four accepted P-256 indices seen so far
(81, 276, 1049, 1383) use the opposite root. All nine published prime curves
with field prime congruent to 3 modulo 4 use the exponentiation root; that
is an observed pattern, not recovered constructor code.

P-224 index 1485 has a 224-bit prime group order larger than the published
P-224 order. It satisfies both tested seed mappings, and the two coefficient
roots are isomorphic over this field. All five earlier prime-order P-224
curves seen so far have orders larger than the published order. Thus a
minimum subgroup-size threshold that admits published P-224 cannot exclude
these earlier curves.

#pagebreak()
== Meaning of the window

The eleven earlier selected-root alternatives falsify a simple first-eligible
explanation under the displayed retrospective screen. A family cofactor preference explains
the binary and P-192 skips in the completed streams. Neither the clock value
nor the number of abandoned clock starts is authenticated. Private selection
filters and the rule for choosing a coefficient root are unknown, so these
counts do not identify intent or a hidden mathematical advantage.

== Selection-window boundary

These results condition on each published field, the fixed coefficient a,
and one reconstructed generator initialization. The recovered clock values
are coordinates that reproduce the published seeds; they are not independent
clock records. A constructor could have restarted, changed the clock input,
or applied an undocumented preference before using this stream. The audit
does not count those other possible searches.

For intact consecutive 20-draw seeds, the 48-bit LCG has at most `2^46`
distinct candidate-start states; allowing arbitrary extra draws between
intact windows raises the ceiling to `2^48`. These are recipe-specific
possibility bounds, not historical attempt counts. A roughly 30-bit estimate
requires a narrower timestamp window and a small number of chosen viable
slots; it is a scenario rather than a universal bound.

#table(
  columns: (1.1fr, 1.9fr, 2fr),
  align: left,
  inset: 5pt,
  [*Decision*], [*Fixed by this audit*], [*Still unverified*],
  [Seed stream], [All positions up to each published index under the reconstructed initialization], [Why that initialization or final index was chosen],
  [Curve coefficient], [Both seeded roots and the published SHA-1 mapping], [The historical root convention and any rejected clock starts],
  [Order and subgroup], [Prime-order census; 9,275 overlapping prefix rows; completed binary and P-192 counts], [Full X9 near-prime count and the private bounds or filters],
  [Base point], [Published points and independent subgroup-point certificates for observed survivors], [The original base-point random state and selection procedure],
)

An earlier publicly admissible curve shows available selection under the
stated reconstruction. It does not prove that the constructor considered it.
The absence of an earlier candidate in a completed stream closes only that
stream and those filters. The prime-order census deliberately aborts on
detected composite orders, so it cannot classify every near-prime curve
allowed by a chosen X9 `lmax` and `rmin`. A hidden advantage would require its own mechanism,
an executable route, subgroup preservation, and a costed comparison against
known attacks; the seed audit alone supplies none of those.

The accessible X9.62 text is a September 1998 working draft; FIPS 186-2 was
published in January 2000. Both postdate all fourteen reconstructed timestamps.
The draft's prime seed formula disagrees with six of ten published prime
anchors. Thus its rules are an explicit public reference, not an authenticated
description of the original search.

== Reproduction pointers

The complete raw candidate grid is `raw/candidates.jsonl`. Full prime-order
classification, source hashes, and overlapping exact checks are in
`raw/full_census_crosscheck_v4.json`; the imported raw point counts are in
`../nist_seed_provenance_20261016/census/`. All 82 branch certificates are in
`raw/full_prime_order_certificates.jsonl`. Binary and P-192 exact counts and
certificates are in `raw/evaluations/` and linked from `REPORT.md`. The
interrupted local prime campaign and stop/correction records remain in
`raw/family_campaign/`. Source texts: #link("https://pdfcoffee.com/x9-62-1998-ecdsa-pdf-free.html")[X9.62 working draft];
#link("https://csrc.nist.gov/files/pubs/fips/186-2/final/docs/fips186-2.pdf")[NIST FIPS 186-2].
