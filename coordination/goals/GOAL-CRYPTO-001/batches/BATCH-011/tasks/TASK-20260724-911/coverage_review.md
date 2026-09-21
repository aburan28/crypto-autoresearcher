# BATCH-011 independent coverage review

Verdict: **REVISE**

## Exact supported claim

At committed producer snapshot
`5c8f04776665bf50503467a380c7c5bb0a233627`, none of the 17 enumerated
primary or authoritative source records is documented as simultaneously
supplying all twelve producer fields for an ordinary \(E(\mathbb F_p)\)
large-prime-order ECDLP. Independent spot checks found no contrary candidate
among the torsion, Frobenius, endomorphism, dynamic-factor-base,
summation-polynomial, hyperplane, quasi-subfield, and structured-generic-model
sources checked here.

That statement is only a no-pass disposition over enumerated and spot-checked
records. It is not exhaustive literature coverage, an impossibility result, or
cryptographic evidence.

Candidate verdict:
`NO_EXPERIMENT_READY_TYPED_CANDIDATE_IN_RECORDED_SET`. Retain the result only
with the narrower wording above. Novelty remains unverified because there is no
admitted candidate to compare.

## Snapshot integrity

The snapshot is reachable from review `HEAD` and changes exactly the producer's
two artifacts plus the snapshot receipt. The artifact SHA-256 values match the
receipt:

- `literature_audit.yaml`:
  `ae7e3ac24131f9ce85bc2a2c362b0e3c230d101d14af5b147a1a31d442fbbaed`
- `typed_candidate_note.md`:
  `543786b9dc6eac48f06c7c45d67d0af003a2b524fdf811c683d99acca9cb7677`

The committed receipt itself still records `pending_post_commit` with null
commit metadata. Independent Git checks establish reachability and exact
scope, but the receipt was not post-commit finalized.

## Coverage and count reproducibility

All four exact OpenAlex URLs replayed on 2026-07-24:

| Query | Replayed total | Replayed first page | Producer |
|---|---:|---:|---:|
| prime-field ECDLP index calculus | 244 | 25 | 244 / 25 |
| summation-polynomial ECDLP | 560 | 25 | 560 / 25 |
| relation matrix automorphism endomorphism | 15 | 15 | 15 / 15 |
| point decomposition index calculus | 4,917 | 25 | 4,917 / 25 |

Thus the OpenAlex aggregate of 90 displayed records reproduces. The reported
relevance labels \(4,2,0,8\) do not: no coding rubric or work-level decisions
were retained, and ranking can change because no raw response or cursor was
archived.

The 25 WebSearch strings are recorded, but the aggregate 122 cannot be
independently verified. There are no per-query displayed counts, ordered URLs,
stable IDs, raw responses, timestamps, provider identity, or hashes. “Every
displayed record was screened” is therefore unauditable.

The Crossref count is inconsistent with the recorded protocol. Four
`rows=3` title queries plus one direct DOI lookup describe at most
\(4\cdot3+1=13\) displayed records, not 15. Exact request URLs and responses
were not retained to explain a different count.

The stated IACR access interval ends at 2025-12-31 even though the audit claims
coverage through 2026-07-24. Google Scholar, MathSciNet, zbMATH, later OpenAlex
pages, exhaustive forward citations, and non-English literature remain access
gaps.

Coverage reproducibility verdict: `FAIL_AS_FULLY_REPRODUCIBLE`.

## Primary-source spot checks and corrections

