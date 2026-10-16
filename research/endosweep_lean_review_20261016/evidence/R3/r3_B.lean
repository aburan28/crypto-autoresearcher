import CryptoResearch.Endosweep.SubgroupIndex
import CryptoResearch.Endosweep.ChainEigen
import CryptoResearch.Endosweep.AlphaAdic
import CryptoResearch.Endosweep.FrobeniusSplit
import CryptoResearch.Endosweep.Blinding

/-! R3 review scratch: satisfiability witnesses, Python cross-checks, axioms. -/

namespace R3

open CryptoResearch.Endosweep

-- (3) glv_basis_spans_relation_lattice: hypotheses satisfiable
#check ChainEigen.glv_basis_spans_relation_lattice 7 3 (7, 0) (-3, 1) (by decide) (by decide) (by decide) (Or.inl (by decide))

-- (4) norm_decrease: hypotheses satisfiable (175 = (4+w)(5-w) on D = -619)
example : AlphaAdic.mul 1 155 (4, 1) (5, -1) = AlphaAdic.sub (175, 0) (0, 0) := by decide
#check AlphaAdic.norm_decrease (τ := 1) (m := 155) (by decide) (4, 1) (175, 0) (0, 0) (5, -1) 7569
  (by decide) (by decide) (by unfold AlphaAdic.Outside; decide)

end R3
