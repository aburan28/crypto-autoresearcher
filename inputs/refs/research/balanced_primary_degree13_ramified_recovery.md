# Balanced-Primary Ramified Recovery at Degrees 13 and 17

Date: 2026-07-24

Status: `OBSERVATION / TOY-EVIDENCE / MODEL-BOUND / POSITIVE SIGNAL / NOVELTY-UNVERIFIED`

## Result

The balanced-primary sign-oblivious criterion now has genuine ramified
self-pairing replications beyond the earlier degree-5 fixture.

Let `phi, psi:E0 -> E1` be isogenies of equal degree `d`, and let `P_i` have
pairwise-coprime exact odd orders `n_i`, prime to `d` and the characteristic.
If

```text
x(phi(P_i)) = x(psi(P_i))  for all i
```

and

```text
beta(n_1,...,n_r)
  = min_S ( product_{i in S} n_i
          + product_{i notin S} n_i )
  > 4d,
```

then `psi=phi` or `psi=-phi`.  The proof partitions the local signs between
`ker(phi-psi)` and `ker(phi+psi)` and uses the degree parallelogram identity

```text
deg(phi-psi) + deg(phi+psi) = 4d.
```

The new experiments supply the required `x(phi(P_i))` values from actual
ramified Frobenius/self-pairing acquisition, not from supplied rows.

## Degree-13 Fixture

```text
p = 390391
trace = 2
#E(F_p) = 390390
D_pi = -1561560 = -9240 * 13^2
degree d = 13
primary orders = (3,5,7,11)

E0: y^2 = x^3 +  76765*x +  66879   conductor 13
E1: y^2 = x^3 + 346159*x + 305173   conductor 1
```

The `Phi_13` neighbor certificate has exactly one rational target root,
`j(E1)=367365`, above `j(E0)=374743`.  For every primary in
`3,5,7,11`, the Frobenius action is ramified and nonscalar modulo that
primary: nilpotent rank `1`, square zero, and exact local Frobenius order
equal to the primary.

The thresholds are strict:

```text
beta(3,5,7,11) = 68 > 52 = 4d
C_ram = 11 < 26 = 2d
```

Every leave-one-primary control falls below the balanced threshold.

## Evidence

Three acquisition seeds passed.  Each run constructs the local torsion fields,
samples primitive oriented generators, computes Weil pairings, solves the
pairing-root equations, descends one sign-free Kummer generator row per
primary, and invokes the public balanced-primary decoder.

| artifact | success | payload |
|---|---:|---|
| `iso_balanced_primary_degree13_ramified_recovery_result.json` | true | `5bb10e79c79c30ab51f37e66f5a03eb23ab27a00bcab3398398b706239875f63` |
| `iso_balanced_primary_degree13_ramified_recovery_seed20260724.json` | true | `0b1d29e4dc26670d8d0e67f410bf731345351b4e1a6fb7ed57c48a909e5e32a1` |
| `iso_balanced_primary_degree13_ramified_recovery_seed20260725.json` | true | `01ec6f7544975ae0293f0b70924982826ba904a7beb8efabdfb1b9b3dbb4ece5` |

All three runs recover the same scientific projection hash:

```text
95aaad373ededb986879b6c413fa88f268e720b033cf1abe898dfadee36156ee
```

The independent verifier recomputes the orientation rows, pairings, roots,
degree-13 candidate, scaled x-map, `Phi_13` neighbor, conductor labels, and
post-freeze degree-13 edge inventory.

| verifier artifact | success | payload |
|---|---:|---|
| `iso_balanced_primary_degree13_ramified_recovery_verify.json` | true | `19a4a86288c86352afcd6e2ccdff65f3c34a3db1c731857aa0f6bf2090fa7532` |
| `iso_balanced_primary_degree13_ramified_recovery_seed20260724_verify.json` | true | `1e88cd6cc20bb59a68d3e9d7167b3ab18f72f0ab8b5f402ae887c72bd6f1fb5d` |
| `iso_balanced_primary_degree13_ramified_recovery_seed20260725_verify.json` | true | `85a9d42007797e20127a9945ebeef34151a89c27220a69fd571a795cfcde7df4` |

The additive rational-interpolation baseline uses all half-orbit rows.  It has
`11` rows, rank `11`, and threshold `26`; therefore it cannot provide the raw
degree-profile `(13,12)` interpolation certificate.

Red Team review is preserved at
`research/red_team_balanced_primary_degree13_ramified_recovery.md`.  It accepts
only the narrow toy/interface claim and rejects promotion to a general
isogeny-complexity improvement, SCALLOP break, PEARL-SCALLOP assessment, or
ECDLP consequence.

## Preserved Failures

Two failed predecessors are preserved.

| artifact | failure |
|---|---|
| `iso_balanced_primary_degree13_ramified_recovery_v1_wrong_globals_failure.json` | wrapper bug: `runpy` constants were not written into the producer function globals, so the old degree-5 constants were used |
| `iso_balanced_primary_degree13_ramified_recovery_v2_hash_failure_result.json` and `_verify.json` | custody bug: the final payload hash included the previous base payload hash field; verifier rejected `producer_payload_hash` |

These failures are implementation/custody negatives.  They do not affect the
accepted V3 arithmetic result.

## Degree-17 Fixture

```text
p = 8678671
trace = 2
#E(F_p) = 8678670
D_pi = -34714680 = -120120 * 17^2
degree d = 17
primary orders = (3,5,7,11,13)

E0: y^2 = x^3 + 1579039*x + 1568263   conductor 17
E1: y^2 = x^3 +  440615*x + 5331942   conductor 1
```

The `Phi_17` neighbor certificate has exactly one rational target root above
the source.  All five primary actions are ramified and nonscalar in the same
Frobenius-orientation sense.

