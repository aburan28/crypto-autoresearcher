# EXP-SMTH-71b1b0 — implementation notes

Implementation record for `RUN-SMTH-71b1b0-001`, produced under
`TASK-20260803-fa7476` (BATCH-038, GOAL-ECDLP-001), authorized by
`DEC-20260803-155a86`.

This file documents **how** the frozen contract was implemented and **every
deviation, delegated determination and unexpected observation**. It states no
finding, selects no outcome branch and interprets nothing.

Frozen contract: `experiments/EXP-SMTH-71b1b0/specification.yaml`,
sha256 `e193a1966b264804b17976c1575f7bded858936005cab393f31763fef8a0e432`,
17950 bytes. Re-hashed at run start; the gate passed. The specification was
**not edited**.

## Files

| file | role |
| --- | --- |
| `smth71b1b0_core.py` | frozen constants, DRBG, factorisation, curve/factor base, Semaev invariants, Dickman rho, statistics, arm production, budget enforcement |
| `run_exp.py` | orchestrator: digest gate → RSS declaration → RSS probe → gate → measurement → artifacts |
| `verify_run.py` | **independent** re-verification; imports nothing from the two files above |

## Order of operations (mandated, and enforced in code)

1. Re-hash `specification.yaml`. On any difference: halt, write the reason to
   `stderr.log` and `raw-result.json`, produce no datum. (`orchestrate`, step 0.)
2. Write `rss-preflight-declaration.json` with the tolerance and margin, and
   hash it. This happens **before** the probe process is spawned, and the
   declaration itself is a literal in `run_exp.py` (`RSS_DECLARATION`), so it
   cannot have been written after seeing the probe.
3. Run the probe in a separate process at ~5, 10 and 20 % of records.
4. Only on a probe pass, run the measurement in a separate process.
5. Independent verification in a third process.

## Delegated determinations (DEV-1)

The contract fixes `master_seed: 4403196`, `domain: EXP-SMTH-71b1b0/v1`,
`field_sizes_bits: [16, 20]`, and states the construction rule as
"deterministic from (master_seed, domain, bits)" — but it names no derivation
function. Four implementation-level determinations were therefore required.
None of them changes a hypothesis, a metric, a threshold, a control or the
success criterion; all four are reproducible, and `verify_run.py` re-derives
every one of them with independent code.

1. **Bit source.** SHA256 counter-mode DRBG. Key `"<master_seed>:<domain>:<label>"`,
   block *i* = `SHA256(key || i as 8-byte big-endian)`, consumed as a byte
   stream. This is the only source of randomness in the run.
2. **Prime.** Label `prime:bits<N>`. Draw `bits-1` bits, force bits 2 and 1
   from the top, take the next prime; accept iff its bitlength is exactly
   `bits`. Result: `p = 59333` (bits 16), `p = 928139` (bits 20).
3. **Curve.** Label `curve:bits<N>`. For t = 1, 2, …: draw `a`, `b` mod p;
   reject if `4a³+27b² ≡ 0` (singular); count `#E(F_p)` exactly; reject if
   `#E = p+1`. Over a prime field with p > 3, supersingular is exactly trace 0,
   so this ordinarity test is exact rather than probabilistic. Both field sizes
   accepted the first candidate: `#E = 59764` (trace −430) and `#E = 929640`
   (trace −1500).
4. **Factor base.** `frozen_deterministic_subset`: the first 512 x-coordinates
   in `F_p`, in increasing integer order, that are x-coordinates of points of
   `E(F_p)`. This is the policy named by
   `H-DS-001.test_boundary.parameters.factor_base_policy` and stated verbatim
   in `EXP-SMTH-001.factor_base.rule`; it was not invented here. It is
   deterministic in (master_seed, domain, bits) through the curve.
   `factor_base_sha256` is taken over the newline-joined decimal x-list.

## Definitions resolved by reference, not by choice

**ENC-B** is pinned by the contract itself: `measured_quantity.encoding`
declares the codomain "an integer `N_ij` in `[1, p**2]`", and the bijection
`[0,p)² → [1,p²]` that realises it is `N = e₁·p + e₂ + 1`. This matches
`EXP-SMTH-001.intermediate_generation.step_4_primary_encoding` exactly.

