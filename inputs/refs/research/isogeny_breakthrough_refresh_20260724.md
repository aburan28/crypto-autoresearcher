# Isogeny Breakthrough Refresh

Date: 2026-07-24

## Handoff: post-paper breakthrough triage

### Claim or task

Find a novel and valuable isogeny-recovery result beyond the balanced-primary
paper, strong enough to count as a general isogeny-complexity improvement, a
SCALLOP/PEARL-SCALLOP break, or an ECDLP consequence.

### Status

`OPEN / NO BREAKTHROUGH FOUND / POSITIVE MODEL-BOUND SIGNAL PRESERVED`

### Current public baseline

The relevant public baseline moved during this search.

- Galbraith--Gilchrist--Robert, ePrint 2025/1243, is the closest direct
  self-pairing baseline for ascending isogenies.  Its abstract claims improved
  ascending recovery, removal of a Galbraith heuristic, an improvement for
  small-crater volcanoes, and only very particular effects on
  `(PEARL)SCALLOP`; current SCALLOP parameters remain unaffected.
  URL: <https://eprint.iacr.org/2025/1243>
- WayFinder, ePrint 2026/1219, is a current broad oriented-supersingular
  isogeny-problem baseline.  It generalizes Delfs--Galbraith and SuperSolver,
  provides a cost model, handles more general orientation orders, and includes
  a low-storage algorithm for oriented supersingular curves, even with distinct
  orientation orders.
  URL: <https://eprint.iacr.org/2026/1219>
- PEARL-SCALLOP, ePrint 2024/1744, gives the current PEARL parameter setting:
  the orientation is represented by a `2^e`-isogeny whose degree is roughly the
  acting class-group discriminant.
  URL: <https://eprint.iacr.org/2024/1744>
- The active PEARL-SCALLOP attack, ePrint 2026/191, recovers the secret using
  a handful of oracle calls in an active model by using non-primitively
  oriented curves.  This is not the passive transcript model tested here.
  URL: <https://eprint.iacr.org/2026/191>
- Ray, ePrint 2026/1305, is a close Kani cautionary baseline: sign/canonical
  ambiguity is not the only issue in two-dimensional Kani encodings; auxiliary
  freedom must also be charged.
  URL: <https://eprint.iacr.org/2026/1305>

### Strongest internal positive signal

Balanced-primary sign-free Kummer rows remain the strongest positive line.
The restricted theorem says that for pairwise-coprime odd primary orders
`n_i`, sign-free Kummer rows identify a degree-`d` homomorphism up to global
sign when

```text
beta(n_1,...,n_r) = min_S (prod_{i in S} n_i + prod_{i notin S} n_i) > 4d.
```

The proof uses the partition of local signs into kernels of `phi-psi` and
`phi+psi`, together with the degree parallelogram identity.

Same-instance toy receipts now show a consistent implementation signal:

| degree | orders | beta | 4d | balanced-primary wall sec | theta-gated Kani wall sec | ratio |
|---:|---|---:|---:|---:|---:|---:|
| 23 | `(7,11,17)` | 94 | 92 | 0.756411291 | 15.21352005 | 20.113 |
| 31 | `(11,13,19)` | 162 | 124 | 1.362477541 | 10.461672068 | 7.679 |
| 39 | `(11,17,19)` | 206 | 156 | 2.962653708 | 125.205960989 | 42.261 |

This is still not a general complexity theorem.  It is selected toy evidence,
uses wall-clock timing rather than normalized field-operation counts, and the
current decoder outputs dense explicit maps.

### SCALLOP transfer gate

The oriented-ideal Kani line has a real restricted theorem: a nonprincipal
ideal of norm `s` satisfying `n^2=d+s` can replace an integer auxiliary in a
balanced Kani diamond.  This gives a useful weak-parameter audit rule for
coprime auxiliary moduli.

The direct transfer to the GGR cyclic self-pairing architecture is closed for
the natural same-ideal block.  In the cyclic self-pairing setting the composed
degree and auxiliary norm share the ramified factor `m`.  At a shared ramified
prime `ell`, the local block has an oversized restricted kernel.  It contains
`ell+1` oriented maximal-isotropic planes, so orientation alone does not select
the required half-kernel.

The refreshed registered verifier confirms the obstruction:

```text
producer payload: f03a541ac07db04a72c47cd6a5879b78378b29451a17e712bfebafb3bf5e794e
verifier payload: bd9a8c76407b7bf84bc33dc7b02a6d88068e80d1235b5d3ff3ee79e6f0feecd0
ell values: 5,17,37
stable isotropic plane counts: 6,18,38 = ell+1
verifier assertions: 11/11
semantic mutations rejected: 3/3
```

This is a scoped negative result for the natural same-ideal SCALLOP transfer,
not an impossibility theorem for every auxiliary or every leakage model.

### Schur and Bockstein lines

The integral-lattice Schur line is mathematically clean but needs two coherent
noncommuting endpoint actions.  Current SCALLOP-style passive public keys have
not been shown to expose that interface.  Its current status is a restricted
theorem plus local-action-oracle toy evidence, not a deployed break.

The Bockstein-Weil line gives a sharp local leakage theorem: in a marked
valuation-one ramified truncation, one cross-level character recovers the
hidden branch digit.  The acquisition remains circular for the public recovery
problem because the character needs the hidden Kani block on an `ell^2`-torsion
lift.

### Conclusion

No internal line currently meets the requested endpoint:

- no general isogeny-complexity improvement beyond current public baselines;
- no SCALLOP or PEARL-SCALLOP break;
- no ECDLP consequence.

The balanced-primary line is still worth developing as a paper-quality
restricted reconstruction theorem and implementation signal.  The
breakthrough route is narrower: prove and implement a compact sign-free
Kummer-row decoder with normalized field-operation costs, or find a real
protocol transcript exposing the Schur/Bockstein extra action.

### Next concrete action

Finish the crosswalk against the full GGR 2025/1243 PDF once a non-403 copy is
available.  The supplied text does not appear to contain the balanced-primary
`beta>4d` Kummer-row uniqueness criterion, but the status remains
`NOVELTY-UNVERIFIED` until the PDF is checked end to end.  In parallel,
instrument the balanced-primary and theta-gated Kani same-instance scripts
with field-operation counters and output-size accounting.

### Artifact paths

- `research/balanced_primary_ggr_sign_factor_gate_20260724.md`
- `research/balanced_primary_theta_gated_comparison_table_20260724.md`
- `research/ggr_balanced_primary_crosswalk_20260724.md`
- `research/oriented_ideal_kani_recovery.md`
- `research/integral_lattice_schur_breakthrough_gate_20260724.md`
- `research/tate_bockstein_right_division_audit_20260724.md`
- `experiments/ecdlp_isogeny/iso_cyclic_kani_local_branching_result.json`
- `experiments/ecdlp_isogeny/iso_cyclic_kani_local_branching_verify.json`
