---
id: KN-LIT-7593
type: literature
title: "Cryptanalysis of 7-Round AES via the Algebraic Structure of its S-box"
authors:
  - "Milad Nasr"
  - "Nicholas Carlini"
year: 2026
venue: 'Anthropic technical report (released 2026-07-28)'
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: https://anthropic.com/document/aes_mobius_bridge.pdf
tags: [aes, s-box, mobius-bridge, meet-in-the-middle, demirci-selcuk, differential-enumeration, invariant, fingerprint, round-reduced, llm-autonomous-discovery, verification-methodology, scaled-down-cipher, cost-accounting]
confidence: reported
citation_verified: web
added: "2026-07-28"
superseded_by: null
---

## Contribution
Improves the best-known meet-in-the-middle attack on **7-round AES-128** by exploiting
the `affine ∘ inverse` factorization of the AES S-box to build a key-byte-invariant
fingerprint — the **Möbius bridge** — eliminating one of the nine guessed key bytes in
[DFJ13]. Discovered fully autonomously by Claude Mythos Preview; the reasoning transcript
is [[KN-LIT-7595]] and the program-level account is [[KN-LIT-7594]].

## Key claims (as reported)
- **Baseline.** Derbez–Fouque–Jean [DFJ13] attack 7-round AES-128 at `2^105` chosen
  plaintexts, `2^99` time, `2^90` storage. This paper keeps the data complexity at
  `2^105` and reduces time to **between `2^89.3` and `2^91.4`**, "depending on the exact
  methods used for accounting."
- **The line of work.** Demirci–Selçuk [DS08]: four AES rounds restricted to a byte
  subset are determined by only 25 parameter bytes, enabling a `2^200`-entry table.
  Dunkelman–Keller–Shamir [DKS10]: a multiset fingerprint invariant to one guessed key
  byte **on the input side**, plus differential enumeration shrinking the table
  `2^200 → 2^127` — first 7-round AES-128 attack below exhaustive search, at `2^116`.
  [DFJ13]: parameter count tightened to 10 bytes.
- **Core idea.** [DKS10] made the fingerprint invariant to the key byte *above* the
  meet-in-the-middle table; this paper makes it **also invariant to the key byte below**
  it, by constructing a fingerprint invariant under affine transformations — which is
  possible precisely because the AES S-box is `L ∘ Inv` (invert, then GF(2)-affine).
  This removes one guessed key byte, a direct **factor-256** reduction in key guesses.
- **The cost that had to be paid back.** Naïve computation of the Möbius fingerprint is
  expensive enough to cancel the 256× saving. Three implementation techniques — a packed
  power table, a Gray-code walk over DDT solution choices, and an XOR-separable S-box
  cache — bring the per-entry cost from `≈ 2^19` to `≈ 2^8.6` lookups.
- **Two fingerprints.** The first realizes the invariance algebraically via ratios of
  power sums that cancel the unknown byte (§4.1); a second, **χ-canonicalization** (§4.2),
  achieves the same invariance by orbit canonicalization rather than algebraic
  elimination and is cheaper to evaluate by construction.
- **The full cipher is not broken.** AES-128 has 10 rounds; this attacks 7. The best
  single-key attacks on full AES (bicliques [BKR11]) still beat brute force by only about
  two bits. At `2^105` data the attack is far outside any practical threat model; the
  authors state it has no impact on production systems.

## Verification methodology (the reason this entry matters most here)
The attack cannot be run: it costs `≥ 2^89` time. The authors therefore assemble a
**ladder of partial validations**, and are explicit that the humans' role was primarily
verification of a machine-generated result. The ladder, in ascending order of coverage:

1. **Fingerprint collision entropy (§5.1).** The false-positive analysis assumes the
   12-byte fingerprint carries `12 log2 255 ≈ 95.9` bits. They draw `N = 3 × 10^9`
   random 255-element multisets and measure collision entropy of `k`-byte prefixes,
   `k = 1..7`. Every residual lies within `1.1σ` of the ideal line; at `k = 1` the
   measurement is sensitive to `±10^-8` bits. **A hidden algebraic relation among the
   fingerprint coordinates was the specific failure mode being hunted, and it was not
   found at that sample size.**
2. **Wrong-key randomization (§5.2)** — the complementary check that wrong guesses
   behave as assumed.
