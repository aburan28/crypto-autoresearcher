#set page(paper: "a4", margin: (x: 17mm, y: 16mm))
#set text(font: "New Computer Modern", size: 10pt)
#set par(justify: true)

= What might have selected the published curves?

*2026-10-22 · Exploratory comparison of recovered NIST/ANSI prime-field seed streams*

The clock-seeded generator makes candidate seed blocks enumerable. It does not reveal how many timestamps the 1997–98 designers tried, which blocks their program evaluated, or a mathematical weakness in a published curve. The eleven reported omissions pass the checked prime-order screens. FIPS 186-2 Appendix 6.4 says to retry when a curve lacks suitable order, but contains no complete acceptance trace. The primary discovery accounts likewise leave the extra selection rule unresolved.

#figure(image("selection_fork.svg", width: 100%), caption: [Three distinct historical explanations. The published constants do not choose a branch.])

== A new exploratory coefficient pattern

The archived 21-row curve file supplies 8 published and 11 omitted curves in four fields where both labels occur; the two singleton published fields are excluded. For P-224, which has isomorphic coefficient signs, the analysis uses the smaller bit weight of the two signs. The published coefficient is lighter in *22 of 25* within-field published-versus-omitted comparisons. The 192-bit published weights are 89, 92, 93 versus omitted weights 94, 96. P-256 differs by one bit. Yet an omitted 239-bit coefficient is lighter than published prime239v2, and two P-224 omissions are lighter than published P-224. This is no exact selection rule.

#figure(image("b_weight.svg", width: 100%), caption: [Exact coefficient bit weights divided by field bit length; 19 source-bound rows, with no sampling uncertainty. Blue: published; orange: qualifying omission.])

#pagebreak()

The exact conditional rank diagnostic is 37 of 4,480 allocations with an equal or lower published rank sum. Because this feature was noticed after seeing the labels and the labels were never randomized, the fraction is not a historical probability or evidence of intent. Seed, hash-output and group-order bit weights do not show the same directional comparison. Standard scalar-multiplication formulas need not use b in their main group operations; a lower bit weight has no established ECDLP implication here.

== Remaining mechanisms and discriminating evidence

- *Known screens:* the eleven omissions pass the checked prime-order, cofactor-one, order-size and bounded MOV/CM screens. Simple universal trace, twist and first-valid rules fail against published controls. A new predicate must classify every row and predict an independent historical decision.
- *Program path:* other generator calls could mean a reconstructed 20-byte window was never evaluated. Every published seed's 20-draw alignment constrains that explanation. Original source or call logs would settle it.
- *1997 arithmetic:* a point-count, prime-certificate or bookkeeping outcome might have suppressed a valid curve. Modern arithmetic cannot replay an unavailable implementation. Obtain the old executable and dependencies, then preserve every pass, failure and time limit.
- *Curation or hidden mathematical class:* a low-dimensional seed generator permits a search for a defined property. It supplies no property. An actual claim needs a witness or predictive rule, exact published subgroup, construction and evaluation costs, solver consequence, controls, and cold versus amortized accounting. Earlier field-prime and later base-point choices remain separate.

The strict 20-draw model has 2^46 distinct candidate-start states. A local 65,536-state P-256 shard applied only the coefficient square-root screen, so its count is not a census of prime-order or weak curves. The 21 reported slots are not a count of all historical attempts. The historical-selection problem remains open.

== Sources and reproducibility

Primary sources: FIPS 186-2 Appendix 6 (csrc.nist.gov/files/pubs/fips/186-2/final/docs/fips186-2.pdf); NIST's 2014 FIPS 186 history slides (csrc.nist.gov); Anthropic's 2026 recovered-generator account (anthropic.com/research/ecdsa-curve-origins); Valsorda's 2026 candidate list (words.filippo.io/seeds-solved/); Explicit-Formulas Database (hyperelliptic.org/EFD/g1p/auto-shortw-jacobian.html). Internal sources and exact EC1 curve identities: research/nist_seed_skipped_curves_20261016/assessed.json and traits.json; prior process and selection reports; numeric shard manifest. Derived record and editable visuals: analyze.py, analysis.json, selection_fork.svg, b_weight.svg beside this PDF. No research-state transition is made.
