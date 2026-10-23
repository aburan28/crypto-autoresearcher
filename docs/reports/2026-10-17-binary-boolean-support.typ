#set page(paper: "us-letter", margin: 0.62in)
#set text(font: "New Computer Modern", size: 9.3pt)
#set heading(numbering: "1.")

= Boolean input support of two binary eight-summand chains

_2026-10-17 · Exact ANF input construction on the certified ordinary-binary GF(2^61) fixture; no solver run._

The selected torsion-coordinate base has 267 projected log columns and ten binary degrees of freedom per external coordinate. The raw-x affine base has 265 columns and nine such degrees. Both seven-equation chains use six 61-bit intermediates and the same planted raw target. Thus the torsion chain has 446 Boolean variables and the raw-x chain has 438. These systems use different coordinate maps, so their input counts are stage observations, not end-to-end cost comparisons.

== Counting rule and result

Polynomials are expanded in the fixed $"GF"(2^61)$ polynomial basis, with Boolean idempotence $v_i^2=v_i$ and characteristic-two cancellation. One nonzero field coefficient is one field monomial; its Hamming weight is its number of coefficient-bit term occurrences in the 61 descended Boolean equations. Each chain has seven equations over the field.

#figure(image("2026-10-17-binary-boolean-support.svg", width: 94%), caption: [Exact support of one middle equation. Selected-base rows have nearly equal projected-column counts; gray width controls equalize binary variable count only. Sage independently replayed the distinct equation shapes.])

For the selected bases, a middle torsion-coordinate equation has 36,133 distinct field monomials and 647,014 coefficient-bit terms. The classical raw-x equation has 38,431 field monomials and 121,546 coefficient-bit terms. Across all seven equations the counts are 3,326,200 and 637,159. Equal-width controls give 574,020 versus 121,546 terms at $k=9$ and 647,014 versus 131,238 at $k=10$ for a middle equation. All four arms have maximum input Boolean degree three. Independent Sage arithmetic checked exact first, middle and final support digests, and all seven equations on eight seeded assignments per arm.

== Scope

The compact two-term invariant expression has fewer field monomials but more expanded Boolean term occurrences on this exact presentation. This does not determine degree of regularity, solver fill, runtime or useful relation yield. Liftability, signs, poles, the other target channels, row deduplication, linear algebra and matched rho remain outside this input count. A circuit solver may avoid expansion and needs its own measured comparison. The full-width arity-grid obstruction remains open.

Exact records, source hashes, width-control limits and next protocol are in the companion Markdown report and `research/icperf_binary_boolean_support_20261017/`. Canonical frontier graphs were checked and remain unchanged.