3. **End-to-end key recovery on a scaled-down cipher (§5.3).** The full pipeline —
   structure generation, ciphertext filter, DDT-constrained outer-key guesses, δ-set
   construction, table lookup, key-schedule solve — is run to completion on
   **SR(7,2,2,6)** [CMR05]: 7 rounds over a 2×2 state of 6-bit cells, 24-bit block and
   key, the smallest AES-shaped cipher on which the [DFJ13] parameter space is fully
   enumerable. All 8 random keys recovered. The measured Bloom-hit rate 0.0460 matched
   the two-parity prediction `1 - (1 - p_FP)^2 = 0.0459`, and the [DFJ13] baseline
   performed exactly `2^e = 64×` as many lookups per structure for the same outcome —
   **the predicted speedup was observed, at small scale, as a measured ratio.**
   6 of 14 structures contained no right pair and produced only false positives, "exactly
   as expected" — the negative cases were predicted in advance and checked.
4. **End-to-end on real 7-round AES-128 with two declared cheats (§5.4).** Real cipher,
   real key schedule; the harness is permitted to (a) construct only the one true offline
   table entry rather than instantiating all `2^88` tuples, and (b) use key knowledge to
   designate the right pair instead of collecting `2^105` plaintexts. Both cheats are
   named, and each is argued to be **completeness-preserving but soundness-losing**, with
   the lost soundness explicitly delegated to the §5.1 measurements.
5. **A machine-verified false-positive bound (§5.5)** and **numerical estimation of the
   computational complexity (§5.6)** — the source of the `2^89.3`–`2^91.4` range.

## Relevance to this program
**No ECDLP content.** AES is a symmetric block cipher; nothing here transfers to the
elliptic-curve discrete logarithm, and this entry must never be cited as though it did.
It earns a place in the corpus for two things.

**The verification ladder is directly adoptable.** This program routinely faces the same
structural problem — a claimed asymptotic improvement that cannot be run at the scale
where it would matter — and `AGENTS.md` rule 4 plus `docs/claims-and-verification.md`
already forbid presenting toy-scale evidence as crypto-scale. §§5.1–5.6 are a worked
example of how to discharge that obligation honestly: isolate each assumption the
complexity analysis rests on and measure it separately at a scale where measurement is
possible; run the *whole* pipeline on a scaled-down instance where the predicted speedup
appears as a **measured ratio against the baseline**, not as an extrapolation; then run
the real object with cheats that are individually named and individually classified as
completeness- or soundness-affecting. The §5.4 discipline — "both cheats reduce the
computational complexity in a way that minimizes the risk that this cheating hides a
potential flaw" — is the standard the Validator role should be held to.

**The invariance-elimination move.** Abstractly: *a guessed quantity can be removed from
a search if you can compute a statistic invariant to it.* [DKS10] did this once, this
paper does it a second time on the other side, and the enabling structure was a
factorization of the nonlinear component (`L ∘ Inv`) that had been in plain sight since
1998. The generalizable caution is the second half: the naïve invariant cost more than it
saved, and the result only exists because three separate implementation optimizations paid
the cost back. **An invariance that eliminates a search dimension is not a speedup until
the cost of computing the invariant is accounted for** — which is `KN-TECH-035`
full-cost discipline restated in a new setting.

## Not verified here
Full paper text retrieved from the official Anthropic URL above on 2026-07-28 and read at
the level of the abstract, introduction, overview (§2), and the correctness-verification
section (§5); `confidence: reported`. The technical body (§§3–4) and appendices were not
read line by line, and **nothing in this entry has been independently re-derived or
re-run by this program.**

NOT verified here: the Möbius bridge construction and its claimed affine-invariance; the
`2^19 → 2^8.6` per-entry cost reduction and the three techniques achieving it; the
χ-canonicalization fingerprint; the headline `2^89.3`–`2^91.4` runtime range and the
accounting choices that produce a two-bit spread in it; the collision-entropy
measurement and its extrapolation from 7 measured bytes to the full 12-byte fingerprint;
the SR(7,2,2,6) end-to-end run and its tables; the §5.4 argument that both cheats are
completeness-preserving; and the machine-verified false-positive bound. The cited
complexities for [DS08], [DKS10], [DFJ13], and [BKR11] are relayed from this paper's own
account and were not checked against those sources. Preprint released by the discovering
party — not peer-reviewed, no DOI or venue as of this entry. The authors state the result
was validated with consultation from outside academics; that consultation is not
documented in what was read.
