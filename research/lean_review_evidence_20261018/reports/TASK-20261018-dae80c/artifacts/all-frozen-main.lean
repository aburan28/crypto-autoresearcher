import CryptoResearch.Endosweep.AlphaAdic
import CryptoResearch.Endosweep.BinaryGLS
import CryptoResearch.Endosweep.Blinding
import CryptoResearch.Endosweep.ChainEigen
import CryptoResearch.Endosweep.Discriminant
import CryptoResearch.Endosweep.DkExact
import CryptoResearch.Endosweep.DkExactBatch2
import CryptoResearch.Endosweep.DkExactBatch3
import CryptoResearch.Endosweep.FrobeniusSplit
import CryptoResearch.Endosweep.Koblitz
import CryptoResearch.Endosweep.LambdaCoordinates
import CryptoResearch.Endosweep.NativeChains
import CryptoResearch.Endosweep.NistCertificates
import CryptoResearch.Endosweep.Pippenger
import CryptoResearch.Endosweep.RMGoldenNorm
import CryptoResearch.Endosweep.SubgroupIndex
import CryptoResearch.Endosweep.XOnlyConjugate
import CryptoResearch.FallDegree.LastFall
import CryptoResearch.NCP.AffineNormalForm
import CryptoResearch.NCP.CommutatorIdeal
import CryptoResearch.Quotient.TranslationDescent
import CryptoResearch.Runbook.BsgsCoverage
import CryptoResearch.Semaev.Certificate
import CryptoResearch.Semaev.DegreeTwoFall
import CryptoResearch.Semaev.FrobeniusCollapse
import CryptoResearch.Semaev.Symmetrization
import Lean
open Lean Elab Command
run_cmd do
  let target := `CryptoResearch.Endosweep.AlphaAdic.cp6_782_int_rule_1plus4w_cycle
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.AlphaAdic.cp6_782_int_rule_terminates
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.AlphaAdic.cryptoProB_int_rule_terminates
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.AlphaAdic.norm_decrease
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.AlphaAdic.terminates_of_disk
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.Blinding.babai_unreduced_erases
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.Blinding.decompose_mod_erases
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.Blinding.blind_reconstructs
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.ChainEigen.cp6_782_chain_certificate
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.ChainEigen.cryptopro_b_chain_certificate
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.ChainEigen.glv_basis_spans_relation_lattice
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.Discriminant.isFundamental_of_primes
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.Discriminant.minNonscalarDegree_isLeast
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.Discriminant.prod_mul_bound_le_of_eq_mul_sq
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.DkExactBatch2.exact_discriminants
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.DkExactBatch3.exact_discriminants
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.DkExact.exact_discriminants
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.FrobeniusSplit.order_F4_eq
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.FrobeniusSplit.order_double
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.FrobeniusSplit.q4_small_m
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.FrobeniusSplit.q4_split
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.BinaryGLS.psi_add
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.BinaryGLS.psi_eq_conj_by_twist
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.BinaryGLS.psi_psi
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.Koblitz.koblitz_certificates
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.Koblitz.norm_delta
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.Koblitz.norm_one_sub_tau_pow
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.Koblitz.min_norm_nonscalar
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.Koblitz.ztau_iso_order_neg_seven
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.LambdaCoordinates.add_correct
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.LambdaCoordinates.curve_equation_iff
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.LambdaCoordinates.dbl_add_correct
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.LambdaCoordinates.dbl_alt_eq_dbl_main
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.LambdaCoordinates.dbl_main_correct
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.LambdaCoordinates.madd_correct
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.Pippenger.bit_conservation
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.Pippenger.glv_wins_iff
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.Pippenger.ideal_glv_wins_iff
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.Pippenger.window_slots
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.NativeChains.bandersnatch_native_chain_certificate
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.NativeChains.cp6_782_native_chain_certificate
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.NativeChains.tom384_native_chain_certificate
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.NistCertificates.B571.abs_DK_lower_bound
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.NistCertificates.exact_discriminants
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.NistCertificates.finding3_bounds
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.NistCertificates.koblitz_discriminants
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.RMGoldenNorm.norm_eq_four_pow_mul_odd
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.SubgroupIndex.bls12_381_control
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.SubgroupIndex.cp6_782_certificate
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.SubgroupIndex.ideal_index_eq_elementIndex
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.SubgroupIndex.index_eq_minorGcd
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.XOnlyConjugate.xonly_difference_eq_conj
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.XOnlyConjugate.conj_eigenvalue
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.XOnlyConjugate.QuadOrder.trace_one_exists_iff_D_odd
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Endosweep.XOnlyConjugate.QuadOrder.omega_norms
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.FallDegree.lastFallDegree_eq_max_degreeFall
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.NCP.word_action_affine_normal_form
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.NCP.kernel_not_generated_by_commutators
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Quotient.translation_descends_iff_two_torsion
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Runbook.BsgsCoverage.coverage
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Semaev.decidable_validDecomposition
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Semaev.pow_q_eq_frobeniusTwist_mod_fieldEquations
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Semaev.trace_witness_annihilates_degree_two_part
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
run_cmd do
  let target := `CryptoResearch.Semaev.totalDegree_symmetricRewrite_le
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
