# Dated class-number bound: source and prospective certificate plan

User-directed continuation, 28 October2026 UTC, T-5518. The full historical selector remains unresolved.

Fixed source bounds, before any new certificate evaluation:

* Baier2002 dissertation, submitted26 March2002, examined7 May2002, section2.3.5: maximal CM-order class number at least200. Primary text https://d-nb.info/964515040/34 .
* ETSI TS102176-1 V1.2.1 July2005, clause6.1.2.3 and AnnexD.3: h(K)>=200 for the maximal order; order class number is a multiple of h(K). Primary https://www.etsi.org/deliver/etsi_ts/102100_102199/10217601/01.02.01_60/ts_10217601v010201p.pdf .
* RFC5639 March2010 section2.1 requirement3: h(K)>10^7, explicitly maximal order of the quotient field of End(E). Primary https://www.rfc-editor.org/rfc/rfc5639.html . Original Brainpool2005 PDF timed out; no1997 attribution inferred from these later texts.

Existing all21 h<=2000 list-comparison result conditionally settles the200 threshold: all pass if the external list completeness theorem holds. It does not settle10^7. Preserve that dependency rather than claiming an independent exact class-number calculation.

Next new check: produce an unconditional class-number lower-bound certificate from small split primes for every input with a certified fundamental D_K. Do not substitute the Frobenius-order discriminant for D_K. Missing fundamental discriminants remain UNKNOWN, and all21 rows stay present. Existing19 matched-field conductor records include all11 omissions; verify exact input identities and source certificates before relying on that coverage.

Use k=24 solely because2^24>10^7. Select the first24 rational primes splitting in K, in ascending order, skipping ramified primes. The fixed certificate condition is4*product(primes)<abs(D_K); no tuning. If it fails, return NOT_CERTIFIED, not h(K)<=10^7. No exact h(K) or historical use is claimed.

Two planned verification methods: Python integer/Kronecker arithmetic and independent PARI exact primality/Kronecker/product checks. Verify certified fundamental discriminants and every witness, full p,b,n,UID/seed identities, cardinality and labels. Positive controls D=-23/-15 with k=1; negative noncertifying D=-7 and invalid nonfundamental D=-75; A/A serialization. No statistical inference, randomness, timing comparison or attack claim. Complete the experiment.protocol/v1 record and implementation, validate/freeze/commit/push/checkpoint before any new cohort certificate evaluation.

Retain complete successes, unknowns, noncertificates and operational failures; no arbitrary retries or threshold changes. Raw/export archive precedes report, editable visual and inspected PDF on existing PR2602. No outgoing contacts, subagents or memory writes.
