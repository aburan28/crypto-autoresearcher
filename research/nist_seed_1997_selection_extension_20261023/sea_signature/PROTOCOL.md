# Frozen small-prime point-counting signature screen

Frozen 2026-10-23 local time before calculating any curve signatures in this round. This is an exact retrospective structural screen and a proxy for one possible old point-counting workload, not a replay of the unknown 1997 program or an ECDLP experiment.

## Inputs and question

Use the eleven seed-level omitted rows in `research/nist_seed_skipped_curves_20261016/assessed.json` and the eight same-field published rows in `traits.json` (prime192v1/v2/v3, prime239v1/v2/v3, secp224r1, prime256v1). Pin SHA-256 digests. Check the source `p,n,t,Delta` identities and unique EC1 curve UIDs. Do not include published P-384 or P-521 in within-field comparisons because these archives have no omitted control in those fields.

Question: could a simple deficiency of small Elkies primes distinguish every omitted curve from the published controls, and thereby suggest a point-counter timeout rather than a security filter?

## Fixed computation and metrics

For every odd prime ell <= 997, compute the Legendre symbol of `Delta = (p+1-n)^2-4p` modulo ell, where ell != p. Label +1 Elkies, -1 Atkin, 0 ramified. This signature is determined by the exact archived `p,n`; it does not measure 1997 runtime. For each curve record the full ordered signature.

Primary metric: scan ascending odd primes, multiply only Elkies primes into `M`, and report the first ell for which `M^2 > 16p`, plus the number of odd primes scanned, the number of Elkies/Atkin/ramified primes seen, and M. This is a deliberately favorable Elkies-only CRT information proxy for uniquely recovering a trace within Hasse's interval. Fail closed if ell=997 does not suffice. Secondary fixed metrics: Elkies counts through ell=101 and ell=251. Ramified primes contribute no information to this particular proxy. Atkin information, cost per modular polynomial, and implementation behavior are outside scope.

Compare all 25 within-field omitted-published pairs for each metric, recording direction and ties. A simple universal timeout rule of the form `reject if cutoff > c` requires the smallest omitted cutoff to exceed the largest published cutoff in **each** field under one global c; calculate exact extrema and counterexamples. A perfect retrospective split remains only a candidate, because labels are known and the metric was chosen after studying this story.

## Controls, verification, limits

Synthetic controls: for ell=11, assert Legendre(1)=+1, Legendre(2)=-1, and Legendre(0)=0; assert the strict CRT boundary with M=4, p=1 (`M^2 == 16p`) does not pass and M=5 does. Independently check every sign with Sage's `kronecker` or `legendre_symbol` for all 19 curves, not by importing the Python output. Verify the digest and UID set, all Hasse inequalities, counts, and signature enumeration. Limit this run to 19 exact rows and 166 odd primes <=997, with a 60-second wall watchdog. Preserve source, stdout/stderr, environment/version, raw JSON, independent check, report, editable diagram and graph, SVG and inspected PDF. A timeout or verifier failure is infrastructure, not an observed mathematical distinction.

No later feature or threshold is added to this round. The task stops after these fixed outputs. A candidate workflow explanation needs original code, per-candidate state and time limit, and a source-identical replay. A cryptanalytic interpretation additionally needs an attack on the exact prime-order group with full costs and matched published controls.
