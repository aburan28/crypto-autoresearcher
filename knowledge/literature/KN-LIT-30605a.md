---
id: KN-LIT-30605a
type: literature
title: "Updating Key Size Estimations for Pairings"
authors:
  - "Razvan Barbulescu"
  - "Sylvain Duquesne"
year: 2019
venue: "Journal of Cryptology 32, pp. 1298-1336 (2019; published online 29 January 2018); IACR ePrint 2017/334"
identifiers:
  eprint: "2017/334"
  doi: "10.1007/s00145-018-9280-5"
  arxiv: null
  url: "https://eprint.iacr.org/2017/334"
tags: [pairing, pairing-friendly, key-size, security-estimate, nfs, snfs, extnfs, bn-curve, bls12, kss16, kss18, bls24, finite-field-dlp, special-form-prime]
confidence: reported
citation_verified: "abstract fetched from eprint.iacr.org on 2026-10-10; body figures taken from the Journal of Cryptology HTML full text at link.springer.com (doi 10.1007/s00145-018-9280-5) and its table pages /tables/8, /tables/9, /tables/10 via the fetch tool on 2026-10-10; no PDF retrieved (eprint PDF HTTP 403, HAL hal-01534101 blocked by a bot check)"
added: "2026-10-10"
superseded_by: null
---

## Contribution

Abstract, as on the ePrint landing page and the Springer article page (the
fetch tool returned it in short quoted segments, joined here in order with
nothing added): "Recent progress on NFS imposed a new estimation of the
security of pairings. In this work we study the best attacks against some of
the most popular pairings and propose new key sizes using an analysis which
is more precise than the analysis in a recent article of Menezes, Sarkar and
Singh. We also select pairing-friendly curves for standard security levels."

ePrint metadata: category Public-key cryptography; received 2017-04-18, last
of 4 revisions 2018-02-01; "Published by the IACR in JOC 2018", DOI
10.1007/s00145-018-9280-5. Springer: Journal of Cryptology vol. 32, pp.
1298-1336, year 2019, online 29 January 2018 (issue number not shown).

## Key claims (as reported)

All figures below were relayed by the fetch tool from the Springer HTML full
text and table pages; section and table numbers are as the tool reported
them. Quotes are the tool's verbatim excerpts.

- **The popular 254-bit BN curve (u = -2^62 - 2^55 - 1).** Sect. 6.2: "One
  of the most popular BN curve is the one associated with u=-2^{62}-2^{55}-1
  which was evaluated to 128 bits of security before the recent developments
  on NFS." Sect. 6.2, step 4: "Equation [2] gives a security level of 99.69
  bits." and "the BN curve used in most of the existing implementations
  ensures no more than the 100-bit security level." The string "BN-254" does
  not occur in the text read; the curve is identified by its parameter u.
  Sect. 3.1 gives the pre-2016 framing: "a 256-bit prime p leads to a
  256-bit curve and to pairings taking values in" F_{p^12}, and "Both groups
  involved are then supposed to match the 128-bit security level according
  to the NIST recommendations". Sect. 1: a precise analysis of "a popular
  pairing, Barreto-Naehrig of 128 bits of security, showed that the key
  sizes must be re-evaluated."
- **Special form of p is what the analysis exploits.** Table 5 caption:
  "Rule of thumb values for kappa. Here d is the degree of the polynomial
  P(x) such that p=P(u) for some integer u". Table 1 caption: "Value of
  kappa to match the formula cost(NFS)=2^kappa L_Q[c]".
- **128-bit level (Table 8, caption as paraphrased by the tool: sizes of
  finite fields associated to pairing-friendly curves whose DLP cost is
  2^128 operations).** Columns Family | log2(p^k) | kappa | A | log2 B:
  BN 5534 | 2 | 1145 | 74.00; BLS12 5530 | 2 | 1098 | 73.65;
  KSS16 ~4400 | 1 | 9 | 76.5; KSS18 ~4300 | 1 | 9 | 76. The first-half
  pass relayed the caption as "Size of finite fields associated to
  pairing-friendly curves which have a DLP cost of 2^128 operations."