**ENC-A** is *named* by the blocking control `CTRL-ENCA-POWER` but is **not
defined anywhere inside EXP-SMTH-71b1b0**, and the contract's
`reuses_nothing_unapproved` clause declines to reuse EXP-SMTH-001's contract.
There is exactly one definition of ENC-A in the corpus —
`EXP-SMTH-001.intermediate_generation.step_5_power_certificate_encoding`:
"`M_ij = max(lift(e_1), 1) * max(lift(e_2), 1)`. Range `[1, (p-1)**2]`" — and
`H-SMTH-001.test_boundary.parameters.power_certificate_encoding` names ENC-A in
that role. That single definition was used. **This is flagged as
`OBS-ENCA-DEFINITION-BY-REFERENCE` in the run manifest so the Validator can
rule on whether a blocking control defined only outside the frozen contract is
admissible.** The Executor resolved it by reference rather than choosing a
definition, and did not treat the gap as licence to invent one.

## Semaev half-arity map

`S_3(x₁,x₂,Z) = (x₁−x₂)²Z² − 2((x₁+x₂)(x₁x₂+a) + 2b)Z + ((x₁x₂−a)² − 4b(x₁+x₂))`
— the same expression as `harness/semaev.py:s3_expr`. Writing it `c₂Z² + c₁Z + c₀`,
`e₁ = −c₁·c₂⁻¹ mod p` and `e₂ = c₀·c₂⁻¹ mod p`.

`c₂ = (x₁−x₂)²` is nonzero for every enumerated pair because the loop bound is
`for j in range(i+1, 512)`, not a post-hoc diagonal filter. The verifier
confirms `c₂ ≠ 0` on sampled pairs, and — where the discriminant is a square —
recovers both roots by Tonelli-Shanks, checks that `S_3` vanishes at each, and
checks that `(e₁, e₂)` equals (root sum, root product). 199/199 split pairs at
each field size.

## Smoothness predicate and metrics

* `z = log(max(1, LPF(N)))/log(D)`, `D = 2^(2·bits)`.
* Smooth at rung *u* iff `LPF ≤ D^(1/u)`, evaluated as the **exact integer**
  comparison `LPF^u ≤ D` so no floating-point boundary case exists.
* Tail statistic: `z ≥ 0.5`, evaluated as `LPF² ≥ D`.
* Two-sample KS is computed on the sorted **integer** LPF values. `z` is
  strictly increasing in LPF, so the statistic is identical to the one on `z`
  and no float tie can perturb it.
* One-sample KS uses `F(z) = rho(1/z)`, the Dickman LPF CDF, evaluated at both
  the left and right limits of every jump.
* Factorisation is **complete**, never truncated: trial division by the 168
  primes below 1000, then deterministic Miller-Rabin (witness set 2..37, a
  proven witness set for n < 3.317·10²⁴; every integer here is < 2⁴⁰) and
  Pollard-Brent to full splitting. A record that failed to split completely
  would carry LPF 0 and be excluded from every fraction, with its count
  reported. **0 of 784896 records were incomplete and 0 had a
  factorisation-product mismatch.**

## Dickman rho

RK4 on `rho'(u) = −rho(u−1)/u` from `rho ≡ 1` on `[0,1]`, step `2e−5`, u to 60
— the provenance stated in `decision_rules.RATE-DS-1.rho_provenance`. It is used
**only** for the non-blocking `KS-DS-1` CDF. Every frozen rho value and every
frozen band in the contract was used **verbatim**; nothing was recomputed.

## Bounded working set (the RUN-SMTH-PILOT-002 failure mode)

Every per-record buffer is preallocated at its full contract-declared size
(6 arms × 130816 × 8 bytes) **before any record is produced**, together with the
fixed rho table. Peak resident memory is therefore fixed at process start-up by
the shard buffer, the preallocated arrays and the interpreter baseline. The
shard buffer holds at most 1024 records. Three enforcement layers:

* `RLIMIT_AS = 4294967296` in every stage process. RSS never exceeds virtual
  address space, so this is a kernel-enforced hard guarantee, not an advisory
  check.
* `VmHWM` polled at every 1024-record shard boundary.
* A `SIGALRM` flag tested after **every** record, so a wall-clock crossing stops
  at the next record boundary.

Declared tolerance (written and hashed before the probe): absolute peak RSS
≤ 1 GiB (margin 3 GiB, 75 % below the contract cap); growth between the 5 % and
20 % checkpoints ≤ 64 MiB. Observed peak RSS: 49745920 → 49745920 → 49762304
bytes. Growth **16384 bytes** — four pages — across a fourfold increase in
records produced.

