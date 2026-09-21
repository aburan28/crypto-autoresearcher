# Coordinator synthesis — 2026-07-18 experiment batch

**Scope:** 16 approved hypotheses executed by parallel Executor sub-agents under the
AGENTS.md cycle (frozen specs → seeded runs → controls → EV records → coordinator DEC
records). 12 from the Research Director submission `research_directions_20260717.md`
(candidates A1–D3), 4 from the HYPOTHESES_100 review batch (ICI, DREG, SIG, R6).
All runs toy-scale (p ≤ 2^12) with matched controls; nothing here is crypto-scale
evidence (rules 6–7). No run was fabricated; invalid/infrastructure runs are retained
as immutable records alongside the valid runs of record.

## Scoreboard

| Hypothesis | Experiment | Decision | One-line measured ground |
|---|---|---|---|
| H-JET-001 (A1 tangent-split) | EXP-JET-001 | rejected_scoped | σ ≡ 1.0000 exactly — ε-system implied by zeroth order; screen is pure overhead (16–23% worse) |
| H-INC-001 (A2 incidence reporting) | EXP-INC-001 | rejected_scoped | zero output sensitivity (α = 2.078 = Θ(B²) for all methods); EC chords at generic richness |
| H-STR-001 (A3 AP displacement rank) | EXP-STR-001 | rejected_scoped | supply penalty 17.5×–4128.6×; displacement rank at generic max; structured solve 4.9–39× worse |
| H-NET-001 (B1 elliptic-net Somos) | EXP-NET-001 | rejected_scoped | collision statistics = birthday (enrichment ≈ 1.1, all universal tautologies); charged exp 1.97–2.80 |
| H-BKK-001 (B2 sparse/BKK solve) | EXP-BKK-001 | rejected_scoped | sectioned S_m Newton-saturated: MV = Bézout_box exactly (ρ = 1 at m = 3,4,5) |
| H-EQJ-001 (B3 isotypic split) | EXP-EQJ-001 | rejected_scoped | 6/10 blocks exactly zero; rank never splits; reduces to FHJRV symmetrization bookkeeping |
| H-TRA-001 (C1 Koopman channel) | EXP-TRA-001 | rejected_scoped | L = O(1) (δ = 0.0195); coarse operators exactly reversible with real spectra — no phase channel at all |
| H-TTN-001 (C2 tensor-network) | EXP-TTN-001 | rejected_scoped | recall ≥ 0.99 needs full bond rank; growth α = 1.16–1.32 > gate 1; exact fit C(2^{m−3}+2, 2) predicts → 2 |
| H-NCP-001 (C3 NC path algebra) | EXP-NCP-001 | rejected_scoped | commutative quotient reproduces ALL NC relations (0 violations); exponents ≥ 0.80 |
| H-JETB-001 (D1 jet barrier) | EXP-JETB-001 | supported_scoped | simulable-model prediction matched exactly at all sizes (σ_true = 1, leakage 0) — toy barrier evidence |
| H-BKKMV-001 (D2 MV certificate) | EXP-BKKMV-001 | supported_scoped | certified law MV_m = (m−1)!·2^{(m−1)(m−2)}; box-saturated (ratio 1.0) — barrier side for B2-class |
| H-INCB-001 (D3 chord richness) | EXP-INCB-001 | supported_scoped | EC richness ≈ random lines at all sizes (the one z > 3 cell shown to be a fit artifact) — toy ceiling evidence |
| H-ICI-001 (IC exponent + UQ) | EXP-ICI-001 | rejected_scoped | crossbred 0.891 [0.869, 0.914]; MITM best 0.583; all CIs above 0.5; drift upward with extension |
| H-DREG-001 (d_reg deficit) | EXP-DREG-001 | **inconclusive** | instrument validated bit-identical (5 anchors); no past-wall cell measured (infrastructure censoring, rule 5) |
| H-SIG-001 (syzygy classification) | EXP-SIG-001 | **inconclusive** | non-Koszul D3 syzygy exists; residual non-rewritable D4 at all sizes; growth unresolved (1 seed) |
| H-R6-001 (explicit-base PDP) | EXP-R6-001 | rejected_scoped | α = 2.074 CI90 (1.565, 2.621), entirely > 0.5; d_reg flat 2; 2e4–1.5e5× above rho |

## What this batch establishes

1. **Twelve fresh mechanism families closed at toy scope, each with matched controls** —
   jets, incidence reporting, designed-support matrices, elliptic nets, sparse elimination,
   equivariant decomposition, operator spectra, tensor networks, noncommutative algebra,
   plus UQ-hardened IC exponents and explicit-base membership. Every one failed on
   *measured* quantities against its own pre-registered promotion gate, and ten of the
   twelve landed exactly on the fatal obstruction its candidate text named. The harness
   (specify → freeze → control → measure → decide) is working as intended.
