# ECDLP-IDEA-188 — Kashiwara crystal-string source extraction

## Status and claim labels

- Class: `representation`
- Risk band: `high_risk`
- Top lane: `none`
- State: `merged_rejected_crystal_colors_recreate_source_labels`
- Cohort: `20260718-d`
- Evidence scale: checked primary literature and semantic preflight only; no experiment ran
- Contract posture: rejected at the public crystal compiler and source-return gates; no contract or run is authorized
- Scale labels: every future finite check is `toy`; all projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valid crystal action, string parameter, relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

A target-uniform, scalar-blind compiler sends an elliptic endpoint and the frozen factor base into a finite tensor-product crystal whose Kashiwara string parameters canonically expose every exact ordered signed factor-base source of that endpoint. Applying the same compiler to known-log relation endpoints and fresh masked targets would then yield complete factor logs and blind target descent with time and memory exponents below rho and BSGS.

## Mechanism-new operation

The proposed operation is **elliptic-endpoint-to-crystal compilation followed by Kashiwara raising/lowering and canonical string-source extraction**. It would be mechanism-new only if the crystal, its colors, tensor order, highest-weight component, and endpoint-to-string inverse were computed from public curve coordinates without scalar labels or a source table. A crystal whose colored arrows are assigned from the factor points, a supplied tensor word, exhaustive traversal of all `B^m` words, or a generic solver is a control.

Operation-level review rejects the present form: Kashiwara colors and tensor positions identify oriented generators, so making them correspond exactly to elliptic factor points installs the missing source identities in the representation. Removing those colors leaves string data that does not distinguish source tuples. This is a representation change around the occupied direct-label and full-rank boundaries, not a demonstrated new endpoint-to-source operation.

## Assumptions

1. Public `E,P,N,Q,F,B=N^beta,m`, a crystal family, tensor convention, masks, and an independent verifier are frozen.
2. The endpoint compiler uses only public coordinates and returns a crystal object of size and construction cost below the generic bound.
3. Crystal colors, orientations, and tensor positions are not factor-point identifiers, scalar labels, or a disguised `B^m` source deck.
4. A canonical string parameter returns every exact signed source tuple, including repeats, infinity, singular cases, and all declared strata.
5. Compilation, crystal traversal, output, relation density, rank, factor logs, masked descent, ambiguity, verification, time, and peak memory are charged.

## Semantic fingerprint

