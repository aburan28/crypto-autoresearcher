#set page(paper: "a4", margin: 17mm)
#set text(size: 10pt)
= Prime-field factor-base continuation
Software implementation and validation · 28 October 2026

This delivery implements four follow-ups from the repository survey. It is not
a scientific experiment, an independent review, or a speedup claim.

#image("diagram.svg", width: 100%)

== Implemented
- Exact affine relation diagnostics: original-row certificates, affine-equation
  deduplication, complete kernels and deficient-rank target identification.
- Partial-relation cancellation: eliminate outside points before counting new
  information on the existing factor base. Every equation retains its weights.
- Additive Prym x=0 source/interpolation completion, with full-stream replay in
  the separate arithmetic lane; the old frozen collector is unchanged.
- Complete Dickson extractor driver: all three multiplicity strata, finite
  resultant and signed point-sum oracle, resource guards and arity-four controls.

== Validation scope
The tests use small software fixtures: the exterior extractor is compared with
complete finite sets at depths 2–4 over p=127, while Prym zero completion is
checked over p=101. The affine diagnostics are checked against every solution
of small systems. Deliberate missing solutions, false signs, inconsistent rows,
false digests/ranks and unadmitted collection are rejected. See
`validation.json` for exact commands, initial failures and final outcomes.

No P-256 fixed-panel execution or p=4099 collector trial was launched. These
remain separate frozen-protocol, native-supervision and checkpoint operations.
The entry points bind committed source/input bytes and call the existing real
checkpoint gate; they provide no bypass or execution release.

== Sources and limits
Petit–Kosters–Messeng, PKC 2016, sections 2.4 and 3.1–3.5, retrieved and read:
#link("https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf")[primary paper].
The composed-map construction is prior work, and the relation solver and linear
algebra must both be charged. Small input degree is not a cost bound.

Reused repository source: the October 26 F1 core/exterior implementation and
the October 19/25 Prym producer, Census and independent verifier at main base
`cdd2150922211f180ab3d8c3f3b248356c78f025`. The accompanying README records
individual paths and the issue-only October 27 evidence gap.

The exterior dimension remains binomial in fibre size and exponential in depth.
Individual factor-base logs need not be identifiable for one combination to be
recoverable, but a cheap natural target decomposition is still required.
No canonical scientific metric, hypothesis status or historical run is changed.
