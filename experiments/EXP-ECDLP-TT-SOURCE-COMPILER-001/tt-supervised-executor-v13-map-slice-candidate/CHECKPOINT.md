# V13 Typed Private-Map Observation Checkpoint

Status: `HYPOTHESIS` | `MODEL-BOUND` | `ZERO-RUN` |
`NOVELTY-UNVERIFIED`

Decision: `READY_FOR_POST_REPAIR_STAGING_REVIEW`.

This checkpoint concerns only the finite-model externalization of the E0
private-map open result. It is not a runtime executor, campaign authorization,
cryptanalytic result, or ECDLP claim.

## Positive evidence

- Five canonical traces reach final lock release in 422 journal transitions
  and 927 final records.
- P001 supplies the durable request and intent; a typed gateway record supplies
  `map_opened` or `map_open_failed`.
- P002 has no action domain and is rejected at the canonical post-P001 wait.
- P003 writes only the E0 map-failure terminal.
- The exceptional P003 route creates its missing ref observation in G000,
  commits E0 failure, and closes normally.

## Preserved negative evidence

The initial independent Red Team returned `NO_GO` for staging because the
generic publication verifier accepted self-selected path sets and listed
AppleDouble files. Its report is preserved as `V13-RED-TEAM-REVIEW.md`.

## Repair boundary

- Bind publication to a pinned exact V13 path set and payload count.
- Reject AppleDouble, `.DS_Store`, symlinks, special files, unlisted files, and
  every path component ending in `-work`.
- Store replay inputs under durable non-work paths.
- Persist forced P002, active E0-close map observation, P003 extra-domain,
  missing-required-payload, and listed-AppleDouble controls.
- Require a post-freeze Theory and Red Team decision over the immutable root.

## Repair evidence

- The exact publication policy contains 227 required relative paths and is
  externally pinned in the publication verifier.
- Persistent replay inputs contain 30 semantic, 19 spawn, 16 reap, and 17 map
  mutation universes under non-`work` directories.
- Seven meta controls include a complete-policy positive bundle, both decision
  parity faults, mandatory-registry substitution, unlisted payload, symlink,
  missing required payload, and listed AppleDouble.
- The expanded mandatory registry is 89 of 89 complete: 70 inherited V12
  controls plus 19 V13 map/publication controls.
- The initial policy-label mismatch is preserved in
  `meta-publication-regressions-v13-initial-policy-failure.json` rather than
  overwritten.

## Open boundaries

Restart, process reconciliation, infrastructure finalization, OS producer
authentication, crash atomicity, filesystem durability, live Git behavior,
implementation equivalence, campaign execution, and ECDLP relevance remain
outside V13.

## Next concrete action

Obtain a post-repair independent staging decision, then copy only the 227
policy-required payloads and verify the external manifest root.
