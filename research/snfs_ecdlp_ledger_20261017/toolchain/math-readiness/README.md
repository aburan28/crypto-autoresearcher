# Mathematical software readiness

This is software preparation, not a ledger-lead experiment, independent scientific review, rank certificate, or approval of a new protocol. Original frozen runs and failures are unchanged.

Sage 10.9 imports successfully in the isolated Pixi environment. Pari/GP 2.17.3 and CryptoMiniSat return their version output. Singular, fplll and mwrank executables are located in that environment. msolve was built from upstream commit `a18d0de45550363405f3dd8747abbf33f4384a06`; all 71 upstream software tests passed and its installed help command succeeds. These checks do not validate an E3/A3 encoding or qualify a full experiment over every proposed prime size.

The exact package URLs, versions and hashes are in `pixi.lock`; `pixi.toml` records the requested dependencies. Bootstrap download hashes, literal failed installation logs, successful installation logs, build commands/flags, test output and version/import checks are retained. `build-provenance.json` pins the copied files and installed binaries. The failed `sage -python` invocation is preserved in `sage-readiness.log`; the later check imports Sage with the environment's Python and records actual return codes.

The successful environment is `/workspace/snfs-toolchains/sage-pixi/.pixi/envs/default`. Execute commands through `/workspace/snfs-toolchains/bin/pixi run --manifest-path /workspace/snfs-toolchains/sage-pixi/pixi.toml`. The final readiness script records its workspace-local cache/state variables. No HOME or CODEX_HOME override was used. Earlier Mamba/Miniforge attempts failed on read-only home-directory cache/registration paths; their logs remain separate.

msolve is installed under `/workspace/snfs-toolchains/msolve`, linked against the isolated mathematical libraries. Its binary uses the host-specific vector flags and local library paths recorded in the build log; rebuild from the pinned source on another host. Its upstream tests exercise software examples, not the 23 proposed lead protocols.

G1's frozen Rust crate also builds offline with the installed Rust toolchain; its build log is in the parent directory. Its original missing-cargo run remains an infrastructure failure, and no scientific retry was launched. G3's rank arm is explicitly skipped in its frozen implementation; adding Pari/Sage afterward does not supply a descent implementation or independence proof.

Remaining experiment-specific obligations include constructors, certified inputs, complete encodings, WDSat parser/MAX_ID admission where used, the approved final source/input bindings, lawful dispatch and independent review. The configured Coordinator access limit remains separate from software installation.
