---
id: KN-LIT-b9e1a8
type: literature
title: Hamming Quasi-Cyclic (HQC)
authors: [Gaborit Philippe, Aguilar-Melchor Carlos, Aragon Nicolas, Bettaieb Slim, Bidoux Loic, Blazy Olivier, Deneuville Jean-Christophe, Persichetti Edoardo, Zemor Gilles, Bos Jurjen, Dion Arnaud, Lacan Jerome, Robert Jean-Marc, Veron Pascal, Barreto Paulo L., Ghosh Santosh, Gueron Shay, Guneysu Tim, Misoczki Rafael, Richter-Brokmann Jan, Sendrier Nicolas, Tillich Jean-Pierre, Vasseur Valentin]
year: 2025
venue: 'HQC team specification document dated 22/08/2025, 51 pp. (NIST PQC selected KEM; no published standard cited by this entry)'
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: https://pqc-hqc.org/doc/hqc_specifications_2025_08_22.pdf
tags: [hqc, code-based, kem, quasi-cyclic, syndrome-decoding, qcsd, decoding-failure-rate, dfr, reed-muller, reed-solomon, concatenated-code, shortened-reed-solomon, binary-symmetric-channel, fujisaki-okamoto, ind-cca2, information-set-decoding, specification, primary-source, pqc]
confidence: reported
citation_verified: read
added: 2026-08-02
superseded_by: null
---

## Contribution
The specification of Hamming Quasi-Cyclic (HQC), a code-based KEM whose security is
stated to rest on quasi-cyclic syndrome-decoding problems (2-DQCSD-P and
3-DQCSD-PT). It specifies the scheme (sampling, polynomial multiplication, the
concatenated Reed-Muller / Reed-Solomon auxiliary code, HQC-PKE, and HQC-KEM via a
salted Fujisaki-Okamoto transform with implicit rejection), three parameter sets, and
a security analysis whose §6.1 gives the **analytic decoding-failure-rate (DFR)
model** for the concatenated decoder and whose §6.2 joins that DFR to the IND-CCA2
statement.

Formula-level detail, numbered assumptions (A1–A23), the source's own hedges
(H1–H11) and published-text anomalies (X1–X10) are transcribed in
`coordination/goals/GOAL-HQC-001/batches/BATCH-001/tasks/TASK-20260802-6344ed/dfr_model_transcription.md`.
That transcription is superseded on one point only — the reading of anomaly X6 — by
`coordination/goals/GOAL-HQC-001/batches/BATCH-002/tasks/TASK-20260802-63b16a/correction_report.md`,
whose findings are carried into the "Published-text inconsistencies" section below.

## Key claims (as reported)
Each item carries the specification's own hedging level. Nothing here has been
re-derived, recomputed, or measured by this program except where explicitly said.

- **Parameter sets (Table 5, p.29 — design targets, not measurements).**
  HQC-1/NIST-1: n₁=46, n₂=384, n=17 669, k=128, ω=66, ω_r=ω_e=75, DFR < 2⁻¹²⁸.
  HQC-3/NIST-3: 56, 640, 35 851, 192, 100, 114, DFR < 2⁻¹⁹².
  HQC-5/NIST-5: 90, 640, 57 637, 256, 131, 149, DFR < 2⁻²⁵⁶.
  n is stated to be "the smallest primitive prime greater than n₁n₂".
- **Auxiliary code (§3.4).** External: shortened Reed-Solomon over F₂₅₆; internal:
  the Reed-Muller code [128, 8, 64] duplicated 3 or 5 times to [384, 8, 192] and
  [640, 8, 320]. Maximum-likelihood decoding on the internal code, then an algebraic
  decoder on the Reed-Solomon code.
- **Shortened Reed-Solomon parameters (§3.4.2, Table 3, p.18).** RS-S1 (n=46, k=16,
  δ=15), RS-S2 (n=56, k=24, δ=16), RS-S3 (n=90, k=32, δ=29), obtained from RS-1/2/3
  by subtracting 209 / 199 / 165 from **both** n and k. §3.4.2 defines the family it
  uses by `n − k = 2δ` and `d_min = 2δ + 1`, and states that "shortening the
  Reed-Solomon code does not affect its error correcting capacity". Those definitions
  give minimum distances **31, 33 and 59**. See "Published-text inconsistencies".
