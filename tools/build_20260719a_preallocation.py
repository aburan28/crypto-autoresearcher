#!/usr/bin/env python3
"""Build the immutable 20260719-a pre-ID ECDLP screening packet."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ideas" / "rejected" / "preallocation"
COHORT = "20260719-a"

COMMON_NEIGHBORS = [
    ("ECFG-H673", "public deck structure or additive energy must change exact relation supply, not only summarize it"),
    ("ECFG-NR-1432-NO-PROSPECTIVE-HIGH-ENERGY-PROMOTION", "aggregate energy failed to provide transferable exact source return"),
    ("ECFG-H675", "the missing operation is an exact public source-resolving circuit for coordinate predicates"),
    ("ECFG-H676", "explicit public source-fibre joins restore the materialization boundary"),
    ("P1476", "the complete m-ary membership, source-output, rank, descent, and memory exponents must be charged together"),
]

CANDIDATES = [
    dict(key="A01", slug="tverberg_barycentric_partition_source_lift", title="Tverberg barycentric-partition source lift", risk="representation-changing", cls="geometric_partition", op="embed the five signed decks as a public point configuration, compute a Tverberg partition with a common barycentric point, and decode its blocks as an exact five-source relation", assumption="a finite-field or lifted ordered embedding makes a common convex-hull point biconditional with the prescribed elliptic endpoint and remains exact under restrictions", fatal="Tverberg's theorem starts from an explicit point configuration and proves existence of intersecting convex hulls, not a prescribed finite-field group sum or labelled occurrence inverse. Constructing the configuration with the needed incidence is the missing source compiler; real convexity also has no faithful target-uniform finite-field meaning.", collisions="IDEAs 155/257/326/359/379", lit_title="Tverberg, A Generalization of Radon's Theorem", lit_url="https://doi.org/10.1112/jlms/s1-41.1.123"),
    dict(key="A02", slug="dulmage_mendelsohn_source_matching_decomposition", title="Dulmage-Mendelsohn source-matching decomposition", risk="conservative", cls="graph_decomposition", op="canonically decompose a public bipartite compatibility graph into Dulmage-Mendelsohn blocks, isolate relation-capable components, and replay a matched source tuple", assumption="the endpoint-only graph is sparse, restriction-stable, and has perfect-matchability exactly when a signed five-source relation exists", fatal="Dulmage-Mendelsohn decomposes a supplied bipartite graph. Edges biconditional with elliptic pair compatibility are already the missing source incidence, while matching feasibility is not exact five-way endpoint equality and a matching does not avoid edge materialization.", collisions="IDEAs 223/345/382/392/396", lit_title="Dulmage and Mendelsohn, Coverings of Bipartite Graphs", lit_url="https://doi.org/10.4153/CJM-1958-052-0"),
    dict(key="A03", slug="szemeredi_regularity_energy_source_quotient", title="Szemeredi-regularity energy source quotient", risk="high-risk", cls="approximate_graph_quotient", op="apply energy-increment regularization to the public relation-incidence graph, query the bounded quotient for target support, and refine only the reported cells to exact sources", assumption="a bounded regular partition preserves every rare exact relation under arbitrary restrictions and admits deterministic source replay within the online cap", fatal="regularity preserves dense statistics only up to an error population far larger than the expected constant number of exact relations. Building the incidence graph is source-sized, and refining irregular or false-positive cells restores the original search; an approximate quotient cannot answer the required exact existence bit.", collisions="IDEAs 340/348/351/366/370", lit_title="Szemeredi, Regular Partitions of Graphs", lit_url="https://www.cnrseditions.fr/catalogue/mathematiques/problemes-combinatoires-et-theories-des-graphes/"),
    dict(key="A04", slug="zero_suppressed_decision_source_compiler", title="Zero-suppressed decision source compiler", risk="conservative", cls="succinct_family_representation", op="compile all valid restricted source subsets into a reduced zero-suppressed decision diagram, apply restriction updates by graph operations, and unrank one accepting five-source path", assumption="the diagram can be built endpoint-first with size at most B^(9/4+o(1)) and remains small for every campaign and blind-target restriction", fatal="ZDD compression is output-sensitive to a supplied family and variable ordering. Compiling the accepting family requires the exact relation predicate or enumerated source sets; adversarial relation families have exponential diagrams, and target updates can rebuild the whole object.", collisions="IDEAs 120/337/371/377/397", lit_title="Minato, Zero-Suppressed BDDs for Set Manipulation", lit_url="https://doi.org/10.1145/157485.164890"),
    dict(key="A05", slug="spqr_triconnected_source_router", title="SPQR triconnected source router", risk="conservative", cls="graph_decomposition", op="construct an endpoint compatibility graph, split it into triconnected SPQR components, answer restricted existence through the decomposition tree, and replay a source path", assumption="the graph is endpoint-constructible without pair tables and relation existence is invariant under the two-vertex separations exposed by the tree", fatal="SPQR decomposition is linear only after every vertex and edge of the supplied graph exists. Generic elliptic compatibility need not have useful separators, restrictions change the graph, and triconnected reachability is not biconditional with a five-source zero sum.", collisions="IDEAs 352/369/383/386/388", lit_title="Hopcroft and Tarjan, Dividing a Graph into Triconnected Components", lit_url="https://doi.org/10.1137/0202012"),
    dict(key="A06", slug="fm_index_backward_source_unranking", title="FM-index backward source unranking", risk="representation-changing", cls="succinct_string_index", op="serialize source-labelled transition words, apply a Burrows-Wheeler transform, use backward-search intervals for target restrictions, and locate one exact source occurrence", assumption="a target-independent serialization makes every valid five-source tuple one contiguous pattern occurrence while retaining entropy-compressed state and exact signed labels", fatal="the FM-index accelerates pattern matching in an explicit text. Serializing all valid source transitions is the missing source catalogue, and no fixed pattern language makes elliptic endpoint equality contiguous without embedding the target or the answers. Entropy bounds do not limit a generic relation text.", collisions="IDEAs 120/350/371/374/377", lit_title="Ferragina and Manzini, Opportunistic Data Structures with Applications", lit_url="https://doi.org/10.1109/SFCS.2000.892127"),
    dict(key="A07", slug="rees_principal_factor_source_coordinates", title="Rees principal-factor source coordinates", risk="high-risk", cls="semigroup_factorization", op="form the finite semigroup of partial source transitions, pass to its principal Rees matrix factors, and read row/group/column coordinates as exact source ancestry", assumption="the semigroup and sandwich matrices are endpoint-constructible below the caps and one factor coordinate is biconditional with a complete signed relation", fatal="Rees coordinates classify a supplied multiplication semigroup. Its elements and sandwich matrix already encode source transitions, while a commutative prime-order quotient is trivial or the original group and factorization does not create missing occurrence labels.", collisions="IDEAs 154/166/184/314/398", lit_title="Rees, On Semi-Groups", lit_url="https://doi.org/10.1017/S0305004100017436"),
    dict(key="A08", slug="nested_dissection_schur_source_separator", title="Nested-dissection Schur source separator", risk="representation-changing", cls="sparse_elimination", op="order a public source-incidence matrix by recursive separators, eliminate interior variables, and use Schur-complement boundary states to recover an exact relation source", assumption="the implicit incidence graph has sublinear balanced separators uniformly under target shifts and the Schur states preserve signed provenance without dense fill", fatal="nested dissection improves factorization only for a supplied sparse graph with geometric separators. The elliptic incidence matrix is not constructed, generic compatibility is dense and separator-free, and Schur complements mix source labels or introduce fill comparable to the omitted incidence.", collisions="IDEAs 231/338/341/369/387", lit_title="George, Nested Dissection of a Regular Finite Element Mesh", lit_url="https://doi.org/10.1137/0710032"),
    dict(key="A09", slug="dancing_links_exact_cover_source_unranking", title="Dancing-links exact-cover source unranking", risk="conservative", cls="exact_cover_backend", op="encode signed deck choice and endpoint constraints as exact cover, use reversible cover/uncover updates, and emit one accepting five-row cover with source labels", assumption="the exact-cover matrix is endpoint-constructible with subgate nonzeros and its accepting covers are exactly complete signed elliptic relations", fatal="dancing links is a reversible implementation of backtracking over an explicit exact-cover matrix. Encoding endpoint equality requires the missing source-incidence columns or a solver oracle, and worst-case branching plus failed covers is unbounded; reversibility preserves supplied labels but does not compile them.", collisions="IDEAs 117/122/146/325/377", lit_title="Knuth, Dancing Links", lit_url="https://arxiv.org/abs/cs/0011047"),
    dict(key="A10", slug="cegar_endpoint_abstraction_source_refinement", title="CEGAR endpoint-abstraction source refinement", risk="high-risk", cls="abstraction_refinement", op="start from a coarse endpoint abstraction, reject spurious relation witnesses with proof-derived predicates, and refine until an exact signed source tuple remains", assumption="a target-independent predicate basis reaches exactness after at most B^(5/4+o(1)) refinement work and avoids enumerating source combinations on no-relation queries", fatal="CEGAR needs a concrete transition system and a checker capable of distinguishing real from spurious counterexamples. Here that checker is Query2P1 or explicit source search; generic refinement can add one source-specific predicate per counterexample and has no target-uniform compactness guarantee.", collisions="IDEAs 120/138/146/377/378", lit_title="Clarke et al., Counterexample-Guided Abstraction Refinement", lit_url="https://doi.org/10.1007/10722167_15"),
    dict(key="A11", slug="fks_perfect_hash_source_dictionary", title="FKS perfect-hash source dictionary", risk="conservative", cls="static_dictionary", op="store source-labelled partial endpoints in a collision-free two-level perfect hash, query exact target complements in constant probes, and return one source tuple", assumption="the dictionary can be constructed without materializing more than B^(9/4+o(1)) partial endpoints and remains reusable on fresh targets", fatal="FKS hashing gives constant-time lookup only after all keys and satellite source labels are supplied. The natural pair/triple dictionaries contain B^2/B^3 keys, and hashing changes lookup constants rather than the number of states, failed attempts, relation density, rank, or descent cost.", collisions="IDEAs 344/347/350/374/380", lit_title="Fredman, Komlos, and Szemeredi, Storing a Sparse Table", lit_url="https://doi.org/10.1145/828.1884"),
    dict(key="A12", slug="aho_corasick_source_failure_automaton", title="Aho-Corasick source failure automaton", risk="conservative", cls="multi_pattern_automaton", op="encode factor-source words as a public dictionary, build a failure-link automaton, stream target-dependent transition text, and report exact accepting source patterns", assumption="valid relation tuples form a target-independent finite pattern dictionary of total subgate length and target updates generate a short searchable text", fatal="Aho-Corasick indexes explicitly supplied keywords. Listing relation-source words is the missing answer catalogue, while encoding the target into the text is only a query rewrite; failure links share string prefixes, not elliptic partial-sum states, and generic dictionaries have source-sized total length.", collisions="IDEAs 070/120/154/371/377", lit_title="Aho and Corasick, Efficient String Matching", lit_url="https://doi.org/10.1145/360825.360855"),
]


def record(c: dict[str, str]) -> str:
    artifact = f"ideas/rejected/preallocation/artifacts/{COHORT}/{c['key'].lower()}_source_obligations.md"
    neighbors = "\n".join(
        f"{i}. `inputs/ledger_inventory.json` — imported `{entry}`; {note}."
        for i, (entry, note) in enumerate(COMMON_NEIGHBORS, 1)
    )
    return f"""# Pre-ID duplicate draft — {c['title']}