`public_elliptic_endpoint_to_tensor_crystal | Kashiwara_operators | canonical_string_parameter | exact_signed_factor_sources | blind_masked_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-NR-1410-DIRECT-LABEL-NO-PROMOTION`, the direct scalar-orientation label boundary.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, the full-rank representation boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1422-ADDITIVE-CHARACTER-NO-PROMOTION`, the character-label control.
4. `inputs/ledger_inventory.json` — imported `P1479`, the nearest representation-to-source transition proposal.
5. `inputs/ledger_inventory.json` — imported `P1434`, the missing public algebraic source-fiber generator.

## Closest primary literature

- Kashiwara, [Global crystal bases of quantum groups](https://doi.org/10.1215/S0012-7094-93-06920-7), develops global crystal bases and colored Kashiwara operators, but not an elliptic endpoint compiler.
- Kashiwara, [On crystal bases of the q-analogue of universal enveloping algebras](https://doi.org/10.1215/S0012-7094-91-06321-0), defines crystal operators and tensor rules for an already specified representation rather than an elliptic endpoint.

Neither checked primary source gives a target-uniform finite-field map from one elliptic endpoint to all factor-point leaves, and no novelty claim beyond this unverified mechanism is made.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,Q,F,B=N^beta,m`, the factor base, crystal type, tensor rule, color convention, masks, exceptional strata, and verifier.
2. Construct from public coordinates a scalar-blind endpoint compiler and prove that its output represents exactly the complete signed factor-base source fiber.
3. For known-log endpoints `R_j=[r_j]P`, compute the crystal object, apply Kashiwara operators, and enumerate every canonical string/source output without source advice.
4. Decode strings to exact signed factor points; verify every sum and preserve repeats, cancellations, infinity, collisions, misses, multiplicities, and output volume.
5. Collect at least `B+sigma` verified relation rows of rank `B`, solve all factor-base logarithms, and independently verify each recovered log.
6. Apply the identical frozen compiler and string extraction to fresh masked targets `Q+[t]P`, with `t` chosen independently after setup.
7. Substitute verified factor logs, remove each mask, retain every string/source ambiguity candidate, and accept only `x` satisfying `[x]P=Q`.
8. Charge crystal construction, colors, traversal, source output, failed endpoints, rank, factor logs, target descent, verification, total time, and peak memory.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` expected time with constant-sized state; BSGS costs `N^(1/2+o(1))` time and memory. Let crystal compilation have time and memory exponents `a,a_m`; let reciprocal relation and masked-target success densities be `N^delta,N^delta_t`; let one string extraction query cost `N^q` time and `N^q_m` memory; let exact source output and residual target ambiguity have exponents `o,u`; and let factor-log linear algebra have exponents `ell,ell_m`. The complete exponents are

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every color dictionary, tensor word, crystal node, branch, decoded source, failure, and verification is included; hiding a `B^m` colored graph makes `a`, `q`, or `o` pay for it.

## Likely fatal obstruction

Crystal operators require a color and orientation, while an exact elliptic source return needs those colors to identify the signed factor points and tensor slots. Assigning one color per factor point is a source dictionary; assigning fewer colors merges distinct tuples; constructing the correct colored path from the endpoint is itself the missing source oracle. Canonical string data therefore either forgets the leaves or recreates `B^m` labeled source structure.

## Proof track

Give an explicit coordinate-only endpoint compiler, prove crystal axioms and all-strata biconditionality between string outputs and exact signed source tuples, prove that no color or tensor position encodes a factor identity, and derive complete blind-descent exponents `lambda,mu<=0.45`.

## Disproof track

Exhibit two source-distinct tuples with the same uncolored string data, prove that separating colors determine factor identities, reduce compiler construction to source enumeration or DLP, find an omitted stratum, or derive `max(lambda,mu)>=0.50` after charging the colored graph and output.

## Positive and negative controls

- Positive control: a published finite highest-weight crystal with supplied tensor factors and known string parameters.
- Positive control: exhaustive toy elliptic source fibers compiled from deliberately supplied source tuples, used only to test decoding.
- Negative control: erase or permute point colors and tensor positions, then measure collisions between source-distinct tuples.
- Negative control: direct point labels, explicit `B^m` word enumeration, generic Gröbner/resultant solving, rho, BSGS, known-log endpoints, and fresh blind masked targets.

## Quantitative promotion and falsification gates

This record remains merged/rejected. A distinct successor requires a public scalar-blind compiler, 100% source and multiplicity recall on preregistered toy strata, zero false tuples, invariance under frozen crystal equivalences, zero source/color advice, and formal `lambda,mu<=0.45`. If `0.45<max(lambda,mu)<0.50`, the result is inconclusive; any identity-bearing color table, lost source, false tuple, nonuniform compiler, or `max(lambda,mu)>=0.50` falsifies the scoped successor.

## Artifact plan

- Prospective compiler theorem: `ideas/artifacts/ECDLP-IDEA-188/crystal_endpoint_compiler_theorem.md`
- Prospective color/source separation proof: `ideas/artifacts/ECDLP-IDEA-188/crystal_color_source_separation.md`
- Prospective fixtures and independent verifier: `ideas/artifacts/ECDLP-IDEA-188/fixtures.json` and `ideas/artifacts/ECDLP-IDEA-188/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-188/cost_analysis.md`

All paths are prospective. No artifact root, contract, experiment, or run exists or is authorized.

## Interpretation boundary

This is merged/rejected, novelty-unverified representation evidence. Any finite check would be toy, and the complexity forecast is heuristic and model-bound. Crystal correctness, a valid string, or a relation is neither a generic ECDLP improvement nor a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-188/crystal_color_source_separation.md` proving whether any target-uniform string parameter can distinguish exact factor-point leaves without assigning identity-bearing colors or enumerating the source fiber.
