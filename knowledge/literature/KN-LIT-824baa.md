---
id: KN-LIT-824baa
type: literature
title: "On the Mismatch between Neural-Discovered Differential-Linear Features and Long-Round Distinguisher Construction"
authors:
  - "Thomas Peyrin"
  - "Zilong Wang"
  - "Liu Zhang"
  - "Chenlu Zheng"
year: 2026
venue: "Preprint; venue not stated in the supplied text (document dated 2026-09-02)"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: "https://anonymous.4open.science/r/revisiting_differential_nerual_cryptanalysis-F573/README.md"
tags: [differential-neural, neural-distinguisher, differential-linear, fourier-analysis, goldreich-levin, speck, siphash, chacha, arx, mask-search, sat-linear-trail, sparsity-regularization, objective-mismatch, interpretability, symmetric, symmetric-cryptanalysis, negative-result]
confidence: reported
citation_verified: read
added: "2026-09-04"
superseded_by: null
---

> **Provenance, stated exactly.** The complete text of this paper (abstract,
> Sections 1–5, Appendices A–E, tables and reference list) was supplied verbatim
> by the user in session on 2026-09-04 and read in full when this entry was
> written. It was **not** located on IACR ePrint, DBLP, or a publisher index by
> any agent in this program, and the supplied text carries no ePrint number,
> DOI, or arXiv id — only a document date and an anonymized artifact repository,
> which is the usual signature of a paper under double-blind submission.
> `citation_verified: read` therefore records that the *content* below reflects
> the real document; it does **not** record that the *bibliographic entry* has
> been resolved against a primary index. Resolve the identifier before this
> entry is used to support `novelty_status: known` for any proposal
> (`AGENTS.md` rule 9, `templates/research-records.md` "Citation provenance").

## Contribution

Asks whether the classical differential-linear (DL) masks recoverable from a
trained *difference-only* differential-neural distinguisher are useful as
intermediate-mask candidates for **long-round** DL search. The answer is split
and is the paper's point: at short round counts the neural model is a good
candidate generator, but a fixed-round neural training objective ranks
candidates by their **local** middle correlation `|r|`, which is not the
quantity that decides a long-round distinguisher (`p·r·q²`). The paper reports
this as an open problem rather than solving it.

Three instruments: (i) `Conv1DFully`, an architecture whose first layer can be
projected onto sparse classical masks; (ii) Goldreich–Levin heavy-Fourier
extraction of the decision rule (framework inherited from [YWZW26]); (iii) a
first-layer sparsity regularizer used as a structural bias toward
low-Hamming-weight candidates.

## Key claims (as reported)

**Architecture (`Conv1DFully`).** Gohr's residual tower is removed and the first
convolution is reorganized to run along the ciphertext-difference **bit**
dimension, giving `W ∈ R^{N_f × d}` with one learned coefficient per difference
bit. Each row is projected to a Hamming-weight-`k` binary mask by
`Γ_j = TopK(|W_j|)`. Stated purpose is mask-level accessibility, **not** accuracy
or parameter efficiency (`N_f = 1024`; LayerNorm+ReLU; FC 1024/256/64; Adam
`lr = 1e-3`; `BCEWithLogitsLoss`).

**Speck32/64 control — the architectural change preserves the feature.** From
the known 9-round DL distinguisher `(0xa840,0x0010) →4→ (0x1000,0x5000) →2→
(0x1000,0x0020) →3→ (0x0205,0x0204)` (practical correlation `2^-7.3`), the
4-round differential prefix is stripped to give a 5-round task with input
difference `(0x1000,0x5000)` and DL correlation `2^-1`. Over 10 seeds:

| network | params | accuracy | Fourier similarity | dominant term | coefficient |
| --- | ---: | --- | --- | --- | --- |
| Gohr-style ResNet | 69,217 | 0.6268 ± 0.0003 | 96.54% ± 0.18% | `{25,18,16,9,2}` | 0.9308 ± 0.0034 |
| `Conv1DFully` | 1,367,041 | 0.6255 ± 0.0004 | 98.45% ± 0.69% | `{25,18,16,9,2}` | 0.9666 ± 0.0138 |