2. **Three barrier-side theory results (toy-certified):** jet channels carry no
   information beyond zeroth order (D1, replicating A1's σ = 1 self-containedly); the
   target-sectioned Semaev family is Newton/box-saturated with a certified MV law
   (D2 + B2, two independent pipelines agreeing exactly); EC chord arrangements sit at
   the generic richness ceiling (D3). These convert folklore into measured, scoped
   statements and close their associated attack families.
3. **The two highest-value objects remain genuinely open:** the d_reg deficit past the
   memory wall (DREG — instrument now certified and checkpointed; n = 17 cells costed
   and resumable) and the non-rewritable syzygy growth question (SIG — existence shown,
   growth unresolved). Both have concrete, budgeted follow-ups.
4. **Reusable structural observations banked (rule 8):** TTN bond ranks are exactly and
   field-independently low (χ = 3, 6, 15 = C(2^{m−3}+2, 2)) even though truncation cannot
   exploit them; EQJ relation matrices collapse to few distinct rows; DREG sem-arm
   Macaulay column support declines (84→81%) while the null stays at 100%; SIG's 8n/3
   law fails at n = 9; INCB's EC c₃ runs 15–35% below the uniform prediction.

## Standing assessment (unchanged, hardened)

No generic prime-field ECDLP breakthrough was found, and the accumulating barrier-side
evidence (jets, polytopes, incidences, spectra) increasingly explains *why* whole
mechanism classes cannot deliver one. The honest research frontier is now:
(i) the two open objects above (DREG past-wall ladder, SIG growth law);
(ii) theory notes, not experiments: the jet simulation theorem (P7 amendment included),
the commutator-generation theorem (closes NC directions by proof), the sectioned
box-saturation/MV theorem (publishable), and the chord-richness ceiling via character sums.

## Next actions

- EXP-DREG-002: n = 17 sem + null full-rank cells from checkpoints (decisive for H-DREG-001).
- EXP-SIG-002: n = 12 re-run (non-degenerate seed) + multi-seed residual-growth ladder n ∈ {9,…,21}.
- Theory notes: THM_JETBARRIER1, commutator-kernel, MV/box-saturation, chord ceiling.
- All artifacts committed; ledger IDs DEC-20260718-001..016 reference EV-* and RUN-* records.

## Addendum — follow-up wave (EXP-DREG-002, EXP-SIG-002/003/004)

- **H-SIG-001: supported_scoped** (DEC-017/019/020). The boolean chained Semaev family carries a
  **degree-born non-rewritable syzygy cascade**: D3 count exactly 1 (all n = 9..21), D4 residual
  **2n/3 + 1** (9→11→13→15 at n = 12..21, replicated, zero seed variance, nulls exactly 0), D5
  deficit fully decomposes as deficit₅ = A4 + residual₅ − 1 with a D5-born component
  (878/879/1,158). The DREG rank deficit is therefore syzygy-born in mechanism; its
  n-asymptotics remain open. n = 9 is a uniform exception (mechanism unexplained).
- **H-DREG-001: still inconclusive** (DEC-018). First past-wall point certified two-partition:
  n = 17 sem deficit 1,823 (series 1,322/1,862/1,823/1,999, non-monotone; relative deficit
  4.71%→1.39%); null == sr_pred exactly at n = 17 (C1 discharged, partition A). The n = 21
  cell and the null-B gate are owned by the concurrent coordinator session — no duplicate dispatch.
- **Integrity:** EV-SIG-002's D4 series stands as a lower bound; EXP-SIG-004 re-anchored it with
  the canonical-reduction instrument (continuity verified on all 41 cells). Queued falsifiable
  checks: n = 24 residual == 17; residual_D birth law at D = 6.
- DEC-20260718-001..020 issued this session; every decision cites EV/RUN artifacts per rule 10.

## Addendum 2 — next-batch wave, decided 2026-07-22 (DEC-20260722-001..006)

This wave converted three toy-certified barrier results into PROVED THEOREMS and sharpened the
one supported structural finding:

- **Jet barrier is theorem** (THM_JETBARRIER1, T4): all order-r jet queries are simulable from
  zeroth-order public data with zero overhead; Shoup's Ω(√ℓ) lifts to the jet-augmented model.
  A1-class channels closed in-model BY PROOF. H-JETB-001 → supported.
- **Noncommutative direction closed by proof** (THM_COMMUTATOR_KERNEL1): kernel = normal closure
  of commutators + dihedral torsion + subset-sum lattice; theorem quantitatively reproduces the
  measured strict inclusion. Prime-field NC-correspondence closed.
- **Chord ceiling is theorem in the uniform-x model** (THM_INCBARRIER1): no ≥4-rich lines, exact
  T₃ law, phase diagram; the "c₃ deficit" was a heuristic artifact (1+3/B overstatement), not a
  signal. Group-AP excess exists but trivializes via rank defect. H-INCB-001 → supported.
- **MV law proved at m ≤ 5, certified at m = 6** (THM_BKKMV1 + EXP-BKKMV-002): box-saturation
  theorem proved; MV_m = (m−1)!·2^((m−1)(m−2)) = box Bézout; MV₆ = 125,829,120 exact on 6/6.
  All-m law reduced to one named lemma. H-BKKMV-001 → supported; B2-class barrier theorem-backed.
- **TTN rank law certified at m = 6** (EXP-TTN-002): χ(6) = 45 = C(10,2) exactly; new universal
  S_4 X-coefficient syzygy found (child bond 68). Slope trend toward asymptotic 2 continues —
  the attack rejection stands hardened.
- **SIG cascade sharpened AND bounded** (EXP-SIG-005): D4 residual law 2n/3+1 confirmed at n = 24
  (six-point linear series); but the D5-born component is NON-MONOTONE in n (drop at n = 18,
  replicated), and the D=6 axis is INVALID (support-matched null provably miscalibrated at D6).
  The cascade is confirmed through D = 5; its exploitability outlook is weaker than the first
  monotone picture. SIG and DREG deficit instruments now cross-validated bit-exactly.

Program state: 26 decisions on record. The mechanism-hunt side of the generic prime-field
program is now closed by a combination of scoped experiments and proved barriers across jets,
nets, polytopes, incidences, spectra, tensor networks, noncommutative algebra, isotypic splits,
and UQ-hardened index calculus. The live frontier is exactly: (i) the DREG deficit n-asymptotics
(n = 21 cell, concurrent session), (ii) the SIG cascade's degree axis (needs a re-derived D6
null baseline) and its n = 21 residual_5 point, (iii) two named theory lemmas (interior-fiber
non-cancellation; cross-character cancellation at α ≤ 1/2).

