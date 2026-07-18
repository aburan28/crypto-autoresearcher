# ECDLP-IDEA-130 — Folded AG list-recovery source decoder

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_encoder_biconditional_missing`
- Cohort: `20260717-g`
- Evidence scale: no run; any future list-recovery preflight is `toy`
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a decodable codeword, short list, exact local test, valid
  relation, or recovered toy scalar is not an ECDLP break.

## Falsifiable hypothesis

Encode each target-independent factor point as a folded evaluation word on a public
algebraic curve. Suppose elliptic addition induces target-computable local tests such that
the word for `R` is close to, or list-recoverable from, exactly the folded words of signed
five-source tuples summing to `R`. A folded algebraic-geometric list-recovery algorithm
would then output a bounded complete source list in exponent `alpha<3/2`, generate
`B+sigma` rank-`B` rows, verify all factor logs, and perform blind descent below rho.

This record is rejected and merged with algebraic source-fiber/list-decoding controls:
known list decoders recover codewords from supplied agreement data, while no theorem makes
generic elliptic addition into a source-resolving folded-code proximity instance.

## Mechanism-new operation

The proposed operation is **map factor points to folded AG evaluation words, compute an
addition-compatible received word from a target, and list-recover a bounded exact set of
factor-point sources from local agreement**. The encoder must be target-independent,
addition compatibility biconditional, and source output complete with signs, repetitions,
infinity, and every list branch.

Applying Guruswami-Sudan or a folded decoder to an explicitly enumerated source table,
changing folds/parameters, treating a membership predicate as a received word, or using a
short list that omits provenance is a solver substitution/control. A new mathematical
encoder theorem must remove the recorded source-fiber obstruction.

## Assumptions

1. `E(F_p)` contains public prime-order `<P>` of order `N=p^(1+o(1))`, target `Q=[x]P`,
   fixed arity five, and target-independent sign-canonical factor base
   `F={F_1,...,F_B}` with `B=L=N^ell`.
2. The auxiliary AG curve, evaluation places, folding automorphism, alphabet, encoder,
   local tests, and decoder are uniform and target-independent.
3. A target word is computed from `R` alone, without source enumeration, factor logs, or
   target-specific retraining.
4. Codeword proximity/list agreement is biconditional with exact five-source elliptic
   addition and yields a bounded complete source list.
5. Signs, order, repetitions, infinity, evaluation collisions, fold orbits, and every
   decoder ambiguity are emitted and independently verified on `E`.
6. Encoder setup, interpolation, root finding, list size, output, misses, rank, linear
   algebra, descent, verification, field operations, and peak bit memory are charged.
7. All finite observations remain toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`factor_point_evaluation_words | addition_compatible_local_tests | folded_AG_list_recovery | bounded_exact_source_list | rank_and_blind_descent`

The addition-compatible target-word/source-codeword biconditional is load-bearing. Generic
list decoding after the source incidence is materialized is only a backend substitution.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H675`, where exact coordinate predicates
   and recursive addition features do not by themselves give a source-resolving generator.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H676`, where exact pair/four-sum source
   generation and transposed joins retain materialization cost; folded words must remove,
   not rename, that boundary.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1407-NO-PROMOTION`, where tested
   coordinate and character predicate bases expand
   like hash controls rather than compressing elliptic sumsets.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1408-NO-EC-PROMOTION`, where low-degree
   polynomial and Mobius image bases fail
   held-out EC compression despite algebraic preimage collisions.
5. `ledger/FINDING-PF-IC-001.md` — imported `P1434`, which asks for a public algebraic
   source-fiber generator and transposed join; the encoder theorem is precisely the missing
   source-generation operation.

## Closest primary literature

- Guruswami and Sudan,
  [Improved decoding of Reed-Solomon and algebraic-geometry codes](https://doi.org/10.1109/18.782097),
  give polynomial-time list decoding from high agreement with evaluation words; they do
  not encode elliptic addition sources into such received words.
- Huang and Narayanan,
  [Folded Algebraic Geometric Codes From Galois Extensions](https://arxiv.org/abs/0901.1162),
  construct folded AG codes and list decoders using automorphisms of function-field
  extensions; they do not prove a source-resolving ECDLP addition encoder.

No checked primary source supplies the required addition/source biconditional or a fully
charged better-than-rho factor-base descent.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,B=L`, the AG curve, evaluation places, folding automorphism, encoder,
   target-word map, local tests, list-recovery radius, source unranking, exceptional cases,
   and independent elliptic verifier.
2. Encode every factor point target-independently and certify all fold orbits and collisions;
   prove the local-test/addition biconditional without materializing pair or five-source
   incidence tables.
3. For known public `R_j=[r_j]P`, compute the frozen received word, run complete folded AG
   list recovery, map every accepted codeword to exact signed factor points, and
   independently verify every five-point elliptic sum.
4. Preserve misses, false lists, duplicate codewords, and ambiguities; collect exactly
   `B+sigma` verified source rows whose coefficient matrix has rank `B` modulo `N`.
5. Solve every factor-base logarithm and independently verify
   `[log_P(F_i)]P=F_i` for all `i`.
