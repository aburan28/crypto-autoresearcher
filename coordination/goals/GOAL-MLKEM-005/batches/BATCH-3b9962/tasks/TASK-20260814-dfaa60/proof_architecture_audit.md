# Proof-architecture audit — TASK-20260814-dfaa60

Per `docs/inventor-protocol.md` section 8 (`KN-TECH-080`) and
`agents/coordinator.md`'s own "Proof-oriented dispatch gate": before
approving implementation or expensive experiments for a proof-oriented
proposal, the Coordinator fills and checks a `proof_search_map`. Both source
ideas (`IDEA-20260805-3d71ca`, `IDEA-20260814-8f8f45`) already carry their
own, independently authored `proof_search_map` fields. **This audit verifies
those maps against the actual frozen protocol drafted in this task
(`prereg_draft.md`, `experiment_spec_draft.yaml`), not merely against the
source ideas' own text** — that is the distinction the task card draws
("a head start, not a substitute"), and section 3 below is exactly the place
this drafting task found a divergence worth stopping on rather than papering
over.

This is a falsification aid, not a new claim tier (`KN-TECH-080`, "Mandatory
cheap audits"). Passing every audit below asserts nothing beyond what
AGENTS.md rules 4 and 6 already allow; a failed audit is frequently the
useful result, and section 3 is exactly such a case — not a rejection of the
protocol, but a scoped, disclosed amendment to one control.

---

## 1. Exact bottleneck and baseline reproduction

### C1 (from `IDEA-20260805-3d71ca`)

**Bottleneck, verified against the frozen protocol.** The factor `1/p(beta)`
in the single-target primal-BDD cost `T = T_BKZ(beta)/p(beta)`. Removing it
— replacing repetition-by-re-randomisation with selection-over-M-targets —
is the entire claimed gain; every other term is unchanged. This is preserved
unmodified in `hypothesis_draft.yaml`'s own `proof_search_map.bottleneck`
and in `prereg_draft.md` sections 0 and 3.

**Baseline embedding.** `M = 1` reproduces the standard single-target primal
BDD exactly (selection is vacuous, best-of-1 equals typical). **Verified as
an EXACT parameter slice, not a similar-looking curve**: the frozen protocol
(`prereg_draft.md` section 3.1 point 4; `experiment_spec_draft.yaml`
`CTRL-M1-SINGLE-TARGET-BASELINE`) requires the measured decode-success rate
at `M = 1` to equal the pinned estimator's own `primal_bdd` amplification
`p(beta)` within the sampling interval, checked BEFORE the multi-target arm
is read — this is a frozen regression fixture, not merely stated as one.
**Verdict: passes, unmodified from the source idea.**

### C2 (from `IDEA-20260814-8f8f45`)

**Bottleneck.** Whether the continuous Beta extreme-value law C1 itself
needs for its left-tail description remains valid at the large-`M` end of
the reachable range, or breaks down against a hard combinatorial floor
before that end. Preserved unmodified.

**Baseline embedding.** `M = 1` degenerates the running-minimum trajectory
to a single point with no order-statistic content, correctly excluded from
any decay-rate fit as a degenerate case (not a data point) —
`hypothesis_draft.yaml`'s own `baseline_embedding.parameter_slice`,
transcribed verbatim. The reproduction check — the trajectory computation
run on NULL-2 (Gaussian, continuous) must show NO deceleration and NO
brute-force floor — is preserved as `prereg_draft.md` section 3.2 item 1 and
is REQUIRED to run FIRST, before either conjunct's real-arm data is read.
**Verdict: passes, unmodified from the source idea.**

---

## 2. Observation-collision search

### C1

**Observable.** `rho(t) = ||pi_{d-beta}(t~)|| / (sigma sqrt(beta))`.
**Collision, deliberately sought (not assumed away):** a target with a
LARGE error vector whose projection happens to be small, and a target with
a SMALL error vector whose projection is large — both exist by construction,
because the projection is a random beta-subspace cut. `rho` does NOT
identify "this target has a short error"; the additional condition
separating decodability from raw error size is that decodability depends on
the PROJECTION and not the full norm, which is exactly why `rho` and not
`||e||` is the correct observable. This audit finds no gap: the collision is
explicitly named, its resolution is explicitly stated (decodability tracks
the projection, not the norm), and the frozen protocol requires the
collision to be exhibited in the run record (`prereg_draft.md` section 4.1,
the variance decomposition and the `rho`-vs-success correlation), not
assumed away. **Verdict: passes, unmodified.**

### C2

**Observable.** The pair (measured decay-rate deceleration, exact `r_min(B)`
versus its Beta-law prediction). **Collision, deliberately sought:** a floor
detected in BOTH the real-CBD arm and the NULL-2 (Gaussian) arm would be a
collision on the discreteness explanation — it would instead implicate the
BASIS, not the error's own finite support, since a continuous error cannot
have a combinatorial floor by construction. **This audit confirms the
frozen protocol preserves the required response to that collision exactly**:
`prereg_draft.md` section 4.2 defines `C2-COLLISION` as its own adjudication
state, distinct from and never merged into `C2-FLOOR-CONFIRMED`, and section
4.3's termination taxonomy forces at least `T-FLOOR-MIXED` whenever any
`C2-COLLISION` is present, "never absorbed into CONFIRMED or ABSENT." This
is a genuine strengthening this drafting task verified is carried through to
the aggregate level, not merely the per-cell level, where the source idea's
own text left the aggregate handling implicit. **Verdict: passes, and the
frozen protocol closes a gap the source idea left implicit (aggregate-level
collision handling).**

---

## 3. Quantifier order — AND the NULL-3 divergence found here

### C1

`FOR ALL` FIPS 203 parameter sets `P` and all `M`, `THERE EXISTS beta(M)`
such that `FOR A RANDOM` key and a random set of `M` ciphertexts, `WITH
PROBABILITY >= 1/2` at least one target decodes at block size `beta(M)`.
The witness `beta(M)` depends on `M` and the parameter set but NOT on the
individual key or on any particular ciphertext. **This drafting task's own
check**: the frozen protocol's `>= 8` independent `(key, basis)` draws exist
precisely to test whether `beta(M)` is genuinely key-independent (H3's own
between-basis variance decomposition, `prereg_draft.md` section 4.1) —
consistent with the source idea's own reviewer challenge ("If a reviewer can
show `beta(M)` must depend on the key, the uniform claim fails"). **Verdict:
the quantifier order is preserved and the protocol's own multi-draw design
is the correct instrument to test it — passes.**

### C2

`FOR` the specific `(n, beta, d)` cells tested, `EXISTS` a measured
deceleration statistic and an exact `r_min(B)` at the toy sub-cell. No
uniform claim over all ML-KEM parameter sets. **Passes**, unmodified.

### 3.1 THE DIVERGENCE THIS AUDIT FOUND

`IDEA-20260805-3d71ca`'s own `proof_search_map.method_ceiling.nearby_object_control`
names NULL-3 — "fresh key and fresh basis per target" — as the control
whose FAILURE (a reported gain in the ephemeral arm) would mean "the
experimental pipeline has not identified the load-bearing structure and is
measuring its own harness." Read together with `3d71ca`'s own `minimal_test`
control text, this control is specified at the SAME `M` as the main arm —
i.e. literally, a fresh BKZ reduction for EACH of up to `2^20`-`2^22`
targets.

**This is not a quantifier-order defect in the mathematical claim.** The
`FOR ALL ... EXISTS ... FOR A RANDOM ...` structure above is unaffected by
how many ephemeral draws are actually measured; the control's PURPOSE (rule
out that the effect is a harness artifact of basis reuse) does not require
matching `M` exactly, only enough ephemeral draws to detect a gain of the
same ORDER as the real arm's own claimed effect. **What this audit found is
a resource-feasibility defect in the control's literal specification**: at
`M = 2^20`, `2^20` independent BKZ reductions for the null arm alone would
cost, even at a wildly optimistic 10 seconds per reduction,
`2^20 x 10 s = 10,485,760` s, roughly `2,913` CPU-hours (`~0.33` CPU-years
— CORRECTED FROM AN EARLIER DRAFT OF THIS AUDIT, WHICH STATED `2.9`
CPU-years, an ~8.7x arithmetic error in the unit conversion). Even
corrected, this is roughly a `15x` overage against the main arm's own
`~192`-CPU-hour worst-case ceiling for the ENTIRE main-arm grid
(`prereg_draft.md` section 6.2, prior to that section's own NULL-3 budget
correction) — well beyond what this protocol's own budget could absorb for
one control alone, even though the qualitative conclusion (the literal
control is infeasible) is unaffected by the arithmetic correction.

