# ECDLP-IDEA-132 — High-dimensional-expander sheaf decoder

## Status and claim labels

- Class: `algorithm`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_supplied_local_view_decoder`
- Cohort: `20260717-g`
- Evidence scale: zero run; any future HDX-sheaf preflight is `toy`
- Contract posture: no contract; execution is not authorized
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an expanding complex, locally testable sheaf code,
  recovered local section, valid relation, or recovered toy scalar is not an ECDLP break.

## Falsifiable hypothesis

Construct an implicit bounded-degree high-dimensional addition complex whose faces encode
compatible partial factor-base sums, and place a source-label sheaf code on it. Suppose a
public target determines a coboundary syndrome, the complex has source-preserving
unique-neighbor/cosystolic expansion, and syndrome peeling recovers a bounded complete
list of global sections biconditional with exact signed five-source tuples. If complex
access plus decoding has complete exponent `alpha<3/2`, this yields rank-`B` factor logs
and blind descent below rho.

The record is merged/rejected. Existing HDX, agreement, and sheaf-code theorems start from
supplied local views; they do not construct those views from one elliptic endpoint. That
endpoint-to-local-view map is the missing source oracle already isolated by IDEA-014's
public-target syndrome/error-locator lane, while invoking a stronger decoder after local
views exist repeats IDEA-130's decoder-substitution boundary.

## Mechanism-new operation

The proposed operation is **encode partial elliptic sources as stalk data on an implicit
addition complex, derive a target coboundary syndrome, use high-dimensional
unique-neighbor expansion to peel inconsistent faces, and reconstruct an exact global
source section**. The sheaf, restriction maps, syndrome, decoder, and source unranking are
frozen target-independently.

Running an agreement test on already enumerated local sources, building the entire relation
hypergraph, substituting a generic LDPC decoder, returning only a membership certificate,
or discarding provenance is a duplicate/control. Only a source-preserving implicit
expansion theorem that reduces source generation is mechanism-new. Relative to IDEA-014,
the proposal needs a concrete public identity mapping an endpoint to exact source-bearing
local-view syndromes; relative to IDEA-130, the HDX/sheaf decoder cannot be the only changed
operation after an incidence word has already been supplied.

## Assumptions

1. `E(F_p)` contains public prime-order `<P>` of order `N=p^(1+o(1))`, target `Q=[x]P`,
   fixed arity five, and target-independent sign-canonical factor base
   `F={F_1,...,F_B}` with `B=L=N^ell`.
2. The addition complex has a public implicit incidence oracle, bounded local degree, and
   source-label stalks/restriction maps uniform over the declared curve family.
3. Target `R` determines a syndrome from public point data alone, without source
   enumeration, factor logs, or a dense pair/five-source table.
4. Quantified unique-neighbor, spectral, coboundary, and cosystolic expansion hypotheses
   hold for the source sheaf and imply a bounded complete global-section list.
5. Every decoded section maps biconditionally to exact signed factor points, including
   order, repetitions, infinity, covers, and all cohomological ambiguity.
6. Complex setup/access, local views, peeling rounds, list output, misses, rank, linear
   algebra, blind descent, verification, and peak bit memory are fully charged.
7. All finite observations remain toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`implicit_addition_complex | source_stalk_sheaf_code | high_dimensional_unique_neighbor_expansion | coboundary_syndrome_peeling | exact_global_source_section | blind_descent`

The implicit source-preserving expansion theorem and target-syndrome/global-section
biconditional are load-bearing. Local agreement after relation enumeration is only a
control.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-P044`, where six-point cores give an
   exact rank-one pencil primitive but fixed cores lose diversity; the addition complex
   must spread source support without that collapse.
2. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-P045`, where consecutive cores retain
   a useful kernel section; the sheaf restriction maps generalize this only if expansion
   gives exact global source recovery.
3. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-P060`, where a matrix kernel has a
   canonical active-support decomposition; source stalks must retain the same presentation
   fidelity without hidden inactive incidence.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H675`, where exact coordinate predicates
   and recursive addition features fail to give a complete source-resolving generator.
5. `ledger/FINDING-PF-IC-001.md` — imported `P1434`, which asks for a public algebraic
   source-fiber generator and transposed target join; the HDX syndrome/section theorem is a
   distinct candidate for that missing generator.

## Closest primary literature

- First and Kaufman,
  [On Good 2-Query Locally Testable Codes from Sheaves on High Dimensional Expanders](https://arxiv.org/abs/2208.01778),
  introduce expanding sheaves on simplicial complexes for locally testable codes; they do
  not construct elliptic source stalks or a target-to-section decoder.
- Dinur and Kaufman,
  [High dimensional expanders imply agreement expanders](https://eccc.weizmann.ac.il/eccc-reports/2017/TR17-089/),
  prove local-to-global agreement testing on high-dimensional expanders; they begin with
  local functions and do not generate a rare source witness from one group endpoint.
- Dikstein and Dinur,
  [Agreement theorems for high dimensional expanders in the small soundness regime](https://arxiv.org/abs/2308.09582),
  show that covers govern list versus lift decoding; this exposes, rather than removes,
  possible source-section ambiguity.
- Dikstein, Dinur, Harsha, and Ron-Zewi,
  [Locally testable codes via high-dimensional expanders](https://arxiv.org/abs/2005.01045),
  derive local testability from high-dimensional expansion and iterative correction; they
  do not prove an implicit ECDLP source-incidence complex.

No checked primary source supplies the required addition-complex expansion, target
syndrome/source-section biconditional, or fully charged better-than-rho descent.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,B=L`, implicit addition complex, incidence oracle, source sheaf,
   restriction maps, expansion parameters, syndrome map, peeling/list decoder,
   exceptional cases, and independent elliptic verifier.
2. Construct target-independent local complex/sheaf data and prove the incidence oracle
   uses subquadratic work/memory; certify expansion and record all covers, cohomology,
   disconnected links, repeated labels, and failed local restrictions.
3. For known public `R_j=[r_j]P`, compute its frozen coboundary syndrome, run complete
   peeling/list decoding, unrank every accepted global section to exact signed factor
   points, and independently verify every five-point elliptic sum.
4. Preserve misses, lift-decoding covers, duplicate sections, and residual cocycles;
   collect exactly `B+sigma` verified rows whose coefficient matrix has rank `B` modulo `N`.
5. Solve every factor-base logarithm and independently verify
   `[log_P(F_i)]P=F_i` for all `i`.
6. Freeze the complex, sheaf, and decoder, choose fresh public masks `t`, and apply the
   identical syndrome and global-section decoder to blind targets `Q+[t]P`.