## Status and claim labels

- Prospect: `{COHORT}-{c['key']}`; no canonical ECDLP idea ID was allocated
- Class: `{c['cls']}`
- Risk band: `{c['risk']}`
- Top lane: relative pre-ID screen only
- State: `merged_rejected_supplied_source_object_or_unchanged_exact_endpoint_compiler`
- Cohort: `{COHORT}`
- Evidence scale: complete corpus/ledger and primary-literature review only; no experiment ran
- Contract posture: {'retired zero-run text snapshot' if c['key'] in {'A01','A02','A07'} else 'none; rejected before dispatch'}
- Scale labels: every prospective finite check declares its tested parameters;
  every extrapolation states its heuristic and model assumptions.
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; correctness of the named operation is not an ECDLP result.

## Falsifiable hypothesis

For generic prime-order `E(F_p)`, one can {c['op']}. The operation is target-uniform and restriction-stable, yields at least `B` independent verified rows, supports fresh masked-target descent, and has complete time and memory exponents below rho and BSGS.

## Mechanism-new operation

The raw screened operation is **{c['op']}**. It would count only if it acts on public endpoint/deck data before source incidence is known and removes the exact source-return obstruction; applying it to a supplied answer catalogue is a duplicate/control.

## Assumptions

1. {c['assumption']}.
2. Setup, state, failed branches, restrictions, source output, rank, logs, target descent, verification, bit time, and peak memory are all charged.
3. The same target-independent state and policy work on known-log calibration targets and fresh scalar-blind `Q+[t]P` targets.
4. Exact signed/chart-complete existence survives every dyadic restriction; charged bisection and singleton verification recover actual occurrences.
5. No scalar oracle, post-hoc selector, explicit `B^3` table, dense resultant, relation-only certificate, or uncharged source dictionary is admitted.

