# A single class-group witness also passes on all eleven omissions

28 October 2026 UTC, T-5518; NIST-CLASS-ELEMENT-ORDER-01, run element-01. Observation report only; no official hypothesis or goal transition.

## Recorded result

All eleven reconstructed omissions and eight publications have a directly checked ideal-class element of order at least 200, using the first odd split rational prime. No retries are needed under this fixed policy. Both implementations agree on all 3,781 reduced powers per arm (19*199), all controls and all 21 summaries. Published P-384/P-521 retain UNKNOWN_D_K; all six streams stay present. No chosen element returns to the identity among powers 1..199.

| Curve / block | Label | First odd split q | Powers checked | Result |
|---|---|---:|---:|---|
| omitted 239 / 36 | omitted | 11 | 199 | ELEMENT_ORDER_GE_200 |
| omitted 239 / 1562 | omitted | 13 | 199 | ELEMENT_ORDER_GE_200 |
| prime239v1 | published | 23 | 199 | ELEMENT_ORDER_GE_200 |
| prime239v2 | published | 5 | 199 | ELEMENT_ORDER_GE_200 |
| omitted 239 / 2491 | omitted | 11 | 199 | ELEMENT_ORDER_GE_200 |
| omitted 239 / 2682 | omitted | 17 | 199 | ELEMENT_ORDER_GE_200 |
| omitted 239 / 2863 | omitted | 11 | 199 | ELEMENT_ORDER_GE_200 |
| prime239v3 | published | 17 | 199 | ELEMENT_ORDER_GE_200 |
| prime192v1 | published | 13 | 199 | ELEMENT_ORDER_GE_200 |
| omitted 192 / 2198 | omitted | 7 | 199 | ELEMENT_ORDER_GE_200 |
| prime192v3 | published | 13 | 199 | ELEMENT_ORDER_GE_200 |
| omitted 192 / 5405 | omitted | 7 | 199 | ELEMENT_ORDER_GE_200 |
| prime192v2 | published | 7 | 199 | ELEMENT_ORDER_GE_200 |
| secp521r1 | published | unknown | 0 | UNKNOWN_D_K |
| omitted 256 / 876 | omitted | 11 | 199 | ELEMENT_ORDER_GE_200 |
| prime256v1 | published | 11 | 199 | ELEMENT_ORDER_GE_200 |
| secp384r1 | published | unknown | 0 | UNKNOWN_D_K |
| omitted 224 / 777 | omitted | 11 | 199 | ELEMENT_ORDER_GE_200 |
| omitted 224 / 1485 | omitted | 11 | 199 | ELEMENT_ORDER_GE_200 |
| omitted 224 / 5736 | omitted | 11 | 199 | ELEMENT_ORDER_GE_200 |
| secp224r1 | published | 11 | 199 | ELEMENT_ORDER_GE_200 |

The full UID/model/p/n/seed/ordinal, source discriminant and transcript hashes are in cohort.csv. Every reduced triple is retained under runs/element-01/python and gp, one JSON file per curve and arm; largest file24,158 bytes. The quantitative first-prime.svg is drawn only from recorded q values. Its prime-selection policy is a research choice because the source leaves that choice unspecified; no fitted acceptance threshold or historical distribution is inferred.

## Source and the distinction tested

