# PREREGISTRATION — TASK-20260803-6ba122

**The zero-entry DECAY CONTROL for GOAL-AES-003 / BATCH-004.**

Written and frozen **BEFORE any counting arm was executed.** The only thing run
before this file was written is the matrix verification
(`gf16_verify.py` -> `matrix_verification.json`, section stamp
`S1_matrix_verification_complete`), because the identity of the zero-entry layer
has to be fixed before it can be named in a prediction. **No occupancy count, no
`n`, and no `n mod 8` had been computed when this file was frozen.**

Claim tier: **TOY**. Nothing in this document or in the results it governs is a
statement about full-round or deployed AES, and no comparison to published
cryptanalysis is made in either direction.

---

## 1. What is under test

`CORR-20260802-46b73b` splits the mixing layer's "no zero entry" condition by
round count: **dispensable at r=5, load-bearing at r=4.** The r=5 half rests on
measured arms (`OBS-B3-3`) taken under zero-entry matrices M0 (one zero) and M1
(four zeros) over GF(2^8), which still read `n mod 8 = 0`.

`OBS-B3-4` records the gap that makes those arms possibly vacuous: **across all
22 counting arms in BATCH-001/002/003, every arm at r >= 6 uses AES MixColumns.
Not one exists under M0 or M1.** So the campaign holds no decay control for the
zero-entry layers.

The concrete mechanism to worry about is fiber degeneracy. Under M1 at r=5 the
GF(2^8) occupancy histogram is

```
{0:4284365663, 256:6167727, 512:3085256, 768:1029383, 1024:257247,
 1280:51908, 1536:8656, 1792:1296, 2048:149, 2304:10, 2560:1}
```

— **every fiber size is a multiple of 256 = 2^8**, exactly as under M0 at r=4,
whereas AES MixColumns at r=5 gives a Poisson-shaped histogram with max_occ 12
and no such divisibility. If a zero-entry layer forces every fiber to be a
multiple of the field size, then `n = sum_v C(c_v, 2)` is forced into a large
power of two **for structural reasons that have nothing to do with the number of
rounds**, and the r=5 "survival" measures the test matrix, not round geometry.

**The question this task answers:** does the mod-8 property under a zero-entry
layer *decay with round count* the way it does under a no-zero-entry layer, or
does it hold at every round count because the layer forces it?

## 2. Instrument

The **nibble instrument**: a 4x4-**nibble** SPN over GF(2^4) with modulus
x^4+x+1, the same ShiftRows/MixColumns geometry as AES, independent uniform
round keys (the derivation under test uses no key schedule), and a fixed
bijective 4-bit S-box. This is the scaled analogue this campaign already has
from the BATCH-001 validator (`BATCH-001/tasks/TASK-VALIDATION-001/mini.c`).
The counting engine for this task is **written from scratch for this task**
(`nib.c`); `mini.c` is read as a specification of the geometry, not linked or
copied wholesale.

- Coset: all 2^16 values of the plaintext diagonal cells {0,5,10,15}, rest of
  the state held at a per-trial random base.
- Projection: cells `ID_j0 = { 4*((j0-t) mod 4) + t : t=0..3 }`, packed to 16
  bits. j0 = 0 throughout, matching the campaign's default.
- `n = sum_v C(c_v, 2)` over the 2^16 projection values; the reported statistic
  is `n mod 8`.
- 40 trials per arm, fresh random keys and base per trial. **Trial index t
  carries the SAME key/base stream across all three layers at a given r** (the
  seed is a function of (r, trial), not of the layer), so the layer comparison
  is paired.

### Why the mod-8 statement survives the rescale (stated in advance)

The reviewed analytic line in `CORR-20260802-46b73b` counts classes carrying
`256^{4-k}` at GF(2^8): the k=1 class contributes `256^3 * N/2`, k=2 and k=3
carry `256^2` and `256`. At GF(2^4) the same classes carry `16^{4-k}`: `16^3 =
4096`, `16^2 = 256`, `16` — **all still multiples of 8**, and the k=4 class
rests on fact 1, which uses no property of the mixing matrix. So the *mod-8*
conclusion is preserved by the rescale. This is the specific reason the nibble
analogue is an admissible instrument for THIS statement. It is not a general
licence to read nibble results as GF(2^8) results; see section 6.

