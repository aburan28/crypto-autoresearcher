# EXP-MONO-917e3a implementation notes

`implementation/witness_search.py` implements standard short-Weierstrass
elliptic-curve point addition/negation over `F_p` (prime `p`, no library
dependency), a brute-force point finder (scans x-coordinates, rejects
2-torsion points with `y=0`), and a witness checker that computes all
`2^{m-2}` signed sums of `m-1` points (sign vector `eps` with `eps_1=+1`
fixed) and reports whether the resulting x-coordinates are pairwise
distinct.

Run directly: `python3 implementation/witness_search.py`. No CAS, no
external dependency, no randomness — every reported curve, point, and root
is an explicit, reproducible input/output pair recorded in
`runs/RUN-MONO-917e3a-1/raw-result.json`.

The one disclosed anomaly: the first m=5 attempt (same curve as the m=4
witnesses, `xstart=2`) produced a collision between two distinct sign
classes. This is expected and harmless — the underlying mechanism
(IDEA-20260904-0417a5) only requires existence of one clean witness per
arity, not that every arbitrary point choice succeeds. A second attempt
(`xstart=17`, same curve) produced a fully clean witness.
