# R4 — null adequacy, the nearby object, the s = 1 slice identity, and the named confounds

TASK-20260904-0d66e3 (red team), EXP-PFDR-20ee58. Computed values from
`r1_r4_checks.py` → `r1-r4-checks.json` and `r0_regenerate.py` →
`r0-regeneration.json`. Meter snapshot `2d2083e5`.

## (a) NULL-TOPOLOGY versus NULL-SUPPORT — what the topology null adds

The topology null draws uniform coefficients (zero allowed) on the whole
degree-bounded "box" of each generator: monomials multilinear in the generator's
own digit blocks with per-block degree ≤ 2 and u-exponent ≤ 2, total degree ≤ 4.
I computed the box sizes from that definition and compared with the realised
supports:

| s | box(E1) | realised terms E1 | extra monomials | box(E2) | realised terms E2 | extra |
|---|---|---|---|---|---|---|
| 3 | 111 | 98 | 13 | 21 | 21 | **0** |
| 4 | 243 | 218 | 25 | 33 | 33 | **0** |
| 5 | 468 | 427 | 41 | 48 | 48 | **0** |
| 6 | 822 | 761 | 61 | 66 | 66 | **0** |

This reproduces the executor's anomaly A4 and quantifies it: **at E2 the
topology null is the support null**, differing only in the coefficient law
(support-matched draws uniformly *nonzero*, topology allows zero). At E1 it adds
11.7 % more monomials at s = 3, falling to 7.4 % at s = 6. The realised
generator degrees were [4, 4] in every draw of both null arms (R0), so the two
arms did not even differ in degree. **NULL-TOPOLOGY is therefore not a distinct
control at E2 at any tested s, and is a near-duplicate of NULL-SUPPORT at E1.**
Since the topology null's five seeds all returned 0, the "null band" used for
the residual and for the curve-spread and p-ladder comparisons has width exactly
0 by construction, so those comparisons reduce to "is the SEM value exactly 0"
rather than to a statistical test. That is a scope statement, not an error; but
"inside the null band" should not be reported as if a band had been estimated.

## (b) D3 — five null seeds on one template

The executor generated the five nulls per (cell, arm) from curve 4101 / target 1
only, and asserted that the term counts of E1, E2 are identical across the six
curves so a repeat on another template reproduces the same null. **Confirmed
independently**: at s = 3, p = 4099 all six curves give term counts (98, 21) and
identical degree histograms `{0:1,1:7,2:15,3:33,4:42}` and
`{0:1,1:4,2:7,3:6,4:3}`; the six template records are byte-identical after
serialisation. The deviation is benign for the support-matched null. Its cost is
that the null arms carry no curve variability at all, which is the mechanical
reason the null band is width 0 (see (a)).

## (c) The nearby non-curve cubic — how nearby is it?

The S_3 coefficients A and B occur **only in monomials of total degree ≤ 3**:
`top(E1) = (x1-x2)^2 u^2 - 2 x1x2(x1+x2) u + x1^2x2^2` and
`top(E2) = u^2 x3^2` are independent of A and B. I verified this directly: the
degree-4 parts of the generators built from the generic curve (2975, 3349) and
from the singular cubic (1915, 2403) are equal, monomial for monomial. So the
NEARBY-NON-CURVE-CUBIC arm perturbs only sub-leading coefficients, and its
generator shape is identical except for one vanishing term (20 terms in E2
instead of 21). It is about as *near* as a nearby object can be, which is a
strength for detecting a leading-form effect and a weakness for detecting a
curve-arithmetic effect. **With every arm at 0 it discriminates nothing**: all
four arms — SEM, both nulls, the non-curve cubic — and an ordinary random
quartic pair I drew myself (`r2-sensitivity.json`, object N) return the identical
`[0, 0, 0, 0]`. The SEM measurement is a **controlled null**: indistinguishable
from a random quartic pair on the reported quantity.

