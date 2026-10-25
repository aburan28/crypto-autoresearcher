/-
Axiom audit for the repository's Lean proof gate (tools/lean/proof-gate.sh).

Usage: lake env lean --run tools/lean/AuditAxioms.lean [--trusted FILE] <Module> [<Module> ...]

Imports the named modules, then, for every theorem declared in them (including
submodules sharing the prefix), collects the axioms it depends on transitively.
Only Lean's standard foundations are accepted: `propext`, `Classical.choice`
and `Quot.sound`. Anything else fails the gate, in particular:

* `sorryAx`          -- a `sorry` anywhere in the proof or its dependencies;
* `Lean.ofReduceBool` / `Lean.trustCompiler`
                     -- `native_decide`, which trusts the compiler, not the kernel;
* any user `axiom`   -- an assumption standing in for the research claim.

`--trusted FILE` names theorems whose `native_decide` use was reviewed and
recorded (one fully qualified name per line, then `#` and the reason). Such a
theorem is reported as TRUST, not ok: its only non-standard axioms may be the
compiler-trust axioms `native_decide` generates. Anything else still fails.

Prints one line per theorem and exits 1 if any theorem uses a non-standard axiom
or if no theorem was found (a gate that audits nothing must not pass).
-/
import Lean
open Lean

def standardAxioms : List Name := [``propext, ``Classical.choice, ``Quot.sound]

def inScope (env : Environment) (roots : List Name) (c : Name) : Bool :=
  match env.getModuleIdxFor? c with
  | none => false
  | some idx =>
    let m := env.header.moduleNames[idx.toNat]!
    roots.any fun r => r == m || r.isPrefixOf m

/-- The smallest monad `collectAxioms` accepts: just an environment. -/
abbrev AuditM := StateT Environment IO
instance : MonadEnv AuditM := { getEnv := get, modifyEnv := modify }

/-- An axiom `native_decide` introduces (`<thm>._native.native_decide.ax_…`) or the
compiler-trust axioms it historically used. -/
def isNativeAxiom (a : Name) : Bool :=
  a == `Lean.ofReduceBool || a == `Lean.trustCompiler ||
    (a.toString.splitOn "._native.native_decide.").length > 1

def readTrusted (path : String) : IO (List Name) := do
  let lines ← IO.FS.lines path
  return lines.toList.filterMap fun l =>
    let n := String.ofList (((l.splitOn "#").head!).toList.filter (fun c => !c.isWhitespace))
    if n.isEmpty then none else some n.toName

def main (args : List String) : IO UInt32 := do
  let (trusted, args) ← match args with
    | "--trusted" :: f :: rest => do pure ((← readTrusted f), rest)
    | _ => pure ([], args)
  if args.isEmpty then
    IO.eprintln "usage: AuditAxioms [--trusted FILE] <Module> [<Module> ...]"
    return 2
  let roots := args.map String.toName
  initSearchPath (← findSysroot)
  let env ← importModules (roots.map fun m => { module := m }).toArray {} (trustLevel := 0)
  let thms := env.constants.fold (init := (#[] : Array Name)) fun acc n ci =>
    match ci with
    | .thmInfo _ => if !n.isInternal && inScope env roots n then acc.push n else acc
    | _ => acc
  let thms := thms.qsort (·.toString < ·.toString)
  let mut bad := 0
  let mut trustedCount := 0
  for n in thms do
    let axs ← (collectAxioms n : AuditM (Array Name)).run' env
    let extra := axs.toList.filter (!standardAxioms.contains ·)
    if extra.isEmpty then
      IO.println s!"ok    {n}  [{", ".intercalate (axs.toList.map toString)}]"
    else if trusted.contains n && extra.all isNativeAxiom then
      trustedCount := trustedCount + 1
      IO.println s!"TRUST {n}  native_decide, recorded in the trust manifest"
    else
      bad := bad + 1
      IO.println s!"FAIL  {n}  non-standard axioms: {extra}"
  IO.println s!"audited {thms.size} theorems in {roots}; {bad} failing, {trustedCount} trusted (native_decide)"
  if thms.isEmpty then
    IO.eprintln "no theorems found: refusing to pass an audit of nothing"
    return 1
  return if bad == 0 then 0 else 1
