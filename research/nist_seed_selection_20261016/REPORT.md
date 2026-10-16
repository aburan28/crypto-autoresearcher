# Reconstructed 1997–1998 curve-seed selection window

**Status, 2026-10-16:** Seed and coefficient enumeration is complete for all
14 published anchors and all 31,931 earlier target/index pairs. Exact
published-family-profile acceptance is complete for the four binary streams
and P-192. A separately
merged six-stream prime-order census covers all 21,753 prime stream positions;
our [independent source-bound cross-check](raw/full_census_crosscheck_v4.json)
confirms its 11,042 seeded coefficient candidates, 21 accepted entries under
the retrospective screen, and all 11 unpublished entries. The original
interrupted prime-family run is preserved as an independent partial check;
its 9,275 retained prefix rows agree with the full census wherever the profiles
overlap. Complete X9.62 near-prime counts and the historical private
acceptance rule remain unresolved.
This is a historical parameter-selection audit, not a claim about the
constructors' intentions or an ECDLP algorithm.

## Question and sources

How many earlier seeds in each reconstructed `lrand48` stream produce curves
that meet explicit public acceptance references, and where does unexplained
choice remain? The accessible X9.62 text is a September 1998 working draft;
FIPS 186-2 was published in January 2000. Both postdate all fourteen
recovered 1997–1998 timestamps, so neither authenticates the private stopping rule.

- **[internal]** The user-supplied article, whose SHA-256, timestamps, indices,
  and local intake path are frozen in [SOURCE.json](SOURCE.json). The dates and
  indices are reproduced generator coordinates, not independently dated
  historical clock records.
