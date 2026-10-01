# Native exception custody correction

TASK-20260910-f299db, approved by DEC-20260910-d066bb, corrects descriptor ownership, primary and secondary error preservation, and host cleanup outcomes for EXP-ECDLP-709063.

The final fixed suite passed 171/171 controls. The earlier attempt passed 166/171; its five fixture mismatches and all raw attempts remain in check-receipt.json. Two registry discoveries executed zero controls. Across both suites, 342 controls and ten bounded benign process starts were recorded. No scientific runs or live Docker/cgroup operations occurred.

The corrected fixtures supply the complete handle state and assert original-error preservation with separate rollback failure. Source and registry bindings are retained for both attempts.

The initial tool launch response for attempt1 is known from conversation, but its original final tool response was unavailable after session recovery. Retained native controller attempt and raw process observations establish exit 2; no missing tool response is reconstructed.

The delivery requires Coordinator snapshot and fresh independent complete source/custody review. It grants no measurement admission. Sampled RSS does not establish a hard memory guard.
