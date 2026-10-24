import CryptoResearch
import Lean
open Lean Elab Command

-- binstd-x17-factorization.yaml
run_cmd do
  let target := `CryptoResearch.Binstd.x17_factorization
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- binstd-yield-ceiling.yaml
run_cmd do
  let target := `CryptoResearch.Binstd.YieldCeiling.saturated_open_below_band
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-alphaadic-int-rule-1plus4w-cycle.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.AlphaAdic.cp6_782_int_rule_1plus4w_cycle
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-alphaadic-int-rule-4plusw-cp6.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.AlphaAdic.cp6_782_int_rule_terminates
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-alphaadic-int-rule-4plusw.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.AlphaAdic.cryptoProB_int_rule_terminates
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-alphaadic-norm-decrease.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.AlphaAdic.norm_decrease
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-alphaadic-termination-from-disk.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.AlphaAdic.terminates_of_disk
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-blinding-classical-erased.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.Blinding.babai_unreduced_erases
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-blinding-mod-n.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.Blinding.decompose_mod_erases
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-blinding-reconstruction.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.Blinding.blind_reconstructs
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-chain-cp6-782-certificate.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.ChainEigen.cp6_782_chain_certificate
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-chain-cryptopro-b-certificate.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.ChainEigen.cryptopro_b_chain_certificate
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-chain-glv-basis.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.ChainEigen.glv_basis_spans_relation_lattice
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-disc-fundamental-from-primes.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.Discriminant.isFundamental_of_primes
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-disc-min-nonscalar-degree.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.Discriminant.minNonscalarDegree_isLeast
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-disc-squarefree-part-bound.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.Discriminant.prod_mul_bound_le_of_eq_mul_sq
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-dk-exact-batch2-discriminants.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.DkExactBatch2.exact_discriminants
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-dk-exact-batch3-discriminants.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.DkExactBatch3.exact_discriminants
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-dk-exact-batch4-discriminants.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.DkExactBatch4.exact_discriminants
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-dk-exact-batch5-discriminants.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.DkExactBatch5.exact_discriminants
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-dk-exact-discriminants.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.DkExact.exact_discriminants
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-frob-f4-trace.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.FrobeniusSplit.order_F4_eq
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-frob-lucas-double.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.FrobeniusSplit.order_double
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-frob-q4-small-m.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.FrobeniusSplit.q4_small_m
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-frob-q4-split.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.FrobeniusSplit.q4_split
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-gls-psi-endomorphism.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.BinaryGLS.psi_add
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-gls-psi-from-twist.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.BinaryGLS.psi_eq_conj_by_twist
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-gls-psi-squared.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.BinaryGLS.psi_psi
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-koblitz-curve-certificates.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.Koblitz.koblitz_certificates
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-koblitz-delta-norm.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.Koblitz.norm_delta
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-koblitz-lucas-norm.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.Koblitz.norm_one_sub_tau_pow
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-koblitz-min-norm.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.Koblitz.min_norm_nonscalar
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-koblitz-ztau-order.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.Koblitz.ztau_iso_order_neg_seven
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-lambda-add.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.LambdaCoordinates.add_correct
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-lambda-curve-equation.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.LambdaCoordinates.curve_equation_iff
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-lambda-dbl-add.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.LambdaCoordinates.dbl_add_correct
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-lambda-dbl-alt.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.LambdaCoordinates.dbl_alt_eq_dbl_main
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-lambda-dbl-theorem1.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.LambdaCoordinates.dbl_main_correct
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-lambda-madd.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.LambdaCoordinates.madd_correct
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-msm-bit-conservation.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.Pippenger.bit_conservation
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-msm-break-even.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.Pippenger.glv_wins_iff
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-msm-ideal-cstar.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.Pippenger.ideal_glv_wins_iff
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-msm-window-slots.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.Pippenger.window_slots
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-native-chains-bandersnatch.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.NativeChains.bandersnatch_native_chain_certificate
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-native-chains-cp6-782.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.NativeChains.cp6_782_native_chain_certificate
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-native-chains-tom384.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.NativeChains.tom384_native_chain_certificate
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-nist-b571-bound.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.NistCertificates.B571.abs_DK_lower_bound
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-nist-exact-discriminants.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.NistCertificates.exact_discriminants
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-nist-finding3-bounds.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.NistCertificates.finding3_bounds
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-nist-koblitz-discriminants.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.NistCertificates.koblitz_discriminants
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-rm-golden-norm-2adic.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.RMGoldenNorm.norm_eq_four_pow_mul_odd
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-subgroup-bls12-381-control.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.SubgroupIndex.bls12_381_control
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-subgroup-cp6-782-certificate.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.SubgroupIndex.cp6_782_certificate
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-subgroup-ideal-index.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.SubgroupIndex.ideal_index_eq_elementIndex
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-subgroup-index-gcd-minors.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.SubgroupIndex.index_eq_minorGcd
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-xonly-conjugate-difference.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.XOnlyConjugate.xonly_difference_eq_conj
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-xonly-conjugate-eigenvalue.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.XOnlyConjugate.conj_eigenvalue
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-xonly-odd-trace-needed.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.XOnlyConjugate.QuadOrder.trace_one_exists_iff_D_odd
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- endosweep-xonly-omega-norms.yaml
run_cmd do
  let target := `CryptoResearch.Endosweep.XOnlyConjugate.QuadOrder.omega_norms
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- frob-c4-null-curve-order.yaml
run_cmd do
  let target := `CryptoResearch.FrobTrace.NullCurveOrder.all_five_unique
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- frob-c5-characteristic-five-control.yaml
run_cmd do
  let target := `CryptoResearch.FrobTrace.CharacteristicFive.x_pow_five_sub_one_not_squarefree
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- frob-c5-factors-q11.yaml
run_cmd do
  let target := `CryptoResearch.FrobTrace.FactorKernel.q11_field_factor_kernel
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- frob-c5-factors-q13.yaml
run_cmd do
  let target := `CryptoResearch.FrobTrace.FactorKernel.q13_field_factor_kernel
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- frob-c5-factors-q19.yaml
run_cmd do
  let target := `CryptoResearch.FrobTrace.FactorKernel.q19_field_factor_kernel
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- frob-c5-finite-field-trace.yaml
run_cmd do
  let target := `CryptoResearch.FrobTrace.FiniteField.finite_field_c5_core
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- frob-c5-order-five-trace-kernel.yaml
run_cmd do
  let target := `CryptoResearch.FrobTrace.ker_trace5_eq_range_sub
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- frob-c5-quotient-matrices.yaml
run_cmd do
  let target := `CryptoResearch.FrobTrace.QuotientMatrices.all_quotient_frobenius_matrices
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- frob-c5-quotient-matrix-kernels.yaml
run_cmd do
  let target := `CryptoResearch.FrobTrace.QuotientMatrixKernels.all_matrix_C5_controls
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- lastfall-is-max-degree-fall.yaml
run_cmd do
  let target := `CryptoResearch.FallDegree.lastFallDegree_eq_max_degreeFall
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- ncp-affine-normal-form.yaml
run_cmd do
  let target := `CryptoResearch.NCP.word_action_affine_normal_form
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- ncp-commutator-ideal-refutation.yaml
run_cmd do
  let target := `CryptoResearch.NCP.kernel_not_generated_by_commutators
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- ncp-reachability.yaml
run_cmd do
  let target := `CryptoResearch.NCP.shadow_reachable_iff
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- quotient-translation-descent.yaml
run_cmd do
  let target := `CryptoResearch.Quotient.translation_descends_iff_two_torsion
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- runbook-example-bsgs-coverage.yaml
run_cmd do
  let target := `CryptoResearch.Runbook.BsgsCoverage.coverage
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- semaev-decomposition-certificate.yaml
run_cmd do
  let target := `CryptoResearch.Semaev.decidable_validDecomposition
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- semaev-frobenius-collapse.yaml
run_cmd do
  let target := `CryptoResearch.Semaev.pow_q_eq_frobeniusTwist_mod_fieldEquations
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- semaev-s3-boolean-parity-finite-20261022.yaml
run_cmd do
  let target := `CryptoResearch.Semaev.BooleanParityFiniteCertificate.exact_first_fall_at_three
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- semaev-s3-degree2-fall-witness.yaml
run_cmd do
  let target := `CryptoResearch.Semaev.trace_witness_annihilates_degree_two_part
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- semaev-s3-finite-equation-semantics-20261022.yaml
run_cmd do
  let target := `CryptoResearch.Semaev.FiniteEquationSemantics.all_component_equations_match_s3
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- semaev-s3-finite-filtration-20261022.yaml
run_cmd do
  let target := `CryptoResearch.Semaev.BooleanParityFiltrationCertificate.FiniteSemaev.existsNewLowDegreeVector
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- semaev-s3-semantic-rank-degree2-20261022.yaml
run_cmd do
  let target := `CryptoResearch.Semaev.BooleanParitySemanticRankCertificate.semanticNoFallTwo
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- semaev-s3-semantic-rank-degree3-20261022.yaml
run_cmd do
  let target := `CryptoResearch.Semaev.BooleanParityDegreeThreeRankCertificate.semanticOneNewFallThree
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"

-- semaev-symmetrization-degree.yaml
run_cmd do
  let target := `CryptoResearch.Semaev.totalDegree_symmetricRewrite_le
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"
