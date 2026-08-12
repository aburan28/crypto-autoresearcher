# Mechanism screen — GOAL-SSI-001 BATCH-005

Task `TASK-20260725-517` · access date 2026-07-25  
Resolved model: `cursor-grok-4.5-high-fast` (`research-sol-max` unavailable; fallback authorized by `inference-amendment-TASK-20260725-517.yaml`)  
Disposition: **ADMIT_CANDIDATE_FOR_REVIEW** → `IDEA-20260725-003`

## 1. Target survivor and open problem

- **Survivor assumption:** SQIsign Fiat–Shamir signatures resting on secret
  endomorphism-ring knowledge and KLPT responses (`KN-TECH-028`, `KN-LIT-072`,
  `KN-LIT-073`), reported to reveal **no torsion images** under a secret
  isogeny.
- **Open problem:** `KN-OPEN-015` — when does published auxiliary structure
  collapse an isogeny/DL assumption? SQIsign is listed as a survivor; the
  residual is whether the *signature transcript itself* is a weaker but still
  fatal auxiliary channel.
- **Secondary (not selected):** `KN-OPEN-014` CSIDH quantum cost-convention pin
  (`KN-TECH-027`, `KN-LIT-071`) — deferred below.
- **Closed / forbidden reopen:** `IDEA-20260725-002` orientation Cl-cost
  (`DEC-20260725-005`, `EV-SSI-004`); SIDH torsion-image rediscovery as a
  positive novelty target (`KN-TECH-026`).

## 2. Frozen transcript / leakage model (mandatory before any embedding claim)

**Model name:** `SQI-FS-T0` (spine-minimal Fiat–Shamir transcript object).

Public inputs for static verification of one signature on message \(m\):

1. Public key \(\mathrm{pk}\) naming a supersingular curve \(E\) (or \(j(E)\)),
   with **no** published \(\mathrm{End}(E)\) and **no** images of a fixed
   torsion basis under a long-term secret isogeny.
2. Signature \(\sigma\) that, under the Fiat–Shamir transform of the SQIsign
   identification protocol as reported in `KN-LIT-072` / `KN-TECH-028`, parses
   into:
   - commitment objects \(C\) present in \(\sigma\);
   - challenge \(c = H(\mathrm{pk}, m, C)\);
   - response objects \(R\): encodings of **connecting isogenies** of
     **publicly recoverable degree** between **publicly named curves** arising
     from the commitment / challenge structure (KLPT-produced responses;
     `KN-LIT-073`).

**Explicitly excluded from `SQI-FS-T0` (not charged, not assumed):**

- Images \(\varphi(P),\varphi(Q)\) of a known torsion basis under a secret
  isogeny of known degree (SIDH auxiliary; `KN-TECH-025` / `KN-TECH-026`).
- Adaptive torsion-point oracles (GPST; `KN-LIT-076`).
- Free \(\mathrm{End}(E)\) or a free connecting ideal to a known-order curve.
- Any reopening of oriented Cl-vectorization / `IDEA-20260725-002`.
- Invented protocol fields beyond the spine-minimal objects above (version-specific
  bit layouts of SQIsign / SQIsign2D are **out of model** until cited into the
  knowledge spine).

No Kani / glue-and-split / higher-dimensional embedding claim is allowed until
a later derivation shows that objects *inside* `SQI-FS-T0` meet that attack's
necessary conditions — or names a distinct non-torsion pathway with charged cost.

## 3. Typed candidate mechanism

**KN-OPEN-015 sufficiency test of `SQI-FS-T0` against Kani-necessary conditions
and named non-torsion residual pathways.**

Mechanism sketch (proposal + falsification only):

1. Freeze `SQI-FS-T0` as the sole public leakage channel under test.
2. Compare `SQI-FS-T0` to the **necessary** inputs of `KN-TECH-026` (known
   degree **and** torsion action on a known basis). Expected spine-consistent
   outcome: torsion action is absent → Kani pathway fails closed.
3. Separately ask whether `SQI-FS-T0` still supplies a **named** non-torsion
   auxiliary (e.g., systems of known-degree connecting isogenies among named
   curves across one or many transcripts) that reduces End / path-finding below
   `KN-TECH-050` / End baselines under a charged cost convention — without
   inventing \(\sigma\) fields.
4. Emit a regime disposition (see §6). Cap: no break claim, no GOAL completion.

