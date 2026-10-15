---
id: KN-LIT-1624b6
type: literature
title: "The Special Number Field Sieve in F_{p^n}: Application to Pairing-Friendly Constructions"
authors:
  - "Antoine Joux"
  - "Cécile Pierrot"
year: 2013
venue: "Pairing-Based Cryptography -- Pairing 2013, LNCS 8365, pp. 45-61 (Springer, 2014); IACR ePrint 2013/582"
identifiers:
  eprint: "2013/582"
  doi: "10.1007/978-3-319-04873-4_3"
  arxiv: null
  url: "https://eprint.iacr.org/2013/582"
tags: [snfs, nfs, extension-field, finite-field-dlp, pairing, pairing-friendly, special-form-prime, polynomial-selection, discrete-log]
confidence: reported
citation_verified: "abstract and bibliographic data fetched from eprint.iacr.org (landing page) and link.springer.com (chapter page) on 2026-10-10; PDF not retrieved (eprint.iacr.org/2013/582.pdf returned HTTP 403; HAL hal-01213666 has no file; no PDF on either author's publication page)"
added: "2026-10-10"
superseded_by: null
---

## Contribution

Abstract, as it appears on the ePrint landing page and on the Springer
chapter page (the fetch tool returned it in short quoted segments; the
segments are joined here in order and nothing is added between them):

"In this paper, we study the discrete logarithm problem in finite fields
related to pairing-based curves. We start with a precise analysis of the
state-of-the-art algorithms for computing discrete logarithms that are
suitable for finite fields related to pairing-friendly constructions. To
improve upon these algorithms, we extend the Special Number Field Sieve to
compute discrete logarithms in F_{p^n}, where p has an adequate sparse
representation. Our improved algorithm works for the whole range of
applicability of the Number Field Sieve."

ePrint metadata: category Foundations; keywords "Discrete logarithms, SNFS,
pairing-based"; received 2013-09-14; status "Preprint. MINOR revision."
Springer: Pairing 2013, LNCS 8365, pp. 45-61, DOI 10.1007/978-3-319-04873-4_3.

## Key claims (as reported)

- The paper extends the Special Number Field Sieve from prime fields to
  F_{p^n} for primes p "with an adequate sparse representation" (the
  p = P(u) form of pairing-friendly constructions), and the extension
  "works for the whole range of applicability of the Number Field Sieve"
  (abstract).
- **The complexity constant was NOT retrieved.** Neither the ePrint landing
  page nor the Springer chapter page states an L(1/3, c) expression or any
  numeric constant; the abstract contains no complexity formula at all. The
  full text, which is where the constant and its dependence on deg P and on
  n would be stated, could not be fetched (see "Not verified here"). No
  value is recorded here and none should be cited to this entry.
- Secondary attributions found while searching, recorded as what those
  sources say and not as this paper's own statement:
  - Taechan Kim's exTNFS talk abstract (math.kyushu-u.ac.jp/activities/6277,
    fetched 2026-10-10) says discrete logarithms in F_Q = F_{p^n} with
    p = L_Q(l_p), l_p > 1/3, can be solved in time L_Q(1/3, (64/9)^{1/3}),
    and that earlier NFS algorithms assured this bound only for l_p > 2/3
    (JLSV) or, quoting the fragment the fetch tool returned, "when p is of
    special form when 1/3 < l_p < 2/3 by Joux and Pierrot, Pairing 2013)".
    That is a statement about the *regime* in which Joux-Pierrot reaches the
    (64/9)^{1/3} bound for special p; it is not a quotation of the
    Joux-Pierrot theorem and gives no constant as a function of deg P.
  - Barbulescu-Gaudry-Kleinjung, "The Tower Number Field Sieve", ePrint
    2015/505 landing-page abstract (fetched 2026-10-10): "When p has a
    special form (SNFS), as in many pairings constructions, NFS has a faster
    variant due to Joux and Pierrot" (also relayed in KN-LIT-7084).
  - Guillevic-Morain-Thome, arXiv:1605.07746v2 (PDF fetched and text-
    extracted 2026-10-10), listing polynomial-selection methods: "the
    Joux-Pierrot (JP) method for pairing-friendly curves [33] which produces
    polynomials equivalent to the Conjugation method for MNT curves".
- Application to pairing-friendly curves, as reported: the abstract scopes
  the whole paper to "finite fields related to pairing-based curves" and to
  "pairing-friendly constructions"; which families (BN, MNT, Freeman, KSS,
  ...) are treated and what each gains is in the unread body.

## Relevance to this program

`ledger/hypotheses/H-ECDLP-bd1572.yaml` lists this paper among its
`structural_ingredients` with provenance `recalled` and `verified_by: null`
("a pointer, not support, until read"). What this entry does and does not
settle for that hypothesis:

- Supported in kind (abstract level): the mechanism paragraph's statement
  that after a pairing transfer into F_{p^k}^* the polynomial form p = P(u)
  is exploited by "Joux-Pierrot SNFS", i.e. that an SNFS variant for
  F_{p^n} with p of sparse form exists and covers the NFS range. The
  abstract says exactly this and nothing finer.
- NOT supported by this entry: the hypothesis's fourth assumption and L1
  part B (`EXP-ECDLP-6dacdb`) use "recalled complexity constants for ...
  Joux-Pierrot SNFS" to locate the transfer threshold k*. No constant was
  retrieved, so that number remains recalled, and the hypothesis's own
  flag (optimistic; every conclusion must survive replacing it by the GNFS
  constant) stays load-bearing. The only external anchor found is the
  secondary (64/9)^{1/3}-for-special-p regime statement above.
- NOT a source for the "BN254 ... ~128 to ~100 bits" figure in the
  `source_statement`: this paper reports no bit-security number in the
  text read; that figure belongs to KN-LIT-30605a (Barbulescu-Duquesne).
- Upgrade path: the `recalled` row can move to `kb` with `verified_by`
  pointing here only for the existence/scope claim; the constant needs the
  PDF.

## Not verified here

- The full text was not read. eprint.iacr.org/2013/582.pdf (and the
  versioned archive path) returned HTTP 403 from this session; HAL record
  hal-01213666 carries no file; Pierrot's and Joux's publication pages link
  only to the ePrint entry; Semantic Scholar lists no open-access PDF; the
  Springer chapter PDF is paywalled; web.archive.org is unreachable here.
- Consequently unverified: the L(1/3, c) constant of the variant and its
  dependence on d = deg P and on n; the exact conditions on the sparse
  representation of p; which pairing-friendly families are analysed and the
  per-family consequences; the "precise analysis of the state-of-the-art
  algorithms" the abstract promises.
- The abstract text is assembled from quoted segments returned by the fetch
  tool (which caps each quote), not copied from a PDF; the segments were
  consistent across the ePrint and Springer pages.
