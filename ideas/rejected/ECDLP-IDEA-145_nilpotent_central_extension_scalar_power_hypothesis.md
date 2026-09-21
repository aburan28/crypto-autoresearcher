# ECDLP-IDEA-145 — Nilpotent central-extension scalar power

## Status and claim labels

- Class: `mechanism`
- Risk band: `high-risk`
- Top lane: `high-risk`
- State: `merged_rejected_noncanonical_cyclic_section`
- Cohort: `20260717-h`
- Evidence scale: group-cohomology/literature audit only; no experiment ran
- Contract posture: retired `review_required` draft; unapproved; zero runs permitted
- Scale labels: every prospective finite measurement is `toy`; complexity claims are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valid cocycle, central coordinate, auxiliary point, or recovered toy scalar is not an ECDLP break.

## Falsifiable hypothesis

Lift `<P>` into a public two-step nilpotent/theta-group central extension with a canonical efficiently computable section. The central coordinate of the canonical lift of `Q=[x]P` follows a known nonlinear law. A scalar-valued return such as `binom(x,2)c` would expose `x` by direct polynomial solving; a group-valued return such as `[x^d]Z` would need all orientation maps required for Cheon-style recovery below rho without already knowing `x`.

## Mechanism-new operation

The proposed operation is **canonical nonlinear central coordinate from a cyclic subgroup lift**. A normalized two-cocycle would accumulate quadratically along repeated addition, while a public return map would expose the central component of the endpoint lift.

Semantic and group-cohomology review merges/rejects the current form. For trivial action, `H^2(C_N,A)=A/NA`; if multiplication by `N` is invertible on `A`, including every finite coprime-order center, the restriction splits. An alternating commutator is also trivial on a cyclic subgroup. For odd `N`, under `delta b(i,j)=b(i)+b(j)-b(i+j)`, a quadratic bilinear cocycle `c(i,j)=i*j*a` with `N*a=0` is the section/gauge coboundary of `b(i)=-binom(i,2)*a`; genuinely nontrivial cyclic classes are carry-like. This does not rule out `N`-primary nonsplit centers such as `C_(N^2)`. For those, reduction of a canonical readout to an order-`N` DLP or self-bilinear map is a construction-specific obligation, not a universal theorem, and it overlaps IDEA-003, IDEA-008, IDEA-015, IDEA-024, IDEA-025, and IDEA-069.

## Assumptions

1. Public `E/F_p`, prime-order `<P>` of order `N`, target `Q=[x]P`, and the extension/section are efficiently computable from point encodings.
2. The section is canonical and scalar blind; it is not defined by walking from `P` to `Q` or a precomputed lift table.
3. The central coordinate has a nonlinear scalar law, is publicly readable, and has an exact verification/return map whose scalar-valued or group-valued type is explicit.
4. Extension construction, coefficient fields, section evaluation, coordinate conversion, auxiliary-input density, Cheon recovery when applicable, ambiguity, and memory are charged.
5. Ordinary pairings, a split extension, a section chosen after `x`, and an order-`N` target-group DLP are controls.

## Semantic fingerprint

`prime_cyclic_E_subgroup | two_step_nilpotent_theta_extension | canonical_public_section | quadratic_cocycle_accumulation | readable_scalar_power_coordinate | Cheon_recovery`

