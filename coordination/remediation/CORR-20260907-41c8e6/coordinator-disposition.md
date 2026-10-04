# Coordinator disposition: administrative integrity repair

Date: 2026-09-07
Handoff supplied by parent: `TASK-20260907-88f112` (identifier check was pending in the supplied message; parent must complete it before archival use).
Output scope: this local disposition only.
Experimental runs authorized by this disposition: 0.

## Decision and boundary

Approve preparation and implementation of the proposed **administrative repair**, subject to the concrete requirements below. The parent may incorporate these requirements without seeking another idea, experiment, or user approval. Final acceptance requires review of the actual changes and passing the specified integrity checks; this document is not a finding that those checks already passed.

This decision permits restoration of file packaging and schema consistency and an explicit representation of an unrecoverable execution-provenance gap. It does not establish historical execution provenance, validate scientific observations, approve a new experiment, change a hypothesis or goal, or waive any independent scientific review. The original producer assertions remain identifiable as such. A clean validator result after repair means the declared records meet the revised integrity contract; it must not be described as restoration of missing evidence or cryptanalytic validation.

The assessment uses only parent-supplied descriptions and the earlier diagnostic. This agent has not inspected the proposed diff, complete source files, artifact hashes, validator implementation, or tests, and has executed no commands or experiments. No independently verified model identifier was exposed. The parent's control plane owns verification, current ownership checks, bounded implementation, and the scoped PR archive.

## Required treatment of each repair class

1. **Six `bbb42f` raw-result companions.** Add byte-identical copies from the existing `results.json` to `raw-result.json` only after the source is verified as the same run's actual result artifact. Record source and destination hashes. Preserve the original file and original manifest. A new filename supplies packaging, not new evidence.

2. **SSI log companions.** Add `.log` companions as byte-identical copies of the corresponding original `.txt` files; do not rename or remove the originals. Retain the exact original contents, including failure text and incomplete output.

3. **MLKEM command, environment, and terminal receipt.** Populate command/environment companions from the original manifest without guessed values. If `terminal_receipt.json` is copied to `raw-result.json`, the correction record must explicitly identify the new file as a byte-identical operational terminal receipt and preserve its source hash. It cannot stand in for absent scientific outputs, controls, or a correctness certificate. Accept a valid operational-control result only if the original frozen task explicitly measured the quantities this receipt actually records and the required original evidence exists. Otherwise represent the missing scientific-result evidence explicitly as incomplete/invalid; do not retain or introduce scientific validity merely because required filenames now exist. Do not fabricate or silently reclassify a scientific experiment as an operational task to clear validation.

4. **Eight ECRANK wrappers and one checkpoint wrapper.** Produce canonical wrappers by mapping existing fields without changing observations, timestamps, claimed statuses, or provenance. Record `certificate.kind: none` as absence of a supplied certificate. A checkpoint wrapper must preserve its checkpoint identity and must not assert that another run occurred. Missing substantive fields are defects to disclose, not template values to invent.

5. **Five `a98ea9` manifest corrections.** Preserve exact original multiline `dirty_summary` values in the parsed replacement, including meaningful newlines and content. Preserve original validity assertions in explicit source metadata. Map a producer's `gate_failure` to `completed_invalid`, and a producer's `valid` to `completed_valid`, only as the schema's execution/result classification; neither mapping constitutes independent review. Any substantive inconsistency between the raw result and the original status must be recorded and resolved conservatively, rather than erased by normalization.

6. **Malformed ECRANK evidence record.** Add canonical `EV-ECRANK-469594` only after identifier allocation/check and schema verification. Supersede `EV-ECRANK-76a70d-285d90` using the established hash-pinned registry and `replacement_id`; preserve the original file and its identifier. Preserve observations and source assertions without endorsing them. `direction: neutral`, `strength: unverified`, empirical-only labeling, and no proof references are appropriate. Label the scale as toy only to the extent the actual original tested parameters justify it, and carry those parameters explicitly. State that independent review remains pending. Do not remove an existing review, contradiction, or negative observation if one is present; surface any such conflict before final acceptance.

7. **S2 manifest with missing code provenance.** Add a hash-pinned canonical replacement, with actual source-backed metadata and `code.commit: null`, dirty-tree state null, `status: completed_invalid`, `result.valid: false`, `certificate.kind: none`, and a nonempty `provenance_gap` naming the unrecovered execution-time revision and dirty-tree state. Record hashes for inspected originals and preserve the original `status: valid` solely as an attributed producer assertion. Identify invalidity as a reproducibility/provenance defect, not a failed mathematical hypothesis or a failed H3 run. Do not substitute the archival commit, S1 provenance, a current checkout revision, or a guessed clean-tree state. The existing S2 observations remain available within this disclosed boundary.

