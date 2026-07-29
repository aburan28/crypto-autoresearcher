# SCREEN-20260728 — unspent-involution screen run over the live portfolio

Screen: `KN-TECH-057`. Run 2026-07-28 against branch
`knowledge/eprint-arxiv-20260728`. Read-only; **no ledger record was modified and
no hypothesis status was changed** (AGENTS rule 1 — Coordinator authority).

## Scope

38 records in `ledger/proposals/` (18) and `ledger/hypotheses/` (20). Trigger
term set: `symmetr|involut|automorph|galois|endomorph|negation|frobenius|
conjugat|equivalence class|orbit|invariant`. **12 triggered**; all 12 read
individually.

## Headline: the screen killed nothing

Zero records were closed. Recording that plainly, because a screen that reports
kills it did not make is worse than useless. What the run produced instead is one
**scope ceiling** and one **design defect** — both checkable, both stated below
with the file and line that carry them.

## Triage

| Record | Verdict |
|---|---|
| `H-FBG-001` | **False positive.** "Asymmetric sizing" = unequal factor-base sizes, not a symmetry. Out of scope |
| `H-IC-001`, `H-P13-001` | **False positive.** Trigger terms appear in disclaimers, not mechanisms (`IDEA-20260725-001`: "No sub-`p^{1/4}` endomorphism-ring break is claimed") |
| `H-SUBRES-001` | **Correctly self-scoped.** ASSUM-2 explicitly assumes ordinary, non-anomalous, `j ∉ {0, 1728}`, "so no CM or automorphism structure supplies a collapse that would not exist on a generic curve." Screen agrees; no action |
| `H-XEDN-003` | **Correctly self-scoped.** Explicitly designed so that observed growth is *not* attributable to the μ₃ automorphism. This is the control discipline the screen asks for, already present |
| `IDEA-20260722-001` | **Out of domain, newly relevant.** Isometry-orbit batching for lattice dual attacks — the object is a lattice, not a curve. But this is the *same family as HAWK* (`KN-LIT-7592`, module-LIP), so the new result bears on it directly and it should be re-read against `KN-LIT-7592` |
| `IDEA-20260726-003` | **Not a symmetry-advantage claim.** Uses the Galois group of the Semaev fiber as a *predictor feature*. Notable because it is the nearest existing instance of `KN-TECH-057`'s forward guidance item 3 — symmetry on a derived object rather than on `E(F_p)` |
| `IDEA-20260726-002` / `H-STR-002` | **Direct instance — with a hard scope ceiling.** See below |
| `IDEA-20260726-004` / `H-GGM-001` | **Design defect.** See below |

## Finding 1 — scope ceiling on `IDEA-20260726-002` / `H-STR-002`

The proposal ("Endomorphism-invariant factor base for block-structured relation
matrix linear algebra") chooses the factor base as a union of φ-orbits so the
relation matrix acquires block-circulant structure and admits a
low-displacement-rank solve. **This is structurally the HAWK move**: an
underused symmetry converts the derived object into a class that already has a
better-than-generic algorithm. It is the closest thing in the portfolio to the
mechanism that took down a NIST candidate, and the screen does **not** kill it.

What the screen adds is a ceiling the records do not state. Over a **prime**
field, an efficiently computable endomorphism requires CM by a small
discriminant — `j = 0`, `j = 1728`, and a short list besides. `H-STR-002`
confirms this is where it lives: "toy GLV prime-field curves (`j=0`,
`p ≡ 1 mod 3`)". So the two available settings are:

1. **Special CM prime-field curves** — `j ∈ {0, 1728}`. These are *excluded from
   the program's target family* of random ordinary curves, which `KN-TECH-018`
   states directly and which `H-SUBRES-001`'s own ASSUM-2 relies on.
2. **Extension fields** — where GLS-type endomorphisms are broadly available.
   That is the Galois-exposed setting, i.e. the Weil-descent / summation-polynomial
   lane (`KN-TECH-016`) already known to be the productive one.

**There is no third option**, and the two options are exactly the two branches of
`KN-TECH-057`'s forward guidance. The consequence worth recording: whatever
`EXP-STR-002` measures, **it cannot transfer to the target family** — a positive
result is a statement about special curves or about the already-known extension-field
lane. That does not make the experiment worthless; it makes its `scope` field
wrong if it does not say this.

Two further notes. `H-STR-002` already carries the right falsifier —
"the φ-orbit relation-density penalty ≥ B/α, meaning the LA [saving is
cancelled]" — which is precisely the cost-cancellation pattern from
`KN-LIT-7593`, where the naïve Möbius invariant cost more than the 256× it
saved and three separate optimizations were needed to pay it back. The
`KN-LIT-7593` precedent suggests the density penalty is the likely outcome and
that the interesting question is whether it can be paid back, not whether it
appears.

## Finding 2 — the endomorphism arm of `H-GGM-001` cannot return a negative

`H-GGM-001` line 42 fixes the model's public data as **"the curve parameters
(a, b, p, N) and any endomorphism computable from them."** Lines 46–47 list the
four oracles to be given a SIMULABLE / NON-SIMULABLE verdict: **jet,
elliptic-net, incidence, endomorphism.**

The simulator is therefore granted the endomorphism, and then asked whether an
endomorphism oracle is simulable. For the only endomorphisms that matter here —
efficiently computable ones, given by explicit rational maps determined by the
curve equation — the answer is fixed at SIMULABLE **by the model's own
definition of public data**, before any computation. The arm has no possible
negative outcome.

This violates a rule already in the harness: `.claude/agents/idea-generator.md`,
"Never propose an experiment with no possible negative outcome."

Precise scope of the claim:
- It applies to **one arm of four**. The jet, elliptic-net, and incidence arms
  are untouched and their verdicts remain genuinely open.
- The narrow escape, which should be named rather than assumed away: an
  endomorphism *not* computable from `(a, b, p, N)` — one requiring the CM order,
  a discrete-log-dependent precomputation, or auxiliary data. If `IDEA-20260726-004`
  intends that case, the record does not say so, and line 42 should be amended to
  exclude it explicitly.
- The defect is in the **specification**, not in any executed run. No evidence
  record is impugned.

**Recommended (Coordinator's call, not mine):** either amend `H-GGM-001` line 42
to withhold the endomorphism from the simulator, or strike the endomorphism arm
from `IDEA-20260726-004` and record why. Per AGENTS rule 2 this is a supersede,
not an edit.

## What this run does not establish

- **No kills.** Nothing was closed.
- The screen is `adaptation`/probable folklore (`KN-TECH-057` status section) and
  is **not a theorem**. Finding 1 is a scoping observation resting on textbook
  GLV/CM facts and on `KN-TECH-018`; Finding 2 rests on two line ranges in one
  file and is checkable in under a minute.
- Neither finding bears on `KN-OPEN-001`. Prime-field ECDLP is exactly as open
  as it was.
- 26 of 38 records were never examined — they did not trigger the term set. A
  symmetry argument phrased without any of those words would have been missed.
