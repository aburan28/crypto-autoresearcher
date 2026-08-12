# TASK-20260724-303 — adversarial notes on toy validation protocol

## Scope

Independent review of the immutable TASK-20260724-301 package archived by
TASK-20260724-302 at commit `5a3a629dd9bd938e010bd8580bab93303be4e2c7`.
This note reconstructs attack points against the protocol design; it does not
implement a verifier, run an experiment, or authorize either.

## Snapshot and runtime gates (before interpretation)

- Recomputed producer SHA-256 values match the snapshot receipt and the Git
  blobs at `5a3a629`:
  - `toy_validation_protocol.yaml` →
    `a43237b1d835065b7473ff030ad9e01c2b4474715a69158d62efceed7c2c9907`
  - `fixture_schedule_verifier_bindings.md` →
    `ed05f2f5d3a6665c49db82d154a7451bb8774853128b1a8349efa5e1ddafcc69`
- Commit changes exactly those two producer paths plus the snapshot receipt;
  message cites TASK-20260724-302/301, GOAL-ECDLP-001, BATCH-003,
  DEC-20260722-005, and DEC-20260724-007; first parent is `d34843b`.
- Producer inference matches DEC-20260724-007 (`research-sol-max` →
  `cursor-grok-4.5-high-fast`, `fallback_used: true`).
- This review session used the same auditable Grok fallback under
  DEC-20260724-007; equivalence to `review-xhigh` is not claimed.
- Attestation: this reviewer did **not** originate the producer artifacts.

## Fixture recomputation (p=53, a=1, b=0, G=(6,13), ℓ=17)

Independent short-Weierstrass arithmetic over \(\mathbb F_{53}\):

- 53 and 17 are prime by trial division up to \(\sqrt{n}\).
- Affine points on \(y^2 = x^3 + x\): 67; group order including
  \(\mathcal O\): **68**; cofactor \(68/17=4\).
- \(G=(6,13)\) lies on the curve; \(17G=\mathcal O\); no smaller positive
  multiple is identity ⇒ \(\mathrm{ord}(G)=17\).
- Factor base: \(FB1=G\), \(FB2=2G=(24,42)\), \(FB3=3G=(13,14)\); each has
  \(17P=\mathcal O\); encodings `04060d` / `04182a` / `040d0e`.
- `point_sha256` recomputes as SHA-256 of the raw uncompressed SEC1 bytes
  (not the hex string). All three digests match.
- Fixture compact sorted-key JSON SHA-256 recomputes to
  `e9604173f1606052d4513e3d171bd0fe5abd0427c45f4b0018cb3309bc700088`.
- Linear-algebra field modulus 17 equals \(\ell\); coefficient width
  \(\lceil\mathrm{bitlength}(16)/8\rceil=1\).

Falsification of fixture completeness/correctness **failed**.

## Adversarial reconstructions attempted

### 1. Inflated or wrong curve order

If \(\#E(\mathbb F_{53})\neq 68\) or \(\mathrm{ord}(G)\neq 17\), the field
schema and row width would be dishonest. Independent enumeration and scalar
multiplication refute that attack for this concrete fixture.

### 2. Factor-base points off the subgroup

If any FB point failed \(\ell P=\mathcal O\) or left the curve, relation rows
over \(\mathbb F_{17}\) would be meaningless. All three points are on-curve
order-17 multiples of \(G\).

### 3. Post-hoc attempt minting / omitted work

Attempt IDs minted only at receipt time hide omissions. The template freezes
A0, A1, A0R1 with contiguous ordinals, unique seeds, and a finite acyclic
retry forest before any activation, and keeps
`verified_before_execution: false` until a Coordinator snapshot fills
precommit fields — consistent with contract 1.0.0-review for a design-time
template.

### 4. Probability-gate smuggling via \(r=0\) or \(p_L=0\)

With \(r>0\) and \(p_L=0\), \(n_\star=\infty\) and a finite schedule would be
invalid. Here \(r=0\Rightarrow n_\star=0\); scheduled \(n=2\) only exercises
bijection/retry activation and does not claim a positive-yield completion
budget. `ceil(r/p_L)` is absent. \(\alpha\) union bound holds
(\(0.025+0.025=0.05\)).

### 5. Retry cohort pollution

If retries counted in the probability cohort, yield estimates would be
outcome-conditioned. A0R1 has `probability_cohort_member: false` and
activates only on infrastructure/timeout terminals — consistent with the
contract.

### 6. Verifier digest theater

A digest of prose that does not bind the algorithm list or contract version
could be swapped later. Recomputed stub digest over the declared field set
matches `3d74cde9…b8d7` and binds schema/version plus
`implementation_authorized: false`. Residual: stub is not an executable;
campaign PASS still requires a later concrete artifact re-seal.

### 7. Illicit group-op scalarization / double-count

Cross-type summing into one scalar is forbidden by the frozen vocabulary and
matches contract `no_scalarization`. Residual: `SCALAR_MUL_BIT` versus
`AFFINE_ADD`/`AFFINE_DOUBLE` needs an exclusivity rule before counting is
operationally unambiguous.

### 8. Claim inflation

The package repeatedly bounds itself to toy protocol design. No route turns
this PASS into an ECDLP attack improvement, lower bound, crypto-scale result,
or breakthrough. Implementation and experiment remain unauthorized.

## Non-blocking residuals

1. Standalone JCS schedule with contract-required `field`, `column_schema`,
   `canonical_row_format`, `initial_matrix` schema digests, `schedule_sha256`,
   and filled precommit snapshot fields is still required before activation.
2. Spec-only verifier stub must be replaced and re-sealed for any campaign
   certificate.
3. Resource ownership placeholders beyond wall/cpu caps (exclusive/shared
   work registries) and a `SCALAR_MUL_BIT` exclusivity rule remain for the
   future freeze.
4. Protocol text should state the observed `point_sha256` rule
   (`sha256(raw encoding bytes)`).

These residuals block activation, not this design-stage PASS.

## Independence

This reviewer originated none of TASK-20260724-301, its artifacts, or the
TASK-20260724-302 snapshot.

## Verdict

`PASS` — DEC-20260722-005 protocol pins are discharged at review-only design
level. Authorize no implementation or experiment.
