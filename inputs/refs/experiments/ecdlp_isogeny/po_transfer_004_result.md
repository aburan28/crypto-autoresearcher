# PO-transfer-004 Result: Plucker Incidence Compression Gate

## Claim Or Task

Test whether BNIT's target-plus-four-cover-point co-cubic condition exposes a
non-random finite-projective incidence structure or a concrete pair-table query
algorithm that materially compresses relation generation.

## Status

`NEGATIVE RESULT / TOY-EVIDENCE / MODEL-BOUND / CONTROLLED-INSTANCES`

The Plucker reformulation is an exact public relation gate, and accepted rows
recover the original elliptic target on seven curve labels somewhere in the
factor-base sweep.  It is not a useful compression algorithm in this model.
The measured pair sets match the random Klein-quadric null, every normalized
pair plane is unique, brute orthogonality loses badly to rho, and even the
unimplemented ideal-oracle floor has an adverse toy exponent and remains above
rho.

This closes `TRANSFER-H002` only for the tested quotient representation and
accounting model.  It does not rule out a different correspondence, a
target-lift family with useful coset freedom, or a genuine sub-pair-table
incidence data structure with independently proved cost.

## Restricted Theorem Used By The Gate

Let

```text
m(P) = (1, x, x^2, x^3, y)
```

and fix a target cover point `T`.  Subtracting `m(T)` gives quotient vectors
`w(P)` in `W_T ~= F_p^4`.  For four cover points with five distinct
`x`-coordinates including the target,

```text
target plus P1,P2,P3,P4 lie on a graph cubic
iff (w1 wedge w2) wedge (w3 wedge w4) = 0.
```

In Plucker coordinates `(z12,z13,z14,z23,z24,z34)`, the exact bilinear form is

```text
B(z,r) = z12*r34 - z13*r24 + z14*r23
       + z23*r14 - z24*r13 + z34*r12.
```

Shared factor-base indices, zero bivectors, repeated abscissas, and the three
pairings of one four-point set are filtered explicitly.  Orthogonality is a
hyperplane-incidence query, not an equality hash.

For a random decomposable bivector over `F_q`, the exact matched null rate is

```text
rho_K = (q^3 + 2q^2 + q + 1) / ((q^2 + 1)(q^2 + q + 1)) ~= 1/q.
```

## Experiment

- Four frozen BNIT curves and four preregistered fresh curves.
- Three factor-base sizes per curve, for 24 configurations total.
- Public target lifts generated only from `-lambda*Q`; fresh `Q` values are
  deterministic public curve points outside the factor base, with no fixture
  discrete logarithm constructed or consumed.
- Exact pair-pair enumeration with shared-index rejection.
- Cubic interpolation and residual replay for every candidate incidence.
- Direct rows and one-large-prime cancellation followed by public rank solve.
- One squarefree production-path divisor control per configuration, planted
  around four actual factor-base lifts.
- Five hundred matched random-vector/Klein controls covering every target and
  configuration, with eight replicates on each base cell's first target.
- Separate charged brute work and `ideal_oracle_ops`; the latter omits query
  cost and is not an implemented algorithm.

Reproduction:

```bash
HOME=/private/tmp/codex-sage-home sage experiments/ecdlp_isogeny/po_transfer_004_plucker_incidence_gate.sage \
  --out experiments/ecdlp_isogeny/po_transfer_004_result.json

HOME=/private/tmp/codex-sage-home sage experiments/ecdlp_isogeny/po_transfer_004_verify.sage \
  --input experiments/ecdlp_isogeny/po_transfer_004_result.json \
  --out experiments/ecdlp_isogeny/po_transfer_004_verify.json
```

## Base-Cell Results

| Cell | B | Incidence / exact null | Incidence / random control | Rank | Charged / rho | Oracle floor / rho | Memory / sqrt(n) |
|---|---:|---:|---:|---:|---:|---:|---:|
| frozen `p=101` | 8 | 1.110 | 1.150 | 8/8 | 15609.06 | 245.47 | 149.76 |
| frozen `p=211` | 10 | 0.927 | 0.886 | 10/10 | 50742.37 | 451.81 | 200.61 |
| frozen `p=431` | 12 | 1.013 | 1.042 | 12/12 | 57420.39 | 328.75 | 170.17 |
| frozen `p=4099` | 16 | 1.003 | 0.920 | 10/16 | 115587.62 | 351.66 | 75.13 |
| fresh `p=103` | 8 | 1.002 | 1.122 | 8/8 | 8652.33 | 132.67 | 114.59 |
| fresh `p=223` | 10 | 0.975 | 0.917 | 10/10 | 32850.62 | 290.91 | 162.19 |
| fresh `p=439` | 12 | 1.018 | 1.037 | 12/12 | 62652.06 | 357.41 | 172.16 |
| fresh `p=4127` | 16 | 0.960 | 0.931 | 1/16 | 65049.77 | 229.54 | 68.28 |

