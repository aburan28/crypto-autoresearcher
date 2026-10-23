#set page(paper: "a4", margin: 13mm)
#set text(size: 9.3pt)

= Could the eleven omitted curves share one CM field or a named isogeny relation?
<could-the-eleven-omitted-curves-share-one-cm-field-or-a-named-isogeny-relation>
#strong[Date:] 2026-10-23 UTC. #strong[Status:] Exact structural result,
independently checked; historical cause and cryptographic weakness
remain unknown.

#strong[Question:] Under the stipulated premise that the original
program evaluated all eleven otherwise qualifying but unpublished seed
classes and rejected them for an unknown weakness, could that weakness
be explained by their sharing one imaginary quadratic
complex-multiplication (CM) field, or by a direct isogeny or twist
relationship among the named curves?

== Result in plain language
<result-in-plain-language>
Each ordinary elliptic curve has an imaginary quadratic field attached
to its Frobenius endomorphism. The eleven omitted curves have
#strong[eleven different fields]. In fact, all #strong[21] named omitted
and published seed classes have different fields, and none has a field
with fundamental discriminant of absolute value at most
#strong[1,000,000]. This also proves that every non-scalar endomorphism
of any of these curves has degree #strong[greater than 250,000]. None of
the named same-field curve pairs has the same group order, the opposite
Frobenius trace, or the same `j`-invariant. Thus a #strong[single shared
CM field, a low-degree CM endomorphism, a direct rational isogeny
between two named curves, or a named quadratic-twist pairing] cannot be
the missing common weakness. The findings apply equally to the published
curves, so they do #strong[not] explain which seeds were kept.
#link("analysis.json")[Exact matrix] (`internal`);
#link("sage_verification.json")[independent Sage check] (`internal`).

#box(image("inference.svg", alt: "Exact pairwise structural screen"))

This is a restriction on the #emph[form] of a possible explanation. An
algorithm or implementation failure could affect curves with different
CM fields, and a curve may have an isogeny to an #strong[unlisted]
representative. We found no attack, no such endpoint, and no evidence
that the original program made these comparisons.

== Exact calculation
<exact-calculation>
The population is the #strong[eleven seed-level omitted classes] in
#link("../../nist_seed_skipped_curves_20261016/assessed.json")[assessed.json]
and #strong[ten published controls] in
#link("../../nist_seed_skipped_curves_20261016/traits.json")[traits.json],
with no extra count for the three P-224 coefficient-sign models. The
#link("analysis.json")[machine-readable analysis] records every exact
EC1 curve UID, field prime `p`, prime subgroup order `n`, one-based seed
ordinal, trace and Frobenius discriminant. It binds the source files by
SHA-256:
`370e79ce0bff8f26bb437fe37d1756f3f8261a5c00e9062ba41cf70f272e8841` and
`a1102bd487379d223581863fab731d6eb6957bf0e264b450f1c7b298279b0b67`.
Those identities and orders are the comparison objects; familiar curve
names are only display labels. The source audit checked group order and
primality (`internal`).

For each curve we recompute `t = p + 1 − n` and `Δ = t² − 4p < 0` from
source `p,n`. Every `t` is nonzero; for these prime fields of
characteristic greater than three, that makes the curves ordinary. For
an ordinary curve, `Δ = f_π² D_K`, where `D_K` is the fundamental
discriminant of its imaginary quadratic CM field. Consequently, two such
fields are equal #strong[if and only if] `ΔᵢΔⱼ` is a perfect integer
square. This is an exact test requiring no integer factorization or
conjectural conductor value.
#link("https://msp.org/obs/2013/1-1/obs-v1-n1-p25-s.pdf")[Sutherland, #emph[Isogeny volcanoes], §2.11]
(`retrieved`).

The #link("analyze.py")[Python program] evaluates all `C(21,2)=210`
pairs. It separately enumerates every #strong[negative fundamental
discriminant] `D` with `|D| ≤ 1,000,000`, then tests whether `Δ/D` is a
perfect integer square for each curve. This detects every CM field
within that cutoff, even if the Frobenius-order conductor has large
factors. There are exactly #strong[303,968] discriminants and
#strong[6,383,328] curve/discriminant comparisons, with zero matches.
The cutoff is an exploratory test range, not a documented 1997 threshold
(`derived`).