- **192-bit level (Table 9, "Recommended parameters for pairings of 192
  bits of security").** Columns Family | log2 u | log2(p^k) | kappa | A |
  log2 B: KSS18 85 | 12,200 | 1 | 44 | 110.2; BLS24 56 | 13,300 | 1 | 9 |
  109.4.
- **256-bit level (Table 10, "Recommended parameters for pairings of 256
  bits of security").** KSS18 185 | 26,900 | 2 | 12,855 | 137.8; BLS24 86 |
  24,700 | 1 | 23 | 141.0.
- **Concrete 128-bit curves (Sect. 7-8).** "For BN and BLS12 curves, p has
  461 bits so that 15 32-bit words are necessary." BN: "parameter
  u= 2^{114}+ 2^{101}- 2^{14} - 1" (Sect. 8.1.1), Remark 1: "this
  particular choice offers 131 bits of security." BLS12: "The recommended
  parameter is" u = -2^77 + 2^50 + 2^33 (Sect. 8.1.2); "The field p^k is
  5280 bits long instead of the 5530 bits required by the general
  estimations in Table 7." KSS16: "The recommended parameter is"
  u = 2^35 - 2^32 - 2^18 + 2^8 + 1 (Sect. 8.1.3). Conclusion: "concluded
  that BLS12 and, more surprisingly, KSS16 are the most efficient choices."
- The meaning of the columns kappa, A and B (the NFS cost model's
  calibration constant, and polynomial-selection parameters) was not read
  in detail; they are reproduced only so the rows are complete.

## Relevance to this program

`ledger/hypotheses/H-ECDLP-bd1572.yaml` lists this paper (with KN-LIT-1624b6)
among its `structural_ingredients` with provenance `recalled`,
`verified_by: null`, role "the BN254 drop quoted in the source statement; a
pointer, not support, until read". What this entry settles:

- SUPPORTS the `source_statement`'s "That's what dropped BN254 from ~128 to
  ~100 bits" and the ingredient description "BN254 to about 100 bits": the
  paper states 99.69 bits / "no more than the 100-bit security level" for the
  BN curve with u = -2^62 - 2^55 - 1, "evaluated to 128 bits of security"
  before the NFS progress. One caveat: the paper names the curve by u and
  as "the BN curve used in most of the existing implementations"; the label
  "BN254" is the hypothesis's, not a string found in the text.
- SUPPORTS, at the level of the cost model, the mechanism claim that the
  post-transfer sieve exploits p = P(u) together with the extension degree
  (Table 5 is indexed by d = deg P with p = P(u)).
- Does NOT supply the L(1/3, c) constants the hypothesis's fourth assumption
  and L1 part B (`EXP-ECDLP-6dacdb` k* table) recall for Joux-Pierrot SNFS
  or exTNFS; the paper's tables give bit-level costs via a calibrated
  2^kappa L_Q[c] model, not the asymptotic constants, and the parts of the
  text defining c and kappa per variant were not read. The hypothesis's
  "optimistic, robust to replacing by the GNFS constant" flag stays
  load-bearing.
- Says nothing about any curve-side observable (L1 distributions, L2 covers,
  L3 lifts); it is evidence only that the specialness is real where the
  hypothesis says it lives, i.e. in F_{p^k}^* after transfer.
- The `recalled` row can be upgraded to `kb` with `verified_by` pointing here
  for the BN figure specifically.

## Not verified here

- No PDF was read: eprint.iacr.org/2017/334.pdf returned HTTP 403 (as did the
  versioned archive path); the HAL copy (hal-01534101/file/main.pdf) is
  behind an Anubis bot check; web.archive.org is unreachable from this
  session. The JoC HTML page on link.springer.com was readable (apparently
  open access) and is the source of every number above, relayed through a
  fetch tool that caps quotes at 125 characters, so long sentences were
  reassembled or summarised by the tool; the ePrint version (2018-02-01
  revision) may differ from the JoC text in numbering or values.
- Table 8's caption was paraphrased by the tool, and the tool's own note
  that "5530 bits required by the general estimations in Table 7" conflicts
  with its listing of 5530 under Table 8 for BLS12; table numbering between
  the ePrint and JoC versions, and which table that sentence cites, were not
  checked.
- Not read: the derivation of "Equation [2]", the cost model behind kappa, A
  and B, the Menezes-Sarkar-Singh comparison, the treatment of the special
  (SNFS/STNFS) variants per family, the BN/KSS16 rows at 192 and 256 bits
  (none were relayed), and the twist-security and curve-order statements in
  Sect. 7.
