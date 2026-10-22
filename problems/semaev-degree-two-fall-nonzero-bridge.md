# Semaev degree-two cancellation lacks a nonzero fall bridge

- **Status:** `open`
- **Kind:** proof gap, source-code defect, and interpretation gap
- **Affected work:** [historical measurement](../research/FFD_SEMAEV_MEASUREMENT1.md), [frozen formal target](../formal/targets/semaev-s3-degree2-fall-witness.yaml), [Lean trace theorem](../formal/CryptoResearch/Semaev/DegreeTwoFall.lean), [2026-10-20 validation report](../docs/reports/2026-10-20-formal-validation/report.md), [2026-10-22 corrected replay](../docs/reports/2026-10-22-semaev-first-fall-replay/report.md)
- **Next action owner:** formal research lane and Coordinator for claim wording
- **Last updated:** 2026-10-22

## Problem

The uniform claim that the descended Semaev `S₃` system has a nontrivial first fall at degree two is not proved by its Lean theorem. That theorem cancels degree-two coefficients for nonzero target abscissa `x_R`; it does not show that the residual gives a new nonzero class. A checked finite example contradicts the uniform conclusion in the stated toy Boolean model without refuting the narrower trace identity.

The historical first-fall implementation has a separate defect: `fall_profile` represents a monomial multiple as `{mm | m for mm in f}`. Boolean polynomial multiplication over F₂ requires duplicate monomials to cancel. The frozen summary is exactly reproducible as written, but its ranks and grades are not generally the ranks and grades of the Boolean F₂ polynomial system.

## Evidence and uncertainty

- **Archived observable:** The eight frozen cells report 70 of 80 Semaev draws at degree two and ten at degree three. The original script reproduced its JSON byte for byte on October 22. Its 200 support-matched null grades reproduced as well. The [archive receipt](../docs/reports/2026-10-22-semaev-first-fall-replay/evidence/archive-replay.json) binds the command, work directory and output hash.
- **Source defect witness:** In `n=4,n'=4,s=1`, the first equation multiplied by `u₀` has masks `1`, `17`, `129` in the archived set product; all three cancel in F₂. The archived product disagrees with direct product evaluation on 64 of 256 Boolean assignments; the corrected product agrees on all 256. The [checker](../research/verification/replay_ffd_semaev_20261022.py) asserts this and records it in [draws.json](../docs/reports/2026-10-22-semaev-first-fall-replay/evidence/draws.json).
- **Corrected exact data:** With XOR cancellation and independent binary ranks on the same 80 systems, 68 draws first fall at degree two and 12 at degree three. Two originally degree-two draws become degree three: `(n,n',s,x_R)=(5,3,4,8)` and `(5,3,8,8)`. Twelve of 200 null grades change. Seven corrected Semaev degree-three draws have `x_R≠0`; five have `x_R=0`. All 280 systems and both rank profiles are retained per draw.
- **Finite explanation:** At `n=4,n'=4,s=1,x_R=1`, the trace residual `u₀+u₃+w₀+w₃` is already the fourth linear generator. Correct Boolean ranks give `dim V₁=1`, `dim(V₂∩R_{≤1})=1`, so `new_falls(2)=0`; `dim V₂=11`, `dim V₃=53`, and `dim(V₃∩R_{≤2})=12`, so `new_falls(3)=1`. The trace theorem's nonzero-target premise holds, yet the stronger first-fall claim fails in this finite model.
- **Proved scope:** [`DegreeTwoFall.lean`](../formal/CryptoResearch/Semaev/DegreeTwoFall.lean) proves Artin–Schreier normalization and trace annihilation of quadratic coefficients. It does not prove a nonzero quotient class or universal first fall.
- **Unresolved:** The Boolean filtration and rank certificate need kernel-checked Lean formalization and independent semantic review. The frozen claim needs an additive correction through normal review; official hypothesis status is unchanged. The finite data do not establish solving degree or ECDLP cost.

## What would unblock it

- [ ] Formalize exact Boolean F₂ multiplication, the degree-compatible filtration, and the finite `n=4,n'=4,s=1` rank certificate in Lean. Prove the link from executable rank to vector-space dimension; state a qualified positive theorem only with hypotheses that exclude the checked exceptions, or publish the checked counterexample.
- [x] Replay every frozen seed, target, basis and equation; reproduce the archived table; compute the corrected parity ranks for all 80 Semaev and 200 null systems; classify all exceptional grades; retain exact equation hashes and source revision.
- [ ] Add a reviewed, additive correction to the frozen target and historical uniform wording. Keep the original record immutable and distinguish archived counts from corrected Boolean counts in every graph and dashboard.

Meeting these conditions would settle the toy Boolean claim. General solving-degree and cryptanalytic cost claims are separate obligations.

## Next discriminating step

- **Action:** Formalize the finite Boolean multiplication witness and the degree-two rank certificate in Lean, then compare the formal row construction with the Python checker on the exact equation masks.
- **Inputs and controls:** Use the source-hash-bound per-draw equations, 256-assignment multiplication witness, archived set result as a negative control, and corrected projection ranks. Preserve the existing trace lemma.
- **Execution limits and stop condition:** Do not edit the frozen target or infer a universal repair. A finite Lean certificate settles this toy counterexample only. If the rank model differs, record the precise definition mismatch before promoting any theorem.
- **Outcomes:** A kernel-checked exact model supports the additive correction; a mismatch requires resolving semantics; any qualified positive theorem needs independent review against these seven nonzero-target exceptions.
- **Recheck trigger:** Kernel-checked rank model or reviewed additive claim correction.

## Resolution and history

- 2026-10-20: Opened after comparing the frozen target, Lean scope, and raw summary; per-draw replay missing.
- 2026-10-22: Reproduced archived 70/10 counts. Independent Boolean F₂ multiplication exposed a source-code defect and corrected the same seeds to 68/12. The proof bridge and claim correction remain open; no official state transition was made.
