# K-283 conductor-1697 census

Status: **implementation only; not yet executed through the canonical `run` entry point.** Values below are frozen expectations or exact parameter derivations, not measured output.

## Question

For NIST K-283,
`y^2 + xy = x^3 + 1` over
`F_2[x]/(x^283 + x^12 + x^7 + x^5 + 1)`, enumerate the `1697`-direction floor at `f_E = 1697` and test whether a split degree-37 ideal
acts transitively on it.

The named Koblitz model has an explicit absolute Frobenius endomorphism and
`f_E = 1`. Its q-Frobenius conductor is

```text
f_pi = 489878522800087734083485536590018444665943
     = 1697 * 162254089 * 1779143207551652584836995286271.
```

This round studies only the first factor, 1697. It is the bottom in the
1697-direction, not the global bottom across the other conductor primes. The order has
discriminant `D = -7 * 1697^2 = -20158663`.

## Frozen gates

The producer and independent verifier must establish all of the following or
fail closed:

- the standard NIST field polynomial is irreducible;
- the pinned SEC2 subgroup order is prime, the cofactor is 4, and the source
  order and trace equal the K-283 values;
- the Frobenius discriminant equals `-7 f_pi^2`;
- `h(-20158663) = 1698`;
- the Weber class polynomial has degree 1698 and, modulo 2, six distinct
  irreducible factors of degree 283;
- the census contains exactly 1,698 distinct nonzero `b` values, all with
  `a2 = 0`, and exactly matches the separately recomputed CM roots;
- every model has the standard K-283 group order;
- all endpoints have Frobenius orbit size 283, in exactly six orbits;
- the degree-37 ideal class has order 1698;
- the distinct rational degree-37 endpoint at the crater is the crater itself;
- a non-backtracking degree-37 walk from the floor has length 1698, visits
  every census endpoint once, and has no outside or missing vertex.

The census script rejects an invalid explicit field modulus. The verifier
rejects malformed rows and a file to which GP's `write()` appended a second
expression.

## Claim boundary

A passing run would certify an endpoint census and the 1697-direction order level. It would **not** establish any of the repository's weak-curve claim
labels.

In particular, this implementation does not construct the degree-1697
source-to-floor isogeny, its dual, or a subgroup-preservation certificate.
The direct 1697-kernel route is predicted to require an extension of degree
848 over `F_(2^283)` (absolute degree 239,984). The CM census identifies
models without supplying that transfer. It also does not measure an ECDLP,
an attack cost, or a speedup.

The full-degree Frobenius orbits and absence of `j = 0` are negative checks
for two obvious endpoint traits--proper-subfield definition and exceptional
automorphisms--but they do not rule out other representative-dependent
structure.

## Execution and evidence

These scripts are reusable implementation material and may land before an
experiment ID. Scientific execution must be packaged into a frozen
`EXP-*` contract, pass the repository's capacity/readiness checks, and be
launched only through the canonical `run` entry point. Do not treat an
ad-hoc GP invocation or CI smoke test as a canonical run.

Expected generated files, once admitted, include the floor vector, captured
stdout/stderr, resource measurements, dependency versions, and SHA-256
digests. The later research record must label the result as observation until
independent review and must charge construction, evaluation, path discovery,
memory, data, and precomputation before making any transfer claim.
