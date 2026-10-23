import ScopedObstructions
import Lean
open Lean Elab Command

run_cmd do
  for target in [``ScopedObstructions.AdditiveModel.odd_translation,
                 ``ScopedObstructions.AdditiveModel.odd_translation_outside_kernel,
                 ``ScopedObstructions.even_scalar_control,
                 ``ScopedObstructions.positive_control] do
    match (← getEnv).find? target with
    | some (.thmInfo _) => pure ()
    | _ => throwError "requested declaration is not a theorem: {target}"
    let axioms ← liftCoreM <| Lean.collectAxioms target
    unless axioms.isEmpty do
      throwError "nonempty axiom dependency list for {target}: {axioms.toList}"
    logInfo m!"zero-axiom audit passed: {target}"
