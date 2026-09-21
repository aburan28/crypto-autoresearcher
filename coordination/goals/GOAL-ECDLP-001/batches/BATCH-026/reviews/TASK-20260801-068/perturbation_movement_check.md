# TASK-20260801-068 — DUTY: PERTURBATION MOVEMENT, RE-RUN NOT RE-READ

RTB-068. The generating operation was **re-run**, not its output re-read.

## 1. Can each plant family move each certifying statistic AT ALL? (from source)

Derived from `lpf001_driver.py` source before any datum was consulted, then
tested by executing the driver's own functions.

**OBJ-PLANT-ROUGH.** `build_rough_replacement(v, p, rng)` returns `q*r` with `q`
prime drawn in `(p, v//64]` and `r` prime with `r <= v//q`. For `v <= X = p²`:
`r <= v//q <= p²/q < p < q`, so `P_max = q` exactly and
`Z = ln(qr)/ln q = 1 + ln r/ln q < 2`. The null's `Z` is Dickman-distributed with
`P(Z < 2) = 1 - rho(2) = 0.693147` (I computed `rho(2) = 0.306853` from the
driver's own solver; `1 - rho(2) = ln 2` as it must be). The plant puts mass 1
on `Z < 2` against the null's 0.693. **Not invariant in law.** It therefore CAN
move `STAT-RATE-u` (it removes smooth samples) and `STAT-KS-DICK` (it distorts
the Z-CDF), and it structurally CANNOT move `STAT-TAIL-DEEP` (deep-tail floor
above 5 at both cells).

**OBJ-PLANT-SMOOTH.** `build_smooth_replacement` returns a product of primes at
most `Bsm(u = 4)` = 256 / 1024, so `P_max <= X^{1/4}` and `Z >= 4` with
probability 1, against a null `P(Z >= 4) = rho(4) = 0.004911`. **Not invariant in
law**, by a mass difference of 0.995. It CAN move `STAT-RATE-u` at `u <= 4`
strongly and `STAT-KS-DICK`; at `u = 6` it is second-order (STRIKE-2's argument,
unfaulted) and in the deep tail it is measured-negligible (D1-v2 part (ii)).

**DESIGN-TRAP-LPF-1 re-derived independently: neither frozen plant family is
invariant in law.** The driver's own docstring says the same; I did not rely on
it.

**No retained certifying statistic is incapable of moving on the objects here.**
Each of the five retained ids moves at the γ = 0.05 top rung of at least one
ladder at BOTH cells:

| id | bits 16 via | bits 20 via |
|---|---|---|
| STAT-RATE-u@u=2 | SMOOTH, ROUGH | SMOOTH, ROUGH |
| STAT-RATE-u@u=3 | SMOOTH, ROUGH | SMOOTH, ROUGH |
| STAT-RATE-u@u=4 | SMOOTH, ROUGH | SMOOTH, ROUGH |
| STAT-RATE-u@u=5 | SMOOTH | SMOOTH |
| STAT-KS-DICK | SMOOTH, ROUGH | SMOOTH |

## 2. Row-by-row over all 210 rows

I regenerated the flag column from first principles and then regenerated all 28
lists, addressing every row by its own `family` / `gamma_rung` / `field_bits` /
`statistic_id` fields.

- **210 rows; 0 disagreements** between `LPF_movement_beyond_noise_flag` and my
  own `|LPF_movement_shift_in_null_sd| >= 1.0`. The archived flag column is
  faithful to the contract's criterion at every row.
- **210 expected (family, γ, cell, statistic) addresses; 0 missing, 0 extra, 0
  duplicated.** The table is complete and uniquely addressable — the row-order
  assumption is not load-bearing for my regeneration, which never used position.
- **28 of 28** published `raw_flag_sets_all_28` entries reproduce **exactly**.
- **28 of 28** `certified_ladders` `moving_rungs` entries equal (raw set if
  certified, `[]` if STRUCK).
- **28 of 28** certified-or-STRUCK statuses equal (`certified` iff the γ = 0.05
  flag is true).

## 3. The precise check this batch exists to pass

**"Every γ in every `moving_rungs` list must carry flag true."**
→ **0 unsupported entries across all 28 lists.** RR-LPF-1 had 2 (RTB-054-1a/b);
both are gone.

**"Every γ with flag true must appear in its list."**
→ **1 omission across all 28 lists**, and it is exactly the disclosed case:
OBJ-PLANT-ROUGH / STAT-KS-DICK / bits 20, γ = 0.02, shift −1.402750452642616,
flag true, ladder status STRUCK, list `[]`. That is OPEN-RR066-A and it is ruled
in `contract_review.yaml`; the ruling is READING 1 and the omission is correct.
RR-LPF-1 had the same omission plus one more (DIFF-3, γ = 0.001 on
SMOOTH/RATE-u=3/bits 20, shift +1.5724157930250209, flag true, ladder
certified) — that second one was a genuine under-certification and change (a)
repaired it.

**"A rung with no recorded movement that the reading rule certifies"** →
**none.** **"A family invariant in law"** → **none.** **"A certifying statistic
incapable of moving on any object here"** → **none among the retained five; the
two that are incapable are struck, which is the rule working.**

## 4. Artifact-tell audit (inventor-protocol §3)

I asked, for each of the 28 sequences, what the reported quantity should do as
γ — the parameter meant to drive it — increases, and whether it does.

- **27 of 28 sequences are monotone in the required sense**: once the flag turns
  true it stays true up the ladder.
- **1 of 28 is not**: ROUGH / KS-DICK / bits 20, flags
  `(F,F,F,F,F,T,F)` across γ = 0.0005…0.05, shift sequence
  `−0.0205, −0.0486, −0.1222, −0.3581, −0.6871, −1.4028, −0.7587`. I confirmed by
  exhaustive search over all 28 sequences that this is the **only** row where a
  sub-top rung flags and the top rung does not. That is the canonical artifact
  tell, D6 diagnoses the mechanism (D+/D− argmax switching in `max(D+, D-)`),
  and the whole-ladder strike is the conservative response. Ruled correct at
  TASK-20260801-054 (OPEN-RR052-C); I concur on re-derivation.
- **Null-object control present:** the movement metric's denominator is the
  measured null sd over 200 OBJ-NULL-UNIF replicates at the same cell through
  the identical pipeline — the identical measurement against a random instance
  of the same shape. The two struck statistics are exactly the case where the
  measured shift is indistinguishable from that null (max |shift| 0.338 and
  0.481 over 28 rows each), and they were struck rather than reported as low
  power. This is the control-before-belief obligation discharged.

## 5. DET-LPF-1 cross-criterion agreement

The S1/S2 detection floors in ALT-CLASS come from `LPF_gamma_det_both_cells`, a
different archived criterion. I read them directly from the archive:
SMOOTH — u=4: 0.002, u=3: 0.005, u=2: 0.01, KS-DICK: 0.05, u=5: NONE_ON_LADDER;
ROUGH — u=2: 0.02, u=3: 0.05, everything else NONE_ON_LADDER.
**Identical to the file, and unmoved by change (a).** The claim that the two
criteria agree at the two corrected rungs is confirmed independently in
attainability_check.md §L-2 (both rungs also produce no band exit).

## 6. Duty verdict

**PASS.** The regeneration is genuinely mechanical, reproduces at 28/28 from the
archive, corrects two entries against the experiment and one in its favour, and
leaves exactly one flag-true rung out of a list — the D9 struck ladder, disclosed
in three places and ruled here.
