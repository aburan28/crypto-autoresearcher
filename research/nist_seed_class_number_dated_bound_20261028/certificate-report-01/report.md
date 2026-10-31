# Dated CM class-number bounds: complete omission test

28 October 2026 UTC, T-5518. Observation report; no official research-state transition. Two frozen protocol versions and their original runs are retained.

## Observed result

All eleven reconstructed omissions and eight published controls have directly checked maximal-order class-number lower bounds h(K)>=2^24=16,777,216. Every certified row clears both dated bounds. Published P-384 and P-521 remain UNKNOWN_D_K for this method because a certified fundamental field discriminant was not imported. All 21 identities and six streams remain in the table. No row was treated as rejected on missing data.

| Curve / block | Label | Direct-certificate status | Certified lower bound |
|---|---|---|---|
| omitted 239 / 36 | omitted | CERTIFIED | 16,777,216 |
| omitted 239 / 1562 | omitted | CERTIFIED | 16,777,216 |
| prime239v1 | published | CERTIFIED | 16,777,216 |
| prime239v2 | published | CERTIFIED | 16,777,216 |
| omitted 239 / 2491 | omitted | CERTIFIED | 16,777,216 |
| omitted 239 / 2682 | omitted | CERTIFIED | 16,777,216 |
| omitted 239 / 2863 | omitted | CERTIFIED | 16,777,216 |
| prime239v3 | published | CERTIFIED | 16,777,216 |
| prime192v1 | published | CERTIFIED | 16,777,216 |
| omitted 192 / 2198 | omitted | CERTIFIED | 16,777,216 |
| prime192v3 | published | CERTIFIED | 16,777,216 |
| omitted 192 / 5405 | omitted | CERTIFIED | 16,777,216 |
| prime192v2 | published | CERTIFIED | 16,777,216 |
| secp521r1 | published | UNKNOWN_D_K | unknown |
| omitted 256 / 876 | omitted | CERTIFIED | 16,777,216 |
| prime256v1 | published | CERTIFIED | 16,777,216 |
| secp384r1 | published | UNKNOWN_D_K | unknown |
| omitted 224 / 777 | omitted | CERTIFIED | 16,777,216 |
| omitted 224 / 1485 | omitted | CERTIFIED | 16,777,216 |
| omitted 224 / 5736 | omitted | CERTIFIED | 16,777,216 |
| secp224r1 | published | CERTIFIED | 16,777,216 |

Full field/model/order/seed/ordinal, exact UID, fundamental discriminant, first 24 split primes, exact product Q and outcome are in cohort.csv and the immutable version2 RESULT.json. The editable certificate-margins.svg plots floor(log2(|D_K|/(4Q))) derived from the recorded integers; the minimum is 23 bits. Both omitted and published rows are shown. This margin is sufficient-certificate slack, not a stronger class-number estimate.

## Fixed dated requirements

