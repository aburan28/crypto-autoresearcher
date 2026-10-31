# All-root SEA branch audit of the fixed NIST/ANSI cohort

2026-10-27. Descriptive execution and independent arithmetic observations. Historical selection remains unresolved.

## Exact question and cohort

Could choosing a different rational root of a modular equation lead to an exceptional invariant or failed eigenvalue calculation, explaining any of the reconstructed omissions? This audit follows every rational root at levels 3, 5 and 13 in the available LiDIA build, rather than repeating its full point counts. The cohort contains exactly 21 curves: 11 reconstructed omissions and 10 publications across all six recovered streams. The source program is not authenticated as the original generator.

Exact field, a=-3 model, b, order, seed, stream timestamp, ordinal and full curve UID are retained in evidence/attempt-02/{PROTOCOL.json,cohort-inputs.json,traits.json}. comparison.csv retains every full curve UID. The cohort-input SHA-256 is 93ac4774b993a994a17d9327df92e0f2b287e66755cd933fdc683015fec1d545. No post-endpoint candidates were added.

## Measured execution and independently verified arithmetic

The successful attempt completed all 63 curve/level specializations. It emitted 39 rational modular roots and completed 78 kernel/profile checks (one direct Y-coordinate profile and one pre-Dewaghe ambiguous X-coordinate profile per root); 35 specializations used the Atkin branch. All 78 quotient/root Fricke checks passed. No actual cohort specialization failed, aborted or timed out. These are counts of this observer workload, not full point counts or performance estimates.

The observer receives only p, a, b and the auxiliary prime. It receives no subgroup order, known trace, seed ordinal or publication label. Only private/protected access labels are exposed in a local observer header; the linked static library is unchanged. The independent Python replay reconstructs every specialized modular polynomial from frozen coefficients, verifies squarefreeness and the complete root set using gcd(F,X^p-X), checks every kernel against an independent division-polynomial recurrence, checks the Velu quotient and its F_p isomorphism type, ties the selected root to the quotient using the Fricke involution, and checks each resulting trace relation against the certified input order. Distinct modular roots must have distinct kernels.

## Controls and retained failures

The first attempt invoked nine controls and stopped because the modular-table directory was absent from its minimal environment. All nine returned TABLE_UNAVAILABLE; zero cohort specializations ran in that attempt. The second attempt supplied the source-supported LIDIA_ECO path to the same frozen local tables, then ran nine controls before the 63 named cases. All three generic controls completed. Constructed j=0 controls at levels 3 and 13 reached the explicit tildeEf E4_tau division-by-zero guard; the j=1728 level-13 control reached an undefined-inverse error. Those three controls terminated with SIGABRT and are preserved as source exceptions, not mathematical rejections. The other three exceptional-invariant controls completed. Total native observer invocations: 81 = 9 + 9 + 63.

Independent controls include brute-force point counts over F_1000003, an explicit order-3 kernel on y^2=x^3+1 over F_101 with its Velu quotient, a nonkernel negative control, and polynomial division controls. Local LMFDB manifests were consulted: the complete av_fq index (source public.av_fq_isog, extraction ended 2026-10-19T16:45:49.243703+00:00) has genus-1 coverage only through q=1024. It contains neither these large prime fields nor the constructed q=1000003 control. No catalog identity claim is made.

The initial compile ambiguity and both offline auditor versions are retained. The stronger auditor adds modular-table reconstruction, quotient/root binding and distinct-kernel checks to the first passing auditor; it does not change or repeat any native capture.

## Observed splitting patterns

These are post hoc descriptions of this fixed sample, not predeclared predictive tests or historical rules. Rational root counts are exact deterministic values for the frozen models and tables; no sampling uncertainty or p-value is assigned.

| Field bits | Level | Published root counts | Omitted root counts |
| --- | --- | --- | --- |
| 192 | 5 | [1] | [0] |
| 224 | 3 | [4] | [1] |
| 239 | 13 | [0] | [1, 2] |
| 256 | 5 | [1] | [0] |