`{25,18,16,9,2}` is exactly the output mask `(0x0205,0x0204)`. Threshold
`τ = 0.1` throughout.

**SipHash-2-4 finalization, 4 rounds — the positive result.** Input difference
`Δ = (0x40000, 0x80040000, 0x0, 0x0)` taken from Niu et al. [NSLL22], whose
published output mask is `γ_out = 0x2000000020000000` = bits `{61,29}` with
measured correlation `2^-6.03`. Exhaustive evaluation of **all 679,120 masks of
Hamming weight ≤ 4** finds 18 with correlation `> 2^-6`; the neural Fourier
terms recover **15 of the 18**, including the four strongest — `{25}` at
`2^-4.86`, `{25,24}` at `2^-4.92`, `{41}` at `2^-5.06`, `{41,40}` at `2^-5.08` —
each in 10/10 runs. The three missed masks (`2^-5.75`, `2^-5.89`, `2^-5.97`) are
the three weakest above the threshold. Training used `10^7` samples (≈ `2^23.25`);
validation accuracy `0.5191 ± 0.0004`. Recurrence frequency broadly, **but not
monotonically**, decreases with correlation; the paper explicitly declines to
read this as causal.

**Speck128/128, 18 rounds — the negative result.** Baseline is Chen–Bao–Yu
[CBY23]: `(0x40002403c012, 0x10020040000400c2) →5→ {117} →8→ {77,5} →5→
(0xa49000000020343, 0x208000000020303)` with `p = 2^-30`, `r = 2^-5.81`,
`q = 2^-10`, so `p·r·q² = 2^-55.81`. The `5+8+5` split is retained deliberately
over Gong et al.'s [GWH+25] `5+9+4` re-decomposition so that the neural boundary
carries a genuine **multi-bit** mask rather than the singleton `{5}`. An 8-round
difference-only distinguisher is trained on the middle component under
`Δ = {117}` (`10^7` samples, 30 epochs, 30 seeds, accuracy `0.8217 ± 0.0012`).
`q` is then obtained by SAT (CryptoMiniSat) minimum-weight **single XOR-linear
trail** search over the last 5 rounds — a single-trail correlation, not a
linear hull:

| intermediate mask | `\|r\|` (8 rd) | `\|q\|` (5 rd) | `\|r q²\|` (13 rd) |
| --- | --- | --- | --- |
| `{75,67,64,11,3}` (30/30 runs) | `2^-0.01` | `2^-25` | `2^-50.01` |
| `{75,72,67,64,11,8,3}` (29/30) | `2^-0.97` | `2^-30` | `2^-60.97` |
| `{72,8}` (28/30) | `2^-0.97` | `2^-19` | `2^-38.97` |
| `{75,72,71,67,64,11,8,7,3}` (26/30) | `2^-0.99` | `2^-28` | `2^-56.99` |
| `{72,71,8,7}` (25/30) | `2^-0.99` | `2^-20` | `2^-40.99` |
| **`{77,5}` (classical, 0/30)** | `2^-5.81` | `2^-10` | **`2^-25.81`** |

Every recurrent neural candidate has a *stronger* middle correlation than the
classical mask and a *far weaker* composed correlation — the best of them loses
by `2^13.16`. The classically selected mask is **never** retained by the Fourier
reconstruction at `τ = 0.1` in any of the 30 runs.

**First-layer visibility and sparsity guidance.** Of the 8,128 Hamming-weight-2
masks, 77 have correlation `> 2^-8`. Top-2 projection of the unconstrained
first layer exposes `34.40 ± 1.96` of them per model (range 32–39), and `{77,5}`
appears in **1 of 30** models. Adding a global first-layer sparsity regularizer
(target `max_hw = 3`, i.e. `ρ_final = 3/128`) raises coverage to `44.37 ± 3.16`
and `{77,5}` to **9 of 30**, at the cost of markedly less stable training
(accuracy `0.81872 ± 0.02280`, range `[0.75039, 0.82896]` vs `± 0.0012`
unconstrained). At the **decision** level the intervention changes nothing that
matters: the recurrent Fourier terms remain the same locally strong relations and
`{77,5}` is retained in **0 of 30** sparsity-guided runs.

