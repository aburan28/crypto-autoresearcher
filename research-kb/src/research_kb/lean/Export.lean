/- Read compiled environments with the same axiom collector as CryptoLean's gate.
   Run after `lake build`, via `research-kb export-lean` on the operator host. -/
import Lean
open Lean

abbrev AuditM := StateT Environment IO
instance : MonadEnv AuditM := { getEnv := get, modifyEnv := modify }

def main (args : List String) : IO UInt32 := do
  if args.isEmpty then
    IO.eprintln "usage: Export <Module> [<Module> ...]"
    return 2
  initSearchPath (← findSysroot)
  let roots := args.map String.toName
  let env ← importModules (roots.map fun m => { module := m }).toArray {} (trustLevel := 0)
  let names := env.constants.fold (init := (#[] : Array Name)) fun acc n _ =>
    match env.getModuleIdxFor? n with
    | none => acc
    | some idx =>
      let m := env.header.moduleNames[idx.toNat]!
      if !n.isInternal && roots.any (fun r => r == m || r.isPrefixOf m) then acc.push n else acc
  for n in names.qsort (·.toString < ·.toString) do
    let some ci := env.find? n | continue
    let kind := match ci with
      | .thmInfo _ => "theorem"
      | .axiomInfo _ => "axiom"
      | _ => "definition"
    let axs ← (collectAxioms n : AuditM (Array Name)).run' env
    let moduleName := match env.getModuleIdxFor? n with
      | some idx => env.header.moduleNames[idx.toNat]!.toString
      | none => ""
    let doc ← findDocString? env n
    IO.println (Json.mkObj [
      ("name", toJson n.toString), ("module", toJson moduleName),
      ("kind", toJson kind), ("kernel_type", toJson (toString ci.type)),
      ("axioms", toJson (axs.map Name.toString)),
      ("docstring", toJson (doc.getD ""))]).compress
  return 0