- Faugère–Huot–Joux–Renault–Vitse, EUROCRYPT 2014,
  [DOI 10.1007/978-3-642-55220-5_3](https://doi.org/10.1007/978-3-642-55220-5_3):
  accessible IACR/HAL text supports the torsion-equivariant map, reduced
  factor base, extension-field regime, and \(m^{n-1}\) decomposition-probability
  penalty.
- Galbraith–Granger–Merz–Petit,
  [ePrint 2020/1315](https://eprint.iacr.org/2020/1315): the
  Frobenius-invariant factor base, \(1/n\) polynomial-system reduction,
  \(n^2\) linear-algebra saving, and \(E(\mathbb F_{q^n})\) scope are accurate.
  Independence of transformed relations is a condition, not an unconditional
  rank guarantee.
- Tsakou–Ionica,
  [ePrint 2021/721](https://eprint.iacr.org/2021/721) and TMC 1(2):
  “Effective Endomorphisms” is the preprint title; “efficient endomorphisms”
  is the journal title. The producer's journal citation is accurate. The
  factor-base orbit mechanism remains extension-field elliptic/hyperelliptic
  boundary evidence.
- Petit–Kosters–Messeng PKC 2016, Amadori–Pintore–Sala 2018,
  [McGuire–Mueller 2017/1262](https://eprint.iacr.org/2017/1262),
  [Mahalanobis–Mallick 2018/134](https://eprint.iacr.org/2018/134), and
  [Hu 2024/1923](https://eprint.iacr.org/2024/1923) have accurate metadata and
  broadly accurate mechanism classifications.
- Sakemi et al., DOI 10.1515/jmc-2019-0029, derives its lower bound under
  statistical assumptions and reports experiments only through 25-bit prime
  fields. It is a conditional baseline control, not unconditional evidence
  that a family is impossible.

The Kudo–Yokota–Takahashi–Yasuda CANS 2018 citation is confirmed by author and
institutional metadata, but primary chapter text remained inaccessible. A
related WCC 2017 item, “Practical Limit of Index Calculus Algorithms for ECDLP
over Prime Fields,” was found but not source-screened.

Relevant records present in replayed or cutoff-eligible coverage but absent
from `source_screen` are:

1. Huang–Kosters–Petit–Yeo–Yun, “Quasi-subfield Polynomials and the Elliptic
   Curve Discrete Logarithm Problem,” DOI 10.1515/jmc-2015-0049. It appeared
   on the first OpenAlex page and was directly queried through Crossref. Its
   ECDLP is over \(\mathbb F_{p^n}\), so it is not a target candidate.
2. Euler–Petit, “New results on quasi-subfield polynomials,”
   [DOI 10.1016/j.ffa.2021.101881](https://doi.org/10.1016/j.ffa.2021.101881).
   It appeared on the second OpenAlex page, reports no speedup, and is an
   extension-field/small-characteristic boundary source.
3. Corrigan-Gibbs–Henzinger–Wu, “The Structured Generic-Group Model,”
   [ePrint 2026/384](https://eprint.iacr.org/2026/384). It predates the cutoff
   and directly informs the oracle/generic-simulator comparison. It is a
   lower-bound framework, not a relation-action candidate.

These omissions do not produce a candidate, but they contradict the statement
that all relevant unique source families from recorded coverage are
enumerated.

## Admission and interface review

The twelve-field rule is appropriate for declaring an experiment-ready,
fully costed path. It is too strict for candidate discovery. Requiring one
paper to contain an adaptive transcript, certificate protocol, traffic,
verification, and matched-rho analysis rejects a mechanism because its
documentation is incomplete. Requiring an action generator also rejects
dynamic-factor-base and direct-solve mechanisms by definition. Discovery,
target-scope typing, and experiment readiness must be distinct labels.

The closest source interfaces are:

- **Torsion (SRC-08):** genuine factor-base and tuple action; extension-field
  only, bounded action, reduced decomposition probability, partial source
  recovery, no target-scope fresh descent or complete cost.
- **Frobenius (SRC-09):** genuine growing extension-field orbit action and
  representative rewrite; pointwise identity on \(E(\mathbb F_p)\), with
  conditional independent-rank savings and no ordinary-prime-field descent.
- **Endomorphism (SRC-10/SRC-11):** invariant orbit representatives and row
  rewrites in extension-field elliptic, transferred, or hyperelliptic groups;
  no target-scope end-to-end path. Available finite actions must also discount
  matched rho.
- **Prime-field summation (SRC-02):** typed factor base, signed Semaev
  relation, and \(aP+bQ\) target, but no useful relation action and unresolved
  yield/solver, replay, rank-tail, descent, memory, traffic, and rho cost.
- **Dynamic factor base (SRC-03):** target-dependent direct solve with one
  dependency, not reusable factor logs. This can be typed as a partial
  mechanism while still failing readiness.
- **McGuire–Mueller (SRC-04):** alternate relation-solving backend and
  challenge-dependent base, not a distinct source-faithful action.
- **Hyperplane (SRC-15):** the source/subset or initial-minor locator and
  complete cost remain unresolved; a “Las Vegas” title or toy examples do not
  establish matched-rho performance.

Across all action-bearing sources, orbit size does not establish independent
rank. None supplies fresh scalar-blind target descent, a complete adaptive
oracle transcript, or aggregate preprocessing, memory, traffic, and
verification costs. Exact relation equality alone is not a rank, replay, or
final-solution certificate.

Novelty/deduplication verdict: `UNVERIFIED`. The family labels are sensible,
but the package lacks a source-by-source semantic fingerprint tying each
exclusion to an exact prior record and interface equivalence.

## Baselines and scope

Pollard rho remains unbeaten at \(N^{1/2+o(1)}\) work and negligible serial
memory, with the same negation/automorphism quotient applied to both sides.
BSGS has \(N^{1/2+o(1)}\) work and memory. The closest specialized baselines
are the in-scope prime-field summation/direct-solve papers, sparse Wiedemann
after relation supply, and the adjacent torsion/Frobenius/endomorphism orbit
methods. None has a fully charged target-scope advantage.

No curve execution, key recovery, operational code, empirical solve, or
cryptographic-scale inference was performed.

## Exactly one final-batch action

Produce one coverage-repair addendum that archives per-query receipts,
reconciles the Crossref count, source-screens the omitted quasi-subfield and
ePrint 2026/384 records plus the Kudo/WCC access path, and reapplies a
two-stage discovery/readiness gate.