---

## Addendum 3 — frontier wave 2026-07-24 (DEC-20260724-001…005, CORR-20260724-002)

The three frontier items named in the closing program state above were pursued in parallel;
all five dispatched executors returned. Outcomes:

- **Theory frontier (i/c): both named lemmas resolved.**
  - *THM_INCBARRIER2* (DEC-001): the norm/moment certification family provably caps at
    α = 1/2 — the method ceiling is now theorem, not conjecture. New unconditional energy
    certificate |T3 − μ| ≤ (1/6)·√(B·N2) proved and measured 8–70× sharper than Weil on all
    21 toy factor bases. Conditional ladder α > (k+1)/(2k+1) supersedes the old heuristic cap;
    the whole problem is reduced to one named statement CC(α), α ≤ 1/2, with closing input
    BIL(θ = 1/4). 148 verification checks, 0 failures. Incidence line is CLOSED at the
    theory level; H-INCB-001 stays supported with the ceiling on record.
  - *THM_BKKMV2* (DEC-002): the interior-fiber non-cancellation lemma is decomposed into
    three named gaps G1/G2/G3 with falsifiable degree predictions deg_b S_{6,7,8} = 23, 57, 135;
    T1–T8 proved. **Erratum (CORR-20260724-002)**: THM_BKKMV1 §4's u_5-artifact claims are
    invalidated (a²-vs-a³ exponent bug); main Theorem 2 unaffected and stands.
    H-BKKMV-001 stays supported.
- **SIG frontier (ii): D6 axis re-derived, n = 21 advanced.**
  - *EXP-SIG-006* (DEC-003): the D6 failure is diagnosed as the semi-regular freeze-degree
    break — first HF = 0 at D = n/3 + 3; the null saturates rank = ncols − |V| exactly, so
    column-matched nulls still fail. The D6 baseline is predicted VALID for n ≥ 12
    (sr_pred(12,6) = 156,520). New confound on record: column-matching itself induces
    syzygies (N1 D5 extra = 369), so part of the sem-D5 deficit may be support-induced.
  - *EXP-SIG-007* (DEC-004): residual_4 = 15 at n = 21 — the 2n/3+1 law now holds on SEVEN
    points (n = 8…21). Closure A3_5 = 800, A4_5 = 1,407 (increments accelerating
    +261/+321/+381). residual_5/deficit_5 at n = 21 not yet measured; rank checkpointed at
    48,000/778,394 cols with a resumable command. Null D5 censored → D5 numbers preliminary.
- **DREG frontier (i): n = 21 cell progressing under checkpoint discipline.**
  - *EXP-DREG-004* (DEC-005): 142,000/778,394 columns (18.24%) at the sem-D5 cell;
    sr_pred = 268,674 reproduced exactly. Chunk size ≤ 6,000 fits the 300 s cap; two-partition
    control is mandatory before any rank claim; ~8–9 h wall-clock remain, resumable.

Hypothesis statuses unchanged this wave: H-INCB-001 supported, H-BKKMV-001 supported,
H-SIG-001 supported_scoped, H-DREG-001 inconclusive (awaits the completed n = 21 rank and the
5-point deficit series).

Program state: 32 decisions + 2 corrections on record. The live frontier is now exactly:
(i) finish the DREG n = 21 cell (multi-turn, checkpointed); (ii) EXP-SIG-008 — validate the
D6 null baseline at n = 12 against sr_pred = 156,520, then take the first admissible
residual_6 measurement and quantify the support-induced share of the D5 deficit;
(iii) the named theory statements CC(α)/BIL(1/4) and G1/G2/G3 with their degree predictions
(23, 57, 135) as the only remaining theory targets.
