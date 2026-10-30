# Independent specialization, extraction, and cost review

2026-10-26 · TASK-20261026-e48b18 · joint `specialization-extraction-cost`

## Scoped verdict

**INCONCLUSIVE for theorem applicability or attack readiness; scoped acceptance of the source's boundary labeling.** Static inspection found that the native source keeps the symbolic result separate from group interpretation, leaves reduction and extraction `not_requested`, enumerates the required symbolic phases, and preserves the original reach-cost and verified-current-IC-improvement requirements as unresolved. That is the strongest conclusion available without a scientific or differential call.

The review does not certify a Coppersmith root-recovery theorem for this six-variable object. Ryan's Lemma 7 is heuristic and conditional, its polynomial-time statement excludes final root recovery, and the native panel performs neither lattice reduction nor extraction. Finite-field specialization, degree/leading-term/pivot preservation, group lifts, subgroup relations, usable independent equations, extraction, and fully charged end-to-end cost remain open.

This verdict covers only the assigned joint. It is not a whole-claim verdict and does not compose the sibling normalization joint.

## Exact counterexamples and controls

### An x-only zero does not identify a signed group relation

The native control source fixes, over `F_101`,

```
P=(1,39), T=(3,6), R=(41,15),  R=P+T.
```

It also checks `S(1,3,41)=0 mod 101`, computes `Q=2R`, and requires `Q` to be finite (`src/model.hpp`, immutable crypto commit `1d479882…`, lines 170-192). Therefore the all-positive lift is an exact counterexample to the implication “x-polynomial zero implies this signed relation”:

```
S(x(P),x(T),x(R)) = 0,
P + T + R = 2R = Q != O.
```

Only the sign choices compatible with the actual group law can be relations. The source correctly prints every sign triple separately and assigns no subgroup. A future report must not turn an x-only zero, a support match, or a symbolic `delta_star` into a group relation.

The corruption control is also exact. Direct substitution gives

```
S(1,3,41) = 4545 = 45 * 101,
S(1,3,41) + 1 = 4546 = 1 mod 101.
```

The constant monomial was already present, so `F1+1` has the same support but fails the planted root. The source rejects it at `model.hpp:189-190`. This meets the assigned proves-too-much check at source level. It does not replace a later supervised control run.

### The formal object has explicit invalid finite specializations

The source freezes `a=2,b=3` but has no finite modulus in a symbolic cell (`model.hpp:17-49`). For the intended short Weierstrass curve,

```
4*a^3 + 27*b^2 = 4*8 + 27*9 = 275 = 5^2 * 11.
```

Thus `p=5` and `p=11` are explicit invalid finite specializations: the discriminant vanishes and the group interpretation is unavailable. The symbolic native pipeline cannot reject them because `p` is a polynomial variable. The producer's transfer assessment correctly lists `p>3` and nonzero discriminant as future predicates. This counterexample is a boundary on applicability, not evidence of a defect in formal-`p` computation.

No panel output exists from which to exhibit an actual final-shift denominator or leading coefficient that vanishes at a permitted finite prime. That is an exact unresolved obligation rather than a pass: after a finite `p` is selected, every final-shift rational denominator must be invertible, and every stripped leading coefficient and constant pivot used by the symbolic construction must survive specialization.

## Primary-source comparison

I verified and read the full 52-page Ryan primary PDF, `/tmp/ryan-eprint-2024-1577-v20250716.pdf`, SHA-256 `15dd6ae6b939c51f3bc124097f954bd858ef47e4739037381fb4951f0366043f`. Relevant obligations are:

- Section 6.1, PDF page 19: symbolic fraction-field substitution requires all denominators in `S` to be coprime to the known modulus multiple `N`.
- Sections 6.4-6.6, PDF pages 22-24: Algorithm 3 uses suitability, symbolic ideal/shift construction, discrete shift statistics, interpolation, and Lemma 7. The construction remains sensitive to the selected `M_vert`.
- Lemma 7, PDF page 23: `S1` must have the shared modular root; Heuristics 1 and 2 are assumed; substituted values must be proportional to `p`; `p` must be sufficiently large; the bound is strict, `delta < delta_star - epsilon`; and `log p` must dominate the stated lattice-dimension expression.
- Heuristic 1 requires the ideal of recovered integer polynomials to have zero-dimensional variety. Heuristic 2 requires the interpolated dimension/determinant functions to be polynomials of bounded total degree. Finite interpolation and a degree check do not prove either heuristic globally.
- Appendix C, PDF pages 48-51: the asymptotic cost argument includes shift construction and lattice reduction but explicitly excludes final root recovery. It also needs the growth condition on `log p` to discard the lattice-reduction error term.

