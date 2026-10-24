import CryptoResearch.Endosweep.DkExactBatch5
import Lean
open Lean Elab Command
run_cmd do
  let target := `CryptoResearch.Endosweep.DkExactBatch5.gost_gost512
  match (← getEnv).find? target with
  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"
  | _ => throwError "requested declaration is not a theorem: {target}"
