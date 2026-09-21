---
id: KN-LIT-f6de4b
type: literature
title: "Bombieri–Weil bound (additive / Artin–Schreier case) — attempted verification of hypothesis (H1')"
authors:
  - "Enrico Bombieri"
  - "André Weil"
year: 1966
venue: "American Journal of Mathematics 88 (1966) 71–105; Proc. Nat. Acad. Sci. USA 34 (1948) 204–207"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: "https://encyclopediaofmath.org/wiki/Bombieri-Weil_bound"
tags: [character-sums, weil-bound, bombieri, artin-schreier, additive-characters, algebraic-curves, ecdlp]
confidence: partial
citation_verified: secondary_only
added: "2026-08-03"
superseded_by: null
---

## Why this entry exists, and what it concludes

`analysis/o2-sum-compatible-filters/O2_additive_completion.md` §5.1 records
hypothesis **(H1′)**:

> Weil/Bombieri bound for **additive** character sums on a curve of genus `g`
> over `F_p`, valid unless the function is Artin–Schreier degenerate
> (`F = g^p − g + c`).

That document asserts (H1′) is *"better attested"* than the multiplicative (H1)
of [[KN-LIT-7639]], citing the Encyclopedia of Mathematics *Bombieri–Weil bound*
entry as stating "precisely this case" with constant `(2g − 1 + deg f)`.

**That assertion is too strong and this entry corrects it.** On direct retrieval
the Encyclopedia entry states the **genus-0 / projective-line** case, and does
not state the curve-level version or the non-degeneracy condition.

## What the source actually says

- **The bound given is for a polynomial on the affine line**:
  `|S(f)| ≤ (n − 1)√q` for `f` of degree `n`, with the characteristic not
  dividing `n`, via the Artin–Schreier covering `Y^p − Y = f(x)`.
- The genus that appears, `g = (n−1)/2` for odd `n`, is the genus **of the
  Artin–Schreier covering curve**, not of a base curve on which points are being
  summed. Conflating the two is exactly the error to avoid here.
- **The degeneracy condition is not stated.** The entry gives only the implicit
  condition that the characteristic does not divide `n`; it does **not** say
  when `f` degenerates, and in particular does not state the
  `f = g^p − g + c` criterion the completion argument relies on.
- Original references credited: Bombieri, *On exponential sums in finite
  fields*, Amer. J. Math. **88** (1966) 71–105; Weil, *On some exponential
  sums*, Proc. Nat. Acad. Sci. USA **34** (1948) 204–207. **Neither primary
  source was obtained.**

A secondary summary encountered during search did quote a curve-level form
(`|S(f)| ≤ (2g − 1 + deg f)√q`, with pole count entering via
`D < 2g − 2 + |P| + deg f`) and attributed it to Bombieri's extension from the
projective line to general curves. **That quotation was not confirmed against
any primary or authoritative source and is recorded here as unverified.**

## Status of (H1′)

| component | status |
|---|---|
| additive Weil bound on the **projective line**, `(n−1)√q` | **verified** from this source |
| Bombieri extended Weil's method from the line to **general curves** | **verified as an attribution**, not as a statement with constants |
| explicit **curve-level** additive bound with genus/pole constant | **NOT verified** — secondary snippet only |
| **Artin–Schreier non-degeneracy** condition `F = g^p − g + c` | **NOT verified** from any source |

## Consequence for the (O2) line

`O2_additive_completion.md` closes F1 families A, B, I, J by fibring over
`R = P+Q` and applying an additive Weil bound to `F_R(P) = αx(P) + βx(R−P)` on
`E`, genus 1. That is a **curve-level** application, and it uses the
Artin–Schreier degeneracy criterion explicitly in its §2.3 lemma. Both of those
are in the "NOT verified" rows above.

**So (H1′) is materially LESS well attested than (H1)** — the reverse of what
that document claims. [[KN-LIT-7639]] at least supplies a curve-level statement
with an explicit non-degeneracy hypothesis and a stated validity regime for the
multiplicative case; nothing equivalent has been obtained for the additive case.

The §2.3 degeneracy lemma is a *pole-order* argument that is self-contained given
the criterion, so what is missing is the criterion's provenance, not the lemma's
internal logic. The families A/B/I/J closure should be read as **conditional on
(H1′) as stated, with (H1′) currently untraced to a primary source.**

## What is owed

1. Bombieri 1966 (Amer. J. Math. 88, 71–105) directly, for the curve-level
   additive statement and its constant.
2. A primary statement of the Artin–Schreier non-degeneracy criterion.
3. The same for general multiplicative order `k > 2` on curves, still owed under
   [[KN-LIT-7639]] and needed by F1 family D (`k = 3,4,8`).
4. A correction to `O2_additive_completion.md` §5.1 replacing "better attested"
   with the position recorded here. **Not applied yet**: that file was under
   independent Validator and Red Team review when this entry was written, and
   editing an artifact mid-review would invalidate the reads.

## Not verified here

Both primary papers; Perel'muter; the curve-level constant in either the
additive or multiplicative case; and whether the relevant sheaf non-degeneracy
holds for the specific `F_R` used in the completion.
