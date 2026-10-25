# Concrete finite Semaev first-fall witness — 2026-10-23

**Status:** machine-checked finite proof, pending independent semantic review and hosted current-head CI. This report makes no generic first-fall, solving-degree, ECDLP cost, or official hypothesis-state claim.

## Question and source

Can we exhibit the low-degree class whose existence was proved in the [finite filtration certificate](../../../formal/CryptoResearch/Semaev/BooleanParityFiltrationCertificate.lean)? The frozen sample is `n=4`, `n'=4`, draw index `1`, seed `32201`, `x_R=1`, basis `[9,3,2,12]`, over `F₂[X]/(X⁴+X+1)`. Its four component equations have canonical SHA-256 `89ab8e668c510572bbf9307f105b2eaf46858ad900f0b6b4a2fce8803e0ba6eb` in the [archived replay](../2026-10-22-semaev-first-fall-replay/evidence/draws.json). No new experiment was run; the same archived draw and corrected Boolean multiplication rule were used.

## Constructed certificate

The [Lean module](../../../formal/CryptoResearch/Semaev/ConcreteFirstFallWitness.lean) selects 23 of the 80 compatible degree-three rows with `comboMask = 1321682796735964` and XORs them. Its packed coefficient vector is `6277101735386703064921270320751746415339343215057222047510`; the present monomial masks are `1, 2, 4, 8, 9, 10, 12, 16, 18, 20, 32, 40, 48, 64, 65, 128, 144, 192`. Every present monomial has degree at most two.

The linear functional `c₈₀ + c₁₉₂`, where `cₘ` is the coefficient of monomial mask `m`, is zero on all 28 compatible degree-two rows. It is one on this vector. By linearity, the vector cannot be in their span. Lean proves membership in the degree-three row space by induction over the selected XORs, checks the degree bound, and proves the separator annihilates the degree-two span. Its theorem `concreteNewFall` states exactly that the vector belongs to `V₃ ∩ R≤2` and lies outside `V₂`.

The independent [source-binding checker](check_source_binding.py) compares the archived equations with Lean's literal list, regenerates the Boolean rows in source order, recomputes the XOR and separator, and checks that adding the witness raises the degree-two rank from 11 to 12. Its [machine-readable receipt](evidence/source-binding.json) lists every selected row and source hash. The archived set-product error remains a negative control: multiplication of the first equation by mask `1` retains three masks that cancel under F₂ parity.

The checker refuses optimized Python, where its validation assertions would be disabled. The ordinary run reproduced the committed receipt; `python3 -O` exited nonzero before reading source evidence.

A separate [finite replay](verify_independent.py) derives the four Boolean component equations anew from all 256 evaluations of `S₃(x₁,x₂,1)` in `F₂[X]/(X⁴+X+1)`, using a shift-and-reduce field multiplier and a Möbius transform. Its elimination starts at the lowest column, unlike the source-binding checker's highest-column pivots. It reproduces the degree-one, -two and -three ranks `1, 11, 53`, the low-degree intersection dimensions `1, 12`, and the same 23-row witness and two-coordinate separator. The [receipt](evidence/independent-replay.json) binds the archived draw and Lean source hashes. This is an independent implementation replay of one finite model, not an independent human review of the historical claim or a generic theorem.

![Finite row-space dimension chart](row-space.svg)

The [editable chart source](render.py) reads the binding receipt. These are exact finite dimensions, with no sampling uncertainty. The canonical archived-versus-corrected first-fall [draw chart](../2026-10-22-semaev-first-fall-replay/draws.svg) and performance dashboards need no data change: this certificate adds a witness for one already charted draw and measures no performance. The archived 70/10 and corrected 68/12 counts remain distinct.

## Validation and limits

The [proof receipt](evidence/concrete-proof.json) records the pinned Lean version, full workspace build, project theorem axiom audit, theorem axiom output, target verifier, and source hashes. The [formal target](../../../formal/targets/semaev-s3-concrete-first-fall-20261023.yaml) is additive; the historical target and result remain unchanged. This certificate refines an already proved finite existence theorem. It still needs independent semantic-fidelity review before claim wording changes. Generic `rankOn` correctness, generic symbolic descent, a reviewed additive correction of the historical uniform wording, and cryptanalytic cost inference remain open in the [problem record](../../../problems/semaev-degree-two-fall-nonzero-bridge.md).

## Current-main integration check

An isolated full-workspace copy of main `d513b75233e1eb58b24c753ff51675b83b284b44` was compared byte for byte with all 148 tracked formal files. Its pinned `lake build` completed 8,975 jobs, and the project axiom audit accepted 652 theorems using only standard axioms. Adding the exact PR theorem source, regenerating the root import, and repeating both commands completed 8,976 jobs and audited 661 theorems with the same axiom policy. The [integration receipt](evidence/current-main-integration.json) binds the main commit, all copied formal source hashes, the theorem SHA-256, generated root, commands and [raw logs](evidence/current-main-with-witness-build.log). This is an integration check; it does not provide independent semantic review of the 83 current target specs.