The native formula is statically aligned with the pinned cuso specialization for this restricted case: `exact.hpp:466-483` forms `k*s_dim-s_C/mu`, divides by `sum_i weights_i*s_x_i/mu`, cancels the polynomial gcd, rejects zero or unequal-degree limits, and takes the exact leading-coefficient ratio. `pipeline.hpp:181-231` interpolates at `k=1,...,d+3`, enforces the declared degree caps, applies the strict `1/r` domain cap, and labels the full-tree conversion as not being a joint-feasibility certificate.

That alignment certifies no theorem assumption. In particular:

1. No shift set has been constructed, so shared-root, suitability, denominator, coefficient-height, leading-term, pivot, and ideal/span preservation have not been observed.
2. The fixed centers are constants in the prospective fixture. Transfer to centers or curve coefficients that scale with `p` needs a fresh height analysis; the current asymptotic `s_C` treatment covers formal modulus powers, not arbitrary growing public coefficients.
3. Heuristic 1, Heuristic 2, sufficiently-large-`p`, and the `log p` growth condition remain assumptions even after a native/reference equality check.
4. The computed object would be a symbolic asymptotic bound. It would not by itself establish a finite root, an extractable system, or a group relation.

## Source and stage audit

The owner source was read from immutable commit `1d47988261c4d13f7a8549d70f53571163246c77`; all 77 paths in the producer manifest independently matched their recorded SHA-256 values. Current working-tree integrations were not used as source evidence.

| Obligation | Status | Evidence and limit |
| --- | --- | --- |
| Primary Ryan source | verified complete | 52 pages read; Algorithm 3, Lemma 7, Section 6.1, and Appendix C checked directly. |
| Symbolic formula | statically matched | Native numerator, denominator, cancellation, degree failure, and strict cap agree with pinned cuso's restricted no-`t` formula. No cell ran. |
| Denominator specialization | unresolved | `pipeline.hpp:232-245` records final rational denominators and the obligation `gcd(D,p)=1`; it does not and cannot verify a future `p`. |
| Leading term / degree / pivot specialization | unresolved | Full `S`, matrices, and pivot trace would be retained, but no finite evaluation or native/reference certificate exists. |
| Group interpretation | boundary verified | Exact F_101 counterexample above; nearby objects have no group oracle; source claims symbolic completion only. |
| Corrupted and same-support objects | source check verified | `F1+1` evaluates to `1 mod 101`; support alone is insufficient. The supervised control remains not started. |
| Reduction and extraction | correctly absent | Every slot says `not_requested`; Ryan's final root recovery is outside Lemma 7's polynomial-time claim. |
| Symbolic phase coverage | implemented prospectively | Ideal power, Gröbner basis, domain, FIFO closure/echelon, augmented polytope, discrete convolution, interpolation, limit, and failure checkpoint are explicit phases. |
| Cost coverage | partial | Per-call cgroup `cpu.stat`, memory peak/events, wall time, exit/failure/censorship are planned. Per-phase `std::clock` excludes Singular/cdd children and is labeled worker-only. No actual cost exists. |
| Reach-cost and current IC improvement | unresolved | No bound, reduction, extraction, group verification, baseline, rho comparison, or independent replay exists. |

The constant-pivot implementation agrees with the installed Sage 10.9 source: first available nonzero constant pivot, row normalization from the pivot column, elimination from every other row, and refreshed constant entries. Sage maps `wdeglex` to Singular `Wp`. These are static source findings plus bounded structural fixtures, not whole-pipeline equivalence.

## Fully charged cost boundary

