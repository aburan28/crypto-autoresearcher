# A dated 1997 X9.62 draft is the next historical source to recover

**Date:** 2026-10-23 UTC. **Scope:** Read-only archival search for a contemporaneous X9.62 parameter record or acceptance rule. **Result:** Two primary IETF documents identify an ANSI X9.62 ECDSA working draft dated **17 November 1997**. The draft's contents were not obtained, so this search does not establish which curves it listed or why any candidate was passed over.

## Evidence and its precise limit

The NIST-authored [PKIX ECDSA Internet Draft of 21 November 1997](https://www.ietf.org/archive/id/draft-ietf-pkix-ipki-ecdsa-00.txt) cites an ANSI X9.62-199x ECDSA working draft dated 17 November 1997 at its lines 832–836 (`retrieved`, primary). An early [TLS ECC Internet Draft](https://www.ietf.org/archive/id/draft-ietf-tls-ecc-00.txt) names the same working-draft date at lines 947 and 974 (`retrieved`, primary). The [source metadata record](evidence.json) binds the exact retrieved text SHA-256 values. Both documents point to the X9.62 draft; neither supplies its parameter table or a candidate-rejection log. The claim sometimes made in later discussion that P-256 already appeared *inside* that draft is **not independently verified here**.

The November draft is a concrete contemporary target because it followed the reconstructed May and August 1997 seed-stream starts and preceded the public 1998 X9.62 text. The recovered start dates are computational reconstructions from the seed streams, not independent wall-clock run logs ([earlier workflow study](../nist_seed_1997_workflow_20261016/report.md), `internal`). The September 1998 [X9.62 text](https://safecurves.cr.yp.to/grouper.ieee.org/groups/1363/private/x9-62-09-20-98.pdf) (`retrieved`, primary) documents final sample parameters and ordinary screens, but cannot tell us which decisions had already been made in November 1997.

An [Internet Archive CDX query](sources/wayback_x962_index.json) for `grouper.ieee.org/groups/1363/private/x9-62*` returned five indexed URLs for the September 1998 draft, four with archived `401` statuses and one `404`. It returned no 1997 draft content. This search covered only one file-prefix path in one archive; it does **not** prove that the November draft no longer exists elsewhere. A guessed `x9-62-11-17-97.pdf` at the live IEEE path returned `404`; that guessed filename is not a documented historical URL.

![Historical evidence and missing draft](timeline.svg)

*Figure 1. Solid links show dated reconstructed runs and primary-document references. The dashed branch marks the absent draft contents and decision trace. Editable source: [timeline.dot](timeline.dot).*

## Why obtaining the draft matters

The draft could give a dated candidate list, equations, seed values, version notes or security language closer to the 1997 decisions than the 1998 publication. If it lists an omitted candidate as a then-current sample or records a replacement, that would directly alter the keep/skip history. If it contains only the final curves, it would bound publication timing but still not identify why other qualifying stream blocks were unused. Either outcome must be compared by exact seed or `p,a,b,n` identity against the [eleven-candidate archive](../nist_seed_skipped_curves_20261016/assessed.json), with the ten published controls; names or bit lengths alone are insufficient.

The actionable acquisition target is the **17 November 1997 X9.62-199x ECDSA working draft cited by the two IETF documents**, and then any immediately preceding or following committee drafts, change sheets, parameter tables, or Bob Reiter's generator/review records. A copy should be pinned by source, date and digest before its entries are compared with the 21 known seed-level classes. The current [selection-rule problem](../../problems/nist-seed-selection-rule-unexplained.md) remains open. This search found no new curve property or attack edge; the canonical ECDLP graphs were checked and remain unchanged.

## Provenance and reproduction

The retrieved IETF text digests and exact reference lines are in [evidence.json](evidence.json); the [CDX response](sources/wayback_x962_index.json) is retained verbatim. The reproducible query URL and its narrow scope are also in the evidence record. The study's observation is limited to these sources and to the current access result. It does not assert that the original 1997 draft was publicly archived, accessible through IEEE, or absent from NIST, ANSI, or private collections. No official hypothesis or goal status changes here.
