# Frozen low-class-number screen for the 21 named NIST/ANSI seed classes

Frozen 2026-10-23 UTC before downloading or testing the class-number list.
This is a retrospective mathematical screen under the user's stipulated
historical-evaluation premise. It is not a reconstruction of the 1997 program
or an attack experiment.

## Question and population

Does any of the eleven passed-over seed classes, or any of the ten published
controls, have an imaginary quadratic CM field with class number at most
2,000? A low-class-number threshold can select the eleven only if all eleven
meet it and the controls do not. Count each P-224 seed once despite its two
isomorphic coefficient signs.

Use `research/nist_seed_skipped_curves_20261016/assessed.json` and
`research/nist_seed_skipped_curves_20261016/traits.json`, recording SHA-256
digests. Recompute `Delta = (p + 1 - n)^2 - 4p` from exact archived `p,n` and
stop if any row is nonordinary or duplicates an exact identity unexpectedly.

## External list and exact test

Use Kimura, *Imaginary quadratic fields of class number at most 2000*,
arXiv:2610.21511v2 (2026-10-22), code tag `v1.2`, commit `e451afc`, list
`lists/imq_h2000.txt.xz`. The paper reports 16,453,493 entries and SHA-256
`07100ea3589ab2b490122fa69b438cd5393bdcd2e547dfc29bb3b5c86f9f24c0`
for the **uncompressed** file. Verify the checksum, row count, strictly
increasing positive discriminants, `h<=2000`, and reported maximum
`D=1062350083` before analysis. Retain the URL, tag, digest, command,
software versions, elapsed time, and any failure. Keep the large third-party
list outside Git and retain only its digest and count in this repository.

For each listed positive fundamental discriminant `D` and each curve's
negative Frobenius discriminant `Delta`, test exact integer divisibility
`D | abs(Delta)` and then whether `abs(Delta)/D` is a perfect square. Record
every hit with its `D`, paper-reported class number, and square conductor.
For ordinary curves, a hit is equivalent to that CM field having the listed
fundamental discriminant. Run all 21 times 16,453,493 comparisons; record
both divisor and square-hit counts by curve. Use GMP exact arithmetic and
validate one synthetic hit at `Delta=-3*17^2` and one at `-4*19^2` using
the same scan code; verify a synthetic nonhit `Delta=-5`. Independently
cross-check the source `Delta` values and every found hit in Sage.

## Outcome and inference policy

If all eleven omissions have zero hits, a rule that rejects exactly those
eleven because their CM **field** class number is at most 2,000 is excluded,
**conditional on the paper's list being complete**. If all 21 have zero
hits, the screen cannot classify the labels. The screen does not determine
the endomorphism ring of each representative, its order class number, or an
ECDLP cost. The paper's theorem and external table are not independently
reproved here; report its formal/computational verification scope.

A hit would be a candidate property only and would require its exact curve
identity, a same-field published control, and a mechanism before any
weakness claim. A timeout, checksum failure, or missing list is censored,
not a negative mathematical result. Stop after one full bounded pass or
240 seconds of the comparison loop, whichever comes first; retain raw output
and the failure status. Generate machine-readable results, editable chart and
diagram sources, SVGs, Markdown report, Typst source, and an inspected PDF.
