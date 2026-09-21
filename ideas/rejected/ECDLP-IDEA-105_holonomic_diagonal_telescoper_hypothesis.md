# ECDLP-IDEA-105 — Holonomic diagonal telescoper

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- State: `merged_rejected_aggregate_no_witness`
- Evidence scale: no run; any diagnostic would be `toy`
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Deduplication verdict: a telescoper compresses an aggregate diagonal/count but does not
  recover factor-base sources; conditioned witness extraction returns to the occupied
  membership and source-enumeration lanes.
- Breakthrough claim: **none**; a correct differential equation, recurrence, relation
  count, or toy decomposition is not an ECDLP break.

## Falsifiable hypothesis

Encode the signed `m`-source Semaev relation fiber for output `R` as a diagonal or residue
of a rational function. The proposed claim is that Griffiths-Dwork creative telescoping
produces a target-uniform holonomic operator of order and coefficient size
`N^(o(1))`. Its recurrence would evaluate exact conditional source counts quickly enough
to self-reduce to factor-base witnesses, collect `B+sigma` full-rank rows, solve all
factor logs, and perform blind descent with total time and memory exponents below `1/2`.
The formulation is rejected because the cited telescoper deliberately omits certificates
and aggregates the very source provenance required by the ECDLP path.

## Mechanism-new operation

The screened operation is **take a rational diagonal of the complete relation incidence,
compute a compact holonomic telescoper in the target parameter, and use recursively
conditioned diagonal values to unrank exact source tuples**. A recurrence for counts,
faster summation-polynomial evaluation, creative telescoping without certificates, or a
new implementation of resultant elimination is a control. Exact source unranking would
require a separate conditioned diagonal for every branch or a source-retaining
certificate; that is the already occupied membership/source problem, so the candidate is
merged and rejected.

## Assumptions

1. `E(F_p)` has a public prime-order subgroup `<P>` of order `N=p^(1+o(1))`, target
   `Q=[x]P`, fixed arity `m`, and target-independent factor base `F` of size `B=N^beta`.
2. A rational function of sub-rho description size has a diagonal equal to the exact
   signed relation count for every target, including exceptional and repeated branches.
3. A compact telescoper over a suitable parameter specializes correctly over `F_p` and
   has enough initial conditions for all relation and masked-target queries.
4. Conditional diagonal values can be computed and inverted to exact source indices,
   signs, and multiplicities without constructing one operator per explicit branch.
5. Rational-function construction, reduction, telescoper order/degree, initial values,
   conditioning, source output, misses, rank, descent, verification, and memory are charged.
6. Any diagnostic remains toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`Semaev_relation_rational_diagonal | Griffiths_Dwork_telescoper | compact_holonomic_target_recurrence | conditioned_count_self_reduction | exact_source_unranking | blind_descent`

The collision key is `aggregate count without certificate + conditional self-reduction
reconstructs source incidence`. A short recurrence by itself has no algorithmic credit.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-MX-1478`, where a compact exact
   transition norm still fails when dense composition and source output are charged.
2. `ledger/FINDING-PF-IC-001.md` — imported `P1478`, the closest exact norm/resultant
   identity with no black-box common-root source algorithm.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1477`, where serial state
   polynomials do not provide complete five-term membership.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1479`, showing that compact public
   features do not carry factor-log orientation.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H661`, the nearest target-adaptive
   zero-product tree whose exact filtering still requires source work.

## Closest primary literature

