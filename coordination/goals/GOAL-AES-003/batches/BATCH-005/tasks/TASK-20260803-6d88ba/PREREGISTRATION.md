# PREREGISTRATION — TASK-20260803-6d88ba

**BATCH-005 RANK 2: the GF(2^8) zero-entry arm at r=6.**
Written and frozen BEFORE any counting run was launched. Timestamp of freeze is
recorded in `budget_stamps.jsonl` (section `prereg_frozen`). Nothing below was
edited after the first counting run started.

TOY TIER. Everything here is about a reduced-round AES-shaped SPN on one 2^32
diagonal coset with one key. Nothing here is a statement about full-round or
deployed AES, and no comparison to published cryptanalysis is made in either
direction.

---

## 1. What is being measured, and why this arm and not another

`CORR-20260802-46b73b` splits the mixing layer's no-zero-entry condition by round
count: dispensable at r=5, load-bearing at r=4. `OBS-B3-4` (EV-AES-96257a) is the
standing objection to reading any of that as a statement about round structure:
under M1 at r=5 at byte width, EVERY nonzero fiber size is a multiple of 256, so
the zero-entry matrices may force `n mod 8 = 0` by fiber degeneracy
**independently of round count**. If so, the r=5 zero-entry readings are not
evidence about round structure at all.

BATCH-004 (EV-AES-c66a80, OBS-B4-1) answered that in a **GF(2^4) nibble
analogue**: 40 trials per arm, r=4 and r=5 read 40/40 forced under all three
layers, r=6 read 4 (no-zero control) / 9 (one zero) / 7 (four zeros) against a
chance level of 5. Decay tracked round count, not zero entries.

Its own validator ruled the analogue **insufficient to settle byte width**: it can
establish that the mechanism exists, dies, and admits a counterexample at r=5, but
it cannot establish the round count at which GF(2^8) decays. The mod-8 margin is
**32x the modulus at byte width and only 2x at nibble width**. `OBS-B3-4` is
recorded STILL OPEN at byte width. This task runs it at byte width.

## 2. The object (frozen)

- Full 2^32 coset of the diagonal D_0 (state bytes 0,5,10,15 free, the other 12
  fixed by the base block), r-round AES-shaped SPN, C1 convention (final round has
  no mixing layer), AES S-box, AES-128 key schedule.
- Projection `pi_{j0}(c)` onto the inverse diagonal `ID_{j0}`, `j0 = 0` for every
  arm in this task.
- Statistic `n = sum_v C(m_v, 2)` over the 2^32 projected values, with the
  engine's independent cross-check `n_alt = (sum_v m_v^2 - N)/2`. A run whose
  `agree` is false, whose `N_ok` is false, or whose `counter_integrity_ok` is
  false is an **INVALID MEASUREMENT** and is reported as such, never as a number.
- Key `6fe52e2e9b3ea04085c370f9bc609245`, base
  `e35f00e7631cdd862e59d126e72b8fc9` — the same fixed, deterministic pair
  BATCH-002 used for its M0/M1 arms, chosen so this task's numbers are directly
  comparable to that batch's. There is no RNG anywhere in the counting engine.

### Layers (paired; the pairing IS the measurement)

| label | matrix (row-major hex) | zero entries |
|---|---|---|
| CTRL | `02030101010203010101020303010102` (AES MixColumns) | 0 |
| M0 | `00030101010203010101020303010102` | 1 |
| M1 | `00030101010203000101000303000102` | 4 |

All three re-verified non-singular over GF(2^8) by this task's own arithmetic
before any counting run (`matrix_verification.json`).

## 3. The two readings, and which one carries the information

**Reading A — the residue `n mod 8`.** This is what the campaign's prior records
report.

**Reading B — the fiber-divisibility signature.** Whether every nonzero fiber size
`m_v` in the occupancy histogram is a multiple of 256.

These are **not independent, and B dominates A.** OBS-B4-2 records the red team's
entailment: fiber divisibility makes the residue CERTAIN rather than likely. At
byte width, if every fiber is `m = 256k`, then

    C(256k, 2) = 256k(256k-1)/2 = 128k(256k-1),

which is divisible by 128 and hence by 8, for every k. So **whenever the
divisibility signature is present, `n mod 8 = 0` is forced arithmetically and the
residue reading carries ZERO information.** Reading A is only informative when
Reading B is absent.

This matters for statistical power. Each arm here is ONE 2^32 pass, not 40 trials.
A single `n mod 8 = 0` reading has chance probability 1/8 under a random-map null
— weak on its own. The divisibility signature has no such weakness: under a
random-map null the probability that all ~2^32 fiber sizes are simultaneously
multiples of 256 is astronomically small. **Reading B is therefore the
preregistered primary endpoint, and Reading A is secondary and interpreted only
conditionally on B.** I state this now, before measuring, so that a bare
`n mod 8 = 0` at r=6 cannot later be sold as a persistence result.

## 4. Predictions (frozen)

The nibble analogue says the mechanism dies by r=6 at every layer. If GF(2^8)
behaves the same way, then:

| arm | predicted Reading B (divisibility by 256) | predicted Reading A (`n mod 8`) | predicted max_occ |
|---|---|---|---|
| r=5 CTRL | ABSENT (prior: Poisson, max_occ 12) | 0 (forced by the reviewed analytic argument) | ~12 |
| r=5 M0 | ABSENT (prior BATCH-002: max_occ 12) | 0 (forced) | ~12 |
| r=5 M1 | **PRESENT** (prior BATCH-002: max_occ 2816, all fibers mult. of 256) | 0, but UNINFORMATIVE — entailed by B | ~2000-3000 |
| r=6 CTRL | ABSENT | free, 1/8 chance of 0 | ~12 |
| r=6 M0 | **ABSENT** | free, 1/8 chance of 0 | ~12 |
| **r=6 M1** | **ABSENT** — this is the prediction under test | free, 1/8 chance of 0 | ~12 |
| r=7 CTRL | ABSENT | free | ~12 |
| r=7 M0 | ABSENT | free | ~12 |
| r=7 M1 | ABSENT | free | ~12 |

