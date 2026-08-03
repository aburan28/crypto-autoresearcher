---
id: KN-LIT-1c9474
type: literature
title: HQC-RMRS, an instantiation of the HQC encryption framework with a more efficient auxiliary error-correcting code
authors: [Aragon Nicolas, Gaborit Philippe, Zemor Gilles]
year: 2020
venue: 'arXiv preprint arXiv:2005.10741 (submitted 21 May 2020), 14 pp.'
identifiers:
  eprint: null
  doi: null
  arxiv: 'arXiv:2005.10741'
  url: https://arxiv.org/abs/2005.10741
tags: [hqc, hqc-rmrs, code-based, kem, decoding-failure-rate, dfr, reed-muller, reed-solomon, concatenated-code, shortened-reed-solomon, binary-symmetric-channel, quasi-cyclic, primary-source, pqc]
confidence: reported
citation_verified: read
added: 2026-08-02
superseded_by: null
---

## Contribution
Replaces HQC's original tensor-product BCH ⊗ repetition auxiliary code with a
concatenation of Reed-Muller and Reed-Solomon codes (the instantiation the authors
call HQC-RMRS), and supplies the error-distribution and decoding-failure-rate
analysis for that construction. **This is the paper the 2025 HQC specification
(`KN-LIT-b9e1a8`) cites as reference [4] and says it follows in §6.1.1**, i.e. the
derivation source of the specification's analytic DFR model. The identification is
read out of the specification's own reference list, not recalled.

## Key claims (as reported)
- **Abstract.** The concatenated RM/RS codes "yield better decoding results than the
  BCH and repetition codes: overall we gain roughly 17% in the size of the key and the
  ciphertext, while keeping a simple modelization of the decoding error rate." The
  paper "also presents a simplified and more precise analysis of the distribution of
  the error vector output by the HQC protocol."
- **§3, the error-vector model.** Carries the same "simplifying assumption that the
  coordinates e′_k of e′ are independent variables" as the specification, with the
  same "realistically only be ≤ p∗" justification and the same claim that the
  resulting computations "can only be upper bounds on their real values". The
  specification's added sentence "In other words we modelize the error vector as a
  binary symmetric channel with parameters p∗" is **absent** from this paper's
  corresponding paragraph.
- **Propositions 4.2.1 / 4.2.2** are the specification's Propositions 6.1.3 / 6.1.4
  (simple union bound; improved bound crediting 1/2 on two-way ties).
- **Remark 4.1 — a hedge the specification does not carry.** "Propositions 4.2.1 and
  4.2.2 give upper bounds on the Decryption Failure Rate for the internal code. The
  smaller the DFR, the closer the bounds become to the real value." Its Table 4
  tabulates **both** bounds against the observed DFR at the 2020 parameters
  (log₂ DFR): security 128, p⋆=0.3196, [256, 8, 128], −7.84 / −8.03 / observed −8.72;
  security 192, p⋆=0.3535, [512, 8, 256], −11.81 / −12.12 / −12.22; security 256,
  p⋆=0.3728, [768, 8, 384], −13.90 / −14.20 / −14.25. The specification's Table 11
  tabulates one bound, at different codes and different p⋆ values.
- **Remark 4.2 — the only explicit scope statement for the independence assumption in
  either primary source.** The bounds "have been derived with a binary symmetric
  channel model for the distribution of the HQC error vector restricted to the support
  of a (duplicated) Reed-Muller code. Figure 4 compares the actual weight distribution
  of the error vector to the binomial distribution when restricted to this relatively
  small number of bits. We observe that they are virtually identical, meaning that **a
  small proportion of HQC bits do behave as i.i.d Bernoulli variables**."
- **§4.3.** "For Reed-Muller codes, rather than considering the upper bound
  approximation we effectively decoded the code, which means than in practice the
  upper bound that we use for our theoretical DFR, is greater than what is obtained in
  the simulations."
- **Theorem 4.3** is the specification's Theorem 6.1 — the same binomial-tail bound
  Σ_{l=δ_e+1}^{n_e} C(n_e, l) p_i^l (1 − p_i)^{n_e − l}, with the same closing clause
  "Where d_e = 2δ_e + 1 and p_i is defined as in Proposition 4.2.1". **This paper
  gives no proof of Theorem 4.3**: the text goes from the theorem statement directly
  to §4.3 "Simulation results". Consequently the i.i.d.-across-inner-blocks assumption
  that turns the expression into a binomial tail is unstated and unproved here as
  well as in the specification (transcription assumption A17).