Across base cells, incidence excess is `0.927..1.110` versus the exact null and
`0.886..1.150` versus target-matched controls.  There is no
persistent fresh-cell excess.  The large frozen cell reaches `18/18` only after
raising `B` to 18; the large fresh cell remains `4/18` at the same sweep point.

The toy fits are:

| Metric | Fitted exponent in group order | Interpretation |
|---|---:|---|
| charged brute work | 0.958 | adverse; optimistic field-op proxy already far above rho |
| ideal-oracle floor | 0.561 | unimplemented and still above the `0.5` target |
| recorded memory entries | 0.293 | exponent alone hides a `68.3..200.6 sqrt(n)` base-cell constant |

At the shared frozen `p=4099`, `B=16` anchor, charged PO4 work is `208.25x`
the BNIT `003c` kernel count.  The oracle floor is `0.634x` that count, only a
`1.58x` diagnostic reduction rather than the required `16x`, and rank is only
`10/16`.

## Verification

`po_transfer_004_verify.json` reports `VERIFIED` for all 24 configurations.
It independently reconstructs factor bases and target lifts, re-enumerates the
Plucker counters and all 500 random controls, replays 2,973 primitive cubic
witnesses underlying 1,603 public final rows, recomputes large-prime
cancellation, matrix rank, and every public `kG=Q` recovery.  No public relation
or cancellation failed.

## Contract Decision

| Criterion | Decision | Evidence |
|---|---|---|
| public recovery on at least three sizes | pass | seven labels recover somewhere in the three-`B` sweep |
| concrete measured incidence data structure | fail | only exact pair-pair enumeration exists |
| at least `16x` fewer kernels than BNIT | fail | anchor is `208.25x` worse; oracle floor improves only `1.58x` |
| memory below `4 sqrt(n)` | fail | base cells use `68.3..200.6 sqrt(n)` entries; every configuration exceeds the gate |
| persistent incidence/rank excess | fail | exact-null and random-control ratios straddle one |
| charged work below rho | fail | no configuration is below rho |
| fitted exponent at most `0.5` | fail | charged `0.958`; oracle floor `0.561` |

The experiment gate is therefore `success=false`.

## Red-Team Repairs

The final artifact incorporates the independent red-team findings:

- fresh targets no longer come from known fixture scalars;
- every planted control uses four actual factor-base lifts and replays through
  the production relation function;
- matched random controls cover every target and factor-base configuration;
- the JSON gate exposes every structural and algorithmic contract clause;
- `charged_actual_ops`, `ideal_oracle_ops`, and `memory_entries` remain labeled
  optimistic proxies, not exact field-operation or byte counts.

These repairs strengthen the negative result.  They do not create a speedup.

## Reusable Negative Lemma

For the tested BNIT quotient vectors, explicit Plucker orthogonality does not
compress co-cubic relation search.  The pair table has no repeated-plane signal,
nontrivial incidences occur at the matched random Klein rate, and relation
supply needs the expected pair-table scale.  Any follow-up that keeps the same
vectors must identify and charge a real orthogonal-incidence data structure;
renaming the predicate as a hash or oracle is invalid.

## Next Positive Question

What auxiliary representation exposes a genuinely cheaper solver rather than
only more names for the same pushed-forward tuples?  The next candidate is a
trace-quotient lift into `E(F_{p^m})`.  Trace-fiber multiplicity itself collapses
exactly to weighted `k`-sum on `Tr_m(S)` and receives no credit.  `PO-transfer-005`
instead asks whether Weil-restricted extension coordinates expose low-degree or
sparse algebraic solving that finds those image-valid tuples faster after
extension arithmetic, image-column deduplication, rank, and target descent are
all charged.

## Artifact Paths

- `research/PO_transfer_004_contract.md`
- `experiments/ecdlp_isogeny/po_transfer_004_plucker_incidence_gate.sage`
- `experiments/ecdlp_isogeny/po_transfer_004_result.json`
- `experiments/ecdlp_isogeny/po_transfer_004_verify.sage`
- `experiments/ecdlp_isogeny/po_transfer_004_verify.json`