This converts the BATCH-001 deferred slogan
(“SQIsign transcript leakage → Kani-style embedding”) into a typed model with a
cheap closed-form gate.

## 4. Comparison to matched baselines / attack templates

| Comparator | Role under this candidate |
| --- | --- |
| `KN-TECH-026` Kani / glue-and-split | Necessary-condition check only; not a positive rediscovery target |
| `KN-LIT-077` Petit unbalanced isogeny | Check whether degree-known responses without torsion images instantiate Petit; else fail closed |
| `KN-TECH-050` classical path-finding / End baselines | Only if a named non-torsion residual claims a classical advantage |
| `KN-TECH-028` “reveals no torsion images” | Hypothesis under test: holds for `SQI-FS-T0`, or fails with typed counterexample |

Secondary `KN-OPEN-014` CSIDH quantum pin is **not** chosen: pinning
query/memory/circuit conventions for contested Kuperberg constants is a larger
setup than freezing `SQI-FS-T0` and running the sufficiency gate, and the
preferred lane under `DEC-20260725-005` / `batch.yaml` is SQIsign transcript
typing.

## 5. Novelty screen

- vs BATCH-001 deferred route: that exclusion demanded a precise Fiat–Shamir
  leakage model; `SQI-FS-T0` is that freeze.
- vs `KN-TECH-028` survivor slogan: spine asserts no torsion images; this
  candidate asks for a decision-relevant classification under an explicit
  transcript object, not a new slogan.
- vs `KN-TECH-026`: uses Kani only as a necessary-condition template; does not
  propose rediscovering SIDH torsion attacks.
- vs closed `IDEA-20260725-001` / `KN-TECH-050`: not a full-cost re-baseline.
- vs closed `IDEA-20260725-002`: not orientation / Cl-cost; `DEC-20260725-005`
  forbids reopen.
- vs `KN-OPEN-014`: quantum CSIDH sizing intentionally not selected this batch.

## 6. Full-cost boundary

**Charged (if any later classical residual is claimed):** parsing \(\sigma\);
algebraic work on publicly named curves and publicly known degrees; any End /
path-finding reduction cost compared under `KN-TECH-050` conventions.

**Not charged / forbidden:** torsion-image oracles; free \(\mathrm{End}(E)\);
uncharged exponential tables; quantum Kuperberg queries; invented SQIsign
version fields not present in the knowledge spine; orientation Cl-cost reopen.

**Cost convention name:** `sqi_fs_t0_aux_sufficiency_plus_kn_tech_050_if_classical_residual`

## 7. Cheapest falsification gate (derivation, zero curve compute)

Write a short derivation that:

1. Restates `SQI-FS-T0` using only `KN-TECH-028`, `KN-LIT-072`, `KN-LIT-073`,
   and `KN-OPEN-015` / `KN-TECH-026` necessary conditions;
2. Checks whether `SQI-FS-T0` supplies (degree **and** torsion action);
3. Checks whether Petit-style unbalanced improvement (`KN-LIT-077`) applies
   without torsion images under `SQI-FS-T0`;
4. Outputs exactly one of:
   - `T0_FAILS_KANI_AND_PETIT_NECESSARY_CONDITIONS`
   - `T0_SUPPLIES_NAMED_NON_TORSION_AUXILIARY`
   - `SPINE_INSUFFICIENT_TO_FREEZE_T0`

**Falsifies admission as a cryptanalytic mechanism** if the only honest outcome
is documentation already fully contained in `KN-TECH-028` with no decision
delta for `KN-OPEN-015` (Coordinator may then demote to residual note rather
than promote a structure-attack track).  
**Falsifies the Kani pathway** (expected) if torsion action is absent from
`SQI-FS-T0`.  
**Blocks embedding claims** if the derivation must invent protocol fields
(`SPINE_INSUFFICIENT_TO_FREEZE_T0`).

## 8. Interpretation limits

- Admission is a **typed novelty screen**, not a SQIsign break and not GOAL
  completion.
- Prefer `NO_ADMISSIBLE_NEXT_MECHANISM` over untyped “transcript leaks”
  slogans; this batch admits only because `SQI-FS-T0` is frozen first.
- Independence weakened: same-lineage fallback model
  (`cursor-grok-4.5-high-fast`); red-team must re-check typing and that no
  SIDH rediscovery or orientation reopen sneaks in.
- Toy-parameter speculation and version-specific SQIsign2D bit encodings are
  out of scope until added to the knowledge spine.
