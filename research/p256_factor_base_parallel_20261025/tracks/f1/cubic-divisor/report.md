# F1 continuation: reduced cubic-divisor membership on P-256

2026-10-25 · TASK-20261025-13c38e · exact implementation and solver-formulation
validation. This continuation completes the fixed k=3 membership+S4 target that
the original forward formulation left unknown. It also proves and checks reduced
membership ideals for all coordinate-multiplicity strata. Distinct-coordinate
solving at k=4 remains unknown after three fresh bounded attempts. No performance
trial, speed advantage, asymptotic benefit or official research transition is
claimed.

## Inputs, scope and representation

The original F1 package and this card were supplied as pushed commit
`c35b9da6a65e019eaa517fc1a5f7774428ff35db`. All output is under this new
`tracks/f1/cubic-divisor/` directory; original evidence is unchanged. The exact
published P-256 p,a,b,r and 35-term symmetric S4 are inherited from the committed
baseline and original F1 source. [execution.json](execution.json) binds their
hashes and the source/commands used here. No Git, PR, shared-file or external
service action was performed.

Use F(t)=D_(2^k)(t)−c with c≠±2 and the monic cubic
h=t³−s1 t²+s2 t−s3. Repeated squaring computes the three coefficients of F mod h
without constructing D_(2^k) densely. Setting them to zero means h divides F.
For separable F this automatically selects three **distinct coordinate roots**.
It avoids the earlier triple-equal terminal's scheme multiplicities, while
repeated coordinates are preserved through separate systems.

The exact three-stratum construction and its proof are in
[derivation.md](derivation.md):

| Coordinate stratum | Equations before S4 | Geometric membership points |
|---|---|---:|
| Three distinct | Three coefficients of F mod h vanish | C(S,3) |
| Exactly two equal (x,x,y) | F(x)=0 and Δ_F(x,y)=0 | S(S−1) |
| All equal (x,x,x) | F(x)=0 | S |

Here Δ_F=(F(x)−F(y))/(x−y) is a polynomial computed by a short circuit. On the
diagonal it equals F'(x), so separability excludes x=y without a saturation
variable. Each ideal is reduced. Joining S4 keeps a subset of a finite reduced
algebra and therefore remains reduced. All tested F split completely over Fp,
so all geometric points are rational. This rationality is checked rather than
assumed from the field size.

## Completed solver and completeness checks

The algebraic adapter expands the remainder coefficients, joins S4, constructs a
grevlex Groebner basis, then performs exact lex/root extraction. Each successful
basis checks original generator reductions, every critical pair, basis vanishing
on every complete reference zero, and equality of finite quotient dimension with
that zero count. A separate implementation of sparse modular polynomial division
replays these certificates without calling SymPy. Complete geometric references
are enumerated for certification; they do not feed coefficients or roots into the
Groebner search. The delivered validation harness includes that exhaustive
reference work and does not claim to avoid its cost.

All accepted coordinate states are factored and fully lifted with signs on P-256.
The three strata's signed solutions are united and compared with a separate
exhaustive signed-point triple implementation. Equal x-coordinates can lift to
opposite points; this includes inverse-pair cancellations.

| Fixed public query | Distinct / two-equal / all-equal S4 states | Signed point solutions | Algebraic completeness |
|---|---:|---:|---|
| k=2 constructed positive | 1 / 0 / 0 | 1 | Complete |
| k=3 original constructed positive | 1 / 0 / 0 | 1 | Complete |
| k=3 constructed two-equal coordinates | 0 / 1 / 0 | 1 | Complete |
| k=3 constructed all-equal coordinates | 0 / 0 / 1 | 1 | Complete |
| k=3 base-member cancellation control | 0 / 7 / 1 | 7 | Complete |
| k=3 published generator G | 0 / 0 / 0 | 0 | Complete empty set |
| k=4 original constructed positive | unknown / 0 / 0 | unknown; reference has 1 | Partial: distinct solver stopped |

The k=3 fixed terminal and public target are the original fixture. k=2 uses its
same subfibre as the earlier forward adapter. k=4 uses the committed generic k=4
fixture. These solver fixtures have actual canonical base sizes M=4,7,10,
respectively; the k=2 subfibre differs from the first package's matched-M=3 coset.
Exact c, targets, roots, signed bases, all accepted states and all point
witness indices are retained in the result and recombination files.
Constructed positives establish correctness only. The fixed G empty check is a
finite-domain fact, not a uniform-target sampling result. Base cancellations are
controls and are not counted as independent useful relations.

Additional exact outcomes:

- Membership-only k=3 gives a reduced quotient of dimension 56=C(8,3), 28 basis
  polynomials and 378 checked critical pairs. These are exact algebraic counts.
- Across 21 successful algebraic attempts, the separate sparse verifier checks
  386 critical pairs. All 21 certificates pass.
