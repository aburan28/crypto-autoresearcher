---
id: KN-FIND-028
type: internal_finding
title: AES supplies one element of order 4 in GL(4,GF(2^8)) on a column, so no
  GL/AGL transitivity argument kills column-local invariants; and byte-wise Inv
  preserves GF(2^8)-collinearity, so the obstruction at SubBytes is the affine
  layer L
tags:
- aes
- mixcolumns
- subbytes
- gf256
- collinearity
- transitivity
- burnside
- column-local
- scoped-negative
- argument-unavailability
- derivation
- toy-scale
- reduced-round
confidence: established
internal_refs:
- EV-AES-002
- DEC-20260731-025
- EV-AES-001
- DEC-20260731-011
- RQ-AES-001
- TASK-20260731-701
- TASK-20260731-705
proof_status: derivation
proof_refs:
- coordination/goals/GOAL-AES-001/batches/BATCH-002/tasks/TASK-20260731-701/derivation_note_column_local_obstructions.md
- coordination/goals/GOAL-AES-001/batches/BATCH-002/tasks/TASK-20260731-701/verify_derivation.py
- coordination/goals/GOAL-AES-001/batches/BATCH-002/tasks/TASK-20260731-705/derivation_and_ideation_review.md
added: 2026-08-01
superseded_by: null
---

## Why this entry exists

Two elementary facts about the algebra of AES components. Each is **negative**:
it says a particular *style of argument is unavailable*, and why. Each is an
error this program actually made, in the TASK-20260731-601 ideation package,
and that a reader who has not made it yet would plausibly make. They are
recorded so the error is not repeated.

Neither fact is a cryptanalytic claim. See "Non-claims" below, which is
load-bearing rather than boilerplate.

Both were produced under the reduced-round AES campaign **GOAL-AES-001**
(question `RQ-AES-001`), in BATCH-002, and promoted by `DEC-20260731-025` on
`EV-AES-002`. The goal ID is named here in prose rather than in
`internal_refs` because `GOAL-*` records are not registered in the validator's
ledger ID index (`tools/validate_ledger.py`, `LEDGER_DIRS`) and citing one
there is a schema error; the linkage is preserved without breaking the schema.

## Fact 1 — MixColumns supplies ONE element of GL(4,GF(2^8)), not the group

Let `F = GF(2^8)` under `x^8+x^4+x^3+x+1` (0x11B) and let `M` be the AES
MixColumns circulant with first row `(02,03,01,01)`, acting on one column
`F^4`.

- **`ord(M) = 4`.** Via the circulant isomorphism to `F[y]/(y^4+1) =
  F[z]/(z^4)` in characteristic 2: `c = 1 + n` with `n = 02z + z^3` nilpotent,
  so `c^2 = 1 + 04z^2 != 1` and `c^4 = 1`. Hence `<M> ~ Z/4`.
- **`|<M>| / |GL(4,GF(2^8))| = 4 / 338947946628913982763966439819837440000
  ~ 1.18e-38`.**
- **The orbit of `e1` under `<M>` has size 4** —
  `{(01,00,00,00), (02,01,01,03), (05,00,04,00), (0e,09,0d,0b)}` — against
  `q^4 - 1 = 4294967295` nonzero vectors.
- **Orbit count on nonzero vectors: at least `1073741824`, exactly
  `1073758335`.** Kernel dimensions of `M^e - I` are `4,1,2,1`, giving fixed
  nonzero counts `4294967295, 255, 65535, 255`; Burnside gives `1073758335`,
  cross-checked by stratification as `255 + 32640 + 1073725440`.

**What is therefore unavailable.** The true group fact `<translations,
GL(4,q)> = AGL(4,q)` is 2-transitive, but AES does not supply `GL(4,q)` on a
column — it supplies one element of order 4. On **differences**, AddRoundKey
acts trivially and the group available is exactly `<M> ~ Z/4`: not transitive.
On **states**, the group is `T . <M>` of order `q^4 * 4 = 17179869184`; it *is*
transitive (because `T` alone is) but the stabiliser of `0` is `<M>`, which has
`1073758335` orbits on the nonzero vectors, so it is **not 2-transitive**.
Consequently **no `GL`/`AGL` transitivity argument can exclude nonconstant
invariants of a single column difference, or of a pair of column states.** Such
invariants exist in abundance: they are exactly the functions constant on those
`1073758335` orbits.

