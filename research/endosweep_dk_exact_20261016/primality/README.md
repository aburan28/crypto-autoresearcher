# Primality certificates for the D_K-exact factors above 10^8 (2026-10-29)

Closes the "unrecheckable" gap in `../README.md` ("Every factor is proved prime
with PARI `isprime`") and in the `largePrimes` hypothesis of
`formal/CryptoResearch/Endosweep/DkExact*.lean`.

* `certificates/<N>.json`: one ECPP certificate per distinct factor (`kind: ecpp`,
  PARI 2.15.4 `primecert` steps `[N, t, s, a4, [x, y]]`), or `kind: small` for
  `N < 2^64` where PARI's own proof is BPSW.
* `manifest.json`: each factor -> certificate SHA-256, both verdicts, and every
  card that uses it (Lean card and `factorizations.jsonl` curve).
* `certify.py`: regenerates everything (`gp` required). Refuses to run if a
  card's `largePrimes` is not exactly its odd-exponent factors above 10^8, or a
  JSONL factor appears in no Lean card.
* `verify_ecpp.py`: independent checker, standard library only, no PARI.
  Verifies each Goldwasser-Kilian/Atkin-Morain step (size condition
  `q > (N^(1/4)+1)^2` in exact integers, nonsingularity, `[q]([s]P) = O`) and
  proves the last `q` prime by a Pratt certificate. `test_verify_ecpp.py`
  (112 tests) shows it accepts all 98 certificates and rejects tampered chains,
  composites and a fabricated step.

Result: 98 distinct factors (82 are odd-exponent `largePrimes` entries; 16 occur
only with even exponent), 98/98 valid under both `primecertisvalid` and
`verify_ecpp.py`; no failures.

Establishes: each of these 98 integers is prime (given the checker's correctness,
which `test_verify_ecpp.py` exercises but does not prove). Does not establish: that
the factor lists multiply back to the discriminants (done in `DkExact*.lean` by
kernel arithmetic), primality of `p` or `n` (not part of this claim), any
elliptic-curve fact, or Lean-level primality: the Lean files still take
`IsPrimeNat` of these factors as an explicit hypothesis.
