# P1 — Is the comparison against `MATZOV.Nf` well-posed on this design?

**TASK-20260803-5f11b7 / BATCH-f75059 (batch 2 of 6) / GOAL-MLKEM-004**

Machine-readable form: `results.json` → `S2_wellposedness_P1`.
Instrument: rebuilt venv `/tmp/sagevenv-f75059`; pinned lattice-estimator at
`/tmp/le`, commit `3e48ef421ec256afddb3e7d2249a77eab6e9ba12` (clean tree),
`estimator/lwe_dual.py` class `MATZOV`, method `Nf` (line 526).

---

## Answer

> **NO SUCH TUPLE EXISTS.** There is no `(m, k_enum, k_fft, p, β_bkz, β_sieve)`
> that makes `MATZOV.Nf` a prediction about the object this design measures. The
> admissible set is **empty**, verified by exhaustive enumeration over all 351
> integer pairs `(k_enum, k_fft)` with `k_enum + k_fft ≤ n = 25`.
>
> Three components of the tuple **are** pinned by the run and are not fits —
> `m = 35`, `β_sieve = 60`, and `β_bkz` (irrelevant, see below). The obstruction
> is confined to `(k_enum, k_fft, p)`, and through `k_lat` it then contaminates
> the length model as well.
>
> The comparison is therefore made against the law's **two separable
> ingredients** — the per-vector advantage law and the iid noise model for
> wrong candidates — and is reported as such in `report.md` §3 and §4.

No tuple was manufactured to make a comparison possible.

---

## 1. The obstruction, stated exactly

`estimator/lwe_dual.py:540` fixes

```python
k_lat = params.n - k_fft - k_enum          # p.15
```

so `k_lat + k_fft + k_enum = n` is an **identity**, not a constraint one may
relax. The measured design imposes two requirements on that identity:

**R1 (the vector family).** MATZOV's dual vectors live in a lattice of dimension
`m + k_lat`: `k_lat` secret coordinates are absorbed by the shortness of the
`y`-part, and it is that shortness which makes `y·s_lat` small. The measured
database is a `bgj1_sieve` run over the **full** `d = m + n = 60` dimensional
dual lattice `L = {(x,y) : y ≡ Aᵀx mod q}`, in which *every* one of the `n = 25`
secret coordinates has a short `y`-component (measured `⟨‖y‖²⟩ = 129.56`).
Hence `m + k_lat = 60 = m + n`, i.e.

    k_lat = n = 25   ⟹   k_enum + k_fft = 0.

**R2 (the candidate axis).** MATZOV guesses `k_enum` coordinates and FFTs
`k_fft` of them; a candidate hypothesis differs from the truth on exactly those
`k_enum + k_fft` coordinates. The measured design scores candidate secrets that
differ from `s` on any of all `n = 25` coordinates. Hence

    k_enum + k_fft = n = 25.

R1 and R2 are simultaneously satisfiable only if `n = 0`. The measured design is
the **conjunction of R1's vector family with R2's scoring**, and that conjunction
requires `k_lat + k_enum + k_fft = 2n > n`, contradicting line 540.

This is checked in code, not asserted: `compare.py` enumerates every
`(k_enum, k_fft)` with `k_enum + k_fft ≤ n` (351 pairs) and returns the
admissible set, which is empty (`results.json → S2 → admissible_tuples_found: []`).

## 2. What *is* pinned by the run

| symbol | value | why it is not a fit |
|---|---|---|
| `m` | 35 | the number of LWE samples actually used |
| `β_sieve` | 60 | the sieve ran on the full `d = 60` lattice; this is a fact of the run |
| `β_bkz` | **irrelevant** | `β_bkz` enters `Nf` only through `deltaf(β_bkz)^(m + k_lat − β_sieve)`, whose exponent is `0` when `β_sieve = m + k_lat = d`. Verified as known-answer control **KA-5**: `Nf(β_bkz=45) == Nf(β_bkz=300)` exactly. |

So the frequently-quoted "you also have to choose two block sizes" ambiguity does
**not** arise here. The ambiguity is entirely in `(k_enum, k_fft, p)`.

## 3. `p` has no referent, and that is the term that matters most

The design performs no FFT sub-block split, so `k_fft = 0` under any reading that
respects the vector family. Known-answer control **KA-3** confirms the
consequence directly against the pinned callable: with `k_fft = 0`,
`Nf(p=2) == Nf(p=q=127)` to machine precision, because both `p`-bearing terms —
`k_fft·log p` and `exp(k_fft/3 · (σ_s π/p)²)` — vanish identically.

The second of those is the term MATZOV includes **precisely to charge the
adjacent-FFT-bin degradation**. That is the same phenomenon as batch 1's
near-miss observation. It is therefore identically `1` here and **cannot be
tested by this design at all**, in either direction. This is recorded as a
boundary of the batch, not as a defect of the law.