- **Error-vector model (§6.1.1, explicitly an approximation).** Every coordinate of
  e′ = x·r₂ − r₁·y + e is exactly Bernoulli(p⋆) (Prop. 6.1.2); the *weight*
  distribution is then modelled as binomial under the "simplifying assumption that
  the coordinates e′_k of e′ are independent variables", i.e. "we modelize the error
  vector as a binary symmetric channel with parameters p∗". The text says this
  "working assumption is justified by remarking" an inequality and is "support[ed]
  … by extensive simulations", and that the resulting DFRs "can only be upper bounds
  on their real values" — **stated and simulation-supported, not proved**.
- **Internal-code DFR (§6.1.2, upper bounds).** Prop. 6.1.3 is a union bound over the
  255 non-zero Reed-Muller codewords; Prop. 6.1.4 improves it by crediting a 1/2
  success probability on two-way ties and capping the coefficient by C(n, ω). The
  text states that maximum-likelihood decoding of Reed-Muller codes has "no exact
  formula", and that "[f]or cryptographic parameters the approximation is less
  precise, which means that the DFR obtained will be conservative".
- **Concatenated DFR (Theorem 6.1, §6.1.3, p.38–39).** Upper bounded by the binomial
  tail Σ_{l=δ_e+1}^{n_e} C(n_e, l) p_i^l (1 − p_i)^{n_e − l}, "where d_e = 2δ_e + 1
  and p_i is defined as in proposition 6.1.3". The i.i.d.-across-inner-blocks
  assumption that makes this a binomial tail is **implicit in the formula and is not
  stated in prose** (transcription assumption A17).
- **Reported internal-code simulation (Table 11, p.38), log₂ DFR:** NIST-1
  p⋆=0.3398, [384, 8, 192], −10.79 vs observed −10.96; NIST-3 p⋆=0.3618,
  [640, 8, 320], −14.14 vs −14.39; NIST-5 p⋆=0.3725, [640, 8, 320], −11.30 vs
  −11.48. Relayed as the specification reports them.
- **DFR → IND-CCA2 (§6.2.2–§6.2.3).** HQC-PKE is δ-correct with δ the §6.1 quantity,
  and §6.2.3 (p.45) enumerates the four terms of the HQC-KEM IND-CCA2 advantage bound
  in prose: the first two are the salt/hash terms 1/(2^{|k|}·2^{|salt|}) and
  3q_RO/2^{|k|}; "[t]he third term (q_RO + q_D) · δ is related to the δ-correctness of
  the scheme"; the fourth is 2·(Adv_{2-DQCSD-P}(B₁) + Adv_{3-DQCSD-PT}(B₂)). This is
  the exact textual join between the DFR model and the IND-CCA2 statement. §6.2.3
  further states that with the deployed biased sampler `SampleFixedWeightVect`
  replacing the uniform `SampleFixedWeightVect$`, the third and fourth terms increase
  "by at most (τ^{ω_r}_max)³", with τ^{ω_r}_max = 1.00015 / 1.00047 / 1.00101 at
  NIST-1/3/5 (Table 12).
- **Known attacks (§6.3, p.45–46)** covers Information-Set Decoding (Prange, Stern,
  Dumer and the works cited as [29], [5], [30], [11]), the DOOM quasi-cyclic speedup,
  and structural attacks on the factorisation of xⁿ − 1. It does **not** discuss
  decryption-failure attacks, and Guo–Johansson's *A New Decryption Failure Attack
  Against HQC* (ASIACRYPT 2020) is absent from its reference list.

## Published-text inconsistencies bearing on the DFR chain
Recorded because a downstream re-derivation that silently picks one reading would be
unreproducible. These are observations about the published document, checked against
the primary text at the sha256 below; they are **not** claims about HQC's security in
either direction.

1. **RS-S3's printed minimum distance is inconsistent with the rest of the document.**
   §3.4.2 p.18 prints `RS-S3[90 = 255 − 165, 32 = 197 − 165, 49]`. Three
   derivations *internal to this same specification* give **59**, not 49:
   (a) §3.4.2's own definition `n − k = 2δ`, `d_min = 2δ + 1` gives
   `d = n − k + 1 = 90 − 32 + 1 = 59` (the MDS/Singleton relation, which shortening
   preserves because §3.4.2 subtracts 165 from n *and* k); (b) Table 3's δ = 29 gives
   `d = 2·29 + 1 = 59`; (c) the printed generator polynomial g₃(x) has degree 58 =
   2δ = n − k, again forcing δ = 29. The sibling rows are consistent on all three
   routes (RS-S1 → 31, RS-S2 → 33, both as printed). **The value that the
   specification's own decoder parameter δ_e = 29 implies for Theorem 6.1 is d_e = 59;
   the printed `49` is isolated to that one bracket.** Verified independently at 6×
   page rendering and in the PDF text layer by `TASK-20260802-63b16a`.