**Method-ceiling consequence, stated plainly.** The nearby-object control's
strongest certifiable claim, AS LITERALLY SPECIFIED, is not attainable
within any defensible budget. This drafting task's response
(`prereg_draft.md` section 3.4; `experiment_spec_draft.yaml`
`CTRL-NULL-3-EPHEMERAL-SCOPED`) is to SCOPE the control to
`M_null3 = 64` independent single-target ephemeral draws per cleared cell —
enough to bound any best-of-`M_null3` selection gain by `log2(64) = 6` bits
absolutely, and to detect a gain of the same order as the real arm's own
`>= 5`-bit materiality gate — while disclosing explicitly, in both the
hypothesis record's own `interpretation_limits` and the prereg's own section
3.4, that this WEAKENS (does not eliminate) the control's power at the FULL
tested `M`. A reviewer is explicitly invited to require a larger `M_null3`
before approval; this draft does not pre-empt that judgment, only names the
gap and proposes a bounded, defensible interim value rather than leaving the
control unspecified or silently running it at a trivially small, uninformative
scale.

**Why this is reported here rather than silently fixed.** The task card
(`task_card.md` "If ... you find a genuine reason this conversion is NOT yet
ready to freeze ... say so plainly") explicitly asks for exactly this kind
of finding. A control specified at an infeasible scale, if not caught, would
either (a) silently fail to run at all (a worse outcome — an unreported gap
in the frozen protocol), or (b) be quietly run at some ad hoc reduced scale
without the reduction being argued or disclosed (a worse outcome still — an
undisclosed weakening of a nearby-object control, which is precisely the
kind of gap `docs/inventor-protocol.md` section 3 exists to catch:
"controls before belief").

---

## 4. Method ceiling and nearby-object control

### C1

**Strongest certifiable claim.** At most a saving of `log2(1/p*)` bits,
where `p*` is the single-target-optimum success probability; cannot lower
MLWE's exponent, cannot recover `s`, and cannot help when `M = 1`. Preserved
unmodified in `hypothesis_draft.yaml`.

**Nearby-object control.** The ephemeral-key deployment (§3 above) — SCOPED
per section 3.1's finding, with the scoping disclosed rather than silent.
**This is the one place this audit's verification diverges from what
`3d71ca` assumed, and it is fully accounted for above.**

### C2

**Strongest certifiable claim.** At most a quantified floor `r_min(B)` at
TOY dimension, exactly, plus a statistical deceleration reading at the
cells actually reached; cannot certify the floor's value at ML-KEM
dimension (`d ~ 1000+`), where exhaustive search is infeasible by
construction. Preserved unmodified, and explicitly stated in
`hypothesis_draft.yaml`'s own `interpretation_limits`.

**Nearby-object control.** Any CONTINUOUS error law of matched variance
(the same NULL-2 control C1 uses) — has no finite alphabet and so cannot
exhibit a combinatorial floor by construction; REQUIRED to pass (show no
floor) before any real-CBD floor finding is reportable. **This audit finds
no feasibility defect here** — NULL-2 reuses the SAME basis-generation
infrastructure as the real arm (it changes only the error-sampling step,
not the reduction), so it costs no more than the main arm itself and needs
no scoping. **Verdict: passes, unmodified.**

---

## 5. Constructive transforms selected

Both source ideas name their transforms (`telescoping_potential` and
`baseline_as_boundary_lift` for C1; `observable_fiber` for C2), each with a
`proposed_object` and `predicted_gain`. This audit confirms all three
transforms are consistent with the audits above (no transform depends on
the NULL-3 divergence found in section 3; the telescoping-potential and
baseline-as-boundary-lift transforms for C1 concern the `M=1` boundary and
the free-repetition mechanism, both unaffected by how the ephemeral CONTROL
is scoped) and carries them into `hypothesis_draft.yaml`'s own
`proof_search_map.constructive_transforms` without modification. No
proposal is required to use every transform (`KN-TECH-080`); none of the
other five transform cards (baseline-as-boundary lift beyond what is used,
stronger-compositional-invariant, telescoping-potential beyond what is used,
specialize-measure-pack, representation/reduction chain) applies to either
conjunct beyond what is already selected, and this is recorded as such
rather than silently omitted.

---

## 6. `IDEA-20260814-137f68` (the optional GSA-fidelity covariate) — audited briefly

`137f68`'s own `proof_search_map` states its `nearby_object_control` is
`H-MLKEM-11aabf`'s own object (a closed-form estimator readout with no real
GSO), where "hkz" is undefined — explicitly inapplicable there, and not
proposed as an extension of `H-MLKEM-11aabf`. This is consistent with the
frozen protocol admitting `137f68` only as a diagnostic layered onto C1/C2's
own real-GSO byproduct data (`prereg_draft.md` section 3.3), never as an
extension of the estimator-only hypothesis. **No divergence found; this
covariate's own map is verified consistent with the frozen protocol as
drafted.**

---

## 7. Summary

| audit | C1 | C2 | 137f68 (optional) |
|---|---|---|---|
| baseline reproduction | passes, unmodified | passes, unmodified | n/a (diagnostic, no baseline claim) |
| observation collision | passes, unmodified | passes; frozen protocol closes an aggregate-level gap the source idea left implicit | n/a |
| quantifier order | passes, unmodified | passes, unmodified | passes, unmodified |
| method ceiling / nearby-object | **DIVERGENCE FOUND**: NULL-3 as literally specified is computationally intractable at the main arm's own M; scoped to M_null3 = 64, disclosed, not silently fixed | passes, unmodified | passes, unmodified |

**Overall verdict.** Three of four audits pass unmodified for both
conjuncts; the fourth surfaces one genuine, disclosed scoping amendment
(NULL-3) that this task recommends the reviewing Coordinator either accept
as drafted or require a larger `M_null3` before approval — either way, a
decision to be made explicitly at review, not defaulted. No audit finding
here blocks freezing the protocol; per `KN-TECH-080`, "a failed audit is
frequently the useful result," and this one produced a bounded, defensible,
disclosed fix rather than an obstruction to the whole protocol.
