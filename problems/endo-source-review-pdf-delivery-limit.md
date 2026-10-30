# ENDO source review PDF exceeds the declared repository artifact route

- **Status:** `open`
- **Kind:** source-only review delivery and artifact-routing obstruction; no mathematical or scientific finding
- **Affected work:** `GOAL-ENDO-001`, `BATCH-1c84fc`, `TASK-20261030-d95835`; the dependent archive `TASK-20261030-f06b85` remains ineligible
- **Next action owner:** Coordinator
- **Last updated:** 2026-10-30

## Problem

The independent reviewer authored the three declared UTF-8 review bodies and a Typst report source in its admitted session. The first pinned render was 84,845 bytes and the reviewer-authored typographic correction rendered to 73,534 bytes. Both exceed the frozen 65,536-byte tracked-PDF route. The parent stopped before copying a PDF to the declared fourth output. There is no four-output completion check, landed complete review, or completed release. The two private PDFs are diagnostic evidence, not alternative deliverables.

## Evidence and uncertainty

- **Observed:** Initial private render SHA256 `dd0602f0870ea56bd4b9a1a926c8a4ece42502c32f0c0af3938059e758614540`, 84,845 bytes, three pages. Supplementary private render SHA256 `4c66d21668b965e89a3a0f59fc38ca8aed185ad522971c9cde046e2dfd9f99d3`, 73,534 bytes. The latter used only the two pinned Droid font subsets; changing that font choice alone did not meet the size bound.
- **Observed:** The first raw response had one JSON object followed by an extra closing brace. The same admitted reviewer confirmed mechanical extraction of the three unchanged bodies. Original and corrected `report.typ` are separate immutable task-turn sources. Sanitized partial-custody and failure receipts bind exact bytes; raw prompts, events, reasoning and oversized PDFs remain private.
- **Observed:** The native epoch-1 release outcome is `failed`; its declared artifact hash map is empty because no four-output set was landed and remotely read back. The separate custody record binds the three local output hashes. The exact failed release was published at `809d1ee65f7c9214bd4cdbd0438a706f7c488978`, SHA256 `b130ec8a5900f6ea2ea814d05cba93a248e007f77436a60e4a8a067072a9f87e`, at `2026-10-30T06:54:10Z` with `was_expired: false` and an empty declared artifact map.
- **Not established:** A compliant fourth PDF, a successful four-output check, scientific/JINV host admission, J3 PASS, or an eligible dependent archive. The source-only findings in three local bodies do not constitute a completed independent review.

## What would unblock it

- [ ] Coordinator selects an explicit, source-pinned route for a prospective compliant four-output review, including the tracked-file size bound or a separately authorized artifact-store contract that the handoff actually supports. No silent storage bypass or parent editing of independent review content.
- [ ] A newly scoped task/claim/session or other explicitly authorized continuation has its own finite budget, exact owner, fresh independent model admission and source/Conductor/goal-wide lane fences. The old epoch and deadline are immutable; no implied retry of the blocked card.
- [ ] The eventual reviewer checks all four actual output bytes, and landing, remote readback and truthful release succeed before dependent archive or scientific use.

This is an operational artifact-route obstruction. It does not change the protocol-v7 resource, host, toy, second-domain, transport or scientific holds, and does not imply the source-only JINV contract is complete.
