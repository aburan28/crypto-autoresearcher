---
id: KN-LIT-d2f917
type: literature
title: >-
  NIST / X9.62 curve seeds explained: drand48 output after srand48(timestamp) (Anthropic Frontier Red Team; Valsorda), 2026-10-16
authors:
  - "Anthropic Frontier Red Team"
  - "Filippo Valsorda"
year: 2026
venue: >-
  Two web publications, both dated 2026-10-16: Anthropic research post
  "Claude reveals ECDSA curve origins"; F. Valsorda, blog post "NIST Elliptic
  Curves Seeds Bounty Has Been Claimed"
identifiers:
  eprint: null
  arxiv: null
  doi: null
  url: "https://www.anthropic.com/research/ecdsa-curve-origins"
  url_valsorda: "https://words.filippo.io/seeds-solved/"
tags: [nist-curves, x9.62, fips-186-2, seed-provenance, drand48, srand48, freelip, verifiably-random, rigidity, safecurves, seed-manipulation, p-224, p-256, p-384, p-521, binary-curves]
confidence: reported
confidence_note: >-
  Literature claim. The seed regeneration has an internal reproduction
  (research/nist_seed_provenance_20261016/), which this program has not yet
  validated independently, so the entry stays at `reported`. Its
  attribution argument, that a 48-bit LCG regenerates a 160-bit seed by
  chance with probability about 2^-112, is derived in that bundle.
citation_verified: web
citations:
  - ref: "https://www.anthropic.com/research/ecdsa-curve-origins"
    provenance: retrieved
    claim: >-
      Every X9.62 / FIPS 186-2 prime-curve seed is one 20-byte block of
      (int)(drand48()*256) after srand48(t), with t a 1997-98 UNIX time, and is
      tried as an X9.62 seed. The base points of P-192, prime192v2/v3 and
      prime239v1-3 come from FreeLIP zrandom.
    verified_by: >-
      Top-level Claude Code session session_01TPFiTk4kt2VfEauB3PKCbN, which
      read the page text in full on 2026-10-16 (retrieved by its research
      subagent) and reproduced its code's output. This entry was written by
      the session's Coordinator subagent from that reading; the Coordinator
      did not open the page.
  - ref: "https://words.filippo.io/seeds-solved/"
    provenance: retrieved
    claim: >-
      The bounty was claimed. The seed derivation, the binary-curve lrand48
      words, the unexplained items, and a bound of about 30 bits of freedom per
      curve.
    verified_by: >-
      Top-level Claude Code session session_01TPFiTk4kt2VfEauB3PKCbN on
      2026-10-16. The user pasted the post up to its security discussion.
      The session's research subagent retrieved the remainder (including the
      30-bit bound) and the linked Go code; the session relied on that
      extraction for those parts.
added: "2026-10-16"
superseded_by: null
---

## Contribution

The two posts report that the "unexplained" seeds of the 1997-98 ANSI X9.62
and FIPS 186-2 elliptic curves came from a standard C library pseudorandom
generator seeded with the time of day. The seeds were not chosen as
arbitrary 160-bit strings.

## Key claims (as read on 2026-10-16; see `citations` for who read them)

- **Prime-curve seeds.** Every X9.62 / FIPS 186-2 prime-curve seed (P-192,
  P-224, P-256, P-384, P-521, prime192v2, prime192v3, prime239v1, prime239v2,
  prime239v3) is one 20-byte block of `(int)(drand48() * 256)` output after
  `srand48(t)`, where `t` is a UNIX time between May 1997 and April 1998. Each
  block was tried as an X9.62 seed.
- **Binary-curve seeds.** The B-233, B-283, B-409 and B-571 seeds are five
  `lrand48()` words per candidate after `srand48(s)`. Read as `s = t / 2`,
  the four runs start on 1998-04-17 between 15:24 and 15:32 UTC; read
  directly, `s` is a February 1984 time. Anthropic presents the halved clock
  as a possibility, not a certainty. The **B-163 seed is unexplained.**
- **Base points.** The base points of P-192, prime192v2/v3 and prime239v1-3
  come from Lenstra's FreeLIP `zrandom` with seeds 20000-20517. The **base points
  of P-224, P-256, P-384 and P-521 are unexplained.**
- **Skipped candidates.** In each run, about half of the candidates passing
  every known check were skipped, for a reason the sources do not identify.
- **Freedom bound (Valsorda).** About 30 bits of freedom per curve: any
  1997-98 timestamp (about 2^25.9 choices) times any of the first 16 accepted
  candidates (2^4). This is an upper estimate under stated assumptions, not a
  count of runs actually made.

## Internal reproduction (pointer, not a promoted finding)

`research/nist_seed_provenance_20261016/` (copied from aburan28/crypto; file
hashes in its `SOURCE.md`) reports the following:
- 10 of 10 prime seeds and 4 of 4 binary seeds regenerated, with the
  X9.62 check `r * b^2 = -27 (mod p)`, by a native Rust test in aburan28/crypto.
- A full census of 21,753 blocks with 11,042 point-counted candidates
  reproduces the posts' accept list 21 of 21 (10 published, 11 skipped).
- 17 prime-order candidates were rejected by `bitlen(n) > bitlen(p)`.
- On all nine published `p = 3 (mod 4)` curves, `b` is the `(p+1)/4` root.
- A preregistered skip-filter screen and a seed-agnostic generator scan of
  the unexplained values (both run outside the repository) were negative.