## (d) CTRL-S1-SLICE — identity holds; the fixture is usable; the embedding is off-axis

- The recorded generator list at (p = 4099, B = 4) is, in order,
  `S_3(x1,x2,u)`, `S_3(u,x3,xR)`, `fV(x1)`, `fV(x2)`, `fV(x3)`, which is
  IDEA-20260830-cb8e46's J verbatim (that record, line ~39: "the resultant-tree
  encoding J = (S_3(x_1,x_2,u), S_3(u,x_3,xR), fV(x_1), fV(x_2), fV(x_3)) in
  F_p[x_1,x_2,x_3,u], where u is NOT constrained to V"). The membership
  generators render as `x^4 + 4093x^3 + 11x^2 + 4093x = x(x-1)(x-2)(x-3)` mod
  4099, i.e. `fV` for the interval base V = [0, 4), as the contract specifies.
  `same_ring: true`, `per_generator_equal: [true × 5]`. **P5 holds.**
- The fixture (`stage2-s1-fixture.yaml`) records the identity statement, the
  generator order, the rendered generators, the certificate and both
  conventions' graded ranks for six (p, B) cells, and names its source raw
  record with a sha256. It is usable by a future instrument. There is indeed no
  instrument to compare against today, which the contract's forced disposition
  already concedes.
- **Off-axis embedding (recorded, not a defect).** The s = 1 slice runs in
  ORDINARY mode (four free variables, explicit membership generators
  `fV`) at d = B ∈ {4, 8}, while every measured arm runs in MIXED mode
  (squarefree digits + free u, membership absorbed into the quotient) at d = 2.
  So the "baseline embedding" reproduces cb8e46's encoding, not the instrument
  configuration the twin values come from; the twin's own d = 2 family at s = 1
  is a two-element window and degenerate. A boundary/strictness reading — "the
  old object is embedded as a limiting case of the new one" — is therefore not
  available on the tested axis, and the composition should not claim it.

## (e) Named confounds

- **Ideal-level reading.** The recorded `quotient.dimension` is 6–7 on SEM,
  0–1 on the support null, 0 on the topology null, 6 on the non-curve cubic,
  with `gcd_degree_histogram {0: 506, 1: 6}` over the 512 digit points — i.e.
  the count of grid cells where the two fibre polynomials share a root, exactly
  cb8e46's CRT/complete-splitting picture. It appears in `analysis.json` under
  `covariates` only. I re-read the branch rule in `analyze.py`: it uses the
  residual deficits and the D ∈ {5,6,7} SEM deficits and nothing else. **No
  ideal-level quantity enters a metric.** Confirmed.
- **No Gröbner degree.** `sol(D)` is `False` at every recorded (cell, arm, D)
  and is recorded as a covariate; no solving degree is read anywhere.
- **Degree convention frozen and identical across arms.** The
  `deficit_convention` block is byte-identical in all fourteen manifests
  (one hash, `ad4e950bfbdc`), it names the read field
  (`LayerResult.deficit_pairwise`, `convention='cumulative'`), and it discloses
  that the Frobenius term enters at p = 2 in the pure squarefree ring only.
  `zero_product_rows` is 0 on every twin draw, so the non-homogeneous reduction
  never dropped a row in any arm.
- **Two generators / far from overdetermined.** Contract confounder (iv) is
  correct and is exactly the point R2 quantifies: the trivial-syzygy budget at
  D = 8 is 1, against 78 at the calibration cell.

## Result

R4 **holds** as a validity matter: no null arm is mislabelled or unable to fail
in principle (my planted objects show the same meter, same convention, same
arms' configuration returning nonzero), no ideal-level reading enters a metric,
no Gröbner degree is read, the convention is frozen and identical, and the s = 1
identity with cb8e46's J is exact. Two scope findings stand: NULL-TOPOLOGY is
not a distinct control at E2 (and barely one at E1), and with every arm at 0 the
nearby-object arm discriminates nothing.