## Semantic fingerprint

`public_endpoint_or_deck_state | {c['slug']} | exact_restricted_existence | signed_source_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

{neighbors}

## Closest primary literature

- [{c['lit_title']}]({c['lit_url']}) states the named operation on its native supplied input; it does not provide an elliptic endpoint-to-source compiler.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations but not this exact source-return operation.
- Shoup, [Lower Bounds for Discrete Logarithms and Related Problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the matched generic-group boundary, not a lower bound on coordinate-sensitive operations.

No checked primary source constructs the required public ECDLP interface; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, five signed decks, repeated/tangent/vertical/infinity charts, restrictions, representation, update policy, and verifier before targets.
2. Build target-independent state within `B^(9/4+o(1))` without source-product materialization or discrete logarithms.
3. On known-log targets, answer exact restricted existence and recover five signed occurrences using charged `O(log B)` positive-parent/negative-child bisection plus singleton verification.
4. Collect at least `B` independent verified rows, retaining failures and dependencies; solve factor-base logarithms.
5. Reuse unchanged state on fresh scalar-blind `Q+[t]P`, recover a verified factor tuple, substitute logs, remove `t`, and verify `[x]P=Q`.
6. Charge construction, updates, failed branches, output, rank, factor logs, descent, verification, bit operations, and peak memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work `N^q,N^q_m`, verified-rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Require `0<=r<=o`, setup/state at most `B^(9/4+o(1))`, total fresh online restriction/bisection and singleton verification at most `B^(5/4+o(1))`, and `lambda<=0.45`, `mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

