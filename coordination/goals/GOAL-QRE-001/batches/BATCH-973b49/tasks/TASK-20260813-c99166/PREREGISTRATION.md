# PREREGISTRATION — arithmetic-layer counting convention

- task: TASK-20260813-c99166
- goal: GOAL-QRE-001
- batch: BATCH-973b49
- question: RQ-QRE-6dba8c
- repository commit at freeze time: `5fa40e21de534100449eb03506e3d4840df8b869`
- working tree at freeze time: clean
- frozen: before any gate was counted or any circuit was built. Nothing in this
  file is derived from a count; it is the unit in which the counts will later be
  expressed.

This document fixes the counting convention. It is frozen. If a construction
turns out to be impossible to build under this convention, the convention is not
edited: the failure is reported as a failure and an amendment is requested from
the Coordinator.

Scope note: this artifact and every artifact of this task states only what a
circuit costs under the convention below. It contains no date, no timeline, no
statement about when any machine might exist, no arrival probability, no
forecast, and no migration or policy advice.

---

## 1. Gate set

The circuits are built from exactly three gates:

| gate | meaning | counted as |
| --- | --- | --- |
| `X(a)` | `a ← a ⊕ 1` | Clifford, T-cost 0 |
| `CNOT(a,b)` | `b ← b ⊕ a` | Clifford, T-cost 0 |
| `CCX(a,b,c)` (Toffoli) | `c ← c ⊕ (a ∧ b)` | 1 Toffoli |

No other gate appears anywhere in either circuit. In particular there are no
multi-controlled gates with more than two controls, no `CSWAP` primitive
(a controlled swap, where used, is expanded into `CNOT, CCX, CNOT` and
contributes its 1 Toffoli), and no relative-phase or measurement-assisted
constructions.

This gate set is classical-reversible, which is the property that makes
constraint 3 (blocking classical simulation of the *identical* circuit)
meaningful: every circuit counted here is a permutation of computational basis
states and can be executed exactly on a classical bit vector.

**Reported gate metrics** (all three are reported for every circuit):
`toffoli`, `cnot`, `x`.

## 2. T-count

T-count is **derived from the Toffoli count at a declared, derived ratio**, not
counted directly:

```
T = 7 × (Toffoli count)
```

Justification obligation accepted here and discharged in the artifacts, not
cited: an explicit Clifford+T circuit containing exactly 7 `T`/`T†` gates
(and otherwise only `H`, `CNOT`) will be exhibited, its 8×8 unitary computed
from first principles by exact complex matrix multiplication, and checked
against the Toffoli permutation matrix to numerical tolerance 1e-12. Constant
`7` is admissible only if that check passes. If it fails, the T column is
reported as *not derived* and left empty.

`X` and `CNOT` contribute 0 to the T-count. No T-depth, T-width, or
measurement-and-feedforward variant is claimed. Constructions using fewer than
7 T per Toffoli exist in the literature; **none is used here, and none is
cited**, because this task may not import a constant it has not derived. This
is a stated upper bound under this convention, not a claim of optimality.

## 3. Ancilla accounting

- All ancillas are **clean**: allocated in state `|0⟩`. No borrowed or dirty
  ancillas are used anywhere.
- All ancillas are **returned to `|0⟩`** before the circuit ends. This is
  enforced mechanically: the allocator refuses to free a register whose
  simulated bits are not all zero, so every validation run that passes has
  also proved ancilla cleanliness for that input.
- Reported qubit metrics: `peak_qubits` (maximum number of simultaneously
  allocated qubits, including the input/output registers) and
  `ancilla_qubits = peak_qubits − io_qubits`.
- Qubits are **not** counted as a cost that trades against gates. No qubit/gate
  tradeoff is optimized or claimed.

## 4. Uncomputation policy

- Every intermediate value is uncomputed by running the inverse of the circuit
  that produced it. The inverse costs the same Toffoli count as the forward
  circuit; no measurement-based uncomputation, no "free" deallocation, and no
  garbage output is permitted.
- Uncomputation gates are counted in full, on the same footing as computation
  gates.
- No measurement occurs anywhere in either circuit. There is no
  measurement-and-correct step and no classical feedforward.

## 5. What "one modular exponentiation" includes

Definition frozen here. For an `n`-bit odd modulus `N` and a classical base `a`
with `gcd(a,N)=1`, one modular exponentiation is the reversible circuit

```
|e⟩ |1⟩ |0…0⟩  ↦  |e⟩ |a^e mod N⟩ |0…0⟩
```

where

- `e` is a **2n-bit** quantum exponent register (the exponent width used by
  order finding on an `n`-bit modulus), left unchanged;
- the target register is `n` bits and is initialised to the value 1;
- the circuit is the standard sequence of **2n controlled modular
  multiplications** by the classical constants `a^(2^j) mod N`, `j = 0 … 2n−1`;
- every ancilla is returned to `|0⟩` (clause 3);
- `N` and `a` are classical compile-time constants: no register holds `N`.

Included in the count: all 2n controlled modular multiplications, all
uncomputation, all constant loading, all comparison/reduction logic.
Excluded from the count, explicitly: the QFT, the Hadamard layer, phase
estimation, any measurement, and any error-correction or routing overhead.
This is an *arithmetic-layer* count only.

Controlled modular multiplication is realised in place as: out-of-place
multiply-accumulate into a zeroed register, controlled swap, then uncomputation
of the source register by an accumulate with the constant `a^(−2^j) mod N`
(which exists because `gcd(a,N)=1`). No other formulation is scored.