#figure(
  align(center)[#table(
    columns: 2,
    align: (auto,right,),
    table.header([Exact comparison], [Result],),
    table.hline(),
    [Omitted--omitted pairs], [55],
    [All omitted/published pairs], [210],
    [Pairs sharing a CM field], [#strong[0 / 210]],
    [Curves with CM-field discriminant magnitude at most
    1,000,000], [#strong[0 / 21]],
    [Lower bound on every non-scalar endomorphism
    degree], [#strong[greater than 250,000]],
    [Fundamental discriminants in that range], [303,968],
    [Maximum pairwise discriminant gcd among omissions], [55],
    [Pairs over the same prime field `p`], [45],
    [Same-field pairs with equal group order], [#strong[0 / 45]],
    [Same-field pairs with opposite trace], [#strong[0 / 45]],
    [Same-field pairs with equal `j`], [#strong[0 / 45]],
    [Raw P-224 same-invariant positive controls], [3 / 3],
  )]
  , kind: table
  )

For any non-scalar endomorphism `α`, its characteristic polynomial gives
`disc(Z[α]) = Tr(α)² − 4 deg(α) = c² D_K`, for an integer `c ≥ 1`. Hence
`4 deg(α) = Tr(α)² + c²|D_K| ≥ |D_K| > 1,000,000`. The degree bound
applies to each ordinary curve, its quadratic twist, and every
`F_p`-isogenous representative because they have the same CM field. It
rules out a #strong[small-degree integral CM endomorphism]\; it is
#strong[not] a lower bound on the time needed to evaluate a high-degree
endomorphism, an isogeny to another curve, or an ECDLP algorithm.
#link("https://math.mit.edu/classes/18.783/2017/LectureNotes13.pdf")[Sutherland\'s endomorphism-algebra notes]
give the degree/trace characteristic equation;
#link("https://gaati.org/bisson/res/endomorphism.pdf")[Bisson and Sutherland]
give the ordinary order/discriminant relation (`retrieved`). The
inequality is `derived` from those facts.

#link("verify.sage")[Sage] reloads the original sources separately,
recomputes every discriminant and pairwise square test, and
independently enumerates the small fundamental discriminants with
Sage\'s `fundamental_discriminant` function. It checks every row and
pair against the matrix, verifies a Bézout witness, and checks three raw
P-224 model pairs as positive controls. The P-224 controls have
different `b` values but equal `p,n,Δ,j`, and the square-product
predicate returns true for each. Eight synthetic
fundamental-discriminant positives and a nonfundamental negative check
the range enumeration. The #link("sage_verification.json")[Sage receipt]
reports `PASS` on SageMath 10.10.rc0 (`independently verified`).

The omitted-pair discriminant-gcd counts are `40` at gcd `1`, `6` at
`3`, `5` at `5`, `3` at `13`, and `1` at `55`. Even the nontrivial gcds
do not make the full product a square. The
#link("pair_gcd.svg")[vector chart] shows these exact counts; its
editable generator is in #link("analyze.py"). There is no sampling
uncertainty. The analysis JSON includes one explicit `u|Δᵢ| + v|Δⱼ| = 1`
witness for an omitted same-field pair. This is an auxiliary integer
check; the product-square test is the actual CM-field certificate
(`derived`).

#box(image("pair_gcd.svg", width: 70%, alt: "Pairwise omitted-curve discriminant gcds"))

For pairs over the #strong[same] `F_p`, equal group order is equivalent
to being `F_p`-isogenous by Tate\'s theorem. The 45 named same-field
pairs all have different orders, so no two named curves are linked by an
`F_p`-rational isogeny. Opposite traces are necessary for a
quadratic-twist pair, and equal `j` is necessary for geometric
isomorphism; neither occurs for the named pairs.
#link("https://pazuki.perso.math.cnrs.fr/index_fichiers/Tate66.pdf")[Tate, #emph[Endomorphisms of Abelian Varieties over Finite Fields]]
(`retrieved`). An unlisted `F_p`-isogenous endpoint would have the
#strong[same trace and CM field] as its source, and a quadratic twist
has the opposite trace but the #strong[same `Δ`]. The small-CM bound
therefore applies to those endpoints and twists too. These tests do
#strong[not] enumerate isogeny classes, compute kernels or maps, or
exclude representative-specific transfers to unlisted curves.

== Interpretation for the hypothetical 1997 selector
<interpretation-for-the-hypothetical-1997-selector>
The premise that a program reached all eleven omissions and screened
them for a weakness remains #strong[stipulated].
#link("https://words.filippo.io/seeds-solved/")[Valsorda] and
#link("https://www.anthropic.com/research/ecdsa-curve-origins")[Anthropic]
report skipped viable seeds but do not supply the historical acceptance
code or logs (`retrieved`). The exact pair result rules out a fixed
shared CM field or a direct relationship among these named curves as the
hidden common feature. Because the same CM-field uniqueness occurs among
the published controls, it supplies no keep/skip predicate.

The open mathematical space includes #strong[different weak
representatives reached from each curve], CM fields beyond the explicit
cutoff, a common algorithm whose precondition varies with each curve\'s
parameters, or a defect tied to another property such as an
implementation\'s point-counting or validation behavior. The preceding
#link("../report.md")[small-conductor screen] excludes small squared
discriminant factors through 10,000 as a universal omission feature; the
#link("../isogeny_screen/report.md")[degree screen] excludes a single
rational-isogeny availability bit through degree 10,000 as a perfect
selector. None of these screens constructs endpoint maps or measures
ECDLP costs. To promote any hidden-weakness proposal, specify a
reproducible property and unknown-scalar advantage, prove subgroup
transport where used, account for construction and evaluation, and
compare it against published same-field controls. A perfect
retrospective label split alone would not establish either an attack or
historical use (`derived`, bounded).

The next discriminating historical evidence is the original source, run
log, or review sheet identifying which candidates were evaluated and why
they failed. For a mathematical proposal involving unlisted endpoints,
the first concrete task is to give #strong[one] endpoint UID, exact
field and order, isogeny degree/kernel/map, a checked subgroup transport
certificate, and complete costs for an omitted curve, then test the same
frozen rule against a matched published control. The candidate 256-bit
omitted block 876 and published P-256 block 1842 are the shortest named
same-field first comparison. Until such an object exists, the possible
common weakness remains undefined.

The earlier
#link("../../nist_seed_selection_deep_20261016/seed_slots.svg")[seed-stream graph]
and canonical graphs in `knowledge/frontiers/ecdlp/` were checked. This
study adds no verified map, endpoint, attack cost, or frontier movement,
so their supported content is unchanged. The editable
#link("inference.dot")[diagram source], rendered
#link("inference.svg")[diagram], editable
#link("analyze.py")[chart generator], #link("pair_gcd.svg")[chart],
#link("report.typ")[Typst source], and inspected
#link("report.pdf")[PDF] are the visual record for this bounded search.
