/-
Source: docs/reports/ecdlp-lead-discovery-20261024/report.md, section f, "Derivation for the third target" @ branch lead-discovery/20261024-mythos-ecdlp
Target: formal/targets/ic-extension-field-embedding-20261024.yaml
Claim: Embedding the prime-field problem on E(F_p) (order about p) into E(F_{p^n})
  and running Gaudry's decomposition with the subfield base {x ∈ F_p} costs, under
  H6, p^{2 − 2/n + o(1)} for every fixed n ≥ 2 (KR-IC-46d822).  The reference is
  rho on the original group at p^{1/2}.  For every real n ≥ 2, 1/2 < 2 − 2/n;
  equivalently there is no n ≥ 2 with 2 − 2/n ≤ 1/2.  Without n ≥ 2 the statement
  fails at n = 1 (the trivial extension), so the degree hypothesis is
  load-bearing; n = 2 gives exponent 1.
WHAT IS PROVED: the real-number inequalities above.
WHAT IS NOT PROVED: Gaudry's cost itself (H6 is a heuristic hypothesis, not
  formalised); nothing about curve points, Weil restriction, o(1) terms, memory,
  or any finite size; nothing about other factor bases over F_{p^n}.
Heuristics taken as hypotheses:
  H6 Gaudry: decomposition index calculus on E(F_{q^n}) for fixed n costs
     q^{2 − 2/n + o(1)} (KR-IC-46d822, heuristic), applied with q = p.
Data: none.
-/
import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum

set_option autoImplicit false

namespace CryptoResearch.IC.ExtensionFieldEmbedding

/-- Gaudry's cost exponent on E(F_{p^n}) in base p (H6). -/
noncomputable def gaudryExponent (n : ℝ) : ℝ := 2 - 2 / n

/-- For every extension degree `n ≥ 2` the Gaudry exponent exceeds the generic `1/2`
of the original prime-field group. -/
theorem gaudry_exponent_gt_half (n : ℝ) (hn : 2 ≤ n) : 1 / 2 < gaudryExponent n := by
  unfold gaudryExponent
  have hpos : 0 < n := by linarith
  have h : 2 / n ≤ 1 := by
    rw [div_le_iff₀ hpos]
    linarith
  linarith

/-- No extension degree `n ≥ 2` brings the embedded problem to or below the generic exponent. -/
theorem embedding_never_helps : ¬ ∃ n : ℝ, 2 ≤ n ∧ gaudryExponent n ≤ 1 / 2 := by
  rintro ⟨n, hn, hle⟩
  have := gaudry_exponent_gt_half n hn
  linarith

/-- At `n = 2` the exponent is exactly 1 (the lead row's "p at n = 2"). -/
theorem exponent_at_two : gaudryExponent 2 = 1 := by
  unfold gaudryExponent
  norm_num

/-- Non-vacuity: the hypothesis `2 ≤ n` is satisfiable and the conclusion is not trivial there. -/
theorem main_hyps_satisfiable : ∃ n : ℝ, 2 ≤ n ∧ gaudryExponent n = 1 ∧ (1 : ℝ) / 2 < 1 :=
  ⟨2, le_rfl, exponent_at_two, by norm_num⟩

/-- Proves-too-much control: without `2 ≤ n` the claim fails at the trivial extension `n = 1`. -/
theorem needs_degree_two : gaudryExponent 1 < 1 / 2 := by
  unfold gaudryExponent
  norm_num

#print axioms gaudry_exponent_gt_half
#print axioms embedding_never_helps
#print axioms exponent_at_two
#print axioms main_hyps_satisfiable
#print axioms needs_degree_two

end CryptoResearch.IC.ExtensionFieldEmbedding
