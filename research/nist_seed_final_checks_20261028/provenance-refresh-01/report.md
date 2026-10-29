# Direct-provenance refresh after the fixed arithmetic pass

Observed 28 October 2026. This is a source-availability check, with zero new curve-arithmetic trials. The [closing arithmetic report](../report.md) and its frozen results are unchanged. The original selection rule remains unresolved.

## What was checked

The [current bounty account](https://words.filippo.io/seeds-solved/) still identifies an unexplained additional selection step. The [Anthropic primary account](https://www.anthropic.com/research/ecdsa-curve-origins), under “Open questions”, likewise leaves both an additional criterion and an unintentional implementation artifact open. These are current descriptions of the gap, not original generation records.

The linked Go reconstruction has a single commit in the returned file-history page: [5fea0f56c717b8499710fb0237cda6f6ed75653d](https://github.com/FiloSottile/mostly-harmless/commit/5fea0f56c717b8499710fb0237cda6f6ed75653d), authored 16 October 2026. Its message identifies a reimplementation. The pinned [source header](https://github.com/FiloSottile/mostly-harmless/blob/5fea0f56c717b8499710fb0237cda6f6ed75653d/seeds/seeds.go) identifies PARI/GP as the order-counting backend and explicitly leaves eleven omissions unexplained. It is not Reiter's 1997–98 source and cannot establish the original acceptance path.

Separate GitHub issue and pull-request searches for “seed” in that repository returned zero items, each with incomplete_results=false. This is a bounded keyword search, not proof that no relevant discussion exists. The first combined query was refused because the connector required an issue-type qualifier; that error and the two corrected query results are retained in [evidence.json](evidence.json).

Exact-date searches for the 17 November 1997 X9.62 draft returned bibliographic references, including the [1997 IETF draft](https://datatracker.ietf.org/doc/html/draft-ietf-pkix-ipki-ecdsa-00) and [PKCS #11 v2.01 reference list](https://www.cryptsoft.com/pkcs11doc/STANDARD/v201-95.pdf). They did not yield the X9.62 draft body or a generation log. The earlier [draft-archive investigation](../../nist_seed_1997_draft_archive_20261023/report.md) remains the source for the independently retained draft references. No new candidate-list history is established here.

## The Reiter–Solinas patent is a different setting

A source search surfaced [US6243467B1](https://patents.google.com/patent/US6243467B1/en), filed 23 July 1998, by Robert W. Reiter and Jerome A. Solinas. Its detailed description and claim 1 select a characteristic-two Koblitz curve and use reduced tau-adic scalar multiplication for signing and verification. The source provides a concrete endomorphism setting associated with those authors, but that setting is not the odd-prime-field cohort under investigation. It supplies no acceptance test or decision trace for any of these 21 curves. No predicate or experiment was inferred from it.

## Evidence boundary

No original generator source, original keep/skip log, or documented rule explaining all eleven omissions and ten publications was acquired. This source refresh does not prove that such records are unavailable elsewhere, and does not prove that the missing rule is non-arithmetic. No new scientific result is claimed. The arithmetic loop remains closed; any future candidate procedure needs direct provenance before another all-cohort test is justified.

