import ScopedObstructions.Torsion
import Lean
open Lean Elab Command
run_cmd do
  let target := `ScopedObstructions.AdditiveModel.odd_translation_outside_kernel
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {target}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {bad.toList}"
  logInfo m!"target axiom audit passed: {target}"