- Bostan, Lairez, and Salvy,
  [Creative telescoping for rational functions using the Griffiths-Dwork method](https://arxiv.org/abs/1301.4313),
  give an algorithm and order/degree bounds for telescopers of rational functions; a key
  feature is avoiding certificates, which is precisely the missing source provenance.
- Semaev,
  [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031),
  defines the comparison relation equations and requires actual bounded/source solutions,
  not only their count.
- Bostan, Chen, Chyzak, and Li,
  [Complexity of Creative Telescoping for Bivariate Rational Functions](https://arxiv.org/abs/1301.5045),
  supplies a nearby complexity analysis for rational telescoping and diagonal examples,
  not an ECDLP witness inverse.

No checked source turns a telescoper for an elliptic relation count into a sub-rho exact
factor-base source unranking algorithm. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,B,m`, the rational diagonal representation, target parameter,
   coefficient field, exceptional-branch policy, and exhaustive tiny source truth.
2. Construct the rational function and telescoper without enumerating `F^m`; independently
   verify every diagonal count through the exhaustive range.
3. For random known outputs `R_j=[r_j]P`, use conditioned recurrence queries to unrank all
   accepted signed factor-base tuples and independently verify each elliptic sum.
4. Retain zero counts, failed conditionings, duplicate tuples, ambiguous branches, and
   dependencies; collect exactly `B+sigma` verified rows of rank `B`.
5. Solve and independently verify every factor-base logarithm modulo `N`.
6. Freeze all recurrence data and apply identical conditioned unranking to masked blind
   targets `Q+[t]P`, with no target-specific rebuilt source table.
7. Substitute factor logs, unmask all candidates, retain ambiguity, and accept only after
   verifying `[x]P=Q`.

## Full rho/BSGS cost model

Pollard rho has time exponent `1/2` and constant state; BSGS has time and memory
exponents `1/2`. Let `B=N^beta`. Let target-independent rational-function/telescoper
setup take `N^(a+o(1))` time and `N^(a_m+o(1))` peak memory. Let construction and
serialization of the telescoper, its coefficients, recurrence state, and all initial
values take `N^(h+o(1))` time and `N^(h_m+o(1))` storage. Let one exact conditioned
recurrence query take `N^(q+o(1))` time and `N^(q_m+o(1))` working memory. Let the full
self-reduction tree use `N^(b+o(1))` such query-equivalents per returned source and
`N^(b_m+o(1))` resident state; a literal scan across all `B` next-source choices has
`b>=beta`. Let emitted source tuples and residual target-scalar ambiguity have exponents
`o` and `u`. Let reciprocal usable-relation and target success probabilities be
`N^delta` and `N^delta_t`. Let factor-log linear algebra take `N^(ell+o(1))` time and
`N^(ell_m+o(1))` memory, with `ell>=2beta` absent proved structure. Finally, let
verification per emitted tuple or candidate take `N^(v+o(1))` time and
`N^(v_m+o(1))` working memory.

The complete time exponent is

`lambda=max(a,h,beta+delta+q+b+o+v,ell,delta_t+q+b+o+u+v)`,

and the complete peak-memory exponent is

`mu=max(a_m,h_m,q_m,b_m,ell_m,beta,o+u,v_m)`.

Every reduction, initial value, specialization, conditioning branch, failed target,
emitted tuple, candidate, and verification is charged. The setup terms `a,a_m,h,h_m`
receive one-time credit only when the serialized object is target-independent; rebuilding
any part for a relation or blind target adds that work to every corresponding attempt.
If exact unranking scans `B` conditionals per source position or reconstructs a `B^m`
coefficient object, that full work appears in `b` and in the charged state/output terms.

## Likely fatal obstruction

Creative telescoping projects away integration variables and hence source identities.
Different factor-base tuples with the same target contribute to one diagonal coefficient
and one recurrence value. Recovering a tuple by conditioning requires new diagonals or
initial data that distinguish the individual atoms; their total description/output can
equal the original incidence table. Over finite fields, differential recurrences can also
degenerate or require degree/order proportional to the geometric solution count.

## Proof track

A versioned successor would need a source-retaining holonomic certificate, a theorem
bounding the complete conditioned-unranking tree below rho, and a proof of the seven-step
rank and blind-descent path with `lambda,mu<1/2`. A count-only telescoper cannot satisfy
the proof obligation.

## Disproof track

Exhibit two source tuples with identical telescoper data, show that conditioning requires
one diagonal/operator per source branch, prove telescoper order or initial data scales as
the relation-algebra degree, or establish complete time/output/memory exponent at least
`1/2`.

## Positive and negative controls

- Positive telescoping control: rational functions with published low-order telescopers
  and independently verified diagonals.
- Positive witness control: a planted product measure whose conditional coefficients
  admit a known exact self-reduction.
- Negative source control: distinct relation tuples deliberately collapsed to the same
  target count and recurrence.
- Mechanism controls: direct Semaev solving, serial-state resultants, explicit coefficient
  tables, and source-conditioned telescopers built after enumeration.
- Leakage control: permute source labels while preserving every aggregate diagonal.
- Baseline control: matched Pollard-rho and BSGS.

## Quantitative promotion and falsification gates

No promotion gate remains for this merged formulation. A successor must first prove a
source-retaining certificate and symbolic `lambda,mu<=0.45`. A diagnostic may only check
count/telescoper correctness on exhaustive curves through 18 bits; it cannot promote the
idea. Falsify as written if source-label permutation leaves all telescoper data unchanged,
one recurrence value has multiple unresolved source tuples, conditioned data have lower
95% exponent at least `0.50`, or the complete path has `lambda>=0.50`.

## Artifact plan

- Merge proof: `ideas/artifacts/ECDLP-IDEA-105/telescoper_source_loss.md`
- Rational representation: `ideas/artifacts/ECDLP-IDEA-105/relation_diagonal.yaml`
- Diagnostic telescoper: `ideas/artifacts/ECDLP-IDEA-105/diagonal_telescoper.sage`
- Independent count checker: `ideas/artifacts/ECDLP-IDEA-105/verify_diagonals.py`
- Complete analysis: `ideas/artifacts/ECDLP-IDEA-105/analysis.md`
- Any diagnostic receipts: `ideas/artifacts/ECDLP-IDEA-105/runs/<run-id>/`

## Interpretation boundary

This rejected record is toy, heuristic, model-bound, and novelty-unverified. A compact
operator, correct recurrence, fast count, valid relation, or recovered toy scalar is not
evidence of a better-than-rho algorithm. Source-labelled rows, factor logs, and blind
descent remain mandatory.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-105/telescoper_source_loss.md` proving that Griffiths-Dwork projection forgets source labels and that exact conditioned unranking reconstructs the occupied relation-incidence object.