{c['fatal']} This merges with {c['collisions']} at the operation-plus-information-flow boundary.

## Proof track

Construct the endpoint-only object without source materialization, prove exact restriction-stable existence and source replay, and then certify independent rank plus the full sub-rho descent and memory bounds.

## Disproof track

Exhibit one required supplied source object or oracle, one restriction collision, one lost signed occurrence, worst-case state/query work above the caps, or a complete exponent at least `0.50`.

## Positive and negative controls

- Positive: a supplied native-domain instance with planted unique source labels must execute the named operation and replay those labels exactly.
- Negative: identical aggregate/quotient state with different source tuples, absent endpoints, repeated labels, signed/chart exceptions, adversarial restrictions, and fresh blind targets.
- Baselines: {c['collisions']}, explicit pair/triple tables, Query2P1/P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only construction, exact all-strata restricted existence, charged bisection, `1,000` independent rows, `100` blind descents, both state/query caps, and `lambda,mu<=0.45`.
- Falsify on one supplied answer catalogue, one existence/source mismatch, one source-dependent update, cap violation, or either exponent at least `0.50`.
- Correctness on a supplied object is a valid control or result within the
  declared object and transfer assumptions.

## Artifact plan

- `{artifact}`
- `ideas/rejected/preallocation/artifacts/{COHORT}/{c['key'].lower()}_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/{COHORT}/{c['key'].lower()}_cost_analysis.md`

