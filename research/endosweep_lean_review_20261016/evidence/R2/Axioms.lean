import CryptoResearch.Endosweep.LambdaCoordinates
import CryptoResearch.Endosweep.BinaryGLS
import CryptoResearch.Endosweep.XOnlyConjugate
import CryptoResearch.Endosweep.Pippenger
open CryptoResearch.Endosweep
#print axioms XOnlyConjugate.xonly_difference_eq_conj
#print axioms XOnlyConjugate.conj_eigenvalue
#print axioms XOnlyConjugate.eigen_conj_mod
#print axioms XOnlyConjugate.QuadOrder.trace_one_exists_iff_D_odd
#print axioms XOnlyConjugate.QuadOrder.omega_norms
#print axioms LambdaCoordinates.add_correct
#print axioms LambdaCoordinates.curve_equation_iff
#print axioms LambdaCoordinates.dbl_add_correct
#print axioms LambdaCoordinates.dbl_alt_eq_dbl_main
#print axioms LambdaCoordinates.dbl_main_correct
#print axioms LambdaCoordinates.madd_correct
#print axioms BinaryGLS.psi_add
#print axioms BinaryGLS.psi_eq_conj_by_twist
#print axioms BinaryGLS.psi_psi
#print axioms Pippenger.bit_conservation
#print axioms Pippenger.glv_wins_iff
#print axioms Pippenger.ideal_glv_wins_iff
#print axioms Pippenger.window_slots
#check @LambdaCoordinates.add_correct
#check @BinaryGLS.psi_psi