The prospective source retains every symbolic stage that the task named. The supervisor places the worker and descendants in one cgroup, records whole-call CPU and memory, kills the full tree on timeout, and serializes calls. The control worker is an additional charged process containing four `(r,mu)` constructions and must remain separate from the 24 bound workers.

Any later reach-cost statement must charge, for every attempted cell including failures and censorship:

1. admission and control work;
2. exact expansion, ideal-power generation, Gröbner basis and normal forms;
3. cdd conversion and integer-point enumeration;
4. FIFO closure, echelon intersection, augmented hulls and discrete convolutions;
5. interpolation, limit, specialization checks, and archive/verification overhead;
6. lattice construction and reduction;
7. root extraction, candidate verification, y-lifts/sign resolution, subgroup and target checks;
8. relation handling, later linear algebra/final scalar recovery, and any failed attempts;
9. cold setup and separately justified amortized reuse.

Call-level cgroup CPU/memory can supply the fully charged total even while child CPU remains unavailable per phase. A phase breakdown must either capture child user/system CPU or keep that field explicitly null. `tau_cuso=0` is a no-`t`-shifts parameter and is not an attack-cost exponent.

## Smallest next acceptance test

The smallest repair is a two-part, fail-closed verification after a concrete finite instance and a separately authorized non-scientific differential fixture exist:

1. **Specialization certificate.** Bind prime `p`, curve/subgroup/target IDs, centers, bounds and exact `S`. Require `p>3`, `p` prime, `p` not dividing `275`, injective bounded windows (or deduplicated density), and `gcd(D,p)=1` for every recorded denominator. Evaluate all symbolic coefficients at `p`; recompute stripped leading monomials/coefficients and the constant-pivot trace; require every needed coefficient/pivot nonzero and certify that the evaluated rows preserve the intended ideal/span. Any failure invalidates that cell.
2. **Pinned semantic equality fixture.** On the smallest separately approved algebra fixture, compare native and pinned cuso/Sage outputs byte-for-byte or as exact ordered objects for reduced basis, normal forms, `M`, `M_bar`, `S_bar`, `S`, row operations, valuations, interpolation polynomials, cancellations and final ratio. A compiler pass or ideal equality is insufficient.

Before any attack/reach claim, additionally record Ryan's Heuristics 1 and 2, suitability, shared-root modulus, coefficient-scaling and `log p` growth assumptions; run the planted/corrupted controls; produce enough independent recovered integer equations; complete and verify extraction; and report the fully charged cost above. Before any IC-improvement claim, bind the named frozen current prime-field IC baseline, matched curve/subgroup/target identities and resources, verified answers, matched rho gap, independent replay, and a valid progress-fidelity record.

## Commands and provenance

Read-only commands used for this review included:

```text
sha256sum /tmp/ryan-eprint-2024-1577-v20250716.pdf
pdfinfo /tmp/ryan-eprint-2024-1577-v20250716.pdf
pdftotext -layout /tmp/ryan-eprint-2024-1577-v20250716.pdf /tmp/ryan-eprint-2024-1577-v20250716.txt
git -C /workspace/crypto-native-smallroot show 1d47988261c4d13f7a8549d70f53571163246c77:<path>
git -C /workspace/cuso show fb2747d2105a8e48499bf10a3a717cf80c14d079:<path>
sed -n <range> /workspace/skeleton_sage-runtime/lib/python3.12/site-packages/sage/{matrix/matrix_mpolynomial_dense.pyx,rings/polynomial/term_order.py}
```

The manifest check streamed each of its 77 paths through `git show` and `sha256sum`; all matched. No ideal, bound, reduction, extraction, parameter search, or other scientific call was made.

Invocation identity: published task claim owner `reviewer-native-specialization`, session `native-smallroot-specialization-20261026`, epoch 1, programme commit `872112b912f8b6d4d5a6a34b6be4a3eba17da614`, PR 2594. Configured selection was backend `openai`, policy `review-adversarial`, native model `gpt-5.6-sol`, reasoning effort `xhigh`, fresh independent `fork:none`; fallback was false and degraded requirements were empty. This records the task's actual native selection and resolution. It does not assert a new API catalogue probe or current serving-metadata attestation.

Mutual blindness was preserved. No file under sibling task `TASK-20261026-391e68` was read.
