/-
Axiom audit for the formal research lane.

`LeanWorker` runs this file with `lake env lean AxiomAudit.lean` after a
successful `lake build`, and treats a non-zero exit as a failed audit. So this
file has to FAIL LOUDLY, not merely print: `#print axioms foo` writes its
findings to stdout and exits 0 whatever it finds, which would make the audit
step a no-op that passes for any theorem at all.

What it checks: every theorem this project declares depends only on the three
axioms Lean's classical development is built on. Anything else fails the run.
The one that matters most is `sorryAx`, which is what an unfinished proof
leaves behind -- the textual scan in LeanWorker catches a literal `sorry`, and
this catches a dependency on one reached through any other route.

NOTE: this file has not yet been compiled against a live toolchain (the
container this was written in has no Lean). setup.sh runs it as its last step
so a mismatch surfaces at setup time rather than mid-campaign.
-/
import CryptoResearch
import Lean

open Lean Elab Command

namespace CryptoResearch.AxiomAudit

/-- The axioms Mathlib itself is built on. Nothing else is admissible: an
assumption the audit cannot see makes the artifact worthless. -/
def allowed : List Name := [``propext, ``Classical.choice, ``Quot.sound]

/-- Audit every theorem declared under the `CryptoResearch` namespace. -/
elab "#audit_project" : command => do
  let mut audited : Nat := 0
  let mut failures : Array MessageData := #[]
  for (name, info) in (← getEnv).constants.toList do
    if (`CryptoResearch).isPrefixOf name && !name.isInternal then
      if info matches .thmInfo _ then
        let axioms ← liftCoreM <| collectAxioms name
        let bad := axioms.filter (fun a => !allowed.contains a)
        audited := audited + 1
        unless bad.isEmpty do
          failures := failures.push m!"{name} depends on {bad.toList}"
  if failures.isEmpty then
    logInfo m!"axiom audit: {audited} theorem(s), all standard axioms only"
  else
    throwError "AXIOM AUDIT FAILED:{indentD (MessageData.joinSep failures.toList \", \")}"

end CryptoResearch.AxiomAudit

#audit_project