6. Freeze all encoder/decoder state, choose fresh public masks `t`, and apply the identical
   target-word map and list-recovery decoder to blind targets `Q+[t]P`.
7. Substitute verified factor logs, subtract `t`, enumerate every list-derived scalar
   candidate, and accept only `x` satisfying `[x]P=Q`.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` expected group operations with constant-state memory;
BSGS costs `N^(1/2+o(1))` time and memory. Set `B=L=N^ell`. Let the AG curve, places,
folding, encodings, and decoder setup cost `L^(s+o(1))` time and `L^(s_m+o(1))` peak
memory. Let one complete target-word computation, interpolation/root finding, entire list,
source output, and verification cost `L^(alpha+o(1))` time and `L^(m_q+o(1))` memory.

Unless a proved encoder changes density, use `pi=min(1,L^5/N)`. In the sparse regime,

`T_rel=N*L^(alpha-4+o(1))`

and

`T_desc=N*L^(alpha-5+o(1))`.

Sparse linear algebra costs `L^(2+o(1))` time and at least `L^(1+o(1))` memory. Hence

`lambda=max(s*ell,1+(alpha-4)*ell,2*ell,1+(alpha-5)*ell)`

and

`mu=max(s_m*ell,m_q*ell,ell)`

For `ell=1/5`, strict time below rho requires `alpha<3/2`; promotion
`lambda,mu<=0.45` requires `alpha<=1.25` and `s,s_m,m_q<=2.25`. Block length,
alphabet bit cost, genus, extension degree, interpolation matrices, root-finding branches,
complete list size, failed targets, source output, rows, factor logs, and verifier work are
charged. A length-`L^c` received word or list contributes exponent `c`.

## Likely fatal obstruction

AG list recovery assumes that a received word already agrees with evaluations of a low
degree function at many places. A generic elliptic target supplies only one group element,
not those local symbols. Constructing a received word whose nearby codewords are exactly
the target's source tuples appears to require evaluating the same source-incidence fiber
that the decoder is meant to avoid. Arbitrary factor-base predicates are not closed under
elliptic addition, and a bounded decoder list may fail under the many valid source tuples
needed for rank.

## Proof track

Prove a uniform factor-point encoder, target-computable received word, addition/local-test
biconditional, bounded complete source list, and the full seven-step relation, rank,
factor-log, blind-descent, output, field-operation, and peak-memory bounds.

## Disproof track

Show no target word can be computed without source incidence, exhibit valid source tuples
outside every decoder list, prove list size or word length is `Omega(L^2)`, or derive
complete time or peak-memory exponent at least `1/2`.

## Positive and negative controls

- Positive coding control: published folded AG instances with planted codewords, controlled
  errors, and complete list recovery.
- Positive source control: a planted homomorphic code where target words are genuinely
  computable and source labels are blinded from the decoder.
- Negative controls: random factor predicates, random received words, excessive-list
  instances, and encoders lacking addition compatibility.
- Mechanism controls: Guruswami-Sudan parameter sweeps, folded-code substitutions after
  incidence materialization, coordinate classifiers, P1434 joins, SAT, and Groebner bases.
- Leakage control: permute factor-point scalar labels while preserving codewords and public
  point data; output must track points only.
- Baseline control: matched Pollard rho and memory-matched BSGS.

## Quantitative promotion and falsification gates

This rejected lane cannot reopen without an encoder theorem proving the target-word/source
biconditional, bounded complete list, and symbolic `lambda,mu<=0.45`. A future toy
preflight must cover at least 20 ordinary curves per size across four increasing sizes,
exhaustive codeword/source truth through 18 bits, at least `1,000` verified relations and
`100` blind descents at each of the two largest sizes, exactly `B+sigma` retained rows of
rank `B`, zero source omissions/errors, and upper 95% bounds `lambda<=0.45` and
`mu<=0.45` including full word and list output. Falsify on one stable source omission,
target word requiring hidden incidence, or a proved or lower-95% complete bound
`lambda>=0.50` or `mu>=0.50`.

## Artifact plan

- Encoder/source theorem gate: `ideas/artifacts/ECDLP-IDEA-130/encoder_source_gate.md`
- Frozen code specification: `ideas/artifacts/ECDLP-IDEA-130/folded_ag_code.yaml`
- Prospective list-recovery driver: `ideas/artifacts/ECDLP-IDEA-130/list_recover_sources.sage`
- Independent list/source verifier: `ideas/artifacts/ECDLP-IDEA-130/verify_decoder_sources.py`
- Prospective receipts: `ideas/artifacts/ECDLP-IDEA-130/runs/<run-id>/`
- Complete analysis: `ideas/artifacts/ECDLP-IDEA-130/analysis.md`

## Interpretation boundary

This merged/rejected record is toy, heuristic, model-bound, and novelty-unverified. A
folded code, decoded codeword, bounded toy list, exact local test, valid relation, full-rank
toy matrix, verified factor log, or recovered toy scalar is not a better-than-rho result or
a breakthrough. Without an addition-compatible source encoder, list recovery is only a
solver substitution.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-130/encoder_source_gate.md` proving either a target-computable folded-AG received-word/source biconditional with symbolic `lambda,mu<=0.45` or an explicit incidence/list-size lower-bound obstruction.