[ETSI TS102176-1 V1.2.1, July 2005](https://www.etsi.org/deliver/etsi_ts/102100_102199/10217601/01.02.01_60/ts_10217601v010201p.pdf), Annex D.1 and D.3, printed 43-46, asks for one ideal-class element of order at least MinClass=200. The proposed test composes that element through powers 1..199 and fails if identity appears. It tells generation to restart if a suitable element cannot be found, but expressly leaves element selection and the unsuccessful-selection limit unspecified. This is a real operational gap in that later document, not authenticated evidence about the 1997 NIST caller.

The previous direct h(K)>=2^24 result does not alone imply that a single element has order>=200: a large finite abelian group can have small exponent. The new test checks the additional single-element witness directly. Existence of this witness clears the source's threshold on every omitted curve; a hypothetical low-order first witness would not prove that no other witness exists.

The lifting rationale in Annex D.3 concerns a lift to characteristic zero preserving the CM endomorphism ring. It supplies no concrete discrete-log transfer algorithm. Merely lifting finite-field equation coefficients to rational integers does not establish preservation of the CM ring or subgroup transport. [Baier2002 section2.3.5](https://d-nb.info/964515040/34) describes the same class-number concern as controversial. These later sources do not establish1997 adoption, nor rule out all other transfer ideas.

## Two exact paths

Both arms choose the first odd split prime q<=10000, then the least positive odd b<2q with b^2 congruent D_K modulo4q. Python directly constructs each q^m ideal by Hensel lifting b and independently implements Gauss reduction. If a=q^m and c=(b^2-D_K)/(4a), the next root is b+2a*k with k=-c/b moduloq. This preserves the selected prime-ideal orientation. GP repeatedly composes the original Qfb(q,b,c) with qfbcomp. [Official PARI documentation](https://pari.math.u-bordeaux.fr/dochtml/html-stable/Arithmetic_functions.html) specifies composition and reduction. Every reduced triple, not merely the final order flag, agrees.

The exact imported19 fundamental discriminants and21 identities are byte-identical to the completed P-256 source amendment. Both arms recheck discriminant/factor relations; GP proves all supplied factors prime. Curve point counts and ordinary status are inherited from prior certified records; this is no new point-count computation. No class-number algorithm assuming GRH is used.

## Controls, execution and custody

Known D=-23 has selected-element order3, so passes threshold3 and returns at3 for threshold4; D=-15 returns at2; D=-7 returns at1. Nonfundamental D=-75 is rejected, deterministic A/A agrees, and unexpected-exception/early-return guards each exit1 without completion. Two initial control-only GP syntax failures are retained in preflight; renaming the built-in powers function to classpowers fixed the parser before freeze. No cohort input ran in those preflights.

Protocol SHA0636225ef6ce97eaa0c831093b946a6da960edd0e04c366d12db65e68f86ec60 was frozen and committed at a49aa5259d before cohort data; a successful S3 resume checkpoint and gate preceded launch. Exact command: python3 research/nist_seed_class_number_dated_bound_20261028/element-order-01/run.py . Python3.13.1 and PARI2.17.3 on shared macOS, one thread each;180s timeout per arm,30s guards,no retries. Raw commit c8163cfe2b precedes this report. Flow:2 requested/attempted/completed full-cohort evaluations,0 unexpected failures/timeouts,2 deliberate guard failures retained separately. The unified export passes file verification. Process CPU/wall values are diagnostic,L0; no performance claim. Source, executable, input, output and analysis hashes are retained in protocol/manifests/export/receipts.

## Inference boundary and next discriminator

Zero omissions fails the class-number bounds or this first-element threshold 200 check. Thus neither property supplies the missing exclusions. This result does not authenticate NIST's choice of class element, retries, arithmetic backend, failure behavior or use of any class-group test; it is not a claim that every historical implementation would succeed. Unknown P-384/P-521 do not affect the all-eleven witness result. Reconstructed omissions are not original rejection logs.

Canonical signed-action/SEA diagrams were checked and remain unchanged. evidence-boundary.svg keeps the independently tested number-of-classes and order-of-one-element facts separate from missing historical-use evidence. Existing P-224 cube/splitting lead stays open. The source-based next check is the actual May1997 generic polynomial-degree routines against later documented splitting-degree fixes, with no assumption that a later bug already existed or was called by NIST. Any actual curve test requires a newly frozen source condition and all 21 accounting. Full historical-selector goal remains active and unresolved. No outgoing contacts, subagents or memory writes.