2. **§3.4.1's "dimension 32" is level-specific in §3.4.2.** §3.4.1 p.17 says "For the
   external code, we use a Reed-Solomon code of dimension 32 over F256", while §3.4.2
   p.17 says the shortened codes have "k … equal to 16, 24 or 32", Table 3 lists
   k = 16/24/32, and Table 5's k = 128/192/256 bits is 16/24/32 F₂₅₆-symbols. The
   §3.4.1 sentence therefore holds only for HQC-5.
3. Prop. 6.1.3's statement carries the exponent (1 − p)^{d_i − j} while the general
   expression inside its own proof carries (1 − p)^{n − j}; Eq. (5) p.37 prints the
   literal English word `weight` inside a binomial coefficient where Prop. 6.1.4
   prints ω − j; Table 11's column header names Prop. 6.1.4 while its caption names
   Prop. 6.1.3, and Theorem 6.1's own text names Prop. 6.1.3; the p.38 prose names
   "[512, 8, 256] and [640, 8, 320]" where Table 11 immediately below lists
   [384, 8, 192] and [640, 8, 320]. Full list as X1–X10 in the transcription cited
   above.

## Relevance to this program
`GOAL-HQC-001` / `RQ-HQC-001` lane 1: this is the primary statement of the analytic
DFR model that goal exists to measure against, and lane 2's IND-CCA2 sensitivity
question is anchored at §6.2.2–§6.2.3. Filing this entry is the act that discharges
`RQ-HQC-001.constraints[0]` for the specification. It also supplies the selected
parameter sets at which any memory-charged ISD baseline would eventually be
instantiated.

The two items a re-derivation must resolve first, per this program's own review
chain, are **A17** (the unstated i.i.d.-across-inner-blocks assumption behind Theorem
6.1's binomial tail, proved in neither this document nor `KN-LIT-1c9474`) and **X9**
(§6.2.2 states the failure event as ω(e′) > ∆ with ∆ = ⌊(d−1)/2⌋, a bounded-distance
quantity, while §6.1 computes the failure probability of the two-stage
ML-then-algebraic decoder of §3.4.1).

**Forecloses**: nothing. **Leaves open**: everything `RQ-HQC-001` asks. This entry
records what the model *says*, not whether it holds.

## Not verified here
- **No claim in this entry has been re-derived, recomputed, or measured by this
  program**, with one exception stated as such: the three arithmetic derivations of
  RS-S3's minimum distance in "Published-text inconsistencies" item 1, which are
  applications of the specification's own stated definitions to its own printed
  numbers. Table 5, Table 9, Table 11 and Table 12 figures are the specification's.
- Nothing here asserts that HQC's DFR model is correct, tight, or sufficient, or that
  any parameter set does or does not meet its DFR target. `RQ-HQC-001`'s toy
  claim-tier ceiling is untouched by this entry.
- Assumptions A1–A23 were transcribed, not tested. No decoding trial has been run by
  this program.
- The relationship between this document and any NIST draft or published standard was
  not examined; no FIPS text has been read by this program.

## Provenance
- Obtained by `TASK-20260802-6344ed` (BATCH-001) from
  `https://pqc-hqc.org/doc/hqc_specifications_2025_08_22.pdf`, the HQC team's own
  publication point, on 2026-08-02.
- **sha256 `174186cb5fdc0108aad914391360c222f52ea533bfb406146fac124b3a25406d`**,
  876 126 B, PDF 1.5, 51 pp., producer pdfTeX-1.40.26, creationDate
  D:20250822133716Z.
- Re-acquired byte-identically and independently by `TASK-20260802-b8d69f`
  (validator) and again by `TASK-20260802-63b16a` (this filing). Three independent
  fetches, same sha256.
- **The PDF is not committed to this repository** (third-party copyright). The URL
  and hash above let any reviewer re-acquire and verify byte-identity.
- `citation_verified: read` rests on full-text reading of all 51 pages by
  `TASK-20260802-6344ed`, with pages 17, 18, 29, 32, 33, 35–39, 44 and 45
  independently re-read from the re-acquired PDF by this filing task.