None of this is yet an evidence record or a `KN-FIND`. Promotion waits for
independent validation (DEC-20261016-fb3a6f).

## Relevance to this program

- SafeCurves rigidity rows for P-224, P-256 and P-384 (GOAL-SCURVE-137bd9,
  GOAL-SCURVE-be9707, GOAL-SCURVE-cef9f7): the seed half of "unexplained seed"
  is now explained. The base points and the selection among accepted
  candidates are not, so the expected `rigid: false` is unchanged
  (CORR-20261016-0bf0b2).
- Seed manipulation (KN-TECH-031027) and the Koblitz-Menezes density argument
  (KN-LIT-b58682): for these historical curves the reachable set is bounded by
  the generator (about 2^30 per curve under Valsorda's assumptions), not by
  the 2^160 seed space.
- Open problem: problems/nist-seed-selection-rule-unexplained.md.

## Limits

This is provenance, not cryptanalysis. It changes no ECDLP cost, no twist
or invalid-curve analysis, and nothing about Shor. It does not show that any
curve is weak, and it does not show that none is. The 30-bit bound assumes
that the published provenance is the actual generation process. The
unexplained skip rule is itself freedom that the bound covers only through
the "first 16 accepted candidates" allowance.

## Addendum (2026-10-22): base-point and B-163 follow-up, and the scope of the earlier scan; a disclosure, not a correction of this summary

Added by the Coordinator under DEC-20261022-4e7b19. The text above is
unchanged, and it remains a faithful account of the two posts as read on
2026-10-16.

**What the posts tested.** This entry records from the posts only that the
P-192, prime192v2/v3 and prime239v1-3 base points come from FreeLIP
`zrandom`, and that the base points of P-224, P-256, P-384 and P-521 and the
B-163 seed are unexplained. It does not record whether either post discusses
the binary-curve base points, or which generators either post tried on the
unexplained base points or on B-163. This addendum cannot tell, and it
attributes no such test to Anthropic or to Valsorda. Everything below comes
from aburan28/crypto, not from the posts.

**Scope of the earlier scan.** The last bullet under "Internal reproduction"
reports a negative seed-agnostic generator scan of the unexplained values. On
the binary curves that scan tested the published `Gx` and `Gy`. The follow-up
reads X9.62-1998 A.3.1 as building the base point as `G = hR` from a random
`R`, with cofactor `h = 2` or `4`, so the random draw is `x(R)`. The scan
therefore did not test the draw, and its negative says nothing about it. The
K-curve base points were probably not among its 19 targets.
CORR-20261022-b3c8a5 records this. The prime-curve and B-163 parts of that
bullet are unaffected.

**Follow-up searches (unvalidated observations).** aburan28/crypto PR #2410
(branch `claude/nist-basepoint-tests`, open and unmerged; head `2275ed6e` as
read on 2026-10-22), `research/nist_basepoint_provenance_20261017/`:
- On the binary curves it tests every `R` with `hR = G` (2 halvings for the
  B-curves and K-163, 4 quarter points for K-233 to K-571), each coordinate in
  the polynomial and the normal basis: 137 targets.
- 14 searches with planted positive controls found no informative target hit:
  FreeLIP with small, timestamp and date seeds; the FreeLIP lattice for any
  seed; drand48 continuing the seed run and with un-reduced chunks; GMP 2.0.2;
  MIRACL; PARI; SHA-1 expansion of the curve seed; small multiples of
  small-`x` points; the FreeLIP and drand48 lattice and PARI patterns on the
  137 binary targets; C `rand()`/`random()` with 1997-98 time seeds, and any
  one-byte edit of a drand48-family output, for the B-163 seed.
- Blind cells, untested rather than negative: the FreeLIP lattice on P-224 and
  P-256 (controls missed); P-384 at NBITS = 62 (no specificity: it flags 126
  of 200 random values); Maple V `rand` (control missed).
- Eight of the 14 searches (T3-T5, T8, T9, T11, T12, T14) were computed in
  Python in a standalone session. aburan28/crypto forbids Python for results,
  keeps their sources as a frozen snapshot, and treats them as observations
  until a native port reproduces them. The other six are C or PARI/GP.
- Side checks: FreeLIP `zsqrtmod` for `p = 3 (mod 4)` returns `a^((p+1)/4)`
  with no seed input, so the negated `Gy` on 3 of the 6 FreeLIP points was
  chosen by the calling code. A CM-discriminant screen of the skip rule,
  whose protocol was self-dated and not committed first, found no split (8 of
  10 published and 10 of 11 skipped have conductor proxy `f = 1`). The
  separate, merged skip-filter study `research/nist_seed_skip_filter_20261017`
  (H7-H11, 21 features) found none either.

**Status of these results here.** None of this has been independently
validated. It is not an evidence record in this repository, and it changes
no `KN-FIND`: the base points and B-163 stay outside KN-FIND-cee88d. A bounded
search with found controls excludes only what it ran. It does not show that
these base points or this seed are not generator output. The follow-up names
two remaining hypotheses, a generator not covered and a choice that is not a
function of a recoverable seed, and says neither can be tested from public
data. Open problems: problems/nist-base-points-generation-unexplained.md,
problems/nist-b163-seed-generation-unexplained.md, and, for the skip rule,
problems/nist-seed-selection-rule-unexplained.md.

**Limits.** Provenance, not cryptanalysis. Any point of order `n` is an
equally good generator. Nothing here changes the ECDLP on any curve, any
attack cost, any hypothesis status or any SafeCurves cell. This entry's
confidence stays `reported`.