**What survives.** Only the elementary fact that any invertible `F`-linear map
preserves collinearity (`M(lambda v) = lambda(Mv)`), so the *collinearity
relation* on column differences propagates deterministically through
AddRoundKey and MixColumns. That, and nothing about invariants in general, is
the correct residue.

## Fact 2 — Inv preserves GF(2^8)-collinearity; the affine layer L does not

With the AES convention `Inv(0) = 0`, extended byte-wise:

**`Inv(lambda v) = lambda^-1 Inv(v)` for every `v in F^n` and every
`lambda in F^*`, including at zero coordinates.** Case `v_i != 0`:
`(lambda v_i)^-1 = lambda^-1 v_i^-1`. Case `v_i = 0`: both sides are `0`. The
`Inv(0)=0` convention is not a nuisance to be waved past — it is exactly what
makes the identity hold on all of `F^n` rather than only on full-support
vectors. Hence `Inv` **preserves** collinearity (the *relation* is preserved;
the scalar is inverted, so `Inv` acts on the projective class by a genuine map,
not the identity).

**The `GF(2)`-affine layer `L(b) = Ab + 0x63` is the operative obstruction.**
Deterministic counterexample, checkable by hand: `v = (01,00,00,00)`,
`w = 02*v`, `L(v) = (7c,63,63,63)`, `L(w) = (5d,63,63,63)`; matching any of the
last three coordinates forces `mu = 1`, hence `7c = 5d`, false.

**The exception, stated rather than hidden (Corollary 2.2).** On **constant
vectors** `(a,a,a,a)`, `L` *does* preserve collinearity, since `L` applied
coordinate-wise yields another constant vector and any two nonzero constant
vectors are collinear. Verified exhaustively over all `255*254 = 64770` pairs
`(a, lambda)`: **64262 preserved, 508 degenerate, 0 broken**. This is why
Corollary 2.1 is correctly stated as "not **in general**", and it is
load-bearing: without it the universal statement would be false.

**Reading.** Inside `S = L . Inv`, the collinearity-breaking factor is `L`, not
`Inv`. Any argument of the form "the object dies at SubBytes because inversion
destroys the `GF(2^8)` structure" is **wrong as stated**; the conclusion may
still hold, but by a different mechanism.

## Reproduction

```
python3 coordination/goals/GOAL-AES-001/batches/BATCH-002/tasks/TASK-20260731-701/verify_derivation.py
```

Standard library only, all randomness seeded from constants in the source
(`202608010001`-`202608010004`, `N_SAMPLES = 4000`), one `CLAIM ` line per
claim, non-zero exit iff any claim FAILs.

Independently re-executed from the committed blob (`9618f55f...4951`, snapshot
`ebac9ba8`) in the TASK-20260731-705 session: **16 PASS, 0 FAIL, 1 SKIP of 17**.
That session additionally recomputed **every** fact above by its own method
(own GF multiply, brute-force inverse by search, own Gaussian elimination, own
seeds; no code or constants taken from the script) with **no discrepancy
anywhere**, including `ord(M)=4` by a second independent method, and the
scalar identity exhaustively over all `65280` `(lambda, x)` pairs, of which
`255` are at `x = 0`, with `0` failures.

Known script defect: claim `C0` (cross-check against the BATCH-001 harness)
SKIPs, because the loader omits `sys.modules[spec.name] = mod` before
`exec_module`, so `@dataclass` resolution fails (D-705-2). Its intent was
covered independently — the harness `AES_MIX` equals `M`, the harness S-box
equals an independently constructed `L(Inv(x))` on all 256 inputs, the harness
inverse equals an independent brute-force inverse on all 256 inputs, and the
harness MixColumns matrix has order 4.

## Non-claims — read this before citing