The thresholds are again strict:

```text
beta(3,5,7,11,13) = 248 > 68 = 4d
C_ram = 17 < 34 = 2d
```

The producer and verifier passed:

| artifact | success | payload |
|---|---:|---|
| `iso_balanced_primary_degree17_ramified_recovery_result.json` | true | `001045f0e9d73fabade4a9a743242ce38da4ca3716e39b261724c8070945313e` |
| `iso_balanced_primary_degree17_ramified_recovery_verify.json` | true | `8cf0d9153122d63aaa62d293b6b756c3dd55b1acef05d211c173f25077eb611c` |

The scientific projection is

```text
b6afd5afbcb352c0368fe7947ad9293205aaeb1ac3be39eedfff723a17bb0a3a
```

The raw additive baseline has `17` rows, rank `17`, and threshold `34`.

One verifier predecessor is preserved:

| artifact | failure |
|---|---|
| `iso_balanced_primary_degree17_ramified_recovery_v1_invalid_leave_one_verify.json` | invalid inherited negative control: with five primaries, removing `3`, `5`, `7`, or `11` still leaves a strict balanced tuple; leave-one is diagnostic, not a required rejection |

## Interpretation

This is a real strengthening of the balanced-primary evidence: it covers
degrees `13` and `17`, four and five primary orders respectively, actual
ramified self-pairing row acquisition, three acquisition seeds on the
degree-13 fixture, and a verified degree-17 scaling stress.

It is not yet the requested endpoint breakthrough.  The current evidence does
not establish a general isogeny-complexity improvement, a SCALLOP break, or an
ECDLP consequence.  The result supports a reconstruction-stage positive signal
in the following restricted model:

- sign-free Kummer images are obtainable through ramified self-pairings;
- the primary orders are pairwise coprime and satisfy `beta>4d`;
- an explicit degree-`d` map is an acceptable output;
- torsion-field construction, pairings, DLP/root search, and `Omega(d log q)`
  output size are charged.

Compared with Galbraith--Gilchrist--Robert, this route targets the sign
ambiguity and explicit reconstruction stage rather than the full Kani/volcano
search problem.  It removes the local `2^r` sign enumeration
information-theoretically in the balanced-primary regime, but it does not yet
show a same-instance field-operation speedup over GGR/Kani, BMSS-style
normalized reconstruction, or an additive solver augmented with public curve
identity constraints.

## Literature Boundary

Primary sources checked in this cycle:

- Castryck, Houben, Merz, Mula, van Buuren, and Vercauteren, "Weak instances
  of class group action based cryptography via self-pairings",
  IACR ePrint 2023/549.
- Macula and Stange, "Extending class group action attacks via sesquilinear
  pairings", arXiv:2406.10440.
- Galbraith, Gilchrist, and Robert, "Improved algorithms for ascending
  isogeny volcanoes, and applications", IACR ePrint 2025/1243.
- Bostan, Morain, Salvy, and Schost, "Fast algorithms for computing isogenies
  between elliptic curves", arXiv:cs/0609020.
- The phase-retrieval complement-property literature was checked as the
  abstract sign-partition analogue; it supports caution on novelty but does
  not by itself state the isogeny degree/product criterion.

No explicit antecedent for the complementary-product isogeny criterion has
been found yet.  This remains `NOVELTY-UNVERIFIED` until a focused literature
agent completes review.

## Next Concrete Action

Run a same-instance comparison on a multi-degree family:

```text
balanced-primary decoder
vs additive curve-identity solver
vs BMSS after normalization
vs GGR/Kani/theta with shared work
```

Charge torsion fields, pairings, DLP/root search, memory, and output size.  A
cryptographic claim requires this comparison to show a strict advantage across
increasing degrees or to identify a parameter regime where the balanced-primary
criterion changes the asymptotic cost.

## Artifact Paths

- `experiments/ecdlp_isogeny/iso_balanced_primary_degree13_ramified_recovery_contract.md`
- `experiments/ecdlp_isogeny/iso_balanced_primary_degree13_ramified_recovery.sage.py`
- `experiments/ecdlp_isogeny/iso_balanced_primary_degree13_ramified_recovery_verify.sage.py`
- `experiments/ecdlp_isogeny/iso_balanced_primary_degree13_ramified_recovery_result.json`
- `experiments/ecdlp_isogeny/iso_balanced_primary_degree13_ramified_recovery_verify.json`
- `experiments/ecdlp_isogeny/iso_balanced_primary_degree13_ramified_recovery_seed20260724.json`
- `experiments/ecdlp_isogeny/iso_balanced_primary_degree13_ramified_recovery_seed20260724_verify.json`
- `experiments/ecdlp_isogeny/iso_balanced_primary_degree13_ramified_recovery_seed20260725.json`
- `experiments/ecdlp_isogeny/iso_balanced_primary_degree13_ramified_recovery_seed20260725_verify.json`
- `experiments/ecdlp_isogeny/iso_balanced_primary_degree17_ramified_recovery_contract.md`
- `experiments/ecdlp_isogeny/iso_balanced_primary_degree17_ramified_recovery.sage.py`
- `experiments/ecdlp_isogeny/iso_balanced_primary_degree17_ramified_recovery_verify.sage.py`
- `experiments/ecdlp_isogeny/iso_balanced_primary_degree17_ramified_recovery_result.json`
- `experiments/ecdlp_isogeny/iso_balanced_primary_degree17_ramified_recovery_verify.json`
- `experiments/ecdlp_isogeny/iso_balanced_primary_degree17_ramified_recovery_v1_invalid_leave_one_verify.json`
- `research/red_team_balanced_primary_degree13_ramified_recovery.md`
