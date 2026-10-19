import CryptoResearch.Endosweep.SubgroupIndex
import CryptoResearch.Endosweep.ChainEigen
import CryptoResearch.Endosweep.AlphaAdic
import CryptoResearch.Endosweep.FrobeniusSplit
import CryptoResearch.Endosweep.Blinding

/-! R3 review scratch: satisfiability witnesses, Python cross-checks, axioms. -/


#print axioms CryptoResearch.Endosweep.SubgroupIndex.index_eq_minorGcd
#print axioms CryptoResearch.Endosweep.SubgroupIndex.ideal_index_eq_elementIndex
#print axioms CryptoResearch.Endosweep.SubgroupIndex.cp6_782_certificate
#print axioms CryptoResearch.Endosweep.SubgroupIndex.bls12_381_control
#print axioms CryptoResearch.Endosweep.ChainEigen.cp6_782_chain_certificate
#print axioms CryptoResearch.Endosweep.ChainEigen.cryptopro_b_chain_certificate
#print axioms CryptoResearch.Endosweep.ChainEigen.glv_basis_spans_relation_lattice
#print axioms CryptoResearch.Endosweep.AlphaAdic.cp6_782_int_rule_1plus4w_cycle
#print axioms CryptoResearch.Endosweep.AlphaAdic.cp6_782_int_rule_terminates
#print axioms CryptoResearch.Endosweep.AlphaAdic.cryptoProB_int_rule_terminates
#print axioms CryptoResearch.Endosweep.AlphaAdic.norm_decrease
#print axioms CryptoResearch.Endosweep.AlphaAdic.terminates_of_disk
#print axioms CryptoResearch.Endosweep.FrobeniusSplit.order_F4_eq
#print axioms CryptoResearch.Endosweep.FrobeniusSplit.order_double
#print axioms CryptoResearch.Endosweep.FrobeniusSplit.q4_small_m
#print axioms CryptoResearch.Endosweep.FrobeniusSplit.q4_split
#print axioms CryptoResearch.Endosweep.Blinding.babai_unreduced_erases
#print axioms CryptoResearch.Endosweep.Blinding.decompose_mod_erases
#print axioms CryptoResearch.Endosweep.Blinding.blind_reconstructs
