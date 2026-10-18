import Lean
import CryptoResearch.Semaev.Certificate
import CryptoResearch.NCP.AffineNormalForm
import CryptoResearch.NCP.CommutatorIdeal
open Lean Elab Command
#print axioms CryptoResearch.Semaev.inDeclaredSpan_iff
run_cmd do
  let target := `CryptoResearch.Semaev.inDeclaredSpan_iff
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
#print axioms CryptoResearch.Semaev.checkDecomposition_iff
run_cmd do
  let target := `CryptoResearch.Semaev.checkDecomposition_iff
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
#print axioms CryptoResearch.Semaev.decidable_validDecomposition
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
#print axioms CryptoResearch.NCP.wordSign_eq_negOne_pow
run_cmd do
  let target := `CryptoResearch.NCP.wordSign_eq_negOne_pow
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
#print axioms CryptoResearch.NCP.word_action_affine_normal_form
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
#print axioms CryptoResearch.NCP.same_shadow_same_action
run_cmd do
  let target := `CryptoResearch.NCP.same_shadow_same_action
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
#print axioms CryptoResearch.NCP.orbit_value
run_cmd do
  let target := `CryptoResearch.NCP.orbit_value
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
#print axioms CryptoResearch.NCP.neg_square_not_in_commutators
run_cmd do
  let target := `CryptoResearch.NCP.neg_square_not_in_commutators
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
#print axioms CryptoResearch.NCP.neg_square_in_action_kernel
run_cmd do
  let target := `CryptoResearch.NCP.neg_square_in_action_kernel
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
#print axioms CryptoResearch.NCP.kernel_not_generated_by_commutators
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
