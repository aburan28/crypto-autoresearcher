---
id: KN-LIT-0e854b
type: literature
title: "Analysis of the GHS Weil descent attack on the ECDLP over characteristic two finite fields of composite degree (Maurer, Menezes, Teske) -- Section 6 read: the ANSI X9.62 c2pnb*w1 curves, including the (n, m) = (8, 5) question for c2pnb176w1"
authors:
  - "Markus Maurer"
  - "Alfred Menezes"
  - "Edlyn Teske"
year: 2002
venue: "LMS Journal of Computation and Mathematics 5 (2002) 127-174; CACR technical report CORR 2001-59 (dated 2001-10-12, read); IACR ePrint 2001/084"
identifiers:
  eprint: "iacr:2001/084"
  doi: null
  arxiv: null
  url: "https://cacr.uwaterloo.ca/techreports/2001/corr2001-59.ps"
tags: [ghs, weil-descent, binary-field, composite-degree, magic-number, ansi-x9.62, c2pnb176w1, c2pnb208w1, c2pnb272w1, c2pnb304w1, c2pnb368w1, subfield-curve, enge-gaudry, isogeny-walk, extended-ghs, ecdlp-challenge]
confidence: reported
citation_verified: read
added: "2026-10-09"
superseded_by: null
---

## What this entry is

A partial read on 2026-10-09 of the CACR technical-report version (42 pages):
the abstract, the table notation of Section 5 (Table 1), and all of Section 6
"Elliptic curves from ANSI X9.62" (Remarks 21 to 26, Tables 2 to 4). Sections
2 to 5, 7, 8 and the appendices were not read beyond their headings. The
journal version was not read; page and remark numbers are the report's.
Read because two notes in aburan28/crypto attribute a "c2pnb176w1 break at
m' = 5" to Menezes-Teske and neither Menezes-Teske paper in the corpus
(KN-LIT-d7995a, KN-LIT-f64d86) mentions that curve; this is the paper that
does. Vendored under `inputs/MTW-WEAK-FIELDS-20261009/`. The ledger
hypotheses H-BINSTD-490c76 and H-BINSTD-6fe132 cite the LMS version.

## Contribution (abstract)

For each composite N in [100, 600] the paper identifies the descent
parameters (n, l) and curve parameters (magic number m, genus g) for which
the GHS attack is most efficient, estimates the Enge-Gaudry cost against
rho, examines the five ANSI X9.62 example curves over F_{2^176}, F_{2^208},
F_{2^272}, F_{2^304}, F_{2^368}, and poses ECDLP challenges that resist
everything but GHS. Table notation (Section 5, Table 1): N, n, l, m, g;
I = log2 of the number of isomorphism classes with that (n, m); t =
smoothness bound; F = log2 factor-base size; T = log2 Enge-Gaudry time;
rho = log2 rho time; D = rho - T when positive. EG1 caps the factor base at
10^7; EG2 does not.

## Section 6: the ANSI X9.62 curves (read in full)

- The five curves have N = 16 p, p in {11, 13, 17, 19, 23}, and in every
  case a, b lie in F_{2^16}, so #E(F_{2^N}) = r d with d in
  [2^16 + 1 - 2^9, 2^16 + 1 + 2^9] (Table 2 lists a, b, r).
- **Remark 21 (failure for subfield curves).** The GHS descent of E/K down
  to F_q depends only on F_q(a, b), not on K, so when F_q(a, b) is a proper
  subfield of F_{q^n} the order-r subgroup lands in the kernel of the
  descent map. **Remark 23** confirms this computationally for E176
  (descent to F_{2^2}, (n, m, g) = (88, 8, 128)) and E272: the prime-order
  subgroup is in the kernel. **Remark 22**: when F_q(a, b) = F_{q^n}
  (equivalently lcm(n, l) = N, i.e. gcd(n, p) = 1 here) the usual
  non-subfield arguments apply.
- **Table 3** (direct GHS on the given curves): for E176, (n, l, m, g) =
  (8, 22, 8, 128) gives EG2 T = 2^222 against rho 2^87; (4, 44, 4, 8) gives
  T = 2^58 against 2^78 but is a gcd(n, p) > 1 descent and so fails by
  Remark 21; all other decompositions are worse. No ANSI curve is
  directly attackable.