7. Substitute verified factor logs, subtract `t`, enumerate every cover/cocycle scalar
   candidate, and accept only `x` satisfying `[x]P=Q`.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` expected group operations with constant-state memory;
BSGS costs `N^(1/2+o(1))` time and memory. Set `B=L=N^ell`. Let implicit-complex,
incidence-oracle, sheaf, restriction-map, and expansion-certificate setup cost
`L^(s+o(1))` time and `L^(s_m+o(1))` peak memory. Let one complete syndrome query,
all peeling rounds, cover/cocycle branches, global-section/source output, and verification
cost `L^(alpha+o(1))` time and `L^(m_q+o(1))` memory.

Unless a theorem proves a changed density, use `pi=min(1,L^5/N)`. In the sparse regime,

`T_rel=N*L^(alpha-4+o(1))`

and

`T_desc=N*L^(alpha-5+o(1))`.

Sparse linear algebra costs `L^(2+o(1))` time and at least `L^(1+o(1))` memory. Hence

`lambda=max(s*ell,1+(alpha-4)*ell,2*ell,1+(alpha-5)*ell)`

and

`mu=max(s_m*ell,m_q*ell,ell)`

These are the complete time and peak-memory exponent bounds for the declared path.

For `ell=1/5`, strict time below rho requires `alpha<3/2`; promotion
`lambda,mu<=0.45` requires `alpha<=1.25` and `s,s_m,m_q<=2.25`. Every face/stalk touched,
restriction map, expansion certificate, syndrome symbol, peeling round, cover, cocycle,
global section, emitted source, failed target, row, factor log, and verifier operation is
charged. Materializing `L^2` edges/faces or source incidence fails the gate even if later
decoding is linear in that materialized object.

## Likely fatal obstruction

The exact relation faces are rare and target dependent, so constructing their links may be
the original source search. Arbitrary factor bases need not yield bounded-degree spectral,
unique-neighbor, or cosystolic expansion, and source labels can make the coherent closure
dense. Agreement and sheaf-code theorems recover a global word from supplied noisy local
views; a target endpoint supplies no such views. Postulating an endpoint syndrome without
an exact construction is IDEA-014's missing error-locator oracle, and changing only the
decoder after local incidence is known is IDEA-130's solver-substitution failure.
Nontrivial covers can force lift-decoding ambiguity, while an explicit incidence complex
has at least the recorded `L^2` pair-state cost.

## Proof track

First prove an endpoint-to-local-view expansion identity that is not the postulated public
syndrome of IDEA-014 and does not require IDEA-130-style supplied incidence. Only under a
new ID may a successor then construct the implicit addition complex and source sheaf,
prove source-preserving expansion, bounded complete decoding, and the full seven-step
relation, rank, factor-log, blind-descent, output, and peak-memory bounds.

## Disproof track

Show the endpoint-to-local-view oracle requires dense source enumeration, reduce it to
IDEA-014's public-target syndrome postulate or IDEA-130's supplied-word decoder, prove the
addition complex lacks one required expansion parameter, exhibit a connected cover or
cocycle yielding two different source sections, or derive complete time or memory exponent
at least `1/2`.

## Positive and negative controls

- Positive HDX control: a published finite complex/sheaf-code instance with certified
  expansion, planted global sections, corrupted local views, and complete decoding.
- Positive source control: a planted bounded-degree addition complex whose blinded exact
  source sections and target syndromes are known independently.
- Negative controls: random sparse complexes below expansion threshold, disconnected links,
  connected covers, nontrivial cocycles, and local views with no global source section.
- Mechanism controls: ordinary LDPC/expander codes, agreement tests after source
  enumeration, explicit relation hypergraphs, shared-core pencils, SAT, and Groebner bases.
- Leakage control: permute source labels while preserving unlabeled complex incidence; the
  decoded section must follow the permutation without hidden scalar data.
- Baseline control: matched Pollard rho and memory-matched BSGS.

## Quantitative promotion and falsification gates

This merged/rejected ID cannot reopen by changing the decoder, HDX family, sheaf, or
expansion parameters. No contract exists and no execution is authorized. Reopening
requires a new ID and a concrete public endpoint-to-local-view expansion identity that is
semantically distinct from IDEA-014, is constructed without IDEA-130-style supplied
incidence, proves the syndrome/section biconditional, and derives symbolic
`lambda,mu<=0.45`. Only then may a future toy preflight cover at least 20 ordinary curves per size
across four increasing sizes, exhaustive complex/source truth through 18 bits, at least
`1,000` verified relations and `100` blind descents at each of the two largest sizes,
exactly `B+sigma` retained rows of rank `B`, zero source omissions/errors, and upper 95%
bounds `lambda<=0.45` and `mu<=0.45` including endpoint conversion, all incidence access,
covers, sections, and output. Falsify on failure to construct a source-blind local view,
one reproducible false/omitted section, reduction to IDEA-014 or IDEA-130, unresolved cover
ambiguity, or a proved or lower-95% complete bound `lambda>=0.50` or `mu>=0.50`.

## Artifact plan

- Expansion/source-section theorem gate: `ideas/artifacts/ECDLP-IDEA-132/expansion_section_gate.md`
- Frozen complex/sheaf specification: `ideas/artifacts/ECDLP-IDEA-132/addition_sheaf.yaml`
- Prospective syndrome decoder: `ideas/artifacts/ECDLP-IDEA-132/decode_sections.py`
- Independent complex/source verifier: `ideas/artifacts/ECDLP-IDEA-132/verify_source_sections.sage`
- Prospective receipts: `ideas/artifacts/ECDLP-IDEA-132/runs/<run-id>/`
- Complete analysis: `ideas/artifacts/ECDLP-IDEA-132/analysis.md`

## Interpretation boundary

This merged/rejected record is toy, heuristic, model-bound, high-risk, and
novelty-unverified. An HDX, expanding sheaf, locally testable code, decoded local word,
exact global toy section,
valid relation, full-rank toy matrix, verified factor log, or recovered toy scalar is not
a better-than-rho result or a breakthrough. A concrete endpoint-to-local-view identity is
a new mechanism requiring a new ID; decoder substitution cannot reopen this record.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-132/expansion_section_gate.md` as a zero-run merge note showing why supplied local views reduce to IDEA-014 or IDEA-130 and specifying the concrete endpoint-to-local-view expansion identity that any independently deduplicated new ID would have to prove.