## Interpretation boundary

This rejects the screened ECDLP transplant, not the cited native theorem or algorithm. Every prospective check is parameter-bound, heuristic where applicable, model-bound where applicable, and novelty-unverified; no relation, validator pass, or correct native operation is a breakthrough by itself.

## Exactly one next executable action

1. Write `{artifact}` and classify every input token, state transition, restriction update, acceptance bit, and returned label as endpoint-derived or source-bearing before any run is considered.
"""


def contract(c: dict[str, str]) -> str:
    base = f"ideas/rejected/preallocation/artifacts/{COHORT}/{c['key'].lower()}"
    return f"""# Non-dispatchable pre-ID contract snapshot. The .yaml.txt suffix is intentional.
experiment:
  id: PREID-{COHORT}-{c['key']}-PREFLIGHT
  hypothesis_id: PREID-{COHORT}-{c['key']}
  lane: {c['risk'].replace('-', '_')}
  version: 1
  title: {c['title']} theorem preflight
  status: review_required
  retired_from_dispatch: true
  retirement_reason: supplied_source_object_or_unchanged_exact_endpoint_compiler
  approved_by: null
  assigned_to: none
  objective: Audit endpoint-only construction, exact restricted existence, signed source replay, and complete descent costs.
  claim_boundary:
    evidence_scale: null
    model_status: heuristic_model_bound
    novelty_status: novelty_unverified
    breakthrough_claim: false
  controls:
    - positive_supplied_native_domain_instance
    - negative_same_aggregate_state_different_source_labels
    - negative_blind_target_and_arbitrary_restrictions
  metrics:
    - lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)
    - mu=max(a_m,q_m,beta+o,ell_m,u)
  budget:
    maximum_runs: 0
    wall_clock_seconds: 0
    memory_gb: 0
  stopping_rules:
    - stop_if_any_input_or_update_requires_source_incidence_or_a_target_fitted_oracle
    - stop_if_any_complete_exponent_reaches_0_50
  success_criterion: A theorem-only endpoint compiler and complete lambda,mu<=0.45 proof.
  falsification_criterion: Any supplied source object, restriction mismatch, cap violation, or complete exponent at least 0.50.
  required_artifacts:
    - {base}_source_obligations.md
    - {base}_counterexamples.json
    - {base}_cost_analysis.md

handoff:
  id: TASK-{COHORT}-{c['key']}
  from: coordinator
  to: executor
  objective: Preserve this retired theorem-only preflight; never dispatch or run it.
  inputs:
    - ideas/rejected/preallocation/{COHORT}_{c['key']}_{c['slug']}_preid_duplicate.md
    - ideas/rejected/preallocation/{COHORT}_{c['key']}_{c['slug']}_contract_preid_duplicate.yaml.txt
  constraints:
    - No experiment, solver, relation campaign, or artifact generation is authorized.
    - State the tested parameters, transfer assumptions, and novelty status for every prospective claim.
  deliverables:
    - theorem obligation audit only
  budget:
    wall_clock_seconds: 0
    memory_gb: 0
    maximum_runs: 0
  completion_gate:
    - No run occurred and no canonical idea ID was allocated.
"""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for candidate in CANDIDATES:
        path = OUT / f"{COHORT}_{candidate['key']}_{candidate['slug']}_preid_duplicate.md"
        if path.exists():
            raise SystemExit(f"refusing to overwrite {path}")
        path.write_text(record(candidate), encoding="utf-8")
        if candidate["key"] in {"A01", "A02", "A07"}:
            cpath = OUT / f"{COHORT}_{candidate['key']}_{candidate['slug']}_contract_preid_duplicate.yaml.txt"
            if cpath.exists():
                raise SystemExit(f"refusing to overwrite {cpath}")
            cpath.write_text(contract(candidate), encoding="utf-8")


if __name__ == "__main__":
    main()
