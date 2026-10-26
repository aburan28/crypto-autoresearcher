# Finite Semaev row-space closure audit — 2026-10-26

**Status:** independent finite-model code review; a semantic bridge and a new
Lean theorem remain open. This report does not change the frozen target,
archived outputs, official research status, or any ECDLP cost claim.

## Question and sources

Does the published rank-53 degree-three span of the fixed Boolean Semaev draw
already have the multiplication closure required by the `V_{F,3}` filtration?
This matters because a verified matrix rank proves the dimension of the
*selected row span*, while the name `V_{F,3}` additionally requires the correct
row-generation and closure semantics.

The repository inputs were the [historical measurement](../../../research/FFD_SEMAEV_MEASUREMENT1.md),
the [corrected replay](../2026-10-22-semaev-first-fall-replay/report.md), the
[finite Lean certificate](../../../formal/CryptoResearch/Semaev/BooleanParityFiniteCertificate.lean),
the [finite filtration proof](../../../formal/CryptoResearch/Semaev/BooleanParityFiltrationCertificate.lean),
the [concrete witness report](../2026-10-23-semaev-concrete-witness/report.md), and
the source-bound draw record in the corrected replay. For the mathematical
boundary, [Caminata–Gorla, Definition 1.5 and equation (1)](https://arxiv.org/pdf/2112.05579)
define `V_{F,D}` by closure under multiplication within the degree budget and
identify it with a degree-compatible Macaulay row space in a polynomial ring.
[Kosters–Yeo, Corollary 4.11 and Remark 4.12](https://arxiv.org/pdf/1503.08001)
give a trace identity for ordinary binary curves and describe degree-two first
falls as *usual*, not universal under every factor-base choice. Their paper
does not identify the particular Boolean quotient row generator audited here.

## Independent calculation

Run `python3 docs/reports/2026-10-26-semaev-closure-review/audit.py` at the
repository root. The script reads the frozen draw from Git, checks its equation
SHA-256 `89ab8e668c510572bbf9307f105b2eaf46858ad900f0b6b4a2fce8803e0ba6eb`,
and independently evaluates `S₃=e₂²+e₃+1` over
`F₂[X]/(X⁴+X+1)` for all 256 Boolean assignments. A Möbius transform recovers
all four archived component equations exactly. It also finds `y=6,7` on
`y²+xy=x³+x²+1` at the fixed target `x_R=1` and uses the archived basis
`[9,3,2,12]`.

Boolean monomial products combine variable masks by OR and **coefficients by
XOR**. The script compares two direct row policies: multipliers with degree at
most `D−deg(f)`, and the repository's policy accepting every multiplier whose
parity-corrected product has degree at most `D`. Their row counts differ, but
the rank and top-degree projection rank agree on this sample:

| Degree | Strict rows | Product-degree rows | Full rank | Top-degree projection rank |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 1 | 17 | 1 | 1 |
| 2 | 12 | 28 | 11 | 10 |
| 3 | 64 | 80 | 53 | 41 |

The resulting *direct-row statistic* has no new degree-two fall
(`11−10−1=0`) and one new degree-three fall (`53−41−11=1`). This reproduces
the published finite computation with a separate field evaluator, Boolean
multiplier, and elimination routine.

There is an additional closure witness. Let `W` be the already published
degree-two polynomial with monomial masks
`[1,2,4,8,9,10,12,16,18,20,32,40,48,64,65,128,144,192]`.
The audit confirms `W` belongs to the selected degree-three row span and lies
outside the degree-two row span. Multiplication by `u₀` (mask `1`) gives a
degree-three polynomial with masks
`[1,3,5,11,13,17,19,21,33,41,49,129,145,193]`.
Adjoining that product increases the selected degree-three row rank from
**53 to 54**. The exact inputs and output are in [evidence.json](evidence.json).

## Interpretation and limits

The Lean matrix-rank theorems remain valid for their literal 80 rows. This
counterexample shows that their span is **not closed under multiplication** by
all monomials allowed by a degree-three filtration rule in the Boolean
quotient: `W` has degree two, `u₀` has degree one, and their product is absent
from the span. It does not by itself compute the full closed filtration or
prove that the polynomial-ring `V_{F,3}` of Caminata–Gorla, augmented with
Boolean field equations, has rank 54. The passage between that polynomial
ring and this quotient needs an explicit theorem or independently reviewed
definition. The published `newFalls(3)=1` is established for the selected
row statistic; its equality with a standard first-fall multiplicity remains
unproved. The exact degree-two direct-row statistic and the existence of a
degree-three witness in the literal system are unaffected by this calculation;
their full-filtration interpretation still needs the stated bridge.

This also does not refute Kosters–Yeo's trace identity or their qualified
statement that degree-two first falls usually occur. The frozen uniform
assertion had already been withdrawn in the historical note. A reviewer
should decide whether the final claim is about a specified Boolean quotient
filtration or the polynomial-ring filtration with field equations, then
formalize that definition and check its row-span closure before promoting a
first-fall theorem or updating any graph's interpretation. The archive and
corrected 68/12 draw counts are preserved; this audit adds no new draw.

No Lean build was started for this report. GitHub Actions currently refuses
runner assignment with a payment-or-spending-limit annotation, and this Spot
host lacks the required reserve for a memory-heavy proof build. The script's
small finite check is evidence of a model boundary, not a replacement for a
Lean theorem or independent human claim review.
