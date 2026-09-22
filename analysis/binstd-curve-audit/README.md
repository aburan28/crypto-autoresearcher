# Standardized binary-curve audit (BINSTD seed)

Pre-compute structural audit of the named binary-field elliptic curves that
`RQ-BINSTD-b6f698` takes as targets. Nothing here is an experiment, a run, or
evidence; it is a **derived, regenerable fact sheet** that the ideation batch of
2026-09-22 cites instead of recalling curve parameters from memory.

Everything below was computed in this repository, from parameters the local
OpenSSL emits, by the two scripts in this directory. Regenerate with:

```sh
./dump_params.sh > binary-curve-params.txt
python3 subfield_scan.py     > audit-scan.txt
python3 subfield_certify.py  > audit-certificate.txt
```

## Provenance

| item | value |
| --- | --- |
| parameter source | `openssl ecparam -name <curve> -param_enc explicit -text -noout` |
| OpenSSL build | 3.0.13, 30 Jan 2024 (`/usr/bin/openssl`) |
| curves dumped | 31 named binary curves: SECG/NIST `sect*`, ANSI X9.62 `c2tnb*`/`c2pnb*` |
| computed | 2026-09-22, branch `claude/elliptic-curve-discrete-log-62k04u` |

OpenSSL's named-curve tables are a **secondary** source. They agree with FIPS
186-4 and ANSI X9.62 as far as this audit read them, but no primary standards
document was opened here. Any record that needs the parameters at claim
strength re-derives them from the primary standard and says so; this file is
provenance `internal`, confidence `computed-here`.

## What the scan does

`subfield_scan.py` parses each curve's field polynomial `f`, coefficients
`A`, `B`, subgroup order and cofactor, then for every proper divisor `d | m`
tests subfield membership of `A` and `B` in `F_{2^d}` by the Frobenius
fixed-point test `a^(2^d) == a`, evaluated in `F_2[x]/(f)` with carry-less
multiplication and polynomial reduction. `A == 0` is in every subfield and is
reported as such.

`subfield_certify.py` takes the five composite-degree curves further. If `E` is
defined over `F_q`, `q = 2^16`, with trace `t`, then `#E(F_q) = q + 1 - t` and
`#E(F_{q^k}) = q^k + 1 - s_k`, where `s_0 = 2`, `s_1 = t`,
`s_{i+1} = t·s_i - q·s_{i-1}`. The script reads `t` off the published cofactor,
checks it against the Hasse bound, runs the recursion to `k = m/16`, and
compares the result with the published `cofactor × order`.

## The result

**All five composite-degree ANSI X9.62 binary curves are subfield curves
defined over `F_{2^16}`.** For each, `A` and `B` lie in `F_{2^16}`, the
extension degree is `m = 16k` with `k` prime, the trace implied by the cofactor
satisfies the Hasse bound, and the Weil recursion reproduces the published
group order **exactly**:

| curve | `m` | `k = m/16` | `A, B ∈ F_{2^16}` | cofactor | implied `t` | `#E(F_{2^m})` reproduced |
| --- | --- | --- | --- | --- | --- | --- |
| `c2pnb176v1` | 176 | 11 | yes | 65390 | 147 | yes |
| `c2pnb208w1` | 208 | 13 | yes (`A = 0`) | 65096 | 441 | yes |
| `c2pnb272w1` | 272 | 17 | yes | 65286 | 251 | yes |
| `c2pnb304w1` | 304 | 19 | yes | 65070 | 467 | yes |
| `c2pnb368w1` | 368 | 23 | yes | 65392 | 145 | yes |

Every other curve in the dump has **prime** extension degree — `m ∈ {131, 163,
191, 193, 233, 239, 283, 359, 409, 431, 571}` — and no proper subfield contains
`A` or `B`. That includes every NIST/FIPS binary curve (`K-163` … `B-571`,
`m ∈ {163, 233, 283, 409, 571}`) and the ANSI `c2tnb*` family.

## Why it matters to RQ-BINSTD-b6f698

The standardized binary population splits cleanly into two index-calculus
regimes, and the split is a property of the curves, not of anyone's opinion:

1. **Prime extension degree** (every NIST binary curve, every `c2tnb*`, every
   `sect*`, and ECC2K-130 at `n = 131`). GHS-style Weil descent to a proper
   intermediate subfield has no intermediate subfield to descend to. The
   index-calculus lane here is Semaev/Nagao point decomposition with descent to
   `F_2`, the quasi-subfield-polynomial line (`RQ-QSP-f9bbdb`), and the
   Frobenius structure of the Koblitz members (`RQ-FROB-7d8dd4`).
2. **Composite extension degree `16k`, curve defined over `F_{2^16}`** (the five
   `c2pnb*` above). This is simultaneously the GHS/Weil-descent class and the
   subfield-curve class `RQ-FROB-7d8dd4` defines — `E/F_q` attacked over
   `F_{q^k}`, `q = 2^16`, `k` prime — at deployed parameters rather than at toy
   scale. The 16-fold Frobenius orbit structure and the `≈ 2^16` cofactor are
   both consequences of the same fact.

These five curves being composite-degree is not news — the composite-degree
binary curves have been discussed as Weil-descent candidates since the GHS
literature (`KN-LIT-007`, `KN-LIT-090`, `KN-LIT-6987`, `KN-LIT-449`). What this
audit adds is that **this program has now checked it**, with a reproducible
script and an exact point-count certificate, rather than carrying it as
recollection. No claim is made here about whether any attack on them is
feasible; that is the research question's business, and every cost in it is
charged there.

## Scope limits

- Secondary parameter source; no primary standards document was read.
- The audit is arithmetic on published parameters. It solves no ECDLP instance,
  runs no attack, and establishes no cost.
- Deployed parameters remain **arithmetic-only** targets under the program's
  standing norm: nothing in `RQ-BINSTD-b6f698` runs an attack at `m ≥ 131`.
  Executable cells are toy curves; the named curves appear only in computed
  cost tables under stated, numbered assumptions.