- **No cryptanalytic claim about AES of any kind, at any round count.** No
  distinguisher, no key recovery, no complexity claim, no measured structural
  excess.
- **Not a barrier statement about AES security.** Nothing here concerns
  full-round AES, AES-NI-deployed AES, or any deployed system.
- **Fact 1 removes an argument; it does not supply one.** It restores
  column-local objects to status *open*, which is strictly weaker than either
  "closed" or "promising". No claim is made that any of the `1073758335`
  orbit-invariants is useful, measurable, key-dependent or attack-relevant —
  only that their uselessness must be argued or measured, not deduced from
  transitivity.
- **Fact 2 is about values, not about differences.** `S(x+d) + S(x)` is not a
  function of `d`, so neither Fact 2 nor its corollaries says anything about
  whether collinearity of a *difference* vector survives a SubBytes layer.
  Symmetrically, on values collinearity is destroyed by AddRoundKey. This is
  the boundary at which correcting an over-strong claim would itself become an
  over-strong claim.
- **ShiftRows is a separate, untouched obstruction to column-local objects.**
  Column `j` of the output draws one byte from each of the four input columns,
  so a column-defined object is not carried to a column of the next state.
  Fact 1 is not a green light for column-local objects.
- **No novelty is claimed and none should be inferred.** Both facts are
  elementary and the honest expectation is that both are well known to
  specialists. No primary source was read: `eprint.iacr.org`, `csrc.nist.gov`
  and `arxiv.org` are unreachable under this campaign's network policy, so
  novelty is **unresolvable** in this environment. `confidence: established`
  refers to the internal verification status of the mathematics, not to
  novelty or priority.
- **`proof_status: derivation`**, copied from EV-AES-002: checkable written
  arguments with machine-recomputed numerical conclusions. Not machine-checked
  proof.
- The AES specification is pinned **operationally** — by the constants restated
  in the derivation note and by cross-checks against a harness whose full-round
  outputs agree three ways — not by a read specification. That is the strongest
  grounding available here and it is weaker than a read document.

## Adjacent result deliberately NOT promoted: PROP-701-I

The same task produced `PROP-701-I` (`candidate_report.yaml`, same directory):
*a round-independent, single-word, single-state, deterministic lossy projection
propagating across the AES super-box interface `Phi = ARK.MC.SR` is either
injective or constant* — proved from the facts that every MixColumns entry is
nonzero and that those entries generate `GF(2^8)*`. The independent
TASK-20260731-705 session worked all three steps and judged the **proof
complete and correct**, and confirmed the AES-shaped case exhaustively in a
`GF(2^4)` analogue (65535/65535 kernels closing to dimension 16).

It is **not promoted here**, and is named only so a future session can find it
without the corpus asserting it. Three reasons, recorded rather than argued
away:

1. Its own **pre-declared falsification gate GATE-701-C is VOID on its own
   terms**. When the validator ran it, `null_2` (circulant `(02,00,01,01)`)
   read 65535/65535 at dimension 16 — the *same* reading as the target — which
   fires the gate's declared VOID condition. The cause is general and worth
   remembering: `null_2` negates "every entry nonzero", which is a *sufficient*
   hypothesis of Step 2, not a necessary one. **A null built by negating a
   sufficient hypothesis is not automatically discriminating.** (`null_1`, the
   identity interface, does discriminate sharply — dimension 1 versus 16 — so
   the gate retains a working sensitivity anchor.)
2. Two scope holes are **unnamed** by the proposition: word-position-dependent
   families `pi_0..pi_3` within one layer, and restriction of the "for every
   state" quantifier to a structured subset. Neither invalidates a step; both
   narrow the closure.
3. The independent promotion-fitness verdict was issued for the derivation note
   **only**. `PROP-701-I` self-labels a probable re-derivation of known
   subspace-trail limits at recall confidence LOW-MEDIUM,
   `unverified_from_memory` — which does not by itself bar promotion, since
   this corpus records internal derivations rather than priority, but it is
   recorded here for completeness.

Do not cite `PROP-701-I` as established. See EV-AES-002 observations A-10 to
A-13 and DEC-20260731-025 for its exact standing and for what would change it.
