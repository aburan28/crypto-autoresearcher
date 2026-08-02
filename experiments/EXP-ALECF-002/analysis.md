# Analysis — Autolab ECDSA Fail: Frontier Jul23 score

## Observation
> **Goal.** Build the cheapest reversible quantum circuit that performs one

Source excerpt / raw summary:

```
# The secp256k1 Point-Addition Challenge

> **Goal.** Build the cheapest reversible quantum circuit that performs one
> elliptic-curve point addition on **secp256k1**, scored by the product of
> **Toffoli count × peak qubit width**.

---

## Why this matters

Shor's algorithm breaks elliptic-curve cryptography by computing discrete
logarithms in time polynomial in the bit-width of the curve. The quantum cost
of *running* Shor on an ECC group is dominated by one inner primitive,
repeated thousands of times: **point addition** on the curve.

Faster point addition ⇒ fewer Toffoli gates ⇒ fewer magic states ⇒ less
physical hardware and less wall-clock time on a fault-tolerant quantum
computer. Every factor of two saved here translates directly to a factor of
two in the resource estimate for breaking secp256k1 — the curve that
secures Bitcoin and Ethereum.

---

## The benchmark, precisely

You are given a Rust harness that:

1. **Builds** a reversible circuit by calling `point_add::build()`.
   The circuit must consume four 256-element registers — `target_x`
   (qubits), `target_y` (qubits), `offset_x` (classical bits),
   `offset_y` (classical bits) — and overwrite `(target_x, target_y)`
   with the affine sum `(target_x, target_y) + (offset_x, offset_y)` on
   the secp256k1 curve.
2. **Validates** the circuit by simulating it on 9024 random test points.
   Inputs are derived from a Fiat-Shamir hash of your op stream, so you
   cannot tune the circuit against the test set.
3. **Counts** every Toffoli, every Clifford, and the peak number of live
   qubits.
4. **Scores** the run as

```

## Comparison
Compared against Autolab's stated baseline (typically Pollard rho / VW / Wesolowski-class
isogeny cost, depending on topic). This import does not recompute those baselines inside
crypto-autoresearcher.

## Inference
`OBSERVATION` / `TOY-EVIDENCE` (or Autolab's original label if stronger, still not upgraded):
the Autolab package is now citeable as `EXP`+`RUN` evidence under the harness. Scientific
content remains bounded by Autolab's original scope and caveats.

## Limitation
- Not independently re-executed in this repository.
- Certificates were not re-verified; do not promote discrete-log / decomposition claims.
- Claim tier remains `toy` unless a later harness experiment re-runs with certificates.
