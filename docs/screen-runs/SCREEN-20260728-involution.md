# SCREEN-20260728 — unspent-involution screen run over the live portfolio

Screen: `KN-TECH-057`. Run 2026-07-28 against branch
`knowledge/eprint-arxiv-20260728`. Read-only; **no ledger record was modified and
no hypothesis status was changed** (AGENTS rule 1 — Coordinator authority).

> **REVISION 2, same day.** Revision 1 of this document reported two findings.
> **Both were substantially wrong**, because revision 1 screened
> `ledger/proposals/` and `ledger/hypotheses/` and did not read the
> corresponding **evidence** records. `EV-GGM-002` and `H-STR-002`'s own
> `interpretation_limits` already covered both, one of them more sharply than
> this run did. The retractions are in **§ Retractions** and are stated before
> anything that survives. Revision 1's text is superseded, not deleted — it is
> in this file's git history at commit `e14f16e5`.

## Scope, and the scoping error

38 records in `ledger/proposals/` (18) and `ledger/hypotheses/` (20). Trigger
term set: `symmetr|involut|automorph|galois|endomorph|negation|frobenius|
conjugat|equivalence class|orbit|invariant`. **12 triggered**; all 12 read.

**The error: `ledger/evidence/` was not in scope.** Two of the twelve triggering
hypotheses (`H-GGM-001`, `H-STR-002`) have evidence records, and those records
contain the analysis this run claimed was missing. A screen over specifications
that does not read the evidence produced from them will re-report defects the
program has already caught. That is a defect in this screen's procedure, and it
is corrected here rather than in a later note.

## Retractions

### Retracted — "the endomorphism arm of `H-GGM-001` cannot return a negative"

Revision 1 argued that `H-GGM-001` line 42 grants the simulator "any
endomorphism computable from" the curve parameters, so the endomorphism arm's
SIMULABLE verdict was fixed before any computation.

**`EV-GGM-002` had already withdrawn that verdict, on better grounds.** It
records that `EV-GGM-001`'s `endomorphism_oracle: SIMULABLE with C=0` was
obtained by "applying a coordinate formula **the model forbids**", that the
correct simulator answers `φ(σ(A))` as `[λ]σ(A)` **using only the group
oracle** — φ acting on the prime-order subgroup as multiplication by a publicly
computable λ — and that this preserves exponent 1/2 at `C = Θ(log N)`, not
`C = 0`. It further records that the result "restates Wiener–Zuccherato, GLV and
Duursma–Gaudry–Morain", that it "is not adopted as a finding", and that
simulability under a single frozen model "is UNDETERMINED by this record and is
not decided anywhere."

So the diagnosis was not merely known — it was **more accurate than this run's**.
Revision 1 guessed the run had been handed the endomorphism; in fact the run
applied a forbidden coordinate formula, and the honest simulator costs
`Θ(log N)`. Retracted in full.

### Retracted — "scope ceiling omitted from `IDEA-20260726-002` / `H-STR-002`"

Revision 1 claimed the records fail to state that results cannot transfer to the
target family. They state it. `H-STR-002` `interpretation_limits`: *"Toy scale
only (max 24 bits); applies only to GLV (j=0) curves"* and **"No claim about
generic curves or crypto-scale behavior."** `EV-STR-002` `boundaries`: *"Toy
scale only (max 20 bits); j=0 curves only."* Retracted.

## What survives

### 1. A narrow residual on `H-GGM-001`, for the Coordinator

`EV-GGM-002` repaired the **evidence**. It did not amend the **specification**,
and `H-GGM-001` is still `status: specified` — live.

The residual: line 42 defines public data as "the curve parameters (a, b, p, N)
and any endomorphism computable from them," which grants the simulator the
coordinate-level access that `EV-GGM-002` says the model forbids. The
specification that produced the withdrawn `C = 0` verdict is unamended, so a
re-execution against the frozen contract would reproduce it.

This is one sentence in one field, and it is **not** the revision-1 claim: the
arm is not vacuous, it has a real answer (`SIMULABLE` at `C = Θ(log N)`, per
`EV-GGM-002`), and the defect is that the spec licenses the wrong route to it.

**No correction record is written here.** `ledger/corrections/` records carry
`recorded_by: coordinator` and an `authorizing_decision`; this session has
neither, and writing one would be impersonating an authority AGENTS rule 1
reserves. Recorded as a flagged item, not a repair.

### 2. A knowledge point, already recorded in `KN-TECH-057`

The records say `H-STR-002` applies *only* to `j=0` curves. They do not say
*why* that is a ceiling rather than a starting point. Over a prime field an
efficiently computable endomorphism requires small-discriminant CM — `j ∈ {0,
1728}` and a short list besides — so the mechanism's two settings are special CM
curves (excluded from the target family) or extension fields (the known
Weil-descent lane). "We tested only `j=0`" and "`j=0` is the whole universe for
this mechanism over prime fields" are different statements, and only the first
is in the ledger.

That belongs in the knowledge corpus, where it already is (`KN-TECH-057`,
forward guidance). It is **not** a ledger defect and no ledger change follows.

## Triage table

| Record | Verdict |
|---|---|
| `H-FBG-001` | False positive — "asymmetric sizing" = unequal factor-base sizes |
| `H-IC-001`, `H-P13-001` | False positive — trigger terms in disclaimers, not mechanisms |
| `H-SUBRES-001` | Correctly self-scoped (ASSUM-2 excludes CM/automorphism structure) |
| `H-XEDN-003` | Correctly self-scoped — designed so growth is not attributable to the μ₃ automorphism |
| `IDEA-20260722-001` | Out of domain (lattice dual attack), but same family as HAWK (`KN-LIT-7592`); worth re-reading against it |
| `IDEA-20260726-003` | Not a symmetry-advantage claim; nearest instance of `KN-TECH-057` forward-guidance item 3 |
| `IDEA-20260726-002` / `H-STR-002` | Structurally the HAWK move. Screen does not kill it. Scope already correctly stated in-record |
| `IDEA-20260726-004` / `H-GGM-001` | Evidence-level defect already caught by `EV-GGM-002`; narrow specification residual survives (above) |

## Outcome

**Zero kills, and — after checking the evidence layer — zero new defects.** The
screen's net contribution to the ledger this run is one flagged sentence in
`H-GGM-001` and nothing else.

The more useful result is about the screen than about the portfolio: on its first
run it reported two findings the program had already recorded, because it read
specifications without reading the evidence produced from them. `KN-TECH-057`
must not be run again without `ledger/evidence/` in scope.

## What this run does not establish

- Nothing bears on `KN-OPEN-001`. Prime-field ECDLP is exactly as open as it was.
- `KN-TECH-057` remains `adaptation`/probable folklore and is not a theorem.
- 26 of 38 records never triggered the term set and were never examined.
- `EV-GGM-002`'s own caveats stand and are not adopted here as findings: it
  records that rule 12 is undischarged for it, that the reviewer's derivation
  "needs its own independent review", and that oracle simulability under a single
  frozen model is undetermined.
