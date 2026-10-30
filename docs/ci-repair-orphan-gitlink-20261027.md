# Repair checkout's orphaned Git submodule entries

Main merge-sweeper run [40570631850](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/40570631850)
failed during checkout, before the sweeper ran: Git could not map
`.tmp/cm-factor-base-ideas-20260905-01ed89` to a `.gitmodules` entry.
On main `1ca331520f920d9dd8863faa56a7d0e98d968f8c`, native
`git submodule status --recursive` independently reproduces exit 128.

All six mode-160000 entries lack submodule mappings. Four are temporary review
worktrees under `.tmp`; the other two are imported ECDSA research references.
The repair removes only those six index entries with `git rm --cached` and
preserves every original path and exact commit OID in
`ci-repair-orphan-gitlink-20261027/original-references.json`. It neither deletes
another working directory nor changes any referenced commit or raw evidence.
`.tmp` joins the existing `.worktrees` ignore rule to prevent another accidental
recursive add.

The two imported references retain explicit `SOURCE_REFERENCE.json` records at
their original directory paths. Their original exact commits remain recorded;
no source URL or source bytes are invented. Their unresolved source custody is
tracked in [the problem record](../problems/imported-ecdsa-source-references-unresolved.md).
This repairs checkout metadata, without asserting those external sources are
available, validated or executed.

After the index repair, both `git submodule status --recursive` and
`git submodule foreach --recursive true` pass. An exact path/OID comparison
confirms all six original references remain in the custody record. No scientific
ledger, protocol, numeric result, threshold, frozen file or workflow validation
is weakened. Fresh current-head CI and review remain required before merge.

Sources reviewed: the actual failed checkout log, all staged Git modes and
`.gitmodules` mappings, the existing temporary-worktree ignore rationale, and
the imported-reference paths. Public commit searches for the two imported OIDs
returned no matches; this bounded search does not prove the sources are lost.
The before/after native Git diagnostics are retained beside the reference list.