The single load-bearing prediction is **r=6 under M1: divisibility ABSENT, a
Poisson-shaped histogram with max_occ around 12**, i.e. the degeneracy visible at
r=5 (max_occ 2816) is gone one round later.

## 5. What reading would show the NIBBLE ANALOGUE MISLED this campaign

Stated before measuring, and to be reported without softening if it occurs:

**M-1 (primary, decisive).** At r=6, the divisibility-by-256 signature is
**PRESENT under M1 (or under M0) while ABSENT under the CTRL arm at the same round
count.** That is the fiber degeneracy surviving a round past where the nibble
analogue says it dies, with the control at the same round count showing it does
not. This contradicts BATCH-004's central result and means EV-AES-c66a80's
conclusion rested on an analogue that misled. The 2x-vs-32x margin gap the
validator named is exactly the reason this is possible.

**M-2 (supporting, weaker).** At r=6, divisibility is absent under all layers but
`n mod 8 = 0` holds under M1 and/or M0 while the CTRL arm reads nonzero. On its
own this is 1/8-level and NOT decisive from one trial per arm; it would be
recorded as suggestive and as motivating a replication at other `j0`, not as a
contradiction.

**M-3.** Divisibility PRESENT under the no-zero CTRL arm at r=6. That would
falsify the campaign's framing in a different direction — the signature would not
be about zero entries at all — and is equally reportable.

**CONFIRMS** requires: at r=6, divisibility ABSENT under every layer measured,
including M1, with the histograms Poisson-shaped and mutually comparable.

**UNDECIDED** is the honest verdict if the critical arms do not complete, if any
completed arm fails its integrity checks, or if the r=6 comparison lacks either a
zero-entry arm or the control.

I note in advance that CONFIRMS from one trial per arm is **weaker evidence than
BATCH-004's 40 trials per arm on Reading A**, and is strong only on Reading B,
where one arm suffices because the signature is structural rather than
statistical. I will not claim more than that.

## 6. Instrument, and the overflow discipline

**REUSED, not rewritten.** The counting engine is BATCH-002's `cnt.c`, copied
byte-identically (sha256 recorded in RESULTS.json) into this task directory and
recompiled here. This is a control task, not a reimplementation; reusing the
engine is what makes the byte-width numbers directly comparable to BATCH-002's.
Its FIPS-197 pin was verified by me before use, not taken on trust: the soft
engine at r=10 under AES MixColumns reproduces both FIPS-197 C.1 vectors exactly
and agrees with the AES-NI path (results in RESULTS.json).

**Counter width, chosen deliberately.** BATCH-002's M1 r=5 arm reached max_occ
2816, which an 8-bit counter cannot hold. Therefore:

- **M1 arms use 16-bit counters (`cw=16`, `wbits=0`, 8 GB)**, which hold up to
  65535 and cover the r=5 precedent with a 23x margin.
- CTRL and M0 arms use 8-bit counters (`cw=8`, `wbits=0`, 4 GB); both read
  max_occ 12 at r=5 in BATCH-002, well under 255.
- The engine's `wsum != inw` detector is exact for wrap. **Any arm reporting
  `counter_integrity_ok: false` is recorded as an INVALID MEASUREMENT and its
  count is not reported as a number.** If an 8-bit arm trips it, that arm is
  re-run at 16 bits if budget allows and named as dropped if not.

## 7. Budget plan and the drop order, declared in advance

3600 s wall clock, 8 GB, at most 2 threads (one other producer is concurrent). A
full 2^32 pass took ~500-700 s in BATCH-002. **Nine arms do not fit; roughly four
to six do.** The engine's threads are value-partitioned — every thread scans the
whole input space — so a 1-thread run is a complete measurement at the same wall
time as a 4-thread run. I therefore run arms as 1-thread processes, at most two
concurrently, subject to the 8 GB cap.

Priority order, declared before measuring:

1. **r=6 M1** (`cw=16`, 8 GB, alone) — the one arm the dispatch card names as
   most important.
2. **r=6 CTRL** and **r=6 M0** (`cw=8`, 4 GB each, concurrent) — without CTRL at
   the same round count, arm 1 answers nothing.
3. **r=7 M1** and **r=7 CTRL** (concurrent) — tests whether decay, if seen at r=6,
   stays gone.
4. r=7 M0, then any r=5 arm.

**r=5 is dropped by design, not by accident**, and this is declared here rather
than discovered later: all three r=5 byte-width readings already exist in prior
batches under the same object — M0 r=5 (n = 2147411968, max_occ 12) and M1 r=5
(n = 1098070622208, max_occ 2816, all fibers multiples of 256) from BATCH-002,
and the AES-MixColumns r=5 Poisson histogram with max_occ 12 quoted in OBS-B3-4.
Re-measuring them would consume the whole budget to reproduce known numbers and
would leave r=6 — the open question — unrun. Spending the budget at r=6 instead is
the "fewer round counts done properly" the card asks for.

Any arm not reached is named in RESULTS.json with what it would have settled.

## 8. Inference block

```yaml
inference:
  policy: executor-implementation
  requested_policy: executor-implementation
  resolved_model: claude-opus-5
  fallback_used: true
  model_verified: false
  model_verification_note: >-
    No adapter probe exists in this harness; the resolved model is self-reported
    by the running agent and is NOT independently verified.
  standing_basis: 0137a051eb5828789eb267fa83c8278086578d4c
```
