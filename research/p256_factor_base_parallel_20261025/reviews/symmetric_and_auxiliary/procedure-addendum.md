# Local authoring procedure addendum

TASK-20261025-1a83bb, 2026-10-25. The handoff calls the derivation, review and
result write-once. The blind derivation was written once and remains byte-identical.
The producer artifacts remain byte-identical to their bound inputs.

The reviewer revised review.md during PDF layout repair, and result.json while
adding presentation and software metadata, before final sealing. This does not
satisfy a literal write-once interpretation for those two files. The first report
source and PDF are retained as review-first-render.md and review-first-render.pdf;
its extracted text records the original layout issue. An exact copy of the first
provisional result.json was not retained. No mathematical verdict or test output
was reversed. This procedure deviation is explicit and cannot be treated as
canonical review compliance.

A late metadata probe used system python3 rather than the validation virtualenv
and failed to find python-flint distribution metadata. metadata-probe.stderr
transcribes its tool-returned traceback. The successful next probe read module
versions in the same virtualenv used for all mathematical computations. That
probe also printed the ordinary Matplotlib fallback-cache warning; no arithmetic
check was run in the system environment.

The primary report remains review.md, with local scope and scientific-gate limits
in its first paragraph. result.json and final-seal.json bind the delivered state.
