# TASK-20260731-027 — ECTD literature sources note

**Role:** idea-generator (executed in Coordinator session after Task API limit)  
**Requested policy:** `research-deep`  
**Resolved model:** Cursor Grok 4.5  
**fallback_used:** true (policy alias not served; session inherit)  
**independent_session:** false  
**Date:** 2026-07-31

## Deliverables

| ID | Title | citation_verified | Local PDF |
|---|---|---|---|
| KN-LIT-7261 | Teske, An Elliptic Curve Trapdoor System | **true** | sources/teske-2003-058.pdf (Wayback) |
| KN-LIT-7630 | Galbraith, Constructing Isogenies… | **true** | sources/galbraith-iso.pdf |
| KN-LIT-7631 | Jao–Miller–Venkatesan expanders (redirect → KN-LIT-237) | read (matches KN-LIT-237) | sources/jmv-0811.0647.pdf |
| KN-LIT-7632 | De Feo, Mathematics of Isogeny Based Cryptography | **true** | sources/defeo-1711.04062.pdf |
| KN-LIT-7633 | Dent–Galbraith, Hidden Pairings and Trapdoor DDH | **false** | — PDF blocked |
| KN-LIT-7634 | Kutas–Petit–Silva, Trapdoor DDH from pairings/isogenies | **true** | sources/kutas-2019-1290.pdf (SAC mirror) |
| KN-LIT-7635 | Fried–Gaudry–Heninger–Thomé, Kilobit Hidden SNFS | **true** | sources/fght-2016-961.pdf (Wayback) |
| KN-LIT-7636 | Jacobson–Kushwaha, Removable Weak Keys | **true** | sources/jk-2020-1436.pdf (arXiv) |

Already present (not re-filed): KN-LIT-007 (GHS), KN-LIT-3748 (Extending GHS), KN-LIT-5102 (Seurin trapdoor DDH).

## Fetch log

| URL | Result |
|---|---|
| https://eprint.iacr.org/2003/058 | 200 HTML abstract OK |
| https://eprint.iacr.org/2003/058.pdf | **403** |
| https://web.archive.org/web/2020/https://eprint.iacr.org/2003/058.pdf | 200 PDF OK sha256 `8d889ae0…2646` |
| https://www.math.auckland.ac.nz/~sgal018/iso.pdf | 200 PDF OK sha256 `77362b01…bcb8` |
| https://arxiv.org/pdf/0811.0647.pdf | 200 PDF OK sha256 `118c6096…ed9e` |
| https://arxiv.org/pdf/1711.04062.pdf | 200 PDF OK sha256 `ca0e70ab…d553` (44 pp) |
| https://eprint.iacr.org/2019/1290.pdf | **403** |
| https://sacworkshop.org/SAC20/files/preproceedings/17-TrapdoorDDH.pdf | 200 PDF OK sha256 `a7f94571…f9ec` |
| https://eprint.iacr.org/2016/961.pdf | **403** |
| https://web.archive.org/web/2020/https://eprint.iacr.org/2016/961.pdf | 200 PDF OK sha256 `5ba7f4b4…36ea` |
| https://eprint.iacr.org/2020/1436.pdf | **403** |
| https://arxiv.org/pdf/2011.07483.pdf | 200 PDF OK sha256 `65a8ecff…fee8` |
| Dent–Galbraith author PDF guesses + Springer content/pdf | **404 / HTML paywall** |

## Relevance summary for ideation

- **Teske + GHS + Extending GHS:** binary-field secret-isogeny-to-GHS-weak architecture.
- **Galbraith 1999:** ordinary $\mathbb{F}_p$ isogeny construction; conductor gap = incomplete equivalence boundary.
- **JMV (KN-LIT-237):** GRH expander → weakness must be sparse / cross-level.
- **De Feo:** survey of isogeny graphs / path-to-weak threat.
- **Dent–Galbraith / Kutas–Petit–Silva / Seurin:** hide extra operation (pairing); trapdoor DDH intermediate.
- **Hidden SNFS:** parameter-level trapdoor gold standard (not EC).
- **Jacobson–Kushwaha:** key-level removable weak keys baseline.

## Literature gate status

**Satisfied for proceeding to ideation**, with one honest gap: Dent–Galbraith PDF unobtainable (`citation_verified: false`). Abstract + consistent secondary citations are recorded; do not design experiments that require Dent–Galbraith theorem numbers until a PDF is filed.

## Non-actions

No IDEA / hypothesis / experiment / evidence / decision records created. `knowledge/INDEX.md` not hand-edited (archive task regenerates).
