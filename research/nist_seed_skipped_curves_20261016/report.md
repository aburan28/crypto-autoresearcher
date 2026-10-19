# The eleven skipped prime-field seed candidates

**Date:** 2026-10-16

**Question:** What mathematical traits distinguish the qualifying curves that the recovered NIST/ANSI seed streams passed over from the curves that were published?
**Status:** Reproducible structural assessment, supplemented by a check of a supplied 21-curve trait sheet. The historical reason for the omissions remains unknown.

## Scope and exact identities

The [Valsorda report][valsorda] names eleven unpublished candidates at specific one-based ordinals in four timestamp streams: five over the ANSI 239-bit field, two over the 192-bit field, one over the P-256 field, and three over the P-224 field. [Anthropic's primary writeup][anthropic] independently describes the same eleven omissions and cautions that the surviving numbers do not show how many generator runs took place. The P-384 and P-521 streams name no skipped qualifying candidate. The comparison set contains **ten published controls and eleven passed-over candidates, 21 curves in total**. A candidate present in a reconstructed stream is not proof that the historical program evaluated it and made an explicit rejection decision.

Every tested model is an ordinary short Weierstrass curve

\[
E_b/\mathbb F_p:\quad y^2=x^3-3x+b,
\qquad c\,b^2\equiv-27\pmod p,
\]

where `c` is the [NIST SP 800-186 Appendix C.3.1][nist] SHA-1 expansion of the recovered 160-bit seed. The four exact field primes are

| Field | Exact prime |
| --- | --- |
| 192 bits | `2^192 - 2^64 - 1` |
| 224 bits | `2^224 - 2^96 + 1` |
| 239 bits | `2^239 - 2^143 - 2^95 + 2^47 - 1` |
| 256 bits | `2^256 - 2^224 + 2^192 + 2^96 - 1` |

**Exact per-curve parameters** are in [assessed.json](assessed.json), one row per seed: full `p`, `a`, `b`, prime group order `n`, cofactor `1`, selected generator `(Gx,Gy)`, 160-bit seed, and full `curve_uid`. The [raw traits](traits.json) retain both square-root models, as well as the ten published controls. `curve_uid` follows the repository's EC1 representation-identity convention, so its generator is explicitly part of the identity. The skipped curves have no historically published generator; each stored `G` is a study-defined point chosen by the smallest nonnegative `x` with the smaller square-root `y`, then checked to have order `n`. This produces an exact comparison record without suggesting that this was the historical base point.

## Method and verification

1. [audit.py](audit.py) implements `srand48(timestamp)` with state `(timestamp << 16) | 0x330e`, 48-bit recurrence `x ← (0x5deece66d x + 0xb) mod 2^48`, and one candidate byte `x >> 40` per draw. Its one-based candidate ordinals reproduce all ten published seeds **exactly**, including P-384 and P-521, and OpenSSL's published `p,a,b,G,n,h` satisfy the NIST seed-to-coefficient check.
2. For each abbreviated unpublished seed in the [article][valsorda], it recovers all 20 bytes, applies SHA-1 expansion, computes both roots of `b² = -27/c`, and obtains the point count using Sage. It checks primality with Sage's proof mode, constructs a nonidentity point `G` with `[n]G=O`, and checks `n²>16p`. Since the Hasse interval has width `4√p<n`, the point check independently pins down `#E(Fp)=n` once the candidate `n` is known. These are checked computations, not a report of historical generation intent.
3. [audit.py](audit.py) also checks `p^k != 1 mod n` for every `1 ≤ k ≤ 100` and trial-divides quadratic-twist orders by every prime at most 10,000. [postprocess.py](postprocess.py) groups equivalent sign models, tests the twist residuals for proven primality, and applies the repository's exhaustive `small_discriminant_scan` through `|D_K|=2,000,000`. The scan is a rigorous bounded screen for low-degree noninteger endomorphisms. It does not determine the full endomorphism ring or `f_E`.
4. The later [supplemental checker](supplemental_checks.py) reads the frozen `traits.json` and `assessed.json` records and iterates `p^k mod n` for every `1 ≤ k ≤ 1,000,000` across all 21 rows. Its [machine-readable output](supplemental_checks.json) also recomputes the six UTC dates and the corrected P-521 trace and twist order; PARI/GP `isprime` checks the published P-384 and P-521 twists. This is a bounded modular screen, not a determination of the exact embedding degrees or a rerun of point counting.

The first run used zero-based indexing and was rejected by its own published-seed control. Its preserved [error log](audit_attempt1.log) shows that failure. The corrected [audit log](audit_attempt2.log) and [screening log](postprocess_attempt1.log) show the completed checks. The JSON files contain script SHA-256 values and exact numerical outputs. The SHA-1 coefficient procedure is [NIST primary documentation][nist]; the seed-stream and omission list are [Valsorda][valsorda] and [Anthropic][anthropic], both retrieved on this date. OpenSSL and Sage version strings are stored in `traits.json`.

## Results by candidate

`t = p+1-n`. The normalized trace `t/(2√p)` is shown to three decimals to compare positions in the Hasse interval; the underlying `t` is exact in the JSON. The twist column lists **only certified prime factors at most 10,000**; `P` means the remaining twist factor is proven prime, so that twist factorization is complete, while `C` means a composite residual remains unfactored. The field, seed and ordinal uniquely key each row to the exact parameter record.

| Field bits | Seed ordinal | Full seed (hex) | `n` vs `p` | `t/(2√p)` | Twist factors ≤10,000 | Residual |
| ---: | ---: | --- | :---: | ---: | --- | :---: |
| 239 | 36 | `25e56088185f8c3207b166cd2e007b88276afe78` | `<` | +0.730 | 139 | C |
| 239 | 1562 | `d09bfb7db85672dc700269f9189983f25f81958d` | `>` | −0.113 | 41 | C |
| 239 | 2491 | `1256fdd46eeb96b7d312ddb1de99bff159cf6701` | `>` | −0.151 | 43, 173, 307, 953 | C |
| 239 | 2682 | `d2c18e22558203444a2b33ea97c178675b438484` | `>` | −0.062 | 29 | C |
| 239 | 2863 | `3a700d3e6bf03255949804ba2a8677550c19ee11` | `<` | +0.447 | none found | C |
| 192 | 2198 | `692d90186057951de011733105bf1b3d3b0fc451` | `<` | +0.815 | 11, 127, 5827 | P |
| 192 | 5405 | `3ad10ff61797bc7258480cadd4e59c1ac1fb66d1` | `<` | +0.472 | 7, 19² | P |
| 256 | 876 | `50c71a63f911db7b2f31618ecf609d37154437f9` | `<` | +0.156 | 3, 11, 37, 8081 | C |
| 224 | 777 | `d00720e7691d403449c0d91be84bfb2c7501a267` | `<` | +0.376 | 3, 5, 683 | C |
| 224 | 1485 | `18cfdbcbb825568171212bc1610a5b8a8004e5c4` | `<` | +0.015 | 3, 31 | C |
| 224 | 5736 | `3c170a30ee6709df9b4c9ea0b6c1e95fcd6200ce` | `<` | +0.311 | 3, 1607, 3371 | C |

For each P-224 seed, **both** signs of `b` pass because `-1` has a square root `u` in this field. The map `(x,y) ↦ (-x,u³y)` gives an explicit isomorphism between the two equations. Thus the fourteen raw equations represent **eleven** seed-level isomorphism classes. Both signs and the map witness are in `traits.json` and `assessed.json`.

## Trait comparison and interpretation

- **Prime-order structure:** All eleven omitted classes have proven prime order, cofactor one, and order bit length no greater than their field bit length. They pass the article's stated extra bit-length screen. They are nonanomalous (`n ≠ p`), and none has `j=0` or `j=1728`. The generic subgroup size corresponds to approximately 96, 112, 119.5 and 128 bits of conventional square-root attack work for the respective field sizes, before implementation costs; this is a size estimate, not an attack measurement. [NIST SP 800-186][nist] likewise relates nominal strength to about half the base-point-order bit length.
- **Pairing and endomorphism screens:** Every skipped class, and all ten published controls, has embedding degree greater than 1,000,000 under the supplemental modular screen. This exceeds the `k ≥ 2^10` floor in [NIST SP 800-186 Appendix C.1][nist], but does not determine the exact `k`. None of the skipped classes has a CM field discriminant with `|D_K|≤2,000,000`; therefore a noninteger endomorphism of degree below 500,000 is excluded by this screen. The exact `D_K`, Frobenius conductor `f_pi` and representative conductor `f_E` are **not** determined. Candidate 239/#2682 has a visible `5³` factor in `|t²−4p|`, which only establishes a factor of 5 in `f_pi`; published prime239v2 also has a square factor of 5, and published P-224 has a square factor of 3. A list of small factors of `t²−4p` alone is not a complete CM-field or endomorphism-ring certificate.
- **Twists:** The two omitted 192-bit curves have fully certified twist factorizations consisting of the listed small factors and one proven large prime. The other nine have composite residuals, so their largest twist prime factor and complete twist security are unresolved. Ten of eleven have at least one twist factor at most 10,000; 239/#2863 has none in that range but its residual is composite. Published controls also show small twist factors. A small twist factor affects protocols that accept unchecked off-curve points; it is not an ordinary-group weakness in these prime-order curves.
- **Same-field isogeny comparison:** All eleven omitted group orders differ from every published order over the same prime field, and from one another. By the finite-field isogeny criterion, none is isogenous **over that base field** to a published curve in its field. This says nothing about paths over extension fields or maps to other groups.
- **Selection clues:** Three of the five omitted 239-bit candidates have `n>p`, but so does published prime239v2, so `n<p` cannot be the missing rule. The trace plot contains published and omitted curves on both sides of zero; all rows pass the same coarse conventional screens above. These traits provide **no identified rule** that picks precisely the published subset.

The [trace plot](trace.svg) compares all eleven omitted classes with eight published controls over the same four fields; [its editable source](render_visuals.py) also generates the [reconstruction diagram](selection.svg). There is no sampling uncertainty in these exact derived values. The plot is a structural comparison, not a statistical test of historical intent.

## Audit of the supplied complete-traits sheet

A separately supplied sheet titled *NIST/ANSI Pseudorandom Prime Curves Complete Trait Analysis* (2026-10-16; SHA-256 `4076201e051737c9c7086ed577ddfb7912d0c729611b5a67f153e53d80765f34`) was checked against the frozen reconstruction. Of its 21 per-curve sections, **18 match exactly, one skipped P-224 row uses the opposite isomorphic coefficient sign, and two published rows contain incorrect fields**. All eleven skipped candidates have the expected seeds, fields, orders, traces, and twist orders, and their coefficients match one of the recorded sign models. Of the ten published controls, the prime192v2 coefficient and P-521 field row require correction; the other eight match on the checked numeric fields. The [source-bound comparison output](supplemental_checks.json) names every exception and checks each sheet's three small-factor lists through 100,000: the only mismatches are P-521's discriminant-factor list and twist-order-minus-one list.

| Sheet claim | Checked correction and significance |
| --- | --- |
| “9 published” and “all 20” | Its own entries are **10 published + 11 skipped = 21**. |
| Six UTC date-time conversions | All six differ from `datetime.fromtimestamp(timestamp, UTC)`. The exact conversions are below and in `supplemental_checks.json`; the primary article gives the same dates. |
| prime192v2 `b = cc22…13ceab4` | The pasted value is 228 bits, exceeds the 192-bit field, and does not reduce to either sign of the published coefficient. Correct `b = 0xcc22d6dfb95c6b25e49c0d6364a4e5980c393aa21668d953`. |
| P-521 `p` labelled 513 bits | Correct `p = 2^521 - 1`. The sheet's truncated field makes its stated trace violate Hasse's bound and its twist order negative. With the correct field, the twist order is **positive, 522 bits, composite**, with factors 5 and 7 below 100,000; the small factors of `|t²−4p|` below 100,000 consist of 5, and twist-order-minus-one has factor 2. Exact integers are in the supplemental output. |
| P-384 twist prime | Confirmed for the correct published P-384 order by PARI/GP `isprime`. |

| `srand48` timestamp | Correct UTC date and time |
| ---: | --- |
| `863711343` | 1997-05-15 15:49:03 |
| `863966734` | 1997-05-18 14:45:34 |
| `871002724` | 1997-08-08 01:12:04 |
| `871696354` | 1997-08-16 01:52:34 |
| `872952608` | 1997-08-30 14:50:08 |
| `891607927` | 1998-04-03 12:52:07 |

The sheet's `n−1` and *twist-order-minus-one* factors agree with the checked arithmetic except for P-521's twist-order-minus-one list, but they are not factors of the curve or twist group orders. Pohlig–Hellman decomposes a discrete logarithm using factors of the **group order**. Smooth `n−1` therefore does not provide the proposed hidden Pohlig–Hellman weakness when `n` is prime. Actual twist-order factors for the skipped curves appear in the candidate table above. A small twist factor may matter to a protocol or implementation that accepts unsuitable points; it does not by itself weaken the prime-order group.

The sheet supplies no sampling model, predeclared equivalence test, or historical generator trace. Its “statistically indistinguishable,” “no structural discriminator exists,” and “roughly 50% rejection rate” statements do not follow. The narrower supported statement is that **these checked conventional traits identify no selection rule** among the 21 observed candidates. The fraction `11/21` describes passed-over qualifying entries in the reconstructed prefixes, not a measured probability of historical rejection. A bounded trait screen also cannot rule out every untested structural criterion or a withheld mathematical route.

## What remains open

The specific obstruction is the **unrecorded historical acceptance rule or implementation state** after a candidate passed the visible mathematical checks. It is tracked in the [named problem record](../../problems/nist-seed-selection-rule-unexplained.md). The present artifacts do not include the original generator program, its point-selection state, a complete log of runs, or enough history to distinguish a deliberate preference from an accidental skip. A discriminating next step would recover contemporaneous source/logs or identify a deterministic rule that classifies every accepted and passed-over seed in all six streams, including the published controls, without tuning on those outcomes; it should then predict an independent held-out run. Failing to find such a rule in these eleven cases would remain bounded evidence, not proof that none existed. This assessment does not enumerate every earlier rejected 20-byte block or search other timestamps.

The recovered timestamps and seed ordinals sharply constrain *one proposed* history of selection, but they do not certify how many timestamp runs were tried. Anthropic explicitly says that the surviving numbers do not show that count. The eleven omitted curves leave room for a local, unexplained choice among candidates; the available traits do not identify a hidden mathematical advantage or a specific selection mechanism. An estimate of roughly 30 bits of search freedom is conditional on the assumed timestamp window and bounded candidate search, not a measured upper bound on every possible historical procedure. A hypothetical costly intermediate advantage, retained secret map, or route over another representation would need its own explicit construction, subgroup-preserving transport, destination-solver advantage, secrecy analysis, and cold-start and amortized cost models. Public reconstruction of an equally useful route must be considered separately from recovery of the exact secret. These ordinary trait screens neither establish nor exclude such a route.

## Visual and source record

- [Reconstruction diagram](selection.svg), [normalized-trace comparison](trace.svg), both regenerated by [render_visuals.py](render_visuals.py).
- [Exact grouped records](assessed.json), [raw two-sign records and published controls](traits.json), [reconstruction code](audit.py), [bounded screening code](postprocess.py).
- [Supplemental verification script](supplemental_checks.py) and its [machine-readable results](supplemental_checks.json): 21-curve embedding-degree screen, date conversions, and published-control corrections. The supplied sheet is identified by SHA-256 above; it is not copied into the repository.
- [PDF version](report.pdf) and editable [Typst source](report.typ).
- The [trace graph](trace.svg), [selection diagram](selection.svg), and their [editable source](render_visuals.py) were checked against the corrected counts and exact candidate data; no plotted point or diagram edge changes. Existing canonical graphs checked: `knowledge/frontiers/ecdlp/` and `research/endosweep_nist_20261006/`; neither contains this historical seed-selection comparison, and no established mechanism edge changes from this assessment.

[valsorda]: https://words.filippo.io/seeds-solved/ "retrieved primary account"
[anthropic]: https://www.anthropic.com/research/ecdsa-curve-origins "retrieved primary discovery writeup"
[nist]: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-186.pdf "retrieved NIST primary specification"
