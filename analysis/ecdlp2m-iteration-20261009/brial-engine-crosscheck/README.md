# BRiAl (PolyBoRi) step degree vs mutant-closure refuting degree, same instances

Exploratory cross-check, not program evidence. It tests heuristic H1 of
IDEA-20261010-066c44: that the mutant-closure refuting degree D_W tracks the
degree an independent GF(2) Groebner engine reaches on the same system.

## Engine
`passagemath-brial` (pip wheel, cp311; installed into a venv, nothing system-wide)
provides BRiAl/PolyBoRi's `groebner_basis` for Boolean polynomial rings. With
`prot=True` it prints `Current Degree: d` for every reduction round; the maximum
over a run is the engine's step degree, the analogue of an F4 step degree. UNSAT
systems reduce to `[1]`. The wheel also bundles a post-2020 `libm4ri.so.2`
(symbol set matches the 2024+ releases; exact release string not embedded).
`brial_degree.py` captures the protocol from the C-level stdout.

## Inputs
Pilot #1's labelled instances (`../m3-closure-pilot/instances/*.json`, now
committed), rebuilt with the vendored chained-S_3 builder by `export_systems.py`
(S3 and support-matched nulls) and `export_null2.py` (dense matched nulls,
n = 9 and 11). The run was time-capped at 30 min and covered 90 systems.

## Result (`brial_crosscheck.csv`)

| cell | family | label | BRiAl max step degree |
|---|---|---|---|
| n=9 (N=18) | S3 chained, m=3 | UNSAT (40) | 4 on 40/40 |
| n=9 | S3 | SAT (10) | 4 on 10/10 |
| n=11 (N=23) | S3 | UNSAT (8) | 4 on 8/8 |
| n=9 | support-matched null (12) | — | 3: 1, 4: 7, 5: 4 |
| n=11 | support-matched null (8) | — | 4: 1, 5: 7 |
| n=9 | dense matched null (12) | UNSAT (6) / SAT (6) | 6 on 6/6 / 8 on 6/6 |

BRiAl's UNSAT verdict agreed with the enumeration label on every labelled
system (0 mismatches of 70).

## Reading (derived)
1. On the S_3 systems the engine's step degree is exactly 4 on every instance,
   SAT and UNSAT, at n = 9 and 11. That matches the W_4 refuting degree of the
   pilot and the single in-repo msolve reading at (17,3,3,7) (RUN-SEMBIN-b6eb9f).
   It is an independent-engine read of Semaev's d_F4 = 4 at m = 3, on
   enumeration-certified instances.
2. The engine reports higher degrees where the system warrants it: 5 on most
   support-matched nulls at n = 11, 6 and 8 on the dense nulls. So the flat
   "4" on S_3 is not an instrument artifact (the concern raised in this
   session's red-team review).
3. The ordering S_3 (4) < support null (4–5) < dense null (6–8) says the chained
   descent is sharper than its own monomial support predicts, which is a
   finer statement than the pilot's W_4 contrast (support null refuted,
   dense null not).

## Limitations
m = 3 only; n ≤ 11; polynomial-basis V; one curve per n; support nulls are
unlabelled (BRiAl's verdict is the only label); 30-minute cap. Not a
contract run. Wall times: S3 0.06 s (n=9) and 0.7 s (n=11) per system; dense
nulls ~56 s.

## Regenerate
Create a venv, `pip install passagemath-brial passagemath-environment`, then
`python3 export_systems.py <cells>`, `python3 export_null2.py`,
`<venv>/bin/python brial_crosscheck.py` (cwd: this directory's parent must
hold `m3closure/` or edit the paths to `../m3-closure-pilot/`).
