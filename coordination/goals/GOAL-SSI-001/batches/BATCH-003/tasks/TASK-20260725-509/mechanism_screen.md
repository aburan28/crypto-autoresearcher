# Mechanism screen — GOAL-SSI-001 BATCH-003

Task `TASK-20260725-509` · access date 2026-07-25  
Resolved model: `cursor-grok-4.5-high-fast` (research-sol-max unavailable; fallback)  
Disposition: **ADMIT_CANDIDATE_FOR_REVIEW** → `IDEA-20260725-002`

## 1. Target survivor and open problem

- **Survivor assumption:** supersingular endomorphism-ring / isogeny path-finding
  underpinning CGL and SQIsign foundations (`KN-TECH-024`, `KN-TECH-028`),
  *without* published torsion images under a secret isogeny.
- **Open problem:** `KN-OPEN-013` — does extra structure (orientation, small-degree
  endomorphisms, special curves) admit faster attacks than the matched classical
  baselines?
- **Not targeted:** SIDH/SIKE torsion-image regime (closed); `RQ-ISO-001` Semaev
  neighbors; pure cost-model re-baseline (`IDEA-20260725-001`, closed by
  `DEC-20260725-003`).

## 2. Typed candidate mechanism

**Public effective orientation from a known small-degree non-scalar endomorphism.**

Public inputs: curves \(E_0, E_1\) supersingular; a non-scalar endomorphism
\(\alpha \in \mathrm{End}(E_0)\) of known degree \(d = \mathrm{poly}(\log p)\);
no torsion-point images under a secret isogeny; no full endomorphism ring of
\(E_1\).

Mechanism sketch:

1. Treat \(\mathbb{Z}[\alpha]\) as an effective imaginary-quadratic orientation of
   \(E_0\) (order of discriminant determined by the minimal polynomial of
   \(\alpha\)).
2. Assume the instance is in the oriented regime: \(E_1\) lies in the class-group
   orbit of \(E_0\) under ideals of that order (CSIDH-style oriented isogeny
   graph / volcano slice), or state failure if the orbit membership is not
   public.
3. Recover a connecting ideal / path by classical vectorization (MITM / BSGS) in
   the class group \(\mathrm{Cl}(\mathbb{Z}[\alpha])\), charging each class-group
   action evaluation as an isogeny-walk cost.
4. Compare the charged cost \(\tilde{O}(\sqrt{h})\) (with \(h = \#\mathrm{Cl}\))
   to `KN-TECH-050` matched baselines — not to memory-free MITM.

This is **not** "orientation is easier" as a slogan: the typed object is a
public \(\alpha\) of polynomial degree plus an explicit Cl-vectorization cost
model.

## 3. Comparison to KN-TECH-050 matched baselines

| Regime | Matched baseline (`KN-TECH-050`) | Oriented Cl-vectorization claim to test |
| --- | --- | --- |
| \(\mathbb{F}_{p^2}\) pure | claw-PCS \(\tilde{O}(p^{1/2})\) small memory; high-memory MITM \(\tilde{O}(p^{2/3+o(1)})\) | Material only if \(\sqrt{h} = o(p^{1/2})\) under the charged action model |
| \(\mathbb{F}_p\)-rational | Delfs–Galbraith \(\tilde{O}(p^{1/4})\) | Material only if \(\sqrt{h} = o(p^{1/4})\); CSIDH-like \(\Delta \sim -p\) typically fails this |

Secondary `KN-OPEN-014` CSIDH quantum pin is **not** chosen: contested concrete
Kuperberg constants have no cheaper decisive gate than this classical oriented
derivation under the campaign budget.

## 4. Novelty screen

- vs `KN-TECH-029` / `KN-TECH-050`: those fix *unoriented* baselines; they do not
  cost an effective-orientation → Cl-vectorization reduction.
- vs CSIDH (`KN-TECH-027`): CSIDH *is* the oriented group-action setting; the
  candidate is not a new CSIDH break. It asks whether a **path-finding /
  endomorphism-ring** instance that *publishes only a small-degree endomorphism*
  (not a CSIDH public key protocol) falls into a Cl-orbit attack that beats
  unoriented baselines — a `KN-OPEN-013` structure question, not `KN-OPEN-014`.
- vs KLPT / SQIsign trapdoor (`KN-TECH-028`, `KN-LIT-073`): KLPT assumes known
  connecting ideal / known End as trapdoor; this candidate assumes much less
  (one endomorphism on \(E_0\) only).
- vs Wesolowski equivalence (`KN-LIT-074`): full End ↔ path-finding; partial End
  is the residual gap this gate probes.
- vs SIDH breaks (`KN-TECH-026`): no torsion images; not Castryck–Decru / Robert.
- vs closed `IDEA-20260725-001`: not a cost-model hygiene batch.

## 5. Full-cost boundary

**Charged:** class-group action evaluations; MITM/BSGS tables in Cl under Wiener
full-cost if tables are large; isogeny walk steps; any preprocessing that builds
orientation data from \(\alpha\).

**Not charged / forbidden:** torsion-image oracles; free full \(\mathrm{End}(E_1)\);
quantum queries; SQIsign transcript leakage (separate deferred lane).

## 6. Cheapest falsification gate (derivation, zero curve compute)

Write a short derivation that:

1. Fixes the public input \((\alpha, E_0, E_1)\) and the orbit-membership
   assumption;
2. Reduces to Cl-vectorization with an explicit action-cost unit;
3. Under standard class-number heuristics (\(h \approx \sqrt{|\Delta|}\)) and at
   least two discriminant regimes (poly-bounded \(|\Delta|\) vs CSIDH-like
   \(\Delta \sim -p\)), compares \(\sqrt{h}\) to `KN-TECH-050` baselines;
4. Outputs one of: `MATERIAL_IN_SOME_REGIME` | `NEVER_BEATS_BASELINE` |
   `REDUCTION_REQUIRES_UNCHARGED_ORACLE_OR_FULL_END`.

**Falsifies admission** if (b) or (c) is forced for every honest orientation
regime, or if publishing \(\alpha\) is shown equivalent to already solving
path-finding at baseline cost.

## 7. Interpretation limits

- Admission is for a **typed novelty screen**, not a cryptanalytic break.
- No GOAL-SSI-001 completion claim.
- Independence of this producer is weakened (same-lineage fallback after API
  limit); red-team must re-check typing and baseline comparison.
- If the derivation shows oriented instances are already covered by CSIDH
  classical costs with no path-finding advantage, demote to documentation /
  residual under `KN-OPEN-013`, not a breakthrough track.
