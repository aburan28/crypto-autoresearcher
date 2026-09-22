# CryptoMiniSat 5.14.7 exit-status inspection

Provenance: retrieved primary upstream source, read before the pilot's first solver invocation. The official tag release/v5.14.7 (tag object611105c66897ea02a6a4d75e88f532fe7df1743a) resolves to commit3c8e228e8a48e41276e8ab039f763daa08d61161. The archived source `main.cpp`, SHA2567ce88d86e3cb6b0d47c5040650aac9417fa0f9b8bd5e4664e5ded1f425a9b34f, defines Main::correctReturnValue at lines1364–1383. Source URL: https://github.com/msoos/cryptominisat/blob/3c8e228e8a48e41276e8ab039f763daa08d61161/src/main.cpp .

The default return mapping is SAT10, UNSAT20, undefined15. Undefined output uses the status line `s INDETERMINATE`. The option `--zero-exit-status` changes the return to0; the frozen pilot arguments do not include it. Parser fixtures should therefore pair the status text with10/20/15 and distinguish unexpected exits from censored indeterminate solves.

This inspection identifies a latent issue in the archived N7 worker: it recognized0, rather than15, as a solver UNKNOWN. That completed N7 panel had no UNKNOWN and is not rerun or reclassified by this note. The new pilot implements the already frozen censor-handling requirement correctly; no target, cap, sample count or mathematical prediction changes.

The retrieved tag identifies upstream source behavior. The installed executable's version string is5.14.7 but its GIT-notfound marker does not prove it was built from this commit. Exact installed binary/library bytes are separately hash-bound and their actual status outputs will be archived. No source-build provenance or reproducible-build match is inferred from the tag.
