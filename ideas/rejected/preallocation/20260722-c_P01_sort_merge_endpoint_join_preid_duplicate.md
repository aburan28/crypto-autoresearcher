# Pre-ID duplicate draft — sort-merge endpoint join

## Status and claim labels

- Provisional ID: `PREID-20260722-c-P01`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_sorted_source_relations`.
- Class/risk: algorithm / conservative.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a correct merge, relation, or validator pass is not an ECDLP result.

## Falsifiable hypothesis

For a generic prime-order curve, two endpoint-derived sorted streams encode complementary
source partial sums. A sort-merge equijoin on the target label returns exact signed five-point
occurrences for relation collection and fresh masked targets with complete time and memory
exponents at most `0.45`.

## Mechanism-new operation

The native operation advances two sorted relations monotonically and emits equal-key tuples.
It counts here only if both streams and their keys are produced from public endpoints without
enumerating source pairs or embedding scalar labels, and if restricted joins replay actual
signed occurrences. Merging already materialized pair sums is a control.

## Assumptions

1. Both sorted streams are target-independent and constructible inside the setup cap.
2. Key equality is biconditional with elliptic target equality on every exceptional stratum.
3. Equal-key runs retain point identities, signs, multiplicities, and a charged inverse.
4. Restriction does not require rebuilding a source table or scanning a dense run.
5. The same byte-identical state serves relation targets and fresh masked targets.

## Semantic fingerprint

`public_endpoint_sorted_relations | monotone_sort_merge_equality | exact_restricted_existence | charged_signed_occurrence_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260721-c_K01_schroeppel_shamir_four_list_source_join_preid_duplicate.md` — list joins remain source-bearing when partial sums are materialized.
2. `ideas/rejected/ECDLP-IDEA-117_degree_aware_provenance_join_hypothesis.md` — factorized joins must charge source construction and output.
3. `ideas/rejected/ECDLP-IDEA-325_insideout_faq_source_join_hypothesis.md` — a join backend does not create the missing source relations.
4. `ideas/artifacts/ECDLP-IDEA-117/p1511_factorized_semijoin_derivation.md` — explicit semijoin derivation exposes the input-width floor.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — current exact endpoint-existence and replay owner.

## Closest primary literature

- Blasgen and Eswaran, [Storage and Access in Relational Data Bases](https://doi.org/10.1147/sj.164.0363), analyzes relational access and join processing on supplied relations.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies equations but not sorted sparse source streams.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), is the generic baseline.

The database primitive is title-new here but the ECDLP transplant is a list-join/backend
merge. No literature source supplies the endpoint compiler or signed inverse; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, stream schemas, key order, signs, restrictions, strata, and verifier.
2. Build endpoint-only sorted state within `B^(9/4+o(1))`; forbid explicit pair tables,
   target fitting, scalar residues, and hidden decomposition calls.
3. For each known-log target, merge restricted streams, replay an occurrence tuple, and verify
   the elliptic sum before admitting a row.
4. Collect `max(d_FB+32,1000)` verified independent rows, require rank `d_FB`, and solve every
   factor log while charging sorting, equal-key runs, failures, output, and sparse linear algebra.
5. Reuse identical state for 100 fresh `R=Q+[t]P`, replay signed points, compute
   `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge endpoint compilation, sorting, scans, duplicates, replay, rank, factor logs, bit
   complexity, and peak live memory.

## Full rho/BSGS cost model

For `beta=1/5`, let setup/state be `N^a,N^a_m`; relation and target reciprocal densities be
`N^delta,N^delta_t`; query/workspace be `N^q,N^q_m`; verified-rank credit be `N^r`; output
be `N^o`; ambiguity be `N^u`; and factor-log time/memory be `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Sorting and all equal-key traffic are included.
Promotion requires `lambda,mu<=0.45`, setup/state `<=B^(9/4+o(1))`, and fresh
work/workspace `<=B^(5/4+o(1))`. Pollard rho expected time and BSGS time/memory have exponent `0.50`.

## Likely fatal obstruction

The sorted relations are the missing source-bearing object. Building useful keys requires
enumerating partial sums or an equivalent `Query2P1` predicate; otherwise merge equality is
unrelated to elliptic target equality. Large duplicate runs restore the omitted output cost.

## Proof track

Prove an endpoint-only stream compiler, exact all-strata key biconditional, bounded equal-key
runs, restriction-stable signed inverse, and complete descent inside both caps.

## Disproof track

Identify source enumeration in either stream, a false/missed equality, a super-cap sort/run,
lost occurrence identity, restriction rebuild, or complete exponent `>=0.50`.

## Positive and negative controls

- Positive: two supplied toy sorted relations with one labelled equal-key tuple.
- Negative: equal aggregate/different sources, empty fibres, duplicate runs, repeated signed
  points, shuffled keys, and blind targets.
- Baselines: Schroeppel-Shamir, factorized semijoins, P1553 R4, rho, and BSGS.
- Native merge correctness is only toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with zero semantic errors over four sizes/all strata, full rank/logs, 100 blind
  descents, both caps, and `lambda,mu<=0.45`.
- Falsify on supplied source streams, one key-semantic error, lost replay, cap violation, or
  any complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-c/p01_stream_compiler_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-c/p01_equal_key_collision_cases.json`
- `ideas/rejected/preallocation/artifacts/20260722-c/p01_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not sort-merge joins. Evidence is toy, heuristic, model-bound,
and novelty-unverified; no relation or correctness result would be a breakthrough.

## Exactly one next executable action

1. Specify both endpoint-only sorted-stream constructors and either prove exact restricted signed replay within the caps or preserve the first source-enumeration dependency.