## 4. The factor-29 spread, reproduced under contract

`RT-20260803-4064e1` OBJ-1 reported admissible readings spanning
`N_pred = 24.9 … 723`. Both endpoints are reproduced here with the pinned
callable and the measured length:

| reproduced quantity | RT value | this task |
|---|---|---|
| low endpoint (`exp(2a_x) · (log(1/μ) + log 33)`) | 24.9 | **24.854** |
| high endpoint (`exp(2a_x) · (n log q + log(1/μ))`) | 723 | **722.545** |

The grid this task evaluates is wider, because it varies the **prefactor** as
well as the log-term. Both are ambiguous, and independently:

*Log-term readings* (`k_enum·H(X_s) + k_fft·log p + log(1/μ)`):

| id | reading | value |
|---|---|---|
| L1 | pure distinguisher, `k_enum = k_fft = 0` | 0.693 |
| L2 | union bound over the 33 tested candidates | 4.190 |
| L3 | whole secret enumerated, `k_enum = n` | 51.871 |
| L4 | whole secret FFT'd at `p = q` | 121.798 |

*Prefactor readings* (`exp(4(ℓσ_s π/q)²)`):

| id | reading | `ℓσ_s` | prefactor |
|---|---|---|---|
| P-A | modeled length, `k_lat = n`, `β_sieve = d = 60` | 24.406 | 4.297 |
| P-B | modeled length, `k_lat = 0`, `β_sieve = m = 35` | 3.306 | 1.027 |
| P-C | **measured** length from the sieve database (`a_x = 0.8902`) | 26.970 | 5.932 |

Over the 12-cell grid, `N_pred` runs from **0.712 to 722.545**, a spread of
**1015×** before any data is consulted. A residual against a predicted value that
is uncertain by three orders of magnitude is not a measurement of anything, which
is why none is reported.

**Additional ambiguity found in this task (KA-4).** `MATZOV.Hf` returns an
entropy in **bits** (it divides by `log 2`, and `MATZOV.cost`'s `T_guess` uses
`2**(k_enum*H)`, confirming the intent), while `log(p)` and `log(1/μ)` in the
same sum are **natural** logs. Any reading that uses `k_enum` therefore carries
a further factor-`ln 2` ambiguity on that term, on top of the referent ambiguity
above. Recorded as an observation about the callable; no claim is made that the
estimator is wrong.

## 5. The one sub-comparison that *is* well-posed

Under reading R-A (`k_lat = n`, `k_enum = k_fft = 0`) the **vector family** that
`Nf` describes is exactly the measured one, `β_sieve = 60` is a fact of the run,
and `β_bkz` drops out. So `lsigma_s` is fully determined with no free parameter,
and the *length half* of the law can be compared honestly:

| quantity | label | value |
|---|---|---|
| `lsigma_s` | **modeled** (MATZOV, R-A) | 24.406 |
| effective `ℓσ` from the database | **measured** | 29.274 |
| ratio modeled/measured | — | **0.834** |
| per-vector advantage at that length | **modeled** | 0.4824 |
| mean score, `reference_zero` candidate (phase `= x·b`, no candidate subtracted) | **measured**, 2000 draws | **0.3280 ± 0.0722** |

MATZOV's length heuristic (`√(4/3) · √(β/2πe)` × Gaussian-heuristic scaling)
under-predicts the effective phase spread of this database by 17 %, which
over-predicts the per-vector advantage by 47 % (0.482 modeled against 0.328 ±
0.072 measured; the modeled value sits +2.1 sd of the measured distribution).

**This is not licensed as a departure claim.** It is a single toy-scale
configuration, `β_sieve = 60` is far below the regime where the
`√(β/2πe)` Gaussian-heuristic asymptotic is intended to hold, and no null object
of the right shape for a *length* claim was run. It is recorded as a measured
comparison, correctly labelled modeled vs measured, and left for the Reviewer.

R-A's log-term is `log(1/μ)` alone — under R-A no candidate is enumerated at all
— so this sub-comparison reaches the length/advantage half of the law only. That
half **is** ingredient 1, which is exactly why the fallback is not a
consolation prize: it is the same object, isolated.

## 6. What this answer does and does not mean

- It does **not** mean `MATZOV.Nf` is wrong, ill-defined, or inapplicable. It
  means it is not a prediction *about this design*, because this design is not
  an instance of the attack `Nf` costs.
- It does **not** mean the comparison is impossible. It means the well-posed
  comparison is against the law's separable ingredients, which is what batch 2
  reports.
- A design that *would* admit a tuple would have to split the secret: sieve on
  `m + k_lat` coordinates with `k_lat < n`, and enumerate/FFT the remaining
  `n − k_lat`. That is a concrete successor design, not a redesign of the
  measurement, and it is the only route by which the `p`-dependent near-miss
  correction term becomes testable at all.
