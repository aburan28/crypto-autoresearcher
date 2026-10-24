# Exact embedding-degree screen of named NIST/ANSI seed candidates

Frozen 2026-10-23 UTC before computing any embedding degree in this round.
This is an exact class-invariant screen, not an attack-cost benchmark or a
reconstruction of the historical selection program.

## Inputs and scope

Use the eleven omitted and eight same-field published prime-field classes in
`research/nist_seed_skipped_curves_20261016/assessed.json` (SHA-256
`370e79ce0bff8f26bb437fe37d1756f3f8261a5c00e9062ba41cf70f272e8841`)
and `traits.json` (SHA-256
`a1102bd487379d223581863fab731d6eb6957bf0e264b450f1c7b298279b0b67`).
Use the complete `n−1` factorizations in the sealed
`research/nist_seed_order_certificate_20261023/runs/certificate-20261023T1747Z/results.json`
(SHA-256 `59dae2376fcc477fcfcf69b8a3d5b592b81c15726d33ca61e2ee7e4bc6c9ec32`),
whose proof-enabled factor verification is in `verification.json`
(SHA-256 `c1375cf10666797817794b46af39c88123b7de9080c02ef75041a6d90afea756`).
Bind each row by exact EC1 UID, `p`, and prime group order `n`; refuse a missing,
duplicate, censored, mismatched, or unverified factorization. P-384/P-521 are
excluded because they have no omitted same-field candidate in the named set.

## Calculation and controls

For each prime `n`, calculate `k = ord_n(p)` by starting at `n−1` and
repeatedly dividing by each proven prime factor `q` while
`p^(k/q) ≡ 1 (mod n)`. Check `p^k ≡ 1 (mod n)` and
`p^(k/q) != 1 (mod n)` for every distinct prime `q | k`; together with the
complete factorization of `n−1`, these certify minimality. Report `k`, its
decimal size and bit length, prime factors inherited from `n−1`, and whether
it is at most each fixed bound `100, 1,000, 10,000, 1,000,000`.

Use arithmetic controls with exact expected orders: `ord_11(2)=10`,
`ord_13(3)=3`, `ord_17(4)=4`. Reject a negative control with modulus `n=15`
as outside the prime-order input contract. Verify every real `k` independently
in Sage from `p,n` with `Mod(p,n).multiplicative_order()` and check the
reported minimality witnesses, source digests, labels and UIDs. Retain exact
commands, software versions, source commit and output hashes. All computation
is deterministic; bound a run to 120 seconds and 1 GiB resident memory.

## Interpretation fixed in advance

If all eleven omitted `k` values are below a fixed threshold while all eight
published controls exceed it, record a *candidate* class-invariant selector,
then analyze actual MOV/Frey–Rück finite-field DLP cost before any weakness
claim. A small `k` alone is not such a cost. If both labels exceed all bounds,
or overlap at every fixed bound, the specified small-embedding-degree selector
does not explain these skips. Report all exact values and within-field
counterexamples, not only the threshold result. Neither outcome proves how
the 1997–98 program behaved; an exact label split still needs a dated rule or
held-out prediction and historical provenance. Preserve any timeout, crash or
failed control without treating it as negative mathematical evidence.

Publish an evidence-linked report, editable diagram, quantitative SVG and
visually inspected PDF. Update the existing selection-rule obstruction if the
result changes its tested-scope evidence; leave official statuses to the
Coordinator.