- Complete linear factorization, divisor identities, nonzero Jacobians and the
  equality det Jacobian=Res(h,F/h) are checked at all 4+56+560 distinct divisors
  for S=4,8,16 over the actual field.
- Forty deterministic actual-field coefficient cases compare symbolic remainder
  circuits with independent polynomial long division and automatic derivatives.
- Seven three-distinct divisor/remainder/nonzero-Jacobian witnesses reach depths
  k=6,7,8,16,32,64,96. They certify representations, not complete high-depth solves.
- The out-of-scope actual-field control F=D8−2, h=t³−4t divides F but has zero
  remainder Jacobian determinant. This checks that separability is a substantive
  hypothesis for the proof; it does not classify every nonseparable fibre.

## Preserved unknown attempts and costs

[attempts-01/receipt.json](attempts-01/receipt.json) retains 22 sequential attempts:
21 complete, one stopped. The default SymPy Buchberger k=4 distinct-positive
attempt stops during basis construction. [attempts-02/receipt.json](attempts-02/receipt.json)
retains two fresh F5B attempts, for that k=4 positive and the fixed generator;
both stop during basis construction. Each has a declared 30-second watchdog and
2 GiB process address-space cap. Native stdout/stderr remain per attempt. No
stopped case has an empty-set or completeness label. The original F1 watchdog is
left unchanged in its original directory.

No timing or peak-memory benchmark was collected, and no adapter comparison is
inferred. Environment: the pinned `/workspace/dickson-solver/.venv/bin/python`,
CPython 3.12.14, SymPy 1.14.0, python-flint 0.8.0. The inherited native Codex
runtime/model binding remains unprobed; same-session replay is not independent
scientific review.

With fixed h-coefficient products shared, a uniform remainder step has 3 field
squarings, 9 general multiplications, 3 small-constant scalings and 8 additions.
This is an arithmetic-circuit count. Polynomial expansion still grows:

| k | S | Expanded coefficient degree | Nonzero terms (R0,R1,R2) |
|---:|---:|---:|---|
| 2 | 4 | 2 | 2,2,3 |
| 3 | 8 | 6 | 10,13,14 |
| 4 | 16 | 14 | 67,85,81 |
| 5 | 32 | 30 | 496,575,546 |

The generic cubic-divisor quotient has length C(S,3), versus S³ for the earlier
symmetric-terminal representation; the full reduced union has C(S+2,3) states.
These representation facts do not bound solver runtime, certificate-generation
cost, target success, or total ECDLP complexity. The current algebraic adapter
expands the input; the circuit code and deep witnesses keep the short formulation
available for further work.

## Artifacts and reproduction

- [checks-01/receipt.json](checks-01/receipt.json): six complete query unions and
  one partial unknown; individual files contain full witnesses.
- [checks-01/identities.json](checks-01/identities.json): exact factor, Jacobian,
  circuit, gradient, hypothesis-control and deep-witness results.
- [basis-replay-01.json](basis-replay-01.json): independent-code replay of 21 bases.
- [execution.json](execution.json): source/input identities, exact commands and
  environment; native logs remain alongside their receipts.
- [packed-artifacts.json](packed-artifacts.json): the 71,029-byte native membership
  certificate is retained losslessly as gzip with its original byte hash. Its
  receipt still binds the decompressed bytes. No data was omitted.
- [diagram.svg](diagram.svg): editable vector explanation; aggregate PDF rendering
  belongs to the Coordinator.

For a fresh single-case replay from the repository root, choose a previously
unused output path:

```bash
TRACK=research/p256_factor_base_parallel_20261025/tracks/f1/cubic-divisor
PYTHONDONTWRITEBYTECODE=1 /workspace/dickson-solver/.venv/bin/python "$TRACK/solve.py" \
  --case "$TRACK/../checks-02/generic-k3.json" --depth 3 \
  --stratum distinct --target positive --out "$TRACK/replay-distinct-k3-new.json"
```

The two supervisor scripts and check script deliberately refuse existing result
directories; preserve the delivered records. `verify_basis.py` reads either native
JSON or its exact gzip representation. Source inputs and frozen receipt hashes
are retained, including the stopped attempts' reconstructible equations.

## Remaining obligation

The nonreduced generic membership obstacle now has an exact replacement on all
three strata. The separate obstacle is a certified global elimination method and
cost bound for the unexpanded circuit. [problem.md](problem.md) records that change
and the next discriminating step: implement incremental elimination on the
multiplication-gate circuit and replay unchanged k=3 and k=4 positive/empty
controls, retaining complete or unknown outcomes. Relation rank, labels, setup,
linear algebra and final target attachment remain separate ECDLP obligations.

No shared graph or problem index was edited. The Coordinator should link this
progress into the original F1 problem and include the new report/diagram in the
aggregate PDF. Neither filing nor archiving this package changes a hypothesis.