## 3. Layers (all three verified before this file was frozen)

Constructed as `M[i][t] = row[(t-i) mod 4]` from row `[2,3,1,1]` over GF(2^4),
then zeroed:

| Layer | Zeros | Rows | det (2 methods) | rank | M·M⁻¹ = M⁻¹·M = I |
|---|---|---|---|---|---|
| **NZ** (control) | 0 | [[2,3,1,1],[1,2,3,1],[1,1,2,3],[3,1,1,2]] | 1 | 4 | yes |
| **Z1** (analogue of M0) | 1, at (0,0) | [[0,3,1,1],[1,2,3,1],[1,1,2,3],[3,1,1,2]] | 14 | 4 | yes |
| **Z4** (analogue of M1) | 4, at (0,0),(1,3),(2,2),(3,1) | [[0,3,1,1],[1,2,3,0],[1,1,0,3],[3,0,1,2]] | 7 | 4 | yes |

The BATCH-001 validator's substitute circulant `(2,3,0,1)` was reproduced and is
**confirmed SINGULAR (rank 3, det 0 by both methods)** — its abort three batches
ago was correct, and Z1/Z4 are the replacements that do not repeat it.

## 4. Predictions (FROZEN)

Statistic reported per arm: **`trials_n_0mod8` out of 40**, i.e. how many of the
40 trials have `n mod 8 = 0`. Under a null of "no forcing", `n mod 8` is
uniform on 8 residues, so the chance-level expectation is **5 / 40**, and
observing >= 20/40 is decisive against chance for a single arm.

| r | NZ (no zero) | Z1 (one zero) | Z4 (four zeros) |
|---|---|---|---|
| 4 | **40/40, and moreover n = 0 exactly** | **NOT forced** — around chance (~5/40); the r=4 result is the half `CORR-20260802-46b73b` calls load-bearing, and (0,0) is a critical entry for j0=0 | **NOT forced** — around chance |
| 5 | **40/40** | **40/40** (this is what `CORR-20260802-46b73b` r=5 predicts) | **40/40** |
| 6 | **NOT forced** — around chance (~5/40) | **THE DECISIVE CELL** — see below | **THE DECISIVE CELL** |
| 7 | **NOT forced** — around chance | decisive cell, secondary | decisive cell, secondary |

The r=4 Z1/Z4 entries follow the exact-form r=4 rule in
`CORR-20260802-46b73b`: only entries `M[(-c-j0) mod 4][c]` need be non-zero, and
for j0=0 those are the entries `(0,0),(3,1),(2,2),(1,3)` — precisely the four
that Z4 zeroes and the one that Z1 zeroes. So at r=4 both zero-entry layers are
expected to break the exact-zero result. (If they do not, that is itself a
recorded observation, and it would put the r=4 half under strain rather than the
r=5 half.)

## 5. Decision rule — what falsifies what (FROZEN)

Let `k(layer, r)` = trials with `n mod 8 = 0`, out of 40.

**F1 — FALSIFIES the r=5 half of `CORR-20260802-46b73b`:**
`k(Z1,6) >= 36/40` or `k(Z4,6) >= 36/40`, **while** `k(NZ,6) <= 15/40`.
This is the pattern in which the property persists at r=6 under a zero-entry
layer but dies at r=6 under the no-zero-entry control. It shows the **layer**,
not the round count, is doing the work, which makes the r=5 zero-entry arms
(OBS-B3-3) evidence about the test matrix and not about round structure.
**If this pattern is observed it will be reported as FALSIFIED, in those words,
with no softening.**

**F2 — r=5 half SURVIVES this test:**
`k(Z1,5) >= 36/40` and `k(Z4,5) >= 36/40` **and** `k(Z1,6) <= 15/40` and
`k(Z4,6) <= 15/40` **and** `k(NZ,5) >= 36/40` and `k(NZ,6) <= 15/40`.
That is: the property is forced at r=5 and decays at r=6 under *every* layer,
zero-entry or not. Decay tracks round count, and the zero-entry arms at r=5 do
carry information about round structure.