## Requirements for the validator changes

The validator may recognize an explicit, registered historical correction with incomplete provenance. It may not generally relax the execution-code requirement.

- Bind the exception to the original path, verified original content hash, replacement identity/path, and the registered correction. Use an explicit exception kind or equivalent precise registry condition; mere presence in a supersession registry is insufficient. Require the declared missing fields to match the replacement's actual provenance gap.
- Permit missing execution provenance under this exception only when the replacement is explicitly `completed_invalid`, `result.valid` is exactly false, the gap/reason is nonempty, and no certificate or scientific-validity assertion contradicts that classification. A null value must remain unknown, never coerced to a clean state or a successful check.
- Keep normal code-commit and dirty-state requirements unchanged for unregistered records, ordinary replacements, and any valid completed run. Do not hide validator errors by broadly skipping a directory, swallowing a parse error, or accepting a replacement solely because the old file was malformed.
- Check evidence references through the same canonical supersession resolution used elsewhere. Evidence depending on the incomplete S2 run must be limited to neutral/inconclusive direction, carry an explicit unresolved-provenance disclosure, and not promote the record into proof or supported scientific evidence through an alias or an indirect replacement reference. Existing claim and promotion gates still apply. The incomplete run may document observed artifacts or an operational defect; it cannot establish a mathematical obstruction.
- The optional `superseded_id_line` mechanism applies only to an original source that fails normal parsing. Verify the registered original hash **before** extracting its identity. Require the recorded line to contain one exact, literal, root-level `run_id` scalar, matching the expected run identity and run directory. Reject ambiguity, duplicate root identities, aliases, tags, interpolation, nested keys, wrong line numbers, path mismatches, and hash mismatches. Do not use a permissive YAML repair or substring search to infer identity.
- Normally parseable originals must use the normal parser and identity checks. Every replacement must parse and validate normally; the malformed-original fallback must never be used to validate a replacement. Enforce unambiguous replacement resolution and the existing protection against inconsistent bindings or cycles.

The incomplete-provenance exception makes the absence machine-readable and ineligible for scientific reliance. It does not discharge the missing provenance requirement for the original run or assert that recovery is impossible from sources not inspected.

## Acceptance and PR scope

Before accepting the repair, the parent must verify all of the following:

- Original artifacts and identifiers are preserved. Every byte-copy companion matches its source hash; every reconstructed scalar or structured value has a named original source. Multiline dirty-state summaries survive parsing exactly.
- Each originally reported violation has an explicit corrective disposition. Run the full current ledger validation and compare against the retained 50-error inventory; a passing count alone does not justify unregistered suppression or concealment of newly introduced defects.
- Focused regression checks demonstrate acceptance of the exact disclosed historical-invalid case and rejection of: unregistered null provenance; valid status with null provenance; absent or empty gap; contradictory `result.valid` or certificate; favorable evidence relying on the incomplete run; hash, identity, directory or line mismatch; ambiguous/multiple root identifiers; misuse of the malformed-source fallback for a valid original or any replacement; and altered multiline source values. Reuse existing meaningful tests where possible.
- Reconcile canonical evidence references and affected archive bindings using the repository's additive correction rules. Do not rename any original bound by a completed archive. Existing scientific review obligations remain recorded and outstanding.
- Inspect the final PR diff for intended source, correction, validator and test paths only. Preserve unrelated concurrent edits and current claims. S2H3's reported claim and scope are outside this repair; no H3 execution or takeover is authorized.
- Report remaining code-provenance loss and pending independent scientific review plainly in the PR. Distinguish software/integrity checks from experimental validation. An administrative PR may be created under the user's explicit request; its acceptance is not a scientific-status transition.

If a required source or binding is absent, retain that exact gap as a failing prerequisite unless it fits the narrowly disclosed historical-invalid representation above. Do not broaden the exception opportunistically just to reach zero errors.

## Recorded next action

The parent control plane should implement the scoped additive package corrections and narrow validator rules above, verify the real diff against the retained source artifacts and the regression/ledger gates, and create the requested PR with the S2 provenance limitation stated explicitly. No further research execution or scientific status transition is part of this action.
