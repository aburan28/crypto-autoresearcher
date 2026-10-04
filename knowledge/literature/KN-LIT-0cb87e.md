---
id: KN-LIT-0cb87e
type: literature
title: "Elliptic curve cryptography: the serpentine course of a paradigm shift (Koblitz, Koblitz, Menezes) -- conductor-gap speculation, Sec. 11.2-11.3"
authors:
  - "Ann Hibner Koblitz"
  - "Neal Koblitz"
  - "Alfred Menezes"
year: 2011
venue: "Journal of Number Theory 131(5) (2011) 781-814; preprint IACR ePrint 2008/390"
identifiers:
  eprint: "iacr:2008/390"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2008/390"
tags: [ecdlp, isogeny, isogeny-class, endomorphism-ring, conductor, conductor-gap, volcano, crater, random-self-reduction, jmv, weil-descent, special-vs-random-curves, kkm, prime-field, binary-field]
confidence: reported
citation_verified: read
added: "2026-10-03"
superseded_by: null
supersedes: KN-LIT-235
---

## Contribution

Mostly a history / sociology-of-science essay on how ECC went from mistrusted
to standard (1985 -> NSA Suite B). The technically load-bearing part for this
program is **Section 11 ("A Tale of Two Standards: Brainpool vs. Voltage")**,
specifically:

- **Sec. 11.2 "Isogenies and endomorphism rings"** (ePrint pp. 26-27). Partitions
  an F_q-isogeny class into endomorphism classes (orders of conductor c | c0,
  where t^2 - 4q = c0^2 d). Restates Jao-Miller-Venkatesan [their ref 44 =
  KN-LIT-237]: under GRH, isogenies of prime degree l < L = (log q)^{2+eps},
  (l, c0) = 1, give an expander on each endomorphism class. Defines the
  **L-conductor-gap class** of E: all endomorphism classes whose conductor
  differs from End(E)'s only by primes < L. ECDLP is random self-reducible
  inside such a class (time ~ T1 + T2/eps if a fraction eps of curves are
  "weak"), and **not** across a large conductor gap.
- **Sec. 11.3 "More examples of potential weakness of random curves"**
  (ePrint pp. 27-29). The **KKM speculation**: assume "weakness" (some
  faster-than-sqrt attack applying to a fraction eps of curves) is distributed
  independently of isogeny/endomorphism class. Then a curve in a *large*
  L-conductor-gap class can be walked by O(1/eps) isogenies onto a weak curve,
  while a curve in a *tiny* class (maximal order / crater, isolated by a large
  prime r | c0) almost surely cannot. Conclusion they draw: the random self-
  reducibility of the generic class "under certain circumstances might make a
  generic curve less secure than a special curve".

## Key claims (verified against ePrint 2008/390 text, read 2026-10-03)

- Example 3: Muller's Koblitz curve y^2 + xy = x^3 + x^2 + gamma over
  F_{2^{3*59}} (CM field Q(sqrt(-23)), c0 = 11681 * 98766024850235972863,
  End = maximal order) vs. Bob's random curve over the same field. Using the
  Menezes-Teske weak fraction eps ~ 2^-58 of curves (Weil descent to genus 3
  over F_{2^59}, DLP ~ 2^79), Bob's random curve is computed to give ~79 bits
  (walk of ~2^58 isogeny steps at ~2^17 each) vs. Alice's special curve's 84;
  Alice's 2^66-conductor-gap class has < 2^16 curves, so the chance of
  reaching a weak curve is ~2^-42. **Arithmetic is the authors'; not re-derived.**
- Example 4: NIST K-571 (Delta = -7 c0^2, c0 = 22-bit prime * 263-bit prime,
  conductor 1) has an L = 2^262 conductor-gap class of ~2^22 curves, vs. the
  random NIST B-571 whose discriminant is squarefree (one big class). Argued
  "likely safer" if eps << 2^-22, *under the independence assumption*.
- Example 5 (prime field): suggests deliberately choosing E/F_p in a very small
  L-conductor-gap class (y^2 = x^3 - alpha x construction) as insurance against
  a future attack on a fraction of prime-field curves.
- Footnote 5: faster special-case isogeny methods [their ref 15] work only
  within one L-conductor-gap class and do not change the argument.

## What it does NOT claim

- No algorithm makes floor/generic curves weaker. It is conditional on a
  hypothetical eps-fraction attack AND on weakness being independent of
  endomorphism class. Zero direct evidence (Galbraith 2024 Sec. 10, KN-LIT-ca35e0).
- The paper never uses the words "volcano", "crater" or "floor"; that framing
  is Galbraith's (KN-LIT-ca35e0). Crater = maximal order / conductor 1;
  "generic" = conductor divisible by the large prime r.

## Relevance to this program

The defensive mirror image of the trapdoor line (GOAL-ECTD-001,
KN-OPEN-cc1988, KN-OPEN-cbbd97): the same conductor barrier that could *hide*
a secret weak curve from the public is what KKM say *protects* an isolated
crater curve from an attacker's isogeny walk. Directional refinement stated as
KN-OPEN-f2f6dc. Also anchors RQ-VOLC-f6253b (does volcano depth change any
measurable ECDLP cost).

## Local copies

- Fetched to session scratch from https://eprint.iacr.org/2008/390.pdf
  (42 pages, sha256 `2e9f49752c311befa5c78981c357bc3a9e611d8dfa5e45d7d2aceaa795ff30f3`);
  not vendored. Bulk-seed copy: `downloads/2008-390.pdf` (per KN-LIT-235).
