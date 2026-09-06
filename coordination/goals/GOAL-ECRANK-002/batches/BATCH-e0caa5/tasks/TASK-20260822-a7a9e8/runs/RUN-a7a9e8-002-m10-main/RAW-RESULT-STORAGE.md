# raw-result.json is stored compressed in git

The producer wrote `raw-result.json` at **112301654 bytes (108 MB)** — it dumps all
39,876 trial curves, each with points, polynomials and regulator data, not just
the high-rank pool the handoff asked for. GitHub rejects any file over 100 MB
(`GH001`), so the push failed on it.

The producer's bytes are NOT edited, summarised or trimmed. They are stored
losslessly as `raw-result.json.gz` (23137977 bytes):

    original  sha256 = ff0935a0c68c58da7da3fdb861f36d80e33f72365fb2ecb57d8196b0af5ccb47
    roundtrip sha256 = verified byte-identical via `gunzip -c | sha256sum`

Recover the exact original with:

    gunzip -c raw-result.json.gz > raw-result.json

The uncompressed file remains on local disk because the producer subagent had
not returned and may still read it; it is excluded from git via
`.git/info/exclude` (LOCAL ONLY — nothing committed, no repo config changed).

## Deviation, recorded not absorbed

Archive-verbatim is preserved in content but NOT in file layout: the archived
object is a compressed copy under a different name. The Coordinator snapshot
archive must hash `raw-result.json.gz` and record the original sha256 above, so
a reader can verify the producer's bytes without the 108 MB file ever entering
git history.

Separately, and for the Coordinator rather than for this note to settle: dumping
every trial including rank-3 results is over-collection against a handoff that
asked for a pool of constructed curves. That is a producer design question, not
something to fix by silently trimming its output.