- **§4.1 and Figure 6, the 2020 parameters.** §4.1 says "For the external code, we
  chose a Reed-Solomon code of dimension 32 over F256", and Figure 6's proposed
  parameter sets use external codes **[80, 32, 49]**, **[76, 32, 45]** and
  **[78, 32, 47]** — dimension 32 at all three security levels, with internal codes
  [256, 8, 128], [512, 8, 256], [768, 8, 384] and DFR targets < 2⁻¹²⁸ / 2⁻¹⁹² /
  2⁻²⁵⁶, claiming a gain over the BCH ⊗ repetition instantiation of 16.8% / 16.7% /
  15.4%.
- **§5 Conclusion.** "In Section 3 we presented a better analysis of the error weight
  distribution for HQC, which leads to a better DFR estimation. This can be used to
  reduce the size of the parameters, no matter what family of codes is used for
  decoding."

## Relevance to this program
Supplies the derivation-level hedges (Remarks 4.1 and 4.2) that the 2025
specification compresses or omits, and is therefore required reading for any
independent re-derivation of the model under `RQ-HQC-001`. Filing it alongside
`KN-LIT-b9e1a8` is what discharges `RQ-HQC-001.constraints[0]` for the DFR lane.

Two observations bear directly on `KN-LIT-b9e1a8`'s published-text inconsistencies,
and are recorded as observations only:

- This paper's §4.1 sentence "a Reed-Solomon code of dimension 32 over F256" is
  **consistent with its own Figure 6**, where all three external codes have k = 32.
  The specification carries a near-identical sentence in §3.4.1 while its §3.4.2 uses
  k ∈ {16, 24, 32}.
- Figure 6's first external code is **[80, 32, 49]**, whose minimum distance
  49 = 80 − 32 + 1 is correct for n = 80. The specification's RS-S3 has n = 90 and
  prints the same number 49 where its own definitions give 59. Whether that is
  causally an unrevised carry-over is **not established here**; only the coincidence
  of the numeral and the fact that 49 is the correct value for this paper's n = 80
  code are recorded.

**Its parameters are the 2020 ones and differ from the specification's**; a
comparison across the two must not mix them.

## Not verified here
- No claim in this entry has been re-derived, recomputed, or measured by this program.
  Table 4's and Figure 6's figures are the authors'.
- Displayed formulas in this paper were quoted from the PDF text layer and were
  **not** verified against rendered page images (unlike the specification's, which
  were). Where this entry states a formula it does so only to record that it is the
  same expression as the specification's counterpart.
- This entry does **not** assert that the specification's §6.1 and this paper's
  §3–§4 are mathematically identical, only that the specification cites this paper as
  what it follows and that the passages named above correspond.
- Nothing here asserts anything about HQC's security in either direction.

## Provenance
- Obtained by `TASK-20260802-6344ed` (BATCH-001) from `https://arxiv.org/pdf/2005.10741`
  on 2026-08-02, after the identifier was read out of the specification's reference
  list ([4]) rather than recalled. Metadata confirmed on the arXiv abs page
  (`citation_title`, `citation_author`, `citation_date` 2020/05/21,
  `citation_arxiv_id` 2005.10741).
- **sha256 `cbb7dbd670f27cdcf602438018df52745c0af495050aedb3b83a0b00986f5446`**,
  525 223 B, PDF 1.4, 14 pp., producer pdfTeX-1.40.17, creationDate D:20200522002924Z.
- Re-acquired byte-identically and independently by `TASK-20260802-b8d69f`
  (validator) and again by `TASK-20260802-63b16a` (this filing). Three independent
  fetches, same sha256.
- **The PDF is not committed to this repository** (third-party copyright). The URL and
  hash above let any reviewer re-acquire and verify byte-identity.
- `citation_verified: read` rests on full-text reading of all 14 pages by
  `TASK-20260802-6344ed`, with pages 1, 4, 8–14 independently re-read from the
  re-acquired PDF by this filing task.
- No journal or conference version was located by this program; the arXiv preprint is
  the only version read. No DOI is asserted.
