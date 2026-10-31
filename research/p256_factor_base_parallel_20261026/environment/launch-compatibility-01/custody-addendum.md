# Custody addendum to TASK-20261026-7f2e09

The original `inspection.md` and `result.json` remain byte-for-byte unchanged. Their SHA-256 values are `bb07e43f86f1a8eed03f7a54c81666b303444388473eb579c69a25cffc6dc9a7` and `19e5b996d6185c4f5c4e88a5656723fe0b21592cd11d412be04a0e211d6084b3` respectively.

The original JSON pairs a later live-file hash with an earlier comparison result:

| Exact script object | SHA-256 |
| --- | --- |
| Dispatch `616878bcf0c8a749f38dd3ad0dbb1153478d4010` | `de5d922d7b38a14d16843901b5fb182434ff8fdd1b3a81085e66c49ce2dc8f1f` |
| Later cache-failure repair `a527b62b11e6dcc2a365bae2bf9cfd0107a765cd` | `f534f47957913c6c4258e123dcbba83a3189e57ad5e4fd4342015c31a7ac41cb` |

`result.json`'s `common_helper.checkpoint_script_sha256` and its script source-exposure hash match the later object. Therefore `checkpoint_script_matches_dispatch: true` is **false when interpreted as a comparison of that recorded hash to the dispatch**. The earlier true comparison applies only to the dispatch digest `de5d922d7b38a14d16843901b5fb182434ff8fdd1b3a81085e66c49ce2dc8f1f`. `inspection.md:45` correctly describes that dispatch object; its script line references are also dispatch-relative.

Report construction recomputed the live script digest while retaining the earlier comparison boolean after root changed the script. These are mixed-time observations, not evidence that the later script was part of the original inspection. The later source diff was read here only to identify custody; neither the original inspection nor this addendum independently reviews or certifies the cache-failure repair.

Read-only exact-object comparisons found all 80 selected source, protocol, input, common-helper and interpreter-record paths byte-identical between the two commits. The seven frozen protocol/source comparisons and existing F3, watchdog, F4 checkpoint and CLI findings therefore remain valid within their original limits. The interpreter executable's original observation remains time-local; this addendum did not re-probe it.

Only this custody addendum was added. No scientific module, help path, panel, gate/upload, export or credential access occurred. No Git mutation or sibling report read occurred. The native model remains unprobed, and no scientific review admission, correctness or release-success claim is made. `custody-addendum.json` records the exact field interpretations, path inventory and preservation hashes.
