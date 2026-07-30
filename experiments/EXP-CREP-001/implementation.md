# EXP-CREP-001 implementation note

Executor implementation of the frozen contract `specification.yaml` (status
approved, frozen: true). Nothing in the specification was modified. This file
describes only the implementation approach and recorded interpretation
choices; it is not a result.

## File map (all under `experiments/EXP-CREP-001/`)

- `instances/generate_instances.py` — deterministic generator of the 12
  recorded symbolic labelled-deck instances (`INST-<B>-<STRATUM>.json`, B in
  {2,3} x six strata) with embedded mutated twins. No randomness (frozen
  seed policy: `seeds: []`).
- `verifier/package_schema.json` — normative package schema document.
- `verifier/check_representation.py` — frozen machine verifier (predicates
  V1–V6, dedup control, toy execution engine `crep-toy-v1`). Stdlib only.
- `packages/build_packages.py` — deterministic builder of the 8 route
  representation packages and the 2 calibration fixtures
  (`packages/<ID>/package.json`). Packages are static typed documents; all
  semantics live in the verifier.
- `driver/run_crep.py` — phase driver (one phase per planned run).
- `driver/launch_run.py` — supervised launcher: hard per-run wall-clock cap
  (1800 s, kill on expiry → `resource_exhaustion`), total-budget check
  (5400 s), maximum-runs check (4), best-effort 4 GiB address-space rlimit,
  capture and measurement, manifest/environment/command writing.
- `driver/validate_execution.py` — lifecycle §7 validation checks (read-only).

## Toolchain probe (recorded before implementation)

- python3 3.12.8 — present.
- sympy 1.14.0 — present; not required (the toy instance model is integer
  arithmetic; no symbolic algebra library is used).
- pyyaml 6.0.3 — present (spec parsing, manifest writing).
- jsonschema — absent. The frozen contract requires a `package_schema.json`
  and a verifier, not a specific validation library; the verifier therefore
  implements schema validation natively against the schema document. No
  packages were installed. Not an infrastructure failure.

## Toy instance model (fully public, deterministic)

Five signed, coloured decks of B occurrence records each. A label is
complete when it occurs in every deck; a source tuple picks one occurrence
per deck; tuples containing `identity`/`infinity` markers are inadmissible;
a label is extendible when it has an admissible tuple. The reference support
set E = extendible ∩ target; reference z_R = ∏_{l∈E}(x − l); the replay
table maps every universe label to its exact admissible tuple set (empty =
negative). Pair-product generators are exactly the B² deck0×deck1 pairs with
endpoint values `(x+y) mod M`; generator g witnesses l iff both endpoints
carry l and l is extendible — in this synthetic model extendibility is a
static Boolean OR over this relation table (exactly what the CAL-PASS
fixture legitimately exploits; the fixture is an instrument, not a route).

Strata are engineered per the frozen enumeration: `no_relation_unit`
(E = ∅, z_R = 1), `single_hit` (one linear factor, collision-free
endpoints), `multi_hit`, `collision_duplicate_endpoints` (a false pair
collides with the true witness at its endpoint value), `exceptional_markers`
(tangent/vertical admissible; identity/infinity inadmissible),
`repeated_source` (two occurrences in deck 2 → exactly two tuples). Each
instance embeds a mutated twin (same decks, disjoint target label set;
twin labels are never placed, so E′ = ∅) for the V2 mutation control.

The verifier independently re-derives extendibility, E, z_R, the replay
table, and the generator list from the deck records and asserts equality
with the instance's reference block (instance integrity instrument check).

## Verifier design

- **V1** schema + frozen vocabulary + graph totality (roots are
  `load_pair_product_generators`, single `support_factor` sink, acyclic,
  every node on a root→sink path, every edge carries the three typed map
  exponents) + no oracle node (`supplied_input`) + no untyped macro
  (`whole_divisor_translation_macro`, `target_fitted_selector`).
- **V2** preprocessing artifacts (retained preprocessing node values,
  canonical bytes) compared byte-wise across each instance/twin pair; the
  engine structurally gives preprocessing nodes no target argument, and the
  comparison is still executed mechanically on all 12 pairs.
- **V3** forbidden-payload scan over node `produces` types (the BATCH-002
  list: represented degree-B² target coefficient vector, Θ(B³) translated
  pair endpoints or quotient coordinates, supplied resultant/residue/common
  factor/source tuple/scalar character, target-fitted selector,
  whole-divisor translation) + declared caps: preprocessing
  time/advice/state ≤ 9/4, online-materialized target-dependent coordinates
  ≤ 5/4.
- **V4** support(z_R_constructed) ⊿ support(z_R_reference) per instance.
- **V5** exact replay per instance over every universe label against the
  reference table (positive and negative queries), plus the
  no-relation-unit check (z_R = 1 and no credited split).
- **V6** certificate aggregation consistency (phase-max over typed maps;
  edge phase = target-node phase; retained state = max retained
  preprocessing node size; online workspace = max online edge outputs and
  online node sizes) + caps 9/4 (preprocessing time/advice/state) and 5/4
  (online time/workspace) + replay accounting fields (positive/negative
  dyadic queries and final exact source verification included).

Dedup control (CTRL-DEDUP-PRIOR-NEGATIVES): D1 supplied-input payloads and
D2 macros → owner EV-CRYPTO-002; D3 node-kind signatures → the P1553/P1513
duplicate-owner list recorded in the pinned candidate report (blob
69615720416250cd713c030df9b7414eefc13494 at the pinned commit; integrity of
that record is itself audited by CTRL-CORPUS-INTEGRITY).

## Route packages (honest declared exponents)

The eight frozen routes are the standard algebraic backends named in the
pinned candidate report: they materialize the represented degree-B² target
coefficient vector (Θ(B³) target-dependent coordinates) online, or assume
r_R supplied. Certificates are computed from the typed maps by the builder
with the phase-max rule. Expected mechanical outcomes (not predictions about
the hypothesis): routes 01, 03–08 fail V3 and V6 with correct instance
semantics (V4/V5 pass); ROUTE-02 additionally fails V1 (oracle node) and is
recorded failed_duplicate with owner EV-CRYPTO-002; ROUTE-07 matches
IDEA-063; ROUTE-08 matches IDEA-071.

## Recorded interpretation choices

1. **Corpus audit is spec-parsed, never hand-transcribed.** During
   pre-implementation contract validation, the executor manually re-typed
   hash-manifest entry #16's path into a `git rev-parse` probe and mistook
   its `BATCH-001` segment for `BATCH-002`, producing a spurious "missing
   path" observation; the frozen manifest is in fact consistent (19/19
   entries verify at the pinned commit, confirmed by the mechanical audit in
   the smoke rehearsal and again in RUN-CREP-001-A). The implementation
   therefore parses `specification.yaml` programmatically and never
   hand-transcribes pinned paths or hashes. The incident is recorded as an
   anomaly in the execution report (AGENTS.md rule 8).
2. **Run-artifact naming**: the specification's `required_artifacts` lists
   `{manifest.yaml, command.txt, environment.json, raw-result.json,
   stdout.log, stderr.log}` per run while the handoff lists `{manifest.yaml,
   command.txt, environment.json, raw.json, summary.json, stdout.txt,
   stderr.txt}`. Each run directory contains the union; alias files are
   byte-identical copies.

## Budget discipline

Per-run hard cap 1800 s enforced by the launcher (kill on expiry);
total 5400 s checked before each launch against recorded manifests; 4 GiB
best-effort address-space rlimit; maximum 4 runs enforced by the launcher
(refuses a fifth).
