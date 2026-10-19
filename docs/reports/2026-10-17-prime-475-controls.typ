#set page(paper: "a4", margin: 17mm)
#set text(size: 9pt)
#set heading(numbering: none)

= Equal-realized-size controls for a 475-point prime coset base

*Exact target-blind preparation and independent Sage replay, 2026-10-17 UTC.*
Two deterministic controls each contain 475 curve points on the certified
63-bit prime-order curve. The control record keeps every random draw and
small-x candidate, including misses, and the full membership coefficients.
No solver degree, relation yield or ECDLP speed was measured.

#image("2026-10-17-prime-475-controls.svg", width: 100%)

The d=896 coset predicate has two terms but 896 field roots, of which 421 do
not lift to curve points. The random control's exact degree-475 product has
476 nonzero terms; the small-x product has 475 because x=0 makes its constant
coefficient zero. The random control examined 941 x-values and small-x
examined 923. These inputs are matched in realized point count and curve,
not in algebraic representation or measured runtime.

== Independent check and failure custody

SageMath 10.10.rc0 replayed both draw streams, every accepted curve point,
the point digests and every membership coefficient. The first builder
attempt failed an overstrong 476-term assertion; the first Sage replay
failed only when writing a Sage integer to JSON. The partial output is
retained, and the corrected replay is a new file. Neither failure supplies
negative evidence about the factor-base mechanism.

== Required next comparison

Freeze control systems on a common target schedule and independently check
point extraction. A bounded solver protocol must then measure actual
degree, time and RSS, certified natural relations, useful rank, linear
algebra, unseen same-point target cost and matched rho, charging all setup
and the coset's nonliftable roots. The companion Markdown report links the
full records and failed-attempt artifact.