**ChaCha (Appendix D), stated by the authors as qualitative only.** The 2.5-round
middle of Beierle et al. [BLT20] with `Δ = ({2},{5,29,17,9},{30,22,10},{30,10})`
(their `i = 6` case; their reported 2.5-round DL correlation `2^-8.3` with
single-bit output mask `{0}`). 10 seeds, `10^8` samples, 40 epochs; accuracy
`0.7988 ± 0.0505` (range `[0.7030, 0.8732]`). 21 non-constant heavy-Fourier
occurrences over 8 distinct masks. The classical reference bit `0` appears only
**inside larger supports**, never as a singleton term. Several extracted masks
have near-unit measured correlation, one quoted as `2^{-3.84×10^-5}`.

**Sparsity formulation (Appendix E).** `L = L_cls + λ_sp(e)·b_sp(e)·L_sp(W)` on
the first layer only. Soft activity `A_ij` is a baseline-corrected sigmoid of
`|W_ij| − τ_w` with sharpness `k = 100`, `τ_w = 0.01`; `ρ_act = mean(A)`;
`L_sp = w_L1·mean(|W|) + α·max(ρ_act − ρ_t, 0) + β·max(ρ_t − ρ_act, 0)`. Target
ratio anneals `ρ_0 = 0.1 → ρ_final = 3/128`; `λ_sp` steps `λ_A = 0.8 → λ_B = 1.5`
over stages `(e_A, e_A2B, e_B) = (10,10,10)`; `w_L1 = 0.01`, `α = 1.5`, `β = 3.0`;
boost `b_sp = clip(ρ_act/ρ_t, 1, 5)`.

**Conclusion as the authors state it.** Difference-only differential-neural
distinguishers can *assist long-round candidate generation*; reliable recovery
and long-round-aware prioritization *remain unresolved*. The authors also state,
"to the best of our knowledge", that no existing differential-neural attack has
shown a clear round advantage over the strongest comparable classical analysis.

## What the paper explicitly does not claim

- No optimality over the full mask space. The SipHash exhaustion covers Hamming
  weight ≤ 4 only — 679,120 of `2^64` masks.
- No causal account of why weaker approximations are recovered less often; the
  training-set size and other factors were not varied.
- No claim that learned representations are architecture-independent; only that
  *this* dominant feature survived *this* reorganization in *this* setting.
- The ChaCha appendix is explicitly labelled qualitative, with seed variance
  `± 0.0505` cited as the reason.
- `q` is a **single-trail** correlation from a minimum-weight SAT search, not a
  linear-hull correlation; the paper says so.

## Relevance to this program

Directly serves `GOAL-SIMSPK-001` / `RQ-SIMSPK-f6a6c0` (Speck rotation constants
scored against a computable cryptanalytic portfolio): it supplies a working
DL pipeline for Speck32/64 and Speck128/128, exact published reference numbers
usable as implementation-fidelity gates, and a warning that a DL score is
**decomposition-dependent** — the same 18-round distinguisher is `5+8+5` here and
`5+9+4` in [GWH+25]. Adjacent to `GOAL-ASCON-001`, `GOAL-BLAKE-001` (ChaCha
lineage) and `GOAL-POLYMAC-001` through the shared ARX DL machinery.

Its methodological content is wider than its cipher content, and is abstracted
in [[KN-TECH-d64293]] with the unresolved question stated in [[KN-OPEN-7f0d85]].
Classical background: [[KN-TECH-065]] (differential-linear), [[KN-TECH-077]]
(rotational). Neighbouring literature already in this corpus: [[KN-LIT-4449]]
(Gohr, CRYPTO 2019), [[KN-LIT-3694]] (Bao et al., enhancing differential-neural),
[[KN-LIT-1717]] (local constraints behind Fourier analysis of Speck32/64 neural
distinguishers), [[KN-LIT-6310]] (Niu et al., the SipHash reference setting),
[[KN-LIT-4400]] (Beierle et al., the ChaCha reference setting), [[KN-LIT-3459]]
(DLCT).

## Program deductions (not claims attributed to the paper)

These are this program's readings of the paper's own tables. Each is an
**unverified hypothesis**, stated so it can be falsified cheaply, not a result.