* [Baier, dissertation, submitted 26 March 2002, section 2.3.5](https://d-nb.info/964515040/34): h(K) >= 200.
* [ETSI TS 102 176-1 V1.2.1, July 2005, 6.1.2.3 and D.3](https://www.etsi.org/deliver/etsi_ts/102100_102199/10217601/01.02.01_60/ts_10217601v010201p.pdf): h(K) >= 200.
* [RFC 5639, March 2010, section 2.1 item 3](https://www.rfc-editor.org/rfc/rfc5639.html): h(K) > 10^7.

All concern the maximal CM order. Baier describes the German condition as controversial and outside the then-common international criteria. These sources postdate 1997 and do not establish NIST adoption. The requested original Brainpool 2005 PDF timed out; no claim is made about unread contents. The prior all21 h<=2000 list comparison conditionally clears200; the new nineteen certificates do not depend on that external completeness theorem or GRH.

## Certificate and order distinction

The first 24 rational split primes q_i are selected in ascending order with fixed cap10000. Let Q be their product. For fundamental D_K<0, 4Q<|D_K| implies h(K)>=2^24: distinct subset products of prime ideals have distinct classes. Otherwise cancellation would produce an integral principal ideal of squarefree norm N,1<N<=Q. A rational generator has square norm; a nonrational algebraic integer has norm at least |D_K|/4. Both contradict that N. CERTIFICATE-LEMMA.md gives the argument. This is an elementary exact certificate, not the full class-group computation.

The class map from a CM order to the maximal order is surjective, so h(O_K) divides h(End(E)). Each certified lower bound therefore also applies to the actual CM order without determining its conductor. The reverse inference from a large Frobenius-order class number would be invalid. For both P-256 rows the imported factorization gives f_pi=1, hence f_E=1. Published P-256 has3 as a ramified factor of D_K; that3 is not its CM conductor.

## Execution, controls and amendment

Version 1 protocol SHA1fa24263792c84ebf0040ffb7e1b0d03bdb0fe7d21040b5be976a5ca05e53c7e was frozen and committed at72c533ee10 before execution. Its two arms agreed on17 certificates and4 unknowns. Input assembly had omitted the separately archived P-256 first-stage pair. All first outputs and guard failures remain under runs/certificate-01 and export.json.

Version 2 SHA4371127490749adf5413200c7f60710c39347039b7ad179573ec7461438fecb4 was frozen and committed at9c3872cc7f before the two added inputs' witnesses. IMPORT-CHANGE.json pins the original P-256 source and identifies the only two changed records. Producer/audit bytes, threshold, prime-selection rule and all other rows are identical. Both full21 evaluations repeated, giving19 certificates and2 unknowns. Raw version2 commitc58405ea3f precedes this report. No threshold or feature was fitted after either output.

Python 3.13.1 uses trial division for the small primes and Euler symbols; PARI 2.17.3 independently uses nextprime and Kronecker symbols and proves all supplied discriminant factors with isprime. Both check Delta_pi=(p+1-n)^2-4p=f_pi^2 D_K, the complete factor product, square class and fundamental-discriminant relation. Original p,n and curve validity are inherited from the pinned prior records, not newly point-counted here. Source/runtime/input/analysis hashes and exact commands are retained.

Positive controls D=-23/-15,k=1 certify bounds2 (GP exact class numbers3,2); D=-7 correctly returns noncertificate; D=-75 is rejected as nonfundamental; deterministic A/A passes. Exception and early-return controls each exit1 without completion. Across both versions: 4 requested/attempted/completed whole-cohort arm evaluations,0 unexpected failures/timeouts/retries, 4 deliberate failure-guard invocations retained separately. Both experiment.export/v1 checks pass, each flow2/2 complete. CPU/wall receipts are diagnostic on a shared macOS desktop,L0; no performance comparison or attack cost claim.

## Inference and limits

For the two specified dated bounds, zero of eleven omissions fails. Thus this class-number requirement cannot account for any of those omissions; adding it to a two-rule rejection model contributes no exclusions at these bounds. This does not exclude arbitrary different thresholds, other CM predicates, operational failure during class-number validation, or a different historical implementation. Those would need source evidence and a separate prospective test. P-384/P-521 unknowns do not affect the all-eleven result. Reconstructed omissions are not documented original visitation/rejection events.

The historical selector remains unresolved. Existing general CM/transfer and P-224 splitting leads remain separate. Canonical signed-action/SEA graphs were checked and left unchanged: these observations change no isogeny edge, signed action or historical-use claim. This report and its linked result add the dated-bound outcome to the selector problem and study index. No new catalog comparison was needed: this tests exact frozen cryptographic instances, outside the local LMFDB indexes' arbitrary-field coverage.

Next historical discriminator: a dated caller or validation specification that imposes a different concrete endomorphism/class-group condition, or documents failure handling. Do not tune a new bound to these labels or repeat the completed fixed-bound test.