- **[retrieved]** [X9.62 working draft, 20 September 1998, §§5.1 and Annexes A.1–A.3](https://pdfcoffee.com/x9-62-1998-ecdsa-pdf-free.html):
  subgroup order, near-primality, MOV-20, anomalous exclusion, seeded
  coefficients, and point generation. The text permits `lmax` and `rmin` to
  be chosen within stated constraints; it gives 255 as an example `lmax`.
- **[retrieved]** [NIST FIPS 186-2, 27 January 2000, Appendix 6](https://csrc.nist.gov/files/pubs/fips/186-2/final/docs/fips186-2.pdf):
  unmasked prime SHA-1 mapping, binary normal-basis mapping and conversion,
  prime cofactor one and pseudorandom binary cofactor two in the published
  family.
- **[retrieved]** [NIST SP 800-186](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-186.pdf):
  later independent table of published parameters and basis conversion. It
  is a parameter cross-check, not the historical acceptance rule.

The frozen [protocol](PROTOCOL.md) defines every target and candidate,
including both prime coefficient roots, and
[AMENDMENT_1.md](AMENDMENT_1.md) states the prospective exact torsion
rejections used in the prime family-profile campaign;
[AMENDMENT_3.md](AMENDMENT_3.md) freezes its execution-only continuation.
The [campaign stop record](raw/family_campaign/campaign_stop.json) and its
[count correction](raw/family_campaign/campaign_stop_correction.json) bind the
completed retry and later partial file after a complete census landed.
No private
construction log, start/stop rule, or base-point random state was supplied.
P-192 and the two other prime192 targets share one seed stream; the three
prime239 targets share another. Final counts will distinguish an earlier
candidate already published as another curve from an unpublished alternative.
An earlier output in the reconstructed stream is not evidence that a historical
program actually tested that output as a curve; the program's control flow is
not available.

## Completed generation and controls

The 48-bit `lrand48` recurrence reproduces all 14 published 160-bit seeds at
the article's indices. The FIPS SHA-1 relation reproduces all ten published
prime coefficients; SHA-1 interpreted in a Gaussian normal basis, followed by
the FIPS Appendix 6.9 conversion, reproduces all four binary coefficients.
[candidates.jsonl](raw/candidates.jsonl) contains every one of the 31,945
target/index pairs, including anchors. Because two prime-field groups reuse
their generator streams, these are 22,073 distinct stream positions, not
31,945 independent seeds. The
[screening_summary.json](raw/screening_summary.json) recomputes the counts.
An independent replay using the host C library's `srand48`/`lrand48` matched
all 31,945 raw seeds in [libc_replay.json](raw/libc_replay.json).
All 21 altered-seed, altered-coefficient, singularity, and basis controls in
[controls.json](raw/controls.json) passed. Each exact-count JSONL header binds
the candidate-file SHA-256. The 10 published prime orders and P-256 index 876
also have independent scalar-multiplication/Hasse certificates in
[prime_order_certificates.json](raw/prime_order_certificates.json).

**A standards-text mismatch matters.** The strict bit-clearing step in the
accessible X9.62-1998 prime generator reproduces only four of the ten
published prime coefficients: P-192, prime192v2, prime192v3, and prime239v2.
It does not reproduce the standard's own prime239v1 example. The main stream
therefore uses the unmasked FIPS mapping that matches all ten, while retaining
the strict-X9 variant for each candidate. This discrepancy does not identify
which unpublished draft or program the 1997 constructors used.

## Exact completed acceptance results

The family profile means the published field, `a`, and cofactor: one for prime
curves, two for B curves, with a prime subgroup, subgroup-size bounds, MOV-20,
and anomalous exclusion. The X9 reference column uses a 255-smooth cofactor,
the minimum subgroup bounds, MOV-20, and anomalous exclusion. For P-192, the
displayed subset also requires the unmasked coefficient to equal the strict
X9 seed formula; candidates whose two mappings differ await exact count. A qualifying
prime subgroup implies that a generator exists; independent subgroup-point
certificates are retained for all 16 binary and four strict-X9 P-192 earlier
survivors. This tests a public reference criterion, not an unknown private
choice of `lmax` or `rmin`.

| Stream | Earlier indices exactly evaluated | Earlier family-profile eligible | Earlier X9 255-reference eligible in displayed subset |
| --- | ---: | ---: | ---: |
| B-233 | 154 | 0 | 13 |
| B-283 | 31 | 0 | 0 |
| B-409 | 59 | 0 | 1 |
| B-571 | 72 | 0 | 2 |
| P-192 | 138 | 0 | 4 |

The earlier binary X9-reference indices are B-233 **9, 18, 51, 57, 62, 78,
107, 123, 124, 126, 134, 135, 138**; B-409 **17**; and B-571 **16, 55**.
The earlier P-192 indices where the unmasked and strict seed formulas agree
and the X9 reference order checks pass are **7, 14, 97, 121**. This is the
intersection of two mappings, not the full strict-X9 count. The list of seeds,
coefficients, cofactors, prime subgroup orders, and bit lengths is in
[analysis_summary.json](raw/analysis_summary.json). Four P-192 orders were
certified independently in
[p192_skipped_x9_certificates.json](raw/p192_skipped_x9_certificates.json),
and all 16 binary survivors in
[binary_all_skipped_x9_certificates.json](raw/binary_all_skipped_x9_certificates.json).

P-192 has another 11 earlier curves that pass the X9 order/security tests on
the published-compatible unmasked coefficients, but whose coefficients change
under the strict X9 bit-clearing formula. Their 15 total indices and exact
branch-specific values are in `analysis_summary.json`; the 11 are **not**
counted in the strict-X9 table above.

The X9 reference count depends on choices the draft leaves open. Among
the 20 earlier survivors displayed above, the counts whose smooth
cofactor uses only prime factors at or below `lmax` are:

| `lmax` | 7 | 15 | 31 | 63 | 127 | 255 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Subgroup `> 2^160` and `> 4√q` | 4 | 4 | 9 | 14 | 14 | 20 |

All 20 have subgroup order above `2^180`; 16 exceed `2^200`. The full
[sensitivity record](raw/x9_sensitivity.json) identifies each candidate
under every displayed bound. No historical `lmax` or `rmin` is recovered.

## Complete prime-order census: two explicit screens

The [merged census](../nist_seed_provenance_20261016/README.md) used PARI/GP
`ellsea(E,1)` on every seeded coefficient candidate in the six recovered
prime streams. As specified by the [PARI/GP manual](https://pari.math.u-bordeaux.fr/pub/pari/manuals/2.15.4/users.pdf),
its zero means an early abort after a detected small factor;
such a candidate cannot have prime group order. Our
[cross-check code](crosscheck_full_census.py) independently reclassified all
positive orders with PARI/GP 2.17.3, matched the exact candidate-index set
against our independently generated seeds, matched all eleven omitted orders
against the separate [curve assessment](../nist_seed_skipped_curves_20261016/report.md),
and matched ten published orders. Across our 9,275 retained prefix rows, 277
selected-root and 423 other-root exact order values were available in both
records and agreed. The checker also reproduced the source classifier's six
lists. Its first attempt wrongly assumed a selected curve and its twist could
not both have prime order; published P-384 disproved that assumption. The
[failed attempt](raw/full_census_attempt1.json) and raw GP output are retained.
An [independent affine-scalar/Hasse replay](raw/full_prime_order_certificates.jsonl)
certifies the claimed prime group order for **all 82 eligible root branches**
across the 69 seed-level entries, binding each field, coefficient, order,
seed, and stream index. This tests all accepted branches directly; it does
not recompute the censored composite orders. The merged copy omits its native
candidate enumerator and census driver (as its
[source note](../nist_seed_provenance_20261016/SOURCE.md) states); our separate
seed file, exact overlap, and accepted-branch certificates provide the
cross-checks available in this checkout.

The **retrospective screen** is the explicit filter in the merged census:
selected exponentiation root, prime group order, `bitlen(n) <= bitlen(p)`,
`n != p`, and MOV nontriviality for `1 <= k < 1024`. It gives the same 21
entries as the source classifier: ten published and eleven unpublished. The
order-width test is *not* a minimum rule found in the accessible X9.62-1998
draft, and that draft postdates the reported clock values. Thus this screen
reproduces the reported skip set; it is not an authenticated 1997–1998
constructor rule.

The **broader published-family profile** fixes each published prime field and
`a=-3`, uses the unmasked coefficient mapping that reproduces the anchors,
allows either seeded square-root branch, and requires prime order, cofactor
one, the public minimum subgroup-size bound, MOV-20, and `n != p`. It imposes
no unsourced order-width cap. The complete census finds **69 seed-level
eligible entries**: ten published and **59 earlier alternatives**. They split
into the eleven retrospective-screen skips, seventeen selected-root prime
orders wider than their fields, and 31 prime orders on only the opposite
seeded root. P-224 has `p = 1 mod 4`, so its two seeded signs are isomorphic;
its sixteen *quadratic-twist-only* entries in the imported file are not
seeded-root alternatives. Published P-384 has prime order on both curve and
twist and is counted once.

| Distinct prime stream | Published | Screen skips | Wider prime order | Opposite seeded root only | Broader family total |
| --- | ---: | ---: | ---: | ---: | ---: |
| 239-bit ANSI | 3 | 5 | 0 | 9 | 17 |
| 192-bit NIST/ANSI | 3 | 2 | 7 | 14 | 26 |
| P-521 | 1 | 0 | 0 | 0 | 1 |
| P-256 | 1 | 1 | 0 | 4 | 6 |
| P-384 | 1 | 0 | 2 | 4 | 7 |
| P-224 | 1 | 3 | 8 | 0 | 12 |
| **Total** | **10** | **11** | **17** | **31** | **69** |

The eleven unpublished screen entries, with one-based indices, are 239-bit
**36, 1562, 2491, 2682, 2863**; 192-bit **2198, 5405**; P-256 **876**;
and P-224 **777, 1485, 5736**. All lists and full seeds are in the
[machine-readable cross-check](raw/full_census_crosscheck_v4.json). The
[complete-window graph](full_prime_window.svg) keeps published controls,
screen skips, the width-filtered candidates, and opposite-root alternatives
distinct. The same seed stream serves multiple named ANSI curves: an earlier
candidate already published as another curve is not another unpublished
alternative.

## P-256's earlier cofactor-one candidates and root choice

At index **876**, the P-256 stream produces seed
`50C71A63F911DB7B2F31618ECF609D37154437F9` and canonical coefficient
`A84FCA4BE639727675CCEA4A9CECDA4B900C32DD7E86192AB71B355FDE8255BD`.
Its group order is the prime
`115792089210356248762697446949407573529980276179566407717841077783673421468943`.
It passes the published cofactor-one profile and MOV/anomalous checks; its
coefficient also agrees with the strict X9 seed formula. The exact count is
in [P-256/00876-00876.jsonl](raw/evaluations/P-256/00876-00876.jsonl)
and the independent order certificate is in
`raw/prime_order_certificates.json`. The imported full prime-order census
confirms that this is the sole earlier P-256 candidate on the published-style
root that passes its retrospective screen.

The frozen pre-retry snapshot covers 1,541 of 1,841 earlier P-256 indices and
finds four additional prime-order curves at **81, 276, 1049, 1383**, all on
the opposite square-root branch from the published-style exponentiation root.
The [exact segment files](raw/family_evaluations/P-256/) retain both orders.
Independent affine-scalar and Hasse certificates for all five earlier
family-profile branches are in
[prefix_certificates.jsonl](raw/family_campaign/prefix_certificates.jsonl);
the earlier three-candidate control remains in
[p256_early_root_certificates.json](raw/p256_early_root_certificates.json).
All nine published prime anchors with `p = 3 mod 4` use
the root given by exponentiation to `(p+1)/4`; [the root-choice record](raw/root_choice_pattern.json)
checks this pattern. It suggests a plausible deterministic root convention
under which indices 81 and 276 would not qualify, but the constructor's
source code has not been recovered.

## Exact prime-family prefixes and the P-224 discriminator

The [frozen continuation plan](raw/family_campaign/retry_plan.json) records
the SHA-256 of each original complete shard and retained partial prefix. The
following counts use only those bound source segments, omit each
representative stream's published endpoint, and are **independent prefix
checks** of the full census, not its totals. A qualifying seed is counted once even if
both coefficient roots pass.

| Representative stream | Earlier indices counted / earlier indices total | Family-profile eligible seeds seen |
| --- | ---: | ---: |
| P-224 | 2,500 / 7,025 | 5 |
| P-256 | 1,541 / 1,841 | 5 |
| P-384 | 845 / 2,687 | 1 |
| P-521 | 230 / 1,135 | 0 |
| prime239v3 | 1,500 / 3,047 | 5 |
| prime192v2 | 2,500 / 6,012 | 9 |

The prime239 and prime192 representatives each cover several named curves
with the same generator stream. In particular, prime192v2 index **139** is
the already published P-192 curve; it is an earlier output for the later ANSI
curves but not an unpublished alternative. The [coverage graph](prefix_family.svg)
places accepted indices against all unevaluated positions.

P-224's five earlier prime-order indices are **77, 777, 1485, 2232, 2328**.
Every one has group order **larger** than the published P-224 order. Indices
77, 2232, and 2328 have a 225-bit order on a 224-bit field; a separate,
unsourced order-width cap would exclude those three. Indices **777** and
**1485** have 224-bit orders. Index **1485** also agrees with the accessible
X9 prime seed formula. Because the two `b` roots for P-224 are isomorphic
over its field, a root-choice rule cannot remove it. The public X9 minimum
subgroup-size rule cannot remove any of these five while retaining published
P-224: each has a larger prime order. All ten P-224 root branches, and all
thirty accepted branches in the frozen prefix snapshot, passed independent
affine-scalar/Hasse checks in [prefix_certificates.jsonl](raw/family_campaign/prefix_certificates.jsonl).

The P-384 prefix has one prime-order alternative, index **592**, on the
opposite root. The prime239v3 prefix has five at **21, 36, 155, 765, 1280**;
the prime192v2 prefix has nine at **139, 338, 774, 1006, 1256, 1477,
1914, 2034, 2198**. These prefix counts agree with the full census on their
tested ranges; neither record supplies the private 1997–1998 stopping rule.

## What this changes about the selection window

**Derived:** Within the six recovered fixed-field prime streams, eleven
earlier candidates pass the retrospective selected-root screen and 59 earlier
candidates pass the broader cofactor-one published-family profile when both
seeded roots and no order-width cap are allowed. P-256 index 876 and P-224
index 1485 are concrete earlier cofactor-one examples on the
published-compatible coefficient mapping. The
completed binary streams and P-192 show no earlier candidate meeting their
published family cofactor profile, even though 20 earlier candidates across
those streams pass a broader X9.62 reference rule. The cofactor preference
can explain those particular skips without establishing that it was the
actual stopping rule.

**Conditional search-space ceiling:** The separately derived
[generator-process audit](../nist_seed_generation_process_20261016/report.md)
shows that a strict sequence of 20 consecutive output draws per seed has at
most `2^46` distinct candidate-start states across the full-period 48-bit
LCG; extra draws *between* intact 20-byte windows expand that ceiling to
`2^48`. These are ceilings on possible seeds under those generator recipes,
not counts of actual attempts or costs to find a desired curve. A narrower
1997–1998 timestamp window plus a small choice among viable slots yields the
often cited roughly 30-bit *scenario*, but it is not a measured upper bound on
the construction search. The 21/69 counts above condition further on the six
recovered starts and fixed field primes. They do not account for other starts,
an earlier choice of field, a different seed procedure, or an algorithm that
works on honestly generated instances. Shared ANSI streams also prevent
treating every published curve as an independent seed search.

**Limits:** The imported `ellsea(E,1)` zeros intentionally censor exact
composite group orders, so they cannot decide the full X9.62 near-prime
reference profile; strict-X9 coefficient variants also remain uncounted
outside the completed subset. The X9.62 text mismatch, unknown private `lmax` and
`rmin`, possible extra filters, unrecorded restarts or timestamp selection,
and base-point selection leave room for deliberate or incidental choices.
This audit fixes each published prime field, `a`, binary field polynomial and
basis; it does not audit how those parameters were selected.
The pasted article has no recovered generator coordinates for B-163, so its
earlier candidate stream cannot be enumerated from this recipe.
The specifically missing historical acceptance path is tracked in
[the existing problem record](../../problems/nist-seed-selection-rule-unexplained.md).
These observations do not identify motive, a hidden advantage, or a shortcut
for solving discrete logarithms. A hypothetical costly intermediate advantage
or withheld transfer would still require a construction, subgroup-preserving
map, destination solver, secrecy test, and cold-start and amortized cost model.

## Evidence status and next checks

- **[internal, exact]** All 320 binary candidate/anchor orders are in
  `raw/evaluations/B-*/`; all 139 P-192 candidate/anchor orders are in
  `raw/evaluations/P-192/`. They have zero `INDETERMINATE` rows. Independent
  subgroup-point/Hasse checks cover the 20 earlier strict-X9 survivors.
- **[internal, exact screening]** Across 31,625 prime target/index pairs,
  [2-torsion screening](raw/prime_2torsion_screen.jsonl) rejects 15,543 for
  lack of a seeded coefficient and 10,700 for even order, leaving 5,382
  target/index pairs for further cofactor-one decisions. Shared generator
  streams appear more than once in these pair counts. The separate
  [3-torsion screen](raw/prime_3torsion_screen.jsonl) tests both coefficient
  roots; it is not itself a complete point count.
- **[internal, interrupted and preserved]** The frozen
  [family campaign plan](raw/family_campaign/plan.json) contains 79 shards
  over six distinct prime streams. Its first launch was stopped under severe
  host load; all original complete shards, partial prefixes, and logs remain.
  The [retry plan](raw/family_campaign/retry_plan.json) hashes 33 source
  segments and would cover the missing positions with 217 smaller shards at one
  worker. One retry shard completed and the next stopped when the merged full
  census became available; the [stop record](raw/family_campaign/campaign_stop.json)
  and [correction](raw/family_campaign/campaign_stop_correction.json) preserve
  their exact files and hashes. The earlier complete P-192 grid and
  P-256 index 876 agree exactly with the torsion-assisted path in
  [fast_evaluator_controls.json](raw/fast_evaluator_controls.json).
  [PILOT.md](PILOT.md) records the PARI stack failure and the successful
  larger-stack P-521 candidate count as operational observations.
- **[internal, independent prefix check]** All 30 accepted root branches in
  the pre-retry source snapshot passed independent affine scalar and Hasse
  checks in [prefix_certificates.jsonl](raw/family_campaign/prefix_certificates.jsonl).
  A second four-case control record for the segmented X9 loader is
  [x9_evaluator_controls_v2.json](raw/x9_evaluator_controls_v2.json); the
  original control record remains unchanged.
- **[internal, full accepted-branch certificate]** All 82 root branches in
  the complete prime-family set have independently checked affine
  scalar/Hasse certificates in
  [full_prime_order_certificates.jsonl](raw/full_prime_order_certificates.jsonl).
- **[internal, graph scope]** Checked `knowledge/frontiers/` and related
  technique files for a canonical NIST seed-selection graph; none describes
  this recovered candidate stream. The local editable source
  [draw_visuals.py](draw_visuals.py) produces the
  [quantitative graph](selection_counts.svg) and
  [pipeline diagram](audit_pipeline.svg), plus the
  [prime-prefix coverage graph](prefix_family.svg). Captions distinguish
  completed streams from exact but incomplete prefixes.

The full cofactor-one profile is classified by the cross-checked imported
census. Completing the distinct X9 near-prime question requires exact orders
for the census's early-aborted composite cases and the strict-X9 coefficient
variants, then a declared `lmax` and `rmin`. Even that would be a
public-reference count; resolving the historical choice requires the source
or predictive evidence in the named problem record.
