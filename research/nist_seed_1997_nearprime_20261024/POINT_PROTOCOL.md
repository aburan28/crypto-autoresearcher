# Independent subgroup-point certificate follow-up

**Frozen after the corrected near-prime classification and before the point
check, 2026-10-24 UTC.** Input is the corrected write-once run
`runs/positive-20261024T022524Z/analysis.json`, SHA-256
`01b33e08abf1746669ed22d7b1afafbf4175a9d739638cd298194663c5126e33`,
plus `research/nist_seed_selection_20261016/raw/candidates.jsonl`,
SHA-256 `e854c17a38d5e9f1fca9eb8dd1aa034a6b6cd69d28a2a3acf78b1a187515a441`.
The correction in [AMENDMENT.md](AMENDMENT.md) excludes P-224's unseeded
quadratic-twist column. No raw near-prime result is edited.

For **every one of the 99** qualifying seed positions, choose the qualifying
root branch with the smallest cofactor, breaking ties in favor of the canonical
root. Check the seed-derived coefficient and form the exact short Weierstrass
curve over its archived prime field. Deterministically test x=1,2,...,32;
for the first available curve point Q with `P=hQ != O`, check `nP=O` and
`n²>16p`, where `u=h*n` is the archived order. The latter strict inequality
makes the Hasse interval narrower than n, so a nonidentity point of prime
order n proves that the archived u is the full group order: it is the unique
multiple of n in that interval. Record the first successful x, exact point
coordinates, order, cofactor, seed, coefficient, field, and full input hashes.

Controls: all ten published and eleven named omitted seed positions must be
present and pass; all 69 previously certified full-prime positions must be
present; a changed seed must fail the coefficient relation at each checked
position. Stop on the first failure and keep partial output; do not extend the
32-x cap, swap roots after observing failure, or silently omit a case. Use a
120-second overall wall watchdog and 10-second per-position watchdog where
the environment supports them. The run is a separate point certificate for
the *99 exact named positions* and does not resolve censored zero rows or
historical visitation. Preserve command, Sage version, git state, full output,
failure record if any, and resource use in a write-once path.
