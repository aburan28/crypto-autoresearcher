# Correction before a valid near-prime result

**2026-10-24 UTC; after the first run, before the corrected run.** The frozen
[PROTOCOL.md](PROTOCOL.md) incorrectly treats the census's `nt` column as
the order of the second SHA-1-derived coefficient sign in **all** six fields.
The census actually stores the quadratic-twist order. In the five fields
with `p ≡ 3 (mod 4)`, the sign change `b -> -b` is that twist and `nt` is a
valid order for the second seeded root. In P-224, `p ≡ 1 (mod 4)`: `b` and
`-b` are isomorphic and have the *same* order, whereas the `nt` column is the
order of a different, unseeded quadratic twist. The original 69-position
census [explicitly applies this field distinction](../nist_seed_selection_20261016/crosscheck_full_census.py).

The first run `runs/positive-20261024T022340Z/` and its verification are
preserved as evidence of the mistake. Its 130-position figure is **invalid
for seed-derived curve eligibility**: it incorrectly includes P-224 twist
orders. The corrected launcher is `run.py`; the exact first launcher is
retained as `run_v1.py`. The corrected run excludes P-224 `nt` completely,
counts a P-224 position with `n=0` as censored even if `nt>0`, and retains
both columns in the other five fields. All other frozen controls, `l_max=255`,
thresholds, sources, 120-second GP timeout and output requirements remain.

The corrected result must be checked against the 69 full-prime-order seed
positions and independently replayed. This amendment changes the input
interpretation, so the corrected run is a new write-once record, not an
overwrite or reinterpretation of the first raw output.
