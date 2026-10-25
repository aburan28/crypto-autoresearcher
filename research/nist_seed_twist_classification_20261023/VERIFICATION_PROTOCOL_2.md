# Sage integer primality method correction

**Frozen:** 2026-10-23 UTC after `verification/20261023T2107Z` stopped before its first curve. The initial verifier called top-level `sage.all.is_prime(p, proof=True)`, which rejected the `proof` keyword. The API check `ZZ(101).is_prime(proof=True)` returned true on this host.

For a new write-once verification directory, change only the primality invocation to `p.is_prime(proof=True)` where `p` is already a Sage `ZZ` integer. Keep the source input hash, 21 curves, `j` rederivation, `twists()` enumeration, isomorphism checks, order identity and interpretation from `VERIFICATION_PROTOCOL.md` unchanged. Stop and preserve any further failure before amending again.