1. **The paper's data falsifies Hamming weight as an adequate surrogate for
   linear extendability — using only Table 7.** `{72,8}` and `{77,5}` are both
   Hamming weight 2, yet their 5-round minimum-weight trail correlations are
   `2^-19` and `2^-10`: a factor `2^9` that no weight prior can see. Sparsity
   guidance can therefore only ever *enlarge the candidate pool*; it cannot rank
   within it. This is consistent with the paper's own finding that sparsity moved
   first-layer recovery 1/30 → 9/30 and decision-level recovery 0/30 → 0/30, and
   it predicts that outcome rather than merely reporting it.
2. **A near-unit middle correlation is a warning sign, not a strength.**
   `|r| = 2^-0.01` over 8 rounds of Speck128/128, and `2^{-3.84×10^-5}` over 2.5
   rounds of ChaCha, are close enough to deterministic to be candidates for
   *structurally forced* parities — relations implied by the input difference and
   the round function rather than by any statistical bias worth attacking with.
   Under `docs/inventor-protocol.md` these demand a **null-object control** before
   they are treated as findings: check whether the same parity holds with the same
   correlation under a random key schedule, a reduced round count, or an unrelated
   input difference. The paper reports these correlations without such a control.
3. **A candidate mechanism for the mismatch: diffusion depth.** A mask whose
   middle correlation is near 1 is one the middle rounds have barely randomized,
   which plausibly means it is still close to the deterministic image of the input
   difference and therefore carries structure that costs weight when propagated
   *forward* through the linear part. If so, `|r|` and `|q|` are negatively
   associated across the candidate space and the neural preference is not merely
   uninformative about `q` but **anti**-informative. Falsifiable directly: compute
   `(|r|, |q|)` for all 77 strong Hamming-weight-2 masks and test for negative rank
   correlation. A null or positive result kills the mechanism.
4. **The two Hamming-weight-2 families in Table 6 look structurally different.**
   The masks the network prefers — `{72,8}`, `{71,7}`, `{70,6}`, `{69,5}`,
   `{67,3}` — are all of the form (left-word bit `b`, right-word bit `b`) on
   Speck128's two 64-bit words. The classically useful `{77,5}` is (left bit 13,
   right bit 5), an offset of 8, which is Speck128's rotation constant `α`. If the
   `α`-offset family systematically admits lower-weight forward linear trails,
   that is a **cheap enumerable prior** that would do what sparsity cannot. **Not
   verified here** — the bit-position arithmetic is this program's reading of the
   paper's notation and the structural claim is untested.
5. **The classical SipHash reference mask is not the strongest local candidate,
   and that is fine.** `{61,29}` at `2^-6.03` is beaten by 18 masks of Hamming
   weight ≤ 4. Before this is read as an improvement on [NSLL22], note that that
   work operates in the rotational-DL setting with arbitrary output masks and may
   have selected `{61,29}` for key-recovery reasons that raw distinguishing
   correlation does not capture. Verify the selection criterion in primary text
   before any comparison is recorded.
6. **The transferable lesson is not about neural networks.** A learned or
   heuristic search that scores an *intermediate* object by a locally measurable
   proxy will select against the composed objective whenever the proxy and the
   downstream cost are anti-correlated — the failure is in the objective, not the
   model class. This program runs at least one search of exactly that shape
   (`harness/rl_isogeny`, whose reward is null-relative Macaulay excess rather
   than downstream yield), and the same audit applies there. See
   [[KN-OPEN-7f0d85]].

## Not verified here

No experiment in this paper has been reproduced by this program. Every number
above is transcribed from the supplied text: the correlations, accuracies, trail
weights, recovery frequencies, and hyperparameters are **reported**, not
measured here. The bibliographic identifier is unresolved (see the provenance
note at the top). The cited prior works `[YWZW26]`, `[YXZW25]`, `[CBY23]`,
`[GWH+25]`, `[NSLL22]`, `[BLT20]`, `[ZYS+26]` are relayed as this paper cites
them; where this corpus holds an entry for one it is linked above, and where it
does not the reference remains `recalled` in the sense of `AGENTS.md` rule 9.