Because the mandated production order puts the null arms first, the 20 %
checkpoint (156979 of 784896 records) falls **inside the null arms**; the probe
factored no treatment record and could not leak treatment information into any
later choice.

## Null-before-treatment ordering

`null_calibration.ordering_constraint` requires the null arms to be drawn,
factored and hash-committed before any treatment record is factored. The driver
produces `NULL-UNIF-D.bits16`, `NULL-UNIF-D.bits20`, computes their full summary
statistics, writes `null-commit.json` and records its sha256
(`4bc1b3920502af8b0d35dadcf427ec5b691b308c73ea871c1eeabb78bda5695f`) — and only
then factors the first treatment record. The digest is recorded in the manifest
and in `raw-result.json`.

## Independent verification

`verify_run.py` shares no code with the driver and uses different algorithms
where it matters: pure trial division to `sqrt(N)` (no probabilistic primality
test, no rho) for 2398 sampled records across all six arms; Fermat inverse
rather than `pow(x, -1, p)`; Tonelli-Shanks root recovery with direct `S_3`
vanishing checks; Legendre-sum point counting; and a Heun integration of
Dickman rho at step `1e−4` against the driver's RK4 at `2e−5`. 40 checks, all
pass; see `verification-report.json`.

## Deviations and recorded observations

| id | what | affects a verdict? |
| --- | --- | --- |
| DEV-1 | Four delegated determinations above (DRBG, prime, curve, factor base) — the contract states a rule, not a function. | no |
| DEV-2 | `sympy` is **absent** in this environment. `H-SMTH-001` had anticipated "sympy 1.14.0 for factorization" for the superseded EXP-SMTH-001 driver; the frozen contract names no library. Factorisation is pure Python. No package was installed — `no_network` was honoured. | no |
| DEV-3 | Before the single authorized full-scale invocation, the pipeline was exercised **once** at a reduced, non-contract scale (factor base 24, n = 276, shard 16) in a scratch directory **outside the repository**, purely to exercise code paths. That configuration cannot produce the contract's datum, its thresholds are meaningless at n = 276, and none of its numbers appears anywhere in this run package. The contract-scale entry point was invoked exactly **once**; no run was repeated and no result was discarded. | no |
| DEV-4 | 1 worker used of 4 permitted. Single-process execution keeps peak RSS lower and record order strictly deterministic; the run finished in 0.66 % of its wall ceiling. | no |
| OBS-RHO2-TRANSCRIPTION | `rho_frozen.u2 = 0.30684282` in the frozen contract, against `1 − ln 2 = 0.30685282` which the contract's own provenance says it cross-checked; difference 1.0e−5 (3.3e−5 relative), consistent with a single-digit transcription slip. The driver's RK4 reproduces `1 − ln 2` to 1.2e−14 and reproduces `rho(3)`–`rho(6)` to every digit the contract quotes. **No action taken**: frozen values and bands used verbatim, nothing recomputed. The factor-8 band is 64× wider than the discrepancy, and RATE-DS-1 does not gate the criterion. An Executor does not repair a frozen contract. | no |
| OBS-ENCA-DEFINITION-BY-REFERENCE | ENC-A is a blocking control's object but is undefined inside the frozen contract; resolved by reference to its single corpus definition (see above). | only CTRL-ENCA-POWER; it passes by ~106× under that definition |
| OBS-ENCA-INT-COLLISION | `min_integer` differs by exactly 1 between `TREAT-ENCB.bits20` (387014) and `CTRL-ENCA.bits20` (387013). Expected arithmetic on a pair with `e₁ = 0`: ENC-B gives `e₂+1`, ENC-A gives `max(0,1)·e₂ = e₂`. Recorded so it is not later read as an encoder defect. | no |

## Not done, deliberately

* The specification was not edited, and no threshold, band or frozen constant
  was adjusted.
* No ledger record, hypothesis, evidence record or knowledge entry was touched.
* No outcome branch was selected and no evidence strength was assigned. The run
  reports the mechanical evaluation of the frozen success criterion and nothing
  more.
* Nothing in this run licenses any cost saving, exponent, early abort or
  crypto-scale claim. **TOY TIER under every outcome.**
