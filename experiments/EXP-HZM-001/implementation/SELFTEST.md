# Implementation self-test (isolated, NOT a protocol run)

This note records a one-off smoke test of the three implementation modules
required by `specification.yaml`'s `required_artifacts`
(`signature_enumeration.py`, `cost_ledger.py`, `brute_force_control.py`),
run manually during EXP-HZM-001 execution to confirm the modules are
genuinely functional code, not placeholders.

**This is explicitly not part of the EXP-HZM-001 protocol.** The
specification's pre-registered stopping rule (`stopping_rules[0]`) fired in
`RUN-HZM-001-a` because `CTRL-HZM-MANUSCRIPT-ALIGNMENT` failed: the
manuscript's own displayed formulas for `M`/`q` (base `l'`, the post-halving
reduced kernel dimension) and for `H` (base `l = 2*l'`, the pre-halving full
kernel dimension) use two different base symbols, so the spec's pinned
identity `H = M*d/(L+1)` does not correspond to one shared manuscript
quantity `L`. Per the frozen protocol, "a toy run is never opened on
unaligned formulas" — so `RUN-HZM-001-b` (the formal 9-config x 3-seed grid)
and `RUN-HZM-001-c` (the formal brute-force control subset and primary-gate
cost ledger) were never opened, and no run record exists for them.

The smoke test below used ad hoc toy parameters chosen only to exercise the
code paths (not the specification's pinned `(L,d)` grid, not seeded via
`harness.toycurve` with the specification's recorded seeds `[1,2,3]`, and
not compared against the pinned formulas as a measurement). It carries
**no evidentiary status** under EXP-HZM-001 and is **not** a `RUN-HZM-001-*`
run record.

## `brute_force_control.py`

Positive control: built a hand-constructed 4x8 matrix over F_101 with a
column artificially duplicated (columns 2 and 3 identical), guaranteeing an
exact zero minor at column-index tuple `(0,1,2,3)`.

```
brute_force_control smoke test: planted zero minor detected = True
total zero minors found among all C(8,4)=70 column choices: 33
```

The planted zero minor was correctly detected by direct determinant
evaluation, and the brute-force oracle (`zero_minors_by_definition`) ran to
completion over all 70 column-subsets without error.

## `cost_ledger.py`

Reproduced the specification's own pinned algebra (not the manuscript's
verbatim equations, which `RUN-HZM-001-a` found do not share a base for
`H`) at `N=257, L=8, d=1` (illustrative parameters, not the primary gate
sizes):

```
cost_ledger smoke test (MODELED, spec formula, N=257 L=8 d=1):
  M = 9  H(spec) = 1  q = 0.034479
  charged_expected_signatures = 29.003
  rho_bound = 17  survives_rho_gate = False
```

All numbers here are labeled `modeled`, derived only from the spec's own
pinned formula, never from an executed enumeration -- consistent with
`docs/evidence-and-reproducibility.md`'s cost-model reporting rules.

## `signature_enumeration.py`

Ran the full defect-restriction / left-kernel / signature-construction /
duplicate-detection pipeline on a random 4x8 matrix over F_101 with d=1:

```
candidate_completions = 4
signatures_processed = 20
duplicates found = 2
```

The pipeline executed end-to-end without error and found duplicate
signatures (as expected generically for a random matrix at this small
size), confirming the kernel/RREF/signature-construction code paths are
functional.

## Conclusion

All three modules execute correctly on ad hoc instances. This establishes
only that the code is not vaporware; it does **not** constitute the
formal EXP-HZM-001 measurement, which the pre-registered stopping rule
correctly prevented from being opened.
