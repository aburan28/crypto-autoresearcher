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
