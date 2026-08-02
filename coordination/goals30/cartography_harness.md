# Cartography — Harness Capabilities & Evidence Rules (2026-07-23)

## What the harness measures today (harness/*.py, pure Python + sympy/pyyaml, no Sage)
- toycurve.py: deterministic short-Weierstrass curves over prime fields, 4–~32 bits, exact point counting, prime-order subgroup, seeded ECDLPInstance; also the independent certificate verifier.
- rho.py: Pollard rho (Teske r-adding walk, 32 branches, Floyd cycle detection); reports group_operations + iterations; self-checks k*P==Q; budget-limited.
- semaev.py: S_2/S_3 explicit, S_4 via resultant; measure_s3_decomposition builds ideal <S_3, fV(x1), fV(x2)> over F_p and times sympy grevlex Gröbner basis. Metrics: groebner_seconds, basis_size, max_degree PROXY (NOT d_reg), is_trivial_ideal, decomposition_found.
- runner.py: immutable run dirs (FileExistsError on rewrite), manifest.yaml v2 with model-resolution block, command/env/stdout/stderr/raw-result, git commit + dirty state, wall/CPU/peak-RSS; certificates re-verified by independent code; statuses completed_valid|completed_invalid|cancelled_by_budget.
- run.py: hard-coded EXP-SEMAEV-001 (8/10/12-bit, factor base 14, seeds 1–2, 60s/run, 2GB cap).
- 35 experiments/EXP-* dirs carry one-off Sage scripts (not reusable modules). EXP-DREG-003 commissioned but empty.

## Record formats & validators
- templates/research-records.md schemas: research_goal, research_question, hypothesis, experiment, evidence (claim_tier toy|medium|crypto, proof_status), claim (reproduced/partially/not/not_attempted/open/invalidated), attention_contract + resource_estimate.stages (queue v3), run, correction (append-only), coordinator_decision (knowledge_promotion block), handoff, archive receipt.
- tools/: validate_ledger.py (ID/xref/manifest checks; baseline grandfathering), check_run_immutability.py (CI gate), autoresearch_focus.py (≤3 active experiments, stage budgets, claim/run consistency), research_dispatch.py (Git-verified archives), build_knowledge_index.py. Resolution receipts are produced by `orchestration/adapter/resolver.py` (`python -m orchestration.adapter doctor`), not by tools/ — the parallel tools/model_policy.py implementation was removed once its catalog schema stopped matching the vendor-free model-policies.yaml.
- tests/test_harness.py: 14 tests (curve law, determinism, rho 6–14 bits, S_3 identity, tamper detection, immutability).
- knowledge/: 41 entries (KN-LIT-001..025, KN-TECH-001..010, KN-OPEN-001..006); knowledge/findings/ EMPTY (no KN-FIND yet).

## Capability gaps (what new goals may need to commission)
1. True degree-of-regularity measurement (F4/F5 backend) — proxy cannot test KN-OPEN-002.
2. measure_sm_decomposition for m=3,4 with factor-base ideal systems (scaling studies).
3. Generalized EXP runner (parameterized experiment registration, not hard-coded).
4. End-to-end cost model converting Gröbner/LA cost into rho-comparable group-op equivalents; sparse/structured LA benchmark module (KN-OPEN-006).
5. Sage environment capture in manifests (sage_version currently null).
6. 40–64-bit instance ladder (naive O(p) counting caps at ~32 bits; need Schoof-lite or curated tables — still toy tier).

## Evidence rules every goal must respect
- Immutability: run dirs never edited; corrections append CORR-* records; defective runs superseded by new RUN ids.
- Certificate discipline: every claimed solve/relation carries independently verified certificate or run = invalid_measurement.
- Claim tiers: claim_tier never exceeds run parameters; toy-field results motivate scaling studies, never P-256 claims (AGENTS.md rule 7).
- Controls: matched rho baseline required; incomparable op types never equated without a cost model; trivial-ideal control distinguishes "no decomposition" from cheap solve.
- Negative semantics: negatives close only exact tested scope; timeouts ≠ evidence against math; report censored/invalid runs; predefined primary metric; distributions not best-runs.
- Archival: snapshot commit before review; ledger commit before status transition; Git-verified receipts.

## Open frontier (KN-OPEN-001..006)
001 prime-field IC vs rho; 002 Gröbner solving-degree growth; 003 representation/symmetry cost reduction; 004 BKK/mixed-volume vs dense resultants, Newton saturation; 005 non-generic representations vs GGM birthday bound; 006 structured (low-displacement-rank) relation matrices beating generic sparse LA net of relation-probability penalty.

## Harness state after 2026-07-23 run
- venv at .venv/ with sympy 1.14, pyyaml, pytest (harness tests 14/14 pass; tools tests have pre-existing failures unrelated to harness).
- EXP-SEMAEV-001 re-run with fresh seeds 3–4 at 8/10/12/14 bits: 16 new immutable runs (RUN-SEMAEV-{rho,gb}-b{8,10,12,14}-s{3,4}). rho solved everywhere (group ops 6–72 at these toy sizes); gb found a verified decomposition only at b8-s3 (trivial ideal = no decomposition elsewhere, as expected for random targets over a small factor base).