- **Remark 26 and Table 4 (extended GHS, i.e. an isogenous curve).** For
  every decomposition N = n l they list the best magic number m an
  isogenous non-subfield curve could have, the number of such classes, and
  the Enge-Gaudry cost. For **E176** the only improving instance is
  (n, l, m, g) = (8, 22, 5, 16): I = 2^110 isomorphism classes, EG1 t = 1,
  F = 2^21, T = 2^65 versus rho 2^87 (D1 = 22); EG2 t = 2, F = 2^42,
  T = 2^61 (D2 = 26). Verbatim: "it is well possible that such a curve
  exists. However, finding such a curve is very likely to be much harder
  than solving the ECDLP using Pollard rho." For E208 the best is
  (8, 26, 5, 16): T = 2^69 versus 2^103 (D2 = 34), same caveat; E272:
  (8, 34, 5, 16) T = 2^77 versus 2^135, and (272, 1, 9, 255) T = 2^51
  versus 2^135 (D2 = 84, a descent all the way to F_2 with I = 2^10
  classes); E304: (8, 38, 5, 16) T = 2^81 versus 2^151; E368: (8, 46, 5,
  16) T = 2^89 versus 2^183. In every case the number of target classes
  is tiny relative to the isogeny class (2^110 of ~2^176 for E176, i.e.
  density 2^-66), and the paper's verdict is that reaching one is harder
  than rho.
- **Remark 24**: for l in {1, 2, 4, 8, 16}, b in F_{2^16} \ F_{2^8} forces
  8/l < m <= 16/l. **Remark 25**: E176, E272, E304 have Tr(a) = 1, so the
  GHS reduction works through the weaker condition of Lemma 6 when
  m(b) != n.

## Key claims: verified versus reported

| Claim | Status here |
| --- | --- |
| Remarks 21-23 (subfield curves: order-r subgroup in the kernel) | Read; the E176 and E272 kernel computations are the authors'. |
| Table 4 numbers for E176 | Transcribed; cost model (Enge-Gaudry with the 2001 parameters) not re-run. |
| "finding such a curve is very likely much harder than Pollard rho" | The authors' judgment, 2001; no isogeny-walk cost is computed in this paper. KN-LIT-f64d86 (2004) prices a walk at N 2^{v+15} with 2^-v the target density, which at density 2^-66 is ~2^88.5 for N = 176, consistent with the verdict. |

## Relevance to this program (correction)

- aburan28/crypto `research/ghs-c2pnb/ghs_poc.py` (docstring of
  `hess_magic_vs_cost`, Section 4 banner, summary table) states that
  "Menezes-Teske 2006 answered it positively for c2pnb176w1 at m' = 5",
  with "resulting cost ~2^57" and the verdict "BROKEN", and
  `research/notes/ecc2k130/RESEARCH_ECC2K130_HYPERELLIPTIC.md` Section 3
  repeats "exactly how c2pnb176w1 fell, at m' = 5, genus 16 over F_2^16".
  Neither Menezes-Teske paper in the corpus mentions these curves (full
  texts read, KN-LIT-d7995a and KN-LIT-f64d86). The source is this paper's
  Section 6, and it says the opposite: an isogenous curve with
  (n, m) = (8, 5) would give **genus 16 over F_{2^22}** (not F_{2^16}),
  Enge-Gaudry **2^61 to 2^65** (not 2^57) against rho 2^87, and finding
  that curve is judged **harder than rho**. The 2^57 figure does not appear
  in Table 4 for any ANSI curve. c2pnb176w1 is therefore not a positive
  control for an isogeny-walk-to-weak-curve pipeline on the published
  evidence; the ECC2K-130 note's argument does not depend on it, but its
  sentence should cite this entry and drop "fell".
- Remark 21 is the binary analogue of the subfield-curve exclusion in every
  weak-field statement: a curve defined over a proper subfield is not made
  weaker by GHS at all, because the descent map kills the large subgroup.
  This matters for any program experiment that descends a lifted subfield
  curve (KN-TECH-36e667, ECC2K-130 over F_{2^393}).
- Table 4's "n = N, l = 1" rows (descent to F_2, genus 2^{m-1} with
  m = ord_p(2)-type magic numbers) are the same objects as the
  description-length argument in the ECC2K-130 note: e.g. E272's
  (272, 1, 9, 255) instance.

## Limits of applicability

Only Section 6 was read; the per-N best-parameter tables (Section 5 and
Appendix A), the challenge instances (Section 7) and the selection
algorithms (Appendix B) are not relayed here and should be read before
being cited. Costs are 2001 Enge-Gaudry estimates in the paper's own units.

## Provenance

Retrieved 2026-10-09 from `https://cacr.uwaterloo.ca/techreports/2001/corr2001-59.ps`
(606,633 bytes, 42 pages after Ghostscript conversion) after the ePrint
PDF for 2001/084 was not attempted (same Cloudflare wall as 2003/128 and
2004/235). Same glyph loss in the text extraction as the other PostScript
sources. Retrieval record: `inputs/MTW-WEAK-FIELDS-20261009/provenance.json`.

## Local copies

- `inputs/MTW-WEAK-FIELDS-20261009/sources/maurer-menezes-teske-corr2001-59.ps` and `.txt`