Only a canonical efficient `N`-primary nonsplit section with a nonlinear readable return would be new. Section-dependent coboundaries, a direct center DLP, or a self-bilinear return are rejected duplicates only after the relevant construction-specific reduction is proved.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `P1474`, where a growing known-scalar CM orbit does not produce an invariant sparse deck or functional transition.
2. `ledger/FINDING-PF-IC-001.md` — imported `P1479`, where tested public low-dimensional features do not encode factor logs.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H664`, whose exact phase/character identities remain controls without a source/scalar generator.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1425-BOUNDED-PHASE-LIFT-NO-PROMOTION`, where bounded lifted phase coordinates fail exact membership.
5. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-NR-005`, whose restricted homomorphism model shows fiber multiplicity/known maps do not create original-group rank or descent.

## Closest primary literature

- Mumford, [On the equations defining abelian varieties I](https://doi.org/10.1007/BF01389737), develops theta groups/central extensions but does not supply the required canonical nonlinear cyclic section.
- Boneh and Silverberg, [Applications of Multilinear Forms to Cryptography](https://eprint.iacr.org/2002/080), explain strong constraints on geometric multilinear structures.
- Cheon and Lee, [A Note on Self-Bilinear Maps](https://doi.org/10.4134/BKMS.2009.46.2.303), analyze the extraordinary consequences of a usable self-bilinear channel.
- Cheon, [Discrete Logarithm Problems with Auxiliary Inputs](https://doi.org/10.1007/s00145-009-9047-0), gives recovery after suitable scalar-power auxiliary input; it does not construct that input from `Q`.

No checked source supplies the canonical section/return map. Novelty remains unverified outside the merged fingerprint.

## Complete factor-base-to-target-descent path

1. Freeze curve, subgroup, extension, center, cocycle, canonical section, coordinate normalization, and independent verifier.
2. Compute section lifts of `P`, known-log points, factor points, and targets directly from public encodings; verify the group law and nonlinear coordinate formula.
3. For known-log relation targets, derive exact scalar/source information, collect rank `B`, and solve/verify factor logs if the channel is relation based.
4. For `Q` or fresh masks `Q+[t]P`, read the nonlinear central coordinate. If it is scalar valued, solve and verify the resulting polynomial directly. If it is group valued, construct the exact auxiliary point, verify the divisor/orientation hypotheses, run the fully charged Cheon recovery, remove masks, and enumerate ambiguity.
5. Accept only `[x]P=Q`; report extension/section construction, auxiliary-input density, recovery, output, time, and memory against rho/BSGS.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time and constant state; BSGS costs `N^(1/2+o(1))` time/memory. Let extension/section setup be `N^a,N^a_m`; section evaluation/central-readout time and working memory `N^q,N^q_m`; useful auxiliary-input inverse density `N^delta`; Cheon recovery `N^chi` time and `N^chi_m` memory; ambiguity `u`; and any factor-log linear algebra `N^ell,N^ell_m`. Then

`lambda=max(a,q+delta,chi+u,ell,beta)`

`mu=max(a_m,q_m,chi_m,ell_m,u)`.

Thus `lambda` is the complete time exponent and `mu` is the complete peak-memory exponent.
Cheon's `d | N-1` case is admitted only when `Z`, `[x]Z`, and `[x^d]Z` are supplied in the same order-`N` group with the required orientation maps. Then `d=N^kappa` gives `chi=max((1-kappa)/2,kappa/2)` before conversion/readout costs; fixed `d=2` leaves `chi=1/2`. A quadratic center output alone does not supply `[x]Z`. A scalar-valued quadratic return is solved directly with at most two candidates and is therefore not a Cheon claim. Center orientation, coefficient representation, section tables, retries, and verification are charged. Toy cocycle identities are model-bound.

## Likely fatal obstruction

For trivial action, a coprime-center extension splits because `H^2(C_N,A)=A/NA=0`, and alternating commutators vanish on the cyclic subgroup. For odd `N`, the proposed quadratic bilinear term is gauge removable. `N`-primary nonsplit centers remain mathematically possible, but the proposal supplies no canonical endpoint lift or efficient readout. A scalar return would already solve a low-degree equation directly; a group return with fixed `d` gives no Cheon exponent gain, while useful growing `d` requires the missing same-group/orientation maps and a fully charged conversion.

## Proof track

Construct an explicit `N`-primary nonsplit extension and canonical section, prove gauge independence and a nonlinear law, classify the return as scalar or group valued, give its conversion/verification maps, and derive complete `lambda,mu<=0.45` without assuming an order-`N` center DLP.

## Disproof track

Prove the cyclic restriction splits, exhibit a gauge eliminating the proposed quadratic coordinate, show that scalar readout already gives direct polynomial recovery rather than the claimed auxiliary-input lane, or give a construction-specific reduction of group readout to an order-`N` DLP/self-bilinear map. Any one closes its corresponding stated branch; none is asserted as a universal no-go for all `N`-primary extensions.

## Positive and negative controls

- **Positive control:** finite Heisenberg/nilpotent groups with supplied coordinates and canonical matrix sections.
- **Positive control:** Cheon instances with externally supplied valid auxiliary inputs, clearly outside the construction claim.
- **Negative control:** split extensions, cohomologous sections, cyclic subgroups with trivial alternating pairing, and randomized gauges.
- **Negative control:** centers of order coprime to `N` versus centers with `N`-torsion and separately charged center DLPs.
- **End-to-end control:** rho/BSGS and independent `[x]P=Q` verification.

## Quantitative promotion and falsification gates

The current mechanism is merged/rejected. A new ID requires an independently verified canonical `N`-primary nonsplit section, an explicit scalar/group return type, all orientation/conversion maps, and `lambda,mu<=0.45`. A gauge-dependent coordinate, split cyclic restriction, construction-specific center-DLP reduction, supplied auxiliary input, fixed-degree `chi=1/2`, or complete exponent at least `0.5` falsifies its stated branch.

## Artifact plan

- Cyclic-extension audit: `ideas/artifacts/ECDLP-IDEA-145/cyclic_section_no_go.md`
- Prospective canonical-section theorem: `ideas/artifacts/ECDLP-IDEA-145/canonical_nonlinear_section.md`
- Frozen group controls: `ideas/artifacts/ECDLP-IDEA-145/fixtures.json`
- Independent auxiliary-input verifier: `ideas/artifacts/ECDLP-IDEA-145/verify_auxiliary.py`
- Complete cost receipt: `ideas/artifacts/ECDLP-IDEA-145/cost_analysis.md`
- Retired review-required contract: `ideas/rejected/contracts/ECDLP-EXP-CONTRACT-145_nilpotent_central_extension_scalar_power_preflight.yaml`

No successor artifact or run exists; only the retired `review_required` contract exists.

## Interpretation boundary

This is preserved merged/rejected, novelty-unverified evidence. Any finite examples are toy; costs are heuristic/model-bound. A cocycle identity or externally supplied auxiliary point is not a generic ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-145/cyclic_section_no_go.md` computing the restricted cohomology class, all public gauge changes, and the center-readout cost for the frozen cyclic subgroup model.