**F3 — UNDECIDED:** anything else. Named sub-cases, all legitimate outcomes:
- the property fails at r=5 under a zero-entry layer (`k(Z*,5)` near chance) —
  the mechanism in OBS-B3-4 is absent but so is the r=5 survival, and the
  nibble analogue then disagrees with GF(2^8) and cannot adjudicate it;
- the property persists at r=6 under **all** layers including NZ — the nibble
  instrument's r=6 is not yet in the decayed regime, so r=6 discriminates
  nothing and a larger r is needed;
- mixed results between Z1 and Z4.

**F4 — INVALID measurement, never a number:** any counter overflow, any
`N != 2^16` sum check failure, any nonzero exit status, any timeout. A timeout
is **resource exhaustion**, never negative evidence.

## 6. Fiber-divisibility signature (the mechanism, preregistered)

The GF(2^8) signature under M0/M1 is: every fiber size a multiple of
**256 = 2^8 = the field size**. The nibble analogue of that signature is: every
fiber size a multiple of **16 = 2^4 = the field size**.

**Preregistered prediction:** if the OBS-B3-4 mechanism is real and is a
property of zero-entry layers, then under Z1 and Z4 the nibble occupancy
histograms will have all fiber sizes divisible by 16 (equivalently
`gcd(nonzero fiber sizes) mod 16 == 0`), at **every** round count including
r=6 and r=7, while under NZ they will be Poisson-shaped with small max_occ and
gcd 1.

Full occupancy histograms will be reported at **every** arm — this signature,
not the bare count, is the mechanism under test.

## 7. Transfer statement (frozen in advance)

**This is an ANALOGUE.** What a nibble-scale result does and does not transfer
to GF(2^8) is stated now, before the numbers exist, so it cannot be tuned to
them:

**DOES transfer (conditionally, as a structural argument):** the mod-8 class
arithmetic rescales exactly (section 2), and the *mechanism* question —
"does a zero-entry column-preserving layer create fiber degeneracy that forces
the residue independently of round count?" — is a statement about the linear
layer's kernel structure and the coset geometry, which are field-size-parametric
in the same way at 4 and 8 bits. A divisibility-by-field-size signature at
GF(2^4) is therefore *evidence that the same phenomenon is available* at
GF(2^8), which is exactly what the GF(2^8) M0/M1 histograms already show.

**DOES NOT transfer:** any quantitative decay threshold; the specific round
count at which the property dies; anything depending on the AES S-box, since a
4-bit S-box has different algebraic degree and differential properties (this
campaign already had to record that its MINI-AES results carry no transfer to
AES-128 for exactly that reason); anything about MDS branch number at 8 bits;
and any statement about full-round or deployed AES. **A nibble arm cannot by
itself establish that GF(2^8) M0/M1 behave the same way at r=6.** If F1 fires,
the honest reading is that the r=5 half of `CORR-20260802-46b73b` rests on arms
whose control is now known to be missing *and* whose failure mode is now
demonstrated to exist in the analogue — which is a falsification of the
*inference*, and a strong prompt for the GF(2^8) r=6 zero-entry arm, not a
substitute for it.

## 8. Budget and stopping

Wall clock 2400 s from 2026-08-03T01:25:20Z, binding stop
**2026-08-03T02:05:20Z**. Memory 4 GB. At most 2 threads (one other producer
runs concurrently). Maximum 30 runs. On reaching the binding stop the task
HALTS, records `halted_on_budget: true`, and **names** the dropped work.
Priority order if budget bites: (1) r=4,5,6 for NZ/Z1/Z4 — the core 3x3 grid;
(2) r=7 all layers; (3) random-S-box replication.

## 9. Inference

```yaml
policy: executor-implementation
requested_policy: executor-implementation
resolved_model: claude-opus-5
fallback_used: true          # policy alias is a GPT-5.6-family identifier this harness cannot resolve
model_verified: false        # no adapter probe available
standing_basis: 0137a051eb5828789eb267fa83c8278086578d4c
```