## 6. What "one elliptic-curve point addition" includes

Definition frozen here. For an `n`-bit prime `p`, a short Weierstrass curve
`y² = x³ + Ax + B` over `F_p`, and a **classical constant** affine point
`Q = (x₂, y₂)`, one point addition is the reversible circuit

```
|x₁⟩ |y₁⟩ |0…0⟩  ↦  |x₃⟩ |y₃⟩ |0…0⟩ ,   (x₃, y₃) = (x₁, y₁) + Q
```

acting in place on the two `n`-bit coordinate registers, with every ancilla
returned to `|0⟩`. This is the building block of Shor's algorithm for ECDLP,
where the added point is always a classical constant.

**Declared domain of correctness.** The circuit is a permutation on all
`2^m` basis states (it is built from reversible gates), but it computes the
group law only on the declared domain: `P = (x₁,y₁)` an affine point of the
curve with `x₁ ≠ x₂` (so `P ≠ ±Q`, excluding the doubling and
point-at-infinity cases) and `0 ≤ x₁, y₁ < p`. Behaviour outside that domain is
unspecified and is not counted as a failure. Exceptional-case handling is
**not** included in the circuit and therefore not in the count; this omission is
declared here rather than discovered later.

Included in the count: the two constant coordinate subtractions, the modular
inversion(s), the modular multiplications, and every uncomputation needed to
return all ancillas — including the uncomputation of the inverse and of the
slope λ.
Excluded: the QFT/phase-estimation layer, measurement, error correction,
routing, and any exceptional-case branch.

## 7. Sub-circuit constructions to be used (fixed here, so the count is not
   chosen after seeing it)

All are built from the gate set of clause 1 and none imports a constant:

- **Ripple-carry adder** on `n` bits via a MAJ/UMA carry chain, 1 Toffoli per
  bit in each of the two passes, 1 clean carry ancilla.
- **Constant addition** by loading the classical constant into a clean ancilla
  register with `X` gates (0 Toffoli) and running the general adder. Not
  optimised into a constant-specialised adder.
- **Modular addition** mod a classical constant `M` by: add; subtract `M`;
  record the sign bit into a flag; conditionally add `M` back (the conditional
  load of the classical `M` costs `CNOT`s only, 0 Toffoli); uncompute the flag
  by a comparison against the first addend. Five general adder passes.
- **Modular doubling** mod an odd constant by rotation (SWAPs, 0 Toffoli),
  constant subtraction, and a flag-controlled constant addition; the flag is
  uncomputed from the parity of the result.
- **Quantum×quantum modular multiplication** as an accumulate loop over the
  bits of one factor, using a running register repeatedly modular-doubled, with
  the partial product formed into a scratch register by `n` Toffolis per bit
  and uncomputed by `n` Toffolis per bit.
- **Modular inversion by Fermat's little theorem**: `x^(p−2) mod p` via
  left-to-right square-and-multiply, each intermediate held in its own clean
  register, the result copied out with `CNOT`s, and the whole chain reversed to
  free all scratch. **No Euclid/Kaliski-style inverter is derived in this
  task.** Consequence, stated in advance: the reported EC counts are the cost
  of *this* inverter, they are an upper bound for the point addition, and they
  carry an ancilla footprint quadratic in `n`. This is a declared property of
  the construction, not a claim about the cheapest possible point addition.

Because the Fermat inverter's length depends on the binary weight `w(p−2)`, EC
counts are declared in advance to be reported **twice**: (i) as an exact closed
form in `(n, w)`, and (ii) as a fit in `n` alone over a declared ladder of
primes, whose residuals are expected to be non-zero and are reported, not
hidden.

## 8. How counts are produced and reported

- **One circuit description, two consumers.** The circuit is emitted once, by
  one builder, into an abstract sink. The sink is either a **tally** (counts
  gates and tracks qubit allocation) or a **runner** (executes the gates on a
  classical bit vector). The builder cannot tell them apart. A counted circuit
  and a simulated circuit are therefore the same circuit by construction, and
  the correspondence is auditable by reading a single source file.
- Counts are **exact enumerations**, obtained by running the builder and
  tallying; they are never estimated, extrapolated, or hand-derived.
- Counts are reported **as a function of `n`** over a ladder of widths, with a
  fitted closed form and the residual of the fit at every ladder point. The
  fit is by exact rational least squares/interpolation over an assumed
  polynomial degree declared in `counts.json`; a fit is only reported as exact
  if every residual is exactly 0, and it is additionally checked against
  held-out widths not used in the fit.

## 9. Validation is blocking

- A circuit is reported only if its classical simulation computes the intended
  function at every declared small bit width, on the declared input set
  (exhaustive where feasible, otherwise a seeded random sample whose seed is
  recorded), **and** every ancilla is verified returned to `|0⟩`.
- A width that fails simulation is reported as failed and its count is
  withheld.
- The simulated circuit is the counted circuit (clause 8). Simplified or
  idealised variants are not simulated and not reported.

## 10. Determinism

Every random choice (sampled inputs, sampled primes, sampled bases) is drawn
from `random.Random(seed)` with the seed recorded in `execution_report.yaml`
and in the artifact that consumes it. All moduli, bases, curves and points used
are recorded explicitly so that any run is reproducible from the artifacts
alone.