P-224 therefore retains its specific four-roots-versus-one-root lead. P-192 and P-256 retain a level-5 root-versus-no-root lead, and P-239 retains a level-13 no-root-versus-root lead. These descriptions require different field-dependent choices. A predicate in just the three root counts cannot classify the whole cohort: omitted P-192 ordinal 2198 and published P-239 ordinal 2185/P-384 ordinal 2688 all have (0,0,0). Field-dependent rules remain possible, but this source takes all of these branches successfully and does not implement those descriptions as rejection gates.

## Source dating and inference boundary

Compatibility amendment: the inherited static-library build includes the recorded pre-Dewaghe sign-ambiguity switch. With NIST_PRE1998_X set, test_x_coordinate_uniquely returns false, retaining both X-coordinate trace signs. This is an explicit reconstruction amendment preserved in source/pre-dewaghe-sign.patch, not authenticated 1997 source. The all-root observer itself adds access-label changes only.

Measured source: passagemath/upstream-LiDIA commit 23dac491f4cd96eb7de648a5cf90eb9ec77653c8; version string 2.3.0+latte-patches-2019-05-02. The full fetched Git history starts with a 2013 import of release 2.3.0. The initial-import NEWS says the point-counting package was integrated in 2.1pre2. The retained ChangeLog dates documentation of the newly inserted package to 2001-06-05. It records a splitting-degree fix and an occasional-crash comparison typo on 2001-09-15, and a schoofpart failure fix on 2004-03-15. These messages do not identify the old faulty lines, date creation of standalone ECO, or demonstrate generator use. No speculative reversal of a comparison has been presented as recovered code.

For this precise build and these levels, every rational-root branch produced independently valid arithmetic for both profiles. Consequently these captures provide no omission-specific failure mechanism. They leave earlier implementations, other levels, optimizer settings and an external caller policy untested. They do not turn all later point counters into reconstructions of a 1997 program. The original selection criterion is not identified.

The next source-dependent test is to recover a dated pre-fix or standalone point counter, identify the exact corrected path, freeze its prediction without label-dependent changes, and check all 21 inputs. Arbitrary field-specific Boolean fits cannot establish that history.

## Evidence and reproduction

Top-level observer and auditor copies are browseable mirrors. Run the verifier inside the extracted evidence directory, where its sealed source/table/input paths are present.

The raw evidence archive includes every native capture, source/table/static-library bindings, both frozen protocols, failures, controls, observer and independent arithmetic replay. Extract evidence.tar.zst, then run `python3 -B evidence/verify.py`. The replay verifies 489 sealed files and repeats only pure Python arithmetic, launching zero native point-counting programs. The exact source/static-library build is retained for provenance; this is a portable arithmetic replay, not a claim of a portable historical build.

PROTOCOL SHA-256: b80560225b69b2cbb8370f01e26946164ef03b3d30055b31e50605a3566834ab. Seal SHA-256: eee2ca89c74ec4ca9fe5dc57ac5d46821c754900f48c3b0ca35e04a2bde52b44. Archive bytes/hash are in BUNDLE.json. Canonical graphs were checked by scope: this audit records no official hypothesis decision and changes no previously established map, conductor or transfer claim, so none was revised.

Primary sources:

- https://github.com/passagemath/upstream-LiDIA/tree/23dac491f4cd96eb7de648a5cf90eb9ec77653c8/src/ec_order
- https://github.com/passagemath/upstream-LiDIA/blob/23dac491f4cd96eb7de648a5cf90eb9ec77653c8/ChangeLog
- https://github.com/passagemath/upstream-LiDIA/blob/0171e66/NEWS
- Historical question: https://words.filippo.io/seeds-solved/

The old Darmstadt distribution URL and Wayback index requests were inaccessible through the web reader in this search. A failed retrieval is not proof that a release or archive does not exist. The Coster/SVIC lead yielded bibliographic references but no authenticated 1997 source release, and was not executed.
